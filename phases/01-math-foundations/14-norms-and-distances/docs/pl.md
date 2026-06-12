# Normy i odległości

> Twoja funkcja odległości definiuje, co znaczy "podobne". Wybierz źle, a wszystko, co budujesz dalej, się zawali.

**Typ:** Build
**Język:** Python
**Wymagania wstępne:** Faza 1, Lekcje 01 (Intuicja algebry liniowej), 02 (Wektory, macierze i operacje)
**Czas:** ~90 minut

## Cele nauki

- Zaimplementować od zera funkcje odległości L1, L2, cosinusową, Mahalanobisa, Jaccarda oraz odległość edycyjną
- Wybrać odpowiednią metrykę odległości dla danego zadania ML i wyjaśnić, dlaczego alternatywy zawodzą
- Połączyć normy L1 i L2 z regularyzacją LASSO i Ridge oraz ich geometrycznymi regionami ograniczeń
- Pokazać, jak ten sam zbiór danych daje różnych najbliższych sąsiadów w zależności od metryki

## Problem

Masz dwa wektory. Może to są embeddingi słów. Może profile użytkowników. Może tablice pikseli. Musisz wiedzieć: jak bliskie są sobie te wektory?

Odpowiedź zależy całkowicie od tego, jaką funkcję odległości wybierzesz. Dwa punkty danych mogą być najbliższymi sąsiadami w jednej metryce, a odległe w innej. Twój klasyfikator KNN, system rekomendacji, baza wektorowa, algorytm klastrowania, funkcja straty -- wszystkie one zależą od tego wyboru. Wybierz źle, a model zoptymalizuje się względem niewłaściwej rzeczy.

Nie istnieje uniwersalnie najlepsza odległość. L2 działa dobrze dla danych przestrzennych. Podobieństwo cosinusowe dominuje w NLP. Jaccard obsługuje zbiory. Odległość edycyjna obsługuje ciągi znaków. Mahalanobis uwzględnia korelacje. Wasserstein przemieszcza masę probabilistyczną. Każda z tych metryk koduje inne założenie o tym, co znaczy "podobne".

Ta lekcja buduje od zera każdą główną funkcję odległości, pokazuje, kiedy każda z nich jest właściwym narzędziem, i demonstruje, jak te same dane dają zupełnie różnych najbliższych sąsiadów w zależności od użytej metryki.

## Koncepcja

### Normy: mierzenie wielkości wektora

Norma mierzy "rozmiar" wektora. Każdą funkcję odległości między dwoma wektorami można zapisać jako normę ich różnicy: d(a, b) = ||a - b||. Zrozumienie norm to więc zrozumienie odległości.

### Norma L1 (odległość Manhattan)

Norma L1 sumuje wartości absolutne wszystkich komponentów.

```
||x||_1 = |x_1| + |x_2| + ... + |x_n|
```

Nazywa się ją odległością Manhattan, bo mierzy, jak daleko trzeba przejść po sieci miejskiej, gdzie można poruszać się tylko wzdłuż osi. Bez przekątnych.

```
Punkt A = (1, 1)
Punkt B = (4, 5)

Odległość L1 = |4-1| + |5-1| = 3 + 4 = 7

Na siatce idziesz 3 przecznice na wschód i 4 przecznice na północ.
```

Kiedy używać L1:
- Dane o wysokiej wymiarowości i rzadkie (cechy tekstowe, kodowanie one-hot)
- Gdy chcesz odporności na wartości odstające (jedna duża różnica nie dominuje)
- Problemy selekcji cech (regularyzacja L1 promuje rzadkość)

Związek z regularyzacją L1 (Lasso): dodanie ||w||_1 do funkcji straty penalizuje sumę wartości absolutnych wag. To spycha małe wagi do dokładnie zera, wykonując automatyczną selekcję cech. Penalizacja L1 tworzy w przestrzeni wag regiony ograniczeń w kształcie diamentu, a wierzchołki diamentów leżą na osiach, gdzie niektóre wagi są zerowe.

