# Modelowanie tematyczne — LDA i BERTopic

> LDA: dokumenty są mieszaniną tematów, tematy są rozkładem słów. BERTopic: klastry dokumentów w przestrzeni osadzania, klastry to tematy. Ten sam cel, różne rozkłady.

**Typ:** Ucz się
**Języki:** Python
**Wymagania wstępne:** Faza 5 · 02 (BoW + TF-IDF), Faza 5 · 03 (Word2Vec)
**Czas:** ~45 minut

## Problem

Masz 10 000 zgłoszeń do obsługi klienta, 50 000 artykułów prasowych lub 200 000 tweetów. Trzeba wiedzieć, o czym jest zbiór, nie czytając go. Nie masz oznaczonych kategorii. Nawet nie wiesz, ile istnieje kategorii.

Modelowanie tematyczne odpowiada na to pytanie bez nadzoru. Daj mu korpus, uzyskaj mały zestaw spójnych tematów i, dla każdego dokumentu, rozkład tych tematów.

Dominują dwie rodziny algorytmiczne. LDA (2003) traktuje każdy dokument jako mieszaninę ukrytych tematów, a każdy temat jako rozkład słów. Wnioskowanie jest Bayesowskie. Nadal jest dostępny w wersji produkcyjnej, gdzie potrzebne są zadania tematyczne o mieszanym członkostwie i zrozumiałe rozkłady prawdopodobieństwa na poziomie słów.

BERTopic (2020) koduje dokumenty za pomocą BERT, redukuje wymiarowość za pomocą UMAP, grupuje za pomocą HDBSCAN i wyodrębnia słowa tematyczne za pomocą opartego na klasach TF-IDF. Wygrywa w przypadku krótkich tekstów, mediów społecznościowych i wszystkiego, gdzie podobieństwo semantyczne jest ważniejsze niż nakładanie się słów. Jeden dokument ma jeden temat, co jest ograniczeniem w przypadku długich treści.

Ta lekcja buduje intuicję dla obu i wskazuje, który z nich wybrać dla danego korpusu.

## Koncepcja

![Model mieszaniny LDA a grupowanie BERTopic](../assets/topic-modeling.svg)

**Historia generatywna LDA.** Każdy temat jest rozkładem słów. Każdy dokument jest mieszanką tematów. Aby wygenerować słowo w dokumencie, wypróbuj temat z mieszaniny dokumentu, a następnie spróbuj słowa z rozkładu tego tematu. Wnioskowanie odwraca tę sytuację: biorąc pod uwagę zaobserwowane słowa, wywnioskowaj rozkład tematów na dokument i rozkład słów na temat. Zwinięte próbkowanie Gibbsa lub wariacyjne Bayesa załatwiają sprawę.

Kluczowe wyjście LDA:

- `doc_topic`: macierz `(n_docs, n_topics)`, każdy wiersz sumuje się do 1 (mieszanka tematów dokumentu).
- `topic_word`: macierz `(n_topics, vocab_size)`, każdy wiersz sumuje się do 1 (rozkład słów tematu).

**Próbka BERTopic.**

1. Zakoduj każdy dokument za pomocą transformatora zdań (np. `all-MiniLM-L6-v2`). 384-ciemne wektory.
2. Zmniejsz wymiarowość za pomocą UMAP do ~5 wymiarów. Osadzenia BERT są zbyt ciemne, aby można było je grupować.
3. Klaster z HDBSCAN. Na podstawie gęstości tworzy klastry o zmiennej wielkości i etykietę „odstającą”.
4. Dla każdego klastra oblicz TF-IDF oparty na klasach na podstawie dokumentów klastra, aby wyodrębnić najważniejsze słowa.

Wynikiem jest jeden temat na dokument (plus etykieta wartości odstającej -1). Opcjonalnie miękkie członkostwo poprzez wektor prawdopodobieństwa HDBSCAN.

## Zbuduj to

### Krok 1: LDA poprzez scikit-learn

```python
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import numpy as np

def fit_lda(documents, n_topics=5, max_features=1000):
    cv = CountVectorizer(
        max_features=max_features,
        stop_words="english",
        min_df=2,
        max_df=0.9,
    )
    X = cv.fit_transform(documents)
    lda = LatentDirichletAllocation(
        n_components=n_topics,
        random_state=42,
        max_iter=50,
        learning_method="online",
    )
    doc_topic = lda.fit_transform(X)
    feature_names = cv.get_feature_names_out()
    return lda, cv, doc_topic, feature_names

def print_top_words(lda, feature_names, n_top=10):
    for idx, topic in enumerate(lda.components_):
        top_idx = np.argsort(-topic)[:n_top]
        words = [feature_names[i] for i in top_idx]
        print(f"topic {idx}: {' '.join(words)}")
```

