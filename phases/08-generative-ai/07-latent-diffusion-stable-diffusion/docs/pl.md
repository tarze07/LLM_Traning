# Ukryta dyfuzja i stabilna dyfuzja

> Rozpraszanie przestrzeni pikseli na obrazach 512×512 jest obliczeniową zbrodnią wojenną. Rombacha i in. (2022) zauważyli, że do wygenerowania obrazu nie potrzeba wszystkich 786 tys. wymiarów — wystarczy, aby uchwycić strukturę semantyczną, a do reszty potrzebny jest oddzielny dekoder. Uruchom dyfuzję w utajonej przestrzeni VAE. Tym jednym pomysłem jest stabilna dyfuzja.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania:** Faza 8 · 02 (VAE), Faza 8 · 06 (DDPM), Faza 7 · 09 (ViT)
**Czas:** ~75 minut

## Problem

Rozproszenie w przestrzeni pikseli przy 512² oznacza, że U-Net działa na tensorach o kształcie `[B, 3, 512, 512]`. Każdy krok próbkowania wynosi ~100 GFLOPS dla sieci U-Net o parametrach 500M. Pięćdziesiąt kroków to 5 TFLOPS na obraz. Trenuj na miliardzie obrazów, a rachunek za obliczenia jest absurdalny.

Większość tych FLOP-ów polega na przepychaniu przez sieć percepcyjnie nieistotnych szczegółów — tekstury o wysokiej częstotliwości, którą stratny VAE mógłby skompresować. Pomysł Rombacha: wytrenuj VAE raz (*pierwszy etap*), zamroź go i przeprowadź dyfuzję całkowicie w 4-kanałowej przestrzeni ukrytej 64×64 (*drugi etap*). Ta sama sieć U. 1/16 pikseli. ~64x mniej FLOP-ów przy porównywalnej jakości.

To jest przepis na stabilną dyfuzję. SD 1.x / 2.x korzystało z sieci U-Net 860M przez `64×64×4`, SDXL korzystało z sieci U-Net 2,6B przez `128×128×4`, SD3 zamieniło sieć U-Net na transformator dyfuzyjny (DiT) z dopasowaniem przepływu. Flux.1-dev (Black Forest Labs, 2024) dostarcza moduł DiT-MMDiT o parametrach 12B. Wszystkie działają na tym samym dwustopniowym podłożu.

## Koncepcja

![Dyfuzja utajona: kompresja VAE + dyfuzja w przestrzeni utajonej](../assets/latent-diffusion.svg)

**Dwa etapy, oddzielnie przeszkolone.**

1. **Etap 1 — VAE.** Koder `E(x) → z`, dekoder `D(z) → x`. Kompresja docelowa: próbkowanie 8× na każdej osi przestrzennej + dostosowanie kanałów tak, aby całkowity rozmiar ukryty wynosił ~1/16 liczby pikseli. Strata = rekonstrukcja (L1 + LPIPS percepcyjna) + KL (mała waga, więc `z` nie jest wymuszone zbyt Gaussa, ponieważ nie potrzebujemy dokładnego próbkowania z `z`). Często trenowany ze stratą kontradyktoryjną, więc zdekodowane obrazy są ostre.

2. **Etap 2 — rozpowszechnianie na `z`.** Traktuj `z = E(x_real)` jako dane. Trenuj U-Net (lub DiT), aby odszumiać `z_t`. Podsumowując: próbka `z_0` poprzez dyfuzję, a następnie `x = D(z_0)`.

**Kondycjonowanie tekstu.** Dwa dodatkowe komponenty. Koder zamrożonego tekstu (CLIP-L dla SD 1.x, CLIP-L+OpenCLIP-G dla SD 2/XL, T5-XXL dla SD3 i Flux). Zastrzyk krzyżowy: każdy blok U-Net pobiera `[Q = image features, K = V = text tokens]` i miesza je. Tokeny to jedyny sposób, w jaki tekst wpływa na obraz.

