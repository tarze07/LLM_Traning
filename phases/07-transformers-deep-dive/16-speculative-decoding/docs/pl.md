# Dekodowanie spekulatywne — wersja robocza, weryfikacja, powtórzenie

> Dekodowanie autoregresyjne jest szeregowe. Każdy token czeka na poprzedni. Dekodowanie spekulatywne przerywa łańcuch: tani model pobiera N tokenów, drogi model weryfikuje wszystkie N w jednym przebiegu do przodu. Kiedy draft jest odpowiedni, płacisz jednego dużego napastnika za N pokoleń.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 7 · 07 (przyczynowy LM GPT), faza 7 · 12 (pamięć podręczna KV i uwaga Flash)
**Czas:** ~60 minut

## Problem

Próbkowanie jednego tokena 70B LLM zajmuje ~30 ms na H100. Model roboczy 3B zajmuje ~3 ms. Jeśli pozwolimy firmie 3B na wybranie 5 tokenów z wyprzedzeniem, a następnie uruchomimy 70B *raz*, aby zweryfikować wszystkie 5, łączna liczba wyniesie `5×3 + 30 = 45 ms` dla maksymalnie 5 zaakceptowanych tokenów — w porównaniu do `5×30 = 150 ms` w przypadku generowania liniowego. To jest pełny zakres dekodowania spekulatywnego: zamień niewielką ilość dodatkowej pamięci GPU (model roboczy) na 2–4 ​​razy mniejsze opóźnienie dekodowania.

Sztuka polega na zachowaniu dystrybucji. Próbkowanie spekulatywne, wprowadzone przez Leviathan i in. (2023) oraz Chen i in. jednocześnie gwarantuje, że sekwencja wyjściowa jest **identycznie rozłożona** w stosunku do tej, którą duży model wygenerowałby samodzielnie. Żadnych kompromisów w zakresie jakości. Po prostu szybciej.

We wnioskowaniu na rok 2026 dominują cztery rodziny par weryfikatora wersji roboczej:

1. **Waniliowy spekulacyjny (Lewiatan 2023).** Oddzielny model roboczy (np. Lama 3 1B) + weryfikator (np. Lama 3 70B).
2. **Medusa (Cai 2024).** Wiele głowic dekodujących na weryfikatorze przewiduje pozycje `t+1..t+k` równolegle. Brak oddzielnego modelu roboczego.
3. **Rodzina EAGLE (Li 2024, 2025).** Lekka wersja robocza, która ponownie wykorzystuje ukryte stany weryfikatora; bliższy wskaźnik akceptacji niż waniliowy; 3–4× typowe.
4. **Dekodowanie z wyprzedzeniem (Fu 2024).** Iteracja Jacobiego; w ogóle nie jest wymagany projekt modelu. Spekulacje własne. Niszowa, ale wolna od zależności.

Każdy stos wnioskowania produkcyjnego w roku 2026 domyślnie zawiera dekodowanie spekulatywne. vLLM, TensorRT-LLM, SGLang i llama.cpp obsługują co najmniej wersję waniliową + EAGLE-2.

## Koncepcja

### Podstawowy algorytm

Biorąc pod uwagę weryfikator `M_q` i tańszą wersję roboczą `M_p`:

1. Niech `x_1..x_k` będzie już zdekodowanym przedrostkiem.
2. **Draft**: użyj `M_p`, aby autoregresywnie zaproponować `d_{k+1}, d_{k+2}, ..., d_{k+N}` z prawdopodobieństwami draftu `p_1..p_N`.
3. **Weryfikuj równolegle**: uruchom `M_q` raz na `x_1..x_k, d_{k+1}, ..., d_{k+N}`, uzyskując prawdopodobieństwa weryfikatora `q_1..q_{N+1}` dla pozycji `k+1..k+N+1`.
4. **Zaakceptuj/odrzuć każdy żeton wersji roboczej od lewej do prawej**: dla każdego `i` zaakceptuj z prawdopodobieństwem `min(1, q_i(d_i) / p_i(d_i))`.
5. Przy pierwszym odrzuceniu na pozycji `j`: próbka `t_j` z rozkładu „resztkowego” `(q_j - p_j)_+` znormalizowana. Wszystkie wersje robocze po `j` są odrzucane.
6. Po zaakceptowaniu wszystkich `N`: wypróbuj jeden dodatkowy token `t_{N+1}` z `q_{N+1}` (bezpłatny token bonusowy).

