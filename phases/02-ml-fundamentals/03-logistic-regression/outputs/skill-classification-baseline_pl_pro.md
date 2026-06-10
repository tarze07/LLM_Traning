---

name: skill-classification-baseline
description: Zanim sięgniesz po złożone modele, ustal solidny model bazowy dla klasyfikacji
version: 1.0.0
phase: 2
lesson: 3
tags: [classification, logistic-regression, baseline, preprocessing]

---

# Przewodnik po klasyfikacji bazowej

Przed sięgnięciem po złożone architektury, powinieneś zawsze ustalić punkt odniesienia (model bazowy), wykorzystując do tego celu regresję logistyczną. Trenuje się ona zaledwie w kilka sekund, na wyjściu generuje użyteczne miary prawdopodobieństwa, a co najważniejsze – jest w pełni interpretowalna. Zaskakująco duża liczba problemów pojawiających się w środowisku biznesowym nigdy nie wymaga wdrażania rozwiązań o wyższym stopniu zaawansowania.

## Lista kontrolna

1. Czy przewidywana granica decyzyjna ma prawdopodobnie charakter liniowy?
   - Tak: regresja logistyczna niemal na pewno okaże się wystarczająca.
   - Nie: nadal warto ją zastosować, by uzyskać bazowy punkt odniesienia (baseline) pozwalający ocenić, o ile lepszy jest bardziej skomplikowany model.

2. Iloma cechami dysponujesz?
   - Poniżej 50: standardowa regresja logistyczna sprawdzi się doskonale.
   - Od 50 do 10 000: zastosuj regularyzację L2 (Ridge).
   - Powyżej 10 000 (np. cechy tekstowe po transformacji TF-IDF): użyj regularyzacji L1 (Lasso) lub modelu LinearSVC.

3. Czy klasy w zbiorze danych są silnie niezrównoważone?
   - Stosunek klas poniżej 5:1: model prawdopodobnie poradzi sobie bez wprowadzania dodatkowych korekt.
   - Od 5:1 do 50:1: użyj parametru `class_weight="balanced"` w bibliotece scikit-learn.
   - Powyżej 50:1: konieczne jest połączenie wagi klas z rzetelną oceną omijającą dokładność na rzecz: precyzji, czułości (recall) lub wyniku F1.

4. Czy cechy różnią się znacząco rzędami wielkości (skalą)?
   - Pamiętaj: przed użyciem regresji logistycznej bezwzględnie przeprowadzaj proces standaryzacji. Model ten opiera swoje działanie na optymalizacji z wykorzystaniem spadku gradientu, z kolei użycie nieprzeskalowanych cech bardzo agresywnie wyhamowuje zbieżność algorytmu oraz prowadzi do wykrzywienia granicy decyzyjnej.

5. Czy w zbiorze występują braki danych (wartości puste / missing values)?
   - Dokonaj imputacji (uzupełnienia) przed przystąpieniem do dopasowywania modelu. Algorytmy regresji logistycznej z reguły nie potrafią poprawnie obsłużyć wartości NaN.
   - Najbezpieczniej wykorzystać imputację w oparciu o medianę dla kolumn zawierających wartości numeryczne oraz dominantę (wartość najczęstszą) dla danych kategorycznych.

## Kiedy regresja logistyczna jest rozwiązaniem "wystarczająco dobrym"?

- W przypadku prostej klasyfikacji binarnej z dominującymi liniowymi zależnościami pomiędzy cechami.
- Gdy system wymaga uzyskania wartości ułamkowych wyrażających szanse, a nie jedynie wskazania konkretnej etykiety.
- Kiedy niezwykle istotna pozostaje wysoka interpretowalność modelu (współczynniki wyuczone przez regresję w jasny sposób wskazują kierunek znaczenia cechy, a po zastosowaniu standaryzacji pozwalają także określić i uszeregować wagę z jaką realnie wpływają na ostateczny werdykt).
- Zbiór danych wykorzystywanych do treningu modelu cechuje się małym wolumenem (oscylując w granicach od setek do zaledwie rzędu kilku tysięcy rekordów).
- Środowisko docelowe nakazuje bezwzględnie zastosować wysoce responsywny algorytm dla potrzeb szybkiego serwowania wyników do serwerów aplikacji w czasie rzeczywistym.
- Ramy i narzucone prawnie bariery regulacyjne stawiają wymóg ścisłego, deterministycznego objaśnienia czynników dla podejmowanych przez model decyzji.

