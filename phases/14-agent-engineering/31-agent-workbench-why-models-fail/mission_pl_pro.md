# Misja - Środowisko pracy agenta (Agent Workbench): Dlaczego zdolne modele nadal zawodzą

## Cel
Uruchom dwukrotnie to samo małe zadanie w repozytorium: najpierw opierając się wyłącznie na promptach, a następnie z wykorzystaniem siedmiu płaszczyzn środowiska pracy. Wygeneruj raport o błędach mapujący każdą brakującą płaszczyznę na spowodowany przez nią symptom.

## Wejścia
- Agent z tzw. zaślepką (stub) i miniaturowy handler w stylu FastAPI do walidacji
- Lista siedmiu płaszczyzn (instrukcje, stan, zakres, sprzężenie zwrotne, weryfikacja, recenzja, przekazanie zadania)

## Rezultaty
- `code/main.py` uruchamiający oba potoki jeden po drugim
- `failure_modes.json` podsumowujący przebieg oparty wyłącznie na prompcie
- Jednowierszowy werdykt dla przebiegu ze środowiskiem pracy

## Kryteria akceptacji
- `python3 code/main.py` kończy się z kodem wyjścia zero (zero exit code)
- Wynik pokazuje zestawione obok siebie logi z obu przebiegów
- `failure_modes.json` wymienia każdą brakującą płaszczyznę wraz z odpowiadającym jej symptomem

## Poza zakresem
- Wywołanie prawdziwego modelu. Zaślepka jest celowo oparta na regułach.
- Szczegółowe budowanie jakiejkolwiek pojedynczej płaszczyzny. Tego dotyczą kolejne lekcje.

## Źródła
- `docs/pl.md` - pełna lekcja
- `code/main.py` - implementacja referencyjna
- `outputs/skill-workbench-audit_pl.md` - wyodrębniona umiejętność
