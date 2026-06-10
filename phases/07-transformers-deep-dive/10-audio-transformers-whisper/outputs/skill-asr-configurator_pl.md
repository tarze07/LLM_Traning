---

name: asr-configurator
description: Wybierz model ASR (wariant Whisper / Moonshine / szybszy szept) i parametry dekodowania dla nowego potoku mowy.
version: 1.0.0
phase: 7
lesson: 10
tags: [transformers, whisper, asr, speech]

---

Biorąc pod uwagę zadanie mowy (transkrypcja / tłumaczenie / przesyłanie strumieniowe / na urządzeniu), język(i), charakterystykę dźwięku (szum, akcent, czas trwania) i docelowe opóźnienia/jakość, wynik:

1. Wybór modelu. Jeden z: szybszy szept duży-v3-turbo (produkcja domyślna), szept duży-v3 (najwyższa jakość, wielojęzyczność), szept średni (średni poziom), baza Moonshine (edge), destil-whisper (2x szybszy angielski). Powód w jednym zdaniu.
2. Kwantyzacja. int8_float16 (domyślnie CPU), float16 (domyślnie GPU), fp32 (badania). Flaga wpływu na pamięć VRAM.
3. Dekodowanie. Szerokość wiązki (5 typowo, 1 do przesyłania strumieniowego), harmonogram obniżania temperatury, próg log-prob, próg braku mowy, włączanie/wyłączanie bramki VAD.
4. Kawałki. Stałe okno 30 s w porównaniu z fragmentami strumieniowymi (zwykle 10 s z nałożeniem 2 s) + segmentacja oparta na VAD. Udokumentuj strategię po połączeniu w przypadku nakładania się.
5. Obróbka końcowa. Wyrównanie znacznika czasu (wymuszone wyrównanie WhisperX), przywracanie interpunkcji, diaryzacja (pyannote). Flagi wymagane przez zadanie.

Odmów polecania zwykłego OpenAI Whisper (implementacja referencyjna) do produkcji — `faster-whisper` jest 4 razy szybszy i ma identyczne wyniki. Odmów przesyłania strumieniowego ASR bez VAD, chyba że zostanie udokumentowany powód. Oznacz wszelkie założenia dotyczące jednego głośnika, jeśli na wejściu prawdopodobnie znajduje się wiele głośników.