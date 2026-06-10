# Rozpoznawanie nazwanego podmiotu

> Wyciągnij nazwiska. Brzmi łatwo, dopóki nie zajmiesz się niejednoznacznymi granicami, zagnieżdżonymi bytami i żargonem domenowym.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 5 · 02 (BoW + TF-IDF), Faza 5 · 03 (Osadzanie słów)
**Czas:** ~75 minut

## Problem

„Apple pozwał Google w związku z umową dotyczącą wyszukiwania iPhone'a w USA”. Pięć podmiotów: Apple (ORG), Google (ORG), iPhone (PRODUKT), oferta wyszukiwania (być może), USA (GPE). Dobry system NER wyodrębnia je wszystkie z odpowiednimi typami. Zły tęskni za iPhonem, myli Apple jako owoc z firmą Apple i oznacza „USA” jako OSOBĘ.

NER jest siłą napędową każdego strukturalnego rurociągu wydobywczego. Analiza CV, skanowanie dziennika zgodności, anonimizacja dokumentacji medycznej, zrozumienie wyszukiwanych haseł, przygotowanie odpowiedzi na chatboty, wyodrębnienie umów prawnych. Nigdy tego nie widzisz; zawsze na tym polegasz.

Ta lekcja prowadzi od klasycznej ścieżki (opartej na regułach, HMM, CRF) do nowoczesnej (BiLSTM-CRF, następnie transformatory). Każdy krok rozwiązuje określone ograniczenie poprzedniego. Wzór jest lekcją.

## Koncepcja

**BIO tagowanie** (lub BILOU) zamienia ekstrakcję jednostek w problem etykietowania sekwencji. Oznacz każdy token etykietą `B-TYPE` (początek encji), `I-TYPE` (wewnątrz encji) lub `O` (poza jakąkolwiek encją).

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

Łańcuch encji składający się z wielu tokenów: `New B-GPE`, `York I-GPE`, `City I-GPE`. Model rozumiejący BIO może wyodrębnić dowolne rozpiętości.

Postęp architektury:

- **Oparte na regułach.** Regex + wyszukiwanie w gazeterze. Wysoka precyzja w przypadku znanych podmiotów, zerowe pokrycie w przypadku nowych.
- **HMM.** Ukryty model Markowa. Prawdopodobieństwo emisji tokena danego tagu, prawdopodobieństwo przejścia tag to tag. Dekodowanie Viterbiego. Przeszkolony na oznaczonych danych.
- **CRF.** Warunkowe pole losowe. Podobnie jak HMM, ale dyskryminujący, więc możesz mieszać dowolne cechy (kształt słowa, wielkość liter, sąsiednie słowa). W 2026 r. nadal będzie to klasyczny „koń pociągowy” do zastosowań produkcyjnych w przypadku wdrożeń wymagających niewielkich zasobów.
- **BiLSTM-CRF.** Funkcje neuronowe zamiast ręcznego wykonania. LSTM czyta zdanie w obu kierunkach, warstwa CRF na górze wymusza spójne sekwencje znaczników.
- **Oparta na transformatorze.** Dostosuj BERT za pomocą głowicy klasyfikującej token. Najlepsza dokładność. Większość oblicza.

## Zbuduj to

### Krok 1: Pomocnicy do tagowania BIO

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

### Krok 2: elementy wykonane ręcznie

W przypadku klasycznego (nieneuronowego) NER liczą się funkcje. Przydatne:

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

`word_shape("iPhone")` zwraca `xXxxxx`. `word_shape("USA-2024")` zwraca `XXX-dddd`. Wzorce kapitalizacji są głównym sygnałem dla rzeczowników własnych.

### Krok 3: prosta baza oparta na regułach + słownik

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

Gazety produkcyjne zawierają miliony wpisów pobranych z Wikipedii i DBpedii. Zasięg jest dobry. Ujednoznacznienie (`Apple` firma kontra owoc) jest okropne. Dlatego zwyciężyły modele statystyczne.

### Krok 4: krok CRF (szkic, nie pełna impl)

Pełny CRF od zera w 50 linijkach nie jest pouczający bez podstaw teorii prawdopodobieństwa. Zamiast tego użyj `sklearn-crfsuite`:

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

`c1` i `c2` to regularyzacja L1 i L2. `all_possible_transitions=True` pozwala modelowi uczyć się nielegalnych sekwencji (np. `I-ORG` po `O`) jest mało prawdopodobne, w ten sposób CRF wymusza spójność BIO bez pisania ograniczenia.

