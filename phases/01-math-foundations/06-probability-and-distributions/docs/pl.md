# Prawdopodobieństwo i rozkłady

> Prawdopodobieństwo to język, którego sztuczna inteligencja używa do wyrażania niepewności.

**Typ:** Ucz się
**Język:** Python
**Wymagania wstępne:** Faza 1, lekcje 01-04
**Czas:** ~75 minut

## Cele nauczania

- Implementuj od podstaw pliki PMF i PDF dla rozkładów Bernoulliego, kategorycznych, Poissona, jednolitych i normalnych
- Oblicz wartość oczekiwaną, wariancję i użyj centralnego twierdzenia granicznego, aby wyjaśnić, dlaczego dominują Gaussa
- Twórz funkcje softmax i log-softmax za pomocą sztuczki ze stabilnością numeryczną (odejmij max logit)
- Oblicz stratę entropii krzyżowej na podstawie logitów i połącz ją z ujemnym logarytmem wiarygodności

## Problem

Klasyfikator generuje wynik `[0.03, 0.91, 0.06]`. Model językowy wybiera następne słowo spośród 50 000 kandydatów. Model dyfuzji generuje obrazy poprzez próbkowanie z wyuczonych rozkładów. Wszystko to jest prawdopodobieństwo w działaniu.

Każda prognoza dokonywana przez model jest rozkładem prawdopodobieństwa. Każda funkcja straty mierzy, jak daleko przewidywany rozkład jest od prawdziwego. Każdy etap uczenia dostosowuje parametry, aby jedna dystrybucja bardziej przypominała inną. Bez prawdopodobieństwa nie można przeczytać pojedynczego artykułu dotyczącego uczenia maszynowego, debugować pojedynczego modelu ani zrozumieć, dlaczego strata szkoleniowa wynosi NaN.

## Koncepcja

### Zdarzenia, przestrzenie próbek i prawdopodobieństwo

Przestrzeń próbek S jest zbiorem wszystkich możliwych wyników. Zdarzenie jest podzbiorem przestrzeni próbki. Prawdopodobieństwo przypisuje zdarzenia do liczb z zakresu od 0 do 1.

```
Coin flip:
  S = {H, T}
  P(H) = 0.5,  P(T) = 0.5

Single die roll:
  S = {1, 2, 3, 4, 5, 6}
  P(even) = P({2, 4, 6}) = 3/6 = 0.5
```

Trzy aksjomaty definiują całe prawdopodobieństwo:
1. P(A) >= 0 dla dowolnego zdarzenia A
2. P(S) = 1 (zawsze coś się dzieje)
3. P(A lub B) = P(A) + P(B), gdy A i B nie mogą wystąpić jednocześnie

Wszystko inne (twierdzenie Bayesa, oczekiwania, rozkłady) wynika z tych trzech zasad.

### Prawdopodobieństwo warunkowe i niezależność

P(A|B) to prawdopodobieństwo zdarzenia A, przy założeniu, że wydarzyło się B.

```
P(A|B) = P(A and B) / P(B)

Example: deck of cards
  P(King | Face card) = P(King and Face card) / P(Face card)
                      = (4/52) / (12/52)
                      = 4/12 = 1/3
```

Dwa zdarzenia są niezależne, jeśli wiedza o jednym nie mówi nic o drugim:

```
Independent:   P(A|B) = P(A)
Equivalent to: P(A and B) = P(A) * P(B)
```

Rzuty monetą są niezależne. Karty do rysowania bez wymiany nie są.

### Funkcje masy prawdopodobieństwa a funkcje gęstości prawdopodobieństwa

Dyskretne zmienne losowe mają funkcję masy prawdopodobieństwa (PMF). Każdy wynik ma określone prawdopodobieństwo, które można bezpośrednio odczytać.

```
PMF: P(X = k)

Fair die:
  P(X = 1) = 1/6
  P(X = 2) = 1/6
  ...
  P(X = 6) = 1/6

  Sum of all probabilities = 1
```

