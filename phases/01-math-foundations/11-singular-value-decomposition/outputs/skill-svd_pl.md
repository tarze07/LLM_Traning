---

name: skill-svd
description: Zastosuj SVD do rzeczywistych problemów, w tym kompresji, odszumiania, zaleceń i rozwiązywania metodą najmniejszych kwadratów
phase: 1
lesson: 11

---

Jesteś ekspertem w stosowaniu rozkładu wartości osobliwych do praktycznych problemów inżynierskich. Jeśli otrzymasz zadanie obejmujące macierze, kompresję danych, szum, brakujące dane lub systemy liniowe, określ, czy SVD jest właściwym narzędziem i jak go zastosować.

## Ramy decyzyjne

### Krok 1: Zidentyfikuj typ problemu

- **Kompresja danych/redukcja wymiarów**: Użyj obciętego SVD. Zachowaj górne k wartości osobliwych. Wybierz k według progu energii (częstym celem jest 95%) lub wykonania kolejnego zadania.
- **Redukcja szumów**: Oblicz pełne SVD. Poszukaj luki w spektrum wartości osobliwych. Obetnij poniżej szczeliny. Szczelina oddziela sygnał od szumu.
- **Brakujące dane / zalecenia**: Uzupełnij brakujące wpisy (średnie wierszy lub zera), oblicz SVD, zrekonstruuj z niską rangą. W środowisku produkcyjnym użyj ALS lub przyrostowego SVD, które natywnie obsługują brakujące dane.
- **Metoda najmniejszych kwadratów / pseudoodwrotność**: Oblicz SVD. Odwracanie niezerowych wartości osobliwych. Pomnóż V Sigma+ U^T przez wektor docelowy. Bardziej stabilne niż normalne równania.
- **Podobieństwo tekstu / modelowanie tematu**: Zbuduj matrycę termin-dokument. Zastosuj SVD (to jest LSA/LSI). Dokumenty projektu i warunki w przestrzeni niskiej rangi. Do porównań użyj podobieństwa cosinus.
- **Numeryczne określenie rangi**: Oblicz SVD. Zliczaj pojedyncze wartości powyżej progu (w odniesieniu do największej). Jest to bardziej niezawodne niż redukcja rzędów.
- **Obliczenie normy matrycowej**: Norma widmowa = największa wartość osobliwa. Norma Frobeniusa = sqrt(suma kwadratów wartości osobliwych). Norma jądrowa = suma wartości osobliwych.
- **Numer stanu**: sigma_max / sigma_min. Informuje o wrażliwości systemu na zakłócenia.

### Krok 2: Wybierz odpowiedni wariant

| Sytuacja | Metoda | Dlaczego |
|----------|--------|-----|
| Gęsta matryca, potrzebny pełny rozkład | `np.linalg.svd(A)`/`svd(A)` w Julii | Algorytm standardowy, stabilny numerycznie |
| Potrzebne są tylko najlepsze komponenty k | `scipy.sparse.linalg.svds(A, k)` | Szybszy niż pełny SVD, gdy k jest małe |
| Rzadka macierz | `scipy.sparse.linalg.svds` | Skutecznie obsługuje rzadkie przechowywanie |
| Dane strumieniowe | Przyrostowy SVD / online SVD | Aktualizuje dekompozycję bez ponownego obliczania od zera |
| Brakujące dane (zalecenia) | ALS, Funk SVD lub NMF | Standardowy SVD wymaga pełnej matrycy |
| Bardzo duża macierz (miliony wierszy) | Randomizowany SVD (`sklearn.utils.extmath.randomized_svd`) | O(mn log k) zamiast O(mn min(m,n)) |
| PCA w sprawie danych skupionych | SVD wycentrowanej matrycy danych | Odpowiednik rozkładu własnego kowariancji, ale bardziej stabilny |

### Krok 3: Wybierz rangę k

- **Próg energii**: Oblicz skumulowaną energię = suma(sigma_1^2 ... sigma_k^2) / suma(wszystkie sigma^2). Zatrzymaj, gdy energia przekroczy 0,95 (lub 0,99 w przypadku zadań o wysokiej wierności).
- **Wykrywanie luk**: Wykreśl wartości osobliwe. Poszukaj ostrego spadku. Szczelina wskazuje granicę pomiędzy sygnałem a szumem.
- **Weryfikacja krzyżowa**: W przypadku dalszych zadań należy przeszukać k i zmierzyć wydajność zatrzymanych danych.
- **Metoda łokcia**: Błąd rekonstrukcji wykresu w funkcji k. Łokieć to miejsce, w którym dodawanie kolejnych komponentów przestaje pomagać.
- **Wiedza dziedzinowa**: Jeśli wiesz, że dane mają d czynników bazowych, użyj k = d.

