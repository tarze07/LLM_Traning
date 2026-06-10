# Dekodowanie spekulatywne — wersja robocza, weryfikacja, powtórzenie

> Dekodowanie autoregresyjne jest z natury szeregowe — każdy token zależy od poprzedniego. Dekodowanie spekulatywne przerywa ten łańcuch: lekki model proponuje N tokenów, a ciężki model weryfikuje je wszystkie w jednym przejściu w przód. Gdy projekt jest trafny, płacisz koszt jednego dużego wywołania za N wygenerowanych tokenów.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 7 · 07 (przyczynowy LM GPT), faza 7 · 12 (pamięć podręczna KV i uwaga Flash)
**Czas:** ~60 minut

## Problem

Próbkowanie jednego tokena z 70B LLM zajmuje około 30 ms na H100. Model roboczy o rozmiarze 3B zajmuje jedynie ~3 ms. Jeśli pozwolimy modelowi 3B zaproponować 5 tokenów z wyprzedzeniem, a następnie uruchomimy 70B *raz* w celu weryfikacji wszystkich pięciu, łączny czas wyniesie `5×3 + 30 = 45 ms` dla maksymalnie 5 zaakceptowanych tokenów — w porównaniu z `5×30 = 150 ms` przy generowaniu liniowym. To właśnie istota dekodowania spekulatywnego: niewielki koszt dodatkowej pamięci GPU (model roboczy) przekłada się na 2–4-krotne skrócenie czasu dekodowania.

Kluczowe jest zachowanie rozkładu wyników. Próbkowanie spekulatywne, przedstawione niezależnie przez Levithana i in. (2023) oraz Chena i in., gwarantuje, że sekwencja wyjściowa jest **identycznie rozłożona** jak ta, którą duży model wygenerowałby samodzielnie. Żadnych kompromisów jakościowych — po prostu szybciej.

W roku 2026 we wnioskowaniu dominują cztery rodziny par weryfikator–wersja robocza:

1. **Waniliowe próbkowanie spekulatywne (Leviathan 2023).** Oddzielny model roboczy (np. Llama 3 1B) wraz z weryfikatorem (np. Llama 3 70B).
2. **Medusa (Cai 2024).** Wiele głowic dekodujących na weryfikatorze przewiduje pozycje `t+1..t+k` równolegle. Nie wymaga osobnego modelu roboczego.
3. **Rodzina EAGLE (Li 2024, 2025).** Lekka wersja robocza, która ponownie wykorzystuje ukryte stany weryfikatora; wyższy wskaźnik akceptacji niż w waniliowym podejściu, typowo 3–4×.
4. **Dekodowanie z wyprzedzeniem (Fu 2024).** Iteracja Jacobiego — nie wymaga żadnego modelu roboczego. Podejście własne. Niszowe, lecz wolne od zewnętrznych zależności.

Każdy produkcyjny stos wnioskowania w roku 2026 domyślnie zawiera dekodowanie spekulatywne. vLLM, TensorRT-LLM, SGLang i llama.cpp obsługują co najmniej wariant waniliowy oraz EAGLE-2.

## Koncepcja

### Podstawowy algorytm

Mając weryfikator `M_q` i tańszy model roboczy `M_p`:

1. Niech `x_1..x_k` będzie już zdekodowanym prefiksem.
2. **Draft**: użyj `M_p`, aby autoregresywnie zaproponować `d_{k+1}, d_{k+2}, ..., d_{k+N}` z prawdopodobieństwami wersji roboczej `p_1..p_N`.
3. **Weryfikacja równoległa**: uruchom `M_q` raz na `x_1..x_k, d_{k+1}, ..., d_{k+N}`, uzyskując prawdopodobieństwa weryfikatora `q_1..q_{N+1}` dla pozycji `k+1..k+N+1`.
4. **Akceptacja lub odrzucenie każdego tokenu wersji roboczej od lewej do prawej**: dla każdego `i` zaakceptuj z prawdopodobieństwem `min(1, q_i(d_i) / p_i(d_i))`.
5. Przy pierwszym odrzuceniu na pozycji `j`: pobierz próbkę `t_j` ze znormalizowanego rozkładu rezydualnego `(q_j - p_j)_+`. Wszystkie kolejne tokeny robocze po pozycji `j` są odrzucane.
6. Po zaakceptowaniu wszystkich `N`: pobierz jeden dodatkowy token `t_{N+1}` z `q_{N+1}` — jest to bezpłatny token bonusowy.