Ciągłe zmienne losowe mają funkcję gęstości prawdopodobieństwa (PDF). Gęstość w jednym punkcie nie jest prawdopodobieństwem. Prawdopodobieństwo wynika z całkowania gęstości w przedziale.

```
PDF: f(x)

P(a <= X <= b) = integral of f(x) from a to b

f(x) can be greater than 1 (density, not probability)
integral from -inf to +inf of f(x) dx = 1
```

To rozróżnienie ma znaczenie w ML. Wynikiem klasyfikacji są PMF (wybory dyskretne). Ukryte przestrzenie VAE wykorzystują pliki PDF (ciągłe).

### Wspólne dystrybucje

**Bernoulli:** jedno badanie, dwa wyniki. Modele klasyfikacji binarnej.

```
P(X = 1) = p
P(X = 0) = 1 - p
Mean = p,  Variance = p(1-p)
```

**Kategoryczne:** jedno badanie, k wyników. Modele klasyfikacji wieloklasowej (wyjście softmax).

```
P(X = i) = p_i,  where sum of p_i = 1
Example: P(cat) = 0.7,  P(dog) = 0.2,  P(bird) = 0.1
```

**Jednolity:** wszystkie wyniki są jednakowo prawdopodobne. Używany do losowej inicjalizacji.

```
Discrete: P(X = k) = 1/n for k in {1, ..., n}
Continuous: f(x) = 1/(b-a) for x in [a, b]
```

**Normalna (Gaussa):** krzywa dzwonowa. Sparametryzowany za pomocą średniej (mu) i wariancji (sigma^2).

```
f(x) = (1 / sqrt(2*pi*sigma^2)) * exp(-(x - mu)^2 / (2*sigma^2))

Standard normal: mu = 0, sigma = 1
  68% of data within 1 sigma
  95% within 2 sigma
  99.7% within 3 sigma
```

**Poisson:** liczba rzadkich zdarzeń w ustalonych odstępach czasu. Modeluje wskaźniki zdarzeń.

```
P(X = k) = (lambda^k * e^(-lambda)) / k!
Mean = lambda,  Variance = lambda
```

### Oczekiwana wartość i wariancja

Wartość oczekiwana to średni ważony wynik.

```
Discrete:   E[X] = sum of x_i * P(X = x_i)
Continuous: E[X] = integral of x * f(x) dx
```

Miary wariancji rozłożone są wokół średniej.

```
Var(X) = E[(X - E[X])^2] = E[X^2] - (E[X])^2
Standard deviation = sqrt(Var(X))
```

W ML wartość oczekiwana pojawia się jako funkcja straty (średnia strata w rozkładzie danych). Wariancja mówi o stabilności modelu. Duża zmienność nachyleń oznacza hałaśliwy trening.

### Podziały łączne i krańcowe

Rozkład łączny P(X, Y) opisuje łącznie dwie zmienne losowe.

Wspólny przykład PMF (X = pogoda, Y = parasol):

| | Y=0 (bez parasola) | Y=1 (parasol) | Marginalny P(X) |
|---|---|---|---|
| X=0 (słońce) | 0,40 | 0,10 | P(X=0) = 0,50 |
| X=1 (deszcz) | 0,05 | 0,45 | P(X=1) = 0,50 |
| **Marginalny P(Y)** | P(Y=0) = 0,45 | P(Y=1) = 0,55 | 1,00 |

Rozkład krańcowy sumuje drugą zmienną:

```
P(X = x) = sum over all y of P(X = x, Y = y)
```

Sumy wierszy i kolumn w powyższej tabeli są marginesami.

### Dlaczego rozkład normalny pojawia się wszędzie

Centralne twierdzenie graniczne: suma (lub średnia) wielu niezależnych zmiennych losowych zbiega się do rozkładu normalnego, niezależnie od rozkładu pierwotnego.

```
Roll 1 die:  uniform distribution (flat)
Average of 2 dice:  triangular (peaked)
Average of 30 dice: nearly perfect bell curve

This works for ANY starting distribution.
```

