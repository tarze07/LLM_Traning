# Receptury treningowe dla modeli VLM open-weight: co naprawdę ma znaczenie

> Literatura dotycząca modeli VLM z lat 2024–2026 to prawdziwy gąszcz badań ablacyjnych. W pracy nad modelem Apple MM1 przetestowano 13 kombinacji encoderów obrazu, adapterów (złączy) oraz miksów danych treningowych. Zespół projektujący model Molmo (Allen AI) udowodnił, że szczegółowe opisy stworzone przez ludzi (human-annotated captions) przewyższają dane syntetyczne wydestylowane z GPT-4V. W projekcie Cambrian-1 przeprowadzono ponad 20 porównań encoderów wizyjnych. Z kolei przy Idefics2 sformalizowano pięcioosiową przestrzeń projektową. Praca Prismatic VLMs zestawiła 27 receptur treningowych w kontrolowanym benchmarku. Z tego szumu informacyjnego wyłania się spójny zestaw wniosków: encoder wizyjny ma większe znaczenie niż architektura samego adaptera, miks danych treningowych jest ważniejszy niż oba te elementy razem wzięte, a szczegółowe opisy ludzkie zdecydowanie przewyższają syntetyczne dane destylowane. Przeanalizowaliśmy te publikacje i tabele za Ciebie.

**Typ:** Teoria + Laboratorium
**Języki:** Python (biblioteka standardowa, analizator tabel ablacyjnych + selektor receptur)
**Wymagania wstępne:** Faza 12 · Lekcja 05 (architektura LLaVA)
**Czas:** ~180 minut

## Cele nauczania

- Zdefiniuj pięcioosiową przestrzeń projektową modeli VLM: encoder wizyjny, adapter (złącze), LLM, miks danych treningowych, harmonogram rozdzielczości.
- Analizuj tabele badań ablacyjnych z prac MM1, Idefics2 oraz Cambrian-1 i prognozuj, która zmiana wpłynie na konkretny benchmark.
- Dobierz optymalną konfigurację (encoder, adapter, dane, rozdzielczość) dla nowego modelu VLM, uwzględniając budżet obliczeniowy oraz specyfikację zadań.
- Wyjaśnij, dlaczego szczegółowe opisy stworzone przez ludzi przewyższają dane syntetyczne z GPT-4V przy zachowaniu tego samego budżetu tokenów.

## Problem

W bazie danych istnieją setki otwartych modeli VLM. Większość różnic dzielących modele „przeciętne” od tych typu „state-of-the-art” nie wynika z samej architektury sieci. Decydujące są: dane treningowe, harmonogram rozdzielczości obrazu oraz dobór encodera. Wiedza o tym, który parametr zmodyfikować w pierwszej kolejności w przypadku słabych wyników modelu, pozwala zaoszczędzić ogromne zasoby obliczeniowe.

Generacja modeli z 2023 roku (LLaVA-1.5, InstructBLIP, MiniGPT-4) opierała się na pretreningu dopasowującym pary obraz-opis oraz zestawie LLaVA-Instruct-150k. Był to poprawny fundament, pozwalający na osiągnięcie około 35% na benchmarku MMMU.

Generacja modeli z 2024 roku (MM1, Idefics2, Molmo, Cambrian-1, Prismatic VLMs) przyniosła ze sobą szczegółowe badania ablacyjne. Ich wnioski okazały się zaskakujące i bardzo praktyczne.

## Koncepcja

### Pięcioosiowa przestrzeń projektowa

Autorzy Idefics2 (Laurençon et al., 2024) zdefiniowali następujące osie projektowe:

1. Encoder wizyjny: np. CLIP ViT-L/14, SigLIP SO400m/14, DINOv2 ViT-g/14, InternViT-6B. Różnią się one rozmiarem patcha, natywną rozdzielczością oraz celami pretreningu.
2. Adapter (złącze/connector): np. MLP (2-4 warstwy), Q-Former (32 zapytania + cross-attention), Perceiver Resampler (64 zapytania), C-Abstractor (warstwy splotowe + pooling dwuliniowy).
3. Model językowy (LLM): np. Llama-3 (8B/70B), Mistral 7B, Phi-3, Gemma-2, Qwen2.5. Rozmiar LLM to dominujący koszt pod kątem liczby parametrów.
4. Dane treningowe: proste pary obraz-opis (CC3M, LAION), dane przeplatane (OBELICS, MMC4), dane instruktażowe (LLaVA-Instruct, ShareGPT4V, PixMo, Cauldron).
5. Harmonogram rozdzielczości: stała rozdzielczość (224/336/448), AnyRes, natywna rozdzielczość dynamiczna. Może być modyfikowana w trakcie treningu lub stała.

Każdy model VLM wymaga decyzji na każdej z tych osi. Większość różnic w wynikach na benchmarku MMMU wynika z osi 1 (encoder), 4 (dane) oraz 5 (rozdzielczość), a nie z samego adaptera.

### Oś 1: Encoder jest ważniejszy niż adapter

W sekcji 3.2 publikacji MM1 wykazano, że zamiana encodera z CLIP ViT-L/14 na SigLIP SO400m/14 przyniosła wzrost o ponad 3 punkty procentowe na benchmarku MMMU. Tymczasem zamiana adaptera z MLP na Perceiver Resampler dała zysk poniżej 1 punktu. Podobne wnioski przyniosły testy Idefics2: SigLIP sprawdza się lepiej niż CLIP, natomiast wybór pomiędzy Q-Former, MLP i Perceiver (przy tej samej liczbie tokenów) daje zbliżone rezultaty.

W ramach projektu Cambrian-1 (Tong et al., 2024) przetestowano ponad 20 różnych encoderów w benchmarku CV-Bench (zorientowanym na ocenę samej wizji komputerowej). Najlepsze wyniki osiągnęło połączenie DINOv2 oraz SigLIP; CLIP uplasował się w środku stawki, natomiast ImageBind i ViT-MAE osiągnęły najniższe notowania. Różnica w wynikach CV-Bench pomiędzy CLIP ViT-L a DINOv2 ViT-g/14 wyniosła aż ~5-7 punktów.

Standardowym wyborem dla modeli open-weight stał się SigLIP 2 SO400m/14 (do ogólnych cech semantycznych), czasami łączony z DINOv2 ViT-g/14 (dla cech przestrzennych, co realizuje agregator przestrzenny w Cambrian-1).

### Oś 2: Projekt adaptera ma drugorzędne znaczenie

Prace MM1, Idefics2, Prismatic oraz MM-Interleaved doszły do identycznego wniosku: przy zachowaniu tej samej liczby wyjściowych tokenów wizualnych, wewnętrzna architektura adaptera nie wpływa znacząco na jakość. Prosty dwuwarstwowy MLP z poolingiem daje wyniki w granicach 1 punktu procentowego różnicy w porównaniu do złożonego Q-Formera z 32 zapytaniami.

Kluczowa jest sama liczba tokenów. Większa liczba tokenów wizualnych przekłada się na większe obciążenie obliczeniowe LLM i lepsze wyniki — aż do osiągnięcia punktu nasycenia. Budżet 64 tokenów na obraz to za mało dla zadań OCR. Zakres 576-1024 tokenów stanowi optymalny kompromis dla większości modeli VLM, a wartości powyżej 2048 pomagają głównie w analizie gęstych dokumentów i wykresów.

Wybór między Q-Former a MLP sprowadza się do kosztów okna kontekstowego: Q-Former ogranicza liczbę tokenów do stałej wartości (np. 32-64) niezależnie od rozdzielczości wejściowej, podczas gdy MLP przekazuje wszystkie wygenerowane patche. Przy obrazach o wysokiej rozdzielczości Q-Former chroni kontekst LLM; przy niskich rozdzielczościach różnica ta staje się pomijalna.

