# Generowanie wideo

> Obraz to tensor 2D. Film to obiekt 3D. Teoria jest ta sama, lecz obliczenia są od 10 do 100 razy kosztowniejsze. Sora firmy OpenAI (luty 2024) dowiodła, że jest to wykonalne. Do 2026 roku Veo 2, Kling 1.5, Runway Gen-3, Pika 2.0 i WAN 2.2 dostarczają wideo generowane z tekstu w rozdzielczości 1080p, a stos modeli o otwartych wagach (CogVideoX, HunyuanVideo, Mochi-1, WAN 2.2) pozostaje w tyle o około 12 miesięcy.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 8 · 07 (dyfuzja utajona), Faza 7 · 09 (ViT), Faza 8 · 06 (DDPM)
**Czas:** ~45 minut

## Problem

10-sekundowy film 1080p przy 24 klatkach na sekundę to 240 klatek o rozdzielczości 1920 × 1080 × 3 piksele — czyli około 1,5 GB surowych danych na klip. Dyfuzja w przestrzeni pikseli jest w praktyce niemożliwa. Potrzebne są cztery elementy:

1. **Kompresja czasoprzestrzenna.** VAE kodujący filmy — nie pojedyncze klatki — w sekwencję bloków przestrzenno-czasowych.
2. **Spójność czasowa.** Klatki muszą zachowywać wspólną treść, oświetlenie i tożsamość obiektów przez całe sekundy. Siatka musi modelować ruch.
3. **Budżet obliczeniowy.** Trenowanie na danych wideo jest od 10 do 100 razy droższe niż na obrazach przy tym samym rozmiarze modelu.
4. **Kondycjonowanie.** Tekst, obraz (pierwsza klatka), dźwięk lub inny film. Większość modeli produkcyjnych akceptuje wszystkie cztery typy.

Architekturą, która rozwiązuje ten problem, jest **Transformator Dyfuzyjny (DiT)** stosowany do bloków czasoprzestrzennych, trenowany na ogromnych zbiorach danych (podpowiedzi, napisy, wideo). Funkcja straty pozostaje taka sama jak w lekcji 06.

## Koncepcja

![Rozpowszechnianie wideo: patchify, DiT, decode](../assets/video-generation.svg)

### Patchowanie

Wideo jest kodowane za pomocą 3D VAE (wyuczona kompresja czasoprzestrzenna). Reprezentacja utajona ma kształt `[T_latent, H_latent, W_latent, C_latent]` i jest dzielona na bloki o rozmiarze `[t_p, h_p, w_p]`. W modelach wzorowanych na Sorze `t_p = 1` (jeden blok na klatkę) lub `t_p = 2` (co dwie klatki). 10-sekundowy film 1080p kompresuje się do około 20 000–100 000 bloków.

### Czasoprzestrzenny DiT

Transformator przetwarza spłaszczoną sekwencję bloków. Każdy blok posiada trójwymiarowe osadzenie pozycyjne (czas + y + x). Mechanizm uwagi jest zwykle faktoryzowany:

- **Uwaga przestrzenna** — w obrębie każdej klatki.
- **Uwaga czasowa** — między klatkami w tym samym miejscu przestrzennym.
- **Pełna uwaga 3D** jest od 16 do 100 razy kosztowniejsza; stosowana wyłącznie przy niskiej rozdzielczości lub w badaniach.

### Kondycjonowanie tekstem

Uwaga krzyżowa z dużym enkoderem tekstu (T5-XXL dla Sory, CogVideoX-5B również korzysta z T5-XXL). Rozbudowane podpowiedzi mają istotne znaczenie — zbiór treningowy Sory zawierał gęste opisy generowane przez GPT, średnio 200 tokenów na klip.

### Trenowanie

Standardowa strata dyfuzyjna (przewidywanie ε lub v) na utajonych reprezentacjach czasoprzestrzennych. Dane: wideo z internetu oraz około 100 milionów wyselekcjonowanych klipów z syntetycznymi napisami. Obliczenia: ponad 10 000 godzin GPU nawet przy krótkim projekcie badawczym; Sora przekracza 100 000.

