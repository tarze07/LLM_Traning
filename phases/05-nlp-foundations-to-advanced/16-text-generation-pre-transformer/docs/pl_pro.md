# Generowanie tekstu przed erą transformerów – n-gramowe modele językowe

> Jeśli jakieś słowo zaskakuje model, to znaczy, że model jest słaby. Perpleksja pozwala zmierzyć to zaskoczenie liczbowo, a wygładzanie sprawia, że nie jest ono nieskończone.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 5 · 01 (Przetwarzanie tekstu), Faza 2 · 14 (Naiwny klasyfikator Bayesowski)
**Czas:** ~45 minut

## Problem

Przed erą transformerów, sieci RNN i embeddingów słów, modele językowe przewidywały kolejne słowo na podstawie częstości jego występowania po sekwencji `n-1` poprzednich słów. Przykładowo: zliczamy, ile razy po słowie „kot” wystąpiło słowo „usiadł” (np. 47 razy), „skoczył” (12 razy), a „lodówka” (0 razy), a następnie normalizujemy te wartości, aby otrzymać rozkład prawdopodobieństwa.

Tak właśnie działa n-gramowy model języka. Stanowił on fundament systemów rozpoznawania mowy, korektorów pisowni oraz statystycznych systemów tłumaczenia maszynowego (PBMT) od lat 80. XX wieku aż do roku 2015. Wciąż znajduje zastosowanie wszędzie tam, gdzie wymagane jest lekkie i tanie modelowanie języka bezpośrednio na urządzeniu użytkownika.

Kluczowym wyzwaniem jest postępowanie z niezaobserwowanymi wcześniej n-gramami. Model oparty na surowych statystykach przypisuje zerowe prawdopodobieństwo każdej sekwencji, której nie widział w zbiorze treningowym. Jest to niedopuszczalne, ponieważ w dłuższych zdaniach niemal zawsze pojawia się przynajmniej jedna nowa, nieznana wcześniej sekwencja. Problem ten rozwiązano dzięki trwającym kilkadziesiąt lat badaniom nad tzw. wygładzaniem (smoothing). Ich ukoronowaniem stała się metoda wygładzania Knesera-Neya (Kneser-Ney smoothing), z której empirycznych doświadczeń czerpie także współczesne głębokie uczenie.

## Koncepcja

![Model N-gramowy: zliczanie, wygładzanie, generowanie](../assets/ngram.svg)

**Prawdopodobieństwo n-gramu:** `P(w_i | w_{i-n+1}, ..., w_{i-1})`. Wartość `n` jest ustalona (zwykle 3 dla trygramów, 4 dla 4-gramów). Prawdopodobieństwo oblicza się ze wzoru:

```text
P(w | context) = count(context, w) / count(context)
```

**Problem zerowych częstości (zero probability problem).** Każdy n-gram niezaobserwowany podczas uczenia otrzymuje prawdopodobieństwo zerowe. Badanie z 2007 roku przeprowadzone na Korpusie Browna wykazało, że nawet w modelu 4-gramowym aż 30% napotkanych w zbiorze testowym sekwencji 4-gramowych nie wystąpiło w zbiorze treningowym. Oznacza to, że bez wygładzania ocena jakiegokolwiek rzeczywistego tekstu jest niemożliwa.

**Metody wygładzania (od najprostszych do najbardziej zaawansowanych):**

1. **Wygładzanie Laplace'a (add-one smoothing).** Dodanie 1 do każdego licznika. Metoda prosta, lecz daje bardzo słabe rezultaty przy rzadkich danych.
2. **Estymacja Gooda-Turinga.** Redystrybucja masy prawdopodobieństwa z częściej występujących n-gramów na te niezaobserwowane, w oparciu o liczbę n-gramów o danej częstości (frequency of frequencies).
3. **Interpolacja (Interpolation).** Łączenie estymacji n-gramów, (n-1)-gramów itd. za pomocą wag podlegających dostrojeniu.
4. **Wycofanie (Back-off).** Jeśli licznik n-gramu wynosi zero, model cofa się do (n-1)-gramu. Formalnym rozwinięciem tej koncepcji jest wycofanie Katza (Katz back-off).
5. **Dyskontowanie absolutne (Absolute discounting).** Odjęcie stałej wartości `D` od każdego niezerowego licznika i redystrybucja uwolnionej masy prawdopodobieństwa na zdarzenia niezaobserwowane.
6. **Wygładzanie Knesera-Neya.** Dyskontowanie absolutne połączone z nowatorskim podejściem do modeli niższego rzędu – zamiast surowej częstości stosuje się *prawdopodobieństwo kontynuacji* (continuation probability), czyli liczbę unikalnych kontekstów, w których dane słowo występuje.

