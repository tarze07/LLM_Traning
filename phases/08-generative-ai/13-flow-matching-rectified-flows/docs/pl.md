# Dopasowanie przepływu i skorygowane przepływy

> Modele dyfuzyjne wymagają 20–50 kroków próbkowania, ponieważ przechodzą zakrzywioną ścieżką od szumu do danych. Dopasowanie przepływu (Lipman i in., 2023) i skorygowany przepływ (Liu i in., 2022) trenowały proste ścieżki. Prostsze ścieżki oznaczają mniej kroków i szybsze wnioskowanie. Stable Diffusion 3, Flux.1 i AudioCraft 2 zostały przełączone na funkcję dopasowywania przepływu w 2024 r.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 8 · 06 (DDPM), Faza 1 · Rachunek różniczkowy
**Czas:** ~45 minut

## Problem

Proces odwrotny DDPM to 1000-krokowy spacer stochastyczny od `N(0, I)` z powrotem do dystrybucji danych. DDIM zwinął go do 20–50 deterministycznych kroków. Chcesz mniej kroków – najlepiej jeden. Blokadą jest to, że ODE rozwiązujące proces odwrotny jest sztywne; ścieżka jest zakrzywiona.

Gdybyś mógł wytrenować model w taki sposób, aby ścieżka od szumu do danych była *linią prostą*, zadziałałby pojedynczy krok Eulera od `t=1` do `t=0`. Dopasowanie przepływu buduje to bezpośrednio: zdefiniuj interpolację liniową od `x_1 ∼ N(0, I)` do `x_0 ∼ data`, trenuj pole wektorowe `v_θ(x, t)`, aby dopasować jego pochodną po czasie, całkuj na podstawie wnioskowania.

Wyprostowany przepływ (Liu 2022) idzie dalej: iteracyjnie prostuj ścieżki za pomocą procedury ponownego przepływu, która wytwarza stopniowo bliższy liniowemu ODE. Po dwóch iteracjach ponownego przepływu, 2-stopniowy próbnik odpowiada 50-stopniowej jakości DDPM.

## Koncepcja

![Dopasowanie przepływu: interpolacja liniowa pomiędzy szumem a danymi](../assets/flow-matching.svg)

### Przepływ w linii prostej

Zdefiniuj:

```
x_t = t · x_1 + (1 - t) · x_0,   t ∈ [0, 1]
```

gdzie `x_0 ~ data` i `x_1 ~ N(0, I)`. Pochodna czasu wzdłuż tej prostej jest stała:

```
dx_t / dt = x_1 - x_0
```

Zdefiniuj pole wektora neuronowego `v_θ(x_t, t)` i wytrenuj je, aby pasowało do tej pochodnej:

```
L = E_{x_0, x_1, t} || v_θ(x_t, t) - (x_1 - x_0) ||²
```

Jest to **strata warunkowego dopasowania przepływu** (Lipman 2023). Szkolenie nie wymaga symulacji: nigdy nie rozwijasz ODE. Po prostu spróbuj `(x_0, x_1, t)` i wykonaj regresję.

### Próbkowanie

Podsumowując, zintegruj poznane pole wektorowe *wstecz* w czasie:

```
x_{t-Δt} = x_t - Δt · v_θ(x_t, t)
```

Zacznij od `x_1 ~ N(0, I)`, krok Eulera w dół do `t=0`.

### Przepływ poprawiony (Liu 2022)

Przepływ w linii prostej działa, ale wyuczone ścieżki *nie są tak naprawdę proste* — zakrzywiają się, ponieważ wiele `x_0` może być odwzorowanych na te same `x_1`. Etap ponownego przepływu skorygowanego przepływu:

1. Model przepływu pociągów v_1 z losowymi parami.
2. Próbka N par `(x_1, x_0)` poprzez całkowanie v_1 z `x_1` do miejsca docelowego `x_0`.
3. Trenuj v_2 na tych sparowanych przykładach. Ponieważ pary są teraz „dopasowane do ODE”, interpolant liniowy między nimi jest rzeczywiście bardziej płaski.
4. Powtórz.

W praktyce 2 iteracje ponownego przepływu prowadzą do stanu prawie liniowego, umożliwiając wnioskowanie w 2-4 krokach. SDXL-Turbo, SD3-Turbo, LCM to modele destylowane z dopasowywania przepływu.

### Dlaczego to zwyciężyło w przypadku zdjęć w 2024 r

Trzy powody:

1. **Szkolenie bez symulacji** — brak rozwijania ODE podczas szkolenia, banalne w realizacji.
2. **Lepsza geometria strat** – proste ścieżki mają stały stosunek sygnału do szumu, podczas gdy DDPM ε-loss ma zły SNR na krawędziach harmonogramu.
3. **Szybsze wnioskowanie** — 4-8 kroków przy jakości SDXL-Turbo; 1 etap z destylacją konsystencji.

