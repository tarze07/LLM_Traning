---

name: skill-gradient-computation
description: Oblicz gradienty typowych funkcji straty ML i wybierz odpowiednie podejście pochodne
version: 1.0.0
phase: 1
lesson: 4
tags: [calculus, gradients, backpropagation]

---

# Obliczanie gradientu dla ML

Praktyczny podręcznik do obliczania gradientów funkcji strat, funkcji aktywacji i operacji warstwowych stosowanych w sieciach neuronowych.

## Lista kontrolna decyzji

1. Czy funkcja składa się z prostych prymitywów (potęga, exp, log, trig)? Skorzystaj z pochodnych analitycznych i reguły łańcuchowej.
2. Czy funkcja jest operacją niestandardową czy operacją czarnej skrzynki? Użyj różniczkowania numerycznego: `(f(x+h) - f(x-h)) / (2h)` z h = 1e-7.
3. Czy funkcja jest zbudowana z operacji tensorowych w PyTorch/JAX? Niech autograd się tym zajmie. Sprawdź za pomocą kontroli numerycznej.
4. Czy potrzebujesz gradientu straty skalarnej w.r.t. macierz wag? Zastosuj regułę łańcucha poprzez wykres obliczeniowy, po jednym węźle na raz.
5. Czy istnieje operacja nieróżniczkowalna (argmax, zaokrąglanie, próbkowanie)? Użyj prostego estymatora lub sztuczki reparametryzacji.

## Kiedy zastosować każde podejście

| Podejście | Kiedy używać | Koszt |
|---|---|---|
| Analityczne (wyprowadzone ręcznie) | Proste funkcje sprawdzające wyjście autogradu | Bezpłatnie w czasie wykonywania |
| Numeryczne (różnice skończone) | Debugowanie, sprawdzanie gradientu, funkcje czarnej skrzynki | 2n przejść w przód dla n parametrów |
| Automatyczne różnicowanie | Dowolny różniczkowalny wykres obliczeniowy (domyślny) | Jedno podanie do tyłu |
| Symboliczne (SymPy, Mathematica) | Wyprowadzanie gradientów zamkniętych dla prac | Tylko czas kompilacji |

## Skrócona instrukcja: popularne instrumenty pochodne

| Funkcja | f(x) | f'(x) | Kontekst ML |
|---|---|---|---|
| Strata MSE | (1/n) suma(y_hat - y)^2 | (2/n)(y_hat - y) | Regresja |
| Entropia krzyżowa (binarna) | -(y log(p) + (1-y) log(1-p)) | p - y (po esicy) | Klasyfikacja binarna |
| Entropia krzyżowa (wiele) | -log(p_true_klasa) | p - one_hot(y) (po softmax) | Klasyfikacja wieloklasowa |
| Sigmoida | 1 / (1 + e^(-x)) | sigma(x) * (1 - sigma(x)) | Bramki wyjściowe, wyjście binarne |
| Tanh | (e^x - e^(-x)) / (e^x + e^(-x)) | 1 - tanh(x)^2 | Ukryte aktywacje (starsze) |
| ReLU | maks.(0, x) | 1 jeśli x > 0, 0 jeśli x < 0 | Default hidden activation |
| Leaky ReLU | max(0.01x, x) | 1 if x > 0, 0,01 jeśli x < 0 | Unikanie martwych neuronów |
| ŻELU | x * Fi(x) | Fi(x) + x * Fi(x) | Transformatory |
| Softmax_i | e^(x_i) / suma(e^(x_j)) | s_i(1 - s_i) dla i=j, -s_i*s_j dla i!=j | Warstwa wyjściowa (jakobianowa) |
| Log-softmax | x_i - log(suma(e^(x_j))) | 1 - softmax(x_i) dla i-tego wpisu | Numerycznie stabilny CE |
| Warstwa liniowa | y = Wx + b | dL/dW = dL/dy * x^T, dL/db = dL/dy | Każda warstwa |
| Regularyzacja L2 | lambda * suma(w^2) | 2 * lambda * w | Spadek wagi |
| Regularyzacja L1 | lambda * suma(\|w\|) | lambda * znak(w) | Rzadkość |

## Typowe błędy

- Zapominanie o współczynniku 1/n w stratach uśrednionych wsadowo (MSE, entropia krzyżowa). Gradient jest skalowany według wielkości partii.
- Obliczanie gradientu softmax jako wektora, gdy w rzeczywistości jest to macierz Jakobianu. W przypadku kombinacji entropii krzyżowej + softmax gradient upraszcza się do (p - y), co pozwala uniknąć pełnego Jakobianu.
- Zastosowanie reguły łańcucha w niewłaściwej kolejności. Pracuj wstecz od straty: dL/dW = dL/dy * dy/dW.
- Stosowanie h, które jest zbyt duże (h = 0,1) lub zbyt małe (h = 1e-15) dla pochodnych numerycznych. Trzymaj się h = 1e-7 dla float64.
- Zapominając, że ReLU ma niezdefiniowany gradient dokładnie przy x = 0. W praktyce ustaw go na 0 lub 0,5.

## Przepis sprawdzający gradient

```
For each parameter w:
  numeric_grad = (loss(w + h) - loss(w - h)) / (2h)
  auto_grad = backward pass value
  relative_error = |numeric - auto| / max(|numeric|, |auto|, 1e-8)
  assert relative_error < 1e-5
```

Błąd względny powyżej 1e-3 oznacza, że coś jest nie tak. Pomiędzy 1e-5 a 1e-3 zbadaj.