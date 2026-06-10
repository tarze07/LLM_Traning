# Metody Monte Carlo — nauka na podstawie całych odcinków

> Programowanie dynamiczne wymaga modelu. Monte Carlo nie potrzebuje nic poza epizodami. Uruchom politykę, obserwuj zwroty, uśredniaj je. Najprostszy pomysł w RL — i ten, który otwiera drzwi do wszystkiego, co nastąpi później.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 9 · 01 (MDP), Faza 9 · 02 (programowanie dynamiczne)
**Czas:** ~75 minut

## Problem

Programowanie dynamiczne jest eleganckie, lecz zakłada możliwość odpytywania `P(s' | s, a)` dla każdego stanu i akcji. Niemal nic w rzeczywistym świecie nie działa w ten sposób. Robot nie jest w stanie analitycznie wyznaczyć rozkładu pikseli kamery po zadaniu momentu obrotowego. Algorytm wyceny nie może scałkować wszystkich możliwych reakcji klientów. LLM nie wyliczy wszystkich możliwych kontynuacji po danym tokenie.

Potrzebna jest metoda, która wymaga jedynie możliwości *próbkowania* ze środowiska. Uruchamiamy politykę, uzyskujemy trajektorię `s_0, a_0, r_1, s_1, a_1, r_2, …, s_T` i używamy jej do oszacowania wartości. To właśnie jest Monte Carlo.

Przejście z DP na MC ma duże znaczenie filozoficzne: zamiast *znanego modelu i dokładnych kopii zapasowych* korzystamy z *próbnych przebiegów i uśrednionego zwrotu*. Wariancja rośnie, ale zakres zastosowań gwałtownie się poszerza. Każdy algorytm RL omawiany po tej lekcji — TD, Q-learning, REINFORCE, PPO, GRPO — jest w istocie estymatorem Monte Carlo, nierzadko wzbogaconym o mechanizm bootstrapowania.

## Koncepcja

![Monte Carlo: wdrożenie, obliczenie zwrotu, średnia; pierwsza wizyta a każda wizyta](../assets/monte-carlo.svg)

**Podstawowa idea w jednej linii:** `V^π(s) = E_π[G_t | s_t = s] ≈ (1/N) Σ_i G^{(i)}(s)`, gdzie `G^{(i)}(s)` to zaobserwowany zwrot po odwiedzeniu stanu `s` zgodnie z polityką `π`.

**Pierwsza wizyta a każda wizyta.** Gdy stan `s` pojawia się w odcinku wielokrotnie, MC przy pierwszej wizycie uwzględnia tylko zwrot z pierwszego pojawienia; MC przy każdej wizycie bierze pod uwagę wszystkie wystąpienia. Obydwa podejścia są asymptotycznie nieobciążone. Analiza MC przy pierwszej wizycie jest prostsza, ponieważ próbki są niezależne i jednakowo rozłożone. MC przy każdej wizycie lepiej wykorzystuje dane z odcinka i w praktyce zazwyczaj zbiega szybciej.

**Średnia przyrostowa.** Zamiast przechowywać wszystkie zwroty, wystarczy aktualizować średnią kroczącą:

`V_n(s) = V_{n-1}(s) + (1/n) [G_n - V_{n-1}(s)]`

Po przekształceniu: `V_new = V_old + α · (target - V_old)`, gdzie `α = 1/n`. Zastąpienie `1/n` stałym krokiem `α ∈ (0, 1)` daje niestacjonarny estymator MC, który śledzi zmiany polityki `π`. Ten zabieg stanowi fundament przejścia od MC przez TD do wszystkich nowoczesnych algorytmów RL.

**Eksploracja staje się problemem.** DP odwiedza każdy stan poprzez wyliczenie. MC widzi tylko te stany, które odwiedza dana polityka. Jeśli `π` jest deterministyczna, całe obszary przestrzeni stanów nigdy nie są próbkowane, a ich szacunki wartości pozostają zerowe. Istnieją trzy historyczne rozwiązania tego problemu:

