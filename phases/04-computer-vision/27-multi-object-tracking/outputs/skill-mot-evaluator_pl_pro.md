---

name: skill-mot-evaluator
description: Przygotowanie pełnego skryptu ewaluacyjnego dla metryk MOTA/IDF1/HOTA w odniesieniu do danych referencyjnych (ground truth)
version: 1.0.0
phase: 4
lesson: 27
tags: [mot, evaluation, tracking, metrics]

---

# Ewaluator śledzenia MOT (Multi-Object Tracking Evaluator)

Przetwarzanie danych wyjściowych trackera w ramach standardowego potoku obliczeniowego metryk MOTA/IDF1/HOTA w celu rzetelnego porównania wyników z literaturą naukową.

## Kiedy używać

- Benchmarking nowych trackerów na zbiorach danych takich jak MOT17 / MOT20 / DanceTrack / SportsMOT.
- Porównanie ByteTrack, BoT-SORT i SAM 2 na własnych nagraniach wideo.
- Generowanie powtarzalnych metryk do publikacji naukowych lub opisów w Pull Requestach (PR).

## Dane wejściowe

- `predictions`: lista krotek `(track_id, x, y, w, h, confidence)` dla każdej klatki.
- `ground_truth`: lista krotek `(gt_id, x, y, w, h)` dla każdej klatki.
- `iou_threshold`: próg IoU (zazwyczaj 0.5 dla MOTA; HOTA oblicza całkę po wielu progach).
- `evaluator`: biblioteka `py-motmetrics` (dla MOTA, IDF1) lub `TrackEval` (dla HOTA).

## Specyfikacja formatu danych

Zarówno `py-motmetrics`, jak i `TrackEval` wymagają zapisu danych na dysku w określonym formacie:

```
# predictions.txt
<frame>,<track_id>,<x>,<y>,<w>,<h>,<confidence>,-1,-1,-1

# ground_truth.txt
<frame>,<gt_id>,<x>,<y>,<w>,<h>,1,-1,-1,-1
```

Indeksowanie klatek rozpoczyna się od 1, a współrzędne ramek otaczających mają format `(x, y, w, h)` (lewy górny róg, szerokość, wysokość), a nie `(x1, y1, x2, y2)`. Błędna konwersja współrzędnych jest najczęstszą przyczyną błędów integracji.

## Procedura (Krok po kroku)

1. Skonwertuj wyniki działania trackera na format tekstowy MOT Challenge.
2. Wczytaj pliki przy użyciu `mm.io.loadtxt`.
3. Oblicz metryki MOTA i IDF1 za pomocą `mm.metrics.create().compute()`.
4. W celu wyliczenia HOTA, uruchom narzędzie `TrackEval` ze wskazaniem tych samych plików i parametru `Metrics: HOTA`.
5. Zapisz wyjściowe metryki do formatu JSON na potrzeby wizualizacji w panelach kontrolnych.

## Przykład implementacji

```python
import motmetrics as mm

def evaluate_mota_idf1(pred_path, gt_path):
    gt = mm.io.loadtxt(gt_path, fmt="mot15-2D")
    pred = mm.io.loadtxt(pred_path, fmt="mot15-2D")
    acc = mm.utils.compare_to_groundtruth(gt, pred, dist="iou", distth=0.5)
    metrics = mm.metrics.create().compute(
        acc, metrics=["num_frames", "mota", "motp", "idf1", "idp", "idr", "num_switches"]
    )
    return metrics


def write_mot_txt(predictions, path):
    with open(path, "w") as f:
        for frame_idx, detections in enumerate(predictions, start=1):
            for tid, x, y, w, h, conf in detections:
                f.write(f"{frame_idx},{tid},{x:.2f},{y:.2f},{w:.2f},{h:.2f},{conf:.3f},-1,-1,-1\n")
```

## Raport (Wyjście)

```
[mot evaluation]
  frames:     <int>
  gt tracks:  <int>
  pred tracks: <int>

[metrics]
  MOTA:       <float>
  MOTP:       <float>
  IDF1:       <float>
  IDP/IDR:    <float/float>
  ID switches: <int>
  HOTA:       <float>  (from TrackEval)
```

## Reguły

- Zawsze rozpoczynaj indeksowanie klatek od 1 w plikach wynikowych — jest to standard oczekiwany przez narzędzia MOT.
- Przed zapisaniem ramek otaczających skonwertuj współrzędne z formatu `(x1, y1, x2, y2)` do `(x, y, w, h)`.
- Nie ograniczaj się do podawania wyłącznie metryki MOTA we współczesnych publikacjach i testach porównawczych; zawsze dołączaj metryki IDF1 oraz HOTA.
- Zwróć szczególną uwagę na rozróżnienie pomiędzy detekcjami prywatnymi (private detections) a publicznymi (public detections) w zbiorze MOT17 — są one ewaluowane oddzielnie, a ich zmieszanie fałszuje końcowy wynik.
- Analizuj i loguj wyniki ososobo dla każdej sekwencji wideo; uśrednione wyniki zbiorcze mogą maskować błędy na trudniejszych ujęciach.
