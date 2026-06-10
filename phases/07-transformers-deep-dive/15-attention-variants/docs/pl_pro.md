# Warianty uwagi — okno przesuwne, rzadka, różnicowa

> Pełna uwaga to okrąg. Każdy token widzi każdy inny token, a pamięć płaci za to cenę. Cztery warianty zmieniają kształt tego koła i odzyskują połowę kosztów.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 7 · 02 (Samouwaga), Faza 7 · 03 (Wiele głowic), Faza 7 · 12 (pamięć podręczna KV / Flash Attention)
**Czas:** ~60 minut

## Problem

Pełna uwaga wymaga `O(N²)` pamięci i `O(N²)` obliczeń względem długości sekwencji. W przypadku Llama 3 70B z kontekstem 128 tys. tokenów daje to 16 miliardów wpisów uwagi na warstwę, pomnożone przez 80 warstw. Flash Attention (lekcja 12) ukrywa aktywacyjne zużycie pamięci rzędu `O(N²)`, lecz nie zmienia kosztu arytmetycznego — każdy token nadal obsługuje każdy inny.

Trzy klasy wariantów zmieniają topologię samej macierzy uwagi:

1. **Uwaga z przesuwnym oknem (SWA).** Każdy token odnosi się jedynie do stałego okna sąsiadów, nie do całego prefiksu. Pamięć i obliczenia spadają do `O(N · W)`, gdzie `W` to rozmiar okna. Stosowane w: Gemma 2/3, pierwszych warstwach Mistral 7B, Phi-3-Long.
2. **Rzadka uwaga blokowa.** Oceniane są tylko wybrane pary `(i, j)`; pozostałe otrzymują zerową wagę. Przykłady: Longformer, BigBird, Sparse Transformer OpenAI.
3. **Uwaga różnicowa.** Obliczane są dwie mapy uwagi z oddzielnymi projekcjami Q/K, po czym jedna jest odejmowana od drugiej. Eliminuje problem „pochłaniacza uwagi", który powoduje skupianie wagi na pierwszych kilku tokenach. Zastosowana w: DIFF Transformer firmy Microsoft (2024).

Wszystkie trzy podejścia współistnieją. Modele graniczne z 2026 roku często je łączą: większość warstw to SWA-1024, co piąta to globalna pełna uwaga, a część głowic to głowice różnicowe odpowiedzialne za precyzyjne wyszukiwanie. Aktualnym wzorcem z podręcznika jest proporcja 5:1 (SWA do globalnych), zastosowana w Gemma 3.

## Koncepcja

### Uwaga z przesuwnym oknem (SWA)

Każde zapytanie na pozycji `i` odnosi się tylko do pozycji z przedziału `[i - W, i]` (przyczynowe SWA) lub `[i - W/2, i + W/2]` (dwukierunkowe). Tokeny spoza okna otrzymują wartość `-inf` w macierzy wyników.

```
full causal:           sliding window (W=4):
positions 0-7          positions 0-7, W=4
    0 1 2 3 4 5 6 7        0 1 2 3 4 5 6 7
0 | x                0 |  x
1 | x x              1 |  x x
2 | x x x            2 |  x x x
3 | x x x x          3 |  x x x x
4 | x x x x x        4 |    x x x x
5 | x x x x x x      5 |      x x x x
6 | x x x x x x x    6 |        x x x x
7 | x x x x x x x x  7 |          x x x x
```

Dla `N = 8192` i `W = 1024` macierz wyników zawiera oczekiwanie 1024 × 8192 niezerowych wierszy, co oznacza ośmiokrotną redukcję.

**SWA zmniejsza rozmiar pamięci podręcznej KV.** W każdej warstwie wystarczy przechowywać jedynie ostatnie `W` tokenów K i V. Dla konfiguracji Gemma-3 (okno 1024, kontekst 128 KB) pamięć podręczna KV zmniejsza się 128-krotnie.

**Koszt jakościowy.** Transformatory oparte wyłącznie na SWA mają trudności z powiązaniami dalekiego zasięgu. Rozwiązanie: przeplatanie warstw SWA z warstwami pełnej uwagi. Gemma 3 stosuje proporcję 5:1 (SWA do globalnych). Mistral 7B używał stosu przyczynowego SWA, w którym informacja „przepływa naprzód" przez nakładające się okna — każda warstwa rozszerza efektywne pole recepcyjne o `W`, więc po `L` warstwach model może sięgać `L × W` tokenów wstecz.

