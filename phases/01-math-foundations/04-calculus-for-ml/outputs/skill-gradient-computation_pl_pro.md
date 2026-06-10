---

name: skill-gradient-computation
description: Oblicz gradienty typowych funkcji straty w uczeniu maszynowym i wybierz optymalne podejście do różniczkowania
version: 1.0.0
phase: 1
lesson: 4
tags: [calculus, gradients, backpropagation]

---

# Obliczanie gradientu w uczeniu maszynowym

Praktyczny podręcznik do obliczania gradientów funkcji straty, funkcji aktywacji i operacji warstwowych stosowanych w sieciach neuronowych.

## Algorytm decyzyjny

1. Czy funkcja składa się z prostych operacji matematycznych (potęga, exp, log, funkcje trygonometryczne)? Skorzystaj z pochodnych analitycznych i reguły łańcuchowej.
2. Czy funkcja jest niestandardową operacją typu "czarna skrzynka" (black-box)? Użyj różniczkowania numerycznego (różnicy centralnej): `(f(x+h) - f(x-h)) / (2h)` z h = 1e-7.
3. Czy funkcja jest zbudowana z operacji tensorowych we frameworku typu PyTorch/JAX? Zostaw to wbudowanym silnikom automatycznego różniczkowania (autograd). Ewentualnie zweryfikuj poprawność testem numerycznym (gradient checking).
4. Czy potrzebujesz wyliczyć gradient skalarnej wartości straty (loss) względem macierzy wag? Zastosuj regułę łańcuchową wstecz na grafie obliczeniowym, węzeł po węźle.
5. Czy napotkałeś operację nieróżniczkowalną (argmax, zaokrąglanie, próbkowanie)? Użyj aproksymatora z prostym szacowaniem przepływu (straight-through estimator) lub tzw. triku reparametryzacji (reparameterization trick).

## Kiedy stosować konkretne podejście

| Podejście | Kiedy używać | Koszt obliczeniowy |
|---|---|---|
| Analityczne (wzory na papierze) | Proste funkcje, do weryfikacji testów autogradu | Zerowy narzut w czasie wykonania (runtime) |
| Numeryczne (różnice skończone) | Debugowanie, sprawdzanie poprawności (gradient checking), operacje "czarnej skrzynki" | 2n przepływów w przód (forward passes) dla n parametrów |
| Automatyczne różniczkowanie (Autodiff) | Dowolny zróżniczkowany graf obliczeniowy (podejście domyślne) | Jeden przepływ wstecz (backward pass) |
| Symboliczne (SymPy, Mathematica) | Wyprowadzanie ścisłych, zamkniętych wzorów do publikacji naukowych | Koszt ponoszony tylko w czasie analizy / kompilacji |

## Ściągawka: Popularne pochodne

