# OpenTelemetry GenAI — kompleksowe śledzenie wywołań (End-to-End Tracing)

> Gdy agent wywołuje pięć narzędzi, trzy serwery MCP i dwóch subagentów, kluczowe jest posiadanie jednego, spójnego śladu (trace) dla całego procesu. Konwencje semantyczne OpenTelemetry GenAI (stabilne atrybuty w wersji 1.37 i nowszych) to standard w 2026 roku, natywnie wspierany przez Datadog, Langfuse, Arize Phoenix, OpenLLMetry i AgentOps. W tej lekcji omawiamy wymagane atrybuty, hierarchię zakresów (Span hierarchy: agent → LLM → tool) oraz przedstawiamy emiter oparty na bibliotece standardowej Pythona, który można zintegrować z dowolnym eksporterem OpenTelemetry (OTel).

**Typ:** Implementacja
**Język:** Python (biblioteka standardowa, emiter zakresów OTel)
**Wymagania wstępne:** Faza 13 · 07 (serwer MCP), Faza 13 · 08 (klient MCP)
**Czas:** ~75 minut

## Cele lekcji

- Zdefiniowanie wymaganych atrybutów OTel GenAI dla zakresów LLM oraz zakresów wykonania narzędzi.
- Zaprojektowanie hierarchii śledzenia (tracing hierarchy) obejmującej pętlę agenta, zapytania LLM, wywołania narzędzi oraz żądania klienta MCP.
- Określenie zasad rejestrowania treści (opcjonalne przechwytywanie danych wejściowych/wyjściowych lub domyślne ich maskowanie).
- Emitowanie danych telemetrycznych (spans) do lokalnego kolektora (np. Jaeger, Langfuse) bez konieczności modyfikowania logiki narzędzi.

## Problem

Scenariusz debugowania (luty 2026 r.): użytkownicy zgłaszają błąd: „odpowiedź agenta zajmuje czasami 3 sekundy, a czasami aż 30 sekund”. Brak jakiejkolwiek telemetrii. Logi pokazują jedynie wywołanie LLM, ale milczą na temat zapytań do narzędzi, komunikacji po stronie serwera MCP czy wywołań subagentów. Jedyne, co pozostaje, to domysły. Ostatecznie okazuje się, że jeden z serwerów MCP sporadycznie zawiesza się podczas zimnego startu (cold start).

Bez kompleksowego śledzenia (end-to-end tracing) zdiagnozowanie takich problemów jest niemożliwe. Standard OTel GenAI skutecznie rozwiązuje to wyzwanie.

W latach 2025-2026 grupa robocza OpenTelemetry zdefiniowała stabilne konwencje semantyczne (semantic conventions). Określają one jednolite nazwy atrybutów, dzięki czemu platformy takie jak Datadog, Langfuse, Phoenix, OpenLLMetry czy AgentOps interpretują te same struktury danych. Oznacza to, że oprzyrządowanie (instrumentation) kodu wykonuje się raz, a dane można wysłać do dowolnego systemu monitorowania.

## Założenia koncepcyjne

### Hierarchia zakresów (Span Hierarchy)

```
agent.invoke_agent  (top, INTERNAL span)
 ├── llm.chat       (CLIENT span)
 ├── tool.execute   (INTERNAL)
 │    └── mcp.call  (CLIENT span)
 ├── llm.chat       (CLIENT span)
 └── subagent.invoke (INTERNAL)
```

Wszystkie zakresy (spans) są powiązane z jednym identyfikatorem śledzenia (`trace_id`). Relacje nadrzędny-podrzędny (parent-child) są określane przez identyfikatory zakresów.

### Wymagane atrybuty

Zgodnie ze standardem semconv na lata 2025–2026:

- `gen_ai.operation.name` — `"chat"`, `"text_completion"`, `"embeddings"`, `"execute_tool"`, `"invoke_agent"`.
- `gen_ai.provider.name` — `"openai"`, `"anthropic"`, `"google"`, `"azure_openai"`.
- `gen_ai.request.model` — żądany ciąg modelu (np. `"gpt-4o-2024-08-06"`).
- `gen_ai.response.model` — faktycznie obsłużony model.
- `gen_ai.usage.input_tokens` / `gen_ai.usage.output_tokens`.
- `gen_ai.response.id` — identyfikator odpowiedzi dostawcy dla korelacji.

Dla zakresów wywołań narzędzi:

- `gen_ai.tool.name` — identyfikator narzędzia.
- `gen_ai.tool.call.id` — konkretny identyfikator połączenia.
- `gen_ai.tool.description` — opis narzędzia (opcjonalnie).

