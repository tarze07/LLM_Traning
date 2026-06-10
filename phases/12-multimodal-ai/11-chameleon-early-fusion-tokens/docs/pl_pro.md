# Modele multimodalne oparte na wczesnej fuzji (Early Fusion) i tokenach Chameleon

> W klasycznych modelach VLM, które analizowaliśmy do tej pory, reprezentacje obrazu i tekstu są od siebie oddzielone. Tokeny wizualne generowane przez encoder wizyjny trafiają do projektora, a następnie są łączone z tekstem w warstwach LLM. Słowniki modeli wizyjnych i tekstowych nigdy się nie pokrywają. Autorzy modelu Chameleon (Meta, maj 2024) postawili pytanie: co się stanie, jeśli połączymy te przestrzenie? W tym celu wytrenowano moduł VQ-VAE, który konwertuje obraz do postaci sekwencji dyskretnych tokenów pochodzących ze wspólnego słownika. Dzięki temu każdy dokument multimodalny staje się jedną, spójną sekwencją — przeplatanymi tokenami tekstowymi i wizualnymi optymalizowanymi jedną autoregresyjną funkcją straty. Efekt uboczny: model potrafi generować odpowiedzi o mieszanej modalności — naprzemiennie tokeny tekstowe i obrazy w ramach jednego przebiegu wnioskowania. W tej lekcji przeanalizujemy teorię wczesnej fuzji (early fusion) i zaimplementujemy uproszczony potok od początku do końca.

**Typ:** Projekt / Implementacja
**Języki:** Python (biblioteka standardowa, tokenizer VQ-VAE + dekoder przeplatany)
**Wymagania wstępne:** Faza 12 · Lekcja 05, Faza 8 (Generatywna AI)
**Czas:** ~180 minut

## Cele nauczania

- Wyjaśnij, w jaki sposób wspólne słownictwo oraz pojedyncza funkcja straty wpływają na możliwości generatywne modelu.
- Zrozum proces tokenizacji obrazu przez VQ-VAE na sekwencję indeksów dyskretnych dopasowaną do zadania modelowania języka transformatora.
- Wskaż metody stabilizacji treningu w modelu Chameleon: QK-Norm, strategiczne rozmieszczenie dropoutu oraz kolejność warstw LayerNorm.
- Porównaj architekturę Chameleon z rozwiązaniem opartym na adapterze Q-Former w BLIP-2 i wskaż sytuacje optymalne dla każdego z nich.

## Problem

Modele VLM oparte na adapterach (np. LLaVA, BLIP-2, Qwen-VL) traktują tekst i obrazy jako niezależne byty. Token tekstowy jest przetwarzany przez `embed(text_token)`, natomiast obraz przechodzi przez `visual_encoder(image) → projector → pseudo_tokens`. Model posiada dwie oddzielne ścieżki wejściowe, które łączą się dopiero na dalszym etapie.

Niesie to ze sobą trzy konsekwencje:

1. Model LLM potrafi wyłącznie przetwarzać (rozumieć) obrazy, ale nie potrafi ich generować. Wyjściem modelu jest zawsze czysty tekst.
2. Obsługa dokumentów o mieszanej modalności (naprzemiennie występujące obrazy i tekst) jest skomplikowana — wymaga albo parsowania danych wejściowych poza modelem, albo budowania łańcuchów generowania.
3. Problem z dopasowaniem rozkładów. Tokeny wizualne oraz tekstowe znajdują się w innych obszarach przestrzeni ukrytej, co generuje subtelne błędy wyrównania.

Twórcy Chameleon odrzucili to założenie, uznając, że obrazy to po prostu sekwencje dyskretnych tokenów pochodzących ze wspólnego, zunifikowanego słownika. Trenując jeden model na przeplatanych dokumentach przy użyciu jednej autoregresyjnej funkcji straty, zyskujemy możliwość natywnej generacji treści o mieszanej modalności.

## Koncepcja

### Tokenizacja obrazu za pomocą VQ-VAE

Tokenizer w tym podejściu to wariacyjny autokoder skwantowany wektorowo (Vector Quantized Variational Autoencoder). Architektura:

