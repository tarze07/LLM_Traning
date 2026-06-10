---

name: skill-statistical-testing
description: Wybierz odpowiedni test statystyczny do porównywania modeli ML i oceny eksperymentów
version: 1.0.0
phase: 1
lesson: 15
tags: [statistics, hypothesis-testing, model-comparison]

---

# Testowanie statystyczne dla ML

Jak wybrać odpowiedni test podczas porównywania modeli, przeprowadzania eksperymentów A/B lub walidacji wyników.

## Lista kontrolna decyzji

1. Co porównujesz? Środki, proporcje, rozkłady czy korelacje?
2. Ile grup? Jedna próbka vs odniesienie, dwie grupy czy wiele grup?
3. Czy obserwacje są sparowane (ten sam zbiór testowy, te same fałdy) czy niezależne?
4. Czy dane mają rozkład normalny? Jeżeli n < 30 and not clearly normal, use non-parametric.
5. Is the data continuous, ordinal, or categorical?
6. How many tests are you running? Apply correction if more than one.

## Decision tree

PHCB0

## When to use each test

| Test | Data type | Assumptions | ML use case |
|---|---|---|---|
| Paired t-test | Continuous, paired | Normal differences | Compare 2 models on same k-fold splits |
| Wilcoxon signed-rank | Continuous/ordinal, paired | None (non-parametric) | Compare 2 models, small k (5-10 folds) |
| Welch's t-test | Continuous, independent | Roughly normal | Compare model on two separate datasets |
| Mann-Whitney U | Continuous/ordinal, independent | None | Compare latency distributions |
| ANOVA | Continuous, 3+ groups | Normal, equal variance | Compare multiple model architectures |
| Kruskal-Wallis | Continuous/ordinal, 3+ groups | None | Compare multiple models, non-normal metrics |
| Chi-squared | Categorical counts | Expected count >= 5 | Porównaj rozkłady klas, macierze zamieszania |
| Dokładny Fisher | Liczby kategoryczne | Małe próbki | Porównanie rzadkich wydarzeń |
| Próba KS | Ciągłe | Brak | Sprawdź, czy przewidywania są zgodne z oczekiwanym rozkładem |
| Bootstrap CI | Dowolna statystyka | Brak | Przedział ufności dla AUC, F1, dowolnej metryki |
| Próba McNemara | Sparowany plik binarny | Brak | Porównaj dwa klasyfikatory na tym samym zestawie testowym |

## Przepis na porównanie modeli

1. Przed rozpoczęciem eksperymentów zdefiniuj metrykę i poziom istotności (alfa = 0,05).
2. Przetestuj oba modele na tych samych k-krotnych podziałach walidacji krzyżowej (k = 5 lub 10).
3. Zbierz sparowane wyniki: (a_1, b_1), (a_2, b_2), ..., (a_k, b_k).
4. Oblicz różnice: d_i = b_i - a_i.
5. Przeprowadź test w parach (Wilcoxon dla k <= 10, paired t-test for k > 10 lub normalnych różnic).
6. Raport: wartość p, średnia różnica, 95% przedział ufności, wielkość efektu (d Cohena).
7. Jeśli p< alpha AND effect size is meaningful, the difference is real and worth acting on.

## Common mistakes

- Using an independent test when data is paired. If both models were evaluated on the same test folds, you must use a paired test. Independent tests throw away the pairing and lose statistical power.
- Reporting p < 0.05 without effect size. A statistically significant 0.1% accuracy improvement is not worth deploying. Always compute Cohen's d or the raw mean difference.
- Comparing models across different test sets. The test set MUST be identical for both models. Different test sets make comparison meaningless.
- Running 20 comparisons and reporting the best one without Bonferroni correction. With 20 tests at alpha = 0.05, you expect 1 false positive by chance.
- Using accuracy on imbalanced data. On a 99% majority class, a trivial classifier achieves 99%. Use F1, precision-recall AUC, or Matthews correlation coefficient.
- Treating cross-validation folds as independent samples. They share training data, which violates the independence assumption. The corrected resampled t-test accounts for this.

## Quick reference: effect size interpretation

| Cohen's d | Interpretation |
|---|---|
| 0.2 | Small effect |
| 0.5 | Medium effect |
| 0.8 | Large effect |
| > 1.0 | Bardzo duży efekt |

| Co zgłosić | Dlaczego |
|---|---|
| wartość p | Czy różnica jest realna? |
| Przedział ufności | Jak duża może być różnica? |
| Wielkość efektu (d Cohena) | Czy różnica jest znacząca? |
| Rozmiar próbki (n lub k fałd) | Czy możemy ufać wynikowi? |