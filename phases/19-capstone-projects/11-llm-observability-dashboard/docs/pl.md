# Capstone 11 — Panel obserwacji i oceny LLM

> Langfuse przeszedł na technologię open-core. Arize Phoenix opublikował mapowania semconv GenAI na rok 2026. Zarówno Helicone, jak i Braintrust podwoiły swoje działania w zakresie atrybucji kosztów na użytkownika. OpenLLMetry firmy Traceloop stało się de facto instrumentem SDK. Forma produkcyjna to ClickHouse dla śladów, Postgres dla metadanych, Next.js dla interfejsu użytkownika i mała armia zadań ewaluacyjnych (DeepEval, RAGAS, LLM-judge) uruchamiających próbkowane ślady. Zbuduj jeden hostowany samodzielnie, pozyskuj z co najmniej czterech rodzin zestawów SDK i zademonstruj wychwytywanie wprowadzonej regresji w czasie krótszym niż pięć minut.

**Typ:** Zwieńczenie
**Języki:** TypeScript (UI), Python / TypeScript (ingest + evals), SQL (ClickHouse)
**Wymagania wstępne:** Faza 11 (inżynieria LLM), Faza 13 (narzędzia), Faza 17 (infrastruktura), Faza 18 (bezpieczeństwo)
**Wykonywane fazy:** P11 · P13 · P17 · P18
**Czas:** 25 godzin

## Problem

Każdy zespół AI obsługujący ruch produkcyjny w 2026 r. utrzymuje płaszczyznę obserwowalności obok modelu. Atrybucja kosztów. Wykrywanie halucynacji. Monitorowanie dryfu. Sygnał jailbreaka. Panele SLO. Powiadomienia o wycieku danych osobowych. Odniesienia do open source — Langfuse, Phoenix, OpenLLMetry — zbiegły się w konwencjach semantycznych OpenTelemetry GenAI jako schemat pozyskiwania. Możesz teraz instrumentować OpenAI, Anthropic, Google, LangChain, LlamaIndex i vLLM za pomocą jednego zestawu SDK i zakresów zgodnych z dostarczaniem.

Zbudujesz samodzielnie hostowany pulpit nawigacyjny, który pobiera dane z co najmniej czterech rodzin zestawów SDK, uruchamia niewielki zestaw zadań ewaluacyjnych na próbkowanych śladach, wykrywa dryf i alerty. Pasek pomiaru: po celowo wstrzykniętej regresji (podpowiedź, która rozpoczyna generowanie informacji umożliwiających identyfikację użytkownika), pulpit nawigacyjny wychwytuje go i uruchamia alert w czasie krótszym niż pięć minut.

## Koncepcja

Pozyskiwanie to OTLP HTTP. SDK tworzy zakresy GenAI-semconv: `gen_ai.system`, `gen_ai.request.model`, `gen_ai.usage.input_tokens`, `gen_ai.response.id`, `llm.prompts`, `llm.completions`. Rozpiętości lądują w ClickHouse w celu analizy kolumnowej; metadane (użytkownicy, sesje, aplikacje) trafiają do Postgres.

Ewaluacje działają jako zadania wsadowe na próbkowanych śladach. DeepEval ocenia wierność, toksyczność i trafność odpowiedzi. RAGAS ocenia metryki wyszukiwania, gdy ślad zawiera kontekst wyszukiwania. Niestandardowi sędziowie LLM przeprowadzają kontrole specyficzne dla domeny (wyciek danych osobowych, reakcja niezgodna z zasadami). Przebiegi Eval zapisują z powrotem w tym samym ClickHouse, co zakresy eval połączone z nadrzędnym śladem.

Wykrywanie dryfu monitoruje rozkład przestrzeni osadzania w czasie (rozbieżność PSI lub KL w przypadku szybkiego osadzania) oraz trendy oceny wyników. Alerty zasilają Prometheus Alertmanager, a następnie Slack / PagerDuty. Interfejs użytkownika to Next.js 15 z Recharts.

## Architektura

