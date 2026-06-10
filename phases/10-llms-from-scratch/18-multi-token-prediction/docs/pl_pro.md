# Przewidywanie wielu tokenów (MTP)

> Każdy autoregresyjny LLM — od GPT-2 po Llamę 3 — trenuje z jedną stratą na pozycję: przewiduj kolejny token. DeepSeek-V3 dołożył drugą stratę na pozycję: przewiduj token następny po następnym. Dodatkowe 14B parametrów (w modelu 671B) zostało przesączone z powrotem do modelu głównego przez przepływ gradientowy, a wytrenowane głowice MTP można ponownie wykorzystać podczas wnioskowania jako kreślarzy dekodowania spekulatywnego — ze współczynnikiem akceptacji ponad 80%. Przepustowość generacji wzrosła 1,8-krotnie niemal bez dodatkowego kosztu. Niniejsza lekcja buduje sekwencyjny moduł MTP zgodnie z raportem technicznym DeepSeek, oblicza stratę i rozkład parametrów wspólnej głowicy, a także wyjaśnia, dlaczego sekwencyjne MTP zachowuje łańcuch przyczynowy, podczas gdy oryginalny równoległy MTP Gloeckle'a i in. go zrywał.

**Typ:** Kompilacja
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 10 · 04 (wstępne szkolenie mini GPT), Faza 10 · 15 (dekodowanie spekulatywne)
**Czas:** ~60 minut

## Cele nauczania

- Przedstawić cel trenowania MTP i obliczyć łączną stratę dla zadanych głębokości przewidywania.
- Wyjaśnić różnicę między równoległymi głowicami MTP (Gloeckle i in., 2024) a sekwencyjnymi modułami MTP (DeepSeek-V3) oraz uzasadnić, dlaczego konstrukcja sekwencyjna zachowuje łańcuch przyczynowy.
- Obliczyć liczbę parametrów i obciążenie pamięci związane z dodawaniem modułów MTP do przebiegu przedtreningowego.
- Zaimplementować od podstaw jeden moduł MTP: wspólne osadzanie, blok transformatora dla każdej głębokości, rzutowanie oraz wspólną głowicę wyjściową.

## Problem

Przewidywanie kolejnego tokena jest standardowym celem trenowania LLM. Każdy ukryty stan jest nadzorowany tak, by przewidzieć dokładnie jedno: bezpośrednio następujący token. To zaskakująco słaby sygnał. Większość informacji w sekwencji — struktura, spójność, wiarygodność faktyczna, przepływ arytmetyczny — wykracza poza pojedynczy symbol. Model musi zrekonstruować te wzorce, gromadząc miliardy szczątkowych sygnałów jednotokenowych z bilionów tokenów.

MTP stawia pytanie: co by się stało, gdyby każdy ukryty stan był nadzorowany w kierunku przewidywania kilku przyszłych tokenów jednocześnie? Gloeckle i in. (Meta, 2024) wykazali, że takie podejście przynosi korzyści. Ich rozwiązanie polegało na umieszczeniu kilku niezależnych głowic wyjściowych na szczycie szkieletu, z których każda przewidywała inne przesunięcie. Proste i równoległe — ale każda głowica widziała ten sam ukryty stan bez hierarchicznego doprecyzowania, a przewidywania nie były ze sobą przyczynowo powiązane. Nie można było zatem użyć ich w dekodowaniu spekulatywnym.

DeepSeek-V3 (grudzień 2024) przeprojektował MTP jako moduły sekwencyjne, które zachowują łańcuch przyczynowy na każdej głębokości przewidywania. Model przewiduje `t+1` na podstawie `h_i^(0)`, a następnie przewiduje `t+2` na podstawie nowego ukrytego stanu `h_i^(1)`, który łączy `h_i^(0)` z osadzeniem `E(t+1)`, i tak dalej. Każda głębokość to osobny, niewielki blok transformatora. Wspólne osadzanie i wspólna głowica wyjściowa zapewniają umiarkowany narzut parametrów. W skali DeepSeek-V3 moduły MTP wnoszą 14B dodatkowych parametrów ponad 671B wag modelu głównego. Ten narzut rzędu 2% kupił jednocześnie gęstszy sygnał treningowy oraz gotowy mechanizm dekodowania spekulatywnego przy wnioskowaniu.

