# GANy — Generator vs Dyskryminator

> Pomysł Goodfellowa z 2014 roku polegał na całkowitym pominięciu gęstości prawdopodobieństwa. Dwie sieci. Jedna tworzy fałszywki. Druga je wyłapuje. Rywalizują ze sobą, dopóki fałszywki nie stają się nieodróżnialne od oryginałów. Teoretycznie nie powinno to działać — i często rzeczywiście nie działa. Kiedy jednak się sprawdza, jakość generowanych próbek pozostaje najwyższa w literaturze dla wąskich dziedzin.

**Typ:** Budowa
**Języki:** Python
**Wymagania:** Faza 3 · 02 (Propagacja wsteczna), Faza 3 · 08 (Optymalizatory), Faza 8 · 02 (VAE)
**Czas:** ~75 minut

## Problem

Modele VAE generują rozmyte próbki, ponieważ ich funkcja straty dekodera (MSE) jest optymalna w sensie Bayesa dla *średniego* obrazu — a uśrednienie wielu wiarygodnych cyfr daje rozmytą cyfrę. Potrzebna jest funkcja straty nagradzająca *wiarygodność*, a nie pikselową bliskość do wzorca. Nie istnieje zamknięty wzór na wiarygodność. Trzeba się jej nauczyć.

Rozwiązanie Goodfellowa: wytrenuj klasyfikator `D(x)` do odróżniania prawdziwych obrazów od fałszywych, a generator `G(z)` — do oszukiwania `D`. Sygnał straty dla `G` wyraża to, co `D` w danej chwili uznaje za cechy świadczące o autentyczności. Sygnał ten ewoluuje wraz z poprawą `G`, który goni ruchomy cel. Jeśli obie sieci osiągną zbieżność, `G` opanuje rozkład danych bez konieczności jawnego wyznaczania `log p(x)`.

To jest uczenie kontradwersaryjne (adversarial training). Matematycznie stanowi grę minimaksową:

```
min_G max_D  E_real[log D(x)] + E_fake[log(1 - D(G(z)))]
```

W 2026 roku GANy nie są już czołowymi generatorami (modele dyfuzyjne i flow matching przejęły tę pozycję). Mimo to StyleGAN 2/3 pozostają najostrzejszymi modelami syntezy twarzy, jakie kiedykolwiek opublikowano. Dyskryminatory GAN służą jako *perceptual losses* podczas trenowania modeli dyfuzyjnych, a uczenie kontradwersaryjne napędza szybką destylację jednoetapową (SDXL-Turbo, SD3-Turbo, LCM), umożliwiającą generowanie obrazów w czasie rzeczywistym.

## Koncepcja

![Uczenie GAN: generator i dyskryminator w schemacie minimaks](../assets/gan.svg)

**Generator `G(z)`.** Przekształca wektor szumu `z ~ N(0, I)` w próbkę `x̂`. Ma architekturę dekodera — gęstą lub opartą na konwolucji transponowanej.

**Dyskryminator `D(x)`.** Przypisuje próbce skalarną wartość prawdopodobieństwa (lub wynik). Prawdziwe → 1, fałszywe → 0.

**Funkcja straty.** Dwie naprzemienne aktualizacje:

- **Trenuj `D`:** `loss_D = -[ log D(x) + log(1 - D(G(z))) ]`. Binarna entropia krzyżowa (BCE): prawdziwe=1, fałszywe=0.
- **Trenuj `G`:** `loss_G = -log D(G(z))`. To forma *nienasycająca* (non-saturating) zastosowana przez Goodfellowa — oryginalne `log(1 - D(G(z)))` nasyca się i niszczy gradienty, gdy `D` jest zbyt pewny swojej oceny.

**Pętla uczenia.** Jeden krok `D`, jeden krok `G`. Powtarzaj.

**Dlaczego to działa.** Gdy `G` idealnie odwzoruje `p_data`, `D` nie poradzi sobie lepiej niż losowe zgadywanie i wszędzie zwróci 0,5 — `G` przestanie otrzymywać gradient. Układ osiąga równowagę.

**Dlaczego to się psuje.** Zapaść trybu (mode collapse) — `G` odkrywa jeden tryb, którego `D` nie potrafi sklasyfikować, i produkuje go bez przerwy. Znikający gradient — `D` uczy się zbyt szybko, a `log D` się nasyca. Niestabilność uczenia — wynikająca z doboru wskaźników uczenia, rozmiarów paczek i innych czynników.

## Warianty, dzięki którym GANy zaczęły działać

