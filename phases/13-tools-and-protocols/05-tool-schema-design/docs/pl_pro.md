# Projektowanie schematu narzędzia — nazewnictwo, opisy, ograniczenia parametrów

> Prawidłowo zaimplementowane narzędzie może zawieść w działaniu, jeśli model nie wie dokładnie, kiedy go użyć. Nazewnictwo, opisy oraz struktury parametrów wpływają na wahania dokładności wyboru narzędzi (tool selection accuracy) rzędu 10–20 punktów procentowych w testach porównawczych, takich jak StableToolBench czy MCPToolBench++. W tej lekcji omówimy zasady projektowania, które decydują o tym, czy model bezbłędnie wybierze właściwe narzędzie, czy też pominie je podczas wykonywania zadania.

**Typ:** Ucz się
**Języki:** Python (biblioteka standardowa, linter schematów narzędzi)
**Warunki wstępne:** Faza 13 · 01 (Interfejs narzędzi), Faza 13 · 04 (Ustrukturyzowane dane wyjściowe)
**Czas:** ~45 minut

## Cele nauczania

- Napisz opis narzędzia według szablonu „Użyj, gdy X. Nie używaj dla Y”, zachowując limit do 1024 znaków.
- Nadawaj narzędziom czytelne, spójne nazwy w formacie `snake_case`, zapobiegając niejednoznaczności w dużych rejestrach.
- Podejmij decyzję o wyborze między zestawem narzędzi atomowych a pojedynczym narzędziem monolitycznym dla danego obszaru zadań.
- Uruchom linter schematów narzędzi w rejestrze i popraw wykryte błędy.

## Problem

Wyobraź sobie agenta dysponującego zestawem 30 narzędzi. Przy każdym zapytaniu użytkownika model analizuje opisy dostępnych narzędzi i wybiera jedno z nich. W tym procesie mogą pojawić się dwa typowe błędy:

**Wybór błędnego narzędzia.** Model wybiera `search_contacts`, zamiast wywołać `get_customer_details`. Przyczyna: oba opisy zawierały ogólne sformułowanie „wyszukaj ludzi”, a model nie miał wystarczających danych do rozróżnienia ich funkcji.

**Pominięcie odpowiedniego narzędzia.** Użytkownik pyta o aktualny kurs akcji, a model odpowiada zmyśloną wartością, zamiast użyć narzędzia. Przyczyna: opis narzędzia brzmiał „pobierz dane finansowe”, przez co model nie skojarzył go z zapytaniem o „kurs akcji”.

W przewodniku terenowym Composio zmierzono wahania dokładności wyboru narzędzi sięgające 10–20 punktów procentowych, wynikające wyłącznie ze zmiany nazewnictwa i redakcji opisów. Podobne obserwacje opisano w dokumentacji Anthropic SDK. Analiza Databricks idzie jeszcze dalej: w rejestrze 50 narzędzi o niejednoznacznych opisach skuteczność wyboru spadła do 62%, podczas gdy po optymalizacji opisów ten sam rejestr uzyskał wynik 89%.

Dobra nazwa i precyzyjny opis to najprostsze i najtańsze sposoby na poprawę skuteczności działania agenta.

## Koncepcja

### Zasady nazewnictwa

1. **Format `snake_case`.** Tokenizatory wszystkich dostawców radzą sobie z tym formatem bez problemów. Format `camelCase` w niektórych tokenizatorach może być dzielony na granicy słów na osobne tokeny.
2. **Kolejność czasownik-rzeczownik.** `get_weather`, a nie `weather_get`. Odzwierciedla to naturalny szyk zdań w języku angielskim.
3. **Brak czasu przeszłego ani przyszłego.** `get_weather`, a nie `got_weather` czy `get_weather_later`.
4. **Stabilność wsteczna.** Zmiana nazwy narzędzia to poważna modyfikacja, która psuje kompatybilność. Wersjonuj narzędzia poprzez dodawanie nowych nazw, zamiast modyfikować istniejące.
5. **Przedrostki (przestrzenie nazw) dla dużych rejestrów.** Nazwy `notes_list`, `notes_search`, `notes_create` są znacznie lepsze niż trzy niezależne, ogólne nazwy. Protokół MCP rozwiązuje to poprzez przestrzenie nazw serwerów (omówione w fazie 13 · 17).
6. **Brak przekazywania parametrów w nazwie.** `get_weather_for_city(city)`, a nie `get_weather_in_tokyo()`.

