# Embeddingi słów — Word2Vec od podstaw

> Słowo poznaje się po towarzystwie, w jakim się znajduje. Wytrenuj na tej idei płytką sieć neuronową, a otrzymasz bogatą strukturę geometryczną (przestrzeń wektorową).

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 5 · Lekcja 02 (BoW + TF-IDF), Faza 3 · Lekcja 03 (Propagacja wsteczna od podstaw)
**Czas:** ~75 minut

## Problem

TF-IDF traktuje słowa `dog` i `puppy` jako całkowicie odrębne jednostki. Nie „wie”, że oznaczają one niemal to samo. Klasyfikator wytrenowany na słowie `dog` nie potrafi uogólnić wiedzy na słowo `puppy`. Można próbować temu zaradzić, ręcznie tworząc listy synonimów, ale rozwiązanie to zawodzi w przypadku rzadkich terminów, żargonu branżowego czy niespodziewanych języków.

Cel to reprezentacja, w której `dog` i `puppy` leżą blisko siebie w przestrzeni wektorowej. Gdzie operacja `king - man + woman` daje wynik bliski wektorowi `queen`. Gdzie model nauczony na słowie `dog` automatycznie przenosi część tej wiedzy na słowo `puppy`.

Biblioteka Word2Vec dała nam taką przestrzeń. To dwuwarstwowa sieć neuronowa wyszkolona na bilionach tokenów, zaprezentowana w 2013 roku. Architektura ta jest niezwykle prosta, lecz uzyskane dzięki niej wyniki zrewolucjonizowały NLP na kolejną dekadę.

## Pojęcia

**Hipoteza dystrybucyjna** (Firth, 1957): „Słowo poznaje się po towarzystwie, w jakim się obraca”. Jeśli dwa słowa pojawiają się w podobnych kontekstach, prawdopodobnie mają zbliżone znaczenie.

Word2Vec występuje w dwóch wariantach realizujących tę ideę:

- **Skip-gram:** Na podstawie słowa centralnego przewiduje słowa otaczające (kontekstowe). Na przykład `cat -> (the, sat, on)` przy oknie o rozmiarze 2.
- **CBOW (Continuous Bag of Words):** Na podstawie słów otaczających (kontekstu) przewiduje słowo centralne. Na przykład `(the, sat, on) -> cat`.

Skip-gram uczy się wolniej, ale lepiej radzi sobie z rzadkimi słowami. Stał się domyślnym wyborem w większości zastosowań.

Sieć neuronowa ma jedną warstwę ukrytą bez funkcji aktywacji (liniową). Wejściem do sieci jest wektor typu one-hot o długości równej rozmiarowi słownika. Wyjściem jest funkcja softmax obliczana nad całym słownikiem. Po zakończeniu treningu warstwa wyjściowa jest odrzucana. Wagi warstwy ukrytej stanowią poszukiwane embeddingi słów.

```
one-hot(center) ── W ──▶ ukryta (d-dim) ── W' ──▶ softmax(vocab)
                           ^
                    to jest embedding
```

**Problem:** Obliczanie softmaxu dla słownika o rozmiarze ponad 100 tys. pozycji jest niezwykle kosztowne obliczeniowo. Word2Vec stosuje **próbkowanie negatywne** (negative sampling), aby przekształcić to zadanie w klasyfikację binarną: „Czy dane słowo kontekstowe pojawiło się w sąsiedztwie słowa centralnego – tak czy nie?”. Dla każdej pary uczącej losuje się kilka słów negatywnych (które nie współwystępują w kontekście), zamiast obliczać kosztowny softmax dla całego słownika.

## Implementacja krok po kroku

### Krok 1: Przygotowanie par treningowych z korpusu

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

Każda para (słowo centralne, słowo kontekstowe) w obrębie zdefiniowanego okna stanowi pozytywny przykład treningowy.

### Krok 2: Tabele embeddingów

Model przechowuje dwie macierze wag. `W` to tabela embeddingów słów centralnych (ta, którą zachowujemy po treningu). `W'` to tabela słów kontekstowych (zazwyczaj odrzucana, czasem uśredniana z `W`).

```python
import numpy as np

def init_embeddings(vocab_size, dim, seed=0):
    rng = np.random.default_rng(seed)
    W = rng.normal(0, 0.1, size=(vocab_size, dim))
    W_prime = rng.normal(0, 0.1, size=(vocab_size, dim))
    return W, W_prime
```

Stosujemy niewielką losową inicjalizację. W rzeczywistych warunkach słownik rzędu 10 tys. słów i wymiarowość wektora 100 są standardem. Na potrzeby nauki wystarczy słownik złożony z 50 słów i wymiarowość 16, by zaobserwować strukturę geometryczną.

### Krok 3: Optymalizacja z próbkowaniem negatywnym

Dla każdej pozytywnej pary `(center, context)` losujemy `k` słów ze słownika jako przykłady negatywne. Trenujemy model tak, aby iloczyn skalarny `W[center] · W'[context]` był wysoki dla par pozytywnych oraz niski dla par negatywnych.

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

    W_prime[context_idx] -= lr * (pos_score - 1) * v_c
    for i, neg_idx in enumerate(negative_indices):
        W_prime[neg_idx] -= lr * neg_scores[i] * v_c
    W[center_idx] -= lr * grad_center
