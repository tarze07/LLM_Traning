# Prawdopodobieństwo i rozkłady

> Prawdopodobieństwo to język, którym AI wyraża niepewność.

**Typ:** Nauka
**Język:** Python
**Wymagania wstępne:** Faza 1, Lekcje 01-04
**Czas:** ~75 minut

## Cele nauki

- Zaimplementuj od podstaw PMF i PDF dla rozkładów Bernoulliego, kategorycznego, Poissona, jednostajnego i normalnego
- Oblicz wartość oczekiwaną, wariancję i wykorzystaj centralne twierdzenie graniczne, by wyjaśnić, dlaczego rozkłady Gaussa dominują
- Zbuduj funkcje softmax i log-softmax z trikiem zapewniającym stabilność numeryczną (odejmowanie maksymalnego logitu)
- Oblicz stratę cross-entropy z logitów i powiąż ją z ujemnym logarytmem wiarygodności (negative log-likelihood)

## Problem

Klasyfikator zwraca `[0.03, 0.91, 0.06]`. Model językowy wybiera kolejne słowo spośród 50 000 kandydatów. Model dyfuzyjny generuje obrazy, próbkując z wyuczonych rozkładów. Wszystko to jest prawdopodobieństwem w działaniu.

Każda predykcja modelu jest rozkładem prawdopodobieństwa. Każda funkcja straty mierzy, jak bardzo przewidywany rozkład różni się od prawdziwego. Każdy krok treningu dostosowuje parametry tak, aby jeden rozkład bardziej przypominał drugi. Bez prawdopodobieństwa nie da się przeczytać ani jednego artykułu z dziedziny ML, zdebugować ani jednego modelu, ani zrozumieć, dlaczego strata treningowa wynosi NaN.

## Koncepcja

### Zdarzenia, przestrzenie zdarzeń elementarnych i prawdopodobieństwo

Przestrzeń zdarzeń elementarnych S to zbiór wszystkich możliwych wyników. Zdarzenie to podzbiór przestrzeni zdarzeń elementarnych. Prawdopodobieństwo przypisuje zdarzeniom liczby z przedziału od 0 do 1.

```
Rzut monetą:
  S = {H, T}
  P(H) = 0.5,  P(T) = 0.5

Rzut pojedynczą kostką:
  S = {1, 2, 3, 4, 5, 6}
  P(parzysta) = P({2, 4, 6}) = 3/6 = 0.5
```

Trzy aksjomaty definiują całą teorię prawdopodobieństwa:
1. P(A) >= 0 dla dowolnego zdarzenia A
2. P(S) = 1 (coś zawsze się zdarza)
3. P(A lub B) = P(A) + P(B), gdy A i B nie mogą wystąpić jednocześnie

Wszystko inne (twierdzenie Bayesa, wartości oczekiwane, rozkłady) wynika z tych trzech reguł.

### Prawdopodobieństwo warunkowe i niezależność

P(A|B) to prawdopodobieństwo zajścia A pod warunkiem, że zaszło B.

```
P(A|B) = P(A i B) / P(B)

Przykład: talia kart
  P(Król | Karta figurowa) = P(Król i Karta figurowa) / P(Karta figurowa)
                      = (4/52) / (12/52)
                      = 4/12 = 1/3
```

Dwa zdarzenia są niezależne, gdy znajomość jednego nic nie mówi o drugim:

```
Niezależność:   P(A|B) = P(A)
Równoważnie:    P(A i B) = P(A) * P(B)
```

Rzuty monetą są niezależne. Losowanie kart bez zwracania - nie.

### Funkcje masy prawdopodobieństwa (PMF) a funkcje gęstości prawdopodobieństwa (PDF)

Dyskretne zmienne losowe mają funkcję masy prawdopodobieństwa (PMF). Każdy wynik ma konkretne prawdopodobieństwo, które można odczytać bezpośrednio.

```
PMF: P(X = k)

Uczciwa kostka:
  P(X = 1) = 1/6
  P(X = 2) = 1/6
  ...
  P(X = 6) = 1/6

  Suma wszystkich prawdopodobieństw = 1
```

