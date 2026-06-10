---

name: skill-clustering-guide
description: Wybierz odpowiedni algorytm grupowania w oparciu o kształt danych, szum i ograniczenia
version: 1.0.0
phase: 2
lesson: 7
tags: [clustering, k-means, dbscan, hierarchical, gmm, unsupervised]

---

# Przewodnik po wyborze algorytmu grupowania

Klastrowanie nie ma jednego najlepszego algorytmu. Właściwy wybór zależy od kształtu klastra, tego, czy znasz liczbę klastrów, ile szumu jest w danych i jak duży jest zbiór danych.

## Lista kontrolna decyzji

1. Czy znasz liczbę klastrów?
   - Tak: K-średnie lub GMM
   - Nie: DBSCAN (automatycznie wyszukuje klastry) lub hierarchiczny (przecina dendrogram na różnych poziomach)

2. Jaki kształt mają skupiska?
   - Mniej więcej kulisty (podobny do plamy): K-średnie
   - Eliptyczne o różnych rozmiarach: GMM
   - Dowolne kształty (półksiężyce, pierścienie, łańcuchy): DBSCAN
   - Zagnieżdżone lub hierarchiczne: grupowanie hierarchiczne

3. Czy dane zawierają szum lub wartości odstające?
   - Tak: DBSCAN (wyraźnie oznacza punkty szumu) lub GMM (punkty o niskim prawdopodobieństwie są wartościami odstającymi)
   - Nie: K-średnie są w porządku

4. Czy potrzebujesz miękkich przypisań (prawdopodobieństw)?
   - Tak: GMM podaje P(klaster | punkt danych) dla każdego klastra
   - Nie: K-Means lub DBSCAN dają trudne zadania

5. Jak duży jest zbiór danych?
   - Poniżej 10 000: działa każdy algorytm
   - 10 000 do 1 000 000: K-średnie (szybkie), mini-partie K-średnie (szybsze)
   - Ponad 1 000 000: Mini-partia K-Means lub BIRCH. Hierarchiczna jest zbyt powolna.

## Kiedy zastosować każde podejście

**K-średnie**: domyślny punkt początkowy. Szybki (O(n * k * iteracji)), prosty i wystarczająco dobry do wielu problemów. Użyj metody łokcia lub wyniku sylwetki, aby wybrać K. Ograniczenia: zakłada klastry kuliste, wrażliwe na inicjalizację (użyj K-Means++ lub uruchom wiele razy), nie radzi sobie dobrze ze zmiennymi rozmiarami klastrów.

**DBSCAN**: najlepszy do odkrywania skupień o dowolnym kształcie i automatycznego wykrywania wartości odstających. Dwa parametry: eps (promień sąsiedztwa) i min_samples (minimalna gęstość). Nie wymaga określenia K. Ograniczenia: problemy, gdy klastry mają bardzo różną gęstość, a dostrojenie eps może być trudne. Użyj wykresu k-odległości, aby oszacować eps: oblicz odległość do k-tego najbliższego sąsiada każdego punktu, posortuj i poszukaj łokcia.

**Hierarchiczny (aglomeracyjny)**: buduje drzewo połączeń. Przydatne, gdy chcesz zbadać strukturę skupień na wielu poziomach szczegółowości (wytnij dendrogram na różnych wysokościach). Połączenie Warda działa najlepiej w przypadku klastrów kompaktowych. Pojedyncze połączenie znajduje wydłużone skupiska, ale jest wrażliwe na szum. Ograniczenia: pamięć O(n^2) i czas O(n^3), więc niepraktyczne w przypadku dużych zbiorów danych.

**GMM (Gaussian Mixture Models)**: miękkie grupowanie z przypisaniami probabilistycznymi. Modeluje każdy klaster jako rozkład Gaussa z własną średnią i kowariancją. Lepsze niż K-średnie, gdy klastry są eliptyczne lub nakładają się. Aby wybrać liczbę komponentów, użyj BIC (Bayesowskie kryterium informacyjne). Ograniczenia: zakłada rozkłady Gaussa, może zawieść w przypadku kształtów niewypukłych, jest wrażliwy na inicjalizację.

## Ocena jakości klastra (bez etykiet)

| Metryczne | Co mierzy | Zakres | Użyj, gdy |
|--------|-------|-------|---------|
| Wynik sylwetki | Spójność a separacja | -1 do 1 (wyżej tym lepiej) | Porównywanie wartości K lub algorytmów |
| Bezwładność (w obrębie klastra SS) | Szczelność klastrów | 0 do inf (niżej tym lepiej) | Metoda łokcia dla K-średnich |
| BIC / AIC | Dopasowanie modelu z karą za złożoność | Niżej jest lepiej | Wybór liczby komponentów GMM |
| Indeks Calińskiego-Harabasza | Stosunek między wariancją w granicach | Wyżej jest lepiej | Szybkie porównanie |
| Indeks Daviesa-Bouldina | Średnie podobieństwo klastrów | Niżej jest lepiej | Karze nakładające się klastry |

## Typowe błędy

- Uruchamianie średnich K bez funkcji skalowania (w obliczaniu odległości dominują cechy w większych skalach)
- Wybieranie K poprzez przyglądanie się danym w 2D, gdy rzeczywiste dane są wielowymiarowe (użyj wyników sylwetki)
- Używanie średnich K w klastrach niesferycznych (dane w kształcie półksiężyca lub pierścienia wymagają DBSCAN)
- Ustawienie zbyt dużego eps DBSCAN (wszystko w jednym klastrze) lub zbyt małego (wszystko jest szumem)
- Traktowanie etykiet klastrów jako podstawowej prawdy (grupowanie ma charakter eksploracyjny; sprawdzaj na podstawie wiedzy dziedzinowej)
- Uruchamianie hierarchicznego grupowania na zbiorach danych zawierających ponad 20 000 punktów (eksplozja pamięci i czasu)

## Szybkie odniesienie

| Algorytm | Kształt klastra | Znajduje K | Obsługuje hałas | Miękkie zadania | Skalowalność |
|---------------|--------------|---------|---------------|--------------------------------|------------|
| K-Średnie | Sferyczny | Nie (ustawiasz K) | Nie | Nie | Miliony |
| Mini-partia K-Średnie | Sferyczny | Nie | Nie | Nie | Dziesiątki milionów |
| DBSCAN | Dowolne | Tak | Tak | Nie | Setki tysięcy |
| Hierarchiczny | Dowolny (zależny od połączenia) | Elastyczny (dendrogram cięty) | Zależy od powiązania | Nie | Poniżej 20 tys. |
| GMM | Eliptyczny | Nie (ustawiasz K) | Częściowe (małe prawdopodobieństwo) | Tak | Poniżej 100 tys. |
| HDBSCAN | Dowolne | Tak | Tak | Częściowe | Setki tysięcy |