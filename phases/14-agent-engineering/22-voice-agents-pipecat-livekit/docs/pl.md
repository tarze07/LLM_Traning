# Agenci głosowi: Pipecat i LiveKit

> Agenci głosowi będą w 2026 roku pierwszorzędną kategorią produkcyjną. Pipecat udostępnia potok oparty na ramkach Pythona (VAD → STT → LLM → TTS → transport). LiveKit Agents łączy modele AI z użytkownikami za pośrednictwem WebRTC. Docelowe opóźnienia produkcyjne wynoszą od początku do końca 450–600 ms w przypadku stosów premium.

**Typ:** Ucz się
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 14 · 01 (pętla agenta), faza 14 · 12 (wzorce przepływu pracy)
**Czas:** ~60 minut

## Cele nauczania

- Opisz potok oparty na ramkach Pipecat: DOWNSTREAM (źródło → ujście) i UPSTREAM (sterowanie).
- Nazwij kanoniczne etapy potoku głosowego i transportujące wsparcie Pipecat.
- Wyjaśnij dwie klasy agentów głosowych LiveKit Agents (MultimodalAgent, VoicePipelineAgent) i kiedy każda z nich pasuje.
- Podsumuj oczekiwania dotyczące opóźnień produkcyjnych w roku 2026 i ich wpływ na wybory dotyczące architektury.

## Problem

Agenci głosowi nie są pętlą tekstową z włączonym TTS. Budżety opóźnień są ogromne (~600 ms), częściowy dźwięk jest domyślny, wykrywanie skrętu jest modelem, a zakres transportu obejmuje telefonię SIP i WebRTC. Albo budujesz potok oparty na ramkach (Pipecat), albo opierasz się na platformie (LiveKit).

## Koncepcja

### Pipecat (pipecat-ai/pipecat)

- Framework potokowy oparty na ramkach Pythona.
- Łańcuch `Frame` → `FrameProcessor`.
- Dwa kierunki przepływu:
  - **DOWNSTREAM** — źródło → ujście (wejście audio, wyjście TTS).
  - **UPSTREAM** — informacje zwrotne i kontrola (anulowanie, wskaźniki, wtrącanie).
- `PipelineTask` zarządza cyklem życia ze zdarzeniami (`on_pipeline_started`, `on_pipeline_finished`, `on_idle_timeout`) i obserwatorami dla metryk/śledzenia/RTVI.

Typowy rurociąg:

```
VAD (Silero) → STT → LLM (context alternates user/assistant) → TTS → transport
```

Transporty: Daily, LiveKit, SmallWebRTCTransport, FastAPI WebSocket, WhatsApp.

Pipecat Flows dodaje ustrukturyzowane konwersacje (maszyny stanu). Pipecat Cloud to zarządzane środowisko wykonawcze.

### Agenci LiveKit (livekit/agenci)

- Łączy modele AI z użytkownikami za pośrednictwem WebRTC.
- Kluczowe pojęcia: `Agent`, `AgentSession`, `entrypoint`, `AgentServer`.
- Dwie klasy agentów głosowych:
  - **MultimodalAgent** — bezpośredni dźwięk poprzez OpenAI Realtime lub odpowiednik.
  - **VoicePipelineAgent** — kaskada STT → LLM → TTS; zapewnia kontrolę na poziomie tekstu.
- Semantyczne wykrywanie skrętu poprzez model transformatora.
- Natywna integracja MCP.
- Telefonia poprzez protokół SIP.
- Ponad 50 modeli bez kluczy API poprzez wnioskowanie LiveKit; Ponad 200 więcej dzięki wtyczkom.

### Platformy komercyjne

Vapi (~450–600 ms na zoptymalizowanym stosie premium) i Retell (~600 ms od końca do końca w 180 wywołaniach testowych) opierają się na nich. Wybierz platformę, jeśli potrzebujesz zarządzanego stosu głosu bez zespołu WebRTC.

### Gdzie ten wzorzec jest błędny

- **Zakaz obsługi barki.** Użytkownik przerywa; agent mówi dalej. Wymaga ramek anulowania UPSTREAM w Pipecat, odpowiednika w LiveKit.
- **Zignorowano pewność STT.** Transkrypcje o niskim stopniu pewności przekazywane do LLM jak ewangelia. Brama poufna lub żądanie potwierdzenia.
- **TTS odcięcie w połowie zdania.** Kiedy potok anuluje w połowie wypowiedzi, TTS musi poznać lub wyciąć dźwięk.
- **Ignorowany budżet opóźnień.** Każdy komponent dodaje 50–200 ms. Zsumuj swój łańcuch przed wysyłką.

