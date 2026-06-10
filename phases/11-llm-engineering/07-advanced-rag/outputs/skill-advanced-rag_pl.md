---

name: skill-advanced-rag
description: Twórz RAG klasy produkcyjnej dzięki hybrydowemu wyszukiwaniu, rerankingowi i ocenie
version: 1.0.0
phase: 11
lesson: 7
tags: [rag, hybrid-search, bm25, reranking, hyde, evaluation]

---

# Zaawansowany wzór RAG

Podstawowy RAG: osadzanie zapytania -> wyszukiwanie wektorów -> top-k -> generuj.
Zaawansowane RAG: osadzanie zapytania + BM25 -> rangi bezpieczników -> zmiana rangi -> top-k -> generowanie.

```
query -> [vector search (top-50)] -+-> RRF fusion -> reranker (top-5) -> prompt -> LLM
                                   |
query -> [BM25 search (top-50)]  --+
```

## Kiedy dokonać aktualizacji z podstawowego RAG

- Jakość pobierania spada poniżej 70% Recall@5
- Użytkownicy zgłaszają błędne lub nieistotne odpowiedzi
- Corpus rozrasta się do ponad 100 000 kawałków
- Zapytania używają innego słownictwa niż dokumenty
- Pytania typu multi-hop konsekwentnie zawodzą

## Lista kontrolna wdrożenia

1. Dodaj indeks BM25 obok indeksu wektorowego
2. Przeprowadź oba wyszukiwania równolegle (po 50 najlepszych)
3. Połącz z wzajemną fuzją rang (k=60)
4. Zmień klasyfikację najlepszych kandydatów za pomocą cross-enkodera
5. Jako ostatnie pytanie wybierz 5 najlepszych
6. Dodaj ocenę wierności na zestawie testowym

## Przewodnik po wyborze techniki

- **Wyszukiwanie hybrydowe**: zawsze używaj w produkcji. Nie kosztuje nic więcej w momencie zapytania.
- **Reranking**: użyj, gdy Recall@50 jest dobry, ale Recall@5 jest zły. Dodaje opóźnienie 50-200 ms.
- **HyDE**: używaj, gdy zapytania są niejasne lub używają innego słownictwa niż dokumenty. Dodaje jedno połączenie LLM.
- **Części nadrzędne-podrzędne**: użyj, gdy małe fragmenty nie mają kontekstu, ale duże fragmenty osłabiają znaczenie.
- **Filtrowanie metadanych**: użyj, gdy korpus ma jasne kategorie (data, typ źródła, dział).
- **Dekompozycja zapytań**: użyj w przypadku pytań z wieloma przeskokami, które wymagają informacji z wielu dokumentów.

## Typowe błędy

- Uruchamianie BM25 i wyszukiwania wektorowego z różnymi zestawami fragmentów (muszą przeszukiwać ten sam korpus)
- Użycie zbyt małej puli kandydatów do zmiany rankingu (10 najlepszych to za mało; użyj 50 najlepszych)
- Dodanie HyDE do każdego zapytania (pomaga tylko wtedy, gdy niedopasowanie słownictwa jest wąskim gardłem)
- Brak oceny zmian (zmierz Recall@k przed i po każdej technice)
- Nadmierna inżynieria rurociągu przed pomiarem w miejscu, w którym zawodzi

## Przebieg oceny

1. Utwórz ponad 50 pytań testowych ze znanymi fragmentami odpowiedzi
2. Zmierz Recall@5 i Recall@10 dla każdej metody wyszukiwania
3. W przypadku zapytań, w przypadku których wyszukiwanie zakończyło się sukcesem, zmierz wierność wygenerowanych odpowiedzi
4. Śledź wskaźniki co tydzień w miarę wzrostu korpusu
5. Zbadaj poszczególne awarie przed dodaniem kolejnych technik