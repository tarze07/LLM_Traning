# Misja - Umowy dotyczące zakresu i granice zadań

## Cel
Napisz `scope_contract.json` dla każdego zadania oraz moduł sprawdzający (obsługujący dopasowania glob), który porównuje zmiany (diff) agenta z umową i flaguje wszelkie modyfikacje zabronione lub wykraczające poza zakres.

## Wejścia
- Opis zadania zawierający dozwolone i zabronione wzorce glob, polecenia weryfikujące (acceptance commands), opis procedury wycofania zmian oraz wymagane zgody (approvals)
- Dwa przebiegi demonstracyjne: jeden mieszczący się w zakresie, a drugi wykraczający poza niego

## Produkty (Deliverables)
- Walidator schematu `scope_contract.json` (podzbiór JSON Schema z tablicami wzorców glob)
- Parser zmian (diff), który generuje obiekt `RunSummary` na podstawie zmodyfikowanych plików i uruchomionych poleceń
- Funkcja `scope_check(contract, run) -> (violations, in_scope, off_scope)`
- Raport `scope_report.json` zapisany w tym samym katalogu co skrypt

## Kryteria akceptacji
- Polecenie `python3 code/main.py` kończy działanie z kodem wyjścia 0
- Przebieg zgodny z zakresem nie wykazuje żadnych naruszeń
- Przebieg wykraczający poza zakres raportuje konkretne pliki spoza zakresu oraz przyczynę każdego z naruszeń

## Poza zakresem
- Budżet czasowy oraz listy dozwolonych połączeń sieciowych wychodzących (egress). Lekcja skupia się na dopasowaniach plików za pomocą wzorców glob; rozszerzenie tych funkcjonalności jest częścią ćwiczeń.
- Integracja z przerwaniami środowiska uruchomieniowego. Lekcja kończy się na etapie generowania raportu.

## Materiały odniesienia
- `docs/en.md` – pełna lekcja
- `code/main.py` – implementacja referencyjna
- `outputs/skill-scope-contract.md` – wyodrębniona umiejętność
