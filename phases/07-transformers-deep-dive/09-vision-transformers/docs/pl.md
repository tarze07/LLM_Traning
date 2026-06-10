# Transformatory wizyjne (ViT)

> Obraz jest siatką plam. Zdanie to siatka żetonów. Ten sam transformator zjada oba.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 7 · 05 (Pełny transformator), Faza 4 · 03 (CNN), Faza 4 · 14 (wprowadzenie do Transformatorów wizyjnych)
**Czas:** ~45 minut

## Problem

Przed rokiem 2020 wizja komputerowa oznaczała sploty. Każda SOTA w ImageNet, COCO i benchmarkach wykrywania korzystała ze szkieletu CNN. Transformatory były dla języka.

Dosovitskiy i in. (2020) — „Obraz jest wart 16 x 16 słów” — pokazał, że można całkowicie zrezygnować ze splotów. Pokrój obraz na fragmenty o stałym rozmiarze, liniowo wyświetl każdy fragment w formie osadzania, podaj sekwencję do kodera z transformatorem waniliowym. W wystarczającej skali (wstępne szkolenie ImageNet-21k lub większe) ViT dorównuje lub pokonuje modele oparte na ResNet.

ViT był początkiem szerszego wzorca w 2026 r.: jedna architektura, wiele modalności. Szept tokenizuje dźwięk. ViT tokenizuje obrazy. Żetony akcji dla robotyki. Tokeny pikseli dla wideo. Transformatorowi to nie przeszkadza — podaj mu sekwencję, a się nauczy.

Do 2026 r. ViT i jego potomkowie (DeiT, Swin, DINOv2, ViT-22B, SAM 3) będą posiadać większość wizji. Sieci CNN nadal wygrywają w przypadku urządzeń brzegowych i zadań wrażliwych na opóźnienia. Wszystko inne ma gdzieś na stosie ViT.

## Koncepcja

![Obraz → łatki → tokeny → transformator](../assets/vit.svg)

### Krok 1 — naprawa

Podziel obraz `H × W × C` na sekwencję `N × (P·P·C)` płaskich fragmentów. Typowa konfiguracja: obraz `224 × 224`, poprawki `16 × 16` → 196 poprawek po 768 wartości każda.

```
image (224, 224, 3) → 14 × 14 grid of 16x16x3 patches → 196 vectors of length 768
```

Rozmiar łaty to dźwignia. Mniejsze łatki = więcej tokenów, lepsza rozdzielczość, kwadratowy koszt uwagi. Większe łaty = grubsze, tańsze.

### Krok 2 — osadzanie liniowe

Pojedyncza wyuczona macierz rzutuje każdą płaską poprawkę na `d_model`. Odpowiednik splotu rozmiaru jądra `P` i kroku `P`. W PyTorch jest to dosłownie `nn.Conv2d(C, d_model, kernel_size=P, stride=P)` — implementacja dwuwierszowa.

### Krok 3 — dodaj token `[CLS]`, dodaj osadzania pozycyjne

- Dołącz token `[CLS]`, którego można się nauczyć. Jego ostatecznym stanem ukrytym jest reprezentacja obrazu używana do klasyfikacji.
- Dodaj możliwe do nauczenia osadzania pozycyjne (oryginalne ViT) lub sinusoidalne 2D (późniejsze warianty).
- W roku 2024+ RoPE rozszerzono do 2D dla pozycji, czasami bez wyraźnych osadzań.

### Krok 4 — standardowy enkoder transformatorowy

Ułóż L bloków `LayerNorm → Self-Attention → + → LayerNorm → MLP → +`. Identyczny jak BERT. Brak warstw specyficznych dla wizji. To jest puenta pedagogiczna tej gazety.

### Krok 5 — głowa

Do klasyfikacji: weź `[CLS]` stan ukryty → liniowy → softmax. W przypadku DINOv2 lub SAM odrzuć `[CLS]` i użyj bezpośrednio osadzonych poprawek.

