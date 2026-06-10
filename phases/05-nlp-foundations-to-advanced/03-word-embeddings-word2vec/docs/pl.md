# Osadzanie słów — Word2Vec od podstaw

> Słowo jest towarzystwem, któremu dotrzymuje. Wytrenuj płytką siatkę na tym pomyśle, a geometria wypadnie.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 5 · 02 (BoW + TF-IDF), Faza 3 · 03 (propagacja wsteczna od podstaw)
**Czas:** ~75 minut

## Problem

TF-IDF wie, że `dog` i `puppy` to różne słowa. Nie wie, że mają na myśli prawie to samo. Klasyfikator przeszkolony w zakresie `dog` nie może uogólniać opinii na temat `puppy`. Możesz to zatuszować, wymieniając synonimy, ale nie udaje się to w przypadku rzadkich terminów, żargonu domeny i każdego języka, którego się nie spodziewałeś.

Chcesz reprezentacji, w której `dog` i `puppy` lądują blisko siebie w przestrzeni. Gdzie `king - man + woman` ląduje w pobliżu `queen`. Gdzie model przeszkolony na `dog` przekazuje część sygnału do `puppy` za darmo.

Word2Vec dał nam tę przestrzeń. Dwuwarstwowa sieć neuronowa, przebiegi szkoleniowe o wartości bilionów tokenów, opublikowana w 2013 roku. Architektura jest niemal żenująco prosta. Wyniki zmieniły NLP na dekadę.

## Koncepcja

**Hipoteza dystrybucyjna** (Firth, 1957): „Poznasz słowo po towarzystwie, w jakim się ono znajduje”. Jeśli dwa słowa pojawiają się w podobnych kontekstach, prawdopodobnie mają na myśli podobne rzeczy.

Word2Vec jest dostępny w dwóch wersjach, obie wykorzystują ten pomysł.

- **Pomiń gram.** Biorąc pod uwagę słowo środkowe, przewiduj słowa otaczające. `cat -> (the, sat, on)` z oknem o rozmiarze 2.
- **CBOW (ciągły zbiór słów).** Biorąc pod uwagę otaczające słowa, przewiduj środek. `(the, sat, on) -> cat`.

Skip-gram jest wolniejszy w uczeniu, ale lepiej radzi sobie z rzadkimi słowami. Stało się domyślnym.

Sieć ma jedną warstwę ukrytą, pozbawioną nieliniowości. Dane wejściowe to wektor o wartości jednokrotnej nad słownictwem. Dane wyjściowe to softmax w stosunku do słownictwa. Po treningu wyrzucasz warstwę wyjściową. Wagi warstw ukrytych to osadzenia.

```
one-hot(center) ── W ──▶ hidden (d-dim) ── W' ──▶ softmax(vocab)
                          ^
                          this is the embedding
```

Sztuczka: softmax powyżej 100 tys. słów jest zaporowo drogi. Word2Vec używa **próbkowania negatywnego**, aby przekształcić je w zadanie klasyfikacji binarnej. Wytypuj, „czy to słowo kontekstowe pojawiło się w pobliżu tego środkowego słowa, tak czy nie”. Próbuj garść negatywnych (nie współwystępujących) słów na parę treningową, zamiast obliczać softmax dla całego słownictwa.

## Zbuduj to

### Krok 1: szkolenie par z korpusu

```python
def skipgram_pairs(docs, window=2):
    pairs = []
    for doc in docs:
        for i, center in enumerate(doc):
            for j in range(max(0, i - window), min(len(doc), i + window + 1)):
                if i == j:
                    continue
                pairs.append((center, doc[j]))
    return pairs
```

```python
>>> skipgram_pairs([["the", "cat", "sat", "on", "mat"]], window=2)
[('the', 'cat'), ('the', 'sat'),
 ('cat', 'the'), ('cat', 'sat'), ('cat', 'on'),
 ('sat', 'the'), ('sat', 'cat'), ('sat', 'on'), ('sat', 'mat'),
 ...]
```

