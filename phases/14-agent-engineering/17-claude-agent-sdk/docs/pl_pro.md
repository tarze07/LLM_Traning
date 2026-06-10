# Claude Agent SDK: Podagenci i sklep sesyjny

> Zestaw Claude Agent SDK to wersja biblioteczna środowiska uruchomieniowego Claude Code. Oferuje wbudowane narzędzia, podagentów do izolacji kontekstu, hooki (haki cyklu życia), propagację śladów W3C oraz spójny interfejs magazynu sesji. Claude Managed Agents to hostowana alternatywa przeznaczona do długotrwałych zadań asynchronicznych.

**Typ:** Ucz się + Buduj
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 14 · 01 (Pętla agenta), Faza 14 · 10 (Biblioteki umiejętności)
**Czas:** ~75 minut

## Cele nauczania

- Wyjaśnić różnicę między pakietem Anthropic Client SDK (surowym API) a Claude Agent SDK (kompletnym środowiskiem uruchomieniowym).
- Opisać rolę podagentów (subagents) – ich równoległość oraz izolację kontekstu – i wskazać, kiedy należy z nich korzystać.
- Omówić interfejs magazynu sesji w Python SDK (`append`, `load`, `list_sessions`, `delete`, `list_subkeys`) oraz rolę flagi `--session-mirror`.
- Zaimplementować uproszczone środowisko uruchomieniowe (oparte na bibliotece standardowej) z wbudowanymi narzędziami, uruchamianiem podagentów z izolowanym kontekstem, hakami (hooks) cyklu życia oraz magazynem sesji.

## Problem

Surowe API LLM obsługuje jedynie pojedyncze cykle żądanie-odpowiedź. Produkcyjny agent wymaga jednak uruchamiania narzędzi, integracji z serwerami MCP, haków cyklu życia, tworzenia podagentów, trwałego przechowywania sesji oraz propagacji śladów (tracingu). Claude Agent SDK dostarcza te funkcjonalności w postaci biblioteki – to samo środowisko, z którego korzysta narzędzie Claude Code, jest teraz dostępne dla własnych agentów.

## Koncepcja

### SDK klienta a SDK agenta

- **Client SDK (`anthropic`).** Surowe API do wymiany wiadomości. Programista sam zarządza pętlą agenta, narzędziami oraz stanem.
- **Agent SDK (`claude-agent-sdk`).** Wbudowane wykonywanie narzędzi, integracja z MCP, haki cyklu życia, uruchamianie podagentów oraz magazyn sesji. Pętla wykonawcza Claude Code dostępna jako biblioteka.

### Wbudowane narzędzia (Built-in tools)

Pakiet SDK zawiera ponad 10 wbudowanych narzędzi: odczyt i zapis plików, dostęp do powłoki systemowej, wyszukiwanie (grep, glob), pobieranie zawartości stron internetowych i inne. Własne narzędzia można rejestrować za pomocą standardowego schematu definicji narzędzi.

### Podagenci (Subagents)

Dwa główne cele dokumentowane przez Anthropic to:

1. **Równoległość.** Równoległe wykonywanie niezależnych zadań. Na przykład zadanie „znajdź plik testowy dla każdego z tych 20 modułów” można rozbić na 20 równolegle działających podagentów.
2. **Izolacja kontekstu.** Podagenci operują we własnym oknie kontekstowym, a do orkiestratora trafiają wyłącznie końcowe wyniki. Dzięki temu oszczędzany jest limit kontekstu głównego agenta.

Najnowsze wersje Python SDK dodają metody `list_subagents()` oraz `get_subagent_messages()` służące do odczytywania historii konwersacji podagentów.

### Magazyn sesji

Zgodność protokołu z wersją TypeScript obejmuje:

- `append(session_id, message)` – dodanie nowej tury rozmowy.
- `load(session_id)` – wczytanie historii rozmowy.
- `list_sessions()` – wylistowanie sesji.
- `delete(session_id)` – usunięcie sesji (wraz z kaskadowym usuwaniem sesji podagentów).
- `list_subkeys(session_id)` – pobranie kluczy powiązanych z podagentami.