## Krajobraz produkcyjny w 2026 r.

| Model | Data | Maks. czas trwania | Maks. rozdzielczość | Otwarte wagi? | Uwagi |
|-------|------|-------------|---------|--------------|---------|
| Sora (OpenAI) | 2024-02 | 60 s | 1080p | Nie | Pierwszy model wykazujący właściwości symulatora świata w tej skali |
| Sora Turbo | 2024-12 | 20 s | 1080p | Nie | Wersja produkcyjna Sory z 5-krotnie szybszym wnioskowanием |
| Veo 2 (Google) | 2024-12 | 8 s | 4K | Nie | Najwyższa jakość i odwzorowanie fizyki w 2025 roku |
| Veo 3 | III kw. 2025 | 15 s | 4K | Nie | Natywny dźwięk i lepsza kontrola kamery |
| Kling 1.5 / 2.1 (Kuaishou) | 2024–2025 | 10 s | 1080p | Nie | Najlepsza animacja postaci ludzkich w I kw. 2025 r. |
| Runway Gen-3 Alpha | 2024-06 | 10 s | 768p | Nie | Profesjonalne narzędzia wideo |
| Pika 2.0 | 2024-10 | 5 s | 1080p | Nie | Najlepsza spójność postaci |
| CogVideoX (THUDM) | 2024 | 10 s | 720p | Tak (2B, 5B) | Pierwsze otwarte wideo klasy 5B |
| HunyuanVideo (Tencent) | 2024-12 | 5 s | 720p | Tak (13B) | Otwarty stan techniki pod koniec 2024 r. |
| Mochi-1 (Genmo) | 2024-10 | 5,4 s | 480p | Tak (10B) | Najbardziej liberalna licencja |
| WAN 2.2 (Alibaba) | 2025-07 | 5 s | 720p | Tak | Najsilniejszy model open-source w połowie 2025 r. |

Modele o otwartych wagach nadrabiają zaległości szybciej niż miało to miejsce w przypadku generowania obrazów. Rozwiązania oparte na LoRA dla HunyuanVideo i WAN 2.2 obsługują już większość przepływów pracy open-source do połowy 2026 roku.

## Zbuduj to

`code/main.py` symuluje podstawową koncepcję czasoprzestrzennego DiT: patchowanie małego syntetycznego wideo, dodawanie osadzeń pozycyjnych do poszczególnych bloków i odszumianie całej sekwencji za pomocą mechanizmu uwagi transformatora. Bez NumPy — wyłącznie czysty Python. Demonstracja pokazuje, że spójność czasowa wyłania się nawet w jednym wymiarze, gdy sąsiadujące klatki dzielą osadzenie pozycyjne i procesor odszumiania.

### Krok 1: patchowanie syntetycznego „wideo" 1D

```python
def make_video(T_frames=8, rng=None):
    # a "video" is a sequence of 1-D values following a smooth trajectory
    base = rng.gauss(0, 1)
    return [base + 0.3 * t + rng.gauss(0, 0.1) for t in range(T_frames)]
```

### Krok 2: osadzanie pozycji w każdej klatce

```python
def pos_embed(t, dim):
    return sinusoidal(t, dim)
```

### Krok 3: denoiser przetwarza całą sekwencję

Zamiast odszumiać każdą klatkę oddzielnie, mała sieć łączy wartości wszystkich klatek wraz z ich osadzeniami pozycyjnymi i jednocześnie przewiduje szum dla całej sekwencji.

### Krok 4: test spójności czasowej

Po trenowaniu należy przejrzeć przykładowy film i zmierzyć delty między klatkami. Jeżeli model nauczył się struktury czasowej, delty będą mniejsze niż przy niezależnym próbkowaniu każdej klatki.

## Pułapki

