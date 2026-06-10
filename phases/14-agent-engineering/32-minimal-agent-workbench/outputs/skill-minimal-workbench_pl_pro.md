---

name: minimal-workbench
description: Przygotuj minimalne, trzyplikowe środowisko pracy agenta dla dowolnego repozytorium — krótki router AGENTS.md, trwały plik agent_state.json i plik task_board.json w formacie JSON, powiązane z bieżącą listą zadań projektu.
version: 1.0.0
phase: 14
lesson: 32
tags: [workbench, agents-md, state, task-board, scaffold]

---

Biorąc pod uwagę ścieżkę do repozytorium oraz zwięzłą listę zadań (backlog), zbuduj minimalne, funkcjonalne środowisko pracy agenta.

Wygeneruj:

1. `AGENTS.md` o długości do 80 linii. Musi on kierować do: pliku stanu, tablicy zadań, szczegółowego dokumentu z regułami (nawet jeśli jest pusty) oraz polecenia weryfikacji. Plik ten nie powinien zawierać żadnych opisowych poradników ani zbędnego tekstu.
2. `agent_state.json` zawierający klucze: `active_task_id`, `touched_files`, `assumptions`, `blockers`, `next_action`. Wszystkie pola opcjonalne powinny domyślnie przyjmować wartość pustej tablicy lub pustego ciągu znaków (nigdy `null` dla tablic).
3. `task_board.json` jako tablicę zadań JSON. Każde zadanie musi posiadać klucze: `id`, `goal`, `owner` (`builder` | `reviewer` | `human`), `acceptance` (lista stringów) oraz `status` (`todo` | `in_progress` | `done` | `blocked`).
4. Szablon `docs/agent-rules.md` zawierający pojedynczy nagłówek H2 dla każdej płaszczyzny środowiska pracy, przeznaczony do uzupełnienia w kolejnych lekcjach.

Bezwarunkowe odrzucenia:

- Plik `AGENTS.md` o długości powyżej 80 lub poniżej 10 linii. Zbyt długi plik zostanie zignorowany przez agenta, a zbyt krótki nie spełni swojej funkcji routującej.
- Plik stanu odwołujący się do historii czatu zamiast do stanu repozytorium. Repozytorium jest jedynym wiarygodnym źródłem informacji.
- Zadania w tablicy bez zdefiniowanych kryteriów akceptacji (`acceptance`). Zadania bez tych kryteriów kończą się bezrefleksyjnymi zatwierdzeniami typu „wygląda w porządku” bez faktycznego sprawdzenia.
- Przypisywanie ról `agent` lub `model` jako `owner`. Właścicielem musi być określona rola (np. builder, reviewer), a nie podmiot.

Zasady odmowy:

- Jeśli repozytorium nie posiada polecenia weryfikacji, odmów wygenerowania `AGENTS.md` do czasu, aż zostanie ono zdefiniowane lub zastąpione zaślepką. Router odsyłający do nieistniejącej bramki testowej jest gorszy niż brak routera.
- Jeśli backlog zawiera więcej niż 12 otwartych zadań, odmów wykonania i poproś użytkownika o ich podział. Tablice zadań przekraczające rozmiar jednego ekranu stają się jedynie bezużyteczną dekoracją planistyczną.
- Jeśli projekt zawiera dane wrażliwe (sekrety) w śledzonych plikach, odmów zapisu pliku stanu i wskaż wyciek danych jako problem blokujący.

Struktura wyjściowa:

```
<repo>/
├── AGENTS.md
├── agent_state.json
├── task_board.json
└── docs/
    └── agent-rules.md
```

Zakończ sekcją „Polecana lektura”, wskazując:

- Lekcję 33 dotyczącą przekształcania szablonów reguł w wykonywalne ograniczenia.
- Lekcję 34 opisującą schemat stanu trwałego.
- Lekcję 36 omawiającą umowę zakresową dla poszczególnych zadań.
