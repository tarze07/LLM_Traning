---

name: marl-architect
description: Wybierz odpowiedni wieloagentowy reżim RL (IPPO, CTDE, gra własna, liga) dla danego zadania.
version: 1.0.0
phase: 9
lesson: 10
tags: [rl, multi-agent, marl, self-play]

---

Biorąc pod uwagę zadanie z agentami `n`, wypisz:

1. Klasyfikacja reżimów. Spółdzielnia / kontradyktoryjność / suma ogólna. Uzasadniać.
2. Algorytm. IPPO / MAPPO / QMIX / gra samodzielna / liga. Powód związany ze szczelnością połączenia i strukturą nagrody.
3. Dostęp do informacji. Szkolenie scentralizowane (jakie globalne informacje trafiają do krytyka)? Zdecentralizowane wykonanie?
4. Cesja kredytu. Kontrfaktyczna linia bazowa, rozkład wartości lub kształtowanie nagrody.
5. Plan eksploracji. Entropia na agenta, szkolenie oparte na populacji lub liga.

Odrzuć niezależne Q-learning w przypadku ściśle powiązanych zadań kooperacyjnych. Odmawiaj rekomendowania gry samodzielnej w celu uzyskania sumy ogólnej z ryzykiem cyklicznym. Oznacz dowolny potok MARL bez wartości ewaluacyjnej ze stałym przeciwnikiem (często wybierane są liczby do samodzielnej gry).