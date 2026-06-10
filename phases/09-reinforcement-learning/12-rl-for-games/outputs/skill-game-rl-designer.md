---

name: game-rl-designer
description: Design an RL game or RL reasoning training pipeline (AlphaZero / MuZero / GRPO) for a given domain.
version: 1.0.0
phase: 9
lesson: 12
tags: [rl, alphazero, muzero, grpo, self-play]

---

Given the goal (perfect information game / imperfect information / Atari / LLM reasoning / combinatorial), output:

1. Environment fit. Known rules? Markov? Stochastic? Multi-agent? Informs AlphaZero vs MuZero vs GRPO.
2. Search strategy. MCTS (PUCT with prior learned knowledge), Gumbel sample, best-of-N, or none.
3. Self-play plan. Symmetric self-play data / league / offline / verifier-generated.
4. Objective signal. Game score / verifier reward / preferences / learned model. Include a robustness plan.
5. Diagnostics. Win rate against baseline, ELO curve, verifier pass rate, KL to reference.

Reject AlphaZero for imperfect information games (route to CFR). Reject GRPO without a trusted verifier. Reject any RL game pipeline without a fixed baseline set of opponents (otherwise self-play ELO is uncalibrated).
