# Normy i odległości

> Funkcja odległości definiuje, czym jest "podobieństwo". Jeśli wybierzesz złą, wszystko w Twoim modelu pójdzie źle.

**Typ:** Kompilacja
**Język:** Python
**Wymagania wstępne:** Faza 1, lekcje 01 (Intuicja algebry liniowej), 02 (Wektory, macierze i operacje)
**Czas:** ~90 minut

## Cele nauczania

- Zaimplementowanie od podstaw metryk odległości: L1, L2, cosinusowej, Mahalanobisa, Jaccarda oraz odległości Levenshteina (edycji).
- Dobór odpowiedniej metryki dla specyficznego zadania uczenia maszynowego ze zrozumieniem, dlaczego inne by w nim zawiodły.
- Powiązanie norm L1 i L2 z regularyzacjami Lasso i Ridge oraz analiza ich wpływu na przestrzeń wag.
- Zrozumienie, jak zastosowanie różnych metryk na tych samych danych kompletnie zmienia strukturę najbliższych sąsiadów.

## Problem

Masz dwa wektory. Mogą to być osadzenia słów (word embeddings), profile użytkowników lub tablice pikseli z obrazów. Zastanawiasz się: jak blisko siebie one leżą?

Odpowiedź w pełni zależy od dobranej funkcji odległości. Dwa punkty mogą być swoimi najbliższymi sąsiadami w jednej metryce, a być skrajnie odległe w innej. Wybór ten całkowicie definiuje zachowanie algorytmu KNN, systemu rekomendacji, baz danych wektorowych, klasteryzacji czy też wyliczania funkcji straty. Popełnienie tu błędu prowadzi do optymalizowania modelu w stronę niewłaściwego celu.

Nie istnieje jedna "najlepsza" uniwersalna odległość. L2 sprawdza się dla fizycznej przestrzeni. Podobieństwo cosinusowe wiedzie prym w NLP. Indeks Jaccarda działa świetnie na zbiorach. Odległość edycji przetwarza ciągi znaków (stringi). Odległość Mahalanobisa uwzględnia korelację danych. Dystans Wassersteina skupia się na przepływie mas prawdopodobieństwa. Każda funkcja przyjmuje całkowicie odmienne definicje tego, czym jest "podobieństwo".

## Koncepcja

### Normy: Pomiar wielkości wektora

Norma określa po prostu "długość" lub "rozmiar" wektora. Dowolna funkcja odległości między dwoma wektorami może być zapisana jako norma ich różnicy: $d(a, b) = ||a - b||$. Zatem zrozumienie norm równa się bezpośrednio zrozumieniu odległości.

### Norma L1 (Odległość Manhattan)

Norma L1 to prosta suma wartości bezwzględnych wszystkich współrzędnych.

```
||x||_1 = |x_1| + |x_2| + ... + |x_n|
```

Nazywana "odległością taksówkową" lub Manhattan, ponieważ wyznacza odległość przebytą po prostopadłej siatce ulic miasta (nie uwzględniając skrótów na ukos).

Kiedy używać metryki L1:
- Dla danych wysokowymiarowych, wysoce rzadkich (np. one-hot encoding, reprezentacje tekstu).
- Gdy chcemy uzyskać odporność na rzadkie, drastyczne wartości odstające (outliers).
- W redukcji cech – regularyzacja L1 wymusza rzadkość modelu (sparsity).

Związek z regularyzacją (Lasso): Dodanie składnika normy $L1$ do funkcji straty wymusza selekcję cech (najmniej przydatne wagi opadają precyzyjnie do zera).
Związek z funkcjami straty: Mean Absolute Error (MAE) karze błędy liniowo, więc wyjątkowo błędne próbki nie przeciągają modelu aż tak silnie jak przy L2.

### Norma L2 (Odległość Euklidesowa)

Norma L2 to długość odcinka w linii prostej. To po prostu wzór Pitagorasa przeniesiony w wyższe wymiary:

```
||x||_2 = sqrt(x_1^2 + x_2^2 + ... + x_n^2)
```

Kiedy używać metryki L2:
- Dla wektorów o małej i średniej liczbie wymiarów, których cechy są ciągłe i porównywalnie wyskalowane.
- Odległości typowo przestrzenne/fizyczne (np. pomiary z sensorów).
- Bezpośrednie porównanie intensywności pikseli.

