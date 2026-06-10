# Misja - Pętle zwrotne w czasie wykonywania

## Cel
Zbuduj `run_with_feedback`, który otacza `subprocess.run`, przechwytuje stdout, stderr, kod zakończenia i czas trwania, deterministycznie obcina dane wyjściowe i dołącza rekord JSONL w następnej turze, a bramka weryfikacyjna odczytuje oba.

## Wejścia
- Trzy polecenia demonstracyjne do ćwiczenia biegacza: jeden sukces, jedna porażka, jedno wolne
- Budżet tokena: deterministyczna głowa plus ogon ze znacznikiem `...truncated N lines...`

## Elementy dostarczane
- Zapis `run_with_feedback(command, agent_note)` do `feedback_record.jsonl`
- Program ładujący, który przesyła strumieniowo JSONL do listy Pythona
- Drukarka wyświetlająca ostatni rekord każdego polecenia

## Akceptacja
- `python3 code/main.py` wychodzi z zera
- `feedback_record.jsonl` gromadzi jeden rekord na polecenie w przypadku powtórnych uruchomień
- Polecenie z `exit_code: null` nie może zostać oznaczone jako pomyślne w pętli

## Poza zakresem
- Rurociągi telemetryczne (OTel, Langfuse). Informacja zwrotna dotyczy następnej tury; telemetria jest dla operatora.
- Karnety redakcyjne i zasady rotacji. Podpowiedzi do ćwiczeń lekcyjnych obejmują te zagadnienia.

## Referencje
- `docs/en.md` - pełna lekcja
- `code/main.py` - implementacja referencyjna
- `outputs/skill-feedback-runner.md` - wyodrębniona umiejętność