---
name: skill-feature-selector
description: Podręczne drzewo decyzyjne do wyboru odpowiedniej metody selekcji cech
version: 1.0.0
phase: 2
lesson: 18
tags: [feature-selection, mutual-information, rfe, lasso, tree-importance]
---

# Strategia Wyboru Cech (Feature Selection Strategy)

Szybki przewodnik do wyboru i zastosowania odpowiedniej metody selekcji cech.

## Krok 1: Zacznij od oczyszczenia danych

Zanim zastosujesz jakąkolwiek metodę, usuń oczywiście bezużyteczne cechy:

- **Stałe cechy**: wariancja = 0. Usuń je.
- **Cechy prawie stałe**: wariancja < 0.01 (lub twój próg). Usuń je.
- **Zduplikowane cechy**: identyczne kolumny. Zostaw jedną, usuń resztę.
- **Kolumny z ID**: unikalne dla każdego rzędu, nie niosą informacji do generalizacji. Usuń je.

Trwa to sekundy, a może wyeliminować 10-30% cech w brudnych rzeczywistych zbiorach danych.

## Krok 2: Wybierz metodę na podstawie swojej sytuacji

### Szybkie Drzewo Decyzyjne

1. **< 50 cech?** Zacznij od rankingu opartego na informacji wzajemnej. Zachowaj K najlepszych.
2. **50 - 500 cech?** Najpierw użyj progu wariancji, a następnie L1 (Lasso) dla modelu liniowego, lub ważności drzewa jeśli korzystasz z drzew.
3. **> 500 cech?** Złącz metody: próg wariancji -> filtr informacji wzajemnej (najlepsze 50%) -> RFE na tych, które przetrwały.
4. **Potrzebujesz interpretowalności?** Regularyzacja L1 pozwala na odrzucenie zmiennych dzięki precyzyjnemu zerowaniu. Ważność drzewa podaje sklasyfikowane wyniki.
5. **Potrzebujesz wyłapać nieliniowe zależności?** Użyj informacji wzajemnej lub ważności opartej na drzewach. Unikaj L1 (tylko liniowe).
6. **Potrzebujesz zbadać interakcje pomiędzy cechami?** Użyj RFE lub ważności opartej na drzewach. Metody filtrujące omijają interakcje.

### Tabela Metod

| Metoda | Kiedy Używać | Kiedy Unikać |
|--------|------------|---------------|
| Próg wariancji | Zawsze, jako pierwszy krok | Nigdy nie pomijaj tego kroku |
| Informacja wzajemna | Szybki ranking, relacje nieliniowe | Gdy potrzebujesz wykrywania interakcji między cechami |
| RFE | Dokładna selekcja, umiarkowana liczba cech | Bardzo kosztowne modele, > 1000 cech |
| L1 / Lasso | Modele liniowe, szybka wbudowana selekcja | Problemy nieliniowe, wysoce skorelowane cechy |
| Ważność drzewa | Relacje nieliniowe, interakcje cech | Modele ukierunkowane (biased) na zmienne o wysokiej kardynalności |
| Ważność permutacji | Niezależna walidacja, finalne sprawdzenie | Zbyt wolna na potrzeby początkowego filtrowania |

## Krok 3: Waliduj dokonany wybór

- Porównaj wydajność modelu wykorzystującego wybrane cechy w stosunku do modelu ze wszystkimi cechami.
- Używaj walidacji krzyżowej (cross-validation), a nie tylko pojedynczego podziału na zbiór treningowy/testowy.
- Jeśli wydajność spadnie o ponad 1-2%, mogłeś usunąć użyteczne cechy.
- Jeśli wydajność się poprawiła, pomyślnie usunąłeś szum.

## Krok 4: Uważaj na typowe pułapki

### Skorelowane cechy
- L1 w sposób arbitralny wybiera jedną cechę z grupy skorelowanych i zeruje pozostałe.
- Najpierw policz macierz korelacji i zdecyduj, które ze skorelowanych cech zachować.
- Ważność na bazie drzew rozkłada wagę na poszczególne skorelowane cechy.

### Wyciek danych (Data leakage)
- Dopasowuj dobór cech wyłacznie na danych treningowych.
- Zastosuj ten sam zestaw do danych testowych.
- Podczas walidacji krzyżowej, dobór cech musi przebiegać wewnątrz każdego foldu.

### Przetrenowanie podczas selekcji cech
- RFE ze zbyt dużą liczbą iteracji może doprowadzić do przetrenowania na zestawie treningowym.
- Waliduj na danych nieużywanych w trakcie trenowania, a nie na tych z selekcji.
- Aby upewnić się o solidności metody, używaj metody tzw. stabilnego wyboru (powtarzanie na wielu podpróbkach danych).

## Krok 5: Lista kontrolna przed wdrożeniem

- [ ] Próg wariancji zastosowany jako pierwszy filtr
- [ ] Wybór cech (Feature selection) wytrenowany wyłącznie na danych treningowych
- [ ] Zdokumentowanie wybranych cech (nazwy, wykorzystana metoda, wyniki)
- [ ] Porównanie wyników: wybrane cechy względem wszystkich cech
- [ ] Zweryfikowano używając cross-validation (a nie zwykłego dzielenia zbioru)
- [ ] Wybór cech zintegrowany z potokiem treningowym (pipeline) - niewykonywany ręcznie
- [ ] Przygotowano monitorowanie dla zjawiska dryfu cech (feature drift) - wyselekcjonowane wcześniej cechy mogą przestać być użyteczne