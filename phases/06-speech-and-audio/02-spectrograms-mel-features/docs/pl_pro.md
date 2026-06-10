# Spektrogramy, skala Mel i cechy audio

> Sieci neuronowe słabo radzą sobie z surowymi przebiegami. Pobierają spektrogramy. Jeszcze lepiej — spektrogramy Mel. Każdy klasyfikator ASR, TTS i audio w 2026 roku stoi lub upada w zależności od tego jednego wyboru preprocessingu.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 6 · 01 (Podstawy dźwięku)
**Czas:** ~45 minut

## Problem

Nagraj 10-sekundowy klip przy 16 kHz. Otrzymasz 160 000 wartości zmiennoprzecinkowych z zakresu `[-1, 1]`, które są niemal całkowicie niezwiązane z etykietą „szczekanie psa" czy „słowo kot". Surowy przebieg zawiera informację, lecz w postaci, z której model nie może jej łatwo wydobyć. Dwa identyczne fonemy wymówione w odstępie 100 ms mają zupełnie różne surowe próbki.

Spektrogram rozwiązuje ten problem. Pomija szczegóły czasowe tam, gdzie ludzka percepcja je ignoruje (mikrosekundowy jitter) i zachowuje strukturę istotną perceptualnie — czyli to, które częstotliwości są energetyczne w oknach czasowych rzędu 10–25 ms.

Spektrogramy Mel idą jeszcze dalej. Ludzie postrzegają wysokość dźwięku logarytmicznie: odległość między 100 Hz a 200 Hz brzmi tak samo jak między 1000 Hz a 2000 Hz. Skala Mel dopasowuje oś częstotliwości do tej właściwości. Spektrogram w skali melowej to najważniejsza cecha ML dla mowy w latach 2010–2026.

## Koncepcja

![Przebieg do STFT, spektrogram mel do drabinki MFCC](../assets/mel-features.svg)

**STFT (krótka transformata Fouriera).** Podziel przebieg na nakładające się ramki (typowo: okno 25 ms, skok 10 ms, czyli 400 próbek i 160 próbek przy 16 kHz). Każdą ramkę pomnóż przez funkcję okna (domyślnie Hann; Hamming daje nieco inny kompromis). Wykonaj FFT każdej ramki. Ułóż widma amplitud w macierz o kształcie `(n_frames, n_freq_bins)`. To jest Twój spektrogram.

**Amplituda logarytmiczna.** Surowe amplitudy obejmują 5–6 rzędów wielkości. Zastosuj `log(|X| + 1e-6)` lub `20 * log10(|X|)`, aby skompresować zakres dynamiczny. Każdy potok produkcyjny korzysta z amplitudy logarytmicznej, nie surowej.

**Skala Mel.** Częstotliwość `f` w Hz odwzorowuje się na wartość mel `m` według wzoru `m = 2595 * log10(1 + f / 700)`. Odwzorowanie jest w przybliżeniu liniowe poniżej 1 kHz i logarytmiczne powyżej. Standardowym wejściem ASR jest 80 pojemników mel obejmujących pasmo 0–8 kHz.

**Bank filtrów Mel.** Zestaw trójkątnych filtrów rozmieszczonych równomiernie w skali Mel. Każdy filtr stanowi ważoną sumę sąsiednich pojemników FFT. Pomnożenie amplitud STFT przez macierz banku filtrów daje spektrogram mel za pomocą jednego mnożenia macierzowego.

**Spektrogram log-mel.** `log(mel_spec + 1e-10)`. Wejście Whispera. Wejście Parrot. Wejście SeamlessM4T. Uniwersalny interfejs audio na rok 2026.

**MFCC.** Pobierz spektrogram log-mel, zastosuj DCT (typ II), zachowaj pierwsze 13 współczynników. Dekoreluje cechy i dodatkowo je kompresuje. Dominująca reprezentacja do około 2015 r., gdy sieci CNN i Transformery dorównały jej jakością przy pracy na surowych cechach. Nadal stosowana w rozpoznawaniu mówców (wektory x, ECAPA).

**Kompromis rozdzielczości.** Większy rozmiar FFT oznacza lepszą rozdzielczość częstotliwościową, lecz gorszą czasową. Domyślne ustawienie w ML audio to 25 ms / 10 ms; dla muzyki 50 ms / 12,5 ms; dla wykrywania stanów przejściowych (uderzenia w bębny, dźwięki wybuchowe) 5 ms / 2 ms.

## Zbuduj to

### Krok 1: podział przebiegu na ramki

