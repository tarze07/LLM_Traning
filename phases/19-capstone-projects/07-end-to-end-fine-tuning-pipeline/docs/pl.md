# Capstone 07 — Kompleksowy proces dostrajania (dane przesyłane do SFT do DPO w celu udostępnienia)

> Model 8B wytrenowany na Twoich własnych danych, dostosowany do DPO według Twoich własnych preferencji, skwantowany, zdekodowany spekulatywnie i serwowany z wymiernymi tokenami $/1M. Otwarty stos 2026 to Axolotl v0.8, TRL 0.15, Unsloth do iteracji, GPTQ/AWQ/GGUF do kwantyzacji, vLLM 0.7 z EAGLE-3 do obsługi. Podstawą jest powtarzalne uruchomienie całego potoku — wejście YAML, obsługa punktu końcowego — i opublikowanie karty modelu w ramach modelu otwartości na rok 2026.

**Typ:** Zwieńczenie
**Języki:** Python (potok), YAML (konfiguracje), Bash (skrypty)
**Wymagania wstępne:** Faza 2 (ML), Faza 3 (DL), Faza 7 (transformatory), Faza 10 (LLM od podstaw), Faza 11 (inżynieria LLM), Faza 17 (infrastruktura), Faza 18 (bezpieczeństwo)
**Wykonywane fazy:** P2 · P3 · P7 · P10 · P11 · P17 · P18
**Czas:** 35 godzin

## Problem

Każdy poważny zespół zajmujący się sztuczną inteligencją w 2026 r. będzie stale monitorował proces dostrajania. Nie dlatego, że dostarczają podstawowy model graniczny, ale dlatego, że adaptacja na późniejszym etapie — domena SFT, DPO w stosunku do oznaczonych preferencji, destylowane wersje robocze do spekulatywnego dekodowania, obsługa z EAGLE-3 — jest miejscem, w którym wymierne zwycięstwa są. Axolotl v0.8 obsługuje konfiguracje SFT z wieloma GPU. TRL 0.15 obsługuje DPO i GRPO. Unsloth zapewnia szybką iterację z jednym procesorem graficznym. vLLM 0.7 z EAGLE-3 zwiększa przepustowość dekodowania 2-3 razy bez utraty jakości. Oprzyrządowanie działa; rzemiosło leży w YAML, higienie danych i dyscyplinie ewaluacyjnej.

Przeprowadzisz bazę 8B (Llama 3.3, Qwen3 lub Gemma 3) przez SFT, a następnie DPO na danych specyficznych dla zadania, dokonasz kwantyzacji przed podaniem i zmierzysz zyski względem lm-evaluation-harness, RewardBench-2, MT-Bench-v2 i MMLU-Pro. Przygotujesz kartę modelową w ramach Ram otwartości modelu 2026. Chodzi o powtarzalność — jedno polecenie powoduje ponowne uruchomienie całego potoku od końca do końca.

## Koncepcja

Rurociąg ma pięć etapów. **Dane**: dedup (MinHash / Datatrove), filtr jakości (klasyfikator w stylu Nemotron-CC), oczyszczanie danych osobowych, kontrola higieny Split pod kątem zanieczyszczenia publicznych testów porównawczych. **SFT**: Axolotl YAML, ZeRO-3 na 8xH100, harmonogram cosinus, upakowane sekwencje, 2-3 epoki. **DPO lub GRPO**: konfiguracja TRL, 1 epoka, pary preferencji albo oznaczone przez człowieka, albo ocenione przez model, tuning beta. **Kwantyzacja**: GPTQ + AWQ + GGUF dla elastyczności wdrażania. **Obsługa**: vLLM 0.7 z głowicami spekulacyjnymi EAGLE-3 (lub SGLang ze SpecForge), wdrożenie K8s, HPA w oczekiwaniu na kolejkę.

Ablacje są możliwe do dostarczenia: tylko SFT vs SFT+DPO vs SFT+GRPO w trzech testach porównawczych specyficznych dla zadania. Wskaźniki udostępniania: tokeny/s w partii 1/8/32, współczynnik akceptacji EAGLE-3, tokeny $/1M. Ocena bezpieczeństwa: współczynnik zdawalności Llama Guard 4. Karta modelu: oceny odchyleń, nasiona odtwarzalności, licencjonowanie danych.

## Architektura

