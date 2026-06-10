# Capstone — Zbuduj kompletny ekosystem narzędzi

> W fazie 13 nauczono się każdego utworu. To zwieńczenie łączy je w jeden system o charakterze produkcyjnym: serwer MCP z narzędziami + zasobami + podpowiedziami + zadaniami + interfejs użytkownika, OAuth 2.1 na brzegu, brama RBAC, klient wieloserwerowy, wywołanie subagenta A2A, śledzenie Otel do modułu zbierającego, wykrywanie zatrucia narzędzi w CI oraz pakiet AGENTS.md + SKILL.md. Do końca można obronić każdy wybór architektoniczny.

**Typ:** Kompilacja
**Języki:** Python (stdlib, kompleksowa konfiguracja ekosystemu)
**Wymagania wstępne:** Faza 13 · 01 do 21
**Czas:** ~120 minut

## Cele nauczania

- Utwórz serwer MCP udostępniający narzędzia, zasoby, podpowiedzi i zadania za pomocą aplikacji `ui://`.
— Przed serwerem znajduje się brama OAuth 2.1, która wymusza RBAC i przypięte skróty.
- Napisz klienta wieloserwerowego, który kompleksowo śledzi atrybuty Otel GenAI.
- Deleguj część zadań subagentowi A2A; sprawdź, czy nieprzezroczystość jest zachowana.
- Spakuj cały stos za pomocą AGENTS.md + SKILL.md, aby inni agenci mogli nim sterować.

## Problem

Wysyłka systemu „badania i raportowanie”:

— Użytkownik pyta: „podsumuj trzy najczęściej cytowane artykuły arXiv z 2026 r. na temat protokołów agentów”.
- System: wyszukaj arXiv poprzez MCP; deleguj podsumowanie artykułu wyspecjalizowanemu agentowi piszącemu za pośrednictwem A2A; wyniki zbiorcze; renderuj interaktywny raport jako zasób aplikacji MCP `ui://`; rejestruj każdy krok w Otel.

Pojawiają się wszyscy prymitywni z fazy 13. To nie jest zabawka — systemy wspomagające badania produkcyjne dostarczone w 2026 r. przez firmę Anthropic (produkt Claude Research), OpenAI (GPT z pakietem SDK aplikacji) i strony trzecie mają dokładnie taki kształt.

## Koncepcja

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

### Hierarchia śledzenia

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

Jeden identyfikator śledzenia. Każdy zakres ma odpowiednie atrybuty `gen_ai.*`.

### Postawa bezpieczeństwa

- OAuth 2.1 + PKCE ze wskaźnikiem zasobów przypinającym odbiorców do bramy.
- Brama przechowuje dane uwierzytelniające upstream; użytkownik nigdy ich nie widzi.
- RBAC: `alice` ma `research:read`, `research:write`, może wywoływać wszystkie narzędzia. `bob` ma `research:read`, nie może wywołać `generate_report`.
- Przypięty manifest opisu: usunięto każdy serwer, którego skróty narzędzi uległy zmianie.
- Audyt Zasada Dwóch: żadne narzędzie nie łączy niezaufanych danych wejściowych, wrażliwych danych i wynikających z nich działań.

### Renderowanie

Ostatnie zadanie `generate_report` zwraca bloki treści oraz zasób `ui://report/current`. Host klienta (Claude Desktop itp.) renderuje interaktywny pulpit nawigacyjny w ramce iframe piaskownicy. Panel zawiera posortowaną listę artykułów, liczbę cytowań i przycisk wywołujący `host.callTool('summarize_paper', {arxiv_id})` dla dowolnego artykułu klikniętego przez użytkownika.

### Opakowanie

Całość jest wysyłana jako:

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

Użytkownicy wdrażają z `docker compose up`. Użytkownicy Claude Code, Cursor, Codex i opencode mogą sterować systemem, wywołując umiejętność `run-research`.

### Co wniosła każda lekcja fazy 13

| Lekcja | Z czego korzysta zwieńczenie |
|------------|--------------------------------------|
| 01-05 | Interfejs narzędzia, przenośność dostawcy, wywołania równoległe, schematy, linting |
| 06-10 | Elementy podstawowe MCP, serwer, klient, transporty, zasoby + podpowiedzi |
| 11-14 | Próbkowanie, pierwiastki + wywoływanie, zadania asynchroniczne, aplikacje `ui://` |
| 15-17 | Zatrucie narzędzia, OAuth 2.1, brama + rejestr |
| 18 | Delegowanie podagenta A2A |
| 19 | Śledzenie Otel GenAI |
| 20 | Brama routingu dla warstwy LLM |
| 21 | SKILL.md + AGENTS.md opakowanie |

