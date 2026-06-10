# Zunifikowane modele Show-o i Discrete Diffusion

> Projekt Transfusion łączy ze sobą reprezentacje ciągłe i dyskretne. Z kolei autorzy modelu Show-o (Xie et al., sierpień 2024) poszli w innym kierunku: tokeny tekstowe wykorzystują przyczynowe przewidywanie następnego tokenu (Next-Token Prediction), natomiast tokeny obrazu są optymalizowane metodą maskowanej dyfuzji dyskretnej (masked discrete diffusion) w stylu MaskGIT. Obie te metody zaimplementowano w jednym transformatorze wykorzystującym hybrydową maskę uwagi (hybrid attention mask). Rozwiązanie to unifikuje zadania VQA, syntezę tekstu na obraz (T2I), inpainting (dopełnianie obrazu) oraz generowanie o mieszanej modalności w ramach jednego szkieletu modelu (jeden tokenizer na modalność, jedna funkcja straty oparta na przewidywaniu maskowanych tokenów). Ta lekcja szczegółowo omawia architekturę Show-o — wyjaśniając, dlaczego maskowana dyfuzja dyskretna umożliwia równoległe, kilkuetapowe generowanie obrazów — oraz porównuje ten kierunek z Transfusion i Emu3.

**Typ:** Teoria / Zrozumienie
**Języki:** Python (biblioteka standardowa, próbnik z maskowaną dyfuzją dyskretną)
**Wymagania:** Faza 12 · Lekcja 13 (Transfusion)
**Czas:** ~120 minut

## Cele nauczania

- Wyjaśnij mechanizm maskowanej dyfuzji dyskretnej: harmonogram maskowania tokenów, a następnie odzyskiwanie oryginalnych wartości przez transformator.
- Porównaj równoległe dekodowanie obrazu (Show-o, MaskGIT) z autoregresywnym dekodowaniem obrazu (Chameleon, Emu3) pod kątem szybkości działania i jakości syntezy.
- Omów trzy główne zadania realizowane przez pojedynczy checkpoint Show-o: T2I, VQA oraz inpainting obrazu.
- Dobierz odpowiedni harmonogram maskowania (cosinusowy, liniowy, obcięty) i opisz jego wpływ na jakość generowania.

## Problem

Trening z dwiema różnymi funkcjami strat w Transfusion jest skuteczny, ale wiąże się ze skomplikowaną dynamiką uczenia — ciągła strata dyfuzyjna operuje na innej skali wartości numerycznych niż dyskretna strata NTP. Prawidłowe zbalansowanie wag strat wymaga czasochłonnego strojenia hiperparametrów, co czyni tę architekturę trudną w implementacji.

Rozwiązanie Show-o: zachowaj dyskretną formę dla obu modalności (podobnie jak w Chameleon), ale generuj obrazy równolegle przy użyciu maskowanej dyfuzji dyskretnej zamiast sekwencyjnego próbkowania. Celem treningowym staje się przewidywanie maskowanych tokenów, które w naturalny sposób uogólnia zadanie modelowania języka (NTP).

## Koncepcja

### Maskowana dyfuzja dyskretna (MaskGIT)

Mechanizm wprowadzony w MaskGIT (Chang et al., 2022) jest bardzo elegancki. Proces rozpoczyna się od całkowicie zamaskowanego obrazu (gdzie każdy token ma przypisany specjalny identyfikator `<MASK>`). W każdym kroku model przewiduje równolegle wartości wszystkich zamaskowanych tokenów, po czym zachowuje najbardziej pewne predykcje (top-K), a pozostałe maskuje ponownie. Po około 8-16 iteracjach wszystkie tokeny obrazu zostają poprawnie wygenerowane. Harmonogram określający liczbę tokenów do odmaskowania w każdym kroku (zazwyczaj oparty na funkcji cosinus) ma kluczowe znaczenie dla stabilności.

Proces treningu jest bardzo prosty: losowany jest współczynnik zamaskowania (mask ratio) z przedziału [0, 1], aplikowany do tokenów VQ obrazu, a transformator uczy się odzyskiwać oryginalne wartości zamaskowanych elementów. To dokładnie ta sama metoda, którą model BERT stosował dla tekstu, przeskalowana do zadań generowania obrazów.

### Show-o: jeden transformator, maska hybrydowa

Show-o integruje metodę MaskGIT z transformerem przyczynowego modelu językowego (causal LLM). Maska uwagi (attention mask):

- Tokeny tekstowe: maskowanie przyczynowe (standardowe dla LLM).
- Tokeny obrazu: pełna uwaga dwukierunkowa w ramach jednego bloku obrazu (dzięki czemu zamaskowane tokeny mogą analizować wszystkie pozostałe tokeny obrazu w trakcie predykcji).
- Tekst a obraz: tekst przetwarza poprzedzające go obrazy, a obraz przetwarza poprzedzający go tekst.

