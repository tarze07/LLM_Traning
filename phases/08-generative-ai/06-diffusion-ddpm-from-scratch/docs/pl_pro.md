# Modele dyfuzyjne — DDPM od podstaw

> Ho, Jain, Abbeel (2020) opracowali w tej dziedzinie przepis, od którego nie ma odwrotu. Zniszcz dane szumem w tysiącu małych kroków. Wytrenuj sieć neuronową do przewidywania szumu. Odwróć ten proces podczas wnioskowania. Dziś każdy wiodący model obrazu, wideo, grafiki 3D i muzyki działa na tej samej zasadzie — być może wzbogaconej o techniki dopasowywania przepływu lub spójności.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 3 · 02 (podpórka), Faza 8 · 02 (VAE)
**Czas:** ~75 minut

## Problem

Potrzebujesz próbnika dla `p_data(x)`. Sieci GAN rozwiązują grę minimax, która często jest niestabilna. VAE produkują rozmyte próbki z dekodera Gaussa. W praktyce potrzebujesz celu treningowego spełniającego trzy warunki: (a) pojedyncza, stabilna strata — bez punktu siodłowego i minimaksu, (b) dolna granica `log p(x)`, zapewniająca miarę prawdopodobieństwa, oraz (c) próbki dorównujące jakością aktualnym najlepszym rozwiązaniom.

Sohl-Dickstein i in. (2015) zaproponowali odpowiedź teoretyczną: zdefiniuj łańcuch Markowa `q(x_t | x_{t-1})`, który stopniowo dodaje szum Gaussa, i wytrenuj łańcuch odwrotny `p_θ(x_{t-1} | x_t)` do usuwania tego szumu. Ho, Jain i Abbeel (2020) pokazali, że stratę można sprowadzić do jednej linii — przewidywania szumu — i w ten sposób uporządkowali matematyczne podstawy. W 2020 roku była to ciekawostka. W 2021 roku metoda osiągnęła czołowe wyniki. W 2022 roku stała się fundamentem Stable Diffusion. W 2026 roku jest to już standard.

## Koncepcja

![DDPM: szum w przód, odszumianie w tył](../assets/ddpm.svg)

**Przebieg procesu `q`.** Szum Gaussa jest dodawany w małych krokach przez `T` iteracji. Kluczowa właściwość — i zarazem powód, dla którego matematyka pozostaje przejrzysta — polega na tym, że krok skumulowany ma również postać rozkładu Gaussa:

```
q(x_t | x_0) = N( sqrt(α̅_t) · x_0,  (1 - α̅_t) · I )
```

gdzie `α̅_t = ∏_{s=1..t} (1 - β_s)` dla harmonogramu `β_t`. Przy liniowym rozkładzie `β_t` od 1e-4 do 0,02 na T=1000 kroków wartość `x_T` jest w przybliżeniu równa `N(0, I)`.

**Proces odwrotny `p_θ`.** Sieć neuronowa `ε_θ(x_t, t)` uczy się przewidywać dodany szum. Mając `x_t`, odszumianie przebiega według wzoru:

```
x_{t-1} = (1 / sqrt(α_t)) · ( x_t - (β_t / sqrt(1 - α̅_t)) · ε_θ(x_t, t) )  +  σ_t · z
```

gdzie `σ_t` to `sqrt(β_t)` lub nauczona wariancja. Wyrażenie wygląda skomplikowanie, lecz jest to zwykła algebra — rozwiązanie `x_{t-1}` z posteriori `q(x_{t-1} | x_t, x_0)` po podstawieniu `x_0` przewidywanego przez sieć.

**Strata treningowa.**

```
L_simple = E_{x_0, t, ε} [ || ε - ε_θ( sqrt(α̅_t) · x_0 + sqrt(1 - α̅_t) · ε,  t ) ||² ]
```

Pobierz próbkę `x_0` z danych, wylosuj `t`, próbkuj `ε ~ N(0, I)`, oblicz zaszumione `x_t` bezpośrednio w postaci zamkniętej i wykonaj regresję szumu. Jedna strata, żadnego minimaksu, żadnego KL, żadnych trików reparametryzacyjnych.

