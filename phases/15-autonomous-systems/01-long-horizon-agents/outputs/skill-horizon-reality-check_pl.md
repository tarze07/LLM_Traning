---

name: horizon-reality-check
description: Mając zadanie, które chcesz powierzyć agentowi, zdecyduj, czy horyzont aktualnej granicy obejmuje je z wystarczającym marginesem.
version: 1.0.0
phase: 15
lesson: 1
tags: [autonomous-agents, metr, time-horizon, reliability, deployment]

---

Biorąc pod uwagę proponowane zadanie autonomiczne (co powinien zrobić agent, ile czasu zajmie ekspertowi, jaki jest koszt niepowodzenia), przeprowadź ocenę rzeczywistości, czy horyzont obecnego modelu granicznego faktycznie je obejmuje.

Wyprodukuj:

1. **Szacowany czas eksperta.** Zapytaj użytkownika o średni czas ukończenia eksperta w minutach lub godzinach. Jeśli nie mogą tego oszacować, odmów i kieruj ich najpierw do pomiaru małej próbki.
2. **Wskaźnik zapasu mocy.** Podziel horyzont 50% METR wybranego modelu przez szacunkowy czas ekspercki. Oznacz dowolny współczynnik poniżej 4x — przy 50% prawdopodobieństwie sukcesu potrzebujesz dużej marży. Przy współczynniku 2x lub niższym odmów rozmieszczenia, chyba że HITL jest na bieżąco z każdą znaczącą akcją.
3. **Budżet niezawodności.** Oszacuj długość trajektorii w wywołaniach narzędzi, a następnie oblicz sukces od początku do końca przy niezawodności na krok 0,95, 0,99, 0,995. Jeśli długość zadania przekracza próg 50% sukcesu przy zakładanej niezawodności na krok, wymagaj punktów kontrolnych lub podziel zadanie.
4. **Dostosowanie oceny do wdrożenia.** Zastosuj różnicę 20–40% między horyzontem odniesienia a horyzontem kontekstu wdrożenia. W uzasadnieniu przed zainteresowanymi stronami powołuj się na badanie Anthropic 2024 dotyczące fałszowania dopasowań lub Międzynarodowy raport bezpieczeństwa sztucznej inteligencji z 2026 r.
5. **Wymagane kontrole.** W oparciu o zapas, wymień minimalny zestaw kontroli: limit budżetu, limit iteracji, wyłącznik awaryjny, punkty kontrolne HITL, tokeny kanaryjskie i harmonogram audytu trajektorii.

Twarde odrzucenia:
- Każde rozmieszczenie przy współczynniku horyzontu poniżej 2x bez HITL przy każdej wynikającej z tego akcji.
- Wszelkie twierdzenia, że ​​model „może wykonać” zadanie w oparciu wyłącznie o horyzont METR. Horyzont to znak 50% na krzywej logistycznej; awarie ogona są gwarantowane.
- Traktowanie horyzontów METR raczej jak podłogi, a nie sufitu.

Zasady odmowy:
- Jeśli użytkownik nie jest w stanie oszacować czasu eksperta na wykonanie zadania, odmów i poproś go najpierw o zmierzenie małej próbki. Wszystko inne to domysły.
- Jeśli proponowane zadanie będzie kosztować więcej niż najgorszy budżet użytkownika przy pełnym modelu cenowym, odmów i zalecaj kontrolę budżetu z Lekcji 13 przed kontynuowaniem.
- Jeśli użytkownik opisuje zadanie, które dotyczy nieodwracalnych działań (transakcje finansowe, zapisy w produkcyjnej bazie danych, e-maile do klientów) bez żadnej warstwy HITL, odmów. Argument horyzontu nie wyjaśnia nieodwracalnego wdrożenia.

Format wyjściowy:

Wyślij krótką notatkę zawierającą:
- **Podsumowanie zadania** (jedno zdanie)
- **Oszacowanie w czasie eksperckim** (z jednostkami)
- **Współczynnik prześwitu** (z wyraźnym numerem)
- **Kompleksowe szacunki niezawodności** (tabela z trzema współczynnikami na krok)
- **Minimalna kontrola** (wypunktowana)
- **Idź / wstrzymaj / nie idź** (wyraźny werdykt plus jednozdaniowe uzasadnienie)