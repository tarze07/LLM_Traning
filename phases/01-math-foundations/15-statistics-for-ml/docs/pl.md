# Statystyki dotyczące uczenia maszynowego

> Dzięki statystykom wiesz, czy Twój model faktycznie działa, czy po prostu miał szczęście.

**Typ:** Kompilacja
**Język:** Python
**Wymagania wstępne:** Faza 1, lekcje 06 (Prawdopodobieństwo i rozkłady), 07 (Twierdzenie Bayesa)
**Czas:** ~120 minut

## Cele nauczania

- Obliczanie statystyk opisowych, korelacji Pearsona/Spearmana i macierzy kowariancji od podstaw
- Wykonaj testy hipotez (test t, chi-kwadrat) i poprawnie zinterpretuj wartości p oraz przedziały ufności
- Użyj ponownego próbkowania metodą bootstrap, aby skonstruować przedziały ufności dla dowolnej metryki bez założeń dystrybucyjnych
- Odróżnij znaczenie statystyczne od praktycznego za pomocą miar wielkości efektu

## Problem

Wytrenowałeś dwa modele. Model A uzyskuje wynik 0,87 w zestawie testowym. Model B uzyskuje wynik 0,89. Wdrażasz Model B. Trzy tygodnie później wskaźniki produkcyjne są gorsze niż wcześniej. Co się stało?

Model B w rzeczywistości nie przewyższał Modelu A. Różnica wynosząca 0,02 to hałas. Twój zestaw testowy był za mały lub wariancja była zbyt duża, lub jedno i drugie. Wysłałeś losowość przebraną za ulepszenie.

To się dzieje ciągle. Zmiany w tabeli liderów Kaggle. Dokumenty, których nie udało się odtworzyć. Testy A/B, które wyłonią zwycięzców na podstawie kilkuset próbek. Główna przyczyna jest zawsze ta sama: ktoś pominął statystyki.

Statystyka zapewnia narzędzia umożliwiające odróżnienie sygnału od szumu. Informuje Cię, kiedy różnica jest realna, jak pewny powinieneś być i ile danych potrzebujesz, aby móc zaufać wynikowi. Każdy potok ML, każde porównanie modelu, każdy eksperyment wymaga statystyk. Bez tego zgadujesz.

## Koncepcja

### Statystyki opisowe: podsumowanie danych

Zanim cokolwiek zamodelujesz, musisz wiedzieć, jak wyglądają Twoje dane. Statystyki opisowe kompresują zbiór danych do kilku liczb, które oddają jego kształt.

**Miary tendencji centralnej** odpowiadają „gdzie jest środek?”

```
Mean:   sum of all values / count
        mu = (1/n) * sum(x_i)

Median: middle value when sorted
        Robust to outliers. If you have [1, 2, 3, 4, 1000], the mean is 202
        but the median is 3.

Mode:   most frequent value
        Useful for categorical data. For continuous data, rarely informative.
```

Średnia to punkt równowagi. Mediana to połowa drogi. Kiedy się różnią, dystrybucja jest zniekształcona. Rozkłady dochodów mają średnią >> medianę (odchylenie w prawo od miliarderów). Rozkłady strat podczas uczenia często mają średnią << medianę (lewe skośne z łatwych próbek).

**Miary rozproszenia** odpowiadają „jak rozproszone są dane?”

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

**Percentyle** dzielą posortowane dane na 100 równych części. 25. percentyl (Q1) oznacza, że ​​25% wartości spada poniżej tego punktu. 50. percentyl to mediana. 75. percentyl to Q3.

```
For latency monitoring:
  P50 = median latency        (typical user experience)
  P95 = 95th percentile       (bad but not worst case)
  P99 = 99th percentile       (tail latency, often 10x the median)
```

W ML ważne są percentyle opóźnień wnioskowania, rozkłady ufności przewidywań i zrozumienie rozkładów błędów. Model z niskim średnim błędem, ale strasznym błędem P99 może być bezużyteczny w zastosowaniach krytycznych dla bezpieczeństwa.

