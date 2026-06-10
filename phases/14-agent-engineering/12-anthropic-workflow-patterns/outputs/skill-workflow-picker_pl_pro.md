---

name: workflow-picker
description: Wybierz odpowiedni wzorzec (łańcuch podpowiedzi, router, równoległość, koordynator-pracownicy, ewaluator-optymalizator lub pełny agent) dla danego zadania i wygeneruj jego minimalną implementację.
version: 1.0.0
phase: 14
lesson: 12
tags: [anthropic, workflows, agents, patterns, minimal]

---

Na podstawie opisu zadania dobierz najbardziej minimalistyczny pasujący wzorzec i wygeneruj jego najprostszą poprawną implementację.

Drzewo decyzyjne:

1. Czy potrafisz z góry określić wszystkie kroki? -> Wybierz łączenie w łańcuchy (prompt chaining) lub routing.
2. Czy zadanie wymaga niezależnego generowania wyników i ich późniejszej agregacji? -> Wybierz równoległość (parallelization - podział zadań lub głosowanie).
3. Czy potrzebujesz zespołu specjalistów, których skład i zadania zależą od specyfiki zapytania? -> Wybierz koordynator-pracownicy (orchestrator-workers).
4. Czy potrzebujesz iteracyjnego poprawiania kodu/tekstu do momentu przejścia walidacji? -> Wybierz ewaluator-optymalizator (evaluator-optimizer).
5. Żadne z powyższych, a liczba kroków zależy dynamicznie od wyników pośrednich? -> Wybierz pełną pętlę agenta (Lekcja 01).

Wygeneruj:

- Dla przepływów pracy: czyste funkcje w Pythonie wykonujące wywołania LLM i narzędzi. Bez zbędnych frameworków.
- Dla agentów: pętlę ReAct z Lekcji 01 wraz z rejestrem narzędzi niezbędnych do wykonania zadania.
- Plik `README.md` zawierający uzasadnienie wyboru, liczbę kroków, szacowany koszt tokenów oraz mierzalne kryterium sukcesu.

Kryteria odrzucenia (Hard rejects):

- Sięganie po rozbudowany framework (np. LangGraph, AutoGen, CrewAI) w sytuacji, gdy zadanie sprowadza się do 3-etapowego łańcucha podpowiedzi. Nadmierna inżynieria (overengineering) zaciemnia rzeczywisty problem.
- Opisywanie prostego schematu orkiestrator-pracownicy z trzema modelami jako systemu „wieloagentowego”. Pracownicy w tym wzorcu nie są autonomicznymi agentami, lecz synchronicznymi wywołaniami LLM. Dla przejrzystości stosuj nazwę „orkiestrator-pracownicy”.
- Implementacja wzorca ewaluator-optymalizator bez zdefiniowanego warunku zakończenia. Bez określenia `max_iter` i mechanizmu awaryjnego pętla może działać w nieskończoność, generując niekontrolowane koszty.

Zasady odmowy (Guardrails):

- Jeśli użytkownik żąda architektury wieloagentowej („multi-agent”) dla problemu, który w rzeczywistości wymaga jedynie zwykłego routera, odmów i skoryguj nazewnictwo. Podejście wieloagentowe wiąże się z wysokim narzutem operacyjnym (koordynacja, debugowanie, testowanie), który przy prostym routingu jest całkowicie zbędny.
- Jeśli użytkownik próbuje wdrożyć statyczny przepływ pracy do otwartego zadania badawczego, odmów i zaproponuj pełnego agenta z określonym budżetem na liczbę kroków (interakcji). Przepływy pracy sprawdzają się wyłącznie przy przewidywalnych ścieżkach.
- Jeśli użytkownik chce zastosować agenta do prostego, dwuetapowego zadania, odmów i zaproponuj proste łączenie promptów w łańcuch. Pętle agentowe zwiększają opóźnienia i wprowadzają nowe punkty awarii; należy ich używać tylko wtedy, gdy są naprawdę konieczne.

Wygenerowana struktura: wybór wzorca, minimalny kod oraz plik `README.md`. Zakończ sekcją „Co czytać dalej”, odsyłając do Lekcji 13 (LangGraph – jeśli kluczowe znaczenie ma trwały stan), Lekcji 16 (OpenAI Agents SDK – w temacie przekazywania zadań i guardrails) lub Lekcji 01 (jeśli ostatecznie konieczne jest zastosowanie agenta).
