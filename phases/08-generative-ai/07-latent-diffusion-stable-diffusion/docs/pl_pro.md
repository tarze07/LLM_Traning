# Ukryta dyfuzja i stabilna dyfuzja

> Przeprowadzanie dyfuzji w przestrzeni pikseli dla obrazów 512×512 to obliczeniowe marnotrawstwo. Rombach i in. (2022) zauważyli, że do wygenerowania obrazu nie potrzeba wszystkich 786 tys. wymiarów — wystarczy uchwycić strukturę semantyczną, a dekompresję pozostawić oddzielnemu dekoderowi. Wystarczy uruchomić dyfuzję w utajonej przestrzeni VAE. Ten jeden pomysł leży u podstaw stabilnej dyfuzji.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania:** Faza 8 · 02 (VAE), Faza 8 · 06 (DDPM), Faza 7 · 09 (ViT)
**Czas:** ~75 minut

## Problem

Dyfuzja w przestrzeni pikseli przy rozdzielczości 512² oznacza, że U-Net operuje na tensorach o kształcie `[B, 3, 512, 512]`. Każdy krok próbkowania kosztuje ~100 GFLOPS dla sieci U-Net z 500M parametrów. Pięćdziesiąt kroków to 5 TFLOPS na obraz. Przy trenowaniu na miliardzie obrazów koszty obliczeniowe stają się niepraktyczne.

Większość tych FLOP-ów przypada na przetwarzanie percepcyjnie nieistotnych szczegółów — tekstur wysokoczęstotliwościowych, które stratny VAE mógłby skompresować. Rombach zaproponował następujące rozwiązanie: raz wytrenuj VAE (*pierwszy etap*), zamroź go, a całą dyfuzję przeprowadź w 4-kanałowej przestrzeni ukrytej 64×64 (*drugi etap*). Ta sama sieć — lecz na 1/16 pikseli — daje ~64-krotną redukcję FLOP-ów przy porównywalnej jakości.

To właśnie jest przepis na stabilną dyfuzję. SD 1.x / 2.x korzystało z sieci U-Net (860M parametrów) operującej na przestrzeni `64×64×4`, SDXL używał U-Neta 2,6B z przestrzenią `128×128×4`, a SD3 zastąpił U-Net transformatorem dyfuzyjnym (DiT) z dopasowaniem przepływu. Flux.1-dev (Black Forest Labs, 2024) wprowadza moduł DiT-MMDiT o 12B parametrach. Wszystkie te modele opierają się na tym samym dwuetapowym fundamencie.

## Koncepcja

![Dyfuzja utajona: kompresja VAE + dyfuzja w przestrzeni utajonej](../assets/latent-diffusion.svg)

**Dwa etapy, trenowane osobno.**

1. **Etap 1 — VAE.** Koder `E(x) → z`, dekoder `D(z) → x`. Cel kompresji: próbkowanie 8× wzdłuż każdej osi przestrzennej i dostosowanie liczby kanałów tak, aby całkowity rozmiar reprezentacji utajonej wynosił ~1/16 liczby pikseli. Strata = rekonstrukcja (L1 + percepcyjne LPIPS) + KL z małą wagą (dzięki czemu `z` nie jest nadmiernie gaussowskie — dokładne próbkowanie z `z` nie jest tu potrzebne). Często trenowany ze stratą kontradyktoryjną, co zapewnia ostrość zdekodowanych obrazów.

2. **Etap 2 — dyfuzja na `z`.** Traktuj `z = E(x_real)` jako dane treningowe. Trenuj U-Net (lub DiT) do odszumiania `z_t`. W fazie inferencji: próbkuj `z_0` przez dyfuzję, następnie oblicz `x = D(z_0)`.

**Kondycjonowanie tekstem.** Potrzebne są dwa dodatkowe komponenty: zamrożony koder tekstu (CLIP-L dla SD 1.x, CLIP-L+OpenCLIP-G dla SD 2/XL, T5-XXL dla SD3 i Flux) oraz warstwa cross-attention — każdy blok U-Neta przyjmuje `[Q = cechy obrazu, K = V = tokeny tekstu]` i miesza je. Tokeny tekstowe to jedyna droga, przez którą tekst wpływa na obraz.

