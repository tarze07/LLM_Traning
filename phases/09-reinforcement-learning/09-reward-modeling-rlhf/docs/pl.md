# Modelowanie nagród i RLHF

> Ludzie nie potrafią napisać funkcji nagrody za „dobrą reakcję asystenta”, ale mogą porównać dwie odpowiedzi i wybrać lepszą. Dopasuj model nagrody do tych porównań, a następnie porównaj z nim model języka. Christiano 2017. InstructGPT 2022. Przepis, który zmienił GPT-3 w ChatGPT. W 2026 r. będzie on w większości zastępowany przez DPO, ale model mentalny pozostanie.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 5 · 05 (Sentyment), Faza 9 · 08 (PPO)
**Czas:** ~45 minut

## Problem

Wytrenowałeś model języka pod kątem celu przewidywania następnego tokenu. Pisze gramatycznie po angielsku. Kłamie, włóczy się i nie chce odmówić. Nie da się tego naprawić częstszym szkoleniem wstępnym — problemem jest tekst internetowy, a nie lekarstwo.

Chcesz *nagrody skalarnej*, która mówi, że „odpowiedź A jest lepsza niż odpowiedź B dla instrukcji X”. Ręczne napisanie tej funkcji nagrody jest niemożliwe. „Przydatność” nie jest wyrażeniem zamkniętym dotyczącym tokenów. Ale ludzie mogą porównać dwa wyniki i zaznaczyć preferencje. To jest tanie w zbieraniu na dużą skalę.

RLHF (Christiano i in. 2017; Ouyang i in. 2022) przekształca preferencje w model nagrody, a następnie optymalizuje LM poprzez PPO pod kątem tej nagrody. W trzech krokach: SFT → RM → PPO. Jest to przepis, który dostarczył ChatGPT, Claude, Gemini i wszystkie inne dostosowane-LLM w latach 2023–2025.

W 2026 r. krok PPO zostanie w większości zastąpiony przez DPO (faza 10 · 08), ponieważ jest tańszy i prawie tak samo dobry do dostrajania wyrównania. Jednak element *modelu nagrody* nadal leży u podstaw każdego próbnika Best-of-N, każdego rurociągu RL z weryfikowalnych-nagród i każdego modelu wnioskowania wykorzystującego model nagrody procesowej. Zrozum RLHF, a zrozumiesz cały stos wyrównania.

## Koncepcja

![Trzyetapowe RLHF: SFT, szkolenie RM na prefach w parach, PPO z karą KL](../assets/rlhf.svg)

**Etap 1: Nadzorowane dostrajanie (SFT).** Rozpocznij od wstępnie wyszkolonego modelu podstawowego. Dostosuj pisane przez ludzi demonstracje docelowego zachowania (odpowiedzi zgodne z instrukcjami, pomocne odpowiedzi itp.). Wynik: model `π_SFT`, który jest *nastawiony na dobre zachowanie*, ale nadal ma nieograniczoną przestrzeń działania.

**Etap 2: Szkolenie z modelu nagrody.**

- Zbierz pary odpowiedzi `(y_+, y_-)` na podpowiedzi `x`, oznaczone przez ludzi jako „preferowane jest y_+ zamiast y_-”.
- Wytrenuj model nagrody `R_φ(x, y)`, aby przydzielał wyższe wyniki `y_+`.
- Strata: **logistyka par Bradley-Terry**:

  `L(φ) = -E[ log σ(R_φ(x, y_+) - R_φ(x, y_-)) ]`

  σ jest sigmoidą. Różnica w nagrodzie oznacza log-szanse preferencji. BT jest standardem od 1952 r. (Bradley-Terry) i jest dominującym wyborem w nowoczesnych RLHF.

- `R_φ` jest zwykle inicjowany z modelu SFT z głową skalarną na górze. Ten sam szkielet transformatora; pojedyncza warstwa liniowa generuje nagrodę.

**Etap 3: PPO przeciwko RM z karą KL.**