```
raw data (HF datasets + internal)
    |
    v
Datatrove dedup + Nemotron-CC quality filter + PII scrub
    |
    v
split hygiene (MMLU-Pro contamination check)
    |
    v
Axolotl SFT config (YAML)  ---> 8xH100, ZeRO-3
    |
    v
TRL DPO / GRPO config       ---> 4xH100, 1 epoch
    |
    v
GPTQ + AWQ + GGUF quantize
    |
    v
vLLM 0.7 + EAGLE-3 speculative decoding
    |
    v
K8s deployment, HPA on queue-wait
    |
    v
lm-eval-harness + RewardBench-2 + MT-Bench-v2 + MMLU-Pro
    |
    v
model card (2026 MOF) + safety eval (Llama Guard 4)
```

## Stos

- Dane: Datatrove dla deduplikacji, klasyfikator Nemotron-CC dla jakości, Presidio dla PII
- Podstawa: Lama 3.3 8B, Qwen3 14B lub Gemma 3 12B
- SFT: Axolotl v0.8 z ZeRO-3, Flash Attention 3, spakowane sekwencje
- Strojenie preferencji: TRL 0,15 dla DPO lub GRPO; Unsloth dla iteracji z jedną kartą graficzną
- Kwantyzacja: GPTQ (Marlin), AWQ, GGUF poprzez llama.cpp
- Udostępnianie: vLLM 0.7 z dekodowaniem spekulatywnym EAGLE-3 (lub SGLang 0.4 + SpecForge)
- Eval: lm-evaluation-harness, RewardBench-2, MT-Bench-v2, MMLU-Pro
- Ocena bezpieczeństwa: Llama Guard 4, ShieldGemma-2
- Infrastruktura: Kubernetes + wtyczka urządzenia NVIDIA, HPA w oparciu o metrykę oczekiwania na kolejkę
- Obserwowalność: W&B do uczenia, Langfuse do wnioskowania

## Zbuduj to

1. **Potok danych.** Uruchom dedukcję Datatrove na surowym korpusie. Zastosuj klasyfikator jakości typu Nemotron-CC. Presidio usuwa informacje umożliwiające identyfikację. Napisz podział pociągu/val z wyraźnym materiałem siewnym.

2. **Sprawdzanie zanieczyszczeń.** Dla każdego podziału walidacyjnego oblicz MinHash względem zestawów testowych MMLU-Pro, MT-Bench-v2, RewardBench-2. Odrzuć wszelkie nakładanie się.

3. **Axolotl SFT.** YAML z ZeRO-3, FA3, pakowanie sekwencji. 2-3 epoki na 8xH100. Zaloguj się do W&B.

4. **TRL DPO / GRPO.** Weź punkt kontrolny SFT, uruchom jedną epokę DPO na parach preferencji (lub GRPO z weryfikowalną nagrodą za matematykę/kod). Przeszukaj wersję beta.

5. **Kwantyzacja.** Utwórz trzy ilości: GPTQ-INT4-Marlin, AWQ-INT4, GGUF-Q4_K_M dla llama.cpp. Rozmiar rekordu i nominalna przepustowość.

6. **Podawaj z dekodowaniem spekulatywnym.** Konfiguracja vLLM 0.7 z szefami projektów EAGLE-3 przeszkolonymi przez Red Hat Speculators. Zmierz współczynnik akceptacji i opóźnienie końcowe w partii 1/8/32. Zgłoś tokeny $/1M w porównaniu z Anthropic/OpenAI w tej samej ocenie.

7. **Macierz Eval.** Uruchom lm-eval-harness, RewardBench-2, MT-Bench-v2, MMLU-Pro na podstawie, tylko SFT, SFT+DPO, SFT+GRPO. Stwórz tabelę.

8. **Ocena bezpieczeństwa.** Szybkość przejścia Llama Guard 4 na zestawie deweloperskim. Filtr wyjściowy ShieldGemma-2.

9. **Karta modelu.** Szablon MOF 2026: dane, szkolenia, ewaluacja, bezpieczeństwo, licencja, sekcja odtwarzalności z YAML i zatwierdzonymi SHA.

## Użyj tego

```
$ ./pipeline.sh config/llama3.3-8b-domainX.yaml
[data]    300k deduped, 12k filtered, 280k accepted (seed=7)
[SFT]     3 epochs, 8xH100, 6h12m, val loss 1.42 -> 1.03
[DPO]     1 epoch, beta=0.08, 4xH100, 1h40m
[quant]   GPTQ-INT4 4.6 GB, AWQ-INT4 4.8 GB, GGUF-Q4_K_M 5.1 GB
[serve]   vLLM 0.7, EAGLE-3 acceptance 0.74, p99 126ms @ bs=8
[eval]    MMLU-Pro +3.2, MT-Bench-v2 +0.41, RewardBench-2 +0.08
[card]    model-card.md generated under 2026 MOF
```

