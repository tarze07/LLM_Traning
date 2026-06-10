# Statystyka w Uczeniu Maszynowym

> Dzięki statystyce wiesz, czy Twój model faktycznie działa, czy po prostu ma dużo szczęścia.

**Typ:** Kompilacja
**Język:** Python
**Wymagania wstępne:** Faza 1, Lekcje 06 (Prawdopodobieństwo i rozkłady), 07 (Twierdzenie Bayesa)
**Czas:** ~120 minut

## Cele nauczania

- Obliczanie statystyk opisowych, korelacji Pearsona/Spearmana oraz macierzy kowariancji od podstaw.
- Przeprowadzanie testów hipotez (test t, chi-kwadrat) oraz poprawna interpretacja wartości p (p-value) i przedziałów ufności.
- Wykorzystanie próbkowania metodą bootstrap do konstruowania przedziałów ufności dla dowolnej metryki, bez przyjmowania jakichkolwiek założeń o rozkładzie danych.
- Rozróżnianie istotności statystycznej od istotności praktycznej na podstawie miar wielkości efektu.

## Problem

Wytrenowałeś dwa modele. Model A uzyskał wynik 0.87 na zbiorze testowym. Model B uzyskał 0.89. Zdecydowałeś się wdrożyć Model B. Trzy tygodnie później wskaźniki produkcyjne są o wiele gorsze niż wcześniej. Co się stało?

Prawda jest taka, że Model B w rzeczywistości nigdy nie przewyższał Modelu A. Różnica rzędu 0.02 była tylko szumem. Twój zbiór testowy był albo za mały, albo wariancja okazała się zbyt duża – lub jedno i drugie. Wdrożyłeś czystą losowość przebrającą się za poprawę jakości.

Takie rzeczy dzieją się bez przerwy. Nieoczekiwane przetasowania w rankingach Kaggle. Artykuły naukowe, których nikt nie potrafi odtworzyć. Testy A/B, które autorytarnie wyłaniają zwycięzców na podstawie próby kilkuset kliknięć. Główna przyczyna jest zawsze ta sama: zignorowano statystykę.

Statystyka to po prostu formalny zestaw narzędzi, który uczy Cię oddzielać sygnał od szumu. Pozwala jasno ocenić, kiedy zaobserwowana różnica jest prawdziwa, jak bardzo powinieneś jej ufać, oraz jak obszerne powinny być Twoje dane, żeby wnioski miały rację bytu. Każdy zautomatyzowany potok ML, każdy wyścig modeli, każde badanie eksperymentalne wymaga oceny statystycznej. Bez tego to tylko zgadywanka.

## Koncepcja

### Statystyki opisowe: podsumowanie danych

Zanim stworzysz jakikolwiek model, musisz zrozumieć, co masz w danych. Statystyki opisowe kompresują cały obszerny zbiór do zaledwie kilku wymownych liczb.

**Miary tendencji centralnej** odpowiadają na pytanie: „gdzie jest środek?”

```
Średnia (Mean): suma wszystkich wartości / liczba obserwacji
               mu = (1/n) * \sum(x_i)

Mediana (Median): wartość idealnie w środku w posortowanym zbiorze.
                  Jest odporna na elementy skrajne (outliers). 
                  Jeśli masz [1, 2, 3, 4, 1000], średnia wynosi aż 202,
                  podczas gdy mediana to solidne 3.

Dominanta (Mode): najczęściej powtarzająca się wartość w próbie.
                  Przydaje się mocno przy cechach kategorycznych.
```

Średnia to punkt równowagi. Mediana to półmetek. Jeśli drastycznie się od siebie różnią, oznacza to, że rozkład jest skośny. Rozkład zarobków w firmie ma zawsze średnią znacznie przewyższającą medianę (długi, prawostronny ogon od zarobków menedżerów). Z kolei rozkład strat obliczanych przy trenowaniu modelu często ma średnią zepchniętą w dół względem mediany (łatwe do klasyfikacji próbki lewostronnie skrzywiają wykres).

