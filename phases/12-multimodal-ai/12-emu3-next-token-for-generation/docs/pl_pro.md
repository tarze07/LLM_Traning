# Emu3: Przewidywanie następnego tokenu w generowaniu obrazu i wideo

> Publikacja o modelu BAAI Emu3 (Wang et al., wrzesień 2024) to przełomowa praca z 2024 roku, która miała na celu zakończenie debaty dotyczącej wyboru pomiędzy modelami dyfuzyjnymi a autoregresyjnymi w syntezie obrazów. Pojedynczy transformator typu decoder-only (o strukturze zbliżonej do Llama), trenowany wyłącznie na zadaniu przewidywania następnego tokenu (Next-Token Prediction) w ramach zunifikowanego słownika (tekst + dyskretne tokeny obrazu VQ + czasoprzestrzenne tokeny wideo 3D VQ), pokonuje model SDXL w generowaniu obrazów oraz model LLaVA-1.6 pod kątem samej percepcji. Model ten nie wymaga straty CLIP ani harmonogramu dyfuzji (diffusion schedule). Podczas wnioskowania (inference) jakość generowania jest poprawiana techniką Classifier-Free Guidance (CFG), lecz głównym celem treningowym pozostaje przewidywanie kolejnego elementu przy użyciu metody teacher forcing. Publikacja ta ukazała się w czasopiśmie Nature. W tej lekcji przeanalizujemy założenia Emu3 — wyjaśniając, dlaczego wysokiej jakości tokenizer oraz odpowiednia skala to wszystko, czego potrzebujesz — i porównamy ten kierunek z podejściem dyfuzyjnym.

**Typ:** Teoria / Zrozumienie
**Języki:** Python (biblioteka standardowa, obliczenia dla tokenizatora wideo 3D + szkielet próbnika autoregresyjnego)
**Wymagania:** Faza 12 · Lekcja 11 (Chameleon)
**Czas:** ~120 minut

## Cele nauczania

- Wyjaśnij, dlaczego cel przewidywania następnego tokenu (Next-Token Prediction) z jedną funkcją straty w Emu3 sprawdza się w syntezie obrazu, wbrew powszechnemu przekonaniu, że do wysokiej jakości wymagany jest proces dyfuzji.
- Opisz działanie tokenizatora wideo 3D: strukturę czasoprzestrzennej książki kodowej VQ (spatiotemporal codebook) oraz powód próbkowania patchy w czasie.
- Porównaj model Emu3 z modelem Stable Diffusion XL pod kątem: kosztów obliczeniowych treningu, kosztów wnioskowania oraz limitów jakościowych generowania.
- Omów trzy role użytkowe realizowane przez ten sam model Emu3: Emu3-Gen (generowanie obrazów), Emu3-Chat (percepcja/rozumienie) oraz Emu3-Stage2 (generowanie wideo).

## Problem

Powszechne przekonanie w świecie AI do roku 2024 zakładało, że wysoka jakość generowania obrazów wymaga procesów dyfuzyjnych. Argumentowano, że dyskretne tokeny obrazu niosą ze sobą zbyt duże straty informacji, by wiernie rekonstruować drobne szczegóły, a autoregresywne próbkowanie kumuluje błędy przy generowaniu sekwencji o długości tysięcy tokenów. Z tego powodu modele takie jak Stable Diffusion, DALL-E 3, Imagen czy Midjourney korzystały z metod dyfuzyjnych. Model Chameleon (Lekcja 12.11) częściowo podważył tę tezę w mniejszej skali, ale jego jakość wciąż wyraźnie ustępowała modelowi SDXL.

Twórcy Emu3 postanowili bezpośrednio zmierzyć się z tym problemem. Ich teza brzmiała: wysokiej jakości tokenizer wizualny + odpowiednia skala modelu + standardowa strata NTP = generowanie obrazów przewyższające modele dyfuzyjne w ramach tej samej architektury, która odpowiada za zadania percepcji.

Założenie to budziło spore kontrowersje w momencie publikacji. Dwa lata później zunifikowane modele generatywne open-source (takie jak Emu3, Show-o, Janus-Pro czy Transfusion) stały się jednym z głównych kierunków badawczo-rozwojowych, a najsilniejsze komercyjne modele VLM korzystają z pokrewnych rozwiązań.

