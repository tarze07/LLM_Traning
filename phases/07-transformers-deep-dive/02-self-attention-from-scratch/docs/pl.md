# Samouwaga od podstaw

> Uwaga to tabela przeglądowa, w której przy każdym słowie pojawia się pytanie „kto jest dla mnie ważny?” - i poznaje odpowiedź.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 3 (podstawa głębokiego uczenia się), faza 5, lekcja 10 (sekwencja po sekwencji)
**Czas:** ~90 minut

## Cele nauczania

- Zaimplementuj od podstaw skalowaną samouważność produktu punktowego, używając tylko NumPy, łącznie z projekcjami zapytań/kluczy/wartości i sumą ważoną softmax
- Zbuduj wielogłową warstwę uwagi, która dzieli głowy, oblicza równoległą uwagę i łączy wyniki
- Prześledź, w jaki sposób macierz uwagi przechwytuje relacje tokenów i wyjaśnij, dlaczego skalowanie przez sqrt(d_k) zapobiega nasyceniu softmax
- Zastosuj maskowanie przyczynowe, aby przekształcić uwagę dwukierunkową w uwagę autoregresyjną (w stylu dekodera).

## Problem

Sieci RNN przetwarzają sekwencje po jednym tokenie na raz. Zanim dotrzesz do tokena 50, informacje z tokena 1 zostaną poddane 50 krokom kompresji. Zależności dalekiego zasięgu zostają zmiażdżone do stanu ukrytego o stałym rozmiarze — wąskiego gardła, którego nie rozwiązuje w pełni żadna ilość bramkowania LSTM.

W dokumencie zwracającym uwagę Bahdanau z 2014 r. wskazano rozwiązanie: pozwól dekoderowi spojrzeć wstecz na każdą pozycję kodera i zdecydować, które z nich są istotne dla bieżącego kroku. Ale nadal był przykręcony do RNN. W artykule „Uwaga to wszystko, czego potrzebujesz” z 2017 r. zadano ostrzejsze pytanie: co, jeśli uwaga jest *jedynym* mechanizmem? Brak nawrotów. Brak splotu. Tylko uwaga.

Samouważność pozwala każdej pozycji w sekwencji zająć się każdą inną pozycją w jednym, równoległym kroku. To właśnie sprawia, że ​​transformatory są szybkie, skalowalne i dominujące.

## Koncepcja

### Analogia wyszukiwania w bazie danych

Pomyśl o uwadze jako o miękkim przeszukiwaniu bazy danych:

```
Traditional database:
  Query: "capital of France"  -->  exact match  -->  "Paris"

Attention:
  Query: "capital of France"  -->  similarity to ALL keys  -->  weighted blend of ALL values
```

Każdy token generuje trzy wektory:
- **Zapytanie (Q)**: „Czego szukam?”
- **Klucz (K)**: „Co zawieram?”
- **Wartość (V)**: „Jakie informacje mam podać w przypadku wybrania?”

Iloczyn skalarny między zapytaniem a wszystkimi kluczami daje wyniki uwagi. Wysoki wynik oznacza „ten klucz pasuje do mojego zapytania”. Te wyniki ważą wartości. Dane wyjściowe to ważona suma wartości.

### Obliczenia Q, K, V

Każde osadzenie tokenu jest rzutowane na trzy wyuczone macierze wag:

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

Wizualnie dla jednego tokena:

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

### Matryca uwagi

Kiedy już zdobędziesz Q, K, V dla wszystkich żetonów, wyniki uwagi tworzą macierz:

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

### Dlaczego skalowanie?

Iloczyny skalarne rosną wraz z wymiarem dk. Jeśli dk = 64, produkty skalarne mogą mieścić się w zakresie dziesiątek, wypychając softmax w obszary, w których zanikają gradienty. Poprawka: podziel przez sqrt(dk).

```
Scaled scores = (Q @ K^T) / sqrt(dk)
```

Dzięki temu wartości mieszczą się w zakresie, w którym softmax generuje przydatne gradienty.

### Softmax zamienia wyniki w wagi

Softmax konwertuje surowe wyniki na rozkład prawdopodobieństwa w każdym wierszu:

```
Raw scores for q1:   [2.1, 0.3, 0.1, 0.8, 0.2]
                            |
                         softmax
                            |
Attention weights:   [0.52, 0.09, 0.07, 0.14, 0.08]   (sums to ~1.0)
```

Teraz każdy żeton ma zestaw wag mówiących, ile należy zająć się każdym innym żetonem.

