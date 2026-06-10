# Interfejs narzędzi — dlaczego agenci potrzebują strukturyzowanych operacji we/wy

> Model językowy generuje tokeny tekstowe. Program komputerowy podejmuje działania w świecie rzeczywistym. Pomostem między nimi jest interfejs narzędzi (tool interface): kontrakt określający, w jaki sposób model może zażądać wykonania akcji, a system hostujący (host) może ją zrealizować. Wszelkie nowoczesne implementacje w 2026 roku – mechanizmy Function Calling w API OpenAI, Anthropic czy Gemini, protokół MCP (`tools/call`), czy standardy komunikacji między agentami A2A – to tylko różne warianty tej samej czteroetapowej pętli. Ta lekcja definiuje ten cykl i przedstawia minimalistyczny kod do jego obsługi.

**Typ:** Teoria / Podstawy
**Języki:** Python (biblioteka standardowa, bez użycia zewnętrznych LLM)
**Wymagania wstępne:** Faza 11 (Interfejsy API generowania tekstu - Chat Completion API)
**Czas:** ~45 minut

## Cele kształcenia

- Wyjaśnienie, dlaczego model LLM, który potrafi jedynie generować tekst, nie jest w stanie samodzielnie wchodzić w interakcję ze światem zewnętrznym.
- Przedstawienie czteroetapowej pętli wywołań narzędzi (Opisz → Zdecyduj → Wykonaj → Zaobserwuj) wraz z podziałem odpowiedzialności za każdy etap.
- Opracowanie trójskładnikowego opisu narzędzia: nazwa, schemat wejściowy JSON Schema oraz deterministyczna funkcja wykonawcza (executor).
- Rozróżnienie między narzędziami czystymi (pure) a wywołującymi skutki uboczne (consequential) i wyjaśnienie znaczenia tego podziału dla bezpieczeństwa agenta.

## Problem

Model LLM w swojej istocie jedynie wylicza rozkład prawdopodobieństwa dla kolejnych tokenów tekstowych. To jest jego jedyny kanał wyjściowy. Gdy zapytamy model: „Jaka jest teraz pogoda w Bangalore?”, może on sformułować gramatycznie poprawne i wiarygodnie brzmiące zdanie, ale nie potrafi samodzielnie nawiązać połączenia z zewnętrznym API pogodowym. Jego odpowiedź będzie w najlepszym wypadku domysłem, a w najgorszym – halucynacją na podstawie nieaktualnych danych treningowych.

Rozwiązaniem tego problemu jest interfejs narzędzi. Program uruchomieniowy (host) – np. środowisko wykonawcze agenta, aplikacja Claude Desktop, ChatGPT, edytor Cursor czy autorski skrypt – udostępnia modelowi listę narzędzi wraz z ich specyfikacją. Gdy model uzna, że do udzielenia odpowiedzi niezbędne jest wykonanie określonej akcji, generuje ustrukturyzowany ładunek (payload) zawierający nazwę narzędzia oraz wartości jego argumentów. Host przechwytuje ten ładunek, wykonuje powiązaną funkcję w świecie rzeczywistym (np. wysyła zapytanie HTTP) i zwraca wynik do modelu. Pętla ta powtarza się, dopóki model nie zdecyduje, że posiada już komplet danych do sformułowania ostatecznej odpowiedzi.

Pierwszy oficjalny kontrakt tego typu zadebiutował w czerwcu 2023 roku jako parametr `functions` w API OpenAI. Niedługo potem Anthropic dodał bloki `tool_use` w modelu Claude 2.1, a Google wprowadziło sekcję `functionDeclarations` w Gemini. Obecnie wszyscy dostawcy stosują ten sam schemat: deklaracja listy dostępnych narzędzi za pomocą standardu JSON Schema oraz wymiana komunikatów w formacie JSON. Protokół Model Context Protocol (MCP, listopad 2024) ujednolicił ten interfejs, tworząc wspólny rejestr narzędzi niezależny od dostawcy modelu, a standardy A2A (kwiecień 2026, wersja 1.0) zaadaptowały te same reguły do komunikacji między autonomicznymi agentami.

Ta czteroetapowa pętla leży u podstaw każdego z tych systemów. Wszystkie inne tematy w Fazie 13 stanowią jedynie rozwinięcie tej koncepcji.

## Koncepcja

### Krok 1: Opisz (Describe)

Host deklaruje każde dostępne narzędzie za pomocą trzech kluczowych pól:

- **Nazwa (Name):** Stały, unikalny identyfikator przyjazny dla kodu maszynowego, np. `get_weather` zamiast opisu słownego.
- **Opis (Description):** Zwięzła instrukcja w języku naturalnym objaśniająca modelowi cel użycia, np. „Użyj tego narzędzia, gdy użytkownik pyta o aktualne warunki pogodowe w konkretnym mieście. Nie używaj do pobierania danych historycznych”.
- **Schemat wejściowy (Input Schema):** Specyfikacja w formacie JSON Schema (wersja Draft 2020-12) opisująca oczekiwane argumenty wejściowe i ich typy.

Model otrzymuje tę listę deklaracji. Nowoczesne biblioteki klienckie automatycznie serializują te opisy do systemowego promptu modelu, dzięki czemu programista definiuje je w czystej, ustrukturyzowanej formie.

### Krok 2: Zdecyduj (Decide)

Na podstawie pytania użytkownika oraz listy zadeklarowanych narzędzi, model decyduje się na jeden z trzech kroków:

1. **Bezpośrednia odpowiedź tekstowa:** Model odpowiada użytkownikowi bez wywoływania narzędzi.
2. **Wywołanie narzędzi:** Model generuje jedno lub więcej wywołań. W konfiguracji z aktywnym parametrem `parallel_tool_calls: true` (domyślnie w OpenAI i Gemini, opcjonalnie w Anthropic) model może wygenerować kilka wywołań jednocześnie w jednej turze.
3. **Odmowa wykonania:** W trybie ścisłym (strict mode) model zamiast niepoprawnego wywołania może zwrócić jawny obiekt błędu `refusal`.

Ładunek wywołania narzędzia zawiera trzy pola: unikalny identyfikator wywołania (`id`), nazwę narzędzia (`name`) oraz obiekt JSON z wartościami argumentów (`arguments`). Unikalne ID pozwala hostowi na poprawne powiązanie zwracanych wyników z konkretnym wywołaniem, co ma kluczowe znaczenie przy przetwarzaniu równoległym.

### Krok 3: Wykonaj (Execute)

Host odbiera zgłoszenie od modelu, waliduje przesłane argumenty pod kątem zadeklarowanego schematu JSON Schema i uruchamia właściwy moduł wykonawczy (executor). Przekazanie niepoprawnych argumentów lub brakujących pól oznacza, że model wyhalucynował parametry – jest to częsty błąd w przypadku słabszych modeli. W środowiskach produkcyjnych host reaguje na błędy walidacji na trzy sposoby: natychmiast zgłasza wyjątek, próbuje automatycznie naprawić uszkodzony kod JSON (np. domykając klamry) lub odsyła informację o błędzie walidacji z powrotem do modelu, prosząc go o wygenerowanie poprawnego wywołania.

Sam moduł wykonawczy to standardowy kod aplikacyjny: funkcja w Pythonie/TypeScript, wywołanie komendy systemowej czy zapytanie SQL. Zwracany wynik jest najczęściej ciągiem znaków (np. JSON), ale może mieć też formę ustrukturyzowaną (np. obrazy lub odnośniki w protokole MCP). Wynik ten musi być w pełni serializowalny.

### Krok 4: Zaobserwuj (Observe)

Host dołącza rezultat wykonania do historii rozmowy (jako komunikat o roli `tool` z przypisanym identyfikatorem `id` wywołania) i ponownie przesyła historię do modelu. Model analizuje otrzymany wynik i podejmuje decyzję o wygenerowaniu kolejnych wywołań lub sformułowaniu ostatecznej odpowiedzi. Pętla ta kręci się do momentu, aż model zwróci odpowiedź tekstową lub host przerwie działanie po przekroczeniu limitu bezpieczeństwa.

### Klasyfikacja bezpieczeństwa (Rozłam zaufania)

Z punktu widzenia bezpieczeństwa aplikacji, narzędzia dzielimy na dwie kategorie:

- **Narzędzia czyste (Pure tools):** Działają w trybie tylko do odczytu, są deterministyczne i nie generują skutków ubocznych (np. `get_weather`, `search_docs`, `get_current_time`). Ich wywoływanie przez model jest w pełni bezpieczne.
- **Narzędzia wywołujące skutki uboczne (Consequential tools):** Zmieniają stan systemu, wiążą się z kosztami finansowymi lub modyfikują dane użytkownika (np. `send_email`, `delete_file`, `execute_trade`). Ich wywołanie wymaga ścisłego nadzoru.

Zgodnie z sformułowaną przez Meta w 2026 roku „zasadą dwóch” w bezpieczeństwie agentów, w ramach jednej tury interakcji mogą wystąpić maksymalnie dwa z trzech czynników ryzyka: niezaufane wejście, wrażliwe dane lub akcja o trwałych skutkach. Interfejs narzędzi pozwala na skuteczne egzekwowanie tej zasady poprzez wstrzymywanie wywołań krytycznych do czasu uzyskania ręcznego zatwierdzenia od użytkownika (human-in-the-loop). Szczegóły bezpieczeństwa omawia Lekcja 13.15, a uprawnienia agentów – Lekcja 14.09.

