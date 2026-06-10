# Warianty uwagi — okno przesuwne, rzadkie, różnicowe

> Pełna uwaga to okrąg. Każdy token widzi każdy token, a pamięć płaci cenę. Cztery warianty wyginają kształt koła i odzyskują połowę kosztów.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 7 · 02 (Samouwaga), Faza 7 · 03 (Wiele głowic), Faza 7 · 12 (pamięć podręczna KV / uwaga Flash)
**Czas:** ~60 minut

## Problem

Pełna uwaga kosztuje `O(N²)` pamięć i `O(N²)` obliczenia długości sekwencji. W przypadku Lamy 3 70B z kontekstem 128 tys. oznacza to 16 miliardów wpisów uwagi na warstwę, razy 80 warstw. Flash Attention (lekcja 12) ukrywa pamięć aktywacyjną `O(N²)`, ale nie zmienia kosztu arytmetycznego — każdy token nadal obsługuje każdy inny token.

Trzy klasy wariantów zmieniają topologię samej macierzy uwagi:

1. **Uwaga przesuwanego okna (SWA).** Każdy token dotyczy stałego okna sąsiadów, a nie pełnego prefiksu. Pamięć i obliczenia spadają do `O(N · W)`, gdzie `W` to okno. Gemma 2/3, pierwsze warstwy Mistral 7B, Phi-3-Long.
2. **Rzadka/blokuj uwagę.** Punktowane są tylko wybrane pary `(i, j)`; reszta jest zmuszona do zerowej wagi. Longformer, BigBird, rzadki transformator OpenAI.
3. **Zróżnicowana uwaga.** Oblicz dwie mapy uwagi z oddzielnymi projekcjami Q/K, odejmij jedną od drugiej. Zabija „zasysacz uwagi”, który powoduje utratę wagi w pierwszych kilku żetonach. Transformator DIFF firmy Microsoft (2024).

Te współistnieją. Model graniczny z 2026 r. często je miesza: większość warstw to SWA-1024, co piąta to globalna pełna uwaga, a kilka to głowice różnicowe, które sprzątają pobieranie. Obecnie domyślnym podręcznikiem jest stosunek 5:1 SWA do globalnego współczynnika Gemma 3.

## Koncepcja

### Uwaga na przesuwane okno (SWA)

Każde zapytanie na pozycji `i` dotyczy tylko pozycji w `[i - W, i]` (przyczynowy SWA) lub `[i - W/2, i + W/2]` (dwukierunkowy). Tokeny znajdujące się poza oknem otrzymują `-inf` w macierzy wyników.

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

Dla `N = 8192` i `W = 1024` macierz wyników ma w oczekiwaniu 1024 × 8192 niezerowych wierszy – co oznacza redukcję 8×.

**Pamięć podręczna KV zmniejsza się dzięki SWA.** W każdej warstwie należy przechowywać tylko ostatnie `W` tokeny K i V. W przypadku konfiguracji Gemma-3 (okno 1024, kontekst 128 KB) pamięć podręczna KV spada 128×.

**Koszt jakości.** Transformatory wyłącznie SWA mają problemy z odzyskiwaniem na duże odległości. Poprawka: przeplataj warstwy SWA warstwami pełnej uwagi. Gemma 3 wykorzystuje 5:1 SWA:global. Mistral 7B wykorzystywał stos przyczynowo-SWA, w którym informacja „przepływa do przodu” przez nakładające się okna — każda warstwa rozszerza efektywne pole recepcyjne o `W`, a po warstwach `L` model może obsługiwać tokeny `L × W` z powrotem.

### Uwaga rzadka/blokująca

Wybierz z wyprzedzeniem wzorzec rzadkości `N × N`. Trzy kanoniczne kształty:

- **Lokalny + krokowy (rzadki transformator OpenAI).** Zadbaj o ostatnie `W` tokeny plus każdy `stride`-ty token przed nimi. Przechwytuje zarówno dane lokalne, jak i dalekiego zasięgu przy `O(N · sqrt(N))` obliczeniach.
- **Longformer / BigBird.** Okno lokalne + mały zestaw globalnych tokenów (np. `[CLS]`), które są dostępne dla wszystkich i są dostępne dla wszystkich + losowo rzadkie linki. Kontekst empiryczny 2× w dopasowanej jakości.
- **Native Sparse Attention (DeepSeek, 2025).** Dowiedz się, które bloki `(Q, K)` mają znaczenie; pomiń bloki zerowe na poziomie jądra. Kompatybilny z FlashAttention.

Sparse uwaga to historia inżynierii jądra. Matematyka jest prosta (zamaskuj macierz wyników); wygrana wynika z tego, że nigdy nie ładujesz zerowych wpisów do SRAM. FlashAttention-3 i interfejs API FlexAttention 2026 sprawiają, że niestandardowe wzorce rzadkie są pierwszorzędne w PyTorch.

### Uwaga różnicowa (transformator DIFF, 2024)

Regularna uwaga ma problem z „zanikaniem uwagi”: softmax wymusza sumowanie każdego wiersza do 1, więc tokeny, które nie chcą zajmować się niczym konkretnym, zrzucają wagę na pierwszy token (lub kilka pierwszych). To kradnie pojemność, która powinna zostać przeznaczona na prawdziwą treść.

Uwaga różnicowa rozwiązuje ten problem, obliczając **dwie** mapy uwagi i odejmując:

```
A1 = softmax(Q1 K1^T / √d)
A2 = softmax(Q2 K2^T / √d)
DiffAttn = (A1 - λ · A2) V
```

gdzie `λ` jest wyuczonym skalarem (zwykle 0,5–0,8). A1 rejestruje rzeczywiste wagi treści; A2 chwyta zlew. Odejmowanie anuluje ujście, przenosi wagę do odpowiednich żetonów.

Zgłoszone wyniki (Microsoft 2024): 5–10% mniejsze zakłopotanie, 1,5–2 razy dłuższy efektywny kontekst przy tej samej wytrenowanej długości, ostrzejsze aportowanie igłą w stogu siana.

### Porównanie wariantów

| Wariant | Oblicz | Pamięć podręczna KV | Jakość vs pełna | Zastosowanie produkcyjne |
|--------|---------|---------|--------------------------------|----------------|
| Pełna uwaga | O(N²) | O(N) na warstwę | linia bazowa | domyślna warstwa każdego modelu |
| SWA (okno 1024) | O(N·W) | O(W) na warstwę | -0,1 ppl, dobrze z warstwami globalnymi | Gemma 2/3, Phi-3-Długa |
| Lokalne + rzadkie | O(N·√N) | mieszane | podobny do SWA | Transformator rzadki OpenAI, Longformer |
| BigBird (lokalny + globalny + losowy) | O(N) około | mieszane | pasuje do pełnego kontekstu 2× | wczesny długokontekstowy BERT |
| Natywny rzadki (DeepSeek-V3.2) | O(N · frakcja aktywna) | O(N) | w granicach 0,05 ppl | DeepSeek-V3.2, 2025 |
| Mechanizm różnicowy | O(2·N²) | O(2N) | -5 do -10% ppl | Transformator DIFF, modele z początku 2026 r. |

## Zbuduj to

Zobacz `code/main.py`. Implementujemy komparator maski przyczynowej, który pokazuje obok siebie uwagę pełną, SWA, lokalną + krokową i różnicową w sekwencji zabawek.

### Krok 1: pełna maska przyczynowa (linia bazowa)

```python
def causal_mask(n):
    return [[0.0 if j <= i else float("-inf") for j in range(n)] for i in range(n)]
```

Linia bazowa z lekcji 07. Dolny trójkąt; masa zerowa powyżej przekątnej.

### Krok 2: maska przyczynowa przesuwanego okna

```python
def swa_mask(n, window):
    M = [[float("-inf")] * n for _ in range(n)]
    for i in range(n):
        lo = max(0, i - window + 1)
        for j in range(lo, i + 1):
            M[i][j] = 0.0
    return M
```

