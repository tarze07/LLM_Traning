# Stabilność numeryczna

> Liczba zmiennoprzecinkowa jest nieszczelną abstrakcją. Ugryzie Cię podczas treningu i nie zobaczysz, że to nadchodzi.

**Typ:** Kompilacja
**Język:** Python
**Wymagania wstępne:** Faza 1, lekcje 01-04
**Czas:** ~120 minut

## Cele nauczania

- Zaimplementuj numerycznie stabilny softmax i log-sum-exp za pomocą sztuczki z odjęciem maksimum
- Identyfikacja przepełnienia, niedomiaru i katastrofalnego anulowania w obliczeniach zmiennoprzecinkowych
- Weryfikacja gradientów analitycznych względem gradientów numerycznych przy użyciu wyśrodkowanych różnic skończonych
- Wyjaśnij, dlaczego do treningu preferowany jest bfloat16 zamiast float16 i jak skalowanie strat zapobiega niedopełnieniu gradientu

## Problem

Twój model trenuje przez trzy godziny, po czym strata wynosi NaN. Dodajesz instrukcję drukowania. Logity są w porządku w kroku 9000. W kroku 9001 są to `inf`. Do kroku 9002 każdy gradient ma wartość `nan` i szkolenie jest martwe.

Lub: Twój model ćwiczy się do końca, ale dokładność jest o 2% gorsza niż podaje dokument. Sprawdzasz wszystko. Architektura pasuje. Hiperparametry pasują. Dopasowania danych. Problem polega na tym, że papier użył float32, a ty użyłeś float16 bez odpowiedniego skalowania. Trzydzieści dwa bity skumulowanego błędu zaokrągleń po cichu pożerają twoją dokładność.

Lub: wdrażasz od zera utratę entropii krzyżowej. Działa na małych logitach. Gdy logity przekraczają 100, zwraca `inf`. Softmax został przepełniony, ponieważ `exp(100)` jest większy niż może reprezentować float32. Każdy framework ML radzi sobie z tym za pomocą dwuwierszowej sztuczki. Nie wiedziałeś, że istnieje taka sztuczka.

Stabilność numeryczna nie jest problemem teoretycznym. To jest różnica pomiędzy sukcesem treningu, a tym, który po cichu się nie udał. Każdy poważny błąd ML, który będziesz debugować, ostatecznie sprowadza się do liczby zmiennoprzecinkowej.

## Koncepcja

### IEEE 754: Jak komputery przechowują liczby rzeczywiste

Komputery przechowują liczby rzeczywiste jako wartości zmiennoprzecinkowe zgodnie ze standardem IEEE 754. Pływak składa się z trzech części: bitu znaku, wykładnika i mantysy (znaczącej).

```
Float32 layout (32 bits total):
[1 sign] [8 exponent] [23 mantissa]

Value = (-1)^sign * 2^(exponent - 127) * 1.mantissa
```

Mantysa określa precyzję (ile cyfr znaczących). Wykładnik określa zakres (jak duża lub mała może być liczba).

```
Format     Bits   Exponent  Mantissa  Decimal digits  Range (approx)
float64    64     11        52        ~15-16          +/- 1.8e308
float32    32     8         23        ~7-8            +/- 3.4e38
float16    16     5         10        ~3-4            +/- 65,504
bfloat16   16     8         7         ~2-3            +/- 3.4e38
```

float32 daje około 7 cyfr dziesiętnych precyzji. Oznacza to, że potrafi rozróżnić 1,0000001 i 1,0000002, ale nie 1,00000001 i 1,00000002. Po 7 cyfrach wszystko kręci się wokół szumu.

float16 daje około 3 cyfr. Największa liczba, jaką może reprezentować, to 65 504. Jest to niepokojąco małe w przypadku uczenia maszynowego, gdzie logity, gradienty i aktywacje rutynowo przekraczają tę wartość.

bfloat16 to odpowiedź Google na problem z zasięgiem float16. Ma ten sam 8-bitowy wykładnik co float32 (ten sam zakres, aż do 3,4e38), ale tylko 7 bitów mantysy (mniejsza precyzja niż float16). W przypadku uczenia sieci neuronowych zasięg ma większe znaczenie niż precyzja, dlatego bfloat16 zwykle wygrywa.

