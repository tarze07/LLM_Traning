---

name: retrieval-picker
description: Wybierz stos pobierania dla danego korpusu i wzorca zapytania.
version: 1.0.0
phase: 5
lesson: 14
tags: [nlp, retrieval, rag, search]

---

Biorąc pod uwagę wymagania (rozmiar korpusu, wzorzec zapytania, budżet opóźnień, pasek jakości, ograniczenia infrastruktury), wynik:

1. Stos. Tylko BM25, tylko gęsty, hybrydowy (BM25 + gęsty + RRF), hybrydowy + zmiana rangi cross-enkodera lub trójdrożny (BM25 + gęsty + wyuczony-rzadki).
2. Gęsty koder. Nazwij konkretny model (`all-MiniLM-L6-v2`, `bge-large-en-v1.5`, `e5-large-v2`, `paraphrase-multilingual-MiniLM-L12-v2`). Dopasuj do języka, domeny i długości kontekstu.
3. Zmiana rankingu. Nazwij model cross-enkodera, jeśli jest używany (`cross-encoder/ms-marco-MiniLM-L-6-v2`, `BAAI/bge-reranker-large`). Flaga ~30-100 ms dodała opóźnienie w pierwszej 30.
4. Plan ewaluacji. Recall@10 to podstawowa metryka aportera. MRR dla wielu odpowiedzi. Najpierw poziom bazowy, a następnie mierzona w oparciu o niego stopniowa poprawa.

Odmawiaj rekomendowania opcji „tylko gęste” w przypadku korpusów z nazwanymi jednostkami, kodami błędów lub kodami SKU produktów, chyba że użytkownik ma dowody, że gęste obsługuje dokładne dopasowania. Odmów pominięcia ponownego rankingu w celu uzyskania informacji o wysokiej stawce (prawnej, medycznej), gdzie ostateczna piątka decyduje o odpowiedzi użytkownika.