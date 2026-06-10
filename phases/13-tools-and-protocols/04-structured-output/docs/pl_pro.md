# Ustrukturyzowane dane wyjściowe — schemat JSON, Pydantic, Zod, dekodowanie z ograniczeniami

> Nakłonienie modelu do zwrócenia formatu JSON poprzez instrukcje w prompcie (tzw. "JSON mode") kończy się niepowodzeniem w 5–15% przypadków, nawet przy użyciu najlepszych modeli komercyjnych (frontier models). Ustrukturyzowane dane wyjściowe (Structured Outputs) rozwiązują ten problem dzięki dekodowaniu z ograniczeniami (constrained decoding) – model ma technicznie uniemożliwione wygenerowanie tokenu, który naruszałby zdefiniowany schemat. Tryb ścisły (Strict Mode) w OpenAI, wywoływanie narzędzi oparte na schematach w Anthropic, `responseSchema` w Gemini, `output_type` w Pydantic AI oraz `.parse` w bibliotece Zod to po prostu różne implementacje tej samej idei. W tej lekcji omówimy walidację schematów oraz kontrakty w trybie ścisłym, które są niezbędne w każdym produkcyjnym procesie ekstrakcji danych.

**Typ:** Kompilacja
**Języki:** Python (biblioteka standardowa, podzbiór JSON Schema 2020-12)
**Wymagania:** Faza 13 · 02 (Głębokie nurkowanie w wywoływanie funkcji)
**Czas:** ~75 minut

## Cele nauczania

- Napisz schemat JSON (w wersji Draft 2020-12) dla celów ekstrakcji, wykorzystując odpowiednie ograniczenia (`enum`, min/max, pola wymagane, `pattern`).
- Wyjaśnij, dlaczego tryb ścisły (Strict Mode) i dekodowanie z ograniczeniami dają lepsze gwarancje niż walidacja wykonywana po wygenerowaniu odpowiedzi.
- Rozróżnij trzy tryby awarii: błąd parsowania (parse error), naruszenie schematu (schema violation) oraz odmowę modelu (model refusal).
- Wdróż proces ekstrakcji danych wyposażony w mechanizmy automatycznej naprawy błędów oraz obsługę odmowy ze strony modelu.

## Problem

Agent analizujący treść wiadomości e-mail z zamówieniem musi przekształcić tekst w ustrukturyzowany format `{customer, line_items, total_usd}`. Porównajmy trzy podejścia:

**Podejście pierwsze: wymuszenie JSON w prompcie.** „Odpowiedz w formacie JSON z polami customer, line_items, total_usd”. Przy użyciu najlepszych modeli działa to w 85–95% przypadków. Może jednak zawieść na wiele sposobów: brakujący nawias klamrowy, nadmiarowy przecinek na końcu, nieprawidłowe typy danych, zmyślone (halucynowane) pola, ucięcie tekstu z powodu limitu tokenów lub generowanie zbędnego komentarza (np. „Oto Twój JSON:”).

**Podejście drugie: walidacja po wygenerowaniu.** Model generuje odpowiedź swobodnie, po czym host ją parsuje, waliduje pod kątem schematu i w razie błędu podejmuje kolejną próbę. Rozwiązanie to jest niezawodne, ale kosztowne – płacisz za każdą ponowną próbę, a błędy powodujące ucięcie generowanej odpowiedzi kosztują dodatkową turę zapytania.

**Podejście trzecie: dekodowanie z ograniczeniami.** Dostawca API wymusza zgodność ze schematem bezpośrednio podczas dekodowania. Niepoprawne tokeny są maskowane w rozkładzie prawdopodobieństwa próbkowania. Gwarantuje to, że dane wyjściowe zawsze dadzą się sparsować i będą zgodne ze schematem. Jedynym możliwym trybem awarii jest odmowa modelu (gdy model uzna, że dane wejściowe nie pasują do schematu).

W 2026 roku każdy wiodący dostawca oferuje jakąś formę podejścia trzeciego:

- **OpenAI.** Parametr `response_format: {type: "json_schema", strict: true}` oraz pole `refusal` w odpowiedzi, jeśli model odmówi wykonania zadania.
- **Anthropic.** Wymuszanie schematu na wejściach narzędzi (`tool_use`); brak dedykowanego statusu `stop_reason: "refusal"`, ale sygnałem odmowy jest zakończenie tury (`end_turn`) bez wywołania narzędzia.
- **Gemini.** Opcja `responseSchema` na poziomie żądania. Od 2026 roku Gemini dostarcza ograniczenia gramatyczne na poziomie tokenów dla wybranych typów danych.
- **Pydantic AI.** Parametr `output_type=InvoiceModel` zwraca ustrukturyzowany obiekt `RunResult` rzutowany na klasę `InvoiceModel`.
- **Zod (TypeScript).** Parser uruchomieniowy weryfikujący wyjście dostawcy ze schematem Zod; integruje się z metodą `beta.chat.completions.parse` w OpenAI.

Wspólny mianownik: zdefiniuj schemat raz i egzekwuj go na każdym etapie.

## Koncepcja

### Schemat JSON 2020–12 — wspólny standard

Wszyscy główni dostawcy akceptują format JSON Schema w wersji Draft 2020-12. Najczęściej używane elementy to:

- `type`: jeden z typów: `object`, `array`, `string`, `number`, `integer`, `boolean`, `null`.
- `properties`: mapowanie nazw pól na ich podschematy.
- `required`: lista pól, które muszą obowiązkowo wystąpić.
- `enum`: zamknięta lista dozwolonych wartości.
- `minimum` / `maximum` (dla liczb), `minLength` / `maxLength` / `pattern` (dla ciągów znaków).
- `items`: podschemat określający elementy w tablicy.
- `additionalProperties`: wartość `false` zabrania przekazywania nieznanych pól (domyślne zachowanie różni się w zależności od trybu).

Tryb ścisły (Strict Mode) w OpenAI wprowadza dodatkowe wymagania: każde pole musi być zadeklarowane w tablicy `required`, należy ustawić `additionalProperties: false` oraz zabronione jest stosowanie nierozstrzygniętych referencji `$ref`. Naruszenie tych reguł spowoduje zwrócenie błędu HTTP 400 już na etapie wysyłania zapytania.

### Pydantic – integracja z Pythonem

Pydantic v2 automatycznie generuje schemat JSON na podstawie klas Pythona dziedziczących po `BaseModel` za pomocą metody `model_json_schema()`. Pydantic AI ułatwia ten proces:

```python
class Invoice(BaseModel):
    customer: str
    line_items: list[LineItem]
    total_usd: Decimal
```

Framework tłumaczy tak zdefiniowany model na tryb ścisły OpenAI, `input_schema` w Anthropic lub `responseSchema` w Gemini. Odpowiedź z modelu jest automatycznie zwracana jako instancja klasy `Invoice`. Błędy walidacji wywołują wyjątek `ValidationError` zawierający dokładne ścieżki do niepoprawnych pól.

### Zod – integracja z TypeScriptem

Zod (`z.object({customer: z.string(), ...})`) jest odpowiednikiem biblioteki Pydantic w świecie TypeScriptu. Oficjalny pakiet SDK OpenAI dla Node.js udostępnia funkcję `zodResponseFormat(Invoice)`, która automatycznie konwertuje schemat Zod na format oczekiwany przez API.

### Odmowy (Refusals)

Tryb ścisły nie zmusza modelu do udzielenia odpowiedzi za wszelką cenę. Jeśli dane wejściowe nie pasują do schematu (np. e-mail zawiera wiersz zamiast faktury), model zwróci pole `refusal` zawierające powód odmowy. Kod aplikacji powinien traktować taką odmowę jako standardowy, poprawny wynik działania programu, a nie błąd systemu. Odmowa jest także kluczowa dla bezpieczeństwa: jeśli poprosisz model o wyodrębnienie numeru karty kredytowej z wiadomości zawierającej wrażliwe treści, model zwróci odmowę z podaniem przyczyny bezpieczeństwa.

### Dekodowanie z ograniczeniami w modelach Open-Source

W przypadku lokalnych modeli typu open-source stosuje się trzy główne techniki:

1. **Dekodowanie gramatyczne** (biblioteki `outlines`, `guidance`, `lm-format-enforcer`): na podstawie schematu buduje się deterministyczny automat skończony (FSM); na każdym kroku generowania maskuje się wartości logits dla tokenów, które naruszyłyby strukturę automatu.
2. **Maskowanie logitów za pomocą parsera JSON**: uruchamia się strumieniowy parser JSON równolegle z modelem, określając zestaw dopuszczalnych kolejnych tokenów na każdym etapie.
3. **Dekodowanie spekulatywne z weryfikatorem**: mniejszy i szybszy model pomocniczy proponuje tokeny, które są następnie zatwierdzane lub odrzucane przez weryfikator pilnujący schematu.

