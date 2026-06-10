# Obsługa Niezrównoważonych Danych

> Kiedy 99% Twoich danych reprezentuje "stan normalny", poleganie na dokładności to oszukiwanie samego siebie.

**Typ:** Kompilacja
**Język:** Python
**Wymagania wstępne:** Faza 2, lekcje 01-09 (w szczególności metryki ewaluacyjne)
**Czas:** ~90 minut

## Cele edukacyjne

- Pełna implementacja i zrozumienie działania algorytmu SMOTE (od zera) – przyswojenie różnic między syntetycznym nadpróbkowaniem (oversamplingiem) a zwykłą, naiwną duplikacją.
- Ewaluacja niezrównoważonych klasyfikatorów przy wykorzystaniu skutecznych metryk: miary F1, AUPRC oraz współczynnika korelacji Matthewsa (MCC), a nie mylącej dokładności (accuracy).
- Biegłe porównywanie ze sobą trzech fundamentalnych strategii: wagowania klas, optymalizacji progów decyzyjnych oraz resamplingu. Umiejętność doboru optymalnej ścieżki w zależności od zaobserwowanego poziomu nierównowagi.
- Konstrukcja solidnego, odpornego potoku przetwarzania (pipeline), integrującego SMOTE, ważenie klas oraz precyzyjne strojenie progów.

## Problem biznesowy

Opracowujesz złożony model do wykrywania nadużyć finansowych (fraud detection). System chwali się dokładnością rzędu 99,9%. Sukces? Chwilę później uświadamiasz sobie, że model przewiduje brak oszustwa przy absolutnie każdej, pojedynczej transakcji. 

Algorytm nie zawiera błędu w implementacji – z punktu widzenia matematycznej optymalizacji to w pełni racjonalne, obiektywne zachowanie. Skoro faktyczne oszustwa stanowią zaledwie 0,1% wszystkich transakcji, to dla algorytmu ciągłe i ślepe zgadywanie "klasy większościowej" jest najprostszą, najbardziej optymalną drogą do natychmiastowego zminimalizowania błędu całkowitego. Model ma technicznie stuprocentową rację, ale z punktu widzenia biznesu jest absolutnie i jednoznacznie bezużyteczny.

To zjawisko występuje nagminnie tam, gdzie wychwycenie incydentu jest faktycznym i najważniejszym celem, np.:
- Medyczna diagnoza rzadkiego schorzenia (wskaźnik 1% chorych).
- Detekcja krytycznych włamań do sieci teleinformatycznej (0,01% ruchu).
- Wykrywanie niebezpiecznych usterek w rygorystycznym i nowoczesnym procesie fabrycznym (wada zdarza się u 0,5% wyprodukowanych elementów).
- Agresywny system filtrowania poczty (20% to uciążliwy spam).
- Przewidywanie groźnej dla firmy rezygnacji klienta (zaledwie 5% abonentów w ujęciu miesięcznym).

Im bardziej konsekwentne i niebezpieczne jest wpadnięcie na dany punkt ze zbioru patologii (klasa mniejszościowa), tym zazwyczaj jest on coraz to rzadszy z natury. Klasyczna metryka dokładności ponosi sromotną, nieodwołalną porażkę, gdyż po prostu punktuje i uwypukla każde jednorodne przewidywanie jednakowo i naiwnie. Sukces przy detekcji w pełni legalnej transakcji, która mogła nie być weryfikowana ma u klasyfikatora to samo mierzalne zjawiskowo przełożenie z wagą i nagrodą taką samą jak zatrzymanie milionowej próby oszustwa. Jednak to dla wyeliminowania oszustw został zaprogramowany system. Czas więc odciąć i przestroić o 180 stopni paradygmaty, techniki wpajania wiedzy w sieci oraz uformować proces karania za pudło tak by siłą i sprytem nakazać maszynie analitycznej wzrok przesunąć w samą mniejszość.

## Koncepcja teoretyczna

### Bolesna prawda o mierzeniu dokładnością

Przeanalizuj zbiór próbny złożony ze 1000 transakcji: 990 absolutnie negatywnych (czystych) i ledwie 10 pozytywnych (brudnych, oszukańczych). Algorytm przewidujący notorycznie negatyw uderza z następującą skutecznością:

|  | Model prognozuje Negatyw | Model prognozuje Pozytyw |
|--|---|---|
| Stan faktyczny (Brudne, Pozytyw) | 10 (Niewychwycone False Negatives) | 0 (Brak True Positives) |
| Stan faktyczny (Czyste, Negatyw) | 990 (Trafione True Negatives) | 0 (Pomyłki False Positives) |

Dokładność liczona naiwnie = (0 + 990) / 1000 = obłędne 99,0%.

Architektura predykcyjna poniosła w rzeczywistości porażkę nie dając firmie ochrony. 0 schwytanych na oszustwie. Puste sieci, wymknięcia zagrażające kapitałowi na potęgę. Dlatego miara ta powinna być nałożona z rygorystycznym filtrem bezużyteczności i na stałe zakazana.

### Użyteczne środowisko weryfikacyjne dla nierównowagi

**Precision (Precyzja)** = TP / (TP + FP). Ze wszystkich alarmów załączonych i wrzuconych do analityka pod zdefiniowany "incydent", ile realnie okazywało się potężnym strzałem obiektywnym faktem? Wysokie liczby na tym wskaźniku to pewność na uniknięcie i zaprzestanie lawiny i sztormu kosztownych, męczących fałszywych alarmów uderzających na biurko inżynierów z SOC (Security Operations Center).