```

**Zasada działania:** minimalizacja straty logistycznej dla par dodatnich (dążenie do wartości sigmoid bliskiej 1) oraz dla par ujemnych (dążenie do wartości sigmoid bliskiej 0). Gradienty aktualizują wagi w obu macierzach. Pełne wyprowadzenie matematyczne znajduje się w oryginalnej pracy – warto przeanalizować je z kartką i ołówkiem, aby w pełni zrozumieć ten proces. (Uwaga: linijka przypisania `W[context_idx] = W[context_idx]` z oryginalnego kodu została poprawiona na poprawną aktualizację wag macierzy `W_prime` i `W`).

### Krok 4: Trening na korpusie testowym

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

Po wykonaniu odpowiedniej liczby epok na dużym korpusie słowa występujące w podobnych kontekstach uzyskują zbliżone wektory embeddingów. Na miniaturowym korpusie testowym efekt ten będzie ledwo zauważalny, lecz na dużych zbiorach danych tekstowych różnica staje się diametralna.

### Krok 5: Testy analogii

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

Dla gotowych, 300-wymiarowych wektorów Google News:

```python
>>> analogy(vocab, W, "man", "king", "woman")
[('queen', 0.71), ('monarch', 0.62), ('princess', 0.59), ...]
```

`king - man + woman = queen`. Dzieje się tak nie dlatego, że model rozumie znaczenie władzy czy płci, ale dlatego, że wektor `(king - man)` reprezentuje pojęcie „królewskości”, a dodanie go do wektora `woman` prowadzi do obszaru przestrzeni powiązanego z pojęciami żeńsko-królewskimi.

## Zastosowanie w praktyce

Zaimplementowanie Word2Vec od zera służy celom edukacyjnym. W zastosowaniach produkcyjnych standardem jest biblioteka `gensim`.

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

W codziennej pracy rzadko zachodzi potrzeba samodzielnego uczenia modelu Word2Vec od podstaw. Najczęściej korzysta się z gotowych, wytrenowanych wektorów:

- **GloVe (Global Vectors for Word Representation):** Metoda oparta na faktoryzacji globalnej macierzy współwystępowania słów (opracowana na Uniwersytecie Stanforda). Dostępne są wersje 50d, 100d, 200d i 300d. Bardzo dobra baza dla ogólnych zadań NLP. Szczegółowo omówiona w lekcji 04.
- **fastText:** Rozszerzenie Word2Vec opracowane przez Facebooka, które osadza n-gramy znaków. Radzi sobie ze słowami spoza słownika (OOV) dzięki reprezentacji podsłowowej. Szczegółowo omówione w lekcji 04.
- **Wstępnie wytrenowany Word2Vec na zbiorze Google News:** Wektory 300d dla 3 milionów słów, opublikowane w 2013 roku. Wciąż bardzo popularny punkt odniesienia.

### Gdzie Word2Vec wciąż wygrywa (stan na 2026 r.)

- **Szybkie trenowanie modeli dziedzinowych.** Możesz w godzinę wytrenować model na abstraktach medycznych na zwykłym laptopie, uzyskując specjalistyczne wektory bez konieczności pobierania ogromnych modeli ogólnych.
- **Inżynieria cech oparta na relacjach geometrycznych.** Możesz wyznaczyć wektor płci: `gender_vector = mean(wektory_mężczyzn - wektory_kobiet)`, a następnie odjąć go od innych słów, aby zneutralizować ich obciążenie (bias). Metoda ta jest nadal stosowana w badaniach nad etyką i sprawiedliwością sztucznej inteligencji (AI fairness).
- **Wizualizacja i interpretowalność.** Wektory o wymiarowości 100 można łatwo zredukować za pomocą PCA lub t-SNE, co pozwala na bezpośrednią wizualizację i analizę skupisk (klastrów) słów.
- **Wnioskowanie na słabych urządzeniach bez GPU.** Pobranie wektora Word2Vec sprowadza się do prostego odczytu z tablicy (lookup) o złożoności O(1).

### Ograniczenia Word2Vec

1. **Problem wieloznaczności (polisemii).** Słowo `bank` (brzeg rzeki lub instytucja finansowa) ma przypisany tylko jeden statyczny wektor. Podobnie słowo `zamek` (budowla, zapięcie w kurtce lub urządzenie w drzwiach). Klasyfikator końcowy nie jest w stanie rozróżnić tych znaczeń na podstawie samego wektora.
   *Rozwiązanie:* Embeddingi kontekstowe (ELMo, BERT i nowsze modele typu Transformer) generują różne wektory dla tego samego słowa w zależności od kontekstu zdania. Faza 7 omawia budowę transformatorów.

2. **Obsługa słów spoza słownika (OOV).** Word2Vec nie potrafi wygenerować wektora dla słowa, którego nie widział podczas treningu. Biblioteka fastText rozwiązuje to ograniczenie dzięki reprezentacji opartej na podsłowach (lekcja 04).

## Szablon do wdrożenia

Zapisz go jako `outputs/skill-embedding-probe.md`:

```markdown
---
name: embedding-probe
description: Analizuje model Word2Vec. Uruchamia testy analogii, wyszukuje najbliższych sąsiadów, diagnozuje jakość.
version: 1.0.0
phase: 5
lesson: 03
tags: [nlp, embeddings, debugging]
---

