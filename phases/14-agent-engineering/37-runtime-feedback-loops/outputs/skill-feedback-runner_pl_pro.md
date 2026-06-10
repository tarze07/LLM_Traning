---

name: feedback-runner
description: Opakowuj polecenia powłoki za pomocą deterministycznego przechwytywania strumieni stdout/stderr, kodu wyjścia oraz czasu wykonania. Utrwalaj rekord w formacie JSONL dla każdego polecenia i blokuj dalsze działanie pętli agenta w przypadku braku informacji zwrotnej.
version: 1.0.0
phase: 14
lesson: 37
tags: [feedback, subprocess, runner, jsonl, loop-control]

---

Dla projektu uruchamiającego polecenia powłoki w pętli agenta, utwórz moduł sprzężenia zwrotnego (feedback runner) oraz strukturę pliku JSONL, do którego zapisuje on dane.

Wymagane elementy:

1. Skrypt `tools/run_with_feedback.py` udostępniający funkcję `run_with_feedback(command: list[str], agent_note: str, timeout_s: float) -> FeedbackRecord`.
2. Plik `feedback_record.jsonl` umieszczony w katalogu roboczym (workbench), z jednym rekordem zapisanym w każdym wierszu.
3. Skrypt `tools/feedback_loader.py` zwracający N ostatnich rekordów dla bieżącego zadania.
4. Funkcja pomocnicza `loop_can_advance(record) -> bool`, wywoływana w pętli agenta przed uznaniem kroku za pomyślny.
5. Testy jednostkowe weryfikujące: ścieżkę optymistyczną (success path), niezerowy kod wyjścia, przekroczenie limitu czasu (timeout), brak pliku wykonywalnego oraz deterministyczne skracanie początku i końca danych wyjściowych.

Bezwzględne odrzucenia (Twarde kryteria):

- Użycie `shell=True` w kodzie runnera. Dozwolona jest wyłącznie tablica argumentów (argv).
- Skracanie danych zależne od rzeczywistego czasu (zegara) lub oparte na losowym próbkowaniu. Identyczne dane wejściowe muszą zawsze dawać taki sam rekord.
- Rekordy niezawierające pola `duration_ms`. Wydłużenie czasu wykonywania poleceń to pierwsza zapowiedź zawieszenia środowiska roboczego.
- Loader wczytujący całą zawartość bez ograniczeń. Należy ograniczyć wynik do N ostatnich rekordów lub zastosować paginację.

Zasady odmowy współpracy (Refusal rules):

- Jeśli projekt może wypisywać sekrety na standardowe wyjście, odmów wdrożenia runnera bez modułu redagowania (maskowania) danych. Przed zapisem należy wyczyścić wrażliwe linie.
- Jeśli projekt wykonuje polecenia, które mogą się zawiesić na czas nieokreślony, odmów wdrożenia bez ustawienia domyślnego limitu czasu (timeout) oraz czytelnej listy jego nadpisywania.
- Jeśli runner działa w środowisku wieloprocesowym ze współdzielonym stanem, odmów wdrożenia bez implementacji blokady pliku (file lock) przy dopisywaniu do JSONL. Jednoczesny zapis przez wiele procesów uszkodzi strukturę pliku.

Struktura plików:

```
<repo>/
├── feedback_record.jsonl
└── tools/
    ├── run_with_feedback.py
    ├── feedback_loader.py
    └── test_feedback_runner.py
```

Na koniec dodaj sekcję „Co przeczytać dalej”, wskazującą na:

- Lekcję 38 dotyczącą bramki weryfikacyjnej (verification gate) konsumującej wygenerowane rekordy.
- Lekcję 39 dla agenta-recenzenta (reviewer agent), analizującego sprzężenie zwrotne podczas ewaluacji przebiegu.
- Lekcję 23 dotyczącą konwencji OpenTelemetry GenAI, które należy wdrożyć po stronie telemetrycznej po ustabilizowaniu pętli sprzężenia zwrotnego.
