---

name: td-agent
description: Wybierz pomiędzy Q-learningiem, SARSA, Oczekiwaną SARSA dla zadania tabelarycznego lub małego zadania RL.
version: 1.0.0
phase: 9
lesson: 4
tags: [rl, td-learning, q-learning, sarsa]

---

Biorąc pod uwagę środowisko tabelaryczne lub mało funkcjonalne, wynik:

1. Algorytm. Q-learning / SARSA / Oczekiwany SARSA / wariant n-etapowy. Powód w jednym zdaniu powiązany z zasadą, niezgodnością z polityką i wariancją.
2. Hiperparametry. α, γ, ε, harmonogram zaniku.
3. Inicjalizacja. Wartość Q_0 (optymistyczna vs zero) i uzasadnienie.
4. Diagnostyka konwergencji. Docelowa krzywa uczenia się, `|Q - Q*|` sprawdź, czy DP jest możliwe.
5. Zastrzeżenie dotyczące wdrożenia. Jak zachowa się eksploracja po wnioskowaniu? Czy konserwatyzm SARSA jest potrzebny?

Odmawiaj stosowania tabelarycznego TD do przestrzeni stanów > 10⁶. Odmów wysłania agenta Q-learning bez zastrzeżenia dotyczącego maksymalnego odchylenia. Oznacz dowolnego agenta przeszkolonego z ε utrzymywanym na poziomie 1,0 przez cały czas (bez fazy eksploatacji).