# Claude Agent SDK: Podagenci i sklep sesyjny

> Zestaw SDK Claude Agent jest formą biblioteczną uprzęży Claude Code. Wbudowane narzędzia, subagenci do izolacji kontekstu, hooki, propagacja śladów W3C, parzystość magazynu sesji. Claude Managed Agents to hostowana alternatywa dla długotrwałej pracy asynchronicznej.

**Typ:** Ucz się + Buduj
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 14 · 01 (Pętla agenta), Faza 14 · 10 (Biblioteki umiejętności)
**Czas:** ~75 minut

## Cele nauczania

- Wyjaśnij różnicę między pakietem Anthropic Client SDK (surowe API) a pakietem SDK Claude Agent (kształt wiązki przewodów).
- Opisz podagentów — równoległość i izolację kontekstu — oraz kiedy po nich sięgnąć.
- Nazwij powierzchnię magazynu sesji pakietu Python SDK (`append`, `load`, `list_sessions`, `delete`, `list_subkeys`) i rolę `--session-mirror`.
- Zaimplementuj wiązkę stdlib z wbudowanymi narzędziami, odradzaniem podagentów z izolowanym kontekstem, hakami cyklu życia i magazynem sesji.

## Problem

Surowy interfejs API LLM zapewnia jedną podróż w obie strony. Agent produkcyjny potrzebuje wykonania narzędzia, serwerów MCP, haków cyklu życia, tworzenia podagentów, trwałości sesji i propagacji śladów. Claude Agent SDK dostarcza ten kształt jako bibliotekę — tę samą uprząż, której używa Claude Code, dostępną dla niestandardowych agentów.

## Koncepcja

### SDK klienta a SDK agenta

- **Klient SDK (`anthropic`).** Interfejs API nieprzetworzonych wiadomości. Jesteś właścicielem pętli, narzędzi i stanu.
- **Agent SDK (`claude-agent-sdk`).** Wbudowane wykonywanie narzędzi, połączenia MCP, zaczepy, odradzanie podagentów, magazyn sesji. Pętla Claude Code jako biblioteka.

### Built-in tools

Pakiet SDK zawiera ponad 10 narzędzi: odczyt/zapis plików, powłoka, grep, glob, pobieranie z Internetu i inne. Niestandardowe narzędzia rejestrują się za pośrednictwem standardowego interfejsu schematu narzędzi.

### Subagents

Dwa cele udokumentowane przez Anthropic:

1. **Równoległość.** Równoległa praca niezależna. „Znajdź plik testowy dla każdego z tych 20 modułów” to 20 równoległych zadań podagenta.
2. **Izolacja kontekstu.** Podagenci korzystają z własnego okna kontekstowego; tylko wyniki wracają do orkiestratora. Budżet orkiestratora zostaje zachowany.

Najnowsze dodatki do pakietu Python SDK: `list_subagents()`, `get_subagent_messages()` do odczytywania transkrypcji subagentów.

### Sklep sesyjny

Parzystość protokołu z TypeScript:

- `append(session_id, message)` — dodaj zakręt.
- `load(session_id)` — przywróć rozmowę.
- `list_sessions()` — wylicz.
- `delete(session_id)` — z sesjami kaskadowymi do subagentów.
- `list_subkeys(session_id)` — wyświetla klucze podagentów.

`--session-mirror` (flaga CLI) odzwierciedla transkrypcję do pliku zewnętrznego podczas przesyłania strumieniowego w celu debugowania.

### Haczyki

Haki cyklu życia, które możesz zarejestrować:

- `PreToolUse`, `PostToolUse` — wywołania bramki lub narzędzia audytu.
- `SessionStart`, `SessionEnd` — konfiguruj i demontuj.
- `UserPromptSubmit` — działaj na podstawie danych wprowadzonych przez użytkownika, zanim model je zobaczy.
- `PreCompact` — uruchom przed zagęszczeniem kontekstu.
- `Stop` — czyszczenie przy wyjściu agenta.
- `Notification` — alerty z kanału bocznego.

Haki to sposób, w jaki pro-workflow (odniesienie do programu nauczania fazy 14) i podobne systemy dodają przekrojowe zachowanie.

### W3C trace context

Rozpiętości OTel aktywne w programie wywołującym są propagowane do podprocesu CLI za pośrednictwem nagłówków kontekstu śledzenia W3C. Cały ślad wieloprocesowy pojawia się jako jeden ślad w backendzie.

### Claude zarządzał agentami

Hostowana alternatywa (nagłówek wersji beta `managed-agents-2026-04-01`). Długotrwała praca asynchroniczna, wbudowane buforowanie natychmiastowe, wbudowane zagęszczanie. Kontrola handlu dla zarządzanej infrastruktury.

