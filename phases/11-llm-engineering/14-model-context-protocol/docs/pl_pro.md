# Model Context Protocol (MCP)

> Każda aplikacja LLM stworzona przed 2025 rokiem implementowała swój własny, niestandardowy format definiowania narzędzi. Pod koniec 2024 roku firma Anthropic zaprezentowała protokół MCP, który został szybko adoptowany przez Claude, OpenAI oraz Google. Od 2026 roku jest to domyślny standard komunikacji służący do łączenia dowolnego modelu LLM z dowolnym narzędziem, źródłem danych lub agentem. Wystarczy napisać jeden serwer MCP, aby komunikował się z nim każdy kompatybilny host.

**Typ:** Kompilacja  
**Języki:** Python  
**Wymagania wstępne:** Faza 11 · 09 (Wywoływanie funkcji), Faza 11 · 03 (Ustrukturyzowane dane wyjściowe)  
**Czas:** ~75 minut  

## Problem

Wdrażasz chatbota, który potrzebuje trzech narzędzi: zapytań do bazy danych SQL, integracji z API kalendarza oraz modułu odczytu plików. Na potrzeby modeli Claude (Anthropic) przygotowujesz trzy schematy JSON. Chwilę później biznes wymaga dodania tych samych funkcji w ChatGPT – musisz przepisać definicje pod kątem parametru `tools` OpenAI. Następnie dochodzą narzędzia takie jak Cursor, Zed i Claude Code – co wymusza kolejne modyfikacje schematów ze względu na drobne różnice w specyfikacji JSON u każdego dostawcy. Gdy po tygodniu Anthropic dodaje nowe pole, stajesz przed koniecznością aktualizacji i testowania sześciu różnych definicji.

Tak wyglądała rzeczywistość przed powstaniem MCP. Każdy host (aplikacja uruchamiająca LLM) oraz każdy serwer (kod udostępniający narzędzia i dane) korzystały z dedykowanych, niekompatybilnych ze sobą interfejsów. Skalowanie systemu wymagało budowania skomplikowanej macierzy integracji N×M.

Model Context Protocol (MCP) całkowicie eliminuje ten problem. Definiuje jedną wspólną specyfikację opartą na protokole JSON-RPC 2.0. Jeden serwer MCP udostępnia narzędzia, zasoby i prompty, a dowolny kompatybilny host — taki jak Claude Desktop, ChatGPT, Cursor, Claude Code, Zed czy frameworki agentowe — potrafi je automatycznie wykryć i wywołać bez potrzeby pisania dedykowanego kodu integrującego.

Od początku 2026 roku MCP stanowi domyślny protokół integracji narzędzi i kontekstu dla Wielkiej Trójki (Anthropic, OpenAI, Google) oraz wiodących systemów agentowych.

## Koncepcja

![MCP: jeden host, jeden serwer, trzy możliwości](../assets/mcp-architecture.svg)

**Trzy podstawowe prymitywy (Primitives).** Serwer MCP udostępnia hostom trzy kluczowe elementy:

1. **Narzędzia (Tools)** — funkcje wykonywalne, które model może wywołać (odpowiednik `tools` w OpenAI lub `tool_use` w Anthropic). Każde narzędzie posiada nazwę, opis, schemat parametrów wejściowych (JSON Schema) oraz logikę wykonawczą.
2. **Zasoby (Resources)** — dane i treści tylko do odczytu (pliki, rekordy z bazy, odpowiedzi z API), o które model lub użytkownik może poprosić. Są one adresowane za pomocą unikalnych identyfikatorów URI (np. `file:///logs/app.log`).
3. **Prompty (Prompts)** — gotowe szablony promptów z parametrami, które użytkownik może wywołać jako skróty w interfejsie czatu (np. za pomocą komend z ukośnikiem `/`).

**Protokół transmisji.** MCP opiera się na specyfikacji JSON-RPC 2.0 i może być przesyłany przez standardowe wejście/wyjście (stdio), protokół WebSocket lub strumieniowy HTTP. Każdy komunikat ma ujednoliconą strukturę, np. `{"jsonrpc": "2.0", "method": "tools/call", "params": {...}, "id": 1}`. Standardowe metody wykrywania to `tools/list`, `resources/list` oraz `prompts/list`, natomiast metody wywołania to `tools/call`, `resources/read` i `prompts/get`.

**Host, Klient i Serwer.** Hostem jest aplikacja nadrzędna (np. Claude Desktop). Klient to moduł wbudowany w hosta, odpowiedzialny za komunikację z konkretnym serwerem MCP. Serwer to Twój kod udostępniający narzędzia. Jeden host może mieć jednocześnie zamontowanych wiele niezależnych serwerów MCP.

