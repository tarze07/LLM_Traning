# Transfusion: Tekst autoregresyjny + obraz dyfuzyjny w jednym transformatorze

> Modele Chameleon i Emu3 opierają się całkowicie na dyskretnych tokenach. Rozwiązanie to działa, ale wprowadza wąskie gardło kwantyzacji (quantization bottleneck) — jakość generowanych obrazów osiąga punkt nasycenia (plateau) wyraźnie poniżej poziomu modeli dyfuzyjnych w przestrzeni ciągłej. Twórcy architektury Transfusion (Meta; Zhou et al., sierpień 2024) przyjęli odwrotne założenie: zachowali ciągłą reprezentację obrazów, zrezygnowali całkowicie z tokenizera VQ-VAE i wytrenowali jeden transformator za pomocą dwóch różnych funkcji strat. Tokeny tekstowe są optymalizowane klasycznym zadaniem przewidywania następnego tokenu (Next-Token Prediction). Z kolei patche obrazu są optymalizowane funkcją straty dopasowania przepływu (flow matching) / dyfuzji. Oba zadania optymalizują dokładnie te same wagi modelu. Struktura leżąca u podstaw modelu Stable Diffusion 3 (MMDiT) jest bliskim krewnym tego rozwiązania. W tej lekcji przeanalizujemy założenia Transfusion, zbudujemy uproszczony kod treningowy z dwiema funkcjami strat (dual-loss trainer) oraz zdefiniujemy maskę uwagi, która pozwala jednemu transformatorowi na realizację obu zadań jednocześnie.

**Typ:** Projekt / Implementacja
**Języki:** Python (biblioteka standardowa, kod treningowy z dwiema funkcjami strat dla uproszczonego zbioru w skali MNIST)
**Wymagania wstępne:** Faza 12 · Lekcja 11 (Chameleon), Faza 8 (Generatywna AI)
**Czas:** ~180 minut

## Cele nauczania

- Zaimplementuj transformator obsługujący dwie funkcje strat (NTP na tokenach tekstowych oraz dyfuzyjną stratę MSE na ciągłych patchach obrazu) w ramach jednych wag modelu.
- Wyjaśnij, dlaczego połączenie uwagi dwukierunkowej na patchach obrazu oraz uwagi przyczynowej (causal attention) na tokenach tekstowych to optymalny dobór maski uwagi.
- Porównaj architekturę Transfusion (obrazy ciągłe, strata dyfuzyjna) z podejściem typu Chameleon (obrazy dyskretne, NTP) pod kątem wymagań obliczeniowych, jakości syntezy oraz stopnia skomplikowania kodu.
- Omów innowacje wprowadzone w MMDiT: wagi specyficzne dla danej modalności w każdym bloku sieci oraz mechanizm współdzielonej uwagi (shared attention) na strumieniu rezydualnym.

## Problem

Debata na temat wyższości dyskretnej lub ciągłej reprezentacji obrazów trwa od dawna. Reprezentacje ciągłe (surowe piksele, ukryte stany latentne VAE) doskonale zachowują szczegóły obrazu. Z kolei dyskretne tokeny (indeksy z książki kodowej VQ) ułatwiają integrację z tekstowym słownikiem transformatora, ale niszczą detale na etapie kwantyzacji.

W modelach Chameleon i Emu3 wybrano podejście dyskretne: jedna funkcja straty, jedna architektura, ale wierność obrazu ograniczona przez możliwości rekonstrukcji tokenizera.

Tradycyjne modele dyfuzyjne stosowały reprezentację ciągłą: zapewniały świetną jakość obrazu, ale wymagały struktur całkowicie odrębnych od modelu LLM, skomplikowanej konfiguracji harmonogramu szumu (noise scheduler) i nie oferowały bezpośredniej integracji z procesem generowania tekstu.

Twórcy Transfusion postawili pytanie: czy możemy połączyć zalety obu tych światów? Czyli zachować ciągłą reprezentację obrazów, trenować jeden spójny model i stosować dwie funkcje strat połączone w jednym kroku aktualizacji wag.