**Miary rozproszenia** odpowiadają na pytanie: „jak bardzo rozstrzelone są dane?”

```
Wariancja (Variance):  przeciętne odchylenie kwadratowe od obliczonej średniej.
                       sigma^2 = (1/n) * \sum((x_i - mu)^2)

Odchylenie standardowe (Std Dev): pierwiastek kwadratowy z wariancji.
                                  sigma = \sqrt(sigma^2)
                                  Dzieli ze zmienną te same jednostki, co czyni je 
                                  najbardziej interpretowalnym wskaźnikiem.

Rozstęp (Range):       Max - Min. Wysoce podatny na błędy przez outliers.

IQR:                   Rozstęp międzykwartylowy (Interquartile Range) to Q3 - Q1.
                       Wskazuje, gdzie leży środkowe 50% Twoich danych. 
                       Bardzo odporny na anomalię, doskonały do wykresów pudełkowych.
```

**Percentyle** kroją ułożone rosnąco wartości na równe ułamki. P25 (Q1) mówi nam o tym, że 25% wycinka całego zbioru znajduje się fizycznie poniżej podanej progowej wartości. P50 to inna nazwa dla wspomnianej wcześniej mediany. P75 (Q3) to z kolei trzeci kwartyl.

```
Dla monitoringu czasu życia modelu:
  P50 = median latency        (typowe, uśrednione doświadczenie klienta)
  P95 = 95th percentile       (duży dyskomfort działania, rzadki problem)
  P99 = 99th percentile       (najczarniejszy scenariusz opóźnień)
```

W inżynierii ML ekstremalnie istotna jest weryfikacja statystyk rzędu w odniesieniu do opóźnień produkcyjnych wnioskowania, dystrybucji pewności modelu czy też samych rozkładów wyliczanego błędu. Co z tego, że model ma świetną średnią skuteczność, jeśli na statystyce rzędu P99 zachowuje się tak fatalnie, że pociąga za sobą gigantyczne obciążenia finansowe.

**Wariancja z próby a wariancja populacyjna.** Wyliczając wariancję bezpośrednio na wycinku (próbie), musimy podzielić sumę we wzorze przez ułamek $(n-1)$ a nie po prostu przez $n$. Zabieg ten matematyka nazywa poprawką Bessela. Kompensuje ona obiektywny fakt o tym, że średnia z wyciętego losowo małego kawałka nie pokrywa się absolutnie nigdy z idealną średnią z kosmosu (całej populacji). Mianownik w postaci czystego $n$ zaniża wartość, podczas gdy dzielenie przez $(n-1)$ wymusza estymator do bezstronności.

```
Wariancja z całej populacji: sigma^2 = (1/N) * \sum((x_i - mu)^2)
Wariancja dla uciętej próby: s^2     = (1/(n-1)) * \sum((x_i - x_bar)^2)
```

Oczywiście dla ogromnych $n$ (rzędu milionów rekordów) ucięcie tej jedynki nic nie zmieni z racji praw wielkich liczb, ale dla malutkich porcji pomiarowych robi różnicę.

### Korelacja: jak zmienne poruszają się razem

Korelacja kwantyfikuje rygorystycznie, z jaką siłą oraz w jakim kierunku podążają za sobą dwie kolumny (zmienne).

**Współczynnik korelacji Pearsona** precyzuje tę bliskość tylko w zależnościach o ujęciu liniowym:

```
r = \sum((x_i - x_bar)(y_i - y_bar)) / (n * s_x * s_y)

r = +1:  idealna zgodność pod linię prostą
r = -1:  idealna odwrotność pod linię prostą (jak w lustrze)
r =  0:  absolutny brak zauważalnego podążania matematycznie-liniowego
         (uwaga, może tam być nieliniowa wciąż bardzo ścisła zależność!)
```

