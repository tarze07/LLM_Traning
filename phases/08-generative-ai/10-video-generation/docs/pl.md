# Generowanie wideo

> Obraz jest tensorem 2-D. Film jest filmem 3D. Teoria jest taka sama; obliczenia są 10-100 razy trudniejsze. Sora z OpenAI (luty 2024) udowodniła, że ​​jest to możliwe. Do 2026 r. Veo 2, Kling 1.5, Runway Gen-3, Pika 2.0 i WAN 2.2 będą dostarczać wideo z tekstem w rozdzielczości 1080p, a stos otwartych wag (CogVideoX, HunyuanVideo, Mochi-1, WAN 2.2) będzie opóźniony o 12 miesięcy.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 8 · 07 (dyfuzja utajona), Faza 7 · 09 (ViT), Faza 8 · 06 (DDPM)
**Czas:** ~45 minut

## Problem

10-sekundowy film 1080p przy 24 klatkach na sekundę to 240 klatek o rozdzielczości 1920 × 1080 × 3 pikseli. To ~1,5 GB surowych danych na klip. Dyfuzja w przestrzeni pikseli jest niemożliwa. Potrzebujesz:

1. **Kompresja czasoprzestrzenna.** VAE, który koduje filmy, a nie klatki, w sekwencję fragmentów przestrzenno-czasowych.
2. **Spójność czasowa.** Ramki muszą udostępniać treść, oświetlenie i tożsamość obiektu w ciągu kilku sekund. Siatka musi modelować ruch.
3. **Oblicz budżet.** Szkolenie wideo jest 10-100 razy droższe niż obraz dla tego samego rozmiaru modelu.
4. **Kondycjonowanie.** Tekst, obraz (pierwsza klatka), dźwięk lub inny film. Większość modeli produkcyjnych akceptuje wszystkie cztery.

Architekturą, która rozwiązała ten problem, jest **Transformator dyfuzyjny (DiT)** zastosowany do fragmentów czasoprzestrzennych, trenowany na ogromnych zbiorach danych (podpowiedzi, podpisy, wideo). Takie same straty dyfuzyjne jak w lekcji 06.

## Koncepcja

![Rozpowszechnianie wideo: patchify, DiT, decode](../assets/video-generation.svg)

### Popraw

Zakoduj wideo za pomocą 3D VAE (wyuczona kompresja czasoprzestrzenna). Ukrytym elementem jest kształt `[T_latent, H_latent, W_latent, C_latent]`. Podzielony na fragmenty o rozmiarze `[t_p, h_p, w_p]`. W przypadku modeli w stylu Sora `t_p = 1` (łatki na klatkę) lub `t_p = 2` (co dwie klatki). 10-sekundowy film 1080p kompresuje się do ~20 000–100 000 fragmentów.

### Czasoprzestrzenny DiT

Transformator przetwarza płaską sekwencję poprawek. Każda łatka ma osadzenie pozycyjne 3D (czas + y + x). Uwaga jest zwykle rozkładana na czynniki:

- **Uwaga przestrzenna** w obszarach każdej klatki.
- **Uwaga czasowa** pomiędzy klatkami w tym samym miejscu przestrzennym.
- **Pełna uwaga 3D** jest 16-100x droższa; używane tylko w niskiej rozdzielczości lub w badaniach.

### Kondycjonowanie tekstu

Uwaga krzyżowa z koderem dużego tekstu (T5-XXL dla Sora, CogVideoX-5B wykorzystuje T5-XXL). Długie podpowiedzi mają znaczenie — zestaw szkoleniowy Sory zawierał gęste, wygenerowane przez GPT powtórzenia, średnio 200 tokenów na klip.

### Szkolenie

Standardowa strata dyfuzyjna (przewidywanie ε lub v) w stosunku do utajonych czasoprzestrzennych. Dane: wideo internetowe + ~100 mln wyselekcjonowanych klipów + syntetyczne podpisy tekstowe. Obliczenia: ponad 10 000 godzin procesora graficznego nawet w przypadku krótkiego okresu badawczego; Skala Sory wynosi ponad 100 000.

## Krajobraz produkcyjny w 2026 r

