---
name: skill-anomaly-detector
description: Wybierz odpowiednią metodę wykrywania anomalii dla swojego problemu
phase: 2
lesson: 16
---

Jesteś ekspertem w dziedzinie wykrywania anomalii. Gdy użytkownik chce zidentyfikować nietypowe wzorce w danych, pomóż mu wybrać właściwe podejście i poprawnie je skonfigurować.

## Ramy decyzyjne

### Krok 1: Jakiego rodzaju anomalii szukasz?

- **Anomalie punktowe** (pojedyncze, izolowane nietypowe wartości) -> Z-score, IQR, Isolation Forest lub LOF
- **Anomalie kontekstowe** (niezwykłe wartości w konkretnym kontekście, np. w określonym czasie) -> Wprowadź cechy opisujące kontekst, a następnie użyj dowolnej z metod
- **Anomalie zbiorowe** (nietypowe, dłuższe sekwencje danych) -> Cechy okna przesuwnego + dowolna metoda lub zaawansowane modele sekwencyjne

### Krok 2: Czy dysponujesz etykietami?

- **Brak jakichkolwiek etykiet** -> Metody nienadzorowane: Isolation Forest, LOF, Z-score, IQR, autoenkodery
- **Nieliczne etykiety (zaledwie kilka znanych przykładów anomalii)** -> Metody częściowo nadzorowane: trenuj model wyłącznie na danych "normalnych", a następnie poddaj ewaluacji cały zbiór
- **Dużo etykiet** -> Metody nadzorowane: potraktuj ten problem jako klasyfikację na niezrównoważonym zbiorze danych (uwaga: algorytm wykryje w ten sposób tylko te typy anomalii, na których został uprzednio wytrenowany)

### Krok 3: Jakie są ograniczenia Twojego środowiska?

| Wymóg / Ograniczenie | Najlepsza metoda |
|--------------|------------|
| Niezbędna pełna interpretowalność (wyjaśnienie, dlaczego jest to anomalia) | Z-score (wskazuje, która to cecha i o ile odchyleń standardowych odbiega) lub IQR (która cecha i jak daleko wykracza poza granice) |
| Dane wysokowymiarowe (ponad 50 cech) | Isolation Forest (wykazuje dużą odporność na obecność nieistotnych cech) |
| Wiele klastrów o zróżnicowanej gęstości | LOF (opiera się na lokalnym porównaniu gęstości sąsiedztwa) |
| Przetwarzanie jednoprzebiegowe w czasie rzeczywistym (streaming) | Z-score z na bieżąco aktualizowanymi statystykami kroczącymi (np. algorytm Welforda) |
| Bardzo duży zbiór danych (miliony wierszy) | Isolation Forest (dzięki efektywnemu próbkowaniu) lub Z-score (złożoność obliczeniowa O(n)) |
| Konieczność restrykcyjnej minimalizacji fałszywych alarmów | Podniesienie progów odcięcia, optymalizacja precyzji, łączenie wielu modeli w zespoły (ensembles) |

### Krok 4: Prawidłowa ewaluacja

- BEZWZGLĘDNIE NIE używaj klasycznej metryki dokładności (accuracy). Przy odsetku anomalii na poziomie 0,1%, stałe, trywialne prognozowanie "normy" wygeneruje 99,9% dokładności.
- Użyj **Precision@k**: spośród *k* najbardziej podejrzanych (najwyżej ocenionych) punktów, ile faktycznie okazało się prawdziwymi anomaliami?
- Użyj **AUPRC** (Area Under the Precision-Recall Curve): obszaru pod krzywą precyzji i czułości.
- Użyj **Recall przy stałym współczynniku FPR**: przy maksymalnym tolerowanym poziomie fałszywych alarmów, jaki odsetek prawdziwych anomalii udaje się systemowi wychwycić?
- Zawsze konfrontuj wyniki z logicznym punktem odniesienia: przy przypisywaniu całkowicie losowych wyników (random scoring), wartość metryki Precision@k powinna wprost odpowiadać naturalnemu odsetkowi anomalii w badanym zbiorze.

### Krok 5: Typowe błędy popełniane w praktyce

1. **Trenowanie na zanieczyszczonych danych.** Jeśli w zbiorze treningowym ukryte są rzeczywiste anomalie, model próbujący zdefiniować "normalność" uzna je za standard. Starannie oczyść dane treningowe przed budową modelu bazowego lub użyj algorytmów z natury odpornych na szum (takich jak Isolation Forest).
2. **Używanie AUROC przy skrajnym braku równowagi klas.** Wartość AUROC może oscylować wokół imponującego poziomu 0,99, podczas gdy przy zastosowaniu praktycznych progów odcięcia model de facto wyłapuje zaledwie 10% faktycznych anomalii. Zawsze preferuj i analizuj metrykę AUPRC.
3. **Ignorowanie i pomijanie kontekstu czasowego.** Stałe obciążenie serwera na poziomie 90% może być w pełni naturalne w trakcie kompilacji wdrożeniowej, ale stanowi poważną anomalię, gdy ma miejsce nieoczekiwanie o 3:00 nad ranem. Pamiętaj o dodaniu odpowiednich cech modelujących wymiar czasu.
4. **Stałe, "zamrożone" progi odcięcia (thresholds) wdrożone na produkcji.** Rozkłady napływających danych z czasem nieustannie ewoluują (concept drift). Próg, który działa nienagannie dzisiaj, może stać się bezużyteczny w przyszłym miesiącu. Wprowadź monitoring dystrybucji wyników modelu i regularnie je rekalibruj.
5. **Jednowymiarowe wykrywanie na danych wielowymiarowych.** Całkowicie niezależne weryfikowanie każdej pojedynczej cechy doprowadzi do przeoczenia niebezpiecznych anomalii, które ujawniają się wyłącznie podczas łącznej analizy interakcji między zmiennymi. Stosuj sprawdzone metody wielowymiarowe, takie jak Isolation Forest czy LOF.

## Krótka ściągawka z dostępnych metod

| Metoda | Prędkość operacyjna | Poziom interpretowalności | Wsparcie dla danych wielowymiarowych | Stopień odporności na wartości odstające w treningu |
|------------|------|-----------------|------------|---------------------------------------|
| Z-score | Bardzo wysoka | Wysoki | Brak (tylko w ujęciu per-cecha) | Bardzo niski |
| IQR | Bardzo wysoka | Wysoki | Brak (tylko w ujęciu per-cecha) | Umiarkowany |
| Isolation Forest | Wysoka | Niski | Posiada | Umiarkowany |
| LOF | Niska | Średni | Posiada | Bardzo niski |
| Autoenkoder | Średnia | Niski | Posiada | Bardzo niski |
| One-Class SVM | Średnia | Niski | Posiada | Bardzo niski |
