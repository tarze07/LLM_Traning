# Zadania asynchroniczne (SEP-1686) — zadzwoń teraz, pobierz później w przypadku długotrwałej pracy

> Rzeczywiste zadania wykonywane przez agentów mogą zajmować od kilku minut do wielu godzin (np. uruchomienie testów CI, pogłębiony research, eksportowanie dużych partii danych). Synchroniczne wywoływanie narzędzi w takich przypadkach prowadzi do przerywania połączeń sieciowych, przekraczania limitów czasu (timeouts) lub blokowania interfejsu użytkownika. Standard SEP-1686 (wprowadzony 25.11.2025 r.) dodaje do protokołu nowy komponent: Zadania (Tasks). Dowolne żądanie może zostać przetworzone asynchronicznie jako zadanie, a jego wynik może zostać odebrany później lub przekazany strumieniowo za pomocą powiadomień. Uwaga dotycząca wersji eksperymentalnych: specyfikacja zadań ma status eksperymentalny do pierwszej połowy 2026 roku – struktura API w bibliotekach SDK jest wciąż dostosowywana do standardu.

**Typ:** Kompilacja
**Języki:** Python (biblioteka standardowa, maszyna stanów zadań asynchronicznych)
**Wymagania wstępne:** Faza 13 · 07 (Serwer MCP), Faza 13 · 09 (Warstwa transportowa)
**Czas:** ~75 minut

## Cele nauczania

- Określ, kiedy należy przekształcić narzędzie z synchronicznego na asynchroniczne, oparte o model zadań (gdy czas wykonania po stronie serwera przekracza 30 sekund).
- Przeanalizuj cykl życia zadania: `working` → `input_required` → `completed` / `failed` / `cancelled`.
- Zaimplementuj trwałe przechowywanie stanu zadań, zapobiegając utracie postępów w przypadku awarii serwera.
- Odpytuj status zadań za pomocą `tasks/status` i poprawnie pobieraj wyniki metodą `tasks/result`.

## Problem

Narzędzie `generate_report` uruchamia potok generowania raportu, który trwa kilka minut. W tradycyjnym, synchronicznym modelu komunikacji mamy do wyboru trzy rozwiązania:

1. Utrzymywanie otwartego połączenia przez cały czas trwania operacji. Połączenia zdalne są w takich sytuacjach zrywane, klienci zgłaszają przekroczenie limitu czasu (timeout), a interfejs użytkownika ulega zawieszeniu.
2. Natychmiastowe zwrócenie tymczasowego identyfikatora, co zmusza klienta do cyklicznego odpytywania niestandardowego punktu końcowego. Rozwiązanie to łamie spójność standardu MCP.
3. Uruchomienie operacji w tle bez możliwości zwrócenia wyniku (fire-and-forget).

Żadne z tych podejść nie jest zadowalające. Standard SEP-1686 wprowadza czwarte wyjście: delegowanie zadań (Task Promotion). Dowolne żądanie (zazwyczaj `tools/call`) może zostać oznaczone jako zadanie. Serwer natychmiast odsyła identyfikator zadania. Klient monitoruje postęp za pomocą `tasks/status`, a po zakończeniu pracy pobiera dane metodą `tasks/result`. Stan zadań po stronie serwera jest trwały i pozwala na odzyskanie danych po restarcie procesu.

## Koncepcja

### Delegowanie zadań (Task Promotion)

Żądanie staje się zadaniem asynchronicznym po przekazaniu flagi `params._meta.task.required: true` (lub `optional: true` – w zależności od decyzji serwera). Serwer natychmiast odsyła odpowiedź potwierdzającą utworzenie zadania:

```json
{
  "jsonrpc": "2.0", "id": 1,
  "result": {
    "_meta": {
      "task": {
        "id": "tsk_9f7b...",
        "state": "working",
        "ttl": 900000
      }
    }
  }
}
```

Wartość `ttl` określa czas (w milisekundach), przez który serwer gwarantuje przechowywanie stanu i wyników ukończonego zadania. Po upływie tego czasu dane są usuwane.

### Obsługa zadań na poziomie narzędzi

W specyfikacji narzędzia można zadeklarować poziom wsparcia dla zadań asynchronicznych:

- `taskSupport: "forbidden"` — narzędzie zawsze wykonuje się synchronicznie (rekomendowane dla szybkich operacji).
- `taskSupport: "optional"` — klient może opcjonalnie zażądać asynchronicznego wykonania zadania.
- `taskSupport: "required"` — klient ma obowiązek wywołać to narzędzie jako zadanie asynchroniczne.