**Funkcja straty jest identyczna jak w lekcji 06.** To samo DDPM lub dopasowanie przepływu z MSE dla szumu. Zmienia się jedynie dziedzina danych.

## Warianty architektury

| Model | Rok | Szkielet | Kształt przestrzeni utajonej | Koder tekstu | Parametry |
|-------|------|----------|-------------|--------------|--------|
| SD 1,5 | 2022 | U-Net | 64×64×4 | CLIP-L (77 tokenów) | 860M |
| SD 2.1 | 2022 | U-Net | 64×64×4 | OpenCLIP-H | 865M |
| SDXL | 2023 | U-Net + refiner | 128×128×4 | CLIP-L + OpenCLIP-G | 2,6B + 6,6B |
| SDXL-Turbo | 2023 | Destylowany | 128×128×4 | jak wyżej | Próbkowanie w 1–4 krokach |
| SD3 | 2024 | MMDiT (multimodalny DiT) | 128×128×16 | T5-XXL + CLIP-L + CLIP-G | 2B/8B |
| Flux.1-dev | 2024 | MMDiT | 128×128×16 | T5-XXL + CLIP-L | 12B |
| Flux.1-schnell | 2024 | Destylowany MMDiT | 128×128×16 | T5-XXL + CLIP-L | 12B, 1–4 kroki |

Widoczne tendencje: zastępowanie U-Neta przez DiT (transformator operujący na fragmentach przestrzeni utajonej), skalowanie kodera tekstowego (T5 przewyższa CLIP pod względem precyzji opisu), zwiększanie liczby kanałów utajonych (z 4 do 16, co zapewnia większą pojemność szczegółów).

## Zbuduj to

`code/main.py` składa zabawkowy 1-D „VAE" (uproszczone odwzorowanie koder–dekoder, dla celów demonstracyjnych; prawdziwy VAE byłby siecią splotową) na bazie DDPM z lekcji 06 i dodaje warunkowanie klasą z użyciem classifier-free guidance. Pokazuje, że ta sama strata dyfuzyjna działa niezależnie od tego, czy pracujesz na surowych wartościach 1-D, czy na wartościach zakodowanych — to jest kluczowa obserwacja.

### Krok 1: koder/dekoder

```python
def encode(x):    return x * 0.5          # toy "compression" to smaller scale
def decode(z):    return z * 2.0
```

Prawdziwy VAE trenuje z wagami. W tej wersji demonstracyjnej proste odwzorowanie liniowe wystarczy, by pokazać, że dyfuzja działa na `z` bez znajomości oryginalnej przestrzeni danych.

### Krok 2: dyfuzja w przestrzeni `z`

Identyczny DDPM jak w lekcji 06. Dane widoczne przez sieć to `z = E(x)`. Po wylosowaniu `z_0` dekoduj przez `D(z_0)`.

### Krok 3: classifier-free guidance

Podczas trenowania pomijaj etykietę klasy w 10% przypadków (zastępuj zerowym tokenem). Przy inferencji oblicz zarówno `ε_cond`, jak i `ε_uncond`, a następnie:

```python
eps_cfg = (1 + w) * eps_cond - w * eps_uncond
```

`w = 0` = brak prowadzenia (pełna różnorodność), `w = 3` = ustawienie domyślne, `w = 7+` = nasycone / przeostre wyniki.

### Krok 4: warunkowanie tekstem (koncepcja, bez kodu)

Zastąp etykietę klasy zamrożonym wyjściem kodera tekstu. Przekaż osadzenia tekstowe do U-Neta przez cross-attention:

```python
h = h + CrossAttention(Q=h, K=text_embed, V=text_embed)
```

To jedyna istotna różnica między modelem dyfuzji warunkowanej klasą a stabilną dyfuzją.

## Pułapki