Związek z funkcjami straty: Mean Absolute Error (MAE) to średnia odległość L1 między predykcjami a wartościami docelowymi. Penalizuje wszystkie błędy liniowo, co czyni ją odporną na wartości odstające w porównaniu z MSE.

### Norma L2 (odległość euklidesowa)

Norma L2 to odległość po linii prostej. Pierwiastek kwadratowy z sumy kwadratów komponentów.

```
||x||_2 = sqrt(x_1^2 + x_2^2 + ... + x_n^2)
```

To odległość, którą poznałeś na lekcjach geometrii. Pitagoras w n wymiarach.

```
Punkt A = (1, 1)
Punkt B = (4, 5)

Odległość L2 = sqrt((4-1)^2 + (5-1)^2) = sqrt(9 + 16) = sqrt(25) = 5.0

Linia prosta, przecinająca siatkę po przekątnej.
```

Kiedy używać L2:
- Dane ciągłe o niskiej do średniej wymiarowości
- Gdy skale cech są porównywalne
- Odległości fizyczne (dane przestrzenne, odczyty czujników)
- Podobieństwo obrazów na poziomie pikseli

Związek z regularyzacją L2 (Ridge): dodanie ||w||_2^2 do funkcji straty penalizuje duże wagi. W przeciwieństwie do L1, nie spycha wag do zera. Zmniejsza wszystkie wagi proporcjonalnie w kierunku zera. Penalizacja L2 tworzy okrągłe regiony ograniczeń, więc nie ma wierzchołków na osiach. Wagi stają się małe, ale rzadko dokładnie zerowe.

Związek z funkcjami straty: Mean Squared Error (MSE) to średnia z kwadratów odległości L2. Podnoszenie do kwadratu penalizuje duże błędy znacznie silniej niż małe.

```
MAE (strata L1):  |y - y_hat|         Liniowa penalizacja. Odporna na wartości odstające.
MSE (strata L2):  (y - y_hat)^2       Kwadratowa penalizacja. Czuła na wartości odstające.
```

### Normy Lp: ogólna rodzina

L1 i L2 są szczególnymi przypadkami normy Lp:

```
||x||_p = (|x_1|^p + |x_2|^p + ... + |x_n|^p)^(1/p)
```

Różne wartości p dają różnie wykresowane "kule jednostkowe" (zbiór wszystkich punktów w odległości 1 od początku układu współrzędnych):

```
p=1:    Kształt diamentu       (wierzchołki na osiach)
p=2:    Okrąg/sfera            (zwykła okrągła kula)
p=3:    Superelipsa            (zaokrąglony kwadrat)
p=inf:  Kwadrat/hipersześcian  (płaskie boki wzdłuż osi)
```

### Norma L-infinity (odległość Czebyszewa)

Gdy p zbliża się do nieskończoności, norma Lp zbiega do maksymalnego komponentu absolutnego.

```
||x||_inf = max(|x_1|, |x_2|, ..., |x_n|)
```

Odległość między dwoma punktami jest determinowana przez jeden wymiar, w którym różnią się najbardziej. Wszystkie inne wymiary są ignorowane.

```
Punkt A = (1, 1)
Punkt B = (4, 5)

Odległość L-inf = max(|4-1|, |5-1|) = max(3, 4) = 4
```

Kiedy używać L-infinity:
- Gdy istotne jest odchylenie w najgorszym przypadku w jakimkolwiek pojedynczym wymiarze
- Planszówki (król w szachach przemieszcza się w metryce L-infinity: jeden krok w dowolnym kierunku kosztuje 1)
- Tolerancje produkcyjne (każdy wymiar musi być w specyfikacji)

### Podobieństwo cosinusowe i odległość cosinusowa

Podobieństwo cosinusowe mierzy kąt między dwoma wektorami, ignorując ich długości.

