# Różnica czasowa — Q-Learning i SARSA

> Monte Carlo czeka, aż odcinek dobiegnie końca. TD aktualizuje wartości po każdym kroku, korzystając z bieżącego oszacowania. Q-learning jest niezgodny z polityką i optymistyczny; SARSA trzyma się zasad i działa ostrożnie. Oba algorytmy mieszczą się w jednej linii kodu. Oba stanowią fundament każdej metody głębokiego RL na tym etapie.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 9 · 01 (MDP), Faza 9 · 02 (Programowanie dynamiczne), Faza 9 · 03 (Monte Carlo)
**Czas:** ~75 minut

## Problem

Monte Carlo działa, lecz narzuca dwa kosztowne ograniczenia. Wymaga odcinków, które się kończą, i aktualizuje wartości dopiero po otrzymaniu końcowego zwrotu. Gdy odcinek liczy 1000 kroków, MC czeka na wszystkie 1000 przed jakąkolwiek aktualizacją. Wynik to duża wariancja, niski błąd systematyczny i powolne działanie w praktyce.

Programowanie dynamiczne ma odwrotny profil — kopie zapasowe z zerową wariancją — lecz wymaga znajomości modelu środowiska.

Uczenie przez różnicę czasową (TD) stanowi kompromis między tymi podejściami. Na podstawie pojedynczego przejścia `(s, a, r, s')` tworzy jednoetapowy cel `r + γ V(s')` i przesuwa ku niemu `V(s)`. Bez modelu. Bez pełnych odcinków. Błąd wynika z użycia przybliżonego `V` po prawej stronie równania, lecz wariancja jest znacznie mniejsza niż w MC, a aktualizacje odbywają się online od pierwszego kroku.

To jest oś, wokół której obraca się cały nowoczesny RL — DQN, A2C, PPO, SAC. Pozostała część fazy 9 to warstwy aproksymacji funkcji i techniki zbudowane na bazie jednoetapowej aktualizacji TD, którą napiszesz w tej lekcji.

## Koncepcja

![Q-learning vs SARSA: maks. niezgodne z zasadami vs Q(s', a') zgodne z zasadami](../assets/td.svg)

**Aktualizacja TD(0) dla V:**

`V(s) ← V(s) + α [r + γ V(s') - V(s)]`

Wyrażenie w nawiasach to błąd TD: `δ = r + γ V(s') - V(s)`. Jest to odpowiednik online wyrażenia `G_t - V(s_t)` z MC. Zbieżność wymaga, aby `α` spełniało warunki Robbinsa-Monroe (`Σ α = ∞`, `Σ α² < ∞`) oraz aby każdy stan był odwiedzany nieskończenie często.

**Q-learning.** Metoda kontroli TD niezgodna z polityką:

`Q(s, a) ← Q(s, a) + α [r + γ max_{a'} Q(s', a') - Q(s, a)]`

Operator `max` zakłada, że od stanu `s'` będzie stosowana polityka zachłanna, niezależnie od tego, jaką akcję faktycznie podejmie agent. To rozdzielenie sprawia, że Q-learning wyznacza `Q*`, podczas gdy agent eksploruje przy użyciu ε-zachłanności. Mnih i in. (2015) rozwinęli tę ideę do głębokiego Q-learningu na Atari (lekcja 05).

**SARSA.** Metoda TD zgodna z polityką:

`Q(s, a) ← Q(s, a) + α [r + γ Q(s', a') - Q(s, a)]`

Nazwa pochodzi od krotki `(s, a, r, s', a')`. SARSA używa akcji `a'`, którą agent *faktycznie* wykonuje jako następną, a nie zachłannego `argmax`. Zbiega się do `Q^π` dla dowolnego ε-zachłannego `π`, który w granicy `ε → 0` przechodzi w `Q*`.

