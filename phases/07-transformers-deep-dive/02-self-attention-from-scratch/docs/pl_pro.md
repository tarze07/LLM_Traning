# Mechanizm self-attention od podstaw

> Uwaga to rodzaj miękkiego przeszukiwania: przy każdym słowie model zadaje pytanie „które inne słowa są dla mnie istotne?" — i na podstawie odpowiedzi buduje nową reprezentację.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 3 (podstawy głębokiego uczenia), faza 5, lekcja 10 (sekwencja do sekwencji)
**Czas:** ~90 minut

## Cele nauczania

- Zaimplementuj od podstaw skalowany mechanizm scaled dot-product attention przy użyciu wyłącznie NumPy, włącznie z rzutowaniami zapytań, kluczy i wartości oraz ważoną sumą softmax.
- Zbuduj wielogłową warstwę uwagi, która rozdziela głowice, oblicza uwagę równolegle i scala wyniki.
- Prześledź, w jaki sposób macierz uwagi koduje relacje między tokenami, i wyjaśnij, dlaczego skalowanie przez sqrt(d_k) zapobiega nasyceniu softmax.
- Zastosuj maskowanie przyczynowe, aby przekształcić uwagę dwukierunkową w uwagę autoregresyjną (w stylu dekodera).

## Problem

Sieci RNN przetwarzają sekwencje token po tokenie. Zanim model dotrze do pozycji 50., informacja z pozycji 1. przejdzie przez 50 kroków kompresji. Zależności długodystansowe zostają wtłoczone w ukryty stan o stałym rozmiarze — wąskie gardło, którego żadna liczba bramek LSTM nie jest w stanie w pełni wyeliminować.

Artykuł Bahdanau z 2014 roku wskazał wyjście z tej pułapki: pozwól dekoderowi bezpośrednio przyglądać się każdej pozycji kodera i samodzielnie decydować, które z nich są istotne na bieżącym kroku. Rozwiązanie to było jednak nadal sprzężone z architekturą RNN. Artykuł „Attention Is All You Need" z 2017 roku postawił odważniejsze pytanie: co jeśli mechanizm uwagi jest *jedynym* składnikiem? Bez rekurencji. Bez splotu. Tylko uwaga.

Mechanizm self-attention umożliwia każdej pozycji w sekwencji powiązanie się z dowolną inną pozycją w jednym, równoległym kroku. To właśnie dlatego transformery są szybkie, skalowalne i tak powszechnie stosowane.

## Koncepcja

### Analogia do przeszukiwania bazy danych

Mechanizm uwagi można traktować jako miękkie przeszukiwanie bazy danych:

```
Traditional database:
  Query: "capital of France"  -->  exact match  -->  "Paris"

Attention:
  Query: "capital of France"  -->  similarity to ALL keys  -->  weighted blend of ALL values
```

Każdy token generuje trzy wektory:
- **Zapytanie (Q)**: „Czego szukam?"
- **Klucz (K)**: „Co sobą reprezentuję?"
- **Wartość (V)**: „Jaką informację dostarczam, gdy zostanę wybrany?"

Iloczyn skalarny zapytania z każdym kluczem daje wyniki uwagi. Wysoki wynik oznacza „ten klucz odpowiada mojemu zapytaniu". Te wyniki ważą wektory wartości, a dane wyjściowe stanowią ich ważoną sumę.

### Obliczanie Q, K, V

Każde osadzenie tokenu jest rzutowane za pomocą trzech wyuczonych macierzy wag:

```
Input embeddings (sequence of n tokens, each d-dimensional):

  X = [x1, x2, x3, ..., xn]       shape: (n, d)

Three weight matrices:

  Wq  shape: (d, dk)
  Wk  shape: (d, dk)
  Wv  shape: (d, dv)

Projections:

  Q = X @ Wq    shape: (n, dk)      each token's query
  K = X @ Wk    shape: (n, dk)      each token's key
  V = X @ Wv    shape: (n, dv)      each token's value
```

Graficznie, dla pojedynczego tokenu:

```
             Wq
  x_i ------[*]------> q_i    "What am I looking for?"
       |
       |     Wk
       +----[*]------> k_i    "What do I contain?"
       |
       |     Wv
       +----[*]------> v_i    "What do I offer?"
```

### Macierz uwagi

Po wyznaczeniu Q, K, V dla wszystkich tokenów wyniki uwagi tworzą macierz:

```
Scores = Q @ K^T    shape: (n, n)

              k1    k2    k3    k4    k5
        +-----+-----+-----+-----+-----+
   q1   | 2.1 | 0.3 | 0.1 | 0.8 | 0.2 |   <- how much q1 attends to each key
        +-----+-----+-----+-----+-----+
   q2   | 0.4 | 1.9 | 0.7 | 0.1 | 0.3 |
        +-----+-----+-----+-----+-----+
   q3   | 0.2 | 0.6 | 2.3 | 0.5 | 0.1 |
        +-----+-----+-----+-----+-----+
   q4   | 0.9 | 0.1 | 0.4 | 1.7 | 0.6 |
        +-----+-----+-----+-----+-----+
   q5   | 0.1 | 0.3 | 0.2 | 0.5 | 2.0 |
        +-----+-----+-----+-----+-----+

Each row: one token's attention over the entire sequence
```

