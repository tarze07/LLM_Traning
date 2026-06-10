# Metody Monte Carlo — nauka na podstawie całych odcinków

> Programowanie dynamiczne wymaga modelu. Monte Carlo nie potrzebuje nic poza epizodami. Uruchom polisę, obserwuj zwroty, uśredniaj je. Najprostszy pomysł w RL — i ten, który odblokowuje wszystko na dalszym etapie.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 9 · 01 (MDP), Faza 9 · 02 (programowanie dynamiczne)
**Czas:** ~75 minut

## Problem

Programowanie dynamiczne jest eleganckie, ale zakłada, że możesz wysyłać zapytania `P(s' | s, a)` o każdy stan i akcję. Prawie nic w prawdziwym świecie nie działa w ten sposób. Robot nie może analitycznie obliczyć rozkładu w pikselach kamery po wspólnym momencie obrotowym. Algorytm ustalania cen nie jest w stanie zintegrować każdej możliwej reakcji klienta. LLM nie może wyliczyć wszystkich możliwych kontynuacji po tokenie.

Potrzebujesz metody, która wymaga jedynie możliwości *próbkowania* ze środowiska. Uruchom politykę. Uzyskaj trajektorię `s_0, a_0, r_1, s_1, a_1, r_2, …, s_T`. Użyj go do oszacowania wartości. Czyli Monte Carlo.

Przejście z DP na MC jest ważne z filozoficznego punktu widzenia: przechodzimy od *znanego modelu + dokładnej kopii zapasowej* do *próbnych wdrożeń + uśrednionego zwrotu*. Wariancja skacze, ale zastosowanie eksploduje. Każdy algorytm RL po tej lekcji — TD, Q-learning, REINFORCE, PPO, GRPO — jest w istocie estymatorem Monte Carlo, czasem z nałożonym na niego ładowaniem początkowym.

## Koncepcja

![Monte Carlo: wdrożenie, obliczenie zwrotu, średnia; pierwsza wizyta a każda wizyta](../assets/monte-carlo.svg)

**Podstawowa idea w jednym wierszu:** `V^π(s) = E_π[G_t | s_t = s] ≈ (1/N) Σ_i G^{(i)}(s)`, gdzie obserwuje się `G^{(i)}(s)`, powraca po wizytach w `s` zgodnie z polityką `π`.

**Pierwsza wizyta a MC przy każdej wizycie.** Biorąc pod uwagę odcinek, w którym odwiedzany jest stan `s` wiele razy, MC przy pierwszej wizycie liczy się tylko powrót z pierwszej wizyty; MC przy każdej wizycie liczy wszystkie wizyty. Obaj są bezstronni w limicie. Analiza pierwszej wizyty jest prostsza (próbki iid). Przy każdej wizycie zużywa się więcej danych na odcinek i w praktyce zazwyczaj osiągane są one szybciej.

**Średnia przyrostowa.** Zamiast zapisywać wszystkie zwroty, zaktualizuj średnią kroczącą:

`V_n(s) = V_{n-1}(s) + (1/n) [G_n - V_{n-1}(s)]`

Zreorganizuj: `V_new = V_old + α · (target - V_old)` za pomocą `α = 1/n`. Zamień `1/n` na stały rozmiar kroku `α ∈ (0, 1)`, a otrzymasz niestacjonarny estymator MC, który śledzi zmiany w `π`. Ten ruch to cały skok od MC do TD do każdego nowoczesnego algorytmu RL.

**Eksploracja jest teraz problemem.** DP dotknął każdego stanu poprzez wyliczenie. MC widzi tylko stany, które odwiedzają politycy. Jeśli `π` jest deterministyczny, całe obszary przestrzeni stanów nigdy nie są próbkowane, a ich szacunki wartości pozostają na zawsze równe zeru. Trzy poprawki, w kolejności historycznej:

1. **Rozpoczyna się eksploracja.** Rozpocznij każdy odcinek od losowej pary (s, a). Gwarantuje pokrycie; nierealne w praktyce (nie można „zresetować” robota do dowolnego stanu).
2. **ε-chciwy.** Działaj zachłannie w.r.t. bieżące Q, ale z prawdopodobieństwem `ε` wybierz losową akcję. Wszystkie pary stan-akcja są próbkowane asymptotycznie.
3. **MC niezgodny z polityką.** Zbieraj dane zgodnie z polityką zachowania `μ`, poznaj politykę docelową `π` poprzez próbkowanie ważności. Wysoka wariancja, ale jest to pomost do metod buforowania odtwarzania, takich jak DQN.

**Kontrola Monte Carlo.** Oceń → ulepsz → oceń, podobnie jak w przypadku iteracji polityki, ale ocena opiera się na próbkowaniu:

1. Uruchom `π`, pobierz odcinek.
2. Zaktualizuj `Q(s, a)` na podstawie zaobserwowanych zwrotów.
3. Zrób `π` ε-chciwy w.r.t. `Q`.
4. Powtórz.

Zbiega się do `Q*` i `π*` z prawdopodobieństwem 1 w łagodnych warunkach (każda para odwiedzana nieskończenie często, `α` zadowala Robbinsa-Monro).

## Zbuduj to

### Krok 1: wdrożenie → lista (s, a, r)

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

Brak modelu, tylko `env.reset()` i `env.step(s, a)`. Ten sam interfejs, co środowisko siłowni, ale uproszczony.

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

Jedno przejście, `O(T)`. Powtarzanie wstecz `G_t = r_{t+1} + γ G_{t+1}` pozwala uniknąć ponownego sumowania.

### Krok 3: ocena MC po pierwszej wizycie

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

Pracę wykonują trzy linie: zaznacz stan widoczny podczas pierwszej wizyty, liczbę przyrostów, zaktualizuj średnią bieżącą.

### Krok 4: ε-chciwa kontrola MC (na zasadach)

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

### Krok 5: porównaj ze złotym standardem DP

Twoje szacunki MC dotyczące `V^π` powinny zgadzać się z wynikami DP z Lekcji 02 jako odcinki → ∞. W praktyce: 50 000 odcinków w sieci 4×4 GridWorld zapewnia odpowiedź DP w `~0.1`.

## Pułapki

- **Nieskończona liczba odcinków.** MC wymaga, aby odcinki *zakończyły się*. Jeśli Twoja polityka może zapętlać się w nieskończoność, zastosuj ograniczenie `max_steps` i potraktuj ograniczenie jako ukryte niepowodzenie. GridWorld z losową polityką rutynowo przekracza limit czasu — jest to normalne, tylko upewnij się, że policzyłeś go poprawnie.
- **Wariancja.** MC wykorzystuje pełne zwroty. W przypadku długich odcinków rozbieżność jest ogromna — jedna pechowa nagroda na końcu przesuwa `V(s_0)` o tę samą kwotę. Metody TD (lekcja 04) rozwiązują ten problem poprzez ładowanie początkowe.
- **Zasięg stanu.** Chciwy MC na świeżym Q z remisem spróbuje tylko jednej akcji. *Musisz* eksplorować (ε-chciwość, rozpoczynanie eksploracji, UCB).
- **Polityki niestacjonarne.** Jeśli `π` ulegnie zmianie (jak w przypadku kontroli MC), stare zwroty pochodzą z innej polisy. Constant-α MC sobie z tym radzi; MC z próbki średniej nie.
- **Próbkowanie ważności niezgodne z zasadami.** Wagi `π(a|s)/μ(a|s)` mnożą się w obrębie trajektorii. Wariancja eksploduje wraz z horyzontem. Ogranicz z IS ważonym według decyzji lub przejdź na TD.

## Użyj tego

Rola metod Monte Carlo w roku 2026:

| Przypadek użycia | Dlaczego MC |
|---------|--------|
| Gry krótkiego horyzontu (blackjack, poker) | Odcinki kończą się naturalnie; zwroty są czyste. |
| Ocena offline zarejestrowanej polityki | Średnie zdyskontowane zyski w oparciu o zapisane trajektorie. |
| Wyszukiwanie drzewa Monte Carlo (AlphaZero) | Wdrożenia MC z liści drzew prowadzą do wyboru. |
| Ocena LLM RL | Oblicz średnią nagrodę na podstawie próbnych ukończeń dla danej zasady. |
| Szacunek bazowy w PPO | Cel przewagi `A_t = G_t - V(s_t)` wykorzystuje MC `G_t`. |
| Nauczanie RL | Najprostszy algorytm, który faktycznie działa — strip bootstrap, aby zobaczyć rdzeń. |

