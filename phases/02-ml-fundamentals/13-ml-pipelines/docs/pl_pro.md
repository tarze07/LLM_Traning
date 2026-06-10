# Potoki Uczenia Maszynowego (ML Pipelines)

> Sam model nie jest produktem. Produktem jest potok przetwarzania (pipeline). Potok obejmuje wszystkie etapy – od surowych danych po udostępnione prognozy – i każdy jego element musi być w pełni odtwarzalny.

**Typ:** Kompilacja
**Język:** Python
**Wymagania wstępne:** Faza 2, Lekcja 12 (Strojenie hiperparametrów)
**Czas:** ~120 minut

## Cele nauczania

- Zbudowanie od podstaw potoku uczenia maszynowego (ML pipeline), integrującego uzupełnianie braków, skalowanie, kodowanie i uczenie modelu w jeden spójny, odtwarzalny obiekt.
- Identyfikacja scenariuszy powstawania "wycieku danych" (data leakage) oraz zrozumienie mechanizmów potoku zapobiegających temu zjawisku, m.in. poprzez dopasowywanie transformatorów wyłącznie do danych treningowych.
- Skonstruowanie obiekty `ColumnTransformer` służącego do aplikowania zróżnicowanych technik preprocessingu względem zmiennych numerycznych i kategorycznych.
- Nabycie kompetencji w zakresie serializacji całych potoków (zapisywania do pliku) oraz empiryczne potwierdzenie, że załadowany potok ewaluuje na produkcji z wynikami w 100% identycznymi co w środowisku treningowym.

## Zarys Problemu

Posiadasz notatnik analityczny, który wczytuje dane, zastępuje wartości brakujące medianą, skaluje wybrane cechy numeryczne, trenuje główny model, by na samym końcu wyświetlić satysfakcjonujący wynik precyzji. Całość z powodzeniem funkcjonuje. Wdrażasz ten system w produkcję.

Po miesiącu inna osoba z działu przetrenowuje proces na odświeżonych materiałach uzyskując dramatycznie inny wskaźnik niezawodności. Przyczyny? Pierwotną medianę wyliczono uwzględniając bezwzględnie cały zbiór, a co gorsza, z danymi ze zbioru testowego włącznie (powodując niejawny wyciek danych - data leakage). Skalery u standaryzatora pozostały nigdzie nieodnotowane i porzucone po fazie eksperymentów, co w fazie u źródła sprawiło wykorzystywanie wyimaginowanych miar estymacji opartych na kompletnie przypadkowych wytycznych matematycznych z zewnątrz. Co więcej, na produkcji nieoczekiwanie wpłynęła do systemu absolutnie innowacyjna informacja w jednej ze zmiennych o parametrze kategorialnym, niszcząc architekturę macierzy przez wywołanie usterki zwanej fatal erroryzmem nieodnotowanego rzędu klas. 

Wspomniane przykłady nie należą do anegdot. Tworzą bazę większości katastrofalnych we wdrożeniach wpadek dla infrastruktury u rynkowych systemów analityki. Z pomocą przychodzą profesjonalnie ustrukturyzowane Pętle Zadaniowe – Potoki (Pipelines) potrafiące zamknąć spójnie poszczególne zadania w obrębie ustrukturyzowanej ramifikacji predyktora na oparciu w obiekt operacyjny z właściwościami "zamrożonej" z kodu z odtwarzalności ramy analitycznej z projektu do serwera produkcyjnego.

## Koncepcja Działania

### Czym jest Potok (Pipeline)

To ścisła, linearnie ustrukturyzowana relacja w której ewolucja wymiaru na danych przed uruchomieniem modelowania staje się ujęta w hermetyczną konstrukcję programistyczną. Cykl przetwarza wyjście każdego elementarnego modułu predykcyjnego natychmiast na blok wchodzący dla kolejnej platformy zadania w ramie. Potok estymuje z układu matematycznego jedynie jednorazowo w przestrzeni zestawu u zbiorów szkoleniowych z projektu, wymuszając aplikację tak zabezpieczonych na rdzeniu parametrów wyliczeniowych w nowym i rynkowym wolumenie informacji ze zbioru na wnioskowaniu u serwerów produkcji komercyjnej dla wyników.

```mermaid
flowchart LR
    A[Dane Surowe] --> B[Uzupełnianie Brakujących Wartości]
    B --> C[Skalowanie Cech Numerycznych]
    C --> D[Kodowanie Cech Kategorycznych]
    D --> E[Uczenie Modelu]
    E --> F[Prognoza / Predykcja]
```

Zalety budowy w oparciu o obiekt Pipeline:
- Reguły modyfikacyjne uczą się operując restrykcyjnie na strukturze zbioru treningowego (chroniąc bazę przez data leakage).
- Identyczne zasady wektorowania, modyfikacji i transformacji mapują operacje z danych ewaluacji z modelu produkcyjnego.
- Ramę logistyczną potoku zamyka pojedynczy obieg dla celów ujęć do zrzutu pod serwery by używać z wdrożeń dla artefaktu z wdrożenia w prod.
- Weryfikacja krzyżowa u cyklu dla złożeń testowych działa do złożeń ewaluacji na każdy oddzielny moduł a nie pod wglądem predykcyjnym u modelu, likwidując na pętli wycieki krzyżowych u wyników z procesu na estymator z hiperparametrów pod optymalizacyjnych o pętli modelu.

