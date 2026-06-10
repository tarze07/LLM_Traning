# Osadzanie GloVe, FastText i Subword

> Word2Vec przeszkolił jedno osadzanie na słowo. GloVe rozłożył na czynniki macierz współwystępowań. FastText osadził elementy. BPE zmostkowane do transformatorów.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 5 · 03 (Word2Vec od podstaw)
**Czas:** ~45 minut

## Problem

Word2Vec pozostawił dwa otwarte pytania.

Po pierwsze, istniał równoległy kierunek badań, w którym bezpośrednio rozłożono na czynniki macierz współwystępowań (LSA, HAL), zamiast przeprowadzać aktualizacje online z pominięciem gramów. Czy podejście iteracyjne programu Word2Vec było zasadniczo lepsze, czy też różnica wynikała z artefaktu sposobu, w jaki obie metody radziły sobie z liczeniem? **GloVe** odpowiedział, że: faktoryzacja macierzy ze starannie dobraną stratą pasuje lub przewyższa Word2Vec, a szkolenie jest tańsze.

Po drugie, żadna z metod nie miała historii dla słów, których nigdy nie widziała. `Zoomer-approved`, `dogecoin`, dowolny rzeczownik własny powstały w zeszłym tygodniu, każda odmieniona forma rzadkiego rdzenia. **FastText** naprawił ten problem poprzez osadzenie n-gramów znaków: słowo jest sumą jego części, w tym morfemów, więc nawet słowa spoza słownika otrzymują rozsądny wektor.

Po trzecie, kiedy pojawiły się transformatory, kwestia ponownie się zmieniła. Słowniki na poziomie słów obejmują około miliona haseł; prawdziwy język jest bardziej otwarty. **Kodowanie parami bajtów (BPE)** i jego krewni rozwiązali ten problem, ucząc się słownictwa składającego się z częstych jednostek podsłów, które obejmuje wszystko. Każdy nowoczesny tokenizator dla każdego nowoczesnego LLM jest tokenizatorem podsłów.

Ta lekcja omawia wszystkie trzy, a następnie wyjaśnia, po co sięgnąć i kiedy.

## Koncepcja

**GloVe (wektory globalne).** Zbuduj macierz współwystępowania słów `X` gdzie `X[i][j]` określa, jak często słowo `j` pojawia się w kontekście słowa `i`. Trenuj wektory w taki sposób, że `v_i · v_j + b_i + b_j ≈ log(X[i][j])`. Zważ stratę, aby częste pary nie dominowały. Zrobione.

**FastText.** Słowo to suma jego znaków w n-gramach plus samo słowo. `where` zmienia się na `<wh, whe, her, ere, re>, <where>`. Słowo wektor jest sumą tych wektorów składowych. Trenuj jako Word2Vec. Korzyści: niewidoczne słowa (`whereupon`) powstają ze znanych n-gramów.

**BPE (kodowanie par bajtów).** Zacznij od słownika składającego się z pojedynczych bajtów (lub znaków). Policz każdą sąsiadującą parę w korpusie. Połącz najczęstszą parę w nowy token. Powtórz dla `k` iteracji. Wynik: słownictwo składające się z `k + 256` tokenów, w których częste sekwencje (`ing`, `tion`, `the`) to pojedyncze tokeny, a rzadkie słowa są podzielone na znane części. Każde zdanie symbolizuje coś.

## Zbuduj to

### GloVe: rozłóż na czynniki macierz współwystępowań

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

Dwa poruszające elementy, które warto nazwać. Funkcja ważenia `f(x) = (x/x_max)^alpha` zmniejsza wagę bardzo częstych par (takich jak `(the, and)`), tak aby nie zdominowały one straty. Ostateczne osadzenie to suma tabel `W` (w środku) i `W_tilde` (kontekst). Sumowanie obu jest opublikowaną sztuczką, która zwykle osiąga lepsze wyniki przy użyciu tylko jednego.

### FastText: osadzanie uwzględniające podsłowa

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

Każde słowo jest reprezentowane przez zbiór n-gramów (zwykle od 3 do 6 znaków). Słowo osadzanie jest sumą jego n-gramowych osadzania. Aby trenować pomijanie gramów, podłącz to tam, gdzie Word2Vec użył pojedynczego wektora.

```python
def fasttext_vector(word, ngram_table):
    grams = char_ngrams(word)
    vecs = [ngram_table[g] for g in grams if g in ngram_table]
    if not vecs:
        return None
    return np.sum(vecs, axis=0)
```

W przypadku niewidocznego słowa nadal otrzymasz wektor, o ile znane są niektóre jego n-gramy. `whereupon` udostępnia `<wh`, `her`, `ere` i `<where` z `where`, więc oba lądują blisko siebie.

### BPE: nauczono się słownictwa podsłowa

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

Pierwsza iteracja łączy najczęściej sąsiadującą parę. Po wystarczającej liczbie iteracji częste podciągi (`low`, `est`, `tion`) stają się pojedynczymi tokenami, a rzadkie słowa łamią się czysto.

Prawdziwi tokenizatorzy GPT/BERT/T5 uczą się fuzji 30 tys.-100 tys. Wynik: dowolny tekst tokenizuje się w sekwencję znanych identyfikatorów o ograniczonej długości, bez OOV.

## Użyj tego

W praktyce rzadko trenujesz którykolwiek z nich samodzielnie. Ładujesz wstępnie wyszkolone punkty kontrolne.

```python
import fasttext.util
fasttext.util.download_model("en", if_exists="ignore")
ft = fasttext.load_model("cc.en.300.bin")
print(ft.get_word_vector("whereupon").shape)
print(ft.get_word_vector("zoomerapproved").shape)
```

