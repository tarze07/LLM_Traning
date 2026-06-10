# Gradient polityki — REINFORCE od podstaw

> Przestań szacować wartości. Sparametryzuj politykę bezpośrednio, oblicz gradient oczekiwanego zwrotu i ruszaj w górę. Williams (1992) ujął to w jednym twierdzeniu. Stąd właśnie wywodzą się PPO, GRPO i każda pętla RL dla modeli językowych.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 3 · 03 (propagacja wsteczna), Faza 9 · 03 (Monte Carlo), Faza 9 · 04 (uczenie się TD)
**Czas:** ~75 minut

## Problem

Q-learning i DQN parametryzują funkcję *wartości*. Akcje wybiera się przez `argmax Q`. Podejście to sprawdza się w przypadku dyskretnych akcji i dyskretnych stanów, lecz zawodzi, gdy akcje są ciągłe (jak zastosować `argmax` do 10-wymiarowego momentu obrotowego?) lub gdy wymagana jest polityka stochastyczna (`argmax` jest z założenia deterministyczne).

Gradienty polityki podchodzą do problemu inaczej — parametryzują bezpośrednio *politykę*. `π_θ(a | s)` to sieć neuronowa generująca rozkład prawdopodobieństwa po akcjach. Próbkujemy z tego rozkładu, by wybrać akcję, a następnie obliczamy gradient oczekiwanego zwrotu względem `θ` i wykonujemy krok w górę. Żadnego `argmax`, żadnej rekurencji Bellmana — wystarczy ascent gradientowy na `J(θ) = E_{π_θ}[G]`.

Twierdzenie REINFORCE (Williams 1992) stwierdza, że ów gradient jest obliczalny: `∇J(θ) = E_π[ G · ∇_θ log π_θ(a | s) ]`. Uruchamiamy epizod, obliczamy zwrot i na każdym kroku mnożymy go przez `∇ log π_θ(a | s)`, uśredniamy wynik, a następnie wykonujemy krok gradientowy. I tyle.

Każdy algorytm RL dla modeli językowych w 2026 r. — PPO, DPO, GRPO — jest udoskonaleniem REINFORCE. Solidne zrozumienie tej metody jest warunkiem koniecznym do opanowania dalszej części tej fazy oraz lekcji 10 · 07 (implementacja RLHF) i 10 · 08 (DPO).

## Koncepcja

![Gradient polityki: polityka softmax, gradient log-π, aktualizacja ważona zwrotem](../assets/policy-gradient.svg)

**Twierdzenie o gradiencie polityki.** Dla dowolnej polityki `π_θ` sparametryzowanej przez `θ`:

`∇J(θ) = E_{τ ~ π_θ}[ Σ_{t=0}^{T} G_t · ∇_θ log π_θ(a_t | s_t) ]`

gdzie `G_t = Σ_{k=t}^{T} γ^{k-t} r_{k+1}` to zdyskontowany zwrot z kroku `t`. Wartość oczekiwana jest liczona po pełnych trajektoriach `τ` próbkowanych z `π_θ`.

**Dowód jest krótki.** Różniczkujemy `J(θ) = Σ_τ P(τ; θ) G(τ)` po `θ`. Korzystamy ze wzoru `∇P(τ; θ) = P(τ; θ) ∇ log P(τ; θ)` (tak zwana sztuczka pochodnej logarytmicznej). Logarytm rozkładu trajektorii wynosi `log P(τ; θ) = Σ log π_θ(a_t | s_t) + składniki środowiskowe niezależne od θ`. Składniki środowiskowe znikają, a dwie linijki algebry dają gotowe twierdzenie.

**Techniki redukcji wariancji.** Waniliowe REINFORCE cechuje bardzo duża wariancja — zwroty są zaszumione, `∇ log π` jest zaszumione, a ich iloczyn jeszcze bardziej. Dwie standardowe poprawki:

1. **Odejmowanie wartości bazowej.** Zastępujemy `G_t` wyrażeniem `G_t - b(s_t)` dla dowolnej wartości bazowej `b(s_t)` niezależnej od `a_t`. Estymator pozostaje nieobciążony, ponieważ `E[b(s_t) · ∇ log π(a_t | s_t)] = 0`. Typowy wybór: `b(s_t) = V̂(s_t)` uczone przez krytyka → metoda aktor-krytyk (lekcja 07).
2. **Nagroda do przodu.** Zastępujemy `Σ_t G_t · ∇ log π_θ(a_t | s_t)` przez `Σ_t G_t^{from t} · ∇ log π_θ(a_t | s_t)`. Dla danej akcji liczy się wyłącznie przyszły zysk — nagrody z przeszłości wnoszą jedynie szum.

Łącznie otrzymujemy:

`∇J ≈ (1/N) Σ_{i=1}^{N} Σ_{t=0}^{T_i} [ G_t^{(i)} - V̂(s_t^{(i)}) ] · ∇_θ log π_θ(a_t^{(i)} | s_t^{(i)})`

czyli REINFORCE z linią bazową — bezpośredni przodek A2C (lekcja 07) i PPO (lekcja 08).

**Parametryzacja polityki Softmax.** W przypadku akcji dyskretnych standardowy wybór to:

`π_θ(a | s) = exp(f_θ(s, a)) / Σ_{a'} exp(f_θ(s, a'))`

gdzie `f_θ` to dowolna sieć neuronowa przypisująca wynik każdej akcji. Gradient ma zwartą postać:

`∇_θ log π_θ(a | s) = ∇_θ f_θ(s, a) - Σ_{a'} π_θ(a' | s) ∇_θ f_θ(s, a')`

czyli: wynik podjętej akcji minus jego wartość oczekiwana względem bieżącej polityki.

**Polityka Gaussa dla akcji ciągłych.** `π_θ(a | s) = N(μ_θ(s), σ_θ(s))`. Gradient `∇ log N(a; μ, σ)` ma postać zamkniętą. To wszystko, czego potrzebuje SAC w lekcji 9 · 07.

## Zbuduj to

### Krok 1: sieć zasad softmax

```python
def policy_logits(theta, state_features):
    return [dot(theta[a], state_features) for a in range(N_ACTIONS)]

def softmax(logits):
    m = max(logits)
    exps = [exp(l - m) for l in logits]
    Z = sum(exps)
    return [e / Z for e in exps]
```

Użyj liniowej polityki (jeden wektor wag na akcję) dla środowiska tabelarycznego. W przypadku Atari wystarczy podmienić rdzeń na CNN, zachowując głowicę softmax.

### Krok 2: próbkowanie i logarytm prawdopodobieństwa

```python
def sample_action(probs, rng):
    x = rng.random()
    cum = 0
    for a, p in enumerate(probs):
        cum += p
        if x <= cum:
            return a
    return len(probs) - 1

def log_prob(probs, a):
    return log(probs[a] + 1e-12)
```

### Krok 3: zebranie trajektorii z zapisanymi log-prawdopodobieństwami

```python
def rollout(theta, env, rng, gamma):
    trajectory = []
    s = env.reset()
    while not done:
        logits = policy_logits(theta, s)
        probs = softmax(logits)
        a = sample_action(probs, rng)
        s_next, r, done = env.step(s, a)
        trajectory.append((s, a, r, probs))
        s = s_next
    return trajectory
```

### Krok 4: aktualizacja REINFORCE

```python
def reinforce_step(theta, trajectory, gamma, lr, baseline=0.0):
    returns = compute_returns(trajectory, gamma)
    for (s, a, _, probs), G in zip(trajectory, returns):
        advantage = G - baseline
        grad_log_pi_a = [-p for p in probs]
        grad_log_pi_a[a] += 1.0
        for i in range(N_ACTIONS):
            for j in range(len(s)):
                theta[i][j] += lr * advantage * grad_log_pi_a[i] * s[j]
```

Wzór `∇ log π(a|s) = e_a - π(·|s)` (wektor jednostkowy dla akcji `a` minus wektor prawdopodobieństw) stanowi serce gradientów polityki softmax. Warto go zapamiętać.

