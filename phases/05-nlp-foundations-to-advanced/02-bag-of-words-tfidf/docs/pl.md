# Zbiór słów, TF-IDF i reprezentacja tekstu

> Najpierw policz, pomyśl później. W 2026 r. TF-IDF nadal przewyższa osadzanie w dobrze określonych zadaniach.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 5 · 01 (Przetwarzanie tekstu), Faza 2 · 02 (Regresja liniowa od podstaw)
**Czas:** ~75 minut

## Problem

Model potrzebuje numerów. Masz sznurki.

Każdy potok NLP musi odpowiedzieć na to samo pytanie. Jak zamienić strumień tokenów o zmiennej długości w wektor o stałym rozmiarze, który może wykorzystać klasyfikator. Pierwsza odpowiedź, na którą padło pole, była najgłupszą, która zadziałała. Policz słowa. Zrób wektor.

Ten wektor zawiera więcej produkcyjnego NLP niż jakikolwiek model osadzania. Filtry spamu, klasyfikatory tematów, wykrywanie anomalii w logach, ranking wyszukiwania (przed BM25), pierwsza fala analizy nastrojów, pierwsza dekada akademickich testów porównawczych NLP. Praktycy 2026 nadal sięgają po niego w pierwszej kolejności przy zadaniach wąskiej klasyfikacji. Jest szybki, łatwy w interpretacji i często nie do odróżnienia od modelu osadzania zawierającego 400M parametrów w zadaniach, w których liczy się obecność słów.

Ta lekcja buduje od zera zbiór słów, a następnie TF-IDF. Następnie pokazuje scikit-learn, robiąc to samo w trzech liniach. Następnie nazywa tryb awarii, który powoduje, że sięgasz po osady.

## Koncepcja

**Worek słów (BoW)** burzy porządek. W każdym dokumencie policz, ile razy pojawia się każde słowo słownictwa. Długość wektora to rozmiar słownictwa. Pozycja `i` to liczba słów `i`.

**TF-IDF** ponownie waży BoW. Słowo pojawiające się w każdym dokumencie nie zawiera żadnych informacji, więc zmniejsz je. Słowo rzadkie w korpusie, ale częste w pojedynczym dokumencie jest sygnałem, więc zwiększ jego skalę.

```
TF-IDF(w, d) = TF(w, d) * IDF(w)
             = count(w in d) / |d| * log(N / df(w))
```

Gdzie `TF` to częstotliwość występowania terminów w dokumencie, `df` to częstotliwość występowania dokumentów (ile dokumentów zawiera to słowo), `N` to całkowita liczba dokumentów. `log` utrzymuje wagę ograniczoną dla wszechobecnych słów.

Kluczowa właściwość: oba generują rzadkie wektory z możliwymi do interpretacji osiami. Możesz przyjrzeć się wagom przeszkolonego klasyfikatora i przeczytać, które słowa popychają dokument do poszczególnych klas. Nie można tego zrobić za pomocą 768-wymiarowego osadzania BERT.

## Zbuduj to

### Krok 1: zbuduj słownictwo

```python
def build_vocab(docs):
    vocab = {}
    for doc in docs:
        for token in doc:
            if token not in vocab:
                vocab[token] = len(vocab)
    return vocab
```

Dane wejściowe: lista tokenizowanych dokumentów (wystarczy dowolny tokenizator na poziomie słowa; `code/main.py` w tej lekcji używa uproszczonego wariantu małych liter). Dane wyjściowe: `{word: index}` dykt. Stabilna kolejność wstawiania oznacza, że ​​słowo o indeksie 0 jest pierwszym słowem widocznym w pierwszym dokumencie. Konwencja jest różna; scikit-learn sortuje alfabetycznie.

### Krok 2: zbiór słów

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

Wiersze to dokumenty. Kolumny są indeksami słownictwa. Wpis `[i][j]` to „ile razy słowo `j` pojawia się w dokumencie `i`." Dokument 1 zawiera dwukrotnie `cat`, ponieważ tak się stało. Dokument 0 zawiera `ran` zero razy, ponieważ tak nie było.

### Krok 3: częstotliwość terminów i częstotliwość dokumentów

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

Warto wymienić dwa triki wygładzające. `(n+1)/(d+1)` pozwala uniknąć `log(x/0)`. Końcowy `+1` gwarantuje, że słowo w każdym dokumencie nadal będzie miało IDF 1 (a nie 0), co odpowiada wartości domyślnej scikit-learn. Inne implementacje używają surowego `log(N/df)`. Obydwa działają; wersja wygładzona jest bardziej przyjazna.

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