Sztuczka z rozkładem rezydualnym polega na matematycznym wglądzie, który utrzymuje rozkład wyników dokładnie tak, jakby `M_q` próbkował od zera.

### Co decyduje o przyspieszeniu

Niech `α` = oczekiwany współczynnik akceptacji na token wersji roboczej. Niech `c` = stosunek kosztów wersji roboczej do weryfikatora. Na krok:

- Naiwne pokolenie wykonuje 1 wywołanie dużego modelu na token.
- Spekulacyjny wykonuje 1 wywołanie dużego modelu na tokeny `(1 - α^{N+1}) / (1 - α) ≈ 1/(1-α)`, gdy wartość `α` jest wysoka.

Typowa praktyczna zasada w `α = 0.75` i `N = 5`: 3 razy mniej wywołań dużych modeli. Koszt wersji roboczej jest 5 razy tani. Całkowity spadek zegara ściennego ~2,5×.

**α zależy od:**

- W jakim stopniu projekt jest zbliżony do weryfikatora. Ta sama rodzina / te same dane treningowe znacznie zwiększają α.
- Strategia dekodowania. Chciwy projekt przeciwko zachłannemu weryfikatorowi: wysokie α. Próbkowanie temperatury: trudniejsze do dopasowania; spada akceptacja.
- Typ zadania. Kod i ustrukturyzowane dane wyjściowe akceptują więcej (przewidywalne); kreatywne pisanie w dowolnej formie akceptuje mniej.

### Meduza — szkice bez modelu szkicu

Medusa zastępuje model roboczy dodatkowymi głowicami wyjściowymi na weryfikatorze. Na pozycji `t`:

```
shared trunk → hidden h_t
    ├── head_0: predict token at t+1  (standard LM head)
    ├── head_1: predict token at t+2
    ├── head_2: predict token at t+3
    ├── head_3: predict token at t+4
```

Każda głowa wyprowadza własne logity. Wnioskując, pobierasz próbkę z każdej głowy, aby uzyskać sekwencję kandydatów, a następnie weryfikujesz jednym przejściem do przodu, korzystając ze schematu uwagi w postaci drzewa, który uwzględnia wszystkie potencjalne kontynuacje na raz.

Plusy: brak drugiego modelu. Wady: dodaje parametry, które można trenować; wymaga nadzorowanego etapu dostrajania (~1 miliard tokenów); współczynnik akceptacji jest nieco niższy niż waniliowy spekulacyjny z dobrym draftem.

### EAGLE — lepszy szkic dzięki ponownemu wykorzystaniu ukrytych stanów

EAGLE-1/2/3 (Li et al., 2024–2025) sprawia, że model roboczy jest małym transformatorem (zwykle 1 warstwa), który przyjmuje ukryte stany ostatniej warstwy weryfikatora. Ponieważ projekt uwzględnia reprezentację cech weryfikatora, jego przewidywania są silnie skorelowane z rozkładem wyników weryfikatora. Wskaźnik akceptacji wzrasta z ~0,6 (waniliowy) do 0,85+.

W programie EAGLE-3 (2025) dodano wyszukiwanie drzew w poszukiwaniu kontynuacji kandydatów. vLLM i SGLang dostarczają EAGLE-2/3 jako domyślną ścieżkę specyfikacji dla Llama 3/4 i Qwen 3.

### Taniec pamięci podręcznej KV

Weryfikacja dostarcza `N` wersję roboczą tokenów do weryfikatora w jednym przebiegu do przodu. Rozszerza to pamięć podręczną KV weryfikatora o wpisy `N`. Jeśli niektóre wersje robocze zostaną odrzucone, należy przywrócić pamięć podręczną do zaakceptowanej długości prefiksu.

Implementacje produkcyjne (`--speculative-model` firmy vLLM, LookaheadDecoder firmy TensorRT-LLM) radzą sobie z tym za pomocą buforów KV. Najpierw napisz, zobowiąż się do akceptacji. Nie jest to koncepcyjnie trudne, ale jest kłopotliwe.

## Zbuduj to

Zobacz `code/main.py`. Implementujemy podstawowy algorytm próbkowania spekulatywnego (krok odrzucenia + rozkład rezydualny) za pomocą:

- „Duży model”, czyli deterministyczny softmax na podstawie ręcznie zakodowanej dystrybucji (abyśmy mogli analitycznie zweryfikować matematykę akceptacji).
- „Model roboczy”, czyli zaburzenie dużego modelu.
- Pętla akceptacji/odrzucenia, która daje taki sam rozkład krańcowy jak bezpośrednie próbkowanie.

