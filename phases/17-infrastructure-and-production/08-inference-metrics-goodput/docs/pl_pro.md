# Metryki wnioskowania — TTFT, TPOT, ITL, Goodput, P99

> Cztery kluczowe metryki decydują o tym, czy wdrożenie systemu wnioskowania działa prawidłowo. TTFT (Time to First Token) obejmuje fazę wstępnego wypełnienia (prefill), czas oczekiwania w kolejce oraz opóźnienie sieciowe. TPOT (Time Per Output Token, odpowiednik ITL) to koszt dekodowania jednego tokena, ograniczony przepustowością pamięci. Opóźnienie całkowite (end-to-end, E2E) to TTFT plus iloczyn TPOT i długości sekwencji wyjściowej. Przepustowość (throughput) określa liczbę tokenów wygenerowanych na sekundę w skali całej infrastruktury. Jednak z perspektywy biznesowej najważniejsza jest wydajność użyteczna (goodput) — czyli odsetek zapytań, które spełniły jednocześnie wszystkie określone cele SLO (Service Level Objectives). Wysoka ogólna przepustowość przy niskim wskaźniku goodput oznacza, że przetwarzane są tokeny, które ostatecznie nie docierają do użytkownika na czas. Przykładowe dane referencyjne dla modelu Llama-3.1-8B-Instruct na TRT-LLM w 2026 roku: średnie TTFT to 162 ms, średnie TPOT to 7,33 ms, a średnie opóźnienie E2E wynosi 1093 ms. Zawsze podawaj wartości dla percentyli P50, P90 i P99 – nigdy nie ograniczaj się wyłącznie do wartości średnich. Uważaj na pułapki pomiarowe: narzędzie GenAI-Perf wyklucza TTFT z obliczeń ITL, podczas gdy LLMPerf je uwzględnia. W rezultacie oba te narzędzia podadzą różne wartości TPOT dla tego samego testu.

**Typ:** Ucz się
**Języki:** Python (stdlib, kalkulator percentyli i generator raportów goodput)
**Wymagania wstępne:** Faza 17 · 04 (Wewnętrzne mechanizmy vLLM)
**Czas:** ~60 minut

## Cele nauczania

- Dokładnie zdefiniuj TTFT, TPOT, ITL, E2E, przepustowość oraz goodput i wskaż, jaki komponent systemu mierzy każda z tych metryk.
- Wyjaśnij, dlaczego średnia arytmetyczna jest niewłaściwą statystyką w analizie wydajności LLM oraz jak interpretować percentyle P50/P90/P99.
- Skonstruuj wieloograniczeniowe SLO (np. TTFT < 500 ms ORAZ TPOT < 15 ms ORAZ E2E < 2 s) i oblicz na jego podstawie wskaźnik goodput.
- Wskaż dwa narzędzia benchmarkujące, które podają inne wartości TPOT dla tego samego przebiegu testu, i wyjaśnij przyczynę tej rozbieżności.

## Problem

„Przepustowość naszej infrastruktury wynosi 15 000 tokenów na sekundę”. Co z tego? Jeśli 40% zapytań trwało dłużej niż 2 sekundy, użytkownicy zdążyli porzucić sesję. Sama przepustowość nie mówi nic o tym, czy produkt działa satysfakcjonująco.

Opóźnienia podczas wnioskowania mają wiele wymiarów, a każdy z nich zachowuje się inaczej. Faza prefill (wstępnego wypełnienia) zależy od mocy obliczeniowej i rośnie wraz z długością promptu wejściowego. Faza decode (dekodowania) zależy od przepustowości pamięci i rośnie wraz z rozmiarem wsadu (batch size). Czas oczekiwania w kolejce to problem związany z harmonogramem zadań (schedulerem), a opóźnienie sieciowe to kwestia fizycznej odległości. Potrzebujesz oddzielnych metryk dla każdego z tych elementów, potrzebujesz analizy percentylowej oraz jednego skumulowanego wskaźnika, który odpowie na pytanie: „czy użytkownik otrzymał odpowiedź w oczekiwanym czasie?”. Tym wskaźnikiem jest właśnie goodput.

