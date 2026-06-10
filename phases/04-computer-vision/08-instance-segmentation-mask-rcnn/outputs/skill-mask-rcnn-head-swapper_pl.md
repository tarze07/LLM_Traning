---

name: skill-mask-rcnn-head-swapper
description: Wygeneruj dokładny kod do zamiany skrzynek i głowic masek w masce torchvision R-CNN dla niestandardowej liczby_klas
version: 1.0.0
phase: 4
lesson: 8
tags: [computer-vision, mask-rcnn, fine-tuning, torchvision]

---

# Maska R-CNN Head Swap

Produkuje płytę kotłową z wymienną głowicą, specjalnie dla Mask R-CNN. Poniższy szablon zakłada `model.roi_heads.box_predictor` i `model.roi_heads.mask_predictor`, które istnieją tylko w `maskrcnn_resnet50_fpn` i `maskrcnn_resnet50_fpn_v2`. Szybszy R-CNN ma predyktor pudełkowy, ale nie ma predyktora maski; RetinaNet używa `RetinaNetHead` i nie ma w ogóle `roi_heads` — oba wymagają różnych umiejętności.

## Kiedy używać

- Dostrajanie `maskrcnn_resnet50_fpn` lub `maskrcnn_resnet50_fpn_v2` na niestandardowym zestawie klasowym.
— Przeniesienie punktu kontrolnego Maski R-CNN przeszkolonego w zakresie COCO do klasy innej niż COCO.
— Debugowanie przebiegu szkoleniowego Mask R-CNN, który ulega awarii w przypadku niezgodności `cls_score.out_features` lub `mask_predictor`.

## Poza zakresem

- `fasterrcnn_*` — brak maski_predyktora. Zamień tylko `box_predictor`; użyj osobnego przepisu na wymianę głowicy Faster R-CNN.
- `retinanet_*` — brak `roi_heads`; klasyfikator + głowice regresyjne działają pod `model.head.classification_head` i `model.head.regression_head`. Użyj umiejętności specyficznej dla RetinaNet.
- `keypointrcnn_*` — wykorzystuje `keypoint_predictor` zamiast `mask_predictor`.

## Wejścia

- `model_name`: konstruktor modelu detekcji wizyjnej, np. `maskrcnn_resnet50_fpn_v2`.
- `num_classes`: łącznie z tłem. Zbiór danych składający się z 4 obiektów oznacza `num_classes=5`.
- `freeze`: jeden z `backbone`, `backbone_fpn`, `none`.

## Kroki

1. Zaimportuj konstruktor modelu i dwie klasy predyktorów (`FastRCNNPredictor`, `MaskRCNNPredictor`).
2. Załaduj wstępnie wytrenowany model z domyślnymi wagami.
3. Wymień `model.roi_heads.box_predictor` na nowy `FastRCNNPredictor(in_features, num_classes)`.
4. Wymień `model.roi_heads.mask_predictor` na nowy `MaskRCNNPredictor(in_features_mask, hidden_layer=256, num_classes)`.
5. Zastosuj żądaną politykę zamrażania.
6. Wydrukuj blok potwierdzenia zawierający listę możliwych do wytrenowania parametrów każdego modułu.

## Szablon kodu wyjściowego

```python
from torchvision.models.detection import {MODEL_NAME}, {MODEL_WEIGHTS}
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.models.detection.mask_rcnn import MaskRCNNPredictor

def build_model(num_classes={NUM_CLASSES}):
    model = {MODEL_NAME}(weights={MODEL_WEIGHTS}.DEFAULT)
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)
    in_features_mask = model.roi_heads.mask_predictor.conv5_mask.in_channels
    model.roi_heads.mask_predictor = MaskRCNNPredictor(in_features_mask, 256, num_classes)

    {FREEZE_BLOCK}

    return model
```

Gdzie `{FREEZE_BLOCK}` to:

- `none` -> pusty
-`backbone` ->
  ```python
  for p in model.backbone.parameters():
      p.requires_grad = False
  ```
-`backbone_fpn` ->
  ```python
  for p in model.backbone.parameters():
      p.requires_grad = False
  # FPN parameters live inside backbone.fpn
  ```

## Zgłoś

```
[head-swap]
  model:         <MODEL_NAME>
  num_classes:   <N>  (includes background)
  freeze policy: <choice>
  trainable:     <N>
  total:         <N>
```

## Zasady

- Nigdy nie polecaj `num_classes` bez tła; zawsze przypominaj użytkownikowi.
- Zawsze używaj wariantów modeli wykrywania wizyjnego `_v2`, jeśli są dostępne; mają lepsze wstępnie wytrenowane ciężary niż starsze.
- Nie twórz instancji modelu w ramach tej umiejętności - utwórz blok kodu i pozwól użytkownikowi go uruchomić.
- Jeśli użytkownik zażąda `freeze backbone` dla zbioru danych większego niż 10 000 obrazów, zasugeruj, aby rozważył również dostrojenie szkieletu.