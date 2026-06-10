---

name: skill-segmentation-mask-inspector
description: Raportuj rozkład klas, statystyki maski przewidywanej i klasy, które najprawdopodobniej będą niedoszacowane lub zamazane
version: 1.0.0
phase: 4
lesson: 7
tags: [computer-vision, segmentation, debugging, evaluation]

---

# Inspektor maski segmentacji

Diagnoza luki między „utrata spadła” a „maski rzeczywiście wyglądają dobrze”.

## Kiedy używać

- Zaraz po treningu, gdy mIoU wygląda dobrze, ale oględziny mówią co innego.
- Przed wdrożeniem: sprawdzenie równowagi klas przewidywań w stosunku do podstawowej prawdy.
- Gdy IoU na klasę jest wysokie w przypadku dużych obiektów, ale niskie w przypadku małych.
- Debugowanie artefaktów granicznych, które nie pojawiają się w IoU, ponieważ mają małą liczbę pikseli.

## Wejścia

- `preds`: (N, H, W) tensor przewidywanych identyfikatorów klas.
- `targets`: (N, H, W) tensor identyfikatorów klas prawdy ziemskiej.
- `num_classes`: liczba całkowita.
- Opcjonalnie `class_names`: lista ciągów C.

## Kroki

1. **Histogramy pikseli klas.** Oblicz procent pikseli na klasę dla `preds` i `targets`. Oznacz dowolną klasę, w której `|pred% - gt%| / max(gt%, 1e-6) > 0.30` (odchylenie względne powyżej 30%). W przypadku klas nie związanych z podstawową prawdą (`gt% == 0`) oznacz bezpośrednio dowolny przewidywany udział powyżej `0.3`.

2. **IoU na klasę** i **granica F1 na klasę**. Granicę F1 oblicza się poprzez rozszerzenie każdej maski o 3 piksele, przecięcie i punktację. Klasy z IoU > 0,7, ale granica F1 < 0.5 are blurring edges.

3. **Small-object recall.** Separate every ground-truth connected component into size buckets (tiny < 100 px, small < 1000 px, medium < 10000 px, large >= 10000 px). Raportuj wycofanie dla każdego wiadra dla każdej klasy. Przywołanie małych obiektów poniżej 0,3, podczas gdy przywołanie dużych obiektów powyżej 0,9 wskazuje na problem z rozdzielczością/polem recepcyjnym.

4. **Pary zamieszania.** Dla każdej klasy znajdź klasę, z którą najczęściej się myli (najczęstsza błędnie przewidywana klasa w jej masce prawdy). Zgłoś 3 najlepsze pary.

5. **Sprawdzanie nasycenia (wymaga `probs` lub `logits`, a nie tylko `preds`).** Jeśli obiekt wywołujący przejdzie surowy rozkład prawdopodobieństwa na piksel `probs: (N, C, H, W)`, oblicz ułamek pikseli, w których `probs.max(dim=1) > 0.99` przypada na klasę. Wysokie nasycenie (>0,9 pikseli klasy) sugeruje nadmierną pewność siebie — kandydata do wygładzenia etykiety lub kalibracji. Jeśli dostępne są tylko argmaxed `preds`, pomiń ten krok i zanotuj to w raporcie.

## Format raportu

```
[mask-inspector]
  classes: C

[class distribution]
  name       gt %    pred %   delta
  ...

[metrics]
  class       IoU     bF1    recall_tiny  recall_small  recall_medium  recall_large
  ...

[confusion pairs]
  class A confused with class B: <N> pixels (most common)
  class B confused with class A: <N> pixels
  ...

[verdict]
  most impactful issue: <one sentence>
```

## Zasady

- Sortuj wiersze klas według malejącego udziału pikseli GT, tak aby najczęstsze klasy były na pierwszym miejscu.
- Klasy flag z IoU < 0,4 lub granicą F1 < 0,3 jako `critical`.
- Gdy dominującym niepowodzeniem jest przywoływanie małych obiektów, zaleca się: trening o wyższej rozdzielczości, mniejszy krok na ostatnim etapie kodowania lub dekoder piramidy funkcji.
- Gdy granica F1 jest dominującą awarią, zaleca się: utratę świadomości granic (Lovasz lub BoundaryLoss), TTA z przerzuceniem w poziomie i dekoder bez kroku.
- Nigdy nie wyprowadzaj indeksów klas jako jedynego identyfikatora; jeśli zapewniono `class_names`, użyj go w każdym rzędzie.