```python
def frame(signal, frame_len, hop):
    n = 1 + (len(signal) - frame_len) // hop
    return [signal[i * hop : i * hop + frame_len] for i in range(n)]
```

10-sekundowy klip 16 kHz z `frame_len=400, hop=160` daje 998 ramek.

### Krok 2: okno Hanna

```python
import math

def hann(N):
    return [0.5 * (1 - math.cos(2 * math.pi * n / (N - 1))) for n in range(N)]
```

Pomnóż element po elemencie przed FFT. Eliminuje wyciek widma wynikający z obcięcia sygnału w niezerowych punktach końcowych.

### Krok 3: amplituda STFT

```python
def stft_magnitude(signal, frame_len=400, hop=160):
    win = hann(frame_len)
    frames = frame(signal, frame_len, hop)
    return [magnitudes(dft([w * s for w, s in zip(win, f)])) for f in frames]
```

W środowiskach produkcyjnych stosuje się `torch.stft` lub `librosa.stft` (oparte na algorytmie FFT, zwektoryzowane). Pętla ma tu charakter dydaktyczny i działa na krótkich klipach w `code/main.py`.

### Krok 4: bank filtrów Mel

```python
def hz_to_mel(f):
    return 2595.0 * math.log10(1.0 + f / 700.0)

def mel_to_hz(m):
    return 700.0 * (10 ** (m / 2595.0) - 1)

def mel_filterbank(n_mels, n_fft, sr, fmin=0, fmax=None):
    fmax = fmax or sr / 2
    mels = [hz_to_mel(fmin) + (hz_to_mel(fmax) - hz_to_mel(fmin)) * i / (n_mels + 1)
            for i in range(n_mels + 2)]
    hzs = [mel_to_hz(m) for m in mels]
    bins = [int(h * n_fft / sr) for h in hzs]
    fb = [[0.0] * (n_fft // 2 + 1) for _ in range(n_mels)]
    for m in range(n_mels):
        for k in range(bins[m], bins[m + 1]):
            fb[m][k] = (k - bins[m]) / max(1, bins[m + 1] - bins[m])
        for k in range(bins[m + 1], bins[m + 2]):
            fb[m][k] = (bins[m + 2] - k) / max(1, bins[m + 2] - bins[m + 1])
    return fb
```

80 pojemników mel obejmujących 0–8 kHz przy `n_fft=400` daje macierz `(80, 201)`. Pomnóż amplitudy STFT o kształcie `(n_frames, 201)` przez jej transpozycję, aby uzyskać spektrogram mel `(n_frames, 80)`.

### Krok 5: log-mel

```python
def log_mel(mel_spec, eps=1e-10):
    return [[math.log(max(v, eps)) for v in frame] for frame in mel_spec]
```

Typowe alternatywy: `librosa.power_to_db` (decybele znormalizowane względem wartości odniesienia), `10 * log10(power + eps)`. Whisper stosuje bardziej złożoną procedurę obejmującą przycinanie i normalizację (zob. `log_mel_spectrogram` w kodzie Whispera).

### Krok 6: MFCC

```python
def dct_ii(x, n_coeffs):
    N = len(x)
    return [
        sum(x[n] * math.cos(math.pi * k * (2 * n + 1) / (2 * N)) for n in range(N))
        for k in range(n_coeffs)
    ]
```

Zastosuj DCT do każdej ramki log-mel i zachowaj pierwsze 13 współczynników. Tak powstaje macierz MFCC. Pierwszy współczynnik jest zazwyczaj pomijany, ponieważ koduje energię całkowitą.

## Zastosowanie

Stos na rok 2026:

| Zadanie | Cechy |
|------|--------------|
| ASR (Whisper, Parrot, SeamlessM4T) | 80 log-melów, skok 10 ms, okno 25 ms |
| Akustyczny model TTS (VITS, F5-TTS, Kokoro) | 80 melów, skok 5–12 ms dla precyzyjnej kontroli czasowej |
| Klasyfikacja audio (AST, PANN, BEAT) | 128 log-melów, skok 10 ms |
| Osadzanie mówców (ECAPA-TDNN, WavLM) | 80 log-melów lub surowy SSL |
| Muzyka (MusicGen, Stable Audio 2) | Osobne tokeny EnCodec (nie mel) |
| Wyszukiwanie słów kluczowych | 40 MFCC dla urządzeń o ograniczonych zasobach |

Praktyczna zasada: **jeśli nie pracujesz z muzyką, zacznij od 80 log-melów.** Każde odstępstwo wymaga uzasadnienia.