- **Niedopasowanie skali VAE.** Modele SD 1.x stosują stały współczynnik skalowania (`scaling_factor ≈ 0.18215`) po kodowaniu. Pominięcie go skutkuje tym, że U-Net otrzymuje reprezentacje utajone z nieprawidłowymi odchyleniami. Każdy checkpoint zawiera ten parametr.
- **Cicho błędny koder tekstu.** SD3 wymaga T5-XXL z co najmniej 128 tokenami; powrót do samego CLIP jest stratny. Zawsze sprawdzaj `use_t5=True` lub weryfikuj jakość wyników.
- **Mieszanie przestrzeni utajonych.** SDXL, SD3 i Flux korzystają z różnych VAE. LoRA wytrenowana na utajonych SDXL nie zadziała z SD3. Biblioteka Diffusers Hugging Face w wersji 0.30+ odrzuca niedopasowane checkpointy.
- **Za wysoki CFG.** `w > 10` daje nasycone, przeładowane obrazy i nadmierne dopasowanie do promptu kosztem różnorodności. Optymalne wartości to `w = 3–7`.
- **Problem z pustym negatywnym promptem.** Pusty prompt negatywny staje się zerowym tokenem, a wypełniony — wektorem `ε_uncond`. To nie to samo; niektóre pipeline'y domyślnie milcząco ustawiają wartość null.

## Zastosowania produkcyjne

Zestawienie stosów produkcyjnych na rok 2026:

| Cel | Zalecane narzędzie |
|------------|----------------------|
| Wąska dziedzina, dane parowane, trening od zera | Fine-tuning SDXL (LoRA lub pełny) — najszybsze wdrożenie |
| Generowanie obrazów z tekstu w otwartej dziedzinie, otwarte wagi | Flux.1-dev (12B, Apache / licencja niekomercyjna) lub SD3.5-Large |
| Najszybsza inferencja, otwarte wagi | Flux.1-schnell (1–4 kroki, Apache) lub SDXL-Lightning |
| Najlepsza zgodność z promptem, rozwiązania hostowane | GPT Image / DALL-E 3, Midjourney v7, Image 4 |
| Przepływy pracy z edycją | Flux.1-Kontext (grudzień 2024) — natywnie akceptuje obraz i tekst |
| Badania, punkt bazowy | SD 1.5 — przestarzały, ale dobrze zbadany |

## Zadanie do oddania

Zapisz plik `outputs/skill-sd-prompter.md`. Umiejętność wymaga podania promptu tekstowego i docelowego stylu; powinna zwracać: model i checkpoint, skalę CFG, próbnik, prompt negatywny, rozdzielczość, opcjonalne połączenie ControlNet/IP-Adapter oraz listę kontrolną weryfikacji jakości dla każdego etapu.

## Ćwiczenia

1. **Łatwe.** Uruchom `code/main.py` z wartościami guidance `w ∈ {0, 1, 3, 7, 15}`. Zapisz średnią próbkę dla każdej klasy. Przy jakim `w` średnie wartości klas zaczynają odbiegać od średnich danych rzeczywistych?
2. **Średnie.** Zastąp uproszczony koder liniowy parą koder/dekoder opartą na MLP z aktywacją tanh i stratą rekonstrukcji. Przetrenuj dyfuzję na nowych reprezentacjach utajonych. Czy jakość próbek ulega zmianie?
3. **Trudne.** Skonfiguruj rzeczywistą inferencję stabilnej dyfuzji z biblioteką Diffusers: wczytaj `sdxl-base`, wykonaj 30 kroków solvera Eulera z CFG=7, zmierz czas. Następnie przejdź do `sdxl-turbo` z 4 krokami i CFG=0. Ten sam prompt, inna jakość — opisz, co się zmieniło i dlaczego.

## Kluczowe terminy