Niniejsza lekcja buduje od podstaw pojedynczy moduł MTP i stratę dla głębokości D. Matematyka jest przejrzysta, a implementacja mieści się w 150 liniach kodu.

## Koncepcja

### Sekwencyjny przepis MTP

DeepSeek-V3 dodaje `D` modułów MTP na szczycie modelu głównego. Każdy moduł `k` (dla `k = 1..D`) przewiduje token na głębokości `k` — czyli `t_{i+k}` z prefiksu przechodzącego przez pozycję `i`.

Moduł `k` składa się z:

- Bloku transformatorowego `T_k` z własną uwagą i MLP.
- Macierzy rzutowania `M_k`, która łączy ukryty stan z poprzedniej głębokości z osadzeniem tokena referencyjnego kolejnej głębokości.
- Wspólnego osadzania `E` (takiego samego jak w modelu głównym).
- Wspólnej głowicy wyjściowej `Out` (takiej samej jak w modelu głównym).

Podczas trenowania, dla prefiksu do pozycji `i`, ukryty stan według głębokości wynosi:

```
h_i^(0) = main model backbone at position i
h_i^(k) = T_k( M_k * concat(RMSNorm(h_i^(k-1)), RMSNorm(E(t_{i+k}))) )   for k >= 1
```

Przewidywanie na głębokości `k`:

```
logits_{i+k} = Out(h_i^(k-1))   for k = 1..D
```

Strata na głębokość to entropia krzyżowa względem wartości referencyjnej `t_{i+k}`:

```
L_k = CE(logits_{i+k}, t_{i+k})
```

Łączna strata po wszystkich głębokościach:

```
L_MTP = (lambda / D) * sum_{k=1..D} L_k
```

`lambda` to niewielki współczynnik wagowy — DeepSeek-V3 stosuje wartość 0,3 przez pierwsze 10% treningu, a następnie 0,1. Całkowita strata treningowa wynosi `L_main + L_MTP`.

### Dlaczego sekwencyjne, a nie równoległe

Oryginalny równoległy MTP Gloeckle'a miał D głowic wyjściowych, każda zastosowana bezpośrednio do `h_i^(0)`. Każda przewidywała `t_{i+k}` na podstawie tego samego ukrytego stanu szkieletu. Taki układ sprawdza się podczas trenowania, lecz przewidywania nie zależą od siebie nawzajem — nie można wykorzystać wyjścia `head_1`, by wesprzeć `head_2`, ponieważ głowice działają równolegle.

Sekwencyjny projekt DeepSeek-V3 buduje `h_i^(k)` na bazie `h_i^(k-1)` oraz rzeczywistego osadzenia kolejnego tokena `E(t_{i+k})`. Zachowuje to łańcuch przyczynowy: aby przewidzieć `t_{i+k+1}`, moduł na głębokości `k+1` ma dostęp do informacji o `t_{i+k}`. Jest to strukturalnie tożsame z tym, jak dekoder autoregresyjny konsumuje własne wyjście — dzięki czemu moduły MTP można bezpośrednio wykorzystać jako kreślarzy dekodowania spekulatywnego.

Krótko: przekaż `h_i^(k-1)` oraz roboczy token `t_{i+k}` do modułu `k+1`, a otrzymasz prognozę dla `t_{i+k+1}`. Powtarzaj. To dokładnie projekt w stylu EAGLE, w którym wytrenowany moduł MTP pełni rolę sieci roboczej. DeepSeek-V3 raportuje ponad 80% akceptacji pierwszego modułu MTP i przyspieszenie rzędu 1,8x.

### Rozliczanie parametrów

Dla modelu z wymiarem ukrytym `h` i słownikiem o rozmiarze `V`:

- Model główny: miliardy parametrów plus jedna głowica wyjściowa o rozmiarze `V * h`.
- Wspólna głowica wyjściowa: ponowne użycie głowicy modelu głównego. Brak dodatkowych parametrów.
- Wspólne osadzanie: ponowne użycie tablicy osadzania modelu głównego. Brak dodatkowych parametrów.
- Jeden moduł MTP:
  - Rzutowanie `M_k`: `(2h) * h = 2h^2`.
  - Blok transformatorowy `T_k`: uwaga (`4h^2` dla MHA) plus MLP (zazwyczaj `8h^2` dla SwiGLU przy stosunku 8/3). Łącznie około `12h^2` na blok.

Całkowity narzut na moduł: `~14h^2`. Dla `h = 7168` w DeepSeek-V3 i D = 1 moduł: `~14 * 7168^2 = ~720M` parametrów. DeepSeek-V3 raportuje 14B — różnica wynika przede wszystkim z tego, że warstwy eksperckie w module MTP zachowują strukturę MoE modelu głównego.

### Zysk z dekodowania spekulatywnego

Podczas przedtrenowania moduły MTP spowalniają trening o około 10% (więcej obliczeń w przód, dodatkowe straty). W zamian uzyskuje się dwojaką korzyść:

1. Gęstszy sygnał treningowy. Każdy ukryty stan podlega D+1 celom nadzoru. Zmierzony wpływ na MMLU, GSM8K, MATH i HumanEval: stała poprawa o kilka punktów procentowych w ablacjach DeepSeek-V3.

2. Gotowy mechanizm dekodowania spekulatywnego przy wnioskowaniu. Moduł MTP jest już wytrenowany do przewidywania kilku kolejnych tokenów. Użyty jako sieć robocza, osiąga współczynnik akceptacji ponad 80%. Przy takim poziomie dekodowanie spekulatywne z N=3 lub N=5 kandydatami daje przepustowość 1,8x. Koszt trenowania rzędu 10% zwraca się przy pierwszym uruchomieniu wnioskowania.

### Powiązanie z EAGLE

EAGLE trenuje mały model dodatkowy osobno, po zakończeniu przedtrenowania. MTP wbudowuje analogiczny projekt bezpośrednio w fazę przedtreningową. Oba podejścia osiągają zbliżone współczynniki akceptacji, lecz dochodzą do nich różnymi ścieżkami:

| Wymiar | EAGLE-3 | MTP (DeepSeek-V3) |
|----------|---------|--------------------------------|
| Kiedy trenowany | Po treningu przedtreningowym | Podczas treningu przedtreningowego |
| Kompatybilność wsteczna z istniejącymi wagami | Tak | Nie (wymaga ponownego trenowania) |
| Projekt parametrów | 1–2 warstwy transformatora | 1 blok transformatorowy + rzutowanie |
| Wskaźnik akceptacji | 0,88–0,92 | 0,80+ na głębokości 1 |
| Korzyści poza przyspieszeniem | Tylko dekodowanie spekulatywne | Gęstszy sygnał treningowy + przyspieszenie |

## Zbuduj to

`code/main.py` buduje od początku do końca pojedynczy moduł MTP: wspólne osadzanie, rzutowanie, blok transformatora i wspólną głowicę wyjściową. Następnie oblicza stratę entropii krzyżowej na głębokość dla krótkiej sekwencji syntetycznej i wypisuje liczbę parametrów z podziałem na składniki. Zabawkowy słownik 32 tokenów zapewnia czytelność wyników.

### Krok 1: wspólna tablica osadzania

Pojedyncza tablica `vocab_size x hidden` jest używana przez model główny oraz przez każdy moduł MTP na każdej głębokości. Nie kopia — dosłownie ten sam tensor.

### Krok 2: łączenie głębokości

```python
def combine(prev_hidden, next_token_embed, M_k):
    # concat along feature dim, then project down to hidden
    concat = rms_norm(prev_hidden) + rms_norm(next_token_embed)  # vector addition stand-in
    projected = matvec(M_k, concat)
    return projected
```

Właściwy DeepSeek-V3 łączy dwa wektory po RMSNorm w wektor `[2h]` i rzutuje go macierzą `h x 2h`. Wersja zabawkowa używa dodawania wektorów dla zwięzłości w ramach stdlib.