Pearson jest wrogiem nieliniowości, za to wybitnie dobrze przyjmuje wskaźniki podlegające prawom rozkładów dzwonowych (Gaussa). Jak zwykle, należy go mocno kontrolować na ewentualność nieprzyjemnego pojawiania się głośnych punktów z tyłu zbioru, ponieważ mały pyłek outlierowy wykrzywi rzędną np. od razu w stronę od $0.1$ do aż $0.9$.

**Korelacja Rang Spearmana** z kolei śledzi nam rygor w tzw. ujęciu monotonicznym:

```
1. Zamienia prawdziwą wartość każdego rekordu na jego sztuczną numeryczną
   "RANGĘ" rzędu (nr 1 dla najmniejszej liczby, nr 2 dla ciut większej, itp)
2. Narzuca Pearsona na nowo stworzonej ułożonej rangowo liście!
```
Spearman obronną ręką wyciąga zależności silnie wzrastające z racji monotoniczności. Dla wariacji krzywych wielomianów Pearson potrafi skrajnie okłamać analityków.

**Złota zasada warta powtarzania jak mantra:** Sama sucha metryka pod tytułem Korelacja nie zaświadcza o niczym z zakresu prawdziwej implikacji o istnieniu "związku przyczynowo skutkowego" (Causation vs Correlation). Spożycie lodów śmietankowych oraz wskaźniki uśmiercania na tonięciach idą równym sznurem do góry dlatego, że świeci pięknie słoneczna pogoda nad wodą.

### Macierz kowariancji

Kowariancja bada różnicę odchyłów naraz obu badanych zjawisk od samej ich centralnej średniej i zwraca suchy obraz powiązań wzajemnych:

```
Cov(X, Y) = (1/n) * \sum((x_i - x_bar)(y_i - y_bar))

Cov(X, Y) > 0:  Obie wartości chętnie rosną w tym samym czasie.
Cov(X, Y) < 0:  Kiedy jedna cecha rośnie, druga w tym układzie spada.
Cov(X, Y) = 0:  Obie wartości nie widzą pomiędzy sobą żadnych punktów tarcia.
```

W przypadku, kiedy patrzymy na wielowymiarową wejściową próbę o wymiarach rzędu $d$, Macierz Kowariancji $C$ przybiera ułożenie wymiarowe $d \times d$, wyznaczając punkty zapisu komórkowego do odczytania formą $C[i][j] = Cov(Cecha\_i, Cecha\_j)$. Główne diagonale pod postacią tablicowego przejścia $C[i][i]$ określają nam bazowe skale różnic - wariancje.

**Co ma to wspólnego do chociażby PCA?**
Algorytmy typu PCA z automatu rzucają procesem podziałów Własnościowych właśnie tę matrycę na wektory. Uzyskane wyniki "Wektorów Własnych" oznaczają osie dla naszych zróżnicowanych wariancji. Ich moc wyciągnięta do góry (Wartości Własne) udowadnia twardym ujęciem jak głośno wybrzmiewa ukryta cecha matrycy.

**Związek z samą korelacją:**
Korelacyjna tablica z wymiarów to nic obcego jak Macierz kowariancyjna przerzucona na wartości wcześniej standaryzowane, by sprowadzić je mocno i precyzyjnie za kołnierz pomiędzy skalą bezpieczną z domknięciem z zakresu pomiędzy $[-1, 1]$.

### Testowanie hipotez

Testy to żelazny podkład pod decyzyjność, gdzie musimy radzić sobie w wielkiej mgle. Wyznaczasz jasny cel udowodnienia czegoś, gromadzisz armię statystyk i uderzasz by zobaczyć czy mity obroniły się pod ciężarem brutalnych uderzeń faktów.

```
Hipoteza Null/Zerowa (H0): Szary start bez cudów, czyli np. "nic nowego nie odkryto"
                           "Wszystkie wyniki to sprawka losu, i wiatru z brzegu"

Hipoteza Alternatywna (H1): Twierdzenie w obronie Twojej własnej teorii, nad którą to
                            odbywasz swoje zaawansowane testy by udowodnić całemu światu rację.
```

