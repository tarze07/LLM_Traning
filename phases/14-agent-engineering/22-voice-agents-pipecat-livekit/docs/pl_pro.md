# Agenci głosowi: Pipecat i LiveKit

> Agenci głosowi (voice agents) stają się jedną z najważniejszych kategorii wdrożeń produkcyjnych. Framework Pipecat oferuje oparty na ramkach (frame-based) potok przetwarzania w Pythonie (VAD → STT → LLM → TTS → transport). LiveKit Agents łączy modele sztucznej inteligencji z użytkownikami za pomocą protokołu WebRTC. Docelowe opóźnienie w systemach produkcyjnych klasy premium (end-to-end latency) wynosi od 450 do 600 ms.

**Typ:** Ucz się
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 14 · 01 (pętla agenta), faza 14 · 12 (wzorce przepływu pracy)
**Czas:** ~60 minut

## Cele nauczania

- Opisać architekturę potoku Pipecat opartego na ramkach: przepływ danych w dół (DOWNSTREAM: od źródła do odbiornika/ujścia) oraz w górę (UPSTREAM: komunikaty sterujące).
- Wymienić kanoniczne etapy potoku głosowego oraz protokoły transportowe obsługiwane przez Pipecat.
- Wyjaśnić różnicę między dwoma klasami agentów w LiveKit (MultimodalAgent oraz VoicePipelineAgent) i wskazać kryteria ich wyboru.
- Podsumować standardy opóźnień produkcyjnych oraz ich wpływ na decyzje architektoniczne.

## Problem

Projektowanie agentów głosowych to znacznie więcej niż połączenie pętli tekstowej z syntezatorem mowy (TTS). Wymagania dotyczące opóźnień są niezwykle rygorystyczne (budżet rzędu ~600 ms), domyślnie przetwarza się strumienie audio (streaming), wykrywanie końca wypowiedzi (turn detection) opiera się na modelach uczenia maszynowego, a warstwa transportowa musi obsługiwać protokoły SIP oraz WebRTC. Rozwiązaniem jest budowa własnego potoku opartego na ramkach (Pipecat) lub wykorzystanie gotowej platformy (LiveKit).

## Koncepcja

### Pipecat (pipecat-ai/pipecat)

- Framework w Pythonie dedykowany do budowy potoków przetwarzania audio i wideo opartych na ramkach.
- Przepływ danych oparty na łańcuchu: ramka (`Frame`) → procesor ramki (`FrameProcessor`).
- Obsługa dwóch kierunków przepływu:
  - **DOWNSTREAM** – przepływ od źródła do ujścia (od wejścia audio do wyjściowej syntezy TTS).
  - **UPSTREAM** – przepływ komunikatów sterujących i zwrotnych (anulowanie wypowiedzi agenta, metryki, przerywanie przez użytkownika).
- Klasa `PipelineTask` odpowiada za cykl życia potoku, obsługując zdarzenia (np. `on_pipeline_started`, `on_pipeline_finished`, `on_idle_timeout`) oraz obserwatorów telemetrii, metryk i protokołu RTVI.

Typowy potok (pipeline):

```
VAD (Silero) → STT → LLM (z naprzemiennym kontekstem użytkownik/asystent) → TTS → transport
```

Obsługiwane protokoły transportowe: Daily, LiveKit, SmallWebRTCTransport, FastAPI WebSocket, WhatsApp.

Pipecat Flows wprowadza obsługę ustrukturyzowanych konwersacji (opartych na maszynie stanów), natomiast Pipecat Cloud oferuje zarządzane środowisko uruchomieniowe.

### LiveKit Agents

- Bezpośrednia integracja modeli sztucznej inteligencji z użytkownikami przez protokół WebRTC.
- Główne abstrakcje: `Agent`, `AgentSession`, punkt wejścia (`entrypoint`) oraz `AgentServer`.
- Dwie klasy agentów:
  - **MultimodalAgent** – bezpośrednie przetwarzanie strumienia audio (np. za pomocą OpenAI Realtime API).
  - **VoicePipelineAgent** – klasyczny potok kaskadowy (STT → LLM → TTS), umożliwiający pełną kontrolę i modyfikację na etapie tekstowym.