Oto dlaczego:
- Błędy pomiarowe są w przybliżeniu normalne (wiele małych, niezależnych źródeł)
- Inicjalizacja wag w sieciach neuronowych wykorzystuje rozkłady normalne
- Szum gradientowy w SGD jest w przybliżeniu normalny (suma wielu gradientów próbek)
- Rozkład normalny to maksymalny rozkład entropii dla danej średniej i wariancji

### Zapisz prawdopodobieństwa

Surowe prawdopodobieństwa powodują problemy numeryczne. Mnożenie razem wielu małych prawdopodobieństw szybko prowadzi do zera.

```
P(sentence) = P(word1) * P(word2) * ... * P(word_n)
            = 0.01 * 0.003 * 0.02 * ...
            -> 0.0 (underflow after ~30 terms)
```

Prawdopodobieństwa dziennika naprawiają to. Mnożenia stają się dodawaniami.

```
log P(sentence) = log P(word1) + log P(word2) + ... + log P(word_n)
                = -4.6 + -5.8 + -3.9 + ...
                -> finite number (no underflow)
```

Zasady:
- log(a * b) = log(a) + log(b)
- prawdopodobieństwa logarytmiczne są zawsze <= 0 (ponieważ 0 < P <= 1)
- Bardziej negatywne = mniej prawdopodobne
- Strata entropii krzyżowej to ujemny logarytm prawdopodobieństwa właściwej klasy

### Softmax jako rozkład prawdopodobieństwa

Sieci neuronowe generują surowe wyniki (logity). Softmax przekształca je w prawidłowy rozkład prawdopodobieństwa.

```
softmax(z_i) = exp(z_i) / sum(exp(z_j) for all j)

Properties:
  - All outputs are in (0, 1)
  - All outputs sum to 1
  - Preserves relative ordering of inputs
  - exp() amplifies differences between logits
```

Sztuczka softmax: odejmij maksymalny logit przed potęgowaniem, aby zapobiec przepełnieniu.

```
z = [100, 101, 102]
exp(102) = overflow

z_shifted = z - max(z) = [-2, -1, 0]
exp(0) = 1  (safe)

Same result, no overflow.
```

Log-softmax łączy softmax i log w celu zapewnienia stabilności numerycznej. PyTorch używa tego wewnętrznie do utraty entropii krzyżowej.

### Próbkowanie

Próbkowanie oznacza losowanie wartości z rozkładu. W ML:
- Rezygnacja losowo pobiera próbki, które neurony należy wyzerować
- Zwiększanie danych próbek losowych przekształceń
- Modele językowe próbkują następny token z przewidywanej dystrybucji
- Modele dyfuzyjne próbkują szum i stopniowo go odszumiają

Próbkowanie z dowolnych rozkładów wymaga technik takich jak próbkowanie z odwrotną transformacją, próbkowanie przez odrzucenie lub sztuczka reparametryzacyjna (stosowana w VAE).

## Zbuduj to

### Krok 1: Podstawy prawdopodobieństwa

```python
import math
import random

def factorial(n):
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

def combinations(n, k):
    return factorial(n) // (factorial(k) * factorial(n - k))

def conditional_probability(p_a_and_b, p_b):
    return p_a_and_b / p_b

p_king_given_face = conditional_probability(4/52, 12/52)
print(f"P(King | Face card) = {p_king_given_face:.4f}")
```

### Krok 2: PMF i PDF od zera

```python
def bernoulli_pmf(k, p):
    return p if k == 1 else (1 - p)

def categorical_pmf(k, probs):
    return probs[k]

def poisson_pmf(k, lam):
    return (lam ** k) * math.exp(-lam) / factorial(k)

def uniform_pdf(x, a, b):
    if a <= x <= b:
        return 1.0 / (b - a)
    return 0.0

def normal_pdf(x, mu, sigma):
    coeff = 1.0 / (sigma * math.sqrt(2 * math.pi))
    exponent = -0.5 * ((x - mu) / sigma) ** 2
    return coeff * math.exp(exponent)
```

### Krok 3: Wartość oczekiwana i wariancja

