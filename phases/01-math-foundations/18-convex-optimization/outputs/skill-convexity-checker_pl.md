---

name: skill-convexity-checker
description: Określ, czy problem optymalizacyjny jest wypukły i wybierz odpowiednie rozwiązanie
version: 1.0.0
phase: 1
lesson: 18
tags: [optimization, convexity, solvers]

---

# Kontroler wypukłości

Jak sprawdzić, czy problem optymalizacji jest wypukły i co zrobić z odpowiedzią.

## Lista kontrolna decyzji

1. Czy funkcja celu jest wypukła? (Sprawdź dodatnią półokreśloność Hesja lub użyj reguł kompozycji.)
2. Czy wszystkie ograniczenia nierówności mają postać g_i(x) <= 0 where each g_i is convex?
3. Are all equality constraints affine (linear)?
4. If all three are yes, the problem is convex. Use a convex solver with convergence guarantees.
5. If any are no, the problem is non-convex. Use SGD/Adam and accept local optima.

## How to test convexity of a function

| Test | Applies to | Method |
|---|---|---|
| Second derivative >= 0 | Funkcje skalarne f(x) | Oblicz f''(x). Jeśli f''(x) >= 0 dla wszystkich x, wypukłe. |
| Hesjan jest PSD | Funkcje wielowymiarowe f(x) | Oblicz H(x). Jeśli wszystkie wartości własne >= 0 wszędzie, wypukłe. |
| Próba definicji | Dowolna funkcja | Sprawdź f(tx + (1-t)y) <= t*f(x) + (1-t)*f(y) for sampled x, y, t. |
| Composition rules | Composed functions | See composition table below. |
| Restriction to a line | Multivariate f | f is convex iff g(t) = f(x + tv) is convex in t for all x, v. |

## Composition rules (preserving convexity)

| Operation | Result |
|---|---|
| f + g (both convex) | Convex |
| c * f (c > 0, f wypukły) | Wypukły |
| max(f, g) (obie wypukłe) | Wypukły |
| f(Ax + b) gdzie f jest wypukłe | Wypukły |
| g(f(x)) gdzie g jest wypukłe, nie malejące, a f jest wypukłe | Wypukły |
| g(f(x)) gdzie g jest wypukłe, nierosnące, a f jest wklęsłe | Wypukły |
| suma funkcji wypukłych | Wypukły |
| supremum punktowe funkcji wypukłych | Wypukły |

## Typowe cele ML: wypukłe czy nie?

| Cel | Wypukły? | Powód |
|---|---|---|
| MSE: (1/n) suma(y - Xw)^2 | Tak | Kwadratowy w w, Hessian = (2/n) X^T X to PSD |
| Strata logistyczna: suma(log(1 + exp(-y_i * w^T x_i))) | Tak | Suma funkcji wypukłych (rodzina log-sum-exp) |
| Strata zawiasu: suma(max(0, 1 - y_i * w^T x_i)) | Tak | Max funkcji wypukłych (liniowych) |
| Regularyzacja L2: lambda * \|\|w\|\|^2 | Tak | Kwadratowy, Heski = 2*lambda*I |
| Regularyzacja L1: lambda * \|\|w\|\|_1 | Tak | Suma wartości bezwzględnych (wypukła, ale nieróżniczkowalna) |
| Regresja grzbietu: MSE + L2 | Tak | Suma dwóch funkcji wypukłych |
| LASSO: MSE + L1 | Tak | Suma dwóch funkcji wypukłych |
| Siatka elastyczna: MSE + L1 + L2 | Tak | Suma funkcji wypukłych |
| SVM (pierwotny): zawias + L2 | Tak | Suma funkcji wypukłych |
| Entropia krzyżowa z softmax | Tak (w logach) | Log-sum-exp jest wypukły |
| Sieć neuronowa (wszelkie straty) | Nie | Aktywacje nieliniowe tworzą niewypukłą kompozycję |
| k-oznacza cel | Nie | Krok przypisania dyskretnego |
| Faktoryzacja macierzy: \|\|X - UV^T\|\|^2 | Nie | Dwuliniowy w U i V |
| Utrata GAN | Nie | Minimax, niewypukły w generatorze |
| Strata kontrastowa (InfoNCE) | Nie | Log stosunku wykładniczego z próbkami ujemnymi |

## Wybór Solvera na podstawie wypukłości

| Typ problemu | Rozwiązujący | Gwarancja konwergencji |
|---|---|---|
| Wypukły, gładki, swobodny | Zejście gradientowe | O(1/k) do minimum globalnego |
| Wypukły, gładki, swobodny | L-BFGS | Superliniowy do minimum globalnego |
| Wypukły, gładki, swobodny | Metoda Newtona | Kwadratowe w pobliżu minimum (jeśli Hesjan jest wykonalny) |
| Wypukły, gładki, ograniczony | Metoda punktu wewnętrznego | Czas wielomianowy |
| Wypukły, niegładki (L1) | Gradient proksymalny /ISTA | O(1/k) do minimum globalnego |
| Wypukły, niegładki (L1) | ADMM | Elastyczny, obsługuje ograniczenia |
| Wypukły, kwadratowy | Skoniugowany gradient | Dokładne w n krokach |
| Niewypukły, gładki | SGD / Adam | Zbiega się do minimum lokalnego |
| Niewypukły, gładki | SGD + uruchamia się ponownie | Lepsze minimum lokalne średnio |
| Niewypukły, gładki | Przeparametryzacja + SGD | Płaskie minima, dobre uogólnienie |

## Typowe błędy

- Zakładając, że problem jest wypukły, ponieważ funkcja straty jest wypukła. Strata musi być wypukła w optymalizowanych parametrach. Entropia krzyżowa jest wypukła w logitach, ale pełne mapowanie sieci neuronowej z danych wejściowych na logity nie jest wypukłe.
- Stosowanie metody Newtona w przypadku zagadnienia niewypukłego. Hesjan może mieć ujemne wartości własne, powodując, że Newton porusza się w kierunku punktów siodłowych lub maksimów zamiast minimów.
- Zapominając, że regularyzacja L1 sprawia, że ​​cel nie jest różniczkowalny przy zera. Standardowe zejście gradientowe nie działa dobrze. Stosuj metody z gradientem proksymalnym lub metody subgradientowe.
- Podniesienie liczby warunku do kwadratu poprzez utworzenie A^T A. Jeśli chcesz rozwiązać problem najmniejszych kwadratów, a A jest źle uwarunkowane, użyj QR lub SVD zamiast normalnych równań.
- Deklarowanie problemu jako niewypukłego bez sprawdzania. Wiele problemów uczenia maszynowego (modele liniowe, SVM, regresja logistyczna) jest wypukłych i wymagają silniejszych rozwiązań.

## Szybki test: czy mój problem jest wypukły?

```
1. Write out the objective: minimize f(w) subject to constraints
2. For each term in f(w):
   - Is it quadratic with PSD matrix? -> Convex
   - Is it a norm? -> Convex
   - Is it log-sum-exp? -> Convex
   - Does it involve w nonlinearly (sigmoid(w), w1*w2)? -> Likely non-convex
3. Are all constraints linear or convex inequalities?
4. If ALL terms are convex and constraints are convex/linear -> problem is convex
5. If ANY term is non-convex -> problem is non-convex
```