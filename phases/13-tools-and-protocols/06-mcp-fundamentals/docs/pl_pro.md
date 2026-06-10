# Podstawy MCP — elementy podstawowe, cykl życia, baza JSON-RPC

> Przed powstaniem MCP każda integracja była tworzona jednorazowo pod konkretny system. Model Context Protocol (MCP), wprowadzony przez firmę Anthropic w listopadzie 2024 roku, a obecnie rozwijany pod egidą Agentic AI Foundation przy Linux Foundation, standaryzuje procesy odkrywania i wywoływania narzędzi. Dzięki temu dowolny klient może bez problemu komunikować się z każdym serwerem zgodnym z protokołem. Specyfikacja z dnia 25.11.2025 roku definiuje sześć podstawowych komponentów (trzy po stronie serwera, trzy po stronie klienta), trójfazowy cykl życia połączenia oraz format komunikacji JSON-RPC 2.0. Opanowanie tych podstaw sprawi, że dalsza część rozdziału poświęconego MCP będzie wyjątkowo prosta do przyswojenia.

**Typ:** Ucz się
**Języki:** Python (biblioteka standardowa, parser JSON-RPC)
**Warunki wstępne:** Faza 13 · 01 do 05 (Interfejs narzędzi i wywoływanie funkcji)
**Czas:** ~45 minut

## Cele nauczania

- Wymień wszystkie sześć podstawowych komponentów (prymitywów) MCP (narzędzia, zasoby i szablony promptów po stronie serwera; katalogi główne/roots, próbkowanie/sampling i formularze wywoływania/elicitation po stronie klienta) oraz podaj po jednym przypadku użycia dla każdego z nich.
- Prześledź trójfazowy cykl życia połączenia (inicjalizacja, operacja, zamknięcie) i wskaż, która strona wysyła dany komunikat w poszczególnych fazach.
- Parsuj i generuj strukturę żądań, odpowiedzi oraz powiadomień JSON-RPC 2.0.
- Wyjaśnij mechanizm negocjowania możliwości (capabilities negotiation) w metodzie `initialize` i wskaż konsekwencje jego pominięcia.

## Problem

Przed wprowadzeniem standardu MCP każdy agent AI wykorzystujący narzędzia komunikował się za pomocą własnego, zamkniętego protokołu. Edytor Cursor posiadał swój własny system narzędzi (zbliżony do MCP, ale niekompatybilny). Aplikacja Claude Desktop korzystała z jeszcze innego formatu. Wtyczka GitHub Copilot do VS Code bazowała na trzecim rozwiązaniu. W efekcie programiści tworzący narzędzie typu „Zapytanie SQL Postgres” musieli implementować je trzykrotnie – osobno dla każdego z interfejsów API hosta. Wielokrotne użycie tego samego kodu było niemożliwe bez jego ręcznego kopiowania i przepisywania.

Doprowadziło to do eksplozji jednorazowych, niekompatybilnych integracji, co znacznie hamowało rozwój całego ekosystemu.

MCP rozwiązuje ten problem poprzez ujednolicenie formatu wymiany danych w sieci. Pojedynczy serwer MCP działa bez zmian w każdym kompatybilnym kliencie: Claude Desktop, ChatGPT, Cursor, VS Code, Gemini, Goose, Zed czy Windsurf (ponad 300 klientów do kwietnia 2026 roku). Liczba pobrań SDK sięga 110 milionów miesięcznie, a w sieci dostępnych jest ponad 10 000 publicznych serwerów. Linux Foundation przejęła nadzór nad projektem w grudniu 2025 roku w ramach nowo utworzonej organizacji Agentic AI Foundation.

Wersja specyfikacji zastosowana w tym rozdziale to **2025-11-25**. Wprowadza ona m.in. zadania asynchroniczne (SEP-1686), wywoływanie w trybie URL (SEP-1036), próbkowanie z użyciem narzędzi (SEP-1577), stopniową zgodę na uprawnienia (SEP-835) oraz mechanizmy autoryzacji zasobów za pomocą OAuth 2.1. Rozszerzenia te zostaną omówione w fazach 13 · 09 do 16. W tej lekcji skupimy się na fundamentach protokołu.

## Koncepcja

### Trzy komponenty serwera (Server Primitives)

