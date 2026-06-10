# Misja - Umowy dotyczące zakresu i granice zadań

## Cel
Napisz `scope_contract.json` dla każdego zadania i moduł sprawdzający uwzględniający globalność, który porównuje różnicę agenta z umową i zaznacza wszelkie zapisy zabronione lub wykraczające poza zakres.

## Wejścia
- Opis zadania z dozwolonymi i zabronionymi globusami, poleceniami akceptacji, akapitem dotyczącym wycofania i wymaganymi zatwierdzeniami
- Dwie serie demonstracyjne: jedna, która pozostaje w zasięgu, druga, która się skrada

## Elementy dostarczane
- Walidator schematu `scope_contract.json` (podzbiór schematu JSON, tablice glob)
- Parser różnicowy, który tworzy `RunSummary` z dotkniętych plików i uruchamianych poleceń
-`scope_check(contract, run) -> (violations, in_scope, off_scope)`
- `scope_report.json` zapisany obok skryptu

## Akceptacja
- `python3 code/main.py` wychodzi z zera
- Przebieg objęty zakresem zgłasza zero naruszeń
- Przebieg pełzający raportuje dokładne pliki spoza zakresu i przyczynę każdego z nich

## Poza zakresem
- Budżety czasowe, listy dozwolonych wyjść z sieci. Lekcja dotyczy kulek plików; polecenie ćwiczenia nakazuje jego przedłużenie.
- Podłączenie do przerwania wykonawczego. Lekcja kończy się na raporcie.

## Referencje
- `docs/en.md` - pełna lekcja
- `code/main.py` - implementacja referencyjna
- `outputs/skill-scope-contract.md` - wyodrębniona umiejętność