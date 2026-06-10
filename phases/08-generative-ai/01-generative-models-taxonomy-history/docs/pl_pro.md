# Modele generatywne — taksonomia i historia

> Każdy model obrazu, tekstu, wideo i 3D należy do jednej z pięciu rodzin. Wybierz niewłaściwą, a będziesz zmagał się z matematyką przez tygodnie. Wybierz właściwą, a dwanaście lat postępu w tej dziedzinie ułoży się w spójny obraz.

**Typ:** Ucz się
**Języki:** Python
**Wymagania wstępne:** Faza 2 (Podstawy ML), Faza 3 (Rdzeń głębokiego uczenia się), Faza 7 · 14 (Transformatory)
**Czas:** ~45 minut

## Problem

Model generatywny realizuje jedno zadanie: dysponując próbkami treningowymi z nieznanego rozkładu `p_data(x)`, generuje nowe próbki, które wyglądają, jakby z tego samego rozkładu pochodziły. Twarze, zdania, pliki MIDI, struktury białkowe — to ten sam problem, jeśli spojrzeć nań z odpowiedniej perspektywy.

Trudność polega na tym, że `p_data` leży w przestrzeni o milionach wymiarów (obraz RGB 512×512 ma blisko 786 tys. wymiarów), próbki skupiają się na cienkiej rozmaitości wewnątrz tej przestrzeni, a dostępnych danych jest najwyżej kilkanaście milionów. Bezpośrednie estymowanie gęstości jest w takich warunkach nierealne. Każdy model generatywny to kompromis: jeden trudny problem zastępuje się nieco łatwiejszym.

W ciągu ostatnich dwunastu lat ukształtowało się pięć rodzin. Zrozumienie, na jaki kompromis zdecydowała się każda z nich, wyjaśnia, dlaczego jedne zadania rozwiązuje doskonale, a przy innych zawodzi.

## Koncepcja

![Pięć rodzin modeli generatywnych — taksonomia według tego, co modelują](../assets/taxonomy.svg)

**1. Jawna gęstość, obliczalnie wykonalna.** `log p(x)` jest zapisywane jako suma dająca się bezpośrednio oszacować. Modele autoregresyjne (PixelCNN, WaveNet, GPT) rozkładają `p(x) = ∏ p(x_i | x_<i)`. Normalizujące przepływy (RealNVP, Glow) konstruują `p(x)` jako odwracalne przekształcenie prostego rozkładu bazowego. Zaleta: dokładne prawdopodobieństwo i przejrzysta funkcja straty. Wada: wnioskowanie autoregresyjne jest sekwencyjne (wolne dla długich ciągów), a przepływy wymagają architektur odwracalnych, co ogranicza swobodę projektowania.

**2. Jawna gęstość, przybliżona.** `log p(x)` jest ograniczane od dołu przez ELBO, które następnie się optymalizuje. VAE (Kingma 2013) korzystają z architektury koder–dekoder z wariacyjnym wnioskowaniem. Modele dyfuzji (DDPM, Ho 2020) trenują odszumiacz pośrednio optymalizujący ważone ELBO. Dyfuzja pozostaje dominującym szkieletem dla obrazu, wideo i 3D w roku 2026.

**3. Ukryta gęstość.** Gęstość jest pomijana w całości. Zamiast tego uczy się generatora `G(z)` produkującego próbki oraz dyskryminatora `D(x)` odróżniającego oryginały od fałszywek. To podejście stosują sieci GAN (Goodfellow 2014). Wnioskowanie jest szybkie (jedno przejście w przód), lecz trening bywa niestabilny. StyleGAN 1/2/3 pozostaje najlepszą metodą do fotorealistycznej syntezy w wąskich dziedzinach (twarze, wnętrza) jeszcze w 2026 roku.

