---

name: skill-dcgan-scaffold
description: Narzędzie generujące kompletny szablon (rusztowanie) projektu DCGAN z parametrami z_dim, image_size i num_channels, w tym pętlę uczenia i mechanizm zapisu próbek
version: 1.0.0
phase: 4
lesson: 9
tags: [computer-vision, gan, dcgan, scaffolding]

---

# Szablon projektu DCGAN

Na podstawie trzech wejściowych parametrów generuje gotowy do uruchomienia szablon (szkielet) projektu DCGAN z architekturą dostosowaną do docelowej rozdzielczości obrazu.

## Zastosowanie

- Rozpoczynanie nowych eksperymentów generatywnych na niewielkich zbiorach danych.
- Nauka podstaw działania sieci DCGAN na bazie minimalnego, działającego przykładu.
- Prototypowanie warunkowych sieci GAN (Conditional GAN) – dodawanie informacji o klasach odbywa się na tym samym schemacie bazowym.

## Dane wejściowe

- `image_size`: 32, 64 lub 128 pikseli (musi być potęgą dwójki).
- `num_channels`: 1 (obrazy w skali szarości) lub 3 (RGB).
- `z_dim`: wymiar wektora szumu, zazwyczaj 64 lub 128.
- `with_spectral_norm`: tak | nie; domyślnie tak.

## Specyfikacja architektury

Liczba bloków splotów transponowanych (ConvTranspose2d) w generatorze G oraz bloków splotów o zmienionym kroku (Conv2d) w dyskryminatorze D zależy od parametru `image_size`:

| image_size | Bloki G | Bloki D |
|------------|---------|---------|
| 32         | 4       | 4       |
| 64         | 5       | 5       |
| 128        | 6       | 6       |

Każdy kolejny blok podwaja (w G) lub zmniejsza o połowę (w D) wymiar przestrzenny obrazu. Liczba kanałów cech (features) zaczyna się od wartości bazowej (np. 32 lub 64) i jest skalowana jako `feat_base * 2^index_bloku`.

## Pliki wynikowe

- `model.py` — definicje klas Generator oraz Discriminator
- `train.py` — pętla uczenia, obliczanie funkcji straty, konfiguracja optymalizatora
- `sample.py` — skrypt do generowania i zapisu siatek obrazów próbnych
- `config.json` — konfiguracja hiperparametrów
- `README.md` — krótka instrukcja uruchomienia (szybki start)

## Format raportu

```
[scaffold]
  image_size:       <int>
  num_channels:     <int>
  z_dim:            <int>
  spectral_norm:    yes | no

[arch]
  G blocks:         <N>, channels: [list]
  D blocks:         <N>, channels: [list]
  G params (est):   <N>
  D params (est):   <N>

[training defaults]
  optimizer:   Adam(lr=2e-4, betas=(0.5, 0.999))
  batch_size:  64
  epochs:      50
  sample_every: 1 epoch

[files written]
  - model.py
  - train.py
  - sample.py
  - config.json
  - README.md
```

## Reguły

- Zawsze stosuj aktywację `nn.Tanh()` na wyjściu generatora G oraz skaluj obrazy treningowe do przedziału [-1, 1].
- Zawsze stosuj aktywację `LeakyReLU(0.2)` w dyskryminatorze D.
- Jeśli `with_spectral_norm == yes`, nałoż `spectral_norm()` na każdą warstwę splotową w dyskryminatorze D i usuń z niego warstwy BatchNorm. W generatorze G pozostaw BatchNorm bez zmian.
- Nigdy nie generuj szablonu dla rozdzielczości `image_size` większej niż 128. Przy wyższych rozdzielczościach model DCGAN staje się niestabilny; w takich wypadkach skieruj użytkownika do modeli StyleGAN lub modeli dyfuzyjnych.
