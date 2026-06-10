---

name: retrieval-picker
description: Wybierz architekturę (stos) wyszukiwania informacji dla danego korpusu dokumentów i wzorca zapytań.
version: 1.0.0
phase: 5
lesson: 14
tags: [nlp, retrieval, rag, search]

---

Na podstawie wymagań (rozmiar korpusu, wzorzec zapytań, limit opóźnień, kryteria jakości, ograniczenia infrastrukturalne) wygeneruj:

1. Architektura wyszukiwania (stos): wyłącznie BM25, wyłącznie wyszukiwanie gęste (dense), hybrydowe (BM25 + gęste + RRF), hybrydowe z rerankingiem (cross-encoder) lub trójścieżkowe (BM25 + gęste + wyuczone rzadkie/learned-sparse).
2. Gęsty enkoder: wskaż konkretny model (np. `all-MiniLM-L6-v2`, `bge-large-en-v1.5`, `e5-large-v2`, `paraphrase-multilingual-MiniLM-L12-v2`). Dopasuj go do języka, domeny i długości kontekstu.
3. Reranking (ponowne szeregowanie): wskaż konkretny model typu cross-encoder, jeśli jest używany (np. `cross-encoder/ms-marco-MiniLM-L-6-v2`, `BAAI/bge-reranker-large`). Oznacz, że dodanie rerankingu dla czołowych 30 wyników (top-30) wiąże się z narzutem opóźnienia rzędu ~30-100 ms.
4. Plan ewaluacji: Recall@10 jako podstawowa metryka modułu wyszukującego (retrievera), MRR dla zapytań z wieloma możliwymi odpowiedziami. Zdefiniuj najpierw linię bazową (baseline), a następnie mierz na jej podstawie stopniowe usprawnienia.

Odmawiaj rekomendowania podejścia „wyłącznie gęstego” (dense-only) w przypadku korpusów zawierających nazwy własne, kody błędów lub identyfikatory produktów (SKU), chyba że użytkownik przedstawi dowody, że model gęsty poprawnie obsługuje dokładne dopasowania (exact matches). Odmawiaj pominięcia etapu rerankingu w zastosowaniach o krytycznym znaczeniu (np. prawnych, medycznych), gdzie ostateczne top-5 wyników bezpośrednio determinuje odpowiedź udzielaną użytkownikowi.