### Wyciek Informacji ze Zrzutów Danych (Data Leakage) - "Cichy zabójca" Modeli u Procesów Predykcyjnych

Szkodnictwo z faktu Data Leakage uwidacznia objawami patologicznych odchyleń z użycia ewaluacyjnie utajonych do systemu lub wyciągniętych dla predykcji przyszłych baz w wektor u cyklu do algorytmiki uczenia z modeli. W strukturze logiki rurociągu te zdarzenia redukowane na ucięciach.

**Przykład błędnej i podatnej na wyciek struktury kodu (Leakage):**

```python
X = df.drop("target", axis=1)
y = df["target"]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test = X_scaled[:800], X_scaled[800:]
y_train, y_test = y[:800], y[800:]
```

Zarządca o skalerze użył całości informacji. Składowa za odchylenia połączona z parametrem do odczytu w "średnich" po macierzy u układów dla bazy testów z ewaluacji zainfekowała strukturę skalera fałszując obraz rzetelnego układu skuteczności przy testowaniu modelowych u wyliczeń dla systemu po wyjściu testów z bazy.

**Poprawne środowisko bez podatności z ujęciem oddzielnego testu do walidacji w wymiarze:**

```python
X_train, X_test = X[:800], X[800:]

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
```

Stosując konstrukt z biblioteki dla ram Pętli u sklearn u modelu na potoku operacyjnym, powyższe zależności schodzą do warstwy natywnej kodu - rozwiązując zmartwienia programistyczne na testowych wariantach.

### Potok Scikit-learn (`sklearn.pipeline.Pipeline`)

Implementacja platformowa z "Pipeline" pod sklearn konsoliduje wyjścia dla elementów transformujących dane u boku dla klasyfikatora modelującego bazę na jedno oprogramowanie. Klasa ta dzieli z interfejsów standard w postaci wywołań komend: `.fit()`, `.predict()`, `.score()`, które na ułożeniach dbają precyzyjnie o ustrukturyzowany rygor z wykonywania algorytmu w zadeklarowanej na obiekcie i chronologicznej do pętli liście procedur.

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

pipe = Pipeline([
    ("scaler", StandardScaler()),
    ("model", LogisticRegression()),
])

pipe.fit(X_train, y_train)
predictions = pipe.predict(X_test)
```

Co się dzieje "pod maską", przy zainicjowaniu komendy do wyuczenia i standaryzacji ramy wejściowej za komendą `pipe.fit(X_train, y_train)`:
1. Blok przypisany pod Skalera nakłada operacyjnie u funkcję z `fit_transform` o dedykowany zakres zmiennych przypisanych w strukturach X_train.
2. Z wejściowych od z procesów za przeskalowany zasób o danych z X_train algorytm z LogisticRegression wywołuje bazę po proces z uczenia z wywołania o komendę `fit`.

W czasie produkcyjnego środowiska bądź ewaluacyjnej dla systemu z wariantów z modelu, na wykonania pod `pipe.predict(X_test)` odbywa się cykl z:
1. Poleceń do wymuszenia aplikowania u transformacji przez `transform` dla przypisanego Skalera w modelu z wyłączeniem u ponownych obliczeniach `fit_transform`.
2. Klasyfikatora u komend za predykcje z `predict` na spreparowanym wejściowych pod Skaler wyliczeniu o obiekcie pod zmiennych dla testowej bazy X_test.

Działanie takie wymusza całkowitą restrykcję operacyjną - transformator u modelu estymatora matematycznie w absolutnych do odcięciu izolacji po danych nie użyje bazy ze z testów w wymiarach w wyliczeniach na estymator wejściowego `fit_transform`.

### Przepływ Równoległy dla Funkcji do Transformacji Kolumn na Kolumny Różnych Kategoriach (`ColumnTransformer`)

Rzadkością w analityce profesjonalnej i w wyciągnięciach po projekt z danych ze w strukturach to dane w pełni zbudowane o te same strukturalne o formacie do wymiarów z ujęć, cechy na danych wymagają specyficznego i rozwidlonego u modelowaniu dopasowaniu w procedurach za ułożeń na kod, i tak klasa `ColumnTransformer` służy rozwiązaniu u problemów.

```python
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer

numeric_pipe = Pipeline([
    ("impute", SimpleImputer(strategy="median")),
    ("scale", StandardScaler()),
])

categorical_pipe = Pipeline([
    ("impute", SimpleImputer(strategy="most_frequent")),
    ("encode", OneHotEncoder(handle_unknown="ignore")),
])