### Po co skalowanie?

Iloczyny skalarne rosną wraz z wymiarem dk. Gdy dk = 64, wartości iloczynów mogą sięgać dziesiątek, wypychając softmax w obszar, gdzie gradienty zanikają. Rozwiązanie jest proste: podziel przez sqrt(dk).

```
Scaled scores = (Q @ K^T) / sqrt(dk)
```

Dzięki temu wyniki utrzymują się w zakresie, gdzie softmax generuje użyteczne gradienty.

### Softmax zamienia wyniki w wagi

Softmax przekształca surowe wyniki w rozkład prawdopodobieństwa dla każdego wiersza:

```
Raw scores for q1:   [2.1, 0.3, 0.1, 0.8, 0.2]
                            |
                         softmax
                            |
Attention weights:   [0.52, 0.09, 0.07, 0.14, 0.08]   (sums to ~1.0)
```

Każdy token dysponuje teraz zestawem wag określających, ile uwagi poświęca pozostałym tokenom.

### Ważona suma wartości

Końcowa reprezentacja każdego tokenu to ważona suma wszystkich wektorów wartości:

```
output_i = sum( attention_weight[i][j] * v_j  for all j )

For token 1:
  output_1 = 0.52 * v1 + 0.09 * v2 + 0.07 * v3 + 0.14 * v4 + 0.08 * v5
```

### Pełny potok

```
                    +-------+
  X (input)  ----->|  @ Wq  |-----> Q
                    +-------+
                    +-------+
  X (input)  ----->|  @ Wk  |-----> K
                    +-------+                     +----------+
                    +-------+                     |          |
  X (input)  ----->|  @ Wv  |-----> V ---------->| weighted |----> output
                    +-------+          ^          |   sum    |
                                       |          +----------+
                              +--------+--------+
                              |    softmax      |
                              +---------+-------+
                                        ^
                              +---------+-------+
                              | Q @ K^T / sqrt  |
                              +-----------------+
```

Formuła w jednej linii:

```
Attention(Q, K, V) = softmax( Q @ K^T / sqrt(dk) ) @ V
```

## Implementacja

### Krok 1: Softmax od podstaw

Softmax przekształca surowe logity w prawdopodobieństwa. Dla stabilności numerycznej odejmij wcześniej wartość maksymalną.

```python
import numpy as np

def softmax(x):
    shifted = x - np.max(x, axis=-1, keepdims=True)
    exp_x = np.exp(shifted)
    return exp_x / np.sum(exp_x, axis=-1, keepdims=True)

logits = np.array([2.0, 1.0, 0.1])
print(f"logits:  {logits}")
print(f"softmax: {softmax(logits)}")
print(f"sum:     {softmax(logits).sum():.4f}")
```

### Krok 2: Skalowana uwaga iloczynu skalarnego

Podstawowa funkcja mechanizmu uwagi. Przyjmuje macierze Q, K, V i zwraca wynik uwagi wraz z macierzą wag.

```python
def scaled_dot_product_attention(Q, K, V):
    dk = Q.shape[-1]
    scores = Q @ K.T / np.sqrt(dk)
    weights = softmax(scores)
    output = weights @ V
    return output, weights
```

### Krok 3: Klasa SelfAttention z wyuczonymi rzutowaniami

Pełny moduł self-attention z macierzami wag Wq, Wk, Wv inicjowanymi zgodnie ze schematem Xaviera.

```python
class SelfAttention:
    def __init__(self, d_model, dk, dv, seed=42):
        rng = np.random.default_rng(seed)
        scale = np.sqrt(2.0 / (d_model + dk))
        self.Wq = rng.normal(0, scale, (d_model, dk))
        self.Wk = rng.normal(0, scale, (d_model, dk))
        scale_v = np.sqrt(2.0 / (d_model + dv))
        self.Wv = rng.normal(0, scale_v, (d_model, dv))
        self.dk = dk

    def forward(self, X):
        Q = X @ self.Wq
        K = X @ self.Wk
        V = X @ self.Wv
        output, weights = scaled_dot_product_attention(Q, K, V)
        return output, weights
```

### Krok 4: Uruchomienie na przykładowym zdaniu

Stwórz losowe osadzenia zdania i przyjrzyj się rozkładowi wag uwagi.

```python
sentence = ["The", "cat", "sat", "on", "the", "mat"]
n_tokens = len(sentence)
d_model = 8
dk = 4
dv = 4

rng = np.random.default_rng(42)
X = rng.normal(0, 1, (n_tokens, d_model))

attn = SelfAttention(d_model, dk, dv, seed=42)
output, weights = attn.forward(X)

print("Attention weights (each row: where that token looks):\n")
print(f"{'':>6}", end="")
for token in sentence:
    print(f"{token:>6}", end="")
print()

for i, token in enumerate(sentence):
    print(f"{token:>6}", end="")
    for j in range(n_tokens):
        w = weights[i][j]
        print(f"{w:6.3f}", end="")
    print()
```

