# Przetwarzanie dźwięku w czasie rzeczywistym (Real-Time Audio Processing)

> Potoki wsadowe (batch pipelines) przetwarzają cały plik audio jednocześnie. Potoki czasu rzeczywistego (real-time pipelines) muszą przetworzyć bieżącą 20-milisekundową ramkę, zanim nadejdzie kolejna. Każdy konwersacyjny asystent AI, system nadawczy czy bot telefoniczny zależy od tego rygorystycznego budżetu opóźnień.

**Typ:** Kompendium  
**Języki:** Python  
**Wymagania wstępne:** Faza 6 · 02 (spektrogramy i filtry melowe), Faza 6 · 04 (ASR), Faza 6 · 07 (TTS)  
**Czas:** ~75 minut  

## Problem

Aby interakcja z asystentem głosowym była naturalna, system musi reagować błyskawicznie. W naturalnej rozmowie czas reakcji człowieka wynosi średnio ok. 230 ms. Opóźnienie powyżej 500 ms sprawia wrażenie sztuczności, natomiast powyżej 1500 ms wywołuje u użytkownika poczucie, że system przestał działać. Budżet opóźnień na pełną pętlę **słyszenie → rozumienie → generowanie odpowiedzi → synteza mowy** w 2026 roku prezentuje się następująco:

| Etap | Budżet czasowy |
|-------|------------|
| Mikrofon → bufor wejściowy | 20 ms |
| VAD (detekcja aktywności głosowej) | 10 ms |
| ASR (transkrypcja strumieniowa) | 150 ms |
| LLM (wygenerowanie pierwszego tokenu)| 100 ms |
| TTS (synteza pierwszego pakietu audio)| 100 ms |
| Buforowanie wyjścia → głośnik | 20 ms |
| **Łącznie** | **~400 ms** |

Model Moshi (Kyutai, 2024) osiąga latencję na poziomie 200 ms w trybie pełnego dupleksu (full-duplex). Latencja API OpenAI Realtime (GPT-4o, 2024) wynosi średnio 320 ms. Dla porównania, kaskadowe potoki w 2022 roku charakteryzowały się latencją rzędu 2500 ms. Ta 10-krotna redukcja opóźnień była możliwa dzięki trzem technikom: (1) strumieniowaniu danych na każdym etapie potoku, (2) asynchronicznemu przetwarzaniu z wykorzystaniem wyników cząstkowych, (3) mechanizmowi wtrącenia i natychmiastowego przerywania syntezy (barge-in).

## Koncepcja

![Schemat potoku strumieniowego audio z buforem kołowym, bramką VAD oraz mechanizmem przerwania (barge-in)](../assets/real-time.svg)

**Ramka, pakiet lub okno czasowe (Frame / Chunk).** Sygnał audio w czasie rzeczywistym przesyłany jest w postaci pakietów o stałym rozmiarze. Standardowym wyborem jest okno 20 ms (co odpowiada 320 próbkom przy częstotliwości 16 kHz). Wszystkie kolejne moduły w potoku muszą przetwarzać dane w tym samym tempie.

**Bufor kołowy / pierścieniowy (Ring Buffer).** Struktura danych FIFO o stałym rozmiarze. Wątek rejestrujący (producent) zapisuje nowe ramki, a wątek przetwarzający (konsument) je odczytuje. Zapobiega to kosztownym alokacjom pamięci na krytycznej ścieżce przetwarzania. Pojemność bufora ≈ maksymalna latencja x częstotliwość próbkowania (np. 2-sekundowy bufor dla 16 kHz to 32 000 próbek).

**VAD (Voice Activity Detection).** Służy do bramkowania dalszych etapów przetwarzania w okresach ciszy. Model Silero VAD 4.0 (2024) potrzebuje mniej niż 1 ms na przetworzenie 30-milisekundowej ramki na procesorze CPU. Klasyczną, lżejszą alternatywą jest biblioteka `webrtcvad`.

**Strumieniowy model ASR.** Modele te zwracają częściowy tekst transkrypcji na bieżąco, w miarę napływania kolejnych ramek dźwiękowych. Model Parakeet-CTC-0.6B (NVIDIA NeMo) w trybie strumieniowym osiąga 2–5% WER przy opóźnieniu wynoszącym zaledwie 320 ms. Z kolei Whisper-Streaming dzieli nagranie na nachodzące na siebie fragmenty, umożliwiając transkrypcję z latencją ok. 2 s.

**Przerwanie syntezy (Barge-in / Interruption).** Gdy użytkownik wtrąci się (zacznie mówić), podczas gdy bot wciąż odtwarza odpowiedź, system musi natychmiast: (a) wykryć aktywność głosową użytkownika, (b) zatrzymać generowanie i odtwarzanie przez model TTS, (c) zresetować stan generowania LLM. Cała ta operacja musi zajść w czasie poniżej 100 ms, w przeciwnym razie użytkownik odniesie wrażenie, że bot go ignoruje.

