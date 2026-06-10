# Mechanizm uwagi — przełom

> Dekoder przestaje przeglądać skompresowane podsumowanie i zaczyna przeglądać całe źródło. Wszystko później to uwaga plus inżynieria.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 5 · 09 (Modele sekwencyjne)
**Czas:** ~45 minut

## Problem

Lekcja 09 zakończyła się wymierzoną awarią. Koder-dekoder GRU wytrenowany w zadaniu kopiowania zabawki osiąga dokładność od 89% na długości 5 do niemal przypadkowej na długości 80. Powód jest strukturalny, a nie błąd szkoleniowy: każda informacja zebrana przez koder musi zmieścić się w jednym stanie ukrytym o stałym rozmiarze, a dekoder nigdy nie widzi niczego innego.

Bahdanau, Cho i Bengio opublikowali poprawkę składającą się z trzech linii w 2014 r. Zamiast podawać dekoderowi tylko ostateczny stan kodera, zachowaj stan każdego kodera. Na każdym kroku dekodera oblicz średnią ważoną stanów kodera, gdzie wagi mówią „jak bardzo dekoder musi teraz sprawdzać pozycję kodera `i`?” Ta średnia ważona to kontekst, który zmienia się w każdym kroku dekodera.

To jest cały pomysł. Transformers to przedłużyli. Samouważność zastosowała to do pojedynczej sekwencji. Uwaga wielu głów działała równolegle. Ale wersja 2014 już przełamała wąskie gardło, a kiedy już ją uzyskasz, głównym tematem transformatorów jest inżynieria, a nie koncepcja.

## Koncepcja

![Uwaga Bahdanau: dekoder odpytuje wszystkie stany kodera](../assets/attention.svg)

Na każdym etapie dekodera `t`:

1. Użyj poprzedniego stanu ukrytego dekodera `s_{t-1}` jako **zapytania**.
2. Oceń go względem każdego ukrytego stanu kodera `h_1, ..., h_T`. Jeden skalar na pozycję enkodera.
3. Softmax wyniki, aby uzyskać wagi uwagi `α_{t,1}, ..., α_{t,T}`, których suma wynosi 1.
4. Wektor kontekstu `c_t = Σ α_{t,i} * h_i`. Średnia ważona stanów enkodera.
5. Dekoder pobiera `c_t` plus poprzedni token wyjściowy i generuje następny token.

Najważniejsza jest średnia ważona. Kiedy dekoder musi przetłumaczyć „Je” na „I”, waży stan kodera nad wysokim „Je” i pozostałymi niskimi. Kiedy potrzebuje „nie”, waży „pas” wysoko. Wektor kontekstu zmienia każdy krok.

## Kształty (to, co gryzie wszystkich)

To tutaj każda implementacja uwagi kończy się niepowodzeniem za pierwszym razem. Czytaj powoli.

| Rzecz | Kształt | Notatki |
|-------|-------|------|
| Ukryte stany kodera `H` | `(T_enc, d_h)` | Jeśli BiLSTM, `d_h = 2 * d_hidden` |
| Stan ukryty dekodera `s_{t-1}` | `(d_s,)` | Jeden wektor |
| Wynik uwagi `e_{t,i}` | skalar | Jeden na pozycję enkodera |
| Waga uwagi `α_{t,i}` | skalar | Po softmax na wszystkich `i` |
| Wektor kontekstu `c_t` | `(d_h,)` | Taki sam kształt jak stan kodera |

**Wynik Bahdanau (addytywny).** `e_{t,i} = v_α^T * tanh(W_a * s_{t-1} + U_a * h_i)`.

- `s_{t-1}` ma kształt `(d_s,)`, `h_i` ma kształt `(d_h,)`.
- `W_a` ma kształt `(d_attn, d_s)`. `U_a` ma kształt `(d_attn, d_h)`.
- Ich suma wewnątrz tanh ma kształt `(d_attn,)`.
- `v_α` ma kształt `(d_attn,)`. Iloczyn wewnętrzny z `v_α` zwija się do skalara. **To właśnie robi `v_α`.** To nie jest magia. To projekcja zmienia wektor przyćmiony uwagą w wynik skalarny.

**Wynik Luonga (multiplikatywny).** Trzy warianty:

- `dot`: `e_{t,i} = s_t^T * h_i`. Wymaga `d_s == d_h`. Twarde ograniczenie. Pomiń, jeśli koder jest dwukierunkowy.
- `general`: `e_{t,i} = s_t^T * W * h_i` z kształtem `W` `(d_s, d_h)`. Usuwa wiązanie równego przyciemnienia.
- `concat`: zasadniczo forma Bahdanau. Rzadko używane, ponieważ pierwsze dwa są tańsze.