- **Niezależne próbkowanie klatek = migotanie.** Gdy dyfuzja obrazu jest uruchamiana osobno dla każdej klatki, wynik miga, ponieważ szum każdej klatki jest niezależny. Dyfuzja wideo eliminuje ten problem przez połączenie klatek za pomocą uwagi lub wspólnego szumu.
- **Naiwna uwaga 3D = brak pamięci.** Pełna uwaga 3D w 10-sekundowym filmie 1080p wymaga setek miliardów operacji. Należy rozbić ją na komponenty przestrzenny i czasowy.
- **Jakość opisów ważniejsza niż rozmiar zbioru.** Kluczowym usprawnieniem Sory w porównaniu z wcześniejszymi pracami było trenowanie na opisach około 10-krotnie bardziej szczegółowych (klipy opisane ponownie przez GPT-4). Raport techniczny OpenAI wyraźnie to potwierdza.
- **Kondycjonowanie pierwszą klatką.** Większość modeli produkcyjnych przyjmuje również obraz jako pierwszą klatkę — jest to tryb „obraz na wideo"; trenowanie uwzględnia ten wariant.
- **Dryf fizyczny.** Dłuższe klipy (powyżej 10 s) gromadzą subtelne niespójności. Pomocne jest generowanie przesuwnym oknem w połączeniu z zakotwiczaniem klatek kluczowych.

## Użyj tego

| Przypadek użycia | Wybór w 2026 r. |
|---------|-----------|
| Najwyższa jakość generowania wideo z tekstu, hostowane | Veo 3 lub Sora |
| Wideo z kontrolą kamery | Runway Gen-3 z pędzlami ruchu |
| Spójność postaci między klipami | Pika 2.0 lub Kling 2.1 |
| Otwarte wagi, szybkie dostrajanie | WAN 2.2 + LoRA |
| Obraz na wideo | WAN 2.2-I2V, Kling 2.1 I2V lub Runway |
| Synchronizacja ust audio-wideo | Veo 3 (natywny dźwięk) lub dedykowany model z synchronizacją ruchu warg |
| Edycja wideo | Runway Act-2, Kling Motion Brush, Flux-Kontext (nieruchoma klatka) |

Koszt jednej sekundy wideo przy porównywalnej jakości spadł 20-krotnie w latach 2024–2026.

## Wyślij to

Zapisz `outputs/skill-video-brief.md`. Umiejętność tworzy zwięzły opis filmu (czas trwania, proporcje, styl, plan kamery, spójność tematu, dźwięk) oraz zawiera: wybór modelu i hosting, szkielet podpowiedzi (język kamery, opis obiektu, deskryptory ruchu), dane wyjściowe z protokołem powtarzalności oraz listę kontrolną jakości na poziomie klatki.

## Ćwiczenia

1. **Łatwe.** W `code/main.py` porównaj delty między klatkami dla: (a) niezależnego próbkowania klatka po klatce i (b) próbkowania połączonej sekwencji. Podaj średnią i wariancję delt.
2. **Średnie.** Dodaj kondycjonowanie pierwszą klatką: przypnij klatkę 0 do zadanej wartości i próbkuj pozostałe. Zmierz, jak przypisana wartość propaguje się przez sekwencję.
3. **Trudne.** Użyj biblioteki diffusers z HuggingFace, aby uruchomić CogVideoX-2B na lokalnym GPU. Zmierz czas 20 kroków wnioskowania w rozdzielczości 720p dla 6-sekundowego klipu. Sprofiluj uwagę czasoprzestrzenną w celu zidentyfikowania wąskiego gardła.

## Kluczowe terminy

