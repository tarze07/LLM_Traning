# Modele generatywne — taksonomia i historia

> Każdy model obrazu, model tekstowy, model wideo i model 3D mieści się w jednym z pięciu segmentów. Wybierz niewłaściwe wiadro, a będziesz walczyć z matematyką tygodniami. Wybierz właściwą, a ostatnie dwanaście lat postępu w tej dziedzinie będzie wyraźnie widoczne w Twojej głowie.

**Typ:** Ucz się
**Języki:** Python
**Wymagania wstępne:** Faza 2 (Podstawy ML), Faza 3 (Rdzeń głębokiego uczenia się), Faza 7 · 14 (Transformatory)
**Czas:** ~45 minut

## Problem

Model generatywny spełnia jedno zadanie: biorąc pod uwagę próbki szkoleniowe pobrane z nieznanej dystrybucji `p_data(x)`, generuje nowe próbki, które wyglądają, jakby pochodziły z tej samej dystrybucji. Twarze, zdania, pliki MIDI, struktury białkowe – to ten sam problem, jeśli zmrużysz oczy.

Problem w tym, że `p_data` znajduje się w przestrzeni o milionach wymiarów (obraz RGB o wymiarach 512x512 ma ~786 tys. wymiarów), próbki znajdują się na cienkiej rozmaitości wewnątrz tej przestrzeni, a masz tylko może 10 milionów przykładów. Brutalne wymuszanie gęstości jest beznadziejne. Każdy model generatywny jest kompromisem polegającym na zamianie jednego trudnego problemu na nieco mniej trudny.

Ostatnie dwanaście lat przeżyło pięć rodzin. Wiedząc, na jaki kompromis poszła każda rodzina, dowiesz się, dlaczego w niektórych zadaniach wygrywa, a w innych załamuje się.

## Koncepcja

![Pięć rodzin modeli generatywnych — taksonomia według tego, co modelują](../assets/taxonomy.svg)

**1. Wyraźna gęstość, wykonalna.** Zapisz `log p(x)` jako sumę, którą możesz faktycznie oszacować. Modele autoregresyjne (PixelCNN, WaveNet, GPT) rozkładają na czynniki `p(x) = ∏ p(x_i | x_<i)`. Normalizowanie przepływów (RealNVP, Glow) buduje `p(x)` jako odwracalną transformację prostej podstawy. Zaleta: dokładne prawdopodobieństwo, czysta utrata treningu. Wada: wnioskowanie autoregresyjne jest sekwencyjne (powolne w przypadku długich sekwencji), przepływy wymagają architektur odwracalnych (restrykcyjne architektonicznie).

**2. Wyraźna gęstość, przybliżona.** Połącz `log p(x)` od dołu (ELBO) i zoptymalizuj powiązanie. VAE (Kingma 2013) wykorzystują koder-dekoder z wariacyjnym tyłem. Modele dyfuzji (DDPM, Ho 2020) trenują denoiser, który pośrednio optymalizuje ważony ELBO. Rozproszenie będzie dominującym szkieletem obrazu, wideo i 3D w 2026 roku.

**3. Ukryta gęstość.** Całkowicie pomiń gęstość; poznaj generator `G(z)`, który generuje próbki i dyskryminator `D(x)`, który odróżnia rzeczywistość od podróbki. Sieci GAN (Goodfellow 2014). Szybki w wyciąganiu wniosków (jedno podanie w przód), ale notorycznie niestabilny podczas treningu. StyleGAN 1/2/3 pozostanie najnowocześniejszym fotorealizmem w stałych domenach (twarze, sypialnie) nawet w 2026 roku.

**4. Na podstawie wyniku / w czasie ciągłym.** Dowiedz się bezpośrednio o gradiencie gęstości logu `∇_x log p(x)` (wynik). Song i Ermon (2019) wykazali, że dopasowanie wyników uogólnia dyfuzję na SDE. Dopasowywanie przepływu (Lipman 2023) to nowość w latach 2024–2026: szkolenie bez symulacji, prostsze ścieżki, 4–10 razy szybsze próbkowanie niż DDPM. Stable Diffusion 3, Flux, AudioCraft 2 wykorzystują dopasowanie przepływu.

**5. Autoregresja oparta na tokenach w przypadku kodów dyskretnych.** Kompresuj bardzo ciemne dane za pomocą VQ-VAE lub kwantyzatora resztkowego w krótką sekwencję dyskretnych tokenów, a następnie użyj transformatora do modelowania sekwencji tokenów. Używają tego Parti, MuseNet, AudioLM, VALL-E, tokenizer łatek Sory. To jest segment 1 plus wyuczony tokenizator.

## Krótka historia

