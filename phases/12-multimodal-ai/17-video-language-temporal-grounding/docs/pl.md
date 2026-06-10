# Modele języka wideo: tokeny tymczasowe i uziemienie

> Wideo to nie stos zdjęć. W 5-sekundowym klipie występuje porządek przyczynowy, czasowniki akcji i czas zdarzeń, których model obrazu nie jest w stanie odzwierciedlić. Video-LLaMA (Zhang i in., czerwiec 2023 r.) dostarczyło pierwszą otwartą wersję wideo-LLM z uziemieniem audiowizualnym. VideoChat i Video-LLaVA skalowały ten wzorzec. Do 2025 roku TMRoPE firmy Qwen2.5-VL wypełni lukę w stosunku do pionierskich, zastrzeżonych modeli. Każdy system rozwiązywał tokeny tymczasowe w inny sposób — Q-former na klip, pula konkatów na klatkę, TMRoPE na token. Podczas tej lekcji odczytywane są wzorce, tworzy się próbnik klatek jednorodnych i dynamicznych i oceniane są zadania związane z uziemieniem czasowym.

**Typ:** Kompilacja
**Języki:** Python (stdlib, próbnik klatek + narzędzie do oceny uziemienia czasowego)
**Wymagania wstępne:** Faza 12 · 08 (LLaVA-OneVision)
**Czas:** ~180 minut

## Cele nauczania

- Wyjaśnij, dlaczego czasowe kodowanie pozycyjne zmienia wydajność VLM wideo niezależnie od kodera wizyjnego.
- Porównaj jednolite, dynamiczne próbkowanie klatek na sekundę i sterowane zdarzeniami próbkowanie klatek na sekundę w porównaniu z dokładnością uziemienia.
- Opisać projekty typu Q-former na klip (Video-LLaMA) w porównaniu z pulą na klatkę (Video-LLaVA) i M-RoPE na token (Qwen2.5-VL).
- Wymień cztery testy porównawcze wideo: VideoMME, TempCompass, EgoSchema, Video-MMMU.

## Problem

1-minutowy film przy 30 klatkach na sekundę to 1800 klatek. Przy 196 tokenach wizualnych na klatkę (ViT-B – 224), czyli 352 tys. tokenów – więcej niż w jakimkolwiek kontekście LLM z ery 2024.

Istnieją trzy strategie redukcji:

1. Podpróbkowe klatki (1-8 FPS w zależności od treści).
2. Agresywnie łącz żetony łat z każdej ramki (pula dwuliniowa 3x3 lub 4x4).
3. Kompresuj za pomocą Q-formera, który pobiera 16-klatkowy klip i generuje 64 tokeny.

Każdy kompromis jest inny. Podpróbkowanie traci szczegóły czasowe. Łączenie powoduje utratę szczegółów przestrzennych. Q-former traci trochę obu, ale oszczędza tokeny.

Kodowanie położenia czasowego to druga oś: skąd model wie, że klatka 5 pojawiła się przed klatką 6? Opcje obejmują prostą czasową RoPE 1D (Video-LLaMA), wyuczone osadzanie czasowe (Video-LLaVA) i TMRoPE (Qwen2.5-VL, pełne 3D).

## Koncepcja

### Video-LLaMA: Q-former na klip + gałąź audio

Video-LLaMA (2023) było pierwszym otwartym wideo-LLM. Architektura:

- Klipy 16-klatkowe przy 2 FPS (czyli 8 sekund).
- Funkcje ViT dla poszczególnych klatek -> Moduł wideo Q-former, który krzyżowo obsługuje wszystkie 16 klatek -> 32 wyuczone zapytania -> LLM.
- Równoległa gałąź audio: kształt fali -> Koder audio ImageBind -> Audio Q-former -> 32 zapytania -> LLM.

Siła: wspólne rozumowanie audiowizualne. Słabość: stała długość klipu, brak dowolnego uziemienia czasowego.

### Wideoczat i wideo-LLaVA

