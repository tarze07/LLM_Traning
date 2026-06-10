# Analiza sentymentu

> Klasyczne zadanie NLP. Większość kluczowych zagadnień z zakresu klasycznej klasyfikacji tekstu skupia się w tym temacie.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 5 · Lekcja 02 (BoW + TF-IDF), Faza 2 · Lekcja 14 (Naiwny klasyfikator Bayesa)
**Czas:** ~75 minut

## Problem

„Jedzenie nie było wspaniałe.” Pozytywne czy negatywne?

Analiza sentymentu wydaje się prosta: autor wypowiedzi wyraża aprobatę lub jej brak. Wystarczy przypisać etykietę. Jednak powodem, dla którego zadanie to stało się kanonicznym problemem NLP, są liczne wyjątki i zawiłości językowe. Negacja odwraca znaczenie. Sarkazm całkowicie je zmienia. Wyrażenie „nie najgorzej” ma wydźwięk pozytywny, mimo że oba słowa osobno niosą ładunek negatywny. Emotikony często niosą silniejszy ładunek emocjonalny niż towarzyszący im tekst. Ponadto ogromne znaczenie ma kontekst dziedzinowy (np. słowo `ciasny` w recenzji obuwia vs `ciasny` w żargonie hip-hopowym).

Analiza sentymentu to doskonały poligon doświadczalny dla klasycznego NLP. Zrozumienie, dlaczego proste modele bazowe (baselines) zawodzą w określonych przypadkach, pozwala pojąć motywację stojącą za bardziej złożonymi architekturami. W tej lekcji zaimplementujemy od podstaw naiwny klasyfikator Bayesa, zastosujemy regresję logistyczną oraz omówimy wyzwania, które sprawiają, że wdrożenie analizy sentymentu w produkcji bywa skomplikowanym zadaniem.

## Pojęcia

Klasyczna analiza sentymentu składa się z dwóch etapów:

1. **Reprezentacja:** Przekształcenie tekstu w wektor cech (Bag of Words, TF-IDF lub n-gramy).
2. **Klasyfikacja:** Dopasowanie modelu klasyfikacji (Naiwny Bayes, regresja logistyczna, SVM) na zbiorze etykietowanych danych treningowych.

**Naiwny klasyfikator Bayesa** to najprostszy model, który daje zadowalające rezultaty. Zakłada on wzajemną niezależność cech (słów) przy danej klasie. Szacujemy prawdopodobieństwa warunkowe `P(word | positive)` i `P(word | negative)` na podstawie liczby wystąpień słów w zbiorze treningowym. Podczas wnioskowania (klasyfikacji) mnożymy te prawdopodobieństwa. Mimo że to „naiwne” założenie o niezależności jest w oczywisty sposób fałszywe, wyniki bywają zaskakująco dobre. Wynika to z faktu, że przy ograniczonej liczbie cech tekstowych klasyfikator prawidłowo wyznacza kierunek wpływu słów (sentyment dodatni/ujemny), nawet jeśli same wartości prawdopodobieństw są niedokładne.

**Regresja logistyczna** eliminuje konieczność zakładania niezależności cech. Model uczy się wag dla każdej cechy indywidualnie, co pozwala na uwzględnienie współzależności. Na przykład bigram `not good` (nie dobry) otrzyma silną wagę ujemną, podczas gdy Naiwny Bayes bez jawnego uwzględnienia bigramów w słowniku nie potrafiłby tego poprawnie ocenić.

## Implementacja krok po kroku

### Krok 1: Przykładowy minizbiór danych

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

Zbiór jest celowo miniaturowy. W rzeczywistych projektach stosuje się zbiory liczące dziesiątki tysięcy przykładów (np. IMDb, SST-2, Yelp). Matematyka stojąca za klasyfikacją pozostaje bez zmian.

### Krok 2: Wielomianowy naiwny klasyfikator Bayesa od podstaw

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

Wygładzanie addytywne (dla `alpha=1.0`) nosi nazwę wygładzania Laplace'a. Bez tego zabiegu słowo, które nie wystąpiło w danej klasie w zbiorze treningowym, otrzymałoby zerowe prawdopodobieństwo, co uniemożliwiłoby obliczenie logarytmu. W praktyce często stosuje się `alpha=0.01`, natomiast `alpha=1.0` jest dobrym punktem wyjścia.

### Krok 3: Regresja logistyczna od podstaw

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

Regularyzacja L2 odgrywa tu kluczową rolę. Cechy tekstowe są bardzo rzadkie, przez co model bez regularyzacji łatwo ulega przeuczeniu (overfitting) i zapamiętuje dane treningowe. Warto zacząć od współczynnika `0.01` i dostroić go podczas eksperymentów.

### Krok 4: Obsługa negacji (rozwiązanie problemu)

Rozważmy zwroty „nie dobrze” (niedobrze) i „nie źle” (nieźle). Klasyfikator oparty na pojedynczych słowach (BoW) widzi zbiory `{not, good}` oraz `{not, bad}` i podejmuje decyzję na podstawie tego, który wyraz dominował w danych treningowych. Klasyfikator analizujący bigramy widzi `not_good` oraz `not_bad` i uczy się ich jako niezależnych cech, co zazwyczaj rozwiązuje problem.

