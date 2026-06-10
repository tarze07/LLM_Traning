# Wykrywanie aktywności głosowej i wykonywanie tur — Silero, Cobra i sztuczka Flush

> Każdy agent głosowy żyje lub umiera w oparciu o dwie decyzje: czy użytkownik mówi teraz i czy już skończył? VAD odpowiada na pierwsze pytanie. Wykrywanie skrętu (VAD + kac ciszy + model semantycznego punktu końcowego) odpowiada na drugie pytanie. Jeśli się pomylisz, Twój asystent albo odetnie użytkowników, albo nigdy się nie zamknie.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 6 · 11 (dźwięk w czasie rzeczywistym), faza 6 · 12 (Asystent głosowy)
**Czas:** ~45 minut

## Problem

Trzy różne decyzje, które agent głosowy podejmuje co 20 ms:

1. **Czy to mowa ramowa?** — VAD. Binarny, na klatkę.
2. **Czy użytkownik rozpoczął nową wypowiedź?** — wykrywanie początku.
3. **Czy użytkownik skończył?** — wskazywanie końca (zakrętu).

Naiwna odpowiedź (próg energii) nie sprawdza się w przypadku żadnego hałasu – ruchu ulicznego, klawiatur, bełkotu tłumu. Odpowiedź na rok 2026: Silero VAD (otwarty, dogłębnie wyuczony) + model wykrywania skrętu (semantyczne punkty końcowe) + kac ciszy skalibrowany przez VAD.

## Koncepcja

![Kaskada VAD: energia → Silero → wykrywacz skrętu → sztuczka z kolorem](../assets/vad-turn-taking.svg)

### Trójpoziomowa kaskada VAD

**Poziom 1: bramka energetyczna.** Najtańszy. Próg RMS przy -40 dBFS. Filtruje oczywistą ciszę, ale aktywuje każdy hałas powyżej progu.

**Poziom 2: Silero VAD** (2020–2026, MIT). Parametry 1M. Przeszkolony w zakresie ponad 6000 języków. Działa w ~1 ms na fragment 30 ms w pojedynczym wątku procesora. 87,7% TPR przy 5% FPR. Wartość domyślna typu open source.

**Poziom 3: semantyczny detektor skrętu.** Model detekcji skrętu w LiveKit (2024-2026) lub Twój własny mały klasyfikator. Odróżnia „pauzę w połowie zdania” od „zakończenia rozmowy”. Używa kontekstu językowego (intonacja + ostatnie słowa), a nie tylko ciszy.

### Kluczowe parametry i ich wartości domyślne

- **Próg.** Silero podaje prawdopodobieństwo; klasyfikuj mowę na poziomie > 0,5 (domyślnie) lub > 0,3 (wrażliwość). Niższy próg = mniej klipów z pierwszym słowem, więcej wyników fałszywie pozytywnych.
- **Minimalny czas trwania mowy.** Odrzucaj mowę krótszą niż 250 ms — zwykle kaszel lub hałas krzesła.
- **Wycisz kaca (wskazując koniec).** Gdy VAD powróci do 0, odczekaj 500-800 ms przed ogłoszeniem końca tury. Za krótki → przerwać użytkownika. Za długo → powoduje powolne działanie.
- **Bufor przed filmem.** Zachowaj dźwięk przez 300–500 ms przed uruchomieniem VAD. Zapobiega obcinaniu „hej”.

### Sztuczka z kolorem (Kyutai 2025)

Modele strumieniowe STT mają opóźnienie antycypacyjne (500 ms dla Kyutai STT-1B, 2,5 s dla STT-2.6B). Zwykle trzeba czekać tak długo po zakończeniu przemówienia na transkrypcję. Sztuczka z płukaniem: kiedy VAD uruchamia koniec mowy, **wysyła sygnał płukania do STT**, który wymusza natychmiastowe wyjście. STT przetwarza ~4 razy w czasie rzeczywistym, więc bufor 500 ms kończy się w ~125 ms.

Od końca do końca: 125 ms VAD + Flush STT = opóźnienie konwersacji.

### Porównanie VAD 2026

| VAD | TPR przy 5% FPR | Opóźnienie | Licencja |
|---------|--------------|---------|---------|
| WebRTC VAD (Google, 2013) | 50,0% | 30 ms | BSD |
| Silero VAD (2020-2026) | 87,7% | ~1 ms | MIT |
| Cobra VAD (Picovoice) | 98,9% | ~1 ms | komercyjny |
| segmentacja pyannote | 95% | ~10 ms | w stylu MIT |

Silero jest właściwym ustawieniem domyślnym. Cobra to ulepszenie zgodności/dokładności. W produkcji w 2026 r. nie ma miejsca na VAD zasilany wyłącznie energią.

## Zbuduj to

### Krok 1: brama energetyczna

```python
def energy_vad(chunk, threshold_dbfs=-40.0):
    rms = (sum(x * x for x in chunk) / len(chunk)) ** 0.5
    dbfs = 20.0 * math.log10(max(rms, 1e-10))
    return dbfs > threshold_dbfs
```

### Krok 2: Silero VAD w Pythonie

```python
from silero_vad import load_silero_vad, get_speech_timestamps

vad = load_silero_vad()
audio = torch.tensor(waveform_16k, dtype=torch.float32)
segments = get_speech_timestamps(
    audio, vad, sampling_rate=16000,
    threshold=0.5,
    min_speech_duration_ms=250,
    min_silence_duration_ms=500,
    speech_pad_ms=300,
)
for s in segments:
    print(f"{s['start']/16000:.2f}s - {s['end']/16000:.2f}s")
```