### Oś 3: Rozmiar LLM wyznacza możliwości modelu

Zwiększenie rozmiaru LLM z 7B do 13B parametrów przekłada się na stabilny wzrost o 2-4 punkty procentowe na benchmarku MMMU w każdej analizowanej publikacji. Modele o rozmiarze 70B osiągają punkt nasycenia w większości testów. Górna granica możliwości logicznego wnioskowania modelu VLM jest bezpośrednio wyznaczana przez możliwości tekstowe bazowego LLM — encoder wizyjny dostarcza jedynie informacje, lecz to LLM odpowiada za ich analizę.

To właśnie dlatego modele takie jak Qwen2.5-VL-72B czy Claude 3.5 Sonnet osiągają znakomite wyniki na MMMU-Pro i ScreenSpot-Pro: ich tekstowy moduł językowy jest po prostu ogromny. Model o rozmiarze 7B nie jest w stanie pokonać modelu 70B wyłącznie dzięki sprytniejszej architekturze adaptera.

### Oś 4: Dane — szczegółowe opisy ludzkie przewyższają dane syntetyczne

Publikacja o modelach Molmo + PixMo (Deitke et al., 2024) to jedna z najważniejszych lektur w tym obszarze. Zespół Allen AI zaangażował ludzi do szczegółowego opisywania obrazów za pomocą transkrypcji mowy na tekst (nagrania o długości 1-3 minut na obraz), co pozwoliło na stworzenie zbioru 712 tys. obrazów z bardzo bogatymi opisami. W procesie tym nie użyto danych syntetycznych z GPT-4V.

W rezultacie model Molmo-72B pokonał model Llama-3.2-90B-Vision w 11 na 11 testowanych benchmarków. Różnica ta nie wynikała z architektury, lecz z jakości opisów. Szczegółowe opisy stworzone przez ludzi zawierają 5–10 razy więcej informacji na obraz niż krótkie opisy pobrane z internetu, a dodatkowo są wolne od halucynacji typowych dla modeli generatywnych typu GPT-4V.

Podobną strategię (łączenie danych od ludzi i GPT-4V) zastosowano przy ShareGPT4V (Chen et al., 2023) oraz Cauldron (Idefics2). Wniosek jest jasny: kluczowa jest gęstość informacyjna opisów, a nie ich czysta liczba.

### Oś 5: Rozdzielczość i jej harmonogram (Resolution Scheduling)

Badania ablacyjne Idefics2 wykazują: zwiększenie rozdzielczości z 384 do 448 pikseli daje zysk 1-2 punktów. Zastosowanie techniki AnyRes (podział do rozdzielczości 980) daje kolejne 3-5 punktów w zadaniach OCR. Trening przy stałej rozdzielczości szybko osiąga plateau; z kolei stopniowe zwiększanie rozdzielczości w trakcie treningu (np. start od 224, koniec na 448 lub natywnej rozdzielczości dynamicznej) pozwala na szybszą zbieżność i lepsze wyniki końcowe.

W Cambrian-1 zbadano kompromis między rozdzielczością a liczbą tokenów: przy stałym budżecie obliczeniowym można wybrać większą liczbę tokenów w niższej rozdzielczości lub mniejszą liczbę tokenów w wyższej rozdzielczości. Wyższa rozdzielczość sprawdza się lepiej w zadaniach OCR, natomiast konfiguracja z większą liczbą tokenów i niższą rozdzielczością wygrywa w ogólnym rozumieniu sceny.

Optymalna recepta: trenuj Etap 1 w stałej rozdzielczości 384, a Etap 2 z dynamiczną rozdzielczością do 1280 dla zadań wymagających analizy tekstu.

### Wyniki kontrolowanego porównania w Prismatic VLMs

