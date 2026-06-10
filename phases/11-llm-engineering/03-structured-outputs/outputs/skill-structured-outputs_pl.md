---

name: skill-structured-outputs
description: Ramy decyzyjne dotyczące wyboru właściwej strategii wyników strukturalnych w oparciu o dostawcę, niezawodność i złożoność
version: 1.0.0
phase: 11
lesson: 03
tags: [structured-output, json, schema, constrained-decoding, pydantic, function-calling]

---

# Strukturalna strategia wyjścia

Tworząc aplikację LLM wymagającą danych strukturalnych, zastosuj te ramy decyzyjne.

## Kiedy zastosować każde podejście

**Oparta na podpowiedziach („Zwróć JSON”):** Tylko prototypowanie. Dopuszczalne w przypadku narzędzi wewnętrznych, w których tolerowane są sporadyczne błędy analizy. Dodaj próbę/z wyjątkiem ponawiania próby. Nigdy nie stosować w rurociągach produkcyjnych.

**Tryb JSON (flaga API):** Potrzebujesz gwarantowanego prawidłowego formatu JSON, ale schemat jest prosty i elastyczny. Działa, gdy sprawdzasz kształt po stronie aplikacji. Dostępne: OpenAI, Anthropic (poprzez użycie narzędzi), Google.

**Tryb schematu (ograniczone dekodowanie):** Systemy produkcyjne, w których każdy wynik musi pasować do określonego schematu. Zero błędów analizy. Zero naruszeń schematu. Użyj tej opcji domyślnie w przypadku każdego zadania wyodrębniania lub klasyfikacji produkcji. Dostępne: wyniki strukturalne OpenAI, konspekty, wskazówki.

**Wywołanie funkcji/użycie narzędzia:** Model musi wybrać, którą funkcję wywołać, a nie tylko wypełnić parametry. Masz wiele schematów i model wybiera odpowiedni. Używaj również podczas integracji z istniejącą infrastrukturą narzędzi/funkcji.

**Biblioteka instruktorów:** Chcesz sprawdzić poprawność Pydantic z automatycznym ponawianiem prób u dowolnego dostawcy. Najlepszy DX dla projektów Python. Obejmuje modele OpenAI, Anthropic, Google i open source.

## Wskazówki specyficzne dla dostawcy

**OpenAI:** Użyj `response_format` z typem `json_schema`. Wbudowane jest dekodowanie z ograniczeniami. Modele Pydantic działają bezpośrednio. Najbardziej niezawodna implementacja ustrukturyzowanych wyników.

**Antropiczne:** Użyj narzędzi, aby uzyskać ustrukturyzowane wyniki. Zdefiniuj jedno narzędzie z żądanym schematem. Model zwraca argumenty wywołania narzędzia pasujące do schematu. Niezawodny, ale wymaga wzorca API użycia narzędzia.

**Modele open source (vLLM, Ollama):** Użyj zarysów lub wskazówek w przypadku ograniczonego dekodowania. Biblioteki te kompilują schematy JSON w maszyny o skończonym stanie, które maskują nieprawidłowe tokeny podczas generowania. Wymaga lokalnego uruchomienia wnioskowania.

## Wytyczne dotyczące projektowania schematu

1. Jeśli to możliwe, utrzymuj schematy płaskie. Zagnieżdżone obiekty znajdujące się powyżej 2 poziomów zwiększają błędy ekstrakcji.
2. Użyj wyliczeń dla pól kategorialnych. Nie polegaj na tym, że model wymyśli właściwy ciąg.
3. Ustaw jako wymagane niejednoznaczne pola z wyraźną obsługą wartości null, a nie jako opcjonalne. Zmusza model do podjęcia decyzji.
4. Dodaj opisy do właściwości schematu. Modelka odczytuje je jako instrukcje.
5. Unikaj typów unii (oneOf/anyOf), jeśli nie jest to konieczne. Zwiększają złożoność dekodowania.
6. Ustaw minimum/maksimum na liczbach. Łapie halucynacyjne wartości ekstremalne.
7. Użyj minItems/maxItems na tablicach, aby zapobiec pustym lub nieograniczonym wynikom.

## Typowe wzorce awarii i poprawki

- **Model otacza JSON w barierach przecen**: przełącz z trybu opartego na podpowiedzi do trybu JSON lub trybu schematu
- **Schemat prawidłowy, ale błędny pod względem faktycznym**: po wyodrębnieniu dodaj etap walidacji LLM jako sędzia
- **Niespójne wartości wyliczeniowe**: przełącz na dekodowanie ograniczone lub dodaj normalizację przetwarzania końcowego
- **Brakujące pola opcjonalne**: uczyń je wymaganymi lub dodaj wartości domyślne w kodzie aplikacji
- **Bardzo powolna ekstrakcja**: ograniczone dekodowanie dodaje 5-15% opóźnienia, zmniejsza złożoność schematu, jeśli jest wrażliwe na opóźnienia
- **Duże tablice z różnymi elementami**: podziel dane wejściowe i wyodrębnij poszczególne fragmenty, a następnie połącz wyniki

## Drabina niezawodności

| Podejście | Przeanalizuj sukces | Dopasowanie schematu | Wysiłek konfiguracyjny |
|--------------|------------|------------|------------|
| Oparte na podpowiedziach | ~90% | ~80% | 1 minuta |
| Tryb JSON | 100% | ~90% | 5 minut |
| Tryb schematu | 100% | ~99% | 15 minut |
| Ograniczone dekodowanie | 100% | 100% | 30 minut |
| Instruktor + ponowna próba | 100% | ~99,5% | 10 minut |