# Naiwny Bayes

> „Naiwne” założenie jest błędne, a mimo to działa. Na tym polega piękno.

**Typ:** Kompilacja
**Język:** Python
**Wymagania wstępne:** Faza 2, lekcje 01-07 (klasyfikacja, twierdzenie Bayesa)
**Czas:** ~75 minut

## Cele nauczania

- Zaimplementuj od podstaw wielomianowe naiwne Bayesa z wygładzaniem Laplace'a do klasyfikacji tekstu
- Wyjaśnij, dlaczego naiwne założenie o niezależności jest matematycznie błędne, ale w praktyce daje prawidłowe rankingi klas
- Porównaj warianty Wielomianu, Bernoulliego i Gaussa Naiwnego Bayesa i wybierz właściwy dla danego typu cechy
- Oceń naiwnego Bayesa pod kątem regresji logistycznej na wielowymiarowych, rzadkich danych i wyjaśnij kompromis w zakresie odchylenia i wariancji w pracy

## Problem

Musisz sklasyfikować tekst. E-maile do spamu lub nie-spamu. Opinie klientów są pozytywne lub negatywne. Wsparcie biletów według kategorii. Masz tysiące funkcji (po jednej na słowo) i ograniczone dane szkoleniowe.

Większość klasyfikatorów się tutaj dławi. Regresja logistyczna wymaga wystarczającej liczby próbek, aby wiarygodnie oszacować tysiące wag. Drzewa decyzyjne dzielą się na jedno słowo na raz i szalenie się dopasowują. KNN w 10 000 wymiarach jest bez znaczenia, ponieważ każdy punkt jest jednakowo oddalony od każdego innego punktu.

Naiwny Bayes sobie z tym radzi. Przyjmuje matematycznie błędne założenie (że każda funkcja jest niezależna od każdej innej cechy danej klasy) i nadal przewyższa „inteligentniejsze” modele klasyfikacji tekstu, szczególnie w przypadku małych zestawów treningowych. Uczy się w jednym przejściu przez dane. Skaluje się do milionów funkcji. Tworzy szacunki prawdopodobieństwa (choć często są słabo skalibrowane ze względu na założenie niezależności).

Zrozumienie, dlaczego błędne założenie prowadzi do dobrych przewidywań, uczy czegoś fundamentalnego na temat uczenia maszynowego: najlepszy model nie jest tym najbardziej poprawnym, ale tym, który zapewnia najlepszy kompromis w zakresie odchylenia i wariancji dla danych.

## Koncepcja

### Twierdzenie Bayesa (krótki przegląd)

Twierdzenie Bayesa odwraca prawdopodobieństwa warunkowe:

```
P(class | features) = P(features | class) * P(class) / P(features)
```

Chcemy `P(class | features)` — prawdopodobieństwo, że dokument należy do klasy, biorąc pod uwagę zawarte w nim słowa. Możemy to obliczyć z:
- `P(features | class)` – prawdopodobieństwo zobaczenia tych słów w dokumentach tej klasy
- `P(class)` – prawdopodobieństwo wystąpienia klasy (jak ogólnie powszechny jest spam?)
- `P(features)` -- dowód jest taki sam dla wszystkich klas, więc możemy go zignorować przy porównywaniu

Wygrywa klasa z najwyższym `P(class | features)`.

### Naiwne założenie o niepodległości

Dokładne obliczenie `P(features | class)` wymaga oszacowania łącznego prawdopodobieństwa wszystkich cech razem. Przy słownictwie składającym się z 10 000 słów konieczne byłoby oszacowanie rozkładu na 2^10 000 możliwych kombinacji. Niemożliwe.

Naiwne założenie: każda cecha jest warunkowo niezależna, biorąc pod uwagę klasę.

```
P(w1, w2, ..., wn | class) = P(w1 | class) * P(w2 | class) * ... * P(wn | class)
```

Zamiast jednej niemożliwej wspólnej dystrybucji, szacujesz n prostych rozkładów na cechę. Każdy potrzebuje tylko policzenia.