### Typowe opóźnienia w roku 2026

- VAD: 20–60 ms
- Częściowy STT: 100–250 ms
- Pierwszy token LLM: 150–400 ms
- Pierwszy dźwięk TTS: 100–200 ms
- Transport RTT: 30–80 ms

Od końca do końca 450–600 ms to premium. Powszechne jest 800–1200 ms. Wszystko > 1500 ms wydaje się być uszkodzone.

## Zbuduj to

`code/main.py` to potok zabawek oparty na ramkach, oferujący:

- typy `Frame` (audio, transkrypcja, tekst, tts_audio, sterowanie).
- Interfejs `Processor` z `process(frame)`.
- Pięciostopniowy potok (VAD → STT → LLM → TTS → transport) jako procesory skryptowe.
- Ramka anulowania UPSTREAM w celu zademonstrowania wtargnięcia.

Uruchom to:

```
python3 code/main.py
```

Ślad pokazuje normalny przepływ i przerwanie wtrącenia, które zatrzymuje TTS w połowie wypowiedzi.

## Użyj tego

- **Pipecat** dla pełnej kontroli — niestandardowe procesory, pierwsi Python, dostawcy z możliwością podłączenia.
- **Agenci LiveKit** do wdrożeń opartych przede wszystkim na WebRTC i telefonii.
- **Vapi / Retell** dla hostowanych agentów głosowych bez zespołu WebRTC.
- **OpenAI Realtime / Gemini Live** do bezpośredniego wejścia/wyjścia audio (MultimodalAgent).

## Wyślij to

`outputs/skill-voice-pipeline.md` tworzy rusztowanie dla rurociągu głosowego w kształcie Pipecata z obsługą VAD + STT + LLM + TTS + transportem i obsługą barką.

## Ćwiczenia

1. Dodaj obserwatora metryk do swojego potoku zabawek: zliczaj klatki na etap na sekundę. Gdzie kumulują się opóźnienia?
2. Wdrożyj STT z bramką zaufania: poniżej progu zapytaj „czy możesz to powtórzyć?”
3. Dodaj semantyczną detekcję tury: prosta zasada — jeśli transkrypcja kończy się na „?”, koniec tury.
4. Przeczytaj dokumentację transportową Pipecat. Zamień transport stdlib na konfigurację SmallWebRTCTransport (odgałęzienie).
5. Zmierz kaskadę OpenAI Realtime vs STT+LLM+TTS w tym samym zapytaniu. Jakie koszty opóźnień niesie ze sobą kontrola na poziomie tekstu?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Rama | „Wydarzenie” | Wpisana jednostka danych w potoku (audio, transkrypcja, tekst, kontrola) |
| Procesor | „Etap rurociągu” | Procedura obsługi z procesem (ramką) |
| W DÓŁ | „Przepływ do przodu” | Źródło do zatonięcia: wejście audio, wyjście mowy |
| W GÓRĘ | „Przepływ informacji zwrotnej” | Kontrola: anulowanie, metryki, wtrącenie |
| VAD | „Wykrywanie aktywności głosowej” | Wykrywa, kiedy użytkownik mówi |
| Semantyczne wykrywanie skrętu | „Inteligentne zakończenie tury” | Decyzja oparta na modelu, że użytkownik ma już dość |
| Agent multimodalny | „Bezpośredni agent audio” | Wejście audio, wyjście audio; brak tekstu w środku |
| Agent VoicePipeline | „Agent kaskadowy” | STT + LLM + TTS; kontrola na poziomie tekstu |

## Dalsze czytanie

- [Dokumentacja Pipecat](https://docs.pipecat.ai/getting-started/introduction) — potok oparty na ramkach, procesory, transporty
- [Dokumentacja LiveKit Agents](https://docs.livekit.io/agents/) — WebRTC + elementy podstawowe głosowe
- [Vapi](https://vapi.ai/) — zarządzana platforma głosowa
- [Retell AI](https://www.retellai.com/) — zarządzany głos, test porównawczy opóźnień