**P-value** (wartość p) rzuca prawdopodobieństwem faktu wystąpienia obserwacji dokładnie identycznych rozmiarowo pod względem odchylenia zakładając, że za prawdę weźmiemy nasze nudne i konserwatywne "Null" ($H_0$). Jest to absolutnie mylone zjawisko. TO NIE JEST OBLICZENIE, że za teorią $H_0$ stoi jakaś w ogóle konkretna prawda. P-value mówi wyłącznie "Jeśli to pomyłka i szary szum (H0), to jak dziwny mamy wypadek przy pracy, że otrzymaliśmy tak rewelacyjne wykresy?".

```
P-value = P(Wyniki testu na podanej odchyłce | Zakładając ze jednak mamy racje H0)

Jeżeli odchyłka i wynik P-value < uderzy na wartość progową "Alfa"
      (co przyjmuje z tradycji branżowej zazwyczaj 0.05 lub mniej):
      Odtrącamy hipotezę H0 z zadowoleniem! Ujęcie staje się statystycznie
      Znaczące/Prawdomówne.

Jeżeli p-value >= alfa:
      Utrzymujemy H0. Nie obroniłeś się danymi. (To również z logiki, dalej
      nie znaczy, że H0 jest u góry "Prawdziwe i Obiektywne").
```

**Przedziały Ufności (Confidence Intervals):** Gwarancja dla jakich ram szerokości parametru przypisać powinieneś w swoich przewidywaniach obiektywizm wyliczeń rzędu:

```
Ramy przedziału tolerancyjnego rzędu chociażby 95% do Średniej:
     x_bar +/- z * (s / \sqrt(n))
```

Gdzie stała $Z$ przyjmuje zazwyczaj rzędną ułamka wartości na skali uderzenia 1.96 dla błędu z obszaru 95%.

Szerokość pasm wokół ufności to głośnik mówiący nam brutalną prawdę o potędze ujętej w modelu precyzyjności. Gigantyczna szerokość krzyczy, że tkwimy w niewiedzy. Mała szpilka i cienkie paski na boki w modelu twierdzą dumnie o niesamowitej punktowej dokładności wyliczeniowej.

### Test t-Studenta

Testy w postaci tak zwanego $T$, rozbijają nasze uśrednienia.

**Test T nad jedno-badaną próbką z danego populacyjnego zestawu**: Czy w ogóle testowane wyniki różnią nas zauważalnie u źródła wobec podanej wartości startowej i początkowej?

**Niezależny Test uśredniony dwóch uwarunkowanych z góry zbiorowości prób (Two-sample):** Czy jest rozłam zróżnicowania rygorystycznych średnich pochodzących podziale prób ze zbiorów różnych pacjentów?

Dla ujęcia Uczenia Maszyn, tak zwane Paired T-Tests pojawiają się ekstremalnie zjawiskowo nagminnie – rzucasz pot na blachę od tych samych dziesięciu wektorów by sprawdzać modele ramię w ramię przeciw wspólnym błędom od zera do jedynki.

### Test Chi-Kwadrat

To sprawdzenie twardą analizą, ujęte dla kategorycznych wyjść, rygoru czy nasze zaobserwowane wystąpienia idealnie podkładają się wejściowym dystrybucjom dozwolonym za sztywne wzorce oczekiwań z populacji.

```
chi^2 = \sum((Obserwowany Stan - Oczekiwane Przez Nas Zdarzenie)^2 / Oczekiwane)
```

Przykładowo analizuje z ogromną rygorystycznością to czy w Modelu Językowym odchyły na sentymencie nie skrzywiły sztywnie wejściowego treningowego słowotwórstwa. Wyciągnięcie ze zbiornika Chi^2 skali w rozmiarach wysokich dla jednego i więcej Stopnia Swobody zaowocuje błyskawicznym zrzutem rzędnych w granice małych wskaźników typu p < 0.005 dając wprost wynik, że nasze modele się rozkalibrowały kategoryzacyjnie!

### Testy A/B pod Machine Learning

