# Wstępny trening CLIP i kontrastowe uczenie wizualno-tekstowe

> Projekt CLIP (2021) autorstwa OpenAI udowodnił, że jedna prosta idea może zdominować rozwój sztucznej inteligencji na kolejne lata: dopasowanie kodera obrazu i kodera tekstu do tej samej przestrzeni wektorowej przy użyciu wyłącznie zaszumionych par obraz-podpis pobranych z Internetu oraz funkcji straty kontrastowej (contrastive loss). Bez żadnych etykiet nadzorowanych. Na bazie 400 milionów par. Powstała w ten sposób przestrzeń osadzeń (embeddings) umożliwia klasyfikację zero-shot, wyszukiwanie obraz-tekst (image-text retrieval) i służy jako koder wizualny (backbone) w niemal każdym zaawansowanym modelu VLM. Zaprezentowany później SigLIP (2023) i SigLIP 2 (2025) zastąpiły funkcję softmax funkcją sigmoidalną, co pozwoliło na lepsze skalowanie przy znacznie niższych kosztach obliczeniowych. W tej lekcji przeanalizujemy matematyczne podstawy od InfoNCE do sigmoidalnej funkcji straty i zaimplementujemy potok treningowy przy użyciu wyłącznie biblioteki standardowej Pythona.

**Typ:** Teoria i Kod (Kompilacja)
**Języki:** Python (biblioteka standardowa, InfoNCE + implementacje sigmoidalnej funkcji straty)
**Wymagania wstępne:** Faza 12 · 01 (tokeny patchów ViT), Faza 7 (Transformatory)
**Czas:** ~180 minut

## Cele nauczania

- Wyprowadzenie funkcji straty InfoNCE na bazie informacji wzajemnej (mutual information) i wdrożenie jej stabilnej numerycznie wersji wektorowej.
- Wyjaśnienie, dlaczego sigmoidalna funkcja straty (SigLIP) skaluje się efektywnie do rozmiarów batcha rzędu 32768+ bez konieczności synchronizacji all-gather wymaganej przez softmax.
- Implementacja klasyfikacji zero-shot na zbiorze ImageNet poprzez konstruowanie szablonów tekstowych (`a photo of a {class}`) i wybór klasy o najwyższym podobieństwie cosinusowym (argmax).
- Przeanalizowanie czterech głównych czynników wpływających na efektywność uczenia CLIP / SigLIP: rozmiaru batcha, temperatury, szablonów promptów oraz jakości danych.

## Problem

Przed pojawieniem się CLIP wizja komputerowa opierała się na uczeniu nadzorowanym. Wymagało to zbierania precyzyjnie etykietowanych zbiorów danych (np. ImageNet: 1,2 mln obrazów, 1000 klas), trenowania sieci CNN i wdrażania ich do konkretnych zadań. Proces ten był kosztowny, obarczony subiektywizmem adnotatorów, a uzyskane modele nie potrafiły adaptować się do nowych zadań bez kosztownego dostrajania (fine-tuningu).

Tymczasem w sieci dostępne są miliardy par obraz-podpis. Zdjęcie przedstawiające psa rasy golden retriever z tekstem alternatywnym „mój pies Max w parku” niesie ze sobą cenny sygnał nadzorowany – tekst bezpośrednio opisuje zawartość obrazu. Pytanie brzmiało: jak przekształcić ten zaszumiony zbiór w efektywny proces uczenia?

Odpowiedzią CLIP było sformułowanie zadania jako dopasowywania par obraz-tekst. Dla batcha o rozmiarze $N$ (zawierającego $N$ obrazów i $N$ podpisów) model uczy się przyporządkowywać każdy obraz do jego właściwego podpisu, traktując pozostałe $N-1$ podpisów jako elementy zakłócające (negatywne). Sygnał nadzorowany sprowadza się do reguły: „te dwa elementy pasują do siebie; pozostałe $N-1$ nie”. Bez sztywnych klas i bez ręcznego etykietowania – wyłącznie na bazie straty kontrastowej.

Powstała w ten sposób wspólna przestrzeń wektorowa potrafi znacznie więcej, niż zakładał pierwotny cel optymalizacji. Klasyfikacja zero-shot na zbiorze ImageNet działa tak dobrze, ponieważ fraza „zdjęcie kota” jest mapowana w pobliże reprezentacji obrazów kotów, mimo że model nigdy nie widział etykiety o takiej treści. To właśnie to podejście stanowi fundament współczesnych modeli VLM.

## Koncepcja

### Architektura Dual-Encoder (Dwuwieżowa)

Model CLIP składa się z dwóch niezależnych koderów:

- **Kodera obrazu `f`:** Sieci ViT lub ResNet, generującej wektor o wymiarze $D$ dla każdego obrazu.
- **Kodera tekstu `g`:** Małego transformatora, generującego wektor o wymiarze $D$ dla każdego podpisu.

Oba kodery normalizują swoje wektory wyjściowe do długości jednostkowej (L2 normalization). Podobieństwo między obrazem a tekstem oblicza się jako iloczyn skalarny, który ze względu na normalizację jest tożsamy z podobieństwem cosinusowym: $\text{cos}(f(x), g(y)) = f(x)^T g(y)$.

Dla batcha zawierającego $N$ par (obraz, podpis) tworzona jest macierz podobieństwa `S` o wymiarach $(N, N)$:

```
S[i, j] = cos(f(x_i), g(y_j)) / tau
```

gdzie `tau` to parametryzowana, uczona temperatura (CLIP inicjuje ją na poziomie 0,07; parametr jest optymalizowany w przestrzeni logarytmicznej).

### Funkcja straty InfoNCE

CLIP stosuje symetryczną entropię krzyżową (cross-entropy) dla wierszy i kolumn macierzy podobieństwa:

```
loss_i2t = CE(S, labels=identity)     # positive dla obrazu to jego własny podpis
loss_t2i = CE(S^T, labels=identity)   # positive dla podpisu to jego własny obraz
loss = (loss_i2t + loss_t2i) / 2
```

To jest właśnie strata InfoNCE. Zastosowanie funkcji softmax w entropii krzyżowej zmusza model do maksymalizacji podobieństwa poprawnej pary obraz-tekst w porównaniu do wszystkich pozostałych par w batchu. Rolę przykładów negatywnych pełnią pozostałe elementy w batchu. Większy rozmiar batcha oznacza więcej przykładów negatywnych, co przekłada się na silniejszy sygnał treningowy. Oryginalny CLIP był trenowany z batchem o rozmiarze 32 768.

### Rola temperatury (`tau`)

Parametr temperatury `tau` kontroluje ostrość rozkładu prawdopodobieństwa zwracanego przez softmax. Niska temperatura prowadzi do ostrego rozkładu i wymusza skupienie uwagi na najtrudniejszych przykładach negatywnych (hard negative mining). Wysoka temperatura wygładza rozkład, uwzględniając wpływ wszystkich próbek. CLIP uczy się parametru $\log(1/\tau)$, który jest ograniczany (clipped), aby zapobiec niestabilności treningu. SigLIP 2 rezygnuje z uczenia temperatury w ten sposób, stosując stałą wartość temperatury oraz uczony parametr przesunięcia (bias).

### Dlaczego sigmoidalna funkcja straty (SigLIP) lepiej się skaluje

Zastosowanie softmaxu wymaga wyznaczenia mianownika na bazie całego wiersza macierzy podobieństwa. W treningu rozproszonym na wielu procesorach graficznych (GPU) wymaga to kosztownej operacji synchronizacji `all-gather` w celu zebrania osadzeń (embeddings) ze wszystkich replik przed obliczeniem softmaxu. Generuje to duży narzut komunikacyjny rosnący kwadratowo wraz z rozmiarem sieci.

SigLIP zastępuje softmax prostą funkcją sigmoidalną aplikowaną niezależnie do każdej pary $(i, j)$. Zadanie sprowadza się do binarnej klasyfikacji: „czy ta konkretna para obraz-tekst pasuje do siebie?”. Pozycje na przekątnej macierzy stanowią klasę dodatnią ($y_{ij}=1$), a wszystkie pozostałe pozycje – klasę ujemną ($y_{ij}=0$). Wzór na funkcję straty wygląda następująco:

```
L = -1/N sum over (i, j) [ y_ij log sigmoid(S[i,j]) + (1-y_ij) log sigmoid(-S[i,j]) ]
```

Strata dla każdej pary obliczana jest niezależnie. Dzięki temu nie ma potrzeby globalnego zbierania wszystkich osadzeń – każdy GPU może przetwarzać swój lokalny blok macierzy podobieństwa. SigLIP umożliwia bezproblemowe skalowanie batcha od 32 000 do 512 000 przykładów przy minimalnym narzucie komunikacyjnym w porównaniu do klasycznego CLIP.

### Klasyfikacja Zero-Shot

Dla zbioru $N$ klas docelowych tworzy się szablony tekstowe (prompty):

```
"a photo of a {class}"
```

