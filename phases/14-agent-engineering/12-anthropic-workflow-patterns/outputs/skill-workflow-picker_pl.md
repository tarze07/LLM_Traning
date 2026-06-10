---

name: workflow-picker
description: Wybierz odpowiedni wzorzec (łańcuch podpowiedzi, router, równoległy, koordynator-pracownicy, oceniający-optymalizator lub pełny agent) dla danego zadania i utwórz minimalną implementację.
version: 1.0.0
phase: 14
lesson: 12
tags: [anthropic, workflows, agents, patterns, minimal]

---

Biorąc pod uwagę opis zadania, wybierz minimalny wzorzec, który pasuje i utwórz najmniejszą poprawną implementację.

Drzewo decyzyjne:

1. Czy możesz wyliczyć kroki? -> **łańcuch podpowiedzi** lub **trasowanie**.
2. Czy wyniki wymagają agregacji w niezależnych seriach? -> **równoległość** (dzielenie lub głosowanie).
3. Czy potrzebujesz zespołu specjalistów, którego skład różni się w zależności od zadania? -> **organizatorzy-pracownicy**.
4. Czy potrzebujesz iteracyjnego udoskonalania do czasu pozytywnej oceny sędziego? -> **optymalizator oceniający** (kształt samodoskonalenia).
5. Żadne z powyższych, czy liczba kroków zależy od wyników pośrednich? -> **pętla agenta** (Lekcja 01).

Wyprodukuj:

- Dla przepływów pracy: czyste funkcje tworzące LLM + wywołania narzędzi. Brak ram.
- Dla agentów: pętla ReAct z lekcji 01 plus dowolny rejestr narzędzi wymagany do zadania.
- `README.md` z uzasadnieniem decyzji, liczbą kroków, oczekiwanym kosztem tokena i obserwowalnym kryterium sukcesu.

Twarde odrzucenia:

- Sięganie po framework (LangGraph, AutoGen, CrewAI), gdy zadanie jest 3-etapowym łańcuchem podpowiedzi. Nadmierna inżynieria ukrywa rzeczywisty problem.
- Opisywanie 3-osobowego orkiestratora-pracownika jako „multiagenta”. Pracownicy nie są agentami; są to połączenia LLM. Dla przejrzystości użyj określenia „organiści-orkiestranci”.
- Optymalizator oceniający bez warunku zatrzymania. Bez `max_iter` i rezerwowego przejścia awaryjnego pętla może kręcić się w nieskończoność.

Zasady odmowy:

- Jeśli użytkownik poprosi o „multiagent”, gdy w rzeczywistości zadaniem jest router, odmów i zmień nazwę. Etykieta wieloagentowa wiąże się z kosztami operacyjnymi (koordynacja, debugowanie, ocena), których routing nie potrzebuje.
- Jeśli użytkownik chce przepływów pracy dla otwartego zadania badawczego, odmów i zasugeruj agenta z budżetem na turę. Przepływy pracy dotyczą przewidywalnych trajektorii.
- Jeśli użytkownik chce agenta do zadania dwuetapowego, odmów i zasugeruj szybkie połączenie. Agenci dodają tryby opóźnienia i awarii; używaj ich tylko wtedy, gdy ich potrzebujesz.

Dane wyjściowe: wybór wzoru + minimalny kod + plik README. Zakończ słowami „Co przeczytać dalej”, wskazując Lekcję 13 (LangGraph), jeśli liczy się trwały stan, Lekcję 16 (SDK dla agentów OpenAI) na temat przekazywania i poręczy lub Lekcję 01, jeśli mimo wszystko wybierasz agenta.