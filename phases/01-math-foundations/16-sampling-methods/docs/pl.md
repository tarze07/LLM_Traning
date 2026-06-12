# Metody samplowania

> Samplowanie to sposób, w jaki AI eksploruje przestrzeń możliwości.

**Typ:** Build
**Język:** Python
**Wymagania wstępne:** Faza 1, Lekcje 06-07 (Prawdopodobieństwo, Teorem Bayesa)
**Czas:** ~120 minut

## Cele nauki

- Zaimplementuj odwrotny CDF, sampling odrzucania (rejection sampling) i sampling istotnościowy (importance sampling) od zera, używając tylko liczb losowych z rozkładu jednostajnego
- Zbuduj sampling z temperaturą, top-k oraz top-p (nucleus) do generowania tokenów w modelach językowych
- Wyjaśnij trik reparametryzacji (reparameterization trick) i dlaczego umożliwia propagację wsteczną przez samplowanie w VAE
- Uruchom MCMC Metropolis-Hastings, aby samplować z nieznormalizowanego rozkładu docelowego

## Problem

Model językowy kończy przetwarzanie twojego promptu i produkuje wektor 50 000 logitów. Jeden dla każdego tokena w jego słowniku. Teraz musi wybrać jeden. Jak?

Jeśli zawsze wybiera token o najwyższym prawdopodobieństwie, każda odpowiedź jest identyczna. Deterministyczna. Nudna. Jeśli wybiera jednostajnie losowo, wynik to bełkot. Odpowiedź leży gdzieś między tymi ekstremami, i to "gdzieś" jest kontrolowane przez samplowanie.

Samplowanie nie ogranicza się do generowania tekstu. Uczenie ze wzmocnieniem (reinforcement learning) szacuje gradienty polityki poprzez samplowanie trajektorii. VAE uczą się reprezentacji ukrytych (latent representations) poprzez samplowanie z wyuczonych rozkładów i propagację wsteczną przez losowość. Modele dyfuzyjne generują obrazy poprzez samplowanie szumu i iteracyjne odszumianie. Metody Monte Carlo estymują całki, które nie mają rozwiązania w postaci zamkniętej. Algorytmy MCMC eksplorują rozkłady posterior o wysokiej wymiarowości, których nie da się wyliczyć w pełni.

Każdy generatywny system AI jest systemem samplującym. Strategia samplowania determinuje jakość, różnorodność i kontrolowalność wyniku. Ta lekcja buduje każdą główną metodę samplowania od zera, zaczynając od liczb losowych z rozkładu jednostajnego, a kończąc na technikach, które zasilają współczesne LLM-y i modele generatywne.

## Koncepcja

### Czemu samplowanie ma znaczenie

Samplowanie pojawia się w czterech fundamentalnych rolach w AI i uczeniu maszynowym:

**Generacja.** Modele językowe, modele dyfuzyjne i GAN-y produkują wynik poprzez samplowanie. Algorytm samplowania bezpośrednio kontroluje kreatywność, spójność i różnorodność. Temperatura, top-k i nucleus sampling są pokrętłami, które inżynierowie codziennie obracają.

**Trening.** Stochastic gradient descent samplujeje mini-partie (mini-batches). Dropout samplujeje neurony do dezaktywacji. Augmentacja danych samplujeje losowe transformacje. Importance sampling przeważa próbki, aby zmniejszyć wariancję gradientu w uczeniu ze wzmocnieniem (PPO, TRPO).

**Estymacja.** Wiele wielkości w ML nie ma rozwiązania w postaci zamkniętej. Oczekiwana strata po rozkładzie danych, funkcja podziału (partition function) modelu energetycznego, evidence w inferencji bayesowskiej. Estymacja Monte Carlo aproksymuje wszystkie te wielkości poprzez średnią z próbek.

**Eksploracja.** Algorytmy MCMC eksplorują rozkłady posterior w inferencji bayesowskiej. Strategie ewolucyjne samplują perturbacje parametrów. Thompson sampling balansuje eksplorację i eksploatację w bandytach (bandits).

Główne wyzwanie: można samplować bezpośrednio tylko z prostych rozkładów (jednostajny, normalny). Dla wszystkiego innego potrzebna jest metoda przekształcania prostych próbek na próbki z rozkładu docelowego.

### Sampling jednostajny (uniform)

Każda metoda samplowania zaczyna się tutaj. Generator liczb losowych z rozkładu jednostajnego produkuje wartości w [0, 1), gdzie każdy podprzedział o równej długości ma równe prawdopodobieństwo.

