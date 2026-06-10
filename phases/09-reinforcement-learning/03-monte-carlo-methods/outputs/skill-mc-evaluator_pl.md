---

name: mc-evaluator
description: Oceń politykę poprzez wdrożenie Monte Carlo i sporządź raport konwergencji z porównaniem DP, jeśli jest dostępny.
version: 1.0.0
phase: 9
lesson: 3
tags: [rl, monte-carlo, evaluation]

---

Biorąc pod uwagę środowisko (epizodyczne, z interfejsem API resetowania + krok) i politykę, wynik:

1. Metoda. Pierwsza wizyta vs każda wizyta MC. Powód.
2. Budżet odcinka. Liczba docelowa, diagnostyka wariancji, oczekiwany błąd standardowy.
3. Plan eksploracji. ε harmonogram (w razie potrzeby) lub rozpoczęcie zwiedzania.
4. Porównanie złotego standardu. DP-optymalne V*, jeśli tabelaryczne; w przeciwnym razie związane z punktem odniesienia Q-learning / PPO.
5. Kontrola zakończenia. Limit maksymalnego kroku, limity czasu, obsługa niekończących się trajektorii.

Odmawiaj prowadzenia MC w przypadku nieepizodycznych zadań bez ograniczonego horyzontu czasowego. Odmów podawania szacunków V^π dla mniej niż 100 odcinków na stan w przypadku zadań tabelarycznych. Oznacz dowolną politykę z działaniami o zerowej wariancji jako ryzyko eksploracyjne.