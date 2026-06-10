# Testowanie obciążenia API LLM — dlaczego k6 i Locust Lie

> Tradycyjne testery obciążenia nie zostały zaprojektowane pod kątem odpowiedzi przesyłanych strumieniowo, zmiennych długości wyjściowych, wskaźników na poziomie tokena ani nasycenia procesora graficznego. Dwie pułapki nękają większość drużyn. Pułapka GIL: pomiar poziomu tokena Locust uruchamia tokenizację w ramach Python GIL, który konkuruje z generowaniem żądań w przypadku dużej współbieżności; zaległości w tokenizacji zwiększają następnie zgłaszane opóźnienia między tokenami — wąskim gardłem jest Twój klient, a nie serwer. Pułapka jednorodności podpowiedzi: identyczne podpowiedzi w teście pętli w jednym punkcie rozkładu tokenów; rzeczywisty ruch ma zmienną długość i różne dopasowania prefiksów. LLMPerf rozwiązuje ten problem za pomocą `--mean-input-tokens` + `--stddev-input-tokens`. Mapowanie narzędzi w 2026 r.: specjalizacja w LLM (GenAI-Perf, LLMPerf, LLM-Locust, Guidellm) pod kątem dokładności na poziomie tokena; **k6 v2026.1.0** + **k6 Operator 1.0 GA (wrzesień 2025 r.)** — obsługujący przesyłanie strumieniowe, natywny Kubernetes, dystrybuowany za pośrednictwem CRD TestRun/PrivateLoadZone, najlepszy dla bramek CI/CD; Vegeta for Go – nasycenie o stałym tempie; Locust 2.43.3 tylko z rozszerzeniem LLM-Locust do przesyłania strumieniowego. Wzorce obciążenia: stan ustalony, rampa, skok (test automatycznego skalowania), namoczenie (wycieki pamięci).

**Typ:** Kompilacja
**Języki:** Python (stdlib, generator realistycznych podpowiedzi dla zabawek + moduł zbierający opóźnienia)
**Wymagania wstępne:** Faza 17 · 08 (metryki wnioskowania), faza 17 · 03 (automatyczne skalowanie GPU)
**Czas:** ~75 minut

## Cele nauczania

- Wyjaśnij dwa antywzorce (pułapka GIL, pułapka natychmiastowej jednolitości), które sprawiają, że ogólne testery obciążenia kłamią w przypadku interfejsów API LLM.
- Wybierz narzędzie do określonego celu: LLMPerf (przebieg testu porównawczego), k6 + rozszerzenie strumieniowe (bramka CI), Guidellm (syntetyk na dużą skalę), GenAI-Perf (odniesienie NVIDIA).
- Zaprojektuj cztery wzorce obciążenia (stały, rampowy, skokowy, nasiąkający) i nazwij tryb awarii, który wychwytuje każdy z nich.
- Zbuduj realistyczną szybką dystrybucję, używając średniej + stddev tokenów wejściowych, a nie stałej długości.

## Problem

Przetestowałeś k6 swój punkt końcowy LLM przy 500 jednoczesnych użytkownikach. Trzymało się. Wysłałeś. W fazie produkcyjnej, przy 200 rzeczywistych użytkownikach, usługa upadła — P99 TTFT eksplodował, a procesory graficzne zostały przypięte.

Wydarzyły się dwie rzeczy. Po pierwsze, k6 wysłał 500 identycznych podpowiedzi — łączenie żądań i buforowanie prefiksów sprawiało wrażenie, jakbyś obsługiwał 500 równoczesnych dekodowań, podczas gdy w rzeczywistości obsługiwałeś jedno. Po drugie, k6 nie śledzi opóźnień między tokenami w odpowiedziach strumieniowych w sposób, w jaki odczuwa to oko; widzi jedno połączenie HTTP, a nie 500 tokenów przybywających w różnych odstępach czasu.

Testowanie obciążenia dla LLM to osobna dyscyplina.

