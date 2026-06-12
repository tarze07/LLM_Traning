# Stabilność numeryczna

> Liczby zmiennoprzecinkowe to nieszczelna abstrakcja. Ugryzie cię podczas trenowania i nie zauważysz, kiedy to nadejdzie.

**Typ:** Build
**Język:** Python
**Wymagania wstępne:** Faza 1, lekcje 01-04
**Czas:** ~120 minut

## Cele nauki

- Zaimplementować numerycznie stabilny softmax i log-sum-exp przy użyciu triku odejmowania maksimum
- Zidentyfikować przepełnienie (overflow), niedopełnienie (underflow) i katastrofalne znoszenie się cyfr (catastrophic cancellation) w obliczeniach zmiennoprzecinkowych
- Zweryfikować analityczne gradienty względem gradientów numerycznych za pomocą scentrowanych różnic skończonych
- Wyjaśnić, czemu bfloat16 jest preferowany nad float16 do trenowania i jak loss scaling zapobiega niedopełnieniu gradientów

## Problem

Twój model trenuje się od trzech godzin, a potem strata staje się NaN. Dodajesz instrukcję print. Logity są w porządku w kroku 9000. W kroku 9001 są `inf`. Do kroku 9002 każdy gradient jest `nan`, a trenowanie jest martwe.

Albo: twój model trenuje się do końca, ale dokładność jest 2% niższa niż w pracy naukowej, na której się opierasz. Sprawdzasz wszystko. Architektura się zgadza. Hiperparametry się zgadzają. Dane się zgadzają. Problem polega na tym, że w pracy użyto float32, a ty użyłeś float16 bez odpowiedniego skalowania. Trzydzieści dwa bity narastającego błędu zaokrąglenia po cichu zjadły twoją dokładność.

Albo: implementujesz funkcję straty cross-entropy od zera. Działa na małych logitach. Gdy logity przekraczają 100, zwraca `inf`. Softmax się przepełnił, bo `exp(100)` jest większe niż to, co może przedstawić float32. Każdy framework ML obsługuje to za pomocą dwulinijkowego triku. Ty nie wiedziałeś, że ten trik istnieje.

Stabilność numeryczna nie jest problemem teoretycznym. To różnica między biegiem trenowania, który się powiedzie, a takim, który po cichu zawiedzie. Każdy poważny błąd ML, który będziesz debugować, w końcu sprowadza się do liczb zmiennoprzecinkowych.

## Koncepcja

### IEEE 754: jak komputery przechowują liczby rzeczywiste

Komputery przechowują liczby rzeczywiste jako wartości zmiennoprzecinkowe zgodne ze standardem IEEE 754. Float ma trzy części: bit znaku, wykładnik (exponent) i mantysę (significand).

```
Float32 layout (32 bits total):
[1 sign] [8 exponent] [23 mantissa]

Value = (-1)^sign * 2^(exponent - 127) * 1.mantissa
```

Mantysa decyduje o precyzji (ile cyfr znaczących). Wykładnik decyduje o zakresie (jak wielka lub mała może być liczba).

```
Format     Bits   Exponent  Mantissa  Decimal digits  Range (approx)
float64    64     11        52        ~15-16          +/- 1.8e308
float32    32     8         23        ~7-8            +/- 3.4e38
float16    16     5         10        ~3-4            +/- 65,504
bfloat16   16     8         7         ~2-3            +/- 3.4e38
```

float32 daje około 7 cyfr dziesiętnych precyzji. To znaczy, że może odróżnić 1.0000001 od 1.0000002, ale nie 1.00000001 od 1.00000002. Po 7 cyfrach wszystko jest szumem zaokrąglenia.

float16 daje około 3 cyfr. Największa liczba, jaką może przedstawić, to 65 504. To niepokojąco mało dla ML, gdzie logity, gradienty i aktywacje regularnie przekraczają tę wartość.

bfloat16 to odpowiedź Google na problem zakresu float16. Ma ten sam 8-bitowy wykładnik co float32 (taki sam zakres, do 3.4e38), ale tylko 7 bitów mantysy (mniejsza precyzja niż float16). Przy trenowaniu sieci neuronowych zakres ma większe znaczenie niż precyzja, więc bfloat16 zwykle wygrywa.

### Czemu 0.1 + 0.2 != 0.3

