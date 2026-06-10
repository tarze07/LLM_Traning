# Normy i odległości

> Funkcja odległości definiuje, co oznacza „podobny”. Wybierz źle, a wszystko dalej się zepsuje.

**Typ:** Kompilacja
**Język:** Python
**Wymagania wstępne:** Faza 1, lekcje 01 (Intuicja algebry liniowej), 02 (wektory, macierze i operacje)
**Czas:** ~90 minut

## Cele nauczania

- Implementuj L1, L2, cosinus, Mahalanobis, Jaccard i edytuj funkcje odległości od podstaw
- Wybierz odpowiednią metrykę odległości dla danego zadania ML i wyjaśnij, dlaczego rozwiązania alternatywne zawodzą
- Połącz normy L1 i L2 z regularyzacją LASSO i Ridge oraz ich geometrycznymi obszarami więzów
- Zademonstruj, jak ten sam zbiór danych tworzy różnych najbliższych sąsiadów w ramach różnych metryk

## Problem

Masz dwa wektory. Być może są to osadzanie słów. Być może są to profile użytkowników. Być może są to tablice pikseli. Musisz wiedzieć: jak blisko są?

Odpowiedź zależy całkowicie od wybranej funkcji odległości. Dwa punkty danych mogą być najbliższymi sąsiadami w ramach jednej metryki i daleko od siebie w ramach innej metryki. Twój klasyfikator KNN, Twój silnik rekomendacji, Twoja baza danych wektorów, Twój algorytm grupowania, Twoja funkcja straty – wszystko zależy od tego wyboru. Zrób to źle, a Twój model zoptymalizuje się pod kątem niewłaściwej rzeczy.

Nie ma uniwersalnej najlepszej odległości. L2 działa dla danych przestrzennych. Podobieństwo cosinusowe dominuje w NLP. Jaccard obsługuje zestawy. Edytuj ciągi uchwytów odległości. Mahalanobis uwzględnia korelacje. Wasserstein przesuwa masę prawdopodobieństwa. Każdy z nich koduje inne założenie dotyczące tego, co oznacza „podobny”.

W tej lekcji budujemy od zera każdą główną funkcję odległości, pokazujemy, kiedy każda z nich jest właściwym narzędziem, i pokazuje, jak te same dane dają zupełnie różnych najbliższych sąsiadów, w zależności od używanej metryki.

## Koncepcja

### Normy: pomiar wielkości wektora

Norma mierzy „rozmiar” wektora. Każdą funkcję odległości między dwoma wektorami można zapisać jako normę ich różnicy: d(a, b) = ||a - b||. Zatem zrozumienie norm oznacza zrozumienie odległości.

### Norma L1 (odległość Manhattanu)

Norma L1 sumuje wartości bezwzględne wszystkich składników.

```
||x||_1 = |x_1| + |x_2| + ... + |x_n|
```

Nazywa się to dystansem Manhattanu, ponieważ mierzy odległość, jaką pokonujesz po siatce miasta, gdzie możesz poruszać się tylko wzdłuż osi. Brak przekątnych.

```
Point A = (1, 1)
Point B = (4, 5)

L1 distance = |4-1| + |5-1| = 3 + 4 = 7

On a grid, you walk 3 blocks east and 4 blocks north.
```

Kiedy używać L1:
- Wysokowymiarowe, rzadkie dane (funkcje tekstowe, kodowanie typu one-hot)
- Gdy chcesz odporności na wartości odstające (pojedyncza ogromna różnica nie dominuje)
- Problemy z wyborem cech (regularyzacja L1 sprzyja rzadkości)

Połączenie z regularyzacją L1 (Lasso): dodanie ||w||_1 do funkcji straty powoduje karę za sumę bezwzględnych wartości wag. To przesuwa małe wagi dokładnie do zera, wykonując automatyczny wybór funkcji. Kara L1 tworzy obszary ograniczeń w kształcie rombu w przestrzeni wag, a rogi rombów leżą na osiach, gdzie niektóre wagi wynoszą zero.

