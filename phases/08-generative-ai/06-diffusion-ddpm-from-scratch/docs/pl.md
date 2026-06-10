# Modele dyfuzyjne — DDPM od podstaw

> Ho, Jain, Abbeel (2020) podali w tej dziedzinie przepis, z którego nie można zrezygnować. Zniszcz dane za pomocą hałasu w tysiącu małych kroków. Wytrenuj jedną sieć neuronową, aby przewidywała hałas. Odwróć proces przy wnioskowaniu. Obecnie każdy główny model obrazu, wideo, 3D i muzyki działa w tej pętli, być może z dodatkowymi sztuczkami dopasowywania przepływu lub spójności.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 3 · 02 (podpórka), Faza 8 · 02 (VAE)
**Czas:** ~75 minut

## Problem

Potrzebujesz próbnika dla `p_data(x)`. Sieci GAN grają w grę minimax, która często się różni. VAE wytwarzają rozmyte próbki z dekodera Gaussa. Tak naprawdę potrzebujesz celu treningowego, którym jest (a) pojedyncza stabilna strata (bez punktu siodłowego, bez minimaksu), (b) dolna granica `log p(x)` (abyś miał prawdopodobieństwo) oraz (c) próbki odpowiadające jakości SOTA.

Sohl-Dickstein i in. (2015) mieli teoretyczną odpowiedź: zdefiniuj łańcuch Markowa `q(x_t | x_{t-1})`, który stopniowo dodaje szum Gaussa, i wytrenuj łańcuch odwrotny `p_θ(x_{t-1} | x_t)` do usuwania szumów. Ho, Jain, Abbeel (2020) wykazali, że stratę można uprościć do jednej linii – przewidzieć hałas – i uporządkować matematykę. W 2020 roku była to ciekawostka. W 2021 roku wyprodukowała najnowocześniejsze próbki. W 2022 roku stał się stabilną dyfuzją. W 2026 roku będzie to podłoże.

## Koncepcja

![DDPM: szum w przód, odszumianie w tył](../assets/ddpm.svg)

**Przebieg procesu `q`.** Dodaj szum Gaussa małymi krokami `T`. Zamknięta forma — powód, dla którego matematyka jest łatwa do zrozumienia — polega na tym, że krok skumulowany jest również Gaussa:

```
q(x_t | x_0) = N( sqrt(α̅_t) · x_0,  (1 - α̅_t) · I )
```

gdzie `α̅_t = ∏_{s=1..t} (1 - β_s)` dla harmonogramu `β_t`. Wybierz `β_t` od 1e-4 do 0,02 liniowo przez T=1000 kroków, a wartość `x_T` wynosi w przybliżeniu `N(0, I)`.

**Proces odwrotny `p_θ`.** Poznaj sieć neuronową `ε_θ(x_t, t)`, która przewiduje dodany szum. Biorąc pod uwagę `x_t`, odszumij poprzez:

```
x_{t-1} = (1 / sqrt(α_t)) · ( x_t - (β_t / sqrt(1 - α̅_t)) · ε_θ(x_t, t) )  +  σ_t · z
```

gdzie `σ_t` to `sqrt(β_t)` lub wyuczona wariancja. Wyrażenie jest brzydkie, ale to tylko algebra — rozwiązanie `x_{t-1}` biorąc pod uwagę późniejsze `q(x_{t-1} | x_t, x_0)` i zastępując `x_0` jego przewidywaną wartością szumu.

**Strata treningowa.**

```
L_simple = E_{x_0, t, ε} [ || ε - ε_θ( sqrt(α̅_t) · x_0 + sqrt(1 - α̅_t) · ε,  t ) ||² ]
```

Próbkuj `x_0` z danych, wybierz losowy `t`, próbkę `ε ~ N(0, I)`, oblicz zaszumiony `x_t` za jednym razem w formie zamkniętej i wykonaj regresję szumu. Jedna strata, żadnego minimaxu, żadnego KL, żadnych trików reparametryzacyjnych.

