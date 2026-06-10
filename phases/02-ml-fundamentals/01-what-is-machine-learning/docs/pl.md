# Czym jest uczenie maszynowe

> Uczenie maszynowe uczy komputery znajdowania wzorców w danych zamiast ręcznego pisania reguł.

**Typ:** Ucz się
**Języki:** Python
**Wymagania wstępne:** Faza 1 (Podstawy matematyki)
**Czas:** ~45 minut

## Cele nauczania

- Wyjaśnij różnicę pomiędzy uczeniem się pod nadzorem, bez nadzoru i uczeniem się przez wzmacnianie oraz określ, który typ ma zastosowanie w przypadku danego problemu
- Zaimplementuj od podstaw klasyfikator najbliższego centroidu i oceń go w oparciu o losową linię bazową
- Rozróżnij zadania klasyfikacji i regresji i wybierz dla każdego odpowiednią funkcję straty
- Oceń, czy dany problem biznesowy nadaje się do ML lub lepiej rozwiązać za pomocą deterministycznych reguł

## Problem

Chcesz zbudować filtr spamu. Tradycyjne podejście: usiądź i napisz setki reguł. „Jeśli wiadomość e-mail zawiera słowo „DARMOWE PIENIĄDZE”, oznacz ją jako spam. Jeśli zawiera więcej niż 3 wykrzykniki, oznacz ją jako spam.” Spędzasz tygodnie na pisaniu zasad. Następnie spamerzy zmieniają sformułowania. Twoje zasady łamią się. Piszesz więcej zasad. Cykl nigdy się nie kończy.

Uczenie maszynowe odwraca tę sytuację. Zamiast pisać reguły, dajesz komputerowi tysiące e-maili z etykietami („spam” lub „nie spam”) i pozwalasz mu samodzielnie wymyślić reguły. Komputer znajduje wzorce, o których nigdy byś nie pomyślał. Kiedy spamerzy zmieniają taktykę, zamiast przepisywać kod, szkolisz się na nowych danych.

To przejście od „zasad programowania” do „uczenia się na podstawie danych” jest podstawą uczenia maszynowego. Każdy silnik rekomendacji, asystent głosowy, samochód autonomiczny i model językowy działa w ten sposób.

## Koncepcja

### Uczenie się na podstawie danych, a nie reguł

Tradycyjne programowanie i uczenie maszynowe rozwiązują problemy w przeciwnych kierunkach.

```mermaid
flowchart LR
    subgraph Traditional["Traditional Programming"]
        direction LR
        R[Rules] --> P1[Program]
        D1[Data] --> P1
        P1 --> O1[Output]
    end

    subgraph ML["Machine Learning"]
        direction LR
        D2[Data] --> P2[Learning Algorithm]
        O2[Expected Output] --> P2
        P2 --> M[Model / Rules]
    end
```

Programowanie tradycyjne: piszesz zasady. Program stosuje je do danych w celu uzyskania wyników.

Uczenie maszynowe: dostarczasz dane i oczekiwane wyniki. Algorytm odkrywa reguły.

„Model”, który wychodzi ze szkolenia, JEST regułami zakodowanymi jako liczby (wagi, parametry). Uogólnia na podstawie znanych przykładów, aby przewidywać dane, których nigdy nie widział.

### Trzy typy uczenia maszynowego

```mermaid
flowchart TD
    ML[Machine Learning] --> SL[Supervised Learning]
    ML --> UL[Unsupervised Learning]
    ML --> RL[Reinforcement Learning]

    SL --> C[Classification]
    SL --> R[Regression]

    UL --> CL[Clustering]
    UL --> DR[Dimensionality Reduction]

    RL --> PO[Policy Optimization]
    RL --> VL[Value Learning]
```

**Uczenie się nadzorowane**: Masz pary wejście-wyjście. Model uczy się mapować dane wejściowe na wyjścia.
- „Oto 10 000 zdjęć oznaczonych jako kot lub pies. Naucz się je rozróżniać.”
- „Oto cechy domu i ceny. Naucz się przewidywać cenę.”

