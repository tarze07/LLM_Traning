---

name: realtime-voice-pipeline
description: Zaprojektuj potok głosowy w czasie rzeczywistym, określając transport sieciowy, bramkowanie VAD, strumieniowy ASR/STT, model LLM, strumieniowy TTS oraz orkiestrację w celu uzyskania docelowej latencji end-to-end.
version: 1.0.0
phase: 6
lesson: 11
tags: [voice-agent, livekit, pipecat, silero, streaming, latency]

---

Na podstawie zadanego celu (wymagana latencja P50/P95, obsługiwane języki, kanał transmisji, infrastruktura lokalna vs. chmura, wolumen połączeń), określ:

1. Transport sieciowy: WebRTC (LiveKit / Daily) · WebSocket · SIP Trunking (Twilio / Telnyx). Uzasadnij wybór pod kątem odporności na jitter oraz scenariusza użycia.
2. Bramkowanie VAD i detekcja tur (turn-taking): Silero VAD (rozwiązanie open-source, 99.5% TPR) · Cobra (komercyjne) · detektor tur LiveKit. Określ próg czułości, minimalny czas trwania mowy, oraz czas podtrzymania (hangover).
3. Strumieniowy STT/ASR: Parakeet-TDT (najszybsze rozwiązanie open-source) · Kyutai STT (z techniką wymuszonego opróżniania bufora - flushing) · Deepgram Nova-3 (API, ~150 ms latencji) · Whisper-Streaming. Uzasadnij wybór.
4. Model LLM i strumieniowanie: Sposób buforowania pierwszych 20 tokenów przed przekazaniem do modelu TTS. Wybrany model, konfiguracja parametrów strumieniowania oraz zabezpieczenia przed atakami typu Prompt Injection.
5. Strumieniowy TTS: Kokoro-82M (~100 ms TTFA - Time-to-First-Audio) · Orpheus · Cartesia Sonic · ElevenLabs Turbo. Wskaż profil głosu referencyjnego oraz zabezpieczenia przed nieautoryzowanym klonowaniem (zgodnie z lekcją 8).
6. Orkiestrację: LiveKit Agents · Pipecat · Vapi · Retell · autorskie rozwiązanie w języku Rust. Uzasadnij wybór pod kątem kompetencji zespołu oraz skali wdrożenia.
7. Monitorowanie i metryki (Observability): Histogramy latencji P50/P95/P99 dla każdego etapu; wskaźnik fałszywych przerw (false interruption rate); współczynnik utraconych połączeń (packet loss / call drop rate); wskaźnik WER na próbkach testowych z rzeczywistych połączeń.

Zasady weryfikacji:
- Odrzuć projekty, które buforują całe wypowiedzi przed przekazaniem ich do modułu STT (wymagaj przetwarzania strumieniowego).
- Odrzuć modele TTS, które nie wspierają strumieniowego generowania audio (streaming).
- Odrzuć plany ewaluacji bazujące wyłącznie na średnim opóźnieniu (mean latency) – bezwzględnie wymagaj analizy percentyla P95.
- Odrzuć plany korzystania z platform zarządzanych (np. Vapi, Retell) przy wolumenach przekraczających 100 000 minut miesięcznie, jeśli nie przeprowadzono analizy porównawczej kosztów w stosunku do wdrożenia własnej infrastruktury.

Przykładowe dane wejściowe: „Głosowy agent AI do kalkulacji składek ubezpieczeń komunikacyjnych. Latencja < 500 ms P95. Język angielski (USA). Wolumen: 50 000 minut tygodniowo. Zgodność: HIPAA (brak danych osobowych w logach).”

Przykładowy wynik:
- Transport: LiveKit Agents + Twilio SIP. Rozwiązanie sprawdzone produkcyjnie na dużą skalę, z pełnym wsparciem dla zgodności z HIPAA (możliwość wyłączenia zapisu danych).
- VAD: Silero VAD z progiem czułości 0.45, minimalny czas mowy 220 ms, czas podtrzymania ciszy (hangover) 400 ms. Dodatkowy detektor tur z biblioteki LiveKit.
- STT: Deepgram Nova-3 w wersji dla języka angielskiego (~150 ms P95); rozwiązanie zapasowe (fallback): Parakeet-TDT w przypadku konieczności przejścia na infrastrukturę lokalną.
- LLM: Strumieniowy model GPT-4o uruchamiany przez OpenAI Realtime API; filtr wyjściowy chroniący przed wstrzykiwaniem promptów; buforowanie pierwszych 20 tokenów przed uruchomieniem potoku TTS.
- TTS: Cartesia Sonic 2 (~150 ms TTFA, gotowy profil głosu bez klonowania).
- Orkiestracja: LiveKit Agents. Monitorowanie i analiza jakości rozmów za pomocą platformy Hamming AI.
- Logowanie: Filtrowanie danych wrażliwych (numery kart, PESEL/SSN, daty urodzenia) przy użyciu wyrażeń regularnych oraz modeli NER (Named Entity Recognition) przed zapisem do bazy. Czas przechowywania logów ograniczony do 30 dni.
