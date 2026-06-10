# Wektory, macierze i operacje

> Każda sieć neuronowa to w gruncie rzeczy mnożenie macierzy z kilkoma dodatkowymi krokami.

**Typ:** Kompilacja
**Języki:** Python, Julia
**Wymagania wstępne:** Faza 1, Lekcja 01 (Intuicja algebry liniowej)
**Czas:** ~60 minut

## Cele nauczania

- Zbudowanie klasy Matrix z operacjami elementarnymi, mnożeniem macierzy, transpozycją, wyznacznikiem i odwracaniem.
- Odróżnianie mnożenia elementarnego od mnożenia macierzy oraz rozumienie, kiedy stosować każde z nich.
- Zaimplementowanie pojedynczej gęstej warstwy sieci neuronowej (`relu(W @ x + b)`) od podstaw, używając wyłącznie klasy Matrix.
- Zrozumienie zasad rozgłaszania (broadcasting) i mechaniki dodawania obciążeń (bias) w architekturach sieci neuronowych.

## Problem

Chcesz zbudować sieć neuronową. Czytasz kod i widzisz następujący fragment:

```
output = activation(weights @ input + bias)
```

Znak `@` oznacza mnożenie macierzy. `weights` to macierz. `input` to wektor. Jeśli nie wiesz, co robią te operacje, ta linijka wydaje się magiczna. Jeśli wiesz, dostrzegasz w niej kompletne przejście warstwy w przód (forward pass) w zaledwie trzech operacjach.

Każdy obraz przetwarzany przez model to macierz wartości pikseli. Każde osadzenie (embedding) słowa to wektor. Każda warstwa każdej sieci neuronowej to transformacja macierzowa. Nie da się budować systemów AI bez biegłości w operacjach na macierzach, podobnie jak nie można programować bez zrozumienia zmiennych.

Ta lekcja buduje tę biegłość od podstaw.

## Koncepcja

### Wektory: uporządkowane listy liczb

Wektor to lista liczb posiadająca kierunek i wielkość. W sztucznej inteligencji wektory reprezentują punkty danych, cechy lub parametry.

```
v = [3, 4]        -- wektor 2D
w = [1, 0, -2]    -- wektor 3D
```

Wektor 2D `[3, 4]` wskazuje na współrzędne (3, 4) na płaszczyźnie. Jego długość (wielkość) wynosi 5 (zgodnie z trójkątem 3-4-5).

### Macierze: siatki liczb

Macierz to dwuwymiarowa siatka liczb. Składa się z wierszy i kolumn. Macierz m x n ma m wierszy i n kolumn.

```
A = | 1  2  3 |     -- macierz 2x3 (2 wiersze, 3 kolumny)
    | 4  5  6 |
```

W sieciach neuronowych macierze wag przekształcają wektory wejściowe w wektory wyjściowe. Warstwa z 784 wejściami i 128 wyjściami wykorzystuje macierz wag o wymiarach 128x784.

### Dlaczego kształty mają znaczenie

Mnożenie macierzy podlega rygorystycznej regule: `(m x n) @ (n x p) = (m x p)`. Wymiary wewnętrzne muszą się zgadzać.

```
(128 x 784) @ (784 x 1) = (128 x 1)
  wagi          wejście    wyjście

Wymiary wewnętrzne: 784 = 784  -- poprawne
```

Jeśli w PyTorch napotkasz błąd niezgodności wymiarów (shape mismatch), to jest właśnie powód.

### Zestawienie operacji

| Operacja | Działanie | Zastosowanie w sieciach neuronowych |
|----------|------------|--------------------------------|
| Dodawanie | Łączenie elementarne | Dodawanie obciążenia (bias) do wyjścia |
| Mnożenie przez skalar | Skalowanie każdego elementu | Współczynnik uczenia * gradienty |
| Mnożenie macierzy | Przekształcanie wektorów | Propagacja w przód (forward pass) w warstwie |
| Transpozycja | Zamiana wierszy z kolumnami | Propagacja wsteczna (backpropagation) |
| Wyznacznik | Podsumowanie w postaci jednej liczby | Sprawdzanie odwracalności macierzy |
| Odwracanie | Cofanie transformacji | Rozwiązywanie układów równań liniowych |
| Macierz jednostkowa | Macierz "nic nierobienia" | Inicjalizacja, połączenia resztkowe |

