# Rozpoznawanie mowy (ASR) — CTC, RNN-T, Atencja

> Rozpoznawanie mowy to klasyfikacja dźwięku w czasie, połączona w całość za pomocą modelu sekwencyjnego, który uwzględnia reguły językowe oraz pauzy (ciszę). CTC, RNN-T oraz mechanizm atencji (uwagi) to trzy główne podejścia do tego problemu. Wybierz jedno z nich i zrozum zasady jego działania.

**Typ:** Kompendium  
**Języki:** Python  
**Wymagania wstępne:** Faza 6 · 02 (spektrogramy i filtry melowe), Faza 5 · 08 (CNN i RNN dla tekstu), Faza 5 · 10 (Mechanizm atencji)  
**Czas:** ~45 minut  

## Problem

Dysponujesz 10-sekundowym nagraniem audio o częstotliwości próbkowania 16 kHz. Chcesz uzyskać tekstową transkrypcję, np. „włącz światło w kuchni”. Wyzwanie ma charakter strukturalny: ramki audio nie są wyrównane jeden do jednego z akustycznymi jednostkami tekstu (znakami czy słowami). Wypowiedzenie słowa „OK” może zająć 200 ms lub 1200 ms. Cisza przerywa wypowiedź. Niektóre fonemy trwają dłużej niż inne. Liczba tokenów wyjściowych nie jest z góry znana.

Do rozwiązania tego problemu stosuje się trzy główne formuły:

1. **CTC (Connectionist Temporal Classification).** Generuje prawdopodobieństwa tokenów dla każdej ramki, w tym specjalnego tokenu pustego (*blank*). W procesie dekodowania scala powtórzenia i usuwa tokeny puste. Jest to model nieautoregresywny i szybki. Używany m.in. przez wav2vec 2.0 oraz MMS.
2. **RNN-T (Recurrent Neural Network Transducer).** Wspólna sieć (joint network) przewiduje kolejny token na podstawie wyjścia enkodera audio oraz historii dotychczas wygenerowanych tokenów. Doskonale nadaje się do przetwarzania strumieniowego. Używany w systemach ASR działających bezpośrednio na urządzeniach użytkownika (np. rozwiązania Google, NVIDIA Parakeet).
3. **Atencyjny model koder-dekoder (Encoder-Decoder with Attention).** Koder kompresuje sygnał audio do stanów ukrytych, a dekoder stosuje atencję krzyżową (cross-attention) w celu autoregresyjnego generowania kolejnych tokenów tekstu. Używany m.in. przez Whisper oraz SeamlessM4T.

W 2026 r. wskaźnik SOTA WER na zbiorze testowym LibriSpeech wynosi około 1,4% (Parakeet-TDT-1.1B od NVIDIA) oraz 1,58% (Whisper-Large-v3-turbo). Różnice w dokładności są niewielkie, natomiast różnice w wymaganiach wdrożeniowych – ogromne.

## Koncepcja

![Trzy formuły ASR: CTC, RNN-T oraz koder-dekoder z atencją](../assets/asr-formulations.svg)

**Zasada działania CTC.** Enkoder generuje `T` rozkładów prawdopodobieństwa dla każdej ramki czasowej nad słownikiem o rozmiarze `V+1` (V znaków + token pusty `_`). Dla sekwencji docelowej `y` o długości `U < T` bierzemy pod uwagę każdą ścieżkę wyrównania ramek, która po scaleniu daje sekwencję `y`. Funkcja straty CTC sumuje prawdopodobieństwa wszystkich takich ścieżek. Wnioskowanie zachłanne: wybierz najbardziej prawdopodobny token dla każdej ramki, scal powtórzenia, a na koniec usuń tokeny puste.

*Zalety:* brak autoregresji (wysoka szybkość), łatwość przetwarzania strumieniowego, brak opóźnienia spowodowanego patrzeniem w przyszłość.  
*Wada:* tzw. *założenie o warunkowej niezależności* (conditional independence assumption) — predykcja dla każdej ramki jest niezależna od pozostałych, co oznacza brak wewnętrznego modelu językowego. Problem ten rozwiązuje się poprzez integrację zewnętrznego modelu językowego (LM) podczas poszukiwania wiązkowego (beam search) lub tzw. płytką integrację (shallow fusion).