Liczba 0.1 nie może być przedstawiona w sposób ścisły w binarnej liczbie zmiennoprzecinkowej. W systemie binarnym jest to ułamek okresowy:

```
0.1 in binary = 0.0001100110011001100110011... (repeating forever)
```

Float32 przycina to do 23 bitów mantysy. Przechowywana wartość to w przybliżeniu 0.100000001490116. Podobnie 0.2 jest przechowywane jako około 0.200000002980232. Ich suma to 0.300000004470348, a nie 0.3.

```
In Python:
>>> 0.1 + 0.2
0.30000000000000004

>>> 0.1 + 0.2 == 0.3
False
```

Ma to znaczenie dla ML, ponieważ:

1. Porównania straty takie jak `if loss < threshold` mogą dawać błędne wyniki
2. Akumulacja wielu małych wartości (aktualizacje gradientów na przestrzeni tysięcy kroków) odchyla się od prawdziwej sumy
3. Sumy kontrolne i testy reprodukowalności zawodzą, jeśli porównujesz floaty za pomocą `==`

Naprawa: nigdy nie porównuj floatów za pomocą `==`. Używaj `abs(a - b) < epsilon` lub `math.isclose()`.

### Katastrofalne znoszenie się cyfr (catastrophic cancellation)

Gdy odejmujesz dwie prawie równe liczby zmiennoprzecinkowe, cyfry znaczące się znoszą, a w efekcie pozostaje szum zaokrąglenia przesunięty do cyfr najwyższego rzędu.

```
a = 1.0000001    (stored as 1.00000011920929 in float32)
b = 1.0000000    (stored as 1.00000000000000 in float32)

True difference:  0.0000001
Computed:         0.00000011920929

Relative error: 19.2%
```

To jest 19% błąd względny z pojedynczego odejmowania. W ML zdarza się to, kiedy:

- Obliczasz wariancję danych o dużej średniej: `E[x^2] - E[x]^2`, gdy E[x] jest duże
- Odejmujesz prawie równe logarytmy prawdopodobieństw (log-probabilities)
- Obliczasz gradienty za pomocą różnic skończonych z za małym epsilonem

Naprawa: przekształć wzory, aby uniknąć odejmowania dużych, prawie równych liczb. Dla wariancji użyj algorytmu Welforda lub najpierw wycentruj dane. Dla log-prawdopodobieństw pracuj cały czas w przestrzeni logarytmicznej.

### Przepełnienie i niedopełnienie (overflow i underflow)

Przepełnienie (overflow) zdarza się, gdy wynik jest zbyt duży, aby go przedstawić. Niedopełnienie (underflow) zdarza się, gdy jest zbyt mały (bliżej zera niż najmniejsza przedstawialna liczba dodatnia).

```
Float32 boundaries:
  Maximum:  3.4028235e+38
  Minimum positive (normal): 1.175e-38
  Minimum positive (denorm): 1.401e-45
  Overflow:  anything > 3.4e38 becomes inf
  Underflow: anything < 1.4e-45 becomes 0.0
```

Funkcja `exp()` jest głównym źródłem przepełnienia w ML:

```
exp(88.7)  = 3.40e+38   (barely fits in float32)
exp(89.0)  = inf         (overflow)
exp(-87.3) = 1.18e-38   (barely above underflow)
exp(-104)  = 0.0         (underflow to zero)
```

Funkcja `log()` uderza w drugą stronę:

```
log(0.0)   = -inf
log(-1.0)  = nan
log(1e-45) = -103.3      (fine)
log(1e-46) = -inf        (input underflowed to 0, then log(0) = -inf)
```

W ML `exp()` pojawia się w softmax, sigmoidzie i obliczeniach prawdopodobieństw. `log()` pojawia się w cross-entropy, log-likelihoods i dywergencji KL. Kombinacja `log(exp(x))` jest polem minowym bez odpowiednich trików.

### Trik log-sum-exp

Obliczanie `log(sum(exp(x_i)))` bezpośrednio jest numerycznie niebezpieczne. Jeśli jakiekolwiek `x_i` jest duże, `exp(x_i)` przepełnia się. Jeśli wszystkie `x_i` są bardzo ujemne, każde `exp(x_i)` niedopełnia się do zera, a `log(0)` to `-inf`.

Trik: odejmij maksymalną wartość przed eksponencjacją.

