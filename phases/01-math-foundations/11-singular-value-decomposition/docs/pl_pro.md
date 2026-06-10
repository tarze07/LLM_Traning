# Rozkład wartości osobliwych (SVD)

> SVD to szwajcarski scyzoryk algebry liniowej. Każda macierz go posiada, a każdy analityk danych go potrzebuje.

**Typ:** Kompilacja
**Języki:** Python, Julia
**Wymagania wstępne:** Faza 1, Lekcje 01 (Intuicja algebry liniowej), 02 (Operacje na wektorach i macierzach), 03 (Przekształcenia macierzowe)
**Czas:** ~120 minut

## Cele nauczania

- Implementacja SVD za pomocą iteracji potęgowej oraz wyjaśnienie geometrycznego znaczenia macierzy U, $\Sigma$ i $V^T$.
- Zastosowanie obciętego (truncated) SVD do kompresji obrazów i pomiar współczynnika kompresji w stosunku do błędu rekonstrukcji.
- Obliczanie pseudoodwrotności Moore'a-Penrose'a przy użyciu SVD w celu rozwiązywania nadokreślonych układów równań metodą najmniejszych kwadratów.
- Zrozumienie związku SVD z PCA, systemami rekomendacji (czynniki ukryte) oraz ukrytą analizą semantyczną (LSA) w NLP.

## Problem

Masz macierz 1000x2000. Mogą to być oceny filmów wystawione przez użytkowników, macierz występowania terminów w dokumentach (term-document matrix) lub po prostu wartości pikseli obrazu. Twoim celem jest jej kompresja, odszumienie, odnalezienie ukrytej struktury lub rozwiązanie układu równań metodą najmniejszych kwadratów. Klasyczny rozkład według wartości własnych działa tylko dla macierzy kwadratowych i wymaga, by macierz posiadała pełny zbiór liniowo niezależnych wektorów własnych.

Z pomocą przychodzi SVD, który działa dla *każdej* macierzy. Niezależnie od jej kształtu i rzędu. Bez wyjątków. Rozkłada on macierz na trzy czynniki, które geometrycznie opisują, w jaki sposób przekształca ona przestrzeń. To najbardziej uniwersalna i użyteczna faktoryzacja w całej algebrze liniowej.

## Koncepcja

### Co SVD robi geometrycznie

Każda macierz, niezależnie od wymiarów, wykonuje sekwencję trzech operacji: obrót, skalowanie, obrót. SVD precyzyjnie ujawnia te trzy kroki.

```
A = U * \Sigma * V^T

      m x n     m x m    m x n    n x n
     (dowolna) (obrót) (skalowanie) (obrót)
```

Dla dowolnej macierzy A, SVD rozkłada ją na:
- $V^T$ - obraca wektory w przestrzeni wejściowej (n-wymiarowej).
- $\Sigma$ - skaluje (rozciąga lub kompresuje) wzdłuż każdej osi.
- $U$ - obraca wynik do przestrzeni wyjściowej (m-wymiarowej).

Wyobraź to sobie tak: przekazujesz SVD macierz. Algorytm odpowiada: „Ta macierz bierze wejściową kulę danych, obraca ją za pomocą $V^T$, następnie rozciąga w elipsoidę zgodnie z $\Sigma$, a na koniec obraca tę elipsoidę za pomocą $U$”. Wartości osobliwe (singular values) to długości osi wygenerowanej elipsoidy.

### Pełny rozkład

Dla macierzy A o wymiarach m x n:

```
A = U * \Sigma * V^T

gdzie:
  U      jest m x m, ortogonalna (U^T U = I)
  \Sigma jest m x n, diagonalna (wartości osobliwe na przekątnej)
  V      jest n x n, ortogonalna (V^T V = I)

Wartości osobliwe \sigma_1 \ge \sigma_2 \ge ... \ge \sigma_r > 0
gdzie r = rząd(A)
```

Kolumny macierzy U nazywane są **lewymi wektorami osobliwymi**. Kolumny macierzy V to **prawe wektory osobliwe**. Z kolei wartości na przekątnej $\Sigma$ to **wartości osobliwe**. Są one zawsze nieujemne i domyślnie posortowane malejąco.

### Lewe wektory osobliwe, wartości osobliwe i prawe wektory osobliwe

Każdy komponent SVD ma konkretne znaczenie geometryczne:

**Prawe wektory osobliwe (kolumny V):** Tworzą ortonormalną bazę dla przestrzeni wejściowej ($\mathbb{R}^n$). Są to kierunki w przestrzeni wejściowej, które macierz A odwzorowuje na wzajemnie ortogonalne kierunki w przestrzeni wyjściowej. To naturalny układ współrzędnych dziedziny.

