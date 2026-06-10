# Przetwarzanie tekstu — tokenizacja, stemming, lematyzacja

> Język jest ciągły. Modele są dyskretne. Przetwarzanie wstępne jest mostem.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 2 · 14 (Naiwny Bayes)
**Czas:** ~45 minut

## Problem

Modelka nie może przeczytać „Koty biegały”. Odczytuje liczby całkowite.

Każdy system NLP rozpoczyna się od tych samych trzech pytań. Gdzie zaczyna się słowo. Jaki jest rdzeń słowa. Jak traktować „bieganie”, „bieganie” i „bieganie” jako to samo, gdy pomaga, i jako różne rzeczy, gdy nie pomaga.

Jeśli źle tokenizujesz, model uczy się na śmieciach. Jeśli Twój tokenizator traktuje `don't` jako jeden token, ale `do n't` jako dwa, dystrybucja szkoleń zostanie rozdzielona. Jeśli Twój rdzeń zwinie się `organization` i `organ` do tego samego rdzenia, modelowanie tematyczne umrze. Jeśli Twój lemmatyzator potrzebuje kontekstu części mowy, ale go nie podasz, czasowniki będą traktowane jak rzeczowniki.

W tej lekcji omówiono od podstaw trzy etapy przetwarzania wstępnego, a następnie pokazano, jak NLTK i spaCy wykonują tę samą pracę, dzięki czemu można zobaczyć kompromisy.

## Koncepcja

Trzy operacje. Każdy ma zadanie i tryb awarii.

**Tokenizacja** dzieli ciąg na tokeny. „Token” jest celowo niejasny, ponieważ odpowiednia szczegółowość zależy od zadania. Poziom słów dla klasycznego NLP. Podsłowo dla transformatorów. Znak dla języków bez białych znaków.

**Wybijanie** kotletów przyrostków z regułami. Szybki, agresywny, głupi. `running -> run`. `organization -> organ`. Ten drugi to tryb awaryjny.

**Lematyzacja** redukuje słowo do jego formy słownikowej, wykorzystując wiedzę gramatyczną. Wolniejsze, dokładne, wymaga tabeli przeglądowej lub analizatora morfologicznego. `ran -> run` (musi wiedzieć, że „ran” to czas przeszły słowa „run”). `better -> good` (trzeba znać formy porównawcze).

Praktyczna zasada. Zastanów się, kiedy liczy się prędkość i tolerujesz hałas (indeksowanie wyszukiwania, przybliżona klasyfikacja). Lematyzuj, gdy znaczenie ma znaczenie (odpowiadanie na pytania, wyszukiwanie semantyczne, wszystko, co przeczyta użytkownik).

## Zbuduj to

### Krok 1: tokenizator słów regularnych

Najprostszy przydatny tokenizator dzieli się na znaki inne niż alfanumeryczne, zachowując interpunkcję jako własne tokeny. Nie doskonały, nie ostateczny, ale działa w jednej linii.

```python
import re

def tokenize(text):
    return re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?|[0-9]+|[^\sA-Za-z0-9]", text)
```

Trzy wzorce w kolejności pierwszeństwa. Słowa z opcjonalnym wewnętrznym apostrofem (`don't`, `it's`). Czyste liczby. Dowolny pojedynczy znak niealfanumeryczny inny niż białe znaki jako samodzielny token (znak interpunkcyjny).

```python
>>> tokenize("The cats weren't running at 3pm.")
['The', 'cats', "weren't", 'running', 'at', '3', 'pm', '.']
```

Tryby awarii, które należy zauważyć. `3pm` dzieli się na `['3', 'pm']`, ponieważ naprzemiennie korzystaliśmy z ciągów liter i cyfr. Wystarczający do większości zadań. Adresy URL, e-maile, hashtagi – wszystko się psuje. Do produkcji dodaj wzory przed ogólnymi.

### Krok 2: stemmer Portera (tylko krok 1a)

Pełny algorytm Portera ma pięć faz reguł. Sam krok 1a omawia najczęstsze przyrostki w języku angielskim i uczy wzoru.

```python
def stem_step_1a(word):
    if word.endswith("sses"):
        return word[:-2]
    if word.endswith("ies"):
        return word[:-2]
    if word.endswith("ss"):
        return word
    if word.endswith("s") and len(word) > 1:
        return word[:-1]
    return word
```

```python
>>> [stem_step_1a(w) for w in ["caresses", "ponies", "caress", "cats"]]
['caress', 'poni', 'caress', 'cat']
```

Przeczytaj zasady od góry do dołu. Reguła `ies -> i` wyjaśnia, dlaczego `ponies -> poni`, a nie `pony`. Real Porter ma krok 1b, który to naprawi. Zasady konkurują. Wcześniejsze zasady wygrywają. Kolejność jest ważniejsza niż jakakolwiek pojedyncza zasada.