- Encoder: Sieć CNN + ViT mapująca obraz na przestrzenną siatkę cech (np. siatka 32x32 o wymiarze 256).
- Codebook (książka kodowa): wyuczone słownictwo składające się z K wektorów (Chameleon używa K=8192), również o wymiarze 256.
- Kwantyzacja: dla każdej cechy przestrzennej wyszukiwany jest najbliższy wektor z książki kodowej (według odległości L2). Ciągła cecha zostaje zastąpiona dyskretnym indeksem (liczbą całkowitą).
- Decoder: Sieć CNN rekonstruująca skwantowane cechy z powrotem do postaci pikseli obrazu.

Proces treningu optymalizuje: stratę rekonstrukcji VAE + stratę zaangażowania (commitment loss) + stratę książki kodowej (codebook loss). Indeksy z książki kodowej tworzą dyskretny alfabet do opisu obrazów.

W modelu Chameleon pojedynczy obraz jest reprezentowany przez 32 * 32 = 1024 tokeny pobrane ze słownika o rozmiarze 8192. Są one łączone z tokenami tekstowymi (pochodzącymi z klasycznego słownika BPE o rozmiarze np. 32000). Ostateczny, zunifikowany słownik ma rozmiar 40192 tokenów. Transformator przetwarza jedną wspólną sekwencję pod kątem jednej funkcji straty.

### Wspólny słownik (Shared Vocabulary)

Słownik modelu Chameleon łączy w sobie tokeny tekstowe, wizualne oraz specjalne separatory modalności. Każdy token posiada unikalny identyfikator (ID). Wejściowa warstwa embeddingów mapuje każde ID na wektor w przestrzeni ukrytej o wymiarze D. Wyjściowa warstwa projekcji mapuje stany ukryte z powrotem na logity słownika. Funkcja softmax wybiera kolejny token bez względu na to, jakiej jest modalności.

Kluczowe znaczenie mają separatory: tagi `<image>` oraz `</image>` wyznaczają granice sekwencji tokenów obrazu. Jeśli podczas generowania model wyemituje token `<image>`, system wie, że kolejne 1024 tokeny to indeksy VQ, które należy przekazać do dekodera VQ-VAE w celu wygenerowania (wyrenderowania) pikseli obrazu.

### Generowanie w trybie mieszanym (Mixed-Modal Generation)

Wnioskowanie polega na przewidywaniu kolejnego tokenu ze wspólnego słownika. Dla promptu: „Narysuj kota i opisz go”, Chameleon generuje wyjście w formacie:

```
<image> 4821 1029 2891 ... (1024 tokeny obrazu) </image>
The cat is orange, sitting on a windowsill...
```

Model autonomicznie decyduje o kolejności generowania — może najpierw wygenerować obraz, potem tekst, odwrotnie, lub przeplatać je ze sobą, korzystając z tej samej procedury dekodowania i tej samej funkcji straty.

Stanowi to ogromny krok naprzód w stosunku do tradycyjnych modeli VLM z wyjściem czysto tekstowym.

### Stabilizacja treningu: QK-Norm, dropout i warstwy LayerNorm

Trening modeli opartych na wczesnej fuzji (early fusion) w dużej skali bywa skrajnie niestabilny. Autorzy publikacji o Chameleon zastosowali trzy kluczowe techniki stabilizujące:

- QK-Norm. Zastosowanie warstwy LayerNorm do wektorów zapytań (Query) i kluczy (Key) w mechanizmie uwagi bezpośrednio przed obliczeniem iloczynu skalarnych. Zapobiega to niekontrolowanemu wzrostowi wartości logitów na głębszych warstwach sieci. Rozwiązanie to stało się standardem w wielu dużych modelach po 2024 roku.
- Rozmieszczenie dropoutu. Stosowanie dropoutu po każdym dodaniu połączenia rezydualnego, a nie tylko w warstwach uwagi i MLP. Zapewnia to lepszą regularyzację w sytuacjach, gdy gradienty z tokenów wizualnych mogłyby zdominować sieć.
- Uporządkowanie LayerNorm. Oprócz standardowego Pre-LN na gałęzi rezydualnej, wdrożono dodatkową warstwę LN na połączeniu pomijanym (skip connection) ostatniego bloku, co stabilizuje przepływ gradientów w końcowych warstwach.

