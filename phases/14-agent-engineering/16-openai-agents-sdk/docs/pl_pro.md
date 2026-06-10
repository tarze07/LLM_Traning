# OpenAI Agents SDK: Przekazywanie zadań, barierki ochronne i śledzenie

> OpenAI Agents SDK to lekki framework wieloagentowy zbudowany bezpośrednio na bazie API Chat Completions. Składa się z pięciu podstawowych elementów: agent (Agent), przekazanie zadania (Handoff), barierka ochronna (Guardrail), sesja (Session) oraz śledzenie (Tracing). Przekazywanie zadań realizowane jest jako narzędzia o nazwie `transfer_to_<agent_name>`. Barierki ochronne (Guardrails) walidują dane wejściowe i wyjściowe. Śledzenie (Tracing) jest domyślnie aktywne.

**Typ:** Ucz się + Buduj
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 14 · 01 (Pętla agenta), Faza 14 · 06 (Użycie narzędzi)
**Czas:** ~75 minut

## Cele nauczania

- Wymień pięć podstawowych komponentów OpenAI Agents SDK.
- Wyjaśnij mechanizm przekazywania zadań (handoffs): dlaczego są one modelowane jako wywołania narzędzi, pod jaką nazwą model widzi tę funkcję i w jaki sposób przekazywany jest kontekst.
- Rozróżnij barierki ochronne (guardrails) wejściowe, wyjściowe oraz barierki nałożone na narzędzia; wyjaśnij różnicę pomiędzy trybem równoległym (`run_in_parallel`) a blokującym.
- Zaimplementuj w Pythonie (stdlib) uproszczone środowisko uruchomieniowe z obsługą przekazywania zadań, barierek ochronnych oraz śledzenia (tracingu).

## Problem

Agenci, którzy nie posiadają mechanizmu czystego delegowania zadań, zmuszają programistów do umieszczania wszystkich instrukcji w jednym olbrzymim prompcie. Brak wdrożonych zabezpieczeń (guardrails) prowadzi do wycieków danych osobowych (PII), generowania treści niezgodnych z polityką bezpieczeństwa lub wpadania agentów w nieskończone pętle. OpenAI Agents SDK standaryzuje te elementy, ułatwiając tworzenie stabilnych systemów wieloagentowych.

## Koncepcja

### Pięć podstawowych elementów

1. **Agent.** Model LLM + instrukcje systemowe + narzędzia + przekazywanie zadań.
2. **Przekazanie (Handoff).** Delegowanie zadania innemu agentowi. W modelu jest to reprezentowane jako narzędzie o nazwie `transfer_to_<agent_name>`.
3. **Barierka ochronna (Guardrail).** Walidacja danych wejściowych (wywoływana na pierwszym agencie), danych wyjściowych (wywoływana na ostatnim agencie) lub walidacja wywołania konkretnego narzędzia.
4. **Sesja (Session).** Automatyczne zarządzanie historią konwersacji pomiędzy kolejnymi turami.
5. **Śledzenie (Tracing).** Wbudowane mechanizmy generowania spanów (rozpiętości) dla zapytań LLM, wywołań narzędzi, przekazywania zadań oraz walidacji guardrails.

### Przekazywanie zadań jako wywołanie narzędzi (Handoffs)

Model LLM widzi funkcję `transfer_to_billing_agent` na swojej liście dostępnych narzędzi. Jej wywołanie sygnalizuje środowisku uruchomieniowemu konieczność podjęcia następujących akcji:

1. Skopiowania dotychczasowej historii rozmowy (lub jej skrócenia/streszczenia za pomocą opcji `nest_handoff_history`).
2. Zainicjalizowania agenta docelowego z jego instrukcjami systemowymi.
3. Kontynuowania pętli decyzyjnej z nowym agentem.

Jest to bezpośrednia realizacja wzorca nadzorcy i przekazywania zadań (Lekcja 13 / Lekcja 28).