W przypadku zakresów pracy agentów:

- `gen_ai.agent.name` / `gen_ai.agent.id` / `gen_ai.agent.description`.

### Typy zakresów (SpanKind)

- `SpanKind.CLIENT` dla wywołań wychodzących poza proces lokalny (np. zapytania do API LLM, wywołania serwera MCP).
- `SpanKind.INTERNAL` dla wewnętrznych operacji pętli agenta oraz lokalnego wykonania narzędzi.

### Przechwytywanie treści (Content Opt-In)

Domyślnie telemetria rejestruje jedynie czasy wykonania i metryki – nie zapisuje zapytań (prompts) ani odpowiedzi (completions). Dane osobowe (PII) oraz duże ładunki są domyślnie maskowane. Aby włączyć rejestrowanie treści, należy ustawić zmienną środowiskową `OTEL_SEMCONV_STABILITY_OPT_IN=gen_ai_latest_experimental` oraz odpowiednie flagi przechwytywania. Należy zachować szczególną ostrożność przed wdrożeniem tej konfiguracji w środowisku produkcyjnym.

### Zdarzenia w zakresach (Span Events)

Zdarzenia w pętli generowania tokenów mogą być rejestrowane jako zdarzenia zakresu (Span Events):

- `gen_ai.content.prompt` — treść zapytania wejściowego.
- `gen_ai.content.completion` — wygenerowana odpowiedź.
- `gen_ai.content.tool_call` — zarejestrowane wywołanie narzędzia.

Utrzymanie kolejności zdarzeń w czasie pozwala na precyzyjne odtworzenie przebiegu interakcji.

### Systemy monitorowania (Exporters)

OpenTelemetry wspiera eksport danych telemetrycznych do systemów takich jak:

- **Jaeger / Tempo.** Rozwiązania Open Source do uruchomienia lokalnego.
- **Langfuse.** Platforma dedykowana dla aplikacji GenAI, wizualizująca m.in. zużycie tokenów.
- **Arize Phoenix.** Analiza jakościowa i śledzenie modeli.
- **Datadog.** Komercyjny system APM wspierający analizę atrybutów `gen_ai.*`.
- **Honeycomb.** Zorientowana kolumnowo baza danych ułatwiająca analizę zapytań.

Wszystkie te systemy komunikują się przy użyciu standardowego protokołu OTLP. Z punktu widzenia kodu dewelopera transport jest przezroczysty.

### Propagacja kontekstu w MCP

Gdy klient MCP wykonuje zapytanie do serwera, powinien wstrzyknąć nagłówek śledzenia zgodny ze standardem W3C (traceparent). O ile transport HTTP (SSE) natywnie obsługuje nagłówki, o tyle transport stdio wymaga alternatywnego podejścia. W planach specyfikacji MCP na 2026 rok przewidziano dodanie pola `_meta.traceparent` bezpośrednio w wywołaniach JSON-RPC.

Do czasu standaryzacji zaleca się ręczne dołączanie kontekstu śledzenia do obiektu `_meta` w każdym żądaniu, aby serwer mógł powiązać logi z tą samą sesją.

### Metryki

Oprócz zakresów (spans), konwencja GenAI określa standardowe metryki:

- `gen_ai.client.token.usage` — histogram zużycia tokenów.
- `gen_ai.client.operation.duration` — histogram czasu operacji LLM.
- `gen_ai.tool.execution.duration` — histogram czasu wykonania narzędzi.

Metryki te są idealne do tworzenia agregacyjnych pulpitów nawigacyjnych (dashboards) bez potrzeby analizowania szczegółów poszczególnych transakcji.

### Biblioteka AgentOps

AgentOps (platforma rozwijana od 2024 r.) specjalizuje się w monitorowaniu aplikacji GenAI. Udostępnia ona integracje (wrappers) dla popularnych frameworków (takich jak LangGraph, Pydantic AI, CrewAI), automatycznie generując zakresy OTel. Ułatwia to pracę, jeśli projekt bazuje na tych narzędziach; w przeciwnym razie konieczne jest ręczne dodanie oprzyrządowania.

## Zastosowanie w praktyce

Skrypt `code/main.py` generuje i wypisuje zakresy zgodne z formatem OTel (zbliżone do struktury OTLP-JSON) na standardowe wyjście. Symuluje on agenta odpytującego LLM, wywołującego dwa narzędzia oraz realizującego jedną sesję MCP. Skupiamy się na strukturze zakresów i zestawie atrybutów, bez wdrażania fizycznego eksportera telemetrycznego. Dane wyjściowe można wkleić do wizualizatora kompatybilnego z OTLP.

