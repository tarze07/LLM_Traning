---

name: state-schema
description: Generuj schematy JSON specyficzne dla projektu dla stanu agenta i tablicy zadań, menedżera stanu Pythona z zapisami atomowymi i szkieletem migracji, aby zmiany schematu nie uszkodziły środowiska roboczego.
version: 1.0.0
phase: 14
lesson: 34
tags: [state, schema, json-schema, atomic-writes, migrations]

---

Biorąc pod uwagę repozytorium i działający w nim produkt agenta, utwórz pliki stanu pierwszego schematu dla środowiska roboczego.

Wyprodukuj:

1. `schemas/agent_state.schema.json` obejmujący wymagane klucze, dozwolone wartości statusu, dyscyplinę tablica-null i liczbę całkowitą `schema_version`.
2. `schemas/task_board.schema.json` obejmujący wzorzec identyfikatora zadania, dozwolonych właścicieli, dozwolone statusy i tablice akceptacji.
3. `tools/state_manager.py` ujawniający `load`, `commit` i `update` z zapisami atomowymi z temperaturą i zmianą nazwy.
4. Rusztowanie `tools/migrate_state.py` dla następnej aktualizacji schematu, głośno mówiące o awarii, jeśli plik pochodzi z nieznanej wersji.
5. `agent_state.json` i `task_board.json` umieszczone w `schema_version: 1` i nowe zaległości.

Twarde odrzucenia:

- Schemat bez pola `schema_version`. Migracje nie są opcjonalne.
- Zezwolenie na `null`, gdzie oczekiwana jest tablica. `null` to błąd związany z czasem zapisu udający dane.
- Pisarz używający zwykłego `open(path, "w")`. Atomic tylko pisze; częściowe pliki uszkadzają źródło prawdy.
- Przechowywanie tokenów, nieprzetworzonych transkrypcji czatów lub stanu wewnętrznego umożliwiającego identyfikację osób. Stan dotyczy faktów istotnych dla repo.

Zasady odmowy:

- Jeśli repozytorium nie ma kontroli wersji, odmów przesyłania plików stanu. Atomic pisze plus git diff to historia trwałości.
- Jeśli projekt nie zawiera co najmniej jednego polecenia akceptacji w celu sprawdzenia przejścia `done`, odrzuć wartość wyliczeniową `status: done`. Dodanie `done` bez sprawdzenia akceptacji to teatr.
- Jeśli projekt ma na celu współdzielenie stanu między procesami bez strategii blokady, ujawnij to przed wysyłką; zmiana nazwy atomowej jest konieczna, ale niewystarczająca.

Struktura wyjściowa:

```
<repo>/
├── agent_state.json
├── task_board.json
├── schemas/
│   ├── agent_state.schema.json
│   └── task_board.schema.json
└── tools/
    ├── state_manager.py
    └── migrate_state.py
```

Zakończ słowami „co przeczytać dalej”, wskazując:

- Lekcja 35 dotycząca skryptu inicjującego, który wywołuje menedżera przy uruchomieniu.
- Lekcja 38 dotycząca bramki weryfikacyjnej, która odczytuje stan do ukończenia.
- Lekcja 40 dotycząca generatora przełączania, który wykorzystuje ten sam schemat.