To założenie jest oczywiście błędne. Słowa „maszyna” i „uczenie się” nie są w żadnym dokumencie niezależne. Ale klasyfikator nie potrzebuje poprawnych szacunków prawdopodobieństwa. Potrzebuje poprawnych rankingów – która klasa ma największe prawdopodobieństwo. Założenie o niezależności wprowadza błędy systematyczne, ale błędy te wpływają na wszystkie klasy w podobny sposób, więc ranking pozostaje poprawny.

### Dlaczego to nadal działa

Trzy powody:

1. **Ranking nad kalibracją.** Klasyfikacja wymaga, aby tylko klasa z najwyższym rankingiem była poprawna. Nawet jeśli P(spam) = 0,99999, a prawdziwe prawdopodobieństwo wynosi 0,7, klasyfikator nadal poprawnie wybiera spam. Nie potrzebujemy poprawnych prawdopodobieństw. Potrzebujemy odpowiedniego zwycięzcy.

2. **Wysokie obciążenie, niska wariancja.** Założenie niezależności jest mocnym założeniem. Mocno ogranicza model, co zapobiega nadmiernemu dopasowaniu. Przy ograniczonych danych szkoleniowych model, który jest nieco błędny, ale stabilny, pokonuje model, który jest teoretycznie poprawny, ale szalenie niestabilny. To jest kompromis wariancji odchylenia w działaniu.

3. **Nadmiarowość funkcji zostaje wyeliminowana.** Skorelowane funkcje dostarczają zbędnych dowodów. Klasyfikator podwójnie liczy ten dowód, ale także podwójnie liczy go dla właściwej klasy. Jeśli „maszyna” i „uczenie się” zawsze pojawiają się razem, oba dostarczają dowodów na istnienie klasy „tech”. Uwaga: liczy się je dwukrotnie, ale w przypadku właściwej klasy liczy się je dwukrotnie.

Czwarty, praktyczny powód: Naiwny Bayes jest niezwykle szybki. Trening polega na pojedynczym przejściu przez częstotliwości zliczania danych. Przewidywanie to mnożenie macierzy. Możesz trenować na milionie dokumentów w ciągu kilku sekund. Ta prędkość oznacza, że ​​możesz szybciej iterować, wypróbowywać więcej zestawów funkcji i przeprowadzać więcej eksperymentów niż w przypadku wolniejszych modeli.

### Matematyka krok po kroku

Prześledźmy to na konkretnym przykładzie. Załóżmy, że mamy dwie klasy: spam i not-spam. W naszym słownictwie znajdują się trzy słowa: „za darmo”, „pieniądze”, „spotkanie”.

Dane treningowe:
- W wiadomościach spamowych 80 razy pojawia się wzmianka o „za darmo”, 60 razy o „pieniędzy”, 10 razy o „spotkaniu” (łącznie 150 słów)
- E-maile niebędące spamem wspominają o „darmowym” 5 razy, „pieniądze” 10 razy, „spotkanie” 100 razy (łącznie 115 słów)
- 40% e-maili to spam, 60% to nie spam

Z wygładzaniem Laplace'a (alfa=1):

```
P(free | spam)    = (80 + 1) / (150 + 3) = 81/153 = 0.529
P(money | spam)   = (60 + 1) / (150 + 3) = 61/153 = 0.399
P(meeting | spam) = (10 + 1) / (150 + 3) = 11/153 = 0.072

P(free | not-spam)    = (5 + 1) / (115 + 3) = 6/118 = 0.051
P(money | not-spam)   = (10 + 1) / (115 + 3) = 11/118 = 0.093
P(meeting | not-spam) = (100 + 1) / (115 + 3) = 101/118 = 0.856
```

Nowy e-mail zawiera: „za darmo” (2 razy), „pieniądze” (1 raz), „spotkanie” (0 razy).

```
log P(spam | email) = log(0.4) + 2*log(0.529) + 1*log(0.399) + 0*log(0.072)
                    = -0.916 + 2*(-0.637) + (-0.919) + 0
                    = -3.109

log P(not-spam | email) = log(0.6) + 2*log(0.051) + 1*log(0.093) + 0*log(0.856)
                        = -0.511 + 2*(-2.976) + (-2.375) + 0
                        = -8.838
```

