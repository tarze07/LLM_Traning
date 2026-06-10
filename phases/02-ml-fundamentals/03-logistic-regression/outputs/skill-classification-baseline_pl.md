---

name: skill-classification-baseline
description: Zanim sięgniesz po złożone modele, ustal solidną podstawę klasyfikacji
version: 1.0.0
phase: 2
lesson: 3
tags: [classification, logistic-regression, baseline, preprocessing]

---

# Przewodnik po klasyfikacji bazowej

Przed wypróbowaniem złożonych modeli ustal punkt bazowy za pomocą regresji logistycznej. Uczy się w ciągu kilku sekund, generuje prawdopodobieństwa i jest w pełni interpretowalny. Zaskakująca liczba problemów w świecie rzeczywistym nigdy nie wymaga niczego bardziej wymyślnego.

## Lista kontrolna decyzji

1. Czy granica decyzji jest prawdopodobnie liniowa?
   - Tak: regresja logistyczna prawdopodobnie będzie wystarczająca
   - Nie: nadal chcesz, aby był to punkt odniesienia do pomiaru poprawy

2. Ile masz funkcji?
   - Poniżej 50 lat: standardowa regresja logistyczna działa dobrze
   - 50 do 10 000: dodaj regularyzację L2 (grzbiet)
   - Ponad 10 000 (np. funkcje tekstowe TF-IDF): użyj regularyzacji L1 (Lasso) lub LinearSVC

3. Czy zbiór danych jest niezrównoważony?
   - Stosunek poniżej 5:1: prawdopodobnie w porządku bez regulacji
   - 5:1 do 50:1: użyj `class_weight="balanced"` w sklearn
   - Ponad 50:1: połącz wagę klasy z odpowiednią metryką (precyzja, przywołanie lub F1)

4. Czy cechy mają różną skalę?
   - Zawsze standaryzuj przed regresją logistyczną. Wykorzystuje optymalizację opartą na gradientach, a nieskalowane funkcje spowalniają zbieżność lub zniekształcają granicę decyzyjną.

5. Czy brakuje wartości?
   - Przypisz przed dopasowaniem. Regresja logistyczna nie obsługuje NaN.
   - Użyj przypisania mediany dla kolumn liczbowych, trybu dla kategorycznych.

## Kiedy regresja logistyczna jest wystarczająco dobra

- Klasyfikacja binarna z przeważnie liniowymi zależnościami cech
- Potrzebujesz wyników prawdopodobieństwa (nie tylko etykiet klas)
- Wymagana jest interpretowalność (współczynniki wskazują kierunek ważności cechy i względną wielkość po standaryzacji)
- Dane szkoleniowe są małe (od setek do tysięcy próbek)
- Potrzebujesz szybkiego modelu do serwowania w czasie rzeczywistym (iloczyn jednokropkowy przy wnioskowaniu)
- Wymogi regulacyjne lub dotyczące zgodności wymagają wyjaśnienia

## Kiedy dokonać aktualizacji

- Poziom dokładności znacznie poniżej wartości docelowej, a próbowałeś inżynierii funkcji
- Zależność między cechami a celem jest wyraźnie nieliniowa (sprawdź wykresy reszt)
- Masz duże dane tabelaryczne (ponad 10 tys. wierszy): spróbuj zwiększyć gradient (XGBoost lub LightGBM)
- Funkcje mają złożone interakcje, których funkcje wielomianowe nie są w stanie uchwycić
- Masz obraz, tekst lub dane sekwencyjne: regresja logistyczna na surowych danych wejściowych nie będzie działać

## Etapy wstępnego przetwarzania dla linii bazowej klasyfikacji

1. **Podział pociągu/testu** najpierw, przed jakimkolwiek przetwarzaniem wstępnym. Zapobiega to wyciekom danych.
2. **Obsługa brakujących wartości**: mediana przypisywania numerycznego, tryb przypisywania kategorycznego.
3. **Koduj kategorie**: jedna gorąca dla niskiej liczności (poniżej 10 wartości), docelowe kodowanie dla wyższej. Dopasuj kodowanie docelowe tylko do zakładek treningowych (użyj kodowania poza zakładką, aby zapobiec wyciekom).
4. **Skala liczbowa**: StandardScaler (średnia zerowa, wariancja jednostkowa). Zmieścić się w pociągu, przekształcić oba.
5. **Dopasuj regresję logistyczną** za pomocą `C=1.0` (domyślna regularyzacja).
6. **Oceń**: macierz zamieszania, precyzja, przywołanie, F1. Nie tylko dokładność.
7. **Próg dostrojenia**: wartość domyślna 0,5 rzadko jest optymalna. Przesuń od 0,1 do 0,9 i wybierz próg odpowiadający Twojemu priorytetowi precyzji/przywołania.

## Typowe błędy

- Ocena tylko dokładności na niezrównoważonych danych (model przewidujący klasę większościową ma wysokie wyniki, ale jest bezużyteczny)
- Zapominanie o skalowaniu funkcji (regresja logistyczna z nieskalowanymi funkcjami uczy się powoli i prowadzi do gorszego rozwiązania)
- Wykorzystanie zestawu testowego do dostrojenia progu decyzyjnego (użyj walidacji lub walidacji krzyżowej)
- Pominięcie linii bazowej i przejście od razu do XGBoost (tracisz interpretowalność i nie masz punktu odniesienia)
- Nie sprawdzanie współliniowości (silnie skorelowane cechy zwiększają wariancję współczynnika)

## Szybkie odniesienie

| Scenariusz | Modelka | Regularyzacja | Ustawienie klucza |
|---------|-------|--------------|------------|
| Niewiele funkcji, które można zinterpretować | Regresja logistyczna | L2 (domyślnie) | C=1,0 |
| Wiele funkcji, niektóre nieistotne | Regresja logistyczna | L1 | kara="l1",solver="saga" |
| Bardzo przyciemniony, rzadki (tekst) | Klasyfikator SGD | L1 lub ElasticNet | strata="log_strata" |
| Niezrównoważone klasy | Regresja logistyczna | L2 | class_weight="zrównoważony" |
| Potrzebujesz prawdopodobieństw | Regresja logistyczna | L2 | przewidywać_proba() |
| Potrzebujesz tylko etykiet klas | LiniowySVC | L2 | Szybciej niż LR dla dużych danych |