---

name: skill-dcgan-scaffold
description: Napisz kompletne rusztowanie DCGAN z z_dim, image_size i num_channels, łącznie z pętlą treningową i oszczędzaniem próbek
version: 1.0.0
phase: 4
lesson: 9
tags: [computer-vision, gan, dcgan, scaffolding]

---

# Rusztowanie DCGAN

Biorąc pod uwagę trzy parametry, wyemituj działający szkielet projektu DCGAN z architekturą odpowiednio dobraną do docelowej rozdzielczości obrazu.

## Kiedy używać

- Rozpoczęcie nowego eksperymentu generatywnego na małym zbiorze danych.
- Nauczanie podstaw DCGAN na minimalnym działającym przykładzie.
- Prototypowanie warunkowych sieci GAN (wstrzykiwanie etykiet odbywa się na tym samym rusztowaniu).

## Wejścia

- `image_size`: jedna z 32, 64, 128 (musi być potęgą dwójki).
- `num_channels`: 1 (skala szarości) lub 3 (RGB).
- `z_dim`: zazwyczaj 64 lub 128.
- `with_spectral_norm`: tak | NIE; domyślnie tak.

## Rozmiary architektury

Liczba transponowanych bloków konw. w G i bloków konw. krokowych w D zależy od `image_size`:

| rozmiar_obrazu | G bloki | D bloki |
|------------|----------|---------|
| 32 | 4 | 4 |
| 64 | 5 | 5 |
| 128 | 6 | 6 |

Każdy dodatkowy blok podwaja (G) lub zmniejsza o połowę (D) wymiar przestrzenny. Liczba funkcji zaczyna się od 32 i skaluje się z `feat_base * 2^block_index`.

## Pliki wyjściowe

- `model.py` — klasy Generator + Dyskryminator
- `train.py` — pętla treningowa, strata, konfiguracja optymalizatora
- `sample.py` — przykładowy wygaszacz siatki
- `config.json` — hiperparametry
- `README.md` — 10-liniowy szybki start

## Zgłoś

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

## Zasady

- Zawsze używaj `nn.Tanh()` na wyjściu G i skaluj dane do [-1, 1] podczas treningu.
- Zawsze używaj `LeakyReLU(0.2)` w D.
- Kiedy `with_spectral_norm == yes`, zawiń każdą konwersję w D za pomocą `spectral_norm()` i usuń BatchNorm z D. Zachowaj BatchNorm w G.
- Nigdy nie emituj szkieletu dla image_size > 128 — powyżej tego DCGAN staje się niestabilny; skieruj użytkownika do StyleGAN lub modelu dyfuzyjnego.