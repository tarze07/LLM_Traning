---

name: prompt-gpt-architecture-analyzer
description: Analizuj wybór architektury w dowolnym modelu transformatora typu GPT
version: 1.0.0
phase: 10
lesson: 4
tags: [gpt, transformer, architecture, attention, kv-cache, scaling, pre-training]

---

# Analizator architektury GPT

Oceniając model o architekturze typu GPT na podstawie raportu technicznego, karty modelu (model card) lub logów treningowych, użyj poniższych wytycznych, aby przeanalizować strukturę sieci i zidentyfikować kompromisy projektowe.

## Protokół analizy

### 1. Rozkład alokacji parametrów

Oblicz dokładną liczbę parametrów dla każdego komponentu:

- **Osadzenia tokenów (Token embeddings)**: vocab_size x embed_dim
- **Osadzenia pozycyjne (Position embeddings)**: max_seq_len x embed_dim
- **Atencja na blok**: 4 x embed_dim x embed_dim (macierze Q, K, V oraz projekcja wyjściowa)
- **Warstwa FFN na blok**: 2 x embed_dim x ff_dim + embed_dim + ff_dim (dwie warstwy liniowe + obciążenia/biases)
- **Normalizacja warstwy (LayerNorm) na blok**: 4 x embed_dim (dwie warstwy normalizacji, każda z parametrami skali i przesunięcia)
- **Końcowa normalizacja (Final LayerNorm)**: 2 x embed_dim
- **Głowica wyjściowa (Output head / LM head)**: vocab_size x embed_dim (lub 0, jeśli zastosowano współdzielenie wag z warstwą osadzeń – weight tying)

Zwróć uwagę, jeśli jakikolwiek pojedynczy komponent przekracza 40% całkowitej liczby parametrów. W małych modelach dominuje macierz osadzeń (embedding matrix). W dużych modelach dominują warstwy atencji oraz FFN.

### 2. Analiza mechanizmu atencji

Oceń konfigurację atencji:

- **Wymiar głowy (head dimension)**: `embed_dim / num_heads`. Standardem jest 64 (GPT-2) lub 128 (Llama 3). Wartości poniżej 32 ograniczają zdolność reprezentacji pojedynczej głowy, natomiast powyżej 128 obliczenia stają się nieefektywne przy znikomym przyroście jakości.
- **Liczba głów na warstwę**: Większa liczba głów pozwala na modelowanie bardziej zróżnicowanych zależności, ale zwiększa zużycie pamięci przez KV cache.
- **Grouped Query Attention (GQA)**: Czy model współdzieli głowy kluczy i wartości (K/V) pomiędzy wieloma głowami zapytań (Q)? Na Example Llama 3 wykorzystuje GQA z 8 głowami K/V na 32 głowy Q, co redukuje rozmiar KV cache czterokrotnie.
- **Długość kontekstu**: Maksymalny zakres osadzeń pozycyjnych. Zastosowanie RoPE (Rotary Position Embedding) pozwala na ekstrapolację poza długość sekwencji treningowych, podczas gdy absolutne kodowanie pozycji (absolute positional embeddings) na to nie pozwala.

### 3. Budżet pamięci RAM / VRAM

Aby oszacować wymagania pamięciowe przy maksymalnej długości kontekstu:

- **Wagi modelu (FP16)**: `total_params x 2` bajty
- **KV Cache (FP16)**: `2 x num_layers x num_kv_heads x head_dim x max_seq_len x 2` bajty
- **Aktywacje**: `batch_size x seq_len x embed_dim x 2 x num_layers` bajtów (szacunkowo)

Zwróć uwagę, jeśli rozmiar KV cache przekracza wagę modelu. Zjawisko to występuje w modelach o długim kontekście (np. 128k+ tokenów) i oznacza, że generowanie (dekodowanie) będzie silnie ograniczone przez przepustowość pamięci (memory-bound).

