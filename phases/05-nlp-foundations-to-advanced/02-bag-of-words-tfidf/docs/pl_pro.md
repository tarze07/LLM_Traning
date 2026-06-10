# Zbiór słów, TF-IDF i reprezentacja tekstu

> Najpierw licz, potem myśl. W 2026 roku TF-IDF wciąż przewyższa embeddingi w niektórych ściśle zdefiniowanych zadaniach.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 5 · Lekcja 01 (Przetwarzanie tekstu), Faza 2 · Lekcja 02 (Regresja liniowa od podstaw)
**Czas:** ~75 minut

## Problem

Model potrzebuje liczb. Ty dysponujesz tekstem (łańcuchami znaków).

Każdy potok NLP musi odpowiedzieć na to samo pytanie: jak przekształcić sekwencję tokenów o zmiennej długości w wektor o stałym rozmiarze, który może być przetworzony przez klasyfikator? Pierwszym wybranym rozwiązaniem było to najprostsze, które po prostu działało – policzyć słowa i stworzyć wektor.

Ten wektorowy model obsłużył w środowiskach produkcyjnych więcej zadań NLP niż jakikolwiek model embeddingów: filtry spamu, klasyfikatory tematów, wykrywanie anomalii w logach systemowych, ranking wyszukiwania (przed BM25), pierwszą falę analizy sentymentu czy akademickie testy porównawcze NLP przez całą pierwszą dekadę rozwoju tej dziedziny. W 2026 roku praktycy wciąż sięgają po niego w pierwszej kolejności przy wąskich zadaniach klasyfikacyjnych. Jest szybki, łatwo interpretowalny i w zadaniach opartych na obecności słów często dorównuje modelom embeddingów o rozmiarze 400 milionów parametrów.

W tej lekcji zbudujemy od podstaw model Bag of Words (worek słów), a następnie TF-IDF. Następnie pokażemy, jak osiągnąć to samo w trzech linijkach kodu za pomocą scikit-learn. Na koniec omówimy scenariusze awaryjne, które zmuszają do przejścia na embeddingi.

## Pojęcia

**Bag of Words (BoW)** ignoruje kolejność słów. Dla każdego dokumentu oblicza liczbę wystąpień poszczególnych słów ze słownika. Długość wektora jest równa rozmiarowi słownika. Pozycja `i` odpowiada liczbie wystąpień słowa o indeksie `i`.

**TF-IDF** modyfikuje wagi BoW. Słowo, które pojawia się w każdym dokumencie, nie niesie żadnej wartości informacyjnej (nie różnicuje tekstów), dlatego jego waga jest zmniejszana. Z kolei słowo rzadkie w skali całego korpusu, ale częste w konkretnym dokumencie, stanowi silny sygnał, więc jego waga rośnie.

```
TF-IDF(w, d) = TF(w, d) * IDF(w)
             = count(w in d) / |d| * log(N / df(w))
```

Gdzie `TF` to częstość termu w dokumencie (term frequency), `df` to częstość dokumentowa (document frequency – liczba dokumentów zawierających to słowo), a `N` to całkowita liczba dokumentów. Logarytm (`log`) zapobiega zdominowaniu wyniku przez powszechnie występujące słowa.

Kluczowa cecha: obie metody generują rzadkie wektory (sparse vectors) z łatwymi do zinterpretowania wymiarami. Możesz przeanalizować wagi wytrenowanego klasyfikatora i odczytać, które słowa decydują o przypisaniu dokumentu do danej klasy. W przypadku 768-wymiarowych embeddingów BERT jest to niemożliwe.

## Implementacja krok po kroku

### Krok 1: Budowanie słownika

```python
def build_vocab(docs):
    vocab = {}
    for doc in docs:
        for token in doc:
            if token not in vocab:
                vocab[token] = len(vocab)
    return vocab
```

Wejście: lista przetworzonych (stokenizowanych) dokumentów. Wyjście: słownik `{word: index}`. Stabilna kolejność wstawiania w Pythonie sprawia, że słowo o indeksie 0 to pierwszy napotkany wyraz w pierwszym dokumencie. Konwencje bywają różne – np. scikit-learn domyślnie sortuje słownik alfabetycznie.

### Krok 2: Worek słów (Bag of Words)

```python
def bag_of_words(docs, vocab):
    matrix = [[0] * len(vocab) for _ in docs]
    for i, doc in enumerate(docs):
        for token in doc:
            if token in vocab:
                matrix[i][vocab[token]] += 1
    return matrix
```

```python
>>> docs = [["cat", "sat", "on", "mat"], ["cat", "cat", "ran"]]
>>> vocab = build_vocab(docs)
>>> bag_of_words(docs, vocab)
[[1, 1, 1, 1, 0], [2, 0, 0, 0, 1]]
```