```
log(sum(exp(x_i))) = max(x) + log(sum(exp(x_i - max(x))))
```

Czemu to działa: po odjęciu `max(x)` najwyższy wykładnik to `exp(0) = 1`. Przepełnienie staje się niemożliwe. Przynajmniej jeden składnik sumy wynosi 1, więc suma jest co najmniej 1, a `log(1) = 0`. Niedopełnienie do `-inf` jest niemożliwe.

Dowód:

```
log(sum(exp(x_i)))
= log(sum(exp(x_i - c + c)))                    (add and subtract c)
= log(sum(exp(x_i - c) * exp(c)))               (exp(a+b) = exp(a)*exp(b))
= log(exp(c) * sum(exp(x_i - c)))               (factor out exp(c))
= c + log(sum(exp(x_i - c)))                    (log(a*b) = log(a) + log(b))
```

Ustawiamy `c = max(x)` i przepełnienie zostaje wyeliminowane.

Ten trik pojawia się wszędzie w ML:
- Normalizacja softmax
- Obliczanie funkcji straty cross-entropy
- Sumowanie log-prawdopodobieństw w modelach sekwencyjnych
- Mieszanina rozkładów Gaussa (Mixture of Gaussians)
- Wnioskowanie wariacyjne

### Czemu softmax potrzebuje triku odejmowania maksimum

Softmax konwertuje logity na prawdopodobieństwa:

```
softmax(x_i) = exp(x_i) / sum(exp(x_j))
```

Bez triku, logity [100, 101, 102] powodują przepełnienie:

```
exp(100) = 2.69e43
exp(101) = 7.31e43
exp(102) = 1.99e44
sum      = 2.99e44

These overflow float32 (max ~3.4e38)? No, 2.69e43 < 3.4e38? Actually:
exp(88.7) is already at the float32 limit.
exp(100) = inf in float32.
```

Z trikiem, odejmujemy max(x) = 102:

```
exp(100 - 102) = exp(-2) = 0.135
exp(101 - 102) = exp(-1) = 0.368
exp(102 - 102) = exp(0)  = 1.000
sum = 1.503

softmax = [0.090, 0.245, 0.665]
```

Prawdopodobieństwa są identyczne. Obliczenie jest bezpieczne. To nie jest optymalizacja. To wymóg poprawności.

### NaN i Inf: wykrywanie i zapobieganie

`nan` (Not a Number) i `inf` (infinity) rozprzestrzeniają się wirusowo przez obliczenia. Jeden `nan` w aktualizacji gradientu powoduje, że waga staje się `nan`, co powoduje, że każde kolejne wyjście jest `nan`. Trenowanie jest martwe w ciągu jednego kroku.

Jak powstaje `inf`:
- `exp()` dużej liczby dodatniej
- Dzielenie przez zero: `1.0 / 0.0`
- Przepełnienie `float32` w akumulacjach

Jak powstaje `nan`:
- `0.0 / 0.0`
- `inf - inf`
- `inf * 0`
- `sqrt()` liczby ujemnej
- `log()` liczby ujemnej
- Jakakolwiek operacja arytmetyczna z udziałem istniejącego `nan`

Wykrywanie:

```python
import math

math.isnan(x)       # True if x is nan
math.isinf(x)       # True if x is +inf or -inf
math.isfinite(x)    # True if x is neither nan nor inf
```

Strategie zapobiegania:

1. Ograniczanie wejść do `exp()`: `exp(clamp(x, -80, 80))`
2. Dodawanie epsilonu do mianowników: `x / (y + 1e-8)`
3. Dodawanie epsilonu wewnątrz `log()`: `log(x + 1e-8)`
4. Używanie stabilnych implementacji (log-sum-exp, stabilny softmax)
5. Przycinanie gradientów (gradient clipping), aby zapobiec eksplozji wag
6. Sprawdzanie `nan`/`inf` po każdym forward pass podczas debugowania

### Numeryczne sprawdzanie gradientów

Analityczne gradienty (z backpropagation) mogą zawierać błędy. Numeryczne sprawdzanie gradientów weryfikuje je, obliczając gradienty za pomocą różnic skończonych.

Wzór scentrowanej różnicy (centered difference):

```
df/dx ~= (f(x + h) - f(x - h)) / (2h)
```

