# Dekodowanie spekulatywne i EAGLE

> Frontier LLM generujący jeden token wymaga pełnego przejścia w przód przez miliardy parametrów. To podanie w przód jest znacznie przesadzone: w większości przypadków znacznie mniejszy model może poprawnie odgadnąć kolejne 3-5 żetonów, a duży model musi jedynie *zweryfikować* przypuszczenie. Jeśli odgadniesz prawidłowo, otrzymasz 5 żetonów w cenie jednego. Dekodowanie spekulatywne (Leviathan et al. 2023) dokładnie to sprawdziło, a EAGLE-3 (2025) podwyższyło współczynniki akceptacji do ~4,5 tokenów na weryfikację – co oznacza przyspieszenie 4-5x przy dopasowanej dystrybucji wyników.

**Typ:** Kompilacja
**Języki:** Python (z numpy)
**Wymagania wstępne:** Faza 10, lekcja 12 (optymalizacja wnioskowania), faza 10, lekcja 04 (przedtreningowy Mini-GPT)
**Czas:** ~75 minut

## Problem

Przepustowość dekodowania dla modelu klasy 70B na H100 wynosi zazwyczaj 40-80 tokenów/sekundę. Każdy token wymaga pełnego przejścia w przód odczytującego wszystkie wagi modeli z HBM. Nie można zmniejszyć modelu bez zmiany jego wyników. Nie można zwiększyć rozmiaru partii poza pamięć. Utknąłeś — chyba że możesz pozwolić, aby model wygenerował więcej niż jeden token na każde przejście do przodu.

Generowanie autoregresyjne ma z natury charakter szeregowy: `x_{t+1} = sample(p(· | x_{1:t}))`. Istnieje jednak możliwość współbieżności. Jeśli masz tani predyktor, który mówi, że „następne 4 tokeny to prawdopodobnie [a, b, c, d]”, możesz zweryfikować wszystkie 5 pozycji w **pojedynczym przejściu dużego modelu** do przodu i zaakceptować najdłuższy pasujący przedrostek.

Leviathan, Kalai, Matias (2023, „Fast Inference from Transformers via Speculative Decoding”) osiągnęli ten cel dzięki sprytnej zasadzie akceptacji/odrzucenia, która zachowuje rozkład próbkowania modelu docelowego. Ta sama dystrybucja mocy wyjściowej, 2-4 razy szybciej.

## Koncepcja

### Konfiguracja dwóch modeli

- **Model docelowy** `M_p`: duży, powolny model o wysokiej jakości, z którego faktycznie chcesz pobrać próbki. Dystrybucja: `p(x)`.
- **Model roboczy** `M_q`: mały, szybki model o niższej jakości. Dystrybucja: `q(x)`. 5-30× mniejszy.

Na krok:

1. Szkic modelu proponuje autoregresywnie tokeny `K`: `x_1, x_2, ..., x_K ~ q`.
2. Model docelowy uruchamia JEDNĄ transmisję w przód przez wszystkie pozycje `K+1` równolegle, tworząc `p(x_k)` dla każdego proponowanego tokena.
3. Zaakceptuj/odrzuć każdy token od lewej do prawej, korzystając ze zmodyfikowanej reguły próbkowania odrzuconego poniżej. Zaakceptuj najdłuższy pasujący prefiks.
4. Jeżeli którykolwiek token zostanie odrzucony, pobierz próbkę zamiennika z poprawionej dystrybucji i zatrzymaj się. W przeciwnym razie wypróbuj jeden token bonusowy z `p(· | x_1...x_K)`.

Jeśli draft idealnie pasuje do celu, otrzymujesz żetony K+1 za każdego napastnika. Jeśli draft jest błędny na pozycji 1, otrzymujesz tylko 1 żeton.

### Zasada dokładności

Dekodowanie spekulatywne jest **w sposób możliwy do udowodnienia równoważne w dystrybucji próbkowaniu z p**. Zasada odrzucenia:

```
For each drafted token x_t:
    r ~ Uniform(0, 1)
    if r < p(x_t) / q(x_t):
        accept x_t
    else:
        sample replacement from residual: (p - q)+ / ||(p - q)+||_1
        stop
```

gdzie `(p - q)+` oznacza dodatnią część różnicy punktowej. Kiedy wersja robocza i cel są zgodne (`p ≈ q`), akceptacja jest prawie 1. Kiedy się nie zgadzają, rozkład resztowy jest konstruowany w taki sposób, że ogólna próbka nadal wynosi dokładnie `p`.

**Chciwy przypadek.** Dla próbkowania w temperaturze = 0 po prostu sprawdź `argmax(p) == x_t`. Jeśli tak, zaakceptuj; jeśli nie, wypisz `argmax(p)` i zatrzymaj.