Dla tokenizacji podsłów w stylu BPE w epoce transformatorów:

```python
from transformers import AutoTokenizer

tok = AutoTokenizer.from_pretrained("gpt2")
print(tok.tokenize("unbelievably tokenized"))
```

```
['un', 'bel', 'iev', 'ably', 'Ġtoken', 'ized']
```

Przedrostek `Ġ` wyznacza granice słów (konwencja GPT-2). Każdy nowoczesny tokenizer to wariant BPE, WordPiece (BERT) lub SentencePiece (T5, LLaMA).

### Kiedy wybrać który

| Sytuacja | Wybierz |
|----------|------|
| Wstępnie przeszkolone wektory słów ogólnego przeznaczenia, nie jest wymagana tolerancja OOV | Rękawiczka 300d |
| Wstępnie wytrenowane wektory słów ogólnego przeznaczenia, muszą obsługiwać błędy ortograficzne/neologizmy/języki bogate morfologicznie | Szybki Tekst |
| Wszystko, co wchodzi do transformatora (trening lub wnioskowanie) | Niezależnie od tokenizera, z którym model jest dostarczany. Nigdy nie zamieniaj. |
| Szkolenie własnego modelu językowego od podstaw | Najpierw przeszkol tokenizer BPE lub SentencePiece w swoim korpusie |
| Klasyfikacja tekstu produkcyjnego za pomocą modelu liniowego | Nadal TF-IDF. Lekcja 02. |

## Wyślij to

Zapisz jako `outputs/skill-embeddings-picker.md`:

```markdown
---
name: tokenizer-picker
description: Wybierz podejście do tokenizacji dla nowego modelu językowego lub potoku tekstu.
version: 1.0.0
phase: 5
lesson: 04
tags: [nlp, tokenization, embeddings]
---

Biorąc pod uwagę zadanie i opis zbioru danych, wygeneruj:

1. Strategię tokenizacji (poziom słowa, BPE, WordPiece, SentencePiece, poziom bajtów). Powód w jednym zdaniu.
2. Docelowy rozmiar słownictwa (np. 32k dla LM tylko w języku angielskim, 64k-100k dla wielojęzycznego).
3. Wywołanie biblioteki z dokładnym poleceniem szkolenia. Podaj nazwę biblioteki. Wypisz argumenty.
4. Jedną pułapkę dotyczącą powtarzalności. Niedopasowanie tokenizatora do modelu to najczęstszy cichy błąd na produkcji; wskaż, która para musi być używana razem.

Odmów polecania szkolenia niestandardowego tokenizatora, gdy użytkownik dostraja (fine-tuning) wstępnie wytrenowany LLM. Odmów polecania tokenizacji na poziomie słów dla jakiegokolwiek modelu przeznaczonego do wnioskowania na produkcji. Oznacz korpusy w językach innych niż angielski / korzystające z wielu alfabetów jako wymagające SentencePiece z rezerwowym powrotem do bajtów.
```

## Ćwiczenia

1. **Łatwe.** Uruchom `char_ngrams("playing")` i `char_ngrams("played")`. Oblicz nakładanie się Jaccarda dwóch zbiorów n-gramów. Powinieneś zobaczyć istotne wspólne fragmenty (`pla`, `lay`, `play`), dlatego FastText dobrze przenosi się pomiędzy wariantami morfologicznymi.
2. **Średni.** Rozszerz `learn_bpe`, aby śledzić rozwój słownictwa. Wykreśl liczbę tokenów na znak w korpusie jako funkcję liczby połączeń. Na początku powinieneś zobaczyć szybką kompresję, asymptotyczną w pobliżu ~ 2-3 znaków na token.
3. **Trudny.** Trenuj BPE łączący 1 km na wszystkich dziełach Szekspira. Porównaj tokenizację popularnych słów z rzadkimi rzeczownikami własnymi. Zmierz średnie tokeny na słowo przed i po. Napisz, co Cię zaskoczyło.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Macierz współwystępowań | Tabela częstości występowania słów | `X[i][j]` = jak często słowo `j` pojawia się w oknie wokół słowa `i`. |
| Podsłowo | Kawałek słowa | Znak n-gram (FastText) lub wyuczony token (BPE/WordPiece/SentencePiece). |
| BPE | Kodowanie par bajtów | Iteracyjne łączenie najczęściej sąsiadujących par, aż słownictwo osiągnie docelowy rozmiar. |
| OOV | Brak słownictwa | Słowo, którego modelka nigdy nie widziała. Błąd Word2Vec/GloVe. FastText i BPE sobie z tym radzą. |
| BPE na poziomie bajtu | BPE na surowych bajtach | Schemat GPT-2. Słownictwo zaczyna się od 256 bajtów, więc nic nie jest nigdy OOV. |

## Dalsze czytanie

- [Pennington, Socher, Manning (2014). GloVe: Global Vectors for Word Representation](https://nlp.stanford.edu/pubs/glove.pdf) — artykuł GloVe, siedem stron, wciąż najlepsze wyprowadzenie straty.
- [Bojanowski i in. (2017). Wzbogacanie wektorów słów o informacje o podsłowach](https://arxiv.org/abs/1607.04606) — FastText.
- [Sennrich, Haddow, Brzoza (2016). Neural Machine Translation of Rare Words with Subword Units](https://arxiv.org/abs/1508.07909) — artykuł, który wprowadził BPE do współczesnego NLP.
– [Podsumowanie tokenizera Hugging Face](https://huggingface.co/docs/transformers/tokenizer_summary) — czym w praktyce różnią się BPE, WordPiece i SentencePiece.