Spam wygrywa z dużą przewagą. Dwukrotne pojawienie się słowa „bezpłatny” jest mocnym dowodem na spam. Należy zauważyć, że brak „spotkania” wnosi zero do obu sum logarytmicznych (0 * log(P)) — w wielomianowym NB brak słów nie ma żadnego wpływu. To Bernoulli NB wyraźnie modeluje nieobecność słowa.

### Trzy warianty

Naive Bayes występuje w trzech smakach. Każdy model `P(feature | class)` jest inny.

#### Wielomian naiwny Bayesa

Modeluje każdą funkcję jako liczbę. Najlepsze w przypadku danych tekstowych, których funkcjami są częstotliwości słów lub wartości TF-IDF.

```
P(word_i | class) = (count of word_i in class + alpha) / (total words in class + alpha * vocab_size)
```

`alpha` to wygładzanie Laplace'a (objaśnione poniżej). Ten wariant jest podstawą klasyfikacji tekstu.

#### Naiwny Bayes Gaussa

Modeluje każdą cechę jako rozkład normalny. Najlepsze dla funkcji ciągłych.

```
P(x_i | class) = (1 / sqrt(2 * pi * var)) * exp(-(x_i - mean)^2 / (2 * var))
```

Każda klasa ma własną średnią i wariancję dla każdej cechy. Działa to dobrze, gdy funkcje rzeczywiście podążają za krzywą dzwonową w każdej klasie.

#### Bernoulli Naiwny Bayes

Modeluje każdą cechę jako binarną (obecną lub nieobecną). Najlepsze dla krótkich tekstów lub wektorów cech binarnych.

```
P(word_i | class) = (docs in class containing word_i + alpha) / (total docs in class + 2 * alpha)
```

W przeciwieństwie do wielomianu Bernoulli wyraźnie karze brak słowa. Jeśli słowo „bezpłatny” zwykle pojawia się w spamie, ale nie ma go w tym e-mailu, Bernoulli traktuje to jako dowód przeciwko spamowi.

### Kiedy używać poszczególnych wariantów

| Wariant | Typ funkcji | Najlepsze dla | Przykład |
|--------|------------|----------|---------|
| Wielomian | Liczba lub częstotliwości | Klasyfikacja tekstu, zbiór słów | Spam e-mailowy, klasyfikacja tematów |
| Gaussa | Wartości ciągłe | Dane tabelaryczne z normalnymi funkcjami | Klasyfikacja tęczówki, dane czujnika |
| Bernoulliego | Binarny (0/1) | Krótki tekst, binarne wektory cech | Spam SMS, funkcje obecności/nieobecności |

### Wygładzanie Laplace’a

Co się stanie, gdy słowo pojawi się w danych testowych, ale nigdy nie pojawiło się w danych szkoleniowych określonej klasy?

Bez wygładzania: `P(word | class) = 0/N = 0`. Jedno zero pomnożone przez cały iloczyn daje `P(class | features) = 0`, niezależnie od wszystkich innych dowodów. Jedno niewidoczne słowo niszczy całą przepowiednię, niezależnie od tego, jak bardzo potwierdzają ją inne dowody.

Wygładzanie Laplace'a dodaje niewielką liczbę `alpha` (zwykle 1) do każdej liczby funkcji:

```
P(word_i | class) = (count(word_i, class) + alpha) / (total_words_in_class + alpha * vocab_size)
```

Przy alfa=1 każde słowo ma co najmniej małe prawdopodobieństwo. Słowo „discombobulate” pojawiające się w testowej wiadomości e-mail nie zmniejsza już prawdopodobieństwa spamu. Wygładzanie ma interpretację bayesowską: jest równoznaczne z umieszczeniem jednolitego Dirichleta przed rozkładem słów.

