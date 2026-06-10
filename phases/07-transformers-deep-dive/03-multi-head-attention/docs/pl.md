# Uwaga wielogłowa

> Jedna głowa uwagi uczy się jednej relacji na raz. Osiem głów uczy się ośmiu. Głowy są wolne. Weź ich więcej.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 7 · 02 (Samouważność od podstaw)
**Czas:** ~75 minut

## Problem

Pojedyncza głowa samouważności oblicza jedną macierz uwagi. Ta macierz rejestruje jeden rodzaj relacji — zwykle taką, która minimalizuje straty niezależnie od sygnału treningowego. Jeśli dane mają zgodność podmiot-orzeczenie, współodniesienie, dyskurs dalekiego zasięgu i fragmenty syntaktyczne, a wszystko to splątane razem, pojedyncza głowa rozmazuje je w jeden rozkład o miękkim maksimum i traci połowę sygnału.

Poprawka z artykułu Vaswani z 2017 r.: uruchom równolegle kilka funkcji uwagi, każda z własnymi projekcjami Q, K, V i połącz wyniki. Każda głowa działa w mniejszej podprzestrzeni o wymiarze `d_model / n_heads`. Ogólne parametry pozostają takie same. Siła ekspresji rośnie.

Uwaga wielogłowicowa jest domyślną opcją, z którą dostarczany jest każdy transformator w roku 2026. Jedyny argument dotyczy *ilu* głowic i tego, czy klucze i wartości mają wspólne prognozy (Uwaga na zapytanie grupowe, Uwaga na wiele zapytań, Uwaga ukryta na wiele głowic).

## Koncepcja

![Uwaga wielu głów dzieli, uczestniczy, łączy](../assets/multi-head-attention.svg)

**Podziel.** Weź `X` kształt `(N, d_model)`. Projektuj dla Q, K, V każdy o kształcie `(N, d_model)`. Zmień kształt na `(N, n_heads, d_head)` gdzie `d_head = d_model / n_heads`. Transponuj do `(n_heads, N, d_head)`.

** Uczestniczyjcie równolegle. ** Przeprowadź skalowaną uwagę iloczynu skalarnego w każdej głowie. Każda głowa wytwarza `(N, d_head)`. Głowy działają w różnych podprzestrzeniach osadzania i nigdy nie rozmawiają podczas samego obliczania uwagi.

**Połącz i projektuj.** Ułóż stosy z powrotem do `(N, d_model)` i pomnóż przez poznaną macierz wyników `W_o` o kształcie `(d_model, d_model)`. `W_o` to miejsce, w którym mieszają się głowy.

**Dlaczego to działa.** Każdy szef może się specjalizować, nie konkurując z innymi o budżet reprezentacyjny. Badania sondujące z lat 2019–2024 pokazują różne role głów: głowy pozycyjne, głowy obsługujące poprzedni token, głowy kopiujące, głowy nazwanych podmiotów, głowy indukcyjne (które leżą u podstaw uczenia się w kontekście).

**Rodowód odmian z 2026 r.:**

| Wariant | Głowy Q | Głowice K/V | Używany przez |
|--------|---------|------|---------|
| Wielogłowicowy (MHA) | N | N | GPT-2, BERT, T5 |
| Wiele zapytań (MQA) | N | 1 | PaLM, Sokół |
| Zapytanie grupowe (GQA) | N | G (np. N/8) | Lama 2 70B, Lama 3+, Qwen 2+, Mistral |
| Utajone wielogłowicowe (MLA) | N | skompresowany do niskiej rangi | DeepSeek-V2, V3 |

Współczesną opcją domyślną jest GQA, ponieważ zmniejsza pamięć podręczną KV o współczynnik `N/G`, zachowując prawie pełną jakość. MLA idzie dalej, kompresując K/V do ukrytej przestrzeni, a następnie wyświetlając wstecz w czasie obliczeniowym — kosztuje FLOP, oszczędza dużo więcej pamięci.

## Zbuduj to

### Krok 1: oddziel głowy od uwagi pojedynczej głowy, którą już mamy

Weź `SelfAttention` z lekcji 02 i owiń go parą split/concat. Zobacz `code/main.py`, aby zapoznać się z implementacją numpy; logika jest taka:

```python
def split_heads(X, n_heads):
    n, d = X.shape
    d_head = d // n_heads
    return X.reshape(n, n_heads, d_head).transpose(1, 0, 2)  # (heads, n, d_head)

def combine_heads(H):
    h, n, d_head = H.shape
    return H.transpose(1, 0, 2).reshape(n, h * d_head)
```

Jedna zmiana kształtu i jedna transpozycja. Brak pętli. To jest dokładnie to, co robi PyTorch w `nn.MultiheadAttention`.

### Krok 2: przeprowadź analizę skalowanych produktów punktowych na głowę

Każda głowa otrzymuje swój własny kawałek Q, K, V. Uwaga staje się matmulem wsadowym:

```python
def mha_forward(X, W_q, W_k, W_v, W_o, n_heads):
    Q = X @ W_q
    K = X @ W_k
    V = X @ W_v
    Qh = split_heads(Q, n_heads)         # (heads, n, d_head)
    Kh = split_heads(K, n_heads)
    Vh = split_heads(V, n_heads)
    scores = Qh @ Kh.transpose(0, 2, 1) / np.sqrt(Qh.shape[-1])
    weights = softmax(scores, axis=-1)
    out = weights @ Vh                    # (heads, n, d_head)
    concat = combine_heads(out)
    return concat @ W_o, weights
```

Na prawdziwym sprzęcie `Qh @ Kh.transpose(...)` jest jeden `bmm`. Procesor graficzny widzi pojedynczą wsadową matmulę kształtu `(heads, N, d_head) × (heads, d_head, N) -> (heads, N, N)`. Dodanie głowic jest bezpłatne.

### Krok 3: wariant uwagi z zapytaniem grupowym

Zmieniają się tylko prognozy klucza i wartości. Q pobiera `n_heads` grupy; K i V otrzymują grupy `n_kv_heads < n_heads` i są powtarzane w celu dopasowania:

```python
def gqa_project(X, W, n_kv_heads, n_heads):
    kv = split_heads(X @ W, n_kv_heads)       # (kv_heads, n, d_head)
    repeat = n_heads // n_kv_heads
    return np.repeat(kv, repeat, axis=0)      # (n_heads, n, d_head)
```

Podsumowując, oszczędza to pamięć, ponieważ tylko `n_kv_heads` kopiuje na żywo w pamięci podręcznej KV, a nie `n_heads`. Lama 3 70B wykorzystuje 64 głowice zapytań z 8 głowicami KV – co oznacza zmniejszenie pamięci podręcznej 8×.

### Krok 4: sprawdź, czego nauczyła się każda głowa

Uruchom MHA krótkim zdaniem z 4 głowami. Dla każdej głowy wydrukuj macierz uwagi `(N, N)`. Zobaczysz, że różne głowy wybierają inną strukturę nawet przy losowej inicjalizacji — jest to częściowo sygnał, częściowo symetria obrotowa w podprzestrzeniach.

## Użyj tego

W PyTorch wersja jednowierszowa:

```python
import torch.nn as nn

mha = nn.MultiheadAttention(embed_dim=512, num_heads=8, batch_first=True)
```

GQA od PyTorch 2.5+:

```python
from torch.nn.functional import scaled_dot_product_attention

# scaled_dot_product_attention auto-dispatches Flash Attention on CUDA.
# For GQA, pass Q of shape (B, n_heads, N, d_head) and K,V of shape
# (B, n_kv_heads, N, d_head). PyTorch handles the repeat.
out = scaled_dot_product_attention(q, k, v, is_causal=True, enable_gqa=True)
```

**Ile głów?** Praktyczne zasady dotyczące modeli produkcyjnych w 2026 r.:

| Rozmiar modelu | d_model | n_głowy | d_głowa |
|------------|--------|---------|-------|
| Mały (~125M) | 768 | 12 | 64 |
| Baza (~350M) | 1024 | 16 | 64 |
| Duży (~1B) | 2048 | 16 | 128 |
| Granica (~70B) | 8192 | 64 | 128 |