Sztuczka z rozkładem rezydualnym wynika z wglądu matematycznego, który zapewnia, że rozkład wyników jest dokładnie taki sam, jak przy bezpośrednim próbkowaniu z `M_q`.

### Co decyduje o przyspieszeniu

Niech `α` oznacza oczekiwany wskaźnik akceptacji na token wersji roboczej, a `c` — stosunek kosztów modelu roboczego do weryfikatora. Na jeden krok:

- Generowanie naiwne wykonuje jedno wywołanie dużego modelu na token.
- Generowanie spekulatywne wykonuje jedno wywołanie dużego modelu na `(1 - α^{N+1}) / (1 - α) ≈ 1/(1-α)` tokenów, gdy `α` jest wysokie.

Typowa zasada praktyczna: przy `α = 0.75` i `N = 5` uzyskujemy 3-krotną redukcję wywołań dużego modelu. Koszt wersji roboczej to 5 razy mniej. Całkowity zysk czasowy wynosi ~2,5×.

**Wskaźnik α zależy od:**

- Stopnia podobieństwa modelu roboczego do weryfikatora. Ta sama rodzina modeli lub te same dane treningowe znacząco podnoszą α.
- Strategii dekodowania. Zachłanny projekt wobec zachłannego weryfikatora daje wysokie α. Próbkowanie z temperaturą jest trudniejsze do dopasowania i obniża wskaźnik akceptacji.
- Rodzaju zadania. Kod i ustrukturyzowane dane wyjściowe są bardziej przewidywalne, więc wskaźnik akceptacji jest wyższy. Twórcze pisanie swobodne daje niższe wyniki.

### Medusa — szkice bez oddzielnego modelu roboczego

Medusa zastępuje model roboczy dodatkowymi głowicami wyjściowymi na weryfikatorze. Na pozycji `t`:

```
shared trunk → hidden h_t
    ├── head_0: predict token at t+1  (standard LM head)
    ├── head_1: predict token at t+2
    ├── head_2: predict token at t+3
    ├── head_3: predict token at t+4
```

Każda głowica generuje własne logity. Podczas wnioskowania pobierasz próbkę z każdej głowicy, tworząc sekwencję kandydatów, a następnie weryfikujesz je jednym przejściem w przód z zastosowaniem uwagi drzewiastej, która uwzględnia wszystkie potencjalne kontynuacje naraz.

Zalety: brak drugiego modelu. Wady: dodatkowe parametry wymagające trenowania; konieczny etap nadzorowanego dostrajania (~1 miliard tokenów); wskaźnik akceptacji nieco niższy niż w waniliowym podejściu spekulatywnym z dobrym modelem roboczym.

### EAGLE — lepszy szkic dzięki ponownemu wykorzystaniu ukrytych stanów

EAGLE-1/2/3 (Li et al., 2024–2025) stosuje jako model roboczy mały transformer (zwykle jednowarstwowy), który przyjmuje ukryte stany ostatniej warstwy weryfikatora. Ponieważ model roboczy uwzględnia reprezentacje cech weryfikatora, jego przewidywania są silnie skorelowane z rozkładem wyników weryfikatora. Wskaźnik akceptacji wzrasta z ~0,6 (wariant waniliowy) do 0,85 i więcej.

W EAGLE-3 (2025) wprowadzono przeszukiwanie drzewa w celu eksploracji kontynuacji kandydatów. vLLM i SGLang dostarczają EAGLE-2/3 jako domyślną ścieżkę spekulacyjną dla Llama 3/4 i Qwen 3.

