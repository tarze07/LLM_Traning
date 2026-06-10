---

name: skill-heatmap-to-coords
description: Kod realizujący uściślanie subpikselowe przy przekształcaniu map ciepła na współrzędne w modelach detekcji pozycji
version: 1.0.0
phase: 4
lesson: 21
tags: [keypoint, pose, subpixel, inference]

---

# Przekształcanie map ciepła na współrzędne (Heatmap to Coordinates)

Przekształć surowe mapy ciepła z detektora punktów kluczowych na współrzędne o precyzji subpikselowej. Jest to najprostszy i najtańszy sposób na podniesienie dokładności w dowolnym potoku szacowania pozycji.

## Zastosowanie

- Wdożenie modeli detekcji punktów kluczowych opartych na mapach ciepła.
- Precyzyjna ocena jakości modeli – metryka OKS (Object Keypoint Similarity) jest bardzo czuła na dokładność subpikselową.
- Przenoszenie lub portowanie algorytmów szacowania pozycji pomiędzy różnymi frameworkami.

## Dane wejściowe

- `heatmaps`: tensor o wymiarach `(N, K, H, W)` reprezentujący wyjściowe mapy ciepła dla K punktów kluczowych.
- `confidence_threshold`: próg ufności (punkty o wartości szczytowej poniżej tego progu zostaną odrzucone).

## Kroki algorytmu

1. **Wyszukanie maksimum (Argmax)**: dla każdej mapy ciepła lokalizowana jest współrzędna całkowitoliczbowa o najwyższej wartości.
2. **Uściślenie subpikselowe (Subpixel Offset)**: obliczenie przesunięcia na podstawie wartości sąsiednich pikseli. Przemnożenie różnicy przez współczynnik `0.25` to sprawdzona heurystyka dla map ciepła z rozkładem Gaussa o wariancji `sigma >= 1`. Bardzie zaawansowane metody, takie jak dopasowanie kwadratowe (DARK) lub dopasowanie rozkładu Gaussa, pozwalają uzyskać jeszcze wyższą precyzję.

```
dx = 0.25 * sign(heatmap[y, x+1] - heatmap[y, x-1])
dy = 0.25 * sign(heatmap[y+1, x] - heatmap[y-1, x])
```

Dla wariantu DARK lub dopasowania kwadratowego przybliżenie wygląda następująco:

```
dx = -0.5 * (heatmap[y, x+1] - heatmap[y, x-1]) / (heatmap[y, x+1] - 2 * heatmap[y, x] + heatmap[y, x-1] + eps)
```

Dopasowanie kwadratowe jest dokładniejsze dla dobrze ukształtowanych map ciepła z wyraźnym pikiem, natomiast przesunięcie oparte na znaku (`sign`) jest bardziej odporne na zaszumienie.

3. **Korekta pozycji**: dodanie wyznaczonego przesunięcia do współrzędnych całkowitych piku.
4. **Próg ufności (Confidence)**: pobranie maksymalnej wartości prawdopodobieństwa (szczytu) dla każdego punktu. Pozwala to na późniejsze odrzucenie detekcji o niskiej pewności.
5. **Obsługa brzegów (Edge Cases)**: jeśli piksel o maksymalnej wartości znajduje się na samej krawędzi obrazu, sąsiedni piksel byłby poza zakresem. W takich przypadkach przesunięcie jest zerowane, co stanowi najbezpieczniejsze zachowanie awaryjne (fallback).

## Szablon kodu

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

## Format raportu

```
[subpixel decode]
  keypoints:   K
  threshold:   <float>
  valid_rate:  ułamek punktów kluczowych powyżej progu
```

## Zasady i dobre praktyki

- Zawsze przycinaj (clampuj) indeksy sąsiadów do poprawnego zakresu wymiarów obrazu, aby zapobiec błędom wyjścia poza zakres indeksowania.
- Zawsze zwracaj stopień ufności (confidence) wraz ze współrzędnymi, aby umożliwić odrzucenie punktów o słabej jakości.
- Korekta subpikselowa przynosi efekty tylko wtedy, gdy mapa ciepła jest gładka w sąsiedztwie maksimum. Upewnij się, że w procesie uczenia jako etykiety referencyjnej użyto rozkładu Gaussa z parametrem `sigma >= 1`.
- Jeżeli rozdzielczość mapy ciepła jest bardzo niska (np. < 48x48), warto przeskalować ją w górę (upsample) do rozmiaru obrazu wejściowego przed ekstrakcją współrzędnych, gdyż krok dyskretyzacji bezpośrednio wpływa na precyzję przesunięcia.
