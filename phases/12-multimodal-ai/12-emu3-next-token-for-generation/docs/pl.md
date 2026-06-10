# Emu3: Przewidywanie następnego tokenu do generowania obrazu i wideo

> Wynik BAAI Emu3 (Wang i in., wrzesień 2024 r.) to wynik z 2024 r., który powinien był zakończyć debatę na temat dyfuzji kontra autoregresji. Pojedynczy transformator typu lama, przeznaczony wyłącznie do dekodera, przeszkolony tylko w zakresie przewidywania następnego tokena, w ramach ujednoliconego słownictwa tekstu + tokenów obrazu VQ + tokenów wideo 3D VQ, pokonuje SDXL pod względem generowania obrazu i LLaVA-1.6 pod względem percepcji. Brak utraty CLIP. Brak harmonogramu rozpowszechniania. Przy wnioskowaniu dotyczącym jakości wykorzystywane są wskazówki wolne od klasyfikatorów, ale głównym celem szkolenia jest przewidywanie następnego elementu za pomocą wymuszania przez nauczyciela. Opublikowano w Naturze. W tej lekcji czytamy tezę Emu3 – dlaczego lepszy tokenizator i skala to wszystko, czego potrzebujesz – i kontrastuje z podejściem dyfuzyjnym.

**Typ:** Ucz się
**Języki:** Python (stdlib, matematyka tokenizatora wideo 3D + szkielet autoregresyjnego próbnika)
**Wymagania:** Faza 12 · 11 (Kameleon)
**Czas:** ~120 minut

## Cele nauczania

- Wyjaśnij, dlaczego cel następnego żetonu z pojedynczą stratą w Emu3 działa pomimo od dawna utrzymywanego założenia, że dla jakości obrazu wymagana jest dyfuzja.
- Opisz tokenizator wideo 3D: jak wygląda czasoprzestrzenny słownik kodów VQ, dlaczego poprawki obejmują czas.
- Porównaj Emu3 vs Stable Diffusion XL na (obliczenia szkoleniowe, koszt wnioskowania, pułap jakości).
- Wymień trzy role, jakie odgrywa ten sam model Emu3: Emu3-Gen (generowanie obrazu), Emu3-Chat (percepcja), Emu3-Stage2 (generowanie wideo).

## Problem

Obiegowa mądrość do roku 2024: generowanie obrazu wymaga rozpowszechniania. Argument: dyskretne tokeny obrazu tracą zbyt wiele informacji, aby zrekonstruować szczegóły, a próbkowanie autoregresyjne gromadzi błąd w tysiącach tokenów. Stable Diffusion, DALL-E 3, Imagen, Midjourney wykorzystują jakąś formę dyfuzji. Chameleon (lekcja 12.11) częściowo obalił to na małą skalę, ale nie dorównywał SDXL pod względem jakości.

Emu3 bezpośrednio zaatakowało tę argumentację. Twierdzenie: lepszy tokenizator wizualny + wystarczająca skala + strata następnego tokena = generowanie obrazu pokonującego dyfuzję w tym samym modelu, który również zapewnia percepcję.

Zakład był kontrowersyjny, kiedy został opublikowany. Dwa lata później rodzina zunifikowanej generacji open source (Emu3, Show-o, Janus-Pro, Transfusion) stała się domyślną ścieżką badań; Wydaje się, że modele z pogranicza produkcji korzystają z jakiegoś wariantu.

## Koncepcja

### Tokenizer Emu3

Kluczowym składnikiem jest tokenizator wizualny. Emu3 trenuje niestandardowy tokenizator klasy IBQ (odwrotny kwantyzator wąskiego gardła, rodzina SBER-MoVQGAN) przy redukcji rozdzielczości 8x8 na token. Obraz o wymiarach 512 x 512 zmienia się w 64 x 64 = 4096 tokenów przy rozmiarze książki kodowej 32768.

To więcej niż 1024 tokeny Chameleona na 512x512 przy K=8192, ale tańsze w przeliczeniu na token (mniejsze wyszukiwanie w książce kodów, prostszy kodek). Kluczowy wskaźnik: rekonstrukcja PSNR przy 30,5 dB, konkurencyjna w stosunku do ciągłej przestrzeni utajonej Stable Diffusion przy 32 dB.

W przypadku wideo: tokenizator 3D VQ koduje fragment czasoprzestrzenny (4x4x4 piksele) do jednej liczby całkowitej. Klip 4s przy 8 klatkach na sekundę ma 32 klatki; przy 256x256 z 4x przestrzenną i 4x czasową redukcją, liczba tokenów wynosi (256/4) * (256/4) * (32/4) = 64 * 64 * 8 = 32 768 tokenów.

