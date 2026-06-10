# Metody pobierania próbek

> Próbkowanie to sposób, w jaki sztuczna inteligencja bada przestrzeń możliwości.

**Typ:** Kompilacja
**Język:** Python
**Wymagania wstępne:** Faza 1, lekcje 06-07 (Prawdopodobieństwo, Twierdzenie Bayesa)
**Czas:** ~120 minut

## Cele nauczania

- Zaimplementuj od zera odwrotny CDF, odrzucanie i próbkowanie ważności, używając tylko jednolitych liczb losowych
- Próbkowanie temperatury, top-k i top-p (jądro) w celu generowania tokenów modelu języka
- Wyjaśnij sztuczkę z reparametryzacją i dlaczego umożliwia ona propagację wsteczną poprzez próbkowanie w VAE
- Uruchom Metropolis-Hastings MCMC, aby pobrać próbkę z nieznormalizowanego rozkładu docelowego

## Problem

Model językowy kończy przetwarzanie podpowiedzi i generuje wektor 50 000 logitów. Po jednym na każdy żeton w swoim słownictwie. Teraz musi wybrać jednego. Jak?

Jeśli zawsze wybiera żeton o najwyższym prawdopodobieństwie, każda odpowiedź jest identyczna. Deterministyczny. Nudny. Jeśli wybiera równomiernie i losowo, wynik jest bełkotliwy. Odpowiedź leży gdzieś pomiędzy tymi skrajnościami i jest ona kontrolowana przez samplowanie.

Próbkowanie nie ogranicza się do generowania tekstu. Uczenie się przez wzmacnianie szacuje gradienty polityki poprzez próbkowanie trajektorii. VAE uczą się ukrytych reprezentacji poprzez próbkowanie z wyuczonych rozkładów i propagację wsteczną poprzez losowość. Modele dyfuzyjne generują obrazy poprzez próbkowanie szumu i iteracyjne usuwanie szumu. Metody Monte Carlo szacują całki, które nie mają rozwiązania w postaci zamkniętej. Algorytmy MCMC badają wielowymiarowe rozkłady późniejsze, których nie da się wyliczyć.

Każdy generatywny system AI jest systemem próbkowania. Strategia próbkowania określa jakość, różnorodność i możliwość kontrolowania wyników. W tej lekcji omówiono od podstaw każdą główną metodę próbkowania, zaczynając od jednolitych liczb losowych, a kończąc na technikach, które stanowią podstawę nowoczesnych LLM i modeli generatywnych.

## Koncepcja

### Dlaczego próbkowanie ma znaczenie

Próbkowanie pojawia się w czterech podstawowych rolach w sztucznej inteligencji i uczeniu maszynowym:

**Generacja.** Modele językowe, modele dyfuzji i sieci GAN generują dane wyjściowe poprzez próbkowanie. Algorytm próbkowania bezpośrednio kontroluje kreatywność, spójność i różnorodność. Temperatura, top-k i próbkowanie jądra to pokrętła, którymi inżynierowie codziennie kręcą.

**Szkolenie.** Minipartie próbek z gradientem stochastycznym. Porzucanie próbek neuronów w celu dezaktywacji. Rozszerzanie danych próbkuje losowe przekształcenia. Próbkowanie wagowe ponownie waży próbki, aby zmniejszyć wariancję gradientu w uczeniu się przez wzmacnianie (PPO, TRPO).

**Oszacowanie.** Wiele wielkości w ML nie ma rozwiązania w postaci zamkniętej. Oczekiwana strata w rozkładzie danych, funkcja podziału modelu opartego na energii, dowody w wnioskowaniu bayesowskim. Estymacja Monte Carlo przybliża to wszystko poprzez uśrednianie próbek.

**Eksploracja.** Algorytmy MCMC badają rozkłady późniejsze metodą wnioskowania bayesowskiego. Strategie ewolucyjne próbkują zaburzenia parametrów. Próbkowanie Thompsona równoważy eksplorację i wyzysk u bandytów.

Podstawowe wyzwanie: możesz próbkować tylko bezpośrednio z prostych rozkładów (jednolity, normalny). Do wszystkiego innego potrzebna jest metoda konwersji prostych próbek na próbki z docelowej dystrybucji.

### Jednolite próbkowanie losowe

Każda metoda pobierania próbek rozpoczyna się tutaj. Generator jednolitych liczb losowych generuje wartości w [0, 1), gdzie każdy podprzedział o równej długości ma równe prawdopodobieństwo.

```
U ~ Uniform(0, 1)

P(a <= U <= b) = b - a    for 0 <= a <= b <= 1

Properties:
  E[U] = 0.5
  Var(U) = 1/12
```

Aby próbkować równomiernie z dyskretnego zbioru n elementów, wygeneruj U i zwróć minimalny poziom (n * U). Aby pobrać próbkę z zakresu ciągłego [a, b], oblicz a + (b - a) * U.

