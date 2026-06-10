---
name: skill-clustering-guide
description: Przewodnik po wyborze algorytmu klastrowania na podstawie kształtu danych, obecności szumu i ograniczeń obliczeniowych.
version: 1.0.0
phase: 2
lesson: 7
tags: [clustering, k-means, dbscan, hierarchical, gmm, unsupervised]
---

# Przewodnik po wyborze algorytmu klastrowania

W dziedzinie klastrowania nie istnieje jeden uniwersalny algorytm idealny do wszystkich zastosowań. Właściwy wybór zależy od kształtu klastrów, wiedzy o ich oczekiwanej liczbie, poziomu zaszumienia danych oraz rozmiaru zbioru danych.

## Lista kontrolna

1. Czy znana jest ci (lub pożądana) z góry liczba klastrów?
   - Tak: Użyj algorytmu K-Means (K-średnich) lub GMM (Gaussian Mixture Models).
   - Nie: Użyj DBSCAN (automatycznie odkrywa liczbę klastrów) lub grupowania hierarchicznego (pozwala odciąć dendrogram na pożądanym poziomie granularności).

2. Jaki przewidujesz kształt skupisk w danych?
   - Mniej więcej sferyczny/okrągły (podobny do kropel/chmur): K-Means.
   - Eliptyczny, o różnych rozmiarach i ułożeniach osi: GMM.
   - Skomplikowany, dowolny i nieliniowy (półksiężyce, pierścienie, zawiłe pasma): DBSCAN.
   - Hierarchiczny, zagnieżdżony jedne w drugich: Grupowanie hierarchiczne (Aglomeracyjne).

3. Czy w zbiorze danych występuje dużo szumu informacyjnego lub wartości odstających (outlierów)?
   - Tak: DBSCAN (izoluje outliery pod pojęciem "szumu") lub GMM (izoluje outliery za pomocą wskaźników minimalnego prawdopodobieństwa).
   - Nie: K-Means poradzi sobie bez problemu.

4. Czy wymagasz miękkich przypisań (prawdopodobieństw przynależności do klastra)?
   - Tak: GMM zwraca prawdopodobieństwo `P(klaster | punkt)` dla absolutnie każdego podziału.
   - Nie: K-Means oraz DBSCAN stosują tak zwane przypisania twarde (punkt należy w 100% do jednego klastra lub jest odpadem).

5. Jak duży jest zbiór danych?
   - Poniżej 10 000 próbek: Możesz spokojnie wykorzystać dowolny algorytm.
   - Od 10 000 do 1 000 000 próbek: K-Means jest bardzo optymalne. Wersja `Mini-batch K-Means` zapewnia jeszcze lepszą wydajność.
   - Powyżej 1 000 000 próbek: Należy zastosować `Mini-batch K-Means` lub algorytm BIRCH. Klastrowanie hierarchiczne nie wchodzi tu w grę.

## Charakterystyka algorytmów

**K-Means (K-średnich):** Domyślny punkt startowy i swoisty standard rynkowy. Bardzo szybki (`O(n * k * iteracje)`), koncepcyjnie prosty i "wystarczająco dobry" do wielu prostych problemów. Użyj metody łokcia (Elbow method) lub metryki sylwetki (Silhouette score), aby odszukać optymalną liczbę `K`. Ograniczenia: algorytm narzuca klastrom sferyczność, słabo radzi sobie ze zmienną objętością zbiorów względem siebie, jest wrażliwy na to gdzie wylądują losowo centroidy na starcie (bezwzględnie stosuj inicjalizację `K-Means++`).

**DBSCAN:** Król detekcji szumu i odkrywania struktur przypominających nieregularne bryły. Korzysta z dwóch parametrów: promienia zasięgu `eps` i obostrzenia gęstościowego w postaci minimalnej liczby sąsiadów `min_samples`. Całkowicie wyręcza programistę z narzucania z góry wartości `K`. Ograniczenia: potężnie gubi się i kapituluje jeśli poszczególne klastry cechują się drastycznie odmiennymi poziomami gęstości struktury, ponadto dostrajanie parametru `eps` bez wizualizacji jest z reguły trudne. Rada: Użyj wykresu z wartością na k-tej pozycji (k-distance plot), aby pomóc algorytmowi wyznaczyć próg załamania `eps`.

**Hierarchiczne (Aglomeracyjne):** Buduje imponujące struktury w formie drzew łączących najdrobniejsze punkty w wielkie rodziny. Kapitalnie się sprawdza, gdy pragniemy dogłębnie zbadać sieć, wyodrębniając w razie konieczności wyższy lub niższy rzut agregacyjny, tnąc model przez dowolne miejsce węzła (dendrogram). Powiązanie typu Warda świetnie wiąże zbite struktury. Ograniczenia: katastrofalnie żarłoczny pod kątem pamięciowym (`O(n^2)`) jak i obliczeniowym (`O(n^3)`), z góry eliminując go do zabaw przy masowych wolumenach Big Data.

**GMM (Gaussian Mixture Models):** Zaawansowany matematycznie gigant oparty na koncepcji miękkich podziałów i alokacji stochastycznej. Opiera założenie na mieszaniu różnorodnych układów wielowymiarowych ułożonych po linii dzwona Gaussa. Lepszy od modelu K-średnich we wszystkim w czym K-średnie polega, radząc sobie z nakładającymi (przecinającymi) się na siebie płaszczyznami lub asymetrycznymi zgrupowaniami danych. Ograniczenia: opiera logikę bezwzględnie na normalności (Gaussian), polegnie na strukturach o niewypukłych (nieokrągłych w jakikolwiek sposób) bryłach.