## Dopasowanie przepływu vs DDPM — dokładne połączenie

Dopasowanie przepływu ze ścieżką warunkową Gaussa to dyfuzja *z określonym harmonogramem szumów*. Wybierz harmonogram `x_t = α(t) x_0 + σ(t) x_1`, a dopasowanie przepływu przywraca dyfuzję przeformułowaną przez Stratonovicha za pomocą `v = α'·x_0 - σ'·x_1`. Obydwa są algebraicznie równoważne dla ścieżek Gaussa.

Co dodało dopasowanie przepływu: *przejrzystość* celu (zwykła prędkość), czystsze straty i możliwość eksperymentowania z interpolantami innymi niż Gaussa.

## Zbuduj to

`code/main.py` implementuje dopasowanie przepływu 1-D w dwumodowej mieszaninie Gaussa. Pole wektorowe `v_θ(x, t)` to maleńki MLP trenowany z celem liniowym. Podsumowując, zintegruj 1, 2, 4 i 20 kroków Eulera i porównaj jakość próbki.

### Krok 1: strata w treningu

```python
def train_step(x0, net, rng, lr):
    x1 = rng.gauss(0, 1)
    t = rng.random()
    x_t = t * x1 + (1 - t) * x0
    target = x1 - x0
    pred = net_forward(x_t, t)
    loss = (pred - target) ** 2
    # backprop + update
```

### Krok 2: wnioskowanie wieloetapowe

```python
def sample(net, num_steps):
    x = rng.gauss(0, 1)
    for i in range(num_steps):
        t = 1.0 - i / num_steps
        dt = 1.0 / num_steps
        x -= dt * net_forward(x, t)
    return x
```

### Krok 3: porównaj liczbę kroków

Spodziewaj się, że 4-stopniowy próbnik będzie już dorównywał jakością 20-stopniowemu – to duży problem w przypadku opóźnień.

## Pułapki

- **Parametryzacja czasu.** Dopasowanie przepływu wykorzystuje `t ∈ [0, 1]` z `t=0` w przypadku danych, `t=1` w przypadku szumu. DDPM używa `t ∈ [0, T]` z `t=0` przy danych, `t=T` przy szumie. Ten sam kierunek, inna skala. Gazety ciągle się mylą.
- **Wybór harmonogramu.** Linia prosta skorygowanego przepływu jest „harmonogramem dopasowywania przepływu”, ale można zastosować próbkowanie cosinusowe lub logitowo-normalne (robi to SD3) w celu lepszego pokrycia skali.
- **Koszt ponownego przepływu.** Generowanie sparowanego zbioru danych na potrzeby ponownego przepływu oznacza pełne przejście wnioskowania na próbkę. Przepływ wykonuj tylko wtedy, gdy naprawdę potrzebujesz wnioskowania o 1-2 krokach.
- **Wytyczne bez klasyfikatorów nadal obowiązują.** Po prostu zamień ε na v w kombinacji liniowej: `v_cfg = (1+w) v_cond - w v_uncond`.

## Użyj tego

| Przypadek użycia | stos 2026 |
|---------|-----------|
| Zamiana tekstu na obraz, najlepsza jakość | Dopasowanie przepływu: SD3, Flux.1-dev |
| Zamiana tekstu na obraz, 1–4 kroki | Dopasowanie przepływu destylowanego: Flux.1-schnell, SD3-Turbo, SDXL-Turbo |
| Wnioskowanie w czasie rzeczywistym | Destylacja o konsystencji z bazy o dobranym przepływie (LCM, PCM) |
| Generowanie dźwięku | Dopasowanie przepływu: Stable Audio 2.5, AudioCraft 2 |
| Generowanie wideo | Dopasowanie przepływu zmieszane z dyfuzją (Sora, Veo, Stable Video) |
| Nauka / fizyka (trajektorie cząstek, cząsteczki) | Dopasowanie przepływu + równoważne pole wektorowe |

Ilekroć w artykule jest napisane „szybciej niż dyfuzja” w latach 2025–2026, prawie zawsze jest to dopasowanie przepływu + destylacja.

## Wyślij to

Zapisz `outputs/skill-fm-tuner.md`. Skill pobiera specyfikację modelu w stylu dyfuzji i konwertuje ją na konfigurację szkoleniową dopasowującą się do przepływu: wybór harmonogramu, rozkład próbkowania w czasie (jednolity/logit-normalny), optymalizator, plan ponownego przepływu, docelowa liczba kroków, protokół oceny.

## Ćwiczenia

