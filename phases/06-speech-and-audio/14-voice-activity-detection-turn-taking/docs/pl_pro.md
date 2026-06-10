# Detekcja aktywności głosowej (VAD) i przekazywanie tury (Turn-Taking) — Silero, Cobra oraz technika Flush

> Każdy asystent głosowy zależy od dwóch kluczowych decyzji: czy użytkownik mówi w tym momencie oraz czy zakończył już swoją wypowiedź? Detekcja VAD odpowiada na pierwsze pytanie. Za drugie odpowiada moduł wykrywania tury (VAD + czas podtrzymania + semantyczny detektor końca wypowiedzi). Błędy na tym etapie powodują, że asystent albo przerywa wypowiedź użytkownika, albo nigdy nie przestaje słuchać.

**Typ:** Kompendium  
**Języki:** Python  
**Wymagania wstępne:** Faza 6 · 11 (Dźwięk w czasie rzeczywistym), Faza 6 · 12 (Projektowanie potoku asystenta głosowego)  
**Czas:** ~45 minut  

## Problem

W potoku asystenta głosowego co 20 ms podejmowane są trzy kluczowe decyzje:

1. **Czy dana ramka (frame) zawiera mowę?** — zadanie dla detektora VAD (decyzja binarna na poziomie pojedynczej ramki).
2. **Czy użytkownik rozpoczął nową wypowiedź?** — detekcja początku mowy (speech onset).
3. **Czy użytkownik zakończył swoją wypowiedź?** — detekcja końca wypowiedzi (turn detection / endpointing).

Uproszczone metody oparte o próg energetyczny sygnału (energy threshold) zupełnie zawodzą w zaszumionym otoczeniu (np. ruch uliczny, stukanie klawiatury, gwar rozmów w tle). Standard produkcyjny w 2026 roku obejmuje: model Silero VAD (otwarte, głębokie sieci neuronowe) + semantyczny model detekcji tury + czas podtrzymania (hangover) kalibrowany na podstawie opóźnień VAD.

## Koncepcja

![Kaskada detekcji tury: bramkowanie energetyczne → Silero VAD → semantyczny detektor tur → technika Flush (szybkie czyszczenie bufora)](../assets/vad-turn-taking.svg)

### Trójstopniowy potok detekcji tury

**Poziom 1: Bramka energetyczna (Energy Gate).** Najtańsze obliczeniowo rozwiązanie. Wykorzystuje próg RMS na poziomie ok. -40 dBFS. Odcina oczywistą ciszę, ale przepuszcza wszelkie głośniejsze zakłócenia i szumy tła.

**Poziom 2: Silero VAD (2020–2026, licencja MIT).** Kompaktowy model (1M parametrów) wytrenowany na bazie nagrań z ponad 6000 języków. Działa w czasie ok. 1 ms dla ramki 30 ms na pojedynczym wątku CPU, osiągając 87.7% TPR (True Positive Rate) przy zaledwie 5% FPR (False Positive Rate). Stanowi domyślny standard open-source.

**Poziom 3: Semantyczny detektor tur (Semantic Turn Detector).** Moduł wykrywania tury (np. z biblioteki LiveKit lub autorski klasyfikator). Pozwala na odróżnienie naturalnej pauzy wewnątrz zdania (zawieszenie głosu) od intencji zakończenia wypowiedzi. Analizuje kontekst językowy (intonacja, struktura gramatyczna, ostatnie wypowiedziane słowa), a nie tylko fizyczną ciszę.

### Kluczowe parametry konfiguracyjne

- **Próg czułości (Threshold).** Silero zwraca prawdopodobieństwo obecności mowy. Klasyfikuj sygnał jako mowę przy wartości > 0.5 (domyślnie) lub > 0.3 (wysoka czułość). Niższy próg zapobiega ucinaniu pierwszych słów (first-word clipping), ale zwiększa liczbę fałszywych alarmów (false positives).
- **Minimalny czas trwania mowy (Min Speech Duration).** Ignoruj fragmenty mowy krótsze niż 250 ms – najczęściej reprezentują one kaszlnięcia, chrząknięcia lub przesunięcia krzesła.
- **Czas podtrzymania ciszy (Hangover Time).** Gdy prawdopodobieństwo VAD spada do zera, odczekaj 500–800 ms przed zadeklarowaniem końca tury użytkownika. Zbyt krótki czas powoduje przerywanie wypowiedzi użytkownika, natomiast zbyt długi – spowalnia czas reakcji asystenta.
- **Bufor pre-roll.** Buforowanie 300–500 ms audio przed faktyczną aktywacją VAD, co zapobiega ucinaniu początku pierwszego wypowiedzianego słowa (np. „Hej”).

