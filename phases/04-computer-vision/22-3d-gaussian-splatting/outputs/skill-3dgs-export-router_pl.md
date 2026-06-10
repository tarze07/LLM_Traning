---

name: skill-3dgs-export-router
description: Wybierz odpowiedni format eksportu 3DGS (.ply / .splat / glTF KHR_gaussian_splatting / USD), biorąc pod uwagę przeglądarkę lub silnik końcowy
version: 1.0.0
phase: 4
lesson: 22
tags: [3d-gaussian-splatting, export, glTF, OpenUSD, pipeline]

---

# Router eksportowy 3DGS

Zamapuj dalszy cel na odpowiedni format pliku 3DGS. Oszczędza godziny debugowania „nie ładuje się”.

## Kiedy używać

- Po wytrenowaniu sceny 3DGS, przed udostępnieniem jej potokowi treści.
- Wybór pomiędzy formatem badawczym (.ply) i produkcyjnym (glTF / USD).
- Przekazanie rurociągu: zespół przechwytujący -> Inżynier 3DGS -> projektant gry / artysta VFX / twórca stron internetowych.

## Wejścia

- `target_engine`: nierealne | jedność | wszechświat | blender | wizja_pro | trzy_js | babilon_js | cez | płótno | superplat
- `priority`: przenośność | rozmiar_pliku | zachowanie_jakości
- `include_sh_degree`: 0 | 1 | 2 | 3

## Decyzja o formacie

| Cel | Zalecany format | Dlaczego |
|--------|------|-----|
| Unreal Engine (produkcja wirtualna) | Wtyczka Volinga lub glTF KHR_gaussian_splatting | Natywna ścieżka SDK Unreal |
| Unity (XR / gra) | .ply poprzez wtyczkę Aras-P Unity-GaussianSplatting | Rurociąg Unity zgodny ze standardem społeczności |
| NVIDIA Omniverse, narzędzia Pixar | OtwórzUSD 26,03 (UsdVolParticleField3DGaussianSplat) | Natywny typ podstawowy USD |
| Apple Vision Pro | OtwórzUSD 26,03 | Natywny dla systemu VisionOS 2.x |
| Mikser | .ply + dodatek do silnika KIRI | Dodatek społeczności czyta surowe ikony |
| Przeglądarka internetowa Three.js | glTF KHR_gaussian_splatting lub .splat | Standard przeglądarki, współpracuje z `GaussianSplats3D` |
| Babylon.js V9+ | glTF KHR_gaussian_splatting | V9 dodało natywną obsługę |
| Cez (CesiumJS 1.139+, Cez dla Unreal 2.23+) | glTF KHR_gaussian_splatting | Wysłano wyraźne wsparcie |
| OdtwórzPłótno | .plaska | Natywny, skwantyzowany format PlayCanvas |
| SuperSplat (redaktor) | .ply lub .splat | Import + eksport |

## Kompromisy w zakresie kwantyzacji

- Pełna precyzja `.ply`: największy plik, bezstratny, dowolna przeglądarka.
- `.splat`: 4x-8x mniejszy, niewielka utrata jakości na współczynnikach SH3, standard ekosystemu PlayCanvas.
- glTF KHR: konfigurowalny poprzez EXT_meshopt_compression; najmniejszy z najwyższą kompatybilnością.
- USD: skompresowany przez opakowanie USDZ; najmniejszy dla rurociągów Apple.

## Raport wyjściowy

```
[export plan]
  target:         <engine>
  format:         <name>
  sh degree:      <0|1|2|3>
  compression:    <none|meshopt|quantisation|usdz>
  expected size:  <MB>
  compatible with: <list of viewers>

[pipeline]
  1. source: <.ply from training>
  2. optional: SuperSplat cleanup pass
  3. convert: <tool + CLI or API call>
  4. package: <.gltf / .glb / .usd / .usdz / .splat / .ply>
  5. validate: <viewer sanity check>
```

## Zasady

- Nigdy nie usuwaj po cichu współczynników SH3 — w widoczny sposób zmienia to odbicia lustrzane.
- Jeśli `priority == file_size`, polecam `.splat` lub glTF z meshopt; ostrzegaj o utracie jakości.
- W przypadku platform Apple preferuj USD / USDZ zamiast glTF w 2026 r.; USDZ oferuje najwyższej klasy obsługę systemu VisionOS.
- Jeśli obsługa 3DGS docelowej przeglądarki jest wstępnie standardowa (sprzed lutego 2026 r.), polecam `.ply` i niestandardowy moduł ładujący przeglądarki; Standardowy glTF Khronos nie zostanie jeszcze rozpoznany.
- Przed przekazaniem zawsze sprawdź wyeksportowany plik w co najmniej jednej przeglądarce; ciche uszkodzenie następuje podczas kwantyzacji.