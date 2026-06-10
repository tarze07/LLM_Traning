# Malowanie, przemalowywanie i edycja obrazów

> Zamiana tekstu na obraz tworzy nowe rzeczy. Malowanie naprawia stare. W produkcji 70% płatnej pracy związanej z obrazem polega na edycji — zamień tło, usuń logo, rozszerz płótno, zregeneruj rękę. Malarstwo jest miejscem, w którym utrzymuje się dyfuzja.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 8 · 07 (dyfuzja utajona), Faza 8 · 08 (ControlNet i LoRA)
**Czas:** ~75 minut

## Problem

Klient przesyła idealne zdjęcie produktu z rozpraszającym napisem w tle. Chcesz usunąć znak i pozostawić wszystko inne w identycznych pikselach. Nie można od zera przeprowadzić konwersji tekstu na obraz — wynik będzie miał inny kolor, inne oświetlenie i inny kąt widzenia produktu. Chcesz zregenerować *tylko* zamaskowany obszar i chcesz, aby regeneracja uwzględniała otaczający kontekst.

To jest malowanie. Warianty:

- **Malowanie.** Regeneruj wewnątrz maski, zachowaj piksele na zewnątrz.
- **Przemalowanie.** Regeneruj się poza maską (lub poza płótnem), trzymaj w środku.
- **Edycja obrazu.** Wygeneruj ponownie cały obraz, zachowując wierność semantyczną lub strukturalną oryginałowi (SDEdit, InstructPix2Pix).

Każdy rurociąg dyfuzyjny w 2026 roku będzie wyposażony w tryb malowania. Flux.1-Fill, stabilna dyfuzja Inpaint, SDXL-Inpaint, DALL-E 3 Edit. Działają na tej samej zasadzie.

## Koncepcja

![Inpainting: odszumianie uwzględniające maskę i ponowne wstrzykiwanie zachowujące kontekst](../assets/inpainting.svg)

### Naiwne podejście (i dlaczego jest złe)

Uruchom standardową zamianę tekstu na obraz z maską. Na każdym etapie próbkowania zastąp niezamaskowany obszar ukrytego szumu czystym obrazem rozproszonym w przód. To działa... źle. Artefakty graniczne przenikają, ponieważ model nie ma informacji o tym, co znajduje się w zamaskowanym obszarze.

### Właściwy model malowania

Trenuj zmodyfikowaną sieć U-Net, która zajmuje 9 kanałów wejściowych zamiast 4:

```
input = concat([ noisy_latent (4ch), encoded_image (4ch), mask (1ch) ], dim=channel)
```

Dodatkowe kanały to kopia obrazu źródłowego zakodowanego w VAE plus maska jednokanałowa. W czasie uczenia losowo maskujesz obszary obrazu i uczysz model, aby odszumiał tylko zamaskowany obszar, podczas gdy niezamaskowany obszar jest podawany jako czysty sygnał kondycjonujący. Podsumowując, model może „widzieć” to, co otacza zamaskowany obszar i tworzy spójne uzupełnienia.

SD-Inpaint, SDXL-Inpaint, Flux-Fill korzystają z tego 9-kanałowego (lub analogowego) wejścia. Dyfuzory `StableDiffusionInpaintPipeline`, `FluxFillPipeline`.

### SDEdit (Meng i in., 2022) — edycja bezpłatna

Dodaj szum do obrazu źródłowego do pewnego poziomu pośredniego `t`, a następnie uruchom łańcuch odwrotny od `t` do 0 z nowym monitem. Żadnego przekwalifikowania. Decyzja o rozpoczęciu `t` zamienia wierność na wolność twórczą:

- `t/T = 0.3` → prawie identyczny ze źródłem, małe zmiany stylistyczne
- `t/T = 0.6` → moderuj zmiany, zachowując prostą strukturę
- `t/T = 0.9` → wygenerowano na podstawie szumu bliskiego szumowi, przy minimalnym zachowaniu źródła

### InstructPix2Pix (Brooks i in., 2023)

Dostosuj model dyfuzji na `(input_image, instruction, output_image)` trójkach. Podsumowując, połóż warunek zarówno na obrazie wejściowym, jak i na instrukcji tekstowej („spraw, aby zachód słońca”, „dodaj smoka”). Dwie skale CFG: skala obrazu i skala tekstu.

### RePaint (Lugmayr i in., 2022)

Zachowaj standardowy model bezwarunkowej dyfuzji. Przy każdym odwrotnym kroku próbkuj ponownie – od czasu do czasu wróć do głośniejszego stanu i zregeneruj się. Unika artefaktów granicznych. Używane, gdy nie masz wyszkolonego modelu do malowania.

## Zbuduj to