```
cos_sim(a, b) = (a . b) / (||a||_2 * ||b||_2)
```

Przyjmuje wartości od -1 (przeciwne kierunki) do +1 (ten sam kierunek). Wektory prostopadłe mają podobieństwo cosinusowe równe 0.

Odległość cosinusowa przekształca to w odległość: cosine_distance = 1 - cosine_similarity. Przyjmuje wartości od 0 (identyczny kierunek) do 2 (przeciwny kierunek).

```
a = (1, 0)    b = (1, 1)

cos_sim = (1*1 + 0*1) / (1 * sqrt(2)) = 1/sqrt(2) = 0.707
cos_dist = 1 - 0.707 = 0.293
```

Dlaczego cosinus dominuje w NLP i embeddingach: w tekście długość dokumentu nie powinna wpływać na podobieństwo. Dokument o kotach, który jest dwa razy dłuższy niż inny dokument o kotach, powinien wciąż być "podobny". Podobieństwo cosinusowe ignoruje długość i interesuje się tylko kierunkiem. Dwa dokumenty z tym samym rozkładem słów, ale różną długością, wskazują w tym samym kierunku i otrzymują podobieństwo cosinusowe 1.0.

Kiedy używać podobieństwa cosinusowego:
- Podobieństwo tekstu (wektory TF-IDF, embeddingi słów, embeddingi zdań)
- Każda dziedzina, w której długość jest szumem, a kierunek sygnałem
- Systemy rekomendacji (wektory preferencji użytkownika)
- Wyszukiwanie embeddingów (bazy wektorowe niemal zawsze używają cosinusu lub iloczynu skalarnego)

### Podobieństwo iloczynu skalarnego vs podobieństwo cosinusowe

Iloczyn skalarny dwóch wektorów to:

```
a . b = a_1*b_1 + a_2*b_2 + ... + a_n*b_n
      = ||a|| * ||b|| * cos(angle)
```

Podobieństwo cosinusowe to iloczyn skalarny znormalizowany przez obie długości. Gdy oba wektory są już znormalizowane do jednostkowej długości (długość = 1), iloczyn skalarny i podobieństwo cosinusowe są identyczne.

```
Jeśli ||a|| = 1 i ||b|| = 1:
    a . b = cos(angle between a and b)
```

Kiedy się różnią: iloczyn skalarny zawiera informację o długości. Wektor o większej długości otrzymuje wyższy wynik iloczynu skalarnego. To ma znaczenie w niektórych systemach wyszukiwania, gdzie chcesz, aby "popularne" elementy plasowały się wyżej. Długość działa jako niejawny sygnał jakości lub ważności.

```
a = (3, 0)    b = (1, 0)    c = (0, 1)

dot(a, b) = 3     dot(a, c) = 0
cos(a, b) = 1.0   cos(a, c) = 0.0

Obie metryki zgadzają się co do kierunku, ale iloczyn skalarny odzwierciedla też długość.
```

W praktyce:
- Używaj podobieństwa cosinusowego, gdy chcesz czystego podobieństwa kierunkowego
- Używaj iloczynu skalarnego, gdy długości niosą znaczącą informację
- Wiele baz wektorowych (Pinecone, Weaviate, Qdrant) pozwala wybierać między nimi
- Jeśli twoje embeddingi są znormalizowane L2, wybór nie ma znaczenia

### Odległość Mahalanobisa

Odległość euklidesowa traktuje wszystkie wymiary tak samo. Ale jeśli twoje cechy są skorelowane lub mają różne skale, L2 daje wyniki mylące.

Odległość Mahalanobisa uwzględnia strukturę kowariancji danych.

```
d_M(x, y) = sqrt((x - y)^T * S^(-1) * (x - y))
```

gdzie S jest macierzą kowariancji danych.

