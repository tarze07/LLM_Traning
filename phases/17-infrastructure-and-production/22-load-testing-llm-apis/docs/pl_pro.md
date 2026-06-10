# Testowanie obciążenia API LLM — dlaczego k6 i Locust kłamią

> Tradycyjne narzędzia do testowania obciążenia nie zostały zaprojektowane z myślą o odpowiedziach strumieniowych, zmiennej długości generowanego tekstu, metrykach na poziomie tokenów ani nasyceniu procesorów graficznych (GPU). Większość zespołów wpada w dwie pułapki. Pułapka GIL: w narzędziu Locust pomiar na poziomie tokenów uruchamia tokenizację w ramach globalnej blokady interpretera Pythona (GIL), która przy dużej współbieżności konkuruje z wysyłaniem żądań; opóźnienia w tokenizacji zawyżają wówczas raportowany czas między tokenami (inter-token latency) – wąskim gardłem staje się klient, a no serwer. Pułapka jednolitych promptów (prompt uniformity): wysyłanie identycznych promptów w pętli testowej sztucznie zawęża rozkład tokenów; w rzeczywistości ruch ma zmienną długość i różny stopień dopasowania prefiksów w pamięci podręcznej (prefix caching). LLMPerf rozwiązuje ten problem za pomocą parametrów `--mean-input-tokens` + `--stddev-input-tokens`. Podział narzędzi w 2026 r.: specjalistyczne narzędzia LLM (GenAI-Perf, LLMPerf, LLM-Locust, Guidellm) zapewniające dokładność na poziomie pojedynczych tokenów; **k6 v2026.1.0** + **k6 Operator 1.0 GA (wrzesień 2025 r.)** – obsługujące streaming, natywne dla Kubeneteza, dystrybuowane za pomocą CRD TestRun/PrivateLoadZone, idealne do integracji z CI/CD; Vegeta (napisana w Go) – generowanie obciążenia o stałej intensywności (constant rate); Locust 2.43.3 – użyteczny wyłącznie z rozszerzeniem LLM-Locust do obsługi streamingu. Schematy obciążenia: stan ustalony (steady state), narastający (ramp), skokowy (spike - test automatycznego skalowania), długotrwały (soak - testowanie wycieków pamięci).

**Typ:** Kompilacja
**Języki:** Python (stdlib, generator realistycznych promptów testowych + moduł zbierający opóźnienia)
**Wymagania wstępne:** Faza 17 · Lekcja 08 (metryki wnioskowania), faza 17 · Lekcja 03 (automatyczne skalowanie GPU)
**Czas:** ~75 minut

## Cele nauczania

- Wyjaśnij dwa antywzorce (pułapka GIL oraz pułapka jednolitych promptów), przez które uniwersalne narzędzia do testowania obciążenia dają zafałszowane wyniki dla API LLM.
- Dobierz odpowiednie narzędzie do konkretnego scenariusza: LLMPerf (testy porównawcze/benchmarki), k6 + rozszerzenie streamingowe (bramki CI), Guidellm (syntetyczne testy na dużą skalę), GenAI-Perf (referencyjne narzędzie od NVIDIA).
- Zaprojektuj cztery schematy obciążenia (stały, narastający, skokowy, długotrwały) i zidentyfikuj rodzaje awarii, które pozwala wykryć każdy z nich.
- Zbuduj realistyczny rozkład promptów wejściowych, używając średniej oraz odchylenia standardowego długości tokenów zamiast stałej długości.

## Problem

Przetestowałeś swój punkt końcowy (endpoint) LLM za pomocą k6 przy 500 jednoczesnych użytkownikach. System wytrzymał, więc wdrożyłeś go na produkcję. Tam jednak, przy zaledwie 200 rzeczywistych użytkownikach, usługa przestała działać – opóźnienie P99 TTFT (Time to First Token) drastycznie wzrosło, a procesory GPU zostały maksymalnie obciążone.

Powody były dwa. Po pierwsze, k6 wysłał 500 identycznych promptów – dzięki mechanizmom łączenia żądań (request coalescing) oraz buforowania prefiksów (prefix caching) system zachowywał się tak, jakby obsługiwał tylko jedno dekodowanie zamiast 500 równoległych procesów. Po drugie, standardowe k6 nie śledzi opóźnień między kolejnymi tokenami w odpowiedziach strumieniowych tak, jak odczuwa to użytkownik; widzi po prostu jedno długie połączenie HTTP, ignorując fakt, że tokeny docierają w nieregularnych odstępach czasu.

Testowanie obciążenia dla LLM to osobna dyscyplina.

## Koncepcja

### Pułapka GIL (Locust)