### Krok 3: lemmatyzator oparty na wyszukiwaniach

Właściwa lematyzacja wymaga morfologii. Przejrzysta wersja nauczania wykorzystuje małą tabelę lematów i rozwiązanie awaryjne.

```python
LEMMA_TABLE = {
    ("running", "VERB"): "run",
    ("ran", "VERB"): "run",
    ("runs", "VERB"): "run",
    ("better", "ADJ"): "good",
    ("best", "ADJ"): "good",
    ("cats", "NOUN"): "cat",
    ("cat", "NOUN"): "cat",
    ("were", "VERB"): "be",
    ("was", "VERB"): "be",
    ("is", "VERB"): "be",
}

def lemmatize(word, pos):
    key = (word.lower(), pos)
    if key in LEMMA_TABLE:
        return LEMMA_TABLE[key]
    if pos == "VERB" and word.endswith("ing"):
        return word[:-3]
    if pos == "NOUN" and word.endswith("s"):
        return word[:-1]
    return word.lower()
```

```python
>>> lemmatize("running", "VERB")
'run'
>>> lemmatize("cats", "NOUN")
'cat'
>>> lemmatize("better", "ADJ")
'good'
>>> lemmatize("watched", "VERB")
'watched'
```

Ostatni przypadek jest kluczowym momentem nauczania. `watched` nie znajduje się w naszej tabeli, a nasza rezerwa obsługuje tylko `ing`. Prawdziwa lematyzacja obejmuje `ed`, czasowniki nieregularne, przymiotniki porównawcze, liczbę mnogą ze zmianami brzmieniowymi (`children -> child`). Właśnie dlatego systemy produkcyjne korzystają z WordNet, morfologizera spaCy lub pełnego analizatora morfologicznego.

### Krok 4: połącz je razem

```python
def preprocess(text, pos_tagger=None):
    tokens = tokenize(text)
    stems = [stem_step_1a(t.lower()) for t in tokens]
    tags = pos_tagger(tokens) if pos_tagger else [(t, "NOUN") for t in tokens]
    lemmas = [lemmatize(word, pos) for word, pos in tags]
    return {"tokens": tokens, "stems": stems, "lemmas": lemmas}
```

Brakującym elementem jest tager POS. Faza 5 · 07 (tagowanie POS) tworzy jeden. Na razie ustaw domyślnie wszystko na `NOUN` i zaakceptuj ograniczenie.

## Użyj tego

NLTK i spaCy dostarczają wersje produkcyjne. Po kilka linijek każdy.

### NLTK

```python
import nltk
nltk.download("punkt_tab")
nltk.download("wordnet")
nltk.download("averaged_perceptron_tagger_eng")

from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk import pos_tag

text = "The cats were running."
tokens = word_tokenize(text)
stems = [PorterStemmer().stem(t) for t in tokens]
lemmatizer = WordNetLemmatizer()
tagged = pos_tag(tokens)

def nltk_pos_to_wordnet(tag):
    if tag.startswith("V"):
        return "v"
    if tag.startswith("J"):
        return "a"
    if tag.startswith("R"):
        return "r"
    return "n"

lemmas = [lemmatizer.lemmatize(t, nltk_pos_to_wordnet(tag)) for t, tag in tagged]
```

`word_tokenize` obsługuje skurcze, Unicode i przypadki Edge, które pomija Twoje wyrażenie regularne. `PorterStemmer` obejmuje wszystkie pięć faz. `WordNetLemmatizer` potrzebuje przetłumaczenia tagu POS ze schematu Penn Treebank firmy NLTK na zestaw skrótów WordNet. Powyższe okablowanie tłumaczeń to element pomijany przez większość samouczków.

### spaCy

```python
import spacy

nlp = spacy.load("en_core_web_sm")
doc = nlp("The cats were running.")

for token in doc:
    print(token.text, token.lemma_, token.pos_)
```

```
The      the     DET
cats     cat     NOUN
were     be      AUX
running  run     VERB
.        .       PUNCT
```

spaCy ukrywa cały potok za `nlp(text)`. Tokenizacja, tagowanie POS i lematyzacja działają. Szybciej niż NLTK na dużą skalę. Dokładniejszy od razu po wyjęciu z pudełka. Wadą jest to, że nie można łatwo zamienić poszczególnych komponentów.

### Kiedy wybrać który

| Sytuacja | Wybierz |
|----------|------|
| Nauczanie, badania, wymiana komponentów | NLTK |
| Produkcja, wielojęzyczność, szybkość ma znaczenie | spaCy |
| Rurociąg transformatorowy (i tak będziesz tokenizować za pomocą tokenizera modelu) | Użyj `tokenizers` / `transformers` i pomiń klasyczne przetwarzanie wstępne |

### Dwa tryby awarii, o których nikt Cię nie ostrzega

