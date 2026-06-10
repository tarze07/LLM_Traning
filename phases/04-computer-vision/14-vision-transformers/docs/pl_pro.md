Created At: 2026-06-08T18:20:54Z
Completed At: 2026-06-08T18:20:54Z
File Path: `file:///C:/poligon/LLM_Traning/phases/04-computer-vision/14-vision-transformers/docs/pl_pro.md`

# Vision Transformers (ViT)

> Podziel obraz na patche (fragmenty), potraktuj każdy patch jak słowo w tekście i prześlij sekwencję do klasycznego Transformera. Nie oglądaj się za siebie.

**Typ:** Kompilacja  
**Języki:** Python  
**Wymagania wstępne:** Faza 7, lekcja 02 (mechanizm uwagi – self-attention); faza 4, lekcja 04 (klasyfikacja obrazów)  
**Czas:** ~45 minut  

## Cele nauczania

- Zaimplementować od podstaw mechanizm rzutowania patchów (patch embedding), wyuczone kodowanie pozycyjne (positional embedding), token klasy `[CLS]` oraz bloki enkodera Transformera, tworząc minimalny model ViT.
- Wyjaśnić, dlaczego początkowo sądzono, że modele ViT wymagają gigantycznych zbiorów danych do pre-treningu, oraz jak koncepcje takie jak DeiT i MAE zmieniły to podejście.
- Porównać architektury ViT, Swin oraz ConvNeXt pod kątem założeń projektowych (brak ograniczeń indukcyjnych, uwaga w oknach lokalnych, nowoczesne sploty).
- Dostroić pre-trenowany model ViT na niewielkim zbiorze danych za pomocą biblioteki `timm` przy użyciu sondy liniowej (linear probe) oraz pełnego fine-tuningu.

## Problem

Przez dekadę operacja splotu była synonimem wizji komputerowej. Sieci CNN posiadały silne skrzywienia indukcyjne (inductive biases) – lokalność przetwarzania oraz niezmienniczość na przesunięcia (translation equivariance) – co czyniło je bezkonkurencyjnymi. Dopiero praca Dosovitskiy'ego i in. (2020) wykazała, że standardowy Transformer zastosowany do spłaszczonych fragmentów obrazu (patchy), pozbawiony jakichkolwiek warstw splotowych, jest w stanie dorównać lub nawet przewyższyć najlepsze sieci CNN przy odpowiedniej skali uczenia.

Haczyk tkwił jednak w słowie „skala”. Model ViT trenowany wyłącznie na zbiorze ImageNet-1k osiągał gorsze wyniki niż klasyczny ResNet. Dopiero wstępne przeszkolenie na potężnych zbiorach ImageNet-21k lub JFT-300M i późniejsze dostrojenie na ImageNet-1k pozwalało mu wygrać rywalizację. Wykazano, że Transformerom brakuje wbudowanych założeń o strukturze obrazu, ale są ze stanu samodzielnie wyuczyć się tych zależności, o ile otrzymają wystarczająco dużo danych. Kolejne badania (takie jak DeiT, MAE czy DINO) udowodniły, że dzięki odpowiednim technikom treningowym – intensywnej augmentacji danych, uczeniu samo-nadzorowanemu czy destylacji wiedzy – modele ViT można efektywnie trenować także na mniejszych zbiorach danych.

W zastosowaniach brzegowych sieci CNN wciąż pozostają konkurencyjne (architektura ConvNeXt jest tu bardzo mocna), jednak w pozostałych obszarach niepodzielnie rządzą Transformery: w segmentacji (Mask2Former, SegFormer), detekcji obiektów (DETR, RT-DETR), modelach multimodalnych (CLIP, SigLIP) oraz wideo (VideoMAE, V-JEPA). Zrozumienie wewnętrznej struktury ViT jest kluczem do nowoczesnej wizji komputerowej.

## Koncepcja

### Potok przetwarzania (Pipeline)

```mermaid
flowchart LR
    IMG["Obraz<br/>(3, 224, 224)"] --> PATCH["Rzutowanie patchów<br/>splot 16x16, krok=16<br/>-> (768, 14, 14)"]
    PATCH --> FLAT["Spłaszczenie do<br/>(196, 768) tokenów"]
    FLAT --> CAT["Dodanie tokena<br/>[CLS] na początku"]
    CAT --> POS["Dodanie wyuczonego<br/>kodowania poz."]
    POS --> ENC["N bloków enkodera<br/>Transformera"]
    ENC --> CLS["Pobranie wyjścia<br/>tokena [CLS]"]
    CLS --> HEAD["Klasyfikator MLP"]

    style PATCH fill:#dbeafe,stroke:#2563eb
    style ENC fill:#fef3c7,stroke:#d97706
    style HEAD fill:#dcfce7,stroke:#16a34a
```

