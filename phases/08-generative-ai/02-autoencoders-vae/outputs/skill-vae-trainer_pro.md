---

name: vae-trainer
description: Określ architekturę VAE, rozmiar przestrzeni ukrytej (latent size), harmonogram współczynnika beta oraz plan ewaluacji dla danego zbioru danych i jego docelowego zastosowania.
version: 1.0.0
phase: 8
lesson: 02
tags: [vae, latent, generative]

---

Biorąc pod uwagę specyfikację zbioru danych (modalność, rozdzielczość, rozmiar zbioru) oraz jego dalsze wykorzystanie (tylko rekonstrukcja, próbkowanie, koder wejściowy dla modelu utajonej dyfuzji lub model tokenizera AR), wygeneruj:

1. Wariant modelu. Standardowy VAE, beta-VAE, VQ-VAE, RVQ (resztkowy VQ-VAE) lub NVAE. Podaj jednozdaniowe uzasadnienie powiązane z modalnością i docelowym zastosowaniem.
2. Architektura. Topologia kodera i dekodera (współczynnik próbkowania w dół/w górę, szerokość kanałów, wymiar przestrzeni ukrytej, bloki uwagi). W stosownych przypadkach wskaż referencyjne, publicznie dostępne wagi (np. `sd-vae-ft-ema`, Encodec, DAC, WAN-VAE).
3. Wymiar przestrzeni ukrytej (latent). Wymiary przestrzenne oraz liczba kanałów. Całkowita liczba bitów na próbkę. Współczynnik kompresji w porównaniu do danych wejściowych.
4. Harmonogram współczynnika beta. Profil rozgrzewania (warmup), wartość końcowa oraz próg wolnych bitów (free bits threshold), jeśli są stosowane.
5. Plan ewaluacji. Metryki rekonstrukcji: MSE, SSIM, PSNR; dywergencja KL na wymiar, liczba aktywnych wymiarów ukrytych, próg alarmowy dla zjawiska zapadania się rozkładu a posteriori (posterior collapse), odległość Frécheta między `q(z|x)` a rozkładem a priori.

Odrzuć propozycję uruchomienia treningu VAE ze współczynnikiem beta > 0.5 na samym początku (grozi to zapadnięciem rozkładu a posteriori - posterior collapse). Odrzuć stosowanie standardowego gaussowskiego VAE jako samodzielnego generatora obrazów (wygenerowane obrazy będą rozmyte) – zamiast tego rekomenduj użycie go jako kodera przestrzeni ukrytej (latent encoder) dla modelu dyfuzyjnego lub dopasowywania przepływu (flow matching). Oznacz flagą ostrzegawczą każdy model VQ-VAE, w którym wykorzystanie książki kodowej (codebook utilization) spada poniżej 20% (wskazuje to na błędną konfigurację polityki resetowania książki kodowej).
