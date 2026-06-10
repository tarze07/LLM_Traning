# Wstępny trening CLIP i kontrastowego języka wzrokowo-językowego

> Projekt CLIP (2021) OpenAI udowodnił, że pojedynczy pomysł jest wystarczająco duży, aby napędzać następne pięć lat: wyrównanie kodera obrazu i kodera tekstu w tej samej przestrzeni wektorowej, wykorzystując wyłącznie zaszumione pary obraz-podpis w Internecie i stratę kontrastu. Zero nadzorowanych etykiet. 400 milionów par. Powstała przestrzeń do osadzania dokonuje klasyfikacji zerowej, pobiera obraz-tekst i podłącza się do każdego VLM 2026 jako jego wieża wizyjna. SigLIP 2 (2025) zastąpił softmax sigmoidem i przeskalował się w porównaniu z CLIP niższym kosztem. W tej lekcji omówiono obliczenia od InfoNCE do utraty sigmoid w parach i omówiono etap uczenia w stdlib Python.

**Typ:** Kompilacja
**Języki:** Python (stdlib, InfoNCE + implementacje strat sigmoidalnych)
**Wymagania wstępne:** Faza 12 · 01 (łaty ViT), Faza 7 (Transformatory)
**Czas:** ~180 minut

## Cele nauczania

- Wyprowadź straty InfoNCE na podstawie wzajemnych informacji i zaimplementuj stabilną numerycznie wersję wektorową.
- Wyjaśnij, dlaczego utrata par sigmoidalnych (SigLIP) skaluje się do partii 32768+ bez wymagań softmax typu all-gather.
- Uruchom klasyfikację ImageNet metodą zerową, konstruując szablony tekstowe (`a photo of a {class}`) i biorąc argmax na podstawie podobieństwa cosinus.
- Wymień cztery dźwignie, które zapewnia wstępne szkolenie CLIP / SigLIP: wielkość partii, temperatura, szablon podpowiedzi, jakość danych.

## Problem

Wizja przed CLIP była nadzorowana. Zbieraj oznaczone zbiory danych (ImageNet: 1,2 mln obrazów, 1000 klas), szkol CNN i wysyłaj je. Etykiety są drogie, są stronnicze w stosunku do tego, na co mogą się zgodzić wytwórcy etykiet, a etykiet nie można przenieść do nowych zadań bez dopracowania.

W sieci podpisów do obrazów dostępnych jest bezpłatnie ponad miliard par luźno oznakowanych obrazów. Zdjęcie golden retrievera z tekstem alternatywnym „mój pies Max w parku” niesie ze sobą sygnał nadzoru — tekst opisuje zdjęcie. Pytanie: czy możesz zamienić to w przydatne szkolenie?

Odpowiedź CLIP: traktuj pary obrazów i podpisów jako pasujące zadanie. Biorąc pod uwagę partię N obrazów i N podpisów, naucz się dopasowywać każdy obraz do jego własnego podpisu względem czynników rozpraszających N-1. Nadzór polega na tym, że „te dwie rzeczy należą do siebie; te N-1 nie”. Brak etykiet klas. Brak ludzkiej adnotacji. Po prostu kontrastowa strata.

Powstała przestrzeń do osadzania robi więcej, niż był szkolony CLIP. Funkcja zerowego zdjęcia ImageNet działa, ponieważ „zdjęcie kota” jest umieszczane w pobliżu zdjęć kotów, które nigdy nie były wyraźnie oznaczone jako koty. To jest zakład, który pojawiał się w każdym VLM w 2026 roku.

## Koncepcja

### Podwójny koder

CLIP posiada dwie wieże:

- Koder obrazu `f`: ViT lub ResNet, generuje wektor D-dim na obraz.
- Koder tekstu `g`: mały transformator, generuje wektor D-dim na podpis.

