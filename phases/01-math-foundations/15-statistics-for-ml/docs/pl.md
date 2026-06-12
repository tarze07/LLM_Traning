# Statystyka dla Machine Learningu

> Statystyka pozwala wiedzieć, czy Twój model faktycznie działa, czy po prostu miał szczęście.

**Typ:** Build
**Język:** Python
**Wymagania wstępne:** Faza 1, Lekcje 06 (Probabilistyka i rozkłady), 07 (Twierdzenie Bayesa)
**Czas:** ~120 minut

## Cele nauki

- Obliczanie statystyk opisowych, korelacji Pearsona/Spearmana oraz macierzy kowariancji od podstaw
- Wykonywanie testów hipotez (test t, test chi-kwadrat) oraz prawidłowa interpretacja wartości p i przedziałów ufności
- Wykorzystanie resamplingu bootstrapowego do konstruowania przedziałów ufności dla dowolnej metryki bez zakładania rozkładu
- Odróżnianie istotności statystycznej od istotności praktycznej za pomocą miar wielkości efektu

## Problem

Wytrenowałeś dwa modele. Model A osiąga 0.87 na zbiorze testowym. Model B osiąga 0.89. Wdrażasz Model B. Trzy tygodnie później metryki produkcyjne są gorsze niż wcześniej. Co się stało?

Model B w rzeczywistości nie przewyższał Modelu A. Różnica 0.02 to był szum. Twój zbiór testowy był za mały, wariancja za duża, albo i to, i to. Wdrożyłeś losowość przebraną za poprawę.

To się zdarza nieustannie. Wstrząsy w rankingach Kaggle. Artykuły, których nie można odtworzyć. Testy A/B, które wskazują zwycięzcę na podstawie kilkuset próbek. Przyczyna jest zawsze ta sama: ktoś zignorował statystykę.

Statystyka daje narzędzia do odróżnienia sygnału od szumu. Mówi Ci, kiedy różnica jest prawdziwa, jak duże powinno być Twoje przekonanie, oraz ile danych potrzebujesz, by ufać wynikowi. Każdy pipeline ML, każde porównanie modeli, każdy eksperyment wymaga statystyki. Bez niej zgadujesz.

## Koncepcja

### Statystyka opisowa: podsumowanie danych

Zanim zaczniesz modelować, musisz wiedzieć, jak wyglądają Twoje dane. Statystyka opisowa kompresuje zbiór danych do kilku liczb, które ujmują jego kształt.

**Miary tendencji centralnej** odpowiadają na pytanie "gdzie jest środek?"

```
Mean:   sum of all values / count
        mu = (1/n) * sum(x_i)

Median: middle value when sorted
        Robust to outliers. If you have [1, 2, 3, 4, 1000], the mean is 202
        but the median is 3.

Mode:   most frequent value
        Useful for categorical data. For continuous data, rarely informative.
```

Średnia (mean) to punkt równowagi. Mediana (median) to punkt środkowy. Gdy się od siebie różnią, Twój rozkład jest skośny. Rozkłady dochodów mają średnią dużo większą niż mediana (skośność prawostronna spowodowana przez miliarderów). Rozkłady straty (loss) podczas treningu często mają średnią dużo mniejszą niż mediana (skośność lewostronna spowodowana łatwymi przykładami).

**Miary rozproszenia** odpowiadają na pytanie "jak rozproszone są dane?"

```
Variance:   average squared deviation from the mean
            sigma^2 = (1/n) * sum((x_i - mu)^2)

Standard deviation:  square root of variance
                     sigma = sqrt(sigma^2)
                     Same units as the data, so more interpretable.

Range:      max - min
            Sensitive to outliers. Almost never useful alone.

IQR:        Q3 - Q1 (interquartile range)
            The range of the middle 50% of the data.
            Robust to outliers. Used for box plots and outlier detection.
```

**Percentyle** dzielą posortowane dane na 100 równych części. 25. percentyl (Q1) oznacza, że 25% wartości znajduje się poniżej tego punktu. 50. percentyl to mediana. 75. percentyl to Q3.

```
For latency monitoring:
  P50 = median latency        (typical user experience)
  P95 = 95th percentile       (bad but not worst case)
  P99 = 99th percentile       (tail latency, often 10x the median)
```

