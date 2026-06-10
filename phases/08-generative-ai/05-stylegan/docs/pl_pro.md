#StylGAN

> Większość generatorów miesza `z` na każdej warstwie jednocześnie. StyleGAN rozdziela ten proces: najpierw odwzorowuje `z` na pośrednie `w`, a następnie wstrzykuje `w` na każdym poziomie rozdzielczości za pośrednictwem AdaIN. Ta jedna zmiana rozplątała przestrzeń ukrytą i przez siedem lat z rzędu sprawiała, że fotorealistyczne twarze pozostawały problemem rozwiązanym.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 8 · 03 (GAN), Faza 4 · 08 (Normalizacja), Faza 3 · 07 (CNN)
**Czas:** ~45 minut

## Problem

DCGAN odwzorowuje `z` na obraz przez stos transponowanych splotów. Problem polega na tym, że `z` kontroluje wszystko jednocześnie — pozę, oświetlenie, tożsamość i tło — i wszystkie te cechy są ze sobą splecione. Przesunięcie wzdłuż jednej osi `z` zmienia wszystkie cztery naraz. Nie można zapytać modelu „ta sama osoba, inna poza", bo reprezentacja tego po prostu nie obsługuje.

Karras i in. (2019, NVIDIA) zaproponowali inne podejście: zamiast podawać `z` bezpośrednio do warstw konwolucyjnych, jako wejście sieci przekazuje się stały tensor `4×4×512`. Ośmiowarstwowy MLP odwzorowuje `z ∈ Z → w ∈ W`. Wektor `w` jest wstrzykiwany na każdym poziomie rozdzielczości przez *adaptacyjną normalizację instancji* (AdaIN): każda mapa cech jest normalizowana, a następnie skalowana i przesuwana zgodnie z projekcjami afinicznymi `w`. Szum na poziomie warstwy odpowiada za szczegóły stochastyczne, takie jak pory skóry czy pasma włosów.

Wynik: przestrzeń `W` ma w przybliżeniu ortogonalne osie dla „stylu wysokiego poziomu" (poza, tożsamość) i „stylu niskopoziomowego" (oświetlenie, kolor). Można zamieniać style między dwoma obrazami, stosując `w` obrazu A dla niskich rozdzielczości i `w` obrazu B dla wysokich. Otworzyło to drogę do edycji, stylizacji między domenami i całej linii badań nad „inwersją StyleGAN".

## Koncepcja

![StyleGAN: mapowanie sieci + AdaIN + szum na warstwę](../assets/stylegan.svg)

**Sieć mapująca.** `f: Z → W`, ośmiowarstwowy MLP. `Z = N(0, I)^512`. Przestrzeń `W` nie musi być gaussowska — sieć uczy się kształtu dopasowanego do danych.

**Sieć syntezy.** Zaczyna się od wyuczonej stałej `4×4×512`. Każdy blok rozdzielczości: `upsample → conv → AdaIN(w_i) → noise → conv → AdaIN(w_i) → noise`. Rozdzielczości są podwajane: 4, 8, 16, 32, 64, 128, 256, 512, 1024.

**AdaIN.**

```
AdaIN(x, y) = y_scale · (x - mean(x)) / std(x) + y_bias
```

gdzie `y_scale` i `y_bias` pochodzą z projekcji afinicznych `w`. Mapa cech jest normalizowana, a następnie stylizowana. „Styl" oznacza tu statystyki pierwszego i drugiego rzędu mapy cech.

**Szum na warstwę.** Jednokanałowy szum gaussowski jest dodawany do każdej mapy cech i skalowany przez wyuczony współczynnik na kanał. Odpowiada za szczegóły stochastyczne bez wpływu na strukturę globalną.

**Sztuczka z obcięciem.** Podczas wnioskowania oblicza się `w = mapping(z)`, a następnie `w' = ŵ + ψ·(w - ŵ)`, gdzie `ŵ` to średnia `w` z wielu próbek. Wartość `ψ < 1` zamienia różnorodność na jakość. Niemal każde demo StyleGAN korzysta z `ψ ≈ 0.7`.

## StylGAN 1 → 2 → 3

| Wersja | Rok | Innowacja |
|--------|------|------------|
| StylGAN | 2019 | Sieć mapująca + AdaIN + szum + progresywny trening. |
| StylGAN2 | 2020 | Demodulacja wag zastępuje AdaIN (eliminuje artefakty kropelkowe); architektura rezydualna; regularyzacja długości ścieżki. |
| StylGAN3 | 2021 | Sploty pozbawione aliasów i jądra ekwiwariantne; eliminuje przyklejanie się tekstur do siatki pikseli. |
| StylGAN-XL | 2022 | Warunkowanie klasowe, rozdzielczość 1024², zbiór ImageNet. |
| R3GAN | 2024 | Reimplementacja z silniejszą regularyzacją; domyka lukę względem modeli dyfuzyjnych na FFHQ-1024 przy 20-krotnie mniejszej liczbie parametrów. |

