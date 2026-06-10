# Embeddingi GloVe, FastText i jednostki podsłowowe

> Word2Vec trenował jeden statyczny embedding na słowo. GloVe rozłożył na czynniki macierz współwystępowania. FastText wprowadził osadzenia n-gramów znaków. BPE stworzyło pomost dla modelów typu Transformer.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 5 · Lekcja 03 (Word2Vec od podstaw)
**Czas:** ~45 minut

## Problem

Model Word2Vec pozostawił badaczy z dwoma otwartymi pytaniami.

Po pierwsze, istniał równoległy nurt badawczy oparty na bezpośredniej faktoryzacji globalnej macierzy współwystępowania (np. LSA, HAL) zamiast iteracyjnych aktualizacji w locie (jak w Skip-gram). Pojawiło się pytanie: czy iteracyjne podejście Word2Vec było fundamentalnie lepsze, czy też różnica wynikała jedynie ze sposobu zliczania słów? Projekt **GloVe** udowodnił, że faktoryzacja macierzy z odpowiednio zaprojektowaną funkcją straty dorównuje lub przewyższa Word2Vec, a jej trening jest wydajniejszy.

Po secondly, żadna z tych metod nie radziła sobie ze słowami, których nie widziała w trakcie treningu (OOV – Out-Of-Vocabulary). Przykładem są neologizmy typu `Zoomer-approved` czy `dogecoin`, a także rzadkie formy odmiany znanych rdzeni. **FastText** rozwiązał ten problem przez osadzanie n-gramów znaków: wektor słowa jest sumą wektorów jego części składowych (w tym morfemów), dzięki czemu nawet wyrazy spoza słownika otrzymują sensowną reprezentację.

Po trzecie, wraz z pojawieniem się modeli typu Transformer, podejście do tokenizacji uległo całkowitej zmianie. Słowniki na poziomie słów musiałyby obejmować miliony haseł, a żywy język stale ewoluuje. **Kodowanie parami bajtów (BPE)** oraz pokrewne metody rozwiązały ten problem poprzez budowanie słownika złożonego z najczęstszych jednostek podsłowowych (subwords), co pozwala na zapisanie dowolnego słowa. Obecnie każdy nowoczesny tokenizator w dużych modelach językowych (LLM) działa na poziomie podsłów.

W tej lekcji szczegółowo omówimy te trzy koncepcje i wskażemy, kiedy stosować każdą z nich.

## Pojęcia

**GloVe (Global Vectors):** Buduje globalną macierz współwystępowania słów `X`, w której element `X[i][j]` określa, jak często słowo `j` pojawia się w oknie kontekstowym słowa `i`. Wektory są trenowane tak, aby iloczyn skalarny oraz biasy spełniały zależność `v_i · v_j + b_i + b_j ≈ log(X[i][j])`. Wprowadzona jest funkcja wagowa, aby bardzo częste pary słów nie zdominowały wyniku.

**FastText:** Słowo jest reprezentowane jako suma swoich n-gramów znakowych oraz samego słowa ujętego w specjalne nawiasy. Na przykład słowo `where` jest rozbijane na `<wh`, `whe`, `her`, `ere`, `re>`, a także cały wyraz `<where>`. Wektor słowa stanowi sumę wektorów tych n-gramów. Sam trening przebiega analogicznie do Word2Vec. Zaleta: wektor dla nieznanego słowa (np. `whereupon`) powstaje przez złożenie wektorów znanych n-gramów.

**BPE (Byte Pair Encoding):** Proces rozpoczyna się od słownika zawierającego pojedyncze znaki (lub bajty). Następnie zlicza się wystąpienia wszystkich sąsiadujących par w korpusie tekstowym i łączy najczęstszą parę w nowy token. Kroki te powtarza się przez `k` iteracji. Wynikiem jest słownik o rozmiarze `k + 256` tokenów, w którym częste sekwencje (np. `ing`, `tion`, `the`) stają się pojedynczymi tokenami, a rzadkie wyrazy są dzielone na znane segmenty. Dowolny tekst może zostać zakodowany za pomocą tak powstałego słownika bez wystąpienia błędów braku słowa.

## Implementacja krok po kroku