Flaga CLI `--session-mirror` pozwala na bieżąco zapisywać (odzwierciedlać) przebieg rozmowy do zewnętrznego pliku podczas transmisji strumieniowej, co ułatwia debugowanie.

### Haki (Hooks)

Haki cyklu życia, które można zarejestrować:

- `PreToolUse`, `PostToolUse` – weryfikacja przed użyciem narzędzia lub audyt po jego wykonaniu.
- `SessionStart`, `SessionEnd` – inicjalizacja i zwalnianie zasobów sesji.
- `UserPromptSubmit` – modyfikacja lub weryfikacja zapytania użytkownika przed przekazaniem go do modelu.
- `PreCompact` – akcja wywoływana przed kompresją/skracaniem kontekstu.
- `Stop` – sprzątanie zasobów podczas zamykania agenta.
- `Notification` – powiadomienia przesyłane kanałem pomocniczym (side-channel).

Haki stanowią podstawowy mechanizm w zaawansowanych przepływach pracy (pro-workflows), umożliwiając łatwe wdrażanie funkcji przekrojowych (cross-cutting concerns).

### Kontekst śledzenia W3C (W3C trace context)

Aktywne spany OpenTelemetry (OTel) z procesu wywołującego są automatycznie propagowane do podprocesu CLI za pomocą nagłówków standardu W3C trace context. Dzięki temu cała wieloprocesowa transakcja jest widoczna jako jeden spójny ślad w systemie monitorowania.

### Agenci zarządzani przez Anthropic (Claude Managed Agents)

To hostowana alternatywa (wymagany nagłówek wersji beta `managed-agents-2026-04-01`). Zapewnia obsługę długotrwałych zadań asynchronicznych, wbudowane buforowanie promptów (prompt caching) oraz automatyczne skracanie kontekstu. Stanowi gotową, zarządzaną infrastrukturę zamiast samodzielnego utrzymywania serwerów.

### Kiedy ten wzorzec się nie sprawdza (częste błędy)

- **Nadmierne mnożenie podagentów.** Uruchamianie 100 podagentów do wykonania 100 drobnych zadań generuje ogromny narzut wydajnościowy. Lepszym rozwiązaniem jest przetwarzanie wsadowe (batching).
- **Przeładowanie hakami (Hook bloat).** Dodawanie zbyt wielu haków przez różne zespoły drastycznie wydłuża czas startu agenta. Haki należy regularnie przeglądać i optymalizować.
- **Rozrost bazy sesji (Session bloat).** Nieustannie rosnący rozmiar zapisanych sesji. Należy stosować `list_sessions` w połączeniu z polityką automatycznego wygaszania danych.

## Implementacja krok po kroku

Plik `code/main.py` implementuje uproszczony model SDK przy użyciu biblioteki standardowej Pythona:

- klasy `Tool` i `ToolRegistry` z wbudowaną obsługą operacji `read_file`, `write_file` oraz `list_dir`.
- klasę `Subagent` oferującą prywatny kontekst, izolowane uruchamianie i przekazywanie wyników z powrotem.
- `SessionStore` umożliwiający dodawanie, wczytywanie, listowanie, usuwanie sesji oraz pobieranie kluczy powiązanych z podagentami.
- mechanizm `Hooks` obsługujący zdarzenia `pre_tool_use`, `post_tool_use`, `session_start` oraz `session_end`.
- Demo: główny agent uruchamia równelegle trzech izolowanych podagentów, agreguje ich wyniki i zapisuje stan sesji.

Uruchomienie:

```
python3 code/main.py
```

Logi wyjściowe pokazują izolację kontekstu podagentów (rozmiar kontekstu głównego koordynatora nie rośnie niekontrolowanie), przechwytywanie wywołań narzędzi oraz zachowanie stanu sesji.

## Kiedy stosować poszczególne rozwiązania

