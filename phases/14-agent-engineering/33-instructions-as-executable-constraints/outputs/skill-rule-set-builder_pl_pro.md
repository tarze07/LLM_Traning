---

name: rule-set-builder
description: Przeprowadź wywiad z właścicielem projektu, podziel jego dotychczasowe opisowe instrukcje na pięć kategorii operacyjnych i wygeneruj wersjonowany plik agent-rules.md oraz kod walidacyjny w języku Python.
version: 1.0.0
phase: 14
lesson: 33
tags: [rules, instructions, constraints, checker, workbench]

---

Biorąc pod uwagę strukturę repozytorium oraz wszelkie istniejące opisowe instrukcje (`AGENTS.md`, `CONTRIBUTING.md`, dokumenty wdrożeniowe), utwórz zestaw reguł składający się z pięciu kategorii, który może być automatycznie weryfikowany przez środowisko pracy.

Pięć kategorii:

1. `startup` — co musi być spełnione przed rozpoczęciem pracy.
2. `forbidden` – co nigdy nie powinno się wydarzyć.
3. `definition_of_done` — co świadczy o pełnym wykonaniu zadania.
4. `uncertainty` — co robi agent, gdy ma wątpliwości.
5. `approval` — co wymaga zatwierdzenia przez człowieka.

Wygeneruj:

1. `docs/agent-rules.md` z jednym nagłówkiem `##` dla każdej reguły. Każda reguła musi zawierać pola `category`, `check` oraz krótki, jednowierszowy opis.
2. `tools/rule_checker.py` z klasą `RuleChecker` udostępniającą po jednej metodzie dla każdej walidacji (`check`). Każda metoda przyjmuje obiekt `TurnTrace` i zwraca wartość typu `bool`.
3. Skrypt uruchamiający `tools/rule_report.py`, który ładuje reguły, analizuje ślad wykonania (trace) za pomocą klasy sprawdzającej i generuje raport w pliku `rule_report.json`.
4. Plik z notatkami z migracji (`migration-notes.md`) zawierający informację, które opisowe zdania zostały przekształcone w konkretne reguły, które z nich odrzucono jako czysto deklaratywne i dlaczego.

Bezwarunkowe odrzucenia:

- Reguły bez zdefiniowanego pola `check`. Ogólnikowe zasady deklaratywne powinny znajdować się w dokumentacji wdrożeniowej, a nie w technicznym zestawie reguł środowiska pracy.
- Reguły w stylu „bądź ostrożny”. Każdą regułę należy przypisać do konkretnej kategorii i zdefiniować dla niej test walidacyjny albo ją usunąć.
- Sprawdzenia wymagające zapytań do modeli LLM. Walidacja reguł musi być deterministyczna i szybka, aby mogła być uruchamiana przy każdej turze pracy agenta.
- Pliki reguł przekraczające 200 linii. W takim przypadku należy podzielić reguły tematycznie na pliki `agent-rules.{startup,forbidden,done,uncertainty,approval}.md` i odwołać się do nich w głównym pliku indeksu.

Zasady odmowy:

- Jeśli system agenta nie jest w stanie dostarczyć śladu wykonania `TurnTrace` (brak profilowania/logowania), odmów integracji skryptu sprawdzającego do czasu, aż rejestrowane będą przynajmniej zdarzenia `read_state_file`, `edited_files` oraz `tests_exit_code`.
- Jeśli dotychczasowe instrukcje mają w większości charakter deklaratywny (>50%), poinformuj o tym użytkownika przed wdrożeniem reguł. Nowy zestaw reguł może wydawać się bardzo zwięzły – i tak powinno być.
- Jeśli dana reguła została dodana na skutek pojedynczego incydentu z przeszłości, dołącz do niej identyfikator tego incydentu, aby w przyszłości móc ocenić, czy ta reguła jest nadal potrzebna.

Struktura wyjściowa:

```
<repo>/
├── docs/
│   └── agent-rules.md
├── tools/
│   ├── rule_checker.py
│   └── rule_report.py
└── docs/migration-notes.md
```

Zakończ sekcją „Polecana lektura”, wskazując:

- Lekcję 36 dotyczącą umów zakresu zadań (task scopes), które rozbudowują kategorię działań zabronionych (`forbidden`).
- Lekcję 38 opisującą bramki weryfikacyjne wykorzystujące raport z walidacji reguł.
- Lekcję 39 omawiającą agenta recenzującego, który ocenia zgodność z regułami.