Obie wieże normalizują swoje wyjścia do długości jednostkowej. Podobieństwo jest `cos(f(x), g(y)) = f(x)^T g(y)`, ponieważ oba są normami jednostkowymi.

Dla partii N par (obraz, podpis) zbuduj macierz podobieństwa `S` o kształcie `(N, N)`:

```
S[i, j] = cos(f(x_i), g(y_j)) / tau
```

gdzie `tau` to wyuczona temperatura (CLIP inicjuje wartość 0,07; nauczona jest w przestrzeni dziennika).

### Utrata InfoNCE

CLIP wykorzystuje symetryczną entropię krzyżową w wierszach i kolumnach:

```
loss_i2t = CE(S, labels=identity)     # each image's positive is its own caption
loss_t2i = CE(S^T, labels=identity)   # each caption's positive is its own image
loss = (loss_i2t + loss_t2i) / 2
```

To jest InfoNCE. Softmax w CE zmusza każdy obraz do dopasowania podpisu bardziej niż jakikolwiek inny podpis w partii. „Negatywy” to wszystkie pozostałe pozycje wsadowe. Większe partie = więcej negatywów = silniejszy sygnał. CLIP przeszkolony w partii 32 tys.; skala ma znaczenie.

### Temperatura

`tau` kontroluje ostrość softmax. Niskie tau → ostry rozkład, twardy negatywny efekt wydobycia. Wysokie tau → miękkie, wszystkie próbki mają swój udział. CLIP uczy się log(1/tau), obcinany, aby zapobiec zawaleniu. SigLIP 2 naprawia początkowe tau i zamiast tego wykorzystuje wyuczone odchylenie.

### Dlaczego esicy lepiej się łuszczą (SigLIP)

Softmax wymaga synchronizacji całej macierzy podobieństwa. W szkoleniu rozproszonym musisz zebrać wszystkie osady w każdej replice, a następnie wykonać softmax. Jest to kwadratowa wielkość świata dla komunikacji.

SigLIP zastępuje softmax elementarną sigmoidą: dla każdej pary `(i, j)` strata jest binarną klasyfikacją „czy to pasująca para?” etykiety klas dodatnich są przekątną, wszystko inne jest ujemne. Strata wynosi:

```
L = -1/N sum over (i, j) [ y_ij log sigmoid(S[i,j]) + (1-y_ij) log sigmoid(-S[i,j]) ]
```

`y_ij = 1` jeśli `i == j`, w przeciwnym razie 0. Strata każdej pary jest niezależna. Nie ma potrzeby gromadzenia się wszystkich osób. Każdy procesor graficzny oblicza swój lokalny blok i sumy. SigLIP 2 umożliwia tanie skalowanie wsadowe od 32 tys. do 512 tys. tam, gdzie CLIP wymagałby proporcjonalnie większej komunikacji.

### Klasyfikacja zerowego strzału

Biorąc pod uwagę N nazw klas, dla każdej klasy zbuduj szablon tekstowy:

```
"a photo of a {class}"
```

Osadź każdy szablon za pomocą kodera tekstu. Osadź swój obraz za pomocą kodera obrazu. Podobieństwo cosinus Argmax = klasa przewidywana. Brak szkoleń na docelowych zajęciach.

Szybkie szablony mają znaczenie. W oryginalnym artykule CLIP wykorzystano 80 szablonów na zajęcia (zwykłe, artystyczne, fotograficzne, malarskie itp.) i uśredniono osadzenie. +3 punkty ImageNet. Współczesne użycie zazwyczaj wybiera jeden lub dwa szablony.

### Sondy liniowe i dostrajanie

Zero-shot to podstawa. Sonda liniowa (trenuj jedną warstwę liniową na podstawie zamrożonych funkcji CLIP dla klas docelowych) przewyższa zero-shot w przypadku zadań w domenie. Pełne dostrojenie przewyższa sondę liniową w domenie, ale może zaszkodzić transferowi zerowemu. Trzy reżimy z trzema kompromisami.

