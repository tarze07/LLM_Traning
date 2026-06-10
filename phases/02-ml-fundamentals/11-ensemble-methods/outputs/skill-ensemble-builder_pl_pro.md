---

name: skill-ensemble-builder
description: Wybierz odpowiednią metodę zespołową (ensemble) i skonfiguruj ją pod kątem swojego problemu.
version: 1.0.0
phase: 2
lesson: 11
tags: [ensemble, bagging, boosting, random-forest, xgboost, stacking]

---

# Przewodnik wyboru metody zespołowej (Ensemble Method)

Metody zespołowe łączą wiele modeli w celu uzyskania lepszych predykcji niż te, które mógłby zaoferować pojedynczy model. Najważniejsze pytania to: jakiego rodzaju podejście zespołowe wybrać i w jakiej sytuacji?

## Lista decyzyjna

1. Jaki jest główny problem Twojego obecnego modelu?
   - Wysoka wariancja (przeuczenie / overfitting): Zastosuj bagging (Lasy Losowe - Random Forest).
   - Wysoki błąd systematyczny (niedopasowanie / underfitting): Zastosuj boosting (Gradient Boosting, XGBoost).
   - Oba problemy naraz lub maksymalizacja dokładności za wszelką cenę: Zastosuj stacking.

2. Jak duży jest Twój zbiór danych?
   - Poniżej 1000 wierszy: Lasy Losowe (są stabilne, mało podatne na błędy w konfiguracji).
   - Od 1 000 do 100 000 wierszy: XGBoost lub LightGBM (często to najlepszy uniwersalny wybór dla danych tabelarycznych).
   - Ponad 100 000 wierszy: LightGBM (najszybsza implementacja gradient boostingu, stworzona z myślą o dużych zbiorach danych).

3. Ile czasu możesz przeznaczyć na strojenie (tuning) hiperparametrów?
   - Bardzo mało: Lasy Losowe na ustawieniach domyślnych (niemal zawsze dają dobre wyniki od razu).
   - Umiarkowanie: XGBoost ze wskaźnikiem uczenia (learning rate) = 0.1 oraz tuningiem parametru `n_estimators` połączonym z wczesnym zatrzymywaniem (early stopping).
   - Dużo: LightGBM lub XGBoost z optymalizacją bayesowską dla doboru hiperparametrów.

4. Czy model musi być łatwo interpretowalny (Explainable AI)?
   - Zdecydowanie tak: Użyj pojedynczego drzewa decyzyjnego lub bardzo małego Lasu Losowego analizując Feature Importance (ważność cech).
   - Częściowo: Gradient Boosting z wykorzystaniem wartości SHAP.
   - Zupełnie nie: Stacking lub Deep Ensembles.

5. Czy dane są mocno zaszumione i pełne wartości odstających (outliers)?
   - Tak: Lasy Losowe (bagging bardzo skutecznie radzi sobie z szumem).
   - Nie: Gradient Boosting (potrafi wycisnąć znacznie większą dokładność z czystych, jakościowych danych).

## Charakterystyka poszczególnych metod

**Lasy Losowe (Random Forest, oparty na baggingu)**: Bardzo bezpieczny model startowy. Polega na uczeniu wielu decyzyjnych drzew na wyciąganych ze zwracaniem podzbiorach (próbach bootstrapowych) po czym wyniki ulegają uśrednieniu. Obniża to wariancję bez generowania skrajnego obciążenia (bias). Ryzyko przeuczenia tego estymatora przy umiarkowanych zestawach danych bywa marginalne. Zastosuj minimalny stopień tuningowania konfigurując parametr liczbowy `n_estimators` w ramie 100-500 zostawiając domyślne pozostałe wymiary klasyfikacji.

**AdaBoost**: Progresywny wzmacniacz posługujący się tzw. korektą wag (re-weighting) poszczególnych elementów danych. Doskonale radzi sobie z najprostszymi, elementarnymi klasyfikatorami, tzw. "pniami decyzyjnymi". Ze względu na podnoszenie parametrów wagi na bazie popełnianego uchybienia wykazuje silną słabość wobec znaczników bezkierunkowych oraz ogólnego zaszumienia zebranego materiału, stąd w obecnych czasach został w znacznym stopniu zastąpiony architekturą gradientową.

**Gradient Boosting**: Algorytm tworzący łańcuch drzew decyzyjnych, w którym każda iteracja skupia się na skorygowaniu (poprzez aproksymację pseudoreszt) błędów poprzednika. Drastycznie obniża on tzw. błąd bias, gwarantując zjawiskową wydajność przy informatyce struktury tabelarycznej. Znaczny proces zaangażowania użytkownika polega na ręcznej adjustacji atrybutów takich jak parametr nauki `learning rate`, krotność predyktora `n_estimators`, stopień precyzji struktury drzewa `max_depth` oraz stopień tolerancji `min_child_weight` w koniugacji w uśrednianiu estymatorów.

**XGBoost**: Wysoko rozwinięta faza gradient boostingu polegająca m.in. na wykorzystaniu macierzy drugiego rzędu do usprawnienia pracy sprzętu. Jego budowa pozwala omijać brakujące informacje zawarte z badanych krotkach. Ośrodek standardu analitycznego na portalach informatycznych (tj. Kaggle), o silnie zakorzenionej użyteczności w profesjonalnym i naukowym obiegu przy pracy z tabelami zbioru własnego.

**LightGBM**: Moduł optymalizacji gradientowej rozszerzający konary drzew listowie-za-listowiem, (nie operując poziom-za-poziomem, ang. leaf-wise zamiast level-wise). Silnik wykonujący procedury podziałowe przy implementacji opartych na histogramie wyliczeniach dyskretnych operacji wskaźnikowych. Polecany dla zestawów o przekroju bazowym ponad 50 000 wierszy w badanej architekturze systemowej.

