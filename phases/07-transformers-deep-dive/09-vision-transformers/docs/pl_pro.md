# Transformatory wizyjne (ViT)

> Obraz to siatka fragmentów. Zdanie to siatka tokenów. Ten sam transformator przetwarza oba.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 7 · 05 (Pełny transformator), Faza 4 · 03 (CNN), Faza 4 · 14 (wprowadzenie do transformatorów wizyjnych)
**Czas:** ~45 minut

## Problem

Przed rokiem 2020 wizja komputerowa oznaczała sieci splotowe. Każde rozwiązanie na poziomie SOTA w benchmarkach ImageNet, COCO i wykrywania obiektów opierało się na szkielecie CNN. Transformatory były domeną języka.

Dosovitskiy i in. (2020) — „An Image is Worth 16×16 Words" — wykazali, że ze splotów można całkowicie zrezygnować. Wystarczy podzielić obraz na fragmenty o stałym rozmiarze, każdy z nich liniowo przekształcić w osadzanie, a powstałą sekwencję podać do standardowego enkodera transformatorowego. Przy odpowiedniej skali danych (wstępne trenowanie na ImageNet-21k lub większym zbiorze) ViT dorównuje modelom opartym na ResNet lub je przewyższa.

ViT zapoczątkował szerszy wzorzec: jedna architektura, wiele modalności. Whisper tokenizuje dźwięk. ViT tokenizuje obrazy. Tokeny akcji stosuje się w robotyce, tokeny pikseli — w przetwarzaniu wideo. Transformator pozostaje obojętny na typ danych — wystarczy podać mu sekwencję.

Do 2026 r. ViT i jego następniki (DeiT, Swin, DINOv2, ViT-22B, SAM 3) zdominowały większość zadań wizyjnych. Sieci CNN wciąż sprawdzają się na urządzeniach brzegowych i w zastosowaniach wymagających niskich opóźnień. W pozostałych przypadkach gdzieś w stosie technologicznym pojawia się ViT.

## Koncepcja

![Obraz → fragmenty → tokeny → transformator](../assets/vit.svg)

### Krok 1 — podział na fragmenty

Obraz `H × W × C` dzielony jest na sekwencję `N × (P·P·C)` spłaszczonych fragmentów. Typowa konfiguracja: obraz `224 × 224`, fragmenty `16 × 16` → 196 fragmentów, każdy o długości wektora 768.

```
image (224, 224, 3) → 14 × 14 grid of 16x16x3 patches → 196 vectors of length 768
```

Rozmiar fragmentu jest kluczowym parametrem. Mniejsze fragmenty oznaczają więcej tokenów, wyższą rozdzielczość przestrzenną i kwadratowo rosnący koszt mechanizmu uwagi. Większe fragmenty dają grubszą reprezentację przy niższym koszcie obliczeniowym.

### Krok 2 — osadzanie liniowe

Pojedyncza wyuczona macierz rzutuje każdy spłaszczony fragment na przestrzeń `d_model`. Jest to odpowiednik splotu o rozmiarze jądra `P` i kroku `P`. W PyTorch wystarczy jedna linijka: `nn.Conv2d(C, d_model, kernel_size=P, stride=P)`.

### Krok 3 — dodanie tokenu `[CLS]` i osadzeń pozycyjnych

- Dołącza się token `[CLS]`, którego reprezentacja jest uczalna. Jego końcowy stan ukryty służy jako reprezentacja całego obrazu przy klasyfikacji.
- Dodaje się uczalne osadzenia pozycyjne (oryginalne ViT) lub sinusoidalne 2D (późniejsze warianty).
- Od roku 2024 RoPE rozszerzono do wymiaru 2D dla pozycji; niekiedy rezygnuje się z jawnych osadzeń pozycyjnych.

### Krok 4 — standardowy enkoder transformatorowy