| Rok | Modelka | Dlaczego to miało znaczenie |
|------|-------|--------------------------------|
| 2013 | VAE (Kingma) | Pierwszy głęboki model generatywny z użyteczną stratą treningową. |
| 2014 | GAN (Goodfellow) | Ukryta gęstość, brak prawdopodobieństwa — szokująco ostre próbki. |
| 2015 | RYSUJ, PixelCNN | Sekwencyjne generowanie obrazu. |
| 2017 | Blask, RealNVP | Przepływy odwracalne; dokładne prawdopodobieństwo wraz z głębokością. |
| 2017 | Progresywny GAN | Pierwsze twarze megapikselowe. |
| 2019 | StylGAN / StylGAN2 | Fotorealistyczne twarze wciąż nie mają sobie równych w tej jednej domenie. |
| 2020 | DDPM (Ho) | Dyfuzja staje się praktyczna. |
| 2021 | KLIP, DALL-E 1, VQGAN | Zamiana tekstu na obraz trafia do głównego nurtu. |
| 2022 | Obraz, stabilna dyfuzja 1, DALL-E 2 | Rozpowszechnianie utajone + warunkowanie tekstu = towar. |
| 2022 | ControlNet, LoRA | Dobra kontrola nad wstępnie wyszkoloną dyfuzją. |
| 2023 | SDXL, Midjourney v5, dopasowanie przepływu | Skala + lepsza dynamika treningu. |
| 2024 | Sora, Stabilna dyfuzja 3, Flux.1 | Rozpowszechnianie wideo; dopasowanie przepływu wygrywa. |
| 2025 | Veo 2, Kling 1.5, pas startowy Gen-3, Nano Banana | Film na poziomie produkcyjnym. |
| 2026 | Konsystencja + poprawiony przepływ | Próbkowanie jednoetapowe ze szkieletów dyfuzyjnych. |

## Segregacja składająca się z pięciu pytań

Kiedy pojawi się nowy papier modelowy, odpowiedz na pięć pytań przed przeczytaniem sekcji poświęconej metodom.

1. **Co jest modelowane?** Piksele, utajone, dyskretne tokeny, Gaussa 3D, siatki, przebiegi?
2. **Czy gęstość jest wyraźna czy ukryta?** Czy zapisano `log p(x)`?
3. **Próbkowanie: jednorazowe czy iteracyjne?** Iteracyjne oznacza wolniejsze wnioskowanie; one-shot zwykle oznacza kontradyktoryjny lub destylowany.
4. **Warowanie: bezwarunkowe, klasa, tekst, obraz, poza?** Określa to utratę i rusztowanie architektoniczne.
5. **Ocena: FID, wynik CLIP, IS, preferencje ludzkie, dokładność zadania?** Każdy z nich ma znane tryby awarii (patrz Lekcja 14).

Będziesz ponownie odpowiadać na te pięć odpowiedzi podczas każdej lekcji w tej fazie. W końcu wykażą się refleksem.

## Zbuduj to

Kod tej lekcji to uproszczona wizualizacja: dopasuj jednowymiarową mieszaninę Gaussów do próbek, stosując trzy podejścia do zabawek (gęstość jądra, histogram dyskretny i generator „w stylu GAN” najbliższej próbki), aby zobaczyć różnicę między jawną a ukrytą gęstością problemu, który możesz wydrukować na jednym ekranie.

Uruchom `code/main.py`. Pobiera 2000 próbek z dwumodowej mieszaniny Gaussa, a następnie drukuje:

```
explicit density (histogram): p(x in [-0.5, 0.5]) ≈ 0.38
approximate density (KDE):     p(x in [-0.5, 0.5]) ≈ 0.41
implicit (nearest-sample gen): 20 new samples printed, no p(x)
```

Uwaga: pierwsze dwa pozwalają zadać pytanie „jak prawdopodobny jest ten punkt?” Trzeci nie może. To jest rozróżnienie *jawne i ukryte*, które będzie miało znaczenie podczas każdej przyszłej lekcji.

## Użyj tego

Jaka rodzina, jakie zadanie w 2026 roku?

| Zadanie | Najlepsza rodzina | Dlaczego |
|------|------------|---------|
| Fotorealistyczne twarze, wąska domena | StylGAN 2/3 | Wciąż najostrzejsze i najszybsze wnioskowanie. |
| Ogólne zamiana tekstu na obraz | Dyfuzja utajona + dopasowanie przepływu | SD3, Flux.1, DALL-E 3. |
| Szybka zamiana tekstu na obraz | Przepływ rektyfikowany + destylacja | SDXL-Turbo, SD3-Turbo, LCM. |
| Tekst na wideo | Transformator dyfuzyjny + dopasowanie przepływu | Sora, Veo 2, Kling. |
| Mowa + muzyka | AR oparty na tokenach (AudioLM, VALL-E, MusicGen) lub dopasowanie przepływu (AudioCraft 2) | Dyskretne tokeny skalują się tanio. |
| Sceny 3D | Dopasowanie rozpryskiwania Gaussa, przed dyfuzją | 3D-GS do rekonstrukcji, dyfuzja do nowego widoku. |
| Oszacowanie gęstości (bez pobierania próbek) | Przepływy | Tylko rodzina z dokładnym `log p(x)`. |
| Symulacja / fizyka | Dopasowanie przepływu, wynik SDE | Ścieżki proste, gładkie pola wektorowe. |

## Wyślij to

Zapisz jako `outputs/skill-model-chooser.md`.

