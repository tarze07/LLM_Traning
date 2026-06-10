# Metryki wnioskowania — TTFT, TPOT, ITL, Goodput, P99

> Cztery wskaźniki decydują o tym, czy wdrożenie wnioskowania działa. TTFT to wstępne wypełnienie plus kolejka i sieć. TPOT (odpowiednik ITL) to koszt dekodowania związany z pamięcią na token. Opóźnienie od końca do końca to TTFT plus TPOT razy długość sygnału wyjściowego. Przepustowość to tokeny na sekundę zagregowane w całej flocie. Ale dla produktu liczy się goodput — ułamek żądań, które spełniły jednocześnie każdy SLO. Wysoka przepustowość przy niskiej wydajności oznacza, że ​​przetwarzasz tokeny, które nigdy nie docierają do użytkowników na czas. Numery referencyjne dla Llama-3.1-8B-Instruct na TRT-LLM w 2026 r.: średnia TTFT 162 ms, średnia TPOT 7,33 ms, średnia E2E 1093 ms. Zawsze zgłaszaj P50, P90, P99 — nigdy nie tylko to, co masz na myśli. I obserwuj pułapkę pomiarową: GenAI-Perf wyklucza TTFT z obliczeń ITL, LLMPerf go uwzględnia; dwa narzędzia nie zgadzają się co do TPOT dla tego samego przebiegu.

**Typ:** Ucz się
**Języki:** Python (stdlib, kalkulator percentyli zabawek i reporter goodput)
**Wymagania wstępne:** Faza 17 · 04 (vLLM obsługujące urządzenia wewnętrzne)
**Czas:** ~60 minut

## Cele nauczania

- Dokładnie zdefiniuj TTFT, TPOT, ITL, E2E, przepustowość i dobrą wydajność oraz nazwij komponent, który każdy z nich mierzy.
- Wyjaśnij, dlaczego średnia jest niewłaściwą statystyką dla obsługi LLM i jak czytać P50/P90/P99.
- Skonstruuj wieloograniczenie SLO (np. TTFT < 500 ms ORAZ TPOT < 15 ms ORAZ E2E < 2 s) i oblicz na jego podstawie dobrą wydajność.
- Wymień dwa narzędzia testowe, które nie zgadzają się z TPOT w tym samym przebiegu i wyjaśnij dlaczego.

## Problem

„Nasza przepustowość wynosi 15 000 tokenów na sekundę”. No to co? Jeśli 40% żądań trwało dłużej niż 2 sekundy, użytkownicy porzucali sesję. Sama wydajność nie mówi, czy produkt działa.

Wnioskowanie ma wiele osi opóźnienia i każda z nich kończy się inaczej. Wstępne wypełnienie jest powiązane z obliczeniami i skaluje się wraz z długością podpowiedzi. Dekodowanie jest powiązane z pamięcią i skaluje się wraz z rozmiarem partii. Opóźnienie w kolejce jest problemem operacyjnym. Sieć to problem związany z odległością fizyczną. Potrzebujesz odrębnych wskaźników dla każdego z nich, potrzebujesz percentyli i potrzebujesz pojedynczego zestawienia, które mówi „czy użytkownik otrzymał to, czego oczekiwał” – to jest dobra opinia.

## Koncepcja

### TTFT — czas do pierwszego tokena

`TTFT = queue_time + network_request + prefill_time`

W przypadku długich podpowiedzi dominuje wstępne wypełnianie. Na Llama-3.3-70B FP8 na H100, monit 32k zajmuje ~800 ms czystego wstępnego wypełnienia. Czas kolejki to zachowanie programu planującego pod obciążeniem. Żądanie sieciowe to czas połączenia, w tym TLS. TTFT to opóźnienie, które widzi użytkownik, zanim cokolwiek zostanie przesłane z powrotem.

### TPOT / ITL — opóźnienie między tokenami

Wiele nazw dla jednej ilości. `TPOT` (czas na token wyjściowy), `ITL` (opóźnienie między tokenami), `decode latency per token` — wszystko tak samo. Jest to czas pomiędzy kolejnymi przesyłanymi strumieniowo tokenami po pierwszym.

`TPOT = (decode_forward_time + scheduler_overhead) / tokens_produced`

