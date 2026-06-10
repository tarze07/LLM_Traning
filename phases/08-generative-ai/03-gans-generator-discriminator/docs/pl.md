# GANy — Generator vs Dyskryminator

> Trik Goodfellowa w 2014 roku polegał na całkowitym pominięciu gęstości. Dwie sieci. Jedna tworzy fałszywki. Druga je wyłapuje. Walczą, dopóki fałszywki nie stają się nieodróżnialne od rzeczywistości. To nie powinno działać. Często nie działa. Kiedy jednak działa, próbki nadal są najostrzejsze w literaturze dla wąskich dziedzin.

**Typ:** Budowa
**Języki:** Python
**Wymagania:** Faza 3 · 02 (Propagacja wsteczna), Faza 3 · 08 (Optymalizatory), Faza 8 · 02 (VAE)
**Czas:** ~75 minut

## Problem

Modele VAE generują rozmyte próbki, ponieważ ich funkcja straty dekodera (MSE) jest optymalna w sensie Bayesa dla *średniego* obrazu — a średnia z wielu wiarygodnych cyfr to rozmyta cyfra. Potrzebujesz funkcji straty, która nagradza *wiarygodność*, a nie bliskość poszczególnych pikseli do jakiegokolwiek celu. Nie ma zamkniętego wzoru na wiarygodność. Musisz się jej nauczyć.

Pomysł Goodfellowa: wytrenuj klasyfikator `D(x)` do odróżniania prawdziwych obrazów od fałszywych. Wytrenuj generator `G(z)` do oszukiwania `D`. Sygnałem straty dla `G` jest to, co `D` w danej chwili uważa za czynnik sprawiający, że coś wygląda prawdziwie. Sygnał ten aktualizuje się w miarę jak `G` staje się lepszy, goniąc ruchomy cel. Jeśli obie sieci zbiegną się, `G` nauczyło się rozkładu danych bez kiedykolwiek zapisywania `log p(x)`.

To jest uczenie kontradwersaryjne (adversarial training). Matematycznie jest to gra minimaksowa:

```
min_G max_D  E_real[log D(x)] + E_fake[log(1 - D(G(z)))]
```

W 2026 roku GANy nie są już najlepszymi generatorami na świecie (modele dyfuzyjne i flow matching przejęły tę koronę). Jednak StyleGAN 2/3 pozostają najostrzejszymi modelami twarzy, jakie kiedykolwiek wydano, dyskryminatory GAN są używane jako *perceptual losses* w uczeniu dyfuzji, a uczenie kontradwersaryjne napędza szybkie jednoetapowe destylacje (SDXL-Turbo, SD3-Turbo, LCM), które pozwalają dostarczać dyfuzję w czasie rzeczywistym.

## Koncepcja

![Uczenie GAN: generator i dyskryminator w schemacie minimaks](../assets/gan.svg)

**Generator `G(z)`.** Mapuje wektor szumu `z ~ N(0, I)` na próbkę `x̂`. Sieć o kształcie dekodera (gęsta lub z konwolucją transponowaną).

**Dyskryminator `D(x)`.** Mapuje próbkę na skalarne prawdopodobieństwo (lub wynik). Prawdziwe → 1, fałszywe → 0.

**Funkcja straty.** Dwie naprzemienne aktualizacje:

- **Trenuj `D`:** `loss_D = -[ log D(x) + log(1 - D(G(z))) ]`. Binarna entropia krzyżowa (BCE) na prawdziwe=1, fałszywe=0.
- **Trenuj `G`:** `loss_G = -log D(G(z))`. Jest to forma *nienasycająca* (non-saturating), której użył Goodfellow (oryginalne `log(1 - D(G(z)))` nasyca się i zabija gradienty, gdy `D` jest pewny siebie).

**Pętla uczenia.** Jeden krok `D`, jeden krok `G`. Powtarzaj.

**Dlaczego to działa.** Jeśli `G` idealnie dopasuje się do `p_data`, wtedy `D` nie może poradzić sobie lepiej niż przypadek i na wyjściu daje wszędzie 0,5; `G` nie otrzymuje więcej gradientu. Równowaga.

**Dlaczego to się psuje.** Zapaść trybu (mode collapse) (`G` znajduje jeden tryb, którego `D` nie potrafi sklasyfikować i ciągle go produkuje), znikający gradient (`D` uczy się zbyt szybko, a `log D` się nasyca), niestabilność uczenia (wskaźniki uczenia, rozmiary paczek, cokolwiek).

## Warianty, dzięki którym GANy zaczęły działać

