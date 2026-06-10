# Ustrukturyzowane dane wyjściowe — schemat JSON, Pydantic, Zod, dekodowanie ograniczone

> Opcja „Poproś model o zwrócenie JSON” kończy się niepowodzeniem w 5–15 procentach przypadków, nawet w przypadku modeli granicznych. Ustrukturyzowane dane wyjściowe wypełniają tę lukę dzięki ograniczonemu dekodowaniu: modelowi dosłownie uniemożliwia się emisję tokena, który naruszałby schemat. Tryb ścisły OpenAI, użycie narzędzi opartych na schemacie firmy Anthropic, `responseSchema` firmy Gemini, `output_type` firmy Pydantic AI i `.parse` firmy Zod to pięć powierzchniowych form tego samego pomysłu. W tej lekcji omówiono moduł sprawdzania poprawności schematu i kontrakty w trybie ścisłym, których uczestnicy kursu będą używać dla każdego potoku ekstrakcji produkcyjnej.

**Typ:** Kompilacja
**Języki:** Python (stdlib, podzbiór JSON Schema 2020-12)
**Wymagania:** Faza 13 · 02 (funkcja wywołująca głębokie nurkowanie)
**Czas:** ~75 minut

## Cele nauczania

- Napisz schemat JSON 2020-12 dla celu ekstrakcji, używając odpowiednich ograniczeń (wyliczenie, min./maks., wymagane, wzorzec).
- Wyjaśnij, dlaczego tryb ścisły i dekodowanie ograniczone dają inne gwarancje niż „weryfikacja po wygenerowaniu”.
- Rozróżnij trzy tryby awarii: błąd analizy, naruszenie schematu, odmowa modelu.
- Wysłać rurociąg ekstrakcyjny z typową naprawą i typową obsługą odmowy.

## Problem

Agent czytający wiadomość e-mail z zamówieniem musi zamienić dowolny tekst na `{customer, line_items, total_usd}`. Trzy podejścia.

**Podejście pierwsze: monit o podanie JSON.** „Odpowiedz w JSON z polami klient, elementy_liniowe, suma_usd.” Działa od 85 do 95 procent czasu w modelach pionierskich. Zawodzi na sześć sposobów: brak nawiasu klamrowego, końcowy przecinek, nieprawidłowe typy, halucynacyjne pola, obcięcie przy limicie tokenów, wyciekła proza, np. „Oto twój JSON:”.

**Podejście drugie: weryfikacja po wygenerowaniu.** Generuj swobodnie, analizuj, sprawdzaj poprawność względem schematu, ponów próbę w przypadku niepowodzenia. Niezawodny, ale drogi — płacisz za każdą ponowną próbę, a błędy powodujące obcięcie kosztują jedną dodatkową turę za każde wystąpienie.

**Podejście trzecie: dekodowanie ograniczone.** Dostawca wymusza schemat w czasie dekodowania. Nieprawidłowe tokeny są maskowane w rozkładzie próbkowania. Dane wyjściowe są gwarantowane do przeanalizowania i sprawdzenia poprawności. Niepowodzenie zapada się w jeden tryb: odmowę (model stwierdza, że ​​dane wejściowe nie pasują do schematu).

Każdy dostawca graniczny w 2026 r. dostarcza jakąś formę podejścia trzeciego.

- **OpenAI.** `response_format: {type: "json_schema", strict: true}` plus `refusal` w odpowiedzi w przypadku odrzucenia modelu.
- **Anthropic.** Wymuszanie schematu na wejściach `tool_use`; `stop_reason: "refusal"` nie jest rzeczą, ale `end_turn` bez wywołania narzędzia jest sygnałem.
- **Gemini.** `responseSchema` na poziomie żądania; w 2026 r. Gemini dostarcza ograniczenia gramatyczne na poziomie tokena dla wybranych typów.
- **Pydantic AI.** `output_type=InvoiceModel` emituje ustrukturyzowany `RunResult` wpisany do `InvoiceModel`.
- **Zod (TypeScript).** Parser środowiska wykonawczego, który sprawdza dane wyjściowe dostawcy względem schematu Zod; łączy się z `beta.chat.completions.parse` OpenAI.

Wspólny wątek: zadeklaruj schemat raz, wyegzekwuj go od końca do końca.

## Koncepcja

### Schemat JSON 2020–12 — lingua franca

Każdy dostawca akceptuje schemat JSON 2020-12. Konstrukcje, których najczęściej używasz:

- `type`: jeden z `object`, `array`, `string`, `number`, `integer`, `boolean`, `null`.
- `properties`: mapowanie nazwy pola na podschemat.
- `required`: lista nazw pól, które muszą się pojawić.
- `enum`: zamknięty zbiór dozwolonych wartości.
- `minimum` / `maximum` (liczby), `minLength` / `maxLength` / `pattern` (ciągi znaków).
- `items`: podschemat zastosowany do każdego elementu tablicy.
- `additionalProperties`: `false` zabrania dodatkowych pól (wartość domyślna różni się w zależności od trybu).

