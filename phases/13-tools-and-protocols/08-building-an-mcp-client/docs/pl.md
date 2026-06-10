# Budowa klienta MCP — wykrywanie, wywoływanie, zarządzanie sesją

> Większość treści MCP zawiera samouczki dotyczące serwera i macha ręką do klienta. W kodzie klienta znajduje się twarda orkiestracja: tworzenie procesów, negocjowanie możliwości, łączenie list narzędzi na wielu serwerach, próbkowanie wywołań zwrotnych, ponowne łączenie i rozwiązywanie kolizji przestrzeni nazw. W tej lekcji budujemy klienta wieloserwerowego, który łączy trzy różne serwery MCP w jedną płaską przestrzeń nazw narzędzi dla modelu.

**Typ:** Kompilacja
**Języki:** Python (stdlib, wieloserwerowy klient MCP)
**Wymagania wstępne:** Faza 13 · 07 (budowa serwera MCP)
**Czas:** ~75 minut

## Cele nauczania

- Utwórz serwer MCP jako proces potomny, wykonaj `initialize` i wyślij `notifications/initialized`.
- Utrzymanie stanu sesji na serwerze (możliwości, lista narzędzi, identyfikatory ostatnio widzianych powiadomień).
- Scal listy narzędzi na wielu serwerach w jedną przestrzeń nazw z obsługą kolizji.
- Przekieruj wywołanie narzędzia do serwera, który jest jego właścicielem, i ponownie złóż odpowiedź.

## Problem

Prawdziwy host agenta (Claude Desktop, Cursor, Goose, Gemini CLI) ładuje wiele serwerów MCP jednocześnie. Użytkownik może mieć jednocześnie uruchomiony serwer systemu plików, serwer Postgres i serwer GitHub. Zadanie klienta:

1. Spawnuj każdy serwer.
2. Uścisk dłoni każdemu z osobna.
3. Na każdym wywołaj `tools/list` i spłaszcz wynik.
4. Gdy model wyemituje `notes_search`, sprawdź go w połączonej przestrzeni nazw i skieruj do odpowiedniego serwera.
5. Obsługuj powiadomienia z dowolnego serwera (`tools/list_changed`) bez blokowania.
6. Podłącz ponownie w przypadku awarii transportu.

Ręczne walcowanie tego wszystkiego odróżnia „zabawkę” od „użytecznej”. Oficjalne pakiety SDK to opisują, ale model mentalny musi należeć do Ciebie.

## Koncepcja

### Spawnowanie procesu potomnego

`subprocess.Popen` z `stdin=PIPE, stdout=PIPE, stderr=PIPE`. Ustaw `bufsize=1` i użyj trybu tekstowego do odczytu linia po linii. Każdy serwer to jeden proces; klient przechowuje jedno `Popen` uchwyt na serwer.

### Stan sesji na serwerze

Obiekt `Session` na serwer zawiera:

- `process` — uchwyt Popen.
- `capabilities` — co zadeklarował serwer pod adresem `initialize`.
- `tools` — ostatni wynik `tools/list`.
- `pending` — mapa identyfikatora żądania do obietnicy/przyszłości oczekującej na odpowiedź.

Żądania są z natury asynchroniczne; a `tools/call` wysłane do serwera A, gdy serwer B jest w trakcie połączenia, nie może blokować. Użyj wątków z kolejkami lub asyncio.

### Połączona przestrzeń nazw

Kiedy klient widzi zagregowaną listę narzędzi, nazwy mogą się ze sobą kolidować. Obydwa serwery mogą ujawnić `search`. Klient ma trzy możliwości:

1. **Prefiks nazwy serwera.** `notes/search`, `files/search`. Jasne, ale brzydkie.
2. **Kto pierwszy, ten milczy.** `search` późniejszego serwera zastępuje wcześniejsze. Ryzykowny; ukrywa kolizje.
3. **Odrzucenie kolizji.** Odmowa załadowania drugiego serwera; powiadomić użytkownika. Najbezpieczniejszy dla hostów wrażliwych na bezpieczeństwo.

