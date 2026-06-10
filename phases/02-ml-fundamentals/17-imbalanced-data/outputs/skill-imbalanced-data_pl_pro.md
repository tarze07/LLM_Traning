---
name: skill-imbalanced-data
description: Kompletna strategia i lista kontrolna decyzyjna do optymalizacji rozwiązań w problemach klasyfikacji dla silnie niezrównoważonych zbiorów danych.
version: 1.0.0
phase: 2
lesson: 17
tags: [imbalanced-data, smote, class-weights, threshold-tuning, evaluation]
---

# Strategia Pracy z Niezrównoważonymi Danymi (Imbalanced Data Strategy)

Poniższa lista kontrolna posłuży Ci jako rzetelny przewodnik w podejmowaniu świadomych decyzji architektonicznych podczas pracy nad problemami klasyfikacji na niezrównoważonych zbiorach danych. Przejdź przez kolejne kroki, aby metodycznie i poprawnie dobrać najbardziej efektywne rozwiązanie.

## Krok 1: Wymierny pomiar skali nierównowagi

- Precyzyjnie zlicz liczbę próbek dostępnych w obrębie każdej z klas.
- Oblicz dokładny współczynnik nierównowagi (rozmiar klasy większościowej podzielony przez rozmiar klasy mniejszościowej).
- **Niska nierównowaga:** stosunek wynosi < 3:1 (np. podział 70/30).
- **Umiarkowana nierównowaga:** stosunek mieści się w przedziale od 3:1 do 20:1 (np. podział 95/5).
- **Skrajna nierównowaga (Severe):** stosunek wynosi > 20:1 (np. podział 99/1).

## Krok 2: Kontekstowy dobór metryk ewaluacyjnych

Podczas analizowania niezrównoważonych zbiorów absolutnie zrezygnuj z klasycznej miary dokładności (accuracy) na rzecz wskaźników takich jak precyzja (precision), czułość (recall) czy miara F1. Świadomie dobierz optymalną metrykę odpowiadającą Twojemu konkretnemu zagadnieniu biznesowemu:

| Scenariusz biznesowy | Główne kryterium oceny (Metryka pierwszorzędowa) | Wskaźnik pomocniczy (Metryka drugorzędowa) |
|----------|---------------|--------------------------------|
| Przypadki, gdzie przeoczenie klasy pozytywnej generuje ogromne koszty (np. systemy antyfraudowe, diagnostyka nowotworów) | Czułość (Recall) | F2-score |
| Przypadki, gdzie to fałszywe alarmy generują wysokie obciążenia (np. agresywne filtry antyspamowe, drażniące rekomendacje) | Precyzja (Precision) | F0.5-score |
| Oba typy pomyłek są postrzegane jako mniej więcej równie kosztowne biznesowo | F1-score | MCC (Matthews Correlation Coefficient) |
| Wymagana jest pojedyncza, ujednolicona metryka rankingowa | AUPRC (Area Under the Precision-Recall Curve) | AUC-ROC |
| Analiza i porównywanie wyników pomiędzy wieloma różnymi zbiorami danych | MCC | AUPRC |

## Krok 3: Wybór optymalnej strategii przywracania równowagi (Rebalancing)

### Według stopnia nierównowagi

| Stopień Nierównowagi | Strategia pierwszego wyboru | Strategia drugiego wyboru | Działania, których należy stanowczo unikać |
|---------------|-----------|------------|-------|
| Niska (< 3:1) | Skalowanie wag klas (Class weights) | Optymalizacja progu decyzyjnego (Threshold tuning) | Oversamplingu (generuje niepotrzebny narzut obliczeniowy i ryzyko) |
| Umiarkowana (3:1 do 20:1) | SMOTE skorelowany z wagami klas | Nałożenie dodatkowej optymalizacji progu na w/w metody | Undersamplingu (skutkuje dotkliwą i niepotrzebną utratą ważnych informacji) |
| Skrajna (> 20:1) | Hybryda: SMOTE + wagi klas + próg decyzyjny | Podejście zespołowe: Zrównoważony Bagging (Balanced Bagging Ensemble) | Czystego, losowego undersamplingu |

### Według całkowitego rozmiaru zbioru danych

| Skala (Rozmiar zbioru) | Preferowana strategia działania | Merytoryczne uzasadnienie |
|------------|----------------------|-------|
| < 1 000 próbek | Powszechny Oversampling lub SMOTE | Nie możesz pozwolić sobie na odrzucenie chociażby pojedynczej próbki z danych klasy większościowej. |
| 1 000 - 10 000 próbek | SMOTE wspomagany optymalizacją progu | Obecna jest już zazwyczaj wystarczająca liczba próbek w klasie mniejszościowej, aby algorytm k-NN (wewnątrz SMOTE) działał wiarygodnie. |
| > 10 000 próbek | Standardowe wagi klas lub Undersampling | Cechuje się dużą szybkością wykonania, a danych z klasy mniejszościowej jest obiektywnie na tyle dużo, że sieć i tak wyłapie kluczowe wzorce. |

## Krok 4: Wdrożenie i egzekucja wybranej techniki