### Ważona suma wartości

Ostateczny wynik dla każdego tokena jest sumą ważoną wszystkich wektorów wartości:

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

## Zbuduj to

### Krok 1: Softmax od zera

Softmax konwertuje surowe logity na prawdopodobieństwa. Odejmij maksimum, aby uzyskać stabilność numeryczną.

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

Podstawowa funkcja. Pobiera macierze Q, K, V i zwraca wynik uwagi plus macierz wag.

```python
def scaled_dot_product_attention(Q, K, V):
    dk = Q.shape[-1]
    scores = Q @ K.T / np.sqrt(dk)
    weights = softmax(scores)
    output = weights @ V
    return output, weights
```

### Krok 3: Zajęcia z samouważności z wyuczonymi projekcjami

Moduł pełnej samouwagi z macierzami wag Wq, Wk, Wv zainicjowanymi skalowaniem podobnym do Xaviera.

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

### Krok 4: Uruchom to na zdaniu

Twórz fałszywe osadzania zdań i obserwuj wagę uwagi.

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

### Krok 5: Zwizualizuj uwagę za pomocą mapy cieplnej ASCII

Przypisz wagi uwagi do postaci, aby uzyskać szybki podgląd.

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

## Użyj tego

`nn.MultiheadAttention` PyTorch robi dokładnie to, co zbudowaliśmy, plus dzielenie wielu głowic i projekcja wyników:

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

Kluczowa różnica: uwaga wielogłowa uruchamia równolegle wiele funkcji uwagi, każda z własnymi projekcjami Q, K, V o rozmiarze dk = d_model / n_heads, a następnie łączy wyniki. Dzięki temu model może jednocześnie zajmować się różnymi typami relacji.

## Wyślij to

Ta lekcja daje:
- `outputs/prompt-attention-explainer.md` – zachęta do wyjaśnienia uwagi poprzez analogię do wyszukiwania w bazie danych

## Ćwiczenia

1. Zmodyfikuj `scaled_dot_product_attention`, aby zaakceptować opcjonalną macierz masek, która ustawia pewne pozycje na ujemną nieskończoność przed softmaxem (tak działa maskowanie przyczynowe/dekoderowe)
2. Zaimplementuj uwagę wielogłową od podstaw: podziel Q, K, V na `n_heads` fragmenty, skieruj uwagę na każdy z nich, połącz i rzutuj przez ostateczną macierz wag Wo
3. Weź dwa różne zdania tej samej długości, przeprowadź je przez tę samą instancję SelfAttention i porównaj ich wzorce uwagi. Jakie zmiany? Co pozostaje takie samo?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|----------------------|
| Zapytanie (Q) | „Wektor pytania” | Wyuczona projekcja danych wejściowych, która reprezentuje, jakich informacji szuka ten token |
| Klucz (K) | „Wektor etykiety” | Wyuczona projekcja reprezentująca informacje zawarte w tym tokenie, dopasowana do zapytań |
| Wartość (V) | „Wektor treści” | Wyuczona projekcja niosąca rzeczywiste informacje, które są agregowane na podstawie wyników uwagi |
| Skalowana uwaga iloczynu skalarnego | „Formuła uwagi” | softmax(QK^T / sqrt(dk)) @ V - skalowanie zapobiega nasyceniu softmaxu w dużych wymiarach |
| Samouważność | „Token patrzy na siebie i innych” | Uwaga, Q, K, V wszystkie pochodzą z tej samej sekwencji, pozwalając, aby każda pozycja odpowiadała każdej innej pozycji |
| Uwaga wagi | „Jak dużo skupienia” | Rozkład prawdopodobieństwa na pozycjach, utworzony przez softmax na iloczynach skalowanych |
| Uwaga wielogłowa | „Uwaga równoległa” | Uruchamianie wielu funkcji uwagi z różnymi projekcjami, a następnie łączenie wyników w celu uzyskania bogatszych reprezentacji |

## Dalsze czytanie

– [Attention Is All You Need (Vaswani et al., 2017)](https://arxiv.org/abs/1706.03762) – oryginalny papier transformatorowy
- [The Illustrated Transformer (Jay Alammar)](https://jalammar.github.io/ilustrated-transformer/) – najlepszy wizualny przewodnik po pełnej architekturze
- [The Annotated Transformer (Harvard NLP)](https://nlp.seas.harvard.edu/annotated-transformer/) - implementacja PyTorch linia po linii z objaśnieniami