Ciągłe zmienne losowe mają funkcję gęstości prawdopodobieństwa (PDF). Gęstość w pojedynczym punkcie nie jest prawdopodobieństwem. Prawdopodobieństwo otrzymuje się, całkując gęstość po przedziale.

```
PDF: f(x)

P(a <= X <= b) = całka z f(x) od a do b

f(x) może być większe niż 1 (gęstość, nie prawdopodobieństwo)
całka od -inf do +inf z f(x) dx = 1
```

To rozróżnienie ma znaczenie w ML. Wyniki klasyfikacji to PMF (wybory dyskretne). Przestrzenie ukryte VAE wykorzystują PDF (ciągłe).

### Popularne rozkłady

**Bernoulliego:** jedna próba, dwa wyniki. Modeluje klasyfikację binarną.

```
P(X = 1) = p
P(X = 0) = 1 - p
Średnia = p,  Wariancja = p(1-p)
```

**Kategoryczny:** jedna próba, k wyników. Modeluje klasyfikację wieloklasową (wynik softmax).

```
P(X = i) = p_i,  gdzie suma p_i = 1
Przykład: P(kot) = 0.7,  P(pies) = 0.2,  P(ptak) = 0.1
```

**Jednostajny:** wszystkie wyniki jednakowo prawdopodobne. Wykorzystywany do losowej inicjalizacji.

```
Dyskretny: P(X = k) = 1/n dla k z {1, ..., n}
Ciągły: f(x) = 1/(b-a) dla x z [a, b]
```

**Normalny (Gaussa):** krzywa dzwonowa. Parametryzowany przez średnią (mu) i wariancję (sigma^2).

```
f(x) = (1 / sqrt(2*pi*sigma^2)) * exp(-(x - mu)^2 / (2*sigma^2))

Standardowy rozkład normalny: mu = 0, sigma = 1
  68% danych w przedziale 1 sigma
  95% w przedziale 2 sigma
  99.7% w przedziale 3 sigma
```

**Poissona:** liczba rzadkich zdarzeń w ustalonym przedziale. Modeluje tempo występowania zdarzeń.

```
P(X = k) = (lambda^k * e^(-lambda)) / k!
Średnia = lambda,  Wariancja = lambda
```

### Wartość oczekiwana i wariancja

Wartość oczekiwana to średnia ważona wynikami.

```
Dyskretna:  E[X] = suma x_i * P(X = x_i)
Ciągła:     E[X] = całka z x * f(x) dx
```

Wariancja mierzy rozrzut wokół średniej.

```
Var(X) = E[(X - E[X])^2] = E[X^2] - (E[X])^2
Odchylenie standardowe = sqrt(Var(X))
```

W ML wartość oczekiwana pojawia się jako funkcja straty (średnia strata po rozkładzie danych). Wariancja mówi o stabilności modelu. Wysoka wariancja gradientów oznacza zaszumiony trening.

### Rozkłady łączne i brzegowe

Rozkład łączny P(X, Y) opisuje dwie zmienne losowe razem.

Przykład łącznego PMF (X = pogoda, Y = parasol):

| | Y=0 (bez parasola) | Y=1 (parasol) | Brzegowy P(X) |
|---|---|---|---|
| X=0 (słońce) | 0.40 | 0.10 | P(X=0) = 0.50 |
| X=1 (deszcz) | 0.05 | 0.45 | P(X=1) = 0.50 |
| **Brzegowy P(Y)** | P(Y=0) = 0.45 | P(Y=1) = 0.55 | 1.00 |

Rozkład brzegowy sumuje po drugiej zmiennej:

```
P(X = x) = suma po wszystkich y z P(X = x, Y = y)
```

Sumy wierszy i kolumn w powyższej tabeli to rozkłady brzegowe.

### Dlaczego rozkład normalny pojawia się wszędzie

Centralne twierdzenie graniczne (CTG): suma (lub średnia) wielu niezależnych zmiennych losowych zbiega do rozkładu normalnego, niezależnie od rozkładu wyjściowego.

```
Rzut 1 kostką:  rozkład jednostajny (płaski)
Średnia z 2 kostek:  trójkątny (ze szczytem)
Średnia z 30 kostek: niemal idealna krzywa dzwonowa

Działa to dla DOWOLNEGO rozkładu początkowego.
```