| Rok | Innowacja | Poprawka |
|------|------------|-----|
| 2015 | DCGAN | Konwolucja/dekonwolucja, batch norm, LeakyReLU — pierwsza stabilna architektura. |
| 2017 | WGAN, WGAN-GP | Zastąpienie BCE odległością Wassersteina z gradient penalty. Rozwiązuje problem znikającego gradientu. |
| 2017 | Spectral normalization | Ograniczenie Lipschitza dla dyskryminatora. Stosowane w dyskryminatorach również w 2026. |
| 2018 | Progressive GAN | Trenowanie od niskiej rozdzielczości z sukcesywnym dodawaniem warstw. Pierwsze wyniki w skali megapiksela. |
| 2019 | StyleGAN / StyleGAN2 | Sieć mapująca + adaptive instance norm. Najlepsza jakość fotorealizmu w ustalonej dziedzinie. |
| 2021 | StyleGAN3 | Alias-free, translation-equivariant — w 2026 r. nadal złoty standard dla twarzy. |
| 2022 | StyleGAN-XL | Warunkowy, klasowy, większa skala. |
| 2024 | R3GAN | Mocniejsza regularyzacja; działa na rozdzielczości 1024² bez dodatkowych sztuczek. |

## Zbuduj to

Plik `code/main.py` trenuje miniaturowego GAN-a na jednowymiarowych danych: mieszaninie dwóch rozkładów Gaussa. Generator i dyskryminator to proste sieci MLP z jedną ukrytą warstwą. Propagację w przód, propagację wsteczną oraz pętlę minimaksową implementujemy ręcznie. Celem jest zaobserwowanie dwóch głównych rodzajów awarii — mode collapse i vanishing gradient — w trakcie ich występowania.

### Krok 1: nienasycająca funkcja straty

Klasyczna funkcja straty Goodfellowa `log(1 - D(G(z)))` zmierza do zera, gdy D z dużą pewnością klasyfikuje wygenerowaną przez G próbkę jako fałszywą. Gradient dla G staje się wówczas praktycznie zerowy — G nie może się poprawić. Forma nienasycająca `-log D(G(z))` ma przeciwną asymptotę: rośnie, gdy D jest zbyt pewny siebie, dostarczając G silny sygnał uczący.

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

Świeże fałszywki dla G są niezbędne — w przeciwnym razie gradienty będą przestarzałe.

### Krok 3: uważaj na mode collapse

```python
if step % 200 == 0:
    samples = [G(z) for z in sample_noise(500)]
    mode_a = sum(1 for s in samples if s < 0)
    mode_b = 500 - mode_a
    if min(mode_a, mode_b) < 50:
        print("  [!] mode collapse: jeden tryb głoduje")
```

Charakterystyczny objaw: generator przestaje produkować próbki dla jednego z dwóch prawdziwych trybów. Dyskryminator nie koryguje tego zachowania, bo nigdy nie napotyka tych próbek jako fałszywek.

## Pułapki

- **Dyskryminator zbyt silny.** Zmniejsz wskaźnik uczenia D dwu- lub pięciokrotnie albo dodaj szum do wejść lub warstw. Gdy D osiąga skuteczność powyżej 95%, G przestaje się uczyć.
- **Generator zapada się w jeden tryb.** Dodaj szum do wejść D, zastosuj warstwę minibatch-discriminator lub przejdź na WGAN-GP.
- **Batch norm zaburza statystyki.** Gdy prawdziwe i fałszywe próbki przechodzą przez tę samą warstwę BN, statystyki się mieszają. Stosuj instance norm lub spectral norm.
- **Manipulacja wynikiem Inception-score.** FID i IS są zaszumione przy małej liczbie próbek. Do ewaluacji używaj co najmniej 10 tys. próbek.
- **One-shot sampling zawodzi w zadaniach warunkowych.** Nadal potrzebne są skalowanie CFG, obcinanie (truncation) i ponowne próbkowanie, aby uzyskać użyteczne wyniki.

## Zastosuj to

Stos technologiczny GAN w 2026:

| Sytuacja | Wybór |
|-----------|------|
| Fotorealistyczne twarze, ustalona poza | StyleGAN3 (najostrzejszy, najmniejszy) |
| Anime / twarze stylizowane | StyleGAN-XL lub Stable Diffusion LoRA |
| Translacja obraz-na-obraz | Pix2Pix / CycleGAN (Faza 8 · 04) lub ControlNet (Faza 8 · 08) |
| Szybki jednoetapowy text-to-image | Kontradwersaryjna destylacja dyfuzji (SDXL-Turbo, SD3-Turbo) |
| Perceptual loss podczas trenowania dyfuzji | Mały dyskryminator GAN na wycinkach obrazu |
| Zastosowania wielomodalne i otwarta dziedzina | Nie stosuj — użyj dyfuzji lub flow matching |

GANy są precyzyjne, lecz wąsko wyspecjalizowane. Gdy dziedzina się rozszerza — ogólne fotografie, dowolne opisy tekstowe, wideo — należy przejść na modele dyfuzyjne. Uczenie kontradwersaryjne zachowuje wartość jako komponent (perceptual losses, destylacja), nie jako samodzielny generator.

## Wdróż to