Wyższa alfa oznacza silniejsze wygładzenie (bardziej równomierne rozkłady). Niższa alfa oznacza, że ​​model bardziej ufa danym. Alfa to hiperparametr, który dostrajasz.

Efekt alfa:

| Alfa | Efekt | Kiedy używać |
|-------|--------|------------|
| 0,001 | Prawie brak wygładzania, zaufaj danym | Bardzo duży zestaw treningowy, nie oczekuje się żadnych niewidzianych funkcji |
| 0,1 | Lekkie wygładzenie | Duży zestaw treningowy |
| 1,0 | Standardowe wygładzanie Laplace'a | Domyślny punkt początkowy |
| 10,0 | Silne wygładzanie, spłaszcza rozkłady | Bardzo mały zestaw treningowy, oczekiwano wielu niewidzianych funkcji |

### Obliczanie przestrzeni logarytmicznej

Mnożenie setek prawdopodobieństw (każde mniejsze niż 1) powoduje niedomiar zmiennoprzecinkowy. Iloczyn staje się zerem w postaci zmiennoprzecinkowej, mimo że prawdziwą wartością jest bardzo mała liczba dodatnia.

Rozwiązanie: praca w przestrzeni dziennika. Zamiast mnożyć prawdopodobieństwa, dodaj ich logarytmy:

```
log P(class | x1, x2, ..., xn) = log P(class) + sum_i log P(xi | class)
```

To zamienia przewidywanie w iloczyn skalarny:

```
log_scores = X @ log_feature_probs.T + log_class_priors
prediction = argmax(log_scores)
```

Mnożenie macierzy. Dlatego przewidywanie naiwnego Bayesa jest tak szybkie — jest to ta sama operacja, co w przypadku jednowarstwowego modelu liniowego.

### Naiwny Bayes kontra regresja logistyczna

Obydwa są liniowymi klasyfikatorami tekstu. Różnica polega na tym, co modelują.

| Aspekt | Naiwny Bayes | Regresja logistyczna |
|------------|------------|----------------------|
| Wpisz | Generatywne (modele P(X\|Y)) | Dyskryminacyjny (modele P(Y\|X)) |
| Szkolenie | Policz częstotliwości | Optymalizuj funkcję straty |
| Małe dane | Lepiej (silny wcześniej pomaga) | Gorzej (nie na tyle, żeby oszacować wagi) |
| Duże dane | Gorzej (złe założenie boli) | Lepiej (elastyczna granica) |
| Funkcje | Zakłada niezależność | Obsługuje korelacje |
| Prędkość | Pojedyncze przejście, bardzo szybko | Optymalizacja iteracyjna |
| Kalibracja | Małe prawdopodobieństwo | Większe prawdopodobieństwo |

Ogólna zasada: zacznij od Naiwnego Bayesa. Jeśli masz wystarczającą ilość danych i plateau NB, przejdź do regresji logistycznej.

### Potok klasyfikacji

```mermaid
flowchart LR
    A[Raw Text] --> B[Tokenize]
    B --> C[Build Vocabulary]
    C --> D[Count Word Frequencies]
    D --> E[Apply Smoothing]
    E --> F[Compute Log Probabilities]
    F --> G[Predict: argmax P class given words]

    style A fill:#f9f,stroke:#333
    style G fill:#9f9,stroke:#333
```

W praktyce pracujemy w przestrzeni dziennika, aby uniknąć niedomiaru zmiennoprzecinkowego. Zamiast mnożyć wiele małych prawdopodobieństw, dodajemy ich logarytmy:

```
log P(class | features) = log P(class) + sum_i log P(feature_i | class)
```

## Zbuduj to

Kod w `code/naive_bayes.py` implementuje od podstaw zarówno MultinomialNB, jak i GaussianNB.

### WielomianNB

Implementacja od podstaw:

1. **fit(X, y)**: Dla każdej klasy policz częstotliwość każdej cechy. Dodaj wygładzanie Laplace'a. Oblicz prawdopodobieństwo logarytmiczne. Przechowuj priorytety klas (dziennik częstotliwości zajęć).