## Koncepcja

### TTFT — Time to First Token (Czas do pierwszego tokena)

`TTFT = queue_time + network_request + prefill_time`

Przy długich promptach kluczowy staje się czas prefillu. Dla modelu Llama-3.3-70B w formacie FP8 na układzie H100, przetwarzanie promptu o długości 32k tokenów wymaga ok. 800 ms czystego prefillu. Czas oczekiwania w kolejce (queue time) zależy od zachowania schedulera pod dużym obciążeniem. Zapytanie sieciowe (network request) obejmuje czas nawiązania połączenia wraz z uzgadnianiem TLS. TTFT to całkowite opóźnienie, jakie dostrzega użytkownik, zanim aplikacja zacznie zwracać jakiekolwiek dane.

### TPOT / ITL — Opóźnienie między tokenami

Pojęcia te opisują tę samą wielkość fizyczną. `TPOT` (Time Per Output Token), `ITL` (Inter-Token Latency) oraz opóźnienie dekodowania na token (decode latency per token) oznaczają to samo. Jest to czas mierzony pomiędzy kolejno generowanymi tokenami po zwróceniu pierwszego z nich.

`TPOT = (decode_forward_time + scheduler_overhead) / tokens_produced`

Na konfiguracji Llama-3.3-70B H100 z włączonym dzieleniem prefillu (chunked prefill), TPOT wynosi średnio ok. 7 ms. Jeśli jednak wyłączymy chunked prefill i w tym samym czasie rozpocznie się przetwarzanie długiego promptu z innej sekwencji, TPOT może wzrosnąć nawet do 50 ms. W takich sytuacjach należy analizować percentyl P99, a nie wartość średnią.

### Opóźnienie E2E (End-to-End Latency)

`E2E = TTFT + TPOT * output_tokens + network_response`

Przy długich odpowiedziach (> 500 tokenów) o wartości E2E decyduje głównie TPOT. W przypadku krótkich odpowiedzi generowanych dla długich promptów, głównym czynnikiem jest TTFT. Raportując opóźnienie E2E, zawsze podawaj je w odniesieniu do konkretnej długości sekwencji wyjściowej.

### Przepustowość (Throughput)

`throughput = total_output_tokens / elapsed_time`

Metryka zbiorcza opisująca wydajność całej floty serwerów. Nie niesie jednak informacji o jakości obsługi indywidualnych zapytań użytkowników.

### Goodput — Wskaźnik, na którym naprawdę Ci zależy

`goodput = fraction of requests meeting (TTFT <= a) AND (TPOT <= b) AND (E2E <= c)`

SLA to zazwyczaj zestaw kilku warunków. Zapytanie jest uznawane za udane („good”) tylko wtedy, gdy spełnia wszystkie nałożone ograniczenia jednocześnie. Wskaźnik goodput określa udział takich zapytań w całym ruchu. Wysoka przepustowość przy wskaźniku goodput na poziomie 60% oznacza awarię systemu z perspektywy użytkownika. Celem projektowym powinno być zminimalizowanie opóźnień tak, aby wskaźnik goodput wynosił co najmniej 99%.

W 2026 r. goodput stanowi podstawową metrykę w testach MLPerf Inference v6.0 oraz w wewnętrznych umowach SLA dostawców usług sztucznej inteligencji.

### Dlaczego średnia arytmetyczna to zły wybór

Rozkłady opóźnień w systemach LLM są prawostronnie skośne. Batch dekodowania, w którym jedno zapytanie wywołało długi prefill, może obsłużyć 500 tokenów z czasem TPOT ok. 7 ms oraz 20 tokenów z czasem TPOT ok. 60 ms. Średni TPOT wyniesie wtedy 9 ms, podczas gdy percentyl P99 TPOT osiągnie aż 65 ms. Użytkownicy bardzo często doświadczają opóźnień na poziomie P99 i to z ich powodu decydują się na opuszczenie aplikacji.

Zawsze podawaj zestaw trzech percentyli (P50, P90, P99). Projektując UX, optymalizację należy prowadzić pod kątem wartości P99.

