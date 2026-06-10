# aplikacji MCP — interaktywne zasoby interfejsu użytkownika za pośrednictwem `ui://`

> Dane wyjściowe narzędzia tekstowego ograniczają to, co mogą pokazać agenci. Aplikacje MCP (SEP-1724, wersja oficjalna z 26 stycznia 2026 r.) umożliwiają narzędziu zwracanie interaktywnego kodu HTML w trybie piaskownicy renderowanego inline w Claude Desktop, ChatGPT, Cursor, Goose i VS Code. Pulpity nawigacyjne, formularze, mapy, sceny 3D, wszystko w jednym rozszerzeniu. W tej lekcji omówiono schemat zasobów `ui://`, MIME `text/html;profile=mcp-app`, protokół postMessage iframe-sandbox oraz powierzchnię zabezpieczeń związaną z możliwością renderowania HTML przez serwer.

**Typ:** Kompilacja
**Języki:** Python (stdlib, emiter zasobów interfejsu użytkownika), HTML (przykładowa aplikacja)
**Wymagania wstępne:** Faza 13 · 07 (serwer MCP), Faza 13 · 10 (zasoby)
**Czas:** ~75 minut

## Cele nauczania

- Zwróć zasób `ui://` z wywołania narzędzia i ustaw poprawne MIME i metadane.
- Zadeklaruj interfejs użytkownika powiązany z narzędziem za pomocą `_meta.ui.resourceUri`, `_meta.ui.csp` i `_meta.ui.permissions`.
- Zaimplementuj piaskownicę iframe postMessage JSON-RPC do komunikacji między interfejsem użytkownika a hostem.
- Zastosuj domyślne ustawienia CSP i zasad uprawnień, które chronią przed atakami pochodzącymi z interfejsu użytkownika.

## Problem

Narzędzie `visualize_timeline` z 2025 r. może zwrócić „Oto 14 notatek uporządkowanych chronologicznie:…”. To jest akapit. Użytkownicy rzeczywiście chcą interaktywnej osi czasu. Przed aplikacjami MCP dostępne były następujące opcje: interfejsy API widżetów specyficzne dla klienta (artefakty Claude, niestandardowy HTML GPT OpenAI) lub całkowity brak interfejsu użytkownika.

Aplikacje MCP (SEP-1724, wysłane 26 stycznia 2026 r.) standaryzują umowę. Wynik narzędzia zawiera `resource`, którego URI to `ui://...` i którego MIME to `text/html;profile=mcp-app`. Host renderuje go w ramce iframe w trybie piaskownicy z ograniczonym CSP i bez dostępu do sieci, chyba że zostanie to wyraźnie przyznane. Interfejs użytkownika wewnątrz ramki iframe wysyła wiadomości do hosta za pomocą małego dialektu postMessage JSON-RPC.

Każdy kompatybilny klient (Claude Desktop, ChatGPT, Goose, VS Code) renderuje ten sam zasób `ui://` w ten sam sposób. Jeden serwer, jeden pakiet HTML, uniwersalny interfejs użytkownika.

## Koncepcja

### Schemat zasobów `ui://`

Narzędzie zwraca:

```json
{
  "content": [
    {"type": "text", "text": "Here is your notes timeline:"},
    {"type": "ui_resource", "uri": "ui://notes/timeline"}
  ],
  "_meta": {
    "ui": {
      "resourceUri": "ui://notes/timeline",
      "csp": {
        "defaultSrc": "'self'",
        "scriptSrc": "'self' 'unsafe-inline'",
        "connectSrc": "'self'"
      },
      "permissions": []
    }
  }
}
```

Następnie host wywołuje `resources/read` pod adresem URI `ui://notes/timeline` i zwraca:

```json
{
  "contents": [{
    "uri": "ui://notes/timeline",
    "mimeType": "text/html;profile=mcp-app",
    "text": "<!doctype html>..."
  }]
}
```

### Piaskownica iframe

Host renderuje kod HTML w piaskownicy `<iframe>` za pomocą:

- `sandbox="allow-scripts allow-same-origin"` (lub bardziej rygorystyczne w zależności od deklaracji serwera)
- Zadeklarowany przez serwer CSP zastosowany poprzez nagłówki odpowiedzi.
- Żadnych plików cookie, żadnej pamięci lokalnej pochodzącej od hosta.
- Dostęp do sieci ograniczony do `connectSrc` w CSP.

### Protokół postMessage

Element iframe komunikuje się z hostem poprzez `window.postMessage`. Mały dialekt JSON-RPC 2.0:

Zawsze przypinaj `targetOrigin` do dokładnego pochodzenia partnera, a po stronie odbierającej sprawdzaj `event.origin` na liście dozwolonych przed przetworzeniem jakiegokolwiek ładunku. Nigdy nie używaj `"*"` po żadnej stronie tego kanału — treść zawiera wywołania narzędzi i odczyty zasobów.