## Koncepcja

### Architektura z dwiema funkcjami strat (Dual-Loss)

Pojedynczy transformator typu decoder-only przetwarza sekwencję zawierającą:

- Tokeny tekstowe (dyskretne, ze słownika BPE).
- Patche obrazu (ciągłe bloki o rozmiarze np. 16x16 pikseli rzutowane do wymiaru ukrytego za pomocą warstwy liniowej — analogicznie jak na wejściu encodera ViT).
- Tagi specjalne `<image>` oraz `</image>` wyznaczające granice ciągu ciągłych patchy.

Przebieg forward jest wykonywany wspólnie. Funkcja straty wybiera jedną z dwóch głowic wyjściowych (heads) dla każdego tokena:

- Dla tokenów tekstowych: standardowa strata entropii krzyżowej na logitach słownika.
- Dla patchy obrazu: strata dyfuzyjna w przestrzeni ciągłej — przewidywanie szumu dodanego do każdego patcha.

Gradienty przepływają przez wspólny transformator, dzięki czemu obie funkcje strat jednocześnie modyfikują wspólne wagi modelu.

### Maska uwagi: przyczynowy tekst + dwukierunkowy obraz

Tokeny tekstowe muszą być maskowane przyczynowo (causal masking) — token tekstowy nie może przetwarzać informacji z przyszłości. Z kolei patche składające się na jeden obraz reprezentują spójną scenę i powinny przetwarzać informacje dwukierunkowo w ramach tego samego bloku obrazu.

Zaimplementowana maska uwagi (attention mask):

```
M[i, j] = 1, gdy zachodzi przynajmniej jeden warunek:
  (i to tekst oraz j to tekst oraz j <= i)   # maskowanie przyczynowe dla tekstu
  LUB (i to obraz oraz j to obraz oraz ten_sam_blok_obrazu(i, j))   # maskowanie dwukierunkowe w ramach jednego obrazu
  LUB (i to tekst oraz j to obraz oraz j < indeks_konca_obrazu)   # tekst przetwarza poprzedzające go obrazy
  LUB (i to obraz oraz j to tekst oraz j < indeks_startu_obrazu)   # obraz przetwarza poprzedzający go tekst
```

Jest ona stosowana jako maska blokowo-trójkątna (block-triangular mask) podczas treningu oraz wnioskowania.

### Strata dyfuzyjna wewnątrz transformatora

Standardowa strata dyfuzyjna polega na dodaniu szumu do patcha obrazu i postawieniu przed modelem zadania jego przewidzenia (lub zrekonstruowania oryginalnego patcha). Transfusion wykorzystuje specyficzny wariant — dopasowanie przepływu (flow matching), w którym model przewiduje wektor prędkości (velocity field) przejścia od szumu do czystych danych.

W trakcie treningu:
1. Dla każdego czystego patcha obrazu x0 wylosuj krok czasowy t.
2. Pobierz próbkę szumu ε, oblicz stan zaszumiony: xt = (1-t) * x0 + t * ε (interpolacja liniowa dla flow matching).
3. Transformator przewiduje wektor prędkości v_theta(xt, t); strata = MSE(v_theta(xt, t), ε - x0).
4. Zsumuj tę stratę ze stratą NTP dla tekstu pochodzącą z tej samej sekwencji wejściowej.

Podczas wnioskowania generowanie wygląda następująco:
- Tokeny tekstowe: standardowe próbkowanie autoregresywne.
- Patche obrazu: pętla próbkowania dyfuzyjnego (zazwyczaj 10-30 kroków) warunkowana wygenerowanym wcześniej tekstem.

### MMDiT: wariant ze Stable Diffusion 3

W tym samym okresie co Transfusion, w modelu Stable Diffusion 3 (Esser et al., marzec 2024) zaimplementowano strukturę MMDiT (Multimodal Diffusion Transformer). Obie architektury są koncepcyjnie bardzo bliskie.

