# Misja - Pętle sprzężenia zwrotnego środowiska wykonawczego

## Cel
Zaimplementuj funkcję `run_with_feedback`, która opakowuje `subprocess.run`, przechwytuje strumienie stdout i stderr, kod statusu oraz czas wykonania, deterministycznie skraca zbyt długie dane wyjściowe i dopisuje rekord do logu JSONL (do odczytu w kolejnej turze przez agenta oraz przez bramkę weryfikacyjną).

## Wejścia
- Trzy polecenia demonstracyjne do przetestowania runnera: jedno zakończone sukcesem, jedno błędem oraz jedno działające wolno
- Budżet tokenów: deterministyczne zachowanie początku i końca danych wyjściowych wraz ze znacznikiem `...truncated N lines...`

## Produkty (Deliverables)
- Funkcja `run_with_feedback(command, agent_note)` zapisująca rekordy do pliku `feedback_record.jsonl`
- Parser wczytujący dane z pliku JSONL do listy obiektów w Pythonie
- Moduł wypisujący na konsoli ostatni rekord dla każdego z uruchomionych poleceń

## Kryteria akceptacji
- Polecenie `python3 code/main.py` kończy działanie z kodem wyjścia 0
- Plik `feedback_record.jsonl` gromadzi po jednym rekordzie dla każdego polecenia przy kolejnych uruchomieniach
- Wykonanie polecenia zakończone kodem `exit_code: null` musi blokować oznaczenie kroku jako sukces w pętli agenta

## Poza zakresem
- Integracja z potokami telemetrycznymi (OTel, Langfuse). Informacja zwrotna służy do sterowania kolejnym krokiem pętli; telemetria jest przeznaczona dla operatora.
- Maskowanie danych (redagowanie) oraz zasady rotacji logów. Te zagadnienia zostały ujęte w sekcji z ćwiczeniami.

## Materiały odniesienia
- `docs/en.md` – pełna lekcja
- `code/main.py` – implementacja referencyjna
- `outputs/skill-feedback-runner.md` – wyodrębniona umiejętność