**Zasada działania RNN-T.** Dodaje sieć predyktora (predictor network), która koduje historię wygenerowanych tokenów, oraz sieć łączącą (joint network), która scala stany predyktora oraz enkodera audio we wspólny rozkład nad słownikiem `V+1` (gdzie `+1` oznacza token pusty / brak emisji). Rozwiązanie to jawnie modeluje zależności językowe ignorowane przez CTC. Pozwala na przetwarzanie strumieniowe, ponieważ każdy krok zależy wyłącznie od przeszłych ramek i wygenerowanych wcześniej tokenów.

*Zalety:* naturalne przetwarzanie strumieniowe + wbudowany model językowy.  
*Wada:* proces trenowania jest złożony i wymaga dużej ilości pamięci (trójwymiarowa siatka obliczeń funkcji straty). Wydajne obliczanie straty RNN-T wymaga dedykowanych, zoptymalizowanych kerneli.

**Modele koder-dekoder z atencją.** Koder (zwykle 6–32 warstw Transformer) przetwarza ramki log-mel. Dekoder (również 6–32 warstw Transformer) wykorzystuje atencję krzyżową (cross-attention) z wyjściami kodera do autoregresyjnego generowania tokenów. Brak sztywnych ograniczeń dotyczących wyrównania czasowego – uwaga może być skierowana na dowolny fragment nagrania. Modele te nie wspierają bezpośrednio przetwarzania strumieniowego (wymaga to specjalnych modyfikacji, np. Whisper-Streaming).

*Zalety:* najwyższa jakość transkrypcji w trybie offline, łatwość trenowania przy użyciu standardowych narzędzi seq2seq.  
*Wada:* opóźnienie rośnie wraz z długością sekwencji wyjściowej ze względu na autoregresywny charakter generowania; brak natywnego wsparcia dla przesyłania strumieniowego bez dodatkowej inżynierii.

### WER: jedna metryka, by wszystkimi rządzić

**Word Error Rate (WER)** = `(S + D + I) / N`, gdzie `S` to substytucje, `D` – delecje, `I` – insercje, a `N` to całkowita liczba słów w tekście referencyjnym. Odpowiada to odległości edycyjnej Levenshteina na poziomie słów. Im niższa wartość, tym lepiej. WER powyżej 20% jest zazwyczaj nieakceptowalny w systemach produkcyjnych; wynik poniżej 5% oznacza jakość porównywalną z człowiekiem dla czytanej mowy.

Wyniki dla standardowych benchmarków (stan na 2026 r.):

| Model | LibriSpeech test-clean | LibriSpeech test-other | Rozmiar |
|-------|----------------------------|----------------------|------|
| Parakeet-TDT-1.1B | 1,40% | 2,78% | 1.1B parametrów |
| Whisper-Large-v3-turbo | 1,58% | 3,03% | 809M parametrów |
| Canary-1B Flash | 1,48% | 2,87% | 1B parametrów |
| SeamlessM4T v2 | 1,7% | 3,5% | 2.3B parametrów |

Wszystkie te modele oparte są na architekturze koder-dekoder lub RNN-T. Systemy oparte wyłącznie na czystym CTC (np. wav2vec 2.0) osiągają na zbiorze test-clean wyniki w granicach 1,8–2,1%.

## Implementacja krok po kroku

### Krok 1: Zachłanne dekodowanie CTC (Greedy Decoding)

```python
def ctc_greedy(frame_logits, blank=0, vocab=None):
    # frame_logits: lista wektorów prawdopodobieństw dla każdej ramki
    preds = [max(range(len(p)), key=lambda i: p[i]) for p in frame_logits]
    out = []
    prev = -1
    for p in preds:
        if p != prev and p != blank:
            out.append(p)
        prev = p
    return "".join(vocab[i] for i in out) if vocab else out
```

Dwie podstawowe zasady: scalaj bezpośrednio powtarzające się wartości, a następnie usuń tokeny puste. Przykład: `a a _ _ a b b _ c` -> `a a b c`.

