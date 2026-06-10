# Transformatory wizyjne i prymitywne tokeny patchów

> Zanim powstanie jakikolwiek model multimodalny, obraz musi zostać przekształcony w sekwencję tokenów, które transformator będzie w stanie przetworzyć. Przełomowy artykuł o ViT z 2020 roku rozwiązał ten problem, wprowadzając podział na patche (fragmenty) o wymiarach 16x16 pikseli, projekcję liniową i kodowanie pozycyjne (positional embeddings). Pięć lat później każdy wiodący model z 2026 roku (Claude 4.7 Opus działający w natywnej rozdzielczości 2576 pikseli, Gemini 3.1 Pro, Qwen3.5-Omni) wciąż zaczyna pracę w ten sposób. Choć zmieniono koder z podstawowego ViT na DINOv2 lub SigLIP 2, dodano tokeny rejestrów (register tokens), a schemat kodowania pozycyjnego ewoluował do 2D-RoPE, podstawowy prymityw pozostał bez zmian. W tej lekcji prześledzimy potok tokenizacji patchów od początku do końca i zaimplementujemy go przy użyciu wyłącznie biblioteki standardowej Pythona, aby zbudować solidny model mentalny dla „tokenów wizualnych”.

**Typ:** Ucz się
**Języki:** Python (biblioteka standardowa, tokenizator patchów + kalkulator geometrii)
**Wymagania wstępne:** Faza 7 (Transformatory), Faza 4 (Wizja komputerowa)
**Czas:** ~120 minut

## Cele nauczania

- Konwersja obrazu o wymiarach $H \times W \times 3$ na sekwencję tokenów patchów z prawidłowym kodowaniem pozycyjnym.
- Obliczanie długości sekwencji, liczby parametrów i operacji FLOPs dla modelu ViT o zadanym rozmiarze patcha, rozdzielczości, wymiarze ukrytym (hidden dim) i liczbie warstw (depth).
- Omówienie trzech kluczowych usprawnień, które pozwoliły ViT przejść od fazy badawczej w 2020 r. do produkcji w 2026 r.: samonadzorowanego uczenia wstępnego (self-supervised pre-training np. DINO / MAE), tokenów rejestrów (register tokens) oraz pakowania obrazów w ich natywnej rozdzielczości.
- Świadomy wybór między poolingiem CLS (CLS pooling), poolingiem średnim (mean pooling) a tokenami rejestrów w kolejnych zadaniach.

## Problem

Transformatory operują na sekwencjach wektorów. Tekst w naturalny sposób stanowi sekwencję (bajtów lub tokenów). Obraz natomiast jest dwuwymiarową siatką pikseli o trzech kanałach kolorów. Gdybyśmy spłaszczyli każdy piksel z osobna, obraz RGB o wymiarach 224x224 dałby sekwencję o długości 150 528 tokenów – a mechanizm self-attention (samouważności) przy takiej długości odpada na starcie ze względu na kwadratową złożoność obliczeniową.

W podejściach sprzed 2020 roku na początku stosowano ekstraktor cech CNN: na przykład ResNet generował mapę cech o wymiarach 7x7 złożoną z wektorów o długości 2048, przekazując te 49 tokenów do transformatora. Rozwiązanie to działało, ale obarczało model ograniczeniami typowymi dla CNN (indukcyjne skrzywienie lokalności, translacyjna ekwiwariancja) i pozbawiało transformator możliwości pełnego skalowania.

Dosovitskiy i in. (2020) zadali proste pytanie: co jeśli całkowicie pominiemy CNN? Podzielmy obraz na fragmenty (patche) o stałym rozmiarze (np. 16x16 pikseli), zrzutujmy liniowo każdy patch na wektor, dodajmy kodowanie pozycyjne i przekażmy taką sekwencję do klasycznego transformatora. W tamtym czasie była to rewolucja – wizja komputerowa pozbawiona splotów. Jednak przy odpowiednio dużej ilości danych treningowych (JFT-300M, a później LAION), model ten pokonał architektury ResNet na zbiorze ImageNet i wykazał doskonałą skalowalność.

