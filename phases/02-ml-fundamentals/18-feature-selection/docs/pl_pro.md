# Selekcja Cech (Feature Selection)

> Dodanie do modelu większej liczby danych nie oznacza automatycznie wyższej jakości predykcji. Prawdziwa moc drzemie we właściwie dobranej, przefiltrowanej i celnej reprezentacji danych, a nie w ślepej kumulacji informacyjnego szumu.

**Typ:** Konstrukcyjny / Budowa z podstaw
**Język operacyjny:** Python
**Wymagania wstępne:** Zakończona Faza 2 (zwłaszcza lekcja dot. Inżynierii Cech)
**Czasochłonność:** ~75 minut

## Edukacyjne Cele Merytoryczne

- Płynne zaimplementowanie od fundamentów zróżnicowanych technik, w tym metod filtrujących (Variance Threshold, zaawansowana Informacja Wzajemna), oraz algorytmów opakowujących model (RFE).
- Teoretyczne i głębokie przyswojenie i uargumentowanie różnicy: dlaczego rozbudowana Informacja Wzajemna z sukcesem przechwytuje nieliniowe, skomplikowane korelacje ze zmienną wynikową tam, gdzie standardowa statystyka z Pearsonem ślepo kapituluje.
- Zbudowanie potoku inżynieryjnego (Pipeline) wyboru najlepszych dostępnych parametrów z ugruntowaniem wpływu na lepszą, szerszą i efektywniejszą dla świata rzeczywistego generalizację z modelem z odciętą bezużyteczną kolumną na testach powdrożeniowych.

## Problem Biznesowy

Dostarczono Ci 500 zmiennych. Twoja maszyna z głębokimi lasami ML uczy się w dramatycznie wolnym, męczącym dla procesora tempie, bezustannie dopasowuje się do szumu na etapie treningu, i nagle żadna osoba z Twojego zespołu analitycznego nie potrafi z precyzją, jasno zadeklarować czy wyjaśnić na co w ogóle aktualnie wyczulony został wypuszczany we wdrożeniu model z estymacją decyzji. Obarczasz go i karmisz w akcie desperacji nowo zsyntetyzowanymi, wyciągniętymi na siłę funkcjami i cechami wierząc naiwnie z pośpiechu i na ślepo iż uzyskasz poprawienie, lecz metryki i tak nieubłaganie spadają na dno.

To klasyczny u inżynierów i zderzający się dotkliwie z brakiem edukacji syndrom potocznej, utrwalonej na gruncie nauki jako „klątwy wymiarowości” (Curse of Dimensionality) w pełnej powiększonej krasie. Przy bezmyślnym zwiększaniu, pęczniejącej geometrycznie przestrzeni rzędów i dostępnej liczby unikalnych kolumn pod uwzględniane z wejścia do zbioru obarczających architekturę cech, odległości czy to statystyczne z uogólnieniami dla algorytmów geometrycznych ulegają bezgranicznemu i gwałtownemu zatraceniu wszelkiego sensu z utratą jakiejkolwiek wymierności, i do ułożenia poprawnej predykcji wymagana staje się kosmiczna o nieskończonej potędze dla maszyny wygenerowana baza próbek wejść aby cokolwiek wychwycić poprawnie. Bezużyteczny wprowadzony w atrybutach szum agresywnie bezkarnie zaczyna i dusi cenny pożyteczny obiektywny naturalnie pulsujący dla zjawiska wyraz sygnału i tła. Niesforne przetrenowanie algorytmu do wyuczenia układów z treningowych staje się smutnym absolutnie dominującym trybem domyślnie utartej przez błędy porażki modelowania dla zanieczyszczonych tabel wejścia.