### Dlaczego 0,1 + 0,2 != 0,3

Liczby 0,1 nie można dokładnie przedstawić w binarnym formacie zmiennoprzecinkowym. W podstawie 2 jest to ułamek powtarzalny:

```
0.1 in binary = 0.0001100110011001100110011... (repeating forever)
```

Float32 obcina to do 23 bitów mantysy. Zapisana wartość wynosi około 0,100000001490116. Podobnie 0,2 jest przechowywane jako około 0,200000002980232. Ich suma wynosi 0,300000004470348, a nie 0,3.

```
In Python:
>>> 0.1 + 0.2
0.30000000000000004

>>> 0.1 + 0.2 == 0.3
False
```

Ma to znaczenie dla ML, ponieważ:

1. Porównania strat, takie jak `if loss < threshold`, mogą dawać błędne odpowiedzi
2. Gromadzenie wielu małych wartości (aktualizacje gradientów na przestrzeni tysięcy kroków) odbiega od sumy prawdziwej
3. Sumy kontrolne i testy odtwarzalności nie powiodą się, jeśli porównasz liczby zmiennoprzecinkowe z `==`

Poprawka: nigdy nie porównuj zmiennoprzecinkowych z `==`. Użyj `abs(a - b) < epsilon` lub `math.isclose()`.

### Katastrofalne anulowanie

Kiedy odejmiesz dwie prawie równe liczby zmiennoprzecinkowe, cyfry znaczące znoszą się i pozostaje szum zaokrąglania promowany do cyfr wiodących.

```
a = 1.0000001    (stored as 1.00000011920929 in float32)
b = 1.0000000    (stored as 1.00000000000000 in float32)

True difference:  0.0000001
Computed:         0.00000011920929

Relative error: 19.2%
```

Jest to błąd względny wynoszący 19% przy pojedynczym odjęciu. W ML dzieje się tak za każdym razem, gdy:

- Oblicz wariancję danych z dużą średnią: `E[x^2] - E[x]^2` gdy E[x] jest duże
- Odejmij prawie równe logarytmiczne prawdopodobieństwa
- Obliczanie gradientów o skończonej różnicy przy zbyt małym epsilonie

Poprawka: zmień układ formuł, aby uniknąć odejmowania dużych, prawie równych liczb. Aby uzyskać wariancję, użyj algorytmu Welforda lub najpierw wyśrodkuj dane. Aby uzyskać prawdopodobieństwo dziennika, pracuj w przestrzeni dziennika.

### Przepełnienie i niedopełnienie

Przepełnienie ma miejsce, gdy wynik jest zbyt duży, aby go przedstawić. Niedomiar ma miejsce, gdy jest zbyt mały (bliższy zera niż najmniejsza możliwa do przedstawienia liczba dodatnia).

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

Funkcja `log()` działa w innym kierunku:

```
log(0.0)   = -inf
log(-1.0)  = nan
log(1e-45) = -103.3      (fine)
log(1e-46) = -inf        (input underflowed to 0, then log(0) = -inf)
```

W ML `exp()` pojawia się w obliczeniach softmax, sigmoid i prawdopodobieństwa. `log()` pojawia się w przypadku entropii krzyżowej, logarytmu wiarygodności i rozbieżności KL. Kombinacja `log(exp(x))` to pole minowe bez odpowiednich sztuczek.

### Sztuczka log-sumy-exp

Bezpośrednie obliczanie `log(sum(exp(x_i)))` jest numerycznie niebezpieczne. Jeśli którykolwiek `x_i` jest duży, `exp(x_i)` powoduje przepełnienie. Jeśli wszystkie `x_i` są bardzo ujemne, każde `exp(x_i)` spada do zera i `log(0)` wynosi `-inf`.

Sztuczka: odejmij maksymalną wartość przed potęgowaniem.

```
log(sum(exp(x_i))) = max(x) + log(sum(exp(x_i - max(x))))
```

Dlaczego to działa: po odjęciu `max(x)` największym wykładnikiem jest `exp(0) = 1`. Nie ma możliwości przepełnienia. Co najmniej jeden wyraz w sumie wynosi 1, zatem suma wynosi co najmniej 1 oraz `log(1) = 0`. Nie jest możliwe niedopełnienie `-inf`.

