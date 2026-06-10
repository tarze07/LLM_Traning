# ControlNet, LoRA i warunkowanie

> Sam tekst jest niedoskonałym sygnałem sterującym. ControlNet pozwala sklonować wstępnie wytrenowany model dyfuzji i sterować nim za pomocą mapy głębi, szkieletu pozy, szkiców odręcznych lub obrazu krawędzi. LoRA umożliwia dostrojenie modelu o 2B parametrach przez uczenie zaledwie 10 milionów z nich. Razem przekształciły Stable Diffusion z ciekawostki w profesjonalny potok generowania obrazów na rok 2026 — dostępny w każdej agencji.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 8 · 07 (dyfuzja latentna), faza 10 (LLM od podstaw — dla fundamentów LoRA)
**Czas:** ~75 minut

## Problem

Polecenia w stylu „kobieta w czerwonej sukience spaceruje z psem po ruchliwej ulicy" nie przekazują modelowi żadnych informacji o tym, *gdzie* znajduje się pies, *w jakiej pozycji* jest kobieta ani *jak* wygląda perspektywa ulicy. Tekst opisuje najwyżej 10% tego, co decyduje o wyglądzie obrazu. Pozostała część jest wizualna i nie da się jej wiernie ująć w słowach.

Trenowanie od podstaw nowego modelu warunkowego dla każdego rodzaju sygnału (poza, głębia, sprytność, segmentacja) jest kosztowne. Zamiast tego warto zachować zamrożony szkielet SDXL o 2,6B parametrach, podłączyć niewielką sieć boczną odczytującą warunki i pozwolić jej przesuwać pośrednie reprezentacje szkieletu. To właśnie jest ControlNet.

Chcesz również nauczyć model nowych pojęć — własna twarz, produkt, styl graficzny — bez konieczności ponownego trenowania całości. Potrzebujesz stu razy mniejszej delty. To jest LoRA — adaptery niskiej rangi podłączające się do istniejących wag warstw uwagi.

ControlNet + LoRA + tekst = kompletny zestaw narzędzi praktyka na rok 2026. Większość produkcyjnych potoków generowania obrazów opiera się na 2–5 warstwach LoRA, 1–3 sieciach sterujących i adapterze IP zbudowanych na bazie SDXL / SD3 / Flux.

## Koncepcja

![ControlNet klonuje koder; LoRA dodaje delty niskiej rangi](../assets/controlnet-lora.svg)

### ControlNet (Zhang i in., 2023)

Weź wstępnie wytrenowany SD. *Sklonuj* połowę kodera sieci U-Net. Zamroź oryginał. Trenuj klon tak, aby przyjmował dodatkowe sygnały warunkujące (krawędzie, głębię, pozę). Podłącz klon z powrotem do dekodera oryginału za pomocą połączeń pomijanych z *zero-konwolucją* (sploty 1×1 inicjowane zerami — na starcie brak efektu, model uczy się delty).

```
SD U-Net decoder:   ... ← orig_enc_features + zero_conv(controlnet_enc(condition))
```

Inicjalizacja zerami oznacza, że ControlNet na początku działa jak tożsamość — nie wprowadza zakłóceń nawet przed treningiem. Trenuj na 1M trójkach (podpowiedź, warunek, obraz) ze standardową stratą dyfuzyjną.

Sieci ControlNet dla poszczególnych modalności są dostarczane jako małe modele boczne (~360M parametrów dla SDXL, ~70M dla SD 1.5). Można je łączyć podczas wnioskowania:

```
features += weight_a * control_a(depth) + weight_b * control_b(pose)
```

### LoRA (Hu i in., 2021)

Dla dowolnej warstwy liniowej `W ∈ R^{d×d}` w modelu zamroź `W` i dodaj deltę niskiej rangi:

```
W' = W + ΔW,  ΔW = B @ A,  A ∈ R^{r×d},  B ∈ R^{d×r}
```

