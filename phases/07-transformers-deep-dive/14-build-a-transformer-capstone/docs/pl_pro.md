# Zbuduj transformator od podstaw — projekt podsumowujący (Capstone)

> Trzytnaście lekcji. Jeden model. Żadnych dróg na skróty.

**Typ:** Projekt praktyczny
**Język:** Python
**Wymagania wstępne:** Faza 7 (lekcje od 01 do 13). Nie pomijaj ich.
**Czas wykonania:** ~120 minut

## Problem

Przeczytałeś już wszystkie najważniejsze publikacje naukowe. Zaimplementowałeś mechanizm uwagi (attention), podział na wiele głowic (multi-head), kodowanie pozycyjne, bloki kodera i dekodera, funkcje straty dla modeli BERT i GPT, architekturę MoE oraz pamięć podręczną KV (KV cache). Teraz czas połączyć te elementy w jedno działające rozwiązanie dla rzeczywistego zadania.

Twój projekt podsumowujący (capstone) polega na kompleksowym wytrenowaniu małego transformera typu decoder-only w zadaniu modelowania języka na poziomie znaków. Model będzie czytał dzieła Szekspira i generował nowy tekst w jego stylu. Jest on na tyle mały, że można go w pełni wytrenować na zwykłym laptopie w czasie poniżej 10 minut. Jednocześnie architektura ta jest na tyle poprawna, że zastąpienie zbioru danych większym korpusem i dłuższy trening pozwolą uzyskać pełnowartościowy model językowy (LM).

Jest to nasz odpowiednik słynnego projektu „nanoGPT”. Nie odkrywamy tu koła na nowo — udostępniony przez Andreja Karpathy'ego w 2023 roku kod nanoGPT to kanoniczna implementacja referencyjna, którą powinien napisać każdy adept głębokiego uczenia. Opieramy się na tej sprawdzonej strukturze, dostosowując ją do zagadnień omówionych w poprzednich lekcjach.

## Koncepcja

![Schemat blokowy transformatora od podstaw](../assets/capstone.svg)

Architektura z objaśnieniami:

```
input tokens (B, N)
   │
   ▼
token embedding + positional embedding  ◀── Lekcja 04 (opcjonalnie RoPE)
   │
   ▼
┌──── block × L ────────────────────┐
│  RMSNorm                          │  ◀── Lekcja 05
│  MultiHeadAttention (causal)      │  ◀── Lekcja 03 + 07 (maska przyczynowa)
│  residual                         │
│  RMSNorm                          │
│  SwiGLU FFN                       │  ◀── Lekcja 05
│  residual                         │
└────────────────────────────────── ┘
   │
   ▼
final RMSNorm
   │
   ▼
lm_head (powiązany z token embedding)
   │
   ▼
logits (B, N, V)
   │
   ▼
shift-by-one cross-entropy            ◀── Lekcja 07
```

### Co wchodzi w skład implementacji

- `GPTConfig` — scentralizowana konfiguracja wszystkich hiperparametrów.
- `MultiHeadAttention` — moduł przyczynowej uwagi wielogłowicowej przetwarzanej wsadowo z opcjonalną ścieżką FlashAttention (`scaled_dot_product_attention` z biblioteki PyTorch).
- `SwiGLUFFN` — nowoczesna warstwa sieci neuronowej FFN.
- `Block` — blok transformera z normalizacją wstępną (pre-norm), połączeniem rezydualnym dla mechanizmu uwagi oraz warstwą FFN.
- `GPT` — moduły osadzania (embeddings), stos bloków, głowica językową (LM head) oraz funkcja generowania `generate()`.
- Pętla treningowa z optymalizatorem AdamW, cosinusowym harmonogramem współczynnika uczenia (cosine LR schedule) i przycinaniem gradientu (gradient clipping).
- Tokenizer znakowy (character-level tokenizer) dopasowany do tekstów Szekspira.

### Czego nie implementujemy (wersja bazowa)

- **RoPE** — omówiony teoretycznie i praktycznie w lekcji 04. Dla uproszczenia w kodzie startowym stosujemy wyuczone kodowania pozycyjne (learned positional embeddings). Zastąpienie ich przez RoPE jest częścią ćwiczeń.
- **Pamięć podręczna KV (KV cache) podczas generowania** — w wersji podstawowej każdy krok generowania przelicza atencję dla całego prefiksu od nowa. Rozwiązanie to jest wolniejsze, ale prostsze w implementacji. Dodanie KV cache zostało przewidziane jako zadanie w ćwiczeniach.
- **FlashAttention** — PyTorch 2.0+ automatycznie przekazuje obliczenia do zoptymalizowanego jądra (dispatch), jeśli format danych wejściowych jest zgodny; korzystamy bezpośrednio z `F.scaled_dot_product_attention`.
- **MoE** — pojedyncza warstwa FFN na blok. Architektura Mixture of Experts została przedstawiona w lekcji 11.

### Spodziewane rezultaty