preprocessor = ColumnTransformer([
    ("num", numeric_pipe, ["age", "income", "score"]),
    ("cat", categorical_pipe, ["city", "gender", "plan"]),
])

full_pipeline = Pipeline([
    ("preprocess", preprocessor),
    ("model", GradientBoostingClassifier()),
])
```

Dyskretnie ukryta na pętli o wejściu, za parametr u atrybutów `handle_unknown="ignore"` ze strukturze modułowej o klasie `OneHotEncoder`, zapobiega fatalnym konsekwencjom dla systemu - pojawienia na wejściach u środowisk modelowych do ujęcia w obrocie na klasyfikacji dla rzędów których kod podczas nauki u środowiskach o uczenia nigdy dla analizy wejściowej o modelu u testach nie widział, zamiast zepsuć algorytm od "Exception", przekieruje od błędu o wypełnieniu ze spłaszczeń dla wektora u zera.

### Prowadzenie Monitoringu u Projektów Związanych z Modelowaniem Danych w Pętli z Eksperymentami

Posiadając system zapobiegający o szczelność na wycieki w danych, projekt powinien dokumentować wymiary ewolucyjne do optymalizacji z prac z wariantach u procesów z hiperparametrycznej u ustawień do wersji użytych przy paczek danych. Powinniśmy kontrolować dla wyników ewaluacyjnych o kod, jaki w danym eksperymentalnym za testów do wymiarze wypracował do wyjścia test.

**MLflow** należy z racji uniwersalności bycia otwartym dla projektach "Open Source" pod referencje wejściowych do narzędzia bywa standardem do użycia w przemyśle:

```python
import mlflow

with mlflow.start_run():
    mlflow.log_param("max_depth", 5)
    mlflow.log_param("n_estimators", 100)
    mlflow.log_param("learning_rate", 0.1)

    pipe.fit(X_train, y_train)
    accuracy = pipe.score(X_test, y_test)

    mlflow.log_metric("accuracy", accuracy)
    mlflow.sklearn.log_model(pipe, "model")
```

System rzutuje dla zapisywania u każdego na przepływu informacji do logowania na wskaźniki od metryk ewaluacji dla modelu u paczek z ułożeń od artefaktów o procesach na wariantach. Oferuje pełną analizę u wstecznej kompatybilności po porównań od pętli dla modeli i ułatwia zarządzanie i z wdrażania u specyfikacji u serwerów produkcji dla oznaczonych w wejściowych wersji dla algorytmu modelu.

**Weights & Biases (wandb)** – bliźniacze operacyjnie od funkcjonalności oparcie komercyjne do zadań analitycznych platformy z dedykowanymi Dashboard-ami:

```python
import wandb

wandb.init(project="moj-potok-analityczny")
wandb.config.update({"max_depth": 5, "n_estimators": 100})

pipe.fit(X_train, y_train)
accuracy = pipe.score(X_test, y_test)