## Koncepcja

### Tokenizer Emu3

Kluczowym elementem systemu jest tokenizer wizualny. W Emu3 zastosowano niestandardowy tokenizer klasy IBQ (Inverse Bottleneck Quantizer, z rodziny SBER-MoVQGAN) o stopniu kompresji (downsampling factor) 8x8 na token. Obraz o rozdzielczości 512x512 pikseli jest konwertowany do postaci 64x64 = 4096 tokenów przy rozmiarze książki kodowej (codebook size) równym 32768.

To znacznie gęstsza reprezentacja niż 1024 tokeny Chameleona przy K=8192, a jednocześnie wydajniejsza w obliczeniach (mniejszy narzut wyszukiwania w książce kodowej i prostszy kodek). Kluczowy wskaźnik: jakość rekonstrukcji wskaźnika PSNR wynosi 30,5 dB, co jest wynikiem bardzo bliskim ciągłej przestrzeni latentnej Stable Diffusion (32 dB).

Dla wideo: trójwymiarowy tokenizer 3D VQ koduje czasoprzestrzenne bloki (kostki o wymiarach 4x4x4 piksele) w pojedyncze indeksy (liczby całkowite). Przykładowo, 4-sekundowe nagranie wideo przy 8 FPS zawiera 32 klatki. Przy rozdzielczości 256x256 i redukcji 4x w wymiarze przestrzennym oraz 4x w wymiarze czasowym, liczba tokenów wynosi: (256/4) * (256/4) * (32/4) = 64 * 64 * 8 = 32 768 tokenów.

Jakość rekonstrukcji tokenizera wyznacza ostateczną poprzeczkę jakościową modelu. Sukces Emu3 wynika w dużej mierze z udanego wytrenowania bardzo precyzyjnego tokenizera.

### Trening z jedną funkcją straty

Emu3 optymalizuje jeden spójny cel: przewidywanie następnego tokenu (Next-Token Prediction) ze wspólnego słownika obejmującego tokeny tekstowe, dwuwymiarowe tokeny obrazów oraz trójwymiarowe tokeny wideo. Wagi funkcji straty są odpowiednio skalowane w zależności od modalności w celu zbalansowania treningu, ale sama formuła matematyczna straty pozostaje identyczna.

Trening jest realizowany na zróżnicowanym miksie zadań:
- Generowanie obrazu: `<opis tekstowy> <image> tokeny_obrazu </image>`
- Percepcja obrazu: `<image> tokeny_obrazu </image> <pytanie> tokeny_tekstu`
- Generowanie wideo: `<opis tekstowy> <video> tokeny_wideo </video>`
- Percepcja wideo: analogicznie.
- Czysty tekst: standardowa strata NTP na modelowaniu języka.

Dzięki temu model uczy się samodzielnie decydować, kiedy generować tokeny wizualne, a kiedy tekstowe bezpośrednio z dystrybucji danych. Synteza obrazu rozpoczyna się automatycznie po napotkaniu tagu `<image>`.

### Classifier-Free Guidance (CFG) i dobór temperatury

Jakość autoregresywnego generowania obrazów ulega znacznej poprawie dzięki wdrożeniu techniki Classifier-Free Guidance (CFG) podczas wnioskowania. Emu3 generuje dwa przebiegi równolegle: jeden z podanym opisem tekstowym (warunkowy), a drugi z pustym opisem (bezwarunkowy), a następnie odpowiednio modyfikuje wyjściowe logity z wybranym współczynnikiem wagowym (zazwyczaj w zakresie 3.0-7.0). Metoda ta została zaadaptowana bezpośrednio z modeli dyfuzyjnych.

Istotną rolę odgrywa temperatura próbkowania: zbyt wysokie wartości powodują powstawanie artefaktów wizualnych, natomiast zbyt niskie mogą prowadzić do zapętlania generowania. Autorzy Emu3 rekomendują temperaturę 1.0 dla zadań percepcji i 0.8 dla zadań generowania obrazów.