**Statystyki dotyczące próby a populacji.** Obliczając wariancję z próby, należy podzielić przez (n-1) zamiast przez n. To jest poprawka Bessela. Kompensuje to fakt, że średnia próbki nie jest prawdziwą średnią populacji. Mając n w mianowniku, systematycznie nie doceniasz prawdziwej wariancji. W przypadku (n-1) oszacowanie jest bezstronne.

```
Population variance: sigma^2 = (1/N) * sum((x_i - mu)^2)
Sample variance:     s^2     = (1/(n-1)) * sum((x_i - x_bar)^2)
```

W praktyce: jeśli n jest duże (tysiące próbek), różnica jest pomijalna. Jeśli n jest małe (dziesiątki próbek), ma to znaczenie.

### Korelacja: jak zmienne poruszają się razem

Korelacja mierzy siłę i kierunek liniowej zależności między dwiema zmiennymi.

**Współczynnik korelacji Pearsona** mierzy powiązanie liniowe:

```
r = sum((x_i - x_bar)(y_i - y_bar)) / (n * s_x * s_y)

r = +1:  perfect positive linear relationship
r = -1:  perfect negative linear relationship
r =  0:  no linear relationship (but there might be a nonlinear one!)

Range: [-1, 1]
```

Pearson zakłada, że zależność jest liniowa i obie zmienne mają w przybliżeniu rozkład normalny. Jest wrażliwy na wartości odstające. Pojedynczy skrajny punkt może przeciągnąć r z 0,1 do 0,9.

**Korelacja rang Spearmana** mierzy powiązanie monotoniczne:

```
1. Replace each value with its rank (1, 2, 3, ...)
2. Compute Pearson correlation on the ranks

Spearman catches any monotonic relationship, not just linear.
If y = x^3, Pearson gives r < 1 but Spearman gives rho = 1.
```

**Kiedy używać każdego z nich:**

```
Pearson:    Both variables are continuous and roughly normal.
            You care about the linear relationship specifically.
            No extreme outliers.

Spearman:   Ordinal data (rankings, ratings).
            Data is not normally distributed.
            You suspect a monotonic but not linear relationship.
            Outliers are present.
```

**Złota zasada:** korelacja nie implikuje związku przyczynowego. Sprzedaż lodów i liczba zgonów utonięć są ze sobą powiązane, ponieważ w lecie oba zjawiska rosną. Dokładność modelu i liczba parametrów są ze sobą powiązane, ale dodanie parametrów nie poprawia automatycznie dokładności (patrz: nadmierne dopasowanie).

### Macierz kowariancji

Kowariancja między dwiema zmiennymi mierzy, jak różnią się one razem:

```
Cov(X, Y) = (1/n) * sum((x_i - x_bar)(y_i - y_bar))

Cov(X, Y) > 0:  X and Y tend to increase together
Cov(X, Y) < 0:  when X increases, Y tends to decrease
Cov(X, Y) = 0:  no linear co-movement
```

Dla cech d macierz kowariancji C jest macierzą d x d, gdzie C[i][j] = Cov(cecha_i, cecha_j). Ukośne wpisy C[i][i] to wariancje każdej cechy.

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

**Połączenie z PCA.** PCA eigendekomponowuje macierz kowariancji. Wektory własne są głównymi składnikami (kierunkami maksymalnej wariancji). Wartości własne mówią, ile wariancji wychwytuje każdy składnik. Dokładnie to omawialiśmy w lekcji 10, ale teraz widzisz, dlaczego macierz kowariancji najlepiej jest rozłożyć: koduje ona wszystkie liniowe relacje parami w danych.

**Powiązanie z korelacją.** Macierz korelacji to macierz kowariancji zmiennych standaryzowanych (każda podzielona przez jej odchylenie standardowe). Korelacja normalizuje kowariancję, więc wszystkie wartości mieszczą się w [-1, 1].

### Testowanie hipotez

Testowanie hipotez stanowi podstawę podejmowania decyzji w warunkach niepewności. Zaczynasz od roszczenia, zbierasz dane i ustalasz, czy są one zgodne z roszczeniem.

**Konfiguracja:**

```
Null hypothesis (H0):        the default assumption, usually "no effect"
Alternative hypothesis (H1): what you are trying to show

Example:
  H0: Model A and Model B have the same accuracy
  H1: Model B has higher accuracy than Model A
```