Intuicja stojąca za metodą Knesera-Neya jest niezwykle trafna. „San Francisco” to bardzo popularny bigram. Unigram „Francisco” pojawia się w tekstach niemal wyłącznie po słowie „San”. Klasyczne dyskontowanie absolutne przypisałoby słowu „Francisco” wysokie prawdopodobieństwo jako unigramowi (ze względu na dużą liczbę wystąpień). Kneser-Ney zauważa jednak, że „Francisco” pojawia się tylko w jednym specyficznym kontekście, i odpowiednio obniża prawdopodobieństwo jego kontynuacji w innych miejscach. W efekcie nowy bigram kończący się na „Francisco” (np. „auto Francisco”) otrzyma poprawnie niskie prawdopodobieństwo.

**Ocena: Perpleksja (Perplexity).** Definiuje się ją jako eksponent średniej ujemnej wiarygodności logarytmicznej przypadającej na jedno słowo w wydzielonym zbiorze testowym. Im niższa perpleksja, tym lepiej. Perpleksja równa 100 oznacza, że model jest tak samo „zdezorientowany”, jakby na każdym kroku losował słowo z rozkładu jednostajnego spośród 100 możliwości.

```text
perplexity = exp(- (1/N) * Σ log P(w_i | context_i))
```

## Zbuduj to

### Krok 1: Zliczanie trygramów

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

Wejściem jest lista stokenizowanych zdań. Wyjściem są słowniki z częstościami n-gramów oraz kontekstów. Symbole `<s>` i `</s>` oznaczają odpowiednio początek i koniec zdania.

### Krok 2: Wygładzanie Laplace'a (Add-one)

```python
def laplace_probability(ngrams, contexts, vocab_size, context, word):
    ctx = tuple(context)
    numerator = ngrams.get(ctx + (word,), 0) + 1
    denominator = contexts.get(ctx, 0) + vocab_size
    return numerator / denominator
```

Do każdego licznika dodajemy 1. Pozwala to uniknąć zerowych prawdopodobieństw, lecz przenosi zbyt dużą część masy prawdopodobieństwa na zdarzenia niezaobserwowane, zniekształcając prawdopodobieństwa rzadkich, lecz znanych słów.

### Krok 3: Interpolowany model Knesera-Neya dla bigramów

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

Implementacja składa się z trzech głównych elementów. `continuation_prob` określa, w ilu unikalnych kontekstach pojawia się dane słowo (kluczowa innowacja Knesera-Neya). `lambda_prev` reprezentuje masę prawdopodobieństwa zwolnioną dzięki dyskontowaniu, która służy do zważenia wycofania. Ostateczne prawdopodobieństwo to suma zdyskontowanego członu głównego oraz zważonego prawdopodobieństwa kontynuacji.

### Krok 4: Generowanie tekstu metodą próbkowania

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

Próbkowanie odbywa się proporcjonalnie do rozkładu prawdopodobieństwa. Każda wartość ziarna generatora (seed) daje inny wynik. Aby uzyskać zachowanie zbliżone do wyszukiwania wiązkowego (beam search), można na każdym kroku wybierać słowo o najwyższym prawdopodobieństwie (dekodowanie zachłanne/greedy) lub sterować stopniem losowości za pomocą parametru temperatury.

### Krok 5: Perpleksja

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

Im niższa wartość perpleksji, tym lepszy model. Na Korpusie Browna dobrze dostrojony model 4-gramowy z wygładzaniem Knesera-Neya osiąga perpleksję na poziomie około 140. Z kolei model językowy oparty na transformerze na tym samym zbiorze testowym uzyskuje wynik rzędu 15–30. Ta niemal dziesięciokrotna różnica wyjaśnia, dlaczego cała branża przeszła na architektury głębokiego uczenia.

## Zastosowanie

- **Dydaktyka NLP:** Najlepszy sposób na intuicyjne zrozumienie mechanizmów wygładzania, estymacji maksymalnej wiarygodności (MLE) oraz perpleksji.
- **KenLM:** Niezwykle szybka, produkcyjna biblioteka n-gramowa. Stosowana jako model językowy (rescorer) w systemach rozpoznawania mowy i tłumaczenia maszynowego (MT) o niskich wymaganiach dotyczących opóźnień.
- **Autouzupełnianie na urządzeniach klienckich:** Modele trygramowe wciąż napędzają klawiatury w smartfonach ze względu na oszczędność pamięci i energii.
- **Silny punkt odniesienia (Baseline):** Przed ogłoszeniem sukcesu nowego neuronowego modelu języka warto obliczyć perpleksję dla modelu n-gramowego. Jeśli transformer nie osiąga znacząco lepszych wyników niż Kneser-Ney, najprawdopodobniej w implementacji lub procesie uczenia tkwi błąd.

## Zapisywanie szablonu

Zapisz jako `outputs/prompt-lm-baseline.md`:

```markdown
---
name: lm-baseline
description: Zbuduj powtarzalny model bazowy języka n-gramowego przed treningiem neuronowego LM.
phase: 5
lesson: 16
---

Na podstawie korpusu i docelowego zastosowania (przewidywanie kolejnego słowa, rescoring, wyznaczanie bazowej perpleksji) zdefiniuj:

1. Rząd n-gramów: Trygram dla ogólnych tekstów, model 4-gramowy przy dużym korpusie, 5-gramowy do rescoringu w systemach ASR.
2. Metoda wygładzania: Domyślnie zmodyfikowany Kneser-Ney; Laplace wyłącznie w celach edukacyjnych.
3. Biblioteka: `kenlm` do systemów produkcyjnych, `nltk.lm` do celów dydaktycznych, własna implementacja wyłącznie w celach edukacyjnych.
4. Ewaluacja: Obliczanie perpleksji przy zachowaniu identycznej tokenizacji dla zbioru treningowego i testowego.

Nigdy nie porównuj wartości perpleksji obliczonych przy użyciu różnych tokenizatorów — porównania mają sens wyłącznie przy identycznej tokenizacji. Zawsze podawaj odsetek słów spoza słownika (OOV – Out-Of-Vocabulary) w zbiorze testowym. Modele n-gramowe z wygładzaniem KN radzą sobie z OOV słabo, chyba że podczas uczenia jawnie uwzględniono specjalny token <UNK>.
```

## Ćwiczenia praktyczne

1. **Poziom łatwy:** Wytrenuj trygramowy model języka na korpusie dzieł Szekspira składającym się z 1000 zdań. Wygeneruj 20 zdań. Zauważysz, że będą one lokalnie poprawne syntaktycznie, ale globalnie pozbawione spójności semantycznej. To klasyczny eksperyment demonstracyjny.
2. **Poziom średni:** Zaimplementuj obliczanie perpleksji dla swojego modelu Knesera-Neya i przetestuj go na wydzielonym zbiorze testowym z korpusu Szekspira. Porównaj wyniki z wygładzaniem Laplace'a. Wygładzanie KN powinno zmniejszyć perpleksję o 30–50%.
3. **Poziom trudny:** Zbuduj trygramowy korektor pisowni. Dla błędnie zapisanego słowa oraz jego kontekstu wygeneruj listę potencjalnych poprawek i uszereguj je według prawdopodobieństwa generowanego przez model języka. Przeprowadź ewaluację na publicznym korpusie błędów Birkbeck.

## Kluczowe pojęcia

| Termin | Potoczne określenie | Znaczenie precyzyjne |
|------|-----------------|----------------------|
| N-gram | Sekwencja słów | Sekwencja `n` kolejnych tokenów. |
| Wygładzanie | Unikanie zer | Redystrybucja masy prawdopodobieństwa, dzięki której zdarzenia niezaobserwowane otrzymują niezerowe prawdopodobieństwo. |
| Perpleksja | Miernik jakości LM | `exp(-average log-prob)` na wydzielonym zbiorze danych. Im niższa wartość, tym lepsza jakość modelu. |
| Wycofanie | Powrót do krótszego kontekstu | Jeśli licznik n-gramu wynosi zero, model korzysta z prawdopodobieństwa bigramu. Koncepcję tę formalizuje metoda wycofania Katza (Katz back-off). |
| Kneser-Ney | Najlepsze wygładzanie dla n-gramów | Dyskontowanie absolutne połączone z prawdopodobieństwem kontynuacji dla modeli niższego rzędu. |
| Prawdopodobieństwo kontynuacji | Specyficzny dla KN | Prawdopodobieństwo unigramu `P(w)` określane na podstawie liczby unikalnych kontekstów, w których występuje słowo `w`, a nie jego całkowitej liczby wystąpień. |

## Literatura uzupełniająca

- [Jurafsky i Martin — Przetwarzanie mowy i języka, rozdział 3 (wersja robocza z 2026 r.)](https://web.stanford.edu/~jurafsky/slp3/3.pdf) — kanoniczne ujęcie n-gramowych modeli językowych i metod wygładzania.
- [Chen i Goodman (1998). An Empirical Study of Smoothing Techniques for Language Modeling](https://dash.harvard.edu/handle/1/25104739) — publikacja wykazująca empiryczną wyższość wygładzania Knesera-Neya nad innymi technikami.
- [Kneser i Ney (1995). Improved backing-off for M-gram language modeling](https://ieeexplore.ieee.org/document/479394) — oryginalny artykuł naukowy wprowadzający metodę KN.
- [KenLM](https://kheafield.com/code/kenlm/) — szybka, wydajna biblioteka n-gramowa do zastosowań produkcyjnych, wciąż szeroko wykorzystywana w 2026 r.
