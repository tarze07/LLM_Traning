# MDP, stany, działania i nagrody

> Proces decyzyjny Markowa składa się z pięciu elementów: stanów, działań, przejść, nagród i współczynnika dyskontowania. Wszystko w RL — Q-learning, PPO, DPO, GRPO — optymalizuje się w tej postaci. Opanuj to raz, a reszta materiału o uczeniu przez wzmacnianie stanie się znacznie przystępniejsza.

**Typ:** Ucz się
**Języki:** Python
**Wymagania wstępne:** Faza 1 · 06 (Prawdopodobieństwo i rozkłady), Faza 2 · 01 (Taksonomia ML)
**Czas:** ~45 minut

## Problem

Piszesz bota szachowego. Albo planistę zapasów. Albo agenta handlowego. Lub pętlę PPO trenującą model rozumowania. Cztery zupełnie różne dziedziny, jeden zaskakujący fakt: wszystkie cztery sprowadzają się do tego samego obiektu matematycznego.

Uczenie nadzorowane dostarcza par `(x, y)` i wymaga dopasowania funkcji. Uczenie przez wzmacnianie nie daje żadnych etykiet — jedynie strumień stanów, podjętych działań i skalarnych nagród. Czy ten ruch wygrał partię? Czy decyzja o uzupełnieniu zapasów pozwoliła zaoszczędzić pieniądze? Czy transakcja przyniosła zysk? Czy token właśnie wyprodukowany przez LLM doprowadził do wyższej oceny od sędziego?

Z takiego strumienia nie można się uczyć bez jego uprzedniej formalizacji. „To, co widziałem", „co zrobiłem", „co nastąpiło potem", „na ile to było korzystne" — każdy z tych elementów musi stać się precyzyjnie zdefiniowanym obiektem. Tą formalizacją jest właśnie proces decyzyjny Markowa. Każdy algorytm RL omawiany w tej fazie — w tym pętle RLHF i GRPO na jej końcu — optymalizuje tę właśnie strukturę.

## Koncepcja

![Proces decyzyjny Markowa: stany, działania, przejścia, nagrody, dyskontowanie](../assets/mdp.svg)

**Pięć obiektów.**

- **Stany** `S`. Wszystko, co agent musi uwzględnić przy podejmowaniu decyzji. W GridWorld — komórka siatki. W szachach — układ bierek na szachownicy. W LLM — okno kontekstowe wraz z ewentualną pamięcią zewnętrzną.
- **Działania** `A`. Dostępne wybory. Ruch w górę/dół/lewo/prawo. Zagranie figury. Emisja tokenu.
- **Przejścia** `P(s' | s, a)`. Rozkład następnego stanu przy danym stanie `s` i akcji `a`. Deterministyczne w szachach, stochastyczne w zarządzaniu zapasami, niemal deterministyczne w dekodowaniu LLM.
- **Nagrody** `R(s, a, s')`. Skalarny sygnał oceny. Wygrana = +1, przegrana = -1. Przychód minus koszt. Składnik logarytmicznego ilorazu wiarygodności w GRPO.
- **Współczynnik dyskontowania** `γ ∈ [0, 1)`. Określa, ile warta jest przyszła nagroda w porównaniu z bieżącą. `γ = 0.99` daje efektywny horyzont ~100 kroków; `γ = 0.9` skraca go do ~10.

**Własność Markowa** `P(s_{t+1} | s_t, a_t) = P(s_{t+1} | s_0, a_0, …, s_t, a_t)`. Przyszłość zależy wyłącznie od aktualnego stanu. Jeżeli tak nie jest, reprezentacja stanu jest niekompletna — to nie wada metody, lecz błąd w definicji stanu.

**Polityki i zwroty.** Polityka `π(a | s)` odwzorowuje stany na rozkłady działań. Zwrot `G_t = r_t + γ r_{t+1} + γ² r_{t+2} + …` to zdyskontowana suma przyszłych nagród. Funkcja wartości `V^π(s) = E[G_t | s_t = s]` wyraża oczekiwany zwrot osiągany ze stanu `s` przy polityce `π`. Funkcja wartości Q `Q^π(s, a) = E[G_t | s_t = s, a_t = a]` wyraża oczekiwany zwrot przy polityce `π`, gdy w stanie `s` wykonujemy konkretną akcję `a`. Każdy algorytm RL szacuje jedną z tych dwóch funkcji, a następnie na tej podstawie poprawia `π`.

**Równania Bellmana.** Równania punktu stałego używane powszechnie w tej fazie:

`V^π(s) = Σ_a π(a|s) Σ_{s', r} P(s', r | s, a) [r + γ V^π(s')]`
`Q^π(s, a) = Σ_{s', r} P(s', r | s, a) [r + γ Σ_{a'} π(a'|s') Q^π(s', a')]`

Równania te rozkładają oczekiwany zwrot na dwa składniki: nagrodę za bieżący krok i zdyskontowaną wartość stanu, w którym agent się znajdzie. Mają charakter rekurencyjny. Każdy algorytm z fazy 9 albo iteruje te równania do zbieżności (programowanie dynamiczne), albo próbkuje je (Monte Carlo), albo bootstrapuje jeden krok w przód (różnica czasowa).

## Zbuduj to

### Krok 1: mały deterministyczny MDP

Siatka 4×4. Agent startuje w lewym górnym rogu, stan końcowy znajduje się w prawym dolnym rogu, każdy krok kosztuje -1, dostępne akcje to `{up, down, left, right}`. Pełna implementacja w `code/main.py`.

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

Pięć linii — to całe środowisko. Przejścia deterministyczne, stała kara za krok, pochłaniający stan końcowy.

### Krok 2: wprowadź politykę

Polityka to funkcja odwzorowująca stan na rozkład akcji. Najprostsza z możliwych to polityka jednostajnie losowa.

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

Uruchom losową politykę 1000 razy. Średni zwrot na tej planszy 4×4 wynosi około -60 do -80. Optymalny zwrot to -6 (najkrótsza ścieżka w dół i w prawo). Wypełnienie tej luki jest głównym celem fazy 9.

### Krok 3: oblicz `V^π` dokładnie za pomocą równania Bellmana

Dla małych MDP równanie Bellmana tworzy układ liniowy. Wystarczy iterować po stanach, obliczać wartości oczekiwane i powtarzać, aż wartości przestaną się zmieniać.

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

To iteracyjna ocena polityki — pierwszy algorytm opisany w Sutton & Barto i teoretyczna podstawa wszystkich kolejnych metod RL.

### Krok 4: `γ` to hiperparametr o konkretnym znaczeniu

Efektywny horyzont wynosi w przybliżeniu `1 / (1 - γ)`. `γ = 0.9` → 10 kroków. `γ = 0.99` → 100 kroków. `γ = 0.999` → 1000 kroków.

Zbyt niska wartość powoduje, że agent działa krótkowzrocznie. Zbyt wysoka sprawia, że przypisywanie punktów staje się niestabilne — wiele wczesnych kroków współodpowiada za nagrodę odległą w czasie. W RLHF dla LLM stosuje się zazwyczaj `γ = 1`, ponieważ epizody są krótkie i skończone. W zadaniach kontrolnych używa się wartości `0.95–0.99`. W długoterminowych grach strategicznych — `0.999`.

## Pułapki

- **Stan niemarkowski.** Jeśli do podjęcia decyzji potrzebne są trzy ostatnie obserwacje, „stanem" nie jest sama bieżąca obserwacja. Rozwiązanie: stosuj łączenie ramek (DQN na stosach 4 klatek Atari) lub stan rekurencyjny (LSTM/GRU przetwarzające kolejne obserwacje).
- **Rzadkie nagrody.** Gdy sygnał pojawia się tylko przy wygranej, uczenie w dużych przestrzeniach stanów jest praktycznie niemożliwe. Stosuj kształtowanie nagród (sygnały pośrednie) lub inicjalizację przez imitację (faza 9 · 09).
- **Hakowanie nagród.** Optymalizacja nagrody zastępczej często prowadzi do patologicznych zachowań. Agent wyścigów łodzi OpenAI kręcił się w kółko, zbierając premie w nieskończoność zamiast ukończyć wyścig. Zawsze definiuj nagrodę w oparciu o docelowy wynik, a nie jego substytut.
- **Błąd w doborze współczynnika dyskontowania.** `γ = 1` w zadaniu o nieskończonym horyzoncie sprawia, że każda wartość jest nieskończona. Zawsze ograniczaj problem skończonym horyzontem albo wartością `γ < 1`.
- **Skala nagród.** Nagrody z zakresu {+100, -100} i {+1, -1} dają identyczne optymalne polityki, ale znacznie różnią się amplitudą gradientów. Normalizuj do zakresu zbliżonego do `[-1, 1]` przed użyciem PPO lub DQN.

## Użyj tego

Przed napisaniem jakiegokolwiek kodu warto zredukować problem do MDP — to dobra praktyka obowiązująca w całym stosie 2026:

| Sytuacja | Stan | Akcja | Nagroda | γ |
|----------|-------|--------|--------|---|
| Kontrola (ruch, manipulacja) | Kąty stawów + prędkości | Ciągłe momenty obrotowe | Kształt dostosowany do zadania | 0,99 |
| Gry (szachy, Go, poker) | Tablica + historia | Legalny ruch | Wygrana=+1 / przegrana=-1 | 1,0 (skończony) |
| Zapasy / ceny | Zapasy + popyt | Ilość zamówienia | Przychody - koszty | 0,95 |
| RLHF dla LLM | Tokeny kontekstowe | Następny token | Wynik modelu nagrody na końcu | 1.0 (epizod ~200 tokenów) |
| GRPO dla rozumowania | Podpowiedź + częściowa odpowiedź | Następny token | Weryfikator 0/1 na końcu | 1,0 |

Zapisz pięć krotek przed napisaniem jakiejkolwiek pętli treningowej. Większość zgłoszeń „RL nie działa" ma swoje źródło w błędnie sformułowanym MDP, który był wadliwy już na etapie projektowania.

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

1. **Łatwe.** Zaimplementuj GridWorld 4×4 z losową polityką w `code/main.py`. Uruchom 10 000 epizodów. Podaj średnią i odchylenie standardowe zwrotu. Porównaj z optymalnym zwrotem (-6).
2. **Średnie.** Uruchom `policy_evaluation` dla `γ ∈ {0.5, 0.9, 0.99}` przy polityce jednostajnie losowej. Wydrukuj każdą funkcję `V` jako siatkę 4×4. Wyjaśnij, dlaczego wartości stanów w pobliżu stanu końcowego rosną szybciej przy wyższym `γ`.
3. **Trudne.** Wprowadź losowość do GridWorld: każda akcja z prawdopodobieństwem `p = 0.1` przesuwa agenta w sąsiednim kierunku. Ponownie oceń jednolitą politykę. Czy `V[start]` jest wyższe czy niższe? Dlaczego?

## Kluczowe terminy

| Termin | Potoczne rozumienie | Precyzyjna definicja |
|------|-----------------|----------------------|
| MDP | „Konfiguracja uczenia przez wzmacnianie" | Krotka `(S, A, P, R, γ)` spełniająca własność Markowa. |
| Stan | „To, co widzi agent" | Wystarczająca statystyka do opisu przyszłej dynamiki w ramach danej klasy polityk. |
| Polityka | „Zachowanie agenta" | Rozkład warunkowy `π(a \| s)` lub deterministyczne odwzorowanie `s → a`. |
| Zwrot | „Łączna nagroda" | Zdyskontowana suma `Σ γ^t r_t` od bieżącego kroku. |
| Wartość | „Jak dobry jest stan" | Oczekiwany zwrot przy polityce `π` startując ze stanu `s`. |
| Wartość Q | „Jak dobra jest akcja" | Oczekiwany zwrot przy polityce `π`, gdy w stanie `s` wykonujemy akcję `a` jako pierwszą. |
| Równanie Bellmana | „Rekurencja programowania dynamicznego" | Rozkład funkcji wartości lub Q na nagrodę jednokrokową i zdyskontowaną wartość następnika. |
| Dyskontowanie `γ` | „Przyszłość kontra teraźniejszość" | Geometryczna waga nagród odległych w czasie; efektywny horyzont `~1/(1-γ)`. |

## Dalsze czytanie

- [Sutton i Barto (2018). Uczenie się przez wzmacnianie: wprowadzenie, wyd. 2](http://incompleteideas.net/book/RLbook2020.pdf) — podręcznik podstawowy. Rozdział 3 obejmuje MDP i równania Bellmana; rozdział 1 uzasadnia hipotezę nagrody leżącą u podstaw wszystkich kolejnych lekcji.
- [Bellman (1957). Programowanie dynamiczne](https://press.princeton.edu/books/paperback/9780691146683/dynamic-programming) — źródło równania Bellmana.
- [Spinning Up OpenAI — część 1: Kluczowe pojęcia](https://spinningup.openai.com/en/latest/spinningup/rl_intro.html) — zwięzłe wprowadzenie do MDP z perspektywy głębokiego RL.
- [Puterman (2005). Procesy decyzyjne Markowa](https://onlinelibrary.wiley.com/doi/book/10.1002/9780470316887) — obszerne omówienie MDP i metod dokładnego rozwiązywania z perspektywy badań operacyjnych.
- [Littman (1996). Algorytmy sekwencyjnego podejmowania decyzji (praca doktorska)](https://www.cs.rutgers.edu/~mlittman/papers/thesis-main.pdf) — najbardziej przejrzyste wyprowadzenie MDP jako szczególnego przypadku programowania dynamicznego.
