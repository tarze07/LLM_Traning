---

name: voice-pipeline
description: Stwórz szkielet potoku głosowego w kształcie Pipecata (VAD + STT + LLM + TTS + transport) z wtrącaniem się, bramkowaniem zaufania i egzekwowaniem budżetu opóźnień.
version: 1.0.0
phase: 14
lesson: 22
tags: [voice, pipecat, livekit, webrtc, latency]

---

Biorąc pod uwagę specyfikację produktu głosowego (język, transport, dostawcy), utwórz potok oparty na ramkach.

Wyprodukuj:

1. Typ `Frame` z `kind`, `payload`, `direction` (downstream/upstream).
2. Procesory: `VAD`, `STT`, `LLM`, `TTS`, `Transport`. Każdy z `process(frame)`.
3. Pomocnik `link()` łączący procesory w przód i w tył.
4. Anuluj obsługę ramek: ścieżka UPSTREAM z transportu do TTS, LLM do STT, porzucając oczekujące prace na każdym etapie.
5. Obserwatorzy: metryki opóźnień na każdym etapie; emitują okres Otel na ramkę przechodzącą przez procesor (Lekcja 23).
6. Bramka zaufania w STT: poniżej progu zamiast transkrypcji wyemituj ramkę tekstową „proszę powtórzyć”.

Twarde odrzucenia:

- Rurociąg bez obsługi GÓRNEJ. Wtrącanie się nie jest opcjonalne w przypadku głosu.
- Połączenia LLM bez przesyłania strumieniowego. Dominuje opóźnienie pierwszego tokena; musi być transmitowany.
- STT ślepe na pewność siebie. Podawanie błędnych transkrypcji do LLM skutkuje błędnymi odpowiedziami.

Zasady odmowy:

- Jeśli opóźnienie od końca do końca przekracza 1500 ms w trybie zimnego działania, odmów wysyłki. Zoptymalizuj łańcuch lub użyj MultimodalAgent (Direct-audio LiveKit).
- Jeśli produkt jest przeznaczony przede wszystkim dla telefonii, a rurociąg nie ma adaptera SIP, odmów. Trasuj przez LiveKit SIP lub platformę (Vapi/Retell).
- Jeśli podczas transportu produkt zawiera dźwięk pozwalający na identyfikację osób bez szyfrowania, odmów.

Dane wyjściowe: `frames.py`, `processors.py`, `pipeline.py`, `observers.py`, `README.md` wyjaśniające budżet opóźnień, projekt barki i wybór transportu. Zakończ słowami „co dalej czytać”, wskazując Lekcję 23 (OTel), Lekcję 24 (backendy umożliwiające obserwację) lub dokumentację LiveKit zawierającą szczegółowe informacje dotyczące WebRTC.