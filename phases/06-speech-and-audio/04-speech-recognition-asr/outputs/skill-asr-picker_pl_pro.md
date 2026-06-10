---

name: asr-picker
description: Dobierz model ASR, strategię dekodowania, podział na fragmenty oraz integrację z modelem językowym (LM fusion) dla zadanego scenariusza wdrożeniowego.
version: 1.0.0
phase: 6
lesson: 04
tags: [audio, asr, speech-recognition]

---

Na podstawie zadanego scenariusza wdrożeniowego (obsługiwane języki, domena, budżet opóźnień/latencji, platforma sprzętowa, tryb offline/strumieniowy, typowy czas trwania nagrań), określ:

1. Model: Whisper-large-v3-turbo / Parakeet-TDT / Canary-Flash / wav2vec 2.0 / Moonshine. Podaj jednozdaniowe uzasadnienie wyboru.
2. Strategię dekodowania: Zachłanne (greedy) / poszukiwanie wiązkowe (beam search) / próbkowanie z temperaturą / wagi fuzji LM. Uzasadnij wybór pod kątem dostępnego budżetu obliczeniowego i wymagań jakościowych.
3. Podział na fragmenty (chunking) i VAD: Maksymalna długość fragmentu, rozmiar kroku (overlap/stride), oraz to, czy stosowane będzie bramkowanie z użyciem zewnętrznego VAD (np. Silero-VAD), czy też mechanizmu wbudowanego w model Whisper.
4. Politykę językową: Wymuszenie konkretnego języka (forced language) vs. automatyczna detekcja języka (auto-LID); sposób obsługi wypowiedzi wielojęzycznych (code-switching).
5. Plan ewaluacyjny: Sposób obliczania wskaźnika WER na zbiorze testowym z danej domeny, weryfikację reprezentatywności mówców (speaker coverage) oraz częstotliwość występowania halucynacji na fragmentach zawierających wyłącznie ciszę.

Zasady weryfikacji:
- Odrzuć projekty wdrożenia modelu Whisper na długich nagraniach bez zastosowania bramkowania VAD (ryzyko generowania halucynacji w momentach ciszy).
- Odrzuć wszelkie raporty WER, w których nie zastosowano normalizacji tekstu przed porównaniem (np. sprowadzenie do małych liter, usunięcie znaków interpunkcyjnych).
- Oznacz jako błąd konfiguracje poszukiwania wiązkowego o szerokości wiązki (beam width) większej niż 16 bez użycia zewnętrznego modelu językowego (LM) – samo zwiększanie szerokości wiązki na surowych logitach wyjściowych (np. dla CTC) nie przynosi istotnej poprawy.
