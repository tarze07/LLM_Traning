---

name: preference-loss-selector
description: Zalecenia utraty algorytmu bezpośredniego wyrównania, biorąc pod uwagę kształt zbioru danych i etap docelowy.
version: 1.0.0
phase: 18
lesson: 3
tags: [dpo, ipo, kto, simpo, orpo, bpo, daa, preference-optimization]

---

Biorąc pod uwagę opis zestawu danych preferencji (sparowany vs niesparowany, rozkład siły preferencji, rozkład długości, rozmiar) i cel szkoleniowy (jednoetapowy od podstawy, dwuetapowy po SFT, kontynuacja zgodnie z polityką), zarekomenduj stratę z rodziny DPO i nazwij pojedynczy tryb awarii, przed którym chroni.

Wyprodukuj:

1. Odcisk palca zbioru danych. W parze? Nieparzysty? Zrównoważona długość? Różnica w sile preferencji? Głównie w dystrybucji czy w domenie otwartej? Wybierz 4 pola zawierające najwięcej informacji dla tego zbioru danych.
2. Zalecenie dotyczące straty. Od {DPO, IPO, KTO, SimPO, ORPO, BPO}. Jeden podstawowy i jeden rezerwowy. Dla każdego z nich nazwij konkretny tryb awarii, przed którym chroni w tym zbiorze danych.
3. Wartości domyślne hiperparametrów. `beta` dla metod zakotwiczonych, margines `gamma` dla SimPO, `lambda` dla ORPO. Zawsze podawaj je jako punkty początkowe przemiatania, nigdy jako wartości końcowe.
4. Sygnały ostrzegawcze w danych. Jeśli siła preferencji jest idealnie jednakowa, metody z rodziny DPO tracą sygnał parowania — zaleca się zbieranie skalibrowanych preferencji. Jeśli średni `|y_w| / |y_l|` odbiega od > 1,5, długość flagi odchyla się i przesuwa się w stronę SimPO.

Twarde odrzucenia:
- Wszelkie twierdzenia, że inspektor ochrony danych (lub jakikolwiek członek rodziny) „ucieka z Goodhart”. Rafailov i in. (NeurIPS 2024) dowodzą, że algorytmy bezpośredniego dopasowywania nadmiernie optymalizują w przypadku tego samego kształtu krzywej nagrody w złocie, co algorytm jawnego RM RLHF.
- Wszelkie zalecenia, które nie określają oceny zdolności obok oceny preferencji. Algorytmy bezpośredniego dopasowywania nadal wymagają testów porównawczych złotego sygnału.
- Wszelkie twierdzenia, że ​​metody wolne od zasad odniesienia (SimPO, ORPO) „nie wymagają regularyzacji”. Regularyzatorem jest kara za okres lub długość podobna do SFT.

Zasady odmowy:
- Jeśli zbiór danych jest mniejszy niż 5 tys. par, a użytkownik celuje w model o granicznej skali, odmów i zalecaj rozszerzenie zbioru danych lub zastosowanie podejścia opartego na SFT.
- Jeśli użytkownik zażąda „najlepszej” straty, odmów i wyjaśnij, że nie ma zwycięzcy w formie zamkniętej — właściwa metoda zależy od kształtu zbioru danych i zadania.

Dane wyjściowe: jednostronicowe zalecenie zawierające listę odcisków palców zestawu danych, straty pierwotne i rezerwowe, początkowe hiperparametry i czerwone flagi. Cytuj DPO (arXiv:2305.18290) i jedną inną publikację rodzinną (IPO, KTO, SimPO, ORPO lub BPO) dokładnie raz.