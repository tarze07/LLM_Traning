---

name: topology-picker
description: Wybierz topologię debaty wieloagentowej (gwiazda/łańcuch/drzewo/wykres), N agentów, profil heterogeniczności i okrągłą granicę dla danego zadania.
version: 1.0.0
phase: 16
lesson: 15
tags: [multi-agent, debate, topology, voting, self-consistency]

---

Biorąc pod uwagę opis zadania, zarekomenduj topologię i rozmiar wielu agentów.

Wyprodukuj:

1. **Odcisk palca zadania.** Badania (długi horyzont, otwarte), szybkie fakty (odpowiedź w formie zamkniętej), udoskonalanie krokowe (potok etapowy) lub opinia (bez podstawowej prawdy). Wybierz jeden; jeśli obejmuje dwa, wybierz kształt dominujący.
2. **Topologia.** Gwiazda, łańcuch, drzewo lub wykres. Uzasadnij na podstawie odcisku palca:
   - badania → wykres (krytyka od każdego do dowolnego)
   - szybkie fakty → gwiazda (agregaty piastowe)
   - stopniowe udoskonalanie → łańcuch (lub drzewo w przypadku zasady dziel i zwyciężaj)
   - opinia → żadne z powyższych; polecam jednego agenta + ludzką decyzję
3. **N agentów.** 3 to najtańszy użyteczny zespół; 5 to najczęstszy słodki punkt; 7+ to specjalność. Powyżej 5 na topologii wykresu ostrzegaj o podatku koordynacyjnym.
4. **Profil heterogeniczności.** Co najmniej jeden czynnik musi pochodzić z innej rodziny modelu podstawowego, jeśli monokultura ma znaczenie (badania, rozumowanie). Preferuj 3 różne modele podstawowe przy N=5.
5. **Runda ograniczona.** 1 runda = głos. 2 rundy = jedno udoskonalenie. 3 rundy = maksimum, zanim dominuje zgodność. Nigdy bez ograniczeń.
6. **Agregacja.** Wielość (tanio), ważona ufnością (CP-WBFT z lekcji 14), mediana geometryczna (DecentLLM) lub punktacja sędziego. Domyślnie ważona ufnością, chyba że ograniczenia kosztowe wymagają mnogości.
7. **Eskalacja.** Konsensus poniżej progu → eskalacja gdzie? Człowiek, kolejny zespół z różnymi modelami bazowymi, czy może wstrzymanie się od głosu?

Twarde odrzucenia:

- Wszelkie zalecenia dotyczące ponad 10 agentów w zakresie topologii grafów. Dominuje podatek koordynacyjny; najpierw zmierz.
- Topologia gwiazdy dla otwartych pytań badawczych. Star traci korzyści płynące z krytyki typu „każdy do każdego”.
- Wszelkie zalecenia, które uruchamiają ten sam model podstawowy N razy i nazywają go wieloagentowym. To jest zamaskowana samokonsekwencja; oznacz to poprawnie.
- Nieograniczone rundy. Nagradza zgodność; im dłużej trwa debata, tym więcej agentów zgadza się pod naciskiem, a nie logiką.

Zasady odmowy:

- Jeżeli zadanie nie ma podstaw prawdziwych (opinia, synteza, twórczość), stwierdzamy, że głosowanie ma charakter doradczy. Poleć jednego agenta + ludzką decyzję.
- Jeżeli użytkownik nie ma dostępu do wielu modeli podstawowych, należy oznaczyć sufit monokulturowy i jako rozwiązanie awaryjne zalecić zachowanie spójności ze zmianami temperatury.
- Jeśli zadanie jest proste (pojedyncze sprawdzenie faktów, < 100 znaków rozumowania), zarekomenduj jednego agenta o spójności wewnętrznej N=5.

Wynik: jednostronicowy brief. Zacznij od zalecenia składającego się z jednego zdania („Topologia wykresu, N=5 agentów z 3 różnych modeli podstawowych, 2 rundy, agregacja ważona ufnością, eskalacja do człowieka poniżej progu”), a następnie siedem sekcji powyżej. Zakończ szacunkowym budżetem: oczekiwane tokeny na zapytanie i oczekiwane opóźnienie w sekundach.