### Barierki ochronne (Guardrails)

Trzy rodzaje barierek:

- **Barierki wejściowe (Input Guardrails).** Uruchamiane na danych wejściowych pierwszego agenta. Pozwalają odrzucić niebezpieczne lub nieistotne zapytania jeszcze przed wysłaniem zapytania do modelu głównego.
- **Barierki wyjściowe (Output Guardrails).** Działają na wynikach wygenerowanych przez ostatniego agenta. Przechwytują potencjalne wycieki danych wrażliwych (PII), naruszenia zasad bezpieczeństwa lub niepoprawnie sformatowane odpowiedzi.
- **Barierki narzędziowe (Tool Guardrails).** Uruchamiane przed wykonaniem konkretnego narzędzia. Walidują parametry wejściowe, weryfikują uprawnienia i logują operację.

Warianty wykonania:

- **Równoległy** (`run_in_parallel=True` - domyślnie). Weryfikacja guardrail jest uruchamiana współbieżnie z zapytaniem do modelu głównego. Zapewnia to niższe opóźnienia, jednak w przypadku wykrycia naruszenia wynik modelu głównego jest odrzucany (co generuje stratę tokenów).
- **Blokujący** (`run_in_parallel=False`). Weryfikacja guardrail wykonuje się przed zapytaniem do modelu głównego. Zapebiega to marnowaniu tokenów na model główny w przypadku wykrycia błędnego zapytania.

Naruszenie zasad bezpieczeństwa zgłasza wyjątki `InputGuardrailTripwireTriggered` lub `OutputGuardrailTripwireTriggered`.

### Śledzenie (Tracing)

Funkcja ta jest domyślnie włączona. Każde zapytanie do modelu, wywołanie narzędzia, przekazanie zadania oraz przejście przez barierki generuje span telemetryczny. Zdefiniowanie zmiennej środowiskowej `OPENAI_AGENTS_DISABLE_TRACING=1` wyłącza ten mechanizm. Metoda `add_trace_processor(processor)` pozwala na podpięcie własnych procesorów eksportujących logi.

### Sesje (Sessions)

Obiekt `Session` przechowuje historię konwersacji w bazie danych (SQLite, Redis lub własnym rozwiązaniu). Metoda `Runner.run(agent, input, session=session)` automatycznie wczytuje i aktualizuje stan sesji.

### Potencjalne problemy i wady wzorca

- **Nieskończone pętle przekazywania (handoff loops).** Agent A deleguje zadanie agentowi B, który przekazuje je z powrotem do agenta A. Rozwiązaniem jest dodanie licznika przekazań (max hop limit).
- **Ominięcie zabezpieczeń.** Barierki narzędziowe weryfikują wyłącznie niestandardowe narzędzia funkcyjne; wbudowane narzędzia (np. odczyt plików, wyszukiwanie w sieci) wymagają konfiguracji odrębnych polityk.
- **Nadmiarowość danych w telemetrii.** Zapisywanie poufnych danych bezpośrednio w spanach OTel. Należy filtrować te wartości zgodnie ze standardami OTel GenAI (Lekcja 23) lub zastępować je identyfikatorami referencyjnymi.

## Zbuduj to

Plik `code/main.py` implementuje uproszczony szkielet SDK przy użyciu biblioteki standardowej Pythona:

- Klasy `Agent`, `FunctionTool` oraz `Handoff` (jako wyspecjalizowane narzędzie z semantyką przekazania).
- Klasę `Runner` z obsługą barierek wejściowych, wyjściowych i narzędziowych, obsługą przekazywania zadań oraz licznikiem kroków.
- Prosty emiter logów pokazujący generowane spany telemetryczne.
- Agenta rozdzielającego (routera), który deleguje zadania do wsparcia technicznego lub rozliczeń na podstawie zapytania, z demonstracją wyzwolenia barierki ochronnej przy błędnym zapytaniu.

Uruchomienie:

```
python3 code/main.py
```