**Próbkowanie.** Rozpocznij `x_T ~ N(0, I)`. Wykonaj krok odwrotny od `t = T` do `1`. Zrobione.

## Dlaczego to działa

Trzy intuicje:

1. **Odszumianie jest łatwe; generowanie jest trudne.** W `t=T` dane to czysty szum — sieć musi rozwiązać trywialny problem. W `t=0` sieć musi oczyścić tylko kilka pikseli. Na poziomie pośrednim `t` problem jest trudny, ale sieć ma wiele gradientów przepływających przez te same ciężary na każdym poziomie hałasu.

2. **Ukryte dopasowanie wyników.** Vincent (2011) udowodnił, że przewidywanie hałasu jest równoznaczne z oszacowaniem `∇_x log q(x_t | x_0)`, *wyniku*. Odwrotna SDE wykorzystuje ten wynik do poruszania się w górę gradientu gęstości — losowego spaceru z przewodnikiem w kierunku regionów o wysokim prawdopodobieństwie.

3. **ELBO redukuje się do prostego MSE.** Pełna wariacyjna dolna granica ma człon KL na krok czasowy. Dzięki parametryzacji DDPM te terminy KL upraszczają MSE w zakresie przewidywania hałasu za pomocą określonych współczynników; Ho obniżył współczynniki (nazywając to „prostą” stratą), a jakość *poprawiła się*.

## Zbuduj to

`code/main.py` implementuje DDPM 1-D. Dane są mieszaniną dwóch trybów. „Sieć” to mały MLP, który pobiera `(x_t, t)` i generuje przewidywany szum. Trening to strata jednoliniowa. Próbkowanie iteruje odwrotny łańcuch.

### Krok 1: harmonogram przekazania (formularz zamknięty)

```python
betas = [1e-4 + (0.02 - 1e-4) * t / (T - 1) for t in range(T)]
alphas = [1 - b for b in betas]
alpha_bars = []
cum = 1.0
for a in alphas:
    cum *= a
    alpha_bars.append(cum)
```

### Krok 2: próbka `x_t` za jednym razem

```python
def forward_sample(x0, t, alpha_bars, rng):
    a_bar = alpha_bars[t]
    eps = rng.gauss(0, 1)
    x_t = math.sqrt(a_bar) * x0 + math.sqrt(1 - a_bar) * eps
    return x_t, eps
```

### Krok 3: jeden krok szkoleniowy

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

W przypadku problemu 1-D z 40 krokami czasowymi i 24-jednostkowym MLP, uczy się to mieszaniny dwóch trybów w ~ 200 epokach.

## Warunkowanie czasu

Sieć musi wiedzieć, który krok czasowy odszumia. Dwie standardowe opcje:

- **Osadzanie sinusoidalne.** Podobnie jak kodowanie pozycyjne transformatora. `embed(t) = [sin(t/ω_0), cos(t/ω_0), sin(t/ω_1), ...]`. Przejdź przez MLP i wyślij do sieci.
- **Kondycjonowanie według normy filmowej/grupowej.** Osadzanie projektu w skali/odchyleniu na kanał (FiLM) w każdym bloku.

Nasz kod zabawki wykorzystuje sinusoidalny → concat. Produkcyjne sieci U-Net wykorzystują FiLM.

## Pułapki