- Zainicjuj politykę, którą można trenować `π_θ` z `π_SFT`. Zachowaj zamrożone *referencje* `π_ref = π_SFT`.
- Nagroda na końcu odpowiedzi `y`:

  `r_total(x, y) = R_φ(x, y) - β · KL(π_θ(·|x) || π_ref(·|x))`

  Kara za KL uniemożliwia `π_θ` arbitralne odejście od `π_SFT` — jest to *regulator*, a nie region twardego zaufania. `β` zazwyczaj `0.01`-`0.05`.
- Uruchom PPO (lekcja 08) z tą nagrodą. Korzyści są obliczane na podstawie trajektorii na poziomie tokena, ale RM ocenia tylko pełną odpowiedź.

**Dlaczego KL?** Bez tego PPO z radością znajdzie strategie hakowania nagród — RM został przeszkolony jedynie w zakresie ukończeń w dystrybucji. Odpowiedź poza dystrybucją może uzyskać wyższy wynik niż jakakolwiek odpowiedź napisana przez człowieka. KL trzyma `π_θ` w pobliżu kolektora, w którym szkolono RM. Jest to najważniejsze pokrętło w RLHF.

**Stan na rok 2026:**

- **DPO** (Rafailov 2023): algebra w formie zamkniętej zwija etap 2+3 w pojedynczą nadzorowaną stratę w stosunku do danych dotyczących preferencji. Żadnego RM, żadnego PPO. Ta sama jakość w testach porównawczych wyrównania dla ułamka obliczeń. Omówione w fazie 10 · 08.
- **GRPO** (DeepSeek 2024–2025): PPO z punktem odniesienia względem grupy zamiast krytyka, nagroda od *weryfikatora* (przebieg kodu / dopasowanie odpowiedzi matematycznej) zamiast RM wyszkolonego przez człowieka. Dominujący dla modeli rozumowania. Omówione w fazie 9 · 12.
- **Modele nagrody procesu (PRM):** punktują rozwiązania częściowe (każdy etap wnioskowania), stosowane do wnioskowania zarówno w wariantach RLHF, jak i GRPO.
- **Konstytucyjna sztuczna inteligencja / RLAIF:** użyj dostosowanego LLM do generowania preferencji zamiast ludzi. Skaluje budżet preferencji.

## Zbuduj to

W tej lekcji używane są małe, syntetyczne „podpowiedzi” i „odpowiedzi” reprezentowane w postaci ciągów znaków. RM to punktacja liniowa oparta na reprezentacji worka żetonów. Żadnego prawdziwego LLM – liczy się *kształt* rurociągu, a nie skala. Zobacz `code/main.py`.

### Krok 1: syntetyczne dane dotyczące preferencji

```python
PROMPTS = ["help me", "answer me", "explain this"]
GOOD_WORDS = {"clear", "specific", "kind", "thorough"}
BAD_WORDS = {"vague", "rude", "wrong", "short"}

def make_pair(rng):
    x = rng.choice(PROMPTS)
    y_good = rng.choice(list(GOOD_WORDS)) + " " + rng.choice(list(GOOD_WORDS))
    y_bad = rng.choice(list(BAD_WORDS)) + " " + rng.choice(list(BAD_WORDS))
    return (x, y_good, y_bad)
```

W prawdziwym RLHF jest to zastępowane przez ludzkie etykiety. Kształt — `(prompt, preferred_response, rejected_response)` — jest identyczny.

### Krok 2: Model nagrody Bradleya-Terry’ego

Wynik liniowy: `R(x, y) = w · bag(y)`. Trenuj, aby zminimalizować utratę logów w parach BT:

```python
def rm_train_step(w, x, y_pos, y_neg, lr):
    r_pos = dot(w, bag(y_pos))
    r_neg = dot(w, bag(y_neg))
    p = sigmoid(r_pos - r_neg)
    for tok, cnt in bag(y_pos).items():
        w[tok] += lr * (1 - p) * cnt
    for tok, cnt in bag(y_neg).items():
        w[tok] -= lr * (1 - p) * cnt
```

Po kilkuset aktualizacjach `w` przypisuje dodatnie wagi do tokenów dobrych słów, a ujemne do złych.

### Krok 3: Polityka podobna do PPO oprócz RM