1. **Narzędzia (Tools).** Funkcje i akcje, które klient może wywołać. Działają w oparciu o pętlę opisaną w fazie 13 · 01.
2. **Zasoby (Resources).** Dane udostępniane przez serwer. Treści przeznaczone wyłącznie do odczytu, identyfikowane przez URI: `file:///sciezka`, `db://query/...` lub schematy niestandardowe.
3. **Szablony promptów (Prompts).** Szablony gotowe do ponownego użycia. Są one widoczne np. jako komendy z ukośnikiem (slash commands) w interfejsie użytkownika klienta; serwer dostarcza szablon, a klient uzupełnia jego parametry.

### Trzy komponenty klienta (Client Primitives)

4. **Katalogi główne (Roots).** Zbiór ścieżek URI, do których serwer ma prawo dostępu. Klient je deklaruje, a serwer musi przestrzegać tych ograniczeń.
5. **Próbkowanie (Sampling).** Funkcja pozwalająca serwerowi na wysłanie zapytania do modelu klienta w celu wygenerowania odpowiedzi. Pozwala to na uruchamianie pętli agenta bezpośrednio na serwerze bez konieczności przechowywania kluczy API na serwerze.
6. **Formularze wywoływania (Elicitation).** Możliwość zapytania użytkownika klienta w czasie rzeczywistym o podanie ustrukturyzowanych danych wejściowych za pomocą formularzy lub adresów URL (zgodnie z SEP-1036).

Każda funkcja w protokole MCP należy do jednej z tych sześciu kategorii. Szczegółowo zostaną one omówione w fazach 13 · 10 do 14.

### Format komunikacji: JSON-RPC 2.0

Każda wiadomość w protokole jest obiektem JSON posiadającym następujące pola:

- **Żądania (Requests):** `{jsonrpc: "2.0", id, method, params}`.
- **Odpowiedzi (Responses):** `{jsonrpc: "2.0", id, result | error}`.
- **Powiadomienia (Notifications):** `{jsonrpc: "2.0", method, params}` — nie posiadają pola `id`, nie wymagają odpowiedzi.

Specyfikacja definiuje około 15 podstawowych metod. Najważniejsze z nich to:

- `initialize` / `initialized` (nawiązanie połączenia / handshake)
- `tools/list`, `tools/call`
- `resources/list`, `resources/read`, `resources/subscribe`
- `prompts/list`, `prompts/get`
- `sampling/createMessage` (wywoływane przez serwer do klienta)
- `notifications/tools/list_changed`, `notifications/resources/updated`, `notifications/progress`

### Trójfazowy cykl życia połączenia

**Faza 1: Inicjalizacja (Initialization)**

Klient wysyła żądanie `initialize` zawierające zadeklarowane możliwości (`capabilities`) oraz informacje o sobie (`clientInfo`). Serwer odpowiada, podając własne `capabilities`, `serverInfo` oraz obsługiwaną wersję protokołu. Po odebraniu i przetworzeniu tej odpowiedzi klient wysyła powiadomienie `notifications/initialized`. Od tego momentu obie strony mogą przesyłać komunikaty w ramach uzgodnionych możliwości.

**Faza 2: Operacja (Operation)**

Faza dwukierunkowej wymiany danych. Klient odpytuje serwer za pomocą `tools/list` o dostępne narzędzia, a następnie wywołuje je przez `tools/call`. Jeśli serwer zadeklarował taką możliwość, może wysłać żądanie `sampling/createMessage` do klienta. Serwer może również wysłać powiadomienie `notifications/tools/list_changed`, jeśli lista narzędzi ulegnie zmianie. Klient może poinformować o zmianie katalogów głównych za pomocą `notifications/roots/list_changed`.

**Faza 3: Zamknięcie (Shutdown)**

Dowolna ze stron może zamknąć połączenie. Protokół MCP nie definiuje dedykowanej metody zamykania sesji na poziomie aplikacji – informacja o rozłączeniu jest przekazywana bezpośrednio przez warstwę transportową (np. zamknięcie strumienia stdio lub HTTP Stream, o czym mowa w fazie 13 · 09).

### Negocjowanie możliwości (Capabilities Negotiation)

Obiekt `capabilities` przesyłany podczas inicjalizacji stanowi formalny kontrakt między stronami. Przykład konfiguracji serwera:

```json
{
  "tools": {"listChanged": true},
  "resources": {"subscribe": true, "listChanged": true},
  "prompts": {"listChanged": true}
}
```

Serwer deklaruje w ten sposób, że obsługuje powiadomienia o zmianie listy narzędzi (`tools/list_changed`) oraz subskrypcję zasobów. Klient deklaruje swoje możliwości w następujący sposób:

```json
{
  "roots": {"listChanged": true},
  "sampling": {},
  "elicitation": {}
}
```

Jeśli klient nie zadeklaruje obsługi `sampling`, serwer nie ma prawa wysłać żądania `sampling/createMessage`. Analogicznie: jeśli serwer nie zadeklaruje `resources.subscribe`, klient nie może próbować subskrybować zasobów.

Dzięki temu eliminujemy ryzyko niekompatybilności w ekosystemie. Klient, który nie obsługuje próbkowania (sampling), nadal pozostaje w pełni poprawnym klientem MCP, a serwer niewykorzystujący tej funkcji jest poprawnym serwerem. Strony po prostu nie korzystają ze wspólnych zaawansowanych funkcji.

### Ustrukturyzowana treść i formaty błędów

Metoda `tools/call` zwraca w polu `content` tablicę obiektów reprezentujących konkretne typy danych: `text`, `image` lub `resource`. Faza 13 · 14 dodaje do tej listy aplikacje MCP (interfejsy użytkownika identyfikowane przez schemat `ui://`).

Do obsługi błędów stosuje się standardowe kody błędów JSON-RPC. Dodatkowo specyfikacja MCP definiuje własne kody, np.: `-32002` („Nie znaleziono zasobu”), `-32603` („Błąd wewnętrzny”) oraz pozwala na przekazywanie szczegółów błędu w polu `error.data`.

### Możliwości klienta a wywoływanie narzędzi

Częste nieporozumienie: wartość `capabilities.tools` określa jedynie, czy klient potrafi obsługiwać powiadomienia o zmianach na liście narzędzi. To, czy model klienta faktycznie wywoła dane narzędzie w toku pracy, zależy od decyzji silnika LLM w czasie rzeczywistym, a nie od flag możliwości. Flaga możliwości to kontrakt techniczny na poziomie protokołu, natomiast decyzje modelu są podejmowane niezależnie.

### Dlaczego JSON-RPC, a nie REST?

JSON-RPC 2.0 (standard z 2010 roku) to lekki, dwukierunkowy protokół. Klasyczny REST jest inicjowany wyłącznie przez klienta. Protokół MCP wymagał możliwości inicjowania komunikacji również przez serwer (np. próbkowanie lub powiadomienia), dlatego symetryczny format żądanie/odpowiedź w JSON-RPC okazał się naturalnym wyborem. Ponadto JSON-RPC doskonale sprawdza się przy transmisji przez stdio oraz WebSocket/HTTP Stream bez konieczności ponownego definiowania struktury zapytań HTTP.

## Instrukcja użycia

Plik `code/main.py` zawiera uproszczony parser i emiter wiadomości JSON-RPC 2.0. Skrypt przechodzi ręcznie przez sekwencję kroków: `initialize` → `tools/list` → `tools/call` → `shutdown`, wypisując każdy wygenerowany komunikat. Działa on lokalnie, bez użycia rzeczywistej warstwy transportowej. Porównaj wygenerowane komunikaty z dokumentacją techniczną, aby przeanalizować strukturę pakietów.

Na co warto zwrócić uwagę:

- Metoda `initialize` wymienia możliwości obu stron; odpowiedź serwera zawiera obiekt `serverInfo` oraz wersję protokołu `protocolVersion: "2025-11-25"`.
- Żądanie `tools/list` zwraca listę narzędzi, z których każde posiada pola `name`, `description` oraz `inputSchema`.
- Metoda `tools/call` przekazuje parametry w polach `params.name` oraz `params.arguments`.
- Odpowiedź w polu `content` zawiera tablicę bloków danych typu `{type, text}`.

## Wynik wdrożenia

W ramach tej lekcji powstaje plik `outputs/skill-mcp-handshake-tracer.md`. Narzędzie to analizuje logi komunikacji (w stylu zrzutu pcap) między klientem a serwerem MCP, opisując każdy pakiet: wskazuje użyty komponent, fazę cyklu życia oraz powiązane flagi możliwości (capabilities).