Połączenie z funkcjami straty: Średni błąd bezwzględny (MAE) to średnia odległość L1 między przewidywaniami a celami. Karze wszystkie błędy w sposób liniowy, dzięki czemu jest odporny na wartości odstające w porównaniu z MSE.

### Norma L2 (odległość euklidesowa)

Norma L2 to odległość w linii prostej. Pierwiastek kwadratowy z sumy kwadratowych składników.

```
||x||_2 = sqrt(x_1^2 + x_2^2 + ... + x_n^2)
```

Jest to dystans, którego nauczyłeś się na zajęciach z geometrii. Pitagoras w n wymiarach.

```
Point A = (1, 1)
Point B = (4, 5)

L2 distance = sqrt((4-1)^2 + (5-1)^2) = sqrt(9 + 16) = sqrt(25) = 5.0

The straight line, cutting diagonally through the grid.
```

Kiedy używać L2:
- Dane ciągłe o niskim i średnim wymiarze
- Gdy skale cech są porównywalne
- Odległości fizyczne (dane przestrzenne, odczyty czujników)
- Podobieństwo obrazu na poziomie pikseli

Połączenie z regularyzacją L2 (Ridge): dodanie ||w||_2^2 do funkcji straty nakłada karę za duże wagi. W przeciwieństwie do L1, nie przesuwa ciężarów do zera. Proporcjonalnie zmniejsza wszystkie wagi do zera. Kara L2 tworzy obszary z więzami kołowymi, więc na osiach nie ma narożników. Wagi stają się małe, ale rzadko dokładnie równe zero.

Połączenie z funkcjami strat: Średni błąd kwadratowy (MSE) to średnia kwadratów odległości L2. Podnoszenie do kwadratu karze większe błędy niż małe.

```
MAE (L1 loss):  |y - y_hat|         Linear penalty. Robust to outliers.
MSE (L2 loss):  (y - y_hat)^2       Quadratic penalty. Sensitive to outliers.
```

### Normy Lp: ogólna rodzina

L1 i L2 to szczególne przypadki normy Lp:

```
||x||_p = (|x_1|^p + |x_2|^p + ... + |x_n|^p)^(1/p)
```

Różne wartości p dają różne kształty „kul jednostkowych” (zbiór wszystkich punktów w odległości 1 od początku):

```
p=1:    Diamond shape      (corners on axes)
p=2:    Circle/sphere      (the usual round ball)
p=3:    Superellipse       (rounded square)
p=inf:  Square/hypercube   (flat sides along axes)
```

### Norma L-nieskończoności (odległość Czebyszewa)

Gdy p zbliża się do nieskończoności, norma Lp zbiega się do maksymalnej składowej bezwzględnej.

```
||x||_inf = max(|x_1|, |x_2|, ..., |x_n|)
```

Odległość między dwoma punktami jest określana przez pojedynczy wymiar, w którym różnią się one najbardziej. Wszystkie inne wymiary są ignorowane.

```
Point A = (1, 1)
Point B = (4, 5)

L-inf distance = max(|4-1|, |5-1|) = max(3, 4) = 4
```

Kiedy stosować L-infinity:
- Kiedy liczy się najgorsze odchylenie w dowolnym pojedynczym wymiarze
- Plansze do gry (król w ruchach szachowych w L-nieskończoności: jeden krok w dowolnym kierunku kosztuje 1)
- Tolerancje produkcyjne (każdy wymiar musi mieścić się w specyfikacji)

### Podobieństwo cosinusa i odległość cosinusa

Podobieństwo cosinusowe mierzy kąt między dwoma wektorami, ignorując ich wielkości.

```
cos_sim(a, b) = (a . b) / (||a||_2 * ||b||_2)
```