### Oczekiwane przyspieszenie

Jeśli współczynnik akceptacji na poziomie tokenu w modelu roboczym wynosi `α`, oczekiwane tokeny wygenerowane w ramach przekazania docelowego wynoszą:

```
E[tokens] = (1 - α^{K+1}) / (1 - α)        # K = draft length, α in [0, 1]
```

W `α = 0.8, K = 4`: `(1 - 0.8^5)/(1 - 0.8) = 3.36` tokenów na forward. Koszt przekazania pojedynczego celu wynosi mniej więcej `cost_q * K + cost_p` (K kroków draftu plus jedna weryfikacja celu). Jeśli `cost_p >> cost_q * K` współczynnik przyspieszenia wynosi `3.36× / 1 = 3.36×` przepustowości.

Jedynym prawdziwym parametrem jest `α`, który zależy całkowicie od wyrównania wersji roboczej i docelowej. Dobry projekt to wszystko.

### Szkolenie przeciągu: destylacja

Przypadkowy mały model ma słaby przeciąg. Standardowa receptura polega na destylacji z celu:

1. Wybierz małą architekturę (~1B dla celu 70B, ~500M dla celu 7B).
2. Uruchom model docelowy na dużym korpusie tekstowym; przechowuj dystrybucje następnego tokenu.
3. Trenuj pobór z rozbieżnością KL w stosunku do rozkładu celu (nie w stosunku do żetonów prawdy).

Wynik: `α` zazwyczaj 0,6–0,8 w przypadku kodowania, 0,7–0,85 w czacie w języku naturalnym. Przyspieszenie 2-3× w produkcji.

### EAGLE: Rysowanie drzewa + ponowne wykorzystanie funkcji

Li, Wei, Zhang, Zhang (2024, „EAGLE: Speculative Sampling Requires Rethinking Feature Uncertainty”) zaobserwowali dwie nieefektywności w standardowym dekodowaniu spekulatywnym:

1. Draft składa się z K kroków seryjnych, każdy z pełnym stosem. Jednak wersja robocza może ponownie wykorzystać funkcje celu (ukryte stany) z ostatniej weryfikacji — cel obliczył już bogate reprezentacje, które wersja robocza ponownie wyprowadza od zera.
2. Projekt generuje łańcuch liniowy. Jeśli wersja robocza mogłaby wygenerować *drzewo* kandydatów (każdy węzeł wiele razy odgaduje), pojedyncze przejście w przód celu mogłoby zweryfikować wiele ścieżek kandydatów równolegle za pomocą maski uwagi drzewa i wybrać najdłuższą akceptowaną gałąź.

Zmiany w EAGLE-1:
- Dane wejściowe wersji roboczej = ostateczny ukryty stan celu na pozycji t, a nie surowe żetony.
- Architektura robocza = 1 warstwa dekodera transformatora (nie osobny mały model).
- Wyjście = drzewo K = 4-8 kandydatów na głębokość, głębokość 4-6.

EAGLE-2 (2024) dodaje dynamiczną topologię drzewa: drzewo staje się szersze tam, gdzie zanurzenie jest niepewne i pozostaje wąskie tam, gdzie jest pewne. Podnosi `α_effective` bez zwiększania kosztu weryfikacji.

EAGLE-3 (Li et al. 2025, „EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test”) usuwa stałą zależność funkcji górnej warstwy i uczy wersję roboczą z nową stratą „symulacji czasu testu” — wersja robocza jest trenowana na wynikach, które odpowiadają docelowemu rozkładowi czasu testowania, a nie rozkładowi szkoleń wymuszanemu przez nauczyciela. Współczynnik akceptacji wzrasta z 0,75 (EAGLE-2) do 0,82 (EAGLE-3), a średnia liczba tokenów/weryfikacji z 3,0 do 4,5.

### Weryfikacja uwagi drzewa

Kiedy wersja robocza generuje drzewo, model docelowy weryfikuje je w jednym przebiegu do przodu, używając **maski uwagi drzewa** — maski przyczynowej, która koduje topologię drzewa, a nie czystą linię. Każdy token dotyczy tylko swoich przodków w drzewie. Podanie sprawdzające to nadal jeden do przodu, jeden matmul; maska ​​topologiczna kosztuje tylko kilka dodatkowych wpisów KV.

```
        root
       /    \
      a      b
     / \    / \
    c  d   e   f
```

Jeśli `a, b` konkurują z kandydatami na pierwszy token, a `c, d, e, f` to kandydaci na drugi token, wszystkie sześć pozycji jest weryfikowanych w jednym przejściu do przodu. Dane wyjściowe to najdłuższy prefiks na dowolnej akceptowanej ścieżce.

