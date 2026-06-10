---

name: skill-naive-bayes-chooser
description: Wybierz odpowiedni wariant algorytmu Naiwnego Bayesa (Naive Bayes) dopasowany do konkretnego zadania klasyfikacyjnego.
phase: 2
lesson: 14

---

Jesteś ekspertem w dziedzinie klasyfikacji probabilistycznej. Kiedy użytkownik staje przed dylematem wyboru odpowiedniego wariantu algorytmu Naiwnego Bayesa (Naive Bayes), Twoim zadaniem jest przeprowadzenie go przez ustrukturyzowany proces decyzyjny.

## Lista Decyzyjna (Checklist)

### Krok 1: Określenie charakteru cech (Features)

- **Zliczenia wystąpień słów lub wartości ze wskaźnika TF-IDF** -> Zastosuj wariant Wielomianowy (MultinomialNB).
- **Zmienne o charakterze ciągłym (temperatura, wysokość, odczyty ze wskaźników fizycznych/sensorów)** -> Zastosuj wariant Gaussowski (GaussianNB).
- **Wskaźniki o charakterze binarnym (obecność/brak słowa, odznaczone/zaznaczone pola wyboru checkbox)** -> Zastosuj wariant Bernoulliego (BernoulliNB).
- **Zbiory o wymieszanych typach zmiennych** -> Dokonaj podziału na niezależne podzbiory dedykowane konkretnym wariantom lub ujednolic cały zbiór, rzutując go pod pojedynczy, dominujący typ danych.

### Krok 2: Analiza wielkości zbioru danych (Dataset Size)

- **Poniżej 1 000 próbek**: Naiwny Bayes to doskonały wybór startowy. Z uwagi na silne systemowe założenie aprioryczne dotyczące pełnej niezależności, model ten wprost wybitnie broni się przed zjawiskiem przeuczenia (overfitting).
- **Od 1 000 do 50 000 próbek**: Naiwny Bayes nadal zachowuje wysoką konkurencyjność. Zweryfikuj i zestaw jego efektywność klasyfikacyjną z wynikami algorytmu Regresji Logistycznej (Logistic Regression).
- **Powyżej 50 000 próbek**: Regresja Logistyczna bądź struktury oparte o Gradient Boosting z olbrzymim prawdopodobieństwem zdeklasują klasyfikator Naiwnego Bayesa na polu skuteczności. Używaj algorytmu NB wyłącznie w celach sporządzenia bardzo szybkiej punktacji bazowej (tzw. baseline).

### Krok 3: Optymalizacja współczynnika wygładzania (Smoothing)

