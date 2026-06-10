---

name: state-schema
description: Generuj schematy JSON specyficzne dla projektu dla stanu agenta i tablicy zadań, a także menedżera stanu w Pythonie obsługującego zapisy atomowe oraz szablon migracji, aby zmiany schematu nie uszkodziły środowiska pracy.
version: 1.0.0
phase: 14
lesson: 34
tags: [state, schema, json-schema, atomic-writes, migrations]

---

Biorąc pod uwagę strukturę repozytorium oraz produkt agenta, utwórz schematy stanu (schema-first) dla środowiska pracy.

Wygeneruj:

1. `schemas/agent_state.schema.json` zawierający wymagane klucze, dozwolone wartości statusu, regułę blokowania wartości null dla tablic oraz liczbę całkowitą `schema_version`.
2. `schemas/task_board.schema.json` zawierający wzorzec identyfikatora zadania, dozwolonych wykonawców (owners), dozwolone statusy oraz tablice kryteriów akceptacji.
3. `tools/state_manager.py` udostępniający metody `load`, `commit` oraz `update` wykonujące atomowy zapis za pomocą pliku tymczasowego (temp file) i zmiany nazwy (rename).
4. Szablon `tools/migrate_state.py` do obsługi kolejnych aktualizacji schematu, zgłaszający błąd krytyczny, jeśli plik stanu pochodzi z nieznanej wersji.
5. Pliki `agent_state.json` i `task_board.json` zainicjalizowane z `schema_version: 1` oraz z aktualną tablicą zadań.

Bezwarunkowe odrzucenia:

- Schemat bez zdefiniowanego pola `schema_version`. Migracje są elementem obowiązkowym.
- Zezwalanie na wartość `null` tam, gdzie oczekiwana jest tablica. `null` w tablicach to błąd projektowy maskujący brak danych.
- Klasa zapisu korzystająca ze zwykłego `open(path, "w")`. Dopuszczalne są wyłącznie zapisy atomowe; zapisanie pliku w połowie uszkadza źródło prawdy.
- Przechowywanie danych wrażliwych (tokenów, danych osobowych) lub surowych transkrypcji czatu. Stan powinien zawierać wyłącznie fakty istotne dla repozytorium.

Zasady odmowy:

- Jeśli repozytorium nie korzysta z systemu kontroli wersji (git), odmów wdrożenia plików stanu. Zapisy atomowe w połączeniu z historią zmian gita stanowią fundament trwałości i śledzenia zmian.
- Jeśli projekt nie posiada przynajmniej jednego polecenia weryfikującego do sprawdzenia statusu `done`, odrzuć wartość wyliczeniową `status: done`. Oznaczanie zadania jako ukończone bez możliwości jego automatycznej weryfikacji to fikcja.
- Jeśli projekt zakłada współdzielenie stanu między wieloma procesami bez zdefiniowanej strategii blokowania plików (locking), poinformuj o tym użytkownika przed wdrożeniem; atomowa zmiana nazwy jest w tym przypadku niewystarczająca.

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

Zakończ sekcją „Polecana lektura”, wskazując:

- Lekcję 35 omawiającą skrypt inicjalizacyjny (init script), który uruchamia menedżera stanu przy starcie sesji.
- Lekcję 38 opisującą bramkę weryfikacyjną, która sprawdza stan w celu potwierdzenia ukończenia zadań.
- Lekcję 40 dotyczącą generatora pakietu przekazania (handover), korzystającego z tego samego schematu.