Na tym samym stosie Llama-3.3-70B H100 z fragmentarycznym wypełnieniem wstępnym, TPOT oznacza ~7 ms. Bez fragmentarycznego wstępnego wypełniania, podczas długiego wstępnego wypełniania sąsiedniej sekwencji, TPOT może wzrosnąć do 50 ms. Oglądaj P99, nie znaczy.

### Opóźnienie E2E

`E2E = TTFT + TPOT * output_tokens + network_response`

W przypadku długich wyników (> 500 tokenów) E2E jest zdominowany przez TPOT. W przypadku krótkich wyników z długimi podpowiedziami, E2E jest zdominowany przez TTFT. Zgłoś E2E z uwarunkowaniem długości wyjściowej.

### Przepustowość

`throughput = total_output_tokens / elapsed_time`

Metryka zbiorcza. Informuje o wydajności floty. Nie informuje o stanie zdrowia na żądanie indywidualne.

### Goodput — wskaźnik, na którym naprawdę Ci zależy

`goodput = fraction of requests meeting (TTFT <= a) AND (TPOT <= b) AND (E2E <= c)`

SLO to wieloograniczenie. Żądanie jest „dobre” tylko wtedy, gdy spełnione są wszystkie ograniczenia. Goodput to udział. Wysoka przepustowość na poziomie 60% oznacza porażkę. Celem jest niższa przepustowość na poziomie 99%.

W 2026 r. goodput będzie miernikiem używanym w zgłoszeniach MLPerf Inference v6.0 oraz w wewnętrznym śledzeniu umów SLA u dostawców platform AI.

### Dlaczego średnia jest błędną statystyką

Rozkłady opóźnień LLM są prawostronne. Partia dekodowania z jednym sąsiadem o długim wstępnym wypełnieniu może dostarczyć 500 tokenów z czasem TPOT ~7 ms i 20 tokenów z czasem TPOT ~60 ms. Średni TPOT wynosi 9 ms. P99 TPOT wynosi 65 ms. Użytkownicy regularnie klikają P99 — dlatego wychodzą.

Zawsze zgłaszaj potrójne (P50, P90, P99). Jeśli chodzi o wygodę użytkownika, optymalizujesz P99.

### Numery referencyjne — Llama-3.1-8B-Instruct on TRT-LLM, 2026

- średni TTFT: 162 ms
- średni TPOT: 7,33 ms
- średnia E2E: 1093 ms
- P99 TPOT: zmienia się w zakresie 10–25 ms w zależności od konfiguracji wstępnego napełniania fragmentarycznego.

Są to opublikowane punkty odniesienia firmy NVIDIA. Zmieniają się w zależności od rozmiaru modelu (70B pokazałoby 3-5x), sprzętu (H100 vs B200 ~3x) i obciążenia.

### Pułapka pomiarowa

Dwa z najczęściej używanych narzędzi testowych z 2026 r. nie zgadzają się co do TPOT dla tego samego okresu:

- **NVIDIA GenAI-Perf**: wyklucza TTFT z obliczeń ITL. ITL zaczyna się od tokena 2.
- **LLMPerf**: obejmuje TTFT. ITL zaczyna się od tokena 1.

W przypadku żądania z TTFT 500 ms i 100 tokenami wyjściowymi przy całkowitym dekodowaniu 700 ms GenAI-Perf raportuje `ITL = 700/99 = 7.07 ms`, LLMPerf raportuje `ITL = 1200/100 = 12.00 ms`. Wybór narzędzia zmienia liczbę.

Zawsze podawaj, które narzędzie. Zawsze publikuj definicję.

### Konstruowanie SLO

Rozsądny SLO skierowany do konsumentów dla modelu czatu 70B w 2026 r.:

- TTFT P99 <= 800 ms.
- TPOT P99 <= 25 ms.
- E2E P99 <= 3 s dla wyjść <300 tokenów.
- Docelowa wartość dobrego wyniku >= 99%.

Enterprise SLO zawężają TTFT (200–400 ms) i rozluźniają E2E. Chodzi o to, aby je zapisać, zmierzyć wszystkie trzy i śledzić goodput jako pojedynczy element złożony.

### Jak mierzyć