**Funkcja straty jest identyczna jak w lekcji 06.** To samo DDPM/dopasowanie przepływu MSE w przypadku szumu. Po prostu zamieniasz domenę danych.

## Warianty architektury

| Modelka | Rok | Kręgosłup | Ukryty kształt | Koder tekstu | Parametry |
|-------|------|----------|-------------|--------------|--------|
| SD 1,5 | 2022 | U-Net | 64×64×4 | CLIP-L (77 żetonów) | 860M |
| SD 2.1 | 2022 | U-Net | 64×64×4 | OpenCLIP-H | 865M |
| SDXL | 2023 | U-Net + rafineria | 128×128×4 | CLIP-L + OpenCLIP-G | 2,6B + 6,6B |
| SDXL-Turbo | 2023 | Destylowana | 128×128×4 | to samo | Pobieranie próbek 1-4 kroków |
| SD3 | 2024 | MMDiT (multimodalny DiT) | 128×128×16 | T5-XXL + CLIP-L + CLIP-G | 2B/8B |
| Flux.1-dev | 2024 | MMDiT | 128×128×16 | T5-XXL + CLIP-L | 12B |
| Flux.1-schnell | 2024 | MMDiT destylowany | 128×128×16 | T5-XXL + CLIP-L | 12B, krok 1-4 |

Tendencja: zastąpienie U-Net przez DiT (transformator nad ukrytymi poprawkami), skalowanie kodera tekstowego (T5 bije CLIP, aby uzyskać natychmiastową przyczepność), zwiększenie ukrytych kanałów (4 → 16 daje większy zapas szczegółów).

## Zbuduj to

`code/main.py` układa zabawkowy 1-D „VAE” (koder tożsamości + dekoder, do celów demonstracyjnych; prawdziwy VAE byłby siecią konwersji) na wierzchu DDPM z lekcji 06 i dodaje warunkowanie klas ze wskazówkami bez klasyfikatorów. Pokazuje, że ta sama strata dyfuzyjna działa niezależnie od tego, czy pracujesz na surowych wartościach 1-D, czy na wartościach zakodowanych – co jest kluczowym spostrzeżeniem.

### Krok 1: koder/dekoder

```python
def encode(x):    return x * 0.5          # toy "compression" to smaller scale
def decode(z):    return z * 2.0
```

Prawdziwy VAE trenuje z ciężarami. W pedagogice ta mapa liniowa wystarczy, aby pokazać, że dyfuzja działa na `z` bez dbania o pierwotną przestrzeń danych.

### Krok 2: dyfuzja w przestrzeni `z`

Taki sam DDPM jak w lekcji 06. Dane widoczne w sieci to `z = E(x)`. Po próbkowaniu `z_0` zdekoduj za pomocą `D(z_0)`.

### Krok 3: wskazówki bez klasyfikatorów

Podczas szkolenia upuść etykietę klasy w 10% przypadków (zastąp tokenem zerowym). Podsumowując, oblicz zarówno `ε_cond`, jak i `ε_uncond`, a następnie:

```python
eps_cfg = (1 + w) * eps_cond - w * eps_uncond
```

`w = 0` = brak wskazówek (pełna różnorodność), `w = 3` = ustawienie domyślne, `w = 7+` = nasycone / zbyt ostre.

### Krok 4: warunkowanie tekstu (koncepcja, nie kod)

Zastąp etykietę klasy zamrożonym wyjściem kodera tekstu. Przekaż osadzany tekst do sieci U-Net poprzez wzajemne zainteresowanie:

```python
h = h + CrossAttention(Q=h, K=text_embed, V=text_embed)
```

Jest to jedyna istotna różnica pomiędzy modelem dyfuzji warunkowej klasowo a dyfuzją stabilną.

## Pułapki