### Krok 3: maszyna stanu końcowego

```python
class TurnDetector:
    def __init__(self, silence_hangover_ms=500, min_speech_ms=250):
        self.state = "idle"
        self.speech_ms = 0
        self.silence_ms = 0
        self.silence_hangover_ms = silence_hangover_ms
        self.min_speech_ms = min_speech_ms

    def update(self, is_speech, chunk_ms=20):
        if is_speech:
            self.speech_ms += chunk_ms
            self.silence_ms = 0
            if self.state == "idle" and self.speech_ms >= self.min_speech_ms:
                self.state = "speaking"
                return "START"
        else:
            self.silence_ms += chunk_ms
            if self.state == "speaking" and self.silence_ms >= self.silence_hangover_ms:
                self.state = "idle"
                self.speech_ms = 0
                return "END"
        return None
```

### Krok 4: szkielet triku z kolorem

```python
def flush_on_end(stt_client, audio_buffer):
    stt_client.send_audio(audio_buffer)
    stt_client.send_flush()
    return stt_client.recv_transcript(timeout_ms=150)
```

Aby to zadziałało, STT (Kyutai, Deepgram, AssemblyAI) musi obsługiwać kolor. Strumieniowanie szeptów nie — opiera się na blokach i zawsze czeka na fragmenty.

## Użyj tego

| Sytuacja | Wybór VAD |
|----------|-----------|
| Otwarte, szybkie, ogólne | Silero VAD |
| Komercyjne call center | Kobra VAD |
| Na urządzeniu (telefonie) | Silero VAD ONNX |
| Badania / diaryzacja | segmentacja pyannote |
| Rezerwa o zerowej zależności | WebRTC VAD (starsza wersja) |
| Potrzebujesz jakości kończącej turę | Silero + LiveKit wykrywacz skrętu warstwowy |

Ogólna zasada: nigdy nie wysyłaj VAD zasilanego wyłącznie energią, chyba że naprawdę nie masz innej opcji.

## Pułapki

- **Naprawiono próg.** Działa w ciszy, nie działa w hałasie. Wykonaj kalibrację na urządzeniu lub przełącz się na Silero.
- **Zbyt krótka cisza na kacu.** Agent przerywa w połowie zdania. Optymalny czas dla mowy konwersacyjnej wynosi 500–800 ms.
- **Zbyt długi kac.** Czujesz się ospały. Test A/B z docelowymi użytkownikami.
- **Brak bufora przed filmem.** Utrata dźwięku użytkownika po pierwszych 200–300 ms. Zawsze utrzymuj rolkę przed filmem.
- **Ignorowanie semantycznego punktu końcowego.** „Hmm, pozwól mi pomyśleć…” zawiera długie pauzy. Użytkownicy nienawidzą, gdy ktoś ich odcina w połowie myśli. Użyj czujnika skrętu LiveKit lub podobnego.

## Wyślij to

Zapisz jako `outputs/skill-vad-tuner.md`. Wybierz model VAD, próg, kaca, pre-roll i strategię wykrywania skrętu dla obciążenia pracą.

## Ćwiczenia

1. **Łatwe.** Uruchom `code/main.py`. Symuluje sekwencję mowy + ciszy + mowy + kaszlu i testuje trzy poziomy VAD.
2. **Średni.** Zainstaluj `silero-vad`, przetwórz 5-minutowe nagranie, dostosuj próg, aby zminimalizować zarówno klipy pierwszego słowa, jak i fałszywe wyzwalacze. Zgłoś precyzję/przypomnienie.
3. **Trudne.** Zbuduj mini wykrywacz skrętu: Silero VAD + 3-warstwowy MLP na osadzonych 10 ostatnich słowach (użyj transformatorów zdań). Trenuj na ręcznie oznaczonym zbiorze danych końcowych. Pokonaj Silero-tylko o 10% F1.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| VAD | Detektor głosu | Binarny na klatkę: czy to mowa? |
| Wykrywanie skrętu | Punkt końcowy | VAD + cisza-kac + semantyczny punkt końcowy. |
| Wycisz kaca | Czekanie po przemowie | Czas poczekać przed ogłoszeniem końca tury; 500-800 ms. |
| Przed filmem | Bufor przed mową | Zachowaj dźwięk 300–500 ms przed uruchomieniem VAD. |
| Sztuczka z kolorem | Hack Kyutai | VAD → Flush-STT → 125 ms zamiast 500 ms opóźnienia. |
| Semantyczny punkt końcowy | – Czy chcieli się zatrzymać? | Klasyfikator ML, który analizuje słowa, a nie tylko ciszę. |
| TPR @ FPR 5% | Punkt ROC | Standardowy test porównawczy VAD; 87,7% dla Silero, 50% dla WebRTC. |

## Dalsze czytanie

- [Silero VAD](https://github.com/snakers4/silero-vad) — referencyjny otwarty VAD.
- [Picovoice Cobra VAD](https://picovoice.ai/products/cobra/) — lider w zakresie dokładności komercyjnej.
- [Kyutai — sztuczka z wyłączeniem wyciszenia i spłukiwaniem](https://kyutai.org/stt) — sztuczka inżynieryjna poniżej 200 ms.
- [LiveKit — wykrywanie skrętów](https://docs.livekit.io/agents/logic/turns/) — semantyczny punkt końcowy w produkcji.
– [WebRTC VAD](https://webrtc.googlesource.com/src/) – starsza wersja bazowa.
- [segmentacja pyannote](https://github.com/pyannote/pyannote-audio) — segmentacja na poziomie diaryzacji.