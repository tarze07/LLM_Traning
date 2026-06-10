---
name: orchestration-picker
description: Wybierz topologię orkiestracji (nadzorca, rój, hierarchia, debata lub brak) dla danego problemu i wdróż ją w minimalnej formie.
version: 1.0.0
phase: 14
lesson: 28
tags: [orchestration, supervisor, swarm, hierarchical, debate]
---

Biorąc pod uwagę domenę produktu i klasę zadań, wybierz minimalną topologię.

Decyzja:

1. 1 agent + wzorce przepływu pracy (Lekcja 12) są wystarczające? -> w ogóle nie używaj topologii.
2. 2-4 specjalistów z wyraźnie określonymi obowiązkami? -> **nadzorca-pracownik** (supervisor-worker).
3. Krytyczne opóźnienia, a specjaliści mogą czysto przekazywać zadania? -> **rój** (swarm).
4. Ponad 10 specjalistów, a budżet kontekstu nadzorcy zawodzi? -> **hierarchiczny** (hierarchical).
5. Dokładność liczy się bardziej niż koszty, podejście z wieloma oferentami + krytyką pomaga? -> **debata** (debate) (Lekcja 25).

Wytwórz:

1. Szkielet wybranej topologii.
2. Licznik przeskoków (hop counter) w roju; limit głębokości zagnieżdżenia w hierarchii; limit rund w debacie.
3. Punkty zaczepienia (hooks) dla obserwowalności po każdym przekazaniu lub po każdym kroku (OTel GenAI spans, Lekcja 23).
4. Sekcję "dlaczego to, a nie tamto" w README.

Zdecydowanie odrzucaj:

- Nazywanie 3 wywołań LLM w sekwencji podejściem "wieloagentowym". To jest łańcuchowanie promptów (prompt chain).
- Rój (Swarm) bez licznika przeskoków. Odbijanie zapytań (bouncing) jest pewne.
- Model hierarchiczny z pojedynczym specjalistą na gałąź. Spłaszcz to.

Zasady odmowy:

- Jeśli użytkownik chce rozwiązania wieloagentowego do zadania, z którym radzi sobie pojedyncza pętla ReAct, odmów i zasugeruj Lekcję 01.
- Jeśli użytkownik chce nadzorcy dla zadania 2-krokowego, odmów i zasugeruj łańcuchowanie promptów (Lekcja 12).
- Jeśli domena ma wymagania dotyczące zgodności / audytu, odmów tworzenia roju i zasugeruj nadzorcę lub model hierarchiczny.

Dane wyjściowe: szkielet topologii + README z uzasadnieniem decyzji. Zakończ punktem "co czytać dalej", wskazując na Lekcję 13 (LangGraph) w przypadku implementacji nadzorcy, Lekcję 16 (OpenAI Agents SDK) dla przekazań zadań jako narzędzi, lub Lekcję 25, by poznać szczegóły dotyczące debaty.