### Dane referencyjne — Llama-3.1-8B-Instruct na TRT-LLM, 2026

- Średnie TTFT: 162 ms
- Średnie TPOT: 7,33 ms
- Średnie opóźnienie E2E: 1093 ms
- P99 TPOT: Waha się w przedziale 10–25 ms w zależności od konfiguracji mechanizmu chunked prefill.

Są to oficjalne wyniki referencyjne opublikowane przez firmę NVIDIA. Wartości te ulegają zmianie w zależności od rozmiaru modelu (dla wersji 70B będą 3-5x wyższe), sprzętu (przejście z H100 na B200 daje ok. 3-krotne przyspieszenie) oraz charakteru obciążenia.

### Pułapka pomiarowa

Dwa najpopularniejsze narzędzia testowe w 2026 r. różnią się w sposobie wyliczania TPOT dla tego samego przebiegu testu:

- **NVIDIA GenAI-Perf**: wyklucza TTFT z obliczeń ITL. Pomiar ITL rozpoczyna się od drugiego wygenerowanego tokena.
- **LLMPerf**: uwzględnia TTFT. Pomiar ITL rozpoczyna się od pierwszego wygenerowanego tokena.

Dla zapytania z TTFT wynoszącym 500 ms, generującego 100 tokenów przy całkowitym czasie dekodowania 700 ms, narzędzie GenAI-Perf zaraportuje `ITL = 700 / 99 = 7.07 ms`, natomiast LLMPerf wykaże `ITL = 1200 / 100 = 12.00 ms`. Sam wybór narzędzia radykalnie zmienia prezentowane wyniki.

Zgłaszając wyniki, zawsze podawaj nazwę i wersję użytego narzędzia oraz definicję metryk.

### Konstruowanie SLO

Przykładowy, rozsądny poziom SLO dla modelu 70B obsługującego konsumentów w 2026 r.:

- TTFT P99 <= 800 ms.
- TPOT P99 <= 25 ms.
- E2E P99 <= 3 s dla odpowiedzi o długości < 300 tokenów.
- Docelowy wskaźnik goodput >= 99%.

W zastosowaniach korporacyjnych (Enterprise) zazwyczaj zaostrza się wymagania dotyczące TTFT (200–400 ms), dopuszczając jednocześnie dłuższe czasy E2E. Kluczem jest zdefiniowanie wszystkich trzech granic, ciągły pomiar oraz śledzenie wskaźnika goodput jako zbiorczej metryki jakości.

### Jak przeprowadzić pomiar

- Wygeneruj ruch produkcyjny lub zastosuj realistyczny ruch syntetyczny (np. używając LLMPerf z parametrami `--mean-input-tokens 800 --stddev-input-tokens 300 --mean-output-tokens 150`).
- Podczas testu benchmarkowego dąż do osiągnięcia dwukrotności maksymalnej zakładanej współbieżności.
- Przeprowadź od 30 do 50 iteracji testu i wyznacz percentyle z połączonej próby.
- Publikując raport, dołącz informacje o nazwie i wersji narzędzia, modelu, sprzęcie, poziomie współbieżności oraz rozkładzie długości promptów.

## Użycie

Skrypt `code/main.py` to uproszczony kalkulator metryk. Generuje on syntetyczny rozkład opóźnień, nakłada zdefiniowane reguły SLO i wylicza wskaźnik goodput. Pokazuje również różnice w interpretacji TPOT przez narzędzia GenAI-Perf i LLMPerf na tym samym zbiorze danych.

## Efekt końcowy

W ramach tej lekcji tworzony jest dokument `outputs/skill-slo-goodput-gate.md`. Na podstawie parametrów obciążenia oraz celów SLO generuje on szablon testu porównawczego zintegrowanego z potokiem CI/CD, oceniający wdrożenia w oparciu o wskaźnik goodput, a nie surową przepustowość.

## Ćwiczenia

