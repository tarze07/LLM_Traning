---

name: skill-depth-to-pointcloud
description: Tworzenie chmur punktów na podstawie map głębi z poprawnym uwzględnieniem parametrów wewnętrznych kamery (intrinsics) i eksportem do plików .ply
version: 1.0.0
phase: 4
lesson: 26
tags: [depth, point-cloud, 3d, intrinsics]

---

# Konwersja mapy głębi do chmury punktów (Depth to Point Cloud)

Konwersja mapy głębi (depth map) oraz obrazu RGB na teksturowaną chmurę punktów gotową do eksportu, wizualizacji lub dalszego przetwarzania 3D.

## Kiedy używać

- Wizualizacja estymacji głębi w postaci sceny 3D.
- Inicjalizacja (bootstrapping) rzadkiej rekonstrukcji 3D z pojedynczego obrazu.
- Przygotowanie danych wejściowych do trenowania 3DGS (3D Gaussian Splatting) w przypadku niepowodzenia algorytmu SfM (Structure from Motion).
- Porównywanie estymowanej głębi z referencyjnymi danymi LiDAR (ground truth).

## Dane wejściowe

- `depth`: tablica NumPy o kształcie `(H, W)` zawierająca wartości głębi w jednostkach wyjściowych (zalecane są metry).
- `rgb`: tablica NumPy o kształcie `(H, W, 3)` reprezentująca kolory (uint8 lub float32 w zakresie [0, 1]).
- `intrinsics`: parametry wewnętrzne kamery `(fx, fy, cx, cy)` wyrażone w pikselach.
- Opcjonalnie `depth_scale`: współczynnik skalowania (mnożnik) służący do konwersji wartości głębi na metry.

## Krok po kroku (Pipeline)

1. **Weryfikacja** — wartości głębi muszą być dodatnia i skończone w punktach, które mają zostać uwzględnione. Przeprowadź maskowanie nieprawidłowych pikseli.
2. **Rzutowanie wsteczne (Unprojection/Lifting)** — obliczenie współrzędnych 3D dla każdego piksela: `X = (u - cx) * d / fx`, `Y = (v - cy) * d / fy`, `Z = d`.
3. **Mapowanie kolorów RGB** — przypisanie każdemu punktowi 3D wartości `(r, g, b)` z odpowiadającego mu piksela.
4. **Eksport** — zapis do wybranego formatu: PLY (uniwersalny), `.xyz` (prosty tekstowy), `.pcd` (natywny dla Open3D), `.las`/`.laz` (geoprzestrzenne).

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

## Raport (Wyjście)

```
[export]
  input depth shape:  (H, W)
  valid points:       <N> of <H*W>
  output format:      ply | xyz | pcd | las
  coordinate system:  camera (+X right, +Y down, +Z forward)
  scale:              metres | millimetres | normalised
```

## Reguły

- Zawsze maskuj nieprawidłowe wartości głębi (wartości zerowe, ujemne, NaN, inf, nasycone); ich uwzględnienie spowoduje powstanie artefaktów (punktów śmieciowych) w początku układu współrzędnych.
- Jeśli korzystasz z modelu szacującego głębokość względną (relative depth), NIE zapisuj chmury jako metrycznej. Dodaj przedrostek `relative_` do nazwy pliku wyjściowego, aby jasno określić charakter danych.
- Przestrzegaj spójności układu współrzędnych kamery (np. konwencja OpenCV: +X w prawo, +Y w dół, +Z w przód). Odwróć znaki osi, jeśli docelowe oprogramowanie korzysta z konwencji OpenGL (+Y w górę, -Z w przód).
- Dla gęstych scen (> 1 mln punktów) wprowadź opcję downsamplingu (podpróbkowania); pliki PLY o rozmiarze powyżej 500 MB są trudne do wczytania i przetworzenia w większości narzędzi.
- Nigdy nie przycinaj zakresu głębi (clipping) w sposób niejawny w celu uzyskania ładniejszego wyniku; określ jasne progi odcięcia (min_depth/max_depth) i informuj użytkownika o liczbie odrzuconych punktów.
