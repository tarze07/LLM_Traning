# Reguły agenta

## rozruch/aktualny-stan
- kategoria: rozruch
- sprawdź: state_file_fresh
Agent musi odczytać plik agent_state.json przed uruchomieniem jakiegokolwiek narzędzia.

## zabronione/modyfikacja-skryptu-wydania
- kategoria: zabronione
- sprawdź: no_release_script_edits
Nigdy nie modyfikuj skryptu `scripts/release.sh` poza zatwierdzonym zadaniem wydania (release task).

## ukonczenie/testy-zaliczone
- kategoria: definicja_zakonczenia
- sprawdź: testy_pass
Zadanie uznaje się za ukończone tylko wtedy, gdy jego polecenie weryfikujące kończy się kodem wyjścia zero.

## niepewnosc/pytania-otwarte
- kategoria: niepewnosc
- sprawdź: opens_question_when_unsure
Gdy poziom pewności spadnie poniżej progu, zamiast zgadywać rozwiązanie, utwórz notatkę z pytaniem.

## zatwierdzenie/nowa-zaleznosc
- kategoria: zatwierdzenie
- sprawdź: new_dependent_approved
Dodanie nowej zależności środowiska uruchomieniowego wymaga wyraźnej zgody człowieka.