Każda para (centrum, kontekst) w oknie jest pozytywnym przykładem szkoleniowym.

### Krok 2: osadzanie tabel

Dwie matryce. `W` to tabela do osadzania słów środkowych (ta, którą przechowujesz). `W'` to tabela słów kontekstowych (często odrzucana, czasami uśredniana za pomocą `W`).

```python
import numpy as np

def init_embeddings(vocab_size, dim, seed=0):
    rng = np.random.default_rng(seed)
    W = rng.normal(0, 0.1, size=(vocab_size, dim))
    W_prime = rng.normal(0, 0.1, size=(vocab_size, dim))
    return W, W_prime
```

Mały losowy początek. Vocab o rozmiarze 10k i przyciemnieniu 100 jest realistyczny; do nauczania wystarczy 50 słów x 16 dim, aby zobaczyć geometrię.

### Krok 3: cel negatywnego pobierania próbek

Dla każdej pary dodatniej `(center, context)` pobierz `k` losowe słowa ze słownictwa jako wartości ujemne. Wytrenuj model tak, aby iloczyn skalarny `W[center] · W'[context]` był wysoki w przypadku pozytywów i niski w przypadku negatywów.

```python
def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -20, 20)))

def train_pair(W, W_prime, center_idx, context_idx, negative_indices, lr):
    v_c = W[center_idx]
    u_pos = W_prime[context_idx]
    u_negs = W_prime[negative_indices]

    pos_score = sigmoid(v_c @ u_pos)
    neg_scores = sigmoid(u_negs @ v_c)

    grad_center = (pos_score - 1) * u_pos
    for i, u in enumerate(u_negs):
        grad_center += neg_scores[i] * u

    W[context_idx] = W[context_idx]
    W_prime[context_idx] -= lr * (pos_score - 1) * v_c
    for i, neg_idx in enumerate(negative_indices):
        W_prime[neg_idx] -= lr * neg_scores[i] * v_c
    W[center_idx] -= lr * grad_center
```

Magiczna formuła: strata logistyczna na parze dodatniej (chcę sigmoidy w pobliżu 1) plus strata logistyczna na parach ujemnych (chcę sigmoidy w pobliżu 0). Gradienty przepływają do obu tabel. Pełne wyprowadzenie znajduje się w oryginalnej pracy; przejdź przez niego raz ołówkiem i papierem, jeśli chcesz, żeby się przykleił.

### Krok 4: trenuj na korpusie zabawki

```python
def train(docs, dim=16, window=2, k_neg=5, epochs=100, lr=0.05, seed=0):
    vocab = build_vocab(docs)
    vocab_size = len(vocab)
    rng = np.random.default_rng(seed)
    W, W_prime = init_embeddings(vocab_size, dim, seed=seed)
    pairs = skipgram_pairs(docs, window=window)

    for epoch in range(epochs):
        rng.shuffle(pairs)
        for center, context in pairs:
            c_idx = vocab[center]
            ctx_idx = vocab[context]
            negs = rng.integers(0, vocab_size, size=k_neg)
            negs = [n for n in negs if n != ctx_idx and n != c_idx]
            train_pair(W, W_prime, c_idx, ctx_idx, negs, lr)
    return vocab, W
```

Po wystarczającej liczbie epok w dużym korpusie słowa o tym samym kontekście mają podobne osadzenie w środku. Na korpusie zabawki efekt ten jest słabo widoczny. Na miliardach tokenów widać to dramatycznie.

### Krok 5: sztuczka z analogią

