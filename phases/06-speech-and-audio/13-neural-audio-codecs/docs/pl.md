# Neuralne kodeki audio — EnCodec, SNAC, Mimi, DAC i podział semantyczno-akustyczny

> Generacja audio 2026 to prawie same żetony. EnCodec, SNAC, Mimi i DAC przekształcają ciągłe przebiegi w dyskretne sekwencje, które transformator może przewidzieć. Podział tokenów semantycznych i akustycznych – pierwsza książka kodowa jest semantyczna, reszta akustyczna – to najważniejsza zmiana architektoniczna od czasu Transformera dla audio.

**Typ:** Ucz się
**Języki:** Python
**Wymagania wstępne:** Faza 6 · 02 (spektrogramy), Faza 10 · 11 (kwantyzacja), Faza 5 · 19 (Tokenizacja słów kluczowych)
**Czas:** ~60 minut

## Problem

Modele językowe działają na dyskretnych tokenach. Dźwięk jest ciągły. Jeśli potrzebujesz modelu mowy/muzyki w stylu LLM — MusicGen, Moshi, Sesame CSM, VibeVoice, Orpheus — potrzebujesz najpierw **neuralnego kodeka audio**: wyuczonego kodera, który dyskretyzuje dźwięk na mały słownik tokenów, oraz pasującego dekodera, który rekonstruuje kształt fali.

Powstały dwie rodziny:

1. **Kodeki przeznaczone do rekonstrukcji** — EnCodec, DAC. Zoptymalizuj percepcyjną jakość dźwięku. Tokeny są „akustyczne” — rejestrują wszystko, w tym tożsamość mówiącego, barwę głosu i hałas w tle.
2. **Kodeki semantyczne** — Mimi (Kyutai), SpeechTokenizer. Wymuś, aby pierwszy słownik kodów kodował treść językową/fonetyczną (często poprzez destylację z WavLM). Kolejne księgi kodów to detale akustyczne.

Spostrzeżenia na lata 2024–2026: **kodek czystej rekonstrukcji powoduje niewyraźną mowę podczas próby generowania mowy na podstawie tekstu.** LLM za pomocą tokenów kodeków musi nauczyć się zarówno struktury języka ORAZ struktury akustycznej w tym samym słowniku, który nie podlega skalowaniu. Oddzielenie ich — semantycznego słownika 0, akustycznego słownika 1-N — sprawia, że ​​Moshi i Sesame CSM działają.

## Koncepcja

![Cztery kodeki: EnCodec, DAC, SNAC (wieloskalowy), Mimi (semantyczny+akustyczny)](../assets/codec-comparison.svg)

### Podstawowa sztuczka: kwantyzacja wektorów resztkowych (RVQ)

Zamiast jednego dużego słownika (który wymagałby milionów kodów, aby zapewnić dobrą jakość), wszystkie nowoczesne kodeki audio korzystają z **RVQ**: kaskady małych słowników. Pierwsza książka kodów kwantyzuje sygnał wyjściowy kodera; drugi kwantyzuje resztę; itd. Każdy słownik zawiera 1024 kody. 8 książek kodowych = efektywne słownictwo 1024^8 = 10^24.

W czasie wnioskowania dekoder sumuje wszystkie wybrane kody na klatkę w celu rekonstrukcji.

### Cztery kodeki, które mają znaczenie w 2026 r

**EnCodec (Meta, 2022).** Wartość bazowa. Koder-dekoder w kształcie fali, wąskie gardło RVQ. 24 kHz, możliwe 32 książki kodowe, domyślnie 4 książki kodowe przy 1,5 kbps. Wykorzystuje architekturę `1D conv + transformer + 1D conv`. Używany przez MusicGen.

**DAC (Descript, 2023).** RVQ ze słownikami znormalizowanymi do L2, funkcjami okresowej aktywacji, zmniejszonymi stratami. Najwyższa wierność rekonstrukcji spośród wszystkich otwartych kodeków — czasami nie do odróżnienia od oryginalnej mowy z 12 książkami kodowymi. Pełne pasmo 44,1 kHz.

**SNAC (Hubert Siuzdak, 2024).** Wieloskalowe RVQ — zgrubne książki kodowe działają z niższą liczbą klatek na sekundę niż dokładne. Skutecznie modeluje dźwięk hierarchicznie: zgrubny „szkic” przy ~12 Hz plus szczegóły przy 50 Hz. Używany przez Orfeusza-3B, ponieważ hierarchiczna struktura dobrze odwzorowuje generację opartą na LM.

