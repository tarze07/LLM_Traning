# Zbuduj linię asystentów głosowych — zwieńczenie fazy 6

> Wszystko z lekcji 01-11, zszyte razem. Stwórz asystenta głosowego, który słucha, uzasadnia i odpowiada. W 2026 r. będzie to rozwiązany problem inżynieryjny, a nie badawczy, ale o tym, czy zostanie dostarczony, zadecydują szczegóły integracji.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania:** Faza 6 · 04, 05, 06, 07, 11; Faza 11 · 09 (Wywołanie funkcji); Faza 14 · 01 (pętla agenta)
**Czas:** ~120 minut

## Problem

Zbuduj kompleksowego asystenta:

1. Przechwytuje wejście mikrofonowe (16 kHz mono).
2. Wykrywa początek/koniec mowy użytkownika.
3. Transkrypcja transmisji strumieniowej.
4. Przekazuje transkrypcję do LLM, który może wywoływać narzędzia (zegar, pogoda, kalendarz).
5. Przesyła strumieniowo tekst LLM do TTS.
6. Odtwarza dźwięk użytkownikowi.
7. Zatrzymuje się, jeśli użytkownik przerwie w połowie odpowiedzi.

Docelowe opóźnienie: pierwszy bajt audio TTS w ciągu 800 ms od zakończenia wypowiedzi przez użytkownika na procesorze laptopa. Cel jakościowy: brak pominiętych słów, brak halucynacyjnych napisów w ciszy, brak wycieków klonowania głosu, brak szybkiego powodzenia wstrzyknięcia.

## Koncepcja

![Potok asystenta głosowego: mikrofon → VAD → STT → LLM+tools → TTS → głośnik](../assets/voice-assistant.svg)

### Siedem składników

1. **Przechwytywanie dźwięku.** Mikrofon → 16 kHz mono → fragmenty 20 ms. Zwykle `sounddevice` w Pythonie lub natywnym AudioUnit/ALSA/WASAPI w produkcji.
2. **VAD (lekcja 11).** Silero VAD przy progu 0,5, min. mowa 250 ms, zawieszenie ciszy 500 ms. Sygnały „start” i „koniec”.
3. **Streaming STT (lekcja 4-5).** Streaming szeptem, Parakeet-TDT lub Deepgram Nova-3 (API). Transkrypcje częściowe + końcowe.
4. **LLM z wywołaniem narzędzia.** GPT-4o / Claude 3.5 / Gemini 2.5 Flash. Schemat JSON dla narzędzi. Tokeny strumieniowe.
5. **Streaming TTS (lekcja 7).** Kokoro-82M (najszybsze otwarcie) lub Cartesia Sonic (wersja komercyjna). Rozpocznij TTS po 20 tokenach LLM.
6. **Odtwarzanie.** Wyjście głośnikowe; opus-encode dla sieci o niskiej przepustowości.
7. **Obsługa przerwań.** Jeśli VAD uruchomi się podczas odtwarzania TTS, zatrzymaj odtwarzanie, anuluj LLM, zrestartuj STT.

### Trzy tryby awarii, na które trafisz

1. **Klip z pierwszym słowem.** VAD zaczyna rytm za późno. Brakuje „hej” użytkownika. Próg początkowy przy 0,3, a nie 0,5.
2. **Zamieszanie związane z przerwaniem w połowie odpowiedzi.** LLM kontynuuje generowanie po przerwaniach użytkownika; asystent rozmawia z użytkownikiem. Przewód VAD → anuluj-LLM.
3. **Wycisz halucynacje.** W cichych klatkach rozgrzewkowych słychać szept „Dzięki za obejrzenie”. Zawsze bramka VAD.

### Stosy referencyjne produkcji na rok 2026

| Stos | Opóźnienie | Licencja | Notatki |
|-------|--------|---------|-------|
| LiveKit + Deepgram + GPT-4o + Cartesia | 350-500 ms | komercyjne API | Domyślność branży 2026 |
| Pipecat + Przesyłanie strumieniowe szeptów + GPT-4o + Kokoro | 500-800 ms | przeważnie otwarte | Przyjazny dla majsterkowiczów |
| Moshi (pełny dupleks) | 200-300 ms | CC-BY 4.0 | Pojedynczy model; inna architektura, lekcja 15 |
| Vapi / Retell (zarządzany) | 300-500 ms | komercyjny | Najszybszy do uruchomienia; ograniczone dostosowywanie |
| Whisper.cpp + lama.cpp + Kokoro-ONNX | nieaktywny | otwarte | Prywatność / krawędź |

## Zbuduj to

### Krok 1: przechwytywanie mikrofonu z fragmentacją (pseudokod)

```python
import sounddevice as sd

def mic_stream(chunk_ms=20, sr=16000):
    q = queue.Queue()
    def cb(indata, frames, time, status):
        q.put(indata.copy().flatten())
    with sd.InputStream(channels=1, samplerate=sr, blocksize=int(sr * chunk_ms/1000), callback=cb):
        while True:
            yield q.get()
```

### Krok 2: Przechwytywanie skrętu bramkowanego VAD

```python
def capture_turn(stream, vad, pre_roll_ms=300, silence_ms=500):
    buf, pre, triggered = [], collections.deque(maxlen=pre_roll_ms // 20), False
    silent = 0
    for chunk in stream:
        pre.append(chunk)
        if vad(chunk):
            if not triggered:
                buf = list(pre)
                triggered = True
            buf.append(chunk)
            silent = 0
        elif triggered:
            silent += 20
            buf.append(chunk)
            if silent >= silence_ms:
                return b"".join(buf)
```