### Zarządzanie pamięcią podręczną KV

Podczas weryfikacji przekazujemy `N` tokenów roboczych do weryfikatora w jednym przejściu w przód. Rozszerza to pamięć podręczną KV weryfikatora o `N` wpisów. Jeśli część tokenów roboczych zostanie odrzucona, pamięć podręczna musi zostać przywrócona do zaakceptowanej długości prefiksu.

Implementacje produkcyjne (opcja `--speculative-model` w vLLM, `LookaheadDecoder` w TensorRT-LLM) obsługują to za pomocą buforów KV: najpierw zapis, a zatwierdzenie dopiero po akceptacji. Koncepcyjnie nie jest to skomplikowane, lecz wymaga starannej implementacji.

## Zbuduj to

Zobacz `code/main.py`. Implementujemy podstawowy algorytm próbkowania spekulatywnego (krok odrzucenia i rozkład rezydualny), korzystając z:

- „Dużego modelu" — deterministycznego softmaksa na podstawie ręcznie zakodowanego rozkładu, co pozwala analitycznie zweryfikować matematykę akceptacji.
- „Modelu roboczego" — zaburzonej wersji dużego modelu.
- Pętli akceptacji/odrzucenia, która zachowuje identyczny rozkład brzegowy jak bezpośrednie próbkowanie.

### Krok 1: krok odrzucenia

```python
def accept_or_reject(q_prob, p_prob, draft_token, u):
    ratio = q_prob / p_prob if p_prob > 0 else float("inf")
    return u < min(1.0, ratio)
```

`u` to jednostajna liczba losowa. `q_prob` to prawdopodobieństwo weryfikatora dla wygenerowanego tokenu, a `p_prob` — prawdopodobieństwo modelu roboczego. Twierdzenie Levithana głosi, że decyzja Bernoulliego, po której następuje próbkowanie z rozkładu rezydualnego przy odrzuceniu, dokładnie zachowuje rozkład weryfikatora.

### Krok 2: rozkład rezydualny

```python
def residual_dist(q, p):
    raw = [max(0.0, qi - pi) for qi, pi in zip(q, p)]
    s = sum(raw)
    return [r / s for r in raw]
```

Odejmujemy `p` od `q` element po elemencie, ujemne wartości sprowadzamy do zera i renormalizujemy. Z tego rozkładu pobieramy próbkę przy każdym odrzuceniu.

### Krok 3: jeden krok spekulatywny

```python
def spec_step(prefix, q_model, p_model, N, rng):
    drafts = []
    p_probs = []
    ctx = list(prefix)
    for _ in range(N):
        p_dist = p_model(ctx)
        d = sample(p_dist, rng)
        drafts.append(d)
        p_probs.append(p_dist[d])
        ctx.append(d)

    q_dists = [q_model(prefix + drafts[:i]) for i in range(N + 1)]

    for i, d in enumerate(drafts):
        u = rng.random()
        q_prob = q_dists[i][d]
        p_prob = p_probs[i]
        if u < min(1.0, q_prob / p_prob if p_prob > 0 else float("inf")):
            prefix = prefix + [d]
        else:
            res = residual_dist(q_dists[i], p_model(prefix))
            prefix = prefix + [sample(res, rng)]
            return prefix
    prefix = prefix + [sample(q_dists[N], rng)]
    return prefix
```

Pięć zaakceptowanych tokenów plus jeden bonusowy daje sześć tokenów wyprodukowanych w jednym przejściu weryfikatora.

### Krok 4: pomiar wskaźnika akceptacji

Wykonaj 10 000 kroków spekulatywnych przy różnych poziomach jakości wersji roboczej. Narysuj wykres wskaźnika akceptacji w zależności od rozbieżności KL między rozkładem modelu roboczego a weryfikatora. Powinieneś zaobserwować wyraźną, monotoniczną zależność.

### Krok 5: weryfikacja równoważności rozkładów

