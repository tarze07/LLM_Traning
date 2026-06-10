---
name: skill-svm-kernel-chooser
description: Wybierz odpowiednie jądro (kernel) SVM i dostrój parametry C oraz gamma do swojego problemu
version: 1.0.0
phase: 2
lesson: 5
tags: [svm, kernel, classification, hyperparameter-tuning]
---

# Przewodnik po wyborze jądra SVM

Modele SVM (Support Vector Machines) definiuje się poprzez dwie kluczowe decyzje: wybór jądra (które określa kształt granicy decyzyjnej) oraz parametry regularyzacji (które kontrolują kompromis między szerokością marginesu a błędami klasyfikacji). Właściwy dobór tych ustawień decyduje o tym, czy model będzie bezużyteczny, czy wysoce skuteczny.

## Lista kontrolna

1. Czy dane są liniowo separowalne (lub zbliżone do takich)?
   - Tak: użyj jądra liniowego (linear). Jest znacznie szybsze i łatwiejsze w interpretacji.
   - Nie: przejdź do kroku 2.

2. Jaki jest stosunek liczby cech (features) do liczby próbek?
   - Liczba cech >> liczba próbek (np. tekst z reprezentacją TF-IDF): użyj jądra liniowego. Dane wielowymiarowe często można rozdzielić liniowo. Jądro RBF w tym przypadku jedynie zwiększy złożoność modelu, nie dając wymiernych korzyści.
   - Liczba próbek >> liczba cech (np. dane tabelaryczne z 10-50 cechami): domyślnym wyborem jest jądro RBF.

3. Czy oczekujesz, że granica decyzyjna będzie gładka?
   - Gładka, nieliniowa granica: jądro RBF.
   - Granica w kształcie krzywej wielomianowej: jądro wielomianowe (zacznij od stopnia 2 lub 3).
   - Wiedza dziedzinowa sugeruje określone interakcje między zmiennymi: jądro wielomianowe o odpowiednio dobranym stopniu.

4. Jak duży jest zbiór danych?
   - Poniżej 10 000 próbek: sprawdzi się każde jądro, RBF to bezpieczny wybór domyślny.
   - Od 10 000 do 100 000 próbek: jądro liniowe lub model `LinearSVC` (rozwiązanie problemu pierwotnego, ang. primal, złożoność O(n) na epokę).
   - Powyżej 100 000 próbek: unikaj modeli SVM z nieliniowymi jądrami. Rozważ użycie liniowego SVM, gradient boostingu lub sieci neuronowych.

5. Czy cechy zostały przeskalowane?
   - Modele SVM bezwzględnie wymagają skalowania cech. Zawsze stosuj standaryzację (średnia równa zero, wariancja jednostkowa) przed trenowaniem modelu. Nieskalowane cechy całkowicie zniekształcają geometrię marginesu.

## Schemat wyboru jądra

```
Start
  |
  v
Liczba cech > 1000 lub cechy >> próbki?
  Tak --> Jądro liniowe (LinearSVC dla szybkości)
  Nie --> Zbiór danych < 10k próbek?
            Tak --> Najpierw wypróbuj RBF (najlepsze uniwersalne jądro)
            Nie --> Jądro liniowe (złożoność nieliniowych SVM wynosi od O(n^2) do O(n^3))
```

Jeśli RBF nie daje zadowalających wyników, wypróbuj jądro wielomianowe stopnia 2 lub 3. Jeśli i to zawiedzie, być może twój problem nie nadaje się do rozwiązywania za pomocą maszyn wektorów nośnych (SVM).

## Dostrajanie parametru C (Regularyzacja)

Parametr `C` kontroluje karę za błędną klasyfikację próbek treningowych. Jest odwrotnie proporcjonalny do siły regularyzacji.

| Wartość C | Efekt | Kiedy używać |
|--------|--------|------------|
| 0,001 - 0,01 | Szeroki margines, dozwolone liczne naruszenia marginesu. | Zaszumione dane, zależy nam na dużej zdolności do uogólniania (generalizacji). |
| 0,1 - 1,0 | Model zrównoważony. | Dobry zakres początkowy. |
| 10 - 1000 | Wąski margines, niewiele naruszeń dopuszczalnych. | Czyste dane, wymagana jest wysoka dokładność na zbiorze treningowym. |

