# Transformatory audio — architektura szeptów

> Dźwięk jest obrazem częstotliwości w czasie. Whisper to ViT, który zjada spektrogramy Mel i odpowiada.

**Typ:** Ucz się
**Języki:** Python
**Warunki wstępne:** Faza 7 · 05 (Pełny transformator), Faza 7 · 08 (enkoder-dekoder), Faza 7 · 09 (ViT)
**Czas:** ~45 minut

## Problem

Przed Whisperem (OpenAI, Radford i in. 2022) najnowocześniejsze automatyczne rozpoznawanie mowy (ASR) oznaczało wav2vec 2.0 i HuBERT — samonadzorowane ekstraktory cech i precyzyjnie dostrojona głowica. Wysokiej jakości, drogie potoki danych, kruche domeny. Wielojęzyczne rozpoznawanie mowy wymagało oddzielnych modeli dla każdej rodziny języków.

Whisper postawił trzy zakłady:

1. **Trenuj we wszystkim.** 680 000 godzin słabo oznakowanych nagrań audio pobranych z Internetu w 97 językach. Brak czystego korpusu akademickiego. Brak etykiet fonemowych.
2. **Pojedynczy model wielozadaniowy.** Jeden dekoder przeszkolony wspólnie w zakresie transkrypcji, tłumaczenia, wykrywania aktywności głosowej, identyfikatora języka i znacznika czasu za pomocą tokenów zadań.
3. **Standardowy transformator enkoder-dekoder.** Koder zużywa spektrogramy log-mel. Dekoder generuje tokeny tekstowe w sposób autoregresyjny. Żadnego wokodera, żadnego CTC, żadnego HMM.

Wynik: Whisper Large-v3 jest odporny na akcenty, szumy i języki, które nie mają żadnych czystych danych. Jest to domyślny interfejs mowy dla każdego asystenta głosowego typu open source i większości komercyjnych w 2026 roku.

## Koncepcja

![Potok szeptów: audio → mel → koder → dekoder → tekst](../assets/whisper.svg)

### Krok 1 — ponowne próbkowanie + okno

Dźwięk przy 16 kHz. Klip/pad do 30 sekund. Oblicz spektrogram log-mel: 80 pojemników mel, krok 10 ms → ~ 3000 klatek × 80 funkcji. To jest „obraz wejściowy”, który widzi Whisper.

### Krok 2 — rdzeń splotowy

Dwie warstwy Conv1D z jądrem 3 i krokiem 2 zmniejszają liczbę 3000 klatek do 1500. Zmniejsza o połowę długość sekwencji bez dodawania wielu parametrów.

### Krok 3 — koder

24-warstwowy (dla dużych) koder transformatorowy w ponad 1500 krokach czasowych. Sinusoidalne kodowanie pozycyjne, samouważność, GELU FFN. Tworzy 1500 × 1280 stanów ukrytych.

### Krok 4 — dekoder

24-warstwowy dekoder transformatorowy. Autoregresywnie generuje tokeny ze słownika BPE, który jest nadzbiorem GPT-2 z kilkoma specjalnymi tokenami specyficznymi dla dźwięku.

### Krok 5 — żetony zadań

Podpowiedź dekodera zaczyna się od żetonów kontrolnych, które mówią modelowi, co ma robić:

```
<|startoftranscript|>  <|en|>  <|transcribe|>  <|0.00|>
```

lub

```
<|startoftranscript|>  <|fr|>  <|translate|>   <|0.00|>
```

Modelka została przeszkolona w oparciu o tę konwencję. Kontrolujesz zadanie za pomocą prefiksu. Odpowiednik strojenia instrukcji z 2026 r., ale zastosowany do mowy.

### Krok 6 — wyjście

Wyszukiwanie wiązki (szerokość 5) z progiem log-prob. Sygnatury czasowe są przewidywane co 0,02 sekundy dźwięku, jeśli nie ma tokena `<|notimestamps|>`.

### Rozmiary szeptów

| Modelka | Parametry | Warstwy | d_model | Głowy | VRAM (fp16) |
|-------|--------|--------|--------|-------|------------|
| Mały | 39M | 4 | 384 | 6 | ~1 GB |
| Baza | 74M | 6 | 512 | 8 | ~1 GB |
| Mały | 244M | 12 | 768 | 12 | ~2 GB |
| Średni | 769M | 24 | 1024 | 16 | ~5 GB |
| Duży | 1550M | 32 | 1280 | 20 | ~10 GB |
| Duży-v3 | 1550M | 32 | 1280 | 20 | ~10 GB |
| Duże-v3-turbo | 809M | 32 | 1280 | 20 | ~6 GB (dekoder 4-warstwowy) |

