# ControlNet, LoRA i klimatyzacja

> Sam tekst jest niezdarnym sygnałem kontrolnym. ControlNet pozwala sklonować wstępnie wytrenowany model dyfuzyjny i sterować nim za pomocą mapy głębi, szkieletu ułożenia, bazgrołów lub obrazu krawędzi. LoRA umożliwia dostrojenie modelu z parametrami 2B poprzez uczenie 10 milionów parametrów. Wspólnie przekształcili Stable Diffusion z zabawki w potok obrazów na rok 2026, który będzie dostępny w każdej agencji.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 8 · 07 (dyfuzja utajona), faza 10 (LLM od podstaw — dla fundamentu LoRA)
**Czas:** ~75 minut

## Problem

Komunikaty takie jak „kobieta w czerwonej sukience spaceruje z psem po ruchliwej ulicy” nie dają modelce żadnych informacji o *gdzie* znajduje się pies, *w jakiej pozycji* jest kobieta ani *perspektywie* ulicy. Tekst określa około 10% tego, co jest potrzebne do określenia obrazu. Reszta jest wizualna i nie da się jej skutecznie opisać słowami.

Uczenie od podstaw nowego modelu warunkowego dla każdego sygnału (pozy, głębia, spryt, segmentacja) jest wygórowane. Chcesz zachować zamrożony szkielet SDXL o parametrach 2,6B, podłączyć małą boczną sieć, która odczytuje warunkowanie i pozwolić jej przesuwać pośrednie cechy szkieletu. To jest ControlNet.

Chcesz także nauczyć modelkę nowych koncepcji (twoja twarz, produkt, styl) bez konieczności ponownego szkolenia całego modela. Chcesz 100 razy mniejszą deltę. To jest LoRA — adaptery niskiej rangi, które podłączają się do istniejących wag uwagi.

ControlNet + LoRA + tekst = zestaw narzędzi dla praktyków na 2026 rok. Większość potoków obrazu produkcyjnego składa się z 2–5 warstw LoRA, 1–3 sieci sterujących i adaptera IP na bazie SDXL / SD3 / Flux.

## Koncepcja

![ControlNet klonuje koder; LoRA dodaje delty niskiej rangi](../assets/controlnet-lora.svg)

### ControlNet (Zhang i in., 2023)

Weź wstępnie przeszkolony SD. *Klonuj* połowę kodera sieci U-Net. Zamroź oryginał. Trenuj klona, ​​aby akceptował dodatkowe bodźce warunkujące (krawędzie, głębokość, poza). Podłącz klon z powrotem do połowy oryginału dekodera za pomocą połączeń pomijanych *zero splotu* (konwersje 1×1 zainicjowane na zero — zacznij od braku operacji, naucz się delty).

```
SD U-Net decoder:   ... ← orig_enc_features + zero_conv(controlnet_enc(condition))
```

Init bez konwersji oznacza, że ControlNet uruchamia się jako tożsamość — nie szkodzi nawet przed szkoleniem. Trenuj na 1M (podpowiedź, stan, obraz) trzykrotnie ze standardową stratą dyfuzyjną.

Sieci ControlNet dla poszczególnych modalności są dostarczane jako małe modele boczne (~360M dla SDXL, ~70M dla SD 1.5). Możesz je skomponować na zasadzie wnioskowania:

```
features += weight_a * control_a(depth) + weight_b * control_b(pose)
```

### LoRA (Hu i in., 2021)

Dla dowolnej warstwy liniowej `W ∈ R^{d×d}` w modelu zamroź `W` i dodaj deltę niskiego rzędu:

```
W' = W + ΔW,  ΔW = B @ A,  A ∈ R^{r×d},  B ∈ R^{d×r}
```

z `r << d`. Poziom 4-16 to standard dla uwagi, stopień 64-128 dla ciężkich dostrojeń. Liczba nowych parametrów: `2 · d · r` zamiast `d²`. W przypadku SDXL z `d=640`, `r=16`: 20 tys. parametrów na adapter zamiast 410 tys. — 20-krotna redukcja. W całym modelu: LoRA wynosi zwykle 20–200 MB w porównaniu z podstawowymi 5 GB.

Podsumowując, możesz skalować LoRA: `W' = W + α · B @ A`. `α = 0.5-1.5` jest normalne. Wiele LoRA nakłada się na siebie addytywnie (ze zwykłym zastrzeżeniem, że wchodzą w interakcję w sposób nieliniowy).

### Adapter IP (Ye i in., 2023)

Mały adapter, który akceptuje *obraz* jako warunek (obok tekstu). Wykorzystuje koder obrazu CLIP do tworzenia tokenów obrazu, wprowadza je do świadomości obok tokenów tekstowych. ~20 MB na model podstawowy. Umożliwia „wygenerowanie obrazu w stylu tego odniesienia” bez LoRA.

## Macierz kompozycyjności