**Próbkowanie.** Zacznij od `x_T ~ N(0, I)`. Wykonuj krok odwrotny dla `t = T` aż do `1`. Gotowe.

## Dlaczego to działa

Trzy intuicje:

1. **Odszumianie jest łatwe; generowanie jest trudne.** Przy `t=T` dane to czysty szum — sieć rozwiązuje trywialny problem. Przy `t=0` musi poprawić już tylko kilka pikseli. Na pośrednich krokach `t` zadanie jest trudniejsze, ale sieć korzysta z bogatego przepływu gradientów przez te same wagi na każdym poziomie szumu.

2. **Ukryte dopasowanie wyników.** Vincent (2011) udowodnił, że przewidywanie szumu jest równoważne szacowaniu `∇_x log q(x_t | x_0)` — tzw. *score'u*. Odwrotna SDE wykorzystuje ten score do poruszania się w górę gradientu gęstości, czyli do losowego błądzenia prowadzącego w kierunku obszarów wysokiego prawdopodobieństwa.

3. **ELBO redukuje się do prostego MSE.** Pełna wariacyjna dolna granica zawiera człon KL na każdy krok czasowy. Dzięki parametryzacji DDPM człony te upraszczają się do MSE przewidywania szumu z określonymi współczynnikami wagowymi. Ho pominął te współczynniki (nazywając wynik stratą „prostą"), a jakość próbek *poprawiła się*.

## Zbuduj to

`code/main.py` implementuje DDPM w przestrzeni 1-D. Dane stanowią mieszaninę dwóch modów. Sieć to mały MLP przyjmujący `(x_t, t)` i zwracający przewidywany szum. Trening opiera się na jednotermowej stracie, a próbkowanie iteruje odwrotny łańcuch.

### Krok 1: harmonogram przekazania (postać zamknięta)

```python
betas = [1e-4 + (0.02 - 1e-4) * t / (T - 1) for t in range(T)]
alphas = [1 - b for b in betas]
alpha_bars = []
cum = 1.0
for a in alphas:
    cum *= a
    alpha_bars.append(cum)
```

### Krok 2: próbka `x_t` w postaci zamkniętej

```python
def forward_sample(x0, t, alpha_bars, rng):
    a_bar = alpha_bars[t]
    eps = rng.gauss(0, 1)
    x_t = math.sqrt(a_bar) * x0 + math.sqrt(1 - a_bar) * eps
    return x_t, eps
```

### Krok 3: pojedynczy krok treningowy

```python
def train_step(x0, model, alpha_bars, rng):
    t = rng.randrange(T)
    x_t, eps = forward_sample(x0, t, alpha_bars, rng)
    eps_hat = model_forward(model, x_t, t)
    loss = (eps - eps_hat) ** 2
    return loss, gradient_step(model, ...)
```

### Krok 4: próbkowanie odwrotne

```python
def sample(model, alpha_bars, T, rng):
    x = rng.gauss(0, 1)
    for t in range(T - 1, -1, -1):
        eps_hat = model_forward(model, x, t)
        beta_t = 1 - alphas[t]
        x = (x - beta_t / math.sqrt(1 - alpha_bars[t]) * eps_hat) / math.sqrt(alphas[t])
        if t > 0:
            x += math.sqrt(beta_t) * rng.gauss(0, 1)
    return x
```

Dla zadania 1-D, przy 40 krokach czasowych i MLP z 24 jednostkami, model uczy się mieszaniny dwóch modów w około 200 epokach.

## Warunkowanie krokiem czasowym

Sieć musi wiedzieć, który krok czasowy odszumia. Dostępne są dwa standardowe podejścia:

- **Osadzanie sinusoidalne.** Analogicznie do kodowania pozycyjnego w transformerze: `embed(t) = [sin(t/ω_0), cos(t/ω_0), sin(t/ω_1), ...]`. Reprezentacja przechodzi przez MLP i jest podawana na wejście sieci.
- **Warunkowanie przez normalizację FiLM/grupową.** Osadzanie jest rzutowane na parametry skali i przesunięcia na każdy kanał (FiLM) w każdym bloku sieci.

Przykładowy kod używa osadzania sinusoidalnego z konkatenacją. Produkcyjne sieci U-Net korzystają z FiLM.

## Pułapki

- **Harmonogram ma duże znaczenie.** Liniowy `β` to domyślny wybór DDPM, lecz harmonogram cosinusowy (Nichol i Dhariwal, 2021) daje lepszy FID przy tym samym koszcie obliczeniowym. Warto go wypróbować, gdy jakość przestaje rosnąć.
- **Osadzanie kroków czasowych jest kluczowe.** Przekazywanie surowego `t` jako liczby zmiennoprzecinkowej sprawdza się w zadaniach zabawkowych, ale nie przy obrazach — zawsze stosuj właściwe osadzanie.
- **Przewidywanie V a przewidywanie ε.** W skrajnych reżimach (bardzo małe lub bardzo duże `t`) predykcja `ε` cechuje się słabym stosunkiem sygnału do szumu. Predykcja V (`v = α·ε - σ·x`) jest stabilniejsza; stosują ją SDXL, SD3 i Flux.
- **Classifier-free guidance.** Podczas wnioskowania wyznacz zarówno warunkowe, jak i bezwarunkowe `ε`, a następnie zastosuj `ε_cfg = (1 + w) · ε_cond - w · ε_uncond` dla `w ≈ 3–7`. Temat jest omówiony w lekcji 08.
- **1000 kroków to dużo.** Produkcyjne implementacje korzystają z DDIM (20–50 kroków), DPM-Solver (10–20 kroków) lub destylacji (1–4 kroki). Więcej w lekcji 12.

## Zastosowania

| Rola | Typowy stack w 2026 r. |
|------|----------------------|
| Dyfuzja obrazu w przestrzeni pikseli (mała skala, eksperymenty) | DDPM + U-Net |
| Ukryta dyfuzja obrazu | Enkoder VAE + U-Net lub DiT (lekcja 07) |
| Ukryta dyfuzja wideo | Czasoprzestrzenny DiT (Sora, Veo, WAN) |
| Ukryta dyfuzja dźwięku | Kodek + transformer dyfuzyjny |
| Nauka (cząsteczki, białka, fizyka) | Dyfuzja z symetrią równoważności (EDM, RFdiffusion, AlphaFold3) |

Dyfuzja jest uniwersalnym szkieletem generatywnym. Flow matching (lekcja 13) to konkurencyjna metoda z lat 2024–2026, która zwykle wyprzedza dyfuzję pod względem szybkości wnioskowania przy porównywalnej jakości.

## Wyślij to

Zapisz `outputs/skill-diffusion-trainer.md`. Umiejętność korzysta ze zbioru danych i budżetu obliczeniowego, a następnie ocenia: harmonogram (liniowy/cosinusowy/esigmoidalny), cel predykcji (ε/v/x), liczbę kroków, skalę wskazówek, rodzinę próbników oraz protokół ewaluacji.

## Ćwiczenia

1. **Łatwe.** Zmień T z 40 na 10 w `code/main.py`. Jak pogarsza się jakość próbek (wizualny histogram wyników)? Przy jakim T znika struktura dwumodalna?
2. **Średnie.** Zastąp przewidywanie ε przewidywaniem v. Przepisz krok odwrotny. Porównaj ostateczną jakość próbek.
3. **Trudne.** Dodaj classifier-free guidance. Warunkuj model na etykiecie klasy `c ∈ {0, 1}`, pomijaj ją losowo w 10% przypadków podczas treningu, a podczas próbkowania stosuj `ε = (1+w)·ε_cond - w·ε_uncond`. Zmierz współczynnik trafień w trybie warunkowym dla `w = 0, 1, 3, 7`.

## Kluczowe terminy

| Termin | Potoczne określenie | Właściwe znaczenie |
|------|-----------------|----------------------|
| Proces w przód | „Dodawanie szumu" | Ustalony łańcuch Markowa `q(x_t \| x_{t-1})`, który niszczy dane. |
| Proces odwrotny | „Odszumianie" | Wyuczony łańcuch `p_θ(x_{t-1} \| x_t)`, który rekonstruuje dane. |
| Harmonogram β | „Drabina szumów" | Wariancja na krok; może być liniowa, cosinusowa lub sigmoidalna. |
| α̅ | „Alpha bar" | Iloczyn skumulowany `∏(1 - β)`; umożliwia bezpośrednie obliczenie `x_t` z `x_0`. |
| Prosta strata | „MSE szumu" | `\|\|ε - ε_θ(x_t, t)\|\|²`; do tej postaci sprowadzają się wszystkie wyprowadzenia wariacyjne. |
| Przewidywanie ε | „Przewiduj szum" | Wyjście sieci to dodany szum; standardowy DDPM. |
| Przewidywanie V | „Przewiduj prędkość" | Wyjście to `α·ε - σ·x`; lepsza kondycja numeryczna w całym zakresie t. |
| DDPM | „Papier źródłowy" | Ho i in. 2020; liniowy β, 1000 kroków, U-Net. |
| DDIM | „Próbnik deterministyczny" | Próbnik spoza klasy Markowa, 20–50 kroków, ten sam cel treningowy. |
| Classifier-free guidance | „CFG" | Łączenie warunkowych i bezwarunkowych prognoz szumu w celu wzmocnienia kondycjonowania. |

## Uwaga produkcyjna: wnioskowanie dyfuzyjne to problem liczby kroków

Oryginalny artykuł DDPM wymaga T=1000 kroków odwrotnych. Nikt nie wdraża tego w produkcji. Każdy praktyczny stos wnioskowania stosuje jedną z trzech strategii — każda z nich bezpośrednio wskazuje źródło opóźnienia:

1. **Szybszy sampler, ten sam model.** DDIM (20–50 kroków), DPM-Solver++ (10–20), UniPC (8–16). Zamiana samplingu to operacja plug-in; wagi `ε_θ` pozostają niezmienione. Zmniejsza opóźnienie 20–50-krotnie.
2. **Destylacja.** Student uczy się odwzorowywać nauczyciela w mniejszej liczbie kroków: destylacja progresywna (2 → 1), Consistency Models (dowolna → 1–4), LCM, SDXL-Turbo, SD3-Turbo. Ogranicza opóźnienie o kolejne 5–10-krotnie, lecz wymaga ponownego treningu.
3. **Buforowanie i kompilacja.** `torch.compile(unet, mode="reduce-overhead")`, backendy TensorRT-LLM, uwaga `xformers`/SDPA, wagi bf16. Zmniejsza opóźnienie na krok około 2-krotnie. Można łączyć z metodami (1) i (2).

W produkcyjnym serwerze dyfuzyjnym budżet obliczeniowy opisuje się tak samo jak w literaturze o LLM: opóźnienie to `num_steps × step_cost + VAE_decode`, a przepustowość to `batch_size × (num_steps × step_cost)⁻¹`. TTFT jest małe (jeden krok); odpowiednikiem TPOT jest pełny czas odpowiedzi, ponieważ z perspektywy użytkownika generowanie obrazu odbywa się „za jednym razem".

## Dalsza lektura

- [Sohl-Dickstein i in. (2015). Głębokie uczenie bez nadzoru z użyciem termodynamiki nierównowagowej](https://arxiv.org/abs/1503.03585) — artykuł wyprzedzający swoje czasy.
- [Ho, Jain, Abbeel (2020). Probabilistyczne modele dyfuzji z odszumianiem](https://arxiv.org/abs/2006.11239) — DDPM.
- [Song, Meng, Ermon (2021). Ukryte modele dyfuzji z odszumianiem](https://arxiv.org/abs/2010.02502) — DDIM, mniejsza liczba kroków.
- [Nichol i Dhariwal (2021). Ulepszony DDPM](https://arxiv.org/abs/2102.09672) — harmonogram cosinusowy, nauczona wariancja.
- [Dhariwal i Nichol (2021). Modele dyfuzyjne przewyższają GAN w syntezie obrazu](https://arxiv.org/abs/2105.05233) — guidance z klasyfikatorem.
- [Ho i Salimans (2022). Classifier-Free Diffusion Guidance](https://arxiv.org/abs/2207.12598) — CFG.
- [Karras i in. (2022). Wyjaśnienie przestrzeni projektowej generatywnych modeli dyfuzyjnych (EDM)](https://arxiv.org/abs/2206.00364) — ujednolicona notacja, najczytelniejsza receptura.
