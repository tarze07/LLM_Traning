# Modelowanie tematyczne — LDA i BERTopic

> LDA: dokumenty są mieszaniną tematów, tematy są rozkładem słów. BERTopic: klastry dokumentów w przestrzeni osadzeń, klastry to tematy. Ten sam cel, różne podejścia.

**Typ:** Ucz się
**Języki:** Python
**Wymagania wstępne:** Faza 5 · 02 (BoW + TF-IDF), Faza 5 · 03 (Word2Vec)
**Czas:** ~45 minut

## Problem

Masz 10 000 zgłoszeń do obsługi klienta, 50 000 artykułów prasowych lub 200 000 tweetów. Chcesz wiedzieć, o czym jest zbiór, nie czytając go w całości. Nie dysponujesz oznaczonymi kategoriami. Nie wiesz nawet, ile kategorii istnieje.

Modelowanie tematyczne odpowiada na to pytanie bez nadzoru. Podajesz korpus, otrzymujesz zwarty zestaw spójnych tematów, a dla każdego dokumentu — rozkład tych tematów.

W tej dziedzinie dominują dwie rodziny algorytmiczne. LDA (2003) traktuje każdy dokument jako mieszaninę ukrytych tematów, a każdy temat jako rozkład słów. Wnioskowanie opiera się na podejściu bayesowskim. Algorytm nadal sprawdza się w środowiskach produkcyjnych, gdzie wymagane są tematy o mieszanym członkostwie i interpretowalne rozkłady prawdopodobieństwa na poziomie słów.

BERTopic (2020) koduje dokumenty za pomocą BERT, redukuje wymiarowość przy użyciu UMAP, grupuje je algorytmem HDBSCAN i wyodrębnia słowa tematyczne za pomocą TF-IDF opartego na klasach. Sprawdza się lepiej w przypadku krótkich tekstów, mediów społecznościowych i wszędzie tam, gdzie podobieństwo semantyczne jest ważniejsze niż pokrywanie się słów. Każdy dokument otrzymuje jeden temat — to ograniczenie przy długich treściach.

Niniejsza lekcja buduje intuicję dla obu metod i wskazuje, którą wybrać dla danego korpusu.

## Koncepcja

![Model mieszaniny LDA a grupowanie BERTopic](../assets/topic-modeling.svg)

**Historia generatywna LDA.** Każdy temat jest rozkładem słów, a każdy dokument — mieszaniną tematów. Aby wygenerować słowo w dokumencie, losuje się temat z mieszaniny dokumentu, a następnie słowo z rozkładu tego tematu. Wnioskowanie odwraca ten proces: mając dane zaobserwowane słowa, wyznaczamy rozkład tematów dla dokumentu i rozkład słów dla tematu. Służą do tego zwinięte próbkowanie Gibbsa lub wariacyjne podejście bayesowskie.

Kluczowe wyniki LDA:

- `doc_topic`: macierz `(n_docs, n_topics)`, każdy wiersz sumuje się do 1 (mieszanka tematów dokumentu).
- `topic_word`: macierz `(n_topics, vocab_size)`, każdy wiersz sumuje się do 1 (rozkład słów tematu).

**Potok BERTopic.**

1. Zakoduj każdy dokument za pomocą transformatora zdań (np. `all-MiniLM-L6-v2`). Wektory mają 384 wymiary.
2. Zmniejsz wymiarowość przy użyciu UMAP do ok. 5 wymiarów. Osadzenia BERT mają zbyt wiele wymiarów, by bezpośrednio je grupować.
3. Grupuj za pomocą HDBSCAN. Algorytm oparty na gęstości tworzy klastry o zmiennej wielkości i przypisuje etykietę „odstającą".
4. Dla każdego klastra oblicz TF-IDF oparty na klasach z dokumentów klastra, aby wyodrębnić najważniejsze słowa.

Wynikiem jest jeden temat na dokument (plus etykieta wartości odstającej -1). Opcjonalnie można uzyskać miękkie przypisanie przez wektor prawdopodobieństwa HDBSCAN.

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

