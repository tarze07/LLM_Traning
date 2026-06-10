# Bliższa optymalizacja polityki (PPO)

> A2C odrzuca każde wdrożenie po jednej aktualizacji. PPO otacza gradient zasad obciętym współczynnikiem ważności, dzięki czemu można wykonać ponad 10 epok na tych samych danych bez eksplozji zasad. Schulmana i in. (2017). Nadal domyślny algorytm gradientu polityki w 2026 r.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 9 · 06 (WZMOCNIENIE), Faza 9 · 07 (aktor-krytyk)
**Czas:** ~75 minut

## Problem

A2C (lekcja 07) jest zgodna z zasadami: gradient `E_{π_θ}[A · ∇ log π_θ]` wymaga danych próbkowanych z *bieżącego* `π_θ`. Weź jedną aktualizację, a `π_θ` zmieni się; dane, których użyłeś, są teraz niezgodne z zasadami. Użyj go ponownie, a twój gradient będzie stronniczy.

Wdrożenia są drogie. Na Atari jedno wdrożenie w 8 środowiskach × 128 kroków = 1024 przejścia i kilkanaście sekund czasu środowiska. Wyrzucanie tego po jednym kroku gradientu jest marnotrawstwem.

Pierwszą poprawką była optymalizacja polityki regionu zaufania (TRPO, Schulman 2015): ogranicz każdą aktualizację tak, aby rozbieżność KL między starą i nową polityką pozostawała poniżej `δ`. Teoretycznie czyste, ale wymaga rozwiązania gradientu sprzężonego na aktualizację. Nikt nie będzie prowadził TRPO w 2026 roku.

PPO (Schulman et al. 2017) zastępuje twarde ograniczenie regionu zaufania prostym obciętym celem. Jedna dodatkowa linia kodu. Dziesięć epok na wdrożenie. Brak gradientów sprzężonych. Wystarczająco dobre gwarancje teoretyczne. Dziewięć lat później jest to nadal domyślny algorytm gradientu polityki dla wszystkiego, od MuJoCo po RLHF.

## Koncepcja

![Cel zastępczy obcięty przez PPO: obcięcie współczynnika przy 1 ± ε](../assets/ppo.svg)

**Współczynnik ważności.**

`r_t(θ) = π_θ(a_t | s_t) / π_{θ_old}(a_t | s_t)`

Jest to stosunek prawdopodobieństwa nowej zasady do zasady, która zebrała dane. `r_t = 1` oznacza brak zmian. `r_t = 2` oznacza, że ​​nowe zasady z dwukrotnie większym prawdopodobieństwem uwzględnią `a_t` niż stare.

**Przycięta surogatka.**

`L^{CLIP}(θ) = E_t [ min( r_t(θ) A_t, clip(r_t(θ), 1-ε, 1+ε) A_t ) ]`

Dwa terminy:

- Jeśli przewaga `A_t > 0` i stosunek próbuje wzrosnąć powyżej `1 + ε`, klip spłaszcza gradient — nie przesuwaj dobrego działania dalej niż `+ε` powyżej starego prawdopodobieństwa.
- Jeśli przewaga `A_t < 0` i stosunek spróbują przekroczyć `1 - ε` (co oznacza, że ​​prawdopodobieństwo złego działania byłoby większe w porównaniu z jego przyciętą redukcją), klip zamyka gradient — nie przesuwaj złego działania poniżej `-ε`.

`min` działa w innym kierunku: jeśli stosunek przesunął się w *korzystnym* kierunku, nadal uzyskasz gradient (bez przycinania z boku, które mogłoby cię zranić).

Typowy `ε = 0.2`. Przedstaw cel jako funkcję `r_t`: funkcja odcinkowo-liniowa z płaskim dachem po „dobrej stronie” i płaską podłogą po „złej stronie”.

**Pełna strata PPO.**

`L(θ, φ) = L^{CLIP}(θ) - c_v · (V_φ(s_t) - V_t^{target})² + c_e · H(π_θ(·|s_t))`

Ta sama struktura aktora-krytyka co A2C. Trzy współczynniki, zwykle `c_v = 0.5`, `c_e = 0.01`, `ε = 0.2`.

**Pętla treningowa.**