Dowód:

```
log(sum(exp(x_i)))
= log(sum(exp(x_i - c + c)))                    (add and subtract c)
= log(sum(exp(x_i - c) * exp(c)))               (exp(a+b) = exp(a)*exp(b))
= log(exp(c) * sum(exp(x_i - c)))               (factor out exp(c))
= c + log(sum(exp(x_i - c)))                    (log(a*b) = log(a) + log(b))
```

Ustaw `c = max(x)`, a przepełnienie zostanie wyeliminowane.

Ta sztuczka pojawia się wszędzie w ML:
- Normalizacja Softmax
- Obliczanie strat między entropią
- Sumowanie logarytmiczne w modelach sekwencyjnych
- Mieszanka Gaussa
- Wnioskowanie wariacyjne

### Dlaczego Softmax potrzebuje sztuczki z maksymalnym odejmowaniem

Softmax konwertuje logity na prawdopodobieństwa:

```
softmax(x_i) = exp(x_i) / sum(exp(x_j))
```

Bez tej sztuczki logity [100, 101, 102] powodują przepełnienie:

```
exp(100) = 2.69e43
exp(101) = 7.31e43
exp(102) = 1.99e44
sum      = 2.99e44

These overflow float32 (max ~3.4e38)? No, 2.69e43 < 3.4e38? Actually:
exp(88.7) is already at the float32 limit.
exp(100) = inf in float32.
```

Za pomocą tej sztuczki odejmij max(x) = 102:

```
exp(100 - 102) = exp(-2) = 0.135
exp(101 - 102) = exp(-1) = 0.368
exp(102 - 102) = exp(0)  = 1.000
sum = 1.503

softmax = [0.090, 0.245, 0.665]
```

Prawdopodobieństwa są identyczne. Obliczenia są bezpieczne. To nie jest optymalizacja. Jest to wymóg poprawności.

### NaN i Inf: wykrywanie i zapobieganie

`nan` (nie liczba) i `inf` (nieskończoność) rozprzestrzeniają się wirusowo poprzez obliczenia. Jeden `nan` w aktualizacji gradientu daje wagę `nan`, co daje każdemu kolejnemu wynikowi `nan`. Trening kończy się w ciągu jednego kroku.

Jak wygląda `inf`:
- `exp()` dużej liczby dodatniej
- Dzielenie przez zero: `1.0 / 0.0`
- `float32` przepełnienie w nagromadzeniach

Jak wygląda `nan`:
- `0.0 / 0.0`
- `inf - inf`
- `inf * 0`
- `sqrt()` liczby ujemnej
- `log()` liczby ujemnej
- Dowolna arytmetyka obejmująca istniejącą `nan`

Wykrywanie:

```python
import math

math.isnan(x)       # True if x is nan
math.isinf(x)       # True if x is +inf or -inf
math.isfinite(x)    # True if x is neither nan nor inf
```

Strategie zapobiegawcze:

1. Zamocuj wejścia do `exp()`: `exp(clamp(x, -80, 80))`
2. Dodaj epsilon do mianowników: `x / (y + 1e-8)`
3. Dodaj epsilon do `log()`: `log(x + 1e-8)`
4. Używaj stabilnych implementacji (log-sum-exp, stabilny softmax)
5. Obcinanie gradientu, aby zapobiec eksplozji ciężaru
6. Sprawdź `nan`/`inf` po każdym przejściu do przodu podczas debugowania

### Numeryczne sprawdzanie gradientu

Gradienty analityczne (z propagacji wstecznej) mogą zawierać błędy. Numeryczne sprawdzanie gradientów weryfikuje je poprzez obliczenie gradientów o skończonych różnicach.

Wzór na różnicę wyśrodkowaną:

```
df/dx ~= (f(x + h) - f(x - h)) / (2h)
```

To jest dokładność O(h^2), znacznie lepsza niż różnica w przód `(f(x+h) - f(x)) / h`, która wynosi tylko O(h).