W 2026 roku StyleGAN3 pozostaje domyślnym wyborem w trzech zastosowaniach: (a) fotorealizm w wąskich domenach przy wysokiej przepustowości, (b) adaptacja domeny z niewielu próbek (trening na 100 obrazach, zamrożenie sieci mapującej), (c) edycja oparta na inwersji (znalezienie `w` rekonstruującego prawdziwe zdjęcie, a następnie edycja w przestrzeni `W`). Do zamiany tekstu na obraz w otwartej domenie właściwym narzędziem jest dyfuzja, nie StyleGAN.

## Zbuduj to

`code/main.py` implementuje uproszczony „style-GAN lite" w 1D: sieć mapującą MLP, sieć syntezy pobierającą wyuczony wektor stały i modulującą go skalą oraz odchyleniem wynikającym z `w`, a także szum na warstwę. Pokazuje, że wstrzykiwanie `w` przez modulację afiniczną działa lepiej niż podawanie `z` bezpośrednio na wejście generatora.

### Krok 1: sieć mapująca

```python
def mapping(z, M):
    h = z
    for i in range(num_layers):
        h = leaky_relu(add(matmul(M[f"W{i}"], h), M[f"b{i}"]))
    return h
```

### Krok 2: adaptacyjna normalizacja instancji

```python
def adain(x, w_scale, w_bias):
    mu = mean(x)
    sd = std(x)
    x_norm = [(xi - mu) / (sd + 1e-8) for xi in x]
    return [w_scale * xi + w_bias for xi in x_norm]
```

Skala i odchylenie dla poszczególnych cech pochodzą z `w` przez projekcję liniową.

### Krok 3: szum na poziomie warstwy

```python
def add_noise(x, sigma, rng):
    return [xi + sigma * rng.gauss(0, 1) for xi in x]
```

Parametr sigma można uczyć osobno dla każdego kanału.

## Pułapki

- **Artefakty kropelkowe.** StyleGAN 1 wytwarzał plamkowe kropelki na mapach cech, ponieważ AdaIN zerował średnią aktywacji. StyleGAN 2 rozwiązuje ten problem przez demodulację wag splotów zamiast normalizowania aktywacji.
- **Przyklejanie tekstur.** W StyleGAN 1 i 2 tekstury podążały za współrzędnymi pikseli, a nie za współrzędnymi obiektu — widoczne zwłaszcza podczas interpolacji. StyleGAN 3 eliminuje ten problem przez sploty pozbawione aliasów z filtrami sinc.
- **Pokrycie trybów.** Obcięcie `ψ < 0.7` daje czyste wyniki, ale próbki pochodzą z wąskiego stożka; jeśli potrzebna jest różnorodność, należy użyć `ψ = 1.0`.
- **Inwersja jest stratna.** Odwrócenie prawdziwego zdjęcia do przestrzeni `W` odbywa się zazwyczaj przez optymalizację lub koder (e4e, ReStyle, HyperStyle). Przy wielu iteracjach wyniki zaczynają dryftować.

## Użyj tego

| Przypadek użycia | Podejście |
|---------|----------|
| Fotorealistyczne twarze (ludzkie, anime, produktowe, wąska domena) | StyleGAN3 FFHQ / dostrojenie na własnych danych |
| Edycja twarzy ze zdjęcia | inwersja e4e + wskazówki StyleSpace / InterFaceGAN |
| Zamiana twarzy / rekonstrukcja | StyleGAN + koder + mieszanie |
| Potoki generowania awatarów | StyleGAN3 z ADA do dostrajania na małych zbiorach danych |
| Adaptacja domeny z kilku zdjęć | zamrożenie sieci mapującej, dostrojenie syntezy |
| Generacja multimodalna lub warunkowana tekstem | Nie — należy użyć dyfuzji |

W zastosowaniach produkcyjnych, gdzie odpowiedzią jest „fotografia twarzy", StyleGAN bije dyfuzję pod względem kosztu wnioskowania (jedno przejście w przód, <10 ms na GPU 4090) i ostrości przy tym samym progu jakości.

## Wyślij to

Zapisz `outputs/skill-stylegan-inversion.md`. Umiejętność przyjmuje prawdziwe zdjęcie i generuje cztery elementy: metodę inwersji (e4e / ReStyle / HyperStyle), oczekiwaną stratę w przestrzeni ukrytej, budżet edycji (jak daleko w `W` można się przemieszczać przed pojawieniem się artefaktów) oraz listę sprawdzonych kierunków edycji (wiek, wyraz twarzy, poza).

## Ćwiczenia

