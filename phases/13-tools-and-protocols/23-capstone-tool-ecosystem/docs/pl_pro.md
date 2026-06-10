# Capstone — Projekt zaliczeniowy: Budowa kompletnego ekosystemu narzędziowego

> W fazie 13 poznaliśmy poszczególne elementy układanki. Ten projekt zaliczeniowy (capstone) łączy je w jeden spójny system klasy produkcyjnej: serwer MCP (narzędzia, zasoby, prompty, zadania, interfejs ui://), autoryzację OAuth 2.1 na brzegu sieci, bramę RBAC, klienta wieloserwerowego, wywołanie subagenta za pośrednictwem A2A, monitorowanie OTel z wysyłką do kolektora, wykrywanie zatruć narzędzi w potokach CI/CD oraz pakiet konfiguracyjny AGENTS.md + SKILL.md. Na koniec dowiesz się, jak uargumentować i obronić każdą z decyzji architektonicznych.

**Typ:** Projekt (Capstone)
**Język:** Python (biblioteka standardowa, kompleksowa konfiguracja ekosystemu)
**Wymagania wstępne:** Faza 13 · 01 do 21
**Czas:** ~120 minut

## Cele lekcji

- Budowa serwera MCP udostępniającego narzędzia, zasoby, prompty i zadania wraz z interfejsem graficznym `ui://`.
- Zabezpieczenie serwera bramą sieciową OAuth 2.1 wymuszającą polityki RBAC oraz weryfikację skrótów SHA256 (hash pinning).
- Implementacja klienta wieloserwerowego realizującego kompleksowe śledzenie w standardzie OTel GenAI.
- Delegowanie zadań do subagenta za pośrednictwem A2A z zachowaniem zasady nieprzezroczystości (black-box).
- Pakowanie całej konfiguracji z użyciem plików AGENTS.md oraz SKILL.md w celu ułatwienia orkiestracji przez inne systemy agentowe.

## Problem

Wdrożenie produkcyjne systemu badawczo-analitycznego:

— Użytkownik zleca zadanie: „podsumuj trzy najczęściej cytowane artykuły naukowe w serwisie arXiv z 2026 roku dotyczące protokołów komunikacji agentowej”.
- Przebieg procesu: wyszukanie publikacji w arXiv przy użyciu narzędzia MCP, delegowanie podsumowania treści do wyspecjalizowanego subagenta za pośrednictwem protokołu A2A, skonsolidowanie wyników, wyrenderowanie interaktywnego raportu jako zasobu graficznego MCP `ui://` oraz zapisanie telemetrii na każdym etapie w systemie OTel.

W tym scenariuszu wykorzystujemy wszystkie pojęcia bazowe poznane w fazie 13. To rzeczywisty schemat architektoniczny – wiodące systemy analityczne i badawcze wdrożone w 2026 roku (takie jak Claude Research od Anthropic czy wtyczki GPT oparte na OpenAI Apps SDK) są projektowane dokładnie według tego wzorca.

## Założenia koncepcyjne

### Architektura

```
[user] -> [client] -> [gateway (OAuth 2.1 + RBAC)] -> [research MCP server]
                                                      |
                                                      +- MCP tool: arxiv_search (pure)
                                                      +- MCP resource: notes://recent
                                                      +- MCP prompt: /research_topic
                                                      +- MCP task: generate_report (long)
                                                      +- MCP Apps UI: ui://report/current
                                                      +- A2A call: writer-agent (tasks/send)
                                                      |
                                                      +- OTel GenAI spans
```

### Hierarchia śledzenia (Trace Hierarchy)

```
agent.invoke_agent
 ├── llm.chat (kick off)
 ├── mcp.call -> tools/call arxiv_search
 ├── mcp.call -> resources/read notes://recent
 ├── mcp.call -> prompts/get research_topic
 ├── a2a.tasks/send -> writer-agent
 │    └── task transitions (opaque internals)
 ├── mcp.call -> tools/call generate_report (task-augmented)
 │    └── tasks/status polling
 │    └── tasks/result (completed, returns ui:// resource)
 └── llm.chat (final synthesis)
```

Wszystkie zakresy (spans) współdzielą jeden identyfikator śledzenia. Każdy zakres posiada odpowiednie atrybuty `gen_ai.*`.

### Architektura bezpieczeństwa

- Przepływ OAuth 2.1 + PKCE ze wskaźnikami zasobów (resource indicators) wiążącymi token z bramą.
- Przechowywanie danych uwierzytelniających do nadrzędnych systemów (upstream credentials) na bramie; brak dostępu dla klientów deweloperów.
- Polityka RBAC: użytkownik `alice` posiada uprawnienia `research:read` oraz `research:write` (pełny dostęp); użytkownik `bob` posiada jedynie `research:read` i nie może wywołać zadania `generate_report`.
- Przypięty manifest skrótów (hash pinning): odfiltrowanie narzędzi, których sygnatury SHA256 uległy zmianie bez autoryzacji.
- Weryfikacja reguły dwóch (rule of two): żadne z narzędzi nie może jednocześnie przetwarzać niezaufanych danych wejściowych, operować na wrażliwych danych i wywoływać akcji o wysokim priorytecie.

### Renderowanie interfejsu graficznego

Zadanie `generate_report` po ukończeniu zwraca ustrukturyzowaną treść raportu oraz odnośnik do zasobu `ui://report/current`. Aplikacja kliencka (np. Claude Desktop) renderuje interaktywny dashboard w zabezpieczonym oknie typu sandbox (iframe). Panel prezentuje posortowaną listę publikacji, statystyki cytowań oraz przyciski wywołujące funkcję `host.callTool('summarize_paper', {arxiv_id})` po kliknięciu przez użytkownika.

### Pakowanie i dystrybucja

Kompletna struktura katalogów wdrożenia:

```
research-system/
  AGENTS.md                     # project conventions
  skills/
    run-research/
      SKILL.md                  # the top-level workflow
  servers/
    research-mcp/               # the MCP server
      pyproject.toml
      src/
  agents/
    writer/                     # the A2A agent
  gateway/
    config.yaml                 # RBAC + pinned manifest
```

Uruchomienie całego stosu odbywa się za pomocą komendy `docker compose up`. Następnie systemy agentowe (np. Claude Code, Cursor, Codex, OpenCode) mogą automatycznie wykryć i uruchomić zdefiniowany proces za pomocą umiejętności `run-research`.

### Podsumowanie wkładu poszczególnych lekcji Fazy 13

| Lekcja | Wykorzystany element w projekcie zaliczeniowym |
|------------|--------------------------------------|
| 01-05 | Interfejsy narzędzi, niezależność od dostawców, wywołania równoległe, walidacja schematów, linting |
| 06-10 | Architektura MCP, serwer, klient, protokoły transportu, zarządzanie zasobami i promptami |
| 11-14 | Próbkowanie (sampling), uprawnienia wywołań, zadania asynchroniczne, interfejs graficzny `ui://` |
| 15-17 | Zatrucia narzędzi (tool poisoning), OAuth 2.1, bramy sieciowe i rejestry usług |
| 18 | Delegowanie zadań do subagenta (A2A) |
| 19 | Śledzenie telemetryczne (OTel GenAI) |
| 20 | Brama routingu dla warstwy LLM |
| 21 | Konfiguracja i pakowanie (SKILL.md + AGENTS.md) |

## Zastosowanie w praktyce

Skrypt `code/main.py` integruje wzorce z poszczególnych lekcji w jedną, kompletną aplikację demonstracyjną. Kod bazuje wyłącznie na bibliotece standardowej Pythona, co ułatwia jego analizę krok po kroku. Uruchamia on pełny przepływ scenariusza analizy i raportowania: nawiązanie połączenia z bramą, symulację autoryzacji OAuth 2.1, konsolidację listy narzędzi, uruchomienie asynchronicznego zadania `generate_report`, delegację zadania do subagenta przez A2A, wyrenderowanie zasobu `ui://` oraz wyemitowanie danych telemetrycznych OTel.

Kluczowe elementy:

- Spójny identyfikator śledzenia (`traceId`) na każdym etapie przepływu.
- Polityka RBAC na bramie blokująca operacje zapisu dla nieuprawnionego użytkownika.
- Przebieg stanów zadania (working → completed) zwracający treść raportu i konfigurację UI.
- Zachowanie zasady nieprzezroczystości (black-box) przy wywołaniach subagenta A2A.
- Pliki `AGENTS.md` oraz `SKILL.md` jako jedyne źródło wiedzy niezbędne do replikacji procesu przez zewnętrznych agentów.

## Zadanie praktyczne

Efektem tej lekcji powinno być przygotowanie pliku `outputs/skill-ecosystem-blueprint.md`. Na podstawie wymagań funkcjonalnych systemu badawczo-analitycznego należy opracować kompletną specyfikację techniczną architektury systemu: konfigurację serwera MCP, reguły bezpieczeństwa bramy sieciowej, integracje A2A, schemat telemetrii oraz strukturę pakowania projektu.

## Ćwiczenia

1. Uruchom skrypt `code/main.py`. Przeanalizuj powiązania telemetryczne (zagnieżdżenie zakresów pod jednym identyfikatorem śledzenia). Policz, ile różnych pojęć i mechanizmów z Fazy 13 zostało zintegrowanych w tej aplikacji.

2. Rozbuduj aplikację: dodaj drugi backendowy serwer MCP (np. serwer bibliograficzny `bibliography`) i zweryfikuj, czy brama poprawnie konsoliduje narzędzia w ramach tej samej przestrzeni nazw.

3. Zastąp mock subagenta A2A rzeczywistym procesem uruchamianym w osobnym podprocesie (wykorzystaj kod opracowany w lekcji 19).

4. Zaimplementuj filtr anonimizacji danych osobowych (PII) na bramie routingu przed przekazaniem zapytania do LLM. Upewnij się, że adresy e-mail są poprawnie wycinane z promptu użytkownika.

5. Opracuj plik `AGENTS.md` dla deweloperów dołączających do projektu. Upewnij się, że dokument precyzyjnie opisuje architekturę systemu i pozwala na szybkie wdrożenie się w pracę przy użyciu środowisk Cursor lub Codex.

## Kluczowe pojęcia

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Projekt Capstone | „Integracja Fazy 13” | Kompleksowa aplikacja integrująca wszystkie poznane standardy i protokoły |
| Badanie i raport | „Scenariusz użycia” | Klasyczny przepływ: wyszukanie informacji, synteza (podsumowanie) oraz prezentacja wyników |
| Ekosystem | „Kompletny stos” | Integracja serwera, klienta, bramy sieciowej, subagentów, telemetrii i pakietu konfiguracyjnego |
| Hierarchia śladu | „Spójny Trace ID” | Struktura, w której wszystkie zakresy (spans) współdzielą jeden identyfikator śledzenia |
| Token bramy | „Autoryzacja przechodnia” | Klient uwierzytelnia się na bramie, która bezpiecznie zarządza kluczami do systemów nadrzędnych |
| Skonsolidowana przestrzeń | „Płaska lista narzędzi” | Połączenie interfejsów wielu serwerów na poziomie bramy sieciowej |
| Granica nieprzezroczystości | „Izolacja subagenta” | Ukrywanie szczegółów wykonania i wnioskowania subagenta A2A przed systemem zlecającym |
| Trzywarstwowy stos | „AGENTS + SKILL + MCP” | Konfiguracja projektu (AGENTS.md), procesy (SKILL.md) oraz narzędzia (MCP) |
| Defense in Depth | „Wielowarstwowa ochrona” | Łączenie mechanizmów hash pinning, OAuth, RBAC, rule of two i logów audytowych |
| Macierz zgodności | „Weryfikacja ze specyfikacją” | Tabela mapująca wdrożone funkcjonalności na wymogi normatywne standardu |

## Polecana literatura / dokumentacja

- [MCP — Specyfikacja 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25) — skonsolidowane odniesienie
- [Blog MCP — plan działania na rok 2026](https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/) — dokąd zmierza protokół
- [a2a-protocol.org](https://a2a-protocol.org/latest/) — odniesienie do A2A v1.0
- [OpenTelemetry — GenAI semconv](https://opentelemetry.io/docs/specs/semconv/gen-ai/) — konwencje śledzenia kanonicznego
- [Anthropic — przegląd pakietu SDK Agenta Claude'a](https://code.claude.com/docs/en/agent-sdk/overview) — wzorce środowiska wykonawczego agenta produkcyjnego
