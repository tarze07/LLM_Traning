# Analiza sentymentów

> Kanoniczne zadanie NLP. Większość tego, co musisz wiedzieć o klasycznej klasyfikacji tekstu, znajduje się tutaj.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 5 · 02 (BoW + TF-IDF), Faza 2 · 14 (Naive Bayes)
**Czas:** ~75 minut

## Problem

„Jedzenie nie było wspaniałe.” Pozytywne czy negatywne?

Sentyment brzmi prosto. Recenzent powiedział, że coś mu się podobało lub nie. Oznacz zdanie. Powodem, dla którego stało się to kanonicznym zadaniem NLP, jest to, że za każdym pozornie łatwym przypadkiem kryje się trudny. Negacja odwraca znaczenie. Sarkazm to odwraca. „Nieźle” jest pozytywne pomimo dwóch słów zakodowanych negatywnie. Emotikony niosą większy sygnał niż otaczający tekst. Słownictwo dziedzinowe ma znaczenie (`tight` w przeglądzie muzyki w porównaniu z `tight` w przeglądzie mody).

Sentiment to działające laboratorium klasycznego NLP. Jeśli rozumiesz, dlaczego każda naiwna linia bazowa ma określony tryb awarii, rozumiesz, dlaczego wynaleziono każdy bogatszy model. W tej lekcji od zera zbudowano linię bazową Naive Bayes, dodano regresję logistyczną i wymieniono pułapki, które sprawiają, że nastroje produkcyjne stają się problemem stopnia zgodności.

## Koncepcja

Klasyczny sentyment to przepis dwuetapowy.

1. **Reprezentuj.** Zmień tekst w wektor cech. BoW, TF-IDF lub n-gramów.
2. **Klasyfikuj.** Dopasuj model liniowy (Naive Bayes, regresja logistyczna, SVM) do oznaczonych przykładów.

Naiwny Bayes to najgłupszy model, jaki działa. Załóżmy, że każda funkcja jest niezależna, biorąc pod uwagę etykietę. Oszacuj `P(word | positive)` i `P(word | negative)` na podstawie zliczeń. Wnioskując, pomnóż prawdopodobieństwa. „Naiwne” założenie o niezależności jest śmiesznie błędne, a mimo to rezultaty są szokująco mocne. Powód: przy niewielkiej liczbie elementów tekstowych i umiarkowanych danych klasyfikator zwraca uwagę na to, w którą stronę każde słowo pochyla się bardziej niż w jakim stopniu.

Regresja logistyczna naprawia założenie niezależności. Uczy się wagi każdej cechy, w tym wag ujemnych. `not good` jako element bigramu otrzymuje wagę ujemną. Naiwny Bayes nie może tego zrobić w przypadku bigramów, których nigdy nie oznaczył.

## Zbuduj to

### Krok 1: prawdziwy mini-zestaw danych

```python
POSITIVE = [
    "absolutely loved this movie",
    "beautiful cinematography and a great story",
    "one of the best films of the year",
    "brilliant acting from the lead",
    "heartwarming and funny",
]

NEGATIVE = [
    "boring and far too long",
    "not worth your time",
    "the plot made no sense",
    "terrible acting, awful script",
    "i want my two hours back",
]
```

Mały celowo. Prawdziwa praca wykorzystuje dziesiątki tysięcy przykładów (IMDb, SST-2, polaryzacja Yelp). Matematyka jest identyczna.

### Krok 2: wielomian Naiwny Bayes od zera

```python
import math
from collections import Counter

def train_nb(docs_by_class, vocab, alpha=1.0):
    class_priors = {}
    class_word_probs = {}
    total_docs = sum(len(d) for d in docs_by_class.values())

    for cls, docs in docs_by_class.items():
        class_priors[cls] = len(docs) / total_docs
        counts = Counter()
        for doc in docs:
            for token in doc:
                counts[token] += 1
        total = sum(counts.values()) + alpha * len(vocab)
        class_word_probs[cls] = {
            w: (counts[w] + alpha) / total for w in vocab
        }
    return class_priors, class_word_probs

def predict_nb(doc, class_priors, class_word_probs):
    scores = {}
    for cls in class_priors:
        s = math.log(class_priors[cls])
        for token in doc:
            if token in class_word_probs[cls]:
                s += math.log(class_word_probs[cls][token])
        scores[cls] = s
    return max(scores, key=scores.get)
```