### Mnożenie elementarne a mnożenie macierzy

To rozróżnienie nieustannie sprawia problemy początkującym.

Mnożenie elementarne (element-wise): mnożenie odpowiadających sobie pozycji. Obie macierze muszą mieć ten sam kształt.

```
| 1  2 |   | 5  6 |   | 5  12 |
| 3  4 | * | 7  8 | = | 21 32 |
```

Mnożenie macierzy: iloczyny skalarne wierszy i kolumn. Wymiary wewnętrzne muszą się zgadzać.

```
| 1  2 |   | 5  6 |   | 1*5+2*7  1*6+2*8 |   | 19  22 |
| 3  4 | @ | 7  8 | = | 3*5+4*7  3*6+4*8 | = | 43  50 |
```

Różne operacje, różne wyniki, różne reguły.

### Rozgłaszanie (Broadcasting)

Po dodaniu wektora obciążeń do macierzy wyników, kształty zazwyczaj do siebie nie pasują. Rozgłaszanie automatycznie "rozciąga" mniejszą tablicę, aby dopasować ją wymiarami.

```
| 1  2  3 |   +   [10, 20, 30]
| 4  5  6 |

Rozgłaszanie rozciąga wektor na wszystkie wiersze:

| 1  2  3 |   | 10  20  30 |   | 11  22  33 |
| 4  5  6 | + | 10  20  30 | = | 14  25  36 |
```

Każdy nowoczesny framework robi to automatycznie. Zrozumienie tego mechanizmu zapobiega nieporozumieniom, gdy kształty wydają się nie zgadzać, a kod mimo to działa.

## Implementacja

### Krok 1: Klasa Vector

```python
class Vector:
    def __init__(self, data):
        self.data = list(data)
        self.size = len(self.data)

    def __repr__(self):
        return f"Vector({self.data})"

    def __add__(self, other):
        return Vector([a + b for a, b in zip(self.data, other.data)])

    def __sub__(self, other):
        return Vector([a - b for a, b in zip(self.data, other.data)])

    def __mul__(self, scalar):
        return Vector([x * scalar for x in self.data])

    def dot(self, other):
        return sum(a * b for a, b in zip(self.data, other.data))

    def magnitude(self):
        return sum(x ** 2 for x in self.data) ** 0.5
```

### Krok 2: Klasa Matrix z podstawowymi operacjami

```python
class Matrix:
    def __init__(self, data):
        self.data = [list(row) for row in data]
        self.rows = len(self.data)
        self.cols = len(self.data[0])
        self.shape = (self.rows, self.cols)

    def __repr__(self):
        rows_str = "\n  ".join(str(row) for row in self.data)
        return f"Matrix({self.shape}):\n  {rows_str}"

    def __add__(self, other):
        return Matrix([
            [self.data[i][j] + other.data[i][j] for j in range(self.cols)]
            for i in range(self.rows)
        ])

    def __sub__(self, other):
        return Matrix([
            [self.data[i][j] - other.data[i][j] for j in range(self.cols)]
            for i in range(self.rows)
        ])

    def scalar_multiply(self, scalar):
        return Matrix([
            [self.data[i][j] * scalar for j in range(self.cols)]
            for i in range(self.rows)
        ])

    def element_wise_multiply(self, other):
        return Matrix([
            [self.data[i][j] * other.data[i][j] for j in range(self.cols)]
            for i in range(self.rows)
        ])

    def matmul(self, other):
        return Matrix([
            [
                sum(self.data[i][k] * other.data[k][j] for k in range(self.cols))
                for j in range(other.cols)
            ]
            for i in range(self.rows)
        ])

    def transpose(self):
        return Matrix([
            [self.data[j][i] for j in range(self.rows)]
            for i in range(self.cols)
        ])

    def determinant(self):
        if self.shape == (1, 1):
            return self.data[0][0]
        if self.shape == (2, 2):
            return self.data[0][0] * self.data[1][1] - self.data[0][1] * self.data[1][0]
        det = 0
        for j in range(self.cols):
            minor = Matrix([
                [self.data[i][k] for k in range(self.cols) if k != j]
                for i in range(1, self.rows)
            ])
            det += ((-1) ** j) * self.data[0][j] * minor.determinant()
        return det

    def inverse_2x2(self):
        det = self.determinant()
        if det == 0:
            raise ValueError("Macierz jest osobliwa, nie posiada macierzy odwrotnej")
        return Matrix([
            [self.data[1][1] / det, -self.data[0][1] / det],
            [-self.data[1][0] / det, self.data[0][0] / det]
        ])

    @staticmethod
    def identity(n):
        return Matrix([
            [1 if i == j else 0 for j in range(n)]
            for i in range(n)
        ])
```

