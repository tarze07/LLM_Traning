# Zadania asynchroniczne (SEP-1686) — zadzwoń teraz, pobierz później w przypadku długotrwałej pracy

> Prawdziwa praca agenta zajmuje minuty lub godziny: przebiegi CI, dogłębna synteza badawcza, eksport wsadowy. Synchroniczne wywołania narzędzi zrywają połączenia, przekraczają limit czasu lub blokują interfejs użytkownika. SEP-1686, połączony 25.11.2025 r., dodaje element podstawowy Zadania: każde żądanie można rozszerzyć tak, aby stało się zadaniem, a wynik można pobrać później lub przesłać strumieniowo za pośrednictwem powiadomień o stanie. Uwaga dotycząca ryzyka dryfu: Zadania mają charakter eksperymentalny do I połowy 2026 r.; Powierzchnia SDK jest nadal projektowana zgodnie ze specyfikacją.

**Typ:** Kompilacja
**Języki:** Python (stdlib, maszyna stanu zadania asynchronicznego)
**Wymagania wstępne:** Faza 13 · 07 (serwer MCP), Faza 13 · 09 (transporty)
**Czas:** ~75 minut

## Cele nauczania

- Określ, kiedy zmienić narzędzie z synchronicznego na wspomagane zadaniami (> 30 sekund pracy po stronie serwera).
- Przejdź przez cykl życia zadania: `working` → `input_required` → `completed` / `failed` / `cancelled`.
- Utrzymuj stan zadania, aby awarie nie powodowały utraty pracy wykonywanej w locie.
- Odpytuj `tasks/status` i pobierz poprawnie `tasks/result`.

## Problem

Narzędzie `generate_report` uruchamia wielominutowy potok wyodrębniania. Opcje w ramach modelu synchronicznego:

1. Przytrzymaj połączenie otwarte przez trzy minuty. Zdalne transporty to upuszczają; przekroczenie limitu czasu klientów; Interfejsy użytkownika zawieszają się.
2. Wróć natychmiast z symbolem zastępczym; wymagać od klienta sondowania niestandardowego punktu końcowego. Łamie jednolitość MCP.
3. Odpal i zapomnij; brak rezultatu.

Żadne nie jest dobre. SEP-1686 dodaje czwarty: zwiększanie zadań. Każde żądanie (zwykle `tools/call`) można oznaczyć jako zadanie. Serwer natychmiast zwraca identyfikator zadania. Klient odpytuje `tasks/status` i po zakończeniu pobiera `tasks/result`. Stan po stronie serwera przetrwa ponowne uruchomienie.

## Koncepcja

### Rozszerzenie zadania

Żądanie staje się zadaniem po ustawieniu `params._meta.task.required: true` (lub `optional: true`, decyduje serwer). Serwer natychmiast odpowiada:

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

`ttl` to obietnica serwera dotycząca zachowania stanu; po ttl wynik zadania jest odrzucany.

### Możliwość korzystania z poszczególnych narzędzi

Adnotacje narzędzi mogą deklarować obsługę zadań:

- `taskSupport: "forbidden"` — to narzędzie zawsze działa synchronicznie. Bezpieczny dla szybkich narzędzi.
- `taskSupport: "optional"` — klient może zażądać rozszerzenia zadania.
- `taskSupport: "required"` — klient MUSI używać rozszerzania zadań.

Narzędziem `generate_report` byłoby `required`. Narzędziem `notes_search` byłoby `forbidden`.

### Stany

```
working  -> input_required -> working  (loop via elicitation)
working  -> completed
working  -> failed
working  -> cancelled
```

Automat stanów jest przeznaczony tylko do dodawania: po `completed`, `failed` lub `cancelled` zadanie jest zakończone.

### Metody

- `tasks/status {taskId}` — zwraca bieżący stan i wskazówkę dotyczącą postępu.
- `tasks/result {taskId}` — blokuje lub zwraca 404, jeśli jeszcze tego nie zrobiono.
- `tasks/cancel {taskId}` — idempotentny; Stany końcowe są ignorowane.
- `tasks/list` — opcjonalnie; wylicza aktywne i ostatnio zakończone zadania.

### Zmiany stanu przesyłania strumieniowego

Gdy serwer to obsługuje, klient może subskrybować powiadomienia o stanie:

```
server -> notifications/tasks/updated {taskId, state, progress?}
```

Klienci, którzy przesyłają strumieniowo, a nie ankietują, uzyskują lepszy UX. Odpytywanie jest zawsze obsługiwane jako minimalna powierzchnia.

### Stan trwały

Specyfikacja wymaga, aby serwery deklarujące obsługę zadań utrzymywały stan. Awaria nie powinna spowodować utraty ukończonych wyników w ciągu ttl. Sklepy obejmują SQLite, Redis i system plików. Uprząż z Lekcji 13 korzysta z systemu plików.

### Semantyka anulowania

`tasks/cancel` jest idempotentny. Jeśli zadanie jest w połowie wykonywania, serwer próbuje się zatrzymać (sprawdź anulowanie współpracy między wykonawcą). Jeśli już terminal, żądanie jest nieskuteczne.

### Odzyskiwanie po awarii

Po ponownym uruchomieniu procesu serwera:

1. Załaduj wszystkie utrwalone stany zadań.
2. Oznacz wszystkie zadania `working`, których proces zakończył się śmiercią, jako `failed` z błędem `CRASH_RECOVERY`.
3. Zachowaj `completed` / `failed` / `cancelled` dla ich ttl.

