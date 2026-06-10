---
name: gan-debugger
description: Diagnozuj nieudane próby uczenia sieci GAN na podstawie krzywych strat i wygenerowanych próbek; sugeruj szybkie rozwiązania.
version: 1.0.0
phase: 8
lesson: 03
tags: [gan, adversarial, debugging]
---

Biorąc pod uwagę nieudany proces uczenia sieci GAN (krzywe strat D i G, siatka wygenerowanych próbek, rozmiar zbioru danych, konfiguracja optymalizatora), wygeneruj:

1. Diagnoza. Wskaż jedną z głównych przyczyn spośród następujących: zapadanie się modów (mode collapse), zbyt silny dyskryminator (D), zbyt słaby dyskryminator (D), znikający gradient, wyciek informacji przez Batch Normalization (batch-norm leakage), przeuczenie dyskryminatora (overfitting D), niedopasowanie współczynników uczenia (learning rates), niepoprawna inicjalizacja wag.
2. Uzasadnienie. Wskazanie konkretnych sygnałów na krzywych strat lub w wygenerowanych próbkach (np. „D(fake) < 0.05 w kroku 500 = zbyt silny dyskryminator D”).
3. Rozwiązanie (Fix). Jedna konkretna zmiana. Przykłady: ustawienie `lr_D = lr_G / 2`, zastąpienie Batch Normalization przez Instance Normalization (IN), dodanie normalizacji spektralnej (spectral normalization) do D, przejście na architekturę WGAN-GP z parametrem lambda=10, zmniejszenie rozmiaru wsadu (batch size) o połowę, dodanie szumu gaussowskiego o wadze 0.1 do wejść D.
4. Protokół ponownego uruchomienia. Wartości inicjujące (seeds) do przetestowania, liczba kroków przed kolejną weryfikacją oraz kryterium akceptacji (np. „spadek wskaźnika FID poniżej poziomu odniesienia przed krokiem 20k”).
5. Opcja zapasowa (Fallback). Działania na wypadek, gdyby sugerowane rozwiązanie nie przyniosło efektów. Zazwyczaj: zmiana architektury (np. StyleGAN, R3GAN) lub zmiana paradygmatu modelowania (dyfuzja, dopasowywanie przepływu - flow matching), jeśli zbiór danych charakteryzuje się zbyt wysoką różnorodnością.

Odrzuć rekomendację zwiększenia współczynnika uczenia G, gdy dyskryminator D jest już nasycony. Odrzuć pomysł dodawania regularyzacji do generatora G, gdy problem leży po stronie dyskryminatora D – najpierw napraw D. Oznacz awarię jako błąd inicjalizacji (a nie głęboki problem algorytmiczny), jeśli proces uczenia załamuje się całkowicie w ciągu pierwszych 100 kroków.