**Uczenie się bez nadzoru**: Masz tylko dane wejściowe. Brak etykiet. Model sam znajduje strukturę.
- „Oto historie zakupów klientów 10 000. Znajdź naturalne pogrupowania.”
- „Oto 1000 wymiarowych punktów danych. Zmniejsz do 2 wymiarów, zachowując strukturę.”

**Uczenie się przez wzmacnianie**: Agent podejmuje działania w środowisku i otrzymuje nagrody lub kary. Uczy się strategii (polityki) maksymalizacji całkowitej nagrody.
- „Zagraj w tę grę. +1 za wygraną, -1 za przegraną. Wymyśl strategię.”
- „Kontroluj ramię robota. +1 za podniesienie przedmiotu, -0,01 za każdą zmarnowaną sekundę”.

Większość tego, co zbudujesz w praktyce, wykorzystuje uczenie się pod nadzorem. Uczenie się bez nadzoru jest powszechne w przypadku przetwarzania wstępnego i eksploracji. Uczenie się przez wzmacnianie wspomaga sztuczną inteligencję gier, robotykę i RLHF w modelach językowych.

### Poza Wielką Trójką

Trzy powyższe kategorie są jasne, ale ML w świecie rzeczywistym często zaciera granice.

**Uczenie się częściowo nadzorowane** wykorzystuje mały zestaw oznakowanych danych i duży zestaw danych nieoznaczonych. Możesz mieć 100 oznaczonych obrazów medycznych i 100 000 nieoznaczonych. Techniki obejmują:

- **Propagacja etykiet:** Stwórz wykres łączący podobne punkty danych. Etykiety rozprzestrzeniają się od oznaczonych węzłów do nieoznaczonych sąsiadów poprzez graf.
– **Pseudo-etykietowanie:** trenuj model na danych oznaczonych etykietami, używaj go do przewidywania etykiet dla danych nieoznaczonych etykietami, a następnie ponownie ucz się wszystkiego. Model ładuje własny zestaw treningowy.
- **Regularyzacja spójności:** Model powinien dawać tę samą prognozę dla danych wejściowych i lekko zaburzoną wersję tych danych wejściowych. Działa to nawet bez etykiet.

**Uczenie się samonadzorowane** tworzy nadzór na podstawie samych danych. Żadne ludzkie etykiety nie są potrzebne. Model tworzy własne zadanie predykcyjne na podstawie struktury danych.

- **Modelowanie języka maskowanego (BERT):** Ukryj 15% słów w zdaniu, wytrenuj model, aby przewidywał brakujące słowa. „Etykiety” pochodzą z tekstu oryginalnego.
- **Uczenie się kontrastowe (SimCLR):** Zrób zdjęcie i utwórz dwie rozszerzone wersje. Naucz model rozpoznawać, że pochodzą z tego samego obrazu, jednocześnie odróżniając go od rozszerzonych wersji innych obrazów.
- **Przewidywanie następnego tokenu (GPT):** Wytypuj następne słowo, biorąc pod uwagę wszystkie poprzednie słowa. Każdy dokument tekstowy staje się przykładem szkoleniowym.

Nie są to kategorie odrębne od wielkiej trójki. Są to strategie łączące pomysły nadzorowane i nienadzorowane. Samonadzorowane uczenie się jest nadzorowane technicznie (model coś przewiduje), ale etykiety są generowane automatycznie, a nie przez ludzi.

### Klasyfikacja a regresja

Są to dwa główne zadania nadzorowanego uczenia się.

| Aspekt | Klasyfikacja | Regresja |
|--------|-------------------|------------|
| Wyjście | Kategorie dyskretne | Liczby ciągłe |
| Przykład | „Czy ten e-mail jest spamem?” | „Jaka będzie cena domu?” |
| Przestrzeń wyjściowa | {kot, pies, ptak} | Dowolna liczba rzeczywista |
| Funkcja straty | Entropia krzyżowa, dokładność | Średni błąd kwadratowy, MAE |
| Decyzja | Granice między klasami | Krzywa pasująca do danych |

