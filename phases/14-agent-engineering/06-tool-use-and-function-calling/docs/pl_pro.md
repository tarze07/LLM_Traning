# Wykorzystanie narzędzi i wywoływanie funkcji (Function Calling)

> Publikacja Toolformer (Schick i in., 2023) zapoczątkowała samonadzorowane dodawanie adnotacji do wywołań narzędzi w danych treningowych. Berkeley Function Calling Leaderboard V4 (Patil i in., 2025) wyznacza standardy na rok 2026 w oparciu o kryteria: 40% zadań agentowych, 30% wieloturowych (multi-turn), 10% testów na żywo (live), 10% testów syntetycznych (non-live) oraz 10% testów na halucynacje. Wywoływanie funkcji w pojedynczej turze (single-turn) uznaje się za problem rozwiązany. Wyzwaniem pozostają jednak: zarządzanie pamięcią, dynamiczne podejmowanie decyzji oraz długofalowe łańcuchy wywołań narzędzi.

**Typ:** Kompilacja
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 14 · 01 (pętla agenta), faza 13 · 01 (funkcja wywołująca głębokie nurkowanie)
**Czas:** ~60 minut

## Cele nauczania

- Wyjaśnij mechanizm samonadzorowanego uczenia w Toolformerze: zachowywanie adnotacji o wywołaniu narzędzia tylko wtedy, gdy wynik jego wykonania zmniejsza stratę (loss) kolejnego tokena.
- Wymień pięć kategorii oceny w benchmarku BFCL V4 i opisz, co każda z nich mierzy.
- Zaimplementuj rejestr narzędzi przy użyciu biblioteki standardowej (stdlib) z obsługą walidacji schematów, konwersją argumentów oraz bezpiecznym środowiskiem wykonawczym (sandbox).
- Zidentyfikuj i przeanalizuj trzy główne wyzwania: długofalowe sekwencje wywołań narzędzi, dynamiczne podejmowanie decyzji oraz zarządzanie pamięcią.

## Problem

Początkowo kluczowym pytaniem było: czy model potrafi poprawnie wygenerować wywołanie pojedynczej funkcji? Obecnie wyzwanie brzmi inaczej: czy model potrafi łączyć narzędzia w sekwencje liczące 40 kroków, zarządzając pamięcią w warunkach częściowej obserwowalności środowiska, radząc sobie z awariami narzędzi oraz unikając halucynowania nieistniejących API?

Toolformer udowodnił, że modele mogą samodzielnie uczyć się momentu wywoływania narzędzi poprzez samonadzór. Benchmark BFCL V4 wyznacza cele ewaluacji – różnica między nimi obrazuje skok jakościowy, jaki dokonał się w kierunku produkcyjnych wdrożeń agentowych.

## Koncepcja

### Toolformer (Schick i in., NeurIPS 2023)

Koncepcja: Pozwól modelowi samodzielnie nanosić adnotacje o wywołaniach API na własnym korpusie treningowym. Dla każdej próby uruchom powiązane narzędzie. Zachowaj adnotację w zbiorze treningowym tylko wtedy, gdy dołączenie wyniku działania narzędzia zmniejsza stratę (loss) przy przewidywaniu kolejnych tokenów. Następnie dostrój model na tak przefiltrowanym korpusie.

Objęte narzędzia: kalkulator, system kontroli jakości, wyszukiwarki, tłumacz, kalendarz. Sygnał samonadzoru dotyczy wyłącznie tego, czy narzędzie pomaga przewidzieć tekst, a nie ludzkich etykiet.

Efekt skali: Zdolność do korzystania z narzędzi pojawia się jako właściwość emergentna przy odpowiedniej skali modelu. Małe modele radziły sobie gorzej po dodaniu adnotacji o narzędziach, natomiast większe wykazywały znaczne korzyści. Z tego powodu wiodące modele (frontier models) mają natywne wsparcie dla wywoływania funkcji, podczas gdy mniejsze modele klasy 7B wymagają dedykowanego dostrojenia (fine-tuningu) w tym obszarze, aby działać stabilnie.

### Berkeley Function Calling Leaderboard, wersja 4 (Patil i in., ICML 2025)

BFCL to de facto standard ewaluacji. Struktura wersji V4 obejmuje:

- **Zadania agentowe (40%)** – kompletne ścieżki działania: obsługa pamięci, interakcje wieloturowe, dynamiczne decyzje.
- **Interakcje wieloturowe (30%)** – wieloetapowe dialogi połączone z sekwencyjnym wywoływaniem narzędzi.
- **Testy na żywo (10%)** – autentyczne prompty użytkowników (trudniejszy, naturalny rozkład danych).
- **Testy syntetyczne (10%)** – predefiniowane scenariusze testowe.
- **Halucynacje (10%)** – weryfikacja zdolności modelu do powstrzymania się od wywołania narzędzia, gdy żadne nie pasuje.