- **Harmonogram ma duże znaczenie.** Liniowy `β` jest domyślnym ustawieniem DDPM, ale harmonogram cosinusowy (Nichol i Dhariwal, 2021) zapewnia lepszy FID dla tych samych obliczeń. Zmień harmonogramy, jeśli jakość się zatrzyma.
- **Osadzanie kroków czasowych jest delikatne.** Przekazywanie surowego `t` jako elementu pływającego działa w przypadku zabawek 1-D, ale nie w przypadku obrazów; zawsze używaj odpowiedniego osadzania.
- **Przewidywanie V a przewidywanie ε.** W przypadku wąskich reżimów (bardzo małe lub bardzo duże t) `ε` ma słaby stosunek sygnału do szumu. Predykcja V (`v = α·ε - σ·x`) jest bardziej stabilna; Używają go SDXL, SD3 i Flux.
- **Wskazówki bez klasyfikatorów.** Podczas wnioskowania oblicz zarówno warunkowe, jak i bezwarunkowe `ε`, a następnie `ε_cfg = (1 + w) · ε_cond - w · ε_uncond` za pomocą `w ≈ 3-7`. Omówione w lekcji 08.
- **1000 kroków to dużo.** Produkcja wykorzystuje DDIM (20-50 kroków), DPM-Solver (10-20 kroków) lub destylację (1-4 kroki). Zobacz lekcję 12.

## Użyj tego

| Rola | Typowy stack w 2026 r. |
|------|----------------------|
| Rozproszenie obrazu w przestrzeni pikseli (mały, zabawka) | DDPM + U-Net |
| Utajone rozpowszechnianie obrazu | Enkoder VAE + U-Net lub DiT (lekcja 07) |
| Ukryta dyfuzja wideo | Czasoprzestrzenny DiT (Sora, Veo, WAN) |
| Utajona dyfuzja dźwięku | Kodek + transformator dyfuzyjny |
| Nauka (cząsteczki, białka, fizyka) | Rozproszenie równoważne (EDM, RFdiffusion, AlphaFold3) |

Dyfuzja jest uniwersalnym szkieletem generatywnym. Dopasowywanie przepływu (lekcja 13) to konkurent na lata 2024–2026, który zwykle wygrywa pod względem szybkości wnioskowania przy tej samej jakości.

## Wyślij to

Zapisz `outputs/skill-diffusion-trainer.md`. Umiejętność wykorzystuje zbiór danych + oblicza budżet i wyniki: harmonogram (liniowy/cosinus/esigmoidalny), cel przewidywania (ε/v/x), liczbę kroków, skalę wskazówek, rodzinę próbników i protokół ewaluacji.

## Ćwiczenia

1. **Łatwe.** Zmień T z 40 na 10 w `code/main.py`. Jak pogarsza się jakość próbki (wizualny histogram wyników)? W jakim T zapada się struktura dwumodowa?
2. **Średni.** Przełącz z przewidywania ε na przewidywanie v. Powtórz krok odwrotny. Porównaj ostateczną jakość próbki.
3. **Trudne.** Dodaj wskazówki wolne od klasyfikatorów. Warunek na etykiecie zajęć `c ∈ {0, 1}`, upuść go w 10% przypadków podczas szkolenia, a podczas próbkowania użyj `ε = (1+w)·ε_cond - w·ε_uncond`. Zmierz współczynnik trafień w trybie warunkowym w `w = 0, 1, 3, 7`.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Dalszy proces | „Dodawanie szumu” | Naprawiono łańcuch Markowa `q(x_t \| x_{t-1})`, który niszczy dane. |
| Proces odwrotny | „Odszumianie” | Wyuczony łańcuch `p_θ(x_{t-1} \| x_t)`, który rekonstruuje dane. |
| harmonogram β | „Drabina szumów” | Odchylenie na krok; liniowy, cosinusowy lub sigmoidalny. |
| α̅ | „Pasek Alfa” | Produkt skumulowany `∏(1 - β)`; daje formę zamkniętą `x_t` z `x_0`. |
| Prosta strata | „MSE o hałasie” | `\|\|ε - ε_θ(x_t, t)\|\|²`; wszystkie wyprowadzenia wariacyjne do tego się sprowadzają. |
| ε-przewidywanie | „Przewiduj hałas” | Wyjście to dodany szum; standardowy DDPM. |
| V-przewidywanie | „Przewiduj prędkość” | Dane wyjściowe to `α·ε - σ·x`; lepsza kondycjonowanie w całym t. |
| DDPM | „Papier” | Ho i in. 2020; liniowy β, 1000 kroków, U-Net. |
| DDIM | „Próbnik deterministyczny” | Próbnik inny niż Markowa, 20–50 kroków, ten sam cel szkolenia. |
| Wskazówki bez klasyfikatorów | "CFG" | Łącz warunkowe i bezwarunkowe prognozy hałasu, aby wzmocnić kondycjonowanie. |