Waha się od -1 (w przeciwnych kierunkach) do +1 (w tym samym kierunku). Wektory prostopadłe mają podobieństwo cosinus 0.

Odległość cosinus konwertuje ją na odległość: odległość_cosinus = 1 - podobieństwo_cosinusa. Wartość ta waha się od 0 (kierunek identyczny) do 2 (kierunek przeciwny).

```
a = (1, 0)    b = (1, 1)

cos_sim = (1*1 + 0*1) / (1 * sqrt(2)) = 1/sqrt(2) = 0.707
cos_dist = 1 - 0.707 = 0.293
```

Dlaczego cosinus dominuje w NLP i osadzaniu: w tekście długość dokumentu nie powinna wpływać na podobieństwo. Dokument o kotach, który jest dwa razy dłuższy niż inny dokument o kotach, powinien nadal być „podobny”. Podobieństwo cosinusowe ignoruje wielkość (długość) i skupia się jedynie na kierunku. Dwa dokumenty o tym samym rozkładzie słów, ale różnej długości, skierowane są w tym samym kierunku i uzyskują podobieństwo cosinus 1,0.

Kiedy stosować podobieństwo cosinus:
- Podobieństwo tekstu (wektory TF-IDF, osadzanie słów, osadzanie zdań)
- Dowolna dziedzina, w której wielkość to szum, a kierunek to sygnał
- Systemy rekomendacji (wektory preferencji użytkownika)
- Wyszukiwanie osadzane (wektorowe bazy danych prawie zawsze używają iloczynu cosinusowego lub kropkowego)

### Podobieństwo iloczynu skalarnego a podobieństwo cosinusa

Iloczyn skalarny dwóch wektorów to:

```
a . b = a_1*b_1 + a_2*b_2 + ... + a_n*b_n
      = ||a|| * ||b|| * cos(angle)
```

Podobieństwo cosinusowe to iloczyn skalarny znormalizowany przez obie wielkości. Gdy oba wektory są już znormalizowane jednostkowo (wielkość = 1), iloczyn skalarny i podobieństwo cosinus są identyczne.

```
If ||a|| = 1 and ||b|| = 1:
    a . b = cos(angle between a and b)
```

Gdy się różnią: iloczyn skalarny zawiera informację o wielkości. Wektor o większej wielkości otrzymuje wyższą ocenę iloczynu skalarnego. Ma to znaczenie w niektórych systemach wyszukiwania, w których chcesz, aby „popularne” przedmioty miały wyższą pozycję w rankingu. Wielkość działa jako ukryty sygnał jakości lub ważności.

```
a = (3, 0)    b = (1, 0)    c = (0, 1)

dot(a, b) = 3     dot(a, c) = 0
cos(a, b) = 1.0   cos(a, c) = 0.0

Both agree on direction, but dot product also reflects magnitude.
```

W praktyce:
- Użyj podobieństwa cosinus, jeśli chcesz czystego podobieństwa kierunkowego
- Używaj iloczynu skalarnego, gdy wielkości niosą ze sobą znaczące informacje
- Wiele wektorowych baz danych (Pinecone, Weaviate, Qdrant) pozwala na wybór pomiędzy nimi
- Jeśli Twoje osady są znormalizowane L2, wybór nie ma znaczenia

### Odległość Mahalanobisa

Odległość euklidesowa traktuje wszystkie wymiary jednakowo. Ale jeśli twoje cechy są skorelowane lub mają różne skale, L2 daje mylące wyniki.

Odległość Mahalanobisa uwzględnia strukturę kowariancji danych.

```
d_M(x, y) = sqrt((x - y)^T * S^(-1) * (x - y))
```

gdzie S jest macierzą kowariancji danych.

Intuicyjnie: odległość Mahalanobisa najpierw dekoreluje i normalizuje dane (wybielanie), a następnie oblicza odległość L2 w tej przekształconej przestrzeni. Jeśli S jest macierzą jednostkową (nieskorelowaną, jednostkową cechę wariancji), odległość Mahalanobisa redukuje się do odległości euklidesowej.

