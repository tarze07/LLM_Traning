# Misja - Bramy weryfikacyjne

## Cel
Zaimplementuj funkcję `verify(task_id, artifacts)` jako czysto deterministyczną procedurę oceniającą raport zakresu, raport reguł, logi sprzężenia zwrotnego oraz zestaw zmian (diff), generującą raport `verification_report.json` na zakończenie zadania.

## Wejścia
- Parsery pomocnicze dla plików `scope_report.json`, `rule_report.json`, `feedback_record.jsonl` oraz zestawów zmian (diff)
- Lista kontrolna weryfikacji: pomyślne wykonanie poleceń testowych akceptacji (exit 0), brak modyfikacji poza zakresem, brak statusów wyjściowych `null` oraz pomyślne spełnienie wszystkich reguł o statusie blokady

## Produkty (Deliverables)
- Czysta funkcja `verify(task_id, artifacts) -> VerdictReport`
- Moduł prezentujący na konsoli wyniki poszczególnych testów oraz ostateczną decyzję (sukces/błąd)
- Trzy demonstracyjne scenariusze zapisane na dysku: pomyślne przejście weryfikacji, wybiegnięcie poza zakres oraz brak uruchomienia testów akceptacyjnych

## Kryteria akceptacji
- Polecenie `python3 code/main.py` kończy działanie z kodem wyjścia 0
- Scenariusz pomyślnego przejścia weryfikacji zwraca status `passed: true`, natomiast pozostałe dwa zwracają `passed: false`
- Każdy scenariusz generuje osobny plik `verification_report.json` w katalogu `outputs/verification/`

## Poza zakresem
- Wykorzystanie modeli LLM jako weryfikatorów (LLM-as-a-judge). Bramka pozostaje deterministyczna; ocena jakościowa kodu leży po stronie agenta-recenzenta z lekcji 39.
- Podpisane rejestry nadpisań (override logs). Rozbudowa bramki o tę funkcjonalność została przewidziana w sekcji z ćwiczeniami.

## Materiały odniesienia
- `docs/en.md` – pełna lekcja
- `code/main.py` – implementacja referencyjna
- `outputs/skill-verification-gate.md` – wyodrębniona umiejętność