W wersji V3 wprowadzono ocenę opartą na weryfikacji stanu (state-based evaluation): po zakończeniu sekwencji wywołań system sprawdza faktyczny stan środowiska lub API (np. „czy plik został fizycznie utworzony?”), zamiast jedynie porównywać drzewo składniowe (AST) wygenerowanego kodu. W wersji V4 dodano dodatkowo testy wyszukiwania informacji w sieci, obsługi pamięci oraz wrażliwości na format danych.

Kluczowy wniosek: Wywoływanie funkcji w pojedynczym kroku (single-turn) jest problemem niemal całkowicie rozwiązanym. Błędy modeli dotyczą głównie: zarządzania pamięcią (przenoszenie kontekstu między turami), dynamicznego podejmowania decyzji (dobór narzędzi w oparciu o wyniki poprzednich kroków), długofalowego planowania (utrata spójności po ponad 20 krokach) oraz eliminacji halucynacji (brak wywołania narzędzia, gdy brak pasującego API w katalogu).

### Schemat narzędzia

Każdy dostawca ma schemat. Różnią się szczegółami, ale mają ten sam kształt:

```
name: string
description: string (what it does, when to use it)
input_schema: JSON Schema (properties, required, types, enums)
```

Anthropic używa bezpośrednio `input_schema`. OpenAI używa `function.parameters`. Oba akceptują schemat JSON. Opisy parametrów i samych funkcji mają kluczowe znaczenie – to na ich podstawie model decyduje o wyborze odpowiedniego narzędzia. Niedokładne lub niejasne opisy są najczęstszą przyczyną błędnego doboru narzędzi przez modele.

### Walidacja argumentu

Nigdy nie ufaj wygenerowanym argumentom bez weryfikacji. Sprawdź:

1. **Konwersja typów (Type coercion)**: Model może przesłać wartość tekstową `"5"`, mimo że schemat oczekuje liczby całkowitej (int). Wykonaj konwersję, jeśli intencja jest jasna; w przeciwnym razie odrzuć żądanie.
2. **Walidacja wartości wyliczeniowych (Enum validation)**: Jeśli dopuszczalne wartości to `status in {"open", "closed"}`, a model zwraca `"in_progress"`, odrzuć wywołanie i zgłoś czytelny komunikat o błędzie.
3. **Wymagane pola (Required fields)**: W przypadku braku wymaganego pola zwróć informację o błędzie bezpośrednio do modelu (jako wynik działania narzędzia), zamiast przerywać działanie całego programu.
4. **Sprawdzanie formatu**: Adresy e-mail, URL czy daty należy weryfikować przy użyciu dedykowanych parserów, a nie wyłącznie za pomocą prostych wyrażeń regularnych.

Każdy błąd walidacji powinien generować ustrukturyzowany komunikat zwrotny, co umożliwi modelowi skorygowanie argumentów i ponowne wywołanie narzędzia z poprawnymi danymi.

### Równoległe wywołania narzędzi

Współcześni dostawcy obsługują równoległe wywołania narzędzi w jednej turze asystenta. Pętla:

1. Model emituje 3 wywołania narzędzi z różnymi `tool_use_id`s.
2. Runtime wykonuje je (równolegle, jeśli są niezależne).
3. Każdy wynik wraca jako blok `tool_result` skorelowany przez `tool_use_id`.

Wskazówka implementacyjna: Identyfikatory powiązań (correlation IDs) są kluczowe. Ich pomieszanie spowoduje przypisanie wyników do niewłaściwych wywołań narzędzi.

### Piaskownica

Uruchomienie narzędzia wyznacza granicę bezpiecznej piaskownicy (sandbox). Szczegółowe instrukcje znajdziesz w Lekcji 09. W skrócie: każde narzędzie powinno mieć ściśle zdefiniowane uprawnienia odczytu/zapisu, dostęp do sieci, limity czasu wykonania oraz pamięci. Ogólne wywołania typu `run_shell(cmd)` stanowią poważne zagrożenie bezpieczeństwa; znacznie bezpieczniejsze są wyspecjalizowane funkcje, np. `git_status()`.

## Zbuduj to

Plik `code/main.py` implementuje rejestr narzędzi o strukturze zbliżonej do wdrożeń produkcyjnych:

- Parser i walidator podzbioru schematu JSON (oparty wyłącznie na bibliotece standardowej).
- Rejestr narzędzi zawierający opisy, schematy wejściowe, limity czasu i funkcje wykonawcze.
- Automatyczną konwersję argumentów oraz weryfikację wartości enum.
- Równoległe uruchamianie narzędzi z obsługą identyfikatorów powiązań.
- Generowanie ustrukturyzowanych komunikatów o błędach.

Uruchomienie:

```
python3 code/main.py
```