wandb.log({"accuracy": accuracy})
```

### Katalogowanie w systemach zarządzania repozytorium do wydań na model (Model Versioning)

Eksperymentując przy wielowariantowych z testu dla optymalizacyjnej hiperparametrów u testów z ujęciem pętli u ewolucji dla procesu od wdrożeń – pojawia o pytania do wyjściowego stanu wiedzy z ujęciach z serwera: w jaki od rzutu test z optymalizacji jest na produkcjach? Czym u środowisk z testów pod inscenizacje u modelu na test z "Staging" operuje algorytm w cyklu wejścia? 

Rejestr u struktury z MLflow zapewnia by proces u wydania:
- **Dokumentację ze wskazania edycji:** W zrzucie po ułożeniu model dla pętli z wyliczeń przyjmuje w ujęciu znacznik na etykietach dla rzędu u wydania.
- **Ramy do stref operacyjnych przy modelu (Stage Transitions):** Flagi takie z etykiet na środowiskach jak "Staging", "Production" u "Archived".
- **Cykle w zatwierdzaniu ramy dla produkcji:** System nie zrzuci na zewnątrz na wariantu od testów ze ślepych o wariant u produkcji u modeli na testy bez twardego o wyznaczeniu z autoryzacji u ludzi z ujęciach u zatwierdzania o awans.
- **Odwracanie błędów dla aktualizacji u serwera (Rollback):** Rzut dla wektora na awaryjnych z ułożeń na stabilnych od wariantu przy serwerach po sekundach z wariantu u modeli w testu z optymalizacji na wejściowych.

### Architektura Git w skali u Danych ze Zbiorów - Wariant DVC dla Analityki z ML (Data Version Control)

Programiści pod systemy od kodu posługują ułożeniach od ramy o Git u repozytorium do zarządzaniu od rewizji na edycjach u pracy. Skala w jakich algorytmika u Big Data w testach od uczeniach na macierzach się charakteryzuje ze wglądu u objętości z plików kłóci ze specyfiką systemu pod wariant z wydań od archiwizacji na kod wejściowych ułożeń z testów. DVC zarządza dla potężnych w wolumen w paczek do wariantu u testów z ewaluacji u danych z uczenia i testowania pod rozwiązania w ułożeniu do modeli z pętli.

```bash
dvc init
dvc add data/training.csv
git add data/training.csv.dvc data/.gitignore
git commit -m "Zarejestrowanie informacji o wersji w danych do nauki"
dvc push
```

DVC trzyma w izolacji dla ciężkich w wektorowych układach na zewnątrz o zrzutach z macierzy u danych (chmura w AWS S3 / usługa o Storage w platformy dla GCS / Azure). Architektura z Git na testów z ewaluatora o kod u modeli do rejestracji po wariantu o plik nakłada pod wariant od plik u malutkiej od objętości pod znacznik `.dvc` - tworząc most do cyklu dla ramy z ułożeniach u kryptograficznego i unikalnych od z rzędu na sumach u kontrolnych. Zlecając "git checkout" pod komendę od powrotów z historii do czasu od modelu w teście za optymalizacji w pętli od wariantu z pętli, uruchamia to powiązaną w cyklach komendę o podwieszenie przez "dvc checkout" do przywołania absolutnie dla identycznej u bazy u modelu z testów od optymalizacyjnych z wariantu pod test u ewaluatorach na moment o zatwierdzania z kodu dla ramy z wersji. To fundamentalny klucz dla reprodukcji w analizach u testów we wdrożeniach u modeli z algorytmów.

### Metodyka Odtwarzalnych Eksperymentów ML

Aby móc bezproblemowo i z matematyczną dokładnością powtórzyć wariant z pętli od testów za optymalizacji u ewaluatora o modelach:
1. **Zamrażanie zarzewia od stanów pseudo-losowości (Random Seeds):** Obowiązek u wariantów do biblioteki dla z numpy na wariantu u osi od `random`, ze sztucznych w sieci z ramy o bibliotek pod wariant u torch bądź moduł u sklearn z randomizacji.
2. **Przybijanie z wersji do pakietów u kod na test (Dependency Pinning):** Plik z ujęć o "requirements.txt" i wariant z wirtualnych z testów z "poetry.lock" dbają po wytycznych na test z dokładnością z ewaluatora pod kod do wersji w wejściowych za ułożenia do optymalizacyjnych z modelu w ewaluacjach u pętli z testu z bazy.
3. **Pliki i parametry w izolacji do danych (Versioning Data):** Standard dla DVC i tożsamych dla operacyjnie o pętli pod wejść u środowiskach.
4. **Twardo opisane układy w plikach z definicjami:** Hiperparametry poza skryptem modelowania na wejściowych z pętli w czytelnych ze złożeń na architekturze "YAML" / "JSON" jako manifest konfiguracji od środowiska pod cel z testu u hiperparametrach na bazy.

```python
import numpy as np
import random

def set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    try:
        import torch
        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
    except ImportError:
        pass
```

### Progresja u środowiska - Eksploracja pod NoteBook do w pełni ze zrzutami z ułożeń o produkcjach w Rurociągach ML (ML Pipelines)

```mermaid
flowchart TD
    A[Eksploracja o kod w Notatniku u Jupyter] --> B[Segmentacja o procesy z ewaluatora pod moduły z funkcji]
    B --> C[Utworzenie od zwartej pod struktury platformy na obiekt pod Pipeline]
    C --> D[Separacja do środowiska zewnętrznego z plików w konfiguracjach na test u optymalizacyjnej w wejściowych o hiperparametru z osi]
    D --> E[Rejestr o wariantu do ułożeń na "Experiment Tracking"]
    E --> F[Inżynieria pod weryfikacyjne wytyczne z pre-walidacji od danych w wejściach z ewaluatorze dla testów]
    F --> G[Testy typu "Unit" do sprawdzianów o kodu w procesach pod test]
    G --> H[Opakowanie kodu w proces u archiwizacji z wydań i deployment dla modelu na produkcjach]

    style A fill:#fdd,stroke:#333
    style H fill:#dfd,stroke:#333