`d_head` prawie zawsze kończy się na 64 lub 128. Jest to jednostka określająca, ile „widzi” jedna głowa. Spadek poniżej 32 i głowy zaczynają walczyć ze współczynnikiem skalowania `sqrt(d_head)`; przekroczysz 256 i utracisz korzyść „wielu małych specjalistów”.

## Wyślij to

Zobacz `outputs/skill-mha-configurator.md`. Umiejętność zaleca liczbę głowic, liczbę głowic kv i strategię projekcji dla nowego transformatora, biorąc pod uwagę budżet parametrów, długość sekwencji i cel wdrożenia.

## Ćwiczenia

1. **Łatwo.** Weź MHA z `code/main.py` i zmień `n_heads` z 1 na 16 z poprawionym `d_model=64`. Narysuj stratę małego jednowarstwowego modelu w zadaniu syntetycznego kopiowania. Czy więcej głów pomaga, stabilizuje czy szkodzi?
2. **Średni.** Zaimplementuj MQA (jedna głowica KV współdzielona przez wszystkie głowice zapytań). Zmierz, o ile spada liczba parametrów w porównaniu z pełnym MHA. Oblicz, o ile zmniejsza się rozmiar pamięci podręcznej KV przy wnioskowaniu dla N=2048.
3. **Trudne.** Zaimplementuj małą wersję Multi-head Latent Uwaga: skompresuj K,V do rangi-`r` ukrytej, przechowuj utajone w pamięci podręcznej KV, dekompresuj w momencie uwagi. Przy jakim `r` pamięć podręczna przekracza 1/8 pełnego MHA, podczas gdy jakość pozostaje w granicach 1 bitu ppl sprawdzania poprawności?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Głowa | „Pojedynczy obwód uwagi” | Jedna projekcja Q/K/V wymiaru `d_head = d_model / n_heads` z własną macierzą uwagi. |
| d_głowa | „Wymiar głowy” | Ukryta szerokość na głowę; prawie zawsze w produkcji 64 lub 128. |
| Podziel / połącz | „Sztuczki przekształcania” | `(N, d_model) ↔ (n_heads, N, d_head)` zmiana kształtu i transpozycja wokół uwagi. |
| W_o | „Projekcja wyników” | `(d_model, d_model)` macierz stosowana po połączeniu głów; gdzie głowy się mieszają. |
| MQA | „Jedna głowa KV” | Uwaga dotycząca wielu zapytań: pojedyncza wspólna projekcja K/V. Najmniejsza pamięć podręczna KV, pewna utrata jakości. |
| GQA | „Domyślne ustawienie od Lamy 2” | Uwaga na zapytanie grupowe z `n_kv_heads < n_heads`; powtarza się, aby dopasować Q. |
| MLA | „Sztuczka DeepSeeka” | Uwaga utajona wielogłowicowa: K, V skompresowane do utajonego niskiego rzędu, dekompresowane w czasie obecności. |
| Głowica indukcyjna | „Obwód uczenia się w kontekście” | Para głów, które wykrywają poprzednie zdarzenia i kopiują to, co nastąpiło po nich. |

## Dalsze czytanie

- [Vaswani i in. (2017). Uwaga to wszystko, czego potrzebujesz §3.2.2](https://arxiv.org/abs/1706.03762) — oryginalna specyfikacja wielogłowicowa.
- [Shazeer (2019). Szybkie dekodowanie transformatora: wystarczy jedna głowica zapisująca](https://arxiv.org/abs/1911.02150) — artykuł MQA.
- [Ainslie i in. (2023). GQA: Trenowanie uogólnionych modeli transformatorów z wieloma zapytaniami z punktów kontrolnych z wieloma głowicami](https://arxiv.org/abs/2305.13245) — jak po szkoleniu przekonwertować MHA na GQA.
- [DeepSeek-AI (2024). Raport techniczny DeepSeek-V2](https://arxiv.org/abs/2405.04434) — MLA i dlaczego przewyższa MHA/GQA w pamięci podręcznej.
- [Olsson i in. (2022). Uczenie się kontekstowe i głowy wprowadzające](https://transformer-circuits.pub/2022/in-context-learning-and-induction-heads/index.html) — mechanistyczne spojrzenie na to, co faktycznie robią głowy.