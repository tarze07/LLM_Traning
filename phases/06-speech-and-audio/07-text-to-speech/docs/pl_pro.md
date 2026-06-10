# Text-to-Speech (TTS) — od Tacotron do F5 i Kokoro

> ASR zamienia mowę na tekst, natomiast TTS wykonuje zadanie odwrotne – zamienia tekst na mowę. Współczesny stos technologiczny w 2026 roku składa się zazwyczaj z trzech etapów: tekst → tokeny/fonemy, tokeny → spektrogram melowy, spektrogram → surowy przebieg fali (waveform). Każdy z tych modułów posiada gotowe, zoptymalizowane modele uruchamiane lokalnie.

**Typ:** Kompendium  
**Języki:** Python  
**Wymagania wstępne:** Faza 6 · 02 (spektrogramy i filtry melowe), Faza 5 · 09 (Modele seq2seq), Faza 7 · 05 (Pełna architektura Transformer)  
**Czas:** ~75 minut  

## Problem

Otrzymujesz ciąg tekstowy: „Proszę, przypomnij mi, żebym podlał rośliny o 18:00”. Twoim zadaniem jest wygenerowanie naturalnie brzmiącego, 3-sekundowego nagrania audio o nienagannej prozodii (pauzy, akcenty), z poprawną wymową słów i latencją poniżej 300 ms na procesorze CPU (na potrzeby asystenta głosowego działającego w czasie rzeczywistym). Dodatkowo system powinien umożliwiać zmianę barwy głosu, obsługiwać wtrącenia obcojęzyczne (np. code-switching „przypomnij mi o 18:00, daijoubu?”) oraz bezbłędnie radzić sobie z rzadkimi imionami i nazwiskami.

Klasyczny potok TTS składa się z następujących komponentów:

1. **Moduł przetwarzania tekstu (front-end).** Normalizacja tekstu (rozwijanie dat, skrótów, liczb, adresów e-mail), konwersja znaków na fonemy lub tokeny podsłowne (subwords), a także przewidywanie cech prozodycznych.
2. **Model akustyczny.** Mapuje przetworzony tekst (lub fonemy) na spektrogram melowy. Historyczne i współczesne modele: Tacotron 2 (2017), FastSpeech 2 (2020), VITS (2021), F5-TTS (2024), Kokoro (2024).
3. **Wokoder (Vocoder).** Konwertuje spektrogram melowy na surowy przebieg fali dźwiękowej. Przykłady: WaveNet (2016), WaveRNN, HiFi-GAN (2020), BigVGAN (2022), wokodery oparte na neuronowych kodekach audio (2024+).

W 2026 roku granica między modelem akustycznym a wokoderem zaciera się na rzecz modeli typu end-to-end oparte na dyfuzji oraz dopasowywaniu przepływu (flow matching). Niemniej jednak, podział na trzy klasyczne moduły pozostaje bardzo pomocny podczas analizy i debugowania systemów.

## Koncepcja

![Porównanie architektur TTS: Tacotron, FastSpeech, VITS, F5 oraz Kokoro](../assets/tts.svg)

**Tacotron 2 (2017).** Model seq2seq: wektorowanie znaków → dwukierunkowy koder LSTM (BiLSTM) → mechanizm atencji zależnej od lokalizacji (location-sensitive attention) → autoregresyjny dekoder LSTM generujący ramki mel-spektrogramu. Powolny (ze względu na autoregresję), mało stabilny na długich tekstach. Wciąż cytowany jako klasyczny baseline.

**FastSpeech 2 (2020).** Model nieautoregresyjny (non-autoregressive). Wbudowany predyktor czasu trwania (duration predictor) określa, ile ramek mel-spektrogramu przypada na każdy fonem. Generowanie jednoprzebiegowe, około 10-krotnie szybsze niż Tacotron 2. Choć traci nieco na naturalności (ze względu na monotoniczne wyrównanie), jest powszechnie stosowany w przemyśle.

**VITS (2021).** Model end-to-end łączący koder tekstu, moduł przewidywania czasu trwania oparty na przepływach normalizacyjnych (normalizing flows) oraz wokoder HiFi-GAN. Całość jest trenowana wspólnie z użyciem wnioskowania wariacyjnego (variational inference). Zapewnia wysoką jakość w ramach jednego modelu. Dominujące rozwiązanie open-source w latach 2022–2024. Warianty: YourTTS (zero-shot TTS dla wielu mówców), XTTS v2 (2024, Coqui).

