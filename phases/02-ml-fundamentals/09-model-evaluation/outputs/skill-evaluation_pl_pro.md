---
name: skill-evaluation
description: Lista kontrolna strategii oceny modeli dla zadań klasyfikacji i regresji.
version: 1.0.0
phase: 2
lesson: 9
tags: [evaluation, metrics, cross-validation, model-selection]
---

# Strategia oceny modelu (Model Evaluation)

Oto rygorystyczna lista kontrolna, która umożliwi ci poprawną ewaluację i ocenę dowolnego algorytmu uczenia maszynowego (ML). Ściśle podążaj za zaprezentowanym procesem krok po kroku, aby zabezpieczyć projekt przed tragicznymi błędami i pułapkami.

## Krok 1: Wzorowe rozdzielenie zbiorów danych

- Zawsze tnij dane na zbiory (Train/Val/Test) PRZED podjęciem jakichkolwiek działań i kroków związanych z procesowaniem, uzupełnianiem luk (imputacją), obróbką kategoryczną i ze skalowaniem wartości.
- Dla klasyfikacji używaj ułożenia Stratyfikacyjnego (Stratified), zachowującego w równym rozrzucie pierwotne proporcje występowania klas docelowych do osi Y.
- Wyselekcjonuj do bezpiecznego repozytorium Zestaw Testowy, wyciągnięty stricte z myślą o tylko jednej ostatecznej operacji tuż przed wdrożeniem i nigdy na niego nie rzucaj okiem i algorytmem na etapie modelowania.
- Kiedy objętość bazy mocno niedomaga – zastąp statyczny podział na Zbiór Walidacyjny sprawiedliwym obwodem kół i agregacji (tj. klasyczny model na K-Fold lub Stratyfikowany K-Fold na 5 czy rzadziej 10 ramion), uciekając przed ślepą punktową pomyłką bazową z braku i rzadkości sygnału.
- Uważaj kategorycznie pracując w domenie Czasu. Szeregi z rzędami osi (Time-Series) absolutnie się nie tasują (Nie wolno odpalać na nich Shuffle). Cięcia prowadzisz osiami chronologicznie względem wystąpienia dat (np rozkłady po okresie roku/kwartału odcinające stare od nowego).

## Krok 2: Bezbłędny i odpowiedni cel doboru Wskaźnika Metryki z Ocen

### Operacje dla Kategoryzacji i Klasyfikacji Wzorców

| Scenariusz Badań Oczekiwanych | Preferowana optymalizacja pod ułożenie Wskaźnika | Argumentacja wyboru |
|----------|----------------|-----|
| Miarodajne zrównoważenie bazy klas na cele podstawowego zestawienia podziałów. | Dokładność (Accuracy) | Fenomenalny, łatwy przekaz do działu biznesowego z racjonalną interpretacją dający jasny rzut gdy dysproporcje miedzy wariantami odpowiedzi równe są pułapom dookoła równych mas osi. |
| System pod obróbkę alarmów gdzie rzucane fałszywe powiadomienia narażają system na absurdalne koszta strat z obsługi dla biznesu/zasobów (filtry e-mail / bloki ryzyk i transakcyjnego odcięcia kont z racji domniemanych oszustw). | Precyzja (Precision) | Rygorystycznie docina wagowo w dół modele skorelowane ze "zbyt luźnym w podejściach alarmem uaktywnianym pomyłkowo" i wycenia co ostatecznie tak rzetelnie "zakwalifikowało". |
| Błąd związany ze ślepym uśpieniem radaru niszczy szanse wybronienia (pomyłki fałszywie ujemne prowadzące w rzutowaniu bezpośrednio do katastrofy – rakiety w strefie, wczesna diagnoza i leczenie dla raka). | Czułość (Recall) | Zabezpieczenie szeroko na uśrednienia gwarantujące brak ukrytej za zasłoną zjawiskowych ślepot pominięć krytycznie potężnych i drogich incydentów, dbające i maksymalizujące by maszyna cokolwiek wyciągnęła. |
| Obiektywna praca z problemami na rygorystycznym przecięciu równych wymogów z uwagi na konieczność pogodzenia silnych dysproporcji (i zaprzestania szukania między ominięciami a zaspamowaniem rzutami). | F1-Score | Agresywnie docięta i wyśrubowana relacja dająca optymalizacje po krzywych, kategorycznie karząca w wyliczeniu ułożenie dysbalansowe. |
| Konfrontacje po siłach modelowych nieodciętych progowo pułapem na sztywno. | AUC-ROC | Potężna informacja gwarantująca niezależność rankingu wyplutego z silników z uwolnionym pułapem odciecia z osi. |
| Dane kategoryczne gdzie występują anomalie i skrajny dysbalans zjawisk na niekorzyść badanej próbki mniejszościowej. | Ułożenia wycelowane w optymalizowanie układem F1-Score, krzywych PR-AUC, by omijać AUC-ROC z bazy. | Uśredniona osiowa matematyczna predykcja z Dokładności skreśli rzetelne osądy dając "zastępcze" idealne oceny bo uogólnia rzuty jako negatyw maskując fatalną ignorancję względem klasy mniejszości. |

