# Warunkowe GAN-y & Pix2Pix

> Pierwszym wielkim przełomem z lat 2014–2017 było opanowanie sterowania tym, co generuje GAN. Wystarczy dołączyć etykietę, obraz lub zdanie. Pix2Pix to wyspecjalizowana wersja dla obrazów, która w wąskich zadaniach transformacji obrazów wciąż przewyższa ogólne modele text-to-image.

**Typ:** Budowa
**Języki:** Python
**Wymagania:** Faza 8 · 03 (GAN-y), Faza 4 · 06 (U-Net), Faza 3 · 07 (CNN)
**Czas:** ~75 minut

## Problem

Bezwarunkowy GAN generuje wyłącznie losowe obrazy. Przydaje się do demonstracji, lecz w zastosowaniach produkcyjnych jest bezużyteczny. W praktyce potrzeba czegoś innego: *zamiany szkicu na zdjęcie*, *mapy na fotografię lotniczą*, *sceny dziennej na nocną* czy *pokolorowania czarno-białego zdjęcia*. We wszystkich tych przypadkach dysponujemy obrazem wejściowym `x` i musimy wygenerować obraz `y`, zachowując pewną zgodność semantyczną. Dla danego `x` istnieje wiele wiarygodnych obrazów `y`. Błąd średniokwadratowy (MSE) spłaszcza je w jedną bezkształtną masę. Funkcja straty adversarial tego nie robi, ponieważ wymóg bycia „prawdziwym" wymusza generowanie ostrych kształtów.

Conditional GAN (Mirza i Osindero, 2014) wprowadza do sieci `G` i `D` dodatkowy warunek `c`. Pix2Pix (Isola i in., 2017) to wyspecjalizowana odmiana tego podejścia: warunkiem jest cały obraz wejściowy, generator ma architekturę U-Net, dyskryminator to klasyfikator blokowy (*PatchGAN*), a funkcja straty łączy L1 z klasycznym adversarial loss. Ten przepis daje lepsze wyniki niż modele text-to-image trenowane od zera w wąskich dziedzinach transformacji obraz-na-obraz (nawet w roku 2026), ponieważ jest trenowany na *sparowanych danych* — dysponujemy dokładnie takim sygnałem nadzorczym, jakiego potrzebujemy.

## Koncepcja

![Pix2Pix: Generator U-Net, dyskryminator PatchGAN](../assets/pix2pix.svg)

**Warunkowe G.** `G(x, z) → y`. W Pix2Pix `z` jest realizowane poprzez dropout wewnątrz generatora — na wejściu nie ma jawnego szumu, ponieważ, jak stwierdzili badacze z zespołu Isoli, model i tak go zwykle ignoruje.

**Warunkowe D.** `D(x, y) → [0, 1]`. Na wejściu dyskryminator otrzymuje *parę* (warunek, wynik). To kluczowa różnica: D ocenia, czy wygenerowane `y` jest spójne z `x`, a nie tylko czy `y` wygląda realistycznie samo w sobie.

**Generator U-Net.** Architektura koder-dekoder (encoder-decoder) z połączeniami rezydualnymi (skip connections) omijającymi wąskie gardło sieci. Są one niezbędne w zastosowaniach, gdzie wejście i wyjście dzielą podobną strukturę niskopoziomową (krawędzie, kontury). Bez tych skrótów szczegóły wysokich częstotliwości bezpowrotnie giną.

**Dyskryminator PatchGAN.** D nie zwraca jednej globalnej oceny prawdziwy/fałszywy. Zamiast tego produkuje siatkę wyników `N×N`, gdzie każda komórka klasyfikuje wycinek 70×70 pikseli. Końcowa ocena to średnia po wszystkich komórkach. Model ten traktuje realizm obrazu jako zjawisko lokalne (Markov random field). Jest znacznie szybszy w trenowaniu, ma dużo mniej parametrów i generuje wyraźniejsze obrazy.

**Funkcja straty.**

```
loss_G = -log D(x, G(x)) + λ · ||y - G(x)||_1
loss_D = -log D(x, y) - log (1 - D(x, G(x)))
```

Składnik L1 stabilizuje trening i popycha generator ku celowi. Norma L1 faworyzuje wyraźniejsze krawędzie niż L2 (odpowiednik mediany zamiast średniej). `λ = 100` to domyślna wartość stosowana w oryginalnym Pix2Pix.

## CycleGAN — gdy brakuje sparowanych danych

Pix2Pix wymaga sparowanych danych `(x, y)`. CycleGAN (Zhu i in., 2017) radzi sobie bez nich dzięki rozszerzonej funkcji straty: *cycle consistency loss*. Dwa generatory `G: X → Y` i `F: Y → X` są trenowane tak, by zachodziło `F(G(x)) ≈ x` oraz `G(F(y)) ≈ y`. Pozwala to na transformację krajobrazu z końmi w scenerię z zebrami (albo lata w zimę) bez żadnych powiązanych par danych.

