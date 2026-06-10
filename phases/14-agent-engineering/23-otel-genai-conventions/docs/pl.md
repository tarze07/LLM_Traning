# Konwencje semantyczne OpenTelemetry GenAI

> Rozwiązanie GenAI SIG firmy OpenTelemetry (uruchomione w kwietniu 2024 r.) definiuje standardowy schemat telemetrii agentów. Nazwy zakresów, atrybuty i zasady przechwytywania treści są zbieżne u różnych dostawców, więc śledzenie agentów oznacza to samo w Datadog, Grafana, Jaeger i Honeycomb.

**Typ:** Ucz się + Buduj
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 14 · 13 (LangGraph), Faza 14 · 24 (platformy obserwowalności)
**Czas:** ~60 minut

## Cele nauczania

- Nazwij kategorie zakresu GenAI: model/klient, agent, narzędzie.
- Rozróżnij zakresy `invoke_agent` KLIENT i WEWNĘTRZNY oraz kiedy każdy z nich ma zastosowanie.
- Lista atrybutów GenAI najwyższego poziomu: nazwa dostawcy, model żądania, identyfikator źródła danych.
- Wyjaśnij umowę dotyczącą przechwytywania treści: zgoda, `OTEL_SEMCONV_STABILITY_OPT_IN`, rekomendacja dotycząca odniesień zewnętrznych.

## Problem

Każdy sprzedawca wymyśla własne nazwy zakresów. Zespoły operacyjne tworzą pulpity nawigacyjne dla poszczególnych platform. Rozwiązanie GenAI SIG firmy OpenTelemetry rozwiązuje ten problem, definiując jeden standard, na który ma być ukierunkowany cały ekosystem.

## Koncepcja

### Kategorie zakresu

1. **Rozpiętość modelu / klienta.** Obejmuje surowe połączenia LLM. Emitowane przez pakiety SDK dostawców (Anthropic, OpenAI, Bedrock) i adaptery modeli strukturalnych.
2. **Agent spans.** `create_agent` (kiedy agent jest skonstruowany) i `invoke_agent` (kiedy działa).
3. **Rozpiętość narzędzi.** Jeden na wywołanie narzędzia; połączony z obszarem agenta poprzez relację rodzic-dziecko.

### Nazewnictwo zakresu agentów

- Nazwa zakresu: `invoke_agent {gen_ai.agent.name}`, jeśli jest nazwany; powrót do `invoke_agent`.
- Rodzaj przęsła:
  - **KLIENT** — dla usług agenta zdalnego (OpenAI Assistants API, Bedrock Agents).
  - **INTERNAL** — dla frameworków agentów w procesie (LangChain, CrewAI, lokalny ReAct).

### Kluczowe atrybuty

- `gen_ai.provider.name` — `anthropic`, `openai`, `aws.bedrock`, `google.vertex`.
- `gen_ai.request.model` — identyfikator modelu.
- `gen_ai.response.model` — rozwiązany model (może różnić się od żądania ze względu na routing).
- `gen_ai.agent.name` — identyfikator agenta.
- `gen_ai.operation.name` — `chat`, `completion`, `invoke_agent`, `tool_call`.
- `gen_ai.data_source.id` — dla RAG: który korpus lub sklep był konsultowany.

Istnieją konwencje specyficzne dla technologii dla Anthropic, Azure AI Inference, AWS Bedrock i OpenAI.

### Przechwytywanie treści

Domyślna zasada: oprzyrządowanie NIE POWINNO domyślnie przechwytywać wejść/wyjść. Na przechwytywanie można wyrazić zgodę poprzez:

- `gen_ai.system_instructions`
- `gen_ai.input.messages`
- `gen_ai.output.messages`

Zalecany wzorzec produkcji: przechowuj zawartość zewnętrznie (S3, magazyn dzienników), rejestruj odniesienia na przęsłach (identyfikatory wskaźników, nie proza). To jest obrona przed zatruciem treści z Lekcji 27, połączona z obserwowalnością.

### Stabilność

Większość konwencji ma charakter eksperymentalny, stan na marzec 2026 r. Wyraź zgodę na stabilną wersję zapoznawczą, korzystając z:

```
OTEL_SEMCONV_STABILITY_OPT_IN=gen_ai_latest_experimental
```

Datadog v1.37+ odwzorowuje atrybuty GenAI natywnie na swój schemat obserwowalności LLM. Inne backendy (Grafana, Honeycomb, Jaeger) obsługują surowe atrybuty.

### Gdzie ten wzorzec jest błędny