**Wartości osobliwe (przekątna $\Sigma$):** Współczynniki skalujące. $i$-ta wartość osobliwa określa, jak bardzo macierz rozciąga przestrzeń wzdłuż $i$-tego prawego wektora osobliwego. Wartość osobliwa równa zero oznacza, że macierz całkowicie zeruje dany wymiar.

**Lewe wektory osobliwe (kolumny U):** Tworzą ortonormalną bazę dla przestrzeni wyjściowej ($\mathbb{R}^m$). $i$-ty lewy wektor osobliwy to po prostu kierunek w przestrzeni wyjściowej, w który przekształcany jest $i$-ty prawy wektor osobliwy (po przeskalowaniu).

Ich relacja:
```
A * v_i = \sigma_i * u_i

Macierz A bierze i-ty prawy wektor osobliwy v_i, 
skaluje go przez \sigma_i i przekształca na i-ty lewy wektor osobliwy u_i.
```

### Związek z rozkładem własnym (eigendecomposition)

SVD i rozkład własny są ze sobą głęboko powiązane. Wartości i wektory osobliwe macierzy A wynikają bezpośrednio z wartości i wektorów własnych macierzy $A^T A$ oraz $A A^T$.

```
A^T A = V * \Sigma^T * U^T * U * \Sigma * V^T
      = V * \Sigma^T * \Sigma * V^T
      = V * D * V^T

gdzie D = \Sigma^T * \Sigma to macierz diagonalna zawierająca \sigma_i^2.
```
Wynikają z tego trzy kwestie:
1. Wartości osobliwe są zawsze rzeczywiste i nieujemne.
2. SVD można obliczyć badając wartości własne $A^T A$, jednak pogarsza to uwarunkowanie macierzy do kwadratu (co drastycznie obniża precyzję numeryczną). Nowoczesne algorytmy SVD tego unikają.
3. Gdy A jest kwadratowa, symetryczna i dodatnio półokreślona, SVD i rozkład na wartości własne to dokładnie to samo.

### Ucięty SVD: przybliżenie niskiego rzędu (low-rank approximation)

Twierdzenie Eckarta-Younga-Mirsky'ego gwarantuje, że najlepsze przybliżenie rzędu $k$ dla macierzy A uzyskujemy, zachowując wyłącznie $k$ największych wartości osobliwych oraz powiązanych z nimi wektorów:

```
A_k = U_k * \Sigma_k * V_k^T

gdzie:
  U_k     ma wymiar m x k (pierwsze k kolumn macierzy U)
  \Sigma_k ma wymiar k x k (lewy górny blok macierzy \Sigma)
  V_k     ma wymiar n x k (pierwsze k kolumn macierzy V)
```

To matematycznie udowodnione, absolutnie najlepsze możliwe przybliżenie macierzy dla zadanego rzędu $k$.

Jeśli wartości osobliwe szybko maleją (np. dla zdjęć), małe $k$ będzie w stanie zachować praktycznie wszystkie cenne informacje z macierzy.

### Kompresja obrazu za pomocą SVD

Obraz w skali szarości to po prostu macierz pikseli. Dla rozdzielczości 800 x 600 mamy 480 000 wartości. SVD pozwala przybliżyć te dane, używając zaledwie ułamka pierwotnej objętości.

```
Oryginalny obraz: 800 x 600 = 480,000 wartości

Dla SVD rzędu k=50:
14.6% rozmiaru oryginału
```
Kilka pierwszych wartości koduje główne kształty i tło. Kolejne dodają detale i szum. Obcięcie na poziomie $k=50$ często pozwala uzyskać obraz prawie nieodróżnialny od oryginału przy użyciu 85% mniejszej pamięci.

### SVD w systemach rekomendacji i NLP

W Netflix Prize algorytmy SVD były kluczowe. SVD odnajduje "ukryte czynniki" (latent factors) w macierzy ocen użytkowników, łącząc filmy w grupy tematyczne. Przewidywana ocena to iloczyn skalarny profilu użytkownika i filmu.

W NLP technika ta nazywana jest Latent Semantic Analysis (LSA). Aplikuje się SVD na macierz term-document. Słowa synonimiczne zazwyczaj współwystępują w podobnym kontekście, więc SVD mapuje je na podobne wektory w ukrytej przestrzeni.

### SVD w redukcji szumu i Pseudoodwrotność

