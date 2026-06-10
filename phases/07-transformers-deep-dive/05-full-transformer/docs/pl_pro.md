# Pełny transformator — koder + dekoder

> Uwaga jest gwiazdą. Wszystko pozostałe — resztkowe połączenia, normalizacja, projekcje, uwaga krzyżowa — to rusztowanie, które pozwala układać je w głąb.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 7 · 02 (Samouważność), Faza 7 · 03 (Uwaga wielu głów), Faza 7 · 04 (kodowanie pozycyjne)
**Czas:** ~75 minut

## Problem

Pojedyncza warstwa uwagi to ekstraktor cech, nie pełnoprawny model. Jeden iloczyn macierzowy na warstwę jest niewystarczający dla przetwarzania języka. Bez odpowiedniej infrastruktury głębokość sieci prowadzi do problemów z gradientem.

W artykule Vaswanego z 2017 roku opisano sześć decyzji projektowych, które przekształciły jedną warstwę uwagi w blok nadający się do wielokrotnego układania w stos. Od tamtej pory każdy transformator — tylko koder (BERT), tylko dekoder (GPT), koder-dekoder (T5) — dziedziczy ten sam szkielet. W 2026 roku bloki zostały udoskonalone (RMSNorm, SwiGLU, pre-norm, RoPE), lecz fundamentalna struktura pozostaje niezmieniona.

Niniejsza lekcja dotyczy właśnie tego szkieletu. Kolejne lekcje skupiają się na jego wariantach — 06 dla koderów, 07 dla dekoderów, 08 dla koderów-dekoderów.

## Koncepcja

![Wewnętrzne elementy bloku kodera i dekodera, okablowane](../assets/full-transformer.svg)

### Sześć składników

1. **Osadzanie + sygnał pozycyjny.** Żetony są przekształcane w wektory. Informacja o pozycji jest wstrzykiwana przez RoPE (wariant nowoczesny) lub funkcje sinusoidalne (wariant klasyczny).
2. **Samouważność.** Każda pozycja jest powiązana z każdą inną. W dekoderach stosowane jest maskowanie.
3. **Sieć ze sprzężeniem zwrotnym (FFN).** Dwuwarstwowy MLP aplikowany pozycyjnie: `W_2 · activation(W_1 · x)`. Domyślny współczynnik rozszerzenia wynosi 4×.
4. **Połączenie resztkowe.** `x + sublayer(x)`. Bez niego gradienty zanikają powyżej ok. 6 warstw.
5. **Normalizacja warstwy.** `LayerNorm` lub `RMSNorm` (wariant nowoczesny). Stabilizuje przepływ przez strumień resztkowy.
6. **Uwaga krzyżowa (tylko w dekoderze).** Zapytania pochodzą z dekodera, natomiast klucze i wartości — z wyjścia kodera.

### Blok enkodera (stosowany w BERT, enkoderze T5)

```
x → LN → MHA(self) → + → LN → FFN → + → out
                     ^              ^
                     |              |
                     └── residual ──┘
```

Enkoder jest dwukierunkowy. Nie stosuje maskowania — wszystkie pozycje mają dostęp do wszystkich pozostałych.

### Blok dekodera (stosowany w dekoderze GPT, T5)

```
x → LN → MHA(masked self) → + → LN → MHA(cross to encoder) → + → LN → FFN → + → out
```

Blok dekodera zawiera trzy podwarstwy. Środkowa — uwaga krzyżowa — to jedyne miejsce, w którym informacja przepływa z kodera do dekodera. W architekturach wyłącznie dekoderowych (jak GPT) uwaga krzyżowa jest pomijana i struktura sprowadza się do zamaskowanej samouważności oraz FFN.

### Pre-norm i post-norm

Oryginalna publikacja stosowała schemat `x + sublayer(LN(x))`, natomiast alternatywą jest `LN(x + sublayer(x))`. Post-norm wyszedł z użycia około 2019 roku — głębokie sieci są trudniejsze do wytrenowania bez starannego harmonogramu rozgrzewki. Pre-norm (czyli `LN` *przed* podwarstwą) jest standardem w 2026 roku — korzystają z niego Llama, Qwen, GPT-3+ oraz Mistral.

### Zmodernizowany blok z 2026 roku

Vaswani 2017 zaproponował LayerNorm i ReLU. Współczesne architektury zastąpiły oba komponenty. Zestawienie bloków produkcyjnych:

| Składnik | 2017 | 2026 |
|----------|------|------|
| Normalizacja | LayerNorm | RMSNorm |
| Aktywacja FFN | ReLU | SwiGLU |
| Ekspansja FFN | 4× | 2,6× (SwiGLU używa trzech macierzy, co wyrównuje całkowitą liczbę parametrów) |
| Kodowanie pozycji | Absolutne sinusoidalne | RoPE |
| Uwaga | Pełne MHA | GQA (lub MLA) |
| Wyrazy wolne | Tak | Nie |

RMSNorm rezygnuje z centrowania przez średnią obecnego w LayerNorm (jedno odejmowanie mniej), co redukuje koszty obliczeniowe, a empirycznie zapewnia porównywalną stabilność. SwiGLU (`Swish(W1 x) ⊙ W3 x`) konsekwentnie przewyższa FFN z ReLU lub GELU o ok. 0,5 punktu perpleksji — co potwierdzają wyniki prac opisujących Llamę, PaLM i Qwen.

### Liczba parametrów

Dla jednego bloku z `d_model = d` i współczynnikiem ekspansji FFN `r`:

- MHA: `4 · d²` (projekcje Q, K, V, O)
- FFN (SwiGLU): `3 · d · (r · d)` ≈ `3rd²`
- Normy: pomijalnie małe

Przy `d = 4096, r = 2.6, layers = 32` (w przybliżeniu Llama 3 8B) łączna liczba wynosi: `32 · (4·4096² + 3·2.6·4096²) ≈ 32 · (16 + 32) M = ~1.5B parameters per layer × 32 ≈ 7B` (plus osadzenia i głowica wyjściowa). Wynik zgadza się z opublikowanymi danymi.

## Implementacja

### Krok 1: Elementy składowe

Korzystamy z klasy `Matrix` z lekcji 03 (skopiowanej do tego pliku dla zachowania niezależności):

- `layer_norm(x, eps=1e-5)` — odejmij średnią, podziel przez odchylenie standardowe.
- `rms_norm(x, eps=1e-6)` — podziel przez RMS. Bez odejmowania średniej.
- `gelu(x)` i `silu(x) * W3 x` (SwiGLU).
- `ffn_swiglu(x, W1, W2, W3)`.
- `encoder_block(x, params)` i `decoder_block(x, enc_out, params)`.

Pełna implementacja dostępna jest w `code/main.py`.

### Krok 2: Złożenie 2-warstwowego kodera i 2-warstwowego dekodera

Ułóż bloki w stos. Przekaż wyjście kodera do mechanizmu uwagi każdego bloku dekodera. Przed projekcją wyjściową dodaj końcową normalizację LN.

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

### Krok 3: Przejście w przód na przykładzie testowym

Przetworz sekwencję wejściową złożoną z 6 żetonów i sekwencję docelową z 5 żetonami. Sprawdź, czy kształt wyjścia wynosi `(5, vocab)`. Etap uczenia jest tu pominięty — lekcja skupia się na architekturze, nie na funkcji straty.

### Krok 4: Zamiana na RMSNorm + SwiGLU

Zastąp LayerNorm i FFN oparty na ReLU odpowiednio przez RMSNorm i SwiGLU. Upewnij się, że wymiary tensorów nadal się zgadzają. To modernizacja do standardu 2026 sprowadzająca się do zamiany jednej funkcji.

## Zastosowanie w praktyce

Implementacje referencyjne PyTorch/TF: `nn.TransformerEncoderLayer`, `nn.TransformerDecoderLayer`. Jednak większość kodu produkcyjnego w 2026 roku korzysta z własnych bloków, ponieważ:

- Flash Attention jest wywoływana bezpośrednio, z pominięciem `nn.MultiheadAttention`.
- GQA/MLA nie są dostępne w standardowej bibliotece.
- RoPE, RMSNorm i SwiGLU nie są domyślnymi komponentami PyTorch.

W bibliotece HuggingFace `transformers` znajdują się czytelne bloki referencyjne warte przestudiowania: `modeling_llama.py` to kanoniczna implementacja bloku wyłącznie dekoderowego w standardzie 2026. Plik liczy ok. 500 linii i zdecydowanie warto go raz przejrzeć.

**Koder vs dekoder vs koder-dekoder — kiedy który wybrać:**