2. **predict_log_proba(X)**: Dla każdej próbki oblicz log P(klasa) + sumę log P(cecha_i | klasa) dla wszystkich klas. To jest mnożenie macierzy: X @ log_probs.T + log_priors.

3. **predict(X)**: Zwraca klasę z najwyższym prawdopodobieństwem logarytmicznym.

```python
class MultinomialNB:
    def __init__(self, alpha=1.0):
        self.alpha = alpha

    def fit(self, X, y):
        classes = np.unique(y)
        n_classes = len(classes)
        n_features = X.shape[1]

        self.classes_ = classes
        self.class_log_prior_ = np.zeros(n_classes)
        self.feature_log_prob_ = np.zeros((n_classes, n_features))

        for i, c in enumerate(classes):
            X_c = X[y == c]
            self.class_log_prior_[i] = np.log(X_c.shape[0] / X.shape[0])
            counts = X_c.sum(axis=0) + self.alpha
            self.feature_log_prob_[i] = np.log(counts / counts.sum())

        return self
```

Kluczowy spostrzeżenie: po dopasowaniu przewidywanie to po prostu mnożenie macierzy plus obciążenie. To dlatego Naive Bayes jest taki szybki.

### GaussowskiNB

W przypadku cech ciągłych szacujemy średnią i wariancję dla każdej klasy dla każdej cechy:

```python
class GaussianNB:
    def __init__(self):
        pass

    def fit(self, X, y):
        classes = np.unique(y)
        self.classes_ = classes
        self.means_ = np.zeros((len(classes), X.shape[1]))
        self.vars_ = np.zeros((len(classes), X.shape[1]))
        self.priors_ = np.zeros(len(classes))

        for i, c in enumerate(classes):
            X_c = X[y == c]
            self.means_[i] = X_c.mean(axis=0)
            self.vars_[i] = X_c.var(axis=0) + 1e-9
            self.priors_[i] = X_c.shape[0] / X.shape[0]

        return self
```

Predykcja korzysta z pliku PDF Gaussa dla każdej funkcji, pomnożonego przez funkcje (dodane w obszarze dziennika).

### Demo: Klasyfikacja tekstu

Kod generuje syntetyczne dane zawierające zbiór słów symulujące dwie klasy (artykuły techniczne i artykuły sportowe). Każda klasa ma inny rozkład częstotliwości słów. MultimianNB klasyfikuje je na podstawie liczby słów.

Dane syntetyczne działają w ten sposób: tworzymy 200 „słów” (kolumny cech). Słowa 0-39 mają wysoką częstotliwość w artykułach technicznych i niską w sporcie. Słowa 80-119 są często używane w sporcie, a mało w technologii. Słowa 40-79 występują w obu przypadkach ze średnią częstotliwością. Tworzy to realistyczny scenariusz, w którym niektóre słowa są mocnymi wskaźnikami klasy, a inne są szumem.

### Demo: funkcje ciągłe

Kod generuje dane podobne do tęczówki (3 klasy, 4 cechy, klastry Gaussa). GaussianNB klasyfikuje przy użyciu średniej i wariancji dla poszczególnych klas. Każda klasa ma inny środek (wektor średni) i inny rozrzut (wariancję), naśladując dane ze świata rzeczywistego, w których pomiary systematycznie różnią się między kategoriami.

Kod demonstruje również:
- **Porównanie wygładzające:** Trening MultimianNB z różnymi wartościami alfa, aby pokazać wpływ siły wygładzania na dokładność.
- **Eksperyment z wielkością treningu:** Jak poprawia się dokładność NB w miarę wzrostu danych szkoleniowych z 20 do 1600 próbek. NB osiąga przyzwoitą dokładność nawet przy bardzo małej liczbie próbek – to jest jego główna zaleta.
- **Macierz zamieszania:** Precyzja według klasy, zapamiętywanie i wynik w F1 pokazujące, gdzie NB popełnia błędy.

### Prędkość przewidywania