Intuicyjnie: odległość Mahalanobisa najpierw dekorelowuje i normalizuje dane (wybielanie, whitening), a następnie liczy odległość L2 w tej przekształconej przestrzeni. Jeśli S jest macierzą jednostkową (cechy nieskorelowane, o wariancji jednostkowej), odległość Mahalanobisa redukuje się do odległości euklidesowej.

```
Przykład: wzrost i waga są skorelowane.
Osoba o wzroście 188 cm i wadze 82 kg nie jest niczym niezwykłym.
Osoba o wzroście 152 cm i wadze 82 kg jest niezwykła.

Odległość euklidesowa może powiedzieć, że są równie odległe od średniej.
Odległość Mahalanobisa prawidłowo identyfikuje drugą osobę jako wartość odstającą,
ponieważ uwzględnia korelację między wzrostem i wagą.
```

Kiedy używać odległości Mahalanobisa:
- Wykrywanie wartości odstających (punkty o dużej odległości Mahalanobisa od średniej są wartościami odstającymi)
- Klasyfikacja, gdy cechy mają różne skale i korelacje
- Gdy masz wystarczająco dużo danych, by oszacować wiarygodną macierz kowariancji
- Kontrola jakości w produkcji (wielowymiarowe monitorowanie procesu)

### Podobieństwo Jaccarda (dla zbiorów)

Podobieństwo Jaccarda mierzy nakładanie się dwóch zbiorów.

```
J(A, B) = |A intersect B| / |A union B|
```

Przyjmuje wartości od 0 (brak nakładania) do 1 (identyczne zbiory). Odległość Jaccarda = 1 - podobieństwo Jaccarda.

```
A = {cat, dog, fish}
B = {cat, bird, fish, snake}

Przecięcie = {cat, fish}                      rozmiar = 2
Suma zbiorów = {cat, dog, fish, bird, snake}  rozmiar = 5

Podobieństwo Jaccarda = 2/5 = 0.4
Odległość Jaccarda = 0.6
```

Kiedy używać Jaccarda:
- Porównywanie zbiorów tagów, kategorii lub cech
- Podobieństwo dokumentów na podstawie obecności słów (nie częstości)
- Wykrywanie bliskich duplikatów (przybliżenie Jaccarda metodą MinHash)
- Porównywanie binarnych wektorów cech (dane obecność/nieobecność)
- Ewaluacja modeli segmentacji (Intersection over Union = Jaccard)

### Odległość edycyjna (odległość Levenshteina)

Odległość edycyjna zlicza minimalną liczbę operacji na pojedynczych znakach potrzebnych do przekształcenia jednego ciągu w drugi. Operacje to: wstawienie, usunięcie lub zamiana.

```
"kitten" -> "sitting"

kitten -> sitten  (zamiana k -> s)
sitten -> sittin  (zamiana e -> i)
sittin -> sitting (wstawienie g)

Odległość edycyjna = 3
```

Obliczana metodą programowania dynamicznego. Wypełnia się macierz, w której wpis (i, j) to odległość edycyjna między pierwszymi i znakami ciągu A i pierwszymi j znakami ciągu B.

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

Kiedy używać odległości edycyjnej:
- Sprawdzanie i poprawianie pisowni
- Dopasowywanie sekwencji DNA (z ważonymi operacjami)
- Rozmyte dopasowywanie ciągów znaków
- Deduplikacja niechlujnych danych tekstowych

### Dywergencja KL (nie odległość, ale używana jak odległość)

Dywergencja KL mierzy, jak jeden rozkład prawdopodobieństwa różni się od drugiego. Pokryta w Lekcji 09, ale należy do tej dyskusji, bo ludzie używają jej jako "odległości", choć nią nie jest.

```
D_KL(P || Q) = sum(p(x) * log(p(x) / q(x)))
```

Kluczowa właściwość: dywergencja KL NIE jest symetryczna.

```
D_KL(P || Q) != D_KL(Q || P)
```

To oznacza, że nie spełnia podstawowego wymogu metryki odległości. Nie spełnia również nierówności trójkąta. Jest to dywergencja, nie odległość.

