# OpenTelemetry GenAI — narzędzie do śledzenia wywołań kompleksowo

> Agent wywołuje pięć narzędzi, trzy serwery MCP i dwóch podagentów. Potrzebujesz jednego śladu na tym wszystkim. Konwencje semantyczne OpenTelemetry GenAI (stabilne atrybuty w wersji 1.37 i nowszych) to standard 2026, natywnie obsługiwany przez Datadog, Langfuse, Arize Phoenix, OpenLLMetry i AgentOps. W tej lekcji wymieniono wymagane atrybuty, omówiono hierarchię zakresu (agent → LLM → narzędzie) i przedstawiono emiter zakresu stdlib, który można podłączyć do dowolnego eksportera Otel.

**Typ:** Kompilacja
**Języki:** Python (stdlib, emiter zakresu Otel)
**Wymagania wstępne:** Faza 13 · 07 (serwer MCP), Faza 13 · 08 (klient MCP)
**Czas:** ~75 minut

## Cele nauczania

- Nazwij wymagane atrybuty Otel GenAI dla zakresu LLM i zakresu wykonywania narzędzi.
- Zbuduj hierarchię śledzenia obejmującą pętlę agenta, wywołanie LLM, wywołanie narzędzia i wysyłkę klienta MCP.
- Zdecyduj, jaką treść przechwycić (opcja) lub zredagować (domyślnie).
- Emituj zakresy do lokalnego kolektora (Jaeger, Langfuse) bez przepisywania kodu narzędzia.

## Problem

Debugowanie z lutego 2026 r.: użytkownicy zgłaszają, że „mojemu agentowi czasami odpowiedź zajmuje 30 sekund, innym razem 3 sekundy”. Żadnych śladów. Dzienniki pokazują wywołanie LLM, ale nie wysyłkę narzędzia, nie obie strony serwera MCP, a nie subagenta. Zgadujesz. W końcu stwierdzasz: jeden serwer MCP czasami zawiesza się podczas zimnego startu.

Bez kompleksowego śledzenia nie można tego znaleźć. Otel GenAI rozwiązuje ten problem.

Konwencje rozstrzygnęły się w latach 2025-2026 w ramach grupy konwencji semantycznych OpenTelemetry. Definiują stabilne nazwy atrybutów, więc Datadog, Langfuse, Phoenix, OpenLLMetry i AgentOps analizują te same zakresy. Instrument raz; wysłać do dowolnego backendu.

## Koncepcja

### Hierarchia zakresu

```
agent.invoke_agent  (top, INTERNAL span)
 ├── llm.chat       (CLIENT span)
 ├── tool.execute   (INTERNAL)
 │    └── mcp.call  (CLIENT span)
 ├── llm.chat       (CLIENT span)
 └── subagent.invoke (INTERNAL)
```

Całość jest zagnieżdżona pod jednym identyfikatorem śledzenia. Identyfikatory zakresu łączą relacje rodzic-dziecko.

### Wymagane atrybuty

Według semconv 2025–2026:

- `gen_ai.operation.name` — `"chat"`, `"text_completion"`, `"embeddings"`, `"execute_tool"`, `"invoke_agent"`.
- `gen_ai.provider.name` — `"openai"`, `"anthropic"`, `"google"`, `"azure_openai"`.
- `gen_ai.request.model` — żądany ciąg modelu (np. `"gpt-4o-2024-08-06"`).
- `gen_ai.response.model` — faktycznie obsługiwany model.
- `gen_ai.usage.input_tokens` / `gen_ai.usage.output_tokens`.
- `gen_ai.response.id` — identyfikator odpowiedzi dostawcy dla korelacji.

Dla rozpiętości narzędzi:

- `gen_ai.tool.name` — identyfikator narzędzia.
- `gen_ai.tool.call.id` — konkretny identyfikator połączenia.
- `gen_ai.tool.description` — opis narzędzia (opcjonalnie).

W przypadku zakresów agentów:

- `gen_ai.agent.name` / `gen_ai.agent.id` / `gen_ai.agent.description`.

### Rodzaje rozpiętości

- `SpanKind.CLIENT` dla wywołań przekraczających granicę procesu (dostawca LLM, serwer MCP).
- `SpanKind.INTERNAL` dla własnych kroków pętli agenta i wykonania narzędzia.

### Włącz przechwytywanie treści

Domyślnie zakresy zawierają metryki i czas — nie monity ani uzupełnienia. Duże ładunki i informacje umożliwiające identyfikację są domyślnie wyłączone. Ustaw `OTEL_SEMCONV_STABILITY_OPT_IN=gen_ai_latest_experimental` i określone zmienne środowiskowe przechwytywania treści, aby uwzględnić treść. Przejrzyj uważnie przed włączeniem w prod.

### Zdarzenia na przęsłach

Zdarzenia na poziomie tokenu można dodać jako zdarzenia zakresu:

- `gen_ai.content.prompt` — wiadomości wejściowe.
- `gen_ai.content.completion` — komunikaty wyjściowe.
- `gen_ai.content.tool_call` — wywołanie narzędzia zgodnie z zapisem.

Kolejność wydarzeń w określonym przedziale czasu w celu szczegółowego odtworzenia.

### Eksporterzy

Otel obejmuje eksport do:

- **Jaeger / Tempo.** OSS, lokalnie.
- **Langfuse.** Specyficzne dla obserwowalności LLM; wizualizuje użycie tokena.
- **Arize Phoenix.** Łączne wartości + śledzenie.
- **Datadog.** Komercyjny; natywnie analizuje atrybuty `gen_ai.*`.
- **Plaster miodu.** Zorientowany na kolumnę; przyjazne dla zapytań.

