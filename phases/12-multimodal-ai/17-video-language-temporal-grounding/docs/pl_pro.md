# Modele wideo-językowe: tokeny czasowe i temporal grounding

> Wideo to coś więcej niż tylko sekwencja zdjęć. Nawet w 5-sekundowym klipie zakodowana jest przyczynowość, dynamika ruchu oraz czas trwania zdarzeń, których statyczny model obrazu nie potrafi wychwycić. Model Video-LLaMA (Zhang i in., czerwiec 2023) zaproponował pierwszą otwartą wersję wideo-LLM z uziemieniem audiowizualnym (audiovisual grounding). Projekty VideoChat i Video-LLaVA rozwinęły ten schemat. Z kolei do 2025 roku mechanizm TMRoPE zastosowany w Qwen2.5-VL ostatecznie zniwelował dystans dzielący otwarte rozwiązania od wiodących modeli komercyjnych. Każdy z tych systemów w inny sposób przetwarzał tokeny czasowe: od modułów Q-former dla całego klipu, przez łączenie (pooling/concatenation) klatek, aż po mechanizm TMRoPE działający na poziomie pojedynczego tokenu. W tej lekcji przeanalizujemy te architektury, zaimplementujemy próbnik klatek (zarówno o stałej, jak i dynamicznej częstotliwości próbkowania) oraz ocenimy metody lokalizacji zdarzeń w czasie (temporal grounding).

**Typ:** Teoria / Analiza
**Języki:** Python (biblioteka standardowa, próbnik klatek + narzędzie do oceny temporal groundingu)
**Wymagania wstępne:** Faza 12 · 08 (LLaVA-OneVision)
**Czas:** ~180 minut

## Cele kształcenia

- Wyjaśnienie, dlaczego czasowe kodowanie pozycyjne (temporal positional encoding) kluczowo wpływa na wydajność wideo-VLM, niezależnie od samego enkodera wizyjnego.
- Porównanie wpływu próbkowania klatek (jednolitego, dynamicznego oraz sterowanego zdarzeniami) na dokładność lokalizacji zdarzeń.
- Opisanie różnych podejść architektonicznych: Q-former dla całego klipu (Video-LLaMA), pooling klatek (Video-LLaVA) oraz M-RoPE na poziomie tokenu (Qwen2.5-VL).
- Zestawienie czterech kluczowych benchmarków wideo: VideoMME, TempCompass, EgoSchema oraz Video-MMMU.

## Problem

Jednominutowe nagranie wideo przy 30 kl./s składa się z 1800 klatek. Zakładając 196 tokenów wizualnych na klatkę (dla ViT-B/16 na obrazach 224x224), daje to łącznie 352 000 tokenów – czyli znacznie powyżej okna kontekstowego większości modeli LLM z roku 2024.

Istnieją trzy główne strategie redukcji tej liczby:

1. **Podpróbkowanie klatek:** redukcja częstotliwości klatek (do 1–8 FPS w zależności od dynamiki nagrania).
2. **Agresywny pooling tokenów (patch tokens) z każdej klatki:** np. pooling bilinearne 3x3 lub 4x4.
3. **Kompresja za pomocą modułu typu Q-former:** przyjmuje np. 16-klatkowy klip i generuje z niego zaledwie 64 tokeny.

Każdy z tych kompromisów wiąże się z innymi stratami. Podpróbkowanie gubi szczegóły czasowe. Pooling degraduje rozdzielczość przestrzenną. Q-former powoduje częściową utratę obu tych aspektów, ale w zamian drastycznie oszczędza liczbę tokenów.

Kolejnym wyzwaniem jest kodowanie pozycyjne w czasie: skąd model ma wiedzieć, że klatka 5 nastąpiła przed klatką 6? Stosuje się tu m.in. jednowymiarowe czasowe kodowanie RoPE (Video-LLaMA), wyuczone czasowe osadzenia (embeddings) (Video-LLaVA) oraz zaawansowane TMRoPE (Qwen2.5-VL, pełne kodowanie trójwymiarowe).