Forward KL (D_KL(P || Q)) jest "mean-seeking" (poszukujące średniej): Q próbuje pokryć wszystkie mody P.
Reverse KL (D_KL(Q || P)) jest "mode-seeking" (poszukujące mody): Q skupia się na jednym modzie P.

Kiedy zobaczysz dywergencję KL:
- VAE (człon KL w ELBO wypycha rozkład latentny w stronę rozkładu a priori)
- Distylacja wiedzy (knowledge distillation) (model uczeń próbuje dopasować rozkład nauczyciela)
- RLHF (penalizacja KL utrzymuje dostrojony model blisko modelu bazowego)
- Metody policy gradient (ograniczanie aktualizacji polityki)

### Odległość Wassersteina (Earth Mover's Distance)

Odległość Wassersteina mierzy minimalną "pracę" potrzebną do przekształcenia jednego rozkładu prawdopodobieństwa w drugi. Wyobraź sobie to tak: jeśli jeden rozkład to kupka ziemi, a drugi to dziura, ile ziemi musisz przenieść i jak daleko?

```
W(P, Q) = inf over all transport plans gamma of E[d(x, y)]
```

Dla rozkładów jednowymiarowych redukuje się to do całki z wartości absolutnej różnicy funkcji dystrybucji skumulowanej (CDF):

```
W_1(P, Q) = integral |CDF_P(x) - CDF_Q(x)| dx
```

Dlaczego Wasserstein jest ważny:
- Jest prawdziwą metryką (symetryczną, spełniającą nierówność trójkąta)
- Daje gradienty nawet gdy rozkłady się nie nakładają (dywergencja KL idzie do nieskończoności)
- Ta właściwość uczyniła go centralnym dla Wasserstein GAN (WGAN), które rozwiązały problem niestabilności treningu oryginalnych GAN-ów

```
Rozkłady bez nakładania:

P: [1, 0, 0, 0, 0]    Q: [0, 0, 0, 0, 1]

Dywergencja KL: nieskończoność (logarytm z zera)
Wasserstein: 4 (przenieś całą masę przez 4 przedziały)

Wasserstein daje znaczący gradient. KL nie daje.
```

Kiedy używać Wassersteina:
- Trening GAN-ów (WGAN, WGAN-GP)
- Porównywanie rozkładów, które mogą się nie nakładać
- Problemy transportu optymalnego
- Wyszukiwanie obrazów (porównywanie histogramów kolorów)

### Dlaczego różne zadania potrzebują różnych odległości

| Zadanie | Najlepsza odległość | Dlaczego |
|------|--------------|-----|
| Podobieństwo tekstu | Cosinus | Długość jest szumem, kierunek jest znaczeniem |
| Porównanie pikseli obrazów | L2 | Relacje przestrzenne mają znaczenie, cechy są porównywalnej skali |
| Rzadkie cechy o wysokiej wymiarowości | L1 | Odporna, nie wzmacnia rzadkich dużych różnic |
| Nakładanie się zbiorów (tagi, kategorie) | Jaccard | Dane są naturalnie zbiorowe, nie wektorowe |
| Dopasowywanie ciągów znaków | Odległość edycyjna | Operacje odpowiadają ludzkiej intuicji edycji |
| Wykrywanie wartości odstających | Mahalanobis | Uwzględnia korelacje i skale cech |
| Porównywanie rozkładów | Dywergencja KL | Mierzy informację stracona przy użyciu Q zamiast P |
| Trening GAN | Wasserstein | Daje gradienty nawet gdy rozkłady się nie nakładają |
| Embeddingi (baza wektorowa) | Cosinus lub iloczyn skalarny | Embeddingi są trenowane, by kodować znaczenie w kierunku |
| Rekomendacje | Iloczyn skalarny | Długość może kodować popularność lub pewność |
| Sekwencje DNA | Ważona odległość edycyjna | Koszty zamiany różnią się w zależności od pary nukleotydów |
| Kontrola jakości w produkcji | L-infinity | Liczy się odchylenie w najgorszym przypadku w każdym wymiarze |

