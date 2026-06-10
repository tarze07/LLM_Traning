---

name: skill-function-calling-patterns
description: Ramy decyzyjne dotyczące wdrażania wywoływania funkcji w środowisku produkcyjnym — projektowanie narzędzi, obsługa błędów, bezpieczeństwo i wzorce dostawców
version: 1.0.0
phase: 11
lesson: 09
tags: [function-calling, tool-use, agents, mcp, security, openai, anthropic]

---

# Wzorce wywoływania funkcji

Budując aplikację LLM korzystającą z narzędzi, zastosuj te ramy decyzyjne.

## Kiedy używać wywoływania funkcji

**Użyj wywołania funkcji, gdy:**
- Model potrzebuje danych w czasie rzeczywistym (pogoda, ceny akcji, zapytania do baz danych)
- Zadanie wymaga efektów ubocznych (wysyłanie e-maili, tworzenie rekordów, wdrażanie kodu)
- Model musi wybierać pomiędzy wieloma działaniami w oparciu o intencje użytkownika
- Budujesz agenta, który współdziała z systemami zewnętrznymi

**Zamiast tego używaj ustrukturyzowanych wyników, gdy:**
- Potrzebujesz ekstrakcji danych z tekstu (nie są potrzebne żadne połączenia zewnętrzne)
- Wynikiem jest produkt końcowy, a nie etap pośredni
- Masz do wyboru jeden schemat, a nie wiele narzędzi

**Użyj obu, gdy:**
- Model wywołuje narzędzie, a następnie strukturyzuje wynik narzędzia w określonym formacie wyjściowym

## Wytyczne dotyczące projektowania narzędzi

1. **Jedno narzędzie, jedno działanie.** Narzędzie o nazwie `manage_database`, które obsługuje zapytania, wstawia, aktualizuje i usuwa, jest zbyt szerokie. Podzielony na `query_records`, `insert_record`, `update_record`. Modelka lepiej wybiera przy użyciu określonych narzędzi.

2. **Opisy są podpowiedziami.** Model czyta opisy narzędzi w celu podjęcia decyzji o wyborze. Napisz je tak, jakbyś pisał instrukcje dla młodszego programisty. Uwzględnij to, co narzędzie zwraca, a nie tylko to, co robi.

3. **Ogranicz za pomocą wyliczeń.** Jeśli parametr ma 3–10 prawidłowych wartości, użyj wyliczenia. Model wymyśli ciągi znaków – „Celsjusz”, „Celsjusz”, „C”, „metryczny” – chyba że je ograniczysz.

4. **Mniej narzędzi znaczy lepiej.** GPT-4o dobrze radzi sobie z 5-10 narzędziami. Przy ponad 20 narzędziach dokładność wyboru spada. Przy ponad 50 narzędziach należy spodziewać się 10-15% błędnego wyboru narzędzia. Grupuj powiązane funkcje lub użyj warstwy routingu.

5. **Wymagane oznacza wymagane.** Oznacz parametr jako wymagany tylko wtedy, gdy narzędzie dosłownie nie może bez niego działać. Opcjonalne parametry z dobrymi wartościami domyślnymi zmniejszają liczbę błędów wywoływania narzędzi.

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
- `gpt-4o-mini` jest 10 razy tańszy i dobrze radzi sobie z prostym prowadzeniem narzędzi
- Tryb wyjść strukturalnych współpracuje z parametrami narzędzi, zapewniając zgodność ze schematem

### Antropiczny (Claude 3.5 Sonnet, Claude 4 Opus)

```python
tools=[{"name": ..., "description": ..., "input_schema": ...}]
tool_choice={"type": "auto"}     # model decides
tool_choice={"type": "any"}      # must call at least one tool
tool_choice={"type": "tool", "name": "specific_tool"}
```

- Wywołania narzędzi pojawiają się jako bloki treści w `type: "tool_use"`
- Wyniki są przesyłane w wiadomościach użytkownika z `type: "tool_result"`
- Nazwa pola to `input_schema`, a nie `parameters` (częsty błąd migracji)
- Obsługuje wiele wywołań narzędzi na odpowiedź

### Google (Gemini 2.0 Flash, Gemini 2.0 Pro)

```python
function_declarations=[{"name": ..., "description": ..., "parameters": ...}]
function_calling_config={"mode": "AUTO"}   # or "ANY" or "NONE"
```

- Używa `function_declarations` na najwyższym poziomie
- Wyniki zwrócone przez części `function_response`
- Obsługuje równoległe wywoływanie funkcji

### Modele open source (Llama 3, Hermes, Qwen)

– Brak ustandaryzowanego formatu – różni się w zależności od modelu i platformy obsługi
- Format Hermes (NousResearch) jest najczęstszą, dopracowaną konwencją
- vLLM obsługuje wywoływanie narzędzi zgodnych z OpenAI dla obsługiwanych modeli
- Ollama obsługuje podstawowe wywoływanie narzędzi w kompatybilnych modelach
- Sprawdź dokładność wyboru narzędzia przed rozpoczęciem produkcji - otwarte modele są o 15-30% mniej dokładne niż GPT-4o w tabeli liderów wywołań funkcji Berkeley