Empirycznie: histogram tokenów produkowanych przez pętlę spekulatywną powinien odpowiadać histogramowi uzyskanemu przez bezpośrednie próbkowanie z weryfikatora. To jest twierdzenie Levithana w praktyce. Test chi-kwadrat potwierdza błąd próbkowania.

## Użyj tego

Produkcja:

```bash
# vLLM with EAGLE
vllm serve meta-llama/Llama-3.1-70B-Instruct \
    --speculative-model /models/llama-3.1-eagle-70b \
    --speculative-draft-tensor-parallel-size 1 \
    --num-speculative-tokens 5

# vLLM with vanilla draft model
vllm serve meta-llama/Llama-3.1-70B-Instruct \
    --speculative-model meta-llama/Llama-3.2-1B-Instruct \
    --num-speculative-tokens 5
```

TensorRT-LLM dysponuje najszybszą ścieżką Meduzy od połowy 2026 roku. `faster-whisper` stosuje dekodowanie spekulatywne dla Whisper-large z małym modelem roboczym.

**Wybór modelu roboczego:**

| Strategia | Kiedy stosować | Przyspieszenie |
|---------|-------------|--------|
| Waniliowy model roboczy (rodzina Llama 1B/3B) | Szybki prototyp, bez trenowania | 1,8–2,3× |
| Głowice Meduzy | Możliwość dostrojenia weryfikatora | 2–3× |
| EAGLE-2 / 3 | Produkcja, maksymalna prędkość | 3–4× |
| Dekodowanie z wyprzedzeniem | Bez modelu roboczego, bez trenowania, bez dodatkowych parametrów | 1,3–1,6× |

**Kiedy NIE stosować dekodowania spekulatywnego:**

- Generowanie krótkich sekwencji (1–5 tokenów) — dominuje narzut.
- Próbkowanie z wysoką temperaturą i duża swoboda twórcza (wskaźnik α spada).
- Wdrożenia z ograniczoną pamięcią GPU (model roboczy zwiększa zużycie VRAM).

## Wyślij to

Zobacz `outputs/skill-spec-decode-picker.md`. Umiejętność dobiera spekulatywną strategię dekodowania (waniliową/Medusa/EAGLE/lookahead) oraz parametry strojenia (N, temperatura wersji roboczej) dla nowego obciążenia wnioskowania.

## Ćwiczenia

1. **Łatwe.** Uruchom `code/main.py`. Potwierdź, że rozkład tokenów generowany przez pętlę spekulatywną odpowiada rozkładowi uzyskanemu przez bezpośrednie próbkowanie z weryfikatora na 50 000 tokenach, przy p > 0,05 w teście chi-kwadrat.
2. **Średnie.** Wykreśl przyspieszenie (tokeny na wywołanie dużego modelu) jako funkcję `N` dla `α = 0.5, 0.7, 0.85`. Wyznacz optymalne `N` dla każdego α. (Wskazówka: oczekiwana liczba tokenów na wywołanie weryfikacyjne = `(1 - α^{N+1}) / (1 - α)`.)
3. **Trudne.** Zaimplementuj uproszczoną Meduzę: weź model GPT z lekcji 14, dodaj 3 dodatkowe głowice LM przewidujące pozycje t+2, t+3, t+4. Trenuj na zbiorze tinyshakespeare ze wspólną stratą wielogłowicową. Porównaj wskaźniki akceptacji z modelem roboczym uzyskanym przez obcięcie tego samego modelu.
4. **Trudne.** Zaimplementuj wycofywanie pamięci podręcznej KV: zacznij od 10-tokenowej pamięci podręcznej z prefiksem, podaj 5 tokenów roboczych, zasymuluj odrzucenie na pozycji 3. Sprawdź, czy odczyty z pamięci podręcznej poprawnie odpowiadają „prefiksowi + pierwsze 2 zaakceptowane tokeny robocze" w kolejnej iteracji.

## Kluczowe terminy