1. **Eksploracyjne starty.** Każdy odcinek rozpoczyna się od losowo wybranej pary (s, a). Gwarantuje pokrycie, lecz jest nierealistyczne w praktyce — nie zawsze można „zresetować" robota do dowolnego stanu.
2. **ε-zachłanność.** Działaj zachłannie względem bieżącego Q, ale z prawdopodobieństwem `ε` wybierz losową akcję. Asymptotycznie wszystkie pary stan-akcja są próbkowane.
3. **MC niezgodne z polityką.** Zbieramy dane zgodnie z polityką zachowania `μ`, a politykę docelową `π` szacujemy za pomocą ważenia ważnością próbkowania. Metoda ta cechuje się wysoką wariancją, lecz stanowi pomost do technik bufora odtwarzania, takich jak DQN.

**Sterowanie Monte Carlo.** Schemat: oceń → ulepsz → oceń — analogiczny do iteracji polityki, ale ocena opiera się na próbkowaniu:

1. Uruchom politykę `π` i pobierz odcinek.
2. Zaktualizuj `Q(s, a)` na podstawie zaobserwowanych zwrotów.
3. Spraw, by `π` była ε-zachłanna względem `Q`.
4. Powtórz.

Przy łagodnych założeniach (każda para odwiedzana nieskończenie często, kroki `α` spełniające warunki Robbinsa-Monro) metoda zbiega do `Q*` i `π*` z prawdopodobieństwem 1.

## Zbuduj to

### Krok 1: przebieg polityki → lista (s, a, r)

```python
def rollout(env, policy, max_steps=200):
    trajectory = []
    s = env.reset()
    for _ in range(max_steps):
        a = policy(s)
        s_next, r, done = env.step(s, a)
        trajectory.append((s, a, r))
        s = s_next
        if done:
            break
    return trajectory
```

Żadnego modelu — tylko `env.reset()` i `env.step(s, a)`. Ten sam interfejs co środowisko gymnasium, ale uproszczony.

### Krok 2: obliczenie zwrotów (przemiatanie wsteczne)

```python
def returns_from(trajectory, gamma):
    returns = []
    G = 0.0
    for _, _, r in reversed(trajectory):
        G = r + gamma * G
        returns.append(G)
    return list(reversed(returns))
```

Jedno przejście, złożoność `O(T)`. Iterowanie wstecz zgodnie z `G_t = r_{t+1} + γ G_{t+1}` eliminuje potrzebę ponownego sumowania.

### Krok 3: ocena MC przy pierwszej wizycie

```python
def mc_policy_evaluation(env, policy, episodes, gamma=0.99):
    V = defaultdict(float)
    counts = defaultdict(int)
    for _ in range(episodes):
        trajectory = rollout(env, policy)
        returns = returns_from(trajectory, gamma)
        seen = set()
        for t, ((s, _, _), G) in enumerate(zip(trajectory, returns)):
            if s in seen:
                continue
            seen.add(s)
            counts[s] += 1
            V[s] += (G - V[s]) / counts[s]
    return V
```

Całą logikę realizują trzy linie: oznaczenie stanu jako odwiedzonego po pierwszym spotkaniu, inkrementacja licznika i aktualizacja średniej kroczącej.

### Krok 4: ε-zachłanne sterowanie MC (zgodne z polityką)

```python
def mc_control(env, episodes, gamma=0.99, epsilon=0.1):
    Q = defaultdict(lambda: {a: 0.0 for a in ACTIONS})
    counts = defaultdict(lambda: {a: 0 for a in ACTIONS})

    def policy(s):
        if random() < epsilon:
            return choice(ACTIONS)
        return max(Q[s], key=Q[s].get)

    for _ in range(episodes):
        trajectory = rollout(env, policy)
        returns = returns_from(trajectory, gamma)
        seen = set()
        for (s, a, _), G in zip(trajectory, returns):
            if (s, a) in seen:
                continue
            seen.add((s, a))
            counts[s][a] += 1
            Q[s][a] += (G - Q[s][a]) / counts[s][a]
    return Q, policy
```

### Krok 5: porównanie ze złotym standardem DP