### Gdzie ten wzorzec jest błędny

- **Nadmierne pojawianie się subagentów.** Tworzenie 100 subagentów dla 100 małych zadań. Dominuje narzut. Batch instead.
- **Powstanie haka.** Każda drużyna dodaje haki; startup time balloons. Review hooks quarterly.
- **Rozdęcie sesji.** Sesje kumulują się; size grows. Użyj `list_sessions` + zasady wygaśnięcia.

## Zbuduj to

`code/main.py` implementuje kształt SDK w stdlib:

- `Tool`, `ToolRegistry` z wbudowanym `read_file`, `write_file`, `list_dir`.
- `Subagent` — kontekst prywatny, uruchomienie izolowane, zwrócone wyniki.
- `SessionStore` — dodawaj, ładuj, wyświetlaj, usuwaj, list_subkeys.
- `Hooks` — `pre_tool_use`, `post_tool_use`, `session_start`, `session_end`.
- Demo: główny agent tworzy równolegle 3 podagentów (każdy izolowany), agreguje wyniki, utrzymuje sesję.

Uruchom to:

```
python3 code/main.py
```

Śledzenie pokazuje izolację kontekstu podagenta (rozmiar kontekstu programu Orchestrator pozostaje ograniczony), wykonanie przechwytywania i trwałość sesji.

## Użyj tego

- **Claude Agent SDK** dla produktów Claude-first, które wymagają kształtu uprzęży Claude Code.
- **Agenty zarządzane przez Claude** do hostowanej, długotrwałej pracy asynchronicznej.
- **OpenAI Agents SDK** (Lekcja 16) dla odpowiedników obsługujących OpenAI.
- **LangGraph + narzędzia niestandardowe**, jeśli zamiast tego chcesz używać maszyny stanu w kształcie wykresu.

## Wyślij to

`outputs/skill-claude-agent-scaffold.md` tworzy szkielet aplikacji Claude Agent SDK z podagentami, hakami, magazynem sesji, przyłączeniem serwera MCP i propagacją śledzenia W3C.

## Ćwiczenia

1. Dodaj generator podagentów, który dzieli 20 zadań w grupy po 5 równoległych podagentów. Zmierz rozmiar kontekstu programu Orchestrator w porównaniu z rozmiarem jednego zadania.
2. Zaimplementuj hak `PreToolUse`, który ogranicza szybkość połączeń `write_file` (5 na minutę na sesję). Śledź zachowanie.
3. Połącz `list_subkeys`, aby wyrenderować drzewo podagentów. Jak wygląda głębokie zagnieżdżanie?
4. Przenieś zabawkę do prawdziwego `claude-agent-sdk` pakietu Pythona. Jakie zmiany dotyczą rejestracji narzędzi?
5. Przeczytaj dokumentację dotyczącą agentów zarządzanych Claude. Kiedy chcesz przejść z samodzielnego hostingu na zarządzany?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Pakiet SDK agenta | „Claude Code jako biblioteka” | Kształt uprzęży: narzędzia, MCP, haczyki, subagenci, sklep sesyjny |
| Subagent | „Agent dziecięcy” | Odrębny kontekst, własny budżet; wyniki rosną |
| Sklep sesyjny | „DB konwersacji” | Utrzymuj, ładuj, listuj, usuwaj tury z kaskadą podagentów |
| Hak | „Wywołanie zwrotne cyklu życia” | Narzędzie poprzedzające/publikujące, sesja, monit o przesłanie, kompaktowanie, zatrzymanie |
| Kontekst śledzenia W3C | „Śledzenie międzyprocesowe” | Rozpiętość nadrzędna propaguje się do podprocesu CLI |
| Zarządzani agenci | „Uprząż hostowana” | Długotrwała praca asynchroniczna hostowana przez Antropię |
| `--session-mirror` | „Lustro transkrypcji” | Zapisuje sesje w pliku zewnętrznym podczas przesyłania strumieniowego |
| Serwer MCP | „Powierzchnia narzędzia” | Zewnętrzne narzędzie/źródło zasobów dołączone do agenta |

## Dalsze czytanie

- [Omówienie zestawu SDK Claude Agent](https://platform.claude.com/docs/en/agent-sdk/overview) — forma biblioteki Claude Code
- [Anthropic, Agenci budowlani z pakietem SDK Claude Agent](https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk) — wzorce produkcji
- [Przegląd agentów zarządzanych Claude](https://platform.claude.com/docs/en/managed-agents/overview) — alternatywa hostowana
- [SDK dla agentów OpenAI](https://openai.github.io/openai-agents-python/) — odpowiednik