Strategia strojenia:
- Rozpocznij od C=1,0.
- Przeszukuj przestrzeń w skali logarytmicznej: [0,001, 0,01, 0,1, 1, 10, 100, 1000].
- Wykorzystaj walidację krzyżową (cross-validation) do wyboru optymalnej wartości.
- Jeśli najlepsze zidentyfikowane `C` znajduje się na skraju testowanego przedziału, rozszerz zakres poszukiwań w tym kierunku.

## Dostrajanie parametru gamma (Dla jądra RBF)

Parametr `gamma` określa zasięg wpływu pojedynczej próbki treningowej. Kontroluje szerokość funkcji Gaussa.

| Wartość gamma | Efekt | Kiedy używać |
|------------|------------|------------|
| Mała (0,001) | Każdy punkt wpływa na rozległy obszar. Granica decyzyjna jest gładka i prosta. | Zjawisko niedopasowania (underfitting) lub niewielka liczba cech. |
| Średnia (auto: 1/n_features) | Domyślne ustawienie w bibliotece scikit-learn. Rozsądny punkt wyjścia. | Ogólnego przeznaczenia. |
| Duża (10+) | Każdy punkt oddziałuje tylko na swoich najbliższych sąsiadów. Złożona, poszarpana granica. | Wysokie ryzyko przeuczenia (overfitting). |

Strategia strojenia:
- Zacznij od `gamma="scale"` (czyli `1 / (n_features * X.var())`, co jest domyślne w sklearn).
- Przeszukuj przestrzeń w skali logarytmicznej: [0,001, 0,01, 0,1, 1, 10].
- Niska wartość `gamma` i wysokie `C` mają tendencję do prowadzenia do przeuczenia.
- Wysoka wartość `gamma` i niskie `C` mogą skutkować niedopasowaniem modelu.

## Równoczesne dostrajanie C i gamma

Parametry `C` i `gamma` wchodzą w silne interakcje. Zawsze dostrajaj je wspólnie, nigdy niezależnie.

Rekomendowane podejście:
1. Zgrubne przeszukiwanie siatki (grid search): `C` w zakresie [0,01, 0,1, 1, 10, 100], `gamma` w zakresie [0,001, 0,01, 0,1, 1, 10] (łącznie 25 kombinacji).
2. Zidentyfikuj najlepszy region.
3. Precyzyjne przeszukiwanie w pobliżu najlepszego regionu (np. `C` w [5, 10, 20, 50], `gamma` w [0,05, 0,1, 0,2]).
4. Na każdym etapie stosuj 5-krotną walidację krzyżową (5-fold CV).

## Typowe błędy

- Stosowanie jądra RBF do rzadkich (sparse) danych wielowymiarowych (jądro liniowe jest tutaj znacznie lepsze i 100-krotnie szybsze).
- Zapominanie o standaryzacji cech (to najczęstszy błąd przy pracy z SVM).
- Ustawianie zbyt wysokiego parametru `C` dla mocno zaszumionych danych (model uczy się szumu na pamięć zamiast szukać ogólnych reguł).
- Próby używania nieliniowych maszyn SVM dla zbiorów powyżej 50 tys. próbek (czas trenowania staje się wręcz zaporowy).
- Niezależne optymalizowanie `C` i `gamma` (parametry te nawzajem się kompensują).
- Ustawianie jądra wielomianowego od razu na 5. stopień lub wyżej (jest to bardzo agresywne dopasowanie, najpierw należy sprawdzić stopień 2. lub 3.).

## Szybkie podsumowanie

| Jądro (Kernel) | Zastosowanie | Kluczowe parametry | Złożoność czasowa treningu |
|------------|------------|----------------|--------------------------------|
| Liniowe | Tekst/TF-IDF, duża liczba cech, duże zbiory danych. | Tylko C | O(n) na epokę |
| RBF | Uniwersalne, zbiory poniżej 10 tys. próbek. | C, gamma | Od O(n^2) do O(n^3) |
| Wielomianowe | Znane nieliniowe, wielomianowe relacje między cechami. | C, degree (stopień), coef0 | Od O(n^2) do O(n^3) |
| Sigmoidalne | Rzadko stosowane (zbliżone do dwuwarstwowej sieci neuronowej). | C, gamma, coef0 | Od O(n^2) do O(n^3) |
