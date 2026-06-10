---

name: diffusion-trainer
description: Skonfiguruj przebieg szkolenia dyfuzyjnego: harmonogram, cel przewidywania, próbnik i plan oceny.
version: 1.0.0
phase: 8
lesson: 06
tags: [diffusion, ddpm, training]

---

Biorąc pod uwagę profil zbioru danych (modalność, rozdzielczość, rozmiar zbioru danych), budżet obliczeniowy (godziny GPU, minimalna pojemność VRAM) i pasek jakości (docelowy FID lub dalsze wykorzystanie), wynik:

1. Harmonogram. Liniowy, cosinus (Nichol) lub sigmoidalny. Liczba kroków T (1000 dla wartości bazowej DDPM; 256 dla szybszych wariantów).
2. Cel przewidywania. epsilon, v-predykcja lub x_0. Powód związany z rozdzielczością i stosunkiem sygnału do szumu w całym harmonogramie.
3. Architektura. Głębokość U-Net + szerokość kanału dla dyfuzji pikseli, DiT dla dyfuzji utajonej lub 3D U-Net / DiT dla wideo. Uwzględnij schemat osadzania czasu (sinusoidalny + MLP, FiLM lub AdaLN).
4. Próbnik. DDIM (20-50 kroków), DPM-Solver++ (10-20), Euler-A (kreatywny) lub destylowany 1-4-etap. Dołącz zalecenia dotyczące skali wytycznych (CFG w).
5. Plan ewaluacyjny. FID / KID / CLIP-score / preferencje ludzkie, z liczbą próbek (>=10 tys. dla FID), protokół przeszukiwania dla CFG w.

Odmów zalecania trenowania dyfuzji w przestrzeni pikseli na poziomie >=256x256, gdy dyfuzja utajona osiąga tę samą jakość przy 1/16 FLOP. Odmów wysłania modelu bez CFG do generacji warunkowej – próbki bezwarunkowe typu zero-shot z modelu warunkowego są zwykle zdegenerowane. Oznacz dowolny harmonogram za pomocą beta_T &gt; Prawdopodobieństwo, że trening nasycony lub niestabilny będzie wynosił 0,1.