## Koncepcja

### Video-LLaMA: Q-former dla klipu + ścieżka audio

Video-LLaMA (2023) to jeden z pierwszych otwartoźródłowych modeli wideo-LLM. Architektura obejmuje:

- Przetwarzanie 16-klatkowych klipów przy 2 FPS (co daje 8 sekund nagrania).
- Cechy ViT dla poszczególnych klatek → moduł Video Q-former agregujący kontekst z 16 klatek → 32 wyuczone zapytania (queries) → LLM.
- Równoległą ścieżkę audio: surowy sygnał → koder ImageBind → Audio Q-former → 32 zapytania → LLM.

Zalety: zintegrowane rozumowanie audiowizualne. Wady: sztywna długość klipu, brak możliwości precyzyjnej lokalizacji zdarzeń w czasie (temporal grounding).

### VideoChat i Video-LLaVA

Projekt VideoChat zachował ogólną ideę Video-LLaMA, rezygnując jednak z dźwięku na rzecz uproszczenia architektury. Video-LLaVA (Lin i in., 2023) poszła o krok dalej, trenując jeden koder wizyjny zarówno na obrazach statycznych, jak i klatkach wideo („wyrównanie przed projekcją” / alignment before projection), co dało spójną reprezentację danych. W obu przypadkach podstawę stanowi zamrożony enkoder CLIP + adapter MLP + LLM.

Żaden z nich nie obsługuje długich filmów. Oba systemy są ograniczone do przetwarzania 8–16 klatek.

### Qwen2.5-VL i TMRoPE

Model Qwen2.5-VL wprowadził TMRoPE (Time-informed Multimodal RoPE) – czasowe multimodalne kodowanie obrotowe. Każdy token klatki (patch token) otrzymuje trójwymiarowy wektor pozycji (t, h, w), gdzie `t` reprezentuje rzeczywisty znacznik czasu, a nie tylko indeks klatki.

Główne różnice w stosunku do prostego osadzania czasowego:

- **Czas rzeczywisty (bezwzględny) zamiast indeksów:** Model operuje na wartościach typu „w 4,2 sekundzie”, a nie „w klatce numer 15”.
- **Rotacja na poziomie tokenu, a nie klipu:** Każdy token wizyjny jest modyfikowany niezależnie na podstawie przypisanego mu znacznika czasu.
- **Pełna kompatybilność z dynamicznym FPS:** Jeśli w jednym fragmencie filmu próbkowanie wynosi 2 FPS, a w innym 4 FPS, TMRoPE natywnie obsługuje nieregularne odstępy czasowe.

Dzięki temu model może odpowiadać na precyzyjne pytania typu „W której sekundzie kot skacze przez przeszkodę?”, generując odpowiedź w postaci: `w 4,2 sekundy`. Wcześniejsze modele, jak Video-LLaMA, mogły jedynie wskazać: `na początku nagrania`.

### Strategie próbkowania klatek

- **Próbkowanie jednolite (Uniform):** Pobieranie N klatek w równych odstępach czasu. Proste w implementacji, ale pomiija momenty o wysokiej dynamice ruchu.
- **Dynamiczny FPS:** Adaptacyjne próbkowanie w zależności od intensywności ruchu. Analiza przepływu optycznego (optical flow) lub różnic między klatkami pozwala zidentyfikować dynamiczne sceny i próbkować je gęściej. Qwen2.5-VL korzysta z tej metody.
- **Próbkowanie sterowane zdarzeniami (Event-driven):** Uruchomienie lekkiego modelu detekcyjnego w tle i zwiększanie częstotliwości próbkowania w kluczowych momentach (stosowane np. w VideoAgent).
- **Próbkowanie klatek kluczowych i kontekstu:** Próbkowanie na granicach cięć montażowych oraz wokół nich. Rozwiązanie to sprawdza się w analizie filmów fabularnych.

