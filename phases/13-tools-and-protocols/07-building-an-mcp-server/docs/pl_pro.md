# Budowa serwera MCP — zestawy SDK Python + TypeScript

> Większość samouczków MCP ogranicza się do prostych przykładów typu "Hello World" działających przez stdio. W pełni funkcjonalny serwer powinien jednak udostępniać narzędzia, zasoby i szablony promptów, obsługiwać negocjacje możliwości (capabilities), generować ustrukturyzowane komunikaty o błędach oraz działać spójnie niezależnie od wybranego SDK. W tej lekcji od podstaw zbudujemy serwer notatek: zaimplementujemy transport stdio oparty na bibliotece standardowej, obsługę protokołu JSON-RPC oraz trzy kluczowe komponenty serwerowe. Przyjmiemy czytelny styl funkcjonalny, który można z łatwością przenieść do FastMCP (w Python SDK) lub do TypeScript SDK.

**Typ:** Kompilacja
**Języki:** Python (biblioteka standardowa, stdio serwer MCP)
**Wymagania wstępne:** Faza 13 · 06 (Podstawy MCP)
**Czas:** ~75 minut

## Cele nauczania

- Zaimplementuj obsługę metod: `initialize`, `tools/list`, `tools/call`, `resources/list`, `resources/read`, `prompts/list` oraz `prompts/get`.
- Napisz pętlę routującą (dispatch loop) odczytującą komunikaty JSON-RPC ze standardowego wejścia (stdin) i zapisującą odpowiedzi na standardowe wyjście (stdout).
- Generuj ustrukturyzowane odpowiedzi o błędach zgodnie ze specyfikacją JSON-RPC 2.0 oraz rozszerzonymi kodami błędów MCP.
- Przeprowadź migrację kodu opartego na bibliotece standardowej (stdlib) do FastMCP (Python SDK) lub TypeScript SDK bez konieczności przepisywania logiki biznesowej narzędzi.

## Problem

Zanim przejdziesz do zdalnego transportu (faza 13 · 09) lub warstwy autoryzacji (faza 13 · 16), potrzebujesz poprawnie działającego serwera lokalnego. W kontekście MCP lokalność oznacza transport stdio: serwer jest uruchamiany przez klienta jako proces potomny, a komunikaty przesyłane są przez standardowe strumienie wejścia (stdin) i wyjścia (stdout) jako linie tekstu rozdzielone znakiem nowej linii.

Specyfikacja z dnia 2025-11-25 określa, że komunikaty stdio są kodowane jako obiekty JSON, z których każdy musi kończyć się jawnym znakiem nowej linii `\n`. Stosowanie protokołu SSE (Server-Sent Events) w trybie lokalnym zostało uznane za przestarzałe i zostanie całkowicie wycofane w połowie 2026 roku (dla przykładu, wsparcie dla SSE w serwerze Rovo MCP od Atlassiana wygasło 30 czerwca 2026 r., a w Keboola – 1 kwietnia 2026 r.). W przypadku transportu stdio formatem przesyłu danych jest po prostu jeden obiekt JSON w jednej linii.

Serwer notatek doskonale nadaje się na przykład wdrożeniowy, ponieważ wykorzystuje wszystkie trzy podstawowe komponenty serwera. Narzędzia służą do modyfikacji danych (`notes_create`), zasoby udostępniają dane (`notes://{id}`), a szablony promptów dostarczają gotowe instrukcje (`review_note`). Strukturę zbudowaną w tej lekcji można łatwo zaadaptować do dowolnej innej domeny.

## Koncepcja

### Pętla routująca (Dispatch Loop)

```
pętla:
  line = stdin.readline()
  msg = json.loads(line)
  jeśli wiadomość zawiera id:
    obsłuż żądanie -> zapisz odpowiedź
  w przeciwnym wypadku:
    obsłuż powiadomienie -> brak odpowiedzi
```

Trzy kluczowe zasady:

- Nigdy nie pisz na standardowe wyjście (stdout) niczego, co nie jest poprawnym komunikatem JSON-RPC. Logi diagnostyczne i debugowe wysyłaj wyłącznie na standardowe wyjście błędów (stderr).
- Każde żądanie MUSI otrzymać odpowiedź zawierającą identyczny identyfikator `id`.
- Nigdy nie odpowiadaj na powiadomienia (notifications).

### Implementacja metody `initialize`

```python
def initialize(params):
    return {
        "protocolVersion": "2025-11-25",
        "capabilities": {
            "tools": {"listChanged": True},
            "resources": {"listChanged": True, "subscribe": False},
            "prompts": {"listChanged": False},
        },
        "serverInfo": {"name": "notes", "version": "1.0.0"},
    }
```

Deklaruj wyłącznie funkcje, które serwer faktycznie obsługuje. Klient polega na tych informacjach przy decydowaniu o wywołaniu konkretnych metod.