Kluczowe wyróżniki MMDiT:
- Wagi specyficzne dla danej modalności na blok. Każdy blok transformatora posiada niezależne wagi rzutowań Q, K, V oraz warstw MLP dla tokenów tekstowych i patchy obrazu. Mechanizm uwagi jest współdzielony (co pozwala na interakcję modalności), natomiast pozostałe obliczenia są rozdzielone.
- Trening typu Rectified Flow. Specyficzna wersja dopasowania przepływu (flow matching) z prostszą matematyką i stabilniejszą zbieżnością w porównaniu do klasycznego DDPM.
- Skala modelu. MMDiT stanowi szkielet modeli SD3 o rozmiarach 2B i 8B parametrów. Badania Transfusion skalowano z kolei do 7B parametrów.

Oba te rozwiązania opierają się na tej samej idei: jeden transformator obsługuje zadanie NTP na tekście oraz proces dyfuzji na ciągłych reprezentacjach obrazu.

### Dlaczego to podejście przewyższa model typu Chameleon

Różnica jakościowa pomiędzy ciągłą dyfuzją a dyskretnym NTP w generowaniu obrazów jest mierzalna. Badania Transfusion wykazują, że:
- Przy modelu o rozmiarze 7B parametrów, Transfusion osiąga wynik wskaźnika FID lepszy o 3-5 punktów w porównaniu do modelu typu Chameleon o tym samym rozmiarze.
- Nie ma potrzeby trenowania skomplikowanego tokenizera VQ-VAE — rzutowanie obrazu odbywa się za pomocą prostej warstwy liniowej (podobnie jak w ViT).
- Wnioskowanie pozwala na zrównoleglenie procesu odszumiania patchy obrazu, w przeciwieństwie do sekwencyjnego próbkowania tokenów w modelach autoregresywnych.

Wada: Transfusion to model optymalizowany dwiema różnymi funkcjami strat, co znacząco utrudnia stabilizację dynamiki treningu. Dobór współczynników wagowych strat wymaga precyzyjnego dostrajania, aby uniknąć dominacji jednej z modalności nad drugą.

### Rozwój i wdrożenia pochodne

Model Janus-Pro (Lekcja 12.15) rozwija ideę Transfusion, stosując dwa osobne encodery wizyjne do zadań rozumienia (SigLIP) i generowania (VQ), jednocześnie współdzieląc korpus transformatora. Show-o (Lekcja 12.14) zastępuje klasyczną dyfuzję dyfuzją dyskretną (maskowane modelowanie języka).

Komercyjne modele VLM z 2026 roku generujące obrazy (takie jak Gemini 3 Pro, GPT-5 czy Claude 3.5/4 Opus) wykorzystują warianty oparte na zunifikowanym transformatorze i ciągłych reprezentacjach wizualnych.

## Użycie praktyczne

Skrypt `code/main.py` implementuje uproszczony model Transfusion na syntetycznym zadaniu w skali MNIST:

- Prompty tekstowe to krótkie sekwencje liczb opisujące cyfrę (0-9).
- Obrazy są reprezentowane jako ciągła siatka o wymiarach 4x4.
- Zaimplementowano model z dwiema głowicami wyjściowymi (NTP dla tekstu oraz MSE dla zaszumionych patchy obrazu).
- Pętla treningowa optymalizuje jednocześnie obie straty przy użyciu blokowo-trójkątnej maski uwagi.
- Proces generowania tworzy opis tekstowy i obraz 4x4 w ramach jednej sesji wnioskowania.

Kod demonstruje architekturę przesyłu danych, konstrukcję maski uwagi oraz algorytm wnioskowania.

## Zadanie zaliczeniowe

W ramach tej lekcji należy stworzyć dokument `outputs/skill-two-loss-trainer-designer_pro.md`. Na podstawie opisu nowego zadania multimodalnego (np. tekst + obraz, tekst + dźwięk, tekst + wideo), zaprojektuj architekturę treningu z dwiema funkcjami strat (wagi strat, struktura maski uwagi, podział na bloki współdzielone i specyficzne dla modalności) oraz określ potencjalne ryzyka wdrożeniowe.