### Warianty, które miały znaczenie

| Modelka | Rok | Zmień |
|-------|------|------------|
| ViT | 2020 | Oryginał. Naprawiono rozmiar łatki, pełna globalna uwaga. |
| DeiT | 2021 | Destylacja; można trenować tylko w ImageNet-1k. |
| Świń | 2021 | Hierarchiczny z przesuniętymi oknami. Stały koszt subkwadratowy. |
| DINOv2 | 2023 | Samonadzorowany (bez etykiet). Najlepsze funkcje ogólnego widzenia. |
| ViT-22B | 2023 | parametry 22B; obowiązują przepisy dotyczące skalowania. |
| SigLIP | 2023 | ViT + para językowa, esowata utrata kontrastowa. |
| SAM 3 | 2025 | Segmentuj wszystko; ViT-Large + dekoder maski z podpowiedzią. |

### Dlaczego zajęło to trochę czasu

ViT potrzebuje *dużo* danych, aby dopasować CNN, ponieważ nie ma żadnego z odchyleń indukcyjnych CNN (niezmienniczość tłumaczenia, lokalność). Bez > 100 milionów obrazów oznaczonych etykietami lub solidnego samonadzorowanego szkolenia wstępnego CNN nadal wygrywają, jeśli chodzi o dopasowane obliczenia. DeiT naprawił ten problem w 2021 r. za pomocą sztuczek związanych z destylacją; DINOv2 naprawił to na stałe w 2023 roku dzięki samonadzorowi.

## Zbuduj to

Zobacz `code/main.py`. Łatanie w trybie Pure-stdlib + osadzanie liniowe + kontrola poprawności. Żadnego szkolenia — ViT w dowolnej realistycznej skali wymaga PyTorch i godzin pracy procesora graficznego.

### Krok 1: fałszywy obraz

Obraz RGB o wymiarach 24 × 24 jako lista wierszy krotek `(R, G, B)`. Używamy 6×6 łatek → 16 łatek, każdy o 108-d wektorze osadzającym.

### Krok 2: naprawa

```python
def patchify(image, P):
    H = len(image)
    W = len(image[0])
    patches = []
    for i in range(0, H, P):
        for j in range(0, W, P):
            patch = []
            for di in range(P):
                for dj in range(P):
                    patch.extend(image[i + di][j + dj])
            patches.append(patch)
    return patches
```

Kolejność rastrów: główny wiersz w siatce. Każdy ViT stosuje tę kolejność.

### Krok 3: osadzanie liniowe

Pomnóż każdy płaski fragment przez losową macierz `(patch_flat_size, d_model)`. Sprawdź, czy kształt wyjściowy to `(N_patches + 1, d_model)` po dodaniu `[CLS]`.

### Krok 4: policz parametry, aby uzyskać realistyczną ViT

Wydrukuj licznik parametrów dla ViT-Base: 12 warstw, 12 głowic, d=768, patch=16. Porównaj z ResNet-50 (~25M). ViT-Base ląduje na ~86M. ViT-duży ~307M. ViT-Ogromny ~632M.

## Użyj tego

```python
from transformers import ViTImageProcessor, ViTModel
import torch
from PIL import Image

processor = ViTImageProcessor.from_pretrained("google/vit-base-patch16-224-in21k")
model = ViTModel.from_pretrained("google/vit-base-patch16-224-in21k")

img = Image.open("cat.jpg")
inputs = processor(img, return_tensors="pt")
out = model(**inputs).last_hidden_state   # (1, 197, 768): [CLS] + 196 patches
cls_emb = out[:, 0]                       # image representation
```

**Osadzanie DINOv2 jest domyślnym ustawieniem funkcji obrazu w roku 2026.** Zamroź kręgosłup, trenuj małą główkę. Działa na rzecz klasyfikacji, wyszukiwania, wykrywania i opisywania. Punkty kontrolne DINOv2 firmy Meta przewyższają CLIP w przypadku każdego zadania związanego z wizją nietekstową.

