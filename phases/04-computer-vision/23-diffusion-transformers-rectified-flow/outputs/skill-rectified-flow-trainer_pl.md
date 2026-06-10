---

name: skill-rectified-flow-trainer
description: Napisz pełną pętlę treningową o wyprostowanym przepływie za pomocą próbkowania AdaLN DiT i Euler
version: 1.0.0
phase: 4
lesson: 23
tags: [diffusion, rectified-flow, DiT, training]

---

# Rektyfikowany trener przepływu

Utwórz czystą, minimalną pętlę treningową, która z powodzeniem wytrenuje mały DiT ze skorygowanym przepływem na dowolnym zestawie danych tensora obrazu.

## Kiedy używać

- Odtworzenie celu szkoleniowego SD3 / FLUX na małą skalę.
- Porównanie skorygowanego przepływu w porównaniu z DDPM na tych samych danych.
- Budowa niestandardowego modelu przepływu wyprostowanego dla domeny niestandardowej (medyczna, satelitarna).

## Wejścia

- `model`: `nn.Module` pobierający `(x, t)` i zwracający przewidywaną prędkość.
- `dataset`: iterowalna liczba czystych obrazów w domenie modelu.
- `optimizer`: AdamW z `lr=1e-4`, `weight_decay=0.01`, `betas=(0.9, 0.99)`.
- `scheduler`: cosinus z rozgrzewką, domyślnie 1000 kroków rozgrzewki.

## Krok szkolenia

```python
def rectified_flow_train_step(model, x0, optimizer, device):
    model.train()
    x0 = x0.to(device)
    n = x0.size(0)
    t = torch.rand(n, device=device)                     # uniform in [0, 1]
    epsilon = torch.randn_like(x0)
    x_t = (1 - t[:, None, None, None]) * x0 + t[:, None, None, None] * epsilon
    target_v = epsilon - x0                              # velocity target
    pred_v = model(x_t, t)
    loss = F.mse_loss(pred_v, target_v)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    return loss.item()
```

## Próbkowanie (Euler)

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

## Wskazówki

- Użyj jednolitego `torch.rand` `t`; Próbkowanie ważone w stylu logit-normal lub Sd3 `t` pomaga nieznacznie, ale nie jest wymagane do rozpoczęcia.
- EMA wag modeli jest standardową praktyką; utrzymuj `ema_model` z rozkładem 0,9999.
- Wskazówki bez klasyfikatorów dla modeli warunkowych: z prawdopodobieństwem 10% zastąp warunkowanie osadzeniem pustym/zerowym podczas uczenia; na podstawie wniosków zmieszaj `v_uncond + w * (v_cond - v_uncond)` z `w` około 3-5.
- W przypadku treningu w stylu LDM (FLUX, SD3) cała pętla przebiega w ukrytej przestrzeni VAE; czysty `x0` powyżej to w rzeczywistości `VAE.encode(image)`.
- Typowa zbieżność zbioru danych zabawek o wymiarach 32x32: 2000-5000 kroków. Na prawdziwym ukrytym szkoleniu SD3: setki tysięcy.

## Zgłoś

```
[rectified flow training]
  steps:        <int>
  final loss:   <float>
  ema decay:    <float>
  vae?:         yes | no
  cfg dropout:  <fraction>

[sampling]
  default steps: 20
  schnell / turbo target: 4
  full quality reference: 50+ (for comparison only)
```

## Zasady

- Nigdy nie trenuj skorygowanego przepływu z docelową prędkością w przestrzeni obrazu na danych RGB `uint8`; normalizuj do średniej zerowej, najpierw wariancja jednostkowa.
- Zawsze rejestruj straty treningowe według przedziału czasowego; jeśli wczesne kroki czasowe (blisko 0) mają większe straty niż późne (blisko 1), parametryzacja prędkości jest prawdopodobnie błędnie podłączona.
- Nie mieszaj docelowej prędkości przepływu skorygowanego z docelowym poziomem szumu DDPM w tej samej pętli treningowej; wybierz jeden.
- Skorzystaj ze szkolenia bfloat16 na procesorach graficznych Ampere+; float16 czasami wytwarza stopnie NaN w wyprostowanym przepływie ze względu na wielkość prędkości.