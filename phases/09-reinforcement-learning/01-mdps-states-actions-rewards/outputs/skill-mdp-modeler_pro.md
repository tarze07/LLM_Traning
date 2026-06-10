---

name: mdp-modeler
description: Mając opis zadania, przygotuj przed rozpoczęciem uczenia specyfikację Procesu Decyzyjnego Markowa (MDP) i wskaż potencjalne ryzyka w sformułowaniu problemu.
version: 1.0.0
phase: 9
lesson: 1
tags: [rl, mdp, modeling]

---

Biorąc pod uwagę zadanie (sterowanie / gra / rekomendacje / dostrajanie LLM), wygeneruj:

1. Stan (State). Dokładny wektor cech lub specyfikacja tensora. Uzasadnij spełnienie właściwości Markowa.
2. Akcja (Action). Zbiór dyskretny lub zakres ciągły. Wymiarowość przestrzeni akcji.
3. Przejście (Transition). Przejścia deterministyczne, stochastyczne ze znanym modelem lub wyłącznie próbki ze środowiska (brak modelu).
4. Nagroda (Reward). Definicja funkcji nagrody oraz jej źródło. Nagroda rzadka (sparse) kontra gęsta/kształtowana (shaped). Nagroda końcowa (terminal) kontra nagroda za pojedynczy krok.
5. Współczynnik dyskontujący (Discount factor). Uzasadnienie dla wartości parametru gamma (γ) oraz horyzontu czasowego.

Odrzuć propozycje sformułowania MDP, w którym stan nie spełnia właściwości Markowa, bez wyraźnego zalecenia zastosowania techniki szeregowania klatek (frame stacking) lub warstw rekurencyjnych. Odrzuć funkcje nagrody, które nie są bezpośrednio powiązane z docelowym wynikiem zadania. Oznacz flagą ostrzegawczą każdą wartość `γ ≥ 1.0` w zadaniach z nieskończonym horyzontem czasowym. Oznacz ostrzeżeniem sytuacje, w których maksymalna nagroda przekracza 100-krotność typowej nagrody za krok, jako potencjalne źródło eksplozji gradientu (gradient explosion).
