---

name: skill-point-cloud-loader
description: Generowanie klasy PyTorch Dataset do wczytywania i normalizacji plików chmur punktów (.ply, .pcd, .xyz) wraz z centrowaniem i próbkowaniem przestrzennym
version: 1.0.0
phase: 4
lesson: 13
tags: [3d-vision, point-cloud, data-loading, pytorch]

---

# Generator modułu ładującego chmury punktów (Point Cloud Loader)

Przekształca folder zawierający pliki skanów 3D w gotową do uczenia klasę PyTorch `Dataset`.

## Zastosowanie

- Rozpoczynanie nowych projektów z zakresu klasyfikacji lub segmentacji chmur punktów.
- Konfiguracja wczytywania dla różnych formatów plików: `.ply`, `.pcd` oraz `.xyz`.
- Diagnozowanie problemów ze słabą zbieżnością modelu (gdy trening przebiega bez błędów kodu, lecz dokładność nie rośnie – częstym powodem jest nieprawidłowa normalizacja danych).

## Dane wejściowe

- `data_root`: ścieżka do folderu z plikami chmur punktów (oraz opcjonalnym plikiem CSV zawierającym etykiety klas).
- `file_format`: format plików: `ply` | `pcd` | `xyz` | `auto` (automatyczna detekcja)
- `num_points`: docelowa stała liczba punktów w próbce, zazwyczaj 1024 lub 2048.
- `augmentation`: brak (`none`) | rotacja (`rotate`) | szum/drżenie (`jitter`) | tasowanie kolejności (`shuffle`).

## Procedura przygotowania danych

W produkcyjnych potokach przetwarzania chmur punktów operacje są wykonywane w następującej kolejności:

1. **Centrowanie**: odejmij średnią pozycję (środek ciężkości chmury) od współrzędnych wszystkich punktów.
2. **Skalowanie**: znormalizuj wartości do kuli jednostkowej, dzieląc współrzędne przez maksymalną odległość punktu od środka.
3. **Próbkowanie** do docelowej liczby `num_points` punktów. Jeśli chmura wejściowa jest większa, zastosuj **próbkowanie najdalszych punktów (Farthest Point Sampling – FPS)** dla wiernego zachowania geometrii obiektu, bądź szybkie próbkowanie losowe. Jeśli chmura jest mniejsza, powiel punkty (oversampling).
4. **Tasowanie**: wymieszaj kolejność punktów w tensorze (kolejność punktów nie powinna mieć znaczenia dla modelu, a tasowanie eliminuje przypadkowe zależności strukturalne, np. wynikające z powielania klatek/punktów).

## Szablon kodu (PyTorch)

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
    # Fallback: minimalny czytnik ascii-ply
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
        # Przetasuj punkty, aby wyeliminować przypadkowe zależności (szczególnie
        # ważne, gdy powielanie punktów zachodziło w kolejności deterministycznej).
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

## Format raportu

```
[dataset]
  files:          <N>
  format:         <ply|pcd|xyz|npy>
  points_per_sample: <int>
  normalise:      centre + unit sphere
  sampling:       FPS | random
  augmentation:   <list>
```

## Reguły

- Zawsze wykonuj centrowanie przed skalowaniem; odwrócenie tej kolejności całkowicie wypacza definicję „kuli jednostkowej”.
- W zadaniach klasyfikacji kształtów (np. rozpoznawanie obiektów) preferuj próbkowanie FPS; w przypadku segmentacji punktowej próbkowanie losowe jest zazwyczaj wystarczające.
- Nigdy nie stosuj augmentacji danych na etapie ewaluacji/testowania – wyłącznie podczas uczenia.
- Jeżeli pliki chmur punktów zawierają dodatkowe kanały (np. kolory RGB, wektory normalne), rozszerz klasę Dataset, tak aby zwracał tensor `(3 + C, num_points)`, gdzie C oznacza liczbę dodatkowych kanałów.