- **Claude Agent SDK** w projektach opartych głównie na modelach Claude, wymagających funkcjonalności znanych z Claude Code.
- **Claude Managed Agents** w przypadku zapotrzebowania na w pełni zarządzaną, hostowaną infrastrukturę do długotrwałych zadań asynchronicznych.
- **OpenAI Agents SDK** (Lekcja 16) przy budowie agentów w ekosystemie OpenAI.
- **LangGraph + własne narzędzia**, jeśli przepływ pracy opiera się na maszynie stanów w postaci grafu.

## Zadanie wdrożeniowe

Plik `outputs/skill-claude-agent-scaffold.md` definiuje zadanie stworzenia szkieletu aplikacji z użyciem Claude Agent SDK, zawierającego podagentów, haki cyklu życia, magazyn sesji, integrację z serwerem MCP oraz propagację kontekstu śledzenia W3C.

## Ćwiczenia praktyczne

1. Zaimplementuj generator podagentów dzielący 20 zadań na grupy po 5 równolegle uruchamianych agentów pomocniczych. Porównaj rozmiar kontekstu głównego koordynatora z rozmiarem pojedynczego zadania.
2. Dodaj hak `PreToolUse` nakładający limit liczby wywołań `write_file` (maksymalnie 5 na minutę dla danej sesji). Przeanalizuj zachowanie agenta.
3. Użyj metody `list_subkeys` do wygenerowania i wizualizacji drzewa podagentów. Jak prezentuje się struktura przy głębokim zagnieżdżeniu?
4. Przenieś zaimplementowane uproszczone rozwiązanie do rzeczywistego pakietu `claude-agent-sdk`. Jakie różnice napotkasz przy rejestracji narzędzi?
5. Zapoznaj się z dokumentacją usługi Claude Managed Agents. W jakich scenariuszach warto przejść z własnego hostingu na infrastrukturę zarządzaną przez Anthropic?

## Kluczowe terminy

| Termin | Potoczne określenie | Co to dokładnie oznacza |
|------|----------------|--------------------------------------|
| Claude Agent SDK | „Claude Code jako biblioteka” | Środowisko uruchomieniowe udostępniające wbudowane narzędzia, serwery MCP, haki cyklu życia, podagentów i magazyn sesji |
| Podagent (Subagent) | „Agent potomny” | Oddzielny agent z własnym oknem kontekstowym i budżetem tokenów; przekazuje jedynie wyniki końcowe |
| Magazyn sesji | „Baza danych konwersacji” | Moduł do zapisu, wczytywania, listowania i usuwania tur konwersacji z kaskadowym usuwaniem sesji podagentów |
| Hak (Hook) | „Wywołanie zwrotne (callback) cyklu życia” | Funkcja wywoływana automatycznie na określonych etapach (np. przed/po użyciu narzędzia, start/koniec sesji, przesłanie promptu, kompresja, zatrzymanie) |
| Kontekst śledzenia W3C | „Śledzenie międzyprocesowe” | Propagacja identyfikatora spanu nadrzędnego do podprocesu CLI w celu połączenia logów |
| Zarządzani agenci | „Hostowane środowisko uruchomieniowe” | Długotrwałe, asynchroniczne zadania agenta hostowane bezpośrednio przez Anthropic |
| `--session-mirror` | „Zwierciadło sesji” | Flaga CLI zapisująca przebieg sesji na bieżąco do zewnętrznego pliku w celach diagnostycznych |
| Serwer MCP | „Interfejs narzędziowy” | Protokół i usługa udostępniająca agentowi zewnętrzne narzędzia i zasoby danych |

## Dalsze czytanie

- [Omówienie Claude Agent SDK](https://platform.claude.com/docs/en/agent-sdk/overview) — forma biblioteki Claude Code
- [Budowanie agentów z użyciem Claude Agent SDK (Anthropic)](https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk) — wzorce produkcji
- [Przegląd agentów zarządzanych Claude](https://platform.claude.com/docs/en/managed-agents/overview) — alternatywa hostowana
- [SDK dla agentów OpenAI](https://openai.github.io/openai-agents-python/) — odpowiednik