Do 2026 roku prymityw ViT stał się niekwestionowanym standardem. Każdy nowoczesny model VLM o otwartych wagach wykorzystuje koder oparty na tej architekturze (DINOv2, SigLIP 2, CLIP, EVA, InternViT). Pytanie nie brzmi już: „czy powinniśmy używać patchów?”, ale: „jaki rozmiar patcha wybrać, jak zarządzać rozdzielczością, jaki cel uczenia wstępnego przyjąć i jakiego kodowania pozycyjnego użyć”.

## Koncepcja

### Patche jako tokeny

Mając obraz `x` o kształcie `(H, W, 3)` oraz rozmiar patcha `P`, dzielimy obraz na siatkę nienakładających się fragmentów o wymiarach `(H/P) x (W/P)`. Każdy patch to blok pikseli o wymiarach `P x P x 3`. Spłaszczamy go do wektora o długości `3 * P^2`. Następnie stosujemy wspólny rzut liniowy `W_E` o kształcie `(3 * P^2, D)`, aby odwzorować każdy patch na wymiar ukryty (hidden dimension) modelu `D`.

Dla klasycznej konfiguracji ViT-B/16:
- Rozdzielczość 224, rozmiar patcha 16 → siatka 14x14 → 196 tokenów patchów.
- Każdy patch zawiera `16 x 16 x 3 = 768` wartości pikseli, rzutowanych na wymiar `D = 768`.
- Dodajemy specjalny, uczony token klasy `[CLS]` → ostateczna długość sekwencji wynosi 197.

Z matematycznego punktu widzenia projekcja patcha jest tożsama ze splotem 2D (Conv2D) z rozmiarem jądra `P`, krokiem (stride) `P` oraz `D` kanałami wyjściowymi. W kodzie produkcyjnym implementuje się to dokładnie w ten sposób: `nn.Conv2d(3, D, kernel_size=P, stride=P)`. Sformułowanie „projekcja liniowa” służy opisowi koncepcyjnemu, podczas gdy operacja splotu jest zoptymalizowana sprzętowo.

### Kodowanie pozycyjne (Positional Embeddings)

Tokeny patchów nie mają wrodzonej informacji o swoim położeniu w przestrzeni – bez dodatkowych danych transformator traktuje je jak nieuporządkowany zbiór. Wczesne wersje ViT dodawały uczone jednowymiarowe kodowanie pozycyjne (wektor o wymiarze `D` dla każdej z pozycji). To podejście działa, ale ściśle wiąże model z rozdzielczością obrazu użytą podczas treningu: przy wnioskowaniu na innej rozdzielczości konieczna jest interpolacja tabeli pozycji.

Nowoczesne architektury wizyjne stosują dwuwymiarowe obrotowe kodowanie pozycyjne 2D-RoPE (np. M-RoPE w Qwen2-VL, domyślne w SigLIP 2) lub faktoryzowane pozycje 2D. 2D-RoPE obraca wektory zapytań (queries) i kluczy (keys) na podstawie indeksu wiersza i kolumny patcha. Dzięki temu model podczas wnioskowania bezpośrednio odczytuje relacje przestrzenne z kąta obrotu, co eliminuje potrzebę utrzymywania tabeli pozycji i pozwala na obsługę obrazów o dowolnych proporcjach i rozdzielczościach.

### Token CLS, pooling wyjściowy i tokeny rejestrów (Register Tokens)

Jak uzyskać reprezentację całego obrazu na wyjściu? Stosuje się trzy podejścia:

1. **Token `[CLS]`:** Do sekwencji patchów dołącza się uczony wektor. Na wyjściu sieci stan ukryty tego tokena służy za reprezentację całego obrazu (wzorzec zapożyczony z modelu BERT). Stosowany w oryginalnym ViT oraz CLIP.
2. **Pooling średni (Mean Pooling):** Uśrednia się stany ukryte wszystkich tokenów patchów na wyjściu z transformatora. Stosowany w SigLIP, DINOv2 oraz większości nowoczesnych modeli VLM.
3. **Tokeny rejestrów (Register Tokens):** Darcet i in. (2023) zauważyli, że modele ViT trenowane bez jawnego tokena wyjściowego gromadzą specyficzne artefakty – tokeny o bardzo wysokich normach w obszarach tła, które zaburzają mechanizm samouważności. Dodanie od 4 do 16 dodatkowych, uczonych tokenów rejestrów „pochłania” te artefakty, co znacząco poprawia jakość reprezentacji lokalnych (np. w zadaniach segmentacji czy estymacji głębi). Zarówno DINOv2, jak i SigLIP 2 wykorzystują tokeny rejestrów.