Klasyfikacja odpowiada na pytanie: „Jaka kategoria?” Regresja odpowiada na pytanie „ile?”

Niektóre problemy można ująć w dowolny sposób. Przewidywanie, czy akcje pójdą w górę, czy w dół, to klasyfikacja. Przewidywanie dokładnej ceny to regresja.

### Przebieg pracy z systemem uczenia maszynowego

Każdy projekt uczenia maszynowego przebiega według tego samego potoku, niezależnie od algorytmu.

```mermaid
flowchart LR
    A[Collect Data] --> B[Clean & Explore]
    B --> C[Feature Engineering]
    C --> D[Split Data]
    D --> E[Train Model]
    E --> F[Evaluate]
    F -->|Not good enough| C
    F -->|Good enough| G[Deploy]
    G --> H[Monitor]
    H -->|Performance drops| A
```

**Zbieraj dane**: Zbieraj surowe dane. Więcej danych prawie zawsze oznacza lepiej, ale jakość jest ważniejsza niż ilość.

**Wyczyść i eksploruj**: zarządzaj brakującymi wartościami, usuwaj duplikaty, wizualizuj rozkłady, wykrywaj anomalie. Ten krok często zajmuje 60–80% całkowitego czasu projektu.

**Inżynieria funkcji**: Przekształcaj surowe dane w funkcje, z których może korzystać model. Zamień daty na dni tygodnia. Normalizuj kolumny liczbowe. Zakoduj zmienne jakościowe. Dobre funkcje są ważniejsze niż fantazyjne algorytmy.

**Podziel dane**: Podziel dane na zbiory szkoleniowe, walidacyjne i testowe. Model szkoli się na danych szkoleniowych, dostraja parametry na danych walidacyjnych i raportuje ostateczną wydajność na danych testowych.

**Model pociągowy**: Podaj dane szkoleniowe do algorytmu. Algorytm dostosowuje parametry wewnętrzne, aby zminimalizować funkcję straty.

**Oceń**: Zmierz wydajność na podstawie danych z walidacji/testów. Jeśli wydajność jest nie do zaakceptowania, wróć i wypróbuj inne funkcje, algorytmy lub hiperparametry.

**Wdrożenie**: Wprowadź model do środowiska produkcyjnego, gdzie będzie on dokonywał prognoz na podstawie nowych danych.

**Monitor**: śledzenie wydajności w czasie. Rozkłady danych zmieniają się (dryf danych), a modele ulegają degradacji. Gdy wydajność spadnie, przekwalifikuj się.

### Trening, walidacja i podział testów

To najważniejsza koncepcja, którą początkujący mylą. Musisz ocenić swój model na danych, których nigdy nie widział podczas uczenia. W przeciwnym razie mierzysz zapamiętywanie, a nie uczenie się.

```mermaid
flowchart LR
    subgraph Dataset["Full Dataset (100%)"]
        direction LR
        TR["Training Set (70%)"]
        VA["Validation Set (15%)"]
        TE["Test Set (15%)"]
    end

    TR -->|Train model| M[Model]
    M -->|Tune hyperparameters| VA
    VA -->|Final evaluation| TE
```

| Podziel | Cel | Kiedy jest używany | Typowy rozmiar |
|-------|--------|-----------|------------|
| Szkolenie | Model uczy się na podstawie tych danych | Podczas treningu | 60-80% |
| Walidacja | Dostosuj hiperparametry, porównaj modele | Po każdym biegu treningowym | 10-20% |
| Testuj | Ostateczne, obiektywne oszacowanie wyników | Raz, na samym końcu | 10-20% |