### Krok 2: Poszukiwanie wiązkowe CTC (Beam Search)

```python
def ctc_beam(frame_logits, beam=8, blank=0):
    import math
    beams = [([], 0.0)]  # (sekwencja tokenów, log_prob)
    for p in frame_logits:
        log_p = [math.log(max(pi, 1e-10)) for pi in p]
        candidates = []
        for seq, lp in beams:
            for t, lpt in enumerate(log_p):
                new = seq[:] if t == blank else (seq + [t] if not seq or seq[-1] != t else seq)
                candidates.append((new, lp + lpt))
        candidates.sort(key=lambda x: -x[1])
        beams = candidates[:beam]
    return beams[0][0]
```

W systemach produkcyjnych stosuje się poszukiwanie wiązkowe oparte na prefiksach z integracją zewnętrznego modelu językowego (LM fusion); powyższy kod przedstawia koncepcyjny szkielet tego rozwiązania.

### Krok 3: Obliczanie WER

```python
def wer(ref, hyp):
    r, h = ref.split(), hyp.split()
    dp = [[0] * (len(h) + 1) for _ in range(len(r) + 1)]
    for i in range(len(r) + 1):
        dp[i][0] = i
    for j in range(len(h) + 1):
        dp[0][j] = j
    for i in range(1, len(r) + 1):
        for j in range(1, len(h) + 1):
            cost = 0 if r[i - 1] == h[j - 1] else 1
            dp[i][j] = min(
                dp[i - 1][j] + 1,
                dp[i][j - 1] + 1,
                dp[i - 1][j - 1] + cost,
            )
    return dp[len(r)][len(h)] / max(1, len(r))
```

### Krok 4: Wnioskowanie z użyciem modelu Whisper

```python
import whisper
model = whisper.load_model("large-v3-turbo")
result = model.transcribe("clip.wav")
print(result["text"])
```

Niezwykle prosty w użyciu i zarazem jeden z najpotężniejszych modeli ASR w 2026 r. Działa na procesorze graficznym z 24 GB pamięci VRAM z prędkością około 20-krotnie szybszą niż czas rzeczywisty.

### Krok 5: Przetwarzanie strumieniowe z użyciem potoków Hugging Face

```python
from transformers import pipeline
asr = pipeline("automatic-speech-recognition", model="nvidia/parakeet-tdt-1.1b")
for chunk in streaming_audio():
    print(asr(chunk, return_timestamps=True))
```

Strumieniowy ASR wymaga ograniczenia uwagi enkodera do określonych okien czasowych oraz przekazywania stanu pomiędzy krokami. Warto korzystać z bibliotek dobrze wspierających ten proces (np. NeMo dla modeli Parakeet, lub potoków Hugging Face z parametrem `chunk_length_s`).

## Sugerowane rozwiązania (2026)

| Scenariusz | Wybierz |
|----------|------|
| Język angielski, tryb offline, maksymalna jakość | Whisper-large-v3-turbo |
| Obsługa wielu języków, wysoka odporność | SeamlessM4T v2 |
| Przetwarzanie strumieniowe, minimalne opóźnienia | Parakeet-TDT-1.1B lub NVIDIA Riva |
| Urządzenia brzegowe (edge/mobile), opóźnienie <500 ms | Skwantowany model Whisper-Tiny lub Moonshine (2024) |
| Długie nagrania | Whisper z segmentacją opartą o VAD (np. WhisperX) |
| Wąskie domeny specjalistyczne (medycyna, prawo) | Dostrojenie modelu wav2vec 2.0 + dedykowany model językowy (LM) |

## Typowe pułapki (wciąż aktualne w 2026 r.)