Trening jest realizowany naprzemiennie na zadaniach:
1. Standardowe NTP na sekwencjach czystego tekstu.
2. Zadania T2I: tekst → obraz; model generuje tokeny obrazu na podstawie podanego tekstu z użyciem maskowania, a strata liczona jest na predykcji maskowanych tokenów.
3. Zadania VQA: obraz → tekst; model generuje tekst na podstawie obrazu (co sprowadza się do klasycznej straty NTP).

Zunifikowana funkcja straty to strata entropii krzyżowej na tokenach `<MASK>`, która obejmuje zarówno tekstowe zadanie NTP (gdzie tylko ostatni token jest „zamaskowany”), jak i dyfuzję zamaskowanego obrazu (gdzie maskowany jest losowy podzbiór tokenów).

### Próbkowanie równoległe (Parallel Sampling)

Model Show-o generuje kompletny obraz w około 16 krokach zamiast ~1000 kroków (wymaganych przy autoregresywnym próbkowaniu token po tokenie) lub ~20 kroków (przy ciągłej dyfuzji). W każdej iteracji model przewiduje równolegle wartości wszystkich zamaskowanych tokenów, zatwierdza top-K z nich i powtarza proces.

Porównanie:
- Chameleon / Emu3 (autoregresja token po tokenie): N_tokens przebiegów forward, zazwyczaj 1024-4096 na obraz.
- Transfusion (ciągła dyfuzja): ~20 kroków, każdy wymaga pełnego przejścia forward transformatora.
- Show-o (maskowana dyfuzja dyskretna): ~16 kroków, każdy wymaga pełnego przejścia forward transformatora.

Show-o działa znacznie szybciej niż Chameleon w modelach o podobnej skali, oferując liczbę kroków zbliżoną do Transfusion przy niższych kosztach obliczeniowych jednego kroku (dyskretna klasyfikacja na słowniku vs ciągła strata MSE).

### Różnorodne zadania w jednym checkpointcie

Show-o obsługuje cztery główne zadania przy wnioskowaniu, wybierane za pomocą formatu promptu:

- Generowanie tekstu: standardowe autoregresyjne generowanie tekstu.
- VQA: wejście obrazu, wyjście tekstu.
- Synteza T2I: wejście tekstu, wyjście obrazu za pomocą maskowanej dyfuzji dyskretnej.
- Inpainting (dopełnianie obrazu): wejście obrazu z zamaskowanymi obszarami, wyjście w postaci uzupełnionego obrazu.

Możliwość inpaintingu otrzymujemy automatycznie dzięki treningowi na maskowanych danych. Wystarczy zamaskować wybrany fragment siatki tokenów VQ obrazu, podać pozostałą część oraz opis tekstowy, a model odzyska brakujące tokeny.

### Harmonogram maskowania (Masking Schedule)

Sposób zmniejszania liczby zamaskowanych tokenów w kolejnych krokach decyduje o jakości obrazu. Show-o zaleca harmonogram cosinusowy:

```
mask_ratio(t) = cos(pi * t / (2 * T))   # dla kroków t = 0..T
```

W kroku 0 wszystkie tokeny są zamaskowane (współczynnik 1.0). W ostatnim kroku T żaden token nie jest zamaskowany. Funkcja cosinus skupia proces generowania na krokach pośrednich, gdzie predykcja dostarcza najwięcej informacji. Harmonogramy liniowe również są stosowane, ale wykazują tendencję do zbyt szybkiego zatwierdzania predykcji.

### Show-o2

Model Show-o2 (wersja z 2025 roku, arXiv 2506.15564) skaluje te założenia: wykorzystuje większy model językowy LLM, ulepszony tokenizer oraz zoptymalizowany harmonogram masek przy zachowaniu tej samej podstawowej architektury.

### Klasyfikacja modeli ujednoliconych w 2026 roku

- Tokeny dyskretne + NTP: Chameleon, Emu3. Metoda prosta w implementacji, ale charakteryzująca się powolnym wnioskowaniem.
- Dyskretne tokeny + maskowana dyfuzja: Show-o, MaskGIT, LlamaGen, Muse. Pozwala na próbkowanie równoległe, ale jakość jest wciąż ograniczona przez kompresję tokenizera.
- Ciągłe reprezentacje + dyfuzja: Transfusion, MMDiT, DiT. Oferuje najwyższą jakość obrazu, ale wymaga skomplikowanego treningu z dwiema stratami.
- Ciągłe reprezentacje + flow matching w modelach VLM: JanusFlow, InternVL-U. Najnowszy kierunek badawczy.

Wybierz Show-o, jeśli potrzebujesz wdrożyć zadania T2I, inpaintingu oraz VQA w jednym modelu open-weight o wysokiej wydajności. Wybierz Transfusion, jeśli kluczowa jest najwyższa jakość obrazu i posiadasz zasoby na wdrożenie treningu z dwiema funkcjami strat.