Zestaw testowy jest święty. Patrzysz na to dokładnie raz. Jeśli będziesz stale dostosowywać swój model w oparciu o wyniki testów, efektywnie trenujesz na zestawie testowym, a raportowane liczby są bez znaczenia.

W przypadku małych zbiorów danych użyj k-krotnej walidacji krzyżowej: podziel dane na k części, trenuj na k-1 częściach, zweryfikuj pozostałą część, obróć i uśrednij wyniki.

### Nadmierne dopasowanie a niedostateczne dopasowanie

```mermaid
flowchart LR
    subgraph UF["Underfitting"]
        U1["Model too simple"]
        U2["High bias"]
        U3["Misses patterns"]
    end

    subgraph GF["Good Fit"]
        G1["Right complexity"]
        G2["Balanced"]
        G3["Generalizes well"]
    end

    subgraph OF["Overfitting"]
        O1["Model too complex"]
        O2["High variance"]
        O3["Memorizes noise"]
    end

    UF -->|Increase complexity| GF
    GF -->|Too much complexity| OF
```

**Niedopasowanie**: Model jest zbyt prosty, aby uchwycić wzorce w danych. Linia prosta próbująca dopasować się do zakrzywionej relacji. Błąd w szkoleniu jest wysoki. Błąd testu jest wysoki.

**Przedmierne dopasowanie**: Model jest zbyt złożony i zapamiętuje dane treningowe, w tym szum. Falista krzywa, która przechodzi przez każdy punkt treningowy, ale nie sprawdza się w przypadku nowych danych. Błąd szkolenia jest niski. Błąd testu jest wysoki.

**Dobre dopasowanie**: Model rejestruje rzeczywiste wzory bez zapamiętywania hałasu. Zarówno błąd uczenia, jak i błąd testu są stosunkowo niskie.

Oznaki nadmiernego dopasowania:
- Dokładność szkolenia jest znacznie wyższa niż dokładność walidacji
- Model działa dobrze na danych szkoleniowych, ale słabo na nowych danych
- Dodanie większej ilości danych treningowych poprawia wydajność (model zapamiętywał, a nie uczył się)

Poprawki dotyczące nadmiernego dopasowania:
- Uzyskaj więcej danych treningowych
- Zmniejsz złożoność modelu (mniej parametrów, prostsza architektura)
- Regularyzacja (dodaj karę za duże ciężary)
- Rezygnacja (losowe zerowanie neuronów podczas treningu)
- Wczesne zatrzymanie (przerwanie treningu, gdy błąd walidacji zaczyna rosnąć)

Poprawki dotyczące niedopasowania:
- Użyj bardziej złożonego modelu
- Dodaj więcej funkcji
- Ogranicz regularyzację
- Trenuj dłużej

### Kompromis odchylenia i wariancji

Oto ramy matematyczne opisujące nadmierne i niedostateczne dopasowanie.

**Odchylenie**: Błąd wynikający z błędnych założeń modelu. Model liniowy ma duże obciążenie, gdy prawdziwa zależność jest nieliniowa. Wysokie nastawienie prowadzi do niedopasowania.

**Wariancja**: Błąd wynikający z wrażliwości na małe wahania danych treningowych. Model o dużej wariancji daje bardzo różne przewidywania, gdy jest szkolony na różnych podzbiorach danych. Duża wariancja prowadzi do nadmiernego dopasowania.

| Złożoność modelu | stronniczość | Wariancja | Wynik |
|----------------------|------|----------|--------|
| Za niska (model liniowy dla danych zakrzywionych) | Wysoki | Niski | Niedopasowanie |
| W sam raz | Średni | Średni | Dobre uogólnienie |
| Za wysoka (wielomian stopnia 20 na 10 punktów) | Niski | Wysoki | Nadmierne dopasowanie |

Błąd całkowity = odchylenie^2 + wariancja + nieredukowalny szum

Nie można zredukować nieredukowalnego szumu (jest to losowość samych danych). Chcesz znaleźć optymalny punkt, w którym odchylenie^2 + wariancja jest zminimalizowana.

