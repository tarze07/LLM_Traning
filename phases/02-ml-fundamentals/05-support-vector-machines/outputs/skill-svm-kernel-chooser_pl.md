---

name: skill-svm-kernel-chooser
description: Wybierz odpowiednie jądro SVM i dostrój C i gamma do swojego problemu
version: 1.0.0
phase: 2
lesson: 5
tags: [svm, kernel, classification, hyperparameter-tuning]

---

# Przewodnik wyboru jądra SVM

Maszyny SVM są definiowane przez dwie opcje: jądro (które określa kształt granicy decyzyjnej) i parametry regularyzacji (które kontrolują kompromis między szerokością marginesu a błędami klasyfikacji). Właściwe wykonanie tego stanowi różnicę między bezużytecznym modelem a mocnym.

## Lista kontrolna decyzji

1. Czy dane można separować liniowo (lub blisko tego)?
   - Tak: użyj jądra liniowego. Jest szybszy i bardziej zrozumiały.
   - Nie: przejdź do kroku 2.

2. Ile funkcji w porównaniu z próbkami?
   - Funkcje >> próbki (np. tekst z TF-IDF): użyj jądra liniowego. Dane wielowymiarowe są często rozdzielane liniowo. RBF dodaje złożoności bez żadnych korzyści.
   - Próbki >> cechy (np. dane tabelaryczne z 10-50 cechami): Jądro RBF jest wyborem domyślnym.

3. Czy oczekuje się, że granica decyzyjna będzie gładka?
   - Gładka, ciągła granica: jądro RBF
   - Granica w kształcie wielomianu: jądro wielomianu (zacznij od stopnia 2 lub 3)
   - Znajomość dziedziny sugeruje określone terminy interakcji: jądro wielomianowe z pasującym stopniem

4. Jak duży jest zbiór danych?
   - Poniżej 10 000 próbek: działa każde jądro, RBF jest bezpiecznym ustawieniem domyślnym
   - 10 000 do 100 000: jądro liniowe lub LinearSVC (sformułowanie pierwotne, O(n) na epokę)
   - Ponad 100 000: nie używaj SVM jądra. Przejdź na liniowy SVM, wzmacnianie gradientu lub sieci neuronowe.

5. Czy skalowałeś funkcje?
   — Maszyny SVM wymagają skalowania funkcji. Zawsze standaryzuj (średnia zerowa, wariancja jednostkowa) przed dopasowaniem. Nieskalowane obiekty zniekształcają geometrię marginesu.

## Schemat wyboru jądra

```
Start
  |
  v
Features > 1000 or features >> samples?
  Yes --> Linear kernel (LinearSVC for speed)
  No  --> Dataset < 10k samples?
            Yes --> Try RBF first (best general-purpose kernel)
            No  --> Linear kernel (kernel SVMs are O(n^2) to O(n^3))
```

Jeśli RBF nie działa dobrze, wypróbuj stopień wielomianu 2-3. Jeśli to się nie powiedzie, problem może nie być dostosowany do maszyn SVM.

## Strojenie C (regularyzacja)

C kontroluje karę za błędne klasyfikacje. Jest odwrotnie powiązana z siłą regularyzacji.

| Wartość C | Efekt | Kiedy używać |
|--------|--------|------------|
| 0,001 - 0,01 | Szeroki margines, dozwolone wiele naruszeń | Zaszumione dane, chcę uogólnienia |
| 0,1 - 1,0 | Zrównoważony | Dobry zasięg początkowy |
| 10 - 1000 | Wąski margines, kilka naruszeń | Czyste dane, wymagają dużej dokładności |

Strategia strojenia:
- Zacznij od C=1,0
- Szukaj w skali logarytmicznej: [0,001, 0,01, 0,1, 1, 10, 100, 1000]
- Użyj walidacji krzyżowej, aby wybrać najlepszą wartość
- Jeśli najlepsze C znajduje się na granicy twojego zasięgu, rozszerz zasięg w tym kierunku

## Strojenie gamma (jądro RBF)

Gamma kontroluje, jak daleko sięga wpływ pojedynczego punktu treningowego. Określa szerokość Gaussa.

| wartość gamma | Efekt | Kiedy używać |
|------------|------------|------------|
| Mały (0,001) | Każdy punkt wpływa na duży obszar. Gładka, prosta granica | Niedopasowanie lub kilka funkcji |
| Średni (automatyczny: 1/n_features) | sklearn domyślny. Rozsądny punkt wyjścia | Ogólne zastosowanie |
| Duże (10+) | Każdy punkt wpływa tylko na pobliskie punkty. Złożona, falista granica | Ryzyko przeuczenia |

Strategia strojenia:
- Zacznij od gamma="scale" (1 / (n_features * X.var()), wartość domyślna sklearn)
- Szukaj w skali logarytmicznej: [0,001, 0,01, 0,1, 1, 10]
- Niska gamma + wysokie C mają tendencję do nadmiernego dopasowania
- Wysoka gamma + niska C ma tendencję do niedopasowania

## Wspólne strojenie C i gamma

C i gamma oddziałują. Zawsze dostrajaj je razem, a nie niezależnie.

Zalecane podejście:
1. Zgrubne wyszukiwanie siatki: C w [0,01, 0,1, 1, 10, 100], gamma w [0,001, 0,01, 0,1, 1, 10] (25 kombinacji)
2. Znajdź najlepszy region
3. Przeszukiwanie dokładnej siatki wokół najlepszego regionu (np. C w [5, 10, 20, 50], gamma w [0,05, 0,1, 0,2])
4. W całym procesie stosuj 5-krotną weryfikację krzyżową

## Typowe błędy

- Używanie jądra RBF na rzadkich danych wielowymiarowych (liniowe jest lepsze i 100 razy szybsze)
- Zapominanie o skalowaniu funkcji (najczęstszy błąd SVM)
- Ustawienie C zbyt wysoko w przypadku zaszumionych danych (zapamiętuje szum zamiast uczyć się granicy)
- Używanie jądra SVM na zbiorach danych obejmujących ponad 50 tys. próbek (czas szkolenia jest zaporowy)
- Nie dostrajanie C i gamma razem (kompensują się nawzajem)
- Domyślnie stopień wielomianu 5+ (agresywne dopasowanie, spróbuj najpierw 2 lub 3)

## Szybkie odniesienie

| Jądro | Kiedy używać | Kluczowe parametry | Złożoność treningu |
|------------|------------|----------------|--------------------------------|
| Liniowy | Tekst/TF-IDF, wiele funkcji, duże dane | Tylko C | O(n) na epokę |
| RBF | Ogólnego przeznaczenia, poniżej 10 tys. próbek | C, gamma | O(n^2) do O(n^3) |
| Wielomian | Znane zależności wielomianowe | C, stopień, współczynnik0 | O(n^2) do O(n^3) |
| Sigmoida | Rzadko przydatne (odpowiednik dwuwarstwowej sieci neuronowej) | C, gamma, coef0 | O(n^2) do O(n^3) |