### Pooling na poziomie klatki (Frame-level Pooling)

Przy częstotliwości 1 FPS i 576 tokenach na klatkę, 5-minutowy film generuje 172 800 tokenów. Taki wolumen danych mieści się w oknie kontekstowym Qwen2.5-VL-72B (128k), ale jest kosztowny obliczeniowo.

Zastosowanie bilinearnego poolingu 3x3 pozwala zredukować ten narzut do 64 tokenów na klatkę, co daje zaledwie 19 200 tokenów dla 5-minutowego nagrania. Jest to optymalny kompromis dla większości zadań.

W zadaniach agencyjnych, gdzie precyzja przestrzenna ma mniejsze znaczenie, można zastosować jeszcze bardziej agresywny pooling (np. 6x6 dający 16 tokenów na klatkę).

### Cztery benchmarki wideo

- **VideoMME:** Kompleksowa ocena rozumienia wideo z podziałem na materiały krótkie, średnie i długie.
- **TempCompass:** Testowanie szczegółowego wnioskowania czasowego za pomocą pytań typu „przed” / „po” itp.
- **EgoSchema:** Rozumienie wideo w długiej perspektywie czasowej (perspektywa pierwszoosobowa - ego-view).
- **Video-MMMU:** Trudne, wielodyscyplinarne pytania naukowe i techniczne oparte na wideo.

Kompleksowa ewaluacja modeli wideo-VLM wymaga zastosowania wszystkich czterech testów benchmarkowych. Każdy z nich kładzie nacisk na inne aspekty: TempCompass bada porządkowanie zdarzeń, EgoSchema wymaga rozumowania na dystansie ok. 3 minut, a VideoMME ocenia poprawność wnioskowania w zależności od długości wideo.

### Formaty wyjściowe uziemienia czasowego (groundingu)

- **Tekst nieustrukturyzowany:** „Kot wykonuje skok w okolicy 4 sekundy nagrania”. Metoda łatwa do sformułowania przez model, lecz mało precyzyjna do automatycznego przetwarzania.
- **Strukturyzowany format JSON:** `{"event": "jump", "start": 4.1, "end": 4.3}`. W ten sposób trenowany jest Qwen2.5-VL.
- **Format oparty na dedykowanych tokenach:** Specjalne tokeny typu `<time>4.1</time>` wplecione w treść wypowiedzi. Jest to natywny format wewnętrzny Qwen2.5-VL.

Metoda tokenowa zapewnia największą dokładność w systemach kaskadowych. Dane wyjściowe w formacie JSON z modelu Qwen2.5-VL mogą być od razu parsowane przez zewnętrzne aplikacje.

### Najlepsze praktyki w 2026 roku

W projektach opartych na wideo-VLM w 2026 roku rekomenduje się:
- **Enkoder wizyjny:** SigLIP 2 z wbudowanym M-RoPE lub TMRoPE (np. Qwen2.5-VL).
- **Próbkowanie klatek:** Dynamiczny FPS (1–4 FPS zależnie od dynamiki ruchu) z nałożeniem limitu na maksymalną liczbę klatek.
- **Pooling na klatkę:** Bilinearny pooling 3x3.
- **Format wyjściowy:** Strukturyzowany JSON zawierający informacje o czasie trwania i typie zdarzenia.
- **Testy porównawcze:** Zastosowanie VideoMME oraz TempCompass dla ogólnej weryfikacji, a EgoSchema dla długiego kontekstu.

## Zastosowanie w kodzie

Plik `code/main.py` zawiera:
- Przykładowe próbnik klatek dla stałego (Uniform) i dynamicznego FPS.
- Moduł ewaluacyjny do uziemienia czasowego (temporal grounding): oceniający dokładność detekcji zdarzeń przez model w odniesieniu do danych referencyjnych (ground truth) w ramach zdefiniowanego marginesu błędu.
- Porównanie architektur Video-LLaMA (16 klatek, Q-former), Video-LLaVA (8 klatek, MLP) oraz Qwen2.5-VL (dynamiczny FPS + TMRoPE).

