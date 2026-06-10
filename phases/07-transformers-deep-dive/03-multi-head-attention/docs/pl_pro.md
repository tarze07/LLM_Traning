# Uwaga wielogłowa

> Jedna głowa uwagi uczy się jednej relacji na raz. Osiem głów uczy się ośmiu. Głowy są niezależne. Weź ich więcej.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 7 · 02 (Samouważność od podstaw)
**Czas:** ~75 minut

## Problem

Pojedyncza głowa samouważności oblicza jedną macierz uwagi. Rejestruje ona jeden rodzaj relacji — zwykle taki, który minimalizuje straty bez względu na pozostałe sygnały treningowe. Gdy dane zawierają jednocześnie zgodność podmiot-orzeczenie, koreferencję, relacje dyskursu dalekiego zasięgu i fragmenty syntaktyczne, pojedyncza głowa rozmywa je w jeden rozkład z miękkim maksimum i traci znaczną część informacji.

Rozwiązanie zaproponowane przez Vasvaniego w 2017 r.: uruchom równolegle kilka funkcji uwagi, każdą z własnymi projekcjami Q, K, V, a następnie połącz wyniki. Każda głowa działa we własnej podprzestrzeni o wymiarze `d_model / n_heads`. Łączna liczba parametrów pozostaje taka sama, a siła ekspresji rośnie.

Uwaga wielogłowa jest domyślnym mechanizmem w każdym transformerze w roku 2026. Jedyna otwarta kwestia dotyczy *liczby* głów oraz tego, czy klucze i wartości mają wspólne projekcje (Grouped-Query Attention, Multi-Query Attention, Multi-head Latent Attention).

## Koncepcja

![Uwaga wielogłowa: podział, przetwarzanie, łączenie](../assets/multi-head-attention.svg)

**Podziel.** Weź `X` o kształcie `(N, d_model)`. Wyznacz projekcje Q, K, V — każda o kształcie `(N, d_model)`. Zmień kształt na `(N, n_heads, d_head)`, gdzie `d_head = d_model / n_heads`. Transponuj do `(n_heads, N, d_head)`.

**Przetwarzaj równolegle.** Przeprowadź skalowaną uwagę iloczynu skalarnego w każdej głowie. Każda głowa zwraca tensor o kształcie `(N, d_head)`. Głowy działają w odrębnych podprzestrzeniach i nie komunikują się ze sobą podczas obliczania uwagi.

**Połącz i przeprojektuj.** Skumuluj wyniki z powrotem do kształtu `(N, d_model)` i pomnóż przez wyuczoną macierz wyjściową `W_o` o kształcie `(d_model, d_model)`. To właśnie w `W_o` następuje mieszanie informacji między głowami.

**Dlaczego to działa.** Każda głowa może się specjalizować, nie konkurując z pozostałymi o budżet reprezentacyjny. Badania sondujące z lat 2019–2024 ujawniły różne role poszczególnych głów: głowy pozycyjne, głowy obsługujące poprzedni token, głowy kopiujące, głowy rozpoznające nazwane podmioty oraz głowy indukcyjne (leżące u podstaw uczenia się w kontekście).

**Przegląd wariantów w 2026 r.:**

| Wariant | Głowy Q | Głowy K/V | Stosowany przez |
|--------|---------|------|---------|
| Wielogłowicowy (MHA) | N | N | GPT-2, BERT, T5 |
| Wiele zapytań (MQA) | N | 1 | PaLM, Falcon |
| Zapytanie grupowe (GQA) | N | G (np. N/8) | Llama 2 70B, Llama 3+, Qwen 2+, Mistral |
| Utajone wielogłowicowe (MLA) | N | skompresowane do niskiej rangi | DeepSeek-V2, V3 |

Współczesnym standardem jest GQA, ponieważ zmniejsza rozmiar pamięci podręcznej KV o współczynnik `N/G` przy niemal niezmienionych wynikach jakościowych. MLA idzie o krok dalej — kompresuje K/V do ukrytej przestrzeni i odtwarza je w czasie obliczeń, co kosztuje więcej operacji zmiennoprzecinkowych, ale znacznie oszczędza pamięć.

