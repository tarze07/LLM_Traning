---

name: skill-convexity-checker
description: Określ, czy problem optymalizacyjny jest wypukły i wybierz dla niego odpowiedni algorytm rozwiązujący (solver)
version: 1.0.0
phase: 1
lesson: 18
tags: [optimization, convexity, solvers]

---

# Weryfikator wypukłości

Jak sprawdzić, czy problem optymalizacji jest wypukły, i co zrobić z uzyskaną odpowiedzią.

## Lista kontrolna przy podejmowaniu decyzji

1. Czy funkcja celu jest wypukła? (Sprawdź, czy jej hesjan jest dodatnio półokreślony, lub użyj reguł składania funkcji).
2. Czy wszystkie ograniczenia w postaci nierówności mają postać g_i(x) <= 0, gdzie każde g_i jest wypukłe?
3. Czy wszystkie ograniczenia w postaci równości są afiniczne (liniowe)?
4. Jeśli odpowiedź na wszystkie trzy pytania brzmi "tak", problem jest wypukły. Użyj solvera dla optymalizacji wypukłej z gwarancjami zbieżności.
5. Jeśli na którekolwiek z pytań odpowiedź brzmi "nie", problem jest niewypukły. Użyj metod pierwszego rzędu (SGD/Adam) i zaakceptuj rozwiązania w minimum lokalnym.

## Jak testować wypukłość funkcji

| Test | Dotyczy | Metoda |
|---|---|---|
| Druga pochodna >= 0 | Funkcje skalarne f(x) | Oblicz f''(x). Jeśli f''(x) >= 0 dla każdego x, funkcja jest wypukła. |
| Hesjan jest PSD | Funkcje wielu zmiennych f(x) | Oblicz macierz Hessego H(x). Jeśli we wszystkich punktach wszystkie wartości własne są >= 0 (Positive Semi-Definite), funkcja jest wypukła. |
| Test z definicji | Dowolna funkcja | Sprawdź f(tx + (1-t)y) <= t*f(x) + (1-t)*f(y) dla losowo wybranych x, y oraz t z przedziału [0, 1]. |
| Reguły składania | Funkcje złożone | Zobacz tabelę składania funkcji poniżej. |
| Ograniczenie do prostej | Funkcje wielu zmiennych f | Funkcja f jest wypukła wtedy i tylko wtedy, gdy g(t) = f(x + tv) jest wypukła względem t dla dowolnego wektora x oraz kierunku v. |

## Reguły składania (zachowujące wypukłość)

| Operacja | Wynik |
|---|---|
| f + g (obie funkcje wypukłe) | Wypukła |
| c * f (c > 0, f wypukła) | Wypukła |
| max(f, g) (obie funkcje wypukłe) | Wypukła |
| f(Ax + b), gdzie f jest wypukła | Wypukła |
| g(f(x)), gdzie g jest wypukła i niemalejąca, a f jest wypukła | Wypukła |
| g(f(x)), gdzie g jest wypukła i nierosnąca, a f jest wklęsła | Wypukła |
| Suma wielu funkcji wypukłych | Wypukła |
| Supremum (maksimum punktowe) dowolnej rodziny funkcji wypukłych | Wypukła |

## Typowe cele optymalizacji w ML: wypukłe czy nie?

| Funkcja Celu (Loss) | Wypukła? | Powód |
|---|---|---|
| Błąd średniokwadratowy (MSE): (1/n) suma(y - Xw)^2 | Tak | Jest funkcją kwadratową względem w; jej hesjan to (2/n) X^T X, który jest macierzą PSD. |
| Strata logistyczna (Log loss): suma(log(1 + exp(-y_i * w^T x_i))) | Tak | Funkcja z rodziny log-sum-exp, składająca się z sumy funkcji wypukłych. |
| Hinge loss (strata zawiasowa): suma(max(0, 1 - y_i * w^T x_i)) | Tak | Maksimum z wypukłych funkcji liniowych. |
| Regularyzacja L2: lambda * \|\|w\|\|^2 | Tak | Kwadratowa, a jej hesjan to 2*lambda*I (PSD). |
| Regularyzacja L1: lambda * \|\|w\|\|_1 | Tak | Suma wartości bezwzględnych (wypukła, chociaż nieróżniczkowalna w zerze). |
| Regresja grzbietowa (Ridge): MSE + L2 | Tak | Suma dwóch funkcji wypukłych. |
| LASSO: MSE + L1 | Tak | Suma dwóch funkcji wypukłych. |
| Elastic Net: MSE + L1 + L2 | Tak | Suma funkcji wypukłych. |
| SVM (problem prymalny): Hinge loss + L2 | Tak | Suma funkcji wypukłych. |
| Entropia krzyżowa (Cross-entropy) z Softmax | Tak | Funkcja log-sum-exp jest wypukła ze względu na argumenty (logity). |
| Sieć neuronowa (niezależnie od funkcji straty) | Nie | Nieliniowe funkcje aktywacji tworzą złożoną, niewypukłą powierzchnię straty. |
| K-średnie (K-means) | Nie | Zawiera dyskretny krok przypisywania do klastrów. |
| Faktoryzacja macierzy: \|\|X - UV^T\|\|^2 | Nie | Funkcja jest dwuliniowa w relacji do U i V (niewypukła połączona kompozycja). |
| Strata w sieciach GAN | Nie | Jest to problem minimax, wprost niewypukły względem generatora. |
| Strata kontrastowa (InfoNCE) | Nie | Obejmuje logarytm ze stosunku funkcji wykładniczych zawierających negatywne próbki. |