| Narzędzie | Co kontroluje | Rozmiar | Kiedy używać |
|------|----------------------|------|------------|
| Sieć kontrolna | Struktura przestrzenna (poza, głębokość, krawędzie) | 70-360 MB | Dokładny układ, kompozycja |
| LoRA | Styl, temat, koncepcja | 20-200 MB | Personalizacja, styl |
| Adapter IP | Styl lub temat z obrazu referencyjnego | 20 MB | Żaden tekst nie jest w stanie opisać tego wyglądu |
| Inwersja tekstu | Pojedyncza koncepcja jako nowy token | 10 KB | Dziedzictwo, w większości zastąpione przez LoRA |
| DreamBooth | Pełne dopracowanie tematu | 2-5 GB | Silna tożsamość, duża moc obliczeniowa |
| Adapter T2I | Lżejsza alternatywa ControlNet | 70 MB | Urządzenia brzegowe, budżet wnioskowania |

ControlNet ≈ przestrzenny. LoRA ≈ semantyczny. Użyj obu.

## Zbuduj to

`code/main.py` symuluje dwa mechanizmy w widoku 1-D:

1. **LoRA.** Wstępnie wytrenowana warstwa liniowa `W`. Zamroź to. Trenuj `B @ A` niskiej rangi tak, aby `W + BA` pasował do docelowej warstwy liniowej. Pokaż, że `r = 1` wystarczy, aby doskonale nauczyć się korekty rangi 1.

2. **ControlNet-lite.** Predyktor „zamrożonej bazy” i „sieć boczna”, która odczytuje dodatkowy sygnał. Dane wyjściowe sieci bocznej są bramkowane przez możliwy do nauczenia skalar zainicjowany na zero (nasza wersja konwersji zerowej). Trenuj i obserwuj, jak brama się podnosi.

### Krok 1: Matematyka LoRA

```python
def lora(W, A, B, x, alpha=1.0):
    # W is frozen; A, B are the trainable low-rank factors.
    return [W[i][j] * x[j] for i, j in ...] + alpha * (B @ (A @ x))
```

### Krok 2: sieć po stronie zerowej

```python
side_out = control_net(x, condition)
gated = gate * side_out  # gate initialized to 0
h = base(x) + gated
```

W kroku 0 wynik jest identyczny z bazowym. Wczesne aktualizacje szkoleń `gate` powoli — bez katastrofalnych zmian.

## Pułapki

- **Nadmierne skalowanie LoRA.** `α = 2` lub `α = 3` to powszechny trik „uczyń go silniejszym”, który generuje nadmiernie stylizowane / uszkodzone wyniki. Zachowaj `α ≤ 1.5`.
- **Konflikt wagi ControlNet.** Używanie sieci kontroli pozycji przy wadze 1,0 i sieci kontroli głębokości przy wadze 1,0 zwykle powoduje przekroczenie wartości. Suma wag ≈ 1,0 jest bezpieczną wartością domyślną.
- **LoRA na niewłaściwej podstawie.** SDXL LoRA po cichu nie działają na SD 1.5, ponieważ wymiary uwagi nie pasują. Dyfuzory będą ostrzegać w wersji 0.30+.
- **Dryf inwersji tekstu.** Żetony wytrenowane w jednym punkcie kontrolnym źle dryfują w innym. LoRA jest bardziej przenośna.
- **Łączenie i przechowywanie wag LoRA.** Możesz wbudować LoRA w wagi modelu podstawowego w celu szybszego wnioskowania (bez dodawania w czasie wykonywania), ale tracisz możliwość skalowania `α` w czasie wykonywania. Zachowaj obie wersje.

## Użyj tego

| Cel | Gazociąg 2026 |
|------|----------------------------|
| Odtwórz styl graficzny marki | LoRA trenowała na ~30 wyselekcjonowanych obrazach na poziomie 32 |
| Umieść moją twarz na wygenerowanym obrazie | DreamBooth lub LoRA + Adapter IP-FaceID |
| Konkretna poza + podpowiedź | ControlNet-Openpose + SDXL + tekst |
| Kompozycja świadoma głębi | Głębokość sieci sterującej + SD3 |
| Odniesienie + podpowiedź | Adapter IP + tekst |
| Dokładny układ | ControlNet-Scribble lub ControlNet-Canny |
| Zamień tło | ControlNet-Seg + Inpainting (Lekcja 09) |
| Szybki, jednoetapowy styl | LCM-LoRA na SDXL-Turbo |

## Wyślij to

Zapisz `outputs/skill-sd-toolkit-composer.md`. Umiejętność wykonuje zadanie (zasoby wejściowe: monit, opcjonalny obraz referencyjny, opcjonalna poza, opcjonalna głębia, opcjonalny bazgroł) i generuje stos narzędzi, wagi i powtarzalny protokół początkowy.

## Ćwiczenia