W ML percentyle są ważne przy monitorowaniu latencji inferencji, rozkładach pewności predykcji oraz przy zrozumieniu rozkładów błędów. Model z niskim średnim błędem, ale tragicznym błędem P99, może być bezużyteczny w zastosowaniach krytycznych dla bezpieczeństwa.

**Statystyki próbki vs populacji.** Przy obliczaniu wariancji z próbki dzielimy przez (n-1) zamiast przez n. To poprawka Bessela. Kompensuje fakt, że średnia z próbki nie jest prawdziwą średnią populacji. Z n w mianowniku systematycznie nie doszacowujesz prawdziwej wariancji. Z (n-1) estymator jest nieobciążony.

```
Population variance: sigma^2 = (1/N) * sum((x_i - mu)^2)
Sample variance:     s^2     = (1/(n-1)) * sum((x_i - x_bar)^2)
```

W praktyce: jeśli n jest duże (tysiące próbek), różnica jest nieistotna. Jeśli n jest małe (kilkadziesiąt próbek), ma znaczenie.

### Korelacja: jak zmienne zmieniają się razem

Korelacja mierzy siłę i kierunek liniowej zależności między dwiema zmiennymi.

**Współczynnik korelacji Pearsona** mierzy zależność liniową:

```
r = sum((x_i - x_bar)(y_i - y_bar)) / (n * s_x * s_y)

r = +1:  perfect positive linear relationship
r = -1:  perfect negative linear relationship
r =  0:  no linear relationship (but there might be a nonlinear one!)

Range: [-1, 1]
```

Pearson zakłada, że zależność jest liniowa, a obie zmienne mają rozkład zbliżony do normalnego. Jest podatny na obserwacje odstające. Jeden ekstremalny punkt może przesunąć r z 0.1 na 0.9.

**Korelacja rangowa Spearmana** mierzy zależność monotoniczną:

```
1. Replace each value with its rank (1, 2, 3, ...)
2. Compute Pearson correlation on the ranks

Spearman catches any monotonic relationship, not just linear.
If y = x^3, Pearson gives r < 1 but Spearman gives rho = 1.
```

**Kiedy używać którego:**

```
Pearson:    Both variables are continuous and roughly normal.
            You care about the linear relationship specifically.
            No extreme outliers.

Spearman:   Ordinal data (rankings, ratings).
            Data is not normally distributed.
            You suspect a monotonic but not linear relationship.
            Outliers are present.
```

**Złota zasada:** korelacja nie implikuje przyczynowości. Sprzedaż lodów i liczba przypadków utonięć są skorelowane, ponieważ obie wzrastają latem. Dokładność Twojego modelu i liczba parametrów są skorelowane, ale dodawanie parametrów nie poprawia automatycznie dokładności (zobacz: przeuczenie/overfitting).

### Macierz kowariancji

Kowariancja między dwiema zmiennymi mierzy, jak zmieniają się razem:

```
Cov(X, Y) = (1/n) * sum((x_i - x_bar)(y_i - y_bar))

Cov(X, Y) > 0:  X and Y tend to increase together
Cov(X, Y) < 0:  when X increases, Y tends to decrease
Cov(X, Y) = 0:  no linear co-movement
```

Dla d cech, macierz kowariancji C jest macierzą d x d, gdzie C[i][j] = Cov(feature_i, feature_j). Elementy na przekątnej C[i][i] to wariancje każdej cechy.

```
C = | Var(x1)      Cov(x1,x2)  Cov(x1,x3) |
    | Cov(x2,x1)  Var(x2)      Cov(x2,x3) |
    | Cov(x3,x1)  Cov(x3,x2)  Var(x3)     |

Properties:
  - Symmetric: C[i][j] = C[j][i]
  - Positive semi-definite: all eigenvalues >= 0
  - Diagonal = variances
  - Off-diagonal = covariances
```

**Związek z PCA.** PCA przeprowadza dekompozycję macierzy kowariancji na wektory własne. Wektory własne (eigenvectors) to główne składowe (directions of maximum variance, kierunki maksymalnej wariancji). Wartości własne (eigenvalues) mówią, jaką część wariancji obejmuje każda składowa. To jest dokładnie to, co omawiała Lekcja 10, ale teraz widzisz, dlaczego macierz kowariancji jest właściwym obiektem do dekomponowania: koduje wszystkie parami liniowe zależności w Twoich danych.