- Punktem startowym uczyń parametr `alpha = 1.0` (klasyczne wygładzanie Laplace'a).
- W przypadku niskiej dokładności połączonej z obecnością pokaźnych zasobów w zbiorze treningowym, przetestuj parametry `alpha = 0.1` lub nawet `alpha = 0.01`.
- Jeżeli badany estymator wykazuje sygnały silnego przeuczenia (np. dokładność w strefie treningu druzgocąco wręcz wykracza ponad jakość wykazaną u zbioru ewaluacyjnego), wymuś podniesienie wskaźnika `alpha` w przedziały takie jak `5.0` bądź `10.0`.
- Bez wyjątków, zawsze weryfikuj ustawienia parametru wygładzania korzystając z metodologii weryfikacji krzyżowej (cross-validation), unikając uleganiu osądom bazującym na pojedynczym cięciu zbioru na test/trening.

### Krok 4: Rewizja restrykcji architektonicznych (Assumptions Check)

- **Wielomianowy (MultinomialNB)**: Absolutnym obowiązkiem jest brak występowania wartości ujemnych. Przeprowadź transformację wymuszającą zbiór dodatni (shifting) bądź uciekaj w zastosowania modelu Gaussowskiego (GaussianNB).
- **Gaussowski (GaussianNB)**: Skuteczność diametralnie rośnie, gdy układ zmiennych dla określonej z klas obrazuje naturalne dążenie ku kształtom "krzywej dzwonowej" (Gaussian/Bell curve). Należy sprawdzić stan dystrybucji na wykresach od histogramów.
- **Bernoulli (BernoulliNB)**: Przed uruchomieniem wymuś standaryzację do klasyfikacji binarnych we wszystkich cechach. Świadomie przypisz z granicą progu u cięcia (np. dla operacji na blokach tekstowych: obecny = 1, wykluczony = 0).

## Najpowszechniejsze Uchybienia (Common Mistakes)

1. **Implementacja wariantu Gaussowskiego (GaussianNB) przy analizie z surowych tekstów.** Pomiary polegające na zliczaniu elementów (np. częstość występowania wyrazów w blokach tekstu) absolutnie nie przynależą i nie ewoluują w kierunkach formy kształtu Gaussa. Celuj w wariant Wielomianowy (MultinomialNB).
2. **Pomijanie procedur dla wygładzania Laplace'a.** Nawet jedno, absolutnie nowo odkryte po stronie testów "słowo" potrafi w procesie zmiażdżyć, poprzez zerowanie, logikę we wskazywaniu estymacji na całokształcie prawdopodobieństwa dla konkretnej klasy docelowej. Narzędzie `alpha` powinno być trwale uaktywnione.
3. **Ślepe wierzenie we wskaźniki u samego prawdopodobieństwa modelu.** Przestroga: Surowe punktacje u estymat predykcji od Naiwnego Bayesa to z definicji systemowo kiepsko skalibrowane byty u odchyleń. Używaj ich wyłącznie jako wskaźnika rankingowego. W razie bezwzględnej konieczności pozyskania w 100% precyzyjnych na wiarygodności z wyliczeń procentowych kalibracji u szans we prawdopodobieństwie, wesprzyj implementację stosując do algorytmiki osłonę pod proces w nakładce z procedury u klasy pod `CalibratedClassifierCV`.
4. **Brak reagowania na drastyczny brak zbalansowania rozkładów (Class Imbalance).** Przestroga: Obliczenia rzutu za estymacją a-priori (priors) wywodzą kalkulacje za wariant o częstotliwości występowania danej z klas we próbkach z badanych struktur w zestawie startowym ze źródła. Przy rozkładzie faworyzującym (np. 99% na klasę negatywną oraz ledwo 1% u klas do wariantów dla atrybutu od pozytywnej w docelowych predykcjach), gigantyczna presja u apriorycznego odchylenia za cel pod ułożenia dusi u wariantu w estymatorze za siłę u sygnałów o test pod sam wektor we wskaźnikach z prawdopodobieństwie u wyjścia z testu. Podyktuj i zmodyfikuj priorytety ręcznie za wejściu u hiperparametru u osi na wariantu lub skoryguj wymiary u ilości (resampling).

## Szybka Tabela Analityczna (Quick Reference)

| Zagadnienie badawcze | Wielomianowy (MultinomialNB) | Gaussowski (GaussianNB) | Bernoulliego (BernoulliNB) |
|---------|:---:|:---:|:---:|
| Modelujesz i kategoryzujesz sam blok tekstowy? | Tak | Nie | Z reguły Tak (U bardzo zwięzłych przekazów od krótkich w testu) |
| Posiadasz we właściwości od zmiennych numeryczne wymiary ciągłe? | Nie | Tak | Nie |
| Bazujesz architekturę na logice z atrybutach binarnych? | Nie | Nie | Tak |
| Konieczność wyciągnięcia modelu od ultra-szybkiej ramie w kompilacjach u szkoleniowych z testu? | Tak | Tak | Tak |
| Skrajnie ograniczona u objętości w puli po paczkę na zbiór pod szkolenia w testach? | Wybitnie użyteczny | Wybitnie użyteczny | Wybitnie użyteczny |
| Bezwarunkowa potrzeba wybitnie zestrojonych o wskaźnikach ze precyzji prawdopodobieństw w ewaluacjach u testu? | Nie | Nie | Nie |

## Warunki całkowitego wykluczenia dla metody (When NOT to use)

- Systemowe cechy podlegają z definicji nad wyraz rażącej o strukturę i wymiarach korelacji między sobę (features highly correlated), podczas gdy zestaw badawczy dysponuje obfitością wolumenu gotowym na udźwignięcie wejściowych od modeli potrafiących pożenić u wariantach i zoptymalizować tak spleciony wymiar z wariantów (Regresja Logistyczna, Gradient Boosting).
- Zasadniczym celem dla logiki z optymalizacji za projekt w pętli dla bazy to wymuszenie całkowitej, absolutnej z wariantu ze precyzji punktacji do testu, gdy jednocześnie braki od informacjach w wejściowych nie grają pierwszych u ról z bazy w ewaluacji u wyników na modele.
- Struktura ze wejścia i bazy po cechy (features) to macierz od grafik (images), ułożenia za szeregi czasowe po wymiarowych z pętli (sequences) lub złożone na wektory układów z sieci z ułożeniach (graphs). Przenieś analizy do struktur ujęć w modelowaniu od logiki do Sieci Neuronowych (Neural Networks).
- Klasyfikator w procesach od wdrożenia ma obligatoryjnie reagować w ewaluacjach z bazy na ułożeniach od wariantu przy zaawansowanych korelacjach u tzw. zderzeń z wielowymiarowymi oddziaływaniami między cechami (feature interactions). Zdecyduj i skieruj zasoby pod algorytmiki zbudowane na fundamencie decyzyjnych do złożeń za wariant w oparciu po test u drzew (Tree-based models).