```
production apps:
  OpenAI SDK  +  Anthropic SDK  +  Google GenAI SDK
  LangChain + LlamaIndex + vLLM
       |
       v
  OpenTelemetry SDK with GenAI semconv
       |
       v  OTLP HTTP
  collector (ingest, sample, fan-out)
       |
       +-------------+-----------+
       v             v           v
   ClickHouse    Postgres    S3 archive
   (spans)       (metadata)  (raw events)
       |
       +---> eval jobs (DeepEval, RAGAS, LLM-judge)
       |     sampled or all-trace
       |     write eval spans back
       |
       +---> drift detector (PSI / KL on prompt embeddings)
       |
       +---> Prometheus metrics -> Alertmanager -> Slack / PagerDuty
       |
       v
   Next.js 15 dashboard (Recharts)
```

## Stos

- Pozyskiwanie: zestawy SDK OpenTelemetry + konwencje semantyczne GenAI; Transport HTTP OTLP
- Kolektor: Kolektor OpenTelemetry z procesorem próbkowania ogonowego (w celu kontroli kosztów)
- Przechowywanie: ClickHouse dla rozpiętości, Postgres dla metadanych, S3 dla surowego archiwum zdarzeń
- Evals: DeepEval, RAGAS 0.2, pakiet ewaluacyjny Arize Phoenix, niestandardowy sędzia LLM
- Dryft: PSI / KL w przypadku zbiorczego osadzania podpowiedzi (transformatory zdań) co tydzień
- Alarmowanie: Prometheus Alertmanager -> Slack / PagerDuty
- Interfejs użytkownika: Next.js 15 App Router + Recharts + akcje serwera
- Obsługiwane pakiety SDK: OpenAI, Anthropic, Google GenAI, LangChain, LlamaIndex, vLLM

## Zbuduj to

1. **Konfiguracja kolektora.** OpenTelemetry Collector z odbiornikiem OTLP HTTP, próbnikiem końcowym przechowującym 100% błędnych śladów i 10% sukcesów oraz eksporterami do ClickHouse i S3.

2. **Schemat ClickHouse.** Tabela `spans` z kolumnami odzwierciedlającymi semconv GenAI: `gen_ai_system`, `gen_ai_request_model`, `input_tokens`, `output_tokens`, `latency_ms`, `prompt_hash`, `trace_id`, `parent_span_id` oraz torbę JSON na długie ładunki. Dodaj indeksy dodatkowe według user_id i app_id.

3. **Test pokrycia SDK.** Napisz małą aplikację kliencką używając każdego SDK (OpenAI, Anthropic, Google, LangChain, LlamaIndex, vLLM) z automatycznym instrumentem OpenLLMetry. Sprawdź, czy każdy generuje kanoniczne zakresy GenAI, które trafiają do ClickHouse.

4. **Zadania Eval.** Zaplanowane zadanie odczytuje próbki śladów z ostatnich 15 minut i sprawdza wierność, toksyczność oraz trafność odpowiedzi DeepEval. Dane wyjściowe to eval spany powiązane ze ścieżką nadrzędną.

5. **Niestandardowy sędzia LLM.** Sędzia ds. wycieku danych osobowych: po otrzymaniu odpowiedzi zadzwoń do strażnika LLM, aby ocenić prawdopodobieństwo wycieku danych osobowych. Odpowiedzi z najlepszymi wynikami trafiają do kolejki selekcji.

6. **Wykrywanie dryfu.** Cotygodniowe zadanie oblicza PSI pomiędzy zbiorczymi osadzaniami podpowiedzi w tym tygodniu a końcową 4-tygodniową linią bazową. Jeśli PSI przekracza próg, alarmuj.

7. **Dashboard.** Next.js 15 ze stronami: przegląd (rozpiętość/s, koszt/użytkownik, opóźnienie p95), ślady (wyszukiwanie + kaskada), oceny (trend wierności, toksyczność), dryft (PSI w czasie), alerty.

8. **Łańcuch alertów.** Eksporter Prometheus odczytuje agregaty wyników eval i percentyle opóźnień; Alertmanager kieruje do Slacka w przypadku ostrzeżeń i PagerDuty w przypadku krytycznych naruszeń.

9. **Sonda regresyjna.** Wprowadź błąd: oceniany chatbot zaczyna wyciekać fałszywe numery SSN w 1% przypadków. Zmierz MTTR: ​​od wprowadzonego błędu do alertu Slack.

## Użyj tego

```
$ curl -X POST https://my-otel-collector/v1/traces -d @trace.json
[collector]  accepted 1 trace, 3 spans
[clickhouse] inserted 3 spans (app=chat, user=u_42)
[eval]       DeepEval faithfulness 0.82, toxicity 0.03
[drift]      weekly PSI 0.08 (below 0.2 threshold)
[ui]         live at https://obs.example.com
```

