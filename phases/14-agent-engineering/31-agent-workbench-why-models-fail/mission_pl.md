# Misja - Środowisko pracy agenta (Agent Workbench): Dlaczego zdolne modele nadal zawodzą

## Cel
Uruchom to samo małe zadanie w repozytorium dwukrotnie: najpierw polegając wyłącznie na promptach, a następnie z podłączonymi siedmioma płaszczyznami środowiska pracy, i wygeneruj raport błędów mapujący każdą brakującą płaszczyznę na spowodowany przez nią symptom.

## Wejścia
- Agent z tzw. zaślepką (stub) i miniaturowy handler w stylu FastAPI do zwalidowania
- Lista siedmiu płaszczyzn (instrukcje, stan, zakres, informacja zwrotna, weryfikacja, recenzja, przekazanie zadania)

## Rezultaty
- `code/main.py`, który uruchamia oba potoki jeden po drugim
- `failure_modes.json` podsumowujący przebieg polegający wyłącznie na prompcie
- Jednowierszowy werdykt dla przebiegu ze środowiskiem pracy

## Kryteria akceptacji
- `python3 code/main.py` kończy się z kodem zerowym (zero exit code)
- Wynik pokazuje logi z obu przebiegów zestawione obok siebie
- `failure_modes.json` wymienia każdą brakującą płaszczyznę z odpowiadającym jej symptomem

## Poza zakresem
- Wywołanie prawdziwego modelu. Zaślepka jest celowo oparta na regułach.
- Dogłębne budowanie jakiejkolwiek pojedynczej płaszczyzny. Od tego jest następne jedenaście lekcji.

## Źródła
- `docs/pl.md` - pełna lekcja
- `code/main.py` - implementacja referencyjna
- `outputs/skill-workbench-audit_pl.md` - wyodrębniona umiejętność