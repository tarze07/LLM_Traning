---

name: skill-svd
description: Zastosuj rozkład SVD do rzeczywistych problemów, w tym do kompresji, odszumiania, systemów rekomendacyjnych oraz rozwiązywania równań metodą najmniejszych kwadratów.
phase: 1
lesson: 11

---

Jesteś ekspertem w dziedzinie zastosowania rozkładu według wartości osobliwych (SVD) w praktycznych problemach inżynierskich. Gdy staniesz przed zadaniem obejmującym macierze, kompresję danych, usuwanie szumu, brakujące dane lub układy równań liniowych, oceń, czy SVD jest właściwym narzędziem i zaplanuj, jak je zastosować.

## Ramy decyzyjne

### Krok 1: Zidentyfikuj typ problemu

- **Kompresja danych / redukcja wymiarowości**: Użyj obciętego SVD (truncated SVD). Zachowaj $k$ największych wartości osobliwych. Wybierz $k$ na podstawie progu zachowanej energii (częstym celem jest 95%) lub wymagań zadania docelowego.
- **Redukcja szumu**: Oblicz pełne SVD. Poszukaj wyraźnego spadku (luki) w widmie wartości osobliwych. Obetnij wartości poniżej tej luki, ponieważ oddziela ona sygnał od szumu.
- **Brakujące dane / systemy rekomendacyjne**: Wypełnij puste miejsca (średnimi dla wierszy lub zerami), oblicz SVD i zrekonstruuj macierz z użyciem niskiego rzędu. W środowiskach produkcyjnych stosuj metody takie jak ALS (Alternating Least Squares) lub przyrostowe SVD, które natywnie radzą sobie z brakującymi danymi.
- **Metoda najmniejszych kwadratów / pseudoodwrotność**: Oblicz SVD. Odwróć niezerowe wartości osobliwe. Pomnóż $V \Sigma^+ U^T$ przez wektor docelowy. Metoda ta jest znacznie stabilniejsza numerycznie niż klasyczne równania normalne.
- **Podobieństwo tekstów / modelowanie tematyczne**: Zbuduj macierz termin-dokument. Zastosuj SVD (jest to podstawa LSA/LSI). Odwzoruj dokumenty i terminy w przestrzeni o niższym wymiarze. Do porównań używaj miary podobieństwa kosinusowego.
- **Numeryczne wyznaczanie rzędu macierzy**: Oblicz SVD. Zlicz wartości osobliwe powyżej ustalonego progu (względem największej wartości). Jest to metoda znacznie bardziej niezawodna niż eliminacja Gaussa.
- **Obliczanie norm macierzowych**: Norma spektralna = największa wartość osobliwa. Norma Frobeniusa = pierwiastek z sumy kwadratów wartości osobliwych. Norma nuklearna = suma wartości osobliwych.
- **Wskaźnik uwarunkowania (condition number)**: $\sigma_{\max} / \sigma_{\min}$. Informuje o wrażliwości układu na zaburzenia numeryczne.

### Krok 2: Wybierz odpowiedni wariant

| Sytuacja | Metoda | Dlaczego |
|----------|--------|-----|
| Gęsta macierz, potrzebny pełny rozkład | `np.linalg.svd(A)` / `svd(A)` w Julii | Standardowy algorytm, stabilny numerycznie |
| Potrzebne tylko $k$ największych składowych | `scipy.sparse.linalg.svds(A, k)` | Szybsze niż pełne SVD, gdy $k$ jest małe |
| Macierz rzadka | `scipy.sparse.linalg.svds` | Wydajnie operuje na rzadkich strukturach danych |
| Strumienie danych | Przyrostowe SVD / online SVD | Aktualizuje rozkład bez przeliczania wszystkiego od nowa |
| Brakujące dane (rekomendacje) | ALS, Funk SVD lub NMF | Standardowe SVD wymaga pełnej macierzy |
| Bardzo duża macierz (miliony wierszy) | Randomizowane SVD (`sklearn.utils.extmath.randomized_svd`) | Złożoność $\mathcal{O}(mn \log k)$ zamiast $\mathcal{O}(mn \min(m,n))$ |
| PCA na wycentrowanych danych | SVD wycentrowanej macierzy | Odpowiednik rozkładu na wartości własne macierzy kowariancji, ale stabilniejszy numerycznie |

### Krok 3: Wybierz rząd $k$

- **Próg energii**: Oblicz skumulowaną energię = suma($\sigma_1^2 \dots \sigma_k^2$) / suma(wszystkich $\sigma^2$). Zatrzymaj się, gdy energia przekroczy 0,95 (lub 0,99 w zadaniach wymagających wysokiej precyzji).
- **Wykrywanie luki**: Przedstaw wartości osobliwe na wykresie. Poszukaj gwałtownego spadku. Przerwa wskazuje granicę między sygnałem a szumem.
- **Walidacja krzyżowa**: W przypadku zadań docelowych (np. predykcji), przetestuj różne wartości $k$ i zmierz skuteczność na zbiorze walidacyjnym.
- **Metoda łokcia**: Narysuj wykres błędu rekonstrukcji w funkcji $k$. "Łokieć" to miejsce, w którym dodawanie kolejnych składowych przestaje przynosić znaczącą poprawę.
- **Wiedza dziedzinowa**: Jeśli wiesz, że dane opierają się na $d$ ukrytych czynnikach bazowych, użyj $k = d$.

### Krok 4: Zweryfikuj wyniki