Uwaga: usunięto stopwords, filtry min_df i max_df rzadkie i wszechobecne terminy, CountVectorizer (nie TfidfVectorizer), ponieważ LDA oczekuje surowych zliczeń.

### Krok 2: BERTopic (produkcja)

```python
from bertopic import BERTopic

topic_model = BERTopic(
    embedding_model="sentence-transformers/all-MiniLM-L6-v2",
    min_topic_size=15,
    verbose=True,
)

topics, probs = topic_model.fit_transform(documents)
info = topic_model.get_topic_info()
print(info.head(20))
valid_topics = info[info["Topic"] != -1]["Topic"].tolist()
for topic_id in valid_topics[:5]:
    print(f"topic {topic_id}: {topic_model.get_topic(topic_id)[:10]}")
```

Filtr na `Topic != -1` usuwa zbiór wartości odstających BERTopic (dokumenty HDBSCAN nie mogły być klastrowane). `min_topic_size` kontroluje minimalny rozmiar klastra HDBSCAN; Domyślna wartość biblioteki BERTopic to 10. W tym przykładzie jawnie ustawia się ją na 15 dla skali lekcji. W przypadku korpusów zawierających ponad 10 000 dokumentów liczbę należy zwiększyć do 50 lub 100.

### Krok 3: ocena

Obie metody wyprowadzają słowa tematu. Pytanie, czy te słowa są ze sobą spójne.

- **Spójność tematyczna (c_v).** Łączy NPMI (znormalizowane punktowe wzajemne informacje) par górnych słów w kontekstach przesuwanego okna, agreguje wyniki w wektory tematyczne i porównuje te wektory poprzez podobieństwo cosinus. Wyżej jest lepiej. Użyj `gensim.models.CoherenceModel` z `coherence="c_v"`.
- **Różnorodność tematów.** Część unikalnych słów spośród najpopularniejszych słów ze wszystkich tematów. Wyżej znaczy lepiej (tematy nie nakładają się na siebie).
- **Kontrola jakościowa.** Przeczytaj najważniejsze słowa w każdym temacie. Czy podają nazwę prawdziwej rzeczy? Ludzki osąd jest nadal ostatnią linią obrony.

## Kiedy wybrać który

| Sytuacja | Wybierz |
|----------|------|
| Krótki tekst (tweety, recenzje, nagłówki) | BERTopic |
| Długie dokumenty z mieszaninami tematów | LDA |
| Brak procesora graficznego / ograniczone obliczenia | LDA lub NMF |
| Potrzebujesz dystrybucji wielotematycznej na poziomie dokumentu | LDA |
| Integracja LLM w celu etykietowania tematów | BERTopic (bezpośrednie wsparcie) |
| Wdrożenie brzegowe z ograniczonymi zasobami | LDA |
| Maksymalna spójność semantyczna | BERTopic |

Najważniejszym czynnikiem praktycznym jest długość dokumentu. Osadzenia BERT są obcięte; LDA liczy pracę na dowolnej długości. W przypadku dokumentów dłuższych niż kontekst modelu osadzania użyj fragmentu + agregacji lub użyj LDA.

## Użyj tego

Stos na rok 2026:

- **BERTopic.** Domyślny dla krótkiego tekstu i wszystkiego, gdzie liczy się semantyka.
- **`gensim.models.LdaModel`.** Klasyczny LDA do zastosowań produkcyjnych, dojrzały, przetestowany w boju.
- **`sklearn.decomposition.LatentDirichletAllocation`.** Łatwe LDA do eksperymentów.
- **NMF.** Nieujemna faktoryzacja macierzy. Szybka alternatywa dla LDA, porównywalna jakość przy krótkim tekście.
- **Top2Vec.** Podobny projekt do BERTopic. Mniejsza społeczność, ale dobra w niektórych benchmarkach.
- **FASTopic.** Nowszy, szybszy niż BERTopic w przypadku bardzo dużych korpusów.
- **Etykietowanie oparte na LLM.** Uruchom dowolne grupowanie, a następnie poproś model o nadanie nazwy każdemu klasterowi.