## Pułapki, na które warto uważać w 2026 r.

- **Niezgodność liczby pojemników Mel.** Trenowanie z 80 pojemnikami, wnioskowanie z 128. Błąd cichy. Loguj kształt cech po obu stronach potoku.
- **Niezgodna częstotliwość próbkowania na wejściu.** Cechy mel obliczone przy 22,05 kHz wyglądają inaczej niż przy 16 kHz. Ustaw poprawną częstotliwość próbkowania *przed* ekstrakcją cech.
- **dB kontra log.** Whisper oczekuje log-mel, nie dB-mel. Niektóre potoki HuggingFace wykrywają to automatycznie — własny kod nie będzie.
- **Dryf normalizacji.** Normalizacja per wypowiedź podczas treningu, normalizacja globalna podczas wnioskowania. Taki błąd produkcyjny może podwoić WER.
- **Wyciek z dopełnienia.** Uzupełnianie zerami na końcu klipu tworzy płaskie widmo w końcowych ramkach. Stosuj dopełnianie symetryczne lub przez replikację.

## Zadanie do wykonania

Zapisz jako `outputs/skill-feature-extractor.md`. Umiejętność dobiera typ cech, liczbę pojemników mel, długość ramki i skok oraz normalizację dla danego zadania modelowego.

## Ćwiczenia

1. **Łatwe.** Uruchom `code/main.py`. Skrypt syntetyzuje sygnał chirp (przemiatanie od 200 do 4000 Hz) i wypisuje indeks pojemnika mel z maksymalną energią dla każdej ramki. Opcjonalnie narysuj wykres i sprawdź, czy odpowiada oczekiwanemu przebiegowi częstotliwości.
2. **Średnie.** Uruchom skrypt ponownie dla `n_mels` z zakresu `{40, 80, 128}` i `frame_len` z zakresu `{200, 400, 800}`. Zmierz szerokość pasma wyraźnego szczytu na osi czasu. Która kombinacja najlepiej odwzorowuje przebieg chirpu?
3. **Trudne.** Zaimplementuj `power_to_db` i porównaj dokładność małego klasyfikatora CNN na zbiorze AudioMNIST, używając: (a) surowego log-mel, (b) dB-mel z `ref=max`, (c) MFCC-13 z deltą i deltą-deltą. Raportuj najwyższą uzyskaną dokładność.

## Kluczowe pojęcia

| Termin | Potoczne określenie | Właściwe znaczenie |
|------|-----------------|----------------------|
| Rama | Fragment | Wycinek przebiegu o długości 25 ms podawany do jednego FFT. |
| Hop | Krok | Liczba próbek między kolejnymi ramkami; domyślnie 10 ms w ASR. |
| Okno | Filtr Hanna/Hamminga | Mnożnik wygładzający krawędzie ramki do zera. |
| STFT | Generator spektrogramów | FFT z ramkowaniem i oknem; daje macierz czas × częstotliwość. |
| Mel | Zniekształcona częstotliwość | Skala logarytmiczna; `m = 2595·log10(1 + f/700)`. |
| Bank filtrów | Macierz | Filtry trójkątne odwzorowujące STFT na pojemniki mel. |
| Log-mel | Wejście Whispera | `log(mel_spec + eps)`; standard w 2026 r. |
| MFCC | Klasyczna cecha | DCT log-melu; 13 dekorelowanych współczynników. |

## Literatura uzupełniająca

- [Davis, Mermelstein (1980). Porównanie reprezentacji parametrycznych w rozpoznawaniu słów jednosylabowych](https://ieeexplore.ieee.org/document/1163420) — oryginalny artykuł o MFCC.
- [Stevens, Volkmann, Newman (1937). Skala pomiaru wysokości psychologicznej](https://pubs.aip.org/asa/jasa/article-abstract/8/3/185/735757/) — pierwotna definicja skali Mel.
- [OpenAI — kod źródłowy Whispera, log_mel_spectrogram](https://github.com/openai/whisper/blob/main/whisper/audio.py) — implementacja referencyjna.
- [Dokumentacja ekstrakcji cech librosa](https://librosa.org/doc/main/feature.html) — opis funkcji `mfcc`, `melspectrogram` oraz parametrów hop i window.
- [NVIDIA NeMo — preprocessing audio](https://docs.nvidia.com/deeplearning/nemo/user-guide/docs/en/main/asr/asr_all.html#featurizers) — produkcyjny potok dla modeli Parakeet i Canary.
