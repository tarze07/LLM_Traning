---

name: ppo-trainer
description: Utwórz konfigurację treningową PPO i plan diagnostyczny dla danego środowiska.
version: 1.0.0
phase: 9
lesson: 8
tags: [rl, ppo, policy-gradient]

---

Uwzględniając budżet środowiska i treningu, wygeneruj:

1. Rozmiar rolloutu (horyzontu próbkowania): `N` środowisk × `T` kroków.
2. Harmonogram aktualizacji: liczba epok `K`, rozmiar minibatcha (minipartii), harmonogram współczynnika uczenia (LR).
3. Parametry funkcji zastępczej (surrogate objective): `ε` (próg obcięcia / clipping), `c_v`, `c_e` oraz status normalizacji przewagi (advantage normalization).
4. Szacowanie przewagi: GAE(`λ`) z jawnymi wartościami `γ` i `λ`.
5. Plan diagnostyki: dywergencja KL, współczynnik obcięcia (clip fraction), progi wyjaśnionej wariancji (explained variance) z alertami.

Odrzuć konfiguracje, gdzie `K > 30` lub `ε > 0.3` (wykraczające poza bezpieczny obszar zaufania / trust region). Odrzuć wszelkie próby uruchomienia PPO bez normalizacji przewagi lub bez monitorowania dywergencji KL / współczynnika obcięcia. Oznacz flagą sytuacje, w których współczynnik obcięcia utrzymuje się powyżej 0,4, co sygnalizuje dryf strategii (policy drift).
