# Podstawy audio — kształty fal, próbkowanie, transformata Fouriera

> Przebiegi są surowym sygnałem. Spektrogramy są reprezentacją. Funkcje Mel są formą przyjazną ML. Każdy nowoczesny rurociąg ASR i TTS przechodzi po tej drabinie, a pierwszym szczeblem jest zrozumienie próbkowania i Fouriera.

**Typ:** Ucz się
**Języki:** Python
**Wymagania wstępne:** Faza 1 · 06 (wektory i macierze), faza 1 · 14 (rozkłady prawdopodobieństwa)
**Czas:** ~45 minut

## Problem

Mikrofon wytwarza sygnał zależności ciśnienia od czasu. Twoja sieć neuronowa zużywa tensory. Pomiędzy nimi znajduje się stos konwencji, których naruszenie powoduje ciche błędy: model trenuje dobrze, ale WER podwaja się, TTS generuje syk, albo system klonowania głosu zapamiętuje mikrofon zamiast głośnika.

Każdy błąd w systemach mowy ma swoje źródło w jednym z trzech pytań:

1. Z jaką częstotliwością próbkowania zarejestrowano dane i czego oczekuje model?
2. Czy sygnał jest aliasowany?
3. Czy operujesz na surowych próbkach czy na reprezentacji częstotliwościowej?

Zrób to dobrze, a reszta fazy 6 będzie łatwa do wykonania. Zrozum ich źle, a nawet Whisper-Large-v4 wygeneruje śmieci.

## Koncepcja

![Wizualizacja przebiegu, próbkowania, DFT i przedziałów częstotliwości](../assets/audio-fundamentals.svg)

**Format fali.** Jednowymiarowa tablica zmiennoprzecinkowych w `[-1.0, 1.0]`. Indeksowane według numeru próbki. Aby przeliczyć na sekundy, podziel przez częstotliwość próbkowania: `t = n / sr`. 10-sekundowy klip przy 16 kHz to tablica 160 000 pływaków.

**Częstotliwość próbkowania (sr).** Liczba próbek na sekundę. Wspólne stawki w 2026 r.:

| Oceń | Użyj |
|------|-----|
| 8 kHz | Telefonia, starsza wersja VOIP. Nyquist przy 4 kHz zabija spółgłoski. Unikaj dla ASR. |
| 16 kHz | Norma ASR. Whisper, Parakeet, SeamlessM4T v2 zużywają 16 kHz. |
| 22,05 kHz | Szkolenie wokodera TTS dla starszych modeli. |
| 24 kHz | Nowoczesne TTS (Kokoro, F5-TTS, xTTS v2). |
| 44,1 kHz | Płyta CD z dźwiękiem, muzyka. |
| 48 kHz | Film, pro audio, wysokiej jakości TTS (VALL-E 2, NaturalSpeech 3). |

**Nyquist-Shannon.** Częstotliwość próbkowania `sr` może jednoznacznie reprezentować częstotliwości do `sr/2`. Granicę `sr/2` stanowi *częstotliwość Nyquista*. Energia powyżej Nyquista ulega *aliasingowi* — sprowadzeniu do niższych częstotliwości — i zniekształca sygnał. Zawsze filtr dolnoprzepustowy przed próbkowaniem w dół.

**Głębia bitowa.** 16-bitowy PCM (ze znakiem int16, zakres ±32767) to uniwersalny format wymiany. 24-bitowy dla muzyki, 32-bitowy float dla wewnętrznego procesora DSP. Biblioteki takie jak `soundfile` odczytują int16, ale udostępniają tablice float32 w `[-1, 1]`.

**Transformata Fouriera.** Każdy skończony sygnał jest sumą sinusoid o różnych częstotliwościach. Dyskretna transformata Fouriera (DFT) oblicza dla próbek `N` złożone współczynniki `N` — po jednym na przedział częstotliwości. `bin k` odwzorowuje częstotliwość `k · sr / N` Hz. Wielkość to amplituda przy tej częstotliwości, kąt to faza.