| Rok | Innowacja | Poprawka |
|------|------------|-----|
| 2015 | DCGAN | Konwolucja/dekonwolucja, batch norm, LeakyReLU — pierwsza stabilna architektura. |
| 2017 | WGAN, WGAN-GP | Zastąpienie BCE odległością Wassersteina + gradient penalty. Rozwiązuje problem znikającego gradientu. |
| 2017 | Spectral normalization | Ograniczenie Lipschitza dla dyskryminatora. Nadal używane w dyskryminatorach w 2026. |
| 2018 | Progressive GAN | Trenowanie najpierw niskiej rozdzielczości, następnie dodawanie warstw. Pierwsze megapikselowe wyniki. |
| 2019 | StyleGAN / StyleGAN2 | Sieć mapująca + adaptive instance norm. Stan wiedzy w zakresie fotorealizmu w ustalonej dziedzinie. |
| 2021 | StyleGAN3 | Alias-free, translation-equivariant — w 2026 r. to nadal złoty standard dla twarzy. |
| 2022 | StyleGAN-XL | Warunkowe, klasowe, większa skala. |
| 2024 | R3GAN | Rebranding z mocniejszą regularyzacją; działa na 1024² bez trików. |

## Zbuduj to

Plik `code/main.py` trenuje miniaturowego GAN-a na jednowymiarowych danych: mieszaninie dwóch rozkładów Gaussa. Generator i dyskryminator to proste MLP z jedną ukrytą warstwą. Implementujemy przepływ w przód (forward), w tył (backward) oraz pętlę minimaksową ręcznie. Celem jest zaobserwowanie dwóch głównych trybów awarii (mode collapse + vanishing gradient) w trakcie ich występowania.

### Krok 1: nienasycająca funkcja straty

Klasyczna funkcja straty Goodfellowa `log(1 - D(G(z)))` dąży do 0, gdy D klasyfikuje fałszywkę wygenerowaną przez G jako fałszywkę z dużą pewnością. W tym momencie gradient dla G jest w zasadzie zerowy — G nie może się poprawić. Forma nienasycająca `-log D(G(z))` ma przeciwną asymptotę: wybucha, gdy D jest pewny siebie, dając G silny sygnał.

```python
def g_loss(d_fake):
    # maksymalizuj log D(G(z))  <=>  minimalizuj -log D(G(z))
    return -sum(math.log(max(p, 1e-8)) for p in d_fake) / len(d_fake)
```

### Krok 2: jeden krok dyskryminatora na jeden krok generatora

```python
for step in range(steps):
    # trenuj D
    real_batch = sample_real(batch_size)
    fake_batch = [G(z) for z in sample_noise(batch_size)]
    update_D(real_batch, fake_batch)

    # trenuj G
    fake_batch = [G(z) for z in sample_noise(batch_size)]  # świeże fałszywki
    update_G(fake_batch)
```

Świeże fałszywki dla G, w przeciwnym razie gradienty są przestarzałe.

### Krok 3: uważaj na mode collapse

```python
if step % 200 == 0:
    samples = [G(z) for z in sample_noise(500)]
    mode_a = sum(1 for s in samples if s < 0)
    mode_b = 500 - mode_a
    if min(mode_a, mode_b) < 50:
        print("  [!] mode collapse: jeden tryb głoduje")
```

Klasyczny symptom: jeden z dwóch prawdziwych trybów przestaje być generowany. Dyskryminator przestaje go korygować, ponieważ nigdy nie jest postrzegany jako fałszywka.

## Pułapki

- **Dyskryminator zbyt silny.** Zmniejsz wskaźnik uczenia D o 2-5x lub dodaj szum do instancji/warstwy. Jeśli D osiąga >95% skuteczności, G jest martwy.
- **Generator zapamiętuje jeden tryb.** Dodaj szum do wejść D, użyj warstwy minibatch-discriminator lub przełącz na WGAN-GP.
- **Batch norm psujący statystyki.** Przeciekanie statystyk między paczką prawdziwą a fałszywą, gdy przechodzą przez tę samą warstwę BN. Użyj instance norm lub spectral norm zamiast tego.
- **Manipulacja wynikiem Inception-score.** FID i IS są zaszumione przy małej liczbie próbek. Używaj ≥10 tys. próbek podczas ewaluacji.
- **One-shot sampling to kłamstwo w zadaniach warunkowych.** Nadal potrzebujesz skal CFG, sztuczek z obcięciem (truncation) i ponownego próbkowania, aby uzyskać użyteczne wyniki.

## Zastosuj to

Stos technologiczny GAN w 2026:

| Sytuacja | Wybór |
|-----------|------|
| Fotorealistyczne twarze, stała poza | StyleGAN3 (najostrzejszy, najmniejszy) |
| Anime / twarze stylizowane | StyleGAN-XL lub Stable Diffusion LoRA |
| Translacja obraz-na-obraz | Pix2Pix / CycleGAN (Faza 8 · 04) lub ControlNet (Faza 8 · 08) |
| Szybki jednoetapowy text-to-image | Kontradwersaryjna destylacja dyfuzji (SDXL-Turbo, SD3-Turbo) |
| Perceptual loss w procesie trenowania dyfuzji | Mały dyskryminator GAN na wycinkach obrazu |
| Cokolwiek wielomodalnego, o otwartej dziedzinie | Nie używaj — zastosuj dyfuzję lub flow matching |

GAN-y są ostre, ale wąskie. Gdy Twoja dziedzina się otwiera — zdjęcia, dowolne opisy tekstowe (prompty), wideo — przełącz się na modele dyfuzyjne. Uczenie kontradwersaryjne żyje dalej jako komponent (perceptual losses, destylacja), ale nie jako samodzielny generator.