### Związek z funkcjami straty

Funkcje straty to funkcje odległości zastosowane do predykcji względem wartości docelowych.

```
Funkcja straty       Używana odległość       Zachowanie
MSE                   L2 do kwadratu          Silnie penalizuje duże błędy
MAE                   L1                      Penalizuje wszystkie błędy równo
Huber loss            L1 dla dużych błędów,   Najlepsze z obu: odporna na wartości
                      L2 dla małych błędów    odstające, gładki gradient przy zerze
Cross-entropy         Dywergencja KL          Mierzy niezgodność rozkładów
Hinge loss            max(0, margin - d)      Penalizuje tylko poniżej marginesu
Triplet loss          L2 (zwykle)             Przyciąga pozytywy blisko, odpycha
                                               negatywy
Contrastive loss      L2                      Podobne pary blisko, niepodobne
                                               pary poza marginesem
```

### Związek z regularyzacją

Regularyzacja dodaje do funkcji straty penalizację normy wag.

```
Regularyzacja L1 (Lasso):    loss + lambda * ||w||_1
  -> Rzadkie wagi. Niektóre wagi stają się dokładnie zerem.
  -> Automatyczna selekcja cech.
  -> Rozwiązanie ma wierzchołki (niedyferencjalne przy zerze).

Regularyzacja L2 (Ridge):    loss + lambda * ||w||_2^2
  -> Małe wagi. Wszystkie wagi zmniejszają się w kierunku zera.
  -> Brak selekcji cech (nic nie staje się dokładnie zerem).
  -> Gładkie rozwiązanie wszędzie.

Elastic Net:                  loss + lambda_1 * ||w||_1 + lambda_2 * ||w||_2^2
  -> Łączy rzadkość L1 ze stabilnością L2.
  -> Grupy skorelowanych cech są zachowywane lub usuwane razem.
```

Dlaczego L1 daje rzadkość, a L2 nie: wyobraź sobie region ograniczeń w 2D przestrzeni wag. L1 to diament, L2 to okrąg. Kontury funkcji straty (elipsy) najprawdopodobniej dotykają diamentu w wierzchołku, gdzie jedna waga jest zerem. Dotykają okręgu w gładkim punkcie, gdzie obie wagi są niezerowe.

### Wyszukiwanie najbliższego sąsiada

Każda funkcja odległości implikuje problem wyszukiwania najbliższego sąsiada: dla danego punktu zapytania znajdź najbliższe punkty w zbiorze danych.

Dokładne wyszukiwanie najbliższego sąsiada ma złożoność O(n * d) na zapytanie w zbiorze danych o n punktach i d wymiarach. Dla dużych zbiorów danych to jest zbyt wolne.

Algorytmy Approximate Nearest Neighbor (ANN) wymieniają niewielką część dokładności na ogromny przyrost prędkości:

```
Algorytm          Podejście                       Używany przez
KD-trees          Podział przestrzeni wzdłuż osi   scikit-learn (niskie wymiary)
Ball trees        Zagnieżdżone hipersfery          scikit-learn (średnie wymiary)
LSH               Losowe projekcje hashujące       Wykrywanie bliskich duplikatów
HNSW              Hierarchiczny graf małego        FAISS, Qdrant, Weaviate
                  świata (small-world)
IVF               Indeks plików odwróconych z      FAISS (skala miliardowa)
                  wyszukiwaniem klastrowym
Product quant.    Kompresja wektorów, wyszukiwanie FAISS (ograniczenia pamięci)
                  w skompresowanej przestrzeni
```