Trzy dokumenty, pięć słów (`the`, `cat`, `sat`, `dog`, `ran`). `the` pojawia się we wszystkich trzech, więc jego IDF jest niski. `dog` występuje w jednym, więc jego IDF jest wysoki. Wektory są rzadkie (większość wpisów jest mała), a słowa wyróżniające pojawiają się.

### Krok 5: Normalizacja wierszy L2

```python
def l2_normalize(matrix):
    out = []
    for row in matrix:
        norm = math.sqrt(sum(x * x for x in row))
        out.append([x / norm if norm else 0 for x in row])
    return out
```

Bez normalizacji dłuższy dokument zyskuje większy wektor i dominuje w wynikach podobieństwa. Normalizacja L2 umieszcza każdy dokument w hipersferze jednostkowej. Cosinus podobieństwa między wierszami jest teraz tylko iloczynem skalarnym.

## Użyj tego

scikit-learn dostarcza wersję produkcyjną.

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

`CountVectorizer` wykonuje tokenizację, słownictwo i BoW w jednym wywołaniu. `TfidfVectorizer` dodaje wagę IDF i normalizację L2. Obie zwracają rzadkie macierze. W przypadku dokumentów o objętości 100 tys. wersja gęsta nie mieści się w pamięci; pozostań rzadki, dopóki klasyfikator nie zażąda gęstego.

Pokrętła, które zmieniają wszystko:

| Argument | Efekt |
|-----|--------|
| `ngram_range=(1, 2)` | Dołącz bigramy. Zwykle zwiększa klasyfikację. |
| `min_df=2` | Upuść słowa w mniej niż 2 dokumentach. Przycina słownictwo w przypadku zaszumionych danych. |
| `max_df=0.95` | Upuść słowa w ponad 95% dokumentów. Przybliżone usuwanie słów blokujących bez zakodowanej na stałe listy. |
| `stop_words="english"` | wbudowana lista słów blokowanych scikit-learn. Zależna od zadania — analiza nastrojów *nie* powinna odrzucać negacji. |
| `sublinear_tf=True` | Użyj `1 + log(tf)` zamiast surowego `tf`. Pomaga, gdy termin powtarza się wiele razy w jednym dokumencie. |

### Kiedy TF-IDF nadal zwycięża (stan na 2026 r.)

- Wykrywanie spamu, oznaczanie tematów, oznaczanie anomalii w logach. Liczy się obecność słowa; niuanse semantyczne nie.
- Systemy wymagające niewielkiej ilości danych (setki oznaczonych przykładów). TF-IDF plus regresja logistyczna nie wiąże się z kosztami szkolenia wstępnego.
- Wszędzie tam, gdzie liczy się opóźnienie. TF-IDF plus model liniowy odpowiada w mikrosekundach. Osadzanie dokumentu przez transformator zajmuje 10-100ms.
- Systemy, które muszą wyjaśniać swoje przewidywania. Sprawdź współczynniki klasyfikatora. Powodem są najlepsze pozytywne słowa.

### Kiedy TF-IDF zawiedzie

Porażka ślepoty semantycznej. Rozważ te dwa dokumenty:

- „Film wcale nie był dobry”.
- „Film był znakomity”.

Jednym z nich jest negatywna recenzja. Jeden jest pozytywny. Ich nakładanie się na siebie TF-IDF wynosi dokładnie `{the, movie, was}`. Klasyfikator zbioru słów musi zapamiętać, że słowo `not` w pobliżu `good` odwraca etykietę. Może się tego nauczyć na wystarczającej liczbie danych, ale nigdy tak sprawnie, jak model rozumiejący składnię.

Druga porażka: słowa spoza słownika podczas wnioskowania. Model BoW wyszkolony na recenzjach IMDb nie ma pojęcia, co zrobić z `Zoomer-approved`, jeśli ten token nigdy nie pojawił się podczas szkolenia. Osadzanie podsłów (lekcja 04) sobie z tym radzi. TF-IDF nie może.

### Hybrydowe: osadzania ważone TF-IDF

Pragmatyczne ustawienie domyślne na rok 2026 w zakresie klasyfikacji średnich danych: używaj wag TF-IDF jako uwagi zamiast osadzania słów.

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

Otrzymujesz pojemność semantyczną dzięki osadzaniu i podkreślaniu rzadkich słów dzięki TF-IDF. Klasyfikator trenuje na zbiorczym wektorze. To samo w sobie jest lepsze pod względem klasyfikacji nastrojów, tematów i zamiarów poniżej około 50 tys. oznaczonych przykładów.

## Wyślij to

Zapisz jako `outputs/prompt-vectorization-picker.md`:

```markdown
---
name: vectorization-picker
description: Dla danego zadania klasyfikacji tekstu poleca BoW, TF-IDF, osadzanie lub podejście hybrydowe.
phase: 5
lesson: 02
---

Polecasz strategię wektoryzacji tekstu. Biorąc pod uwagę opis zadania, wygeneruj:

1. Reprezentacja (BoW, TF-IDF, osadzanie transformatorowe lub hybryda). Wyjaśnij dlaczego w jednym zdaniu.
2. Konkretna konfiguracja wektoryzatora. Podaj nazwę biblioteki. Wypisz argumenty (`ngram_range`, `min_df`, `max_df`, `sublinear_tf`, `stop_words`).
3. Jeden tryb awarii do przetestowania przed wysyłką.

Odmów polecania osadzania, gdy użytkownik ma mniej niż 500 oznaczonych przykładów, chyba że wykaże dowody na awarię semantyczną w wartości bazowej TF-IDF. Odmów usunięcia stopwords w przypadku analizy sentymentu (negacje niosą sygnał). Oznacz nierównowagę klas jako wymagającą czegoś więcej niż tylko zmiany wektoryzatora.

Przykładowe wejście: "Klasyfikacja 30 tys. zgłoszeń do obsługi klienta na 12 kategorii. Większość zgłoszeń ma 2-3 zdania. Tylko angielski. Wymagana interpretowalność na potrzeby logów audytowych."

Przykładowe wyjście:

- Reprezentacja: TF-IDF. 30 tys. przykładów to nie jest mało; wymóg interpretowalności wyklucza gęste osadzanie.
- Konfiguracja: `TfidfVectorizer(ngram_range=(1, 2), min_df=3, max_df=0.95, sublinear_tf=True, stop_words=None)`. Zachowaj stopwords, ponieważ słowa kluczowe kategorii czasem są stopwordsami ("not working" vs "working").
- Test awarii: sprawdź, czy `min_df=3` nie odrzuca rzadkich słów kluczowych kategorii. Uruchom `get_feature_names_out` przefiltrowane według klas i oceń wzrokowo.
```

## Ćwiczenia

1. **Łatwe.** Zaimplementuj `cosine_similarity(doc_vec_a, doc_vec_b)` na wyjściu TF-IDF znormalizowanym L2. Sprawdź, czy identyczne dokumenty uzyskują ocenę 1,0, a dokumenty zawierające rozłączne słownictwo – 0,0.
2. **Średni.** Dodaj obsługę `n-gram` do `bag_of_words`. Parametr `n` generuje zliczenia w granicach `n`-gramów. Sprawdź, czy `n=2` na `["the", "cat", "sat"]` generuje liczbę bigramów dla `["the cat", "cat sat"]`.
3. **Trudne.** Zbuduj powyższą hybrydę osadzania ważonego TF-IDF, używając wektorów GloVe 100d (pobierz raz, pamięć podręczna). Porównaj dokładność klasyfikacji ze zwykłym osadzeniem TF-IDF i zwykłym osadzeniem średniej puli w zestawie danych 20 grup dyskusyjnych. Zgłoś, który wygrywa gdzie.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Łuk | Wektor częstotliwości słowa | Zlicza słowa słownictwa w jednym dokumencie. Wyrzuca porządek. |
| TF | Częstotliwość terminów | Liczba słów w dokumencie, opcjonalnie znormalizowana według długości dokumentu. |
| DF | Częstotliwość dokumentów | Liczba dokumentów zawierających słowo co najmniej raz. |
| IDF | Odwrotna częstotliwość dokumentów | `log(N / df)` wygładzono. Zmniejsza wagę słów, które pojawiają się wszędzie. |
| Rzadki wektor | Przeważnie zera | Słownictwo obejmuje zazwyczaj 10–100 tys. słów; większości z nich nie ma w żadnym dokumencie. |
| Cosinus podobieństwo | Kąt wektorowy | Iloczyn skalarny wektorów znormalizowanych L2. 1 jest identyczne, 0 jest ortogonalne. |

## Dalsze czytanie

- [scikit-learn — ekstrakcja funkcji z tekstu](https://scikit-learn.org/stable/modules/feature_extraction.html#text-feature-extraction) — kanoniczne odniesienia do API oraz uwagi na temat każdego pokrętła.
- [Salton, G. i Buckley, C. (1988). Podejścia oparte na ważeniu terminów w automatycznym wyszukiwaniu tekstu](https://www.sciencedirect.com/science/article/pii/0306457388900210) — artykuł, dzięki któremu TF-IDF stał się domyślnym rozwiązaniem na dekadę.
– [„Dlaczego TF-IDF wciąż pokonuje osadzanie” — Ashfaque Thonikkadavan (średni)](https://medium.com/@cmtwskb/why-tf-idf-still-beats-embeddings-ad85c123e1b2) — 2026, kiedy wygrywa stara metoda i dlaczego.