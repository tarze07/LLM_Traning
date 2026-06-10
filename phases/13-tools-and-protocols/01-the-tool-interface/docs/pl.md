# Interfejs narzędzia — dlaczego agenci potrzebują strukturalnych operacji we/wy

> Model językowy tworzy tokeny. Program podejmuje działania. Luką pomiędzy nimi jest interfejs narzędzia: kontrakt, który pozwala modelowi zażądać akcji, a host ją wykonać. Każdy stos 2026 — funkcja wywołująca OpenAI, Anthropic i Gemini; `tools/call` MCP; Części zadań A2A — to inne kodowanie tej samej czteroetapowej pętli. Ta lekcja nazywa pętlę i pokazuje minimalną maszynerię, która ją uruchamia.

**Typ:** Ucz się
**Języki:** Python (stdlib, bez LLM)
**Wymagania wstępne:** Faza 11 (interfejsy API ukończenia LLM)
**Czas:** ~45 minut

## Cele nauczania

- Wyjaśnij, dlaczego LLM, który może generować jedynie tekst, nie może samodzielnie podejmować działań przeciwko światu rzeczywistemu.
- Narysuj czteroetapową pętlę wywołań narzędzi (opisz → zdecyduj → wykonaj → obserwuj) i podaj, kto jest właścicielem każdego kroku.
- Napisz opis narzędzia składający się z trzech części: nazwy, danych wejściowych schematu JSON i deterministycznej funkcji executora.
- Rozróżnij narzędzia czyste i powodujące skutki uboczne i wyjaśnij, dlaczego podział ma znaczenie dla bezpieczeństwa.

## Problem

LLM emituje rozkład prawdopodobieństwa dla następnego tokena. To jest cała powierzchnia wyjściowa. Jeśli zapytasz model czatu „Jaka jest teraz pogoda w Bengaluru”, może on napisać wiarygodne zdanie, ale nie może połączyć się z interfejsem API pogody. Zdanie może być trafne przez przypadek lub przeterminowane o trzy dni.

Zamknięcie tej luki jest celem interfejsu narzędzia. Program hosta — środowisko wykonawcze agenta, Claude Desktop, ChatGPT, Cursor lub skrypt niestandardowy — ogłasza modelowi listę możliwych do wywołania narzędzi. Kiedy model zdecyduje, że potrzebne jest działanie, emituje ustrukturyzowany ładunek zawierający nazwę narzędzia i jego argumentów. Host analizuje ten ładunek, naprawdę uruchamia narzędzie i przekazuje wynik. Pętla trwa, dopóki model nie zdecyduje, że nie są już potrzebne żadne dalsze wywołania.

Pierwsza wersja tej umowy została wysłana w czerwcu 2023 r. jako parametr „funkcji” OpenAI. Następnie Anthropic zawierał bloki `tool_use` w Claude 2.1. Gemini dodał `functionDeclarations` kilka miesięcy później. Każdy dostawca udostępnia teraz ten sam kształt: lista narzędzi typu JSON-Schema, wywołanie narzędzia zawierającego ładunek JSON. W protokole Model Context Protocol (listopad 2024 r.) uogólniono umowę, tak aby jeden rejestr narzędzi obsługiwał każdy model. A2A (kwiecień 2026 r., wersja 1.0) nakładała ten sam element podstawowy na potrzeby delegowania między agentami.

Czterostopniowa pętla jest niezmiennikiem pod nimi wszystkimi. Wszystko inne w fazie 13 jest opracowaniem.

## Koncepcja

### Krok pierwszy: opisz

Host deklaruje każde narzędzie za pomocą trzech pól.

- **Nazwa.** Stabilny, czytelny maszynowo identyfikator. `get_weather`, a nie „rzecz pogodowa”.
- **Opis.** Jednoakapitowy brief w języku naturalnym. „Używaj, gdy użytkownik pyta o aktualne warunki dla konkretnego miasta. Nie używaj w przypadku danych historycznych.”
- **Schemat wejściowy.** Obiekt JSON Schema (wersja robocza 2020-12) opisujący argumenty narzędzia.

Model otrzymuje listę. Współcześni dostawcy serializują te deklaracje w wierszu poleceń systemu, korzystając z szablonu specyficznego dla dostawcy, więc jako osoba dzwoniąca masz do czynienia tylko z formularzem strukturalnym.

### Krok drugi: zdecyduj

Biorąc pod uwagę przekaz użytkownika i dostępne narzędzia, model wybiera jedno z trzech zachowań.