**CatBoost**: System podziałowy i wzmacniacz klasyfikacyjny oparty o uśrednienia kategorialne (bez uciążliwej funkcji zmiennych o silnie zdyskretyzowanym wymiarze z użyciem mapowania z formatu "one-hot encoding"). Niezwykle funkcjonalny na danych mocno nacechowanych czynnikami o małej liczbowej wadze zmienności.

**Stacking**: System implementujący warstwę metaucznia wyciągającego wnioski bazowe dla wskaźników wielomodelowych zróżnicowanej struktury wejściowej. Sprawdza się doskonale, gdzie uchybienie o dziesiąte części procenta potrafi przełożyć się na wymiar komercyjny operacji na danej, a sama siła platformowa serwera wykonawczego ulega rezerwie bez wpływu z racji objętości pracy. Bezwarunkowo polecamy estymację predyktora bazy przy ewaluacji krzyżowej wektorów - zminimalizuje to utraty danych ukierunkowując pracę na stabilnym rdzeniu wejściowych metaźródeł.

**Głosowanie (Voting)**: Elementarny proces zestawienia połączonego wyniku za wskaźnikiem składowych bazy metodologicznej metod. Istnieją jego dwie zasadnicze ramy analityczne: tzw. klasa dominanta - "Hard voting" lub tzw. wyliczane prawdopodobieństwo po uśrednieniu - "Soft voting". Wyśmienicie łączy parametry modelowe do trzech systemów bazujących by ominąć obciążenie środowiska warstwą zaawansowaną.

## Pospolite uchybienia (Błędy)

- Aplikacja estymatora "Gradient boosting" bez nakazanej reguły `wcześniejszego zatrzymywania` (zawsze przerost objętości wyliczeniowej w skali obciążenia cyklicznego dla sprzętu).
- Deklaracja na wyjściu zbytnio wzniesionego "learning_rate" (dane opatrzone mnożnikiem `powyżej wartości 0,3` objawią gwałtowną dysfunkcję uśrednienia stabilności badanych zmiennych).
- Pomijanie wymiaru tolerancji maksymalnego poziomu głębokości (brak zapisu ograniczenia potęguje problem).
- Wykorzystywanie stackingu na homogenicznych platformach klasyfikacyjnych (idea systemu stackingu upada przy zastosowaniu identycznych modeli w podstawie bazy).
- Zastosowanie modułu "AdaBoost" na skażonym błędami wierszu operacyjnym algorytmu (odbiegający punkt danych przejmuje znaczącą wagę na kolejnych węzłach uczenia - potęgując wadę u źródła).
- Naiwne przekonanie jakoby implementacja "Random Forest" skoryguje nam podłoże informacyjne u obciążonych biasem składowych algorytmu - las w znacznym stopniu uśrednia wymiar odchylenia zmiennej (wariancję).

## Strojenie według priorytetów bazując na wybranej metodzie

**Lasy Losowe:**
1. n_estimators: 100-500 (wyższa liczba rzadko pogarsza predykcję, jedynie wydłuża czas wykonania).
2. max_depth: None (pełny rozrost struktury drzewa) lub ogranicz maksymalny wskaźnik pomiędzy odnogami od rzędu wielkości 10-20.
3. max_features: "sqrt" wykorzystany dla algorytmu klasyfikacyjnego, wariant "log2" ew. "n/3" zaimplementowany do problemu natury regresji.

**XGBoost / LightGBM:**
1. learning_rate: 0,01-0,3 (niski mnożnik to większa dokładność, pod warunkiem zasobów dla dłuższego cyklu drzewa).
2. n_estimators: zamiast sztywnych granic stosuj proces z "wczesnym zatrzymaniem" względem zbioru o zadanej funkcji.
3. max_depth: 3-8 (dla eksperymentów bazuj domyślnie od `maksymalnej wielkości głębokości równej 6`).
4. min_child_weight / min_data_in_leaf: 1-20 (podnoszenie wielkości pomaga wyeliminować błąd "overfittingu").
5. subsample: 0,7-1,0
6. colsample_bytree: 0,7-1,0
7. reg_alpha (L1) & reg_lambda (L2): 0-10

## Szybka referencja analityczna metody

| Metoda | Redukuje błąd | Szybkość | Stopień Trudności Tuningowania | Przeznaczenie Idealne |
|--------|---------|-------|-------------|--------------|
| Losowy Las | Wariancja | Szybki | Bardzo Niski | Dane Zaszumione, szybki estymator próbny (Base-line) |
| AdaBoost | Bias | Szybki | Niski | Słabi Modele Składowi, przejrzysty zbiór odniesienia dla bazy |
| Gradient Boosting | Bias | Średni | Wysoki | Tabele i ustrukturyzowane ramy bazodanowe, Konkursy Informatyczne (Kaggle) |
| XGBoost | Oba warianty | Szybki | Wysoki | System produkcji klasyfikatorów tabelowych platform ML |
| LightGBM | Oba warianty | Najszybszy | Wysoki | Analiza woluminów wysoce objętościowych (Zbiory powyżej 50 000 wpisów w linii wiersza) |
| CatBoost | Oba warianty | Średni | Średni | Baza wymiarowana szeroko po atrybutach klas kategorialnych operacji |
| Stacking | Oba warianty | Powolny | Wysoki | Implementacja szukająca najwyższej dokładności na heterogenicznych systemach algorytmu modelowego |
| Głosowanie | Wariancja | Szybki | Znikomy/Brak | Fuzja dwóch/trzech sprawdzonych rozwiązań algorytmicznych na bazie ich sumarycznej ramy korelacji i estymacji wyników predykcji końcowej |