Claude Desktop używa prefiksu według serwera. Kursor wykorzystuje odrzucanie kolizji z wyraźnym błędem. VS Code MCP przyjmuje również prefiks według serwera.

### Trasowanie

Po połączeniu tabela rozsyłania mapuje `tool_name -> session`. Model emituje wywołanie po imieniu; klient znajduje sesję i zapisuje komunikat `tools/call` na standardowe wejście tego serwera, a następnie czeka na odpowiedź.

### Próbkowanie wywołania zwrotnego

Jeśli serwer zadeklarował możliwość `sampling` w `initialize`, może wysłać `sampling/createMessage` z prośbą do klienta o uruchomienie LLM. Klient musi:

1. Zablokuj dalsze żądania kierowane do tego serwera do czasu rozwiązania próbki lub potoku, jeśli jego implementacja obsługuje współbieżność.
2. Zadzwoń do swojego dostawcy LLM.
3. Wyślij odpowiedź z powrotem do serwera.

Lekcja 11 obejmuje pobieranie próbek od początku do końca. Ta lekcja sprawdza ją pod kątem kompletności.

### Obsługa powiadomień

`notifications/tools/list_changed` oznacza ponowne wywołanie `tools/list`. `notifications/resources/updated` oznacza ponowne przeczytanie zasobu, jeśli jest on używany. Powiadomienia nie mogą dawać odpowiedzi – nie próbuj ich potwierdzać.

Typowy błąd klienta: blokowanie pętli odczytu na `tools/call`, gdy powiadomienie znajduje się w strumieniu. Użyj wątku czytnika w tle, który wypycha każdą wiadomość do kolejki; główny wątek jest usuwany z kolejki i wysyłany.

### Ponowne połączenie

Transport może się nie powieść: serwer uległ awarii, system operacyjny zabił proces, zepsuł się potok stdio. Klient wykrywa EOF na stdout i traktuje sesję jako martwą. Opcje:

- Cicho zrestartuj serwer i ponownie uzgadnij. OK dla serwerów tylko do odczytu.
- Ujawnij użytkownikowi awarię. OK dla serwerów stanowych z sesjami widocznymi dla użytkownika.

Faza 13 · 09 obejmuje semantykę ponownego połączenia strumieniowego HTTP; stdio jest prostsze.

### Keepalive i identyfikator sesji

Przesyłany strumieniowo protokół HTTP wykorzystuje nagłówek `Mcp-Session-Id`. Stdio nie ma identyfikatora sesji — tożsamość procesu JEST sesją. Pingi podtrzymujące są opcjonalne; Potoki stdio nie pękają w przypadku braku aktywności.

## Użyj tego

`code/main.py` tworzy trzy symulowane serwery MCP jako podprocesy, uzgadnia każdy z nich, łączy ich listy narzędzi i kieruje wywołania narzędzi do właściwego. „Serwery” to w rzeczywistości inne procesy Pythona, w których działają obiekty odpowiadające na zabawki (nie ma prawdziwego LLM). Uruchom, aby zobaczyć:

- Trzy inicjalizacje, każda z własnym zestawem możliwości.
- Trzy wyniki `tools/list` połączone w przestrzeń nazw zawierającą 7 narzędzi.
- Decyzja o routingu na podstawie nazwy narzędzia.
- Kolizja, której zapobiega prefiks przestrzeni nazw.

Na co zwrócić uwagę:

- Klasa danych `Session` przechowuje stan poszczególnych serwerów w sposób przejrzysty.
- Wątek czytnika w tle usuwa z kolejki każdą linię na standardowe wyjście bez blokowania głównego wątku.
- Tabela wysyłkowa to prosty `dict[str, Session]`.
- Obsługa kolizji jest jawna: gdy dwa serwery deklarują tę samą nazwę, nazwa późniejszego zostaje zmieniona z prefiksem.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-mcp-client-harness.md`. Biorąc pod uwagę deklaratywną listę serwerów MCP (nazwa, polecenie, argumenty), umiejętność tworzy wiązkę, która je odradza, łączy listy narzędzi i dostarcza funkcję routingu z rozwiązywaniem kolizji.

## Ćwiczenia

1. Uruchom `code/main.py` i obejrzyj dziennik odradzania serwera. Zabij jeden z symulowanych procesów serwera za pomocą SIGTERM i obserwuj, jak klient wykrywa EOF i oznacza tę sesję jako martwą.

2. Zaimplementuj przedrostek przestrzeni nazw. Kiedy dwa serwery udostępniają `search`, zmień nazwę drugiego na `<server>/search`. Zaktualizuj tabelę wysyłkową i sprawdź poprawność trasy wywołań narzędzi.

3. Dodaj wycofywanie w stylu puli połączeń w przypadku ponownego uruchomienia serwera: wykładnicze wycofywanie w przypadku kolejnych awarii, ograniczenie do 30 sekund, wysyłanie powiadomienia do użytkownika po trzech awariach.

4. Naszkicuj klienta obsługującego 100 równoczesnych serwerów MCP. Jaka struktura danych zastępuje prosty nakaz wysyłania? (Wskazówka: spróbuj zastosować odstępy nazw przedrostków oraz metrykę dotyczącą liczby narzędzi na serwer.)

5. Przenieś klienta do oficjalnego pakietu SDK MCP Python. SDK otacza `stdio_client` i `ClientSession`. Kod powinien zmniejszyć się z ~200 linii do ~40 linii, zachowując routing wieloserwerowy.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Klient MCP | „Host agenta” | Proces tworzący serwery i organizujący wywołania narzędzi |
| Sesja | „Stan na serwerze” | Możliwości, lista narzędzi i księgowanie oczekujących żądań |
| Połączona przestrzeń nazw | „Jedna lista narzędzi” | Płaski zestaw nazw narzędzi na wszystkich aktywnych serwerach |
| Kolizja przestrzeni nazw | „Dwa serwery to samo narzędzie” | Klient musi poprzedzić, odrzucić lub zgłosić jako pierwszy duplikat |
| Trasowanie | „Kto odbiera to połączenie?” | Wysyłka z nazwy narzędzia do serwera będącego właścicielem |
| Czytnik w tle | „Nieblokujące standardowe wyjście” | Wątek lub zadanie, które opróżnia standardowe wyjście serwera do kolejki |
| Próbkowanie wywołania zwrotnego | „LLM jako usługa” | Obsługa klienta dla `sampling/createMessage` z serwera |
| `notifications/*_changed` | „Prymitywny zmutowany” | Sygnał, że klient musi odkryć na nowo lub ponownie przeczytać |
| Polityka ponownego połączenia | „Kiedy serwer umiera” | Uruchom ponownie semantykę, gdy transport się nie powiedzie |
| Sesja Stdio | „Proces = sesja” | Brak identyfikatora sesji; Czas życia procesu potomnego to sesja |

## Dalsze czytanie

- [Model Context Protocol — specyfikacja klienta](https://modelcontextprotocol.io/specification/2025-11-25/client) — kanoniczne zachowanie klienta
- [MCP — przewodnik klienta Szybki start](https://modelcontextprotocol.io/quickstart/client) — samouczek klienta hello-world z pakietem SDK języka Python
- [MCP Python SDK — moduł klienta](https://github.com/modelcontextprotocol/python-sdk) — odwołanie `ClientSession` i `stdio_client`
- [MCP TypeScript SDK — klient] (https://github.com/modelcontextprotocol/typescript-sdk) — równoległy TS
- [VS Code — MCP w rozszerzeniach] (https://code.visualstudio.com/api/extension-guides/ai/mcp) — jak VS Code multipleksuje wiele serwerów MCP w jednym hoście edytora