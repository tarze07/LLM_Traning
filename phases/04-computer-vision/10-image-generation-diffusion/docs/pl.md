# Generowanie obrazów — modele dyfuzyjne

> Model dyfuzyjny uczy się odszumiania. Wytrenuj go, aby usuwał niewielką ilość szumu z zaszumionego obrazu, powtórz to wstecz tysiąc razy, i masz generator obrazów.

**Typ:** Build
**Języki:** Python
**Wymagania wstępne:** Faza 4 Lekcja 07 (U-Net), Faza 1 Lekcja 06 (Prawdopodobieństwo), Faza 3 Lekcja 06 (Optymalizatory)
**Czas:** ~75 minut

## Cele nauki

- Wyprowadzić proces zaszumiania w przód `x_0 -> x_1 -> ... -> x_T` i wyjaśnić, dlaczego forma zamknięta `q(x_t | x_0)` zachodzi dla każdego t
- Zaimplementować cel treningowy w stylu DDPM, który regresuje szum dodany w każdym kroku, oraz sampler, który wraca od czystego szumu do obrazu
- Zbudować U-Net warunkowany czasem (wystarczająco mały, aby trenować na CPU), który przewiduje szum dla dowolnego kroku czasowego
- Wyjaśnić różnicę między samplowaniem DDPM i DDIM oraz kiedy stosować każde z nich (lekcja 23 szczegółowo opisuje flow matching i rectified flow)

## Problem

GAN-y generują jednorazowo: szum na wejściu, obraz na wyjściu, jeden przebieg w przód. Są szybkie i trudne w treningu. Modele dyfuzyjne generują iteracyjnie: zaczynają od czystego szumu, odszumiają w małych krokach, obraz się wyłania. Są wolne i łatwe w treningu. W ciągu ostatnich pięciu lat ta druga właściwość okazała się dominująca: każdy mały zespół może wytrenować model dyfuzyjny i otrzymać rozsądne próbki; trening GAN-ów jest rzemiosłem, którego uczysz się przez lata nieudanych przebiegów.

Poza stabilnością treningu, iteracyjna struktura dyfuzji jest tym, co odblokowuje wszystko, co robi dzisiejsze generowanie obrazów: warunkowanie tekstem, inpainting, edycję obrazów, super-rozdzielczość, kontrolowalny styl. Każdy krok pętli samplowania jest miejscem, w którym można wstrzyknąć nowe ograniczenie. To właśnie ten mechanizm powoduje, że Stable Diffusion, Imagen, DALL-E 3, Midjourney i każdy kontrolowalny model obrazu, z którego będziesz korzystać, są oparte na dyfuzji.

Ta lekcja buduje minimalny DDPM: zaszumianie w przód, odszumianie w tył, pętlę treningową. Następna lekcja (Stable Diffusion) podłącza go do systemu produkcyjnego z VAE, koderem tekstu i classifier-free guidance.

## Koncepcja

### Proces w przód

Weź obraz `x_0`. Dodaj niewielką ilość szumu gaussowskiego, aby otrzymać `x_1`. Dodaj jeszcze odrobinę, aby otrzymać `x_2`. Kontynuuj przez T kroków, aż `x_T` będzie praktycznie nieodróżnialne od czystego szumu gaussowskiego.

```
q(x_t | x_{t-1}) = N(x_t; sqrt(1 - beta_t) * x_{t-1},  beta_t * I)
```

`beta_t` to harmonogram małych wariancji, zazwyczaj liniowy od 0.0001 do 0.02 na przestrzeni T=1000 kroków. Każdy krok lekko zmniejsza sygnał i wstrzykuje świeży szum.

### Skok w formie zamkniętej

Dodawanie szumu krok po kroku to łańcuch Markowa, ale matematyka się "zwija": można wylosować `x_t` bezpośrednio z `x_0` w jednym kroku.

