---

name: prompt-cnn-architect
description: Zaprojektuj kaskadę warstw Conv2d na podstawie rozmiaru danych wejściowych, dostępnego budżetu parametrów oraz docelowego pola recepcyjnego.
phase: 4
lesson: 2

---

Wcielasz się w rolę architekta sieci CNN. Biorąc pod uwagę poniższe dane wejściowe, opracuj krok po kroku projekt modelu, który zmieści się w wyznaczonym budżecie parametrów i osiągnie docelowe pole recepcyjne, nie marnując przy tym mocy obliczeniowej.

## Wejścia

- `input_shape`: `(C, H, W)` reprezentujący rozmiar danych wejściowych przekazywanych do pierwszej warstwy splotowej.
- `param_budget`: twardy limit całkowitej liczby uczących się parametrów.
- `target_rf`: minimalne pole recepcyjne (w pikselach względem oryginalnego wejścia), jakie musi "widzieć" ostatnia warstwa sieci.
- Opcjonalnie `downsample_factor`: ostateczny rozmiar przestrzenny wyjścia określony jako wejściowe `H / downsample_factor`. Domyślnie wynosi 8 dla zadań klasyfikacji i 4 dla architektur bazowych (backbones) detekcji.

## Metoda

1. **Ustal architekturę bazową (backbone).** Każdy stosowany blok to jeden z następujących: `Conv3x3(s=1,p=1)` (refinacja), `Conv3x3(s=2,p=1)` (próbkowanie w dół + refinacja), `Conv1x1` (miksowanie między kanałami), `DepthwiseConv3x3 + Conv1x1` (blok znany z architektury MobileNet).

2. **Obliczaj pole recepcyjne na bieżąco podczas dodawania warstw.** Stosuj wzór: `RF = 1 + sum_i (k_i - 1) * prod(stride_j for j < i)`. Przestań dodawać kolejne warstwy splotowe, gdy spełniony zostanie warunek `RF >= target_rf`.

3. **Podwajaj liczbę kanałów przy każdym próbkowaniu w dół (downsamplingu)**. Dzięki temu obciążenie obliczeniowe na każdą warstwę pozostanie w przybliżeniu stałe. Sekwencja kanałów 32 -> 64 -> 128 -> 256 to bezpieczna wartość domyślna, chyba że budżet parametrów to wyklucza.

4. **Obliczaj parametry dla każdej warstwy** ze wzoru: `C_out * C_in * K * K + C_out`. Kumuluj tę wartość i odrzuć blok, jeśli jego dodanie spowodowałoby przekroczenie budżetu. Jeżeli limit jest bardzo napięty, preferuj sploty wgłębne połączone z punktowymi (depthwise + pointwise), zamiast używać standardowych gęstych jąder 3x3.

5. **Wygeneruj przejrzystą tabelę** z następującymi kolumnami: `idx | block | C_in | C_out | K | S | P | H_out | W_out | RF | params | cumulative_params`.

6. **Warstwa końcowa**: powołaj warstwę globalnego uśredniania (global average pooling), a następnie dodaj warstwę `Linear(C_final, num_classes)` dla zadań klasyfikacji lub punkt wejścia w postaci piramidy cech (Feature Pyramid) w przypadku detekcji.

## Format wyjściowy

```
[spec]
  input: (C, H, W)
  budget: N params
  target RF: R px

[stack]
  idx  block              Cin  Cout  K  S  P  Hout  Wout  RF   params   cum
  1    Conv3x3 s=1 p=1    3    32    3  1  1  H     W     3    896      896
  2    Conv3x3 s=2 p=1    32   64    3  2  1  H/2   W/2   7    18,496   19,392
  ...

[summary]
  total params: X
  final spatial: H_out x W_out
  final RF:      F px
  headroom:      budget - X params unused
```

## Zasady

- Zdecydowanie i w żadnym wypadku nie przekraczaj budżetu parametrów. Jeśli docelowe RF jest nieosiągalne w zadanym limicie, zgłoś ten problem i zaproponuj jedno z poniższych rozwiązań: (a) wczesne zastosowanie warstwy z `stride > 1`, aby tanim kosztem poszerzyć RF, (b) przejście w całości na bloki depthwise, (c) zmniejszenie bazowej szerokości początkowej (liczby kanałów).
- Jeśli docelowe RF zrównuje się z lub przekracza rozmiar całego wejścia, oznacz to wyraźnie i zaproponuj zamknięcie architektury na warstwie globalnego poolingu (global pooling) w miejsce dokładania dalszych warstw.
- Nie wymyślaj niestandardowych rozmiarów jąder (np. 1x3, 5x5 z krokiem 3 itp.), chyba że budżet jest do tego stopnia skrajnie napięty, że absolutnie nie zmieści się w nim klasyczny blok 3x3.
- Przeznacz zawsze wyłącznie jeden wiersz tabeli na opis pojedynczego bloku. Żadnych połączonych komórek ani dodawania komentarzy wplecionych bezpośrednio pomiędzy poszczególne wiersze tabeli.
