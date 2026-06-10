---

name: asr-configurator
description: Dobierz model ASR (warianty Whisper, Moonshine, faster-whisper) oraz parametry dekodowania dla systemu transkrypcji mowy.
version: 1.0.0
phase: 7
lesson: 10
tags: [transformers, whisper, asr, speech]

---

Na podstawie opisu zadania przetwarzania mowy (transkrypcja / tłumaczenie / streaming / działanie na urządzeniu końcowym), języków, charakterystyki dźwięku (szum, akcent, czas nagrania) oraz oczekiwanego poziomu opóźnienia i jakości wygeneruj:

1. Wybór modelu: jeden z modeli: `faster-whisper large-v3-turbo` (rekomendowany domyślnie na produkcję), `Whisper-large-v3` (najwyższa jakość, obsługa wielu języków), `Whisper-medium`, `Moonshine-base` (dla urządzeń edge/brzegowych) lub `distil-whisper` (dwukrotnie szybszy dla języka angielskiego). Podaj uzasadnienie w jednym zdaniu.
2. Kwantyzacja: int8_float16 (domyślnie dla CPU), float16 (domyślnie dla GPU) lub fp32 (zastosowania badawcze). Podaj wpływ na zużycie pamięci VRAM.
3. Parametry dekodowania: szerokość wiązki (beam width - typowo 5, lub 1 dla streamingu), harmonogram obniżania temperatury (temperature fallback schedule), próg log-probability, próg wykrywania ciszy (no-speech threshold), włączenie/wyłączenie detektora aktywności głosowej (VAD).
4. Podział na segmenty (chunking): stałe okna 30-sekundowe vs fragmenty przesyłane strumieniowo (np. 10 s z 2-sekundowym nakładaniem się) + segmentacja oparta na VAD. Opisz strategię łączenia wyników w przypadku nakładających się segmentów.
5. Postprocessing (obróbka końcowa): precyzyjne dopasowanie znaczników czasu (forced alignment za pomocą WhisperX), rekonstrukcja interpunkcji, diaryzacja mówców (np. za pomocą pyannote-audio). Wskaż komponenty wymagane przez zadanie.

Odmawiaj rekomendowania oryginalnej biblioteki OpenAI Whisper (implementacji referencyjnej) w systemach produkcyjnych – `faster-whisper` jest do 4 razy szybszy i daje identyczne wyniki transkrypcji. Odmawiaj wdrażania streamingu ASR bez użycia detektora VAD, chyba że podano wyraźne uzasadnienie. Oznacz jako błąd każde założenie o obecności tylko jednego mówcy (single-speaker assumption), jeśli sygnał wejściowy prawdopodobnie zawiera wypowiedzi wielu osób.