**F5-TTS (2024).** Model oparty na architekturze Transformer z dopasowywaniem przepływu (Flow Matching Transformer). Zapewnia wysoce naturalną prozodię oraz klonowanie głosu w trybie zero-shot przy użyciu zaledwie 5-sekundowej próbki referencyjnej. Lider rankingów open-source w 2026 roku (335M parametrów).

**Kokoro (2024).** Kompaktowy model (82M parametrów), zoptymalizowany pod kątem procesorów CPU, oferujący najwyższą jakość dla języka angielskiego w czasie rzeczywistym. Posiada zamknięty słownik, licencję Apache-2.0.

**Rozwiązania komercyjne (API).** Modele takie jak ElevenLabs v2.5, OpenAI TTS-1-HD czy Google Chirp-3 stanowią komercyjny stan wiedzy. ElevenLabs v2.5 dzięki obsłudze tagów emocjonalnych (np. `[whisper]`, `[laughter]`) i generowaniu głosów postaci zdominował rynek produkcji audiobooków w 2026 roku.

### Ewolucja wokoderów

| Rok | Wokoder | Latencja | Jakość |
|-----|-----|---------|---------|
| 2016 | WaveNet | Tylko offline | Klasa SOTA w momencie publikacji |
| 2018 | WaveRNN | Bliska czasu rzeczywistego | Dobra |
| 2020 | HiFi-GAN | Ok. 100× RT | Bardzo wysoka, bliska ludzkiej |
| 2022 | BigVGAN | Ok. 50× RT | Świetna generalizacja między mówcami i językami |
| 2024 | SNAC, DAC (kodeki neuronowe) | Zintegrowane z modelami AR | Dyskretne tokeny, wysoka wydajność bitowa |

W 2026 roku większość nowoczesnych modeli TTS generuje bezpośrednio surowy sygnał audio z tekstu, traktując spektrogram melowy jako reprezentację pośrednią wewnątrz sieci.

### Ewaluacja systemów TTS

- **MOS (Mean Opinion Score).** Subiektywna ocena jakości w skali 1–5 wystawiana przez ludzi. Pozostaje złotym standardem, mimo że proces jej pozyskiwania jest powolny i kosztowny.
- **CMOS (Comparative MOS).** Test porównawczy typu A vs. B. Pozwala na uzyskanie węższych przedziałów ufności.
- **UTMOS, DNSMOS.** Neuronowe modele automatycznie szacujące wskaźnik MOS bez użycia nagrania referencyjnego. Stosowane w publicznych benchmarkach.
- **CER (Character Error Rate) z użyciem ASR.** Polega na transkrypcji wygenerowanego przez TTS dźwięku za pomocą modelu Whisper i obliczeniu błędu CER w odniesieniu do tekstu wejściowego. Służy do automatycznej oceny zrozumiałości mowy.
- **SECS (Speaker Embedding Cosine Similarity).** Podobieństwo cosinusowe wektorów cech mówcy docelowego i wyjściowego, służące do ewaluacji wierności klonowania głosu.

Wskaźniki ewaluacyjne na zbiorze LibriTTS (stan na 2026 r.):

| Model | UTMOS | CER (ASR Whisper) | Rozmiar |
|-------|-------|-------------------|------|
| Nagranie referencyjne (Ground Truth) | 4.08 | 1,2% | — |
| F5-TTS | 3,95 | 2,1% | 335M |
| XTTS v2 | 3,81 | 3,5% | 470M |
| VITS | 3,62 | 3,1% | 25M |
| Kokoro v0.19 | 3,87 | 1,8% | 82M |
| Parler-TTS Large | 3,76 | 2,8% | 2.3B |

## Implementacja krok po kroku

### Krok 1: Transkrypcja fonetyczna (fonemizowanie)

```python
from phonemizer import phonemize
ph = phonemize("Hello world", language="en-us", backend="espeak")
# Wynik: 'həloʊ wɜːld'
```