**4. Oparte na wyniku / ciągłe w czasie.** Model uczy się bezpośrednio gradientu logarytmu gęstości `∇_x log p(x)` (tzw. score). Song i Ermon (2019) wykazali, że dopasowanie wyniku uogólnia dyfuzję na równania różniczkowe stochastyczne (SDE). Dopasowanie przepływu (Lipman 2023) to nowość lat 2024–2026: trening bez symulacji, prostsze trajektorie próbkowania, cztery do dziesięciu razy szybsze generowanie niż DDPM. Korzystają z niego Stable Diffusion 3, Flux i AudioCraft 2.

**5. Autoregresja na tokenach dyskretnych.** Dane o dużej wymiarowości są kompresowane przez VQ-VAE lub kwantyzator resztkowy do krótkiej sekwencji dyskretnych tokenów, którą modeluje transformator. Tego podejścia używają Parti, MuseNet, AudioLM, VALL-E oraz tokenizator łatek Sory. To rodzina pierwsza wzbogacona o wyuczony tokenizator.

## Krótka historia

| Rok | Model | Znaczenie |
|------|-------|-----------|
| 2013 | VAE (Kingma) | Pierwszy głęboki model generatywny z użyteczną funkcją straty. |
| 2014 | GAN (Goodfellow) | Ukryta gęstość, brak prawdopodobieństwa — zaskakująco ostre próbki. |
| 2015 | DRAW, PixelCNN | Sekwencyjne generowanie obrazu. |
| 2017 | Glow, RealNVP | Odwracalne przepływy; dokładne prawdopodobieństwo z głębokimi sieciami. |
| 2017 | Progressive GAN | Pierwsze twarze w rozdzielczości megapikselowej. |
| 2019 | StyleGAN / StyleGAN2 | Fotorealistyczne twarze bez konkurencji w tej domenie. |
| 2020 | DDPM (Ho) | Dyfuzja staje się praktyczna. |
| 2021 | CLIP, DALL-E 1, VQGAN | Generowanie obrazu z tekstu wchodzi do głównego nurtu. |
| 2022 | Imagen, Stable Diffusion 1, DALL-E 2 | Dyfuzja latentna z warunkowaniem tekstowym staje się produktem. |
| 2022 | ControlNet, LoRA | Precyzyjna kontrola nad wytrenowanymi modelami dyfuzji. |
| 2023 | SDXL, Midjourney v5, dopasowanie przepływu | Większa skala i lepsza dynamika treningu. |
| 2024 | Sora, Stable Diffusion 3, Flux.1 | Dyfuzja dla wideo; dopasowanie przepływu dominuje. |
| 2025 | Veo 2, Kling 1.5, Runway Gen-3, Minimax | Film na poziomie produkcyjnym. |
| 2026 | Modele spójności + ulepszone przepływy | Próbkowanie jednoetapowe ze szkieletów dyfuzyjnych. |

## Pięć pytań klasyfikujących

Kiedy pojawia się nowy artykuł o modelu generatywnym, przed przeczytaniem sekcji metodycznej odpowiedz na pięć poniższych pytań.

1. **Co jest modelowane?** Piksele, reprezentacje latentne, dyskretne tokeny, gaussiany 3D, siatki, przebiegi?
2. **Czy gęstość jest jawna czy ukryta?** Czy model zapisuje `log p(x)`?
3. **Próbkowanie: jednorazowe czy iteracyjne?** Iteracyjne oznacza wolniejsze wnioskowanie; jednorazowe zwykle wiąże się z podejściem kontradyktoryjnym lub destylacją.
4. **Warunkowanie: bezwarunkowe, klasą, tekstem, obrazem, pozą?** Decyduje to o funkcji straty i architekturze.
5. **Ewaluacja: FID, wynik CLIP, IS, oceny ludzkie, dokładność zadania?** Każda miara ma znane słabości (zob. Lekcja 14).

Do tych pięciu pytań będziesz wracał przy każdej lekcji w tej fazie. Z czasem odpowiadanie na nie stanie się odruchem.

## Zbuduj to

