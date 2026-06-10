---

name: ppo-trainer
description: Utwórz konfigurację szkoleniową PPO i plan diagnostyczny dla danego środowiska.
version: 1.0.0
phase: 9
lesson: 8
tags: [rl, ppo, policy-gradient]

---

Biorąc pod uwagę budżet środowiskowy i szkoleniowy, wynik:

1. Rozmiar wdrożenia. Środowiska `N` × kroki `T`.
2. Aktualizuj harmonogram. Epoki `K`, wielkość minipartii, harmonogram LR.
3. Parametry zastępcze. `ε` (klip), `c_v`, `c_e`, włączona normalizacja przewagi.
4. Przewaga. GAE(`λ`) z wyraźnymi `γ` i `λ`.
5. Plan diagnostyki. KL, ułamek obcięcia, wyjaśnione progi wariancji za pomocą alertów.

Odrzuć `K > 30` lub `ε > 0.3` (niebezpieczny region zaufania). Odmów jakiegokolwiek uruchomienia PPO bez normalizacji przewagi lub monitorowania KL/clip. Frakcja klipu flagowego utrzymywała się powyżej 0,4 jako dryf.