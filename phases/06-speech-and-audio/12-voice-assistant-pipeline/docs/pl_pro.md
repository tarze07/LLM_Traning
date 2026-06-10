# Projektowanie potoku asystenta głosowego (Voice Assistant Pipeline)

> Wszystkie elementy z lekcji 01-11 połączone w jeden zintegrowany system. Celem jest stworzenie asystenta głosowego, który płynnie słucha, logicznie rozumuje i naturalnie odpowiada w czasie rzeczywistym. W 2026 roku jest to w pełni rozwiązany problem inżynieryjny, a nie badawczy. O sukcesie wdrożenia produkcyjnego decydują jednak szczegóły integracji poszczególnych komponentów.

**Typ:** Kompendium  
**Języki:** Python  
**Wymagania:** Faza 6 · 04, 05, 06, 07, 11; Faza 11 · 09 (Wywoływanie funkcji); Faza 14 · 01 (Pętla agenta)  
**Czas:** ~120 minut  

## Problem

Twoim zadaniem jest budowa kompletnego asystenta głosowego, który:

1. Przechwytuje wejściowy sygnał z mikrofonu (16 kHz mono).
2. Wykrywa początek i koniec wypowiedzi użytkownika.
3. Realizuje strumieniową transkrypcję mowy.
4. Przekazuje tekst do modelu LLM wspierającego wywoływanie zewnętrznych narzędzi (np. kalendarz, prognoza pogody).
5. Strumieniowo przekazuje generowany tekst z LLM do modułu syntezy TTS.
6. Odtwarza wygenerowany dźwięk użytkownikowi.
7. Natychmiast przerywa odtwarzanie (barge-in), jeśli użytkownik zacznie mówić w trakcie wypowiedzi asystenta.

Docelowe opóźnienie (latencja): pierwszy bajt wyjściowego audio z TTS musi zostać wygenerowany w czasie poniżej 800 ms od momentu zakończenia wypowiedzi przez użytkownika (mierzone lokalnie na procesorze CPU laptopa). Kryteria jakościowe: brak ucinania początków słów, brak halucynacji w ciszy, brak ryzyka naruszenia praw autorskich głosów, odporność na ataki typu Prompt Injection.

## Koncepcja

![Schemat potoku asystenta głosowego: mikrofon → VAD → STT → LLM+narzędzia → TTS → głośnik](../assets/voice-assistant.svg)

### Siedem kluczowych komponentów

1. **Przechwytywanie audio:** Pobieranie sygnału z mikrofonu (16 kHz mono, okna 20 ms). W Pythonie służy do tego biblioteka `sounddevice`, natomiast w systemach produkcyjnych stosuje się natywne interfejsy (AudioUnit, ALSA, WASAPI).
2. **VAD (lekcja 11):** Bramkowanie za pomocą Silero VAD z progiem czułości 0.5, minimalnym czasem mowy 250 ms i czasem podtrzymania ciszy (hangover) 500 ms. Generuje sygnały rozpoczęcia i zakończenia wypowiedzi.
3. **Strumieniowy STT (lekcja 4-5):** Modele Parakeet-TDT, Whisper-Streaming lub API Deepgram Nova-3. Odpowiada za dostarczanie wyników cząstkowych i ostatecznej transkrypcji.
4. **Model LLM z obsługą funkcji (Tool Calling):** GPT-4o, Claude 3.5 Sonnet lub Gemini 2.5 Flash. Przetwarza teksty strukturalnie w formacie JSON i strumieniuje tokeny odpowiedzi.
5. **Strumieniowy TTS (lekcja 7):** Szybki model Kokoro-82M (lokalnie na CPU) lub Cartesia Sonic (chmura). Synteza mowy powinna ruszać po wygenerowaniu pierwszych 20 tokenów przez model LLM.
6. **Odtwarzacz audio:** Buforowanie i odtwarzanie dźwięku; opcjonalnie kompresja Opus przy przesyłaniu przez sieć o niskiej przepustowości.
7. **Obsługa przerwań (Barge-in):** Jeśli VAD wykryje mowę użytkownika podczas odtwarzania TTS, system musi natychmiast zatrzymać odtwarzacz, anulować zapytanie LLM i zresetować stan STT.

### Trzy typowe tryby awarii (i jak ich unikać)

1. **Ucinanie pierwszego słowa (first-word clipping).** Moduł VAD aktywuje się zbyt późno i ucina np. powitanie „Hej”. Rozwiązanie: zastosuj bufor pre-roll o długości 200-300 ms i obniż próg aktywacji VAD do 0.3.
2. **Brak reakcji na przerwanie wypowiedzi (barge-in failure).** Model LLM kontynuuje generowanie tekstu mimo wtrącenia się użytkownika, przez co bot próbuje „przekrzyczeć” rozmówcę. Rozwiązanie: połącz zdarzenie aktywacji VAD z jawnym sygnałem anulowania wątku LLM i wyciszenia TTS.
3. **Halucynacje na fragmentach ciszy.** Wyciszone fragmenty audio prowokują model ASR do generowania fraz typu „Dzięki za obejrzenie”. Rozwiązanie: bezwzględnie filtruj wejście bramką VAD przed przekazaniem do modelu ASR.