Kod do tej lekcji to uproszczona wizualizacja: dopasowuje jednowymiarową mieszaninę Gaussów do próbek za pomocą trzech uproszczonych metod (estymacja jądrowa, histogram dyskretny oraz generator zbliżony do GAN), aby pokazać różnicę między jawną a ukrytą gęstością na przykładzie mieszczącym się na jednym ekranie.

Uruchom `code/main.py`. Pobiera 2000 próbek z dwumodalnej mieszaniny Gaussów i wypisuje:

```
explicit density (histogram): p(x in [-0.5, 0.5]) ≈ 0.38
approximate density (KDE):     p(x in [-0.5, 0.5]) ≈ 0.41
implicit (nearest-sample gen): 20 new samples printed, no p(x)
```

Uwaga: pierwsze dwie metody pozwalają zapytać „jak prawdopodobny jest ten punkt?" Trzecia — nie. To jest właśnie rozróżnienie między *gęstością jawną a ukrytą*, które będzie istotne podczas każdej kolejnej lekcji.

## Użyj tego

Która rodzina, do jakiego zadania w 2026 roku?

| Zadanie | Najlepsza rodzina | Uzasadnienie |
|---------|-------------------|--------------|
| Fotorealistyczne twarze, wąska domena | StyleGAN 2/3 | Najostrzejsze wyniki przy najszybszym wnioskowaniu. |
| Generowanie obrazu z tekstu, ogólne | Dyfuzja latentna + dopasowanie przepływu | SD3, Flux.1, DALL-E 3. |
| Szybkie generowanie obrazu z tekstu | Prostowany przepływ + destylacja | SDXL-Turbo, SD3-Turbo, LCM. |
| Generowanie wideo z tekstu | Transformator dyfuzyjny + dopasowanie przepływu | Sora, Veo 2, Kling. |
| Mowa i muzyka | Autoregresja na tokenach (AudioLM, VALL-E, MusicGen) lub dopasowanie przepływu (AudioCraft 2) | Dyskretne tokeny skalują się tanio. |
| Sceny 3D | Rozpraszanie gaussowskie, poprzedzone dyfuzją | 3D-GS do rekonstrukcji, dyfuzja do syntezy nowych widoków. |
| Estymacja gęstości (bez próbkowania) | Przepływy | Jedyna rodzina dająca dokładne `log p(x)`. |
| Symulacja / fizyka | Dopasowanie przepływu, SDE z wynikiem | Proste trajektorie, gładkie pola wektorowe. |

## Wyślij to

Zapisz jako `outputs/skill-model-chooser.md`.

Opis umiejętności powinien zawierać: (1) wskazanie właściwej rodziny modeli, (2) zestawienie trzech opcji open-source i trzech hostowanych w kolejności od najlepszej, (3) prawdopodobny tryb awarii, na który należy uważać, oraz (4) szacowany budżet obliczeniowy i czasowy.

## Ćwiczenia

1. **Łatwe.** Dla każdego z pięciu poniższych produktów określ rodzinę i szkielet: ChatGPT Image, Midjourney v7, Sora, Runway Gen-3, ElevenLabs. Uzasadnienie powinno opierać się na publicznych raportach technicznych.
2. **Średnie.** Przeczytany jutro artykuł twierdzi, że próbkowanie jest 100 razy szybsze niż w dyfuzji. Zapisz trzy pytania sprawdzające, czy to przyspieszenie utrzymuje się przy warunkowaniu i wysokiej rozdzielczości.
3. **Trudne.** Wybierz domenę, która Cię interesuje (np. struktura białek, CAD, cząsteczki, trajektorie). Zastosuj pięciopytaniową klasyfikację do aktualnego modelu SOTA w tej dziedzinie i naszkicuj, co zmieniłby lepszy model.

## Kluczowe terminy