## Kiedy rozważyć krok naprzód i aktualizację do modelu wyższego rzędu?

- Zmierzona wydajność zatrzymała się na poziomie dalekim od wyników satysfakcjonujących biznes, a inżynieria cech (feature engineering) nie przynosi znaczącej poprawy.
- Przeprowadzona weryfikacja statystyczna (np. wykresy reszt) wykazuje ewidentnie istnienie potężnych form nieliniowych dla relacji między parametrami a zmienną celu.
- Posiadana do wykorzystania pula w bazie danych osiąga wolumen dziesiątek tysięcy zróżnicowanych wierszy: wskazane jest wykorzystanie mechanizmów modelujących np. algorytmem podnoszenia gradientu (np. implementacje XGBoost czy LightGBM).
- Powiązania, sploty korelacji oraz współzależności pomiędzy wieloma cechami osiągnęły stopień skomplikowania na tyle duży, że proste użycie transformacji do wielomianów nie wystarczy by móc wydobyć i poprawnie obrysować zarys ukrytych ścieżek wzorców z danych.
- Dane przybierają postać obrazów, tekstu bądź występują we wariantach czasowych lub innych sekwencyjnych rzutach – dla tak złożonych w budowie architektur wprowadzanie surowych bloków na proste algorytmy liniowe zawsze spotka się ze spektakularną porażką.

## Etapy wstępnego przetwarzania w celu utworzenia klasyfikatora bazowego

1. **Podział na zestaw treningowy/testowy** powinien zawsze odbyć się na absolutnie pierwszym etapie prac. Chroni to model przed wystąpieniem błędu określanego "wyciekiem danych" (data leakage).
2. **Postępowanie w związku z wartościami brakującymi**: narzucanie braków dla danych numerycznych uśrednieniem w oparciu o ich medianę oraz przyporządkowanie wartościom opisowym najczęstszego modusu.
3. **Kodowanie dla kolumn z klasyfikacją atrybutów typu kategorycznego**: do kolumn ubogich rzędem w pulę niepowtarzających się wartości słownikowych, narzucaj rozwiązanie wykorzystujące powszechny "One-Hot Encoding"; rozległe wymiarowo w warianty pozycje ratuj przed ekspansją objętości za pomocą "Target Encodingu", zawsze stosując dopasowywanie do modelu weryfikując rzut tylko przy udziale ram zbioru z danymi pod trening.
4. **Skalowanie wartości w kolumnach z liczbami (skalowanie numeryczne)**: narzucaj rzut formatowaniem StandardScaler (średnia ustawiona na poziomie 0, ujednolicona wariancja ustalona jako 1). Wylicz dopasowanie za pomocą zestawu szkoleniowego, aplikując ostatecznie tak wymierzoną metrykę pod transformację dla obu obozów punktów z danych - treningowych, a także z weryfikacyjnych partii.
5. **Dopasowanie regresji logistycznej** ze standardowym domyślnym parametrem regularyzacyjnym `C=1.0`.
6. **Ewaluacja (Ocena)**: wykorzystaj sprawdzenie macierzą pomyłek, rzuć weryfikację pod miary Czułości, Precyzji i wskaźnik równający je: wynik F1. Zawsze omijaj analizy posiłkujące się samą miarą uogólnionej Dokładności (Accuracy).
7. **Dostrajanie progów podejmowania decyzji**: wartość domyślna wyliczona u wskaźnika poziomu 0.5 niemal nigdy nie stanowi rozwiązania, z którym pozostawia się ostatecznie algorytm na środowisku produkcyjnym, przeto nakazuje się przeprowadzenie operacji sprawdzenia odcięć klas z ułożeniem u marginesu 0.1 wędrując konsekwentnie pod poziom 0.9 dla ustalenia wytycznej decyzyjnej pod optymalnie pożądany biznesowy kierunek za kompromisem.