### Krok 3: przesyłanie strumieniowe STT → LLM → TTS

```python
async def turn(audio_bytes):
    transcript = await stt.transcribe(audio_bytes)
    async for token in llm.stream(transcript):
        async for audio in tts.stream(token):
            await speaker.play(audio)
```

### Krok 4: wywołanie narzędzia w pętli LLM

```python
tools = [
    {"name": "get_weather", "parameters": {"location": "string"}},
    {"name": "set_timer", "parameters": {"seconds": "int"}},
]

async for chunk in llm.stream(user_text, tools=tools):
    if chunk.type == "tool_call":
        result = dispatch(chunk.name, chunk.args)
        continue_streaming(result)
    if chunk.type == "text":
        await tts.stream(chunk.text)
```

### Krok 5: obsługa przerwań

```python
tts_task = asyncio.create_task(tts_loop())
while True:
    chunk = await mic.get()
    if vad(chunk):
        tts_task.cancel()
        await speaker.stop()
        await new_turn()
        break
```

## Użyj tego

Zobacz `code/main.py`, aby zapoznać się z wykonalną symulacją, która łączy wszystkie siedem komponentów z modelami odgałęzień, dzięki czemu można zobaczyć kształt rurociągu nawet bez sprzętu. Aby uzyskać prawdziwą implementację, zamień kody pośrednie na:

- `silero-vad` (`pip install silero-vad`)
- `deepgram-sdk` lub `openai-whisper`
- `openai` (`gpt-4o`) lub `anthropic`
- `kokoro` lub `cartesia`
- `sounddevice` dla wejść/wyjść

## Pułapki

- **Zapisywanie informacji umożliwiających identyfikację na zawsze.** Dźwięk pełnoobrotowy w większości jurysdykcji umożliwia identyfikację osób. Przechowywanie przez 30 dni, szyfrowane w stanie spoczynku.
- **Zakaz wtrącania się.** Użytkownicy będą przeszkadzać. Twój asystent musi przestać mówić.
- **TTS blokujący.** Synchroniczny TTS blokuje pętlę zdarzeń. Użyj asynchronii lub osobnego wątku.
- **Brak obsługi błędów wywołań narzędzi.** Narzędzia nie działają. LLM musi odzyskać błąd i ponowić próbę raz, a następnie bezpiecznie pogorszyć sytuację.
- **Nadgorliwe filtry halucynacyjne.** Przefiltruj, a asystent powtarza: „Nie mogę w tym pomóc”. Filtr pod filtrem i mówi wszystko. Kalibracja na wyciągniętym zestawie.
- **Brak opcji aktywacji.** Zawsze słuchanie stanowi naruszenie prywatności. Dodaj bramkę budzącą (Porcupine lub openWakeWord).

## Wyślij to

Zapisz jako `outputs/skill-voice-assistant-architect.md`. Biorąc pod uwagę budżet + skalę + język + ograniczenia zgodności, utwórz specyfikację pełnego stosu.

## Ćwiczenia

1. **Łatwe.** Uruchom `code/main.py`. Symuluje jeden pełny obrót od końca do końca z modułami pośrednimi i drukuje opóźnienia dla każdego etapu.
2. **Średni.** Zastąp odcinek STT prawdziwym modelem Whisper na nagranym wcześniej `.wav`. Zmierz WER i pełne opóźnienie.
3. **Trudne.** Dodaj wywołanie narzędzia: zaimplementuj `get_weather` (dowolne API) i `set_timer`. Przeprowadź LLM przez narzędzia i sprawdź, czy gdy użytkownik powie „ustaw minutnik na 5 minut”, uruchomi się właściwa funkcja, a odpowiedź głosowa to potwierdzi.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Skręć | Użytkownik + asystent w obie strony | Jedna mowa użytkownika ograniczona VAD + jedna odpowiedź LLM-TTS. |
| Wtargnięcie | Przerwanie | Użytkownik mówi, podczas gdy asystent mówi; asystent zatrzymuje się. |
| Obudź słowo | „Hej, asystentze” | Wykrywacz krótkich słów kluczowych; Porcupine, Snowboy, openWakeWord. |
| Punkt końcowy | Zakończenie tury | VAD + decyzja o min-wyciszeniu, którą użytkownik zakończył. |
| Przed filmem | Bufor przed mową | Zachowaj dźwięk o długości 200–400 ms przed uruchomieniem VAD, aby uniknąć klipu pierwszego słowa. |
| Wywołanie narzędzia | Wywołanie funkcji | LLM emituje JSON; wysyłki w czasie wykonywania; wynik jest przesyłany zwrotnie w pętli. |

## Dalsze czytanie

— [LiveKit — szybki start dotyczący agenta głosowego](https://docs.livekit.io/agents/) — odniesienie do wersji produkcyjnej.
- [Pipecat — przykłady agentów głosowych](https://github.com/pipecat-ai/pipecat) — framework przyjazny dla majsterkowiczów.
- [OpenAI Realtime API](https://platform.openai.com/docs/guides/realtime) — zarządzana ścieżka natywna dla głosu.
- [Kyutai Moshi](https://github.com/kyutai-labs/moshi) — odniesienie do pełnego dupleksu (lekcja 15).
- [Słowo przebudzenia Porcupine](https://picovoice.ai/products/porcupine/) — bramkowanie słów przebudzenia.
- [Anthropic — przewodnik użytkowania narzędzi](https://docs.anthropic.com/en/docs/build-with-claude/tool-use) — wywoływanie funkcji LLM.