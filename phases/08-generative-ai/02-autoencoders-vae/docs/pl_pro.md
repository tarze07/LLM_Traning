# Autoenkodery i autoenkodery wariacyjne (VAE)

> Zwykły autoenkoder kompresuje, a następnie rekonstruuje. Zapamiętuje, ale nie generuje. Wystarczy jeden zabieg — nadanie kodowi rozkładu gaussowskiego — by uzyskać próbnik. To właśnie ta sztuczka z reparametryzacją `z = μ + σ·ε` leży u podstaw każdego modelu obrazu z ukrytą dyfuzją i dopasowaniem przepływu, z którego korzystasz w 2026 roku.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 3 · 02 (backprop), Faza 3 · 07 (CNN), Faza 8 · 01 (taksonomia)
**Czas:** ~75 minut

## Problem

Skompresuj 784-pikselową cyfrę MNIST do 16-wymiarowego kodu, a następnie ją zrekonstruuj. Zwykły autoenkoder poradzi sobie z rekonstrukcją MSE znakomicie, lecz przestrzeń kodu pozostanie nieuporządkowanym chaosem. Wybierz losowy punkt w tej przestrzeni, zdekoduj go — otrzymasz szum. Taki model nie próbkuje. To jedynie model kompresji, choć w zgrabnym opakowaniu.

Tak naprawdę potrzebujesz trzech rzeczy: (a) przestrzeni kodu będącej gładką, regularną dystrybucją, z której można próbkować — na przykład izotropowy gaussowski `N(0, I)`, (b) dekodera, który dla dowolnej próbki generuje wiarygodną cyfrę, oraz (c) kodera i dekodera, które nadal efektywnie kompresują. Trzy cele, jedna architektura, jeden kompromis.

VAE zaproponowany przez Kingmę w 2013 roku rozwiązuje ten problem, ucząc koder generowania *rozkładu* `q(z|x) = N(μ(x), σ(x)²)`. Rozkład ten jest przyciągany w stronę wcześniejszego `N(0, I)` przez karę KL, a następnie `z` jest próbkowane z `q(z|x)` przed dekodowaniem. Podczas wnioskowania koder zostaje usunięty — próbkujemy `z ~ N(0, I)` i przepuszczamy przez dekoder. Kara KL wymusza porządek w przestrzeni kodu.

W 2026 roku VAE rzadko stosuje się jako samodzielny model — pod względem jakości surowego obrazu zostały wyparte przez dyfuzję — lecz stanowią podstawowy koder w każdym modelu z ukrytą dyfuzją (SD 1/2/XL/3, Flux, AudioCraft). Poznając VAE, poznajesz niewidzialną pierwszą warstwę każdego nowoczesnego potoku obrazu.

## Koncepcja

![Autoencoder kontra VAE: sztuczka z ponowną parametryzacją](../assets/vae.svg)

**Autoenkoder.** `z = encoder(x)`, `x̂ = decoder(z)`, strata = `||x - x̂||²`. Przestrzeń kodu jest nieustrukturyzowana.

**Koder VAE.** Zwraca dwa wektory: `μ(x)` i `log σ²(x)`, które definiują `q(z|x) = N(μ, diag(σ²))`.

**Sztuczka reparametryzacji.** Próbkowanie z `q(z|x)` nie jest różniczkowalne. Przepisujemy próbkę jako `z = μ + σ·ε`, gdzie `ε ~ N(0, I)`. Teraz `z` jest deterministyczną funkcją `(μ, σ)` powiększoną o niezależny szum — gradienty przepływają przez `μ` i `σ`.

**Strata.** Dolne ograniczenie wiarygodności (ELBO) składa się z dwóch składników:

```
loss = reconstruction + β · KL[q(z|x) || N(0, I)]
     = ||x - x̂||²  + β · Σ_i ( σ_i² + μ_i² - log σ_i² - 1 ) / 2
```

Człon rekonstrukcji przyciąga `x̂` do `x`, człon KL wypycha `q(z|x)` w stronę rozkładu a priori. Oba człony pozostają w równowadze. Małe β (<1) oznacza ostrzejsze próbki i przestrzeń kodu bliższą danych niż rozkładu Gaussa. Duże β (>1) daje czystszą przestrzeń kodu, lecz bardziej rozmyte próbki. β-VAE (Higgins 2017) spopularyzował ten parametr i zapoczątkował badania nad rozplątaniem reprezentacji.

**Próbkowanie.** W skrócie: losujemy `z ~ N(0, I)` i przepuszczamy przez dekoder. Jedno przejście w przód — bez iteracyjnego próbkowania, jak w dyfuzji.

## Zbuduj to

