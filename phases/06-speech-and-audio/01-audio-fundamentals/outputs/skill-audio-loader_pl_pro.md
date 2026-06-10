---

name: audio-loader
description: Zweryfikuj surowy plik audio pod kątem wymagań modelu docelowego i przeprowadź bezpieczny resampling (ponowne próbkowanie).
version: 1.0.0
phase: 6
lesson: 01
tags: [audio, speech, preprocessing]

---

Na podstawie parametrów wejściowych pliku audio (ścieżka, liczba kanałów, częstotliwość próbkowania, głębia bitowa, kodek) oraz wymagań modelu docelowego (ASR/TTS/klasyfikator o określonej częstotliwości próbkowania i liczbie kanałów) wygeneruj:

1. Niezgodności: wskaż każdy wymiar, w którym plik wejściowy nie pasuje do wymagań modelu (np. częstotliwość próbkowania, liczba kanałów, minimalny czas trwania, wykrycie przesterowania/clippingu).
2. Plan resamplingu: źródłowa i docelowa częstotliwość próbkowania, wybrane narzędzie (`torchaudio.transforms.Resample` lub `librosa.resample`) oraz typ filtru antyaliasingowego.
3. Konwersję kanałów: strategia miksowania do mono (np. uśrednianie kanałów lub pobranie tylko lewego kanału) albo przekazanie sygnału wielokanałowego, jeśli model go obsługuje.
4. Normalizację: normalizacja szczytowa (peak) vs RMS, docelowy poziom w dBFS oraz zabezpieczenie przed przesterowaniem (clipping).
5. Kod weryfikacyjny: fragment kodu w języku Python, który wczytuje plik, aplikuje transformacje i asertuje, że wynikowa tablica spełnia warunek `(target_sr, dtype, channel_count, range)`.

Odmawiaj wykonania downsamplingu (zmniejszenia częstotliwości próbkowania) bez użycia filtru antyaliasingowego. Odmawiaj upsamplingu (zwiększenia częstotliwości próbkowania) o współczynnik większy niż 2x bez użycia filtru rekonstrukcyjnego. Oznacz jako wadliwy każdy plik wejściowy, w którym występują piki przesterowania powyżej ±0,999 lub składowa stała (DC offset) przekracza ±0,01.
