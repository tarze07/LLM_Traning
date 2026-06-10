---
name: chunker
description: Wybierz strategię podziału tekstu na fragmenty, rozmiar bloku oraz margines zakładki (overlap) dla podanego korpusu i rozkładu zapytań.
version: 1.0.0
phase: 5
lesson: 23
tags: [nlp, rag, chunking]
---

Na podstawie charakterystyki korpusu (rodzaje dokumentów, średnia długość, dziedzina) oraz rozkładu zapytań (pytania o fakty / wnioskowanie / multi-hop) wygeneruj:

1. Strategia: Rekursywny, zdaniowy, semantyczny, rodzic-dziecko, late chunking lub wyszukiwanie kontekstowe (Contextual Retrieval) wraz z uzasadnieniem.
2. Rozmiar fragmentu: Liczba tokenów wraz z uzasadnieniem powiązanym z typem zapytań.
3. Margines zakładki (overlap): Domyślnie 0; podaj uzasadnienie w przypadku wyboru wartości wyższej niż 0.
4. Warunki skrajne (min/max): Wdrożenie zabezpieczeń `min_tokens` oraz `max_tokens`.
5. Plan ewaluacji: Wskaźnik Recall@5 na warstwowym zbiorze testowym składającym się z 50 zapytań (pytania o fakty, wnioskowanie, multi-hop).

Nigdy nie akceptuj strategii podziału tekstu bez zaimplementowanej weryfikacji wartości skrajnych (min/max). Zawsze odrzucaj propozycje stosowania zakładek powyżej 20% bez wyników testów (ablation study) wykazujących ich skuteczność. Oznaczaj rekomendacje podziału semantycznego, które nie posiadają zdefiniowanego dolnego limitu tokenów (min-token floor).