Szacunki MC dla `V^π` powinny zbiegać do wyników DP z lekcji 02 wraz ze wzrostem liczby odcinków. W praktyce 50 000 odcinków w siatce 4×4 GridWorld daje wyniki zgodne z DP z dokładnością do `~0.1`.

## Pułapki

- **Nieskończone odcinki.** MC wymaga, aby odcinki *kończyły się*. Jeśli polityka może wpaść w nieskończoną pętlę, należy zastosować ograniczenie `max_steps` i traktować jego przekroczenie jako ukryte niepowodzenie. Losowa polityka w GridWorld często przekracza limit — to normalne zachowanie, ważne jest tylko właściwe jego obsłużenie.
- **Wariancja.** MC operuje na pełnych zwrotach. Przy długich odcinkach wariancja jest ogromna — pojedyncza pechowa nagroda na końcu przesuwa `V(s_0)` o tę samą wartość. Metody TD (lekcja 04) rozwiązują ten problem przez bootstrapowanie.
- **Pokrycie przestrzeni stanów.** Zachłanny MC uruchomiony na świeżym Q bez eksploracji wypróbuje tylko jedną akcję. Eksploracja jest niezbędna — ε-zachłanność, eksploracyjne starty lub UCB.
- **Niestacjonarne polityki.** Gdy `π` ewoluuje (jak w sterowaniu MC), stare zwroty pochodzą z innej wersji polityki. MC ze stałym krokiem `α` radzi sobie z tym problemem; MC ze średnią z próby — nie.
- **Ważenie ważnością próbkowania poza polityką.** Wagi `π(a|s)/μ(a|s)` mnożą się wzdłuż trajektorii. Wariancja rośnie wykładniczo z horyzontem. Należy stosować ważenie per decyzja lub przejść na metody TD.

## Zastosowania

Rola metod Monte Carlo w 2026 roku:

| Przypadek użycia | Uzasadnienie wyboru MC |
|---------|--------|
| Gry o krótkim horyzoncie (blackjack, poker) | Odcinki kończą się naturalnie; zwroty są czytelne. |
| Ocena offline zarejestrowanej polityki | Uśrednione zdyskontowane zwroty wyznaczane na podstawie zapisanych trajektorii. |
| Przeszukiwanie drzewa Monte Carlo (AlphaZero) | Przebiegi MC z liści drzewa służą do oceny węzłów przy wyborze akcji. |
| Ocena LLM w RL | Średnia nagroda obliczana na podstawie próbnych uzupełnień dla danej polityki. |
| Wartość bazowa w PPO | Cel funkcji przewagi `A_t = G_t - V(s_t)` korzysta z MC-owego `G_t`. |
| Nauczanie RL | Najprostszy działający algorytm — usunięcie bootstrapowania odsłania rdzeń metody. |

Nowoczesne algorytmy deep-RL, takie jak PPO i SAC, interpolują między czystym MC (pełne zwroty) a czystym TD (jednoetapowe bootstrapowanie) za pomocą zwrotów n-krokowych lub GAE. Oba skrajne przypadki są przejawami tego samego estymatora.

## Wyślij to

Zapisz jako `outputs/skill-mc-evaluator.md`:

```markdown
---
name: mc-evaluator
description: Evaluate a policy via Monte Carlo rollouts and produce a convergence report with DP-comparison if available.
version: 1.0.0
phase: 9
lesson: 3
tags: [rl, monte-carlo, evaluation]
---

Given an environment (episodic, with reset+step API) and a policy, output:

1. Method. First-visit vs every-visit MC. Reason.
2. Episode budget. Target number, variance diagnostic, expected standard error.
3. Exploration plan. ε schedule (if needed) or exploring starts.
4. Gold-standard comparison. DP-optimal V* if tabular; otherwise a bound from a Q-learning / PPO baseline.
5. Termination check. Max-step cap, timeouts, handling of non-terminating trajectories.

Refuse to run MC on non-episodic tasks without a finite horizon cap. Refuse to report V^π estimates from fewer than 100 episodes per state for tabular tasks. Flag any policy with zero-variance actions as an exploration risk.
```

