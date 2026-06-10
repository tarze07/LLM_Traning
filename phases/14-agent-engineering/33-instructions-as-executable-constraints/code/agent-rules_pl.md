# Zasady agenta

## plik startowy/stanowy-świeży
- kategoria: startupy
- sprawdź: state_file_fresh
Agent musi przeczytać plik agent_state.json przed wywołaniem dowolnego narzędzia.

## zabronione/niedopuszczalne-edycje-skryptu
- kategoria: zabronione
- sprawdź: no_release_script_edits
Nigdy nie edytuj skryptów/release.sh poza zatwierdzonym zadaniem wydania.

## zrobione/testy-zaliczone
- kategoria: definicja_wykonania
- sprawdź: testy_pass
Zadanie jest wykonywane tylko wtedy, gdy jego polecenie akceptacji wychodzi z zera.

## niepewność/notatka z pytaniami otwartymi
- kategoria: niepewność
- sprawdź: opens_question_when_unsure
Kiedy pewność siebie jest poniżej progu, zamiast zgadywać, napisz notatkę z pytaniem.

## zatwierdzenie/nowa-zależność
- kategoria: homologacja
- sprawdź: new_dependent_approved
Dodanie zależności środowiska wykonawczego wymaga wyraźnej zgody człowieka.