| Termin | Potoczne znaczenie | Precyzyjne znaczenie |
|--------|--------------------|----------------------|
| Model generatywny | „Tworzy nowe rzeczy" | Uczy się próbnika dla `p_data(x)`, opcjonalnie udostępniając `log p(x)`. |
| Jawna gęstość | „Możesz ją wyliczyć" | Model podaje analityczną lub obliczalnie wykonalną formę `log p(x)`. |
| Ukryta gęstość | „W stylu GAN" | Tylko próbnik — nie ma możliwości obliczenia `p(x)` dla danego punktu. |
| ELBO | „Dolna granica prawdopodobieństwa danych" | Traktowalne dolne ograniczenie `log p(x)`; optymalizują je VAE i dyfuzja. |
| Wynik (score) | „Gradient logarytmu gęstości" | `∇_x log p(x)`; modele dyfuzyjne i SDE uczą się tego pola. |
| Hipoteza rozmaitości | „Dane leżą na powierzchni" | Dane wysokowymiarowe koncentrują się na rozmaitości o niskiej wymiarowości; wyjaśnia, dlaczego redukcja wymiarowości działa. |
| Autoregresja | „Przewiduj kolejny element" | Rozkład łączny jako iloczyn rozkładów warunkowych. |
| Latentne (ukryte) | „Skompresowany kod" | Niskowy­miarowa reprezentacja, z której dekoder potrafi odtworzyć wejście. |

## Uwaga produkcyjna: pięć rodzin, pięć profili wnioskowania

Każda rodzina przekłada się na inną krzywą kosztów serwera wnioskowania. Literatura o produkcyjnym wnioskowaniu LLM wyróżnia fazę wstępnego wypełniania i fazę dekodowania; ten sam podział ma tu zastosowanie:

- **Autoregresja (rodziny 1 i 5).** Sekwencyjne dekodowanie dominuje w opóźnieniu; pamięć podręczna KV, ciągłe przetwarzanie wsadowe i dekodowanie spekulatywne są tu bezpośrednio przydatne.
- **VAE / dyfuzja / dopasowanie przepływu (rodziny 2 i 4).** Dekodowanie w sensie LLM nie istnieje. Koszt = `num_steps × step_cost`, gdzie `step_cost` to pełne przejście przez transformator lub U-Net w latentnej rozdzielczości. Parametry produkcyjne to liczba kroków (DDIM / DPM-Solver / destylacja), rozmiar partii i precyzja (bf16 / fp8 / int4).
- **GAN (rodzina 3).** Jedno przejście w przód. Brak harmonogramu i pamięci podręcznej KV. Czas do pierwszego tokenu jest równy całkowitemu opóźnieniu. Dlatego StyleGAN wciąż wygrywa w zastosowaniach wymagających niskiego opóźnienia w wąskich domenach.

Kiedy w streszczeniu artykułu widzisz sformułowanie „szybszy niż dyfuzja", przetłumacz je na „mniej kroków przy tym samym koszcie kroku" albo „te same kroki przy tańszym kroku". Wszystko inne to marketing.

## Dalsze czytanie

- [Goodfellow i in. (2014). Generative Adversarial Nets](https://arxiv.org/abs/1406.2661) — artykuł oryginalny GAN.
- [Kingma i Welling (2013). Auto-Encoding Variational Bayes](https://arxiv.org/abs/1312.6114) — artykuł oryginalny VAE.
- [Ho, Jain, Abbeel (2020). Denoising Diffusion Probabilistic Models](https://arxiv.org/abs/2006.11239) — artykuł oryginalny DDPM.
- [Song i in. (2021). Score-Based Generative Modeling through Stochastic Differential Equations](https://arxiv.org/abs/2011.13456) — dyfuzja jako SDE.
- [Lipman i in. (2023). Flow Matching for Generative Modeling](https://arxiv.org/abs/2210.02747) — artykuł o dopasowaniu przepływu.
- [Esser i in. (2024). Scaling Rectified Flow Transformers for High-Resolution Image Synthesis](https://arxiv.org/abs/2403.03206) — Stable Diffusion 3.