```python
def expected_value(values, probabilities):
    return sum(v * p for v, p in zip(values, probabilities))

def variance(values, probabilities):
    mu = expected_value(values, probabilities)
    return sum(p * (v - mu) ** 2 for v, p in zip(values, probabilities))

die_values = [1, 2, 3, 4, 5, 6]
die_probs = [1/6] * 6
mu = expected_value(die_values, die_probs)
var = variance(die_values, die_probs)
print(f"Die: E[X] = {mu:.4f}, Var(X) = {var:.4f}, SD = {var**0.5:.4f}")
```

### Krok 4: Próbkowanie z rozkładów

```python
def sample_bernoulli(p, n=1):
    return [1 if random.random() < p else 0 for _ in range(n)]

def sample_categorical(probs, n=1):
    cumulative = []
    total = 0
    for p in probs:
        total += p
        cumulative.append(total)
    samples = []
    for _ in range(n):
        r = random.random()
        for i, c in enumerate(cumulative):
            if r <= c:
                samples.append(i)
                break
    return samples

def sample_normal_box_muller(mu, sigma, n=1):
    samples = []
    for _ in range(n):
        u1 = random.random()
        u2 = random.random()
        z = math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)
        samples.append(mu + sigma * z)
    return samples
```

### Krok 5: Softmax i log prawdopodobieństwa

```python
def softmax(logits):
    max_logit = max(logits)
    shifted = [z - max_logit for z in logits]
    exps = [math.exp(z) for z in shifted]
    total = sum(exps)
    return [e / total for e in exps]

def log_softmax(logits):
    max_logit = max(logits)
    shifted = [z - max_logit for z in logits]
    log_sum_exp = max_logit + math.log(sum(math.exp(z) for z in shifted))
    return [z - log_sum_exp for z in logits]

def cross_entropy_loss(logits, target_index):
    log_probs = log_softmax(logits)
    return -log_probs[target_index]
```

### Krok 6: Demonstracja centralnego twierdzenia granicznego

```python
def demonstrate_clt(dist_fn, n_samples, n_averages):
    averages = []
    for _ in range(n_averages):
        samples = [dist_fn() for _ in range(n_samples)]
        averages.append(sum(samples) / len(samples))
    return averages
```

### Krok 7: Wizualizacja

```python
import matplotlib.pyplot as plt

xs = [mu + sigma * (i - 500) / 100 for i in range(1001)]
ys = [normal_pdf(x, mu, sigma) for x, mu, sigma in ...]
plt.plot(xs, ys)
```

Pełne wdrożenia wraz ze wszystkimi wizualizacjami znajdują się w `code/probability.py`.

## Użyj tego

W przypadku NumPy i SciPy wszystko powyżej jest jednowierszowe:

```python
import numpy as np
from scipy import stats

normal = stats.norm(loc=0, scale=1)
samples = normal.rvs(size=10000)
print(f"Mean: {np.mean(samples):.4f}, Std: {np.std(samples):.4f}")
print(f"P(X < 1.96) = {normal.cdf(1.96):.4f}")

logits = np.array([2.0, 1.0, 0.1])
from scipy.special import softmax, log_softmax
probs = softmax(logits)
log_probs = log_softmax(logits)
print(f"Softmax: {probs}")
print(f"Log-softmax: {log_probs}")
```

Zbudowałeś je od zera. Teraz już wiesz, co robią wezwania do biblioteki.

## Ćwiczenia

1. Zaimplementuj próbkowanie z odwrotną transformacją dla rozkładu wykładniczego. Sprawdź, próbkując 10 000 wartości i porównując histogram z prawdziwym plikiem PDF.

2. Zbuduj wspólną tabelę rozkładu dla dwóch załadowanych kości. Oblicz rozkłady krańcowe i sprawdź, czy kostki są niezależne.

3. Oblicz stratę entropii krzyżowej dla klasyfikatora 5-klasowego, który generuje logity `[2.0, 0.5, -1.0, 3.0, 0.1]`, gdy poprawną klasą jest indeks 3. Następnie zweryfikuj swoją odpowiedź za pomocą `nn.CrossEntropyLoss` PyTorcha.

