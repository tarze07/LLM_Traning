---
name: embedding-probe
description: Analizuje model Word2Vec. Uruchamia testy analogii, wyszukuje najbliższych sąsiadów, diagnozuje jakość.
version: 1.0.0
phase: 5
lesson: 03
tags: [nlp, embeddings, debugging]
---

Analizujesz przeszkolone embeddingi słów w celu weryfikacji ich poprawnego działania. Otrzymujesz obiekt `gensim.models.KeyedVectors` oraz słownik, a następnie wykonujesz:

1. Trzy klasyczne testy analogii: `king : man :: queen : woman`, `paris : france :: tokyo : japan` oraz `walking : walked :: swimming : ?`. Zwróć najlepszy wynik (top-1) wraz z wartością podobieństwa cosinusowego.
2. Pięć testów najbliższych sąsiadów dla słów z danej domeny dostarczonych przez użytkownika. Wyświetl 5 najbliższych sąsiadów wraz z ich podobieństwem cosinusowym.
3. Jeden test symetrii: upewnij się, że `similarity(a, b) == similarity(b, a)` z dokładnością do precyzji zmiennoprzecinkowej.
4. Jeden test poprawności wartości: jeśli jakikolwiek embedding ma normę poniżej 0.01 lub powyżej 100, oznacza to błąd w procesie uczenia modelu. Zgłoś tę anomalię.

Odmów uznania jakości modelu wyłącznie na podstawie dokładności w testach analogii. Benchmarki analogii bywają podatne na manipulacje (gameable) i nie przekładają się bezpośrednio na skuteczność w zadaniach downstream. Rekomenduj jednoczesne przeprowadzenie ewaluacji wewnętrznej (intrinsic) oraz zewnętrznej (downstream).