Ślad wykonania prezentuje działanie mini-agenta, który wywołuje trzy narzędzia w pojedynczym kroku. Jedno z wywołań celowo zawiera błędne argumenty, co skutkuje zwróceniem czytelnego komunikatu o błędzie, na podstawie którego model jest w stanie samodzielnie skorygować zapytanie.

## Użyj tego

Każdy dostawca chmurowy stosuje własny format definicji narzędzi (Anthropic, OpenAI, Gemini, Bedrock). W projektach wielomodelowych zaleca się stosowanie warstwy abstrakcji, np. Vercel AI SDK, adapterów LangChain lub SDK OpenAI Agents. Przed wdrożeniem produkcyjnym systemu mocno opierającego się na wywoływaniu funkcji warto przetestować go na zadaniach wzorowanych na benchmarku BFCL.

## Wyślij to

Plik `outputs/skill-tool-registry.md` opisuje proces budowania katalogu narzędzi, definiowania schematów oraz rejestracji funkcji dla wybranej domeny. Obejmuje również kryteria weryfikacji opisów (np. czy opis narzędzia jasno wskazuje modelowi właściwy moment jego użycia).

## Ćwiczenia

1. Add do rejestru narzędzie puste („no-op”), które pozwala modelowi w jawny sposób zrezygnować z wywoływania jakichkichkolwiek akcji. Przetestuj to rozwiązanie w scenariuszach weryfikacji halucynacji (wzorem BFCL).
2. Zaimplementuj automatyczną konwersję argumentów przekazanych jako ciąg znaków na typy numeryczne (int, float). W jakich przypadkach taka automatyczna korekta może maskować krytyczne błędy w działaniu modelu?
3. Wprowadź limity czasu wykonania (timeout) dla każdego narzędzia oraz mechanizm bezpiecznika (circuit breaker), który blokuje wywoływanie danego API na 60 sekund po 3 z rzędu awariach. Jak wpływa to na zdolność agenta do samonaprawy?
4. Zapoznaj się ze specyfikacją BFCL V4. Wybierz jedną z kategorii testowych (np. interakcje wieloturowe), przetestuj 10 przykładowych scenariuszy na swoim agencie i oblicz wskaźnik sukcesu (pass rate).
5. Zastąp uproszczony walidator oparty na bibliotece standardowej biblioteką Pydantic lub Zod. Jakie błędy w schematach i argumentach są wykrywane przez te biblioteki, a zostały pominięte w prostym rozwiązaniu?

## Kluczowe terminy

| Termin | Potoczne określenie | Co to w rzeczywistości oznacza |
|------|----------------|--------------------------------------|
| Function Calling | „Wykorzystanie narzędzi” | Wywoływanie zewnętrznych funkcji zwracających ustrukturyzowane dane zgodnie ze zdefiniowanym schematem. |
| Toolformer | „Samonadzorowane uczenie narzędzi” | Podejście (Schick i in., 2023) polegające na trenowaniu modelu na wywołaniach, które realnie obniżają stratę (loss) kolejnego tokena. |
| BFCL | „Benchmark Berkeley” | Kompleksowy zestaw testowy (V4) obejmujący zadania agentowe, dialogi wieloturowe, zapytania na żywo oraz testy na halucynacje. |
| Schemat narzędzia | „Sygnatura funkcji” | Definicja zawierająca nazwę, opis działania oraz schemat JSON parametrów wejściowych narzędzia. |
| tool_use_id | „Identyfikator powiązania” | Unikalny klucz łączący konkretne wywołanie narzędzia z jego rezultatem, kluczowy przy przetwarzaniu równoległym. |
| Wykrywanie halucynacji | „Odmawianie wywołania” | Zdolność modelu do powstrzymania się przed uruchomieniem jakiejkolwiek funkcji, jeśli żadna nie pasuje do kontekstu. |
| Konwersja argumentów | „Naprawa typów” | Automatyczne korygowanie drobnych rozbieżności w typach danych (np. konwersja string na int) na podstawie schematu. |
| Piaskownica (Sandbox) | „Izolacja wykonania” | Ograniczenie uprawnień narzędzia w zakresie zapisu/odczytu, sieci oraz limitów zasobów (pamięć, procesor). |

## Dalsze czytanie

- [Schick i in., Toolformer (arXiv:2302.04761)](https://arxiv.org/abs/2302.04761) — adnotacja dotycząca narzędzia samonadzorowanego
- [Tabela liderów wywołań funkcji Berkeley (V4)](https://gorilla.cs.berkeley.edu/leaderboard.html) – test porównawczy eval 2026
- [Anthropic, dokumentacja użycia narzędzi](https://platform.claude.com/docs/en/agent-sdk/overview) — schemat narzędzia produkcyjnego w pakiecie SDK Claude Agent
- [Dokumentacja pakietu SDK OpenAI Agents](https://openai.github.io/openai-agents-python/) — typ narzędzia funkcyjnego i poręcze
