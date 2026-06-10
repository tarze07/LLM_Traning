---

name: llm-observability
description: Zbuduj własny pulpit nawigacyjny obserwacji LLM, który pozyskuje zakresy OpenTelemetry GenAI, przeprowadza ewaluacje i wychwytuje wprowadzone regresje w czasie krótszym niż pięć minut.
version: 1.0.0
phase: 19
lesson: 11
tags: [capstone, observability, otel, langfuse, phoenix, evals, drift, clickhouse]

---

Biorąc pod uwagę produkcyjny ruch LLM w co najmniej sześciu rodzinach SDK (OpenAI, Anthropic, Google GenAI, LangChain, LlamaIndex, vLLM), wdróż samodzielnie hostowaną płaszczyznę obserwowalności, która pobiera zakresy OTLP GenAI-semconv, uruchamia ewaluacje, wykrywa dryf i alerty.

Plan budowy:

1. Kolektor OpenTelemetry z odbiornikiem HTTP OTLP, procesor próbkowania ogonowego (zachowaj 100% błędów, 10% sukcesu, 100% wysokiej toksyczności/PII), eksporterzy do ClickHouse + S3.
2. Schemat rozpiętości ClickHouse odzwierciedlający semconv GenAI: gen_ai.system, gen_ai.request.model, use.input/output_tokens, latency_ms, user_id, app_id plus torba JSON na monity/uzupełnienia.
3. Magazyn metadanych Postgres dla aplikacji, użytkowników, sesji, kolejki adnotacji.
4. Automatyczne oprzyrządowanie OpenLLMetry w aplikacji klienckiej dla każdej rodziny SDK; sprawdź kanoniczne rozpiętości lądowe.
5. Pakiet ewaluacyjny DeepEval + RAGAS + Phoenix zaplanowany na próbkowane ślady; niestandardowy sędzia LLM pod kątem informacji umożliwiających identyfikację i niezgodnych z polityką.
6. Cotygodniowy detektor dryfu PSI / KL w przypadku osadzania zbiorczego podpowiedzi; próg alarmowy 0,2.
7. Eksporter Prometheusa dla agregatów wyników eval i percentyli opóźnień; Alertmanager na Slack (ostrzeżenie) + PagerDuty (krytyczny).
8. Pulpit nawigacyjny routera aplikacji Next.js 15: przegląd, wyszukiwanie śladów + wodospad, trendy ewaluacyjne, wykres dryfu, alerty.
9. Sonda regresji: wprowadź wzorzec odpowiedzi, który w 1% przypadków powoduje wyciek fałszywych numerów SSN; zmierzyć MTTR (czas alarmu).

Rubryka oceny:

| Waga | Kryterium | Pomiar |
|:-:|---|---|
| 25 | Pokrycie schematu śledzenia | Liczba rodzin SDK tworzących kanoniczne zakresy GenAI (docelowo 6+) |
| 20 | Poprawność oceny | Wyniki DeepEval / RAGAS w porównaniu z zestawem ręcznie oznakowanym |
| 20 | UX panelu | MTTR przy wstrzykniętej regresji (docelowo poniżej 5 minut) |
| 20 | Koszt/skala | Stałe pozyskiwanie 1 tys. rozpiętości na sekundę bez zaległości |
| 15 | Alarmowanie + wykrywanie dryfu | Łańcuch Prometheus/Alertmanager przećwiczony od początku do końca |

Twarde odrzucenia:

- Schematy rozpiętości, które wymyślają nazwy atrybutów, których nie ma w pliku semconv OpenTelemetry GenAI.
- Zasady próbkowania ogonowego, które usuwają błędy (dobrze znany antywzorzec).
- Ewaluacje działające z szybkością przyjmowania bez próbkowania (niedopuszczalny koszt).
- Pulpity nawigacyjne pokazujące „opóźnienie” bez separacji p50/p95/p99.

Zasady odmowy:

- Odmawiaj utrwalenia monitów lub uzupełnień bez zasad redagowania informacji umożliwiających identyfikację.
- Odmów żądania „obsługi wielu zestawów SDK” bez testu regresji zakresu kanonicznego dla każdego zestawu SDK.
- Odmówić wykrywania dryfu statku bez okna bazowego; Dryf zerowy jest bezużyteczny.

Dane wyjściowe: repozytorium zawierające konfigurację modułu zbierającego, schemat ClickHouse, pulpit nawigacyjny Next.js 15, zadania ewaluacyjne, detektor dryfu, łańcuch alertów, zestaw danych demonstracyjnych 10 tys. śledzenia z adnotacjami regresji oraz zapis dokumentujący MTTR dla wstrzykniętej regresji PII oraz trzy najważniejsze ulepszenia UX pulpitu nawigacyjnego, które spowodowały spadek MTTR w trakcie iteracji.