## Koncepcja

### Pułapka GIL (Szarańcza)

Locust używa Pythona i uruchamia tokenizację po stronie klienta pod GIL. W przypadku dużej współbieżności kolejki tokenizera odpowiadają za generowanie żądań. Zgłoszone opóźnienia między tokenami obejmują zaległości w tokenizacji po stronie klienta. Uważasz, że serwer jest powolny; to uprząż testowa.

Poprawka: rozszerzenie LLM-Locust przenosi tokenizację do oddzielnych procesów lub korzysta z uprzęży w języku skompilowanym (k6, LLMPerf przy użyciu tokenizers.rs).

### Pułapka natychmiastowej jednolitości

Wszystkie znane testery obciążenia umożliwiają skonfigurowanie jednego monitu. W teście pętli obejmującym 10 000 iteracji za każdym razem wysyłany jest dokładnie ten sam monit. Serwer za każdym razem widzi ten sam prefiks — trafienia w pamięci podręcznej prefiksów zbliżają się do 100%, przepustowość wygląda świetnie.

Poprawka: próbka z szybkiej dystrybucji. LLMPerf wykorzystuje `--mean-input-tokens 500 --stddev-input-tokens 150` — różne długości, zróżnicowaną treść.

### Cztery wzorce obciążenia

1. **Stan stacjonarny** — stałe RPS przez 30-60 min. Połowy: regresje wydajności bazowej.
2. **Rampa** — liniowo zwiększaj RPS od 0 do wartości docelowej w ciągu 15 minut. Haki: punkt przerwania wydajności, anomalie nagrzewania.
3. **Spike** — nagłe 3-10x RPS przez 2 minuty i z powrotem. Haki: opóźnienie automatycznego skalowania, nasycenie kolejki, wpływ na zimny start.
4. **Namoczyć** — stan stacjonarny przez 4–8 godzin. Haki: wycieki pamięci, dryf puli połączeń, przepełnienie obserwowalności.

### Mapowanie narzędzi 2026

**LLMPerf** (Anyscale) — tokenizacja w Pythonie, ale w oparciu o Rust. Monity Mean/stddev. Możliwość przesyłania strumieniowego. Najlepsze ustawienie domyślne dla przebiegów wydajnościowych.

**NVIDIA GenAI-Perf** — referencja firmy NVIDIA. Używa klienta Triton; kompleksowe pokrycie metryczne. Uwaga: ITL nie obejmuje TTFT; LLMPerf zawiera to. Dwa narzędzia generują różne wartości TPOT dla tego samego serwera.

**LLM-Locust** (TrueFoundry) — rozszerzenie Locust naprawiające pułapkę GIL. Znane wskaźniki Locust DSL + przesyłania strumieniowego.

**guidellm** — syntetyczny benchmarking na dużą skalę.

**k6 v2026.1.0** + **k6 Operator 1.0 GA (wrzesień 2025 r.)**:
- samo k6 (Go, skompilowane, bez GIL) dodało metryki obsługujące przesyłanie strumieniowe.
- Operator k6 używa CRD TestRun / PrivateLoadZone do testów rozproszonych natywnych dla Kubernetes.
- Najlepszy do bramek CI/CD i testowania SLA.

**Vgeta** — Idź, prostsze niż k6. Stałe nasycenie protokołu HTTP. Nie obsługuje LLM, ale jest dobry do testowania bramy/limitu szybkości.

**Karta szarańczy 2.43.3** — posiada pułapkę GIL dla LLM. Tylko z rozszerzeniem LLM-Locust.

### Brama SLA w CI

Uruchom k6 na PR za pomocą:

- 30-50 iteracji każda przy wyjściowym RPS.
- Bramka: P50/P95 TTFT, 5xx < 5%, TPOT poniżej progu.
- Przerwij kompilację po naruszeniu.

### Realistyczna szybka dystrybucja

