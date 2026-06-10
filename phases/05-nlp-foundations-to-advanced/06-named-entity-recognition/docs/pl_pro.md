# Rozpoznawanie encji nazwanych (NER)

> Wyodrębnianie nazw własnych i pojęć kluczowych. Brzmi prosto, dopóki nie napotkasz niejednoznacznych granic encji, struktur zagnieżdżonych czy specyficznego żargonu branżowego.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 5 · Lekcja 02 (BoW + TF-IDF), Faza 5 · Lekcja 03 (Embeddingi słów)
**Czas:** ~75 minut

## Problem

„Apple pozwało Google w związku z umową dotyczącą wyszukiwarki w iPhone'ach w USA”. Mamy tu pięć encji: Apple (ORG), Google (ORG), iPhone (PRODUCT), umowa dotycząca wyszukiwarki (potencjalna encja) oraz USA (GPE). Dobry system NER wyodrębni je wszystkie i przypisze im właściwe typy. Słaby system może pominąć iPhone'a, pomylić firmę Apple z owocem (jabłkiem) lub oznaczyć „USA” jako OSOBĘ (PERSON).

NER stanowi fundament każdego potoku ekstrakcji danych strukturalnych: analizy CV, skanowania dokumentów pod kątem zgodności z regulacjami, anonimizacja dokumentacji medycznej, analizy intencji zapytań w wyszukiwarkach, przygotowywania danych dla chatbotów czy przetwarzania umów prawnych. Choć proces ten często pozostaje niewidoczny dla użytkownika końcowego, systemy informatyczne stale na nim polegają.

W tej lekcji przejdziemy drogę od metod klasycznych (reguły, HMM, CRF) do rozwiązań nowoczesnych (BiLSTM-CRF oraz Transformer). Każdy kolejny etap rozwiązuje konkretne ograniczenia swojego poprzednika, co doskonale obrazuje ewolucję tej dziedziny.

## Pojęcia

**Tagowanie BIO** (lub BILOU) sprowadza zadanie ekstrakcji encji do problemu klasyfikacji sekwencji (sequence labeling). Każdy token otrzymuje etykietę: `B-TYPE` (początek encji), `I-TYPE` (kontynuacja encji) lub `O` (poza encją).

```
Apple    B-ORG
sued     O
Google   B-ORG
over     O
its      O
iPhone   B-PRODUCT
search   O
deal     O
in       O
the      O
US       B-GPE
.        O
```

Encja wielotokenowa: `New` (`B-GPE`), `York` (`I-GPE`), `City` (`I-GPE`). Model rozumiejący format BIO potrafi wyodrębnić segmenty o dowolnej długości.

Ewolucja architektury NER:

1. **Metody oparte na regułach:** Wyrażenia regularne oraz dopasowanie do słowników (gazeteer). Charakteryzują się bardzo wysoką precyzją (precision) dla znanych pojęć, lecz zerową czułością (recall) dla nowych encji.
2. **HMM (Ukryty Model Markowa):** Model generatywny szacujący prawdopodobieństwo wygenerowania tokenu przy danej etykiecie oraz prawdopodobieństwo przejścia między etykietami. Wykorzystuje algorytm Viterbiego do dekodowania sekwencji. Wymaga etykietowanych danych treningowych.
3. **CRF (Warunkowe Pole Losowe):** Model dyskryminacyjny (w przeciwieństwie do HMM), co pozwala na łączenie dowolnych cech (np. kształt słowa, wielkość liter, kontekst sąsiednich wyrazów). W 2026 roku CRF wciąż pozostaje podstawowym i wydajnym rozwiązaniem produkcyjnym w środowiskach o ograniczonych zasobach sprzętowych.
4. **BiLSTM-CRF:** Automatyczne uczenie się cech zamiast ich ręcznego projektowania. Sieć LSTM analizuje zdanie w obu kierunkach (w przód i w tył), a warstwa CRF na wyjściu dba o spójność logiczną sekwencji tagów BIO.
5. **Modele oparte na Transformerach:** Dostrojenie (fine-tuning) modelu typu BERT z dodatkową głowicą do klasyfikacji tokenów. Zapewnia najwyższą skuteczność, lecz wymaga największych zasobów obliczeniowych.

## Implementacja krok po kroku

### Krok 1: Funkcje pomocnicze dla formatu BIO

