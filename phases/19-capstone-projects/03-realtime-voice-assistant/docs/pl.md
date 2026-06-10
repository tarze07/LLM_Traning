# Capstone 03 — Asystent głosowy w czasie rzeczywistym (ASR do LLM do TTS)

> Agent głosowy, który czuje się dobrze, ma pełne opóźnienie poniżej 800 ms, wie, kiedy przestałeś mówić, radzi sobie z wtargnięciem i może wywołać narzędzie bez opóźnień. Retell, Vapi, LiveKit Agents i Pipecat osiągnęły ten poziom w 2026 roku. Robią to w tym samym kształcie: strumieniowy ASR, wykrywacz skrętu, strumieniowy LLM i strumieniowy TTS, a wszystko to podłączone poprzez WebRTC z agresywnymi budżetami opóźnień przy każdym przeskoku. Zbuduj taki, zmierz WER i MOS oraz współczynnik fałszywych odcięć i uruchom go w warunkach utraty pakietów.

**Typ:** Zwieńczenie
**Języki:** Python (agent + potok), TypeScript (klient sieciowy)
**Wymagania wstępne:** Faza 6 (mowa i dźwięk), Faza 7 (transformatory), Faza 11 (inżynieria LLM), Faza 13 (narzędzia), Faza 14 (agenci), Faza 17 (infrastruktura)
**Wykonywane fazy:** P6 · P7 · P11 · P13 · P14 · P17
**Czas:** 30 godzin

## Problem

Głos był najszybciej rozwijającą się kategorią AI UX w latach 2025–2026. Pułap techniczny obniżał się co kwartał. OpenAI Realtime API, Gemini 2.5 Live, Cartesia Sonic-2, ElevenLabs Flash v3, LiveKit Agents 1.0 i Pipecat 0.0.70 zapewniają pierwsze wyjście audio poniżej 800 ms w zasięgu ręki. Pasek to nie tylko opóźnienie. Jest to uczucie interakcji: nie odcinanie użytkownika, brak odcięcia, powrót do zdrowia po przerwaniu w połowie zdania, wywoływanie narzędzia w połowie rozmowy bez zatrzymywania dźwięku, przetrwanie niestabilnych sieci komórkowych.

Nie możesz się tam dostać, łącząc trzy wywołania REST. Architektura polega na przesyłaniu strumieniowym od końca do końca. Zbuduj go, a tryby awarii staną się widoczne: VAD dostrojony do odtwarzania dźwięku z telefonu na telewizorze w tle, czujnik skrętu czekający na znaki interpunkcyjne, które nigdy nie nadchodzą, TTS, który buforuje 400 ms przed emisją. Najważniejsze jest naprawienie ich pojedynczo pod obciążeniem i opublikowanie raportu na temat opóźnień i jakości.

## Koncepcja

Potok składa się z pięciu etapów przesyłania strumieniowego: **wejście audio** (WebRTC z przeglądarki lub PSTN), **ASR** (strumieniowe przesyłanie częściowych transkrypcji z Deepgram Nova-3 lub szybszych szeptów), **wykrywanie skrętu** (VAD plus mały model detektora skrętu, który odczytuje częściowe transkrypcje w celu uzyskania wskazówek o ukończeniu), **LLM** (tokeny przesyłania strumieniowego natychmiast po uznaniu, że tura została zakończona), **TTS** (strumieniowe przesyłanie dźwięku w ciągu ~200 ms od pierwszy token LLM).

Trzy przekrojowe obawy. **Wtrącanie**: gdy użytkownik zacznie mówić w czasie, gdy mówi agent, TTS zostanie anulowany, a ASR natychmiast włączy się. **Wykorzystanie narzędzia**: wywołania funkcji w trakcie rozmowy (pogoda, kalendarz) muszą działać na kanale bocznym bez zakłócania dźwięku; agent wstępnie wypełnia token potwierdzenia („jedna sekunda…”), jeśli opóźnienie przekracza 300 ms. ** Przeciwciśnienie**: w przypadku utraty pakietu częściowe transkrypcje są wstrzymywane, VAD podnosi próg bramki mowy, a agent unika wypowiadania się w niepotwierdzonej wiadomości.

Pasek pomiaru jest ilościowy. WER poniżej 8% w porównaniu z benchmarkiem Hamming VAD przy 15 dB SNR. Pierwsze wyjście audio p50 poniżej 800 ms przy 100 zmierzonych połączeniach. Odsetek fałszywych punktów odcięcia poniżej 3%. MOS powyżej 4,2 na TTS. 50 jednoczesnych połączeń na jednym g5.xlarge. Te liczby są możliwe do dostarczenia.

## Architektura