### Krok 3: blok transformatora dla głębokości k

Uwaga własna plus MLP. W wersji zabawkowej jednowarstwowy liniowy blok uwagi i MLP SwiGLU uwidaczniają strukturę bez potrzeby korzystania z biblioteki numpy.

### Krok 4: wspólna głowica wyjściowa

Ponowne użycie rzutowania wyjściowego modelu głównego. Produkuje logity nad słownikiem.

### Krok 5: strata na głębokości

Entropia krzyżowa softmax(logits) względem tokena referencyjnego przy przesunięciu `k`. Straty z poszczególnych głębokości są agregowane ze współczynnikiem skalowania `lambda / D`.

### Krok 6: rozliczanie parametrów

Wypisz całkowitą liczbę parametrów, liczbę parametrów współdzielonych (osadzanie, głowica) oraz liczbę dodatkowych parametrów na moduł. Pokaż stosunek narzutu MTP do rozmiaru modelu głównego.

## Zastosowania

MTP jest zintegrowany z DeepSeek-V3 (grudzień 2024) i serią DeepSeek-R1. Podczas wnioskowania:

- Własny stos obsługujący DeepSeek używa modułów MTP jako spekulatywnych dekoderów od razu po wyjęciu z pudełka.
- vLLM i SGLang posiadają ścieżki integracji dla DeepSeek-V3 MTP od kwietnia 2026.
- Poradnik AMD ROCm SGLang przedstawia konkretną konfigurację dekodowania spekulatywnego MTP ze zmierzonym przyspieszeniem 1,8x dla punktu kontrolnego V3.

Kiedy stosować MTP w nowym przebiegu przedtreningowym:

- Kontrolujesz pełny potok przedtreningowy i zależy ci na gęstszym sygnale treningowym.
- Wiesz, że model będzie obsługiwany na dużą skalę i chcesz bezpłatnie uzyskać dekodowanie spekulatywne.
- Twój wymiar ukryty wynosi co najmniej 4096. W skali 1B narzut bardziej szkodzi, niż pomaga.

Kiedy nie stosować:

- Dostrajanie istniejącego, wstępnie wytrenowanego, gęstego modelu. Moduł MTP nie będzie wytrenowany.
- Modele badawcze, w których potrzebujesz czystej linii bazowej do porównań. MTP zmienia architekturę.

## Produkt lekcji

Lekcja tworzy plik `outputs/skill-mtp-planner.md`. Na podstawie specyfikacji przebiegu przedtreningowego (rozmiar modelu, dane, obliczenia) zwraca plan integracji MTP: liczba głębokości D, harmonogram `lambda`, obciążenie pamięci oraz okablowanie dekodowania spekulatywnego przy wnioskowaniu.

## Ćwiczenia

1. Uruchom `code/main.py`. Sprawdź, czy strata na głębokość maleje monotonicznie wraz ze wzmacnianiem sygnału syntetycznego. Zmodyfikuj dane syntetyczne tak, by używały stałego wzorca, i zweryfikuj, czy straty na głębokości 1 i 2 zbiegają się.

2. Oblicz narzut parametrów dla gęstego modelu 70B (ukryty wymiar 8192, 80 warstw) z modułem MTP D=1. Porównaj z raportowanym przez DeepSeek-V3 narzutem 14B. Wyjaśnij, dlaczego liczba DeepSeek jest wyższa: blok transformatora MTP dziedziczy tę samą strukturę MoE co model główny, co zawyża liczbę parametrów na moduł.

3. Zaimplementuj D=2 w wersji zabawkowej: dodaj drugi moduł MTP pobierający h^(1) i przewidujący `t_{i+2}`. Sprawdź, czy łączna strata i rozliczenie parametrów odpowiadają równaniom 19–21 z artykułu DeepSeek.

