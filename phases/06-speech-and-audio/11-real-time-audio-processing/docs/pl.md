# Przetwarzanie dźwięku w czasie rzeczywistym

> Potoki wsadowe przetwarzają plik. Potoki czasu rzeczywistego przetwarzają następne 20 milisekund, zanim nadejdzie kolejnych 20. Każda konwersacyjna sztuczna inteligencja, studio nadawcze i bot telefoniczny żyją i umierają w obliczu tego budżetu opóźnień.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 6 · 02 (spektrogramy), Faza 6 · 04 (ASR), Faza 6 · 07 (TTS)
**Czas:** ~75 minut

## Problem

Chcesz asystenta głosowego, który sprawia wrażenie żywego. Opóźnienie wykonywania tury przez człowieka wynosi ~230 ms (od ciszy do odpowiedzi). Wszystko powyżej 500 ms sprawia wrażenie robota; powyżej 1500 ms wydaje się uszkodzony. Budżet na pełną pętlę **słyszeć → rozumieć → odpowiadać → mówić** w 2026 roku wynosi:

| Scena | Budżet |
|-------|------------|
| Mikrofon → bufor | 20 ms |
| VAD | 10 ms |
| ASR (streaming) | 150 ms |
| LLM (pierwszy token) | 100 ms |
| TTS (pierwszy fragment) | 100 ms |
| Renderuj → głośnik | 20 ms |
| **Razem** | **~400 ms** |

Moshi (Kyutai, 2024) taktowany 200 ms w trybie pełnego dupleksu. Zegary czasu rzeczywistego GPT-4o (2024) ~320 ms. Rurociągi kaskadowe w 2022 r. będą dostarczane z częstotliwością 2500 ms. 10-krotna poprawa nastąpiła dzięki trzem technikom: (1) strumieniowaniu wszędzie, (2) asynchronicznemu potokowi z częściowymi wynikami, (3) generowaniu przerywanemu.

## Koncepcja

![Potok strumieniowego przesyłania dźwięku z buforem pierścieniowym, bramką VAD, przerwaniem](../assets/real-time.svg)

**Ramka / fragment / okno.** Dźwięk w czasie rzeczywistym przepływa w postaci bloków o stałym rozmiarze. Powszechnie wybierany: 20 ms (320 próbek przy 16 kHz). Wszystko w dalszej części rzeki musi nadążać za tym rytmem.

**Bufor pierścieniowy.** Bufor okrągły o stałym rozmiarze. Wątek producenta zapisuje nowe ramki, wątek konsumenta czyta. Zapobiega alokacji na ścieżce aktywnej. Rozmiar ≈ maksymalne opóźnienie × częstotliwość próbkowania; 2-sekundowy pierścień 16 kHz = 32 000 próbek.

**VAD (wykrywanie aktywności głosowej).** Bramki od strony odpływu działają, gdy nikt nie mówi. Silero VAD 4.0 (2024) działa <1 ms na ramkę 30 ms na procesorze. `webrtcvad` to starsza alternatywa.

**Streaming ASR.** Modele emitujące częściowe transkrypcje po nadejściu dźwięku. Parakeet-CTC-0.6B w trybie przesyłania strumieniowego (NeMo, 2024) osiąga 2–5% WER przy opóźnieniu 320 ms. Whisper-Streaming (Macháček i in., 2023) dzieli Szept na fragmenty do transmisji strumieniowej z opóźnieniem ~2 s.

**Przerwanie.** Kiedy użytkownik mówi podczas gdy asystent mówi, musisz (a) wykryć wtargnięcie, (b) zatrzymać TTS, (c) odrzucić pozostały sygnał LLM. Wszystko w ciągu 100 ms, w przeciwnym razie użytkownik dostrzeże niesłyszącego asystenta.