## Rezultat

Do tej lekcji dołączono dokument `outputs/skill-video-vlm-frame-planner.md`. Pozwala on dobrać odpowiednią strategię próbkowania klatek, stopień poolingu, format wyjściowy oraz oszacować docelową dokładność modelu w zależności od specyfiki zadania wideo (monitoring, detekcja akcji, temporal grounding, streszczenia).

## Ćwiczenia

1. Dla 3-minutowego nagrania z instruktażem gotowania wybierz próbkowanie jednolite lub dynamiczne. Uzasadnij wybór, szacując ostateczną liczbę wygenerowanych tokenów.
2. Jakie konkretnie możliwości wnosi TMRoPE, których nie da się zrealizować za pomocą zwykłej tabeli czasowych kodowań pozycyjnych?
3. Zaprojektuj schemat JSON dla zadań temporal groundingu, który model VLM będzie generował na wyjściu. Uwzględnij scenariusze obsługi błędów i braku zdarzenia.
4. Przeczytaj sekcję 3 pracy o Video-LLaVA poświęconą etapowi „wyrównania przed projekcją”. Wyjaśnij, dlaczego takie podejście jest lepsze od oddzielnego trenowania enkoderów obrazu i wideo.
5. Jaka jest różnica w wynikach w benchmarku VideoMME (dla stanu na rok 2026) między wiodącym modelem otwartym a komercyjnym? Jak dużą część tej różnicy można przypisać kodowaniu czasowemu, a ile wynika z samej skali bazowego LLM?

## Kluczowe pojęcia

| Termin | Potoczne określenie | Co to dokładnie oznacza |
| :--- | :--- | :--- |
| **Uziemienie czasowe (Temporal grounding)** | „Odpowiedzi ze znacznikami czasu” | Zdolność modelu VLM do wskazywania konkretnego przedziału czasu (znaczników start-stop), w którym występuje dane zdarzenie. |
| **TMRoPE** | „Multimodalne RoPE czasowe” | Trójwymiarowe kodowanie obrotowe (3D Rotary Position Embedding) uwzględniające bezwzględny czas rzeczywisty, stosowane w Qwen2.5-VL. |
| **Dynamiczny FPS** | „Próbkowanie wrażliwe na ruch” | Strategia próbkowania klatek polegająca na zagęszczaniu próbek w dynamicznych scenach i rzadszym próbkowaniu statycznych fragmentów. |
| **Pooling klatek (Frame pooling)** | „Kompresja przestrzenna klatek” | Zmniejszanie liczby tokenów opisu przestrzennego (patch tokens) w pojedynczej klatce przy użyciu np. interpolacji bilinearnej przed przekazaniem do LLM. |
| **Video Q-former** | „Kompresor klipów” | Moduł mapujący reprezentację wizyjną wielu klatek (N) na mniejszą, stałą liczbę wyuczonych zapytań (K queries). |
| **VideoMME** | „Benchmark wideo” | Kompleksowy test porównawczy do oceny modeli wideo na nagraniach o różnej długości (ponad 2500 próbek testowych). |

## Literatura uzupełniająca

- [Zhang i in. — Video-LLaMA (arXiv:2306.02858)](https://arxiv.org/abs/2306.02858)
- [Li i in. — Video Chat (arXiv:2305.06355)](https://arxiv.org/abs/2305.06355)
- [Lin i in. — Video-LLaVA (arXiv:2311.10122)](https://arxiv.org/abs/2311.10122)
- [Zespół Qwen — Qwen2.5-VL (arXiv:2502.13923)](https://arxiv.org/abs/2502.13923)
- [Lin i in. — VILA-1.5 (arXiv:2312.07533)](https://arxiv.org/abs/2312.07533)
