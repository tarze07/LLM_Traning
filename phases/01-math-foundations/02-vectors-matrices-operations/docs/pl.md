# Wektory, macierze i operacje

> Każda sieć neuronowa to po prostu mnożenie macierzy z dodatkowymi krokami.

**Typ:** Kompilacja
**Języki:** Python, Julia
**Wymagania wstępne:** Faza 1, Lekcja 01 (Intuicja algebry liniowej)
**Czas:** ~60 minut

## Cele nauczania

- Zbuduj klasę Matrix z operacjami na elementach, mnożeniem macierzy, transpozycją, wyznacznikiem i odwrotnością
- Odróżnij mnożenie elementarne od mnożenia macierzy i wyjaśnij, kiedy każde z nich ma zastosowanie
- Zaimplementuj pojedynczą gęstą warstwę sieci neuronowej (`relu(W @ x + b)`) używając wyłącznie od podstaw klasy Matrix
- Wyjaśnij zasady rozgłaszania i działanie dodawania odchyleń w strukturach sieci neuronowych

## Problem

Chcesz zbudować sieć neuronową. Czytasz kod i widzisz to:

```
output = activation(weights @ input + bias)
```

To `@` to mnożenie macierzy. `weights` to macierz. `input` jest wektorem. Jeśli nie wiesz, co robią te operacje, ta linia jest magiczna. Jeśli wiesz, jest to całe przejście warstwy w przód w trzech operacjach.

Każdy obraz przetwarzany przez model jest macierzą wartości pikseli. Każde osadzenie słowa jest wektorem. Każda warstwa każdej sieci neuronowej jest transformacją macierzy. Nie da się zbudować systemów AI bez biegłości w operacjach na macierzach, tak samo jak nie można pisać kodu bez zrozumienia zmiennych.

Ta lekcja buduje tę płynność od zera.

## Koncepcja

### Wektory: uporządkowane listy liczb

Wektor to lista liczb z kierunkiem i wielkością. W sztucznej inteligencji wektory reprezentują punkty danych, cechy lub parametry.

```
v = [3, 4]        -- a 2D vector
w = [1, 0, -2]    -- a 3D vector
```

Wektor 2D `[3, 4]` wskazuje na współrzędne (3, 4) na płaszczyźnie. Jego długość (wielkość) wynosi 5 (trójkąt 3-4-5).

### Macierze: siatki liczb

Macierz to siatka 2D. Wiersze i kolumny. Macierz m x n ma m wierszy i n kolumn.

```
A = | 1  2  3 |     -- 2x3 matrix (2 rows, 3 columns)
    | 4  5  6 |
```

W sieciach neuronowych macierze wag przekształcają wektory wejściowe w wektory wyjściowe. Warstwa z 784 wejściami i 128 wyjściami wykorzystuje macierz wag 128x784.

### Dlaczego kształty mają znaczenie

Mnożenie macierzy podlega ścisłej zasadzie: `(m x n) @ (n x p) = (m x p)`. Wymiary wewnętrzne muszą się zgadzać.

```
(128 x 784) @ (784 x 1) = (128 x 1)
  weights       input       output

Inner dimensions: 784 = 784  -- valid
```

Jeśli w PyTorch pojawi się błąd niedopasowania kształtu, oto dlaczego.

### Mapa operacji

| Operacja | Co to robi | Wykorzystanie sieci neuronowej |
|----------|------------|--------------------------------|
| Dodatek | Łącz elementarnie | Dodawanie odchylenia do wyjścia |
| Skalarne mnożenie | Skaluj każdy element | Szybkość uczenia się * gradienty |
| Pomnóż macierz | Przekształć wektory | Warstwowe podanie do przodu |
| Transpozycja | Odwróć wiersze i kolumny | Propagacja wsteczna |
| Wyznacznik | Podsumowanie pojedynczej liczby | Sprawdzanie odwracalności |
| Odwrotność | Cofnij transformację | Rozwiązywanie układów liniowych |
| Tożsamość | Macierz nic nie robienia | Inicjalizacja, pozostałe połączenia |

### Mnożenie według elementów a mnożenie macierzy

To rozróżnienie nieustannie spotyka początkujących.

Elementowo: pomnóż pasujące pozycje. Obie macierze muszą mieć ten sam kształt.

```
| 1  2 |   | 5  6 |   | 5  12 |
| 3  4 | * | 7  8 | = | 21 32 |
```

Mnożenie macierzy: iloczyny skalarne wierszy i kolumn. Wymiary wewnętrzne muszą się zgadzać.

```
| 1  2 |   | 5  6 |   | 1*5+2*7  1*6+2*8 |   | 19  22 |
| 3  4 | @ | 7  8 | = | 3*5+4*7  3*6+4*8 | = | 43  50 |
```

Różne operacje, różne wyniki, różne zasady.

### Nadawanie

Po dodaniu wektora odchylenia do macierzy wyników kształty nie pasują. Nadawanie rozciąga mniejszą tablicę w celu dopasowania.

```
| 1  2  3 |   +   [10, 20, 30]
| 4  5  6 |

Broadcasting stretches the vector across rows:

| 1  2  3 |   | 10  20  30 |   | 11  22  33 |
| 4  5  6 | + | 10  20  30 | = | 14  25  36 |
```

Każdy nowoczesny framework robi to automatycznie. Zrozumienie tego zapobiega nieporozumieniom, gdy kształty wydają się nieprawidłowe, ale kod działa.

## Zbuduj to

