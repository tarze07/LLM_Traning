# Autoenkodery i autoenkodery wariacyjne (VAE)

> Zwykły autoenkoder kompresuje, a następnie rekonstruuje. Zapamiętuje. Nie generuje. Dodaj jedną sztuczkę — nadaj kodowi wygląd gaussowski — a otrzymasz próbnik. Dzięki tej pojedynczej sztuczce, ponownej parametryzacji `z = μ + σ·ε`, każdy model obrazu z utajoną dyfuzją i dopasowaniem przepływu, którego używasz w 2026 r., ma na wejściu VAE.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 3 · 02 (backprop), Faza 3 · 07 (CNN), Faza 8 · 01 (taksonomia)
**Czas:** ~75 minut

## Problem

Skompresuj 784-pikselową cyfrę MNIST do 16-cyfrowego kodu, a następnie zrekonstruuj. Zwykły autoenkoder będzie asem w rekonstrukcji MSE, ale przestrzeń kodu to nierówny bałagan. Wybierz losowy punkt w przestrzeni kodu, zdekoduj go, a otrzymasz szum. Nie posiada próbnika. Jest to model kompresyjny ubrany.

Tak naprawdę chcesz: (a) przestrzeń kodu to czysta, gładka dystrybucja, z której możesz próbkować — powiedzmy izotropowy gaussowski `N(0, I)`, (b) dekodowanie dowolnej próbki daje wiarygodną cyfrę oraz (c) koder i dekoder nadal dobrze kompresują. Trzy gole, jedna architektura, jedna porażka.

VAE firmy Kingma 2013 rozwiązuje ten problem, ucząc koder tak, aby generował *dystrybucję* `q(z|x) = N(μ(x), σ(x)²)`, przeciągając tę dystrybucję w stronę wcześniejszej `N(0, I)` poprzez karę KL, a następnie próbkowanie `z` z `q(z|x)` przed dekodowaniem. W momencie wnioskowania usuń koder, próbkuj `z ~ N(0, I)`, dekoduj. Kara KL wymusza uporządkowanie przestrzeni kodu.

W 2026 r. VAE rzadko są dostarczane jako samodzielne urządzenia — zostały zdeklasowane przez dyfuzję pod względem jakości surowego obrazu — ale są wybieranym koderem dla każdego modelu z utajoną dyfuzją (SD 1/2/XL/3, Flux, AudioCraft). Poznaj VAE, a poznasz niewidzialną pierwszą warstwę każdego potoku obrazu, którego używasz.

## Koncepcja

![Autoencoder kontra VAE: sztuczka z ponowną parametryzacją](../assets/vae.svg)

**Autoenkoder.** `z = encoder(x)`, `x̂ = decoder(z)`, strata = `||x - x̂||²`. Przestrzeń kodu nieustrukturyzowana.

**Koder VAE.** Wyprowadza dwa wektory: `μ(x)` i `log σ²(x)`. Definiują one `q(z|x) = N(μ, diag(σ²))`.

**Sztuczka ponownej parametryzacji.** Próbkowanie z `q(z|x)` nie jest różniczkowalne. Przepisz przykład jako `z = μ + σ·ε` gdzie `ε ~ N(0, I)`. Teraz `z` jest funkcją deterministyczną `(μ, σ)` plus szum nieparametryczny — gradienty przepływają przez `μ` i `σ`.

**Strata.** Dolna granica dowodu (ELBO), dwa terminy:

```
loss = reconstruction + β · KL[q(z|x) || N(0, I)]
     = ||x - x̂||²  + β · Σ_i ( σ_i² + μ_i² - log σ_i² - 1 ) / 2
```

Rekonstrukcja popycha `x̂` w kierunku `x`. KL wypycha `q(z|x)` w stronę wcześniejszego. Handlują. Małe β (<1) = ostrzejsze próbki, przestrzeń kodowa mniejsza od Gaussa. Duże β (>1) = czystsza przestrzeń kodu, bardziej rozmyte próbki. β-VAE (Higgins 2017) rozsławiło to pokrętło i zapoczątkowało badania nad rozplątaniem.

**Próbkowanie.** Podsumowując: pobierz `z ~ N(0, I)`, przekaż dalej przez dekoder. Jedno przejście do przodu — bez próbkowania iteracyjnego, takiego jak dyfuzja.

## Zbuduj to

`code/main.py` implementuje mały VAE bez numpy i latarki. Dane wejściowe to 8-wymiarowe dane syntetyczne pochodzące z 2-składnikowej mieszaniny Gaussa w formacie 8-D. Koder i dekoder to pojedyncze MLP z warstwą ukrytą. Realizujemy aktywację tanh, podanie do przodu, stratę i ręcznie napisane podanie do tyłu. Nie produkcja – pedagogika.

### Krok 1: koder do przodu

