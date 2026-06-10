---

name: skill-regression
description: Wybierz odpowiednie podejście regresyjne w oparciu o charakterystykę danych i ograniczenia problemu
version: 1.0.0
phase: 2
lesson: 2
tags: [regression, linear-regression, polynomial-regression, ridge, regularization]

---

# Przewodnik po strategii regresji

Algorytmy regresyjne służą do predykcji wartości ciągłych. Optymalny wybór metody zależy od tego, jak układa się korelacja między cechami a celem, jaka jest ich liczba, a także jak silne występuje zagrożenie zjawiskiem przeuczenia (overfittingu).

## Lista kontrolna decyzji

1. Czy zależność pomiędzy cechami a zmienną docelową jest w przybliżeniu liniowa?
   - Tak: rozpocznij proces od zastosowania najprostszej zwykłej regresji liniowej
   - Nie: przetestuj dodanie cech wielomianowych lub zastosuj nieliniowe modele

2. Jak dużą liczbą cech dysponujesz w odniesieniu do liczby posiadanych próbek?
   - Mała liczba cech, duża ilość próbek: zwykła regresja liniowa poradzi sobie z tym bez kłopotu
   - Liczne cechy, stosunkowo mało próbek: zastosuj w tym wypadku odpowiednią dla ciebie regularyzację (Ridge lub Lasso)
   - Przewaga liczby cech nad liczbą próbek: Lasso (L1) pozwoli na automatyczne wyselekcjonowanie najbardziej użytecznych cech, natomiast Ridge (L2) ściągnie i wyrówna wartości wag.

3. Czy wymagana jest interpretowalność wyników?
   - Tak: wystarczająca powinna być powszechna regresja liniowa z niewielką ilością cech, albo w ostateczności wykorzystanie Lasso i jej mechanizmu automatycznej selekcji zmiennych 
   - Nie: można spróbować cech wielomianowych lub wdrożyć złożone i nieinterpretowalne w prosty sposób modele maszynowe bazujące na losowych drzewach decyzyjnych albo architekturach sztucznych sieci neuronowych

4. Czy przetwarzasz niewielki rozmiarowo zbiór danych (mniejszy niż 10 000 rekordów)?
   - Zastosuj podejście oparte na wykorzystaniu normalnego równania (rozwiązanie bazujące na bezpośrednim wykorzystaniu formy zamkniętej algorytmu), w ten sposób zoptymalizujesz procesy obliczeniowe
   - Zastosuj mechanizm walidacji krzyżowej (cross-validation) do uzyskania rzetelnej oceny wyników modelu.

5. Czy analizowany zestaw zawiera niezwykle dużą bazę danych (sięgającą pułapu rzędu wielu milionów zgromadzonych wierszy)?
   - Implementuj w projekcie zniżanie stochastycznym gradientem (SGD, Stochastic Gradient Descent), alternatywą może tu okazać się wdrożenie procedury spadku gradientu z wykorzystaniem koncepcji mini-partii danych (Mini-batch Gradient Descent)
   - Porzuć normalne podejście matematyczne z uwagi na spowalniający naturę odwracania rozległych zbiorów algorytm uwarunkowany inwersją badanej siatki na relacji O(n^3)

## Kiedy zastosować każde z podejść

**Zwykła regresja liniowa (OLS - Ordinary Least Squares)**: służy za referencyjny punkt startowy dla absolutnie wszelkiego rodzaju prac związanych z optymalizacją. Jeżeli jej skuteczność (opisana za pomocą współczynnika R-kwadrat) uchodzi za zadawalającą, a zdefiniowany przez nas program zachowuje proste fundamenty struktury z powstrzymaniem rozbudowy w bardziej skomplikowane odnogi, można zakończyć prace po jej poprawnym zastosowaniu.

**Regresja wielomianowa**: zalecana, gdy stworzone w toku prac wykresy rozrzutu ewidentnie udowadniają zjawisko nakreślenia przez obserwowane punkty ścieżek krzywej układającej się w inną aniżeli klasyczną formę prostej kształtkę. Punktem początkowym do poszukiwań adekwatnej struktury wielomianowej powinno uczynić się odgórnie drugi potęgowy wymiar. Dążenie w obrębie stopnia potęgowania algorytmu należy rozważać wyłącznie i tylko wówczas, jeśli ewaluacja zweryfikuje faktyczną do tego potrzebę na płaszczyźnie błędów badanej struktury w zestawieniu do oceny sprawdzającej. Ucieczka do budowy układów przewyższających graniczny wymiar > 5 skutkuje powszechnie przeuczeniem modeli.

**Regresja grzbietowa (Ridge, L2)**: polecana do projektów opartych na zbiorach posiadających wiele uwikłanych oraz wzajemnie zależnych pośród siebie własności. Mechanizm w procesie implementacji wymusza proporcjonalne ukształtowanie i zawężenie przypisanych do każdego jednego atrybutu wektorowych wag do ułamka stanowiącego oscylujące pobliże matematycznego zera (niedopuszczające tymże mechanizmem całkowitego skurczenia jakiegokolwiek z badanych argumentów bezpośrednio w ujemny pułap). Poleca się do prac, w obrębie w których zakładamy bezsporny udział całkowitego składu dostępnych atrybutów badawczych. 