### Krok 1: Klasa wektorowa

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

### Krok 2: Klasa macierzowa z podstawowymi operacjami

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
            raise ValueError("Matrix is singular, no inverse exists")
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

### Krok 3: Zobacz, jak to działa

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

### Krok 4: Połącz się z sieciami neuronowymi

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

print(f"Input shape: {inputs.shape}")
print(f"Weight shape: {weights.shape}")
print(f"Output shape: {output.shape}")
print(f"Output: {output.data}")
```

To jest pojedyncza gęsta warstwa: `output = relu(W @ x + b)`. Każda gęsta warstwa w każdej sieci neuronowej robi dokładnie to.

## Użyj tego

NumPy robi wszystko powyżej w mniejszej liczbie linii i o rzędy wielkości szybciej.

```python
import numpy as np

A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])

print("A + B =\n", A + B)
print("A * B (element-wise) =\n", A * B)
print("A @ B (matrix multiply) =\n", A @ B)
print("A^T =\n", A.T)
print("det(A) =", np.linalg.det(A))
print("A^-1 =\n", np.linalg.inv(A))
print("I =\n", np.eye(2))

inputs = np.random.randn(3, 1)
weights = np.random.randn(2, 3)
bias = np.array([[0.1], [0.1]])
output = np.maximum(0, weights @ inputs + bias)

print(f"\nNeural network layer: {weights.shape} @ {inputs.shape} = {output.shape}")
print(f"Output:\n{output}")
```

Operator `@` w Pythonie wywołuje `__matmul__`. NumPy implementuje to za pomocą zoptymalizowanych procedur BLAS napisanych w C i Fortran. Ta sama matematyka, 100 razy szybciej.

Nadawanie w NumPy:

```python
matrix = np.array([[1, 2, 3], [4, 5, 6]])
bias = np.array([10, 20, 30])
print(matrix + bias)
```

NumPy automatycznie rozgłasza odchylenie 1D w obu wierszach. Tak działa dodawanie odchylenia w każdej strukturze sieci neuronowej.

## Wyślij to

Lekcja ta stanowi zachętę do nauczania operacji na macierzach poprzez intuicję geometryczną. Zobacz `outputs/prompt-matrix-operations.md`.

Zbudowana tutaj klasa Matrix jest podstawą struktury mini sieci neuronowej, którą budujemy w fazie 3, lekcji 10.

## Ćwiczenia

1. **Sprawdź odwrotność.** Pomnóż `A @ A.inverse_2x2()` i potwierdź, że otrzymałeś macierz tożsamości. Wypróbuj z trzema różnymi macierzami 2x2. Co się stanie, gdy wyznacznik wynosi zero?

2. **Zaimplementuj odwrotność 3x3.** Rozszerz klasę Matrix, aby obliczać odwrotności dla macierzy 3x3 przy użyciu metody sprzężonej. Przetestuj to w porównaniu z `np.linalg.inv` NumPy.

3. **Zbuduj sieć dwuwarstwową.** Używając tylko klasy Matrix (bez NumPy), utwórz dwuwarstwową sieć neuronową: wejście (3) -> ukryta (4) -> wyjście (2). Zainicjuj losowe ciężarki, wykonaj przejście do przodu i sprawdź, czy wszystkie kształty są prawidłowe.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|----------------------|
| wektor | „Strzałka” | Uporządkowana lista liczb. W AI: punkt w przestrzeni wielowymiarowej. |
| Matryca | „Tabela liczb” | Transformacja liniowa. Odwzorowuje wektory z jednej przestrzeni do drugiej. |
| Pomnóż macierz | „Po prostu pomnóż liczby” | Iloczyny kropkowe pomiędzy każdym wierszem pierwszej macierzy i każdą kolumną drugiej. Porządek ma znaczenie. |
| Transpozycja | „Odwróć to” | Zamień wiersze i kolumny. Zamienia macierz m x n w n x m. Krytyczny w przypadku propagacji wstecznej. |
| Wyznacznik | „Jakaś liczba z macierzy” | Mierzy, w jakim stopniu matryca skaluje obszar (2D) lub objętość (3D). Zero oznacza, że ​​transformacja miażdży wymiar. |
| Odwrotność | „Cofnij matrycę” | Macierz odwracająca transformację. Istnieje tylko wtedy, gdy wyznacznik nie jest zerem. |
| Macierz tożsamości | „Nudna matryca” | Macierzowy odpowiednik mnożenia przez 1. Stosowany w połączeniach resztkowych (ResNets). |
| Nadawanie | „Magiczne ustalanie kształtu” | Rozciąganie mniejszej tablicy, aby dopasować ją do większej, powtarzając wzdłuż brakujących wymiarów. |
| Elementarnie | „Zwykłe mnożenie” | Pomnóż pasujące pozycje. Obie tablice muszą mieć ten sam kształt (lub umożliwiać rozgłaszanie). |

## Dalsze czytanie

- [3Blue1Brown: Istota algebry liniowej](https://www.3blue1brown.com/topics/linear-algebra) – intuicja wizualna dla każdej opisanej tutaj operacji
- [Dokumentacja NumPy dotycząca nadawania](https://numpy.org/doc/stable/user/basics.broadcasting.html) - dokładne zasady, których przestrzega NumPy
- [Stanford CS229 Linear Algebra Review](http://cs229.stanford.edu/section/cs229-linalg.pdf) - zwięzłe odniesienie do algebry liniowej specyficznej dla ML