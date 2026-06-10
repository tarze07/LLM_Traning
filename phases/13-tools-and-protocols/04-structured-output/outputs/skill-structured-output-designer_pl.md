---

name: structured-output-designer
description: Zaprojektuj schemat JSON zgodny z trybem ścisłym i model Pydantic dla celu wyodrębniania dowolnego tekstu z wpisaną obsługą odmowy i ponawiania prób.
version: 1.0.0
phase: 13
lesson: 04
tags: [structured-output, json-schema, pydantic, strict-mode, extraction]

---

Biorąc pod uwagę cel wyodrębniania dowolnego tekstu (faktury, życiorysy, bilety pomocy technicznej, podsumowania badań), utwórz kontrakt na ekstrakcję gotową do produkcji: schemat JSON 2020-12, model Pydantic, procedura obsługi odmów i zasady ponawiania prób.

Wyprodukuj:

1. Schemat JSON 2020-12. Każda wpisana właściwość. `required` zawiera listę wszystkich nieruchomości. `additionalProperties: false` na każdym obiekcie. Wyliczenia używane dla zamkniętych zestawów wartości. Brak `$ref`. Brak niejednoznacznych `oneOf` / `anyOf`. Sprawdzone pod kątem wymagań trybu ścisłego OpenAI.
2. Model bazowy Pydantic v2. Lustro schematu z typami Pythona. `model_json_schema()` musi generować schemat równoważny (1).
3. Osoba zajmująca się odmową. Wpisano wynik `Refusal(reason: str, category: str)`. Wymień kategorie: `safety`, `input_mismatch`, `insufficient_info`.
4. Zasady ponawiania prób. Trzy kształty ponownych prób: (a) wstrzyknij błędy sprawdzania poprawności i spróbuj ponownie raz (poza trybem ścisłym); (b) przyjąć odmowę jako ostateczną (tryb ścisły); c) w przypadku powtarzającej się odmowy przejść do silniejszego modelu.
5. Wektory testowe. Dziesięć danych wejściowych obejmujących szczęśliwą ścieżkę, pola kontradyktoryjne, częściowe dane wejściowe i przypadek wywołujący odmowę. Każdy z oczekiwanym rezultatem.

Twarde odrzucenia:
- Dowolny schemat z polami bez typu. Nie działa zarówno tryb ścisły, jak i walidator.
- W każdym schemacie brakuje `additionalProperties: false`. Wycieka halucynacje.
- Dowolny schemat wykorzystujący `oneOf` bez pola dyskryminatora. Niejednoznaczne dekodowanie.
- Dowolny model Pydantic bez sprawdzania schematu JSON w obie strony.

Zasady odmowy:
- Jeżeli domena docelowa zawiera dane umożliwiające identyfikację bez udokumentowanego celu, odrzuć je i przejdź do fazy 18 (etyka), aby uzyskać argument dotyczący podstawy prawnej.
- Jeśli użytkownik poprosi o schemat, którego nie da się wyrazić w JSON Schema 2020-12 (np. rekurencyjne dowolne wykresy), odmów i zaproponuj najbliższe możliwe do wyrażenia rozluźnienie.
- Jeśli celem ekstrakcji jest „wydobywanie danych strukturalnych z czegokolwiek”, odmów i poproś o konkretną domenę.

Dane wyjściowe: jednostronicowy kontrakt ze schematem JSON, klasą Pydantic, polityką odmowy i ponawiania prób oraz dziesięcioma wektorami testowymi. Zakończ notatką na temat pierwszego dostawcy, na który chcesz kierować reklamy, i dlaczego.