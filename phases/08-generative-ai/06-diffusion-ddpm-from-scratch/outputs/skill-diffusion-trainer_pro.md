---

name: diffusion-trainer
description: Skonfiguruj proces uczenia modelu dyfuzyjnego: harmonogram szumu, cel predykcji, próbnik (sampler) oraz plan ewaluacji.
version: 1.0.0
phase: 8
lesson: 06
tags: [diffusion, ddpm, training]

---

Biorąc pod uwagę specyfikację zbioru danych (modalność, rozdzielczość, rozmiar zbioru), budżet obliczeniowy (godziny GPU, minimalna pamięć VRAM) oraz wymagania jakościowe (docelowy wskaźnik FID lub dalsze zastosowanie), wygeneruj:

1. Harmonogram szumu (Noise Schedule). Liniowy, cosinusowy (metoda Nichola) lub sigmoidalny. Liczba kroków czasowych T (1000 dla bazowego modelu DDPM; 256 dla szybszych wariantów).
2. Cel predykcji (Prediction Objective). Predykcja szumu (epsilon), predykcja v (v-prediction) lub bezpośrednia predykcja oryginalnego obrazu (x_0). Podaj uzasadnienie uwzględniające rozdzielczość oraz stosunek sygnału do szumu (SNR) w trakcie procesu dyfuzji.
3. Architektura. Architektura U-Net (głębokość i szerokość kanałów) dla dyfuzji w przestrzeni pikseli, DiT (Diffusion Transformer) dla dyfuzji utajonej (latent) lub 3D U-Net / DiT dla wideo. Uwzględnij schemat osadzania kroku czasowego (sinusoidalny embedding + MLP, warstwy FiLM lub AdaLN).
4. Próbnik (Sampler). DDIM (20–50 kroków), DPM-Solver++ (10–20 kroków), Euler-Ancestral (Euler-A, dający bardziej kreatywne wyniki) lub wersje destylowane (1–4 kroki). Dołącz zalecenia dotyczące skali naprowadzania bezklasyfikatorowego (CFG scale, parametr w).
5. Plan ewaluacji. Metryki: FID, KID, CLIP-Score, ocena ludzka; określ liczbę próbek (>=10k dla FID) oraz protokół dostrajania (sweep) dla parametru CFG w.

Odrzuć rekomendację trenowania modelu dyfuzyjnego bezpośrednio w przestrzeni pikseli dla rozdzielczości >=256x256 – w tym przypadku utajona dyfuzja (latent diffusion) pozwala uzyskać taką samą jakość przy 16-krotnie mniejszym nakładzie obliczeniowym (FLOP). Odrzuć projekty generowania warunkowego bez mechanizmu CFG (naprowadzania bezklasyfikatorowego) – próby generowania bezwarunkowego za pomocą modelu warunkowego zazwyczaj dają zdegenerowane wyniki. Oznacz flagą ostrzegawczą każdy harmonogram z parametrem beta_T > 0.1, ze względu na ryzyko niestabilności lub nasycenia procesu uczenia.