Przykładowo: narzędzie `generate_report` powinno mieć status `required`, natomiast `notes_search` – `forbidden`.

### Maszyna stanów zadania

```
working  -> input_required -> working  (pętla poprzez formularze elicitation)
working  -> completed
working  -> failed
working  -> cancelled
```

Statusy są ostateczne: przejście w stan `completed`, `failed` lub `cancelled` kończy cykl życia zadania i nie pozwala na dalsze modyfikacje stanu.

### Dostępne metody

- `tasks/status {taskId}` — zwraca aktualny status zadania oraz postęp prac (np. procentowy).
- `tasks/result {taskId}` — pobiera wynik zadania (zwraca błąd 404, jeśli zadanie nie zostało jeszcze zakończone).
- `tasks/cancel {taskId}` — żądanie anulowania zadania (metoda idempotentna; stany końcowe są ignorowane).
- `tasks/list` — metoda opcjonalna; zwraca listę aktywnych oraz niedawno zakończonych zadań.

### Strumieniowanie aktualizacji stanu

Jeśli serwer i klient wspierają powiadomienia, aktualizacje postępów mogą być przesyłane asynchronicznie przez serwer:

```
server -> notifications/tasks/updated {taskId, state, progress?}
```

Zapewnia to znacznie lepszy UX w porównaniu z cyklicznym odpytywaniem serwera (polling), choć odpytywanie pozostaje minimalnym wymogiem specyfikacji.

### Trwałość stanu zadań (Persistence)

Specyfikacja nakłada na serwery wspierające zadania obowiązek trwałego zapisywania stanu. Awaria serwera nie może powodować utraty wyników zakończonych zadań przed upływem zadeklarowanego czasu TTL. W warunkach produkcyjnych stosuje się bazy danych SQLite, Redis lub system plików. W kodzie tej lekcji używamy systemu plików.

### Idempotentność anulowania

Metoda `tasks/cancel` jest idempotentna. Jeśli zadanie jest w trakcie wykonywania, serwer podejmuje próbę jego zatrzymania (wymaga to obsługi anulowania wątku po stronie wykonawcy). Jeśli zadanie osiągnęło już status końcowy, żądanie anulowania nie wywołuje żadnych skutków.

### Odzyskiwanie stanu po awarii (Crash Recovery)

Po restarcie procesu serwera system powinien:

1. Załadować utrwalone w bazie/plikach stany wszystkich zadań.
2. Oznaczyć zadania o statusie `working`, których procesy obsługujące uległy awarii, jako `failed` z kodem błędu `CRASH_RECOVERY`.
3. Przechowywać wyniki zadań `completed`, `failed` oraz `cancelled` do momentu wygaśnięcia ich czasu TTL.

### Zadania asynchroniczne a próbkowanie (Sampling)

Zadanie uruchomione w tle może samodzielnie wysyłać żądania próbkowania `sampling/createMessage` do klienta. Umożliwia to realizację długotrwałych procesów badawczych (research agents): wątek zadania na serwerze odpytuje model klienta w miarę potrzeb, podczas gdy w interfejsie użytkownika zadanie widnieje jako `working` z okresowo aktualizowanym paskiem postępu.

### Status specyfikacji zadań

Chociaż standard SEP-1686 został zatwierdzony 25.11.2025 r., w planach rozwoju specyfikacji (MCP Roadmap) na rok 2026 wciąż otwarte pozostają trzy kwestie: unifikacja subskrypcji zdarzeń, obsługa podzadań (relacje parent-child) oraz standaryzacja czasu TTL dla wyników. Kod produkcyjny powinien traktować zadania jako stabilne w podstawowych scenariuszach i uwzględniać potencjalne zmiany w SDK dotyczące obsługi podzadań w przyszłości.

## Instrukcja użycia

Plik `code/main.py` zawiera implementację trwałego magazynu zadań (opartego na plikach JSON na dysku) oraz narzędzie `generate_report` uruchamiane w osobnym wątku w tle. Klient wywołuje to narzędzie, natychmiast otrzymuje unikalny identyfikator zadania, monitoruje stan metodą `tasks/status` i pobiera gotowy plik za pomocą `tasks/result`. Skrypt obsługuje anulowanie zadań oraz odzyskiwanie spójności po symulowanej awarii procesu roboczego.

Na co warto zwrócić uwagę:

- Stan zadania jest zapisywany w plikach JSON w katalogu `/tmp/lesson-13-tasks/<id>.json` (na systemie Windows zostanie on utworzony w odpowiedniej ścieżce roboczej).
- Wątek w tle aktualizuje pole `progress`, co jest widoczne przy kolejnych odpytaniach statusu.
- Anulowanie zadania przez klienta ustawia flagę przerwania wątku (Event), a proces roboczy kończy pracę przy kolejnej weryfikacji flagi.
- Próba odczytu stanu po „awarii” oznacza przerwane zadania statusem `failed` z kodem `CRASH_RECOVERY`.

## Wynik wdrożenia

W ramach tej lekcji powstaje plik `outputs/skill-task-store-designer.md`. Narzędzie to, na podstawie specyfikacji długotrwałego procesu (badania, kompilacja, eksport), projektuje architekturę magazynu zadań (strukturę stanu, zasady TTL, trwałość), dobiera parametry `taskSupport` oraz definiuje schematy powiadomień o postępach.

## Ćwiczenia

1. Uruchom `code/main.py`. Uruchom zadanie `generate_report`, odpytaj kilkukrotnie o status i pobierz gotowy wynik po zakończeniu pracy.

2. Przetestuj działanie metody `tasks/cancel` w trakcie wykonywania raportu. Upewnij się, że proces roboczy reaguje na żądanie, a status zadania zmienia się na `cancelled`.

3. Przetestuj odzyskiwanie po awarii: zatrzymaj wątek roboczy w trakcie wykonywania zadania, zrestartuj serwer i zaobserwuj oznaczenie zadania statusem `CRASH_RECOVERY`.

4. Zaimplementuj trwałość stanu zadań z użyciem bazy danych SQLite. Porównaj wydajność i przeanalizuj możliwości odpytywania (np. pobieranie listy wszystkich zadań dla danej sesji).

5. Zapoznaj się z planami rozwoju protokołu MCP na rok 2026. Zidentyfikuj jedno zagadnienie związane z zadaniami asynchronicznymi, które może wpłynąć na strukturę API w bibliotekach SDK w najbliższym czasie.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Zadanie (Task) | „Asynchroniczne narzędzie” | Żądanie oznaczone flagą `_meta.task` wykonywane asynchronicznie w tle |
| SEP-1686 | „Specyfikacja zadań” | Propozycja zmian (SEP), która dodała obsługę zadań w specyfikacji z 25.11.2025 |
| `_meta.task` | „Koperta zadania” | Metadane żądania zawierające identyfikator, status oraz parametr TTL |
| Wsparcie zadań | `taskSupport` | Właściwość określająca zasady wywoływania narzędzia (`forbidden` / `optional` / `required`) |
| Odpytywanie statusu | `tasks/status` | Metoda JSON-RPC służąca do pobierania aktualnego stanu i postępu prac |
| Pobieranie wyniku | `tasks/result` | Metoda zwracająca wynik ukończonego zadania lub błąd 404, jeśli zadanie trwa |
| Anulowanie zadania | `tasks/cancel` | Idempotentne żądanie zatrzymania wykonywania zadania |
| Czas przechowywania (TTL) | „Żywotność wyniku” | Czas w milisekundach, przez który serwer gwarantuje przechowywanie wyniku zadania |
| Powiadomienie o statusie | `notifications/tasks/updated` | Komunikat serwera wysyłany po zmianie stanu lub postępu zadania |
| Magazyn trwały | „Trwałość stanu” | Warstwa zapisu stanu zadań (SQLite, system plików lub Redis) odporna na restarty |

## Dalsze czytanie

- [MCP — GitHub Issue SEP-1686](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1686) — oryginalna propozycja i przebieg dyskusji nad standardem zadań.
- [WorkOS — MCP Async Tasks for AI Agent Workflows](https://workos.com/blog/mcp-async-tasks-ai-agent-workflows) — uzasadnienie biznesowe i architektoniczne dla wprowadzenia zadań.
- [DeepWiki — MCP Task System and Async Operations](https://deepwiki.com/modelcontextprotocol/modelcontextprotocol/2.7-task-system-and-async-operacje) — szczegóły działania maszyny stanów zadań.
- [FastMCP — Tasks Support](https://gofastmcp.com/servers/tasks) — implementacja zadań asynchronicznych w bibliotece FastMCP.
- [MCP Blog — 2026 Roadmap](https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/) — plany rozwoju protokołu na rok 2026, w tym obsługa podzadań.