```
Define alpha_t = 1 - beta_t
Define alpha_bar_t = prod_{s=1..t} alpha_s

Then:
  q(x_t | x_0) = N(x_t; sqrt(alpha_bar_t) * x_0,  (1 - alpha_bar_t) * I)

Equivalently:
  x_t = sqrt(alpha_bar_t) * x_0 + sqrt(1 - alpha_bar_t) * epsilon
  where epsilon ~ N(0, I)
```

To jedno równanie jest całym powodem, dla którego dyfuzja jest praktyczna. Podczas treningu wybierasz losowe `t`, samplujesz `x_t` bezpośrednio z `x_0` i trenujesz w jednym kroku — bez symulowania całego łańcucha Markowa.

### Proces w tył

Proces w przód jest ustalony. Proces w tył `p(x_{t-1} | x_t)` to to, czego uczy się sieć neuronowa. Modele dyfuzyjne nie przewidują `x_{t-1}` bezpośrednio; przewidują szum `epsilon` dodany w kroku t, a matematyka wyprowadza z niego `x_{t-1}`.

```mermaid
flowchart LR
    X0["x_0<br/>(clean image)"] --> Q1["q(x_t|x_0)<br/>add noise"]
    Q1 --> XT["x_t<br/>(noisy)"]
    XT --> MODEL["model(x_t, t)"]
    MODEL --> EPS["predicted epsilon"]
    EPS --> LOSS["MSE against<br/>true epsilon"]

    XT -.->|sampling| STEP["p(x_{t-1}|x_t)"]
    STEP -.-> XT1["x_{t-1}"]
    XT1 -.->|repeat 1000x| X0S["x_0 (sampled)"]

    style X0 fill:#dcfce7,stroke:#16a34a
    style MODEL fill:#fef3c7,stroke:#d97706
    style LOSS fill:#fecaca,stroke:#dc2626
    style X0S fill:#dbeafe,stroke:#2563eb
```

### Funkcja straty treningowej

Dla każdego kroku treningowego:

1. Wylosuj prawdziwy obraz `x_0`.
2. Wylosuj krok czasowy `t` z rozkładu jednostajnego na [1, T].
3. Wylosuj szum `epsilon ~ N(0, I)`.
4. Wyznacz `x_t = sqrt(alpha_bar_t) * x_0 + sqrt(1 - alpha_bar_t) * epsilon`.
5. Przewidź `epsilon_theta(x_t, t)` za pomocą sieci.
6. Minimalizuj `|| epsilon - epsilon_theta(x_t, t) ||^2`.

I to wszystko. Sieć neuronowa uczy się przewidywać szum w dowolnym kroku czasowym. Funkcja straty to MSE. Nie ma żadnej gry adwersarialnej, żadnego collapse'u, żadnych oscylacji.

### Sampler (DDPM)

Aby generować: zacznij od `x_T ~ N(0, I)` i idź wstecz, krok po kroku.

```
for t = T, T-1, ..., 1:
    eps = model(x_t, t)
    x_{t-1} = (1 / sqrt(alpha_t)) * (x_t - (beta_t / sqrt(1 - alpha_bar_t)) * eps) + sqrt(beta_t) * z
    where z ~ N(0, I) if t > 1, else 0
return x_0
```

Kluczowe jest to, że choć rozkład warunkowy procesu odwrotnego nie jest znany w formie zamkniętej w ogólnym przypadku, dla tego konkretnego gaussowskiego procesu w przód — jest. Te koślawo wyglądające współczynniki to to, co daje reguła Bayesa.

### Dlaczego 1000 kroków

Harmonogram szumu w przód jest wybrany tak, aby każdy krok dodawał akurat tyle szumu, że krok odwrotny jest prawie gaussowski. Za mało kroków — krok odwrotny jest daleki od gaussowskiego, sieć nie może go dobrze modelować. Za dużo kroków — samplowanie staje się kosztowne przy malejących zyskach. T=1000 z liniowym harmonogramem to wartość domyślna w DDPM.

### DDIM: 20x szybsze samplowanie

