# Pełny transformator — koder + dekoder

> Uwaga jest gwiazdą. Wszystko inne – pozostałości, normalizacja, wyprzedzanie, uwaga krzyżowa – to rusztowanie, które pozwala ułożyć je głęboko.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 7 · 02 (Samouważność), Faza 7 · 03 (Uwaga wielu głów), Faza 7 · 04 (kodowanie pozycyjne)
**Czas:** ~75 minut

## Problem

Pojedyncza warstwa uwagi to ekstraktor cech, a nie model. Jeden matmul na warstwę to za mało dla języka. Potrzebujesz głębi i przerw w głębokości bez odpowiedniej instalacji wodno-kanalizacyjnej.

W artykule Vaswani z 2017 r. zawarto sześć decyzji projektowych, które zamieniły jedną warstwę uwagi w blok, który można układać jeden na drugim. Od tego czasu każdy transformator – tylko koder (BERT), tylko dekoder (GPT), koder-dekoder (T5) – dziedziczy ten sam szkielet. W 2026 roku bloki zostały udoskonalone (RMSNorm, SwiGLU, pre-norm, RoPE), ale szkielet jest identyczny.

Ta lekcja to szkielet. Kolejne lekcje specjalizują się w tym — 06 dla koderów, 07 dla dekoderów, 08 dla koderów-dekoderów.

## Koncepcja

![Wewnętrzne elementy bloku kodera i dekodera, okablowane](../assets/full-transformer.svg)

### Sześć kawałków

1. **Osadzanie + sygnał pozycyjny.** Żetony → wektory. Pozycja wtryskiwana przez RoPE (nowoczesny) lub sinusoidalny (klasyczny).
2. **Samouważność.** Każde stanowisko wiąże się z każdym innym. Zamaskowane w dekoderach.
3. **Sieć ze sprzężeniem zwrotnym (FFN).** Dwuwarstwowy MLP pozycyjny: `W_2 · activation(W_1 · x)`. Domyślny współczynnik rozszerzenia 4×.
4. **Pozostałe połączenie.** `x + sublayer(x)`. Bez tego gradienty znikają powyżej ~ 6 warstw.
5. **Normalizacja warstw.** `LayerNorm` lub `RMSNorm` (nowoczesne). Stabilizuje strumień resztkowy.
6. **Wspólna uwaga (tylko dekoder).** Zapytania pochodzą z dekodera, klucze i wartości z wyjścia kodera.

### Blok enkodera (używany przez BERT, enkoder T5)

```
x → LN → MHA(self) → + → LN → FFN → + → out
                     ^              ^
                     |              |
                     └── residual ──┘
```

Enkoder jest dwukierunkowy. Żadnego maskowania. Wszystkie pozycje wyświetlają wszystkie pozycje.

### Blok dekodera (używany przez dekoder GPT, T5)

```
x → LN → MHA(masked self) → + → LN → MHA(cross to encoder) → + → LN → FFN → + → out
```

Dekoder ma trzy podwarstwy na blok. Środkowy – uwaga krzyżowa – to jedyne miejsce, w którym informacja przepływa od kodera do dekodera. W architekturze wyłącznie dekoderowej (GPT) uwaga krzyżowa jest pomijana i masz po prostu zamaskowaną samouważność + FFN.

### Przed-normą i post-normą

Papier oryginalny: `x + sublayer(LN(x))` vs `LN(x + sublayer(x))`. Post-norma straciła popularność około 2019 roku — trudniej jest głęboko trenować bez starannej rozgrzewki. Norma wstępna (`LN` *przed* podwarstwą) to domyślna norma na rok 2026: wszystkie z niej korzystają Lama, Qwen, GPT-3+ i Mistral.

### Blok zmodernizowany w 2026 roku

Vaswani 2017 dostarczył LayerNorm + ReLU. Nowoczesne stosy zastąpiły oba. Jak faktycznie wyglądają bloki produkcyjne:

| Składnik | 2017 | 2026 |
|----------|------|------|
| Normalizacja | Norma warstwy | Norma RMS |
| Aktywacja FFN | ReLU | SwiGLU |
| Ekspansja FFN | 4× | 2,6× (SwiGLU wykorzystuje trzy macierze, całkowite dopasowanie parametrów) |
| Pozycja | Absolut sinusoidalny | LINA |
| Uwaga | Pełne MHA | GQA (lub MLA) |
| Warunki stronniczości | Tak | Nie |

