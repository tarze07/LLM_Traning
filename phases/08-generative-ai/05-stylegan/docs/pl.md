#StylGAN

> Większość generatorów miesza `z` w każdej warstwie jednocześnie. StyleGAN rozdzielił to na części: najpierw zmapuj `z` na pośredni `w`, a następnie *inject* `w` na każdym poziomie rozdzielczości za pośrednictwem AdaIN. Ta pojedyncza zmiana rozplątała ukrytą przestrzeń i sprawiła, że ​​fotorealistyczne twarze stały się problemem rozwiązanym na siedem lat z rzędu.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 8 · 03 (GAN), Faza 4 · 08 (Normalizacja), Faza 3 · 07 (CNN)
**Czas:** ~45 minut

## Problem

DCGAN odwzorowuje `z` na obraz poprzez stos transponowanych splotów. Problem: `z` kontroluje wszystko – pozę, oświetlenie, tożsamość, tło – splecione ze sobą. Poruszaj się wzdłuż jednej osi `z`, wszystkie cztery zmieniają się. Nie można zadać modelowi pytania „ta sama osoba, inna poza”, ponieważ przedstawienie nie uwzględnia tego.

Karras i in. (2019, NVIDIA) zaproponował: zaprzestań podawania `z` bezpośrednio do warstw konw. Podaj stały tensor `4×4×512` jako wejście sieciowe. Poznaj 8-warstwowy system MLP, który odwzorowuje `z ∈ Z → w ∈ W`. Wstrzyknij `w` w każdej rozdzielczości poprzez *adaptacyjną normalizację instancji* (AdaIN): normalizuj każdą mapę funkcji konwersji, następnie skaluj i przesuwaj według projekcji afinicznych `w`. Dodaj szum dla poszczególnych warstw, aby uzyskać szczegóły stochastyczne (pory skóry, pasma włosów).

Wynik: `W` ma w przybliżeniu ortogonalne osie dla „stylu wysokiego poziomu” (poza, tożsamość) i „stylu doskonałego” (oświetlenie, kolor). Możesz zamieniać style między dwoma obrazami, używając `w` obrazu A dla poziomów o niskiej rozdzielczości i `w` obrazu B dla wysokich. To odblokowało edycję, stylizację między domenami i całą linię badań „Inwersja StyleGAN”.

## Koncepcja

![StyleGAN: mapowanie sieci + AdaIN + szum na warstwę](../assets/stylegan.svg)

**Mapowanie sieci.** `f: Z → W`, 8-warstwowy system MLP. `Z = N(0, I)^512`. `W` nie musi być gaussowski — uczy się kształtu dostosowanego do danych.

**Sieć syntezy.** Rozpoczyna się od wyuczonej stałej `4×4×512`. Każdy blok rozdzielczości: `upsample → conv → AdaIN(w_i) → noise → conv → AdaIN(w_i) → noise`. Podwójne rozdzielczości: 4, 8, 16, 32, 64, 128, 256, 512, 1024.

**AdaIN.**

```
AdaIN(x, y) = y_scale · (x - mean(x)) / std(x) + y_bias
```

gdzie `y_scale` i `y_bias` pochodzą z projekcji afinicznych `w`. Normalizuj według mapy obiektów, a następnie zmień styl. „Styl” oznacza tutaj statystyki pierwszego i drugiego rzędu mapy obiektów.

**Szum na warstwę.** Jednokanałowy szum Gaussa dodany do każdej mapy obiektów, skalowany według wyuczonego współczynnika na kanał. Kontroluje szczegóły stochastyczne bez wpływu na strukturę globalną.

**Sztuczka z obcięciem.** Podczas wnioskowania spróbuj `z`, oblicz `w = mapping(z)`, a następnie `w' = ŵ + ψ·(w - ŵ)` gdzie `ŵ` to średnia `w` na wielu próbkach. `ψ < 1` zamienia różnorodność na jakość. Prawie każde demo StyleGAN wykorzystuje `ψ ≈ 0.7`.

## StylGAN 1 → 2 → 3

| Wersja | Rok | Innowacja |
|--------|------|------------|
| StylGAN | 2019 | Sieć mapująca + AdaIN + szum + postępujący rozwój. |
| StylGAN2 | 2020 | Demodulacja wagi zastępuje AdaIN (naprawia artefakty związane z kropelkami); architektura pomijana/resztkowa; regularyzacja długości ścieżki. |
| StylGAN3 | 2021 | Splot wolny od aliasów + jądra równoważne; eliminuje przyklejanie się tekstur do siatki pikseli. |
| StylGAN-XL | 2022 | Warunkowe klasowo, 1024², ImageNet. |
| R3GAN | 2024 | Rebranding z mocniejszą rej.; zamyka lukę w dyfuzji na FFHQ-1024 z 20 razy mniejszą liczbą parametrów. |