Kluczowe elementy:

- Wspólny identyfikator śledzenia (`traceId`) łączący wszystkie zakresy.
- Powiązania nadrzędny-podrzędny zdefiniowane polem `parentSpanId`.
- Obecność wymaganych atrybutów z przestrzeni `gen_ai.*`.
- Domyślne wyłączenie przechwytywania treści wejściowych/wyjściowych i możliwość jego aktywacji za pomocą zmiennej środowiskowej.

## Zadanie praktyczne

Wynikiem tej lekcji powinno być przygotowanie pliku `outputs/skill-otel-genai-instrumentation.md`. Na podstawie analizy bazy kodu agenta należy opracować plan oprzyrządowania telemetrycznego (instrumentation plan) wskazujący: miejsca wstrzykiwania zakresów, wymagane atrybuty oraz rekomendacje dotyczące wyboru systemu monitorowania (exporter).

## Ćwiczenia

1. Uruchom skrypt `code/main.py`. Policz wygenerowane zakresy i określ, które z nich mają typ `CLIENT`, a które `INTERNAL`.

2. Aktywuj przechwytywanie treści za pomocą zmiennej środowiskowej i upewnij się, że w logach pojawiają się zdarzenia `gen_ai.content.prompt` oraz `gen_ai.content.completion`. Przeanalizuj ryzyko wycieku danych osobowych (PII) do systemów monitorowania.

3. Zaimplementuj rejestrowanie metryki `gen_ai.tool.execution.duration` i wyemituj ją w postaci próbki histogramu dla każdego wywołania narzędzia.

4. Zaimplementuj przekazywanie kontekstu śledzenia (traceparent) z nadrzędnego zakresu agenta do obiektu `_meta.traceparent` w żądaniu MCP. Zweryfikuj, czy serwer MCP poprawnie odczytuje i wiąże ten sam identyfikator śledzenia.

5. Zapoznaj się ze specyfikacją semconv OTel GenAI. Wskaż jeden atrybut wymieniony w standardzie, który nie został uwzględniony w przykładowym kodzie, i zaimplementuj jego obsługę.

## Kluczowe pojęcia

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| OTel | „Telemetria systemowa” | OpenTelemetry – otwarty standard zbierania śladów (traces), metryk i logów |
| GenAI semconv | „Słownik atrybutów GenAI” | Konwencje semantyczne określające jednolite nazwy atrybutów dla zakresów LLM, agentów i narzędzi |
| gen_ai.* | „Prefiks atrybutów” | Jednolity przedrostek dla wszystkich atrybutów telemetrycznych powiązanych z systemami GenAI |
| Zakres (Span) | „Jednostka pracy” | Reprezentacja pojedynczej operacji w czasie, zawierająca czas startu, końca oraz atrybuty |
| Ślad (Trace) | „Przebieg transakcji” | Kompletny graf (drzewo) zakresów połączonych wspólnym identyfikatorem śledzenia |
| SpanKind | „Typ zakresu” | Określenie roli zakresu (np. CLIENT, SERVER, INTERNAL) ułatwiające analizę przepływu |
| OTLP | „Protokół transportowy OTel” | OpenTelemetry Protocol – format przesyłania danych telemetrycznych drogą sieciową |
| Content Opt-In | „Przechwytywanie treści” | Mechanizm rejestrowania zapytań i odpowiedzi (domyślnie wyłączony ze względów bezpieczeństwa) |
| traceparent | „Nagłówek propagacji” | Standardowy nagłówek W3C służący do przesyłania kontekstu śledzenia między rozproszonymi usługami |
| Eksporter (Exporter) | „Moduł wysyłający” | Komponent odpowiedzialny za przekazywanie danych telemetrycznych do systemów monitorowania (np. Jaeger, Datadog) |

## Polecana literatura / dokumentacja

- [OpenTelemetry — GenAI semconv](https://opentelemetry.io/docs/specs/semconv/gen-ai/) — kanoniczne konwencje dotyczące rozpiętości, metryk i zdarzeń GenAI
- [OpenTelemetry — zakresy GenAI](https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-spans/) — lista atrybutów LLM i zakresu wykonywania narzędzi
- [OpenTelemetry — zakresy agentów GenAI](https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-agent-spans/) — poziom agenta `invoke_agent` zakres
- [open-telemetry/semantic-conventions — GenAI spans](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-spans.md) — źródło prawdy hostowane na GitHubie
- [Datadog — konwencja semantyczna LLM Otel](https://www.datadoghq.com/blog/llm-otel-semantic-convention/) — przewodnik po integracji produkcyjnej