RMSNorm usuwa średnie centrowanie LayerNorm (o jedno odejmowanie mniej), co oszczędza obliczenia i jest empirycznie co najmniej tak samo stabilne. SwiGLU (`Swish(W1 x) ⊙ W3 x`) konsekwentnie przewyższa ReLU/GELU FFN o ~0,5 punktu na osobę w dokumentach Llama, PaLM i Qwen.

### Liczba parametrów

Dla jednego bloku z `d_model = d` i rozwinięciem FFN `r`:

- MHA: `4 · d²` (projekcje Q, K, V, O)
- FFN (SwiGLU): `3 · d · (r · d)` ≈ `3rd²`
- Normy: znikome

W `d = 4096, r = 2.6, layers = 32` (mniej więcej Lama 3 8B) łącznie: `32 · (4·4096² + 3·2.6·4096²) ≈ 32 · (16 + 32) M = ~1.5B parameters per layer × 32 ≈ 7B` (plus osady i nagłówek). Liczba opublikowanych meczów.

## Zbuduj to

### Krok 1: klocki

Używanie małej klasy `Matrix` z lekcji 03 (skopiowanej do tego pliku dla zachowania niezależności):

- `layer_norm(x, eps=1e-5)` — odejmij średnią, podziel przez std.
- `rms_norm(x, eps=1e-6)` — podziel przez RMS. Bez średniego odejmowania.
- `gelu(x)` i `silu(x) * W3 x` (SwiGLU).
- `ffn_swiglu(x, W1, W2, W3)`.
- `encoder_block(x, params)` i `decoder_block(x, enc_out, params)`.

Pełne okablowanie znajdziesz w `code/main.py`.

### Krok 2: podłącz 2-warstwowy koder i 2-warstwowy dekoder

Ułóż je w stos. Przekaż sygnał wyjściowy kodera do uwagi każdego dekodera. Dodaj końcowy LN przed projekcją wyjściową.

```python
def encode(tokens, params):
    x = embed(tokens, params.emb) + sinusoidal(len(tokens), params.d)
    for block in params.encoder_blocks:
        x = encoder_block(x, block)
    return x

def decode(target_tokens, encoder_out, params):
    x = embed(target_tokens, params.emb) + sinusoidal(len(target_tokens), params.d)
    for block in params.decoder_blocks:
        x = decoder_block(x, encoder_out, block)
    return x
```

### Krok 3: biegnij do przodu na przykładzie zabawki

Przeprowadź źródło z 6 żetonami i cel z 5 żetonami. Sprawdź, czy kształt wyjściowy to `(5, vocab)`. Bez szkolenia — ta lekcja dotyczy architektury, a nie strat.

### Krok 4: zamień RMSNorm + SwiGLU

Zamień LayerNorm i ReLU-FFN na RMSNorm i SwiGLU. Potwierdź, że kształty nadal pasują. Jest to modernizacja 2026 z substytucją jednej funkcji.

## Użyj tego

Implementacje referencyjne PyTorch/TF: `nn.TransformerEncoderLayer`, `nn.TransformerDecoderLayer`. Jednak większość kodu produkcyjnego na rok 2026 generuje własny blok, ponieważ:

- Uwaga błyskawiczna nazywana jest uwagą wewnętrzną, a nie poprzez `nn.MultiheadAttention`.
- GQA/MLA nie znajdują się w odwołaniu do stdlib.
- RoPE, RMSNorm, SwiGLU nie są domyślnymi ustawieniami PyTorch.

HF `transformers` zawiera czyste bloki referencyjne, które powinieneś przeczytać: `modeling_llama.py` to kanoniczny blok przeznaczony tylko do dekodera 2026. To ~ 500 linii i warto je raz przejść.

**Koder vs dekoder vs koder-dekoder – kiedy wybrać:**