Dostawcy chmurowi wdrażają te metody pod maską. Obecnie (rok 2026) te techniki pozwalają na szybsze generowanie krótkich ustrukturyzowanych danych niż przy tradycyjnym generowaniu swobodnym, zachowując zbliżoną wydajność dla długich odpowiedzi.

### Trzy tryby awarii

1. **Błąd parsowania (Parse Error).** Wygenerowany tekst nie jest poprawnym kodem JSON. W trybie ścisłym (Strict Mode) ten błąd nie występuje. Może się jednak zdarzyć u dostawców, którzy nie korzystają z dekodowania z ograniczeniami.
2. **Naruszenie schematu (Schema Violation).** JSON został sparsowany poprawnie, ale nie spełnia reguł schematu (np. brak wymaganych pól lub niepoprawne typy). Niemożliwe w trybie ścisłym, bardzo częste bez niego.
3. **Odmowa (Refusal).** Model odmawia przetworzenia zapytania ze względów bezpieczeństwa lub z powodu niedopasowania treści. Powinna być obsługiwana jako poprawny typ wyniku.

### Strategia ponawiania prób (Retry Strategy)

Poza trybem ścisłym (np. przy wywoływaniu narzędzi w Anthropic lub starszych wersjach Gemini) stosuje się następujący schemat naprawczy:

```
generowanie -> parsowanie -> walidacja -> w razie błędu dodaj opis błędu do promptu i spróbuj ponownie (maks. 3 razy)
```

Zazwyczaj wystarcza jedna ponowna próba. Trzykrotne powtórzenie pozwala wyeliminować losowe błędy modelu. Jeśli błąd występuje częściej niż trzy razy, najprawdopodobniej oznacza to błąd w samym schemacie – model nie jest w stanie go spełnić dla danych wejściowych i należy poprawić prompt lub strukturę schematu.

### Wydajność na małych modelach

Dekodowanie z ograniczeniami doskonale sprawdza się na małych modelach. Lokalny model o rozmiarze 3B parametrów z wymuszoną gramatyką potrafi generować bardziej niezawodne ustrukturyzowane dane niż model 70B sterowany wyłącznie instrukcjami w prompcie. Jest to główny powód, dla którego ustrukturyzowane dane wyjściowe są tak ważne w systemach produkcyjnych: pozwalają oddzielić niezawodność aplikacji od rozmiaru modelu.

## Instrukcja użycia

Plik `code/main.py` zawiera uproszczony walidator schematów JSON Schema 2020-12 napisany w czystym Pythonie (obsługuje typy, pola wymagane, `enum`, min/max, wzorce regex, tablice oraz `additionalProperties`). Walidator weryfikuje zasymulowane odpowiedzi LLM pod kątem schematu `Invoice`, prezentując obsługę błędów parsowania, naruszeń schematu oraz ścieżek odmowy. W warunkach produkcyjnych zasymulowane dane należy zastąpić rzeczywistymi odpowiedziami z API.

Na co warto zwrócić uwagę:

- Walidator zwraca listę obiektów `ValidationError` zawierających ścieżkę do błędu oraz jego opis. Taki format błędu doskonale nadaje się do wstrzyknięcia do promptu przy ponownej próbie.
- W przypadku odmowy (refusal) system nie podejmuje kolejnej próby, lecz rejestruje odmowę i zwraca ją jako wynik. Faza 14 · 09 pokazuje, jak wykorzystać odmowę jako sygnał bezpieczeństwa.
- Próba przesłania nadmiarowych pól wywołuje błąd `additionalProperties: false`, co pokazuje, jak tryb ścisły zapobiega halucynowaniu dodatkowych kluczy w JSON.

## Wynik wdrożenia

W ramach tej lekcji powstaje plik `outputs/skill-structured-output-designer.md`. Narzędzie to analizuje wymagania dotyczące ekstrakcji danych z tekstu (faktury, zgłoszenia serwisowe, CV itp.) i generuje poprawny schemat JSON Schema 2020-12 (zgodny z trybem ścisłym OpenAI), odpowiadający mu model Pydantic w Pythonie oraz logikę obsługi odmów i ponawiania prób.