## Wyślij to

Zapisz jako `outputs/skill-topic-picker.md`:

```markdown
---
name: topic-picker
description: Wybierz LDA lub BERTopic dla korpusu. Określ bibliotekę, pokrętła, ocenę.
version: 1.0.0
phase: 5
lesson: 15
tags: [nlp, topic-modeling]
---

Biorąc pod uwagę opis korpusu (liczba dokumentów, średnia długość, domena, język, budżet obliczeniowy), wynik:

1. Algorytm. LDA / NMF / BERTopic / Top2Vec / FASTopic. Uzasadnienie w jednym zdaniu.
2. Konfiguracja. Liczba tematów: `recommended = max(5, round(sqrt(n_docs)))`, ograniczona do 200 dla korpusów poniżej 40 000 dokumentów; pozwól na >200 tylko wtedy, gdy korpus jest rzeczywiście duży (>40k) i zanotuj zwiększony koszt obliczeniowy. Filtry `min_df` / `max_df` i model osadzania dla podejść neuronowych również tu pasują.
3. Ocena. Spójność tematyczna (c_v) za pomocą `gensim.models.CoherenceModel`, różnorodność tematów oraz ręczne sprawdzenie 20 próbek.
4. Tryb awarii do sprawdzenia. W przypadku LDA „śmieciowe tematy” pochłaniające słowa stop i częste pojęcia. Dla BERTopic klaster odstający -1 pochłaniający niejednoznaczne dokumenty.

Odmów użycia BERTopic dla dokumentów dłuższych niż okno kontekstu modelu osadzania bez strategii porcjowania. Odmów użycia LDA dla bardzo krótkiego tekstu (tweety, recenzje poniżej 10 tokenów), ponieważ spójność załamuje się. Oznacz każdy wybór n_topics poniżej 5 jako prawdopodobnie błędny; oznacz >200 dla korpusów poniżej 40k dokumentów jako prawdopodobne nadmierne podziały.
```

## Ćwiczenia

1. **Łatwe.** Dopasuj LDA do 5 tematów w zestawie danych 20 grup dyskusyjnych. Wydrukuj 10 najważniejszych słów na każdy temat. Oznacz każdy temat ręcznie. Czy algorytm znalazł prawdziwe kategorie?
2. **Średni.** Dopasuj BERTopic do tego samego podzbioru 20 grup dyskusyjnych. Porównaj liczbę znalezionych tematów, najczęstsze słowa i spójność jakościową z LDA. Które kategorie są bardziej przejrzyste?
3. **Trudne.** Oblicz spójność c_v zarówno dla LDA, jak i BERTopic w swoim korpusie. Uruchom każdy z 5, 10, 20, 50 tematami. Spójność fabuły a liczba tematów. Zgłoś, która metoda jest bardziej stabilna w zależności od liczby tematów.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Temat | Rzecz, o której opowiada korpus | Rozkład prawdopodobieństwa według słów (LDA) lub grupa podobnych dokumentów (BERTopic). |
| Członkostwo mieszane | Dokument zawiera wiele tematów | LDA przypisuje każdemu dokumentowi podział na wszystkie tematy. |
| UMAP | Redukcja wymiarowości | Różnorodne uczenie się, które zachowuje lokalną strukturę; używany w BERTopic. |
| HDBSCAN | Klastrowanie gęstości | Znajduje klastry o zmiennej wielkości; generuje etykietę „szum” (-1) dla wartości odstających. |
| spójność c_v | Wskaźnik jakości tematu | Średnie punktowe wzajemne informacje dotyczące najważniejszych słów tematycznych w przesuwanych oknach. |

## Dalsze czytanie

- [Blei, Ng, Jordania (2003). Latent Dirichlet Allocation] (https://www.jmlr.org/papers/volume3/blei03a/blei03a.pdf) — artykuł LDA.
- [Grootendorst (2022). BERTopic: Neuronowe modelowanie tematów za pomocą procedury TF-IDF opartej na klasach](https://arxiv.org/abs/2203.05794) — artykuł BERTopic.
- [Röder, Obydwa, Hinneburg (2015). Exploring the Space of Topic Coherence Measures](https://svn.aksw.org/papers/2015/WSDM_Topic_Evaluation/public.pdf) — artykuł przedstawiający c_v i przyjaciół.
- [Dokumentacja BERTopic](https://maartegr.github.io/BERTopic/) — odniesienie do produkcji. Doskonałe przykłady.