| Termin | Jak się mówi | Co to oznacza |
|------|-----------------|----------------------|
| Wideo VAE | „3D VAE" | Enkoder kompresujący `(T, H, W, C)` do utajonej reprezentacji czasoprzestrzennej. |
| Łatki | „Tokeny" | Trójwymiarowe bloki o stałym rozmiarze w przestrzeni utajonej; wejście do DiT. |
| Faktoryzowana uwaga | „Przestrzenna + czasowa" | Uwaga stosowana najpierw w przestrzeni, potem w czasie; bez pełnej uwagi 3D. |
| Obraz na wideo (I2V) | „Animuj to zdjęcie" | Model przyjmuje obraz i tekst, generując wideo rozpoczynające się od tego obrazu. |
| Kondycjonowanie klatkami kluczowymi | „Klatki kotwiczne" | Przypinanie wybranych klatek w celu sterowania przebiegiem wideo. |
| Pędzel ruchu | „Wskazówka kierunkowa" | Element interfejsu, w którym użytkownik rysuje wektory ruchu bezpośrednio na obrazie. |
| Ponowne opisywanie | „Gęste napisy" | Użycie modelu językowego do ponownego opisania klipów treningowych szczegółowymi podpowiedziami. |
| Migotanie | „Artefakt czasowy" | Niespójność między klatkami; usuwana przez sprzężone odszumianie. |

## Uwaga dla inżynierów: utajone wideo to problem z przepustowością pamięci

10-sekundowy klip 1080p przy 24 kl./s to 240 klatek × 1920 × 1080 × 3 ≈ 1,5 GB surowych pikseli. Po 4-krotnej kompresji przez wideo VAE (`2× przestrzennie × 2× czasowo`) reprezentacja utajona zajmuje około 100 MB na żądanie. Przepuszczenie jej przez czasoprzestrzenny DiT dla 30 kroków z rozmiarem partii 1 powoduje przesył około 3 GB/krok przez HBM — wąskim gardłem jest przepustowość pamięci, a nie liczba operacji zmiennoprzecinkowych.

Trzy główne parametry produkcyjne, zaczerpnięte wprost z literatury wdrożeniowej:

- **TP w całym DiT.** Modele z tekstu na wideo mają rutynowo powyżej 10 miliardów parametrów. Paralelizm tensorowy TP=4 na 4 kartach H100 jest standardem; PP=2 × TP=2 dla modeli klasy 405B. Opóźnienie na krok maleje w przybliżeniu liniowo wraz ze wzrostem TP, do granicy narzuconej przez operację all-reduce.
- **Grupowanie klatek jako ciągłe przetwarzanie wsadowe.** Podczas generowania wideo jest ono koncepcyjnie partią klatek połączonych uwagą. Sprawdza się tu ciągłe przetwarzanie wsadowe (harmonogramowanie w locie): renderowanie klatki `t+1` można rozpocząć w trakcie zwracania klatki `t-1`, jeśli architektura modelu obsługuje generowanie przesuwnym oknem.
- **Pamięć podręczna wstępnego wypełniania na poziomie klipu.** W trybie obraz na wideo kondycjonowanie pierwszą klatką jest analogiczne do wstępnego wypełniania podpowiedzi w LLM: wystarczy obliczyć je raz i ponownie używać przy kolejnych przejściach dekodera. W istocie jest to pamięć podręczna KV dla wideo.

## Dalsze czytanie

- [Brooks i in. (2024). Modele generacji wideo jako symulatory świata](https://openai.com/index/video-generation-models-as-world-simulators/) — raport techniczny Sory.
- [Yang i in. (2024). CogVideoX: modele dyfuzji tekstu na wideo z profesjonalnym transformatorem](https://arxiv.org/abs/2408.06072) — CogVideoX.
- [Kong i in. (2024). HunyuanVideo: systematyczna struktura dla dużych modeli generowania wideo](https://arxiv.org/abs/2412.03603) — HunyuanVideo.
- [Genmo (2024). Raport techniczny Mochi-1](https://www.genmo.ai/blog/mochi) — Mochi-1.
- [Alibaba (2025). WAN 2.2](https://wanvideo.io/) — otwarty stan techniki w połowie 2025 r.
- [Ho, Salimans, Gritsenko i in. (2022). Modele dyfuzji wideo](https://arxiv.org/abs/2204.03458) — przełomowa praca na temat dyfuzji wideo.
- [Blattmann i in. (2023). Align Your Latents (Video LDM)](https://arxiv.org/abs/2304.08818) — poprzednik stabilnej dyfuzji wideo.