```python
def spans_to_bio(tokens, spans):
    labels = ["O"] * len(tokens)
    for start, end, label in spans:
        labels[start] = f"B-{label}"
        for i in range(start + 1, end):
            labels[i] = f"I-{label}"
    return labels

def bio_to_spans(tokens, labels):
    spans = []
    current = None
    for i, label in enumerate(labels):
        if label.startswith("B-"):
            if current:
                spans.append(current)
            current = (i, i + 1, label[2:])
        elif label.startswith("I-") and current and current[2] == label[2:]:
            current = (current[0], i + 1, current[2])
        else:
            if current:
                spans.append(current)
                current = None
    if current:
        spans.append(current)
    return spans
```

```python
>>> tokens = ["Apple", "sued", "Google", "over", "iPhone", "sales", "."]
>>> labels = ["B-ORG", "O", "B-ORG", "O", "B-PRODUCT", "O", "O"]
>>> bio_to_spans(tokens, labels)
[(0, 1, 'ORG'), (2, 3, 'ORG'), (4, 5, 'PRODUCT')]
```

### Krok 2: Ręczne projektowanie cech (feature engineering)

W klasycznych modelach CRF kluczowy wpływ na jakość mają przygotowane cechy. Oto przykładowy zestaw ekstrakcji cech:

```python
def token_features(token, prev_token, next_token):
    return {
        "lower": token.lower(),
        "is_upper": token.isupper(),
        "is_title": token.istitle(),
        "has_digit": any(c.isdigit() for c in token),
        "suffix_3": token[-3:].lower(),
        "shape": word_shape(token),
        "prev_lower": prev_token.lower() if prev_token else "<BOS>",
        "next_lower": next_token.lower() if next_token else "<EOS>",
    }

def word_shape(word):
    out = []
    for c in word:
        if c.isupper():
            out.append("X")
        elif c.islower():
            out.append("x")
        elif c.isdigit():
            out.append("d")
        else:
            out.append(c)
    return "".join(out)
```

`word_shape("iPhone")` zwraca `xXxxxx`, natomiast `word_shape("USA-2024")` da wynik `XXX-dddd`. Informacja o wielkości liter i strukturze znaków jest kluczowym sygnałem przy rozpoznawaniu nazw własnych.

### Krok 3: Prosty klasyfikator oparty na regułach i słownikach

```python
ORG_GAZETTEER = {"Apple", "Google", "Microsoft", "OpenAI", "Meta", "Amazon", "Netflix"}
GPE_GAZETTEER = {"US", "USA", "UK", "India", "Germany", "France"}
PRODUCT_GAZETTEER = {"iPhone", "Android", "Windows", "ChatGPT", "Claude"}

def rule_based_ner(tokens):
    labels = []
    for token in tokens:
        if token in ORG_GAZETTEER:
            labels.append("B-ORG")
        elif token in GPE_GAZETTEER:
            labels.append("B-GPE")
        elif token in PRODUCT_GAZETTEER:
            labels.append("B-PRODUCT")
        else:
            labels.append("O")
    return labels
```

Słowniki (gazeteery) w systemach komercyjnych zawierają miliony rekordów wyodrębnionych z Wikipedii czy DBpedii. Choć pokrycie znanych pojęć jest duże, ujednoznacznianie kontekstowe (np. `Apple` jako firma vs owoc) leży na niskim poziomie. Z tego powodu podejście statystyczne zdominowało tę dziedzinę.

### Krok 4: Wdrożenie CRF przy użyciu biblioteki

Pełna implementacja algorytmu CRF od zera wymaga rozbudowanej teorii prawdopodobieństwa. W praktycznych projektach stosuje się gotowe biblioteki, np. `sklearn-crfsuite`:

```python
import sklearn_crfsuite

def to_features(tokens):
    out = []
    for i, tok in enumerate(tokens):
        prev = tokens[i - 1] if i > 0 else ""
        nxt = tokens[i + 1] if i + 1 < len(tokens) else ""
        out.append({
            "word.lower()": tok.lower(),
            "word.isupper()": tok.isupper(),
            "word.istitle()": tok.istitle(),
            "word.isdigit()": tok.isdigit(),
            "word.suffix3": tok[-3:].lower(),
            "word.shape": word_shape(tok),
            "prev.word.lower()": prev.lower(),
            "next.word.lower()": nxt.lower(),
            "BOS": i == 0,
            "EOS": i == len(tokens) - 1,
        })
    return out

crf = sklearn_crfsuite.CRF(algorithm="lbfgs", c1=0.1, c2=0.1, max_iterations=100, all_possible_transitions=True)
X_train = [to_features(s) for s in sentences_tokenized]
crf.fit(X_train, bio_labels_train)
```