```
U ~ Uniform(0, 1)

P(a <= U <= b) = b - a    dla 0 <= a <= b <= 1

Właściwości:
  E[U] = 0.5
  Var(U) = 1/12
```

Aby samplować jednostajnie z dyskretnego zbioru n elementów, generujemy U i zwracamy floor(n * U). Aby samplować z ciągłego zakresu [a, b], obliczamy a + (b - a) * U.

Kluczowy wgląd: pojedyncza liczba losowa z rozkładu jednostajnego zawiera dokładnie odpowiednią ilość losowości, by wyprodukować jedną próbkę z dowolnego rozkładu. Sztuczka polega na znalezieniu odpowiedniej transformacji.

### Metoda odwrotnego CDF (Inverse Transform Sampling)

Funkcja dystrybucji kumulatywnej (CDF) odwzorowuje wartości na prawdopodobieństwa:

```
F(x) = P(X <= x)

Właściwości:
  F jest niemalejąca
  F(-inf) = 0
  F(+inf) = 1
  F odwzorowuje linię rzeczywistą na [0, 1]
```

Odwrotny CDF odwzorowuje prawdopodobieństwa z powrotem na wartości. Jeśli U ~ Uniform(0, 1), to X = F_inverse(U) jest zgodne z rozkładem docelowym.

```
Algorytm:
  1. Wygeneruj u ~ Uniform(0, 1)
  2. Zwróć F_inverse(u)

Czemu to działa:
  P(X <= x) = P(F_inverse(U) <= x) = P(U <= F(x)) = F(x)
```

**Przykład: rozkład wykładniczy (exponential):**

```
PDF: f(x) = lambda * exp(-lambda * x),   x >= 0
CDF: F(x) = 1 - exp(-lambda * x)

Rozwiąż F(x) = u dla x:
  u = 1 - exp(-lambda * x)
  exp(-lambda * x) = 1 - u
  x = -ln(1 - u) / lambda

Ponieważ (1 - U) i U mają ten sam rozkład:
  x = -ln(u) / lambda
```

To działa idealnie, gdy można zapisać F_inverse w postaci zamkniętej. Dla rozkładu normalnego nie istnieje odwrotny CDF w postaci zamkniętej, więc używamy innych metod (Box-Muller lub numeryczna aproksymacja).

**Wersja dyskretna:** Dla rozkładów dyskretnych budujemy CDF jako sumę kumulatywną, generujemy U i znajdujemy pierwszy indeks, w którym suma kumulatywna przekracza U. Tak działa `sample_categorical` z Lekcji 06.

### Sampling odrzucania (Rejection Sampling)

Gdy nie można odwrócić CDF, ale można obliczyć wartość docelowego PDF z dokładnością do stałej, działa sampling odrzucania.

```
Rozkład docelowy: p(x)  (można obliczyć, możliwie nieznormalizowany)
Rozkład proponujący: q(x)  (można z niego samplować)
Granica: M taka, że p(x) <= M * q(x) dla wszystkich x

Algorytm:
  1. Wylosuj x ~ q(x)
  2. Wylosuj u ~ Uniform(0, 1)
  3. Jeśli u < p(x) / (M * q(x)), zaakceptuj x
  4. W przeciwnym razie odrzuć i wróć do kroku 1

Współczynnik akceptacji = 1/M
```

Im ściślejsza granica M, tym wyższy współczynnik akceptacji. W niskich wymiarach (1-3) sampling odrzucania działa dobrze. W wysokich wymiarach współczynnik akceptacji spada wykładniczo, ponieważ większość objętości propozycji jest odrzucana. To jest przekleństwo wymiarowości (curse of dimensionality) dla samplingu odrzucania.

**Przykład: samplowanie z obciętego rozkładu normalnego (truncated normal).** Użyj jednostajnej propozycji w obciętym zakresie. Otoczka M to maksimum PDF rozkładu normalnego w tym zakresie.

**Przykład: samplowanie z półokręgu.** Proponuj jednostajnie w obejmującym prostokącie. Akceptuj, jeśli punkt znajduje się wewnątrz półokręgu. Tak Monte Carlo oblicza pi: współczynnik akceptacji jest równy stosunkowi obszarów pi/4.

### Sampling istotnościowy (Importance Sampling)

Czasami nie potrzebujesz próbek z rozkładu docelowego p(x). Potrzebujesz oszacować wartość oczekiwaną pod p(x), a masz próbki z innego rozkładu q(x).

```
Cel: oszacować E_p[f(x)] = integral z f(x) * p(x) dx

Przekształć:
  E_p[f(x)] = integral z f(x) * (p(x)/q(x)) * q(x) dx
            = E_q[f(x) * w(x)]

gdzie w(x) = p(x) / q(x)  to wagi istotnościowe (importance weights).

Estymator:
  E_p[f(x)] ~ (1/N) * sum(f(x_i) * w(x_i))    gdzie x_i ~ q(x)
```

