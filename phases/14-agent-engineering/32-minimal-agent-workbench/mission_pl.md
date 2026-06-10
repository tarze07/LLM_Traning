# Misja - Minimalny stół warsztatowy agenta

## Cel
Połóż środowisko robocze składające się z minimum trzech plików (router, stan, tablica zadań) na świeżym `workdir/` i udowodnij, że pojedynczy agent może odczytać stan, pobrać zadanie, zapisać w zakresie i utrwalić zaktualizowany stan.

## Wejścia
- Pusty katalog `workdir/` obok kodu lekcji
- Znajomość trzech plików: `AGENTS.md`, `agent_state.json`, `task_board.json`

## Elementy dostarczane
- `code/main.py`, który tworzy trzy pliki i uruchamia jedną turę
- Krótki router `workdir/AGENTS.md` wskazujący stan, płytkę i polecenie weryfikacji
- `workdir/agent_state.json` z identyfikatorem aktywnego zadania, dotkniętymi plikami, następną akcją
- `workdir/task_board.json` z małymi zaległościami i statusami

## Akceptacja
- `python3 code/main.py` wychodzi z zera w pierwszym i drugim przebiegu
- Drugi bieg rozpoczyna się w miejscu, w którym zakończył się pierwszy, a nie od zera
- Różnica wydrukowana przez skrypt pokazuje jeden plik, którego dotknął obrót

## Poza zakresem
- Umowy dotyczące zakresu, bramki weryfikacyjne, agenci recenzenci. Te warstwy będą na wierzchu w późniejszych lekcjach.
- Długi monolityczny `AGENTS.md`. Router celowo pozostaje krótki.

## Referencje
- `docs/en.md` - pełna lekcja
- `code/main.py` - implementacja referencyjna
- `outputs/skill-minimal-workbench.md` - wyodrębniona umiejętność