### Porównanie implementacji pętli

| Środowisko | Kto definiuje/opisuje | Kto podejmuje decyzję | Kto wykonuje akcję |
| :--- | :--- | :--- | :--- |
| **Function Calling (OpenAI/Anthropic/Gemini API)** | Programista aplikacji | Model LLM | Kod aplikacji (własny backend) |
| **Protokół MCP** | Serwer MCP | LLM za pośrednictwem klienta MCP | Serwer MCP |
| **Komunikacja A2A** | Protokół kart agenta (Agent cards) | Agent wywołujący | Agent wywoływany |
| **Przeglądarka (Web Agent)** | Rozszerzenie / WebMCP | Model LLM | Środowisko przeglądarki |

We wszystkich tych systemach proces przebiega tożsamo. Zmieniają się jedynie nazwy komponentów i protokołów komunikacji, ale sama struktura pozostaje nienaruszona.

### Dlaczego nie wystarczy zwykły prompt „Odpowiedz w formacie JSON”?

Metoda instructowa typu „generuj odpowiedź wyłącznie jako poprawny JSON” była powszechnie stosowana przed natywnym wdrożeniem interfejsów narzędziowych. Powodowała ona jednak błędy w 5–15% przypadków dla modeli wiodących i znacznie częściej dla modeli mniejszych. Typowe awarie to: brakujące nawiasy klamrowe, przecinki na końcu list, nieprawidłowe typy danych oraz ucieczka znaków specjalnych. Wymagało to pisania dodatkowego kodu naprawiającego JSON lub wielokrotnego ponawiania zapytań.

Natywny mechanizm Function Calling rozwiązuje te problemy z trzech powodów:
1. **Dedykowany trening:** Dostawcy trenują modele pod kątem generowania poprawnych struktur, co podnosi stabilność generowania JSON do poziomu 98–99% w trybie strict.
2. **Separacja protokołu:** Ładunek wywołania jest przesyłany w osobnym kanale protokołu, a nie w tekście odpowiedzi, co eliminuje wycieki kodu do interfejsu użytkownika.
3. **Wymuszenie schematu:** Dostawcy wymuszają zgodność z przekazanym schematem za pomocą dekodowania sterowanego gramatyką (np. strict mode w OpenAI, `responseSchema` w Gemini). Zgodność z typami danych jest w tym trybie gwarantowana matematycznie.

Różnice w API dostawców opisuje Lekcja 13.02, a zaawansowane generowanie struktur – Lekcja 13.04.

### Bezpieczniki pętli (Circuit Breakers)

Pętla sterowania musi mieć twarde ograniczenie liczby iteracji na wypadek, gdyby model wpadł w nieskończony cykl wywołań. Produkcyjne systemy ustawiają ten limit w przedziale od 5 do 20 kroków. Brak takiego ograniczenia może skutkować wygenerowaniem ogromnych rachunków za zużycie API w krótkim czasie. Przykładowo, edytor Cursor ogranicza pętlę agenta do 25 kroków, a moduł Asystentów OpenAI do 10 kroków.

Więcej o detekcji pętli i naprawianiu błędów dowiesz się z Lekcji 14.12, a o limitach wydajnościowych z Fazy 17.

## Zastosowanie w kodzie

Plik `code/main.py` zawiera kompletną symulację czteroetapowej pętli bez użycia zewnętrznych modeli LLM. Rolę „decydenta” pełni prosty parser dopasowujący wzorce tekstowe w pytaniu użytkownika. Mechanizm rejestracji, walidacja schematu oraz przesyłanie wyników (obserwacja) są w pełni funkcjonalne. Kod ten ułatwia zrozumienie przepływu danych i pozwala na łatwe podpięcie rzeczywistego modelu w kolejnych lekcjach.

Zwróć uwagę na:
- Rejestr narzędzi przechowujący nazwę, opis, schemat i referencję do funkcji wykonawczej.
- Uproszczoną walidację typów i wymaganych parametrów w oparciu o standardową bibliotekę Pythona.
- Zastosowanie sztywnego limitu 5 iteracji w pętli głównej (bezpiecznik).

## Rezultat

Do tej lekcji dołączono dokument `outputs/skill-tool-interface-reviewer.md`. Na podstawie roboczej specyfikacji narzędzia weryfikuje on poprawność jego definicji pod kątem stabilności nazwy, czytelności opisu dla modelu, zgodności ze specyfikacją JSON Schema Draft 2020-12 oraz klasyfikacji stopnia bezpieczeństwa (pure/consequential).

## Ćwiczenia

