# Spektrogramy, skala Mel i funkcje audio

> Sieci neuronowe słabo wykorzystują surowe przebiegi. Konsumują spektrogramy. Jeszcze lepiej zużywają spektrogramy Mel. Każdy klasyfikator ASR, TTS i audio w 2026 roku będzie żył lub umierał w wyniku tego pojedynczego wyboru przetwarzania wstępnego.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 6 · 01 (Podstawy dźwięku)
**Czas:** ~45 minut

## Problem

Nagraj 10-sekundowy klip 16 kHz. To 160 000 elementów pływających, wszystkie w `[-1, 1]`, prawie całkowicie niepowiązanych z etykietą „szczekanie psa” lub „słowo kot”. Surowy przebieg zawiera informacje, ale w formie, której model nie może łatwo wyodrębnić. Dwa identyczne fonemy wymawiane w odstępie 100 ms mają zupełnie różne surowe próbki.

Spektrogram rozwiązuje ten problem. Załamuje szczegóły czasowe tam, gdzie ludzka percepcja je ignoruje (jitter mikrosekundowy) i zachowuje strukturę, w której uczestniczy percepcja (które częstotliwości są energetyczne, w oknach czasowych ~ 10–25 ms).

Spektrogramy Mel idą dalej. Ludzie postrzegają wysokość dźwięku logarytmicznie: częstotliwości 100 Hz i 200 Hz brzmią „w tej samej odległości od siebie”, co częstotliwości 1000 Hz i 2000 Hz. Skala Mel dopasowuje oś częstotliwości do siebie. Spektrogram w skali melowej jest najważniejszą cechą ML mowy w latach 2010–2026.

## Koncepcja

![Przebieg do STFT, spektrogram mel do drabinki MFCC](../assets/mel-features.svg)

**STFT (krótka transformata Fouriera).** Pokrój przebieg na nakładające się ramki (typowo: okno 25 ms, skok 10 ms = 400 próbek / 160 próbek przy 16 kHz). Pomnóż każdą klatkę przez funkcję okna (Hann jest wartością domyślną; Hamming nieco inny kompromis). FFT każdej klatki. Ułóż widma wielkości w macierz kształtu `(n_frames, n_freq_bins)`. To jest twój spektrogram.

**Log magnitudo.** Surowe magnitudo obejmuje 5-6 rzędów wielkości. Użyj `log(|X| + 1e-6)` lub `20 * log10(|X|)`, aby skompresować zakres dynamiczny. Każdy rurociąg produkcyjny wykorzystuje wielkość logarytmiczną, a nie wielkość surową.

**Skala Mel.** Częstotliwość `f` w Hz odwzorowuje mel `m` według `m = 2595 * log10(1 + f / 700)`. Mapowanie jest w przybliżeniu liniowe poniżej 1 kHz i w przybliżeniu logarytmiczne powyżej. Standardowym wejściem ASR jest 80 pojemników mel obejmujących pasmo 0–8 kHz.

**Bank filtrów Mel.** Zestaw trójkątnych filtrów rozmieszczonych w równych odstępach w skali Mel. Każdy filtr jest sumą ważoną sąsiednich pojemników FFT. Mnożenie wielkości STFT przez macierz banku filtrów daje spektrogram mel w jednym matmul.

**Spektrogram log-mel.** `log(mel_spec + 1e-10)`. Wpis Szeptu. Wkład papugi. Wejście SeamlessM4T. Uniwersalny interfejs audio na rok 2026.

**MFCC.** Weź spektrogram log-mel, zastosuj DCT (typ II), zachowaj pierwsze 13 współczynników. Dekoreluje cechy i dalej je kompresuje. Cecha dominująca do około 2015 r., kiedy nadrobiły zaległości CNN/Transformers na surowych kłodach. Nadal używany w rozpoznawaniu mówców (wektory x, ECAPA).