### Zadania asynchroniczne i próbkowanie

Zadanie samo może wywołać `sampling/createMessage`. Tak działają długotrwałe zadania badawcze: wątek zadań serwera w razie potrzeby próbkuje model klienta, podczas gdy interfejs użytkownika klienta pokazuje zadanie jako `working` z okresowymi aktualizacjami postępu.

### Dlaczego to eksperyment

SEP-1686 został dostarczony 25.11.2025 r., ale szerszy plan działania wskazuje trzy otwarte kwestie: trwałe elementy podstawowe subskrypcji, podzadania (relacje zadań nadrzędny-podrzędny) i standaryzacja wyniku-TTL. Oczekuj, że specyfikacja będzie ewoluować do 2026 r. Kod produkcyjny powinien traktować zadania jako stabilne tylko w typowych przypadkach i chronić przed przyszłymi zmianami pakietu SDK dla podzadań.

## Użyj tego

`code/main.py` implementuje trwałą składnicę zadań (opartą na systemie plików) i narzędzie `generate_report` działające w wątku w tle. Klienci wywołują narzędzie, natychmiast uzyskują identyfikator zadania, odpytują `tasks/status`, podczas gdy pracownik aktualizuje postęp, i pobierają `tasks/result` po zakończeniu. Anulowanie działa; odzyskiwanie po awarii jest symulowane poprzez zabicie wątku roboczego i ponowne załadowanie stanu.

Na co zwrócić uwagę:

- Stan zadania JSON utrwalony do `/tmp/lesson-13-tasks/<id>.json`.
- Pole aktualizacji wątku roboczego `progress`; sondaże pokazują, że rośnie.
- Anulowanie ze strony klienta powoduje ustawienie zdarzenia; pracownik sprawdza i wychodzi wcześniej.
- Przeładowanie stanu w przypadku „awarii” oznacza zadanie w trakcie wykonywania jako `failed` z `CRASH_RECOVERY`.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-task-store-designer.md`. Biorąc pod uwagę długotrwałe narzędzie (badania, budowanie, eksport), umiejętność projektuje magazyn zadań (kształt stanu, ttl, trwałość), wybiera odpowiednią flagę taskSupport i szkicuje powiadomienia o postępie.

## Ćwiczenia

1. Uruchom `code/main.py`. Rozpocznij zadanie `generate_report`, sprawdź stan ankiety, a następnie pobierz wynik.

2. Dodaj połączenie `tasks/cancel` w trakcie. Sprawdź, czy pracownik go przestrzega, a stan zmieni się na `cancelled`.

3. Symuluj odzyskiwanie po awarii: zabij wątek roboczy, zrestartuj moduł ładujący i obserwuj tryb awarii `CRASH_RECOVERY`.

4. Rozszerz sklep na SQLite. Zwycięstwa w zakresie trwałości są takie same; otwierają się opcje zapytań (lista wszystkich zadań z sesji X).

5. Przeczytaj post dotyczący planu działania MCP na rok 2026. Zidentyfikuj jeden otwarty problem związany z zadaniami, który najprawdopodobniej będzie miał wpływ na projekt interfejsu API SDK w następnym roku.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Zadanie | „Długotrwałe wywołanie narzędzia” | Żądanie rozszerzone o `_meta.task` w celu wykonania asynchronicznego |
| WRZESIEŃ-1686 | „Specyfikacja zadań” | Propozycja Spec Evolution, która dodała zadania w 2025-11-25 |
| `_meta.task` | „Koperta zadań” | Metadane na żądanie zawierające identyfikator, stan, ttl |
| wsparcie zadania | „Flaga narzędzia” | `forbidden` / `optional` / `required` na narzędzie |
| `tasks/status` | „Metoda ankiety” | Pobierz bieżący stan i opcjonalną wskazówkę dotyczącą postępu |
| `tasks/result` | „Pobierz wynik” | Zwraca ukończony ładunek lub 404, jeśli jeszcze tego nie zrobiono |
| `tasks/cancel` | „Przestań” | Idempotentne żądanie anulowania |
| ttl | „Budżet utrzymania” | W milisekundach serwer obiecuje zachować stan zadania |
| `notifications/tasks/updated` | „Nacisk państwa” | Zdarzenie zmiany stanu inicjowane przez serwer |
| Trwały sklep | „Stan bezpieczny od awarii” | Warstwa trwałości systemu plików / SQLite / Redis |

## Dalsze czytanie

- [MCP — wydanie GitHub SEP-1686](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1686) — pierwotna propozycja i pełna dyskusja
- [WorkOS — zadania asynchroniczne MCP dla przepływów pracy agentów AI](https://workos.com/blog/mcp-async-tasks-ai-agent-workflows) — omówienie projektu z uzasadnieniem
- [DeepWiki — system zadań MCP i operacje asynchroniczne](https://deepwiki.com/modelcontextprotocol/modelcontextprotocol/2.7-task-system-and-async-operacje) — mechanika i maszyna stanów
- [FastMCP — Zadania](https://gofastmcp.com/servers/tasks) — wzorce implementacji zadań na poziomie pakietu SDK
- [Blog MCP — plan działania na rok 2026](https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/) — kwestie otwarte i priorytety na rok 2026, w tym podzadania