Wybór h: za duży i przybliżenie jest błędne. Zbyt małe i katastrofalne anulowanie niszczy odpowiedź. `h = 1e-5` do `1e-7` jest typowe.

Kontrola: obliczenie względnej różnicy pomiędzy gradientami analitycznymi i numerycznymi.

```
relative_error = |grad_analytical - grad_numerical| / max(|grad_analytical|, |grad_numerical|, 1e-8)
```

Praktyczne zasady:
- valid_error < 1e-7: idealnie, gradient jest prawidłowy
- error_relation < 1e-5: akceptowalny, prawdopodobnie poprawny
- valid_error > 1e-3: coś jest nie tak
- error_error > 1: gradient jest całkowicie błędny

Zawsze sprawdzaj gradienty podczas wdrażania nowej warstwy lub funkcji utraty. PyTorch zapewnia do tego `torch.autograd.gradcheck()`.

### Mieszany trening precyzyjny

Nowoczesne procesory graficzne mają wyspecjalizowany sprzęt (rdzenie Tensor), które obliczają mnożenia macierzy float16 2–8 razy szybciej niż float32. Trening o mieszanej precyzji wykorzystuje to:

```
1. Maintain float32 master copy of weights
2. Forward pass in float16 (fast)
3. Compute loss in float32 (prevents overflow)
4. Backward pass in float16 (fast)
5. Scale gradients to float32
6. Update float32 master weights
```

Problem z czystym treningiem float16: gradienty są często bardzo małe (1e-8 lub mniejsze). Float16 przekracza wszystko poniżej ~ 6e-8 do zera. Twój model przestaje się uczyć, ponieważ wszystkie aktualizacje gradientów mają wartość zerową.

Poprawka polega na skalowaniu strat:

```
1. Multiply loss by a large scale factor (e.g., 1024)
2. Backward pass computes gradients of (loss * 1024)
3. All gradients are 1024x larger (pushed above float16 underflow)
4. Divide gradients by 1024 before updating weights
5. Net effect: same update, but no underflow
```

Dynamiczne skalowanie strat automatycznie dostosowuje współczynnik skali. Zacznij od dużej wartości (65536). Jeśli gradienty przechodzą do `inf`, zmniejsz je o połowę. Jeśli N kroków przejdzie bez przepełnienia, podwoj go.

### bfloat16 vs float16: Dlaczego bfloat16 wygrywa na treningu

```
float16:   [1 sign] [5 exponent]  [10 mantissa]
bfloat16:  [1 sign] [8 exponent]  [7 mantissa]
```

float16 ma większą precyzję (10 bitów mantysy w porównaniu z 7), ale ograniczony zasięg (maks. ~ 65 504). bfloat16 ma mniejszą precyzję, ale ten sam zakres co float32 (maks. ~3,4e38).

Do uczenia sieci neuronowych:

- Aktywacje i logity regularnie przekraczają 65 504 podczas skoków treningowych. przepełnienia float16; bfloat16 sobie z tym radzi.
- Skalowanie strat jest wymagane w przypadku float16, ale zwykle jest niepotrzebne w przypadku bfloat16, ponieważ jego zakres obejmuje widmo wielkości gradientu.
- bfloat16 jest prostym skróceniem float32: upuść 16 dolnych bitów mantysy. Konwersja jest trywialna i bezstratna w wykładniku.

float16 jest preferowany do wnioskowania, gdy wartości są ograniczone, a precyzja ma większe znaczenie. bfloat16 jest preferowany do treningów, gdzie zasięg ma większe znaczenie. Właśnie dlatego TPU i nowoczesne procesory graficzne NVIDIA (A100, H100) mają natywną obsługę bfloat16.

### Przycinanie gradientu

Eksplodujące gradienty mają miejsce, gdy gradienty rosną wykładniczo w wielu warstwach (powszechne w RNN, głębokich sieciach i transformatorach). Pojedynczy duży gradient może zepsuć wszystkie wagi w jednym kroku.

Dwa rodzaje przycinania:

**Przytnij według wartości:** zaciskaj niezależnie każdy element gradientu.

```
grad = clamp(grad, -max_val, max_val)
```

Proste, ale może zmienić kierunek wektora gradientu.

