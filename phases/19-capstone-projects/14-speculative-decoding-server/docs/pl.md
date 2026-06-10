# Capstone 14 — Serwer wnioskowania spekulatywnego dekodowania

> EAGLE-3 w vLLM 0.7 zapewnia przepustowość 2,5-3x w rzeczywistym ruchu. P-EAGLE (AWS 2026) jeszcze bardziej popchnęło równoległe spekulacje. SpecForge firmy SGLang przeszkolił szefów ciągnięcia na dużą skalę. Centrum Spekulantów firmy Red Hat opublikowało dostosowane wersje robocze popularnych modeli otwartych. TensorRT-LLM sprawił, że dekodowanie spekulacyjne stało się najwyższej klasy na platformie NVIDIA. Stos obsługujący produkcję na rok 2026 to vLLM lub SGLang z wersjami roboczymi z rodziny EAGLE, kwantyzacją FP8 lub INT4 i HPA w oczekiwaniu na kolejkę. To zwieńczenie ma obsługiwać dwa otwarte modele przy podstawowej przepustowości 2,5x+ z pełnym raportem dotyczącym opóźnień końcowych.

**Typ:** Zwieńczenie
**Języki:** Python (obsługa), C++ / CUDA (inspekcja jądra), YAML (konfiguracje)
**Wymagania wstępne:** Faza 3 (głębokie uczenie), Faza 7 (transformatory), Faza 10 (LLM od podstaw), Faza 17 (infrastruktura)
**Wykonywane fazy:** P3 · P7 · P10 · P17
**Czas:** 30 godzin

## Problem

Dekodowanie spekulatywne stało się towarem w 2026 r. W wersji roboczej EAGLE-3 trenuje się na ukrytych stanach modelu docelowego i przewiduje N tokenów na przyszłość; model docelowy sprawdza w jednym przebiegu. Wskaźniki akceptacji na poziomie 60-80% przekładają się na 2-3 razy większą przepustowość typu end-to-end. vLLM 0.7 integruje to natywnie. SGLang + SpecForge zapewnia potok szkoleniowy. Firma Red Hat's Speculators publikuje dostosowane wersje robocze dla Llama 3.3 70B, Qwen3-Coder-30B MoE, GPT-OSS-120B.

Jednostka służy do serwowania, a nie model. Wskaźnik akceptacji zmienia się wraz z rozkładem ruchu (ShareGPT vs kod vs dane domeny). Opóźnienie ogona w przypadku odrzucenia jest gorsze niż bez spekulacji — należy zgłosić p99 przy wielu rozmiarach partii, a nie tylko tokenach w stanie ustalonym/s. Koszt 1 miliona tokenów w porównaniu z Anthropic / OpenAI API to dźwignia wiarygodności.

## Koncepcja

Dekodowanie spekulatywne ma dwie warstwy. Model **szkicowy** (głowa EAGLE-3, ngram lub mniejszy model dostosowany do celu) proponuje k żetonów kandydatów na krok. Model **docelowy** weryfikuje wszystkie k w jednym przebiegu; dowolny zaakceptowany przedrostek zastępuje zachłanną ścieżkę. Wskaźnik akceptacji zależy od dostosowania wersji roboczej do docelowej i dystrybucji danych wejściowych.

EAGLE-3 pokonuje wersje ngram w większości ruchu. P-EAGLE prowadzi równoległe spekulacje dotyczące drzew o większym zanurzeniu. Kompromis: opóźnienie P99 w przypadku odrzucenia jest większe, ponieważ przepustka weryfikacyjna jest większa. Aby to ujawnić, konfiguracja udostępniania musi zgłaszać opóźnienia w zależności od wielkości partii.

Wdrożenie to Kubernetes. vLLM 0.7 uruchamia jedną replikę na procesor graficzny lub fragment równoległy tensora. HPA automatycznie skaluje się podczas oczekiwania w kolejce, a nie procesora. Kwanty FP8 (Marlin) i INT4 (AWQ) utrzymują pamięć GPU w kopercie H100 / H200. Kompleksowy raport obejmuje przepustowość, współczynnik akceptacji, p50/p99 w partii 1/8/32 i tokeny $/1M.

