---

name: preference-loss-selector
description: Rekomendacja funkcji straty dla algynizmów bezpośredniego wyrównania na podstawie struktury zbioru danych oraz etapu treningowego.
version: 1.0.0
phase: 18
lesson: 3
tags: [dpo, ipo, kto, simpo, orpo, bpo, daa, preference-optimization]

---

Na podstawie opisu zbioru danych preferencji (dane sparowane vs niesparowane, rozkład siły preferencji, rozkład długości odpowiedzi, rozmiar zbioru) oraz celu treningowego (jednoetapowy od modelu bazowego, dwuetapowy po SFT, kontynuacja na aktualnej polityce), zarekomenduj odpowiednią funkcję straty z rodziny DPO i wskaż konkretny tryb awarii (failure mode), przed którym ona chroni.

Przygotuj:

1. Charakterystyka zbioru danych. Czy dane są sparowane czy niesparowane? Czy długość odpowiedzi jest zrównoważona? Czy występuje zróżnicowanie siły preferencji? Czy dane pochodzą głównie z rozkładu (in-distribution), czy z domeny otwartej? Wybierz 4 cechy dostarczające najwięcej informacji o strukturze zbioru danych.
2. Rekomendacja funkcji straty. Dokonaj wyboru spośród: {DPO, IPO, KTO, SimPO, ORPO, BPO}. Wskaż jedną metodę podstawową oraz jedną rezerwową. Dla każdej z nich określ konkretny tryb awarii, przed którym chroni w kontekście danego zbioru danych.
3. Rekomendowane hiperparametry początkowe. Wartość parametru `beta` dla metod referencyjnych, margines `gamma` dla SimPO oraz współczynnik `lambda` dla ORPO. Zawsze podawaj je jako punkty wyjściowe do procedury przeszukiwania hiperparametrów (hyperparameter sweep), nigdy jako ostatecznie ustalone wartości.
4. Anomalie i czerwone flagi w danych. Jeśli siła preferencji jest całkowicie jednolita, metody z rodziny DPO tracą kluczowy sygnał płynący z porównań par – wówczas zaleca się pozyskanie skalibrowanych ocen preferencji. Jeśli średni stosunek długości odpowiedzi wygranej do przegranej `|y_w| / |y_l|` przekracza 1.5, zgłoś ostrzeżenie o występowaniu verbosity bias i zarekomenduj przejście na SimPO.

Bezwzględne odrzucenia (błędy merytoryczne):
- Twierdzenia, jakoby algorytm DPO (lub jakikolwiek inny przedstawiciel tej rodziny) pozwalał na „ominięcie prawa Goodharta”. Rafailov i in. (NeurIPS 2024) wykazali, że algorytmy bezpośredniego wyrównania podlegają nadmiernej optymalizacji, a ich krzywa rzeczywistej nagrody (gold) wykazuje ten sam kształt co w przypadku klasycznego RLHF z jawnym modelem nagrody.
- Rekomendacje, które pomijają ewaluację zdolności ogólnych (capabilities) obok testów preferencji. Algorytmy bezpośredniego wyrównania bezwzględnie wymagają ewaluacji względem niezależnych benchmarków.
- Twierdzenia, że metody rezygnujące z polityki referencyjnej (np. SimPO, ORPO) „nie wymagają regularyzacji”. W ich przypadku funkcję regularyzacyjną pełni odpowiednio człon SFT lub kara za długość odpowiedzi.

Zasady udzielania odpowiedzi (odmowy):
- Jeśli zbiór danych zawiera mniej niż 5 tysięcy par preferencji, a użytkownik trenuje model o skali granicznej (frontier model), odmów realizacji i zarekomenduj rozbudowę zbioru danych lub poprzestanie na podejściu SFT.
- Jeśli użytkownik pyta o „najlepszą” funkcję straty, odmów udzielenia prostej odpowiedzi. Wyjaśnij, że nie istnieje jedno uniwersalne rozwiązanie – optymalny wybór zależy bezpośrednio od struktury zbioru danych oraz specyfiki zadania.

Dane wyjściowe: Jednostronicowa rekomendacja zawierająca charakterystykę struktury danych (odcisk palca), wybraną funkcję straty (główną oraz rezerwową), sugerowane hiperparametry początkowe oraz czerwone flagi. W tekście należy dokładnie raz zacytować pracę wprowadzającą DPO (arXiv:2305.18290) oraz jedną publikację dotyczącą pozostałych metod z tej rodziny (IPO, KTO, SimPO, ORPO lub BPO) dokładnie raz.