### Handshake (Uścisk dłoni)

Każda sesja MCP rozpoczyna się od wywołania metody `initialize`. Klient przesyła wersję protokołu oraz listę obsługiwanych funkcji. Serwer odpowiada, podając swoją nazwę, wersję oraz deklarację wspieranych prymitywów (`tools`, `resources`, `prompts`, `logging` itp.). Cała dalsza komunikacja opiera się na tych ustaleniach.

### Czym MCP NIE jest:

- Nie jest to silnik wyszukiwania RAG. Zadaniem RAG (Faza 11 · 06) nadal pozostaje selekcja i wyszukiwanie danych; MCP stanowi jedynie warstwę transportową pozwalającą na prezentację tych danych w postaci ujednoliconych zasobów (resources).
- Nie jest to framework do budowy agentów. MCP to warstwa niskopoziomowej komunikacji (infrastruktura sieciowa). Ponad nim działają frameworki takie jak LangGraph, PydanticAI czy OpenAI Agents SDK.
- Nie jest to technologia zamknięta dla produktów Anthropic. Specyfikacja oraz referencyjne pakiety SDK są w pełni otwarte (open-source) i rozwijane w ramach niezależnej organizacji GitHub `modelcontextprotocol`.

## Zbuduj to

### Krok 1: Minimalny serwer MCP w Pythonie

Użyjemy oficjalnej biblioteki `mcp` oraz klasy pomocniczej `FastMCP` do szybkiej rejestracji narzędzi za pomocą dekoratorów.

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("demo-server")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b

@mcp.resource("config://app")
def app_config() -> str:
    """Return the app's current JSON config."""
    return '{"env": "prod", "region": "us-east-1"}'

@mcp.prompt()
def code_review(language: str, code: str) -> str:
    """Review code for correctness and style."""
    return f"You are a senior {language} reviewer. Review:\n\n{code}"

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

Typy argumentów w funkcjach Pythona (type hints) są automatycznie konwertowane na schematy JSON Schema widoczne dla hosta. Możesz uruchomić ten serwer bezpośrednio w Claude Desktop lub Cursorze, wskazując plik w konfiguracji.

### Krok 2: Odpytywanie serwera MCP z poziomu klienta

Klient komunikuje się z serwerem za pomocą komunikatów JSON-RPC. Poniższy kod przedstawia inicjalizację sesji i wywołanie narzędzia.

```python
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp import ClientSession

params = StdioServerParameters(command="python", args=["server.py"])

async def call_add(a: int, b: int) -> int:
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            result = await session.call_tool("add", {"a": a, "b": b})
            return int(result.content[0].text)
```

Metoda `session.list_tools()` zwraca zestaw schematów narzędzi, które host może przekazać modelowi LLM. Gdy model podejmie decyzję o użyciu narzędzia, generuje blok `tool_use`, który klient następnie przesyła do wykonania na serwerze MCP.

### Krok 3: Transport sieciowy przez HTTP i SSE

Protokół stdio (standardowe wejście/wyjście) jest idealny do lokalnego programowania. Dla usług zdalnych stosuje się transport HTTP ze strumieniowaniem zdarzeń SSE (Server-Sent Events) do asynchronicznej komunikacji dwukierunkowej.

```python
# Uruchomienie serwera z transportem HTTP
mcp.run(transport="streamable-http", host="0.0.0.0", port=8765)
```

Konfiguracja hosta (np. plik `mcp.json` w Claude Desktop lub `~/.mcp.json` w Claude Code):

```json
{
  "mcpServers": {
    "demo-http": {
      "type": "http",
      "url": "https://tools.example.com/mcp"
    }
  }
}
```

Dekoratory rejestracji narzędzi na serwerze pozostają bez zmian – modyfikacji ulega jedynie warstwa transportowa.

### Krok 4: Bezpieczeństwo i kontrola dostępu

Serwer MCP uruchamia kod na maszynie hosta, co stwarza istotne wyzwania bezpieczeństwa. Zastosuj trzy poniższe zasady obronne:

- **Biała lista ścieżek (Roots).** Host udostępnia serwerowi listę dozwolonych katalogów (roots). Weryfikuj te ścieżki w kodzie serwera; nigdy nie ufaj ścieżkom relatywnym ani bezwzględnym przesyłanym bezpośrednio przez model LLM (Directory Traversal).
- **Zatwierdzanie operacji destrukcyjnych (Human-in-the-Loop).** Narzędzia modyfikujące stan systemu (zapis, usuwanie, wysyłka maili) muszą wymagać akceptacji człowieka. Oznaczaj takie funkcje parametrem `destructiveHint: true` w metadanych narzędzia, co wymusi wyświetlenie okna potwierdzenia w interfejsie hosta.
- **Ochrona przed zatruciem kontekstu (Prompt Poisoning).** Treści odczytywane z zasobów mogą zawierać złośliwe instrukcje (indirect prompt injection). Traktuj dane z zasobów jako surowy tekst i filtruj je przed przekazaniem do modelu. Zobacz lekcję 12 (Guardrails).

Kompletny, działający kod klienta i serwera prezentujący te mechanizmy znajdziesz w pliku `code/main.py`.

## Typowe problemy i pułapki protokołu

- **Dryf stanu narzędzi.** Model pobiera listę narzędzi (`tools/list`) na początku rozmowy. Jeśli zestaw narzędzi zmieni się w trakcie sesji, model może próbować wywołać nieistniejące funkcje. Serwer powinien wysłać powiadomienie `notifications/tools/list_changed` w celu aktualizacji stanu po stronie hosta.
- **Przeciążenie kontekstu dużymi plikami.** Wklejenie całego logu o rozmiarze 2 MB do kontekstu marnuje tokeny i podnosi koszty. Stosuj paginację lub generuj streszczenia danych bezpośrednio po stronie serwera MCP.
- **Przepełnienie budżetu narzędzi.** Podłączenie zbyt wielu serwerów MCP jednocześnie obniża precyzję modelu (Faza 11 · 05). Większość modeli wykazuje spadek jakości wywołań przy liczbie narzędzi przekraczającej 40.
- **Konflikty wersji protokołu.** Różne wersje specyfikacji (np. 2024-11 czy 2025-06) wprowadzają drobne zmiany w strukturze pól. Zablokuj wersję protokołu w swoim potoku CI/CD.
- **Blokowanie strumienia stdio.** Serwery MCP komunikujące się przez stdio nie mogą wypisywać komunikatów diagnostycznych (np. `print()`) na standardowe wyjście (stdout), ponieważ zakłóca to strukturę JSON-RPC. Wszelkie logi deweloperskie kieruj wyłącznie na standardowe wyjście błędów (stderr).

## Wybór technologii MCP

| Przypadek użycia | Rekomendowany wybór |
|----------|------|
| Lokalny deweloper, narzędzia dla jednego użytkownika | Pakiet Python `FastMCP`, transport stdio |
| Narzędzia dla zespołów chmurowych / integracje SaaS | Transport HTTP ze strumieniowaniem (SSE), autoryzacja OAuth 2.1 |
| Rozszerzenia VS Code / Aplikacje Node.js | Oficjalna biblioteka `@modelcontextprotocol/sdk` (TypeScript) |
| Usługi o najwyższej wydajności, aplikacje systemowe | Oficjalny SDK dla języka Rust (`modelcontextprotocol/rust-sdk`) |
| Gotowe integracje i wtyczki | Monorepo `modelcontextprotocol/servers` (gotowe serwery dla baz Postgres, Slacka, GitHuba, Puppeteera) |

Złota zasada: Jeśli dane narzędzie jest tylko do odczytu, może korzystać z cache i będzie wywoływane przez wiele różnych hostów – zaimplementuj je jako serwer MCP. Jeśli logika jest unikalna dla jednej aplikacji – zachowaj ją jako funkcję lokalną (Faza 11 · 09).

## Co zostało wygenerowane

Ta lekcja tworzy plik `outputs/skill-mcp-server-designer.md` — ramy decyzyjne i szablon do projektowania bezpiecznych serwerów MCP:

```markdown
---
name: mcp-server-designer
description: Projektuj i generuj strukturę serwerów MCP z narzędziami, zasobami i domyślnymi zabezpieczeniami.
version: 1.0.0
phase: 11
lesson: 14
tags: [llm-engineering, mcp, tool-use]
---

Na podstawie opisu domeny (wewnętrzne API, baza danych, system plików) oraz hostów docelowych wygeneruj:

1. Mapę prymitywów: Określenie, które funkcje stają się narzędziami (tools), zasobami (resources) lub promptami (prompts).
2. Plan autoryzacji: Dobór i uzasadnienie transportu (stdio, HTTP z kluczem API, OAuth 2.1 z PKCE).
3. Szkice schematów: Schematy JSON Schema dla parametrów narzędzi z opisami zoptymalizowanymi pod kątem wyboru modelu (descriptions).
4. Listę operacji destrukcyjnych: Funkcje modyfikujące stan systemu wymagające flagi `destructiveHint: true` i akceptacji użytkownika.
5. Plan testów: Dla każdego narzędzia zdefiniuj testy kontraktowe schematu, testy integracyjne klienta oraz testy odporności na prompt injection.

Blokuj wdrożenie serwerów modyfikujących dane bez mechanizmów potwierdzeń. Dziel serwery o liczbie narzędzi >20 na mniejsze serwery domenowe.
```