Związek z regularyzacją (Ridge): Karze duże wagi, równomiernie kurcząc je do zera, jednak zazwyczaj nigdy precyzyjnie ich nie wyzerowuje.
Związek z funkcjami straty: Mean Squared Error (MSE) silnie penalizuje duże błędy przez podnoszenie różnic do potęgi.

### Norma L-nieskończoności (Odległość Czebyszewa)

To po prostu wektor oznaczający maksymalną absolutną wartość jednej ze składowych.

```
||x||_inf = max(|x_1|, |x_2|, ..., |x_n|)
```
Jest wykorzystywany w inżynierii tolerancji i szachach (odległość króla w L-inf rośnie zawsze o 1 niezależnie od toru).

### Podobieństwo Cosinusowe i Odległość Cosinusowa

Mierzy po prostu kąt przecięcia między dwoma wektorami, w pełni pomijając ich długość operacyjną.

```
cos_sim(a, b) = (a . b) / (||a||_2 * ||b||_2)
```
Odległość: `cos_dist = 1 - cos_sim`. Wartość ta to zakres od 0 do 2.
Świetnie sprawdza się w NLP i modelach językowych osadzeń, gdzie dokument bardzo długi powinien być uznany za "podobny" względem dokumentu o tych samych proporcjach terminów, ale krótkiego. Jeśli nie chcemy, aby waga/rozmiar tekstu zmieniała wynik, używamy odległości cosinusowej.

### Odległość Mahalanobisa

W odróżnieniu do odległości euklidesowej (zakładającej że każdy wymiar znaczy tyle samo i ma taką samą skalę), odległość Mahalanobisa wciąga w kalkulacje kowariancję cech. Dokonuje ona "wybielenia" (dekorelacji i normalizacji danych) i następnie analizuje dystans Euklidesowy.

Znakomita w identyfikowaniu wartości odstających w cechach zależnych od siebie (np. wzrost i waga w medycynie).

### Odległość Jaccarda (dla zbiorów)

Pomiar skali wzajemnego nakładania się dwóch niezależnych unii zbiorów elementów. Obliczany przez wielkość części wspólnej (przecięcia), podzieloną na sumę unikalnych wielkości w obu zbiorach. Idealne m.in. dla chmur tagów.

### Dystans edycji znaków (Levenshtein)

Wylicza liczbę poszczególnych edycji do zamiany np. liter, stosowany w detekcji literówek, mutacjach DNA.

### Rozbieżność Kullbacka-Leiblera (KL Divergence)

Służy szacowaniu ubytku informacyjnego przy założeniach na różnych uwarunkowaniach. Warto pamiętać, że **nie jest to** prawowita definicja odległości (bo nie jest symetryczna). Zastosowanie w uczeniu VAE i RLHF.

### Dystans Wassersteina (Earth Mover's Distance)

Służy obliczaniu kosztu "transportu" dystrybucji prawdopodobieństwa $P$ na inną - $Q$. Bardzo przydatna w pracy modeli GAN.

## Zbuduj to (Praktyka)

Znajdziesz algorytmy zbudowane od zera w folderze: `code/distances.py`. Demonstrują one naocznie jak ten sam zbiór próbek różnie oddeleguje "Najbliższych Sąsiadów" tylko dlatego, że zastosowano na nich inny model liczenia punktów (np. L1 wyrzuci coś innego niż Cosinus).

## Ćwiczenia

1. Oblicz na sucho odległości dla wektorów `(1, 2, 3)` i `(4, 0, 6)`.
2. Stwórz tak wektory, aby kosinus dał korelację `>0.9`, ale L2 pokazało kolosalny uchyłek `>10`.
3. Pokonstruuj algorytm `MinHash` od zera jako aproksymatora dla indeksu Jaccarda.

## Kluczowe terminy
| Słowo | Znaczenie w branży |
|---|---|
| L1 / L2 | Suma bezwzględna vs odległość Pitagorasa w wielowymiarowej przestrzeni euklidesowej. |
| Odległość Cosinusowa | Oparty tylko i wyłącznie o "kierunek osi i znaczenia" pomiar bez uwzględniania głośności/objętości informacji. |
| Dystans Mahalanobisa | Poszerzone o macierz wariancji kowariancyjnej badanie czy dany wektor odchyla się naturalnie względem tendencji, czy stanowi niebezpiecznego outliera. |
| HNSW | Typ grafów "małego świata" stosowanych jako rewolucyjne rozwiązania w bazie Danych Wektorowych jako sztuczka skracająca szukanie ANN. |