To jest krytyczne w uczeniu ze wzmocnieniem. W PPO (Proximal Policy Optimization) zbierasz trajektorie pod starą polityką pi_old, ale chcesz zoptymalizować nową politykę pi_new. Waga istotnościowa to pi_new(a|s) / pi_old(a|s). PPO przycina (clips) te wagi, aby zapobiec nadmiernemu odchyleniu nowej polityki od starej.

Wariancja estymatora samplingu istotnościowego zależy od tego, jak podobne jest q do p. Jeśli q jest bardzo różne od p, kilka próbek otrzymuje ogromne wagi i dominuje estymację. Self-normalized importance sampling dzieli przez sumę wag, aby zmniejszyć ten problem:

```
E_p[f(x)] ~ sum(w_i * f(x_i)) / sum(w_i)
```

### Estymacja Monte Carlo

Estymacja Monte Carlo aproksymuje całki poprzez średnią z losowych próbek. Prawo wielkich liczb gwarantuje zbieżność.

```
Cel: oszacować I = integral z g(x) dx po domenie D

Metoda:
  1. Wylosuj x_1, ..., x_N jednostajnie z D
  2. I ~ (Objętość D / N) * sum(g(x_i))

Błąd: O(1 / sqrt(N))   niezależnie od wymiaru
```

Tempo błędu jest niezależne od wymiaru. To jest powód, dla którego metody Monte Carlo dominują w wysokich wymiarach, gdzie integracja oparta na siatce jest niemożliwa.

**Estymacja pi:**

```
Wylosuj (x, y) jednostajnie z [-1, 1] x [-1, 1]
Zlicz, ile punktów wpada wewnątrz okręgu jednostkowego: x^2 + y^2 <= 1
pi ~ 4 * (liczba wewnątrz) / (liczba całkowita)
```

**Estymacja wartości oczekiwanych:**

```
E[f(X)] ~ (1/N) * sum(f(x_i))    gdzie x_i ~ p(x)

Średnia z próbki zbiega się do prawdziwej wartości oczekiwanej.
Wariancja estymatora = Var(f(X)) / N
```

### Markov Chain Monte Carlo (MCMC): Metropolis-Hastings

MCMC konstruuje łańcuch Markowa, którego rozkład stacjonarny jest rozkładem docelowym p(x). Po wystarczającej liczbie kroków, próbki z łańcucha są (w przybliżeniu) próbkami z p(x).

```
Cel: p(x)  (znany z dokładnością do stałej normalizującej)
Propozycja: q(x'|x)  (jak proponować następny stan dany stan obecny)

Algorytm Metropolis-Hastings:
  1. Zacznij od pewnego x_0
  2. Dla t = 1, 2, ..., T:
     a. Zaproponuj x' ~ q(x'|x_t)
     b. Oblicz współczynnik akceptacji:
        alpha = [p(x') * q(x_t|x')] / [p(x_t) * q(x'|x_t)]
     c. Zaakceptuj z prawdopodobieństwem min(1, alpha):
        - Jeśli u < alpha (u ~ Uniform(0,1)): x_{t+1} = x'
        - W przeciwnym razie: x_{t+1} = x_t
  3. Odrzuć pierwsze B próbek (burn-in)
  4. Zwróć pozostałe próbki
```