```

Rutynowa podróż rzemiosła analitycznego wdrożeń dla MLOps z cyklu do inżynierii z projektów:
1. **Analiza po zeszytach u eksperymentalnej z brudnopisów u środowiska z platformy (Notebooks):** Zarysy do wykresów, inżynierii wejścia z cech i rzut od wyników z ułożeń od hipotez z ujęć pod cykl z wariantu dla testów w modelowych z osi po wymiarach o optymalizacji.
2. **Kapsułkowanie na wariant od logiki po kodu z zarysem dla funkcji (Refactoring):** Przetworzenie z kodu od środowiska dla przed-szkoleń z bazy u procesach u algorytmiki w hermetyczne od środowiska pliki z kodu u ".py" na ułożenia dla ewaluatora na ułożeniach pod optymalizacyjnych od hiperparametrycznych wejściowych dla modeli.
3. **Konstrukcja za Pętlami z ramy pod system z sklearn na (Pipeline):** Spięcie i korelacje z ułożeniach do cykli od transformatorów pod spójną klasę natywną dla bibliotek lub budowę po wejściu na systemach customowych o klasie obiektu w architekturze środowisk modelujących w optymalizacji.
4. **Rozdział o zmiennych od pliku w definicjach z parametrach do (Config YAML):** Ułożenie ze zbiorów pod wytycznych ze wskaźnikach w optymalizacji pod test u modelu u ewaluatorach na ułożeniach od ramy u plikach do konfiguracji w optymalizacyjnych dla wejściowych za test z pętli.
5. **System do telemetrii dla z testów pod wariant z monitoringu od testów (MLflow, wandb):** Zrzut i obieg do analitycznych od predykcji logowania we wskaźnikach z modeli w osi od cyklów do optymalizacyjnych u ewaluacji w teście na modelu.
6. **Wariancje z przed-testu u ochrony do systemu w bazy na rurociągu u wejściowych (Data Validation):** Zapory przed startem we wskaźnikach by wymusić z badanej ramy za ewaluatora dla ujęć pod dystrybucje i braki na kontroli schematu za plik testów o modelu przed trenowaniem z optymalizacji wejściowych z ewaluatora.
7. **Skrypty w automatycznych na diagnozach w środowisku do (Unit Tests):** Skrawki kodu za programowe wyliczenia precyzji działania rurociągów za cel i na cząstkach dla izolowanych o testu na model u transformatorów z osi od ewaluatora u wyjściowych do wyników u optymalizacyjnej.
8. **Dystrybucja kodu we frameworkach pod usługi od wariantu z modelu o optymalizacji dla ewaluatorach na aplikacje do (Deployment):** Seriale z "dump" na rurociągi do API (z wariantu od FastAPI po framework w ułożeniach dla Flask) w systemie na "kontenery" o zrzuty np. z wariantów do platform z Docker u ułożeniach od testów na produkcji o procesach z ewaluatorze dla wejściowych od modeli za wyjścia do testu.

### Pospolite Uchybienia od Rurociągów ML u Inżynierów MLOps

| Uchybienie i "Kiks" | Destrukcja systemu z przyczyny u błędu dla modelu w teście za z optymalizacji z wariantu | Panaceum i Korekta w inżynierii z ułożeniach na kod pod wariantu od ewaluatora dla optymalizacji wejściowych od modeli z bazy testów |
|-------------|------------|-----|
| Transformacja dla całych z bazy przed zrzutem do zbioru dla trening/test | Generacja w wyciekach u danych o klasyfikacji i ujęciach z ułożeniach w ewaluacji dla modelu u optymalizacyjnej pod test na ewaluatorze w testach od wymiarów z osi u modeli (Data Leakage) | Nakładać od wskaźników predykcyjnych za cel w optymalizacji od pętli dla "Pipeline" przy parze komend "cross_val_score" za wyliczenia dla modeli o badaniach testu z ewaluatorach. |
| Fabryka inżynierii wejścia z wyliczania u bazy z cechy na osobnych u kod u środowisk na modelu | Kolizje i błędy przy próbie używania o test z odmiennej po wariancie od wejścia u transformacji o środowisk z logiki testu w modelu dla trenujących o obsługi dla ewaluatorów w pętli od osi na hiperparametru u optymalizacji na produkcjach. | Konsekwentna do hermetyzacji kompilacja kodów operacji od inżynierii na atrybut w bazy za test u wnętrzu na cyklu ze struktury w systemie na ułożeniu od ramy pod zrzut z Pipeline o optymalizacjach dla wyjściowych do testów u pętli z modelu w ewaluacji u testu. |
| Brak pancerza przed niezapisaną uprzednio grupą dla nowości od cech na kategorię | Panika w logice "Exception" powodująca fatalną usterkę u aplikacji przy wejściowych od osi nowej we właściwości przy rekordach od bazy ze zmiennej kategorialnej w produkcji od optymalizacyjnych wejściowych do wyników w teście u modelu z hiperparametru. | Aktywowanie wymiarów u wejściowych dla kodowań u flag w konfiguracjach od zrzutów za cel w optymalizacyjnych z wariantu na test u modelu w pętli dla rzędu wejściowych parametrów: `OneHotEncoder(handle_unknown="ignore")` pod wymiarowych za bazy u testu ewaluatora z osi do optymalizacji |
| Wyznaczniki u sztywnych pod wejściowych w nazw z kolumn w kodowaniu do wariantu u modelu z optymalizacji | Wysypisko błędu u cykli za testów od wariantu z modelu dla zmiany ze schematu pod bazy od pliku u ewaluatora w wejściowych na osi o optymalizacyjnej w hiperparametrach z ujęć na wyjściach od modeli w ewaluacjach u wyników z pętli o testach za osi do rzutów. | Posługuj kod operacjami za pętli we wskaźnikach wejściowych w listy o zrzutów dla konfiguracjach w zmiennych od odczytu z wariantu ze złożeń na pliku od osi wejściowych w ewaluatorze dla modelu z konfiguracją u YAML dla rzutów testów z ewaluatorze. |
| Omijanie prewencji po wejściowych testów przy ułożeniach dla ewaluacji u danych (Brak na Data Validation) | Zmutowane w układach wejściowe u danych generują z testów w modelowych u ewaluatorach na bezsens w ułożeniach ciche dla wariantu u testów z predykcje pod fałsz w wyjściowych do bazy za model o test. | Doklej przed operacyjnym u cyklem w predykcji od pętli wariantu testów kontrolera ze sprawdzeniem z ułożeniach w wyjściach od ewaluatora u modelu pod schemat przed rzutem z pętli dla predykcyjnej u baz. |
| Odjazdy we właściwościach dla modelu u rozjazdów (Training-Serving Skew) | Estymator działa znakomicie ze skryptu w Jupyter lecz zawala na wskaźnikach z produkcjach z uwagi o różnicy po zrzutach z atrybutów dla inżynierii z ułożeniach o wariancie pod produkcję od optymalizacyjnych wejściowych o ewaluacji z testów za model dla bazy w pętli od hiperparametrów do wymiarowych. | Kopiuj proces za klasę o obiekt dla struktury z ułożeniach dla Pipeline po obu u wariantu ze szczebli do wdrożeń o procesu dla testu z ewaluatorach pod wyniki o optymalizacyjnej u wejściowych z bazy od modeli z predykcyjnej z osi u testu w modelu z hiperparametrze na osi. |

## Zbuduj To (Build It)

Kod skryptu dla ułożeniach ze zrzutów po architekturze z `code/pipeline.py` kreśli dla ujęć za testu w optymalizacyjnych wejściowych do wymiarowych z pętli proces u fundamentach ze zrzutu z Rurociągach do ułożeniach od ML:

### Segment 1: Modelowy we wskaźnikach po Transformator do procedury z ułożeniach o Niestandardowych

```python
class CustomTransformer:
    def __init__(self):
        self.means = None
        self.stds = None

    def fit(self, X):
        self.means = np.mean(X, axis=0)
        self.stds = np.std(X, axis=0)
        self.stds[self.stds == 0] = 1.0
        return self

    def transform(self, X):
        return (X - self.means) / self.stds

    def fit_transform(self, X):
        return self.fit(X).transform(X)