```js
// iframe to host  (pin to host origin)
window.parent.postMessage({
  jsonrpc: "2.0",
  id: 1,
  method: "host.callTool",
  params: { name: "notes_update", arguments: { id: "note-14", title: "..." } }
}, "https://host.example.com");

// host to iframe  (pin to iframe origin)
iframe.contentWindow.postMessage({
  jsonrpc: "2.0",
  id: 1,
  result: { content: [...] }
}, "https://iframe.example.com");

// receiver on both sides
window.addEventListener("message", (event) => {
  if (event.origin !== "https://expected-peer.example.com") return;
  // safe to process event.data
});
```

Dostępne metody po stronie hosta, które interfejs użytkownika może wywołać:

- `host.callTool(name, arguments)` — wywołuje narzędzie serwerowe.
- `host.readResource(uri)` — odczytuje zasób MCP.
- `host.getPrompt(name, arguments)` — pobiera szablon podpowiedzi.
- `host.close()` — zamyka interfejs użytkownika.

Każde połączenie nadal przechodzi przez protokół MCP i dziedziczy uprawnienia serwera.

### Uprawnienia

Lista `_meta.ui.permissions` wymaga dodatkowych możliwości:

- `camera` — dostęp do kamery użytkownika (używanej w interfejsach użytkownika do skanowania dokumentów).
- `microphone` — wprowadzanie głosowe.
- `geolocation` — lokalizacja.
- `network:*` — szerszy dostęp do sieci niż pozwala na to sam `connectSrc`.

Każde uprawnienie to monit wyświetlany użytkownikowi przed wyrenderowaniem interfejsu użytkownika.

### Zagrożenia bezpieczeństwa

HTML w elemencie iframe to nadal HTML. Nowa powierzchnia ataku:

- **Wstrzykiwanie podpowiedzi przez interfejs użytkownika.** Interfejs użytkownika złośliwego serwera może wyświetlać tekst przypominający wiadomość systemową i oszukać użytkownika. Renderowanie hosta powinno wyraźnie odróżniać interfejs serwera od interfejsu hosta.
- ** Eksfiltracja przez `connectSrc`.** Jeśli CSP zezwala na `connect-src: *`, interfejs użytkownika może wysyłać dane w dowolne miejsce. Wartość domyślna powinna być rygorystyczna.
- **Clickjacking.** Interfejs użytkownika nakłada się na Chrome hosta. Hosty muszą zapobiegać manipulacji indeksem Z i egzekwować zasady nieprzezroczystości.
- **Ukradnij fokus.** Interfejs użytkownika przejmuje fokus klawiatury i przechwytuje następną wiadomość. Gospodarze muszą przechwytywać.

Faza 13 · 15 omawia je szczegółowo w ramach bezpieczeństwa MCP; ta lekcja je przedstawia.

### `ui/initialize` uścisk dłoni

Po załadowaniu ramki iframe wysyła ona `ui/initialize` poprzez postMessage:

```json
{"jsonrpc": "2.0", "id": 0, "method": "ui/initialize",
 "params": {"theme": "dark", "locale": "en-US", "sessionId": "..."}}
```

Host odpowiada możliwościami i tokenem sesji. Interfejs użytkownika używa tokena sesji przy każdym kolejnym wywołaniu hosta.

### Elementy podstawowe AppRenderer/AppFrame SDK

Zestaw SDK ext-apps udostępnia dwa podstawowe udogodnienia:

- `AppRenderer` (po stronie serwera) — otacza komponent React / Vue / Solid i emituje zasób `ui://` z właściwym MIME i metadanymi.
- `AppFrame` (po stronie klienta) — odbiera zasób, montuje ramkę iframe i pośredniczy w postMessage.

Możesz ich użyć lub ręcznie rzucić kod HTML i JSON-RPC.

### Stan ekosystemu

Aplikacje MCP zostały wysłane 26 stycznia 2026 r. Obsługa klienta od kwietnia 2026 r.:

- **Claude Desktop.** Pełne wsparcie od stycznia 2026 r.
- **ChatGPT.** Pełna obsługa za pośrednictwem pakietu Apps SDK (ten sam podstawowy protokół MCP Apps).
- **Kursor.** Beta; włączyć w ustawieniach.
- **VS Code.** Tylko kompilacje Insider.
- **Gęś.** Pełne wsparcie.
- **Zed, Windsurf.** Plan działania.

Serwery w produkcji: dashboardy, wizualizacje map, tabele danych, narzędzia do tworzenia wykresów, podglądy sandbox IDE.

## Użyj tego

