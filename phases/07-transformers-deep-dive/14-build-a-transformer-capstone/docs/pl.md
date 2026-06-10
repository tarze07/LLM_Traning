# Zbuduj transformator od podstaw — zwieńczenie

> Trzynaście lekcji. Jeden model. Żadnych skrótów.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 7 · 01 do 13. Nie pomijaj.
**Czas:** ~120 minut

## Problem

Przeczytałeś każdą gazetę. Zaimplementowałeś uwagę, podziały wielogłowicowe, kodowanie pozycyjne, bloki kodera i dekodera, straty BERT i GPT, MoE, pamięć podręczną KV. Teraz spraw, aby pracowali razem nad prawdziwym zadaniem.

Zwieńczenie: kompleksowe przeszkolenie małego transformatora obsługującego tylko dekoder w ramach zadania modelowania języka na poziomie znaków. Czyta Szekspira. Rodzi nowego Szekspira. Jest na tyle mały, że można ćwiczyć na laptopie w niecałe 10 minut. Jest wystarczająco poprawne, że zamiana większego zbioru danych i dłuższe szkolenie zapewniają prawdziwy LM.

To jest „nanoGPT” kursu. Nie jest oryginalny — poradnik nanoGPT firmy Karpathy na rok 2023 to referencyjna implementacja, którą każdy uczeń napisał przynajmniej raz. Podnosimy kształt i dopasowujemy go do tego, co omówiliśmy.

## Koncepcja

![Schemat blokowy transformatora od podstaw](../assets/capstone.svg)

Architektura z adnotacją:

```
input tokens (B, N)
   │
   ▼
token embedding + positional embedding  ◀── Lesson 04 (RoPE option)
   │
   ▼
┌──── block × L ────────────────────┐
│  RMSNorm                          │  ◀── Lesson 05
│  MultiHeadAttention (causal)      │  ◀── Lesson 03 + 07 (causal mask)
│  residual                         │
│  RMSNorm                          │
│  SwiGLU FFN                       │  ◀── Lesson 05
│  residual                         │
└────────────────────────────────── ┘
   │
   ▼
final RMSNorm
   │
   ▼
lm_head (tied to token embedding)
   │
   ▼
logits (B, N, V)
   │
   ▼
shift-by-one cross-entropy            ◀── Lesson 07
```

### Co wysyłamy

- `GPTConfig` — jedno miejsce do konfiguracji wszystkich hiperparametrów.
- `MultiHeadAttention` — przyczynowy, wsadowy, z opcjonalną ścieżką w stylu Flash (`scaled_dot_product_attention` firmy PyTorch).
- `SwiGLUFFN` — nowoczesny FFN.
- `Block` — przednormowa uwaga skupiona na pozostałościach + FFN.
- `GPT` — osadzania, bloki piętrowe, nagłówek LM, generuj().
- Pętla treningowa z AdamemW, cosinus LR, obcinanie gradientu.
- Tokenizator na poziomie znaku w tekście Szekspira.

### Czego nie wysyłamy

- RoPE — zaimplementowane koncepcyjnie w Lekcji 04. Dla uproszczenia używamy tutaj wyuczonych osadzania pozycyjnego. W ćwiczeniach wymagana jest zamiana liny.
- Pamięć podręczna KV podczas generowania — każdy krok generacji przelicza uwagę na pełnym prefiksie. Wolniej, ale prościej. W ćwiczeniach wymagane jest dodanie pamięci podręcznej KV.
- Uwaga Flash — PyTorch 2.0+ automatycznie wysyła informację, jeśli dane wejściowe są zgodne; używamy `F.scaled_dot_product_attention`.
- MoE — pojedynczy FFN na blok. Widziałeś MoE w lekcji 11.

### Dane docelowe

Na laptopie Mac M2, 4-warstwowym, 4-głowicowym, d_model=128 GPT przeszkolonym na 2000 kroków na `tinyshakespeare.txt`:

- Strata treningowa zbiega się z ~4,2 (losowo) do ~1,5 w ciągu około 6 minut.
- Próbki wyjściowe wyglądają jak Szekspir: pojawiają się archaiczne słowa, podziały wierszy, pojawiają się nazwy własne, takie jak „ROMEO:”.
- Utrata Val (zatrzymane ostatnie 10% tekstu) ściśle śledzi utratę treningu; bez nadmiernego wyposażenia przy tym rozmiarze/budżecie.

## Zbuduj to

W tej lekcji wykorzystano PyTorch. Zainstaluj `torch` (kompilacja procesora jest w porządku). Zobacz `code/main.py`. Skrypt obsługuje:

- Pobieranie `tinyshakespeare.txt` w przypadku braku (lub czytanie kopii lokalnej).
- Tokenizator znaków na poziomie bajtu.
- Podział pociągu na val w proporcji 90/10.
- Pętla treningowa z autocastem bf16 na obsługiwanym sprzęcie.
- Pobieranie próbek po zakończeniu szkolenia.

### Krok 1: dane

```python
text = open("tinyshakespeare.txt").read()
chars = sorted(set(text))
stoi = {c: i for i, c in enumerate(chars)}
itos = {i: c for c, i in stoi.items()}
encode = lambda s: [stoi[c] for c in s]
decode = lambda xs: "".join(itos[x] for x in xs)
```