## Wyślij to

`outputs/skill-finetuning-pipeline.md` opisuje element dostarczany. Pojedyncze polecenie uruchamia dane przez SFT, przez DPO, przez quant, poprzez eval, i emituje kartę modelu + obsługiwany punkt końcowy.

| Waga | Kryterium | Jak to się mierzy |
|:-:|---|---|
| 25 | Wartość delta vs podstawa | Zmierzony zysk z zadań docelowych (MMLU-Pro, MT-Bench-v2, specyficzne dla zadania) |
| 20 | Powtarzalność rurociągu | Jedno polecenie powtarza od końca do końca z identycznymi nasionami |
| 20 | Higiena danych | Współczynnik deduplikacji, pokrycie PII, kontrola zanieczyszczeń zielona |
| 20 | Wydajność serwowania | tokenów/s przy bs=1/8/32, współczynnik akceptacji EAGLE-3, tokeny $/1M |
| 15 | Karta modelu + ocena bezpieczeństwa | Kompletność MOF 2026 + wskaźnik przepustowości Llama Guard 4 |
| **100** | | |

## Ćwiczenia

1. Uruchom tylko SFT vs SFT+DPO vs SFT+GRPO w tym samym benchmarku specyficznym dla zadania. Zgłoś, która metoda preferencji wygrywa i o ile.

2. Zamień Lamę 3.3 8B na Qwen3 14B. Zmierz tokeny $/1M w dopasowanej jakości.

3. Zmierz współczynnik akceptacji EAGLE-3 na danych domeny w porównaniu z ogólnym ShareGPT. Zgłoś różnicę i jej znaczenie dla budżetów opóźnień.

4. Wstrzyknij 1% zanieczyszczeń (wyciek odpowiedzi MMLU-Pro do danych treningowych) i powtórz ocenę. Oglądaj nierealistyczne skoki celności MMLU-Pro. Zbuduj bramkę CI sprawdzającą zanieczyszczenia, która to wykryje.

5. Dodaj LoRA SFT jako alternatywę dla pełnego dostrajania. Zmierz różnicę w jakości przy 10-krotnie mniejszej pamięci.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| Aksolotl | „Trener SFT” | Zunifikowany trener oparty na YAML dla SFT, DPO i destylacji |
| TRL | „Tuner preferencji” | Biblioteka Hugging Face dla DPO, GRPO, PPO na LLM |
| GRPO | „Optymalizacja polityki względem grupy” | Przepis na RL DeepSeek R1 z weryfikowalnymi nagrodami |
| ORZEŁ-3 | „Spekulacyjny projekt dekodowania” | Draft reszki, które przewidują N żetonów na przyszłość; vLLM weryfikuje model docelowy |
| MF | „Ramy otwartości modelu” | Standard 2026 dotyczący klasyfikacji wydań modeli na podstawie danych, kodu i licencji |
| Kontrola skażenia | „Podzielna higiena” | Wykrywanie wycieku zestawu testowego do treningu w oparciu o MinHash |
| Wskaźnik akceptacji | „Metryka EAGLE / MTP” | Część opracowanych tokenów, które model docelowy akceptuje |

## Dalsze czytanie

- [Dokumentacja Axolotl](https://axolotl-ai-cloud.github.io/axolotl/) — referencyjny trener SFT / DPO
- [Dokumentacja TRL](https://huggingface.co/docs/trl) — implementacje referencyjne DPO i GRPO
- [Unsloth](https://github.com/unslothai/unsloth) — odniesienie do iteracji z jedną kartą graficzną
- [Artykuł DeepSeek R1 (arXiv:2501.12948)](https://arxiv.org/abs/2501.12948) — Metodologia GRPO
- [dokumentacja vLLM + EAGLE-3](https://docs.vllm.ai) — referencyjny stos obsługujący
- [SGLang SpecForge](https://github.com/sgl-project/SpecForge) — alternatywny trener dekodowania spekulatywnego
– [Model Openness Framework 2026](https://isocpp.org/) — standard oceniania w wersji otwartej
- [lm-evaluation-harness](https://github.com/EleutherAI/lm-evaluation-harness) — kanoniczny moduł oceny