**Różnica w zadaniu chodzenia po klifach.** W klasycznym problemie chodzenia po klifach (upadek z klifu = nagroda -100) Q-learning wyznacza optymalną ścieżkę wzdłuż krawędzi, lecz podczas eksploracji czasem ponosi karę. SARSA wyznacza bezpieczniejszą trasę oddaloną o krok od klifu, ponieważ uwzględnia szum eksploracji w wartości Q. Po treningu oba algorytmy osiągają optimum przy `ε → 0`. W praktyce ma to znaczenie: gdy w momencie wdrożenia nadal trwa eksploracja, zachowanie SARSA jest bardziej zachowawcze.

**Oczekiwany SARSA.** Zastąp `Q(s', a')` jego wartością oczekiwaną pod polityką `π`:

`Q(s, a) ← Q(s, a) + α [r + γ Σ_{a'} π(a'|s') Q(s', a') - Q(s, a)]`

Wariancja jest niższa niż w SARSA (brak próbkowania `a'`), a cel pozostaje zgodny z polityką. We współczesnych podręcznikach jest to często wariant domyślny.

**n-krokowy TD i TD(λ).** Interpolacja między TD(0) a MC przez czekanie `n` kroków przed wykonaniem aktualizacji. Dla `n=1` otrzymujemy TD, dla `n=∞` — MC. TD(λ) uśrednia wszystkie warianty n-krokowe z wagami geometrycznymi `(1-λ)λ^{n-1}`. Większość metod głębokiego RL używa `n` z zakresu od 3 do 20.

## Zbuduj to

### Krok 1: SARSA zgodny z polityką ε-zachłanną

```python
def sarsa(env, episodes, alpha=0.1, gamma=0.99, epsilon=0.1):
    Q = defaultdict(lambda: {a: 0.0 for a in ACTIONS})

    def choose(s):
        if random() < epsilon:
            return choice(ACTIONS)
        return max(Q[s], key=Q[s].get)

    for _ in range(episodes):
        s = env.reset()
        a = choose(s)
        while True:
            s_next, r, done = env.step(s, a)
            a_next = choose(s_next) if not done else None
            target = r + (gamma * Q[s_next][a_next] if not done else 0.0)
            Q[s][a] += alpha * (target - Q[s][a])
            if done:
                break
            s, a = s_next, a_next
    return Q
```

Osiem linii. *Jedyną* różnicą względem Q-learningu jest linia wyznaczająca cel.

### Krok 2: Q-learning

```python
def q_learning(env, episodes, alpha=0.1, gamma=0.99, epsilon=0.1):
    Q = defaultdict(lambda: {a: 0.0 for a in ACTIONS})
    for _ in range(episodes):
        s = env.reset()
        while True:
            a = choose(s, Q, epsilon)
            s_next, r, done = env.step(s, a)
            target = r + (gamma * max(Q[s_next].values()) if not done else 0.0)
            Q[s][a] += alpha * (target - Q[s][a])
            if done:
                break
            s = s_next
    return Q
```

Operator `max` rozdziela cel od zachowania. Ten jeden symbol stanowi różnicę między uczeniem zgodnym z polityką a uczeniem niezgodnym z polityką.

### Krok 3: krzywe uczenia się

Śledź średni zwrot na 100 odcinków. Q-learning szybciej zbiega się w prostym, deterministycznym GridWorld; SARSA zachowuje się ostrożniej w zadaniu chodzenia po klifach. W siatce GridWorld 4×4 w `code/main.py` oba algorytmy są bliskie optimum po około 2000 odcinków przy `α=0.1, ε=0.1`.

### Krok 4: porównanie z rozwiązaniem dokładnym DP

Uruchom iterację wartości (lekcja 02), aby uzyskać `Q*`. Sprawdź `max_{s,a} |Q_learned(s,a) - Q*(s,a)|`. Sprawny tabelaryczny agent TD uzyskuje wynik rzędu `~0.5` w GridWorld 4×4 po 10 000 odcinków.

## Pułapki