Proste i skuteczne rozwiązanie, gdy nie używamy bigramów, to **zakres negacji** (negation scope). Polega ono na dodawaniu prefiksu `NOT_` do wszystkich słów występujących po słowie przeczącym, aż do napotkania pierwszego znaku interpunkcyjnego.

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

Dzięki temu `good` oraz `NOT_good` stają się osobnymi cechami, którym klasyfikator może przypisać przeciwne wagi. Kilka linii kodu przetwarzania wstępnego pozwala uzyskać wyraźny wzrost skuteczności w testach.

### Krok 5: Metryki ewaluacji o kluczowym znaczeniu

Sama dokładność (accuracy) bywa bardzo myląca w przypadku braku zbalansowania klas. Rzeczywiste zbiory danych do analizy sentymentu często zawierają np. 70-80% opinii o jednym charakterze (np. samych pozytywnych). Klasyfikator, który zawsze przewiduje klasę większościową, osiągnie wtedy 80% dokładności, będąc w praktyce bezużytecznym. W ewaluacji należy uwzględnić:

- **Precyzja (precision) i czułość (recall) dla każdej klasy:** Pozwalają precyzyjnie ocenić jakość predykcji dla poszczególnych kategorii.
- **Macro F1-score:** Średnia arytmetyczna z wyników F1 dla każdej z klas. Jest to podstawowa metryka przy niezrównoważonych danych, traktująca klasy równoważnie.
- **Weighted F1-score:** Średnia ważona wyników F1, gdzie waga zależy od liczebności danej klasy. Warto ją raportować obok Macro F1-score.
- **Macierz pomyłek (confusion matrix):** Prezentuje surowe liczby predykcji. Zawsze warto ją przeanalizować, ponieważ pokazuje ona, które klasy są ze sobą najczęściej mylone.
- **Analiza błędów jakościowych:** Wyodrębnij po 5 najpoważniejszych błędów dla każdej klasy i przeanalizuj je ręcznie. Nic nie zastąpi bezpośredniej lektury błędnych predykcji modelu.

Przy skrajnej dysproporcji klas (np. stosunek powyżej 95:5) zamiast dokładności należy stosować metryki **AUROC** oraz **AUPRC**. Metryka AUPRC (Area Under the Precision-Recall Curve) jest szczególnie czuła na wyniki klasy mniejszościowej, która zazwyczaj jest najbardziej interesująca (np. wykrywanie spamu czy anomalii).

Częsty błąd to podawanie wartości Micro F1-score zamiast Macro F1-score. Ta pierwsza może być sztucznie zawyżona przez dominującą klasę większościową. Użycie Macro F1-score zmusza model do wykazania się dobrą skutecznością na klasie mniejszościowej.

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

## Zastosowanie w praktyce

Biblioteka scikit-learn pozwala zaimplementować kompletny potok klasyfikacji w kilku linijkach kodu.

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

Kluczowe szczegóły konfiguracji scikit-learn: ustawienie `stop_words=None` zapobiega usunięciu negacji. Parametr `ngram_range=(1, 2)` dołącza bigramy (dzięki czemu `not_good` staje się osobną cechą). Parametr `sublinear_tf=True` tłumi wpływ słów powtarzających się wielokrotnie. Zastosowanie tych trzech parametrów potrafi podnieść dokładność klasyfikacji na zbiorze SST-2 z poziomu 75% do nawet 85%.

### Kiedy warto przejść na model typu Transformer

1. **Wykrywanie sarkazmu:** Klasyczne modele oparte na statystykach słów zupełnie sobie z tym nie radzą.
2. **Długie teksty:** Scenariusze, w których wydźwięk ulega zmianie w trakcie wypowiedzi.
3. **Analiza sentymentu oparta na aspektach (ABSA – Aspect-Based Sentiment Analysis):** Np. „Aparat był świetny, ale bateria trzymała bardzo krótko”. Wymaga to przypisania emocji do konkretnych cech produktu, co potrafią zrealizować jedynie zaawansowane modele Transformer.
4. **Języki rzadkie lub wielojęzyczność:** Modele takie jak multilingual BERT (mBERT) oferują doskonałe możliwości transferu wiedzy (zero-shot transfer) bez konieczności posiadania dużych zbiorów treningowych dla każdego języka.

W tych scenariuszach optymalnym wyborem będzie architektura typu Transformer (szczegóły w Fazie 5 · Lekcja 07 i kolejnych). W pozostałych przypadkach standardem produkcyjnym pozostaje regresja logistyczna na reprezentacji TF-IDF z bigramami i obsługą negacji.

### Pułapka powtarzalności wyników

Częste trenowanie nowych wariantów modeli to standard. Niestety, rzetelna ewaluacja bywa pomijana. Wyniki podawane w publikacjach naukowych bazują na ściśle określonych podziałach zbiorów, specyficznym preprocessingu i konkretnych tokenizatorach. Porównanie nowego modelu z wynikami z artykułu bez odtworzenia identycznego potoku (pipeline) prowadzi do błędnych wniosków. Zawsze ewaluuj model bazowy we własnym potoku przetwarzania, zamiast bezkrytycznie porównywać się z liczbami z dokumentacji.