Wybór ten ma kluczowe znaczenie. CLS i pooling świetnie nadają się do klasyfikacji. W przypadku modeli VLM przekazujących tokeny bezpośrednio do LLM, pooling jest pomijany – każdy token patcha staje się osobnym tokenem wejściowym dla LLM, natomiast tokeny rejestrów są odrzucane przed przekazaniem danych dalej (pełnią rolę techniczną w koderze).

### Metody uczenia wstępnego (Pre-training)

Pierwsze modele ViT z 2020 roku były trenowane w sposób nadzorowany (supervised classification) na zbiorze JFT-300M. Szybko zastąpiono to bardziej efektywnymi metodami:

- **CLIP (2021):** Uczenie kontrastowe obraz-tekst na parach danych (400 milionów par). Szczegóły w lekcji 12.02.
- **MAE (2021, He et al.):** Maskowanie 75% patchów i rekonstrukcja brakujących pikseli. Metoda samonadzorowana na surowych obrazach.
- **DINO (2021) / DINOv2 (2023):** Autodestylacja w układzie student-nauczyciel bez użycia etykiet ani opisów tekstowych. DINOv2 ViT-g/14 to obecnie jeden z najsilniejszych koderów cech wizualnych, stosowany powszechnie w zadaniach lokalnych.
- **SigLIP / SigLIP 2 (2023, 2025):** Ewolucja CLIP wykorzystująca sigmoidalną funkcję straty (sigmoid loss) oraz mechanizm NaFlex do obsługi natywnych proporcji obrazu. Jest to dominujący koder wizualny w otwartych modelach VLM w 2026 roku (Qwen, Idefics2, LLaVA-OneVision).

Sposób uczenia wstępnego determinuje zastosowanie kodera: CLIP/SigLIP najlepiej sprawdza się w dopasowywaniu semantycznym z tekstem, DINOv2 w zadaniach wymagających precyzyjnych cech geometrycznych i lokalnych, a MAE stanowi świetną bazę do dalszego fine-tuningu.

### Prawa skalowania (Scaling Laws)

Badania nad skalowaniem ViT (Zhai et al. 2022) wykazały, że jakość modeli rośnie w przewidywalny sposób wraz ze wzrostem parametrów, wolumenu danych i nakładów obliczeniowych. Przy określonym budżecie obliczeniowym:
- Większy model wyszkolony na większej ilości danych zapewnia lepsze rezultaty.
- Rozmiar patcha jest kluczowym parametrem kontrolującym długość sekwencji i wierność detali. Patch o rozmiarze 14 (stosowany w DINOv2/SigLIP SO400m) generuje więcej tokenów na obraz niż patch 16, co poprawia wyniki w zadaniach typu OCR czy analizie drobnych szczegółów, kosztem większego narzutu obliczeniowego.
- Rozdzielczość wejściowa to kolejny istotny parametr. Zwiększenie rozdzielczości (np. z 224 do 384 lub 512) niemal zawsze podnosi jakość, ale koszt obliczeniowy (FLOPs) rośnie kwadratowo.

Modele takie jak ViT-g/14 (1B parametrów, patch 14, rozdzielczość 224 → 256 tokenów) oraz SigLIP SO400m/14 (400M parametrów, patch 14) stanowią bazę dla wielu współczesnych systemów VLM.

### Obliczanie parametrów ViT

Szczegółowy kod obliczeniowy znajduje się w pliku `code/main.py`. Przykładowa kalkulacja dla modelu ViT-B/16 przy rozdzielczości 224:

```
patch_embed = 3 * 16 * 16 * 768 + 768  =  591k
cls + pos    = 768 + 197 * 768          =  152k
block        = 4 * 768^2 (QKVO) + 2 * 4 * 768^2 (MLP) + 2 * 2*768 (LN)
             = 12 * 768^2 + 3k          =  7.1M
12 blocks    = 85M
final LN    = 1.5k
total       ≈ 86M
```

Znajomość tych szacunków pozwala określić narzut pamięciowy (VRAM) przed załadowaniem wag modelu.

### Konfiguracja produkcyjna w 2026 roku

Najbardziej popularnym otwartym koderem wizualnym w 2026 roku jest SigLIP 2 SO400m/14 z technologią natywnej elastycznej rozdzielczości (NaFlex). Cechuje się on:
- Rozmiarem 400M parametrów.
- Rozmiarem patcha 14, co przy domyślnej rozdzielczości 384 generuje 729 tokenów patchów na obraz.
- Stosowaniem pooling średniego dla zadań klasyfikacji; w systemach VQA wszystkie 729 tokenów trafia bezpośrednio do LLM.
- Wykorzystaniem 4 tokenów rejestru (register tokens), które są odrzucane przed przekazaniem sekwencji do LLM.
- Kodowaniem 2D-RoPE z dynamicznym skalowaniem rozdzielczości w celu obsługi natywnych proporcji obrazu.

Każda z tych decyzji projektowych wynika bezpośrednio z publikacji naukowych, które warto przeanalizować.

## Kod praktyczny

Plik `code/main.py` zawiera prosty tokenizator patchów oraz kalkulator parametrów geometrycznych. Przyjmuje on parametry obrazu (szerokość `W`, wysokość `H`), rozmiar patcha `P`, wymiar ukryty `D` oraz liczbę warstw `L`, a następnie wylicza:

- Wymiary siatki patchów oraz ostateczną długość sekwencji.
- Sekwencję tokenów dla syntetycznego obrazu o rozmiarze 8x8 pikseli (proces spłaszczania i projekcji liniowej).
- Liczbę parametrów z rozbiciem na warstwę projekcji, kodowanie pozycyjne, bloki transformatora oraz głowicę wyjściową.
- Liczbę operacji FLOPs na jeden krok w przód (forward pass) przy docelowej rozdzielczości.
- Porównanie konfiguracji dla popularnych modeli: ViT-B/16 @ 224, ViT-L/14 @ 336, DINOv2 ViT-g/14 @ 224 oraz SigLIP SO400m/14 @ 384.

Uruchom ten skrypt, aby zweryfikować zgodność obliczeń z oficjalnymi metrykami modeli i przeanalizować wpływ zmiany rozmiaru patcha oraz rozdzielczości na liczbę generowanych tokenów.

## Zastosowanie (Skill)

Ta lekcja udostępnia prompt `outputs/skill-patch-geometry-reader.md`. Na podstawie parametrów ViT (rozmiar patcha, rozdzielczość, wymiar ukryty, głębokość) wylicza on liczbę tokenów, liczbę parametrów oraz szacowane zużycie pamięci VRAM. Używaj tego narzędzia przy doborze kodera wizualnego dla VLM, aby zapobiec problemom z przepełnieniem kontekstu LLM (token explosion).

## Ćwiczenia

1. Oblicz długość sekwencji tokenów patchów dla modelu Qwen2.5-VL przy natywnej rozdzielczości wejściowej 1280x720 i rozmiarze patcha 14. Porównaj ten wynik z podejściem opartym wyłącznie na tokenie CLS.
2. Ile tokenów wygeneruje pojedyncza klatka wideo o rozdzielczości 1080p (1920x1080) przy rozmiarze patcha 14? Ile tokenów wizualnych wygeneruje 5-minutowe wideo przy 30 klatkach na sekundę? Która technika przyniesie największe oszczędności: pooling, redukcja klatek (frame sampling) czy agregacja tokenów (token merging)?
3. Zaimplementuj pooling średni (mean pooling) dla tokenów patchów w czystym Pythonie. Zweryfikuj, czy uśrednienie 196 tokenów wyjściowych z modelu DINOv2 daje wynik tożsamy z osadzeniem zbiorczym zwracanym bezpośrednio przez metodę `forward` modelu.
4. Przeczytaj sekcję 3 publikacji „Vision Transformers Need Registers” (arXiv:2309.16588). Wyjaśnij w dwóch zdaniach, jakie artefakty są absorbowane przez tokeny rejestrów i dlaczego ma to znaczenie dla dokładności prognoz lokalnych.
5. Zmodyfikuj skrypt `code/main.py` tak, aby obsługiwał technikę patch-n'-pack: dla listy obrazów o różnych rozdzielczościach stwórz jedną spakowaną sekwencję wraz z maską uwagi (attention mask) o strukturze blokowo-przekątnej. Szczegóły znajdziesz w lekcji 12.06.

