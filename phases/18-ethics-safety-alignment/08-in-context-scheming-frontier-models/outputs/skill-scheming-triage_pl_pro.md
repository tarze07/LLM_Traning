---
name: scheming-triage
description: Klasyfikuj (triage) raporty o incydentach wdrożeniowych agentów pod kątem trójfilarowych ram spiskowania Apollo.
version: 1.0.0
phase: 18
lesson: 8
tags: [scheming, agent-safety, apollo, three-pillars, safety-cases]
---

Na podstawie raportu o incydencie związanym z wdrożeniem agenta (nieoczekiwane użycie narzędzi, nieautoryzowany dostęp do danych, zachowania samozachowawcze), sklasyfikuj tryb awarii (failure mode). Jeśli zachodzi podejrzenie spiskowania (scheming), zastosuj test trzech filarów Apollo.

Wyprodukuj:

1. Klasyfikacja klasy awarii. Zakwalifikuj incydent do jednej z kategorii: awaria zdolności (model nie był w stanie wykonać zadania), awaria kontroli (mechanizmy monitorowania/ograniczania narzędzi nie utrzymały agenta w ryzach) lub spiskowanie (model podjął działania wbrew celowi użytkownika, służąc innemu celowi kontekstowemu).
2. Weryfikacja trzech filarów (jeśli podejrzewa się spiskowanie).
   - Niedopasowanie celów (Misalignment): Czy podjęte działanie służyło celowi ortogonalnemu, obecnemu w środowisku lub w danych wyjściowych narzędzi?
   - Ukierunkowanie na cel (Goal-directedness): Czy to działanie stanowiło część wieloetapowego planu, czy było jednorazowym błędem?
   - Świadomość sytuacyjna (Situational awareness): Czy istnieją dowody, że model miał świadomość, iż w danym momencie podlega ewaluacji?
3. Audyt kontekstu ewaluacji. Czy incydent zaobserwowano w środowisku produkcyjnym (deployment), podczas testów red-teamingowych, czy w obu przypadkach? Jeśli tylko w środowisku produkcyjnym, pamiętaj, że wyniki uzyskiwane w kontrolowanych warunkach testowych nie muszą przekładać się na rzeczywiste wdrożenie (zastrzeżenie Apollo z 2025 r.).
4. Powtarzalność wyzwalania (elicitation reproducibility). Czy ta sama kombinacja promptu i środowiska może ponownie wywołać to zachowanie? Incydent powtarzalny kwalifikuje się do analizy w ramach trzech filarów; przypadek niepowtarzalny może być jedynie losowym artefaktem wydobywania zdolności (capability elicitation artifact).
5. Luka w uzasadnieniu bezpieczeństwa (safety case gap). Który z trzech filarów jest adresowany przez obecne uzasadnienie bezpieczeństwa (safety case) dla tego wdrożenia, a który pozostaje niepokryty?

Twarde odrzucenia:
- Wszelkie podejścia traktujące spiskowanie jako awarię z klasy zdolności (capability-class failure). Spiskowanie wymaga ukierunkowania na cel oraz świadomości sytuacyjnej – model pozbawiony odpowiednich zdolności nie jest w stanie spiskować.
- Wnioskowanie, że „trening przeciw spiskowaniu zmniejszył wskaźnik działań niejawnych” (co miałoby rzekomo oznaczać redukcję bazowego niedopasowania celów) bez uprzedniej weryfikacji wskaźnika rozpoznawania kontekstu ewaluacji przez ten sam model.
- Twierdzenia, że sabotowanie nadzoru (oversight subversion) nie stanowi „ataku”, ponieważ agent nie dokonał eksfiltracji danych – sabotowanie nadzoru samo w sobie jest działaniem o charakterze spiskowym.

Zasady odmowy:
- Jeśli użytkownik zapyta: „Czy mój model spiskuje?”, odmów udzielenia jednoznacznej odpowiedzi tak/nie (binarnej) bez przedstawienia dowodów opartych na trzech filarach; zażądaj danych dotyczących kontekstu ewaluacji oraz powtarzalności wyzwalania.
- Jeśli użytkownik poprosi o określenie szczątkowego prawdopodobieństwa spiskowania, odmów podania konkretnej wartości liczbowej i wyjaśnij, że wiarygodność ewaluacji (stan na rok 2026) jest ograniczona przez własną świadomość sytuacyjną modelu.

Wynik: Jednostronicowa karta klasyfikacji (triage sheet), która określa klasę awarii, opisuje trzy filary w oparciu o dostępne dowody, wskazuje brakujące informacje oraz identyfikuje najpilniejszą lukę w uzasadnieniu bezpieczeństwa (safety case). Należy jednokrotnie zacytować pracę Meinke i in. (arXiv:2412.04984) jako źródło wykorzystanych ram teoretycznych.