Jest to dokładność O(h^2), znacznie lepsza niż różnica progresywna (forward difference) `(f(x+h) - f(x)) / h`, która jest tylko O(h).

Wybór h: za duże i przybliżenie jest niedokładne. Za małe i katastrofalne znoszenie się cyfr niszczy wynik. Typowe wartości to `h = 1e-5` do `1e-7`.

Sprawdzenie: oblicz błąd względny między gradientami analitycznymi i numerycznymi.

```
relative_error = |grad_analytical - grad_numerical| / max(|grad_analytical|, |grad_numerical|, 1e-8)
```

Praktyczne zasady:
- relative_error < 1e-7: idealnie, gradient jest poprawny
- relative_error < 1e-5: akceptowalnie, prawdopodobnie poprawny
- relative_error > 1e-3: coś jest nie tak
- relative_error > 1: gradient jest całkowicie błędny

Zawsze sprawdzaj gradienty podczas implementacji nowej warstwy lub funkcji straty. PyTorch udostępnia do tego `torch.autograd.gradcheck()`.

### Trenowanie w mieszanej precyzji (mixed precision)

Współczesne GPU mają wyspecjalizowany sprzęt (Tensor Cores), który wykonuje mnożenia macierzy float16 2-8x szybciej niż float32. Trenowanie w mieszanej precyzji wykorzystuje to:

```
1. Maintain float32 master copy of weights
2. Forward pass in float16 (fast)
3. Compute loss in float32 (prevents overflow)
4. Backward pass in float16 (fast)
5. Scale gradients to float32
6. Update float32 master weights
```

Problem z czystym trenowaniem float16: gradienty są często bardzo małe (1e-8 lub mniejsze). Float16 niedopełnia wszystko poniżej ~6e-8 do zera. Twój model przestaje się uczyć, bo wszystkie aktualizacje gradientów są zerowe.

Naprawą jest loss scaling:

```
1. Multiply loss by a large scale factor (e.g., 1024)
2. Backward pass computes gradients of (loss * 1024)
3. All gradients are 1024x larger (pushed above float16 underflow)
4. Divide gradients by 1024 before updating weights
5. Net effect: same update, but no underflow
```

Dynamiczny loss scaling automatycznie dostosowuje współczynnik skalowania. Zaczyna od dużej wartości (65536). Jeśli gradienty przepełniają się do `inf`, zmniejsza ją o połowę. Jeśli N kroków przejdzie bez przepełnienia, podwaja ją.

### bfloat16 vs float16: czemu bfloat16 wygrywa przy trenowaniu

```
float16:   [1 sign] [5 exponent]  [10 mantissa]
bfloat16:  [1 sign] [8 exponent]  [7 mantissa]
```

float16 ma większą precyzję (10 bitów mantysy vs 7), ale ograniczony zakres (maks. ~65 504). bfloat16 ma mniejszą precyzję, ale taki sam zakres jak float32 (maks. ~3.4e38).

Przy trenowaniu sieci neuronowych:

- Aktywacje i logity regularnie przekraczają 65 504 podczas skoków w trenowaniu. float16 się przepełnia; bfloat16 sobie z tym radzi.
- Loss scaling jest wymagany przy float16, ale zwykle niepotrzebny przy bfloat16, ponieważ jego zakres pokrywa spektrum wielkości gradientów.
- bfloat16 to po prostu obcięcie float32: usuń dolne 16 bitów mantysy. Konwersja jest trywialna i bezstratna w zakresie wykładnika.

float16 jest preferowany do inferencji, gdzie wartości są ograniczone i precyzja ma większe znaczenie. bfloat16 jest preferowany do trenowania, gdzie zakres ma większe znaczenie. To dlatego TPU i nowoczesne GPU NVIDIA (A100, H100) mają natywne wsparcie dla bfloat16.

### Przycinanie gradientów (gradient clipping)

Eksplodujące gradienty zdarzają się, gdy gradienty rosną wykładniczo przez wiele warstw (powszechne w RNN, głębokich sieciach i transformerach). Pojedynczy duży gradient może uszkodzić wszystkie wagi w jednym kroku.

Dwa typy przycinania:

**Przycinanie po wartości (clip by value):** ogranicz każdy element gradientu niezależnie.

```
grad = clamp(grad, -max_val, max_val)
```

