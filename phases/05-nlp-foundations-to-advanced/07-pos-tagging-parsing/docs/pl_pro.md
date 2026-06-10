# Tagowanie części mowy (POS) i analiza składniowa

> Przez pewien czas gramatyka wydawała się odchodzić do lamusa. Jednak gdy zaistniała potrzeba weryfikacji strukturalnej danych wyjściowych z modeli LLM, klasyczna analiza składniowa powróciła do łask.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 5 · Lekcja 01 (Przetwarzanie tekstu), Faza 2 · Lekcja 14 (Naiwny klasyfikator Bayesa)
**Czas:** ~45 minut

## Problem

W lekcji 01 wspomnieliśmy, że poprawna lematyzacja wymaga określenia części mowy (tagu POS). Bez wiedzy, że wyraz `running` pełni rolę czasownika, lematyzator nie potrafi sprowadzić go do formy `run`. Podobnie słowo `better` bez oznaczenia jako przymiotnik nie zostanie poprawnie zredukowane do `good`.

Za tym prostym stwierdzeniem kryje się rozbudowany dział nauki. Tagowanie części mowy (POS tagging) polega na przypisywaniu wyrazom ich kategorii gramatycznych. Analiza składniowa (parsing) rekonstruuje strukturę drzewiastą zdania, określając relacje nadrzędności i podrzędności (np. które słowo modyfikuje inne lub które argumenty podlegają danemu czasownikowi). Badacze NLP przez dwadzieścia lat rozwijali te techniki, aż głębokie uczenie sprowadziło je do problemu klasyfikacji tokenów (token classification) za pomocą modeli typu Transformer.

Inaczej wygląda to w zastosowaniach praktycznych. Potoki ekstrakcji danych strukturalnych stale wykorzystują tagi POS oraz drzewa zależności. Tekst generowany przez modele LLM (np. formaty JSON) jest weryfikowany pod kątem poprawności gramatycznej, systemy QA (Question Answering) analizują zapytania za pomocą drzew zależności, a ewaluacja jakości tłumaczenia maszynowego opiera się na porównywaniu struktur składniowych.

W tej lekcji omówimy standardowe zestawy tagów, modele bazowe oraz wskażemy moment, w którym zamiast pisać kod od zera, należy skorzystać z biblioteki spaCy.

## Pojęcia

**Tagowanie POS** przypisuje każdemu tokenowi jego klasę gramatyczną. Tradycyjnym standardem dla języka angielskiego jest zestaw tagów **Penn Treebank (PTB)**. Składa się on z 36 drobnoziarnistych znaczników, np. `NN` (rzeczownik w liczbie pojedynczej), `NNS` (rzeczownik w liczbie mnogiej), `NNP` (rzeczownik właściwy w liczbie pojedynczej), `VBD` (czasownik w czasie przeszłym), czy `VBZ` (czasownik w 3. osobie liczby pojedynczej czasu teraźniejszego). Alternatywą jest standard **Universal Dependencies (UD)**, który wprowadza bardziej zgrubny podział (17 tagów) i jest niezależny od języka, dzięki czemu stał się standardem w zadaniach wielojęzycznych.

```
The/DET cats/NOUN were/AUX running/VERB at/ADP 3pm/NOUN ./PUNCT
```

**Analiza składniowa (parsing)** pozwala na zbudowanie struktury drzewiastej. Wyróżniamy dwa podejścia:

- **Analiza składników bezpośrednich (constituency parsing):** Wyrażenia rzeczownikowe, czasownikowe czy przyimkowe zagnieżdżają się w sobie hierarchicznie. Wynikiem jest drzewo, w którym węzłami wewnętrznymi są kategorie gramatyczne (NP, VP, PP), a liśćmi poszczególne słowa.
- **Analiza zależnościowa (dependency parsing):** Każdy wyraz w zdaniu (z wyjątkiem głównego czasownika) zależy od dokładnie jednego słowa nadrzędnego (head). Wynikiem jest skierowane drzewo zależności, w którym krawędzie określają relacje składniowe (np. podmiot, dopełnienie).

Podejście zależnościowe zyskało dominującą pozycję w latach 2010., ponieważ pozwala na spójne reprezentowanie różnych języków – zwłaszcza tych o swobodnym szyku zdań.

```
running is ROOT
cats is nsubj of running
were is aux of running
at is prep of running
3pm is pobj of at
```

## Implementacja krok po kroku

### Krok 1: Model bazowy: najczęszcza klasa (Most Frequent Tag)

Najprostsze podejście: przypisywanie słowu tagu POS, który występował z nim najczęściej w zbiorze treningowym.