## Wybór algorytmu rozwiązującego (solvera) na podstawie wypukłości

| Charakterystyka problemu | Rekomendowany Algorytm | Gwarancja Zbieżności |
|---|---|---|
| Wypukły, gładki, bez ograniczeń | Spadek gradientu (Gradient Descent) | W tempie O(1/k) do minimum globalnego. |
| Wypukły, gładki, bez ograniczeń | L-BFGS | Zbieżność superliniowa do minimum globalnego. |
| Wypukły, gładki, bez ograniczeń | Metoda Newtona | Zbieżność kwadratowa w okolicy minimum (jeśli hesjan da się wyliczyć i odwrócić). |
| Wypukły, gładki, z ograniczeniami | Metoda punktu wewnętrznego (Interior-point) | Czas wielomianowy. |
| Wypukły, niegładki (np. L1) | Spadek proksymalny / ISTA (Proximal gradient) | O(1/k) do minimum globalnego. |
| Wypukły, niegładki (np. L1) | ADMM | Bardzo elastyczny, doskonale obsługuje ograniczenia i rozproszone środowiska. |
| Wypukły, w pełni kwadratowy | Metoda gradientów sprzężonych (Conjugate Gradient) | Dokładne rozwiązanie w maksymalnie n krokach. |
| Niewypukły, gładki | SGD / Adam | Zbiega się do minimum lokalnego lub punktu krytycznego. |
| Niewypukły, gładki | SGD z restartami (np. cosine annealing) | Szansa na znalezienie średnio lepszego minimum lokalnego. |
| Niewypukły, gładki | Nadmierna parametryzacja (Overparameterization) + SGD | Prowadzi do "płaskich" minimów zapewniających dobrą generalizację. |

## Typowe błędy i pułapki

- Zakładanie, że problem optymalizacji jest wypukły tylko dlatego, że sama funkcja straty jest wypukła. Strata musi być wypukła *względem optymalizowanych parametrów*. Entropia krzyżowa (cross-entropy) jest wypukła względem logitów, ale całościowe mapowanie od danych wejściowych do logitów w głębokiej sieci neuronowej nie jest wypukłe względem jej wag.
- Stosowanie metody Newtona dla problemu niewypukłego. Hesjan może mieć w nim wartości własne mniejsze od zera, przez co metoda Newtona pchnie model w kierunku punktów siodłowych (lub wręcz maksimów) zamiast w stronę minimum.
- Zapominanie, że regularyzacja L1 sprawia, iż funkcja nie jest różniczkowalna w zerze. Tradycyjny spadek gradientu radzi sobie tu słabo. Zawsze stosuj wtedy algorytmy używające subgradientów lub spadek proksymalny.
- Potęgowanie wskaźnika uwarunkowania macierzy (condition number) poprzez ręczne liczenie A^T A. Jeśli próbujesz rozwiązać problem najmniejszych kwadratów, a macierz A jest źle uwarunkowana, rozwiązuj go poprzez rozkład QR lub SVD zamiast równań normalnych.
- Stwierdzanie, że problem na pewno jest niewypukły, bez weryfikacji. Wiele klasycznych problemów w ML (modele liniowe, SVM, regresja logistyczna) jest w pełni wypukłych, przez co warto w ich przypadku stosować mocniejsze algorytmy optymalizacji i silne gwarancje.

## Szybki test: Czy mój problem jest wypukły?

```
1. Rozpisz funkcję celu: minimalizuj f(w) pod zadanymi warunkami (ograniczeniami).
2. Sprawdź po kolei każdy składnik f(w):
   - Czy jest funkcją kwadratową z dodatnio półokreśloną (PSD) macierzą? -> Wypukły
   - Czy jest normą (np. L1, L2)? -> Wypukły
   - Czy jest to operacja log-sum-exp? -> Wypukły
   - Czy zawiera w sposób nieliniowy zmienną w (np. sigmoid(w), w1*w2)? -> Niemal na pewno niewypukły
3. Czy wszystkie ograniczenia są liniowe lub opisane nierównościami wypukłymi?
4. Jeśli WSZYSTKIE składniki celu są wypukłe, a ograniczenia wypukłe/liniowe -> cały problem JEST WYPUKŁY.
5. Jeśli CHOĆ JEDEN składnik jest niewypukły -> problem jest NIEWYPUKŁY.
```
