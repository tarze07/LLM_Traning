# Aplikacje MCP — interaktywne zasoby interfejsu użytkownika za pośrednictwem `ui://`

> Tekstowy format odpowiedzi narzędzi ogranicza możliwości prezentacji danych przez agentów. Rozwiązaniem są aplikacje MCP (MCP Apps - standard SEP-1724, oficjalnie wprowadzony 26 stycznia 2026 r.), które pozwalają narzędziom na zwracanie interaktywnego kodu HTML. Jest on uruchamiany w bezpiecznej piaskownicy (sandbox) i renderowany bezpośrednio w Claude Desktop, ChatGPT, Cursor, Goose oraz VS Code. Pozwala to na wyświetlanie pulpitów nawigacyjnych, formularzy, map czy wizualizacji 3D w ramach jednego rozszerzenia. W tej lekcji omówimy schemat zasobów `ui://`, typ MIME `text/html;profile=mcp-app`, komunikację iframe-sandbox przy użyciu protokołu postMessage oraz kwestie bezpieczeństwa związane z renderowaniem kodu HTML serwowanego przez zewnętrzne usługi.

**Typ:** Kompilacja
**Języki:** Python (biblioteka standardowa, generator zasobów interfejsu użytkownika), HTML (przykładowa aplikacja)
**Wymagania wstępne:** Faza 13 · 07 (Serwer MCP), Faza 13 · 10 (Zasoby)
**Czas:** ~75 minut

## Cele nauczania

- Zwracaj zasoby typu `ui://` w odpowiedziach na wywołanie narzędzi, określając właściwe typy MIME oraz metadane.
- Zadeklaruj powiązanie interfejsu użytkownika z narzędziem przy użyciu pól `_meta.ui.resourceUri`, `_meta.ui.csp` oraz `_meta.ui.permissions`.
- Zaimplementuj protokół komunikacji JSON-RPC oparty o postMessage w piaskownicy iframe do wymiany danych między interfejsem użytkownika a hostem.
- Wdróż rygorystyczne polityki bezpieczeństwa (CSP oraz uprawnień) chroniące hosta przed złośliwymi skryptami wstrzykiwanymi do UI.

## Problem

Narzędzie `visualize_timeline` w starszych implementacjach mogło zwrócić tekst w formacie: „Oto 14 notatek uporządkowanych chronologicznie:…”. Z perspektywy UX użytkownicy oczekują jednak interaktywnej osi czasu. Przed wprowadzeniem aplikacji MCP programiści musieli korzystać z zamkniętych rozwiązań dedykowanych pod konkretnego klienta (np. Claude Artifacts lub niestandardowy kod HTML w GPT OpenAI) lub całkowicie rezygnować z interfejsu graficznego.

Aplikacje MCP (zdefiniowane w SEP-1724 z 26 stycznia 2026 r.) ujednolicają ten mechanizm. Wynik działania narzędzia może zawierać zasób (`resource`) o adresie URI zaczynającym się od `ui://` i typie MIME `text/html;profile=mcp-app`. Aplikacja kliencka (host) renderuje go wewnątrz piaskownicy `<iframe>` z rygorystyczną polityką CSP i zablokowanym dostępem do sieci (chyba że dostęp zostanie jawnie przyznany). Interfejs użytkownika w ramce iframe komunikuje się z hostem przy użyciu uproszczonej wersji protokołu JSON-RPC przesyłanej przez `postMessage`.

Wszystkie kompatybilne aplikacje klienckie (Claude Desktop, ChatGPT, Goose, VS Code) renderują ten sam zasób `ui://` w identyczny sposób. Jeden serwer, jeden pakiet HTML, uniwersalny interfejs użytkownika.

## Koncepcja

### Schemat adresowania URI `ui://`

Narzędzie zwraca dane w formacie:

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

Następnie host wywołuje metodę `resources/read` na ścieżce `ui://notes/timeline`, na co serwer odpowiada:

```json
{
  "contents": [{
    "uri": "ui://notes/timeline",
    "mimeType": "text/html;profile=mcp-app",
    "text": "<!doctype html>..."
  }]
}
```

### Izolacja ramki (iframe sandbox)

Host ładuje otrzymany kod HTML do elementu `<iframe>` z włączoną piaskownicą:

- Parametr `sandbox="allow-scripts allow-same-origin"` (lub bardziej rygorystyczny, w zależności od wymagań serwera).
- Zadeklarowane przez serwer reguły Content Security Policy (CSP) są przekazywane i wymuszane w nagłówkach odpowiedzi.
- Wyłączona jest obsługa plików cookie oraz dostęp do pamięci lokalnej (local storage) domeny hosta.
- Dostęp do sieci jest ściśle ograniczony do reguł zdefiniowanych w `connectSrc` w obiekcie CSP.

### Protokół komunikacji postMessage

Struktura iframe komunikuje się z hostem asynchronicznie przez `window.postMessage`, przesyłając komunikaty w formacie JSON-RPC 2.0.

Bezpieczeństwo transmisji: Zawsze definiuj jawny parametr `targetOrigin` wskazujący na domenę partnera komunikacji. Po stronie odbiorcy bezwzględnie weryfikuj nagłówek `event.origin` pod kątem zgodności z listą dozwolonych przed przetworzeniem danych. Unikaj stosowania maski `"*"` po obu stronach – kanał ten służy do przesyłania wywołań narzędzi i odczytu wrażliwych zasobów.

```js
// iframe -> host  (transmisja do domeny hosta)
window.parent.postMessage({
  jsonrpc: "2.0",
  id: 1,
  method: "host.callTool",
  params: { name: "notes_update", arguments: { id: "note-14", title: "..." } }
}, "https://host.example.com");

// host -> iframe  (transmisja do domeny iframe)
iframe.contentWindow.postMessage({
  jsonrpc: "2.0",
  id: 1,
  result: { content: [...] }
}, "https://iframe.example.com");

// Walidacja po obu stronach odbiorcy
window.addEventListener("message", (event) => {
  if (event.origin !== "https://expected-peer.example.com") return;
  // Bezpieczne przetwarzanie event.data
});
```

Dostępne metody API hosta, które interfejs użytkownika w ramce iframe może wywołać:

- `host.callTool(name, arguments)` — wywołanie dowolnego narzędzia na serwerze.
- `host.readResource(uri)` — odczytanie zasobu MCP.
- `host.getPrompt(name, arguments)` — pobranie szablonu promptu.
- `host.close()` — żądanie zamknięcia interfejsu graficznego.

Wszystkie wywołania są weryfikowane przez protokół MCP i dziedziczą uprawnienia powiązane z sesją serwera.

### Uprawnienia (Permissions)

Tabela `_meta.ui.permissions` pozwala na zażądanie dostępu do dodatkowych funkcji sprzętowych i systemowych urządzenia:

- `camera` — dostęp do kamery użytkownika (np. do skanowania dokumentów).
- `microphone` — nagrywanie dźwięku (wprowadzanie głosowe).
- `geolocation` — odczyt lokalizacji urządzenia.
- `network:*` — rozszerzony dostęp do sieci wykraczający poza reguły `connectSrc`.

Każde z zadeklarowanych uprawnień wymaga wyświetlenia użytkownikowi systemowego okna potwierdzenia przed załadowaniem interfejsu graficznego.

### Zagrożenia bezpieczeństwa

Dynamiczny kod HTML uruchamiany w ramce iframe generuje nowe wektory ataków:

- **Wstrzykiwanie instrukcji do UI (UI Prompt Injection).** Złośliwy serwer może wyrenderować elementy interfejsu imitujące systemowe komunikaty hosta, wprowadzając użytkownika w błąd. Interfejsy graficzne serwera powinny być wyraźnie oddzielone wizualnie od ramki aplikacji nadrzędnej.
- **Wyciek danych (Exfiltration).** Jeśli reguły CSP dopuszczają `connect-src: *`, złośliwy kod w UI może wysyłać przechwycone dane na dowolny serwer zewnętrzny. Domyślne zasady CSP powinny być maksymalnie rygorystyczne.
- **Wyłudzanie kliknięć (Clickjacking).** Elementy UI mogą próbować nakładać się na przyciski aplikacji hosta. Hosty muszą kontrolować układ warstw (indeks z-index) oraz poziom przezroczystości elementów.
- **Przechwytywanie fokusu (Focus Hijacking).** Kod w ramce iframe może przechwytywać fokus klawiatury, przejmując znaki wpisywane przez użytkownika. Hosty muszą kontrolować zarządzanie fokusem.

Szczegółowa analiza bezpieczeństwa znajduje się w fazie 13 · 15.

### Inicjalizacja interfejsu `ui/initialize`

Po załadowaniu kodu HTML ramka iframe wysyła powiadomienie `ui/initialize`:

```json
{"jsonrpc": "2.0", "id": 0, "method": "ui/initialize",
 "params": {"theme": "dark", "locale": "en-US", "sessionId": "..."}}
```

Host odsyła zadeklarowane możliwości oraz token sesji, który musi być dołączany do każdego kolejnego żądania wysyłanego z ramki do hosta.

### Komponenty AppRenderer oraz AppFrame SDK

Oficjalna biblioteka `ext-apps` udostępnia dwa kluczowe komponenty:

- `AppRenderer` (po stronie serwera) — obudowuje komponenty pisane w bibliotekach React / Vue / Solid i generuje gotowy zasób `ui://` z odpowiednim typem MIME i metadanymi.
- `AppFrame` (po stronie klienta) — odbiera zasób, montuje ramkę iframe i pośredniczy w wymianie komunikatów postMessage.

Programista może skorzystać z tych komponentów lub samodzielnie generować kod HTML i obsługiwać pakiety JSON-RPC.

### Wsparcie w ekosystemie

Aplikacje MCP zostały oficjalnie zaprezentowane 26 stycznia 2026 roku. Status wsparcia w systemach klienckich na kwiecień 2026 r.:

- **Claude Desktop.** Pełna obsługa od stycznia 2026 roku.
- **ChatGPT.** Obsługa realizowana przez Apps SDK (zgodne z protokołem MCP Apps).
- **Cursor.** Wersja beta (wymaga włączenia w ustawieniach programu).
- **VS Code.** Dostępne w wersjach testowych (Insider builds).
- **Goose.** Pełne wsparcie produkcyjne.
- **Zed, Windsurf.** Funkcja ujęta w planach rozwoju (roadmap).

Typowe zastosowania produkcyjne: panele administracyjne, interaktywne mapy, tabele danych z filtrowaniem, wykresy oraz podglądy kodu w piaskownicach IDE.

## Instrukcja użycia

Plik `code/main.py` rozbudowuje serwer notatek o narzędzie `visualize_timeline`, które zwraca adres URI zasobu `ui://notes/timeline`, oraz o metodę obsługi `resources/read` na tym adresie, zwracającą kompletny kod HTML z wyrenderowaną osią czasu w formacie SVG. Całość bazuje na bibliotece standardowej bez systemów budowania front-endu. Kod obsługi `postMessage` został zamieszczony w komentarzach w pliku JS, ponieważ środowisko uruchomieniowe Pythona nie kontroluje okna przeglądarki.

Na co warto zwrócić uwagę:

- Sekcja `_meta.ui` w odpowiedzi narzędzia zawiera parametry ResourceUri, CSP oraz wymagane uprawnienia.
- Kod HTML renderuje się całkowicie lokalnie bez odpytywania sieci (wszystkie dane są osadzone bezpośrednio).
- Kod JS wywołuje metodę `host.callTool` za pośrednictwem `window.parent.postMessage` (zgodnie ze specyfikacją).

## Wynik wdrożenia

