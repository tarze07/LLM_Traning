# Konwencje semantyczne OpenTelemetry GenAI

> Inicjatywa GenAI SIG w ramach projektu OpenTelemetry (uruchomiona w kwietniu 2024 r.) definiuje standardowy schemat telemetrii dla agentów. Standaryzacja nazw spanów (zakresów), atrybutów oraz reguł przechwytywania treści sprawia, że dane telemetryczne są spójne i interpretowane w ten sam sposób w systemach takich jak Datadog, Grafana, Jaeger czy Honeycomb.

**Typ:** Ucz się + Buduj
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 14 · 13 (LangGraph), Faza 14 · 24 (platformy obserwowalności)
**Czas:** ~60 minut

## Cele nauczania

- Wymienić kategorie spanów w GenAI: model/klient, agent, narzędzie.
- Rozróżniać typy spanów `invoke_agent` (CLIENT vs INTERNAL) i określić scenariusze ich użycia.
- Wymienić kluczowe atrybuty GenAI najwyższego poziomu (np. nazwa dostawcy, wnioskowany model, identyfikator źródła danych).
- Wyjaśnić zasady bezpiecznego przechwytywania treści: tryb opt-in, flagę `OTEL_SEMCONV_STABILITY_OPT_IN` oraz rekomendację dotyczącą stosowania referencji zewnętrznych.

## Problem

Brak standardu sprawia, że każdy dostawca stosuje własne nazwy spanów, zmuszając zespoły operacyjne do budowania dedykowanych dashboardów dla każdej platformy osobno. Inicjatywa GenAI SIG w OpenTelemetry rozwiązuje ten problem, wprowadzając jednolity standard dla całego ekosystemu.

## Koncepcja

### Kategorie spanów

1. **Spany modelu / klienta (Model/Client spans).** Dotyczą bezpośrednich, surowych połączeń do LLM. Są one generowane przez oficjalne biblioteki SDK (np. Anthropic, OpenAI, Bedrock) oraz adaptery modeli.
2. **Spany agenta (Agent spans).** Reprezentują cykl życia agenta: `create_agent` (podczas inicjalizacji instancji) oraz `invoke_agent` (w trakcie jego działania).
3. **Spany narzędzi (Tool spans).** Generowane dla każdego wywołania narzędzia; są powiązane ze spanem agenta relacją nadrzędny-podrzędny (parent-child).

### Nazewnictwo spanów agenta

- Nazwa spanu: `invoke_agent {gen_ai.agent.name}` (jeśli agent posiada nazwę), w przeciwnym razie domyślnie `invoke_agent`.
- Typ spanu (Span Kind):
  - **CLIENT** – dla zdalnych usług agentycznych (np. OpenAI Assistants API, AWS Bedrock Agents).
  - **INTERNAL** – dla frameworków uruchamianych bezpośrednio w procesie aplikacji (np. LangGraph, CrewAI, lokalne pętle ReAct).

### Kluczowe atrybuty telemetryczne

- `gen_ai.provider.name` – nazwa dostawcy (np. `anthropic`, `openai`, `aws.bedrock`, `google.vertex`).
- `gen_ai.request.model` – identyfikator wnioskowanego modelu w żądaniu.
- `gen_ai.response.model` – rzeczywisty model, który wygenerował odpowiedź (może się różnić od żądanego w wyniku routingu).
- `gen_ai.agent.name` – unikalna nazwa/identyfikator agenta.
- `gen_ai.operation.name` – typ operacji (np. `chat`, `completion`, `invoke_agent`, `tool_call`).
- `gen_ai.data_source.id` – identyfikator źródła danych wykorzystanego w procesie pobierania (np. baza wektorowa w potokach RAG).

Istnieją konwencje specyficzne dla technologii dla Anthropic, Azure AI Inference, AWS Bedrock i OpenAI.

### Zbieranie treści (Content Capture)

Standardowa zasada: telemetria NIE POWINNO domyślnie rejestrować zawartości promptów ani odpowiedzi. Zgodę na rejestrowanie treści (opt-in) można aktywować dla atrybutów:

- `gen_ai.system_instructions`
- `gen_ai.input.messages`
- `gen_ai.output.messages`

Rekomendowane podejście produkcyjne: przechowuj surową treść komunikatów zewnętrznie (np. w chmurze S3 lub dedykowanym log store), a w spanach telemetrycznych rejestruj jedynie unikalne identyfikatory referencyjne. Pozwala to na pełną obserwowalność, chroniąc jednocześnie system przed wstrzyknięciem szkodliwej treści (Lekcja 27) oraz wyciekiem danych osobowych.

### Stabilność i wersjonowanie

Większość konwencji ma status eksperymentalny. Aby aktywować najnowszą stabilną wersję zapoznawczą, ustaw zmienną środowiskową:

```
OTEL_SEMCONV_STABILITY_OPT_IN=gen_ai_latest_experimental
```

System Datadog (od wersji v1.37) natywnie mapuje te atrybuty do swojego modułu LLM Observability. Inne platformy (np. Grafana, Honeycomb, Jaeger) interpretują je jako standardowe tagi/atrybuty OTel.

### Najczęstsze błędy wdrożeniowe