W roku 2026 StyleGAN3 pozostaje domyślnym rozwiązaniem dla (a) fotorealizmu w wąskich domenach przy dużej liczbie klatek na sekundę, (b) kilkukrotnej adaptacji domeny (trening na nowym zestawie danych zawierającym 100 obrazów, zamrożenie mapowania), (c) edycji opartej na inwersji (znajdź `w`, który rekonstruuje prawdziwe zdjęcie, a następnie edytuj je `w`). W przypadku zamiany tekstu na obraz w domenie otwartej nie jest to narzędzie — jest nim dyfuzja.

## Zbuduj to

`code/main.py` implementuje zabawkę „style-GAN lite” w 1-D: mapowanie MLP, funkcję syntezy, która pobiera wyuczony wektor stały i moduluje go za pomocą `w`-pochodnej skali/odchylenia i szumu na warstwę. Pokazuje, że wstrzykiwanie `w` poprzez modulację afiniczną pasuje lub dudni, łącząc `z` na wejście generatora.

### Krok 1: mapowanie sieci

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

Skala i błąd mapy dla poszczególnych obiektów pochodzą z `w` poprzez projekcję liniową.

### Krok 3: szum na poziomie warstwy

```python
def add_noise(x, sigma, rng):
    return [xi + sigma * rng.gauss(0, 1) for xi in x]
```

Można się nauczyć obsługi Sigma na kanał.

## Pułapki

- **Artefakty kropelkowe.** StyleGAN 1 wytworzył plamkowatą kropelkę na mapach obiektów, ponieważ AdaIN wyzerował średnią. Demodulacja wagi StyleGAN 2 rozwiązuje ten problem, zamiast tego skalując wagi splotu.
- **Przyklejanie tekstur.** Tekstury StyleGAN 1 i 2 podążały za współrzędnymi pikseli, a nie współrzędnymi obiektu (widocznymi podczas interpolacji). Pozbawione aliasów sploty StyleGAN 3 rozwiązują ten problem za pomocą okienkowych filtrów sinc.
- **Pokrycie trybu.** Obcięcie `ψ < 0.7` wygląda na czyste, ale próbki pochodzą z wąskiego stożka; użyj `ψ = 1.0`, jeśli potrzebujesz różnorodności.
- **Inwersja jest stratna.** Odwracanie prawdziwego zdjęcia do `W` zwykle odbywa się poprzez optymalizację lub koder (e4e, ReStyle, HyperStyle). Wyniki dryfują w ciągu wielu iteracji.

## Użyj tego

| Przypadek użycia | Podejście |
|---------|----------|
| Fotorealistyczne twarze ludzkie (anime, produkt, wąskie) | StyleGAN3 FFHQ / niestandardowe dostrojenie |
| Edycja twarzy ze zdjęcia | inwersja e4e + wskazówki StyleSpace / InterFaceGAN |
| Zamiana twarzy / rekonstrukcja | StyleGAN + koder + mieszanie |
| Rurociągi Avatara | StyleGAN3 z ADA do dostrajania małej ilości danych |
| Adaptacja domeny z kilku zdjęć | Zamrożenie sieci mapowania, dostrojenie syntezy |
| Generacja multimodalna lub uwarunkowana tekstowo | Nie — używaj dyfuzji |

W przypadku demonstracji produktów, gdzie odpowiedzią jest „zdjęcie twarzy osoby”, StyleGAN pokonuje dyfuzję pod względem kosztów wnioskowania (pojedyncze przejście w przód, <10 ms na 4090) i ostrości przy tym samym pasku jakości.

## Wyślij to

Zapisz `outputs/skill-stylegan-inversion.md`. Umiejętność wykonuje prawdziwe zdjęcie i generuje następujące wyniki: metoda inwersji (e4e / ReStyle / HyperStyle), oczekiwana ukryta strata, budżet edycji (jak daleko w `W` można się poruszać przed artefaktami) oraz listę znanych i dobrych kierunków edycji (wiek, wyraz twarzy, poza).

## Ćwiczenia