## Wyślij to

Elementem dostawy jest `outputs/skill-llm-observability.md`. W przypadku aplikacji LLM pulpit nawigacyjny pobiera ślady, przeprowadza oceny, ostrzega o dryfowaniu i wyświetla podział kosztów na użytkowników w Next.js.

| Waga | Kryterium | Jak to się mierzy |
|:-:|---|---|
| 25 | Pokrycie schematu śledzenia | Liczba rodzin SDK tworzących kanoniczne zakresy GenAI (docelowo: 6+) |
| 20 | Poprawność oceny | Wyniki DeepEval / RAGAS w porównaniu z zestawem ręcznie oznakowanym |
| 20 | UX panelu | MTTR przy wstrzykniętej regresji (docelowo poniżej 5 minut) |
| 20 | Koszt/skala | Ciągłe pozyskiwanie z szybkością 1 tys. rozpiętości/s bez zaległości |
| 15 | Alarmowanie + wykrywanie dryfu | Łańcuch Prometheus/Alertmanager przećwiczony od początku do końca |
| **100** | | |

## Ćwiczenia

1. Dodaj niestandardowe instrumentarium dla środowiska Haystack. Zweryfikuj zakresy kanoniczne w ClickHouse z wiernymi atrybutami `gen_ai.*`.

2. Zamień DeepEval na ewaluatory Phoenix na tych samych śladach. Zmierz dryft wyników pomiędzy dwoma silnikami ewaluacyjnymi.

3. Wyostrz detektor dryfu: obliczaj PSI dla każdego identyfikatora aplikacji, a nie globalnie. Pokaż trasy driftu dla poszczególnych aplikacji.

4. Dodaj stronę „wpływ na użytkownika”: koszt na użytkownika i wskaźnik awaryjności na użytkownika z wykresami przebiegu w czasie.

5. Stwórz politykę pobierania próbek końcowych, która pozwoli zachować 100% śladów o toksyczności > 0,5 plus 10% próbki warstwowej pozostałych. Wprowadzono błąd próbkowania.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| GenAI semconv | „Atrybuty Otel LLM” | Specyfikacja OpenTelemetry 2025 dla atrybutów zakresu LLM (system, model, tokeny) |
| Próbkowanie ogona | „Próbka pośladowa” | Moduł zbierający decyduje się zachować lub usunąć śledzenie po jego zakończeniu (może podglądać błędy) |
| PSI | „Wskaźnik stabilności populacji” | Metryka dryfu porównująca dwa rozkłady; > 0,2 zazwyczaj sygnalizuje znaczący dryft |
| Sędzia LLM | „Eval jako model” | LLM oceniający wyniki innego LLM w rubryce (wierność, toksyczność, PII) |
| Polityka pobierania próbek ogonów | „Zachowaj regułę” | Reguła decydująca, które ślady mają się utrzymać, a jakie zostać usunięte; błąd + częstotliwość próbkowania |
| Rozpiętość ewaluacyjna | „Połączony ślad eval” | Rozpiętość podrzędna niosąca wynik ewaluacyjny powiązany z oryginalnym zakresem połączeń LLM |
| Koszt na użytkownika | „Ekonomika jednostkowa” | Koszt w dolarach przypisany do user_id w oknie; kluczowy wskaźnik produktu |

## Dalsze czytanie

- [Langfuse](https://github.com/langfuse/langfuse) — referencyjna platforma obserwacyjna typu open-core
- [Arize Phoenix](https://github.com/Arize-ai/phoenix) — alternatywne odniesienie z silną obsługą dryfu
- [OpenLLMetry (Traceloop)](https://github.com/traceloop/openllmetry) — rodzina SDK do automatycznego oprzyrządowania
- [Konwencje semantyczne OpenTelemetry GenAI](https://opentelemetry.io/docs/specs/semconv/gen-ai/) — schemat pozyskiwania
- [Helicone](https://www.helicone.ai) — obserwowalność hostowana na alternatywnym serwerze
- [Braintrust](https://www.braintrust.dev) — alternatywna platforma eval-first
- [Dokumentacja ClickHouse](https://clickhouse.com/docs) — sklep z rozpiętościami kolumnowymi
- [DeepEval](https://github.com/confident-ai/deepeval) — biblioteka ewaluatora