## Użyj tego

`code/main.py` łączy wzorce z poprzednich lekcji w jedno możliwe do uruchomienia demo. Wszystko stdlib, wszystko w toku, więc możesz przeczytać od końca do końca. Uruchamia pełny przebieg scenariusza badania i raportowania: uzgadnianie z bramą, symulacja OAuth 2.1, scalanie narzędzi/list, generowanie_raportu jako zadania, wywołanie A2A do autora, zwrócony zasób ui://, wyemitowane zakresy Otel.

Na co zwrócić uwagę:

- Jeden identyfikator śledzenia na każdym przeskoku.
- Polityka bramy blokuje zapis drugiego użytkownika.
- Cykl życia zadania zaczyna działać → zostaje ukończony i zwraca zarówno tekst, jak i zawartość interfejsu użytkownika.
— Stan wewnętrzny wywołania A2A jest niejasny dla orkiestratora.
- AGENTS.md i SKILL.md to jedyne pliki potrzebne innemu agentowi do odtworzenia przepływu pracy.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-ecosystem-blueprint.md`. Biorąc pod uwagę zapotrzebowanie na produkt (badania, podsumowania, automatyzacja), umiejętność tworzy pełną architekturę: które prymitywy MCP, która brama steruje, jakie wywołania A2A, jaka telemetria, jakie pakowanie.

## Ćwiczenia

1. Uruchom `code/main.py`. Zanotuj identyfikator pojedynczego śledzenia i sposób zagnieżdżania zakresów. Policz, ilu prymitywów z fazy 13 dotyka demo.

2. Rozszerz wersję demonstracyjną: dodaj drugi serwer MCP zaplecza (np. `bibliography`) i potwierdź, że brama łączy swoje narzędzia w tej samej przestrzeni nazw.

3. Wymień fałszywego agenta piszącego A2A na prawdziwego, działającego w podprocesie. Użyj uprzęży z lekcji 19.

4. Dodaj krok redagowania danych osobowych w bramie routingu między koordynatorem a LLM. Potwierdź, że wiadomości e-mail w zapytaniu użytkownika zostały usunięte.

5. Napisz plik AGENTS.md dla członka zespołu, który będzie obsługiwał ten system. Przeczytanie i przekazanie im wszystkiego, czego potrzebują, aby osiągnąć zwieńczenie w Kursorze lub Kodeksie, powinno zająć mniej niż pięć minut.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Zwieńczenie | „Demonstracja integracji fazy 13” | Kompleksowy system wykorzystujący każdy prymityw |
| Badania i raport | „Scenariusz” | Wyszukaj, podsumuj, renderuj wzór |
| Ekosystem | „Wszystkie elementy razem” | Serwer + klient + bramka + subagent + telemetria + pakiet |
| Hierarchia śledzenia | „Pojedynczy identyfikator śledzenia” | Rozpiętość każdego przeskoku ma ten sam ślad; rodzic-dziecko poprzez identyfikatory zakresu |
| Token wydany przez bramę | „Autoryzacja przechodnia” | Klient widzi tylko token bramy; brama przechowuje uprawnienia upstream |
| Połączona przestrzeń nazw | „Wszystkie narzędzia na jednej płaskiej liście” | Połączenie wielu serwerów przy bramie, kolizja prefiksu |
| Granica nieprzezroczystości | „Połączenie A2A ukrywa elementy wewnętrzne” | Rozumowanie subagenta niewidoczne dla orkiestratora |
| Stos trójwarstwowy | „AGENTÓW.md + SKILL.md + MCP” | Kontekst projektu + przepływ pracy + narzędzia |
| Obrona dogłębna | „Wiele warstw zabezpieczeń” | Przypięte skróty, OAuth, RBAC, Zasada dwóch, dziennik audytu |
| Macierz zgodności specyfikacji | „Co wysyłamy, czego wymaga specyfikacja” | Lista kontrolna mapująca elementy dostarczane do wymagań 2025-11-25 |

## Dalsze czytanie

- [MCP — Specyfikacja 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25) — skonsolidowane odniesienie
- [Blog MCP — plan działania na rok 2026](https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/) — dokąd zmierza protokół
- [a2a-protocol.org](https://a2a-protocol.org/latest/) — odniesienie do A2A v1.0
- [OpenTelemetry — GenAI semconv](https://opentelemetry.io/docs/specs/semconv/gen-ai/) — konwencje śledzenia kanonicznego
- [Anthropic — przegląd pakietu SDK Agenta Claude'a](https://code.claude.com/docs/en/agent-sdk/overview) — wzorce środowiska wykonawczego agenta produkcyjnego