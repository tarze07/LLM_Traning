# Transporty MCP — migracja stdio vs Streamable HTTP vs SSE

> stdio działa lokalnie i nigdzie indziej. Streamable HTTP (26.03.2025) to zdalny standard. Stary transport HTTP+SSE jest przestarzały i zostanie usunięty w połowie 2026 r. Wybranie niewłaściwego transportu kosztuje migrację; wybranie właściwego powoduje zakup serwera MCP do zdalnego hostowania z ciągłością sesji i ochroną przed ponownym wiązaniem DNS.

**Typ:** Ucz się
**Języki:** Python (stdlib, szkielet punktu końcowego HTTP do przesyłania strumieniowego)
**Wymagania wstępne:** Faza 13 · 07, 08 (serwer i klient MCP)
**Czas:** ~45 minut

## Cele nauczania

- Wybierz pomiędzy standardowym a strumieniowym HTTP w zależności od kształtu wdrożenia (lokalne lub zdalne, jednoprocesowe lub flotowe).
- Zaimplementuj wzorzec pojedynczego punktu końcowego Streamable HTTP: POST dla żądań, GET dla strumienia sesji.
- Wymuszaj `Origin` sprawdzanie poprawności i semantykę identyfikatora sesji, aby uniknąć ponownego wiązania DNS.
— Przeprowadź migrację starszego serwera HTTP+SSE do Streamable HTTP przed terminami usunięcia przypadającymi na połowę 2026 r.

## Problem

Pierwszym zdalnym transportem MCP (2024–2011) był protokół HTTP+SSE: dwa punkty końcowe, jeden dla komunikatów POST klienta i jeden kanał Server-Sent-Events dla strumienia serwer-klient. To zadziałało. Było to również niezdarne: dwa punkty końcowe na sesję, uszkodzone pamięci podręczne przed niektórymi sieciami CDN i duża zależność od długotrwałych połączeń SSE, które niektóre WAF agresywnie kończą.

Specyfikacja z 26.03.2025 zastąpiła ją Streamable HTTP: jeden punkt końcowy, POST dla żądań klientów, GET do ustanawiania strumienia sesji, oba współdzielą nagłówek `Mcp-Session-Id`. Każdy serwer zbudowany lub migrowany od tego czasu korzysta ze strumieniowego protokołu HTTP. Stary tryb SSE jest przestarzały — Atlassian Rovo usunął go 30 czerwca 2026 r.; Keboola 1 kwietnia 2026; większość pozostałych serwerów dla przedsiębiorstw do końca 2026 r.

A stdio nadal ma znaczenie dla serwerów lokalnych. Claude Desktop, VS Code i każdy klient w kształcie IDE uruchamiają serwery poprzez stdio. Właściwy model mentalny: stdio dla „tej maszyny”, Streamable HTTP dla „przez sieć”. Żadnego skrzyżowania.

## Koncepcja

### stdio

- Transport procesowy dzieci. Klient odradza serwer, komunikuje się poprzez stdin/stdout.
- Jeden obiekt JSON na linię. Rozdzielane znakami nowej linii.
- Brak identyfikatora sesji; tożsamością procesu jest sesja.
- Nie jest wymagane żadne uwierzytelnienie (dziecko dziedziczy granicę zaufania rodzica).
- Nigdy nie używaj w przypadku serwerów zdalnych — do tunelowania potrzebny będzie SSH lub socat, w tym momencie użyj Streamable HTTP.

### Przesyłany strumieniowo protokół HTTP

Pojedynczy punkt końcowy `/mcp` (lub dowolna ścieżka). Obsługuje trzy metody HTTP:

- **POST /mcp.** Klient wysyła wiadomość JSON-RPC. Serwer odpowiada za pomocą pojedynczej odpowiedzi JSON lub strumienia SSE zawierającego jedną lub więcej odpowiedzi (przydatne w przypadku odpowiedzi wsadowych i powiadomień związanych z tym żądaniem).
- **GET /mcp.** Klient otwiera długotrwały kanał SSE. Serwer używa go do żądań serwera do klienta (próbkowanie, powiadomienia, wywoływanie).
- **DELETE /mcp.** Klient jawnie kończy sesję.

Sesje są identyfikowane przez nagłówek `Mcp-Session-Id`, który serwer ustawia w pierwszej odpowiedzi, a klient wysyła echo przy każdym kolejnym żądaniu. Identyfikatory sesji MUSZĄ być losowe kryptograficznie (co najmniej 128 bitów); Identyfikatory wybrane przez klienta są odrzucane ze względów bezpieczeństwa.

### Pojedynczy punkt końcowy kontra dwa

Tryb dwóch punktów końcowych ze starej specyfikacji będzie nadal możliwy do wywołania w 2026 r. — specyfikacja określa, że jest on „zgodny ze starszymi wersjami”. Jednak wszystkie nowe serwery powinny mieć jeden punkt końcowy. Oficjalne zestawy SDK emitują pojedynczy punkt końcowy; używaj starszego trybu tylko podczas rozmowy z niezmigrowanym pilotem.

### `Origin` weryfikacja i ponowne wiązanie DNS

Przeglądarki nie są (obecnie) klientami MCP, ale osoba atakująca może stworzyć stronę internetową, która przekona przeglądarkę do wykonania testu POST do `localhost:1234/mcp` — gdzie nasłuchuje lokalny serwer MCP użytkownika. Jeśli serwer nie sprawdzi `Origin`, polityka tego samego pochodzenia przeglądarki nie zapisze go, ponieważ `Origin: http://evil.com` jest prawidłowy dla różnych źródeł.

Specyfikacja z dnia 25.11.2025 wymaga, aby serwery odrzucały żądania, których `Origin` nie znajduje się na liście dozwolonych. Lista dozwolonych zazwyczaj zawiera warianty hosta klienta MCP (`https://claude.ai`, `vscode-webview://*`) i hosta lokalnego dla lokalnych interfejsów użytkownika.

### Cykl życia identyfikatora sesji

1. Klient wysyła pierwsze żądanie bez `Mcp-Session-Id`.
2. Serwer przydziela losowy identyfikator, ustawia `Mcp-Session-Id` w nagłówku odpowiedzi.
3. Klient powtarza ten nagłówek we wszystkich kolejnych żądaniach oraz `GET /mcp` dla strumienia.
4. Serwer może odwołać sesję; klient widzi 404 przy kolejnych żądaniach i musi ponownie zainicjować.
5. Klient może jawnie USUŃ sesję w celu czystego zamknięcia.

### Zachowaj aktywność i połącz się ponownie

Połączenia SSE zrywają się. Klient ustanawia ponownie połączenie poprzez ponowne GETing z tym samym `Mcp-Session-Id`. Serwer MUSI kolejkować zdarzenia pominięte podczas przestoju (do rozsądnego czasu) i odtwarzać je za pomocą nagłówka `last-event-id`, którego echo powtarza klient.

Faza 13 · 13 obejmuje Zadania, dzięki którym długotrwała praca może przetrwać nawet po ponownym połączeniu przez całą sesję.

### Sonda kompatybilności wstecznej

Klient, który chce obsługiwać zarówno stare, jak i nowe serwery:

1. POST do `/mcp`.
2. Jeśli odpowiedź to `200 OK` z JSON lub SSE, jest to strumieniowy HTTP.
3. Jeśli odpowiedź to `200 OK` z `Content-Type: text/event-stream` ORAZ nagłówkiem `Location` wskazującym na dodatkowy punkt końcowy, jest to starsza wersja protokołu HTTP+SSE; postępuj zgodnie z `Location`.

### Cloudflare, ngrok i hosting