Wiersze reprezentują dokumenty, a kolumny indeksy słownika. Wartość pod indeksem `[i][j]` oznacza, ile razy słowo `j` występuje w dokumencie `i`. W dokumencie o indeksie 1 słowo `cat` występuje dwukrotnie, natomiast w dokumencie 0 słowo `ran` występuje zero razy.

### Krok 3: Częstość termów i częstość dokumentowa

```python
import math

def term_frequency(doc_bow, doc_length):
    return [c / doc_length if doc_length else 0 for c in doc_bow]

def document_frequency(bow_matrix):
    df = [0] * len(bow_matrix[0])
    for row in bow_matrix:
        for j, count in enumerate(row):
            if count > 0:
                df[j] += 1
    return df

def inverse_document_frequency(df, n_docs):
    return [math.log((n_docs + 1) / (d + 1)) + 1 for d in df]
```

Warto zwrócić uwagę na dwa zabiegi wygładzające (smoothing). Zastosowanie `(n_docs + 1) / (df + 1)` pozwala uniknąć dzielenia przez zero. Dodanie `1` na końcu gwarantuje, że słowo obecne w każdym dokumencie zachowa wagę IDF równą 1 (a nie 0), co jest zgodne z domyślnym zachowaniem biblioteki scikit-learn. Inne implementacje stosują klasyczny wzór `log(N / df)`. Oba podejścia są poprawne, lecz wariant z wygładzaniem jest bardziej stabilny.

### Krok 4: TF-IDF

```python
def tfidf(bow_matrix):
    n_docs = len(bow_matrix)
    df = document_frequency(bow_matrix)
    idf = inverse_document_frequency(df, n_docs)
    out = []
    for row in bow_matrix:
        length = sum(row)
        tf = term_frequency(row, length)
        out.append([tf_j * idf_j for tf_j, idf_j in zip(tf, idf)])
    return out
```

```python
>>> docs = [
...     ["the", "cat", "sat"],
...     ["the", "dog", "sat"],
...     ["the", "cat", "ran"],
... ]
>>> vocab = build_vocab(docs)
>>> bow = bag_of_words(docs, vocab)
>>> tfidf(bow)
```

Mamy trzy dokumenty i pięć słów (`the`, `cat`, `sat`, `dog`, `ran`). Słowo `the` występuje we wszystkich trzech dokumentach, więc jego waga IDF jest niska. Słowo `dog` występuje tylko w jednym, co daje mu wysoką wagę IDF. Wektory są rzadkie (większość wartości to zera lub małe liczby), a słowa kluczowe zostają uwypuklone.

### Krok 5: Normalizacja wierszy L2

```python
def l2_normalize(matrix):
    out = []
    for row in matrix:
        norm = math.sqrt(sum(x * x for x in row))
        out.append([x / norm if norm else 0 for x in row])
    return out
```

Bez normalizacji dłuższe dokumenty miałyby wektory o większych modułach (długościach), co fałszowałoby wyniki porównania podobieństwa. Normalizacja L2 rzutuje wektor każdego dokumentu na hipersferze jednostkowej. Dzięki temu podobieństwo cosinusowe (cosine similarity) między wierszami sprowadza się do prostego iloczynu skalarnego.

## Zastosowanie w praktyce

Biblioteka scikit-learn dostarcza zoptymalizowane wersje produkcyjne.

```python
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

docs = ["the cat sat on the mat", "the dog sat on the mat", "the cat ran"]

bow_vectorizer = CountVectorizer()
bow = bow_vectorizer.fit_transform(docs)
print(bow_vectorizer.get_feature_names_out())
print(bow.toarray())

tfidf_vectorizer = TfidfVectorizer()
tfidf = tfidf_vectorizer.fit_transform(docs)
print(tfidf.toarray().round(3))
```

Klasa `CountVectorizer` wykonuje tokenizację, buduje słownik i tworzy macierz BoW w jednym kroku. `TfidfVectorizer` dodatkowo nakłada wagi IDF oraz normalizację L2. Oba narzędzia zwracają macierze rzadkie (sparse matrices). Przy dużych korpusach (np. 100 tys. dokumentów) reprezentacja gęsta (dense) nie zmieściłaby się w pamięci RAM – należy pracować na macierzach rzadkich tak długo, jak to możliwe.

Parametry konfiguracyjne o kluczowym znaczeniu:

| Argument | Efekt |
|-----|--------|
| `ngram_range=(1, 2)` | Dołącza bigramy. Zwykle podnosi skuteczność klasyfikacji. |
| `min_df=2` | Odrzuca słowa występujące w mniej niż 2 dokumentach. Ogranicza rozmiar słownika przy zaszumionych danych. |
| `max_df=0.95` | Usuwa słowa występujące w ponad 95% dokumentów. Pozwala to na automatyczne usuwanie stop-words bez używania sztywnej listy. |
| `stop_words="english"` | Wbudowana lista stop-words dla języka angielskiego. Zależy od zadania – analiza sentymentu *nie* powinna usuwać negacji. |
| `sublinear_tf=True` | Stosuje logarytmiczne skalowanie częstości termów (`1 + log(tf)` zamiast `tf`). Pomaga to w sytuacji, gdy jedno słowo powtarza się wielokrotnie w pojedynczym dokumencie. |

### Obszary, w których TF-IDF wciąż wygrywa (stan na 2026 r.)

- Klasyfikacja spamu, tagowanie tematów, wykrywanie anomalii w logach systemowych. Kluczowa jest tu sama obecność słów, a nie subtelności semantyczne.
- Projekty o bardzo małej ilości danych treningowych (np. kilkaset etykietowanych przykładów). Połączenie TF-IDF i regresji logistycznej nie wymaga kosztownego treningu wstępnego.
- Projekty o rygorystycznych wymaganiach czasowych. Połączenie TF-IDF i modelu liniowego wykonuje predykcję w mikrosekundy, podczas gdy generowanie embeddingów przez Transformer zajmuje od 10 do 100 ms.
- Systemy wymagające pełnej wyjaśnialności decyzji. Analiza wag modelu liniowego pozwala jednoznacznie wskazać słowa kluczowe, które zaważyły na klasyfikacji.

### Gdzie TF-IDF zawodzi

1. **Ślepota semantyczna.** Porównajmy dwa zdania:
   - „Film wcale nie był dobry.”
   - „Film był znakomity.”

   Pierwsza opinia jest negatywna, druga pozytywna. Ich wspólne słowa w reprezentacji TF-IDF to dokładnie `{the, movie, was}`. Klasyfikator oparty na BoW musi na podstawie danych treningowych nauczyć się, że obecność słowa `not` w sąsiedztwie `good` odwraca znaczenie (sentyment). Z odpowiednią ilością danych jest to możliwe, ale nigdy nie będzie tak efektywne jak użycie modelu analizującego strukturę składniową.

2. **Obsługa słów spoza słownika (OOV – Out-Of-Vocabulary) podczas wnioskowania.** Model BoW wytrenowany na recenzjach z bazy IMDb nie wie, jak zinterpretować słowo `Zoomer-approved`, jeśli nie wystąpiło ono w zbiorze treningowym. Modele oparte na embeddingach podsłów (lekcja 04) potrafią sobie z tym poradzić, natomiast TF-IDF jest na to bezradny.

### Podejście hybrydowe: embeddingi ważone wartościami TF-IDF

Praktyczne rozwiązanie (stan na 2026 r.) dla zbiorów o średniej wielkości: wykorzystanie wag TF-IDF jako uproszczonego mechanizmu uwagi (attention) przy agregacji embeddingów słów.

```python
def tfidf_weighted_embedding(doc, tfidf_scores, embedding_table, dim):
    vec = [0.0] * dim
    total_weight = 0.0
    for token in doc:
        if token not in embedding_table or token not in tfidf_scores:
            continue
        weight = tfidf_scores[token]
        emb = embedding_table[token]
        for i in range(dim):
            vec[i] += weight * emb[i]
        total_weight += weight
    if total_weight == 0:
        return vec
    return [v / total_weight for v in vec]
```

Łączymy w ten sposób reprezentację semantyczną z embeddingów oraz uwypuklenie unikalnych pojęć dzięki TF-IDF. Klasyfikator uczy się na zagregowanych wektorach. Takie podejście bardzo dobrze sprawdza się w analizie sentymentu, klasyfikacji tematów czy intencji dla zbiorów poniżej 50 tys. etykietowanych przykładów.

## Szablon do wdrożenia

Zapisz go jako `outputs/prompt-vectorization-picker.md`:

```markdown
---
name: vectorization-picker
description: Dla danego zadania klasyfikacji tekstu poleca BoW, TF-IDF, osadzanie lub podejście hybrydowe.
phase: 5
lesson: 02
---

Jesteś doradcą ds. strategii wektoryzacji tekstu. Na podstawie opisu zadania określ:

1. Wybór reprezentacji tekstu (BoW, TF-IDF, embeddingi z modelu Transformer lub hybryda) wraz z jednozdaniowym uzasadnieniem.
2. Szczegółowa konfiguracja wektoryzatora z podaniem nazwy biblioteki oraz kluczowych argumentów (`ngram_range`, `min_df`, `max_df`, `sublinear_tf`, `stop_words`).
3. Jeden scenariusz awaryjny (testowy) do zweryfikowania przed wdrożeniem.

Odmów polecania embeddingów w przypadku zbiorów mniejszych niż 500 etykietowanych przykładów (chyba że użytkownik wykaże, że TF-IDF nie radzi sobie z semantyką tekstu). Odmów usuwania stop-words w przypadku analizy sentymentu (słowa takie jak 'nie' niosą kluczowy ładunek emocjonalny). Wyraźnie zaznacz, że problem braku zbalansowania klas wymaga dodatkowych działań wykraczających poza zmianę wektoryzatora.

Przykładowe wejście: "Klasyfikacja 30 tys. zgłoszeń do obsługi klienta na 12 kategorii. Większość zgłoszeń ma 2-3 zdania. Tylko angielski. Wymagana interpretowalność na potrzeby logów audytowych."

Przykładowy wynik:

- Wybór reprezentacji: TF-IDF. Zbiorcza próba 30 tys. dokumentów jest wystarczająca, a wymóg pełnej interpretowalności wyklucza zastosowanie gęstych embeddingów.
- Konfiguracja: `TfidfVectorizer(ngram_range=(1, 2), min_df=3, max_df=0.95, sublinear_tf=True, stop_words=None)`. Zachowaj stop-words – słowa te w kontekście intencji bywają kluczowe (porównaj: „nie działa” vs „działa”).
- Przypadek testowy: upewnij się, czy próg `min_df=3` nie odrzuca rzadkich, lecz kluczowych pojęć powiązanych z nielicznymi kategoriami. Przeanalizuj słownik zwracany przez `get_feature_names_out` po przefiltrowaniu pod kątem konkretnych klas.
```

## Ćwiczenia

1. **Łatwe.** Zaimplementuj funkcję `cosine_similarity(doc_vec_a, doc_vec_b)` dla wektorów TF-IDF znormalizowanych metodą L2. Upewnij się, że identyczne dokumenty dają wynik 1.0, a dokumenty o całkowicie rozłącznych słownikach dają wynik 0.0.
2. **Średnie.** Dodaj obsługę parametrów n-gramowych do funkcji `bag_of_words`. Parametr `n` powinien określać stopień n-gramów. Sprawdź, czy dla `n=2` na liście `["the", "cat", "sat"]` funkcja poprawnie zlicza bigramy `["the cat", "cat sat"]`.
3. **Trudne.** Zaimplementuj opisaną wyżej metodę hybrydową (embeddingi ważone TF-IDF) przy użyciu 100-wymiarowych wektorów GloVe (pobierz i zapisz w lokalnym cache). Porównaj dokładność klasyfikacji z klasycznym TF-IDF oraz zwykłym uśrednianiem embeddingów na zbiorze 20 Newsgroups. Opisz wyniki.

## Kluczowe pojęcia

| Pojęcie | Potoczne rozumienie | Rzeczywiste znaczenie |
|------|-----------------|----------------------|
| BoW | Worek słów | Reprezentacja wektorowa zliczeń słów ze słownika w dokumencie. Całkowicie pomija kolejność słów. |
| TF | Częstość termów | Liczba wystapień słowa w dokumencie, zazwyczaj znormalizowana względem jego długości. |
| DF | Częstość dokumentowa | Liczba dokumentów w całym korpusie zawierających dane słowo przynajmniej raz. |
| IDF | Odwrotna częstość dokumentowa | Wartość `log(N / df)` po wygładzeniu. Obniża wagi słów występujących powszechnie we wszystkich dokumentach. |
| Wektor rzadki | Wektor o wielu zerach | Słownik ma zazwyczaj od 10 do 100 tys. pozycji, z których tylko niewielka część występuje w pojedynczym dokumencie. |
| Podobieństwo cosinusowe | Kąt między wektorami | Iloczyn skalarny wektorów o długości jednostkowej (znormalizowanych L2). Wartość 1.0 oznacza pełną tożsamość kierunków, 0.0 – ortogonalność. |

## Dalsze czytanie

- [scikit-learn — Feature Extraction](https://scikit-learn.org/stable/modules/feature_extraction.html#text-feature-extraction) — oficjalna dokumentacja API wraz z opisem każdego parametru.
- [Salton, G., Buckley, C. (1988). Term-weighting approaches in automatic text retrieval](https://www.sciencedirect.com/science/article/pii/0306457388900210) — klasyczny artykuł, który ugruntował pozycję TF-IDF na kolejną dekadę.
- [Thonikkadavan, A. (2026). Why TF-IDF still beats embeddings](https://medium.com/@cmtwskb/why-tf-idf-still-beats-embeddings-ad85c123e1b2) — analiza współczesnych scenariuszy, w których tradycyjne metody wygrywają z sieciami neuronowymi.
