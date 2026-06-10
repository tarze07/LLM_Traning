---

name: skill-rectified-flow-trainer
description: Kompletna implementacja pętli uczącej dla modeli Rectified Flow z wykorzystaniem bloków AdaLN DiT oraz próbnika Eulera
version: 1.0.0
phase: 4
lesson: 23
tags: [diffusion, rectified-flow, DiT, training]

---

# Pętla ucząca modeli Rectified Flow (Rectified Flow Trainer)

Zaimplementuj czytelną, minimalną pętlę uczącą do optymalizacji małego modelu DiT w paradygmacie Rectified Flow na dowolnym zbiorze obrazów (zapisanych w postaci tensorów).

## Zastosowanie

- Odtworzenie procesu uczenia modeli SD3 / FLUX na mniejszą skalę.
- Porównanie zbieżności i jakości generacji modeli Rectified Flow oraz DDPM na tym samym zbiorze danych.
- Budowa własnego modelu opartego na przepływie prostoliniowym dla specyficznych domen (np. zdjęcia medyczne, satelitarne).

## Dane wejściowe

- `model`: obiekt klasy `nn.Module` przyjmujący na wejściu parę `(x, t)` i zwracający przewidywany wektor prędkości.
- `dataset`: iterator dostarczający czyste obrazy wejściowe.
- `optimizer`: optimizer AdamW (zalecane parametry: `lr=1e-4`, `weight_decay=0.01`, `betas=(0.9, 0.99)`).
- `scheduler`: harmonogram zmian współczynnika uczenia (np. cosinusowy z rozgrzewką – warmup przez 1000 kroków).

## Pojedynczy krok uczenia

```python
def rectified_flow_train_step(model, x0, optimizer, device):
    model.train()
    x0 = x0.to(device)
    n = x0.size(0)
    t = torch.rand(n, device=device)                     # rozkład jednostajny w [0, 1]
    epsilon = torch.randn_like(x0)
    x_t = (1 - t[:, None, None, None]) * x0 + t[:, None, None, None] * epsilon
    target_v = epsilon - x0                              # wektor prędkości docelowej
    pred_v = model(x_t, t)
    loss = F.mse_loss(pred_v, target_v)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    return loss.item()
```

## Procedura próbkowania (metoda Eulera)

```python
@torch.no_grad()
def sample(model, shape, steps=20, device="cpu"):
    model.eval()
    x = torch.randn(shape, device=device)
    dt = 1.0 / steps
    t = torch.ones(shape[0], device=device)
    for _ in range(steps):
        v = model(x, t)
        x = x - dt * v
        t = t - dt
    return x
```

## Wskazówki i dobre praktyki

- Losowanie parametru czasu `t` za pomocą rozkładu jednostajnego `torch.rand` jest w zupełności wystarczające; zaawansowane próbkowanie ważone (np. rozkład log-normalny stosowany w SD3) przynosi niewielki zysk jakościowy, ale nie jest krytyczne na start.
- Stosowanie wykładniczej średniej kroczącej (EMA) dla wag modelu jest standardową praktyką w modelach dyfuzyjnych; warto utrzymywać kopię `ema_model` z parametrem wygładzania `decay=0.9999`.
- Implementacja Classifier-Free Guidance (CFG): podczas uczenia z prawdopodobieństwem 10% zastępuj wektor warunkujący wektorem zerowym (pustym). W czasie wnioskowania (inference) obliczaj ostateczną prędkość jako: `v = v_uncond + w * (v_cond - v_uncond)`, gdzie współczynnik skali `w` wynosi zazwyczaj od 3 do 5.
- W przypadku uczenia w przestrzeni ukrytej (Latent Diffusion, np. FLUX, SD3) cała procedura odbywa się na reprezentacjach z enkodera VAE – wektorem `x0` w powyższym kodzie jest wówczas wynik operacji `VAE.encode(image)`.
- Czas uczenia dla prostego zbioru o rozmiarze 32x32 wynosi zazwyczaj od 2000 do 5000 kroków. W przypadku pełnowymiarowego uczenia produkcyjnego na latentach (SD3, FLUX) proces ten wymaga setek tysięcy iteracji.

## Format raportu

```
[rectified flow training]
  steps:        <int>
  final loss:   <float>
  ema decay:    <float>
  vae?:         yes | no
  cfg dropout:  <współczynnik odrzucenia>

[sampling]
  default steps: 20
  cel dla wersji schnell / turbo: 4
  punkt odniesienia dla pełnej jakości: 50+ (tylko do porównań)
```

## Zasady i ograniczenia

- Nie uruchamiaj procesu uczenia bezpośrednio na surowych wartościach pikseli RGB z zakresu `uint8` [0, 255]; zawsze znormalizuj dane wejściowe do rozkładu o średniej zerowej i jednostkowej wariancji.
- Zawsze monitoruj wartość funkcji straty w podziale na przedziały parametru czasu `t`. Jeśli błąd w początkowych krokach (blisko `t=0`) jest drastycznie wyższy niż dla kroków końcowych (blisko `t=1`), może to oznaczać błędną parametryzację wektora prędkości lub odwrócenie kierunku interpolacji.
- Nie łącz ze sobą formuł wyznaczania celu dla prędkości (Rectified Flow) oraz celu dla szumu (DDPM) w jednej pętli szkoleniowej; wybierz jedną spójną parametryzację.
- Na kartach graficznych o architekturze Ampere i nowszych zaleca się stosowanie formatu `bfloat16` podczas uczenia; obliczenia w standardowym `float16` mogą czasami powodować przepełnienie wartości i powstawanie wartości NaN ze względu na dynamikę zmian wektora prędkości.
