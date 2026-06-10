---

name: prompt-gpt-architecture-analyzer
description: Analizuj wybór architektury w dowolnym modelu transformatora typu GPT
version: 1.0.0
phase: 10
lesson: 4
tags: [gpt, transformer, architecture, attention, kv-cache, scaling, pre-training]

---

# Analizator architektury GPT

Oceniając model w stylu GPT na podstawie raportu technicznego, karty modelu lub dziennika szkoleniowego, użyj tego frameworka, aby rozbić architekturę i zidentyfikować kompromisy projektowe.

## Protokół analizy

### 1. Podział alokacji parametrów

Oblicz dokładną liczbę parametrów dla każdego komponentu:

- **Osadzanie tokenów**: vocab_size x embed_dim
- **Umiejscowienie osadzania**: max_seq_len x embed_dim
- **Uwaga na blok**: 4 x embed_dim x embed_dim (Q, K, V, projekcje wyjściowe)
- **Na blok FFN**: 2 x embed_dim x ff_dim + embed_dim + ff_dim (dwie warstwy liniowe + odchylenia)
- **Norm warstwy na blok**: 4 x embed_dim (dwie normy, każda ze skalą + obciążeniem)
- **Norma warstwy końcowej**: 2 x embed_dim
- **Głowica wyjściowa**: vocab_size x embed_dim (lub 0, jeśli waga jest powiązana z osadzeniem tokenów)

Oznacz, jeśli jakikolwiek pojedynczy komponent przekracza 40% wszystkich parametrów. W małych modelach dominuje matryca osadzająca. W dużych modelach dominuje uwaga i FFN.

### 2. Analiza projektu uwagi

Oceń konfigurację uwagi:

- **Wymiar główki**: embed_dim / num_heads. Standardem jest 64 (GPT-2) lub 128 (Lama 3). Poniżej 32 limitów ekspresji na głowę. Powyżej 128 obliczenia są marnotrawstwem i przynoszą niewielkie korzyści.
- **Głowice na warstwę**: Więcej głów = bardziej zróżnicowane wzorce uwagi, ale więcej pamięci na pamięć podręczną KV.
- **Grouped Query Attention (GQA)**: Czy model ma wspólne głowice K/V pomiędzy wieloma głowicami Q? Lama 3 wykorzystuje GQA z głowicami 8 KV dla głowic 32 Q. Zmniejsza to pamięć podręczną KV 4x.
- **Długość kontekstu**: Maksymalne osadzenie pozycji. RoPE umożliwia ekstrapolację poza długość treningu. Osadzanie pozycji absolutnej nie.

### 3. Budżet pamięci

Aby wywnioskować na temat maksymalnej długości kontekstu modelu:

- **Wagi (FP16)**: total_params x 2 bajty
- **KV Cache (FP16)**: 2 x num_layers x num_kv_heads x head_dim x max_seq_len x 2 bajty
- **Aktywacje**: rozmiar_wsadu x seq_len x embed_dim x 2 bajty x liczba_warstw (w przybliżeniu)

Oznacz, jeśli pamięć podręczna KV przekracza pamięć wagi. Dzieje się tak w przypadku modeli o długim kontekście (128 KB+) i wskazuje, że model jest związany z pamięcią podczas dekodowania.

### 4. Oblicz profil

- **Wstępne wypełnienie FLOPS na token**: około 2 x total_params (jeden matmul na parametr, przejście w przód)
- **Dekoduj FLOPY na token**: tak samo jak w przypadku wstępnego wypełnienia, ale na pojedynczym tokenie
- **Wstępne wypełnienie wąskiego gardła**: ograniczone obliczeniami (TFLOPS GPU)
- **Wąskie gardło dekodowania**: związane z pamięcią (przepustowość pamięci GPU)
- **Intensywność arytmetyczna**: FLOPS na bajt dostępnej pamięci. Poniżej 100 = związany z pamięcią.

### 5. Decyzje dotyczące skalowania

Oceń pod kątem znanych praw skalowania:

- **Optymalny szynszyla**: Dla danego budżetu obliczeniowego C, optymalny rozmiar modelu N i liczba tokenów D spełniają N ~ D (w przybliżeniu równe skalowanie). Model 7B potrzebuje ~140B tokenów.
- **Lama 3 przetrenowana**: Meta wytrenowała Lamę 3 8B na tokenach 15T (optymalnie 100x Szynszyla). Przetrenowanie małych modeli na większej liczbie danych powoduje lepszy koszt wnioskowania na token.
- **Szerokość w porównaniu z głębokością**: Głębsze modele (więcej warstw) są generalnie bardziej efektywne pod względem próbkowania niż szersze modele (większy embed_dim) przy tej samej liczbie parametrów.

## Czerwone flagi

- **Współczynnik FFN inny niż 4x**: Standardem jest ff_dim = 4 x embed_dim. Lama używa 8/3 x embed_dim z SwiGLU. Odchylenia należy uzasadnić.
- **Brak wiązania wag**: Głowica wyjściowa powinna dzielić wagi z osadzonymi tokenami, chyba że vocab_size jest bardzo duży w stosunku do embed_dim.
- **Brak GQA powyżej 13B**: Modele powyżej 13B bez obsługi zapytań grupowych będą miały zbyt duże pamięci podręczne KV.
- **Brak RoPE w długim kontekście**: Osadzenie pozycji bezwzględnej nie ekstrapoluje poza długość treningu. Modele ukierunkowane na kontekst 32 000+ powinny używać osadzania obrotowego.
- **Tempo uczenia się zbyt wysokie w stosunku do wielkości modelu**: Większe modele wymagają niższych szczytowych współczynników uczenia się. GPT-2 Mały wykorzystuje 6e-4. Lama 3 405B wykorzystuje 8e-5.

##Format wyjściowy

1. **Tabela parametrów**: zliczanie parametrów poszczególnych składników w procentach
2. **Budżet pamięci**: wagi, pamięć podręczna KV i pamięć aktywacyjna przy maksymalnej długości kontekstu
3. **Profil obliczeniowy**: wstępne wypełnienie i oszacowanie przepustowości dla A100/H100
4. **Ocena projektu**: co model jest dobre, a co niestandardowe
5. **Werdykt skalowania**: czy model ma odpowiedni rozmiar pod kątem danych uczących