```
browser / Twilio PSTN
        |
        v
   WebRTC / SIP edge
        |
        v
  LiveKit Agents 1.0  (or Pipecat 0.0.70)
        |
   +----+--------------+--------------+-----------------+
   |                   |              |                 |
   v                   v              v                 v
  ASR              VAD v5         turn-detector     side-channel
(Deepgram         (Silero)          (LiveKit)        tools
 Nova-3 /         speech-gate    completion score    (weather,
 Whisper-v3)      per 20ms        on partials        calendar)
   |                   |              |
   +--------+----------+--------------+
            v
        LLM (streaming)
     GPT-4o-realtime / Gemini 2.5 Flash /
     cascaded Claude Haiku 4.5
            |
            v
        TTS streaming
     Cartesia Sonic-2 / ElevenLabs Flash v3
            |
            v
     audio back to caller
            |
            v
   OpenTelemetry voice traces -> Langfuse
```

## Stos

- Transport: LiveKit Agents 1.0 (WebRTC) plus brama Twilio PSTN; Pipecat 0.0.70 jako alternatywny framework
- ASR: Deepgram Nova-3 (strumieniowanie, pierwsza część poniżej 300 ms) lub szybszy szept Whisper-v3-turbo na własnym serwerze
- VAD: Silero VAD v5 plus wykrywacz skrętu LiveKit (mały transformator odczytujący częściowe transkrypcje)
- LLM: OpenAI GPT-4o-realtime dla ścisłej integracji, Gemini 2.5 Flash Live lub kaskadowy Claude Haiku 4.5 (zakończenie przesyłania strumieniowego, osobna ścieżka audio)
- TTS: Cartesia Sonic-2 (najniższy pierwszy bajt), ElevenLabs Flash v3 lub Orpheus typu open source do samodzielnego hostowania
- Narzędzia: boczny kanał FastMCP dla pogody/kalendarza/rezerwacji; agent wstępnie emituje wypełniacz, jeśli narzędzie zajmuje> 300 ms
- Obserwowalność: zakresy głosu OpenTelemetry, ślady głosu Langfuse z odtwarzaniem dźwięku
- Wdrożenie: pojedynczy g5.xlarge (24 GB VRAM) dla hostowanego samodzielnie Whisper + Orpheus; hostowane interfejsy API zapewniające najniższe opóźnienia

## Zbuduj to

1. **Sesja WebRTC.** Stwórz pokój LiveKit i klienta internetowego, który przesyła strumieniowo dźwięk z mikrofonu. Na serwerze dołącz pracownika agenta, który dołączy do pokoju.

2. **Przesyłanie strumieniowe ASR.** Przesyłaj klatki PCM z szybkością 20 ms do Deepgram Nova-3 (lub szybszy szept na GPU). Subskrybuj transkrypcje częściowe i końcowe. Rejestruj częściowe opóźnienia.

3. **VAD i detektor skrętu.** Uruchom Silero VAD v5 na strumieniu klatek. W przypadku zakończenia mowy uruchom wykrywacz skrętu LiveKit w celu sprawdzenia najnowszej częściowej transkrypcji. Zatwierdź opcję „zakończono” tylko wtedy, gdy VAD powie ciszę na 500 ms, a detektor obrotu uzyska wynik > 0,6.

4. **Strumień LLM.** Po zakończeniu tury rozpocznij połączenie LLM z trwającą rozmową i końcowym zapisem. Wysyłaj tokeny strumieniowe. Przy pierwszym żetonie przekaż TTS.

5. **Strumień TTS.** Cartesia Sonic-2 przesyła strumieniowo fragmenty audio z powrotem. Pierwsza porcja musi opuścić serwer w ciągu 200 ms od pierwszego tokena LLM. Emituj fragmenty do pokoju LiveKit; klient gra poprzez bufor jittera WebRTC.

6. **Wtargnięcie.** Kiedy VAD wykryje mowę nowego użytkownika podczas odtwarzania TTS, natychmiast anuluj strumień TTS, usuń pozostałe wyjście LLM i ponownie uzbrój ASR. Opublikuj zakres `tts_canceled`.

7. **Kanał boczny narzędzia.** Zarejestruj pogodę i kalendarz jako narzędzia wywołujące funkcje. Po wywołaniu wywołaj jednocześnie; jeśli problem nie zostanie rozwiązany w ciągu 300 ms, poproś LLM o wyemitowanie komunikatu „jedna sekunda, pozwól, że sprawdzę” jako uzupełnienie; wznowić po powrocie narzędzia.

8. **Uprząż Eval.** Nagraj 100 rozmów. Oblicz WER (w porównaniu z wstrzymaną transkrypcją), współczynnik fałszywych odcięć (TTS anulowany, gdy użytkownik był w połowie zdania), p50 pierwszego wyjścia audio, TTS MOS (ludzki lub NISQA) i test utraty jittera (utrata 3% pakietów).

9. **Test obciążenia.** Wykonaj 50 jednoczesnych połączeń na pojedynczym g5.xlarge za pomocą syntetycznego wywołującego. Zmierz trwałe pierwsze wyjście audio p95.

## Użyj tego