| Modelka | Data | Maksymalny czas trwania | Maksymalna rozdzielczość | Otwarte ciężary? | Godne uwagi |
|-------|------|-------------|---------|--------------|---------|
| Sora (OpenAI) | 2024-02 | lata 60. | 1080p | Nie | Pierwszy model pokazujący właściwości symulatora świata w skali |
| Sora Turbo | 2024-12 | lata 20. | 1080p | Nie | Produkcja Sora przy 5x szybszym wnioskowaniu |
| Veo 2 (Google) | 2024-12 | 8s | 4K | Nie | Najwyższa jakość + fizyka w 2025 roku |
| Veo 3 | III kw. 2025 | 15s | 4K | Nie | Natywny dźwięk i lepsza kontrola kamery |
| Kling 1,5 / 2,1 (Kuaishou) | 2024-2025 | 10 s | 1080p | Nie | Najlepszy ruch człowieka w I kw. 2025 r. |
| Pas startowy Gen-3 Alpha | 2024-06 | 10 s | 768p | Nie | Profesjonalne narzędzia wideo na górze |
| Pika 2.0 | 2024-10 | 5s | 1080p | Nie | Najsilniejsza spójność charakteru |
| CogVideoX (THUDM) | 2024 | 10 s | 720p | Tak (2B, 5B) | Pierwsze otwarte wideo w skali 5B |
| HunyuanVideo (Tencent) | 2024-12 | 5s | 720p | Tak (13B) | Otwarcie SOTA pod koniec 2024 r. |
| Mochi-1 (Genmo) | 2024-10 | 5,4 s | 480p | Tak (10B) | Najbardziej liberalna licencja |
| WAN 2.2 (Alibaba) | 2025-07 | 5s | 720p | Tak | Najsilniejszy model otwarty w połowie 2025 r. |

Otwarte wagi wypełniają lukę szybciej niż w przestrzeni obrazu: rozwiązania LoRA HunyuanVideo + WAN 2.2 obsługują już większość przepływów pracy typu open source do połowy 2026 r.

## Zbuduj to

`code/main.py` symuluje podstawową koncepcję czasoprzestrzenną DiT: patchowanie małego syntetycznego wideo, dodawanie osadzania pozycji w poszczególnych patchach i odszumianie całej sekwencji z uwagą w stylu transformatora nad poprawkami. Nie numpy; czysty Python. Pokazujemy, że spójność czasowa pojawia się nawet w 1-D, gdy obszary sąsiadujących klatek mają wspólne osadzenie odszumiające i pozycyjne.

### Krok 1: poprawka syntetycznego „wideo” 1-D

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

### Krok 3: denoiser widzi całą sekwencję

Zamiast odszumiać każdą klatkę niezależnie, nasza mała sieć łączy wszystkie wartości klatek wraz z osadzeniem ich pozycji i wspólnie przewiduje szum dla wszystkich klatek.

### Krok 4: test spójności czasowej

Po szkoleniu obejrzyj przykładowy film. Zmierz deltę między klatkami. Jeśli model nauczył się struktury czasowej, delty pozostają mniejsze niż próbkowanie każdej klatki niezależnie.

## Pułapki

- **Niezależne próbkowanie na klatkę = migotanie.** Jeśli dyfuzja obrazu zostanie uruchomiona dla każdej klatki oddzielnie, obraz wyjściowy będzie migotać, ponieważ szum każdej klatki jest niezależny. Dyfuzja wideo rozwiązuje ten problem, łącząc klatki poprzez uwagę lub wspólny szum.
- **Naiwna uwaga 3D = OOM.** Pełna uwaga 3D w 10-sekundowej rozdzielczości 1080p to setki miliardów operacji. Rozłóż na czynniki przestrzenne i czasowe.
- **Podpisy danych są ważniejsze niż ich rozmiar.** Głównym ulepszeniem Sory w porównaniu z poprzednią pracą było przeszkolenie w zakresie ~10 razy bardziej szczegółowych napisów (klipy ze zmienionym oznaczeniem GPT-4). Raport techniczny OpenAI jasno to opisuje.
- **Kondycjonowanie pierwszej klatki.** Większość modeli produkcyjnych akceptuje również obraz jako pierwszą klatkę. Jest to tryb „obraz na wideo”; szkolenie obejmuje ten wariant.
- **Dryf fizyczny.** Długie klipy (> 10 s) kumulują subtelne niespójności. Pomaga generowanie przesuwanego okna + zakotwiczenie klatek kluczowych.

## Użyj tego

| Przypadek użycia | wybór 2026 |
|---------|-----------|
| Najwyższa jakość konwersji tekstu na wideo, hostowana | Veo 3 lub Sora |
| Film sterowany kamerą | Pas startowy Gen-3 ze szczotkami ruchu |
| Spójność postaci w klipach | Pika 2.0 lub Kling 2.1 |
| Otwarte ciężary, szybkie dostrojenie | WAN 2.2 + LoRA |
| Obraz do wideo | WAN 2.2-I2V, Kling 2.1 I2V lub pas startowy |
| Synchronizacja ust audio-wideo | Veo 3 (natywny dźwięk) lub dedykowany model z synchronizacją ruchu warg |
| Edycja wideo | Runway Act-2, Kling Motion Brush, Flux-Kontext (nieruchoma klatka) |

Koszt sekundy wideo przy parytecie jakości spadł 20-krotnie w latach 2024–2026.

## Wyślij to

Zapisz `outputs/skill-video-brief.md`. Skill tworzy krótki opis filmu (czas trwania, proporcje, styl, plan kamery, spójność tematu, dźwięk) i wyniki: model + hosting, szybkie tworzenie szkieletu (język kamery, opis obiektu, deskryptory ruchu), materiał wyjściowy + protokół powtarzalności oraz lista kontrolna kontroli jakości na poziomie klatki.