Locust bazuje na Pythonie i wykonuje tokenizację po stronie klienta w ramach blokady GIL. Przy dużej współbieżności kolejka tokenizera blokuje wysyłanie kolejnych żądań. Raportowane opóźnienia między tokenami (inter-token latency) zawierają w sobie czas spędzony w kolejce po stronie klienta. Myślisz, że to serwer działa wolno, podczas gdy wąskim gardłem jest samo środowisko testowe.

Rozwiązanie: Rozszerzenie LLM-Locust przenosi tokenizację do osobnych procesów lub korzysta z narzędzi napisanych w językach skompilowanych (k6, LLMPerf wykorzystujące bibliotekę tokenizers.rs).

### Pułapka jednolitych promptów (Prompt Uniformity)

Większość tradycyjnych narzędzi testowych pozwala na zdefiniowanie tylko jednego promptu. W pętli testowej na 10 000 iteracji za każdym razem wysyłane jest dokładnie to samo zapytanie. Serwer widzi identyczny prefiks, co sprawia, że współczynnik trafień w pamięci podręcznej prefiksów (prefix cache hit rate) zbliża się do 100%, a przepustowość wygląda sztucznie na znakomitą.

Rozwiązanie: Losowanie promptów z określonego rozkładu. LLMPerf pozwala na konfigurację parametrów takich jak `--mean-input-tokens 500 --stddev-input-tokens 150`, co zapewnia różną długość i zróżnicowaną treść zapytań.

### Cztery schematy obciążenia

1. **Stan ustalony (Steady State)** – stała liczba żądań na sekundę (RPS) przez 30-60 minut. Cel: Wykrywanie regresji bazowej wydajności.
2. **Narastający (Ramp)** – liniowe zwiększanie RPS od 0 do wartości docelowej w ciągu 15 minut. Cel: Wyznaczenie punktu krytycznego wydajności oraz wykrywanie problemów podczas "rozgrzewania" systemu (cold starts/caching).
3. **Skokowy (Spike)** – nagły wzrost RPS o 3-10x na czas 2 minut i powrót do poziomu wyjściowego. Cel: Testowanie opóźnień autoskalowania, przepełnienia kolejek oraz wpływu zimnego startu.
4. **Długotrwały (Soak)** – stałe obciążenie utrzymywane przez 4-8 godzin. Cel: Wykrywanie wycieków pamięci, problemów z pulą połączeń (connection pool drift) czy przeciążenia systemów monitoringu (observability overflow).

### Przegląd narzędzi w 2026 roku

**LLMPerf** (Anyscale) – tokenizacja w Pythonie, ale oparta na silniku w Rust. Obsługuje parametry rozkładu promptów (mean/stddev) oraz streaming. Najlepszy domyślny wybór do testów wydajnościowych.

**NVIDIA GenAI-Perf** – referencyjne narzędzie od NVIDIA. Korzysta z klienta Triton i oferuje kompleksowy zestaw metryk. Uwaga: ITL (Inter-Token Latency) w tym narzędziu nie uwzględnia TTFT, podczas gdy LLMPerf je wlicza. Te dwa narzędzia mogą raportować różne wartości TPOT (Time Per Output Token) dla tego samego serwera.

**LLM-Locust** (TrueFoundry) – rozszerzenie dla systemu Locust eliminujące pułapkę GIL. Oferuje znajomy interfejs Locust DSL oraz metryki dla streamingu.

**guidellm** – syntetyczne testy porównawcze na dużą skalę.

**k6 v2026.1.0** + **k6 Operator 1.0 GA (wrzesień 2025 r.)**:
- samo k6 (napisane w Go, skompilowane, wolne od problemów z GIL) wprowadziło natywne wsparcie dla metryk streamingowych.
- k6 Operator wykorzystuje zasoby CRD TestRun / PrivateLoadZone do przeprowadzania rozproszonych testów natywnych dla Kubernetes.
- Najlepiej sprawdza się w bramkach CI/CD oraz przy weryfikacji umów SLA.

**Vegeta** – narzędzie w Go, prostsze niż k6. Zapewnia stałe natężenie ruchu HTTP. Nie wspiera specyfiki LLM, ale doskonale sprawdza się przy testowaniu bram sieciowych i limitów żądań (rate limiting).

**Locust 2.43.3** – w wersji standardowej wykazuje podatność na pułapkę GIL przy LLM. Wymaga użycia rozszerzenia LLM-Locust.

### Bramka SLA w procesie CI

Uruchamianie k6 na poziomie Pull Requestu (PR):

- 30-50 iteracji dla każdego testu przy określonym bazowym RPS.
- Weryfikacja: P50/P95 TTFT, błędy 5xx < 5%, TPOT poniżej zdefiniowanego progu.
- Przerwanie budowania (build fail) w przypadku naruszenia tych kryteriów.

### Realistyczny rozkład promptów

