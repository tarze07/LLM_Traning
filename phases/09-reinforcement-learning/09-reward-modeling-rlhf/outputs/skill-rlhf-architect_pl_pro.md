---

name: rlhf-architect
description: Zaprojektuj potok dopasowania (alignment) RLHF / DPO / GRPO dla modelu językowego, w tym model nagrody (RM), dywergencję KL i strategię danych.
version: 1.0.0
phase: 9
lesson: 9
tags: [rl, rlhf, alignment, llm]

---

Na podstawie modelu bazowego (base LM), docelowego zachowania (dopasowanie / rozumowanie / odmowa / zachowanie agentowe) oraz budżetu preferencji lub weryfikatora, wygeneruj:

1. Etapy: SFT? RM? IOD? GRPO? Wraz z uzasadnieniem.
2. Źródło preferencji lub weryfikatora: ocena ludzka, informacje zwrotne od sztucznej inteligencji (RLAIF), oparte na regułach, zaliczenie testów jednostkowych lub destylacja nagrody.
3. Strategia KL: stała β, adaptacyjna β lub DPO (niejawna dywergencja KL).
4. Diagnostyka: średnia wartość KL, stabilność nagrody, ochrona przed nadmierną optymalizacją (wydzielony zestaw do oceny przez ludzi).
5. Bramki bezpieczeństwa: zestaw testowy red-teamingu, wskaźnik odmów, model nagrody (RM) dla bezpieczeństwa oddzielony od RM dla użyteczności.

Odrzuć wdrożenie RLHF-PPO bez monitorowania KL. Odrzuć użycie modelu nagrody (RM) mniejszego niż docelowa polityka (policy). Odrzuć nagrody oparte wyłącznie na długości odpowiedzi. Oznacz dowolny potok, który nie wykorzystuje wydzielonego (ślepego) zestawu do oceny przez ludzi, jako pozbawiony ochrony przed nadmierną optymalizacją.
