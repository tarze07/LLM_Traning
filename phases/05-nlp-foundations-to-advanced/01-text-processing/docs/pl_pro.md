# Przetwarzanie tekstu — tokenizacja, stemming, lematyzacja

> Język jest ciągły. Modele są dyskretne. Przetwarzanie wstępne to pomost między nimi.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 2 · Lekcja 14 (Naiwny klasyfikator Bayesa)
**Czas:** ~45 minut

## Problem

Model nie potrafi bezpośrednio przeczytać zdania „Koty biegały”. Analizuje on liczby całkowite.

Każdy system NLP zaczyna się od trzech podstawowych pytań: Gdzie zaczyna się słowo? Jaki jest jego rdzeń? Jak traktować słowa takie jak „bieganie”, „biegałem” i „biegały” – kiedy sprowadzać je do tej samej formy (by ułatwić naukę), a kiedy zachować ich różnice?

Błędy w tokenizacji rzutują na jakość całego modelu. Jeśli tokenizator potraktuje `don't` jako jeden token, a `do n't` jako dwa, rozkład danych treningowych i testowych ulegnie rozbieżności. Jeśli stemming sprowadzi słowa `organization` i `organ` do tego samego rdzenia, modelowanie tematyczne straci sens. Jeśli lematyzator wymaga określenia części mowy (POS), a nie dostarczysz tej informacji, czasowniki mogą zostać potraktowane jak rzeczowniki.

W tej lekcji omówimy od podstaw trzy etapy wstępnego przetwarzania tekstu, a następnie porównamy działanie bibliotek NLTK oraz spaCy, by poznać dzielące je różnice i kompromisy.

## Pojęcia

Wyróżniamy trzy główne operacje. Każda z nich ma określone zadanie oraz typowe problemy (tryby awarii).

**Tokenizacja** dzieli ciąg znaków na tokeny. Pojęcie „tokenu” jest celowo ogólne, ponieważ optymalny podział zależy od konkretnego zadania: poziom słów w klasycznym NLP, podsłowa w architekturze Transformer lub pojedyncze znaki w językach bez wyraźnych odstępów (białych znaków).

**Stemming** (rdzeniowanie) odcina przyrostki na podstawie prostych reguł. Jest to proces szybki, agresywny i uproszczony (np. `running -> run`, ale też `organization -> organ` – ten drugi przypadek to typowy błąd nadmiernego skrócenia).

**Lematyzacja** sprowadza słowo do jego formy słownikowej (lemmatu) przy użyciu wiedzy gramatycznej. Jest to proces wolniejszy, ale bardzo dokładny; wymaga tablicy mapowań lub analizatora morfologicznego (np. `ran -> run` – wymaga wiedzy, że to czas przeszły czasownika „run”; `better -> good` – wymaga znajomości form stopniowania).

**Złota zasada:** stosuj stemming, gdy liczy się prędkość i tolerujesz szum (np. indeksowanie w wyszukiwarkach, zgrubna klasyfikacja). Wybieraj lematyzację, gdy kluczowe jest znaczenie semantyczne (odpowiadanie na pytania, wyszukiwanie semantyczne, teksty prezentowane użytkownikowi).

## Implementacja krok po kroku

### Krok 1: Tokenizator oparty na wyrażeniach regularnych

Najprostszy, a zarazem użyteczny tokenizator dzieli tekst na słowa oraz znaki niealfanumeryczne, traktując znaki interpunkcyjne jako osobne tokeny. Nie jest idealny, ale można go zapisać w jednej linijce kodu.

```python
import re

def tokenize(text):
    return re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?|[0-9]+|[^\sA-Za-z0-9]", text)
```

Wzorce są sprawdzane według kolejności priorytetu: najpierw słowa z opcjonalnym apostrofem wewnątrz (`don't`, `it's`), następnie same liczby, a na końcu wszelkie pojedyncze znaki niealfanumeryczne (np. interpunkcja) jako samodzielne tokeny.

```python
>>> tokenize("The cats weren't running at 3pm.")
['The', 'cats', "weren't", 'running', 'at', '3', 'pm', '.']
```

**Typowe problemy (tryby awarii):** Zapis `3pm` został podzielony na `['3', 'pm']`, ponieważ nastąpiło przejście z cyfr na litery. Taki podział jest wystarczający dla większości zadań, jednak adresy URL, adresy e-mail czy hashtagi ulegną uszkodzeniu. W rozwiązaniach produkcyjnych należy dodać dedykowane reguły przed wzorcami ogólnymi.

### Krok 2: Stemmer Portera (tylko krok 1a)

Pełny algorytm Portera składa się z pięciu faz regułowych. Krok 1a dotyczy najczęstszych przyrostków w języku angielskim i doskonale obrazuje mechanizm działania rdzeniowania.

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

