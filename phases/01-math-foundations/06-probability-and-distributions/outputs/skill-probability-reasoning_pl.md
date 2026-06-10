---

name: skill-probability-reasoning
description: Wybierz właściwy rozkład prawdopodobieństwa dla danego problemu ML
version: 1.0.0
phase: 1
lesson: 6
tags: [probability, distributions, modeling]

---

# Wybór rozkładu prawdopodobieństwa

Jak wybrać właściwą dystrybucję podczas modelowania danych, projektowania funkcji straty lub ustalania priorytetów.

## Lista kontrolna decyzji

1. Czy wynik jest dyskretny (kategorie, zliczenia) czy ciągły (pomiary, wyniki)?
2. Czy wynik jest ograniczony (np. [0, 1]) czy nieograniczony?
3. Ile jest możliwych wyników? Dwa? k? Nieskończony?
4. Czy dane są symetryczne czy przekrzywione?
5. Czy zdarzenia są niezależne czy skorelowane?
6. Czy modelujesz wskaźnik, liczbę, proporcję czy pomiar?

## Drzewo decyzyjne dystrybucji

```
Is the variable discrete?
  Yes --> Only 2 outcomes? --> Bernoulli (p)
     |    k outcomes, one trial? --> Categorical (p1...pk)
     |    k outcomes, n trials? --> Multinomial (n, p1...pk)
     |    Count of successes in n trials? --> Binomial (n, p)
     |    Count of events per interval? --> Poisson (lambda)
     |    Count of trials until first success? --> Geometric (p)
     |    Count of trials until r successes? --> Negative Binomial (r, p)
  No --> Symmetric, bell-shaped? --> Normal (mu, sigma)
     |   Positive values, right-skewed? --> Log-normal or Exponential
     |   Bounded in [0, 1]? --> Beta (alpha, beta)
     |   Positive values, flexible shape? --> Gamma (alpha, beta)
     |   Time between events? --> Exponential (lambda)
     |   Heavy tails needed? --> Student's t (nu) or Cauchy
     |   Multivariate, bell-shaped? --> Multivariate Normal
     |   On a simplex (sums to 1)? --> Dirichlet (alpha)
```

## Mapowanie rzeczywistych scenariuszy ML na dystrybucje

| Scenariusz | Dystrybucja | Parametry |
|---|---|---|
| Dane wyjściowe klasyfikacji binarnej | Bernoulliego | p = sigmoida(logit) |
| Wyniki klasyfikacji wieloklasowej | Kategoryczny | p = softmax(logity) |
| Przewidywanie tokenów w modelach językowych | Kategoryczny ponad słownictwo | p z softmax |
| Intensywność pikseli (znormalizowana) | Beta lub jednolity [0, 1] | Zależy od statystyk obrazu |
| Liczba słów w dokumencie | Poissona | lambda = średnia liczba słów |
| Czas pomiędzy żądaniami użytkownika | wykładniczy | lambda = częstotliwość żądań |
| Błąd pomiaru | Normalny | mu = 0, sigma z danych |
| Inicjalizacja wagi | Normalny lub jednolity | Zasady Kaiminga/Xaviera |
| Przestrzeń ukryta VAE przed | Standardowy Normalny | mu = 0, sigma = 1 |
| Bayesowski priorytet proporcji | Beta | alfa, beta z wiary |
| Bayesowski priorytet wag kategorii | Dirichleta | wektor alfa |
| Hałas w celach regresji | Normalny | mu = 0, sigma oszacowana |
| Regresja odporna na wartości odstające | Studenta t | niskie stopnie swobody |
| Modelowanie czasu trwania/całego życia | Weibulla lub Gamma | kształt i skala |
| Rozkład tematów na dokument (LDA) | Dirichleta | średnia alfa < 1 for sparse |

## When distributions go wrong

- Using Normal when data has a hard lower bound (e.g., prices, distances). The normal assigns nonzero probability to negative values. Use log-normal or gamma instead.
- Using Poisson when the variance differs from the mean. Poisson assumes mean = variance. If variance >, użyj ujemnego dwumianu.
- Wykorzystanie Bernoulliego do problemów wieloklasowych. Bernoulli jest ściśle binarny. Użyj kategorycznego dla k > 2.
- Założenie niezależności, gdy obserwacje są skorelowane. Szeregi czasowe, dane przestrzenne i dane pogrupowane naruszają niezależność. Użyj modeli autoregresyjnych lub hierarchicznych.

## Typowe błędy

- Mylenie wartości PDF z prawdopodobieństwem. Plik PDF może przekraczać 1. Prawdopodobieństwo wynika z integracji pliku PDF w określonym przedziale czasu.
- Zapominanie, że wyniki softmax są prawdopodobieństwami kategorycznymi, a nie niezależnymi prawdopodobieństwami Bernoulliego. Sumują się do 1 według konstrukcji.
- Używanie munduru przed, jeśli masz wiedzę domenową. Priorytety informacyjne zmniejszają wariancję bez wpływania na wynik, jeśli są dobrze wybrane.
- Traktowanie prawdopodobieństw logarytmicznych jako prawdopodobieństw. Log-proby są zawsze ujemne (lub zerowe). Nie sumują się do 1.

## Krótkie odniesienie: właściwości dystrybucji

| Dystrybucja | Wsparcie | Znaczy | Wariancja | Kluczowa właściwość |
|---|---|---|---|---|
| Bernoulli(p) | {0, 1} | p | p(1-p) | Najprostszy dyskretny |
| Dwumian(n, p) | {0..n} | np. | np(1-p) | Suma n Bernoulliego |
| Poissona(lam) | {0, 1, 2, ...} | lam | lam | Średnia = wariancja |
| Normalny(mu, s^2) | (-inf, inf) | mu | s^2 | Maksymalna entropia dla danej średniej/var |
| Wykładniczy(lam) | [0, inf) | 1/lam | 1/lam^2 | Bez pamięci |
| Beta(a, b) | [0, 1] | a/(a+b) | ab/((a+b)^2(a+b+1)) | Koniugat do dwumianu |
| Gamma(a, b) | (0, inf) | a/b | a/b^2 | Koniugat do Poissona |
| Dirichlet(alfa) | Simplex | alfa_i/suma | (patrz wzór) | Koniugat z kategorycznym |