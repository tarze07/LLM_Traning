# Wektory, macierze i operacje

> Każda sieć neuronowa to po prostu mnożenie macierzy z dodatkowymi krokami.

**Typ:** Build
**Języki:** Python, Julia
**Wymagania wstępne:** Faza 1, Lekcja 01 (Intuicja liniowej algebry)
**Czas:** ~60 minut

## Cele nauki

- Zbudować klasę Matrix z operacjami element po elemencie, mnożeniem macierzy, transpozycją, wyznacznikiem i odwrotnością
- Odróżnić mnożenie element po elemencie od mnożenia macierzowego i wyjaśnić, kiedy stosuje się każde z nich
- Zaimplementować pojedynczą gęstą warstwę sieci neuronowej (`relu(W @ x + b)`) używając wyłącznie zbudowanej od podstaw klasy Matrix
- Wyjaśnić zasady broadcastingu i sposób, w jaki działa dodawanie biasu w frameworkach sieci neuronowych

## Problem

Chcesz zbudować sieć neuronową. Czytasz kod i widzisz to:

```
output = activation(weights @ input + bias)
```

To `@` to mnożenie macierzy. `weights` to macierz. `input` to wektor. Jeśli nie wiesz, co robią te operacje, ta linijka jest magią. Jeśli wiesz, to cały przebieg w przód (forward pass) warstwy zamknięty w trzech operacjach.

Każdy obraz przetwarzany przez Twój model to macierz wartości pikseli. Każdy embedding słowa to wektor. Każda warstwa każdej sieci neuronowej to transformacja macierzowa. Nie da się budować systemów AI bez biegłości w operacjach macierzowych - tak samo jak nie da się pisać kodu bez rozumienia zmiennych.

Ta lekcja buduje tę biegłość od podstaw.

## Koncepcja

### Wektory: uporządkowane listy liczb

Wektor to lista liczb mająca kierunek i wielkość (długość). W AI wektory reprezentują punkty danych, cechy (features) lub parametry.

```
v = [3, 4]        -- wektor 2D
w = [1, 0, -2]    -- wektor 3D
```

Wektor 2D `[3, 4]` wskazuje na współrzędne (3, 4) na płaszczyźnie. Jego długość (wielkość) wynosi 5 (trójkąt 3-4-5).

### Macierze: siatki liczb

Macierz to dwuwymiarowa siatka. Wiersze i kolumny. Macierz m x n ma m wierszy i n kolumn.

```
A = | 1  2  3 |     -- macierz 2x3 (2 wiersze, 3 kolumny)
    | 4  5  6 |
```

W sieciach neuronowych macierze wag transformują wektory wejściowe na wektory wyjściowe. Warstwa z 784 wejściami i 128 wyjściami używa macierzy wag 128x784.

### Dlaczego kształty mają znaczenie

Mnożenie macierzy ma ścisłą zasadę: `(m x n) @ (n x p) = (m x p)`. Wewnętrzne wymiary muszą się zgadzać.

```
(128 x 784) @ (784 x 1) = (128 x 1)
  weights       input       output

Wymiary wewnętrzne: 784 = 784  -- poprawne
```

Jeśli kiedykolwiek dostaniesz błąd niezgodności kształtów (shape mismatch) w PyTorchu, to właśnie dlatego.

### Mapa operacji

| Operacja | Co robi | Zastosowanie w sieciach neuronowych |
|-----------|-------------|-------------------|
| Dodawanie | Łączenie element po elemencie | Dodawanie biasu do wyjścia |
| Mnożenie przez skalar | Skalowanie każdego elementu | Learning rate * gradienty |
| Mnożenie macierzy | Transformacja wektorów | Forward pass warstwy |
| Transpozycja | Zamiana wierszy i kolumn miejscami | Backpropagation |
| Wyznacznik | Pojedyncza liczba podsumowująca | Sprawdzanie odwracalności |
| Odwrotność | Cofnięcie transformacji | Rozwiązywanie układów liniowych |
| Macierz jednostkowa | Macierz "nic nie robiąca" | Inicjalizacja, połączenia rezydualne |

### Mnożenie element po elemencie a mnożenie macierzowe

To rozróżnienie ciągle myli początkujących.

Element po elemencie: mnożenie odpowiadających sobie pozycji. Obie macierze muszą mieć ten sam kształt.

```
| 1  2 |   | 5  6 |   | 5  12 |
| 3  4 | * | 7  8 | = | 21 32 |
```

Mnożenie macierzowe: iloczyny skalarne wierszy i kolumn. Wewnętrzne wymiary muszą się zgadzać.

```
| 1  2 |   | 5  6 |   | 1*5+2*7  1*6+2*8 |   | 19  22 |
| 3  4 | @ | 7  8 | = | 3*5+4*7  3*6+4*8 | = | 43  50 |
```

Różne operacje, różne wyniki, różne zasady.

### Broadcasting

Gdy dodajesz wektor biasu do macierzy wyjść, kształty się nie zgadzają. Broadcasting rozciąga mniejszą tablicę, aby do siebie pasowały.

