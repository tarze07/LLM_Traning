---

name: structured-output-designer
description: Zaprojektuj schemat JSON zgodny z trybem ścisłym (Strict Mode) oraz model Pydantic do ekstrakcji ustrukturyzowanych danych z dowolnego tekstu, uwzględniając obsługę odmów i politykę ponawiania prób.
version: 1.0.0
phase: 13
lesson: 04
tags: [structured-output, json-schema, pydantic, strict-mode, extraction]

---

Na podstawie określonego celu ekstrakcji z dowolnego tekstu (faktury, CV, zgłoszenia serwisowe, streszczenia badań) utwórz gotowy do wdrożenia produkcyjnego kontrakt ekstrakcji: schemat JSON Schema 2020-12, model Pydantic, logikę obsługi odmów oraz zasady ponawiania prób.

Wygeneruj:

1. Schemat JSON 2020-12. Każda właściwość z określonym typem. `required` zawiera listę wszystkich właściwości. `additionalProperties: false` dla każdego obiektu. Wyliczenia (enums) użyte dla zamkniętych zbiorów wartości. Brak referencji `$ref`. Brak niejednoznacznych konstrukcji `oneOf` / `anyOf`. Schemat zweryfikowany pod kątem wymagań trybu ścisłego (Strict Mode) w OpenAI.
2. Model bazowy Pydantic v2. Odzwierciedlenie schematu przy użyciu typów Pythona. Metoda `model_json_schema()` musi generować schemat równoważny z punktem (1).
3. Obsługa odmów. Zdefiniuj strukturę wyniku `Refusal(reason: str, category: str)`. Kategorie do uwzględnienia: `safety`, `input_mismatch`, `insufficient_info`.
4. Polityka ponawiania prób. Trzy warianty postępowania: (a) wstrzyknięcie błędów walidacji do promptu i pojedyncza ponowna próba (poza trybem ścisłym); (b) uznanie odmowy za ostateczną (w trybie ścisłym); (c) w przypadku powtarzających się odmów – przełączenie na silniejszy model.
5. Wektory testowe. Dziesięć zestawów danych testowych obejmujących: przypadek poprawny (happy path), dane testowe z elementami kontradyktoryjnymi (adversarial inputs), dane niekompletne oraz przypadek wywołujący odmowę. Każdy z nich z oczekiwanym wynikiem.

Kryteria odrzucenia (Twarde reguły):
- Przesłanie schematu zawierającego pola bez określonego typu (uniemożliwia to poprawne działanie trybu ścisłego oraz walidatora).
- Brak ustawienia `additionalProperties: false` w dowolnym miejscu schematu (powoduje to generowanie wyhalucynowanych pól).
- Stosowanie konstrukcji `oneOf` bez jawnego pola dyskryminatora (powoduje to niejednoznaczności przy dekodowaniu).
- Brak weryfikacji zgodności modelu Pydantic ze schematem JSON (brak testu round-trip).

Zasady odmowy usługi:
- Odmów, jeśli domena docelowa obejmuje dane osobowe (PII) bez jasno udokumentowanego celu biznesowego, i skieruj użytkownika do fazy 18 (etyka i prawo) w celu opracowania podstawy prawnej.
- Jeśli użytkownik poprosi o schemat, którego nie da się wyrazić w standardzie JSON Schema 2020-12 (np. rekurencyjne grafy o dowolnej strukturze), odmów i zaproponuj najbliższe realizowalne uproszczenie.
- Odmów, jeśli zdefiniowanym celem ekstrakcji jest ogólne „wydobywanie danych strukturalnych z dowolnego tekstu”, i poproś o sprecyzowanie konkretnej domeny.

Format wyjściowy: Jednostronicowy kontrakt zawierający schemat JSON, definicję klasy Pydantic, politykę obsługi odmów i ponawiania prób oraz dziesięć wektorów testowych. Na końcu dodaj informację o rekomendowanym dostawcy chmurowym dla tego zadania wraz z uzasadnieniem.