## Ćwiczenia

1. Uruchom `code/main.py`. Dodaj czwarty przypadek testowy, w którym pole `total_usd` ma wartość ujemną. Upewnij się, że walidator odrzuci te dane z powodu ograniczenia `minimum`.

2. Rozbuduj walidator o obsługę słowa kluczowego `oneOf` z dyskryminatorem. Typowy scenariusz: element faktury (`line_item`) może być produktem lub usługą, oznaczonym polem `kind`. Tryb ścisły OpenAI ma w tym przypadku specyficzne ograniczenia; szczegóły znajdziesz w dokumentacji OpenAI dla ustrukturyzowanych danych wyjściowych.

3. Zdefiniuj ten sam schemat faktury jako klasę Pydantic (`BaseModel`) i porównaj strukturę wygenerowaną przez `model_json_schema()` z ręcznie napisanym schematem. Wskaż jedno pole dodawane automatycznie przez Pydantic, które zostało pominięte w wersji ręcznej.

4. Zmierz odsetek odmów modelu. Przygotuj 10 tekstów wejściowych, które nie powinny zostać zakwalifikowane do ekstrakcji (np. tekst piosenki, dowód matematyczny, pusta wiadomość) i wyślij je do modelu w trybie ścisłym. Zlicz, ile razy model poprawnie odmówił wykonania zadania, a ile razy wyhalucynował dane. Pomoże Ci to w zaprojektowaniu obsługi odmów.

5. Przeczytaj uważnie dokumentację ustrukturyzowanych danych wyjściowych OpenAI. Zidentyfikuj jedną funkcję schematu JSON, która jest zabroniona w trybie ścisłym (Strict Mode), mimo że jest poprawna w standardzie JSON Schema. Następnie zaprojektuj schemat wykorzystujący ten zabroniony element i zrefaktoryzuj go tak, aby był w pełni kompatybilny z trybem ścisłym.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Schemat JSON 2020-12 | „Specyfikacja schematu” | Standard zapisu schematów JSON akceptowany przez nowoczesne API |
| Tryb ścisły (Strict Mode) | „Gwarancja schematu” | Flaga OpenAI wymuszająca zgodność ze schematem na poziomie generowania |
| Dekodowanie z ograniczeniami | „Maskowanie logitów” | Technika blokowania tokenów naruszających zdefiniowaną gramatykę |
| Odmowa (Refusal) | „Brak odpowiedzi” | Poprawny typ wyniku zwracany, gdy model nie może przetworzyć danych wejściowych |
| Błąd parsowania | „Niepoprawny JSON” | Dane wyjściowe nie są poprawnym formatem JSON; niemożliwe w trybie ścisłym |
| Naruszenie schematu | „Zły kształt” | JSON jest poprawny składniowo, ale łamie ograniczenia typów lub zakresów |
| `additionalProperties: false` | „Brak dodatkowych pól” | Ograniczenie zabraniające generowania nieznanych pól; wymagane w trybie ścisłym OpenAI |
| Model bazowy Pydantic | „Klasa walidująca” | Klasa Pythona definiująca strukturę i sprawdzająca poprawność danych |
| Schemat Zod | „Typowanie w TS” | Biblioteka TypeScript służąca do walidacji danych w czasie uruchomienia |
| Egzekwowanie gramatyki | „Ograniczenia dla modeli lokalnych” | Maskowanie logitów na podstawie FSM stosowane w modelach open-source (np. Outlines) |

## Dalsze czytanie

- [OpenAI — Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs) — tryb ścisły, obsługa odmów i specyfikacja schematu.
- [OpenAI — Introducing Structured Outputs](https://openai.com/index/introducing-structured-outputs-in-the-api/) — oficjalne ogłoszenie z sierpnia 2024 roku wyjaśniające techniczne gwarancje dekodowania.
- [Pydantic AI — Outputs](https://ai.pydantic.dev/output/) — mapowanie typów wyjściowych na modele różnych dostawców.
- [JSON Schema — Draft 2020-12 Release Notes](https://json-schema.org/draft/2020-12/release-notes) — oficjalna specyfikacja standardu.
- [Microsoft — Structured Outputs w Azure OpenAI](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/structured-outputs) — wskazówki i ograniczenia dotyczące stosowania trybu ścisłego w systemach korporacyjnych.
