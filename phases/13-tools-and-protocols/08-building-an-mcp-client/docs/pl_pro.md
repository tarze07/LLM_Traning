# Budowa klienta MCP — wykrywanie, wywoływanie, zarządzanie sesją

> Większość materiałów poświęconych MCP skupia się na tworzeniu serwerów, traktując kwestię klienta po macoszemu. Tymczasem to po stronie klienta leży cała złożoność orkiestracji: zarządzanie procesami, negocjowanie możliwości (capabilities), scalanie list narzędzi z wielu serwerów, obsługa próbkowania (sampling), ponowne nawiązywanie połączeń oraz rozwiązywanie konfliktów nazw. W tej lekcji zbudujemy klienta wieloserwerowego, który integruje trzy różne serwery MCP w jedną, spłaszczoną przestrzeń nazw narzędzi dostępną dla modelu.

**Typ:** Kompilacja
**Języki:** Python (biblioteka standardowa, wieloserwerowy klient MCP)
**Wymagania wstępne:** Faza 13 · 07 (Budowa serwera MCP)
**Czas:** ~75 minut

## Cele nauczania

- Uruchom serwer MCP jako proces potomny, przeprowadź procedurę `initialize` i prześlij powiadomienie `notifications/initialized`.
- Zarządzaj stanem sesji poszczególnych serwerów (ich możliwościami, listami narzędzi oraz identyfikatorami komunikatów).
- Scal listy narzędzi z wielu serwerów w jedną spójną przestrzeń nazw, poprawnie rozwiązując konflikty nazw (kolizje).
- Przekieruj żądanie wywołania narzędzia do odpowiedniego serwera i zwróć jego odpowiedź.

## Problem

Rzeczywisty host dla agentów AI (np. Claude Desktop, Cursor, Goose, czy Gemini CLI) ładuje wiele serwerów MCP jednocześnie. Użytkownik może w tym samym czasie korzystać z serwera systemu plików, serwera bazy danych Postgres oraz serwera GitHub. Do zadań klienta należy:

1. Uruchomienie (spawnowanie) procesów poszczególnych serwerów.
2. Przeprowadzenie procesu inicjalizacji (handshake) z każdym z nich osobno.
3. Pobranie list narzędzi za pomocą `tools/list` i scalenie ich w jedną wspólną listę.
4. Gdy model wygeneruje wywołanie (np. `notes_search`), odszukanie go na wspólnej liście i przekierowanie żądania do właściwego serwera.
5. Obsługa powiadomień asynchronicznych z serwerów (np. `tools/list_changed`) w sposób nieblokujący.
6. Automatyczne ponowne nawiązywanie połączenia w przypadku awarii warstwy transportowej.

Ręczne zaimplementowanie tych mechanizmów decyduje o tym, czy aplikacja jest stabilnym rozwiązaniem produkcyjnym, czy jedynie prostą zabawką. Oficjalne biblioteki SDK automatyzują te zadania, jednak pełne zrozumienie modelu mentalnego leży po Twojej stronie.

## Koncepcja

### Uruchamianie procesów potomnych

Uruchomienie procesu realizowane jest przez `subprocess.Popen` z parametrami `stdin=PIPE, stdout=PIPE, stderr=PIPE`. Należy ustawić `bufsize=1` oraz włączyć tryb tekstowy do odczytu danych linia po linii. Każdy serwer działa w osobnym procesie; klient przechowuje referencje do obiektów `Popen` dla każdego serwera.

### Stan sesji serwera

Obiekt reprezentujący sesję serwera (`Session`) przechowuje:

- `process` — referencję do procesu potomnego (Popen).
- `capabilities` — możliwości zadeklarowane przez serwer w odpowiedzi na `initialize`.
- `tools` — aktualną listę narzędzi pobraną z `tools/list`.
- `pending` — mapę identyfikatorów oczekujących żądań powiązanych z obiektami Future czekającymi na odpowiedź.

Komunikacja jest z natury asynchroniczna. Wywołanie `tools/call` wysłane do serwera A w momencie, gdy serwer B przetwarza inne zapytanie, nie może blokować działania aplikacji. Wymaga to zastosowania wątków z kolejkami lub biblioteki `asyncio`.

### Wspólna przestrzeń nazw

Przy scalaniu list narzędzi z różnych serwerów w jedną listę może dojść do konfliktów nazw (np. dwa różne serwery udostępniają narzędzie o nazwie `search`). Klient może rozwiązać ten problem na trzy sposoby:

1. **Dodanie prefiksów z nazwą serwera.** Narzędzia będą widoczne jako `notes/search` oraz `files/search`. Rozwiązanie jednoznaczne, ale mało czytelne dla modelu.
2. **Nadpisywanie (kto pierwszy, ten lepszy).** Kolejne narzędzie o tej samej nazwie zastępuje poprzednie. Rozwiązanie ryzykowne, ponieważ ukrywa konflikty.
3. **Odrzucanie kolizji (rejection).** Odmowa załadowania serwera powodującego konflikt i poinformowanie użytkownika. Najbezpieczniejsza metoda dla aplikacji wymagających wysokiego poziomu bezpieczeństwa.

Claude Desktop oraz VS Code MCP stosują dodawanie prefiksów z nazwą serwera. Cursor odrzuca serwer powodujący kolizję i zwraca jawny błąd.

### Routing żądań

Po poprawnym załadowaniu serwerów klient tworzy wewnętrzną tabelę routingu: `tool_name -> session`. Gdy model decyduje o wywołaniu narzędzia po nazwie, klient odszukuje powiązaną sesję, zapisuje żądanie `tools/call` na standardowe wejście (stdin) odpowiedniego procesu serwera i oczekuje na odpowiedź.

### Próbkowanie (Sampling Callbacks)

Jeśli serwer zadeklarował obsługę próbkowania (`sampling`), może wysłać żądanie `sampling/createMessage` do klienta. Klient powinien wtedy:

1. Zablokować dalsze wysyłanie żądań do tego serwera (jeśli transport nie obsługuje pełnej asynchroniczności) do momentu zakończenia próbkowania.
2. Wywołać lokalny model językowy (LLM).
3. Przekazać wygenerowaną odpowiedź z powrotem do serwera.

Lekcja 11 szczegółowo opisuje cały proces próbkowania. Tutaj traktujemy go jako część interfejsu klienta.

### Obsługa powiadomień

Odebranie powiadomienia `notifications/tools/list_changed` oznacza konieczność ponownego odpytania serwera za pomocą `tools/list`. Powiadomienie `notifications/resources/updated` sygnalizuje konieczność odświeżenia zasobu. Powiadomienia nie mogą zwracać odpowiedzi – nie należy na nie odpowiadać.

Częsty błąd: zablokowanie pętli odczytu głównego wątku na oczekiwaniu na wynik `tools/call` w momencie, gdy serwer wysyła powiadomienie. Warto uruchomić wątek czytnika w tle, który zapisuje wszystkie przychodzące linie do kolejki, z której główny wątek pobiera i przetwarza komunikaty.

### Ponowne nawiązywanie połączenia (Reconnection)

Proces serwera może ulec awarii z wielu przyczyn (błąd kodu, zabicie procesu przez system operacyjny, przerwany potok stdio). Klient wykrywa to poprzez odebranie EOF na strumieniu stdout. Dostępne strategie:

- Cichy restart procesu i ponowna inicjalizacja. Dobrze sprawdza się dla serwerów przeznaczonych wyłącznie do odczytu (stateless).
- Wyświetlenie błędu użytkownikowi. Lepsze rozwiązanie dla serwerów przechowujących stan sesji.

Faza 13 · 09 szczegółowo opisuje ponowne nawiązywanie połączenia przy transporcie HTTP Stream; dla stdio proces ten jest znacznie prostszy.

### Czas życia i identyfikatory sesji

Transporty oparte na HTTP używają nagłówka `Mcp-Session-Id` do identyfikacji sesji. Transport stdio nie potrzebuje identyfikatorów sesji – sesją jest po prostu sam proces potomny. Pakiety podtrzymujące połączenie (pingi) są opcjonalne; potoki stdio nie ulegają przerwaniu z powodu braku aktywności.

## Instrukcja użycia

Plik `code/main.py` uruchamia trzy symulowane procesy serwerów MCP, przeprowadza inicjalizację z każdym z nich, scala ich narzędzia i kieruje zapytania do odpowiednich procesów. Symulowane serwery to niezależne skrypty Pythona zwracające zdefiniowane testowe odpowiedzi (brak integracji z rzeczywistym LLM). Uruchom kod, aby zaobserwować:

- Trzy niezależne procesy inicjalizacji z wymianą możliwości.
- Połączenie list narzędzi z trzech serwerów w jeden wykaz zawierający 7 narzędzi.
- Prawidłowe przekazywanie zapytań na podstawie nazwy wywoływanego narzędzia.
- Zapobieganie konfliktom nazw poprzez automatyczne dodawanie prefiksów.

Na co warto zwrócić uwagę:

- Klasa `Session` w czytelny sposób przechowuje stan poszczególnych podprocesów.
- Wątek czytnika w tle przetwarza strumień wyjściowy procesów bez blokowania głównego wątku aplikacji.
- Tabela routingu to prosty słownik `dict[str, Session]`.
- Obsługa kolizji nazw jest jawna: jeśli kolejna usługa deklaruje istniejącą już nazwę narzędzia, zostaje ona uzupełniona o prefiks z nazwą serwera.

## Wynik wdrożenia

W ramach tej lekcji powstaje plik `outputs/skill-mcp-client-harness.md`. Narzędzie to, na podstawie deklaratywnej listy serwerów MCP (nazwy, komendy uruchomieniowe, parametry), generuje kod klienta zarządzającego ich czasem życia, scalającego narzędzia i realizującego routing z obsługą konfliktów nazw.

## Ćwiczenia

1. Uruchom `code/main.py` i przeanalizuj logi uruchamiania serwerów. Ręcznie zakończ jeden z procesów serwera (np. wysyłając sygnał SIGTERM) i zaobserwuj, jak klient wykrywa EOF i oznacza sesję jako zakończoną.

2. Zaimplementuj strategię dodawania prefiksów. Jeśli dwa serwery deklarują narzędzie o nazwie `search`, zmień nazwę drugiego na `<server_name>/search`. Zaktualizuj tabelę routingu i przetestuj poprawne przekazywanie wywołań.

3. Zaimplementuj mechanizm ponownego uruchamiania serwera z wykładniczym czasem oczekiwania (exponential backoff) przy kolejnych awariach (maksymalnie do 30 sekund) oraz wysyłaniem powiadomienia do użytkownika po trzech nieudanych próbach restartu.

4. Zaprojektuj architekturę klienta obsługującego 100 równoległych serwerów MCP. Jaka struktura danych powinna zastąpić prostą tabelę routingu? (Wskazówka: rozważ grupowanie według przestrzeni nazw oraz monitorowanie obciążenia poszczególnych procesów).

5. Przepisz kod klienta z użyciem oficjalnego pakietu SDK MCP dla Pythona. SDK udostępnia klasy `stdio_client` oraz `ClientSession`. Twój kod powinien skrócić się z około 200 linii do około 40, zachowując funkcjonalność routingu wieloserwerowego.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Klient MCP | „Host agenta” | Proces zarządzający uruchamianiem serwerów i przekazywaniem wywołań |
| Sesja | „Stan serwera” | Zbiór informacji o możliwościach serwera, liście narzędzi i oczekujących żądaniach |
| Wspólna przestrzeń nazw | „Wspólna lista narzędzi” | Zagregowana lista narzędzi ze wszystkich aktywnych serwerów |
| Kolizja nazw | „Konflikt narzędzi” | Sytuacja, w której dwa serwery udostępniają narzędzie o identycznej nazwie |
| Routing | „Przekazywanie wywołań” | Mechanizm kierujący wywołanie narzędzia do właściwego serwera na podstawie nazwy |
| Czytnik w tle | „Nieblokujący odczyt” | Wątek przetwarzający strumień wyjściowy serwera do kolejki w tle |
| Próbkowanie (Sampling) | „Wywołanie LLM przez serwer” | Obsługa żądania `sampling/createMessage` wysłanego z serwera do klienta |
| Powiadomienie o zmianie | `notifications/*_changed` | Sygnał informujący klienta o konieczności odświeżenia zasobów lub listy narzędzi |
| Polityka ponownego połączenia | „Obsługa awarii serwera” | Zestaw reguł określających zachowanie systemu po przerwaniu połączenia z serwerem |
| Sesja stdio | „Proces to sesja” | Komunikacja stdio, w której czas życia procesu potomnego definiuje czas trwania sesji |

## Dalsze czytanie

- [Model Context Protocol — Client Specification](https://modelcontextprotocol.io/specification/2025-11-25/client) — oficjalne wymagania techniczne dla implementacji klienta.
- [MCP — Client Quickstart Guide](https://modelcontextprotocol.io/quickstart/client) — tworzenie prostego klienta w Pythonie z użyciem SDK.
- [MCP Python SDK — Client Module](https://github.com/modelcontextprotocol/python-sdk) — dokumentacja klas `ClientSession` oraz `stdio_client`.
- [MCP TypeScript SDK — Client](https://github.com/modelcontextprotocol/typescript-sdk) — oficjalne SDK dla Node.js/TypeScript.
- [VS Code — MCP in Extension Guides](https://code.visualstudio.com/api/extension-guides/ai/mcp) — architektura multipleksowania wielu serwerów MCP w środowisku VS Code.
