# Bliższa optymalizacja polityki (PPO)

> A2C odrzuca każde wdrożenie po jednej aktualizacji. PPO otacza gradient polityki obciętym współczynnikiem ważności, dzięki czemu można wykonać ponad 10 epok na tych samych danych bez destabilizacji polityki. Schulman i in. (2017). Do dziś domyślny algorytm gradientu polityki — stan na 2026 r.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 9 · 06 (REINFORCE), Faza 9 · 07 (aktor-krytyk)
**Czas:** ~75 minut

## Problem

A2C (lekcja 07) jest zgodny z polityką: gradient `E_{π_θ}[A · ∇ log π_θ]` wymaga danych próbkowanych z *bieżącego* `π_θ`. Po jednej aktualizacji `π_θ` ulega zmianie — dane zebrane wcześniej stają się nieaktualne. Ponowne ich użycie wprowadza obciążenie gradientu.

Wdrożenia są kosztowne. Na Atari jedno wdrożenie w 8 środowiskach po 128 kroków daje 1024 przejścia i kilkanaście sekund czasu środowiska. Odrzucanie tych danych po jednym kroku gradientowym jest marnotrawstwem.

Pierwszą propozycją rozwiązania była optymalizacja polityki regionu zaufania (TRPO, Schulman 2015): ogranicz każdą aktualizację tak, by rozbieżność KL między starą a nową polityką pozostawała poniżej `δ`. Podejście eleganckie teoretycznie, lecz wymagające rozwiązania gradientu sprzężonego przy każdej aktualizacji. W praktyce nikt nie stosuje TRPO w 2026 roku.

PPO (Schulman et al. 2017) zastępuje twarde ograniczenie regionu zaufania prostym celem obciętym. Jedna dodatkowa linia kodu. Dziesięć epok na wdrożenie. Żadnych gradientów sprzężonych. Wystarczające gwarancje teoretyczne. Dziewięć lat później pozostaje domyślnym algorytmem gradientu polityki we wszystkich zastosowaniach — od MuJoCo po RLHF.

## Koncepcja

![Cel zastępczy obcięty przez PPO: obcięcie współczynnika przy 1 ± ε](../assets/ppo.svg)

**Współczynnik ważności.**

`r_t(θ) = π_θ(a_t | s_t) / π_{θ_old}(a_t | s_t)`

Jest to stosunek prawdopodobieństwa nowej polityki do polityki, która zebrała dane. `r_t = 1` oznacza brak zmiany. `r_t = 2` oznacza, że nowa polityka dwukrotnie chętniej wybierze `a_t` niż stara.

**Przycięty cel zastępczy.**

`L^{CLIP}(θ) = E_t [ min( r_t(θ) A_t, clip(r_t(θ), 1-ε, 1+ε) A_t ) ]`

Dwa składniki:

- Jeśli przewaga `A_t > 0` i stosunek próbuje wzrosnąć powyżej `1 + ε`, przycinanie spłaszcza gradient — dobre działanie nie zostaje wzmocnione bardziej niż o `+ε` względem starego prawdopodobieństwa.
- Jeśli przewaga `A_t < 0` i stosunek spada poniżej `1 - ε` (co oznaczałoby wzrost prawdopodobieństwa złego działania), przycinanie blokuje gradient — złe działanie nie zostaje stłumione bardziej niż o `-ε`.

Operator `min` działa w przeciwnym kierunku: jeśli stosunek przesunął się w *korzystną* stronę, gradient nadal jest przekazywany (brak przycinania tam, gdzie mogłoby zaszkodzić).

Typowe `ε = 0.2`. Cel jako funkcja `r_t` jest odcinkowo-liniowy — z płaską częścią po „dobrej stronie" i płaską podstawą po „złej stronie".

**Pełna strata PPO.**

`L(θ, φ) = L^{CLIP}(θ) - c_v · (V_φ(s_t) - V_t^{target})² + c_e · H(π_θ(·|s_t))`