- Semantyczne wykrywanie końca wypowiedzi (turn detection) za pomocą dedykowanego modelu Transformer.
- Natywna integracja z protokołem MCP.
- Integracja z telefonią tradycyjną za pomocą protokołu SIP.
- Ponad 50 modeli dostępnych bez konieczności konfiguracji kluczy API dzięki infrastrukturze LiveKit, a ponad 200 kolejnych za pomocą wtyczek.

### Komercyjne platformy zarządzane

Gotowe platformy takie jak Vapi (opóźnienia ~450–600 ms na zoptymalizowanym stosie premium) lub Retell (opóźnienie ~600 ms end-to-end) opierają się na tych technologiach. Warto wybrać takie rozwiązanie, jeśli zależy nam na gotowym, zarządzanym stosie głosowym bez konieczności utrzymywania zespołu inżynierów WebRTC.

### Najczęstsze błędy implementacyjne

- **Brak obsługi przerywania (barge-in).** Gdy użytkownik wchodzi agentowi w słowo, agent mówi dalej. Wymaga to poprawnego przesyłania ramek anulowania kierunkiem UPSTREAM w Pipecat (lub analogicznych mechanizmów w LiveKit).
- **Bezgraniczne ufanie transkrypcjom STT.** Przekazywanie do LLM tekstu o bardzo niskiej pewności rozpoznania (confidence score). Należy wdrożyć bramki weryfikacyjne lub mechanizm prośby o powtórzenie zdania.
- **Nieprawidłowe ucinanie syntezy w połowie zdania.** Gdy potok przerywa generowanie wypowiedzi, syntezator TTS musi płynnie wyciszyć lub poprawnie zakończyć strumieniowanie audio, by uniknąć trzasków.
- **Ignorowanie budżetu opóźnień.** Każdy element potoku dodaje od 50 do 200 ms. Zsumuj opóźnienia wszystkich modułów przed wdrożeniem produkcyjnym.

### Analiza opóźnień komponentów:

- Detekcja głosu (VAD): 20–60 ms
- Rozpoznawanie mowy (STT): 100–250 ms
- Generowanie pierwszego tokenu przez LLM: 150–400 ms
- Generowanie audio przez TTS: 100–200 ms
- Opóźnienie sieciowe transportu (RTT): 30–80 ms

Łączne opóźnienie (end-to-end) na poziomie 450–600 ms jest wynikiem znakomitym. Standardem w branży jest 800–1200 ms. Wszelkie opóźnienia przekraczające 1500 ms psują wrażenie naturalnej rozmowy.

## Przykład implementacji

Plik `code/main.py` zawiera uproszczoną symulację potoku opartego na ramkach:

- Zdefiniowano klasy ramkowe `Frame` (audio, transkrypcja, tekst, tts_audio, komunikaty sterujące).
- Utworzono interfejs procesora `Processor` z metodą `process(frame)`.
- Zaimplementowano 5 etapów potoku (VAD → STT → LLM → TTS → transport) jako niezależne procesory.
- Dodano obsługę komunikatu anulowania przesyłanego UPSTREAM w celu zilustrowania mechanizmu przerywania wypowiedzi.

Uruchomienie:

```
python3 code/main.py
```

Logi wyjściowe pokazują prawidłowy przepływ danych oraz sytuację przerywania wypowiedzi (barge-in), która natychmiast zatrzymuje syntezator TTS.

## Podsumowanie zastosowań

