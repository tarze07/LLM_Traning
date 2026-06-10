---

name: game-rl-designer
description: Zaprojektuj potok szkoleniowy gry RL lub rozumowania RL (AlphaZero / MuZero / GRPO) dla danej domeny.
version: 1.0.0
phase: 9
lesson: 12
tags: [rl, alphazero, muzero, grpo, self-play]

---

Biorąc pod uwagę cel (gra o doskonałych informacjach / informacje niedoskonałe / Atari / rozumowanie LLM / kombinatoryczne), wynik:

1. Dopasowanie do środowiska. Znane zasady? Markow? Stochastyczny? Wielu agentów? Informuje AlphaZero vs MuZero vs GRPO.
2. Strategia wyszukiwania. MCTS (PUCT z wcześniej wyuczoną wiedzą), próbka Gumbela, najlepsza z N lub żadna.
3. Plan samodzielnej zabawy. Symetryczne dane dotyczące gry własnej / ligi / offline / wygenerowane przez weryfikatora.
4. Sygnał celu. Wynik gry / nagroda weryfikatora / preferencje / wyuczony model. Dołącz plan odporności.
5. Diagnostyka. Współczynnik wygranych w porównaniu z wartością bazową, krzywa ELO, współczynnik zaliczania weryfikatorów, KL do odniesienia.

Odrzuć AlphaZero w grach z niedoskonałymi informacjami (droga do CFR). Odrzuć GRPO bez zaufanego weryfikatora. Odrzuć jakikolwiek potok RL gry bez ustalonego podstawowego zestawu przeciwników (w przeciwnym razie ELO w grze samodzielnej nie jest skalibrowane).