### Trzy role użytkowe, jedne wagi modelu

Emu3 udostępnia trzy różne interfejsy API, zaimplementowane na bazie dokładnie tych samych wag modelu:

- Emu3-Gen. Służy do generowania obrazów. Wejście: tekst, wyjście: tokeny obrazu.
- Emu3-Chat. Służy do zadań VQA (odpowiadanie na pytania) oraz opisywania obrazów. Wejście: obraz, wyjście: tekst.
- Emu3-Stage2. Służy do generowania wideo i zadań wideo-VQA. Wejście: tekst lub wideo, wyjście: tekst lub wideo.

Model nie posiada osobnych głowic dla poszczególnych zadań. Różne zachowania są wywoływane wyłącznie za pomocą szablonów promptów.

### Wyniki benchmarków

Dane z publikacji o Emu3 (wrzesień 2024):

- Generowanie obrazów: model pokonał SDXL w benchmarku jakościowym MJHQ-30K pod kątem wskaźnika FID (5,4 vs 5,6), w teście GenEval uzyskał wynik porównywalny (0,54 vs 0,55 — różnica nieznacząca statystycznie) i zrównał się z nim w teście Deep-Eval.
- Percepcja obrazów: model pokonał LLaVA-1.6 w benchmarku VQAv2 (75,1% vs 72,4%) i uzyskał zbliżone wyniki w teście MMMU.
- Generowanie wideo: jakość 4-sekundowych nagrań wskaźnika FVD była w pełni konkurencyjna w stosunku do modeli z okresu debiutu modelu Sora.

Ostateczne dane potwierdzają, że cel zunifikowanego modelowania języka (Next-Token Prediction) jest w pełni realną alternatywą dla modeli dyfuzyjnych.

### Koszty obliczeniowe

Emu3 w wersji 7B przeszkolono na około 300 miliardach tokenów multimodalnych. Zasoby obliczeniowe zużyte na pretrening są porównywalne z pretreningiem modelu Llama-2-7B (szacunkowo 2000-4000 roboczych godzin kart klasy A100). Modele dyfuzyjne (np. Stable Diffusion 3) mają podobne wymagania obliczeniowe, lecz wymagają stosowania osobnych encoderów tekstowych i bardziej skomplikowanych potoków wnioskowania.

Głównym minusem Emu3 jest czas generowania obrazu: sekwencyjne wygenerowanie 4096 tokenów przy przepustowości 30 tokenów/sekundę zajmuje około 2 minut dla obrazu 512x512 pikseli, podczas gdy SDXL wykonuje to w 2-5 sekund. Zastosowanie technik takich jak dekodowanie spekulatywne (speculative decoding) oraz optymalizacja pamięci podręcznej KV Cache pozwala na redukcję tej luki, lecz jej nie eliminuje. Autoregresywna synteza obrazu jest naturalnie bardzo kosztowna obliczeniowo przy wnioskowaniu.

### Dlaczego ta koncepcja jest ważna

Kluczowy wniosek z Emu3 ma charakter koncepcyjny. Jeśli prosta strata NTP potrafi z powodzeniem konkurować z dyfuzją w zadaniach syntezy obrazów, to budowa zunifikowanego modelu multimodalnego (jedna funkcja straty, jedne wagi, dowolny typ danych) jest w pełni realna. Przyszłe modele nie będą wymagały osobnych encoderów tekstowych, skomplikowanych harmonogramów dyfuzji czy oddzielnych struktur VAE. Wystarczy jeden transformator ze zoptymalizowanym tokenizerem dla każdej z modalności.

Tezy te rozwijają lub weryfikują kolejne modele, takie jak Show-o, Janus-Pro oraz InternVL-U.

## Użycie praktyczne

Skrypt `code/main.py` zawiera:

- Kalkulator rozmiaru tokenów dla VQ 2D i 3D: na podstawie rozdzielczości, rozmiaru patcha, czasu nagrania oraz FPS wylicza liczbę tokenów dla obrazu i wideo.
- Generator próbkowania autoregresyjnego z implementacją techniki Classifier-Free Guidance (CFG) i parametrem temperatury.