### Krok 5: Wizualizacja uwagi jako mapa cieplna ASCII

Odwzoruj wagi uwagi na znaki, aby szybko podejrzeć wzorzec skupienia.

```python
def ascii_heatmap(weights, tokens, chars=" ░▒▓█"):
    n = len(tokens)
    print(f"\n{'':>6}", end="")
    for t in tokens:
        print(f"{t:>6}", end="")
    print()

    for i in range(n):
        print(f"{tokens[i]:>6}", end="")
        for j in range(n):
            level = int(weights[i][j] * (len(chars) - 1) / weights.max())
            level = min(level, len(chars) - 1)
            print(f"{'  ' + chars[level] + '   '}", end="")
        print()

ascii_heatmap(weights, sentence)
```

## Zastosowanie w PyTorch

`nn.MultiheadAttention` z PyTorch realizuje dokładnie to samo, co zbudowaliśmy powyżej, dodając podział na wiele głowic oraz rzutowanie wyników:

```python
import torch
import torch.nn as nn

d_model = 8
n_heads = 2
seq_len = 6

mha = nn.MultiheadAttention(embed_dim=d_model, num_heads=n_heads, batch_first=True)

X_torch = torch.randn(1, seq_len, d_model)

output, attn_weights = mha(X_torch, X_torch, X_torch)

print(f"Input shape:            {X_torch.shape}")
print(f"Output shape:           {output.shape}")
print(f"Attention weight shape: {attn_weights.shape}")
print(f"\nAttn weights (averaged over heads):")
print(attn_weights[0].detach().numpy().round(3))
```

Kluczowa różnica polega na tym, że multi-head attention uruchamia równolegle wiele funkcji uwagi — każda z oddzielnymi rzutowaniami Q, K, V o rozmiarze dk = d_model / n_heads — po czym scala ich wyniki. Dzięki temu model może jednocześnie uchwycić różne typy relacji między tokenami.

## Artefakty

Ta lekcja wytwarza:
- `outputs/prompt-attention-explainer.md` — podpowiedź do wyjaśnienia mechanizmu uwagi przez analogię z przeszukiwaniem bazy danych

## Ćwiczenia

1. Zmodyfikuj `scaled_dot_product_attention` tak, aby przyjmowała opcjonalną macierz masek ustawiającą wybrane pozycje na minus nieskończoność przed softmax (tak działa maskowanie przyczynowe stosowane w dekoderach).
2. Zaimplementuj multi-head attention od podstaw: podziel Q, K, V na `n_heads` fragmentów, oblicz uwagę dla każdego z nich, połącz wyniki i przeprowadź przez końcową macierz wag Wo.
3. Weź dwa różne zdania tej samej długości, przepuść je przez tę samą instancję SelfAttention i porównaj wzorce uwagi. Co się zmienia? Co pozostaje niezmienne?

## Kluczowe terminy

| Termin | Co się mówi | Co to naprawdę oznacza |
|------|----------------|----------------------|
| Zapytanie (Q) | „Wektor pytania" | Wyuczone rzutowanie danych wejściowych reprezentujące, jakich informacji poszukuje dany token |
| Klucz (K) | „Wektor etykiety" | Wyuczone rzutowanie reprezentujące informacje zawarte w tokenie, dopasowywane do zapytań |
| Wartość (V) | „Wektor treści" | Wyuczone rzutowanie niosące faktyczną informację agregowaną na podstawie wyników uwagi |
| Scaled dot-product attention | „Formuła uwagi" | softmax(QK^T / sqrt(dk)) @ V — skalowanie zapobiega nasyceniu softmax w przestrzeniach wysokowymiarowych |
| Self-attention | „Token patrzy na siebie i innych" | Mechanizm uwagi, w którym Q, K, V pochodzą z tej samej sekwencji, co pozwala każdej pozycji powiązać się z każdą inną |
| Wagi uwagi | „Rozkład skupienia" | Rozkład prawdopodobieństwa na pozycjach sekwencji, uzyskany przez softmax ze skalowanych iloczynów skalarnych |
| Multi-head attention | „Równoległa uwaga" | Uruchomienie wielu funkcji uwagi z oddzielnymi rzutowaniami, a następnie scalenie wyników dla bogatszych reprezentacji |

## Dalsza lektura

– [Attention Is All You Need (Vaswani et al., 2017)](https://arxiv.org/abs/1706.03762) — oryginalny artykuł opisujący architekturę transformera
- [The Illustrated Transformer (Jay Alammar)](https://jalammar.github.io/ilustrated-transformer/) — najlepszy wizualny przewodnik po pełnej architekturze
- [The Annotated Transformer (Harvard NLP)](https://nlp.seas.harvard.edu/annotated-transformer/) — implementacja PyTorch linia po linii z objaśnieniami
