---

name: dp-solver
description: Rozwiąż mały tabelaryczny MDP dokładnie za pomocą iteracji strategii lub iteracji wartości. Przedstaw przebieg zbieżności.
version: 1.0.0
phase: 9
lesson: 2
tags: [rl, dynamic-programming, bellman]

---

Dla danego MDP ze znanym modelem, wygeneruj:

1. Wybór metody: iteracja strategii a iteracja wartości. Uzasadnienie wyboru w oparciu o |S|, |A| oraz γ.
2. Inicjalizacja: wartości początkowe V_0, początkowa strategia. Wpływ inicjalizacji na zbieżność.
3. Kryterium zatrzymania: próg zbieżności dla normy (tolerancja ε). Oczekiwana liczba pełnych przebiegów (sweeps).
4. Weryfikacja: dokładne obliczenie V*(s_0). Wyznaczona strategia zachłanna.
5. Zastosowanie: sposób wykorzystania tej wartości bazowej (baseline) do debugowania i oceny metod opartych na próbkowaniu.

Odrzuć żądanie uruchomienia programowania dynamicznego (DP) dla przestrzeni stanów o rozmiarze > 10⁷. Nie deklaruj zbieżności bez zweryfikowania normy. Oznacz każdą wartość γ ≥ 1 w zadaniu z nieskończonym horyzontem jako naruszenie założeń gwarantujących zbieżność.