## Szablon do wdrożenia

Zapisz go jako `outputs/prompt-sentiment-baseline.md`:

```markdown
---
name: sentiment-baseline
description: Zaprojektuj bazowy model analizy sentymentu dla nowego zbioru danych.
phase: 5
lesson: 05
---

Jesteś doradcą ds. wdrażania modeli analizy sentymentu. Na podstawie opisu zbioru danych (domena, język, rozmiar, szczegółowość etykiet, budżet opóźnień) określ:

1. Strategię ekstrakcji cech: wybór tokenizatora, zakresu n-gramów, polityki stop-words (zalecane zachowanie negacji) oraz metody obsługi negacji (np. prefiksy lub bigramy).
2. Wybór klasyfikatora: Naiwny Bayes jako podstawowy punkt odniesienia, regresja logistyczna dla środowisk produkcyjnych, model typu Transformer tylko wtedy, gdy wymagane jest wykrywanie sarkazmu, analiza aspektowa lub obsługa wielu języków jednocześnie.
3. Plan ewaluacji modelu: określenie metryk (precyzja, czułość, F1-score, macierz pomyłek) oraz procedury analizy błędów jakościowych na poziomie klas (a nie tylko wartości zagregowanych).
4. Jeden scenariusz ryzyka (dryf domeny lub obecność sarkazmu) do monitorowania po wdrożeniu produkcyjnym.

Odmów rekomendowania usuwania stop-words w analizie sentymentu. Odmów raportowania wyłącznie dokładności (accuracy) przy niezrównoważonych klasach (np. 90% opinii pozytywnych). Wskazuj, że języki o bogatej fleksji i strukturze podsłowowej wymagają użycia modeli fastText lub Transformer zamiast klasycznego TF-IDF na poziomie całych słów.
```

## Ćwiczenia

1. **Łatwe.** Dodaj funkcję `apply_negation` jako krok przetwarzania wstępnego do potoku scikit-learn i zmierz różnicę (deltę) wyniku F1-score na małym zbiorze danych testowych.
2. **Średnie.** Zaimplementuj regresję logistyczną z wagami klas (przekaż parametr `class_weight="balanced"` w scikit-learn lub uwzględnij wagi klas bezpośrednio w obliczaniu gradientu). Przetestuj skuteczność tego rozwiązania na syntetycznie zaburzonym zbiorze danych o proporcjach klas 90:10.
3. **Trudne.** Zbuduj detektor sarkazmu, trenując pomocniczy klasyfikator na podstawie błędów (reszt) głównego modelu analizy sentymentu. Opracuj i udokumentuj procedurę testową. Zwróć szczególną uwagę na to, czy dokładność predykcji sarkazmu przekracza poziom losowy (dla klasyfikacji binarnej wynosi on 50%, co bywa trudną barierą do pokonania w pierwszych próbach).

## Kluczowe pojęcia

| Pojęcie | Potoczne rozumienie | Rzeczywiste znaczenie |
|------|-----------------|----------------------|
| Polaryzacja | Wydźwięk wypowiedzi | Etykieta binarna (pozytywny/negatywny); niekiedy rozszerzana o klasę neutralną lub skalę wielostopniową (np. ocena 1-5 gwiazdek). |
| Analiza sentymentu oparta na aspektach (ABSA) | Wydźwięk wobec cech | Przypisywanie sentymentu do konkretnych obiektów lub cech wymienionych w tekście. |
| Zakres negacji | Modyfikacja negowanych wyrazów | Dodawanie prefiksu `NOT_` do tokenów występujących po słowie przeczącym aż do najbliższego znaku interpunkcyjnego. |
| Wygładzanie Laplace'a | Wygładzanie addytywne | Dodanie stałej (zazwyczaj 1.0) do liczby wystąpień słów w celu wyeliminowania zerowych prawdopodobieństw w klasyfikatorze Bayesa. |
| Regularyzacja L2 | Kary za wagę modelu | Dodanie członu kary `lambda * sum(w^2)` do funkcji straty, co zapobiega przeuczeniu modelu na rzadkich cechach tekstowych. |

## Dalsze czytanie

- [Pang, B., Lee, L. (2008). Opinion Mining and Sentiment Analysis](https://www.cs.cornell.edu/home/llee/opinion-mining-sentiment-analytic-survey.html) — pionierska publikacja przeglądowa. Pierwsze cztery sekcje stanowią kompletne kompendium klasycznych metod.
- [Wang, S., Manning, C. D. (2012). Baselines and Bigrams: Simple, Good Sentiment and Topic Classification](https://aclanthology.org/P12-2018/) — artykuł pokazujący, jak trudno pobić kombinację bigramów i klasyfikatora Bayesa w analizie krótkich tekstów.
- [scikit-learn - Dataset loading utilities](https://scikit-learn.org/stable/modules/feature_extraction.html#text-feature-extraction) — dokumentacja modułów ekstrakcji cech tekstowych wraz ze szczegółowym opisem dostępnych parametrów.
