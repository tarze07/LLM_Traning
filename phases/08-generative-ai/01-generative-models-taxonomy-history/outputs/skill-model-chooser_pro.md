---

name: generative-model-chooser
description: Wybierz odpowiednią rodzinę modeli generatywnych, architekturę (szkielet) oraz alternatywne rozwiązanie w chmurze (hostowane) dla danego zadania i budżetu.
version: 1.0.0
phase: 8
lesson: 01
tags: [generative, taxonomy]

---

Biorąc pod uwagę opis zadania (modalność, dziedzina, wymagania dotyczące opóźnień, budżet obliczeniowy, sygnał warunkujący), wygeneruj:

1. Rodzina modeli. Model o jawnej gęstości (explicit-tractable), jawnej przybliżonej (VAE/dyfuzja), niejawnej (GAN), dopasowywanie gradientu pola punktowego/przepływu (score/flow matching) lub autoregresyjny (token-AR). Podaj jednozdaniowe uzasadnienie powiązane z modalnością i czasem reakcji (opóźnieniem).
2. Architektura bazowa (szkielet) i otwarty model referencyjny. Wskaż jeden gotowy model typu open-weights (o otwartych wagach), który użytkownik może samodzielnie dostroić (np. Stable Diffusion 3, Flux.1-dev, AudioCraft 2, StyleGAN3, 3D Gaussian Splatting).
3. Rozwiązania hostowane (usługi chmurowe). Trzy produkcyjne interfejsy API uporządkowane pod kątem kompromisu między jakością, kosztem a opóźnieniem (np. fal.ai, Replicate, Stability, Runway, Veo, Kling, ElevenLabs itp.).
4. Tryb awaryjny (typowe problemy). Wskaż znane ograniczenia/patologie wybranej rodziny modeli (np. zapadanie się modów (mode collapse), błąd ekspozycji, dryf próbkowania, artefakty tokenizera, nadmierna optymalizacja wskaźnika CLIP).
5. Budżet. Szacunkowa liczba godzin obliczeniowych dla pojedynczego procesora GPU A100, koszt wnioskowania na jedną próbkę oraz minimalna wymagana pamięć VRAM.

Odrzuć rekomendację sieci GAN, gdy zadanie wymaga dokładnego szacowania gęstości prawdopodobieństwa (oceny wiarygodności). Odrzuć rekomendację modeli autoregresyjnych przetwarzających bezpośrednio piksele (pixel-by-pixel autoregressive) do zastosowań w czasie rzeczywistym i w wysokiej rozdzielczości. Oznacz flagą ostrzegawczą zalecenia dotyczące „trenowania od zera”, jeśli istnieją już gotowe, otwarte architektury bazowe obejmujące daną domenę.