1. Zbierz `N × T` przejścia pomiędzy `N` równoległymi środowiskami dla `T` kroków każdy.
2. Oblicz zalety (GAE), zamroź je jako stałe.
3. Zablokuj `π_{θ_old}` jako migawkę bieżącego `π_θ`.
4. Dla epok `K`, dla każdej minipartii `(s, a, A, V_target, log π_old(a|s))`:
   - Oblicz `r_t(θ) = exp(log π_θ(a|s) - log π_old(a|s))`.
   - Zastosuj `L^{CLIP}` + utrata wartości + entropia.
   - Krok gradientowy.
5. Odrzuć wdrożenie. Wróć do kroku 1.

`K = 10` i minipartie po 64 to standardowy zestaw hiperparametrów. PPO jest solidny: dokładne liczby rzadko mają znaczenie w granicach ±50%.

**Wariant kary KL.** W oryginalnej pracy zaproponowano alternatywę wykorzystującą adaptacyjną karę KL: `L = L^{PG} - β · KL(π_θ || π_old)` z `β` skorygowaną na podstawie zaobserwowanego KL. Wersja przycinająca stała się dominująca; wariant KL przetrwał w RLHF (gdzie KL do polityki referencyjnej jest osobnym ograniczeniem, którego i tak zawsze potrzebujesz).

## Zbuduj to

### Krok 1: przechwyć `log π_old(a | s)` w momencie wdrożenia

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

Migawka jest wykonywana jednorazowo, podczas wdrażania. Nie zmienia się podczas okresów aktualizacji.

### Krok 2: oblicz korzyści GAE (lekcja 07)

To samo co A2C. Normalizuj w całej partii.

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

Sercem PPO jest wzór „przycięty → zerowy gradient”. Jeśli nowa polityka odeszła już zbyt daleko w korzystnym kierunku, aktualizacja zostanie zatrzymana.

### Krok 4: wartość i entropia

Dodaj standardowe MSE do celu krytycznego i premię za entropię dla aktora, tak samo jak A2C.

### Krok 5: diagnostyka

Trzy rzeczy, które warto obejrzeć przy każdej aktualizacji:

- **Średnia KL** `E[log π_old - log π_θ]`. Powinien pozostać w `[0, 0.02]`. Jeśli przekroczy `0.1`, zmniejsz `K_EPOCHS` lub `LR`.
- **Ułamek klipu** — ułamek próbek, których stosunek leży poza `[1-ε, 1+ε]`. Powinno być `~0.1-0.3`. Jeśli `~0`, klip nigdy się nie uruchomi → podnieś `LR` lub `K_EPOCHS`. Jeśli `~0.5+` oznacza to, że nadmiernie dopasowujesz wdrożenie → obniż je.
- **Wyjaśniona wariancja** `1 - Var(V_target - V_pred) / Var(V_target)`. Wskaźnik jakości krytyka. W miarę uczenia się krytyka powinno wzrosnąć w kierunku 1.

## Pułapki

- **Źle dostrojony współczynnik Clip.** `ε = 0.2` jest de facto standardem. Przejście do `0.1` powoduje, że aktualizacje są zbyt nieśmiałe; `0.3+` powoduje niestabilność.
- **Zbyt wiele epok.** `K > 20` rutynowo ulega destabilizacji, ponieważ polityka odbiega od `π_old`. Epoki Cap, szczególnie w przypadku dużych sieci.
- **Brak normalizacji nagród.** Duże skale nagród ograniczają zasięg magazynowania. Normalizuj nagrody (uruchamiając std) przed obliczeniem korzyści.
- **Zapominanie o normalizacji przewagi.** Normalizacja średniej zerowej/jednostki standardowej na partię jest standardem. Pominięcie tego niszczy PPO w większości testów porównawczych.
- **Szybkość uczenia się nie spadła.** PPO korzysta z liniowego zaniku LR do zera. Stały LR jest często gorszy.
- **Błędy matematyczne współczynnika ważności.** Zawsze `exp(log_new - log_old)` dla stabilności numerycznej, a nie `new / old`.
- **Zły znak gradientu.** Maksymalizuj surogat = *minimizuj* `-L^{CLIP}`. Odwrócony znak jest najczęstszym błędem PPO.

## Użyj tego

PPO to domyślny algorytm RL w roku 2026 w zaskakującej liczbie domen:

| Przypadek użycia | Wariant PPO |
|--------------|------------|
| MuJoCo / sterowanie robotyką | PPO z polityką Gaussa, GAE(0,95) |
| Atari / gry dyskretne | PPO z kategoryczną polityką, wdrażanie w 128 krokach |
| RLHF dla LLM | PPO z karą KL dla modelu referencyjnego, nagroda od RM na koniec odpowiedzi |
| Agenci gier na dużą skalę | IMPALA + PPO (AlphaStar, OpenAI Five) |
| Rozumowanie LLM | GRPO (Lekcja 12) — wariant PPO bez krytyki |
| Dane wyłącznie preferencyjne | DPO — zamknięcie PPO+KL w formie zamkniętej, brak pobierania próbek online |

*Kształt straty* PPO — obcięty surogat + wartość + entropia — jest rusztowaniem dla DPO, GRPO i prawie każdego rurociągu RLHF.

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

1. **Łatwe.** Uruchom PPO na 4×4 GridWorld za pomocą `ε=0.2, K=4`. Porównaj wydajność próbki z A2C (jedna epoka na wdrożenie) przy dopasowanych krokach środowiska.
2. **Średni.** Przeciągnięcie `K ∈ {1, 4, 10, 30}`. Wykreśl zwrot w funkcji kroków env i śledź średnią KL na aktualizację. O której `K` KL eksploduje podczas tego zadania?
3. **Trudne.** Zastąp obcięty surogat adaptacyjną karą za KL (`β` podwojone, jeśli `KL > 2·target`, zmniejszone o połowę, jeśli `KL < target/2`). Porównaj ostateczny zwrot, stabilność i brak zacisków.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Stosunek ważności | „r_t(θ)” | `π_θ(a\|s) / π_old(a\|s)`; odstępstwo od polityki, w ramach której zbierano dane. |
| Obcięty surogat | „Główna sztuczka PPO” | `min(r·A, clip(r, 1-ε, 1+ε)·A)`; płaski gradient za klipsem po korzystnej stronie. |
| Region zaufania | „Zamiar TRPO/PPO” | Ogranicz KL każdej aktualizacji, aby zagwarantować monotonną poprawę. |
| Kara KL | „Rejon miękkiego zaufania” | Alternatywne PPO: `L - β · KL(π_θ \|\| π_old)`. Adaptacyjny `β`. |
| Ułamek klipu | „Jak często wyzwalacze przycinania” | Diagnostyczny — powinien wynosić 0,1-0,3; na zewnątrz oznacza źle dostrojony. |
| Szkolenie wieloepokowe | „Ponowne wykorzystanie danych” | K epok przy każdym wdrożeniu; koszt wariancji zamieniony na efektywność próbki. |
| Zgodnie z zasadami | „Przeważnie na temat polityki” | PPO jest nominalnie zgodny z zasadami, ale epoki K>1 bezpiecznie korzystają z danych nieco niezgodnych z zasadami. |
| PPO-KL | „Drugi PPO” | KL-wariant karny; używane w RLHF, gdzie KL-do-odniesienia jest już ograniczeniem. |

## Dalsze czytanie

- [Schulman i in. (2017). Algorytmy optymalizacji polityki proksymalnej](https://arxiv.org/abs/1707.06347) — artykuł.
- [Schulman i in. (2015). Optymalizacja polityki regionu zaufania](https://arxiv.org/abs/1502.05477) — TRPO, poprzednik PPO.
- [Andrychowicz i in. (2021). Co ma znaczenie w RL zgodnym z polityką? Badanie empiryczne na dużą skalę](https://arxiv.org/abs/2006.05990) — ablowano każdy hiperparametr PPO.
- [Ouyang i in. (2022). Szkolenie modeli językowych w zakresie wykonywania instrukcji na podstawie opinii ludzi](https://arxiv.org/abs/2203.02155) — InstructGPT; receptury PPO-in-RLHF.
- [OpenAI Spinning Up — PPO](https://spinningup.openai.com/en/latest/algorithms/ppo.html) — czysta nowoczesna ekspozycja z PyTorch.
- [Implementacja CleanRL PPO](https://github.com/vwxyzjn/cleanrl) — odniesienie do jednoplikowego PPO używanego w wielu artykułach.
- [Hugging Face TRL — PPOTrainer](https://huggingface.co/docs/trl/main/en/ppo_trainer) — przepis na produkcję PPO na modelach językowych; przeczytaj obok lekcji 09 (RLHF).
- [Engstrom i in. (2020). Implementacja ma znaczenie w głębokich gradientach polityki](https://arxiv.org/abs/2005.12729) — artykuł „37 optymalizacji na poziomie kodu”; które sztuczki PPO są nośne, a które folklorem.