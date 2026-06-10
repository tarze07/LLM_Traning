# Misja — Projekt końcowy (Capstone): Wdrożenie uniwersalnego pakietu środowiska warsztatowego dla agenta

## Cel
Zebranie dorobku jedenastu poprzednich lekcji w wersjonowany katalog `outputs/agent-workbench-pack/` wraz ze skryptem instalacyjnym, który w sposób idempotentny wdroży je w dowolnym repozytorium docelowym.

## Dane wejściowe
- Schematy, skrypty oraz dokumentacja przygotowane w lekcjach od 32 do 40.
- Struktura pakietu: `AGENTS.md`, `docs/`, `schemas/`, `scripts/`, `bin/`, `README.md`, `VERSION`.

## Rezultaty
- Katalog `outputs/agent-workbench-pack/` zawierający pełną strukturę plików i folderów.
- Skrypt `bin/install.sh` (lub `bin/install.py`), który wymaga użycia flagi `--force` w przypadku nadpisywania istniejącej konfiguracji.
- Pliki `VERSION` oraz `README.md` z opisem zawartości wchodzącej w skład pakietu oraz elementów pozostawionych poza nim.

## Kryteria akceptacji
- Skrypt `python3 code/main.py` kończy działanie z kodem wyjścia 0 i wyświetla strukturę katalogów pakietu.
- Ponowne uruchomienie skryptu budującego pakiet jest idempotentne.
- Uruchomienie `bin/install.sh` w nowej lokalizacji docelowej poprawnie wdraża w pełni funkcjonalne środowisko warsztatowe (stan, tablicę zadań, zasady, zakres prac, skrypty inicjalizacji i uruchamiania, bramkę weryfikacyjną, moduł recenzencki oraz raport przekazania).

## Poza zakresem
- Treści zadań specyficzne dla konkretnego projektu — powinny znajdować się bezpośrednio na tablicy zadań w repozytorium docelowym, a nie w pakiecie.
- Integracja z SDK konkretnych dostawców — pakiet z założenia musi być niezależny od platform (platform-agnostic).

## Referencje
- `docs/en.md` — pełna treść lekcji.
- `code/main.py` — implementacja referencyjna.
- `outputs/skill-workbench-pack.md` — wyodrębniona umiejętność.