- **Niedopasowanie skali VAE.** SD 1.x VAE mają stałą skalowania (`scaling_factor ≈ 0.18215`) zastosowaną po kodowaniu. Zapomnienie o tym powoduje, że U-Net wykorzystuje ukryte dane z niezwykle błędnymi odchyleniami. Każdy punkt kontrolny wysyła jednego.
- **Koder tekstu cicho błędny.** SD3 potrzebuje T5-XXL z >=128 tokenami, a powrót do tylko CLIP jest stratny. Zawsze sprawdzaj `use_t5=True` lub sprawdzaj kratery wierności.
- **Mieszanie ukrytych przestrzeni.** SDXL, SD3, Flux używają różnych VAE. LoRA przeszkolona w zakresie ukrytych SDXL nie będzie działać na SD3. Dyfuzory Hugging Face 0.30+ nie ładują niedopasowanych punktów kontrolnych.
- **CFG za wysoki.** `w > 10` tworzy nasycone, tłuste obrazy i nadmiernie pasuje do podpowiedzi kosztem różnorodności. Najlepszym rozwiązaniem jest `w = 3-7`.
- **Wyciek negatywnych podpowiedzi.** Pusta negatywna zachęta staje się tokenem zerowym; wypełniony monit negatywny staje się `ε_uncond`. To nie to samo; niektóre potoki po cichu mają domyślnie ustawioną wartość null.

## Użyj tego

Stosy produkcyjne w 2026 roku:

| Cel | Zalecany szkielet |
|------------|----------------------|
| Wąska domena, sparowane dane, szkolenie modelu od podstaw | Dostrojenie SDXL (LoRA / pełne) — najszybsza wysyłka |
| Zamiana tekstu na obraz w domenie otwartej, otwarte wagi | Flux.1-dev (12B, Apache / wersja niekomercyjna) lub SD3.5-Large |
| Najszybsze wnioskowanie, otwarte wagi | Flux.1-schnell (1-4 kroki, Apache) lub SDXL-Lightning |
| Najlepsze szybkie przestrzeganie, hostowane | Obraz GPT / DALL-E 3 (nieruchomy), Midjourney v7, obraz 4 |
| Edytuj przepływy pracy | Flux.1-Kontext (grudzień 2024) — natywnie akceptuje obraz + tekst |
| Badania, poziom bazowy | SD 1.5 — starożytny, ale dobrze zbadany |

## Wyślij to

Zapisz `outputs/skill-sd-prompter.md`. Umiejętność wymaga podpowiedzi tekstowej + stylu docelowego i wyników: model + punkt kontrolny, skala CFG, próbnik, podpowiedź negatywna, rozdzielczość, opcjonalna kombinacja ControlNet/Adapter IP oraz lista kontrolna kontroli jakości na każdym etapie.

## Ćwiczenia

1. **Łatwe.** Uruchom `code/main.py` ze wskazówkami `w ∈ {0, 1, 3, 7, 15}`. Zapisz średnią próbkę według klasy. W jakim `w` średnie wartości klasy odbiegają od średnich danych rzeczywistych?
2. **Średni.** Zamień zabawkowy koder liniowy na parę koder/dekoder tanh-MLP ze stratą rekonstrukcji. Ponowne przeszkolenie dyfuzji na nowych utajonych. Czy jakość próbki ulega zmianie?
3. **Trudne.** Skonfiguruj rzeczywiste wnioskowanie o stabilnej dyfuzji z dyfuzorami: załaduj `sdxl-base`, wykonaj 30 kroków Eulera z CFG=7, zmierz czas. Teraz przejdź do `sdxl-turbo` z 4 krokami i CFG=0. Ten sam temat, inna jakość – opisz, co się zmieniło i dlaczego.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Pierwszy etap | „VAE” | Przeszkolona para kodera/dekodera; kompresuje 512² do 64². |
| Drugi etap | „Sieć U” | Model dyfuzji w przestrzeni utajonej. |
| CFG | „Skala wskazówek” | `(1+w)·ε_cond - w·ε_uncond`; reguluje siłę kondycjonowania. |
| Token zerowy | „Osadzanie pustego monitu” | Bezwarunkowe osadzenie używane dla `ε_uncond`. |
| Uwaga krzyżowa | „Jak tekst dostaje się do środka” | Każdy blok U-Net dotyczy tokenów tekstowych jako K i V. |
| DiT | „Transformator dyfuzyjny” | Zamień U-Net na transformator w przypadku ukrytych poprawek; skaluje się lepiej. |
| MMDiT | „Wielomodalny DiT” | Architektura SD3: strumienie tekstu i obrazu ze wspólną uwagą. |
| Współczynnik skalowania VAE | „Magiczna liczba” | Dzieli utajone przez ~ 5,4, więc dyfuzja działa w przestrzeni jednostkowej wariancji. |