### SigLIP 2: NaFlex i gęste funkcje

SigLIP 2 (2025) dodaje:
- NaFlex: pojedynczy model obsługuje różne współczynniki proporcji i rozdzielczości.
— Lepsze funkcje gęstej segmentacji i szacowania głębokości, mające na celu wykorzystanie ich jako zamrożonego szkieletu w VLM.
- Wielojęzyczny: przeszkolony w ponad 100 językach, gdzie CLIP był dostępny tylko w języku angielskim.
- Skala parametrów 1B, gdzie CLIP osiągnął szczyt na poziomie 400M.

W otwartych VLM na rok 2026 domyślną wieżą wizyjną jest SigLIP 2 SO400m/14. CLIP pozostaje ustawieniem domyślnym w przypadku pobierania czystego obrazu i tekstu, gdzie specyficzna dystrybucja uczenia LAION-2B pasuje do wzorca zapytania.

### ALIGN, PODSTAWOWE, OpenCLIP, EVA-CLIP

ALIGN (Google, 2021): ten sam pomysł co CLIP, skala par 1,8B, 90% szumów. Udowodniono, że skale danych są zaszumione. OpenCLIP (LAION): otwarta reprodukcja CLIP-a na LAION-400M / 2B, wiele skal, otwarty punkt kontrolny. EVA-CLIP: inicjuje z modelowania zamaskowanego obrazu; mocny szkielet dla VLM. BASIC: hybryda CLIP+ALIGN firmy Google. Cała ta sama rodzina, różne dane i tuning.

### Sufit zero-shotowy

Modele klasy CLIP zapewniają około 76% zera ImageNet (CLIP-G, OpenCLIP-G). Beyond wymaga albo znacznie większych danych (SigLIP 2 uzyskuje ponad 80%), albo zmian w architekturze (nadzorowane głowice, więcej parametrów). Benchmark się nasyca; prawdziwą wartością jest przestrzeń do osadzania, którą zużywają dalsze VLM.

## Użyj tego

`code/main.py` implementuje:

1. Podwójny koder zabawek (funkcje obrazu oparte na skrótach, funkcje znaków tekstowych), dzięki czemu można zobaczyć kształt InfoNCE bez numpy.
2. Strata InfoNCE w czystym Pythonie (stabilność numeryczna poprzez log-sum-exp).
3. Strata w parach esicy dla porównania.
4. Procedura klasyfikacji zero-shot: obliczenie podobieństwa cosinus na podstawie zestawu podpowiedzi tekstowych, argmax do przewidywania.

Uruchom go i obserwuj krzywą strat. Liczby bezwzględne to zabawka; kształtem odpowiada temu, co emituje prawdziwy trener CLIP.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-clip-zero-shot.md`. Mając zestaw obrazów (poprzez ścieżkę) i listę klas docelowych, tworzy podpowiedzi tekstowe przy użyciu szablonu CLIP, osadza obie strony z określonym punktem kontrolnym (np. `openai/clip-vit-large-patch14`) i zwraca przewidywania z pierwszą/piątką z wynikami podobieństwa. Umiejętność odmawia zgłaszania roszczeń dotyczących klas, których nie ma na liście podpowiedzi.

## Ćwiczenia

1. Ręcznie zaimplementuj InfoNCE dla partii 4 par. Skonstruuj macierz podobieństwa 4x4, uruchom softmax, wybierz przekątną i oblicz entropię krzyżową. Sprawdź swoją implementację Pythona pod kątem tych ręcznych obliczeń.

2. SigLIP oprócz temperatury wykorzystuje parametr odchylenia `b`: `S'[i,j] = S[i,j]/tau + b`. Jaką rolę odgrywa `b`, gdy w partii występuje duża nierównowaga klas (znacznie więcej negatywów niż pozytywów w wierszu)? Przeczytaj sekcję 3 SigLIP (arXiv:2303.15343).