### Rzadka uwaga blokowa

Wzorzec rzadkości `N × N` jest wyznaczany z wyprzedzeniem. Trzy kanoniczne kształty:

- **Lokalny + krokowy (Sparse Transformer OpenAI).** Uwzględniane są ostatnie `W` tokenów oraz co `stride`-ty token przed nimi. Przechwytuje zarówno dane lokalne, jak i długodystansowe przy koszcie `O(N · √N)`.
- **Longformer / BigBird.** Lokalne okno oraz niewielki zestaw tokenów globalnych (np. `[CLS]`), widocznych dla wszystkich i mających dostęp do wszystkich, uzupełniony rzadkimi losowymi połączeniami. Empirycznie dwukrotnie większy efektywny kontekst przy porównywalnej jakości.
- **Native Sparse Attention (DeepSeek, 2025).** Model uczy się, które bloki `(Q, K)` są istotne, a zerowe bloki są pomijane na poziomie jądra. Kompatybilna z FlashAttention.

Rzadka uwaga to przede wszystkim wyzwanie inżynierii jądra. Matematyka jest prosta — wystarczy zamaskować macierz wyników. Zysk pochodzi z nieprzesyłania zerowych wpisów do SRAM. FlashAttention-3 oraz interfejs API FlexAttention z 2026 roku sprawiają, że niestandardowe wzorce rzadkości są w PyTorch traktowane jako pełnoprawne mechanizmy.

### Uwaga różnicowa (DIFF Transformer, 2024)

Zwykła uwaga cierpi na problem „pochłaniacza uwagi": softmax wymusza, by każdy wiersz sumował się do 1, więc tokeny, które nie chcą skupiać się na żadnym konkretnym elemencie, zrzucają wagę na pierwszy token (lub kilka pierwszych). Marnuje to pojemność, którą powinny zajmować rzeczywiste treści.

Uwaga różnicowa rozwiązuje ten problem, obliczając **dwie** mapy uwagi i odejmując jedną od drugiej:

```
A1 = softmax(Q1 K1^T / √d)
A2 = softmax(Q2 K2^T / √d)
DiffAttn = (A1 - λ · A2) V
```

gdzie `λ` to wyuczony skalar (zwykle 0,5–0,8). Mapa A1 rejestruje rzeczywiste wagi treściowe, A2 wychwytuje pochłaniacz. Odejmowanie znosi efekt pochłaniacza i przenosi wagę na odpowiednie tokeny.

Zgłoszone wyniki (Microsoft 2024): o 5–10% niższa perpleksja, 1,5–2-krotnie większy efektywny kontekst przy tej samej długości trenowania, wyraźniejsze wyniki w zadaniu „igły w stogu siana".

### Porównanie wariantów

| Wariant | Obliczenia | Pamięć podręczna KV | Jakość vs pełna | Zastosowanie produkcyjne |
|--------|---------|---------|--------------------------------|----------------|
| Pełna uwaga | O(N²) | O(N) na warstwę | punkt odniesienia | domyślna warstwa każdego modelu |
| SWA (okno 1024) | O(N·W) | O(W) na warstwę | -0,1 ppl, dobrze z warstwami globalnymi | Gemma 2/3, Phi-3-Long |
| Lokalna + krokowa | O(N·√N) | mieszana | porównywalna z SWA | Sparse Transformer OpenAI, Longformer |
| BigBird (lokalna + globalna + losowa) | O(N) aproks. | mieszana | dorównuje pełnej przy 2× kontekście | wczesny długokontekstowy BERT |
| Natywna rzadka (DeepSeek-V3.2) | O(N · aktywna frakcja) | O(N) | w granicach 0,05 ppl | DeepSeek-V3.2, 2025 |
| Różnicowa | O(2·N²) | O(2N) | -5 do -10% ppl | DIFF Transformer, modele z początku 2026 r. |

## Zbuduj to

Patrz `code/main.py`. Implementujemy komparator masek przyczynowych, który zestawia obok siebie uwagę pełną, SWA, lokalną + krokową i różnicową na krótkiej sekwencji testowej.

### Krok 1: pełna maska przyczynowa (punkt odniesienia)

```python
def causal_mask(n):
    return [[0.0 if j <= i else float("-inf") for j in range(n)] for i in range(n)]
```