### Krok 1: krok odrzucenia

```python
def accept_or_reject(q_prob, p_prob, draft_token, u):
    ratio = q_prob / p_prob if p_prob > 0 else float("inf")
    return u < min(1.0, ratio)
```

`u` to jednolita liczba losowa. `q_prob` to prawdopodobieństwo weryfikatora dla wygenerowanego tokena. `p_prob` to prawdopodobieństwo wersji roboczej modelu. Twierdzenie Lewiatana głosi, że decyzja Bernoulliego, po której następuje próbkowanie z reszty po odrzuceniu, dokładnie zachowuje rozkład weryfikatora.

### Krok 2: dystrybucja rezydualna

```python
def residual_dist(q, p):
    raw = [max(0.0, qi - pi) for qi, pi in zip(q, p)]
    s = sum(raw)
    return [r / s for r in raw]
```

Odejmij `p` od `q` elementarnie, zmniejsz wartości ujemne do zera, renormalizuj. Próbka z tego w przypadku jakiegokolwiek odrzucenia.

### Krok 3: jeden krok spekulacyjny

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

Pięć zaakceptowanych → jeden bonus → sześć tokenów wyprodukowanych w jednym przejściu weryfikatora.

### Krok 4: zmierz współczynnik akceptacji

Wykonaj 10 000 spekulacyjnych kroków przy różnych poziomach jakości wersji roboczej. Wskaźnik akceptacji wykresu a rozbieżność KL pomiędzy rozkładem wersji roboczej i weryfikatora. Powinieneś zobaczyć czysty, monotonny związek.

### Krok 5: sprawdź równoważność dystrybucji

Empirycznie: histogram tokenów wytworzony przez pętlę spekulatywną powinien odpowiadać histogramowi wytworzonemu w wyniku próbkowania bezpośrednio z weryfikatora. Oto twierdzenie Lewiatana w praktyce. Test chi-kwadrat potwierdza błąd próbkowania.

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

TensorRT-LLM ma najszybszą ścieżkę Meduzy od połowy 2026 r. `faster-whisper` zamyka dekodowanie spekulatywne dla Whisper-large w małej wersji roboczej.

**Wybieram wersję roboczą:**

| Strategia | Kiedy wybrać | Przyspieszenie |
|---------|-------------|--------|
| Waniliowy projekt (rodzina 1B/3B Lama) | Szybki prototyp, bez szkolenia | 1,8–2,3× |
| Głowy Meduzy | Możesz dostroić weryfikator | 2–3× |
| ORZEŁ-2 / 3 | Produkcja, maksymalna prędkość | 3–4× |
| Wyprzedzenie | Bez draftu, bez szkoleń, bez dodatkowych parametrów | 1,3–1,6× |

**Kiedy NIE należy dekodować według specyfikacji:**

- Generowanie pojedynczej sekwencji 1–5 tokenów. Dominuje narzut.
- Niezwykle kreatywne / próbkowanie w wysokiej temperaturze (krople α).
- Wdrożenia z ograniczoną pamięcią (wersja robocza dodaje VRAM).

## Wyślij to

Zobacz `outputs/skill-spec-decode-picker.md`. Umiejętność wybiera spekulatywną strategię dekodowania (wanilia/meduza/EAGLE/lookahead) i parametry dostrajania (N, temperatura przeciągu) dla nowego obciążenia wnioskowania.

## Ćwiczenia