```
Example: height and weight are correlated.
Someone 6'2" and 180 lbs is not unusual.
Someone 5'0" and 180 lbs is unusual.

Euclidean distance might say they are equally far from the mean.
Mahalanobis distance correctly identifies the second as an outlier
because it accounts for the height-weight correlation.
```

Kiedy stosować odległość Mahalanobisa:
- Wykrywanie wartości odstających (punkty o dużej odległości Mahalanobisa od średniej to wartości odstające)
- Klasyfikacja, gdy cechy mają różne skale i korelacje
- Kiedy masz wystarczającą ilość danych, aby oszacować wiarygodną macierz kowariancji
- Kontrola jakości w produkcji (wieloczynnikowy monitoring procesów)

### Podobieństwo Jaccarda (dla zestawów)

Podobieństwo Jaccarda mierzy nakładanie się dwóch zestawów.

```
J(A, B) = |A intersect B| / |A union B|
```

Waha się od 0 (brak nakładania się) do 1 (identyczne zestawy). Odległość Jaccarda = 1 - podobieństwo Jaccarda.

```
A = {cat, dog, fish}
B = {cat, bird, fish, snake}

Intersection = {cat, fish}         size = 2
Union = {cat, dog, fish, bird, snake}  size = 5

Jaccard similarity = 2/5 = 0.4
Jaccard distance = 0.6
```

Kiedy używać Jaccarda:
- Porównywanie zestawów tagów, kategorii lub funkcji
- Podobieństwo dokumentów na podstawie obecności słów (a nie częstotliwości)
- Wykrywanie prawie duplikatów (przybliżenie MinHash Jaccarda)
- Porównywanie binarnych wektorów cech (dane dotyczące obecności/nieobecności)
- Ocena modeli segmentacji (Przecięcie przez Unię = Jaccard)

### Edytuj odległość (odległość Levenshteina)

Odległość edycji liczy minimalną liczbę operacji jednoznakowych potrzebnych do przekształcenia jednego ciągu w drugi. Operacje to: wstawianie, usuwanie lub zastępowanie.

```
"kitten" -> "sitting"

kitten -> sitten  (substitute k -> s)
sitten -> sittin  (substitute e -> i)
sittin -> sitting (insert g)

Edit distance = 3
```

Obliczono przy użyciu programowania dynamicznego. Wypełnij macierz, w której wpis (i, j) to odległość edycji między pierwszymi i znakami ciągu A a pierwszymi j znakami ciągu B.

```
        ""  s  i  t  t  i  n  g
    ""   0  1  2  3  4  5  6  7
    k    1  1  2  3  4  5  6  7
    i    2  2  1  2  3  4  5  6
    t    3  3  2  1  2  3  4  5
    t    4  4  3  2  1  2  3  4
    e    5  5  4  3  2  2  3  4
    n    6  6  5  4  3  3  2  3
```

Kiedy używać edycji odległości:
- Sprawdzanie i poprawianie pisowni
- Dopasowanie sekwencji DNA (za pomocą operacji ważonych)
- Rozmyte dopasowanie ciągów
- Deduplikacja niechlujnych danych tekstowych

### Rozbieżność KL (nie odległość, ale używana jak jedna)

Rozbieżność KL mierzy, jak jeden rozkład prawdopodobieństwa różni się od drugiego. Omówiono to w lekcji 09, ale należy do tej dyskusji, ponieważ ludzie używają go jako „odległości”, mimo że nią nie jest.

```
D_KL(P || Q) = sum(p(x) * log(p(x) / q(x)))
```

Właściwość krytyczna: rozbieżność KL NIE jest symetryczna.

```
D_KL(P || Q) != D_KL(Q || P)
```

Oznacza to, że nie spełnia podstawowego wymogu metryki odległości. Nie spełnia również nierówności trójkąta. To rozbieżność, a nie odległość.