1. **Łatwe.** Uruchom `code/main.py` z `adain_on=True` i `adain_on=False`. Porównaj rozkład wyników dla stałego utajonego i zaburzonego utajonego.
2. **Średni.** Zastosuj regularyzację mieszania: dla partii szkoleniowej oblicz `w_a`, `w_b` i zastosuj `w_a` dla pierwszej połowy syntezy i `w_b` dla drugiej połowy. Czy dekoder uczy się rozplątanych stylów?
3. **Trudne.** Weź wstępnie wytrenowany model StyleGAN3 FFHQ (ffhq-1024.pkl). Znajdź kierunek `w` kontrolujący „uśmiech”, ucząc SVM na oznakowanych próbkach; zgłoś, jak daleko możesz się posunąć, zanim tożsamość ulegnie dryfowi.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Mapowanie sieci | „MLP” | `f: Z → W`, 8 warstw, oddziela ukrytą geometrię od statystyk danych. |
| W spacja | „Przestrzeń stylu” | Wyjście sieci mapującej; mniej więcej rozplątany. |
| AdaIN | „Norma instancji adaptacyjnej” | Normalizuj mapę obiektów, a następnie skaluj + przesunięcie o `w`-projekcję. |
| Sztuczka z obcięciem | „Psi” | `w = mean + ψ·(w - mean)`, ψ<1 zamienia różnorodność na jakość. |
| Regularyzacja długości ścieżki | "Rej. PL" | Nakłada karę za duże zmiany obrazu na jednostkę zmiany w `w`; sprawia, że ​​`W` jest płynniejszy. |
| Demodulacja wagi | „Poprawka StyleGAN2” | Normalizuj wagi konw. zamiast aktywacji; zabija artefakty kropelkowe. |
| Bez aliasów | „Sztuczka StyleGAN3” | Okienkowe filtry sinc; eliminuje przyklejanie się tekstur do siatki pikseli. |
| Inwersja | „Znajdź w dla prawdziwego obrazu” | Zoptymalizuj lub zakoduj `x → w` tak, aby `G(w) ≈ x`. |

## Uwaga produkcyjna: dlaczego StyleGAN nadal będzie dostarczany w 2026 r

StyleGAN3 na 4090 generuje twarz FFHQ o powierzchni 1024² w czasie krótszym niż 10 ms — `num_steps = 1`, bez dekodowania VAE, bez przejścia uwagi. W kategoriach produkcyjnych jest to minimalne opóźnienie dla dowolnego generatora obrazu. 50-stopniowy potok dekodowania SDXL + VAE przy tej samej rozdzielczości wynosi ~ 3 sekundy. Jest to **luka 300×**, a w przypadku produktów o wąskiej domenie (usługi awatarów, potoki dokumentów tożsamości, generowanie akcji) wygrywa ona pod względem całkowitego kosztu posiadania.

Dwie konsekwencje operacyjne:

- **Brak harmonogramu, brak dozownika.** Partia statyczna przy docelowym obłożeniu jest optymalna. Ciągłe przetwarzanie wsadowe (niezbędne w przypadku LLM i dyfuzji) zapewnia zerowe korzyści, ponieważ każde żądanie wymaga tych samych FLOPów.
- **Obcięcie `ψ` to pokrętło zabezpieczające.** `ψ < 0.7` próbki z wąskiego stożka zasięgu sieci mapującej. Jest to jedyna dźwignia, jaką warstwa obsługująca ma ponad wariancję próbki. Obniż `ψ` przy obciążeniu szczytowym, zwiększ dla użytkowników premium.

## Dalsze czytanie

- [Karras i in. (2019). Architektura generatora oparta na stylach dla sieci GAN](https://arxiv.org/abs/1812.04948) — StyleGAN.
- [Karras i in. (2020). Analizowanie i poprawianie jakości obrazu StyleGAN](https://arxiv.org/abs/1912.04958) — StyleGAN2.
- [Karras i in. (2021). Generacyjne sieci kontrawersyjne bez aliasów](https://arxiv.org/abs/2106.12423) — StyleGAN3.
- [Tov i in. (2021). Projektowanie kodera do manipulacji obrazem StyleGAN](https://arxiv.org/abs/2102.02766) — inwersja e4e.
- [Sauer i in. (2022). StyleGAN-XL: Skalowanie StyleGAN do dużych, różnorodnych zbiorów danych](https://arxiv.org/abs/2202.00273) — StyleGAN-XL.
- [Huang i in. (2024). R3GAN: GAN nie działa; niech żyje GAN!](https://arxiv.org/abs/2501.05441) — nowoczesny, minimalny przepis na GAN.