### Krok 3: Testowanie operacji

```python
A = Matrix([[1, 2], [3, 4]])
B = Matrix([[5, 6], [7, 8]])

print("A + B =", (A + B).data)
print("A @ B =", A.matmul(B).data)
print("A^T =", A.transpose().data)
print("det(A) =", A.determinant())
print("A^-1 =", A.inverse_2x2().data)

I = Matrix.identity(2)
print("A @ A^-1 =", A.matmul(A.inverse_2x2()).data)
```

### Krok 4: Powiązanie z sieciami neuronowymi

```python
import random

inputs = Matrix([[0.5], [0.8], [0.2]])
weights = Matrix([
    [random.uniform(-1, 1) for _ in range(3)]
    for _ in range(2)
])
bias = Matrix([[0.1], [0.1]])

def relu_matrix(m):
    return Matrix([[max(0, val) for val in row] for row in m.data])

pre_activation = weights.matmul(inputs) + bias
output = relu_matrix(pre_activation)

print(f"Kształt wejścia: {inputs.shape}")
print(f"Kształt wag: {weights.shape}")
print(f"Kształt wyjścia: {output.shape}")
print(f"Wyjście: {output.data}")
```

To jest pojedyncza gęsta warstwa: `output = relu(W @ x + b)`. Każda warstwa gęsta w każdej sieci neuronowej robi dokładnie to.

## Zastosowanie w praktyce

NumPy wykonuje wszystkie powyższe operacje w mniejszej liczbie linii kodu i o rzędy wielkości szybciej.

```python
import numpy as np

A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])

print("A + B =\n", A + B)
print("A * B (mnożenie elementarne) =\n", A * B)
print("A @ B (mnożenie macierzy) =\n", A @ B)
print("A^T =\n", A.T)
print("det(A) =", np.linalg.det(A))
print("A^-1 =\n", np.linalg.inv(A))
print("I =\n", np.eye(2))

inputs = np.random.randn(3, 1)
weights = np.random.randn(2, 3)
bias = np.array([[0.1], [0.1]])
output = np.maximum(0, weights @ inputs + bias)

print(f"\nWarstwa sieci neuronowej: {weights.shape} @ {inputs.shape} = {output.shape}")
print(f"Wyjście:\n{output}")
```

Operator `@` w Pythonie wywołuje metodę `__matmul__`. NumPy implementuje to za pomocą wysoce zoptymalizowanych procedur BLAS napisanych w C i Fortranie. Ta sama matematyka, wykonywana 100 razy szybciej.

Rozgłaszanie (broadcasting) w NumPy:

```python
matrix = np.array([[1, 2, 3], [4, 5, 6]])
bias = np.array([10, 20, 30])
print(matrix + bias)
```

NumPy automatycznie rozgłasza obciążenie 1D (bias) na oba wiersze. Dokładnie tak działa dodawanie obciążeń w architekturach sieci neuronowych.

