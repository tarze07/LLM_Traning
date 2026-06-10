---

name: skill-mask-rcnn-head-swapper
description: Generuje dokładny kod PyTorch do podmiany głowic klasyfikacji i masek w modelu Mask R-CNN z biblioteki torchvision dla niestandardowej liczby klas
version: 1.0.0
phase: 4
lesson: 8
tags: [computer-vision, mask-rcnn, fine-tuning, torchvision]

---

# Podmiana głowic w Mask R-CNN

Generuje gotowy szablon kodu (boilerplate) służący do modyfikacji i podmiany głowic predykcyjnych w architekturze Mask R-CNN. Poniższa procedura odwołuje się bezpośrednio do atrybutów `model.roi_heads.box_predictor` oraz `model.roi_heads.mask_predictor`, które występują wyłącznie w modelach `maskrcnn_resnet50_fpn` oraz `maskrcnn_resnet50_fpn_v2`. Modele Faster R-CNN posiadają wyłącznie predyktor ramek (box predictor), natomiast nie posiadają predyktora masek. Z kolei modele RetinaNet wykorzystują strukturę `RetinaNetHead` i nie mają w ogóle modułu `roi_heads` – modyfikacja głowic w tych modelach wymaga innych rozwiązań.

## Zastosowanie

- Dostrajanie (fine-tuning) modeli `maskrcnn_resnet50_fpn` lub `maskrcnn_resnet50_fpn_v2` dla własnego zestawu klas.
- Przenoszenie wag (checkpoints) modelu Mask R-CNN pre-trenowanego na zbiorze COCO do zadań z niestandardowymi klasami spoza tego zbioru.
- Rozwiązywanie problemów i debugowanie procesu treningowego Mask R-CNN, gdy dochodzi do błędów wymiarów w warstwach `cls_score.out_features` lub `mask_predictor`.

## Wyłączenia (Poza zakresem)

- `fasterrcnn_*` – brak predyktora maski. W tych modelach podmienia się wyłącznie `box_predictor` (użyj dedykowanej procedury dla Faster R-CNN).
- `retinanet_*` – brak modułu `roi_heads`. Głowice klasyfikacji i regresji ramek znajdują się pod atrybutami `model.head.classification_head` oraz `model.head.regression_head` (użyj dedykowanej instrukcji dla RetinaNet).
- `keypointrcnn_*` – modele te wykorzystują `keypoint_predictor` zamiast `mask_predictor`.

## Dane wejściowe (Inputs)

- `model_name`: konstruktor modelu detekcji obiektów, np. `maskrcnn_resnet50_fpn_v2`.
- `num_classes`: łączna liczba klas wraz z klasą tła (np. 4 wykrywane obiekty oznaczają `num_classes=5`).
- `freeze`: wybrane warstwy do zamrożenia (`backbone`, `backbone_fpn` lub `none`).

## Procedura krok po kroku

1. Zaimportuj konstruktor modelu oraz wymagane klasy predyktorów (`FastRCNNPredictor` i `MaskRCNNPredictor`).
2. Załaduj pre-trenowany model z domyślnymi wagami ImageNet.
3. Zastąp `model.roi_heads.box_predictor` nową instancją `FastRCNNPredictor(in_features, num_classes)`.
4. Zastąp `model.roi_heads.mask_predictor` nową instancją `MaskRCNNPredictor(in_features_mask, hidden_layer=256, num_classes)`.
5. Zastosuj wybraną strategię zamrażania wag.
6. Wyświetl podsumowanie z liczbą trenowalnych parametrów dla każdego podmodułu.

## Generowany szablon kodu

```python
from torchvision.models.detection import {MODEL_NAME}, {MODEL_WEIGHTS}
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.models.detection.mask_rcnn import MaskRCNNPredictor

def build_model(num_classes={NUM_CLASSES}):
    model = {MODEL_NAME}(weights={MODEL_WEIGHTS}.DEFAULT)
    
    # Podmiana głowicy klasyfikacji i regresji ramek
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)
    
    # Podmiana głowicy masek
    in_features_mask = model.roi_heads.mask_predictor.conv5_mask.in_channels
    model.roi_heads.mask_predictor = MaskRCNNPredictor(in_features_mask, 256, num_classes)

    {FREEZE_BLOCK}

    return model
```

Gdzie `{FREEZE_BLOCK}` w zależności od wyboru przyjmuje postać:

- `none` -> brak kodu (cały model trenowalny)
- `backbone` ->
  ```python
  for p in model.backbone.parameters():
      p.requires_grad = False
  ```
- `backbone_fpn` ->
  ```python
  for p in model.backbone.parameters():
      p.requires_grad = False
  # Parametry FPN również zostają zamrożone, ponieważ znajdują się wewnątrz backbone.fpn
  ```

## Format raportu (Report Format)

```
[head-swap]
  model:         <MODEL_NAME>
  num_classes:   <N> (wliczając tło)
  freeze policy: <none | backbone | backbone_fpn>
  trainable:     <liczba trenowalnych parametrów>
  total:         <całkowita liczba parametrów>
```

## Zasady i wskazówki

- Nigdy nie definiuj `num_classes` z pominięciem tła – zawsze przypominaj o konieczności uwzględnienia tła (indeks 0).
- Zawsze sugeruj użycie nowszych wersji modeli z oznaczeniem `_v2` (np. `maskrcnn_resnet50_fpn_v2`), ponieważ posiadają one znacznie lepsze pre-trenowane wagi niż wersje pierwotne.
- Nie uruchamiaj kodu i nie twórz instancji modelu bezpośrednio w tym narzędziu – wygeneruj kompletny szablon kodu do uruchomienia przez użytkownika.
- Jeśli użytkownik żąda zamrożenia modelu bazowego (`freeze backbone`) przy zbiorze danych większym niż 10 000 obrazów, zasugeruj pełne dostrajanie (fine-tuning) całego modelu, w tym wag kodera.