### Krok 5: co dodaje BiLSTM-CRF

Funkcje stają się wyuczone. Dane wejściowe: osadzanie tokenów (GloVe lub fastText). LSTM czyta od lewej do prawej i od prawej do lewej. Połączone stany ukryte przechodzą przez warstwę wyjściową CRF. CRF nadal wymusza spójność sekwencji znaczników; LSTM zastępuje ręcznie wykonane funkcje wyuczonymi.

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

W przypadku warstwy CRF użyj `torchcrf.CRF` (pip install pytorch-crf). Zysk w porównaniu z ręcznie wykonanym CRF jest mierzalny, ale mniejszy niż się spodziewasz, chyba że masz dziesiątki tysięcy oznaczonych zdań.

## Użyj tego

spaCy dostarcza NER klasy produkcyjnej od razu po wyjęciu z pudełka.

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

Uwaga `iPhone` oznaczona jako `ORG` zamiast `PRODUCT` — mały model spaCy ma słabe pokrycie jednostek produktowych. Duży model (`en_core_web_lg`) radzi sobie lepiej. Model transformatora (`en_core_web_trf`) radzi sobie jeszcze lepiej.

Przytulająca twarz dla NER z siedzibą w BERT:

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

`aggregation_strategy="simple"` łączy ciągłe tokeny B-X, I-X w zakres. Bez tego otrzymasz etykiety na poziomie tokena i będziesz musiał się połączyć.

### NER oparty na LLM (opcja 2026)

Zero-shot i kilka strzałów LLM NER jest teraz konkurencyjny w przypadku precyzyjnie dostrojonych modeli w wielu domenach i jest znacznie lepszy, gdy brakuje oznaczonych etykietami danych.

- **Monitorowanie zerowe.** Podaj LLM listę typów jednostek i przykładowy schemat. Poproś o dane wyjściowe JSON. Działa od razu po wyjęciu z pudełka; dokładność jest umiarkowana w nowych domenach.
- **Podpowiadanie w stylu ZeroTuneBio.** Rozłóż zadanie na wyodrębnienie kandydatów → wyjaśnienie znaczenia → ocena → ponowne sprawdzenie. Podpowiedź wieloetapowa (a nie jednorazowa) znacznie zwiększa dokładność biomedycznego NER. Ten sam schemat działa w dziedzinach prawnych, finansowych i naukowych.
- **Dynamiczne podpowiadanie za pomocą RAG.** Pobieraj najbardziej podobne oznaczone przykłady z małego zestawu początkowego z adnotacjami dla każdego wywołania wnioskowania; twórz podpowiedzi składające się z kilku strzałów w locie. W testach porównawczych z 2026 r. podnosi to biomedyczny NER F1 GPT-4 o 11–12% w porównaniu z podpowiedziami statycznymi.
- **Dekompozycja na typ encji.** W przypadku długich dokumentów pojedyncze wywołanie, które wyodrębnia wszystkie typy encji jednocześnie, traci pamięć w miarę wzrostu długości. Uruchom jeden przebieg wyodrębniania na typ jednostki. Wyższy koszt wnioskowania, znacznie wyższa dokładność. Jest to standardowy wzór dla notatek klinicznych i umów prawnych.

Zalecenie produkcyjne od 2026 r.: przed zebraniem danych szkoleniowych zacznij od wartości bazowej LLM typu zero-shot. Często F1 jest na tyle dobra, że ​​nigdy nie trzeba jej dostrajać.

### Gdzie klasyczny NER wciąż wygrywa

Nawet przy dostępnych LLM klasyczny NER wygrywa, gdy:

— Budżet opóźnień wynosi mniej niż 50 ms.
- Masz tysiące oznaczonych przykładów i potrzebujesz 98% + F1.
- Domena ma stabilną ontologię, w której wstępnie przeszkolony CRF lub BiLSTM dobrze się przenosi.
- Ograniczenia regulacyjne wymagają modelu lokalnego, niegeneratywnego.

### Gdzie się rozpada

