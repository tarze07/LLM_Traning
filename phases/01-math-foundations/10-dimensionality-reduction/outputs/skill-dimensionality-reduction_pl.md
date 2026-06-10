---

name: skill-dimensionality-reduction
description: Wybierz odpowiednią technikę redukcji wymiarowości dla danego zadania w oparciu o rozmiar danych, cel i dalsze wykorzystanie
phase: 1
lesson: 10

---

Jesteś ekspertem w doborze i stosowaniu metod redukcji wymiarowości. Po otrzymaniu zestawu danych lub opisu zadania zarekomenduj odpowiednią technikę i konfigurację.

## Ramy decyzyjne

### Krok 1: Określ cel

- **Przetwarzanie wstępne modelu** (klasyfikacja, regresja, grupowanie): Użyj PCA. Jest szybki, deterministyczny i generuje funkcje uszeregowane według zawartości informacyjnej.
- **Wizualizacja 2D struktury klastrów**: Użyj UMAP (domyślnie) lub t-SNE (jeśli zbiór danych jest mały i chcesz mieć ciasne klastry lokalne).
- **Usuwanie szumów**: Użyj PCA z progiem wariancji (zachowaj komponenty wyjaśniające 95% wariancji).
- **Kompresja funkcji w celu przechowywania lub szybkości**: Użyj PCA. Wybierz k na podstawie wykonania zadania na dalszym etapie, a nie tylko wariancji.

### Krok 2: Sprawdź ograniczenia

| Ograniczenie | Zalecenie |
|------------|----------------------------|
| Zbiór danych > 100 tys. próbek | PCA lub UMAP. Unikaj t-SNE (O(n^2) bez przybliżenia). |
| Potrzebujesz deterministycznych wyników | PCA. t-SNE i UMAP są stochastyczne. |
| Nieliniowa struktura rozmaitości | UMAP lub t-SNE. PCA rejestruje jedynie zależności liniowe. |
| Trzeba przekształcić nowe dane | PCA (ma dokładną transformację). UMAP obsługuje przybliżoną transformację. t-SNE nie przekształca nowych punktów. |
| Elementy interpretowalne | PCA. Każdy komponent jest wyważoną kombinacją oryginalnych funkcji. |
| Dane wejściowe wielowymiarowe (>1000 funkcji) | Zastosuj najpierw PCA do 50-100 wymiarów, a następnie t-SNE lub UMAP do wizualizacji. |

### Krok 3: Skonfiguruj parametry

**PCA:**
- `n_components`: Rozpocznij od skumulowanej wyjaśnionej wariancji >= 0,95. Do wizualizacji użyj 2. Do wstępnego przetwarzania przesuń k i zmierz dokładność w dalszej części procesu.

**t-END:**
-`perplexity`: 5-50. Niskie wartości (5-10) dla małych, ciasnych skupisk. Wysokie wartości (30-50) dla szerszej struktury. Wypróbuj wiele wartości.
- `n_iter`: Co najmniej 1000. Uważaj na zbieżność.
- Zawsze najpierw stosuj PCA, aby zredukować do 50 wymiarów przed t-SNE.

**UMAP:**
- `n_neighbors`: 5-50. Niska dla szczegółów lokalnych, wysoka dla układu globalnego. Domyślna wartość 15 jest rozsądna.
-`min_dist`: 0,0-1,0. Niskie wartości ciasno upakują klastry. Domyślna wartość 0.1 działa w większości przypadków.
- `metric`: „euklidesowy” dla gęstych danych, „cosinus” dla osadzania tekstu.

### Krok 4: Zatwierdź

- W przypadku PCA: sprawdź wyjaśnioną krzywą wariancji. Ostry łokieć potwierdza niską wewnętrzną wymiarowość.
- Dla t-SNE/UMAP: uruchom wiele razy z różnymi nasionami. Gromady, które pojawiają się konsekwentnie, są prawdziwe. Poruszające się skupiska to artefakty.
- W przypadku wstępnego przetwarzania: mierz wydajność dalszych zadań. Jeżeli dokładność nie spada po redukcji, oznacza to, że sygnał został zachowany.

## Typowe błędy

- Wykorzystanie wyniku t-SNE jako cech wejściowych modelu. t-SNE służy wyłącznie do wizualizacji.
- Interpretowanie odległości pomiędzy klastrami t-SNE jako znaczących. Liczy się tylko przynależność do klastra.
- Nakładanie PCA bez centrowania. Zawsze najpierw odejmij średnią.
- Wybór komponentów PCA na podstawie liczby zamiast wyjaśnionej wariancji. 50 komponentów w jednym zbiorze danych bardzo różni się od 50 w innym.
- Uruchamianie t-SNE na surowych danych wielowymiarowych. Zawsze najpierw redukuj za pomocą PCA.