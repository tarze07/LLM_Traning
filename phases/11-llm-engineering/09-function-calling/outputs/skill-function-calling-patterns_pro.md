---

name: skill-function-calling-patterns
description: Zbiór zasad decyzyjnych dotyczących wdrażania wywoływania funkcji w środowisku produkcyjnym – projektowanie narzędzi, obsługa błędów, bezpieczeństwo oraz wzorce dostawców
version: 1.0.0
phase: 11
lesson: 09
tags: [function-calling, tool-use, agents, mcp, security, openai, anthropic]

---

# Wzorce wywoływania funkcji

Podczas budowania aplikacji LLM korzystającej z narzędzi warto zastosować poniższe zasady decyzyjne.

## Kiedy używać wywoływania funkcji

**Użyj wywoływania funkcji, gdy:**
- Model potrzebuje danych w czasie rzeczywistym (pogoda, ceny akcji, zapytania do baz danych)
- Zadanie wymaga wywołania efektów ubocznych (wysyłanie e-maili, tworzenie rekordów, wdrażanie kodu)
- Model musi wybrać jedno z wielu działania na podstawie intencji użytkownika
- Budujesz agenta, który współdziała z systemami zewnętrznymi

**Zamiast tego użyj ustrukturyzowanego formatu danych wyjściowych (structured outputs), gdy:**
- Potrzebujesz ekstrakcji danych z tekstu (nie są wymagane żadne połączenia zewnętrzne)
- Wynikiem jest produkt końcowy, a nie etap pośredni
- Masz do wyboru tylko jeden schemat, a nie wiele narzędzi

**Użyj obu rozwiązań, gdy:**
- Model najpierw wywołuje narzędzie, a następnie strukturyzuje jego wynik w określonym formacie wyjściowym

## Wytyczne dotyczące projektowania narzędzi

1. **Jedno narzędzie, jedno działanie.** Narzędzie o nazwie `manage_database`, które obsługuje zapytania, wstawianie, aktualizowanie i usuwanie rekordów, jest zbyt ogólne. Lepiej podzielić je na `query_records`, `insert_record` oraz `update_record`. Model znacznie lepiej radzi sobie z wyborem węższych, wyspecjalizowanych narzędzi.

2. **Opisy działają jak prompty.** Model analizuje opisy narzędzi, aby podjąć decyzję o ich wyborze. Pisz je tak, jakby były instrukcjami dla młodszego programisty. Uwzględniaj informacje o tym, co dane narzędzie zwraca, a nie tylko o tym, co robi.

3. **Ograniczaj wartości za pomocą typów wyliczeniowych (enum).** Jeśli parametr może przyjąć od 3 do 10 konkretnych wartości, zastosuj enum. W przeciwnym razie model może generować różne warianty ciągów znaków (np. „Celsjusz”, „celsjusz”, „C”, „metryczny”), jeśli go nie ograniczysz.

4. **Mniej narzędzi to lepsza dokładność.** GPT-4o dobrze radzi sobie z obsługą od 5 do 10 narzędzi. Przy ponad 20 narzędziach trafność ich wyboru zaczyna spadać. Z kolei przy ponad 50 narzędziach należy spodziewać się błędnego wyboru w 10–15% przypadków. W takich sytuacjach warto grupować powiązane funkcje lub zastosować warstwę routingu.

5. **Wymagane oznacza rzeczywiście niezbędne.** Oznaczaj parametr jako wymagany tylko wtedy, gdy narzędzie absolutnie nie może bez niego funkcjonować. Opcjonalne parametry z dobrze dobranymi wartościami domyślnymi zmniejszają liczbę błędów przy wywoływaniu narzędzi.

## Wzorce specyficzne dla dostawcy

### OpenAI (GPT-4o, o3, GPT-4o-mini)

```python
tools=[{"type": "function", "function": {"name": ..., "parameters": ...}}]
tool_choice="auto"       # model decides
tool_choice="required"   # must call at least one tool
tool_choice={"type": "function", "function": {"name": "specific_tool"}}
```

