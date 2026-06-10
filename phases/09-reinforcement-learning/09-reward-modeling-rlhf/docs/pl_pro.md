# Modelowanie nagród i RLHF

> Ludzie nie potrafią napisać funkcji nagrody dla „dobrej odpowiedzi asystenta", ale potrafią porównać dwie odpowiedzi i wskazać lepszą. Wystarczy dopasować model nagrody do takich porównań, a następnie użyć go do optymalizacji modelu językowego. Christiano 2017. InstructGPT 2022. Przepis, który przekształcił GPT-3 w ChatGPT. W 2026 r. jest on w znacznej mierze zastępowany przez DPO, lecz leżąca u jego podstaw intuicja pozostaje aktualna.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 5 · 05 (Sentyment), Faza 9 · 08 (PPO)
**Czas:** ~45 minut

## Problem

Wytrenowałeś model językowy pod kątem przewidywania następnego tokenu. Pisze gramatycznie poprawnie, ale kłamie, produkuje obszerne, niepotrzebne elaboracje i nie potrafi odmówić. Częstsze trenowanie wstępne tego nie naprawi — problem tkwi w danych internetowych, a nie w metodzie uczenia.

Potrzebujesz *skalarnej nagrody*, która powie, że „odpowiedź A jest lepsza niż odpowiedź B dla polecenia X". Ręczne napisanie takiej funkcji nagrody jest niemożliwe — „przydatność" nie daje się wyrazić jako zamknięta formuła na tokenach. Natomiast ludzie bez trudu porównują dwa wyniki i wskazują preferowany. Takie etykiety można zbierać tanio i na dużą skalę.

RLHF (Christiano i in. 2017; Ouyang i in. 2022) przekształca preferencje w model nagrody, a następnie optymalizuje LM przez PPO względem tej nagrody. Cały potok składa się z trzech kroków: SFT → RM → PPO. To właśnie ten przepis stoi za ChatGPT, Claude, Gemini i wszystkimi innymi dostrojonymi modelami językowymi z lat 2023–2025.

W 2026 r. krok PPO jest w większości zastępowany przez DPO (faza 10 · 08), który jest tańszy i niemal równie skuteczny przy dostrajaniu wyrównania. Jednak sam *model nagrody* nadal stanowi fundament każdego próbnika Best-of-N, każdego potoku RL z weryfikowalnymi nagrodami i każdego modelu wnioskowania korzystającego z procesowego modelu nagrody. Kto rozumie RLHF, ten rozumie cały stos wyrównania.

## Koncepcja

![Trzyetapowe RLHF: SFT, szkolenie RM na prefach w parach, PPO z karą KL](../assets/rlhf.svg)

**Etap 1: Nadzorowane dostrajanie (SFT).** Punktem wyjścia jest wstępnie wytrenowany model bazowy. Dostrajamy go na demonstracjach docelowego zachowania pisanych przez ludzi (odpowiedzi zgodne z instrukcjami, pomocne odpowiedzi itp.). Wynikiem jest model `π_SFT`, który wykazuje *pożądane zachowanie*, lecz nadal dysponuje nieograniczoną przestrzenią działania.

**Etap 2: Trenowanie modelu nagrody.**

- Zbierz pary odpowiedzi `(y_+, y_-)` na podpowiedź `x`, oznaczone przez ludzi jako „y_+ jest lepsze niż y_-".
- Wytrenuj model nagrody `R_φ(x, y)` tak, aby przypisywał wyższe wyniki odpowiedziom `y_+`.
- Funkcja straty: **logistyczna strata parowa Bradley-Terry**:

  `L(φ) = -E[ log σ(R_φ(x, y_+) - R_φ(x, y_-)) ]`

  σ oznacza funkcję sigmoidalną. Różnica nagród odpowiada log-szansom preferencji. Model BT jest standardem od 1952 r. i dominuje we współczesnych implementacjach RLHF.

- `R_φ` jest zazwyczaj inicjowany z modelu SFT z dodaną skalarną głową liniową. Architektura transformatora pozostaje ta sama; pojedyncza warstwa liniowa produkuje wartość nagrody.

**Etap 3: PPO z modelem nagrody i karą KL.**