- **Pipecat** – gdy wymagana jest pełna kontrola nad każdym etapem potoku w Pythonie (własne procesory, wymienne moduły dostawców).
- **LiveKit Agents** – przy budowie systemów opartych natywnie na WebRTC oraz integracji z telefonią.
- **Vapi / Retell** – gdy potrzebujesz gotowej platformy głosowej w chmurze bez konieczności samodzielnego zarządzania infrastrukturą WebRTC.
- **OpenAI Realtime / Gemini Live** – w celu wdrożenia bezpośredniej komunikacji audio-to-audio bez pośrednich etapów tekstowych (klasa MultimodalAgent).

## Zadanie wdrożeniowe

Plik `outputs/skill-voice-pipeline.md` opisuje proces budowy szkieletu potoku głosowego wzorowanego na Pipecat, integrującego etapy VAD, STT, LLM, TTS, transport oraz zaawansowaną obsługę przerywania wypowiedzi (barge-in).

## Ćwiczenia praktyczne

1. Dodaj do uproszczonego potoku moduł monitorowania metryk: zliczaj liczbę ramek na sekundę na każdym etapie. Zidentyfikuj, w którym miejscu powstają największe opóźnienia.
2. Zaimplementuj bramkę weryfikującą jakość rozpoznawania STT. W przypadku niskiego współczynnika pewności (confidence score) zwróć prośbę o powtórzenie: „Czy możesz to powtórzyć?”.
3. Zaimplementuj uproszczone semantyczne wykrywanie końca wypowiedzi (np. gdy transkrypcja kończy się znakiem zapytania, uznaj turę za zakończoną).
4. Przeczytaj dokumentację Pipecat w obszarze warstwy transportowej. Zastąp uproszczony transport z biblioteki standardowej integracją z szablonem SmallWebRTCTransport.
5. Przeprowadź testy porównawcze czasu reakcji (latency) bezpośredniego modelu multimodalnego (np. OpenAI Realtime API) w porównaniu do potoku kaskadowego (STT + LLM + TTS). Jakie opóźnienia wprowadza warstwa kontroli tekstu?

## Kluczowe terminy

| Termin | Potoczne określenie | Co to dokładnie oznacza |
|------|----------------|--------------------------------------|
| Ramka (Frame) | „Zdarzenie” | Typowana jednostka danych przesyłana w potoku (np. ramka audio, transkrypcji, tekstu lub komunikatu sterującego) |
| Procesor (Processor) | „Krok w potoku” | Klasa lub funkcja przetwarzająca ramki określonego typu |
| Downstream | „Przepływ w dół” | Główny kierunek przepływu danych od źródła do odbiornika (od wejściowego strumienia audio do wyjściowej syntezy TTS) |
| Upstream | „Przepływ w górę” | Kierunek przesyłania komunikatów zwrotnych i sygnałów sterujących (np. anulowanie syntezy, metryki wydajnościowe, sygnał barge-in) |
| VAD (Voice Activity Detection) | „Detekcja głosu” | Algorytm określający, czy w strumieniu audio wejściowego znajduje się ludzka mowa |
| Semantyczne wykrywanie końca wypowiedzi | „Detekcja końca tury” | Logika oparta na analizie językowej lub modelu LLM, określająca moment, w którym użytkownik skończył mówić |
| Agent multimodalny (Multimodal Agent) | „Agent audio-to-audio” | Agent przetwarzający bezpośrednio strumień audio bez pośrednich etapów zamiany mowy na tekst |
| VoicePipelineAgent | „Potok kaskadowy” | Architektura łącząca trzy niezależne etapy (STT → LLM → TTS), umożliwiająca kontrolę i modyfikację tekstu na etapach pośrednich |

## Dalsze czytanie

- [Dokumentacja Pipecat](https://docs.pipecat.ai/getting-started/introduction) — potok oparty na ramkach, procesory, transporty
- [Dokumentacja LiveKit Agents](https://docs.livekit.io/agents/) — WebRTC + elementy podstawowe głosowe
- [Vapi](https://vapi.ai/) — zarządzana platforma głosowa
- [Retell AI](https://www.retellai.com/) — zarządzany głos, test porównawczy opóźnień
