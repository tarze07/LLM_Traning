---

name: td-agent
description: Wybierz optymalny algorytm spośród Q-learning, SARSA lub Expected SARSA dla środowisk tabelarycznych lub o małej przestrzeni stanów.
version: 1.0.0
phase: 9
lesson: 4
tags: [rl, td-learning, q-learning, sarsa]

---

Biorąc pod uwagę środowisko tabelaryczne lub o prostej reprezentacji cech, wygeneruj:

1. Algorytm. Q-learning / SARSA / Expected SARSA / wariant wielokrokowy (n-step). Podaj jednozdaniowe uzasadnienie powiązane z trybem uczenia (on-policy / off-policy) oraz wariancją estymatora.
2. Hiperparametry. Współczynnik uczenia alfa (α), współczynnik dyskontujący gamma (γ), współczynnik eksploracji epsilon (ε) oraz harmonogram jego stopniowego zmniejszania (decay schedule).
3. Inicjalizacja. Wartość początkowa tablicy Q (Q_0) – inicjalizacja optymistyczna (optimistic initialization) kontra zerowa, wraz z uzasadnieniem.
4. Diagnostyka zbieżności. Oczekiwana krzywa uczenia, weryfikacja błędu `|Q - Q*|` (jeśli programowanie dynamiczne DP jest wykonalne dla danego środowiska).
5. Specyfika wdrożenia. Zachowanie eksploracji podczas wnioskowania (inference). Czy ze względów bezpieczeństwa wymagana jest ostrożniejsza polityka oferowana przez SARSA?

Odrzuć stosowanie tabelarycznych metod różnic czasowych (TD) dla przestrzeni stanów przekraczających 10⁶. Odrzuć projekty oparte na Q-learningu bez uwzględnienia problemu systematycznego zawyżania wartości akcji (maximization bias). Oznacz flagą ostrzegawczą każdego agenta szkolonego ze stałym parametrem ε = 1.0 przez cały proces (brak przejścia do fazy eksploatacji).
