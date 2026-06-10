---

name: voice-pipeline
description: Stwórz szkielet potoku głosowego w stylu frameworka Pipecat (VAD + STT + LLM + TTS + transport) z obsługą przerywania wypowiedzi (barge-in), bramkowaniem pewności STT i egzekwowaniem budżetu opóźnień.
version: 1.0.0
phase: 14
lesson: 22
tags: [voice, pipecat, livekit, webrtc, latency]

---

Na podstawie specyfikacji productu głosowego (język, protokół transportowy, dostawcy modeli) utwórz potok przetwarzania oparty na ramkach.

Wyprodukuj:

1. Klasę `Frame` zawierającą pola `kind` (typ), `payload` (ładunek) oraz `direction` (kierunek przepływu: downstream/upstream).
2. Niezależne procesory: `VAD`, `STT`, `LLM`, `TTS` oraz `Transport` – każdy implementujący metodę `process(frame)`.
3. Funkcję pomocniczą `link()` łączącą procesory w łańcuch przepływu w przód i w tył.
4. Obsługę ramek anulowania: mechanizm przepływu UPSTREAM z warstwy transportowej do TTS oraz z LLM do STT, powodujący natychmiastowe porzucanie kolejkowanych zadań na każdym etapie.
5. Moduł obserwatorów mierzący opóźnienia na każdym etapie – generuje on spany OpenTelemetry (OTel) dla każdej ramki przechodzącej przez dany procesor (Lekcja 23).
6. Bramkę pewności w STT: w przypadku spadku pewności rozpoznania poniżej określonego progu, zamiast wątpliwej transkrypcji generowana jest ramka z prośbą o powtórzenie („Proszę powtórzyć”).

Kategoryczne odrzucenia (Twarde kryteria):

- Brak obsługi przepływu komunikatów w górę (UPSTREAM). Przerywanie wypowiedzi przez użytkownika (barge-in) jest kluczowym wymaganiem w komunikacji głosowej.
- Wykonywanie połączeń do LLM bez włączonego przesyłania strumieniowego (streaming). Czas oczekiwania na pierwszy token generuje zbyt duże opóźnienia – odpowiedzi muszą być strumieniowane.
- Brak weryfikacji współczynnika pewności STT (confidence score). Przekazywanie błędnie rozpoznanego tekstu do LLM prowadzi bezpośrednio do generowania niepoprawnych odpowiedzi.

Zasady odmowy wykonania usługi (Refusal rules):

- Jeśli opóźnienie end-to-end w warunkach testowych przekracza 1500 ms, odmów wdrożenia. Zoptymalizuj łańcuch przetwarzania lub skorzystaj z bezpośredniej integracji audio za pomocą `MultimodalAgent`.
- Jeśli produkt jest przeznaczony przede wszystkim dla telefonii, a potok nie posiada zintegrowanego adaptera SIP, odmów. Zarekomenduj routing przez LiveKit SIP lub skorzystanie z zarządzanej platformy (Vapi/Retell).
- Jeśli w warstwie transportowej strumienie audio zawierające dane wrażliwe lub umożliwiające identyfikację osób (PII) są przesyłane bez szyfrowania, odmów.

Pliki wynikowe: `frames.py`, `processors.py`, `pipeline.py`, `observers.py`, `README.md` wyjaśniające budżet opóźnień, architekturę przerywania wypowiedzi (barge-in) oraz dobór protokołu transportowego. Zakończ sekcją „Dalsza lektura”, wskazując na Lekcję 23 (konfiguracja i propagacja spanów OTel), Lekcję 24 (systemy obserwowalności i telemetrii) lub oficjalną dokumentację LiveKit w celu pogłębienia wiedzy o WebRTC.
