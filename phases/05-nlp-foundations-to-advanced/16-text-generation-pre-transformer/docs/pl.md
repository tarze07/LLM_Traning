# Generowanie tekstu przed transformatorami — modele języka N-gramowego

> Jeśli jakieś słowo zaskakuje, to model jest zły. Zakłopotanie sprawia, że ​​niespodzianka jest liczbą. Wygładzanie sprawia, że ​​jest to skończone.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 5 · 01 (Przetwarzanie tekstu), Faza 2 · 14 (Naive Bayes)
**Czas:** ~45 minut

## Problem

Przed transformatorami, przed RNN i przed osadzaniem słów model językowy przewidywał następne słowo, zliczając, jak często występowało ono po poprzednich `n-1` słowach. Policz „kot” → „usiadł” 47 razy, „kot” → „skoczył” 12 razy, „kot” → „lodówka” 0 razy. Normalizuj, aby uzyskać rozkład prawdopodobieństwa.

To jest model języka n-gramowego. Obsługiwał każdy moduł rozpoznawania mowy, moduł sprawdzania pisowni i każdy system tłumaczenia maszynowego oparty na frazach od 1980 do 2015 roku. Nadal działa, gdy potrzebne jest tanie modelowanie języka na urządzeniu.

Interesującym problemem jest to, co zrobić z niewidocznymi n-gramami. Model oparty na surowym zliczeniu przypisuje zerowe prawdopodobieństwo niczemu, czego nie widział, co jest katastrofalne, ponieważ zdania są długie i prawie każde długie zdanie zawiera co najmniej jedną niewidoczną sekwencję. Pięćdziesiąt lat badań nad wygładzaniem naprawiło ten problem. Rezultatem jest wygładzenie Knesera-Neya, a nowoczesne głębokie uczenie się odziedziczyło swoją tradycję empiryczną.

## Koncepcja

![Model N-gramowy: zliczanie, wygładzanie, generowanie](../assets/ngram.svg)

**Prawdopodobieństwo N-gramów:** `P(w_i | w_{i-n+1}, ..., w_{i-1})`. Napraw `n` (zwykle 3 dla trygramów, 4 dla 4 gramów). Oblicz z obliczeń:

```text
P(w | context) = count(context, w) / count(context)
```

**Problem zliczania zerowego.** Każdy n-gram nie zaobserwowany podczas uczenia ma prawdopodobieństwo zerowe. Badanie przeprowadzone w 2007 roku na korpusie Browna wykazało, że nawet 4-gramowy model miał 30% wyciągniętych 4-gramowych ładunków, których nie widać podczas treningu. Nie można oceniać żadnego prawdziwego tekstu bez wygładzania.

**Metody wygładzania, według stopnia zaawansowania:**

1. **Laplace (dodaj jeden).** Dodaj 1 do każdego obliczenia. Proste, straszne w rzadkich przypadkach.
2. **Good-Turing.** Przenieś masę prawdopodobieństwa ze zdarzeń o wyższej częstotliwości do zdarzeń niewidocznych w oparciu o częstotliwość częstotliwości.
3. **Interpolacja.** Połącz szacunki n-gramów, (n-1)-gramów itp. z przestrajalnymi wagami.
4. **Wycofanie.** Jeśli liczba n-gramów wynosi zero, wróć do (n-1)-gramów. Wycofanie Katza normalizuje to.
5. **Bezwzględne rabaty.** Odejmij stały rabat `D` od wszystkich obliczeń i przekaż go ponownie do niewidocznych.
6. **Kneser-Ney.** Dyskontowanie absolutne plus sprytny wybór dla modelu niższego rzędu: użyj *prawdopodobieństwa kontynuacji* (w ilu kontekstach pojawia się słowo) zamiast surowej częstotliwości.

Spostrzeżenie Knesera-Neya jest głębokie. „San Francisco” to powszechny bigram. Unigram „Francisco” pojawia się głównie po „San”. Naiwne dyskontowanie bezwzględne daje „Francisco” wysokie prawdopodobieństwo unigramu (ponieważ liczba jest wysoka). Kneser-Ney zauważa, że ​​„Francisco” pojawia się tylko w jednym kontekście i odpowiednio obniża prawdopodobieństwo jego kontynuacji. Wynik: nowatorski bigram kończący się na „Francisco” uzyskuje odpowiednio niskie prawdopodobieństwo.

**Ocena: zakłopotanie.** Wykładnik średniego ujemnego logarytmu wiarygodności na słowo w odłożonym zestawie testowym. Niżej jest lepiej. Zakłopotanie wynoszące 100 oznacza, że ​​model jest tak zdezorientowany, jak gdyby wybierał jednolicie spośród 100 słów.

```text
perplexity = exp(- (1/N) * Σ log P(w_i | context_i))
```

## Zbuduj to

### Krok 1: liczenie trygramów

