Created At: 2026-06-08T16:05:45Z
Completed At: 2026-06-08T16:05:45Z
File Path: `file:///C:/poligon/LLM_Traning/phases/08-generative-ai/19-visual-autoregressive-var/docs/pl.md`

# Wizualne modelowanie autoregresyjne (VAR): prognozowanie kolejnej skali

> Modele dyfuzyjne próbkuje się iteracyjnie w czasie (etapy odszumiania). VAR próbuje iteracyjnie w skali — prognozuje token 1x1, następnie 2x2, następnie 4x4, aż do osiągnięcia ostatecznej rozdzielczości, przy czym każda kolejna skala jest warunkowana poprzednimi. W publikacji z 2024 r. wykazano, że model VAR podlega prawom skalowania w stylu GPT przy generowaniu obrazu i przewyższa DiT przy takim samym budżecie obliczeniowym. Ta lekcja przedstawia budowę tego podstawowego mechanizmu.

**Typ:** Implementacja
**Języki:** Python (z wykorzystaniem PyTorch)
**Wymagania wstępne:** Faza 7, lekcja 03 (Uwaga wielogłowa), Faza 8, lekcja 06 (DDPM)
**Czas:** ~90 minut

## Problem

W modelowaniu języka naturalnego dominuje generowanie autoregresyjne (AR), ponieważ skaluje się ono w przewidywalny sposób: większa moc obliczeniowa i więcej parametrów prowadzą do niższej perpleksji i lepszych wyników. W dziedzinie generowania obrazu przed rokiem 2024 istniały dwa główne podejścia oparte na AR: PixelRNN/PixelCNN (piksel po pikselu) oraz DALL-E 1 / Parti / MuseGAN (token po tokenie w kodach VQ-VAE).

Oba te podejścia cierpiały z powodu problemu kolejności generowania (generation order). Piksele i tokeny są ułożone w siatkę 2D, ale model AR musi przetwarzać je w kolejności rastrowej 1D. Początkowy piksel w narożniku nie niesie żadnej informacji o tym, czym ostatecznie stanie się obraz. Jakość generowanych obrazów skalowała się gorzej niż w przypadku GPT dla tekstu i nigdy nie osiągnęła jakości modeli dyfuzyjnych przy porównywalnym budżecie obliczeniowym.

VAR rozwiązuje problem kolejności generowania, zmieniając sam obiekt prognozowania. Zamiast przewidywać tokeny obrazu po kolei w przestrzeni, VAR generuje cały obraz w coraz większych rozdzielczościach. Krok 1: przewiduje token 1x1 (ogólne „podsumowanie” obrazu). Krok 2: przewiduje siatkę tokenów 2x2 (zgrubne cechy). Krok 3: przewiduje siatkę 4x4. Krok K: przewiduje ostateczną siatkę (H/8)x(W/8).

Każda skala uwzględnia w atencji wszystkie poprzednie skale (przyczynowo w ramach „porządku skal”) i jest przetwarzana równolegle w obrębie własnej skali. Problem kolejności znika: cała siatka w skali k powstaje w jednym przejściu w przód (forward pass) transformera.

## Koncepcja

### Wieloskalowy tokenizator VQ-VAE

VAR wymaga **dyskretnego tokenizera wieloskalowego**. Dla obrazu x tworzy on sekwencję siatek tokenów o rosnącej rozdzielczości:

```
x -> encoder -> latent f
f -> tokenize at 1x1: token grid z_1 of shape (1, 1)
f -> tokenize at 2x2: token grid z_2 of shape (2, 2)
...
f -> tokenize at (H/p)x(W/p): token grid z_K of shape (H/p, W/p)
```

Każdy $z_k$ korzysta z tej samej książki kodowej (codebook) — typowy rozmiar to 4096–16384. Tokenizacja w poszczególnych skalach nie jest niezależna — proces treningu wymusza, by suma reprezentacji z poszczególnych skal rekonstruowała mapę cech $f$:

```
f ≈ upsample(embed(z_1), target_size) + ... + upsample(embed(z_K), target_size)
```

Jest to wariant **residualnej kwantyzacji wektorowej (Residual VQ)**. Skala k koduje informacje pominięte przez skale 1..k-1. Dekoder przyjmuje sumę wektorów osadzeń ze wszystkich skal i na tej podstawie rekonstruuje obraz.

Wieloskalowy tokenizator VQ trenuje się raz (podobnie jak VQGAN), a następnie zamraża. Cały proces generatywny realizowany jest przez model autoregresyjny nałożony na te kody.

### Prognozowanie kolejnej skali (Next-Scale Prediction)

Model generatywny to transformer, który analizuje tokeny ze wszystkich poprzednich skal i prognozuje tokeny dla kolejnej skali.

Struktura sekwencji wejściowej:

```
[START, z_1 tokens, z_2 tokens, z_3 tokens, ..., z_K tokens]
```

Kodowanie pozycyjne reprezentuje zarówno indeks skali, jak i pozycję przestrzenną w ramach tej skali. Atencja działa przyczynowo w odniesieniu do kolejności skal: token w skali k na pozycji (i, j) może uwzględniać wszystkie tokeny ze skal 1..k-1 oraz tokeny z tej samej skali k, które pojawiły się wcześniej. W obrębie samej skali k nie stosuje się jednak atencji przyczynowej — VAR wykorzystuje stałe kodowanie pozycyjne bez przyczynowości wewnątrzskalowej, co pozwala na równoległe prognozowanie wszystkich pozycji w danej skali.

Funkcja straty: dla każdej skali k prognozuje się tokeny $z_k$ na podstawie tokenów ze wszystkich poprzednich skal. Stosowana jest strata entropii krzyżowej (cross-entropy loss) dla dyskretnych kodów VQ. Struktura jest analogiczna do GPT, z tą różnicą, że „sekwencja” ma strukturę opartą na skalach.

### Generowanie (inferencja)

Podczas inferencji:

```
generate z_1 = sample from p(z_1)                    # 1 token
generate z_2 = sample from p(z_2 | z_1)              # 4 tokens in parallel
generate z_3 = sample from p(z_3 | z_1, z_2)         # 16 tokens in parallel
...
decode: f = sum of embed-and-upsample scales 1..K
image = VAE_decoder(f)
```

Dla liczby skal K = 10 generowanie wymaga jedynie 10 kroków w przód (forward passes) transformera. Każdy krok generuje równolegle całą skalę — bez autoregresji na poziomie pojedynczych tokenów w danej skali. W przypadku obrazu o wymiarach 256x256 daje to około 10 przejść w porównaniu z 28–50 krokami w modelach DiT.

### Dlaczego prognozowanie kolejnej skali przewyższa prognozowanie kolejnego tokena

Trzy kluczowe zalety strukturalne:
1. **Zgodność ze statystyką naturalnych obrazów (od zgrubnego do szczegółu).** Zarówno ludzka percepcja wzrokowa, jak i rozkłady danych obrazowych wykazują prawidłowości zależne od skali: struktury o niskiej częstotliwości są stabilne i przewidywalne, natomiast szczegóły o wysokiej częstotliwości zależą od kontekstu niskoczęstotliwościowego. Prognozowanie kolejnej skali naturalnie to wykorzystuje.
2. **Generowanie równoległe w ramach skali.** W przeciwieństwie do autoregresji na poziomie pojedynczych tokenów (jak w GPT), VAR generuje wszystkie tokeny danej skali w jednym kroku. Efektywna liczba kroków generowania skaluje się logarytmicznie, a nie liniowo.
3. **Eliminacja błędu kolejności generowania.** Tokeny w skali k mają wgląd we wszystkie tokeny ze skali k-1; eliminuje to asymetrię typu „na lewo od” lub „powyżej”, która w klasycznym AR zmusza model do przedwczesnego decydowania o wartości początkowych tokenów przed poznaniem szerszego kontekstu.