Parametry `c1` i `c2` określają regularyzacja L1 i L2. Opcja `all_possible_transitions=True` umożliwia modelowi naukę, że niepoprawne przejścia (np. bezpośrednie przejście z etykiety `O` do `I-ORG`) są skrajnie mało prawdopodobne. W ten sposób warstwa CRF automatycznie dba o poprawność strukturalną sekwencji BIO bez konieczności ręcznego definiowania sztywnych reguł.

### Krok 5: Rola architektury BiLSTM-CRF

Dzięki tej strukturze cechy są automatycznie wyznaczane przez sieć neuronową. Wejściem do modelu są statyczne embeddingi (np. GloVe lub fastText). Warstwa LSTM przetwarza tekst w obu kierunkach. Połączone stany ukryte (hidden states) są przekazywane do warstwy CRF, która odpowiada za strukturę sekwencji tagów. Sieć LSTM skutecznie zastępuje proces ręcznego projektowania cech.

```python
import torch
import torch.nn as nn

class BiLSTM_CRF_Head(nn.Module):
    def __init__(self, vocab_size, embed_dim, hidden_dim, n_labels):
        super().__init__()
        self.embed = nn.Embedding(vocab_size, embed_dim)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, bidirectional=True, batch_first=True)
        self.fc = nn.Linear(hidden_dim * 2, n_labels)

    def forward(self, token_ids):
        e = self.embed(token_ids)
        h, _ = self.lstm(e)
        emissions = self.fc(h)
        return emissions
```

Do obsługi logiki warstwy CRF w PyTorch warto użyć biblioteki `pytorch-crf` (`pip install pytorch-crf`). Wzrost skuteczności w porównaniu do klasycznego modelu CRF jest widoczny, lecz staje się znaczący dopiero przy posiadaniu bardzo dużych zbiorów danych treningowych (dziesiątki tysięcy etykietowanych zdań).

## Zastosowanie w praktyce

Biblioteka spaCy oferuje gotowe do wdrożenia, wydajne modele NER.

```python
import spacy

nlp = spacy.load("en_core_web_sm")
doc = nlp("Apple sued Google over its iPhone search deal in the US.")
for ent in doc.ents:
    print(f"{ent.text:20s} {ent.label_}")
```

```
Apple                ORG
Google               ORG
iPhone               ORG
US                   GPE
```

Zauważmy, że `iPhone` został błędnie oznaczony jako `ORG` zamiast `PRODUCT` – mały model spaCy (`en_core_web_sm`) ma trudności z poprawnym rozpoznawaniem encji produktowych. Większy model (`en_core_web_lg`) lub model oparty na Transformerze (`en_core_web_trf`) radzą sobie z tym zadaniem znacznie lepiej.

Wykorzystanie potoków Hugging Face i modelu BERT:

```python
from transformers import pipeline

ner = pipeline("ner", model="dslim/bert-base-NER", aggregation_strategy="simple")
print(ner("Apple sued Google over its iPhone in the US."))
```

```
[{'entity_group': 'ORG', 'word': 'Apple', ...},
 {'entity_group': 'ORG', 'word': 'Google', ...},
 {'entity_group': 'MISC', 'word': 'iPhone', ...},
 {'entity_group': 'LOC', 'word': 'US', ...}]
```

Parametr `aggregation_strategy="simple"` automatycznie scala powiązane tokeny (np. `B-ORG` i `I-ORG`) w jedną encję tekstową. Bez tej opcji otrzymalibyśmy etykiety dla każdego pojedynczego tokenu (lub podsłowa) osobno, co wymagałoby ręcznego łączenia.

### Rozpoznawanie encji za pomocą dużych modeli językowych (LLM) – stan na 2026 r.

Podejścia zero-shot oraz few-shot z użyciem LLM są obecnie wysoce konkurencyjne wobec dedykowanych modeli NER w wielu specyficznych dziedzinach, a ich przewaga rośnie drastycznie, gdy brakuje etykietowanych danych treningowych.

