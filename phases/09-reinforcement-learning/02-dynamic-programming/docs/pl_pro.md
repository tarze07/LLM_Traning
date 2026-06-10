# Programowanie dynamiczne — iteracja polityki i iteracja wartości

> Programowanie dynamiczne to RL z ułatwieniem. Znasz już funkcje przejścia i nagrody; wystarczy iterować równanie Bellmana, aż `V` lub `π` przestanie się zmieniać. To punkt odniesienia, do którego dążą wszystkie metody oparte na próbkowaniu.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 9 · 01 (MDP)
**Czas:** ~75 minut

## Problem

Masz MDP ze znanym modelem: możesz odpytywać `P(s' | s, a)` i `R(s, a, s')` dla dowolnej pary stan-akcja. Menedżer zapasów zna rozkład popytu. Gra planszowa ma deterministyczne przejścia. GridWorld to kilka linii Pythona. Dysponujesz *modelem*.

Metody RL bez modelu (Q-learning, PPO, REINFORCE) powstały na wypadek, gdy model jest niedostępny — wtedy można jedynie próbkować środowisko. Jeśli jednak model jest znany, istnieją szybsze i skuteczniejsze podejścia: programowanie dynamiczne. Bellman opracował je w 1957 roku. Do dziś wyznaczają standard poprawności: gdy mówi się o „optymalnej polityce dla danego MDP", ma się na myśli politykę zwracaną przez DP.

W 2026 roku potrzebujesz tej wiedzy z trzech powodów. Po pierwsze, każde tabelaryczne środowisko w badaniach RL (GridWorld, FrozenLake, CliffWalking) rozwiązuje się metodami DP w celu wyznaczenia polityki złotego standardu. Po drugie, dokładne wartości pozwalają *debugować* metody próbkowania: jeśli estymata Q-learningu dla `V*(s_0)` różni się od rozwiązania DP o 30%, oznacza to błąd w Q-learningu. Po trzecie, nowoczesne metody RL offline i planowania (MCTS, wyszukiwanie AlphaZero, RL oparte na modelu w fazie 9 · 10) wykonują kopie zapasowe Bellmana na podstawie wyuczonego lub danego modelu.

## Koncepcja

![Iteracja polityki i iteracja wartości, porównanie](../assets/dp.svg)

**Dwa algorytmy, oba oparte na iteracji punktu stałego równania Bellmana.**

**Iteracja polityki.** Dwa kroki wykonywane naprzemiennie, aż polityka przestanie się zmieniać.

1. *Ocena:* dla danej polityki `π` wyznacz `V^π`, wielokrotnie stosując `V(s) ← Σ_a π(a|s) Σ_{s',r} P(s',r|s,a) [r + γ V(s')]`, aż do zbieżności.
2. *Ulepszenie:* dla danego `V^π` wyznacz politykę zachłanną względem `V^π`: `π(s) ← argmax_a Σ_{s',r} P(s',r|s,a) [r + γ V(s')]`.

Zbieżność jest gwarantowana, ponieważ (a) każdy krok ulepszenia albo zachowuje `π` bez zmian, albo istotnie zwiększa `V^π` dla pewnego stanu, (b) przestrzeń deterministycznych polityk jest skończona. Zazwyczaj zbieżność następuje po 5–20 iteracjach zewnętrznych, nawet dla dużych przestrzeni stanów.

**Iteracja wartości.** Łączy ocenę i ulepszenie w jednym kroku. Stosuje się równanie *optymalności* Bellmana:

`V(s) ← max_a Σ_{s',r} P(s',r|s,a) [r + γ V(s')]`

Powtarzaj aż `max_s |V_{new}(s) - V(s)| < ε`. Na końcu wyznacz politykę, wybierając zachłanną akcję. Każda iteracja jest szybsza niż w iteracji polityki — nie ma wewnętrznej pętli oceny — lecz do zbieżności potrzeba zwykle więcej iteracji.

**Uogólniona iteracja polityki (GPI).** Jednolita rama pojęciowa. Funkcja wartości i polityka tworzą dwukierunkową pętlę doskonalenia; każda metoda prowadząca obie strony do wzajemnej spójności (asynchroniczna iteracja wartości, zmodyfikowana iteracja polityki, Q-learning, aktor-krytyk, PPO) jest instancją GPI.

**Dlaczego `γ < 1` ma znaczenie.** Operator Bellmana jest odwzorowaniem zwężającym z współczynnikiem `γ` w normie sup: `||T V - T V'||_∞ ≤ γ ||V - V'||_∞`. Zwężenie gwarantuje istnienie jedynego punktu stałego i geometryczną zbieżność. Bez warunku `γ < 1` gwarancja odpada — potrzebny jest wtedy skończony horyzont lub absorbujący stan końcowy.

## Implementacja

### Krok 1: zbuduj model MDP dla GridWorld

