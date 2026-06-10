---

name: skill-probability-reasoning
description: Wybierz właściwy rozkład prawdopodobieństwa dla danego problemu ML
version: 1.0.0
phase: 1
lesson: 6
tags: [probability, distributions, modeling]

---

# Wybór rozkładu prawdopodobieństwa

Jak wybrać właściwy rozkład podczas modelowania danych, projektowania funkcji straty lub ustalania prawdopodobieństw a priori (priorów).

## Lista kontrolna decyzji

1. Czy zmienna wynikowa jest dyskretna (kategorie, zliczenia), czy ciągła (pomiary, wartości ciągłe)?
2. Czy zmienna jest ograniczona (np. do przedziału [0, 1]), czy nieograniczona?
3. Ile jest możliwych wyników? Dwa? k? Nieskończenie wiele?
4. Czy rozkład danych jest symetryczny, czy skośny (asymetryczny)?
5. Czy zdarzenia są niezależne, czy skorelowane?
6. Czy modelujesz współczynnik, liczebność, proporcję czy pomiar?

## Drzewo decyzyjne rozkładów

```text
Czy zmienna jest dyskretna?
  Tak --> Tylko 2 wyniki? --> Bernoulliego (p)
      |   k wyników, jedna próba? --> Kategoryczny (p1...pk)
      |   k wyników, n prób? --> Wielomianowy (n, p1...pk)
      |   Liczba sukcesów w n próbach? --> Dwumianowy (n, p)
      |   Liczba zdarzeń w przedziale czasu? --> Poissona (lambda)
      |   Liczba prób do pierwszego sukcesu? --> Geometryczny (p)
      |   Liczba prób do r sukcesów? --> Ujemny dwumianowy (r, p)
  Nie --> Symetryczny, kształt dzwonu? --> Normalny (mu, sigma)
      |   Wartości dodatnie, prawoskośny? --> Lognormalny lub Wykładniczy
      |   Ograniczony do [0, 1]? --> Beta (alpha, beta)
      |   Wartości dodatnie, elastyczny kształt? --> Gamma (alpha, beta)
      |   Czas między zdarzeniami? --> Wykładniczy (lambda)
      |   Wymagane grube ogony? --> t-Studenta (nu) lub Cauchy'ego
      |   Wielowymiarowy, kształt dzwonu? --> Wielowymiarowy normalny
      |   Na sympleksie (sumuje się do 1)? --> Dirichleta (alpha)
```

## Przyporządkowanie rozkładów do rzeczywistych scenariuszy ML

| Scenariusz | Rozkład | Parametry |
|---|---|---|
| Wynik klasyfikacji binarnej | Bernoulliego | p = sigmoida(logit) |
| Wyniki klasyfikacji wieloklasowej | Kategoryczny | p = softmax(logity) |
| Przewidywanie tokenów w modelach językowych | Kategoryczny nad słownikiem | p z funkcji softmax |
| Intensywność pikseli (znormalizowana) | Beta lub Jednostajny na [0, 1] | Zależą od statystyk obrazu |
| Liczba słów w dokumencie | Poissona | lambda = średnia liczba słów |
| Czas między żądaniami użytkownika | Wykładniczy | lambda = częstotliwość żądań |
| Błąd pomiaru | Normalny | mu = 0, sigma z danych |
| Inicjalizacja wag | Normalny lub Jednostajny | Reguły He (Kaiminga) / Xaviera |
| Rozkład a priori w przestrzeni ukrytej VAE | Standardowy normalny | mu = 0, sigma = 1 |
| Bayesowski prior dla proporcji | Beta | alfa, beta oparte na przekonaniach a priori |
| Bayesowski prior dla wag kategorycznych | Dirichleta | wektor alfa |
| Szum w celach regresji | Normalny | mu = 0, estymowana sigma |
| Regresja odporna na wartości odstające | t-Studenta | mała liczba stopni swobody |
| Modelowanie czasu trwania/życia (survival) | Weibulla lub Gamma | kształt i skala |
| Rozkład tematów w dokumencie (LDA) | Dirichleta | średnia alfa < 1 dla rzadkich reprezentacji |

## Kiedy wybór rozkładu zawodzi

- Użycie rozkładu normalnego, gdy dane mają ścisłe dolne ograniczenie (np. ceny, odległości). Rozkład normalny przypisuje niezerowe prawdopodobieństwo wartościom ujemnym. Zamiast tego użyj rozkładu lognormalnego lub gamma.
- Użycie rozkładu Poissona, gdy wariancja różni się od średniej. Rozkład Poissona zakłada, że średnia = wariancja. Jeśli wariancja > średniej (nadmierna dyspersja), użyj ujemnego rozkładu dwumianowego.
- Użycie rozkładu Bernoulliego do problemów wieloklasowych. Rozkład Bernoulliego jest ściśle binarny. Użyj rozkładu kategorycznego dla k > 2.
- Zakładanie niezależności, gdy obserwacje są skorelowane. Szeregi czasowe, dane przestrzenne i dane pogrupowane naruszają to założenie. W takich przypadkach używaj modeli autoregresyjnych lub hierarchicznych.

## Typowe błędy

- Mylenie wartości funkcji gęstości prawdopodobieństwa (PDF) z samym prawdopodobieństwem. Wartość PDF może przekraczać 1. Prawdopodobieństwo wynika z całkowania funkcji gęstości w określonym przedziale.
- Zapominanie, że wyniki funkcji softmax reprezentują prawdopodobieństwa kategoryczne, a nie niezależne prawdopodobieństwa w rozkładzie Bernoulliego. Z definicji sumują się one do 1.
- Używanie jednostajnego rozkładu a priori (uniform prior), gdy dysponujesz wiedzą dziedzinową. Informacyjne priory zmniejszają wariancję estymatorów bez zniekształcania ostatecznego wyniku, o ile są dobrze dobrane.
- Traktowanie logarytmów prawdopodobieństw (log-probabilities) jak zwykłych prawdopodobieństw. Log-prawdopodobieństwa są zawsze ujemne (lub równe zero). Nie sumują się do 1.

## Krótkie zestawienie: Właściwości rozkładów

| Rozkład | Nośnik (Support) | Wartość oczekiwana | Wariancja | Kluczowa właściwość |
|---|---|---|---|---|
| Bernoulliego(p) | {0, 1} | p | p(1-p) | Najprostszy rozkład dyskretny |
| Dwumianowy(n, p) | {0..n} | np | np(1-p) | Suma n niezależnych prób Bernoulliego |
| Poissona(lam) | {0, 1, 2, ...} | lam | lam | Średnia = wariancja |
| Normalny(mu, s^2) | (-inf, inf) | mu | s^2 | Rozkład o maksymalnej entropii dla danej średniej i wariancji |
| Wykładniczy(lam) | [0, inf) | 1/lam | 1/lam^2 | Brak pamięci (memorylessness) |
| Beta(a, b) | [0, 1] | a/(a+b) | ab/((a+b)^2(a+b+1)) | Koniugat (prior sprzężony) do dwumianowego |
| Gamma(a, b) | (0, inf) | a/b | a/b^2 | Koniugat do Poissona |
| Dirichleta(alfa) | Sympleks | alfa_i/suma | (patrz wzór) | Koniugat do kategorycznego / wielomianowego |