## Architektura

```
request ingress
    |
    v
vLLM server (0.7) or SGLang (0.4)
    |
    +-- draft: EAGLE-3 heads | P-EAGLE parallel | ngram fallback
    +-- target: Llama 3.3 70B | Qwen3-Coder-30B | GPT-OSS-120B
    |     quantized FP8-Marlin or INT4-AWQ
    |
    v
verify pass: batch k draft tokens through target
    |
    v (accept prefix; resample for rejected suffix)
    v
token stream back to client
    |
    v
Prometheus metrics: throughput, acceptance rate, queue wait, latency p50/p99
    |
    v
HPA on queue-wait metric
```

## Stos

- Podawanie: vLLM 0,7 lub SGLang 0,4
- Metody spekulacyjne: głowice robocze EAGLE-3, spekulacje równoległe P-EAGLE, rezerwa ngram
- Szkolenie draftowe: SpecForge (SGLang) lub Red Hat Speculators
- Modele docelowe: Lama 3.3 70B, Qwen3-Coder-30B MoE, GPT-OSS-120B
- Kwantyzacja: FP8 (Marlin), INT4 AWQ
- Wdrożenie: Kubernetes + wtyczka urządzenia NVIDIA; HPA na podstawie metryki oczekiwania w kolejce
- Eval: ShareGPT, MT-Bench-v2, GSM8K, HumanEval do pomiaru akceptacji rozprzestrzeniania się domeny
- Odniesienie: dekodowanie spekulacyjne TensorRT-LLM dla linii bazowej dostawcy

## Zbuduj to

1. **Przygotowanie modelu docelowego** Wybierz Lamę 3.3 70B. Kwantyzacja do 8PR poprzez Marlin. Wdróż w wersji vLLM 0,7 na 1xH100 (lub 2x równolegle tensorowo).

2. **Źródło wersji roboczej.** Wyciągnij wyrównaną głowicę zanurzeniową EAGLE-3 od Red Hat Speculators (lub wytrenuj ją za pośrednictwem SpecForge). Załaduj do konfiguracji dekodowania spekulatywnego vLLM.

3. **Liczby bazowe.** Przed spekulacjami: tokeny/y w partii 1/8/32, opóźnienie p50/p99, wykorzystanie procesora graficznego. Publikować.

4. **Włącz EAGLE-3.** Odwróć konfigurację; ponownie przeprowadzić ten sam test porównawczy. Przyspieszenie raportu, współczynnik akceptacji, delta opóźnienia ogona p99.

5. **P-EAGLE.** Włącz równoległą spekulację; zmierz głębsze zanurzenie drzewa w porównaniu z seryjnym EAGLE-3. Zgłoś zmianę, w której P-EAGLE pomaga, a nie szkodzi.

6. **Ruch domeny.** Uruchom ShareGPT vs. HumanEval w porównaniu z ruchem specyficznym dla domeny na tym samym serwerze. Zmierz współczynnik akceptacji na dystrybucję. Zidentyfikuj, kiedy dryfują przeciągi.

7. **Drugi model docelowy.** Uruchom ten sam potok na Qwen3-Coder-30B MoE. Wersja robocza jest trudniejsza (szum routingu MoE). Raport.

8. **K8s HPA.** Wdróż pod K8 ze śledzeniem HPA `queue_wait_ms`. Zademonstruj skalowanie w poziomie przy trzykrotnym obciążeniu.

9. **Porównanie kosztów.** Oblicz tokeny $/1M w porównaniu z Anthropic Claude Sonnet 4.7 i OpenAI GPT-5.4 w tej samej ocenie. Publikować.

## Użyj tego

```
$ curl https://infer.example.com/v1/chat/completions -d '{"messages":[...]}'
[serve]     vLLM 0.7, Llama 3.3 70B FP8, EAGLE-3 active
[decode]    bs=8, accepted_tokens_per_step=3.2, acceptance_rate=0.76
[latency]   first-token 42ms, full-response 980ms (620 tokens)
[cost]      $0.34 per 1M output tokens at sustained throughput
```

## Wyślij to

