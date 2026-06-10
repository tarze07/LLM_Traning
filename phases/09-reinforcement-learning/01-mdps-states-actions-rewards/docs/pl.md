# MDP, stany, działania i nagrody

> Proces decyzyjny Markowa składa się z pięciu elementów: stanów, działań, przejść, nagród i rabatu. Wszystko w RL — Q-learning, PPO, DPO, GRPO — optymalizuje się w tym kształcie. Naucz się tego raz, przeczytaj resztę nauki przez wzmacnianie za darmo.

**Typ:** Ucz się
**Języki:** Python
**Wymagania wstępne:** Faza 1 · 06 (Prawdopodobieństwo i rozkłady), Faza 2 · 01 (Taksonomia ML)
**Czas:** ~45 minut

## Problem

Piszesz bota szachowego. Albo planista zapasów. Albo agent handlowy. Lub pętla PPO, która trenuje model rozumowania. Cztery różne dziedziny, jeden zaskakujący fakt: wszystkie cztery sprowadzają się do tego samego obiektu matematycznego.

Uczenie nadzorowane daje `(x, y)` pary i prosi o dopasowanie funkcji. Uczenie się przez wzmacnianie nie daje żadnych etykiet – jedynie strumień stanów, podjęte działania i skalarną nagrodę. Czy ten ruch wygrał mecz? Czy decyzja o uzupełnieniu zapasów pozwoliła zaoszczędzić pieniądze? Czy handel przyniósł zysk? Czy token właśnie wyprodukowany przez LLM doprowadził do wyższej nagrody od sędziego?

Nie możesz uczyć się z tego strumienia, dopóki go nie sformalizujesz. „To, co widziałem”, „co zrobiłem”, „co stało się potem”, „jakie to było dobre” – każde z nich musi stać się przedmiotem, o którym będziesz mógł pomyśleć. Formalizacja ta jest procesem decyzyjnym Markowa. Każdy algorytm RL w tej fazie, łącznie z pętlami RLHF i GRPO na końcu, optymalizuje ten kształt.

## Koncepcja

![Proces decyzyjny Markowa: stany, działania, przejścia, nagrody, rabat](../assets/mdp.svg)

**Pięć obiektów.**

- **Stany** `S`. Wszystko, o czym musi zdecydować agent. W GridWorld komórka. W szachach szachownica. W LLM okno kontekstowe plus dowolna pamięć.
- **Działania** `A`. Wybory. Poruszaj się w górę/w dół/w lewo/w prawo. Zagraj ruch. Wyemituj token.
- **Przejścia** `P(s' | s, a)`. Biorąc pod uwagę stan `s` i akcję `a`, rozkład w następnym stanie. Deterministyczny w szachach, stochastyczny w inwentarzu, prawie deterministyczny w dekodowaniu LLM.
- **Nagrody** `R(s, a, s')`. Sygnał skalarny. Wygrana = +1, przegrana = -1. Przychód minus koszt. Termin współczynnika wiarygodności logarytmicznej w GRPO.
- **Rabat** `γ ∈ [0, 1)`. Ile liczy się przyszła nagroda w porównaniu z obecną. `γ = 0.99` kupuje horyzont ~100 kroków; `γ = 0.9` kupuje ~10.

**Właściwość Markowa** `P(s_{t+1} | s_t, a_t) = P(s_{t+1} | s_0, a_0, …, s_t, a_t)`. Przyszłość zależy tylko od stanu teraźniejszego. Jeżeli tak nie jest, reprezentacja stanu jest niekompletna — nie jest to błąd metody, lecz błąd stanu.

