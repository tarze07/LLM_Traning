# Transporty MCP — migracja stdio vs Streamable HTTP vs SSE

> Transport stdio sprawdza się wyłącznie w środowisku lokalnym. Z kolei standardem dla połączeń zdalnych jest wprowadzony 26.03.2025 roku protokół Streamable HTTP. Starsza metoda oparta na HTTP+SSE została uznana za przestarzałą i zostanie całkowicie wycofana z użycia w połowie 2026 roku. Wybór nieodpowiedniego protokołu warstwy transportowej wiąże się z kosztowną migracją. Zastosowanie właściwego standardu pozwala na bezproblemowe, zdalne hostowanie serwera MCP z obsługą ciągłości sesji i ochroną przed atakami typu DNS Rebinding.

**Typ:** Ucz się
**Języki:** Python (biblioteka standardowa, szkielet punktu końcowego HTTP dla Streamable HTTP)
**Wymagania wstępne:** Faza 13 · 07, 08 (Serwer i klient MCP)
**Czas:** ~45 minut

## Cele nauczania

- Dokonaj wyboru między standardowym transportem stdio a Streamable HTTP w zależności od architektury wdrożenia (lokalne vs zdalne, pojedynczy proces vs infrastruktura chmurowa).
- Zaimplementuj wzorzec pojedynczego punktu końcowego (single endpoint) w Streamable HTTP: metodę POST dla żądań oraz GET do nasłuchiwania strumienia sesji.
- Wdróż weryfikację nagłówka `Origin` oraz mechanizmy kontroli identyfikatora sesji w celu zabezpieczenia serwera przed atakami DNS Rebinding.
- Przeprowadź migrację starszych serwerów korzystających z HTTP+SSE do Streamable HTTP przed ostatecznym wycofaniem wsparcia w połowie 2026 roku.

## Problem

Pierwszą metodą zdalnego transportu w MCP (stosowaną na przełomie 2024 i 2025 roku) był protokół HTTP+SSE. Wymagał on posiadania dwóch punktów końcowych (endpoints): jednego do odbierania żądań POST od klienta oraz drugiego (SSE – Server-Sent Events) do przesyłania odpowiedzi i powiadomień z serwera do klienta. Rozwiązanie to działało, ale było mało optymalne: wymagało otwierania dwóch połączeń dla jednej sesji, powodowało problemy z buforowaniem na niektórych serwerach CDN oraz było podatne na agresywne zamykanie długotrwałych połączeń SSE przez zapory sieciowe (WAF).

Specyfikacja z dnia 26.03.2025 roku zastąpiła ten model standardem Streamable HTTP. W nowym podejściu wykorzystuje się pojedynczy punkt końcowy: metodę POST dla żądań klienta oraz GET do nawiązania strumieniowego połączenia sesyjnego, a oba zapytania współdzielą nagłówek `Mcp-Session-Id`. Wszystkie nowoczesne serwery budowane są w oparciu o Streamable HTTP. Starsza metoda HTTP+SSE jest wycofywana – wsparcie dla niej wyłączył Atlassian Rovo (30 czerwca 2026 r.), Keboola (1 kwietnia 2026 r.), a większość systemów korporacyjnych wycofa ją do końca 2026 roku.

Jednocześnie transport stdio pozostaje standardem dla serwerów uruchamianych lokalnie. Claude Desktop, VS Code oraz inne narzędzia typu IDE domyślnie korzystają ze stdio. Złota zasada: stdio dla procesów lokalnych na tej samej maszynie, Streamable HTTP dla komunikacji sieciowej. Nie należy ich mieszać.

## Koncepcja

### Transport stdio

- Działa w modelu procesu potomnego (child process). Klient uruchamia proces serwera i komunikuje się z nim za pośrednictwem standardowego wejścia/wyjścia (stdin/stdout).
- Komunikaty przekazywane są jako pojedyncze obiekty JSON w jednej linii (JSON Lines), rozdzielone znakiem nowej linii.
- Sesja nie posiada identyfikatora – sesją jest po prostu sam uruchomiony proces potomny.
- Nie wymaga dodatkowych mechanizmów uwierzytelniania (proces dziedziczy poziom uprawnień od aplikacji nadrzędnej).
- Nigdy nie należy używać stdio do łączenia się z serwerami zdalnymi (tunelowanie przez SSH lub socat wprowadza zbędną złożoność – w takich przypadkach należy zastosować Streamable HTTP).

