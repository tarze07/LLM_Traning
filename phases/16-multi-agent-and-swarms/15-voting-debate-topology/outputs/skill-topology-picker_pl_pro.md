---

name: topology-picker
description: Wybierz topologię debaty wieloagentowej (gwiazda, łańcuch, drzewo, graf), określ liczbę agentów (N), profil heterogeniczności oraz limity rund dla wybranego zadania.
version: 1.0.0
phase: 16
lesson: 15
tags: [multi-agent, debate, topology, voting, self-consistency]

---

Na podstawie opisu zadania, zarekomenduj optymalną topologię komunikacji oraz liczbę agentów w zespole.

Opracuj:

1. **Profil (odcisk palca) zadania.** Do wyboru: badania (research — szeroki zakres, otwarte), szybkie fakty (zapytanie zamknięte), sekwencyjne ulepszanie (potok iteracyjny) lub opinie (brak obiektywnej prawdy). Jeśli zadanie łączy w sobie dwa profile, wskaż profil dominujący.
2. **Topologia.** Gwiazda (Star), łańcuch (Chain), drzewo (Tree) lub graf (Graph). Uzasadnij swój wybór na podstawie profilu zadania:
   - badania (research) → graf (swobodna krytyka każdy z każdym)
   - szybkie fakty → gwiazda (agregacja przez węzeł centralny)
   - sekwencyjne ulepszanie → łańcuch (lub drzewo w przypadku strategii „dziel i rządź”)
   - opinie → brak (w tym przypadku zaleca się pojedynczego agenta i ostateczną decyzję człowieka)
3. **Liczba agentów (N).** Zespół 3 agentów to najbardziej ekonomiczny wariant; 5 agentów to zazwyczaj złoty środek; 7 lub więcej to warianty specjalistyczne. Ostrzegaj przed narzutem (podatkiem) koordynacyjnym przy N > 5 w topologii grafu.
4. **Profil heterogeniczności.** W zadaniach wymagających głębokiego rozumowania lub badań co najmniej jeden agent musi korzystać z innej rodziny modeli bazowych (w celu uniknięcia monokultury). Dla N=5 rekomenduje się użycie 3 różnych modeli bazowych.
5. **Limit rund.** 1 runda to proste głosowanie. 2 rundy pozwalają na jednokrotną korektę. 3 rundy to maksimum, zanim zacznie dominować konformizm. Nigdy nie stosuj rund nieograniczonych.
6. **Agregacja wyników.** Głosowanie większościowe (tanie), ważone zaufaniem (CP-WBFT, Lekcja 14), mediana geometryczna (DecentLLM) lub ocena przez dedykowanego sędziego. Domyślnym wyborem powinno być głosowanie ważone zaufaniem, chyba że ograniczenia budżetowe wymuszają zwykłe głosowanie większościowe.
7. **Procedura eskalacji.** Wskazanie ścieżki działania, gdy stopień zgodności spadnie poniżej progu: eskalacja do operatora (człowiek), przekazanie do alternatywnego zespołu opartego na innych modelach, czy wstrzymanie się od decyzji.

Kryteria wykluczające:

- Rekomendowanie ponad 10 agentów w topologii grafu (narzut koordynacyjny drastycznie obniża wydajność).
- Topologia gwiazdy (Star) w zadaniach badawczych (wyklucza to swobodną wymianę argumentów każdy z każdym).
- Uruchamianie tego samego modelu bazowego N razy i nazywanie tego systemem wieloagentowym. Jest to samospójność (Self-Consistency) i powinno być tak nazwane.
- Pozwalanie na nieograniczoną liczbę rund dyskusji (promuje to konformizm; wraz z czasem trwania debaty agenty zgadzają się pod wpływem presji, a nie logicznych argumentów).

Zasady odmowy (Rejection rules):

- Jeśli zadanie nie posiada obiektywnej prawdy (opinie, syntezy, kreacja), oznacz głosowanie jako doradcze i zarekomenduj pojedynczego agenta wspieranego decyzją człowieka.
- Jeśli użytkownik nie ma dostępu do różnych modeli bazowych, wskaż ograniczenia monokultury, a jako rozwiązanie rezerwowe zaleć samospójność ze zmienną temperaturą.
- Jeśli zadanie jest proste (krótkie weryfikacje, prosty proces wnioskowania), zaleć pojedynczego agenta ze spójnością wewnętrzną przy N=5.

Format wyjściowy: jednostronicowy opis architektury. Rozpocznij od jednozdaniowej rekomendacji (np. „Topologia grafu, N=5 agentów z 3 różnych modeli bazowych, 2 rundy, agregacja ważona zaufaniem, eskalacja do operatora w przypadku braku konsensusu”), po której następuje siedem opisanych wyżej sekcji. Zakończ szacunkowym budżetem (oczekiwana liczba tokenów na zapytanie oraz opóźnienie w sekundach).