```
caller: "what is the weather in tokyo tomorrow"
[asr  ] partial @280ms: "what is the"
[asr  ] partial @540ms: "what is the weather"
[turn ] completion score 0.82 at @820ms; commit
[llm  ] first token @960ms
[tool ] weather.tokyo tomorrow -> 68/52 partly cloudy @1140ms
[tts  ] first audio-out @1040ms: "Tokyo tomorrow will be partly cloudy..."
turn latency: 1040ms user-stop -> audio-out
```

## Wyślij to

Elementem dostarczanym jest `outputs/skill-voice-agent.md`. Biorąc pod uwagę domenę (obsługa klienta, harmonogram lub kiosk), wystawia agenta LiveKit z potokiem ASR/VAD/LLM/TTS dostrojonym do paska pomiaru. Rubryka:

| Waga | Kryterium | Jak to się mierzy |
|:-:|---|---|
| 25 | Opóźnienie od końca do końca | p50 pierwsze wyjście audio poniżej 800 ms w 100 nagranych rozmowach |
| 20 | Jakość zwrotna | Wskaźnik fałszywej granicy poniżej 3% w porównaniu z benchmarkiem Hamming VAD |
| 20 | Poprawność użycia narzędzia | Wywołania narzędzi w trakcie rozmowy, które zwracają właściwe dane bez zatrzymywania dźwięku |
| 20 | Niezawodność w przypadku utraty pakietów | WER i stabilność wykonywania skrętów po wstrzyknięciu 3% spadku pakietów |
| 15 | Kompletność uprzęży Eval | Powtarzalne pomiary z konfiguracją publiczną |
| **100** | | |

## Ćwiczenia

1. Zamień Deepgram Nova-3 na szybszą wersję turbo v3 na g5.xlarge. Zmierz opóźnienie i przerwę WER. Zidentyfikuj, gdzie decyzje dotyczące procesora i karty graficznej mają znaczenie.

2. Dodaj politykę arbitrażu przerwań: co robi agent, gdy użytkownik wtrąca się podczas wywołania narzędzia? Porównaj trzy zasady (twarde anulowanie, zakończ narzędzie, a następnie zatrzymaj, kolejka następnej tury).

3. Przeprowadź kontradyktoryjny test wykrywacza ruchu: daj użytkownikowi długą pauzę w połowie zdania. Dostosuj próg ciszy VAD i próg wyniku czujnika obrotu, aby uzyskać najniższe fałszywe odcięcie bez przekraczania 900 ms.

4. Wdróż tego samego agenta w sieci PSTN za pośrednictwem Twilio. Porównaj pierwsze wyjście audio PSTN z WebRTC. Wyjaśnij różnice w buforze jitter i kodekach.

5. Dodaj wykrywanie aktywności głosowej dla języków innych niż angielski (japoński, hiszpański). Zmierz współczynnik fałszywych wyzwalaczy Silero VAD v5 w porównaniu z poprawkami specyficznymi dla języka.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| Wykrywanie skrętu | „Koniec wypowiedzi” | Klasyfikator, który na podstawie ciszy VAD i częściowej transkrypcji decyduje, że użytkownik skończył mówić |
| Wtargnięcie | „Obsługa przerwań” | Anulowanie odtwarzania TTS w trakcie odtwarzania, gdy VAD wykryje mowę nowego użytkownika |
| Pierwsze wyjście audio | „Opóźnienie” | Czas od chwili zaprzestania mówienia przez użytkownika do pierwszego pakietu audio opuszczającego serwer |
| VAD | „Brama mowy” | Model klasyfikujący klatki audio jako mowę i ciszę; Silero VAD v5 jest domyślnym rozwiązaniem na rok 2026 |
| Bufor jittera | „Wygładzanie dźwięku” | Bufor po stronie klienta, który krótko przechowuje pakiety w celu wchłonięcia odchyleń sieci |
| Wypełniacz | „Token potwierdzenia” | Krótka fraza emitowana przez agenta, aby uniknąć ciszy, gdy narzędzie działa wolno |
| MOS | „Średni wynik opinii” | Percepcyjna ocena jakości mowy; NISQA to automatyczny serwer proxy |

## Dalsze czytanie

- [LiveKit Agents 1.0](https://github.com/livekit/agents) — referencyjna platforma agenta WebRTC
- [Pipecat](https://github.com/pipecat-ai/pipecat) — alternatywna platforma agenta przesyłania strumieniowego oparta na Pythonie
- [OpenAI Realtime API](https://platform.openai.com/docs/guides/realtime) — odniesienie do zintegrowanych modeli mowy
- [Dokumentacja Deepgram Nova-3](https://developers.deepgram.com/docs) — informacje dotyczące przesyłania strumieniowego ASR
- [Silero VAD v5](https://github.com/snakers4/silero-vad) — model referencyjny VAD
- [Cartesia Sonic-2](https://docs.cartesia.ai) — odniesienie do TTS o niskim opóźnieniu
- [Architektura Retell AI](https://docs.retellai.com) — architektura produkcyjnego agenta głosowego
- [Stos produkcyjny Vapi.ai](https://docs.vapi.ai) — alternatywne odniesienie do produkcji