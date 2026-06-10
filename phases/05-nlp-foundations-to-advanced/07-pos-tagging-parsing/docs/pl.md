# Tagowanie POS i analiza syntaktyczna

> Gramatyka była przez jakiś czas niemodna. Następnie każdy potok LLM musiał zweryfikować ekstrakcję strukturalną i wszystko wróciło.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 5 · 01 (Przetwarzanie tekstu), Faza 2 · 14 (Naive Bayes)
**Czas:** ~45 minut

## Problem

Lekcja 01 obiecała, że lematyzacja wymaga znacznika będącego częścią mowy. Nie wiedząc, że `running` jest czasownikiem, lemmatyzator nie może go zredukować do `run`. Bez wiedzy, że `better` jest przymiotnikiem, nie można go zredukować do `good`.

Ta obietnica ukrywała całe podpole. Znakowanie części mowy przypisuje kategorie gramatyczne. Analiza syntaktyczna odtwarza strukturę drzewa zdania: które słowo modyfikuje które, który czasownik reguluje które argumenty. Klasyczne NLP spędziło dwadzieścia lat na udoskonalaniu obu. Następnie głębokie uczenie połączyło je w zadanie polegające na klasyfikacji tokenów na wstępnie wyszkolonym transformatorze, a społeczność badawcza poszła dalej.

Nie społeczność stosowana. Każdy potok strukturalnego wyodrębniania nadal wykorzystuje pod maską punkty sprzedaży i drzewa zależności. Wygenerowany przez LLM kod JSON jest sprawdzany pod kątem ograniczeń gramatycznych. Systemy odpowiadania na pytania rozkładają zapytania za pomocą analizy zależności. Osoby oceniające jakość tłumaczenia maszynowego sprawdzają wyrównanie drzew analizy.

Warto wiedzieć. Ta lekcja przedstawia zestawy tagów, linie bazowe i moment, w którym przestajesz wdrażać od zera i wywołujesz spaCy.

## Koncepcja

**Tagowanie POS** oznacza każdy token kategorią gramatyczną. Zestaw tagów **Penn Treebank (PTB)** jest domyślnym ustawieniem w języku angielskim. 36 znaczników z rozróżnieniami, które zwykły czytelnik uważa za wybredne: `NN` rzeczownik w liczbie pojedynczej, `NNS` rzeczownik w liczbie mnogiej, `NNP` rzeczownik właściwy w liczbie pojedynczej, `VBD` czasownik w czasie przeszłym, `VBZ` czasownik 3. osoba liczby pojedynczej, czas teraźniejszy i tak dalej. Zestaw znaczników **Uniwersalne zależności (UD)** jest bardziej zgrubny (17 znaczników) i niezależny od języka; stał się domyślnym dla pracy międzyjęzykowej.

```
The/DET cats/NOUN were/AUX running/VERB at/ADP 3pm/NOUN ./PUNCT
```

**Przetwarzanie syntaktyczne** tworzy drzewo. Dwa główne style:

- **Analiza okręgów wyborczych.** Wyrażenia rzeczownikowe, czasownikowe i przyimkowe zagnieżdżają się w sobie. Dane wyjściowe to drzewo kategorii nieterminalnych (NP, VP, PP) ze słowami w postaci liści.
- **Analiza zależności.** Każde słowo ma jedno słowo główne, od którego zależy, oznaczone relacją gramatyczną. Dane wyjściowe to drzewo, w którym każda krawędź jest potrójna (głowa, zależna, relacja).

Analiza zależności zwyciężyła w 2010 roku, ponieważ pozwala na czyste uogólnianie na różne języki, zwłaszcza te z wolną kolejnością słów.

```
running is ROOT
cats is nsubj of running
were is aux of running
at is prep of running
3pm is pobj of at
```

## Zbuduj to

### Krok 1: linia bazowa najczęściej używanego tagu

Najgłupszy tager POS, jaki działa. Dla każdego słowa przewiduj tag, który miał najczęściej podczas szkolenia.

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

W korpusie Browna ta linia bazowa osiąga dokładność ~85%. Niedobrze, ale podłoga poniżej której żaden poważny model nie powinien spaść.

### Krok 2: tager bigramu HMM

Modeluj łączne prawdopodobieństwo ciągu:

```
P(tags, words) = prod P(tag_i | tag_{i-1}) * P(word_i | tag_i)
```

Dwie tabele: prawdopodobieństwa przejścia (oznaczenie podane w poprzednim znaczniku), prawdopodobieństwa emisji (oznaczenie podane w słowie). Oszacuj oba na podstawie obliczeń za pomocą wygładzania Laplace'a. Dekodowanie za pomocą Viterbiego (programowanie dynamiczne po siatce znaczników).

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

Bigram HMM na Brownie osiąga celność ~93%. Skok z 85% do 93% to głównie prawdopodobieństwo przejścia — model dowiaduje się, że `DET NOUN` jest powszechne, a `NOUN DET` jest rzadkie.

### Krok 3: dlaczego współczesne tagery to pokonują

Prawdopodobieństwa przejścia + emisji są lokalne. Nie potrafią uchwycić, że `saw` jest rzeczownikiem w wyrażeniu „Kupiłem piłę”, ale czasownikiem w przypadku „Widziałem film”. CRF z dowolnymi cechami (przyrostek, kształt słowa, słowo przed i po, samo słowo) osiąga ~97%. BiLSTM-CRF lub transformator osiąga ~98%+.

Pułap tego zadania wyznaczany jest przez brak zgody komentatora. Ludzcy komentatorzy zgadzają się z tym w około 97% przypadków w Penn Treebank. Modele przekraczające 98% prawdopodobnie nadmiernie dopasowują zestaw testowy.

### Krok 4: szkic analizy zależności

Pełna analiza zależności od podstaw jest poza zakresem; kanoniczne leczenie podręcznikowe znajduje się u Jurafsky'ego i Martina. Dwie klasyczne rodziny, które warto znać:

- **Parsery oparte na przejściach** (arc-eager, arc-standard) działają jak parser z redukcją przesunięcia: czytają tokeny, przesuwają je na stos i stosują akcje redukcji, które tworzą łuki. Chciwe dekodowanie jest szybkie. Klasyczną implementacją jest MaltParser. Nowoczesna wersja neuronowa: parser oparty na przejściach Chena i Manninga.
- Parsery **oparte na grafach** (algorytm Eisnera, biaffine Dozata-Manninga) oceniają każdą możliwą krawędź zależną od głowy i wybierają maksymalne drzewo rozpinające. Wolniej, ale dokładniej.

W przypadku większości prac aplikacyjnych zadzwoń do spaCy:

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

Przeczytaj kolumnę `dep` od dołu do góry, a struktura gramatyczna zdania wypadnie.

## Użyj tego

Każda produkcyjna biblioteka NLP dostarcza parsery punktów sprzedaży i zależności w ramach standardowego potoku.

- **spaCy** (`en_core_web_sm` / `md` / `lg` / `trf`). Szybki, dokładny, zintegrowany z tokenizacją + NER + lematyzacją. `token.tag_` (Penn), `token.pos_` (UD), `token.dep_` (relacja zależności).
- **Stanford NLP (strofa)**. Następca CoreNLP firmy Stanford. Najnowocześniejsza wersja w ponad 60 językach.
- **trankit**. Oparta na transformatorze, dobra dokładność UD.
- **NLTK**. `pos_tag`. Użyteczny, powolny, starszy. Dobra do nauczania.

### Gdzie to nadal ma znaczenie w 2026 r

- **Lematyzacja.** Lekcja 01 wymaga POS, aby poprawnie lematyzować. Zawsze.
- **Strukturalna ekstrakcja z wyników LLM.** Sprawdź, czy wygenerowane zdanie spełnia ograniczenia gramatyczne (np. zgodność podmiot-orzeczenie, wymagane modyfikatory).
- **Tonacja oparta na aspektach.** Analiza zależności informuje, który przymiotnik modyfikuje który rzeczownik.
- **Zrozumienie zapytania.** „filmy wyreżyserowane przez Wesa Andersona z Billem Murrayem w roli głównej” rozkładają się na strukturalne ograniczenia poprzez analizę.
- **Transfer międzyjęzykowy.** Tagi UD i relacje zależności są niezależne od języka, umożliwiając ustrukturyzowaną analizę nowych języków z zerowym strzałem.
- **Potoki o małej mocy obliczeniowej.** Jeśli nie możesz wysłać transformatora, POS + analiza zależności + gazeter pozwolą ci zaskakująco daleko.