**Protokół WebRTC i kodek Opus.** Standard przesyłania ramek audio o długości 20 ms, próbkowaniu 48 kHz i adaptacyjnej przepływności (8–128 kb/s). To podstawowy protokół w aplikacjach przeglądarkowych i mobilnych. Narzędzia takie jak LiveKit, Daily.co czy Pion stanowią fundament stosu technologicznego w 2026 roku.

**Bufor jittera (Jitter Buffer).** Pakiety sieciowe mogą docierać z opóźnieniem lub w niewłaściwej kolejności. Bufor jittera porządkuje i wyrównuje strumień pakietów. Zbyt mały rozmiar bufora powoduje utratę pakietów i trzaski (glicze), natomiast zbyt duży – wprowadza dodatkowe opóźnienia. Typowy rozmiar to 60–80 ms.

### Typowe problemy implementacyjne

- **Blokowanie wątków (GIL w Pythonie).** Uruchamianie ciężkich modeli głębokich w tym samym wątku może zablokować pętlę pobierania audio. Zawsze korzystaj z bibliotek audio z niskopoziomowymi callbackami w C (np. `sounddevice`, PortAudio, PyAudio) i deleguj przetwarzanie modeli do osobnych wątków/procesów.
- **Latencja resamplingu.** Konwersacja częstotliwości próbkowania (resampling) w locie dodaje 5–20 ms opóźnienia. Konfiguruj system tak, aby od razu rejestrować dźwięk w częstotliwości docelowej modelu, lub stosuj wydajne biblioteki o niskiej latencji (np. `soxr` lub filtry Polyphase).
- **Zimny start modelu TTS (warm-up delay).** Nawet wydajne modele syntezy, takie jak Kokoro, przy pierwszej próbie generowania potrzebują ok. 100–200 ms na zainicjowanie wag (warm-up). Utrzymuj model w pamięci (caching) i wykonaj jedno próbne (fikcyjne) wnioskowanie podczas startu kontenera.
- **AEC (Acoustic Echo Cancellation).** Bez aktywnego tłumienia echa, dźwięk generowany przez głośnik dociera z powrotem do mikrofonu, co powoduje, że system ASR transkrybuje własne wypowiedzi bota. Algorytm AEC3 z biblioteki WebRTC stanowi standard open-source w tej dziedzinie.

## Implementacja krok po kroku

### Krok 1: Implementacja bufora kołowego (Ring Buffer)

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

Pojemność określa maksymalny czas buforowania. Na przykład 32 000 próbek przy 16 kHz pozwala na przechowywanie 2 sekund nagrania.

### Krok 2: Bramkowanie za pomocą VAD

```python
def simple_energy_vad(frame, threshold=0.01):
    return sum(x * x for x in frame) / len(frame) > threshold ** 2
```

W zastosowaniach produkcyjnych zastąp powyższą heurystykę sprawdzonym modelem, np. Silero VAD:

```python
import torch
vad, _ = torch.hub.load("snakers4/silero-vad", "silero_vad")
is_speech = vad(torch.tensor(frame), 16000).item() > 0.5
```

### Krok 3: Strumieniowa transkrypcja ASR

Wnioskowanie z modelem Parakeet-CTC-0.6B przez bibliotekę NVIDIA NeMo:

```python
from nemo.collections.asr.models import EncDecCTCModelBPE
asr = EncDecCTCModelBPE.from_pretrained("nvidia/parakeet-ctc-0.6b")
# Parametry okna: chunk_ms=320 ms, look_ahead_ms=80 ms
for chunk in audio_stream():
    partial_text = asr.transcribe_streaming(chunk)
    print(partial_text, end="\r")
```

### Krok 4: Obsługa przerwania syntezy (Barge-in)

```python
class Dialog:
    def __init__(self):
        self.tts_task = None

    def on_user_speech(self, frame):
        if self.tts_task and not self.tts_task.done():
            self.tts_task.cancel()   # wykryto wtrącenie się (barge-in)
        # przekazanie ramki audio do strumieniowego ASR

    def on_final_user_utterance(self, text):
        self.tts_task = asyncio.create_task(self.reply(text))

    async def reply(self, text):
        async for tts_chunk in llm_then_tts(text):
            speaker.write(tts_chunk)
```

Kod ten opiera się na asynchronicznej obsłudze wejścia/wyjścia (asyncio) oraz możliwości natychmiastowego anulowania zadań. W potokach WebRTC standardowym sposobem na przerwanie strumienia audio jest zatrzymanie odtwarzania ścieżki.

## Rekomendowane technologie (2026)

| Warstwa | Rekomendowana technologia |
|------|------|
| Transport sieciowy | LiveKit (WebRTC) lub Pion (Go) |
| Detekcja mowy (VAD) | Silero VAD 4.0 |
| Transkrypcja (ASR) | Parakeet-CTC-0.6B lub Whisper-Streaming |
| Niska latencja LLM (Time-to-First-Token) | Dostawcy Groq, Cerebras lub instancja vLLM ze strumieniowaniem |
| Synteza mowy (TTS) | Kokoro lub ElevenLabs Turbo v2.5 |
| Tłumienie echa (AEC) | WebRTC AEC3 |
| Natywny model konwersacyjny (end-to-end) | OpenAI Realtime API lub Moshi |

