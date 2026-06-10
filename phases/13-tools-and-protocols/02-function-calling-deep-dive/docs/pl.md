# Funkcja wywołująca głębokie nurkowanie — OpenAI, Anthropic, Gemini

> Trzej dostawcy graniczni połączyli siły w ramach tej samej pętli wywoływania narzędzi w 2024 r., a następnie rozeszli się we wszystkim innym. OpenAI używa `tools` i `tool_calls`. Anthropic używa bloków `tool_use` i `tool_result`. Gemini używa korelacji `functionDeclarations` i unikalnego identyfikatora. W tej lekcji te trzy rozwiązania są od siebie odmienne, więc kod dostarczany przez jednego dostawcę nie ulegnie uszkodzeniu podczas przenoszenia.

**Typ:** Kompilacja
**Języki:** Python (stdlib, tłumacze schematów)
**Wymagania:** Faza 13 · 01 (interfejs narzędzia)
**Czas:** ~75 minut

## Cele nauczania

- Podaj trzy różnice w kształcie ładunków wywołujących funkcje OpenAI, Anthropic i Gemini (deklaracja, wywołanie, wynik).
- Przetłumacz jedną deklarację narzędzia na wszystkie trzy formaty dostawców i przewidź, gdzie będą się różnić ograniczenia trybu ścisłego.
- Użyj `tool_choice` w każdym dostawcy, aby wymusić, zabronić lub automatycznie wybrać wywołania narzędzi.
- Poznaj twarde limity na dostawcę (liczba narzędzi, głębokość schematu, długość argumentów) i sygnatury błędów emitowane przez każdy z nich w przypadku naruszenia limitów.

## Problem

Kształt żądania wywołania funkcji różni się w zależności od dostawcy. Trzy konkretne przykłady ze stosów produkcyjnych w 2026 r.:

**Interfejs API dokończeń/odpowiedzi na czacie OpenAI.** Zdajesz `tools: [{type: "function", function: {name, description, parameters, strict}}]`. Odpowiedź modelu zawiera `choices[0].message.tool_calls: [{id, type: "function", function: {name, arguments}}]`, gdzie `arguments` to ciąg JSON, który należy przeanalizować. Tryb ścisły (`strict: true`) wymusza zgodność ze schematem poprzez ograniczone dekodowanie.

**API Anthropic Messages.** Zdajesz `tools: [{name, description, input_schema}]`. Odpowiedź wraca jako `content: [{type: "text"}, {type: "tool_use", id, name, input}]`. `input` jest już przeanalizowany (obiekt, a nie ciąg znaków). W odpowiedzi wysyłasz nową wiadomość `user` zawierającą blok `{type: "tool_result", tool_use_id, content}`.

**API Google Gemini.** Przekazujesz `tools: [{functionDeclarations: [{name, description, parameters}]}]` (zagnieżdżony w `functionDeclarations`). Odpowiedź przychodzi w postaci `candidates[0].content.parts: [{functionCall: {name, args, id}}]`, gdzie `id` jest unikatowa w wersji Gemini 3 i nowszych dla korelacji połączeń równoległych. W odpowiedzi wpisz `{functionResponse: {name, id, response}}`.

Ta sama pętla. Różne nazwy pól, różne zagnieżdżenia, różne konwencje ciągu znaków i obiektu, różne mechanizmy korelacji. Zespół piszący agenta pogodowego na OpenAI płaci za dwudniowy port firmie Anthropic i kolejny dzień firmie Gemini tylko za instalację wodno-kanalizacyjną.

Ta lekcja buduje tłumacz, który ujednolica trzy formaty w jedną kanoniczną deklarację narzędzia i trasy na krawędzi. Faza 13 · 17 uogólnia ten sam wzorzec na bramę LLM.

## Koncepcja

### Wspólna struktura

Każdy dostawca potrzebuje pięciu rzeczy:

1. **Lista narzędzi.** Nazwa, opis i schemat wprowadzania poszczególnych narzędzi.
2. **Wybór narzędzia.** Wymuszaj użycie określonego narzędzia, zabraniaj narzędzi lub pozwól modelowi decydować.
3. **Emisja wywołań.** Ustrukturyzowane dane wyjściowe z nazwami narzędzi i argumentów.
4. **Identyfikator połączenia.** Powiąż odpowiedź z właściwym połączeniem (sprawy równoległe).
5. **Wstrzykiwanie wyniku.** Wiadomość lub blok, który wiąże wynik z wywołaniem.

### Różnice w kształcie, pole po polu

| Aspekt | OpenAI | Antropiczny | Bliźnięta |
|--------|--------|-----------|--------|
| Koperta z deklaracją | `{type: "function", function: {...}}` | `{name, description, input_schema}` | `{functionDeclarations: [{...}]}` |
| Pole schematu | `parameters` | `input_schema` | `parameters` |
| Kontener odpowiedzi | `tool_calls[]` w wiadomości Asystenta | `content[]` typu `tool_use` | `parts[]` typu `functionCall` |
| Typ argumentów | skrócony JSON | analizowany obiekt | analizowany obiekt |
| Format identyfikatora | `call_...` (generuje OpenAI) | `toolu_...` (antropiczny) | UUID (Bliźnięta 3+) |
| Blok wynikowy | rola `tool`, `tool_call_id` | `user` z `tool_result`, `tool_use_id` | `functionResponse` z pasującym `id` |
| Narzędzie siły | `tool_choice: {type: "function", function: {name}}` | `tool_choice: {type: "tool", name}` | `tool_config: {function_calling_config: {mode: "ANY"}}` |
| Zabroń narzędzi | `tool_choice: "none"` | `tool_choice: {type: "none"}` | `mode: "NONE"` |
| Ścisły schemat | `strict: true` | schemat-jest-schematem (zawsze wymuszany) | `responseSchema` na poziomie żądania |

### Limity, które faktycznie osiągniesz

- **OpenAI.** 128 narzędzi na żądanie. Głębokość schematu 5. Ciąg argumentów <= 8192 bajtów. Tryb ścisły nie wymaga nakładania się `$ref`, `oneOf`/`anyOf`/`allOf`, każda właściwość wymieniona w `required`.
- **Anthropic.** 64 narzędzia na żądanie. Głębokość schematu faktycznie nieograniczona, ale praktyczny limit 10. Brak flagi trybu ścisłego; schemat jest umową i model ma tendencję do jej przestrzegania.
- **Gemini.** 64 funkcje na żądanie. Typy schematów to podzbiór OpenAPI 3.0 (niewielka rozbieżność ze schematem JSON 2020-12). Wywołania równoległe unikalny-id od Gemini 3.

### Zachowanie `tool_choice`

Trzy tryby obsługiwane przez wszystkich, nazywane inaczej.

- **Auto.** Model wybiera narzędzie lub tekst. Domyślny.
- **Wymagane / Dowolne.** Model musi wywołać przynajmniej jedno narzędzie.
- **Brak.** Model nie może wywoływać narzędzi.

Plus jeden tryb unikalny dla każdego dostawcy:

- **OpenAI.** Wymuś określone narzędzie według nazwy.
- **Antropiczny.** Wymuś określone narzędzie według nazwy; Flaga `disable_parallel_tool_use` oddziela pojedynczy od wielu.
- **Gemini.** `mode: "VALIDATED"` kieruje każdą odpowiedź przez moduł sprawdzania poprawności schematu, niezależnie od przeznaczenia modelu.

### Połączenia równoległe

`parallel_tool_calls: true` OpenAI (domyślnie) emituje wiele wywołań w jednej wiadomości asystenta. Uruchamiasz je wszystkie i odpowiadasz zbiorczym komunikatem roli narzędzia zawierającym jeden wpis na każdy `tool_call_id`. Anthropic historycznie wykonywał pojedyncze połączenia; `disable_parallel_tool_use: false` (domyślnie od Claude 3.5) włącza multi. Gemini 2 umożliwiał połączenia równoległe, ale nie dawał stabilnych identyfikatorów; Gemini 3 dodaje identyfikatory UUID, dzięki czemu odpowiedzi poza kolejnością są dobrze korelowane.