**Zmiana rozdzielczości.** Większa wartość FFT = lepsza rozdzielczość częstotliwościowa, ale gorsza rozdzielczość czasowa. Domyślne ustawienie audio-ML to 25 ms / 10 ms; 50 ms / 12,5 ms dla muzyki; 5 ms / 2 ms dla wykrywania stanów przejściowych (uderzenia w bębny, dźwięki wybuchowe).

## Zbuduj to

### Krok 1: wykadruj przebieg

```python
def frame(signal, frame_len, hop):
    n = 1 + (len(signal) - frame_len) // hop
    return [signal[i * hop : i * hop + frame_len] for i in range(n)]
```

10-sekundowy klip 16 kHz z `frame_len=400, hop=160` daje 998 klatek.

### Krok 2: Okno Hanna

```python
import math

def hann(N):
    return [0.5 * (1 - math.cos(2 * math.pi * n / (N - 1))) for n in range(N)]
```

Pomnóż elementarnie przed FFT. Usuwa wyciek widma spowodowany obcięciem w niezerowych punktach końcowych.

### Krok 3: Wielkość STFT

```python
def stft_magnitude(signal, frame_len=400, hop=160):
    win = hann(frame_len)
    frames = frame(signal, frame_len, hop)
    return [magnitudes(dft([w * s for w, s in zip(win, f)])) for f in frames]
```

W produkcji zastosowano `torch.stft` lub `librosa.stft` (w oparciu o technologię FFT, wektoryzację). Pętla ma tutaj charakter pedagogiczny; działa na krótkich klipach w `code/main.py`.

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

80 meli obejmujących 0–8 kHz z `n_fft=400` daje macierz `(80, 201)`. Pomnóż `(n_frames, 201)` wielkość STFT przez transpozycję, aby otrzymać spektrogram mel `(n_frames, 80)`.

### Krok 5: log-mel

```python
def log_mel(mel_spec, eps=1e-10):
    return [[math.log(max(v, eps)) for v in frame] for frame in mel_spec]
```

Typowe alternatywy: `librosa.power_to_db` (dB znormalizowany względem odniesienia), `10 * log10(power + eps)`. Whisper używa bardziej złożonej procedury klip + normalizacja (zobacz `log_mel_spectrogram` Whispera).

### Krok 6: MFCC

```python
def dct_ii(x, n_coeffs):
    N = len(x)
    return [
        sum(x[n] * math.cos(math.pi * k * (2 * n + 1) / (2 * N)) for n in range(N))
        for k in range(n_coeffs)
    ]
```

Zastosuj DCT do każdej ramki log-mel, zachowaj pierwsze 13 współczynników. To jest twoja macierz MFCC. Pierwszy współczynnik jest zwykle pomijany (koduje energię całkowitą).

## Użyj tego

Stos na rok 2026:

| Zadanie | Funkcje |
|------|--------------|
| ASR (szept, papuga, SeamlessM4T) | 80 log-melów, przeskok 10 ms, okno 25 ms |
| Model akustyczny TTS (VITS, F5-TTS, Kokoro) | 80 meli, skok 5–12 ms dla doskonałej kontroli czasowej |
| Klasyfikacja audio (AST, PANN, BEAT) | 128 log-melów, przeskok 10 ms |
| Osadzanie głośników (ECAPA-TDNN, WavLM) | 80 log-melów lub surowy SSL |
| Muzyka (MusicGen, Stable Audio 2) | Oddzielne tokeny EnCodec (nie mel) |
| Wyszukiwanie słów kluczowych | 40 MFCC dla małych urządzeń |

Praktyczna zasada: **jeśli nie pracujesz nad muzyką, zacznij od 80 log-melów.** Ciężar dowodu spoczywa na każdym odchyleniu.

## Pułapki, które nadal będą widoczne w 2026 r