- Uruchom ruch rzeczywisty lub realistyczny syntetyczny (LLMPerf z `--mean-input-tokens 800 --stddev-input-tokens 300 --mean-output-tokens 150`).
- Docelowa 2-krotna szczytowa współbieżność dla przebiegu testu porównawczego.
- Wykonaj 30–50 iteracji, pobierz percentyle połączonej próbki.
- Publikuj z nazwą narzędzia, wersją narzędzia, modelem, sprzętem, współbieżnością i szybką dystrybucją.

## Użyj tego

`code/main.py` to kalkulator wartości zabawek. Wygeneruj syntetyczny rozkład opóźnień, zastosuj SLO i oblicz dobrą wydajność. Pokazuje również różnicę GenAI-Perf vs LLMPerf TPOT na tym samym śladzie.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-slo-goodput-gate.md`. Biorąc pod uwagę obciążenie pracą i SLO, tworzy przepis porównawczy gotowy do CI/CD, który ocenia wdrożenia na podstawie dobrej przepustowości, a nie przepustowości.

## Ćwiczenia

1. Uruchom `code/main.py`. Wygeneruj rozkład z 1% skokiem końcowym. Jak zmienia się goodput po dokręceniu P99 TPOT z 30 ms do 15 ms?
2. Sprzedawca podaje „15 000 tok/s na Lamie 3.3 70B H100”. Wymień trzy pytania, które należy zadać, zanim zaufasz.
3. Dlaczego cząstkowe wypełnienie wstępne chroni P99 TPOT, ale nie oznacza TPOT?
4. Skonstruuj konsumenckie SLO dla asystenta głosowego (pierwszy token zostanie usłyszany, a nie odczytany). Które dane są najbardziej widoczne dla użytkowników?
5. Przeczytaj pliki README LLMPerf i dokumentację GenAI-Perf. Wskaż trzy inne wskaźniki, w przypadku których narzędzia się nie zgadzają.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| TTFT | „czas do pierwszego tokena” | Kolejka + sieć + wstępne wypełnienie; zdominowany przez wstępne wypełnienie przy długich podpowiedziach |
| TPOT | „czas na token wyjściowy” | Koszt dekodowania związanego z pamięcią na token po pierwszym |
| ITL | „opóźnienie między tokenami” | Taki sam jak TPOT w większości narzędzi (nie we wszystkich — zobacz GenAI-Perf) |
| E2E | „od końca do końca” | TTFT + TPOT * wynik_len; sieć po stronie odpowiedzi na górze |
| Przepustowość | „tok/s” | Wydajność floty; bezużyteczne bez percentyli opóźnień |
| Dobra wiadomość | „Stawka SLO-met” | Część żądań spełniających jednocześnie wszystkie ograniczenia SLO |
| P99 | "ogon" | Opóźnienie w najgorszym przypadku 1 na 100; wskaźnik doświadczenia użytkownika |
| Wiele ograniczeń SLO | "staw" | ORAZ wszystkich trzech granic opóźnienia; żądanie nie powiedzie się, jeśli którekolwiek zostanie naruszone |
| GenAI-Perf vs LLMPerf | „pułapka na narzędzia” | Narzędzia nie są zgodne co do tego, czy ITL obejmuje TTFT |

## Dalsze czytanie

- [NVIDIA NIM — LLM Benchmarking Metrics](https://docs.nvidia.com/nim/benchmarking/llm/latest/metrics.html) — kanoniczna definicja TTFT, ITL, TPOT.
- [Anyscale — LLM Serving Benchmarking Metrics](https://docs.anyscale.com/llm/serving/benchmarking/metrics) — alternatywne definicje i przepis na pomiar.
- [BentoML — LLM Inference Metrics](https://bentoml.com/llm/inference-optimization/llm-inference-metrics) — pomiar stosowany w rzeczywistych wdrożeniach.
- [LLMPerf](https://github.com/ray-project/llmperf) — test porównawczy open source oparty na Ray.
- [GenAI-Perf](https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/client/src/c++/perf_analyzer/genai-perf/README.html) — narzędzie testowe firmy NVIDIA.
— [Wnioskowanie MLPerf](https://mlcommons.org/benchmarks/inference-datacenter/) — akceptowany w branży test porównawczy oparty na goodput.