```python
def encode(x, enc):
    h = tanh(add(matmul(enc["W1"], x), enc["b1"]))
    mu = add(matmul(enc["W_mu"], h), enc["b_mu"])
    log_sigma2 = add(matmul(enc["W_sig"], h), enc["b_sig"])
    return mu, log_sigma2
```

`log σ²` zamiast `σ`, więc wyjście sieciowe nie jest ograniczone (softplus σ jest pułapką — gradienty umierają przy σ ≈ 0).

### Krok 2: ponowna parametryzacja i dekodowanie

```python
def reparameterize(mu, log_sigma2, rng):
    eps = [rng.gauss(0, 1) for _ in mu]
    sigma = [math.exp(0.5 * lv) for lv in log_sigma2]
    return [m + s * e for m, s, e in zip(mu, sigma, eps)]

def decode(z, dec):
    h = tanh(add(matmul(dec["W1"], z), dec["b1"]))
    return add(matmul(dec["W_out"], h), dec["b_out"])
```

### Krok 3: ELBO

```python
def elbo(x, x_hat, mu, log_sigma2, beta=1.0):
    recon = sum((a - b) ** 2 for a, b in zip(x, x_hat))
    kl = 0.5 * sum(math.exp(lv) + m * m - lv - 1 for m, lv in zip(mu, log_sigma2))
    return recon + beta * kl, recon, kl
```

Dokładna forma zamknięta KL, ponieważ oba rozkłady są gaussowskie. Nie integruj numerycznie. Ludzie nadal wysyłają kod z szacunkami Monte-Carlo KL w 2026 r. – bez powodu jest on 3 razy wolniejszy.

### Krok 4: wygeneruj

```python
def sample(dec, z_dim, rng):
    z = [rng.gauss(0, 1) for _ in range(z_dim)]
    return decode(z, dec)
```

Taki jest model generatywny. Pięć linii.

## Pułapki

- **Zapadnięcie tylne.** Termin KL napędza `q(z|x) → N(0, I)` tak agresywnie, że `z` nie zawiera informacji o `x`. Poprawka: wyżarzanie β (początek β=0, rampa do 1), wolne bity lub pomiń KL w nieaktywnych wymiarach.
- **Rozmazane próbki.** Prawdopodobieństwo dekodera Gaussa implikuje rekonstrukcję MSE, która jest optymalna w skali Bayesa dla L2 (średnia) — średnia zbioru wiarygodnych cyfr jest cyfrą rozmytą. Poprawka: dyskretny dekoder (VQ-VAE, NVAE) lub użyj VAE tylko jako kodera i dyfuzja stosu na ukrytych (to właśnie robi Stable Diffusion).
- **β za duże, za wcześnie.** Patrz zapadnięcie tylne. Zacznij od β≈0,01 i rampuj.
- **Przyciemnienie ukryte za małe.** 16-D działa dla MNIST, 256-D dla ImageNet 256², 2048-D dla ImageNet 1024². VAE Stable Diffusion kompresuje 512 × 512 × 3 → 64 × 64 × 4 (32x współczynnik próbkowania w obszarze przestrzennym, 32x w kanałach).

## Użyj tego

Stos VAE 2026:

| Sytuacja | Wybierz |
|----------|------|
| Koder ukryty w obrazie do rozpowszechniania | Stabilne VAE dyfuzyjne (`sd-vae-ft-ema`) lub VAE strumienia |
| Koder ukryty w dźwięku | Kodek (Meta), SoundStream lub DAC (opis) |
| Utajone wideo | Plamy czasoprzestrzenne Sory, Latte VAE, WAN VAE |
| Uczenie się reprezentacji rozplątanej | β-VAE, FactorVAE, TCVAE |
| Dyskretne utajenia (do modelowania transformatora) | VQ-VAE, RVQ (resztkowe VQ) |
| Ciągłe utajone dla pokolenia | Zwykły VAE, a następnie kondycjonuj model przepływu/dyfuzji w tej utajonej przestrzeni |

Model dyfuzji utajonej to VAE z modelem dyfuzji żyjącym pomiędzy koderem a dekoderem. VAE wykonuje zgrubną kompresję, model dyfuzyjny wykonuje ciężkie prace. Ten sam wzór dla wideo (VAE + dyfuzja wideo DiT) i audio (Encodec + transformator MusicGen).

## Wyślij to

Zapisz `outputs/skill-vae-trainer.md`.

Wymagane umiejętności: profil zbioru danych + cel przyciemnienia utajonego + dalsze wykorzystanie (rekonstrukcja, próbkowanie lub dane wejściowe poprzez dyfuzję utajonego) i wyniki: wybór architektury (zwykły/β/VQ/RVQ), harmonogram β, przyciemnienie utajone, prawdopodobieństwo dekodera (gaussowskie vs kategoryczne) i plan oceny (rekonstrukcja MSE, KL na dim, odległość Frécheta między `q(z|x)` i `N(0, I)`).