```python
from collections import Counter, defaultdict

def train_ngram(corpus_tokens, n=3):
    ngrams = Counter()
    contexts = Counter()
    for sentence in corpus_tokens:
        padded = ["<s>"] * (n - 1) + sentence + ["</s>"]
        for i in range(len(padded) - n + 1):
            ctx = tuple(padded[i:i + n - 1])
            word = padded[i + n - 1]
            ngrams[ctx + (word,)] += 1
            contexts[ctx] += 1
    return ngrams, contexts

def raw_probability(ngrams, contexts, context, word):
    ctx = tuple(context)
    if contexts.get(ctx, 0) == 0:
        return 0.0
    return ngrams.get(ctx + (word,), 0) / contexts[ctx]
```

Dane wejściowe to lista tokenizowanych zdań. Dane wyjściowe to liczba n-gramów i liczba kontekstów. `<s>` i `</s>` to granice zdań.

### Krok 2: Wygładzanie Laplace'a

```python
def laplace_probability(ngrams, contexts, vocab_size, context, word):
    ctx = tuple(context)
    numerator = ngrams.get(ctx + (word,), 0) + 1
    denominator = contexts.get(ctx, 0) + vocab_size
    return numerator / denominator
```

Do każdego wyniku dodaj 1. Wygładza, ale nadmiernie przydziela masę niewidocznym wydarzeniom, szkodząc także rzadkim znanym wydarzeniom.

### Krok 3: Kneser-Ney (bigram, interpolowany)

```python
def kneser_ney_bigram_model(corpus_tokens, discount=0.75):
    unigrams = Counter()
    bigrams = Counter()
    unigram_contexts = defaultdict(set)

    for sentence in corpus_tokens:
        padded = ["<s>"] + sentence + ["</s>"]
        for i, w in enumerate(padded):
            unigrams[w] += 1
            if i > 0:
                prev = padded[i - 1]
                bigrams[(prev, w)] += 1
                unigram_contexts[w].add(prev)

    total_unique_bigrams = sum(len(ctx_set) for ctx_set in unigram_contexts.values())
    continuation_prob = {
        w: len(ctx_set) / total_unique_bigrams for w, ctx_set in unigram_contexts.items()
    }

    context_totals = Counter()
    for (prev, w), count in bigrams.items():
        context_totals[prev] += count

    unique_follow = defaultdict(set)
    for (prev, w) in bigrams:
        unique_follow[prev].add(w)

    def prob(prev, w):
        count = bigrams.get((prev, w), 0)
        denom = context_totals.get(prev, 0)
        if denom == 0:
            return continuation_prob.get(w, 1e-9)
        first_term = max(count - discount, 0) / denom
        lambda_prev = discount * len(unique_follow[prev]) / denom
        return first_term + lambda_prev * continuation_prob.get(w, 1e-9)

    return prob
```

Trzy ruchome części. `continuation_prob` uwzględnia „w ilu różnych kontekstach pojawia się to słowo?” (innowacja Knesera-Neya). `lambda_prev` to masa uwolniona w wyniku rabatu, używana do ważenia zwrotu. Ostateczne prawdopodobieństwo to zdyskontowany termin główny plus ważony okres kontynuacji.

### Krok 4: generowanie tekstu z próbkowaniem

```python
import random

def generate(prob_fn, vocab, prefix, max_len=30, seed=0):
    rng = random.Random(seed)
    tokens = list(prefix)
    for _ in range(max_len):
        candidates = [(w, prob_fn(tokens[-1], w)) for w in vocab]
        total = sum(p for _, p in candidates)
        r = rng.random() * total
        acc = 0.0
        for w, p in candidates:
            acc += p
            if r <= acc:
                tokens.append(w)
                break
        if tokens[-1] == "</s>":
            break
    return tokens
```

Próbkowanie proporcjonalne do prawdopodobieństwa. Zawsze daje inną wydajność na ziarno. Aby uzyskać wyniki przypominające wyszukiwanie wiązki, wybierz argmax na każdym kroku (zachłanny) i dodaj małe pokrętło losowości (temperatura).

### Krok 5: zakłopotanie

```python
import math

def perplexity(prob_fn, sentences):
    total_log_prob = 0.0
    total_tokens = 0
    for sentence in sentences:
        padded = ["<s>"] + sentence + ["</s>"]
        for i in range(1, len(padded)):
            p = prob_fn(padded[i - 1], padded[i])
            total_log_prob += math.log(max(p, 1e-12))
            total_tokens += 1
    return math.exp(-total_log_prob / total_tokens)
```

Niżej jest lepiej. W przypadku korpusu Browna dobrze dostrojony 4-gramowy model KN osiąga zakłopotanie w okolicach 140. Transformator LM osiąga 15-30 na tym samym zestawie testowym. Różnica wynosi około 10x. Ta luka jest powodem, dla którego pole posunęło się dalej.