`outputs/skill-inference-server.md` opisuje element dostarczany. Zmierzony stos obsługujący z dekodowaniem spekulacyjnym, pełnym raportem porównawczym i wdrożeniem K8.

| Waga | Kryterium | Jak to się mierzy |
|:-:|---|---|
| 25 | Zmierzone przyspieszenie w porównaniu z wartością bazową | Ponad 2,5x przepustowość przy dopasowanej jakości w dwóch modelach |
| 20 | Wskaźnik akceptacji dla realistycznego ruchu | Raport dotyczący współczynnika akceptacji poszczególnych dystrybucji |
| 20 | Dyscyplina opóźnienia ogona P99 | p99 w partii 1/8/32 ze spekulacjami i bez |
| 20 | Operacje | Wdrożenie K8, HPA w kolejce, oczekiwanie, wdrożenie płynne |
| 15 | Opis i metodologia | Jasne wyjaśnienie, co się zmieniło i dlaczego |
| **100** | | |

## Ćwiczenia

1. Zmierz spadek współczynnika akceptacji, gdy wersja robocza jest o jedną wersję niższa od wersji docelowej (np. dryf Lamy 3.3 -> 3.4). Zbuduj alert monitorujący.

2. Zaimplementuj rozwiązanie ngram-fallback: jeśli akceptacja EAGLE-3 spadnie poniżej progu, przełącz się na wersje robocze ngram. Zgłoś poprawę niezawodności.

3. Przeprowadź kontrolowany eksperyment MoE: ten sam Qwen3-Coder-30B z wstrzykniętym szumem routingu vs. bez. Zmierz czułość akceptacji projektu.

4. Rozszerz do H200 (141 GB). Zgłoś uzyskany zapas wielkości modelu na replikę i czy możesz podać niekwantyzowaną Lamę 3.3 70B.

5. Test porównawczy dekodowania spekulatywnego TensorRT-LLM na tym samym sprzęcie H100. Zgłoś, gdzie wygrywa vs vLLM.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| Projekt modelu | „Spekulant” | Mały model, który proponuje N tokenów dla celu do weryfikacji |
| ORZEŁ-3 | „Projekt architektury 2026” | Szef pociągu przeszkolony w zakresie docelowych stanów ukrytych; ~75% akceptacji |
| P-ORZEŁ | „Spekulacje równoległe” | Drzewo gałęzi projektowych zweryfikowanych w jednym przebiegu docelowym |
| Wskaźnik akceptacji | „Wskaźnik trafień” | Część opracowanych tokenów zaakceptowanych bez ponownego próbkowania |
| Kwantyzacja | "8PR/INT4" | Obciążniki o niższej precyzji, aby zmieścić więcej modeli w pamięci GPU |
| Kolejka czeka | „Miernik HPA” | Czas oczekiwania żądania w kolejce oczekującej przed rozpoczęciem wnioskowania |
| Centrum spekulantów | „Wyrównane wersje robocze” | Centrum wersji roboczych Red Hat Neural Magic dla popularnych modeli otwartych |

## Dalsze czytanie

- [dokumentacja vLLM EAGLE i P-EAGLE](https://docs.vllm.ai) — referencyjny stos obsługujący
- [P-EAGLE (AWS 2026)](https://aws.amazon.com/blogs/machine-learning/p-eagle-faster-llm-inference-with-parallel-speculative-decoding-in-vllm/) — dokument dotyczący równoległego dekodowania spekulatywnego + integracja
- [SGLang SpecForge](https://github.com/sgl-project/SpecForge) — proces szkolenia kierowników roboczych
– [Red Hat Spekulanci](https://github.com/neuralmagic/speculators) — dostosowane centrum robocze
- [Dekodowanie spekulatywne TensorRT-LLM](https://nvidia.github.io/TensorRT-LLM/) — alternatywa dostawcy
- [Architektura obsługująca Fireworks.ai](https://fireworks.ai/blog) — odniesienie komercyjne
- [praca EAGLE-3 (arXiv:2503.01840)](https://arxiv.org/abs/2503.01840) — praca metodyczna
- [repozytorium vLLM](https://github.com/vllm-project/vllm) — kod i testy porównawcze