Proces składa się z siedmiu głównych etapów: podział na patche $\to$ generowanie tokenów $\to$ mechanizm uwagi $\to$ klasyfikacja. Różne warianty architektoniczne (takie jak DeiT, Swin, ConvNeXt czy MAE) modyfikują wybrane z tych kroków, zachowując ogólny zarys potoku.

### Rzutowanie patchów (Patch Embedding)

Kluczem do sukcesu jest pierwsza warstwa splotowa o rozmiarze filtra (kernel) równej 16 i kroku (stride) równym 16. Dzięki temu obraz o rozmiarze $224 \times 224$ zostaje przekształcony w siatkę $14 \times 14$ nienakładających się patchów o rozmiarze $16 \times 16$ każdy, a każdy patch zostaje rzutowany liniowo w wektor o wymiarze 768. Ta pojedyncza operacja splotu realizuje jednocześnie podział na fragmenty oraz rzutowanie do przestrzeni cech:

```
Wejście: (3, 224, 224)
Splot (3 -> 768, k=16, s=16, bez dopełnienia):
Wyjście: (768, 14, 14)
Spłaszczenie przestrzenne: (196, 768)
```

Otrzymujemy $196$ patchów (tokenów). Rozmiar wektora cech każdego tokena (hidden dimension) wynosi odpowiednio: 768 dla ViT-Base (ViT-B), 1024 dla ViT-Large (ViT-L) oraz 1280 dla ViT-Huge (ViT-H).

### Token klasy (Class Token)

Wyuczony wektor parametrów dodany na początku sekwencji tokenów:

```
tokeny = [CLS; patch_1; patch_2; ...; patch_196]   kształt (197, 768)
```

Po przejściu przez $N$ bloków Transformera, stan wyjściowy powiązany z tokenem `[CLS]` służy jako zagregowana, globalna reprezentacja całego obrazu. Ostateczna głowa klasyfikatora pobiera wyłącznie ten jeden wektor cech.

### Kodowanie pozycyjne (Positional Embedding)

Klasyczny Transformer nie posiada informacji o dwuwymiarowej geometrii obrazu. W celu wprowadzenia informacji przestrzennej, do wektorów cech każdego tokena dodaje się wyuczony wektor pozycji:

```
tokeny = tokeny + wyuczone_kodowanie_pozycyjne   (również kształt (197, 768))
```

Te współczynniki są parametrami modelu podlegającymi optymalizacji (uczą się w procesie wstecznej propagacji), co pozwala modelowi samodzielnie odtworzyć geometrię 2D obrazu. Istnieją również warianty ze stałym kodowaniem sinusoidalnym 2D, lecz wyuczone wektory pozycyjne są standardem w praktycznych wdrożeniach.

### Blok enkodera Transformera

Klasyczna struktura: wielogłowicowy mechanizm uwagi (Multi-Head Self-Attention – MSA), blok MLP z funkcją aktywacji GELU, połączenia omijające (residual connections) oraz normalizacja LayerNorm aplikowana przed blokami (Pre-LN).

```
x = x + MSA(LN(x))
x = x + MLP(LN(x))

MLP składa się z dwóch warstw z GELU: Linear(dim -> 4 * dim) -> GELU -> Linear(4 * dim -> dim)
```

Model ViT-B/16 składa się z 12 takich bloków, każdy wyposażony jest w 12 głowic uwagi, co łącznie przekłada się na ok. 86 milionów parametrów.

### Dlaczego Pre-LN?

Pierwsze modele Transformer wykorzystywały normalizację Post-LN (`x = LN(x + sublayer(x))`), co uniemożliwiało stabilny trening głębszych struktur bez skomplikowanego harmonogramu rozgrzewki (warmup). Zastosowanie normalizacji Pre-LN (`x = x + sublayer(LN(x))`) pozwala na stabilne uczenie bardzo głębokich sieci od samego początku. Obecnie standard Pre-LN jest powszechnie stosowany w modelach ViT oraz we wszystkich wiodących modelach LLM.

### Kompromis rozmiaru patcha (Patch Size)