Każdy wygenerowany prompt jest przepuszczany przez koder tekstu. Obraz wejściowy jest kodowany przez koder obrazu. Klasyfikację przeprowadza się poprzez wybór klasy (argmax), której wektor cech wykazuje najwyższe podobieństwo cosinusowe z wektorem obrazu. Nie wymaga to dotrenowywania modelu na nowych klasach.

Szablony promptów mają kluczowe znaczenie. W oryginalnej publikacji CLIP autorzy uśredniali wektory dla 80 różnych szablonów na klasę (np. wersje artystyczne, zbliżenia, rysunki), co podniosło dokładność na ImageNet o 3 punkty procentowe. W codziennej praktyce produkcyjnej stosuje się zazwyczaj jeden lub dwa zoptymalizowane szablony.

### Sondy liniowe (Linear Probes) i Fine-tuning

Klasyfikacja zero-shot to najprostsza metoda ewaluacji. Zastosowanie sondy liniowej (linear probe – uczenie klasyfikatora liniowego na cechach z zamrożonego kodera CLIP) pozwala na uzyskanie lepszych rezultatów w konkretnej domenie. Pełny fine-tuning (dostrojenie wszystkich wag) daje najwyższą dokładność, ale może pogorszyć zdolności generalizacji (zero-shot transfer) modelu na inne domeny.

### SigLIP 2: NaFlex i cechy lokalne

Wprowadzona w 2025 roku wersja SigLIP 2 oferuje:
- **NaFlex (Native Flexible Resolution):** Możliwość przetwarzania obrazów o dowolnych proporcjach i rozdzielczościach bez deformacji obrazu.
- **Lepsze reprezentacje cech lokalnych:** Poprawiona dokładność w zadaniach takich jak segmentacja semantyczna czy estymacja głębi, co czyni go idealnym koderem bazowym (backbone) dla systemów VLM.
- **Wielojęzyczność:** Trening na parach obraz-tekst w ponad 100 językach (oryginalny CLIP obsługiwał głównie język angielski).
- **Skalowanie parametrów:** Modele o rozmiarach do 1B parametrów (oryginalny CLIP osiągał maksymalnie 400M parametrów).

W otwartych modelach VLM z 2026 roku standardowym koderem wizualnym jest SigLIP 2 SO400m/14. Klasyczny CLIP wciąż jest powszechnie stosowany w wyszukiwarkach obrazów i tekstu ze względu na specyfikę dystrybucji danych treningowych zbioru LAION-2B.

## Kod praktyczny

Skrypt `code/main.py` zawiera prostą implementację:

1. Zabawkowego modelu dwuwieżowego (generowanie cech obrazu na bazie skrótów i cech tekstu na bazie znaków), co pozwala przeanalizować działanie InfoNCE bez zewnętrznych bibliotek.
2. Stabilnej numerycznie funkcji straty InfoNCE w czystym Pythonie (z zastosowaniem triku log-sum-exp).
3. Sigmoidalnej funkcji straty dla porównania efektywności.
4. Procedury klasyfikacji zero-shot (obliczanie podobieństwa cosinusowego z zestawem promptów tekstowych i wybór klasy za pomocą argmax).

Uruchom skrypt, aby zaobserwować przebieg minimalizacji funkcji straty. Choć dane są syntetyczne, zachowanie funkcji straty odzwierciedla rzeczywisty proces uczenia modeli CLIP.

## Zastosowanie (Skill)

Ta lekcja udostępnia prompt `outputs/skill-clip-zero-shot.md`. Dla zestawu ścieżek do obrazów oraz listy klas docelowych generuje on prompty tekstowe przy użyciu szablonów CLIP, koduje obie reprezentacje wybranym modelem (np. `openai/clip-vit-large-patch14`) i zwraca predykcje Top-1 oraz Top-5 wraz z wynikami podobieństwa cosinusowego. Narzędzie automatycznie odrzuca próby klasyfikacji obiektów spoza zdefiniowanej listy klas.

## Ćwiczenia

