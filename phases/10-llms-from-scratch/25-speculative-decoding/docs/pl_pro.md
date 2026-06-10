# Dekodowanie spekulatywne i EAGLE

> Frontier LLM generujący pojedynczy token wymaga pełnego przejścia w przód przez miliardy parametrów. To przejście jest jednak w dużej mierze zbędne: w większości przypadków znacznie mniejszy model potrafi trafnie przewidzieć kolejne 3–5 tokenów, a duży model musi jedynie *zweryfikować* tę propozycję. Jeśli przewidywanie jest słuszne, uzyskujemy 5 tokenów kosztem jednego. Dekodowanie spekulatywne (Leviathan et al. 2023) wykorzystało dokładnie tę własność, a EAGLE-3 (2025) podniósł współczynniki akceptacji do ~4,5 tokena na weryfikację — co przekłada się na 4–5-krotne przyspieszenie przy zachowaniu zgodnego rozkładu wyjść.

**Typ:** Kompilacja
**Języki:** Python (z numpy)
**Wymagania wstępne:** Faza 10, lekcja 12 (optymalizacja wnioskowania), faza 10, lekcja 04 (przedtreningowy Mini-GPT)
**Czas:** ~75 minut

## Problem

Przepustowość dekodowania dla modelu klasy 70B na H100 wynosi typowo 40–80 tokenów/sekundę. Każdy token wymaga pełnego przejścia w przód, podczas którego odczytywane są wszystkie wagi modelu z HBM. Nie można zmniejszyć modelu bez zmiany jego wyników, ani zwiększyć rozmiaru wsadu ponad dostępną pamięć. Wyjście z tej pułapki jest możliwe tylko wtedy, gdy model generuje więcej niż jeden token na jedno przejście do przodu.

Generowanie autoregresyjne ma z natury charakter szeregowy: `x_{t+1} = sample(p(· | x_{1:t}))`. Istnieje jednak możliwość wprowadzenia współbieżności. Jeśli dysponujemy tanim predyktorem, który proponuje „następne 4 tokeny to prawdopodobnie [a, b, c, d]", możemy zweryfikować wszystkie 5 pozycji w **pojedynczym przejściu dużego modelu** do przodu i zaakceptować najdłuższy pasujący prefiks.

