---

name: skill-3dgs-export-router
description: Dobór optymalnego formatu eksportu 3DGS (.ply / .splat / glTF / USD) w zależności od docelowego silnika i platformy
version: 1.0.0
phase: 4
lesson: 22
tags: [3d-gaussian-splatting, export, glTF, OpenUSD, pipeline]

---

# Dobór formatu eksportu 3DGS (Export Router)

Dopasuj format pliku wyjściowego 3DGS do docelowego środowiska uruchomieniowego. Pozwala to zaoszczędzić czas tracony na debugowanie błędów wczytywania.

## Zastosowanie

- Po zakończeniu treningu sceny 3DGS, przed przekazaniem jej do dalszych etapów produkcji.
- Podejmowanie decyzji o wyborze formatu badawczego (.ply) lub produkcyjnego (glTF / USD).
- Przekazywanie danych w potoku produkcyjnym: zespół akwizycji -> inżynier 3DGS -> projektant gier / artysta VFX / programista webowy.

## Dane wejściowe

- `target_engine`: `unreal` | `unity` | `omniverse` | `blender` | `vision_pro` | `three_js` | `babylon_js` | `cesium` | `playcanvas` | `supersplat`
- `priority`: `przenosnosc` | `rozmiar_pliku` | `zachowanie_jakosci`
- `include_sh_degree`: `0` | `1` | `2` | `3`

## Zasady doboru formatu

| Docelowe środowisko | Rekomendowany format | Uzasadnienie |
|--------|------|-----|
| Unreal Engine | Wtyczka Volinga lub import glTF `KHR_gaussian_splatting` | Zapewnia natywny potok SDK dla Unreal Engine |
| Unity | Format `.ply` w połączeniu z wtyczką Aras-P (Unity-GaussianSplatting) | Najpopularniejsza integracja społeczności dla silnika Unity |
| NVIDIA Omniverse / Pixar | OpenUSD (schemat `UsdVolParticleField3DGaussianSplat`) | Dedykowany, natywny standard w ekosystemie USD |
| Apple Vision Pro | OpenUSD | W pełni wspierany natywnie w systemie visionOS 2.x |
| Blender | Format `.ply` wraz z dodatkiem KIRI | Najpopularniejszy dodatek społeczności obsługujący surowe chmury punktów Gaussa |
| Przeglądarka internetowa (Three.js) | glTF `KHR_gaussian_splatting` lub `.splat` | Standardy sieciowe kompatybilne z biblioteką `GaussianSplats3D` |
| Babylon.js V9+ | glTF `KHR_gaussian_splatting` | Wbudowane wsparcie od wersji V9 |
| CesiumJS (1.139+ lub Cesium dla Unreal 2.23+) | glTF `KHR_gaussian_splatting` | Wprowadzono pełną natywną obsługę |
| PlayCanvas | Format `.splat` | Oficjalny, skwantyzowany format silnika PlayCanvas |
| SuperSplat (edytor) | `.ply` lub `.splat` | Obsługa bezpośredniego importu oraz eksportu |

## Kompromisy i poziomy kompresji

- **Pełna precyzja (`.ply`)**: największy rozmiar pliku, bezstratny zapis, wysoka kompatybilność z edytorami.
- **Format `.splat`**: plik o 4x-8x mniejszej objętości, minimalny spadek wierności odwzorowania harmonik sferycznych SH3, standard w środowisku PlayCanvas.
- **Format glTF z rozszerzeniem KHR**: wysoce konfigurowalny przy użyciu kompresji `EXT_meshopt_compression`; optymalne połączenie rozmiaru pliku i szerokiej kompatybilności.
- **Format OpenUSD**: kompresowany do kontenera `.usdz`; dedykowany i zoptymalizowany dla ekosystemu Apple.

## Format raportu

```
[export plan]
  target:         <engine>
  format:         <name>
  sh degree:      <0|1|2|3>
  compression:    <none|meshopt|quantisation|usdz>
  expected size:  <MB>
  compatible with: <lista przeglądarek>

[pipeline]
  1. source: <plik wejściowy .ply ze szkolenia>
  2. optional: oczyszczenie sceny w SuperSplat
  3. convert: <wywołanie konwertera z CLI lub API>
  4. package: <docelowy plik gltf / glb / usd / usdz / splat / ply>
  5. validate: <weryfikacja w przeglądarce>
```

## Zasady i dobre praktyki

- Nie usuwaj bez uprzedzenia współczynników harmonik sferycznych SH3; usunięcie tych danych wyraźnie zniekształca dynamiczne refleksy świetlne sceny.
- Jeżeli priorytetem jest najmniejsza objętość danych (`priority == rozmiar_pliku`), zalecaj użycie formatu `.splat` lub glTF z kompresją meshopt i uprzedź zespół o możliwym spadku precyzji.
- Dla systemów firmy Apple (visionOS) bezwzględnie wybieraj OpenUSD / `.usdz` zamiast glTF; format USDZ oferuje pełną, natywną wydajność w ekosystemie Vision Pro.
- Jeśli docelowe narzędzia do wizualizacji bazują na starszych implementacjach sprzed ratyfikacji oficjalnego rozszerzenia glTF Khronos (początek 2026 roku), najbezpieczniejszym wyborem jest format `.ply` w połączeniu z dedykowanym loaderem, ponieważ standardowy parser glTF nie rozpozna jeszcze nowej struktury danych.
- Przed przekazaniem zawsze sprawdź wyeksportowany plik w co najmniej jednej przeglądarce; ciche uszkodzenie następuje podczas kwantyzacji.