4. Napisz funkcję, która pobiera listę logarytmów prawdopodobieństw i zwraca najbardziej prawdopodobną sekwencję, całkowite prawdopodobieństwo logarytmiczne i równoważne prawdopodobieństwo surowe. Przetestuj to za pomocą zdania składającego się z 50 słów, gdzie każde słowo ma prawdopodobieństwo 0,01.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|----------------------|
| Przykładowa przestrzeń | „Wszystkie możliwości” | Zbiór S każdego możliwego wyniku eksperymentu |
| PMF | „Funkcja prawdopodobieństwa” | Funkcja określająca dokładne prawdopodobieństwo każdego dyskretnego wyniku, sumując do 1 |
| PDF | „Krzywa prawdopodobieństwa” | Funkcja gęstości dla zmiennych ciągłych. Całkuj po przedziale, aby uzyskać prawdopodobieństwo |
| Prawdopodobieństwo warunkowe | „Prawdopodobieństwo przy danym czymś” | P(A\|B) = P(A i B) / P(B). Podstawy myślenia bayesowskiego i twierdzenie Bayesa |
| Niepodległość | „Nie wpływają na siebie” | P(A i B) = P(A) * P(B). Znajomość jednego wydarzenia nic nie mówi o drugim |
| Oczekiwana wartość | „Średnia” | Suma wszystkich wyników ważona prawdopodobieństwem. Funkcja straty jest wartością oczekiwaną |
| Wariancja | „Jak rozproszeni” | Oczekiwane kwadratowe odchylenie od średniej. Wysoka wariancja = zaszumione, niestabilne szacunki |
| Rozkład normalny | „Krzywa dzwonowa” | f(x) = (1/sqrt(2*pi*sigma^2)) * exp(-(x-mu)^2/(2*sigma^2)). Pojawia się wszędzie dzięki CLT |
| Centralne twierdzenie graniczne | „Średnie stają się normalne” | Średnia wielu niezależnych próbek zbiega się do rozkładu normalnego niezależnie od źródła |
| Wspólna dystrybucja | „Dwie zmienne razem” | P(X, Y) opisuje prawdopodobieństwo każdej kombinacji wyników X i Y |
| Dystrybucja krańcowa | „Podsumuj drugą zmienną” | P(X) = suma_y P(X, Y). Odzyskuje rozkład jednej zmiennej ze złącza |
| Zaloguj prawdopodobieństwo | „Dziennik prawdopodobieństwa” | log P(x). Zamienia produkty w sumy, zapobiegając niedoborom liczbowym w długich sekwencjach |
| Softmax | „Zamień wyniki na prawdopodobieństwa” | softmax(z_i) = exp(z_i) / suma(exp(z_j)). Odwzorowuje logity o wartościach rzeczywistych na prawidłowy rozkład prawdopodobieństwa |
| Entropia krzyżowa | „Funkcja straty” | -sum(p_true * log(p_przewidywana)). Mierzy, jak różne są dwa rozkłady. Niżej jest lepiej |
| Logity | „Wyniki modelu surowego” | Nieznormalizowane wyniki przed softmax. Nazwany na cześć funkcji logistycznej |
| Próbkowanie | „Rysowanie wartości losowych” | Generowanie wartości na podstawie rozkładu prawdopodobieństwa. Jak modele generują dane wyjściowe |

## Dalsze czytanie

- [3Blue1Brown: Ale czym jest Centralne Twierdzenie Graniczne?](https://www.youtube.com/watch?v=zeJD6dqJ5lo) – wizualny dowód, dlaczego średnie stają się normalne
– [Stanford CS229 Probability Review](https://cs229.stanford.edu/section/cs229-prob.pdf) – zwięzłe odniesienie obejmujące wszystko tutaj i nie tylko
- [Sztuczka log-sum-exp/](https://gregorygundersen.com/blog/2020/02/09/log-sum-exp/) - dlaczego stabilność numeryczna ma znaczenie i jak ją osiągnąć