1. **Łatwe.** Uruchom `code/main.py`. Potwierdź, że spekulacyjny rozkład tokenów odpowiada rozkładowi bezpośredniej próby weryfikatora na 50 000 tokenów w zakresie chi-kwadrat p > 0,05.
2. **Średni.** Przyspieszenie wydruku (tokeny na przesyłanie dużego modelu) jako funkcja `N` dla `α = 0.5, 0.7, 0.85`. Zidentyfikuj optymalny `N` dla każdego α. (Wskazówka: oczekiwana liczba tokenów na wywołanie weryfikacyjne = `(1 - α^{N+1}) / (1 - α)`.)
3. **Trudne.** Zaimplementuj małą Meduzę: weź zwieńczenie GPT z lekcji 14, dodaj 3 dodatkowe głowy LM, które przewidują pozycje t+2, t+3, t+4. Trenuj na tinyshakespeare ze wspólną, wielogłową stratą. Porównaj współczynniki akceptacji z wersją roboczą utworzoną przez obcięcie tego samego modelu.
4. **Trudne.** Zaimplementuj wycofywanie zmian: zacznij od 10-tokenowej pamięci podręcznej KV z prefiksem, podaj 5 tokenów roboczych, symuluj odrzucenie na pozycji 3. Sprawdź, czy odczyty pamięci podręcznej prawidłowo odpowiadają „prefiksowi + pierwsze 2 zaakceptowane wersje robocze” podczas następnej iteracji.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Projekt modelu | „Ten tani” | Mniejszy model, który proponuje tokeny kandydujące; zwykle 10–50× taniej niż weryfikator. |
| Weryfikator | „Ten duży” | Model docelowy, którego dystrybucję zachowujemy; uruchamia się raz na krok spekulacyjny. |
| Wskaźnik akceptacji (α) | „Jak często projekt jest słuszny” | Prawdopodobieństwo na token, że weryfikator zaakceptuje wersję roboczą. typowo 0,7–0,9. |
| Pozostała dystrybucja | „Reakcja na odrzucenie” | `(q - p)_+` znormalizowany; pobieranie próbek z tego po odrzuceniu zachowuje rozkład weryfikatora. |
| Żeton bonusowy | „Ten darmowy” | Po zaakceptowaniu wszystkich N wersji roboczych, należy pobrać jeszcze jedną próbkę z rozkładu następnego kroku weryfikatora. |
| Meduza | „Spekulacyjny bez przeciągów” | Wiele głowic LM na weryfikatorze przewiduje pozycje t+1..t+k równolegle. |
| ORZEŁ | „Szkic w stanie ukrytym” | Mały ciąg transformatora uwarunkowany stanami ukrytymi ostatniej warstwy weryfikatora. |
| Dekodowanie z wyprzedzeniem | „Iteracja Jacobiego” | Samospekulacja przy użyciu iteracji stałoprzecinkowej; brak modelu roboczego. |
| Uwaga drzewa | „Weryfikuj wielu kandydatów na raz” | Weryfikacja rozgałęziona, która uwzględnia jednocześnie kilka kontynuacji wersji roboczej. |
| Cofnięcie KV | „Cofnij odrzucone wersje robocze” | Bufor Scratch KV; zatwierdzić po akceptacji, odrzucić po odrzuceniu. |

## Dalsze czytanie

- [Lewiatan, Kalman, Matias (2023). Szybkie wnioskowanie z transformatorów poprzez dekodowanie spekulatywne](https://arxiv.org/abs/2211.17192) — podstawowy algorytm i twierdzenie o równoważności.
- [Chen i in. (2023). Przyspieszanie dekodowania modeli wielkojęzykowych za pomocą próbkowania spekulatywnego](https://arxiv.org/abs/2302.01318) — wprowadzenie równoległe; czysty dowód odrzucenia Bernoulliego.
- [Cai i in. (2024). Medusa: Prosta struktura przyspieszania wnioskowania LLM z wieloma głowicami dekodującymi](https://arxiv.org/abs/2401.10774) — artykuł Medusa; weryfikacja uwagi drzewa.
- [Li i in. (2024). EAGLE: Próbkowanie spekulatywne wymaga ponownego przemyślenia niepewności funkcji](https://arxiv.org/abs/2401.15077) — EAGLE-1; Przeciąg uwarunkowany stanem ukrytym.
- [Li i in. (2024). EAGLE-2: Szybsze wnioskowanie modeli językowych za pomocą dynamicznych drzew roboczych](https://arxiv.org/abs/2406.16858) — EAGLE-2; dynamiczna głębokość drzewa.
- [Li i in. (2025). EAGLE-3: Zwiększanie przyspieszania wnioskowania w dużych modelach językowych poprzez test czasu szkolenia](https://arxiv.org/abs/2503.01840) — EAGLE-3.
- [Fu i in. (2024). Przerwij zależność sekwencyjną wnioskowania LLM za pomocą dekodowania z wyprzedzeniem](https://arxiv.org/abs/2402.02057) — podejście z wyprzedzeniem, bez wersji roboczej.
- [dokumentacja vLLM — Dekodowanie spekulatywne] (https://docs.vllm.ai/en/latest/features/spec_decode.html) — kanoniczne odniesienie do produkcji z podłączonymi wszystkimi czterema strategiami.
- [Implementacja referencyjna SafeAILab / EAGLE](https://github.com/SafeAILab/EAGLE) — kod referencyjny dla EAGLE-1/2/3.