**Transport WebRTC Opus.** Ramki 20 ms, 48 ​​kHz, adaptacyjna przepływność 8–128 kb/s. Standard dla przeglądarek i urządzeń mobilnych. LiveKit, Daily.co, Pion to stosy na 2026 rok do tworzenia aplikacji głosowych.

**Bufor jitter.** Pakiety sieciowe docierają w niewłaściwej kolejności/z opóźnieniem. Bufor jitter porządkuje i wygładza; za małe → słyszalne przerwy, za duże → opóźnienie. Typowo 60–80 ms.

### Typowe problemy

- **Sporne wątki.** Ciężkie modele Pythona GIL + mogą zagłuszyć wątek audio. Użyj biblioteki audio C-callback (urządzenie dźwiękowe, PortAudio) i trzymaj Pythona z dala od popularnej ścieżki.
- **Opóźnienie konwersji częstotliwości próbkowania.** Ponowne próbkowanie wewnątrz potoku dodaje 5–20 ms. Albo spróbuj ponownie od razu, albo użyj narzędzia do resamplingu o zerowym opóźnieniu (PolyPhase, `soxr_hq`).
- **Uruchamianie TTS.** Nawet szybkie TTS, takie jak Kokoro, na pierwsze żądanie mają czas rozgrzewania 100–200 ms. Model cache + rozgrzej go fikcyjnym biegiem przed pierwszym prawdziwym zakrętem.
- **Wyeliminowanie echa.** Bez AEC sygnał wyjściowy TTS ponownie trafia do mikrofonu i uruchamia funkcję ASR na podstawie głosu bota. WebRTC AEC3 jest domyślnym oprogramowaniem typu open source.

## Zbuduj to

### Krok 1: bufor pierścieniowy

```python
import collections

class RingBuffer:
    def __init__(self, capacity):
        self.buf = collections.deque(maxlen=capacity)
    def write(self, frame):
        self.buf.extend(frame)
    def read(self, n):
        return [self.buf.popleft() for _ in range(min(n, len(self.buf)))]
    def level(self):
        return len(self.buf)
```

Pojemność określa maksymalne opóźnienie buforowania. 32 000 próbek przy 16 kHz = 2 s.

### Krok 2: Brama VAD

```python
def simple_energy_vad(frame, threshold=0.01):
    return sum(x * x for x in frame) / len(frame) > threshold ** 2
```

Zamień na Silero VAD w produkcji:

```python
import torch
vad, _ = torch.hub.load("snakers4/silero-vad", "silero_vad")
is_speech = vad(torch.tensor(frame), 16000).item() > 0.5
```

### Krok 3: przesyłanie strumieniowe ASR

```python
# Parakeet-CTC-0.6B streaming via NeMo
from nemo.collections.asr.models import EncDecCTCModelBPE
asr = EncDecCTCModelBPE.from_pretrained("nvidia/parakeet-ctc-0.6b")
# chunk_ms=320 ms, look_ahead_ms=80 ms
for chunk in audio_stream():
    partial_text = asr.transcribe_streaming(chunk)
    print(partial_text, end="\r")
```

### Krok 4: obsługa przerwań

```python
class Dialog:
    def __init__(self):
        self.tts_task = None

    def on_user_speech(self, frame):
        if self.tts_task and not self.tts_task.done():
            self.tts_task.cancel()   # barge-in
        # then feed to streaming ASR

    def on_final_user_utterance(self, text):
        self.tts_task = asyncio.create_task(self.reply(text))

    async def reply(self, text):
        async for tts_chunk in llm_then_tts(text):
            speaker.write(tts_chunk)
```

Zależnie od asynchronicznych wejść/wyjść i anulowanego przesyłania strumieniowego TTS. WebRTC peerconnection.stop() na ścieżce audio jest sposobem kanonicznym.

## Użyj tego

Stos na rok 2026:

| Warstwa | Wybierz |
|------|------|
| Transport | LiveKit (WebRTC) lub Pion (Go) |
| VAD | Silero VAD 4.0 |
| Streaming ASR | Parakeet-CTC-0.6B lub przesyłanie strumieniowe szeptów |
| Pierwszy token LLM | Groq, Cerebras, transmisja strumieniowa vLLM |
| Transmisja strumieniowa TTS | Kokoro lub ElevenLabs Turbo v2.5 |
| Anuluj echo | WebRTC AEC3 |
| Kompleksowy natywny | OpenAI Realtime API lub Moshi |

## Pułapki

- **Buforowanie 500 ms dla bezpieczeństwa.** Bufor *jest* Twoim minimalnym poziomem opóźnienia. Zmniejsz to.
- **Nie przypina wątków.** Dźwiękowe wywołanie zwrotne w wątku o niższym priorytecie niż interfejs użytkownika = usterki pod obciążeniem.
- ** Fragmenty TTS są za małe.** Fragmenty o długości poniżej 200 ms powodują, że artefakty wokodera są słyszalne. Najlepszym rozwiązaniem są fragmenty o długości 320 ms.
- **Brak bufora jitter.** Prawdziwe sieci są chwiejne; bez wygładzania otrzymasz popy.
- **Pojedyncza obsługa błędów.** Potoki audio muszą być odporne na awarie. Jeden wyjątek zabija sesję.

## Wyślij to

Zapisz jako `outputs/skill-realtime-designer.md`. Zaprojektuj potok audio w czasie rzeczywistym z konkretnymi budżetami opóźnień na etap.

## Ćwiczenia

1. **Łatwe.** Uruchom `code/main.py`. Symuluje bufor pierścieniowy + VAD energii; wypisuje opóźnienia sceniczne dla fałszywego 10-sekundowego strumienia.
2. **Średni.** Używając `sounddevice`, zbuduj pętlę przekazującą, która przetwarza Twój mikrofon w klatkach 20 ms i drukuje stan VAD w każdej klatce.
3. **Trudne.** Zbuduj pełny dupleksowy test echa za pomocą `aiortc`: przeglądarka → WebRTC → Python → WebRTC → przeglądarka. Zmierz opóźnienie szkło-szkło za pomocą impulsu 1 kHz.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Bufor pierścieniowy | Kolejka okrężna | Stały rozmiar, bez blokady (lub z blokadą SPSC) FIFO dla ramek audio. |
| VAD | Brama ciszy | Modelowe lub heurystyczne rozróżnianie mowy i niemowy. |
| Streaming ASR | STT w czasie rzeczywistym | Emituje częściowy tekst po nadejściu dźwięku; ograniczone spojrzenie w przód. |
| Bufor jittera | Sieć płynniejsza | Zmiana kolejności pakietów w kolejce; Typowo 60–80 ms. |
| AEC | Eliminacja echa | Odejmuje ścieżkę sprzężenia zwrotnego głośnik-mikrofon. |
| Wtargnięcie | Przerwanie użytkownika | System wykrywa mowę użytkownika w połowie TTS; należy anulować odtwarzanie. |
| Pełny dupleks | Jednoczesne w obie strony | Użytkownik i bot mogą rozmawiać w tym samym czasie; Moshi jest w trybie pełnego dupleksu. |

## Dalsze czytanie

- [Macháček i in. (2023). Whisper-Streaming](https://arxiv.org/abs/2307.14743) — podzielony na fragmenty prawie strumieniowy Whisper.
- [Kyutai (2024). Moshi](https://kyutai.org/Moshi.pdf) — pełny dupleks, opóźnienie 200 ms.
- [Framework LiveKit Agents (2024)](https://docs.livekit.io/agents/) — orkiestracja produkcyjnego agenta audio.
- [Repozytorium Silero VAD](https://github.com/snakers4/silero-vad) — VAD poniżej 1 ms, Apache 2.0.
- [Dokument WebRTC AEC3](https://webrtc.googlesource.com/src/+/main/modules/audio_processing/aec3/) — eliminacja echa w ramach oprogramowania open source.