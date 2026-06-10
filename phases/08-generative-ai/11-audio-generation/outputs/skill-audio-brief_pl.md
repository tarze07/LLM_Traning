---

name: audio-brief
description: Przetłumacz brief audio na model + podpowiedzi + plan oceny w zakresie TTS, muzyki i efektów dźwiękowych.
version: 1.0.0
phase: 8
lesson: 11
tags: [audio, tts, music, sfx, codec]

---

Biorąc pod uwagę brief audio (zadanie: TTS / muzyka / SFX / klon głosu, czas trwania, styl, głos lub gatunek, ograniczenia licencyjne, czas rzeczywisty lub offline, pasek jakości), wynik:

1. Modelka + hosting. ElevenLabs V3, OpenAI TTS, XTTS v2, Suno v4, Udio, Stable Audio 2.5, MusicGen 3.3B, AudioCraft 2 lub GPT-4o w czasie rzeczywistym. Powód w jednym zdaniu.
2. Format podpowiedzi. TTS: tekst + komunikat głosowy (próbka 3–10 s lub identyfikator głosu) + znaczniki emocji/tempa. Muzyka: gatunek + instrumentacja + nastrój + BPM + znaczniki strukturalne. Efekty dźwiękowe: onomatopeja + źródło + wskazówka dotycząca czasu trwania.
3. Kodek + generator + łańcuch wokodera. Nazwij konkretny kodek (Encodec 32 kHz, DAC 44 kHz, niestandardowy) i wybór generatora (token-AR vs dopasowanie przepływu).
4. Ziarno + odtwarzalność. Pin początkowy, pin wersji, skrót podpowiedzi.
5. Ewaluacja. MOS (średni wynik opinii) lub A/B dla TTS, wynik CLAP dla muzyki, CER dla transkrypcji TTS, test słuchania użytkownika dla SFX.
6. Poręcze. Zgoda na klonowanie głosu + znak wodny (PerTh / SynthID-audio), skanowanie praw autorskich do wyjścia muzycznego, sprawdzenie zasad dotyczących danych szkoleniowych.

Odmawiaj klonowania jakiegokolwiek głosu bez zweryfikowanej zgody właściciela („3-sekundowy monit” z czasów kasety nie jest zgodą). Odmawiaj przesyłania muzyki z nielicencjonowanymi materiałami referencyjnymi. Oznacz dowolny cel w czasie rzeczywistym &lt; 200 ms bez użycia modelu AR z tokenem przesyłania strumieniowego – dźwięk oparty na dyfuzji nie może osiągnąć TTFB poniżej 300 ms w 2026 r.