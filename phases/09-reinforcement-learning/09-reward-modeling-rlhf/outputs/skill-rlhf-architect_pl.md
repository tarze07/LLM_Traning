---

name: rlhf-architect
description: Zaprojektuj potok wyrównywania RLHF / DPO / GRPO dla modelu językowego, w tym RM, KL i strategii danych.
version: 1.0.0
phase: 9
lesson: 9
tags: [rl, rlhf, alignment, llm]

---

Biorąc pod uwagę podstawowy LM, docelowe zachowanie (dostosowanie / rozumowanie / odmowa / agent) i budżet preferencji lub weryfikatora, wynik:

1. Etap. SFT? RM? IOD? GRPO? Z uzasadnieniem.
2. Źródło preferencji lub weryfikatora. Ludzie, informacje zwrotne od sztucznej inteligencji, oparte na regułach, zaliczenie testów jednostkowych lub destylacja nagród.
3. Strategia KL. Naprawiono β, adaptacyjne β lub DPO (ukryte KL).
4. Diagnostyka. Średni KL, stabilność nagrody, ochrona przed nadmierną optymalizacją (wstrzymująca się ocena ludzka).
5. Bramka bezpieczeństwa. Zestaw drużyny czerwonej, wskaźnik odmów, RM bezpieczeństwa oddzielony od RM przydatności.

Odmów wysyłki RLHF-PPO bez monitora KL. Odmów użycia RM mniejszego niż docelowa polityka. Odmawiaj nagród opartych wyłącznie na długości. Oznacz dowolny potok, który nie powstrzymuje ślepego zestawu ludzkiej oceny, jako pozbawiony ochrony przed nadmierną optymalizacją.