SVD idealnie odszumia sygnał, ponieważ cały prawdziwy sygnał leży w największych wartościach osobliwych, a losowy szum odkłada się w najmniejszych. Ucinając małe wartości osobliwe, kasujemy tzw. "poziom szumu" (noise floor).

SVD pozwala też błyskawicznie obliczyć pseudoodwrotność Moore'a-Penrose'a ($A^+$), by znaleźć optymalne (najmniejsze kwadraty) rozwiązanie nadokreślonych układów równań $Ax=b$. Zastępuje tu numerycznie niestabilne odwrotniki od $A^T A$.

### Związek z PCA

Analiza Głównych Składowych (PCA) to w praktyce matematycznej SVD zaaplikowane na wycentrowanych danych (z odjętą średnią). 
Warto wiedzieć, że w bibliotece `scikit-learn`, `PCA` jest zawsze obliczane pod maską za pomocą procedury SVD, a nie poprzez rozkład macierzy kowariancji, ponieważ rozwiązanie SVD jest wydajniejsze i dużo bardziej stabilne numerycznie.

## Zbuduj to

### Krok 1: SVD od podstaw przy użyciu iteracji potęgowej

```python
import numpy as np

def power_iteration(M, num_iters=100):
    n = M.shape[1]
    v = np.random.randn(n)
    v = v / np.linalg.norm(v)

    for _ in range(num_iters):
        Mv = M @ v
        v = Mv / np.linalg.norm(Mv)

    eigenvalue = v @ M @ v
    return eigenvalue, v

def svd_from_scratch(A, k=None):
    m, n = A.shape
    if k is None:
        k = min(m, n)

    sigmas = []
    us = []
    vs = []

    A_residual = A.copy().astype(float)

    for _ in range(k):
        AtA = A_residual.T @ A_residual
        eigenvalue, v = power_iteration(AtA, num_iters=200)

        if eigenvalue < 1e-10:
            break

        sigma = np.sqrt(eigenvalue)
        u = A_residual @ v / sigma

        sigmas.append(sigma)
        us.append(u)
        vs.append(v)

        A_residual = A_residual - sigma * np.outer(u, v)

    U = np.column_stack(us) if us else np.empty((m, 0))
    S = np.array(sigmas)
    V = np.column_stack(vs) if vs else np.empty((n, 0))

    return U, S, V
```

## Użyj tego

Gotowe, działające dema kompresji obrazów i rekomendacji znajdziesz w `code/svd.py`. 

## Ćwiczenia

1. Zaimplementuj od zera pełne SVD, ale bez korzystania z iteracji potęgowej. Wylicz zamiast tego wartości własne z macierzy kowariancyjnej.
2. Pobierz obraz w skali szarości i kompresuj go obciętym SVD w rzędach 1, 5, 10, 25, 50, 100.
3. Utwórz prosty system rekomendacji. Uzupełnij luki średnią z ocen użytkownika.
4. Wygeneruj macierz term-document dla 3 syntetycznych tematów i zastosuj SVD, aby zweryfikować czy podobne terminy znalazły się blisko w przestrzeni LSA.

## Kluczowe terminy

| Termin | Co to oznacza |
|------|----------------------|
| SVD | Faktoryzacja rozkładająca macierz na ortogonalną $U$, diagonalną $\Sigma$ i ortogonalną $V^T$. Działa dla dowolnej macierzy. |
| Wartość osobliwa | i-ty element przekątnej $\Sigma$. Mierzy, jak bardzo macierz rozciąga przestrzeń wzdłuż głównego kierunku. |
| Obcięty SVD | (Truncated SVD) Zatrzymanie tylko $k$ największych wartości osobliwych. Gwarantuje najlepsze matematyczne przybliżenie macierzy oryginalnej w zadanym rzędzie. |
| Rząd (Rank) | Liczba niezerowych wartości osobliwych (niezależnych kierunków przenoszących informację). |
| Pseudoodwrotność | Pozwala wyliczać optymalne błędy układów nadokreślonych metodą najmniejszych kwadratów. |
| Liczba uwarunkowania | Stosunek największej do najmniejszej wartości osobliwej ($\sigma_{max} / \sigma_{min}$). Informuje o podatności na zaokrąglenia i błędy zmiennoprzecinkowe. |
| Czynnik ukryty | (Latent factor) Temat odnaleziony przez SVD w przestrzeni o mniejszej wymiarowości (np. gatunek filmu w układzie Netflixa). |
| Iteracja potęgowa | Algorytm znajdujący wektor powiązany z największą wartością własną przez sekwencyjne domnażanie wektora. |