W 2026 roku transformacje na niesparowanych danych opierają się głównie na modelach dyfuzyjnych (np. ControlNet, IP-Adapter), które zepchnęły CycleGAN na drugi plan. Jednak zasada zachowania spójności cyklu pozostaje aktualna w każdym projekcie dotyczącym nowych dziedzin zastosowań uczenia maszynowego.

## Zbuduj to

`code/main.py` implementuje uproszczony warunkowy GAN na jednowymiarowych (1-D) danych. Warunek `c` to klasa obrazu (np. 0 lub 1). Zadanie polega na wygenerowaniu próbki z właściwego rozkładu dla podanej etykiety klasy.

### Krok 1: przekazanie warunku jako wejścia G i D

```python
def G(z, c, params):
    return mlp(concat([z, one_hot(c)]), params)

def D(x, c, params):
    return mlp(concat([x, one_hot(c)]), params)
```

One-hot encoding to najprostszy sposób na wprowadzenie etykiety. Bardziej rozbudowane sieci stosują wyuczone reprezentacje wektorowe (learned embeddings), modulację FiLM lub mechanizm cross-attention.

### Krok 2: trenowanie na wejściu warunkowym

```python
for step in range(steps):
    x, c = sample_real_conditional()
    noise = sample_noise()
    update_D(x_real=x, x_fake=G(noise, c), c=c)
    update_G(noise, c)
```

Dzięki temu generator uczy się lokalnej zależności dla każdego warunku `c`, a nie uśrednionego rozkładu brzegowego.

### Krok 3: weryfikacja wyników dla poszczególnych klas

```python
for c in [0, 1]:
    samples = [G(noise, c) for noise in batch]
    mean_c = mean(samples)
    assert_near(mean_c, real_mean_for_class_c)
```

## Pułapki

- **Generator ignoruje warunek.** G minimalizuje straty brzegowe, a D nie penalizuje braku zgodności z warunkiem, bo sygnał nie jest właściwie powiązany. Rozwiązanie: sprawić, by D reagował silniej na warunek we wczesnych warstwach sieci zamiast tylko na końcu architektury; zastosować projection discriminator (Miyato i Koyama, 2018).
- **Zbyt mała waga normy L1.** Generator ucieka w losowe krawędzie wizualnie przypominające realne obrazy, lecz niepodobne do oryginału. Dla Pix2Pix należy startować z λ≈100.
- **Zbyt duża waga normy L1.** Generator produkuje rozmyte wyjścia, bo wysoka wartość L1 wygładza gradienty. Należy stopniowo zmniejszać tę wagę — dopiero gdy model wyrobi sobie konkretne cechy wizualne.
- **Podawanie rzeczywistych próbek jako wejścia do D bez warunku.** Częsty błąd implementacyjny: łączenie `(x, y)` jako wejść do D zamiast podawania pary (warunek, wynik). Dyskryminator musi widzieć obydwa elementy pary, żeby oceniać ich wzajemną zgodność.
- **Kolaps trybów per klasa.** Każda etykieta może niezależnie prowadzić do zapaści trybu generatora. Należy regularnie sprawdzać rozkłady wyjść dla każdej klasy.

## Zastosuj to

Zestawienie rekomendowanych podejść do zadań image-to-image w roku 2026:

| Zadanie | Zalecane podejście |
|------|---------------|
| Szkic → fotografia, sparowane dane | Pix2Pix / Pix2PixHD (szybkie wnioskowanie, ostre wyjścia) |
| Szkic → fotografia, dane niesparowane | ControlNet w trybie „Scribble" jako moduł pomocniczy dyfuzji |
| Mapa semantyczna → fotografia | SPADE / GauGAN2 lub Stable Diffusion z wejściem image-to-image |
| Przeniesienie stylu artysty | Dyfuzja z IP-Adapter lub LoRA; podejścia oparte na GAN są już rozwiązaniem przestarzałym |
| Mapa głębi → fotografia | ControlNet-Depth ze standardowym potokiem dyfuzyjnym |
| Super-rozdzielczość | Real-ESRGAN, ESRGAN-Plus lub tryb upscale w Stable Diffusion |
| Kolorowanie zdjęć czarno-białych | ColTran (Google) lub Pix2Pix-color |
| Transformacja sceny (dzień/noc, lato/zima) | CycleGAN lub ControlNet na bazie Stable Diffusion |

Pix2Pix sprawdza się najlepiej, gdy: (a) dysponujesz setkami lub tysiącami sparowanych par treningowych, (b) zadanie jest wąsko zdefiniowane — bez ogólnych promptów tekstowych, za to z wyraźną, powtarzalną specyfikacją wejścia i wyjścia. Gdy dziedzina jest otwarta lub brakuje sparowanych danych, modele dyfuzyjne okazują się lepszym wyborem ze względu na elastyczność i szerokie możliwości generalizacji.

## Wdróż to