**Wartość p** to prawdopodobieństwo, że dane będą tak ekstremalne, jak te, które zaobserwowałeś, przy założeniu, że H0 jest prawdziwe. NIE jest to prawdopodobieństwo, że H0 jest prawdziwe. Jest to najczęstsze nieporozumienie w statystykach.

```
p-value = P(data this extreme | H0 is true)

If p-value < alpha (typically 0.05):
    Reject H0. The result is "statistically significant."
If p-value >= alpha:
    Fail to reject H0. You do not have enough evidence.
    This does NOT mean H0 is true.
```

**Przedziały ufności** dają zakres wiarygodnych wartości parametru:

```
95% confidence interval for the mean:
    x_bar +/- z * (s / sqrt(n))

where z = 1.96 for 95% confidence

Interpretation: if you repeated this experiment many times, 95% of the
computed intervals would contain the true mean. It does NOT mean there
is a 95% probability the true mean is in this specific interval.
```

Szerokość przedziału ufności mówi o precyzji. Szerokie przedziały oznaczają dużą niepewność. Wąskie przedziały oznaczają, że oszacowanie jest dokładne (ale niekoniecznie dokładne, jeśli dane są stronnicze).

### Test t

Test t porównuje średnie. Jest kilka smaków.

**Test t dla jednej próby:** czy średnia populacji różni się od wartości hipotetycznej?

```
t = (x_bar - mu_0) / (s / sqrt(n))

degrees of freedom = n - 1
```

**Test t dla dwóch prób (niezależny):** czy średnie w dwóch grupach są różne?

```
t = (x_bar_1 - x_bar_2) / sqrt(s1^2/n1 + s2^2/n2)

This is Welch's t-test, which does not assume equal variances.
Always use Welch's unless you have a specific reason for equal variances.
```

**Test t dla par:** gdy pomiary występują parami (ten sam model oceniany na tych samych podziałach danych):

```
Compute d_i = x_i - y_i for each pair
Then run a one-sample t-test on the d_i values against mu_0 = 0
```

W ML test t dla par jest powszechny: uruchamiasz oba modele w tych samych 10 przypadkach weryfikacji krzyżowej i porównujesz ich wyniki parami.

### Test chi-kwadrat

Test chi-kwadrat sprawdza, czy obserwowane częstotliwości odpowiadają częstotliwościom oczekiwanym. Przydatne w przypadku danych kategorycznych.

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

Testy A/B w ML to nie to samo, co internetowe testy A/B. Porównanie modeli wiąże się ze specyficznymi wyzwaniami:

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

### Znaczenie statystyczne a znaczenie praktyczne

Wynik może być statystycznie istotny, ale praktycznie bez znaczenia. Przy wystarczającej ilości danych nawet niewielka różnica staje się istotna statystycznie.

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

**Wielkość efektu** określa ilościowo, jak duża jest różnica, niezależnie od wielkości próbki:

```
Cohen's d = (mean_1 - mean_2) / pooled_std

d = 0.2:  small effect
d = 0.5:  medium effect
d = 0.8:  large effect
```

Zawsze podawaj zarówno wartość p, jak i wielkość efektu. Wartość p informuje, czy różnica jest rzeczywista. Rozmiar efektu powie Ci, czy ma to znaczenie.

### Problem z wielokrotnym porównaniem

Kiedy testujesz wiele hipotez, niektóre będą przez przypadek „istotne”. Jeśli przetestujesz 20 rzeczy przy alfa = 0,05, spodziewasz się 1 fałszywie pozytywnego wyniku, nawet jeśli nic nie jest prawdziwe.

```
P(at least one false positive) = 1 - (1 - alpha)^m

m = 20 tests, alpha = 0.05:
P(false positive) = 1 - 0.95^20 = 0.64

You have a 64% chance of at least one false positive.
```

**Korekta Bonferroniego:** podziel alfa przez liczbę testów.

```
Adjusted alpha = alpha / m = 0.05 / 20 = 0.0025

Only reject H0 if p-value < 0.0025.
Conservative but simple. Works when tests are independent.
```