## Ćwiczenia

1. Model typu Transfusion przetwarza w paczce treningowej 70% tokenów tekstowych i 30% patchy obrazu. Średnia wartość straty dyfuzji obrazu jest około 10 razy wyższa niż strata NTP dla tekstu. Zaproponuj współczynniki wagowe dla obu strat, aby zbalansować proces uczenia.

2. Narysuj blokowo-trójkątną maskę uwagi dla sekwencji: `[T, T, <image>, P, P, P, P, </image>, T]`. Oznacz każdy element wartością 0 (brak interakcji) lub 1 (uwaga aktywna).

3. Model MMDiT wykorzystuje oddzielne wagi QKV dla każdej modalności w blokach transformatora. O ile zwiększa to liczbę parametrów modelu w porównaniu do zunifikowanego transformatora Transfusion? Czy w modelu o rozmiarze 7B parametrów inwestycja ta jest uzasadniona?

4. Proces wnioskowania: po otrzymaniu promptu tekstowego model generuje autoregresyjnie (NTP) 50 tokenów tekstu, po napotkaniu tagu `<image>` uruchamia pętlę dyfuzji dla 256 patchy obrazu w 20 krokach odszumiania. Ile łącznie przebiegów forward modelu należy wykonać?

5. Przeczytaj sekcję 3 w artykule o Stable Diffusion 3 (arXiv:2403.03206). Opisz koncepcję Rectified Flow i wyjaśnij, dlaczego pozwala ona na zbieżność w mniejszej liczbie kroków wnioskowania niż tradycyjny model DDPM.

## Słownik pojęć

| Termin | Potoczne określenie | Co to dokładnie oznacza |
|------|-----------------|--------------------------------------|
| Trening z dwiema stratami | „NTP + dyfuzja” | Wspólna optymalizacja straty entropii krzyżowej (dla tekstu) oraz straty MSE (dla ciągłych patchy obrazu) w jednym kroku gradientu. |
| Dopasowanie przepływu | „Flow matching” | Metoda generatywna oparta na dyfuzji, w której model uczy się przewidywać wektor prędkości transformacji szumu w czyste dane. |
| MMDiT | „Multimodalny DiT” | Architektura transformatora dyfuzyjnego (z SD3) ze współdzieloną uwagą i dedykowanymi warstwami MLP dla różnych modalności. |
| Maska blokowo-trójkątna | „Przyczynowo-dwukierunkowa” | Maska uwagi wymuszająca przyczynowość dla tekstu, pozwalając jednocześnie na dwukierunkową wymianę informacji w ramach klocków obrazu. |
| Ciągła reprezentacja | „No-VQ / brak kwantyzacji” | Przetwarzanie patchy obrazu jako wektorów liczb rzeczywistych, bez dyskretyzacji na indeksy z książki kodowej. |
| Przewidywanie prędkości | „v-parametryzacja” | Konfiguracja modelu dyfuzyjnego, w której wyjściem sieci jest wektor prędkości interpolacji, a nie sam szum bazowy. |

## Dalsze czytanie

- [Zhou et al. — Transfusion: Predict the Next Token and Predict the Next Noise (arXiv:2408.11039)](https://arxiv.org/abs/2408.11039)
- [Esser et al. — Scaling Rectified Flow Transformers for High-Resolution Image Synthesis (arXiv:2403.03206)](https://arxiv.org/abs/2403.03206)
- [Peebles and Xie — Scalable Diffusion Models with Transformers (arXiv:2212.09748)](https://arxiv.org/abs/2212.09748)
- [Zhao et al. — MonoFormer: One Transformer for Both Writing and Drawing (arXiv:2409.16280)](https://arxiv.org/abs/2409.16280)
- [Xie et al. — Show-o: One Single Transformer to Unify Temporal, Spatial, and Multimodal Understanding (arXiv:2408.12528)](https://arxiv.org/abs/2408.12528)