### Kiedy wygrywa, kiedy nie

**Wygrywa:**
- Czat / uzupełnienie przewidywalnym tekstem (kod, wspólny angielski, uporządkowane dane wyjściowe). `α` jest wysoki.
- Ustawienia z nieużywanym procesorem graficznym podczas dekodowania (faza związana z pamięcią). Rysowanie drzewa wykorzystuje dostępne FLOPy.

**Przegrana / brak wygranej:**
- Wysoce stochastyczne wyniki (kreatywne pisanie w wysokiej temperaturze). `α` spada w stronę `1/|vocab|`.
- Serwowanie wsadowe z bardzo dużą współbieżnością - wsadowanie już wypełnia FLOPy, mało miejsca na weryfikację drzewa.
- Bardzo małe modele docelowe, w których zanurzenie nie jest dużo mniejsze.

Warsztaty produkcyjne zazwyczaj zgłaszają 2-3-krotne przyspieszenie zegara ściennego na czacie, 3-5-krotne przy generowaniu kodu i prawie zerowe przy kreatywnym pisaniu.

## Zbuduj to

`code/main.py`:

- Odniesienie `speculative_decode(target, draft, prompt, K, temperature)`, które implementuje dokładną regułę odrzucania i weryfikuje, czy zachowuje rozkład elementu docelowego (empiryczny KL < 0,01 w porównaniu ze zwykłym próbkowaniem docelowym).
- Kreator drzew w stylu EAGLE, który buduje drzewo o głębokości K z rozgałęzieniami u góry.
- Konstruktor maski uwagi drzewa, który tworzy właściwy wzór przyczynowy dla weryfikatora.
- Uprząż współczynnika akceptacji, która działa na małym LM (wydestyluj jeden mały GPT-2 ze średniego celu GPT-2).

```python
def speculative_step(p_target, q_draft, K, temperature=1.0):
    """One round of speculative decoding. Returns list of accepted tokens."""
    # 1. Draft K tokens
    draft_tokens = []
    q_probs = []
    state = draft_state_init()
    for _ in range(K):
        probs = softmax(q_draft(state) / temperature)
        t = np.random.choice(len(probs), p=probs)
        draft_tokens.append(t)
        q_probs.append(probs[t])
        state = draft_step(state, t)

    # 2. Target computes p at every drafted position + 1 extra
    p_probs_all = target_forward_batched(p_target, draft_tokens, temperature)

    # 3. Accept/reject left-to-right
    accepted = []
    for k, tok in enumerate(draft_tokens):
        r = np.random.uniform()
        if r < p_probs_all[k][tok] / q_probs[k]:
            accepted.append(tok)
        else:
            residual = np.maximum(p_probs_all[k] - q_probs[k], 0)
            residual /= residual.sum()
            accepted.append(np.random.choice(len(residual), p=residual))
            return accepted
    # 4. All K accepted → sample bonus token from target
    accepted.append(np.random.choice(len(p_probs_all[-1]), p=p_probs_all[-1]))
    return accepted
```

## Użyj tego

- **vLLM** i **SGLang** oferują najwyższej klasy dekodowanie spekulatywne. Flagi: `--speculative_model`, `--num_speculative_tokens`. Obsługa EAGLE-2/3 poprzez flagę `--spec_decoding_algorithm eagle`.
- **NVIDIA TensorRT-LLM** natywnie obsługuje drzewa Medusa i EAGLE.
- **Modele referencyjne**: `Qwen/Qwen3-0.6B-spec` (wersje robocze dla Qwen3-32B), `meta-llama/Llama-3.2-1B-Instruct-spec` (wersje robocze dla 70B).
- **Główki Meduzy** (Cai et al. 2024, „Medusa: Simple LLM Inference Acceleration Framework with Multiple Decoding Heads”): zamiast modelu roboczego dodaj K równoległych głowic predykcyjnych do samego celu. Prostsze we wdrożeniu, nieco niższa akceptacja niż EAGLE.

## Wyślij to

Ta lekcja pozwala uzyskać `outputs/skill-speculative-tuning.md` — umiejętność profilowania obciążenia modelu docelowego i wybierania: modelu roboczego, K (długości roboczej), szerokości drzewa, temperatury i momentu powrotu do zwykłego dekodowania.

## Ćwiczenia

1. Zastosuj dokładną regułę odrzucenia i zweryfikuj ją empirycznie. Uruchom 10 tys. próbek za pomocą `speculative_decode` i zwykłego próbkowania docelowego; obliczyć odległość TV pomiędzy dwoma rozkładami wyjściowymi. Powinno być < 0,01.

