# Przepisy VLM na otwartej wadze: co właściwie ma znaczenie

> Literatura VLM z lat 2024–2026 to las tabel ablacyjnych. Urządzenie Apple MM1 przetestowało 13 kombinacji kodera obrazu, złącza i miksu danych. Molmo z Allen AI udowodnił, że szczegółowe ludzkie podpisy są lepsze od destylacji GPT-4V. Cambrian-1 przeprowadził ponad 20 porównań koderów. Idefiks2 sformalizował pięcioosiową przestrzeń projektową. Pryzmatyczne VLM porównały 27 receptur szkoleniowych w kontrolowanym benchmarku. Spośród całego tego szumu niewielki zestaw wyników można znaleźć w różnych dokumentach: koder obrazu ma większe znaczenie niż architektura złącza, mieszanina danych ma większe znaczenie niż jedno i drugie, a szczegółowe podpisy ludzkie przewyższają destylowane dane syntetyczne. Podczas tej lekcji czytane są te tabele, więc Ty nie musisz tego robić.

**Typ:** Nauka + laboratorium
**Języki:** Python (stdlib, parser tabeli ablacji + selektor receptur)
**Wymagania wstępne:** Faza 12 · 05 (linia bazowa LLaVA)
**Czas:** ~180 minut

## Cele nauczania

- Nazwij pięcioosiową przestrzeń projektową VLM: koder obrazu, złącze, LLM, miks danych, harmonogram rozdzielczości.
- Przeczytaj tabelę ablacji MM1 / Idefics2 / Cambrian-1 i przewiduj, które pokrętło przesuwa dany punkt odniesienia.
- Wybierz przepis (koder, złącze, dane, rozdzielczość) dla nowego VLM, biorąc pod uwagę budżet obliczeniowy i zestaw zadań.
- Wyjaśnij, dlaczego szczegółowe podpisy ludzkie przewyższają destylację GPT-4V przy tej samej liczbie żetonów.

## Problem

Istnieją setki otwartych VLM. Większość przepaści pomiędzy „dobrym” a „najnowocześniejszym” nie leży w architekturze. To dane, harmonogram rozdzielczości i wybór kodera. Wiedząc, które pokrętło obrócić jako pierwsze, gdy Twój model osiąga słabą wydajność, możesz zaoszczędzić 5 milionów godzin pracy procesora.

Fala z 2023 r. (LLaVA-1.5, InstructBLIP, MiniGPT-4) obejmowała wstępne szkolenie w parach napisów + LLaVA-Instruct-150k. Dobra baza. Osiągnięty poziom około MMMU 35%.

Fala z 2024 r. (MM1, Idefics2, Molmo, Cambrian-1, Prismatic VLM) przeprowadziła wyczerpujące ablacje. Wyniki były zaskakujące i praktyczne.

## Koncepcja

### Pięcioosiowa przestrzeń projektowa

Idefics2 (Laurençon i in., 2024) nazwał osie:

1. Koder obrazu. CLIP ViT-L/14, SigLIP SO400m/14, DINOv2 ViT-g/14, InternViT-6B. Kodery różnią się rozmiarem poprawki, rozdzielczością i celem wstępnego uczenia.
2. Złącze. MLP (2-4 warstwy), Q-Former (32 zapytania + cross-attn), Perceiver Resampler (64 zapytania), C-Abstractor (pulowanie splotowe + dwuliniowe).
3. Model języka. Lama-3 8B/70B, Mistral 7B, Phi-3, Gemma-2, Qwen2.5. Rozmiar LLM jest dominującym kosztem parametru.
4. Dane treningowe. Pary napisów (CC3M, LAION), przeplatane (OBELICS, MMC4), instrukcje (LLaVA-Instruct, ShareGPT4V, PixMo, Cauldron).
5. Harmonogram rozstrzygnięć. Naprawiono 224/336/448, AnyRes, natywna dynamika. Narastające podczas treningu lub stałe.

Każdy produkcyjny VLM dokonuje wyboru na każdej osi. Większość rozbieżności w wynikach MMMU jest wyjaśniona przez osie 1, 4 i 5, a nie przez wybrane złącze.

