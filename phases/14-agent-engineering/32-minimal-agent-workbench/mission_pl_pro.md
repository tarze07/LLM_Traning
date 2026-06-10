# Misja - Minimalne środowisko pracy agenta

## Cel
Utwórz minimalne środowisko pracy składające się z trzech plików (router, stan, tablica zadań) w nowym katalogu `workdir/`. Wykaż, że agent potrafi odczytać stan, pobrać zadanie, dokonać zapisu w dozwolonym zakresie i zapisać zaktualizowany stan.

## Wejścia
- Pusty katalog `workdir/` obok kodu lekcji
- Struktura trzech plików: `AGENTS.md`, `agent_state.json`, `task_board.json`

## Rezultaty
- `code/main.py` tworzący trzy pliki i uruchamiający jedną turę pracy agenta
- Krótki router `workdir/AGENTS.md` wskazujący plik stanu, tablicę zadań oraz polecenie weryfikacji
- `workdir/agent_state.json` zawierający identyfikator aktywnego zadania, modyfikowane pliki oraz następną akcję
- `workdir/task_board.json` zawierający krótką listę zadań wraz z ich statusami

## Kryteria akceptacji
- `python3 code/main.py` kończy się kodem wyjścia zero zarówno w pierwszym, jak i drugim przebiegu
- Drugi przebieg rozpoczyna się w miejscu, w którym zakończył się pierwszy (nie startuje od zera)
- Wyświetlony przez skrypt diff pokazuje dokładnie jeden plik zmodyfikowany w danej turze

## Poza zakresem
- Umowy dotyczące zakresu, bramki weryfikacyjne, agenci recenzujący. Warstwy te zostaną dodane w kolejnych lekcjach.
- Długi, monolityczny plik `AGENTS.md`. Router celowo ma pozostać krótki.

## Źródła
- `docs/pl.md` - pełna lekcja w języku polskim
- `code/main.py` - implementacja referencyjna
- `outputs/skill-minimal-workbench_pl.md` - wyodrębniona umiejętność
