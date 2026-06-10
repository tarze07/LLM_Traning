---

name: vae-trainer
description: Określ architekturę VAE, rozmiar ukryty, harmonogram wersji beta i plan ewaluacji dla danego zbioru danych i jego dalszego wykorzystania.
version: 1.0.0
phase: 8
lesson: 02
tags: [vae, latent, generative]

---

Biorąc pod uwagę profil zbioru danych (modalność, rozdzielczość, rozmiar zbioru danych) i dalsze wykorzystanie (tylko rekonstrukcja, próbkowanie lub koder wejściowy dla modelu utajonej dyfuzji lub modelu tokenu AR), wynik:

1. Wariant. Zwykły VAE, beta-VAE, VQ-VAE, RVQ (resztkowy) lub NVAE. Powód w jednym zdaniu powiązany z modalnością i dalszym zastosowaniem.
2. Architektura. Topologia kodera/dekodera (współczynnik próbkowania konwersji, szerokość kanału, ukryte przyciemnienie, bloki uwagi). W stosownych przypadkach podaj publiczne wagi referencyjne (`sd-vae-ft-ema`, Encodec, DAC, WAN-VAE).
3. Przyciemnienie utajone. Przyciemnienie przestrzenne i kanałowe. Całkowita liczba bitów na próbkę. Współczynnik kompresji a surowe dane.
4. Harmonogram wersji beta. Rampa rozgrzewania, wartość końcowa i próg wolnych bitów, jeśli są używane.
5. Plan ewaluacyjny. Rekonstrukcja MSE / SSIM / PSNR, KL na przyciemnienie, liczba aktywnych przyciemnień, próg alarmu tylnego zapadnięcia, odległość Frecheta między `q(z|x)` i wcześniejszym.

Odmówić wysłania VAE z beta > 0,5 na początku treningu (zapadnięcie tylne). Odmawiaj używania zwykłego Gaussa VAE jako końcowego generatora obrazów – będzie rozmyty; zamiast tego użyj go jako ukrytego kodera dla modelu dyfuzji lub dopasowywania przepływu. Oznacz dowolny VQ-VAE z wykorzystaniem książki kodowej poniżej 20% jako źle skonfigurowaną politykę resetowania książki kodowej.