**Regresja Lasso (L1)**: zalecana, w projektach gdzie na badacza czeka masa analizowanych czynników, a z doświadczenia oraz podejrzeń, wpływ na faktyczny wynik końcowy winny mieć jedynie śladowe, skrupulatnie oddzielone atrybuty. Mechanika ta ukierunkowuje najsłabsze w powiazaniach wagi na ściśle weryfikowane matematyczne zero - zapewniając całkowicie zautomatyzowany, niezależny proces rygorystycznego filtrowania powierzonych mu zasobów.

**Sieć elastyczna (Elastic Net)**: sprawna fuzja, która uosabia w sobie najsilniejsze zalety modeli uwzględniających oba wspomniane wyżej kary matematyczne (L1+L2). Wykorzystaj to rozwiązanie, w pracy z zadaniem gdzie wykreowanych wielościowo atrybutów powielających korelacje będzie niezwykle dużo i potrzebny ci zautomatyzowany odgórnie proces wyodrębniający dla ciebie solidne funkcje.

## Typowe błędy

- Ominięcie wykonania kluczowych dla operacji zadań zdefiniowanych procedurami standaryzacji dostępnych dla systemu uwarunkowań - ujednolicenia skal (tzw. "feature scaling") dokonywanych bezspornie zawsze przed wprowadzeniem ich w samą pętlę spadku algorytmicznego gradientu powoduje odgórnie bardzo bolesną powolność dla zbliżającego zbiegania wyników z celem u szczytu lejka badawczego
- Wdrażanie oceniającej puli danych testowych dla wariacji modyfikacji poszczególnych zmiennych optymalizacyjnych hiperparametrów - (powinno się posłużyć uformowanym do takich działań wyodrębnionym wyselekcjonowaniem punktów ze zbioru w ułożeniu weryfikacyjnym dla walidacji lub uformowaną siecią analiz krzyżowych w całym systemie)
- Nadpisywanie modeli opartych w strukturze funkcji wielomianów nadrzędnego formatu podyktowane jedynie chęcią zmniejszenia pomyłki ukazywanej dla zebranych dla treningów wyników przy ignorowaniu oceny dla danych w pakiecie z puli przeznaczonej z weryfikacji walidacyjnej błędu (treningowy współczynnik determinacji R^2 zawsze nieuchronnie pnie się w potęgach swojego stopnia udowadniając swój iluzoryczny ubytek błędu w testach uczenia dla zawiłych ułożeń powiązanych składowych elementów).
- Zaniedbywanie monitoringu oceniających układ nakreśleń krzywych resztkowych ("residual plots") podsumowującego całościowo stan układu (nawet wygórowany punktowo wskaźnik R^2 stanowić tu potrafi czynnik zwodniczy pod zawiłym ukryciem schematyzmów występujących relacjach badanych struktur wyciągających rezydua na swych osiach do skrajnych odkształceń form).
- Fiksacja dla statystyk ujętych ramą współczynnika determinacji (R^2), polegająca z całą odpowiedzialnością jako bezspornie i osamotnionym z drogowskazem na płaszczyźnie obranego punktu oceny działania maszyny (podczas podjętych projektów z odgórnie podanym powagą uwzględnienia wymogów określonych specyfikacją dedykowanych dziedzin dla których zaleca się stałą orientację wobec oceny w zestawieniu weryfikacji powszechnych miar takich jak średniego formatu bezwzględnych strat błędu dla modelu tj. wskaźnika oceniającego - MAE lub monitorowanego na widok form reszt i rozkładu zmienności rzędu statystycznych szacunków.)

## Szybkie podsumowanie

| Metoda | Kiedy używać | Typ regularyzacji | Zdolność do wyboru cech |
|------------|------------|---------------|--------------------------------|
| OLS (zwykła) | Punkt bazowy, mała liczba cech | Brak | Dokonywany ręcznie |
| Grzbietowa (Ridge) | Wiele cech, wszystkie są przypuszczalnie istotne | L2 (kurczenie wag) | Brak takiej możliwości |
| Lasso | Wiele cech, tylko ułamek faktycznie wnosi informację | L1 (redukcja wag z dociągnięciem zerowym) | Działa automatycznie (wbudowana strukturalnie) |
| Elastic Net (Elastyczna siatka) | Mnogość zebranych parametrów uzupełniających korelacje | Mieszana (L1 + L2) | Połowiczna skuteczność działania dla wyodrębniania elementu |
| Wielomianowa | Odkryte w badaniach warianty krzywoliniowych układów z zachowaniem zmienności czynników | Komplementarna z implementacjami układów w formatach (Ridge/Lasso) w dodatkowej składowej mechanizmu nakładanej odgórnie dla systemu | Ręcznie narzucona bariera określeniami dla wpisanych za kryteria algorytmowi poszukiwań stopni dla dopasowania relacji krzywej |