### Strumieniowy protokół HTTP (Streamable HTTP)

Wykorzystuje pojedynczy punkt końcowy (np. `/mcp`) i obsługuje trzy metody HTTP:

- **POST `/mcp`:** Służy do przesyłania zapytań JSON-RPC przez klienta. Serwer odpowiada pojedynczym obiektem JSON lub otwiera strumień SSE zawierający odpowiedzi (przydatne przy przetwarzaniu wsadowym lub powiadomieniach powiązanych z zapytaniem).
- **GET `/mcp`:** Klient nawiązuje długotrwałe połączenie strumieniowe SSE. Serwer wykorzystuje ten kanał do inicjowania zapytań do klienta (np. próbkowanie/sampling, powiadomienia, formularze wywoływania).
- **DELETE `/mcp`:** Klient jawnie zamyka i niszczy sesję.

Sesje są identyfikowane przez nagłówek `Mcp-Session-Id`, który serwer generuje przy pierwszej odpowiedzi, a klient dołącza do każdego kolejnego zapytania. Identyfikatory sesji muszą być generowane przy użyciu silnych kryptograficznie generatorów liczb losowych (minimum 128 bitów); identyfikatory proponowane przez klienta powinny być odrzucane ze względów bezpieczeństwa.

### Jeden czy dwa punkty końcowe?

Obsługa dwóch punktów końcowych z wcześniejszych specyfikacji wciąż jest wspierana w celach kompatybilności wstecznej (backward compatibility). Niemniej jednak wszystkie nowo tworzone serwery powinny implementować wzorzec pojedynczego punktu końcowego. Oficjalne biblioteki SDK domyślnie korzystają z jednego adresu URL – starsze rozwiązania stosuj wyłącznie przy komunikacji z niezaktualizowanymi klientami.

### Weryfikacja nagłówka `Origin` i ochrona przed DNS Rebinding

Chociaż przeglądarki internetowe nie są bezpośrednimi klientami MCP, napastnik może przygotować złośliwą stronę WWW, która wymusi na przeglądarce wysłanie żądania POST pod adres `localhost:1234/mcp` (gdzie może nasłuchiwać lokalny serwer MCP użytkownika). Jeśli serwer nie weryfikuje nagłówka `Origin`, standardowa polityka CORS w przeglądarce nie zablokuje zapytania, ponieważ nagłówek `Origin: http://evil.com` jest poprawnie przekazywany przy zapytaniach międzydomenowych.

Specyfikacja z dnia 25.11.2025 roku nakłada na serwery obowiązek odrzucania żądań, w których nagłówek `Origin` nie pasuje do zdefiniowanej listy dozwolonych (whitelist). Na liście tej powinny znaleźć się domeny klientów MCP (np. `https://claude.ai`, `vscode-webview://*`) oraz adresy lokalne dla lokalnych interfejsów użytkownika.

### Zarządzanie czasem życia sesji

1. Klient wysyła pierwsze zapytanie bez nagłówka `Mcp-Session-Id`.
2. Serwer generuje bezpieczny, losowy identyfikator sesji i odsyła go w nagłówku odpowiedzi.
3. Klient dołącza ten nagłówek do każdego kolejnego żądania POST oraz zapytania GET otwierającego strumień.
4. Serwer może w każdej chwili zamknąć sesję; przy kolejnym żądaniu klient otrzyma kod błędu HTTP 404 i będzie musiał przeprowadzić inicjalizację od nowa.
5. Klient może wysłać żądanie DELETE w celu bezpiecznego zakończenia sesji.

### Podtrzymywanie połączenia i wznawianie sesji

Połączenia SSE mogą ulegać przerwaniu. Klient nawiązuje połączenie ponownie, wysyłając żądanie GET z zachowanym identyfikatorem `Mcp-Session-Id`. Serwer powinien buforować komunikaty, które nie zostały dostarczone w czasie niedostępności klienta (przez określony czas TTL), i przesłać je po wznowieniu połączenia. Do synchronizacji strumienia służy nagłówek `last-event-id` przekazywany przez klienta.

Faza 13 · 13 omawia mechanizmy asynchronicznych zadań (Tasks), które pozwalają na kontynuowanie długotrwałych obliczeń nawet w przypadku przejściowych problemów z siecią.

### Obsługa kompatybilności wstecznej (Fallback)

Klient chcący poprawnie obsługiwać zarówno nowe, jak i starsze serwery powinien postępować według schematu:

1. Wyślij zapytanie POST na adres `/mcp`.
2. Jeśli serwer odpowie kodem `200 OK` z nagłówkiem JSON lub otworzy strumień SSE, oznacza to obsługę standardu Streamable HTTP.
3. Jeśli odpowiedź to `200 OK` z nagłówkiem `Content-Type: text/event-stream` oraz nagłówkiem `Location` wskazującym inny adres URL, serwer korzysta ze starszej wersji HTTP+SSE – należy kontynuować komunikację pod adresem wskazanym w `Location`.

### Infrastruktura i hosting serwerów zdalnych

Zdalne serwery MCP w środowiskach produkcyjnych są najczęściej uruchamiane w chmurze (np. Cloudflare Workers z pakietami SDK, Vercel Functions lub kontenery Docker). Kluczowe wymaganie: środowisko hostingowe musi poprawnie obsługiwać długo otwarte połączenia HTTP na potrzeby strumienia SSE GET. Przykładowo, darmowy pakiet Vercela z limitem 10 sekund na wykonanie funkcji nie nadaje się do tego celu. Cloudflare Workers oferuje pełne wsparcie dla długotrwałego strumieniowania danych.

### Integracja z bramami (Gateway)

W architekturach, w których wiele serwerów MCP jest połączonych z jedną bramą (faza 13 · 17), brama udostępnia pojedynczy punkt końcowy HTTP, zarządza identyfikatorami sesji i kieruje zapytania do odpowiednich usług. Z punktu widzenia klienta brama jest widoczna jako jeden spójny serwer MCP.

### Typowe błędy i awarie warstwy transportowej

- **Błąd SIGPIPE (stdio).** Nagłe zakończenie procesu potomnego w trakcie zapisu wywołuje błąd SIGPIPE. Serwery powinny obsługiwać ten wyjątek i kończyć działanie w bezpieczny sposób. Klient po odebraniu EOF oznacza sesję jako zamkniętą.
- **Błędy HTTP 502/504.** Są generowane przez serwery proxy (np. nginx, Cloudflare) w przypadku problemów z komunikacją z serwerem aplikacji. Klient powinien ponowić zapytanie po krótkim czasie.
- **Zerwanie połączenia SSE.** Problemy z siecią, reset połączenia TCP (RST) lub limity czasu na serwerach proxy mogą przerwać strumień. Klient powinien automatycznie połączyć się ponownie, przesyłając `Mcp-Session-Id` oraz opcjonalnie `last-event-id`.
- **Wygaszenie sesji.** Serwer unieważnia identyfikator sesji, a klient przy kolejnym zapytaniu otrzymuje odpowiedź 404. Wymaga to ponownego przeprowadzenia procedury inicjalizacji.

### Kiedy nie stosować Streamable HTTP?

Niektóre systemy korporacyjne uruchamiają serwery MCP za wewnętrznymi protokołami takimi jak gRPC lub z użyciem kolejek komunikatów. Chociaż specyfikacja MCP nie definiuje oficjalnie tych transportów, bramy sieciowe mogą udostępniać interfejs Streamable HTTP na zewnątrz, tłumacząc komunikację na wewnętrzny standard (np. gRPC) pod maską. Zewnętrzny interfejs systemu powinien zawsze pozostać zgodny ze specyfikacją MCP.

## Instrukcja użycia

Plik `code/main.py` zawiera uproszczoną implementację punktu końcowego Streamable HTTP napisaną w czystym Pythonie z użyciem modułu `http.server` z biblioteki standardowej. Skrypt obsługuje żądania POST, GET oraz DELETE na ścieżce `/mcp`, generuje identyfikator `Mcp-Session-Id` przy pierwszym zapytaniu, weryfikuje nagłówek `Origin` i odrzuca żądania z nieznanych domen. Serwer wykorzystuje logikę obsługi notatek opracowaną w lekcji 07.

Na co warto zwrócić uwagę:

- Żądanie POST odczytuje zapytanie JSON-RPC i odsyła odpowiedź (wersja z pojedynczą odpowiedzią; obsługa strumienia SSE ma analogiczną strukturę).
- Walidacja nagłówka `Origin` odrzuca testowe zapytania z domen typu `http://evil.example`, akceptując jednocześnie `http://localhost`.
- Identyfikatory sesji to losowe, 128-bitowe ciągi szesnastkowe zapisywane w pamięci serwera.