| Termin | Potoczne określenie | Znaczenie techniczne |
|------|-----------------|----------------------|
| Pierwszy etap | „VAE" | Wytrenowana para koder/dekoder; kompresuje 512² do 64². |
| Drugi etap | „U-Net" | Model dyfuzji działający w przestrzeni utajonej. |
| CFG | „Skala prowadzenia" | `(1+w)·ε_cond - w·ε_uncond`; reguluje siłę kondycjonowania. |
| Zerowy token | „Osadzenie pustego promptu" | Bezwarunkowe osadzenie używane jako `ε_uncond`. |
| Cross-attention | „Jak tekst trafia do modelu" | Każdy blok U-Neta traktuje tokeny tekstowe jako K i V. |
| DiT | „Transformator dyfuzyjny" | Zastąpienie U-Neta transformatorem operującym na fragmentach przestrzeni utajonej; lepiej się skaluje. |
| MMDiT | „Multimodalny DiT" | Architektura SD3: strumienie tekstu i obrazu ze wspólną uwagą. |
| Współczynnik skalowania VAE | „Magiczna liczba" | Dzieli reprezentacje utajone przez ~5,4, tak aby dyfuzja działała w przestrzeni o wariancji jednostkowej. |

## Uwaga produkcyjna: uruchamianie Flux-12B na konsumenckim GPU 8 GB

Integracja referencyjna Flux odpowiada na pytanie: „Mam konsumencki GPU — czy mogę na nim uruchomić ten model?" Kluczowe są trzy techniki stosowane przy produkcyjnym wdrażaniu dużych modeli DiT:

1. **Naprzemienne ładowanie modułów.** Flux składa się z trzech sieci, które nigdy nie muszą jednocześnie znajdować się w pamięci VRAM: koder tekstu T5-XXL (~10 GB w fp32), CLIP-L (mały), 12B MMDiT oraz VAE. Schemat działania: zakoduj prompt, *usuń* kodery, wczytaj DiT, przeprowadź odszumianie, *usuń* DiT, wczytaj VAE, zdekoduj. Na konsumenckim GPU 8 GB w danej chwili mieści się tylko jeden etap.
2. **4-bitowa kwantyzacja przez bitsandbytes.** `BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16)` stosowane zarówno dla kodera T5, jak i DiT. Zmniejsza zużycie pamięci 8-krotnie; spadek jakości jest niezauważalny w zadaniu text-to-image według benchmarków Aritry (link w notatniku).
3. **Offloading na CPU.** `pipe.enable_model_cpu_offload()` automatycznie przenosi moduły między CPU a GPU w trakcie każdego przejścia w przód. Dodaje 10–20% opóźnienia, ale umożliwia uruchomienie pipeline'u w ogóle.

Bilans pamięci wygląda następująco: `10 GB T5 / 8 = 1,25 GB` po kwantyzacji, `12B parametrów × 0,5 bajta = ~6 GB` dla skwantowanego DiT wraz z aktywacjami. W terminologii stas00 to skrajny przypadek inferencji TP=1 — brak równoległości modelu, maksymalna kwantyzacja. W środowisku produkcyjnym użyłbyś TP=2 lub TP=4 na H100; na laptopie jednego dewelopera jest to rozwiązanie wystarczające.

## Literatura uzupełniająca

- [Rombach i in. (2022). Synteza obrazu o wysokiej rozdzielczości z modelami dyfuzji utajonej](https://arxiv.org/abs/2112.10752) — Stable Diffusion.
- [Podell i in. (2023). SDXL: Ulepszenie modeli dyfuzji utajonej do syntezy obrazu w wysokiej rozdzielczości](https://arxiv.org/abs/2307.01952) — SDXL.
- [Peebles i Xie (2023). Skalowalne modele dyfuzyjne z transformatorami (DiT)](https://arxiv.org/abs/2212.09748) — DiT.
- [Esser i in. (2024). Skalowanie rektyfikowanych transformatorów przepływu do syntezy obrazu w wysokiej rozdzielczości](https://arxiv.org/abs/2403.03206) — SD3, MMDiT.
- [Ho i Salimans (2022). Classifier-Free Diffusion Guidance](https://arxiv.org/abs/2207.12598) — CFG.
- [Black Forest Labs (2024). Flux.1 — ogłoszenie Black Forest Labs](https://blackforestlabs.ai/announcing-black-forest-labs/) — rodzina Flux.1.
- [Dokumentacja Hugging Face Diffusers](https://huggingface.co/docs/diffusers/index) — implementacja referencyjna dla każdego z powyższych checkpointów.
