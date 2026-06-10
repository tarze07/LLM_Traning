# Polityka niezawodności

Środowisko warsztatowe (workbench) radzi sobie z pięcioma najczęstszymi w branży scenariuszami awarii (trybami błędów):

1. Halucynowanie działań lub wyników — wykrywane za pomocą zestawu reguł i bramki weryfikacyjnej.
2. Rozrastanie się zakresu prac (scope creep) — wykrywane podczas analizy zmian (diff) pod kątem zgodności z kontraktem zakresu.
3. Błędy kaskadowe — blokowane przez mechanizm informacji zwrotnej i wymóg zakończenia weryfikacji kodem wyjścia 0.
4. Utrata kontekstu — eliminowana dzięki zapisywaniu stanu bezpośrednio w repozytorium (historia czatu nie jest jedynym źródłem prawdy).
5. Błędne użycie narzędzi — wykrywane na etapie weryfikacji w rubryce oceny recenzenckiej.

Polityka niezawodności jest automatycznie egzekwowana przez bramkę weryfikacyjną. Wszelkie odstępstwa (zastąpienia reguł) wymagają podpisu i podlegają audytowi — agenci nie mogą samodzielnie omijać zabezpieczeń.