VideoChat zachował pomysł Video-LLaMA, ale porzucił dźwięk i uprościł go. Video-LLaVA (Lin i in., 2023) wyszkolił pojedynczy koder wizualny zarówno na obrazach, jak i klatkach wideo („wyrównanie przed projekcją”), zapewniając ujednoliconą reprezentację. Oba są zamrożonymi koderami CLIP + MLP + LLM.

Żaden z nich nie obsługuje długich filmów. Obydwa są systemami 8-16 ramowymi.

### Qwen2.5-VL i TMRoPE

Qwen2.5-VL wprowadził TMRoPE — osadzanie pozycji obrotowej w trybie czasowo-modalnym. Każdy żeton poprawki zawiera pozycję (t, h, w), gdzie t jest rzeczywistym znacznikiem czasu (nie indeksem ramki).

Kluczowe różnice w stosunku do prostego osadzania czasowego:

- Czas bezwzględny, a nie indeksowy. Model widzi „w 4,2 sekundy”, a nie „w klatce 15”.
- Rotacja według tokena, a nie dla klipu. Każdy token wizualny obraca się niezależnie według swojego znacznika czasu.
- Kompatybilny z dynamicznymi FPS. Jeśli próbkujesz z szybkością 2 FPS tutaj i 4 FPS tam, TMRoPE natywnie radzi sobie z nierównymi odstępami.

TMRoPE umożliwia „w której sekundzie kot skacze?” zapytania. Model może generować sygnał „w 4,2 sekundy”. Video-LLaMA mogła powiedzieć jedynie „na początku klipu”.

### Strategie próbkowania klatek

Jednolity: próbkuj N klatek równomiernie w czasie trwania. Proste, traci szczyty ruchu.

Dynamiczny FPS: próbkuj adaptacyjnie w oparciu o intensywność ruchu. Przepływ optyczny lub różnicowanie klatek wybiera segmenty o dużym ruchu w celu uzyskania gęstszego próbkowania. Trenuje na tym Qwen2.5-VL.

Oparta na zdarzeniach: uruchom lekki detektor i próbkuj więcej tam, gdzie dzieje się akcja. Używany przez VideoAgent.

Klatka kluczowa + kontekst: próbka na granicach ujęcia + kilka sąsiadujących klatek. Używany w treściach filmowych.

### Łączenie na klatkę

Przy 1 kl./s i 576 tokenach na klatkę 5-minutowy klip to 172 800 tokenów. Wykonalne w kontekście 128k Qwen2.5-VL-72B, ale drogie.

Pula dwuliniowa 3x3 zmniejsza się do 64 tokenów na klatkę -> 19 200 tokenów przez 5 minut. Idealne miejsce do większości zadań.

Bardziej agresywne łączenie (6x6 -> 16 tokenów na klatkę) w przypadku przepływów pracy agentów, w których szczegóły przestrzenne mają mniejsze znaczenie.

### Cztery testy porównawcze wideo

- VideoMME: kompleksowe zrozumienie wideo, krótkie + średnie + długie.
- TempCompass: szczegółowe rozumowanie temporalne, pytania „przed” / „po”.
- EgoSchema: wideo z perspektywy pierwszej osoby w długim horyzoncie.
- Video-MMMU: multimodalne, wielodyscyplinarne pytania wideo.

Pełna ocena wideo-VLM uwzględnia wszystkie cztery. Kładą nacisk na różne osie — TempCompass skupia się na porządkowaniu, EgoSchema to około 3-minutowe rozumowanie, VideoMME obejmuje czas trwania.

### Uziemiające formaty wyjściowe

Formaty wyjściowe dla uziemienia tymczasowego:

- Dowolny tekst: „Kot przeskakuje około 4 sekundy”. Łatwe do analizy, ale nieprecyzyjne.
- Strukturalny JSON: `{"event": "jump", "start": 4.1, "end": 4.3}`. Trenuje to Qwen2.5-VL.
- Oparte na tokenach: specjalne `<time>4.1</time>` tokeny przeplatane odpowiedzią. Wewnętrzny format Qwen2.5-VL.

Metoda oparta na tokenach jest najdokładniejsza w przypadku dalszego wykorzystania. Format wyjściowy JSON Qwen2.5-VL analizuje bezpośrednio.

