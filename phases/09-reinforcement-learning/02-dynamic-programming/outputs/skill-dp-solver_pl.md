---

name: dp-solver
description: Rozwiąż mały tabelaryczny MDP dokładnie poprzez iterację zasad lub iterację wartości. Zgłoś zachowanie zbieżności.
version: 1.0.0
phase: 9
lesson: 2
tags: [rl, dynamic-programming, bellman]

---

Biorąc pod uwagę MDP ze znanym modelem, wynik:

1. Wybór. Iteracja polityki a iteracja wartości. Powód związany z |S|, |A|, γ.
2. Inicjalizacja. V_0, polityka początkowa. Wrażliwość konwergencji.
3. Zatrzymanie. Tolerancja powyżej normy ε. Oczekiwana liczba przemiatań.
4. Weryfikacja. V*(s_0) obliczone dokładnie. Wyciągnięto chciwą politykę.
5. Użyj. W jaki sposób ta wartość bazowa zostanie wykorzystana do debugowania/oceny metod opartych na próbkowaniu.

Odmów uruchomienia DP w przestrzeniach stanów > 10⁷. Odmów twierdzenia o zbieżności bez sprawdzenia normy. Oznacz dowolne γ ≥ 1 w zadaniu o nieskończonym horyzoncie jako naruszenie gwarancji.