gdzie `r << d`. Ranga 4–16 to standard dla warstw uwagi, 64–128 stosuje się przy intensywnym dostrajaniu. Liczba nowych parametrów: `2 · d · r` zamiast `d²`. Dla SDXL z `d=640` i `r=16`: 20 tys. parametrów na adapter zamiast 410 tys. — dwudziestokrotna redukcja. W całym modelu LoRA zajmuje zazwyczaj 20–200 MB w porównaniu z 5 GB modelu bazowego.

LoRA można skalować podczas wnioskowania: `W' = W + α · B @ A`. Wartość `α = 0.5–1.5` jest typowa. Wiele adapterów LoRA nakłada się addytywnie, choć wchodzą ze sobą w interakcje w sposób nieliniowy.

### IP-Adapter (Ye i in., 2023)

Niewielki adapter przyjmujący *obraz* jako dodatkowy warunek (obok tekstu). Używa kodera obrazu CLIP do tworzenia tokenów wizualnych i wprowadza je do mechanizmu uwagi obok tokenów tekstowych. Rozmiar to ~20 MB na model bazowy. Umożliwia generowanie obrazów w stylu wskazanego odniesienia — bez użycia LoRA.

## Macierz złożenia

| Narzędzie | Co kontroluje | Rozmiar | Kiedy stosować |
|------|----------------------|------|------------|
| ControlNet | Struktura przestrzenna (poza, głębia, krawędzie) | 70–360 MB | Dokładny układ, kompozycja |
| LoRA | Styl, temat, koncepcja | 20–200 MB | Personalizacja, styl graficzny |
| IP-Adapter | Styl lub temat z obrazu referencyjnego | 20 MB | Gdy tekst nie oddaje danego wyglądu |
| Textual Inversion | Pojedyncza koncepcja jako nowy token | 10 KB | Rozwiązanie starszej generacji, w dużej mierze wyparte przez LoRA |
| DreamBooth | Pełne dostrojenie pod konkretny temat | 2–5 GB | Silna tożsamość osoby/obiektu, duże zasoby obliczeniowe |
| T2I-Adapter | Lżejsza alternatywa ControlNet | 70 MB | Urządzenia brzegowe, ograniczony budżet wnioskowania |

ControlNet ≈ przestrzenny. LoRA ≈ semantyczny. Używaj obu.

## Zbuduj to

`code/main.py` symuluje oba mechanizmy w uproszczeniu 1-D:

1. **LoRA.** Wstępnie wytrenowana warstwa liniowa `W`. Zamroź ją. Trenuj czynniki niskiej rangi `B @ A` tak, aby `W + BA` odtwarzał docelową warstwę liniową. Pokaż, że `r = 1` wystarcza do idealnego nauczenia się korekty rangi 1.

2. **ControlNet-lite.** Predyktor „zamrożonej bazy" i sieć boczna odczytująca dodatkowy sygnał. Wyjście sieci bocznej jest bramkowane przez uczący się skalar inicjowany zerem (odpowiednik zero-konwolucji). Trenuj i obserwuj, jak brama stopniowo się otwiera.

### Krok 1: Matematyka LoRA

```python
def lora(W, A, B, x, alpha=1.0):
    # W is frozen; A, B are the trainable low-rank factors.
    return [W[i][j] * x[j] for i, j in ...] + alpha * (B @ (A @ x))
```

### Krok 2: Sieć boczna z zerową bramą

```python
side_out = control_net(x, condition)
gated = gate * side_out  # gate initialized to 0
h = base(x) + gated
```

W kroku 0 wynik jest identyczny z modelem bazowym. Wczesne aktualizacje treningu otwierają bramę stopniowo — bez gwałtownych zmian.

## Pułapki