### Transmisja strumieniowa

Wszystkie trzy obsługują przesyłane strumieniowo wywołania narzędzi. Format drutu różni się:

- **OpenAI.** Fragmenty delta `tool_calls[i].function.arguments` docierają przyrostowo. Gromadzisz do `finish_reason: "tool_calls"`.
- **Antropiczne.** Zdarzenia rozpoczęcia bloku / delty bloku / zatrzymania bloku. `input_json_delta` fragmenty zawierają częściowe argumenty.
- **Gemini.** `streamFunctionCallArguments` (nowość w Gemini 3) emituje fragmenty z `functionCallId`, dzięki czemu wiele równoległych wywołań może się przeplatać.

Faza 13 · 03 obejmuje ponowny montaż równoległy i strumieniowy. Ta lekcja skupia się na deklaracji i kształtach pojedynczego wywołania.

### Błędy i naprawa

Błędy nieprawidłowego argumentu również wyglądają inaczej.

- **OpenAI (nieścisły).** Model zwraca `arguments: "{bad json}"`, analiza JSON nie powiodła się, wstrzykujesz komunikat o błędzie i wywołujesz ponownie.
- **OpenAI (ścisłe).** Walidacja odbywa się podczas dekodowania; nieprawidłowy JSON jest niemożliwy, ale może pojawić się `refusal`.
- **Anthropic.** `input` może zawierać nieoczekiwane pola; schemat ma charakter doradczy. Sprawdź poprawność po stronie serwera.
- **Gemini.** Dziwactwo OpenAPI 3.0: `enum` w polach obiektów po cichu ignorowane; zweryfikuj się.

### Wzorzec tłumacza

Deklaracja narzędzia kanonicznego w kodzie wygląda następująco (wybierasz kształt):

```python
Tool(
    name="get_weather",
    description="Use when ...",
    input_schema={"type": "object", "properties": {...}, "required": [...]},
    strict=True,
)
```

Trzy małe funkcje przekładają to na trzy kształty dostawców. Uprząż w `code/main.py` robi dokładnie to, a następnie przesyła fałszywe wywołanie narzędzia w obie strony przez kształt odpowiedzi każdego dostawcy. Nie jest wymagana żadna sieć — ta lekcja uczy kształtów, a nie protokołu HTTP.

Zespoły produkcyjne opakowują tego tłumacza w `AbstractToolset` (Pydantic AI), `UniversalToolNode` (LangGraph) lub `BaseTool` (LlamaIndex). Faza 13 · 17 dostarcza bramę, która udostępnia interfejs API w kształcie OpenAI przed dowolnym z trzech.

## Użyj tego

`code/main.py` definiuje jedną kanoniczną `Tool` klasę danych i trzech tłumaczy, którzy emitują deklarację JSON OpenAI, Anthropic i Gemini. Następnie analizuje ręcznie stworzoną odpowiedź dostawcy każdego kształtu w ten sam kanoniczny obiekt wywołania, demonstrując, że semantyka jest identyczna pod skórą. Uruchom go i porównaj trzy deklaracje obok siebie.

Na co zwrócić uwagę:

- Trzy bloki deklaracji różnią się jedynie nazwami kopert i pól.
- Trzy bloki odpowiedzi różnią się lokalizacją połączenia (najwyższy poziom `tool_calls`, `content[]`, wpis `parts[]`).
- Jedna funkcja `canonical_call()` wyodrębnia `{id, name, args}` ze wszystkich trzech kształtów odpowiedzi.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-provider-portability-audit.md`. Biorąc pod uwagę integrację wywołań funkcji z jednym dostawcą, umiejętność generuje audyt przenośności: który dostawca ogranicza, na którym się opiera, które pola wymagają zmiany nazw i co psuje się po przeniesieniu do innego dostawcy.

## Ćwiczenia

1. Uruchom `code/main.py` i sprawdź, czy wszystkie trzy pliki JSON deklaracji dostawcy serializują ten sam bazowy obiekt `Tool`. Zmodyfikuj narzędzie kanoniczne, aby dodać parametr wyliczeniowy i potwierdź, że tylko tłumacz Gemini musi obsłużyć dziwactwo OpenAPI.

2. Dodaj parser `ListToolsResponse` dla każdego dostawcy, który wyodrębnia listę narzędzi zwracaną przez model po wywołaniu `list_tools` lub wykrywaniu. OpenAI nie ma takiego natywnie; zwróć uwagę na tę asymetrię.

3. Zaimplementuj konwersję `tool_choice`: zmapuj kanoniczną `ToolChoice(mode="force", tool_name="x")` na wszystkie trzy kształty dostawców. Następnie zmapuj `mode="any"` i `mode="none"`. Sprawdź tabelę różnic lekcji.

4. Wybierz jednego z trzech dostawców i przeczytaj od początku do końca jego przewodnik dotyczący wywoływania funkcji. Znajdź jedno pole w specyfikacji schematu, którego pozostałe dwa nie obsługują. Kandydaci: OpenAI `strict`, Anthropic `disable_parallel_tool_use`, Gemini `function_calling_config.allowed_function_names`.

5. Napisz wektor testowy: wywołanie narzędzia, którego argumenty naruszają zadeklarowany schemat. Uruchom go przez walidator każdego dostawcy (stdlib z lekcji 01 będzie działał jako serwer proxy) i zapisz, które błędy się uruchamiają. Aby zachować ścisłość, udokumentuj, którego dostawcy będziesz używać w produkcji.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Wywołanie funkcji | „Korzystanie z narzędzi” | Interfejs API na poziomie dostawcy do emisji uporządkowanych wywołań narzędzi |
| Deklaracja narzędzia | „Specyfikacja narzędzia” | Nazwa + opis + ładunek wejściowy schematu JSON |
| `tool_choice` | „Zmuszaj / zabraniaj” | Tryby automatyczne / wymagane / brak / nazwa specyficzna |
| Tryb ścisły | „Egzekwowanie schematu” | Flaga OpenAI ograniczająca dekodowanie w celu dopasowania do schematu |
| `tool_use` blok | „Kształt wezwania Anthropic” | Blok treści inline z identyfikatorem, nazwą i danymi wejściowymi |
| `functionCall` część | „Kształt zewu Bliźniąt” | Wpis `parts[]` zawierający nazwę, argumenty i identyfikator |
| Argumenty jako ciąg | „Stringowany JSON” | OpenAI zwraca argumenty jako ciąg JSON, a nie obiekt |
| Równoległe wywołania narzędzi | „Wachlowanie w jednej turze” | Wiele wywołań narzędzi w jednej wiadomości asystenta |
| Odmowa | „Model upada” | Blok odmowy tylko w trybie ścisłym zamiast połączenia |
| Podzbiór OpenAPI 3.0 | „Dziwactwo schematu Bliźniąt” | Gemini używa dialektu podobnego do schematu JSON z niewielkimi różnicami |

## Dalsze czytanie

- [OpenAI — przewodnik wywoływania funkcji](https://platform.openai.com/docs/guides/function-calling) — odniesienie kanoniczne, w tym tryb ścisły i wywołania równoległe
- [Anthropic — przegląd użycia narzędzi](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/overview) — semantyka bloków `tool_use` i `tool_result`
- [Google — wywoływanie funkcji Gemini](https://ai.google.dev/gemini-api/docs/function-calling) — wywołania równoległe, unikalne identyfikatory i podzbiór OpenAPI
- [Vertex AI — Informacje o wywoływaniu funkcji](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/multimodal/function-calling) — powierzchnia korporacyjna Gemini
- [OpenAI — Wyjścia strukturalne](https://platform.openai.com/docs/guides/structured-outputs) — szczegóły egzekwowania schematu w trybie ścisłym