**Zasady i zwroty.** Zasada `π(a | s)` odwzorowuje stany na rozkłady działań. Zwrot `G_t = r_t + γ r_{t+1} + γ² r_{t+2} + …` to obniżona suma przyszłych nagród. Wartość `V^π(s) = E[G_t | s_t = s]` to oczekiwany zwrot począwszy od `s` zgodnie z polityką `π`. Wartość Q `Q^π(s, a) = E[G_t | s_t = s, a_t = a]` to oczekiwany zwrot rozpoczynający się od określonej akcji. Każdy algorytm RL szacuje jeden z tych dwóch, a następnie odpowiednio poprawia `π`.

**Równania Bellmana.** Równania punktu stałego używane we wszystkim w tej fazie:

`V^π(s) = Σ_a π(a|s) Σ_{s', r} P(s', r | s, a) [r + γ V^π(s')]`
`Q^π(s, a) = Σ_{s', r} P(s', r | s, a) [r + γ Σ_{a'} π(a'|s') Q^π(s', a')]`

Dzielą one oczekiwany zwrot na „nagrodę za ten krok” i „zniżkę na miejsce, w którym wylądujesz”. Rekurencyjne. Każdy algorytm w fazie 9 albo iteruje to równanie do zbieżności (programowanie dynamiczne), pobiera z niego próbki (Monte Carlo), albo ładuje je o jeden krok (różnica czasowa).

## Zbuduj to

### Krok 1: mały deterministyczny MDP

Świat siatki 4×4. Agent zaczyna w lewym górnym rogu, terminal w prawym dolnym rogu, nagroda -1 za krok, akcje `{up, down, left, right}`. Zobacz `code/main.py`.

```python
GRID = 4
TERMINAL = (3, 3)
ACTIONS = {"up": (-1, 0), "down": (1, 0), "left": (0, -1), "right": (0, 1)}

def step(state, action):
    if state == TERMINAL:
        return state, 0.0, True
    dr, dc = ACTIONS[action]
    r, c = state
    nr = min(max(r + dr, 0), GRID - 1)
    nc = min(max(c + dc, 0), GRID - 1)
    return (nr, nc), -1.0, (nr, nc) == TERMINAL
```

Pięć linii. To jest całe środowisko. Przejścia deterministyczne, stała kara za krok, absorbujący stan końcowy.

### Krok 2: wprowadź politykę

Polityka jest funkcją od stanu do rozkładu akcji. Najprostszy: jednolity losowy.

```python
def uniform_policy(state):
    return {a: 0.25 for a in ACTIONS}

def rollout(policy, max_steps=200):
    s, total, steps = (0, 0), 0.0, 0
    for _ in range(max_steps):
        a = sample(policy(s))
        s, r, done = step(s, a)
        total += r
        steps += 1
        if done:
            break
    return total, steps
```

Uruchom losową politykę 1000 razy. Średni zwrot dla tej planszy 4×4 wynosi około -60 do -80. Optymalny zwrot to -6 (ścieżka prosta w dół i w prawo). Zamknięcie tej luki jest najważniejszym zadaniem w fazie 9.

### Krok 3: oblicz `V^π` dokładnie za pomocą równania Bellmana

Dla małych MDP równanie Bellmana jest układem liniowym. Wyliczaj stany, stosuj oczekiwania i powtarzaj, aż wartości przestaną się zmieniać.

```python
def policy_evaluation(policy, gamma=0.99, tol=1e-6):
    V = {s: 0.0 for s in all_states()}
    while True:
        delta = 0.0
        for s in all_states():
            if s == TERMINAL:
                continue
            v = 0.0
            for a, pi_a in policy(s).items():
                s_next, r, _ = step(s, a)
                v += pi_a * (r + gamma * V[s_next])
            delta = max(delta, abs(v - V[s]))
            V[s] = v
        if delta < tol:
            return V
```

Jest to iteracyjna ocena polityki. Jest to pierwszy algorytm w Sutton & Barto i teoretyczna podstawa każdej kolejnej metody RL.

### Krok 4: `γ` to hiperparametr o znaczeniu fizycznym

