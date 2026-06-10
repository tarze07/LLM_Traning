---

name: transformer-review
description: Przegląd implementacji transformera od podstaw w oparciu o 13 lekcji z fazy 7.
version: 1.0.0
phase: 7
lesson: 14
tags: [transformers, review, capstone]

---

Na podstawie kodu źródłowego transformera napisanego od podstaw (PyTorch/JAX), dokonaj przeglądu pod kątem domyślnych standardów z 2026 roku i wskaż brakujące lub niepoprawne elementy:

1. Mechanizm uwagi (Attention). Obecna maska przyczynowa (causal mask). Skalowanie przez `sqrt(d_head)`. Działający podział na wiele głowic (multi-head). Użycie FlashAttention, jeśli jest dostępne. Zastosowanie GQA (Grouped-Query Attention), jeśli d_model ≥ 1024.
2. Kodowanie pozycyjne. RoPE (preferowane w 2026 r.) lub wyuczone absolutne (dopuszczalne dla małych modeli). Oznaczenie kodowania sinusoidalnego jako historycznego (przestarzałego).
3. Architektura bloku. Pre-normalization (Pre-LN, a nie Post-LN). RMSNorm (a nie LayerNorm). SwiGLU FFN (a nie ReLU/GELU). Połączenia omijające (residual connections) wokół każdej podwarstwy. Brak wyrazów wolnych (bias) w warstwach liniowych (współczesny standard).
4. Trening. AdamW (lub Muon od roku 2026+), cosinusowy harmonogram zmian współczynnika uczenia (LR) z liniowym rozgrzewaniem (warmup), przycinanie gradientu (gradient clipping) na poziomie 1.0, automatyczne rzutowanie typów (autocast) do bf16. Powiązanie wag (weight tying) między embeddingiem tokenów a `lm_head`.
5. Funkcja straty (Loss). Obliczanie entropii krzyżowej (cross-entropy) z przesunięciem o jedną pozycję (offset). Maskowanie tokenów dopełnienia (padding), jeśli występują. Logowanie wartości straty na zbiorze treningowym i walidacyjnym w określonych odstępach czasu.

Odrzuć kod w przypadku wykrycia któregokolwiek z poniższych problemów: stosowanie Post-LN bez wyraźnego powodu, LayerNorm w kodzie produkcyjnym z 2026 r. bez uzasadnienia, brak maski przyczynowej w mechanizmie samouwagi (self-attention) dekodera, brak powiązania wag (untied embeddings) w małym modelu językowym (LM). Oznacz flagą ostrzegawczą: brak podziału na zbiór treningowy/walidacyjny, brak przycinania gradientu, LR > 1e-3 bez rozgrzewki (warmup) lub `block_size` przekraczający zakres embeddingów pozycyjnych bez mechanizmu fallback. Zaleca się uruchomienie testu end-to-end za pomocą `python code/main.py` i zweryfikowanie, czy końcowa strata na zbiorze tinyshakespeare w konfiguracji nano wynosi poniżej 2,5.
