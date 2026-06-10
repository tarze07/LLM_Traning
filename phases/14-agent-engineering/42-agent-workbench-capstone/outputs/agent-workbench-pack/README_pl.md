# Pakiet stołu roboczego agenta

Wpuszczany stół warsztatowy dla każdego repozytorium, które wymaga niezawodnej pracy agenta.

## Co otrzymujesz

- Krótki router `AGENTS.md` do reszty pakietu.
- Zasady `docs/`, polityka niezawodności, protokół przekazania, rubryka recenzenta.
- Schematy `schemas/` JSON dla umowy stanowej, zarządu i zakresu.
- Inicjacja `scripts/`, moduł sprzężenia zwrotnego, bramka weryfikacyjna, generator przekazywania.
- Instalator idempotentny `bin/install.sh`.

## Szybki start

```
bin/install.sh
$EDITOR task_board.json
python3 scripts/init_agent.py
```

## Wersja

Plik `VERSION` jest umową. Poważne wstrząsy wymagają migracji stanu.