`code/main.py` implementuje schemat malowania zabawek 1D na danych 5-wymiarowych. Trenujemy DDPM na danych mieszaniny 5-D, gdzie każda próbka składa się z 5 pływaków z jednego z dwóch klastrów. Podsumowując, „maskujemy” 2 z 5 wymiarów, w każdym kroku wstrzykujemy zaszumioną wersję trzech niezamaskowanych wymiarów i regenerujemy tylko zamaskowane wymiary.

### Krok 1: Dane 5-D DDPM

```python
def sample_data(rng):
    cluster = rng.choice([0, 1])
    center = [-1.0] * 5 if cluster == 0 else [1.0] * 5
    return [c + rng.gauss(0, 0.2) for c in center], cluster
```

### Krok 2: wyciszenie wszystkich 5 przyciemnień

Standardowy DDPM. Dane wyjściowe Net Predykcja szumu 5-D dla zakłóconego wejścia 5-D.

### Krok 3: wnioskowanie, odwrócenie uwzględniające maskę

```python
def inpaint_step(x_t, mask, clean_image, alpha_bars, t, rng):
    # replace unmasked dims with a freshly noised version of the clean source
    a_bar = alpha_bars[t]
    for i in range(len(x_t)):
        if not mask[i]:
            x_t[i] = math.sqrt(a_bar) * clean_image[i] + math.sqrt(1 - a_bar) * rng.gauss(0, 1)
    # ...then run the normal reverse step on x_t
```

Jest to podejście naiwne i działa na danych 1-D zabawek. Do malowania prawdziwego obrazu wykorzystuje się 9-kanałowe wejście, ponieważ ważniejsza jest spójność tekstur.

### Krok 4: przemalowanie

Outpainting to inmalowanie z odwróconą maską: zamaskuj nowe (nieistniejące wcześniej) płótno, resztę wypełnij oryginałem. Identyczny cel szkolenia.

## Pułapki

- **Szwy.** Naiwne podejście pozostawia widoczne granice, ponieważ informacje o gradiencie nie przepływają przez maskę. Poprawka: rozszerz maskę o 8-16 pikseli lub użyj odpowiedniego modelu do malowania.
- **Wyciek maski.** Jeśli niezamaskowany obszar obrazu kondycjonującego jest niskiej jakości lub jest zaszumiony, zanieczyszcza to generację wewnątrz maski. Usuń szum lub lekko rozmyj.
- **CFG wpływa na rozmiar maski.** Wysoki CFG na małej masce = nasycona plama. Zmniejsz CFG w przypadku drobnych zmian.
- **Klif wierności SDEdit.** Przejście z `t/T = 0.5` do `t/T = 0.6` może spowodować utratę tożsamości podmiotu. Zamiatanie i punkt kontrolny.
- **Niezgodność podpowiedzi.** Podpowiedź powinna opisywać *cały* obraz, a nie tylko nową zawartość. „Kot siedzący na krześle”, a nie „kot”.

## Użyj tego

| Zadanie | Rurociąg |
|------|--------------|
| Usuń obiekt, mała maska ​​| SD-Inpaint lub Flux-Fill, standardowy monit |
| Zamień niebo | SD-Inpaint + „błękitne niebo o zachodzie słońca” |
| Rozciągnij płótno | Tryb malowania SDXL (pióro 8px) lub Flux-Fill z maską malowania |
| Zregeneruj dłonie/twarz | SD-Inpaint z monitem o ponowne opisanie tematu + ControlNet-Openpose |
| Zmień styl jednego regionu | SDEdytuj w `t/T=0.5` w zamaskowanym regionie |
| „Zrób zachód słońca” | InstructPix2Pix lub Flux-Kontext |
| Wymiana tła | Maska SAM → SD-Inpaint |
| Ultrawysoka wierność | Flux-Fill lub GPT-Image (hostowany) w najtrudniejszych przypadkach |