W ML ma to znaczenie, gdy porównujesz model pod kątem wielu metryk, testujesz wiele konfiguracji hiperparametrów lub oceniasz na wielu zestawach danych.

### Metody ładowania początkowego

Metoda ładowania początkowego szacuje rozkład próbkowania statystyki poprzez ponowne próbkowanie danych z zastępowaniem. Nie są wymagane żadne założenia dotyczące rozkładu bazowego.

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

**Przedział ufności Bootstrap (metoda percentylowa):**

```
Sort the B bootstrap statistics
95% CI = [2.5th percentile, 97.5th percentile]
```

**Dlaczego bootstrap ma znaczenie dla ML:**

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

Jest to bardziej niezawodny niż test t dla par, ponieważ nie uwzględnia żadnych założeń dotyczących dystrybucji.

### Testy parametryczne i nieparametryczne

**Testy parametryczne** zakładają określony rozkład (zwykle normalny):

```
t-test:         assumes normally distributed data (or large n by CLT)
ANOVA:          assumes normality and equal variances
Pearson r:      assumes bivariate normality
```

**Testy nieparametryczne** nie przyjmują żadnych założeń dystrybucyjnych:

```
Mann-Whitney U:     compares two groups (replaces independent t-test)
Wilcoxon signed-rank: compares paired data (replaces paired t-test)
Spearman rho:       correlation on ranks (replaces Pearson)
Kruskal-Wallis:     compares multiple groups (replaces ANOVA)
```

**Kiedy stosować parametry nieparametryczne:**

```
- Small sample size (n < 30) and data is clearly non-normal
- Ordinal data (ratings, rankings)
- Heavy outliers you cannot remove
- Skewed distributions
```

**Kiedy używać parametrów parametrycznych:**

```
- Large sample size (CLT makes the test statistic approximately normal)
- Data is roughly symmetric without extreme outliers
- More statistical power (better at detecting real differences)
```

W eksperymentach ML zazwyczaj masz małe n (5 lub 10 krotności walidacji krzyżowej), więc testy nieparametryczne, takie jak ranga Wilcoxona ze znakiem, są często bardziej odpowiednie niż testy t.

### Centralne twierdzenie graniczne: implikacje praktyczne

CLT twierdzi, że rozkład średnich z próby zbliża się do rozkładu normalnego w miarę wzrostu n, niezależnie od podstawowego rozkładu populacji.

```
If X_1, X_2, ..., X_n are iid with mean mu and variance sigma^2:

    X_bar ~ Normal(mu, sigma^2 / n)    as n -> infinity

Works for n >= 30 in most cases.
For highly skewed distributions, you might need n >= 100.
```

**Dlaczego ma to znaczenie dla ML:**

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

### Typowe błędy statystyczne w dokumentach ML

1. **Testowanie na zbiorze uczącym.** Gwarantuje przeuczenie. Zawsze udostępniaj dane, których model nigdy nie zobaczy podczas uczenia.

2. **Brak przedziałów ufności.** Podanie pojedynczej liczby dokładności bez niepewności sprawia, że ​​wyniki są niepowtarzalne i niemożliwe do sprawdzenia.

3. **Ignorowanie wielokrotnych porównań.** Testowanie 50 konfiguracji i zgłaszanie najlepszej bez korekty zawyża odsetek wyników fałszywie dodatnich.

4. **Mylące znaczenie statystyczne i praktyczne.** Wartość p wynosząca 0,001 przy poprawie dokładności o 0,01% nie jest znacząca.

5. **Wykorzystywanie dokładności w przypadku niezrównoważonych danych.** Dokładność 99% w przypadku zbioru danych z klasą ujemną wynoszącą 99% oznacza, że ​​model niczego się nie nauczył. Użyj precyzji, przypomnienia, F1 lub AUC.

6. **Wybór wskaźników.** Raportowanie tylko tych wskaźników, w przypadku których Twój model wygrywa. Uczciwa ocena uwzględnia wszystkie istotne wskaźniki.

7. **Wyciek informacji pomiędzy podziałami pociągów/testów.** Normalizacja przed podziałem lub wykorzystanie przyszłych danych do przewidywania przeszłości.

