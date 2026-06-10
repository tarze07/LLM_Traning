---

name: feature-extractor
description: Wybierz typ funkcji, liczbę mel, liczbę klatek/przeskoków i normalizację, aby dopasować je do modelu dźwięku przesyłanego dalej.
version: 1.0.0
phase: 6
lesson: 02
tags: [audio, features, spectrogram, mel]

---

Biorąc pod uwagę model docelowy (ASR / TTS / klasyfikator / głośnik / muzyka) i wejściowy dźwięk (częstotliwość próbkowania, domena), wynik:

1. Typ funkcji. Log-mel, mel, MFCC, surowy przebieg lub dyskretny kodek (EnCodec, SoundStream). Powód w jednym zdaniu.
2. Liczba meli i zakres częstotliwości. `n_mels`, `fmin`, `fmax`. Powód powiązany z domeną (mowa vs muzyka) i celem modelu.
3. Wykadruj i przeskocz. `frame_len`, `hop_len`, typ okna. Powód związany z wymaganą rozdzielczością czasową.
4. Normalizacja. Średnia/zmienna na wypowiedź, statystyki globalne lub dB ze stałym odniesieniem; przed lub po funkcji.
5. Fragment weryfikacyjny. Python, który wypisuje wynikowy kształt, min/max, średnia/std w 1-sekundowym klipie referencyjnym i potwierdza, że ​​pasują do treningu.

Odmów dostarczenia potoku funkcji, którego liczba klatek/przeskoków/mel odbiega od opublikowanej konfiguracji szkoleniowej modelu docelowego. Oznacz dowolną konfigurację opartą na MFCC dla Whisper lub Parakeet jako błędną — te modele zużywają log-mel. Oznacz dowolny ekstraktor funkcji bez asercji normalizacji.