## Zbuduj to

### Krok 1: wyodrębnij obsługę głów z pojedynczej uwagi

Weź `SelfAttention` z lekcji 02 i opakuj ją parą operacji split/concat. Pełną implementację w numpy znajdziesz w `code/main.py`. Kluczowa logika wygląda następująco:

```python
def split_heads(X, n_heads):
    n, d = X.shape
    d_head = d // n_heads
    return X.reshape(n, n_heads, d_head).transpose(1, 0, 2)  # (heads, n, d_head)

def combine_heads(H):
    h, n, d_head = H.shape
    return H.transpose(1, 0, 2).reshape(n, h * d_head)
```

Jedna zmiana kształtu i jedna transpozycja — bez pętli. Dokładnie tak samo działa PyTorch w `nn.MultiheadAttention`.

### Krok 2: oblicz skalowaną uwagę iloczynu skalarnego dla każdej głowy

Każda głowa otrzymuje własny fragment Q, K, V. Obliczanie uwagi staje się wsadowym mnożeniem macierzy:

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

Na rzeczywistym sprzęcie `Qh @ Kh.transpose(...)` to jedna operacja `bmm`. GPU widzi pojedyncze wsadowe mnożenie macierzy o kształcie `(heads, N, d_head) × (heads, d_head, N) -> (heads, N, N)`. Dodatkowe głowy nie generują narzutu obliczeniowego.

### Krok 3: wariant Grouped-Query Attention

Zmieniają się wyłącznie projekcje klucza i wartości. Q korzysta z `n_heads` grup; K i V mają `n_kv_heads < n_heads` grup i są powielane w celu dopasowania do Q:

```python
def gqa_project(X, W, n_kv_heads, n_heads):
    kv = split_heads(X @ W, n_kv_heads)       # (kv_heads, n, d_head)
    repeat = n_heads // n_kv_heads
    return np.repeat(kv, repeat, axis=0)      # (n_heads, n, d_head)
```

Oszczędność pamięci wynika z tego, że w pamięci podręcznej KV przechowywanych jest tylko `n_kv_heads` kopii, a nie `n_heads`. Llama 3 70B używa 64 głów zapytań przy 8 głowach KV, co daje ośmiokrotne zmniejszenie pamięci podręcznej.

### Krok 4: zbadaj specjalizację głów

Uruchom MHA na krótkim zdaniu z 4 głowami. Dla każdej głowy wydrukuj macierz uwagi `(N, N)`. Już przy losowej inicjalizacji widać, że poszczególne głowy wybierają odmienne struktury — jest to częściowo efekt sygnału treningowego, częściowo symetria obrotowa w podprzestrzeniach.

## Użyj tego

W PyTorch wystarczy jedna linia:

```python
import torch.nn as nn

mha = nn.MultiheadAttention(embed_dim=512, num_heads=8, batch_first=True)
```

GQA dostępne od PyTorch 2.5+:

```python
from torch.nn.functional import scaled_dot_product_attention

# scaled_dot_product_attention auto-dispatches Flash Attention on CUDA.
# For GQA, pass Q of shape (B, n_heads, N, d_head) and K,V of shape
# (B, n_kv_heads, N, d_head). PyTorch handles the repeat.
out = scaled_dot_product_attention(q, k, v, is_causal=True, enable_gqa=True)
```

**Ile głów?** Praktyczne wskazówki dla modeli produkcyjnych w 2026 r.:

| Rozmiar modelu | d_model | n_heads | d_head |
|------------|--------|---------|-------|
| Mały (~125M) | 768 | 12 | 64 |
| Podstawowy (~350M) | 1024 | 16 | 64 |
| Duży (~1B) | 2048 | 16 | 128 |
| Bardzo duży (~70B) | 8192 | 64 | 128 |

`d_head` niemal zawsze wynosi 64 lub 128. Określa to, ile informacji „widzi" pojedyncza głowa. Zejście poniżej 32 powoduje problemy ze współczynnikiem skalowania `sqrt(d_head)`; przekroczenie 256 niweluje zaś korzyść z posiadania wielu małych, wyspecjalizowanych głów.

## Wyślij to