Dlatego:
- Błędy pomiarowe są w przybliżeniu normalne (wiele małych, niezależnych źródeł)
- Inicjalizacje wag w sieciach neuronowych wykorzystują rozkłady normalne
- Szum gradientu w SGD jest w przybliżeniu normalny (suma wielu gradientów próbkowych)
- Rozkład normalny to rozkład o maksymalnej entropii dla danej średniej i wariancji

### Logarytmy prawdopodobieństw

Surowe prawdopodobieństwa powodują problemy numeryczne. Mnożenie wielu małych prawdopodobieństw szybko prowadzi do underflow do zera.

```
P(zdanie) = P(słowo1) * P(słowo2) * ... * P(słowo_n)
          = 0.01 * 0.003 * 0.02 * ...
          -> 0.0 (underflow po ~30 czynnikach)
```

Logarytmy prawdopodobieństw rozwiązują ten problem. Mnożenia stają się dodawaniami.

```
log P(zdanie) = log P(słowo1) + log P(słowo2) + ... + log P(słowo_n)
              = -4.6 + -5.8 + -3.9 + ...
              -> liczba skończona (brak underflow)
```

Reguły:
- log(a * b) = log(a) + log(b)
- logarytmy prawdopodobieństw są zawsze <= 0 (ponieważ 0 < P <= 1)
- Bardziej ujemna wartość = mniej prawdopodobne
- Strata cross-entropy to ujemny logarytm prawdopodobieństwa poprawnej klasy

### Softmax jako rozkład prawdopodobieństwa

Sieci neuronowe zwracają surowe wyniki (logity). Softmax przekształca je w prawidłowy rozkład prawdopodobieństwa.

```
softmax(z_i) = exp(z_i) / suma(exp(z_j) dla wszystkich j)

Właściwości:
  - Wszystkie wyniki należą do (0, 1)
  - Wszystkie wyniki sumują się do 1
  - Zachowuje względną kolejność wejść
  - exp() wzmacnia różnice między logitami
```

Trik softmax: odejmij maksymalny logit przed eksponencjacją, aby zapobiec przepełnieniu (overflow).

```
z = [100, 101, 102]
exp(102) = overflow

z_shifted = z - max(z) = [-2, -1, 0]
exp(0) = 1  (bezpieczne)

Ten sam wynik, brak overflow.
```

Log-softmax łączy softmax i logarytm dla stabilności numerycznej. PyTorch wykorzystuje to wewnętrznie do straty cross-entropy.

### Próbkowanie

Próbkowanie oznacza losowanie wartości z rozkładu. W ML:
- Dropout losowo próbkuje, które neurony wyzerować
- Augmentacja danych próbkuje losowe transformacje
- Modele językowe próbkują kolejny token z przewidywanego rozkładu
- Modele dyfuzyjne próbkują szum i stopniowo go usuwają

Próbkowanie z dowolnych rozkładów wymaga technik takich jak próbkowanie metodą odwrotnej dystrybuanty (inverse transform sampling), próbkowanie eliminacyjne (rejection sampling) lub trik reparametryzacji (wykorzystywany w VAE).

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

### Krok 2: PMF i PDF od podstaw

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

### Krok 5: Softmax i logarytmy prawdopodobieństw

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

Pełne implementacje ze wszystkimi wizualizacjami znajdują się w `code/probability.py`.

## Wykorzystaj to

Z NumPy i SciPy wszystko powyższe sprowadza się do jednolinijkowców:

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

Zbudowałeś to wszystko od podstaw. Teraz wiesz, co robią wywołania bibliotek.

## Ćwiczenia

1. Zaimplementuj próbkowanie metodą odwrotnej dystrybuanty (inverse transform sampling) dla rozkładu wykładniczego. Zweryfikuj, próbkując 10 000 wartości i porównując histogram z prawdziwym PDF.

2. Zbuduj tabelę rozkładu łącznego dla dwóch obciążonych kostek. Oblicz rozkłady brzegowe i sprawdź, czy kostki są niezależne.

3. Oblicz stratę cross-entropy dla 5-klasowego klasyfikatora, który zwraca logity `[2.0, 0.5, -1.0, 3.0, 0.1]`, gdy poprawną klasą jest indeks 3. Następnie zweryfikuj swój wynik za pomocą `nn.CrossEntropyLoss` z PyTorch.