- **Brak detekcji aktywności głosowej (VAD).** Uruchamianie modelu Whisper na fragmentach zawierających wyłącznie ciszę prowadzi do halucynacji (np. generowania powtarzających się zwrotów typu „Dzięki za obejrzenie!”). Przed przekazaniem dźwięku do modelu ASR zawsze filtruj go za pomocą VAD.
- **Ewaluacja WER na surowym tekście.** Obliczaj WER na poziomie słów dopiero po przeprowadzeniu normalizacji tekstu (zamiana na małe litery, usunięcie znaków interpunkcyjnych i ujednolicenie liczb).
- **Błędy automatycznej detekcji języka (LID).** Wbudowany mechanizm LID w modelu Whisper może błędnie klasyfikować mocno zaszumione nagrania jako nietypowe języki (np. walijski lub japoński). Jeśli język jest znany z góry, zawsze wymuszaj go za pomocą parametru, np. `language="pl"`.
- **Brak dzielenia długich nagrań.** Model Whisper przetwarza dźwięk w 30-sekundowych oknach. W przypadku dłuższych nagrań stosuj parametry takie jak `chunk_length_s=30` i `stride_time_s=5`.

## Zadanie do wykonania

Zapisz jako `outputs/skill-asr-picker.md`. Dobierz model, strategię dekodowania, podział na fragmenty oraz integrację z modelem językowym (LM fusion) dla zadanego scenariusza wdrożeniowego.

## Ćwiczenia

1. **Łatwe.** Uruchom skrypt `code/main.py`. Wykonuje on zachłanne dekodowanie przykładowego wyjścia CTC i oblicza WER w porównaniu do tekstu referencyjnego.
2. **Średnie.** Zaimplementuj pełne poszukiwanie wiązkowe oparte na prefiksach w Kroku 2 (uwzględniając regułę scalania powtórzeń przedzielonych tokenem pustym). Porównaj wyniki z dekodowaniem zachłannym na 10 syntetycznych przykładach.
3. **Trudne.** Pobierz zbiór [LibriSpeech test-clean](https://www.openslr.org/12) i uruchom model `whisper-large-v3-turbo` na pierwszych 100 wypowiedziach. Oblicz wskaźnik WER i porównaj go z oficjalnie deklarowanymi wynikami.

## Kluczowe terminy

| Termin | Potoczne określenie | Co to naprawdę oznacza |
|------|-----------------|----------------------|
| CTC | Connectionist Temporal Classification | Funkcja straty umożliwiająca trenowanie modeli bez wcześniejszego wyrównania czasowego ramka-token. Model nieautoregresywny. |
| RNN-T | Transducer | Rozszerzenie CTC o dodatkową sieć predyktora modelującą zależności językowe; standard w systemach strumieniowych. |
| Atencja koder-dekoder | Encoder-Decoder Attention | Architektura seq2seq wykorzystująca atencję krzyżową między enkoderem audio a dekoderem tekstu; zapewnia najwyższą jakość offline. |
| WER | Word Error Rate | Podstawowa metryka jakości transkrypcji: `(S+D+I)/N` na poziomie słów. |
| Blank | Token pusty | Specjalny symbol w CTC (oznaczany często jako `_`), oznaczający brak emisji znaku w danej ramce czasowej. |
| LM Fusion | Integracja modelu językowego | Łączenie prawdopodobieństw z zewnętrznego modelu językowego (np. n-gram lub RNN) podczas wyszukiwania wiązkowego w celu poprawy gramatyczności tekstu. |
| VAD | Detektor aktywności głosowej | Voice Activity Detection; algorytm wykrywający obecność mowy w sygnale audio w celu pomijania fragmentów ciszy. |

## Dalsze czytanie

- [Graves et al. (2006). Connectionist Temporal Classification](https://www.cs.toronto.edu/~graves/icml_2006.pdf) — oryginalna publikacja wprowadzająca CTC.
- [Graves (2012). Sequence Transduction with Recurrent Neural Networks](https://arxiv.org/abs/1211.3711) — oryginalna publikacja wprowadzająca RNN-T.
- [Radford et al. / OpenAI (2022). Whisper: Robust Speech Recognition via Large-Scale Weak Supervision](https://arxiv.org/abs/2212.04356) — publikacja opisująca model Whisper.
- [NVIDIA NeMo — Parakeet-TDT 1.1B](https://huggingface.co/nvidia/parakeet-tdt-1.1b) — dokumentacja modelu wiodącego w benchmarkach ASR.
- [Hugging Face — Open ASR Leaderboard](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard) — aktualizowane na bieżąco zestawienie modeli ASR.