Eksperymenty testów AB w dziale ujęciowym dla systemów uczących uginają się od pułapek i rygorów. Nie mają wiele do powiedzenia o prostych klikaniach w strony i guziczki:

```
1. Wspólny podział dla testu! Muszą iść dokładnie łeb w łeb z tą samą 
   dystrybucyjną paczką wejść i tablic krzyżowych. Różne sety uodpornią je fałszywie.
   
2. Mnoga optymalizacja metryk! Byle "Dokładność - Accuracy" tu kłamie. Potrzeba dbałości
   o całe ułożenie rygorów recall, false positives i balansu klas.
   
3. Ucieczka (Wyciek) Parametrów - Lekarstwem na testy AB jest używanie zbiornika 
   który w procesie pre-selekcji stał zakluczony w piwnicy od wektorów.
```

### Ocenianie czy Różnica Ma Znaczenie: Wąskie pole z efektem różnic Praktycznych

Znaczenie analityczne i chwalenie "Wyników Znaczących Historycznie dla Uczelni" wprost okłamuje korporacyjne metryki produkcyjne z "Sensownego Przynoszenia Korzyści". Czasami malutki margines odczytywany na dużej armii danych (np 1 000 000 odczytów) podnieca w ujęciu znacząco algorytmicznym modele P-Value na próg rzędu `0.0001`, ale model po deploymencie i wielotygodniowej walce programistów uratuje w ostatecznym procencie "poprawę na licznikach" rzędu nędzy procentowej na pułapie 0.03%, co sprawia, że wdrażanie kodu w chmurze obciążyło kosztorys pod samą górę zamiast generować firmie zyski.

Ocenę realnych wielkości w modelach buduje twardy odczyt tzw. Rozmiarów Skali – (Effect Size) badanych różnic dla ujęć rozmiaru: (Na przykład "D Cohena" d). Powie on Tobie ile tak właściwie wygraliśmy.

### Problem Testów Mnogości

Gdy bombardujesz systemy na wielu wariancjach modeli równolegle o nazwie testy HIPOTEZ... jeden dla przykładu w testach na dwudziestce, wypluje z uderzenia fałszywy odczyt pomylenia dodatniego. I zrobi to na pewniaka. Uderzasz z siłą "p-value", z marginesem błędu alfa - $0.05$. Otrzymujesz matematycznie wręcz murowany odczyt 1 błędu ze wsparciem farta w próbie 20 podejść (64% gwarancji na fałszerstwo).

Dlatego powstały ujęcia uodparniające odczyt ujęcia badawczego: **Korekta Bonferroniego** – bezbłędnie podziel w głowie testowe p przez skalę (np. liczbę mnóstwa wykonanych testów k), w celu redukcji pompowanego błędem szumu na progu. Zatem od teraz "Odniesienie Sukcesu" nastąpi nie przy wariacji $< 0.05$ ale dopiero przy wymuszonym przez Bonferroniego cięciu $< 0.0025$. Zrzuca to całe to p-hackingowe nadużycie fałszerstw na korzyść modeli.

### Próbkowanie z wrzucaniem rygorów powtórek (Bootstrapping)

Bootstrap pozwala uodpornić i uwolnić inżyniera od zakładania jakichkolwiek ujęć wobec modelów parametrycznych (w których musisz modlić się o "Dystrybucję Gaussianowską"). Obliczysz dzięki temu stabilne Estymatory dla nawet poszarpanego gęsto ujęcia błędów!

Bootstrapping losuje z puli $N$ wyników odczytu - podział po jednym elemencie rzucanym na stos z powrotnym wpychaniem elementu z powrotem.