### Prawa skalowania

Tian i in. wykazali, że model VAR podlega prawu skalowania (power law) dla metryki FID na zbiorze ImageNet — analogicznie do zachowania GPT pod kątem perpleksji. Podwojenie liczby parametrów lub nakładu obliczeniowego przewidywalnie poprawia wyniki. Był to pierwszy model generatywny dla obrazów, który wykazał tak wyraźne prawa skalowania, zbliżone do modeli językowych. Dzięki temu wydajność VAR można precyzyjnie szacować na podstawie dostępnego budżetu obliczeniowego, zamiast polegać na empirycznym zgadywaniu parametrów architektury.

### Związek z modelami dyfuzyjnymi

Zarówno VAR, jak i dyfuzja opierają się na podobnym paradygmacie: rozbijają problem generowania na sekwencję łatwiejszych podproblemów.

- Dyfuzja: stopniowo dodaje szum i uczy się go usuwać krok po kroku.
- VAR: stopniowo zwiększa rozdzielczość i uczy się prognozować kolejną skalę.

Różnią się one jednak osią podziału problemu. Obie metody modelują ciągi rozkładów warunkowych. Empirycznie VAR charakteryzuje się szybszą inferencją (mniej kroków, pełna równoległość w ramach skali) i dorównuje lub przewyższa modele DiT na zbiorze ImageNet przy generowaniu warunkowanym klasą. Aktywnym kierunkiem badań jest warunkowanie tekstem w modelach VAR (np. VARclip, HART).

## Wdrożenie praktyczne

W pliku `code/main.py` Twoim zadaniem będzie:
1. Zbudowanie niewielkiego **wieloskalowego tokenizera VQ** dla syntetycznych danych obrazowych (dwuwymiarowe pierścienie Gaussa).
2. Wytrenowanie **transformera w stylu VAR** do prognozowania tokenów kolejnej skali.
3. Wygenerowanie próbki poprzez czterokrotne uruchomienie transformera (4 skale) i zdekodowanie wyniku.
4. Zweryfikowanie, czy trening uporządkowany według skal pozwala na równoległe generowanie w ramach pojedynczej skali.

Jest to uproszczona implementacja typu toy model. Jej celem jest pokazanie w praktyce działania maski atencji opartej na skalach oraz równoległego generowania.

## Efekty lekcji

Efektem tej lekcji jest plik `outputs/skill-var-tokenizer-designer.md` zawierający opis umiejętności projektowania wieloskalowego tokenizera (liczba skal, czynniki skalowania, rozmiar książki kodowej, współdzielenie reszt, architektura dekodera).

## Ćwiczenia

1. **Analiza ablacyjna liczby skal (Scale Ablation).** Wytrenuj model VAR z 4, 6, 8 i 10 skalami. Zmierz jakość rekonstrukcji jako funkcję liczby autoregresyjnych kroków. Więcej skal = mniejsze wartości resztowe = wyższa jakość, ale kosztem większej liczby kroków.

2. **Rozmiar książki kodowej.** Wytrenuj tokenizery o rozmiarach książki kodowej 512, 4096 oraz 16384. Większe książki kodowe zapewniają lepszą rekonstrukcję, lecz utrudniają prognozowanie kolejnych tokenów. Znajdź punkt przegięcia (elbow/knee point).

3. **Weryfikacja równoległości w ramach skali.** Dla wytrenowanego modelu VAR przeanalizuj rozkład atencji. Czy na poziomie skali k model uwzględnia tylko zależności między różnymi skalami, pomijając powiązania wewnątrzskalowe? Zweryfikuj implementację maski.

