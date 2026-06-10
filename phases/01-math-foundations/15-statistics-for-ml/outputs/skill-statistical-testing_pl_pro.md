---
name: skill-statistical-testing
description: Wybierz odpowiedni test statystyczny do porównywania wyników modeli ML i eksperymentów A/B
version: 1.0.0
phase: 1
lesson: 15
tags: [statistics, hypothesis-testing, model-comparison]
---

# Testowanie statystyczne w Uczeniu Maszynowym

Praktyczny poradnik wyboru prawidłowego testu statystycznego do oceny modeli, przeprowadzania eksperymentów A/B i naukowej walidacji wyników.

## Drzewo decyzyjne (Lista kontrolna)

1. **Co dokładnie badasz/porównujesz?** Średnie, proporcje klas, rozkłady prawdopodobieństwa czy korelacje?
2. **Ile jest grup/prób?** Jedna próba względem teoretycznego odniesienia, rygorystycznie dwie grupy badawcze, czy zderzenie wielu grup równolegle?
3. **Czy obserwacje są sparowane (zależne) czy też w pełni niezależne?** (Ten sam zbiór testowy lub te same fałdy walidacji to przypadek próby sparowanej!).
4. **Czy dane cechują się rozkładem normalnym?** Jeżeli wielkość $n < 30$ i gołym okiem brakuje w nich kształtu "dzwona Gaussa", stosuj bezpieczne odpowiedniki nieparametryczne.
5. **Czy mierzona metryka jest precyzyjna i ciągła, ułożona w skali porządkowej, czy to twarde wielkości kategoryczne?**
6. **Jak wiele pomiarów testowych realizujesz w jednym podejściu?** Jeśli wiele – bezwzględnie zaimplementuj korektę na testy wielokrotne (np. Bonferroniego).

## Kiedy stosować konkretny rodzaj testu?

| Narzędzie testowe | Kształt danych | Główne uwarunkowania | Najlepszy przypadek użycia w ML |
|---|---|---|---|
| **Sparowany test t-Studenta** | Ciągłe, sparowane | Normalny rozkład różnic | Ocena i zderzenie czołowe dwóch potężnych modeli trenowanych na sztywno przykładowych tych samych k-fałdach walidacyjnych. |
| **Test Wilcoxona dla par** | Ciągłe/Porządkowe, sparowane | Brak jakichkolwiek założeń o rozkładzie (nieparametryczny) | Małe próby walidacji (np. rzędu k od 5-10 fałd testowych). Oparty o analizę rang zamiast ostrego punktowania odchyleń. |
| **Test t-Welcha (niezależny)** | Ciągłe, niezależne | Rygor względnie normalnego kształtu krzywej | Skrajne zderzenie predykcji od modelu badawczego opartych na kompletnie osobnych (oderwanych) testach zbiorów walidacyjnych, gdzie niemożliwe staje się rzetelne sparowanie fałd. |
| **Test U Manna-Whitneya** | Ciągłe/Porządkowe, niezależne | Brak uwarunkowań (nieparametryczny) | Idealny estymator pod mocno zniekształcone czy asymetryczne pule metryk (chociażby w ocenie skrajnie rozrzuconych parametrów po opóźnieniach na produkcji / latency). |
| **ANOVA (Analiza Wariancji)** | Ciągłe, 3 lub więcej grup | Rygorystycznie gładki dzwonowy rozkład oraz homoskedastyczność wariancyjna | Analizowanie równoczesne potężnej listy ułożonych i ocenianych uśrednień dokładności w zderzeniu kilku równoległych wariantów z architektur modelowych. |
| **Test Kruskala-Wallisa** | Ciągłe/Porządkowe, 3+ | Całkowity brak wymagań formalnych względem krzywej | Nieparametryczny potomek wariancji ANOVA w służbie ratowania oceny kilku odmiennych modeli uczenia przy silnie skośnych metrykach badawczych (np. oceny czasowe obciążenia wejściowego). |
| **Test Chi-Kwadrat** | Zliczenia kategoryczne (Count) | Minimalne obciążenie wystąpień i rzutów z grupy prognoz z pułapem na min. ok $n > 5$ wejściach | Test na integralność dystrybucyjną balansu klasowego - sprawdza surowo skrzywienia od Tablicy Pomyłek Modelu. |
| **Dokładny Test Fishera** | Surowe ujęcie kategoryczne (Bin) | Zaprojektowany dedykowanie dla miniaturowych wycinków prób próbnych | Rzetelne punktowanie przewidywań z algorytmów klasyfikacyjnych dla ekstremalnie zjawiskowo trudnych do uchwycenia rzadkich wypadków w naturze (Anomaly Detection). |
| **Test Kołmogorowa-Smirnowa** | Ciągłe (ciągłe pasmo wejść) | Minimalizacja wymagań w odniesieniu co do założeń w ujęciu krzywych parametrycznych | Ścisły audyt tego, czy oddana jako ostateczna ucięta produkcyjna predyspozycja ciągła predykcji jest spójna topologicznie ze wskazywanym wymaganym rozkładem krzywych teoretycznych. |
| **Bootstrap CI (Przedziały)** | Dosłownie swoboda na każdą statystykę w modelu estymacji | Brak wymagań badawczych przy testach prób parametrycznych | Fenomenalne zaplecze by otoczyć obiektywnym przedziałem ufności niestandardowe i wymagające testy (chociażby oceny dla parametru F1-Score oraz estymatory z ucięcia AUC) |
| **Test McNemara** | Binarne wyjściowe oceny sparowane precyzyjnie w punkt | Brak | Specjalistyczny pomiar "celności" w testowaniu zmian z celnych trafień dla par i rywalizacji 2 wrogich klasyfikatorów testowanych w bojach od dokładnie równego zarysu prób testowych. |