4. Napisz funkcję, która przyjmuje listę logarytmów prawdopodobieństw i zwraca najbardziej prawdopodobną sekwencję, całkowity logarytm prawdopodobieństwa oraz odpowiadające mu surowe prawdopodobieństwo. Przetestuj ją na zdaniu złożonym z 50 słów, z których każde ma prawdopodobieństwo 0.01.

## Kluczowe pojęcia

| Termin | Co się potocznie mówi | Co to faktycznie znaczy |
|------|----------------|----------------------|
| Przestrzeń zdarzeń elementarnych | "Wszystkie możliwości" | Zbiór S wszystkich możliwych wyników eksperymentu |
| PMF | "Funkcja prawdopodobieństwa" | Funkcja podająca dokładne prawdopodobieństwo każdego dyskretnego wyniku, sumująca się do 1 |
| PDF | "Krzywa prawdopodobieństwa" | Funkcja gęstości dla zmiennych ciągłych. Aby uzyskać prawdopodobieństwo, należy ją scałkować po przedziale |
| Prawdopodobieństwo warunkowe | "Prawdopodobieństwo pod warunkiem czegoś" | P(A\|B) = P(A i B) / P(B). Podstawa myślenia bayesowskiego i twierdzenia Bayesa |
| Niezależność | "One na siebie nie wpływają" | P(A i B) = P(A) * P(B). Znajomość jednego zdarzenia nic nie mówi o drugim |
| Wartość oczekiwana | "Średnia" | Ważona prawdopodobieństwami suma wszystkich wyników. Funkcja straty jest wartością oczekiwaną |
| Wariancja | "Jak bardzo rozproszone" | Oczekiwane kwadratowe odchylenie od średniej. Wysoka wariancja = zaszumione, niestabilne estymaty |
| Rozkład normalny | "Krzywa dzwonowa" | f(x) = (1/sqrt(2*pi*sigma^2)) * exp(-(x-mu)^2/(2*sigma^2)). Pojawia się wszędzie dzięki CTG |
| Centralne twierdzenie graniczne | "Średnie stają się normalne" | Średnia z wielu niezależnych próbek zbiega do rozkładu normalnego niezależnie od źródła |
| Rozkład łączny | "Dwie zmienne razem" | P(X, Y) opisuje prawdopodobieństwo każdej kombinacji wyników X i Y |
| Rozkład brzegowy | "Wysumuj drugą zmienną" | P(X) = suma_y P(X, Y). Odzyskuje rozkład jednej zmiennej z rozkładu łącznego |
| Logarytm prawdopodobieństwa | "Logarytm z prawdopodobieństwa" | log P(x). Zamienia iloczyny na sumy, zapobiegając numerycznemu underflow w długich sekwencjach |
| Softmax | "Zamień wyniki na prawdopodobieństwa" | softmax(z_i) = exp(z_i) / suma(exp(z_j)). Przekształca rzeczywiste logity w prawidłowy rozkład prawdopodobieństwa |
| Cross-entropy | "Funkcja straty" | -suma(p_true * log(p_predicted)). Mierzy, jak bardzo różnią się dwa rozkłady. Mniej znaczy lepiej |
| Logity | "Surowe wyjścia modelu" | Nieznormalizowane wyniki przed softmax. Nazwa pochodzi od funkcji logistycznej |
| Próbkowanie | "Losowanie wartości" | Generowanie wartości zgodnie z rozkładem prawdopodobieństwa. Tak modele generują wyniki |

## Dalsza lektura

- [3Blue1Brown: But what is the Central Limit Theorem?](https://www.youtube.com/watch?v=zeJD6dqJ5lo) - wizualny dowód, dlaczego średnie stają się normalne
- [Stanford CS229 Probability Review](https://cs229.stanford.edu/section/cs229-prob.pdf) - zwięzłe opracowanie obejmujące to wszystko i więcej
- [The Log-Sum-Exp Trick](https://gregorygundersen.com/blog/2020/02/09/log-sum-exp/) - dlaczego stabilność numeryczna ma znaczenie i jak ją osiągnąć
