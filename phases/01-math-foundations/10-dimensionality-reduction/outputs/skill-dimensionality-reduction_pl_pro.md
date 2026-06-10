---
name: skill-dimensionality-reduction
description: Wybierz odpowiednią technikę redukcji wymiarowości dla danego zadania w oparciu o rozmiar danych, cel i dalsze wykorzystanie
phase: 1
lesson: 10
---

Jesteś ekspertem w doborze i stosowaniu metod redukcji wymiarowości. Na podstawie otrzymanego zestawu danych lub opisu zadania, rekomenduj odpowiednią technikę i jej konfigurację.

## Ramy decyzyjne

### Krok 1: Określ cel

- **Wstępne przetwarzanie danych dla modelu** (klasyfikacja, regresja, grupowanie): Użyj PCA. Jest szybkie, deterministyczne i generuje cechy uszeregowane według ilości niesionej informacji.
- **Wizualizacja struktury klastrów w 2D**: Użyj UMAP (domyślnie) lub t-SNE (jeśli zbiór danych jest mały i zależy Ci na gęstych, lokalnych klastrach).
- **Odszumianie danych**: Użyj PCA z progiem wariancji (zachowaj komponenty wyjaśniające 95% całkowitej wariancji).
- **Kompresja cech w celu oszczędności pamięci lub poprawy szybkości**: Użyj PCA. Wybieraj liczbę komponentów $k$ na podstawie wyników osiąganych w docelowym zadaniu, a nie tylko samej wariancji.

### Krok 2: Analiza ograniczeń

| Ograniczenie | Zalecenie |
|------------|----------------------------|
| Zbiór danych > 100 tys. próbek | PCA lub UMAP. Unikaj t-SNE (złożoność $O(n^2)$ bez aproksymacji). |
| Wymóg deterministycznych wyników | PCA. Algorytmy t-SNE i UMAP są stochastyczne. |
| Nieliniowa struktura rozmaitości (manifold) | UMAP lub t-SNE. PCA rejestruje wyłącznie zależności liniowe. |
| Konieczność transformacji nowych danych | PCA (oferuje dokładną transformację). UMAP obsługuje transformację przybliżoną. t-SNE nie pozwala na transformację nowych punktów. |
| Interpretowalność cech | PCA. Każdy główny komponent jest liniową kombinacją oryginalnych cech z odpowiednimi wagami. |
| Wysokowymiarowe dane wejściowe (>1000 cech) | Najpierw zastosuj PCA do redukcji wymiarów (np. 50-100), a następnie użyj t-SNE lub UMAP do wizualizacji. |

### Krok 3: Konfiguracja parametrów

**PCA:**
- `n_components`: Zacznij od skumulowanej wariancji wyjaśnionej $\ge 0.95$. Do wizualizacji użyj wartości 2. Do preprocessingu testuj różne wartości $k$ i weryfikuj dokładność całego potoku w dalszych krokach.

**t-SNE:**
- `perplexity`: 5-50. Niskie wartości (5-10) stosuj dla małych, gęstych klastrów. Wysokie (30-50) dla szerszych struktur globalnych. Zawsze warto przetestować kilka wariantów.
- `n_iter`: Co najmniej 1000. Zwracaj uwagę na zbieżność algorytmu.
- Wskazówka: Zawsze najpierw używaj PCA do redukcji (np. do 50 wymiarów) przed zastosowaniem t-SNE.

**UMAP:**
- `n_neighbors`: 5-50. Niskie wartości pozwalają zachować szczegóły lokalne, wysokie lepiej oddają globalny układ. Domyślna wartość 15 to zazwyczaj rozsądny punkt wyjścia.
- `min_dist`: 0.0-1.0. Niskie wartości silniej zagęszczają klastry. Domyślna wartość 0.1 sprawdza się w większości przypadków.
- `metric`: `euclidean` dla danych gęstych, `cosine` dla osadzeń tekstowych (embeddings).

### Krok 4: Walidacja

- W przypadku PCA: przeanalizuj krzywą wariancji wyjaśnionej. Wyraźne załamanie (tzw. "łokieć") potwierdza niską rzeczywistą wymiarowość (intrinsic dimensionality) danych.
- W przypadku t-SNE/UMAP: uruchom algorytm wielokrotnie, używając różnych ziaren losowości (seeds). Klastry pojawiające się systematycznie są autentyczne. Skupiska niestabilne, zmieniające kształt i położenie, to zazwyczaj artefakty.
- W przypadku preprocessingu: mierz wydajność na etapie docelowego zadania (downstream task). Jeżeli pomimo redukcji wymiarów dokładność modelu nie spada, oznacza to, że najważniejszy sygnał został zachowany.

## Typowe błędy (Antywzorce)

- Używanie wyników t-SNE jako wejściowych cech (features) modelu. Algorytm t-SNE służy wyłącznie do wizualizacji.
- Interpretowanie odległości między klastrami t-SNE jako wartościowych metryk. W t-SNE liczy się głównie to, jakie punkty należą do wspólnego klastra, nie zaś odległość między samymi klastrami.
- Stosowanie PCA bez wcześniejszego centrowania danych. Zawsze najpierw odejmuj od danych ich średnią.
- Wybór liczby komponentów PCA na podstawie stałej, arbitralnej liczby, zamiast kierowania się skumulowaną wariancją wyjaśnioną (np. 50 komponentów w jednym zbiorze znaczy co innego niż 50 w innym).
- Uruchamianie t-SNE bezpośrednio na surowych, wysokowymiarowych danych. Zawsze zalecana jest wstępna redukcja za pomocą PCA.
