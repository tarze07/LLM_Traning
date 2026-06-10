# Text-to-Speech (TTS) — od Tacotron do F5 i Kokoro

> ASR zamienia mowę na tekst; TTS zamienia tekst na mowę. Stos 2026 składa się z trzech części: tekst → tokeny, tokeny → mel, mel → przebieg. Każda część ma domyślny model pasujący do laptopa.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 6 · 02 (spektrogramy i Mel), Faza 5 · 09 (Seq2Seq), Faza 7 · 05 (pełny transformator)
**Czas:** ~75 minut

## Problem

Masz ciąg znaków: „Proszę, przypomnij mi, żebym podlał rośliny o 18:00”. Potrzebujesz 3-sekundowego klipu audio, który brzmi naturalnie, ma poprawną prozodię (pauzy, akcent), wymawia „rośliny” z odpowiednią samogłoską i działa w czasie krótszym niż 300 ms na procesorze dla asystenta głosowego na żywo. Musisz także zamieniać głosy, obsługiwać wprowadzanie z przełączaniem kodów („przypomnij mi o 18:00, daijoubu?”) i nie zawstydzać się imionami.

Nowoczesne rurociągi TTS wyglądają następująco:

1. **Nakładka tekstowa.** Normalizuj tekst (daty, liczby, e-maile), konwertuj na fonemy lub tokeny podsłów, przewidywaj cechy prozodii.
2. **Model akustyczny.** Tekst → spektrogram mel. Tacotron 2 (2017), FastSpeech 2 (2020), VITS (2021), F5-TTS (2024), Kokoro (2024).
3. **Wokoder.** Mel → kształt fali. WaveNet (2016), WaveRNN, HiFi-GAN (2020), BigVGAN (2022), wokodery kodeków neuronowych w latach 2024+.

W roku 2026 podział akustyczny + wokoder rozmywa się z modelami kompleksowej dyfuzji i dopasowywania przepływu. Jednak model mentalny składający się z trzech części nadal sprawdza się w przypadku debugowania.

## Koncepcja

![Tacotron, FastSpeech, VITS, F5/Kokoro obok siebie](../assets/tts.svg)

**Tacotron 2 (2017).** Seq2seq: osadzanie znaków → koder BiLSTM → uwaga zależna od lokalizacji → dekoder autoregresyjny LSTM emituje ramki mel. Powolny (AR), chwiejny przy długim tekście. Nadal cytowany jako punkt odniesienia.

**FastSpeech 2 (2020).** Brak autoregresji. Predyktor czasu trwania podaje, ile klatek mel otrzymuje każdy fonem. 1-przebieg, 10 razy szybszy niż Tacotron. Traci trochę naturalności (monotoniczne wyrównanie), ale jest wszędzie widoczny.

**VITS (2021).** Łącznie kompleksowo trenuje koder + czas trwania oparty na przepływie + wokoder HiFi-GAN z wnioskowaniem wariacyjnym. Wysoka jakość, pojedynczy model. Dominujący TTS typu open source 2022–2024. Warianty: YourTTS (wielogłośnikowy zero-shot), XTTS v2 (2024, Coqui).

**F5-TTS (2024).** Transformator dyfuzyjny z dopasowaniem przepływu. Naturalna prozodia, klonowanie głosu o zerowym zasięgu z 5 sekundami referencyjnego dźwięku. Czołówka rankingów TTS typu open source w 2026 r. Parametry 335M.

**Kokoro (2024).** Mały (82M), obsługiwany przez procesor, najlepszy w swojej klasie angielski TTS do użytku w czasie rzeczywistym. Zamknięte słownictwo, tylko w języku angielskim, Apache-2.0.

**OpenAI TTS-1-HD, ElevenLabs v2.5, Google Chirp-3.** Komercyjny stan wiedzy. Tagi emocji ElevenLabs v2.5 („[szeptane]”, „[śmiech]”) i głosy postaci będą zdominować produkcję audiobooków w 2026 roku.

### Ewolucja wokodera