Zdalne produkcyjne serwery MCP w roku 2026 będą działać na platformie Cloudflare Workers (z pakietem SDK dla agentów MCP), Vercel Functions lub w kontenerze Node/Python. Klucz: Twój hosting musi obsługiwać długotrwałe połączenia HTTP dla SSE GET. Limity bezpłatnych poziomów Vercela wynoszą 10 sekund i są nieodpowiednie. Pracownicy Cloudflare obsługują nieograniczone strumienie.

### Skład bramy

Kiedy wiele serwerów MCP łączy się z bramą (faza 13 · 17), brama jest pojedynczym punktem końcowym HTTP umożliwiającym przesyłanie strumieniowe, który przepisuje identyfikatory sesji i multipleksuje w górę. Narzędzia są łączone w warstwie bramy; klient widzi pojedynczy serwer logiczny.

### Tryby awarii transportu

- **stdio SIGPIPE.** Śmierć procesu potomnego w trakcie zapisu podnosi SIGPIPE; serwery powinny zakończyć się czysto. Klienci powinni wykryć EOF i oznaczyć sesję jako martwą.
- **HTTP 502/504.** Cloudflare, nginx i inne serwery proxy emitują je w przypadku awarii przesyłania danych. Klienci HTTP obsługujący przesyłanie strumieniowe powinni ponowić próbę raz po krótkiej przerwie.
- **Zerwanie połączenia SSE.** TCP RST, przekroczenie limitu czasu proxy lub zmiana sieci klienta powoduje zamknięcie strumienia. Klient ponownie łączy się z `Mcp-Session-Id` i opcjonalnie `last-event-id`, aby wznowić.
- **Odwołanie sesji.** Serwer unieważnia identyfikator sesji; klient widzi 404 przy następnym żądaniu. Klient musi ponownie uścisnąć dłoń.
- **Odchylenie zegara.** Obliczenia TTL zasobów na kliencie różnią się od obliczeń na serwerze. Klient powinien traktować znaczniki czasu serwera jako wiarygodne.

### Kiedy pominąć przesyłany strumieniowo protokół HTTP

Niektóre przedsiębiorstwa wdrażają serwery MCP za gRPC lub transportami kolejek komunikatów w swoich własnych sieciach. Jest to niestandardowe — specyfikacja MCP formalnie ich nie definiuje. Bramy mogą udostępniać strumieniową powierzchnię HTTP klientom MCP podczas wewnętrznego korzystania z gRPC. Utrzymuj zgodność powierzchni zewnętrznej ze specyfikacją; brama jest właścicielem tłumaczenia.

## Użyj tego

`code/main.py` implementuje minimalny punkt końcowy HTTP umożliwiający przesyłanie strumieniowe za pomocą `http.server` (stdlib). Obsługuje POST, GET i DELETE na `/mcp`, ustawia `Mcp-Session-Id` na pierwszą odpowiedź, sprawdza `Origin` i odrzuca żądania z źródeł spoza listy dozwolonych. Procedura obsługi ponownie wykorzystuje logikę wysyłania notatek z lekcji 07 serwera.

Na co zwrócić uwagę:

- Procedura obsługi POST odczytuje treść JSON-RPC, wysyła i zapisuje odpowiedź JSON (wariant pojedynczej odpowiedzi; wariant SSE jest strukturalnie podobny).
- Kontrola `Origin` odrzuca domyślną sondę `http://evil.example`, ale akceptuje `http://localhost`.
- Identyfikatory sesji to losowe 128-bitowe ciągi szesnastkowe; serwer przechowuje w pamięci stan sesji.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-mcp-transport-migrator.md`. Biorąc pod uwagę serwer MCP HTTP+SSE (starszy), umiejętność tworzy plan migracji do strumieniowego protokołu HTTP z ciągłością identyfikatora sesji, sprawdzaniem pochodzenia i obsługą sond zgodnych wstecz.

## Ćwiczenia

1. Uruchom `code/main.py`. Opublikuj wiadomość `initialize` z `curl` i zwróć uwagę na nagłówek odpowiedzi `Mcp-Session-Id`. Opublikuj drugie żądanie zawierające echo nagłówka i sprawdź ciągłość sesji.

2. Dodaj procedurę obsługi GET, która otwiera strumień SSE. Wysyłaj jedno zdarzenie `notifications/progress` co pięć sekund. Połącz się ponownie poprzez ponowne GETing z tym samym identyfikatorem sesji i potwierdź, że serwer to akceptuje.

3. Zaimplementuj logikę odtwarzania `last-event-id`. Po ponownym połączeniu odtwórz wszystkie zdarzenia wygenerowane od czasu tego identyfikatora.

4. Rozszerz walidację `Origin`, aby obsługiwała wzorzec wieloznaczny (`https://*.example.com`) i potwierdź, że akceptuje `https://app.example.com`, ale odrzuca `https://evil.example.com.attacker.net`.

5. Weź starszy serwer HTTP+SSE z oficjalnego rejestru (jest ich kilka) i naszkicuj migrację: jakie zmiany w obsłudze punktu końcowego, generowaniu identyfikatora sesji i semantyce nagłówka.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| transport stdio | „Lokalny proces potomny” | JSON-RPC na stdin/stdout, rozdzielane znakami nowej linii |
| Przesyłany strumieniowo protokół HTTP | „Odległy transport” | Pojedynczy punkt końcowy POST + GET + opcjonalnie SSE, specyfikacja z 2025-03-26 |
| HTTP+SSE | „Dziedzictwo” | Model z dwoma punktami końcowymi zostanie usunięty w połowie 2026 r. |
| `Mcp-Session-Id` | „Nagłówek sesji” | Losowy identyfikator przypisany przez serwer jest powtarzany przy każdym kolejnym żądaniu |
| `Origin` lista dozwolonych | „Obrona polegająca na ponownym wiązaniu DNS” | Odrzuć prośby, których pochodzenie nie zostało zatwierdzone |
| Pojedynczy punkt końcowy | „Jeden adres URL” | `/mcp` obsługuje POST / GET / DELETE dla wszystkich operacji sesyjnych |
| `last-event-id` | „Powtórka SSE” | Nagłówek używany do wznowienia przerwanego strumienia bez brakujących zdarzeń |
| Sonda kompatybilności wstecznej | „Stare a nowe wykrywanie” | Kontrola kształtu odpowiedzi klienta, która automatycznie wybiera transport |
| Długowieczny HTTP | „Streaming SSE” | Serwer przesyła zdarzenia przez minuty lub godziny na jednym połączeniu TCP |
| Odwołanie sesji | „Wymuś ponowne uruchomienie” | Serwer unieważnia identyfikator sesji; klient musi ponownie uścisnąć dłoń |

## Dalsze czytanie

- [MCP — Podstawowa specyfikacja transportów 25.11.2025](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports) — kanoniczne odniesienie dla stdio i Streamable HTTP
- [MCP — podstawowa specyfikacja transportów 2025-03-26](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports) — wersja, która wprowadziła Streamable HTTP
— [Cloudflare — transport MCP](https://developers.cloudflare.com/agents/model-context-protocol/transport/) — Wzorce HTTP hostowane przez pracowników
- [AWS — mechanizmy transportu MCP](https://builder.aws.com/content/35A0IphCeLvYzly9Sw40G1dVNzc/mcp-transport-mechanisms-stdio-vs-streamable-http) — porównanie różnych kształtów wdrożeń
- [Atlassian — informacja o wycofaniu protokołu HTTP+SSE](https://community.atlassian.com/forums/Atlassian-Remote-MCP-Server/HTTP-SSE-Deprecation-Notice/ba-p/3205484) — konkretny przykład ostatecznego terminu migracji