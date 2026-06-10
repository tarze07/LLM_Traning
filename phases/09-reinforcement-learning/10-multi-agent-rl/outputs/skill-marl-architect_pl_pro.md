---

name: marl-architect
description: Wybierz odpowiedni wieloagentowy schemat RL (IPPO, CTDE, gra z samym sobą, liga) dla danego zadania.
version: 1.0.0
phase: 9
lesson: 10
tags: [rl, multi-agent, marl, self-play]

---

Dla zadania z liczbą agentów `n`, określ:

1. Klasyfikacja środowiska: kooperacja, rywalizacja lub gra o sumie niezerowej. Wraz z uzasadnieniem.
2. Algorytm: IPPO / MAPPO / QMIX / gra z samym sobą (self-play) / liga. Uzasadnienie oparte na stopniu powiązania agentów (coupling) i strukturze nagród.
3. Przepływ informacji: scentralizowane uczenie (jakie globalne informacje trafiają do krytyka) i zdecentralizowane działanie (execution) (CTDE)?
4. Przypisywanie zasług (credit assignment): kontrfaktyczny stan odniesienia (counterfactual baseline), dekompozycja wartości lub kształtowanie nagrody.
5. Strategia eksploracji: entropia na poziomie agenta, uczenie oparte na populacji lub liga.

Odrzuć niezależne uczenie Q-learning (Independent Q-learning) w przypadku ściśle powiązanych zadań kooperacyjnych. Odrzuć rekomendowanie gry z samym sobą (self-play) w grach o sumie niezerowej z ryzykiem wystąpienia zależności cyklicznych. Oznacz każdy potok MARL bez ewaluacji wobec stałego przeciwnika jako podatny na cykle decyzyjne.
