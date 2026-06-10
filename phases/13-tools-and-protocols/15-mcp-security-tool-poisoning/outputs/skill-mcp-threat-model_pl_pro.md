---

name: mcp-threat-model
description: Utwórz model zagrożeń dla wdrożenia MCP, określając istotne klasy ataków, stosowane zabezpieczenia oraz naruszenia reguły dwóch.
version: 1.0.0
phase: 13
lesson: 15
tags: [mcp, security, tool-poisoning, threat-model, rule-of-two]

---

Na podstawie opisu wdrożenia MCP (lista serwerów, lista narzędzi, lista uprawnień) opracuj model zagrożeń.

Wygeneruj następujące sekcje:

1. Możliwość zastosowania ataków. Dla każdej z siedmiu klas ataków (zatrucie narzędzi, ciągnięcie dywanika [rug pull], cieniowanie, MPMA, pasożytniczy łańcuch narzędzi, ataki próbkujące, maskarada w łańcuchu dostaw) oceń stopień ryzyka jako wysoki/średni/niski, podając jednozdaniowe uzasadnienie.
2. Inwentarz zabezpieczeń. Lista wdrożonych środków ochrony (przypinanie skrótów [hash pinning], detekcja statyczna, brama sieciowa, podpisany rejestr, MELON, egzekwowanie reguły dwóch).
3. Audyt reguły dwóch. Każde narzędzie należy sklasyfikować jako niezaufane, wrażliwe lub wtórne, a także zidentyfikować przypadki, w których dochodzi do jednoczesnego wystąpienia tych trzech cech w jednej turze interakcji.
4. Brakujące zabezpieczenia. Wskaż najbardziej skuteczną metodę ochrony, która nie została jeszcze wdrożona, biorąc pod uwagę profil zagrożeń.
5. Instrukcja operacyjna (Runbook). Trzy konkretne działania, które zespół powinien podjąć w nadchodzącym tygodniu w celu poprawy poziomu bezpieczeństwa.

Kategoryczne odrzucenia:
- Dowolny model zagrożeń zawierający stwierdzenie: „klasa ataku X nie ma zastosowania, ponieważ ufamy temu serwerowi”. Należy założyć scenariusz, w którym co najmniej jeden serwer zostaje przejęty.
- Każde wdrożenie wykorzystujące rozwiązywanie przestrzeni nazw z cichym nadpisywaniem.
- Każde wdrożenie z włączonym próbkowaniem, ale bez limitu częstotliwości żądań (rate limiter) dla sesji.

Reguły odmowy:
- Jeśli wdrożenie nie posiada udokumentowanych i zatwierdzonych opisów narzędzi, odrzuć projekt i nakaż wdrożenie przypinania skrótów (hash pinning).
- Jeśli we wdrożeniu wykorzystywane są publiczne, niepodpisane rejestry MCP, wskaż ryzyko związane z łańcuchem dostaw i zalecaj migrację do zweryfikowanego rejestru.
- Jeśli jakiekolwiek narzędzie łączy w sobie niezaufane dane wejściowe, wrażliwe dane oraz wywoływane przez nie akcje, odmów zatwierdzenia i zażądaj podziału tych funkcji.

Format wyjściowy: Jednostronicowy model zagrożeń zawierający tabelę podatności na ataki, inwentarz zabezpieczeń, listę naruszeń reguły dwóch oraz runbook z trzema konkretnymi działaniami. Na końcu umieść jedno dodatkowe zabezpieczenie o najwyższym priorytecie dla tego wdrożenia.