Bez wdrożenia tych technik trening modelu Chameleon w wersji 34B charakteryzował się częstym brakiem zbieżności i anomaliami gradientów.

### Ograniczenia jakościowe rekonstrukcji tokenizera

VQ-VAE jest kodowaniem stratnym. Przy książce kodowej o rozmiarze 8192 i 1024 tokenach dla obrazu o rozdzielczości 512x512, jakość rekonstrukcji wskaźnika PSNR zatrzymuje się w okolicach 26-28 dB. Pozwala to na wygenerowanie czytelnego obrazu, ale ustępuje pod kątem wierności szczegółów modelom dyfuzyjnym w przestrzeni ciągłej (np. Stable Diffusion 3 osiąga wyniki powyżej 32 dB).

Dlatego to tokenizer jest głównym wąskim gardłem tego podejścia. Wdrożenie nowocześniejszych tokenizerów (np. MAGVIT-v2, IBQ, SBER-MoVQGAN) pozwala podnieść tę poprzeczkę. Model Emu3 (Lekcja 12.12) osiąga jakość generowania porównywalną z SDXL głównie dzięki ulepszonej konstrukcji tokenizera.

### Porównanie: Chameleon vs BLIP-2 / LLaVA

Chameleon (Wczesna fuzja, wspólny słownik):
- Jedna spójna funkcja straty, jeden wspólny dekoder.
- Możliwość generowania przeplatanych treści (tekst + obrazy).
- Jakość generowania ograniczona przez możliwości rekonstrukcji tokenizera.
- Wysoki koszt wdrożenia (wymaga uruchomienia dekodera VQ-VAE dla wygenerowanego obrazu przy wnioskowaniu).

BLIP-2 / LLaVA (Późna fuzja, osobne gałęzie):
- Wejście multimodalne, wyjście wyłącznie tekstowe.
- Możliwość ponownego wykorzystania gotowych wag wcześniej wytrenowanych modeli LLM.
- Brak ograniczeń jakościowych związanych z tokenizerem przy analizie obrazów.
- Niskie koszty wnioskowania (pojedyncze przejście forward).

Dobierz strategię bezpośrednio pod typ zadania. Jeśli kluczowe jest generowanie obrazów, wybierz architekturę typu Chameleon. Jeśli model ma służyć wyłącznie do rozumienia i analizy obrazów, tradycyjne podejście z adapterem i MLP będzie prostsze i tańsze w treningu.

### Fuyu oraz AnyGPT

Model Fuyu (Adept, 2023) to pokrewna koncepcja: całkowicie rezygnuje z osobnego encodera wizyjnego, rzutując surowe patche obrazu do przestrzeni wejściowej LLM tak, jakby były tokenami tekstowymi (bez użycia tokenizera). Jest to rozwiązanie prostsze, ale nie pozwala na generowanie obrazów na wyjściu.

Z kolei AnyGPT (Zhan et al., 2024) rozszerza pomysł Chameleon na cztery modalności: tekst, obrazy, mowę oraz muzykę, wykorzystując odpowiednie tokenizery VQ-VAE podpięte do jednego wspólnego transformatora (szczegółowo omawia to Lekcja 12.16).

## Użycie praktyczne

Skrypt `code/main.py` buduje uproszczoną implementację modelu opartego na wczesnej fuzji:

- Prosty kwantyzator VQ-VAE mapujący bloki 8x8 na indeksy z książki kodowej (K=16).
- Wspólny słownik zawierający ID tekstu (0..31), ID obrazów (32..47) oraz separatory modalności (48, 49).
- Model autoregresyjny (oparty na bigramach) wytrenowany na syntetycznych sekwencjach tekstu i tokenów obrazu.
- Pętlę próbkowania generującą naprzemiennie tekst i obrazy na podstawie promptu.

Kod celowo wykorzystuje prosty model bigramowy w celu przejrzystego zilustrowania przepływu sygnału od wejścia do wyjścia.

## Zadanie zaliczeniowe

W ramach tej lekcji należy stworzyć dokument `outputs/skill-tokenizer-vs-adapter-picker_pro.md`. Na podstawie specyfikacji produktu (wymaganie generowania obrazów vs samo rozumienie, pożądana jakość wizualna, budżet obliczeniowy), dobierz optymalne podejście pomiędzy wczesną fuzją (rodzina Chameleon) a późną fuzją (rodzina LLaVA), uzasadniając wybór wyliczeniami kosztów i jakości.

