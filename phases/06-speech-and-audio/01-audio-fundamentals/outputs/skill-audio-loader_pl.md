---

name: audio-loader
description: Zweryfikuj surowy plik audio pod kątem oczekiwań modelu docelowego i bezpiecznie go ponownie próbkuj.
version: 1.0.0
phase: 6
lesson: 01
tags: [audio, speech, preprocessing]

---

Biorąc pod uwagę plik audio (ścieżkę, kanały, częstotliwość próbkowania, głębię bitową, kodek) i model docelowy (ASR/TTS/klasyfikator z wymaganą częstotliwością próbkowania i liczbą kanałów), wynik:

1. Niedopasowania. Wymień każdy wymiar, w którym plik nie pasuje do celu (sr, kanały, minimalny czas trwania, kontrola obcinania).
2. Plan ponownego próbkowania. Source sr, target sr, biblioteka resamplingu (`torchaudio.transforms.Resample` lub `librosa.resample`), typ filtra antyaliasingowego.
3. Plan kanałów. Strategia pojedynczego składania (średnia lub tylko lewa) lub przekazywanie wielokanałowe, jeśli model to obsługuje.
4. Normalizacja. Normalizacja wartości szczytowej vs RMS, wartość docelowa dBFS, ochrona przed przecięciem.
5. Fragment weryfikacyjny. Python, który ładuje plik, uruchamia transformacje i potwierdza, że ​​ostateczna tablica pasuje do `(target_sr, dtype, channel_count, range)`.

Odmawiaj próbkowania w dół bez filtra antyaliasingowego. Odmawiaj próbkowania powyżej 2x bez filtra rekonstrukcyjnego. Oznacz dowolny plik wejściowy z pikami obcinania powyżej ± 0,999 lub przesunięciem DC powyżej ± 0,01.