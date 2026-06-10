---

name: transformer-review
description: Przejrzyj wdrożenie transformatora od podstaw w oparciu o 13 lekcji z fazy 7.
version: 1.0.0
phase: 7
lesson: 14
tags: [transformers, review, capstone]

---

Biorąc pod uwagę bazę kodu transformatora od podstaw (PyTorch/JAX), przejrzyj ustawienia domyślne z 2026 r. i oznacz brakujące lub nieprawidłowe elementy:

1. Uwaga. Obecna maska ​​przyczynowa. Skala według `sqrt(d_head)`. Podział na wiele głowic działa. Funkcja Flash Uwaga jest używana, jeśli jest dostępna. GQA wymienione, jeśli d_model ≥ 1024.
2. Kodowanie pozycyjne. RoPE (preferowany 2026) lub wyuczony absolut (dopuszczalny dla małych modeli). Oznacz sinusoidę jako historyczną.
3. Zablokuj okablowanie. Przednormą (nie postnormą). RMSNorm (nie LayerNorm). SwiGLU FFN (nie ReLU/GELU). Pozostałości wokół każdej podwarstwy. W warstwach liniowych usunięto odchylenia (nowoczesne ustawienie domyślne).
4. Szkolenie. AdamW (lub Muon na rok 2026+), harmonogram cosinus LR z liniowym rozgrzewaniem, obcinanie gradientu na poziomie 1.0, automatyczne rzucanie bf16. Powiązanie wagi pomiędzy osadzeniem tokenu a lm_head.
5. Strata. Przesunięcie entropii krzyżowej o jeden w każdej pozycji. Zamaskuj dopełnienie, jeśli występuje. Rejestruj straty pociągu i wartości w ustalonych odstępach czasu.

Odmów podpisania bazy kodu za pomocą któregokolwiek z: post-norma bez wyraźnego powodu, LayerNorm w kodzie produkcyjnym 2026 bez uzasadnienia, brakująca maska ​​przyczynowa w samouważności dekodera, niewiązane osadzania w małym LM. Flaga: brak podziału sprawdzającego, brak obcinania gradientu, LR > 1e-3 bez rozgrzewki lub block_size przekraczający zakres osadzania pozycyjnego bez powrotu. Zalecamy uruchomienie `python code/main.py` od końca do końca i sprawdzenie końcowej utraty wartości poniżej 2,5 na tinyshakespeare w konfiguracji nano.