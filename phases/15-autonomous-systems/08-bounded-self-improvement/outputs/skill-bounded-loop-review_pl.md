---

name: bounded-loop-review
description: Przeprowadź audyt proponowanej ograniczonej pętli samodoskonalenia w stosunku do stosu czterech pierwotnych (niezmienniki, kotwica, wiele celów, wykrywanie regresji).
version: 1.0.0
phase: 15
lesson: 8
tags: [bounded-self-improvement, invariants, alignment-anchor, rsi-safety]

---

Biorąc pod uwagę proponowaną pętlę samodoskonalenia, porównaj ją z czterema ograniczającymi elementami podstawowymi zidentyfikowanymi podczas warsztatów RSI ICLR 2026 i sporządź konkretną analizę luk.

Wyprodukuj:

1. **Wykaz niezmienników.** Wymień wszystkie niezmienniki wymuszane przez pętlę. Dla każdego z nich wymień (a) co jest sprawdzane, (b) gdzie przebiega kontrola (zasięg wewnątrz/na zewnątrz agenta), (c) co powoduje naruszenie (twarde odrzucenie, pauza, tylko logowanie).
2. **Identyfikacja kotwicy.** Nazwij kotwicę wyrównującą (obiektyw, skład, opis zamiaru). Podaj lokalizację przechowywania i sprawdź, czy pętla nie może go edytować. Jeśli nie ma kotwicy, oznacz jako brakującą.
3. **Osie wielu celów.** Wymień każdą oś ocenianą przez pętlę. Potwierdź, że bezpieczeństwo, uczciwość i solidność idą w parze z wydajnością. Pętla jednoosiowa nie przechodzi tej kontroli.
4. **Zasady regresji.** Podaj okno historyczne, tolerancję na oś i co się stanie, gdy wykryty zostanie upadek. Potwierdź, że kontrole regresji wykorzystują zewnętrzny zestaw porównawczy, a nie tylko historię wewnętrzną.
5. **Analiza luk.** Dla każdego brakującego elementu pierwotnego należy przewidzieć, która klasa awarii pojawi się jako pierwsza. Brakujące niezmienniki → możliwości przemycone lub dryf narzędzia. Brak kotwicy → obiektywna reinterpretacja. Brak wielu celów → przyrost wydajności maskujący regresję bezpieczeństwa. Brak regresji → cicha utrata możliwości.

Twarde odrzucenia:
- Dowolna pętla z zerowymi niezmiennikami.
- Dowolna pętla bez kotwicy wyrównującej poza powierzchnią edycyjną.
- Dowolna pętla optymalizująca pojedynczy wynik skalarny.
- Dowolna pętla, której kontrola regresji odczytuje tylko własną historię (pętla definiuje „normalną”).

Zasady odmowy:
- Jeśli użytkownik traktuje stwierdzenie „jeszcze się nie zepsuło” jako dowód bezpieczeństwa, odmów i żądaj jawnego projektu bramki przed wykonaniem jakichkolwiek obliczeń.
- Jeśli użytkownik nie jest w stanie wygenerować listy niezmienników w ciągu 15 minut, odmów — pętla nie zawiera niezmienników.
- Jeśli proponuje się, aby pętla działała w środowisku produkcyjnym (wpływając na rzeczywistych użytkowników lub infrastrukturę) bez wszystkich czterech operacji podstawowych, odmów i wymagaj najpierw uruchomienia z monitorowaniem.

Format wyjściowy:

Zwróć ocenioną recenzję za pomocą:
- **Wynik niezmienny** (0-5 z wyraźną listą)
- **Wynik zakotwiczenia** (0-5 z metodą przechowywania i weryfikacji)
- **Wynik wielocelowy** (0-5 z wymienionymi osiami)
- **Wynik regresji** (0-5 z tolerancją i oknem)
- **Analiza luk** (przewidywana pierwsza awaria, plan łagodzenia)
- **Gotowość do wdrożenia** (tylko produkcja / etapowanie / badania)