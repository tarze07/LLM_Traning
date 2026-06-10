---

name: crew-or-flow
description: Wybierz CrewAI Crew lub Flow do danego zadania i przygotuj minimalną implementację.
version: 1.0.0
phase: 14
lesson: 15
tags: [crewai, crews, flows, multi-agent, role-based]

---

Biorąc pod uwagę opis zadania, wybierz Załoga (autonomiczna) lub Przepływ (deterministyczny), a następnie rusztowanie.

Decyzja:

1. Czy zadanie ma wymagania dotyczące SLA, zgodności lub deterministycznego odtwarzania? -> Przepływ.
2. Czy zadanie ma charakter eksploracyjny (badania, pierwszy szkic, burza mózgów)? -> Załoga.
3. Czy zadanie obejmuje ponad 4 specjalistów z zamówieniami wybranymi w ramach LLM? -> Hierarchiczna załoga.
4. Czy zadanie obejmuje załogę sekwencyjną <=3 specialists in a fixed order? -> lub przepływ — preferuj przepływ.

Dla załóg wyprodukuj:

1. Definicje agenta: rola, cel, fabuła (zwarta, <=200 słów), narzędzia.
2. Definicje zadań: opis, oczekiwany_wyjście, agent.
3. Załoga z właściwym procesem (sekwencyjny | hierarchiczny).
4. Wiązka testowa, która uruchamia załogę na przykładowych danych wejściowych i sprawdza, czy generowane są oczekiwane wyniki.

W przypadku przepływów wyprodukuj:

1. Funkcja wejścia `@start`.
2. Kroki `@listen(topic)` tworzące DAG.
3. Wyraźne tematy wydarzeń; żadnej magicznej transmisji.
4. Uprząż powtórkowa: mając ładunek startowy, powtórz deterministycznie.

Twarde odrzucenia:

- Załogi bez historii. Historie są nośne.
- Przepływy bez wyraźnych nazw tematów. „Niejawne łączenie łańcuchowe” mija się z celem kontroli.
- Hierarchiczne załogi składające się z 2 specjalistów. Koszty ogólne menedżera nie stanowią kosztów uzyskania przychodów.

Zasady odmowy:

- Jeśli użytkownik poprosi o załogę do zadania związanego wyłącznie z produktami, odmów i przenieś się do Flow.
- Jeśli użytkownik poprosi o Flow w ramach otwartego zadania badawczego, odmów i migruj do Crew.
- Jeśli historia przekracza 200 słów, odmów i wymagaj przycięcia. Budżet kontekstowy jest ograniczony.

Dane wyjściowe: `agents.py`, `tasks.py`, `crew.py` lub `flow.py` plus `README.md` z uzasadnieniem decyzji. Zakończ słowami „Co przeczytać dalej”, wskazując Lekcję 24 (Langfuse/AgentOps) dla obserwowalności lub Lekcję 13, jeśli Flow wymaga trwałej semantyki wznowienia.