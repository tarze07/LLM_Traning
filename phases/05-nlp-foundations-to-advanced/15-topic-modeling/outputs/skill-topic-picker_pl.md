---

name: topic-picker
description: Wybierz LDA lub BERTopic dla korpusu. Określ bibliotekę, pokrętła, ocenę.
version: 1.0.0
phase: 5
lesson: 15
tags: [nlp, topic-modeling]

---

Biorąc pod uwagę opis korpusu (liczba dokumentów, średnia długość, domena, język, budżet obliczeniowy), wynik:

1. Algorytm. LDA / NMF / BERTopic / Top2Vec / FASTopic. Powód w jednym zdaniu.
2. Konfiguracja. Liczba tematów (zaczynaj od ~sqrt(n_docs)), filtry `min_df` / `max_df`, model osadzania dla podejść neuronowych.
3. Ocena. Spójność tematu (c_v) poprzez `gensim.models.CoherenceModel`, różnorodność tematów oraz 20-próbkowy odczyt człowieka.
4. Tryb awarii do sondowania. W przypadku LDA „śmieciowe tematy” pochłaniają słowa i częste terminy. Dla BERTopic, -1 klaster odstający połykający niejednoznaczne dokumenty.

Odrzuć BERTopic w przypadku dokumentów dłuższych niż okno kontekstowe modelu osadzania bez strategii fragmentowania. Odrzuć LDA w przypadku bardzo krótkiego tekstu (tweety, recenzje poniżej 10 tokenów), ponieważ załamuje się spójność. Oznacz dowolny wybór n_topics poniżej 5 lub powyżej 200 jako prawdopodobnie błędny w przypadku prawdziwych danych.