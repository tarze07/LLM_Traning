# Zasoby i podpowiedzi MCP — ekspozycja kontekstowa wykraczająca poza narzędzia

> Narzędzia przyciągają 90 procent uwagi MCP. Pozostałe dwa prymitywy serwerowe rozwiązują różne problemy. Zasoby udostępniają dane do odczytu; monity udostępniają szablony wielokrotnego użytku jako polecenia ukośnika. Wiele serwerów powinno używać zasobów zamiast zawijać odczyty w narzędziach i podpowiedzi zamiast kodowania na stałe przepływów pracy w monitach klienta. W tej lekcji wymieniono reguły decyzyjne i omówiono komunikaty `resources/*` i `prompts/*`.

**Typ:** Kompilacja
**Języki:** Python (stdlib, zasób + obsługa podpowiedzi)
**Wymagania wstępne:** Faza 13 · 07 (serwer MCP)
**Czas:** ~45 minut

## Cele nauczania

- Zdecyduj, czy chcesz zaprezentować zdolność jako narzędzie, zasób czy zachętę dla danej domeny.
- Zaimplementuj `resources/list`, `resources/read`, `resources/subscribe` i obsłuż `notifications/resources/updated`.
- Zaimplementuj `prompts/list` i `prompts/get` z szablonami argumentów.
- Rozpoznaje, kiedy host wyświetla monity w postaci poleceń ukośnika lub automatycznie wstrzykiwanego kontekstu.

## Problem

Naiwny serwer MCP dla aplikacji do notatek udostępnia wszystko jako narzędzia: `notes_read`, `notes_list`, `notes_search`. Spowoduje to zamknięcie każdego dostępu do danych w wywołaniu narzędzia opartego na modelu. Konsekwencje:

- Model musi zdecydować, czy wywołać `notes_read` dla każdego zapytania, które może skorzystać z kontekstu.
- Treści tylko do odczytu nie mogą być subskrybowane ani przesyłane strumieniowo do bocznego panelu hosta.
- Interfejsy klienta (panel załączników zasobów Claude Desktop, selektor „Dołącz plik” kursora) nie mogą wyświetlać danych.

Właściwy podział: eksponuj dane jako zasób, eksponuj mutujące lub obliczone działania jako narzędzia, udostępniaj wieloetapowe przepływy pracy wielokrotnego użytku jako podpowiedzi. Każdy prymityw ma swoją afordancję UX i wzorzec dostępu.

## Koncepcja

### Narzędzia kontra zasoby kontra podpowiedzi — reguła decyzyjna

| Zdolność | Prymitywny |
|------------|-----------|
| Użytkownik chce wyszukiwać, filtrować lub przekształcać dane | narzędzie |
| Użytkownik chce, aby host umieścił te dane jako kontekst | zasób |
| Użytkownik chce szablonowego przepływu pracy, który może ponownie uruchomić | podpowiedź |

Wytyczna: jeśli model odniesie korzyść z wywoływania go przy każdym powiązanym zapytaniu, jest to narzędzie. Jeśli użytkownik odniesie korzyść z dołączenia go do rozmowy, jest to zasób. Jeśli użytkownik chce ponownie wykorzystać cały, wieloetapowy przepływ pracy, jest to podpowiedź.

### Zasoby

`resources/list` zwraca `{resources: [{uri, name, mimeType, description?}]}`. `resources/read` pobiera `{uri}` i zwraca `{contents: [{uri, mimeType, text | blob}]}`.

URI mogą być dowolne, adresowalne:

- `file:///Users/alice/notes/mcp.md`
- `postgres://my-db/query/SELECT ...`
- `notes://note-14` (schemat niestandardowy)
- `memory://session-2026-04-22/recent` (specyficzne dla serwera)

`contents[]` obsługuje zarówno tekst, jak i plik binarny. Binarny używa `blob` jako ciągu zakodowanego w formacie Base64 plus `mimeType`.

### Subskrypcje zasobów

Zadeklaruj `{resources: {subscribe: true}}` w możliwościach. Klient wywołuje `resources/subscribe {uri}`. Serwer wysyła `notifications/resources/updated {uri}` w przypadku zmiany zasobu. Klient czyta ponownie.