### GloVe: Faktoryzacja macierzy współwystępowania

```python
import numpy as np
from collections import Counter

def build_cooccurrence(docs, window=5):
    pair_counts = Counter()
    vocab = {}
    for doc in docs:
        for token in doc:
            if token not in vocab:
                vocab[token] = len(vocab)
    for doc in docs:
        indexed = [vocab[t] for t in doc]
        for i, center in enumerate(indexed):
            for j in range(max(0, i - window), min(len(indexed), i + window + 1)):
                if i != j:
                    distance = abs(i - j)
                    pair_counts[(center, indexed[j])] += 1.0 / distance
    return vocab, pair_counts

def glove_train(vocab, pair_counts, dim=16, epochs=100, lr=0.05, x_max=100, alpha=0.75, seed=0):
    n = len(vocab)
    rng = np.random.default_rng(seed)
    W = rng.normal(0, 0.1, size=(n, dim))
    W_tilde = rng.normal(0, 0.1, size=(n, dim))
    b = np.zeros(n)
    b_tilde = np.zeros(n)

    for epoch in range(epochs):
        for (i, j), x_ij in pair_counts.items():
            weight = (x_ij / x_max) ** alpha if x_ij < x_max else 1.0
            diff = W[i] @ W_tilde[j] + b[i] + b_tilde[j] - np.log(x_ij)
            coef = weight * diff

            grad_W_i = coef * W_tilde[j]
            grad_W_tilde_j = coef * W[i]
            W[i] -= lr * grad_W_i
            W_tilde[j] -= lr * grad_W_tilde_j
            b[i] -= lr * coef
            b_tilde[j] -= lr * coef

    return W + W_tilde
```

Dwa istotne elementy wdrożeniowe: funkcja wagowa `f(x) = (x/x_max)^alpha` ogranicza wpływ bardzo częstych par słów (np. `(the, and)`), aby nie zdominowały one funkcji straty. Ostateczny wektor słowa stanowi sumę macierzy `W` (embedding centralny) oraz `W_tilde` (embedding kontekstowy). Sumowanie obu macierzy to sprawdzony zabieg, który zazwyczaj poprawia wyniki w porównaniu z użyciem tylko jednej z nich.

### FastText: Embeddingi oparte na podsłowach

```python
def char_ngrams(word, n_min=3, n_max=6):
    wrapped = f"<{word}>"
    grams = {wrapped}
    for n in range(n_min, n_max + 1):
        for i in range(len(wrapped) - n + 1):
            grams.add(wrapped[i:i + n])
    return grams
```

```python
>>> char_ngrams("where")
{'<where>', '<wh', 'whe', 'her', 'ere', 're>', '<whe', 'wher', 'here', 'ere>', '<wher', 'where', 'here>'}
```

Słowo jest reprezentowane przez zbiór n-gramów znakowych (zazwyczaj o długości od 3 do 6 znaków). Wektor słowa jest sumą wektorów jego n-gramów. Aby wytrenować model Skip-gram w tym wariancie, podstawiamy tę sumę w miejsce pojedynczego wektora słowa w klasycznym algorymie Word2Vec.

```python
def fasttext_vector(word, ngram_table):
    grams = char_ngrams(word)
    vecs = [ngram_table[g] for g in grams if g in ngram_table]
    if not vecs:
        return None
    return np.sum(vecs, axis=0)
```

Dzięki temu dla nieznanego słowa wciąż otrzymamy wektor, o ile znane są niektóre jego n-gramy. Wyraz `whereupon` współdzieli np. `<wh`, `her`, `ere` oraz `<where` ze słowem `where`, dzięki czemu reprezentacje obu wyrazów leżą blisko siebie.

### BPE: Budowanie słownika podsłów