Efektywny horyzont to mniej więcej `1 / (1 - γ)`. `γ = 0.9` → 10 kroków. `γ = 0.99` → 100 kroków. `γ = 0.999` → 1000 kroków.

Za niski i środek działa krótkowzrocznie. Zbyt wysoka i przypisywanie punktów staje się hałaśliwe, ponieważ wiele wczesnych kroków jest wspólnie odpowiedzialnych za nagrodę w dalekiej przyszłości. LLM RLHF zazwyczaj używa `γ = 1`, ponieważ odcinki są krótkie i ograniczone. Zadania kontrolne wykorzystują `0.95–0.99`. Długofalowe gry strategiczne wykorzystują `0.999`.

## Pułapki

- **Stan niemarkowski.** Jeśli do podjęcia decyzji potrzebne są trzy ostatnie obserwacje, „stan” to nie tylko bieżąca obserwacja. Poprawka: stosuj ramki (DQN na stosach Atari 4) lub użyj stanu rekurencyjnego (LSTM/GRU na obserwacjach).
- **Rzadkie nagrody.** Nagrody tylko za wygraną sprawiają, że nauka w dużych przestrzeniach stanów jest prawie niemożliwa. Kształtuj nagrody (sygnał pośredni) lub bootstrap z imitacją (faza 9 · 09).
- **Hakowanie nagród.** Optymalizacja nagrody zastępczej często prowadzi do patologicznych zachowań. Agent wyścigów łodzi OpenAI kręcił się w kółko, zbierając bonusy na zawsze, zamiast ukończyć wyścig. Zawsze definiuj nagrodę na podstawie docelowego wyniku, a nie zastępczego.
- **Błąd w specyfikacji rabatu.** `γ = 1` w przypadku zadania o nieskończonym horyzoncie powoduje, że każda wartość jest nieskończona. Zawsze ograniczaj albo skończonym horyzontem, albo `γ < 1`.
- **Skala nagród.** Nagrody w wysokości {+100, -100} w porównaniu z {+1, -1} zapewniają identyczne optymalne zasady, ale znacznie różnią się wielkością gradientu. Normalizuj do `[-1, 1]`-ish przed podłączeniem do PPO/DQN.

## Użyj tego

Stos 2026 redukuje każdy potok RL do MDP przed dotknięciem kodu:

| Sytuacja | stan | Akcja | Nagroda | γ |
|----------|-------|--------|--------|---|
| Kontrola (ruch, manipulacja) | Kąty połączeń + prędkości | Ciągłe momenty obrotowe | Kształt dostosowany do zadania | 0,99 |
| Gry (szachy, Go, poker) | Tablica + historia | Legalny ruch | Wygrana=+1 / przegrana=-1 | 1,0 (skończony) |
| Zapasy / ceny | Zapasy + popyt | Ilość zamówienia | Przychody - koszty | 0,95 |
| RLHF dla LLM | Tokeny kontekstowe | Następny token | Wynik modelu nagrody na końcu | 1.0 (odcinek ~200 tokenów) |
| GRPO za rozumowanie | Podpowiedź + częściowa odpowiedź | Następny token | Weryfikator 0/1 na końcu | 1,0 |

Zapisz pięć krotek przed napisaniem jakiejkolwiek pętli szkoleniowej. Większość raportów o błędach typu „RL nie działa” ma swoje korzenie w sformułowaniu MDP, które zostało złamane na papierze.

## Wyślij to

Zapisz jako `outputs/skill-mdp-modeler.md`:

```markdown
---
name: mdp-modeler
description: Given a task description, produce a Markov Decision Process spec and flag formulation risks before training.
version: 1.0.0
phase: 9
lesson: 1
tags: [rl, mdp, modeling]
---

Given a task (control / game / recommendation / LLM fine-tuning), output:

1. State. Exact feature vector or tensor spec. Justify Markov property.
2. Action. Discrete set or continuous range. Dimensionality.
3. Transition. Deterministic, stochastic-with-known-model, or sample-only.
4. Reward. Function and source. Sparse vs shaped. Terminal vs per-step.
5. Discount. Value and horizon justification.

Refuse to ship any MDP where the state is non-Markovian without explicit mention of frame-stacking or recurrent state. Refuse any reward that was not defined in terms of the target outcome. Flag any `γ ≥ 1.0` on an infinite-horizon task. Flag any reward range >100x the typical step reward as a likely gradient-explosion source.
```