### Oś 1: enkoder > złącze

MM1 Sekcja 3.2 pokazała: zamiana z CLIP ViT-L/14 na SigLIP SO400m/14 dodała 3+ punkty MMMU. Zamiana złącza z MLP na Perceiver Resampler dodała mniej niż 1 punkt. Replikacja Idefics2: SigLIP > CLIP, Q-Former ≈ MLP ≈ Perceiver przy tej samej liczbie tokenów.

W ramach projektu „Cambrian Vision Encoders Match-Up” firmy Cambrian-1 (Tong i in., 2024) przetestowano ponad 20 koderów w teście porównawczym zorientowanym na wizję (CV-Bench). Na szczycie tabeli liderów znajduje się połączenie DINOv2 i SigLIP; CLIP jest w środku stawki; ImageBind i ViT-MAE są niższe. Różnica między CLIP ViT-L a DINOv2 ViT-g/14 wynosi ~5-7 punktów w CV-Bench.

Domyślnym koderem 2026 dla otwartych VLM jest SigLIP 2 SO400m/14 dla funkcji semantycznych i gęstych, czasami połączonych z funkcjami DINOv2 ViT-g/14 (robi to „Spatial Vision Aggregator” firmy Cambrian).

### Oś 2: projekt złącza to bzdura

MM1, Idefics2, Prismatic i MM-Interleaved doszły do tego samego wniosku: przy stałej liczbie tokenów wizualnych architektura złącza nie ma większego znaczenia. Dwuwarstwowy system MLP na poprawkach ze średnią pulą działa w granicach 1 punktu w stosunku do Q-Formera z 32 zapytaniami przy tym samym budżecie tokenów.

Liczy się liczba tokenów. Więcej tokenów wizualnych = więcej obliczeń LLM = lepsza wydajność do pewnego momentu, a następnie malejące zyski. 64 tokeny na obraz to za mało dla OCR. Tokeny 576-1024 to najlepszy wybór dla większości otwartych VLM. 2048+ pomaga tylko w przypadku dokumentów i wykresów.

Q-Former vs MLP to kwestia kosztów, a nie jakości: Q-Former ogranicza tokeny do 32-64 niezależnie od rozdzielczości obrazu; MLP emituje wszystkie tokeny łatek. W przypadku wejść o wysokiej rozdzielczości Q-Former zapisuje kontekst LLM; w przypadku niskiej rozdzielczości różnicą jest hałas.

### Oś 3: Rozmiar LLM wyznacza pułap

Podwojenie LLM z 7B do 13B niezawodnie dodaje 2-4 punkty na MMMU w każdym artykule VLM. Przy 70B nasycasz większość benchmarków. Sufit rozumowania multimodalnego VLM jest pułapem rozumowania tekstowego LLM — koder wizualny może go jedynie zasilać, a nie uzasadniać.

Właśnie dlatego Qwen2.5-VL-72B i Claude Opus 4.7 miażdżą MMMU-Pro i ScreenSpot-Pro: mózg językowy jest ogromny. VLM 7B nie może zastąpić VLM 70B dzięki sprytnej konstrukcji złącza.

### Oś 4: dane — szczegółowe podpisy ludzkie przewyższają destylację

Molmo + PixMo (Deitke i in., 2024) to wynik za rok 2024, który każdy powinien przeczytać. Allen AI zlecił ludzkim adnotatorom opisywanie obrazów w ciągu 1–3 minut gęstych przejść z mowy na tekst, co dało 712 tys. obrazów z gęstymi podpisami. Brak destylacji GPT-4V w dowolnym miejscu danych szkoleniowych.

Molmo-72B pokonał Llamę-3.2-90B-Vision w 11 z 11 testów porównawczych. Delta to nie architektura — to jakość napisów. Szczegółowe podpisy ludzkie zawierają 5–10 razy więcej informacji na obraz niż krótkie podpisy internetowe i pozostają oparte na faktach tam, gdzie destylacja GPT-4V wywołuje halucynacje.