```python
def learn_bpe(corpus, k_merges):
    vocab = Counter()
    for word, freq in corpus.items():
        tokens = tuple(word) + ("</w>",)
        vocab[tokens] = freq

    merges = []
    for _ in range(k_merges):
        pair_freq = Counter()
        for tokens, freq in vocab.items():
            for a, b in zip(tokens, tokens[1:]):
                pair_freq[(a, b)] += freq
        if not pair_freq:
            break
        best = pair_freq.most_common(1)[0][0]
        merges.append(best)

        new_vocab = Counter()
        for tokens, freq in vocab.items():
            new_tokens = []
            i = 0
            while i < len(tokens):
                if i + 1 < len(tokens) and (tokens[i], tokens[i + 1]) == best:
                    new_tokens.append(tokens[i] + tokens[i + 1])
                    i += 2
                else:
                    new_tokens.append(tokens[i])
                    i += 1
            new_vocab[tuple(new_tokens)] = freq
        vocab = new_vocab
    return merges

def apply_bpe(word, merges):
    tokens = list(word) + ["</w>"]
    for a, b in merges:
        new_tokens = []
        i = 0
        while i < len(tokens):
            if i + 1 < len(tokens) and tokens[i] == a and tokens[i + 1] == b:
                new_tokens.append(a + b)
                i += 2
            else:
                new_tokens.append(tokens[i])
                i += 1
        tokens = new_tokens
    return tokens
```

```python
>>> corpus = Counter({"low": 5, "lower": 2, "newest": 6, "widest": 3})
>>> merges = learn_bpe(corpus, k_merges=10)
>>> apply_bpe("lowest", merges)
['low', 'est</w>']
```

Każda kolejna iteracja łączy najczęściej występującą parę sąsiadujących tokenów. Po wykonaniu odpowiedniej liczby kroków częste podciągi znaków (np. `low`, `est`, `tion`) stają się samodzielnymi tokenami, a rzadkie wyrazy są dzielone na mniejsze, znane i poprawne cząstki.

Rzeczywiste tokenizatory stosowane w modelach GPT, BERT czy T5 uczą się od 30 do 100 tysięcy takich scaleń. W efekcie każdy tekst jest dzielony na sekwencję znanych identyfikatorów bez generowania błędów OOV.

## Zastosowanie w praktyce

W codziennej pracy rzadko zachodzi potrzeba samodzielnego trenowania tych algorytmów – zazwyczaj ładuje się gotowe modele.

```python
import fasttext.util
fasttext.util.download_model("en", if_exists="ignore")
ft = fasttext.load_model("cc.en.300.bin")
print(ft.get_word_vector("whereupon").shape)
print(ft.get_word_vector("zoomerapproved").shape)
```

Tokenizacja podsłowa w bibliotece Transformers:

```python
from transformers import AutoTokenizer

tok = AutoTokenizer.from_pretrained("gpt2")
print(tok.tokenize("unbelievably tokenized"))
```

```
['un', 'bel', 'iev', 'ably', 'Ġtoken', 'ized']
```

Znak `Ġ` oznacza spację (konwencja wprowadzona w GPT-2). Każdy nowoczesny tokenizer to wariant algorytmów BPE, WordPiece (stosowanego w BERT) lub SentencePiece (stosowanego w T5 oraz modelach LLaMA).

### Wybór odpowiedniej metody

| Scenariusz | Rekomendacja |
|----------|------|
| Wstępnie wytrenowane wektory ogólnego przeznaczenia bez konieczności obsługi słów OOV | GloVe 300d |
| Wstępnie wytrenowane wektory z obsługą błędów, neologizmów i języków o bogatej fleksji | fastText |
| Dane wejściowe do modeli typu Transformer | Użyj wyłącznie tokenizera dostarczonego fabrycznie z danym modelem. Nigdy go nie podmieniaj. |
| Trening nowego modelu językowego od podstaw | Wytrenuj najpierw dedykowany tokenizer BPE lub SentencePiece na swoim korpusie tekstowym. |
| Produkcyjna klasyfikacja tekstu za pomocą modeli liniowych | TF-IDF (lekcja 02). |

## Szablon do wdrożenia

Zapisz go jako `outputs/skill-embeddings-picker.md`:

```markdown
---
name: tokenizer-picker
description: Wybierz podejście do tokenizacji dla nowego modelu językowego lub potoku tekstu.
version: 1.0.0
phase: 5
lesson: 04
tags: [nlp, tokenization, embeddings]
---

Na podstawie opisu zadania i zbioru danych określ:

1. Rekomendowaną strategię tokenizacji (poziom słów, BPE, WordPiece, SentencePiece lub poziom bajtów) wraz z jednozdaniowym uzasadnieniem.
2. Docelowy rozmiar słownika (np. 32 tys. dla modeli jednojęzycznych angielskich, 64 tys. - 100 tys. dla modeli wielojęzycznych).
3. Konkretne wywołanie biblioteki wraz z parametrami treningowymi.
4. Zidentyfikowanie jednej kluczowej pułapki wdrożeniowej (np. cichy błąd niedopasowania tokenizatora do modelu, wskazując, które elementy muszą bezwzględnie współpracować).

Odmów polecania trenowania nowego tokenizatora w przypadku dostrajania (fine-tuning) istniejących modeli LLM. Odmów polecania tokenizacji na poziomie słów dla modeli wdrażanych produkcyjnie. Wyraźnie zaznacz, że teksty wielojęzyczne lub korzystające z wielu alfabetów wymagają użycia SentencePiece z obsługą bajtów jako fallback.
```

## Ćwiczenia

1. **Łatwe.** Wyznacz zbiory n-gramów dla słów `playing` oraz `played` za pomocą `char_ngrams`. Oblicz współczynnik podobieństwa Jaccarda dla tych zbiorów. Wynik wykaże wysoki stopień pokrycia, co wyjaśnia zdolność modelu fastText do uogólniania informacji między formami fleksyjnymi.
2. **Średnie.** Rozbuduj funkcję `learn_bpe` o analizę stopnia kompresji korpusu. Wykreśl średnią liczbę tokenów przypadających na słowo w zależności od liczby wykonanych scaleń. Zaobserwujesz szybki spadek długości sekwencji na początku procesu, dążący asymptotycznie do średniej wartości 2-3 znaków na token.
3. **Trudne.** Wytrenuj tokenizer BPE wykonujący 1000 scaleń na komplecie dzieł Szekspira. Porównaj sposób tokenizacji słów powszechnych z rzadkimi nazwami własnymi. Oblicz i porównaj średnią liczbę tokenów przypadających na wyraz przed i po treningu. Zredaguj wnioski z eksperymentu.

## Kluczowe pojęcia

| Pojęcie | Potoczne rozumienie | Rzeczywiste znaczenie |
|------|-----------------|----------------------|
| Macierz współwystępowania | Tabela powiązań słów | Globalna macierz, gdzie `X[i][j]` określa siłę współwystępowania słowa `j` w otoczeniu słowa `i`. |
| Podsłowo (subword) | Cząstka słowa | N-gram znakowy (fastText) lub wyznaczony jednostkowy token słownikowy (BPE, WordPiece, SentencePiece). |
| BPE | Kodowanie par bajtów | Algorytm budowania słownika przez iteracyjne scalanie najczęstszych par sąsiadujących znaków/tokenów. |
| OOV (Out-Of-Vocabulary) | Słowo spoza słownika | Słowo nieobecne w zbiorze treningowym. Stanowi problem dla modeli Word2Vec/GloVe, ale jest obsługiwane przez fastText i tokenizatory podsłowowe. |
| Byte-level BPE | BPE na poziomie bajtów | Standard zastosowany np. w GPT-2. Słownik startowy bazuje na 256 surowych bajtach, co eliminuje problem wystąpienia słów spoza słownika. |

## Dalsze czytanie

- [Pennington, Socher, Manning (2014). GloVe: Global Vectors for Word Representation](https://nlp.stanford.edu/pubs/glove.pdf) — artykuł wprowadzający GloVe z dokładnym wyprowadzeniem funkcji straty.
- [Bojanowski et al. (2017). Enriching Word Vectors with Subword Information](https://arxiv.org/abs/1607.04606) — oficjalny artykuł o bibliotece fastText.
- [Sennrich, Haddow, Birch (2016). Neural Machine Translation of Rare Words with Subword Units](https://arxiv.org/abs/1508.07909) — kluczowa publikacja wprowadzająca BPE do współczesnych systemów neuronowych.
- [Hugging Face Tokenizer Summary](https://huggingface.co/docs/transformers/tokenizer_summary) — praktyczne porównanie algorytmów BPE, WordPiece i SentencePiece.