Forward KL (D_KL(P || Q)) to „poszukiwanie środka”: Q próbuje objąć wszystkie tryby P.
Odwrotny KL (D_KL(Q || P)) to „wyszukiwanie trybu”: Q skupia się na pojedynczym trybie P.

Kiedy widzisz rozbieżność KL:
- VAE (termin KL w ELBO przesuwa utajoną dystrybucję w kierunku wcześniejszej)
- Destylacja wiedzy (uczeń próbuje dopasować rozkład wiedzy nauczyciela)
- RLHF (kara KL utrzymuje dopracowany model blisko modelu podstawowego)
- Metody gradientu zasad (ograniczające aktualizacje zasad)

### Odległość Wassersteina (odległość poruszającego się ziemią)

Odległość Wassersteina mierzy minimalną „pracę” potrzebną do przekształcenia jednego rozkładu prawdopodobieństwa w inny. Pomyśl o tym w ten sposób: jeśli jedna dystrybucja to kupa ziemi, a druga to dziura, ile ziemi musisz przenieść i jak daleko?

```
W(P, Q) = inf over all transport plans gamma of E[d(x, y)]
```

W przypadku rozkładów 1D upraszcza się to do całki z różnicy bezwzględnej funkcji rozkładu skumulowanego:

```
W_1(P, Q) = integral |CDF_P(x) - CDF_Q(x)| dx
```

Dlaczego Wasserstein jest ważny:
- Jest to metryka prawdziwa (symetryczna, spełnia nierówność trójkąta)
- Zapewnia gradienty nawet wtedy, gdy rozkłady się nie pokrywają (rozbieżność KL zmierza do nieskończoności)
- Ta właściwość uczyniła go centralnym elementem sieci GAN Wassersteina (WGAN), co rozwiązało problem niestabilności uczenia oryginalnych sieci GAN

```
Distributions with no overlap:

P: [1, 0, 0, 0, 0]    Q: [0, 0, 0, 0, 1]

KL divergence: infinity (log of zero)
Wasserstein: 4 (move all mass 4 bins)

Wasserstein gives a meaningful gradient. KL does not.
```

Kiedy stosować Wasserstein:
- Szkolenia GAN (WGAN, WGAN-GP)
- Porównywanie rozkładów, które nie mogą się pokrywać
- Optymalne problemy transportowe
- Wyszukiwanie obrazu (porównywanie histogramów kolorów)

### Dlaczego różne zadania wymagają różnych odległości

| Zadanie | Najlepszy dystans | Dlaczego |
|------|------------------|-----|
| Podobieństwo tekstu | Cosinus | Wielkość to hałas, kierunek to znaczenie |
| Porównanie pikseli obrazu | L2 | Liczą się relacje przestrzenne, cechy mają porównywalną skalę |
| Rzadkie, mocno przyciemnione elementy | L1 | Solidny, nie wzmacnia rzadkich dużych różnic |
| Ustaw nakładanie się (tagi, kategorie) | Jaccard | Dane mają naturalnie ustaloną wartość, a nie wektorową |
| Dopasowanie ciągu | Edytuj odległość | Mapa operacji na ludzką intuicję redakcyjną |
| Wykrywanie wartości odstających | Mahalanobis | Uwzględnia korelacje i skale cech |
| Porównanie rozkładów | Rozbieżność KL | Mierzy utracone informacje, używając Q zamiast P |
| Szkolenie GAN | Wassersteina | Zapewnia gradienty nawet wtedy, gdy rozkłady nie nakładają się |
| Osadzenia (wektor DB) | Iloczyn cosinusowy lub skalarny | Osadzania są szkolone, aby kodować znaczenie w kierunku |
| Zalecenie | Produkt kropkowy | Wielkość może zakodować popularność lub pewność siebie |
| Sekwencje DNA | Odległość edycji ważonej | Koszty substytucji różnią się w zależności od pary nukleotydów
| Kontrola jakości produkcji | L-nieskończoność | Najgorsze odchylenie w jakimkolwiek wymiarze ma znaczenie |