1. **Odpowiedz bezpośrednio** SMS-em. Brak wezwania narzędzia.
2. **Wywołaj jedno lub więcej narzędzi.** Emituj obiekty wywołań strukturalnych. W ramach `parallel_tool_calls: true` (domyślnie w OpenAI i Gemini, opcja włączenia w Anthropic) model może emitować wiele wywołań w jednej turze.
3. **Odmów.** Ustrukturyzowane wyjścia w trybie ścisłym mogą zamiast wywołania wygenerować wpisany blok `refusal`.

Ładunek wywołania narzędzia ma trzy stabilne pola: wywołanie `id`, narzędzie `name` i obiekt JSON `arguments`. Identyfikator istnieje, aby host mógł powiązać późniejszy wynik z konkretnym wywołaniem, co ma znaczenie, gdy połączenia równoległe nie działają.

### Krok trzeci: wykonaj

Host odbiera wywołanie, sprawdza argumenty względem zadeklarowanego schematu i uruchamia moduł wykonujący. Nieprawidłowe argumenty oznaczają, że model wywołał halucynację pola lub użył niewłaściwego typu — bardzo częsty tryb awarii w słabych modelach. Hosty produkcyjne wykonują jedną z trzech rzeczy w przypadku nieprawidłowych argumentów: szybko kończą się niepowodzeniem i ujawniają błąd w modelu, naprawiają kod JSON za pomocą ograniczonego analizatora składni lub ponawiają próbę stworzenia modelu z błędem sprawdzania poprawności zawartym w monicie.

Sam executor jest zwykłym kodem. Python, TypeScript, polecenie powłoki, zapytanie do bazy danych. Generuje wynik, który zwykle jest ciągiem znaków, ale może to być dowolna wartość JSON lub blok treści strukturalnej (tekst, obraz lub odwołanie do zasobu w MCP). Wynik musi nadawać się do serializacji.

### Krok czwarty: obserwuj

Host dołącza wynik narzędzia do konwersacji (jako komunikat roli `tool` z pasującym `id`) i ponownie wywołuje model. Model ma teraz wyniki narzędzia w kontekście i może dać ostateczną odpowiedź lub zażądać większej liczby połączeń. Dzieje się tak do momentu, gdy model przestanie emitować wywołania lub host osiągnie limit bezpieczeństwa liczby iteracji.

### Rozłam zaufania

Narzędzia są dostępne w dwóch wersjach, które mają znaczenie dla bezpieczeństwa.

- **Pure.** Tylko do odczytu, deterministyczny, bez skutków ubocznych. `get_weather`, `search_docs`, `get_current_time`. Bezpiecznie jest dzwonić spekulacyjnie.
- **Konsekwencje.** Zmienia stan, wydaje pieniądze, dotyka danych użytkownika. `send_email`, `delete_file`, `execute_trade`. Musi być ogrodzony.

„Zasada dwóch” Meta z 2026 r. dotycząca bezpieczeństwa agentów mówi, że w jednej turze mogą wystąpić co najwyżej dwa z następujących czynników: niezaufane dane wejściowe, wrażliwe dane i wynikające z nich działania. Interfejs narzędzia umożliwia egzekwowanie tej reguły — poprzez odrzucanie połączeń, wymaganie potwierdzenia od użytkownika lub eskalację zakresów. Zobacz fazę 13 · 15, aby zapoznać się z rozdziałem dotyczącym pełnego bezpieczeństwa i fazę 14 · 09, aby zapoznać się z zasadami uprawnień na poziomie agenta.

### Gdzie znajduje się pętla

| Kontekst | Kto opisuje | Kto decyduje | Kto wykonuje |
|--------|---------------|------------|-------------|
| Wywoływanie funkcji jednym obrotem (OpenAI/Anthropic/Gemini) | Twórca aplikacji | LLM | Twórca aplikacji |
| MCP | Serwer MCP | LLM za pośrednictwem klienta MCP | Serwer MCP |
| A2A | Wydawca kart agenta | Agent telefoniczny | Wezwany agent |
| Przeglądarka internetowa (agent wywołujący funkcje) | Rozszerzenie przeglądarki / WebMCP | LLM | Środowisko wykonawcze przeglądarki |

Wszędzie te same cztery kroki. Nazwy kolumn zmieniają się; struktura nie.

### Dlaczego po prostu nie poprosić modelu o emisję JSON?