- Patche $16 \times 16$: daje 196 tokenów, standardowa i sprawdzona wartość.
- Patche $32 \times 32$: daje 49 tokenów; szybkie działanie, ale słabsza szczegółowość przestrzenna.
- Patche $8 \times 8$: daje 784 tokeny; wysoka precyzja geometryczna, lecz koszt obliczeniowy uwagi rośnie kwadratowo ($O(N^2)$).

Większe rozmiary patchów oznaczają mniejszą liczbę tokenów, co przyspiesza działanie, lecz gubi drobne detale geometryczne. Model SwinV2 stosuje patche $4 \times 4$ połączone z piramidą rozdzielczości i uwagą w oknach lokalnych.

### Metodologia uczenia DeiT

Pierwsze modele ViT wymagały ogromnego zbioru JFT-300M, aby dorównać sieciom CNN. Model DeiT (Touvron i in., 2020) osiągnął wynik 81.8% Top-1 na standardowym ImageNet-1k za pomocą czterech innowacji w procesie treningu:

1. Intensywna augmentacja danych: techniki RandAugment, Mixup, CutMix oraz Random Erasing.
2. Stochastic Depth (losowe wyłączanie całych bloków sieci w trakcie uczenia).
3. Repeated Augmentation (przekazywanie tej samej próbki z różną augmentacją w obrębie jednej paczki).
4. Destylacja wiedzy (knowledge distillation) z silnego modelu splotowego (CNN) pełniącego rolę nauczyciela.

Wszystkie współczesne schematy uczenia modeli ViT bazują na tych zasadach.

### Swin vs. ConvNeXt

- **Swin** (Liu i in., 2021) – model oparty na uwadze w oknach lokalnych (Shifted Windows). Obliczenia uwagi zachodzą wyłącznie w małych, lokalnych obszarach obrazu, które w kolejnych warstwach są przesuwane w celu wymiany informacji. Przywraca to lokalność cech charakterystyczną dla CNN przy zachowaniu elastyczności mechanizmu uwagi.
- **ConvNeXt** (Liu i in., 2022) – sieć splotowa zmodernizowana w taki sposób, aby odtworzyć kluczowe wybory projektowe z modelu Swin (sploty głębokie – depthwise convolutions, normalizacja LayerNorm zamiast BatchNorm, aktywacja GELU, struktura inverted bottleneck). Praca ta udowodniła, że przewaga Swin nie wynikała z samego mechanizmu uwagi, lecz z nowoczesnego schematu treningu i doboru warstw.

Zarówno modele ConvNeXt-V2, jak i Swin-V2 są doskonałym wyborem produkcyjnym. Wybór zależy od środowiska docelowego (ConvNeXt znacznie lepiej kompiluje się na układach brzegowych i NPU) oraz dostępności pre-trenowanych wag.

### Pre-trening samonadzorowany MAE (Masked Autoencoders)

Koncepcja MAE (He i in., 2022): z obrazu losowo usuwa się aż 75% patchów. Koder ViT przetwarza wyłącznie pozostałe 25% widocznych fragmentów. Następnie lekki dekoder rekonstruuje usunięte patche na podstawie cech wyjściowych kodera. Po zakończeniu tego uczenia samo-nadzorowanego, dekoder jest usuwany, a koder podlega standardowemu dostrajaniu (fine-tuning) do docelowego zadania.

Uczenie MAE pozwala na trenowanie modeli ViT bezpośrednio na zbiorze ImageNet-1k do wyników klasy SOTA i stanowi obecnie dominujący schemat uczenia samo-nadzorowanego.

## Zbuduj to

### Krok 1: Rzutowanie patchów (Patch Embedding)

```python
import torch
import torch.nn as nn

class PatchEmbedding(nn.Module):
    def __init__(self, in_channels=3, patch_size=16, dim=192, image_size=64):
        super().__init__()
        assert image_size % patch_size == 0
        self.proj = nn.Conv2d(in_channels, dim, kernel_size=patch_size, stride=patch_size)
        num_patches = (image_size // patch_size) ** 2
        self.num_patches = num_patches

    def forward(self, x):
        x = self.proj(x)
        return x.flatten(2).transpose(1, 2)
```

Pojedyncza warstwa splotowa, spłaszczenie oraz transpozycja wymiarów – to wszystko, co jest potrzebne do konwersji obrazu na sekwencję tokenów.

### Krok 2: Blok enkodera Transformera

