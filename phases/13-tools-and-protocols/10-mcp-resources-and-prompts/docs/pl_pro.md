# Zasoby i podpowiedzi MCP — ekspozycja kontekstowa wykraczająca poza narzędzia

> Choć to narzędzia (tools) przyciągają 90% uwagi twórców systemów MCP, pozostałe dwa komponenty serwerowe rozwiązują bardzo ważne problemy architektoniczne. Zasoby (resources) udostępniają dane przeznaczone do odczytu, natomiast szablony promptów (prompts) dostarczają szablony instrukcji wielokrotnego użytku wywoływane w interfejsie jako komendy z ukośnikiem (slash commands). Zamiast obudowywać zwykły odczyt danych w definicjach narzędzi lub kodować przepływy pracy na stałe po stronie klienta, należy odpowiednio stosować zasoby oraz prompty. W tej lekcji omówimy kryteria podziału funkcjonalności oraz strukturę komunikatów z przestrzeni `resources/*` i `prompts/*`.

**Typ:** Kompilacja
**Języki:** Python (biblioteka standardowa, obsługa zasobów i promptów)
**Wymagania wstępne:** Faza 13 · 07 (Budowa serwera MCP)
**Czas:** ~45 minut

## Cele nauczania

- Przeprowadź poprawny podział funkcjonalności danej domeny biznesowej na narzędzia, zasoby lub szablony promptów.
- Zaimplementuj obsługę metod `resources/list`, `resources/read`, `resources/subscribe` oraz powiadomień `notifications/resources/updated`.
- Zaimplementuj metody `prompts/list` oraz `prompts/get` obsługujące szablony z parametrami.
- Zidentyfikuj sposoby prezentacji promptów w interfejsie klienta (np. jako slash commands lub automatycznie dołączany kontekst).

## Problem

Prosty, intuicyjnie napisany serwer MCP dla aplikacji notatek często udostępnia wszystkie funkcje jako narzędzia (np. `notes_read`, `notes_list`, `notes_search`). W takim scenariuszu każdy dostęp do danych wymaga od modelu wywołania narzędzia. Niesie to ze sobą poważne konsekwencje:

- Model musi samodzielnie decydować, czy wywołać `notes_read` przy każdym zapytaniu, które mogłoby skorzystać z dodatkowego kontekstu.
- Dane przeznaczone wyłącznie do odczytu nie mogą być subskrybowane ani wyświetlane w panelu bocznym klienta.
- Interfejsy klienckie (np. załączniki w Claude Desktop czy panel „Dołącz plik” w Cursorze) nie mają możliwości bezpośredniego pobrania i prezentacji listy danych.

Prawidłowa architektura wymaga podziału: udostępniaj dane jako zasoby (resources), akcje modyfikujące stan lub wymagające obliczeń jako narzędzia (tools), a powtarzalne, wieloetapowe instrukcje jako szablony promptów (prompts). Każdy z tych komponentów oferuje inne możliwości w interfejsie użytkownika (UX) i inny schemat dostępu.

## Koncepcja

### Narzędzia vs Zasoby vs Szablony promptów — kryteria wyboru

| Funkcjonalność | Komponent |
|------------|-----------|
| Użytkownik chce wyszukać, przefiltrować lub przekształcić dane | Narzędzie (Tool) |
| Użytkownik chce przekazać określone dane do kontekstu modelu | Zasób (Resource) |
| Użytkownik chce wywołać gotowy szablon pracy z parametrami | Szablon promptu (Prompt) |

Zasada ogólna: jeśli model powinien decydować o wywołaniu funkcji przy powiązanych zapytaniach w celu realizacji podzdań, zaimplementuj ją jako **narzędzie**. Jeśli użytkownik odniesie korzyść z ręcznego dołączenia zbioru danych do rozmowy, zaimplementuj go jako **zasób**. Jeśli użytkownik chce wielokrotnie uruchamiać gotowy, wieloetapowy szablon instrukcji, zaimplementuj go jako **szablon promptu**.

### Zasoby (Resources)

Metoda `resources/list` zwraca `{resources: [{uri, name, mimeType, description?}]}`. Z kolei `resources/read` przyjmuje parametr `{uri}` i zwraca `{contents: [{uri, mimeType, text | blob}]}`.

Identyfikatory URI mogą wskazywać na dowolne zasoby:

- `file:///Users/alice/notes/mcp.md` (lokalny plik)
- `postgres://my-db/query/SELECT ...` (wynik zapytania do bazy danych)
- `notes://note-14` (dedykowany schemat serwera notatek)
- `memory://session-2026-04-22/recent` (stan pamięci bieżącej sesji)

