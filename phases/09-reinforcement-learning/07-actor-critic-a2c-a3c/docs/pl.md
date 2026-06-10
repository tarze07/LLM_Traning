# Aktor-krytyk — A2C i A3C

> REINFORCE jest głośny. Dodaj krytyka, który uczy się `V̂(s)`, odejmij to od zwrotu, a uzyskasz przewagę, która ma takie same oczekiwania, ale znacznie mniejszą wariancję. To jest krytyka aktora. A2C uruchamia go synchronicznie; A3C uruchamia go w wątkach. Obydwa stanowią mentalny model każdej nowoczesnej metody głębokiego RL.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 9 · 04 (Nauka TD), Faza 9 · 06 (WZMOCNIENIE)
**Czas:** ~75 minut

## Problem

Vanilla REINFORCE działa, ale jej zmienność jest straszna. Zwroty w Monte Carlo `G_t` mogą zmieniać się 10-krotnie między odcinkami. Pomnożenie tego szumu przez `∇ log π` i uśrednienie daje estymator gradientu, który wymaga tysięcy odcinków, aby przesunąć politykę na tę samą odległość, na jaką można ją przenieść przy znacznie mniejszej liczbie aktualizacji DQN.

Wariancja wynika z zastosowania surowych zwrotów. Jeśli odejmiemy linię bazową `b(s_t)` — dowolną funkcję stanu, w tym wartość wyuczoną — oczekiwania pozostają niezmienione, a wariancja spada. Najlepszym możliwym do zastosowania punktem odniesienia jest `V̂(s_t)`. Teraz mnożenie ilości `∇ log π` jest *zaletą*:

`A(s, a) = G - V̂(s)`

Działanie jest dobre, jeśli przyniosło ponadprzeciętny zwrot; źle, jeśli poniżej. WZMOCNIENIE z uczonym krytykiem to *aktor-krytyk*. Krytyk daje aktorowi nauczyciela o niskiej wariancji. To każda metoda głębokiej polityki po 2015 roku (A2C, A3C, PPO, SAC, IMPALA).

## Koncepcja

![Actor-critic: polityka netto plus wartość netto, pozostała część TD jako zaleta](../assets/actor-critic.svg)

**Dwie sieci, jedna wspólna strata:**

- **Aktor** `π_θ(a | s)`: zasady. Próbki do działania. Wyszkolony z gradientem polityki.
- **Krytyk** `V_φ(s)`: szacuje oczekiwany zwrot ze stanu. Przeszkolony w minimalizowaniu `(V_φ(s) - target)²`.

**Zaleta.** Dwie standardowe formy:

- *Zaleta MC:* `A_t = G_t - V_φ(s_t)`. Bezstronny, większa wariancja.
- *Przewaga TD:* `A_t = r_{t+1} + γ V_φ(s_{t+1}) - V_φ(s_t)`. stronniczy (używa `V_φ`), znacznie mniejsza wariancja. Nazywany także *resztą TD* `δ_t`.

**Przewaga w n-stopniach.** Interpolacja między nimi:

`A_t^{(n)} = r_{t+1} + γ r_{t+2} + … + γ^{n-1} r_{t+n} + γ^n V_φ(s_{t+n}) - V_φ(s_t)`

`n = 1` to czysty TD. `n = ∞` to MC. Większość implementacji używa `n = 5` dla Atari, `n = 2048` dla PPO na MuJoCo.

**Uogólnione oszacowanie korzyści (GAE).** Schulman i in. (2016) zaproponowali wykładniczą średnią ważoną wszystkich zalet n-stopniowych:

`A_t^{GAE} = Σ_{l=0}^{∞} (γλ)^l δ_{t+l}`

z `λ ∈ [0, 1]`. `λ = 0` to TD (niska wariancja, duże obciążenie). `λ = 1` to MC (wysoka wariancja, bezstronność). Wartość domyślna `λ = 0.95` to wartość domyślna na rok 2026 — dostosuj, aż tarcza odchylenia/wariancji znajdzie się tam, gdzie chcesz.

**A2C: synchroniczna przewaga aktor-krytyk.** Zbierz `T` kroki w `N` równoległych środowiskach. Oblicz korzyści dla każdego kroku. Zaktualizuj aktora i krytyka w połączonej partii. Powtarzać. Prostszy, bardziej skalowalny brat A3C.