Wygładzanie addytywne (alfa=1,0) to wygładzanie Laplace'a. Bez tego słowo niewidoczne w klasie ma prawdopodobieństwo zerowe i dziennik eksploduje. `alpha=0.01` jest powszechne w praktyce. `alpha=1.0` jest domyślnym ustawieniem uczenia.

### Krok 3: regresja logistyczna od zera

```python
import numpy as np

def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -20, 20)))

def train_lr(X, y, epochs=500, lr=0.05, l2=0.01):
    n_features = X.shape[1]
    w = np.zeros(n_features)
    b = 0.0
    for _ in range(epochs):
        logits = X @ w + b
        preds = sigmoid(logits)
        err = preds - y
        grad_w = X.T @ err / len(y) + l2 * w
        grad_b = err.mean()
        w -= lr * grad_w
        b -= lr * grad_b
    return w, b

def predict_lr(X, w, b):
    return (sigmoid(X @ w + b) >= 0.5).astype(int)
```

Regularyzacja L2 ma tutaj znaczenie. Funkcje tekstowe są rzadkie; bez L2 model zapamiętuje przykłady szkoleniowe. Zacznij od `0.01` i dostrój.

### Krok 4: obsługa negacji (tryb awarii)

Rozważ „niedobrze” i „nieźle”. Klasyfikator BoW widzi `{not, good}` i `{not, bad}` i uczy się od tego, co pokazało więcej podczas szkolenia. Klasyfikator bigramów widzi `not_good` i `not_bad` i uczy się ich jako odrębnych cech. To zwykle wystarcza.

Prosta poprawka, która działa, gdy nie masz bigramów: **zakres negacji**. Przedstaw tokeny po słowie negacji za pomocą `NOT_` aż do następnej interpunkcji.

```python
NEGATION_WORDS = {"not", "no", "never", "nor", "none", "nothing", "neither"}
NEGATION_TERMINATORS = {".", "!", "?", ",", ";"}

def apply_negation(tokens):
    out = []
    negate = False
    for token in tokens:
        if token in NEGATION_TERMINATORS:
            negate = False
            out.append(token)
            continue
        if token in NEGATION_WORDS:
            negate = True
            out.append(token)
            continue
        out.append(f"NOT_{token}" if negate else token)
    return out
```

```python
>>> apply_negation(["not", "good", "at", "all", ".", "but", "funny"])
['not', 'NOT_good', 'NOT_at', 'NOT_all', '.', 'but', 'funny']
```

Teraz `good` i `NOT_good` to różne funkcje. Klasyfikator może nadać im przeciwną wagę. Trzy linie wstępnego przetwarzania, mierzalny skok dokładności w benchmarkach nastrojów.

### Krok 5: wskaźniki oceny, które mają znaczenie

Sama dokładność wprowadza w błąd, jeśli klasy są niezrównoważone. Korpusy nastrojów rzeczywistych są zwykle w 70–80% pozytywne lub w 70–80% negatywne; klasyfikator o stałej większości uzyskuje 80% dokładności i jest bezwartościowy. Zgłoś każdą z poniższych sytuacji:

- **Precyzja i zapamiętywanie na klasę.** Jedna para na klasę. Uśrednij je makro, aby uzyskać jedną liczbę, która uwzględnia równowagę klas.
- **Makro-F1 (podstawowa metryka dla niezrównoważonych danych).** Średnia wyników F1 dla każdej klasy, jednakowo ważona. Użyj tego zamiast dokładności, gdy klasy są niezrównoważone.
- **Ważony-F1 (alternatywa).** Taki sam jak makro, ale ważony według częstotliwości klasy. Raportuj wraz z makro-F1, gdy sama nierównowaga ma znaczenie biznesowe.
- **Macierz zamieszania.** Surowe dane. Zawsze sprawdź, zanim zaufasz jakimkolwiek metrykom skalarnym; ujawnia, którą parę klas myli model.
- **Przykłady błędów dla poszczególnych klas.** Wyciągnij 5 błędnych przewidywań na klasę. Przeczytaj je. Nic nie zastąpi odczytania rzeczywistych błędów.

W przypadku poważnie niezrównoważonych danych (stosunek > 95-5) zamiast dokładności należy podać **AUROC** i **AUPRC**. AUPRC jest bardziej wrażliwy na klasę mniejszości, na której zwykle ci zależy (spam, oszustwo, rzadkie sentymenty).

**Typowy błąd, którego należy unikać.** Zgłaszanie mikro-F1 zamiast makro-F1 w przypadku niezrównoważonych danych daje liczbę, która wygląda na wysoką, ponieważ jest zdominowana przez klasę większości. Macro-F1 zmusza do zobaczenia występów klasy mniejszościowej.

```python
def evaluate(y_true, y_pred):
    tp = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 1)
    fp = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 1)
    fn = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 0)
    tn = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 0)
    precision = tp / (tp + fp) if tp + fp else 0
    recall = tp / (tp + fn) if tp + fn else 0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0
    return {"tp": tp, "fp": fp, "tn": tn, "fn": fn, "precision": precision, "recall": recall, "f1": f1}
```

## Użyj tego

scikit-learn robi to poprawnie w sześciu liniach.

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

pipe = Pipeline([
    ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True, stop_words=None)),
    ("clf", LogisticRegression(C=1.0, max_iter=1000)),
])
pipe.fit(X_train, y_train)
print(pipe.score(X_test, y_test))
```

Trzy rzeczy, na które warto zwrócić uwagę. `stop_words=None` przechowuje negacje. `ngram_range=(1, 2)` dodaje bigramy, więc `not_good` staje się funkcją. `sublinear_tf=True` tłumi powtarzające się słowa. Te trzy flagi stanowią różnicę pomiędzy linią bazową z dokładnością do 75% a linią bazową z dokładnością do 85% w SST-2.

### Kiedy sięgnąć po transformator

- Wykrywanie sarkazmu. Klasyczne modele tu zawodzą. Okres.
- Długie recenzje, w przypadku których nastroje zmieniają się w połowie dokumentu.
- Nastroje oparte na aspektach. „Aparat był świetny, ale bateria okropna”. Musisz przypisać sentyment do aspektów. Tylko transformatory lub modele z wyjściem strukturalnym.
- Języki inne niż angielski i wymagające niewielkich zasobów. Wielojęzyczny BERT zapewnia bezpłatną wersję zerową.

Jeśli potrzebujesz któregokolwiek z powyższych, przejdź do fazy 7 (głębokie nurkowanie transformatorów). W przeciwnym razie podstawą produkcji na rok 2026 będzie naiwny Bayes lub regresja logistyczna na TF-IDF plus bigramy i obsługa negacji.

### Pułapka powtarzalności (ponownie)

Ponowne szkolenie modeli nastrojów jest rutyną. Ponowna ich ocena nie jest. Liczby dokładności podawane w artykułach wykorzystują określone podziały, określone przetwarzanie wstępne i określone tokenizatory. Jeśli porównasz nowy model z wartością bazową bez użycia identycznego potoku, otrzymasz mylące delty. Zawsze regeneruj linię bazową swojego rurociągu, a nie numer papieru.

## Wyślij to

Zapisz jako `outputs/prompt-sentiment-baseline.md`:

```markdown
---
name: sentiment-baseline
description: Zaprojektuj bazowy model analizy sentymentu dla nowego zbioru danych.
phase: 5
lesson: 05
---

