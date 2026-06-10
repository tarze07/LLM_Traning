---

name: whisper-tuner
description: Zaprojektuj potok dostrajania lub wnioskowania Whisper dla danego języka, domeny i budżetu opóźnień.
version: 1.0.0
phase: 6
lesson: 05
tags: [audio, whisper, asr, fine-tuning, lora]

---

Biorąc pod uwagę cel (zestaw języków, domenę, rozkład długości klipów, budżet opóźnień, sprzęt) i dane (dostępne godziny, jakość), wynik:

1. Wariant. Mały / Podstawowy / Mały / Średni / Duży-v3 / Turbo. Powód.
2. Czas działania. waniliowy / szybszy szept / szeptx / przesyłanie strumieniowe szeptem. Powód.
3. Dostosuj plan. Full-FT vs LoRA (r, target_modules), zasady blokowania kodera, liczba epok.
4. Strażnicy wnioskowania. VAD (własność Silero lub Whisper), `temperature=0`, `condition_on_previous_text=False`, `no_speech_threshold`.
5. Ocena. Cel domeny WER, zasady normalizacji tekstu, kontrola częstości halucynacji w klipach ciszy.

Odmów wdrożenia Whisper na dowolnym audio bez VAD. Odmawiaj ustawiania `condition_on_previous_text=True` dla zadań wieloczęściowych bez niekontrolowanej ucieczki. Oznacz dowolne dostrojenie, które zamienia tokenizer lub potok Mel firmy Whisper.