**Przytnij według normy:** skaluj cały wektor gradientu tak, aby jego norma nie przekraczała progu.

```
if ||grad|| > max_norm:
    grad = grad * (max_norm / ||grad||)
```

Zachowuje kierunek gradientu. To właśnie robi `torch.nn.utils.clip_grad_norm_()`. Jest to standardowy wybór.

Typowe wartości: `max_norm=1.0` dla transformatorów, `max_norm=0.5` dla RL, `max_norm=5.0` dla prostszych sieci.

Przycinanie gradientu nie jest hackiem. Jest to mechanizm zabezpieczający. Bez tego pojedyncza partia odstająca może wytworzyć gradient wystarczająco duży, aby zrujnować tygodnie treningu.

### Warstwy normalizacyjne jako stabilizatory numeryczne

Normalizacja wsadowa, normalizacja warstw i normalizacja RMS są zwykle przedstawiane jako regularyzatory, które pomagają w zbieżności uczenia się. Są także stabilizatorami numerycznymi.

Bez normalizacji aktywacje mogą rosnąć lub kurczyć się wykładniczo w warstwach:

```
Layer 1: values in [0, 1]
Layer 5: values in [0, 100]
Layer 10: values in [0, 10,000]
Layer 50: values in [0, inf]
```

Normalizacja wyśrodkowuje i przeskalowuje aktywacje w każdej warstwie:

```
LayerNorm(x) = (x - mean(x)) / (std(x) + epsilon) * gamma + beta
```

`epsilon` (zwykle 1e-5) zapobiega dzieleniu przez zero, gdy wszystkie aktywacje są identyczne. Wyuczone parametry `gamma` i `beta` pozwalają sieci przywrócić potrzebną skalę.

Dzięki temu wartości w całej sieci mieszczą się w bezpiecznym numerycznie zakresie, zapobiegając zarówno przepełnieniu przy przepływie do przodu, jak i eksplozji gradientu przy przepływie wstecz.

### Typowe błędy numeryczne ML

**Błąd: Strata wynosi NaN po kilku epokach.**
Przyczyna: logity stały się zbyt duże, softmax się przepełnił. Lub tempo uczenia się jest zbyt wysokie i wagi są rozbieżne.
Poprawka: użyj stabilnego softmax (maksymalne odejmowanie), zmniejsz szybkość uczenia się, dodaj obcinanie gradientu.

**Błąd: Strata utknęła w log(num_classes).**
Przyczyna: wyniki modelu mają prawie jednolite prawdopodobieństwo. Często oznacza to, że gradienty zanikają lub model w ogóle się nie uczy.
Poprawka: sprawdź, czy etykiety danych są poprawne, sprawdź funkcję utraty, sprawdź, czy nie ma martwych ReLU.

**Błąd: Dokładność walidacji jest niższa od oczekiwanej o 1-3%.**
Przyczyna: mieszana precyzja bez odpowiedniego skalowania strat. Niedomiar gradientu po cichu zeruje małe aktualizacje.
Poprawka: włącz dynamiczne skalowanie strat lub przejdź na bfloat16.

**Błąd: dla niektórych warstw normy gradientu wynoszą 0,0.**
Przyczyna: martwe neurony ReLU (wszystkie wejścia ujemne) lub niedomiar float16.
Poprawka: użyj LeakyReLU lub GELU, użyj skalowania gradientu, sprawdź inicjalizację wagi.

**Błąd: Model działa na jednym GPU, ale daje inne wyniki na innym.**
Przyczyna: niedeterministyczny porządek akumulacji zmiennoprzecinkowej. Redukcje równoległe GPU sumują się w różnej kolejności na różnych urządzeniach, a dodawanie zmiennoprzecinkowe nie jest asocjacyjne.
Poprawka: zaakceptuj małe różnice (1e-6) lub ustaw `torch.use_deterministic_algorithms(True)` i zaakceptuj karę za prędkość.

**Błąd: `exp()` zwraca `inf` przy obliczaniu strat.**
Przyczyna: surowe logity przekazane do `exp()` bez sztuczki z odjęciem maksymalnego.
Poprawka: użyj `torch.nn.functional.log_softmax()`, który wewnętrznie implementuje log-sum-exp.