Reguły są sprawdzane od góry do dołu. Reguła `ies -> i` wyjaśnia, dlaczego `ponies -> poni` (zamiast oczekiwanego `pony`). Pełny algorytm Portera zawiera krok 1b, który to koryguje. Reguły konkurują ze sobą – te zdefiniowane wcześniej wygrywają, dlatego ich kolejność jest ważniejsza niż konstrukcja pojedynczych reguł.

### Krok 3: Lematyzator słownikowy

Właściwa lematyzacja opiera się na analizie morfologicznej. Poniższa uproszczona wersja dydaktyczna wykorzystuje małą tabelę lematów oraz mechanizm awaryjnego dopasowania.

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

Ostatni przykład (`watched`) dobrze pokazuje ograniczenia tej metody. Słowa `watched` nie ma w naszej tabeli, a reguła awaryjna obsługuje tylko końcówkę `ing`. Pełna lematyzacja musi uwzględniać końcówkę `ed`, czasowniki nieregularne, stopnie przymiotników czy nieregularną liczbę mnogą (`children -> child`). Z tego powodu systemy produkcyjne korzystają z bazy WordNet, modułu morfologicznego spaCy lub innych zaawansowanych analizatorów.

### Krok 4: Integracja potoku

```python
def preprocess(text, pos_tagger=None):
    tokens = tokenize(text)
    stems = [stem_step_1a(t.lower()) for t in tokens]
    tags = pos_tagger(tokens) if pos_tagger else [(t, "NOUN") for t in tokens]
    lemmas = [lemmatize(word, pos) for word, pos in tags]
    return {"tokens": tokens, "stems": stems, "lemmas": lemmas}
```

Brakującym elementem jest tu tagger części mowy (POS tagger). Stworzymy go w lekcji Faza 5 · Lekcja 07. Na razie przyjmijmy domyślnie, że każde słowo to rzeczownik (`NOUN`), akceptując wynikające z tego uproszczenia.

## Zastosowanie w praktyce

Zarówno NLTK, jak i spaCy oferują gotowe do użycia implementacje produkcyjne. Oto jak z nich korzystać w kilku linijkach kodu.

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

Funkcja `word_tokenize` poprawnie obsługuje skróty, znaki Unicode oraz przypadki brzegowe omijane przez proste wyrażenia regularne. Klasa `PorterStemmer` wdraża wszystkie pięć faz oryginalnego algorytmu. `WordNetLemmatizer` wymaga zmapowania tagów części mowy ze schematu Penn Treebank (NLTK) na format akceptowany przez bazę WordNet – ten kluczowy etap mapowania jest często pomijany w uproszczonych poradnikach.

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

Biblioteka spaCy ukrywa cały potok przetwarzania za wywołaniem `nlp(text)`. Tokenizacja, tagowanie POS i lematyzacja wykonywane są automatycznie. Rozwiązanie to charakteryzuje się wysoką wydajnością przy dużych wolumenach danych oraz doskonałą dokładnością po wyjęciu z pudełka. Minusem jest mniejsza elastyczność w modyfikacji poszczególnych komponentów potoku.

### Porównanie rozwiązań

| Scenariusz | Rekomendacja |
|----------|------|
| Dydaktyka, badania naukowe, potrzeba modyfikacji komponentów | NLTK |
| Zastosowania produkcyjne, wielojęzyczność, wysoka wydajność | spaCy |
| Potoki oparte na modelach Transformer (tokenizacja wbudowana w model) | Użyj bibliotek `tokenizers` / `transformers` i pomiń klasyczne przetwarzanie wstępne |

### Dwa krytyczne problemy wdrożeniowe

Większość poradników skupia się na teorii algorytmów. W praktyce produkcyjnej dwa zjawiska potrafią zepsuć działanie całego potoku, choć rzadko się o nich wspomina.

**1. Dryf odtwarzalności (reproducibility drift):** Aktualizacje bibliotek NLTK i spaCy mogą zmienić sposób działania tokenizatorów i lematyzatorów. Kod, który w spaCy 2.x dzielił słowo na `['do', "n't"]`, w wersji 3.x może zwrócić `["don't"]`. W efekcie model nauczony na jednym rozkładzie danych zaczyna pracować na innym. Dokładność modelu spada bez wyraźnego powodu.
*Rozwiązanie:* Zablokuj dokładne wersje bibliotek w pliku `requirements.txt`. Napisz testy regresji dla przetwarzania wstępnego – zamroź oczekiwany podział dla zestawu np. 20 reprezentatywnych zdań i uruchamiaj test przy każdej aktualizacji zależności.