| Funkcja | Wzór f(x) | Pochodna f'(x) | Kontekst w ML |
|---|---|---|---|
| Błąd średniokwadratowy (MSE) | (1/n) suma(y_hat - y)^2 | (2/n)(y_hat - y) | Modele regresji |
| Entropia krzyżowa binarna (BCE) | -(y log(p) + (1-y) log(1-p)) | p - y (jeśli obliczona po użyciu funkcji sigmoidalnej) | Klasyfikacja binarna |
| Entropia krzyżowa wieloklasowa (CE) | -log(p_true_class) | p - one_hot(y) (jeśli obliczona po użyciu funkcji softmax) | Klasyfikacja wieloklasowa |
| Sigmoid (Sigmoida) | 1 / (1 + e^(-x)) | sigma(x) * (1 - sigma(x)) | Bramki filtrujące (LSTM/GRU), prawdopodobieństwa binarne |
| Tanh (Tangens hiperboliczny) | (e^x - e^(-x)) / (e^x + e^(-x)) | 1 - tanh(x)^2 | Funkcje aktywacji w warstwach ukrytych (rzadziej stosowane w nowszych modelach) |
| ReLU | max(0, x) | 1 jeśli x > 0, w przeciwnym razie 0 | Domyślna funkcja aktywacji w warstwach ukrytych |
| Leaky ReLU | max(0.01x, x) | 1 jeśli x > 0, w przeciwnym razie 0.01 | Zapobieganie problemowi "martwych neuronów" |
| GELU | x * Phi(x) | Phi(x) + x * phi(x) | Szeroko stosowana w modelach opartych na architekturze Transformer |
| Softmax_i | e^(x_i) / suma(e^(x_j)) | s_i(1 - s_i) dla i=j, -s_i*s_j dla i!=j | Warstwa wyjściowa (uwaga: tworzy to macierz Jakobiego, a nie zwykły wektor!) |
| Log-softmax | x_i - log(suma(e^(x_j))) | 1 - softmax(x_i) dla i-tej współrzędnej | Stabilna numerycznie baza dla wyliczenia entropii krzyżowej |
| Warstwa liniowa (Dense) | y = Wx + b | dL/dW = dL/dy * x^T, dL/db = dL/dy | Wyprowadzenie aktualizacji wag dla każdej standardowej warstwy |
| Regularyzacja L2 (Ridge) | lambda * suma(w^2) | 2 * lambda * w | Wygaszanie wag modelu (Weight decay) |
| Regularyzacja L1 (Lasso) | lambda * suma(\|w\|) | lambda * sign(w) (funkcja znaku) | Wymuszanie rzadkości (Sparsity) - redukowanie wag precyzyjnie do zera |

## Typowe błędy i pułapki (Common pitfalls)

- Pominięcie współczynnika skali 1/n przy uśrednianiu po całej paczce danych (batch) podczas wyliczania strat z użyciem MSE czy entropii krzyżowej. Gradient zależy liniowo od wielkości tzw. partii roboczej.
- Wyliczanie gradientu po funkcji Softmax, jakby była jednym wektorem. W praktyce jest to cała macierz Jakobiego. Gdy złączymy entropię krzyżową z log-softmax, ta kłopotliwa kalkulacja macierzowa na szczęście elegancko i wydajnie upraszcza się do `(p - y)`.
- Zastosowanie mnożeń reguły łańcuchowej (chain rule) w odwrotnej / wadliwej kolejności. Prawidłowy kierunek podążania: pracuj od tyłu, zaczynając wyliczenia od funkcji straty w przód: `dL/dW = dL/dy * dy/dW`.
- Definiowanie testowego progu "h" jako zbyt dużej wartości (np. h = 0.1) albo za małej mikrowartości (np. h = 1e-15) wywołującej lawinę błędów numerycznych we floatach podczas różniczkowania numerycznego. Trzymaj się stabilnego rzędu `h = 1e-7` przy typie float64.
- Zignorowanie faktu, że dla popularnej funkcji aktywacji ReLU, w punkcie dokładnie odpowiadającym x = 0 gradient nie posiada prawnego/matematycznego bytu i zdefiniowania. W czystej praktyce deweloperskiej narzuca się tam po prostu zwrot arbitralny na twarde `0` lub `0.5`.

## Procedura weryfikacji (Gradient Checking Recipe)

```
Dla każdego pojedynczego parametru w:
  numeric_grad = (loss(w + h) - loss(w - h)) / (2h)
  auto_grad = wartość wyliczona przez przepływ backpropagation (backward pass)
  błąd_względny (relative_error) = |numeric - auto| / max(|numeric|, |auto|, 1e-8)
  upewnij_się_że(assert) błąd_względny < 1e-5
```

Względny błąd powyżej `1e-3` najprawdopodobniej oznacza gruby błąd logiczny w wyprowadzeniu analitycznym. Przy wynikach pomiędzy `1e-5` a `1e-3` zbadaj dokładnie stabilność zmiennoprzecinkową użytych danych.
