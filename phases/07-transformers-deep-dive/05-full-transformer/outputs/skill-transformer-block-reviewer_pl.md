---

name: transformer-block-reviewer
description: Przejrzyj wdrożenie bloku transformatora pod kątem wartości domyślnych z 2026 r. i dryftu flagi.
version: 1.0.0
phase: 7
lesson: 5
tags: [transformers, architecture, review]

---

Biorąc pod uwagę źródło bloku transformatora (PyTorch / JAX / numpy / pseudokod) i jego zamierzoną rolę (koder / dekoder / koder-dekoder), wynik:

1. Kontrola okablowania. Przednormą lub postnormą. Resztkowe połączenia wokół każdej podwarstwy. Oznacz post-normę jako inną niż domyślna na rok 2026, chyba że autor poda powód.
2. Normalizacja. LayerNorm vs RMSNorm. Preferowana norma RMSNorm. Oznacz, jeśli w prognozach Q/K/V/O obecne są terminy odchylenia — większość modeli na rok 2026 je pomija.
3. Kształt uwagi. MHA/GQA/MQA/MLA. Dla bloków dekodera: sprawdź, czy zastosowano maskę przyczynową. Dla wzajemnej uwagi: potwierdź Q z dekodera, K/V z kodera.
4. FFN. Aktywacja (ReLU / GELU / SwiGLU / GeGLU). Współczynnik ekspansji. SwiGLU z ~2,67× jest nowoczesnym ustawieniem domyślnym; 4× ReLU/GELU to klasyka.
5. Sygnał pozycyjny. Potwierdź, że tam, gdzie jest to oczekiwane, zastosowano RoPE / ALiBi / bezwzględny (zazwyczaj projekcje Q, K dla RoPE).

Odmów podpisania bloku, który składa się z więcej niż 12 warstw, w stanie post-normowym i bez harmonogramu rozgrzewki – treningi będą się różnić. Odrzuć blok dekodera bez maskowania przyczynowego. Oznacz dowolny blok, którego ekspansja FFN spadnie poniżej 2-krotności prawdopodobnego niedoboru mocy. Ostrzegaj, jeśli blok zakoduje na stałe `d_model` bez pola konfiguracyjnego do zmiany rozmiaru.