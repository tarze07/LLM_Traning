# Pakiet środowiska warsztatowego dla agenta

Gotowe do wdrożenia (drop-in) środowisko warsztatowe dla dowolnego repozytorium wymagającego niezawodnej pracy agenta AI.

## Zawartość pakietu

- Krótki plik sterujący `AGENTS.md` kierujący do pozostałych elementów pakietu.
- Pliki w katalogu `docs/`: zasady pracy, polityka niezawodności, protokół przekazania oraz rubryka oceny recenzenckiej.
- Schematy JSON w katalogu `schemas/`: walidacja stanu, tablicy zadań oraz kontraktu zakresu prac.
- Skrypty w katalogu `scripts/`: inicjalizacja, pętla informacji zwrotnej (feedback loop), bramka weryfikacyjna oraz generator raportu przekazania.
- Idempotentny skrypt instalacyjny `bin/install.sh`.

## Szybki start

```
bin/install.sh
$EDITOR task_board.json
python3 scripts/init_agent.py
```

## Wersjonowanie

Wersja zdefiniowana w pliku `VERSION` stanowi kontrakt. Zmiany wersji głównej (major) mogą wymagać migracji stanu.