`code/main.py` rozszerza serwer notatek o narzędzie `visualize_timeline`, które zwraca zasób `ui://notes/timeline` oraz moduł obsługi `resources/read` na tym URI, który zwraca mały, ale kompletny pakiet HTML z plikiem SVG oś czasu. Kod HTML jest oparty na szablonie stdlib — bez systemu kompilacji. postMessage jest szkicowany w komentarzach JS, ponieważ stdlib nie może sterować przeglądarką.

Na co zwrócić uwagę:

- `_meta.ui` w odpowiedzi narzędzia przenosi ResourceUri, CSP i uprawnienia.
- HTML renderuje bez dostępu do sieci; wszystkie dane są wstawiane.
- JS wywołuje `host.callTool` poprzez `window.parent.postMessage` (udokumentowane, ale obojętne w tym demo stdlib).

## Wyślij to

Ta lekcja przedstawia `outputs/skill-mcp-apps-spec.md`. Mając narzędzie, które korzystałoby z interaktywnego interfejsu użytkownika, umiejętność tworzy pełny kontrakt dotyczący aplikacji MCP: `ui://` URI, CSP, uprawnienia, punkty wejścia postMessage i listę kontrolną zabezpieczeń.

## Ćwiczenia

1. Uruchom `code/main.py` i sprawdź wyemitowany kod HTML. Otwórz kod HTML bezpośrednio w przeglądarce; sprawdź rendery SVG. Następnie naszkicuj kontrakt postMessage, którego interfejs użytkownika użyłby do wywołania `host.callTool("notes_update", ...)`.

2. Udoskonal CSP: usuń `'unsafe-inline'` i użyj polityki skryptów nieopartych na danych. Jakie zmiany w kodzie generowania HTML?

3. Dodaj drugi zasób interfejsu użytkownika `ui://notes/editor` z formularzem do edycji notatki na miejscu. Kiedy użytkownik przesyła dane, element iframe wywołuje `host.callTool("notes_update", ...)`.

4. Sprawdź powierzchnię ataku interfejsu użytkownika. Gdzie złośliwy serwer może wstrzyknąć treść? Przed czym chroni piaskownica iframe, a czego nie?

5. Przeczytaj specyfikację SEP-1724 i zidentyfikuj jedną funkcję w pakiecie SDK aplikacji MCP, której nie wykorzystuje ta implementacja zabawki. (Wskazówka: synchronizacja stanu na poziomie komponentu.)

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Aplikacje MCP | „Interaktywne zasoby interfejsu użytkownika” | Rozszerzenie SEP-1724 wysłane 26.01.2026 |
| `ui://` | „Schemat URI aplikacji” | Schemat zasobów dla pakietów interfejsu użytkownika |
| `text/html;profile=mcp-app` | „MIME” | Typ zawartości dla aplikacji MCP HTML |
| Piaskownica iframe | „Kontener renderowania” | Sandboxing przeglądarki interfejsu użytkownika z CSP i uprawnieniami |
| postMessage JSON-RPC | „Przewód interfejsu użytkownika do hosta” | Mały dialekt JSON-RPC-over-postMessage dla połączeń hosta |
| `_meta.ui` | „Powiązanie narzędzia z interfejsem użytkownika” | Metadane łączące wynik narzędzia z zasobem interfejsu użytkownika |
| CSP | „Polityka bezpieczeństwa treści” | Deklaruje dozwolone źródła skryptów, sieci, stylów |
| Aplikacja renderująca | „Podstawowy zestaw SDK serwera” | Konwertuje komponent frameworka na zasób `ui://` |
| Ramka aplikacji | „Podstawowy pakiet SDK klienta” | Pomocnik montowania ramki iframe, który pośredniczy w postMessage |
| `ui/initialize` | „Uścisk dłoni” | Pierwszy postWiadomość z interfejsu użytkownika do hosta |

## Dalsze czytanie

- [MCP ext-apps — GitHub](https://github.com/modelcontextprotocol/ext-apps) — implementacja referencyjna i SDK
- [Specyfikacja aplikacji MCP 26.01.2026](https://github.com/modelcontextprotocol/ext-apps/blob/main/specification/2026-01-26/apps.mdx) — formalny dokument specyfikacji
- [MCP — przegląd rozszerzeń aplikacji](https://modelcontextprotocol.io/extensions/apps/overview) — dokumentacja wysokiego poziomu
– [Blog MCP — uruchomienie aplikacji MCP](https://blog.modelcontextprotocol.io/posts/2026-01-26-mcp-apps/) — post dotyczący premiery w styczniu 2026 r.
— [Informacje o interfejsie API aplikacji MCP](https://apps.extensions.modelcontextprotocol.io/api/) — Informacje o pakiecie SDK w stylu JSDoc