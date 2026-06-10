---

name: skill-advanced-rag
description: Twórz systemy RAG klasy produkcyjnej z użyciem wyszukiwania hybrydowego, rerankingu i ewaluacji.
version: 1.0.0
phase: 11
lesson: 7
tags: [rag, hybrid-search, bm25, reranking, hyde, evaluation]

---

# Zaawansowany potok RAG

Podstawowy RAG: embedding zapytania -> wyszukiwanie wektorowe -> Top-K -> generowanie.
Zaawansowany RAG: embedding zapytania + wyszukiwanie BM25 -> fuzja rang (RRF) -> reranking -> Top-K -> generowanie.

```
query -> [vector search (top-50)] -+-> RRF fusion -> reranker (top-5) -> prompt -> LLM
                                   |
query -> [BM25 search (top-50)]  --+
```

## Kiedy przejść na zaawansowany RAG

- Jakość wyszukiwania (retrieval) spada poniżej 70% Recall@5.
- Użytkownicy zgłaszają nieprecyzyjne lub nieistotne odpowiedzi.
- Korpus dokumentów rozrasta się do ponad 100 000 segmentów (chunks).
- Zapytania użytkowników posługują się inną terminologią niż dokumenty źródłowe.
- Zapytania wieloetapowe (multi-hop) systematycznie kończą się niepowodzeniem.

## Lista kontrolna wdrożenia

1. Dodaj indeks BM25 działający równolegle obok bazy wektorowej.
2. Wykonuj oba wyszukiwania równolegle (pobierając po top 50 wyników z każdego).
3. Połącz wyniki za pomocą algorytmu Reciprocal Rank Fusion (RRF, domyślnie k=60).
4. Przeprowadź reranking najlepszych kandydatów przy użyciu modelu Cross-Encoder.
5. Przekaż top 5 ostatecznych wyników jako kontekst do promptu.
6. Zaimplementuj automatyczną ewaluację wierności (faithfulness) na zbiorze testowym.

## Przewodnik po wyborze technik optymalizacji

- **Wyszukiwanie hybrydowe**: Stosuj zawsze w systemach produkcyjnych. Nie generuje dodatkowych narzutów w czasie obsługi zapytania.
- **Reranking**: Wdróż, gdy wartość Recall@50 jest wysoka, ale Recall@5 jest niska. Dodaje od 50 do 200 ms opóźnienia (latency).
- **HyDE**: Stosuj, gdy zapytania użytkowników są nieprecyzyjne lub używają synonimów nieobecnych w dokumentach. Wymaga jednego dodatkowego wywołania LLM.
- **Segmentacja Parent-Child**: Stosuj, gdy małe segmenty tracą kontekst, a duże segmenty rozmywają precyzję wektora semantycznego.
- **Filtrowanie metadanych**: Stosuj, gdy dokumenty posiadają wyraźne kategorie (data publikacji, typ źródła, uprawnienia, dział).
- **Dekompozycja zapytania (Query Decomposition)**: Stosuj dla pytań wieloetapowych (multi-hop), wymagających syntezy wiedzy z wielu różnych dokumentów.

## Typowe błędy

- Uruchamianie BM25 i wyszukiwania wektorowego na różnych bazach segmentów (oba algorytmy muszą przeszukiwać dokładnie ten sam korpus).
- Przekazywanie zbyt małej puli kandydatów do rerankera (top 10 to za mało; przekazuj co najmniej top 50).
- Dodawanie techniki HyDE do każdego zapytania bez wyjątku (powinna być stosowana tylko przy rozbieżnościach słownikowych).
- Brak pomiaru efektów (zawsze mierz metrykę Recall@K przed i po wdrożeniu nowej techniki).
- Nadmierne skomplikowanie architektury potoku przed zlokalizowaniem i zmierzeniem konkretnego wąskiego gardła.

## Procedura ewaluacji

1. Przygotuj zbiór testowy zawierający ponad 50 pytań wraz ze wskazanymi właściwymi segmentami odpowiedzi.
2. Zmierz wskaźniki Recall@5 oraz Recall@10 dla każdej z testowanych metod wyszukiwania.
3. Dla zapytań, które poprawnie pobrały kontekst, zmierz wierność (faithfulness) wygenerowanych odpowiedzi LLM.
4. Monitoruj te wskaźniki cyklicznie wraz ze wzrostem bazy dokumentów.
5. Dokładnie analizuj pojedyncze przypadki awarii (błędnych odpowiedzi) przed wdrożeniem kolejnych technik optymalizacji.