```python
class Block(nn.Module):
    def __init__(self, dim, num_heads, mlp_ratio=4, dropout=0.0):
        super().__init__()
        self.ln1 = nn.LayerNorm(dim)
        self.attn = nn.MultiheadAttention(dim, num_heads, dropout=dropout, batch_first=True)
        self.ln2 = nn.LayerNorm(dim)
        self.mlp = nn.Sequential(
            nn.Linear(dim, dim * mlp_ratio),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(dim * mlp_ratio, dim),
            nn.Dropout(dropout),
        )

    def forward(self, x):
        a, _ = self.attn(self.ln1(x), self.ln1(x), self.ln1(x), need_weights=False)
        x = x + a
        x = x + self.mlp(self.ln2(x))
        return x
```

Klasa `nn.MultiheadAttention` odpowiada za podział na głowice, skalowanie iloczynu skalarnego (scaled dot-product) oraz rzutowanie wyjściowe. Dzięki `batch_first=True` tensory wejściowe i wyjściowe mają wymiary `(N, seq, dim)`.

### Krok 3: Kompletny model ViT

```python
class ViT(nn.Module):
    def __init__(self, image_size=64, patch_size=16, in_channels=3,
                 num_classes=10, dim=192, depth=6, num_heads=3, mlp_ratio=4):
        super().__init__()
        self.patch = PatchEmbedding(in_channels, patch_size, dim, image_size)
        num_patches = self.patch.num_patches
        self.cls_token = nn.Parameter(torch.zeros(1, 1, dim))
        self.pos_embed = nn.Parameter(torch.zeros(1, num_patches + 1, dim))
        self.blocks = nn.ModuleList([
            Block(dim, num_heads, mlp_ratio) for _ in range(depth)
        ])
        self.ln = nn.LayerNorm(dim)
        self.head = nn.Linear(dim, num_classes)
        nn.init.trunc_normal_(self.pos_embed, std=0.02)
        nn.init.trunc_normal_(self.cls_token, std=0.02)

    def forward(self, x):
        x = self.patch(x)
        cls = self.cls_token.expand(x.size(0), -1, -1)
        x = torch.cat([cls, x], dim=1)
        x = x + self.pos_embed
        for blk in self.blocks:
            x = blk(x)
        x = self.ln(x[:, 0])
        return self.head(x)

vit = ViT(image_size=64, patch_size=16, num_classes=10, dim=192, depth=6, num_heads=3)
x = torch.randn(2, 3, 64, 64)
print(f"Wyjście kształt: {vit(x).shape}")
print(f"Liczba parametrów: {sum(p.numel() for p in vit.parameters()):,}")
```

Lekki model ViT posiadający ok. 2.8 miliona parametrów, który z powodzeniem można trenować i testować nawet na CPU. Pełnowymiarowy model ViT-Base (86M parametrów) otrzymujemy, ustawiając parametry klasy na: `dim=768, depth=12, num_heads=12`.

### Krok 4: Weryfikacja działania (Inference)

```python
logits = vit(torch.randn(1, 3, 64, 64))
print(f"logity: {logits}")
print(f"prawdopodobieństwa: {logits.softmax(-1)}")
```

Kod powinien wykonać się poprawnie, a sumaryczne prawdopodobieństwo klas powinno wynosić 1.0.

## Biblioteki

Biblioteka `timm` (PyTorch Image Models) udostępnia niemal wszystkie warianty modeli ViT z gotowymi wagami pre-trenowanymi na zbiorze ImageNet. Załadowanie modelu sprowadza się do jednej linijki:

```python
import timm

model = timm.create_model("vit_base_patch16_224", pretrained=True, num_classes=10)
```

Biblioteka `timm` to produkcyjny standard w dziedzinie modeli Vision. Obsługuje ona ViT, DeiT, Swin, Swin-V2, ConvNeXt, ConvNeXt-V2, MaxViT, MViT, EfficientFormer i setki innych modeli za pomocą ujednoliconego interfejsu.

W zadaniach multimodalnych (obraz + tekst) wiodąca biblioteka `transformers` oferuje modele takie jak CLIP, SigLIP, BLIP-2 oraz LLaVA. We wszystkich tych modelach koderem obrazu jest właśnie odpowiednio dostosowany wariant sieci ViT.

## Wyślij to

Niniejsza lekcja dostarcza:

- `outputs/prompt-vit-vs-cnn-picker.md` – prompt automatycznie dobierający odpowiednią architekturę (ViT, ConvNeXt lub Swin) na podstawie rozmiaru zbioru danych, budżetu obliczeniowego oraz specyfiki środowiska docelowego.
- `outputs/skill-vit-patch-and-pos-embed-inspector.md` – skrypt weryfikujący zgodność wymiarów rzutowania patchów oraz wektorów kodowania pozycyjnego z wymogami określonej architektury ViT (wykrywanie błędów przenoszenia wag).

