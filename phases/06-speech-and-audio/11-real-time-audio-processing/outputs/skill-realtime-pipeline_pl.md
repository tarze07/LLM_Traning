---

name: realtime-voice-pipeline
description: Wybierz transport, VAD, przesyłanie strumieniowe STT, LLM, przesyłanie strumieniowe TTS i orkiestrację, aby uzyskać docelowe opóźnienie od końca do końca.
version: 1.0.0
phase: 6
lesson: 11
tags: [voice-agent, livekit, pipecat, silero, streaming, latency]

---

Biorąc pod uwagę cel (opóźnienie P50/P95, język, kanał, tryb offline vs chmura, głośność połączeń), wynik:

1. Transport. WebRTC (LiveKit / Daily) · WebSocket · SIP trunking (Twilio / Telnyx). Powód związany z tolerancją jittera + przypadek użycia.
2. VAD + wykonywanie tur. Silero VAD (otwarty, 99,5% TPR) · Cobra (komercyjny) · Detektor skrętu LiveKit. Próg, minimalny czas trwania mowy, kac ciszy.
3. Przesyłanie strumieniowe STT. Parakeet TDT (najszybsze otwarcie) · Kyutai STT (ze sztuczką spłukiwania) · Deepgram Nova-3 (API, ~150 ms) · Przesyłanie strumieniowe szeptem. Powód.
4. LLM + streaming. Przypnij pierwsze 20 tokenów, zanim uruchomi się TTS. Model + konfiguracja przesyłania strumieniowego + poręcze umożliwiające natychmiastowe wstrzyknięcie.
5. Przesyłanie strumieniowe TTS. Kokoro-82M (~100 ms TTFA) · Orfeusz · Cartesia Sonic · ElevenLabs Turbo. Pakiet głosowy lub strażnik klonujący (Lekcja 8).
6. Orkiestracja. Agenci LiveKit · Pipecat · Vapi · Retell · niestandardowy rdza. Powód związany z umiejętnościami zespołowymi + skala.
7. Obserwowalność. Histogramy P50/P95/P99 według stopnia; wskaźnik fałszywie dodatnich przerw; współczynnik odrzuceń połączeń; WER na próbkach połączeń.

Odmowa wdraża buforowanie całych wypowiedzi przed STT. Odrzuć TTS, który nie przesyła strumieniowo. Odmów oceny według średniego opóźnienia — wymagaj P95. Odrzuć platformy zarządzane (Vapi / Retell) dla &gt; 100 tys. minut miesięcznie bez porównania kosztów w przypadku samodzielnego zbudowania.

Przykładowe wejście: „Agent głosowy do wyceny ubezpieczenia samochodu. &lt; 500 ms P95. Angielski, USA. 50 tys. minut/tydzień. Zgodność: zgodne z HIPAA (brak danych osobowych w logach).”

Przykładowe wyjście:
- Transport: agenci LiveKit + Twilio SIP. Sprawdzone w skali call center, możliwość wyboru w trybie HIPAA.
- VAD: Silero VAD @ próg 0,45, min. mowa 220 ms, zawieszenie ciszy 400 ms. Nakładka na czujnik skrętu LiveKit.
- STT: Deepgram Nova-3 angielski (~150 ms P95); powrót do Parakeet-TDT, jeśli wymagany jest audyt lokalny.
- LLM: przesyłanie strumieniowe GPT-4o poprzez API czasu rzeczywistego OpenAI; strzeż się przed szybkim wtryskiem za pomocą filtra końcowego; przypnij pierwsze 20 tokenów do TTS.
- TTS: Cartesia Sonic 2 (~150 ms TTFA, klonowanie głosu nie jest używane — głos predefiniowany).
- Orkiestracja: agenci LiveKit. Obserwowalność za pomocą Hamming AI na potrzeby produkcji.
- Dzienniki: usuń CVV / SSN / DOB za pomocą wyrażenia regularnego + przejścia NER przed utrwaleniem. Zachowaj 30 dni.