```python
from collections import Counter, defaultdict

def train_mft(train_examples):
    word_tag_counts = defaultdict(Counter)
    all_tags = Counter()
    for tokens, tags in train_examples:
        for token, tag in zip(tokens, tags):
            word_tag_counts[token.lower()][tag] += 1
            all_tags[tag] += 1
    word_best = {w: c.most_common(1)[0][0] for w, c in word_tag_counts.items()}
    default_tag = all_tags.most_common(1)[0][0]
    return word_best, default_tag

def predict_mft(tokens, word_best, default_tag):
    return [word_best.get(t.lower(), default_tag) for t in tokens]
```

Na korpusie Browna model ten osiąga około 85% dokładności. Jest to dolny próg skuteczności, który każdy zaawansowany system powinien z łatwością przekroczyć.

### Krok 2: Tagger bigramowy oparty na Ukrytym Modelu Markowa (HMM)

Modelujemy łączne prawdopodobieństwo sekwencji tagów i słów:

```
P(tags, words) = prod P(tag_i | tag_{i-1}) * P(word_i | tag_i)
```

Wyznaczamy dwie macierze: prawdopodobieństwa przejść (prawdopodobieństwo wystąpienia tagu pod warunkiem tagu poprzedzającego) oraz prawdopodobieństwa emisji (prawdopodobieństwo wygenerowania słowa przy danym tagu). Obie macierze są szacowane na podstawie liczby wystąpień z zastosowaniem wygładzania Laplace'a. Znalezienie optymalnej ścieżki tagów (dekodowanie) odbywa się przy użyciu algorytmu Viterbiego.

```python
import math

def train_hmm(train_examples, alpha=0.01):
    transitions = defaultdict(Counter)
    emissions = defaultdict(Counter)
    tags = set()
    vocab = set()

    for tokens, ts in train_examples:
        prev = "<BOS>"
        for token, tag in zip(tokens, ts):
            transitions[prev][tag] += 1
            emissions[tag][token.lower()] += 1
            tags.add(tag)
            vocab.add(token.lower())
            prev = tag
        transitions[prev]["<EOS>"] += 1

    return transitions, emissions, tags, vocab

def log_prob(table, given, key, smooth_denom, alpha):
    return math.log((table[given].get(key, 0) + alpha) / smooth_denom)

def viterbi(tokens, transitions, emissions, tags, vocab, alpha=0.01):
    tags_list = list(tags)
    n = len(tokens)
    V = [[0.0] * len(tags_list) for _ in range(n)]
    back = [[0] * len(tags_list) for _ in range(n)]

    for j, tag in enumerate(tags_list):
        em_denom = sum(emissions[tag].values()) + alpha * (len(vocab) + 1)
        tr_denom = sum(transitions["<BOS>"].values()) + alpha * (len(tags_list) + 1)
        tr = log_prob(transitions, "<BOS>", tag, tr_denom, alpha)
        em = log_prob(emissions, tag, tokens[0].lower(), em_denom, alpha)
        V[0][j] = tr + em
        back[0][j] = 0

    for i in range(1, n):
        for j, tag in enumerate(tags_list):
            em_denom = sum(emissions[tag].values()) + alpha * (len(vocab) + 1)
            em = log_prob(emissions, tag, tokens[i].lower(), em_denom, alpha)
            best_prev = 0
            best_score = -1e30
            for k, prev_tag in enumerate(tags_list):
                tr_denom = sum(transitions[prev_tag].values()) + alpha * (len(tags_list) + 1)
                tr = log_prob(transitions, prev_tag, tag, tr_denom, alpha)
                score = V[i - 1][k] + tr + em
                if score > best_score:
                    best_score = score
                    best_prev = k
            V[i][j] = best_score
            back[i][j] = best_prev

    last_best = max(range(len(tags_list)), key=lambda j: V[n - 1][j])
    path = [last_best]
    for i in range(n - 1, 0, -1):
        path.append(back[i][path[-1]])
    return [tags_list[j] for j in reversed(path)]
```

Tagger HMM oparty na bigramach osiąga na korpusie Browna dokładność około 93%. Wyraźny wzrost skuteczności (z 85% do 93%) wynika z uwzględnienia prawdopodobieństwa przejść – model uczy się m.in., że po przedimku (`DET`) bardzo często występuje rzeczownik (`NOUN`), natomiast odwrotna kolejność jest mało prawdopodobna.

### Krok 3: Dlaczego nowoczesne taggery osiągają lepsze wyniki

