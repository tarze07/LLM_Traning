---

name: skill-image-tensor-inspector
description: Sprawdź dowolny tensor lub tablicę w kształcie obrazu i zgłoś typ, układ, zakres oraz to, czy wygląda na surowy, znormalizowany czy ustandaryzowany
version: 1.0.0
phase: 4
lesson: 1
tags: [computer-vision, debugging, preprocessing, tensors]

---

# Inspektor tensora obrazu

Umiejętność diagnostyczna dla dowolnego punktu potoku wizji, w którym trzymasz tablicę w kształcie obrazu i musisz dokładnie wiedzieć, w jakim jest stanie.

## Kiedy używać

— Wstępnie wyszkolony model zwraca prognozy dotyczące śmieci i podejrzewasz przetwarzanie wstępne.
- Migracja potoku pomiędzy OpenCV i torchvision oraz kolejność kanałów są niejasne.
- Układanie warstw z wielu frameworków i oś wsadowa ciągle pojawia się w niewłaściwym miejscu.
- Debugowanie pętli treningowej, w której strata utknęła na `log(num_classes)`.

## Wejścia

- `x`: dowolna tablica 2-D, 3-D lub 4-D (NumPy, PyTorch, JAX).
- Opcjonalnie `expected`: zestaw niezmienników do sprawdzenia, np. `{"layout": "CHW", "range": "standardized"}`.

## Kroki

1. **Rozwiąż backend** — sprawdź, czy `x` to NumPy, Torch czy JAX. Konwertuj na NumPy do kontroli bez zmiany oryginału.

2. **Sklasyfikuj rangę**:
   - ranga 2 -> obraz jednokanałowy (wys., szer.).
   - ranga 3 -> `HWC` jeśli ostatnia oś ma numer 1, 3 lub 4 i jest wyraźnie mniejsza od pozostałych dwóch; w przeciwnym razie `CHW`.
   - ranga 4 -> preferuj `NCHW`, jeśli oś 1 znajduje się w {1, 3, 4} **i** albo oś 2, albo oś 3 jest większa niż 16; w przeciwnym razie preferuj `NHWC`. Kontrola czystej osi 1 błędnie klasyfikuje partie NHWC małych obrazów, takie jak `(3, 4, 224, 3)`.
   - Zawsze oznaczaj niejednoznaczne przypadki (np. `(1, 3, 3, 3)`) jako `ambiguous`, zamiast zgadywać; wymagać od osoby dzwoniącej podania numeru `expected`.

3. **Sklasyfikuj typ i zakres**:
   - `uint8` w [0, 255] -> `raw`.
   - `float*` z min >= 0 i max <= 1.01 -> `normalized`.
   - `float*` z min. < 0 and |mean| < 0.5 and 0.5 <= std <= 1.5 -> `standardized`.
   - Wszystko inne -> `unusual`, wydrukuj histogram.

4. **Statystyki na kanał** — raportuj średnią i standardową wartość na kanał. Porównaj ze średnią/std ImageNet, jeśli tablica wygląda na standaryzowaną i uzyskaj pewność dopasowania.

5. **Raport** w tym dokładnie bloku:

```
[inspector]
  backend:   numpy | torch | jax
  rank:      2 | 3 | 4
  layout:    HW | HWC | CHW | NHWC | NCHW
  dtype:     <dtype>
  shape:     <shape>
  range:     raw | normalized | standardized | unusual
  min/max:   <min> / <max>
  per-channel mean: [ ... ]
  per-channel std:  [ ... ]
  likely source:    camera | PIL | OpenCV | torchvision | random init
  likely target:    display | training | inference
```

6. **Zalecaj następne działanie** w oparciu o `likely target`:
   - Dla `display`: transpozycja do HWC, klip, konwersja do uint8.
   - W przypadku `training`: standaryzacja za pomocą statystyk zbioru danych, transpozycja do CHW, dodanie osi wsadowej.
   - Dla `inference`: dopasuj dokładnie niezmienniki na karcie modelu.

## Zasady

- Nigdy nie mutuj wejścia. Drukuj tylko diagnostykę.
- Jeśli zapewniono `expected`, oznacz każdą niezgodność z `[expected X got Y]`.
- Wskaż ryzyko cichej awarii, gdy układ lub kolejność kanałów jest niejednoznaczna.
- Polecaj jedno działanie na raz, a nie listę opcji.