- Zainicjuj trening polityki `π_θ` z `π_SFT`. Zachowaj zamrożoną kopię referencyjną `π_ref = π_SFT`.
- Całkowita nagroda na końcu odpowiedzi `y`:

  `r_total(x, y) = R_φ(x, y) - β · KL(π_θ(·|x) || π_ref(·|x))`

  Kara KL zapobiega zbytniemu odchyleniu `π_θ` od `π_SFT` — pełni rolę *regulatora*, nie twardego ograniczenia obszaru zaufania. Typowa wartość `β` wynosi `0.01`–`0.05`.
- Uruchom PPO (lekcja 08) z tą nagrodą. Korzyści są obliczane na podstawie trajektorii na poziomie tokenu, ale RM ocenia wyłącznie kompletną odpowiedź.

**Dlaczego kara KL jest niezbędna?** Bez niej PPO chętnie odkrywa strategie oszukiwania modelu nagrody — RM był trenowany tylko na uzupełnieniach w rozkładzie. Odpowiedź spoza rozkładu może uzyskać wyższy wynik niż cokolwiek napisanego przez człowieka. Kara KL utrzymuje `π_θ` blisko rozkładu, na którym trenowano RM. To najważniejszy parametr w całym RLHF.

**Stan na rok 2026:**

- **DPO** (Rafailov 2023): algebraiczne, zamknięte rozwiązanie łączy etapy 2 i 3 w jedną nadzorowaną stratę opartą na danych preferencji. Bez RM, bez PPO. Porównywalna jakość na testach wyrównania przy ułamku kosztu obliczeniowego. Omówione w fazie 10 · 08.
- **GRPO** (DeepSeek 2024–2025): PPO z linią bazową obliczaną grupowo zamiast krytykiem; nagroda pochodzi od *weryfikatora* (wykonanie kodu / zgodność odpowiedzi matematycznej) zamiast od RM trenowanego przez ludzi. Dominująca metoda dla modeli wnioskowania. Omówiona w fazie 9 · 12.
- **Procesowe modele nagrody (PRM):** oceniają częściowe rozwiązania (każdy krok wnioskowania); stosowane zarówno w wariantach RLHF, jak i GRPO.
- **Konstytucyjna SI / RLAIF:** dostrojony LLM generuje preferencje zamiast ludzi, co pozwala skalować budżet danych preferencyjnych.

## Zbuduj to

W tej lekcji używamy małych, syntetycznych „podpowiedzi" i „odpowiedzi" reprezentowanych jako ciągi znaków. RM to liniowa funkcja punktująca oparta na reprezentacji worka tokenów. Nie ma tu prawdziwego LLM — liczy się *kształt* potoku, nie skala. Patrz `code/main.py`.

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

W rzeczywistym RLHF to miejsce zajmują etykiety ludzkie. Struktura danych — `(prompt, preferred_response, rejected_response)` — pozostaje identyczna.

### Krok 2: Model nagrody Bradleya-Terry'ego

Wynik liniowy: `R(x, y) = w · bag(y)`. Trenujemy, minimalizując parową stratę logarytmiczną BT:

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

Po kilkuset aktualizacjach wektor `w` przypisuje dodatnie wagi tokenom dobrych słów, a ujemne — złych.

### Krok 3: Polityka wzorowana na PPO z modelem nagrody

Nasza uproszczona polityka generuje pojedynczy token ze słownika. Oceniamy token za pomocą RM, obliczamy `log π_θ(token | prompt)`, dodajemy karę KL względem polityki referencyjnej i stosujemy przycięty surogat PPO.

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

Śledź `KL(π_θ || π_ref)` przy każdej aktualizacji. Jeśli wartość przekroczy `~5–10`, polityka zbyt mocno oddaliła się od `π_SFT` — należy zwiększyć `β` lub liczyć się z początkiem zjawiska oszukiwania modelu nagrody. To najważniejsza diagnostyka w produkcyjnym RLHF.

### Krok 5: przepis produkcyjny z TRL