„Poproś model o odpowiedź w JSON” był wzorcem poprzedzającym wywołanie funkcji. Zawodzi w ~5 do 15 procentach przypadków w modelach pionierskich i znacznie częściej w mniejszych modelach. Tryby awarii obejmują brakujące nawiasy klamrowe, końcowe przecinki, pola halucynacyjne i nieprawidłowe typy. Następnie potrzebujesz przepustki naprawy JSON, ponownej próby lub ograniczonego dekodera.

Natywne wywoływanie funkcji jest lepsze z trzech powodów. Po pierwsze, dostawca kompleksowo szkoli model pod kątem dokładnego kształtu wywołania, dzięki czemu współczynnik poprawności JSON wzrasta do 98–99 procent w trybie ścisłym. Po drugie, ładunek wywołania znajduje się we własnym gnieździe protokołu, a nie w wolnym tekście — więc wywołanie narzędzia nigdy nie wycieka do odpowiedzi widocznej dla użytkownika. Po trzecie, dostawcy wymuszają zgodność schematu z ograniczonym dekodowaniem (tryb ścisły OpenAI, `tool_use` firmy Anthropic, `responseSchema` firmy Gemini). Dane wyjściowe są gwarantowane.

Faza 13 · 02 przedstawia interfejsy API trzech dostawców obok siebie. Faza 13 · 04 obejmuje szczegółowe wyniki ustrukturyzowane.

### Wyłączniki automatyczne

Pętla kończy się, gdy model przestanie emitować wywołania lub host osiągnie maksymalną liczbę tur. Gospodarze produkcji ustawiają to na od 5 do 20 tur. Poza tym prawie na pewno znajdujesz się w pętli, z której model nie może wyjść. Kod Claude'a domyślnie wynosi 20; Asystentów OpenAI do 10; Tryb agenta kursora na 25.

Alternatywa — nieograniczone pętle — pojawia się co sześć miesięcy, gdy sekcja zwłok „agent wydał 400 dolarów na wywołania API w ciągu jednej nocy”. Nie wysyłaj bez ograniczeń.

Faza 14 · 12 obejmuje dogłębne usuwanie błędów i samonaprawę; Faza 17 obejmuje limity wydajności produkcji.

### Dokąd zmierza faza 13

- Lekcje od 02 do 05 dopracowują powierzchnię wywołań narzędzi na poziomie dostawcy.
- Lekcje od 06 do 14 uogólniają pętlę na MCP.
- Lekcje od 15 do 18 chronią pętlę przed wrogimi serwerami, wrogimi użytkownikami i nieuwierzytelnionymi zdalnymi powierzchniami uwierzytelniającymi.
- Lekcje od 19 do 22 rozszerzają wzorzec na współpracę między agentami, obserwowalność, wyznaczanie tras i pakowanie.
- Lekcja 23 przedstawia kompletny ekosystem wykorzystujący każdy prymityw.

Każda pozostała lekcja jest rozwinięciem tej czteroetapowej pętli. Zapamiętaj to jako niezmiennik.

## Użyj tego

`code/main.py` uruchamia czteroetapową pętlę bez LLM. Fałszywa funkcja „decydująca” symuluje model poprzez dopasowywanie wzorców w wiadomości użytkownika; executor, walidator schematu i wiązka kroków obserwacji są rzeczywiste. Uruchom go, aby zobaczyć pełną choreografię żądania/odpowiedzi z możliwym do wydrukowania stanem pośrednim, a następnie w późniejszej lekcji zastąp fałszywy element decyzyjny dowolnym prawdziwym dostawcą.

Na co zwrócić uwagę:

- Rejestr narzędzi zawiera trzy pola na każde narzędzie: nazwę, opis, schemat i odnośnik do wykonawcy.
- Walidator to minimalny podzbiór schematu JSON (typy, wymagane, wyliczenie, min/max) napisany tylko w stdlib. Faza 13 · 04 dostarcza pełniejszą.
- Pętla ogranicza liczbę iteracji do pięciu. Agenci produkcyjni potrzebują właśnie tego rodzaju wyłącznika.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-tool-interface-reviewer.md`. Biorąc pod uwagę roboczą definicję narzędzia (nazwa + opis + schemat + konspekt wykonawcy), umiejętność sprawdza ją pod kątem zgodności z pętlą: czy nazwa jest stabilna maszynowo, czy opis jest kompletnym opisem użycia, czy schemat poprawnie korzysta ze schematu JSON 2020-12 i czy wyraźna jest klasyfikacja czysta czy wynikowa.

## Ćwiczenia

1. Dodaj czwarte narzędzie do `code/main.py` o nazwie `get_stock_price(ticker)`. Zapisz jego opis w następujący sposób: „Użyj, gdy użytkownik pyta o aktualny kurs akcji za pomocą tickera. Nie używaj w przypadku cen historycznych lub podsumowań rynkowych”. Uruchom uprząż i potwierdź fałszywe zapytania dotyczące tras decyzyjnych, wspominające o znacznikach do nowego narzędzia.

2. Złam walidator schematu. Przekaż wywołanie, w którym w obiekcie `arguments` brakuje wymaganego pola i potwierdź, że host je odrzucił przed wykonaniem. Następnie przekaż połączenie z dodatkowym nieznanym polem. Zdecyduj: czy gospodarz powinien odrzucić czy zignorować? Uzasadnij swój wybór argumentem bezpieczeństwa.

3. Sklasyfikuj każde narzędzie w uprzęży jako czyste lub wtórne. Dodaj flagę `consequential: true` do wpisów rejestru, które jej potrzebują, i zmień pętlę tak, aby wyświetlała wiersz „potwierdziłby z użytkownikiem” za każdym razem, gdy wybrane zostanie kolejne narzędzie. To jest kształt bramki potwierdzenia, którego potrzebuje każdy gospodarz produkcyjny.

4. Narysuj czteroetapową pętlę na papierze, wypełniając powyższą tabelę kolumn dostawców dla swojego ulubionego klienta (Claude Desktop, Cursor, ChatGPT lub stos niestandardowy). Odsyłacz do wariantu specyficznego dla MCP w fazie 13 · 06.

5. Przeczytaj od góry do dołu przewodnik wywoływania funkcji OpenAI. Zidentyfikuj jedno pole, które znajduje się w żądaniu, ale nie w czteroetapowej pętli, jak pokazano tutaj. Wyjaśnij, co dodaje i dlaczego jest to wygodne, a nie niezbędne.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Narzędzie | „Rzecz, którą modelka może nazwać” | Potrójna nazwa + dane wejściowe typu JSON-Schema + funkcja executora |
| Wywołanie funkcji | „Natywne użycie narzędzia” | Obsługa API na poziomie dostawcy do emitowania wywołań narzędzi strukturalnych zamiast prozy |
| Wywołanie narzędzia | „Prośba modelki o działanie” | Ładunek JSON zawierający `id`, `name`, `arguments` emitowany przez model |
| Wynik narzędzia | „Co zwróciło narzędzie” | Dane wyjściowe modułu wykonującego zapakowane w komunikat roli `tool` z pasującym identyfikatorem |
| Równoległe wywołania narzędzi | „Wiele połączeń na raz” | Wiele obiektów wywoławczych w jednym modelu, niezależnych i możliwych do uporządkowania według identyfikatora |
| Tryb ścisły | „Gwarantowany JSON” | Ograniczone dekodowanie, które wymusza sprawdzenie danych wyjściowych modelu względem zadeklarowanego schematu |
| Czyste narzędzie | „Narzędzie tylko do odczytu” | Brak skutków ubocznych; można bezpiecznie uruchomić ponownie |
| Konsekwentne narzędzie | „Narzędzie działania” | Mutuje stan zewnętrzny; wymaga potwierdzenia bramki, audytu lub użytkownika |
| Pętla czterostopniowa | „Cykl wywołania narzędzia” | opisz → zdecyduj → wykonaj → obserwuj |
| Gospodarz | „Środowisko wykonawcze agenta” | Program przechowujący rejestr narzędzi, wywołujący model i uruchamiający executor |

## Dalsze czytanie

- [OpenAI — przewodnik wywoływania funkcji](https://platform.openai.com/docs/guides/function-calling) — kanoniczne odniesienie do deklaracji narzędzi w stylu OpenAI i kształtów wywołań
– [Anthropic — przegląd użycia narzędzi](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/overview) — format blokowy `tool_use` / `tool_result` Claude'a
- [Google — wywoływanie funkcji Gemini](https://ai.google.dev/gemini-api/docs/function-calling) — `functionDeclarations` i semantyka wywołań równoległych w Gemini
- [Model Context Protocol — Specyfikacja 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25) — uogólnienie interfejsu narzędzia niezależne od dostawcy
- [Schemat JSON — informacje o wersji 2020-12](https://json-schema.org/draft/2020-12/release-notes) — dialekt schematu, którym mówi każde nowoczesne narzędzie API