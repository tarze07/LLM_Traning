---

name: actor-critic-trainer
description: Skonfiguruj proces uczenia z użyciem algorytmów Actor-Critic (A2C / A3C / GAE) dla zadanego środowiska, określając metodę estymacji przewagi oraz wagi funkcji strat.
version: 1.0.0
phase: 9
lesson: 7
tags: [rl, actor-critic, gae]

---

Biorąc pod uwagę specyfikację środowiska oraz budżet obliczeniowy, wygeneruj:

1. Równoległość. Architektura synchroniczna A2C (przetwarzanie wsadowe na GPU) kontra asynchroniczna A3C (wielowątkowość na CPU) oraz liczba procesów roboczych (workers).
2. Długość horyzontu krokowego (rollout length) T. Liczba kroków wykonywanych w środowisku przed każdą aktualizacją wag.
3. Estymator przewagi (Advantage Estimator). Estymator n-krokowy (n-step) lub uogólniona estymacja przewagi GAE(λ); określ wartość parametru λ.
4. Wagi funkcji strat. Współczynnik straty wartości `c_v` (value loss), współczynnik entropii `c_e` (entropy loss) oraz próg przycinania gradientu (gradient clipping).
5. Współczynniki uczenia (Learning rates). Osobne wartości dla aktora (actor) i krytyka (critic), jeśli stosowane są oddzielne sieci.

Odrzuć stosowanie synchronicznego A2C z jednym procesem roboczym (single worker) w środowiskach o horyzoncie czasowym > 1000 kroków (powolna zbieżność ze względu na silną korelację próbek on-policy). Odrzuć projekty bez zastosowania normalizacji przewagi (advantage normalization). Oznacz flagą ostrzegawczą każdy proces uczenia ze współczynnikiem `c_e = 0` i entropią polityki spadającą poniżej 0.1 jako utratę zdolności eksploracji (entropy collapse).