1. Zaimplementuj w pliku `code/main.py` nowe narzędzie `get_stock_price(ticker)`. Zdefiniuj jego opis: „Użyj tego narzędzia, gdy użytkownik pyta o aktualny kurs akcji na podstawie symbolu giełdowego (ticker). Nie używaj do pobierania danych historycznych ani podsumowań rynkowych”. Przetestuj działanie pętli dla pytań związanych z cenami akcji.
2. Spróbuj celowo wysłać do modułu wykonawczego wywołanie pozbawione jednego z wymaganych parametrów i upewnij się, że system odrzucił je na etapie walidacji. Jak powinien zareagować host, gdy w zapytaniu pojawi się nieznany parametr: odrzucić wywołanie czy zignorować dodatkowe pole? Uzasadnij odpowiedź z punktu widzenia bezpieczeństwa.
3. Przypisz do każdego narzędzia w rejestrze flagę `consequential: true` / `false` określającą, czy wywołuje ono skutki uboczne. Zmodyfikuj pętlę sterowania tak, aby przed wywołaniem każdego narzędzia krytycznego wyświetlała komunikat z prośbą o potwierdzenie akcji przez użytkownika.
4. Rozrysuj schemat czteroetapowej pętli i przypisz do poszczególnych ról komponenty ze swojego ulubionego środowiska programistycznego (np. edytor Cursor, asystenci w ChatGPT czy autorskie środowisko).
5. Zapoznaj się z oficjalną dokumentacją Function Calling w API OpenAI. Wskaż parametry żądania, które nie zostały ujęte w podstawowym schemacie czteroetapowej pętli, i wyjaśnij, jaką funkcję pełnią.

## Kluczowe pojęcia

| Termin | Potoczne określenie | Co to dokładnie oznacza |
| :--- | :--- | :--- |
| **Narzędzie (Tool)** | „Funkcja dla modelu” | Definicja składająca się z unikalnej nazwy, opisu w języku naturalnym, schematu wejściowego JSON Schema oraz powiązanej funkcji wykonawczej. |
| **Function Calling** | „Wywoływanie funkcji” | Natywne wsparcie na poziomie API dostawcy umożliwiające modelowi generowanie ustrukturyzowanych poleceń zamiast prozy. |
| **Wywołanie narzędzia** | „Tool Call / Payload” | Obiekt JSON wygenerowany przez model, zawierający unikalny identyfikator `id`, nazwę `name` oraz wartości argumentów `arguments`. |
| **Wynik narzędzia** | „Tool Result” | Odpowiedź z modułu wykonawczego przekazana z powrotem do modelu jako komunikat o roli `tool` z pasującym `id` wywołania. |
| **Równoległe wywołania** | „Parallel Tool Calls” | Zdolność modelu do zgłoszenia kilku wywołań w jednej turze, co przyspiesza działanie systemu. |
| **Tryb ścisły (Strict Mode)** | „Wymuszony schemat” | Blokada dekodowania modelu wymuszająca pełną zgodność wyjściowych tokenów ze strukturą zadeklarowanego schematu JSON Schema. |
| **Narzędzie czyste (Pure)** | „Tylko do odczytu” | Narzędzie bezskutkowe i deterministyczne; jego wywołanie jest bezpieczne i może być łatwo powtarzane. |
| **Narzędzie krytyczne (Consequential)** | „Narzędzie akcji” | Narzędzie modyfikujące stan zewnętrzny systemu; jego uruchomienie wymaga nadzoru, logowania lub autoryzacji użytkownika. |
| **Pętla czterostopniowa** | „Cykl sterowania agenta” | Niezmienny cykl operacyjny: Opisz → Zdecyduj → Wykonaj → Zaobserwuj. |
| **Host** | „Środowisko uruchomieniowe” | Główna aplikacja zarządzająca rejestrem narzędzi, przekazująca dane do modelu LLM i uruchamiająca powiązany kod aplikacyjny. |

## Literatura uzupełniająca

- [OpenAI — Function Calling Guide](https://platform.openai.com/docs/guides/function-calling) — Kanoniczne źródło wiedzy o strukturze deklaracji i wywołań w modelach OpenAI.
- [Anthropic — Tool Use Overview](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/overview) — Specyfikacja bloków `tool_use` / `tool_result` dla modeli z rodziny Claude.
- [Google — Gemini Function Calling](https://ai.google.dev/gemini-api/docs/function-calling) — Zasady deklaracji funkcji oraz obsługi wywołań równoległych w API Gemini.
- [Model Context Protocol — Specyfikacja 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25) — Otwarty standard komunikacji i współdzielenia narzędzi między modelami a serwerami zewnętrznymi.
- [JSON Schema — Draft 2020-12 Release Notes](https://json-schema.org/draft/2020-12/release-notes) — Dialekt zapisu struktur, w którym definiowane są argumenty wejściowe narzędzi.