1. **Łatwe.** Uruchom `code/main.py` z `adain_on=True` i `adain_on=False`. Porównaj rozkład wyjść dla stałego wektora ukrytego i zaburzonego.
2. **Średnie.** Zastosuj regularyzację mieszania stylów: dla partii treningowej oblicz `w_a` i `w_b`, a następnie użyj `w_a` dla pierwszej połowy sieci syntezy i `w_b` dla drugiej. Sprawdź, czy dekoder uczy się rozplątanych stylów.
3. **Trudne.** Pobierz wstępnie wytrenowany model StyleGAN3 FFHQ (ffhq-1024.pkl). Znajdź kierunek `w` kontrolujący „uśmiech", trenując SVM na oznaczonych próbkach. Zbadaj, jak daleko można przesunąć się w tym kierunku, zanim tożsamość zacznie dryftować.

## Kluczowe terminy

| Termin | Co się mówi | Co to oznacza |
|------|-----------------|----------------------|
| Sieć mapująca | „MLP" | `f: Z → W`, 8 warstw; oddziela geometrię przestrzeni ukrytej od statystyk danych. |
| Przestrzeń W | „przestrzeń stylu" | Wyjście sieci mapującej; w przybliżeniu rozplątana. |
| AdaIN | „adaptacyjna norma instancji" | Normalizacja mapy cech, a następnie skalowanie i przesunięcie według projekcji `w`. |
| Sztuczka z obcięciem | „psi" | `w = mean + ψ·(w - mean)`, ψ<1 zamienia różnorodność na jakość. |
| Regularyzacja długości ścieżki | „regularyzacja PL" | Nakłada karę za duże zmiany obrazu na jednostkę zmiany w `w`; wygładza przestrzeń `W`. |
| Demodulacja wag | „poprawka StyleGAN2" | Normalizowanie wag splotów zamiast aktywacji; eliminuje artefakty kropelkowe. |
| Bez aliasów | „sztuczka StyleGAN3" | Filtry sinc z okienkowaniem; eliminuje przyklejanie się tekstur do siatki pikseli. |
| Inwersja | „znajdź w dla prawdziwego obrazu" | Optymalizacja lub kodowanie `x → w` tak, aby `G(w) ≈ x`. |

## Uwaga produkcyjna: dlaczego StyleGAN nadal będzie stosowany w 2026 r.

StyleGAN3 na GPU 4090 generuje twarz FFHQ o rozdzielczości 1024² w czasie krótszym niż 10 ms — jeden krok, bez dekodowania VAE, bez warstw uwagi. W warunkach produkcyjnych to minimalne możliwe opóźnienie dla dowolnego generatora obrazów. Pięćdziesięciokrokowy potok SDXL + dekodowanie VAE przy tej samej rozdzielczości zajmuje około 3 sekund. Różnica wynosi **300×** i w produktach o wąskiej domenie (serwisy awatarów, potoki dokumentów tożsamości, generowanie grafiki akcji) decyduje o całkowitym koszcie posiadania.

Dwie praktyczne konsekwencje:

- **Brak harmonogramu, brak kolejkowania.** Statyczne partie przy docelowym obciążeniu są optymalne. Dynamiczne grupowanie żądań (niezbędne dla LLM i modeli dyfuzyjnych) nie przynosi tu żadnych korzyści, ponieważ każde żądanie wymaga dokładnie tych samych FLOPów.
- **Obcięcie `ψ` jako regulator jakości.** `ψ < 0.7` pobiera próbki z wąskiego stożka zasięgu sieci mapującej. To jedyna dźwignia, jaką warstwa serwująca ma nad wariancją próbek. Warto obniżać `ψ` przy szczytowym obciążeniu i podnosić dla użytkowników premium.

## Dalsze czytanie

- [Karras i in. (2019). Architektura generatora oparta na stylach dla sieci GAN](https://arxiv.org/abs/1812.04948) — StyleGAN.
- [Karras i in. (2020). Analiza i poprawa jakości obrazu w StyleGAN](https://arxiv.org/abs/1912.04958) — StyleGAN2.
- [Karras i in. (2021). Generatywne sieci przeciwstawne bez aliasów](https://arxiv.org/abs/2106.12423) — StyleGAN3.
- [Tov i in. (2021). Projektowanie kodera do manipulacji obrazami StyleGAN](https://arxiv.org/abs/2102.02766) — inwersja e4e.
- [Sauer i in. (2022). StyleGAN-XL: skalowanie StyleGAN do dużych i zróżnicowanych zbiorów danych](https://arxiv.org/abs/2202.00273) — StyleGAN-XL.
- [Huang i in. (2024). R3GAN: GAN nie działa; niech żyje GAN!](https://arxiv.org/abs/2501.05441) — nowoczesny, minimalistyczny przepis na GAN.
