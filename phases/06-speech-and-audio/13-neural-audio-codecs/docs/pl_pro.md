# Neuronowe kodeki audio — EnCodec, SNAC, Mimi, DAC i podział semantyczno-akustyczny

> Generowanie audio w 2026 roku opiera się niemal wyłącznie na tokenach dyskretnych (tokens). Narzędzia takie jak EnCodec, SNAC, Mimi oraz DAC przekształcają ciągłe przebiegi fal dźwiękowych w dyskretne sekwencje tokenów, które mogą być z powodzeniem modelowane przez sieci typu Transformer. Rozdział tokenów na semantyczne (pierwsza książka kodowa - codebook) oraz akustyczne (pozostałe książki) to najważniejszy przełom architektoniczny w dziedzinie przetwarzania dźwięku od czasu wprowadzenia sieci Transformer.

**Typ:** Podręcznik  
**Języki:** Python  
**Wymagania wstępne:** Faza 6 · 02 (spektrogramy i filtry melowe), Faza 10 · 11 (Kwantyzacja modeli), Faza 5 · 19 (Tokenizacja tekstu)  
**Czas:** ~60 minut  

## Problem

Klasyczne modele językowe (LLM) operują wyłącznie na dyskretnych jednostkach (tokenach). Dźwięk z natury jest sygnałem ciągłym. Jeśli chcemy zbudować generatywny model mowy lub muzyki o architekturze zbliżonej do LLM (np. MusicGen, Moshi, Sesame CSM, VibeVoice, Orpheus), musimy najpierw zastosować **neuronowy kodek audio**. Składa się on z trenowanego enkodera, który dyskretyzuje wejściowy sygnał audio na sekwencję tokenów ze skończonego słownika, oraz dekodera, który na podstawie tych tokenów rekonstruuje surowy przebieg fali dźwiękowej.

Wyróżniamy dwie główne rodziny neuronowych kodeków:

1. **Kodeki zorientowane na rekonstrukcję (np. EnCodec, DAC).** Ich głównym celem jest maksymalizacja percepcyjnej jakości rekonstruowanego dźwięku. Wygenerowane tokeny mają charakter czysto akustyczny – kodują wszystkie szczegóły nagrania, w tym barwę głosu, tożsamość mówcy oraz szumy tła.
2. **Kodeki o strukturze semantycznej (np. Mimi, SpeechTokenizer).** Wymuszają one, aby pierwsza książka kodowa (codebook 0) kodowała wyłącznie treść językową/fonetyczną (co osiąga się np. poprzez destylację wiedzy z modelu WavLM). Kolejne książki kodowe służą do uzupełniania brakujących szczegółów akustycznych.

Kluczowe spostrzeżenie z lat 2024–2026: **stosowanie kodeków o charakterze wyłącznie akustycznym prowadzi do bełkotliwej syntezy mowy (low intelligibility) w zadaniach Text-to-Speech.** Model LLM pracujący na takich tokenach musi uczyć się jednocześnie reguł językowych oraz skomplikowanej struktury akustycznej w obrębie jednego, niewydolnego słownika. Dopiero rozdzielenie tych reprezentacji – semantycznej (codebook 0) i akustycznej (codebooks 1-N) – umożliwiło powstanie systemów o tak wysokiej jakości jak Moshi czy Sesame CSM.

## Koncepcja

![Porównanie struktur neuronowych kodeków audio: EnCodec, DAC, SNAC oraz Mimi](../assets/codec-comparison.svg)

### Kwantyzacja wektorów resztkowych (Residual Vector Quantization - RVQ)

Zbudowanie jednej gigantycznej książki kodowej wymagającej milionów unikalnych tokenów do wiernego odtworzenia dźwięku byłoby nieefektywne obliczeniowo. Wszystkie współczesne kodeki neuronowe wykorzystują **Residual Vector Quantization (RVQ)**, czyli kaskadę mniejszych książek kodowych. Pierwsza książka kodowa kwantyzuje wyjście enkodera; druga kwantyzuje błąd (resztę) kwantyzacji pierwszego etapu; trzecia kwantyzuje błąd drugiego etapu itd. Każda z książek kodowych zawiera zazwyczaj 1024 kody. Zastosowanie 8 takich książek kodowych daje efektywny rozmiar słownika rzędu $1024^8 = 10^{24}$.

Podczas dekodowania (rekonstrukcji), reprezentacje wybrane z poszczególnych książek kodowych dla danej ramki czasowej są sumowane i przekazywane do dekodera.