## Wynik wdrożenia

W ramach tej lekcji powstaje plik `outputs/skill-mcp-transport-migrator.md`. Narzędzie to analizuje starszy kod serwera MCP korzystający z HTTP+SSE i generuje plan migracji do standardu Streamable HTTP, uwzględniając obsługę identyfikatorów sesji, weryfikację nagłówka Origin oraz mechanizmy kompatybilności wstecznej.

## Ćwiczenia

1. Uruchom `code/main.py`. Wyślij zapytanie `initialize` za pomocą narzędzia `curl` i zaobserwuj nagłówek `Mcp-Session-Id` w odpowiedzi. Wyślij kolejne zapytanie z tym nagłówkiem i upewnij się, że serwer poprawnie przypisał je do tej samej sesji.

2. Zaimplementuj obsługę metody GET otwierającej strumień SSE. Skonfiguruj wysyłanie powiadomienia `notifications/progress` co 5 sekund. Przetestuj ponowne połączenie z tym samym identyfikatorem sesji i upewnij się, że serwer kontynuuje pracę.

3. Dodaj obsługę parametru `last-event-id`. Po wznowieniu połączenia prześlij do klienta wszystkie zaległe powiadomienia wygenerowane od momentu odebrania podanego identyfikatora.

4. Rozbuduj walidację domen w nagłówku `Origin` o obsługę masek (np. `https://*.example.com`). Upewnij się, że serwer akceptuje domeny takie jak `https://app.example.com`, ale odrzuca próby podszywania się pod adresy (np. `https://evil.example.com.attacker.net`).

5. Wybierz dowolny starszy serwer korzystający z HTTP+SSE z publicznego rejestru MCP i zaplanuj jego migrację: określ zmiany w punktach końcowych, generowaniu identyfikatorów sesji oraz obsłudze nagłówków HTTP.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Transport stdio | „Lokalny podproces” | Komunikacja JSON-RPC na stdin/stdout rozdzielana znakami nowej linii |
| Streamable HTTP | „Zdalny transport” | Standard komunikacji zdalnej z pojedynczym punktem końcowym POST/GET zdefiniowany 26.03.2025 |
| HTTP+SSE | „Starszy transport” | Model z dwoma punktami końcowymi wycofywany z użycia w połowie 2026 roku |
| `Mcp-Session-Id` | „Identyfikator sesji” | Nagłówek zawierający losowy klucz sesji przypisywany przez serwer i powtarzany przez klienta |
| Lista dozwolonych `Origin` | „Zabezpieczenie przed DNS Rebinding” | Mechanizm odrzucania żądań z domen, które nie zostały zatwierdzone przez administratora serwera |
| Pojedynczy punkt końcowy | „Jeden adres URL” | Ścieżka `/mcp` obsługująca wszystkie metody (POST / GET / DELETE) w ramach sesji |
| `last-event-id` | „Wznawianie strumienia” | Parametr służący do odtwarzania komunikatów SSE, które nie zostały dostarczone podczas przerwy w połączeniu |
| Sonda kompatybilności | „Weryfikacja transportu” | Testowe zapytanie wysyłane przez klienta w celu automatycznego wyboru obsługiwanej wersji protokołu |
| Strumieniowanie HTTP | „Długie połączenie SSE” | Długotrwały kanał HTTP, przez który serwer przesyła powiadomienia do klienta |

## Dalsze czytanie

- [Model Context Protocol — Basic Transports 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports) — specyfikacja techniczna dla transportów stdio oraz Streamable HTTP.
- [Model Context Protocol — Basic Transports 2025-03-26](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports) — wersja specyfikacji, w której wprowadzono Streamable HTTP.
- [Cloudflare — MCP Transport](https://developers.cloudflare.com/agents/model-context-protocol/transport/) — wdrażanie serwerów MCP w infrastrukturze Cloudflare Workers.
- [AWS — MCP Transport Mechanisms](https://builder.aws.com/content/35A0IphCeLvYzly9Sw40G1dVNzc/mcp-transport-mechanisms-stdio-vs-streamable-http) — porównanie cech wdrożeniowych stdio oraz HTTP.
- [Atlassian — Remote MCP HTTP+SSE Deprecation Notice](https://community.atlassian.com/forums/Atlassian-Remote-MCP-Server/HTTP-SSE-Deprecation-Notice/ba-p/3205484) — komunikat o wycofaniu starszego transportu w systemach Atlassian.