8. **Małe zestawy testowe bez oszacowań wariancji.** Ocena na 100 próbkach i twierdzenie o 2% poprawie to szum, a nie sygnał.

9. **Założenie niezależności w przypadku, gdy dane nie są niezależne.** Obrazy medyczne tego samego pacjenta, wiele zdań z tego samego dokumentu. Obserwacje w obrębie grupy są ze sobą skorelowane.

10. **P-hakowanie.** Próbowanie różnych testów, podzbiorów lub kryteriów wykluczenia, aż uzyskasz p < 0,05. Rezultatem jest artefakt poszukiwań.

## Budowanie

Wdrożysz:

1. **Statystyka opisowa od podstaw** (średnia, mediana, tryb, odchylenie standardowe, percentyle, IQR)
2. **Funkcje korelacji** (Pearsona i Spearmana, z macierzą kowariancji)
3. **Testowanie hipotez** (test t dla jednej próby, test t dla dwóch prób, test chi-kwadrat)
4. **Przedziały ufności Bootstrap** (dla dowolnej statystyki, nie są potrzebne żadne założenia)
5. **Symulator testów A/B** (wygeneruj dane, przetestuj, sprawdź błędy I i II rodzaju)
6. **Demonstracja znaczenia statystycznego i praktycznego** (pokazująca, że duże n sprawia, że wszystko jest „znaczące”)

Wszystko od zera, używając wyłącznie `math` i `random`. Żadnego numpy, żadnego scipy.

## Kluczowe terminy

| Termin | Definicja |
|---|---|
| Znaczy | Suma wartości podzielona przez liczbę. Wrażliwy na wartości odstające. |
| Mediana | Wartość środkowa posortowanych danych. Odporny na wartości odstające. |
| Odchylenie standardowe | Pierwiastek kwadratowy z wariancji. Miary rozłożone w oryginalnych jednostkach. |
| Percentyl | Wartość, poniżej której spada dany procent danych. |
| IQR | Rozstęp międzykwartylowy. Q3 minus Q1. Rozrzut środkowych 50%. |
| Korelacja Pearsona | Mierzy liniowe powiązanie między dwiema zmiennymi. Zakres [-1, 1]. |
| Korelacja Spearmana | Mierzy monotoniczne powiązania za pomocą rang. |
| Macierz kowariancji | Macierz kowariancji parami pomiędzy wszystkimi cechami. |
| Hipoteza zerowa | Domyślne założenie braku efektu lub różnicy. |
| wartość p | Prawdopodobieństwo danych tego ekstremum przy założeniu, że hipoteza zerowa jest prawdziwa. |
| Przedział ufności | Zakres wiarygodnych wartości parametru przy danym poziomie ufności. |
| test t | Testuje, czy średnie różnią się znacząco. Wykorzystuje rozkład t. |
| Test chi-kwadrat | Testuje, czy zaobserwowane częstotliwości różnią się od oczekiwanych częstotliwości. |
| Rozmiar efektu | Wielkość różnicy niezależna od wielkości próbki. D Cohena jest powszechne. |
| Korekta Bonferroniego | Dzieli próg istotności przez liczbę testów w celu kontroli wyników fałszywie dodatnich. |
| Bootstrap | Ponowne próbkowanie z zastępowaniem w celu oszacowania rozkładów próbkowania. |
| Błąd typu I | Fałszywie dodatnie. Odrzucanie H0, gdy jest ono prawdziwe. |
| Błąd typu II | Fałszywie negatywny. Nieodrzucenie H0, gdy jest fałszywe. |
| Moc statystyczna | Prawdopodobieństwo prawidłowego odrzucenia fałszywego H0. Moc = 1 minus współczynnik błędów typu II. |
| Centralne twierdzenie graniczne | Średnie próbki zbiegają się do rozkładu normalnego w miarę wzrostu wielkości próby. |
| Test parametryczny | Zakłada określony rozkład danych (zwykle normalny). |
| Test nieparametryczny | Nie przyjmuje żadnych założeń dotyczących dystrybucji. Działa na szeregi lub znaki. |