Zapisz `outputs/skill-gan-debugger_pl.md`. Celem jest opanowanie umiejętności analizy nieudanego treningu GAN — na podstawie krzywych strat, siatki próbek i rozmiaru zbioru danych — oraz tworzenia posortowanej listy prawdopodobnych przyczyn, jednoliniowych poprawek i protokołu ponownego uruchomienia.

## Ćwiczenia

1. **Łatwe.** Uruchom `code/main.py` ze standardowymi ustawieniami. Następnie ustaw `D_LR = 5 * G_LR` i uruchom ponownie. Jak szybko strata G spada do stałej wartości?
2. **Średnie.** Zastąp funkcję straty BCE Goodfellowa funkcją straty WGAN: `loss_D = E[D(fake)] - E[D(real)]`, `loss_G = -E[D(fake)]` i przytnij wagi D do zakresu `[-0.01, 0.01]`. Czy trening jest bardziej stabilny? Porównaj czas zbieżności.
3. **Trudne.** Rozszerz jednowymiarowy przykład do dwóch wymiarów (mieszanina 8 rozkładów Gaussa na okręgu). Śledź, ile z 8 trybów generator wychwytuje po 1k, 5k i 10k krokach. Zaimplementuj minibatch discrimination i przeprowadź pomiary ponownie.

## Kluczowe pojęcia

| Termin | Jak mówią ludzie | Co to naprawdę znaczy |
|------|-----------------|-----------------------|
| Generator | "G" | Sieć przekształcająca szum w próbkę: `G: z → x̂`. |
| Dyskryminator | "D" | Klasyfikator `D: x → [0, 1]`, prawdziwe vs fałszywe. |
| Minimaks | "Gra" | `min_G max_D` wspólnego celu (joint objective). |
| Non-saturating loss | "Rozwiązanie" | Stosowanie `-log D(G(z))` dla G zamiast `log(1 - D(G(z)))`. |
| Zapaść trybu (Mode collapse) | "G zapamiętał jedną rzecz" | Generator produkuje mało zróżnicowane próbki mimo bogatych danych treningowych. |
| WGAN | "Wasserstein" | Zamiana BCE dystansem Earth-Mover z gradient penalty; daje łagodniejszy gradient. |
| Spectral norm | "Trik z obszarem Lipschitza" | Ograniczenie normy wag D w celu kontrolowania nachylenia; stabilizuje trening. |
| StyleGAN | "Ten co działa" | Sieć mapująca + AdaIN; najlepsza w swojej klasie do twarzy, również w 2026. |

## Notatka produkcyjna: jednoetapowa inferencja (one-shot inference) jako trwała przewaga GANów

GANy nie dominują już pod względem jakości w generowaniu z otwartej dziedziny, lecz wciąż wygrywają pod kątem kosztów inferencji. W kontekście wdrożeń produkcyjnych GAN oferuje:

- **Brak etapów prefill, brak dekodowania.** Pojedyncze przejście `G(z)`. Czas pierwszego tokena (TTFT) jest praktycznie równy całkowitemu opóźnieniu.
- **Brak narzutu pamięci podręcznej (KV-cache).** Jedynym stanem są wagi modelu. Rozmiar paczki zależy od pamięci potrzebnej na aktywacje, nie od rozmiaru cache.
- **Proste ciągłe grupowanie (continuous batching).** Ponieważ każde zapytanie wymaga stałej liczby operacji zmiennoprzecinkowych (FLOPs), statyczna paczka na serwerze jest zazwyczaj optymalnym rozwiązaniem. Dynamiczny scheduler nie jest potrzebny.

Dlatego destylacja GAN (SDXL-Turbo, SD3-Turbo, ADD, LCM) stała się dominującą techniką szybkich modeli text-to-image w 2026 r.: przekształca 20–50-krokowy potok dyfuzyjny w 1–4 etapy zbliżone do GAN, zachowując rozkład wyuczony przez model dyfuzyjny. Kontradwersaryjna funkcja straty przetrwała jako narzędzie do przyspieszania powolnych generatorów.

## Dalsza lektura

- [Goodfellow et al. (2014). Generative Adversarial Nets](https://arxiv.org/abs/1406.2661) — oryginalna publikacja nt. GAN-ów.
- [Radford et al. (2015). Unsupervised Representation Learning with DCGAN](https://arxiv.org/abs/1511.06434) — pierwsza stabilna architektura.
- [Arjovsky, Chintala, Bottou (2017). Wasserstein GAN](https://arxiv.org/abs/1701.07875) — WGAN.
- [Miyato et al. (2018). Spectral Normalization for GANs](https://arxiv.org/abs/1802.05957) — normalizacja spektralna (SN).
- [Karras et al. (2020). Analyzing and Improving the Image Quality of StyleGAN](https://arxiv.org/abs/1912.04958) — StyleGAN2.
- [Karras et al. (2021). Alias-Free Generative Adversarial Networks](https://arxiv.org/abs/2106.12423) — StyleGAN3.
- [Sauer et al. (2023). Adversarial Diffusion Distillation](https://arxiv.org/abs/2311.17042) — SDXL-Turbo.
