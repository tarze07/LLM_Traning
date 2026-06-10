# Misja - Capstone: Wyślij pakiet warsztatowy agenta wielokrotnego użytku

## Cel
Złóż jedenaście poprzednich lekcji w wersjonowany katalog `outputs/agent-workbench-pack/` za pomocą instalatora, który umieści je idempotentnie w dowolnym docelowym repozytorium.

## Wejścia
- Schematy, skrypty i dokumentacja z lekcji od 32 do 40
- Układ opakowania: `AGENTS.md`, `docs/`, `schemas/`, `scripts/`, `bin/`, `README.md`, `VERSION`

## Elementy dostarczane
- `outputs/agent-workbench-pack/` z wypełnionym pełnym układem
- `bin/install.sh` (lub `bin/install.py`), który nie chce nadpisać bez `--force`
- Plik `VERSION` plus plik `README.md` opisujący, co pozostaje w środku, a co pozostaje na zewnątrz

## Akceptacja
- `python3 code/main.py` wychodzi z zera i drukuje drzewo pakietów
- Ponowne uruchomienie asemblera jest idempotentne
- `bin/install.sh` do nowego celu opuszcza roboczy stół warsztatowy: stan, tablica, zasady, zakres, init, biegacz, brama, recenzent, przekazanie wszystko na swoim miejscu

## Poza zakresem
- Treść zadań dla poszczególnych projektów. Zadania znajdują się na tablicy docelowego repozytorium, a nie w pakiecie.
- Połączenia SDK dostawcy. Pakiet z założenia jest niezależny od platformy.

## Referencje
- `docs/en.md` - pełna lekcja
- `code/main.py` - implementacja referencyjna
- `outputs/skill-workbench-pack.md` - wyodrębniona umiejętność