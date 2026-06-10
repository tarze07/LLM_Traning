---

name: feedback-runner
description: Zawijaj polecenia powłoki za pomocą deterministycznego przechwytywania stdout/stderr/exit/duration, utrwalaj rekord JSONL dla każdego polecenia i odmawiaj przesuwania pętli agenta w przypadku braku informacji zwrotnej.
version: 1.0.0
phase: 14
lesson: 37
tags: [feedback, subprocess, runner, jsonl, loop-control]

---

Biorąc pod uwagę projekt, który uruchamia polecenia powłoki w pętli agenta, utwórz moduł uruchamiający sprzężenie zwrotne i zapisywany przez niego kod JSONL.

Wyprodukuj:

1. `tools/run_with_feedback.py` odsłaniający `run_with_feedback(command: list[str], agent_note: str, timeout_s: float) -> FeedbackRecord`.
2. Lokalizacja `feedback_record.jsonl` pod stołem warsztatowym, po jednym rekordzie w wierszu.
3. `tools/feedback_loader.py`, który zwraca N ostatnich rekordów dla aktywnego zadania.
4. Pomocnik `loop_can_advance(record) -> bool`, który pętla agenta wywołuje przed ogłoszeniem sukcesu.
5. Testy obejmujące: ścieżkę sukcesu, niezerowe wyjście, przekroczenie limitu czasu, brakujący plik binarny, deterministyczne obcięcie głowy/ogona.

Twarde odrzucenia:

- `shell=True` w dowolnym miejscu prowadnicy. Tylko Argv.
- Obcięcie zależne od zegara ściennego lub losowego próbkowania. Te same dane wejściowe muszą generować ten sam rekord.
- Nagrania bez `duration_ms`. Powolne sondy są pierwszą oznaką zaklinowanego stołu warsztatowego.
- Program ładujący, który zwraca nieograniczoną listę. Zakończ na ostatnim N lub paginuj.

Zasady odmowy:

- Jeśli projekt przepuszcza sekrety przez standardowe wyjście, odmów wysłania modułu runner bez etapu redakcji. Wykreśl linie, które zostałyby uchwycone.
- Jeśli projekt zawiera polecenia, które mogą zawieszać się w nieskończoność, odmów wysyłki bez domyślnego limitu czasu i jawnej listy zastąpień.
- Jeśli moduł uruchamiający działa wewnątrz procesu roboczego ze stanem współdzielonym, odmów pominięcia blokady pliku wokół dodatku JSONL. Wielu autorów uszkodzi plik.

Struktura wyjściowa:

```
<repo>/
├── feedback_record.jsonl
└── tools/
    ├── run_with_feedback.py
    ├── feedback_loader.py
    └── test_feedback_runner.py
```

Zakończ słowami „co przeczytać dalej”, wskazując:

- Lekcja 38 dotycząca bramki weryfikacyjnej zużywającej zapisy.
- Lekcja 39 dla agenta recenzenta, który czyta opinie podczas oceniania przebiegu.
- Lekcja 23 dotycząca konwencji Otel GenAI, które należy dodać do strony telemetrycznej, gdy informacja zwrotna będzie solidna.