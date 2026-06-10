# Misja - Bramy weryfikacyjne

## Cel
Zaimplementuj `verify(task_id, artifacts)` jako czysto deterministyczną funkcję w oparciu o raport zakresu, raport reguł, dziennik opinii i różnicę, emitując jeden `verification_report.json` na zakończenie zadania.

## Wejścia
- Ładowarki pośrednie dla `scope_report.json`, `rule_report.json`, `feedback_record.jsonl` i różnic
- Tabela kontrolna: akceptacja przebiegła, akceptacja wyszła zero, zakres czysty, brak wyjść `null`, wszystkie reguły ważności bloków przeszły pomyślnie

## Elementy dostarczane
- Czysty `verify(task_id, artifacts) -> VerdictReport`
- Drukarka pokazująca wyniki poszczególnych kontroli i końcowy wynik pozytywny/negatywny
- Trzy scenariusze demonstracyjne zapisane na dysku: czyste przejście, przesunięcie zakresu, brak akceptacji

## Akceptacja
- `python3 code/main.py` wychodzi z zera
- Scenariusz czystego przejścia raportuje `passed: true`; pozostałe dwa zgłaszają `passed: false`
- Każdy scenariusz zapisuje oddzielny `verification_report.json` pod `outputs/verification/`

## Poza zakresem
- Logika LLM jako sędziego. Brama pozostaje deterministyczna; ocena jakościowa należy do recenzenta z lekcji 39.
- Podpisane dzienniki kontroli zastąpień. Ćwiczenie nakazuje wydłużenie bramy w tę stronę.

## Referencje
- `docs/en.md` - pełna lekcja
- `code/main.py` - implementacja referencyjna
- `outputs/skill-verification-gate.md` - wyodrębniona umiejętność