Użyj tego samego GridWorld 4×4 z lekcji 01. Dodajemy wariant stochastyczny: z prawdopodobieństwem `0.1` agent przesuwa się w losowym kierunku prostopadłym do zamierzonego.

```python
SLIP = 0.1

def transitions(state, action):
    if state == TERMINAL:
        return [(state, 0.0, 1.0)]
    outcomes = []
    for direction, prob in action_probs(action):
        outcomes.append((apply_move(state, direction), -1.0, prob))
    return outcomes
```

`transitions(s, a)` zwraca listę `(s', r, p)`. To jest cały model.

### Krok 2: ocena polityki

Dla danej polityki `π(s) = {action: prob}` iteruj równanie Bellmana, aż `V` przestanie się zmieniać:

```python
def policy_evaluation(policy, gamma=0.99, tol=1e-6):
    V = {s: 0.0 for s in states()}
    while True:
        delta = 0.0
        for s in states():
            v = sum(pi_a * sum(p * (r + gamma * V[s_prime])
                              for s_prime, r, p in transitions(s, a))
                   for a, pi_a in policy(s).items())
            delta = max(delta, abs(v - V[s]))
            V[s] = v
        if delta < tol:
            return V
```

### Krok 3: ulepszenie polityki

Zastąp `π` polityką zachłanną względem `V`. Jeśli `π` nie uległo zmianie, zatrzymaj się — osiągnięto optymalność.

```python
def policy_improvement(V, gamma=0.99):
    new_policy = {}
    for s in states():
        best_a = max(
            ACTIONS,
            key=lambda a: sum(p * (r + gamma * V[s_prime])
                              for s_prime, r, p in transitions(s, a)),
        )
        new_policy[s] = best_a
    return new_policy
```

### Krok 4: złóż całość

```python
def policy_iteration(gamma=0.99):
    policy = {s: "up" for s in states()}   # arbitrary start
    for _ in range(100):
        V = policy_evaluation(lambda s: {policy[s]: 1.0}, gamma)
        new_policy = policy_improvement(V, gamma)
        if new_policy == policy:
            return V, policy
        policy = new_policy
```

Typowa zbieżność dla GridWorld 4×4 następuje po 4–6 iteracjach zewnętrznych. Wynik to `V*(0,0) ≈ -6` i polityka konsekwentnie minimalizująca liczbę kroków.

### Krok 5: iteracja wartości (wersja z jedną pętlą)

```python
def value_iteration(gamma=0.99, tol=1e-6):
    V = {s: 0.0 for s in states()}
    while True:
        delta = 0.0
        for s in states():
            v = max(sum(p * (r + gamma * V[s_prime])
                       for s_prime, r, p in transitions(s, a))
                   for a in ACTIONS)
            delta = max(delta, abs(v - V[s]))
            V[s] = v
        if delta < tol:
            break
    policy = policy_improvement(V, gamma)
    return V, policy
```

Ten sam punkt stały, mniej kodu.

## Pułapki

- **Brak obsługi stanów terminalnych.** Jeśli zastosujesz Bellmana do stanu absorbującego, algorytm nadal będzie wybierał „najlepszą akcję", która nic nie zmienia. Zabezpiecz się warunkiem `if s == terminal: V[s] = 0`.
- **Norma sup a zbieżność L2.** Używaj `max |V_new - V|`, nie wartości średniej. Gwarancja teoretyczna opiera się na normie supremum.
- **Aktualizacje lokalne a synchroniczne.** Aktualizowanie `V[s]` w miejscu (styl Gaussa-Seidela) jest szybsze niż utrzymywanie osobnej tablicy `V_new` (styl Jacobiego). Kod produkcyjny korzysta z aktualizacji lokalnych.
- **Remisy w polityce.** Gdy dwie akcje mają równą wartość Q, `argmax` może w kolejnych iteracjach rozstrzygać remisy różnie, powodując oscylacje w teście stabilności polityki. Stosuj deterministyczną regułę łamania remisów (np. pierwsza akcja w ustalonej kolejności).
- **Eksplozja przestrzeni stanów.** DP ma złożoność `O(|S| · |A|)` na cykl. Metoda jest praktyczna do ok. 10⁷ stanów. Przy większych przestrzeniach konieczna jest aproksymacja funkcji wartości (faza 9 · 05 i dalej).

## Zastosowania

W 2026 roku DP pełni rolę wzorca poprawności i wewnętrznej pętli planistów:

| Przypadek użycia | Metoda |
|---------|--------|
| Dokładne rozwiązanie małego tabelarycznego MDP | Iteracja wartości (prostsza) lub iteracja polityki (mniej iteracji zewnętrznych) |
| Weryfikacja implementacji Q-learning / PPO | Porównanie z optymalnym `V*` wyznaczonym przez DP w środowisku testowym |
| RL oparty na modelu (faza 9 · 10) | Kopia zapasowa Bellmana na podstawie wyuczonego modelu przejść |
| Planowanie w AlphaZero / MuZero | Przeszukiwanie drzewa Monte Carlo = asynchroniczna kopia zapasowa Bellmana |
| Offline RL (CQL, IQL) | Konserwatywna iteracja Q — DP z karą za akcje spoza rozkładu (OOD) |