## Typowe błędy w podejściu do prac

- Oparcie analiz statystycznych na ogólnej mierze tzw. dokładności ("Accuracy") na zestawach pozbawionych zbilansowanego osadzenia wolumenu we wskaźnikach zebranych do poszczególnej z kategorii punktów. Wynik ten maskuje absolutne pomyłki poprzez wygórowane trafienia przyporządkowane jedynie w ramy jednej, wielkościowo górującej w rzędzie klasy, stając się tym zupełnie mylącym drogowskazem.
- Ignorowanie procedury normalizacji/standaryzacji przed podpięciem zmiennych - powoduje zwłoki by nie rzec - wywleczony nierzadko w niezbadane w nieskończoność osadzony etap wyliczeń sprowadzania wektorowego podczas odnajdywania celów minimalizacji kosztów dla modelu z zejściem u pętli opartych na spadkach stochastycznych dla narzutu pod weryfikowane optymalizacje.
- Zanieczyszczanie procedur rzetelnych weryfikacji poprawności przez implementowanie zbiorów oddzielonych celem testu przy manipulacjach dostrojeniowych rzędu punktowego odcięcia pułapów barier decyzyjnych u wariantu weryfikowanego mechanizmu (koniecznym zawsze tu wymogiem z narzuceń nakazuje formacja wyciągania osobnych zestawień dedykowanych celowo i rozgraniczonych od testu ram tzw. walidacyjnych prób lub opieranie procedur pojęciem z krzyżowych walidacji dla zabezpieczeń testowej próby i jej nieskazitelności po oceny sprawdzające u celów od absolutnego rzutu).
- Podrzędne ignorowanie pod test procedur z tworzeniem bazowego osądu ustaleń referencyjnych (Baseline) rzucając system zawsze z miejsca w złożone pętle modeli wielo-poziomowych o złożoności XGBoosta bez cienia odniesień po wskaźnik oceny skali poprawy przy stratach w ujęciu całkowitej przejrzystości od form i wyników z mechanizmu.
- Brak czujności rzędu pominięć wykrywania ze wskazaniem pod korekty zjawiska podwyższonej współliniowości danych, która narzucona po zrzuconym od cech u wariancji prowadzi do wysokiej zmienności współczynników z nałożonych dla struktury.

## Szybkie odniesienie

| Scenariusz | Model | Regularyzacja | Kluczowe ustawienia |
|---------|-------|--------------|------------|
| Niewielka liczba cech, wdrożenie nastawione na interpretowalność | Regresja logistyczna | L2 (domyślna) | `C=1.0` |
| Znaczna liczba cech, z wyraźnym uwzględnieniem szumu z odrzucaniem | Regresja logistyczna | L1 | `penalty="l1"`, `solver="saga"` |
| Ogromna wymiarowość cech, rzadkie wpisy punktowe (dane z ujęć tekstu) | Klasyfikator SGD | L1 lub ElasticNet | `loss="log_loss"` |
| Brak zbilansowania w wolumenie u rzutu za klasy w zbiorze | Regresja logistyczna | L2 | `class_weight="balanced"` |
| Wymóg w postaci uzyskiwania ocen rzutem we szanse prawdopodobieństw | Regresja logistyczna | L2 | Oparcie odczytu na wywołaniu z algorytmiki metody o formule `predict_proba()` |
| Potrzebne wyłącznie klasyfikacje ze wskazaniem ramy na decyzje z konkretu przypisywanej z góry klasy w dużej objętości pakietu | LinearSVC (Liniowe SVM) | L2 | Optymalnie krótszy pod czas czasokres procedur o wyrokowania z trenujących w dużym gabarycie tabularycznym formacji dla ustaleń bazujących bez użyć u regresji logistycznych |