Proste, ale może zmienić kierunek wektora gradientu.

**Przycinanie po normie (clip by norm):** przeskaluj cały wektor gradientu tak, aby jego norma nie przekroczyła progu.

```
if ||grad|| > max_norm:
    grad = grad * (max_norm / ||grad||)
```

Zachowuje kierunek gradientu. To robi `torch.nn.utils.clip_grad_norm_()`. To standardowy wybór.

Typowe wartości: `max_norm=1.0` dla transformerów, `max_norm=0.5` dla RL, `max_norm=5.0` dla prostszych sieci.

Przycinanie gradientów to nie jest hack. To mechanizm bezpieczeństwa. Bez niego pojedyncza nietypowa partia danych (batch) może wygenerować gradient wystarczająco duży, aby zniszczyć tygodnie trenowania.

### Warstwy normalizacyjne jako stabilizatory numeryczne

Batch normalization, layer normalization i RMS normalization są zwykle przedstawiane jako regularyzatory pomagające w zbieżności trenowania. Są one również stabilizatorami numerycznymi.

Bez normalizacji aktywacje mogą rosnąć lub zmniejszać się wykładniczo przez warstwy:

```
Layer 1: values in [0, 1]
Layer 5: values in [0, 100]
Layer 10: values in [0, 10,000]
Layer 50: values in [0, inf]
```

Normalizacja przesuwa i przeskalowuje aktywacje w każdej warstwie:

```
LayerNorm(x) = (x - mean(x)) / (std(x) + epsilon) * gamma + beta
```

`epsilon` (typowo 1e-5) zapobiega dzieleniu przez zero, gdy wszystkie aktywacje są identyczne. Wyuczone parametry `gamma` i `beta` pozwalają sieci przywrócić dowolną potrzebną skalę.

Trzyma to wartości w numerycznie bezpiecznym zakresie w całej sieci, zapobiegając zarówno przepełnieniu w forward pass, jak i eksplozji gradientów w backward pass.

### Częste błędy numeryczne w ML

**Błąd: strata to NaN po kilku epokach.**
Przyczyna: logity wzrosły zbyt mocno, softmax się przepełnił. Albo learning rate jest zbyt wysoki i wagi rozbiegły się.
Naprawa: użyj stabilnego softmax (odejmowanie maksimum), zmniejsz learning rate, dodaj przycinanie gradientów.

**Błąd: strata jest zablokowana na log(num_classes).**
Przyczyna: wyjścia modelu są bliskie jednorodnym prawdopodobieństwom. Często oznacza to, że gradienty zanikają (vanishing) albo model wcale się nie uczy.
Naprawa: sprawdź, czy etykiety danych są poprawne, zweryfikuj funkcję straty, sprawdź, czy nie ma martwych ReLU.

**Błąd: dokładność walidacyjna jest niższa od oczekiwanej o 1-3%.**
Przyczyna: mieszana precyzja bez odpowiedniego loss scaling. Niedopełnienie gradientów po cichu zeruje małe aktualizacje.
Naprawa: włącz dynamiczny loss scaling albo przejdź na bfloat16.

**Błąd: normy gradientów wynoszą 0.0 dla niektórych warstw.**
Przyczyna: martwe neurony ReLU (wszystkie wejścia ujemne) albo niedopełnienie float16.
Naprawa: użyj LeakyReLU lub GELU, użyj skalowania gradientów, sprawdź inicjalizację wag.

**Błąd: model działa na jednym GPU, ale daje inne wyniki na drugim.**
Przyczyna: niedeterministyczny porządek akumulacji zmiennoprzecinkowej. Równoległe redukcje na GPU sumują w różnym porządku na różnym sprzęcie, a dodawanie zmiennoprzecinkowe nie jest łączne (associative).
Naprawa: zaakceptuj małe różnice (1e-6) albo ustaw `torch.use_deterministic_algorithms(True)` i zaakceptuj spadek wydajności.

**Błąd: `exp()` zwraca `inf` przy obliczaniu straty.**
Przyczyna: surowe logity przekazane do `exp()` bez triku odejmowania maksimum.
Naprawa: użyj `torch.nn.functional.log_softmax()`, który implementuje log-sum-exp wewnętrznie.