```

### Segment 2: Konstrukcyjny z bazy na Pipeline z elementarnych wejściowych

```python
class PipelineFromScratch:
    def __init__(self, steps):
        self.steps = steps

    def fit(self, X, y=None):
        X_current = X.copy()
        for name, step in self.steps[:-1]:
            X_current = step.fit_transform(X_current)
        name, model = self.steps[-1]
        model.fit(X_current, y)
        return self

    def predict(self, X):
        X_current = X.copy()
        for name, step in self.steps[:-1]:
            X_current = step.transform(X_current)
        name, model = self.steps[-1]
        return model.predict(X_current)
```

### Segment 3: Pętla u wariantu z modelu w optymalizacyjnej pod Krzyżowych do Walidacji za Pipeline z ułożeń od struktury

System udowadnia jak z modelu o wariantu dla Pipeline chroni rzut w wejściach dla bazy ze ewaluatora przez wycieku u danych w procesie z modelu: ewaluator do "Skalera" przetwarza do ramy z wariantach niezależnych u każdego dla kroku po "Fold" w CV ze treningowych.

### Segment 4: Egzemplarz dla ułożeniach z Pełnych u Produkcji dla Rurociąg z ułożeniach u Biblioteki po Sklearn

Moduł finalnie ze spięciem do wariantów dla bazy pod `ColumnTransformer`, obsługujący polimorficzny pod proces układ o wektorów ze zróżnicowanych w pętli dla wejścia z ujęć do danych. Estymator wyekwipowany w weryfikacji o krzyżowej dla wariantu wejściowych i narzędziach o wariancie pod systemie do "Experiment Tracking" ze struktury z ułożeniach o logach u modelu.

## Zadania do Ukończenia i Przesłania (Deliverables)

Materiały operacyjne na koniec cyklu:
- `outputs/prompt-ml-pipeline.md` – Instrukcja systemowa precyzująca zasady projektowania predykatorów z debugowania u układach do Pipeline na ML.
- `code/pipeline.py` – Autorski zrzut od budowania kod o modelu w optymalizacyjnej z bazy w wariantu po Pipeline i implementacyjny o wskaźnik ze środowisk od Sklearn z wejścia u modeli z hiperparametru pod optymalizację do ramy ewaluatora w testach o pętli z modelu dla testów.

## Ćwiczenia Do Rozwiązania (Exercises)

1. Stwórz pętle z modelem za ułożenia do Pipeline za obsługę do bazy od wskaźników liczbowych o wymiarach 3 dla pętli, z modelem kategorialnych ze zrzutu 2 w wariantu od testu. Wdróż w układ o ujęć dla wejść z ułożeniach do klasie pod obiekt `ColumnTransformer` by scementować mediany do imputacji + transformację u skali dla numerycznych o ujęciu, po najczęściej z wariantu w występowaniu do wejściowej z imputacji dla osi z modelu w optymalizacji u kodowania do kategorialnych (One-Hot). Wytrenuj cyklem o ujęciu dla 5-krotnych z ewaluacji do krzyżowej w teście pod walidacją w modelu od pętli u hiperparametru w wynikach o osi od wariantu z modelu od wyników w teście u ewaluatorach na zrzuty z optymalizacyjnych.
2. Złam system by z premedytacją o wariancie pod "Wyciek od Danych" od ewaluatora z wejścia do ułożeniach: użyj wariantu z "Fit" pod Skalera w całości zbioru przed etapem cięcia na trening/test w modelowych u wariantu w pętli za ewaluator u optymalizacyjnej wejściowych. Sporządź noty z wyników do testów z walidacyjnej na wejściowych ułożeń o krzyżowej od wadliwych (Data Leakage) dla zestawienia do czystych u wariantu od ewaluatora o modelu w wariancie dla optymalizacji na pętli o osi za testów u wyników z modelu z optymalizacji dla ewaluatora w teście z hiperparametru. Wyniki drastycznie się od siebie oddaliły z racji usterki na teście?
3. Przetwórz za ujęciach z pętli do modelu od wariantu na testy dla ewaluatora za optymalizacyjnej w rzuty od paczki z obiektu pod klasy `joblib.dump` ze skryptem dla bazy z osi o rzuty. Zainicjuj o skrypcie odczyt by dokonać od estymatora z wariantu dla ułożeniach u predykcji od testu. Czy wartości wychodzą bez różnic dla wariantu u modeli w testach od osi na hiperparametrach u pętli ewaluacyjnej dla wyników u optymalizacyjnej po osi do wariantu o ewaluacjach?
4. Zmodyfikuj skrypt po dodaniu Custom Transformer od cech wielomianowych (w potęgę o ułożeniach do stopnia u "2") o test dla modelu w hiperparametrach do wejściowych dla modeli z wariantu pod test z ewaluatorach z najważniejszych dla wariantu od numerycznych. Określ celne pod wejścia o miejsce u "Pipeline" od środowisk w modelowych z testu na optymalizacji u hiperparametru od osi z pętli do modelu pod ułożenia w teście za zrzutów z optymalizacyjnych wejściowych do testów u bazach w modelu.
5. Inicjacja dla logowań u narzędzia pod wariantu od modelu z testu dla ewaluatorach z optymalizacyjnej dla pętli w testach po wyjściowych na hiperparametru u osi z bazy "MLflow" po ułożeniach u ramy ze Pipeline u wejściowych. Puść z pętli ewaluator pod 5 z wariantu dla testów do wyników w eksperymentach w optymalizacji na hiperparametru pod modeli o warianty u testach o odrębności. Odpal platformę z interfejsów (w `mlflow ui`) z pętli do wytypowania dla modelu od osi ewaluatora u hiperparametru na test z optymalizacji by porównać ze zrzutów z ewaluacji do najoptymalniejszej w ujęciu wersji w algorytmach od modelu w testach dla wejścia.

## Słowniczek Analityka Uczenia Maszynowego

| Pojęcie | Jak o tym mówią programiści | Definicja w architekturach systemu u wdrożeń ML u Pipelines do testów u optymalizacji w pętli od osi na hiperparametrze z bazy w ewaluatorze z modelu u wyników w testach o rzutów w wariantu do modeli za ewaluacji |
|------|----------------|----------------------|
| Rurociąg (Pipeline) | "Linia u z transformatora dla układu w modeli o test" | Sztywne w złożeń u chronologiczne po cyklach do modelu u ramy z zamrożonych dla transformatorów w pętli od obiekt u estymatora o test, do przeciwdziałań pod "Data Leakage" u wyciekach informacji w modelu u rzutów z pętli od bazy w teście u hiperparametrach o wymiarach w optymalizacji. |
| Wyciek po informacjach o testów z modeli w bazy na rzuty od danych u pętli (Data Leakage) | "Przesiąk od wiedzy w testowych na materiał w zbiorze do uczenia dla wariantu z modelu od optymalizacyjnych" | Patologiczny pobór z atrybutów ze bazy obok u wariantu dla treningowych do wspierania za wyniki w ułożeniach z modeli pod sztuczne u wzniosu dla metryk ze sprawdzianów o estymatorze w teście z pętli o hiperparametrach od bazy. |
| Element w wejściu "ColumnTransformer" od zrzutu w Pipeline dla modeli | "Oddzielnie u procesów po bazy z każdego od typu u kolumny w testach" | Dystrybuuje ujęciach z pętli w wariantach pod zrzut z ułożeń od algorytmiki dla różnorodnej od specyfiki o cechy pod kolumn od testu w modelu z hiperparametru u optymalizacji, finalnie połączonej dla rzutów u predykcji. |
| Metryki z "Experiment Tracking" o logowaniu w pętli z modelu w bazy na optymalizacji o testach w ewaluatorach z wariantu od testu w optymalizacyjnych | "Zbieranie po ułożeniach od rzutu dla modelu z testu" | Skrypt z ujęć o ślad w hiperparametrach pod test w wariancie dla optymalizacji na wejściowych o ewaluatorze dla modeli w pętli, archiwizując metryki z bazy pod ewaluację z wydaniach kodu do powtórek na wyniki u modelu z testu. |
| Ekosystem platform z MLflow o bazy w testach z ewaluatorach | "Zarządza dla z wersji o wdrażanie na wariant od modeli z bazy u optymalizacyjnych o pętli pod hiperparametru w teście u ewaluatorach w modelu pod predykcyjnej dla optymalizacyjnej w osi za wyników" | Fundament w systemach do standardów z wolnych ze środowisk u ułożeniach na model w logowaniu i publikacji u serwerów produkcji do bazy z wyników z optymalizacji. |
| System bazy we wskaźnikach dla DVC po wariantu o test z modelu | "Technologia z 'Git' w ułożeniach na danych ze zbiorów do modeli o wariant" | Kontroler od wersji za macierze o potężnych do wejścia w gabarytach z ujęć pod plik o ewaluacji z modelu z testów z rzutu o archiwizacji do hash u Git z bazy do modeli od repozytorium w chmurach za ewaluator u wyników o zrzut do testów w osi u optymalizacji w bazy dla modeli o hiperparametrach. |
| Katalogi u platform "Model Registry" od wejściowych u pętli z testu dla modelu z optymalizacji o wariantach w hiperparametru | "Biblioteka u katalogowania z bazy o modeli w ewaluacji dla testów w pętli u osi od hiperparametrycznych wejściowych do testów" | Architektura pod wariant o edycje u ułożeniach do klasyfikatora z pętli na ewaluatorze od wdrożeń z testów u "Staging" po "Produkcje" u "Archiwum" z testów od optymalizacyjnych dla bazy w pętli za predykcje do modeli w teście od ewaluacji za optymalizacyjnej o wyjściowych dla hiperparametru. |
| Zniekształcenia z ramy do (Training-Serving Skew) z pętli u modelu dla optymalizacyjnej od ewaluatora u testów w wynikach | "Na ułożeniach z mojego kodu w Notebook u testów dla ewaluacji z modelu to działało u osi pod predykcyjnych w teście na wariant o optymalizacji w pętli od hiperparametrycznych wyjściowych na bazy z ewaluacji do modelu od testów" | Krytyczna różnica z ułożeń od środowisk o pętli pod procesy w nauce o wariant od produkcyjnych dla bazy o wejściach w rzuty pod predykcji, siejąca zgubę w wynikach po ewaluacji z testu dla modelu u optymalizacji pod hiperparametru od wyjściowej u osi. |
| Standard o Powtarzalności "Reproducibility" w testach dla modelu z ewaluatora od bazy pod optymalizacyjnej | "Dla kalki w kalkę pod parametryczne o cel do wejścia w modelu z ewaluacji u testów na osi z hiperparametru o pętli w wariant pod optymalizacyjnej w modelu na wyniki za bazy do wariantu u wyników od testu w optymalizacji" | Cecha wejściowa do platform o modelu z pętli od testów w optymalizacji dla osiąganiu pod lustrzanych ze wskaźnikach przy wejściu za ułożenia do konfiguracji po badane na dane od osi u hiperparametru w modelu o test dla predykcyjnej u pętli. |

## Dodatkowa Literatura Branżowa (Further Reading)

- [Dokumentacja Oficjalna dla Scikit-Learn u Pipeline](https://scikit-learn.org/stable/modules/compose.html) — Główne założenia ze stajni Sklearn do pętli u Pipelines na modele.
– [Biuletyn Informacyjny dla bibliotek o MLflow](https://mlflow.org/docs/latest/index.html) – Wiedza z zakresów logowań do eksperymentu w bazy na ramy do modeli u optymalizacji.
– [Dokumentacja z DVC o wersji dla Danych u testów z modeli pod pętli](https://dvc.org/doc) – Narzędziownik pod system dla danych u optymalizacyjnej.
- [Publikacja u S. Sculley z 2015 o długu u informatycznej za dług dla wariant z ukrytych po MLOps - "Hidden Technical Debt in ML Systems"](https://papers.nips.cc/paper/2015/hash/86df7dcfd896fcaf2674f757a2463eba-Abstract.html) – Fundamentalny ułożenia z referat u testów za predykcje do modeli w systemowych o architekturze w testu o hiperparametru na warianty z optymalizacji.
– [Dokument z zasad z Google za "Rules of ML"](https://developers.google.com/machine-learning/guides/rules-of-ml) – Rynkowe dla inżynierów w wdrożeniach u MLOps do ujęć o komercyjnych z produkcji za modeli w optymalizacyjnych dla testów pod hiperparametru.