### Technika Flush (szybkie opróżnianie bufora)

Strumieniowe modele ASR cechują się pewnym opóźnieniem związanym z oknem analizy w przód (look-ahead latency), wynoszącym od 500 ms do nawet 2.5 s. Normalnie system musiałby czekać ten czas po zakończeniu wypowiedzi na finalną transkrypcję. **Technika Flush polega na wysłaniu sygnału czyszczenia bufora do modelu STT w momencie, gdy VAD wykryje koniec wypowiedzi**. Wymusza to na modelu natychmiastowe wyplucie przetworzonego tekstu w czasie ok. 125 ms.

W rezultacie latencja end-to-end wynosi zaledwie 125 ms (VAD) + czas przetwarzania Flush STT.

### Porównanie detektorów VAD (2026)

| Detektor VAD | TPR przy 5% FPR | Latencja | Licencja |
|---------|--------------|---------|---------|
| WebRTC VAD (Google, 2013) | 50,0% | 30 ms | BSD |
| Silero VAD (2020-2026) | 87,7% | ~1 ms | MIT |
| Cobra VAD (Picovoice) | 98,9% | ~1 ms | Komercyjna |
| pyannote.audio (segmentacja) | 95,0% | ~10 ms | MIT-like |

Silero VAD stanowi optymalny wybór domyślny. Cobra VAD to świetne rozwiązanie komercyjne o wyższej precyzji. W systemach produkcyjnych w 2026 roku nie ma miejsca na detektory VAD bazujące wyłącznie na energii sygnału.

## Implementacja krok po kroku

### Krok 1: Bramkowanie energetyczne (baseline)

```python
import math

def energy_vad(chunk, threshold_dbfs=-40.0):
    rms = (sum(x * x for x in chunk) / len(chunk)) ** 0.5
    dbfs = 20.0 * math.log10(max(rms, 1e-10))
    return dbfs > threshold_dbfs
```

### Krok 2: Wdrożenie Silero VAD w Pythonie

```python
import torch
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

### Krok 3: Maszyna stanów (State Machine) dla detekcji tury

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

### Krok 4: Koncepcja techniki Flush

```python
def flush_on_end(stt_client, audio_buffer):
    stt_client.send_audio(audio_buffer)
    stt_client.send_flush()
    return stt_client.recv_transcript(timeout_ms=150)
