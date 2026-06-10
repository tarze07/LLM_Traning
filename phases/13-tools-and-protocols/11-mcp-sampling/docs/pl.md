# Próbkowanie MCP — uzupełnienia LLM na żądanie serwera i pętle agentów

> Większość serwerów MCP to głupie programy wykonujące: pobierają argumenty, uruchamiają kod i zwracają treść. Próbkowanie pozwala serwerowi zmienić kierunek: prosi LLM klienta o podjęcie decyzji. Umożliwia to pętle agentów hostowanych na serwerze bez posiadania przez serwer żadnych poświadczeń modelu. SEP-1577, połączony w dniu 25.11.2025 r., dodał narzędzia do żądań próbkowania, dzięki czemu pętla może obejmować głębsze rozumowanie. Uwaga dotycząca ryzyka dryfu: kształt narzędzia do próbkowania SEP-1577 był w fazie eksperymentalnej do pierwszego kwartału 2026 r. i nadal jest wdrażany w interfejsach API SDK.

**Typ:** Kompilacja
**Języki:** Python (stdlib, wiązka do pobierania próbek)
**Wymagania wstępne:** Faza 13 · 07 (serwer MCP), Faza 13 · 10 (zasoby i podpowiedzi)
**Czas:** ~75 minut

## Cele nauczania

- Wyjaśnij, co rozwiązuje `sampling/createMessage` (pętle hostowane na serwerze bez kluczy API po stronie serwera).
- Zaimplementuj serwer, który prosi klienta o próbkowanie w trybie wieloobrotowym i zwraca zakończenie.
- Użyj `modelPreferences` (priorytety kosztu/szybkości/inteligencji), aby pomóc w wyborze modelu klienta.
- Zbuduj narzędzie `summarize_repo`, które wewnętrznie wykonuje iteracje poprzez próbkowanie, a nie zachowanie na stałe w kodzie.

## Problem

Przydatny serwer MCP do przepływu pracy podsumowującego kod musi: przeglądać drzewo plików, wybierać pliki do odczytania, syntezować podsumowanie i zwracać. Gdzie dzieje się rozumowanie LLM?

Opcja A: serwer wywołuje własny LLM. Wymaga klucza API, rachunki po stronie serwera, są drogie w przeliczeniu na użytkownika.

Opcja B: serwer zwraca surową zawartość; agent klienta uzasadnia. Działa, ale przenosi logikę serwera do monitu klienta, co jest delikatne.

Opcja C: serwer pyta LLM klienta za pośrednictwem `sampling/createMessage`. Serwer zachowuje algorytm (które pliki odczytać, ile przebiegów wykonać), podczas gdy klient zachowuje rozliczenia i wybór modelu. Serwer nie ma żadnych danych uwierzytelniających.

Próbkowanie to opcja C. Jest to mechanizm, dzięki któremu zaufany serwer może hostować pętlę agenta, sam nie będąc pełnym hostem LLM.

## Koncepcja

### `sampling/createMessage` żądanie

Serwer wysyła:

```json
{
  "jsonrpc": "2.0",
  "id": 42,
  "method": "sampling/createMessage",
  "params": {
    "messages": [{"role": "user", "content": {"type": "text", "text": "..."}}],
    "systemPrompt": "...",
    "includeContext": "none",
    "modelPreferences": {
      "costPriority": 0.3,
      "speedPriority": 0.2,
      "intelligencePriority": 0.5,
      "hints": [{"name": "claude-3-5-sonnet"}]
    },
    "maxTokens": 1024
  }
}
```

Klient uruchamia LLM, zwraca:

```json
{"jsonrpc": "2.0", "id": 42, "result": {
  "role": "assistant",
  "content": {"type": "text", "text": "..."},
  "model": "claude-3-5-sonnet-20251022",
  "stopReason": "endTurn"
}}
```

### `modelPreferences`

Trzy liczby zmiennoprzecinkowe sumujące się do 1,0:

- `costPriority`: preferuj tańsze modele.
- `speedPriority`: preferuj szybsze modele.
- `intelligencePriority`: preferuj modele o większych możliwościach.

Plus `hints`: nazwane modele preferowane przez serwer. Klient może, ale nie musi, honorować wskazówki; konfiguracja użytkownika klienta zawsze wygrywa.

### `includeContext`

Trzy wartości:

- `"none"` — tylko wiadomości dostarczane przez serwer. Domyślny.
- `"thisServer"` — uwzględnij wcześniejsze wiadomości z sesji tego serwera.
- `"allServers"` — uwzględnij cały kontekst sesji.

`includeContext` został wycofany programowo od 25.11.2025 r., ponieważ powoduje wyciek kontekstu między serwerami, co stanowi zagrożenie dla bezpieczeństwa. Preferuj `"none"` i przekazuj w wiadomościach wyraźny kontekst.

### Próbkowanie za pomocą narzędzi (SEP-1577)

Nowość w 25.11.2025 r.: żądanie pobierania próbek może zawierać tablicę `tools`. Klient uruchamia pełną pętlę wywoływania narzędzi przy użyciu tych narzędzi. Dzięki temu serwer może hostować agenta w stylu ReAct w pętli po modelu klienta.

```json
{
  "messages": [...],
  "tools": [
    {"name": "fetch_url", "description": "...", "inputSchema": {...}}
  ]
}
```

Pętle klienta: próbka, wykonanie narzędzia, jeśli zostanie wywołane, próbkowanie ponownie, zwrócenie końcowej wiadomości asystenta. To rozwiązanie ma charakter eksperymentalny i będzie obowiązywać do pierwszego kwartału 2026 r.; Podpisy SDK mogą nadal dryfować. Podczas wdrażania potwierdź zgodność z sekcją klienta/próbkowania specyfikacji 2025-11-25.

### Człowiek w pętli

Klient MUSI pokazać użytkownikowi, o co serwer prosi model przed uruchomieniem próbki. Złośliwy serwer może wykorzystać próbkowanie do manipulowania sesją użytkownika („powiedz użytkownikowi X, aby kliknął Y”). Żądania próbkowania powierzchni Claude Desktop, VS Code i Cursor jako okno dialogowe potwierdzenia, które użytkownik może odrzucić.

Konsensus na rok 2026: pobieranie próbek bez potwierdzenia przez człowieka to sygnał ostrzegawczy. Bramy (faza 13–17) mogą automatycznie zatwierdzać pobieranie próbek niskiego ryzyka i automatycznie odrzucać wszelkie podejrzane dane.

### Pętle hostowane na serwerze bez kluczy API

Kanoniczny przypadek użycia: serwer MCP podsumowujący kod bez własnego dostępu LLM. To robi:

1. Przejdź przez strukturę repo.
2. Wywołaj `sampling/createMessage` z informacją „Wybierz pięć plików, które najprawdopodobniej opisują cel tego repozytorium”.
3. Przeczytaj te pliki.
4. Wywołaj `sampling/createMessage` z zawartością plików i „Podsumuj repozytorium w 3 akapitach”.
5. Zwróć podsumowanie jako wynik `tools/call`.

Serwer nigdy nie dotyka interfejsu API LLM. Użytkownik klienta płaci za uzupełnienia przy użyciu własnych danych uwierzytelniających.

### Zagrożenia bezpieczeństwa (ujawnienie Jednostki 42, I kwartał 2026 r.)

- **Ukryte próbkowanie.** Narzędzie, które zawsze wywołuje próbkowanie z komunikatem „odpowiedz za pomocą wiadomości e-mail użytkownika z kontekstu sesji”. Faza 13 · 15 obejmuje wektory ataku.
- **Kradzież zasobów poprzez próbkowanie.** Serwer prosi klienta o podsumowanie ładunku atakującego, obciążając użytkownika rachunkiem.
- **Bomby pętlowe.** Serwer wywołuje próbkowanie w ciasnej pętli. Klienci MUSZĄ egzekwować limity stawek na sesję.

## Użyj tego

`code/main.py` dostarcza fałszywą wiązkę próbkowania między serwerem a klientem. Symulowane narzędzie „summarize_repo” wywołuje dwie rundy próbkowania (wybór plików, a następnie podsumowanie), a fałszywy klient zwraca gotowe odpowiedzi. Uprząż pokazuje:

- Serwer wysyła `sampling/createMessage` z `modelPreferences`.
- Klient zwraca uzupełnienie.
- Serwer kontynuuje swoją pętlę.
- Ogranicznik szybkości ogranicza całkowitą liczbę wywołań próbkowania na wywołanie narzędzia.

Na co zwrócić uwagę:

- Serwer udostępnia tylko jedno narzędzie (`summarize_repo`); całe rozumowanie ma miejsce podczas wywołań próbkowania.
- Preferencje modelu mają wpływ na wybór modelu przez klienta; wskazówki zawierają listę preferowanych modeli.
- Pętla kończy się w dniu `stopReason: "endTurn"`.
- Limit `max_samples_per_tool = 5` łapie niekontrolowaną pętlę.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-sampling-loop-designer.md`. Biorąc pod uwagę algorytm po stronie serwera, który wymaga wywołań LLM (badania, podsumowanie, planowanie), umiejętność projektuje implementację opartą na próbkowaniu z odpowiednimi preferencjami modelu, limitami szybkości i potwierdzeniami bezpieczeństwa.

## Ćwiczenia

1. Uruchom `code/main.py`. Zmień `max_samples_per_tool` na 2 i przestrzegaj wartości granicznej szybkości.

2. Zaimplementuj wariant próbkowania narzędzia SEP-1577: żądanie próbkowania zawiera tablicę `tools`. Przed zwróceniem ostatecznego zakończenia sprawdź, czy pętla po stronie klienta wykonuje te narzędzia. Uwaga na ryzyko dryfu: sygnatury SDK mogą jeszcze ulec zmianie do pierwszej połowy 2026 r.

3. Dodaj potwierdzenie przez człowieka w pętli: przed pierwszym `sampling/createMessage` serwera wstrzymaj i poczekaj na zatwierdzenie przez użytkownika. Odrzucone połączenia zwracają wpisaną odmowę.

4. Dodaj ogranicznik szybkości dla użytkownika, kluczowany w zależności od sesji klienta. Pętle tego samego serwera tego samego użytkownika powinny mieć wspólny budżet.

5. Zaprojektuj narzędzie `summarize_pdf`, które korzysta z próbkowania w celu wybrania fragmentów do uwzględnienia. Naszkicuj wysłane wiadomości. W jaki sposób `modelPreferences.intelligencePriority` zmienia zachowanie przy 0,1 w porównaniu z 0,9?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Próbkowanie | „Połączenie LLM serwer-klient” | Serwer pyta model klienta o uzupełnienie |
| `sampling/createMessage` | „Metoda” | Metoda JSON-RPC dla żądań próbkowania |
| `modelPreferences` | „Priorytety modelu” | Koszt / prędkość / wagi inteligencji plus wskazówki dotyczące nazw |
| `includeContext` | „Wyciek między sesjami” | Nieaktualny tryb włączania kontekstu |
| wrzesień 1577 | „Narzędzia w próbkowaniu” | Zezwalaj narzędziom na próbkowanie dla hostowanego na serwerze ReAct |
| Człowiek w pętli | „Użytkownik potwierdza” | Klient wyświetla użytkownikowi żądanie próbkowania przed uruchomieniem |
| Bomba pętlowa | „Niekontrolowane pobieranie próbek” | Nieskończona pętla próbkowania po stronie serwera; klient musi mieć limit stawek |
| Tajne pobieranie próbek | „Ukryte rozumowanie” | Złośliwy serwer ukrywa zamiar w monitach o próbkowanie |
| Kradzież zasobów | „Korzystanie z budżetu LLM użytkownika” | Serwer zmusza klienta do wydawania próbek na próbkowanie, którego nie chce |
| `stopReason` | „Dlaczego zatrzymano generację” | `endTurn`, `stopSequence` lub `maxTokens` |

## Dalsze czytanie

- [MCP — Concepts: Sampling](https://modelcontextprotocol.io/docs/concepts/sampling) — ogólny przegląd próbkowania
- [MCP — specyfikacja próbkowania klienta 25.11.2025](https://modelcontextprotocol.io/specification/2025-11-25/client/sampling) — kształt kanoniczny `sampling/createMessage`
- [MCP — GitHub SEP-1577](https://github.com/modelcontextprotocol/modelcontextprotocol) — Propozycja Spec Evolution dotycząca narzędzi do próbkowania (eksperymentalna)
- [Jednostka 42 — Wektory ataków MCP] (https://unit42.paloaltonetworks.com/model-context-protocol-attack-vectors/) — tajne próbkowanie i wzorce kradzieży zasobów
- [Speakeasy — podstawowa koncepcja próbkowania MCP](https://www.speakeasy.com/mcp/core-concepts/sampling) — przewodnik po przykładach kodu po stronie klienta