## Wzorce obsługi błędów

### Zwróć błędy strukturalne

```json
{"error": true, "message": "City 'Toky' not found. Did you mean 'Tokyo'?", "code": "NOT_FOUND", "suggestions": ["Tokyo"]}
```

Dołącz przydatne informacje. „Nie znaleziono” jest złe. „Nie znaleziono. Czy miałeś na myśli X?” jest dobre. Model wykorzystuje komunikaty o błędach do samokorekty.

### Strategia ponów próbę

1. Wywołanie narzędzia nie powiodło się z powodu możliwego do naprawienia błędu (literówka, zła wartość wyliczeniowa)
2. Wyślij błąd z powrotem do modelu jako wynik narzędzia
3. Model dostosowuje się i próbuje ponownie
4. Maksymalnie 3 próby na wywołanie narzędzia
5. Po 3 awariach zwróć błąd użytkownikowi

### Obsługa przekroczenia limitu czasu

Ustaw limity czasu dla wszystkich wykonań narzędzi. 30 sekund to rozsądna wartość domyślna. Jeśli upłynie limit czasu narzędzia, zwróć ustrukturyzowany błąd przekroczenia limitu czasu, aby model mógł poinformować użytkownika, zamiast się zawieszać.

## Lista kontrolna zabezpieczeń

| Sprawdź | Dlaczego | Jak |
|-------|-----|-----|
| Funkcje listy dozwolonych | Zapobiegaj wykonaniu dowolnego kodu | Rejestruj tylko narzędzia, których potrzebuje użytkownik |
| Sprawdź typy argumentów | Zapobiegaj atakom polegającym na pomyleniu typów | Sprawdź typy przed wykonaniem |
| Oczyść argumenty ciągu | Zapobiegaj zastrzykom | Odrzuć lub wycofaj znaki specjalne |
| Sparametryzuj zapytania do bazy danych | Zapobiegaj wstrzykiwaniu SQL | Nigdy nie przekazuj bezpośrednio kodu SQL wygenerowanego przez model |
| Wyniki narzędzia filtrującego | Zapobiegaj wyciekom danych | Usuń klucze API, PII, błędy wewnętrzne |
| Wywołania narzędzia ograniczającego stawkę | Zapobiegaj niekontrolowanym pętlom | Maks. 10-20 połączeń na rozmowę |
| Rejestruj wszystkie wywołania narzędzi | Ścieżka audytu | Przechowuj nazwę narzędzia, argumenty, wynik, znacznik czasu |
| Blokuj przejście ścieżki | Zapobiegaj dostępowi do systemu plików | Odrzuć `..` i ścieżki bezwzględne w narzędziach plikowych |
| Wykonanie kodu piaskownicy | Zapobiegaj dostępowi do systemu | Użyj kontenerów lub ograniczonych wbudowanych |
| Sprawdź rozmiar zwrotu | Zapobiegaj upychaniu kontekstu | Obetnij wyniki powyżej 10 KB |

## Optymalizacja wydajności

- **Wywołania równoległe:** Gdy model żąda wielu niezależnych narzędzi, wykonaj je jednocześnie z `asyncio.gather()` lub `concurrent.futures`
- **Buforowanie:** Wyniki narzędzia pamięci podręcznej dla identycznych argumentów w tej samej sesji (pogoda nie zmienia się w ciągu 60 sekund)
- **Przesyłanie strumieniowe:** Przesyłaj strumieniowo ostateczną reakcję modelu podczas pobierania wyników narzędzia
- **Oczyszczanie narzędzi:** Jeśli kontekst jest wąski, uwzględnij tylko definicje narzędzi istotne dla bieżącego zapytania (do filtrowania użyj klasyfikatora)
- **Mniejsze modele do trasowania:** Użyj `gpt-4o-mini` lub `claude-3-5-haiku` do wyboru narzędzia, a następnie przekaż wyniki do silniejszego modelu w celu syntezy

## Typowe wzorce awarii

| Porażka | Przyczyna | Napraw |
|--------|-------|-----|
| Wybrano niewłaściwe narzędzie | Niejednoznaczne opisy | Przepisz opisy, używając konkretnych słów wyzwalających |
| Brak wymaganych argumentów | Model zapomniał parametru | Dodaj jasne przykłady w opisach parametrów |
| Nieskończona pętla narzędzi | Model ciągle wywołuje to samo narzędzie | Ustaw maksymalną liczbę iteracji (5-10) i wykryj powtarzające się wywołania |
| Halucynacyjne argumenty | Model wymyśla wiarygodne, ale błędne wartości | Użyj wyliczeń, sprawdź znane wartości |
| Wynik narzędzia za duży | API zwróciło 100KB danych | Obetnij lub podsumuj przed przekazaniem zwrotnym |
| Model ignoruje wynik narzędzia | Format wyniku mylący | Zwróć czysty JSON z wyraźnymi nazwami pól |