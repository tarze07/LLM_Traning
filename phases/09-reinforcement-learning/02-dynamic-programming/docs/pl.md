# Programowanie dynamiczne — iteracja zasad i iteracja wartości

> Programowanie dynamiczne to RL z oszukiwaniem. Znasz już funkcje przejścia i nagrody; po prostu iterujesz równanie Bellmana, aż `V` lub `π` przestanie się poruszać. Jest to punkt odniesienia, do którego stara się podejść każda metoda oparta na próbkowaniu.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 9 · 01 (MDP)
**Czas:** ~75 minut

## Problem

Masz MDP ze znanym modelem: możesz wysyłać zapytania do `P(s' | s, a)` i `R(s, a, s')` o dowolną parę stan-akcja. Menedżer zapasów zna rozkład popytu. Gra planszowa ma deterministyczne przejścia. Gridworld to cztery linie Pythona. Masz *modelkę*.

Model RL bez modelu (Q-learning, PPO, REINFORCE) został wynaleziony na wypadek, gdy nie masz modelu — możesz jedynie próbkować ze środowiska. Ale jeśli już go masz, istnieją szybsze i lepsze metody: programowanie dynamiczne. Bellman zaprojektował je w 1957 roku. Nadal definiują poprawność: kiedy ludzie mówią „optymalna polityka dla tego MDP”, mają na myśli, że polityka DP powróci.

Potrzebujecie ich w 2026 roku z trzech powodów. Po pierwsze, każde środowisko tabelaryczne w badaniach RL (GridWorld, FrozenLake, CliffWalking) jest rozwiązywane za pomocą DP w celu stworzenia polityki złotego standardu. Po drugie, dokładne wartości pozwalają *debugować* metody próbkowania: jeśli oszacowanie Q-learningu dla `V*(s_0)` nie zgadza się z odpowiedzią DP o 30%, oznacza to, że Q-learning zawiera błąd. Po trzecie, nowoczesne metody RL offline i planowania (MCTS, wyszukiwanie AlphaZero, RL oparte na modelu w fazie 9 · 10) wykonują iterację kopii zapasowej Bellmana na podstawie wyuczonego lub danego modelu.

## Koncepcja

![Iteracja zasad i iteracja wartości, obok siebie](../assets/dp.svg)

**Dwa algorytmy, oba z iteracją stałoprzecinkową na Bellmanie.**

**Iteracja zasad.** Naprzemiennie dwa kroki, aż zasady przestaną się zmieniać.

1. *Ocena:* biorąc pod uwagę zasadę `π`, oblicz `V^π`, wielokrotnie stosując `V(s) ← Σ_a π(a|s) Σ_{s',r} P(s',r|s,a) [r + γ V(s')]`, aż osiągnie zbieżność.
2. *Ulepszenie:* biorąc pod uwagę `V^π`, spraw, aby `π` był zachłanny w.r.t. `V^π`: `π(s) ← argmax_a Σ_{s',r} P(s',r|s,a) [r + γ V(s')]`.

Zbieżność jest gwarantowana, ponieważ (a) każdy krok doskonalenia albo utrzymuje `π` na tym samym poziomie, albo znacznie zwiększa `V^π` dla jakiegoś stanu, (b) przestrzeń polityk deterministycznych jest skończona. Zwykle zbiega się w ~ 5–20 iteracjach zewnętrznych, nawet w przypadku dużych przestrzeni stanów.

**Iteracja wartości.** Łączy ocenę i poprawę w jednym cyklu. Zastosuj równanie *optymalności* Bellmana:

`V(s) ← max_a Σ_{s',r} P(s',r|s,a) [r + γ V(s')]`

Powtarzaj aż do `max_s |V_{new}(s) - V(s)| < ε`. Wyodrębnij politykę na końcu, podejmując zachłanną akcję. Zdecydowanie szybsze na iterację — bez wewnętrznej pętli oceny — ale zazwyczaj potrzeba więcej iteracji, aby osiągnąć zbieżność.

**Uogólniona iteracja polityki (GPI).** Ujednolicające ramy. Funkcja wartości i polityka są zamknięte w dwukierunkowej pętli doskonalenia; każda metoda, która prowadzi obie strony do wzajemnej spójności (asynchroniczna iteracja wartości, zmodyfikowana iteracja zasad, Q-learning, aktor krytyczny, PPO) jest instancją GPI.

**Dlaczego `γ < 1` ma znaczenie.** Operator Bellmana jest skurczem `γ` w normie sup: `||T V - T V'||_∞ ≤ γ ||V - V'||_∞`. Skurcz oznacza unikalny punkt stały i zbieżność geometryczną. Porzuć `γ < 1`, a stracisz gwarancję — potrzebujesz skończonego horyzontu lub absorbującego stanu końcowego.

## Zbuduj to

### Krok 1: zbuduj model GridWorld MDP

Użyj tego samego 4×4 GridWorld z lekcji 01. Dodajemy wariant stochastyczny: z prawdopodobieństwem `0.1` agent przesuwa się w losowo prostopadłym kierunku.

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

Biorąc pod uwagę zasadę `π(s) = {action: prob}`, iteruj równanie Bellmana, aż `V` przestanie się poruszać:

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

### Krok 3: poprawa polityki

Zamień `π` na zachłanną politykę w.r.t. `V`. Jeśli `π` się nie zmienił, wróć — jesteśmy w optymalnej sytuacji.

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

### Krok 4: zszyj je razem

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

Typowa zbieżność w 4 × 4: 4–6 zewnętrznych iteracji. Wynikiem jest `V*(0,0) ≈ -6` i zasada, która ściśle zmniejsza liczbę kroków.

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

