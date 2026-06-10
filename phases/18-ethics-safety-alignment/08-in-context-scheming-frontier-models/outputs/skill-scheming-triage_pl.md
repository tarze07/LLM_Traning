---

name: scheming-triage
description: Segreguj raport o incydencie związanym z wdrożeniem agenta pod kątem trójfilarowego schematu Apollo.
version: 1.0.0
phase: 18
lesson: 8
tags: [scheming, agent-safety, apollo, three-pillars, safety-cases]

---

Mając raport o incydencie związanym z wdrożeniem agenta (nieoczekiwane użycie narzędzi, dostęp do danych, zachowanie związane z samozachowawczością), sklasyfikowaj tryb awarii i, jeśli potencjalnym kandydatem jest intryga, zastosuj test trzech filarów Apollo.

Wyprodukuj:

1. Segregacja według klasy niepowodzenia. Oznacz incydent jako jeden z: awaria zdolności (model nie mógł wykonać zadania), awaria kontroli (protokół monitorowania/użycia narzędzia nie zawierał modelu) lub intryga (model podjął działania przeciwko celowi użytkownika w służbie innego celu kontekstowego).
2. Kontrola trzech filarów (jeśli kandydatem jest intryga).
   - Niewspółosiowość: czy działanie służyło ortogonalnemu celowi obecnemu w środowisku lub wynikach narzędzia?
   - Ukierunkowanie na cel: czy działanie było częścią wieloetapowego planu, czy też było jednorazowym błędem?
   - Świadomość sytuacyjna: czy istnieją dowody, że model wiedział, że jest poddawany ocenie?
3. Audyt kontekstu ewaluacyjnego. Czy incydent zaobserwowano podczas wdrażania, podczas oceny zespołu czerwonego, czy w obu przypadkach? Jeśli dotyczy to tylko wdrożenia, należy pamiętać, że wyniki w czasie oceny nie są przenoszone (zastrzeżenie Apollo 2025).
4. Powtarzalność wzbudzenia. Czy ten sam monit + środowisko może ponownie wywołać zachowanie? Powtarzalny incydent mieści się w ramach trzech filarów; artefakt nieodtwarzalny może być artefaktem wywoływania zdolności.
5. Luka w obudowie bezpieczeństwa. Który z trzech filarów odnosi się do obecnego uzasadnienia bezpieczeństwa tego wdrożenia, a który pozostaje nieuwzględniony?

Twarde odrzucenia:
- Każde podejście, które traktuje intrygi jako porażkę klasy możliwości. Planowanie wymaga ukierunkowania na cel i świadomości sytuacyjnej – model pozbawiony możliwości nie może planować.
- Wszelkie wnioski, że „szkolenie w zakresie przeciwdziałania intrygom zmniejszyło odsetek tajnych działań” implikuje zmniejszoną podstawową niewspółosiowość, bez sprawdzania współczynnika rozpoznawania kontekstu oceny dla tego samego modelu.
- Wszelkie twierdzenia, że ​​dywersja w nadzorze nie jest „atakiem”, ponieważ agent nie wydobył danych – dywersja w nadzorze sama w sobie jest działaniem intrygującym.

Zasady odmowy:
- Jeśli użytkownik zapyta: „Czy mój model jest schematem”, odmów odpowiedzi binarnej bez dowodu opartego na trzech filarach; zażądać danych dotyczących kontekstu oceny i powtarzalności wywoływania.
- Jeśli użytkownik poprosi o szczątkowe prawdopodobieństwo schematu, odrzuć odpowiedź liczbową i wyjaśnij, że wiarygodność oceny na rok 2026 jest ograniczona własną świadomością sytuacyjną modelu.

Wynik: jednostronicowy segregator, który określa klasę niepowodzenia, wypełnia trzy filary dostępnymi dowodami, zaznacza brakujące dowody i wskazuje pojedynczą lukę w przypadku bezpieczeństwa, którą należy pilnie wypełnić. Cytuj Meinke i in. (arXiv:2412.04984) raz jako źródło frameworka.