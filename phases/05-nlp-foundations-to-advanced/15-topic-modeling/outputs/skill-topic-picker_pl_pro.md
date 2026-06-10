---

name: topic-picker
description: Wybór algorytmu LDA lub BERTopic dla danego korpusu. Określenie biblioteki, parametrów konfiguracyjnych oraz metod oceny.
version: 1.0.0
phase: 5
lesson: 15
tags: [nlp, topic-modeling]

---

Na podstawie opisu korpusu (liczba dokumentów, średnia długość tekstu, domena, język, budżet obliczeniowy) określ:

1. **Algorytm**: LDA / NMF / BERTopic / Top2Vec / FASTopic. Uzasadnij wybór w jednym zdaniu.
2. **Konfiguracja**: Docelowa liczba tematów (rekomendowany punkt startowy to ok. `~sqrt(n_docs)`), filtry częstotliwości dokumentów `min_df` / `max_df` oraz model osadzeń (embeddings) dla podejść neuronowych.
3. **Ocena**: Spójność tematyczna (ang. *topic coherence*, np. miara $c_v$) wyznaczana za pomocą `gensim.models.CoherenceModel`, różnorodność tematów (ang. *topic diversity*) oraz weryfikacja ekspercka (manualna analiza próby 20 dokumentów).
4. **Potencjalne problemy (tryby awarii)**: W przypadku LDA – powstawanie tematów-„śmietników” (ang. *garbage topics*) gromadzących powtarzające się słowa i częste terminy. W przypadku BERTopic – klaster oznaczony jako -1 (szum/odstający), absorbujący zbyt wiele niejednoznacznych dokumentów.

Odrzuć BERTopic dla dokumentów przekraczających okno kontekstowe modelu osadzeń, jeśli nie zastosowano strategii dzielenia tekstu na fragmenty (ang. *chunking*). Odrzuć LDA w przypadku bardzo krótkich tekstów (np. tweety, recenzje poniżej 10 tokenów), ponieważ w ich przypadku spójność tematów ulega załamaniu. Oznacz wybór liczby tematów (`n_topics`) poniżej 5 lub powyżej 200 jako prawdopodobny błąd w przypadku rzeczywistych danych.
