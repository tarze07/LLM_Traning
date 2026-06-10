---

name: game-rl-designer
description: Zaprojektuj potok uczenia (training pipeline) dla agenta gry RL lub wnioskowania RL (AlphaZero / MuZero / GRPO) w danej domenie.
version: 1.0.0
phase: 9
lesson: 12
tags: [rl, alphazero, muzero, grpo, self-play]

---

Biorąc pod uwagę cel (gra z pełną informacją / z niepełną informacją / Atari / wnioskowanie LLM / problem kombinatoryczny), wygeneruj:

1. Dostosowanie do środowiska: Czy zasady są znane? Czy środowisko jest markowowskie? Stochastyczne? Wieloagentowe? (Wpływa na wybór między AlphaZero, MuZero a GRPO).
2. Strategia przeszukiwania: MCTS (PUCT z aprioryczną wiedzą), próbkowanie Gumbela, best-of-N lub brak przeszukiwania.
3. Schemat gry z samym sobą (self-play): symetryczna gra z samym sobą, liga, dane offline lub dane generowane przez weryfikator.
4. Sygnał celu: wynik gry, nagroda z weryfikatora, preferencje lub wyuczony model nagrody. Dołącz plan zapewnienia stabilności i odporności.
5. Diagnostyka: współczynnik wygranych w porównaniu z poziomem odniesienia (baseline), krzywa ELO, wskaźnik zaliczonych testów weryfikatora, dywergencja KL względem modelu referencyjnego.

Odrzuć AlphaZero w grach z niepełną informacją (zalecane CFR). Odrzuć GRPO bez zaufanego weryfikatora. Odrzuć każdy potok uczenia RL w grach bez ustalonego, bazowego zestawu przeciwników (w przeciwnym razie wskaźnik ELO w grze z samym sobą nie będzie skalibrowany).