## Typowe pułapki

- **Zbyt duże bufory wejściowe.** Rozmiar bufora na wejściu bezpośrednio określa minimalną latencję systemu. Staraj się schodzić z wielkością buforów do niezbędnego minimum (np. 20 ms).
- **Brak priorytetyzacji wątków audio.** Callbacki audio muszą działać na wątkach o wysokim priorytecie (high priority / real-time priority). W przeciwnym razie obciążenie procesora przez interfejs użytkownika lub model LLM spowoduje trzaski i przerwy w dźwięku.
- **Zbyt małe pakiety wyjściowe TTS.** Przesyłanie do głośnika fragmentów audio o długości poniżej 200 ms wywołuje słyszalne zniekształcenia na łączeniach ramek wokodera. Optymalny rozmiar pakietu wyjściowego to ok. 320 ms.
- **Brak bufora jittera.** W sieciach publicznych pakiety rzadko docierają w idealnych odstępach czasu; brak bufora jittera prowadzi do ciągłego przerywania strumienia.
- **Brak izolacji błędów w pętli audio.** Procesy audio muszą być odporne na sporadyczne wyjątki (np. zgubiony pakiet sieciowy). Jeden błąd sieci nie może zawieszać całego potoku wątku.

## Zadanie do wykonania

Zapisz jako `outputs/skill-realtime-designer.md`. Zaprojektuj potok przetwarzania audio w czasie rzeczywistym z rozpisanym szczegółowo budżetem opóźnień (latencji) dla każdego etapu.

## Ćwiczenia

1. **Łatwe.** Uruchom skrypt `code/main.py`. Symuluje on bufor kołowy oraz prosty algorytm VAD oparty na energii sygnału. Wypisuje latencje poszczególnych etapów dla symulowanego 10-sekundowego strumienia.
2. **Średnie.** Wykorzystując bibliotekę `sounddevice`, napisz prostą pętlę zwrotną (audio loopback), która odczytuje sygnał z mikrofonu w oknach 20 ms i wypisuje w czasie rzeczywistym stan detekcji mowy (VAD).
3. **Trudne.** Zbuduj pełny, dwukierunkowy (full-duplex) potok za pomocą `aiortc`: przeglądarka → WebRTC → skrypt Python → WebRTC → przeglądarka. Zmierz pełną latencję (round-trip latency) poprzez nadanie krótkiego impulsu o częstotliwości 1 kHz.

## Kluczowe terminy

| Termin | Potoczne określenie | Co to naprawdę oznacza |
|------|-----------------|----------------------|
| Ring Buffer | Bufor kołowy | Struktura danych FIFO o stałym rozmiarze, służąca do przesyłania ramek audio między wątkami (często bez blokad w architekturze SPSC). |
| VAD | Detektor aktywności | Voice Activity Detection; moduł odróżniający mowę od ciszy lub szumów tła. |
| Streaming ASR | Strumieniowy ASR | Model automatycznego rozpoznawania mowy zwracający tekst w locie, posiadający minimalne okno analizy w przód (look-ahead). |
| Jitter Buffer | Bufor sieciowy | Kolejka stabilizująca strumień pakietów audio docierających przez sieć ze zmiennym opóźnieniem. |
| AEC | Acoustic Echo Cancellation | Algorytm tłumienia echa, który modeluje i odejmuje sygnał odtwarzany przez głośnik od sygnału rejestrowanego przez mikrofon. |
| Barge-in | Wtrącenie się | Sytuacja, w której użytkownik zaczyna mówić w trakcie wypowiedzi bota, co powinno skutkować natychmiastowym przerwaniem syntezy mowy. |
| Full-duplex | Dwukierunkowość | Możliwość jednoczesnej transmisji audio w obu kierunkach (użytkownik i bot mogą mówić w tym samym czasie). |

## Dalsze czytanie

- [Macháček et al. (2023). Simple and Efficient Whisper-Streaming](https://arxiv.org/abs/2307.14743) — technika strumieniowego wnioskowania z użyciem modelu Whisper.
- [Kyutai (2024). Moshi: a Speech-Text Duplex Large Language Model](https://kyutai.org/Moshi.pdf) — techniczna specyfikacja architektury pełnego dupleksu.
- [LiveKit Agents Framework](https://docs.livekit.io/agents/) — otwarta platforma do budowy i orkiestracji strumieniowych agentów AI.
- [snakers4/silero-vad Repository](https://github.com/snakers4/silero-vad) — wiodąca lekka biblioteka VAD do celów produkcyjnych.
- [WebRTC Acoustic Echo Canceller (AEC3) Module](https://webrtc.googlesource.com/src/+/main/modules/audio_processing/aec3/) — kod źródłowy i dokumentacja modułu tłumienia echa z biblioteki WebRTC.
