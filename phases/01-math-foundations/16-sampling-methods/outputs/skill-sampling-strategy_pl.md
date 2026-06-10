---

name: skill-sampling-strategy
description: Wybierz właściwą metodę próbkowania na potrzeby generowania, szacowania lub wnioskowania
version: 1.0.0
phase: 1
lesson: 16
tags: [sampling, mcmc, generation]

---

# Wybór strategii próbkowania

Jak wybrać właściwą metodę próbkowania do generowania tekstu, wnioskowania bayesowskiego, estymacji Monte Carlo i uczenia.

## Lista kontrolna decyzji

1. Czy generujesz wynik (tekst, obrazy) czy szacujesz ilość (całka, oczekiwanie)?
2. Czy możesz próbkować bezpośrednio z docelowej dystrybucji, czy tylko ocenić jej gęstość?
3. Czy rozkład docelowy jest dyskretny czy ciągły?
4. Jaki wymiar ma przestrzeń próbki? Niski (< 5), medium (5-100), or high (> 100)?
5. Czy potrzebujesz próbek dokładnych czy przybliżonych?
6. Czy podczas pobierania próbek potrzebne są gradienty?

## Kiedy używać poszczególnych metod

| Metoda | Kiedy używać | Złożoność | Dokładny? |
|---|---|---|---|
| Bezpośrednie pobieranie próbek | Masz CDF lub możesz użyć funkcji bibliotecznej | O(1) na próbkę | Tak |
| Odwrotna CDF | Znana odwrotność CDF w postaci zamkniętej (wykładnicza, Cauchy'ego) | O(1) na próbkę | Tak |
| Box-Muller | Potrzebujesz normalnych próbek bez biblioteki | O(1) na próbkę | Tak |
| Próbkowanie odrzucone | Potrafi ocenić docelowy plik PDF, niski wymiar (1-3) | O(1/akceptacja) na próbkę | Tak |
| Próbkowanie znaczenia | Potrzebujesz oczekiwań, a nie pojedynczych próbek | O(n) dla n próbek | Przybliżone |
| Próbkowanie warstwowe | Estymacja Monte Carlo, wymagana jest mniejsza wariancja | O(n) dla n próbek | Przybliżone |
| Metropolis-Hastings | Wielowymiarowy, może ocenić nieznormalizowaną gęstość | O(1) na stopień + wypalenie | Asymptotycznie |
| Próbkowanie Gibbsa | Może pobierać próbki z każdego rozkładu warunkowego | O(d) na pełne przeciągnięcie | Asymptotycznie |
| HMC/NAKRĘTKI | Wysokowymiarowa ciągła, gładka gęstość | O(L * d) na krok | Asymptotycznie |
| Próbkowanie temperatury | Generowanie tekstu LLM, kontrola kreatywności | O(V) dla słownictwa o rozmiarze V | Nie dotyczy |
| Próbkowanie top-k | Generowanie LLM, usuń mało prawdopodobne tokeny | O(V log k) | Nie dotyczy |
| Top-p (jądro) | Generacja LLM, adaptacyjny zestaw kandydatów | O(Vlog V) | Nie dotyczy |
| Reparametryzacja | Potrzebujesz gradientów poprzez próbkowanie gaussowskie (VAE) | O(d) | Tak |
| Gumbel-Softmax | Potrzebujesz gradientów poprzez próbkowanie kategoryczne | O(k) dla k klas | Przybliżone |

## Ustawienia generowania LLM

| Przypadek użycia | Temperatura | Do góry | Top-k | Notatki |
|---|---|---|---|---|
| Pytania i odpowiedzi oparte na faktach | 0,0 (chciwy) | -- | -- | Deterministyczny, bez losowości |
| Generowanie kodu | 0,2-0,5 | 0,9 | -- | Niska kreatywność, wysoka spójność |
| Czat ogólny | 0,7 | 0,9 | -- | Zrównoważony |
| Twórcze pisanie | 0,9-1,2 | 0,95 | -- | Większa różnorodność |
| Burza mózgów | 1,0-1,5 | 0,95 | -- | Maksymalna różnorodność, może stracić spójność |

Można łączyć temperaturę i top-p. Najpierw zastosuj temperaturę (logity skali), a następnie zastosuj filtrowanie top-p.

## Wybór metody MCMC

| Nieruchomość | Metropolis-Hastings | Gibbsa | HMC/NAKRĘTKI |
|---|---|---|---|
| Wymiar | Dowolny | Dowolny (najlepszy < 100) | High (100+) |
| Requires conditionals | No | Yes | No |
| Requires gradient | No | No | Yes |
| Acceptance rate | Tune to ~23% | Always 100% | Tune to ~65% |
| Correlation | High (random walk) | Moderate | Low |
| Burn-in | Long | Moderate | Short |
| Best for | Exploration, simple models | Conjugate models, Bayesian networks | Continuous posteriors, deep probabilistic models |

## Common mistakes

- Using rejection sampling in high dimensions. Acceptance rate drops exponentially with dimension. Above 5 dimensions, switch to MCMC.
- Setting MCMC proposal variance too high or too low. Too high: most proposals rejected, chain stuck. Too low: all proposals accepted, chain moves slowly. Target ~23% acceptance for random walk MH.
- Forgetting burn-in. The first N samples from MCMC are biased by the starting point. Discard at least 1000 steps (or more for complex distributions).
- Using importance sampling with a proposal very different from the target. A few samples get enormous weights, making the estimate unreliable. Monitor the effective sample size: ESS = (sum w_i)^2 / sum(w_i^2).
- Using temperature > 0 do zadań wymagających deterministycznych wyników (np. klasyfikacja, ekstrakcja strukturalna). Zamiast tego użyj wyszukiwania zachłannego (T=0) lub wyszukiwania belek.
- Nie łączenie top-p z temperaturą. Sama temperatura nie usuwa znaczników śmieci z długiego ogona. Top-p tak.
- Propagacja wsteczna poprzez standardową operację próbkowania. Użyj sztuczki z reparametryzacją dla wartości ciągłych (gaussowskich) i Gumbel-Softmax dla dyskretnych (kategorycznych).

## Skrócona instrukcja: techniki redukcji wariancji

| Technika | Jak to działa | Redukcja wariancji |
|---|---|---|
| Próbkowanie warstwowe | Podziel przestrzeń na warstwy, wypróbuj każdą | Zawsze <= standardowe MC |
| Zmienne antytetyczne | Użyj zarówno U, jak i 1-U | Działa dla funkcji monotonicznych |
| Kontrola jest zmienna | Odejmij znaną zmienną średnią | Proporcjonalne do korelacji |
| Próbkowanie znaczenia | Ponownie zważ próbki z lepszej propozycji | Zależy od jakości propozycji |
| Łaciński hipersześcian | Stratyfikuj każdy wymiar niezależnie | Lepsze niż warstwowe w wysokim d |