ShareGPT4V (Chen i in., 2023) i Cauldron (Idefics2) korzystały z tego samego podręcznika z mieszanymi podpisami ludzkimi i GPT-4V. Tendencja jest jasna: dla granicy 2026 gęstość napisów > ilość napisów > wygoda destylacji.

### Oś 5: uchwała i jej harmonogram

Ablacje Idefics2: 384 -> 448 dodaje 1-2 punkty. 448 -> 980 z podziałem obrazu (AnyRes) dodaje kolejne 3-5 w testach OCR. Plateau szkoleniowe o płaskiej rozdzielczości przy średniej dokładności; rampowanie rozdzielczości (początek 224, koniec 448 lub natywny) trenuje szybciej i kończy się wyżej.

Cambrian-1 przeprowadził kompromis w zakresie rozdzielczości i tokenów: przy stałych obliczeniach możesz mieć więcej tokenów w niższej rozdzielczości lub mniej tokenów w wyższej rozdzielczości. Wyższa rozdzielczość wygrywa w OCR; niższa rozdzielczość-więcej-tokenów wygrywa w ogólnym zrozumieniu sceny.

Przepis na produkcję na rok 2026: trenuj Etap 1 przy stałej rozdzielczości 384, Etap 2 z dynamiczną rozdzielczością do 1280 dla zadań wymagających dużej liczby OCR.

### Porównanie kontrolowane pryzmatycznie

Prismatic VLM (Karamcheti i in., 2024) to papier, który kontroluje wszystkie osie. Ten sam 13B LLM, te same dane instrukcji, ta sama ocena – tylko jedna oś zmienia się w danym momencie. Wyniki:

- Liczba tokenów wizualnych na obraz wyjaśnia ~60% wariancji.
- Wybór enkodera wyjaśnia ~20%.
- Architektura złącza wyjaśnia ~5%.
- Wszystko inne (miks danych, harmonogram, LR) pozostałe ~15%.

Jest to przybliżony rozkład, ale jest najczystszą odpowiedzią na pytanie „co powinienem najpierw ablować” w literaturze.

### Selekcjoner na rok 2026

Biorąc pod uwagę dowody, domyślna recepta open-VLM na nowy projekt w 2026 r.:

- Koder: SigLIP 2 SO400m/14 w rozdzielczości natywnej z NaFlex, połączony z DINOv2 ViT-g/14 w celu uzyskania gęstych funkcji, jeśli potrzebujesz segmentacji/uziemienia.
- Złącze: 2-warstwowe MLP na żetonach łatek. Pomiń Q-Former, chyba że jesteś ograniczony tokenem.
- LLM: Qwen2.5 / Llama-3.1 / Gemma 2, 7B za koszt, 70B za jakość, wybierane według docelowego opóźnienia.
- Dane: PixMo + ShareGPT4V + Cauldron, uzupełnione danymi instrukcji specyficznych dla zadania.
- Rozdzielczość: dynamiczna (min. 256, maks. 1280 pikseli na dłuższy bok).
- Harmonogram: Dostrajanie na etapie 1 (tylko projektor), Pełne dostrajanie na etapie 2, Dostrajanie na etapie 3 pod kątem konkretnego zadania.

Każde z tych uchybień ma swój początek w zmierzonej ablacji opisanej w artykułach cytowanych na końcu tej lekcji.

## Użyj tego

`code/main.py` to parser tabeli ablacji i selektor receptur. Koduje tabele ablacji MM1 i Idefics2 (skondensowane) i umożliwia zapytanie:

- „Jaki przepis wygrywa, biorąc pod uwagę budżet X i zadanie Y?”
- „Jeśli zamienię SigLIP na CLIP na lamie 7B, jaka jest oczekiwana delta MMMU?”
- „Którą oś powinienem najpierw ablować, aby uzyskać odpowiedź z pewnością na poziomie 80%?”