## Ćwiczenia

1. **Łatwe.** Zaimplementuj ocenę jednolitej polityki losowej metodą MC przy pierwszej wizycie w siatce 4×4 GridWorld. Uruchom 10 000 odcinków. Wykreśl `V(0,0)` jako funkcję liczby odcinków i porównaj z odpowiedzią DP.
2. **Średnie.** Zaimplementuj ε-zachłanne sterowanie MC dla `ε ∈ {0.01, 0.1, 0.3}`. Porównaj średni zwrot po 20 000 odcinków. Jak wygląda krzywa zależności? Gdzie leży kompromis między obciążeniem a wariancją?
3. **Trudne.** Zaimplementuj *off-policy* MC z ważeniem ważnością próbkowania: zbierz dane zgodnie z polityką jednostajnie losową `μ`, a następnie oszacuj `V^π` dla deterministycznej polityki optymalnej `π`. Porównaj zwykłe IS, IS per decyzja i ważone IS. Która metoda osiąga najmniejszą wariancję?

## Kluczowe terminy

| Termin | Potoczna definicja | Właściwe znaczenie |
|------|-----------------|----------------------|
| Monte Carlo | „Losowe próbkowanie" | Szacowanie wartości oczekiwanych przez uśrednianie niezależnych próbek z danego rozkładu. |
| Zwrot `G_t` | „Przyszła nagroda" | Suma zdyskontowanych nagród od kroku `t` do końca odcinka: `Σ_{k≥0} γ^k r_{t+k+1}`. |
| Pierwsza wizyta MC | „Licz każdy stan raz" | Do oszacowania wartości uwzględniana jest wyłącznie pierwsza wizyta w danym odcinku. |
| Każda wizyta MC | „Wykorzystaj wszystkie wizyty" | Każda wizyta wnosi wkład; metoda jest nieco obciążona, lecz efektywniej wykorzystuje dane. |
| ε-zachłanność | „Szum eksploracyjny" | Akcja zachłanna wybierana z prawdopodobieństwem `1-ε`; losowa akcja z prawdopodobieństwem `ε`. |
| Ważenie ważnością próbkowania | „Korekcja próbkowania z niewłaściwego rozkładu" | Zwroty są ważone iloczynem `π(a\|s)/μ(a\|s)`, co pozwala szacować `V^π` na podstawie danych zebranych przez `μ`. |
| Zgodne z polityką | „Ucz się na własnych danych" | Polityka docelowa jest tożsama z polityką zachowania. Dotyczy m.in. MC, PPO i SARSA. |
| Niezgodne z polityką | „Ucz się na cudzych danych" | Polityka docelowa różni się od polityki zachowania. Dotyczy m.in. MC z ważeniem IS, Q-learningu i DQN. |

## Dalsza lektura

- [Sutton i Barto (2018). Ch. 5 — Metody Monte Carlo](http://incompleteideas.net/book/RLbook2020.pdf) — kanoniczne omówienie tematu.
- [Singh i Sutton (1996). Uczenie się przez wzmacnianie z wykorzystaniem śladów kwalifikowalności](https://link.springer.com/article/10.1007/BF00114726) — analiza porównawcza MC przy pierwszej i każdej wizycie.
- [Precup, Sutton, Singh (2000). Ślady kwalifikowalności do oceny polityki poza polityką](http://incompleteideas.net/papers/PSS-00.pdf) — MC poza polityką i kontrola rozbieżności.
- [Mahmood i in. (2014). Ważone próbkowanie ważnością do uczenia poza polityką](https://arxiv.org/abs/1404.6362) — nowoczesne estymatory IS o niskiej wariancji.
- [Tesauro (1995). TD-Gammon, program do samodzielnej nauki gry w backgammona](https://dl.acm.org/doi/10.1145/203330.203343) — pierwsza empiryczna demonstracja na dużą skalę, w której samogranie oparte na MC/TD zbiega do poziomu ponadludzkiego; koncepcyjny poprzednik wszystkich lekcji w drugiej połowie tej fazy.