**Wybór rozmiaru łatki.** Małe modele korzystają z formatu 16×16 (ViT-B/16). Gęste przewidywanie (segmentacja) wykorzystuje 8 × 8 lub 14 × 14 (SAM, DINOv2). Bardzo duże modele korzystają z formatu 14×14.

## Wyślij to

Zobacz `outputs/skill-vit-configurator.md`. Umiejętność wybiera wariant ViT i rozmiar poprawki dla nowego zadania wizyjnego, biorąc pod uwagę rozmiar zestawu danych, rozdzielczość i budżet obliczeniowy.

## Ćwiczenia

1. **Łatwe.** Uruchom `code/main.py`. Sprawdź, czy liczba łat jest równa `(H/P) * (W/P)`, a wymiar płaskiej łaty jest równy `P*P*C`.
2. **Średni.** Implementuj sinusoidalne osadzanie pozycyjne 2D — dwa niezależne kody sinusoidalne dla `row` i `col` każdej poprawki, połączone. Wprowadź je do małego PyTorch ViT i porównaj dokładność z możliwymi do nauczenia się osadzaniami pozycyjnymi na CIFAR-10.
3. **Trudne.** Zbuduj 3-warstwowy ViT (PyTorch), trenuj na 1000 obrazach MNIST z łatami 4×4. Zmierz dokładność testu. Teraz dodaj wstępne szkolenie DINOv2 na tych samych 1000 obrazach (uproszczone: po prostu wytrenuj koder, aby przewidywał osadzanie poprawek na podstawie zamaskowanych poprawek). Czy poprawia się dokładność?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Łatka | „Żeton transformatora wizji” | Płaski wektor wartości pikseli dla `P × P × C` obszaru obrazu. |
| Popraw | „Posiekaj + spłaszcz” | Pokrój obraz na nienakładające się obszary i spłaszcz każdy do wektora. |
| `[CLS]` token | „Podsumowanie obrazu” | Dołączony token, którego można się nauczyć; jego ostatecznym osadzeniem jest reprezentacja obrazu. |
| Odchylenie indukcyjne | „Co zakłada model” | ViT ma mniej priorytetów niż CNN; potrzebuje więcej danych, aby uzupełnić lukę. |
| DINOv2 | „Samonadzorowany ViT” | Trenowany bez etykiet przy użyciu wzmacniania obrazu + nauczyciel pędu. Najlepsze ogólne funkcje obrazu w 2026 r. |
| SigLIP | „Następca CLIP-a” | Koder tekstu ViT + przeszkolony z esowatą utratą kontrastu; lepsze niż CLIP na dopasowanych obliczeniach. |
| Świń | „Okienko ViT” | Hierarchiczny ViT z lokalną uwagą + przesunięte okna; podkwadratowe. |
| Zarejestruj tokeny | „Sztuczka 2023” | Kilka dodatkowych żetonów, których można się nauczyć i które pochłaniają uwagę; poprawia funkcje DINOv2. |

## Dalsze czytanie

- [Dosovitskiy i in. (2020). Obraz jest wart 16x16 słów: transformatory do rozpoznawania obrazów w skali](https://arxiv.org/abs/2010.11929) – artykuł ViT.
- [Touvron i in. (2021). Szkolenie transformatorów obrazu wydajnych pod względem danych i destylacji poprzez uwagę](https://arxiv.org/abs/2012.12877) — DeiT.
- [Liu i in. (2021). Swin Transformer: Hierarchiczny transformator wizyjny wykorzystujący przesunięte okna](https://arxiv.org/abs/2103.14030) — Swin.
- [Oquab i in. (2023). DINOv2: Nauka solidnych funkcji wizualnych bez nadzoru](https://arxiv.org/abs/2304.07193) — DINOv2.
- [Darcet i in. (2023). Transformatory wizyjne wymagają rejestrów](https://arxiv.org/abs/2309.16588) — poprawka dotycząca tokena rejestru dla DINOv2.