1. Uruchom skrypt `code/main.py`. Wygeneruj rozkład zawierający 1% skok opóźnienia na końcu (długi ogon). Jak zmieni się wskaźnik goodput, jeśli zaostrzymy wymaganie P99 TPOT z 30 ms do 15 ms?
2. Dostawca infrastruktury deklaruje wydajność na poziomie „15 000 tokenów/s dla modelu Llama-3.3-70B na GPU H100”. Wymień trzy kluczowe pytania, które należy zadać przed zaakceptowaniem tej oferty.
3. Dlaczego włączenie mechanizmu chunked prefill pozwala zabezpieczyć percentyl P99 TPOT, ale nie wpływa znacząco na średni TPOT?
4. Zaprojektuj cele SLO dla asystenta głosowego (gdzie kluczowe jest to, kiedy użytkownik usłyszy pierwszy wygenerowany token). Które z metryk opóźnienia są w tym scenariuszu najbardziej krytyczne z punktu widzenia użytkownika?
5. Przeczytaj dokumentację README narzędzia LLMPerf oraz oficjalną dokumentację GenAI-Perf. Wskaż trzy inne metryki, w przypadku których oba te narzędzia stosują różne algorytmy obliczeniowe.

## Kluczowe terminy

| Termin | Potoczna nazwa | Rzeczywiste znaczenie |
|------|----------------|--------------------------------------|
| TTFT | „czas do pierwszego tokena” | Czas oczekiwania w kolejce + opóźnienie sieci + czas prefillu; przy długich promptach dominuje faza prefillu |
| TPOT | „czas na token wyjściowy” | Koszt dekodowania jednego tokena wyjściowego (po wygenerowaniu pierwszego), ograniczony przepustowością pamięci |
| ITL | „opóźnienie między tokenami” | Pojęcie tożsame z TPOT w większości narzędzi (wyjątkiem jest np. GenAI-Perf) |
| E2E | „opóźnienie całkowite” | Suma TTFT i iloczynu TPOT oraz długości sekwencji wyjściowej, powiększona o opóźnienie sieciowe przy wysyłaniu odpowiedzi |
| Przepustowość | „tokeny na sekundę” | Sumaryczna wydajność floty serwerowej; nieprzydatna do oceny jakości bez znajomości percentyli opóźnień |
| Goodput | „wskaźnik zgodności z SLO” | Odsetek zapytań, które spełniają wszystkie zdefiniowane kryteria SLO jednocześnie |
| P99 | „ogon rozkładu” | Opóźnienie w najgorszym przypadku (1 na 100 zapytań); kluczowy wskaźnik jakości doświadczenia użytkownika (UX) |
| Wieloograniczeniowe SLO | „złożone SLO” | Iloczyn logiczny (AND) wszystkich trzech zdefiniowanych limitów opóźnień; przekroczenie dowolnego z nich oznacza niespełnienie SLO |
| GenAI-Perf vs LLMPerf | „rozbieżność narzędziowa” | Brak spójności metodologicznej w definicji ITL (uwzględnianie lub pomijanie czasu TTFT) |

## Dalsze czytanie

- [NVIDIA NIM — LLM Benchmarking Metrics](https://docs.nvidia.com/nim/benchmarking/llm/latest/metrics.html) — Kanoniczne definicje TTFT, ITL oraz TPOT.
- [Anyscale — LLM Serving Benchmarking Metrics](https://docs.anyscale.com/llm/serving/benchmarking/metrics) — Alternatywne definicje i metodologie pomiarowe.
- [BentoML — LLM Inference Metrics](https://bentoml.com/llm/inference-optimization/llm-inference-metrics) — Praktyczne podejście do pomiaru metryk w wdrożeniach produkcyjnych.
- [LLMPerf](https://github.com/ray-project/llmperf) — Otwarty pakiet benchmarkujący oparty na frameworku Ray.
- [GenAI-Perf](https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/client/src/c++/perf_analyzer/genai-perf/README.html) — Narzędzie testowe rozwijane przez firmę NVIDIA.
- [Wnioskowanie MLPerf](https://mlcommons.org/benchmarks/inference-datacenter/) — Powszechnie akceptowany w branży benchmark wydajności oparty na wskaźniku goodput.
