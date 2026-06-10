---

name: skill-structured-outputs
description: Ramy decyzyjne wyboru optymalnej strategii generowania ustrukturyzowanych danych wyjściowych w zależności od dostawcy API, wymagań niezawodności oraz stopnia złożoności.
version: 1.0.0
phase: 11
lesson: 03
tags: [structured-output, json, schema, constrained-decoding, pydantic, function-calling]

---

# Strategia generowania ustrukturyzowanych danych wyjściowych

Projektując aplikację LLM, która wymaga danych ustrukturyzowanych, postępuj zgodnie z poniższymi ramami decyzyjnymi.

## Kiedy stosować poszczególne podejścia

**Podejście oparte na promptach („Zwróć JSON”):** Wyłącznie do prototypowania. Dopuszczalne w wewnętrznych narzędziach pomocniczych, gdzie sporadyczne błędy parsowania są akceptowalne. Wymaga wdrożenia obsługi wyjątków (try-catch) i mechanizmu ponawiania prób. Nigdy nie stosuj w produkcyjnych potokach danych (pipelines).

**Tryb JSON (flaga API / Response Format):** Gdy wymagany jest poprawnie sformatowany plik JSON, ale sam schemat struktury jest prosty lub elastyczny. Sprawdza się w scenariuszach, gdy walidacja struktury odbywa się po stronie aplikacji. Dostępność: OpenAI, Anthropic (poprzez Tool Use), Google.

**Tryb schematu (dekodowanie z ograniczeniami / Structured Outputs):** Systemy produkcyjne, w których każdy wynik bezwzględnie musi być zgodny ze zdefiniowanym schematem. Eliminuje do zera błędy parsowania i naruszenia struktury. Powinien być domyślnym wyborem dla wszelkich produkcyjnych zadań ekstrakcji danych lub klasyfikacji. Wsparcie: OpenAI (Structured Outputs), biblioteki Outlines, Guidance.

**Wywoływanie funkcji (Function Calling) / Tool Use:** Gdy model musi samodzielnie zdecydować, którą funkcję wywołać, a nie tylko wypełnić wskazany schemat parametrów. Stosuj również przy integracji z istniejącą infrastrukturą narzędziową lub API.

**Biblioteka Instructor:** Gdy chcesz wykorzystać walidację za pomocą Pydantic wraz z automatycznym ponawianiem prób dla dowolnego dostawcy API. Zapewnia doskonały komfort deweloperski (DX) w ekosystemie Pythona. Wspiera modele OpenAI, Anthropic, Gemini oraz modele Open Source.

## Wskazówki specyficzne dla dostawcy

**OpenAI:** Użyj parametru `response_format` o typie `json_schema` (Structured Outputs). Dekodowanie z ograniczeniami (constrained decoding) jest realizowane natywnie na poziomie API. Wspiera bezpośrednie przekazywanie modeli Pydantic. Obecnie najbardziej niezawodna implementacja ustrukturyzowanych danych wyjściowych na rynku.

**Anthropic:** Wykorzystaj mechanizm narzędzi (Tool Use). Zdefiniuj jedno dedykowane narzędzie z oczekiwanym schematem. Model zwróci argumenty wywołania pasujące do schematu. Rozwiązanie stabilne, ale wymaga obsługi formatu API dla narzędzi.

**Modele Open Source (vLLM, Ollama):** Wykorzystaj biblioteki Outlines lub Guidance do dekodowania z ograniczeniami. Narzędzia te kompilują schematy JSON do automatów skończonych (FSM), które dynamicznie maskują niedozwolone tokeny podczas generowania tekstu. Wymaga to własnej infrastruktury inferencyjnej.

## Wytyczne dotyczące projektowania schematu

1. Projektuj jak najpłatsze schematy. Zagnieżdżenie obiektów na głębokość większą niż 2 poziomy drastycznie zwiększa ryzyko błędów ekstrakcji.
2. Stosuj typy wyliczeniowe (enum) dla pól kategorycznych. Nie oczekuj, że model sam wpisze poprawny tekst bez ograniczeń.
3. Zamiast pól opcjonalnych, stosuj pola wymagane z jawną możliwością przypisania wartości `null`. Zmusza to model do podjęcia świadomej decyzji.
4. Dodawaj opisy (description) do poszczególnych właściwości schematu. Model traktuje te opisy jak instrukcje wykonawcze.
5. Unikaj typów unii (oneOf/anyOf), o ile nie jest to absolutnie konieczne. Zwiększają one złożoność procesu dekodowania.
6. Definiuj wartości minimalne i maksymalne (minimum/maximum) dla pól liczbowych. Pomaga to zapobiec halucynacjom skrajnych wartości.
7. Stosuj ograniczenia `minItems` oraz `maxItems` dla tablic, aby zapobiec generowaniu pustych lub nieskończonych list.

## Typowe błędy i metody ich naprawy

- **Model umieszcza JSON w blokach kodu markdown**: przejdź z podejścia opartego na promptach na tryb JSON lub tryb schematu (Structured Outputs).
- **Struktura poprawna, ale dane są niezgodne z prawdą (halucynacje)**: po ekstrakcji dodaj etap walidacji za pomocą innego modelu w roli sędziego (LLM-as-a-judge).
- **Niezgodne lub zniekształcone wartości enum**: przejdź na dekodowanie z ograniczeniami lub dodaj moduł normalizacji w postprocessingu.
- **Pomiń opcjonalne pola**: zdefiniuj je jako wymagane i obsłuż wartości domyślne bezpośrednio w aplikacji.
- **Wydłużony czas ekstrakcji**: dekodowanie z ograniczeniami dodaje ok. 5–15% narzutu czasowego (latency); w systemach wrażliwych na opóźnienia uprość strukturę schematu.
- **Olbrzymie tablice z różnorodnymi elementami**: podziel dane wejściowe na mniejsze fragmenty (batching), wyodrębnij dane dla każdego z nich osobno, a następnie scal wyniki w aplikacji.

## Porównanie strategii niezawodności

| Strategia | Skuteczność parsowania | Zgodność ze schematem | Czas wdrożenia |
|--------------|------------|------------|------------|
| Oparta na promptach | ~90% | ~80% | 1 minuta |
| Tryb JSON | 100% | ~90% | 5 minut |
| Tryb schematu | 100% | ~99% | 15 minut |
| Dekodowanie z ograniczeniami | 100% | 100% | 30 minut |
| Instructor + ponawianie prób | 100% | ~99,5% | 10 minut |