HNSW (Hierarchical Navigable Small World) jest dominującym algorytmem w nowoczesnych bazach wektorowych. Buduje wielowarstwowy graf, w którym każdy węzeł łączy się ze swoimi przybliżonymi najbliższymi sąsiadami. Wyszukiwanie zaczyna się w górnej warstwie (rzadkiej, z dalekimi skokami) i schodzi do dolnej warstwy (gęstej, z krótkimi skokami).

## Zbuduj to

### Krok 1: Wszystkie funkcje norm i odległości

Zobacz `code/distances.py` po kompletną implementację. Każda funkcja jest zbudowana od zera, używając jedynie podstawowej matematyki Pythona.

### Krok 2: Te same dane, różne odległości, różni sąsiedzi

Demo w `distances.py` tworzy zbiór danych, wybiera punkt zapytania i pokazuje, jak zmienia się najbliższy sąsiad w zależności od metryki odległości. Punkt, który jest "najbliższy" w L1, może nie być najbliższy w L2 czy w cosinusie.

### Krok 3: Wyszukiwanie podobieństwa embeddingów

Kod zawiera makietowe wyszukiwanie podobieństwa embeddingów, które znajduje "dokumenty" najbardziej podobne do zapytania, używając podobieństwa cosinusowego vs odległości L2, pokazując, że rankingi mogą się różnić.

## Zastosowanie

Najczęstsze praktyczne zastosowanie: znajdowanie podobnych elementów w bazie wektorowej.

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

Gdy wywołujesz `model.encode(text)`, a następnie przeszukujesz bazę wektorową, dzieje się właśnie to, co powyżej, pod maską. Model embeddingów mapuje tekst na wektory. Baza wektorowa liczy podobieństwo cosinusowe (lub iloczyn skalarny) między twoim wektorem zapytania i każdym przechowywanym wektorem, używając algorytmów ANN, aby nie sprawdzać ich wszystkich.

## Ćwiczenia

1. Oblicz odległości L1, L2 i L-infinity między (1, 2, 3) i (4, 0, 6). Sprawdź, że L-inf <= L2 <= L1 zawsze zachodzi dla każdej pary punktów. Udowodnij, dlaczego ta kolejność jest gwarantowana.

2. Stwórz dwa wektory, gdzie podobieństwo cosinusowe jest wysokie (> 0.9), ale odległość L2 jest duża (> 10). Wyjaśnij geometrycznie, co się dzieje. Następnie stwórz dwa wektory, gdzie podobieństwo cosinusowe jest niskie (< 0.3), ale odległość L2 jest mała (< 0.5).

3. Zaimplementuj funkcję, która dla danego zbioru danych i punktu zapytania zwraca najbliższego sąsiada w odległości L1, L2, cosinusowej i Mahalanobisa. Znajdź zbiór danych, dla którego wszystkie cztery metryki nie zgadzają się co do tego, który punkt jest najbliższy.

4. Oblicz odległość Wassersteina między [0.5, 0.5, 0, 0] i [0, 0, 0.5, 0.5] ręcznie, metodą CDF. Następnie oblicz ją między [0.25, 0.25, 0.25, 0.25] i [0, 0, 0.5, 0.5]. Która jest większa i dlaczego?

5. Zaimplementuj MinHash dla przybliżonego podobieństwa Jaccarda. Wygeneruj 100 losowych zbiorów, oblicz dokładny Jaccard dla wszystkich par i porównaj z przybliżeniem MinHash używającym 50, 100 i 200 funkcji hashujących. Narysuj wykres błędu przybliżenia.

## Kluczowe terminy