Jeden parametr — `window`. Podczas `window >= n` odzyskujesz pełną uwagę przyczynową. W przypadku `window = 1` każdy token dotyczy tylko siebie.

### Krok 3: lokalna + rzadka maska ​​w krokach

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

Gęste okno lokalne plus każdy `stride`-ty token z powrotem na początek sekwencji. Pole recepcyjne rośnie w logicznych krokach z dodatkowymi warstwami.

### Krok 4: zróżnicowanie uwagi

```python
def diff_attention(Q1, K1, Q2, K2, V, lam):
    A1 = softmax_causal(Q1 @ K1.T / sqrt_d)
    A2 = softmax_causal(Q2 @ K2.T / sqrt_d)
    return (A1 - lam * A2) @ V
```

Dwie uwagi, odejmij z wyuczonym współczynnikiem mieszania. W kodzie porównujemy mapę cieplną przyciągania uwagi dla pojedynczego i różnicowego i obserwujemy załamanie się ujścia.

### Krok 5: Rozmiary pamięci podręcznej KV

Wydrukuj rozmiar pamięci podręcznej na warstwę w `N = 131072` dla każdego wariantu. Warianty SWA i rzadkie spadają o 10–100×. Różnica podwójna. Płać świadomie swój rachunek za pamięć.

## Użyj tego

Wzory produkcji 2026:

```python
from transformers import AutoModelForCausalLM
# Gemma 3 mixes SWA (window=1024) and global layers at 5:1.
model = AutoModelForCausalLM.from_pretrained("google/gemma-3-27b-it")
# print(model.config.sliding_window, model.config.layer_types)
```

FlexAttention w PyTorch 2.5+ akceptuje funkcję maski:

```python
from torch.nn.attention.flex_attention import flex_attention, create_block_mask

def swa_pattern(b, h, q_idx, kv_idx):
    return (q_idx - kv_idx < 1024) & (q_idx >= kv_idx)

mask = create_block_mask(swa_pattern, B=batch, H=heads, Q_LEN=n, KV_LEN=n)
out = flex_attention(q, k, v, block_mask=mask)
```

To kompiluje do niestandardowego jądra Triton. W granicach 10% szybkości FlashAttention-3 dla typowych wzorców, a funkcja maski jest wywoływalna w języku Python.

**Kiedy wybrać każdy z nich:**

- **Czysta pełna uwaga** — każda warstwa w kontekście do ~16 tys. lub gdy najważniejsza jest jakość wyszukiwania.
- **SWA + global mix** — długi kontekst (>32 KB), uczenie i wnioskowanie powiązane z pamięcią. Wartość domyślna na rok 2026 przekracza 32 tys.
- **Uwaga na rzadki blok** — niestandardowe jądro, niestandardowy wzór. Zarezerwowane dla specjalistycznych obciążeń (pobieranie, audio).
- **Zróżnicowana uwaga** – każde obciążenie pracą, które powoduje ból pochłaniający uwagę (długi kontekst RAG, igła w stogu siana).

## Wyślij to

Zobacz `outputs/skill-attention-variant-picker.md`. Umiejętność wybiera topologię uwagi dla nowego modelu, biorąc pod uwagę długość kontekstu docelowego, wymagania dotyczące pobierania i profil obliczeniowy uczenia/wnioskowania.

## Ćwiczenia