W ramach tej lekcji powstaje plik `outputs/skill-mcp-apps-spec.md`. Narzędzie to, dla wskazanego scenariusza wymagającego interaktywnego interfejsu graficznego, projektuje kontrakt aplikacji MCP: adresy `ui://`, polityki CSP, uprawnienia sprzętowe, punkty komunikacji postMessage oraz listę kontrolną bezpieczeństwa.

## Ćwiczenia

1. Uruchom `code/main.py` i przeanalizuj wygenerowany kod HTML. Otwórz plik HTML bezpośrednio w przeglądarce i sprawdź renderowanie obiektów SVG. Następnie przygotuj strukturę wywołania `postMessage` na potrzeby metody `host.callTool("notes_update", ...)`.

2. Zaostrz reguły CSP: wyeliminuj opcję `'unsafe-inline'` i zastosuj politykę podpisywania skryptów (nonces). Jakie modyfikacje należy wprowadzić w generatorze HTML w Pythonie?

3. Dodaj nowy zasób graficzny `ui://notes/editor` zawierający formularz do edycji notatki na miejscu. Po zatwierdzeniu formularza ramka iframe powinna wysyłać żądanie modyfikacji danych metodą `host.callTool("notes_update", ...)`.

4. Przeanalizuj zagrożenia bezpieczeństwa w warstwie UI. Wskazuj miejsca, w których złośliwy serwer mógłby spróbować wstrzyknąć kod. Przed jakimi rodzajami ataków chroni piaskownica iframe, a które pozostają otwarte?

5. Przeczytaj uważnie specyfikację standardu SEP-1724. Zidentyfikuj jedną zaawansowaną funkcję w SDK aplikacji MCP, która nie została uwzględniona w naszej uproszczonej implementacji (Wskazówka: synchronizacja stanu na poziomie poszczególnych komponentów UI).

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Aplikacje MCP (MCP Apps) | „Interaktywne UI” | Rozszerzenie SEP-1724 z dnia 26.01.2026 wprowadzające graficzne widoki HTML |
| `ui://` | „Schemat URI aplikacji” | Dedykowany protokół adresowania zasobów graficznych aplikacji MCP |
| `text/html;profile=mcp-app` | „Typ MIME aplikacji” | Typ zawartości nagłówka identyfikujący kod HTML aplikacji MCP |
| Piaskownica iframe | „Kontener UI” | Izolowane środowisko uruchomieniowe przeglądarki z nałożonymi restrykcjami CSP i uprawnień |
| postMessage JSON-RPC | „Komunikacja z hostem” | Protokół wymiany wiadomości JSON-RPC przesyłany przez mechanizm postMessage |
| `_meta.ui` | „Powiązanie z interfejsem” | Metadane odpowiedzi narzędzia określające parametry powiązanego widoku UI |
| CSP | „Polityka bezpieczeństwa treści” | Zbiór reguł określających dopuszczalne źródła skryptów, stylów i połączeń sieciowych |
| AppRenderer | „Biblioteka serwera” | Komponent SDK konwertujący kod komponentów UI na zasób `ui://` |
| AppFrame | „Biblioteka klienta” | Komponent SDK ułatwiający montowanie ramki iframe i obsługę komunikatów postMessage |
| `ui/initialize` | „Inicjalizacja UI” | Pierwszy komunikat wysyłany z ramki iframe do aplikacji hosta |

## Dalsze czytanie

- [MCP ext-apps — GitHub Repository](https://github.com/modelcontextprotocol/ext-apps) — referencyjne implementacje oraz pakiety SDK.
- [MCP Apps Specification 2026-01-26](https://github.com/modelcontextprotocol/ext-apps/blob/main/specification/2026-01-26/apps.mdx) — oficjalny dokument specyfikacji technicznej standardu.
- [MCP — Application Extensions Overview](https://modelcontextprotocol.io/extensions/apps/overview) — przegląd architektury aplikacji MCP.
- [MCP Blog — Launching MCP Apps](https://blog.modelcontextprotocol.io/posts/2026-01-26-mcp-apps/) — wpis na blogu prezentujący możliwości nowo wdrażanego standardu.