## Ćwiczenia

1. Uruchom `code/main.py`. Wskaż linię kodu, w której odbywa się negocjacja możliwości, i opisz, co uległoby zmianie, gdyby serwer nie zadeklarował obsługi `tools.listChanged`.

2. Rozbuduj parser o obsługę powiadomienia `notifications/progress`. Format wiadomości: `{method: "notifications/progress", params: {progressToken, progress, total}}`. Wyemituj taki komunikat w trakcie symulowanego, długiego wywołania `tools/call` i upewnij się, że klient poprawnie interpretuje dane o postępie.

3. Przeczytaj uważnie oficjalną specyfikację MCP z dnia 2025-11-25. Zidentyfikuj jedną flagę możliwości (capability), która rzadko jest wymagana przez proste serwery (Wskazówka: dotyczy subskrypcji zasobów).

4. Zaprojektuj strukturę nowego komponentu (primitive) dla hipotetycznej funkcji planowania zadań ("cron jobs") – serwer chce zlecić klientowi wywołanie określonej metody o zadanej godzinie. Żaden z obecnych 6 komponentów nie obsługuje tego scenariusza. Wskazówka: w planach rozwoju MCP (MCP Roadmap) na 2026 rok znajduje się szkic propozycji SEP dla tego zastosowania.

5. Przeanalizuj logi sesji dowolnego publicznego serwera MCP dostępnego na GitHubie. Zlicz liczbę żądań, odpowiedzi oraz powiadomień. Oblicz, jaki procent ruchu stanowią komunikaty związane z zarządzaniem cyklem życia połączenia w porównaniu do operacji biznesowych.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| MCP | „Protokół kontekstu modelu” | Otwarty standard komunikacji modeli językowych z narzędziami zewnętrznymi |
| Serwerowe komponenty (Server Primitives) | „Zasoby serwera” | Narzędzia (akcje), zasoby (dane) oraz szablony promptów (szablony) |
| Klienckie komponenty (Client Primitives) | „Uprawnienia klienta” | Katalogi główne (dostęp do ścieżek), próbkowanie (zapytania LLM) oraz wywoływanie (interakcja) |
| JSON-RPC 2.0 | „Protokół przesyłu” | Lekki, symetryczny format żądanie/odpowiedź/powiadomienie zapisany w JSON |
| Handshake `initialize` | „Negocjacja możliwości” | Pierwsza wymiana komunikatów, w której strony deklarują obsługiwane funkcje |
| `tools/list` | „Odkrywanie” | Zapytanie klienta o listę dostępnych na serwerze narzędzi |
| `tools/call` | „Uruchomienie” | Żądanie wykonania określonego narzędzia z przekazanymi parametrami |
| `notifications/*_changed` | „Aktualizacje stanu” | Powiadomienia serwera o modyfikacji zasobów lub listy narzędzi |
| Blok treści (Content Block) | „Typ wyniku” | Obiekt `{type: "text" \| "image" \| "resource"}` w odpowiedzi na wywołanie narzędzia |
| SEP | „Propozycja zmian” | Zgłoszony projekt modyfikacji specyfikacji protokołu (np. SEP-1686) |

## Dalsze czytanie

- [Model Context Protocol — Specification 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25) — oficjalny dokument specyfikacji standardu.
- [Model Context Protocol — Architecture Concepts](https://modelcontextprotocol.io/docs/concepts/architecture) — opis architektury i 6 podstawowych komponentów.
- [Anthropic — Introducing the Model Context Protocol](https://www.anthropic.com/news/model-context-protocol) — oficjalne ogłoszenie protokołu z listopada 2024 roku.
- [MCP Blog — First Anniversary of MCP](https://blog.modelcontextprotocol.io/posts/2025-11-25-first-mcp-anniversary/) — podsumowanie roku rozwoju i zmian wprowadzonych w wersji z listopada 2025.
- [WorkOS — MCP 2025-11-25 Spec Update](https://workos.com/blog/mcp-2025-11-25-spec-update) — zestawienie najważniejszych zmian (SEP-1686, 1036, 1577, 835 oraz 1724).
