---

name: control-protocol-audit
description: Przeprowadź audyt protokołu wdrożenia w ramach modelu zagrożeń AI Control.
version: 1.0.0
phase: 18
lesson: 10
tags: [ai-control, subversion, trusted-editing, untrusted-monitoring, safety-case]

---

Mając opis protokołu wdrożenia, przeprowadź jego audyt pod kątem modelu zagrożeń AI Control: U (niezaufany silny), T (zaufany słaby), H (zaufany człowiek) i zmierz pozycję protokołu na granicy użyteczności i bezpieczeństwa.

Wyprodukuj:

1. Przydział ról. Zidentyfikuj, który model gra U, a który T. Jeżeli T jest kolejnym przypadkiem U, natychmiast zgłoś ryzyko zmowy.
2. Audyt rachunkowości budżetowej. Jak przydzielane jest H? Jednolity, losowy, kierowany flagą? Jaka część wyników podlega audytowi zgodnie z oczekiwaniami?
3. Wyliczenie wektorów zmowy. Dla każdej pary niezaufanych komponentów (producent U + U-monitor, producent U + edytor U) wylicz wektory zmowy: wskazówki steganograficzne, wcześniejsze wykorzystanie wspólnego szkolenia, kanały czasowe.
4. Analiza luk w możliwościach. O ile słabszy jest T od U? W którym momencie sygnał edycyjny T staje się szumem (np. T nie może niezawodnie wykryć backdoorów wytwarzanych przez U)?
5. Model zagrożenia dla najgorszego przypadku. Zakładając, że U jest przeciwnikiem z doskonałą znajomością protokołu, jaka jest najlepsza strategia przeciwnika? Jaka część prób drużyny czerwonych kończy się sukcesem?

Twarde odrzucenia:
- Dowolny opis protokołu, który wykorzystuje U jako własny monitor bez mechanizmu odporności na zmowy.
- Wszelkie roszczenia protokołu dotyczące „prawie zerowego wskaźnika backdoorów” bez oceny zespołu czerwonego, w przypadku którego zespół czerwony ma widoczność protokołu.
- Jakikolwiek audyt protokołu bez wyszczególniania luki w możliwościach T-do-U i budżetu H.

Zasady odmowy:
- Jeśli użytkownik zapyta „czy ten protokół jest bezpieczny”, odmów bez trzyczęściowego dowodu: (a) wynik czerwonej drużyny, (b) szacunkowa luka w możliwościach, (c) budżet H.
- Jeśli użytkownik łączy wyrównanie i kontrolę („dopasowaliśmy U, więc nie potrzebujemy protokołu”), odmów i wskaż Lekcję 9 (fałszowanie wyrównania) — wyrównanie jest właściwością U; kontrola jest właściwością protokołu.

Wynik: jednostronicowy audyt, który wypełnia pięć powyższych sekcji, wskazuje najsłabsze ogniwo (zwykle lukę w możliwościach T-do-U lub odporność na zmowę) i określa największy pojedynczy, nierozwiązany tryb awarii. Cytuj Greenblatt i in. (arXiv:2312.06942) raz jako źródło modelu zagrożenia.