### Połączenie z funkcjami straty

Funkcje straty to funkcje odległości stosowane do przewidywań względem celów.

```
Loss function       Distance it uses       Behavior
MSE                 L2 squared             Penalizes large errors heavily
MAE                 L1                     Penalizes all errors equally
Huber loss          L1 for large errors,   Best of both: robust to outliers,
                    L2 for small errors    smooth gradient near zero
Cross-entropy       KL divergence          Measures distribution mismatch
Hinge loss          max(0, margin - d)     Only penalizes below margin
Triplet loss        L2 (typically)         Pulls positives close, pushes
                                           negatives away
Contrastive loss    L2                     Similar pairs close, dissimilar
                                           pairs beyond margin
```

### Połączenie z regularyzacją

Regularyzacja dodaje karę normalną do wag do funkcji straty.

```
L1 regularization (Lasso):   loss + lambda * ||w||_1
  -> Sparse weights. Some weights become exactly zero.
  -> Automatic feature selection.
  -> Solution has corners (non-differentiable at zero).

L2 regularization (Ridge):   loss + lambda * ||w||_2^2
  -> Small weights. All weights shrink toward zero.
  -> No feature selection (nothing goes to exactly zero).
  -> Smooth solution everywhere.

Elastic Net:                  loss + lambda_1 * ||w||_1 + lambda_2 * ||w||_2^2
  -> Combines sparsity of L1 with stability of L2.
  -> Groups of correlated features are kept or dropped together.
```

Dlaczego L1 wytwarza rzadkość, a L2 nie: zobrazuj obszar ograniczeń w przestrzeni wag 2D. L1 to romb, L2 to okrąg. Kontury funkcji straty (elipsy) najprawdopodobniej dotkną diamentu w narożniku, gdzie jedna waga wynosi zero. Dotykają koła w gładkim punkcie, w którym obie wagi są niezerowe.

### Wyszukiwanie najbliższego sąsiada

Każda funkcja odległości implikuje problem wyszukiwania najbliższego sąsiada: mając punkt zapytania, znajdź najbliższe punkty w zbiorze danych.

Dokładne wyszukiwanie najbliższego sąsiada to O(n * d) na zapytanie w zbiorze danych składającym się z n punktów o wymiarach d. W przypadku dużych zbiorów danych jest to zbyt wolne.

Algorytmy przybliżonego najbliższego sąsiada (ANN) zamieniają niewielką dokładność na ogromny wzrost prędkości:

```
Algorithm         Approach                      Used by
KD-trees          Axis-aligned space partition   scikit-learn (low-dim)
Ball trees        Nested hyperspheres            scikit-learn (medium-dim)
LSH               Random hash projections        Near-duplicate detection
HNSW              Hierarchical navigable         FAISS, Qdrant, Weaviate
                  small-world graph
IVF               Inverted file index with       FAISS (billion-scale)
                  cluster-based search
Product quant.    Compress vectors, search       FAISS (memory-constrained)
                  in compressed space
```

HNSW (Hierarchical Navigable Small World) to algorytm dominujący we współczesnych wektorowych bazach danych. Tworzy wielowarstwowy graf, w którym każdy węzeł łączy się z przybliżonymi najbliższymi sąsiadami. Wyszukiwanie rozpoczyna się od górnej warstwy (rzadkie, długie skoki) i schodzi do dolnej warstwy (gęste, krótkie skoki).

## Zbuduj to

### Krok 1: Wszystkie funkcje norm i odległości

Pełną implementację znajdziesz w `code/distances.py`. Każda funkcja jest budowana od podstaw przy użyciu jedynie podstawowej matematyki Pythona.

### Krok 2: Te same dane, różne odległości, różni sąsiedzi

