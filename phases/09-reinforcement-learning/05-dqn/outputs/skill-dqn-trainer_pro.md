---

name: dqn-trainer
description: Utwórz konfigurację treningową DQN (bufor powtórek, synchronizacja sieci docelowej, harmonogram ε, przycinanie nagród) dla zadania uczenia ze wzmocnieniem (RL) z dyskretną przestrzenią akcji.
version: 1.0.0
phase: 9
lesson: 5
tags: [rl, dqn, deep-rl]

---

Dla podanego środowiska z dyskretną przestrzenią akcji (wymiar obserwacji, liczba akcji, horyzont czasowy, skala nagrody), wygeneruj:

1. Sieć neuronowa: Architektura (MLP/CNN/Transformer), wymiar cech, głębokość.
2. Bufor powtórek (replay buffer): Pojemność, rozmiar minipaczki (minibatch size), rozmiar fazy rozgrzewkowej (warmup size).
3. Sieć docelowa (target network): Strategia aktualizacji (twarda co C kroków lub miękka z parametrem τ).
4. Eksploracja: Początkowa i docelowa wartość ε oraz czas trwania (harmonogram) jej wygaszania.
5. Funkcja straty: Huber vs MSE, próg przycinania gradientu (gradient clipping), reguły przycinania nagród (reward clipping).
6. Double DQN: Domyślnie włączone, chyba że istnieje istotny powód do jego wyłączenia.

Odrzuć konfigurację DQN bez sieci docelowej, bez bufora powtórek lub z wartością ε stale równą 1. Odrzucaj zadania z ciągłą przestrzenią akcji (przekieruj do SAC / TD3). Oznacz każdy zakres nagród przekraczający 10-krotność średniej wartości na krok jako wymagający przycięcia lub normalizacji skali.