Tablica `contents[]` obsługuje zarówno dane tekstowe, jak i binarne. W przypadku danych binarnych przesyłany jest ciąg znaków zakodowany w formacie Base64 (pole `blob`) oraz odpowiedni `mimeType`.

### Subskrypcje zasobów

Serwer deklaruje obsługę subskrypcji w obiekcie capabilities: `{resources: {subscribe: true}}`. Klient rejestruje się na zmiany za pomocą `resources/subscribe {uri}`. W przypadku modyfikacji danych serwer wysyła powiadomienie `notifications/resources/updated {uri}`, co pozwala klientowi na automatyczne odświeżenie (ponowne pobranie) zawartości zasobu.

Typowy scenariusz: serwer monitoruje pliki na dysku; edycja pliku w zewnętrznym programie wyzwala powiadomienie, dzięki czemu Claude Desktop natychmiast aktualizuje treść załącznika w kontekście czatu.

### Szablony zasobów (Resource Templates)

Rozszerzenie z wersji specyfikacji z dnia 2025-11-25 wprowadza `resourceTemplates` – szablony adresów URI z parametrami (np. `notes://{id}`). Ułatwia to klientom dynamiczne uzupełnianie identyfikatorów bezpośrednio w interfejsie wyboru zasobów.

### Szablony promptów (Prompts)

Metoda `prompts/list` zwraca listę `{prompts: [{name, description, arguments?}]}`. Z kolei `prompts/get` przyjmuje parametr `{name, arguments}` i zwraca wyrenderowany szablon `{description, messages: [{role, content}]}`.

Prompt w MCP to gotowy schemat konwersacji (lista wiadomości) z parametrami uzupełnianymi przez klienta. Na przykład szablon `code_review` przyjmujący parametr `file_path` może zwracać zestaw trzech wiadomości: instrukcję systemową, treść pliku w wiadomości użytkownika oraz początek odpowiedzi asystenta ze schematem analizy.

### Integracja z interfejsem klienta

Claude Desktop, VS Code oraz Cursor prezentują szablony promptów jako polecenia z ukośnikiem (slash commands) bezpośrednio na czacie. Wpisanie `/code_review` wyświetla formularz do uzupełnienia parametrów. Szablony promptów stanowią pomost między potrzebami użytkownika (skrót komendy) a pełną strukturą promptu wysyłaną do modelu.

Nie wszystkie aplikacje klienckie obsługują ten komponent – weryfikacja odbywa się podczas inicjalizacji sesji. Jeśli klient nie zadeklarował obsługi promptów, szablony nie będą widoczne dla użytkownika.

### Aktualizacja listy elementów

Zarówno dla zasobów, jak i promptów serwer może wysłać powiadomienie `notifications/list_changed` (np. `notifications/resources/list_changed`), sygnalizując, że zestaw danych uległ zmianie i klient powinien odświeżyć ich listę metodą pobierania.

### Standardy typów MIME

- Dla danych tekstowych: `mimeType: "text/plain"`, `text/markdown`, `application/json`.
- Dla danych binarnych: `image/png`, `application/pdf` (wraz z polem `blob`).
- Dla interaktywnych aplikacji MCP (omówionych w lekcji 14): `text/html;profile=mcp-app` pod adresem URI z protokołem `ui://`.

### Zasoby dynamiczne

URI zasobu nie musi odpowiadać statycznej lokalizacji na dysku. Zasób `notes://recent` może przy każdym odczycie dynamicznie generować listę 5 ostatnich notatek, a `db://query/users/active` może uruchamiać zapytanie SQL.

Zasada cachowania: jeśli klient przechowuje dane w pamięci podręcznej na podstawie URI, identyfikator musi być stabilny. Jeśli dane są generowane dynamicznie, URI powinien zawierać unikalny identyfikator (np. timestamp), aby zapobiec serwowaniu nieaktualnych danych z cache.

### Subskrypcje a odpytywanie (Polling)

Klienci obsługujący subskrypcje są informowani o zmianach asynchronicznie przez serwer (`notifications/resources/updated`). Klienci bez obsługi tego mechanizmu muszą cyklicznie odpytywać serwer o aktualizacje (polling). Obie metody są poprawne.

Utrzymywanie stanu subskrypcji na serwerze wiąże się z alokacją pamięci na każdą aktywną sesję. Zestaw subskrybowanych zasobów powinien być ograniczony, a nieaktywne połączenia powinny być automatycznie zamykane po przekroczeniu limitu czasu (timeout).

### Prompty MCP a prompty systemowe

Prompty w MCP nie zastępują instrukcji systemowych (system prompts) samego klienta. Instrukcje systemowe hosta oraz szablony promptów MCP działają równolegle. Prawidłowo zaimplementowany klient nakłada instrukcje warstwowo, nie dopuszczając do nadpisania promptu systemowego przez szablon serwera.