### Wagi klas (Class Weights - absolutnie zawsze testuj jako pierwsze)
- W środowisku scikit-learn realizowane prosto przez dodanie argumentu: `class_weight='balanced'`.
- Rozwiązanie to w ogóle nie wymaga fizycznej modyfikacji czy transformacji pierwotnego zbioru danych.
- Bezproblemowo i natywnie działa z niemal każdym modelem, którego mechanizm uczenia opiera się na optymalizacji funkcji straty.
- Wynikowo daje efekt w pełni i matematycznie równoważny nadpróbkowaniu (oversamplingowi) w ujęciu wartości oczekiwanej.

### Algorytm SMOTE (Synthetic Minority Over-sampling Technique)
- **Krytyczne:** Aplikuj ten algorytm absolutnie i wyłącznie na zbiorze treningowym (nigdy nie odpalaj go na zbiorze walidacyjnym ani testowym).
- W typowych uwarunkowaniach używaj $k=5$ najbliższych sąsiadów (jest to powszechnie akceptowana wartość domyślna).
- W celu maksymalizacji finalnej jakości modelu, rutynowo łącz tę technikę z zastosowaniem wag klas.
- Bądź niezwykle wyczulony na ryzyko generowania mocno zaszumionych, mało wiarygodnych punktów syntetycznych w newralgicznych rejonach blisko granicy decyzyjnej.

### Zaawansowana Optymalizacja Progu (Threshold Tuning)
- Klasycznie wytrenuj swój model, a następnie wyodrębnij prognozowane, czyste prawdopodobieństwa, bazując stricte na oddzielnym, niezależnym zestawie walidacyjnym.
- Przeprowadź systematyczne badanie (tzw. sweep) potencjalnych progów operacyjnych (np. w szerokim zakresie od 0,05 aż do 0,95).
- Docelowo wyselekcjonuj ten próg, który w sposób jednoznaczny maksymalizuje wcześniej wybraną, kluczową dla Ciebie metrykę.
- **Złota zasada:** proces doboru (strojenia) tego progu zawsze musi opierać się o odrębne dane walidacyjne. Kategorycznie nie wolno używać do tego celu danych testowych.

## Krok 5: Poprawność i sterylność procesów walidacyjnych

- Jako normę powszechnie stosuj tzw. **warstwową walidację krzyżową** (Stratified Cross-Validation), która rygorystycznie gwarantuje i zachowuje oryginalne, naturalne proporcje klas we wszystkich izolowanych podziałach (foldach).
- Finalne raporty i metryki opieraj wyłączenie na wynikach wygenerowanych z całkowicie oryginalnego (w ogóle nie modyfikowanego, nie poddanego resamplingowi) i sterylnego zbioru testowego.
- Przestrzegaj fundamentalnej zasady: absolutnie nigdy nie aplikuj techniki SMOTE na całym, spłaszczonym zbiorze danych przed jego operacyjnym podziałem - transformacje te muszą bezwarunkowo odbywać się wyłącznie i odizolowanie wewnątrz poszczególnych przebiegów treningowych.
- Swoje rozwiązania rutynowo i systematycznie porównuj z wynikami prostego naiwnego punktu odniesienia (np. fikcyjnego modelu, opierającego swoje działanie na stałym prognozowaniu przynależności do klasy większościowej).

## Krok 6: Rejestr nagminnych i krytycznych błędów (Czego unikać)

- Zastosowania metody SMOTE do całości posiadanego zbioru danych jeszcze przed wykonaniem czystego podziału trening/test (to fatalny i podręcznikowy przykład wycieku danych - data leakage).
- Bezrefleksyjnego opierania się i raportowania klasycznej dokładności (accuracy) jako wiodącego wskaźnika przy ewaluacji skuteczności modelu.
- Pominięcia początkowej i prostej weryfikacji rezultatów dających przez samo wprowadzenie wag klas (jest to najprostsze technicznie podejście i nader często okazuje się w zupełności wystarczające w praktyce).
- Brutalnego oversamplingu wykonanego statycznie przed inicjacją procesu walidacji krzyżowej (zduplikowane i wygenerowane syntetyczne próbki bezwiednie "wyciekają" z treningu do strefy weryfikacyjnej fałszując obraz modelu).
- Bagatelizowania lub całkowitego zignorowania potężnej procedury optymalizacji progu odcięcia (to darmowy i w pełni zyskowny krok operacyjny, zupełnie niewymagający ponownego, kosztownego trenowania sieci).
- Mechanicznego używania losowego undersamplingu na wyjątkowo małych zbiorach danych (z racji wyrzucenia w ten sposób zbytniej ilości kluczowych dla generalizacji danych i bezpowrotnej utraty cennych informacji).

## Błyskawiczne Drzewo Decyzyjne (Quick Decision Tree)

1. Czy współczynnik istniejącej nierównowagi kształtuje się na poziomie < 3:1? -> Nie komplikuj, po prostu użyj samych wag klas.
2. Czy Twój zbiór operacyjny posiada > 10 000 próbek? -> Wdroż wagi klas w ścisłym duecie z optymalizacją progu.
3. Czy dysponowany zbiór danych jest silnie ograniczony i obejmuje zaledwie < 1 000 próbek? -> Skompiluj metodykę SMOTE dodatkowo ze standardowymi wagami klas.
4. Jeżeli żaden z w/w punktów nie odpowiada stricte Twojej sytuacji -> Wykorzystaj całe kombo: SMOTE + solidne wagi klas + zaawansowana optymalizacja progu.
5. Wyniki końcowe nadal nie satysfakcjonują i odbiegają od oczekiwań? -> Zastosuj zrównoważone techniki uczenia zespołowego (tzw. Balanced Bagging Ensemble).