Dla symetrycznych propozycji (q(x'|x) = q(x|x')), współczynnik redukuje się do p(x')/p(x). To jest oryginalny algorytm Metropolis.

**Czemu to działa.** Reguła akceptacji zapewnia szczegółowy bilans (detailed balance): prawdopodobieństwo bycia w x i przejścia do x' jest równe prawdopodobieństwu bycia w x' i przejścia do x. Szczegółowy bilans implikuje, że p(x) jest rozkładem stacjonarnym łańcucha.

**Praktyczne rozważania:**
- Burn-in: odrzuć wczesne próbki, zanim łańcuch osiągnie równowagę
- Thinning: zachowuj co k-tą próbkę, aby zredukować autokorelację
- Skala propozycji: zbyt mała i łańcuch przemieszcza się powoli (wysoka akceptacja, wolna eksploracja); zbyt duża i większość propozycji jest odrzucana (niska akceptacja, zablokowanie w miejscu)
- Optymalny współczynnik akceptacji dla propozycji gaussowskiej w wysokich wymiarach to około 0.234

### Gibbs Sampling

Gibbs sampling jest specjalnym przypadkiem MCMC dla rozkładów wielowymiarowych. Zamiast proponować ruch we wszystkich wymiarach na raz, aktualizuje jedną zmienną na raz z jej rozkładu warunkowego.

```
Cel: p(x_1, x_2, ..., x_d)

Algorytm:
  Dla każdej iteracji t:
    Wylosuj x_1^{t+1} ~ p(x_1 | x_2^t, x_3^t, ..., x_d^t)
    Wylosuj x_2^{t+1} ~ p(x_2 | x_1^{t+1}, x_3^t, ..., x_d^t)
    ...
    Wylosuj x_d^{t+1} ~ p(x_d | x_1^{t+1}, x_2^{t+1}, ..., x_{d-1}^{t+1})
```

Gibbs sampling wymaga, aby można było samplować z każdego rozkładu warunkowego p(x_i | x_{-i}). To jest proste dla wielu modeli:
- Sieci bayesowskie: rozkłady warunkowe wynikają ze struktury grafu
- Mieszaniny gaussowskie (Gaussian mixtures): rozkłady warunkowe są gaussowskie
- Modele Isinga: warunkowy rozkład każdego spinu zależy tylko od jego sąsiadów

Współczynnik akceptacji jest zawsze równy 1 (każda propozycja jest akceptowana), ponieważ samplowanie z dokładnego rozkładu warunkowego automatycznie spełnia szczegółowy bilans.

**Ograniczenie.** Gdy zmienne są silnie skorelowane, Gibbs sampling miesza się wolno, ponieważ aktualizowanie jednej zmiennej na raz nie może wykonać dużych ruchów po przekątnej przez rozkład.

### Temperature Sampling (używany w LLM)

Modele językowe wyprowadzają logity z_1, ..., z_V dla każdego tokena w słowniku. Softmax przekształca te wartości w prawdopodobieństwa. Temperatura przeskalowuje logity przed softmax:

```
p_i = exp(z_i / T) / sum(exp(z_j / T))

T = 1.0: standardowy softmax (oryginalny rozkład)
T -> 0:  argmax (deterministyczny, zawsze wybiera najwyższy logit)
T -> inf: jednostajny (wszystkie tokeny równie prawdopodobne)
T < 1.0: zaostrza rozkład (bardziej pewny, mniej różnorodny)
T > 1.0: spłaszcza rozkład (mniej pewny, bardziej różnorodny)
```

**Czemu to działa.** Dzielenie logitów przez T < 1 wzmacnia różnice między logitami. Jeśli z_1 = 2 i z_2 = 1, dzielenie przez T = 0.5 daje z_1/T = 4 i z_2/T = 2, powiększając różnicę. Po softmax token o najwyższym logicie otrzymuje znacznie większy udział.

**W praktyce:**
- T = 0.0: greedy decoding, najlepsze dla faktograficznych Q&A
- T = 0.3-0.7: lekko kreatywny, dobry dla generowania kodu
- T = 0.7-1.0: zbalansowany, dobry dla ogólnej konwersacji
- T = 1.0-1.5: twórcze pisanie, brainstorming
- T > 1.5: coraz bardziej losowy, rzadko użyteczny

Temperatura nie zmienia, które tokeny są możliwe. Zmienia masę prawdopodobieństwa przypisaną do każdego tokena.

### Top-k Sampling

Top-k sampling ogranicza zbiór kandydatów do k tokenów o najwyższych prawdopodobieństwach, następnie renormalizuje i sampluje z tego ograniczonego zbioru.

```
Algorytm:
  1. Oblicz prawdopodobieństwa softmax dla wszystkich V tokenów
  2. Sortuj tokeny według prawdopodobieństwa (malejąco)
  3. Zachowaj tylko top k tokenów
  4. Renormalizuj: p_i' = p_i / sum(p_j dla j w top-k)
  5. Sampluj z renormalizowanego rozkładu

k = 1:  greedy decoding
k = V:  brak filtrowania (standardowy sampling)
k = 40: typowe ustawienie, usuwa długi ogon nieprawdopodobnych tokenów
```

Top-k zapobiega wybieraniu przez model wyjątkowo nieprawdopodobnych tokenów (literówki, nonsens), które istnieją w długim ogonie rozkładu słownictwa. Problem: k jest ustalone niezależnie od kontekstu. Gdy model jest pewny (jeden token ma 95% prawdopodobieństwa), k = 40 wciąż pozwala na 39 alternatyw. Gdy model jest niepewny (prawdopodobieństwo jest rozłożone na 1000 tokenów), k = 40 odcina prawdopodobne opcje.

### Top-p (Nucleus) Sampling

Top-p sampling dynamicznie dostosowuje rozmiar zbioru kandydatów. Zamiast zachowywać ustaloną liczbę tokenów, zachowuje najmniejszy zbiór tokenów, których kumulatywne prawdopodobieństwo przekracza p.

```
Algorytm:
  1. Oblicz prawdopodobieństwa softmax dla wszystkich V tokenów
  2. Sortuj tokeny według prawdopodobieństwa (malejąco)
  3. Znajdź najmniejsze k takie, że suma top-k prawdopodobieństw >= p
  4. Zachowaj tylko te k tokenów
  5. Renormalizuj i sampluj

p = 0.9:  zachowuje tokeny pokrywające 90% masy prawdopodobieństwa
p = 1.0:  brak filtrowania
p = 0.1:  bardzo restrykcyjny, prawie greedy
```

Gdy model jest pewny, nucleus sampling zachowuje mało tokenów (może 2-3). Gdy model jest niepewny, zachowuje wiele (może 200). To adaptacyjne zachowanie jest powodem, dla którego nucleus sampling generalnie produkuje lepszy tekst niż top-k.

**Powszechne kombinacje:**
- Temperatura 0.7 + top-p 0.9: dobre ustawienie ogólnego przeznaczenia
- Temperatura 0.0 (greedy): najlepsze dla zadań deterministycznych
- Temperatura 1.0 + top-k 50: ustawienie z oryginalnego artykułu Fan et al. (2018)

Top-k i top-p mogą być łączone. Zastosuj najpierw top-k, a następnie top-p na pozostałym zbiorze.

### Trik reparametryzacji (Reparameterization Trick) (używany w VAE)

Wariacyjne autoenkodery (VAE) uczą się poprzez kodowanie wejść w rozkład w przestrzeni ukrytej (latent space), samplowanie z tego rozkładu i dekodowanie próbki z powrotem. Problem: nie można propagować wstecznie przez operację samplowania.

```
Standardowe samplowanie (niedyferencjowalne):
  z ~ N(mu, sigma^2)

  Losowość blokuje przepływ gradientu.
  d/d_mu [próbka z N(mu, sigma^2)] = ???
```

Trik reparametryzacji separuje losowość od parametrów:

```
Reparametryzowane samplowanie:
  epsilon ~ N(0, 1)          (ustalony losowy szum, bez parametrów)
  z = mu + sigma * epsilon   (deterministyczna funkcja parametrów)

  Teraz z jest deterministyczną, dyferencjowalną funkcją mu i sigma.
  d(z)/d(mu) = 1
  d(z)/d(sigma) = epsilon

  Gradienty przepływają przez mu i sigma.
```

To działa, ponieważ N(mu, sigma^2) ma ten sam rozkład jak mu + sigma * N(0, 1). Kluczowy wgląd: przenieś losowość do źródła bez parametrów (epsilon), a następnie wyraź próbkę jako dyferencjowalną transformację parametrów.

**W pętli treningowej VAE:**
1. Enkoder wyprowadza mu i log(sigma^2) dla każdego wejścia
2. Sampluj epsilon ~ N(0, 1)
3. Oblicz z = mu + sigma * epsilon
4. Zdekoduj z, aby zrekonstruować wejście
5. Propaguj wstecznie przez kroki 4, 3, 2, 1 (możliwe, ponieważ krok 3 jest dyferencjowalny)

Bez triku reparametryzacji VAE nie mogą być trenowane standardową propagacją wsteczną. Ten jeden wgląd uczynił VAE praktycznymi.

### Gumbel-Softmax (Dyferencjowalne samplowanie kategoryczne)

Trik reparametryzacji działa dla rozkładów ciągłych (gaussowski). Dla dyskretnych rozkładów kategorycznych potrzebujemy innego podejścia. Gumbel-Softmax dostarcza dyferencjowalną aproksymację samplowania kategorycznego.

**Trik Gumbel-Max (niedyferencjowalny):**

```
Aby samplować z rozkładu kategorycznego z log-prawdopodobieństwami log(p_1), ..., log(p_k):
  1. Wylosuj g_i ~ Gumbel(0, 1) dla każdej kategorii
     (g = -log(-log(u)), gdzie u ~ Uniform(0, 1))
  2. Zwróć argmax(log(p_i) + g_i)

To produkuje dokładne próbki kategoryczne.
```

**Gumbel-Softmax (dyferencjowalna aproksymacja):**

```
Zastąp twardy argmax miękkim softmax:
  y_i = exp((log(p_i) + g_i) / tau) / sum(exp((log(p_j) + g_j) / tau))

tau (temperatura) kontroluje aproksymację:
  tau -> 0:  zbliża się do wektora one-hot (twardy kategoryczny)
  tau -> inf: zbliża się do jednostajnego (1/k, 1/k, ..., 1/k)
  tau = 1.0: miękka aproksymacja
```

Gumbel-Softmax produkuje ciągłą relaksację dyskretnej próbki. Wynikiem jest wektor prawdopodobieństwa (miękki one-hot) zamiast twardego one-hot. Gradienty przepływają przez softmax. Podczas przejścia w przód (forward pass) w treningu, można użyć estymatora "straight-through": użyj twardego argmax dla przejścia w przód, ale miękkich gradientów Gumbel-Softmax dla przejścia w tył (backward pass).

**Zastosowania:**
- Dyskretne zmienne ukryte w VAE
- Neural architecture search (wybieranie dyskretnych operacji)
- Mechanizmy hard attention
- Uczenie ze wzmocnieniem z dyskretnymi akcjami

### Stratified Sampling

Standardowy sampling Monte Carlo może przypadkowo zostawiać dziury w przestrzeni próbek. Stratified sampling wymusza równomierne pokrycie poprzez podzielenie przestrzeni na warstwy (strata) i samplowanie z każdej.

```
Standardowy Monte Carlo:
  Wylosuj N punktów jednostajnie z [0, 1]
  Niektóre regiony mogą mieć skupiska, inne dziury

Stratified sampling:
  Podziel [0, 1] na N równych warstw: [0, 1/N), [1/N, 2/N), ..., [(N-1)/N, 1)
  Wylosuj jeden punkt jednostajnie w każdej warstwie
  x_i = (i + u_i) / N   gdzie u_i ~ Uniform(0, 1),  i = 0, ..., N-1
```

Stratified sampling ma zawsze mniejszą lub równą wariancję w porównaniu do standardowego Monte Carlo:

```
Var(stratified) <= Var(standardowy Monte Carlo)

Ulepszenie jest największe, gdy f(x) zmienia się gładko.
Dla funkcji kawałkami stałych, stratified sampling jest dokładny.
```

**Zastosowania:**
- Integracja numeryczna (quasi-Monte Carlo)
- Podziały danych treningowych (zapewnienie balansu klas w każdym foldzie)
- Sampling istotnościowy ze stratyfikacją (łączenie obu technik)
- NeRF (Neural Radiance Fields) używa stratified sampling wzdłuż promieni kamery

### Połączenie z modelami dyfuzyjnymi

Modele dyfuzyjne generują obrazy poprzez proces samplowania. Proces w przód (forward process) dodaje szum gaussowski do obrazu w T krokach, aż staje się czystym szumem. Proces w tył (reverse process) uczy się odszumiać, odzyskując oryginalny obraz krok po kroku.

```
Proces w przód (znany):
  x_t = sqrt(alpha_t) * x_{t-1} + sqrt(1 - alpha_t) * epsilon
  gdzie epsilon ~ N(0, I)

  Po T krokach: x_T ~ N(0, I)  (czysty szum)

Proces w tył (wyuczony):
  x_{t-1} = (1/sqrt(alpha_t)) * (x_t - (1 - alpha_t)/sqrt(1 - alpha_bar_t) * epsilon_theta(x_t, t)) + sigma_t * z
  gdzie z ~ N(0, I)

  Każdy krok odszumiania jest krokiem samplowania.
```

Połączenie z metodami z tej lekcji:
- Każdy krok odszumiania używa triku reparametryzacji (sampluje szum, zastosuj deterministyczną transformację)
- Harmonogram szumu {alpha_t} kontroluje formę wygaszania (annealing) temperatury
- Trening używa estymacji Monte Carlo do aproksymacji ELBO (evidence lower bound)
- Ancestral sampling w modelach dyfuzyjnych jest łańcuchem Markowa (każdy krok zależy tylko od aktualnego stanu)

Cały proces generowania obrazu jest iteracyjnym samplowaniem: zacznij od szumu i na każdym kroku sampluj nieco mniej zaszumioną wersję, warunkowaną na wyuczonym modelu odszumiania.

## Zbuduj to

### Krok 1: Sampling jednostajny i odwrotny CDF

```python
import math
import random

def sample_uniform(a, b):
    return a + (b - a) * random.random()

def sample_exponential_inverse_cdf(lam):
    u = random.random()
    return -math.log(u) / lam
```

Wygeneruj 10 000 próbek wykładniczych i zweryfikuj, że średnia wynosi 1/lambda.

### Krok 2: Sampling odrzucania

```python
def rejection_sample(target_pdf, proposal_sample, proposal_pdf, M):
    while True:
        x = proposal_sample()
        u = random.random()
        if u < target_pdf(x) / (M * proposal_pdf(x)):
            return x
```

Użyj samplingu odrzucania, aby wygenerować próbki z obciętego rozkładu normalnego (truncated normal). Zweryfikuj kształt poprzez histogramowanie próbek.

### Krok 3: Sampling istotnościowy

```python
def importance_sampling_estimate(f, target_pdf, proposal_pdf, proposal_sample, n):
    total = 0
    for _ in range(n):
        x = proposal_sample()
        w = target_pdf(x) / proposal_pdf(x)
        total += f(x) * w
    return total / n
```

Oszacuj E[X^2] pod rozkładem normalnym, używając jednostajnej propozycji. Porównaj z znaną odpowiedzią (mu^2 + sigma^2).

### Krok 4: Estymacja Monte Carlo dla pi

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

### Krok 5: Metropolis-Hastings MCMC

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

Sampluj z rozkładu bimodalnego (mieszanina dwóch rozkładów Gaussa). Zwizualizuj trajektorię łańcucha.

### Krok 6: Gibbs Sampling

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

### Krok 7: Temperature Sampling

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

Pokaż, jak temperatura zmienia rozkład wyjściowy dla zbioru logitów tokenów.

### Krok 8: Top-k i Top-p Sampling

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

### Krok 9: Trik reparametryzacji

```python
def reparam_sample(mu, sigma):
    epsilon = random.gauss(0, 1)
    return mu + sigma * epsilon

def reparam_gradient(mu, sigma, epsilon):
    dz_dmu = 1.0
    dz_dsigma = epsilon
    return dz_dmu, dz_dsigma
```

Zademonstruj, że gradienty przepływają przez reparametryzowaną próbkę, ale nie przez bezpośrednie samplowanie.

### Krok 10: Gumbel-Softmax

```python
def gumbel_sample():
    u = random.random()
    return -math.log(-math.log(u))

def gumbel_softmax(logits, temperature):
    gumbels = [math.log(p) + gumbel_sample() for p in logits]
    return softmax([g / temperature for g in gumbels])
```

Pokaż, jak zmniejszanie temperatury powoduje, że wynik zbliża się do wektora one-hot.

Pełne implementacje z wszystkimi wizualizacjami znajdują się w `code/sampling.py`.

## Użyj tego

Z NumPy i SciPy, wersje produkcyjne:

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

Dla MCMC w dużej skali, użyj dedykowanych bibliotek:
- PyMC: pełne modelowanie bayesowskie z NUTS (adaptive HMC)
- emcee: ensemble MCMC sampler
- NumPyro/JAX: MCMC akcelerowane na GPU

Zbudowałeś to od zera. Teraz wiesz, co robią wywołania bibliotek.

## Ćwiczenia

1. Zaimplementuj sampling odwrotnego CDF dla rozkładu Cauchy'ego. CDF wynosi F(x) = 0.5 + arctan(x)/pi. Wygeneruj 10 000 próbek i narysuj histogram na tle prawdziwego PDF. Zwróć uwagę na ciężkie ogony (heavy tails - wartości ekstremalne, dalekie od centrum).

2. Użyj samplingu odrzucania, aby wygenerować próbki z rozkładu Beta(2, 5), używając propozycji Uniform(0, 1). Narysuj zaakceptowane próbki na tle prawdziwego PDF rozkładu Beta. Jaki jest teoretyczny współczynnik akceptacji?

3. Oszacuj całkę z sin(x) od 0 do pi, używając Monte Carlo z 1 000, 10 000 i 100 000 próbek. Porównaj błąd na każdym poziomie. Zweryfikuj, że błąd skaluje się jak O(1/sqrt(N)).

4. Zaimplementuj Metropolis-Hastings, aby samplować z 2D rozkładu p(x, y) proporcjonalnego do exp(-(x^2 * y^2 + x^2 + y^2 - 8*x - 8*y) / 2). Narysuj próbki i trajektorię łańcucha. Eksperymentuj z różnymi odchyleniami standardowymi propozycji.

5. Zbuduj kompletne demo generowania tekstu: dla słownika 10 słów z logitami, wygeneruj sekwencje 20 tokenów, używając (a) greedy, (b) temperature=0.7, (c) top-k=3, (d) top-p=0.9. Porównaj różnorodność wyników w 5 uruchomieniach.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to faktycznie znaczy |
|------|----------------|----------------------|
| Sampling | "Losowanie wartości" | Generowanie wartości zgodnie z rozkładem prawdopodobieństwa. Mechanizm leżący za całym generatywnym AI |
| Rozkład jednostajny (Uniform distribution) | "Wszystko równie prawdopodobne" | Każda wartość w [a, b] ma równą gęstość prawdopodobieństwa 1/(b-a). Punkt wyjścia dla wszystkich metod samplowania |
| Odwrotny CDF (Inverse CDF) | "Transformacja prawdopodobieństwa" | F_inverse(U) przekształca próbkę jednostajną w próbkę z dowolnego rozkładu o znanym CDF. Dokładny i efektywny |
| Sampling odrzucania (Rejection sampling) | "Proponuj i akceptuj/odrzucaj" | Generuj z prostej propozycji, akceptuj z prawdopodobieństwem proporcjonalnym do stosunku target/proposal. Dokładny, ale marnuje próbki |
| Sampling istotnościowy (Importance sampling) | "Przeważ próbki" | Oszacuj wartości oczekiwane pod p(x), używając próbek z q(x), wagując każdą próbkę przez p(x)/q(x). Kluczowy w PPO w RL |
| Monte Carlo | "Średnia z losowych próbek" | Aproksymuj całki jako średnie z próbek. Błąd O(1/sqrt(N)) niezależnie od wymiaru |
| MCMC | "Losowy spacer, który zbiega" | Konstrukcja łańcucha Markowa, którego rozkład stacjonarny jest celem. Metropolis-Hastings jest fundamentalnym algorytmem |
| Metropolis-Hastings | "Akceptuj pod górę, czasem w dół" | Proponuj ruchy, akceptuj na podstawie stosunku gęstości. Szczegółowy bilans zapewnia zbieżność do rozkładu docelowego |
| Gibbs sampling | "Jedna zmienna na raz" | Aktualizuj każdą zmienną z jej rozkładu warunkowego, trzymając inne ustalone. 100% współczynnik akceptacji |
| Temperatura | "Pokrętło pewności" | Dzieli logity przez T przed softmax. T<1 zaostrza (bardziej pewny), T>1 spłaszcza (bardziej różnorodny) |
| Top-k sampling | "Zachowaj k najlepszych" | Wyzeruj wszystko poza k tokenami o najwyższym prawdopodobieństwie, renormalizuj, sampluj. Ustalony rozmiar zbioru kandydatów |
| Nucleus sampling (top-p) | "Zachowaj te prawdopodobne" | Zachowaj najmniejszy zbiór tokenów, których kumulatywne prawdopodobieństwo przekracza p. Adaptacyjny rozmiar zbioru kandydatów |
| Trik reparametryzacji (Reparameterization trick) | "Przenieś losowość na zewnątrz" | Zapisz z = mu + sigma * epsilon, gdzie epsilon ~ N(0,1). Sprawia, że samplowanie jest dyferencjowalne. Niezbędny dla treningu VAE |
| Gumbel-Softmax | "Miękkie samplowanie kategoryczne" | Dyferencjowalna aproksymacja samplowania kategorycznego, używająca szumu Gumbel + softmax z temperaturą |
| Stratified sampling | "Wymuszone pokrycie" | Podziel przestrzeń próbek na warstwy (strata), sampluj z każdej. Zawsze mniejsza wariancja niż naiwny Monte Carlo |
| Burn-in | "Okres rozgrzewki" | Początkowe próbki MCMC odrzucane, zanim łańcuch osiągnie swój rozkład stacjonarny |
| Szczegółowy bilans (Detailed balance) | "Warunek odwracalności" | p(x) * T(x->y) = p(y) * T(y->x). Wystarczający warunek, by p było rozkładem stacjonarnym łańcucha Markowa |
| Diffusion sampling | "Iteracyjne odszumianie" | Generuj dane, zaczynając od szumu i stosując wyuczone kroki odszumiania. Każdy krok jest warunkową operacją samplowania |

## Dalsza lektura

- [Holbrook (2023): The Metropolis-Hastings Algorithm](https://arxiv.org/abs/2304.07010) - szczegółowy tutorial o podstawach MCMC
- [Jang, Gu, Poole (2017): Categorical Reparameterization with Gumbel-Softmax](https://arxiv.org/abs/1611.01144) - oryginalny artykuł o Gumbel-Softmax
- [Holtzman et al. (2020): The Curious Case of Neural Text Degeneration](https://arxiv.org/abs/1904.09751) - artykuł o nucleus (top-p) sampling
- [Kingma & Welling (2014): Auto-Encoding Variational Bayes](https://arxiv.org/abs/1312.6114) - artykuł o VAE wprowadzający trik reparametryzacji
- [Ho, Jain, Abbeel (2020): Denoising Diffusion Probabilistic Models](https://arxiv.org/abs/2006.11239) - DDPM łączy samplowanie z generowaniem obrazów
