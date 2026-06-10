---

name: rule-set-builder
description: Przeprowadź wywiad z właścicielem projektu, podziel jego istniejące instrukcje prozatorskie na pięć kategorii operacyjnych i wyślij plik agent-rules.md z wersją wersjonowaną oraz kod sprawdzający Python.
version: 1.0.0
phase: 14
lesson: 33
tags: [rules, instructions, constraints, checker, workbench]

---

Biorąc pod uwagę repozytorium i wszelkie istniejące instrukcje prozy (`AGENTS.md`, `CONTRIBUTING.md`, dokumenty wprowadzające), utwórz zestaw reguł składający się z pięciu kategorii, który może wykonać środowisko robocze.

Pięć kategorii:

1. `startup` — co musi być prawdą przed rozpoczęciem pracy.
2. `forbidden` – co nigdy nie powinno się wydarzyć.
3. `definition_of_done` — co świadczy o wykonaniu zadania.
4. `uncertainty` — co robi agent, gdy nie jest pewien.
5. `approval` — co wymaga podpisu człowieka.

Wyprodukuj:

1. `docs/agent-rules.md` z jednym nagłówkiem `##` na regułę. Każda reguła zawiera `category`, `check` i jednowierszowy opis.
2. `tools/rule_checker.py` z klasą `RuleChecker` udostępniającą jedną metodę na `check`. Każda metoda pobiera klasę danych `TurnTrace` i zwraca `bool`.
3. Runner `tools/rule_report.py`, który ładuje reguły, uruchamia moduł sprawdzający ślad, emituje `rule_report.json`.
4. Plik notatek o migracji: które wersety prozy stały się jaką zasadą, które odrzucono jako aspiracyjne, dlaczego.

Twarde odrzucenia:

- Reguły bez pola `check`. Reguły aspiracyjne należą do dokumentów wprowadzających, a nie do zestawu reguł środowiska roboczego.
- Jedna zasada „bądź ostrożny”. Określ kategorię i zaznacz ją lub usuń.
- Czeki wymagające połączeń LLM. Sprawdzanie reguł musi być deterministyczne i tanie, aby można je było przeprowadzać w każdej turze.
- Pliki reguł zawierające ponad 200 linii. Podziel według kategorii na `agent-rules.{startup,forbidden,done,uncertainty,approval}.md` i trasę z indeksu nadrzędnego.

Zasady odmowy:

- Jeśli produkt agenta nie może dostarczyć `TurnTrace` (bez oprzyrządowania), odmów podłączenia kontrolera do czasu zarejestrowania co najmniej `read_state_file`, `edited_files` i `tests_exit_code`.
- Jeśli istniejące instrukcje mają w większości charakter aspiracyjny (>50%), ujawnij tę informację przed wydaniem reguł. Zestaw reguł będzie wyglądał na cienki; to prawda.
- Jeśli reguła została dodana z powodu pojedynczego zdarzenia z przeszłości, dołącz identyfikator zdarzenia, aby w przyszłości można było zdecydować, czy jest ona nadal potrzebna.

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

Zakończ słowami „co przeczytać dalej”, wskazując:

- Lekcja 36 dotycząca umów dotyczących zakresu zadań, które rozszerzają zakazaną kategorię.
- Lekcja 38 dotycząca bramek weryfikacyjnych zużywających raport reguły.
- Lekcja 39 dla agenta recenzenta, który ocenia zgodność z regułami.