4. **Porównanie skalowania: VAR vs DiT.** Dla tego samego zadania generowania warunkowanego klasą na zbiorze ImageNet wytrenuj modele VAR i DiT przy porównywalnych budżetach parametrów (np. 33M, 130M, 458M). Wykreśl zależność FID od nakładu obliczeniowego (compute). Model VAR powinien osiągać lepsze wyniki niż DiT dla każdego rozmiaru – odtwarzając wyniki z publikacji naukowej w mniejszej skali.

5. **Warunkowanie tekstem.** Rozbuduj model VAR o obsługę osadzeń tekstowych (np. z modeli CLIP) jako dodatkowego warunku przekazywanego przez adaLN (Adaptive Layer Normalization). Jest to podejście stosowane w HART. Zbadaj, jak bardzo poprawia się metryka FID przy próbkowaniu zgodnym z tekstem.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|----------------------|
| VAR | „Wizualna autoregresja” | Generowanie obrazu poprzez prognozowanie kolejnej skali na podstawie piramidy siatek tokenów VQ |
| Prognozowanie kolejnej skali | „Przewidywanie od zgrubnego do szczegółu” | Model prognozuje tokeny w rosnących skalach rozdzielczości, uwzględniając wszystkie poprzednie skale |
| Wieloskalowy tokenizator VQ | „Wieloskalowe VQ / RVQ” | VQ-VAE tworzący K siatek tokenów o rosnącej rozdzielczości, z dekoderem sumującym reprezentacje ze wszystkich skal |
| Skala k | „Poziom k piramidy” | Jeden z K poziomów rozdzielczości, od 1x1 przy k=1 do (H/p)x(W/p) przy k=K |
| Równoległość w ramach skali | „Jedno przejście w przód na skalę” | Wszystkie tokeny w skali k są prognozowane w jednym przebiegu transformera, a nie autoregresywnie |
| Atencja przyczynowa między skalami | „Uporządkowanie uwagi według skal” | Token w skali k może uwzględniać w atencji wszystkie skale 1..k, ale nie skale k+1..K |
| Resztkowe VQ | „Kwantyzacja addytywna” | Tokeny każdej skali kodują resztę pozostałą po niższych skalach; dekoder sumuje wszystkie wektory osadzeń (embeddings) |
| Prawa skalowania VAR | „Skalowanie obrazu a'la GPT” | FID podlega przewidywalnemu prawu potęgowemu wraz ze wzrostem mocy obliczeniowej, podobnie jak perpleksja w modelach językowych |
| HART | „Hybrydowy VAR + tekst” | Warunkowany tekstem wariant VAR łączący iteracyjne dekodowanie w stylu MaskGIT ze strukturą skali VAR |
| Kodowanie pozycji i skali | „Trójka (skala, wiersz, kolumna)” | Kodowanie pozycyjne przekazujące zarówno indeks skali, jak i współrzędne przestrzenne w ramach tej skali |

## Dalsze czytanie

- [Tian et al., 2024 — „Visual Autoregressive Modeling: Scalable Image Generation via Next-Scale Prediction”](https://arxiv.org/abs/2404.02905) — oryginalna publikacja naukowa o VAR, podstawowe źródło wiedzy.
- [Peebles and Xie, 2022 — „Scalable Diffusion Models with Transformers”](https://arxiv.org/abs/2212.09748) — publikacja o DiT, kluczowy punkt odniesienia dla porównań modeli dyfuzyjnych.
- [Esser et al., 2021 — „Taming Transformers for High-Resolution Image Synthesis”](https://arxiv.org/abs/2012.09841) — praca o VQGAN, stanowiąca podstawę architektury tokenizatorów wieloskalowych w VAR.
- [van den Oord et al., 2017 — „Neural Discrete Representation Learning”](https://arxiv.org/abs/1711.00937) — publikacja wprowadzająca VQ-VAE, fundament dyskretnej tokenizacji obrazu.
- [Tang et al., 2024 — „HART: Efficient Visual Generation with Hybrid Autoregressive Transformer”](https://arxiv.org/abs/2410.10812) — rozwinięcie VAR o warunkowanie tekstem.
