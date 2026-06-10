# Malowanie, przemalowywanie i edycja obrazów

> Generowanie z tekstu tworzy obrazy od zera. Malowanie naprawia istniejące. W produkcji 70% płatnych zleceń związanych z obrazem dotyczy edycji — zmiana tła, usunięcie logo, rozszerzenie płótna, regeneracja dłoni. To właśnie tutaj dyfuzja utrzymuje swoją pozycję.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 8 · 07 (dyfuzja utajona), Faza 8 · 08 (ControlNet i LoRA)
**Czas:** ~75 minut

## Problem

Klient przesyła idealne zdjęcie produktu z rozpraszającym napisem w tle. Chcesz usunąć ten napis, pozostawiając wszystko inne w niezmienionej postaci. Generowanie od nowa z tekstu jest niemożliwe — wynik będzie miał inny kolor, inne oświetlenie i inny kąt kamery. Potrzebujesz zregenerować *wyłącznie* zamaskowany obszar, tak aby regeneracja uwzględniała otaczający kontekst.

To jest właśnie malowanie (inpainting). Jego warianty:

- **Malowanie (inpainting).** Regeneruj wnętrze maski, zachowaj piksele na zewnątrz.
- **Przemalowanie (outpainting).** Regeneruj obszar poza maską (lub poza płótnem), zachowaj zawartość wewnątrz.
- **Edycja obrazu.** Wygeneruj obraz od nowa, zachowując wierność semantyczną lub strukturalną oryginałowi (SDEdit, InstructPix2Pix).

Każdy potok dyfuzyjny z 2026 roku obsługuje tryb malowania: Flux.1-Fill, Stable Diffusion Inpaint, SDXL-Inpaint, DALL-E 3 Edit. Wszystkie działają na tej samej zasadzie.

## Koncepcja

![Inpainting: odszumianie uwzględniające maskę i ponowne wstrzykiwanie zachowujące kontekst](../assets/inpainting.svg)

### Naiwne podejście i jego wady

Uruchom standardowe generowanie z tekstu z maską. Na każdym etapie próbkowania zastąp niezamaskowany obszar przestrzeni ukrytej czystym obrazem rozproszonym w przód. To działa — ale źle. Na granicach pojawiają się artefakty, ponieważ model nie widzi zawartości zamaskowanego obszaru.

### Właściwy model malowania

Wytrenuj zmodyfikowaną sieć U-Net przyjmującą 9 kanałów wejściowych zamiast 4:

```
input = concat([ noisy_latent (4ch), encoded_image (4ch), mask (1ch) ], dim=channel)
```

Dodatkowe kanały to zakodowany w VAE obraz źródłowy oraz jednokanałowa maska. Podczas treningu losowo maskujesz obszary obrazu i uczysz model odszumiania wyłącznie zamaskowanego obszaru, podczas gdy niezamaskowane fragmenty podawane są jako czysty sygnał warunkujący. Dzięki temu model „widzi" otoczenie zamaskowanego obszaru i tworzy spójne uzupełnienia.

SD-Inpaint, SDXL-Inpaint i Flux-Fill korzystają z tego 9-kanałowego (lub analogicznego) wejścia. W bibliotece Diffusers: `StableDiffusionInpaintPipeline`, `FluxFillPipeline`.

### SDEdit (Meng i in., 2022) — edycja bez dogrzewania

Dodaj szum do obrazu źródłowego aż do pewnego pośredniego poziomu `t`, a następnie uruchom odwrotny łańcuch dyfuzji od `t` do 0 z nowym promptem. Żadnego dodatkowego treningu. Parametr startowy `t` wyznacza kompromis między wiernością oryginałowi a swobodą twórczą:

- `t/T = 0.3` → wynik prawie identyczny ze źródłem, drobne zmiany stylistyczne
- `t/T = 0.6` → umiarkowane zmiany przy zachowaniu ogólnej struktury
- `t/T = 0.9` → generowanie zbliżone do losowego, minimalne zachowanie oryginału

### InstructPix2Pix (Brooks i in., 2023)

Model dyfuzji dostrojony na trójkach `(input_image, instruction, output_image)`. Warunkuje się jednocześnie na obrazie wejściowym i instrukcji tekstowej („zmień na zachód słońca", „dodaj smoka"). Dysponuje dwiema niezależnymi skalami CFG: dla obrazu i dla tekstu.

### RePaint (Lugmayr i in., 2022)

Zachowaj standardowy model dyfuzji bezwarunkowej. Podczas każdego kroku odwrotnego próbkuj ponownie — od czasu do czasu wróć do stanu o wyższym poziomie szumu i wykonaj regenerację. Redukuje to artefakty na granicach. Stosowane wtedy, gdy nie dysponujesz wytrenowanym modelem do malowania.

## Budowa

