# Gradient polityki — WZMACNIAJ od podstaw

> Przestań oceniać wartość. Sparametryzuj politykę bezpośrednio, oblicz gradient oczekiwanego zwrotu, idź w górę. Williams (1992) zapisał to w jednym twierdzeniu. Dlatego istnieją PPO, GRPO i każda pętla LLM RL.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 3 · 03 (propagacja wsteczna), Faza 9 · 03 (Monte Carlo), Faza 9 · 04 (uczenie się TD)
**Czas:** ~75 minut

## Problem

Q-learning i DQN parametryzują funkcję *wartość*. Akcje wybierasz do `argmax Q`. Jest to w porządku w przypadku dyskretnych działań i dyskretnych stanów. Psuje się, gdy działania są ciągłe (co `argmax` w 10-wymiarowym momencie obrotowym?) lub gdy wymagana jest polityka stochastyczna (`argmax` jest z założenia deterministyczne).

Zamiast tego gradienty zasad parametryzują *politykę*. `π_θ(a | s)` to sieć neuronowa, która generuje rozkład według działań. Próbka z tego, aby działać. Oblicz gradient oczekiwanego zwrotu w odniesieniu do `θ`. Krok pod górę. Nie `argmax`. Brak rekurencji Bellmana. Wystarczy gradientowe podejście na `J(θ) = E_{π_θ}[G]`.

Twierdzenie WZMOCNIJ (Williams 1992) mówi, że ten gradient jest obliczalny: `∇J(θ) = E_π[ G · ∇_θ log π_θ(a | s) ]`. Uruchom odcinek. Oblicz zwrot. Na każdym kroku mnożysz przez `∇ log π_θ(a | s)`. Przeciętny. Wspinaczka gradientowa. Zrobione.

Każdy algorytm LLM-RL w 2026 r. — PPO, DPO, GRPO — jest udoskonaleniem REINFORCE. Zrozumienie tego na wyciągnięcie ręki jest warunkiem wstępnym dalszej części tej fazy oraz fazy 10 · 07 (wdrożenie RLHF) i fazy 10 · 08 (DPO).

## Koncepcja

![Gradient polityki: polityka softmax, gradient log-π, aktualizacja ważona zwrotem](../assets/policy-gradient.svg)

**Twierdzenie o gradiencie polityki.** Dla dowolnej polityki `π_θ` sparametryzowanej przez `θ`:

`∇J(θ) = E_{τ ~ π_θ}[ Σ_{t=0}^{T} G_t · ∇_θ log π_θ(a_t | s_t) ]`

gdzie `G_t = Σ_{k=t}^{T} γ^{k-t} r_{k+1}` to zdyskontowany zwrot z kroku `t`. Oczekiwania obejmują pełne trajektorie `τ` pobrane z `π_θ`.

**Dowód jest krótki.** Odróżnij `J(θ) = Σ_τ P(τ; θ) G(τ)` od oczekiwanej. Użyj `∇P(τ; θ) = P(τ; θ) ∇ log P(τ; θ)` (sztuczki polegającej na pochodnej logu). Współczynnik `log P(τ; θ) = Σ log π_θ(a_t | s_t) + environment terms that do not depend on θ`. Terminy dotyczące środowiska znikają. Dwie linie algebry dają twierdzenie.

**Sztuczki redukcji wariancji.** Vanilla REINFORCE ma morderczą wariancję — zwroty są hałaśliwe, `∇ log π` jest hałaśliwe, a ich produkt jest bardzo hałaśliwy. Dwie standardowe poprawki:

1. **Odejmowanie wartości bazowej.** Zamień `G_t` na `G_t - b(s_t)` dla dowolnej wartości bazowej `b(s_t)`, która nie zależy od `a_t`. Bezstronny, ponieważ `E[b(s_t) · ∇ log π(a_t | s_t)] = 0`. Typowy wybór: `b(s_t) = V̂(s_t)` poznany przez krytyka → aktora-krytyka (lekcja 07).
2. **Nagroda do wykorzystania.** Zamień `Σ_t G_t · ∇ log π_θ(a_t | s_t)` na `Σ_t G_t^{from t} · ∇ log π_θ(a_t | s_t)`. Dla danego działania liczą się tylko przyszłe zyski — przeszłe nagrody przyczyniają się do zerowego szumu.