### Cztery wiodące kodeki w 2026 r.

**EnCodec (Meta, 2022).** Klasyczny model bazowy (baseline). Architektura typu koder-dekoder z wąskim gardłem RVQ. Dla częstotliwości 24 kHz obsługuje zazwyczaj do 32 książek kodowych (domyślnie stosuje się 8 książek przy przepływności 6 kbps). Wykorzystuje jednowymiarowe warstwy splotowe i bloki Transformer. Stanowi fundament modelu MusicGen.

**DAC (Descript, 2023).** Wykorzystuje RVQ ze słownikami (codebooks) znormalizowanymi do normy L2, okresowe funkcje aktywacji oraz zoptymalizowane funkcje straty. Zapewnia najwyższą wierność rekonstrukcji spośród wszystkich otwartoźródłowych kodeków – przy 12 książkach kodowych wyjściowe audio o pełnym pasmie 44.1 kHz jest często nie do odróżnienia od oryginału.

**SNAC (Hubert Siuzdak, 2024).** Wieloskalowa kwantyzacja RVQ, w której książki kodowe wyższego rzędu (zgrubne) działają przy znacznie niższej częstotliwości próbkowania niż książki szczegółowe. Pozwala to na hierarchiczne modelowanie dźwięku: zgrubny „szkic” przy ok. 12 Hz uzupełniany jest o szczegóły przy 50 Hz. Wykorzystywany m.in. w modelach Orpheus-3B, ze względu na świetną kompatybilność z autoregresyjnym generowaniem (LM).

**Mimi (Kyutai, 2024).** Prawdziwy przełom. Niezwykle niska częstotliwość generowania ramek (zaledwie 12.5 Hz), 8 książek kodowych przy przepływności 4.4 kbps. Pierwsza książka kodowa (codebook 0) jest destylowana z reprezentacji WavLM (trenowana na przewidywanie cech językowych z WavLM). Książki od 1 do 7 kodują resztkowe informacje akustyczne. Architektura ta stanowi serce modeli Moshi (lekcja 15) oraz Sesame CSM.

### Wpływ częstotliwości ramek (frame rate) na wydajność modeli językowych

Niska częstotliwość ramek przekłada się na krótsze sekwencje tokenów, co drastycznie przyspiesza wnioskowanie z modeli LLM.

| Kodek | Częstotliwość ramek | Długość sekwencji dla 1 s audio | Zastosowanie |
|-------|------|----------------|--------|
| EnCodec-24k | 75 Hz | 75 ramek | Muzyka, ogólne sygnały audio |
| DAC-44.1k | 86 Hz | 86 ramek | Muzyka o wysokiej wierności (hi-fi) |
| SNAC-24k (zgrubny) | ~12 Hz | 12 ramek | Wydajne modele autoregresyjne (AR-LM) |
| Mimi | 12,5 Hz | 12,5 ramek | Strumieniowa synteza mowy |

Przy częstotliwości 12.5 Hz, 10-sekundowa wypowiedź reprezentowana jest przez zaledwie 125 ramek – tak krótka sekwencja jest niezwykle łatwa do przetworzenia dla modeli Transformer.

### Podział semantyczno-akustyczny

```
ramka_t → [token_semantyczny_t, token_akustyczny_0_t, token_akustyczny_1_t, ..., token_akustyczny_6_t]
```

- **Token semantyczny (codebook 0 w modelu Mimi):** Koduje treść językową (fonemy, słowa, znaczenie). Destylowany z WavLM z użyciem pomocniczej funkcji straty.
- **Tokeny akustyczne (codebooks 1-7):** Kodują barwę, tożsamość mówcy, prozodię, szumy tła oraz drobne szczegóły sygnału.

Model autoregresyjny (AR LM) najpierw przewiduje token semantyczny na podstawie tekstu wejściowego, a następnie tokeny akustyczne (warkunowane wygenerowaną semantyką oraz wektorem referencyjnym mówcy). Dzięki takiemu rozplotowi (factorization) nowoczesne systemy TTS mogą bezbłędnie klonować głosy: moduł semantyczny odpowiada za treść, a moduł akustyczny za barwę i ekspresję.

### Wierność rekonstrukcji (stan na 2026 r.)