```
| 1  2  3 |   +   [10, 20, 30]
| 4  5  6 |

Broadcasting rozciąga wektor na wszystkie wiersze:

| 1  2  3 |   | 10  20  30 |   | 11  22  33 |
| 4  5  6 | + | 10  20  30 | = | 14  25  36 |
```

Każdy nowoczesny framework robi to automatycznie. Zrozumienie tego mechanizmu zapobiega zamieszaniu, gdy kształty wydają się nie pasować, a kod mimo to działa.

## Zbuduj to

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

### Krok 3: Zobacz to w działaniu

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

### Krok 4: Połącz to z sieciami neuronowymi

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

To pojedyncza warstwa gęsta (dense layer): `output = relu(W @ x + b)`. Każda warstwa gęsta w każdej sieci neuronowej robi dokładnie to.

## Zastosuj to

NumPy robi wszystko powyższe w mniejszej liczbie linii i o rzędy wielkości szybciej.

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

Operator `@` w Pythonie wywołuje `__matmul__`. NumPy implementuje go za pomocą zoptymalizowanych procedur BLAS napisanych w C i Fortranie. Ta sama matematyka, 100x szybciej.

Broadcasting w NumPy:

```python
matrix = np.array([[1, 2, 3], [4, 5, 6]])
bias = np.array([10, 20, 30])
print(matrix + bias)
```

NumPy automatycznie rozciąga jednowymiarowy bias na oba wiersze. W ten sposób działa dodawanie biasu w każdym frameworku sieci neuronowych.

## Wykorzystaj to

Ta lekcja tworzy prompt do nauczania operacji macierzowych poprzez intuicję geometryczną. Zobacz `outputs/prompt-matrix-operations.md`.

Klasa Matrix zbudowana tutaj jest fundamentem dla mini frameworka sieci neuronowych, który zbudujemy w Fazie 3, Lekcji 10.

## Ćwiczenia

1. **Zweryfikuj odwrotność.** Pomnóż `A @ A.inverse_2x2()` i potwierdź, że otrzymasz macierz jednostkową. Spróbuj z trzema różnymi macierzami 2x2. Co się dzieje, gdy wyznacznik wynosi zero?

2. **Zaimplementuj odwrotność 3x3.** Rozszerz klasę Matrix o obliczanie odwrotności dla macierzy 3x3 metodą macierzy dołączonej (adjugate). Przetestuj wyniki względem `np.linalg.inv` z NumPy.

3. **Zbuduj dwuwarstwową sieć.** Używając wyłącznie swojej klasy Matrix (bez NumPy), stwórz dwuwarstwową sieć neuronową: wejście (3) -> warstwa ukryta (4) -> wyjście (2). Zainicjalizuj losowe wagi, wykonaj forward pass i zweryfikuj, że wszystkie kształty są poprawne.

## Kluczowe pojęcia

| Pojęcie | Co się mówi | Co to naprawdę oznacza |
|------|----------------|----------------------|
| Wektor | "Strzałka" | Uporządkowana lista liczb. W AI: punkt w przestrzeni wielowymiarowej. |
| Macierz | "Tabela liczb" | Transformacja liniowa. Mapuje wektory z jednej przestrzeni do drugiej. |
| Mnożenie macierzy | "Po prostu mnożysz liczby" | Iloczyny skalarne między każdym wierszem pierwszej macierzy a każdą kolumną drugiej. Kolejność ma znaczenie. |
| Transpozycja | "Odwróć ją" | Zamiana wierszy i kolumn miejscami. Zmienia macierz m x n w n x m. Kluczowe w backpropagation. |
| Wyznacznik | "Jakaś liczba z macierzy" | Mierzy, jak bardzo macierz skaluje pole powierzchni (2D) lub objętość (3D). Zero oznacza, że transformacja zgniata jeden z wymiarów. |
| Odwrotność | "Cofnij macierz" | Macierz, która odwraca transformację. Istnieje tylko wtedy, gdy wyznacznik jest różny od zera. |
| Macierz jednostkowa | "Nudna macierz" | Macierzowy odpowiednik mnożenia przez 1. Używana w połączeniach rezydualnych (ResNet). |
| Broadcasting | "Magiczne dopasowywanie kształtów" | Rozciąganie mniejszej tablicy, aby pasowała do większej, poprzez powtarzanie wzdłuż brakujących wymiarów. |
| Element po elemencie | "Zwykłe mnożenie" | Mnożenie odpowiadających sobie pozycji. Obie tablice muszą mieć ten sam kształt (lub być zgodne dla broadcastingu). |

## Dalsza lektura

- [3Blue1Brown: Essence of Linear Algebra](https://www.3blue1brown.com/topics/linear-algebra) - wizualna intuicja dla każdej omówionej tu operacji
- [NumPy documentation on broadcasting](https://numpy.org/doc/stable/user/basics.broadcasting.html) - dokładne zasady, którymi kieruje się NumPy
- [Stanford CS229 Linear Algebra Review](http://cs229.stanford.edu/section/cs229-linalg.pdf) - zwięzłe odniesienie do algebry liniowej dla ML