### Twierdzenie o braku darmowego lunchu

Nie ma jednego algorytmu, który działałby najlepiej w przypadku każdego problemu. Algorytm, który dobrze radzi sobie z jedną klasą problemów, będzie słabo radził sobie z inną. Właśnie dlatego analitycy danych wypróbowują wiele algorytmów i porównują wyniki.

W praktyce wybór zależy od:
- Ile masz danych
- Ile jest funkcji
- Czy zależność jest liniowa czy nieliniowa
- Czy potrzebujesz możliwości interpretacji
- Na ile mocy obliczeniowej możesz sobie pozwolić

### Kiedy NIE używać uczenia maszynowego

ML to potężne narzędzie, ale nie zawsze właściwe. Zanim sięgniesz po dany model, zapytaj, czy faktycznie go potrzebujesz.

**Nie używaj ML, gdy:**

- **Zasady są proste i dobrze zdefiniowane.** Obliczanie podatku, algorytmy sortowania, przeliczanie jednostek. Jeśli potrafisz zapisać logikę w kilku instrukcjach if, model zwiększa złożoność bez żadnych korzyści.
- **Nie masz danych lub masz ich bardzo mało.** ML potrzebuje przykładów, z których może się uczyć. Mając 10 punktów danych, nie można wytrenować niczego znaczącego. Najpierw zbierz dane.
- **Koszt błędu jest katastrofalny i potrzebujesz gwarancji poprawności.** Obliczanie dawek medycznych, kontrola reaktora jądrowego, weryfikacja kryptograficzna. Modele ML są probabilistyczne. Czasem się mylą. Jeśli „czasami źle” jest niedopuszczalne, użyj metod deterministycznych.
- **Tabela przeglądowa lub heurystyka rozwiązuje problem.** Jeśli prosty próg lub tabela obejmuje 99% przypadków, dodanie ML zwiększa koszty utrzymania bez znaczącej poprawy.
- **Nie można wyjaśnić decyzji i wymagane jest jej wyjaśnienie.** Branże regulowane (kredyty, ubezpieczenia, wymiar sprawiedliwości w sprawach karnych) czasami wymagają, aby każda decyzja była w pełni możliwa do wyjaśnienia. Niektóre modele ML można interpretować (regresja liniowa, małe drzewa decyzyjne). Większość nie.
- **Problem zmienia się szybciej, niż możesz się przeszkolić.** Jeśli zasady zmieniają się codziennie, a przekwalifikowanie trwa tydzień, model jest zawsze przestarzały.

Skorzystaj z tego schematu podejmowania decyzji:

```mermaid
flowchart TD
    A["Do you have data?"] -->|No| B["Collect data first or use rules"]
    A -->|Yes| C["Can you write the rules explicitly?"]
    C -->|"Yes, and they are simple"| D["Use rules. Skip ML."]
    C -->|"No, or they are too complex"| E["Is the cost of errors acceptable?"]
    E -->|"No, need guaranteed correctness"| F["Use deterministic methods"]
    E -->|Yes| G["Do you need explainability?"]
    G -->|"Yes, strictly"| H["Use interpretable models only"]
    G -->|"No, or partially"| I["Use ML"]
    I --> J["Do you have enough labeled data?"]
    J -->|Yes| K["Supervised learning"]
    J -->|"Some labels"| L["Semi-supervised learning"]
    J -->|"No labels"| M["Unsupervised or self-supervised"]
```

## Zbuduj to

Kod w `code/ml_intro.py` implementuje od podstaw klasyfikator najbliższego centroidu, czyli najprostszy możliwy algorytm ML. Pokazuje podstawową ideę: uczyć się na podstawie danych, a następnie przewidywać na podstawie nowych danych.

### Krok 1: Najbliższy klasyfikator centroidów od podstaw

Najbliższy klasyfikator centroidów oblicza środek (średnią) każdej klasy w danych szkoleniowych. Aby przewidzieć, przypisuje każdy nowy punkt klasie, której środek jest najbliżej.

