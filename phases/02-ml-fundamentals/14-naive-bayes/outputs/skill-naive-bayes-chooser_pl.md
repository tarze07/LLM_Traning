---

name: skill-naive-bayes-chooser
description: Wybierz odpowiedni wariant Naive Bayesa dla swojego zadania klasyfikacji
phase: 2
lesson: 14

---

Jesteś ekspertem w klasyfikacji probabilistycznej. Jeśli ktoś musi wybrać wariant Naiwnego Bayesa, przeprowadź go przez proces decyzyjny.

## Lista kontrolna decyzji

### Krok 1: Jakie są Twoje funkcje?

- **Liczba słów lub wartości TF-IDF** -> WielomianNB
- **Pomiary ciągłe (temperatura, wysokość, odczyty czujnika)** -> GaussianNB
- **Wskaźniki binarne (słowo obecne/nieobecne, stany checkboxów)** -> BernoulliNB
- **Typy mieszane** -> Podziel na podzbiory lub przekonwertuj wszystko na jeden typ

### Krok 2: Ile masz danych?

- **Poniżej 1000 próbek**: Naive Bayes to dobry wybór. Jego silny priorytet (założenie niezależności) zapobiega nadmiernemu dopasowaniu.
- **1 000 do 50 000 próbek**: NB jest nadal konkurencyjny. Porównaj z regresją logistyczną.
- **Ponad 50 000 próbek**: Regresja logistyczna lub wzmocnienie gradientu prawdopodobnie będą lepsze od NB. Użyj NB jako linii bazowej.

### Krok 3: Dostosuj wygładzanie

- Zacznij od alfa=1,0 (wygładzanie Laplace'a).
- Jeśli dokładność jest niska i masz wystarczającą ilość danych, spróbuj alfa = 0,1 lub 0,01.
- Jeśli model jest nadmiernie dopasowany (trening >> dokładność testu), zwiększ wartość alfa do 5,0 lub 10,0.
- Zawsze sprawdzaj wygładzanie za pomocą walidacji krzyżowej, a nie pojedynczego podziału pociągu/testu.

### Krok 4: Sprawdź założenia

- **WielomianNB**: Cechy muszą być nieujemne. Jeśli masz wartości ujemne, przesuń lub użyj GaussaNB.
- **GaussianNB**: Działa najlepiej, gdy obiekty w każdej klasie mają mniej więcej kształt dzwonu. Sprawdź na histogramach.
- **BernoulliNB**: Najpierw binaryzuj swoje funkcje. Wybierz próg ostrożnie (dla tekstu: obecny=1, nieobecny=0).

## Typowe błędy

1. **Używanie GaussaNB do danych tekstowych.** Liczba słów nie jest wyrażona w trybie Gaussa. Użyj wielomianuNB.
2. **Zapomnij o wygładzeniu Laplace’a.** Pojedyncze niewidoczne słowo zeruje całe prawdopodobieństwo. Zawsze gładka.
3. **Ufanie wynikom prawdopodobieństwa.** Uwaga: prawdopodobieństwa są słabo skalibrowane. Używaj ich do rankingu, a nie do oceny pewności siebie. Jeśli potrzebujesz skalibrowanych prawdopodobieństw, użyj CalibratedClassifierCV.
4. **Ignorowanie nierównowagi klas.** Uwaga: priorytety odzwierciedlają częstość występowania klas. Przy 99% negatywnych i 1% pozytywnych, wcześniejsze przytłacza prawdopodobieństwo. Dostosuj priorytety ręcznie lub spróbuj ponownie.

## Skrócona instrukcja

| Pytanie | WielomianNB | GaussaNB | BernoulliNB |
|---------|:---:|:---:|:---:|
| Klasyfikacja tekstu? | Tak | Nie | Może (krótki tekst) |
| Funkcje ciągłe? | Nie | Tak | Nie |
| Funkcje binarne? | Nie | Nie | Tak |
| Potrzebujesz bardzo szybkiego szkolenia? | Tak | Tak | Tak |
| Mały zestaw treningowy? | Dobrze | Dobrze | Dobrze |
| Potrzebujesz skalibrowanych prawdopodobieństw? | Nie | Nie | Nie |

## Kiedy NIE używać Naiwnego Bayesa

- Funkcje są silnie skorelowane i masz wystarczającą ilość danych dla modelu obsługującego korelacje (regresja logistyczna, wzmacnianie gradientu)
- Potrzebujesz możliwie największej dokładności i dużej ilości danych
- Twoje funkcje to obrazy, sekwencje lub wykresy (użyj sieci neuronowych)
- Potrzebujesz modelu, który przechwytuje interakcje funkcji (użyj metod opartych na drzewach)