- **Zbyt duże skalowanie LoRA.** Ustawianie `α = 2` lub `α = 3` w celu „wzmocnienia efektu" to powszechny błąd prowadzący do nadmiernej stylizacji lub artefaktów. Zachowaj `α ≤ 1.5`.
- **Konflikt wag ControlNet.** Jednoczesne użycie sieci pozy i sieci głębi z wagą 1,0 dla każdej zazwyczaj powoduje przekroczenia. Bezpieczna reguła: suma wag ≈ 1,0.
- **LoRA na niewłaściwej bazie.** LoRA przeznaczona dla SDXL nie zadziała cicho na SD 1.5 — wymiary warstw uwagi nie pasują. Biblioteka Diffusers ostrzega o tym od wersji 0.30+.
- **Dryfowanie tokenów z Textual Inversion.** Tokeny wytrenowane na jednym punkcie kontrolnym źle przenoszą się na inne. LoRA jest w tym względzie bardziej przenośna.
- **Scalanie wag LoRA.** Można wbudować LoRA bezpośrednio w wagi modelu bazowego (`W' = W + α·B·A`), co przyspiesza wnioskowanie o ~3–5% na krok, ale uniemożliwia późniejsze skalowanie `α`. Warto przechowywać obie wersje.

## Użyj tego

| Cel | Potok 2026 |
|------|----------------------------|
| Odtworzenie stylu graficznego marki | LoRA trenowana na ~30 wyselekcjonowanych obrazach, ranga 32 |
| Umieszczenie własnej twarzy na wygenerowanym obrazie | DreamBooth lub LoRA + IP-Adapter FaceID |
| Konkretna poza + podpowiedź tekstowa | ControlNet-Openpose + SDXL + tekst |
| Kompozycja z uwzględnieniem głębi | ControlNet-Depth + SD3 |
| Obraz referencyjny + podpowiedź | IP-Adapter + tekst |
| Precyzyjny układ kompozycji | ControlNet-Scribble lub ControlNet-Canny |
| Zamiana tła | ControlNet-Seg + Inpainting (Lekcja 09) |
| Szybki, jednoetapowy styl | LCM-LoRA na SDXL-Turbo |

## Wyślij to

Zapisz `outputs/skill-sd-toolkit-composer.md`. Umiejętność przyjmuje zadanie (dane wejściowe: podpowiedź, opcjonalny obraz referencyjny, opcjonalna poza, opcjonalna głębia, opcjonalny szkic) i generuje stos narzędzi, wagi oraz powtarzalny protokół początkowy.

## Ćwiczenia

1. **Łatwe.** W `code/main.py` zmień rangę LoRA `r` od 1 do 4. Przy jakiej randze LoRA dokładnie odtwarza deltę docelową rangi 2?
2. **Średnie.** Wytrenuj dwie oddzielne LoRA na dwóch różnych transformacjach docelowych. Załaduj je jednocześnie i pokaż ich addytywne oddziaływanie. Kiedy interakcja wychodzi poza liniowość?
3. **Trudne.** Użyj biblioteki Diffusers do złożenia stosu: baza SDXL + Canny-ControlNet (waga 0,8) + LoRA stylu (α 0,8) + IP-Adapter (waga 0,6). Zmierz zależność między FID a stopniem przestrzegania podpowiedzi przy różnych konfiguracjach wag.

## Kluczowe terminy

| Termin | Potoczne określenie | Co to faktycznie oznacza |
|------|-----------------|----------------------|
| ControlNet | „Kontrola przestrzenna" | Sklonowany koder + pominięcia z zero-konwolucją; odczytuje obraz warunkujący. |
| Zero-konwolucja | „Startuje od tożsamości" | Splot 1×1 inicjowany zerami; ControlNet zaczyna jako operacja pusta. |
| LoRA | „Adapter niskiej rangi" | `W + B @ A`, `r << d`; stukrotnie mniej parametrów niż pełne dostrojenie. |
| Ranga r | „Pokrętło kompresji" | Stopień kompresji LoRA; 4–16 typowo, 64+ przy intensywnej personalizacji. |
| α | „Siła LoRA" | Współczynnik skalowania delty LoRA podczas wnioskowania. |
| IP-Adapter | „Obraz referencyjny" | Niewielki adapter do warunkowania obrazem przez tokeny CLIP. |
| DreamBooth | „Pełne dostrojenie tematu" | Trening całego modelu na ~30 zdjęciach danego obiektu lub osoby. |
| Textual Inversion | „Nowy token" | Uczenie wyłącznie osadzenia nowego słowa; starsze podejście, w dużej mierze wyparte. |

