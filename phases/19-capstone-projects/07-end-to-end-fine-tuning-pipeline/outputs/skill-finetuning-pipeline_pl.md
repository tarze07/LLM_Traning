---

name: finetuning-pipeline
description: Uruchom powtarzalny potok danych do SFT i DPO, aby zapewnić precyzyjne dostrajanie danych za pomocą ablacji, kwantyzacji i karty modelu 2026 Model Openness Framework.
version: 1.0.0
phase: 19
lesson: 07
tags: [capstone, fine-tuning, axolotl, trl, dpo, grpo, vllm, eagle-3, mof]

---

Mając model podstawowy (Llama 3.3 8B, Qwen3 14B lub Gemma 3 12B) i zestaw danych specyficzny dla zadania, utwórz potok z jednym poleceniem, który generuje obsługiwany punkt końcowy i odtwarzalną kartę modelu.

Plan budowy:

1. Etap danych: deduplikacja Datatrove, filtr jakości w stylu Nemotron-CC, peeling Presidio PII, zaszczepiony podział pociągu/wartości.
2. Kontrola skażenia: MinHashLSH względem MMLU-Pro, MT-Bench-v2, RewardBench-2. Odrzuć przy nakładaniu się.
3. SFT: Axolotl v0.8 z ZeRO-3, Flash Attention 3, sekwencje spakowane, 2-3 epoki na 8xH100.
4. Strojenie preferencji: TRL 0,15 DPO (lub GRPO z weryfikowalnymi nagrodami) na 1 epokę, beta.
5. Kwantyzacja: GPTQ-INT4-Marlin + AWQ-INT4 + GGUF-Q4_K_M.
6. Podaj: vLLM 0.7 z dekodowaniem spekulatywnym EAGLE-3 (głowy robocze za pośrednictwem Red Hat Speculators lub SGLang SpecForge). Wdrożenie K8 z HPA w trybie oczekiwania w kolejce.
7. Ocena: lm-evaluation-harness, RewardBench-2, MT-Bench-v2, MMLU-Pro na całej bazie/tylko SFT/SFT+DPO/SFT+GRPO.
8. Bezpieczeństwo: przepustowość Llama Guard 4, filtr wyjściowy ShieldGemma-2.
9. Karta modelu w ramach Ram otwartości modelu 2026 z sekcjami dotyczącymi danych, szkoleń, ewaluacji, bezpieczeństwa i odtwarzalności.

Rubryka oceny:

| Waga | Kryterium | Pomiar |
|:-:|---|---|
| 25 | Wartość delta vs podstawa | Zmierzony zysk w MMLU-Pro, MT-Bench-v2, testy porównawcze specyficzne dla zadania |
| 20 | Powtarzalność rurociągu | Ponowne uruchomienie jednym poleceniem z identycznymi nasionami daje pasujące skróty |
| 20 | Higiena danych | Współczynnik deduplikacji, pokrycie PII, kontrola zanieczyszczeń zielona |
| 20 | Wydajność serwowania | tokeny/y w partii 1/8/32, akceptacja EAGLE-3, tokeny $/1M |
| 15 | Karta modelu + ocena bezpieczeństwa | Kompletność MOF 2026 + wskaźnik przepustowości Llama Guard 4 |

Twarde odrzucenia:

- Rurociągi, które pomijają kontrolę skażenia MinHash. Wyciekanie MMLU-Pro do treningu to klasyczny sposób na porażkę polegającą na oszustwie ewaluacyjnym.
- Trening przebiega bez dołączonych nasion i YAML. Powtarzalność jest trudnym wymaganiem.
- Obsługa bez EAGLE-3 lub równoważnej konfiguracji dekodowania spekulatywnego. Tokeny bazowe nie są słupkami z 2026 r.
- Brak oceny bezpieczeństwa. Każdy dostrojony statek ma współczynnik przepustowości Llama Guard 4.

Zasady odmowy:

- Odmów opublikowania karty modelu, która podaje wyniki testów porównawczych bez załączenia SHA lm-eval-harness.
- Odmówić dostrajania danych, których licencja zabrania modeli pochodnych. MF ocenia licencjonowanie danych.
- Odmów dostarczenia skwantowanego modelu bez pomiaru utraty jakości na matrycy eval.

Dane wyjściowe: repozytorium zawierające koordynatora potoku, YAML dla Lamy 3.3 8B + jedna alternatywna baza, dzienniki uruchomień SFT i DPO W&B, skwantowane artefakty, obsługiwany punkt końcowy, macierz ewaluacji z trzema wzorcami, ewaluację bezpieczeństwa, kartę modelu MOF 2026 oraz zapis trzech największych problemów z higieną danych, które wykryłeś i naprawiłeś.