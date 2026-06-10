---

name: dqn-trainer
description: Utwórz konfigurację szkoleniową DQN (bufor, synchronizacja celu, harmonogram ε, przycinanie nagrody) dla zadania RL o działaniu dyskretnym.
version: 1.0.0
phase: 9
lesson: 5
tags: [rl, dqn, deep-rl]

---

Biorąc pod uwagę środowisko działań dyskretnych (kształt obserwacji, liczba działań, horyzont, skala nagrody), wynik:

1. Sieć. Architektura (MLP/CNN/Transformer), cecha przyciemnienia, głębia.
2. Bufor odtwarzania. Pojemność, wielkość minipartii, wielkość rozgrzewki.
3. Sieć docelowa. Strategia synchronizacji (twarda co C kroków lub miękka τ).
4. Eksploracja. ε początek / koniec / długość harmonogramu.
5. Strata. Huber vs MSE, wartość obcinania gradientu, reguła obcinania nagrody.
6. Podwójne DQN. Domyślnie włączone, chyba że jest wyraźny powód wyłączenia.

Odmów wysłania DQN bez sieci docelowej, bez bufora odtwarzania lub ε utrzymywanego na poziomie 1. Odmawiaj zadań o działaniu ciągłym (trasa do SAC / TD3). Oznacz dowolny zakres nagród > 10× średniej na krok jako wymagający przycięcia lub normalizacji skali.