### Najlepsze praktyki z 2026 r

W przypadku wideo VLM w 2026 r.:

- Enkoder: SigLIP 2 z M-RoPE lub TMRoPE (Qwen2.5-VL).
- Próbkowanie klatek: dynamiczny FPS (1-4 w zależności od ruchu) z ograniczeniem maksymalnej liczby klatek.
- Łączenie na klatkę: dwuliniowe 3x3.
- Dane wyjściowe: strukturalny JSON z polami czasu i zdarzeń.
- Testy porównawcze: VideoMME + TempCompass dla ogółu; EgoSchema na długi horyzont.

## Użyj tego

`code/main.py` obejmuje:

- Jednolite i dynamiczne próbniki klatek FPS.
- Zabawkowy oceniacz uziemienia czasowego: biorąc pod uwagę zdarzenie „prawdy podstawowej” w czasie T i sygnał wyjściowy modelu, oceń dokładność z tolerancją.
- Porównanie Video-LLaMA (16 klatek, Q-former), Video-LLaVA (8 klatek, MLP), Qwen2.5-VL (dynamiczny FPS + TMRoPE).

## Wyślij to

Ta lekcja przedstawia `outputs/skill-video-vlm-frame-planner.md`. Biorąc pod uwagę zadanie wideo (monitorowanie, rozpoznawanie akcji, uziemienie czasowe, podsumowanie), wybiera próbnik klatek, współczynnik łączenia, format wyjściowy i oczekiwany poziom dokładności.

## Ćwiczenia

1. Aby obejrzeć 3-minutową demonstrację gotowania, wybierz jednolity lub dynamiczny FPS. Uzasadnij liczbą żetonów.

2. TMRoPE dodaje, czego konkretnie nie może zrobić prosta tabela osadzania tymczasowego?

3. Napisz schemat JSON dla tymczasowego uziemienia, którego VLM może nauczyć się emitować. Uwzględnij przypadki błędów.

4. Przeczytaj sekcję 3 Video-LLaVA dotyczącą „Wyrównanie przed projekcją”. Dlaczego jest to lepsze niż szkolenie oddzielnych koderów obrazu i wideo?

5. Jaka jest różnica pomiędzy czołowym modelem otwartym a czołowym modelem zastrzeżonym, biorąc pod uwagę ranking VideoMME na rok 2026? Jak dużą część tej luki można przypisać kodowaniu czasowemu w porównaniu z podstawową skalą LLM?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| Uziemienie tymczasowe | „Odpowiedzi zlokalizowane w czasie” | VLM generuje określony zakres znaczników czasu dla chwili wystąpienia zdarzenia |
| TMRoPE | „Lina multimodalna czasowa” | Pozycja obrotowa 3D z bezwzględnymi znacznikami czasu, używana przez Qwen2.5-VL |
| Dynamiczny FPS | „Próbkowanie świadome ruchu” | Próbuj więcej klatek w segmentach o dużym ruchu, mniej w segmentach statycznych |
| Łączenie ramek | „Kompresja przestrzenna na klatkę” | Zmniejsz liczbę poprawek na klatkę dzięki interpolacji dwuliniowej przed LLM |
| Wideo Q-były | „Kompresor klipów” | Mapowanie wąskiego gardła między uwagami N ramek na K wyuczonych zapytań |
| WideoMME | „Ławka wideo” | Kompleksowy test porównawczy krótkich, średnich i długich filmów, ponad 2500 próbek |

## Dalsze czytanie

- [Zhang i in. — Wideo-LLaMA (arXiv:2306.02858)](https://arxiv.org/abs/2306.02858)
- [Li i in. — Czat wideo (arXiv:2305.06355)](https://arxiv.org/abs/2305.06355)
- [Lin i in. — Wideo-LLaVA (arXiv:2311.10122)](https://arxiv.org/abs/2311.10122)
- [Zespół Qwen — Qwen2.5-VL (arXiv:2502.13923)](https://arxiv.org/abs/2502.13923)
- [Lin i in. — VILA-1.5 (arXiv:2312.07533)](https://arxiv.org/abs/2312.07533)