Demo w `distances.py` tworzy zbiór danych, wybiera punkt zapytania i pokazuje, jak zmienia się najbliższy sąsiad w zależności od metryki odległości. Punkt, który jest „najbliższy” pod L1, może nie być najbliższy pod L2 lub cosinus.

### Krok 3: Osadzanie wyszukiwania podobieństw

Kod zawiera próbne wyszukiwanie podobieństwa z osadzeniem, które znajduje najbardziej podobne „dokumenty” do zapytania przy użyciu podobieństwa cosinus w funkcji odległości L2, co pokazuje, że rankingi mogą się różnić.

## Użyj tego

Najczęstsze zastosowanie praktyczne: wyszukiwanie podobnych elementów w bazie danych wektorowych.

```python
import numpy as np

def cosine_similarity_matrix(X):
    norms = np.linalg.norm(X, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1, norms)
    X_normalized = X / norms
    return X_normalized @ X_normalized.T

embeddings = np.random.randn(1000, 768)

sim_matrix = cosine_similarity_matrix(embeddings)

query_idx = 0
similarities = sim_matrix[query_idx]
top_k = np.argsort(similarities)[::-1][1:6]
print(f"Top 5 most similar to item 0: {top_k}")
print(f"Similarities: {similarities[top_k]}")
```

Kiedy wywołujesz `model.encode(text)`, a następnie przeszukujesz wektorową bazę danych, oto co się dzieje. Model osadzania mapuje tekst na wektory. Baza danych wektorów oblicza podobieństwo cosinus (lub iloczyn skalarny) między wektorem zapytania a każdym przechowywanym wektorem, używając algorytmów ANN, aby uniknąć sprawdzania ich wszystkich.

## Ćwiczenia

1. Oblicz odległości L1, L2 i L-nieskończoności pomiędzy (1, 2, 3) i (4, 0, 6). Sprawdź, że L-inf <= L2 <= L1 zawsze obowiązuje dla dowolnej pary punktów. Udowodnij, dlaczego to uporządkowanie jest gwarantowane.

2. Utwórz dwa wektory, w których podobieństwo cosinusa jest wysokie (> 0,9), ale odległość L2 jest duża (> 10). Wyjaśnij geometrycznie co się dzieje. Następnie utwórz dwa wektory, w których podobieństwo cosinusa jest niskie (< 0,3), ale odległość L2 jest mała (< 0,5).

3. Zaimplementuj funkcję, która pobiera zbiór danych i punkt zapytania i zwraca najbliższego sąsiada w obszarze L1, L2, cosinus i odległość Mahalanobisa. Znajdź zbiór danych, w którym wszyscy czterej nie zgadzają się co do tego, który punkt jest najbliższy.

4. Oblicz ręcznie odległość Wassersteina pomiędzy [0,5, 0,5, 0, 0] i [0, 0, 0,5, 0,5] ręcznie, stosując metodę CDF. Następnie oblicz go pomiędzy [0,25, 0,25, 0,25, 0,25] a [0, 0, 0,5, 0,5]. Który jest większy i dlaczego?

