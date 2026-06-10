# Zasady pracy agenta

## Inicjalizacja / Aktualność stanu
- Kategoria: inicjalizacja
- Sprawdzenie: state_file_fresh
Agent ma obowiązek odczytać plik agent_state.json przed wywołaniem jakiegokolwiek innego narzędzia.

## Strefy zakazane / Zapisy poza zakresem
- Kategoria: zabronione
- Sprawdzenie: no_out_of_scope_writes
Nigdy nie edytuj plików leżących poza zakresem określonym w kontrakcie aktywnego zadania.

## Kryteria ukończenia / Zaliczenie testów
- Kategoria: definicja_wykonania
- Sprawdzenie: testy_pass
Zadanie uważa się za wykonane tylko wtedy, gdy każde polecenie weryfikujące (akceptacyjne) kończy się kodem wyjścia 0.

## Obsługa niepewności / Pytania otwarte
- Kategoria: niepewność
- Sprawdzenie: opens_question_when_unsure
Jeśli poziom pewności spada poniżej określonego progu, nie zgaduj — utwórz nową notatkę z pytaniem.

## Akceptacja zmian / Nowe zależności
- Kategoria: zatwierdzanie
- Sprawdzenie: new_dependent_approved
Dodanie nowej zależności uruchomieniowej (runtime dependency) wymaga wyraźnej akceptacji ze strony człowieka.
