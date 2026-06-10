# Aktor-krytyk — A2C i A3C

> REINFORCE jest głośny. Dodaj krytyka, który uczy się `V̂(s)`, odejmij tę wartość od zwrotu, a uzyskasz przewagę o tych samych oczekiwaniach, lecz znacznie mniejszej wariancji. Na tym polega metoda aktora-krytyka. A2C uruchamia ją synchronicznie, A3C — w wątkach. Obie stanowią fundament pojęciowy każdej nowoczesnej metody głębokiego RL.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 9 · 04 (Nauka TD), Faza 9 · 06 (WZMOCNIENIE)
**Czas:** ~75 minut

## Problem

Vanilla REINFORCE działa, ale jego zmienność jest bardzo wysoka. Zwroty Monte Carlo `G_t` mogą się różnić dziesięciokrotnie między epizodami. Pomnożenie tego szumu przez `∇ log π` i uśrednienie daje estymator gradientu, który potrzebuje tysięcy epizodów, aby przenieść politykę o odległość osiągalną przez DQN przy znacznie mniejszej liczbie aktualizacji.

Wariancja wynika z użycia surowych zwrotów. Jeśli odejmiemy linię bazową `b(s_t)` — dowolną funkcję stanu, w tym nauczoną wartość — wartość oczekiwana pozostaje niezmieniona, a wariancja maleje. Najlepszym dostępnym punktem odniesienia jest `V̂(s_t)`. Mnożnik `∇ log π` staje się wtedy *przewagą*:

`A(s, a) = G - V̂(s)`

Dane działanie jest dobre, jeśli przyniosło ponadprzeciętny zwrot; złe — jeśli poniżej przeciętnej. WZMOCNIENIE z nauczonym krytykiem to *aktor-krytyk*. Krytyk dostarcza aktorowi nauczyciela o niskiej wariancji. Ta idea leży u podstaw każdej metody głębokiej polityki po 2015 roku: A2C, A3C, PPO, SAC, IMPALA.

## Koncepcja

![Actor-critic: polityka netto plus wartość netto, pozostała część TD jako zaleta](../assets/actor-critic.svg)

**Dwie sieci, jedna łączna strata:**

- **Aktor** `π_θ(a | s)`: wyznacza politykę. Próbkuje działania. Trenowany gradientem polityki.
- **Krytyk** `V_φ(s)`: szacuje oczekiwany zwrot ze stanu. Trenowany przez minimalizację `(V_φ(s) - target)²`.

**Przewaga.** Dwie standardowe formy:

- *Przewaga MC:* `A_t = G_t - V_φ(s_t)`. Nieobciążona, lecz o większej wariancji.
- *Przewaga TD:* `A_t = r_{t+1} + γ V_φ(s_{t+1}) - V_φ(s_t)`. Obciążona (korzysta z `V_φ`), ale o znacznie mniejszej wariancji. Nazywana też *resztą TD* `δ_t`.

**Przewaga n-krokowa.** Interpolacja między powyższymi:

`A_t^{(n)} = r_{t+1} + γ r_{t+2} + … + γ^{n-1} r_{t+n} + γ^n V_φ(s_{t+n}) - V_φ(s_t)`

`n = 1` odpowiada czystemu TD. `n = ∞` odpowiada MC. Większość implementacji stosuje `n = 5` dla Atari i `n = 2048` dla PPO na MuJoCo.

**Uogólnione szacowanie przewagi (GAE).** Schulman i in. (2016) zaproponowali wykładniczo ważoną sumę wszystkich przewag n-krokowych:

`A_t^{GAE} = Σ_{l=0}^{∞} (γλ)^l δ_{t+l}`

gdzie `λ ∈ [0, 1]`. Przy `λ = 0` otrzymujemy TD (niska wariancja, duże obciążenie). Przy `λ = 1` — MC (wysoka wariancja, brak obciążenia). Wartość `λ = 0.95` to praktyczny standard na rok 2026 — dostosuj ją tak, by kompromis między obciążeniem a wariancją był optymalny dla danego zadania.

**A2C: synchroniczny aktor-krytyk z przewagą.** Zbierz `T` kroków w `N` równoległych środowiskach. Oblicz przewagi dla każdego kroku. Zaktualizuj aktora i krytyka na połączonej minipaczce. Powtarzaj. To prostsze i lepiej skalowalne rozwiązanie niż A3C.

**A3C: asynchroniczny aktor-krytyk z przewagą.** Mnih i in. (2016). Uruchom `N` wątków roboczych, z których każdy działa we własnym środowisku. Każdy wątek oblicza gradienty lokalnie podczas własnego wdrożenia, a następnie asynchronicznie przesyła je do wspólnego serwera parametrów. Bufor doświadczeń nie jest potrzebny — pracownicy dekorelują dane, przemierzając różne trajektorie. Projekt A3C udowodnił możliwość trenowania na procesorach CPU w dużej skali. W 2026 roku dominuje jednak A2C oparte na GPU (ze wsadowo równoległymi środowiskami), ponieważ procesory graficzne wymagają dużych paczek danych.