Tryb ścisły OpenAI dodaje trzy wymagania: każda właściwość musi być wymieniona wszędzie w `required`, `additionalProperties: false` i nie może być żadnych nierozwiązanych `$ref`. Jeśli je złamiesz, interfejs API zwróci 400 w momencie żądania.

### Pydantic, wiązanie Pythona

Pydantic v2 generuje schemat JSON na podstawie modeli w kształcie klasy danych za pośrednictwem `model_json_schema()`. Pydantic AI zamyka to, więc piszesz:

```python
class Invoice(BaseModel):
    customer: str
    line_items: list[LineItem]
    total_usd: Decimal
```

a struktura agenta tłumaczy schemat na tryb ścisły OpenAI, Anthropic `input_schema` lub Gemini `responseSchema` na krawędzi. Dane wyjściowe modelu są zwracane w postaci wpisanej instancji `Invoice`. Błędy sprawdzania poprawności zgłaszają `ValidationError` z wpisanymi ścieżkami błędów.

### Zod, wiązanie TypeScriptu

Zod (`z.object({customer: z.string(), ...})`) jest odpowiednikiem TS. Pakiet SDK Node OpenAI udostępnia `zodResponseFormat(Invoice)`, co przekłada się na ładunek schematu JSON interfejsu API.

### Odmowy

Tryb ścisły nie może zmusić modelu do odpowiedzi. Jeśli dane wejściowe nie pasują do schematu („e-mail był wierszem, a nie fakturą”), model emituje pole `refusal` zawierające przyczynę. Twój kod musi sobie z tym poradzić jako wynik najwyższej klasy, a nie porażkę. Odmowa jest również przydatna jako sygnał bezpieczeństwa: modelka poproszona o wyodrębnienie numeru karty kredytowej z wiadomości e-mail zawierającej chronioną treść zwraca odmowę z załączoną przyczyną bezpieczeństwa.

### Ograniczone dekodowanie na otwartej przestrzeni

Implementacje wag otwartych wykorzystują trzy techniki.

1. **Dekodowanie gramatyczne** (`outlines`, `guidance`, `lm-format-enforcer`): zbuduj deterministyczny automat skończony ze schematu; na każdym kroku maskuj logity tokenów, które naruszałyby FSM.
2. **Maskowanie logitu za pomocą parsera JSON**: uruchom parser przesyłania strumieniowego JSON na wzór modelu; na każdym kroku obliczaj zestaw ważnych następnych tokenów.
3. **Dekodowanie spekulatywne z weryfikatorem**: tani model roboczy proponuje tokeny, weryfikator wymusza schemat.

Dostawcy komercyjni wybierają jedną z nich za kulisami. Stan wiedzy na rok 2026 jest szybszy niż zwykłe generowanie w przypadku krótkich wyników strukturalnych i mniej więcej taką samą prędkość w przypadku długich.

### Trzy tryby awarii

1. **Błąd analizy.** Dane wyjściowe nie są prawidłowym kodem JSON. Nie może się to zdarzyć w trybie ścisłym. Nadal może się to zdarzyć w przypadku dostawców, którzy nie są rygorystyczni.
2. **Naruszenie schematu.** Dane wyjściowe są analizowane, ale naruszają schemat. Nie może się to zdarzyć w trybie ścisłym. Powszechne poza nim.
3. **Odmowa.** Modelka odmawia. Należy traktować jako wynik wpisany.

### Strategia ponów próbę

Kiedy jesteś poza trybem ścisłym (użycie narzędzi antropicznych, nieścisłe OpenAI, starsze Gemini), schemat odzyskiwania jest następujący:

```
generate -> parse -> validate -> if fail, inject error and retry, max 3x
```

Zwykle wystarczy jedna ponowna próba. Trzy próby wyłapują płatki słabego modelu. Wartość powyżej trzech oznacza zły schemat: model nie jest w stanie spełnić tego warunku w przypadku niektórych danych wejściowych i monit lub schemat wymaga naprawy.

### Obsługa małych modeli

Ograniczone dekodowanie działa na małych modelach. Otwarty model z parametrami 3B i wymuszaniem gramatyki przewyższa model z parametrami 70B z surowymi podpowiedziami dotyczącymi zadań strukturalnych. Jest to główny powód, dla którego ustrukturyzowane wyniki mają znaczenie dla produkcji: oddziela to niezawodność od wielkości modelu.

## Użyj tego

`code/main.py` dostarcza minimalny walidator schematu JSON 2020-12 w stdlib (typy, wymagane, wyliczenie, min/max, wzorzec, elementy, dodatkowe właściwości). Opakowuje schemat `Invoice` i uruchamia fałszywe dane wyjściowe LLM przez moduł sprawdzania poprawności, demonstrując błąd analizy, naruszenie schematu i ścieżki odmowy. Zamień fałszywe dane wyjściowe na prawdziwą reakcję dowolnego dostawcy w produkcji.

Na co zwrócić uwagę:

- Walidator zwraca wpisaną listę `[ValidationError]` ze ścieżką i komunikatem. To jest kształt, który chcesz wyświetlić w monicie o ponowienie próby.
- Oddział odmowy NIE podejmuje ponownej próby. Rejestruje i zwraca wpisaną odmowę. Faza 14 · 09 wykorzystuje odmowę jako sygnał bezpieczeństwa.
- Sprawdzanie `additionalProperties: false` uruchamia się na wejściu testu kontradyktoryjnego, pokazując, dlaczego tryb ścisły zamyka drzwi dla pól halucynacyjnych.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-structured-output-designer.md`. Biorąc pod uwagę cel wyodrębniania dowolnego tekstu (faktury, bilety pomocy technicznej, życiorysy itp.), umiejętność tworzy schemat JSON 2020-12, który jest zgodny z trybem ścisłym i model Pydantic, który go odzwierciedla, z wpisaną obsługą odmowy i ponawiania prób.

## Ćwiczenia

1. Uruchom `code/main.py`. Dodaj czwarty przypadek testowy, którego `total_usd` jest liczbą ujemną. Potwierdź, że walidator odrzucił to, używając ścieżki ograniczenia `minimum`.

2. Rozszerz walidator o obsługę `oneOf` z dyskryminatorem. Typowy przypadek: `line_item` to albo produkt, albo usługa oznaczona tagiem `kind`. Tryb ścisły ma tutaj subtelne zasady; sprawdź przewodnik po uporządkowanych wynikach OpenAI.

3. Napisz ten sam schemat faktury co Pydantic BaseModel i porównaj dane wyjściowe `model_json_schema()` z ręcznie utworzonym schematem. Zidentyfikuj jedno pole domyślnie ustawiane przez Pydantic, które pomija wersja ręcznie zwijana.

4. Zmierz współczynnik odmów. Skonstruuj dziesięć danych wejściowych, których nie należy wyodrębniać (tekst piosenki, dowód matematyczny, pusty e-mail) i przepuść je przez prawdziwego dostawcę w trybie ścisłym. Policz odmowy a halucynacje. To jest podstawowa zasada dotycząca ponownych prób ze świadomością odmowy.

5. Przeczytaj przewodnik po ustrukturyzowanych wynikach OpenAI od góry do dołu. Zidentyfikuj jedną konstrukcję, której wyraźnie zabrania w trybie ścisłym, na którą pozwala zwykły schemat JSON. Następnie zaprojektuj schemat, który wykorzystuje zakazaną konstrukcję w sposób nieistotny i zrefaktoryzuj go tak, aby był ściśle kompatybilny.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Schemat JSON 2020-12 | „Specyfikacja schematu” | Dialekt schematu IETF, którym mówi każdy nowoczesny dostawca |
| Tryb ścisły | „Schemat gwarantowany” | Flaga OpenAI wymuszająca schemat poprzez ograniczone dekodowanie |
| Ograniczone dekodowanie | „Maskowanie logitowe” | Wymuszanie czasu dekodowania, które maskuje nieprawidłowe następne tokeny |
| Odmowa | „Model upada” | Wpisany wynik, gdy dane wejściowe nie pasują do schematu |
| Błąd analizy | „Nieprawidłowy JSON” | Dane wyjściowe nie zostały przeanalizowane jako JSON; niemożliwe pod ścisłym |
| Naruszenie schematu | „Zły kształt” | Przeanalizowano, ale naruszono typy / wymagane / wyliczenie / zakres |
| `additionalProperties: false` | „Żadne dodatki nie są dozwolone” | Zabrania nieznanych pól; wymagane w OpenAI strict |
| Pydantyczny model bazowy | „Wpisane dane wyjściowe” | Klasa Pythona, która emituje i sprawdza poprawność schematu JSON |
| Schemat Zoda | „Typ wyjściowy TypeScript” | Schemat środowiska wykonawczego TS do sprawdzania poprawności wyników dostawcy |
| Egzekwowanie gramatyki | „Dekodowanie z ograniczeniami wag otwartych” | Maskowanie logitowe oparte na FSM, jak w zarysach/wskazówkach |

## Dalsze czytanie

- [OpenAI — Wyjścia strukturalne](https://platform.openai.com/docs/guides/structured-outputs) — tryb ścisły, odmowy i wymagania dotyczące schematu
– [OpenAI — Przedstawiamy uporządkowane wyjścia](https://openai.com/index/introducing-structured-outputs-in-the-api/) — post o uruchomieniu z sierpnia 2024 r. wyjaśniający gwarancję dekodowania
- [Pydantic AI — Dane wyjściowe](https://ai.pydantic.dev/output/) — wpisano powiązania typu_wyjścia, które serializują do każdego dostawcy
- [Schemat JSON — informacje o wersji 2020-12](https://json-schema.org/draft/2020-12/release-notes) — specyfikacja kanoniczna
— [Microsoft — Ustrukturyzowane dane wyjściowe w Azure OpenAI] (https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/structured-outputs) — uwagi dotyczące wdrażania w przedsiębiorstwie i zastrzeżenia dotyczące trybu ścisłego