### Operacje dla Przeliczeń Wartości - Regresja Numeryczna

| Scenariusz Badań Oczekiwanych | Preferowana optymalizacja pod ułożenie Wskaźnika | Argumentacja wyboru |
|----------|----------------|-----|
| Klasyczna regresja numeryczna i zjawiskowa pozbawiona patologicznych skoków wartości outlayerów i ekstremalnych pułapów zniekształcających. | RMSE | Zwraca wektor wskaźnika i ocen w tych samych rodzinnych przelicznikach rzutu z układów miar bazy z karaniem dla grubszych niedomagań oszacowania. |
| Zbiory z gigantyczną dozą bardzo odstających śmieciowych pomiarów wyrzucających statystyki w ramy wariancyjnego nieporządku poza logiką. | MAE | Solidnie obroni układy nie dając obciążać zbytnio w osi ocen błędami ekstremów "wybijających" w górę model – liczy wszystko od odciętej prostej. |
| Porównywania skuteczności w zjawiskach, które pracują po różnych liniach na skali numerycznej w obozach niezwiązanych wzajemną konwersją dla ułożenia. | R-Kwadrat (R2) | Relacyjny ułamek określający siłę wytłumaczenia ukrytych praw z uniwersalnie osadzoną z definicji przedziałową rzutnią 0-1 pozwalający oceniać ogólną jakość mechanik w korelacyjnej dolegliwości i zjawisk. |
| Bezpośredni styk prac dla zarządu pod rozkłady wymiernych miar korporacyjnych gdzie biznes celuje oczekiwania co do kosztu z tolerancji lub realnego wydatku z konta bankowego. | MAE z opcją ewentualnego RMSE | Wypluwa miary nie rozmyte skalą – operując w dziedzinie strat i tolerancji biznes może jasno szacować opłacalność tolerowania odchylenia rzutu dając np. informację, że błąd 5 Euro w te czy wewte to koszt mniejszy, lub błąd, o którym informacja to dla firmy realne kłopoty produkcyjne i trzeba obciąć pętlą błąd z poziomu kodu uczenia. |

## Krok 3: Określenie Punktu Odniesienia (Base-line z minimum przyzwoitości algorytmicznej)

Bezwzględnie zanim ruszysz maszyny na poważnie zmierz wskaźnik i oceń na ile dobrze wypadałoby całkowicie ślepe bezmyślne obstawianie bazujące wyłącznie na naiwnej logice ludzkiej, bez używania komputera i ML:
- Przy ocenie kategorycznej (Klasyfikacyjnej): Uderzenie mechanicznie zawsze jednolitym werdyktem i rzutowaniem prognozy pod element który zdefiniowany z bazy ma najwyższy ułamek w masie. Zobacz na ile wycelowała ci celność takiej prostej polityki domyślnej.
- Przy ciągłości ocennej w liczbie (Regresji): Skaluj błąd od sztywnego, obciętego z średniej punktu stałego przewidywania dla treningowych rzędnych - każdy obiekt wektorowany z założeniem "że średnia wartość ułoży wynik prawidłowy".
- Pamiętaj: Jeśli ostatecznie algorytm wykręci wynik identyczny ze stratami na równi (bądź nie daj boże z większym błędem od w/w "Głupich z góry narzuconych rozwiązań" – rzuciłeś wyliczeniami w piach lub nie masz odpowiednich surowców. Skasuj go z procedury do wdrożenia).

## Krok 4: Testowanie Poprzez Cross-Validacje

- Stosuj zawsze i egzekwuj silniki sprawdzające wyliczenia w stabilności na K-rzutach (wymuś 5 bądź 10).
- Bezwzględnie ładuj parametry rozwarstwienia `Stratified` k-Fold jeśli rzutujesz kategorie po układach niezrównoważonych.
- Informując w raporcie wyrzucaj miary agregowane: wskaźnik ze średnich + parametry ze odchyleń z wariancji std z puli.
- Pamiętaj, architektura zwracająca osie [Średnie=0.85 + Skok_Odchyleń(std)=0.02] bije na głowę stabilnością rzuty modelu udającego lepsze [Średnie=0.87] ukrywające potworne piki niestabilnych wektorów predykcji po sieciach o [Skokach(std)=0.10].

## Krok 5: Analiza Wyników Przez Uogólnienia z Próg Badania (Testowanie Statystyki i Walidowanie Różnic)