`code/main.py` implementuje niewielki VAE bez NumPy ani PyTorcha. Dane wejściowe to 8-wymiarowe dane syntetyczne pochodzące z dwuskładnikowej mieszaniny Gaussa. Koder i dekoder to proste sieci MLP z jedną warstwą ukrytą. Implementujemy ręcznie aktywację tanh, przejście w przód, stratę oraz propagację wsteczną. To podejście pedagogiczne, nie produkcyjne.

### Krok 1: koder — przejście w przód

```python
def encode(x, enc):
    h = tanh(add(matmul(enc["W1"], x), enc["b1"]))
    mu = add(matmul(enc["W_mu"], h), enc["b_mu"])
    log_sigma2 = add(matmul(enc["W_sig"], h), enc["b_sig"])
    return mu, log_sigma2
```

Używamy `log σ²` zamiast `σ`, dzięki czemu wyjście sieci pozostaje nieograniczone. Wariant z softplus dla σ to pułapka — gradienty zanikają przy σ ≈ 0.

### Krok 2: reparametryzacja i dekodowanie

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

Dywergencja KL wyraża się tu w postaci zamkniętej, ponieważ oba rozkłady są gaussowskie — nie ma potrzeby całkowania numerycznego. Wciąż jednak zdarzają się implementacje z estymacją KL metodą Monte Carlo w 2026 roku; to trzykrotne spowolnienie bez żadnego uzasadnienia.

### Krok 4: generowanie

```python
def sample(dec, z_dim, rng):
    z = [rng.gauss(0, 1) for _ in range(z_dim)]
    return decode(z, dec)
```

To jest model generatywny. Pięć linii.

## Pułapki

- **Zapadnięcie rozkładu a posteriori.** Człon KL może zbyt agresywnie wymuszać `q(z|x) → N(0, I)`, przez co `z` przestaje zawierać informację o `x`. Rozwiązania: stopniowe wyżarzanie β (start od β=0, stopniowe zwiększanie do 1), metoda wolnych bitów lub pomijanie KL w nieaktywnych wymiarach.
- **Rozmyte próbki.** Gaussowski dekoder odpowiada rekonstrukcji MSE, która w sensie bayesowskim optymalizuje wartość oczekiwaną — a średnia zbioru wiarygodnych cyfr to cyfra rozmyta. Rozwiązania: dyskretny dekoder (VQ-VAE, NVAE) albo użycie VAE wyłącznie jako kodera z modelem dyfuzji działającym w przestrzeni ukrytej (tak działa Stable Diffusion).
- **Zbyt duże β zbyt wcześnie.** Skutkuje zapadnięciem opisanym powyżej. Zacznij od β≈0,01 i stopniowo zwiększaj.
- **Za mały wymiar przestrzeni ukrytej.** 16 wymiarów wystarczy dla MNIST, 256 dla ImageNet 256², 2048 dla ImageNet 1024². VAE używany w Stable Diffusion kompresuje obraz 512×512×3 do 64×64×4 (32-krotna redukcja przestrzenna, 32-krotna w kanałach).

## Użyj tego

Ekosystem VAE w 2026 roku:

| Sytuacja | Wybierz |
|----------|------|
| Koder ukryty w obrazie do dyfuzji | Stable Diffusion VAE (`sd-vae-ft-ema`) lub VAE przepływu |
| Koder ukryty w dźwięku | Encodec (Meta), SoundStream lub DAC |
| Ukryte wideo | Czasoprzestrzenne bloki Sory, Latte VAE, WAN VAE |
| Uczenie się rozplątanych reprezentacji | β-VAE, FactorVAE, TCVAE |
| Dyskretne reprezentacje ukryte (do modelowania transformatorem) | VQ-VAE, RVQ (resztkowe VQ) |
| Ciągłe reprezentacje ukryte do generowania | Zwykły VAE, następnie warunkowanie modelu przepływu lub dyfuzji w tej przestrzeni ukrytej |

Model dyfuzji utajonej to VAE z modelem dyfuzji osadzonym między koderem a dekoderem. VAE wykonuje zgrubną kompresję, model dyfuzji — pracę właściwą. Ten sam wzorzec obowiązuje dla wideo (VAE + wideo DiT) i audio (Encodec + transformator MusicGen).

## Wyślij to

Zapisz `outputs/skill-vae-trainer.md`.

Wymagane informacje: profil zbioru danych, cel wymiaru przestrzeni ukrytej oraz zamierzone zastosowanie (rekonstrukcja, próbkowanie lub dane wejściowe do dyfuzji utajonej). Wyniki: wybór architektury (zwykły/β/VQ/RVQ), harmonogram β, wymiar przestrzeni ukrytej, prawdopodobieństwo dekodera (gaussowskie lub kategoryczne) oraz plan oceny (MSE rekonstrukcji, KL na wymiar, odległość Frécheta między `q(z|x)` a `N(0, I)`).

## Ćwiczenia