Zapoznaj się z `outputs/skill-mha-configurator.md`. Umiejętność zaleca liczbę głów zapytań, liczbę głów KV oraz strategię projekcji dla nowego transformera, uwzględniając budżet parametrów, długość sekwencji i wymagania wdrożeniowe.

## Ćwiczenia

1. **Łatwe.** Weź MHA z `code/main.py` i zmieniaj `n_heads` od 1 do 16 przy stałym `d_model=64`. Narysuj wykres straty prostego jednowarstwowego modelu na zadaniu syntetycznego kopiowania. Czy większa liczba głów pomaga, stabilizuje wyniki, czy pogarsza je?
2. **Średnie.** Zaimplementuj MQA (jedna współdzielona głowa KV dla wszystkich głów zapytań). Zmierz, o ile spada łączna liczba parametrów w porównaniu z pełnym MHA. Oblicz zmniejszenie rozmiaru pamięci podręcznej KV podczas wnioskowania dla N=2048.
3. **Trudne.** Zaimplementuj uproszczoną wersję Multi-head Latent Attention: skompresuj K, V do ukrytej reprezentacji rzędu `r`, przechowuj ją w pamięci podręcznej KV, a w momencie obliczania uwagi dekompresuj. Przy jakim `r` rozmiar pamięci podręcznej przekracza 1/8 pełnego MHA, jednocześnie utrzymując jakość w granicach 1 bitu perplexity na zbiorze walidacyjnym?

## Kluczowe terminy

| Termin | Co się mówi | Co to faktycznie oznacza |
|------|-----------------|----------------------|
| Głowa | „Pojedynczy obwód uwagi" | Jedna projekcja Q/K/V o wymiarze `d_head = d_model / n_heads` z własną macierzą uwagi. |
| d_head | „Wymiar głowy" | Szerokość ukryta na głowę; w zastosowaniach produkcyjnych niemal zawsze 64 lub 128. |
| Podziel / połącz | „Przekształcenia kształtu" | Zmiana kształtu i transpozycja `(N, d_model) ↔ (n_heads, N, d_head)` wokół obliczania uwagi. |
| W_o | „Projekcja wyjściowa" | Macierz `(d_model, d_model)` stosowana po połączeniu głów; tu następuje mieszanie informacji między głowami. |
| MQA | „Jedna głowa KV" | Multi-Query Attention: pojedyncza wspólna projekcja K/V. Najmniejsza pamięć podręczna KV, pewna utrata jakości. |
| GQA | „Domyślny standard od Llamy 2" | Grouped-Query Attention z `n_kv_heads < n_heads`; powielana w celu dopasowania do Q. |
| MLA | „Sztuczka DeepSeeka" | Multi-head Latent Attention: K, V skompresowane do ukrytej przestrzeni niskiej rangi, dekompresowane w czasie obliczania uwagi. |
| Głowa indukcyjna | „Obwód uczenia się w kontekście" | Para głów wykrywających wcześniejsze wystąpienia wzorca i kopiujących to, co po nich następowało. |

## Dalsze czytanie

- [Vaswani i in. (2017). Uwaga to wszystko, czego potrzebujesz §3.2.2](https://arxiv.org/abs/1706.03762) — oryginalna specyfikacja uwagi wielogłowej.
- [Shazeer (2019). Szybkie dekodowanie transformera: wystarczy jedna głowa zapisująca](https://arxiv.org/abs/1911.02150) — artykuł opisujący MQA.
- [Ainslie i in. (2023). GQA: Trenowanie uogólnionych modeli transformerów z wieloma zapytaniami na podstawie punktów kontrolnych z wieloma głowami](https://arxiv.org/abs/2305.13245) — metoda konwersji MHA do GQA po treningu.
- [DeepSeek-AI (2024). Raport techniczny DeepSeek-V2](https://arxiv.org/abs/2405.04434) — MLA i jej przewagi nad MHA/GQA pod względem pamięci podręcznej.
- [Olsson i in. (2022). Uczenie się w kontekście i głowy indukcyjne](https://transformer-circuits.pub/2022/in-context-learning-and-induction-heads/index.html) — mechanistyczna analiza rzeczywistych funkcji głów uwagi.
