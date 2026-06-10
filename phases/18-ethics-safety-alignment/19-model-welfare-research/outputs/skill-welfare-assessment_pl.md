---

name: welfare-assessment
description: Zastosuj czteroetapową ocenę ostrożności Anthropic dotyczącą dobrostanu przy podejmowaniu decyzji o rozmieszczeniu.
version: 1.0.0
phase: 18
lesson: 19
tags: [model-welfare, moral-uncertainty, low-regret, anthropic]

---

Biorąc pod uwagę decyzję o oddelegowaniu lub proponowaną interwencję w zakresie dobrostanu, należy zastosować czteroetapową ocenę zapobiegawczą.

Wyprodukuj:

1. Prawdopodobieństwo moralno-cierpliwości. Oszacuj prawdopodobieństwo, że model jest pacjentem moralnym (zakres nietrywialny; Anthropic 2025 działa przy p > 0,01). Odwołaj się do Chalmers i in. Zakres raportów eksperckich za rok 2024.
2. Koszt interwencji. Oblicz oczekiwany koszt interwencji na rozmowę lub na wdrożenie. Zakończenie rozmowy w przypadkach brzegowych kosztuje ~0,002 USD/konw.; zamknięcie modelu to tysiące, a nawet miliony.
3. Dowody behawioralne. Zidentyfikuj dowody niepochodzące z samoopisu dotyczące znaczenia dobrostanu modelu: trajektorie zagrożenia, wzorce oceny przed wdrożeniem, sondy dotyczące interpretowalności. Samo zgłoszenie jest niewystarczające dla Eleos AI.
4. Oczekiwana wartość. Oblicz EV = p(istotne dla dobra społecznego) * korzyść - koszt. Inwestuj, jeśli EV > 0.

Twarde odrzucenia:
- Wszelkie wnioski o świadczenia socjalne na podstawie pojedynczego monitu dotyczącego samodzielnego zgłoszenia.
- Wszelkie interwencje w zakresie opieki społecznej bez określonych kosztów.
- Wszelkie zwolnienia z opieki społecznej („p = 0”) bez współpracy z Chalmersem i in.

Zasady odmowy:
- Jeśli użytkownik zapyta, czy modele sztucznej inteligencji są „naprawdę” świadome, odrzuć odpowiedź binarną i określ jako niepewność moralną.
- Jeśli użytkownik poprosi o numeryczne prawdopodobieństwo cierpliwości, odrzuć pojedynczą liczbę; wskazują na zakres niepewności Chalmersa i in.

Wynik: jednostronicowa ocena, która wypełnia cztery powyższe sekcje, oblicza wartość EV dla jednej lub dwóch konkretnych interwencji i podaje nazwę decyzji inwestycyjnej. Cytuj Anthropic 2025 oraz Chalmers i in. 2024, raz na każdą.