**Jeden Bahdanau / Luong jest warty wymienienia.** Bahdanau używa `s_{t-1}` (stan dekodera *przed* wygenerowaniem bieżącego słowa). Luong używa `s_t` (stan *po*). Mieszanie ich powoduje powstanie subtelnie błędnych gradientów, które są niezwykle trudne do debugowania. Wybierz jeden artykuł i trzymaj się jego konwencji.

## Zbuduj to

### Krok 1: uwaga addytywna (Bahdanau).

```python
import numpy as np

def additive_attention(decoder_state, encoder_states, W_a, U_a, v_a):
    projected_dec = W_a @ decoder_state
    projected_enc = encoder_states @ U_a.T
    combined = np.tanh(projected_enc + projected_dec)
    scores = combined @ v_a
    weights = softmax(scores)
    context = weights @ encoder_states
    return context, weights

def softmax(x):
    x = x - np.max(x)
    e = np.exp(x)
    return e / e.sum()
```

Sprawdź swoje kształty w tabeli powyżej. `encoder_states` ma kształt `(T_enc, d_h)`. `projected_enc` ma kształt `(T_enc, d_attn)`. `projected_dec` ma kształt `(d_attn,)` i nadaje. `combined` ma kształt `(T_enc, d_attn)`. `scores` ma kształt `(T_enc,)`. `weights` ma kształt `(T_enc,)`. `context` ma kształt `(d_h,)`. Wyślij to.

### Krok 2: kropka Luonga i informacje ogólne

```python
def dot_attention(decoder_state, encoder_states):
    scores = encoder_states @ decoder_state
    weights = softmax(scores)
    return weights @ encoder_states, weights

def general_attention(decoder_state, encoder_states, W):
    projected = W.T @ decoder_state
    scores = encoder_states @ projected
    weights = softmax(scores)
    return weights @ encoder_states, weights
```

Po trzy linie każda. Dlatego właśnie wylądowała gazeta Luonga. Ta sama dokładność w przypadku większości zadań, znacznie mniej kodu.

### Krok 3: sprawdzony przykład numeryczny

Biorąc pod uwagę trzy stany kodera (w przybliżeniu „cat”, „sat”, „mat”) i stan dekodera, który najbardziej odpowiada pierwszemu, rozkład uwagi koncentruje się na pozycji 0. Jeśli stan dekodera przesuwa się w celu dopasowania do ostatniego, uwaga przesuwa się do pozycji 2. Śledzenie wektora kontekstu.

```python
H = np.array([
    [1.0, 0.0, 0.2],
    [0.5, 0.5, 0.1],
    [0.1, 0.9, 0.3],
])

s_close_to_cat = np.array([0.9, 0.1, 0.2])
ctx, w = dot_attention(s_close_to_cat, H)
print("weights:", w.round(3))
```

```
weights: [0.464 0.305 0.231]
```

Pierwszy rząd wygrywa. Następnie przesuń stan dekodera bliżej trzeciego stanu kodera i obserwuj zmianę wag. To jest to. Uwaga jest wyraźnym wyrównaniem.

### Krok 4: dlaczego jest to pomost do transformatorów

Przetłumacz powyższy język na Q/K/V:

- **Zapytanie** = stan dekodera `s_{t-1}`
- **Klucz** = stany kodera (na podstawie czego oceniamy)
- **Wartość** = stany kodera (co ważymy i sumujemy)

W klasycznej uwadze klucze i wartości są tym samym. Samouważność je rozdziela: możesz skierować sekwencję przeciwko sobie, z różnymi wyuczonymi projekcjami dla K i V. Uwaga wielogłowa uruchamia ją równolegle z różnymi wyuczonymi projekcjami. Transformatory wielokrotnie układają całą scenę i upuszczają RNN.

Matematyka jest taka sama. Kształty są takie same. Pedagogiczny skok od uwagi Bahdanau do skalowanej uwagi iloczynu skalarnego polega głównie na notacji.

## Użyj tego

PyTorch i TensorFlow bezpośrednio przyciągają uwagę.

```python
import torch
import torch.nn as nn

mha = nn.MultiheadAttention(embed_dim=128, num_heads=8, batch_first=True)
query = torch.randn(2, 5, 128)
key = torch.randn(2, 10, 128)
value = torch.randn(2, 10, 128)

output, weights = mha(query, key, value)
print(output.shape, weights.shape)
```

```
torch.Size([2, 5, 128]) torch.Size([2, 5, 10])
```

To jest warstwa uwagi transformatora. Partia zapytań z 5 pozycjami, partia klucz/wartość z 10 pozycji, 128 przyciemnień każda, 8 głowic. `output` to nowe zapytania kontekstowe. `weights` to macierz wyrównania 5x10, którą możesz wizualizować.

### Kiedy klasyczna uwaga nadal ma znaczenie