Naiwne przewidywanie Bayesa to mnożenie macierzy. Dla n próbek o cechach d i k klasach:
- WielomianNB: pomnożenie jednej macierzy (n x d) @ (d x k) = O(n * d * k)
- GaussianNB: n * k Gaussian ocen PDF, każda po d funkcji = O(n * d * k)

Obydwa są liniowe w każdym wymiarze. Porównaj to z KNN (który wymaga obliczenia odległości do wszystkich punktów treningowych) lub SVM z jądrem RBF (który wymaga oceny jądra względem wszystkich wektorów wsparcia). NB jest szybszy o rzędy wielkości w momencie przewidywania.

## Użyj tego

W przypadku sklearn oba warianty są jednowierszowe:

```python
from sklearn.naive_bayes import GaussianNB, MultinomialNB

gnb = GaussianNB()
gnb.fit(X_train, y_train)
print(f"GaussianNB accuracy: {gnb.score(X_test, y_test):.3f}")

mnb = MultinomialNB(alpha=1.0)
mnb.fit(X_train_counts, y_train)
print(f"MultinomialNB accuracy: {mnb.score(X_test_counts, y_test):.3f}")
```

Do klasyfikacji tekstu za pomocą sklearn:

```python
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

text_clf = Pipeline([
    ("vectorizer", CountVectorizer()),
    ("classifier", MultinomialNB(alpha=1.0)),
])

text_clf.fit(train_texts, train_labels)
accuracy = text_clf.score(test_texts, test_labels)
```

Kod w `naive_bayes.py` porównuje implementacje od podstaw z implementacjami sklearn na tych samych danych, aby zweryfikować poprawność.

### TF-IDF z Naiwnym Bayesem

Surowe liczby słów dają każdemu słowu równą wagę na wystąpienie. Jednak popularne słowa, takie jak „the” i „is”, pojawiają się często w każdych zajęciach i nie niosą ze sobą żadnych informacji. TF-IDF (częstotliwość terminów - odwrotna częstotliwość dokumentów) zmniejsza wagę popularnych słów i podnosi wagę rzadkich, wyróżniających słów.

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

text_clf = Pipeline([
    ("tfidf", TfidfVectorizer()),
    ("classifier", MultinomialNB(alpha=0.1)),
])
```

Wartości TF-IDF są nieujemne, więc działają z MultinomialNB. Połączenie TF-IDF + MultimianNB jest jedną z najsilniejszych podstaw klasyfikacji tekstu. Często pokonuje bardziej złożone modele na zestawach danych zawierających mniej niż 10 000 próbek szkoleniowych.

### BernoulliNB dla krótkiego tekstu

W przypadku krótkich tekstów (tweety, SMS-y, wiadomości na czacie) BernoulliNB może przewyższać MultinomialNB. W krótkich tekstach jest mało słów, więc informacje o częstotliwości, na których opiera się MultinomialNB, są zaszumione. BernoulliNB interesuje tylko obecność lub nieobecność, co jest bardziej wiarygodne w przypadku krótkiego tekstu.

```python
from sklearn.naive_bayes import BernoulliNB
from sklearn.feature_extraction.text import CountVectorizer

text_clf = Pipeline([
    ("vectorizer", CountVectorizer(binary=True)),
    ("classifier", BernoulliNB(alpha=1.0)),
])
```

Flaga `binary=True` w CountVectorizer konwertuje wszystkie zliczenia na 0/1. Bez tego BernoulliNB nadal działa, ale osiąga wyniki, do których nie został zaprojektowany.

### Kalibracja prawdopodobieństw NB

Prawdopodobieństwa NB są słabo skalibrowane. Kiedy NB podaje P(spam) = 0,95, prawdziwe prawdopodobieństwo może wynosić 0,7. Jeśli potrzebujesz wiarygodnych szacunków prawdopodobieństwa (na przykład, aby ustawić próg lub połączyć z innymi modelami), użyj CalibratedClassifierCV sklearna:

```python
from sklearn.calibration import CalibratedClassifierCV

