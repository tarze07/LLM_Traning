---

name: vit-configurator
description: Dobierz wariant architektury Vision Transformer (ViT), rozmiar patcha oraz strategię pre-trainingu dla wybranego zadania komputerowej wizji.
version: 1.0.0
phase: 7
lesson: 9
tags: [transformers, vit, vision]

---

Na podstawie opisu zadania wizyjnego (klasyfikacja / segmentacja / detekcja obiektów / wyszukiwanie obrazów), rozdzielczości obrazów, rozmiaru zbioru danych (etykietowane i nieetykietowane) oraz założeń wdrożeniowych wygeneruj:

1. Model bazowy (backbone): jeden z modeli: DINOv2 ViT-L/14 (rekomendowany do wyszukiwania i klasyfikacji), enkoder SAM 2/3 (dla segmentacji), SigLIP (dla modeli multimodalnych vision-language) lub ConvNeXt (dla zastosowań z restrykcyjnymi limitami opóźnień). Podaj jednozdaniowe uzasadnienie.
2. Rozmiar patcha: np. 16 dla standardowej klasyfikacji przy rozdzielczości 224x224, 14 dla DINOv2, 8 dla detekcji obiektów o wysokiej gęstości w wysokiej rozdzielczości. Oblicz długość sekwencji tokenów według wzoru `(H/P)^2 + 1` oraz wskaż narzut pamięciowy atencji klasy `O(N^2)`.
3. Wstępnie wytrenowany checkpoint: nazwa konkretnego punktu kontrolnego. Dla małych zbiorów etykietowanych (<10k): zamrożenie cech DINOv2 + warstwa liniowa (linear probe). Dla dużych zbiorów (>100k): dostrojenie końcowych bloków sieci. Podaj uzasadnienie.
4. Przepis na trening (training recipe): optymalizator (AdamW), współczynnik uczenia (learning rate), techniki augmentacji danych (RandAugment, Mixup, Random Erasing), wygładzanie etykiet (label smoothing - typowo 0.1) oraz EMA (Exponential Moving Average).
5. Analiza ryzyka: zbyt mała ilość danych do pełnego dostrojenia (overfitting), niezgodność rozdzielczości (trening na 224 → wdrożenie na 1024 bez interpolacji pozycji) lub brak tokenów rejestru (register tokens - co może negatywnie wpłynąć na cechy reprezentacji DINOv2).

Odmawiaj rekomendowania trenowania modeli ViT od zera (from scratch) na zbiorach zawierających mniej niż 1 milion obrazów – w takich przypadkach tradycyjne architektury CNN (baselines) osiągną lepsze wyniki. Odmawiaj rekomendowania rozmiaru patcha, który prowadzi do długości sekwencji > 4096, bez wdrożenia technologii FlashAttention lub wariantów hierarchicznych (np. Swin Transformer). Oznacz jako błąd każdą konfigurację, która zmienia rozdzielczość wejściową obrazu bez przeprowadzenia interpolacji osadzeń pozycyjnych (positional embeddings).
