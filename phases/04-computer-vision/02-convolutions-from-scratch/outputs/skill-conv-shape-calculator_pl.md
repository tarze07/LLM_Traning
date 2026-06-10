---

name: skill-conv-shape-calculator
description: Przeglądaj specyfikację CNN warstwa po warstwie i raportuj kształt wyjściowy, pole odbiorcze i liczbę parametrów dla każdego bloku
version: 1.0.0
phase: 4
lesson: 2
tags: [computer-vision, cnn, architecture, debugging]

---

# Kalkulator kształtu konw

Deterministyczny pomocnik do planowania lub debugowania CNN. Biorąc pod uwagę kształt wejściowy i listę specyfikacji warstw, kształtów śledzenia, pól receptywnych i liczby parametrów bez uruchamiania modelu.

## Kiedy używać

- Projektujesz nową CNN i chcesz sprawdzić, czy każda próbka ma prawidłowy rozmiar.
- Czytanie artykułu i tłumaczenie jego tabeli architektury na kod.
- Wstępnie wyszkolony szkielet ulega awarii z powodu niedopasowania kształtu w głowicy klasyfikatora i trzeba wiedzieć, która warstwa zmieniła rozmiar przestrzenny.
- Porównanie dwóch szkieletów pod względem wydajności parametrów przed szkoleniem.

## Wejścia

-`input_shape`:`(C, H, W)`.
- `layers`: uporządkowana lista nagrań warstw. Każdy obsługuje:
  -`{type: "conv", c_out, k, s, p, groups=1, bias=true}`
  -`{type: "pool", mode: "max"|"avg", k, s, p=0}`
  -`{type: "adaptive_pool", out_h, out_w}`
  -`{type: "flatten"}`
  -`{type: "linear", out_features, bias=true}`

## Kroki

1. **Zainicjuj śledzenie** za pomocą `(C, H, W)`, pole receptywne `1`, efektywny krok `1`, skumulowane parametry `0`.

2. **Dla każdej warstwy** aktualizuj w następującej kolejności:
   - Oblicz `C_out` (konw./liniowy) lub przenieś `C_in` (pula).
   - Oblicz wynik przestrzenny przy użyciu `(H + 2P - K) / S + 1` dla konwersji i puli, `out_h/out_w` dla puli adaptacyjnej, `(1, 1)` dla spłaszczonego kształtu wyjściowego `(C * H * W, 1, 1)` przed linią i skalarnego `1x1` dla liniowości.
   - Zaktualizuj pole receptywne i efektywny krok:
     - Konw./pula: `RF_new = RF_old + (K - 1) * effective_stride`, `effective_stride *= S`.
     - Pula adaptacyjna: traktuj jak pulę z efektywnym `S = H_in / out_h` (zaokrąglając w dół). `RF_new = RF_old + (H_in - 1) * effective_stride_old`; `effective_stride *= S`. Należy pamiętać, że RF puli adaptacyjnej jest równy pełnemu poprzedniemu zakresowi przestrzennemu.
     - Spłaszczony / liniowy: RF i efektywny krok nie mają już znaczenia; zamroź je do wartości sprzed spłaszczenia i pomiń w kolejnych wierszach.
   - Oblicz parametry:
     - Konw.: `C_out * (C_in / groups) * K * K + (C_out if bias else 0)`.
     - Liniowy: `out_features * in_features + (out_features if bias else 0)`.
     - Basen i spłaszczenie: 0.

3. **Wykryj problemy** i oznacz je:
   - Rozmiar wyjściowy niecałkowity (niewłaściwie wyrównany krok/wypełnienie).
   - `H_out <= 0` przed końcem stosu.
   - Pole recepcyjne przekracza rozmiar wejściowy (możliwe zmarnowane obliczenia po tym punkcie).
   - Nagłe 10-krotne skoki parametrów na warstwę, które sugerują niewłaściwy plan kanałów.

4. **Raport** jako pojedyncza tabela:

```
idx  layer                C_in  C_out  K  S  P  H_out  W_out  RF    params     cum_params
1    conv 3x3 s=1 p=1     3     32     3  1  1  224    224    3     896        896
2    conv 3x3 s=2 p=1     32    64     3  2  1  112    112    7     18,496     19,392
3    pool max 2x2         64    64     2  2  0  56     56     11    0          19,392
...
```

5. **Linia podsumowania**: końcowy `(C, H, W)`, końcowe pole odbiorcze, parametry całkowite, ostrzeżenia.

## Zasady

- Zawsze zwracaj liczby całkowite dla rozmiarów przestrzennych. Jeśli formuła zwróci liczbę niecałkowitą, oznacz jako błąd i nie przesuwaj po cichu.
- W przypadku `groups > 1` sprawdź `C_in % groups == 0` i `C_out % groups == 0`; w przeciwnym razie błąd.
- W przypadku konwersji głębinowej (`groups == C_in`) oznacz ją w kolumnie `layer`, aby czytelnik zobaczył, dlaczego parametry są niskie.
- Jeśli użytkownik udostępnia BatchNorm lub warstwy aktywacyjne, zignoruj ​​je ze względu na kształt, ale przenieś parametry do przodu (`2 * C` na BatchNorm).
- Nigdy nie zgaduj wartości domyślnych dla brakujących pól. Wymagaj `k`, `s`, `p` w każdej konwersji i puli.