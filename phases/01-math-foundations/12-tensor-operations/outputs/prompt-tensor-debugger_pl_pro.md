---

name: prompt-tensor-debugger
description: Asystent debugowania krok po kroku błędów związanych z kształtami tensorów w kodzie deep learning.
phase: 1
lesson: 12

---

W moim kodzie głębokiego uczenia występuje błąd kształtu (wymiarów) tensora. Pomóż mi go naprawić.

**Komunikat o błędzie:** [wklej tutaj błąd]

**Moje kształty tensorów:**
- [nazwa]: [kształt]
- [nazwa]: [kształt]

**Operacja, którą próbuję wykonać:** [opisz ją]

---

Podczas debugowania przeprowadź dokładnie poniższy proces:

**Krok 1: Określ typ operacji.**
Jaka operacja spowodowała błąd? Przypisz ją do jednej z poniższych kategorii:
- Mnożenie macierzy / Warstwa liniowa (wymiary wewnętrzne muszą się zgadzać)
- Rozgłaszanie / Broadcasting (wyrównaj do prawej, każdy zestaw wymiarów musi być równy lub wynosić 1)
- Konkatenacja / Concatenation (wszystkie wymiary muszą pasować, z wyjątkiem wymiaru wzdłuż którego następuje łączenie)
- Splot / Convolution (oczekuje konkretnego rzędu tensora i określonej pozycji dla kanału)
- Zmiana kształtu / Reshape (wszystkie elementy muszą zostać zachowane)

**Krok 2: Określ układ wymiarów (shape contract).**
Dla zidentyfikowanej operacji zapisz jawnie oczekiwane kształty:
```
matmul(A, B): A to (..., m, k), B to (..., k, n) -> wynik: (..., m, n)
broadcast(A, B): wyrównaj do prawej, w każdej parze muszą być równe lub jeden wynosi 1
cat([A, B], dim=d): wszystkie wymiary pasują z wyjątkiem wymiaru d
Linear(in_f, out_f): ostatni wymiar wejścia musi być równy in_f
Conv2d(in_c, out_c, k): wejście musi wynosić (B, in_c, H, W)
```

**Krok 3: Znajdź niezgodność.**
Porównaj rzeczywiste kształty z oczekiwanymi. Wskaż dokładny wymiar, który narusza regułę.

**Krok 4: Wybierz minimalną poprawkę.**
Wybierz optymalne rozwiązanie z poniższej tabeli:

| Objaw | Rozwiązanie |
|---|---|
| Brak wymiaru wsadu (batch dim) | `.unsqueeze(0)` |
| Brak wymiaru kanału | `.unsqueeze(1)` |
| Zbędny wymiar o rozmiarze 1 | `.squeeze(dim)` |
| Niezgodne wymiary wewnętrzne dla mnożenia macierzy | `.transpose(-1, -2)` lub sprawdź kształt wag |
| Masz NHWC, a potrzebujesz NCHW | `.permute(0, 3, 1, 2)` |
| Masz NCHW, a potrzebujesz NHWC | `.permute(0, 2, 3, 1)` |
| Spłaszczenie wymiarów przestrzennych dla warstwy liniowej | `.flatten(1)` lub `.reshape(B, -1)` |
| Podział na głowy: z (B,T,D) do (B,H,T,D/H) | `.reshape(B, T, H, D//H).transpose(1, 2)` |
| Łączenie głów: z (B,H,T,D/H) do (B,T,D) | `.transpose(1, 2).reshape(B, T, H*(D//H))` |
| Nieciągły tensor błądzący przy .view() | `.contiguous().view(...)` lub po prostu `.reshape(...)` |

**Krok 5: Zweryfikuj poprawkę.**
Pokaż wynikowe kształty dla każdego kroku. Upewnij się, że całkowita liczba elementów została zachowana (szczególnie przy operacji `reshape`). Sprawdź, czy kontrakt układu wymiarów jest teraz poprawnie spełniony.

**Krok 6: Sprawdź potencjalne, ciche błędy.**
Nawet jeśli wymiary pasują, upewnij się, że:
- Rozgłaszanie (broadcasting) ma miejsce wzdłuż prawidłowej osi (a nie przypadkowej).
- Redukcja sumuje zmienne na zamierzonej osi.
- Wymiar wsadu (batch) – najczęściej wymiar 0 – pozostaje nietknięty na każdym etapie przetwarzania (forward pass).
- Jeśli zależy nam na kolejności wymiarów, prawidłowym rozwiązaniem jest transpozycja z następującą zmianą kształtu (transpose + reshape), a nie tylko samo `reshape`.

Sformatuj swoją odpowiedź następująco:
```
OPERACJA: [jaka operacja wywołała błąd]
OCZEKIWANE: [wymagany układ wymiarów - shape contract]
RZECZYWISTE: [jakie podano kształty]
NIEZGODNOŚĆ: [który z wymiarów wywołał błąd i dlaczego]
ROZWIĄZANIE: [dokładny kod]
WYNIK: [kształty na koniec procesu weryfikacji po poprawce]
```