**A3C: asynchroniczna przewaga aktora-krytyka.** Mnih i in. (2016). Utwórz `N` wątki robocze, z których każdy uruchamia środowisko. Każdy proces roboczy oblicza gradienty lokalnie podczas własnego wdrożenia, a następnie asynchronicznie stosuje je do udostępnionego serwera parametrów. Nie jest potrzebny bufor odtwarzania — pracownicy dekorelują, biegnąc różnymi trajektoriami. Projekt A3C udowodnił, że można trenować na procesorach na dużą skalę. W 2026 r. dominuje A2C (wsadowo równoległe środowiska) oparte na procesorach graficznych, ponieważ procesory graficzne wymagają dużych partii.

**Łączna strata.**

`L(θ, φ) = -E[ A_t · log π_θ(a_t | s_t) ]  +  c_v · E[(V_φ(s_t) - G_t)²]  -  c_e · E[H(π_θ(·|s_t))]`

Trzy terminy: strata w wyniku gradientu polityki, regresja wartości, premia za entropię. `c_v ~ 0.5`, `c_e ~ 0.01` to kanoniczne punkty początkowe.

## Zbuduj to

### Krok 1: krytyk

Krytyk liniowy `V_φ(s) = w · features(s)` zaktualizowany za pomocą MSE:

```python
def critic_update(w, x, target, lr):
    v_hat = dot(w, x)
    err = target - v_hat
    for j in range(len(w)):
        w[j] += lr * err * x[j]
    return v_hat
```

W formie tabelarycznej krytyk skupia się na kilkuset odcinkach. Na Atari zastąp krytyka liniowego wspólnym łączem CNN + głową wartości.

### Krok 2: przewaga w n-krokach

Biorąc pod uwagę wdrożenie długości `T` i załadowaną wersję końcową `V(s_T)`:

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

`returns` jest celem krytyków. `advantages` to mnożenie `∇ log π`.

### Krok 3: aktualizacja łączona

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

Zgodnie z zasadami, jedno wdrożenie na aktualizację, oddzielne stawki uczenia się dla aktora i krytyka.

### Krok 4: równoległość (A3C vs A2C)

- **A3C:** rozwiń `N` wątki. Każdy ma własne środowisko i własne podanie do przodu. Okresowo przesyłaj aktualizacje gradientu do udostępnionego wzorca. Żadnych blokad na mistrzu – wyścigi są w porządku, po prostu dodają hałasu.
- **A2C:** uruchamianie `N` instancji env w jednym procesie, układanie obserwacji w `[N, obs_dim]` wsad, wsadowy przebieg w przód, wsadowy przebieg w tył. Wyższe wykorzystanie procesora graficznego, deterministyczne, łatwiejsze do uzasadnienia. Domyślnie w 2026 r.

Dla przejrzystości nasz kod zabawek jest jednowątkowy; przepisanie na wsadowe A2C to trzy linie numpy.

## Pułapki

- **Stronniczość krytyka przed gradientem aktora.** Jeśli krytyk jest przypadkowy, jego punkt odniesienia nie ma charakteru informacyjnego i trenujesz na czystym szumie. Rozgrzej krytyka przez kilkaset kroków, zanim włączysz gradient polityki, lub użyj wolnego tempa uczenia się aktora.
- **Normalizacja korzyści.** Normalizacja korzyści do średniej zerowej/jednostki standardowej na partię. Stabilizuje trening masowo przy niemal zerowych kosztach.
- **Wspólny bagażnik.** Użyj współdzielonego ekstraktora funkcji dla aktora i krytyka na wejściach obrazu. Oddzielne głowy. Udostępnione funkcje freeride na obu stratach.
- **Umowa oparta na zasadach.** A2C ponownie wykorzystuje dane podczas dokładnie jednej aktualizacji. Więcej, a twój gradient jest stronniczy (korekta próbkowania ważności jest tym, co dodaje PPO).
- **Załamanie entropii.** Bez `c_e > 0` zasady stają się niemal deterministyczne po kilkuset aktualizacjach i przestają być eksplorowane.
- **Skala nagród.** Wielkość przewagi zależy od skali nagród. Normalizuj nagrody (np. dzielenie według standardu działania) w celu uzyskania spójnych wielkości gradientu w zadaniach.