## Ocena jakości klastrowania (gdy brak etykiet)

| Wskaźnik | Co dokładnie mierzy? | Zasięg wartości | W jakim przypadku stosować? |
|--------|-------|-------|---------|
| Wynik Sylwetki (Silhouette score) | Spójność wewnętrzną punktów a izolację względem obcych sąsiadów. | Od -1 do 1 (im wyższa tym precyzyjniejsza jakość podziału). | Porównania iteracji wielu `K` w poszukiwaniu rzetelnego, prawdziwego grupowania. |
| Bezwładność (Inertia, SS wewnątrz klastrów) | Wewnętrzna szczelność i rygor. | Od 0 w nieskończoność (im bliżej do zera tym zwartszy klaster). | Pomiary z wdrożeniem metody łokcia dla zdiagnozowania K-Means. |
| BIC / AIC | Dopasowanie wielowymiarowe do wariantu z wpisaną silną karą za przeuczenie. | Niżej znaczy lepiej. | Optymalizacje do doboru idealnej liczby komponentów w modelu struktury GMM. |
| Indeks Calińskiego-Harabasza | Stosunek korelacji wariancji pomiędzy środkami a wariancją węzłów otoczenia klastra. | Wyżej jest lepiej. | Uproszczone rzuty porównawcze między paroma testowanymi na brudno ułożeniami. |
| Indeks Daviesa-Bouldina | Poziom uśrednionego upodabniania się jednego klastra do drugiego. | Niżej jest lepiej. | Agresywnie karze model w przypadku gdy klastry mocno zlewają się ze sobą. |

## Typowe błędy i pułapki

- Wdrożenie K-Means w obieg **bez absolutnej standaryzacji, czy skalowania**. Algorytm w ciemno rzuci uwagę na kolumnę w której wariancje i różnice osiągają skale od 0-5000 punktów, w pełni odcinając jakiekolwiek znaczenie od wariancji skaczących o wartości dziesiętne z kolumny sąsiedniej.
- Bazowanie we wnioskach po sprawdzeniu tylko 2 zmiennych przy użyciu oka rzuconego w prosty dwuwymiarowy wykres kropkowy dla bardzo zaawansowanych systemów. Posługuj się wskaźnikami rzetelnego pomiaru sylwetki.
- Usilne dociskanie problemów klastrami typu K-Means, kiedy na "oko" zbiór przypomina rozlaną wstęgę, rurę lub ułożony jest we fali – w takich warunkach z automatu narzuca się DBSCAN.
- Parametryzacja DBSCAN: Skrócenie (minimalizacja) parametru `eps` doprowadzi to tego, że DBSCAN wszystko z marszu zaetykietuje i wyrzuci do szumu. Maksymalizacja (powiększenie eps na odlew) stworzy z wszystkiego jeden, gigantyczny zlewający się w papkę klaster bez jakichkolwiek izolacji.
- Oczekiwanie i założenie, że to co pokaże algorytm staje się jedyną słuszną prawdą dla danego problemu merytorycznego. To tylko i aż procesor, bez zaplecza rozumienia sfer i uwarunkowań biznesowo-funkcjonalnych. Oceniaj i analizuj wyniki krytycznie.
- Uruchamianie procedur Hierarchicznych z podziałami Agglomeracyjnymi na masowym zbiorze wynoszącym więcej jak kilkadziesiąt tysięcy krotek. Załatwisz w ten sposób w krótkim czasie eksplozję pamięci lub katastrofalnie udusisz obciążenie procesora.

## Krótkie podsumowanie i referencja

| Algorytm | Profil Kształtu | Automatyczne znalezienie liczby K | Separuje i izoluje Szum? | Pozwala na Miękkie (Soft) Probabilistyczne przynależności? | Praktyczny górny limit ilości rekordów |
|---------------|--------------|---------|---------------|--------------------------------|------------|
| K-Means | Sferyczny (wypukły) | Odrzuca (Programista narzuca) | Kategorycznie Nie | Nie | Rzędu Milionów |
| Mini-batch K-Means | Sferyczny (wypukły) | Odrzuca | Nie | Nie | Rzędu Dziesiątek Milionów |
| DBSCAN | Pełna Dowolność Kształtów | Autodetekcja | Rewelacyjnie (Tak) | Nie | Rzędu Setek Tysięcy |
| Hierarchiczny | Zależny od powiązania i zastosowanej agregacji | Elastyczne docinanie na bazie wykresu uciętego dendrogramu | Skorelowane pod zastosowane powiązanie (linkage) | Nie | Rzędu Dziesiątek Tysięcy (Max) |
| GMM | Eliptyczne (z wypłaszczeniem) | Odrzuca | Wyłapuje po odrzuceniu małych prawdopodobieństw w dystrybucji Gaussa | Zdecydowanie Tak | Rzędu Setek Tysięcy |
| HDBSCAN | Pełna Dowolność Kształtów | Autodetekcja | Zdecydowanie Tak | Częściowo | Rzędu Setek Tysięcy |