Prawdopodobieństwa przejść i emisji w HMM mają charakter wyłącznie lokalny. Nie potrafią one poprawnie zróżnicować słowa `saw` (piła – rzeczownik vs widziałem – czasownik) na podstawie szerszego kontekstu. Zastosowanie modeli CRF z bogatym zestawem cech pozwala osiągnąć dokładność na poziomie 97%. Z kolei modele BiLSTM-CRF oraz Transformer osiągają skuteczność przekraczającą 98%.

Górną granicę skuteczności wyznacza zgodność między sędziami (inter-annotator agreement). Dla korpusu Penn Treebank wynosi ona około 97%. Wyniki modeli przekraczające tę wartość zazwyczaj oznaczają przeuczenie (overfitting) do zbioru testowego.

### Krok 4: Metody analizy składniowej

Pełna implementacja parsera zależnościowego wykracza poza ramy tej lekcji (szczegółowy opis można znaleźć w podręczniku Jurafsky'ego i Martina). Warto jednak znać dwie główne rodziny parserów:

- **Parsery oparte na przejściach (transition-based parsers):** Działają na zasadzie parsera typu shift-reduce. Czytają tokeny, odkładają je na stos i wykonują akcje (np. przejście, redukcja, utworzenie łuku zależności). Są bardzo szybkie. Klasycznym przykładem jest MaltParser, a nowoczesnym wariantem neuronowym – parser Chena i Manninga.
- **Parsery oparte na grafach (graph-based parsers):** Oceniają prawdopodobieństwo wystąpienia krawędzi dla każdej możliwej pary słów i wyznaczają maksymalne drzewo rozpinające (Maximum Spanning Tree). Są wolniejsze, lecz dokładniejsze (np. parser biaffine Dozata i Manninga).

W większości zastosowań inżynieryjnych korzysta się z gotowych narzędzi takich jak spaCy:

```python
import spacy

nlp = spacy.load("en_core_web_sm")
doc = nlp("The cats were running at 3pm.")
for token in doc:
    print(f"{token.text:10s} tag={token.tag_:5s} pos={token.pos_:6s} dep={token.dep_:10s} head={token.head.text}")
```

```
The        tag=DT    pos=DET    dep=det        head=cats
cats       tag=NNS   pos=NOUN   dep=nsubj      head=running
were       tag=VBD   pos=AUX    dep=aux        head=running
running    tag=VBG   pos=VERB   dep=ROOT       head=running
at         tag=IN    pos=ADP    dep=prep       head=running
3pm        tag=NN    pos=NOUN   dep=pobj       head=at
.          tag=.     pos=PUNCT  dep=punct      head=running
```

Analiza kolumny `dep` pozwala jednoznacznie odczytać gramatyczną strukturę zdania.

## Zastosowanie w praktyce

Każda produkcyjna biblioteka NLP dostarcza parsery tagów POS i zależności w ramach standardowego potoku przetwarzania.

- **spaCy** (`en_core_web_sm` / `md` / `lg` / `trf`): Szybki, dokładny potok integrujący tokenizację, NER, lematyzację i gramatykę. Udostępnia atrybuty `.tag_` (zbiór Penn Treebank), `.pos_` (Universal Dependencies) oraz `.dep_` (relacja zależności).
- **Stanza (Stanford NLP)**: Następca CoreNLP firmy Stanford. Oferuje najwyższą jakość modeli dla ponad 60 języków.
- **Trankit**: Biblioteka oparta na architekturze Transformer, zoptymalizowana pod kątem standardu Universal Dependencies.
- **NLTK**: Moduł `pos_tag` jest łatwy w użyciu, lecz wolny. Przydatny głównie do celów edukacyjnych.

### Gdzie analiza składniowa ma znaczenie w 2026 roku

- **Dokładna lematyzacja:** Poprawne sprowadzenie słów do formy słownikowej wymaga znajomości części mowy (lekcja 01).
- **Weryfikacja danych wyjściowych z modeli LLM:** Sprawdzanie, czy wygenerowane teksty spełniają określone reguły gramatyczne i syntaktyczne.
- **Analiza sentymentu oparta na aspektach (ABSA):** Drzewo zależności wskazuje, który przymiotnik określa dany rzeczownik.
- **Parsowanie zapytań:** Rozbicie zapytania typu „filmy wyreżyserowane przez Wesa Andersona z Billem Murrayem” na strukturę filtrów bazodanowych.
- **Potoki o niskich zasobach obliczeniowych:** W środowiskach bez kart GPU lekki parser zależności i słownik pozwalają na szybką ekstrakcję informacji.

## Szablon do wdrożenia

Zapisz go jako `outputs/skill-grammar-pipeline.md`:

```markdown
---
name: grammar-pipeline
description: Zaprojektuj klasyczny potok POS + analizy składniowej dla docelowego zadania NLP.
version: 1.0.0
phase: 5
lesson: 07
tags: [nlp, pos, parsing]
---

Jesteś doradcą ds. klasycznej analizy składniowej i tagowania w NLP. Na podstawie opisu zadania (ekstrakcja informacji, weryfikacja poprawności, dekompozycja zapytań, lematyzacja) określ:

1. Rekomendowany zestaw tagów: Penn Treebank dla potoków wyłącznie anglojęzycznych, Universal Dependencies dla zadań wielojęzycznych.
2. Wybór biblioteki i modelu (np. spaCy dla rozwiązań produkcyjnych, Stanza dla zaawansowanych potoków wielojęzycznych, Trankit dla maksymalnej precyzji w standardzie UD) wraz z podaniem dokładnego identyfikatora modelu.
3. Przykładową integrację: 3-5 linijek kodu ilustrujących pobieranie atrybutów (`.pos_`, `.dep_`, `.head`).
4. Jeden kluczowy przypadek testowy (np. niejednoznaczność rzeczownik-czasownik dla słów `saw`, `book`, `can` lub błędy w określaniu zasięgu fraz przyimkowych – PP-attachment). Zaproponuj weryfikację na próbie 20 zdań.

Odmów rekomendowania budowy własnego parsera od podstaw (jest to zadanie naukowe, a nie inżynieryjne). Oznacz potoki wykorzystujące tagowanie POS bez uprzedniej normalizacji wielkości liter jako podatne na błędy.
```

## Ćwiczenia

1. **Łatwe.** Wykorzystaj model bazowy MFT (najczęstsza klasa) na podzbiorze korpusu Browna (dostępnego w NLTK) i zmierz dokładność klasyfikacji na zbiorze testowym (powinieneś uzyskać wynik w okolicach 85%).
2. **Średnie.** Wytrenuj tagger bigramowy HMM i przeanalizuj macierz pomyłek. Wskaż, które części mowy są ze sobą najczęściej mylone przez model HMM i dlaczego.
3. **Trudne.** Wykorzystaj parser zależnościowy spaCy do wyodrębnienia trójek (podmiot, czasownik, dopełnienie) z korpusu 1000 zdań. Przeanalizuj ręcznie 50 losowych wyników i opisz typowe błędy (np. w przypadku zdań w stronie biernej lub struktur współrzędnych).

## Kluczowe pojęcia

| Pojęcie | Potoczne rozumienie | Rzeczywiste znaczenie |
|------|-----------------|----------------------|
| Tag POS | Część mowy | Klasa gramatyczna wyrazu. Zestaw PTB zawiera 36 tagów, standard UD – 17. |
| Penn Treebank (PTB) | Standard tagów angielskich | Dedykowany dla języka angielskiego zestaw uwzględniający drobnoziarniste różnice (np. czasy czasowników, liczba mnoga/pojedyncza). |
| Universal Dependencies (UD) | Uniwersalny standard | Niezależny językowo, zgrubny podział tagów i zależności stosowany w projektach wielojęzycznych. |
| Analiza zależnościowa | Struktura zależnościowa | Drzewiasta reprezentacja zdania, w której każdy token podlega pod słowo nadrzędne (head) za pomocą określonej relacji. |
| Algorytm Viterbiego | Programowanie dynamiczne | Algorytm wyznaczający najbardziej prawdopodobną sekwencję ukrytych stanów (tagów) na podstawie macierzy przejść i emisji. |

## Dalsze czytanie

- [Jurafsky, D., Martin, J. H. Speech and Language Processing (Chapters 8 & 18)](https://web.stanford.edu/~jurafsky/slp3/) — podstawowe źródło wiedzy akademickiej z zakresu tagowania i parsowania.
- [Universal Dependencies Project](https://universaldependencies.org/) — oficjalna dokumentacja uniwersalnego standardu tagowania i drzew zależności.
- [spaCy linguistic features guide](https://spacy.io/usage/linguistic-features) — praktyczny poradnik wykorzystania atrybutów gramatycznych w tokenach spaCy.
- [Chen, D., Manning, C. (2014). A Fast and Accurate Dependency Parser Using Neural Networks](https://nlp.stanford.edu/pubs/emnlp2014-depparser.pdf) — kamień milowy we wdrożeniu sieci neuronowych do parserów zależnościowych.
