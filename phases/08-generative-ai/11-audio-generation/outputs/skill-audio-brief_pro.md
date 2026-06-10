---

name: audio-brief
description: Przełóż krótki opis (brief) audio na wybór modelu, strukturę promptów oraz plan ewaluacji dla syntezy mowy (TTS), muzyki i efektów dźwiękowych (SFX).
version: 1.0.0
phase: 8
lesson: 11
tags: [audio, tts, music, sfx, codec]

---

Biorąc pod uwagę krótki opis (brief) audio (zadanie: TTS / muzyka / SFX / klonowanie głosu, czas trwania, styl, głos lub gatunek, ograniczenia licencyjne, praca w czasie rzeczywistym lub offline, wymagania jakościowe), wygeneruj:

1. Model + Hosting. ElevenLabs V3, OpenAI TTS, XTTS v2, Suno v4, Udio, Stable Audio 2.5, MusicGen 3.3B, AudioCraft 2 lub GPT-4o w trybie czasu rzeczywistego. Podaj jednozdaniowe uzasadnienie wyboru.
2. Format promptu. TTS: tekst wejściowy + próbka referencyjna głosu (3–10 sekund lub identyfikator głosu) + znaczniki emocji/tempa. Muzyka: gatunek + instrumentacja + nastrój + tempo (BPM) + znaczniki strukturalne (np. intro, refren). Efekty dźwiękowe (SFX): wyrażenia dźwiękonaśladowcze (onomatopeje) + źródło dźwięku + sugestie dotyczące czasu trwania.
3. Kodek + Generator + Wokoder. Wskaż konkretny kodek audio (np. Encodec 32 kHz, DAC 44 kHz, kodek autorski) oraz architekturę generatora (autoregresyjna na tokenach vs dopasowywanie przepływu - flow matching).
4. Ziarno (Seed) + Odtwarzalność. Wartość początkowa seed, wersja modelu (version pin), skrót promptu.
5. Ewaluacja. Metryka MOS (Mean Opinion Score) lub testy porównawcze A/B dla TTS, współczynnik CLAP dla muzyki, współczynnik błędów znakowych (CER) dla weryfikacji poprawności TTS, testy odsłuchowe dla SFX.
6. Filtry bezpieczeństwa (Guardrails). Weryfikacja zgody na klonowanie głosu + cyfrowy znak wodny (np. PerTh, SynthID-audio), skanowanie praw autorskich dla wygenerowanej muzyki, audyt licencyjny danych treningowych.

Odrzuć realizację klonowania głosu bez zweryfikowanej zgody jego właściciela (wykorzystanie próbki głosowej bez autoryzacji jest niedopuszczalne). Odrzuć projekty generowania muzyki z użyciem nielicencjonowanych utworów referencyjnych. Oznacz flagą ostrzegawczą wszelkie wymagania dotyczące czasu reakcji (latency) < 200 ms, które nie wykorzystują strumieniowych autoregresyjnych modeli tokenów – synteza audio oparta na modelach dyfuzyjnych nie jest w stanie osiągnąć czasu do pierwszego bajtu (TTFB) poniżej 300 ms w 2026 roku.