Punkt odniesienia z lekcji 07. Dolny trójkąt; wartości zerowe poniżej przekątnej, `-inf` powyżej.

### Krok 2: maska przyczynowa z przesuwnym oknem

```python
def swa_mask(n, window):
    M = [[float("-inf")] * n for _ in range(n)]
    for i in range(n):
        lo = max(0, i - window + 1)
        for j in range(lo, i + 1):
            M[i][j] = 0.0
    return M
```

Jeden parametr — `window`. Gdy `window >= n`, otrzymujemy pełną uwagę przyczynową. Dla `window = 1` każdy token odnosi się tylko do siebie.

### Krok 3: lokalna + krokowa maska rzadka

```python
def strided_mask(n, window, stride):
    M = [[float("-inf")] * n for _ in range(n)]
    for i in range(n):
        lo = max(0, i - window + 1)
        for j in range(lo, i + 1):
            M[i][j] = 0.0
        for j in range(0, i + 1, stride):
            M[i][j] = 0.0
    return M
```

Gęste okno lokalne oraz co `stride`-ty token aż do początku sekwencji. Pole recepcyjne rośnie logarytmicznie wraz z kolejnymi warstwami.

### Krok 4: uwaga różnicowa

```python
def diff_attention(Q1, K1, Q2, K2, V, lam):
    A1 = softmax_causal(Q1 @ K1.T / sqrt_d)
    A2 = softmax_causal(Q2 @ K2.T / sqrt_d)
    return (A1 - lam * A2) @ V
```

Dwie mapy uwagi odejmowane z wyuczonym współczynnikiem mieszania. W kodzie zestawiamy mapy cieplne uwagi dla wariantu pojedynczego i różnicowego, obserwując zanikanie efektu pochłaniacza.

### Krok 5: rozmiary pamięci podręcznej KV

Wydrukuj rozmiar pamięci podręcznej na warstwę dla `N = 131072` w każdym wariancie. Warianty SWA i rzadkie zmniejszają ją 10–100-krotnie. Wariant różnicowy podwaja zużycie. Zarządzaj pamięcią świadomie.

## Użyj tego

Wzorce produkcyjne z 2026 roku:

```python
from transformers import AutoModelForCausalLM
# Gemma 3 mixes SWA (window=1024) and global layers at 5:1.
model = AutoModelForCausalLM.from_pretrained("google/gemma-3-27b-it")
# print(model.config.sliding_window, model.config.layer_types)
```

FlexAttention w PyTorch 2.5+ przyjmuje funkcję maski:

```python
from torch.nn.attention.flex_attention import flex_attention, create_block_mask

def swa_pattern(b, h, q_idx, kv_idx):
    return (q_idx - kv_idx < 1024) & (q_idx >= kv_idx)

mask = create_block_mask(swa_pattern, B=batch, H=heads, Q_LEN=n, KV_LEN=n)
out = flex_attention(q, k, v, block_mask=mask)
```

Kod kompiluje się do niestandardowego jądra Triton. Wydajność mieści się w granicach 10% szybkości FlashAttention-3 dla typowych wzorców, a funkcja maski jest zapisywana w czystym Pythonie.

**Kiedy sięgnąć po każdy wariant:**