Prismatic VLMs (Karamcheti et al., 2024) to praca, w której kontrolowano wszystkie osie jednocześnie (ten sam LLM 13B, te same dane, ta sama procedura ewaluacyjna, zmieniana tylko jedna oś na raz). Wyniki:

- Liczba tokenów wizualnych przypadających na obraz wyjaśnia ~60% wariancji wyników.
- Dobór encodera wizyjnego wyjaśnia ~20% wariancji.
- Architektura adaptera (złącza) odpowiada za zaledwie ~5%.
- Pozostałe czynniki (miks danych, LR, harmonogram) to ~15%.

To zestawienie to najlepsza wskazówka dla inżynierów szukających odpowiedzi na pytanie: „który parametr optymalizować w pierwszej kolejności”.

### Rekomendacja wdrożeniowa

Na podstawie zgromadzonych dowodów, optymalna konfiguracja dla nowego projektu VLM obejmuje:

- Encoder: SigLIP 2 SO400m/14 w rozdzielczości natywnej z NaFlex, połączony z DINOv2 ViT-g/14 (jeśli zadanie wymaga precyzyjnego lokalizowania obiektów lub segmentacji).
- Adapter: 2-warstwowy MLP na tokenach patchy. Pomiń Q-Former, chyba że ogranicza Cię rozmiar okna kontekstowego LLM.
- LLM: Qwen2.5 / Llama-3.1 / Gemma 2 (rozmiar 7B/9B dla niskich kosztów i opóźnień, 70B dla maksymalnej jakości).
- Dane: Miks PixMo + ShareGPT4V + Cauldron, uzupełniony o specyficzne dane instruktażowe dla docelowego zadania.
- Rozdzielczość: dynamiczna (od 256 do 1280 pikseli na dłuższym boku).
- Harmonogram treningu: Etap 1 (trening samego projektora), Etap 2 (trening całego modelu), opcjonalny Etap 3 (dostrajanie pod specyficzne zadanie).

Każda z tych decyzji opiera się na twardych danych z badań ablacyjnych opisanych w literaturze naukowej.

## Użycie praktyczne

Skrypt `code/main.py` zawiera parser tabel ablacyjnych oraz selektor receptur. Koduje on skrócone wyniki z prac MM1 oraz Idefics2 i pozwala na zadawanie pytań typu:

- „Jaka konfiguracja będzie optymalna przy zadanym budżecie X i typie zadania Y?”
- „Jaka będzie różnica w wynikach MMMU, jeśli zamienię encoder SigLIP na CLIP przy modelu Llama 7B?”
- „Którą oś projektową powinienem zoptymalizować najpierw, aby uzyskać najwyższe prawdopodobieństwo poprawy wyników?”

Skrypt generuje ranking konfiguracji wraz z przewidywanym wpływem na benchmarki i rekomendacją kolejności modyfikacji parametrów.

## Zadanie zaliczeniowe

W ramach tej lekcji należy stworzyć dokument `outputs/skill-vlm-recipe-picker_pro.md`. Na podstawie zadanego profilu zadań, budżetu treningowego oraz wymagań dotyczących opóźnień (latency), zaproponuj kompletną konfigurację modelu VLM (encoder, adapter, LLM, miks danych, harmonogram rozdzielczości) wraz z powołaniem się na odpowiednie badania ablacyjne uzasadniające każdą decyzję. Zapobiega to konieczności ponownego analizowania tych samych tabel przez zespoły inżynierskie przy każdym nowym projekcie.

## Ćwiczenia

1. Przeczytaj sekcję 3.2 w artykule o MM1. Który encoder sprawdza się lepiej przy zamrożonym LLM 2B i budżecie 50 milionów obrazów? Czy odpowiedź zmieni się w przypadku LLM 13B? Uzasadnij dlaczego.