**Mimi (Kyutai, 2024).** Zmiana zasad gry w 2026 roku. Częstotliwość odświeżania 12,5 Hz (bardzo niska), 8 książek kodowych przy 4,4 kb/s. Codebook 0 jest **wydestylowany z WavLM** — przeszkolony w zakresie przewidywania funkcji zawierających mowę WavLM. Książki kodowe 1-7 to pozostałości akustyczne. Ten podział zasila Moshi (lekcja 15) i Sesame CSM.

### Liczba klatek na sekundę ma znaczenie w modelowaniu języka

Niższa liczba klatek na sekundę = krótsza sekwencja = szybszy LM.

| Kodek | Liczba klatek na sekundę | 1 s = N klatek | Dobre dla |
|-------|------|----------------|--------|
| EnCodec-24k | 75 Hz | 75 | muzyka, dźwięk ogólny |
| DAC-44.1k | 86 Hz | 86 | muzyka wysokiej jakości |
| SNAC-24k (zgrubny) | ~12 Hz | 12 | AR-LM wydajny |
| Mimi | 12,5 Hz | 12,5 | przesyłanie strumieniowe mowy |

Przy częstotliwości 12,5 Hz 10-sekundowa wypowiedź to tylko 125 ramek kodeka – transformator może je łatwo przewidzieć.

### Tokeny semantyczne a akustyczne

```
frame_t → [semantic_token_t, acoustic_token_0_t, acoustic_token_1_t, ..., acoustic_token_6_t]
```

- **Token semantyczny (książka kodów 0 w Mimi).** Koduje to, co zostało powiedziane — fonemy, słowa, treść. Destylowany z WavLM poprzez pomocniczą stratę przewidywania.
- **Żetony akustyczne (książki kodów 1-7).** Zakoduj barwę, tożsamość mówiącego, prozodię, szum tła, drobne szczegóły.

AR LM najpierw przewiduje token semantyczny (uwarunkowany na podstawie tekstu), a następnie przewiduje tokeny akustyczne (uwarunkowany na podstawie semantyki + odniesienia do mówcy). Dzięki tej faktoryzacji nowoczesny TTS może całkowicie klonować głosy: model semantyczny obsługuje treść; model akustyczny obsługuje barwę.

### Jakość rekonstrukcji 2026 (bity na sekundę, niższa przepływność jest lepsza)

| Kodek | Szybkość transmisji | PESQ | ViSQOL |
|-------|--------|------|-------|
| Opus-20kbps | 20 kb/s | 4,0 | 4.3 |
| EnCodec-6kbps | 6 kb/s | 3.2 | 3,8 |
| DAC-6kbps | 6 kb/s | 3,5 | 4,0 |
| SNAC-3kbps | 3 kb/s | 3.3 | 3,8 |
| Mimi-4,4kbps | 4,4 kb/s | 3.1 | 3,7 |

Tradycyjne kodeki, takie jak Opus, nadal wygrywają pod względem jakości percepcyjnej. Kodeki neuronowe wygrywają na **oddzielnych tokenach** (których Opus nie produkuje) i **jakości modelu generatywnego** (co LM może zrobić z tymi tokenami).

## Zbuduj to

### Krok 1: zakoduj za pomocą EnCodeca

```python
from encodec import EncodecModel
import torch

model = EncodecModel.encodec_model_24khz()
model.set_target_bandwidth(6.0)  # kbps

wav = torch.randn(1, 1, 24000)
with torch.no_grad():
    encoded = model.encode(wav)
codes, scale = encoded[0]
# codes: (1, n_codebooks, n_frames), dtype=int64
```

`n_codebooks=8` przy 6 kb/s. Każdy kod to 0-1023 (10-bitowy).

### Krok 2: dekodowanie i mierzenie rekonstrukcji

```python
with torch.no_grad():
    wav_recon = model.decode([(codes, scale)])

from torchaudio.functional import compute_deltas
import torch.nn.functional as F

mse = F.mse_loss(wav_recon[:, :, :wav.shape[-1]], wav).item()
```

### Krok 3: podział semantyczno-akustyczny (w stylu Mimi)

```python
from moshi.models import loaders
mimi = loaders.get_mimi()

with torch.no_grad():
    codes = mimi.encode(wav)  # shape (1, 8, frames@12.5Hz)

semantic = codes[:, 0]
acoustic = codes[:, 1:]
```

Semantyczny słownik kodów 0 jest dostosowany do WavLM. Możesz wytrenować transformator tekstu na semantyczny — znacznie mniejszy słownictwo niż przejście bezpośrednio na dźwięk. Następnie osobny dekoder sygnału akustycznego na falę warunkuje referencyjny głośnik.

### Krok 4: dlaczego działa AR LM poprzez tokeny kodeków

Dla 10-sekundowego klipu mowy w książkach kodowych Mimi 12,5 Hz × 8:

```
N_tokens = 10 * 12.5 * 8 = 1000 tokens
```

1000 tokenów to banalny kontekst dla transformatora. Transformator o parametrach 256M może wygenerować 10 sekund mowy w milisekundach na nowoczesnym procesorze graficznym.

## Użyj tego

Problem z mapą → kodek:

| Zadanie | Kodek |
|------|-------|
| Generacja muzyki ogólnej | EnCodec-24k |
| Rekonstrukcja o najwyższej wierności | DAC-44.1k |
| AR LM nad mową (TTS) | SNAC lub Mimi |
| Przesyłanie strumieniowe mowy w trybie pełnego dupleksu | Mimi (12,5 Hz) |
| Biblioteka efektów dźwiękowych z tekstem | EnCodec + warunek T5 |
| Dokładna edycja dźwięku | DAC + malowanie |

Ogólna zasada: **jeśli budujesz model generatywny, zacznij od Mimi lub SNAC. Jeśli budujesz potok kompresji, użyj Opus.**

## Pułapki

- **Zbyt wiele słowników.** Dodanie słowników zwiększa wierność liniowo, ale także liniowo długość sekwencji LM. Zatrzymaj się o 8-12.
- **Niedopasowanie liczby klatek na sekundę.** Trening LM na 12,5 Hz Mimi, a następnie dostrajanie na 50 Hz EnCodec cicho zawodzi.
- **Zakładając, że wszystkie księgi kodów są równe.** W Mimi, książka kodów 0 przenosi treść; jej utrata niszczy zrozumiałość. Utrata książki kodów 7 jest ledwo zauważalna.
- **Używanie jakości rekonstrukcji jako jedynej metryki.** Kodek może mieć świetną rekonstrukcję, ale może być bezużyteczny do generacji opartej na LM, jeśli struktura semantyczna jest zła.

## Wyślij to

Zapisz jako `outputs/skill-codec-picker.md`. Wybierz kodek dla danego zadania generowania lub kompresji.

## Ćwiczenia

1. **Łatwe.** Uruchom `code/main.py`. Implementuje zabawkowy skalar + kwantyzator resztkowy i mierzy błąd rekonstrukcji podczas dodawania książek kodowych.
2. **Średni.** Zainstaluj `encodec` i porównaj książki kodowe 1, 4, 8, 32 na wyciągniętym klipie mowy. Wykres PESQ lub MSE w funkcji bitrate.
3. **Trudne.** Załaduj Mimi. Zakoduj klip. Zastąp słownik 0 losowymi liczbami całkowitymi; rozszyfrować. Następnie w podobny sposób wymień książkę kodów 7. Porównaj te dwa zniekształcenia — zniekształcenie książki kodowej 0 powinno zniszczyć zrozumiałość; Korupcja Codebook 7 nie powinna prawie nic zmienić.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| RVQ | Kwantyzacja resztkowa | Kaskada małych książeczek kodowych; każdy kwantyzuje poprzednią resztę. |
| Liczba klatek na sekundę | Szybkość kodeka | Ile klatek tokenów na sekundę. Niższy = szybszy LM. |
| Semantyczny słownik | Książka kodów 0 (Mimi) | Książka kodów wydestylowana z funkcji SSL; koduje treść. |
| Książki kodów akustycznych | Wszystko inne | Barwa, prozodia, hałas, drobne szczegóły. |
| PESQ / ViSQOL | Jakość percepcyjna | Metryki obiektywne korelujące z MOS. |
| Kodek | Metakodek | Wartość bazowa RVQ; używany przez MusicGen. |
| Mimi | Kodek Kyutai | częstotliwość odświeżania 12,5 Hz; rozłam semantyczno-akustyczny; moc Moshiego. |

## Dalsze czytanie

- [Défossez i in. (2023). EnCodec](https://arxiv.org/abs/2210.13438) — wartość bazowa RVQ.
- [Kumar i in. (2023). Descript Audio Codec (DAC)](https://arxiv.org/abs/2306.06546) — otwarcie najwyższej jakości.
- [Siuzdak (2024). SNAC](https://arxiv.org/abs/2410.14411) — wieloskalowe RVQ.
- [Kyutai (2024). Kodek Mimi](https://kyutai.org/codec-explainer) — podział semantyczno-akustyczny, destylacja WavLM.
- [Borsos i in. (2023). AudioLM](https://arxiv.org/abs/2209.03143) — dwustopniowy paradygmat semantyczno-akustyczny.
- [Zeghidur i in. (2021). SoundStream](https://arxiv.org/abs/2107.03312) — oryginalny kodek RVQ umożliwiający przesyłanie strumieniowe.