### Porównanie stosów technologicznych (stan na 2026 r.)

| Stos technologiczny | Latencja | Licencja | Uwagi |
|-------|--------|---------|-------|
| LiveKit + Deepgram + GPT-4o + Cartesia | 350-500 ms | Komercyjna (API) | Branżowy standard (2026) |
| Pipecat + Whisper-Streaming + GPT-4o + Kokoro | 500-800 ms | Głównie open-source | Optymalny dla własnych wdrożeń (DIY) |
| Moshi (pełny dupleks) | 200-300 ms | CC-BY 4.0 | Pojedynczy model (architektura end-to-end, lekcja 15) |
| Vapi / Retell | 300-500 ms | Komercyjna (SaaS) | Najszybsze wdrożenie, ograniczona kastomizacja |
| Whisper.cpp + llama.cpp + Kokoro-ONNX | >1200 ms | Open-source | Maksymalna prywatność / urządzenia brzegowe (edge) |

## Implementacja krok po kroku

### Krok 1: Strumieniowe przechwytywanie dźwięku z mikrofonu (pseudokod)

```python
import sounddevice as sd
import queue

def mic_stream(chunk_ms=20, sr=16000):
    q = queue.Queue()
    def cb(indata, frames, time, status):
        q.put(indata.copy().flatten())
    with sd.InputStream(channels=1, samplerate=sr, blocksize=int(sr * chunk_ms/1000), callback=cb):
        while True:
            yield q.get()
```

### Krok 2: Przechwytywanie wypowiedzi użytkownika (Turn Detection) z bramkowaniem VAD

```python
def capture_turn(stream, vad, pre_roll_ms=300, silence_ms=500):
    buf = []
    pre = collections.deque(maxlen=pre_roll_ms // 20)
    triggered = False
    silent_time = 0
    for chunk in stream:
        pre.append(chunk)
        if vad(chunk):
            if not triggered:
                buf = list(pre)  # pobranie bufora pre-roll, aby nie uciąć początku słowa
                triggered = True
            buf.append(chunk)
            silent_time = 0
        elif triggered:
            silent_time += 20
            buf.append(chunk)
            if silent_time >= silence_ms:
                return b"".join(buf)
```

### Krok 3: Strumieniowy potok STT → LLM → TTS

```python
async def turn(audio_bytes):
    transcript = await stt.transcribe(audio_bytes)
    async for token in llm.stream(transcript):
        async for audio in tts.stream(token):
            await speaker.play(audio)
```

### Krok 4: Wywoływanie funkcji (Tool Calling) w pętli agenta

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

### Krok 5: Obsługa przerwania syntezy (Barge-in)

```python
tts_task = asyncio.create_task(tts_loop())
while True:
    chunk = await mic.get()
    if vad(chunk):
        tts_task.cancel()  # zatrzymanie generowania
        await speaker.stop()  # natychmiastowe wyciszenie odtwarzacza
        await new_turn()  # rozpoczęcie nowej tury rozmowy
        break
```

## Sugerowane podejście produkcyjne

Szczegółowa symulacja pokazująca integrację wszystkich siedmiu komponentów z użyciem modeli referencyjnych znajduje się w pliku `code/main.py`. Pozwala to na przetestowanie przepływu potoku i latencji bez konieczności podłączania mikrofonu. Przy przejściu do rzeczywistego wdrożenia zastąp moduły makietowe bibliotekami:
- `silero-vad` (`pip install silero-vad`)
- `deepgram-sdk` lub `openai-whisper`
- `openai` (`gpt-4o`) lub `anthropic`
- `kokoro` lub `cartesia`
- `sounddevice` dla obsługi wejścia/wyjścia audio.

## Typowe pułapki

