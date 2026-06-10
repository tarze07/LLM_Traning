# Budowa serwera MCP — zestawy SDK Python + TypeScript

> Większość tutoriali MCP pokazuje tylko stdio hello-worlds. Prawdziwy serwer udostępnia narzędzia, zasoby i podpowiedzi, obsługuje negocjacje możliwości, emituje błędy strukturalne i działa tak samo we wszystkich zestawach SDK. W tej lekcji kompleksowo budujemy serwer notatek: transport stdlib stdio, wysyłanie JSON-RPC, trzy operacje podstawowe serwera i styl czysto funkcjonalny, który po ukończeniu nauki można przenieść do zestawu FastMCP pakietu Python SDK lub zestawu SDK TypeScript.

**Typ:** Kompilacja
**Języki:** Python (stdlib, stdio serwer MCP)
**Wymagania wstępne:** Faza 13 · 06 (podstawy MCP)
**Czas:** ~75 minut

## Cele nauczania

- Implementacja `initialize`, `tools/list`, `tools/call`, `resources/list`, `resources/read`, `prompts/list` i metody `prompts/get`.
- Napisz pętlę wysyłającą, która odczytuje komunikaty JSON-RPC ze standardowego wejścia i zapisuje odpowiedzi na standardowe wyjście.
- Emituj uporządkowane odpowiedzi na błędy zgodnie ze specyfikacją JSON-RPC 2.0 i dodatkowymi kodami MCP.
- Ukończ implementację stdlib do FastMCP (Python SDK) lub TypeScript SDK bez przepisywania logiki narzędzia.

## Problem

Zanim będziesz mógł skorzystać ze zdalnego transportu (faza 13 · 09) lub warstwy autoryzacji (faza 13 · 16), potrzebujesz czystego serwera lokalnego. Lokalne oznacza stdio: serwer jest uruchamiany przez klienta jako proces potomny, komunikaty przepływają przez standardowe wejście/stdout i są rozdzielane znakami nowej linii.

Specyfikacja z dnia 25.11.2025 określa, że ​​komunikaty stdio są kodowane jako obiekty JSON z jawnym separatorem `\n`. Nie ma tutaj SSE; SSE był starym trybem zdalnym i zostanie usunięty w połowie 2026 r. (serwer Rovo MCP firmy Atlassian wycofał go 30 czerwca 2026 r.; Keboola 1 kwietnia 2026 r.). W przypadku stdio jeden obiekt JSON na linię to cały format drutu.

Serwer notatek jest w dobrym stanie, ponieważ wykonuje wszystkie trzy operacje podstawowe serwera. Narzędzia dokonują mutacji (`notes_create`). Zasoby udostępniają dane (`notes://{id}`). Wyświetla szablony wysyłki (`review_note`). Kształt tej lekcji można uogólnić na dowolną dziedzinę.

## Koncepcja

### Pętla wysyłkowa

```
loop:
  line = stdin.readline()
  msg = json.loads(line)
  if has id:
    handle request -> write response
  else:
    handle notification -> no response
```

Trzy zasady:

- Nie drukuj na standardowe wyjście niczego, co nie jest kopertą JSON-RPC. Dzienniki debugowania trafiają do stderr.
- Każdemu żądaniu MUSI towarzyszyć odpowiedź zawierająca ten sam `id`.
- NIE WOLNO odpowiadać na powiadomienia.

### Implementacja `initialize`

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

Deklaruj tylko to, co wspierasz. Klient polega na możliwościach ustawionych dla funkcji bramek.

### Implementacja `tools/list` i `tools/call`

`tools/list` zwraca `{tools: [...]}`, przy czym każdy wpis zawiera `name`, `description`, `inputSchema`. `tools/call` pobiera `{name, arguments}` i zwraca `{content: [blocks], isError: bool}`.

Wpisywane są bloki treści. Najczęstsze:

```json
{"type": "text", "text": "Found 2 notes"}
{"type": "resource", "resource": {"uri": "notes://14", "text": "..."}}
{"type": "image", "data": "<base64>", "mimeType": "image/png"}
```

Błędy narzędzi mają dwie postacie. Błędy na poziomie protokołu (nieznana metoda, nieprawidłowe parametry) to błędy JSON-RPC. Błędy na poziomie narzędzia (poprawne wywołanie, ale narzędzie nie powiodło się) są zwracane jako `{content: [...], isError: true}`. Dzięki temu model może zobaczyć awarię w jej kontekście.

### Wdrażanie zasobów

Zasoby są z założenia przeznaczone tylko do odczytu. `resources/list` zwraca manifest; `resources/read` zwraca treść. Identyfikatory URI mogą mieć postać `file://...`, `http://...` lub według niestandardowego schematu, takiego jak `notes://`.

Kiedy udostępniasz dane jako zasób, a nie narzędzie:

- Model tego nie „woła”; klient może wstawić go do kontekstu na żądanie użytkownika.
- Subskrypcje umożliwiają serwerowi przesyłanie aktualizacji w przypadku zmiany zasobu (faza 13 · 10).
- Faza 13 · 14 rozszerza to o `ui://` dla zasobów interaktywnych.

### Implementowanie podpowiedzi

Podpowiedzi to szablony z nazwanymi argumentami. Host wyświetla je jako polecenia ukośnika. Podpowiedź `review_note` może przyjąć argument `note_id` i wygenerować szablon podpowiedzi zawierający wiele komunikatów, który klient przekazuje do swojego modelu.

### Subtelności transportu Stdio