## Ćwiczenia

1. **Easy.** W `code/main.py` porównaj deltę między klatkami dla (a) niezależnego próbkowania na klatkę, (b) próbkowania połączonej sekwencji. Podaj średnią i wariancję delt.
2. **Średni.** Dodaj warunek pierwszej klatki: przypnij klatkę 0 do danej wartości i próbkuj resztę. Zmierz sposób propagacji przypiętej wartości.
3. **Trudne.** Użyj dyfuzorów HuggingFace, aby uruchomić CogVideoX-2B na lokalnym procesorze graficznym. Czas 20 kroków wnioskowania w rozdzielczości 720p dla 6-sekundowego klipu. Sprofiluj uwagę czasoprzestrzenną, aby zidentyfikować wąskie gardło.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Wideo VAE | „3-D VAE” | Koder kompresujący `(T, H, W, C)` → utajony czasoprzestrzenny. |
| Łatki | „Tokeny” | Bloki 3-D o stałym rozmiarze utajonego; wejście do DiT. |
| Faktoryzowana uwaga | „Przestrzenne + czasowe” | Skup uwagę na przestrzeni, a następnie na czasie; pomiń pełną uwagę 3D. |
| Obraz do wideo (I2V) | „Animuj to zdjęcie” | Model pobiera obraz + tekst i generuje wideo, które się od niego zaczyna. |
| Kondycjonowanie klatek kluczowych | „Ramki kotwiczne” | Przypinaj określone klatki, aby kontrolować łuk wideo. |
| Pędzel ruchu | „Wskazówka kierunkowa” | Dane wejściowe interfejsu użytkownika, podczas których użytkownik maluje wektory ruchu na obrazie. |
| Ponowne napisy | „Gęste napisy” | Używanie LLM do ponownego oznaczania klipów szkoleniowych szczegółowymi podpowiedziami. |
| Migotanie | „Artefakt czasowy” | Niespójność między klatkami; naprawiono ze sprzężonym odszumianiem. |

## Uwaga producenta: utajone wideo to problem z przepustowością pamięci

10-sekundowy klip 1080p przy 24 kl./s to 240 klatek × 1920 × 1080 × 3 ≈ 1,5 GB surowych pikseli. Po 4-krotnej kompresji wideo VAE (`2 × spatial × 2 × temporal`) wartość ukryta wynosi ~100 MB na żądanie. Uruchom to przez czasoprzestrzenną DiT dla 30 kroków w partii 1 i przejdziesz ~ 3 GB/krok przez HBM – wąskim gardłem jest przepustowość pamięci, a nie FLOP.

Trzy pokrętła produkcyjne, wszystkie prosto z rozdziału o wnioskach z literatury dotyczącej produkcji:

- **TP w całym DiT.** Modele tekstu na wideo mają rutynowo parametry ≥10B. TP=4 w 4 H100 jest standardem; PP=2 × TP=2 dla modeli klasy 405B. Opóźnienie na krok spada mniej więcej liniowo wraz z TP aż do ściany all-reduce.
- ** Grupowanie klatek = ciągłe grupowanie.** W momencie generowania wideo jest koncepcyjnie partią klatek połączonych uwagą. Obowiązuje ciągłe przetwarzanie wsadowe (harmonogram w locie): rozpocznij renderowanie ramki `t+1` podczas zwracania ramki `t-1`, jeśli architektura modelu umożliwia generowanie przesuwanego okna.
- **Pamięć podręczna wstępnego wypełniania na poziomie klipu.** W przypadku przetwarzania obrazu na wideo warunkowanie pierwszej klatki jest analogiczne do wstępnego wypełniania podpowiedzi LLM: oblicz je raz i użyj ponownie w tymczasowych przejściach dekodera. Jest to właściwie pamięć podręczna KV dla wideo.

## Dalsze czytanie

- [Brooks i in. (2024). Modele generacji wideo jako symulatory świata](https://openai.com/index/video-generation-models-as-world-simulators/) — raport techniczny Sora.
- [Yang i in. (2024). CogVideoX: modele dyfuzji tekstu na wideo z profesjonalnym transformatorem](https://arxiv.org/abs/2408.06072) — CogVideoX.
- [Kong i in. (2024). HunyuanVideo: systematyczna struktura dla dużych modeli generowania wideo](https://arxiv.org/abs/2412.03603) — HunyuanVideo.
- [Genmo (2024). Raport techniczny Mochi-1](https://www.genmo.ai/blog/mochi) — Mochi-1.
- [Alibaba (2025). WAN 2.2](https://wanvideo.io/) — otwarcie SOTA w połowie 2025 r.
- [Ho, Salimans, Gritsenko i in. (2022). Modele dyfuzji wideo](https://arxiv.org/abs/2204.03458) — przełomowy artykuł dotyczący rozpowszechniania wideo.
- [Blattmann i in. (2023). Wyrównaj swoje latenty (Video LDM)](https://arxiv.org/abs/2304.08818) — przodek stabilnej dyfuzji wideo.