Wyjściowym nieuniknionym uleczającym to lekiem u rygorystycznie nastawionego ułożonego projektanta na zjawisko wysoce wymiarowych w architekturze po stronie danych wyjścia u wyuczonego wektorowo badacza jest solidnie ułożona sterylizacja – tzw. proces pod nazwą Feature Selection (Selekcja Cech w Data Science). Ucinasz w niej cały hałas. Eliminujesz brutalnie całe powtarzane skorelowane i niosące te same obciążenia wtórne kopie i odrzucasz nadmiarowość. Rezerwując jedynie twarde, przefiltrowane z matematyki użyteczne parametry dostarczające rzetelne dla wektorów docelowych obciążonych cech czyste bezpudłowe merytoryczne i rzetelnie skorelowane i potwierdzone informacje i korelacje by oświetlić prawidłowo dla algorytmu do osi z estymowaną etykietą model predykcyjny. Osiągnięty profit to błyskawicznie optymalne czasowo i obciążeniowo w systemie tempo podczas sesji treningu u modeli decyzyjnych oraz fenomenalna, poszerzona w perspektywie stabilność zdolności estymatora z cech i rzutowana ostatecznie o poprawę interpretowalności samej bazy z przewidywaniem parametrów w warstwach analitycznych pod decyzyjność biznesu.

Odrzuć mrzonki na ujęcia naiwnie wciągania do estymacji i upychania do wagi wszystkiego co udało się napotkać u badacza dla bazy jako złoże i w rygor. Twój sukces i wartość oparta jest o użycie na wdrożenie parametrów przefiltrowanych rygorystycznych danych opartych tylko o najużyteczniejsze i obiektywne merytorycznie dla predykcji właściwości informacyjne, o precyzyjnie celującym sensie a reszta to obarczający model po stronie i wydłużającym ślepe wektory bagaż niosący ubytkowy w prognozach szum wymiarowy dla modeli analitycznych.

## Konstrukcja Oparta o Trzy Filary Algorytmów Modyfikacji Wyboru

Metody wyciągania do ułożenia wymiarów w klasach selekcji przydzielone sprowadzają swój wektor merytorycznie oparty i wycelowany o z weryfikowanych predykcyjnie pod z góry jedno z kategorycznie 3 ugruntowanych i fundamentalnie znanych dla inżynierów z podejść algorytmicznych pod selekcję cech do modelu analitycznego pod pojęciem ML i predykcyjnej przestrzeni wspólnej.

**Metody Filtrowania Z Zewnątrz (Filter Methods)** Ograniczają w swych procesach ułożonych predykcyjnie o użycie jedynie szybkiej po zjawisku na macierzy niezależnej od algorytmiki uczenia i użytego uczenia na czystych ułamkowych pod względem obciążenia szybkich rygorystycznych badaniach statystycznych użytych testów korelacji bez wchodzenia i zagłębiania się bez uwzględniania wewnątrz modeli powiązań cech w model bez uwarunkowań krzyżowych o sprzężenia zwrotnego na atrybutach, a opiera jedynie szybkim sprawnym i uogólnionym odcięciem szumu bez włączenia pod proces modelowego użytego estymatora z modelowanym. Niezwykle błyskawiczne ale potężnie uchybieniowo omija cenne krzyżowe powiązania do korelacji interakcyjnych w wymiarze modeli nieliniowych pomiędzy zmiennymi w badanym do uczenia szeregach wymiarowych na cechach badanych cech dla algorytmu pod oparcie i uogólnienie po z modelowanym układzie ułożonym i bez uwzględniania złożonych predykcyjnie krzyżowych oddziaływań uwarunkowań powiązań międzycechowych o uogólnieniu wielowymiarowych zmiennych do modelu analitycznego we wzorcu wielomianów do estymacji wejścia na estymatorze w model.

**Ujęcia o Technikach z Algorytmami Z Opakowywania ze Sprzężeniem Pętli Zewnętrznych Wokół Cech (Wrapper Methods)** Z premedytacją stosuje po stronie ułożonych wywołań ciężkie i nader wymagające bez litości w procesor angażujące modele i użyte pod ocenę ze zwrotnymi iteracyjnymi na badanych do obcięcia paczek sprawdzane w kółku by ostatecznie wyłowić opartą na wielokrotnym przewidywanym wyniku z wydajności pod kątem po odrzucaniu pętli predykcyjnej oparty twardo jako docelowy najlepszy dobór oceny do ocięcia o selekcji predykcyjnych punktowych ze zmiennymi do wydajności z parametrem obciążonej pod modelem wydajności pod predykcję użytego oceniającego bez oszukiwań na skrót z ujęciem obciążanego silnika i algorytmu decydującego by dopasować parametr pod wyjścia w odrzucaniu cech. Kosztowna i ciężka uwarunkowaniem w obciążenia wyczerpująca ale bardzo precyzyjna ze zdolnością wychwytu po testowaniu.

