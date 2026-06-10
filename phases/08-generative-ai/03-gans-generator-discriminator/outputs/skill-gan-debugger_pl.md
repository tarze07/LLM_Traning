---
name: gan-debugger
description: Diagnozuj nieudane treningi GAN na podstawie krzywych strat i siatek próbek; sugeruj szybkie poprawki.
version: 1.0.0
phase: 8
lesson: 03
tags: [gan, adversarial, debugging]
---

Biorąc pod uwagę nieudany przebieg treningu GAN (krzywe straty D i G, siatka wygenerowanych próbek, rozmiar zbioru danych, konfiguracja optymalizatora), wypisz:

1. Diagnozę. Jedną z głównych przyczyn z następujących: mode collapse (zapaść trybu), D jest zbyt silny, D jest zbyt słaby, znikający gradient, batch-norm leakage (przeciekanie informacji), przeuczenie D (overfit D), niedopasowanie learning rate, zła inicjalizacja (bad init).
2. Dowody. Wskazówka na sygnał z krzywych strat lub próbek (np. "D(fake) < 0.05 na kroku 500 = D jest zbyt silny").
3. Naprawa (Fix). Jedna konkretna zmiana. Przykłady: `lr_D = lr_G / 2`, zastąpienie BN normą IN, dodanie spectral norm do D, zmiana na WGAN-GP z lambda=10, przecięcie batch size na pół, dodanie szumu Gaussa 0.1 na wejściach D.
4. Protokół re-run (ponownego uruchomienia). Ziarna (seeds) do wypróbowania, liczba kroków przed kolejną weryfikacją, kryterium akceptacji (np. "FID spada poniżej punktu odniesienia przed krokiem 20k").
5. Opcja zapasowa (Fallback). Co zrobić, jeśli poprawka nie poskutkuje przy pierwszym uruchomieniu. Zazwyczaj: zmień architekturę (StyleGAN, R3GAN) lub zmień paradygmat (dyfuzja, flow matching), jeśli zbiór danych jest zbyt różnorodny.

Odmów rekomendowania zwiększenia learning rate G, kiedy D jest już nasycony. Odmów dodania regularyzacji do G, kiedy prawdziwym problemem jest D - najpierw napraw D. Oznacz jako błędną inicjalizację, jeśli trening całkowicie się psuje w ciągu pierwszych 100 kroków (a nie jako głęboki błąd algorytmiczny).