Przypadek użycia: serwer notatek, którego zasobami są pliki na dysku; obserwator plików wyzwala powiadomienia o aktualizacjach; Claude Desktop ponownie pobiera plik do kontekstu, gdy jest edytowany poza hostem.

### Szablony zasobów (dodatek 2025-11-25)

`resourceTemplates` umożliwia ujawnienie sparametryzowanego wzorca URI: `notes://{id}` z `id` jako celem zakończenia. Klient może automatycznie uzupełniać identyfikatory w selektorze zasobów.

### Podpowiedzi

`prompts/list` zwraca `{prompts: [{name, description, arguments?}]}`. `prompts/get` pobiera `{name, arguments}` i zwraca `{description, messages: [{role, content}]}`.

Podpowiedź to szablon, który wypełnia listę komunikatów dostarczanych przez hosta swojemu modelowi. Na przykład zachęta `code_review` przyjmuje argument `file_path` i zwraca sekwencję trzech komunikatów: komunikat systemowy, komunikat użytkownika z treścią pliku i początek asystenta z szablonem rozumowania.

### Hosty i monity

Claude Desktop, VS Code i Cursor wyświetlają podpowiedzi jako polecenia ukośnika w interfejsie czatu. Użytkownik wpisuje `/code_review` i wybiera argumenty z formularza. Monit serwera to umowa pomiędzy „skrótem użytkownika” a „pełnym monitem wysłanym do modelu”.

Nie każdy klient obsługuje jeszcze monity — sprawdź negocjacje możliwości. Serwer z zadeklarowaną możliwością podpowiedzi, ale klient bez obsługi podpowiedzi po prostu nie zobaczy poleceń ukośnika.

### Powiadomienie o zmianie listy

Zarówno zasoby, jak i podpowiedzi emitują `notifications/list_changed`, gdy zestaw ulega mutacji. Serwer notatek, który właśnie zaimportował 20 nowych notatek, emituje `notifications/resources/list_changed`; klient ponownie dzwoni do `resources/list`, aby odebrać dodatki.

### Konwencje typów treści

Dla tekstu: `mimeType: "text/plain"`, `text/markdown`, `application/json`.
W przypadku plików binarnych: `image/png`, `application/pdf` plus pole `blob`.
W przypadku aplikacji MCP (lekcja 14): `text/html;profile=mcp-app` w identyfikatorze URI `ui://`.

### Zasoby dynamiczne

Identyfikator URI zasobu nie musi odpowiadać plikowi statycznemu. `notes://recent` może zwrócić pięć ostatnich notatek przy każdym czytaniu. `db://query/users/active` może wykonać sparametryzowane zapytanie. Serwer może dynamicznie obliczać zawartość.

Reguła: jeśli klient może buforować według URI, URI musi być stabilny. Jeśli obliczenia są wykonywane jednorazowo, identyfikator URI powinien zawierać znacznik czasu lub wartość jednorazową, aby pamięć podręczna klienta nie uległa przedawnieniu.

### Subskrypcje a ankiety

Klienci obsługujący subskrypcję otrzymują funkcję push serwera za pośrednictwem `notifications/resources/updated`. Klienci lub hosty z przedsubskrypcją, które jej nie obsługują, sondują poprzez ponowne odczytanie. Obydwa są zgodne ze specyfikacją. Deklaracja możliwości serwera informuje klienta, które serwery obsługuje.

Koszt subskrypcji: stan na sesję na serwerze (kto i na co subskrybuje). Trzymaj subskrybowany zestaw ograniczony; rozłączeni klienci powinni przekroczyć limit czasu.

### Podpowiedzi a podpowiedzi systemowe

Podpowiedzi w MCP nie są podpowiedziami systemowymi. Podpowiedź systemowa hosta (własna instrukcja obsługi) i podpowiedź MCP (szablony dostarczone przez serwer, wywoływane przez użytkownika) działają obok siebie. Dobrze zachowujący się klient nigdy nie pozwala, aby monit serwera zastąpił monit systemowy; nakłada je warstwowo.

## Użyj tego

`code/main.py` rozszerza serwer notatek z lekcji 07 o:

- Zasoby dla poszczególnych nut (`notes://note-1` itp.) z obsługą `resources/subscribe`.
- Podpowiedź `review_note` wyświetlana w szablonie składającym się z trzech wiadomości.
- Symulacja obserwatora plików, która emituje `notifications/resources/updated` po modyfikacji notatki.
- `notes://recent` zasób dynamiczny, który zawsze zwraca pięć ostatnich notatek.

Uruchom wersję demonstracyjną, aby zobaczyć pełny przebieg.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-primitive-splitter.md`. Biorąc pod uwagę proponowany serwer MCP, umiejętność kategoryzuje każdą możliwość jako narzędzie/zasób/podpowiedź z uzasadnieniem.

## Ćwiczenia

1. Uruchom `code/main.py`. Obserwuj początkową listę zasobów, a następnie uruchom edycję notatki i sprawdź, czy zostało wywołane zdarzenie `notifications/resources/updated`.

2. Dodaj emiter `resources/list_changed`: po utworzeniu nowej notatki wyślij powiadomienie, aby klienci mogli ją ponownie odkryć.

3. Zaprojektuj trzy podpowiedzi dla serwera MCP GitHub: `summarize_pr`, `triage_issue`, `release_notes`. Każdy ze schematami argumentacji. Treść podpowiedzi powinna nadawać się do uruchomienia bez dalszych edycji.

4. Weź istniejące narzędzie na serwerze Lekcji 07 i zaklasyfikuj, czy powinno pozostać narzędziem, czy też zostać podzielone na parę zasobów i narzędzi. Uzasadnij jednym zdaniem.

5. Przeczytaj sekcje `server/resources` i `server/prompts` specyfikacji. Wskaż jedno pole w `resources/read`, które jest rzadko wypełniane, ale obsługiwane przez specyfikację. Wskazówka: spójrz na `_meta` na temat zawartości zasobów.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Zasób | „Ujawnione dane” | Treść adresowalna przez URI, którą host może odczytać |
| URI zasobu | „Wskaźnik do danych” | Identyfikator z prefiksem schematu (`file://`, `notes://` itd.) |
| `resources/subscribe` | „Uważaj na zmiany” | Za zgodą klienta aktualizacje wypychane przez serwer dla określonego identyfikatora URI |
| `notifications/resources/updated` | „Zmieniono zasób” | Sygnał klientowi, że subskrybowany zasób zawiera nową treść |
| Szablon zasobu | „Sparametryzowany URI” | Wzorzec URI ze wskazówkami dotyczącymi zakończenia dla selektora hostów |
| Podpowiedź | „Szablon poleceń z ukośnikiem” | Nazwany szablon wielu wiadomości z miejscami na argumenty |
| Szybkie argumenty | „Wprowadzanie szablonów” | Wpisane parametry, które host zbiera przed renderowaniem |
| `prompts/get` | „Szablon renderowania” | Serwer zwraca wypełnioną listę wiadomości |
| Blok treści | „Wpisany fragment” | `{type: text \| image \| resource \| ui_resource}` |
| Polecenie ukośnika UX | „Skrót użytkownika” | Powierzchnie hosta wyświetlają monity jako polecenia rozpoczynające się od `/` |

## Dalsze czytanie

- [MCP — Concepts: Resources](https://modelcontextprotocol.io/docs/concepts/resources) — identyfikatory URI zasobów, subskrypcje i szablony
- [MCP — Concepts: Prompts](https://modelcontextprotocol.io/docs/concepts/prompts) — szablony podpowiedzi i integracja poleceń ukośnikowych
- [MCP — specyfikacja zasobów serwera 25.11.2025](https://modelcontextprotocol.io/specification/2025-11-25/server/resources) — pełne odwołanie do komunikatu `resources/*`
- [MCP — specyfikacja monitów serwera 25.11.2025](https://modelcontextprotocol.io/specification/2025-11-25/server/prompts) — pełne odwołanie do komunikatu `prompts/*`
- [MCP — witryna informacyjna protokołu: zasoby](https://modelcontextprotocol.info/docs/concepts/resources/) — przewodnik społeczności rozszerzający się na oficjalne dokumenty