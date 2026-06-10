---

name: minimal-workbench
description: Przygotuj minimum trzyplikowe środowisko robocze agenta dla dowolnego repozytorium — krótki router AGENTS.md, trwały plik agent_state.json i JSON task_board.json powiązane z bieżącymi zaległościami projektu.
version: 1.0.0
phase: 14
lesson: 32
tags: [workbench, agents-md, state, task-board, scaffold]

---

Biorąc pod uwagę ścieżkę repo i krótkie zaległości, zbuduj minimalny realny warsztat agenta.

Wyprodukuj:

1. `AGENTS.md` nie dłuższy niż 80 linii. Musi kierować do: pliku stanu, tablicy zadań, głębszego dokumentu reguł (nawet jeśli jest pusty) i polecenia weryfikacji. W tym pliku nie ma żadnych tutoriali dotyczących prozy.
2. `agent_state.json` z kluczami: `active_task_id`, `touched_files`, `assumptions`, `blockers`, `next_action`. Wszystkie pola opcjonalne mają domyślnie pustą tablicę lub pusty ciąg znaków, nigdy `null` w przypadku tablic.
3. `task_board.json` jako tablica zadań JSON. Każde zadanie ma `id`, `goal`, `owner` (`builder` | `reviewer` | `human`), `acceptance` (lista ciągów) i `status` (`todo` | `in_progress` | `done` | `blocked`).
4. Symbol zastępczy `docs/agent-rules.md` z pojedynczym H2 na powierzchnię, aby można go było wypełnić na późniejszych lekcjach.

Twarde odrzucenia:

- `AGENTS.md` powyżej 80 linii lub poniżej 10 linii. Za długie i agent je pomija; jest zbyt krótki i nie prowadzi do routingu.
- Plik stanu, który odwołuje się do historii czatów zamiast do repozytorium. Repo to system zapisów.
- Tablica zadań bez `acceptance`. Zadania bez kryteriów akceptacji stają się pieczątkami „wygląda dobrze”.
- Zadania, których `owner` to `agent` lub `model`. Właściciele to role, a nie podmioty.

Zasady odmowy:

- Jeśli repozytorium nie ma polecenia weryfikacji, odmów pisania `AGENTS.md`, dopóki nie zostanie ono dostarczone lub zakryte. Router wskazujący brakującą bramę jest gorszy niż brak routera.
- Jeśli backlog ma więcej niż 12 otwartych zadań, odmów i poproś użytkownika o podzielenie go. Tablice nad ekranem dryfują w stronę teatru planowania.
- Jeśli projekt zawiera sekrety w śledzonych plikach, odmów zapisania pliku stanu i najpierw ujawnij sekretny wyciek jako wynik blokujący.

Struktura wyjściowa:

```
<repo>/
├── AGENTS.md
├── agent_state.json
├── task_board.json
└── docs/
    └── agent-rules.md
```

Zakończ słowami „co przeczytać dalej”, wskazując:

- Lekcja 33 dotycząca przekształcania symbolu zastępczego reguł w ograniczenia wykonywalne.
- Lekcja 34 dotycząca trwałego schematu stanu.
- Lekcja 36 dotycząca umowy zakresowej na zadanie.