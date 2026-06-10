---

name: skill-point-cloud-loader
description: Napisz zestaw danych PyTorch dla plików .ply / .pcd / .xyz z prawidłową normalizacją, centrowaniem i próbkowaniem punktowym
version: 1.0.0
phase: 4
lesson: 13
tags: [3d-vision, point-cloud, data-loading, pytorch]

---

# Program ładujący chmury punktów

Zmień folder plików skanowania 3D w gotowy do szkolenia plik PyTorch `Dataset`.

## Kiedy używać

- Rozpoczęcie nowego projektu klasyfikacji/segmentacji chmur punktów.
- Przełączanie między formatami `.ply`, `.pcd` i `.xyz`.
- Debugowanie modelu, który trenuje bez błędów, ale słabo zbiega się; często normalizacja modułu ładującego dane jest błędna.

## Wejścia

- `data_root`: folder plików chmury punktów i opcjonalny plik CSV z etykietami.
- `file_format`: warstwa | szt | xyz | nie wiem.
- `num_points`: stała wielkość próbkowania, zazwyczaj 1024 lub 2048.
- `augmentation`: brak | obrócić | drżenie | pomieszanie.

## Polityka normalizacji

Każdy potok produkcyjnej chmury punktów ma zastosowanie w następującej kolejności:

1. **Wyśrodkuj** chmurę: odejmij środek ciężkości.
2. **Skala** do kuli jednostkowej: podziel przez maksymalną odległość od środka.
3. **Przykład** punktów `num_points`. Jeśli chmura jest większa, użyj **próbkowania z najdalszego punktu** (FPS), aby uzyskać wierne odwzorowanie kształtu, lub próbkowania losowego ze względu na szybkość. Jeśli jest ich mniej, powtórz punkty.
4. **Przetasuj** kolejność punktów (kolejność i tak nie powinna mieć znaczenia dla modelu, ale przetasowanie przerywa przypadkowe zależności kolejności).

## Szablon wyjściowy

```python
import numpy as np
import torch
from torch.utils.data import Dataset

try:
    import open3d as o3d
    HAS_O3D = True
except ImportError:
    HAS_O3D = False

def _read_ply(path):
    if HAS_O3D:
        pc = o3d.io.read_point_cloud(path)
        return np.asarray(pc.points, dtype=np.float32)
    # Fallback: minimal ascii-ply reader
    ...

def _fps(points, k):
    idx = np.zeros(k, dtype=np.int64)
    dist = np.full(len(points), np.inf)
    seed = np.random.randint(len(points))
    idx[0] = seed
    for i in range(1, k):
        dist = np.minimum(dist, ((points - points[idx[i-1]]) ** 2).sum(axis=1))
        idx[i] = int(np.argmax(dist))
    return idx

def normalise(points):
    centre = points.mean(axis=0)
    points = points - centre
    scale = np.max(np.linalg.norm(points, axis=1))
    return points / max(scale, 1e-8)

class PointCloudDataset(Dataset):
    def __init__(self, files, labels, num_points=1024, augment=False):
        self.files = files
        self.labels = labels
        self.num_points = num_points
        self.augment = augment

    def __len__(self):
        return len(self.files)

    def __getitem__(self, i):
        pts = _read_ply(self.files[i])
        pts = normalise(pts)
        if len(pts) >= self.num_points:
            idx = _fps(pts, self.num_points)
            pts = pts[idx]
        else:
            reps = int(np.ceil(self.num_points / len(pts)))
            pts = np.tile(pts, (reps, 1))[:self.num_points]
        # Shuffle point order to break any accidental dependencies (especially
        # important when tiling repeats points in deterministic order).
        np.random.shuffle(pts)
        if self.augment:
            theta = np.random.uniform(0, 2 * np.pi)
            R = np.array([[np.cos(theta), 0, np.sin(theta)],
                          [0, 1, 0],
                          [-np.sin(theta), 0, np.cos(theta)]], dtype=np.float32)
            pts = pts @ R
            pts = pts + np.random.normal(0, 0.02, pts.shape).astype(np.float32)
        pts = np.ascontiguousarray(pts, dtype=np.float32)
        return torch.from_numpy(pts).transpose(0, 1), int(self.labels[i])
```

## Zgłoś

```
[dataset]
  files:          <N>
  format:         <ply|pcd|xyz|npy>
  points_per_sample: <int>
  normalise:      centre + unit sphere
  sampling:       FPS | random
  augmentation:   <list>
```

## Zasady

- Zawsze wyśrodkuj przed skalowaniem; zamiana kolejności zmienia znaczenie „sfery jednostkowej”.
- Preferuj FPS zamiast losowego próbkowania w przypadku zadań związanych z kształtami; random jest w porządku w przypadku segmentacji, w której każdy punkt i tak ma znaczenie.
- Nigdy nie wzmacniaj podczas oceny; tylko podczas treningu.
- Jeśli pliki chmur punktów zawierają kolory lub normalne jako dodatkowe kanały, rozszerz zestaw danych, aby zwracał tensor `(3 + C, num_points)`, a nie tylko xyz.