**Związek z korelacją.** Macierz korelacji to macierz kowariancji zmiennych zestandaryzowanych (każda podzielona przez swoje odchylenie standardowe). Korelacja normalizuje kowariancję, tak aby wszystkie wartości znalazły się w przedziale [-1, 1].

### Testowanie hipotez

Testowanie hipotez to ramy do podejmowania decyzji w warunkach niepewności. Zaczynasz od stwierdzenia, zbierasz dane i sprawdzasz, czy dane są zgodne z tym stwierdzeniem.

**Konfiguracja:**

```
Null hypothesis (H0):        the default assumption, usually "no effect"
Alternative hypothesis (H1): what you are trying to show

Example:
  H0: Model A and Model B have the same accuracy
  H1: Model B has higher accuracy than Model A
```

**Wartość p (p-value)** to prawdopodobieństwo zaobserwowania danych co najmniej tak ekstremalnych jak te, które otrzymaliśmy, zakładając, że H0 jest prawdziwe. NIE jest to prawdopodobieństwo, że H0 jest prawdziwe. To najczęstsze nieporozumienie w statystyce.

```
p-value = P(data this extreme | H0 is true)

If p-value < alpha (typically 0.05):
    Reject H0. The result is "statistically significant."
If p-value >= alpha:
    Fail to reject H0. You do not have enough evidence.
    This does NOT mean H0 is true.
```

**Przedziały ufności** dają zakres wiarygodnych wartości dla parametru:

```
95% confidence interval for the mean:
    x_bar +/- z * (s / sqrt(n))

where z = 1.96 for 95% confidence

Interpretation: if you repeated this experiment many times, 95% of the
computed intervals would contain the true mean. It does NOT mean there
is a 95% probability the true mean is in this specific interval.
```

Szerokość przedziału ufności mówi o precyzji. Szerokie przedziały oznaczają wysoką niepewność. Wąskie przedziały oznaczają, że Twój estymator jest precyzyjny (ale niekoniecznie dokładny, jeśli dane są obciążone).

### Test t

Test t porównuje średnie. Istnieje kilka jego odmian.

**Jednopróbkowy test t (one-sample t-test):** czy średnia populacji różni się od hipotetycznej wartości?

```
t = (x_bar - mu_0) / (s / sqrt(n))

degrees of freedom = n - 1
```

**Dwuprobkowy test t (independent):** czy średnie dwóch grup się różnią?

```
t = (x_bar_1 - x_bar_2) / sqrt(s1^2/n1 + s2^2/n2)

This is Welch's t-test, which does not assume equal variances.
Always use Welch's unless you have a specific reason for equal variances.
```

**Test t dla par (paired t-test):** gdy pomiary tworzą pary (ten sam model oceniany na tych samych podziałach danych):

```
Compute d_i = x_i - y_i for each pair
Then run a one-sample t-test on the d_i values against mu_0 = 0
```

W ML test t dla par jest powszechny: uruchamiasz oba modele na tych samych 10 foldach walidacji krzyżowej i porównujesz ich wyniki parami.

### Test chi-kwadrat

Test chi-kwadrat sprawdza, czy obserwowane częstości zgadzają się z oczekiwanymi częstościami. Przydatny dla danych kategorialnych.

```
chi^2 = sum((observed - expected)^2 / expected)

Example: does a language model's output distribution match the
training distribution across categories?

Category    Observed   Expected
Positive       120        100
Negative        80        100
chi^2 = (120-100)^2/100 + (80-100)^2/100 = 4 + 4 = 8

With 1 degree of freedom, chi^2 = 8 gives p < 0.005.
The difference is significant.
```

### Testy A/B dla modeli ML

Testy A/B w ML nie są tym samym, co testy A/B na stronach internetowych. Porównywanie modeli ma specyficzne wyzwania:

```
1. Same test set:    Both models must be evaluated on identical data.
                     Different test sets make comparison meaningless.

2. Multiple metrics: Accuracy alone is not enough. You need precision,
                     recall, F1, latency, and fairness metrics.

3. Variance:         Use cross-validation or bootstrap to estimate
                     the variance of each metric, not just point estimates.

4. Data leakage:     If the test set was used during model selection,
                     your comparison is biased. Hold out a final test set.
```

**Procedura:**

```
1. Define your metric and significance level (alpha = 0.05)
2. Run both models on the same k-fold cross-validation splits
3. Collect paired scores: [(a1, b1), (a2, b2), ..., (ak, bk)]
4. Compute differences: d_i = b_i - a_i
5. Run a paired t-test on the differences
6. Check: is the mean difference significantly different from 0?
7. Compute a confidence interval for the mean difference
8. Compute effect size (Cohen's d) to judge practical significance
```

### Istotność statystyczna vs istotność praktyczna

Wynik może być statystycznie istotny, ale praktycznie bezsensowny. Przy wystarczająco dużej liczbie danych nawet trywialna różnica staje się istotna statystycznie.

```
Example:
  Model A accuracy: 0.9234
  Model B accuracy: 0.9237
  n = 1,000,000 test samples
  p-value = 0.001

Statistically significant? Yes.
Practically significant? A 0.03% improvement is not worth the
engineering cost of deploying a new model.
```

**Wielkość efektu (effect size)** kwantyfikuje rozmiar różnicy, niezależnie od wielkości próbki:

```
Cohen's d = (mean_1 - mean_2) / pooled_std

d = 0.2:  small effect
d = 0.5:  medium effect
d = 0.8:  large effect
```

Zawsze raportuj zarówno wartość p, jak i wielkość efektu. Wartość p mówi, czy różnica jest realna. Wielkość efektu mówi, czy ma to znaczenie.

### Problem wielokrotnych porównań

Gdy testujesz wiele hipotez, niektóre będą "istotne" przez przypadek. Jeśli testujesz 20 rzeczy przy alpha = 0.05, oczekujesz 1 wyniku fałszywie pozytywnego, nawet gdy nic nie jest prawdziwe.

```
P(at least one false positive) = 1 - (1 - alpha)^m

m = 20 tests, alpha = 0.05:
P(false positive) = 1 - 0.95^20 = 0.64

You have a 64% chance of at least one false positive.
```

**Korekcja Bonferroniego:** dziel alpha przez liczbę testów.

```
Adjusted alpha = alpha / m = 0.05 / 20 = 0.0025

Only reject H0 if p-value < 0.0025.
Conservative but simple. Works when tests are independent.
```

W ML ma to znaczenie, gdy porównujesz model na wielu metrykach, testujesz wiele konfiguracji hiperparametrów albo ewaluujesz na wielu zbiorach danych.

### Metody bootstrapowe

Bootstrapping estymuje rozkład próbkowy (sampling distribution) statystyki poprzez resampling danych ze zwracaniem. Nie wymaga żadnych założeń o rozkładzie bazowym.

**Algorytm:**

```
1. You have n data points
2. Draw n samples WITH replacement (some points appear multiple times,
   some not at all)
3. Compute your statistic on this bootstrap sample
4. Repeat B times (typically B = 1000 to 10000)
5. The distribution of bootstrap statistics approximates the
   sampling distribution
```

**Przedział ufności bootstrapowy (metoda percentylowa):**

```
Sort the B bootstrap statistics
95% CI = [2.5th percentile, 97.5th percentile]
```

**Dlaczego bootstrap jest ważny w ML:**

```
- Test set accuracy is a point estimate. Bootstrap gives you
  confidence intervals.
- You cannot assume metric distributions are normal (especially
  for AUC, F1, precision at k).
- Bootstrap works for ANY statistic: median, ratio of two means,
  difference in AUC between two models.
- No closed-form formula needed.
```

**Bootstrap do porównania modeli:**

```
1. You have predictions from Model A and Model B on the same test set
2. For each bootstrap iteration:
   a. Resample test indices with replacement
   b. Compute metric_A and metric_B on the resampled set
   c. Store diff = metric_B - metric_A
3. 95% CI for the difference:
   [2.5th percentile of diffs, 97.5th percentile of diffs]
4. If the CI does not contain 0, the difference is significant
```