- JSON rozdzielany znakami nowej linii. Brak obramowania o ustalonej długości.
- Nie buforuj. `sys.stdout.flush()` po każdym zapisie.
- Klient kontroluje czas życia. Kiedy stdin się zamknie (EOF), wyjdź czysto.
- Nie obsługuj SIGPIPE po cichu; zaloguj się i wyjdź.

### Adnotacje

Każde narzędzie może zawierać `annotations` opisujący właściwości bezpieczeństwa:

- `readOnlyHint: true` — czysty odczyt, można bezpiecznie spróbować ponownie.
- `destructiveHint: true` — nieodwracalne skutki uboczne; klient powinien potwierdzić.
- `idempotentHint: true` — te same dane wejściowe dają takie same wyniki.
- `openWorldHint: true` — współdziała z systemami zewnętrznymi.

Klient używa ich do decydowania o UX (okna dialogowe potwierdzenia, wskaźniki stanu) i routingu (faza 13 · 17).

### Ścieżka ukończenia studiów

Serwer stdlib w `code/main.py` ma około 180 linii. FastMCP (Python) sprowadza tę samą logikę do stylu dekoratora:

```python
from fastmcp import FastMCP
app = FastMCP("notes")

@app.tool()
def notes_search(query: str, limit: int = 10) -> list[dict]:
    ...
```

Zestaw SDK TypeScript ma równoważny kształt. Ścieżka ukończenia studiów jest dostępna, gdy jesteś gotowy; koncepcje (możliwości, wysyłka, bloki treści) są takie same.

## Użyj tego

`code/main.py` to kompletny serwer Notes MCP poprzez stdio, tylko stdlib. Obsługuje `initialize`, `tools/list`, `tools/call` dla trzech narzędzi (`notes_list`, `notes_search`, `notes_create`), `resources/list` i `resources/read` dla każdej notatki oraz zachętę `review_note`. Można nim sterować, przesyłając komunikaty JSON-RPC:

```
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | python main.py
```

Na co zwrócić uwagę:

- Moduł rozsyłający to `dict[str, Callable]` oznaczony nazwą metody.
- Każdy wykonawca narzędzia zwraca listę bloków treści, a nie pusty ciąg znaków.
- `isError: true` jest ustawiane, gdy executor podbija.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-mcp-server-scaffolder.md`. Biorąc pod uwagę domenę (notatki, bilety, pliki, bazę danych), umiejętność tworzy rusztowanie serwera MCP z odpowiednimi narzędziami/zasobami/podziałem podpowiedzi i ścieżką stopniowania SDK.

## Ćwiczenia

1. Uruchom `code/main.py` i steruj nim za pomocą ręcznie zbudowanych komunikatów JSON-RPC. Ćwicz `notes_create`, a następnie `resources/read`, aby pobrać nową notatkę.

2. Dodaj narzędzie `notes_delete` z `annotations: {destructiveHint: true}`. Sprawdź, czy klient wyświetli okno dialogowe z potwierdzeniem (wymaga to prawdziwego hosta; Claude Desktop działa).

3. Zaimplementuj `resources/subscribe` tak, aby serwer przesyłał `notifications/resources/updated` za każdym razem, gdy modyfikowana jest notatka. Dodaj zadanie podtrzymujące.

4. Przenieś serwer do FastMCP. Plik Pythona powinien zmniejszyć się do mniej niż 80 linii. Zachowanie przewodu musi być identyczne; sprawdź za pomocą tej samej wiązki testowej JSON-RPC.

5. Przeczytaj sekcję `server/tools` specyfikacji i znajdź jedno pole definicji narzędzia, które nie zostało zaimplementowane na serwerze tej lekcji. (Wskazówka: jest ich kilka; wybierz jeden i dodaj go.)

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Serwer MCP | „To, co odsłania narzędzia” | Proces mówiący MCP JSON-RPC przez stdio lub HTTP |
| transport stdio | „Model procesu potomnego” | Serwer jest uruchamiany przez klienta; komunikuje się poprzez stdin/stdout |
| Dyspozytor | „Router metod” | Mapa nazwy metody JSON-RPC na funkcję obsługi |
| Blok treści | „Fragment wyniku narzędzia” | Wpisany element w tablicy `content` odpowiedzi narzędzia |
| `isError` | „Awaria na poziomie narzędzia” | Sygnalizuje awarię narzędzia; odróżnia od błędu JSON-RPC |
| Adnotacje | „Wskazówki dotyczące bezpieczeństwa” | readOnly / destrukcyjne / idempotentne / flagi openWorld |
| FastMCP | „SDK Pythona” | Framework wyższego poziomu oparty na dekoratorach, oparty na protokole MCP |
| URI zasobu | „Dane adresowalne” | `file://`, `db://` lub niestandardowy schemat identyfikujący zasób |
| Szablon podpowiedzi | „Krótki opis polecenia z ukośnikiem” | Szablon dostarczony przez serwer z miejscami na argumenty dla interfejsów użytkownika hosta |
| Deklaracja zdolności | „Przełączanie funkcji” | Flagi per-primitive zadeklarowane w `initialize` |

## Dalsze czytanie

- [Model Context Protocol — Python SDK](https://github.com/modelcontextprotocol/python-sdk) — referencyjna implementacja Pythona
- [Model Context Protocol — TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk) — równoległa implementacja TS
- [FastMCP — framework serwerowy](https://gofastmcp.com/) — API Pythona w stylu dekoratora dla serwerów MCP
- [MCP — przewodnik po serwerze Szybki start](https://modelcontextprotocol.io/quickstart/server) — kompleksowy samouczek przy użyciu dowolnego pakietu SDK
- [MCP — specyfikacja narzędzi serwerowych](https://modelcontextprotocol.io/specification/2025-11-25/server/tools) — pełna dokumentacja narzędzi/* wiadomości