## Uwaga producenta: wnioskowanie o dyfuzji to problem związany z liczbą kroków

Papier DDPM wykonuje T=1000 kroków odwrotnych. Nikt tego nie wysyła do produkcji. Każdy prawdziwy stos wnioskowania wybiera jedną z trzech strategii — a każda z nich w sposób przejrzysty odwzorowuje produkcyjne ramy określające, „skąd pochodzi opóźnienie”:

1. **Szybszy sampler, ten sam model.** DDIM (20-50 kroków), DPM-Solver++ (10-20), UniPC (8-16). Wymiana pętli zwrotnej metodą drop-in; wytrenowane wagi `ε_θ` pozostają nietknięte. Zmniejsza opóźnienia 20–50×.
2. **Destylacja.** Przeszkol ucznia tak, aby dopasowywał się do nauczyciela w mniejszej liczbie kroków: Destylacja progresywna (2 → 1), Modele konsystencji (dowolne → 1-4), LCM, SDXL-Turbo, SD3-Turbo. Skraca opóźnienia o kolejne 5–10×, wymaga ponownego szkolenia.
3. **Buforowanie i kompilacja.** `torch.compile(unet, mode="reduce-overhead")`, backendy dyfuzyjne TensorRT-LLM, uwaga `xformers`/SDPA, wagi bf16. Zmniejsza opóźnienie na krok ~2×. Stosy z (1) i (2).

W przypadku produkcyjnego serwera dyfuzyjnego rozmowa o budżecie jest taka sama, jak opisano w literaturze produkcyjnej dla LLM: opóźnienie wynosi `num_steps × step_cost + VAE_decode`, przepustowość wynosi `batch_size × (num_steps × step_cost)^-1`. TTFT jest mały (jeden krok); Odpowiednik TPOT to pełny czas reakcji, ponieważ z punktu widzenia użytkownika generowanie obrazu odbywa się „wszystko na raz”.

## Dalsze czytanie

- [Sohl-Dickstein i in. (2015). Głębokie uczenie się bez nadzoru przy użyciu termodynamiki nierównowagowej](https://arxiv.org/abs/1503.03585) — publikacja wyprzedzająca swoje czasy.
- [Ho, Jain, Abbeel (2020). Modele probabilistyczne odszumiania dyfuzji](https://arxiv.org/abs/2006.11239) — DDPM.
- [Pieśń, Meng, Ermon (2021). Ukryte modele odszumiania dyfuzji](https://arxiv.org/abs/2010.02502) — DDIM, mniej kroków.
- [Nichol i Dhariwal (2021). Ulepszony DDPM](https://arxiv.org/abs/2102.09672) — harmonogram cosinus, wyuczona wariancja.
- [Dhariwal i Nichol (2021). Modele dyfuzyjne pokonują GAN w syntezie obrazu](https://arxiv.org/abs/2105.05233) — wskazówki dotyczące klasyfikatora.
- [Ho i Salimans (2022). Wytyczne dotyczące rozpowszechniania bez klasyfikatorów](https://arxiv.org/abs/2207.12598) — CFG.
- [Karras i in. (2022). Wyjaśnienie przestrzeni projektowej modeli generatywnych opartych na dyfuzji (EDM)](https://arxiv.org/abs/2206.00364) — ujednolicona notacja, najczystsza receptura.