Po powtórzeniu magii losowań tysiące razy ($B = 10000$), buduje całą wielką falę krzywych dla podnoszonych na próbkach wskaźników predykcji. Mając je odrzucone i usortowane ucinamy dolne i górne (na ujęciu $2.5\%$ z obu boków by otrzymać piękny bezzałożeniowy i bezpardonowy wynik Pasa Ufności Modelu pod metrykę np rzędu czystego F1. 

Jest absolutnym Świętym Graalem nowoczesnego i potężnego ujęcia wyboru potężnych wyników do deploymentu zamiast ryzykować na standardowych wariancjach (T-Test). Gwarantuje ominięcie twardych założeń!

## Praktyka (Zbuduj to)

Kody w języku Python przygotowane z rygorem ujęć własnych bez uginania nad paczkami scipy:
1. Obliczenie całości na funkcjach odczytujących pełne Spektrum Statystyki (od kwartyli do dominancji z percentylami).
2. Wykrywanie punktowe Kowariancji oraz Spearmana i zrzuty na tablice od Pearsona.
3. Testy na poziomie rzutu Chi-Kwadrat czy procedur z T-Wariancjami od Welch.
4. Całe wspaniałe mechaniki ujęcia Pasa Ufności Bootstrap dla AUC i skali modelu predykcyjnego P-value.
5. Zamknięcie ujęć z Korektami na wdrożenie testu symulatora z błędami Typu Pierwszego na A/B setach!

Wszystko budowane na bazie matematycznej surowicy modułu `math` oraz twardego `random`. Nie będziesz już zmuszony ufnie patrzeć, dlaczego model zrzucił metrykę podczas testu pod obudowę!

## Kluczowe terminy i słowniczek pojęciowy

| Termin | Przystępna Definicja Użytkowa |
|---|---|
| Rozstęp międzykwartylowy (IQR) | Pomiar odcinający szeroko wariancję, z ujęciem 50% gęsto upakowanego "wewnętrznego brzuszka" wyników. Bardzo rygorystycznie i dumnie opiera się outlayerom, broniąc przed rozkalibrowaniem wykresu od skoków danych. |
| Korelacja (Pearson / Spearman) | Kwantyfikowane oddawanie relacji zależności matematycznej od punktowego zakresu ujemnego (-1) po pełną kompatybilność w wektor (+1). |
| Macierz kowariancji | Dwuwymiarowa struktura wymiarowości w celu opisywania wzajemnej zależności i wchodzenia kolumn na obszary zachowań (skok lub spadek). |
| p-value (Wartość P) | Bezwzględnie wyliczane miano prawdopodobieństwa odnalezienia tak rygorystycznie wielkich różnic w dychotomicznych próbach statystycznych dla absolutnie idealnie zachowanego i głuchego podziału (bez ukrytych różnic). |
| T-test | Testowanie czy w próbach z modeli o rozkładach w miarę ciągłych ułożonych dzwonowato zaistniał rygor różnicowania w średnich badawczych predykcji dla wyników od paczki modeli. |
| Rozmiar Efektu | Dodawana z definicji d Cohena mierzona na skali odchyłka wyłaniająca, dla ujęć czy wygrany "model rzędu matematycznego na wielkich danych" posiada wyczuwalny w ogóle namacalny zmysłowy wygrany wymiar dla zastosowań czysto biznesowych na produkcji! |
| Bootstrap | Algorytmiczne próbkowanie z zawracaniem w celu budowy rozbudowanych, czułych estymatorów rozrzutu błędu czy wyliczeń, które nie wymusza od użytkownika wiary we wzorcowe krzywe normalne. |
| Błąd Typu 1 oraz Typu 2 | Odpowiednio – Wybuch radości pod odkrycie fałszywe przy braku podstaw do zmiany wyników od zerowej zasady odczytu dla (Typ 1 / Alarm Fałszywy). Lub błąd negacji – przegapienie wielkiego rewolucyjnego ujęcia zmian z powodu braku przebicia rygoru i ucięcie go (Typ 2 / Ślepota). |
| Centralne Twierdzenie Graniczne (CLT) | Prawo we Wszechświecie nakazujące by odpowiednio gęsto poszatkowane i rzucane próbki, dumnie dążyły i skłaniały gładko całą masę własnych "średnich wyliczeń" by w efekcie skrzywić się idealnie pod wspaniale opisywany i przyjazny wykres od rozkładów Normalnych. |