**Błąd: trenowanie rozbiega się po przejściu z float32 na float16.**
Przyczyna: float16 nie może przedstawić wielkości gradientów poniżej 6e-8 ani aktywacji powyżej 65 504.
Naprawa: użyj mieszanej precyzji z loss scaling (AMP) albo użyj bfloat16.

## Zbuduj to

### Krok 1: Demonstracja ograniczeń precyzji liczb zmiennoprzecinkowych

```python
print("=== Floating Point Precision ===")
print(f"0.1 + 0.2 = {0.1 + 0.2}")
print(f"0.1 + 0.2 == 0.3? {0.1 + 0.2 == 0.3}")
print(f"Difference: {(0.1 + 0.2) - 0.3:.2e}")
```

### Krok 2: Implementacja naiwnego i stabilnego softmax

```python
import math

def softmax_naive(logits):
    exps = [math.exp(z) for z in logits]
    total = sum(exps)
    return [e / total for e in exps]

def softmax_stable(logits):
    max_logit = max(logits)
    exps = [math.exp(z - max_logit) for z in logits]
    total = sum(exps)
    return [e / total for e in exps]

safe_logits = [2.0, 1.0, 0.1]
print(f"Naive:  {softmax_naive(safe_logits)}")
print(f"Stable: {softmax_stable(safe_logits)}")

dangerous_logits = [100.0, 101.0, 102.0]
print(f"Stable: {softmax_stable(dangerous_logits)}")
# softmax_naive(dangerous_logits) would return [nan, nan, nan]
```

### Krok 3: Implementacja stabilnego log-sum-exp

```python
def logsumexp_naive(values):
    return math.log(sum(math.exp(v) for v in values))

def logsumexp_stable(values):
    c = max(values)
    return c + math.log(sum(math.exp(v - c) for v in values))

safe = [1.0, 2.0, 3.0]
print(f"Naive:  {logsumexp_naive(safe):.6f}")
print(f"Stable: {logsumexp_stable(safe):.6f}")

large = [500.0, 501.0, 502.0]
print(f"Stable: {logsumexp_stable(large):.6f}")
# logsumexp_naive(large) returns inf
```

### Krok 4: Implementacja stabilnej cross-entropy

```python
def cross_entropy_naive(true_class, logits):
    probs = softmax_naive(logits)
    return -math.log(probs[true_class])

def cross_entropy_stable(true_class, logits):
    max_logit = max(logits)
    shifted = [z - max_logit for z in logits]
    log_sum_exp = math.log(sum(math.exp(s) for s in shifted))
    log_prob = shifted[true_class] - log_sum_exp
    return -log_prob

logits = [2.0, 5.0, 1.0]
true_class = 1
print(f"Naive:  {cross_entropy_naive(true_class, logits):.6f}")
print(f"Stable: {cross_entropy_stable(true_class, logits):.6f}")
```

### Krok 5: Sprawdzanie gradientów

```python
def numerical_gradient(f, x, h=1e-5):
    grad = []
    for i in range(len(x)):
        x_plus = x[:]
        x_minus = x[:]
        x_plus[i] += h
        x_minus[i] -= h
        grad.append((f(x_plus) - f(x_minus)) / (2 * h))
    return grad

def check_gradient(analytical, numerical, tolerance=1e-5):
    for i, (a, n) in enumerate(zip(analytical, numerical)):
        denom = max(abs(a), abs(n), 1e-8)
        rel_error = abs(a - n) / denom
        status = "OK" if rel_error < tolerance else "FAIL"
        print(f"  param {i}: analytical={a:.8f} numerical={n:.8f} "
              f"rel_error={rel_error:.2e} [{status}]")

def f(params):
    x, y = params
    return x**2 + 3*x*y + y**3

def f_grad(params):
    x, y = params
    return [2*x + 3*y, 3*x + 3*y**2]

point = [2.0, 1.0]
analytical = f_grad(point)
numerical = numerical_gradient(f, point)
check_gradient(analytical, numerical)
```

## Użyj tego

### Symulacja mieszanej precyzji

```python
import struct

def float32_to_float16_round(x):
    packed = struct.pack('f', x)
    f32 = struct.unpack('f', packed)[0]
    packed16 = struct.pack('e', f32)
    return struct.unpack('e', packed16)[0]

def simulate_bfloat16(x):
    packed = struct.pack('f', x)
    as_int = int.from_bytes(packed, 'little')
    truncated = as_int & 0xFFFF0000
    repacked = truncated.to_bytes(4, 'little')
    return struct.unpack('f', repacked)[0]
```