## Wyślij to

Zapisz jako `outputs/skill-grammar-pipeline.md`:

```markdown
---
name: grammar-pipeline
description: Zaprojektuj klasyczny potok POS + analizy składniowej dla docelowego zadania NLP.
version: 1.0.0
phase: 5
lesson: 07
tags: [nlp, pos, parsing]
---

Biorąc pod uwagę zadanie docelowe (ekstrakcja informacji, weryfikacja przepisywania, dekompozycja zapytań, lematyzacja), wygeneruj:

1. Zestaw znaczników do użycia. Penn Treebank dla starszych potoków tylko w języku angielskim, Universal Dependencies dla wielojęzycznych lub międzyjęzycznych.
2. Biblioteka. spaCy do większości wdrożeń produkcyjnych, stanza dla rozwiązań wielojęzycznych o jakości akademickiej, trankit dla najwyższej dokładności UD. Podaj dokładny identyfikator modelu.
3. Wzór integracji. Pokaż 3-5 linii kodu wywołujących bibliotekę i pobierających potrzebne atrybuty (`.pos_`, `.dep_`, `.head`).
4. Tryb awarii do testowania. Niejednoznaczność rzeczownik-czasownik (`saw`, `book`, `can`) oraz niejednoznaczność przyłączeń fraz przyimkowych (PP-attachment) to klasyczne pułapki. Pobierz 20 próbek i oceń wzrokowo.

Odmów zalecania budowania własnego parsera od podstaw. Tworzenie parserów to projekt badawczy, a nie zadanie aplikacyjne. Oznacz każdy potok, który korzysta ze znaczników POS bez obsługi małych/wielkich liter, jako podatny na błędy.
```

## Ćwiczenia

1. **Łatwe.** Używając linii bazowej najczęstszego znacznika w małym korpusie oznaczonym tagami (np. podzbiór Browna NLTK), zmierz dokładność wstrzymanych zdań. Sprawdź wynik ~85%.
2. **Średni.** Trenuj powyższy bigram HMM i raportuj precyzję/zapamiętywanie poszczególnych tagów. Które tagi HMM najbardziej myli?
3. **Trudne.** Użyj analizy zależności spaCy, aby wyodrębnić trójki podmiot-czasownik-dopełnienie z próbki składającej się z 1000 zdań. Oceń 50 ręcznie oznaczonych trójek. Dokumentuj tam, gdzie ekstrakcja się nie udaje (często strony bierne, koordynacje i tematy pominięte).

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Etykieta POS | Typ słowa | Kategoria gramatyczna. PTB ma 36; UD ma 17. |
| Bank drzew Penn | Standardowy zestaw tagów | Specyficzne dla języka angielskiego. Drobnoziarniste czasy czasownika i liczba rzeczownika. |
| Zależności uniwersalne | Wielojęzyczny zestaw tagów | Grubszy niż PTB; neutralny językowo; domyślne dla pracy międzyjęzykowej. |
| Analiza zależności | Drzewo zdań | Każde słowo ma jedną głowę, każda krawędź ma relację gramatyczną. |
| Viterbiego | Programowanie dynamiczne | Znajduje sekwencję znaczników o najwyższym prawdopodobieństwie, biorąc pod uwagę emisje i przejścia. |

## Dalsze czytanie

- [Jurafsky i Martin — Przetwarzanie mowy i języka, rozdziały 8 i 18] (https://web.stanford.edu/~jurafsky/slp3/) — kanoniczne podręcznikowe podejście do POS i parsowania.
- [Projekt Universal Zależności](https://universaldependentages.org/) — międzyjęzyczny zestaw tagów i zbiór drzew, używany przez każdy wielojęzyczny parser.
- [przewodnik po funkcjach językowych spaCy](https://spacy.io/usage/linguistic-features) — praktyczne informacje dotyczące każdego atrybutu widocznego w `Token`.
- [Chen i Manning (2014). Szybki i dokładny analizator zależności wykorzystujący sieci neuronowe](https://nlp.stanford.edu/pubs/emnlp2014-depparser.pdf) — artykuł, który wprowadził parsery neuronowe do głównego nurtu.