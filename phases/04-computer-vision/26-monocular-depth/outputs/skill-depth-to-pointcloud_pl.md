---

name: skill-depth-to-pointcloud
description: Twórz chmury punktów na podstawie map głębokości z prawidłową obsługą elementów wewnętrznych i eksportem do pliku .ply
version: 1.0.0
phase: 4
lesson: 26
tags: [depth, point-cloud, 3d, intrinsics]

---

# Głębokość do chmury punktów

Zamień mapę głębi wraz z kolorowym obrazem w teksturowaną chmurę punktów, którą można wyeksportować do wizualizacji lub dalszej pracy 3D.

## Kiedy używać

- Wizualizacja przewidywań głębokości jako rzeczywistej sceny 3D.
- Bootstrapowanie rzadkiej rekonstrukcji 3D z pojedynczego obrazu.
- Tworzenie danych wejściowych do szkolenia 3DGS w przypadku niepowodzenia SfM.
- Porównanie przewidywanej głębokości z prawdą naziemną LiDAR.

## Wejścia

- `depth`: `(H, W)` numpy tablica głębokości w tych samych jednostkach, które chcesz uzyskać na wyjściu (zalecane metry).
- `rgb`: `(H, W, 3)` numpy tablica kolorów (uint8 lub float32 [0, 1]).
- `intrinsics`: `(fx, fy, cx, cy)` w jednostkach pikseli.
- Opcjonalnie `depth_scale`: mnożnik do konwersji przewidywanych jednostek głębokości na metry.

## Rurociąg

1. **Sprawdź** — głębokość musi być dodatnia i skończona wszędzie tam, gdzie planujesz uwzględnić. Zamaskuj nieprawidłowe piksele.
2. **Podniesienie** — `X = (u - cx) * d / fx`, `Y = (v - cy) * d / fy`, `Z = d` na piksel.
3. **Sparuj** z RGB — każdy punkt 3D otrzymuje potrójną wartość `(r, g, b)` z pasującego piksela.
4. **Eksport** — PLY (przenośny), `.xyz` (lekki), `.pcd` (natywny Open3D), `.las`/`.laz` (geoprzestrzenny).

## Szablon implementacji

```python
import numpy as np

def depth_to_point_cloud(depth, intrinsics, depth_scale=1.0, min_depth=0.1, max_depth=100.0):
    H, W = depth.shape
    fx, fy, cx, cy = intrinsics
    v, u = np.meshgrid(np.arange(H), np.arange(W), indexing="ij")
    z = depth.astype(np.float32) * depth_scale
    valid = (z > min_depth) & (z < max_depth) & np.isfinite(z)
    x = (u - cx) * z / fx
    y = (v - cy) * z / fy
    points = np.stack([x, y, z], axis=-1)
    return points, valid


def write_ply(path, points, colors=None, valid_mask=None):
    p = points.reshape(-1, 3)
    if valid_mask is not None:
        p = p[valid_mask.flatten()]
    lines = [
        "ply",
        "format ascii 1.0",
        f"element vertex {p.shape[0]}",
        "property float x", "property float y", "property float z",
    ]
    if colors is not None:
        c = colors.reshape(-1, 3).astype(np.uint8)
        if valid_mask is not None:
            c = c[valid_mask.flatten()]
        lines += ["property uchar red", "property uchar green", "property uchar blue"]
    lines.append("end_header")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
        if colors is not None:
            for pt, col in zip(p, c):
                f.write(f"{pt[0]:.4f} {pt[1]:.4f} {pt[2]:.4f} {col[0]} {col[1]} {col[2]}\n")
        else:
            for pt in p:
                f.write(f"{pt[0]:.4f} {pt[1]:.4f} {pt[2]:.4f}\n")
```

## Zgłoś

```
[export]
  input depth shape:  (H, W)
  valid points:       <N> of <H*W>
  output format:      ply | xyz | pcd | las
  coordinate system:  camera (+X right, +Y down, +Z forward)
  scale:              metres | millimetres | normalised
```

## Zasady

- Zawsze maskuj nieprawidłową głębokość (zero, NaN, inf, nasycone); włączenie ich powoduje powstanie chmury punktów śmieciowych w miejscu pochodzenia.
- W przypadku przewidywania na podstawie modelu względnej głębokości NIE eksportuj jako metryki; przedrostek nazwy pliku wyjściowego za pomocą `relative_`, aby zasygnalizować konwencję.
- Zachowaj spójność konwencji współrzędnych kamery (OpenCV: +X w prawo, +Y w dół, +Z w przód). Zamień znaki, jeśli dalsze narzędzie oczekuje OpenGL (+Y w górę).
- W przypadku gęstych scen (> 1 mln punktów) zaoferuj parametr podpróbki; Pliki PLY > 500 MB są niewygodne do załadowania wszędzie.
- Nigdy po cichu nie przycinaj głębi, aby uzyskać „rozsądny” wynik; klip wyraźnie z ostrzeżonymi progami, aby użytkownicy wiedzieli, co zostało odrzucone.