| Termin | Co się mówi | Co to faktycznie znaczy |
|------|----------------|----------------------|
| Norma | "Rozmiar wektora" | Funkcja mapująca wektor na nieujemny skalar, spełniająca nierówność trójkąta, jednorodność absolutną i równa zero tylko dla wektora zerowego |
| Norma L1 | "Odległość Manhattan" | Suma wartości absolutnych komponentów. Daje rzadkość w optymalizacji. Odporna na wartości odstające |
| Norma L2 | "Odległość euklidesowa" | Pierwiastek kwadratowy z sumy kwadratów komponentów. Odległość po linii prostej w przestrzeni euklidesowej |
| Norma Lp | "Uogólniona norma" | p-ty pierwiastek z sumy p-tych potęg wartości absolutnych komponentów. L1 i L2 są szczególnymi przypadkami |
| Norma L-infinity | "Norma max" lub "odległość Czebyszewa" | Maksymalna wartość absolutna komponentu. Granica Lp, gdy p zbliża się do nieskończoności |
| Podobieństwo cosinusowe | "Kąt między wektorami" | Iloczyn skalarny znormalizowany przez obie długości. Przyjmuje wartości od -1 do +1. Ignoruje długość wektora |
| Odległość cosinusowa | "1 minus podobieństwo cosinusowe" | Przekształca podobieństwo cosinusowe w odległość. Przyjmuje wartości od 0 do 2 |
| Iloczyn skalarny | "Nieznormalizowany cosinus" | Suma iloczynów komponentów. Równa się podobieństwu cosinusowemu razy obie długości |
| Odległość Mahalanobisa | "Odległość uwzględniająca korelacje" | Odległość L2 w przestrzeni, która została wybielona (zdekorelowana i znormalizowana) za pomocą macierzy kowariancji danych |
| Podobieństwo Jaccarda | "Nakładanie się zbiorów" | Rozmiar przecięcia podzielony przez rozmiar sumy zbiorów. Dla zbiorów, nie wektorów |
| Odległość edycyjna | "Odległość Levenshteina" | Minimalna liczba wstawień, usunięć i zamian potrzebnych do przekształcenia jednego ciągu w drugi |
| Dywergencja KL | "Odległość między rozkładami" | Nie jest prawdziwą odległością (niesymetryczna). Mierzy dodatkowe bity wynikające z użycia Q do kodowania P |
| Odległość Wassersteina | "Earth mover's distance" | Minimalna praca potrzebna do przeniesienia masy z jednego rozkładu do drugiego. Prawdziwa metryka |
| Approximate nearest neighbor | "Wyszukiwanie ANN" | Algorytmy (HNSW, LSH, IVF), które znajdują przybliżone najbliższe punkty znacznie szybciej niż dokładne wyszukiwanie |
| HNSW | "Algorytm baz wektorowych" | Graf Hierarchical Navigable Small World. Wielowarstwowy graf do szybkiego przybliżonego wyszukiwania najbliższego sąsiada |
| Regularyzacja L1 | "Lasso" | Dodanie normy L1 wag do funkcji straty. Spycha wagi do zera (rzadkość) |
| Regularyzacja L2 | "Ridge" lub "weight decay" | Dodanie kwadratu normy L2 wag do funkcji straty. Zmniejsza wagi w kierunku zera bez rzadkości |
| Elastic Net | "L1 + L2" | Łączy regularyzację L1 i L2. Lepiej obsługuje grupy skorelowanych cech niż każda z nich osobno |

## Dalsze materiały

- [FAISS: A Library for Efficient Similarity Search](https://github.com/facebookresearch/faiss) - biblioteka Meta do wyszukiwania ANN w skali miliardowej
- [Wasserstein GAN (Arjovsky et al., 2017)](https://arxiv.org/abs/1701.07875) - artykuł, który wprowadził odległość Earth Mover's do GAN-ów
- [Locality-Sensitive Hashing (Indyk & Motwani, 1998)](https://dl.acm.org/doi/10.1145/276698.276876) - fundamentalny algorytm ANN
- [Efficient Estimation of Word Representations (Mikolov et al., 2013)](https://arxiv.org/abs/1301.3781) - Word2Vec, gdzie podobieństwo cosinusowe stało się domyślne dla embeddingów
- [sklearn.neighbors documentation](https://scikit-learn.org/stable/modules/neighbors.html) - praktyczny przewodnik po metrykach odległości i algorytmach sąsiadów w scikit-learn