Przygotuj rozkład na podstawie próbek rzeczywistego ruchu (jeśli są dostępne) lub publicznych zbiorów danych (np. promptów ShareGPT dla czatów, HumanEval dla kodu). Przekaż parametry średniej (mean) oraz odchylenia standardowego (stddev) do LLMPerf. Unikaj pętli wysyłających w kółko to samo zapytanie.

### Kluczowe dane do zapamiętania

- k6 Operator 1.0 GA: wrzesień 2025.
- k6 v2026.1.0: metryki ze wsparciem dla streamingu.
- Typowy test w LLMPerf: 100-1000 żądań przy współbieżności X.
- Typowa bramka CI: 30-50 iteracji na jeden PR.
- Cztery schematy obciążenia: stały (steady state), narastający (ramp), skokowy (spike), długotrwały (soak).

## Kod demonstracyjny

Skrypt `code/main.py` symuluje test obciążenia z realistycznym rozkładem promptów, mierzy rzeczywisty TPOT i demonstruje konsekwencje pułapki jednolitych promptów.

## Rezultat zadania

W ramach tej lekcji powstanie plik `outputs/skill-load-test-plan.md`. Na podstawie charakterystyki obciążenia oraz umowy SLA dobierane jest odpowiednie narzędzie i projektowane są cztery opisane schematy obciążenia.

## Ćwiczenia

1. Uruchom skrypt `code/main.py`. Porównaj rozkład jednolity z realistycznym – na czym polega główna różnica?
2. Napisz scenariusz k6 dla bramki CI: P95 TTFT < 800 ms przy 100 jednoczesnych połączeniach i czasie trwania testu wynoszącym 5 minut.
3. Test długotrwały (soak test) wykazał wzrost zużycia pamięci o 50 MB na godzinę. Wymień trzy potencjalne przyczyny i wskaż narzędzia diagnostyczne, które pozwolą ustalić źródło problemu.
4. Test skokowy (spike) polega na nagłym wzroście z 10 RPS do 100 RPS. Jaki będzie oczekiwany czas stabilizacji systemu, jeśli w środowisku produkcyjnym wdrożono zestaw Karpenter + vLLM (Faza 17 · Lekcje 03 + 18)?
5. GenAI-Perf raportuje TPOT = 6 ms, natomiast LLMPerf wskazuje TPOT = 11 ms dla tego samego serwera. Wyjaśnij tę różnicę.

## Słownik pojęć

| Termin | Jak się potocznie mówi | Co to dokładnie oznacza |
|------|----------------|--------------------------------------|
| LLMPerf | „harness do LLM” | Narzędzie od Anyscale do testów porównawczych (benchmarking) ze wsparciem dla streamingu |
| GenAI-Perf | „narzędzie od NVIDIA” | Referencyjne środowisko testowe NVIDIA |
| LLM-Locust | „Locust dla LLM” | Rozszerzenie do Locusta eliminujące problem blokady GIL |
| guidellm | „syntetyczny benchmark” | Narzędzie do syntetycznych testów wydajnościowych na dużą skalę |
| k6 Operator | „k6 na K8s” | Rozproszone testy k6 zarządzane przez CRD w Kubernetes |
| Pułapka GIL | „narzut klienta w Pythonie” | Opóźnienia w tokenizacji po stronie klienta sztucznie zawyżają wyniki |
| Pułapka jednolitych promptów | „zafałszowanie przez jeden prompt” | Powtarzanie tego samego zapytania trafia w cache i sztucznie zawyża przepustowość |
| Stan ustalony (Steady State) | „stałe obciążenie” | Stały poziom RPS utrzymywany przez N minut |
| Rampa (Ramp) | „liniowe zwiększanie” | Narastanie obciążenia od 0 do wartości docelowej w określonym czasie |
| Skok (Spike) | „test uderzeniowy” | Nagły, kilkukrotny wzrost obciążenia i szybki powrót do bazy |
| Soak test | „test długodystansowy” | Wielogodzinny test mający na celu wykrycie wycieków pamięci |

## Materiały uzupełniające

- [TianPan — aplikacje LLM do testowania obciążenia](https://tianpan.co/blog/2026-03-19-load-testing-llm-applications)
- [PremAI — Testowanie obciążenia LLM 2026](https://blog.premai.io/load-testing-llms-tools-metrics-realistic-traffic-simulation-2026/)
- [NVIDIA NIM — wprowadzenie do testów porównawczych wnioskowania LLM](https://docs.nvidia.com/nim/large-language-models/1.0.0/benchmarking.html)
- [TrueFoundry — LLM-Locust](https://www.truefoundry.com/blog/llm-locust-a-tool-for-benchmarking-llm-performance)
- [LLMPerf](https://github.com/ray-project/llmperf)
- [Operator k6](https://github.com/grafana/k6-operator)