- **Czysta pełna uwaga** — wszystkie warstwy w kontekście do ~16 tys. tokenów lub gdy jakość wyszukiwania jest priorytetem.
- **SWA + warstwy globalne** — długi kontekst (>32 KB), gdy pamięć jest ograniczona zarówno podczas trenowania, jak i wnioskowania. Domyślny wybór w 2026 roku dla kontekstów powyżej 32 tys.
- **Rzadka uwaga blokowa** — niestandardowe jądro, niestandardowy wzorzec; zarezerwowana dla wyspecjalizowanych zastosowań (wyszukiwanie, dźwięk).
- **Uwaga różnicowa** — dowolne zastosowanie, w którym problem pochłaniacza uwagi jest dotkliwy (długi kontekst RAG, zadanie „igły w stogu siana").

## Wyślij to

Patrz `outputs/skill-attention-variant-picker.md`. Umiejętność dobiera topologię uwagi dla nowego modelu na podstawie docelowej długości kontekstu, wymagań wyszukiwania oraz profilu obliczeniowego trenowania i wnioskowania.

## Ćwiczenia

1. **Łatwe.** Uruchom `code/main.py`. Sprawdź, czy SWA z `window=4` zeruje wszystko poza ostatnimi czterema tokenami w wierszu. Zweryfikuj, czy `window=n` odtwarza pełną uwagę przyczynową w sposób bitowo identyczny.
2. **Średnie.** Zaimplementuj przyczynowe SWA z `window=1024` na bazie modelu z lekcji 07. Trenuj 1000 kroków na zbiorze Tinyshakespeare. O ile zmniejsza się strata walidacyjna w porównaniu z pełną uwagą? O ile spada szczytowe zużycie pamięci?
3. **Trudne.** Zastosuj mieszankę warstw 5:1 w stylu Gemma-3 (5 SWA, 1 globalna) w modelu z lekcji 07. Porównaj straty, zużycie pamięci i jakość generacji z wariantami czysto SWA i czysto globalnym przy tych samych parametrach.
4. **Trudne.** Zaimplementuj uwagę różnicową z wyuczonym `λ` na głowicę. Trenuj na syntetycznym zadaniu wyszukiwania (jedna igła, 2000 elementów odwracających uwagę). Zmierz dokładność wyszukiwania w odniesieniu do bazowego wariantu z pojedynczą uwagą przy tych samych parametrach.

## Kluczowe terminy

| Termin | Co się mówi | Co to faktycznie oznacza |
|------|-----------------|----------------------|
| Uwaga z przesuwnym oknem (SWA) | „Lokalna uwaga" | Każde zapytanie odnosi się do ostatnich `W` tokenów; pamięć podręczna KV spada do `O(W)`. |
| Efektywne pole recepcyjne | „Jak daleko wstecz widzi model" | W stosie `L` warstw SWA z oknem `W` maksymalnie `L × W` tokenów. |
| Longformer / BigBird | „Lokalna + globalna + losowa" | Wzorce rzadkie z kilkoma stale obecnymi tokenami globalnymi; wczesne podejście do długiego kontekstu. |
| Native Sparse Attention | „Sztuczka jądra DeepSeeka" | Model uczy się rzadkości na poziomie bloków; zerowe bloki są pomijane na poziomie jądra bez utraty jakości. |
| Uwaga różnicowa | „Dwie mapy, jedna odejmowana" | DIFF Transformer: od pierwszej mapy uwagi odejmuje się wyuczoną `λ`-krotność drugiej, neutralizując pochłaniacz uwagi. |
| Pochłaniacz uwagi | „Waga spada na token 0" | Normalizacja softmax wymusza, by wiersze sumowały się do 1; zapytania bez konkretnego celu zrzucają wagę na pozycję 0. |
| FlexAttention | „Maska jako Python" | Interfejs API PyTorch 2.5+, który kompiluje dowolne funkcje maski do jąder w stylu FlashAttention. |
| Mieszanka typów warstw | „5:1 SWA do globalnych" | Przeplatanie warstw rzadkich i pełnej uwagi w stosie — zachowuje jakość przy mniejszym zużyciu pamięci. |

## Dalsze czytanie

- [Beltagy, Peters, Cohan (2020). Longformer: The Long-Document Transformer](https://arxiv.org/abs/2004.05150) — kanoniczny artykuł o przesuwnym oknie z globalnym tokenem dokumentu.
- [Zaheer i in. (2020). Big Bird: Transformers for Longer Sequences](https://arxiv.org/abs/2007.14062) — podejście lokalne + globalne + losowe.
- [Child i in. (2019). Generating Long Sequences with Sparse Transformers](https://arxiv.org/abs/1904.10509) — wzorzec lokalny + krokowy OpenAI.
- [Zespół Gemmy (2024). Gemma 2: Improving Open Language Models at a Practical Size](https://arxiv.org/abs/2408.00118) — mieszanka SWA:globalna 1:1.
- [Zespół Gemmy (2025). Gemma 3 Technical Report](https://arxiv.org/abs/2503.19786) — mieszanka 5:1 z oknem=1024, obecnie wzorcowy standard.
- [Ye i in. (2024). Differential Transformer](https://arxiv.org/abs/2410.05258) — artykuł oryginalny DIFF Transformer.
- [Yuan i in. (2025). Native Sparse Attention](https://arxiv.org/abs/2502.11089) — wyuczona rzadka uwaga w DeepSeek-V3.2.
- [PyTorch — blog i dokumentacja FlexAttention](https://pytorch.org/blog/flexattention/) — opis interfejsu API dla wzorca maska-jako-funkcja w sekcji „Użyj tego".