Wszyscy mówią w formacie OTLP, w formacie przewodowym. Twój kod nie obchodzi.

### Propagacja w MCP

Kiedy klient MCP wywołuje serwer, wstrzyknij do żądania nagłówek śledzenia W3C. Przesyłany strumieniowo protokół HTTP obsługuje standardowe nagłówki. Stdio nie obsługuje natywnie nagłówków HTTP; plan działania specyfikacji na rok 2026 omawia dodanie pola `_meta.traceparent` w wywołaniach JSON-RPC.

Dopóki to nie nastąpi: ręcznie dołącz element śledzenia do `_meta` każdego żądania. Serwer rejestruje identyfikator śledzenia.

### Metryki

Oprócz rozpiętości, semconv GenAI definiuje metryki:

- `gen_ai.client.token.usage` — histogram.
- `gen_ai.client.operation.duration` — histogram.
- `gen_ai.tool.execution.duration` — histogram.

Użyj ich w przypadku pulpitów nawigacyjnych, które nie wymagają szczegółów poszczególnych połączeń.

### Warstwa AgentOps

AgentOps (założony w 2024 r.) specjalizuje się w obserwowalności GenAI. Opakowuje popularne frameworki (LangGraph, Pydantic AI, CrewAI), aby automatycznie emitować rozpiętości OTel. Przydatne, jeśli Twój stos korzysta z obsługiwanego frameworka; w przeciwnym razie użyj oprzyrządowania ręcznego.

## Użyj tego

`code/main.py` emituje zakresy w kształcie OTel na standardowe wyjście (w formacie podobnym do OTLP-JSON) dla agenta, który wywołuje LLM, wysyła dwa narzędzia i wykonuje jedną podróż w obie strony MCP. Żaden prawdziwy eksporter — lekcja koncentruje się na kształcie zakresu i zestawie atrybutów. Wklej wynik do przeglądarki kompatybilnej z OTLP lub po prostu go przeczytaj.

Na co zwrócić uwagę:

- Identyfikator śledzenia jest wspólny dla wszystkich zakresów.
- Linki rodzic-dziecko są kodowane za pomocą `parentSpanId`.
- Wypełniono wymagane atrybuty `gen_ai.*`.
- Przechwytywanie treści jest domyślnie wyłączone; jeden scenariusz włącza to poprzez env var.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-otel-genai-instrumentation.md`. Biorąc pod uwagę bazę kodu agenta, umiejętność tworzy plan instrumentacji: gdzie dodać zakresy, które atrybuty należy wypełnić i którzy eksporterzy są celem.

## Ćwiczenia

1. Uruchom `code/main.py`. Policz rozpiętości i określ, który jest KLIENTEM, a który WEWNĘTRZNY.

2. Włącz przechwytywanie treści (env var) i potwierdź pojawienie się zdarzeń `gen_ai.content.prompt` i `gen_ai.content.completion`. Zwróć uwagę na konsekwencje dla danych osobowych.

3. Dodaj metrykę wykonania narzędzia `gen_ai.tool.execution.duration` i wyemituj ją jako próbkę histogramu na wywołanie.

4. Propaguj element śledzenia z zakresu agenta nadrzędnego do pola `_meta.traceparent` żądania MCP. Sprawdź, czy serwer MCP zobaczy ten sam identyfikator śledzenia.

5. Przeczytaj specyfikację semconv Otel GenAI. Wskaż jeden atrybut wymieniony w pliku semconv, którego NIE emituje kod tej lekcji. Dodaj to.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Otel | „Otwarta telemetria” | Otwarty standard dla śladów, metryk i logów |
| GenAI semconv | „Konwencje semantyczne GenAI” | Stabilne nazwy atrybutów dla rozpiętości LLM / narzędzia / agenta |
| `gen_ai.*` | „Przestrzeń nazw atrybutów” | Wszystkie atrybuty GenAI mają ten sam przedrostek |
| Rozpiętość | „Operacja czasowa” | Jednostka pracy z początkiem, końcem i atrybutami |
| Ślad | „Pochodzenie między rozpiętościami” | Drzewo rozpiętości dzielące identyfikator śledzenia |
| SpanKind | „KLIENT / SERWER / WEWNĘTRZNY” | Wskazówki dotyczące kierunku przęsła |
| OTLP | „Protokół linii OpenTelemetry” | Format drutu dla eksporterów |
| Treść zgody | „Monit/przechwytywanie zakończenia” | Domyślnie wyłączone; env var, aby włączyć |
| śladowy rodzic | „Nagłówek W3C” | Propaguje kontekst śledzenia między usługami |
| Eksporter | „Nadawca specyficzny dla backendu” | Komponent wysyłający rozpiętości do Jaeger / Datadog / itp. |

## Dalsze czytanie

- [OpenTelemetry — GenAI semconv](https://opentelemetry.io/docs/specs/semconv/gen-ai/) — kanoniczne konwencje dotyczące rozpiętości, metryk i zdarzeń GenAI
- [OpenTelemetry — zakresy GenAI](https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-spans/) — lista atrybutów LLM i zakresu wykonywania narzędzi
- [OpenTelemetry — zakresy agentów GenAI](https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-agent-spans/) — poziom agenta `invoke_agent` zakres
- [open-telemetry/semantic-conventions — GenAI spans](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-spans.md) — źródło prawdy hostowane na GitHubie
- [Datadog — konwencja semantyczna LLM Otel](https://www.datadoghq.com/blog/llm-otel-semantic-convention/) — przewodnik po integracji produkcyjnej