Jest to bardziej odporne niż test t dla par, ponieważ nie wymaga żadnych założeń o rozkładzie.

### Testy parametryczne vs nieparametryczne

**Testy parametryczne** zakładają konkretny rozkład (zwykle normalny):

```
t-test:         assumes normally distributed data (or large n by CLT)
ANOVA:          assumes normality and equal variances
Pearson r:      assumes bivariate normality
```

**Testy nieparametryczne** nie zakładają żadnego rozkładu:

```
Mann-Whitney U:     compares two groups (replaces independent t-test)
Wilcoxon signed-rank: compares paired data (replaces paired t-test)
Spearman rho:       correlation on ranks (replaces Pearson)
Kruskal-Wallis:     compares multiple groups (replaces ANOVA)
```

**Kiedy używać testów nieparametrycznych:**

```
- Small sample size (n < 30) and data is clearly non-normal
- Ordinal data (ratings, rankings)
- Heavy outliers you cannot remove
- Skewed distributions
```

**Kiedy używać testów parametrycznych:**

```
- Large sample size (CLT makes the test statistic approximately normal)
- Data is roughly symmetric without extreme outliers
- More statistical power (better at detecting real differences)
```

W eksperymentach ML zwykle mamy małe n (5 lub 10 foldów walidacji krzyżowej), dlatego testy nieparametryczne, takie jak Wilcoxon signed-rank, są często bardziej odpowiednie niż testy t.

### Centralne twierdzenie graniczne: praktyczne implikacje

Centralne twierdzenie graniczne (CLT) mówi, że rozkład średnich z próbek zbliża się do rozkładu normalnego w miarę wzrostu n, niezależnie od rozkładu bazowej populacji.

```
If X_1, X_2, ..., X_n are iid with mean mu and variance sigma^2:

    X_bar ~ Normal(mu, sigma^2 / n)    as n -> infinity

Works for n >= 30 in most cases.
For highly skewed distributions, you might need n >= 100.
```

**Dlaczego to ma znaczenie w ML:**

```
1. Justifies confidence intervals and t-tests on aggregated metrics
2. Explains why averaging over cross-validation folds gives stable
   estimates even when individual folds vary wildly
3. Mini-batch gradient descent works because the average gradient
   over a batch approximates the true gradient (CLT in action)
4. Ensemble methods: averaging predictions from many models gives
   more stable output than any single model
```

**Czego CLT NIE robi:**

```
- Does NOT make your data normal. It makes the MEAN of samples normal.
- Does NOT work for heavy-tailed distributions with infinite variance
  (Cauchy distribution).
- Does NOT apply to dependent data (time series without correction).
```

### Częste błędy statystyczne w artykułach ML

1. **Testowanie na zbiorze treningowym.** Gwarantuje przeuczenie (overfitting). Zawsze wydzielaj dane, których model nigdy nie widzi podczas treningu.

2. **Brak przedziałów ufności.** Raportowanie jednej liczby dokładności bez niepewności sprawia, że wyniki są niemożliwe do odtworzenia i zweryfikowania.

3. **Ignorowanie wielokrotnych porównań.** Testowanie 50 konfiguracji i raportowanie najlepszej bez korekcji zawyża wskaźnik wyników fałszywie pozytywnych.

4. **Mylenie istotności statystycznej z praktyczną.** Wartość p równa 0.001 dla poprawy dokładności o 0.01% nie jest istotna.

5. **Używanie accuracy na danych niezbalansowanych.** 99% accuracy na zbiorze, gdzie 99% przykładów to klasa negatywna, oznacza, że model niczego się nie nauczył. Używaj precision, recall, F1 lub AUC.

6. **Wybiórcze raportowanie metryk (cherry-picking).** Raportowanie tylko metryki, na której Twój model wygrywa. Rzetelna ewaluacja raportuje wszystkie istotne metryki.

7. **Przeciek informacji między podziałem train/test.** Normalizacja przed podziałem albo używanie danych z przyszłości do przewidywania przeszłości.

8. **Małe zbiory testowe bez oszacowania wariancji.** Ewaluacja na 100 próbkach i twierdzenie o 2% poprawie to szum, nie sygnał.