Biorąc pod uwagę opis zbioru danych (domena, język, rozmiar, szczegółowość etykiet, budżet opóźnień), wygeneruj:

1. Przepis na ekstrakcję cech. Określ tokenizator, zakres n-gramów, politykę dotyczącą stopwords (zazwyczaj zachowaj), obsługę negacji (prefiks w określonym zakresie lub bigramy).
2. Klasyfikator. Naive Bayes dla modelu bazowego, regresja logistyczna dla produkcji, transformator tylko wtedy, gdy domena wymaga obsługi sarkazmu / analizy aspektowej / wielojęzyczności.
3. Plan ewaluacji. Raportuj precyzję, czułość (recall), F1, macierz pomyłek oraz przykłady błędów dla każdej klasy (nie tylko wartości skalarne).
4. Jeden tryb awarii do monitorowania po wdrożeniu. Dryf domeny i sarkazm to dwa najczęstsze.

Odmów zalecania usuwania stopwords w zadaniach związanych z sentymentem. Odmów raportowania dokładności jako jedynej metryki, gdy klasy są niezrównoważone (np. 90% pozytywnych). Oznacz języki o bogatej strukturze podsłów jako wymagające osadzania FastText lub transformatora zamiast TF-IDF na poziomie słów.
```

## Ćwiczenia

1. **Łatwe.** Dodaj `apply_negation` jako krok przetwarzania wstępnego w potoku scikit-learn i zmierz deltę F1 na małym zbiorze danych nastrojów.
2. **Średni.** Zaimplementuj regresję logistyczną ważoną klasami (przekaż `class_weight="balanced"` do scikit-learn lub samodzielnie uzyskaj gradient). Zmierz wpływ na syntetyczną nierównowagę klas 90-10.
3. **Trudne.** Zbuduj detektor sarkazmu, ucząc drugi klasyfikator na podstawie reszt modelu nastrojów. Udokumentuj konfigurację eksperymentalną. Ostrzegaj czytelnika, gdy twoja celność jest poniżej szansy (poziom szansy na sarkazm 2-klasowy wynosi ~50% i większość pierwszych prób kończy się na tym).

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Polaryzacja | Pozytywne czy negatywne | Etykieta binarna; czasami rozszerzony do neutralnego lub drobnoziarnistego (5 gwiazdek). |
| Nastroje oparte na aspektach | Polaryzacja według aspektu | Przypisz sentyment do konkretnych obiektów lub atrybutów wymienionych w tekście. |
| Zakres negacji | Odwracanie pobliskich żetonów | Przedstaw tokeny po „nie” za pomocą `NOT_` aż do znaku interpunkcyjnego. |
| Wygładzanie Laplace'a | Dodanie 1 do zliczeń | Zapobiega funkcjom o zerowym prawdopodobieństwie w Naive Bayes. |
| Regularyzacja L2 | Kurczące się ciężary | Dodaje `lambda * sum(w^2)` do straty. Niezbędne w przypadku rzadkich funkcji tekstowych. |

## Dalsze czytanie

- [Pang i Lee (2008). Eksploracja opinii i analiza nastrojów] (https://www.cs.cornell.edu/home/llee/opinion-mining-sentiment-analytic-survey.html) — badanie podstawowe. Długie, ale pierwsze cztery sekcje obejmują wszystko, co klasyczne.
- [Wang i Manning (2012). Baselines i Biggrams: Simple, Good Sentiment and Topic Classification](https://aclanthology.org/P12-2018/) — artykuł pokazujący bigramy i Naive Bayes jest trudny do pokonania w krótkim tekście.
- [dokumentacja dotycząca ekstrakcji funkcji tekstowych scikit-learn](https://scikit-learn.org/stable/modules/feature_extraction.html#text-feature-extraction) — informacje dotyczące `CountVectorizer`, `TfidfVectorizer` i każdego pokrętła, które dostroisz.