Nasza polityka dotycząca zabawek generuje pojedynczy token ze słownictwa. Oceniamy token poniżej RM, obliczamy `log π_θ(token | prompt)`, dodajemy karę KL do odniesienia i stosujemy obcięty surogat PPO.

```python
def rlhf_step(theta, ref, w, prompt, rng, eps=0.2, beta=0.1, lr=0.05):
    logits_theta = policy_logits(theta, prompt)
    probs = softmax(logits_theta)
    token = sample(probs, rng)
    logits_ref = policy_logits(ref, prompt)
    probs_ref = softmax(logits_ref)
    reward = dot(w, bag([token])) - beta * kl(probs, probs_ref)
    # ppo-style update on theta, treating reward as the return
    ...
```

### Krok 4: monitoruj KL

Śledź `KL(π_θ || π_ref)` każdą aktualizację. Jeśli przekroczy `~5-10`, zasada odeszła daleko od `π_SFT` — dolna wartość `β` rośnie lub rozpoczyna się hakowanie nagród. Jest to najlepsza diagnostyka w prawdziwym RLHF.

### Krok 5: przepis produkcyjny z TRL

Kiedy już zrozumiesz potok zabawek, oto ta sama pętla, którą pisze prawdziwy użytkownik biblioteki. [TRL](https://huggingface.co/docs/trl) Hugging Face to implementacja referencyjna — `RewardTrainer` dla etapu 2 i `PPOTrainer` (z wbudowaną funkcją KL-to-reference) dla etapu 3.

```python
# Stage 2: reward model from pairwise preferences
from trl import RewardTrainer, RewardConfig
from transformers import AutoModelForSequenceClassification, AutoTokenizer

tok = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8B-Instruct")
rm = AutoModelForSequenceClassification.from_pretrained(
    "meta-llama/Llama-3.1-8B-Instruct", num_labels=1
)

# dataset rows: {"prompt", "chosen", "rejected"} — Bradley-Terry format
trainer = RewardTrainer(
    model=rm,
    tokenizer=tok,
    train_dataset=preference_data,
    args=RewardConfig(output_dir="./rm", num_train_epochs=1, learning_rate=1e-5),
)
trainer.train()
```

```python
# Stage 3: PPO against the RM with KL penalty to the SFT reference
from trl import PPOTrainer, PPOConfig, AutoModelForCausalLMWithValueHead

policy = AutoModelForCausalLMWithValueHead.from_pretrained("./sft-checkpoint")
ref    = AutoModelForCausalLMWithValueHead.from_pretrained("./sft-checkpoint")  # frozen

ppo = PPOTrainer(
    config=PPOConfig(learning_rate=1.41e-5, batch_size=64, init_kl_coef=0.05,
                     target_kl=6.0, adap_kl_ctrl=True),
    model=policy, ref_model=ref, tokenizer=tok,
)

for batch in dataloader:
    responses = ppo.generate(batch["query_ids"], max_new_tokens=128)
    rewards   = rm(torch.cat([batch["query_ids"], responses], dim=-1)).logits[:, 0]
    stats     = ppo.step(batch["query_ids"], responses, rewards)
    # stats includes: mean_kl, clip_frac, value_loss — the three PPO diagnostics
```

Trzy rzeczy, które biblioteka robi dla Ciebie. `adap_kl_ctrl=True` implementuje harmonogram adaptacyjny-β: jeśli zaobserwowane KL przekracza `target_kl`, β podwaja się; jeśli poniżej połowy, β połówki. Model referencyjny jest zamrożony zgodnie z konwencją — nie wolno przypadkowo udostępniać parametrów `policy`. Głowa wartości opiera się na tym samym szkielecie co polityka (`AutoModelForCausalLMWithValueHead` dołącza skalarną głowę MLP), dlatego TRL raportuje oddzielnie `policy/kl` i `value/loss`.

## Pułapki

- **Nadmierna optymalizacja/hakowanie nagród.** RM jest niedoskonały; `π_θ` znajduje uzupełnienia kontradyktoryjne, które uzyskują wysoki wynik, ale są złe. Objawy: nagroda rośnie w nieskończoność, podczas gdy wynik oceny ludzkiej utrzymuje się na stałym poziomie lub spada. Poprawka: zatrzymaj się wcześniej, podnieś `β`, poszerz dane treningowe RM.
- **Hackowanie długości.** RM przeszkoleni w zakresie pomocnych odpowiedzi często pośrednio nagradzają długość. Polityka uczy się uzupełniania odpowiedzi. Remediacja: nagroda znormalizowana do długości lub RLAIF z RM uwzględniającym długość.
- **Zbyt mała RM.** RM musi być co najmniej tak duża jak polisa. Mały RM nie jest w stanie wiernie ocenić wyników polityki.
- **Trening KL.** Zbyt niskie β → hackowanie driftu i nagród. Zbyt wysokie β → polityka prawie się nie zmienia. Standardową sztuczką jest *adaptacyjne* β, którego celem jest stałe KL na krok.
- **Szum danych preferencji.** ~30% ludzkich etykiet jest zaszumionych lub niejednoznacznych. Skalibruj, ucząc RM na danych filtrowanych według zgodności lub użyj temperatury na BT.
- **Problemy niezgodne z zasadami.** Dane PPO po pierwszej epoce są nieco niezgodne z zasadami. Monitoruj ułamek klipu jak w lekcji 08.

## Użyj tego

RLHF w 2026 r. jest warstwowy:

| Warstwa | Cel | Metoda |
|-------|--------|--------|
| Przestrzeganie instrukcji, przydatność, nieszkodliwość | Wyrównanie | DPO (faza 10 · 08) preferowany zamiast RLHF-PPO. |
| Poprawność rozumowania (matematyka, kod) | Zdolność | GRPO z nagrodą weryfikatora (faza 9 · 12). |
| Zadania wieloetapowe o długim horyzoncie | Agent | PPO / GRPO z modelami nagród procesowych na etapach. |
| Zachowanie związane z bezpieczeństwem/odmową | Bezpieczeństwo | RLHF-PPO z oddzielnym RM bezpieczeństwa lub konstytucyjną AI. |
| Best-of-N przy wnioskowaniu | Szybkie wyrównanie | Użyj RM w czasie dekodowania; nie jest potrzebne żadne szkolenie polityczne. |
| Destylacja nagród | Obliczanie wnioskowania | Trenuj małą „głowę nagrody” na zamrożonym LM. |

RLHF była *metodą* w latach 2022–2024. W 2026 r. rurociągi dostosowania produkcji będą w pierwszej kolejności uwzględniać DPO, a jedynie PPO w przypadku etapów intensywnie wykorzystujących RM lub mających kluczowe znaczenie dla bezpieczeństwa.

## Wyślij to

Zapisz jako `outputs/skill-rlhf-architect.md`:

```markdown
---
name: rlhf-architect
description: Design an RLHF / DPO / GRPO alignment pipeline for a language model, including RM, KL, and data strategy.
version: 1.0.0
phase: 9
lesson: 9
tags: [rl, rlhf, alignment, llm]
---

Given a base LM, a target behavior (alignment / reasoning / refusal / agent), and a preference or verifier budget, output:

1. Stage. SFT? RM? DPO? GRPO? With justification.
2. Preference or verifier source. Humans, AI feedback, rule-based, unit-test-pass, or reward distillation.
3. KL strategy. Fixed β, adaptive β, or DPO (implicit KL).
4. Diagnostics. Mean KL, reward stability, over-optimization guard (holdout human eval).
5. Safety gate. Red-team set, refusal rate, safety RM separate from helpfulness RM.

Refuse to ship RLHF-PPO without a KL monitor. Refuse to use an RM smaller than the target policy. Refuse length-only rewards. Flag any pipeline that does not hold back a blind human-eval set as lacking over-optimization protection.
```

## Ćwiczenia

1. **Łatwe.** Trenuj model nagrody Bradleya-Terry'ego w `code/main.py` na 500 syntetycznych parach preferencji. Zmierz dokładność par na wystawionych 100 parach. Powinno przekraczać 90%.
2. **Średni.** Uruchom zabawkową pętlę PPO-RLHF za pomocą `β ∈ {0.0, 0.1, 1.0}`. Dla każdego wykreśl wynik RM w funkcji KL do odniesienia na podstawie aktualizacji. Który uruchamia nagrodę-hack?
3. **Trudne.** Zaimplementuj DPO (utratę wiarygodności preferencji w formie zamkniętej) na tych samych danych preferencji i porównaj z potokiem RLHF-PPO pod względem wykorzystanych obliczeń i osiągniętego końcowego wyniku RM.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| RLHF | „Wyrównanie RL” | Trójstopniowy rurociąg SFT + RM + PPO (Christiano 2017, Ouyang 2022). |
| Model nagrody (RM) | „Siatka punktacji” | Nauczona funkcja skalarna dopasowana do preferencji par za pośrednictwem Bradleya-Terry'ego. |
| Bradley-Terry | „Straty logistyczne parami” | `P(y_+ ≻ y_-) = σ(R(y_+) - R(y_-))`; standardowy cel RM. |
| Kara KL | „Trzymaj się blisko odniesienia” | `β · KL(π_θ \|\| π_ref)` w nagrodzie; narzędzie zapobiegające hakowaniu nagród. |
| Hakowanie nagród | „Prawo Goodharta” | Polityka wykorzystuje wady RM; objawy: nagroda w górę, ocena ludzka płaska. |
| RLAIF | „Preferencje oznaczone sztuczną inteligencją” | RLHF, gdzie etykiety pochodzą od innego LM, a nie od ludzi. |
| PRM | „Model nagrody procesu” | Ocenia częściowe kroki rozumowania; używane w potokach rozumowania. |
| Konstytucyjna sztuczna inteligencja | „Metoda antropiczna” | Preferencje generowane przez sztuczną inteligencję oparte na wyraźnych zasadach. |

## Dalsze czytanie

- [Christiano i in. (2017). Deep Reinforcement Learning from Human Preferences](https://arxiv.org/abs/1706.03741) – artykuł, który zapoczątkował RLHF.
- [Ouyang i in. (2022). InstructGPT — szkolenie modeli językowych w zakresie wykonywania instrukcji na podstawie opinii ludzi](https://arxiv.org/abs/2203.02155) — przepis na ChatGPT.
- [Stiennon i in. (2020). Nauka podsumowywania na podstawie opinii ludzi](https://arxiv.org/abs/2009.01325) — wcześniej RLHF do podsumowań.
- [Rafailov i in. (2023). Bezpośrednia optymalizacja preferencji](https://arxiv.org/abs/2305.18290) — DPO; niewypłacalność po RLHF w 2026 r.
- [Bai i in. (2022). Konstytucyjna sztuczna inteligencja: nieszkodliwość na podstawie opinii AI](https://arxiv.org/abs/2212.08073) — RLAIF i pętla samokrytyki.
- [Artykuł antropiczny RLHF (Bai i in. 2022). Szkolenie pomocnego i nieszkodliwego asystenta](https://arxiv.org/abs/2204.05862) – artykuł HH.
- [Biblioteka TRL Hugging Face](https://huggingface.co/docs/trl) — produkcja `RewardTrainer` i `PPOTrainer`. Przeczytaj źródło trenera, aby uzyskać szczegółowe informacje na temat adaptacyjnego KL i wartościowego nagłówka.
– [Przytulająca twarz — ilustrowanie uczenia się przez wzmacnianie na podstawie informacji zwrotnych od ludzi] (https://huggingface.co/blog/rlhf) autorstwa Lamberta, Castricato, von Werra, Havrilla — kanoniczny przewodnik po trzyetapowym rurociągu z diagramami.
- [von Werra i in. (2020). TRL: Nauka wzmacniania transformatora](https://github.com/huggingface/trl) — biblioteka; `examples/` zawiera kompleksowe skrypty RLHF dla Lamy, Mistrala i Qwen.
- [Sutton i Barto (2018). Ch. 17.4 — Projektowanie sygnałów nagrody](http://incompleteideas.net/book/RLbook2020.pdf) — widok hipotezy nagrody; niezbędny warunek wstępny myślenia o hackowaniu z nagrodami.