| Potrzebuję | Wybierz | Przykład |
|------|------|--------|
| Klasyfikacja, osadzanie, kontrola jakości tekstu | Tylko koder | BERT, DeBERTa, ModernBERT |
| Generowanie tekstu, czat, kod, rozumowanie | Tylko dekoder | GPT, Lama, Claude, Qwen |
| Ustrukturyzowane wejście → ustrukturyzowane wyjście (tłumaczenie, podsumowanie) | Koder-dekoder | T5, BART, Szept |

Język przeznaczony wyłącznie dla dekodera, ponieważ skaluje się najczyściej i obsługuje zarówno zrozumienie, jak i generowanie. Koder-dekoder jest nadal najlepszy, gdy dane wejściowe mają wyraźną tożsamość „sekwencji źródłowej” (tłumaczenie, rozpoznawanie mowy, zadania strukturalne).

## Wyślij to

Zobacz `outputs/skill-transformer-block-reviewer.md`. Umiejętność sprawdza nową implementację bloku transformatora pod kątem wartości domyślnych z 2026 r. i oznacza brakujące elementy (wstępna norma, RoPE, RMSNorm, GQA, współczynnik rozszerzalności FFN).

## Ćwiczenia

1. **Łatwo.** Policz parametry w bloku encoder_block w `d_model=512, n_heads=8, ffn_expansion=4, swiglu=True`. Sprawdź poprawność, implementując blok i używając `sum(p.numel() for p in block.parameters())`.
2. **Średni.** Przełącz z post-normy na pre-normę. Zainicjuj oba i zmierz normę aktywacji po 12 nałożonych na siebie warstwach na losowym wejściu. Aktywacje post-normy powinny eksplodować; normy wstępne powinny pozostać ograniczone.
3. **Trudne.** Zaimplementuj 4-warstwowy koder-dekoder w zadaniu kopiowania zabawki (kopiuj `x` w odwrotnej kolejności). Trenuj 100 kroków. Zgłoś stratę. Zamień na RMSNorm + SwiGLU + RoPE – czy strata spada?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Blok | „Jedna warstwa transformatora” | Stos normy + uwaga + norma + FFN, owinięty resztkowymi połączeniami. |
| Pozostałość | „Pomiń połączenie” | `x + f(x)` dane wyjściowe; umożliwia gradientowy przepływ przez głębokie stosy. |
| Wstępna norma | „Normalizuj przed, nie po” | Nowoczesne: `x + sublayer(LN(x))`. Trenuj głębiej bez gimnastyki rozgrzewkowej. |
| Norma RMS | „LayerNorm bez średniej” | Podziel przez RMS; o jedną operację mniej, ta sama stabilność empiryczna. |
| SwiGLU | „FFN, na który wszyscy przeszli” | `Swish(W1 x) ⊙ W3 x → W2`. Pokonuje ReLU/GELU na LM ppl. |
| Uwaga krzyżowa | „Jak dekoder widzi koder” | MHA z Q z dekodera, K/V z wyjść kodera. |
| Ekspansja FFN | „Jak szeroki jest środkowy MLP” | Stosunek rozmiaru ukrytego do d_model, zwykle 4 (LayerNorm) lub 2,6 (SwiGLU). |
| Bezstronny | „Porzuć warunki +b” | Nowoczesne stosy eliminują odchylenia w warstwach liniowych; niewielka poprawa ppl, mniejszy model. |

## Dalsze czytanie

- [Vaswani i in. (2017). Uwaga to wszystko, czego potrzebujesz](https://arxiv.org/abs/1706.03762) — oryginalna specyfikacja bloku.
- [Xiong i in. (2020). O normalizacji warstw w architekturze transformatora] (https://arxiv.org/abs/2002.04745) — dlaczego stan przednormowy przewyższa postnormę.
- [Zhang, Sennrich (2019). Średnia kwadratowa normalizacja warstwy](https://arxiv.org/abs/1910.07467) — RMSNorm.
- [Shazeer (2020). Warianty GLU ulepszają transformator](https://arxiv.org/abs/2002.05202) — artykuł SwiGLU.
- [HuggingFace `modeling_llama.py`](https://github.com/huggingface/transformers/blob/main/src/transformers/models/llama/modeling_llama.py) — kanoniczny blok tylko dla dekodera 2026.