- Wyrzuć uogólnione zachowanie, nie ufaj zrzutom dającym ułamek tysięcznej przewagi dających złudne "ulepszenie na papierku". Badaj wskaźniki pod testami zjawisk.
- Wyciągaj dla iteracji Cross-Validacyjnych rzuty testów na klamrę testów T-Studenta w ujęciu ułożenia paramentrycznych próbek powiązanych dla różnic wyników wektorów (paired t-test).
- Patrz w pułap: jeśli wartość `|t|` pod korelacji wyliczona ląduje nisko do zera tzn `< 2.78` w teście dla K-Fold na 5 ze stopniami sf df=4 i przy p-value zakotwiczonego o klasyczne <0.05, oznacza że skok przewagi jest mrzonką ze zrządzenia fali wariancji i zwykłego farta podyktowanego lepszą porcją układów zmiennych z wylosowanych indeksów od bazy. Szansa na brak obiektywnego ulepszenia to matematyczna jedność przy ocenie i decyzjach dla inwestycji modelarza w projekt.
- Trzymaj zasady Brzytwy o Okhamie. Jeżeli w teście statystycznym dwa odmienne modele nie potrafią wejść w ostre przewagi (np potężna głęboka sieć ML i prosty las drzew z modelem logicznym radzą sobie statystycznie zbieżnie w obrębie hałasu z zjawiskiem w ułamku z błędu) – uciekaj na produkcję z modelem PROSTSZYM – jest mniejszym zagrożeniem przy awariach i o rząd stabilniejszy na chmurach dla obsługi, szybszy oraz przyjaźniejszy i wyciąga zyski identyczne do wyżyłowanego byta z wyższej ligi, dla logiki.

## Krok 6: Poszukiwania Winnego ze spłycania modeli

- Przeciekanie informacyjnych uwarunkowań rzutów: Upewnij się kategorycznie, pytając ze sprawdzaniem logów "czy sieć w procedurach pre-pocesowych pobrała logiki, estymatory i wariancje z paczek, do których miała zaglądać jako niespodziankę na stół ewaluacyjny pod kątem np obudowy targetowania po y?"
- Dysbalanse informacyjne mniejszości klas po fali: Pytanie - czy urocze, obiecujące w niebiosa wysokie Accuracy nie kłamie nam o ujęciu, gdy pod powłoką rzuca 0 na klasie rzadkiej gubiąc u nas pacjenta ze śmiertelnym zachorowaniem w raku w ramach wspaniałego ogółu trafnie oznaczonych setek "okazów zdrowych"? Użyj tablic pomyłek dla sprawdzania prawdy rzutowanej o model z recall by ubić błędy fałszywych ujemnych.
- Szalejąca na sieci dewiacja - Wariancja z rzutu przeuczenia: Kategorycznie wyłuskaj dla różnicy z raportu rzutu testu o uśrednienie pętli uogólnień dla rzutu szkolnego. Czy jest wyrwa? Luka i ucięcie wyników rzędami oznacza katastrofę z optymalizacji – masz model wędrowniczek gubiący realne związki, uczący punktów z treningu i hałasu na sztywno nie odnajdując ukrytych pojęć pod nowymi próbkami.
- Skażenie tablicy wybitnie sterylizowanej z Test-setem: Jeśli twój projekt wielokrotnie dostosowywał hyper parametry lub dokonywał cięć decyzyjnych zaglądając do logiki w test-data – ten folder to teraz drugie śmietnisko użyte na walidacji i nic mądrego i optymalnego uogólnieniem na nim do świata zewnętrznego po fuzji ML nie osiągniesz, straciłeś całą ochronę badawczą i rzut o szlachetności pod oceny obiektywnej optymalizacji algorytmu. Odcinaj bezwzględnie rzuty tylko i wyłącznie kiedy masz stuprocentową wizje u wgrania mechaniki i algorytmu gotowego na start pod implementację rynkową.

## Krok 7: Złożenie do Wniosków – Wydruk Zestawienia Obliczeniowego Ostatniej Linii

- Model przetrenowany na połączonym zlewku informacji paczki szkoleniowej po fuzji po walidacyjnym teście i dogranych wektorach na parametrach by nabrać jak najgrubszy pancerz przed testowaniem fali wyjściowej pod estymator rzeczywisty.
- Odcięta ostateczna pieczęć o wskaźnik i puszczona ustronnie rzutnia procedury sprawdzającej i oceniającej maszynę przez Set - TEST-owy bez żadnych odwrotów wstecz pod parametry. Odczytaj ostateczny wynik bez opcji pod zmianę – to on na zawsze uwiecznia i jest flagą statystyki o mocy dla algorytmu rzuconego z gniazda.
- Zamieść w dokumentacji architekta pod ML (np. przy wnioskach) docelowy metryk wyliczony punktowy dla miar precyzyjnych lub obcięcia MSE w kooperacji z marginesem o rygorystycznym błędzie obostrzeń na 95 procentowych strefach krzyżowych (przedziały ujęte i ufnosć statystyczna miar z estymatora std i powiązań od ułożenia po T-Student).
- Podsumuj wydania tabel ze statystyki na dno wycinków dodając adnotacje i adwersarza rzutów z Bazowych z Baseline - uogólnieniem pokazując w ilu odsetkach Twoja technologia rzuciła w firmę i budżet poprawą ułożenia i szacunku względem tanich z osądu ślepych rozwiązań, jakimi obdarzyła was uprzednio "głupia decyzja lub uśrednianie" dla modelu nie wymagającego od procesora zasobów na naukę ML.