Kluczowy wniosek: pojedyncza jednolita liczba losowa zawiera dokładnie taką ilość losowości, aby wygenerować jedną próbkę z dowolnego rozkładu. Sztuka polega na znalezieniu właściwej transformacji.

### Metoda odwrotnego CDF (próbkowanie z odwrotną transformacją)

Funkcja dystrybucji skumulowanej (CDF) odwzorowuje wartości na prawdopodobieństwa:

```
F(x) = P(X <= x)

Properties:
  F is non-decreasing
  F(-inf) = 0
  F(+inf) = 1
  F maps the real line to [0, 1]
```

Odwrotna CDF odwzorowuje prawdopodobieństwa z powrotem na wartości. Jeśli U ~ Uniform(0, 1), to X = F_inverse(U) ma rozkład docelowy.

```
Algorithm:
  1. Generate u ~ Uniform(0, 1)
  2. Return F_inverse(u)

Why it works:
  P(X <= x) = P(F_inverse(U) <= x) = P(U <= F(x)) = F(x)
```

**Przykład rozkładu wykładniczego:**

```
PDF: f(x) = lambda * exp(-lambda * x),   x >= 0
CDF: F(x) = 1 - exp(-lambda * x)

Solve F(x) = u for x:
  u = 1 - exp(-lambda * x)
  exp(-lambda * x) = 1 - u
  x = -ln(1 - u) / lambda

Since (1 - U) and U have the same distribution:
  x = -ln(u) / lambda
```

Działa to doskonale, gdy możesz zapisać F_inverse w formie zamkniętej. W przypadku rozkładu normalnego nie ma odwrotnego CDF w postaci zamkniętej, dlatego stosujemy inne metody (Box-Muller lub przybliżenie numeryczne).

**Wersja dyskretna:** W przypadku dystrybucji dyskretnych zbuduj CDF jako sumę skumulowaną, wygeneruj U i znajdź pierwszy indeks, w którym suma skumulowana przekracza U. Oto jak działa `sample_categorical` z lekcji 06.

### Próbkowanie odrzucone

Jeśli nie można odwrócić CDF, ale można ocenić docelowy plik PDF do stałej wartości, próbkowanie odrzucone działa.

```
Target distribution: p(x)  (can evaluate, possibly unnormalized)
Proposal distribution: q(x)  (can sample from)
Bound: M such that p(x) <= M * q(x) for all x

Algorithm:
  1. Sample x ~ q(x)
  2. Sample u ~ Uniform(0, 1)
  3. If u < p(x) / (M * q(x)), accept x
  4. Otherwise, reject and go to step 1

Acceptance rate = 1/M
```

Im ściślejsze ograniczenie M, tym wyższy współczynnik akceptacji. W przypadku małych wymiarów (1-3) próbkowanie przez odrzucenie działa dobrze. W przypadku dużych wymiarów współczynnik akceptacji spada wykładniczo, ponieważ większość ofert zostaje odrzucona. Jest to przekleństwo wymiarowości w próbkowaniu odrzuconym.

**Przykład: próbkowanie z obciętej normalnej.** Użyj jednolitej propozycji w obciętym zakresie. Koperta M to maksimum normalnego pliku PDF w tym zakresie.

**Przykład: próbkowanie z półkola.** Proponuj równomiernie w prostokącie ograniczającym. Zaakceptuj, jeśli punkt mieści się w półkolu. W ten sposób Monte Carlo oblicza pi: współczynnik akceptacji jest równy stosunkowi powierzchni pi/4.

### Próbkowanie ważności

Czasami nie są potrzebne próbki z docelowego rozkładu p(x). Musisz oszacować wartość oczekiwaną pod p(x) i masz próbki o innym rozkładzie q(x).

```
Goal: estimate E_p[f(x)] = integral of f(x) * p(x) dx

Rewrite:
  E_p[f(x)] = integral of f(x) * (p(x)/q(x)) * q(x) dx
            = E_q[f(x) * w(x)]

where w(x) = p(x) / q(x)  are the importance weights.

Estimator:
  E_p[f(x)] ~ (1/N) * sum(f(x_i) * w(x_i))    where x_i ~ q(x)
```

Ma to kluczowe znaczenie w procesie uczenia się przez wzmacnianie. W PPO (Proximal Policy Optimization) zbierasz trajektorie w ramach starej polityki pi_old, ale chcesz zoptymalizować nową politykę pi_new. Waga ważności to pi_new(a|s) / pi_old(a|s). PPO obcina te wagi, aby nowa polityka nie odbiegała zbytnio od starej.

Wariancja estymatora próbkowania ważności zależy od stopnia podobieństwa q do p. Jeśli q bardzo różni się od p, kilka próbek uzyskuje ogromne wagi i dominują w oszacowaniu. Próbkowanie o samonormalizowanej ważności dzieli się przez sumę wag, aby zmniejszyć ten problem:

```
E_p[f(x)] ~ sum(w_i * f(x_i)) / sum(w_i)
```

### Szacowanie Monte Carlo

Estymacja Monte Carlo przybliża całki poprzez uśrednianie próbek losowych. Prawo wielkich liczb gwarantuje zbieżność.

```
Goal: estimate I = integral of g(x) dx over domain D

Method:
  1. Sample x_1, ..., x_N uniformly from D
  2. I ~ (Volume of D / N) * sum(g(x_i))

Error: O(1 / sqrt(N))   regardless of dimension
```

Poziom błędu jest niezależny od wymiaru. Z tego powodu metody Monte Carlo dominują w dużych wymiarach, gdzie integracja oparta na siatce jest niemożliwa.

**Szacowanie pi:**

```
Sample (x, y) uniformly from [-1, 1] x [-1, 1]
Count how many fall inside the unit circle: x^2 + y^2 <= 1
pi ~ 4 * (count inside) / (total count)
```

**Szacowanie oczekiwań:**

```
E[f(X)] ~ (1/N) * sum(f(x_i))    where x_i ~ p(x)

The sample mean converges to the true expectation.
Variance of the estimator = Var(f(X)) / N
```

### Łańcuch Markowa Monte Carlo (MCMC): Metropolis-Hastings

MCMC konstruuje łańcuch Markowa, którego rozkład stacjonarny jest rozkładem docelowym p(x). Po wystarczającej liczbie kroków próbki z łańcucha są (w przybliżeniu) próbkami z p(x).

```
Target: p(x)  (known up to a normalizing constant)
Proposal: q(x'|x)  (how to propose the next state given the current state)

Metropolis-Hastings algorithm:
  1. Start at some x_0
  2. For t = 1, 2, ..., T:
     a. Propose x' ~ q(x'|x_t)
     b. Compute acceptance ratio:
        alpha = [p(x') * q(x_t|x')] / [p(x_t) * q(x'|x_t)]
     c. Accept with probability min(1, alpha):
        - If u < alpha (u ~ Uniform(0,1)): x_{t+1} = x'
        - Otherwise: x_{t+1} = x_t
  3. Discard first B samples (burn-in)
  4. Return remaining samples
```