| Kodek | Przepływność (Bitrate) | Jakość PESQ | Jakość ViSQOL |
|-------|--------|------|-------|
| Opus | 20 kbps | 4.0 | 4.3 |
| EnCodec | 6 kbps | 3.2 | 3.8 |
| DAC | 6 kbps | 3.5 | 4.0 |
| SNAC | 3 kbps | 3.3 | 3.8 |
| Mimi | 4.4 kbps | 3.1 | 3.7 |

Klasyczne kodeki (np. Opus) wciąż zapewniają wyższą jakość rekonstrukcji przy danej przepływności. Neuronowe kodeki mają jednak tę przewagę, że **generują dyskretne tokeny** (których Opus nie produkuje) umożliwiające bezpośrednie zastosowanie modeli językowych (LM) do syntezy i manipulacji dźwiękiem.

## Implementacja krok po kroku

### Krok 1: Kodowanie sygnału z użyciem EnCodec

```python
from encodec import EncodecModel
import torch

model = EncodecModel.encodec_model_24khz()
model.set_target_bandwidth(6.0)  # Przepływność w kbps

wav = torch.randn(1, 1, 24000)
with torch.no_grad():
    encoded = model.encode(wav)
codes, scale = encoded[0]
# codes: tensor int64 o kształcie (1, n_codebooks, n_frames)
```

Dla przepływności 6 kbps parametr `n_codebooks` wynosi 8. Każdy token przyjmuje wartość z zakresu 0-1023 (reprezentacja 10-bitowa).

### Krok 2: Dekodowanie i pomiar błędu rekonstrukcji

```python
with torch.no_grad():
    wav_recon = model.decode([(codes, scale)])

import torch.nn.functional as F
mse = F.mse_loss(wav_recon[:, :, :wav.shape[-1]], wav).item()
```

### Krok 3: Separacja semantyczno-akustyczna (w stylu modelu Mimi)

```python
from moshi.models import loaders
mimi = loaders.get_mimi()

with torch.no_grad():
    codes = mimi.encode(wav)  # Zwraca tensor o kształcie (1, 8, frames@12.5Hz)

semantic_tokens = codes[:, 0]
acoustic_tokens = codes[:, 1:]
```

Pierwsza książka kodowa (codebook 0) jest dostrojona do cech modelu WavLM. Pozwala to na wytrenowanie modelu LLM mapującego tekst bezpośrednio na tokeny semantyczne (co jest znacznie prostszym zadaniem niż bezpośrednia synteza surowego audio). Następnie osobny dekoder akustyczny generuje finalną falę dźwiękową na podstawie tokenów semantycznych oraz wektora referencyjnego mówcy.

### Krok 4: Dlaczego modelowanie autoregresyjne na tokenach kodeków jest wydajne

Dla 10-sekundowej wypowiedzi w formacie kodeka Mimi (12.5 Hz, 8 książek kodowych):

$$\text{Liczba tokenów} = 10 \text{ s} \times 12.5 \text{ Hz} \times 8 \text{ codebooks} = 1000 \text{ tokenów}$$

Sekwencja złożona z 1000 tokenów jest bardzo krótka i łatwa do przetworzenia. Model Transformer o rozmiarze 256M parametrów jest w stanie wygenerować taki ciąg w czasie zaledwie kilku milisekund na nowoczesnej karcie graficznej.

## Sugerowane rozwiązania (2026)

| Zadanie | Rekomendowany kodek |
|------|-------|
| Synteza muzyki ogólnej | EnCodec (24 kHz) |
| Systemy wymagające najwyższej jakości rekonstrukcji | DAC (44.1 kHz) |
| Uczenie modeli językowych (LM) na mowie (TTS) | SNAC lub Mimi |
| Systemy konwersacyjne o niskiej latencji (duplex) | Mimi (12.5 Hz) |
| Synteza efektów dźwiękowych z tekstu | EnCodec + enkoder tekstowy T5 |

*Złota zasada:* **Jeśli projektujesz generatywny model audio oparty o LLM/Transformer, wybierz Mimi lub SNAC. Jeśli budujesz standardowy system kompresji lub transmisji audio, użyj kodeka Opus.**

## Typowe pułapki