**Recall (Czułość, Pamięć)** = TP / (TP + FN). Nałożone z perspektywy samego występowania nieczystych uderzeń. Mając podaną, absolutną prawdę na wystąpienie setki ataków, ilu ze złośliwych morderców ujęto przy sieci na gorącym uderzeniu?

**Skonsolidowany F1-Score** = 2 * (Precyzja * Czułość) / (Precyzja + Czułość). Agregowana silną, dławiącą odchyły harmonijną wielomianem kompozycja oceny, bezlitosna z natury dla drastycznej różnicy. Model faworyzujący jedną w stronę zapominania drugiej zostanie matematycznie skarcony w dół o rzędy.

**Parametr F-beta** = Przesuń bezwiednie suwak i wagę faworyzowania pod rygor z beta. Gdzie z mnożnikiem np. beta o wartości > 1 waga i nacisk priorytetowo przenosi siły na wykrycie za wszelką cenę zdarzenia (odnajduje zastosowania idealne na wdrożeniach medycznych gdzie poświadczenie błędnego przeoczenia skazuje na katastrofę, zaś zbędny fałszywy alarm skazuje pacjenta jedynie na nieszkodliwe chociaż stresujące dopytujące kolejne pogłębione badania medyczne). Model klasyczny gdzie wskaźnik beta jest znacznie niższy w ułamkach podbija priorytetyzowanie w Precyzji oszczędzając denerwujących pomyłek do analityków. W modelowaniu na fraudy nagminnie z powodzeniem adaptuje się system we wzmocnionym wskaźniku wariantu pod szyldem wielomianu F2.

**Odczyty Krzywej z AUPRC** (Area Under the Precision-Recall Curve). Znane AUC-ROC oszukuje nagminnie dając poczucie zadowolenia na sztucznych urojonych wysokościach rzędu .90 gdzie klasy bywają ułożone w olbrzymim rozszczepieniu. Wykres z AUPRC oparty na czułości od precyzji odsłania bezpardonowo bez maskowania faktyczne porażki z modelem nie radzącym sobie w asymilacji na trudnych skrajnie zbiorach mniejszości. Obarczona wynikiem linia losowa w teście ląduje nisko (z miarą w punkt obiektywnego balansu odsetku bazy) więc najmniejsza potyczka uwydatniona.

**Obciążenie Korelacji Matthewsa (MCC)** = Bada z bezwzględnością we wzorcu czy architekt w wdrażanym rozwiązaniu w obydwóch równocześnie przestrzeniach dowozi trafienia. Wylicza miary z marginesów na plus minus w granicach jedności i uderzy z siłą sprowadzając wynik ku 0 przy bezmyślnych odczytach o ślepych rzutach dla faworyzacji i odrzutu jednej. Idealnie uodporniony mechanicznie do stosowania i miar dla głęboko z natury niesymetrycznych zbiorów.

Dla rzuconego we wdrożenie w opisie wyżej przykładu naiwnego generatora samych uderzeń o "Negatywie" wyniki spadają bezbłędnie z hukiem obnażając zjawisko do cna w liczbach przy precyzji w dzieleniu pod błędne zera i z MCC na nierozerwalnym odczycie dla rygoru na czyste 0. Algorytmy pomiarowe jednoznacznie zdiagnozowały i rzetelnie uświadomiły nieuchronnie o katastrofie.

## Zbuduj to i użyj (Scikit-Learn / Imbalanced-Learn)

Korzystając z dobrodziejstw z ekosystemów i paczek jak z uczenia w bibliotece scikit oraz użytego środowiska uzupełniającego u deweloperów o dopisku imbalanced-learn rozwiązania te powołuje się na jednym rzucie kodu:

```python
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline

# Klasyczne wdrożenie użycia argumentu klas z parametrem wagi odwróconego balansu 
model_weighted = LogisticRegression(class_weight="balanced")
model_weighted.fit(X_train, y_train)

# Techniki oparte o resampling ujęte bez skomplikowanego rygoru z pętlami SMOTE w potoku
pipeline = Pipeline([
    ("smote", SMOTE(random_state=42)),
    ("model", LogisticRegression())
])
pipeline.fit(X_train, y_train)
```

Natywne, manualne implementacje algorytmów uwydatniają precyzyjnie operacyjny cel: algorytmiczne wstawienie i zaaranżowanie do modelu klas SMOTE ujawnia, iż owa konstrukcja opiera się banalnie na zjawisku operacyjnym opartym w swej sile uwarunkowanym interpolacją geometryczną splecionym dla przestrzeni z prostym wyliczaniem wielomianowym algorytmu k-NN na klasach po mniejszości. 

Optymalizowanie strojenia parametrów o z góry nie uwarunkowanych ścisłymi sztywnymi wyuczonymi narzutami na rygory o progu decyzyjnym (Cut-Off Point) dla predykcji sprowadza po stronie inżyniera optymalne wyciąganie prostej i celującej pętli z iteracjami (for-over loop) testującej weryfikującej na wylot wartości predykcyjne dla zagnieżdżonego testowego ucięcia. Odrzucasz w procesie przysłowiowe urojone na twardo granice .50 do zróżnicowania klasy w binarnym, dla lepszej biznesowej uogólniającej statystyki. 

## Wyślij to
Lekcja produkuje aktywa merytoryczne i narzędzia:
- `outputs/skill-imbalanced-data.md` – skondensowana i profesjonalna strategia merytoryczna na szybkie wdrożenie i odpowiednie ułożenie u programisty środowiska pracującego nad silnie niesymetrycznym balansem klas w procesie modelowania danych z odniesieniem.