- Pedagogika. Wersja jednogłowicowa, jednowarstwowa, oparta na technologii RNN sprawia, że ​​każda koncepcja jest widoczna.
- Zadania sekwencyjne na urządzeniu, w których transformatory nie pasują.
- Dowolny artykuł z lat 2014-2017. Źle to odczytasz, nie znając konwencji Bahdanau.
- Drobnoziarnista analiza wyrównania w MT. Surowe wagi uwagi są narzędziem umożliwiającym interpretację nawet w przypadku modeli transformatorów, a ich odczytanie wymaga wiedzy, czym one są.

### Pułapka skupiająca uwagę jako wyjaśnienie

Wagi uwagi wydają się możliwe do zinterpretowania. Są to wagi, które sumują się do jedności na wszystkich pozycjach; możesz je nakreślić; wysoki oznacza „przyjrzałem się temu”. Recenzenci je uwielbiają.

Nie da się ich tak zinterpretować, jak wyglądają. Jain i Wallace (2019) wykazali, że rozkłady uwagi można permutować i zastępować dowolnymi alternatywami bez zmiany przewidywań modelu dla niektórych zadań. Nigdy nie podawaj wag uwagi jako dowodu uzasadnienia bez ablacji lub sprawdzenia kontrfaktycznego.

## Wyślij to

Zapisz jako `outputs/prompt-attention-shapes.md`:

```markdown
---
name: attention-shapes
description: Debug shape bugs in attention implementations.
phase: 5
lesson: 10
---

Given a broken attention implementation, you identify the shape mismatch. Output:

1. Which matrix has the wrong shape. Name the tensor.
2. What its shape should be, derived from (d_s, d_h, d_attn, T_enc, T_dec, batch_size).
3. One-line fix. Transpose, reshape, or project.
4. A test to catch regressions. Typically: assert `output.shape == (batch, T_dec, d_h)` and `weights.shape == (batch, T_dec, T_enc)` and `weights.sum(dim=-1) close to 1`.

Refuse to recommend fixes that silently broadcast. Broadcast-hiding bugs surface later as silent accuracy degradation, the worst kind of attention bug.

For Bahdanau confusion, insist the decoder input is `s_{t-1}` (pre-step state). For Luong, `s_t` (post-step state). For dot-product, flag dimension mismatch between query and key as the most common first-time error.
```

## Ćwiczenia

1. **Łatwe.** Zaimplementuj maskowanie `softmax`, aby tokeny dopełniające w koderze miały wagę zerową. Przetestuj na partii z sekwencjami o zmiennej długości.
2. **Średni.** Dodaj wielogłową uwagę do formularza Luong `general`. Podziel `d_h` na grupy `n_heads`, zwróć uwagę na każdą głowę, połącz. Sprawdź, czy obudowa z pojedynczą głowicą pasuje do wcześniejszej implementacji.
3. **Trudne.** Trenuj koder-dekoder GRU z uwagą Bahdanau w zakresie zadania kopiowania zabawek z lekcji 09. Dokładność wykresu a długość sekwencji. Porównaj z wartością bazową braku uwagi. Powinieneś zobaczyć, jak luka poszerza się wraz ze wzrostem długości, co potwierdza, że ​​uwaga znosi wąskie gardło.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Uwaga | Patrząc na rzeczy | Średnia ważona sekwencji wartości, wagi obliczone na podstawie podobieństwa klucza zapytania. |
| Zapytanie, klucz, wartość | QKV | Trzy projekcje: Q pyta, K to, co dopasować, V to, co zwrócić. |
| Uwaga addytywna | Bahdanau | Wynik sprzężenia zwrotnego: `v^T tanh(W q + U k)`. |
| Uwaga multiplikatywna | Kropka Luonga / ogólne | Wynik to `q^T k` lub `q^T W k`. Tańsze, ta sama dokładność w przypadku większości zadań. |
| Macierz wyrównania | Ładny obrazek | Wagi uwagi jako siatka `(T_dec, T_enc)`. Przeczytaj, żeby zobaczyć, czym zajmował się model. |

## Dalsze czytanie

- [Bahdanau, Cho, Bengio (2014). Neural Machine Translation by Jointly Learning to Align and Translate](https://arxiv.org/abs/1409.0473) – artykuł.
- [Luong, Pham, Manning (2015). Efektywne podejścia do neuronowego tłumaczenia maszynowego opartego na uwadze](https://arxiv.org/abs/1508.04025) — trzy warianty punktacji i ich porównanie.
- [Jain i Wallace (2019). Uwaga nie jest wyjaśnieniem](https://arxiv.org/abs/1902.10186) — zastrzeżenie dotyczące interpretacji.
- [Zanurz się w głębokie uczenie się — Bahdanau Attention](https://d2l.ai/chapter_attention-mechanisms-and-transformers/bahdanau-attention.html) — przewodnik, który można uruchomić za pomocą PyTorch.