2. Oblicz wzór na przyspieszenie. Biorąc pod uwagę ustalone wartości `α` i `K`, wykreśl oczekiwane tokeny według elementu docelowego. Znajdź optymalne K dla α ∈ {0,5, 0,7, 0,9}.

3. Trenuj mały przeciąg. Weź cel 124M GPT-2 i wydestyluj 30M draftu GPT-2 na 100M tokenów ze stratą KL. Zmierz `α` na odsuniętym tekście. Oczekiwane: 0,6-0,7.

4. Zaimplementuj kreślenie drzew w stylu EAGLE. Zamiast łańcucha, ustaw wyjściowy ciąg 3 górnych gałęzi na każdej głębokości. Zbuduj maskę uwagi drzewa. Sprawdź, czy cel akceptuje najdłuższą poprawną gałąź.

5. Zmierz tryby awarii. Uruchom dekodowanie spekulatywne w temperaturze = 1,5 (wysoka stochastyczność). Pokaż α załamuje się, a algorytm jest wolniejszy niż zwykłe dekodowanie z powodu narzutu roboczego.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| Model docelowy | „Wielki model” | Powolny, wysokiej jakości model, z którego chcesz pobrać próbki (rozkład p) |
| Projekt modelu | „Spekulant” | Mały, szybki predyktor (rozkład q); 5-30x mniejszy |
| K / długość zanurzenia | „Patrz w przyszłość” | Liczba spekulowanych tokenów na przejście weryfikacji |
| α / współczynnik akceptacji | „Wskaźnik trafień” | Prawdopodobieństwo na token, że propozycja projektu została zaakceptowana |
| Dokładna zasada odrzucenia | „Test akceptacji” | r < p/q porównanie, które zachowuje rozkład celu |
| Pozostała dystrybucja | „Poprawione p-q” | (p - q)+ / ||(p - q)+||_1, rozkład do próbki z chwili odrzucenia |
| Projektowanie drzewa | „Rozgałęzianie spekulacji” | Wersja robocza generuje drzewo kandydatów, weryfikowane w jednym przebiegu za pomocą maski uwagi o strukturze drzewa |
| Maska uwagi drzewa | „Maska topologiczna” | Maska przyczynowa kodująca topologię drzewa, dzięki czemu każdy węzeł obsługuje tylko swoich przodków |
| Głowy Meduzy | „Równoległe głowy” | K dodatkowych głowic prognostycznych na samym celu; brak odrębnego projektu modelu |
| Ponowne wykorzystanie funkcji EAGLE | „Szkic w stanie ukrytym” | Dane wejściowe wersji roboczej to ostatni ukryty stan celu, a nie surowe tokeny, co zmniejsza wersję roboczą |
| Strata symulacji w czasie testu | „Szkolenie EAGLE-3” | Trenuj wersję roboczą na wynikach odpowiadających docelowemu rozkładowi czasu testu, a nie narzucaniu nauczycielowi |

## Dalsze czytanie

- [Lewiatan, Kalai, Matias, 2023 — „Fast Inference from Transformers via Speculative Decoding”](https://arxiv.org/abs/2211.17192) — dokładna reguła odrzucenia i teoretyczna analiza przyspieszenia
– [Chen, Borgeaud, Irving i in., 2023 — „Acceleating Large Language Model Decoding with Speculative Sampling”](https://arxiv.org/abs/2302.01318) — równoległy artykuł dotyczący próbkowania spekulatywnego w DeepMind
– [Cai, Li, Geng, Wang, Wang, Zhu, Dao, 2024 — „Medusa: prosta struktura przyspieszania wnioskowania LLM z wieloma głowicami dekodującymi”](https://arxiv.org/abs/2401.10774) — alternatywa dla modelu roboczego z równoległymi głowicami
– [Li, Wei, Zhang, Zhang, 2024 — „EAGLE: próbkowanie spekulatywne wymaga ponownego przemyślenia niepewności funkcji”](https://arxiv.org/abs/2401.15077) — ponowne wykorzystanie funkcji i kreślenie drzewa
- [Li et al., 2024 — „EAGLE-2: Faster Inference of Language Models with Dynamic Draft Trees”](https://arxiv.org/abs/2406.16858) — dynamiczna topologia drzewa
- [Li i in., 2025 — „EAGLE-3: Skalowanie przyspieszania wnioskowania w dużych modelach językowych za pomocą testu czasu uczenia”](https://arxiv.org/abs/2503.01840) — dopasowywanie czasu testu i czasu pociągu
- [Fu, Haotian, Peng et al., 2024 — „Przerwij zależność sekwencyjną wnioskowania LLM przy użyciu dekodowania z wyprzedzeniem”](https://arxiv.org/abs/2402.02057) — Dekodowanie Jacobi/lookahead, alternatywa wolna od spekulantów