2. Autorzy Cambrian-1 wskazują, że połączenie DINOv2 + SigLIP daje lepsze wyniki w benchmarkach wizyjnych (CV-Bench), ale nie przekłada się na wzrost wyników w MMMU. Spróbuj przewidzieć, które typy zadań odnotują wzrost dokładności, a które pozostaną bez zmian.

3. Zaproponuj konfigurację encodera, adaptera, rozdzielczości i miksu danych dla agenta mobilnego UI opartego na modelu LLM 2B. Uzasadnij każdy wybór, powołując się na konkretne badania ablacyjne.

4. Model Molmo jest dostępny w wersjach 4B oraz 72B. Wersja 4B rywalizuje z komercyjnymi modelami 7B, a wersja 72B pokonuje model Llama-3.2-90B-Vision w 11 na 11 benchmarków. Jakie wnioski można z tego wyciągnąć w kontekście hipotezy o nasyceniu możliwości modeli LLM (scaling limits)?

5. Zaprojektuj plan badań ablacyjnych mających na celu oddzielenie wpływu jakości miksu danych od wpływu jakości encodera dla modelu VLM 7B. Jaka jest minimalna liczba procesów treningowych niezbędna do wyciągnięcia wniosków? Zaproponuj parametry dla czterech osi projektowych.

## Słownik pojęć

| Termin | Potoczne określenie | Co to dokładnie oznacza |
|------|-----------------|--------------------------------------|
| Ablacja (Ablation study) | „Izolowanie parametru” | Proces trenowania modeli różniących się dokładnie jednym parametrem w celu zmierzenia jego rzeczywistego wpływu na wynik końcowy. |
| Adapter (Connector) | „Mostek” / „projektor” | Trenowalny moduł pośredniczący, który mapuje reprezentacje z encodera wizyjnego do przestrzeni embeddingów LLM. |
| Szczegółowy opis ludzki | „Gęsty opis” | Wielozdaniowy opis obrazu stworzony przez człowieka (zazwyczaj 80-300 tokenów), znacznie bogatszy niż standardowe teksty alternatywne (alt-text) z sieci. |
| Destylacja (Distillation) | „Syntetyczne opisy z GPT-4V” | Generowanie danych treningowych za pomocą silniejszego, zamkniętego modelu VLM; tanie w pozyskaniu, ale niesie ryzyko przenoszenia halucynacji. |
| AnyRes / rozdzielczość dynamiczna | „Wielokrotne kafelkowanie” | Strategia przetwarzania obrazów o rozdzielczości wyższej niż natywna rozdzielczość encodera za pomocą kafelkowania (tiling) lub mechanizmu M-RoPE. |
| Stopniowanie rozdzielczości | „Resolution warmup” | Metoda treningowa polegająca na rozpoczynaniu uczenia w niskiej rozdzielczości i jej stopniowym zwiększaniu w celu przyspieszenia zbieżności. |
| Benchmark wizyjny | „Vision-centric benchmark” | Test oceniający precyzję samej percepcji wizualnej (np. CV-Bench, BLINK) w przeciwieństwie do zadań wymagających zaawansowanej wiedzy językowej. |
| PixMo | „Dane z Molmo” | Stworzony przez Allen AI zbiór 712 tys. obrazów z bardzo szczegółowymi, gęstymi opisami pochodzącymi z transkrypcji mowy ludzkiej. |

## Dalsze czytanie

- [McKinzie et al. — MM1 (arXiv:2403.09611)](https://arxiv.org/abs/2403.09611)
- [Laurençon et al. — Idefics2 / What matters when building VLMs (arXiv:2405.02246)](https://arxiv.org/abs/2405.02246)
- [Deitke et al. — Molmo and PixMo (arXiv:2409.17146)](https://arxiv.org/abs/2409.17146)
- [Tong et al. — Cambrian-1 (arXiv:2406.16860)](https://arxiv.org/abs/2406.16860)
- [Karamcheti et al. — Prismatic VLMs (arXiv:2402.07865)](https://arxiv.org/abs/2402.07865)