- **Przechwytywanie pełnych monitów w różnych zakresach.** Dane osobowe, tajemnice i dane klientów w śladach, które mogą odczytać operatorzy. Przechowywać na zewnątrz.
- **Nie `gen_ai.provider.name`.** Pulpity nawigacyjne wielu dostawców ulegają awarii w przypadku braku przypisania.
- **Rozpiętości bez łączy nadrzędnych.** Osierocone rozpiętości narzędzi. Zawsze propaguj kontekst.
- **Brak ustawienia zgody na stabilność.** Nazwa Twoich atrybutów może zostać zmieniona podczas aktualizacji zaplecza.

## Zbuduj to

`code/main.py` implementuje emiter zakresu stdlib pasujący do konwencji GenAI:

- `Span` ze schematem atrybutów GenAI.
- `Tracer` z `start_span`, zagnieżdżonymi kontekstami.
- Uruchomienie agenta skryptowego, które emituje: `create_agent`, `invoke_agent` (INTERNAL), zakresy dla poszczególnych narzędzi, zakresy `chat` dla wywołań LLM.
- Tryb przechwytywania treści, który przechowuje monity zewnętrznie i rejestruje identyfikatory na zakresach.

Uruchom to:

```
python3 code/main.py
```

Dane wyjściowe: drzewo rozpiętości ze wszystkimi wymaganymi atrybutami GenAI oraz „zewnętrzny magazyn” pokazujący odniesienia do treści objętych zgodą.

## Użyj tego

- **Datadog LLM Observability** (v1.37+) natywnie mapuje atrybuty.
- **Langfuse / Phoenix / Opik** (Lekcja 24) — automatyczne instrumentowanie ekosystemu.
- **Jaeger / Honeycomb / Grafana Tempo** — surowe ślady OTel; buduj dashboardy na podstawie atrybutów GenAI.
- **Własny hosting** — uruchom Otel Collector z procesorem GenAI.

## Wyślij to

`outputs/skill-otel-genai.md` łączy Otel GenAI z istniejącym agentem z domyślnymi ustawieniami przechwytywania treści i pamięcią zewnętrzną.

## Ćwiczenia

1. Oprzyrząduj pętlę ReAct z Lekcji 01 za pomocą `invoke_agent` (WEWNĘTRZNIE) + rozpiętości dla poszczególnych narzędzi. Wyślij do instancji Jaeger.
2. Dodaj przechwytywanie treści w trybie „tylko odniesienia”: monituje SQLite, atrybuty zakresu zawierają tylko identyfikatory wierszy.
3. Przeczytaj specyfikację `gen_ai.data_source.id`. Podłącz go do wyszukiwania Mem0 w Lekcji 09.
4. Ustaw `OTEL_SEMCONV_STABILITY_OPT_IN=gen_ai_latest_experimental` i sprawdź, czy kolektor nie zmienił nazw Twoich atrybutów.
5. Zbuduj dashboard: „które błędy narzędzi korelują z jakimi modelami” na podstawie samych atrybutów GenAI.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| GenAI SIG | „Grupa OpenTelemetry GenAI” | Grupa robocza OTel określająca schemat |
| wywołaj_agenta | „Rozpiętość agentów” | Nazwa zakresu reprezentującego uruchomienie agenta |
| KLIENT rozpiętość | „Zdalne połączenie” | Zakres połączenia z usługą agenta zdalnego |
| Przęsło WEWNĘTRZNE | „W trakcie” | Zakres uruchomienia agenta w procesie |
| gen_ai.nazwa.dostawcy | „Dostawca” | anthropic / openai / aws.bedrock / google.vertex |
| gen_ai.data_source.id | „Źródło RAG” | Który korpus/magazyn został trafiony podczas pobierania |
| Przechwytywanie treści | „Szybkie logowanie” | Wyrażenie zgody na przechwytywanie wiadomości; przechowuj na zewnątrz w prod |
| Zgoda na stabilność | „Tryb podglądu” | Env var do przypinania konwencji eksperymentalnych |

## Dalsze czytanie

- [Konwencje semantyczne OpenTelemetry GenAI](https://opentelemetry.io/docs/specs/semconv/gen-ai/) — specyfikacja
- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/) — domyślne rozpiętości GenAI
- [AutoGen v0.4 (Microsoft Research)](https://www.microsoft.com/en-us/research/articles/autogen-v0-4-reimagining-the-foundation-of-agentic-ai-for-scale-extensibility-and-robustness/) — wbudowane rozpiętości Otel
- [Claude Agent SDK](https://platform.claude.com/docs/en/agent-sdk/overview) — propagacja kontekstu śledzenia W3C