---
name: embedding-picker
description: Wybierz model osadzeń, wymiarowość wektorów oraz tryb wyszukiwania dla podanego korpusu i architektury wdrożenia.
version: 1.0.0
phase: 5
lesson: 22
tags: [nlp, embeddings, retrieval]
---

Na podstawie parametrów korpusu (rozmiar, języki, dziedzina, średnia długość), środowiska uruchomieniowego (chmura / urządzenia brzegowe / on-premise), limitów opóźnień oraz budżetu dyskowego wygeneruj:

1. Model: Dokładna nazwa punktu kontrolnego (checkpoint) lub usługa API wraz z jednozdaniowym uzasadnieniem.
2. Wymiarowość: Pełna / skrócona (Matryoshka) / skwantyzowana do int8 wraz z uzasadnieniem budżetowym.
3. Tryb wyszukiwania: Gęsty / rzadki / wielowektorowy / hybrydowy wraz z uzasadnieniem.
4. Prefiks zapytania (Query prefix) lub szablon promptu (jeśli jest wymagany przez specyfikację modelu).
5. Plan ewaluacji: Lista powiązanych zadań z benchmarku MTEB oraz testy na własnym, wydzielonym zbiorze z wykorzystaniem metryki nDCG@10.

Nigdy nie rekomenduj skracania wektorów Matrioszki do mniej niż 64 wymiarów bez przeprowadzenia dokładnej walidacji dziedzinowej. Zawsze odrzucaj propozycję stosowania modeli ColBERTv2 dla korpusów mniejszych niż 10 000 fragmentów (narzut infrastrukturalny przewyższa korzyści). Oznaczaj korpusy o długich tekstach (>8k tokenów) przekazywane do modeli o małym oknie kontekstowym (np. 512 tokenów).