- **1. Klasyczne podejście zero-shot:** Podaj modelowi LLM listę typów jednostek oraz oczekiwany schemat wyjściowy (np. format JSON). Rozwiązanie to działa natychmiastowo, wykazując zadowalającą dokładność.
- **2. Potoki wieloetapowe (np. w stylu ZeroTuneBio):** Zadanie jest dzielone na mniejsze kroki: ekstrakcja kandydatów → ujednoznacznienie znaczenia → weryfikacja → ostateczna ocena. Takie etapowe podejście znacząco podnosi dokładność w trudnych domenach (np. medycynie, prawie czy finansach) w porównaniu do pojedynczego zapytania.
- **3. Dynamiczne dopasowanie kontekstu (RAG-based few-shot):** Dla każdego przetwarzanego dokumentu wyszukuje się w bazie danych najbardziej zbliżone przykłady i dynamicznie buduje podpowiedź (prompt) typu few-shot. W testach z 2026 roku podniosło to skuteczność (F1-score) modelu GPT-4 w biomedycznym NER o 11-12% w stosunku do statycznych promptów.
- **4. Podział ekstrakcji według typów encji (Entity Decomposition):** Przy długich tekstach próba wyodrębnienia wszystkich klas encji naraz często prowadzi do pomijania rzadszych kategorii. Rozwiązaniem jest uruchamianie osobnych przebiegów dla każdego typu encji. Mimo wyższego kosztu obliczeniowego, podejście to gwarantuje znacznie wyższą czułość i jest standardem przy analizie dokumentów medycznych oraz umów.

Rekomendacja na rok 2026: przed rozpoczęciem kosztownego procesu etykietowania danych, stwórz model bazowy oparty na LLM zero-shot. W wielu przypadkach uzyskana dokładność okazuje się w zupełności wystarczająca dla celów biznesowych.

### Gdzie tradycyjne modele NER wciąż mają przewagę

Nawet przy powszechności LLM klasyczne podejście do NER wygrywa, gdy:
- Rygorystyczny budżet czasowy (opóźnienia poniżej 50 ms).
- Dostępność dużego, zweryfikowanego zbioru treningowego pozwalającego osiągnąć F1-score powyżej 98%.
- Stabilna ontologia pojęciowa w danej dziedzinie, dla której CRF lub BiLSTM wykazują dobre cechy transferu wiedzy.
- Względy prawne i bezpieczeństwa wymagające działania lokalnego modelu bez generowania tekstu.

### Typowe ograniczenia i problemy

1. **Dryf dziedzinowy (domain shift):** Model NER przeszkolony na korpusie ogólnym (np. CoNLL) po uruchomieniu na dokumentach prawnych może okazać się gorszy od zwykłego słownika. Niezbędna jest adaptacja dziedzinowa.
2. **Encje zagnieżdżone (nested entities):** Np. nazwa „Bank of America Tower” zawiera w sobie zarówno organizację (Bank of America), jak i lokalizację/budynek. Klasyczny format BIO nie pozwala na nakładanie się etykiet. Rozwiązaniem są dedykowane modele do zagnieżdżonego NER (np. span-based).
3. **Długie, wieloczłonowe encje:** Np. „Federal Deposit Insurance Corporation of the United States”. Modele na poziomie tokenów bywają niestabilne przy takich strukturach. Należy zadbać o odpowiednie mechanizmy agregacji.
4. **Bardzo specyficzne lub rzadkie typy encji:** Np. nazwy substancji chemicznych czy dawkowanie leków. Modele ogólne nie posiadają takiej wiedzy; w takich przypadkach punktem wyjścia są wyspecjalizowane modele (np. scispacy lub BioBERT).

## Szablon do wdrożenia

Zapisz go jako `outputs/skill-ner-picker.md`:

```markdown
---
name: ner-picker
description: Wybierz odpowiednie podejście NER dla danego zadania ekstrakcji.
version: 1.0.0
phase: 5
lesson: 06
tags: [nlp, ner, extraction]
---

Jesteś doradcą ds. wdrażania systemów rozpoznawania encji nazwanych (NER). Na podstawie opisu zadania (domena, zestaw etykiet, język, opóźnienie, objętość danych) określ:

1. Rekomendowane podejście modelowe (reguły + gazeteery, klasyczny CRF, BiLSTM-CRF lub dostrajanie Transformerów).
2. Model bazowy jako punkt startowy (np. konkretny identyfikator modelu spaCy, checkpoint z biblioteki Hugging Face lub dedykowany model trenowany od podstaw).
3. Wybór formatu etykietowania (BIO, BILOU lub podejście oparte na rozpiętościach - span-based) wraz z jednozdaniowym uzasadnieniem.
4. Procedurę ewaluacji: użycie biblioteki `seqeval`. Wyniki F1-score muszą być raportowane na poziomie całych encji (entity-level), a nie pojedynczych tokenów.

Odmów polecania dostrajania Transformerów w przypadku zbiorów mniejszych niż 500 etykietowanych przykładów (chyba że użytkownik posiada już model wstępnie dostrojony do danej domeny). Oznacz encje zagnieżdżone jako wymagające modeli opartych na rozpiętościach (span-based) lub potoków wieloetapowych. Wymagaj weryfikacji słowników (gazeteer), jeśli użytkownik planuje wdrożenie produkcyjne, a typy encji nie wykraczają poza standardowy zestaw CoNLL-2003.
```

## Ćwiczenia

1. **Łatwe.** Zaimplementuj funkcję `bio_to_spans` (odwrotność `spans_to_bio`) i przetestuj jej poprawność w obie strony na zestawie 10 przykładowych zdań.
2. **Średnie.** Wytrenuj klasyczny model CRF za pomocą biblioteki `sklearn-crfsuite` na angielskim zbiorze danych CoNLL-2003. Dokonaj ewaluacji predykcji na poziomie całych encji przy użyciu biblioteki `seqeval` (oczekiwany wynik: około 84% F1-score).
3. **Trudne.** Dostrój model `distilbert-base-cased` na specyficznym zbiorze danych NER (np. z domeny medycznej lub finansowej). Porównaj wyniki ze standardowym modelem spaCy. Zwróć szczególną uwagę na zapobieganie wyciekowi danych (data leakage) między podziałami korpusu.

## Kluczowe pojęcia

| Pojęcie | Potoczne rozumienie | Rzeczywiste znaczenie |
|------|-----------------|----------------------|
| NER | Rozpoznawanie encji nazwanych | Proces wyodrębniania i klasyfikowania określonych pojęć w tekście (np. osoby, organizacje, lokalizacje). |
| BIO | Schemat etykietowania | Standard oznaczania granic encji: `B-X` (początek), `I-X` (kontynuacja), `O` (poza encją). |
| BILOU | Rozszerzenie BIO | Dodaje tagi `L-X` (ostatni token encji) oraz `U-X` (encja jednotokenowa) w celu precyzyjniejszego określania granic. |
| CRF | Warunkowe Pole Losowe | Klasyfikator sekwencyjny modelujący prawdopodobieństwo całej sekwencji przejść między etykietami, dbający o spójność strukturalną. |
| Zagnieżdżone encje | Nakładające się rozpiętości | Sytuacja, w której jedna encja zawiera się wewnątrz innej (np. lokalizacja w nazwie organizacji). Niemożliwa do zakodowania w standardowym BIO. |
| Entity-level F1 | Rzetelna ewaluacja NER | Wynik obliczany przy założeniu, że wyodrębniony segment musi w 100% zgadzać się z rzeczywistymi granicami encji. Ewaluacja na poziomie tokenów sztucznie zawyża skuteczność. |

## Dalsze czytanie

- [Lample et al. (2016). Neural Architectures for Named Entity Recognition](https://arxiv.org/abs/1603.01360) — klasyczna publikacja wprowadzająca architekturę BiLSTM-CRF dla NER.
- [Devlin et al. (2018). BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding](https://arxiv.org/abs/1810.04805) — opisuje mechanizm klasyfikacji tokenów (token classification), który stał się nowym standardem.
- [spaCy linguistic features - Named Entities](https://spacy.io/usage/linguistic-features#named-entities) — praktyczny poradnik korzystania z atrybutów `Doc.ents` oraz obiektów klasy `Span` w bibliotece spaCy.
- [seqeval package](https://github.com/chakki-works/seqeval) — oficjalne repozytorium standardowej biblioteki do ewaluacji modeli sekwencyjnych.