## Instrukcja użycia

Plik `code/main.py` rozbudowuje serwer notatek z lekcji 07 o:

- Udostępnianie notatek jako zasobów (`notes://note-1` itp.) z obsługą subskrypcji (`resources/subscribe`).
- Szablon promptu `review_note` zwracający sekwencję trzech wiadomości.
- Zasymulowany proces monitorowania plików (file watcher) wysyłający powiadomienie `notifications/resources/updated` po zmianie notatki.
- Dynamiczny zasób `notes://recent` zwracający listę 5 ostatnich notatek.

Uruchom skrypt, aby przetestować działanie poszczególnych komponentów.

## Wynik wdrożenia

W ramach tej lekcji powstaje plik `outputs/skill-primitive-splitter.md`. Narzędzie to analizuje wymagania biznesowe planowanego serwera MCP i dokonuje klasyfikacji poszczególnych funkcjonalności na narzędzia, zasoby oraz szablony promptów wraz z technicznym uzasadnieniem wyboru.

## Ćwiczenia

1. Uruchom `code/main.py`. Pobierz listę zasobów, po czym zmodyfikuj treść jednej z notatek i zaobserwuj wygenerowanie powiadomienia `notifications/resources/updated` w logach.

2. Zaimplementuj wysyłanie powiadomienia `notifications/resources/list_changed` przy tworzeniu nowej notatki, aby klient mógł automatycznie zaktualizować listę zasobów.

3. Zaprojektuj zestaw trzech szablonów promptów dla serwera obsługującego integrację z GitHubem: `summarize_pr`, `triage_issue` oraz `release_notes` wraz z parametrami wejściowymi.

4. Przeanalizuj narzędzia z serwera zaimplementowanego w lekcji 07 i określ, które z nich powinny zostać przekształcone w zasoby lub szablony promptów. Przygotuj krótkie uzasadnienie dla każdego z nich.

5. Przeczytaj uważnie rozdziały specyfikacji MCP poświęcone zasobom (`server/resources`) oraz promptom (`server/prompts`). Zidentyfikuj jedno pole struktury `resources/read`, które jest rzadko używane, ale obsługiwane przez standard (Wskazówka: sprawdź pole `_meta` w zwracanej zawartości).

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Zasób (Resource) | „Udostępnione dane” | Dane tekstowe lub binarne identyfikowane przez URI, przeznaczone wyłącznie do odczytu |
| URI zasobu | „Adres zasobu” | Identyfikator ze schematem (np. `file://`, `notes://`) wskazujący na konkretne dane |
| `resources/subscribe` | „Subskrypcja” | Rejestracja klienta na powiadomienia o zmianach stanu zasobu o zadanym URI |
| Powiadomienie o zmianie | `notifications/resources/updated` | Komunikat serwera informujący o modyfikacji subskrybowanego zasobu |
| Szablon zasobu | „Dynamiczny URI” | Wzorzec adresu URI z parametrami ułatwiający dynamiczne odpytywanie |
| Szablon promptu (Prompt) | „Slash command” | Nazwany szablon sekwencji wiadomości z parametrami uzupełnianymi przed wywołaniem |
| Parametry promptu | „Argumenty” | Zdefiniowane typy danych wejściowych wymagane do wyrenderowania szablonu promptu |
| Odczyt promptu | `prompts/get` | Żądanie wyrenderowania i zwrócenia gotowej sekwencji wiadomości na podstawie parametrów |
| Blok treści | „Wpisany fragment” | Obiekt określający typ przesyłanych danych `{type: text \| image \| resource}` |
| Slash command UX | „Komenda z ukośnikiem” | Prezentacja szablonów promptów w interfejsie czatu jako poleceń zaczynających się od `/` |

## Dalsze czytanie

- [Model Context Protocol — Concepts: Resources](https://modelcontextprotocol.io/docs/concepts/resources) — szczegółowy opis zasobów, subskrypcji oraz szablonów adresów URI.
- [Model Context Protocol — Concepts: Prompts](https://modelcontextprotocol.io/docs/concepts/prompts) — dobre praktyki tworzenia szablonów promptów i ich integracji z interfejsem.
- [MCP — Server Resources Specification](https://modelcontextprotocol.io/specification/2025-11-25/server/resources) — dokumentacja techniczna komunikatów z przestrzeni `resources/*`.
- [MCP — Server Prompts Specification](https://modelcontextprotocol.io/specification/2025-11-25/server/prompts) — dokumentacja techniczna komunikatów z przestrzeni `prompts/*`.