Trening jest taki sam. Zmienia się samplowanie. DDIM (Song i in., 2020) definiuje deterministyczny proces odwrotny, który pomija kroki czasowe bez ponownego treningu. Samplowanie w 50 krokach z DDIM daje jakość zbliżoną do 1000-krokowego DDPM. Każdy system produkcyjny używa DDIM lub jeszcze szybszego wariantu (DPM-Solver, Euler ancestral).

### Warunkowanie czasem

Sieć `epsilon_theta(x_t, t)` musi wiedzieć, który krok czasowy odszumia. Współczesne modele dyfuzyjne wstrzykują `t` za pomocą sinusoidalnych embeddingów czasu (ta sama idea co positional encoding w transformerach), które są dodawane do map cech na każdym poziomie U-Net.

```
t_embedding = sinusoidal(t)
feature_map += MLP(t_embedding)
```

Bez warunkowania czasem sieć musiałaby zgadywać poziom szumu z samego obrazu, co działa, ale jest dużo mniej efektywne pod względem liczby próbek.

## Zbuduj to

### Krok 1: Harmonogram szumu

```python
import torch

def linear_beta_schedule(T=1000, beta_start=1e-4, beta_end=2e-2):
    return torch.linspace(beta_start, beta_end, T)


def precompute_schedule(betas):
    alphas = 1.0 - betas
    alphas_cumprod = torch.cumprod(alphas, dim=0)
    return {
        "betas": betas,
        "alphas": alphas,
        "alphas_cumprod": alphas_cumprod,
        "sqrt_alphas_cumprod": torch.sqrt(alphas_cumprod),
        "sqrt_one_minus_alphas_cumprod": torch.sqrt(1.0 - alphas_cumprod),
        "sqrt_recip_alphas": torch.sqrt(1.0 / alphas),
    }

schedule = precompute_schedule(linear_beta_schedule(T=1000))
```

Oblicz raz, indeksuj podczas treningu i samplowania.

### Krok 2: Dyfuzja w przód (q_sample)

```python
def q_sample(x0, t, noise, schedule):
    sqrt_a = schedule["sqrt_alphas_cumprod"][t].view(-1, 1, 1, 1)
    sqrt_one_minus_a = schedule["sqrt_one_minus_alphas_cumprod"][t].view(-1, 1, 1, 1)
    return sqrt_a * x0 + sqrt_one_minus_a * noise
```

Jednolinijkowa forma zamknięta. `t` to wsad kroków czasowych, jeden na obraz w batchu.

### Krok 3: Mały U-Net warunkowany czasem

```python
import torch.nn as nn
import torch.nn.functional as F
import math

def timestep_embedding(t, dim=64):
    half = dim // 2
    freqs = torch.exp(-math.log(10000) * torch.arange(half, device=t.device) / half)
    args = t[:, None].float() * freqs[None]
    emb = torch.cat([args.sin(), args.cos()], dim=-1)
    return emb


class TinyUNet(nn.Module):
    def __init__(self, img_channels=3, base=32, t_dim=64):
        super().__init__()
        self.t_mlp = nn.Sequential(
            nn.Linear(t_dim, base * 4),
            nn.SiLU(),
            nn.Linear(base * 4, base * 4),
        )
        self.t_dim = t_dim
        self.enc1 = nn.Conv2d(img_channels, base, 3, padding=1)
        self.enc2 = nn.Conv2d(base, base * 2, 4, stride=2, padding=1)
        self.mid = nn.Conv2d(base * 2, base * 2, 3, padding=1)
        self.dec1 = nn.ConvTranspose2d(base * 2, base, 4, stride=2, padding=1)
        self.dec2 = nn.Conv2d(base * 2, img_channels, 3, padding=1)
        self.time_proj = nn.Linear(base * 4, base * 2)

    def forward(self, x, t):
        t_emb = timestep_embedding(t, self.t_dim)
        t_emb = self.t_mlp(t_emb)
        t_proj = self.time_proj(t_emb)[:, :, None, None]

        h1 = F.silu(self.enc1(x))
        h2 = F.silu(self.enc2(h1)) + t_proj
        h3 = F.silu(self.mid(h2))
        d1 = F.silu(self.dec1(h3))
        d2 = torch.cat([d1, h1], dim=1)
        return self.dec2(d2)
```