```python
class NearestCentroid:
    def fit(self, X, y):
        self.classes = np.unique(y)
        self.centroids = np.array([
            X[y == c].mean(axis=0) for c in self.classes
        ])

    def predict(self, X):
        distances = np.array([
            np.sqrt(((X - c) ** 2).sum(axis=1))
            for c in self.centroids
        ])
        return self.classes[distances.argmin(axis=0)]
```

To jest cały algorytm. Fit oblicza dwa średnie. Przewidywanie oblicza odległości. Bez opadania gradientu, bez iteracji, bez hiperparametrów.

### Krok 2: Trenuj na danych syntetycznych

Generujemy zbiór danych klasyfikacyjnych 2D z dwiema klasami, które nieznacznie się pokrywają. Klasyfikator centroidów rysuje liniową granicę decyzyjną pomiędzy ośrodkami klas.

```python
rng = np.random.RandomState(42)
X_class0 = rng.randn(100, 2) + np.array([1.0, 1.0])
X_class1 = rng.randn(100, 2) + np.array([-1.0, -1.0])
X = np.vstack([X_class0, X_class1])
y = np.array([0] * 100 + [1] * 100)
```

### Krok 3: porównanie z wartością bazową

Każdy model ML należy porównać z trywialną wartością bazową. Tutaj linia bazowa przewiduje losową klasę. Jeśli Twój model ML nie pokonuje losowego zgadywania, coś jest nie tak.

```python
baseline_preds = rng.choice([0, 1], size=len(y_test))
baseline_acc = np.mean(baseline_preds == y_test)
```

Klasyfikator centroidów powinien uzyskać około 90% + dokładność w tym czystym zbiorze danych. Losowa wartość bazowa wynosi około 50%.

### Dlaczego to ma znaczenie

Najbliższy klasyfikator centroidów jest banalnie prosty. Nie ma hiperparametrów, iteracji ani opadania gradientu. Jednak oddaje podstawowy wzorzec ML:

1. **Naucz się** reprezentacji na podstawie danych szkoleniowych (centroidy)
2. **Przewiduj** nowe dane przy użyciu tej reprezentacji (najbliższa odległość)
3. **Oceń** względem wartości bazowej (losowe zgadywanie)

Każdy algorytm ML, od regresji logistycznej po transformatory, opiera się na tym samym trzyetapowym schemacie. Reprezentacja staje się bardziej złożona, ale przepływ pracy pozostaje ten sam.

### Krok 4: Czego nie może zrobić klasyfikator centroidów

Najbliższy klasyfikator centroidu zakłada, że każda klasa tworzy pojedynczą plamkę. Rysuje liniowe granice decyzji. Nie udaje się, gdy:

- Klasy mają wiele skupień (np. cyfrę „1” można zapisać na kilka różnych sposobów)
- Granica decyzji jest nieliniowa (np. jedna klasa zawija się wokół drugiej)
- Obiekty mają bardzo różne skale (odległość jest zdominowana przez obiekt o największej skali)

Te ograniczenia motywują każdy inny algorytm, którego się nauczysz. K-najbliżsi sąsiedzi obsługują wiele klastrów. Drzewa decyzyjne obsługują granice nieliniowe. Skalowanie funkcji rozwiązuje problem skali. Każda lekcja opiera się na ograniczeniach poprzedniej.

## Użyj tego

sklearn udostępnia `NearestCentroid` i generatory danych syntetycznych:

```python
from sklearn.neighbors import NearestCentroid
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split

X, y = make_classification(
    n_samples=500, n_features=2, n_redundant=0,
    n_clusters_per_class=1, random_state=42
)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)

clf = NearestCentroid()
clf.fit(X_train, y_train)
print(f"Accuracy: {clf.score(X_test, y_test):.3f}")
```

## Wyślij to