Ta sama struktura aktora-krytyka co w A2C. Trzy współczynniki, zazwyczaj `c_v = 0.5`, `c_e = 0.01`, `ε = 0.2`.

**Pętla treningowa.**

1. Zbierz `N × T` przejść z `N` równoległych środowisk po `T` kroków każde.
2. Oblicz przewagi (GAE) i zamroź je jako stałe.
3. Zachowaj migawkę bieżącego `π_θ` jako `π_{θ_old}`.
4. Przez `K` epok, dla każdej minipartii `(s, a, A, V_target, log π_old(a|s))`:
   - Oblicz `r_t(θ) = exp(log π_θ(a|s) - log π_old(a|s))`.
   - Zastosuj `L^{CLIP}` + strata wartości + entropia.
   - Wykonaj krok gradientowy.
5. Odrzuć wdrożenie. Wróć do kroku 1.

`K = 10` i minipartie po 64 to standardowe hiperparametry. PPO jest odporny na zmiany — dokładne wartości rzadko mają znaczenie w granicach ±50%.

**Wariant z karą KL.** Oryginalna praca proponuje alternatywę z adaptacyjną karą KL: `L = L^{PG} - β · KL(π_θ || π_old)`, gdzie `β` jest korygowane na podstawie obserwowanego KL. Wersja z przycinaniem stała się dominująca; wariant z karą KL przetrwał w RLHF (gdzie KL względem polityki referencyjnej jest osobnym ograniczeniem, którego i tak zawsze potrzebujesz).

## Implementacja

### Krok 1: przechwytywanie `log π_old(a | s)` podczas wdrożenia

```python
for step in range(T):
    probs = softmax(logits(theta, state_features(s)))
    a = sample(probs, rng)
    s_next, r, done = env.step(s, a)
    buffer.append({
        "s": s, "a": a, "r": r, "done": done,
        "v_old": value(w, state_features(s)),
        "log_pi_old": log(probs[a] + 1e-12),
    })
    s = s_next
```

Migawka jest tworzona jednorazowo, podczas wdrożenia. Nie zmienia się w trakcie kolejnych aktualizacji.

### Krok 2: obliczanie przewag GAE (lekcja 07)

Identycznie jak w A2C. Normalizuj w obrębie całej partii.

### Krok 3: przycięta aktualizacja zastępcza

```python
for _ in range(K_EPOCHS):
    for mb in minibatches(buffer, size=64):
        for rec in mb:
            x = state_features(rec["s"])
            probs = softmax(logits(theta, x))
            logp = log(probs[rec["a"]] + 1e-12)
            ratio = exp(logp - rec["log_pi_old"])
            adv = rec["advantage"]
            surrogate = min(
                ratio * adv,
                clamp(ratio, 1 - EPS, 1 + EPS) * adv,
            )
            # backprop -surrogate, add value loss, subtract entropy
            grad_logpi = onehot(rec["a"]) - probs
            if (adv > 0 and ratio >= 1 + EPS) or (adv < 0 and ratio <= 1 - EPS):
                pg_grad = 0.0  # clipped
            else:
                pg_grad = ratio * adv
            for i in range(N_ACTIONS):
                for j in range(N_FEAT):
                    theta[i][j] += LR * pg_grad * grad_logpi[i] * x[j]
```

Sercem PPO jest wzorzec „obcięcie → zerowy gradient". Gdy nowa polityka zbyt daleko odeszła w korzystnym kierunku, aktualizacja zostaje zatrzymana.

### Krok 4: wartość i entropia

Dodaj standardowe MSE dla celu krytyka oraz premię entropijną dla aktora — tak samo jak w A2C.

### Krok 5: diagnostyka

Trzy wskaźniki warte śledzenia przy każdej aktualizacji:

- **Średnie KL** `E[log π_old - log π_θ]`. Powinno pozostawać w przedziale `[0, 0.02]`. Przekroczenie `0.1` sygnalizuje konieczność zmniejszenia `K_EPOCHS` lub `LR`.
- **Ułamek obciętych próbek** — odsetek próbek, których stosunek wykracza poza `[1-ε, 1+ε]`. Oczekiwana wartość to `~0.1-0.3`. Wartość bliska `0` oznacza, że obcinanie nigdy nie jest aktywowane — zwiększ `LR` lub `K_EPOCHS`. Wartość `~0.5+` wskazuje na nadmierne dopasowanie do wdrożenia — ogranicz oba parametry.
- **Wyjaśniona wariancja** `1 - Var(V_target - V_pred) / Var(V_target)`. Miara jakości krytyka. W miarę uczenia powinna rosnąć w kierunku 1.

## Pułapki

- **Źle dobrany współczynnik obcinania.** `ε = 0.2` jest de facto standardem. Zmniejszenie do `0.1` sprawia, że aktualizacje są zbyt zachowawcze; wartości `0.3+` prowadzą do niestabilności.
- **Zbyt wiele epok.** `K > 20` regularnie destabilizuje uczenie, bo polityka odbiega od `π_old`. Ogranicz liczbę epok, szczególnie przy dużych sieciach.
- **Brak normalizacji nagród.** Duże skale nagród zaburzają estymację przewag. Normalizuj nagrody (bieżącym odchyleniem standardowym) przed obliczaniem przewag.
- **Pominięcie normalizacji przewag.** Normalizacja do zerowej średniej i jednostkowego odchylenia standardowego na poziomie partii jest standardem. Jej pominięcie psuje PPO w większości testów porównawczych.
- **Stała szybkość uczenia.** PPO czerpie korzyści z liniowego zaniku LR do zera. Stały LR daje na ogół gorsze wyniki.
- **Błędy numeryczne współczynnika ważności.** Zawsze używaj `exp(log_new - log_old)` dla stabilności numerycznej, a nie bezpośredniego ilorazu `new / old`.
- **Zły znak gradientu.** Maksymalizacja surogatu oznacza *minimalizację* `-L^{CLIP}`. Odwrócony znak to najczęstszy błąd przy implementacji PPO.

## Zastosowania

PPO to domyślny algorytm RL w 2026 roku w zaskakująco szerokim spektrum dziedzin:

| Przypadek użycia | Wariant PPO |
|--------------|------------|
| MuJoCo / sterowanie robotyką | PPO z polityką Gaussa, GAE(0,95) |
| Atari / gry dyskretne | PPO z polityką kategoryczną, wdrożenie w 128 krokach |
| RLHF dla LLM | PPO z karą KL względem modelu referencyjnego, nagroda od RM na końcu odpowiedzi |
| Agenci gier na dużą skalę | IMPALA + PPO (AlphaStar, OpenAI Five) |
| Rozumowanie LLM | GRPO (Lekcja 12) — wariant PPO bez krytyka |
| Dane wyłącznie preferencyjne | DPO — zamknięta forma PPO+KL, bez próbkowania online |

*Kształt straty* PPO — obcięty surogat, strata wartości i entropia — stanowi szkielet dla DPO, GRPO i niemal każdego potoku RLHF.

## Wyślij to

Zapisz jako `outputs/skill-ppo-trainer.md`:

```markdown
---
name: ppo-trainer
description: Produce a PPO training config and a diagnostic plan for a given environment.
version: 1.0.0
phase: 9
lesson: 8
tags: [rl, ppo, policy-gradient]
---

Given an environment and training budget, output:

1. Rollout size. `N` envs × `T` steps.
2. Update schedule. `K` epochs, minibatch size, LR schedule.
3. Surrogate params. `ε` (clip), `c_v`, `c_e`, advantage normalization on.
4. Advantage. GAE(`λ`) with explicit `γ` and `λ`.
5. Diagnostics plan. KL, clip fraction, explained variance thresholds with alerts.

Refuse `K > 30` or `ε > 0.3` (unsafe trust region). Refuse any PPO run without advantage normalization or KL/clip monitoring. Flag clip fraction sustained above 0.4 as drift.
```