1. **Łatwe.** W `code/main.py` zmień rangę LoRA `r` od 1 do 4. Przy jakiej randze LoRA dokładnie odpowiada delcie docelowej rangi 2?
2. **Średni.** Trenuj dwie oddzielne LoRA na dwóch transformacjach docelowych. Załaduj je razem i pokaż ich addytywne oddziaływanie. Kiedy interakcja przełamuje liniowość?
3. **Trudne.** Użyj dyfuzorów do układania w stosy: podstawa SDXL + Canny-ControlNet (waga 0,8) + styl LoRA (α 0,8) + adapter IP (waga 0,6). Zmierz kompromis między przestrzeganiem FID a przestrzeganiem podpowiedzi, gdy waga stosów jest różna.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Sieć kontrolna | „Kontrola przestrzenna” | Sklonowany koder + pominięcia konwersji zerowych; odczytuje obraz warunkujący. |
| Zerowy splot | „Zaczyna się od tożsamości” | Konw. 1×1 zainicjowano na zero; ControlNet zaczyna działać bez operacji. |
| LoRA | „Adapter niskiej rangi” | `W + B @ A`, `r << d`; 100 razy mniej parametrów niż pełne dostrojenie. |
| ranga r | „Pokrętło” | kompresja LoRA; 4-16 typowo, 64+ w przypadku intensywnej personalizacji. |
| α | „Siła LoRA” | Skalowanie środowiska wykonawczego delty LoRA. |
| Adapter IP | „Obraz referencyjny” | Mały adapter do kondycjonowania obrazu poprzez tokeny CLIP-image. |
| DreamBooth | „Pełne dostrojenie tematu” | Wytrenuj pełny model na około 30 obrazach obiektu. |
| Inwersja tekstu | „Nowy token” | Naucz się tylko osadzania nowych słów; dziedzictwo, w większości zastąpione. |

## Uwaga produkcyjna: zamiana LoRA, linie ControlNet, obsługa wielu dzierżawców

Prawdziwa usługa SaaS zamiany tekstu na obraz obsługuje setki LoRA i tuzin sieci ControlNet w tym samym podstawowym punkcie kontrolnym. Problem obsługi wygląda podobnie do wielodostępności LLM (literatura produkcyjna obejmuje przypadek LLM w trybie ciągłego przetwarzania wsadowego i LoRAX/S-LoRA):

- ** LoRA wymieniane podczas pracy, nie łącz.** Łączenie `W' = W + α·B·A` z bazą zapewnia ~3-5% szybsze wnioskowanie na każdym kroku, ale zawiesza `α` i bazę. Utrzymuj LoRA w pamięci VRAM jako delty rangi R; diffusers udostępnia `pipe.load_lora_weights()` + `pipe.set_adapters([...], adapter_weights=[...])` do aktywacji na żądanie. Koszt wymiany to `2 · d · r · num_layers` wagi — skala MB, subsekunda.
- **ControlNet jako drugi pas uwagi.** Sklonowany enkoder działa równolegle z podstawą. Dwie siatki kontrolne o wadze 1,0 każda = dwa dodatkowe przejścia do przodu na krok, a nie jedno połączone przejście. Prześwit wielkości partii spada kwadratowo. Budżet na ~1,5 x koszt kroku na aktywną sieć ControlNet.
- **Również kwantyzowane LoRA.** Jeśli skwantowałeś bazę (zobacz Lekcję 07, Strumień na 8 GB), delta LoRA również kwantyzuje czysto do 8-bitów lub 4-bitów. Ładowanie w stylu QLoRA umożliwia układanie 5–10 LoRA na 4-bitowej bazie Flux bez obciążania pamięci.

Specyficzne dla Flux: notebook Niels Flux-on-8GB kwantyzuje bazę do 4-bitów; układanie stylu LoRA (`pipe.load_lora_weights("user/style-lora")`) na skwantowaną bazę w `weight_name="pytorch_lora_weights.safetensors"` nadal działa. To jest przepis, który większość agencji SaaS wysyła w 2026 roku.

## Dalsze czytanie

- [Zhang, Rao, Agrawala (2023). Dodawanie kontroli warunkowej do modeli dyfuzji tekstu na obraz](https://arxiv.org/abs/2302.05543) — ControlNet.
- [Hu i in. (2021). LoRA: adaptacja modeli dużych języków o niskiej randze](https://arxiv.org/abs/2106.09685) — LoRA (pierwotnie dla LLM; porty do dyfuzji).
- [Ye i in. (2023). Adapter IP: Adapter podpowiedzi tekstowych zgodny z tekstem](https://arxiv.org/abs/2308.06721) — Adapter IP.
- [Mou i in. (2023). T2I-Adapter: adaptery edukacyjne umożliwiające lepsze kontrolowanie możliwości](https://arxiv.org/abs/2302.08453) — lżejsza alternatywa dla ControlNet.
- [Ruiz i in. (2023). DreamBooth: Dostrajanie modeli dyfuzji tekstu na obraz pod kątem generowania zależnego od podmiotu](https://arxiv.org/abs/2208.12242) — DreamBooth.
- [Dyfuzory HuggingFace — dokumentacja ControlNet / LoRA / IP-Adapter](https://huggingface.co/docs/diffusers/training/controlnet) — potoki referencyjne.