**Łączna strata.**

`L(θ, φ) = -E[ A_t · log π_θ(a_t | s_t) ]  +  c_v · E[(V_φ(s_t) - G_t)²]  -  c_e · E[H(π_θ(·|s_t))]`

Trzy składniki: strata gradientu polityki, regresja wartości oraz premia za entropię. Wartości `c_v ~ 0.5` i `c_e ~ 0.01` to kanoniczne punkty startowe.

## Zbuduj to

### Krok 1: krytyk

Liniowy krytyk `V_φ(s) = w · features(s)` aktualizowany przez MSE:

```python
def critic_update(w, x, target, lr):
    v_hat = dot(w, x)
    err = target - v_hat
    for j in range(len(w)):
        w[j] += lr * err * x[j]
    return v_hat
```

W wersji tablicowej krytyk zbiega się po kilkuset epizodach. Dla Atari zastąp liniowego krytyka wspólnym łączem CNN z osobną głową wartości.

### Krok 2: przewaga n-krokowa

Dla wdrożenia o długości `T` i bootstrapowanej wartości końcowej `V(s_T)`:

```python
def compute_advantages(rewards, values, gamma=0.99, lam=0.95, last_value=0.0):
    advantages = [0.0] * len(rewards)
    gae = 0.0
    for t in reversed(range(len(rewards))):
        next_v = values[t + 1] if t + 1 < len(values) else last_value
        delta = rewards[t] + gamma * next_v - values[t]
        gae = delta + gamma * lam * gae
        advantages[t] = gae
    returns = [a + v for a, v in zip(advantages, values)]
    return advantages, returns
```

`returns` stanowi cel dla krytyka. `advantages` to mnożnik `∇ log π`.

### Krok 3: połączona aktualizacja

```python
for step_i, (x, a, _r, probs) in enumerate(traj):
    adv = advantages[step_i]
    target_v = returns[step_i]

    # critic
    critic_update(w, x, target_v, lr_v)

    # actor
    for i in range(N_ACTIONS):
        grad_logpi = (1.0 if i == a else 0.0) - probs[i]
        for j in range(N_FEAT):
            theta[i][j] += lr_a * adv * grad_logpi * x[j]
```

Zgodnie z założeniami metody: jedno wdrożenie na aktualizację, oddzielne współczynniki uczenia dla aktora i krytyka.

### Krok 4: równoległość (A3C vs A2C)

- **A3C:** uruchom `N` wątków. Każdy ma własne środowisko i własne przejście w przód. Gradienty są okresowo przesyłane do wspólnego modelu głównego. Wyścig wątków jest dopuszczalny — wprowadza jedynie dodatkowy szum.
- **A2C:** uruchom `N` instancji środowiska w jednym procesie, ułóż obserwacje w paczkę `[N, obs_dim]`, wykonaj wsadowy przebieg w przód i wstecz. Lepsze wykorzystanie GPU, deterministyczny przebieg, łatwiejszy w analizie. Domyślne podejście w 2026 roku.

Nasz kod demonstracyjny jest jednowątkowy dla przejrzystości; przepisanie na wsadowe A2C wymaga trzech linii numpy.

## Pułapki

- **Nienauczony krytyk przed gradienten aktora.** Jeśli krytyk jest losowy, jego punkt odniesienia jest bezużyteczny i trening odbywa się na czystym szumie. Rozgrzej krytyka przez kilkaset kroków przed włączeniem gradientu polityki lub zastosuj niski współczynnik uczenia aktora.
- **Normalizacja przewagi.** Normalizuj przewagi do zerowej średniej i jednostkowego odchylenia standardowego na każdą paczkę. Stabilizuje trening przy minimalnym koszcie obliczeniowym.
- **Wspólny kręgosłup.** Przy wejściach obrazowych stosuj wspólny ekstraktor cech dla aktora i krytyka, z osobnymi głowami. Dzielone cechy korzystają jednocześnie z obu strat.
- **Ograniczenie on-policy.** A2C ponownie wykorzystuje dane podczas dokładnie jednej aktualizacji. Więcej przejść daje obciążony gradient — korekcja przez ważenie ważnością próbkowania to właśnie to, co PPO dodaje do A2C.
- **Zanik entropii.** Bez `c_e > 0` polityka staje się niemal deterministyczna po kilkuset aktualizacjach i przestaje eksplorować.
- **Skala nagród.** Wielkość przewagi zależy od skali nagród. Normalizuj nagrody (np. dzieląc przez odchylenie standardowe z aktualnego wdrożenia), aby uzyskać spójne wielkości gradientu w różnych zadaniach.

## Zastosowania

A2C i A3C rzadko są ostatecznym wyborem w 2026 roku, stanowią jednak architekturę, którą rozwijają nowsze metody:

| Metoda | Związek z A2C |
|------------|----------------|
| PPO | A2C + obcięty współczynnik ważności dla aktualizacji wieloepokowych |
| IMPALA | A3C z korekcją niezgodności polityki + V-trace |
| SAC (faza 9 · 07) | A2C off-policy z krytykiem miękkiej wartości (następna lekcja) |
| GRPO (faza 9 · 12) | A2C bez krytyka — przewaga względna w grupie |
| IOD | A2C osadzone w stracie rankingu preferencji, bez próbkowania |
| AlphaStar / OpenAI Five | A2C z treningiem ligowym i wstępnym uczeniem przez imitację |

Gdy w artykule z 2026 roku pojawia się słowo „przewaga", myśl: aktor-krytyk.

## Wyślij to

Zapisz jako `outputs/skill-actor-critic-trainer.md`:

```markdown
---
name: actor-critic-trainer
description: Produce an A2C / A3C / GAE configuration for a given environment, with advantage estimation and loss weights specified.
version: 1.0.0
phase: 9
lesson: 7
tags: [rl, actor-critic, gae]
---

Given an environment and compute budget, output:

1. Parallelism. A2C (GPU batched) vs A3C (CPU async) and the number of workers.
2. Rollout length T. Steps per env per update.
3. Advantage estimator. n-step or GAE(λ); specify λ.
4. Loss weights. `c_v` (value), `c_e` (entropy), gradient clip.
5. Learning rates. Actor and critic (separate if using).

Refuse single-worker A2C on environments with horizon > 1000 (too on-policy, too slow). Refuse to ship without advantage normalization. Flag any run with `c_e = 0` and observed entropy < 0.1 as entropy-collapsed.
```

## Ćwiczenia

1. **Łatwe.** Wytrenuj aktor-krytyka z przewagą MC (`G_t - V(s_t)`) na siatce 4×4 GridWorld. Porównaj efektywność próbkowania z WZMOCNIENIEM ze średnią kroczącą z lekcji 06.
2. **Średnie.** Przełącz na przewagę reszty TD (`r + γ V(s') - V(s)`). Zmierz wariancję paczki przewag. O ile maleje?
3. **Trudne.** Zaimplementuj GAE(λ). Przeszukaj `λ ∈ {0, 0.5, 0.9, 0.95, 1.0}`. Wykreśl końcowy zwrot w funkcji liczby próbek. Gdzie leży optymalny punkt kompromisu obciążenie/wariancja dla tego zadania?

## Kluczowe terminy

| Termin | Co się mówi | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Aktor | „Sieć polityki" | `π_θ(a\|s)`, aktualizowana gradientem polityki. |
| Krytyk | „Sieć wartości" | `V_φ(s)`, aktualizowana przez regresję MSE do zwrotów lub celów TD. |
| Przewaga | „O ile lepiej niż przeciętnie" | `A(s, a) = Q(s, a) - V(s)` lub jej estymatory. Mnożnik dla `∇ log π`. |
| Reszta TD | „δ" | `δ_t = r + γ V(s') - V(s)`; jednoetapowy estymator przewagi. |
| GAE | „Pokrętło interpolacyjne" | Wykładniczo ważona suma przewag n-krokowych, sparametryzowana przez `λ`. |
| A2C | „Synchroniczny aktor-krytyk" | Środowiska pogrupowane w paczkę; jeden krok gradientu na wdrożenie. |
| A3C | „Asynchroniczny aktor-krytyk" | Wątki robocze przesyłają gradienty do wspólnego serwera parametrów. Oryginalna praca; rzadziej stosowany w 2026 r. |
| Bootstrap | „Użyj V na horyzoncie" | Skróć wdrożenie i dodaj `γ^n V(s_{t+n})`, aby zamknąć sumę nagród. |

## Dalsze czytanie

- [Mnih i in. (2016). Asynchronous Methods for Deep Reinforcement Learning](https://arxiv.org/abs/1602.01783) — A3C, oryginalna praca o asynchronicznym aktorze-krytyku.
- [Schulman i in. (2016). Wysokowymiarowa ciągła kontrola z uogólnionym szacowaniem przewagi](https://arxiv.org/abs/1506.02438) — GAE.
- [Sutton i Barto (2018). Ch. 13 — Metody aktora-krytyka](http://incompleteideas.net/book/RLbook2020.pdf) — podstawy teoretyczne; warto połączyć z Ch. 9 o aproksymacji funkcji, gdy krytykiem jest sieć neuronowa.
- [Espeholt i in. (2018). IMPALA](https://arxiv.org/abs/1802.01561) — skalowalny rozproszony aktor-krytyk z korekcją niezgodności polityki V-trace.
- [OpenAI Baselines / Stable-Baselines3](https://stable-baselines3.readthedocs.io/) — produkcyjne implementacje A2C/PPO warte przestudiowania.
- [Konda i Tsitsiklis (2000). Algorytmy aktora-krytyka](https://papers.nips.cc/paper/1786-actor-critic-algorithms) — podstawowy wynik zbieżności dla aktora-krytyka w dwóch skalach czasowych.
