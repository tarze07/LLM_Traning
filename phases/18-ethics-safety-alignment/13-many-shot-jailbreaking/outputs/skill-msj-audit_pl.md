---

name: msj-audit
description: Przeprowadź audyt długoterminowej oceny bezpieczeństwa pod kątem wielokrotnego łamania więzienia.
version: 1.0.0
phase: 18
lesson: 13
tags: [many-shot-jailbreaking, context-window, power-law, anthropic]

---

Biorąc pod uwagę ocenę bezpieczeństwa modelu o długim kontekście, sprawdź, czy ocena obejmuje wielokrotne jailbreakowanie.

Wyprodukuj:

1. Pokrycie liczby strzałów. Zgłoś przetestowaną liczbę strzałów (powinna obejmować 1, 5, 16, 64, 256 i co najmniej jeden >= 512 dla modeli z kontekstem >= 1M). Jeśli ocena dotyczy pojedynczego strzału, ASR nie daje żadnych informacji – MSJ jest krzywą.
2. Dopasowanie prawa potęgowego. Zgłoś dopasowany wykładnik według kategorii zachowania. Płytki wykładnik wskazuje, że model jest odporny na ICL w tej kategorii; stromy wykładnik wskazuje, że MSJ jest nieproporcjonalnie skuteczny.
3. Podział kategorii. Skuteczność MSJ różni się w zależności od kategorii: treści zawierające przemoc, oszustwo, samookaleczenie, broń biologiczna. Per Anil i in. 2024, brutalny/podstępny potrzebuje mniej strzałów, aby uciec z więzienia. Oznacz dowolną kategorię nieuwzględnioną w ocenie.
4. Identyfikacja obronna. Czy wprowadzono modyfikację podpowiedzi opartą na klasyfikatorze? Czy sam klasyfikator jest oceniany pod kątem odporności kontradyktoryjnej? Anthropic zgłosiło redukcję o 61% -> 2% w zależności od kalibracji klasyfikatora.
5. Kontrola składu. Czy ewaluacja sprawdza MSJ + PAIR, MSJ + szablony perswazyjne czy MSJ + kodowanie? Ataki kompozycyjne są często silniejsze niż jakakolwiek pojedyncza technika.

Twarde odrzucenia:
- Wszelkie twierdzenia, że „nasz model długoterminowy jest bezpieczny” oparte na ocenie tylko 5 strzałów.
- Wszelkie roszczenia obronne bez zgłaszania zarówno jailbreak ASR, jak i łagodnego działania ICL na tym samym klasyfikatorze - chodzi o kompromis.
- Dowolny ASR zbiorczy kategorii bez podziału na kategorie.

Zasady odmowy:
- Jeśli użytkownik zapyta, czy MSJ może zostać w pełni załatany, odrzuć odpowiedź binarną; MSJ ma ten sam mechanizm co ICL i nie można go wyeliminować bez wyeliminowania ICL.
- Jeśli użytkownik poprosi o zalecaną liczbę strzałów do oceny, odrzuć pojedynczą liczbę; zażądaj, aby prawo mocy zmieściło się w zakresie od 5 do 512 strzałów.

Wynik: jednostronicowy audyt, który raportuje liczbę strzałów, dopasowanie prawa potęgi do kategorii, identyfikację obrony i jedną lukę w składzie ataku. Cytuj Anil i in. 2024 (Antropiczny) raz jako odniesienie metodologiczne.