Fonemy stanowią uniwersalny pomost między tekstem a dźwiękiem. Unikaj podawania surowego tekstu bezpośrednio do modeli akustycznych starszych niż VITS.

### Krok 2: Wnioskowanie z użyciem modelu Kokoro (zoptymalizowany pod CPU)

```python
from kokoro import KPipeline
tts = KPipeline(lang_code="a")  # "a" = American English
audio, sr = tts("Please remind me to water the plants at 6 pm.", voice="af_bella")
# audio: tensor float32, sr=24000
```

Model działa w trybie offline, zajmuje tylko 82M parametrów i doskonale nadaje się do uruchomienia na procesorach komputerów osobistych.

### Krok 3: Wnioskowanie z F5-TTS (klonowanie głosu)

```python
from f5_tts.api import F5TTS
tts = F5TTS()
wav = tts.infer(
    ref_file="my_voice_5s.wav",
    ref_text="The quick brown fox jumps over the lazy dog.",
    gen_text="Please remind me to water the plants.",
)
```

Przekaż 5-sekundowe nagranie referencyjne wraz z jego transkrypcją – model F5 precyzyjnie sklonuje barwę głosu oraz prozodię mówcy docelowego.

### Krok 4: Architektura wokodera HiFi-GAN (koncepcyjnie)

```python
import torch.nn as nn

class HiFiGAN(nn.Module):
    def __init__(self, mel_channels=80, upsample_rates=[8, 8, 2, 2]):
        super().__init__()
        # 4 bloki upsamplingu, łącznie zwiększające rozdzielczość 256-krotnie 
        # (przejście z częstotliwości ramek mel do częstotliwości próbek audio)
        ...
    def forward(self, mel):
        return self.blocks(mel)  # zwraca surowy przebieg audio (waveform)
```

Proces treningowy HiFi-GAN opiera się na uczeniu kontradyktoryjnym (z użyciem dyskryminatorów wieloskalowych i wielookresowych), funkcji straty rekonstrukcji spektrogramu melowego (Mel Reconstruction Loss) oraz straty dopasowania cech (Feature Matching Loss). W praktyce stosuje się gotowe, przeszkolone wagi z repozytorium `hifi-gan` lub NVIDIA NeMo.

### Krok 5: Kompletny potok syntezy (pseudokod)

```python
text = "Please remind me at 6 pm."
phones = phonemize(text)
mel = acoustic_model(phones, speaker=alice)      # zwraca tensor [T, 80]
wav = vocoder(mel)                                # zwraca tensor [T * 256]
soundfile.write("out.wav", wav, 24000)
```

## Sugerowane rozwiązania (2026)

| Scenariusz | Rekomendowane rozwiązanie |
|----------|------|
| Asystent głosowy (język angielski) działający w czasie rzeczywistym | Kokoro (CPU) lub XTTS v2 (GPU) |
| Szybkie klonowanie głosu (na podstawie 5-sekundowej próbki) | F5-TTS |
| Profesjonalne, wysoce ekspresyjne głosy komercyjne | API ElevenLabs v2.5 |
| Generowanie audiobooków (wysoka jakość) | ElevenLabs v2.5 lub XTTS v2 po dostrojeniu (finetuning) |
| Języki o ograniczonych zasobach (low-resource) | Uczenie modelu VITS na 5–20 godzinach nagrań docelowych |
| Kontrola emocji i ekspresji głosu | ElevenLabs v2.5 lub StyleTTS 2 |

Złoty standard open-source w 2026 roku: **F5-TTS dla uzyskania najwyższej jakości, Kokoro dla maksymalnej wydajności**. Nie stosuj modeli typu Tacotron, chyba że w celach historycznych.

## Typowe pułapki