Większość tutoriali uczy algorytmów i kończy. Dwie rzeczy będą dotyczyć prawdziwego potoku przetwarzania wstępnego i prawie nigdy nie są omawiane.

**Dryf odtwarzalności.** NLTK i spaCy zmieniają tokenizację i zachowanie lemmatyzatora pomiędzy wersjami. To, co wygenerowało `['do', "n't"]` w spaCy 2.x, może wygenerować `["don't"]` w 3.x. Twój model został przeszkolony w jednej dystrybucji. Wnioskowanie działa teraz na innym. Dokładność cicho spada i nikt nie wie dlaczego. Przypnij wersje bibliotek w `requirements.txt`. Napisz test regresji przetwarzania wstępnego, który zamraża oczekiwaną tokenizację 20 przykładowych zdań. Uruchom go przy każdej aktualizacji.

**Niedopasowanie uczenia/wnioskowania.** Trenuj z agresywnym przetwarzaniem wstępnym (małe litery, usuwanie słów pomijanych, stemmming), wdrażaj na podstawie nieprzetworzonych danych wejściowych użytkownika, obserwuj krater wydajności. Jest to najczęstsza awaria NLP w produkcji. Jeśli wykonujesz przetwarzanie wstępne podczas uczenia, musisz uruchomić tę samą funkcję podczas wnioskowania. Przetwarzanie wstępne statku jako funkcja wewnątrz pakietu modelu, a nie jako komórka notatnika przepisana przez zespół obsługujący.

## Wyślij to

Podpowiedź wielokrotnego użytku, która pomaga inżynierom wybrać strategię przetwarzania wstępnego bez konieczności czytania trzech podręczników.

Zapisz jako `outputs/prompt-preprocessing-advisor.md`:

```markdown
---
name: preprocessing-advisor
description: Zaleca konfigurację tokenizacji, stemplowania i lematyzacji dla zadania NLP.
phase: 5
lesson: 01
---

Doradzasz w zakresie klasycznego przetwarzania wstępnego NLP. Biorąc pod uwagę opis zadania, wyprowadzasz:

1. Wybór tokenizacji (regex, NLTK word_tokenize, spaCy lub tokenizer transformatorowy). Wyjaśnij dlaczego.
2. Czy stemplować, lematyzować, jedno i drugie, czy żadne. Wyjaśnij dlaczego.
3. Konkretne zaproszenia do bibliotek. Nazwij funkcje. Dołącz tłumaczenie tagu POS, jeśli używany jest NLTK.
4. Jeden tryb awarii, który użytkownik powinien przetestować.

Odmów polecania stemplowania tekstu widocznego dla użytkownika. Odmów polecania lemmatyzacji bez tagów POS. Oznacz dane wejściowe w języku innym niż angielski jako wymagające innego potoku.
```

## Ćwiczenia

1. **Łatwe.** Rozszerz `tokenize`, aby zachować adresy URL jako pojedyncze tokeny. Test: `tokenize("Visit https://example.com today.")` powinien wygenerować jeden token adresu URL.
2. **Średni.** Wykonaj krok 1b Portera. Jeśli słowo zawiera samogłoskę i kończy się na `ed` lub `ing`, usuń je. Obsługuj regułę podwójnej spółgłoski (`hopping -> hop`, a nie `hopp`).
3. **Trudne.** Zbuduj lematyzator, który używa WordNet jako tabeli przeglądowej, ale gdy w WordNet nie ma wpisu, wraca do macierzy Portera. Zmierz dokładność otagowanego korpusu w porównaniu ze zwykłym WordNetem i zwykłym Porterem.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Znak | Słowo | Jakakolwiek jednostka, którą zużywa model. Może to być słowo, podsłowo, znak lub bajt. |
| Łodyga | Korzeń słowa | Wynik usuwania sufiksów w oparciu o reguły. Nie zawsze prawdziwe słowo. |
| Lemat | Formularz słownikowy | Formularz, który będziesz szukać. Do prawidłowego obliczenia wymagany jest kontekst gramatyczny. |
| Etykieta POS | Część mowy | Kategoria taka jak RZECZOWNIK, CZASOWNIK, PRZYM. Potrzebne do dokładnego lematyzowania. |
| Morfologia | Zasady kształtu słowa | Jak słowo zmienia formę w zależności od czasu, liczby i wielkości liter. Od tego zależy lematyzacja. |

## Dalsze czytanie

- [Porter, MF (1980). Algorytm usuwania sufiksów](https://tartarus.org/martin/PorterStemmer/def.txt) — artykuł oryginalny, pięć stron, wciąż najjaśniejsze wyjaśnienie.
- [spaCy 101 — funkcje językowe](https://spacy.io/usage/linguistic-features) — jak zbudowany jest prawdziwy rurociąg.
- [Książka NLTK, rozdział 3](https://www.nltk.org/book/ch03.html) — przypadki brzegowe tokenizacji, o których jeszcze nie pomyślałeś.