Dwupoziomowy U-Net z warunkowaniem czasem wstrzykiwanym w bottlenecku. Zwiększ głębokość i szerokość dla prawdziwych obrazów.

### Krok 4: Pętla treningowa

```python
def train_step(model, x0, schedule, optimizer, device, T=1000):
    model.train()
    x0 = x0.to(device)
    bs = x0.size(0)
    t = torch.randint(0, T, (bs,), device=device)
    noise = torch.randn_like(x0)
    x_t = q_sample(x0, t, noise, schedule)
    pred = model(x_t, t)
    loss = F.mse_loss(pred, noise)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    return loss.item()
```

To cała pętla treningowa. Bez gry GAN, bez specjalnej funkcji straty, jedno wywołanie MSE.

### Krok 5: Sampler (DDPM)

```python
@torch.no_grad()
def sample(model, schedule, shape, T=1000, device="cpu"):
    model.eval()
    x = torch.randn(shape, device=device)
    betas = schedule["betas"].to(device)
    sqrt_one_minus_a = schedule["sqrt_one_minus_alphas_cumprod"].to(device)
    sqrt_recip_alphas = schedule["sqrt_recip_alphas"].to(device)

    for t in reversed(range(T)):
        t_batch = torch.full((shape[0],), t, dtype=torch.long, device=device)
        eps = model(x, t_batch)
        coef = betas[t] / sqrt_one_minus_a[t]
        mean = sqrt_recip_alphas[t] * (x - coef * eps)
        if t > 0:
            x = mean + torch.sqrt(betas[t]) * torch.randn_like(x)
        else:
            x = mean
    return x
```

1000 przebiegów w przód, aby wyprodukować jeden batch próbek. W rzeczywistym kodzie zamieniłbyś to na 50-krokowy sampler DDIM.

### Krok 6: Sampler DDIM (deterministyczny, ~20x szybszy)

```python
@torch.no_grad()
def sample_ddim(model, schedule, shape, steps=50, T=1000, device="cpu", eta=0.0):
    model.eval()
    x = torch.randn(shape, device=device)
    alphas_cumprod = schedule["alphas_cumprod"].to(device)

    ts = torch.linspace(T - 1, 0, steps + 1).long()
    for i in range(steps):
        t = ts[i]
        t_prev = ts[i + 1]
        t_batch = torch.full((shape[0],), t, dtype=torch.long, device=device)
        eps = model(x, t_batch)
        a_t = alphas_cumprod[t]
        a_prev = alphas_cumprod[t_prev] if t_prev >= 0 else torch.tensor(1.0, device=device)
        x0_pred = (x - torch.sqrt(1 - a_t) * eps) / torch.sqrt(a_t)
        sigma = eta * torch.sqrt((1 - a_prev) / (1 - a_t) * (1 - a_t / a_prev))
        dir_xt = torch.sqrt(1 - a_prev - sigma ** 2) * eps
        noise = sigma * torch.randn_like(x) if eta > 0 else 0
        x = torch.sqrt(a_prev) * x0_pred + dir_xt + noise
    return x
```

`eta=0` jest w pełni deterministyczne (to samo wejściowe ziarno szumu zawsze daje to samo wyjście). `eta=1` odtwarza DDPM.

## Użyj tego

Do pracy produkcyjnej użyj `diffusers`:

```python
from diffusers import DDPMScheduler, UNet2DModel

unet = UNet2DModel(sample_size=32, in_channels=3, out_channels=3, layers_per_block=2)
scheduler = DDPMScheduler(num_train_timesteps=1000)
```

Biblioteka udostępnia gotowe schedulery (DDPM, DDIM, DPM-Solver, Euler, Heun), konfigurowalne U-Nety, pipeline'y do text-to-image i image-to-image oraz pomocnicze narzędzia do fine-tuningu LoRA.