## Ćwiczenia

1. **Łatwo.** Zmień `β` w `code/main.py` na `0.01`, `0.1`, `1.0`, `5.0`. Nagraj ostateczną rekonstrukcję MSE i KL. Które β jest najlepsze w sensie Pareto dla danych syntetycznych?
2. **Średnie.** Zastąp prawdopodobieństwo dekodera Gaussa prawdopodobieństwem Bernoulliego (strata entropii krzyżowej). Porównaj jakość próbki w binarnej wersji tych samych danych syntetycznych.
3. **Trudne.** Rozszerzenie `code/main.py` na mini VQ-VAE: zastąp ciągłe `z` wyszukiwaniem najbliższego sąsiada w książce kodów zawierającej K=32 wpisy. Porównaj rekonstrukcję MSE i zgłoś, ile wpisów książki kodowej zostało wykorzystanych (załamanie książki kodowej jest rzeczywiste).

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Autoenkoder | Sieć kodowania i dekodowania | `x → z → x̂`, ucz się MSE. Nie generatywne. |
| VAE | AE z próbnikiem | Koder wyprowadza rozkład, kara KL kształtuje przestrzeń kodu. |
| ELBO | Dolna granica dowodu | `log p(x) ≥ recon - KL[q(z\|x) \|\| p(z)]`; ciasno, gdy `q = p(z\|x)`. |
| Reparametryzacja | `z = μ + σ·ε` | Przepisuje węzeł stochastyczny jako deterministyczny + czysty szum. Umożliwia wsparcie poprzez próbkowanie. |
| Wcześniej | `p(z)` | Docelowa dystrybucja elementów ukrytych, zazwyczaj `N(0, I)`. |
| Zapadnięcie tylne | „Wygrywa termin KL” | Koder ignoruje `x`, wysyła poprzednie; dekoder musi mieć halucynacje. |
| β-VAE | Regulowana waga KL | `loss = recon + β·KL`. Wyższe β = bardziej rozplątane, ale bardziej rozmyte. |
| VQ-VAE | Dyskretny utajony | Zamień ciągły `z` na najbliższy wektor słownika; umożliwia modelowanie transformatorów. |

## Uwaga produkcyjna: VAE to najgorętsza ścieżka w serwerze dyfuzyjnym

W potoku Stable Diffusion/Flux/SD3 VAE jest wywoływany dwa razy na żądanie — raz w celu kodowania (jeśli wykonujesz img2img/inpainting) i raz w celu dekodowania. Przy 1024² przebieg dekodera jest często największym pojedynczym szczytem pamięci aktywacyjnej w całym potoku, ponieważ zwiększa próbkowanie utajonych `128×128×16` z powrotem do `1024×1024×3`. Dwie praktyczne konsekwencje:

- **Pokrój lub podziel dekodowanie.** `diffusers` ujawnia `pipe.vae.enable_slicing()` i `pipe.vae.enable_tiling()`. Kafelkowanie zamienia mały artefakt szwu na pamięć `O(tile²)` zamiast `O(H·W)`. Niezbędny dla 1024²+ na konsumenckich procesorach graficznych.
- **dekoder bf16, cyfry fp32 do ostatecznej zmiany rozmiaru.** SD 1.x VAE został wydany w fp32 i *cicho produkuje NaN* po rzutowaniu do fp16 przy 1024²+. SDXL jest dostarczany `madebyollin/sdxl-vae-fp16-fix` — zawsze preferuj wariant fp16-fix lub używaj bf16.

## Dalsze czytanie

- [Kingma i Welling (2013). Auto-Encoding Variational Bayes](https://arxiv.org/abs/1312.6114) — artykuł VAE.
- [Higgins i in. (2017). β-VAE: Nauka podstawowych pojęć wizualnych z ograniczoną ramą wariacyjną](https://openreview.net/forum?id=Sy2fzU9gl) — rozwikłany β-VAE.
- [van den Oord i in. (2017). Uczenie się neuronowej reprezentacji dyskretnej](https://arxiv.org/abs/1711.00937) — VQ-VAE.
- [Vahdat i Kautz (2021). NVAE: głęboki, hierarchiczny autoenkoder wariacyjny] (https://arxiv.org/abs/2007.03898) — najnowocześniejszy obraz VAE.
- [Rombach i in. (2022). Synteza obrazu o wysokiej rozdzielczości z modelami dyfuzji utajonej](https://arxiv.org/abs/2112.10752) — stabilna dyfuzja; VAE jako enkoder.
- [Défossez i in. (2022). Kompresja dźwięku neuronowego High Fidelity](https://arxiv.org/abs/2210.13438) — Encodec, standard audio VAE.