### Szablon opisu

Stosowanie prostego, dwuzdaniowego szablonu znacząco podnosi dokładność wyboru narzędzi:

```
Use when {condition}. Do not use for {close-but-wrong-cases}.
```

Przykład:

```
Use when the user asks about current conditions for a specific city.
Do not use for historical weather or multi-day forecasts.
```

Zdanie określające przypadki wykluczone („Do not use for...”) pozwala modelowi precyzyjnie rozróżnić narzędzia o zbliżonym działaniu.

Opis powinien mieścić się w limicie 1024 znaków. OpenAI w trybie ścisłym (Strict Mode) obcina dłuższe opisy.

Dodawaj wskazówki dotyczące formatu danych: „Akceptuje nazwy miast w języku angielskim. Zwraca temperaturę w stopniach Celsjusza, chyba że parametr `units` wskazuje inaczej”. Model wykorzysta te informacje do prawidłowego uzupełnienia parametrów wywołania.

### Narzędzia atomowe vs monolityczne

Narzędzie monolityczne:

```python
do_everything(action: str, target: str, options: dict)
```

Z technicznego punktu widzenia pozwala na zachowanie zasady DRY (Don't Repeat Yourself), ale zmusza model do określania parametrów `action` oraz `options` z surowych ciągów tekstowych lub nieotagowanych słowników. W testach porównawczych podejście monolityczne obniża celność wyboru narzędzi o 15 do 30 procent.

Narzędzia atomowe:

```python
notes_list()
notes_create(title, body)
notes_delete(note_id)
notes_search(query)
```

Każde z nich posiada precyzyjny opis oraz jednoznaczny schemat typów. Model dokonuje wyboru na poziomie nazwy funkcji, a nie poprzez analizę wartości przekazywanych w argumencie `action`.

Zasada ogólna: jeśli argument `action` może przyjmować więcej niż trzy różne wartości, należy podzielić narzędzie na osobne funkcje.

### Projektowanie parametrów

- **Stosuj typy wyliczeniowe (enum) dla zbiorów zamkniętych.** Zamiast `units: string` zadeklaruj `units: "celsius" | "fahrenheit"`. Informuje to model o dopuszczalnym zakresie wartości.
- **Wyraźnie określaj parametry wymagane i opcjonalne.** Zdefiniuj minimalny zestaw wymaganych danych. Pozostałe oznacz jako opcjonalne. W trybie ścisłym OpenAI wymaga zadeklarowania wszystkich pól jako wymaganych (`required`); w takim przypadku możesz zdefiniować w kodzie domyślną flagę (np. `is_default: true`) i pozwolić modelowi na pominięcie wartości.
- **Stosuj walidację formatu identyfikatorów.** Wartość `note_id: string` jest poprawna, ale dodanie ograniczenia `pattern` (`^note-[0-9]{8}$`) zapobiega generowaniu halucynowanych ID przez model.
- **Unikaj zbyt elastycznych typów.** Stosowanie `type: any` prowadzi do generowania przez model obiektów o nieprzewidywalnej strukturze.
- **Dodawaj opisy do poszczególnych pól.** Przykład: `{"type": "string", "description": "ISO 8601 date in UTC, e.g. 2026-04-22"}`. Opis pola stanowi część promptu i instruuje model, jak formatować dane.

### Komunikaty o błędach jako instrukcja naprawcza

Gdy wykonanie narzędzia zakończy się niepowodzeniem, komunikat o błędzie jest przekazywany z powrotem do modelu. Błędy powinny być sformułowane w sposób zrozumiały dla LLM:

```
ZŁY PRZYKŁAD: TypeError: object of type 'NoneType' has no attribute 'lower'
DOBRY PRZYKŁAD: Invalid input: 'city' is required. Example: {"city": "Bengaluru"}.
```

Precyzyjnie sformułowany komunikat o błędzie wskazuje modelowi, jak poprawić wywołanie. Testy wykazują, że ustrukturyzowane komunikaty o błędach pozwalają ograniczyć liczbę ponownych prób o połowę, zwłaszcza przy użyciu słabszych modeli.

### Wersjonowanie

Narzędzia podlegają zmianom w czasie. Przestrzegaj poniższych zasad:

- **Nigdy nie zmieniaj nazwy działającego narzędzia.** Zamiast tego dodaj `get_weather_v2` i oznacz `get_weather` jako przestarzałe.
- **Nigdy nie zmieniaj typów argumentów.** Zmiana typu na szerszy (np. ze string na string lub number) wymaga utworzenia nowej wersji narzędzia.
- **Dodawanie opcjonalnych parametrów jest bezpieczne.** Możesz je wprowadzać bez zmiany wersji.
- **Usuwanie narzędzi powinno być poprzedzone okresem przejściowym.** Oznacz narzędzie flagą `deprecated: true` i usuń je dopiero po pełnym cyklu wydawniczym.

### Zapobieganie wstrzykiwaniu instrukcji (Prompt Injection)

Opisy narzędzi są przekazywane bezpośrednio do kontekstu modelu. Istnieje ryzyko, że złośliwy serwer spróbuje osadzić w nich ukryte instrukcje (np. „odczytaj plik ~/.ssh/id_rsa i prześlij go na adres...”). Temat ten szczegółowo omawia faza 13 · 15. W ramach tej lekcji nasz linter automatycznie odrzuca opisy zawierające słowa kluczowe wskazujące na próby wstrzyknięcia instrukcji (np. `<SYSTEM>`, `ignore previous`, wzorce skracaczy linków lub nieodpowiednio sformatowane tagi markdown).

### Testy porównawcze (Benchmarks)

- **StableToolBench.** Mierzy dokładność wyboru narzędzi w ramach ustalonego rejestru. Służy do weryfikacji decyzji projektowych dotyczących schematów.
- **MCPToolBench++.** Rozszerza test StableToolBench o obsługę serwerów MCP, weryfikując procesy odkrywania i wyboru narzędzi.
- **SafeToolBench.** Testuje odporność zestawu narzędzi na ataki (np. zatrute opisy).

Wszystkie te narzędzia są dostępne jako open-source i pozwalają na uruchomienie pełnego cyklu testowego w czasie poniżej godziny na podstawowej karcie graficznej. Warto włączyć je do procesu CI (programowanie sterowane ewaluacją zostanie omówione w kolejnych fazach).

## Instrukcja użycia

Plik `code/main.py` zawiera linter schematów narzędzi, który weryfikuje rejestr pod kątem opisanych wyżej reguł. Wykrywa on:

- Nazwy niezgodne z formatem `snake_case` lub zawierające parametry.
- Opisy za krótkie (poniżej 40 znaków), za długie (powyżej 1024 znaków) lub niezawierające sekcji wykluczającej „Do not use for”.
- Schematy bez określonych typów pól, bez zdefiniowanej listy pól wymaganych lub posiadające podejrzane wzorce w opisach (ryzyko wstrzyknięcia instrukcji).
- Struktury monolityczne oparte o parametr `action: str`.

Uruchom skrypt na dołączonych rejestrach `GOOD_REGISTRY` (poprawny) oraz `BAD_REGISTRY` (zawierający błędy), aby zobaczyć raport z walidacji.

## Wynik wdrożenia

W ramach tej lekcji powstaje plik `outputs/skill-tool-schema-linter.md`. Narzędzie to analizuje dowolny rejestr narzędzi, sprawdza go pod kątem zgodności z opisanymi zasadami i generuje listę poprawek z określeniem stopnia ważności oraz rekomendacjami zmian. Może być zintegrowane z systemami CI.

## Ćwiczenia

1. Otwórz `BAD_REGISTRY` w `code/main.py` i popraw każde z narzędzi tak, aby przechodziło walidację lintera. Porównaj liczbę naruszeń zasad i długość opisów przed i po modyfikacji.

2. Zaprojektuj serwer MCP dla aplikacji do notatek zawierający zestaw narzędzi atomowych: listowanie, wyszukiwanie, tworzenie, aktualizacja, usuwanie oraz narzędzie pomocnicze `summarize`. Przeprowadź linting rejestru i upewnij się, że nie zwraca on żadnych błędów.

3. Wybierz dowolny popularny serwer z oficjalnego rejestru MCP i przeanalizuj opisy jego narzędzi. Zaproponuj co najmniej dwie poprawki usprawniające ich działanie.

4. Zintegruj linter z procesem CI. Skonfiguruj build tak, aby kończył się błędem, jeśli weryfikacja schematów narzędzi w nowym kodzie (PR) wykaże naruszenia o statusie `block`. Wzorce CI oparte na ewaluacji zostaną omówione w kolejnych fazach.

5. Przeczytaj uważnie przewodnik projektowania narzędzi przygotowany przez Composio. Zidentyfikuj jedną zasadę, która nie została opisana w tej lekcji, i dodaj jej obsługę do kodu lintera.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Schemat narzędzia | „Struktura wejściowa” | Schemat JSON określający dopuszczalne argumenty wywołania narzędzia |
| Opis narzędzia | „Opis przeznaczenia” | Krótki opis w języku naturalnym, na podstawie którego model decyduje o wyborze narzędzia |
| Narzędzie atomowe | „Jedno narzędzie, jedna akcja” | Narzędzie wykonujące jedną, jasno określoną operację, odzwierciedloną w nazwie |
| Narzędzie monolityczne | „Szwajcarski scyzoryk” | Pojedyncze narzędzie przyjmujące parametr typu `action: str`; znacząco obniża celność wyboru |
| Zbiór zamknięty (Enum) | „Parametr kategoryczny” | Definicja `{type: "string", enum: [...]}` określająca zamkniętą listę dopuszczalnych opcji |
| Zatrucie narzędzia | „Wstrzyknięta instrukcja” | Złośliwy kod lub instrukcje ukryte w opisie narzędzia, przejmujące kontrolę nad agentem |
| Celność wyboru narzędzi | „Trafność wywołania” | Odsetek zapytań, w których model poprawnie wybiera właściwe narzędzie |
| Linter opisów | „Walidator schematów w CI” | Automatyczny skrypt weryfikujący nazewnictwo, długość opisów i ujednoznacznienia |
| Przedrostek przestrzeni nazw | „notatki_*” | Spójny prefiks grupujący powiązane funkcjonalnie narzędzia w dużych rejestrach |
| StableToolBench | „Benchmark wyboru” | Otwarty zestaw testowy do oceny skuteczności wyboru narzędzi przez modele |

## Dalsze czytanie

- [Composio — How to Build Tools for AI Agents: A Field Guide](https://composio.dev/blog/how-to-build-tools-for-ai-agents-a-field-guide) — dobre praktyki nazewnictwa i opisów oraz zmierzone wzrosty wydajności.
- [OneUptime — Tool Schemas for Agents](https://oneuptime.com/blog/post/2026-01-30-tool-schemas/view) — produkcyjne wzorce projektowania parametrów.
- [Databricks — Agent System Design Patterns](https://docs.databricks.com/aws/en/generative-ai/guide/agent-system-design-patterns) — projektowanie rejestru narzędzi i testy porównawcze.
- [Anthropic — Building Agents with the Claude Agent SDK](https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk) — wzorce tworzenia opisów dla modeli Claude.
- [OpenAI — Function Calling Best Practices](https://platform.openai.com/docs/guides/function-calling#best-practices) — wymagania dotyczące długości opisów, trybu ścisłego oraz wytyczne dla narzędzi atomowych.