- **Stosowanie zbyt wielu książek kodowych.** Zwiększanie liczby książek kodowych poprawia jakość rekonstrukcji, ale drastycznie wydłuża sekwencję wejściową dla modelu LLM. Optymalnym kompromisem jest stosowanie 8–12 książek kodowych.
- **Niedopasowanie częstotliwości ramek w potoku.** Próba trenowania modelu LLM na tokenach z kodeka Mimi (12.5 Hz), a następnie syntezy za pomocą dekodera EnCodec (50 Hz/75 Hz) bez odpowiedniego resamplingu doprowadzi do awarii systemu.
- **Traktowanie wszystkich książek kodowych w ten sam sposób.** W modelach semantycznych pierwsza książka (codebook 0) odpowiada za treść – jej uszkodzenie uniemożliwia zrozumienie słów. Uszkodzenie ostatniej książki (np. codebook 7) wpływa jedynie na drobne niuanse akustyczne.
- **Ocena kodeka wyłącznie po jakości rekonstrukcji.** Kodek może charakteryzować się świetną wiernością rekonstrukcji (np. DAC), ale być bezużyteczny do modelowania językowego, jeśli jego tokeny nie niosą wyraźnych struktur semantycznych.

## Zadanie do wykonania

Zapisz jako `outputs/skill-codec-picker.md`. Dobierz optymalny kodek dla zadanego zadania syntezy generatywnej lub kompresji audio.

## Ćwiczenia

1. **Łatwe.** Uruchom skrypt `code/main.py`. Zawiera on uproszczoną implementację kwantyzatora wektorów resztkowych (RVQ) i mierzy błąd rekonstrukcji w zależności od liczby użytych książek kodowych.
2. **Średnie.** Zainstaluj bibliotekę `encodec` i porównaj wierność rekonstrukcji nagrania dla 1, 4, 8 i 32 książek kodowych. Przedstaw wykres MSE w funkcji przepływności (bitrate).
3. **Trudne.** Załaduj model Mimi i zakoduj przykładowe nagranie. Podmień wartości w pierwszej książce kodowej (codebook 0) na losowe liczby całkowite i dokonaj dekodowania. Wykonaj ten sam eksperyment dla ostatniej książki kodowej (codebook 7). Porównaj brzmienie – modyfikacja pierwszej książki powinna całkowicie zniszczyć zrozumiałość słów, podczas gdy zaburzenie ostatniej książki będzie niemal niesłyszalne.

## Kluczowe terminy

| Termin | Potoczne określenie | Co to naprawdę oznacza |
|------|-----------------|----------------------|
| RVQ | Kwantyzacja resztkowa | Residual Vector Quantization; wieloetapowa kwantyzacja wektorowa, w której każdy kolejny stopień kwantyzuje błąd rekonstrukcji stopnia poprzedniego. |
| Frame Rate | Częstotliwość ramek | Liczba ramek tokenów generowana przez kodek na sekundę sygnału audio. Im niższa, tym krótsza sekwencja dla modelu Transformer. |
| Semantic Codebook | Książka semantyczna | Pierwsza książka kodowa (codebook 0) w kodekach takich jak Mimi, destylowana z modeli SSL w celu reprezentowania czystej treści językowej. |
| Acoustic Codebooks | Książki akustyczne | Książki kodowe kodujące informacje o barwie głosu, prozodii oraz szczegółach tła. |
| PESQ / ViSQOL | Jakość percepcyjna | Obiektywne metryki automatycznej oceny jakości mowy (PESQ) i ogólnego audio (ViSQOL), korelujące z ludzkimi ocenami MOS. |
| EnCodec | Kodek firmy Meta | Jeden z pierwszych powszechnie stosowanych neuronowych kodeków audio opartych o architekturę RVQ. |
| Mimi | Kodek Kyutai | Nowoczesny neuronowy kodek o częstotliwości 12.5 Hz realizujący jawny podział semantyczno-akustyczny. |

## Dalsze czytanie

- [Défossez et al. (2022). High Fidelity Neural Audio Compression](https://arxiv.org/abs/2210.13438) — publikacja wprowadzająca kodek EnCodec.
- [Kumar et al. (2023). High-Fidelity Audio Compression with Improved RVQGAN](https://arxiv.org/abs/2306.06546) — publikacja wprowadzająca model Descript Audio Codec (DAC).
- [Siuzdak (2024). Neural Audio Compression with Multi-Scale Residual Vector Quantization](https://arxiv.org/abs/2410.14411) — specyfikacja modelu SNAC.
- [Kyutai Mimi Codec Explainer](https://kyutai.org/codec-explainer) — opis technologii podziału semantyczno-akustycznego w modelu Mimi.
- [Borsos et al. (2022). AudioLM: a Language Modeling Approach to Audio Generation](https://arxiv.org/abs/2209.03143) — pionierska praca nad hierarchicznym modelowaniem audio.
