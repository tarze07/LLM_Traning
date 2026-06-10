---

name: img2img-chooser
description: Wybierz podejście „od obrazu do obrazu”, biorąc pod uwagę dane sparowane i niesparowane, specyfikę domeny i budżet opóźnień.
version: 1.0.0
phase: 8
lesson: 04
tags: [pix2pix, img2img, conditional]

---

Biorąc pod uwagę opis zadania (domena źródłowa, domena docelowa, dostępność danych – sparowane/niesparowane/N próbek, budżet opóźnienia, pasek jakości), wynik:

1. Podejście. Pix2Pix (sparowany, wąski), Pix2PixHD (sparowany, wysoka rozdzielczość), CycleGAN (niesparowany), SPADE (seg-to-image) lub wariant ControlNet przez SD3 / Flux.1 (ogólny, otwarta domena).
2. Specyfikacja danych treningowych. Minimalna liczba par, rozdzielczość, rozszerzenia, kwestie licencyjne.
3. Architektura. G (głębokość U-Net, szerokość kanału), D (pole recepcyjne PatchGAN, norma widmowa), wagi strat (adv, L1, VGG-percepcyjne).
4. Opóźnienie wnioskowania. Docelowy ms/obraz na pojedynczym konsumenckim procesorze graficznym (RTX 4090, M3 Max), kompromis w zakresie rozdzielczości.
5. Ewaluacja. LPIPS względem wstrzymanych sparowanych danych, FID na 5 tys. próbek, metryki specyficzne dla zadania (mIoU dla zadań seg, PSNR dla super rozdzielczości), preferencje ludzkie.

Odmów polecania Pix2Pix, gdy dane nie są sparowane – zamiast tego zapisz CycleGAN lub ControlNet. Odmów trenowania sparowanego modelu z mniej niż 500 parami bez porady dotyczącej wzmocnienia/przedtreningu. Oznacz każde żądanie zawierające „dowolny monit tekstowy” — wymagają one rozpowszechniania + ControlNet, a nie sparowanej sieci GAN.