**FFT.** Szybka transformata Fouriera: algorytm `O(N log N)` dla DFT, gdy `N` jest potęgą liczby 2. Każda biblioteka audio pod maską używa FFT. FFT o 1024 próbkach przy 16 kHz daje 512 użytecznych przedziałów częstotliwości w zakresie 0–8 kHz przy rozdzielczości 15,6 Hz.

**Obramowanie + okno.** Nie FFT całego klipu. Dzielimy ją na nakładające się *ramki* (zwykle 25 ms z 10 ms przeskokiem), mnożymy każdą klatkę przez funkcję okna (Hann, Hamming), aby wyeliminować nieciągłości krawędzi, a następnie FFT każdej klatki. Jest to krótkoczasowa transformata Fouriera (STFT). Lekcja 02 rozpoczyna się stąd.

## Zbuduj to

### Krok 1: przeczytaj klip i narysuj przebieg

`code/main.py` używa tylko modułu stdlib `wave`, aby zachować niezależność wersji demonstracyjnej. Do produkcji użyjesz `soundfile` lub `torchaudio.load` (oba zwracają krotki `(waveform, sr)`):

```python
import soundfile as sf
waveform, sr = sf.read("clip.wav", dtype="float32")  # shape (T,), sr=int
```

### Krok 2: zsyntetyzuj falę sinusoidalną na podstawie pierwszych zasad

```python
import math

def sine(freq_hz, sr, seconds, amp=0.5):
    n = int(sr * seconds)
    return [amp * math.sin(2 * math.pi * freq_hz * i / sr) for i in range(n)]
```

Sinus 440 Hz (koncert A) przy 16 kHz przez 1 sekundę to 16 000 pływaków. Pisz za pomocą `wave.open(..., "wb")`, używając 16-bitowego kodowania PCM.

### Krok 3: ręcznie oblicz DFT

```python
def dft(x):
    N = len(x)
    out = []
    for k in range(N):
        re = sum(x[n] * math.cos(-2 * math.pi * k * n / N) for n in range(N))
        im = sum(x[n] * math.sin(-2 * math.pi * k * n / N) for n in range(N))
        out.append((re, im))
    return out
```

`O(N²)` — w porządku dla `N=256` w celu potwierdzenia poprawności, bezużyteczne w przypadku prawdziwego dźwięku. Prawdziwy kod wywołuje `numpy.fft.rfft` lub `torch.fft.rfft`.

### Krok 4: znajdź dominującą częstotliwość

Indeks szczytowy wielkości `k_star` jest odwzorowywany na częstotliwość `k_star * sr / N`. Uruchomienie tego na sinusie 440 Hz powinno zwrócić wartość szczytową w bin `440 * N / sr`.

### Krok 5: zademonstruj aliasing

Próbkuj sinus 7 kHz przy 10 kHz (Nyquist = 5 kHz). Ton 7 kHz jest powyżej Nyquista i składa się do `10 − 7 = 3 kHz`. Szczyt FFT pojawia się przy 3 kHz. To jest klasyczne demo aliasingu i powód, dla którego każdy DAC/ADC jest wyposażony w ceglany filtr dolnoprzepustowy.

## Użyj tego

Stos, który faktycznie wyślesz w 2026 r.:

| Zadanie | Biblioteka | Dlaczego |
|------|---------|-----|
| Odczyt/zapis WAV/FLAC/OGG | `soundfile` (opakowanie pliku libsnd) | Najszybszy, stabilny, zwraca float32. |
| Ponowna próbka | `torchaudio.transforms.Resample` lub `librosa.resample` | Wbudowany poprawny antyaliasing. |
| STFT / Mel | `torchaudio` lub `librosa` | Przyjazny dla GPU; Ekosystem PyTorch. |
| Transmisja strumieniowa w czasie rzeczywistym | `sounddevice` lub `pyaudio` | Wieloplatformowe powiązania PortAudio. |
| Sprawdź plik | `ffprobe` lub `soxi` | CLI, szybko, raportuje sr/kanały/kodek. |