| epoka | Wokoder | Opóźnienie | Jakość |
|-----|-----|---------|---------|
| 2016 | Sieć Wave | tylko offline | SOTA w wydaniu |
| 2018 | FalaRNN | ~czas rzeczywisty | dobrze |
| 2020 | HiFi-GAN | 100× w czasie rzeczywistym | prawie ludzki |
| 2022 | BigVGAN | 50× w czasie rzeczywistym | uogólnia na różne głośniki/języki |
| 2024 | SNAC, DAC (kodeki neuronowe) | zintegrowany z modelami AR | dyskretne tokeny, bitowo wydajne |

Do 2026 r. większość modeli „TTS” będzie obejmować kompleksowe rozwiązania od tekstu do kształtu fali; spektrogram mel jest reprezentacją wewnętrzną.

### Ocena

- **MOS (średni wynik opinii).** Skala 1–5, badanie crowdsourcingowe. Nadal złoty standard; boleśnie powolny.
- **CMOS (porównawczy MOS).** Preferencje A-vs-B. Węższe przedziały ufności na adnotację.
- **UTMOS, DNSMOS.** Bezreferencyjne predyktory neuronowe MOS. Używany do tablic liderów.
- **CER (wskaźnik błędów znaków) przez ASR.** Uruchom wyjście TTS przez Whisper, oblicz CER na podstawie wprowadzonego tekstu. Pełnomocnik dotyczący zrozumiałości.
- **SECS (podobieństwo cosinusowe osadzania głośników).** Jakość klonowania głosu.

Liczby 2026 w teście czyszczenia LibriTTS:

| Modelka | UTMOS | CER (przez szept) | Rozmiar |
|-------|-------|----------------------|------|
| Podstawowa prawda | 4.08 | 1,2% | — |
| F5-TTS | 3,95 | 2,1% | 335M |
| XTTS wersja 2 | 3,81 | 3,5% | 470M |
| WITA | 3,62 | 3,1% | 25M |
| Kokoro v0.19 | 3,87 | 1,8% | 82M |
| Parler-TTS duży | 3,76 | 2,8% | 2.3B |

## Zbuduj to

### Krok 1: fonemizuj dane wejściowe

```python
from phonemizer import phonemize
ph = phonemize("Hello world", language="en-us", backend="espeak")
# 'həloʊ wɜːld'
```

Fonemy są uniwersalnym pomostem. Unikaj podawania surowego tekstu do elementów o jakości poniżej poziomu VITS.

### Krok 2: uruchom Kokoro (domyślnie procesor 2026)

```python
from kokoro import KPipeline
tts = KPipeline(lang_code="a")  # "a" = American English
audio, sr = tts("Please remind me to water the plants at 6 pm.", voice="af_bella")
# audio: float32 tensor, sr=24000
```

Działa w trybie offline, pojedynczy plik, 82M parametrów.

### Krok 3: uruchom F5-TTS z klonowaniem głosu

```python
from f5_tts.api import F5TTS
tts = F5TTS()
wav = tts.infer(
    ref_file="my_voice_5s.wav",
    ref_text="The quick brown fox jumps over the lazy dog.",
    gen_text="Please remind me to water the plants.",
)
```

Przekaż 5-sekundowy klip referencyjny + jego transkrypcję; F5 klonuje prozodię i barwę.

### Krok 4: Wokoder HiFi-GAN od zera

Zbyt duży, aby zmieścić się w skrypcie samouczka, ale kształt jest:

```python
class HiFiGAN(nn.Module):
    def __init__(self, mel_channels=80, upsample_rates=[8, 8, 2, 2]):
        super().__init__()
        # 4 upsample blocks, total 256x to go from mel-rate to audio-rate
        ...
    def forward(self, mel):
        return self.blocks(mel)  # -> waveform
```

Trening: kontradyktoryjny (dyskryminator w krótkich oknach) + utrata rekonstrukcji spektrogramu melowego + utrata dopasowania cech. Utowarowione — użyj wstępnie wyszkolonych punktów kontrolnych z repozytorium `hifi-gan` lub nvidia-NeMo.

### Krok 5: pełny potok (pseudokod)

```python
text = "Please remind me at 6 pm."
phones = phonemize(text)
mel = acoustic_model(phones, speaker=alice)      # [T, 80]
wav = vocoder(mel)                                # [T * 256]
soundfile.write("out.wav", wav, 24000)
```

## Użyj tego

Stos na rok 2026:

| Sytuacja | Wybierz |
|----------|------|
| Asystent głosowy w języku angielskim w czasie rzeczywistym | Kokoro (CPU) lub XTTS v2 (GPU) |
| Klonowanie głosu z odniesienia 5 | F5-TTS |
| Głosy postaci komercyjnych | ElevenLabs v2.5 |
| Narracja audiobooka | ElevenLabs v2.5 lub XTTS v2 + dostrojenie |
| Język o niskich zasobach | Trenuj VITS na 5–20 godzinach danych języka docelowego |
| Tagi ekspresyjne / emocjonalne | ElevenLabs v2.5 lub StyleTTS 2 dostosowują |

Lider open source od 2026 r.: **F5-TTS dla jakości, Kokoro dla wydajności**. Nie sięgaj po Tacotron, jeśli nie jesteś historykiem.

## Pułapki

- **Brak normalizatora tekstu.** „Dr. Smith” brzmi „Doktor” lub „Drive”? „2026” jako „dwadzieścia dwadzieścia sześć” czy „dwa zero dwa sześć”? Normalizuj PRZED fonemizerem.
- ** Rzeczowniki własne OOV.** „Ghumare” → „ghyu-mair”? Wyślij zastępczy model grafemu na fonem dla nieznanych tokenów.
- **Przycinanie.** Wyjście wokodera rzadko ulega przesterowaniu, ale niedopasowanie skalowania Mel przy wnioskowaniu może przekroczyć ±1,0. Zawsze `np.clip(wav, -1, 1)`.
- **Niedopasowanie częstotliwości próbkowania.** Kokoro wysyła sygnał 24 kHz; Twój potok downstream oczekuje 16 kHz → spróbuj ponownie lub uzyskaj aliasing.

## Wyślij to

Zapisz jako `outputs/skill-tts-designer.md`. Zaprojektuj potok TTS dla danego głosu, opóźnienia i języka docelowego.

## Ćwiczenia

1. **Łatwe.** Uruchom `code/main.py`. Tworzy słownik fonemów na podstawie słownictwa zabawkowego, szacuje czas trwania każdego fonemu i drukuje fałszywy harmonogram „mel”.
2. **Średni.** Zainstaluj Kokoro, zsyntetyzuj to samo zdanie w głosach `af_bella` i `am_adam`. Porównaj czas trwania dźwięku i subiektywną jakość.
3. **Trudne.** Nagraj 5-sekundowy klip przedstawiający siebie. Aby go sklonować, użyj klawisza F5-TTS. Zgłoś SECS między odniesieniem a sklonowanym wyjściem.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Fonem | Jednostka dźwiękowa | Abstrakcyjna klasa dźwięku; 39 w języku angielskim (ARPABet). |
| Predyktor czasu trwania | Jak długo trwa każdy fonem | Dane wyjściowe modelu innego niż AR; liczba całkowitych klatek na fonem. |
| Wokoder | Mel → przebieg | Mapowanie sieci neuronowej mel-spec na surowe próbki. |
| HiFi-GAN | Standardowy wokoder | oparty na GAN; dominujący 2020–2024. |
| MOS | Jakość subiektywna | 1–5 średnia ocena opinii osób oceniających. |
| SEK | Metryka klonowania głosu | Podobieństwo cosinusowe między osadzeniem głośników docelowych i wyjściowych. |
| F5-TTS | SOTA typu open source 2024 | Dyfuzja dopasowująca się do przepływu; klonowanie zero-shotowe. |
| Kokoro | Lider angielskiego procesora | Model z parametrami 82M, Apache 2.0. |

## Dalsze czytanie

- [Shen i in. (2017). Tacotron 2](https://arxiv.org/abs/1712.05884) — linia bazowa seq2seq.
- [Kim, Kong, syn (2021). VITS](https://arxiv.org/abs/2106.06103) — kompleksowo oparty na przepływie.
- [Chen i in. (2024). F5-TTS](https://arxiv.org/abs/2410.06885) — aktualna SOTA typu open source.
- [Kong, Kim, Bae (2020). HiFi-GAN](https://arxiv.org/abs/2010.05646) — wokoder, który będzie nadal dostępny w 2026 r.
– [Kokoro-82M na HuggingFace](https://huggingface.co/hexgrad/Kokoro-82M) — angielski TTS przyjazny procesorowi na rok 2024.