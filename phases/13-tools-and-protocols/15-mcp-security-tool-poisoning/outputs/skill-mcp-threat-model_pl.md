---

name: mcp-threat-model
description: Utwórz model zagrożenia dla wdrożenia MCP, podając odpowiednie klasy ataku, stosowane zabezpieczenia i naruszenia zasady dwóch.
version: 1.0.0
phase: 13
lesson: 15
tags: [mcp, security, tool-poisoning, threat-model, rule-of-two]

---

Biorąc pod uwagę wdrożenie MCP (lista serwerów, lista narzędzi, lista uprawnień), utwórz model zagrożenia.

Wyprodukuj:

1. Możliwość zastosowania ataku. Dla każdej z siedmiu klas ataków (zatrucie narzędzi, ciągnięcie dywanika, cieniowanie, MPMA, pasożytniczy łańcuch narzędzi, ataki próbkujące, maskarada w łańcuchu dostaw) oceń możliwość zastosowania jako wysoką/średnią/niską z uzasadnieniem w jednym zdaniu.
2. Inwentarz obronny. Lista zabezpieczeń już istniejących (przypinanie skrótu, detektor statyczny, brama, podpisany rejestr, MELON, egzekwowanie zasady dwóch).
3. Audyt Zasada Dwóch. Każde narzędzie należy sklasyfikować jako niezaufane / wrażliwe / wtórne i oznaczyć dowolną kombinację wszystkich trzech w jednej turze.
4. Brakująca obrona. Wymień najskuteczniejszą ochronę, która nie została jeszcze zastosowana, biorąc pod uwagę profil zagrożenia.
5. Element Runbook. Trzy działania, które zespół powinien podjąć w następnym tygodniu, aby poprawić stan bezpieczeństwa.

Twarde odrzucenia:
- Dowolny model zagrożenia, który mówi „klasa ataku X nie ma zastosowania, ponieważ ufamy temu serwerowi”. Załóżmy, że jeden serwer zostanie naruszony.
— Każde wdrożenie korzystające z rozpoznawania przestrzeni nazw z cichym nadpisywaniem.
- Każde wdrożenie z włączonym próbkowaniem, ale bez ogranicznika szybkości sesji.

Zasady odmowy:
- Jeśli wdrożenie nie zawiera dokumentacji zatwierdzonych opisów narzędzi, najpierw odmów i nakaż przypinanie skrótu.
- Jeśli we wdrożeniu wykorzystywane są publiczne niepodpisane rejestry MCP, należy oznaczyć ryzyko związane z łańcuchem dostaw i zalecić migrację do zweryfikowanego rejestru.
- Jeśli jakiekolwiek narzędzie łączy niezaufane dane wejściowe, wrażliwe dane i wynikające z nich działania, odmów zatwierdzenia i żądaj podziału.

Dane wyjściowe: jednostronicowy model zagrożeń z tabelą możliwości zastosowania ataków, inwentarzem obrony, listą flag Reguły dwóch i elementem Runbook z trzema działaniami. Zakończ pojedynczym dodatkiem zabezpieczającym o najwyższej wartości dla tego wdrożenia.