| Termin | Potoczne określenie | Właściwe znaczenie |
|------|-----------------|----------------------|
| Model roboczy | „Ten tani" | Mniejszy model proponujący tokeny kandydujące; zazwyczaj 10–50× tańszy od weryfikatora. |
| Weryfikator | „Ten duży" | Model docelowy, którego rozkład zachowujemy; uruchamiany raz na krok spekulatywny. |
| Wskaźnik akceptacji (α) | „Jak często model roboczy ma rację" | Prawdopodobieństwo akceptacji tokenu roboczego przez weryfikatora; typowo 0,7–0,9. |
| Rozkład rezydualny | „Reakcja na odrzucenie" | `(q - p)_+` znormalizowany; próbkowanie z tego rozkładu po odrzuceniu zachowuje rozkład weryfikatora. |
| Token bonusowy | „Ten darmowy" | Po zaakceptowaniu wszystkich N tokenów roboczych pobieramy jeszcze jeden z rozkładu następnego kroku weryfikatora. |
| Medusa | „Spekulacja bez modelu roboczego" | Wiele głowic LM na weryfikatorze przewidujących pozycje t+1..t+k równolegle. |
| EAGLE | „Szkic ze stanów ukrytych" | Mały transformer uwarunkowany stanami ukrytymi ostatniej warstwy weryfikatora. |
| Dekodowanie z wyprzedzeniem | „Iteracja Jacobiego" | Samospekulacja z użyciem iteracji punktu stałego; nie wymaga modelu roboczego. |
| Uwaga drzewiasta | „Weryfikacja wielu kandydatów naraz" | Rozgałęziona weryfikacja uwzględniająca jednocześnie kilka możliwych kontynuacji. |
| Wycofanie KV | „Cofnij odrzucone tokeny robocze" | Bufor pomocniczy KV; zatwierdzany po akceptacji, odrzucany po odrzuceniu. |

## Dalsze czytanie

- [Leviathan, Kalman, Matias (2023). Szybkie wnioskowanie z transformatorów poprzez dekodowanie spekulatywne](https://arxiv.org/abs/2211.17192) — podstawowy algorytm i twierdzenie o równoważności.
- [Chen i in. (2023). Przyspieszanie dekodowania dużych modeli językowych za pomocą próbkowania spekulatywnego](https://arxiv.org/abs/2302.01318) — niezależne wprowadzenie; przejrzysty dowód odrzucenia Bernoulliego.
- [Cai i in. (2024). Medusa: Prosta architektura przyspieszania wnioskowania LLM z wieloma głowicami dekodującymi](https://arxiv.org/abs/2401.10774) — artykuł o Medusie; weryfikacja z użyciem uwagi drzewiastej.
- [Li i in. (2024). EAGLE: Próbkowanie spekulatywne wymaga ponownego przemyślenia niepewności cech](https://arxiv.org/abs/2401.15077) — EAGLE-1; model roboczy uwarunkowany stanem ukrytym.
- [Li i in. (2024). EAGLE-2: Szybsze wnioskowanie modeli językowych z dynamicznymi drzewami roboczymi](https://arxiv.org/abs/2406.16858) — EAGLE-2; dynamiczna głębokość drzewa.
- [Li i in. (2025). EAGLE-3: Wzmocnienie przyspieszania wnioskowania w dużych modelach językowych przez uczenie w czasie testu](https://arxiv.org/abs/2503.01840) — EAGLE-3.
- [Fu i in. (2024). Przerwij sekwencyjną zależność wnioskowania LLM za pomocą dekodowania z wyprzedzeniem](https://arxiv.org/abs/2402.02057) — podejście z wyprzedzeniem, bez modelu roboczego.
- [Dokumentacja vLLM — Dekodowanie spekulatywne](https://docs.vllm.ai/en/latest/features/spec_decode.html) — kanoniczna dokumentacja produkcyjna obejmująca wszystkie cztery strategie.
- [Implementacja referencyjna SafeAILab / EAGLE](https://github.com/SafeAILab/EAGLE) — kod referencyjny dla EAGLE-1/2/3.