Twórz na podstawie próbek prawdziwego ruchu (jeśli je posiadasz) lub z opublikowanych dystrybucji (np. podpowiedzi ShareGPT w przypadku czatu, HumanEval w przypadku kodu). Podaj średnią + stddev do LLMPerf. Za wszelką cenę unikaj pętli z jednym pytaniem.

### Liczby, które powinieneś zapamiętać

- k6 Operator 1.0 GA: wrzesień 2025.
- k6 v2026.1.0: metryki obsługujące transmisję strumieniową.
- Typowy przebieg LLMPerf: 100-1000 żądań przy współbieżności X.
- Typowa bramka CI: 30-50 iteracji na PR.
- Cztery wzory: stały, rampa, kolec, namoczenie.

## Użyj tego

`code/main.py` symuluje test obciążenia z realistycznym rozkładem natychmiastowym, mierzy efektywny TPOT i demonstruje pułapkę jednolitego podpowiedzi.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-load-test-plan.md`. Biorąc pod uwagę obciążenie pracą i umowę SLA, wybiera narzędzie i projektuje cztery wzorce obciążenia.

## Ćwiczenia

1. Uruchom `code/main.py`. Porównaj rozkład jednolity z realistycznym – gdzie jest różnica?
2. Napisz skrypt k6 dla bramki CI: TTFT P95 < 800 ms przy 100 połączeniach jednoczesnych, czas działania 5 minut.
3. Twój test namaczania pokazuje, że pamięć rośnie o 50 MB/godzinę. Wymień trzy przyczyny i instrumenty, które należy wybrać między nimi.
4. Test skokowy od 10 RPS do 100 RPS. Jaki jest oczekiwany czas przywracania, jeśli stos produkcyjny Karpenter + vLLM jest na miejscu (faza 17 · 03 + 18)?
5. GenAI-Perf raportuje TPOT=6ms; LLMPerf zgłasza TPOT = 11 ms na tym samym serwerze. Wyjaśnić.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| LLMPerf | „uprząż LLM” | Narzędzie do testów porównawczych Anyscale, obsługujące transmisję strumieniową |
| GenAI-Perf | „Narzędzie NVIDIA” | Uprząż referencyjna NVIDIA |
| LLM-Szarańcza | „Szarańcza dla LLM” | Przedłużenie szarańczy mocujące pułapkę GIL |
| przewodnik | „syntetyczny benchmark” | Syntetyczne narzędzie na dużą skalę |
| k6 Operator | „K8s K6” | Rozproszone k6 oparte na CRD |
| Pułapka GIL | „Narzut klienta Pythona” | Zaległości w tokenizacji zwiększają zgłaszane opóźnienia |
| Pułapka natychmiastowej jednolitości | „jednokrotne kłamstwo” | Pętla z tym samym monitem trafia do pamięci podręcznej, zwiększając przepustowość |
| Stan ustalony | „stałe obciążenie” | Płaskie RPS przez N minut |
| Rampa | „linearnie” | 0 do celu w czasie trwania |
| Spike | „próba wybuchowa” | Nagły mnożnik, a następnie powrót |
| Namoczyć | „długi test” | Godziny wykrywania wycieków |

## Dalsze czytanie

- [TianPan — aplikacje LLM do testowania obciążenia](https://tianpan.co/blog/2026-03-19-load-testing-llm-applications)
- [PremAI — Testowanie obciążenia LLM 2026](https://blog.premai.io/load-testing-llms-tools-metrics-realistic-traffic-simulation-2026/)
— [NVIDIA NIM — wprowadzenie do testów porównawczych wnioskowania LLM](https://docs.nvidia.com/nim/large-language-models/1.0.0/benchmarking.html)
— [TrueFoundry — LLM-Locust](https://www.truefoundry.com/blog/llm-locust-a-tool-for-benchmarking-llm- Performance)
- [LLMPerf](https://github.com/ray-project/llmperf)
- [Operator k6](https://github.com/grafana/k6-operator)