## Rygorystyczny Przepis na Uczciwe Porównanie Modeli:

1. Najpierw przed eksperymentami jasno zamknij cele w ramach założeń o badanej metryce punktowej dla Twojego rozwiązania na rygorystycznie oznaczonym progu np (Alfa ucinająca błędy na $\alpha = 0.05$).
2. Zmuś pod maską kod do przeprowadzenia bitwy z modelami używając dla uczciwości absolutnie tego samego pulsu dzielonego wejścia K-Fold (Dla pułapu krzyżowej Cross-Validation z np $K = 5 \dots 10$).
3. Zacznij rzetelnie wyłuskiwać predykcyjny wynik dla sparowanej listy z ucięciami wejściowymi wektorów rzędu: $(A_{1}, B_{1}), \dots, (A_{k}, B_{k})$.
4. Zanotuj skoki z różnic zysku dla każdego wejścia od wzoru na surowo: $d_{i} = B_{i} - A_{i}$.
5. Pchnij rzetelne parametry wejściowe z różnic na mechanikę odpowiedniego rzutu od testów (Odpal t-Student dla par gdy czujesz się bezpieczny przy gładkim podbiciu różnic, albo załóż sztywne wsparcie za pomocą testów Wilcoxona by wyminąć skrzywione odchyły dla $k < 10$).
6. Opisz sumaryczny ubytek oraz wygrane w estymacji na zewnątrz od modelu korzystając jawnie ze statystyki opisowej: Punktu wartości testowej dla rygorów z *P-Value*, Różnic uśrednianych, Rzędnych z przedziałów 95% *Pasa Ufności*, czy wreszcie samej Siły Zmian – wywołanej przez surową metrykę badawczą za pomocą algorytmu skali D Cohena.
7. Gdy ujęcie pomiarowe udokumentuje faktyczne, statystyczne złamanie granic $P < \alpha$ ORAZ – (co najważniejsze) sam rozmiar fali odbicia estymatora w skali wyznaczonej rzędną o tzw. "Znaczącej Wyporności dla Biznesu i Optymalizacji", test wygrywa! Decyzję o przełączeniu silnika uważa się za prawomocną z racji merytoryki opłacalności.

## Błędy Typowe u Młodszych Inżynierów