Trening na laptopie z procesorem Mac M2, przy użyciu modelu GPT o 4 warstwach, 4 głowicach uwagi i `d_model=128`, trenowanego przez 2000 kroków na zbiorze `tinyshakespeare.txt`:

- Strata treningowa (training loss) spada z ~4,2 (wartość początkowa dla losowych wag) do ~1,5 w czasie około 6 minut.
- Generowane teksty przypominają styl Szekspira: pojawiają się archaiczne słowa, podziały wierszy oraz nazwy własne postaci (np. „ROMEO:”).
- Strata na zbiorze walidacyjnym (validation loss — wyodrębnione ostatnie 10% tekstu) ściśle podąża za stratą treningową; przy tym rozmiarze modelu i budżecie treningowym nie występuje zjawisko przeuczenia (overfitting).

## Implementacja krok po kroku

W tym projekcie wykorzystujemy bibliotekę PyTorch. Zainstaluj pakiet `torch` (wersja na procesor [CPU] w zupełności wystarczy). Szczegółowy kod znajduje się w pliku `code/main.py`. Skrypt realizuje:

- Pobieranie pliku `tinyshakespeare.txt` w przypadku jego braku (lub odczyt z lokalnego katalogu).
- Tokenizer znakowy na poziomie bajtów.
- Podział zbioru danych na część treningową i walidacyjną (train/val) w proporcji 90/10.
- Pętlę treningową z automatycznym doborem precyzji (autocast bf16) na obsługiwanym sprzęcie.
- Generowanie próbek tekstu po zakończeniu procesu uczenia.

### Krok 1: Przygotowanie danych

```python
text = open("tinyshakespeare.txt").read()
chars = sorted(set(text))
stoi = {c: i for i, c in enumerate(chars)}
itos = {i: c for c, i in stoi.items()}
encode = lambda s: [stoi[c] for c in s]
decode = lambda xs: "".join(itos[x] for x in xs)
```

Nasz słownik składa się z 65 unikalnych znaków. Jest on bardzo mały, więc rozmiar słownika (`vocab_size`) mieści się bez problemu w jednym bajcie. Omijamy skomplikowane tokenizery typu BPE i związane z nimi trudności implementacyjne.

### Krok 2: Definicja modelu

Szczegóły znajdziesz w pliku `code/main.py`. Moduł `Block` to klasyczna implementacja z lekcji 05 — normalizacja wstępna (pre-norm), RMSNorm, SwiGLU oraz przyczynowa uwaga wielogłowicowa (causal MHA). Liczba parametrów dla konfiguracji 4 warstwy / 4 głowice / szerokość 128 wynosi około 800 tysięcy.

### Krok 3: Pętla treningowa

Pobierz losowy minibatch okien tokenów o długości 256. Wykonaj przejście w przód (forward pass). Oblicz stratę za pomocą funkcji entropii krzyżowej z przesunięciem o jeden element (shift-by-one cross-entropy). Wykonaj przejście wsteczne (backward pass). Wykonaj krok optymalizatora AdamW. Zapisz wyniki w logach i powtórz proces.

```python
for step in range(max_steps):
    x, y = get_batch("train")
    logits = model(x)
    loss = F.cross_entropy(logits.view(-1, vocab_size), y.view(-1))
    loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
    opt.step()
    opt.zero_grad()
```

### Krok 4: Generowanie próbek (sampling)

Mając dany prompt (tekst wejściowy), wykonuj iteracyjnie przejście w przód, próbkowanie z logitów przy użyciu metody top-k/top-p, dołączaj wygenerowane tokeny do kontekstu i kontynuuj. Zatrzymaj generowanie po osiągnięciu 500 tokenów.

### Krok 5: Analiza wyników

Przykładowy wygenerowany tekst po 2000 kroków uczenia:

```
ROMEO:
Away and mild will not thy friend, that thou shalt wit:
The chief that well shame and hath been his friends,
...
```

Nie jest to jeszcze dzieło sztuki literackiej, ale tekst zachowuje strukturę metryczną Szekspira. Jest to ogromny sukces dla modelu o rozmiarze zaledwie ~800 tys. parametrów, trenowanego przez 6 minut na zwykłym laptopie.

## Zastosowanie praktyczne

Ten projekt stanowi architekturę referencyjną. Aby przekształcić go w pełnowartościowy, użyteczny model językowy, należy wdrożyć trzy modyfikacje:

1. **Zastosowanie zaawansowanego tokenizera.** Wykorzystaj tokenizer BPE (np. `tiktoken.get_encoding("cl100k_base")`). Rozmiar słownika wzrośnie wtedy z 65 do około 100 000 tokenów. Aby to skompensować, należy odpowiednio zwiększyć pojemność modelu.
2. **Trening na dużym korpusie danych.** Wykorzystaj zbiory danych takie jak `OpenWebText` lub `fineweb-edu` (dostępne na platformie HuggingFace). Trening na 10 miliardach tokenów (10B tokens) przy użyciu pojedynczej karty GPU A100 trwa około 24 godzin dla modelu GPT o rozmiarze 125M parametrów.
3. **Wdrożenie RoPE, KV cache oraz FlashAttention.** Zadania te zostały opisane w sekcji z ćwiczeniami.