5. Zaimplementuj MinHash, aby uzyskać przybliżone podobieństwo Jaccarda. Wygeneruj 100 losowych zestawów, oblicz dokładny Jaccard dla wszystkich par i porównaj z przybliżeniem MinHash przy użyciu 50, 100 i 200 funkcji skrótu. Narysuj błąd aproksymacji.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|----------------------|
| Norma | „Rozmiar wektora” | Funkcja odwzorowująca wektor na nieujemny skalar, spełniająca nierówność trójkąta, absolutną jednorodność i zero tylko dla wektora zerowego |
| Norma L1 | „Odległość Manhattanu” | Suma bezwzględnych wartości składników. Powoduje rzadkość optymalizacji. Odporny na wartości odstające |
| Norma L2 | „Odległość euklidesowa” | Pierwiastek kwadratowy z sumy kwadratowych składników. Odległość w linii prostej w przestrzeni euklidesowej |
| Norma Lp | „Norma uogólniona” | P-ty pierwiastek z sumy p-tych potęg składowych bezwzględnych. L1 i L2 to przypadki szczególne |
| Norma L-nieskończoności | „Norma maksymalna” lub „odległość Czebyszewa” | Maksymalna bezwzględna wartość składnika. Granica Lp gdy p zbliża się do nieskończoności |
| Cosinus podobieństwo | „Kąt między wektorami” | Iloczyn skalarny znormalizowany według obu wielkości. Zakres od -1 do +1. Ignoruje długość wektora |
| Odległość cosinusa | „1 minus cosinus podobieństwa” | Konwertuje cosinus podobieństwa na odległość. Zakresy od 0 do 2 |
| Produkt kropkowy | „Nieznormalizowany cosinus” | Suma produktów składowych. Równa się cosinusowi podobieństwa razy obie wielkości |
| Odległość Mahalanobisa | „Odległość świadoma korelacji” | Odległość L2 w przestrzeni, która została wybielona (dekorelowana i znormalizowana) przy użyciu macierzy kowariancji danych |
| Podobieństwo Jaccarda | „Ustaw nakładanie się” | Rozmiar przecięcia podzielony przez rozmiar związku. Dla zbiorów, a nie wektorów |
| Edytuj odległość | „Odległość Levenshteina” | Minimalna liczba wstawek, usunięć i podstawień w celu przekształcenia jednego ciągu w inny |
| Rozbieżność KL | „Odległość między rozkładami” | Nie jest to prawdziwa odległość (nie symetryczna). Mierzy dodatkowe bity powstałe przy użyciu Q do kodowania P |
| Odległość Wassersteina | „Odległość poruszającego się Ziemią” | Minimalna praca potrzebna do transportu masy z jednej dystrybucji do drugiej. Prawdziwy wskaźnik |
| Przybliżony najbliższy sąsiad | „Wyszukiwanie SSN” | Algorytmy (HNSW, LSH, IVF), które znajdują w przybliżeniu najbliższe punkty znacznie szybciej niż wyszukiwanie dokładne |
| HNSW | „Algorytm DB wektora” | Hierarchiczny wykres żeglownego małego świata. Wykres wielowarstwowy do szybkiego przybliżonego wyszukiwania najbliższego sąsiada |
| Regularyzacja L1 | „Lasso” | Doliczenie do straty normy wagowej L1. Sprowadza wagę do zera (rzadkość) |
| Regularyzacja L2 | „Grzbiet” lub „zanik masy” | Dodanie do straty kwadratowej normy wag L2. Zmniejsza wagę do zera bez rzadkości |
| Elastyczna siatka | „L1 + L2” | Łączy regularyzację L1 i L2. Radzi sobie ze skorelowanymi grupami obiektów lepiej niż z każdą z osobna |

## Dalsze czytanie

– [FAISS: Biblioteka do efektywnego wyszukiwania podobieństw](https://github.com/facebookresearch/faiss) – Biblioteka Meta do wyszukiwania ANN na skalę miliardową
- [Wasserstein GAN (Arjovsky et al., 2017)](https://arxiv.org/abs/1701.07875) – artykuł przedstawiający odległość Earth Mover do GAN
- [Hashing uwzględniający lokalizację (Indyk i Motwani, 1998)] (https://dl.acm.org/doi/10.1145/276698.276876) - podstawowy algorytm ANN
- [Efficient Estimation of Word Representations (Mikolov et al., 2013)](https://arxiv.org/abs/1301.3781) - Word2Vec, gdzie podobieństwo cosinusa stało się wartością domyślną dla osadzania
- [dokumentacja sklearn.neighbors](https://scikit-learn.org/stable/modules/neighbors.html) - praktyczny przewodnik po metrykach odległości i algorytmach sąsiadów w scikit-learn