- **Wartości początkowe Q mają znaczenie.** Optymistyczna inicjalizacja (`Q = 0` przy ujemnych nagrodach) zachęca do eksploracji. Pesymistyczny start może trwale uwięzić politykę zachłanną.
- **Harmonogram α.** Stały `α` sprawdza się w problemach niestacjonarnych. Rozkład `α_n = 1/n` zapewnia zbieżność w teorii, lecz w praktyce jest zbyt powolny — ustaw `α` w przedziale `[0.05, 0.3]` i obserwuj krzywą uczenia się.
- **Harmonogram ε.** Zacznij od wysokiej wartości (`ε=1.0`) i zmniejszaj do `ε=0.05`. Warunek GLIE (zachłanny w granicy z nieskończoną eksploracją) jest wymagany do zbieżności.
- **Błąd maksymalizacji w Q-learningu.** Operator `max` zawyża wartości, gdy `Q` jest zaszumione, co prowadzi do przeszacowania. Metoda Double Q-learning Hasselta (używana przez DDQN w lekcji 05) rozwiązuje ten problem za pomocą dwóch oddzielnych tablic Q.
- **Odcinki bez zakończenia.** TD może uczyć się bez stanów terminalnych, lecz należy albo ograniczyć liczbę kroków, albo poprawnie obsłużyć bootstrapping na końcu. Standardowe podejście: traktuj osiągnięcie limitu jako stan nieterminalny i kontynuuj aktualizacje.
- **Haszowanie stanu.** Jeśli stany są krotkami lub tensorami, używaj kluczy obsługujących haszowanie (krotka zamiast listy; krotka wartości zmiennoprzecinkowych zaokrąglonych, nie surowych).

## Zastosowania

Krajobraz TD w 2026 roku:

| Zadanie | Metoda | Powód |
|------|--------|--------|
| Małe środowiska tabelaryczne | Q-learning | Uczy się bezpośrednio optymalnej polityki. |
| Krytyczne dla bezpieczeństwa, zgodne z polityką | SARSA / Oczekiwany SARSA | Zachowawcze podczas eksploracji. |
| Wielowymiarowa przestrzeń stanów | DQN (faza 9 · 05) | Sieć neuronowa jako funkcja Q z buforem powtórek i siecią docelową. |
| Akcje ciągłe | SAC / TD3 (faza 9 · 07) | Aktualizacja TD w sieci Q; sieć polityk generuje akcje. |
| RL dla LLM (z modelem nagrody) | PPO / GRPO (faza 9 · 08, 12) | Aktor-krytyk z przewagą w stylu TD poprzez GAE. |
| Uczenie offline (offline RL) | CQL/IQL (faza 9 · 08) | Q-learning z konserwatywną regularyzacją. |

Dziewięćdziesiąt procent metod RL, o których czytasz w artykułach z 2026 roku, to rozwinięcia Q-learningu lub SARSA. Zanim zagłębisz się w bardziej zaawansowane zagadnienia, opanuj tabelaryczną aktualizację TD do perfekcji.

## Wyślij to

Zapisz jako `outputs/skill-td-agent.md`:

```markdown
---
name: td-agent
description: Pick between Q-learning, SARSA, Expected SARSA for a tabular or small-feature RL task.
version: 1.0.0
phase: 9
lesson: 4
tags: [rl, td-learning, q-learning, sarsa]
---

Given a tabular or small-feature environment, output:

1. Algorithm. Q-learning / SARSA / Expected SARSA / n-step variant. One-sentence reason tied to on-policy vs off-policy and variance.
2. Hyperparameters. α, γ, ε, decay schedule.
3. Initialization. Q_0 value (optimistic vs zero) and justification.
4. Convergence diagnostic. Target learning curve, `|Q - Q*|` check if DP is possible.
5. Deployment caveat. How will exploration behave at inference? Is SARSA's conservatism needed?

Refuse to apply tabular TD to state spaces > 10⁶. Refuse to ship a Q-learning agent without a max-bias caveat. Flag any agent trained with ε held at 1.0 throughout (no exploitation phase).
```

## Ćwiczenia