Otrzymany w ten sposób model GPT-125M potrafi generować gramatycznie poprawny i spójny tekst w języku angielskim. Choć nie jest to model typu frontier, to dokładnie taka sama ścieżka kodu (odpowiednio przeskalowana) jest wykorzystywana przez zespoły takie jak EleutherAI czy Allen Institute do trenowania nowoczesnych modeli badawczych.

## Ewaluacja projektu

Przejdź do pliku `outputs/skill-transformer-review.md`. Dedykowane narzędzie (skill) służy do weryfikacji poprawności Twojej implementacji transformera od podstaw, bazując na wiedzy zebranej we wszystkich 13 wcześniejszych lekcjach.

## Ćwiczenia

1. **Łatwe.** Uruchom skrypt `code/main.py`. Sprawdź, czy strata walidacyjna w ostatnim kroku treningu spadła poniżej 2,0. Zwiększ `max_steps` z 2000 do 5000 — czy strata walidacyjna wciąż maleje?
2. **Średnie.** Zastąp wyuczone kodowania pozycyjne kodowaniem RoPE (Rotary Position Embedding). Zastosuj rotację do tensorów Q i K wewnątrz modułu `MultiHeadAttention`. Wytrenuj model i sprawdź, czy strata walidacyjna jest na zbliżonym lub lepszym poziomie.
3. **Średnie.** Zaimplementuj pamięć podręczną KV (KV cache) w pętli generowania (sampling). Wygeneruj 500 tokenów z pamięcią podręczną i bez niej. Rzeczywisty czas generowania (wall-clock time) na laptopie powinien spaść od 5 do 20 razy.
4. **Trudne.** Dodaj do modelu drugą głowę (head), która przewiduje kolejny token oraz token po nim (MTP — Multi-Token Prediction, znane np. z DeepSeek-V3). Zastosuj wspólny trening (joint training). Czy poprawia to zbieżność i dynamikę uczenia?
5. **Trudne.** Zastąp pojedynczą sieć FFN w każdym bloku warstwą MoE (Mixture of Experts) z 4 ekspertami. Zaimplementuj router wybierający 2 najlepszych ekspertów (top-2 routing). Sprawdź, jak zmienia się strata walidacyjna przy zachowaniu tej samej liczby aktywnych parametrów.

## Kluczowe terminy

| Termin | Potoczne określenie | Co to naprawdę oznacza |
| :--- | :--- | :--- |
| **nanoGPT** | „Samouczek od Karpathy'ego” | Minimalny kod treningowy transformera opartego wyłącznie na dekoderze (decoder-only), składający się z około 300 linii kodu (LOC); kanoniczna implementacja referencyjna. |
| **Tiny Shakespeare** | „Klasyczny minikorpus testowy” | ~1,1 MB tekstu; wykorzystywany w niemal każdym samouczku tworzenia modeli językowych na poziomie znaków od 2015 roku. |
| **Wiązanie wag (Weight tying)** | „Współdzielenie macierzy wejścia/wyjścia” | Wagi warstwy lm_head są tożsame z transponowaną macierzą osadzeń tokenów (token embeddings). Pozwala to zaoszczędzić parametry i poprawić jakość modelu. |
| **Autocast bf16** | „Trening o mieszanej precyzji” | Wykonanie przejścia w przód i wstecz (forward/backward) w precyzji bf16 przy jednoczesnym zachowaniu wag optymalizatora w fp32; standard w branży od 2021 roku. |
| **Przycinanie gradientów (Gradient clipping)** | „Zapobieganie nagłym skokom” | Ograniczenie globalnej normy gradientu do określonej wartości (np. 1,0); zapobiega eksplozji gradientu podczas treningu. |
| **Cosinusowy harmonogram LR (Cosine LR schedule)** | „Domyślna konfiguracja uczenia” | Współczynnik uczenia (learning rate) rośnie liniowo (rozgrzewka / warmup), a następnie maleje według funkcji cosinusowej do 10% swojej wartości szczytowej. |
| **MFU (Model FLOPs Utilization)** | „Efektywność obliczeniowa modelu” | Stosunek faktycznie wykonanych operacji FLOP do teoretycznej wydajności szczytowej sprzętu; wartości na poziomie 40% dla modeli gęstych (dense) i 30% dla MoE są bardzo dobrymi wynikami. |
| **Strata walidacyjna (Validation loss)** | „Strata na zbiorze testowym” | Wartość funkcji straty (entropii krzyżowej) obliczana na danych niewykorzystywanych w treningu; podstawowe narzędzie do wykrywania przeuczenia (overfitting). |

## Dalsze czytanie

- [The Annotated Transformer (Harvard NLP)](https://nlp.seas.harvard.edu/annotated-transformer/) — klasyczna, szczegółowo omówiona implementacja architektury Transformer.