Bloki `LayerNorm → Self-Attention → + → LayerNorm → MLP → +` układa się w L warstw. Architektura jest identyczna jak w BERT. Nie ma żadnych warstw specyficznych dla danych wizyjnych — to właśnie stanowi główną tezę oryginalnej pracy.

### Krok 5 — głowica klasyfikacyjna

Do klasyfikacji: pobiera się stan ukryty tokenu `[CLS]` → warstwa liniowa → softmax. W modelach takich jak DINOv2 lub SAM token `[CLS]` jest pomijany, a osadzenia fragmentów wykorzystuje się bezpośrednio.

### Warianty o największym znaczeniu

| Model | Rok | Zmiana |
|-------|------|------------|
| ViT | 2020 | Oryginał. Stały rozmiar fragmentu, pełna globalna uwaga. |
| DeiT | 2021 | Destylacja wiedzy; możliwe trenowanie wyłącznie na ImageNet-1k. |
| Swin | 2021 | Hierarchiczny z przesuniętymi oknami. Stały koszt subkwadratowy. |
| DINOv2 | 2023 | Samouczący się (bez etykiet). Najlepsze reprezentacje ogólnych cech wizyjnych. |
| ViT-22B | 2023 | 22 miliardy parametrów; potwierdzenie praw skalowania. |
| SigLIP | 2023 | ViT z parującym enkoderem językowym, sigmoidalna funkcja straty kontrastowej. |
| SAM 3 | 2025 | Segmentuj cokolwiek; ViT-Large z dekoderem masek sterowanym podpowiedzią. |

### Dlaczego ViT potrzebował czasu

ViT wymaga znacznie większych zbiorów danych niż CNN, ponieważ nie korzysta z żadnych z jej indukcyjnych preferencji (niezmienność na translację, lokalność). Bez ponad 100 milionów obrazów z etykietami lub solidnego samoucząc się wstępnego trenowania CNN wygrywa przy porównywalnym budżecie obliczeniowym. DeiT rozwiązał ten problem w 2021 r. dzięki technikom destylacji, a DINOv2 w 2023 r. wyeliminował go trwale poprzez uczenie bez nadzoru.

## Zbuduj to

Zobacz `code/main.py`. Podział na fragmenty w czystym Pythonie (bez zewnętrznych bibliotek) wraz z osadzaniem liniowym i weryfikacją poprawności. Trenowanie pominięto — ViT w realistycznej skali wymaga PyTorch i wielu godzin na GPU.

### Krok 1: sztuczny obraz

Obraz RGB o wymiarach 24 × 24 jako lista wierszy krotek `(R, G, B)`. Używamy fragmentów 6×6 → 16 fragmentów, każdy reprezentowany przez wektor osadzenia o wymiarze 108.

### Krok 2: podział na fragmenty

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

Kolejność rastrowania: wiersz po wierszu (ang. row-major). Tę kolejność stosuje każda implementacja ViT.

### Krok 3: osadzanie liniowe

Każdy spłaszczony fragment mnoży się przez losową macierz `(patch_flat_size, d_model)`. Po dodaniu tokenu `[CLS]` kształt wyjścia powinien wynosić `(N_patches + 1, d_model)`.

### Krok 4: zlicz parametry dla realistycznego ViT

Wypisz liczbę parametrów dla ViT-Base: 12 warstw, 12 głowic, d=768, patch=16. Porównaj z ResNet-50 (~25M). ViT-Base ma ~86M parametrów, ViT-Large ~307M, ViT-Huge ~632M.

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

**Osadzenia DINOv2 są domyślnym wyborem do reprezentacji obrazów w 2026 r.** Wystarczy zamrozić kręgosłup modelu i wytrenować małą głowicę. Podejście sprawdza się przy klasyfikacji, wyszukiwaniu, detekcji i opisywaniu obrazów. Punkty kontrolne DINOv2 od Meta przewyższają CLIP we wszystkich zadaniach wizyjnych niezwiązanych z tekstem.