## Ćwiczenia

1. Chameleon wykorzystuje książkę kodową o rozmiarze K=8192 i 1024 tokeny na obraz 512x512. Oszacuj stopień kompresji w stosunku do surowego 24-bitowego obrazu RGB. Jaka jest skala utraty informacji?

2. Ile tokenów wygeneruje obraz w rozdzielczości 4K (3840x2160) przy zachowaniu tej samej gęstości tokenizatora VQ-VAE? Czy model w stylu Chameleon jest w stanie wygenerować obraz 4K w jednym przebiegu wnioskowania? Co ulegnie przepełnieniu lub awarii w pierwszej kolejności — kontekst modelu, stabilność tokenizera czy rozmiar pamięci podręcznej KV Cache?

3. Zaimplementuj mechanizm QK-Norm w czystym Pythonie. Dla wektorów zapytań i kluczy o wymiarze 64, porównaj ich iloczyn skalarny przed i po zastosowaniu LayerNorm. Wyjaśnij, dlaczego kontrola skali wartości logitów jest kluczowa w głębokich sieciach.

4. Przeczytaj sekcję 2.3 w publikacji o modelu Chameleon dotyczącą stabilności treningu. Opisz zdiagnozowany przez autorów błąd stabilności dla wariantu 34B przy braku normy QK. Jakie były symptomy anomalii gradientowych?

5. Rozbuduj uproszczony dekoder z kodu demonstracyjnego tak, aby po otrzymaniu promptu tekstowego generował odpowiedź o mieszanej modalności. Zmierz częstotliwość wybierania przez model generowania obrazu na pierwszym miejscu przy rozkładzie danych treningowych równym: 60% tekst jako pierwszy, 40% obraz jako pierwszy.

## Słownik pojęć

| Termin | Potoczne określenie | Co to dokładnie oznacza |
|------|-----------------|--------------------------------------|
| Wczesna fuzja (Early fusion) | „Zunifikowane tokeny” | Przetwarzanie obrazu i tekstu jako spójnego strumienia tokenów ze wspólnego słownika od samego wejścia modelu. |
| VQ-VAE | „Tokenizator obrazu” | Model autokodera mapujący ciągłe cechy obrazu na dyskretne indeksy (liczby całkowite) z książki kodowej. |
| Wspólny słownik | „Shared vocab” | Zunifikowana przestrzeń identyfikatorów tokenów obejmująca tekst, dyskretne indeksy obrazu oraz tagi specjalne. |
| QK-Norm | „Normalizacja uwagi” | Aplikowanie warstwy LayerNorm do zapytań (Q) i kluczy (K) przed obliczeniem ich iloczynu skalarnego w celu stabilizacji treningu. |
| Generowanie mieszane | „Mixed-modal generation” | Zdolność modelu do generowania w jednym przebiegu sekwencji zawierających naprzemiennie fragmenty tekstu oraz obrazy. |
| Rozmiar książki kodowej | „Codebook size K” | Liczba unikalnych wektorów w słowniku VQ-VAE; określa kompromis pomiędzy stopniem kompresji a wiernością rekonstrukcji. |
| Granica tokenizatora | „Tokenizer limit (PSNR)” | Maksymalna jakość rekonstrukcji obrazu możliwa do uzyskania przez dekoder VQ-VAE, stanowiąca barierę dla ostatecznej jakości modelu. |

## Dalsze czytanie

- [Chameleon Team — Chameleon: Mixed-Modal Early-Fusion Foundation Models (arXiv:2405.09818)](https://arxiv.org/abs/2405.09818)
- [Aghajanyan et al. — CM3 (arXiv:2201.07520)](https://arxiv.org/abs/2201.07520)
- [Yu et al. — CM3Leon (arXiv:2309.02591)](https://arxiv.org/abs/2309.02591)
- [Zhan et al. — AnyGPT (arXiv:2402.12226)](https://arxiv.org/abs/2402.12226)
- [Adept — Fuyu-8B Blog (adept.ai)](https://www.adept.ai/blog/fuyu-8b)
