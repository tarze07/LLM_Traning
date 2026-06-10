---

name: skill-anchor-designer
description: Biorąc pod uwagę zestaw danych pól prawdy, uruchom k-średnie na (w, h) i zwróć zestawy kotwic na poziom FPN plus statystyki pokrycia
version: 1.0.0
phase: 4
lesson: 6
tags: [computer-vision, detection, anchors, kmeans]

---

# Projektant kotwicy

Kotwice są pojedynczym hiperparametrem najbardziej specyficznym dla zbioru danych w detektorze opartym na kotwicach. Domyślne kotwice COCO słabo sprawdzają się w przypadku obrazów z hodowli komórkowych, płytek satelitarnych lub monitoringu małych obiektów. Ta umiejętność tworzy kotwice, które faktycznie pasują do danych docelowych.

## Kiedy używać

- Przed pierwszym uruchomieniem szkolenia na nowym zestawie danych.
- Przywołanie bardzo małych lub bardzo dużych obiektów jest słabe w przypadku zdrowego modelu.
- Po znacznym rozszerzeniu zbioru danych, w wyniku którego rozkład wielkości pudełek mógł się zmienić.

## Wejścia

- `boxes`: numpy tablica kształtów (N, 4) w formacie `(cx, cy, w, h)` lub `(x1, y1, x2, y2)`; zalecane co najmniej 1000 pozytywnych pudełek.
- `num_anchors_per_level`: zwykle 3.
- `num_fpn_levels`: zwykle 3 (P3, P4, P5) lub 4.
- `input_size`: rozdzielczość treningowa WxS.
- Opcjonalnie `strides`: kroki na poziomie; w przypadku pominięcia, weź pierwsze wpisy `num_fpn_levels` z `[8, 16, 32, 64]`. Przekaż jawnie dłuższą lub krótszą tablicę, jeśli FPN detektora ma różne kroki.

## Kroki

1. **Normalizuj ramki** do par `(w, h)` w jednostkach pikseli w `input_size`. Usuń dowolne z w lub h < 2 pixels.

2. **Run k-means** on `boxes`2 pairs, with `boxes`3. Use `boxes`4 as the distance function, not Euclidean distance — Euclidean on `boxes`5 collapses thin tall boxes and square boxes together. All boxes contribute equally (unweighted); if you have a class-imbalanced dataset and want larger-box recall, repeat rare-class boxes in the input array rather than passing a weight vector.

3. **Sort clusters by area** ascending. Split into `boxes`6 groups of `boxes`7. Smallest areas go to the highest-resolution level (smallest stride).

4. **Compute coverage statistics** per level:
   - `boxes`8 of each ground-truth box to its best anchor at that level.
   - `boxes`9 — percentage of boxes whose best anchor has IoU >= 0,5.
   - `area coverage` – część skrzynek, których powierzchnia mieści się w `[anchor_min_area / 4, anchor_max_area * 4]` poziomu.

5. **Raportuj kotwice według poziomu** i poziomy flag, jeśli `recall@IoU=0.5 < 0.9`; kotwice tego poziomu nie odpowiadają dobrze danym i należy je ponownie dostroić lub zwiększyć liczbę kotwic na poziom.

## Format raportu

```
[anchor-designer]
  total boxes:         <N>
  clusters:            <k>
  distance metric:     1 - IoU

[level P3  stride=8]
  anchors (w, h):      [(A, B), (C, D), (E, F)]
  median IoU:          <X>
  recall@IoU=0.5:      <X>
  coverage:            <X>
  flag:                ok | retune

[level P4  stride=16]
  ...

[summary]
  overall recall@IoU=0.5: <X>
  smallest anchor:        <w x h>
  largest anchor:         <w x h>
  recommendation:         <one sentence if any level flagged>
```

## Zasady

- Zawsze używaj odległości opartej na IoU; Euklidesowe k-średnie dają wizualnie rozsądne, ale empirycznie gorsze kotwice.
- Sortuj klastry według obszaru, a następnie przypisz je do poziomów w kolejności rosnącej.
- W przypadku `num_anchors_per_level = 1` całkowicie pomiń k-średnich: podziel pola na pojemniki `num_fpn_levels` według kwantylu powierzchni (np. tercyle dla 3 poziomów) i ustaw kotwicę każdego poziomu na medianę przypadającą na przedział (w, h). Jest to bardziej niezawodne niż obliczanie k-średnich za pomocą `k = num_fpn_levels` na małych zbiorach danych.
- Nigdy nie wyprowadzaj ujemnych wymiarów kotwy; zacisk na 1.
- Jeśli zbiór danych zawiera < 200 pól, ostrzeż użytkownika, że wyszukiwanie kotwic jest zawodne i zaleć użycie domyślnych kotwic COCO oraz większej ilości danych szkoleniowych.