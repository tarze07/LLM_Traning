---

name: skill-heatmap-to-coords
description: Zapisz subpikselową procedurę przekształcania mapy cieplnej w koordynację stosowaną w każdym modelu pozycji produkcyjnej
version: 1.0.0
phase: 4
lesson: 21
tags: [keypoint, pose, subpixel, inference]

---

# Mapa termiczna do współrzędnych

Zamień surowe mapy cieplne punktów kluczowych na współrzędne o dokładności subpikselowej. Najtańsze ulepszenie dokładności w każdym potoku pozy.

## Kiedy używać

- Wdrożenie modelu punktu kluczowego opartego na mapie cieplnej.
- Benchmarking wskaźników pozycji — firma OKS jest niezwykle wrażliwa na dokładność subpikselową.
- Przenoszenie kodu pozycji z jednego frameworka do drugiego.

## Wejścia

- `heatmaps`: tensor `(N, K, H, W)`, mapy cieplne poszczególnych punktów kluczowych z modelu.
- `confidence_threshold`: odrzuć punkty kluczowe, których szczyt jest poniżej tej wartości.

## Kroki

1. **Argmax** każda mapa cieplna, aby znaleźć lokalizację piku w postaci liczby całkowitej.
2. **Przesunięcie pierwszej różnicy** — szacunkowe przesunięcie subpiksela od sąsiadujących pikseli. Współczynnik `0.25` jest heurystycznie skalibrowany dla map cieplnych Gaussa z `sigma >= 1`; w celu odzyskania subpikseli należy zastosować pełne dopasowanie kwadratowe (DARK) lub dopasowanie Gaussa.

```
dx = 0.25 * sign(heatmap[y, x+1] - heatmap[y, x-1])
dy = 0.25 * sign(heatmap[y+1, x] - heatmap[y-1, x])
```

Dla wariantu DARK/kwadratowy przybliżenie przy użyciu lokalnego kwadratu:

```
dx = -0.5 * (heatmap[y, x+1] - heatmap[y, x-1])
        / (heatmap[y, x+1] - 2 * heatmap[y, x] + heatmap[y, x-1] + eps)
```

Dopasowanie kwadratowe jest dokładniejsze w przypadku map cieplnych z wartościami szczytowymi; przesunięcie oparte na znakach jest bezpieczniejszym ustawieniem domyślnym, gdy mapy cieplne są zaszumione.

3. **Dodaj przesunięcie** do piku całkowitego.
4. **Pewność** — zwraca wartość szczytową dla każdego punktu kluczowego; klienci używają go do maskowania przewidywań o niskim poziomie pewności.
5. **Przypadek graniczny** — gdy szczyt ląduje na pierwszym lub ostatnim pikselu wzdłuż osi, jeden z sąsiadów zostaje zaciśnięty; przesunięcie spada do zera, co jest najbezpieczniejszym rozwiązaniem awaryjnym.

## Szablon wyjściowy

```python
import torch

def heatmap_to_coords_subpixel(heatmaps, threshold=0.2):
    N, K, H, W = heatmaps.shape
    flat = heatmaps.reshape(N, K, -1)
    conf, idx = flat.max(dim=-1)
    ys = (idx // W).float()
    xs = (idx % W).float()

    ys_int = ys.long()
    xs_int = xs.long()

    x_minus = (xs_int - 1).clamp(min=0)
    x_plus = (xs_int + 1).clamp(max=W - 1)
    y_minus = (ys_int - 1).clamp(min=0)
    y_plus = (ys_int + 1).clamp(max=H - 1)

    batch_idx = torch.arange(N).view(-1, 1).expand(-1, K)
    kp_idx = torch.arange(K).view(1, -1).expand(N, -1)

    dx_raw = (heatmaps[batch_idx, kp_idx, ys_int, x_plus]
              - heatmaps[batch_idx, kp_idx, ys_int, x_minus])
    dy_raw = (heatmaps[batch_idx, kp_idx, y_plus, xs_int]
              - heatmaps[batch_idx, kp_idx, y_minus, xs_int])
    dx = 0.25 * torch.sign(dx_raw)
    dy = 0.25 * torch.sign(dy_raw)

    at_left = xs_int == 0
    at_right = xs_int == (W - 1)
    at_top = ys_int == 0
    at_bottom = ys_int == (H - 1)
    dx = torch.where(at_left | at_right, torch.zeros_like(dx), dx)
    dy = torch.where(at_top | at_bottom, torch.zeros_like(dy), dy)

    refined_x = xs + dx
    refined_y = ys + dy
    coords = torch.stack([refined_x, refined_y], dim=-1)
    mask = conf >= threshold
    return coords, conf, mask
```

## Zgłoś

```
[subpixel decode]
  keypoints:   K
  threshold:   <float>
  valid_rate:  fraction of keypoints above threshold
```

## Zasady

- Zawsze dopasowuj indeksy sąsiadów do prawidłowego zakresu; punkty kluczowe znajdujące się poza krawędzią mają przesunięcie o zerowej różnicy, ale nie powodują awarii.
- Zwróć pewność wraz ze współrzędnymi, aby klienci mogli maskować punkty o niskim stopniu pewności.
— Udoskonalenie subpikseli pomaga tylko wtedy, gdy mapa cieplna jest gładka wokół szczytu — sprawdź, czy w szkoleniu zastosowano cel Gaussa z sigma >= 1.
- W przypadku bardzo małych rozdzielczości mapy cieplnej (< 48x48) rozważ zwiększenie próbkowania mapy cieplnej do pełnego rozmiaru obrazu przed wyodrębnieniem współrzędnych; przesunięcie subpikselowe skaluje się wraz z krokiem.