Nowoczesne algorytmy deep-RL (PPO, SAC) interpolują pomiędzy czystym MC (pełne zwroty) i czystym TD (jednoetapowy bootstrap) poprzez zwroty z krokiem `n` lub GAE. Obydwa punkty końcowe są instancjami tego samego estymatora.

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

1. **Łatwe.** Wdrożenie oceny jednolitej losowości przez MC podczas pierwszej wizyty w sieci 4×4 GridWorld. Uruchom 10 000 odcinków. Wykreśl `V(0,0)` jako funkcję liczby odcinków względem odpowiedzi DP.
2. **Średni.** Zaimplementuj ε-chciwą kontrolę MC za pomocą `ε ∈ {0.01, 0.1, 0.3}`. Porównaj średni zwrot po 20 000 odcinków. Jak wygląda krzywa? Gdzie leży kompromis pomiędzy odchyleniami a wariancją?
3. **Trudne.** Zaimplementuj *off-policy* MC z próbkowaniem ważności: zbierz dane zgodnie z polityką uniform-random `μ`, oszacuj `V^π` dla deterministycznej optymalnej polityki `π`. Porównaj zwykły IS z IS na podstawie decyzji i ważonym IS. Który ma najmniejszą wariancję?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Monte Carlo | „Losowe pobieranie próbek” | Oszacuj oczekiwania, uśredniając próbki iid z rozkładu. |
| Zwróć `G_t` | „Przyszła nagroda” | Suma nagród ze zniżką od kroku `t` do końca odcinka: `Σ_{k≥0} γ^k r_{t+k+1}`. |
| Pierwsza wizyta MC | „Policz każdy stan raz” | Tylko pierwsza wizyta w odcinku uwzględniana jest w oszacowaniu wartości. |
| Każda wizyta MC | „Wykorzystaj wszystkie wizyty” | Każda wizyta wnosi wkład; nieco stronniczy, ale bardziej efektywny pod względem próbki. |
| ε-chciwy | „Hałas eksploracyjny” | Wybierz zachłanne działanie z prawdopodobieństwem `1-ε`; losowa akcja z prawdopodobieństwem `ε`. |
| Próbkowanie znaczenia | „Poprawianie próbkowania z niewłaściwej dystrybucji” | Ponownie zważ zwroty według produktów `π(a\|s)/μ(a\|s)`, aby oszacować `V^π` na podstawie danych `μ`. |
| Na zasadach | „Ucz się na własnych danych” | Polityka docelowa = polityka zachowania. Waniliowy MC, PPO, SARSA. |
| Niezgodne z zasadami | „Ucz się na cudzych danych” | Polityka docelowa ≠ polityka zachowania. MC z próbką ważności, Q-learning, DQN. |

## Dalsze czytanie

- [Sutton i Barto (2018). Ch. 5 — Metody Monte Carlo](http://incompleteideas.net/book/RLbook2020.pdf) — leczenie kanoniczne.
- [Singh i Sutton (1996). Uczenie się przez wzmacnianie poprzez zastępowanie śladów kwalifikowalności](https://link.springer.com/article/10.1007/BF00114726) — analiza pierwszej wizyty i każdej wizyty.
- [Precup, Sutton, Singh (2000). Ślady kwalifikowalności do oceny polityki poza polityką](http://incompleteideas.net/papers/PSS-00.pdf) — MC poza polityką i kontrola rozbieżności.
- [Mahmood i in. (2014). Ważone próbkowanie ważności do uczenia się poza polityką](https://arxiv.org/abs/1404.6362) — nowoczesne estymatory IS o niskiej wariancji.
- [Tesauro (1995). TD-Gammon, program samokształcenia w backgammona] (https://dl.acm.org/doi/10.1145/203330.203343) — pierwsza empiryczna demonstracja na dużą skalę gry samodzielnej MC/TD zbiegającej się z grą nadludzką; koncepcyjny prekursor każdej lekcji w drugiej połowie tej fazy.