65 unikalnych znaków. Malutkie słownictwo. Pasuje do 4-bajtowego pliku vocab_size. Żadnego BPE, żadnego dramatu tokenizera.

### Krok 2: model

Zobacz `code/main.py`. Blok to podręcznik z lekcji 05 — pre-norm, RMSNorm, SwiGLU, przyczynowy MHA. Ilość parametrów dla 4/4/128: ~800K.

### Krok 3: pętla treningowa

Zdobądź losową partię okien żetonowych o długości 256. Do przodu. Przesunięcie entropii krzyżowej o jeden. Wstecz. Krok Adama. Dziennik. Powtarzać.

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

### Krok 4: próbka

Po wyświetleniu monitu wielokrotnie przesyłaj dalej, próbkuj z logitów z najwyższej półki, dołącz i kontynuuj. Zatrzymaj się po 500 żetonach.

### Krok 5: przeczytaj wynik

Po 2000 kroków:

```
ROMEO:
Away and mild will not thy friend, that thou shalt wit:
The chief that well shame and hath been his friends,
...
```

Nie Szekspir. Ale w kształcie Szekspira. Wyraźne zwycięstwo przy parametrach ~800K i 6 minutach na laptopie.

## Użyj tego

To zwieńczenie jest architekturą referencyjną. Trzy rozszerzenia, aby wysłać go do czegoś prawdziwego:

1. **Zamień tokenizer.** Użyj BPE (np. `tiktoken.get_encoding("cl100k_base")`). Rozmiar słownictwa skacze z 65 do ~ 50 000. Aby to zrekompensować, pojemność modelu musi zostać zwiększona.
2. **Trenuj na większym ciele.** Użyj `OpenWebText` lub `fineweb-edu` (HuggingFace). Tokeny 10B na pojedynczym A100 zajmują ~24 godziny w przypadku GPT o parametrach 125M.
3. **Dodaj RoPE + pamięć podręczną KV + uwaga Flash.** Poniższe ćwiczenia przeprowadzą Cię przez każdy z nich.

Kończy się to jako GPT o parametrach 125M, który generuje płynny język angielski. To nie jest model graniczny. Ale tę samą ścieżkę kodu – tylko większą – wykorzystają firmy Karpathy, EleutherAI i Instytut Allena do szkolenia punktów kontrolnych badań w 2026 r.

## Wyślij to

Zobacz `outputs/skill-transformer-review.md`. Umiejętność sprawdza poprawność implementacji transformatora od podstaw we wszystkich 13 wcześniejszych lekcjach.

## Ćwiczenia

1. **Łatwe.** Uruchom `code/main.py`. Sprawdź, czy utrata walidacji w ostatnim kroku przeszkolonego modelu jest mniejsza niż 2,0. Zmień `max_steps` z 2000 na 5000 — czy utrata wartości stale się poprawia?
2. **Średni.** Zastąp wyuczone osadzania pozycyjne RoPE. Zastosuj obrót do Q i K wewnątrz `MultiHeadAttention`. Trenuj i sprawdzaj, czy utrata wartości jest co najmniej tak niska.
3. **Średni.** Zaimplementuj pamięć podręczną KV w pętli próbkowania. Wygeneruj 500 tokenów z pamięcią podręczną i bez niej. Zegar ścienny powinien poprawić się o 5–20× na laptopie.
4. **Trudne.** Dodaj drugą głowę do modelu, który przewiduje token następny plus jeden (MTP — Multi-Token Prediction z DeepSeek-V3). Trenuj wspólnie. Czy to pomaga?
5. **Trudne.** Zamień pojedynczy FFN na blok na 4-ekspertowy MoE. Router + routing top 2. Zobacz, jak zmienia się utrata wartości przy dopasowanych aktywnych parametrach.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| nanoGPT | „Repozytorium samouczków Karpathy” | Minimalny kod szkoleniowy transformatora przeznaczony tylko do dekodera, ~300 LOC; odniesienie kanoniczne. |
| malutki Szekspir | „Standardowy korpus zabawek” | ~1,1 MB tekstu; używa go każdy samouczek dotyczący postaci LM od 2015 roku. |
| Wiązane osadzania | „Udostępnij macierz wejść/wyjść” | Masa głowy LM = transpozycja macierzy osadzania tokenu; zapisuje parametry, poprawia jakość. |
| Automatyczne rzucanie bf16 | „Trening precyzji” | Uruchom do przodu/do tyłu w bf16, zachowaj stan optymalizatora w fp32; standard od 2021 r. |
| Przycinanie gradientu | „Zatrzymuje skoki” | Ogranicz globalną normę gradacyjną na poziomie 1,0; zapobiega wybuchom treningowym. |
| Cosinus harmonogram LR | „Domyślne ustawienie na rok 2020+” | LR narasta liniowo (rozgrzewka), a następnie zanika w kształcie cosinusa do 10% wartości szczytowej. |
| MFU | „Wykorzystanie modelu FLOP” | Osiągnięte FLOPy / szczyt teoretyczny; 40% gęstości, 30% MoE jest mocne w 2026 r. |
| Utrata wartości | „Przetrzymywana strata” | Entropia krzyżowa na danych, których model nigdy nie widział; detektor nadmiernego dopasowania. |

## Dalsze czytanie

- [The Annotated Transformer (Harvard NLP)](https://nlp.seas.harvard.edu/annotated-transformer/) — klasyczna implementacja z adnotacjami.