Large-v3-turbo (2024) skrócił dekoder z 32 warstw do 4,8 razy szybszego dekodowania z regresją punktową <1 WER. Dzięki temu odblokowaniu prędkości dekodowania w 2026 r. Whisper-turbo stanie się domyślnym rozwiązaniem dla agentów głosowych działających w czasie rzeczywistym.

### Czego Whisper nie robi

- Brak diaryzacji (kto mówi). W tym celu sparuj z pyannote.
- Brak natywnego przesyłania strumieniowego w czasie rzeczywistym - naprawiono 30-sekundowe okno. Nowoczesne opakowania (`faster-whisper`, `WhisperX`) przyspieszają przesyłanie strumieniowe przez VAD + nakładanie się.
- Brak długiego kontekstu trwającego dłużej niż 30 s bez zewnętrznego fragmentowania. Sprawdza się dobrze w praktyce, ponieważ mowa ludzka rzadko potrzebuje do transkrypcji kontekstu dalekiego zasięgu.

### Krajobraz 2026

| Zadanie | Modelka | Notatki |
|------|-------|------|
| angielski ASR | Szept-turbo, Moonshine | Moonshine jest 4× szybszy na krawędzi |
| Wielojęzyczny ASR | Whisper-large-v3 | 97 języków |
| Streaming ASR | szybszy szept + VAD | Osiągalne docelowe opóźnienia 150 ms |
| TTS | Piper, XTTS-v2, Kokoro | Wzór kodera-dekodera, ale w kształcie szeptu |
| Dźwięk + język | AudioLM, BezszwoweM4T | Tokeny tekstowe + tokeny audio w jednym transformatorze |

## Zbuduj to

Zobacz `code/main.py`. Nie szkolimy Whispera — budujemy potok spektrogramu log-mel + formater podpowiedzi tokenu zadania. To są części, których faktycznie dotykasz podczas produkcji.

### Krok 1: synteza dźwięku

Wygeneruj 1-sekundową falę sinusoidalną przy 440 Hz próbkowaną przy 16 kHz. 16 000 próbek.

### Krok 2: spektrogram log-mel (uproszczony)

Spektrogram pełnego melu wymaga FFT. Wykonujemy uproszczoną wersję kadrowania + energia na klatkę, która pokazuje potok bez wymagania `librosa`:

```python
def frame_signal(x, frame_size=400, hop=160):
    frames = []
    for start in range(0, len(x) - frame_size + 1, hop):
        frames.append(x[start:start + frame_size])
    return frames
```

Ramka = 25 ms, przeskok = 10 ms. Pasuje do okna Whisper. Energia na klatkę oznacza pojemniki mel w pedagogice.

### Krok 3: pad do 30 s

Whisper zawsze przetwarza fragmenty 30-sekundowe. Dopasuj (lub przytnij) spektrogram do 3000 klatek.

### Krok 4: zbuduj tokeny podpowiedzi

```python
def whisper_prompt(lang="en", task="transcribe", timestamps=True):
    tokens = ["<|startoftranscript|>", f"<|{lang}|>", f"<|{task}|>"]
    if not timestamps:
        tokens.append("<|notimestamps|>")
    return tokens
```

To jest cała powierzchnia sterowania zadaniem. Prefiks składający się z 4 żetonów.

## Użyj tego

```python
import whisper
model = whisper.load_model("large-v3-turbo")
result = model.transcribe("meeting.wav", language="en", task="transcribe")
print(result["text"])
print(result["segments"][0]["start"], result["segments"][0]["end"])
```

Szybszy, kompatybilny z OpenAI:

```python
from faster_whisper import WhisperModel
model = WhisperModel("large-v3-turbo", compute_type="int8_float16")
segments, info = model.transcribe("meeting.wav", vad_filter=True)
for s in segments:
    print(f"{s.start:.2f} - {s.end:.2f}: {s.text}")
```

**Kiedy wybrać Whisper w 2026 roku:**

- Wielojęzyczny ASR w jednym modelu.
- Solidna transkrypcja hałaśliwego, zróżnicowanego dźwięku.
- Badania/prototyp ASR — najszybszy punkt wyjścia.

**Kiedy wybrać coś innego:**

- Przesyłanie strumieniowe na krawędzi z bardzo niskim opóźnieniem — Moonshine pokonuje Whisper w dopasowanej jakości.
- Sztuczna inteligencja konwersacyjna w czasie rzeczywistym wymagająca <200 ms — dedykowana funkcja ASR do przesyłania strumieniowego.
- Diaryzacja głośników — Whisper tego nie robi; włącz pyannote.