## Podsumowanie

Ta lekcja ma na celu zachęcenie do nauczania operacji na macierzach poprzez intuicję geometryczną. Zobacz plik `outputs/prompt-matrix-operations.md`.

Zbudowana tutaj klasa Matrix stanowi podstawę dla małego frameworka sieci neuronowych, który zbudujemy w fazie 3, lekcji 10.

## Ćwiczenia

1. **Sprawdź odwracanie.** Pomnóż `A @ A.inverse_2x2()` i potwierdź, że otrzymujesz macierz jednostkową. Wypróbuj to dla trzech różnych macierzy 2x2. Co się dzieje, gdy wyznacznik wynosi zero?

2. **Zaimplementuj odwracanie 3x3.** Rozszerz klasę Matrix, aby obliczała macierz odwrotną dla macierzy 3x3 przy użyciu metody dopełnień algebraicznych (macierzy dołączonej). Przetestuj swoje rozwiązanie, porównując z wynikami `np.linalg.inv` z biblioteki NumPy.

3. **Zbuduj sieć dwuwarstwową.** Używając tylko klasy Matrix (bez NumPy), stwórz dwuwarstwową sieć neuronową: warstwa wejściowa (3 neurony) -> ukryta (4 neurony) -> wyjściowa (2 neurony). Zainicjuj wagi wartościami losowymi, wykonaj propagację w przód i sprawdź, czy wszystkie kształty macierzy są poprawne.

## Kluczowe pojęcia

| Pojęcie | Jak to określamy potocznie | Co to właściwie oznacza |
|------|----------------|----------------------|
| Wektor | "Strzałka" | Uporządkowana lista liczb. W AI: punkt w przestrzeni wielowymiarowej. |
| Macierz | "Tabela liczb" | Transformacja liniowa. Odwzorowuje wektory z jednej przestrzeni do innej. |
| Mnożenie macierzy | "Po prostu pomnóż to" | Iloczyny skalarne pomiędzy każdym wierszem pierwszej macierzy i każdą kolumną drugiej. Kolejność ma znaczenie. |
| Transpozycja | "Odwróć to na bok" | Zamiana wierszy z kolumnami. Zmienia macierz m x n w macierz n x m. Kluczowa w propagacji wstecznej. |
| Wyznacznik | "Jakaś liczba wyliczana z macierzy" | Mierzy, jak bardzo macierz skaluje pole powierzchni (2D) lub objętość (3D). Zero oznacza, że transformacja "spłaszcza" przestrzeń do niższego wymiaru. |
| Macierz odwrotna | "Cofnij to, co zrobiła macierz" | Macierz odwracająca działanie transformacji. Istnieje tylko wtedy, gdy wyznacznik jest różny od zera. |
| Macierz jednostkowa | "Nudna macierz" | Odpowiednik mnożenia przez 1 dla macierzy. Często stosowana w połączeniach resztkowych (ResNets). |
| Rozgłaszanie (Broadcasting) | "Magiczne dopasowywanie kształtów" | Rozciąganie mniejszej tablicy w celu dopasowania jej do większej przez powielanie wzdłuż brakujących wymiarów. |
| Mnożenie elementarne | "Zwykłe mnożenie" | Mnożenie po współrzędnych (odpowiadających sobie pozycji). Obie tablice muszą mieć ten sam kształt (lub pozwalać na rozgłaszanie). |

## Dodatkowe materiały

- [3Blue1Brown: Essence of linear algebra](https://www.3blue1brown.com/topics/linear-algebra) – doskonała intuicja wizualna dla każdej omówionej tutaj operacji.
- [Dokumentacja NumPy o rozgłaszaniu](https://numpy.org/doc/stable/user/basics.broadcasting.html) – dokładne reguły, którymi kieruje się NumPy.
- [Stanford CS229 Linear Algebra Review](http://cs229.stanford.edu/section/cs229-linalg.pdf) – zwięzłe repetytorium z algebry liniowej ukierunkowane pod kątem uczenia maszynowego (ML).
