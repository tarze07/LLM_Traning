---

name: skill-conv-shape-calculator
description: Przeglądaj specyfikację CNN warstwa po warstwie i raportuj kształt wyjściowy, pole odbiorcze i liczbę parametrów dla każdego bloku
version: 1.0.0
phase: 4
lesson: 2
tags: [computer-vision, cnn, architecture, debugging]

---

# Kalkulator wymiarów i parametrów warstw CNN

Deterministyczne narzędzie pomocnicze do projektowania i debugowania sieci CNN. Na podstawie kształtu wejściowego oraz listy parametrów warstw wyznacza wymiary wyjściowe tensorów, pole receptywne (receptive field) oraz liczbę parametrów dla każdego bloku, bez konieczności uruchamiania kodu modelu.

## Kiedy używać

- Projektujesz nową sieć CNN i chcesz upewnić się, że wymiary wyjściowe każdej warstwy są prawidłowe.
- Czytasz artykuł naukowy i chcesz przełożyć tabelę z architekturą sieci na działający kod.
- Model bazowy (backbone) zgłasza błąd niezgodności wymiarów (shape mismatch) w głowicy klasyfikacyjnej i musisz zlokalizować, która warstwa niepoprawnie zmieniła wymiar przestrzenny.
- Porównujesz dwie architektury pod kątem liczby parametrów i zapotrzebowania na pamięć przed rozpoczęciem treningu.

## Dane wejściowe

- `input_shape`: kształt wejściowy w formacie `(C, H, W)`.
- `layers`: uporządkowana lista definicji warstw. Obsługiwane typy warstw:
  - `{type: "conv", c_out, k, s, p, groups=1, bias=true}` (warstwa konwolucyjna)
  - `{type: "pool", mode: "max"|"avg", k, s, p=0}` (pooling)
  - `{type: "adaptive_pool", out_h, out_w}` (pooling adaptacyjny)
  - `{type: "flatten"}` (spłaszczenie)
  - `{type: "linear", out_features, bias=true}` (warstwa liniowa)

## Procedura obliczeniowa

1. **Inicjalizacja stanu**: Ustaw wymiar początkowy `(C, H, W)`, pole receptywne (RF) na `1`, efektywny krok (effective stride) na `1` oraz skumulowaną liczbę parametrów na `0`.

2. **Dla każdej warstwy** wylicz i zaktualizuj kolejno:
   - **Liczba kanałów wyjściowych (`C_out`)**: odpowiednio do definicji dla warstw konwolucyjnych i liniowych lub przepisz `C_in` dla warstw poolingu.
   - **Wymiary przestrzenne (`H_out`, `W_out`)**:
     - Dla warstw konwolucyjnych (conv) oraz poolingu: $\lfloor(H_{in} + 2P - K) / S\rfloor + 1$.
     - Dla poolingu adaptacyjnego: docelowe wymiary przestrzenne `out_h` oraz `out_w`.
     - Dla spłaszczenia (flatten): wyjściowy wymiar wynosi $C_{in} \cdot H_{in} \cdot W_{in}$ (wymiary przestrzenne sprowadzane są do 1).
     - Dla warstwy liniowej: wymiar przestrzenny wynosi $1 \times 1$, a liczba kanałów odpowiada liczbie cech wyjściowych (`out_features`).
   - **Pole receptywne (RF) i efektywny krok**:
     - Warstwa konwolucyjna / pooling: $RF_{new} = RF_{old} + (K - 1) \cdot \text{effective\_stride}$, a następnie $\text{effective\_stride}_{new} = \text{effective\_stride}_{old} \cdot S$.
     - Pooling adaptacyjny: traktuj jak pooling z efektywnym krokiem $S = H_{in} / out\_h$ (zaokrąglonym w dół). $RF_{new} = RF_{old} + (H_{in} - 1) \cdot \text{effective\_stride}_{old}$; $\text{effective\_stride}_{new} = \text{effective\_stride}_{old} \cdot S$. Warto zauważyć, że pole receptywne po poolingu adaptacyjnym pokrywa pełen dotychczasowy obszar przestrzenny.
     - Spłaszczenie (flatten) / warstwa liniowa: pole receptywne i efektywny krok nie są już modyfikowane (zamroź je na wartościach sprzed spłaszczenia).
   - **Liczba parametrów warstwy**:
     - Konwolucja (conv): $C_{out} \cdot (C_{in} / \text{groups}) \cdot K \cdot K + (C_{out}\text{ jeśli bias jest włączony, w przeciwnym razie } 0)$.
     - Warstwa liniowa (linear): $\text{out\_features} \cdot \text{in\_features} + (\text{out\_features}\text{ jeśli bias jest włączony, w przeciwnym razie } 0)$.
     - Pooling i spłaszczenie (flatten): 0.

3. **Detekcja problemów** (oznaczanie potencjalnych błędów w raporcie):
   - Wymiar wyjściowy nie będący liczbą całkowitą (nieprawidłowo dobrany krok/stride lub dopełnienie/padding).
   - Wymiary przestrzenne warstwy spadek do wartości $H_{out} \le 0$ przed końcem sieci.
   - Pole receptywne przekraczające fizyczny rozmiar danych wejściowych (potencjalnie bezużyteczne operacje obliczeniowe).
   - Nagłe, co najmniej 10-krotne skoki liczby parametrów na warstwę, co sugeruje złe planowanie liczby kanałów.

4. **Raport** w formie zunifikowanej tabeli:

```
idx  layer                C_in  C_out  K  S  P  H_out  W_out  RF    params     cum_params
1    conv 3x3 s=1 p=1     3     32     3  1  1  224    224    3     896        896
2    conv 3x3 s=2 p=1     32    64     3  2  1  112    112    7     18,496     19,392
3    pool max 2x2         64    64     2  2  0  56     56     11    0          19,392
...
```

5. **Wiersz podsumowania**: końcowy kształt tensora `(C, H, W)`, końcowe pole receptywne, całkowita liczba parametrów sieci oraz wykaz ostrzeżeń diagnostycznych.

## Reguły i ograniczenia

- Zawsze zwracaj liczby całkowite dla wymiarów przestrzennych. Jeśli formuła da wynik ułamkowy, zgłoś błąd – nie dokonuj zaokrągleń w sposób niejawny.
- Przy konwolucji grupowanej (`groups > 1`) zweryfikuj, czy zachodzą warunki: `C_in % groups == 0` oraz `C_out % groups == 0`. Jeśli nie, zgłoś błąd.
- Przy konwolucji głębokiej (depthwise convolution, gdzie `groups == C_in`), dodaj odpowiednie oznaczenie w kolumnie `layer`, aby wyjaśnić niski koszt parametryczny warstwy.
- Jeśli specyfikacja zawiera warstwy BatchNorm lub aktywacji – zignoruj je przy wyznaczaniu wymiarów przestrzennych, ale uwzględnij ich parametry ($2 \cdot C$ parametrów dla każdej warstwy BatchNorm).
- Nigdy nie domyślaj się wartości brakujących parametrów. Wymagaj jawnego podania wartości `k` (kernel), `s` (stride) i `p` (padding) dla każdej warstwy konwolucyjnej i poolingu.