## Użyj tego

- **Klasyczne nauczanie NLP.** Najwyraźniejszy kontakt z wygładzaniem, MLE i zakłopotaniem, jaki możesz uzyskać.
- **KenLM.** Produkcyjna biblioteka n-gramów. Używany jako rejestrator w systemach mowy i MT, gdzie liczy się małe opóźnienie.
- **Autouzupełnianie na urządzeniu.** Modele trygramów na klawiaturach. Nadal.
- **Linie bazowe.** Zawsze obliczaj n-gramowe zakłopotanie LM, zanim zadeklarujesz, że Twój neuronalny LM jest dobry. Jeśli twój transformator nie pokonuje KN znacznie, coś jest nie tak.

## Wyślij to

Zapisz jako `outputs/prompt-lm-baseline.md`:

```markdown
---
name: lm-baseline
description: Zbuduj powtarzalny model bazowy języka n-gramowego przed treningiem neuronowego LM.
phase: 5
lesson: 16
---

Biorąc pod uwagę korpus i docelowe zastosowanie (przewidywanie następnego słowa, ponowna punktacja, poziom bazowy perplexity), wygeneruj:

1. Rząd N-gramów. Trygram dla ogólnego języka angielskiego, 4-gramowy jeśli korpus jest duży, 5-gramowy dla ponownej punktacji mowy.
2. Wygładzanie. Zmodyfikowany Kneser-Ney jest domyślny; Laplace tylko do celów dydaktycznych.
3. Biblioteka. `kenlm` do produkcji, `nltk.lm` do nauczania, własna implementacja tylko do nauki.
4. Ewaluacja. Wyizolowane perplexity przy spójnej tokenizacji między zbiorami treningowymi i testowymi.

Odmów podawania perplexity obliczonego przy użyciu innej tokenizacji między porównywanymi systemami — wartości perplexity można porównywać tylko przy identycznej tokenizacji. Oznacz odsetek OOV (Out-Of-Vocabulary) w zbiorze testowym; KN źle radzi sobie z OOV, chyba że podczas treningu zarezerwujesz specjalny token <UNK>.
```

## Ćwiczenia

1. **Łatwo.** Trenuj trygram LM na korpusie Szekspira składającym się z 1000 zdań. Utwórz 20 zdań. Będą lokalnie wiarygodne, ale globalnie niespójne. To jest demo kanoniczne.
2. **Średni.** Zaimplementuj zakłopotanie w swoim modelu KN w obliczu utrzymującego się rozłamu Szekspira. Porównaj z Laplacem. Powinieneś zobaczyć, że KN obniża zakłopotanie o 30-50%.
3. **Trudne.** Zbuduj korektor pisowni trygramu: biorąc pod uwagę błędnie napisane słowo i jego kontekst, wygeneruj poprawki i uszereguj według prawdopodobieństwa kontekstu pod LM. Oceń korpus pisowni Birkbeck (publiczny).

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| N-gram | Sekwencja słów | Sekwencja `n` kolejnych tokenów. |
| Wygładzanie | Unikanie zer | Ponowne przydzielenie masy prawdopodobieństwa, aby niewidoczne zdarzenia uzyskały prawdopodobieństwo niezerowe. |
| Zakłopotanie | Miernik jakości LM | `exp(-average log-prob)` na wstrzymanych danych. Niżej jest lepiej. |
| Odwrót | Powrót do krótszego kontekstu | Jeśli liczba trygramów wynosi zero, użyj bigramu. Wycofanie się Katza formalizuje to. |
| Knesera-Neya | Najlepsze wygładzanie dla n-gramów | Dyskontowanie bezwzględne + prawdopodobieństwo kontynuacji dla modelu niższego rzędu. |
| Prawdopodobieństwo kontynuacji | Specyficzny dla KN | `P(w)` ważony według liczby kontekstów, w których pojawia się `w`, a nie według surowej liczby. |

## Dalsze czytanie

- [Jurafsky i Martin — Przetwarzanie mowy i języka, rozdział 3 (wersja robocza z 2026 r.)](https://web.stanford.edu/~jurafsky/slp3/3.pdf) — kanoniczne traktowanie n-gramowych LM i wygładzanie.
- [Chen i Goodman (1998). An Empirical Study of Smoothing Techniques for Language Modeling](https://dash.harvard.edu/handle/1/25104739) — artykuł, który ustalił, że Kneser-Ney jest najlepszym n-gramowym wygładzaczem.
- [Kneser i Ney (1995). Ulepszone wsparcie dla modelowania języka M-gramowego](https://ieeexplore.ieee.org/document/479394) — oryginalna praca KN.
- [KenLM](https://kheafield.com/code/kenlm/) — szybki produkcyjny n-gramowy LM, nadal używany w 2026 r. w aplikacjach wrażliwych na opóźnienia.