**Wybór rozmiaru fragmentu.** Małe modele używają fragmentów 16×16 (ViT-B/16). Zadania wymagające gęstych predykcji (segmentacja) korzystają z fragmentów 8×8 lub 14×14 (SAM, DINOv2). Bardzo duże modele pracują na fragmentach 14×14.

## Wyślij to

Zobacz `outputs/skill-vit-configurator.md`. Umiejętność dobiera wariant ViT i rozmiar fragmentu do nowego zadania wizyjnego na podstawie rozmiaru zbioru danych, rozdzielczości i budżetu obliczeniowego.

## Ćwiczenia

1. **Łatwe.** Uruchom `code/main.py`. Sprawdź, czy liczba fragmentów wynosi `(H/P) * (W/P)`, a wymiar spłaszczonego fragmentu — `P*P*C`.
2. **Średnie.** Zaimplementuj sinusoidalne osadzenia pozycyjne 2D: dwa niezależne kody sinusoidalne dla `row` i `col` każdego fragmentu, a następnie je połącz. Wprowadź je do małego ViT w PyTorch i porównaj dokładność z uczalnymi osadzeniami pozycyjnymi na zbiorze CIFAR-10.
3. **Trudne.** Zbuduj 3-warstwowy ViT w PyTorch i wytrenuj go na 1000 obrazach MNIST z fragmentami 4×4. Zmierz dokładność na zbiorze testowym. Następnie dodaj wstępne trenowanie w stylu DINOv2 na tych samych 1000 obrazach (uproszczone: wytrenuj enkoder do przewidywania osadzeń fragmentów na podstawie zamaskowanych wejść). Sprawdź, czy dokładność wzrasta.

## Kluczowe terminy

| Termin | Co się mówi | Co to faktycznie oznacza |
|------|-----------------|----------------------|
| Łatka (patch) | „Token transformatora wizyjnego" | Spłaszczony wektor wartości pikseli dla obszaru `P × P × C` obrazu. |
| Patchify | „Potnij i spłaszcz" | Podział obrazu na nienakładające się fragmenty i spłaszczenie każdego do wektora. |
| Token `[CLS]` | „Podsumowanie obrazu" | Dołączony uczalny token; jego końcowe osadzenie reprezentuje cały obraz. |
| Uprzedzenie indukcyjne | „Założenia modelu" | ViT ma ich mniej niż CNN; potrzebuje więcej danych, aby nadrobić tę różnicę. |
| DINOv2 | „Samouczący się ViT" | Trenowany bez etykiet z użyciem augmentacji obrazów i nauczyciela opartego na pędzie. Najlepsze ogólne reprezentacje wizualne w 2026 r. |
| SigLIP | „Następca CLIP-a" | ViT sparowany z enkoderem tekstowym, trenowany z sigmoidalną stratą kontrastową; lepszy od CLIP przy porównywalnych zasobach. |
| Swin | „Okienkowy ViT" | Hierarchiczny ViT z lokalną uwagą i przesuniętymi oknami; złożoność subkwadratowa. |
| Tokeny rejestrów | „Sztuczka z 2023 r." | Kilka dodatkowych uczalnych tokenów absorbujących uwagę; poprawia jakość reprezentacji DINOv2. |

## Dalsze czytanie

- [Dosovitskiy i in. (2020). An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale](https://arxiv.org/abs/2010.11929) — artykuł źródłowy ViT.
- [Touvron i in. (2021). Training data-efficient image transformers & distillation through attention](https://arxiv.org/abs/2012.12877) — DeiT.
- [Liu i in. (2021). Swin Transformer: Hierarchical Vision Transformer using Shifted Windows](https://arxiv.org/abs/2103.14030) — Swin.
- [Oquab i in. (2023). DINOv2: Learning Robust Visual Features without Supervision](https://arxiv.org/abs/2304.07193) — DINOv2.
- [Darcet i in. (2023). Vision Transformers Need Registers](https://arxiv.org/abs/2309.16588) — tokeny rejestrów dla DINOv2.
