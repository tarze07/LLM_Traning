---

name: skill-image-tensor-inspector
description: Zbadaj dowolny tensor lub tablicę reprezentującą obraz i zwróć jego typ, układ osi, zakres wartości oraz określ, czy dane są surowe, znormalizowane, czy ustandaryzowane.
version: 1.0.0
phase: 4
lesson: 1
tags: [computer-vision, debugging, preprocessing, tensors]

---

# Inspektor Tensorów Obrazu

Narzędzie diagnostyczne przydatne w dowolnym punkcie potoku wizyjnego, gdy operujesz na tablicy danych obrazu i musisz precyzyjnie zweryfikować jej stan.

## Kiedy używać

- Wstępnie wytrenowany model zwraca całkowicie błędne predykcje, a Ty podejrzewasz problem z preprocessingiem.
- Migrujesz potok przetwarzania z OpenCV do torchvision i kolejność kanałów jest niejasna.
- Łączysz warstwy z różnych frameworków, a oś wymiaru paczki (batch) ciągle pojawia się w niewłaściwym miejscu.
- Debugujesz pętlę treningową, w której funkcja straty (loss) utknęła na poziomie `log(num_classes)`.

## Wejścia

- `x`: dowolna tablica 2D, 3D lub 4D (NumPy, PyTorch, JAX).
- Opcjonalne `expected`: zbiór niezmienników do sprawdzenia, np. `{"layout": "CHW", "range": "standardized"}`.

## Kroki

1. **Zidentyfikuj backend** — sprawdź, czy `x` pochodzi z NumPy, Torch czy JAX. Dokonaj bezinwazyjnej konwersji do NumPy w celu inspekcji, nie modyfikując przy tym oryginału.

2. **Sklasyfikuj rangę wymiaru (rank)**:
   - Ranga 2 -> obraz jednokanałowy (wysokość, szerokość - HW).
   - Ranga 3 -> `HWC`, jeśli ostatnia oś ma rozmiar 1, 3 lub 4 i jest zauważalnie mniejsza od pozostałych dwóch; w przeciwnym razie `CHW`.
   - Ranga 4 -> preferuj układ `NCHW`, jeśli oś 1 ma rozmiar w {1, 3, 4} **oraz** oś 2 lub oś 3 jest większa niż 16; w przeciwnym wypadku preferuj `NHWC`. Samo sprawdzanie osi 1 prowadzi do błędnej klasyfikacji partii NHWC małych obrazów, takich jak np. `(3, 4, 224, 3)`.
   - Zawsze oznaczaj przypadki niejednoznaczne (np. `(1, 3, 3, 3)`) jako `ambiguous` zamiast zgadywać w ciemno; w takich sytuacjach wymagaj od użytkownika podania parametru `expected`.

3. **Sklasyfikuj typ i zakres wartości**:
   - `uint8` w przedziale [0, 255] -> `raw` (surowy).
   - `float*` z min >= 0 i max <= 1.01 -> `normalized` (znormalizowany).
   - `float*` z min < 0 oraz |mean| < 0.5 oraz 0.5 <= std <= 1.5 -> `standardized` (ustandaryzowany).
   - Jakikolwiek inny przypadek -> `unusual` (nietypowy), wydrukuj histogram.

4. **Statystyki poszczególnych kanałów** — zaraportuj średnią oraz odchylenie standardowe dla każdego kanału. Jeśli tablica wydaje się ustandaryzowana, porównaj statystyki ze średnią i std. dla ImageNet, określając pewność takiego dopasowania.

5. **Wygeneruj raport**, korzystając dokładnie z tego bloku:

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

6. **Zarekomenduj następny krok** na podstawie przewidywanego celu (`likely target`):
   - Dla celu `display` (wyświetlanie): transpozycja do układu HWC, przycięcie (clip) i konwersja do typu uint8.
   - Dla celu `training` (trening): standaryzacja za pomocą statystyk ze zbioru danych, transpozycja do CHW i dodanie osi paczki (batch).
   - Dla celu `inference` (inferencja): wymuś dokładne dopasowanie niezmienników z karty używanego modelu.

## Zasady

- Nigdy nie mutuj ani nie nadpisuj wejścia. Wypisuj wyłącznie diagnostykę.
- Jeśli dostarczono słownik `expected`, oznacz każdą znalezioną niezgodność w formacie `[expected X got Y]`.
- Ostrzegaj o ryzyku cichej awarii w przypadku niejasnego układu osi lub kolejności kanałów.
- Sugeruj tylko jedną najsensowniejszą akcję naprawczą na raz, zamiast wylistowywać ich opcje.