- **Niedopasowanie liczby Mel.** Trening z 80 Melami, wniosek z 128 Melami. Cicha porażka. Zarejestruj kształt elementu na obu końcach.
- **Niedopasowanie częstotliwości próbkowania w górę strumienia.** Meldunki obliczone przy 22,05 kHz wyglądają inaczej niż przy 16 kHz. Napraw SR *przed* funkcją.
- **dB vs log.** Whisper oczekuje log-mel, a nie dB-mel. Niektóre rurociągi HF automatycznie wykrywają; Twój niestandardowy kod nie będzie.
- **Dryf normalizacji.** Normalizacja na podstawie wypowiedzi podczas uczenia, normalizacja globalna podczas wnioskowania. Błąd produkcyjny podwajający WER.
- **Wyciek z dopełnienia.** Wypełnienie zerami na końcu klipu powoduje powstanie płaskiego widma w końcowych klatkach. Pad symetrycznie lub replikacyjnie.

## Wyślij to

Zapisz jako `outputs/skill-feature-extractor.md`. Umiejętność wybiera typ funkcji, liczbę meli, liczbę klatek/skoków i normalizację dla danego celu modelu.

## Ćwiczenia

1. **Łatwe.** Uruchom `code/main.py`. Syntetyzuje sygnał chirp (przemiatanie częstotliwości 200 → 4000 Hz) i drukuje bin argmax mel na klatkę. Narysuj (opcjonalnie) i potwierdź, że pasuje do przeciągnięcia.
2. **Średni.** Uruchom ponownie z `n_mels` w `{40, 80, 128}` i `frame_len` w `{200, 400, 800}`. Zmierz szerokość pasma o ostrym szczycie na osi czasu. Która kombinacja najlepiej rozwiązuje ćwierkanie?
3. **Trudne.** Zaimplementuj `power_to_db` i porównaj dokładność ASR małego klasyfikatora CNN na AudioMNIST, używając (a) surowego log-mel, (b) dB-mel z `ref=max`, (c) MFCC-13 + delta + delta-delta. Zgłoś najwyższą dokładność.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Rama | Kawałek | Fragment przebiegu o długości 25 ms podawany do jednego FFT. |
| Hop | Krok | Próbki pomiędzy kolejnymi klatkami; Wartość domyślna ASR wynosi 10 ms. |
| Okno | Sprawa Hanna/Hamminga | Mnożnik punktowy zwężający krawędzie ramki do zera. |
| STFT | Generator spektrogramów | Oprawione + okienko FFT; daje macierz czasu × częstotliwości. |
| Mel | Wypaczona częstotliwość | Skala logarytmiczna; `m = 2595·log10(1 + f/700)`. |
| Bank filtrów | Matryca | Filtry trójkątne, które wyświetlają STFT na pojemnikach mel. |
| Log-mel | Wpis Szeptu | `log(mel_spec + eps)`; ujednolicone w 2026 r. |
| MFCC | Funkcja starej szkoły | DCT log-melu; 13 współczynników, dekorelowanych. |

## Dalsze czytanie

- [Davis, Mermelstein (1980). Porównanie reprezentacji parametrycznych w rozpoznawaniu słów jednosylabowych](https://ieeexplore.ieee.org/document/1163420) — artykuł MFCC.
- [Stevens, Volkmann, Newman (1937). Skala pomiaru wysokości psychologicznej] (https://pubs.aip.org/asa/jasa/article-abstract/8/3/185/735757/) — oryginalna skala Mel.
- [OpenAI — źródło Whisper, log_mel_spectrogram](https://github.com/openai/whisper/blob/main/whisper/audio.py) — przeczytaj implementację referencyjną.
- [dokumentacja ekstrakcji funkcji librosa](https://librosa.org/doc/main/feature.html) — odniesienie do `mfcc`, `melspectrogram` i hop/window.
- [NVIDIA NeMo — wstępne przetwarzanie dźwięku](https://docs.nvidia.com/deeplearning/nemo/user-guide/docs/en/main/asr/asr_all.html#featurizers) — potok na skalę produkcyjną dla modeli Parakeet + Canary.