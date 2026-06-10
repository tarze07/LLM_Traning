---

name: skill-mot-evaluator
description: Napisz kompletną wiązkę ewaluacyjną dla MOTA/IDF1/HOTA względem torów naziemnych
version: 1.0.0
phase: 4
lesson: 27
tags: [mot, evaluation, tracking, metrics]

---

# Oceniający MOT

Zapakuj dane wyjściowe modułu śledzącego w standardowy potok MOTA/IDF1/HOTA, aby móc rzetelnie porównać je z literaturą.

## Kiedy używać

- Test porównawczy nowego trackera na MOT17 / MOT20 / DanceTrack / SportsMOT.
- Porównanie ByteTrack z BoT-SORT i SAM 2 na własnym materiale filmowym.
- Wyprodukowanie powtarzalnego numeru artykułu lub opisu PR.

## Wejścia

- `predictions`: lista krotek `(track_id, x, y, w, h, confidence)` w ramce.
- `ground_truth`: lista krotek `(gt_id, x, y, w, h)` w ramce.
- `iou_threshold`: 0,5 typowo dla MOTA; HOTA używa przeciągnięcia.
- `evaluator`: `py-motmetrics` (MOTA, IDF1) lub `TrackEval` (HOTA).

## Umowa formatu wyjściowego

Zarówno `py-motmetrics`, jak i `TrackEval` oczekują określonego formatu na dysku:

```
# predictions.txt
<frame>,<track_id>,<x>,<y>,<w>,<h>,<confidence>,-1,-1,-1

# ground_truth.txt
<frame>,<gt_id>,<x>,<y>,<w>,<h>,1,-1,-1,-1
```

Ramki są indeksowane 1, ramki są (x, y, w, h), a nie (x1, y1, x2, y2). W konwersji występuje większość błędów integracji.

## Kroki

1. Konwertuj dane wyjściowe trackera na format tekstowy MOT Challenge.
2. Uruchom `py-motmetrics.io.loadtxt` na obu plikach.
3. Oblicz MOTA + IDF1 za pomocą `mm.metrics.create().compute()`.
4. W przypadku HOTA wywołaj `TrackEval` z tymi samymi plikami i `Metrics: HOTA`.
5. Zapisz wyniki w formacie JSON dla dashboardów.

## Szkic wdrożenia

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

## Zgłoś

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

## Zasady

- Zawsze używaj ramek z indeksem 1 w wyjściowym pliku tekstowym; Oprzyrządowanie MOT tego oczekuje.
- Konwertuj (x1, y1, x2, y2) na (x, y, w, h) przed zapisaniem.
- Nie zgłaszaj samego MOTA do współczesnych porównań; obejmują IDF1 i HOTA.
- Uważaj na wykrycia prywatne i publiczne w MOT17 — są one oceniane osobno, a ich mieszanie zawyża wyniki.
- Rejestruj wyniki według sekwencji; agregat ukrywa awarie pojedynczych trudnych sekwencji.