Ten sam stały punkt, mniej linii kodu.

## Pułapki

- **Zapominanie o obsłudze terminali.** Jeśli zastosujesz Bellmana do stanu absorbującego, nadal będzie on wykonywał „najlepszą akcję”, która niczego nie zmienia. Strzeż za pomocą `if s == terminal: V[s] = 0`.
- **Dodatkowa norma a zbieżność L2.** Użyj `max |V_new - V|`, a nie średniej. Teoretyczna gwarancja jest na poziomie ponadnormowym.
- **Aktualizacje lokalne a aktualizacje synchroniczne.** Aktualizowanie `V[s]` lokalnie (Gauss-Seidel) jest szybsze niż oddzielny nakaz `V_new` (Jacobi). Kod produkcyjny wykorzystuje lokalnie.
- **Powiązania zasad.** Jeśli dwie akcje mają równą wartość Q, `argmax` może w każdej iteracji inaczej przerywać powiązania, powodując oscylację kontroli „stabilności polityki”. Użyj stabilnego tie-breaka (pierwsza akcja w ustalonej kolejności).
- **Eksplozja w przestrzeni stanów.** DP wynosi `O(|S| · |A|)` na cykl. Działa do ~10⁷ stanów. Poza tym potrzebne jest przybliżenie funkcji (faza 9 · 05 i później).

## Użyj tego

W roku 2026 DP jest bazą poprawności i wewnętrzną pętlą planistów:

| Przypadek użycia | Metoda |
|---------|--------|
| Rozwiąż dokładnie mały tabelaryczny MDP | Iteracja wartości (prostsza) lub iteracja polityki (mniej kroków zewnętrznych) |
| Zweryfikuj wdrożenie Q-learning / PPO | Porównanie z optymalnym DP V* w środowisku zabawek |
| RL oparty na modelu (faza 9 · 10) | Kopia zapasowa Bellmana w oparciu o wyuczony model przejścia |
| Planowanie w AlphaZero / MuZero | Wyszukiwanie drzewa Monte Carlo = asynchroniczna kopia zapasowa Bellmana |
| Offline RL (CQL, IQL) | Konserwatywna Q-iteracja — DP z karą za działania OOD |

Za każdym razem, gdy ktoś mówi „funkcja wartości optymalnej”, ma na myśli „punkt stały DP”. Kiedy zobaczysz `V*` lub `Q*` w gazecie, wyobraź sobie tę pętlę.

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

1. **Łatwe.** Uruchom iterację wartości w GridWorld 4×4 za pomocą `γ ∈ {0.9, 0.99}`. Ile cykli do `max |ΔV| < 1e-6`? Wydrukuj `V*` jako siatkę 4×4.
2. **Średni.** Porównaj iterację polityki z iteracją wartości w *stochastycznym* GridWorld (prawdopodobieństwo poślizgu `0.1`). Liczba: przebiegów, czas zegara ściennego, końcowy `V*(0,0)`. Co zbiega się szybciej w iteracjach? W zegarze ściennym?
3. **Trudne.** Utwórz iterację zmodyfikowanej polityki: na etapie oceny wykonaj tylko przeszukiwanie `k` zamiast do zbieżności. Wykreśl błąd `V*(0,0)` w funkcji `k` dla `k ∈ {1, 2, 5, 10, 50}`. Co krzywa mówi o kompromisie między oceną a poprawą?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Iteracja polityki | „Algorytm DP” | Naprzemienna ocena (`V^π`) i doskonalenie (chciwe `π` w.r.t. `V^π`), dopóki zasady nie przestaną się zmieniać. |
| Iteracja wartości | „Szybszy DP” | Kopia zapasowa optymalności Bellmana zastosowana za jednym razem; zbiega się geometrycznie do `V*`. |
| Operator Bellmana | „Rekursja” | `(T V)(s) = max_a Σ P (r + γ V(s'))`; `γ`-skurcz w normie. |
| Skurcz | „Dlaczego DP się łączy” | Każdy operator `T` z `\|\|T x - T y\|\| ≤ γ \|\|x - y\|\|` ma unikalny punkt stały. |
| GPI | „Wszystko jest DP” | Uogólniona iteracja zasad: dowolna metoda zapewniająca wzajemną spójność `V` i `π`. |
| Aktualizacja synchroniczna | „w stylu Jacobiego” | Używaj starego `V` podczas przeglądania; można łatwo przeanalizować, ale wolniej. |
| Aktualizacja na miejscu | „W stylu Gaussa-Seidla” | Użyj `V` podczas aktualizacji; w praktyce osiąga większą zbieżność. |

## Dalsze czytanie

- [Sutton i Barto (2018). Ch. 4 — Programowanie dynamiczne](http://incompleteideas.net/book/RLbook2020.pdf) — kanoniczna prezentacja iteracji polityki i iteracji wartości.
- [Bertsekas (2019). Uczenie się przez wzmocnienie i optymalna kontrola] (http://www.athenasc.com/rlbook.html) — rygorystyczne traktowanie argumentów mapowania skurczów.
- [Putermana (2005). Procesy decyzyjne Markowa](https://onlinelibrary.wiley.com/doi/book/10.1002/9780470316887) — zmodyfikowana iteracja polityki i analiza jej zbieżności.
- [Howarda (1960). Programowanie dynamiczne i procesy Markowa] (https://mitpress.mit.edu/9780262582300/dynamic-programming-and-markov-processes/) — oryginalny dokument dotyczący iteracji polityki.
- [Bertsekas i Tsitsiklis (1996). Programowanie neurodynamiczne](http://www.athenasc.com/ndpbook.html) — pomost od DP do przybliżonego DP / głębokiego RL używany na każdej kolejnej lekcji.