Zapisz wynik do pliku `outputs/skill-img2img-chooser_pl.md`. Dokument powinien zawierać: opis zadania transformacji (co chcesz zamienić), specyfikację dostępnych danych (sparowane pary lub niezależne zbiory), rekomendowane podejście implementacyjne z Pix2Pix lub CycleGAN, opis potoku dyfuzyjnego (np. SDXL + IP-Adapter), wymagania dotyczące danych treningowych, metryki oceny jakości (FID) oraz sposób pomiaru opóźnienia przy wdrożeniu produkcyjnym.

## Ćwiczenia

1. **Poziom podstawowy.** W pliku `code/main.py` dodaj trzecią klasę do wektora wejściowego. Upewnij się, że generator poprawnie uczy się odrębnego rozkładu dla nowej etykiety.
2. **Poziom średni.** Zastąp stratę L1 stratą percepcyjną (perceptual loss) opartą na cechach sieci pretrenowanej. Sprawdź, czy zmiana wpływa na ostrość wyjść dyskryminatora. Możesz użyć zamrożonej sieci pomocniczej po stronie warunkowania.
3. **Poziom zaawansowany.** Zaimplementuj uproszczony CycleGAN na danych 1-D: dwa rozkłady A i B, dwa generatory i cykl strat (cycle consistency loss). Sprawdź, czy model potrafi nauczyć się mapowania między rozkładami bez sparowanych danych.

## Kluczowe słownictwo

| Termin | Definicja | Znaczenie |
|------|-----------------|-----------------------|
| Conditional GAN | GAN z dodatkowym sygnałem warunkującym | Obie sieci — G i D — widzą ten sam warunek `c`: `G(z, c)`, `D(x, c)`. |
| Pix2Pix | Warunkowy GAN do transformacji obraz-na-obraz | Trenowany na sparowanych parach; łączy U-Net z dyskryminatorem PatchGAN. |
| U-Net | Architektura koder-dekoder z połączeniami rezydualnymi | Umożliwia zachowanie szczegółów wysokich częstotliwości między wejściem a wyjściem. |
| PatchGAN | Dyskryminator oceniający lokalne wycinki obrazu | Klasyfikuje niezależnie każdy fragment zamiast całego obrazu; szybszy i bardziej szczegółowy. |
| CycleGAN | GAN do transformacji dziedzin bez sparowanych danych | Wykorzystuje cycle consistency loss: `F(G(x)) ≈ x` oraz `G(F(y)) ≈ y`. |
| SPADE | Warunkowa normalizacja przestrzenna (GauGAN) | Moduluje aktywacje na podstawie mapy segmentacji; stosowana w zadaniach segmentacja → fotografia. |
| FiLM | Feature-wise Linear Modulation | Tanie i efektywne warunkowanie przez przesunięcie i skalowanie cech wektorowych. |

## Pix2Pix w zastosowaniach produkcyjnych — latencja

Przy wąsko zdefiniowanych zadaniach image-to-image z dostępnymi sparowanymi danymi potok oparty na Pix2Pix jest zazwyczaj szybszy od rozwiązań dyfuzyjnych. Poniżej porównanie przybliżonych opóźnień dla karty Nvidia L4, obraz 512×512:

| Podejście | Liczba kroków | Przybliżone opóźnienie |
|------|-------|----------------------------------------|
| Pix2Pix (jedno przejście w przód) | 1 | ~30 ms |
| Stable Diffusion 1.x / 2.x (img2img) | ~20 | ~1,2 s |
| SDXL-Turbo (img2img) | 1–4 | ~0,15–0,35 s |
| ControlNet + SDXL | ~20–30 | ~3–5 s |

Pix2Pix jest wydajniejszy w zastosowaniach wymagających niskiego opóźnienia i stałej specyfikacji wejścia. Modele dyfuzyjne oferują większą elastyczność i lepszą jakość w otwartych dziedzinach, kosztem dłuższego czasu wnioskowania. W architekturach produkcyjnych Pix2Pix często pełni rolę szybkiej ścieżki, podczas gdy model dyfuzyjny służy jako awaryjne rozwiązanie dla przypadków brzegowych.

## Literatura

- [Mirza i Osindero, „Conditional Generative Adversarial Nets"](https://arxiv.org/abs/1411.1784) — artykuł źródłowy wprowadzający warunkowe GAN-y.
- [Isola i in., „Image-to-Image Translation with Conditional Adversarial Networks"](https://arxiv.org/abs/1611.07004) — oryginalna praca opisująca Pix2Pix.
- [Zhu i in., „Unpaired Image-to-Image Translation using Cycle-Consistent Adversarial Networks"](https://arxiv.org/abs/1703.10593) — artykuł opisujący CycleGAN.
- [Wang i in., „High-Resolution Image Synthesis and Semantic Manipulation with Conditional GANs"](https://arxiv.org/abs/1711.11585) — Pix2PixHD: rozszerzenie do wysokiej rozdzielczości.
- [Park i in., „Semantic Image Synthesis with Spatially-Adaptive Normalization"](https://arxiv.org/abs/1903.07291) — praca opisująca SPADE i GauGAN (Nvidia).
- [Miyato i Koyama, „cGANs with Projection Discriminator"](https://arxiv.org/abs/1802.05637) — projection discriminator dla warunkowych GAN-ów.