- **Naruszenie prywatności i przechowywanie danych wrażliwych.** Nagrania głosowe w większości jurysdykcji są traktowane jako dane biometryczne (dane osobowe). Przechowuj je maksymalnie przez 30 dni w formie zaszyfrowanej, a logi z transkrypcji czyść z danych wrażliwych (CVV, PESEL) za pomocą modeli NER lub wyrażeń regularnych przed zapisem do bazy.
- **Ignorowanie wtrąceń (barge-in).** Brak obsługi przerwania wypowiedzi bota jest krytycznym błędem UX – użytkownik musi mieć możliwość przerwania asystenta w dowolnym momencie.
- **Blokowanie pętli zdarzeń.** Synchroniczne wywołania TTS lub modeli akustycznych potrafią całkowicie zawiesić odtwarzanie dźwięku. Zawsze stosuj biblioteki asynchroniczne lub deleguj te zadania do osobnych wątków roboczych (worker threads).
- **Brak obsługi błędów przy wywoływaniu funkcji.** Narzędzia mogą zwracać błędy sieciowe lub niepoprawne dane. Model LLM musi umieć zinterpretować błąd, spróbować ponownego wywołania lub w razie trwałego błędu poinformować o tym użytkownika w naturalny sposób (graceful degradation).
- **Źle skalibrowane filtry bezpieczeństwa/halucynacji.** Zbyt rygorystyczne filtry powodują, że asystent odmawia odpowiedzi na neutralne zapytania (false positives), natomiast zbyt łagodne pozwalają na generowanie nieprawdziwych informacji. Należy kalibrować te filtry na dedykowanym zbiorze walidacyjnym.
- **Brak detekcji słowa budzącego (Wake Word).** Ciągłe nasłuchiwanie i przesyłanie dźwięku do chmury bez wyraźnej aktywacji stanowi naruszenie prywatności użytkownika. Zaimplementuj lokalny moduł wykrywania słowa kluczowego (np. Porcupine lub openWakeWord).

## Zadanie do wykonania

Zapisz jako `outputs/skill-voice-assistant-architect.md`. Zaprojektuj kompletną specyfikację techniczną potoku asystenta głosowego (architektura, opóźnienia, obsługa błędów, zgodność z przepisami).

## Ćwiczenia

1. **Łatwe.** Uruchom skrypt `code/main.py`. Symuluje on pełną turę rozmowy (end-to-end) z użyciem makiet komponentów i wypisuje latencje poszczególnych etapów.
2. **Średnie.** Zastąp makietę STT rzeczywistym wywołaniem modelu Whisper na nagranym wcześniej pliku `.wav`. Zmierz współczynnik WER oraz całkowity czas odpowiedzi (round-trip latency).
3. **Trudne.** Zaimplementuj obsługę narzędzi: stwórz funkcje `get_weather` oraz `set_timer`. Przeprowadź model LLM przez proces wywołania narzędzia i zweryfikuj, czy wypowiedź „ustaw minutnik na 5 minut” wywołuje poprawną funkcję w tle, a odpowiedź głosowa TTS to potwierdza.

## Kluczowe terminy

| Termin | Potoczne określenie | Co to naprawdę oznacza |
|------|-----------------|----------------------|
| Turn | Tura rozmowy | Pełny cykl interakcji: wypowiedź użytkownika ograniczona bramką VAD + odpowiedź systemu (LLM-TTS). |
| Barge-in | Wtrącenie się | Sytuacja, w której użytkownik przerywa wypowiedź bota, co powinno skutkować natychmiastowym przerwaniem syntezy mowy. |
| Wake Word | Słowo budzące | Lokalny detektor krótkich fraz kluczowych (np. „Alexa”, „Ok Google”), uruchamiający główny potok asystenta. |
| Endpointing | Wykrycie końca wypowiedzi | Decyzja algorytmu (na bazie VAD i czasu trwania ciszy), że użytkownik zakończył swoją wypowiedź. |
| Pre-roll buffer | Buforowanie wstępne | Buforowanie 200–400 ms dźwięku przed faktycznym wykryciem mowy przez VAD, co zapobiega ucinaniu początku pierwszego wypowiedzianego słowa. |
| Tool Calling | Wywoływanie funkcji | Zdolność modelu LLM do wygenerowania ustrukturyzowanego kodu JSON w celu uruchomienia zewnętrznych funkcji, których wyniki są włączane do kontekstu rozmowy. |

## Dalsze czytanie

- [LiveKit Voice Agent Documentation](https://docs.livekit.io/agents/) — kompletny przewodnik po budowie produkcyjnych agentów głosowych.
- [Pipecat Framework GitHub](https://github.com/pipecat-ai/pipecat) — popularny framework open-source do budowy asystentów głosowych.
- [OpenAI Realtime API Guide](https://platform.openai.com/docs/guides/realtime) — dokumentacja OpenAI dla zintegrowanych sesji głosowych o niskiej latencji.
- [Kyutai Moshi Repository](https://github.com/kyutai-labs/moshi) — kod źródłowy i wagi modelu Moshi.
- [Picovoice Porcupine Wake Word](https://picovoice.ai/products/porcupine/) — narzędzie do projektowania własnych słów budzących.
- [Anthropic Tool Use Guide](https://docs.anthropic.com/en/docs/build-with-claude/tool-use) — instrukcje i najlepsze praktyki dotyczące wywoływania funkcji w modelach Claude.