`code/main.py` implementuje uproszczony schemat malowania 1D na danych 5-wymiarowych. Trenujemy DDPM na danych z mieszaniny 5-D, gdzie każda próbka składa się z 5 liczb zmiennoprzecinkowych należących do jednego z dwóch skupisk. „Maskujemy" 2 z 5 wymiarów, na każdym kroku wstrzykujemy zaszumioną wersję trzech niezamaskowanych wymiarów i regenerujemy wyłącznie wymiary zamaskowane.

### Krok 1: Dane 5-D dla DDPM

```python
def sample_data(rng):
    cluster = rng.choice([0, 1])
    center = [-1.0] * 5 if cluster == 0 else [1.0] * 5
    return [c + rng.gauss(0, 0.2) for c in center], cluster
```

### Krok 2: Zaszumianie wszystkich 5 wymiarów

Standardowy DDPM. Sieć przewiduje szum 5-D dla zakłóconego wejścia 5-D.

### Krok 3: Wnioskowanie z odwrotną dyfuzją uwzględniającą maskę

```python
def inpaint_step(x_t, mask, clean_image, alpha_bars, t, rng):
    # replace unmasked dims with a freshly noised version of the clean source
    a_bar = alpha_bars[t]
    for i in range(len(x_t)):
        if not mask[i]:
            x_t[i] = math.sqrt(a_bar) * clean_image[i] + math.sqrt(1 - a_bar) * rng.gauss(0, 1)
    # ...then run the normal reverse step on x_t
```

To naiwne podejście sprawdza się na uproszczonych danych 1-D. Do malowania prawdziwych obrazów stosuje się 9-kanałowe wejście, ponieważ spójność tekstur ma kluczowe znaczenie.

### Krok 4: Przemalowanie (outpainting)

Outpainting to inpainting z odwróconą maską: maskujesz nowe (wcześniej nieistniejące) obszary płótna, a resztę wypełniasz oryginałem. Cel treningowy pozostaje identyczny.

## Pułapki

- **Szwy.** Naiwne podejście pozostawia widoczne granice, ponieważ informacje gradientu nie przepływają przez maskę. Rozwiązanie: rozszerz maskę o 8–16 pikseli lub użyj dedykowanego modelu do malowania.
- **Wyciek maski.** Jeśli niezamaskowany obszar obrazu warunkującego jest niskiej jakości lub zaszumiony, zanieczyszcza generację wewnątrz maski. Usuń szum lub lekko rozmyj obraz wejściowy.
- **CFG a rozmiar maski.** Wysoki CFG na małej masce daje nasyconą plamę. Zmniejsz CFG przy drobnych korektach.
- **Skokowa utrata wierności w SDEdit.** Przejście z `t/T = 0.5` do `t/T = 0.6` może spowodować utratę tożsamości obiektu. Przetestuj zakres wartości i zapisuj punkty kontrolne.
- **Niedopasowanie promptu.** Prompt powinien opisywać *cały* obraz, a nie tylko nową zawartość. „Kot siedzący na krześle", a nie samo „kot".

## Zastosowania

| Zadanie | Potok |
|------|--------------|
| Usuń obiekt (mała maska) | SD-Inpaint lub Flux-Fill, standardowy prompt |
| Zmień niebo | SD-Inpaint + „błękitne niebo o zachodzie słońca" |
| Rozciągnij płótno | Tryb outpainting SDXL (pióro 8px) lub Flux-Fill z maską outpaintingu |
| Zregeneruj dłonie/twarz | SD-Inpaint z promptem opisującym cały temat + ControlNet-Openpose |
| Zmień styl jednego regionu | SDEdit przy `t/T=0.5` na zamaskowanym regionie |
| „Zrób zachód słońca" | InstructPix2Pix lub Flux-Kontext |
| Wymiana tła | Maska SAM → SD-Inpaint |
| Najwyższa wierność | Flux-Fill lub GPT-Image (hostowany) w najtrudniejszych przypadkach |