Ta lekcja generuje `outputs/prompt-ml-problem-framer.md` — monit, który zamienia niejasne problemy biznesowe w konkretne zadania ML. Podaj opis problemu („chcemy zmniejszyć odpływ pracowników” lub „przewiduj popyt na następny kwartał”), a on zidentyfikuje typ uczenia się, zdefiniuje cel prognozy, wylistuje potencjalne cechy, wybierze miernik sukcesu, ustali punkt odniesienia i wskaże pułapki, takie jak wyciek danych lub brak równowagi klas. Użyj go na początku dowolnego projektu ML, aby uniknąć zbudowania niewłaściwej rzeczy.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|----------------------|
| Modelka | „AI” | Funkcja matematyczna z możliwymi do nauczenia się parametrami, która odwzorowuje wejścia na wyjścia |
| Szkolenie | „Nauczanie sztucznej inteligencji” | Uruchamianie algorytmu optymalizacji w celu dostosowania parametrów modelu, aby przewidywania odpowiadały znanym wynikom
| Funkcja | „Kolumna wejściowa” | Mierzalna właściwość danych wykorzystywana przez model do prognozowania |
| Etykieta | „Odpowiedź” | Znane dane wyjściowe dla przykładu szkoleniowego, użyte do obliczenia sygnału błędu |
| Hiperparametr | „Ustawienie, które możesz dostosować” | Parametr ustawiony przed treningiem kontrolujący proces uczenia się (szybkość uczenia się, liczba warstw) |
| Funkcja straty | „Jak błędny jest model” | Funkcja mierząca różnicę między przewidywanymi a rzeczywistymi wynikami, którą uczenie stara się zminimalizować |
| Nadmierne dopasowanie | „Zapamiętał test” | Model nauczył się szumu specyficznego dla treningu zamiast ogólnych wzorców, więc nie radzi sobie z nowymi danymi |
| Niedopasowanie | „Niczego się nie nauczyło” | Model jest zbyt prosty, aby uchwycić rzeczywiste wzorce w danych
| Uogólnienie | „Działa na nowych danych” | Zdolność modelu do dokonywania dokładnych przewidywań na podstawie danych, na których nie był trenowany |
| Walidacja krzyżowa | „Testowanie na różnych fragmentach” | Wielokrotne dzielenie danych na części pociągowe/testowe i uśrednianie wyników, dając bardziej wiarygodne oszacowanie wydajności |
| Regularyzacja | „Utrzymywanie małych ciężarów” | Dodanie warunku kary do funkcji straty, która zniechęca do stosowania zbyt skomplikowanych modeli |
| Dryf danych | „Świat się zmienił” | Rozkład statystyczny napływających danych zmienia się w czasie, pogarszając wydajność modelu |

## Ćwiczenia

1. Weź dowolny zbiór danych (np. Iris, Titanic). Podziel to 70/15/15 na pociąg/walidację/test. Wyjaśnij, dlaczego nie należy dostrajać hiperparametrów na zestawie testowym.
2. Wymień trzy problemy występujące w świecie rzeczywistym. Dla każdego z nich określ, czy jest to klasyfikacja, regresja czy grupowanie oraz czy jest nadzorowany, czy nie.
3. Model uzyskuje 99% dokładności w przypadku danych szkoleniowych i 60% w przypadku danych testowych. Zdiagnozuj problem i wypisz trzy rzeczy, które chciałbyś spróbować naprawić.

## Dalsze czytanie

- [Wprowadzenie do uczenia się statystycznego](https://www.statlearning.com/) - bezpłatny podręcznik obejmujący wszystkie klasyczne metody ML z praktycznymi przykładami
– [Kurs awaryjny Google Machine Learning](https://developers.google.com/machine-learning/crash-course) – zwięzłe wizualne wprowadzenie do koncepcji ML
- [Podręcznik użytkownika Scikit-learn](https://scikit-learn.org/stable/user_guide.html) - praktyczne informacje dotyczące implementacji ML w Pythonie