```

Aby to zadziałało, wybrany silnik STT (np. Deepgram, AssemblyAI) musi obsługiwać zdarzenie wymuszonego przetwarzania (flush). Strumieniowe implementacje oparte na stałych oknach (np. standardowy Whisper) nie obsługują tej metody i zawsze czekają na dopełnienie okna czasowego.

## Sugerowane rozwiązania (2026)

| Scenariusz | Rekomendowany wybór VAD |
|----------|-----------|
| Otwarte, szybkie systemy ogólne | Silero VAD |
| Komercyjne systemy call center | Cobra VAD |
| Urządzenia mobilne i wbudowane (edge) | Silero VAD w formacie ONNX |
| Prace badawcze / diaryzacja mówców | pyannote.audio (segmentacja) |
| Brak dodatkowych zależności (legacy) | WebRTC VAD |
| Wymagana wysoka kultura konwersacji | Silero VAD + semantyczny detektor tur (np. LiveKit) |

## Typowe pułapki

- **Sztywne progi w zmiennych warunkach.** Systemy oparte na progach energii działają świetnie w wyciszonym biurze, ale przestają działać na ulicy lub w kawiarni. W takich scenariuszach zawsze wdrażaj neuronowe modele VAD (np. Silero).
- **Zbyt krótki czas podtrzymania (hangover).** Asystent przerywa wypowiedź użytkownika przy najmniejszej pauzie na zaczerpnięcie powietrza. Dla mowy potocznej czas podtrzymania powinien wynosić od 500 do 800 ms.
- **Zbyt długi czas podtrzymania.** Powoduje, że asystent wydaje się powolny i ospały w reakcjach. Kalibruj ten parametr za pomocą testów A/B na grupie użytkowników.
- **Brak bufora pre-roll.** Powoduje ucinanie początku wypowiedzi (np. powitania „Hej”). Zawsze przechowuj w buforze kołowym ostatnie 200–300 ms dźwięku przed aktywacją VAD.
- **Ignorowanie semantyki wypowiedzi.** Pauzy typu „Yyy... daj mi pomyśleć” mogą zostać zinterpretowane jako koniec tury. Zastosowanie dodatkowego, semantycznego detektora tur chroni przed przedwczesnym przerywaniem myśli użytkownika.

## Zadanie do wykonania

Zapisz jako `outputs/skill-vad-tuner.md`. Dobierz model VAD, próg czułości, parametry pre-roll i hangover oraz strategię detekcji tury dla zadanego scenariusza wdrożeniowego.

## Ćwiczenia

1. **Łatwe.** Uruchom skrypt `code/main.py`. Symuluje on sekwencję mowa + cisza + mowa + kaszel i testuje zachowanie trzech różnych konfiguracji detektorów VAD.
2. **Średnie.** Zainstaluj bibliotekę `silero-vad`, przetwórz 5-minutowe nagranie i dobierz próg czułości tak, aby zminimalizować zjawisko ucinania słów oraz liczbę fałszywych alarmów (false positives). Podaj wartości wskaźników Precision i Recall.
3. **Trudne.** Zaprojektuj uproszczony detektor tur: Silero VAD + 3-warstwowy model MLP pobierający wektory osadzeń (embeddings) ostatnich 10 słów wypowiedzi (np. z użyciem biblioteki sentence-transformers). Przetestuj model i wykaż poprawę F1-score o 10% w stosunku do samego detektora VAD.

## Kluczowe terminy

| Termin | Potoczne określenie | Co to naprawdę oznacza |
|------|-----------------|----------------------|
| VAD | Detektor aktywności | Voice Activity Detection; binarna decyzja dla każdej ramki, określająca obecność mowy ludzkiej. |
| Endpointing | Wykrywanie końca wypowiedzi | Decyzja logiczna o zakończeniu tury użytkownika bazująca na sygnale VAD, czasie podtrzymania i analizie semantycznej. |
| Hangover | Czas podtrzymania | Czas oczekiwania systemu po wykryciu ciszy przez VAD przed uznaniem, że użytkownik przestał mówić (zazwyczaj 500-800 ms). |
| Pre-roll buffer | Bufor wstępny | Przechowywanie ostatnich 300–500 ms audio przed wykryciem mowy w celu zachowania pierwszych zgłosek. |
| Flush | Opróżnianie bufora | Wymuszenie na strumieniowym modelu STT natychmiastowego przetworzenia dotychczas zgromadzonego dźwięku po wykryciu końca mowy przez VAD. |
| Semantic Endpointing | Semantyczny koniec wypowiedzi | Zastosowanie modeli NLP/ML do oceny struktury słów w celu podjęcia decyzji o przekazaniu tury (odróżnienie pauzy od kropki). |

## Dalsze czytanie

- [Silero VAD GitHub Repository](https://github.com/snakers4/silero-vad) — oficjalne wdrożenie i wagi modelu Silero.
- [Picovoice Cobra VAD](https://picovoice.ai/products/cobra/) — specyfikacja i testy wydajnościowe komercyjnego detektora Cobra.
- [LiveKit Turn Detection Logic](https://docs.livekit.io/agents/logic/turns/) — dokumentacja i logika produkcyjnego detektora tur.
- [pyannote.audio Speaker Diarization and Segmentation](https://github.com/pyannote/pyannote-audio) — biblioteka pyannote i wdrożenia modeli segmentacji.