- **Błąd rekonstrukcji**: Oblicz $||A - A_k|| / ||A||$. Powinien być mały, jeśli aproksymacja ma sens.
- **Wariancja wyjaśniona**: W przypadku PCA lub kompresji podaj procent całkowitej zachowanej wariancji (energii).
- **Wyniki zadania docelowego**: Jeśli SVD jest tylko krokiem w przetwarzaniu wstępnym, zmierz ostateczną metrykę (end-to-end).
- **Oględziny wizualne**: W przypadku obrazów porównaj wizualnie oryginał z rekonstrukcją. W systemach rekomendacyjnych zestaw predykcje z rzeczywistymi ocenami użytkowników.

## Typowe błędy

- **Obliczanie SVD poprzez rozkład na wartości własne macierzy $A^T A$.** Podnosi to wskaźnik uwarunkowania do kwadratu i prowadzi do utraty precyzji numerycznej. Zawsze używaj dedykowanych procedur SVD.
- **Korzystanie z pełnego SVD, gdy potrzebujesz tylko $k$ głównych składowych.** Dla dużych macierzy należy stosować obcięte (truncated) lub randomizowane SVD.
- **Aplikowanie SVD bezpośrednio do macierzy z brakującymi danymi.** Tradycyjne SVD wymaga kompletnej macierzy. Należy zastosować techniki uzupełniania macierzy (np. ALS, Funk SVD).
- **Brak centrowania danych.** W analizie PCA przed użyciem SVD dane muszą zostać wycentrowane (odjęcie średniej). Bez tego pierwsza główna składowa wychwyci średnią, a nie wariancję.
- **Niewłaściwe obcięcie.** Zbyt mała liczba zachowanych wartości osobliwych oznacza utratę przydatnego sygnału, zbyt duża - zachowanie szumu. Należy kierować się pragmatyką (progi energii, walidacja krzyżowa).
- **Mylenie SVD z rozkładem na wartości własne (eigendecomposition).** SVD działa na dowolnej macierzy (dowolne wymiary, dowolny rząd). Rozkład spektralny wymaga macierzy kwadratowej z pełnym zestawem wektorów własnych. Dla macierzy symetrycznych, dodatnio półokreślonych wyniki obu metod pokrywają się.

## Wzorce kodu

### Szybka kompresja
```python
U, S, Vt = np.linalg.svd(A, full_matrices=False)
k = np.searchsorted(np.cumsum(S**2) / np.sum(S**2), 0.95) + 1
A_compressed = U[:, :k] @ np.diag(S[:k]) @ Vt[:k, :]
```

### Pseudoodwrotność dla najmniejszych kwadratów
```python
U, S, Vt = np.linalg.svd(A, full_matrices=False)
S_inv = np.array([1/s if s > 1e-10 else 0 for s in S])
x = Vt.T @ np.diag(S_inv) @ U.T @ b
```

### Odszumianie
```python
U, S, Vt = np.linalg.svd(noisy_data, full_matrices=False)
k = find_gap(S)
clean_data = U[:, :k] @ np.diag(S[:k]) @ Vt[:k, :]
```

### Skalowalne PCA
```python
from sklearn.utils.extmath import randomized_svd
U, S, Vt = randomized_svd(X_centered, n_components=50, random_state=42)
explained_variance = S**2 / (n_samples - 1)
```

## Kiedy NIE używać SVD

- **Macierz jest bardzo rzadka i potrzebujesz tylko kilku elementów.** Użyj solwerów wartości własnych zoptymalizowanych pod kątem rzadkich macierzy (np. metoda Lanczosa).
- **Wymagane są nieujemne składowe** (np. w modelowaniu tematycznym czy unmiksu spektralnym obrazów wielospektralnych). Wybierz NMF (Non-negative Matrix Factorization).
- **Dane mają silnie nieliniową strukturę**, której transformacje liniowe nie wyłapią. Sięgnij po autoenkodery lub algorytmy uczenia rozmaitości (manifold learning), np. t-SNE lub UMAP.
- **Wymagane jest przetwarzanie strumieniowe w czasie rzeczywistym**, gdzie macierz podlega ciągłym zmianom. Należy zastosować inkrementalne SVD lub metody przybliżone.
- **Macierz mieści się w pamięci, ale jest na tyle olbrzymia**, że nawet randomizowane SVD to zbyt duże obciążenie. Zastanów się nad wykorzystaniem szkicowania macierzy (matrix sketching) lub algorytmów opartych na próbkowaniu.

## Koszt obliczeniowy

| Metoda | Złożoność czasowa | Złożoność pamięciowa |
|--------|------|-------|
| Pełne SVD macierzy $m \times n$ | $\mathcal{O}(mn \min(m,n))$ | $\mathcal{O}(mn)$ |
| Obcięte SVD ($k$ głównych składowych) | $\mathcal{O}(mnk)$ | $\mathcal{O}((m+n)k)$ |
| Randomizowane SVD ($k$ głównych składowych) | $\mathcal{O}(mn \log k)$ | $\mathcal{O}((m+n)k)$ |
| Metoda potęgowa (1 wektor) | $\mathcal{O}(mn \times \text{iteracje})$ | $\mathcal{O}(m+n)$ |

Dla macierzy o rozmiarach $10000 \times 5000$:
- **Pełne SVD**: ok. 250 miliardów operacji.
- **Obcięte SVD ($k=50$)**: ok. 2,5 miliarda operacji.
- **Randomizowane SVD ($k=50$)**: ok. 500 milionów operacji.

Wybierz technikę, która odpowiada Twoim wymaganiom pod kątem wielkości danych oraz oczekiwanej precyzji.