Wynikiem jest rankingowa lista receptur z oczekiwanymi deltami wzorcowymi i zaleceniem „najpierw ablacja”.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-vlm-recipe-picker.md`. Biorąc pod uwagę docelowy zestaw zadań, budżet obliczeniowy i docelowe opóźnienie, emituje pełną recepturę (koder, łącznik, LLM, miks danych, harmonogram rozdzielczości) z cytatami do ablacji uzasadniającymi każdy wybór. Uniemożliwia inżynierom wymyślanie na nowo stołu ablacyjnego Idefics2 za każdym razem, gdy rozpoczyna się nowy projekt VLM.

## Ćwiczenia

1. Przeczytaj MM1 Sekcja 3.2. Który koder wygrywa w przypadku stałego 2 miliardów LLM przy budżecie 50 milionów obrazów? Czy odpowiedź zmieni się na 13B LLM? Dlaczego?

2. Cambrian-1 stwierdza, że ​​połączenie DINOv2 + SigLIP daje lepsze wyniki w pojedynkę w testach porównawczych zorientowanych na wizję, ale nie dodaje sygnału na MMMU. Przewiduj, które benchmarki zyskają, a które pozostaną bez zmian.

3. Twoim celem jest mobilny agent UI na 2B LLM. Wybierz koder, złącze, rozdzielczość i miks danych. Uzasadnij każdy wybór konkretną tabelą ablacji.

4. Molmo dostarcza modele 4B i 72B. 4B jest konkurencyjny w stosunku do zamkniętych VLM 7B; 72B pokonuje Llama-3.2-90B-Vision w testach porównawczych z 11/11. Co to mówi o hipotezie plateau wielkości LLM?

5. Zaprojektuj tabelę ablacji, aby odizolować jakość miksu danych od jakości kodera na 7B VLM. Ile przebiegów treningowych jest minimum? Zaproponuj ustawienia czterech osi.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| Ablacja | „Przekręcenie jednego pokrętła” | Trenowanie wielu przebiegów, które różnią się dokładnie jedną osią przestrzeni projektowej, utrzymując wszystko inne na stałym poziomie |
| Złącze | „Most” / „projektor” | Możliwość szkolenia modułu, który odwzorowuje dane wyjściowe kodera wizyjnego na przestrzeń tokenów LLM (MLP, Q-Former, Perceiver) |
| Szczegółowy podpis ludzki | „Gęsty podpis” | Wielozdaniowy opis napisany przez człowieka (zwykle 80-300 tokenów) bogatszy niż tekst alternatywny w Internecie |
| Destylacja | „Napisy GPT-4V” | Dane szkoleniowe generowane przez silniejszy, zastrzeżony VLM; wygodne, ale podatne na dziedziczne halucynacje |
| AnyRes / dynamiczna rozdzielczość | „Ścieżka w wysokiej rozdzielczości” | Strategia podawania obrazów większych niż natywna rozdzielczość kodera poprzez kafelkowanie lub M-RoPE |
| Rampa rozdzielczości | „Program nauczania” | Harmonogram treningów, który rozpoczyna się w niskiej rozdzielczości i zwiększa, przyspieszając naukę wyrównania |
| Ławka skupiająca się na wizji | „Ławka CV / BLINK” | Ocena, która kładzie nacisk na precyzyjną percepcję wzrokową, a nie na rozumowanie oparte na języku |
| PixMo | „Dane Molmo” | Zbiór danych obrazów Allen AI o objętości 712 KB z gęstymi podpisami; mowa ludzka przepisana na gęste napisy |

## Dalsze czytanie

- [McKinzie i in. — MM1 (arXiv:2403.09611)](https://arxiv.org/abs/2403.09611)
- [Laurençon i in. — Idefics2 / Co się liczy przy budowaniu VLM (arXiv:2405.02246)](https://arxiv.org/abs/2405.02246)
- [Deitke i in. — Molmo i PixMo (arXiv:2409.17146)](https://arxiv.org/abs/2409.17146)
- [Tong i in. — Kambr-1 (arXiv:2406.16860)](https://arxiv.org/abs/2406.16860)
- [Karamcheti i in. — Pryzmatyczne VLM (arXiv:2402.07865)](https://arxiv.org/abs/2402.07865)