# Misja - Przekazanie wielu sesji

## Cel
Wygeneruj pliki `handoff.md` i `handoff.json` na podstawie artefaktów środowiska roboczego na koniec sesji deweloperskiej, aby kolejna sesja mogła wystartować z pełną wydajnością od pierwszej minuty. Obie formy zawierają ten sam zestaw siedmiu pól (w przypadku rozbieżności priorytet ma struktura JSON).

## Wejścia
- Pliki `agent_state.json`, `verification_report.json`, `review_report.json` oraz `feedback_record.jsonl` z poprzednich lekcji
- Siedem pól: `summary`, `changed_files`, `commands_run`, `failed_attempts`, `open_risks`, `next_action`, `verdict_pointer`

## Produkty (Deliverables)
- Loader wczytujący cztery artefakty wejściowe do obiektu `WorkbenchSnapshot`
- Funkcja `generate_handoff(snapshot) -> (markdown, payload)`
- Filtr logów sprzężenia zwrotnego wybierający K ostatnich rekordów oraz wszystkie błędy
- Pliki `handoff.md` oraz `handoff.json` zapisane w katalogu roboczym obok skryptu

## Kryteria akceptacji
- Polecenie `python3 code/main.py` kończy działanie z kodem wyjścia 0
- Oba pliki zawierają komplet siedmiu pól oraz niepustą sekcję `next_action`
- Ponowne wykonanie skryptu na tych samych danych wejściowych generuje identyczny pakiet (idempotentność)

## Poza zakresem
- Strategie kompresji kontekstu (np. kompaktowanie po stronie API Codex czy pięcioetapowa kompresja w Claude Code). Przekazanie (handoff) zamyka sesję, natomiast kompresja ma na celu jej przedłużenie.
- Szablony pull requestów. Opis w formacie Markdown może zostać wykorzystany jako treść PR, jednak lekcja kończy się na wygenerowaniu samego pliku.

## Materiały odniesienia
- `docs/en.md` – pełna lekcja
- `code/main.py` – implementacja referencyjna
- `outputs/skill-handoff-generator.md` – wyodrębniona umiejętność