Do badań `k-diffusion` (Katherine Crowson) ma najbardziej wierne implementacje referencyjne i najlepsze warianty samplowania.

## Wypuść to

Ta lekcja produkuje:

- `outputs/prompt-diffusion-sampler-picker.md` — prompt, który wybiera DDPM / DDIM / DPM-Solver / Euler na podstawie docelowej jakości, budżetu czasowego oraz typu warunkowania.
- `outputs/skill-noise-schedule-designer.md` — skill, który produkuje liniowy, kosinusowy lub sigmoidalny harmonogram beta dla danego T i docelowego poziomu zniekształcenia, wraz z diagnostycznymi wykresami współczynnika sygnał-szum (signal-to-noise ratio) w czasie.

## Ćwiczenia

1. **(Łatwe)** Zwizualizuj proces w przód: weź jeden obraz i narysuj `x_t` dla `t in [0, 100, 250, 500, 750, 1000]`. Sprawdź, że `x_1000` wygląda jak czysty szum gaussowski.
2. **(Średnie)** Wytrenuj TinyUNet na zbiorze syntetycznych okręgów (synthetic-circles) przez 20 epok i wygeneruj 16 okręgów. Porównaj samplowanie DDPM (1000 kroków) i DDIM (50 kroków) — czy z tego samego ziarna szumu (seed) produkują podobne obrazy?
3. **(Trudne)** Zaimplementuj kosinusowy harmonogram szumu (Nichol & Dhariwal, 2021): `alpha_bar_t = cos^2((t/T + s) / (1 + s) * pi / 2)`. Wytrenuj ten sam model z harmonogramem liniowym i kosinusowym i pokaż, że harmonogram kosinusowy daje lepsze próbki przy małej liczbie kroków.

## Kluczowe terminy

| Termin | Co się mówi | Co to faktycznie znaczy |
|------|----------------|----------------------|
| Proces w przód (forward process) | "Dodawanie szumu w czasie" | Ustalony łańcuch Markowa, który zniekształca obraz w szum gaussowski przez T kroków |
| Proces w tył (reverse process) | "Odszumianie krok po kroku" | Wyuczony rozkład, który wraca od szumu do obrazu |
| Predykcja epsilon | "Przewidywanie szumu" | Cel treningowy: `epsilon_theta(x_t, t)` przewiduje szum dodany w kroku t |
| Harmonogram beta | "Wielkości szumu" | Sekwencja T małych wariancji, które definiują, ile szumu wchodzi w każdym kroku |
| alpha_bar_t | "Skumulowany współczynnik zachowania" | Iloczyn (1 - beta_s) do czasu t; większe t oznacza mniej pozostałego sygnału |
| Sampler DDPM | "Ancestralny, stochastyczny" | Próbkuje każde x_{t-1} z jego warunkowego rozkładu gaussowskiego; 1000 kroków |
| Sampler DDIM | "Deterministyczny, szybki" | Przepisuje samplowanie jako deterministyczne ODE; 20-100 kroków o podobnej jakości |
| Warunkowanie czasem | "Powiedz modelowi, jakie jest t" | Sinusoidalny embedding t wstrzykiwany do U-Net, aby znał poziom szumu |

## Dalsze materiały

- [Denoising Diffusion Probabilistic Models (Ho i in., 2020)](https://arxiv.org/abs/2006.11239) — artykuł, który uczynił dyfuzję praktyczną i pobił GAN-y w metryce FID
- [Improved DDPM (Nichol & Dhariwal, 2021)](https://arxiv.org/abs/2102.09672) — harmonogram kosinusowy i v-parametryzacja
- [DDIM (Song, Meng, Ermon, 2020)](https://arxiv.org/abs/2010.02502) — deterministyczny sampler, który umożliwił wnioskowanie w czasie rzeczywistym
- [Elucidating the Design Space of Diffusion (Karras i in., 2022)](https://arxiv.org/abs/2206.00364) — zunifikowany przegląd wszystkich decyzji projektowych dotyczących dyfuzji; obecnie najlepsze źródło referencyjne
