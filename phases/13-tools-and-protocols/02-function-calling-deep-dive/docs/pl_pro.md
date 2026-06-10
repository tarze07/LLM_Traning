# Głębokie nurkowanie w Function Calling — OpenAI, Anthropic, Gemini

> Trzej wiodący dostawcy modeli LLM w 2024 roku ujednolicili ogólny schemat pętli wywołań narzędzi, ale różnią się w szczegółach jej implementacji. OpenAI stosuje parametry `tools` oraz `tool_calls`. Anthropic korzysta z bloków `tool_use` i `tool_result`. Z kolei Gemini bazuje na sekcji `functionDeclarations` i własnej metodzie korelacji identyfikatorów. W tej lekcji przeanalizujemy te różnice i zbudujemy adapter, dzięki któremu Twój kod będzie w pełni przenośny między różnymi dostawcami API.

**Typ:** Teoria / Porównanie
**Języki:** Python (biblioteka standardowa, translacja schematów)
**Wymagania:** Faza 13 · 01 (Interfejs narzędzi — dlaczego agenci potrzebują strukturyzowanych operacji we/wy)
**Czas:** ~75 minut

## Cele kształcenia

- Wskazanie trzech głównych różnic w strukturze ładunku (payload) dla OpenAI, Anthropic oraz Gemini (na etapach deklaracji, wywołania i zwracania wyniku).
- Translacja pojedynczej deklaracji narzędzia na formaty wszystkich trzech dostawców i omówienie ograniczeń trybu ścisłego (strict mode) w każdym z nich.
- Wykorzystanie parametru `tool_choice` (lub jego odpowiedników) u każdego dostawcy do wymuszania, blokowania lub automatyzacji wywołań.
- Omówienie twardych limitów (liczba narzędzi, głębokość zagnieżdżenia schematu, długość argumentów) oraz obsługa błędów generowanych przez poszczególne API w przypadku ich przekroczenia.

## Problem

Struktura żądania i odpowiedzi w mechanizmie Function Calling różni się znacznie w zależności od dostawcy API. Oto trzy konkretne przykłady z systemów produkcyjnych w 2026 roku:

**OpenAI Chat Completions API:** Narzędzia przekazuje się jako `tools: [{"type": "function", "function": {name, description, parameters, strict}}]`. Odpowiedź modelu zawiera tablicę `choices[0].message.tool_calls: [{"id", "type": "function", "function": {name, arguments}}]`, w której `arguments` jest zakodowanym jako string kodem JSON, wymagającym ręcznego parsowania. Tryb ścisły (`strict: true`) wymusza pełną zgodność wyjścia ze schematem poprzez dekodowanie sterowane gramatyką.

**Anthropic Messages API:** Narzędzia deklaruje się jako `tools: [{name, description, input_schema}]`. Odpowiedź powraca w strukturze `content: [{"type": "text"}, {"type": "tool_use", id, name, input}]`, gdzie parametr `input` jest już w pełni sparsowanym obiektem (a nie surowym stringiem). Jako odpowiedź zwrotną przesyła się nowy komunikat o roli `user` zawierający blok `{"type": "tool_result", tool_use_id, content}`.

**Google Gemini API:** Narzędzia przekazuje się w zagnieżdżonej strukturze `tools: [{"functionDeclarations": [{name, description, parameters}]}]`. Odpowiedź powraca w sekcji `candidates[0].content.parts: [{"functionCall": {name, args, id}}]`, gdzie parametr `id` (wprowadzony w Gemini 3) służy do korelacji wywołań równoległych. Odpowiedź zwrotną przesyła się jako strukturę `{"functionResponse": {name, id, response}}`.

Koncepcja jest identyczna, lecz diabeł tkwi w szczegółach: inne nazwy pól, odmienne zagnieżdżenia struktur, niespójność (string vs obiekt) oraz różne mechanizmy korelacji wywołań. Zespół programistów piszący integrację z OpenAI musi poświęcić dodatkowe dni pracy na portowanie kodu dla Anthropic i Gemini tylko po to, by obsłużyć różnice w formatach przesyłania danych.

W tej lekcji stworzymy parser (translator), który ujednolica te trzy formaty do jednej, kanonicznej reprezentacji narzędzia. Lekcja 13.17 rozwinie tę koncepcję do poziomu uniwersalnej bramki proxy (LLM Gateway).

## Koncepcja

### Wspólna struktura

Każda integracja z API dostawców wymaga obsłużenia pięciu kroków:

1. **Rejestracja narzędzi:** Przekazanie specyfikacji (nazwa, opis, schemat parametrów) do modelu.
2. **Konfiguracja wyboru (Tool Choice):** Wymuszenie użycia konkretnego narzędzia, zablokowanie wywołań lub pozostawienie decyzji modelowi.
3. **Odczyt wywołania:** Parsowanie ustrukturyzowanej odpowiedzi z nazwą funkcji i argumentami.
4. **Identyfikacja wywołania:** Przechwycenie identyfikatora `id` w celu poprawnej korelacji przy wywołaniach równoległych.
5. **Przekazanie rezultatu:** Odesłanie wyniku wykonania z powrotem do kontekstu modelu.

### Różnice w strukturach danych

| Właściwość | OpenAI | Anthropic | Gemini |
| :--- | :--- | :--- | :--- |
| **Koperta deklaracji** | `{"type": "function", "function": {...}}` | `{"name", "description", "input_schema"}` | `{"functionDeclarations": [{...}]}` |
| **Pole schematu** | `parameters` | `input_schema` | `parameters` |
| **Kontener odpowiedzi** | `tool_calls[]` w komunikacie asystenta | `content[]` o typie `tool_use` | `parts[]` o typie `functionCall` |
| **Typ argumentów** | Surowy string JSON | Sparsowany obiekt JSON | Sparsowany obiekt JSON |
| **Format identyfikatora ID** | `call_...` (generowany przez OpenAI) | `toolu_...` (generowany przez Anthropic) | UUID (wprowadzony w Gemini 3+) |
| **Blok wynikowy** | Rola `tool` + pole `tool_call_id` | Rola `user` + blok `tool_result` z `tool_use_id` | `functionResponse` z pasującym `id` |
| **Wymuszenie narzędzia** | `tool_choice: {"type": "function", "function": {"name": ...}}` | `tool_choice: {"type": "tool", "name": ...}` | `tool_config: {function_calling_config: {mode: "ANY"}}` |
| **Zablokowanie narzędzi** | `tool_choice: "none"` | `tool_choice: {"type": "none"}` | `mode: "NONE"` |
| **Ścisła walidacja** | `strict: true` | Zawsze włączona (zależna od schematu) | Parametr `responseSchema` na poziomie żądania |

### Twarde limity operacyjne

- **OpenAI:** Maksymalnie 128 narzędzi na żądanie. Maksymalna głębokość zagnieżdżenia schematu wynosi 5. Długość ciągu argumentów $\le 8192$ bajtów. Tryb strict zabrania stosowania konstrukcji takich jak `$ref` oraz `oneOf`/`anyOf`/`allOf`, a każda zdefiniowana właściwość w schemacie musi być jawnie wymieniona na liście parametrów wymaganych (`required`).
- **Anthropic:** Maksymalnie 64 narzędzia na żądanie. Głębokość zagnieżdżenia schematu w teorii nieograniczona, w praktyce limit wynosi 10. Brak jawnej flagi trybu strict – model z natury ściśle przestrzega kontraktu schematu.
- **Gemini:** Maksymalnie 64 narzędzia na żądanie. Dialekt schematu opiera się na podzbiorze specyfikacji OpenAPI 3.0 (co tworzy drobne różnice względem standardu JSON Schema Draft 2020-12). Wywołania równoległe z unikalnymi ID są obsługiwane od wersji Gemini 3.

### Konfiguracja parametru `tool_choice`

Wszyscy dostawcy obsługują trzy podstawowe tryby pracy, choć nazywają je inaczej:
- **Auto:** Model decyduje, czy wywołać narzędzie, czy odpowiedzieć tekstem. Jest to tryb domyślny.
- **Wymagane (Required / Any):** Model musi wywołać przynajmniej jedno narzędzie.
- **Brak (None):** Model ma zakaz korzystania z narzędzi i musi odpowiedzieć tekstem.

Ponadto każdy dostawca oferuje tryby unikalne:
- **OpenAI:** Wymuszenie wywołania jednego, konkretnego narzędzia po nazwie.
- **Anthropic:** Wymuszenie konkretnego narzędzia po nazwie; flaga `disable_parallel_tool_use` pozwala dodatkowo wymusić wykonanie tylko jednego wywołania na raz.
- **Gemini:** Tryb `mode: "VALIDATED"` wymusza przepuszczenie każdej odpowiedzi przez moduł walidacji schematu, niezależnie od intencji modelu.

### Przetwarzanie równoległe (Parallel Tool Calls)