- Obsługuje równoległe wywołania narzędzi (wiele `tool_calls` w jednej odpowiedzi)
- Identyfikatory wywołań narzędzi muszą zostać przekazane z wynikami
- `gpt-4o-mini` jest 10-krotnie tańszy i bardzo dobrze radzi sobie z prostym kierowaniem (routingiem) do narzędzi
- Tryb ustrukturyzowanych danych wyjściowych (Structured Outputs) współpracuje z parametrami narzędzi, gwarantując pełną zgodność ze schematem

### Anthropic (Claude 3.5 Sonnet, Claude 4 Opus)

```python
tools=[{"name": ..., "description": ..., "input_schema": ...}]
tool_choice={"type": "auto"}     # model decides
tool_choice={"type": "any"}      # must call at least one tool
tool_choice={"type": "tool", "name": "specific_tool"}
```

- Wywołania narzędzi pojawiają się jako bloki zawartości o typie `tool_use`
- Wyniki są przekazywane w komunikatach od użytkownika (user messages) jako `tool_result`
- Nazwa pola to `input_schema`, a nie `parameters` (częsty błąd podczas migracji z OpenAI)
- Obsługuje wiele wywołań narzędzi na odpowiedź

### Google (Gemini 2.0 Flash, Gemini 2.0 Pro)

```python
function_declarations=[{"name": ..., "description": ..., "parameters": ...}]
function_calling_config={"mode": "AUTO"}   # or "ANY" or "NONE"
```

- Używa tablicy `function_declarations` na najwyższym poziomie konfiguracji
- Wyniki są zwracane w sekcjach `function_response`
- Obsługuje równoległe wywoływanie funkcji

### Modele open source (Llama 3, Hermes, Qwen)

– Brak jednego ustandaryzowanego formatu – różni się w zależności od modelu i dostawcy infrastruktury
- Format projektu Hermes (NousResearch) jest najpopularniejszą i najbardziej dopracowaną konwencją
- Narzędzie vLLM obsługuje wywoływanie narzędzi w formacie zgodnym z OpenAI dla kompatybilnych modeli
- Ollama oferuje podstawowe wsparcie dla wywoływania narzędzi w wybranych modelach
- Przed wdrożeniem produkcyjnym dokładnie sprawdź trafność wyboru narzędzi – modele open source uzyskują wyniki o 15–30% gorsze niż GPT-4o w rankingu Berkeley Function Calling Leaderboard

## Wzorce obsługu błędów

### Zwróć błędy strukturalne

```json
{"error": true, "message": "City 'Toky' not found. Did you mean 'Tokyo'?", "code": "NOT_FOUND", "suggestions": ["Tokyo"]}
```

Dołączaj do błędów wartościowe informacje szczegółowe. Komunikat „Nie znaleziono” jest mało pomocny. Lepszy będzie: „Nie znaleziono miasta. Czy chodziło o X?”. Model potrafi wykorzystać szczegółowe komunikaty o błędach do samonaprawy (samokorekty).

### Strategia ponawiania prób

1. Wywołanie narzędzia kończy się niepowodzeniem z powodu błędu, który da się łatwo skorygować (np. literówka, błędna wartość enum).
2. Prześlij komunikat o błędzie z powrotem do modelu jako wynik działania narzędzia.
3. Model analizuje błąd, koryguje swoje zapytanie i próbuje ponownie.
4. Zastosuj limit maksymalnie 3 prób na jedno wywołanie narzędzia.
5. Po 3 nieudanych próbach zwróć ostateczny komunikat o błędzie użytkownikowi.

### Obsługa przekroczenia limitu czasu (timeout)

Zawsze definiuj limit czasu (timeout) dla każdego wywołania narzędzia. Rozsądną wartością domyślną jest 30 sekund. Jeśli limit zostanie przekroczony, zwróć ustrukturyzowany błąd przekroczenia limitu czasu, aby model mógł odpowiednio poinformować użytkownika, zamiast zawieszać działanie aplikacji.

## Lista kontrolna zabezpieczeń