1. **Łatwe.** Uruchom `code/main.py`. Sprawdź, czy SWA w `window=4` zeruje wszystko poza ostatnimi 4 tokenami w wierszu. Sprawdź, czy `window=n` odtwarza pełną uwagę przyczynową w bitowo identyczny sposób.
2. **Średni.** Zaimplementuj przyczynowe SWA z `window=1024` na szczycie zwieńczenia lekcji 07. Trenuj 1000 kroków na Tinyshakespeare. Jak bardzo zmniejsza się utrata wartości Val w porównaniu z pełną uwagą? Jak bardzo spada pamięć szczytowa?
3. **Trudne.** Zastosuj mieszankę warstw 5:1 w stylu Gemma-3 (5 SWA, 1 globalna) w modelu zwieńczenia. Porównaj straty, pamięć i jakość generacji z czystymi SWA i czysto globalnymi wartościami bazowymi przy dopasowanych parametrach.
4. **Trudne.** Wdrażaj zróżnicowaną uwagę dzięki wyuczonemu `λ` na głowę. Trenuj zadanie odzyskiwania syntetycznego (jedna igła, 2000 dystraktorów). Zmierz dokładność wyszukiwania w porównaniu z wartością bazową pojedynczej uwagi przy dopasowanych parametrach.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Uwaga przesuwanego okna (SWA) | „Lokalna uwaga” | Każde zapytanie dotyczy jego ostatnich tokenów `W`; Pamięć podręczna KV zmniejsza się do `O(W)`. |
| Efektywne pole recepcyjne | „Jak daleko wstecz widzi model” | W `L`-warstwowym stosie SWA z oknem `W` maksymalnie tokenów `L × W`. |
| Longformer / BigBird | „Lokalny + globalny + losowy” | Rzadkie wzorce z kilkoma zawsze obecnymi tokenami globalnymi; wczesne podejście długokontekstowe. |
| Natywna rzadka uwaga | „Sztuczka z jądrem DeepSeeka” | Naucz się rzadkości na poziomie bloku; pomiń zero bloków na poziomie jądra, zachowując jakość. |
| Uwaga różnicowa | „Dwie mapy, jedna odejmuje” | Transformator DIFF: odejmij wyuczoną `λ` razy drugą mapę uwagi od pierwszej, aby anulować pochłanianie uwagi. |
| Uwaga zlew | „Waga spada do tokena 0” | Normalizacja Softmax wymusza sumowanie wierszy do 1; zapytania nieinformacyjne zrzucają wagę na pozycję 0. |
| FlexUwaga | „Maska-jako-Python” | PyTorch 2.5+ API, które kompiluje dowolne funkcje maski w jądra w kształcie FlashAttention. |
| Mieszanka typu warstwowego | „5:1 SWA na skalę globalną” | Przeplataj warstwy rzadkie i pełne uwagi w stosie, aby zachować jakość przy mniejszej pamięci. |

## Dalsze czytanie

- [Beltagy, Peters, Cohan (2020). Longformer: The Long-Document Transformer](https://arxiv.org/abs/2004.05150) — kanoniczne przesuwane okno + dokument z globalnym tokenem.
- [Zaheer i in. (2020). Wielki ptak: Transformatory dla dłuższych sekwencji](https://arxiv.org/abs/2007.14062) — lokalnie + globalnie + losowo.
- [Dziecko i in. (2019). Generowanie długich sekwencji za pomocą rzadkich transformatorów](https://arxiv.org/abs/1904.10509) — lokalny+krokowy wzór OpenAI.
- [Zespół Gemmy (2024). Gemma 2: Udoskonalanie modeli języka otwartego w praktycznym rozmiarze](https://arxiv.org/abs/2408.00118) — globalna mieszanka SWA:globalna 1:1.
- [Zespół Gemmy (2025). Raport techniczny Gemma 3](https://arxiv.org/abs/2503.19786) — mieszanka 5:1 z oknem=1024, która jest teraz domyślną podręcznikową wartością.
- [Ye i in. (2024). Transformator różnicowy](https://arxiv.org/abs/2410.05258) — artykuł dotyczący transformatora DIFF.
- [Yuan i in. (2025). Natywna rzadka uwaga](https://arxiv.org/abs/2502.11089) — wyuczona uwaga rzadka w DeepSeek-V3.2.
- [PyTorch — blog i dokumentacja FlexAttention](https://pytorch.org/blog/flexattention/) — Informacje o interfejsie API dla wzorca maska-as-callable w Use It.