Parametr `parallel_tool_calls: true` w OpenAI (włączony domyślnie) pozwala modelowi wygenerować wiele wywołań w jednym kroku. Backend aplikacji powinien wykonać je wszystkie i odesłać rezultaty jako serię komunikatów powiązanych odpowiednimi `tool_call_id`. Anthropic w starszych wersjach obsługiwał wywołania wyłącznie sekwencyjnie; od wersji Claude 3.5 opcja ta jest włączona domyślnie (można ją wyłączyć za pomocą `disable_parallel_tool_use: true`). Gemini 2 pozwalał na wywołania równoległe, ale nie dostarczał unikalnych identyfikatorów w odpowiedziach; Gemini 3 naprawia ten problem, dodając identyfikatory UUID do poprawnej korelacji odpowiedzi.

### Obsługa strumieniowania (Streaming)

Wszyscy trzej dostawcy wspierają strumieniowe wywoływanie narzędzi, ale struktura ramek danych (wire format) różni się znacząco:
- **OpenAI:** Fragmenty (deltas) parametrów wejściowych napływają pod kluczem `tool_calls[i].function.arguments`. Należy je konkatenować do momentu odebrania ramki z `finish_reason: "tool_calls"`.
- **Anthropic:** Wysyła zdarzenia rozpoczęcia bloku (block start), przyrostowych zmian (block delta) oraz zakończenia (block stop). Fragmenty argumentów są przesyłane w `input_json_delta`.
- **Gemini:** Nowy mechanizm `streamFunctionCallArguments` (od wersji Gemini 3) przesyła częściowe argumenty powiązane z konkretnym `functionCallId`, co umożliwia przeplatanie danych dla wywołań równoległych.

Zagadnienia strumieniowania i rekonstrukcji wywołań omawia Lekcja 13.03. W tej skupiamy się na poprawności struktur pojedynczych wywołań.

### Obsługa błędów i walidacja

Reakcja na błędne argumenty z modelu wygląda inaczej u każdego z dostawców:
- **OpenAI (bez trybu strict):** Model może zwrócić uszkodzony string w polu `arguments` (np. nieprawidłowy JSON). Host musi to wyłapać, sparsować i odesłać komunikat o błędzie z prośbą o poprawę.
- **OpenAI (tryb strict):** Walidacja odbywa się bezpośrednio na etapie dekodowania tokenów na serwerach OpenAI. Wygenerowanie nieprawidłowego JSON jest niemożliwe; model może co najwyżej zgłosić jawną odmowę (`refusal`).
- **Anthropic:** Pole `input` może zawierać nieoczekiwane parametry spoza specyfikacji, ponieważ schemat ma charakter doradczy. Walidacja musi być realizowana po stronie aplikacji.
- **Gemini:** Ze względu na ograniczenia OpenAPI 3.0, pola typu `enum` wewnątrz obiektów mogą być ignorowane przez model; wymagana jest walidacja po stronie kodu aplikacji.

### Wzorzec adaptera/translatora

Kanoniczna deklaracja narzędzia w kodzie aplikacji powinna mieć jedną, spójną strukturę, na przykład:

```python
Tool(
    name="get_weather",
    description="Use when ...",
    input_schema={"type": "object", "properties": {...}, "required": [...]},
    strict=True,
)
```

Następnie zestaw prostych funkcji konwertuje ten obiekt do formatu wymaganego przez konkretnego dostawcę API. Kod w pliku `code/main.py` ilustruje ten proces, realizując pełną translację żądań i odpowiedzi bez potrzeby nawiązywania połączeń sieciowych (skupiamy się na strukturze danych, a nie na protokole transportowym HTTP).

W gotowych frameworkach produkcyjnych wzorzec ten realizują klasy takie jak `AbstractToolset` (Pydantic AI), `UniversalToolNode` (LangGraph) czy `BaseTool` (LlamaIndex). Lekcja 13.17 pokazuje, jak zbudować bramkę proxy udostępniającą jednolity interfejs zgodny z OpenAI dla wszystkich trzech dostawców.

## Zastosowanie w kodzie

Skrypt `code/main.py` zawiera definicję klasy `Tool` oraz trzy translatory generujące specyfikacje JSON dla OpenAI, Anthropic i Gemini. Ponadto implementuje parser wyodrębniający ustandaryzowane parametry `{id, name, args}` z surowych odpowiedzi każdego z dostawców. Uruchom skrypt, aby porównać wyjściowe specyfikacje.

Zwróć uwagę na:
- Konwersję nazw pól i zagnieżdżeń w deklaracjach narzędzi.
- Różnice w strukturze odpowiedzi (klucze `tool_calls`, `content` oraz `parts`).
- Dedykowaną funkcję `canonical_call()` ujednolicającą wyodrębnianie argumentów.

## Rezultat