## Uwaga produkcyjna: uruchamianie Flux-12B na konsumenckim procesorze graficznym o pojemności 8 GB

referencyjna integracja Flux jest kanoniczna: „Mam konsumencki procesor graficzny, czy mogę go wysłać?” przepis. Sztuczka polega na tym, że te same trzypokrętłowe listy literatury dotyczącej produkcji receptur zastosowano w przypadku dyfuzyjnego DiT:

1. **Ładowanie naprzemienne.** Flux ma trzy sieci, które nigdy nie muszą współistnieć w pamięci VRAM: koder tekstu T5-XXL (~10 GB w fp32), CLIP-L (mały), 12B MMDiT i VAE. Najpierw zakoduj zachętę, *usuń* kodery, załaduj DiT, odszumij, *usuń* DiT, załaduj VAE, zdekoduj. Konsumenckie procesory graficzne o pojemności 8 GB pasują tylko do jednego stopnia na raz.
2. **4-bitowa kwantyzacja za pomocą bitów i bajtów.** `BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16)` zarówno w koderze T5, jak i DiT. Zmniejsza pamięć 8×, spadek jakości jest niezauważalny w przypadku zamiany tekstu na obraz według testów porównawczych Aritry (link w notatniku).
3. **Odciążenie procesora.** `pipe.enable_model_cpu_offload()` automatycznie zamienia moduły między procesorem a procesorem graficznym w miarę postępu każdego przebiegu w przód. Dodaje 10–20% opóźnienia, ale w ogóle powoduje uruchomienie potoku.

Rejestracja pamięci jest następująca: `10 GB T5 / 8 = 1.25 GB` skwantowana, `12 B params × 0.5 bytes = ~6 GB` skwantowana DiT plus aktywacje. W terminologii stas00 jest to skrajny koniec wnioskowania TP=1 — brak równoległości modelu, maksymalna kwantyzacja. Do celów produkcyjnych uruchomiłbyś TP=2 lub TP=4 na H100; w przypadku laptopa z jednym deweloperem jest to przepis.

## Dalsze czytanie

- [Rombach i in. (2022). Synteza obrazu o wysokiej rozdzielczości z modelami dyfuzji utajonej](https://arxiv.org/abs/2112.10752) — Stabilna dyfuzja.
- [Podell i in. (2023). SDXL: Udoskonalanie modeli dyfuzji utajonej na potrzeby syntezy obrazu w wysokiej rozdzielczości](https://arxiv.org/abs/2307.01952) — SDXL.
- [Peebles i Xie (2023). Skalowalne modele dyfuzyjne z transformatorami (DiT)](https://arxiv.org/abs/2212.09748) — DiT.
- [Esser i in. (2024). Skalujące rektyfikowane transformatory przepływowe do syntezy obrazu w wysokiej rozdzielczości](https://arxiv.org/abs/2403.03206) — SD3, MMDiT.
- [Ho i Salimans (2022). Wytyczne dotyczące rozpowszechniania bez klasyfikatorów](https://arxiv.org/abs/2207.12598) — CFG.
- [Laboratoria (2024). Flux.1 — ogłoszenie Black Forest Labs](https://blackforestlabs.ai/announcing-black-forest-labs/) — rodzina Flux.1.
– [Dokumentacja Hugging Face Diffusers](https://huggingface.co/docs/diffusers/index) — referencyjna implementacja dla każdego powyższego punktu kontrolnego.