**2. Niedopasowanie fazy uczenia i wnioskowania (train/inference mismatch):** Wytrenowanie modelu na danych poddanych agresywnej obróbce (małe litery, usunięte stop-words, stemming) i wdrożenie go bezpośrednio na surowym tekście od użytkownika drastycznie obniży jego skuteczność. To jeden z najczęstszych błędów w produkcyjnych systemach NLP.
*Rozwiązanie:* Kod odpowiedzialny za przetwarzanie wstępne w trakcie uczenia musi być dokładnie tym samym kodem, który działa podczas wnioskowania. Przetwarzanie wstępne powinno być spakowane jako funkcja wewnątrz artefaktu modelu, a nie istnieć jako luźny kod w notatniku Jupyter przepisany przez inny zespół.

## Szablon do wdrożenia

Poniższy prompt ułatwia inżynierom dobór odpowiedniej strategii przetwarzania wstępnego bez konieczności analizowania dokumentacji.

Zapisz go jako `outputs/prompt-preprocessing-advisor.md`:

```markdown
---
name: preprocessing-advisor
description: Zaleca konfigurację tokenizacji, stemmingu i lematyzacji dla zadania NLP.
phase: 5
lesson: 01
---

Jesteś doradcą ds. klasycznego przetwarzania wstępnego w NLP. Na podstawie opisu zadania określ:

1. Wybór metody tokenizacji (wyrażenia regularne, word_tokenize z NLTK, spaCy lub tokenizer z modelu Transformer) wraz z uzasadnieniem.
2. Decyzję dotyczącą stosowania stemmingu, lematyzacji, obu metod lub żadnej z nich wraz z uzasadnieniem.
3. Konkretne wywołania funkcji z odpowiednich bibliotek. W przypadku wyboru NLTK dołącz kod mapowania tagów części mowy (POS).
4. Jeden kluczowy przypadek testowy (tryb awarii), który użytkownik powinien zweryfikować.

Odmów polecania stemmingu dla tekstów wyświetlanych bezpośrednio użytkownikowi końcowemu. Odmów rekomendowania lematyzacji bez użycia tagów POS. Wyraźnie zaznacz, jeśli tekst wejściowy jest w języku innym niż angielski i wymaga dedykowanego potoku przetwarzania.
```

## Ćwiczenia

1. **Łatwe.** Rozszerz funkcję `tokenize` tak, aby adresy URL były traktowane jako pojedyncze tokeny. Test: Wywołanie `tokenize("Visit https://example.com today.")` powinno zwrócić jeden token dla adresu URL.
2. **Średnie.** Zaimplementuj krok 1b Portera. Jeśli słowo zawiera samogłoskę i kończy się na `ed` lub `ing`, usuń te końcówki. Obsłuż zasadę podwójnych spółgłosek (np. `hopping -> hop`, a nie `hopp`).
3. **Trudne.** Zbuduj lematyzator, który korzysta z bazy WordNet jako słownika głównego, a w przypadku braku wpisu automatycznie przechodzi do stemmingu Portera. Zmierz i porównaj dokładność działania na otagowanym korpusie dla WordNetu, Portera oraz Twojego rozwiązania hybrydowego.

## Kluczowe pojęcia

| Pojęcie | Potoczne rozumienie | Rzeczywiste znaczenie |
|------|-----------------|----------------------|
| Token | Słowo | Podstawowa jednostka przetwarzana przez model (słowo, podsłowo, znak lub bajt). |
| Stem (rdzeń) | Temat słowa | Rezultat obcięcia końcówek słowa za pomocą reguł. Nie zawsze tworzy poprawne ortograficznie słowo. |
| Lemat | Forma słownikowa | Podstawowa, kanoniczna forma wyrazu. Jej poprawne wyznaczenie wymaga kontekstu gramatycznego. |
| Tag POS | Część mowy | Klasa gramatyczna słowa (np. NOUN, VERB, ADJ). Niezbędna do dokładnej lematyzacji. |
| Morfologia | Budowa wyrazów | Reguły odmiany wyrazów przez czasy, liczby i przypadki. Stanowi podstawę działania lematyzatorów. |

## Dalsze czytanie

- [Porter, M. F. (1980). An algorithm for suffix stripping](https://tartarus.org/martin/PorterStemmer/def.txt) — oryginalny, zaledwie 5-stronicowy artykuł. Wciąż najbardziej przystępne wyjaśnienie metody.
- [spaCy 101 — Linguistic Features](https://spacy.io/usage/linguistic-features) — szczegółowy opis działania nowoczesnego potoku przetwarzania języka naturalnego.
- [NLTK Book, Chapter 3](https://www.nltk.org/book/ch03.html) — omówienie przypadków brzegowych w tokenizacji, które łatwo przeoczyć.