W przypadku propozycji symetrycznych (q(x'|x) = q(x|x')) stosunek upraszcza się do p(x')/p(x). To jest oryginalny algorytm Metropolis.

**Dlaczego to działa.** Reguła akceptacji zapewnia szczegółową równowagę: prawdopodobieństwo znalezienia się w x i przejścia do x' jest równe prawdopodobieństwu znalezienia się w x' i przejścia do x. Bilans szczegółowy implikuje, że p(x) jest rozkładem stacjonarnym łańcucha.

**Względy praktyczne:**
- Wypalenie: wyrzucić wczesne próbki, zanim łańcuch osiągnie równowagę
- Rozcieńczanie: zachowaj każdą k-tą próbkę, aby zmniejszyć autokorelację
- Skala propozycji: zbyt mała i łańcuch porusza się powoli (wysoka akceptacja, powolna eksploracja); zbyt duży i większość propozycji jest odrzucana (niska akceptacja, utknięcie w miejscu)
- Optymalny współczynnik akceptacji propozycji Gaussa w dużych wymiarach wynosi około 0,234

### Próbkowanie Gibbsa

Próbkowanie Gibbsa jest szczególnym przypadkiem MCMC dla rozkładów wielowymiarowych. Zamiast proponować ruch we wszystkich wymiarach na raz, aktualizuje jedną zmienną na raz na podstawie rozkładu warunkowego.

```
Target: p(x_1, x_2, ..., x_d)

Algorithm:
  For each iteration t:
    Sample x_1^{t+1} ~ p(x_1 | x_2^t, x_3^t, ..., x_d^t)
    Sample x_2^{t+1} ~ p(x_2 | x_1^{t+1}, x_3^t, ..., x_d^t)
    ...
    Sample x_d^{t+1} ~ p(x_d | x_1^{t+1}, x_2^{t+1}, ..., x_{d-1}^{t+1})
```

Próbkowanie Gibbsa wymaga próbkowania z każdego rozkładu warunkowego p(x_i | x_{-i}). Jest to proste w przypadku wielu modeli:
- Sieci Bayesa: warunki warunkowe wynikają ze struktury grafu
- Mieszanki Gaussa: warunki warunkowe są gaussowskie
- Modele Isinga: warunek każdego spinu zależy tylko od sąsiadów

Wskaźnik akceptacji wynosi zawsze 1 (każda propozycja jest akceptowana), ponieważ próbkowanie na podstawie dokładnego warunku automatycznie zapewnia osiągnięcie salda szczegółowego.

**Ograniczenia.** Gdy zmienne są silnie skorelowane, próbkowanie Gibbsa miesza się powoli, ponieważ aktualizacja jednej zmiennej na raz nie może spowodować dużych przesunięć ukośnych w rozkładzie.

### Próbkowanie temperatury (używane w LLM)

Modele językowe wyprowadzają logity z_1, ..., z_V dla każdego tokenu w słowniku. Softmax konwertuje je na prawdopodobieństwa. Temperatura przeskalowuje logity przed softmaxem:

```
p_i = exp(z_i / T) / sum(exp(z_j / T))

T = 1.0: standard softmax (original distribution)
T -> 0:  argmax (deterministic, always picks highest logit)
T -> inf: uniform (all tokens equally likely)
T < 1.0: sharpens the distribution (more confident, less diverse)
T > 1.0: flattens the distribution (less confident, more diverse)
```

**Dlaczego to działa.** Dzielenie logitów przez T < 1 wzmacnia różnice między logitami. Jeżeli z_1 = 2 i z_2 = 1, podzielenie przez T = 0,5 daje z_1/T = 4 i z_2/T = 2, co zwiększa odstęp. Po softmax token o najwyższym logicie otrzymuje znacznie większy udział.

**W praktyce:**
- T = 0,0: dekodowanie zachłanne, najlepsze w przypadku pytań i odpowiedzi opartych na faktach
- T = 0,3-0,7: lekko kreatywny, dobry do generowania kodu
- T = 0,7-1,0: zrównoważony, dobry do ogólnej rozmowy
- T = 1,0-1,5: twórcze pisanie, burza mózgów
- T > 1,5: coraz bardziej losowe, rzadko przydatne

Temperatura nie zmienia tego, które tokeny są możliwe. Zmienia masę prawdopodobieństwa przypisaną do każdego żetonu.

### Próbkowanie z góry k

Próbkowanie top-k ogranicza zbiór kandydatów do k żetonów o najwyższym prawdopodobieństwie, następnie renormalizuje i pobiera próbki z tego ograniczonego zestawu.

```
Algorithm:
  1. Compute softmax probabilities for all V tokens
  2. Sort tokens by probability (descending)
  3. Keep only the top k tokens
  4. Renormalize: p_i' = p_i / sum(p_j for j in top-k)
  5. Sample from the renormalized distribution

k = 1:  greedy decoding
k = V:  no filtering (standard sampling)
k = 40: typical setting, removes long tail of unlikely tokens
```

Top-k zapobiega wybieraniu przez model niezwykle mało prawdopodobnych tokenów (literówek, nonsensów), które istnieją na długim ogonie rozkładu słownictwa. Problem: k został naprawiony niezależnie od kontekstu. Gdy model jest pewny (jeden żeton ma 95% prawdopodobieństwa), k = 40 nadal pozwala na 39 alternatyw. Gdy model jest niepewny (prawdopodobieństwo rozkłada się na 1000 żetonów), k = 40 odcina prawdopodobne opcje.

### Próbkowanie z góry (jądro).

Próbkowanie Top-p dynamicznie dostosowuje rozmiar zestawu kandydującego. Zamiast utrzymywać stałą liczbę żetonów, zatrzymuje najmniejszy zestaw żetonów, których skumulowane prawdopodobieństwo przekracza p.

```
Algorithm:
  1. Compute softmax probabilities for all V tokens
  2. Sort tokens by probability (descending)
  3. Find smallest k such that sum of top-k probabilities >= p
  4. Keep only those k tokens
  5. Renormalize and sample

p = 0.9:  keeps tokens covering 90% of probability mass
p = 1.0:  no filtering
p = 0.1:  very restrictive, nearly greedy
```

Gdy model jest pewny, próbkowanie jądra pozwala zachować kilka tokenów (może 2-3). Gdy model jest niepewny, przechowuje wiele (może 200). To zachowanie adaptacyjne jest powodem, dla którego próbkowanie jądra generalnie daje lepszy tekst niż górne-k.

**Typowe kombinacje:**
- Temperatura 0,7 + góra-p 0,9: dobre ustawienie ogólnego przeznaczenia
- Temperatura 0,0 (zachłanny): najlepsza dla zadań deterministycznych
- Temperatura 1,0 + top-k 50: Fan i in. (2018) oryginalne ustawienie papieru

Top-k i top-p można łączyć. Najpierw zastosuj top-k, a następnie top-p na pozostałym zestawie.

### Sztuczka reparametryzacyjna (używana w VAE)

Autoenkodery wariacyjne (VAE) uczą się poprzez kodowanie danych wejściowych do rozkładu w przestrzeni utajonej, próbkowanie z tego rozkładu i ponowne dekodowanie próbki. Problem: nie można propagować wstecznie poprzez operację próbkowania.

```
Standard sampling (not differentiable):
  z ~ N(mu, sigma^2)

  The randomness blocks gradient flow.
  d/d_mu [sample from N(mu, sigma^2)] = ???
```

Sztuczka reparametryzacji oddziela losowość od parametrów:

```
Reparameterized sampling:
  epsilon ~ N(0, 1)          (fixed random noise, no parameters)
  z = mu + sigma * epsilon   (deterministic function of parameters)

  Now z is a deterministic, differentiable function of mu and sigma.
  d(z)/d(mu) = 1
  d(z)/d(sigma) = epsilon

  Gradients flow through mu and sigma.
```

Działa to, ponieważ N(mu, sigma^2) ma taki sam rozkład jak mu + sigma * N(0, 1). Kluczowy wniosek: przenieś losowość do źródła wolnego od parametrów (epsilon), a następnie wyraź próbkę jako różniczkowalną transformację parametrów.

**W pętli szkoleniowej VAE:**
1. Koder wyprowadza mu i log(sigma^2) dla każdego wejścia
2. Próbka epsilon ~ N(0, 1)
3. Oblicz z = mu + sigma * epsilon
4. Zdekoduj z, aby zrekonstruować dane wejściowe
5. Propaguj wstecznie przez kroki 4, 3, 2, 1 (możliwe, ponieważ krok 3 jest różniczkowalny)

Bez sztuczki z reparametryzacją VAE nie mogą być trenowane przy użyciu standardowej propagacji wstecznej. Dzięki temu pojedynczemu spostrzeżeniu VAE stały się praktyczne.

### Gumbel-Softmax (różnicowane próbkowanie kategoryczne)

Sztuczka reparametryzacji działa w przypadku rozkładów ciągłych (Gaussa). W przypadku dyskretnych rozkładów kategorycznych potrzebujemy innego podejścia. Gumbel-Softmax zapewnia różniczkowe przybliżenie próbkowania kategorycznego.

**Sztuczka Gumbel-Maxa (nieróżniczkowalna):**

```
To sample from a categorical distribution with log-probabilities log(p_1), ..., log(p_k):
  1. Sample g_i ~ Gumbel(0, 1) for each category
     (g = -log(-log(u)), where u ~ Uniform(0, 1))
  2. Return argmax(log(p_i) + g_i)

This produces exact categorical samples.
```

**Gumbel-Softmax (przybliżenie różniczkowalne):**

```
Replace the hard argmax with a soft softmax:
  y_i = exp((log(p_i) + g_i) / tau) / sum(exp((log(p_j) + g_j) / tau))

tau (temperature) controls the approximation:
  tau -> 0:  approaches a one-hot vector (hard categorical)
  tau -> inf: approaches uniform (1/k, 1/k, ..., 1/k)
  tau = 1.0: soft approximation
```

Gumbel-Softmax zapewnia ciągłą relaksację dyskretnej próbki. Dane wyjściowe to wektor prawdopodobieństwa (miękki, jeden gorący), a nie twardy, jeden gorący. Gradienty przepływają przez softmax. Podczas treningu w przód możesz użyć estymatora „prostego”: użyj twardego argmax dla podania w przód, ale miękkiego gradientu Gumbel-Softmax dla podania w tył.

**Zastosowania:**
- Dyskretne zmienne ukryte w VAE
- Wyszukiwanie architektury neuronowej (wybór operacji dyskretnych)
- Mechanizmy twardej uwagi
- Uczenie się ze wzmocnieniem za pomocą dyskretnych działań

### Próbkowanie warstwowe

Standardowe próbkowanie Monte Carlo może przez przypadek pozostawić luki w przestrzeni próbki. Próbkowanie warstwowe wymusza równomierne pokrycie poprzez podzielenie przestrzeni na warstwy i pobieranie próbek z każdej z nich.

```
Standard Monte Carlo:
  Sample N points uniformly from [0, 1]
  Some regions may have clusters, others gaps

Stratified sampling:
  Divide [0, 1] into N equal strata: [0, 1/N), [1/N, 2/N), ..., [(N-1)/N, 1)
  Sample one point uniformly within each stratum
  x_i = (i + u_i) / N   where u_i ~ Uniform(0, 1),  i = 0, ..., N-1
```

Próbkowanie warstwowe zawsze ma mniejszą lub równą wariancję w porównaniu ze standardowym Monte Carlo:

```
Var(stratified) <= Var(standard Monte Carlo)

The improvement is largest when f(x) varies smoothly.
For piecewise-constant functions, stratified sampling is exact.
```

**Zastosowania:**
- Całkowanie numeryczne (quasi-Monte Carlo)
- Podział danych treningowych (zapewniający równowagę klas w każdym przypadku)
- Próbkowanie według ważności z stratyfikację (połączenie obu technik)
- NeRF (Neural Radiance Fields) wykorzystuje próbkowanie warstwowe wzdłuż promieni kamery

### Połączenie z modelami dyfuzyjnymi

Modele dyfuzyjne generują obrazy w procesie próbkowania. Proces do przodu dodaje szum Gaussa do obrazu w T krokach, aż stanie się czystym szumem. Proces odwrotny uczy się odszumiania, krok po kroku odzyskując oryginalny obraz.

```
Forward process (known):
  x_t = sqrt(alpha_t) * x_{t-1} + sqrt(1 - alpha_t) * epsilon
  where epsilon ~ N(0, I)

  After T steps: x_T ~ N(0, I)  (pure noise)

Reverse process (learned):
  x_{t-1} = (1/sqrt(alpha_t)) * (x_t - (1 - alpha_t)/sqrt(1 - alpha_bar_t) * epsilon_theta(x_t, t)) + sigma_t * z
  where z ~ N(0, I)

  Each denoising step is a sampling step.
```

Połączenie z metodami z tej lekcji:
- Każdy krok odszumiania wykorzystuje sztuczkę ponownej parametryzacji (próbka szumu, zastosowanie transformacji deterministycznej)
- Harmonogram szumów {alpha_t} kontroluje formę wyżarzania temperaturowego
- Trening wykorzystuje estymację Monte Carlo w celu przybliżenia ELBO (dolna granica dowodu)
- Próbkowanie przodków w modelach dyfuzyjnych to łańcuch Markowa (każdy krok zależy tylko od stanu bieżącego)

Cały proces generowania obrazu polega na próbkowaniu iteracyjnym: zacznij od szumu i na każdym etapie próbkuj wersję nieco mniej zaszumioną, uwarunkowaną wyuczonym modelem odszumiania.

## Zbuduj to

### Krok 1: Próbkowanie jednolite i odwrotne CDF

```python
import math
import random

def sample_uniform(a, b):
    return a + (b - a) * random.random()

def sample_exponential_inverse_cdf(lam):
    u = random.random()
    return -math.log(u) / lam
```

Wygeneruj 10 000 próbek wykładniczych i sprawdź, czy średnia wynosi 1/lambda.

### Krok 2: Próbkowanie odrzucone

```python
def rejection_sample(target_pdf, proposal_sample, proposal_pdf, M):
    while True:
        x = proposal_sample()
        u = random.random()
        if u < target_pdf(x) / (M * proposal_pdf(x)):
            return x
```

Użyj próbkowania przez odrzucenie, aby wyciągnąć z obciętego rozkładu normalnego. Sprawdź kształt poprzez histogram próbek.

### Krok 3: Próbkowanie ważności

```python
def importance_sampling_estimate(f, target_pdf, proposal_pdf, proposal_sample, n):
    total = 0
    for _ in range(n):
        x = proposal_sample()
        w = target_pdf(x) / proposal_pdf(x)
        total += f(x) * w
    return total / n
```

Oszacuj E[X^2] w rozkładzie normalnym, korzystając z jednolitej propozycji. Porównaj ze znaną odpowiedzią (mu^2 + sigma^2).

### Krok 4: Oszacowanie liczby pi metodą Monte Carlo

```python
def monte_carlo_pi(n):
    inside = 0
    for _ in range(n):
        x = random.uniform(-1, 1)
        y = random.uniform(-1, 1)
        if x*x + y*y <= 1:
            inside += 1
    return 4 * inside / n
```

### Krok 5: MCMC Metropolis-Hastings

```python
def metropolis_hastings(target_log_pdf, proposal_sample, proposal_log_pdf, x0, n_samples, burn_in):
    samples = []
    x = x0
    for i in range(n_samples + burn_in):
        x_new = proposal_sample(x)
        log_alpha = (target_log_pdf(x_new) + proposal_log_pdf(x, x_new)
                     - target_log_pdf(x) - proposal_log_pdf(x_new, x))
        if math.log(random.random()) < log_alpha:
            x = x_new
        if i >= burn_in:
            samples.append(x)
    return samples
```

Próbka z rozkładu bimodalnego (mieszanina dwóch Gaussów). Wizualizuj trajektorię łańcucha.

### Krok 6: Próbkowanie Gibbsa

```python
def gibbs_sampling_2d(conditional_x_given_y, conditional_y_given_x, x0, y0, n_samples, burn_in):
    x, y = x0, y0
    samples = []
    for i in range(n_samples + burn_in):
        x = conditional_x_given_y(y)
        y = conditional_y_given_x(x)
        if i >= burn_in:
            samples.append((x, y))
    return samples
```

### Krok 7: Próbkowanie temperatury

```python
def softmax(logits):
    max_l = max(logits)
    exps = [math.exp(z - max_l) for z in logits]
    total = sum(exps)
    return [e / total for e in exps]

def temperature_sample(logits, temperature):
    scaled = [z / temperature for z in logits]
    probs = softmax(scaled)
    return sample_from_probs(probs)
```

Pokaż, jak temperatura zmienia rozkład wyjściowy dla zestawu logitów symbolicznych.

### Krok 8: Próbkowanie top-k i top-p

```python
def top_k_sample(logits, k):
    indexed = sorted(enumerate(logits), key=lambda x: -x[1])
    top = indexed[:k]
    top_logits = [l for _, l in top]
    probs = softmax(top_logits)
    idx = sample_from_probs(probs)
    return top[idx][0]

def top_p_sample(logits, p):
    probs = softmax(logits)
    indexed = sorted(enumerate(probs), key=lambda x: -x[1])
    cumsum = 0
    selected = []
    for token_idx, prob in indexed:
        cumsum += prob
        selected.append((token_idx, prob))
        if cumsum >= p:
            break
    sel_probs = [pr for _, pr in selected]
    total = sum(sel_probs)
    sel_probs = [pr / total for pr in sel_probs]
    idx = sample_from_probs(sel_probs)
    return selected[idx][0]
```

### Krok 9: Sztuczka z ponowną parametryzacją

```python
def reparam_sample(mu, sigma):
    epsilon = random.gauss(0, 1)
    return mu + sigma * epsilon

def reparam_gradient(mu, sigma, epsilon):
    dz_dmu = 1.0
    dz_dsigma = epsilon
    return dz_dmu, dz_dsigma
```

Wykazać, że gradienty przepływają przez ponownie sparametryzowaną próbkę, ale nie przez bezpośrednie próbkowanie.

### Krok 10: Gumbel-Softmax

```python
def gumbel_sample():
    u = random.random()
    return -math.log(-math.log(u))

def gumbel_softmax(logits, temperature):
    gumbels = [math.log(p) + gumbel_sample() for p in logits]
    return softmax([g / temperature for g in gumbels])
```

Pokaż, jak malejąca temperatura powoduje, że sygnał wyjściowy zbliża się do wektora jednego gorącego.

Pełne wdrożenia wraz ze wszystkimi wizualizacjami znajdują się w `code/sampling.py`.

## Użyj tego

W przypadku NumPy i SciPy wersje produkcyjne:

```python
import numpy as np

rng = np.random.default_rng(42)

exponential_samples = rng.exponential(scale=2.0, size=10000)
print(f"Exponential mean: {exponential_samples.mean():.4f} (expected 2.0)")

from scipy import stats
normal = stats.norm(loc=0, scale=1)
print(f"CDF at 1.96: {normal.cdf(1.96):.4f}")
print(f"Inverse CDF at 0.975: {normal.ppf(0.975):.4f}")

logits = np.array([2.0, 1.0, 0.5, 0.1, -1.0])
temperature = 0.7
scaled = logits / temperature
probs = np.exp(scaled - scaled.max()) / np.exp(scaled - scaled.max()).sum()
token = rng.choice(len(logits), p=probs)
print(f"Sampled token index: {token}")
```

W przypadku MCMC na dużą skalę użyj dedykowanych bibliotek:
- PyMC: pełne modelowanie bayesowskie za pomocą NUTS (adaptacyjna HMC)
- emcee: sampler zespołu MCMC
- NumPyro/JAX: MCMC z akceleracją GPU

Zbudowałeś je od zera. Teraz już wiesz, co robią wezwania do biblioteki.

## Ćwiczenia

1. Zaimplementuj odwrotne próbkowanie CDF dla rozkładu Cauchy'ego. CDF wynosi F(x) = 0,5 + arctan(x)/pi. Wygeneruj 10 000 próbek i porównaj histogram z prawdziwym plikiem PDF. Zwróć uwagę na ciężkie ogony (ekstremalne wartości daleko od środka).

2. Użyj próbkowania odrzucającego, aby wygenerować próbki z rozkładu Beta(2, 5) przy użyciu propozycji Uniform(0, 1). Porównaj zaakceptowane próbki z prawdziwym plikiem Beta PDF. Jaki jest teoretyczny współczynnik akceptacji?

3. Oszacuj całkę sin(x) od 0 do pi, stosując metodę Monte Carlo dla 1000, 10 000 i 100 000 próbek. Porównaj błąd na każdym poziomie. Sprawdź, czy błąd skaluje się jako O(1/sqrt(N)).

4. Zaimplementuj Metropolis-Hastings, aby próbkować z rozkładu 2D p(x, y) proporcjonalnego do exp(-(x^2 * y^2 + x^2 + y^2 - 8*x - 8*y) / 2). Narysuj próbki i trajektorię łańcucha. Eksperymentuj z różnymi odchyleniami standardowymi propozycji.

5. Zbuduj pełne demo generowania tekstu: mając słownictwo składające się z 10 słów z logitami, wygeneruj sekwencje 20 tokenów za pomocą (a) zachłannego, (b) temperatury=0,7, (c) top-k=3, (d) top-p=0,9. Porównaj różnorodność wyników w 5 seriach.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|----------------------|
| Próbkowanie | „Rysowanie wartości losowych” | Generowanie wartości na podstawie rozkładu prawdopodobieństwa. Mechanizm stojący za całą generatywną sztuczną inteligencją |
| Równomierny rozkład | „Wszystkie równie prawdopodobne” | Każda wartość w [a, b] ma równą gęstość prawdopodobieństwa 1/(b-a). Punkt wyjścia dla wszystkich metod pobierania próbek |
| Odwrotna CDF | „Transformacja prawdopodobieństwa” | F_inverse(U) konwertuje próbkę jednorodną na próbkę z dowolnego rozkładu o znanej CDF. Dokładny i wydajny |
| Próbkowanie odrzucone | „Zaproponuj i zaakceptuj/odrzuć” | Generuj na podstawie prostej propozycji, zaakceptuj z prawdopodobieństwem proporcjonalnym do stosunku cel/propozycja. Dokładne, ale marnuje próbki |
| Próbkowanie znaczenia | „Ponowne zważenie próbek” | Oszacuj oczekiwania w ramach p(x), korzystając z próbek z q(x), ważąc każdą próbkę przez p(x)/q(x). Rdzeń do PPO w RL |
| Monte Carlo | „Średnie próbki losowe” | Całki przybliżone jako średnie z próbek. Błąd O(1/sqrt(N)) niezależnie od wymiaru |
| MCMC | „Losowy spacer, który zbiega się” | Skonstruuj łańcuch Markowa, którego rozkład stacjonarny jest celem. Metropolis-Hastings to podstawowy algorytm |
| Metropolis-Hastings | „Akceptuj pod górę, czasem w dół” | Proponuj ruchy, akceptuj je na podstawie współczynnika gęstości. Szczegółowy bilans zapewnia zbieżność z dystrybucją docelową |
| Próbkowanie Gibbsa | „Jedna zmienna na raz” | Zaktualizuj każdą zmienną na podstawie jej rozkładu warunkowego, pozostawiając inne stałe. 100% współczynnik akceptacji |
| Temperatura | „Pokrętło pewności” | Dzieli logity przez T przed softmax. T<1 wyostrza (bardziej pewny siebie), T>1 spłaszcza (bardziej zróżnicowany) |
| Próbkowanie top-k | „Zachowaj najlepsze wyniki” | Wyzeruj wszystkie oprócz k żetonów o najwyższym prawdopodobieństwie, renormalizuj, próbkuj. Naprawiono rozmiar zestawu kandydatów |
| Pobieranie próbek jądra (góra-p) | „Zachowaj prawdopodobne” | Zachowaj najmniejszy zestaw żetonów, których skumulowane prawdopodobieństwo przekracza p. Rozmiar adaptacyjnego zestawu kandydatów |
| Sztuczka reparametryzacyjna | „Przenieś losowość na zewnątrz” | Zapisz z = mu + sigma * epsilon gdzie epsilon ~ N(0,1). Umożliwia różnicowanie próbkowania. Niezbędne w szkoleniu VAE |
| Gumbel-Softmax | „Miękkie próbkowanie kategoryczne” | Różniczkowe przybliżenie do próbkowania kategorycznego przy użyciu szumu Gumbela + softmax z temperaturą |
| Próbkowanie warstwowe | „Przymusowy zasięg” | Podziel przestrzeń próbki na warstwy, pobierz próbkę z każdej. Zawsze niższa wariancja niż naiwne Monte Carlo |
| Wypalenie | „Okres rozgrzewkowy” | Początkowe próbki MCMC odrzucone, zanim łańcuch osiągnie rozkład stacjonarny |
| Bilans szczegółowy | „Warunek odwracalności” | p(x) * T(x->y) = p(y) * T(y->x). Warunek wystarczający, aby p było rozkładem stacjonarnym łańcucha Markowa |
| Próbkowanie dyfuzyjne | „Iteracyjne odszumianie” | Generuj dane, zaczynając od szumu i stosując wyuczone kroki odszumiania. Każdy krok jest operacją próbkowania warunkowego |

## Dalsze czytanie

- [Holbrook (2023): The Metropolis-Hastings Algorithm](https://arxiv.org/abs/2304.07010) - szczegółowy poradnik na temat podstaw MCMC
- [Jang, Gu, Poole (2017): Kategoryczna reparametryzacja za pomocą Gumbel-Softmax](https://arxiv.org/abs/1611.01144) - oryginalna praca Gumbel-Softmax
- [Holtzman i in. (2020): Ciekawy przypadek degeneracji tekstu neuronowego](https://arxiv.org/abs/1904.09751) – dokument dotyczący jądra (góra-p)
- [Kingma & Welling (2014): Auto-Encoding Variational Bayes](https://arxiv.org/abs/1312.6114) - artykuł VAE przedstawiający sztuczkę reparametryzacji
- [Ho, Jain, Abbeel (2020): Denoising Diffusion Probabilistic Models](https://arxiv.org/abs/2006.11239) – DDPM łączy próbkowanie z generowaniem obrazu