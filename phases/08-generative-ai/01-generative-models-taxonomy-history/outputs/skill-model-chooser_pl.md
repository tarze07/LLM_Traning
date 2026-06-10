---

name: generative-model-chooser
description: Wybierz rodzinę modelu generatywnego, szkielet i hostowaną alternatywę dla danego zadania i budżetu.
version: 1.0.0
phase: 8
lesson: 01
tags: [generative, taxonomy]

---

Biorąc pod uwagę opis zadania (modalność, dziedzina, budżet opóźnienia, budżet obliczeniowy, sygnał kondycjonujący), wynik:

1. Rodzina. Jawne-wykonalne, jawne-przybliżone (VAE/dyfuzja), ukryte (GAN), dopasowanie wyniku/przepływu lub token-AR. Powód jednozdaniowy powiązany z modalnością + opóźnieniem.
2. Szkielet + otwarte odniesienie. Jeden wstępnie wytrenowany model z otwartymi ciężarami, który użytkownik może już dziś dostroić (np. Stable Diffusion 3, Flux.1-dev, AudioCraft 2, StyleGAN3, 3D Gaussian Splatting).
3. Hostowane alternatywy. Trzy produkcyjne interfejsy API uszeregowane według kompromisu jakość/koszt/opóźnienie (fal.ai, Replicate, Stability, Runway, Veo, Kling, ElevenLabs itp.).
4. Tryb awaryjny. Znana patologia dla wybranej rodziny (załamanie trybu, błąd ekspozycji, dryf próbnika, artefakty tokenizera, gra z wynikiem CLIP).
5. Budżet. Przybliżone godziny szkolenia na pojedynczym procesorze A100, koszt wnioskowania na próbkę, minimalna ilość pamięci VRAM.

Odmów rekomendowania sieci GAN, gdy zadanie wymaga oceny wiarygodności. Odmów rekomendowania autoregresyjnej funkcji over-pixels do użytku w czasie rzeczywistym w wysokiej rozdzielczości. Oznacz wszelkie zalecenia dotyczące „trenowania od zera”, jeśli wymieniona otwarta sieć szkieletowa obejmuje już domenę.