## Wdróż to

Zapisz `outputs/skill-gan-debugger_pl.md`. Umiejętność ta (skill) polega na analizie nieudanego treningu GAN (krzywe strat, siatka próbek, rozmiar zbioru danych) i wyprowadzeniu posortowanej listy prawdopodobnych przyczyn, poprawek w jednej linijce oraz protokołu ponownego uruchomienia.

## Ćwiczenia

1. **Łatwe.** Uruchom `code/main.py` ze standardowymi ustawieniami. Następnie ustaw `D_LR = 5 * G_LR` i uruchom ponownie. Jak szybko strata G zapada się do stałej?
2. **Średnie.** Zastąp funkcję straty BCE Goodfellowa funkcją straty WGAN: `loss_D = E[D(fake)] - E[D(real)]`, `loss_G = -E[D(fake)]` i przytnij wagi D do `[-0.01, 0.01]`. Czy trening jest bardziej stabilny? Porównaj czas zbieżności.
3. **Trudne.** Rozszerz jednowymiarowy przykład do 2-D (mieszanina 8 rozkładów Gaussa na okręgu). Śledź, ile z 8 trybów generator wychwytuje po 1k, 5k, 10k krokach. Zaimplementuj minibatch discrimination i zmierz ponownie.

## Kluczowe pojęcia

| Termin | Jak mówią ludzie | Co to naprawdę znaczy |
|------|-----------------|-----------------------|
| Generator | "G" | Sieć przetwarzająca szum na próbkę, `G: z → x̂`. |
| Dyskryminator | "D" | Klasyfikator `D: x → [0, 1]`, realne vs fałszywe. |
| Minimaks | "Gra" | `min_G max_D` wspólnego celu (joint objective). |
| Non-saturating loss | "Rozwiązanie" | Użycie `-log D(G(z))` dla G zamiast `log(1 - D(G(z)))`. |
| Zapaść trybu (Mode collapse) | "G zapamiętał jedną rzecz" | Generator produkuje niewiele różnych obrazków mimo różnorodnych danych. |
| WGAN | "Wasserstein" | Zastąpienie BCE dystansem Earth-Mover + gradient penalty; gładszy gradient. |
| Spectral norm | "Trik z obszarem Lipschitza" | Ograniczenie normy wag D, by kontrolować jego nachylenie; stabilizuje trening. |
| StyleGAN | "Ten co działa" | Sieć mapująca + AdaIN; najlepsza w swojej klasie do twarzy, nadal w 2026. |

## Notatka produkcyjna: jednoetapowa inferencja (one-shot inference) to trwała przewaga GAN-ów

GAN-y już nie wygrywają pod względem jakości w generowaniu otwartej dziedziny (open-domain), ale nadal wygrywają pod względem kosztów wnioskowania. W słownictwie produkcyjnym dotyczącym inferencji, GAN posiada:

- **Brak etapów prefill, brak dekodowania.** Pojedyncze przejście `G(z)`. Czas pierwszego tokena (TTFT) ≈ całkowite opóźnienie.
- **Brak obciążenia pamięci podręcznej (KV-cache).** Jedynym stanem są wagi. Rozmiar paczki zależy od pamięci na aktywacje, a nie od cache.
- **Trywialne ciągłe grupowanie (continuous batching).** Skoro każde zapytanie zajmuje określoną liczbę FLOPów, statyczna paczka na serwerze zazwyczaj jest optymalna. Żaden scheduler "w locie" nie jest potrzebny.

Dlatego destylacja GAN (SDXL-Turbo, SD3-Turbo, ADD, LCM) jest dominującą techniką dla szybkich modeli text-to-image w 2026 r.: zamienia potok 20-50-krokowy z modelu dyfuzyjnego w 1-4 etapy przypominające GAN z zachowaniem rozkładu z modelu dyfuzyjnego. Kontradwersaryjna funkcja straty przetrwała jako narzędzie podczas trenowania powolnych generatorów, by przekształcić je w szybkie.

## Dalsza lektura

- [Goodfellow et al. (2014). Generative Adversarial Nets](https://arxiv.org/abs/1406.2661) — oryginalna publikacja nt. GAN-ów.
- [Radford et al. (2015). Unsupervised Representation Learning with DCGAN](https://arxiv.org/abs/1511.06434) — pierwsza stabilna architektura.
- [Arjovsky, Chintala, Bottou (2017). Wasserstein GAN](https://arxiv.org/abs/1701.07875) — WGAN.
- [Miyato et al. (2018). Spectral Normalization for GANs](https://arxiv.org/abs/1802.05957) — normalizacja spektralna (SN).
- [Karras et al. (2020). Analyzing and Improving the Image Quality of StyleGAN](https://arxiv.org/abs/1912.04958) — StyleGAN2.
- [Karras et al. (2021). Alias-Free Generative Adversarial Networks](https://arxiv.org/abs/2106.12423) — StyleGAN3.
- [Sauer et al. (2023). Adversarial Diffusion Distillation](https://arxiv.org/abs/2311.17042) — SDXL-Turbo.