### Przycinanie gradientów

```python
def clip_by_norm(gradients, max_norm):
    total_norm = math.sqrt(sum(g**2 for g in gradients))
    if total_norm > max_norm:
        scale = max_norm / total_norm
        return [g * scale for g in gradients]
    return gradients

grads = [10.0, 20.0, 30.0]
clipped = clip_by_norm(grads, max_norm=5.0)
print(f"Original norm: {math.sqrt(sum(g**2 for g in grads)):.2f}")
print(f"Clipped norm:  {math.sqrt(sum(g**2 for g in clipped)):.2f}")
print(f"Direction preserved: {[c/clipped[0] for c in clipped]} == {[g/grads[0] for g in grads]}")
```

### Wykrywanie NaN/Inf

```python
def check_tensor(name, values):
    has_nan = any(math.isnan(v) for v in values)
    has_inf = any(math.isinf(v) for v in values)
    if has_nan or has_inf:
        print(f"WARNING {name}: nan={has_nan} inf={has_inf}")
        return False
    return True

check_tensor("good", [1.0, 2.0, 3.0])
check_tensor("bad",  [1.0, float('nan'), 3.0])
check_tensor("ugly", [1.0, float('inf'), 3.0])
```

Zobacz `code/numerical.py` po kompletne implementacje z demonstracją wszystkich przypadków granicznych.

## Wypuszczenie (Ship It)

Ta lekcja tworzy:
- `code/numerical.py` ze stabilnym softmax, log-sum-exp, cross-entropy, sprawdzaniem gradientów i symulacją mieszanej precyzji
- `outputs/prompt-numerical-debugger.md` do diagnozowania problemów NaN/Inf i numerycznych w trenowaniu

Te stabilne implementacje powrócą w Fazie 3 podczas budowania pętli trenowania oraz w Fazie 4 podczas implementacji mechanizmów uwagi (attention).

## Zadania

1. **Katastrofalne znoszenie się cyfr.** Oblicz wariancję [1000000.0, 1000001.0, 1000002.0] używając naiwnego wzoru `E[x^2] - E[x]^2` w float32. Następnie oblicz ją używając algorytmu online Welforda. Porównaj błędy względem prawdziwej wariancji (0.6667).

2. **Polowanie na precyzję.** Znajdź najmniejszą dodatnią wartość float32 `x` taką, że `1.0 + x == 1.0` w Pythonie. To jest epsilon maszynowy (machine epsilon). Zweryfikuj, że odpowiada `numpy.finfo(numpy.float32).eps`.

3. **Przypadki graniczne log-sum-exp.** Przetestuj swoją funkcję `logsumexp_stable` z: (a) wszystkimi wartościami równymi, (b) jedną wartością dużo większą od pozostałych, (c) wszystkimi wartościami bardzo ujemnymi (-1000). Zweryfikuj, że daje poprawne wyniki tam, gdzie wersja naiwna zawodzi.

4. **Sprawdzanie gradientów warstwy sieci neuronowej.** Zaimplementuj jedną warstwę liniową `y = Wx + b` oraz jej analityczny backward pass. Użyj `numerical_gradient`, aby zweryfikować poprawność dla macierzy wag 3x2.

5. **Eksperyment z loss scaling.** Zasymuluj trenowanie z float16: stwórz losowe gradienty w zakresie [1e-9, 1e-3], skonwertuj do float16 i zmierz, jaka część staje się zerem. Następnie zastosuj loss scaling (pomnóż przez 1024), skonwertuj do float16, przeskaluj wstecz i zmierz frakcję zer ponownie.

## Kluczowe terminy