Zasada decyzji: **dopasuj częstotliwość próbkowania, zanim dopasujesz cokolwiek innego**. Whisper oczekuje sygnału monofonicznego o częstotliwości 16 kHz32. Podaj sygnał stereo 44,1 kHz, a otrzymasz śmieci, które wyglądają jak błąd modelu.

## Wyślij to

Zapisz jako `outputs/skill-audio-loader.md`. Umiejętność ta pomaga sprawdzić, czy wejście audio spełnia oczekiwania modelu końcowego, a jeśli tak nie jest, przeprowadza ponowne próbkowanie.

## Ćwiczenia

1. **Łatwe.** Zsyntetyzuj 1-sekundowy miks 220 Hz + 440 Hz + 880 Hz przy 16 kHz. Uruchom DFT. Potwierdź trzy piki w oczekiwanych przedziałach.
2. **Średni.** Nagraj 3-sekundowy plik WAV swojego głosu przy częstotliwości 48 kHz. Próbkuj w dół do 16 kHz za pomocą `torchaudio.transforms.Resample` (z antyaliasingiem), następnie do 16 kHz za pomocą naiwnego dziesiątkowania (co trzecia próbka). FFT oba. Gdzie pojawia się aliasing?
3. **Trudne.** Zbuduj STFT od zera, używając tylko `math` i DFT z kroku 3. Rozmiar ramki 400, przeskok 160, okno Hanna. Narysuj jasności za pomocą `matplotlib.pyplot.imshow`. To jest spektrogram z lekcji 02.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Częstotliwość próbkowania | Ile próbek na sekundę | Częstotliwość w Hz, przy której przetwornik ADC mierzy sygnał. |
| Nyquista | Maksymalna częstotliwość, jaką możesz reprezentować | `sr/2`; energia powyżej niego alias z powrotem w dół. |
| Głębia bitowa | Rozdzielczość każdej próbki | `int16` = 65 536 poziomów; `float32` = 24-bitowa precyzja w `[-1, 1]`. |
| DFT | Transformata Fouriera dla ciągów | `N` próbki → `N` złożone współczynniki częstotliwości. |
| FFT | Szybki DFT | Algorytm `O(N log N)` wymagający `N` = potęgi 2. |
| Kosz | Kolumna częstotliwości | `k · sr / N` Hz; rozdzielczość = `sr / N`. |
| STFT | Spektrogram pod maską | Oprawione + okienko FFT w czasie. |
| Aliasowanie | Dziwne duchy częstotliwości | Energia powyżej Nyquista odbijająca się w dół do dolnych pojemników. |

## Dalsze czytanie

- [Shannon (1949). Komunikacja w obecności hałasu](https://people.math.harvard.edu/~ctm/home/text/others/shannon/entropy/entropy.pdf) — artykuł dotyczący twierdzenia o próbkowaniu.
- [Smith — The Scientist and Engineer's Guide to Digital Signal Processing] (https://www.dspguide.com/ch8.htm) — bezpłatny, kanoniczny podręcznik DSP.
- [librosa docs — elementarz audio](https://librosa.org/doc/latest/tutorial.html) — praktyczny przewodnik z kodem.
– [Heinrich Kuttruff — Room Acoustics (wyd. 6)](https://www.routledge.com/Room-Acoustics/Kuttruff/p/book/9781482260434) — źródło informacji wyjaśniające, dlaczego dźwięk w świecie rzeczywistym nie jest czystą sinusoidą.
– [Steve Eddins — Notatnik interpretacji FFT](https://blogs.mathworks.com/steve/2020/03/30/fft-spectrum-and-spectral-densities/) — intuicja bin częstotliwości wyjaśniona w 10 minut.