---

name: img2img-chooser
description: Wybierz odpowiednie podejście typu „obraz do obrazu” (img2img), biorąc pod uwagę dostępność danych sparowanych/niesparowanych, specyfikę domeny oraz ograniczenia czasowe (opóźnienia).
version: 1.0.0
phase: 8
lesson: 04
tags: [pix2pix, img2img, conditional]

---

Biorąc pod uwagę opis zadania (domena źródłowa, domena docelowa, dostępność danych – sparowane/niesparowane/liczba próbek, wymagania dotyczące opóźnień, kryteria jakości), wygeneruj:

1. Podejście. Pix2Pix (dane sparowane, wąska domena), Pix2PixHD (dane sparowane, wysoka rozdzielczość), CycleGAN (dane niesparowane), SPADE (generowanie obrazu z map segmentacji) lub wariant ControlNet oparty na SD3 / Flux.1 (ogólne zastosowania, otwarta domena).
2. Specyfikacja danych treningowych. Minimalna liczba par obrazów, rozdzielczość, metody augmentacji, kwestie licencyjne.
3. Architektura. Generator G (głębokość U-Net, szerokość kanałów), dyskryminator D (pole recepcyjne PatchGAN, normalizacja spektralna), wagi funkcji strat (strata adwersarialna, L1, percepcyjna VGG).
4. Opóźnienie wnioskowania (Inference Latency). Docelowy czas generowania (ms na obraz) na pojedynczym konsumenckim GPU (np. RTX 4090, M3 Max) oraz kompromis związany z rozdzielczością.
5. Ewaluacja. Metryka LPIPS na wydzielonym zbiorze sparowanym, wskaźnik FID na próbie 5k wygenerowanych obrazów, metryki specyficzne dla zadania (mIoU dla zadań segmentacji, PSNR dla super-rozdzielczości) oraz ocena ludzka (human preference).

Odrzuć rekomendację Pix2Pix, gdy dane nie są sparowane (wtedy zaproponuj CycleGAN lub ControlNet). Odrzuć propozycję trenowania modelu sparowanego na zbiorze liczącym mniej niż 500 par bez wskazówek dotyczących augmentacji danych lub pre-treningu. Oznacz flagą ostrzegawczą każde zapytanie wymagające obsługi „dowolnych promptów tekstowych” – takie zadania wymagają modeli dyfuzyjnych z ControlNet, a nie klasycznych sparowanych sieci GAN.
