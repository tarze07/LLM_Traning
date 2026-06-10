---

name: policy-gradient-trainer
description: Skonfiguruj proces uczenia za pomocą metod gradientu polityki (REINFORCE / Actor-Critic / PPO) dla zadanego środowiska i zdiagnozuj problemy z wysoką wariancją.
version: 1.0.0
phase: 9
lesson: 6
tags: [rl, policy-gradient, reinforce]

---

Biorąc pod uwagę specyfikację środowiska (dyskretne/ciągłe akcje, horyzont czasowy, statystyki nagród), wygeneruj:

1. Głowica polityki (Policy Head). Rozkład Softmax (dla akcji dyskretnych) lub rozkład Gaussa (dla akcji ciągłych) wraz z określeniem liczby parametrów.
2. Linia odniesienia (Baseline). Brak (standardowy REINFORCE), średnia ruchoma, wyuczony krytyk `V̂(s)` lub architektura A2C.
3. Kontrola wariancji. Domyślnie włączone sumowanie zdyskontowanych nagród (reward-to-go), normalizacja stóp zwrotu (returns normalization), wartość przycinania gradientu (gradient clipping).
4. Regularyzacja entropią. Współczynnik entropii β oraz harmonogram jego stopniowego zmniejszania (decay schedule).
5. Rozmiar wsadu (Batch Size). Liczba epizodów na jedną aktualizację wag; wymagania dotyczące aktualności danych (on-policy).

Odrzuć stosowanie algorytmu REINFORCE bez linii odniesienia (baseline) przy horyzoncie czasowym > 500 kroków. Odrzuć projekty sterowania ciągłego (continuous control) wykorzystujące głowicę softmax. Oznacz flagą ostrzegawczą każdy proces uczenia z parametrem `β = 0` i entropią polityki spadającą poniżej 0.1 jako utratę zdolności eksploracji (entropy collapse).