## Wyślij to

Zobacz `outputs/skill-asr-configurator.md`. Umiejętność wybiera model ASR, parametry dekodowania i potok przetwarzania wstępnego dla nowej aplikacji mowy.

## Ćwiczenia

1. **Łatwe.** Uruchom `code/main.py`. Sprawdź, czy liczba klatek dla 1-sekundowego sygnału przy 16 kHz ze skokiem 10 ms wynosi ~100 klatek. Przez 30 sekund: ~3000 klatek.
2. **Średni.** Zbuduj pełny spektrogram log-mel przy użyciu `numpy.fft`. Sprawdź, czy pojemniki 80 Mel pasują do `librosa.feature.melspectrogram(n_mels=80)` w zakresie błędu numerycznego.
3. **Trudne.** Zaimplementuj wnioskowanie o strumieniowaniu: podziel audio na 10-sekundowe okna z 2-sekundowym nałożeniem, uruchom Whisper na każdym fragmencie, połącz transkrypcje. Zmierz współczynnik błędów słownych w porównaniu z pojedynczym przebiegiem na 5-minutowej próbce podcastu.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Spektrogram Mela | „Obraz dźwiękowy” | Reprezentacja 2D: przedziały częstotliwości na jednej osi, ramy czasowe na drugiej; energia skalowana logarytmicznie na ogniwo. |
| Log-mel | „Co widzi szept” | Spektrogram Mel przeszedł przez log; zbliżony do ludzkiego postrzegania głośności. |
| Rama | „Jednorazowy kawałek” | Okno próbek 25 ms; nakładają się na siebie w odstępie 10 ms. |
| Żeton zadania | „Przedrostek monitu o mowę” | Specjalne tokeny, takie jak `<\|transcribe\|>` / `<\|translate\|>` w znaku zachęty dekodera. |
| Wykrywanie aktywności głosowej (VAD) | „Znajdź mowę” | Brama usuwająca ciszę przed ASR; znacząco tnie koszty. |
| CTC | „Konekcjonistyczna klasyfikacja czasowa” | Klasyczna strata ASR dla treningu bez wyrównania; Whisper NIE używa tego. |
| Szept-turbo | „Mały dekoder, pełny koder” | koder Large-v3 + dekoder 4-warstwowy; 8x szybsze dekodowanie. |
| Szybszy szept | „Opakowanie produkcyjne” | Ponowna implementacja CTranslate2; kwantyzacja int8; 4 razy szybciej niż referencja OpenAI. |

## Dalsze czytanie

- [Radford i in. (2022). Solidne rozpoznawanie mowy dzięki słabemu nadzorowi na dużą skalę](https://arxiv.org/abs/2212.04356) – artykuł dotyczący szeptów.
- [Repozytorium OpenAI Whisper](https://github.com/openai/whisper) — kod referencyjny + wagi modeli. Przeczytaj `whisper/model.py`, aby zobaczyć rdzeń Conv1D + koder + dekoder od góry do dołu w ~400 liniach.
- [OpenAI Whisper — `whisper/decoding.py`](https://github.com/openai/whisper/blob/main/whisper/decoding.py) — logika wyszukiwania wiązki + tokenu zadania opisana w krokach 5–6 jest tutaj; 500 linii, w pełni czytelne.
- [Baevski i in. (2020). wav2vec 2.0: Ramy samonadzorowanego uczenia się reprezentacji mowy](https://arxiv.org/abs/2006.11477) — prekursor; nadal funkcje SOTA w niektórych ustawieniach.
- [SYSTRAN/faster-whisper](https://github.com/SYSTRAN/faster-whisper) — opakowanie produkcyjne, 4 razy szybsze niż referencja.
- [Jia i in. (2024). Moonshine: rozpoznawanie mowy w przypadku transkrypcji na żywo i poleceń głosowych](https://arxiv.org/abs/2410.15608) — ASR przyjazny dla krawędzi 2024, w kształcie szeptu, ale mniejszy.
- [Blog HuggingFace — „Dopracuj szept dla wielojęzycznego ASR z 🤗 Transformers”](https://huggingface.co/blog/fine-tune-whisper) — kanoniczny przepis na dostrajanie, w tym preprocesor spektrogramu mel i obsługa tokenów-znaczników czasowych.
- [HuggingFace `modeling_whisper.py`](https://github.com/huggingface/transformers/blob/main/src/transformers/models/whisper/modeling_whisper.py) — pełna implementacja (koder, dekoder, przeplatanie uwagi, generowanie) odzwierciedlająca diagram architektury lekcji.