### Krok 5: wartości bazowe

Krocząca średnia zwrotów `G` z ostatnich epizodów wystarczy do skutecznej redukcji wariancji w środowisku GridWorld 4×4; zbieżność następuje po około 500 epizodach. Po podmianie linii bazowej na wyuczone `V̂(s)` uzyskujemy metodę aktor-krytyk.

## Pułapki

- **Eksplodujące gradienty.** Zwroty bywają bardzo duże. Przed pomnożeniem przez `∇ log π` zawsze normalizuj `G` do rozkładu `~N(0, 1)` w całej paczce danych.
- **Kolaps entropii.** Polityka zbyt wcześnie zbliża się do zachowania niemal deterministycznego, traci zdolność eksploracji i utyka w lokalnym optimum. Rozwiązanie: dodaj premię entropijną `β · H(π(·|s))` do funkcji celu.
- **Duża wariancja.** Waniliowe REINFORCE wymaga tysięcy epizodów. Standardowym lekiem jest nauczenie się krytyka dostarczającego linię bazową (lekcja 07) lub zastosowanie metod z obszarem zaufania — TRPO lub PPO (lekcja 08).
- **Niska efektywność próbkowania.** Uczenie zgodne z polityką (on-policy) oznacza, że po każdej aktualizacji odrzucamy wszystkie zebrane przejścia. Metody niezgodne z polityką (off-policy) ratują dane kosztem wzrostu wariancji dzięki próbkowaniu ważonemu — obcięty współczynnik wagowy IS to właśnie mechanizm PPO.
- **Niestacjonarne gradienty.** Gradient obliczony 100 epizodów temu opisuje starą politykę `π`. Właśnie dlatego metody on-policy aktualizują parametry co kilka wdrożeń.
- **Przypisanie zasług.** Bez nagrody do przodu wcześniejsze nagrody wprowadzają szum do gradientu. Zawsze stosuj nagrodę do przodu (reward-to-go).

## Zastosowania

W 2026 r. REINFORCE rzadko jest stosowany bezpośrednio, lecz jego formuła gradientowa pojawia się wszędzie:

| Przypadek użycia | Metoda pochodna |
|---------|--------------|
| Ciągła kontrola | PPO/SAC z polityką Gaussa |
| LLM RLHF | PPO z karą KL działający na poziomie tokenów |
| Rozumowanie LLM (DeepSeek) | GRPO — REINFORCE na poziomie grupy, bez krytyka |
| Wielu agentów | Scentralizowany krytyk z REINFORCE (MADDPG, COMA) |
| Robotyka z dyskretnymi akcjami | A2C, A3C, PPO |
| Uczenie tylko z preferencji | DPO — REINFORCE przepisany jako strata prawdopodobieństwa preferencji, bez próbkowania |

Kiedy w skrypcie treningowym z 2026 r. widzisz `loss = -advantage * log_prob`, to jest właśnie REINFORCE z linią bazową. Całe artykuły (DPO, GRPO, RLOO) to techniki redukcji wariancji nadbudowane na tej jednej linijce.

## Wyślij to

Zapisz jako `outputs/skill-policy-gradient-trainer.md`:

```markdown
---
name: policy-gradient-trainer
description: Produce a REINFORCE / actor-critic / PPO training config for a given task and diagnose variance issues.
version: 1.0.0
phase: 9
lesson: 6
tags: [rl, policy-gradient, reinforce]
---

Given an environment (discrete / continuous actions, horizon, reward stats), output:

1. Policy head. Softmax (discrete) or Gaussian (continuous) with parameter counts.
2. Baseline. None (vanilla), running mean, learned `V̂(s)`, or A2C critic.
3. Variance controls. Reward-to-go on by default, return normalization, gradient clip value.
4. Entropy bonus. Coefficient β and decay schedule.
5. Batch size. Episodes per update; on-policy data freshness contract.

Refuse REINFORCE-no-baseline on horizons > 500 steps. Refuse continuous-action control with a softmax head. Flag any run with `β = 0` and observed policy entropy < 0.1 as entropy-collapsed.
```

