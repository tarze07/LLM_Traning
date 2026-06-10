---

name: feature-extractor
description: Dobierz typ cech, liczbę filtrów melowych (n_mels), rozmiar okna/kroku (frame/hop length) oraz metodę normalizacji, aby dopasować je do wymagań docelowego modelu audio.
version: 1.0.0
phase: 6
lesson: 02
tags: [audio, features, spectrogram, mel]

---

Na podstawie modelu docelowego (ASR / TTS / klasyfikator / rozpoznawanie mówcy / muzyka) oraz wejściowego sygnału audio (częstotliwość próbkowania, domena), określ:

1. Typ cech: Log-mel, mel, MFCC, surowy przebieg fali (raw waveform) lub dyskretny kodek (EnCodec, SoundStream). Podaj jednozdaniowe uzasadnienie wyboru.
2. Liczbę filtrów melowych i zakres częstotliwości: `n_mels`, `fmin`, `fmax`. Uzasadnij wybór w oparciu o domenę (mowa vs. muzyka) oraz przeznaczenie modelu.
3. Parametry okna i kroku: `frame_len`, `hop_len` oraz typ okna. Uzasadnij wybór pod kątem wymaganej rozdzielczości czasowej.
4. Normalizację: Standaryzacja (średnia/wariancja) dla pojedynczej wypowiedzi, statystyki globalne lub skala dB ze stałym punktem odniesienia; określ, czy normalizacja zachodzi przed, czy po ekstrakcji cech.
5. Kod weryfikacyjny: Skrypt w języku Python, który wypisuje wynikowy kształt (shape), wartości min/max oraz średnią i odchylenie standardowe dla 1-sekundowego referencyjnego klipu audio, potwierdzając ich zgodność z konfiguracją treningową.

Odrzuć potok ekstrakcji cech, którego parametry okna, kroku lub liczby filtrów melowych odbiegają od oficjalnej konfiguracji treningowej modelu docelowego. Oznacz jako błędną każdą konfigurację opartą na MFCC przeznaczoną dla modeli Whisper lub Parakeet – modele te wymagają spektrogramów log-mel. Oznacz jako błędny każdy ekstraktor cech, który nie zawiera asercji weryfikujących normalizację.