### Krok 4: Zweryfikuj wyniki

- **Błąd rekonstrukcji**: Oblicz ||A - A_k|| / ||A||. Powinien być mały, jeśli obcięcie ma znaczenie.
- **Wyjaśniona wariancja**: W przypadku PCA/kompresji należy podać ułamek całkowitej wychwyconej wariancji (energii).
- **Wydajność zadania na dalszym etapie**: Jeśli SVD jest etapem przetwarzania wstępnego, zmierz metrykę od początku do końca.
- **Oględziny wizualne**: W przypadku obrazów porównaj wizualnie oryginał i rekonstrukcję. Aby uzyskać rekomendacje, porównaj prognozy ze znanymi ocenami.

## Typowe błędy

- Obliczanie SVD poprzez rozkład własny A^T A. To podnosi liczbę warunku do kwadratu i traci precyzję numeryczną. Użyj dedykowanej procedury SVD.
- Korzystanie z pełnego SVD, gdy potrzebnych jest tylko k górnych komponentów. W przypadku dużych macierzy użyj skróconego lub randomizowanego SVD.
- Zastosowanie SVD bezpośrednio do matrycy z brakującymi wpisami. Standardowy SVD wymaga pełnej matrycy. Zamiast tego użyj metod uzupełniania macierzy (ALS, Funk SVD).
- Ignorowanie centrowania. W przypadku PCA dane należy wyśrodkować (odjąć średnią) przed SVD. Bez centrowania pierwszy składnik rejestruje średnią, a nie wariancję.
- Nadmierne obcięcie. Jeśli zachowasz zbyt mało wartości osobliwych, utracisz sygnał. Jeśli zatrzymasz ich za dużo, utrzymasz hałas. Użyj progów energetycznych lub weryfikacji krzyżowej.
- Mylenie SVD z rozkładem własnym. SVD działa na dowolnej matrycy (dowolny kształt, dowolna ranga). Rozkład własny wymaga macierzy kwadratowej z pełnym zestawem wektorów własnych. Dla symetrycznych dodatnich macierzy półokreślonych są one takie same.

## Wzorce kodu

### Szybka kompresja
```python
U, S, Vt = np.linalg.svd(A, full_matrices=False)
k = np.searchsorted(np.cumsum(S**2) / np.sum(S**2), 0.95) + 1
A_compressed = U[:, :k] @ np.diag(S[:k]) @ Vt[:k, :]
```

### Pseudoodwrotność najmniejszych kwadratów
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

### PCA na dużą skalę
```python
from sklearn.utils.extmath import randomized_svd
U, S, Vt = randomized_svd(X_centered, n_components=50, random_state=42)
explained_variance = S**2 / (n_samples - 1)
```

## Kiedy NIE używać SVD

- Matryca jest bardzo rzadka i potrzeba tylko kilku elementów. Użyj bezpośrednio rzadkich rozwiązań własnych.
- Potrzebujesz czynników nieujemnych (modelowanie tematyczne, rozmieszanie widmowe). Zamiast tego użyj NMF.
- Dane mają silną nieliniową strukturę, której nie można uchwycić metodami liniowymi. Użyj autoenkoderów lub uczenia się wielorakiego.
- Potrzebujesz aktualizacji danych przesyłanych strumieniowo w czasie rzeczywistym, a matryca stale się zmienia. Użyj przyrostowych/online SVD lub metod przybliżonych.
- Matryca mieści się w pamięci, ale jest tak duża, że ​​nawet losowy SVD jest zbyt wolny. Rozważ metody szkicowania lub podejścia oparte na próbkowaniu.

## Koszt obliczeniowy

| Metoda | Czas | Przestrzeń |
|--------|------|-------|
| Pełne SVD macierzy m x n | O(mnmin(m,n)) | O(mn) |
| Obcięty SVD (na górze k) | O(mnk) | O((m+n)k) |
| Randomizowany SVD (górne k) | O(mnlog k) | O((m+n)k) |
| Iteracja mocy (1 wektor) | O(mn * iters) | O(m+n) |

Dla matrycy 10000 x 5000:
- Pełny SVD: ~250 miliardów operacji
- Obcięty SVD (k=50): ~2,5 miliarda operacji
- Randomizowane SVD (k=50): ~500 milionów operacji

Wybierz metodę odpowiadającą Twoim wymaganiom dotyczącym skali i dokładności.