## Ćwiczenia

1. **Łatwe.** Zaimplementuj REINFORCE w środowisku GridWorld 4×4 z liniową polityką softmax. Trenuj przez 1000 epizodów bez linii bazowej. Wykreśl krzywą uczenia się i zmierz wariancję (odchylenie standardowe zwrotów).
2. **Średnie.** Dodaj krocząca średnią jako linię bazową i wytrenuj model od nowa. Porównaj wyniki i wariancję z poprzednim przebiegiem. O ile szybciej następuje zbieżność?
3. **Trudne.** Dodaj premię entropijną `β · H(π)`. Przeszukaj siatkę wartości `β ∈ {0, 0.01, 0.1, 1.0}`. Wykreśl końcowy zwrot i entropię polityki. Gdzie leży punkt optymalny dla tego zadania?

## Kluczowe terminy

| Termin | Co się mówi | Co to faktycznie oznacza |
|------|-----------------|----------------------|
| Gradient polityki | „Bezpośrednie uczenie polityki" | `∇J(θ) = E[G · ∇ log π_θ(a\|s)]`; wynika ze sztuczki pochodnej logarytmicznej. |
| REINFORCE | „Oryginalny algorytm PG" | Williams (1992); zwroty Monte Carlo pomnożone przez gradient log-polityki. |
| Sztuczka log-pochodnej | „Estymator funkcji wyniku" | `∇P(τ;θ) = P(τ;θ) · ∇ log P(τ;θ)`; pozwala obliczać gradienty wartości oczekiwanych. |
| Linia bazowa | „Redukcja wariancji" | Dowolne `b(s)` odjęte od `G`; estymator pozostaje nieobciążony, bo `E[b · ∇ log π] = 0`. |
| Nagroda do przodu | „Liczą się tylko przyszłe zyski" | `G_t^{from t}` zamiast pełnego `G_0`; poprawne i o mniejszej wariancji. |
| Premia entropijna | „Zachęcaj do eksploracji" | Składnik `+β · H(π(·\|s))` zapobiega kolapsowi polityki. |
| On-policy | „Trenuj na danych z bieżącej polityki" | Gradient jest wartością oczekiwaną względem aktualnej polityki — starych danych nie można bezpośrednio ponownie użyć. |
| Przewaga | „O ile lepiej niż przeciętnie" | `A(s, a) = G(s, a) - V(s)`; wartość ze znakiem, przez którą REINFORCE z linią bazową mnoży gradient. |

## Dalsze czytanie

- [Williams (1992). Proste statystyczne algorytmy gradientowe do uczenia ze wzmocnieniem w sieciach koneksjonistycznych](https://link.springer.com/article/10.1007/BF00992696) — oryginalny artykuł REINFORCE.
- [Sutton i in. (2000). Metody gradientu polityki do uczenia ze wzmocnieniem z aproksymacją funkcji](https://papers.nips.cc/paper_files/paper/1999/hash/464d828b85b0bed98e80ade0a5c43b0f-Abstract.html) — nowoczesne twierdzenie o gradiencie polityki z aproksymacją funkcji.
- [Sutton i Barto (2018). Rozdział 13 — Metody gradientu polityki](http://incompleteideas.net/book/RLbook2020.pdf) — prezentacja podręcznikowa.
- [OpenAI Spinning Up — VPG / REINFORCE](https://spinningup.openai.com/en/latest/algorithms/vpg.html) — przejrzyste wprowadzenie pedagogiczne z kodem PyTorch.
- [Peters i Schaal (2008). Uczenie umiejętności motorycznych przez wzmacnianie z użyciem gradientów polityki](https://homes.cs.washington.edu/~todorov/courses/amath579/reading/PolicyGradient.pdf) — redukcja wariancji i perspektywa naturalnego gradientu łącząca REINFORCE z metodami obszaru zaufania (TRPO, PPO).