## Użycie praktyczne

Skrypt `code/main.py` symuluje proces próbkowania w Show-o:

- Generuje testową siatkę 16 tokenów VQ.
- Zawiera model testowy przewidujący logity na podstawie promptu i aktualnie odmaskowanych tokenów.
- Realizuje równoległe próbkowanie maskowane w 8 krokach przy użyciu harmonogramu cosinusowego.
- Wizualizuje stany pośrednie (zmniejszanie obszaru maskowania) oraz generowane tokeny końcowe.

Uruchomienie skryptu pozwala zaobserwować proces stopniowego znoszenia maski z obrazu.

## Zadanie zaliczeniowe

W ramach tej lekcji należy stworzyć dokument `outputs/skill-unified-gen-model-picker_pro.md`. Na podstawie specyfikacji systemu produkcyjnego wymagającego zadań rozumienia (VQA, opisywanie obrazów) oraz syntezy (T2I, inpainting) przy użyciu modeli open-weight, dobierz optymalne rozwiązanie spośród: rodziny Show-o, rodziny Transfusion/MMDiT lub modeli Emu3/Chameleon, szczegółowo analizując ich kompromisy wdrożeniowe.

## Ćwiczenia

1. Próbkowanie w maskowanej dyfuzji dyskretnej wymaga około 16 kroków. Wyjaśnij, dlaczego nie można wygenerować obrazu w 1 kroku i co ulegnie uszkodzeniu, jeśli odmaskujemy wszystkie tokeny jednocześnie w kroku 0.

2. Zadanie inpaintingu (dopełniania obrazu) jest realizowane bez dodatkowego treningu. Zaproponuj komercyjne zastosowanie (przypadek użycia), w którym model Show-o przewyższa wyspecjalizowane modele dedykowane.

3. Porównaj harmonogram cosinusowy z harmonogramem liniowym: wylicz liczbę odmaskowywanych tokenów w każdym kroku dla T=8. Wyjaśnij, który z nich zapewnia stabilniejszy przebieg procesu generowania.

4. Obraz w Show-o o rozmiarze 512x512 składa się z 1024 tokenów. Przy słowniku K=16384 model generuje 1024 * log2(16384) = 14336 bitów (~1,75 KiB) danych. Dla porównania, wyjście obrazu o rozdzielczości 512x512 w surowych pikselach (24 bity) to 6 291 456 bitów (~768 KiB). Oblicz stopień kompresji i określ, na jakie kompromisy jakościowe się decydujemy.

5. Przeczytaj publikację o modelu LlamaGen (arXiv:2406.06525). Wyjaśnij, czym różni się warunkowany klasowo autoregresywny model obrazu LlamaGen od podejścia opartego na maskowaniu w Show-o.

## Słownik pojęć

| Termin | Potoczne określenie | Co to dokładnie oznacza |
|------|-----------------|--------------------------------------|
| Maskowana dyfuzja dyskretna | „Styl MaskGIT” | Metoda treningu na odzyskiwaniu maskowanych tokenów; przy wnioskowaniu model stopniowo demaskuje najbardziej pewne predykcje. |
| Harmonogram cosinusowy | „Cosinus demaskowania” | Funkcja określająca spadek współczynnika zamaskowania w kolejnych krokach wnioskowania w celu stabilizacji jakości. |
| Próbkowanie równoległe | „Parallel decoding” | Równoległe przewidywanie wartości wszystkich zamaskowanych tokenów w jednym kroku forward transformatora. |
| Uwaga hybrydowa | „Hybrid attention” | Maska uwagi przyczynowa dla tokenów tekstowych, a dwukierunkowa dla tokenów składających się na obraz. |
| Inpainting | „Dopełnianie obrazu” | Zadanie polegające na uzupełnianiu brakujących, zamaskowanych fragmentów obrazu na podstawie kontekstu i promptu tekstowego. |
| Liczba zatwierdzanych tokenów | „Top-K na krok” | Parametr określający, ile przewidzianych tokenów o najwyższej pewności zostaje trwale odmaskowanych w danym kroku. |

## Dalsze czytanie

- [Xie et al. — Show-o: One Single Transformer to Unify Temporal, Spatial, and Multimodal Understanding (arXiv:2408.12528)](https://arxiv.org/abs/2408.12528)
- [Show-o2 (arXiv:2506.15564)](https://arxiv.org/abs/2506.15564)
- [Chang et al. — MaskGIT: Masked Generative Image Transformer (arXiv:2202.04200)](https://arxiv.org/abs/2202.04200)
- [Sun et al. — Autoregressive Image Generation without Vector Quantization (LlamaGen, arXiv:2406.06525)](https://arxiv.org/abs/2406.06525)
- [Chang et al. — Muse: Text-To-Image Generation via Masked Generative Transformers (arXiv:2301.00704)](https://arxiv.org/abs/2301.00704)