### Implementacja `tools/list` oraz `tools/call`

Metoda `tools/list` zwraca obiekt `{tools: [...]}`, w którym każdy wpis zawiera pola `name`, `description` oraz `inputSchema`. Z kolei `tools/call` przyjmuje `{name, arguments}` i zwraca `{content: [blocks], isError: bool}`.

Bloki w polu `content` muszą mieć zdefiniowane typy. Najpopularniejsze z nich to:

```json
{"type": "text", "text": "Found 2 notes"}
{"type": "resource", "resource": {"uri": "notes://14", "text": "..."}}
{"type": "image", "data": "<base64>", "mimeType": "image/png"}
```

Błędy wywołania narzędzi dzielimy na dwa rodzaje. Błędy protokołu (np. nieznana metoda, niepoprawne parametry) są zwracane jako standardowe błędy JSON-RPC. Z kolei błędy samej logiki narzędzia (np. poprawne wywołanie, ale operacja nie powiodła się) są zwracane jako poprawna odpowiedź z flagą `isError: true` oraz odpowiednią treścią błędu w polu `content`. Dzięki temu model widzi błąd bezpośrednio w kontekście wykonania.

### Implementacja zasobów (Resources)

Zasoby z definicji służą wyłącznie do odczytu. Metoda `resources/list` zwraca ich listę, natomiast `resources/read` zwraca zawartość konkretnego zasobu. Zasoby są identyfikowane przez URI, np. `file://...`, `http://...` lub dedykowane schematy takie jak `notes://`.

Kiedy warto udostępnić dane jako zasób, a nie poprzez narzędzie:

- Model nie wywołuje zasobu bezpośrednio; to klient decyduje o dołączeniu go do kontekstu na życzenie użytkownika.
- Mechanizm subskrypcji pozwala serwerowi na wysyłanie powiadomień o aktualizacji zasobu (`notifications/resources/updated`, patrz faza 13 · 10).
- Faza 13 · 14 rozszerza zasoby o obsługę interaktywnych widoków użytkownika (`ui://`).

### Implementacja szablonów promptów (Prompts)

Szablony promptów to gotowe instrukcje z parametrami, które host prezentuje użytkownikowi (np. jako komendy z ukośnikiem). Przykładowy prompt `review_note` może przyjmować parametr `note_id` i generować ustrukturyzowaną listę komunikatów dla modelu, które klient dołącza do konwersacji.

### Specyfika transportu stdio

- Dane przesyłane są jako linie JSON (JSON Lines). Nie stosuje się tu nagłówków o stałej długości.
- Wyłącz buforowanie wyjścia. Wywołaj `sys.stdout.flush()` po każdym zapisie linii.
- Klient zarządza czasem życia procesu. Serwer powinien zakończyć działanie natychmiast po zamknięciu strumienia stdin (EOF).
- Zawsze obsługuj sygnał SIGPIPE – zapisz informację w logach i wyjdź bezpiecznie.

### Adnotacje (Annotations)

Definicja narzędzia może zawierać obiekt `annotations` opisujący właściwości bezpieczeństwa:

- `readOnlyHint: true` — operacja tylko do odczytu, bezpieczna do ponownego wykonania.
- `destructiveHint: true` — operacja niszcząca lub wywołująca nieodwracalne skutki; klient powinien poprosić użytkownika o potwierdzenie przed jej uruchomieniem.
- `idempotentHint: true` — identyczne parametry wejściowe zawsze dają ten sam rezultat.
- `openWorldHint: true` — narzędzie wchodzi w interakcję z systemami zewnętrznymi.

Klient wykorzystuje te informacje do modyfikacji interfejsu (np. wyświetlania ostrzeżeń) oraz do routingu wywołań (faza 13 · 17).

### Migracja do SDK

Serwer oparty na bibliotece standardowej w pliku `code/main.py` zajmuje około 180 linii kodu. Użycie biblioteki FastMCP (Python) pozwala skrócić ten kod i zapisać go przy użyciu dekoratorów:

```python
from fastmcp import FastMCP
app = FastMCP("notes")

@app.tool()
def notes_search(query: str, limit: int = 10) -> list[dict]:
    ...
```

SDK dla TypeScriptu oferuje analogiczną strukturę. Wykorzystanie gotowych SDK jest rekomendowaną ścieżką rozwoju; kluczowe pojęcia (możliwości, routing, bloki danych) pozostają identyczne.

## Instrukcja użycia

Plik `code/main.py` zawiera kompletny serwer MCP dla aplikacji notatek napisany w czystym Pythonie przy użyciu wyłącznie biblioteki standardowej. Serwer obsługuje metody `initialize`, `tools/list`, `tools/call` (dla narzędzi `notes_list`, `notes_search`, `notes_create`), `resources/list`, `resources/read` oraz szablon promptu `review_note`. Pracę serwera można przetestować, przekazując żądania JSON-RPC na standardowe wejście:

```
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | python main.py
```

Na co warto zwrócić uwagę:

- Routing metod zrealizowany jest jako słownik `dict[str, Callable]` mapujący nazwy metod JSON-RPC na odpowiednie funkcje obsługi.
- Każde narzędzie zwraca listę bloków danych (tablicę), a nie surowy tekst.
- W przypadku wystąpienia błędu podczas wykonywania narzędzia, w odpowiedzi ustawiana jest flaga `isError: true`.

## Wynik wdrożenia

W ramach tej lekcji powstaje plik `outputs/skill-mcp-server-scaffolder.md`. Narzędzie to, na podstawie opisu domeny biznesowej (notatki, zgłoszenia, pliki, bazy danych), generuje szkielet kodu serwera MCP z podziałem na narzędzia, zasoby i prompty, wskazując jednocześnie ścieżkę migracji do oficjalnych SDK.

## Ćwiczenia

1. Uruchom `code/main.py` i przetestuj jego działanie, przekazując ręcznie przygotowane komunikaty JSON-RPC. Utwórz nową notatkę za pomocą `notes_create`, a następnie odczytaj ją, korzystając z `resources/read`.

2. Dodaj narzędzie `notes_delete` z adnotacją `annotations: {destructiveHint: true}`. Sprawdź, czy klient wyświetli ostrzeżenie przed uruchomieniem tej operacji (test wymaga użycia rzeczywistego klienta, np. Claude Desktop).

3. Zaimplementuj obsługę metody `resources/subscribe` tak, aby serwer wysyłał powiadomienie `notifications/resources/updated` za każdym razem, gdy powiązana notatka zostanie zmodyfikowana. Dodaj proces monitorujący stan zasobów.

4. Przenieś logikę serwera do FastMCP. Rozmiar kodu w Pythonie powinien spaść poniżej 80 linii. Upewnij się, że struktura przesyłanych komunikatów na poziomie transportu stdio nie uległa zmianie (wykorzystaj te same testowe zapytania JSON-RPC).

5. Przeczytaj uważnie sekcję specyfikacji dotyczącą narzędzi serwerowych (`server/tools`). Zidentyfikuj jedno pole definicji narzędzia, które nie zostało zaimplementowane w naszym przykładowym serwerze, i dodaj jego obsługę.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Serwer MCP | „Serwer narzędzi” | Proces obsługujący komunikację MCP JSON-RPC przez stdio lub HTTP |
| Transport stdio | „Model podprocesu” | Uruchomienie serwera jako procesu potomnego klienta; komunikacja przez stdin/stdout |
| Router (Dispatcher) | „Obsługa metod” | Mechanizm mapujący nazwę metody JSON-RPC na konkretną funkcję obsługującą |
| Blok treści (Content Block) | „Element wyniku” | Ustrukturyzowany obiekt w tablicy `content` w odpowiedzi na wywołanie narzędzia |
| `isError` | „Błąd wykonania narzędzia” | Flaga wskazująca na błąd biznesowy narzędzia, odróżniająca go od błędów protokołu JSON-RPC |
| Adnotacje (Annotations) | „Flagi bezpieczeństwa” | Flagi informacyjne takie jak readOnly, destructive, idempotent lub openWorld |
| FastMCP | „Framework Python SDK” | Wysokopoziomowa biblioteka ułatwiająca tworzenie serwerów MCP w Pythonie przy użyciu dekoratorów |
| URI zasobu | „Adresowalny zasób” | Ścieżka (np. `file://`, `db://` lub schemat niestandardowy) jednoznacznie identyfikująca zasób |
| Szablon promptu | „Komenda z ukośnikiem” | Zdefiniowany przez serwer szablon instrukcji dla modelu z parametrami uzupełnianymi przez klienta |
| Deklaracja możliwości | „Flagi capabilities” | Parametry określające obsługiwane funkcje protokołu, wymieniane w metodzie `initialize` |

## Dalsze czytanie

- [Model Context Protocol — Python SDK](https://github.com/modelcontextprotocol/python-sdk) — oficjalna referencyjna implementacja w języku Python.
- [Model Context Protocol — TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk) — oficjalne SDK dla języków TypeScript i Node.js.
- [FastMCP — Server Framework](https://gofastmcp.com/) — framework ułatwiający deklarowanie serwerów w stylu dekoratorów.
- [MCP — Server Quickstart Guide](https://modelcontextprotocol.io/quickstart/server) — kompletny samouczek budowy serwera krok po kroku.
- [MCP — Server Tools Specification](https://modelcontextprotocol.io/specification/2025-11-25/server/tools) — dokumentacja techniczna komunikatów z przestrzeni `tools/*`.