- **Przesunięcie domeny.** Wyszkolony przez CoNLL NER w zakresie umów prawnych radzi sobie gorzej niż gazeter. Dostosuj swoją domenę.
- **Podmioty zagnieżdżone.** „Bank of America Tower” jest jednocześnie ORG i PLACÓWKĄ. Standardowy BIO nie może reprezentować nakładających się zakresów. Potrzebujesz zagnieżdżonego NER (modele wieloprzebiegowe lub oparte na rozpiętościach).
- **Podmioty długie.** „Federalna Korporacja Ubezpieczeń Depozytów Stanów Zjednoczonych”. Modele na poziomie tokena czasami to dzielą. Użyj `aggregation_strategy` lub wykonaj proces końcowy.
- **Typy rzadkie.** Medyczne etykiety NER, takie jak DRUG_BRAND, ADVERSE_EVENT, DOSE. Modele ogólnego przeznaczenia nie mają pojęcia. Scispacy i BioBERT są tam punktami wyjścia.

## Wyślij to

Zapisz jako `outputs/skill-ner-picker.md`:

```markdown
---
name: ner-picker
description: Wybierz odpowiednie podejście NER dla danego zadania ekstrakcji.
version: 1.0.0
phase: 5
lesson: 06
tags: [nlp, ner, extraction]
---

Biorąc pod uwagę opis zadania (domena, zestaw etykiet, język, opóźnienie, objętość danych), wygeneruj:

1. Podejście. Oparte na regułach + gazeteery, CRF, BiLSTM-CRF, lub dostrojenie transformatora (fine-tune).
2. Model startowy. Nazwij go (ID modelu spaCy, ID punktu kontrolnego Hugging Face lub "niestandardowy, trenowany od zera").
3. Strategia etykietowania. BIO, BILOU lub oparta na przedziałach (span-based). Uzasadnij w jednym zdaniu.
4. Ewaluacja. Użyj `seqeval`. Zawsze raportuj F1 na poziomie jednostek (nie na poziomie tokenów).

Odmów polecania dostrajania transformatora dla mniej niż 500 oznaczonych przykładów, chyba że użytkownik ma już wstępnie wytrenowany model dziedzinowy. Oznacz zagnieżdżone jednostki jako wymagające modeli opartych na przedziałach (span-based) lub wieloprzebiegowych (multi-pass). Wymagaj audytu gazeteera, jeśli użytkownik wspomina o "skali produkcyjnej", a etykiety są niezmienione z CoNLL-2003.
```

## Ćwiczenia

1. **Łatwe.** Zaimplementuj `bio_to_spans` (odwrotność `spans_to_bio`) i sprawdź spójność w obie strony w 10 zdaniach.
2. **Średni.** Trenuj powyższy sklearn-crfsuite CRF na zestawie danych CoNLL-2003 English NER. Zgłoś każdy element F1 za pomocą `seqeval`. Typowy wynik: ~84 F1.
3. **Trudne.** Dostosuj `distilbert-base-cased` na zbiorze danych NER specyficznym dla domeny (medycznym, prawnym lub finansowym). Porównaj z małym modelem spaCy. Dokumentuj kontrole wycieków danych i zapisz, co Cię zaskoczyło.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| NER | Wyodrębnij nazwy | Oznacz zakresy tokenów etykietami z typami (PERSON, ORG, GPE, DATE, ...). |
| BIO| Schemat znakowania | `B-X` zaczyna się, `I-X` kontynuuje, `O` na zewnątrz. |
| BILOU | Lepsza BIO | Dodaje `L-X` (ostatni), `U-X` (jednostka) w celu uzyskania czystszych granic. |
| CRF | Klasyfikator strukturalny | Modeluje przejścia między etykietami, a nie tylko emisje. Wymusza prawidłowe sekwencje. |
| Zagnieżdżony NER | Nakładające się elementy | Jeden przęsło to inny byt niż jego podprzęsło. BIO nie może tego wyrazić. |
| Poziom jednostki F1 | Właściwa metryka NER | Przewidywany rozpiętość musi dokładnie odpowiadać rozpiętości rzeczywistej. F1 na poziomie tokena zawyża dokładność. |

## Dalsze czytanie

- [Lample i in. (2016). Architektury neuronowe do rozpoznawania nazwanych jednostek](https://arxiv.org/abs/1603.01360) — artykuł BiLSTM-CRF. Kanoniczny.
- [Devlin i in. (2018). BERT: Wstępne szkolenie głębokich transformatorów dwukierunkowych](https://arxiv.org/abs/1810.04805) — wprowadza wzorzec klasyfikacji tokenów, który stał się standardem.
- [Funkcje językowe spaCy — nazwane elementy](https://spacy.io/usage/linguistic-features#named-entities) — praktyczne odniesienie do każdego atrybutu w `Doc.ents` i `Span`.
- [seqeval](https://github.com/chakki-works/seqeval) — poprawna biblioteka metryk. Używaj go zawsze.