- Uparcie zaciągane procedury z wymogami użycia **niezależnych** procedur klasyfikatorów przy fałdach z prób walidacji krzyżowej i sparowaniu zestawów. Niszczy to korelacyjną więź o tym skąd próbki tak właściwie przybyły. Tracisz całą uciętą ze ścieżki badawczej siłę dla rozróżniania drobinek błędu statystycznej siły detekcji wykrzywień. Uderzaj w procedury pod zjawisko **SPAROWANE**.
- Publikacja gołego "$P-Value < 0.05$" bez nakreślania opinii podpartej o współczynnik mianowany ujęciem Efektu Wielkości. Uzyskanie minimalnego "P" poprzez rozstrzelenie predykcji od modelu ML i zyskanie w efekcie podrzędnej celności z różnicą $0.1\%$ skrzywionego wzrostu – to czyste straty z wdrożenia oprogramowania produkcyjnego na serwer, co stanowi klapę w inwestycjach! Dodaj pod wejścia $d-Cohena$.
- Prowadzenie pomiarów testowych A/B na innych wektorach! Model do audytu od zderzenia absolutnie i u zarania MUSI korzystać z precyzyjnie tego samego pliku `Test_Set.csv`. Inaczej patrzysz na pomiary wróżb.
- Szukanie "strzału P-hackingowego" w rywalizacji modeli hyper-parametrowych po wykonaniu chociażby szukanych 20 rund bez założenia i ociosania wyników korektami testu za wielokrotność (Correction Bonferroni). W próbach strzelanych ślepo do tarczy aż 20 razy przy odcięciu granic alpha na kropce 0.05 – murowanie i rygorystycznie zgarniesz jeden "Pozytywny Zbieg Fałszywego Odkrycia Modelu Rzędu Pierwszego" dla rzutu monetą w testach!
- Zaufanie na twardo metryce zjawiska (Accuracy / Celność Ocen), jeżeli wrzucona po rurze z kodem klasa to silnie niezbalansowane próbki (Oceniana ujemna i poszukiwana Rzadka Zjawiskowość). Na 99% większości paczek o chorobach z etykietami "Brak Raka" najprostszy głupi klasyfikator dostanie i dumnie odda celność dla inżynierów $99\%$ bo zgadnie wprost klasę zerową na pewniaka bez grama analiz. Korzystaj i promuj krzywe na $F1-Score$ i analizę *Precision-Recall AUC*.
- Estymacja wektorów uciętego walidacyjnego krzyżowania `Cross-Validation K-Folds` jako całkowicie autonomicznego niezależnego zderzenia próbek na świat. Fałdy dzielą z tyłu dla siebie "Wspólną Treningową Wiedzę ze Zbiorów", wymuszając wysoce obciążoną sieć estymatora i depczą o ścianę względem wymogów dla surowej NIEZALEŻNOŚCI od obserwacji próbek.

## Tablica referencyjna wspierająca decyzyjność interpretacji z odczytu (D Cohena)

| Indeks Cohena "$d$" | Bezpośrednia Ocena Rozstrzygnięcia Biznesowo i Naukowo |
|---|---|
| 0.2 | Niemal marginalny, cichy ruch w poprawie zmian na wykresach oceny celności. |
| 0.5 | Znaczące podbicie statystyczne dla metryki; umiarkowanie odczuwalny gołym okiem skok jakości. |
| 0.8 | Wielkie poruszenie na produkcyjnym i rygorystycznie twardo celnym skoku wdrożeniowym w algorytmach. |
| $\ge 1.0$ | Kolosalnie i wybitnie olbrzymia siła rozstrzygnięcia dla twardego wdrażania zmian, model o lata do przodu deklasuje słabego wroga. |

| Raportowany Klucz | Filozofia Użytkowa Wprost |
|---|---|
| **$P-Value$** (Wartość w progu $P$) | Kwantyfikowanie pytania: "Czy skok skuteczności, na który właśnie dziś patrzymy ma rygorystyczną linię pokrycia i nie wynika jedynie i wyłącznie ze zjawiskowej szczęśliwej karty od losu (szum)? |
| **Pasy i Przedziały Ufności** ($CI$) | Kwantyfikowanie pytania: "Daj szerokie widełki ram, i powiedz jak mocno te granice oddzielają faktyczny spodziewany w skrajności rygor odchyleń skoku?" |
| **Analiza Siły Estymatora ze Wskaźnika Wielkości** ($Effect Size$) | Kwantyfikowanie biznesowego rygorystycznego pytania: "Czy wywalczone właśnie ulepszenie matematyczne przejawia zyski z potu w programowaniu na produkcji (Wartość Inwestycyjna w skoku na zysku)?" |
| **Ilości Próbek Badawczych** (Ujęte $n$ / Próba $K$-fałd) | Kwantyfikowanie pytania: "Z jaką ogromną stanowczością musimy wierzyć na pewniaka w wyżej wykonany raport z tych audytów?" |