**Błąd: Trening różni się po zmianie z float32 na float16.**
Przyczyna: float16 nie może reprezentować wielkości gradientu poniżej 6e-8 ani aktywacji powyżej 65 504.
Poprawka: użyj mieszanej precyzji ze skalowaniem strat (AMP) lub zamiast tego użyj bfloat16.

## Zbuduj to

### Krok 1: Zademonstruj granice precyzji zmiennoprzecinkowej

```python
print("=== Floating Point Precision ===")
print(f"0.1 + 0.2 = {0.1 + 0.2}")
print(f"0.1 + 0.2 == 0.3? {0.1 + 0.2 == 0.3}")
print(f"Difference: {(0.1 + 0.2) - 0.3:.2e}")
```

### Krok 2: Zaimplementuj naiwny lub stabilny softmax

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

### Krok 3: Zaimplementuj stabilną wartość log-sum-exp

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

### Krok 4: Zaimplementuj stabilną entropię krzyżową

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

### Krok 5: Sprawdzanie gradientu

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

### Przycinanie gradientu

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

Zobacz `code/numerical.py`, aby zapoznać się z kompletnymi implementacjami z zademonstrowanymi wszystkimi przypadkami brzegowymi.

## Wyślij to

Ta lekcja daje:
- `code/numerical.py` ze stabilnym softmax, log-sum-exp, entropią krzyżową, sprawdzaniem gradientu i symulacją mieszanej precyzji
- `outputs/prompt-numerical-debugger.md` do diagnozowania NaN/Inf i problemów numerycznych podczas szkolenia

Te stabilne wdrożenia pojawiają się ponownie w fazie 3, kiedy budujemy pętlę treningową, oraz w fazie 4, kiedy wdrażamy mechanizmy uwagi.

## Ćwiczenia

1. **Katastrofalne anulowanie.** Oblicz wariancję [1000000.0, 1000001.0, 1000002.0] przy użyciu naiwnego wzoru `E[x^2] - E[x]^2` w float32. Następnie oblicz to za pomocą algorytmu online Welforda. Porównaj błędy z prawdziwą wariancją (0,6667).

2. **Wyszukiwanie precyzyjne.** Znajdź najmniejszą dodatnią wartość float32 `x` taką, że `1.0 + x == 1.0` w Pythonie. To jest maszyna epsilon. Sprawdź, czy pasuje do `numpy.finfo(numpy.float32).eps`.

3. **Przypadki graniczne log-sum-exp.** Przetestuj swoją funkcję `logsumexp_stable` za pomocą: (a) wszystkich wartości równych, (b) jednej wartości znacznie większej od pozostałych, (c) wszystkich wartości bardzo ujemnych (-1000). Sprawdź, czy daje poprawne wyniki, gdy wersja naiwna zawodzi.

4. **Sprawdzanie gradientu warstwy sieci neuronowej.** Zaimplementuj pojedynczą warstwę liniową `y = Wx + b` i jej analityczne przejście wstecz. Użyj `numerical_gradient`, aby sprawdzić poprawność macierzy wag 3x2.