## Uwaga produkcyjna: wymiana LoRA, potoki ControlNet, obsługa wielu najemców

Rzeczywista usługa SaaS zamiany tekstu na obraz obsługuje setki adapterów LoRA i kilkanaście sieci ControlNet na tym samym punkcie kontrolnym. Problem obsługi jest zbliżony do wielodostępności w LLM (literatura produkcyjna obejmuje tryb ciągłego przetwarzania wsadowego dla LLM oraz LoRAX/S-LoRA):

- **LoRA wymieniana w locie, nie scalana.** Scalenie `W' = W + α·B·A` z bazą przyspiesza wnioskowanie o ~3–5% na krok, ale zamraża `α` i bazę. Lepiej trzymać LoRA w pamięci VRAM jako delty rangi R; biblioteka Diffusers udostępnia `pipe.load_lora_weights()` i `pipe.set_adapters([...], adapter_weights=[...])` do aktywacji na żądanie. Koszt wymiany to wagi rzędu `2 · d · r · num_layers` — skala megabajtów, czas poniżej sekundy.
- **ControlNet jako dodatkowe przejście przez sieć.** Sklonowany koder działa równolegle z bazą. Dwie sieci ControlNet z wagą 1,0 każda oznaczają dwa dodatkowe przejścia do przodu na krok, nie jedno połączone. Przepustowość przy danym rozmiarze partii spada kwadratowo. Zakładaj ~1,5-krotny wzrost kosztu kroku na każdą aktywną sieć ControlNet.
- **Kwantyzacja LoRA.** Jeśli baza jest skwantowana (zob. Lekcja 07, strumień na 8 GB), delta LoRA również kwantyzuje się czysto do 8 lub 4 bitów. Styl ładowania QLoRA umożliwia układanie 5–10 adapterów LoRA na 4-bitowej bazie Flux bez przeciążania pamięci.

Specyfika Flux: notatnik Niels Flux-on-8GB kwantyzuje bazę do 4 bitów; ładowanie LoRA stylu (`pipe.load_lora_weights("user/style-lora")`) na skwantowaną bazę z `weight_name="pytorch_lora_weights.safetensors"` nadal działa. To przepis stosowany przez większość agencji SaaS w 2026 roku.

## Dalsze czytanie

- [Zhang, Rao, Agrawala (2023). Dodawanie kontroli warunkowej do modeli dyfuzji tekstu na obraz](https://arxiv.org/abs/2302.05543) — ControlNet.
- [Hu i in. (2021). LoRA: adaptacja modeli dużych języków o niskiej randze](https://arxiv.org/abs/2106.09685) — LoRA (pierwotnie dla LLM; przeniesiona do dyfuzji).
- [Ye i in. (2023). IP-Adapter: adapter podpowiedzi tekstowych zgodny z tekstem](https://arxiv.org/abs/2308.06721) — IP-Adapter.
- [Mou i in. (2023). T2I-Adapter: uczące się adaptery do precyzyjniejszego sterowania generowaniem](https://arxiv.org/abs/2302.08453) — lżejsza alternatywa dla ControlNet.
- [Ruiz i in. (2023). DreamBooth: dostrajanie modeli dyfuzji tekstu na obraz do generowania zależnego od podmiotu](https://arxiv.org/abs/2208.12242) — DreamBooth.
- [HuggingFace Diffusers — dokumentacja ControlNet / LoRA / IP-Adapter](https://huggingface.co/docs/diffusers/training/controlnet) — potoki referencyjne.