Jakość tokenizera to pułap. Wkład Emu3 polega częściowo na tym, że „wyszkoliliśmy bardzo dobrego tokenizatora”.

### Trening z jedną stratą

Emu3 ma jeden cel: przewidywanie następnego tokenu na podstawie wspólnego słownictwa w tokenach tekstowych, tokenach obrazów 2D i tokenach wideo 3D. Wagi są mnożone podczas treningu przez czynniki specyficzne dla modalności, aby zrównoważyć wkład, ale funkcja straty jest identyczna.

Trenuj na mieszance:
- Generowanie obrazu: `<text caption> <image> image_tokens </image>`
- Percepcja obrazu: `<image> image_tokens </image> <question> text_tokens`
- Generowanie wideo: `<text caption> <video> video_tokens </video>`
- Percepcja wideo: analogicznie.
- Tylko tekst: standardowy NTP.

Model uczy się, kiedy emitować tokeny graficzne, a kiedy tokeny tekstowe z dystrybucji danych. Generowanie wyłania się z modelu przewidującego tokeny obrazu po tagu `<image>`.

### Wskazówki i temperatura bez klasyfikatorów

Generowanie obrazów autoregresyjnych staje się znacznie lepsze dzięki prowadzeniu bez klasyfikatorów (CFG) przy wnioskowaniu. Emu3 go używa: wygeneruj dwukrotnie, raz z pełnym podpisem, raz z pustym podpisem, wymieszaj logity z wagą orientacyjną (typowo 3,0-7,0). Jest to ten sam sposób, w jaki wykorzystuje się dyfuzję sztuczek CFG, zapożyczony z ustawieniami autoregresyjnymi.

Temperatura ma znaczenie: zbyt wysoka, artefakty; za niski, tryb załamuje się. Zalecana temperatura Emu3 to 1,0 dla percepcji i 0,8 dla generowania obrazu.

### Trzy role, jeden model

Emu3 jest dostarczany jako trzy funkcjonalnie różne interfejsy API, ale z jednym podstawowym zestawem wag:

- Emu3-Gen. Generowanie obrazu. Tekst wejściowy, tokeny obrazu wyjściowego.
- Czat Emu3. VQA i napisy. Obraz wejściowy (tokeny), tekst wyjściowy.
- Emu3-Stage2. Generowanie wideo i VQA wideo. Wprowadź tekst lub wideo, wyprowadź tekst lub wideo.

Brak szefów zajmujących się określonymi zadaniami. Po prostu różne szablony podpowiedzi. Ten sam punkt kontrolny.

### Testy porównawcze

Z artykułu Emu3 (wrzesień 2024):

- Generowanie obrazu: przewyższa SDXL na MJHQ-30K FID (5,4 vs 5,6), ogólnie GenEval (0,54 vs 0,55 — remis statystyczny) i kompozyt Deep-Eval na równi.
- Percepcja obrazu: przewyższa LLaVA-1.6 na VQAv2 (75,1 vs 72,4) i mniej więcej dorównuje MMMU.
- Generowanie wideo: 4-sekundowa jakość klipu w konkurencyjnym FVD z publicznie testowanymi modelami z ery Sory.

Liczby nie zawsze wygrywają — Emu3 zamienia punkt tutaj na punkt tam — ale twierdzenie, że „wystarczy przewidywanie następnego żetonu” można obronić na wiele sposobów.

### Oblicz koszt

Emu3 został przeszkolony na ~300 miliardach tokenów multimodalnych w modelu z parametrami 7B. Godziny pracy procesora graficznego są w przybliżeniu porównywalne z treningiem wstępnym Llama-2-7B (2–4 tys. lat pracy procesora graficznego na krzemie klasy A100). Modele dyfuzji, takie jak Stable Diffusion 3, mają podobne budżety, ale wymagają oddzielnych koderów tekstu i bardziej złożonych potoków.

Podsumowując, Emu3 jest wolniejszy niż SDXL na obraz: 4096 tokenów obrazu przy 30 tok/s to ~2 minuty na obraz 512x512, w porównaniu z 2-5 sekundami w przypadku SDXL. Dekodowanie spekulatywne i optymalizacja pamięci podręcznej KV zmniejszają lukę, ale jej nie zamykają. Generowanie obrazu autoregresyjnego wymaga dużej mocy obliczeniowej; to jest stały kompromis.

### Dlaczego to ma znaczenie