5. **Eksperyment ze skalowaniem strat.** Symuluj trening za pomocą float16: utwórz losowe gradienty w zakresie [1e-9, 1e-3], przekonwertuj na float16 i zmierz, jaki ułamek stał się zerem. Następnie zastosuj skalowanie strat (pomnóż przez 1024), przekonwertuj na float16, zmniejsz skalę i ponownie zmierz ułamek zerowy.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|----------------------|
| IEEE 754 | „Standard pływakowy” | Międzynarodowy standard definiujący binarne formaty zmiennoprzecinkowe, zasady zaokrąglania i wartości specjalne (inf, nan). Implementuje go każdy nowoczesny procesor i procesor graficzny. |
| Maszyna epsilon | „Granica precyzji” | Najmniejsza wartość e taka, że ​​1,0 + e != 1,0 w danym formacie zmiennoprzecinkowym. Dla float32 jest to około 1,19e-7. |
| Katastrofalne anulowanie | „Utrata precyzji przy odejmowaniu” | Podczas odejmowania prawie równych liczb zmiennoprzecinkowych, cyfry znaczące znoszą się, a w wyniku dominuje szum zaokrągleń. |
| Przepełnienie | „Liczba za duża” | Wynik przekracza maksymalną możliwą do przedstawienia wartość i staje się inf. exp(89) przepełnia float32. |
| Niedomiar | „Liczba za mała” | Wynik jest bliższy zeru niż najmniejsza możliwa do przedstawienia liczba dodatnia i przyjmuje wartość 0,0. exp(-104) przekracza wartość float32. |
| Sztuczka z sumą logarytmiczną | „Najpierw odejmij maksimum” | Obliczanie log(sum(exp(x))) poprzez rozłożenie na czynniki exp(max(x)), aby zapobiec przepełnieniu i niedopełnieniu. Używany w matematyce softmax, entropii krzyżowej i logarytmicznym prawdopodobieństwie. |
| Stabilny softmax | „Softmax, który nie eksploduje” | Odejmowanie max(logitów) przed potęgowaniem. Numerycznie identyczny wynik, brak możliwości przepełnienia. |
| Sprawdzanie gradientu | „Zweryfikuj swoje wsparcie” | Porównywanie gradientów analitycznych z propagacji wstecznej z gradientami numerycznymi z różnic skończonych w celu wykrycia błędów implementacyjnych. |
| Mieszana precyzja | „Float16 do przodu, float32 do tyłu” | Używanie pływaków o niższej precyzji do operacji, w których prędkość jest krytyczna, i pływaków o wyższej precyzji do operacji wrażliwych numerycznie. Typowe przyspieszenie wynosi 2-3x. |
| Skalowanie strat | „Zapobiegaj niedopełnieniu gradientu” | Mnożenie straty przez dużą stałą przed podparciem, tak aby gradienty pozostały w możliwym do przedstawienia zakresie float16, a następnie dzielenie przez tę samą stałą przed aktualizacją wagi. |
| bfloat16 | „zmiennoprzecinkowy mózg” | 16-bitowy format Google z 8 bitami wykładnika (ten sam zakres co float32) i 7 bitami mantysy (mniejsza precyzja niż float16). Preferowany na treningi. |
| Przycinanie gradientu | „Ogranicz normę gradientu” | Skalowanie wektora gradientu tak, aby jego norma nie przekraczała progu. Zapobiega eksplodującym gradientom i niszczeniu ciężarów. |
| NaN | „To nie jest liczba” | Specjalna wartość zmiennoprzecinkowa z niezdefiniowanych operacji (0/0, inf-inf, sqrt(-1)). Propaguje przez całą następną arytmetykę. |
| Informacje | „Nieskończoność” | Specjalna wartość zmiennoprzecinkowa wynikająca z przepełnienia lub dzielenia przez zero. Można łączyć, aby wytworzyć NaN (inf - inf, inf * 0). |
| Gradient numeryczny | „Pochodna brutalnej siły” | Przybliżanie pochodnej poprzez obliczenie f(x+h) i f(x-h) i podzielenie przez 2h. Powolny, ale niezawodny do weryfikacji. |

## Dalsze czytanie

– [Co każdy informatyk powinien wiedzieć o arytmetyce zmiennoprzecinkowej (Goldberg 1991)](https://docs.oracle.com/cd/E19957-01/806-3568/ncg_goldberg.html) – ostateczne źródło informacji, gęste, ale kompletne
– [Mixed Precision Training (Micikevicius et al., 2018)](https://arxiv.org/abs/1710.03740) – artykuł firmy NVIDIA przedstawiający skalowanie strat w treningu float16
- [AMP: Automatyczna precyzja mieszana (dokumentacja PyTorch)](https://pytorch.org/docs/stable/amp.html) -- praktyczny przewodnik po precyzji mieszanej w PyTorch
– [format bfloat16 (dokumentacja Google Cloud TPU)](https://cloud.google.com/tpu/docs/bfloat16) – dlaczego Google wybrało ten format dla TPU
- [Sumowanie Kahana (Wikipedia)](https://en.wikipedia.org/wiki/Kahan_summation_algorithm) -- algorytm zmniejszający błąd zaokrąglania sum zmiennoprzecinkowych