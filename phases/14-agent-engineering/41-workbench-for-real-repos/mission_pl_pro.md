# Misja — Środowisko pracy na rzeczywistym repozytorium

## Cel
Uruchomienie tego samego zadania walidacji `/signup` w dwóch wersjach: za pomocą potoku opartego wyłącznie na prompcie oraz potoku korzystającego ze środowiska warsztatowego (workbench) na tej samej aplikacji testowej, a następnie wygenerowanie raportu porównawczego przed/po przeznaczonego dla sceptyków.

## Dane wejściowe
- Katalog `sample_app/` zawierający: `app.py` (brak walidacji), `test_app.py` (jeden test ścieżki pomyślnej/happy path), `README.md` oraz `scripts/release.sh` służący jako „przynęta” w strefie wyłączonej z zakresu prac.
- Oba potoki są w pełni oskryptowane (bez rzeczywistych wywołań LLM).

## Rezultaty
- Skrypt `code/main.py` koordynujący oba potoki na tej samej konfiguracji testowej.
- Raport `before-after-report.md` zawierający tabelę z pięcioma wskaźnikami.
- Plik `comparison.json` do dalszej analizy lub wizualizacji danych.

## Kryteria akceptacji
- Polecenie `python3 code/main.py` kończy działanie z kodem wyjścia 0.
- Raport uwzględnia wszystkie pięć wskaźników: faktycznie uruchomione testy, spełnienie kryteriów akceptacji, pliki zmodyfikowane poza zakresem, jakość pakietu przekazania, ocena recenzenta.
- Potok korzystający ze środowiska warsztatowego uzyskuje lepszy wynik niż potok bezpośredni w co najmniej 4 z 5 wskaźników.

## Poza zakresem
- Integracja z rzeczywistym LLM. Potoki są oskryptowane w celu zapewnienia powtarzalności.
- Strojenie modelu. Porównanie opiera się na tym samym, niezmiennym modelu zachowań.

## Referencje
- `docs/en.md` — pełna treść lekcji.
- `code/main.py` — implementacja referencyjna.
- `outputs/skill-workbench-benchmark.md` — wyodrębniona umiejętność.