3. Zbuduj klasyfikator zerowego strzału dla kotów i psów. Wypróbuj dwa szablony podpowiedzi: `a photo of a {class}` i `a picture of a {class}`. Zmierz dokładność na 100 obrazach testowych. Czy zestaw szablonów przebija singiel?

4. Oblicz koszt komunikacji softmax InfoNCE w porównaniu z sigmoidem w parach dla procesora 512-GPU w partii 32 tys. Które skalują się jako O(N), a które jako O(N^2)? Cytuj sekcję 4 SigLIP.

5. Przeczytaj dokument dotyczący praw skalowania OpenCLIP (arXiv:2212.07143, Cherti i in.). Odtwórz ich wnioski dotyczące skalowania danych na podstawie rysunków: jaka jest logarytmiczno-liniowa zależność między dokładnością zera ImageNet a rozmiarem danych szkoleniowych przy ustalonym rozmiarze modelu?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| InformacjeNCE | „Strata kontrastowa” | Entropia krzyżowa w macierzy podobieństwa partii; plus każdego elementu to jego sparowany element, negatywy to cała reszta |
| Utrata esicy | „Utrata SigLIP” | Binarna entropia krzyżowa na parę; bez softmax, bez all-gather, skaluje się tanio w szkoleniach rozproszonych |
| Temperatura | "tau" | Skalar skalujący logity przed softmax/esigmoidem; kontroluje ostrość dystrybucji |
| Zerowy strzał | „klasyfikacja bez dostrojenia” | Używaj podpowiedzi tekstowych do konstruowania osadzania klas i klasyfikowania według podobieństwa cosinus; brak szkoleń na zajęciach docelowych |
| Szablon podpowiedzi | "zdjęcie ..." | Ramka tekstowa wokół nazwy klasy; wpływa na celność zerowego strzału o 1-5 punktów |
| Podwójny koder | „Dwie wieże” | Jeden koder obrazu + jeden koder tekstu, wyjścia we współdzielonej przestrzeni D-dim |
| Twardy negatyw | „Twardy rozpraszacz” | Negatyw na tyle podobny do pozytywu, że model musi pracować, aby je rozdzielić |
| Sonda liniowa | „Mrożone + jedna warstwa” | Trenuj tylko klasyfikator liniowy na podstawie zamrożonych obiektów; mierzy jakość cech |
| NaFlex | „Natywna elastyczna rozdzielczość” | Możliwość SigLIP 2 do pozyskiwania obrazów w dowolnym formacie i rozdzielczości bez zmiany rozmiaru |
| Skalowanie temperatury | „tau sparametryzowane logarytmicznie” | CLIP parametryzuje `log(1/tau)`, aby zachować gradienty; klipsy zapobiegające zapadnięciu się do wartości tau bliskiej zeru |

## Dalsze czytanie

- [Radford i in. — Uczenie się możliwych do przeniesienia modeli wizualnych na podstawie nadzoru nad językiem naturalnym (arXiv:2103.00020)](https://arxiv.org/abs/2103.00020) — artykuł CLIP.
- [Zhai i in. — Utrata esicy na potrzeby wstępnego szkolenia obrazu językowego (arXiv:2303.15343)](https://arxiv.org/abs/2303.15343) — SigLIP.
- [Tschannen i in. — SigLIP 2 (arXiv:2502.14786)](https://arxiv.org/abs/2502.14786) — wielojęzyczny + NaFlex.
- [Jia i in. — ALIGN (arXiv:2102.05918)](https://arxiv.org/abs/2102.05918) — skala z zaszumionymi danymi internetowymi.
- [Cherti i in. — Powtarzalne prawa skalowania do nauki kontrastowego obrazu językowego (arXiv:2212.07143)](https://arxiv.org/abs/2212.07143) — Prawa skalowania OpenCLIP.