Gdy zrozumiesz uproszczony potok, poniżej znajdziesz tę samą pętlę w wersji bibliotecznej. [TRL](https://huggingface.co/docs/trl) od Hugging Face to implementacja referencyjna — `RewardTrainer` dla etapu 2 oraz `PPOTrainer` (z wbudowaną karą KL względem modelu referencyjnego) dla etapu 3.

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

Biblioteka wykonuje za nas trzy rzeczy. `adap_kl_ctrl=True` wdraża adaptacyjny harmonogram β: gdy obserwowane KL przekracza `target_kl`, β się podwaja; gdy spada poniżej połowy wartości docelowej, β maleje o połowę. Model referencyjny jest zamrożony zgodnie z konwencją — parametry polityki nie mogą być przypadkowo współdzielone. Głowa wartości opiera się na tym samym szkielecie co polityka (`AutoModelForCausalLMWithValueHead` dołącza skalarną głowę MLP), dlatego TRL raportuje oddzielnie `policy/kl` i `value/loss`.

## Pułapki

- **Nadmierna optymalizacja / oszukiwanie modelu nagrody.** RM jest niedoskonały; `π_θ` odkrywa odpowiedzi, które uzyskują wysoki wynik, lecz faktycznie są złe. Objawy: nagroda rośnie, tymczasem ocena ludzka pozostaje płaska lub spada. Remedium: wczesne zatrzymanie, podniesienie `β`, rozszerzenie danych treningowych RM.
- **Oszukiwanie przez długość.** Modele nagrody trenowane na pomocnych odpowiedziach często pośrednio premiują dłuższe teksty. Polityka uczy się wówczas rozbudowywać odpowiedzi bez potrzeby. Remedium: nagroda normalizowana długością lub RLAIF z RM uwzględniającym długość.
- **Zbyt mały RM.** Model nagrody musi być co najmniej tak duży jak optymalizowana polityka. Mniejszy RM nie jest w stanie rzetelnie oceniać jej wyników.
- **Strojenie KL.** Zbyt niskie β prowadzi do dryfu i oszukiwania nagród; zbyt wysokie β sprawia, że polityka prawie się nie zmienia. Standardowym rozwiązaniem jest *adaptacyjne* β dążące do stałej wartości KL na krok.
- **Szum w danych preferencji.** Około 30% ludzkich etykiet jest zaszumionych lub niejednoznacznych. Warto kalibrować RM, ucząc go na danych filtrowanych według zgodności między adnotatorami lub stosując temperaturę w funkcji straty BT.
- **Problemy ze zgodnością zasad.** Dane PPO po pierwszej epoce są częściowo niezgodne z zasadami. Monitoruj ułamek przycinania jak w lekcji 08.

## Zastosowania

RLHF w 2026 r. funkcjonuje jako architektura warstwowa:

| Warstwa | Cel | Metoda |
|-------|--------|--------|
| Przestrzeganie instrukcji, przydatność, nieszkodliwość | Wyrównanie | DPO (faza 10 · 08) preferowany zamiast RLHF-PPO. |
| Poprawność rozumowania (matematyka, kod) | Zdolność | GRPO z nagrodą weryfikatora (faza 9 · 12). |
| Zadania wieloetapowe o długim horyzoncie | Agenty | PPO / GRPO z procesowymi modelami nagrody na poszczególnych etapach. |
| Zachowanie związane z bezpieczeństwem i odmową | Bezpieczeństwo | RLHF-PPO z osobnym RM bezpieczeństwa lub konstytucyjną SI. |
| Best-of-N przy wnioskowaniu | Szybkie wyrównanie | RM stosowany w czasie dekodowania; bez potrzeby trenowania polityki. |
| Destylacja nagród | Redukcja kosztu wnioskowania | Trenowanie małej „głowy nagrody" na zamrożonym LM. |

RLHF był *metodą wiodącą* w latach 2022–2024. W 2026 r. produkcyjne potoki dostrajania sięgają przede wszystkim po DPO, a po PPO tylko w przypadku etapów intensywnie korzystających z RM lub krytycznych dla bezpieczeństwa.

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

1. **Łatwe.** Wytrenuj model nagrody Bradleya-Terry'ego w `code/main.py` na 500 syntetycznych parach preferencji. Zmierz dokładność parową na wydzielonym zbiorze 100 par. Powinna przekraczać 90%.
2. **Średnie.** Uruchom uproszczoną pętlę PPO-RLHF dla `β ∈ {0.0, 0.1, 1.0}`. Dla każdej wartości narysuj wykres wyniku RM w funkcji KL względem modelu referencyjnego w kolejnych aktualizacjach. Przy której wartości dochodzi do oszukiwania nagrody?
3. **Trudne.** Zaimplementuj DPO (zamkniętą stratę wiarygodności preferencji) na tych samych danych i porównaj z potokiem RLHF-PPO pod względem zużytych zasobów obliczeniowych i osiągniętego końcowego wyniku RM.

## Kluczowe terminy

| Termin | Co się mówi | Co to naprawdę oznacza |
|------|-----------------|----------------------|
| RLHF | „Wyrównanie przez RL" | Trzystopniowy potok SFT + RM + PPO (Christiano 2017, Ouyang 2022). |
| Model nagrody (RM) | „Sieć punktująca" | Wyuczona funkcja skalarna dopasowana do parowych preferencji metodą Bradleya-Terry'ego. |
| Bradley-Terry | „Parowa strata logistyczna" | `P(y_+ ≻ y_-) = σ(R(y_+) - R(y_-))`; standardowa funkcja celu RM. |
| Kara KL | „Trzymaj się blisko modelu referencyjnego" | `β · KL(π_θ \|\| π_ref)` w nagrodzie; mechanizm zapobiegający oszukiwaniu modelu nagrody. |
| Oszukiwanie nagród | „Prawo Goodharta" | Polityka eksploatuje słabości RM; objawy: nagroda rośnie, ocena ludzka stoi w miejscu. |
| RLAIF | „Preferencje etykietowane przez SI" | RLHF, w którym etykiety pochodzą od innego LLM, nie od ludzi. |
| PRM | „Procesowy model nagrody" | Ocenia częściowe kroki wnioskowania; stosowany w potokach rozumowania. |
| Konstytucyjna SI | „Metoda Anthropic" | Preferencje generowane przez SI na podstawie jawnych zasad. |

## Dalsza lektura

- [Christiano i in. (2017). Deep Reinforcement Learning from Human Preferences](https://arxiv.org/abs/1706.03741) – artykuł, który zapoczątkował RLHF.
- [Ouyang i in. (2022). InstructGPT — szkolenie modeli językowych w zakresie wykonywania instrukcji na podstawie opinii ludzi](https://arxiv.org/abs/2203.02155) — przepis na ChatGPT.
- [Stiennon i in. (2020). Nauka podsumowywania na podstawie opinii ludzi](https://arxiv.org/abs/2009.01325) — wcześniejsze zastosowanie RLHF do streszczania tekstów.
- [Rafailov i in. (2023). Bezpośrednia optymalizacja preferencji](https://arxiv.org/abs/2305.18290) — DPO; następca RLHF dominujący w 2026 r.
- [Bai i in. (2022). Konstytucyjna sztuczna inteligencja: nieszkodliwość na podstawie opinii AI](https://arxiv.org/abs/2212.08073) — RLAIF i pętla samokrytyki.
- [Bai i in. (2022). Szkolenie pomocnego i nieszkodliwego asystenta](https://arxiv.org/abs/2204.05862) — artykuł HH od Anthropic.
- [Biblioteka TRL Hugging Face](https://huggingface.co/docs/trl) — produkcyjna implementacja `RewardTrainer` i `PPOTrainer`. Warto przeczytać kod trenerów, aby zrozumieć szczegóły adaptacyjnego KL i głowy wartości.
- [Lambert, Castricato, von Werra, Havrilla — ilustrowanie uczenia przez wzmacnianie na podstawie opinii ludzi](https://huggingface.co/blog/rlhf) — kanoniczny przewodnik po trójstopniowym potoku z diagramami.
- [von Werra i in. (2020). TRL: Nauka wzmacniania transformatora](https://github.com/huggingface/trl) — biblioteka; katalog `examples/` zawiera kompletne skrypty RLHF dla Llamy, Mistrala i Qwen.
- [Sutton i Barto (2018). Rozdz. 17.4 — Projektowanie sygnałów nagrody](http://incompleteideas.net/book/RLbook2020.pdf) — perspektywa hipotezy nagrody; lektura obowiązkowa przed myśleniem o oszukiwaniu nagród.
