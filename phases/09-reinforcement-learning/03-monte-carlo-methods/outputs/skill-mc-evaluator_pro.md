---

name: mc-evaluator
description: Oceń politykę (policy evaluation) za pomocą metody Monte Carlo i sporządź raport zbieżności, porównując wyniki z programowaniem dynamicznym (DP), jeśli jest dostępne.
version: 1.0.0
phase: 9
lesson: 3
tags: [rl, monte-carlo, evaluation]

---

Biorąc pod uwagę środowisko (epizodyczne, z interfejsem API typu reset/step) oraz politykę, wygeneruj:

1. Metoda. Estymacja Monte Carlo oparta na pierwszej wizycie (First-visit MC) kontra na każdej wizycie (Every-visit MC). Podaj uzasadnienie wyboru.
2. Budżet epizodów. Docelowa liczba epizodów, diagnostyka wariancji, oczekiwany błąd standardowy (standard error).
3. Plan eksploracji. Harmonogram parametru epsilon (ε-greedy) lub technika Exploring Starts (startów eksploracyjnych).
4. Porównanie z punktem odniesienia (Golden Standard). Wartość V* z programowania dynamicznego (DP) dla problemów tabelarycznych; w innych przypadkach porównanie z wynikami algorytmów Q-learning / PPO.
5. Kontrola zakończenia epizodu. Limit maksymalnej liczby kroków (cutoff), limity czasu (timeouts), obsługa nieskończonych trajektorii.

Odrzuć stosowanie metod Monte Carlo w zadaniach nieepizodycznych bez zdefiniowanego skończonego horyzontu czasowego. Odrzuć szacunki wartości stanów V^π wyznaczone na podstawie mniej niż 100 epizodów na stan w przypadku środowisk tabelarycznych. Oznacz flagą ostrzegawczą polityki deterministyczne (o zerowej wariancji działań) ze względu na ryzyko braku eksploracji.