9. **Zakładanie niezależności, gdy dane nie są niezależne.** Obrazy medyczne od tego samego pacjenta, wiele zdań z tego samego dokumentu. Obserwacje w ramach grupy są skorelowane.

10. **P-hacking.** Wypróbowywanie różnych testów, podzbiorów lub kryteriów wykluczenia, aż do uzyskania p < 0.05. Wynik jest artefaktem przeszukiwania.

## Co zbudujemy

Zaimplementujesz:

1. **Statystykę opisową od podstaw** (mean, median, mode, standard deviation, percentyle, IQR)
2. **Funkcje korelacji** (Pearson i Spearman, wraz z macierzą kowariancji)
3. **Testy hipotez** (jednoprobkowy test t, dwuprobkowy test t, test chi-kwadrat)
4. **Przedziały ufności bootstrapowe** (dla dowolnej statystyki, bez żadnych założeń)
5. **Symulator testu A/B** (generowanie danych, testowanie, sprawdzanie błędów typu I i typu II)
6. **Demo istotności statystycznej vs praktycznej** (pokazujące, że duże n sprawia, że wszystko staje się "istotne")

Wszystko od podstaw, używając jedynie `math` i `random`. Bez numpy, bez scipy.

## Kluczowe terminy

| Termin | Definicja |
|---|---|
| Mean (średnia) | Suma wartości podzielona przez ich liczbę. Podatna na obserwacje odstające. |
| Median (mediana) | Wartość środkowa posortowanych danych. Odporna na obserwacje odstające. |
| Standard deviation (odchylenie standardowe) | Pierwiastek kwadratowy z wariancji. Mierzy rozproszenie w jednostkach oryginalnych danych. |
| Percentile (percentyl) | Wartość, poniżej której znajduje się dany procent danych. |
| IQR | Rozstęp międzykwartylowy. Q3 minus Q1. Rozproszenie środkowych 50% danych. |
| Pearson correlation (korelacja Pearsona) | Mierzy liniową zależność między dwiema zmiennymi. Zakres [-1, 1]. |
| Spearman correlation (korelacja Spearmana) | Mierzy zależność monotoniczną na podstawie rang. |
| Covariance matrix (macierz kowariancji) | Macierz kowariancji par wszystkich cech. |
| Null hypothesis (hipoteza zerowa) | Domyślne założenie braku efektu lub braku różnicy. |
| p-value (wartość p) | Prawdopodobieństwo zaobserwowania danych co najmniej tak ekstremalnych, zakładając, że hipoteza zerowa jest prawdziwa. |
| Confidence interval (przedział ufności) | Zakres wiarygodnych wartości parametru przy danym poziomie ufności. |
| t-test (test t) | Testuje, czy średnie różnią się istotnie. Wykorzystuje rozkład t. |
| Chi-squared test (test chi-kwadrat) | Testuje, czy obserwowane częstości różnią się od oczekiwanych. |
| Effect size (wielkość efektu) | Rozmiar różnicy, niezależny od wielkości próbki. Cohen's d jest powszechną miarą. |
| Bonferroni correction (korekcja Bonferroniego) | Dzieli próg istotności przez liczbę testów, aby kontrolować liczbę wyników fałszywie pozytywnych. |
| Bootstrap | Resampling ze zwracaniem służący do estymacji rozkładów próbkowych. |
| Type I error (błąd typu I) | Wynik fałszywie pozytywny. Odrzucenie H0, gdy jest ono prawdziwe. |
| Type II error (błąd typu II) | Wynik fałszywie negatywny. Nieodrzucenie H0, gdy jest ono fałszywe. |
| Statistical power (moc statystyczna) | Prawdopodobieństwo prawidłowego odrzucenia fałszywego H0. Moc = 1 minus wskaźnik błędu typu II. |
| Central limit theorem (centralne twierdzenie graniczne) | Średnie z próbek zbiegają do rozkładu normalnego w miarę wzrostu wielkości próbki. |
| Parametric test (test parametryczny) | Zakłada konkretny rozkład danych (zwykle normalny). |
| Non-parametric test (test nieparametryczny) | Nie zakłada żadnego rozkładu. Działa na rangach lub znakach. |
