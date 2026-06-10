---

name: sleeper-audit
description: Zweryfikuj (przeprowadź audyt) raport z procesu wyrównywania pod kątem tego, czy skutecznie wykazuje on usunięcie wszczepionego lub podejrzewanego backdooru.
version: 1.0.0
phase: 18
lesson: 7
tags: [sleeper-agents, backdoor, alignment-training, adversarial-training, probes]

---

Na podstawie raportu deklarującego usunięcie szkodliwego zachowania z modelu (za pomocą SFT, RLHF, treningu adwersaryjnego lub ich kombinacji), zweryfikuj, czy skuteczność tej procedury została wykazana zgodnie ze standardem modelu zagrożeń Hubingera i in. (2024).

Przygotuj:

1. Zakres wstrzymanych testów (holdout evaluation). Czy w raporcie przedstawiono wyniki ewaluacji na wyzwalaczach, które nigdy nie były wykorzystywane w procesie szkoleniowym? Jeśli jedynym kryterium oceny jest zbiór testowy red-teamu wykorzystany do treningu, usunięcie backdooru uznaje się za niepotwierdzone.
2. Charakterystyka wyzwalacza. Czy zidentyfikowany trigger to prosty ciąg znaków, przesunięcie dystrybucyjne czy cecha środowiskowa (data, token, długość kontekstu)? Ogólność wyzwalacza definiuje wielkość przestrzeni poszukiwań, którą musi pokryć zespół red-teamingowy.
3. Ewaluacja stanów wewnętrznych. Czy w procesie weryfikacji zastosowano sondy strumienia rezydualnego, kodery SAE (Sparse Autoencoders) lub inne mechanistyczne metody analizy, aby sprawdzić obecność reprezentacji wyzwalacza w wagach modelu (nawet przy poprawnym zachowaniu zewnętrznym)? Zgodnie z analizami Anthropic z kwietnia 2024 r., wewnętrzna liniowa reprezentacja wyzwalacza pozostaje czytelna nawet po zablokowaniu szkodliwego zachowania na poziomie wyjścia.
4. Monitorowanie potoku treningowego. Czy proces usunięcia weryfikowano na każdym kolejnym etapie modyfikacji modelu (dalsze SFT, kolejne iteracje RLHF, łączenie adapterów, destylacja)? Backdoory wykazują wysoką odporność na pętle optymalizacyjne – ewaluacji musi podlegać ostateczna wersja produkcyjna modelu, a nie przejściowe punkty kontrolne (checkpoints).
5. Skalowanie wyników. Jeśli deklarowane usunięcie wykazano na modelu o mniejszej liczbie parametrów, weź pod uwagę Rysunek 4 z pracy Hubinger i in. (2024) wskazujący, że trwałość backdooru rośnie wraz ze skalą modelu. Wyniki uzyskane na mniejszych jednostkach nie uogólniają się automatycznie na większe modele.

Bezwzględne odrzucenia (błędy merytoryczne):
- Twierdzenia typu „zastosowaliśmy RLHF, więc model jest w pełni bezpieczny” bez przedstawienia rzetelnych dowodów z wstrzymanych testów (holdout evaluation).
- Wnioski opierające się wyłącznie na ewaluacji w rozkładzie red-teamingu (gdy dane treningowe i ewaluacyjne pochodzą z tego samego zbioru).
- Deklarowanie usunięcia backdooru bez przeprowadzenia analizy stanów wewnętrznych w sytuacjach, gdy pierwotny mechanizm implantacji (wyzwalacz) pozostaje nieznany.

Zasady udzielania odpowiedzi (odmowy):
- Jeśli użytkownik pyta, czy „RLHF jest w stanie usunąć zwodnicze wyrównanie”, odmów udzielenia jednoznacznej odpowiedzi tak/nie. Skieruj go do Sekcji 5 (dotyczącej trwałości backdoorów) oraz Sekcji 6 (analizującej rolę łańcucha myśli) w pracy Hubingera i in. (2024).
- Jeśli użytkownik żąda podania wartości liczbowej określającej prawdopodobieństwo ukrytego oszustwa (decepcji), odmów. Wyjaśnij, że prawdopodobieństwa a priori (base rates) nie są znane, a dowody empiryczne dotyczą trwałości backdoorów w kontrolowanych organizmach modelowych, a nie częstotliwości ich spontanicznego powstawania w standardowym procesie treningowym.

Dane wyjściowe: Jednostronicowy raport z audytu, który mapuje treść raportu bezpieczeństwa na 5 powyższych wymiarów kontrolnych, wskazuje obszary pominięte i definiuje kluczowe nieuwzględnione zagrożenia. W tekście należy dokładnie raz zacytować pracę Hubingera i in. (arXiv:2401.05566) jako definicję bazowego modelu zagrożeń.