Uwaga: usunięto stopwords, filtry `min_df` i `max_df` eliminują rzadkie i wszechobecne terminy. Używa się `CountVectorizer` (nie `TfidfVectorizer`), ponieważ LDA oczekuje surowych zliczeń.

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

Filtr `Topic != -1` usuwa zbiór wartości odstających BERTopic — dokumenty, których HDBSCAN nie zdołał przypisać do żadnego klastra. Parametr `min_topic_size` kontroluje minimalny rozmiar klastra; domyślna wartość w bibliotece BERTopic wynosi 10. W tym przykładzie ustawiono ją jawnie na 15, co odpowiada skali lekcji. Dla korpusów powyżej 10 000 dokumentów wartość tę należy zwiększyć do 50 lub 100.

### Krok 3: ocena

Obie metody zwracają słowa tematu. Kluczowe pytanie brzmi: czy te słowa są ze sobą spójne.

- **Spójność tematyczna (c_v).** Łączy NPMI (znormalizowaną wzajemną informację punktową) par czołowych słów w oknach przesuwnych, agreguje wyniki w wektory tematyczne i porównuje je za pomocą podobieństwa cosinusowego. Im wyższa wartość, tym lepiej. Używaj `gensim.models.CoherenceModel` z `coherence="c_v"`.
- **Różnorodność tematów.** Odsetek unikalnych słów spośród czołowych słów ze wszystkich tematów. Im wyższa wartość, tym mniejsze nakładanie się tematów.
- **Kontrola jakościowa.** Przejrzyj najważniejsze słowa każdego tematu. Czy opisują rzeczywistą kategorię? Ludzka ocena pozostaje ostatnią linią obrony.

## Kiedy wybrać który

| Sytuacja | Wybierz |
|----------|------|
| Krótki tekst (tweety, recenzje, nagłówki) | BERTopic |
| Długie dokumenty z mieszaniną tematów | LDA |
| Brak GPU / ograniczone zasoby obliczeniowe | LDA lub NMF |
| Potrzebny rozkład wielotematyczny na poziomie dokumentu | LDA |
| Integracja LLM do etykietowania tematów | BERTopic (wbudowane wsparcie) |
| Wdrożenie w środowisku brzegowym z ograniczonymi zasobami | LDA |
| Maksymalna spójność semantyczna | BERTopic |

Najważniejszym czynnikiem praktycznym jest długość dokumentu. Osadzenia BERT mają ograniczone okno kontekstu; LDA przetwarza tekst dowolnej długości. Dla dokumentów przekraczających okno kontekstu modelu osadzania stosuj podział na fragmenty z agregacją lub sięgnij po LDA.

## Użyj tego

Stos na rok 2026:

- **BERTopic.** Domyślny wybór dla krótkich tekstów i wszędzie tam, gdzie liczy się semantyka.
- **`gensim.models.LdaModel`.** Klasyczny LDA do zastosowań produkcyjnych — dojrzały i sprawdzony w praktyce.
- **`sklearn.decomposition.LatentDirichletAllocation`.** Uproszczony LDA do eksperymentów.
- **NMF.** Nieujemna faktoryzacja macierzy. Szybka alternatywa dla LDA, o porównywalnej jakości przy krótkim tekście.
- **Top2Vec.** Projekt podobny do BERTopic. Mniejsza społeczność, lecz dobry wynik w niektórych testach porównawczych.
- **FASTopic.** Nowszy i szybszy niż BERTopic przy bardzo dużych korpusach.
- **Etykietowanie oparte na LLM.** Uruchom dowolny algorytm grupowania, a następnie poproś model językowy o nadanie nazwy każdemu klastrowi.

## Wyślij to

Zapisz jako `outputs/skill-topic-picker.md`:

```markdown
---
name: topic-picker
description: Wybierz LDA lub BERTopic dla korpusu. Określ bibliotekę, parametry i sposób oceny.
version: 1.0.0
phase: 5
lesson: 15
tags: [nlp, topic-modeling]
---

Na podstawie opisu korpusu (liczba dokumentów, średnia długość, domena, język, budżet obliczeniowy) zwróć:

1. Algorytm. LDA / NMF / BERTopic / Top2Vec / FASTopic. Uzasadnienie w jednym zdaniu.
2. Konfiguracja. Liczba tematów: `recommended = max(5, round(sqrt(n_docs)))`, ograniczona do 200 dla korpusów poniżej 40 000 dokumentów; wartości powyżej 200 dopuszczalne tylko przy rzeczywiście dużych korpusach (>40k) — należy wtedy odnotować wyższy koszt obliczeniowy. Filtry `min_df` / `max_df` i model osadzania dla podejść neuronowych również tu należy podać.
3. Ocena. Spójność tematyczna (c_v) za pomocą `gensim.models.CoherenceModel`, różnorodność tematów oraz ręczne sprawdzenie 20 próbek.
4. Potencjalne problemy do weryfikacji. Przy LDA: „śmieciowe tematy" pochłaniające słowa stop i powszechne wyrazy. Przy BERTopic: klaster odstający -1 absorbujący niejednoznaczne dokumenty.

Nie stosuj BERTopic dla dokumentów dłuższych niż okno kontekstu modelu osadzania bez strategii podziału na fragmenty. Nie stosuj LDA dla bardzo krótkich tekstów (tweety, recenzje poniżej 10 tokenów), ponieważ spójność gwałtownie spada. Oznacz każdy wybór n_topics poniżej 5 jako prawdopodobnie błędny; oznacz wartości >200 dla korpusów poniżej 40k dokumentów jako nadmierne rozdrobnienie.
```

## Ćwiczenia

1. **Łatwe.** Dopasuj LDA do 5 tematów na zbiorze danych 20 grup dyskusyjnych. Wypisz 10 czołowych słów dla każdego tematu i ręcznie przypisz im etykiety. Czy algorytm odnalazł rzeczywiste kategorie?
2. **Średnie.** Dopasuj BERTopic do tego samego podzbioru danych. Porównaj liczbę znalezionych tematów, czołowe słowa i spójność jakościową z wynikami LDA. Które kategorie są bardziej czytelne?
3. **Trudne.** Oblicz spójność c_v dla LDA i BERTopic na swoim korpusie. Uruchom każdą metodę dla 5, 10, 20 i 50 tematów. Sporządź wykres spójności w zależności od liczby tematów. Oceń, która metoda jest bardziej stabilna przy zmianie tej liczby.

## Kluczowe terminy

| Termin | Co się przez to rozumie | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Temat | Rzecz, o której opowiada korpus | Rozkład prawdopodobieństwa nad słowami (LDA) lub skupisko podobnych dokumentów (BERTopic). |
| Członkostwo mieszane | Dokument należy do wielu tematów | LDA przypisuje każdemu dokumentowi udział we wszystkich tematach. |
| UMAP | Redukcja wymiarowości | Metoda uczenia różnorodności, zachowująca lokalną strukturę; stosowana w BERTopic. |
| HDBSCAN | Grupowanie oparte na gęstości | Wykrywa skupiska o zmiennej wielkości; dokumentom nienależącym do żadnego klastra przypisuje etykietę „szum" (-1). |
| spójność c_v | Miara jakości tematu | Średnia znormalizowana wzajemna informacja punktowa dla czołowych słów tematycznych w oknach przesuwnych. |

## Dalsze czytanie

- [Blei, Ng, Jordania (2003). Latent Dirichlet Allocation] (https://www.jmlr.org/papers/volume3/blei03a/blei03a.pdf) — artykuł źródłowy LDA.
- [Grootendorst (2022). BERTopic: Neuronowe modelowanie tematów za pomocą procedury TF-IDF opartej na klasach](https://arxiv.org/abs/2203.05794) — artykuł źródłowy BERTopic.
- [Röder, Both, Hinneburg (2015). Exploring the Space of Topic Coherence Measures](https://svn.aksw.org/papers/2015/WSDM_Topic_Evaluation/public.pdf) — artykuł przedstawiający miarę c_v i pokrewne.
- [Dokumentacja BERTopic](https://maartegr.github.io/BERTopic/) — kompletna dokumentacja produkcyjna z przykładami.