## Ćwiczenia

1. **Łatwo.** Zaimplementuj 4×4 GridWorld i wdrożenie zasad losowych w `code/main.py`. Uruchom 10 000 odcinków. Podaj średnią i std zwrotu. Porównaj z optymalnym zwrotem (-6).
2. **Medium.** Uruchom `policy_evaluation` z `γ ∈ {0.5, 0.9, 0.99}`, aby uzyskać zasadę uniform-random. Wydrukuj dla każdego `V` jako siatkę 4×4. Wyjaśnij, dlaczego wartości stanu w pobliżu terminala rosną szybciej przy większym `γ`.
3. **Trudne.** Zmień stochastyczny GridWorld: każda akcja przesuwa się w sąsiednim kierunku z prawdopodobieństwem `p = 0.1`. Dokonaj ponownej oceny jednolitej polityki. Czy `V[start]` jest lepszy czy gorszy? Dlaczego?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| MDP | „Konfiguracja uczenia się przez wzmacnianie” | Krotka `(S, A, P, R, γ)` spełniająca własność Markowa. |
| stan | „Co widzi agent” | Wystarczające statystyki dla przyszłej dynamiki w ramach wybranej klasy polis. |
| Polityka | „Zachowanie agenta” | Rozkład warunkowy `π(a \| s)` lub mapa deterministyczna `s → a`. |
| Powrót | „Całkowita nagroda” | Suma rabatu `Σ γ^t r_t` z bieżącego kroku. |
| Wartość | „Jak dobre jest państwo” | Oczekiwany zwrot poniżej `π` począwszy od `s`. |
| Wartość Q | „Jak dobra jest akcja” | Oczekiwany zwrot w ramach `π` począwszy od `s` z pierwszą akcją `a`. |
| Równanie Bellmana | „Rekurencja programowania dynamicznego” | Stały rozkład wartości / Q na jednoetapową nagrodę plus zdyskontowaną wartość następczą. |
| Rabat `γ` | „Przyszłość kontra teraźniejszość” | Waga geometryczna nagrody z dalekiej przyszłości; efektywny horyzont `~1/(1-γ)`. |

## Dalsze czytanie

- [Sutton i Barto (2018). Uczenie się przez wzmacnianie: wprowadzenie, wyd. 2](http://incompleteideas.net/book/RLbook2020.pdf) — podręcznik. Ch. 3 obejmuje równania MDP i Bellmana; Ch. 1 motywuje hipotezę nagrody, która leży u podstaw każdej kolejnej lekcji.
- [Bellmana (1957). Programowanie dynamiczne](https://press.princeton.edu/books/paperback/9780691146683/dynamic-programming) — pochodzenie równania Bellmana.
- [Rozkręcanie OpenAI — część 1: Kluczowe pojęcia](https://spinningup.openai.com/en/latest/spinningup/rl_intro.html) — zwięzły elementarz MDP z perspektywy głębokiego RL.
- [Putermana (2005). Procesy decyzyjne Markowa](https://onlinelibrary.wiley.com/doi/book/10.1002/9780470316887) — dokumentacja badań operacyjnych na temat MDP i metod dokładnych rozwiązań.
- [Littman (1996). Algorytmy sekwencyjnego podejmowania decyzji (praca doktorska)](https://www.cs.rutgers.edu/~mlittman/papers/thesis-main.pdf) — najczystsze wyprowadzenie MDP jako specjalizacji z programowania dynamicznego.