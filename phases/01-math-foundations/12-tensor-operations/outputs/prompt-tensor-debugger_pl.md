---

name: prompt-tensor-debugger
description: Monit o debugowanie krok po kroku pod kątem błędów kształtu tensora w kodzie głębokiego uczenia się
phase: 1
lesson: 12

---

W moim kodzie głębokiego uczenia się występuje błąd kształtu tensora. Pomóż mi to naprawić.

**Komunikat o błędzie:** [wklej tutaj błąd]

**Moje kształty tensora:**
- [nazwa]: [kształt]
- [nazwa]: [kształt]

**Operacja, którą próbuję wykonać:** [opisz ją]

---

Podczas debugowania wykonaj dokładnie ten proces:

**Krok 1: Określ typ operacji.**
Jaka operacja spowodowała błąd? Zamapuj go na jeden z tych:
- Mnożenie macierzy / Warstwa liniowa (wymiary wewnętrzne muszą się zgadzać)
- Nadawanie (wyrównaj od prawej, każde przyciemnienie musi być równe lub 1)
- Łączenie (wszystkie wymiary pasują oprócz wymiaru kota)
- Splot (oczekuje określonej rangi i pozycji kanału)
- Zmień kształt (należy zachować wszystkie elementy)

**Krok 2: Spisz umowę dotyczącą kształtu.**
Dla zidentyfikowanej operacji zapisz jawnie oczekiwane kształty:
```
matmul(A, B): A is (..., m, k), B is (..., k, n) -> (..., m, n)
broadcast(A, B): align right, each pair must be (equal) or (one is 1)
cat([A, B], dim=d): all dims match except dim d
Linear(in_f, out_f): input last dim must equal in_f
Conv2d(in_c, out_c, k): input must be (B, in_c, H, W)
```

**Krok 3: Znajdź niezgodność.**
Porównaj rzeczywiste kształty z umową. Określ dokładny wymiar, który narusza regułę.

**Krok 4: Wybierz minimalną poprawkę.**
Wybierz z tej tabeli:

| Objaw | Napraw |
|---|---|
| Brak wymiaru partii | `.unsqueeze(0)` |
| Brak wymiaru kanału | `.unsqueeze(1)` |
| Dodatkowy rozmiar-1 wymiar | `.squeeze(dim)` |
| Wewnętrzne przyciemnienie jest złe dla matmul | `.transpose(-1, -2)` lub sprawdź kształt ciężarka |
| Potrzebujesz NCHW z NHWC | `.permute(0, 3, 1, 2)` |
| Potrzebujesz NHWC z NCHW | `.permute(0, 2, 3, 1)` |
| Spłaszcz przyciemnienia przestrzenne dla liniowego | `.flatten(1)` lub `.reshape(B, -1)` |
| Głowice dzielone: ​​(B,T,D) do (B,H,T,D/H) | `.reshape(B, T, H, D//H).transpose(1, 2)` |
| Połącz głowy: (B,H,T,D/H) z (B,T,D) | `.transpose(1, 2).reshape(B, T, H*(D//H))` |
| Nieciągły tensor z .view() | `.contiguous().view(...)` lub użyj `.reshape(...)` |

**Krok 5: Sprawdź poprawkę.**
Pokaż powstałe kształty na każdym kroku. Upewnij się, że wszystkie elementy zostały zachowane w przypadku dowolnej zmiany kształtu. Upewnij się, że kontrakt dotyczący kształtu operacji jest teraz spełniony.

**Krok 6: Sprawdź, czy nie występują ciche błędy.**
Nawet jeśli kształty pasują, sprawdź:
- Nadawanie odbywa się wzdłuż zamierzonej osi (nieprzypadkowo)
- Redukcja to sumowanie po właściwym wymiarze
- Wymiar wsadowy (wymiar 0) przetrwa cały przebieg do przodu
- Transpozycja + zmiana kształtu są stosowane (a nie tylko zmiana kształtu), gdy liczy się kolejność wymiarów

Sformatuj swoją odpowiedź jako:
```
OPERATION: [what operation failed]
EXPECTED: [shape contract]
ACTUAL: [what shapes were provided]
MISMATCH: [which dimension, why]
FIX: [exact code]
RESULT: [shapes after fix]
```