Logi (trace) pokazują dwa pomyślne przekazania zadań, jedno wyzwolenie barierki wejściowej oraz strukturę spanów odpowiadającą zachowaniu rzeczywistego SDK.

## Użyj tego

- **OpenAI Agents SDK** — w projektach opartych wyłącznie o modele OpenAI.
- **Claude Agent SDK** (Lekcja 17) — w projektach zorientowanych na modele Anthropic.
- **LangGraph** (Lekcja 13) — gdy wymagana jest pełna kontrola nad stanem i deterministyczne wznawianie działania.
- **Własne rozwiązanie** — w przypadku specyficznych wymagań (np. integracja z wieloma dostawcami, dedykowane systemy audio/video).

## Wyślij to

Plik `outputs/skill-agents-sdk-scaffold.md` tworzy szkielet aplikacji w oparciu o Agents SDK z agentem kierującym, mechanizmami przekazywania, barierki ochronne (wejścia/wyjścia/narzędzi), obsługą sesji oraz procesorem logów telemetrycznych.

## Ćwiczenia

1. Dodaj licznik przekazań (hops): przerwij proces po N transferach i przeanalizuj zachowanie systemu.
2. Zaimplementuj opcję `nest_handoff_history`: streść poprzednie wiadomości i usuń szczegóły przed przekazaniem zadania nowemu agentowi.
3. Zaimplementuj blokującą barierkę wyjściową. Porównaj czas odpowiedzi dla komunikatów, które wyzwalają to zabezpieczenie, z komunikatami przechodzącymi pomyślnie.
4. Podłącz własny procesor przez `add_trace_processor` eksportujący dane do logu JSON. Przeanalizuj strukturę generowanego spana.
5. Zapoznaj się z oficjalną dokumentacją. Przepisz wersję z stdlib z użyciem rzeczywistego pakietu `openai-agents-python`. Przeanalizuj różnice w strukturze i modelowaniu obiektów.

## Kluczowe terminy

| Termin | Co mówią ludzie | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Agent | „LLM + instrukcje” | Podstawowy typ agenta w SDK; posiada narzędzia i obsługuje przekazywanie zadań |
| Przekazanie (Handoff) | „Przeniesienie” | Narzędzie służące do delegowania przetwarzania do innego agenta |
| Barierka ochronna (Guardrail) | „Sprawdzanie zasad” | Walidacja danych wejściowych, wyjściowych lub wywołań narzędzi |
| Wyzwalacz zabezpieczenia (Tripwire) | „Wyzwanie poręczą” | Wyjątek zgłaszany w przypadku zablokowania przepływu przez guardrail |
| Sesja (Session) | „Magazyn historii” | Pamięć historii konwersacji utrzymywana pomiędzy uruchomieniami |
| Śledzenie (Tracing) | „Spany telemetryczne” | Wbudowane generowanie logów dla wywołań LLM, narzędzi, przekazań i guardrails |
| Barierka blokująca | „Kontrola sekwencyjna” | Walidacja guardrail wykonuje się przed zapytaniem do modelu głównego, zapobiegając stracie tokenów |
| Barierka równoległa | „Kontrola współbieżna” | Walidacja guardrail wykonuje się współbieżnie z zapytaniem głównym, redukując opóźnienia kosztem tokenów |

## Dalsze czytanie

- [Dokumentacja OpenAI Agents SDK](https://openai.github.io/openai-agents-python/) — opis elementów podstawowych, handoffs, guardrails oraz tracingu
- [Dokumentacja Claude Agent SDK](https://platform.claude.com/docs/en/agent-sdk/overview) — oficjalny framework od Anthropic
- [Anthropic, Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) — wytyczne dotyczące stosowania mechanizmów przekazywania zadań
- [Specyfikacja semantyczna OpenTelemetry GenAI](https://opentelemetry.io/docs/specs/semconv/gen-ai/) — standard logowania i telemetrii w systemach AI