Kod symuluje łączenie logitów warunkowych i bezwarunkowych zgodnie ze specyfikacją Emu3.

## Zadanie zaliczeniowe

W ramach tej lekcji należy stworzyć dokument `outputs/skill-token-gen-cost-analyzer_pro.md`. Na podstawie specyfikacji docelowego produktu (typ syntezy, docelowa rozdzielczość, pożądana jakość obrazu, budżet opóźnień), oblicz zapotrzebowanie na tokeny, szacowany koszt wnioskowania i wybierz pomiędzy modelami z rodziny Emu3 a dedykowanymi potokami dyfuzyjnymi.

## Ćwiczenia

1. Emu3 generuje 4096 tokenów dla obrazu 512x512 przy stopniu kompresji 8x8. Oblicz odpowiednią liczbę tokenów dla rozdzielczości 1024x1024 oraz 2048x2048. Wyjaśnij, jak wpłynie to na opóźnienia (latency) wnioskowania.

2. Przeczytaj sekcję 3.3 w artykule o Emu3 dotyczącą tokenizatora wideo. Opisz strukturę przestrzenną bloku 3D VQ i wyjaśnij, dlaczego wybrano format 4x4x4 zamiast 8x8x1.

3. Porównaj wizualny wpływ parametru wagi Classifier-Free Guidance (CFG) ustawionego na 5.0 w stosunku do wartości 3.0. Przeanalizuj odpowiednie wyliczenia w pliku `code/main.py`.

4. Oblicz łączną liczbę operacji FLOPs potrzebnych do wytrenowania Emu3-7B na zbiorze 300B tokenów i porównaj ten wynik ze Stable Diffusion 3. Trening którego z modeli był bardziej kosztowny?

5. Emu3 wygrywa z SDXL w benchmarku FID, ale ustępuje dedykowanym modelom VLM w zadaniach VQAv2. Wyjaśnij, dlaczego podejście oparte na jednej zunifikowanej funkcji straty daje zróżnicowane wyniki w zależności od specyfiki benchmarku.

## Słownik pojęć

| Termin | Potoczne określenie | Co to dokładnie oznacza |
|------|-----------------|--------------------------------------|
| Przewidywanie następnego tokenu (NTP) | „Next-Token Prediction” | Autoregresyjna funkcja straty: przewidywanie kolejnego tokenu na podstawie historii sekwencji; uniwersalna dla tekstu i obrazów. |
| Tokenizer IBQ | „Inverse Bottleneck Quantizer” | Zaawansowana wersja VQ-VAE o większym rozmiarze książki kodowej (32768+) pozwalająca na lepszą rekonstrukcję szczegółów. |
| VQ 3D | „Spatiotemporal quantizer” | Tokenizer czasoprzestrzenny, w którym pojedynczy token opisuje blok pikseli w wymiarze przestrzenno-czasowym (np. kostka 4x4x4). |
| Classifier-Free Guidance | „CFG” | Metoda poprawy jakości syntezy poprzez liniowe łączenie logitów generowania warunkowanego tekstem i bezwarunkowego. |
| Zunifikowane słownictwo | „Shared vocabulary” | Wspólna przestrzeń indeksów tokenów dla tekstu, obrazu i wideo, umożliwiająca przetwarzanie ich jednym transformatorem. |
| MJHQ-30K | „Benchmark Midjourney” | Zbiór 30 tysięcy promptów służący do oceny jakości generowania obrazów wysokiej rozdzielczości pod kątem wskaźnika FID. |

## Dalsze czytanie

- [Wang et al. — Emu3: Next-Token Prediction is All You Need (arXiv:2409.18869)](https://arxiv.org/abs/2409.18869)
- [Sun et al. — Emu: Generative Pretraining in Multimodality (arXiv:2307.05222)](https://arxiv.org/abs/2307.05222)
- [Liu et al. — LWM: Large World Model (arXiv:2402.08268)](https://arxiv.org/abs/2402.08268)
- [Yu et al. — MAGVIT-v2 (arXiv:2310.05737)](https://arxiv.org/abs/2310.05737)
- [Tian et al. — VAR (arXiv:2404.02905)](https://arxiv.org/abs/2404.02905)