1. **Łatwe.** Zaimplementuj Q-learning i SARSA w GridWorld 4×4. Narysuj krzywe uczenia się (średni zwrot na 100 odcinków) dla 2000 odcinków. Który algorytm zbiega się szybciej?
2. **Średnie.** Zbuduj środowisko chodzenia po klifach (siatka 4×12, ostatni rząd to klif z nagrodą -100 i powrotem do startu). Porównaj wynikowe polityki Q-learningu i SARSA. Zrób zrzut ekranu pokazujący ścieżki obu algorytmów. Która z nich biegnie bliżej krawędzi?
3. **Trudne.** Zaimplementuj Double Q-learning. W zaszumionym GridWorld (szum Gaussa σ=5 dodany do nagrody za krok) pokaż, że Q-learning zawyża `V*(0,0)` o istotną wartość, podczas gdy Double Q-learning tego unika.

## Kluczowe terminy

| Termin | Co się mówi | Co to faktycznie oznacza |
|------|-----------------|----------------------|
| Błąd TD | „Sygnał aktualizacji" | `δ = r + γ V(s') - V(s)` — zaktualizowana reszta. |
| TD(0) | „Jednoetapowe uczenie TD" | Aktualizuj po każdym przejściu, korzystając wyłącznie z oszacowania następnego stanu. |
| Q-learning | „Niezgodny z polityką RL 101" | Aktualizacja TD z operatorem `max` nad akcjami następnego stanu; wyznacza `Q*` niezależnie od polityki zachowania. |
| SARSA | „Q-learning zgodny z polityką" | Aktualizacja TD z faktycznie podjętą następną akcją; wyznacza `Q^π` dla bieżącego ε-zachłannego π. |
| Oczekiwany SARSA | „SARSA o niskiej wariancji" | Zastępuje próbkowane `a'` jego wartością oczekiwaną pod π. |
| GLIE | „Właściwy harmonogram eksploracji" | Zachłanny w granicy z nieskończoną eksploracją; wymagany do zbieżności Q-learningu. |
| Bootstrapping | „Cel oparty na bieżącym oszacowaniu" | To, co odróżnia TD od MC. Źródło błędu systematycznego, lecz znacznie zmniejsza wariancję. |
| Błąd maksymalizacji | „Q-learning przeszacowuje" | Operator `max` zawyża zaszumione oszacowania; rozwiązaniem jest Double Q-learning. |

## Dalsza lektura

- [Watkins i Dayan (1992). Q-learning](https://link.springer.com/article/10.1007/BF00992698) — artykuł oryginalny wraz z dowodem zbieżności.
- [Sutton i Barto (2018). Ch. 6 — Uczenie się na podstawie różnicy czasowej](http://incompleteideas.net/book/RLbook2020.pdf) — TD(0), SARSA, Q-learning, oczekiwany SARSA.
- [Hasselt (2010). Double Q-learning](https://papers.nips.cc/paper_files/paper/2010/hash/091d584fced301b442654dd8c23b3fc9-Abstract.html) — rozwiązanie problemu błędu maksymalizacji.
- [Seijen, Hasselt, Whiteson, Wiering (2009). Teoretyczna i empiryczna analiza oczekiwanej SARSA](https://ieeexplore.ieee.org/document/4927542) — uzasadnienie dla oczekiwanego SARSA.
- [Rummery i Niranjan (1994). Q-learning online z wykorzystaniem systemów koneksjonistycznych](https://www.researchgate.net/publication/2500611_On-Line_Q-Learning_Using_Connectionist_Systems) — artykuł, w którym wprowadzono nazwę SARSA (wówczas określaną jako „zmodyfikowany koneksjonistyczny Q-learning").
- [Sutton i Barto (2018). Ch. 7 — n-step Bootstrapping](http://incompleteideas.net/book/RLbook2020.pdf) — uogólnienie TD(0) na TD(n), droga od Q-learningu przez ślady kwalifikowalności do GAE w PPO.
