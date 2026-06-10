---

name: whisper-tuner
description: Zaprojektuj kompletny potok dostrajania (finetuning) lub wnioskowania (inference) modelu Whisper dla wybranego języka, domeny oraz budżetu opóźnień.
version: 1.0.0
phase: 6
lesson: 05
tags: [audio, whisper, asr, fine-tuning, lora]

---

Na podstawie zadanego celu (obsługiwane języki, domena, rozkład długości nagrań, budżet opóźnień, platforma sprzętowa) oraz danych (liczba godzin nagrań, jakość etykiet), określ:

1. Wariant modelu: Tiny / Base / Small / Medium / Large-v3 / Turbo. Uzasadnij wybór.
2. Środowisko uruchomieniowe (runtime): Hugging Face (vanilla) / faster-whisper / WhisperX / Whisper-Streaming. Uzasadnij wybór.
3. Strategię dostrajania: Pełny finetuning (Full FT) vs. LoRA (parametry r, target_modules), zasady zamrażania warstw enkodera, liczba epok.
4. Zabezpieczenia procesu wnioskowania (inference guards): Bramkowanie VAD (Silero VAD lub wbudowane w Whisper), parametry `temperature=0.0`, `condition_on_previous_text=False`, `no_speech_threshold`.
5. Ewaluację: Docelowy wskaźnik WER dla danej domeny, reguły normalizacji tekstu, monitorowanie wskaźnika halucynacji na fragmentach ciszy.

Zasady weryfikacji:
- Odrzuć projekty wdrożenia modelu Whisper na nagraniach audio bez zastosowania bramkowania VAD.
- Odrzuć konfiguracje ustawiające `condition_on_previous_text=True` dla zadań przetwarzania wieloczęściowego (multi-chunk) bez wprowadzenia mechanizmów zapobiegających zapętleniom i halucynacjom.
- Oznacz jako błąd każdą procedurę dostrajania, która podmienia oryginalny tokenizer lub wbudowany potok ekstrakcji cech log-mel modelu Whisper.