## Ćwiczenia

1. **(Łatwe)** Wyświetl wymiary wszystkich tensorów pośrednich w trakcie przejścia w przód przez zaimplementowany model ViT. Potwierdź poprawność przekształceń: wejście `(N, 3, 64, 64)` $\to$ rzutowanie patchów `(N, 16, 192)` $\to$ po dołączeniu tokena `[CLS]` `(N, 17, 192)` $\to$ wejście do klasyfikatora `(N, 192)` $\to$ wyjściowe logity `(N, num_classes)`.
2. **(Średnie)** Wykorzystaj bibliotekę `timm` do załadowania modelu `vit_tiny_patch16_224` i przeprowadź jego fine-tuning na syntetycznym zbiorze CIFAR (z lekcji 4). Porównaj wyniki z analogicznym dostrajaniem modelu ResNet-18. Porównaj czasy uczenia obu modeli oraz uzyskaną dokładność końcową.
3. **(Trudne)** Zaimplementuj proces pre-treningu MAE dla uproszczonego modelu ViT: usuń losowo 75% patchów wejściowych, a następnie wytrenuj koder wraz z lekkim dekoderem do rekonstrukcji brakujących fragmentów obrazu. Porównaj jakość cech reprezentacji (za pomocą sondy liniowej – linear probe) przed rozpoczęciem pre-treningu oraz po jego zakończeniu.

## Kluczowe terminy

| Termin | Obiegowe określenie | Co to oznacza w rzeczywistości |
|------|----------------|----------------------|
| Rzutowanie patchów (Patch Embedding) | Rzutowanie liniowe | Warstwa splotu o rozmiarze filtra równym krokowi (stride), co pozwala przekształcić obraz w siatkę wektorów (tokenów) |
| Token klasy ([CLS] token) | Token klasyfikacji | Zmienna parametryczna dołączana na początku sekwencji; jej wyjściowy wektor reprezentuje całościowe cechy całego obrazu |
| Kodowanie pozycyjne (Positional Embedding) | Wektory pozycji | Wyuczone wektory dodawane do tokenów w celu wstrzyknięcia do Transformera informacji o ich dwuwymiarowej geometrii na obrazie |
| Pre-LN | Normalizacja wstępna | Wariant architektury aplikujący normalizację LayerNorm przed przetworzeniem w bloku (np. uwagi), co gwarantuje wysoką stabilność treningu |
| Multi-Head Attention (MHA) | Skalowana uwaga | Klasyczny mechanizm uwagi realizujący rzutowanie danych do kilku niezależnych podprzestrzeni reprezentacji równolegle |
| ViT-B/16 | Model bazowy | Kanoniczny wariant modelu: wymiar cech 768, 12 bloków enkodera, 12 głowic uwagi, patche 16x16, obraz wejściowy 224x224 (ok. 86M parametrów) |
| DeiT (Data-efficient Image Transformers) | Wydajne uczenie ViT | Metodologia uczenia ViT bezpośrednio na ImageNet-1k z zastosowaniem intensywnej augmentacji danych i destylacji, co eliminuje konieczność pre-treningu na gigantycznych zbiorach danych |
| MAE (Masked Autoencoders) | Samo-nadzorowany pre-trening | Samo-nadzorowany schemat uczenia polegający na rekonstrukcji brakujących 75% fragmentów obrazu; wiodący standard pre-treningu w wizji komputerowej |

## Literatura uzupełniająca

- [An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale (Dosovitskiy et al., 2020)](https://arxiv.org/abs/2010.11929) – artykuł wprowadzający koncepcję Vision Transformers (ViT).
- [Training Data-Efficient Image Transformers & Distillation Through Attention (Touvron et al., 2020)](https://arxiv.org/abs/2012.12877) – opis modelu DeiT i metod efektywnego uczenia bez wielkich zbiorów danych.
- [Masked Autoencoders Are Scalable Vision Learners (He et al., 2022)](https://arxiv.org/abs/2111.06377) – kluczowa praca naukowa wprowadzająca proces samo-nadzorowanego uczenia MAE.
- [Dokumentacja biblioteki timm (PyTorch Image Models)](https://huggingface.co/docs/timm) – oficjalne źródło i kompendium wiedzy o gotowych architekturach wizyjnych w PyTorch.