## Ćwiczenia

1. **Łatwe.** Uruchom PPO na 4×4 GridWorld z `ε=0.2, K=4`. Porównaj efektywność próbkowania z A2C (jedna epoka na wdrożenie) przy tej samej liczbie kroków środowiska.
2. **Średnie.** Przetestuj `K ∈ {1, 4, 10, 30}`. Wykreśl zwrot w funkcji kroków środowiska i śledź średnie KL na aktualizację. Przy jakiej wartości `K` KL eksploduje na tym zadaniu?
3. **Trudne.** Zastąp obcięty surogat adaptacyjną karą KL (`β` podwajane, gdy `KL > 2·target`; zmniejszane o połowę, gdy `KL < target/2`). Porównaj końcowy zwrot, stabilność uczenia i częstość aktywacji obcinania.

## Kluczowe pojęcia

| Termin | Jak się mówi | Co to oznacza |
|------|-----------------|----------------------|
| Stosunek ważności | „r_t(θ)" | `π_θ(a\|s) / π_old(a\|s)`; miara odchylenia od polityki, z której zebrano dane. |
| Obcięty surogat | „Główna sztuczka PPO" | `min(r·A, clip(r, 1-ε, 1+ε)·A)`; gradient zeruje się po przekroczeniu progu po korzystnej stronie. |
| Region zaufania | „Cel TRPO/PPO" | Ograniczenie KL każdej aktualizacji gwarantujące monotoniczną poprawę polityki. |
| Kara KL | „Miękki region zaufania" | Alternatywne PPO: `L - β · KL(π_θ \|\| π_old)` z adaptacyjnym `β`. |
| Ułamek obciętych próbek | „Jak często działa obcinanie" | Wskaźnik diagnostyczny — powinien wynosić 0,1–0,3; wartości poza tym zakresem sygnalizują złe dostrojenie. |
| Trening wieloepokowy | „Ponowne użycie danych" | K epok na jedno wdrożenie; kompromis między wariancją a efektywnością próbkowania. |
| Zgodność z polityką | „Nominalnie on-policy" | PPO jest formalnie zgodny z polityką, lecz K>1 epok bezpiecznie korzysta z danych nieznacznie niezgodnych. |
| PPO-KL | „Drugi wariant PPO" | Wariant z karą KL; stosowany w RLHF, gdzie KL względem modelu referencyjnego jest i tak wymaganym ograniczeniem. |

## Literatura

- [Schulman i in. (2017). Proximal Policy Optimization Algorithms](https://arxiv.org/abs/1707.06347) — artykuł źródłowy.
- [Schulman i in. (2015). Trust Region Policy Optimization](https://arxiv.org/abs/1502.05477) — TRPO, poprzednik PPO.
- [Andrychowicz i in. (2021). What Matters In On-Policy Reinforcement Learning? A Large-Scale Empirical Study](https://arxiv.org/abs/2006.05990) — ablacja każdego hiperparametru PPO.
- [Ouyang i in. (2022). Training language models to follow instructions with human feedback](https://arxiv.org/abs/2203.02155) — InstructGPT; recepta na PPO w RLHF.
- [OpenAI Spinning Up — PPO](https://spinningup.openai.com/en/latest/algorithms/ppo.html) — przejrzyste współczesne omówienie z przykładami w PyTorch.
- [CleanRL PPO implementation](https://github.com/vwxyzjn/cleanrl) — jednoplikowa implementacja referencyjna stosowana w wielu pracach naukowych.
- [Hugging Face TRL — PPOTrainer](https://huggingface.co/docs/trl/main/en/ppo_trainer) — produkcyjna implementacja PPO dla modeli językowych; warto czytać równolegle z lekcją 09 (RLHF).
- [Engstrom i in. (2020). Implementation Matters in Deep Policy Gradients](https://arxiv.org/abs/2005.12729) — artykuł „37 optymalizacji na poziomie kodu"; które praktyki PPO są istotne, a które to tylko folklor.