Głęboki wkład Emu3 ma charakter koncepcyjny. Jeśli przewidywanie następnego tokenu skaluje się w celu dopasowania do dyfuzji podczas generowania obrazu, ścieżka ujednoliconego modelu (jedna strata, jeden szkielet, dowolna modalność) jest wykonalna. Przyszłe modele nie będą potrzebowały oddzielnych koderów tekstu, oddzielnych programów planujących rozpowszechnianie, oddzielnych VAE. Jeden transformator, jeden tokenizator na modalność, skalę.

Show-o, Janus-Pro i InternVL-U opierają się na tej tezzie lub ją kwestionują. Do roku 2025 laboratoria chińskie (BAAI, DeepSeek) publikują w tym kierunku bardziej agresywnie niż laboratoria amerykańskie.

## Użyj tego

`code/main.py` buduje dwa elementy zabawki:

- Kalkulator liczby tokenizerów VQ 2D i 3D: podane (rozdzielczość, łatka, długość_klipu, FPS), oblicz liczbę tokenów dla obrazu i wideo.
- Autoregresyjny próbnik tokenów obrazowych z wytycznymi bez klasyfikatorów w temperaturze.

Implementacja CFG odpowiada przepisowi Emu3 — miesza logity warunkowe i bezwarunkowe z wagą orientacyjną.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-token-gen-cost-analyzer.md`. Biorąc pod uwagę specyfikację produktu generacji (obraz lub wideo, docelowa rozdzielczość, poziom jakości, budżet opóźnień), oblicza liczbę tokenów, koszt wnioskowania i wybiera rodzinę Emu3 vs dyfuzję.

## Ćwiczenia

1. Emu3 produkuje 4096 tokenów na obraz 512x512 przy redukcji 8x8. Oblicz odpowiednik dla 1024x1024 i 2048x2048. Co się dzieje z opóźnieniem wnioskowania?

2. Przeczytaj sekcję 3.3 Emu3 na temat tokenizera wideo. Opisz kształt łaty 3D VQ i dlaczego jest to 4x4x4, a nie 8x8x1.

3. Waga prowadzenia bez klasyfikatorów 5,0 vs 3,0: jaki efekt wizualny? Prześledź obliczenia w `code/main.py`.

4. Oblicz FLOPy szkoleniowe dla Emu3-7B przy żetonach 300B i porównaj z Stable Diffusion 3. Które szkolenie było droższe?

5. Emu3 pokonuje SDXL na FID, ale nie na VQAv2 w porównaniu z wyspecjalizowanymi VLM. Wyjaśnij, dlaczego podejście ujednoliconych strat wykazuje różne mocne strony w porównaniu ze specjalistami w różnych testach porównawczych.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| Przewidywanie następnego tokenu | „NTP” | Standardowa strata autoregresyjna: przewidź token[i+1] podany token[0..i]; działa dla każdej modalności po tokenizacji |
| Tokenizer IBQ | „Odwrotny kwantyzator wąskiego gardła” | Klasa VQ-VAE z większymi słownikami (32768+) i lepszą rekonstrukcją niż Chameleon |
| VQ 3D | „Kwantizer czasoprzestrzenny” | Książka kodowa indeksowana według (czas, wiersz, kol.); jeden żeton pokrywa kostkę pikseli 4x4x4 |
| Wskazówki bez klasyfikatorów | "CFG" | Mieszaj logity warunkowe i bezwarunkowe z wagą gamma; zwiększa jakość obrazu przy wnioskowaniu |
| Ujednolicone słownictwo | „Współdzielone tokeny” | Tekst + obraz + wideo są rysowane z tej samej przestrzeni całkowitej; model przewiduje, która modalność będzie następna |
| MJHQ-30K | „Porównanie generowania obrazu” | Test porównawczy jakości w trakcie podróży z 30 tys. podpowiedzi; Emu3 raportuje tutaj FID |

## Dalsze czytanie

- [Wang i in. — Emu3: wystarczy przewidywanie następnego tokenu (arXiv:2409.18869)](https://arxiv.org/abs/2409.18869)
- [Sun i in. — Emu: Generatywne szkolenie wstępne w zakresie multimodalności (arXiv:2307.05222)](https://arxiv.org/abs/2307.05222)
- [Liu i in. — LWM (arXiv:2402.08268)](https://arxiv.org/abs/2402.08268)
- [Yu i in. — MAGVIT-v2 (arXiv:2310.05737)](https://arxiv.org/abs/2310.05737)
- [Tian i in. — VAR (arXiv:2404.02905)](https://arxiv.org/abs/2404.02905)