## Ćwiczenia

1. **Poziom łatwy.** Dodaj do serwera `demo-server` nowe narzędzie o nazwie `subtract` (odejmowanie). Przetestuj integrację w Claude Desktop i upewnij się, że host poprawnie wykrywa zmianę dzięki powiadomieniu `notifications/tools/list_changed` bez konieczności restartu serwera.
2. **Poziom średni.** Zaimplementuj zasób (resource) zwracający 100 ostatnich linii pliku `/var/log/app.log`. Wdróż walidację katalogów (roots whitelist), aby próba odczytania pliku `../../etc/passwd` została zablokowana i nie powodowała wycieku danych, nawet jeśli model wygeneruje takie zapytanie.
3. **Poziom trudny.** Stwórz serwer proxy MCP (orchestrator), który multipleksuje trzy niezależne serwery MCP (np. system plików, GitHub i bazę danych) w jeden ujednolicony interfejs. Obsłuż ewentualne konflikty nazw narzędzi i poprawnie przekazuj powiadomienia o zmianie stanu narzędzi (`tools/list_changed`) do hosta nadrzędnego.

## Kluczowe terminy

| Termin | Potoczne rozumienie | Rzeczywiste znaczenie techniczne |
|------|-----------------|----------------------|
| MCP | „Standard narzędzi dla AI” | Otwarty protokół komunikacyjny oparty na JSON-RPC 2.0 do łączenia modeli LLM z narzędziami i danymi |
| Host | „Edytor Cursor / Claude” | Aplikacja uruchamiająca model LLM i integrująca klientów MCP do komunikacji z serwerami |
| Klient | „Połączenie z narzędziem” | Podzespół hosta odpowiedzialny za komunikację JSON-RPC z jednym konkretnym serwerem MCP |
| Serwer | „Wtyczka z narzędziami” | Twój kod lub usługa udostępniająca narzędzia, zasoby i prompty zgodnie ze specyfikacją MCP |
| Narzędzie (Tool) | „Wywołanie funkcji” | Funkcja wykonywalna zdefiniowana schematem JSON Schema, którą model LLM może uruchomić w locie |
| Zasób (Resource) | „Dane tekstowe” | Dane tylko do odczytu adresowane unikalnym URI, które model może pobrać do swojego kontekstu |
| Prompt | „Szablon zapytania” | Gotowy szablon promptu z parametrami ułatwiający użytkownikowi interakcję z chatbotem |
| Transport stdio | „Lokalne stdio” | Uruchomienie serwera jako procesu potomnego hosta i przesyłanie komunikatów przez stdin/stdout |
| Transport HTTP | „Zdalne API” | Komunikacja chmurowa oparta na zapytaniach POST i strumieniowaniu Server-Sent Events (SSE) |

## Dalsze czytanie

- [Model Context Protocol Specification](https://modelcontextprotocol.io/specification) — oficjalna specyfikacja protokołu MCP.
- [GitHub modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) — oficjalne, referencyjne implementacje serwerów MCP (Postgres, Slack, Puppeteer).
- [Anthropic — Introducing MCP (listopad 2024 r.)](https://www.anthropic.com/news/model-context-protocol) — oficjalny artykuł prezentujący założenia projektowe i motywację stojącą za protokołem.
- [Python SDK for MCP](https://github.com/modelcontextprotocol/python-sdk) — oficjalne biblioteki dla języka Python użyte w tej lekcji.
- [MCP Security and Best Practices](https://modelcontextprotocol.io/docs/concepts/security) — omówienie kwestii bezpieczeństwa, reguł roots oraz barier ochronnych.
- [Google Agent2Agent (A2A) Specification](https://google.github.io/A2A/) — standard komunikacji między agentami dopełniający specyfikację MCP.
- [Anthropic — Building Effective Agents (grudzień 2024 r.)](https://www.anthropic.com/research/building-effective-agents) — analiza wzorców projektowych i struktur agentowych z wykorzystaniem narzędzi i protokołu MCP.