SAM (Meta's Segment Everything, 2023) + dyfuzyjna farba to proces usuwania tła na rok 2026. SAM 2 (2024) działa na wideo.

## Wyślij to

Zapisz `outputs/skill-editing-pipeline.md`. Umiejętność pobiera oryginalny obraz + opis edycji + opcjonalną maskę (lub monit SAM) i generuje wyniki: podejście do generowania maski, model podstawowy, skale CFG (obraz + tekst), tryb SDEdit-t lub malowanie oraz lista kontrolna kontroli jakości.

## Ćwiczenia

1. **Łatwe.** W `code/main.py` zmień ułamek maskowanych wymiarów od 0,2 do 0,8. W jakim ułamku jakość farby (resztka w zamaskowanych przyciemnieniach) jest równa generacji bezwarunkowej?
2. **Średni.** Wprowadź RePaint: co 10. krok wstecz, cofnij się o 5 kroków (dodaj szum) i ponownie usuń szum. Zmierz, czy zmniejsza to resztkową granicę na krawędzi maski.
3. **Trudne.** Użyj dyfuzorów Hugging Face do porównania: SD 1.5 Inpaint + ControlNet-Openpose vs Flux.1-Fill przy 20 zadaniach regeneracji twarzy. Oceniaj oddzielnie przestrzeganie pozycji i zachowanie tożsamości.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Malarstwo | „Wypełnij dziurę” | Regeneruj się w masce; zachowaj zewnętrzne piksele. |
| Przewyższenie | „Rozwiń płótno” | Zregeneruj się poza płótnem; trzymaj w środku. |
| 9-kanałowa sieć U-Net | „Właściwy model malarski” | U-Net z `noisy \| encoded-source \| mask` jako wejściem. |
| SDEdytuj | „Img2img z poziomem szumu” | Szum do czasu `t`, usuń szum za pomocą nowego monitu. |
| InstruujPix2Pix | „Edycje wyłącznie tekstowe” | Dostrojone rozproszenie (obraz, instrukcja, wynik) potrójne. |
| Przemaluj | „Bez przekwalifikowania” | Powtarzaj okresowo hałas podczas cofania, aby zmniejszyć liczbę szwów. |
| SAM | „Segmentuj wszystko” | Generator masek za pomocą kliknięć lub pól; łączy się z inpaintem. |
| Kontekst Flux | „Edytuj z kontekstem” | Wariant Flux, który akceptuje obraz referencyjny + instrukcję edycji. |

## Uwaga produkcyjna: potoki edycji są wrażliwe na opóźnienia

Użytkownicy edytujący obraz oczekują, że podróż w obie strony zajmie mniej niż 5 sekund. 30-etapowy SDXL-Inpaint przy 1024² to 3-4 s na L4 plus generowanie maski SAM (~200 ms) i kodowanie/dekodowanie VAE (łącznie ~500 ms). W ramach produkcyjnych jest to raczej związane z TTFT niż przepustowością — partia 1, niska współbieżność, minimalizacja każdego etapu:

- **SAM-H jest powolny.** SAM-H przy 1024² wynosi ~200 ms; SAM-ViT-B wynosi ~40 ms z niewielką utratą jakości. SAM 2 (wideo) dodaje czasowy narzut; nie używaj go do edycji pojedynczego obrazu.
- **Pomiń kodowanie, jeśli to możliwe.** `pipe.image_processor.preprocess(img)` koduje do ukrytych. Jeśli masz ukryte elementy z poprzedniej generacji (typowe dla interfejsów użytkownika z edycją iteracyjną), przekaż je bezpośrednio przez `latents=...`, aby pominąć jedno kodowanie VAE.
- **Rozszerzenie maski ma również znaczenie dla przepustowości.** Mała maska ​​oznacza, że ​​większość przepustowości U-Net jest marnowana (niezamaskowane piksele i tak są zaciśnięte). `diffusers`' `StableDiffusionInpaintPipeline` niezależnie od tego obsługuje pełną sieć U-Net; tylko 9-kanałowe warianty z właściwym malowaniem wykorzystują maskowane obliczenia.
- **Flux-Kontext to odpowiedź na rok 2025.** Pojedyncze przejście do przodu przez `(source_image, instruction)` — bez oddzielnej maski, bez przemiatania szumów SDEdit. Na H100 edycja trwa ~1,5 s. Lekcja architektury: zwiń sceny.

## Dalsze czytanie

- [Lugmayr i in. (2022). RePaint: Malowanie przy użyciu probabilistycznych modeli dyfuzji odszumiającej](https://arxiv.org/abs/2201.09865) — malowanie niewymagające szkolenia.
- [Meng i in. (2022). SDEdit: Synteza i edycja obrazów z przewodnikiem za pomocą stochastycznych równań różniczkowych](https://arxiv.org/abs/2108.01073) — SDEdit.
- [Brooks, Holynski, Efros (2023). InstructPix2Pix](https://arxiv.org/abs/2211.09800) — edycja instrukcji tekstowych.
- [Kirillov i in. (2023). Segmentuj wszystko](https://arxiv.org/abs/2304.02643) — SAM, źródło maski.
- [Ravi i in. (2024). SAM 2: Segmentuj wszystko na obrazach i filmach](https://arxiv.org/abs/2408.00714) — wideo SAM.
- [Hertz i in. (2022). Edycja obrazu „od podpowiedzi do podpowiedzi” z kontrolą wzajemnej uwagi](https://arxiv.org/abs/2208.01626) — edycja na poziomie uwagi.
- [Laboratoria Schwarzwaldu (2024). Flux.1-Fill i Flux.1-Kontext](https://blackforestlabs.ai/flux-1-tools/) — oprzyrządowanie 2024.