| Sprawdź | Dlaczego | Jak |
|-------|-----|-----|
| Biała lista funkcji | Zapobieganie wykonaniu dowolnego kodu | Rejestrowanie wyłącznie tych narzędzi, do których użytkownik powinien mieć dostęp |
| Walidacja typów argumentów | Zapobieganie atakom typu Type Confusion | Weryfikacja typów danych przed uruchomieniem kodu |
| Sanitacja argumentów tekstowych | Zapobieganie atakom typu injection | Odrzucanie lub escapowanie znaków specjalnych |
| Parametryzacja zapytań SQL | Zapobieganie SQL Injection | Nigdy nie wykonuj bezpośrednio kodu SQL wygenerowanego przez model |
| Filtrowanie wyników narzędzi | Zapobieganie wyciekom wrażliwych danych | Usuwanie kluczy API, danych osobowych (PII) i szczegółów błędów wewnętrznych |
| Ograniczanie liczby wywołań (Rate Limiting) | Zapobieganie wpadnięciu w nieskończoną pętlę wywołań | Maksymalnie 10–20 wywołań na całą konwersację |
| Logowanie wywołań narzędzi | Utrzymanie pełnej ścieżki audytu (audit log) | Zapisywanie nazwy narzędzia, przekazanych argumentów, wyniku oraz znacznika czasu |
| Blokowanie Directory Traversal | Zapobieganie nieuprawnionemu dostępowi do systemu plików | Blokowanie znaków „..” oraz ścieżek bezwzględnych w narzędziach operujących na plikach |
| Uruchamianie kodu w piaskownicy (sandbox) | Izolacja od systemu operacyjnego hosta | Używanie kontenerów (np. Docker) lub środowisk o ograniczonych uprawnieniach |
| Kontrola rozmiaru zwracanych danych | Zapobieganie przepełnieniu okna kontekstowego (context stuffing) | Skracanie/obcinanie danych wynikowych przekraczających np. 10 KB |

## Optymalizacja wydajności

- **Wywołania równoległe:** Gdy model żąda uruchomienia kilku niezależnych narzędzi, wykonaj je współbieżnie za pomocą `asyncio.gather()` lub `concurrent.futures`.
- **Buforowanie (Caching):** Zapisuj w pamięci podręcznej wyniki wywołań narzędzi z identycznymi argumentami w ramach tej samej sesji (np. dane pogodowe nie zmieniają się w ciągu 60 sekund).
- **Przesyłanie strumieniowe:** Generuj i przesyłaj strumieniowo ostateczną odpowiedź modelu dla użytkownika w trakcie pobierania wyników z narzędzi pośrednich.
- **Dynamiczna selekcja narzędzi:** Jeśli okno kontekstowe jest małe, przekazuj modelowi tylko te definicje narzędzi, które są istotne dla danego zapytania (możesz użyć klasyfikatora do ich wstępnego przefiltrowania).
- **Mniejsze modele jako routery:** Wykorzystaj tańsze modele (np. `gpt-4o-mini` lub `claude-3-5-haiku`) do wyboru odpowiedniego narzędzia, a następnie przekaż uzyskane wyniki do potężniejszego modelu w celu dokonania ostatecznej syntezy.

## Typowe wzorce awarii

| Porażka | Przyczyna | Napraw |
|--------|-------|-----|
| Wybranie błędnego narzędzia | Niejednoznaczne opisy | Przeredaguj opisy narzędzi, używając precyzyjnych słów kluczowych i wyzwalaczy (triggers) |
| Brak wymaganych argumentów | Model pominął kluczowy parametr | Dodaj czytelne przykłady użycia bezpośrednio w opisach parametrów |
| Nieskończona pętla wywołań | Model w koło uruchamia to samo narzędzie | Zdefiniuj maksymalną liczbę iteracji (np. 5–10) i wykrywaj powtarzające się żądania |
| Halucynowanie argumentów | Model generuje prawdopodobne, ale nieistniejące wartości | Zastosuj typy wyliczeniowe (enum) i weryfikuj dane z bazą znanych wartości |
| Zbyt duży wynik z narzędzia | API zwróciło np. 100 KB danych | Skróć wynik lub stwórz jego streszczenie przed przekazaniem go z powrotem do modelu |
| Ignorowanie wyniku przez model | Format danych wyjściowych z narzędzia jest mało czytelny | Zwracaj przejrzysty i prosty format JSON z jednoznacznymi nazwami pól |