## Kluczowe terminy

| Termin | Potoczne określenie | Co to dokładnie oznacza |
|------|----------------|--------------------------------------|
| Patch (fragment) | „Kwadrat 16x16 pikseli” | Nienakładający się fragment obrazu o stałym rozmiarze, przekształcany w pojedynczy token. |
| Osadzanie patcha (Patch Embedding) | „Projekcja liniowa” | Wspólna macierz wag (lub warstwa Conv2D z krokiem P) mapująca spłaszczone piksele patcha na wektor o wymiarze D. |
| Token CLS | „Token klasy” | Uczony wektor dołączany do sekwencji, którego końcowy stan reprezentuje globalne cechy obrazu; opcjonalny w modelach z 2026 r. |
| Token rejestru (Register Token) | „Token ujścia (sink)” | Dodatkowe uczone tokeny absorbujące artefakty uwagi (wysokie normy wektorów) powstające podczas uczenia wstępnego ViT. |
| Kodowanie pozycyjne (Positional Embedding) | „Informacja o pozycji” | Wektor lub operacja obrotu przypisywana do pozycji patcha w celu zachowania informacji przestrzennej; standardem jest 2D-RoPE. |
| Siatka (Grid) | „Siatka patchów” | Dwuwymiarowy układ patchów o wymiarach (H/P) x (W/P) dla danej rozdzielczości i rozmiaru patcha. |
| NaFlex | „Natywna elastyczna rozdzielczość” | Rozwiązanie w SigLIP 2 pozwalające modelowi obsługiwać różne proporcje i rozdzielczości obrazu bez ponownego trenowania. |
| Koder bazowy (Backbone) | „Wieża wizyjna” | Wstępnie wytrenowany koder obrazu dostarczający tokeny wizualne do modelu językowego (LLM) w strukturze VLM. |
| Pooling | „Agregacja cech obrazu” | Metoda redukcji tokenów patchów do jednego wektora reprezentacji (np. przez CLS, uśrednianie lub mechanizm uwagi). |
| Patch 14 vs 16 | „Gęsta vs rzadka siatka” | Rozmiar 14 generuje więcej tokenów, co poprawia dokładność (np. przy OCR), ale zwiększa koszt obliczeniowy w porównaniu do rozmiaru 16. |

## Dalsze czytanie

- [Dosovitskiy et al. — An Image is Worth 16x16 Words (arXiv:2010.11929)](https://arxiv.org/abs/2010.11929) — Oryginalna publikacja wprowadzająca ViT.
- [He et al. — Masked Autoencoders Are Scalable Vision Learners (arXiv:2111.06377)](https://arxiv.org/abs/2111.06377) — Publikacja na temat MAE i samonadzorowanego uczenia wstępnego.
- [Oquab et al. — DINOv2 (arXiv:2304.07193)](https://arxiv.org/abs/2304.07193) — Praca opisująca metodę autodestylacji na dużą skalę bez użycia etykiet.
- [Darcet et al. — Vision Transformers Need Registers (arXiv:2309.16588)](https://arxiv.org/abs/2309.16588) — Analiza artefaktów uwagi i wprowadzenie tokenów rejestru.
- [Tschannen et al. — SigLIP 2 (arXiv:2502.14786)](https://arxiv.org/abs/2502.14786) — Specyfikacja nowoczesnego kodera wizualnego SigLIP 2.
- [Zhai et al. — Scaling Vision Transformers (arXiv:2106.04560)](https://arxiv.org/abs/2106.04560) — Empiryczne analizy praw skalowania dla architektury ViT.