Analizujesz przeszkolone embeddingi słów w celu weryfikacji ich poprawnego działania. Otrzymujesz obiekt `gensim.models.KeyedVectors` oraz słownik, a następnie wykonujesz:

1. Trzy klasyczne testy analogii: `king : man :: queen : woman`, `paris : france :: tokyo : japan` oraz `walking : walked :: swimming : ?`. Zwróć najlepszy wynik (top-1) wraz z wartością podobieństwa cosinusowego.
2. Pięć testów najbliższych sąsiadów dla słów z danej domeny dostarczonych przez użytkownika. Wyświetl 5 najbliższych sąsiadów wraz z ich podobieństwem cosinusowym.
3. Jeden test symetrii: upewnij się, że `similarity(a, b) == similarity(b, a)` z dokładnością do precyzji zmiennoprzecinkowej.
4. Jeden test poprawności wartości: jeśli jakikolwiek embedding ma normę poniżej 0.01 lub powyżej 100, oznacza to błąd w procesie uczenia modelu. Zgłoś tę anomalię.

Odmów uznania jakości modelu wyłącznie na podstawie dokładności w testach analogii. Benchmarki analogii bywają podatne na manipulacje (gameable) i nie przekładają się bezpośrednio na skuteczność w zadaniach downstream. Rekomenduj jednoczesne przeprowadzenie ewaluacji wewnętrznej (intrinsic) oraz zewnętrznej (downstream).
```

## Ćwiczenia

1. **Łatwe.** Uruchom pętlę uczenia na małym korpusie (np. 20 zdań o kotach i psach). Po 200 epokach sprawdź, czy wywołanie `nearest(vocab, W, W[vocab["cat"]])` zwraca słowo `dog` w pierwszej trójce najbliższych sąsiadów. Jeśli nie, zwiększ liczbę epok lub rozbuduj korpus.
2. **Średnie.** Zaimplementuj mechanizm podpróbkowania (subsampling) częstych słów. Słowa o częstości powyżej `10^-5` powinny być usuwane z par treningowych z prawdopodobieństwem proporcjonalnym do ich częstości. Zmierz wpływ tej modyfikacji na jakość reprezentacji rzadkich słów.
3. **Trudne.** Wytrenuj model na korpusie 20 Newsgroups. Zdefiniuj dwie osie obciążenia (bias): `he - she` (płeć) oraz `doctor - nurse` (stereotypy zawodowe). Rzutuj nazwy zawodów na obie te osie. Wskaż, które zawody wykazują największe obciążenie stereotypami. Ten rodzaj analizy jest powszechnie stosowany w badaniach nad etyką modeli językowych.

## Kluczowe pojęcia

| Pojęcie | Potoczne rozumienie | Rzeczywiste znaczenie |
|------|-----------------|----------------------|
| Embedding (osadzenie) | Słowo jako wektor | Gęsta reprezentacja wektorowa o niskiej wymiarowości (zazwyczaj 100-300), wyznaczona na podstawie kontekstu. |
| Skip-gram | Wariant Word2Vec | Przewidywanie słów kontekstowych na podstawie słowa centralnego. Wolniejszy w trenowaniu niż CBOW, ale lepiej reprezentuje rzadkie słowa. |
| Negative sampling | Próbkowanie negatywne | Metoda przyspieszająca trening. Zastępuje kosztowny softmax nad całym słownikiem klasyfikacją binarną dla `k` losowych słów negatywnych. |
| Embedding statyczny | Stały wektor słowa | Ta sama reprezentacja niezależnie od kontekstu, w jakim pojawia się słowo. Nie radzi sobie z wieloznacznością (polisemią). |
| Embedding kontekstowy | Zmienny wektor słowa | Inny wektor dla każdego wystąpienia słowa, obliczany na podstawie kontekstu (generowany np. przez modele typu Transformer). |
| OOV (Out-Of-Vocabulary) | Słowo spoza słownika | Wyraz, który nie wystąpił w zbiorze treningowym. Statyczne modele Word2Vec nie potrafią utworzyć dla niego wektora. |

## Dalsze czytanie

- [Mikolov et al. (2013). Distributed Representations of Words and Phrases and their Compositionality](https://arxiv.org/abs/1310.4546) — oryginalna publikacja wprowadzająca negative sampling. Krótka i przystępna.
- [Rong, X. (2014). word2vec Parameter Learning Explained](https://arxiv.org/abs/1411.2738) — bardzo przejrzyste wyprowadzenie matematyczne gradientów dla algorytmu.
- [Gensim Word2Vec Tutorial](https://radimrehurek.com/gensim/models/word2vec.html) — praktyczny poradnik konfiguracji parametrów treningowych dla zastosowań produkcyjnych.
