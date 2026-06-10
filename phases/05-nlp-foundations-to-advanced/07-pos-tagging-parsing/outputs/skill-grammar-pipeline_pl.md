---

name: grammar-pipeline
description: Zaprojektuj klasyczny potok zależności POS + dla dalszego zadania NLP.
version: 1.0.0
phase: 5
lesson: 07
tags: [nlp, pos, parsing]

---

Biorąc pod uwagę dalsze zadanie (wydobywanie informacji, sprawdzanie poprawności przepisania, rozkład zapytań, lematyzacja), wyprowadzasz:

1. Zestaw tagów. Penn Treebank dla starszych potoków tylko w języku angielskim, uniwersalne zależności dla wersji wielojęzycznych i międzyjęzykowych.
2. Biblioteka. spaCy dla większości produkcji (`en_core_web_sm` / `_lg` / `_trf`), zwrotka dla wielojęzycznego poziomu akademickiego, trankit dla najwyższej dokładności UD.
3. Fragment integracji. 3-5 linii wywołujących bibliotekę i zużywających `.pos_`, `.dep_`, `.head`.
4. Tryb awaryjny do przetestowania. Niejednoznaczność rzeczownik-czasownik (`saw`, `book`, `can`) i niejednoznaczność dołączenia PP to klasyczne pułapki. Próbka 20 wyników i gałka oczna.

Odmów polecania tworzenia własnego parsera. Budowanie parserów od podstaw to projekt badawczy, a nie zadanie aplikacyjne. Oznacz dowolny potok, który wykorzystuje tagi POS bez obsługi wariantów małych i wielkich liter, jako niestabilny.