```python
def nearest(vocab, W, target_vec, topk=5, exclude=None):
    exclude = exclude or set()
    inv_vocab = {i: w for w, i in vocab.items()}
    norms = np.linalg.norm(W, axis=1, keepdims=True) + 1e-9
    W_norm = W / norms
    target = target_vec / (np.linalg.norm(target_vec) + 1e-9)
    sims = W_norm @ target
    order = np.argsort(-sims)
    out = []
    for i in order:
        if i in exclude:
            continue
        out.append((inv_vocab[i], float(sims[i])))
        if len(out) == topk:
            break
    return out

def analogy(vocab, W, a, b, c, topk=5):
    v = W[vocab[b]] - W[vocab[a]] + W[vocab[c]]
    return nearest(vocab, W, v, topk=topk, exclude={vocab[a], vocab[b], vocab[c]})
```

Na wstępnie wytrenowanych wektorach 300d Google News:

```python
>>> analogy(vocab, W, "man", "king", "woman")
[('queen', 0.71), ('monarch', 0.62), ('princess', 0.59), ...]
```

`king - man + woman = queen`. Nie dlatego, że modelka wie, czym jest królewskość. Ponieważ wektor `(king - man)` przechwytuje coś w rodzaju „królewskiego”, a dodanie go do `woman` ląduje w pobliżu regionu królewskiego-żeńskiego.

## Użyj tego

Pisanie Word2Vec od zera to nauka. Produkcja NLP używa `gensim`.

```python
from gensim.models import Word2Vec

sentences = [
    ["the", "cat", "sat", "on", "the", "mat"],
    ["the", "dog", "ran", "across", "the", "room"],
]

model = Word2Vec(
    sentences,
    vector_size=100,
    window=5,
    min_count=1,
    sg=1,
    negative=5,
    workers=4,
    epochs=30,
)

print(model.wv["cat"])
print(model.wv.most_similar("cat", topn=3))
```

Do prawdziwej pracy prawie nigdy sam nie szkolisz Word2Vec. Pobierasz wstępnie wytrenowane wektory.

- **GloVe** — podejście faktoryzacji oparte na macierzy współwystępowań Stanforda. Punkty kontrolne 50d, 100d, 200d, 300d. Dobry zasięg ogólny. Lekcja 04 dotyczy konkretnie GloVe.
- **fastText** — rozszerzenie Facebooka do Word2Vec, które osadza n-gramy znaków. Radzi sobie ze słowami spoza słownika, tworząc podsłowa. Lekcja 04.
- **Wstępnie przeszkolony Word2Vec w Google News** — 300d, 3 miliony słów, publikacja 2013. Nadal pobierany codziennie.

### Kiedy Word2Vec nadal zwycięża w 2026 roku

- Lekkie pobieranie specyficzne dla domeny. Trenuj abstrakty medyczne w ciągu godziny na laptopie, uzyskując specjalistyczne wektory bez ogólnych przechwytów modeli.
- Inżynieria funkcji w stylu analogii. `gender_vector = mean(man - woman pairs)`. Odejmij to od innych słów, aby uzyskać oś neutralną pod względem płci. Nadal używany w badaniach nad uczciwością.
- Interpretowalność. 100d jest na tyle małe, że można je wykreślić za pomocą PCA lub t-SNE i faktycznie zobaczyć formujące się klastry.
- Wnioskowanie w dowolnym miejscu musi działać na urządzeniu bez procesora graficznego. Wyszukiwanie Word2Vec to pobieranie jednego wiersza.

### Gdzie zawodzi Word2Vec

Ściana polisemiczna. `bank` ma jeden wektor. `river bank` i `financial bank` udostępniają to. `table` (arkusz kalkulacyjny a meble) udostępnia to. Klasyfikator znajdujący się poniżej nie jest w stanie odróżnić zmysłów od wektora.

Osadzanie kontekstowe (ELMo, BERT, każdy transformator od tego czasu) rozwiązało ten problem, tworząc inny wektor dla każdego wystąpienia słowa w oparciu o otaczający kontekst. To jest przeskok z Word2Vec do BERT: od statycznego do kontekstowego. Faza 7 obejmuje połowę transformatora.