### 4. Profil obliczeniowy

- **Prefill FLOPS na token**: około `2 x total_params` (operacja mnożenia macierzy na parametr w przejściu w przód – forward pass)
- **Decode FLOPS na token**: analogicznie do fazy prefill, ale obliczane dla pojedynczego generowanego tokenu
- **Wąskie gardło fazy prefill**: ograniczenie mocą obliczeniową (compute-bound, np. TFLOPS karty GPU)
- **Wąskie gardło fazy decode**: ograniczenie przepustowością pamięci (memory-bandwidth bound)
- **Intensywność arytmetyczna (arithmetic intensity)**: liczba operacji FLOP na bajt przetransferowanej pamięci. Wartość poniżej 100 oznacza ograniczenie pamięciowe (memory-bound).

### 5. Prawa skalowania (scaling laws)

Oceń pod kątem znanych praw skalowania:

- **Optymalność wg praw Chinchilla**: Przy zadanym budżecie obliczeniowym $C$, optymalny rozmiar modelu $N$ oraz liczba tokenów treningowych $D$ powinny rosnąć proporcjonalnie ($N \approx D$). Model o rozmiarze 7B parametrów potrzebuje ok. 140B (miliardów) tokenów treningowych.
- **Nadmierne trenowanie (overtraining) w Llama 3**: Meta wytrenowała model Llama 3 8B na 15T tokenów (ok. 100-krotność optimum Chinchilla). Trenowanie mniejszych modeli na znacznie większej liczbie danych obniża koszt wnioskowania (inference) na token.
- **Szerokość a głębokość**: Przy stałej liczbie parametrów, modele głębsze (więcej warstw) charakteryzują się zazwyczaj lepszą efektywnością uczenia się na próbkach (sample efficiency) niż modele szersze (większy `embed_dim`).

## Sygnały ostrzegawcze (czerwone flagi)

- **Współczynnik wymiaru FFN inny niż 4x**: Standardowo `ff_dim = 4 x embed_dim`. Rodzina Llama stosuje `8/3 x embed_dim` w połączeniu z aktywacją SwiGLU. Inne odstępstwa wymagają solidnego uzasadnienia.
- **Brak współdzielenia wag (weight tying)**: Głowica wyjściowa (LM Head) powinna współdzielić wagi z warstwą osadzeń tokenów, chyba że rozmiar słownika (`vocab_size`) jest ekstremalnie duży w porównaniu do `embed_dim`.
- **Brak mechanizmu GQA w modelach powyżej 13B**: Architektury przekraczające 13B parametrów bez zastosowania Grouped Query Attention zużywają zbyt dużo zasobów na KV cache.
- **Brak RoPE przy długim kontekście**: Absolutne kodowanie pozycji nie pozwala na ekstrapolację poza długość sekwencji treningowej. Modele obsługujące kontekst 32k+ tokenów powinny stosować kodowanie obrotowe (RoPE).
- **Zbyt wysoki współczynnik uczenia się (learning rate) dla dużych modeli**: Większe modele wymagają znacznie mniejszej maksymalnej wartości współczynnika uczenia. Np. GPT-2 Small używa $6 \cdot 10^{-4}$, podczas gdy Llama 3 405B stosuje $8 \cdot 10^{-5}$.

## Format wyjściowy

1. **Tabela parametrów**: zestawienie liczby parametrów dla poszczególnych komponentów wraz z udziałem procentowym.
2. **Budżet pamięci**: zapotrzebowanie pamięciowe na wagi modelu, KV cache oraz aktywacje przy maksymalnej długości kontekstu.
3. **Profil obliczeniowy**: szacunki wydajności dla fazy prefill i dekodowania na kartach A100/H100.
4. **Ocena architektury**: analiza zalet i nietypowych decyzji projektowych.
5. **Ocena skalowania**: weryfikacja, czy model został odpowiednio wytrenowany (proporcja parametrów do liczby tokenów).