Kiedy ktoś mówi „optymalna funkcja wartości", ma na myśli punkt stały DP. Gdy w artykule naukowym widzisz `V*` lub `Q*`, wyobraź sobie tę właśnie pętlę.

## Wyślij to

Zapisz jako `outputs/skill-dp-solver.md`:

```markdown
---
name: dp-solver
description: Solve a small tabular MDP exactly via policy iteration or value iteration. Report convergence behavior.
version: 1.0.0
phase: 9
lesson: 2
tags: [rl, dynamic-programming, bellman]
---

Given an MDP with a known model, output:

1. Choice. Policy iteration vs value iteration. Reason tied to |S|, |A|, γ.
2. Initialization. V_0, starting policy. Convergence sensitivity.
3. Stopping. Sup-norm tolerance ε. Expected number of sweeps.
4. Verification. V*(s_0) computed exactly. Greedy policy extracted.
5. Use. How this baseline will be used to debug/evaluate sampling-based methods.

Refuse to run DP on state spaces > 10⁷. Refuse to claim convergence without a sup-norm check. Flag any γ ≥ 1 on an infinite-horizon task as a guarantee violation.
```

## Ćwiczenia

1. **Łatwe.** Uruchom iterację wartości w GridWorld 4×4 dla `γ ∈ {0.9, 0.99}`. Ile cykli potrzeba, by osiągnąć `max |ΔV| < 1e-6`? Wydrukuj `V*` jako siatkę 4×4.
2. **Średnie.** Porównaj iterację polityki z iteracją wartości w *stochastycznym* GridWorld (prawdopodobieństwo poślizgu `0.1`). Zmierz: liczbę przebiegów, czas rzeczywisty, końcowe `V*(0,0)`. Co zbiega się szybciej pod względem liczby iteracji? Pod względem czasu?
3. **Trudne.** Zaimplementuj zmodyfikowaną iterację polityki: na etapie oceny wykonaj tylko `k` przeglądów zamiast czekać na zbieżność. Wykreśl błąd `V*(0,0)` w zależności od `k` dla `k ∈ {1, 2, 5, 10, 50}`. Co krzywa mówi o kompromisie między oceną a ulepszeniem?

## Kluczowe terminy

| Termin | Co się mówi | Co to faktycznie oznacza |
|------|-----------------|----------------------|
| Iteracja polityki | „Algorytm DP" | Naprzemienne wyznaczanie `V^π` i ulepszanie polityki (zachłannie względem `V^π`), aż polityka przestanie się zmieniać. |
| Iteracja wartości | „Szybszy DP" | Kopia zapasowa optymalności Bellmana stosowana w jednym kroku; zbieżność geometryczna do `V*`. |
| Operator Bellmana | „Rekursja" | `(T V)(s) = max_a Σ P (r + γ V(s'))`; odwzorowanie zwężające z współczynnikiem `γ` w normie sup. |
| Zwężenie | „Dlaczego DP zbiega" | Każdy operator `T` spełniający `\|\|T x - T y\|\| ≤ γ \|\|x - y\|\|` ma jedyny punkt stały. |
| GPI | „Wszystko jest DP" | Uogólniona iteracja polityki: każda metoda zapewniająca wzajemną spójność `V` i `π`. |
| Aktualizacja synchroniczna | „Styl Jacobiego" | Korzystaj ze starego `V` podczas całego przeglądania; łatwiejsza do analizy, ale wolniejsza. |
| Aktualizacja w miejscu | „Styl Gaussa-Seidela" | Korzystaj z bieżącego `V` podczas aktualizacji; w praktyce szybciej osiąga zbieżność. |

## Dalsze czytanie

- [Sutton i Barto (2018). Ch. 4 — Programowanie dynamiczne](http://incompleteideas.net/book/RLbook2020.pdf) — kanoniczna prezentacja iteracji polityki i iteracji wartości.
- [Bertsekas (2019). Uczenie się przez wzmocnienie i optymalna kontrola](http://www.athenasc.com/rlbook.html) — rygorystyczne omówienie argumentów opartych na odwzorowaniach zwężających.
- [Puterman (2005). Procesy decyzyjne Markowa](https://onlinelibrary.wiley.com/doi/book/10.1002/9780470316887) — zmodyfikowana iteracja polityki i analiza jej zbieżności.
- [Howard (1960). Programowanie dynamiczne i procesy Markowa](https://mitpress.mit.edu/9780262582300/dynamic-programming-and-markov-processes/) — oryginalny artykuł poświęcony iteracji polityki.
- [Bertsekas i Tsitsiklis (1996). Programowanie neurodynamiczne](http://www.athenasc.com/ndpbook.html) — pomost między DP a przybliżonym DP i głębokim RL, omawiany na kolejnych lekcjach.