Problem braku słownictwa to kolejna awaria. Word2Vec nigdy nie widział `Zoomer-approved`, jeśli nie było go w danych szkoleniowych. Żadnego powrotu. fastText rozwiązuje ten problem za pomocą kompozycji podsłów (lekcja 04).

## Wyślij to

Zapisz jako `outputs/skill-embedding-probe.md`:

```markdown
---
name: embedding-probe
description: Inspect a word2vec model. Run analogies, find neighbors, diagnose quality.
version: 1.0.0
phase: 5
lesson: 03
tags: [nlp, embeddings, debugging]
---

You probe trained word embeddings to verify they are working. Given a `gensim.models.KeyedVectors` object and a vocabulary, you run:

1. Three canonical analogy tests. `king : man :: queen : woman`. `paris : france :: tokyo : japan`. `walking : walked :: swimming : ?`. Report the top-1 result and its cosine.
2. Five nearest-neighbor tests on domain-specific words the user supplies. Print top-5 neighbors with cosines.
3. One symmetry check. `similarity(a, b) == similarity(b, a)` to within float precision.
4. One degenerate check. If any embedding has a norm below 0.01 or above 100, the model has a training bug. Flag it.

Refuse to declare a model good on analogy accuracy alone. Analogy benchmarks are gameable and do not transfer to downstream tasks. Recommend intrinsic + downstream evaluation together.
```

## Ćwiczenia

1. **Łatwo.** Uruchom pętlę treningową na małym korpusie (20 zdań o kotach i psach). Po 200 epok sprawdź, czy `nearest(vocab, W, W[vocab["cat"]])` zwraca `dog` w pierwszej trójce. Jeśli nie, zwiększ epoki lub słownictwo.
2. **Średni.** Dodaj podpróbkę częstych słów. Słowa o częstotliwości powyżej `10^-5` są usuwane z par uczących z prawdopodobieństwem proporcjonalnym do ich częstotliwości. Zmierz wpływ na podobieństwo rzadkich słów.
3. **Trudne.** Trenuj model w korpusie 20 grup dyskusyjnych. Oblicz dwie osie odchylenia: `he - she` i `doctor - nurse`. Rzuć słowa okupacyjne na obie osie. Podaj, które zawody charakteryzują się największą różnicą w uprzedzeniach. Tego rodzaju sondę stosują badacze uczciwości.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Osadzanie słów | Słowo jako wektor | Gęsta, słabo przyciemniona (zwykle 100-300) reprezentacja wyuczona z kontekstu. |
| Pomiń gram | Sztuczka Word2Vec | Przewiduj słowa kontekstu na podstawie słowa środkowego. Wolniejsze niż CBOW, lepsze dla rzadkich słów. |
| Próbkowanie negatywne | Skrót treningowy | Zamień softmax na pełne słownictwo klasyfikacją binarną względem losowych słów `k`. |
| Osadzanie statyczne | Jeden wektor na słowo | Ten sam wektor niezależnie od kontekstu. Nie udaje się na polisemii. |
| Osadzanie kontekstowe | Wektor kontekstowy | Inny wektor dla każdego wystąpienia w oparciu o otaczające słowa. Co produkują transformatory. |
| OOV | Brak słownictwa | Słowo nie widziane na treningu. Word2Vec nie może utworzyć dla nich wektora. |

## Dalsze czytanie

- [Mikolov i in. (2013). Rozproszone reprezentacje słów i wyrażeń oraz ich skład] (https://arxiv.org/abs/1310.4546) — artykuł o próbkach negatywowych. Krótkie i czytelne.
- [Rong, X. (2014). word2vec Poradnik uczenia się parametrów](https://arxiv.org/abs/1411.2738) — najjaśniejsze wyprowadzenie gradientów, jeśli matematyka w oryginalnym artykule wydaje się gęsta.
- [samouczek Gensim Word2Vec](https://radimrehurek.com/gensim/models/word2vec.html) — ustawienia szkolenia produkcyjnego, które faktycznie działają.