4. Przełącz wersję zabawkową na równoległe MTP (w stylu Gloeckle'a): dodaj D głowic wyjściowych na szczycie głównego ukrytego stanu, z których każda przewiduje inne przesunięcie. Porównaj straty na głębokość z wersją sekwencyjną na tym samym sygnale syntetycznym. Wersja sekwencyjna powinna dawać niższą stratę na głębokości k dla k > 1, ponieważ opiera się na pośrednich przewidywaniach.

5. Użyj wytrenowanego modułu MTP jako sieci roboczej w stylu EAGLE: wywołaj moduł k, by zaproponować `t_{i+k}` podczas wnioskowania. Zmierz współczynnik akceptacji tych tokenów roboczych w porównaniu z przewidywaniami modelu głównego na wstrzymanej sekwencji. Wynik powyżej 50% na wersji zabawkowej potwierdza odtworzenie empirycznej właściwości MTP jako mechanizmu roboczego.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to naprawdę oznacza |
|------|----------------|--------------------------------------|
| Moduł MTP | „Dodatkowa strata na blokadę" | Niewielki blok transformatora z rzutowaniem, przewidujący token na pozycji `k` od modelu głównego |
| Głębokość przewidywania | „Jakie przesunięcie" | Liczba całkowita `k`, taka że moduł `k` przewiduje `t_{i+k}` z prefiksu do pozycji `i` |
| Równoległe MTP | „Styl Gloeckle'a" | D niezależnych głowic na tym samym ukrytym stanie szkieletu, bez łańcucha warunkowego |
| Sekwencyjne MTP | „Styl DeepSeek-V3" | Każdy moduł jest warunkowany ukrytym stanem poprzedniej głębokości oraz osadzeniem kolejnego tokena; zachowuje łańcuch przyczynowy |
| Wspólna głowica wyjściowa | „Ponowne użycie głównej głowicy" | Moduły MTP wywołują głowicę LM modelu głównego zamiast osobnej projekcji wyjściowej |
| Wspólne osadzanie | „Ponowne użycie głównej tablicy" | Ta sama tablica osadzania słownika jest używana wszędzie; brak zduplikowanych parametrów |
| Macierz rzutowania M_k | „Połącz ukryty + kolejny token" | Warstwa liniowa `h x 2h` składająca poprzedni ukryty stan i osadzenie tokena docelowego na wejście kolejnej głębokości |
| Łączna strata L_MTP | „Uśrednione straty dodatkowe" | Średnia arytmetyczna strat entropii krzyżowej na głębokość, przeskalowana przez `lambda` |
| Wskaźnik akceptacji na głębokości 1 | „Jak często projekt MTP się zgadza" | Częstość, z jaką token przewidziany przez moduł MTP D=1 zgadza się z przewidywaniem modelu głównego; ponad 80% w DeepSeek-V3 |
| Ważenie lambda | „Waga dodatkowych strat" | Współczynnik skalowania na głębokość; 0,3 na początku treningu, 0,1 w późniejszej fazie w DeepSeek-V3 |

## Dalsze czytanie

- [DeepSeek-AI — Raport techniczny DeepSeek-V3 (arXiv:2412.19437)](https://arxiv.org/abs/2412.19437) — pełny opis sekwencyjnego MTP (sekcja 2.2), w tym równania łącznej straty i przyspieszenie 1,8x przy wnioskowaniu
- [Gloeckle i in. — Lepsze i szybsze duże modele językowe dzięki przewidywaniu wielu tokenów (arXiv:2404.19737)](https://arxiv.org/abs/2404.19737) — równoległy projekt bazowy, który DeepSeek-MTP ulepsza
- [Karta modelu DeepSeek-V3 na Hugging Face](https://huggingface.co/deepseek-ai/DeepSeek-V3) — łącznie 685B (671B model główny + 14B MTP), uwagi dotyczące wdrożenia
- [Leviathan i in. — Szybkie wnioskowanie z transformatorów poprzez dekodowanie spekulatywne (arXiv:2211.17192)](https://arxiv.org/abs/2211.17192) — struktura, do której projekt dekodowania spekulatywnego MTP się odwołuje
- [Li i in. — EAGLE-3 (arXiv:2503.01840)](https://arxiv.org/abs/2503.01840) — projekt architektury EAGLE z 2025 roku, odpowiednik podejścia MTP