| Potrzebuję | Wybierz | Przykład |
|------|------|--------|
| Klasyfikacja, osadzanie, ocena jakości tekstu | Tylko koder | BERT, DeBERTa, ModernBERT |
| Generowanie tekstu, czat, kod, wnioskowanie | Tylko dekoder | GPT, Llama, Claude, Qwen |
| Ustrukturyzowane wejście → ustrukturyzowane wyjście (tłumaczenie, streszczanie) | Koder-dekoder | T5, BART, Whisper |

Architektura tylko-dekoderowa dominuje w zastosowaniach językowych, ponieważ skaluje się najefektywniej i obsługuje zarówno rozumienie, jak i generowanie tekstu. Koder-dekoder pozostaje najlepszym wyborem wtedy, gdy dane wejściowe mają wyraźny charakter „sekwencji źródłowej" — w tłumaczeniu maszynowym, rozpoznawaniu mowy czy zadaniach strukturalnych.

## Weryfikacja

Zapoznaj się z `outputs/skill-transformer-block-reviewer.md`. Narzędzie sprawdza nową implementację bloku transformatora pod kątem standardów z 2026 roku i wskazuje brakujące elementy (pre-norm, RoPE, RMSNorm, GQA, współczynnik ekspansji FFN).

## Ćwiczenia

1. **Łatwe.** Oblicz liczbę parametrów w bloku encoder_block dla `d_model=512, n_heads=8, ffn_expansion=4, swiglu=True`. Zweryfikuj wynik, implementując blok i stosując `sum(p.numel() for p in block.parameters())`.
2. **Średnie.** Przełącz z post-norm na pre-norm. Zainicjalizuj oba warianty i zmierz normę aktywacji po 12 nałożonych warstwach na losowym wejściu. Aktywacje w wariancie post-norm powinny rosnąć wykładniczo, a w wariancie pre-norm — pozostawać ograniczone.
3. **Trudne.** Zaimplementuj 4-warstwowy koder-dekoder dla zadania kopiowania z odwróceniem sekwencji (kopiuj `x` w odwrotnej kolejności). Trenuj przez 100 kroków i zaraportuj wartość straty. Następnie zamień na RMSNorm + SwiGLU + RoPE — czy strata maleje szybciej?

## Słownik pojęć

| Termin | Potoczne określenie | Właściwe znaczenie |
|------|-----------------|----------------------|
| Blok | „Jedna warstwa transformatora" | Zestaw: norma + uwaga + norma + FFN, opakowany połączeniami resztkowymi. |
| Połączenie resztkowe | „Pomiń połączenie" | `x + f(x)` — umożliwia przepływ gradientu przez głębokie sieci. |
| Pre-norm | „Normalizuj przed, nie po" | Nowoczesny schemat: `x + sublayer(LN(x))`. Umożliwia trenowanie głębszych sieci bez skomplikowanego harmonogramu rozgrzewki. |
| RMSNorm | „LayerNorm bez średniej" | Dzielenie przez RMS; jedna operacja mniej, porównywalna stabilność empiryczna. |
| SwiGLU | „FFN, który wszyscy przyjęli" | `Swish(W1 x) ⊙ W3 x → W2`. Przewyższa ReLU/GELU pod względem perpleksji modeli językowych. |
| Uwaga krzyżowa | „Jak dekoder czyta koder" | MHA z Q z dekodera i K/V z wyjść kodera. |
| Ekspansja FFN | „Szerokość środkowego MLP" | Stosunek rozmiaru warstwy ukrytej do d_model — zazwyczaj 4 (LayerNorm) lub 2,6 (SwiGLU). |
| Brak wyrazów wolnych | „Rezygnacja z +b" | Współczesne architektury usuwają wyrazy wolne z warstw liniowych — nieznaczna poprawa perpleksji przy mniejszej liczbie parametrów. |

## Literatura uzupełniająca

- [Vaswani i in. (2017). Attention Is All You Need](https://arxiv.org/abs/1706.03762) — oryginalna specyfikacja bloku.
- [Xiong i in. (2020). On Layer Normalization in the Transformer Architecture](https://arxiv.org/abs/2002.04745) — dlaczego pre-norm przewyższa post-norm.
- [Zhang, Sennrich (2019). Root Mean Square Layer Normalization](https://arxiv.org/abs/1910.07467) — RMSNorm.
- [Shazeer (2020). GLU Variants Improve Transformer](https://arxiv.org/abs/2002.05202) — artykuł o SwiGLU.
- [HuggingFace `modeling_llama.py`](https://github.com/huggingface/transformers/blob/main/src/transformers/models/llama/modeling_llama.py) — kanoniczna implementacja bloku wyłącznie dekoderowego w standardzie 2026.