Łącznie otrzymujesz:

`∇J ≈ (1/N) Σ_{i=1}^{N} Σ_{t=0}^{T_i} [ G_t^{(i)} - V̂(s_t^{(i)}) ] · ∇_θ log π_θ(a_t^{(i)} | s_t^{(i)})`

czyli WZMOCNIJ o linię bazową — bezpośredniego przodka A2C (lekcja 07) i PPO (lekcja 08).

**Parametryzacja polityki Softmax.** W przypadku działań dyskretnych, standardowy wybór:

`π_θ(a | s) = exp(f_θ(s, a)) / Σ_{a'} exp(f_θ(s, a'))`

gdzie `f_θ` to dowolna sieć neuronowa, która generuje wynik za każde działanie. Gradient ma czystą formę:

`∇_θ log π_θ(a | s) = ∇_θ f_θ(s, a) - Σ_{a'} π_θ(a' | s) ∇_θ f_θ(s, a')`

tj. wynik podjętego działania minus jego wartość oczekiwana w ramach polisy.

**Polityka Gaussa dla działań ciągłych.** `π_θ(a | s) = N(μ_θ(s), σ_θ(s))`. `∇ log N(a; μ, σ)` ma formę zamkniętą. To wszystko, czego potrzebuje SAC w fazie 9 · 07.

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

Użyj polityki liniowej (jeden wektor wagi na akcję) dla środowiska tabelarycznego. W przypadku Atari zamień CNN i zachowaj głowicę softmax.

### Krok 2: pobieranie próbek i logarytm prawdopodobieństwa

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

### Krok 3: wdrożenie z przechwyconymi logami probierczymi

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

### Krok 4: WZMOCNIJ aktualizację

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

Gradient `∇ log π(a|s) = e_a - π(·|s)` (jeden gorący z `a` minus prawdopodobieństwa) jest sercem gradientów zasad Softmax. Wypal to w pamięci mięśniowej.

### Krok 5: wartości bazowe

Średnia krocząca `G` z ostatnich odcinków jest wystarczającą redukcją wariancji, aby uruchomić GridWorld 4×4; zbieżność zajmuje około 500 odcinków. Uaktualnij linię bazową do wyuczonego `V̂(s)`, a zyskasz krytykę aktora.

## Pułapki

- **Wybuchające gradienty.** Zyski mogą być ogromne. Zawsze normalizuj `G` do `~N(0, 1)` w całej partii przed pomnożeniem przez `∇ log π`.
- **Załamanie entropii.** Polityka zbyt wcześnie zbliża się do działania niemal deterministycznego, przestaje eksplorować, utknie. Poprawka: dodaj premię za entropię `β · H(π(·|s))` do celu.
- **Wysoka wariancja.** Waniliowe REINFORCE wymaga tysięcy odcinków. Krytyczna linia bazowa (lekcja 07) lub region zaufania TRPO/PPO (lekcja 08) to standardowe rozwiązanie.
- **Przykładowa nieefektywność.** Zgodność z zasadami oznacza, że ​​po jednej aktualizacji odrzucasz każde przejście. Korekty niezgodne z zasadami poprzez próbkowanie ważności przywracają dane kosztem wariancji (stosunek PPO to obcięta waga IS).
- **Niestacjonarne gradienty.** Ten sam gradient sprzed 100 odcinków wykorzystuje stary `π`. Z tego powodu metody zgodne z zasadami aktualizują się co kilka wdrożeń.
- **Przypisanie punktów.** Bez nagrody na później wcześniejsze nagrody powodują hałas. Zawsze korzystaj z nagrody na wynos.

## Użyj tego

W 2026 r. REINFORCE rzadko jest uruchamiany bezpośrednio, ale jego formuła gradientowa jest wszędzie:

| Przypadek użycia | Metoda pochodna |
|---------|--------------|
| Ciągła kontrola | PPO/SAC z polityką Gaussa |
| LLM RLHF | PPO z karą KL, działające na zasadach na poziomie tokena |
| Rozumowanie LLM (DeepSeek) | GRPO — WZMOCNIJ na poziomie podstawowym względem grupy, bez krytyki |
| Wielu agentów | Scentralizowane krytyczne WZMOCNIENIE (MADDPG, COMA) |
| Robotyka o działaniu dyskretnym | A2C, A3C, PPO |
| Ustawienia wyłącznie preferencyjne | DPO – WZMOCNIENIE przepisane jako utrata prawdopodobieństwa preferencji, brak pobierania próbek |