- **Rejestrowanie pełnych promptów bezpośrednio w spanach.** Prowadzi to do wycieku danych osobowych (PII), haseł lub poufnych danych klientów do logów telemetrii dostępnych dla operatorów. Dane te należy bezwzględnie przechowywać w wydzielonym, zewnętrznym bezpiecznym magazynie.
- **Pomijanie atrybutu `gen_ai.provider.name`.** Uniemożliwia to prawidłowe agregowanie i filtrowanie danych na dashboardach obsługujących wielu dostawców.
- **Gubienie powiązań nadrzędnych (Orphaned spans).** Tworzenie spanów dla narzędzi bez powiązania ich ze spanem nadrzędnym agenta. Kontekst śledzenia (trace context) must być zawsze prawidłowo propagowany.
- **Brak zdefiniowania zmiennej stabilności.** Może to skutkować nagłą zmianą nazw atrybutów przy aktualizacji bibliotek telemetrycznych, co popsuje działanie dashboardów.

## Przykład implementacji

Plik `code/main.py` zawiera przykładową implementację emitera spanów w oparciu o bibliotekę standardową, zgodną z konwencją GenAI:

- Zdefiniowano klasę `Span` obsługującą atrybuty standardu GenAI.
- Zaimplementowano klasę `Tracer` obsługującą zagnieżdżanie kontekstów (`start_span`).
- Przygotowano skryptowany przebieg agenta, który generuje spany: `create_agent`, `invoke_agent` (INTERNAL), spany wywołań narzędzi oraz spany operacji `chat` dla zapytań do LLM.
- Wdrożono tryb bezpiecznego zapisu treści, w którym prompty są przechowywane w zewnętrznym magazynie, a spany rejestrują jedynie unikalne identyfikatory referencyjne.

Uruchomienie:

```
python3 code/main.py
```

Dane wyjściowe prezentują drzewo spanów z przypisanymi atrybutami GenAI oraz zawartość „zewnętrznego magazynu” pokazującą powiązania referencyjne.

## Podsumowanie zastosowań

- **Datadog LLM Observability** (od wersji v1.37) automatycznie i natywnie mapuje te atrybuty.
- **Langfuse / Phoenix / Opik** (Lekcja 24) oferują automatyczną instrumentację dla wiodących frameworków.
- **Jaeger / Honeycomb / Grafana Tempo** – przyjmują surowe ślady standardu OTel, na bazie których można tworzyć zaawansowane dashboardy analityczne.
- **Własna infrastruktura** – uruchomienie OpenTelemetry Collector z procesorem filtrującym pod kątem atrybutów GenAI.

## Zadanie wdrożeniowe

Plik `outputs/skill-otel-genai.md` opisuje proces integracji standardu OpenTelemetry GenAI z istniejącym agentem, z zachowaniem zasad bezpiecznego zapisu treści w zewnętrznym magazynie.

## Ćwiczenia praktyczne

1. Oprzyrząduj pętlę ReAct z Lekcji 1 za pomocą spanów typu `invoke_agent` (INTERNAL) oraz spanów dla poszczególnych narzędzi. Prześlij zebrane dane do lokalnej instancji systemu Jaeger.
2. Zaimplementuj bezpieczne rejestrowanie treści w trybie referencyjnym: prompty zapisuj w bazie SQLite, a w atrybutach spanów telemetrycznych umieszczaj wyłącznie identyfikatory rekordów.
3. Zapoznaj się ze specyfikacją atrybutu `gen_ai.data_source.id` i zintegruj go z modułem pamięci Mem0 (Lekcja 9).
4. Skonfiguruj zmienną środowiskową `OTEL_SEMCONV_STABILITY_OPT_IN=gen_ai_latest_experimental` i zweryfikuj w kolektorze, czy nazwy atrybutów są zgodne ze specyfikacją.
5. Zaprojektuj i zbuduj panel analityczny (dashboard) korelujący błędy wywołań poszczególnych narzędzi z konkretnymi modelami LLM na podstawie wyłącznie atrybutów standardu GenAI.

## Kluczowe terminy

| Termin | Potoczne określenie | Co to dokładnie oznacza |
|------|----------------|--------------------------------------|
| GenAI SIG | „Grupa robocza GenAI” | Grupa w strukturach OpenTelemetry definiująca konwencje semantyczne dla sztucznej inteligencji |
| invoke_agent | „Span agenta” | Standardowa nazwa spanu reprezentującego wywołanie/pracę agenta |
| CLIENT span | „Połączenie zewnętrzne” | Span reprezentujący komunikację ze zdalną, zewnętrzną usługą agenta (np. API) |
| INTERNAL span | „Wywołanie lokalne” | Span reprezentujący wykonanie kodu agenta lokalnie w procesie aplikacji |
| gen_ai.provider.name | „Dostawca modelu” | Nazwa podmiotu udostępniającego model (np. anthropic, openai, aws.bedrock, google.vertex) |
| gen_ai.data_source.id | „Źródło RAG” | Który korpus/magazyn został trafiony podczas pobierania |
| Content Capture | „Bezpieczne rejestrowanie” | Konfiguracja trybu opt-in do zbierania promptów; na produkcji zalecane jest stosowanie referencji zewnętrznych |
| Stability Opt-in | „Zgoda na wersję eksperymentalną” | Zmienna środowiskowa służąca do przypięcia najnowszych konwencji semantycznych GenAI |

## Dalsze czytanie

- [Konwencje semantyczne OpenTelemetry GenAI](https://opentelemetry.io/docs/specs/semconv/gen-ai/) — specyfikacja
- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/) — domyślne rozpiętości GenAI
- [AutoGen v0.4 (Microsoft Research)](https://www.microsoft.com/en-us/research/articles/autogen-v0-4-reimagining-the-foundation-of-agentic-ai-for-scale-extensibility-and-robustness/) — wbudowane rozpiętości Otel
- [Claude Agent SDK](https://platform.claude.com/docs/en/agent-sdk/overview) — propagacja kontekstu śledzenia W3C