Do tej lekcji dołączono dokument `outputs/skill-provider-portability-audit.md`. Na podstawie kodu integracji wywołań funkcji analizuje on kompatybilność z różnymi dostawcami, wskazuje ograniczenia, pola wymagające translacji oraz potencjalne błędy przy migracji kodu do innego API.

## Ćwiczenia

1. Uruchom `code/main.py` i zweryfikuj poprawność generowania plików JSON dla każdego dostawcy. Dodaj do parametrów wejściowych pole typu `enum` i sprawdź, jak tłumacz Gemini radzi sobie ze specyfiką OpenAPI 3.0.
2. Zaimplementuj parser dla komunikatu `ListToolsResponse`, który wyodrębnia listę zadeklarowanych narzędzi zwracaną przez model. Zwróć uwagę, że OpenAI nie posiada natywnego odpowiednika dla tej operacji.
3. Dodaj obsługę parametru `tool_choice`: zaimplementuj translację obiektu `ToolChoice(mode="force", tool_name="x")` oraz trybów `mode="any"` i `mode="none"` na specyficzne parametry OpenAI, Anthropic oraz Gemini (skorzystaj z tabeli porównawczej w lekcji).
4. Zapoznaj się ze szczegółową dokumentacją wybranego dostawcy API i znajdź jeden parametr konfiguracyjny Function Calling, którego nie wspierają pozostali dwaj dostawcy (np. `strict` w OpenAI, `disable_parallel_tool_use` w Anthropic czy `allowed_function_names` w Gemini).
5. Przygotuj wektor testowy: wywołanie funkcji z argumentami naruszającymi zadeklarowany schemat. Przepuść je przez walidatory każdego dostawcy (możesz użyć kodu walidacji z Lekcji 13.01) i przeanalizuj generowane komunikaty o błędach. Zdecyduj, które podejście najlepiej zabezpiecza system produkcyjny.

## Kluczowe pojęcia

| Termin | Potoczne określenie | Co to dokładnie oznacza |
| :--- | :--- | :--- |
| **Function Calling** | „Wywoływanie funkcji” | Interfejs API dostawcy umożliwiający modelowi generowanie ustrukturyzowanych poleceń zamiast prozy. |
| **Deklaracja narzędzia** | „Specyfikacja funkcji” | Zestaw parametrów (nazwa, opis, JSON Schema) przekazywany do modelu w celu opisania dostępnej funkcji. |
| **tool_choice** | „Tryb wyboru narzędzia” | Parametr żądania określający, czy model ma obowiązek wywołać funkcję, ma zakaz jej używania, czy decyduje sam. |
| **Tryb strict** | „Walidacja w locie” | Mechanizm w API OpenAI gwarantujący zgodność wygenerowanych przez model tokenów ze specyfikacją JSON Schema. |
| **Blok tool_use** | „Format Anthropic” | Specyficzny dla API Claude blok odpowiedzi zwierający identyfikator wywołania, nazwę oraz obiekt z argumentami. |
| **Część functionCall** | „Format Gemini” | Element struktury `parts[]` w API Gemini przechowujący wywołanie funkcji wraz z ID. |
| **Stringified JSON** | „JSON w stringu” | Sposób przekazywania argumentów w API OpenAI, gdzie cały obiekt JSON jest zakodowany jako tekst i wymaga sparsowania. |
| **Wywołania równoległe** | „Parallel calls” | Wygenerowanie przez model wielu komend wywołania funkcji w jednej turze interakcji. |
| **Odmowa (Refusal)** | „Odmowa modelu” | Specjalny komunikat zwracany przez model w trybie strict, gdy żądanie użytkownika narusza bezpieczeństwo lub nie pozwala na wywołanie funkcji. |
| **OpenAPI 3.0 Subset** | „Schemat Gemini” | Dialekt zapisu struktur w API Gemini posiadający pewne ograniczenia i różnice w stosunku do standardu JSON Schema. |

## Literatura uzupełniająca

- [OpenAI — Function Calling Guide](https://platform.openai.com/docs/guides/function-calling) — Oficjalny przewodnik po implementacji wywołań i trybu strict w modelach GPT.
- [Anthropic — Tool Use Overview](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/overview) — Dokumentacja obsługi bloków `tool_use` i `tool_result` w modelach Claude.
- [Google — Gemini Function Calling](https://ai.google.dev/gemini-api/docs/function-calling) — Opis specyfikacji wywołań, unikalnych ID oraz integracji z OpenAPI w modelach Gemini.
- [Vertex AI — Function Calling Info](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/multimodal/function-calling) — Dokumentacja wdrożeń biznesowych dla modeli Gemini na platformie Google Cloud.
- [OpenAI — Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs) — Szczegóły dotyczące gwarancji zgodności struktur w trybie strict.