## Użyj tego

A2C/A3C rzadko są ostatecznym wyborem w 2026 r., ale są to architektury, które później udoskonala się:

| Metoda | Związek z A2C |
|------------|----------------|
| PPO | A2C + obcięty współczynnik ważności dla aktualizacji wieloepokowych |
| IMPALA | Korekta niezgodności z zasadami A3C + V-trace |
| SAC (faza 9 · 07) | A2C niezgodne z polityką z krytykiem wartości miękkiej (następna lekcja) |
| GRPO (faza 9 · 12) | A2C bez krytyka — przewaga względna grupy |
| IOD | A2C pogrążyło się w stracie w rankingu preferencji, bez pobierania próbek |
| AlphaStar / OpenAI Pięć | A2C z treningiem ligowym + przedtreningiem imitacyjnym |

Jeśli w artykule z 2026 roku widzisz „przewagę”, pomyśl o aktorze-krytyku.

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

1. **Łatwe.** Szkolowanie aktorów-krytyków z przewagą MC (`G_t - V(s_t)`) w sieci 4×4 GridWorld. Porównaj wydajność próbki z WZMOCNIENIEM ze średnią bieżącą z lekcji 06.
2. **Średni.** Przełącz na przewagę rezydualną TD (`r + γ V(s') - V(s)`). Zmierz wariancję partii korzyści. O ile spada?
3. **Trudne.** Implementuj GAE(λ). Przeszukaj `λ ∈ {0, 0.5, 0.9, 0.95, 1.0}`. Wykreśl ostateczny zwrot w funkcji wydajności próbki. Gdzie jest optymalny punkt odchylenia/wariancji dla tego zadania?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Aktor | „Sieć polityczna” | `π_θ(a\|s)`, zaktualizowany zgodnie z gradientem zasad. |
| Krytyk | „Wartość netto” | `V_φ(s)`, zaktualizowane przez regresję MSE do zwrotów / celów TD. |
| Zaleta | „O ile lepiej niż przeciętnie” | `A(s, a) = Q(s, a) - V(s)` lub jego estymatory. Mnożnik dla `∇ log π`. |
| Pozostałość TD | „δ” | `δ_t = r + γ V(s') - V(s)`; jednoetapowe oszacowanie korzyści. |
| GAE | „Pokrętło interpolacyjne” | Wykładniczo ważona suma korzyści w n-stopniach, sparametryzowana przez `λ`. |
| A2C | „Synchroniczny aktor-krytyk” | Pogrupowane w środowiskach env; jeden krok gradientu na wdrożenie. |
| A3C | „Asynchroniczny krytyk aktorski” | Wątki robocze wypychają gradienty do udostępnionego serwera parametrów. Papier oryginalny; rzadziej w 2026 r. |
| Bootstrap | „Użyj V na horyzoncie” | Skróć wdrożenie, dodaj `γ^n V(s_{t+n})`, aby zamknąć sumę. |

## Dalsze czytanie

- [Mnih i in. (2016). Asynchronous Methods for Deep Reinforcement Learning](https://arxiv.org/abs/1602.01783) — A3C, oryginalna praca krytyka aktorów asynchronicznych.
- [Schulman i in. (2016). Wysokowymiarowa ciągła kontrola z wykorzystaniem uogólnionego szacowania przewagi](https://arxiv.org/abs/1506.02438) – GAE.
- [Sutton i Barto (2018). Ch. 13 — Metody aktora-krytyka](http://incompleteideas.net/book/RLbook2020.pdf) — podstawy; połącz to z Ch. 9 na temat aproksymacji funkcji, gdy krytykiem jest sieć neuronowa.
- [Espeholt i in. (2018). IMPALA](https://arxiv.org/abs/1802.01561) — skalowalny rozproszony aktor krytyczny z korekcją niezgodności z polityką V-trace.
- [OpenAI Baselines / Stable-Baselines3](https://stable-baselines3.readthedocs.io/) — warto przeczytać produkcyjne implementacje A2C/PPO.
- [Konda i Tsitsiklis (2000). Algorytmy aktor-krytyk](https://papers.nips.cc/paper/1786-actor-critic-algorithms) — podstawowy wynik zbieżności rozkładu aktor-krytyk w dwóch skalach czasowych.