1. **Łatwo.** Zmień `β` w `code/main.py` na `0.01`, `0.1`, `1.0`, `5.0`. Zapisz końcową wartość MSE rekonstrukcji i KL dla każdego przypadku. Które β jest najlepsze w sensie Pareto dla danych syntetycznych?
2. **Średnie.** Zastąp dekoder gaussowski dekoderem Bernoulliego (strata entropii krzyżowej). Porównaj jakość próbek na binarnej wersji tych samych danych syntetycznych.
3. **Trudne.** Rozszerz `code/main.py` o mini VQ-VAE: zastąp ciągłe `z` wyszukiwaniem najbliższego sąsiada w słowniku zawierającym K=32 wektory. Porównaj MSE rekonstrukcji i sprawdź, ile pozycji słownika zostało użytych (zjawisko zapaści słownika jest realne).

## Kluczowe terminy

| Termin | Co się mówi | Co to naprawdę oznacza |
|------|-----------------|----------------------|
| Autoenkoder | Sieć kodująca i dekodująca | `x → z → x̂`, trenowana na MSE. Niegeeneratywna. |
| VAE | AE z próbnikiem | Koder zwraca rozkład, kara KL kształtuje przestrzeń kodu. |
| ELBO | Dolne ograniczenie wiarygodności | `log p(x) ≥ recon - KL[q(z\|x) \|\| p(z)]`; dokładne gdy `q = p(z\|x)`. |
| Reparametryzacja | `z = μ + σ·ε` | Przekształca węzeł stochastyczny w deterministyczny plus czysty szum. Umożliwia propagację gradientu przez próbkowanie. |
| Rozkład a priori | `p(z)` | Docelowy rozkład zmiennych ukrytych, zazwyczaj `N(0, I)`. |
| Zapadnięcie a posteriori | „Wygrywa KL" | Koder ignoruje `x` i wysyła rozkład a priori; dekoder musi halucynować. |
| β-VAE | Regulowana waga KL | `loss = recon + β·KL`. Wyższe β oznacza bardziej rozplątane, lecz bardziej rozmyte reprezentacje. |
| VQ-VAE | Dyskretna przestrzeń ukryta | Ciągłe `z` zastąpione najbliższym wektorem ze słownika; umożliwia modelowanie transformatorem. |

## Uwaga produkcyjna: VAE to krytyczna ścieżka w serwerze dyfuzyjnym

W potoku Stable Diffusion/Flux/SD3 VAE jest wywoływany dwukrotnie na żądanie — raz do kodowania (przy img2img lub inpaintingu) i raz do dekodowania. Przy rozdzielczości 1024² przebieg dekodera jest często największym pojedynczym spikiem zużycia pamięci aktywacyjnej w całym potoku, ponieważ przeskalowuje ukryte tensory `128×128×16` z powrotem do `1024×1024×3`. Dwie praktyczne konsekwencje:

- **Stosuj cięcie lub kafelkowanie dekodowania.** Biblioteka `diffusers` udostępnia `pipe.vae.enable_slicing()` i `pipe.vae.enable_tiling()`. Kafelkowanie zamienia niewielki artefakt na szwach na zużycie pamięci rzędu `O(tile²)` zamiast `O(H·W)`. Niezbędne przy rozdzielczościach 1024²+ na konsumenckich kartach graficznych.
- **Dekoder w bf16, finalna zmiana rozmiaru w fp32.** VAE z SD 1.x został opublikowany w formacie fp32 i *po cichu generuje wartości NaN* po rzutowaniu do fp16 przy 1024²+. SDXL jest dostarczany z `madebyollin/sdxl-vae-fp16-fix` — zawsze wybieraj ten wariant lub używaj bf16.

## Dalsze czytanie

- [Kingma i Welling (2013). Auto-Encoding Variational Bayes](https://arxiv.org/abs/1312.6114) — artykuł VAE.
- [Higgins i in. (2017). β-VAE: Nauka podstawowych pojęć wizualnych z ograniczoną ramą wariacyjną](https://openreview.net/forum?id=Sy2fzU9gl) — β-VAE z rozplątaniem.
- [van den Oord i in. (2017). Uczenie się neuronowej reprezentacji dyskretnej](https://arxiv.org/abs/1711.00937) — VQ-VAE.
- [Vahdat i Kautz (2021). NVAE: głęboki, hierarchiczny autoenkoder wariacyjny](https://arxiv.org/abs/2007.03898) — VAE na obrazach w stanie sztuki.
- [Rombach i in. (2022). Synteza obrazu o wysokiej rozdzielczości z modelami dyfuzji utajonej](https://arxiv.org/abs/2112.10752) — Stable Diffusion; VAE jako koder.
- [Défossez i in. (2022). Kompresja dźwięku neuronowego wysokiej wierności](https://arxiv.org/abs/2210.13438) — Encodec, standard audio VAE.