1. Zaimplementuj ręcznie funkcję straty InfoNCE dla batcha składającego się z 4 par. Stwórz macierz podobieństwa 4x4, oblicz softmax, wybierz elementy na przekątnej i oblicz entropię krzyżową. Porównaj wyniki z działaniem kodu w Pythonie.
2. Funkcja straty SigLIP wykorzystuje dodatkowy uczony parametr przesunięcia (bias) `b`: $S'[i,j] = S[i,j]/\tau + b$. Wyjaśnij, jaką rolę pełni ten parametr przy dużej asymetrii liczby przykładów ujemnych do dodatnich w batchu. Pomocna będzie analiza sekcji 3 publikacji SigLIP (arXiv:2303.15343).
3. Zbuduj prosty klasyfikator zero-shot rozróżniający obrazy kotów i psów. Przetestuj dwa szablony promptów: `a photo of a {class}` oraz `a picture of a {class}`. Oceń ich dokładność na 100 obrazach testowych. Czy zastosowanie uśrednionego wektora z obu szablonów poprawia stabilność wyników w porównaniu do pojedynczego promptu?
4. Porównaj złożoność komunikacyjną obliczania softmaxu w InfoNCE z niezależną funkcją sigmoidalną dla klastra 512 GPU przy rozmiarze batcha 32 000. Które podejście skaluje się jako $O(N)$, a które jako $O(N^2)$? Odnieś się do sekcji 4 publikacji SigLIP.
5. Przeczytaj publikację na temat praw skalowania OpenCLIP (arXiv:2212.07143, Cherti et al.). Na podstawie wykresów opisz zależność między dokładnością zero-shot na ImageNet a rozmiarem zbioru treningowego przy stałym rozmiarze modelu. Czy jest to zależność logarytmiczno-liniowa?

## Kluczowe terminy

| Termin | Potoczne określenie | Co to dokładnie oznacza |
|------|----------------|--------------------------------------|
| InfoNCE | „Strata kontrastowa” | Entropia krzyżowa obliczana na macierzy podobieństwa batcha; poprawnym dopasowaniem dla każdego wiersza jest element na przekątnej, reszta to przykłady negatywne. |
| Sigmoidalna strata (Sigmoid Loss) | „Strata SigLIP” | Binarna entropia krzyżowa obliczana osobno dla każdej pary w macierzy; eliminuje potrzebę stosowania softmaxu i operacji all-gather. |
| Temperatura | „Parametr tau” | Współczynnik skalujący logity przed nałożeniem funkcji softmax lub sigmoid; reguluje ostrość rozkładu prawdopodobieństwa. |
| Zero-shot | „Klasyfikacja bez uczenia” | Wykorzystanie promptów tekstowych do wygenerowania osadzeń klas i klasyfikacji obrazu na podstawie podobieństwa cosinusowego bez modyfikacji wag modelu. |
| Szablon promptu (Prompt Template) | „Szablon tekstu” | Tekst otaczający nazwę klasy (np. „a photo of a {}”), poprawiający dokładność klasyfikacji zero-shot o kilka punktów procentowych. |
| Dual-Encoder (Dwuwieżowy) | „Dwie wieże” | Architektura składająca się z osobnego kodera obrazu i osobnego kodera tekstu, mapujących dane do tej samej przestrzeni ukrytej. |
| Trudny przykład negatywny (Hard Negative) | „Twardy negatyw” | Przykład negatywny, który jest bardzo podobny do pozytywnego, zmuszający model do precyzyjnego wyznaczania granic decyzyjnych. |
| Sonda liniowa (Linear Probe) | „Zamrożony model + klasyfikator” | Uczenie wyłącznie jednej warstwy liniowej na cechach wyjściowych z zablokowanego (zamrożonego) kodera wizyjnego. |
| NaFlex | „Elastyczna rozdzielczość” | Technologia w SigLIP 2 umożliwiająca koderowi przetwarzanie obrazów o dowolnych proporcjach bez konieczności zmiany ich wymiarów (resizing). |
| Skalowanie temperatury | „Uczone log-tau” | Parametryzacja temperatury jako $\log(1/\tau)$ w celu optymalizacji stabilności gradientów w trakcie uczenia kontrastowego. |

## Dalsze czytanie

- [Radford et al. — Learning Transferable Visual Models From Natural Language Supervision (arXiv:2103.00020)](https://arxiv.org/abs/2103.00020) — Oryginalna publikacja wprowadzająca model CLIP.
- [Zhai et al. — Sigmoid Loss for Language-Image Pre-Training (arXiv:2303.15343)](https://arxiv.org/abs/2303.15343) — Artykuł prezentujący architekturę SigLIP.
- [Tschannen et al. — SigLIP 2 (arXiv:2502.14786)](https://arxiv.org/abs/2502.14786) — Specyfikacja wielojęzycznego modelu SigLIP 2 z obsługą NaFlex.
- [Jia et al. — ALIGN (arXiv:2102.05918)](https://arxiv.org/abs/2102.05918) — Skalowanie uczenia kontrastowego na zaszumionych zbiorach danych pobranych z sieci.
- [Cherti et al. — Reproducible scaling laws for contrastive language-image learning (arXiv:2212.07143)](https://arxiv.org/abs/2212.07143) — Analiza praw skalowania na bazie modeli OpenCLIP.