SAM (Meta's Segment Anything, 2023) w połączeniu z dyfuzją to standardowy proces wymiany tła na rok 2026. SAM 2 (2024) obsługuje wideo.

## Wdrożenie

Zapisz `outputs/skill-editing-pipeline.md`. Umiejętność przyjmuje oryginalny obraz, opis edycji i opcjonalną maskę (lub prompt dla SAM), a następnie generuje dokumentację: metodę tworzenia maski, model bazowy, skale CFG (dla obrazu i tekstu), tryb SDEdit-t lub malowania oraz listę kontrolną jakości.

## Ćwiczenia

1. **Łatwe.** W `code/main.py` zmień ułamek maskowanych wymiarów od 0,2 do 0,8. Przy jakim ułamku jakość malowania (resztkowy błąd w zamaskowanych wymiarach) zrównuje się z bezwarunkowym generowaniem?
2. **Średnie.** Zaimplementuj RePaint: co 10. krok wstecz cofnij się o 5 kroków (dodaj szum), po czym ponownie usuń szum. Sprawdź, czy redukuje to resztkowy artefakt na krawędzi maski.
3. **Trudne.** Użyj biblioteki Hugging Face Diffusers do porównania: SD 1.5 Inpaint + ControlNet-Openpose kontra Flux.1-Fill na 20 zadaniach regeneracji twarzy. Oceniaj oddzielnie zgodność z pozą oraz zachowanie tożsamości osoby.

## Słownik pojęć

| Termin | Potoczne określenie | Właściwe znaczenie |
|------|-----------------|----------------------|
| Malowanie (inpainting) | „Wypełnij dziurę" | Regeneruj obszar wewnątrz maski, zachowaj piksele zewnętrzne. |
| Przemalowanie (outpainting) | „Rozszerz płótno" | Regeneruj obszar poza płótnem, zachowaj zawartość wewnętrzną. |
| 9-kanałowa sieć U-Net | „Właściwy model malowania" | U-Net z `noisy \| encoded-source \| mask` jako wejściem. |
| SDEdit | „Img2img z poziomem szumu" | Dodaj szum do czasu `t`, usuń szum z nowym promptem. |
| InstructPix2Pix | „Edycja wyłącznie tekstem" | Dostrojona dyfuzja na trójkach (obraz, instrukcja, wynik). |
| RePaint | „Bez dodatkowego treningu" | Cykliczne ponowne zaszumianie podczas kroku odwrotnego — redukuje szwy. |
| SAM | „Segmentuj wszystko" | Generator masek sterowany kliknięciami lub obszarami; łączy się z inpaintingiem. |
| Flux-Kontext | „Edycja z kontekstem" | Wariant Flux przyjmujący obraz referencyjny i instrukcję edycji. |

## Uwaga produkcyjna: potoki edycji są wrażliwe na opóźnienia

Użytkownicy edytujący obraz oczekują odpowiedzi poniżej 5 sekund. SDXL-Inpaint w 30 krokach przy rozdzielczości 1024² zajmuje 3–4 s na GPU L4, do tego dochodzi generowanie maski SAM (~200 ms) i kodowanie/dekodowanie VAE (łącznie ~500 ms). W środowisku produkcyjnym bottleneck to TTFT, a nie przepustowość — używaj partii po 1, ogranicz współbieżność, minimalizuj każdy etap:

- **SAM-H jest wolny.** SAM-H przy 1024² to ~200 ms; SAM-ViT-B osiąga ~40 ms przy niewielkiej utracie jakości. SAM 2 (wideo) wprowadza dodatkowy narzut czasowy — nie używaj go do edycji pojedynczych obrazów.
- **Pomiń kodowanie, jeśli to możliwe.** `pipe.image_processor.preprocess(img)` koduje obraz do przestrzeni ukrytej. Jeśli masz już gotowe reprezentacje ukryte z poprzedniej generacji (typowe w interfejsach z edycją iteracyjną), przekaż je bezpośrednio przez `latents=...`, omijając jedno kodowanie VAE.
- **Rozmiar maski wpływa na przepustowość.** Mała maska oznacza, że większość obliczeń U-Net jest marnowana — niezamaskowane piksele i tak są przetwarzane. `StableDiffusionInpaintPipeline` z biblioteki `diffusers` obsługuje zawsze pełną sieć U-Net; tylko 9-kanałowe warianty z właściwym malowaniem wykorzystują obliczenia warunkowane maską.
- **Flux-Kontext to rozwiązanie roku 2025.** Pojedyncze przejście w przód przez `(source_image, instruction)` — bez oddzielnej maski, bez iteracyjnego odszumiania w stylu SDEdit. Na H100 edycja trwa ~1,5 s. Architektoniczna lekcja: integruj warunki bezpośrednio w modelu.

## Literatura

- [Lugmayr i in. (2022). RePaint: Malowanie przy użyciu probabilistycznych modeli dyfuzji odszumiającej](https://arxiv.org/abs/2201.09865) — inpainting bez dodatkowego treningu.
- [Meng i in. (2022). SDEdit: Synteza i edycja obrazów z przewodnikiem za pomocą stochastycznych równań różniczkowych](https://arxiv.org/abs/2108.01073) — SDEdit.
- [Brooks, Holynski, Efros (2023). InstructPix2Pix](https://arxiv.org/abs/2211.09800) — edycja sterowana instrukcjami tekstowymi.
- [Kirillov i in. (2023). Segment Anything](https://arxiv.org/abs/2304.02643) — SAM, generator masek.
- [Ravi i in. (2024). SAM 2: Segment Anything on Images and Videos](https://arxiv.org/abs/2408.00714) — SAM dla wideo.
- [Hertz i in. (2022). Prompt-to-Prompt Image Editing with Cross Attention Control](https://arxiv.org/abs/2208.01626) — edycja na poziomie mechanizmu uwagi.
- [Black Forest Labs (2024). Flux.1-Fill i Flux.1-Kontext](https://blackforestlabs.ai/flux-1-tools/) — narzędzia z 2024 roku.