- **Brak normalizacji tekstu (Text Normalization).** Skrót „Dr Smith” może zostać przeczytany jako „Doktor Smith” lub „Droga Smith”. Liczba „2026” może brzmieć „dwa tysiące dwadzieścia sześć” lub „dwadzieścia dwadzieścia sześć”. Zawsze przeprowadzaj pełną normalizację tekstu przed fonemizacją.
- **Rzeczowniki własne spoza słownika (OOV - Out-Of-Vocabulary).** Systemy mogą błędnie fonemizować nietypowe nazwiska. Zastosuj model G2P (Grapheme-to-Phoneme) lub słownik wyjątków jako rozwiązanie zapasowe dla nieznanych wyrazów.
- **Przesterowanie dźwięku (Clipping).** Wyjście wokodera rzadko generuje przesterowania, ale rozbieżności w skalowaniu spektrogramów melowych podczas wnioskowania mogą wypchnąć wartości amplitudy poza zakres [-1.0, 1.0]. Zawsze stosuj `np.clip(wav, -1.0, 1.0)`.
- **Niedopasowanie częstotliwości próbkowania (sampling rate mismatch).** Model Kokoro generuje dźwięk o częstotliwości 24 kHz. Jeśli Twój dalszy potok (np. system transmisji) wymaga 16 kHz, musisz dokonać resamplingu, aby uniknąć aliasingu.

## Zadanie do wykonania

Zapisz jako `outputs/skill-tts-designer.md`. Zaprojektuj kompletny potok TTS dobrany do konkretnego głosu, wymagań opóźnienia (latencji) oraz języka docelowego.

## Ćwiczenia

1. **Łatwe.** Uruchom skrypt `code/main.py`. Buduje on prosty słownik fonetyczny, symuluje predyktor czasu trwania fonemów i generuje przykładową siatkę czasową spektrogramu melowego.
2. **Średnie.** Zainstaluj bibliotekę Kokoro i wygeneruj to samo zdanie z użyciem głosów `af_bella` oraz `am_adam`. Porównaj czas syntezy oraz jakość brzmienia.
3. **Trudne.** Nagraj swój własny 5-sekundowy klip audio i wykorzystaj model F5-TTS do sklonowania głosu. Oblicz metrykę SECS pomiędzy próbką referencyjną a wygenerowanym klonem.

## Kluczowe terminy

| Termin | Potoczne określenie | Co to naprawdę oznacza |
|------|-----------------|----------------------|
| Fonem | Głoska | Najmniejsza abstrakcyjna jednostka dźwiękowa języka (np. 39 fonemów w języku angielskim w standardzie ARPAbet). |
| Predyktor czasu trwania | Duration Predictor | Moduł w modelach nieautoregresyjnych wyznaczający liczbę ramek spektrogramu przydzieloną dla każdego fonemu. |
| Wokoder | Vocoder | Model generatywny przekształcający reprezentację mel-spektrogramu na surowe próbki fali dźwiękowej. |
| HiFi-GAN | Klasyczny wokoder | Model oparty na sieciach GAN, dominujący w latach 2020–2024. |
| MOS | Ocena jakości | Mean Opinion Score; średnia ocena naturalności mowy wystawiana przez ludzkich sędziów w skali 1–5. |
| SECS | Speaker Cosine Similarity | Speaker Embedding Cosine Similarity; wskaźnik podobieństwa cosinusowego wektorów mówcy oceniający stopień wierności klonowania. |
| F5-TTS | SOTA Open Source | Model oparty na dopasowywaniu przepływu (flow matching) umożliwiający świetne klonowanie zero-shot. |
| Kokoro | Lekki model CPU | Szybki model syntezy o rozmiarze 82M parametrów na licencji Apache 2.0. |

## Dalsze czytanie

- [Shen et al. (2017). Natural TTS Synthesis by Conditioning WaveNet on Mel Spectrogram Predictions](https://arxiv.org/abs/1712.05884) — publikacja wprowadzająca model Tacotron 2.
- [Kim, Kong, Son (2021). Conditional Variational Autoencoder with Adversarial Learning for End-to-End Text-to-Speech](https://arxiv.org/abs/2106.06103) — publikacja wprowadzająca model VITS.
- [Chen et al. (2024). F5-TTS: A Simple and Strong Zero-Shot Text-to-Speech System](https://arxiv.org/abs/2410.06885) — specyfikacja modelu F5-TTS.
- [Kong, Kim, Bae (2020). HiFi-GAN: Generative Adversarial Networks for Efficient and High Fidelity Speech Synthesis](https://arxiv.org/abs/2010.05646) — oryginalna praca wprowadzająca wokoder HiFi-GAN.
- [hexgrad/Kokoro-82M on Hugging Face](https://huggingface.co/hexgrad/Kokoro-82M) — strona projektu i wagi modelu Kokoro.
