---

name: actor-critic-trainer
description: Utwórz konfigurację A2C / A3C / GAE dla danego środowiska, podając oszacowanie korzyści i wagi strat.
version: 1.0.0
phase: 9
lesson: 7
tags: [rl, actor-critic, gae]

---

Biorąc pod uwagę środowisko i budżet obliczeniowy, wynik:

1. Równoległość. A2C (wsadowo GPU) vs A3C (asynchronizacja procesora) i liczba procesów roboczych.
2. Długość wdrożenia T. Liczba kroków na środowisko na aktualizację.
3. Estymator przewagi. n-etapowy lub GAE(λ); określ λ.
4. Wagi strat. `c_v` (wartość), `c_e` (entropia), klip gradientowy.
5. Szybkość uczenia się. Aktor i krytyk (oddzielnie, jeśli używasz).

Odrzuć A2C dla jednego pracownika w środowiskach z horyzontem> 1000 (zbyt zgodnie z zasadami, zbyt wolno). Odmów wysyłki bez normalizacji korzyści. Oznacz dowolny przebieg za pomocą `c_e = 0` i zaobserwowaną entropię < 0,1 jako załamanie entropii.