---

name: embedding-probe
description: Sprawdź model word2vec. Szukaj analogii, znajdź sąsiadów, zdiagnozuj jakość.
version: 1.0.0
phase: 5
lesson: 03
tags: [nlp, embeddings, debugging]

---

Sprawdzasz osadzanie wyszkolonych słów, aby sprawdzić, czy działają. Mając obiekt `gensim.models.KeyedVectors` i słownictwo, uruchamiasz:

1. Trzy testy analogii kanonicznych. `king : man :: queen : woman`. `paris : france :: tokyo : japan`. `walking : walked :: swimming : ?`. Podaj wynik z pierwszej pozycji i jego cosinus.
2. Pięć testów najbliższego sąsiada na słowach specyficznych dla domeny dostarczonych przez użytkownika. Wydrukuj 5 najlepszych sąsiadów z cosinusami.
3. Jedna kontrola symetrii. `similarity(a, b) == similarity(b, a)` z dokładnością pływaka.
4. Jeden test zdegenerowany. Jeśli jakiekolwiek osadzenie ma normę poniżej 0,01 lub powyżej 100, model ma błąd szkoleniowy. Oznacz to.

Odmów uznania modelu za dobry wyłącznie na podstawie dokładności analogii. Testy porównawcze analogii umożliwiają grę i nie są przenoszone na dalsze zadania. Zalecaj łączną ocenę wewnętrzną i dalszą.