Umiejętność wymaga opisu zadania i wyników: (1) której rodziny użyć, (2) rankingowej listy trzech otwartych i trzech hostowanych opcji, (3) prawdopodobnego trybu awarii, na który należy zwrócić uwagę oraz (4) budżetu obliczeniowego/czasowego.

## Ćwiczenia

1. **Łatwo.** Dla każdego z pięciu produktów określ rodzinę i szkielet: obraz ChatGPT, Midjourney v7, Sora, Runway Gen-3, ElevenLabs. Dowody powinny pochodzić z publicznych raportów technicznych.
2. **Średni.** Artykuł, który będziesz jutro czytać, twierdzi, że próbkowanie jest 100 razy szybsze niż dyfuzja. Zapisz trzy pytania, aby sprawdzić, czy przyspieszenie przetrwa uwarunkowanie i wysoką rozdzielczość.
3. **Trudne.** Wybierz jedną domenę, na której Ci zależy (np. struktura białka, CAD, cząsteczki, trajektorie). Odpowiedz na składającą się z pięciu pytań selekcję dotyczącą bieżącego modelu SOTA w tej dziedzinie i naszkicuj, co zmieniłby lepszy model.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Model generatywny | „To tworzy nowe rzeczy” | Uczy się próbnika dla `p_data(x)`, opcjonalnie udostępnia `log p(x)`. |
| Wyraźna gęstość | „Możesz to ocenić” | Model zapewnia formę zamkniętą lub wykonalną `log p(x)`. |
| Ukryta gęstość | „w stylu GAN” | Tylko próbnik — nie ma możliwości oceny `p(x)` danego punktu. |
| ELBO | „Dolna granica dowodów” | Przejrzysta dolna granica `log p(x)`; Optymalizują to VAE i dyfuzja. |
| Wynik | „Gradient gęstości logarytmicznej” | `∇_x log p(x)`; Modele dyfuzyjne i SDE uczą się tego pola. |
| Hipoteza rozmaitości | „Dane żyją na powierzchni” | Dane o dużym przyciemnieniu koncentrują się na kolektorze o niskim przyciemnieniu; dlaczego redukcja wymiarowości działa. |
| Autoregresja | „Przewiduj następny kawałek” | Rozłóż łączenie na czynniki jako iloczyn warunków warunkowych. |
| Utajone | „Skompresowany kod” | Reprezentacja o niskim przyciemnieniu, z której dekoder może zrekonstruować sygnał wejściowy. |

## Uwaga produkcyjna: pięć rodzin, pięć kształtów wnioskowania

Każda rodzina jest odwzorowywana na inną krzywą kosztów serwera wnioskowania. Literatura dotycząca wnioskowania produkcyjnego przedstawia wnioskowanie LLM jako wstępne wypełnienie + dekodowanie; ten sam rozkład ma zastosowanie tutaj:

- **Autoregresja (zasobnik 1 i 5).** Dekodowanie sekwencyjne dominuje w opóźnieniu; Pamięć podręczna KV, ciągłe przetwarzanie wsadowe i dekodowanie spekulacyjne mają zastosowanie bezpośrednio.
- **VAE / dyfuzja / dopasowanie przepływu (kosze 2 i 4).** Nie ma dekodowania w sensie LLM. Koszt = `num_steps × step_cost`, a `step_cost` to transformator lub przekaz U-Net w pełnej rozdzielczości utajonej. Pokrętła produkcyjne obejmują liczbę kroków (DDIM / DPM-Solver / destylacja), wielkość partii i precyzję (bf16 / fp8 / int4).
- **GAN (wiadro 3).** Jedno podanie w przód. Bez harmonogramu, bez pamięci podręcznej KV. TTFT ≈ całkowite opóźnienie. Właśnie dlatego StyleGAN nadal wygrywa w przypadku UX w wąskiej domenie.

Kiedy w streszczeniu artykułu widzisz „szybciej niż dyfuzja”, przetłumacz to na „mniej kroków × ten sam koszt kroku” lub „te same kroki × tańszy koszt kroku”. Wszystko inne to marketing.

## Dalsze czytanie

- [Goodfellow i in. (2014). Generacyjne sieci kontradyktoryjne](https://arxiv.org/abs/1406.2661) — artykuł GAN.
- [Kingma i Welling (2013). Auto-Encoding Variational Bayes](https://arxiv.org/abs/1312.6114) — artykuł VAE.
- [Ho, Jain, Abbeel (2020). Denoising Diffusion Probabilistic Models](https://arxiv.org/abs/2006.11239) — artykuł DDPM.
- [Song i in. (2021). Modelowanie generatywne oparte na wynikach za pomocą SDE](https://arxiv.org/abs/2011.13456) — rozpowszechnianie jako SDE.
- [Lipman i in. (2023). Dopasowywanie przepływów w modelowaniu generatywnym](https://arxiv.org/abs/2210.02747) — dokument dotyczący dopasowywania przepływów.
- [Esser i in. (2024). Skalowanie rektyfikowanych transformatorów przepływowych do syntezy obrazu w wysokiej rozdzielczości](https://arxiv.org/abs/2403.03206) — Stable Diffusion 3.