| Termin | Co się mówi | Co to faktycznie znaczy |
|------|----------------|----------------------|
| IEEE 754 | "Standard dla floatów" | Międzynarodowy standard definiujący binarne formaty zmiennoprzecinkowe, zasady zaokrąglania i wartości specjalne (inf, nan). Każdy współczesny CPU i GPU go implementuje. |
| Epsilon maszynowy (machine epsilon) | "Granica precyzji" | Najmniejsza wartość e taka, że 1.0 + e != 1.0 w danym formacie zmiennoprzecinkowym. Dla float32 to około 1.19e-7. |
| Katastrofalne znoszenie się cyfr (catastrophic cancellation) | "Utrata precyzji przy odejmowaniu" | Gdy odejmujemy prawie równe liczby zmiennoprzecinkowe, cyfry znaczące się znoszą i szum zaokrąglenia dominuje wynik. |
| Przepełnienie (overflow) | "Liczba za duża" | Wynik przekracza maksymalną przedstawialną wartość i staje się inf. exp(89) przepełnia float32. |
| Niedopełnienie (underflow) | "Liczba za mała" | Wynik jest bliżej zera niż najmniejsza przedstawialna liczba dodatnia i staje się 0.0. exp(-104) niedopełnia float32. |
| Trik log-sum-exp | "Najpierw odejmij maksimum" | Obliczanie log(sum(exp(x))) przez wyłączenie exp(max(x)) przed nawias, aby zapobiec przepełnieniu i niedopełnieniu. Używane w softmax, cross-entropy i obliczeniach log-prawdopodobieństw. |
| Stabilny softmax | "Softmax, który się nie wysadza" | Odejmowanie max(logits) przed eksponencjacją. Numerycznie identyczny wynik, przepełnienie niemożliwe. |
| Sprawdzanie gradientów (gradient checking) | "Weryfikacja backpropu" | Porównywanie analitycznych gradientów z backpropagation z gradientami numerycznymi z różnic skończonych, aby wychwycić błędy implementacji. |
| Mieszana precyzja (mixed precision) | "Float16 forward, float32 backward" | Używanie floatów niższej precyzji dla operacji krytycznych pod względem szybkości i floatów wyższej precyzji dla operacji wrażliwych numerycznie. Typowe przyspieszenie to 2-3x. |
| Loss scaling | "Zapobieganie niedopełnieniu gradientów" | Mnożenie straty przez dużą stałą przed backpropagation, aby gradienty pozostały w zakresie przedstawialnym przez float16, a następnie dzielenie przez tę samą stałą przed aktualizacją wag. |
| bfloat16 | "Brain floating point" | 16-bitowy format Google z 8 bitami wykładnika (taki sam zakres jak float32) i 7 bitami mantysy (mniejsza precyzja niż float16). Preferowany do trenowania. |
| Przycinanie gradientów (gradient clipping) | "Ogranicz normę gradientu" | Przeskalowanie wektora gradientu tak, aby jego norma nie przekroczyła progu. Zapobiega eksplozji gradientów niszczącej wagi. |
| NaN | "Not a Number" | Specjalna wartość zmiennoprzecinkowa pochodząca z niezdefiniowanych operacji (0/0, inf-inf, sqrt(-1)). Rozprzestrzenia się przez wszystkie kolejne operacje arytmetyczne. |
| Inf | "Infinity" (nieskończoność) | Specjalna wartość zmiennoprzecinkowa pochodząca z przepełnienia lub dzielenia przez zero. Może się połączyć i utworzyć NaN (inf - inf, inf * 0). |
| Gradient numeryczny | "Brutalna siła zamiast derywaty" | Przybliżanie derywaty poprzez obliczenie f(x+h) i f(x-h) i podzielenie przez 2h. Wolne, ale wiarygodne do weryfikacji. |

## Dalsze materiały

- [What Every Computer Scientist Should Know About Floating-Point Arithmetic (Goldberg 1991)](https://docs.oracle.com/cd/E19957-01/806-3568/ncg_goldberg.html) -- klasyczny, definitywny materiał źródłowy, gęsty, ale kompletny
- [Mixed Precision Training (Micikevicius et al., 2018)](https://arxiv.org/abs/1710.03740) -- artykuł NVIDIA, który wprowadził loss scaling dla trenowania w float16
- [AMP: Automatic Mixed Precision (PyTorch docs)](https://pytorch.org/docs/stable/amp.html) -- praktyczny przewodnik po mieszanej precyzji w PyTorch
- [bfloat16 format (Google Cloud TPU docs)](https://cloud.google.com/tpu/docs/bfloat16) -- czemu Google wybrał ten format dla TPU
- [Kahan Summation (Wikipedia)](https://en.wikipedia.org/wiki/Kahan_summation_algorithm) -- algorytm redukcji błędu zaokrąglenia w sumach zmiennoprzecinkowych