1. **Łatwe.** Uruchom `code/main.py` i porównaj 1-etapowy i 20-etapowy MSE z rzeczywistą dystrybucją danych.
2. **Średni.** Przełącz z jednolitego próbkowania `t` na logit-normalny (pobieranie próbek w połowie t). Czy jakość modelu uległa poprawie?
3. **Trudne.** Zaimplementuj jedną iterację ponownego przepływu: wygeneruj pary (x_0, x_1) poprzez integrację pierwszego modelu, wytrenuj drugi model na parach i porównaj jakość próbek w 1 kroku.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Dopasowanie przepływu | „Dyfuzja liniowa” | Trenuj `v_θ(x, t)`, aby dopasować `x_1 - x_0` wzdłuż interpolanta. |
| Naprawiony przepływ | „Przepływ” | Procedura iteracyjna prostująca wyuczone przepływy. |
| Pole prędkości | "v_θ" | Wynik modelu — kierunek ruchu `x_t`. |
| Interpolant liniowy | „Ścieżka” | `x_t = (1-t)·x_0 + t·x_1`; trywialna pochodna celu. |
| Próbnik Eulera | „Rozwiązywanie ODE pierwszego rzędu” | Najprostszy integrator; działa dobrze, gdy ścieżki są proste. |
| Logit-normalny t | „Próbkowanie SD3” | Skoncentruj `t` próbkowanie w kierunku wartości średnich, gdzie gradienty są najsilniejsze. |
| Destylacja konsystencji | „Próbnik 1-etapowy” | Poinstruuj ucznia, jak zmapować dowolny `x_t` bezpośrednio do `x_0`. |
| CFG z prędkością | „v-CFG” | `v_cfg = (1+w) v_cond - w v_uncond`; ta sama sztuczka, nowa zmienna. |

## Uwaga produkcyjna: Flux.1-schnell najszybciej dopasowuje przepływ

Zwycięskim rozwiązaniem produkcyjnym Flow Match jest Flux.1-schnell — DiT dopasowany pod względem przepływu, destylowany do 1-4 kroków wnioskowania, przy jednoczesnym zachowaniu jakości na poziomie Flux-dev. Notatnik Nielsa „Uruchom Flux na maszynie 8 GB” to referencyjny przepis na wdrożenie: kodowanie T5 + CLIP, kwantyzowane odszumianie MMDiT (w 4 krokach dla schnell vs 50 dla programisty), dekodowanie VAE. Rachunek kosztów:

| Wariant | Kroki | Opóźnienie przy 1024² na L4 | Suma FLOP (względna) |
|--------|-------|--------------------------------------|----------------------|
| Flux.1-dev (surowy) | 50 | ~15 s | 1,0× |
| Flux.1-schnell | 4 | ~1,2 s | 0,08× (12× szybciej) |
| Podstawa SDXL | 30 | ~4 s | 0,25× |
| SDXL-Lightning 2-stopniowy | 2 | ~0,3 s | 0,03× |

Zasada produkcji: **baza dopasowana do przepływu + destylacja = wartość domyślna z 2026 r. dla szybkiej zamiany tekstu na obraz.** Każdy większy dostawca oferuje tę kombinację: SD3-Turbo (SD3 + przepływ + destylacja), Flux-schnell (Flux-dev + prostowanie przepływu prostowanego), CogView-4-Flash. Bazy oparte na czystej dyfuzji istnieją tylko dla starszych punktów kontrolnych.

## Dalsze czytanie

- [Liu, Gong, Liu (2022). Przepływ prosty i szybki: nauka generowania i przesyłania danych za pomocą skorygowanego przepływu](https://arxiv.org/abs/2209.03003) — przepływ poprawiony.
- [Lipman i in. (2023). Dopasowanie przepływu do modelowania generatywnego](https://arxiv.org/abs/2210.02747) — dopasowanie przepływu.
- [Esser i in. (2024). Skalowanie rektyfikowanych transformatorów przepływowych do syntezy obrazów o wysokiej rozdzielczości](https://arxiv.org/abs/2403.03206) — SD3, przepływ prostowany na dużą skalę.
- [Albergo, Vanden-Eijnden (2023). Interpolanty stochastyczne](https://arxiv.org/abs/2303.08797) — ogólne ramy obejmujące dyfuzję FM +.
- [Song i in. (2023). Modele spójności](https://arxiv.org/abs/2303.01469) — 1-etapowa destylacja dyfuzyjna/przepływowa.
- [Sauer i in. (2023). Destylacja dyfuzyjna kontradyktoryjna (SDXL-Turbo)](https://arxiv.org/abs/2311.17042) — wariant turbo.
- [Laboratoria Schwarzwaldu (2024). Modele Flux.1](https://blackforestlabs.ai/announcing-black-forest-labs/) — dopasowanie przepływu w produkcji.