Leviathan, Kalai, Matias (2023, „Fast Inference from Transformers via Speculative Decoding") osiągnęli ten cel dzięki przemyślanej regule akceptacji/odrzucenia, która zachowuje rozkład próbkowania modelu docelowego. Wynik jest identyczny pod względem rozkładu, lecz generowany 2–4 razy szybciej.

## Koncepcja

### Konfiguracja dwóch modeli

- **Model docelowy** `M_p`: duży, wolny model wysokiej jakości, z którego faktycznie chcemy pobierać próbki. Rozkład: `p(x)`.
- **Model roboczy** `M_q`: mały, szybki model o niższej jakości. Rozkład: `q(x)`. 5–30× mniejszy.

Na każdy krok:

1. Model roboczy proponuje autoregresywnie `K` tokenów: `x_1, x_2, ..., x_K ~ q`.
2. Model docelowy wykonuje JEDNO przejście w przód przez wszystkie `K+1` pozycji równolegle, wyznaczając `p(x_k)` dla każdego zaproponowanego tokena.
3. Tokeny są akceptowane lub odrzucane od lewej do prawej zgodnie ze zmodyfikowaną regułą próbkowania z odrzuceniem opisaną poniżej. Przyjmowany jest najdłuższy pasujący prefiks.
4. Jeśli którykolwiek token zostaje odrzucony, pobierana jest próbka zastępcza z rozkładu resztowego i algorytm się zatrzymuje. W przeciwnym razie pobierany jest jeden dodatkowy token z `p(· | x_1...x_K)`.

Gdy propozycja robocza idealnie pokrywa się z celem, uzyskujemy K+1 tokenów za jedną weryfikację. Gdy propozycja jest błędna już na pierwszej pozycji, uzyskujemy tylko 1 token.

### Zasada dokładności

Dekodowanie spekulatywne jest **w sposób udowodniony równoważne** próbkowaniu z rozkładu `p`. Reguła odrzucenia:

```
For each drafted token x_t:
    r ~ Uniform(0, 1)
    if r < p(x_t) / q(x_t):
        accept x_t
    else:
        sample replacement from residual: (p - q)+ / ||(p - q)+||_1
        stop
```

gdzie `(p - q)+` oznacza dodatnią część różnicy punktowej. Gdy model roboczy i docelowy są zgodne (`p ≈ q`), prawdopodobieństwo akceptacji zbliża się do 1. W przeciwnym razie rozkład resztowy jest skonstruowany tak, że łączna próbka odpowiada dokładnie rozkładowi `p`.

**Przypadek zachłanny.** Przy próbkowaniu z temperaturą = 0 wystarczy sprawdzić `argmax(p) == x_t`. Jeśli warunek jest spełniony, token zostaje zaakceptowany; w przeciwnym razie wypisywane jest `argmax(p)` i algorytm się zatrzymuje.

### Oczekiwane przyspieszenie

Jeśli współczynnik akceptacji na poziomie tokenu dla modelu roboczego wynosi `α`, oczekiwana liczba tokenów wygenerowanych podczas jednego przejścia przez model docelowy wynosi:

```
E[tokens] = (1 - α^{K+1}) / (1 - α)        # K = draft length, α in [0, 1]
```

Dla `α = 0.8, K = 4`: `(1 - 0.8^5)/(1 - 0.8) = 3.36` tokenów na przejście. Koszt jednego cyklu wynosi w przybliżeniu `cost_q * K + cost_p` (K kroków roboczych plus jedna weryfikacja celu). Gdy `cost_p >> cost_q * K`, współczynnik przyspieszenia przepustowości wynosi `3.36×`.

Jedynym istotnym parametrem jest `α`, który zależy wyłącznie od zgodności modelu roboczego z docelowym. Dobra jakość modelu roboczego decyduje o wszystkim.

### Trenowanie modelu roboczego: destylacja

Losowo zainicjowany mały model osiąga niski współczynnik akceptacji. Standardowe podejście polega na destylacji z modelu docelowego:

1. Wybierz małą architekturę (~1B dla celu 70B, ~500M dla celu 7B).
2. Uruchom model docelowy na dużym korpusie tekstowym i zapisz rozkłady prawdopodobieństwa dla kolejnych tokenów.
3. Trenuj model roboczy, minimalizując rozbieżność KL względem rozkładu docelowego (nie względem tokenów referencyjnych).

Wynik: `α` typowo 0,6–0,8 przy generowaniu kodu, 0,7–0,85 przy czacie w języku naturalnym. Przyspieszenie produkcyjne: 2–3×.

### EAGLE: generowanie drzewa kandydatów i ponowne wykorzystanie reprezentacji

Li, Wei, Zhang, Zhang (2024, „EAGLE: Speculative Sampling Requires Rethinking Feature Uncertainty") zidentyfikowali dwie nieefektywności standardowego dekodowania spekulatywnego:

1. Generowanie robocze składa się z K kroków seryjnych, każdy z pełnym stosem. Model roboczy mógłby jednak ponownie wykorzystywać reprezentacje (ukryte stany) obliczone przez model docelowy podczas ostatniej weryfikacji — docelowy wyznaczył już bogate reprezentacje, które model roboczy odtwarza od zera.
2. Model roboczy generuje liniowy łańcuch tokenów. Gdyby zamiast tego generował *drzewo* kandydatów (każdy węzeł z wieloma możliwymi kontynuacjami), pojedyncze przejście modelu docelowego mogłoby zweryfikować wiele ścieżek równolegle za pomocą maski uwagi o strukturze drzewa, akceptując najdłuższą poprawną gałąź.

Zmiany wprowadzone w EAGLE-1:
- Dane wejściowe modelu roboczego = ostatni ukryty stan modelu docelowego na pozycji t, a nie surowe tokeny.
- Architektura robocza = 1 warstwa dekodera transformatora (nie oddzielny mały model).
- Wyjście = drzewo K = 4–8 kandydatów na głębokość, głębokość 4–6.

EAGLE-2 (2024) wprowadza dynamiczną topologię drzewa: drzewo rozszerza się tam, gdzie przewidywanie jest niepewne, i pozostaje wąskie tam, gdzie jest pewne. Podnosi to efektywny `α` bez zwiększania kosztu weryfikacji.

EAGLE-3 (Li et al. 2025, „EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test") usuwa stałą zależność od reprezentacji ostatniej warstwy i uczy model roboczy przy użyciu nowej straty „symulacji czasu testowania" — model roboczy jest trenowany na wynikach odpowiadających docelowemu rozkładowi w czasie testowania, a nie rozkładowi wymuszanemu przez nauczyciela. Współczynnik akceptacji wzrasta z 0,75 (EAGLE-2) do 0,82 (EAGLE-3), a średnia liczba tokenów na weryfikację — z 3,0 do 4,5.

### Weryfikacja z maską uwagi drzewa

Gdy model roboczy generuje drzewo, model docelowy weryfikuje je w jednym przejściu do przodu, używając **maski uwagi drzewa** — maski przyczynowej kodującej topologię drzewa zamiast prostej sekwencji liniowej. Każdy token uwzględnia wyłącznie swoich przodków w drzewie. Weryfikacja to nadal jedno przejście do przodu z jednym mnożeniem macierzy; maska topologiczna kosztuje zaledwie kilka dodatkowych wpisów KV.

```
        root
       /    \
      a      b
     / \    / \
    c  d   e   f
```

Jeśli `a, b` rywalizują jako kandydaci na pierwszy token, a `c, d, e, f` to kandydaci na drugi token, wszystkie sześć pozycji jest weryfikowanych w jednym przejściu. Wynikiem jest najdłuższy prefiks na dowolnej zaakceptowanej ścieżce.

### Kiedy metoda działa, a kiedy nie

**Działa dobrze:**
- Czat i uzupełnianie przewidywalnego tekstu (kod, typowy angielski, ustrukturyzowane wyniki). `α` jest wysoki.
- Scenariusze z niedociążonym GPU podczas dekodowania (faza ograniczona przepustowością pamięci). Generowanie drzewa wykorzystuje dostępne FLOPy.

**Nie przynosi zysku:**
- Wysoce stochastyczne wyniki (kreatywne pisanie przy wysokiej temperaturze). `α` spada w kierunku `1/|vocab|`.
- Serwowanie wsadowe przy bardzo dużej współbieżności — batchowanie wypełnia już dostępne FLOPy, nie ma miejsca na weryfikację drzewa.
- Bardzo małe modele docelowe, gdzie koszt weryfikacji nie dominuje nad kosztem generowania roboczego.

Wdrożenia produkcyjne typowo raportują 2–3-krotne przyspieszenie przy czacie, 3–5-krotne przy generowaniu kodu i niemal zerowe przy pisaniu kreatywnym.

## Zbuduj to

`code/main.py`:

- Implementacja referencyjna `speculative_decode(target, draft, prompt, K, temperature)` stosująca dokładną regułę odrzucenia i weryfikująca zachowanie rozkładu modelu docelowego (empiryczny KL < 0,01 w porównaniu ze zwykłym próbkowaniem docelowym).
- Generator drzewa w stylu EAGLE budujący drzewo głębokości K z rozgałęzieniami na każdym poziomie.
- Konstruktor maski uwagi drzewa tworzący właściwy wzorzec przyczynowy dla weryfikatora.
- Moduł pomiaru współczynnika akceptacji działający na małym modelu językowym (destylacja małego GPT-2 z większego GPT-2 jako celu).

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

- **vLLM** i **SGLang** oferują zaawansowane dekodowanie spekulatywne. Flagi: `--speculative_model`, `--num_speculative_tokens`. Obsługa EAGLE-2/3 przez flagę `--spec_decoding_algorithm eagle`.
- **NVIDIA TensorRT-LLM** natywnie obsługuje drzewa Medusa i EAGLE.
- **Modele referencyjne**: `Qwen/Qwen3-0.6B-spec` (model roboczy dla Qwen3-32B), `meta-llama/Llama-3.2-1B-Instruct-spec` (model roboczy dla 70B).
- **Głowice Medusa** (Cai et al. 2024, „Medusa: Simple LLM Inference Acceleration Framework with Multiple Decoding Heads"): zamiast osobnego modelu roboczego do modelu docelowego dodawanych jest K równoległych głowic predykcyjnych. Prostsze wdrożenie, nieco niższy współczynnik akceptacji niż w EAGLE.

## Wyślij to

Ta lekcja prowadzi do uzyskania `outputs/skill-speculative-tuning.md` — umiejętności profilowania obciążenia modelu docelowego i doboru: modelu roboczego, K (długości generowania roboczego), szerokości drzewa, temperatury oraz warunków powrotu do standardowego dekodowania.

## Ćwiczenia

1. Zastosuj dokładną regułę odrzucenia i zweryfikuj ją empirycznie. Wygeneruj 10 tys. próbek za pomocą `speculative_decode` oraz zwykłego próbkowania z modelu docelowego, a następnie oblicz odległość TV między dwoma rozkładami wyjściowymi. Wynik powinien być < 0,01.

2. Wyprowadź wzór na przyspieszenie. Dla ustalonych wartości `α` i `K` wykreśl oczekiwaną liczbę tokenów generowanych przez model docelowy. Wyznacz optymalne K dla α ∈ {0,5, 0,7, 0,9}.

3. Wytrenuj mały model roboczy. Przyjmij cel 124M GPT-2 i destyluj z niego model roboczy 30M GPT-2 na 100M tokenów ze stratą KL. Zmierz `α` na zbiorze testowym. Oczekiwany wynik: 0,6–0,7.

4. Zaimplementuj generowanie drzewa w stylu EAGLE. Zamiast łańcucha liniowego rozgałęziaj wyjście na 3 kandydatów na każdym poziomie głębokości. Zbuduj maskę uwagi drzewa i sprawdź, czy model docelowy akceptuje najdłuższą poprawną gałąź.

5. Zbadaj scenariusze awarii. Uruchom dekodowanie spekulatywne przy temperaturze = 1,5 (wysoka stochastyczność). Pokaż, że `α` gwałtownie spada, a algorytm jest wolniejszy od zwykłego dekodowania ze względu na narzut związany z modelem roboczym.

## Kluczowe terminy

| Termin | Co się mówi | Co to faktycznie oznacza |
|------|-----------------|--------------------------------------|
| Model docelowy | „Wielki model" | Wolny, wysokiej jakości model, z którego pobieramy próbki (rozkład p) |
| Model roboczy | „Spekulant" | Mały, szybki predyktor (rozkład q); 5–30× mniejszy |
| K / długość robocza | „Patrzenie w przyszłość" | Liczba spekulowanych tokenów na jedno przejście weryfikacyjne |
| α / współczynnik akceptacji | „Wskaźnik trafień" | Prawdopodobieństwo na token, że propozycja modelu roboczego zostanie zaakceptowana |
| Dokładna reguła odrzucenia | „Test akceptacji" | Porównanie r < p/q zachowujące rozkład modelu docelowego |
| Rozkład resztowy | „Poprawione p-q" | (p - q)+ / ||(p - q)+||_1, rozkład do próbkowania w przypadku odrzucenia |
| Generowanie drzewa | „Rozgałęzianie spekulatywne" | Model roboczy generuje drzewo kandydatów weryfikowane w jednym przejściu za pomocą maski uwagi drzewa |
| Maska uwagi drzewa | „Maska topologiczna" | Maska przyczynowa kodująca topologię drzewa — każdy węzeł uwzględnia wyłącznie swoich przodków |
| Głowice Medusa | „Równoległe głowice" | K dodatkowych głowic predykcyjnych dołączonych bezpośrednio do modelu docelowego; brak osobnego modelu roboczego |
| Ponowne wykorzystanie reprezentacji EAGLE | „Szkicowanie w przestrzeni ukrytej" | Dane wejściowe modelu roboczego to ostatni ukryty stan modelu docelowego, a nie surowe tokeny — redukuje narzut modelu roboczego |
| Strata symulacji czasu testowania | „Trening EAGLE-3" | Trenowanie modelu roboczego na wynikach odpowiadających docelowemu rozkładowi czasu testowania, a nie wymuszaniu nauczyciela |

## Dalsze czytanie

- [Leviathan, Kalai, Matias, 2023 — „Fast Inference from Transformers via Speculative Decoding"](https://arxiv.org/abs/2211.17192) — dokładna reguła odrzucenia i teoretyczna analiza przyspieszenia
- [Chen, Borgeaud, Irving et al., 2023 — „Accelerating Large Language Model Decoding with Speculative Sampling"](https://arxiv.org/abs/2302.01318) — równoległa praca nad próbkowaniem spekulatywnym z DeepMind
- [Cai, Li, Geng, Wang, Wang, Zhu, Dao, 2024 — „Medusa: Simple LLM Inference Acceleration Framework with Multiple Decoding Heads"](https://arxiv.org/abs/2401.10774) — alternatywa dla modelu roboczego z równoległymi głowicami
- [Li, Wei, Zhang, Zhang, 2024 — „EAGLE: Speculative Sampling Requires Rethinking Feature Uncertainty"](https://arxiv.org/abs/2401.15077) — ponowne wykorzystanie reprezentacji i generowanie drzewa
- [Li et al., 2024 — „EAGLE-2: Faster Inference of Language Models with Dynamic Draft Trees"](https://arxiv.org/abs/2406.16858) — dynamiczna topologia drzewa
- [Li et al., 2025 — „EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test"](https://arxiv.org/abs/2503.01840) — dopasowanie rozkładu czasu testowania do czasu trenowania
- [Fu, Haotian, Peng et al., 2024 — „Break the Sequential Dependency of LLM Inference Using Lookahead Decoding"](https://arxiv.org/abs/2402.02057) — dekodowanie Jacobiego/lookahead jako alternatywa niewymagająca modelu spekulatywnego