calibrated_nb = CalibratedClassifierCV(MultinomialNB(), cv=5, method="sigmoid")
calibrated_nb.fit(X_train, y_train)
proba = calibrated_nb.predict_proba(X_test)
```

Odpowiada to regresji logistycznej na podstawie surowych wyników NB przy użyciu walidacji krzyżowej. Otrzymane prawdopodobieństwa są znacznie bliższe prawdziwym częstościom klasowym.

### Typowe problemy

1. **Ujemne wartości cech.** WielomianNB wymaga cech nieujemnych. Jeśli masz wartości ujemne (np. TF-IDF z pewnymi ustawieniami lub znormalizowanymi funkcjami), użyj zamiast tego GaussianNB lub przesuń funkcje na dodatnie.

2. **Cechy zerowej wariancji.** GaussianNB dzieli przez wariancję. Jeżeli cecha ma zerową wariancję dla klasy (wszystkie wartości są identyczne), obliczenia prawdopodobieństwa nie działają. Aby temu zapobiec, kod dodaje mały składnik wygładzający (1e-9) do wszystkich wariancji.

3. **Nierównowaga klas.** Jeśli 99% e-maili nie jest spamem, wcześniejszy współczynnik P(nie-spam) = 0,99 jest tak silny, że przytłacza dowody prawdopodobieństwa. Możesz ustawić priorytety klas ręcznie lub użyć parametru class_prior w sklearn.

4. **Skalowanie funkcji.** WielomianNB nie wymaga skalowania (działa na liczbach). GaussianNB również nie wymaga skalowania (oszacowuje statystyki według funkcji). Jest to zaleta w porównaniu z regresją logistyczną i SVM, które są wrażliwe na skale cech.

## Wyślij to

Ta lekcja daje:
- `outputs/skill-naive-bayes-chooser.md` – umiejętność podejmowania decyzji pozwalająca wybrać właściwy wariant NB
- `code/naive_bayes.py` -- Wielomian NB i GaussianNB od podstaw, z porównaniem sklearn

### Kiedy naiwny Bayes zawodzi

NB zawodzi, gdy założenie niezależności powoduje nieprawidłowe rankingi (a nie tylko nieprawidłowe prawdopodobieństwa). Dzieje się tak, gdy:

1. **Silne interakcje cech.** Jeśli klasa zależy od kombinacji dwóch cech, ale nie żadnej z osobna (wzorce podobne do XOR), NB całkowicie ją pominie. Każda cecha sama w sobie nie dostarcza żadnych dowodów, a NB nie może łączyć ich w sposób nieliniowy.

2. **Wysoce skorelowane cechy z przeciwstawnymi dowodami.** Jeśli cecha A mówi „spam”, a cecha B mówi „nie spam”, ale A i B są doskonale skorelowane (w rzeczywistości zawsze się zgadzają), NB zobaczy sprzeczne dowody tam, gdzie ich nie ma.

3. **Bardzo duże zbiory szkoleniowe.** Przy wystarczającej ilości danych modele dyskryminacyjne, takie jak regresja logistyczna, uczą się prawdziwej granicy decyzyjnej i osiągają lepsze wyniki niż NB. Założenie niezależności, które pomogło w przypadku małych danych, teraz powstrzymuje model.

W praktyce te tryby awarii są rzadkie w przypadku klasyfikacji tekstu. Funkcje tekstowe są liczne, indywidualnie słabe, a błędy założenia o niezależności mają tendencję do znoszenia się. W przypadku danych tabelarycznych z kilkoma silnie skorelowanymi cechami należy najpierw rozważyć regresję logistyczną lub modele oparte na drzewach.

## Ćwiczenia

1. **Eksperyment wygładzający.** Trenuj wielomian NB na danych tekstowych z wartościami alfa 0,01, 0,1, 1,0, 10,0 i 100,0. Dokładność wykresu vs alfa. Gdzie osiąga szczyt wydajności? Dlaczego bardzo wysoka alfa boli?

2. **Test niezależności funkcji.** Weź prawdziwy tekstowy zbiór danych. Wybierz dwa słowa, które są ze sobą wyraźnie powiązane („maszyna” i „uczenie się”). Oblicz P(słowo1 | klasa) * P(słowo2 | klasa) i porównaj z P(słowo1 ORAZ słowo2 | klasa). Jak błędne jest założenie o niezależności? Czy ma to wpływ na dokładność klasyfikacji?

3. **Implementacja Bernoulliego.** Rozszerz kod o klasę BernoulliNB. Konwertuj zbiór słów na binarny (obecny/nieobecny) i porównaj dokładność z MultimianNB na danych tekstowych. Kiedy Bernoulli wygrywa?

4. **NB a regresja logistyczna.** Trenuj oba na danych tekstowych. Zacznij od 100 próbek treningowych i zwiększaj do 10 000. Dokładność wykresu a wielkość zestawu szkoleniowego dla obu. W którym momencie regresja logistyczna wyprzedza Naive Bayes?

5. **Filtr spamu.** Zbuduj kompletny klasyfikator spamu: tokenizuj surowy tekst wiadomości e-mail, buduj słownictwo, twórz funkcje zbioru słów, trenuj MultinomialNB, oceniaj z precyzją i zapamiętywaniem (nie tylko dokładnością – dlaczego?).

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|----------------------|
| Naiwny Bayes | „Prosty klasyfikator probabilistyczny” | Klasyfikator stosujący twierdzenie Bayesa przy założeniu, że cechy są warunkowo niezależne, biorąc pod uwagę klasę |
| Warunkowa niezależność | „Funkcje nie wpływają na siebie” | P(A, B \| C) = P(A \| C) * P(B \| C) -- wiedza o B nie mówi nic nowego o A, gdy poznasz C |
| Wygładzanie Laplace'a | „Dodaj jedno wygładzanie” | Dodanie małej liczby do każdej funkcji, aby zapobiec zdominowaniu przewidywania przez zerowe prawdopodobieństwa |
| Wcześniej | „W co wierzyłeś, zanim zobaczyłeś dane” | P(klasa) -- prawdopodobieństwo wystąpienia każdej klasy przed zaobserwowaniem jakichkolwiek cech |
| Prawdopodobieństwo | „Jak dobrze pasują dane” | P(cechy \| klasa) -- prawdopodobieństwo zaobserwowania tych cech, jeśli znana jest klasa |
| Tylny | „W co wierzysz po zobaczeniu danych” | P(class \| cechy) -- zaktualizowane prawdopodobieństwo klasy po zaobserwowaniu cech |
| Model generatywny | „Modele sposobu generowania danych” | Model, który uczy się P(X \| Y) i P(Y), a następnie wykorzystuje twierdzenie Bayesa, aby otrzymać P(Y \| X) |
| Model dyskryminacyjny | „Modele granicy decyzyjnej” | Model, który bezpośrednio uczy się P(Y \| X) bez modelowania sposobu generowania X
| Zaloguj prawdopodobieństwo | „Unikaj niedomiaru” | Praca z log P zamiast P, aby zapobiec zmianie iloczynu wielu małych liczb na zero w zmiennoprzecinkowej |

## Dalsze czytanie

- [dokumentacja scikit-learn Naive Bayesa](https://scikit-learn.org/stable/modules/naive_bayes.html) - wszystkie trzy warianty ze szczegółami matematycznymi
- [McCallum i Nigam, A Comparison of Event Models for Naive Bayes Text Classification (1998)](https://www.cs.cmu.edu/~knigam/papers/multinomial-aaaiws98.pdf) - klasyczne porównanie wielomianu i Bernoulliego dla tekstu
- [Rennie i in., Tackling the Poor Assumptions of Naive Bayes Text Classifiers (2003)](https://people.csail.mit.edu/jrennie/papers/icml03-nb.pdf) — ulepszenia NB dla tekstu
- [Ng i Jordan, On Discriminative vs. Generative Classifiers (2001)](https://ai.stanford.edu/~ang/papers/nips01-discriminativegenerative.pdf) - udowadnia, że NB zbiega się szybciej niż LR przy mniejszej ilości danych