Kiedy czytasz `loss = -advantage * log_prob` w skrypcie szkoleniowym na 2026 rok, oznacza to WZMOCNIENIE o linię bazową. Całe dokumenty (DPO, GRPO, RLOO) to sztuczki zmniejszające wariancję na górze tej jednej linijki.

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

1. **Łatwe.** Wdróż REINFORCE w 4×4 GridWorld z liniową polityką softmax. Trenuj przez 1000 odcinków bez planu bazowego. Wykreśl krzywą uczenia się; miara wariancji (std zwrotów).
2. **Średni.** Dodaj średnią kroczącą linię bazową. Pociąg ponownie. Porównaj wydajność i wariancję próbki z przebiegiem waniliowym. O ile wartość bazowa zmniejsza liczbę kroków prowadzących do konwergencji?
3. **Trudne.** Dodaj premię za entropię `β · H(π)`. Przeszukaj `β ∈ {0, 0.01, 0.1, 1.0}`. Wykreśl ostateczny zwrot i entropię polityki. Gdzie jest słaby punkt w tym zadaniu?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Gradient polityki | „Bezpośrednie szkolenie w zakresie polityki” | `∇J(θ) = E[G · ∇ log π_θ(a\|s)]`; wywodzi się ze sztuczki z pochodną logarytmiczną. |
| WZMOCNIJ | „Oryginalny algorytm PG” | Williamsa (1992); Zwroty Monte Carlo pomnożone przez gradient zasad logu. |
| Sztuczka log-pochodna | „Estymator funkcji wyniku” | `∇P(τ;θ) = P(τ;θ) · ∇ log P(τ;θ)`; sprawia, że ​​gradienty oczekiwań są akceptowalne. |
| Linia bazowa | „Redukcja wariancji” | Dowolne `b(s)` odjęte od `G`; bezstronny, ponieważ `E[b · ∇ log π] = 0`. |
| Nagroda na wynos | „Liczą się tylko przyszłe zyski” | `G_t^{from t}` zamiast pełnego `G_0`; prawidłowe i o mniejszej wariancji. |
| Premia za entropię | „Zachęcaj do eksploracji” | `+β · H(π(·\|s))` termin zapobiega upadkowi zasad. |
| Na zasadach | „Trenuj na podstawie tego, co właśnie zobaczyłeś” | Oczekiwanie gradientu jest w.r.t. bieżąca polityka — nie można bezpośrednio ponownie wykorzystywać starych danych. |
| Zaleta | „O ile lepiej niż przeciętnie” | `A(s, a) = G(s, a) - V(s)`; podpisana ilość WZMOCNIJ z linią bazową mnoży się. |

## Dalsze czytanie

- [Williams (1992). Proste statystyczne algorytmy podążania za gradientem do uczenia się ze wzmocnieniem koneksjonistycznym](https://link.springer.com/article/10.1007/BF00992696) — oryginalny artykuł REINFORCE.
- [Sutton i in. (2000). Metody gradientu polityki do uczenia się ze wzmocnieniem z aproksymacją funkcji](https://papers.nips.cc/paper_files/paper/1999/hash/464d828b85b0bed98e80ade0a5c43b0f-Abstract.html) — nowoczesne twierdzenie o gradiencie polityki z aproksymacją funkcji.
- [Sutton i Barto (2018). Ch. 13 — Metody gradientu polityki](http://incompleteideas.net/book/RLbook2020.pdf) — prezentacja podręcznika.
- [OpenAI Spinning Up — VPG / REINFORCE](https://spinningup.openai.com/en/latest/algorithms/vpg.html) — przejrzysta ekspozycja pedagogiczna z kodem PyTorch.
- [Peters i Schaal (2008). Uczenie się umiejętności motorycznych przez wzmacnianie za pomocą gradientów polityki](https://homes.cs.washington.edu/~todorov/courses/amath579/reading/PolicyGradient.pdf) — redukcja wariancji i widok naturalnego gradientu, który łączy REINFORCE z rodziną regionów zaufania (TRPO, PPO).