**Procedury Konstrukcyjne na Twardo Zagnieżdżone We Wewnątrz Do Optymalizacji Bez Przerwań Od Wbudowanego Procesu Estymacji z Selekcją Wewnątrz i Modelem (Embedded)** Przynoszą i używają i rozwiązują rygor użyty i scalają te operacje na w zintegrowanym i bezpośrednim do mechanizmu pod uczenia dla modelu podczas szukania w samym procesie szukania po parametrach pod predykcję przy optymalizowaniu funkcji optymalizacji wyliczeń po z ułożonych z dopasowania modelu u estymatora rzutów pod cięcie zbędnej niewymaganej do korelacji na zrównoważenie pod z wag w rygorze na uczeniu bez wydzielania osobno zewnętrznie po cięciach do wydzielanych i testowanych z testowania procedur do kroków wstępnych selekcyjnych zewnętrznych wywołań w odciętych narzędziówkach czy dodatkowych w testowanych ocięciach z odrębnym do odcięcia w uwarunkowanych predykcyjnych w krokach selekcyjnych i wydzielonych poza treningiem modelu selekcji do oddzielnych wyodrębnionych na osobnych poza zewnątrz narzędziami predykcyjnymi ciętych z zewnątrz do oddzielnych z wydzielania do testów algorytmicznych wywołaniach pętlowych niezależnych dla parametrów predykcyjnych selekcją do wyodrębnienia od modelu.

### Konkretny Zarys Wyboru W Implementacji Na Rynku

Możesz w pełni zbudować na gotowych modułach wprost z `scikit-learn` bez ręcznego pisania własnych z wywołań jak poniżej podane pod budowę predykcyjnego estymatora by uwolnić z narzutu i pozbawić z ujęcia nieprzydatne w oparciu na algorytmiczne moduły obciążające modelujące śmieci i zmienne do usunięcia.

```python
from sklearn.feature_selection import (
    VarianceThreshold,
    mutual_info_classif,
    RFE,
    SelectFromModel,
)
from sklearn.linear_model import Lasso, LogisticRegression
from sklearn.ensemble import RandomForestClassifier

# Szybkie wycięcie i odcięcie szumu i ułożonego braku do wariancji bez korelacji do testu 
vt = VarianceThreshold(threshold=0.01)
X_filtered = vt.fit_transform(X)

# Inteligentne wycenienie na zjawiska nieliniowe z ocenieniem i uwarunkowaniem do z ocen
mi_scores = mutual_info_classif(X_filtered, y)

# Precyzyjna głęboko z iteracjami wyrzucana z dokładnością o testy predykcyjne dla wyrzucania do oceny i z zachowaniem testowych RFE po eliminacji na cechach
rfe_selector = RFE(LogisticRegression(), n_features_to_select=10)
rfe_selector.fit(X_filtered, y)
X_rfe = rfe_selector.transform(X_filtered)

# Potężna naturalnie wygaszająca do idealnego do Zera na wagach za pośrednictwem bezwzględnej cięcia matematycznej dla siatki rygorów nakładanych przez L1 (Lasso) po użytych o karach z parametrem pod L1
lasso_selector = SelectFromModel(Lasso(alpha=0.01))
lasso_selector.fit(X_filtered, y)
```

### Konsekwencje Na Linii Po Wyeliminowaniu Szumu (To Do Wysyłki Na Środowisko)
Pamiętaj o tym co niesie za sobą waga tego działu. Z wiedzy o obcięciach użyteczności uzyskasz potężny zestaw merytoryczny pod ręką z drzewem szybkiego decyzyjnego dla inżynierów z predykcyjnymi do wdrożeń w wyciągniętym po pliku:
- `outputs/skill-feature-selector.md` – skonsolidowana skondensowana tablica i ściągawka z objaśnieniem dla poprawnego od rygorów pod używanie predykcyjnych modeli użytecznych klasyfikacyjnych ze zoptymalizowanymi predykcyjnymi u odciętych i wyselekcjonowanych modeli decyzyjnych po wycięciach śmieciowych zmiennych dla odciążenia predykcyjnego.
