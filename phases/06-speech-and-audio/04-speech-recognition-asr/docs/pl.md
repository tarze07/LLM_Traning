# Rozpoznawanie mowy (ASR) — CTC, RNN-T, Uwaga

> Rozpoznawanie mowy to klasyfikacja dźwięku na każdym etapie, połączona w całość za pomocą modelu sekwencyjnego, który zna angielski i ciszę. CTC, RNN-T i uwaga to trzy sposoby, aby to zrobić. Wybierz jedno i zrozum dlaczego.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 6 · 02 (spektrogramy i Mel), Faza 5 · 08 (CNN i RNN dla tekstu), Faza 5 · 10 (Uwaga)
**Czas:** ~45 minut

## Problem

Masz 10-sekundowy klip 16 kHz. Chcesz ciąg znaków: „włącz światło w kuchni”. Wyzwanie ma charakter strukturalny: ramki audio nie są wyrównane jeden do jednego ze znakami. Słowo „OK” może zająć 200 ms lub 1200 ms. Cisza przerywa wypowiedź. Niektóre fonemy są dłuższe niż inne. Liczba żetonów wyjściowych nie jest z góry znana.

Rozwiązują ten problem trzy formuły:

1. **CTC (konektywistyczna klasyfikacja czasowa).** Emituj prawdopodobieństwa tokena na klatkę, łącznie ze specjalnym *pustym*. Zwija powtórzenia i spacje w czasie dekodowania. Nieautoregresywny, szybki. Używany przez wav2vec 2.0, MMS.
2. **RNN-T (przetwornik rekurencyjnej sieci neuronowej).** Wspólna sieć przewiduje następny token na podstawie ramki kodera i poprzednich tokenów. Możliwość przesyłania strumieniowego. Używany przez funkcję ASR na urządzeniu firmy Google, NVIDIA Parakeet.
3. **Uwaga koder-dekoder.** Koder kompresuje dźwięk do stanów ukrytych, dekoder uczestniczy krzyżowo w celu autoregresyjnego generowania tokenów. Używany przez Whisper, SeamlessM4T.

W 2026 r. SOTA WER w trybie testowym LibriSpeech wynosi 1,4% (Parakeet-TDT-1.1B, NVIDIA) i 1,58% (Whisper-Large-v3-turbo). Różnice są niewielkie; różnice we wdrażaniu są ogromne.

## Koncepcja

![Trzy formuły ASR: CTC, RNN-T, koder uwagi-dekoder](../assets/asr-formulations.svg)

**Intuicja CTC.** Pozwól, aby koder wyprowadzał `T` rozkłady na poziomie ramki na tokeny `V+1` (znaki V + puste). W przypadku łańcucha docelowego `y` o długości `U < T` liczy się każde wyrównanie ramki, które zwija się do `y`. Sumy strat CTC we wszystkich takich zestawieniach. Wnioskowanie: argmax na klatkę, zwiń powtórzenia, usuń spacje.

Zalety: brak autoregresji, możliwość przesyłania strumieniowego, brak wyprzedzania. Wada: *założenie warunkowej niezależności* — każda predykcja ramki jest niezależna od pozostałych, więc nie ma wewnętrznego modelu językowego. Napraw za pomocą zewnętrznego LM poprzez przeszukiwanie wiązki lub płytką fuzję.

**Intuicja RNN-T.** Dodaje sieć *predyktorów*, która osadza historię tokenów, oraz *łącznik* łączący stan predyktora z ramką kodera we wspólną dystrybucję na `V+1` (`+1` to wartość null/no-emit). Jawnie modeluje zależność warunkową ignorowaną przez CTC. Możliwość transmisji strumieniowej, ponieważ każdy krok warunkuje tylko przeszłe klatki i przeszłe tokeny.

Zalety: możliwość przesyłania strumieniowego + wewnętrzny LM. Wada: trening jest bardziej złożony i wymaga dużej pamięci (siatka strat 3D); Jądra strat RNN-T stanowią osobną kategorię bibliotek.

**Uwaga koder-dekoder.** Koder (6-32 warstw transformatora) w ramkach log-mel. Dekoder (6–32 warstw transformatora) łączy się krzyżowo z wyjściami kodera w celu autoregresyjnego generowania tokenów. Brak ograniczeń dotyczących wyrównania — uwaga może być skierowana w dowolne miejsce w dźwięku. Nie można przesyłać strumieniowo, chyba że ograniczysz uwagę (fragmenty Whisper-Streaming, 2024).

Zalety: najwyższa jakość w trybie offline ASR, łatwe do trenowania przy użyciu standardowych narzędzi seq2seq. Wada: opóźnienie autoregresyjne jest proporcjonalne do długości sygnału wyjściowego; nie można przesyłać strumieniowo bez inżynierii.

### WER: jedna liczba

**Współczynnik błędów słownych** = `(S + D + I) / N`, gdzie S=podstawienia, D=delecje, I=wstawienia, N=liczba słów referencyjnych. Odpowiada odległości edycji Levenshteina na poziomie słowa. Niżej jest lepiej. WER powyżej 20% jest generalnie bezużyteczny; poniżej 5% to parzystość człowieka dla czytanej mowy. Liczby za rok 2026 w standardowych benchmarkach:

| Modelka | Test-czyszczenie LibriSpeech | LibriSpeech test-inne | Rozmiar |
|-------|----------------------------|----------------------|------|
| Parakeet-TDT-1.1B | 1,40% | 2,78% | Parametry 1.1B |
| Whisper-Large-v3-turbo | 1,58% | 3,03% | 809M |
| Canary-1B Flash | 1,48% | 2,87% | 1B |
| Bezszwowe M4T v2 | 1,7% | 3,5% | 2.3B |

Wszystkie są oparte na koderze-dekoderze lub RNN-T. Systemy czystego CTC (wav2vec 2.0) przy czystości testowej wynoszą około 1,8–2,1%.

## Zbuduj to

### Krok 1: zachłanne dekodowanie CTC

```python
def ctc_greedy(frame_logits, blank=0, vocab=None):
    # frame_logits: list of per-frame probability vectors
    preds = [max(range(len(p)), key=lambda i: p[i]) for p in frame_logits]
    out = []
    prev = -1
    for p in preds:
        if p != prev and p != blank:
            out.append(p)
        prev = p
    return "".join(vocab[i] for i in out) if vocab else out
```

Dwie zasady: zwijaj kolejne powtórzenia, usuwaj puste miejsca. Przykład: `a a _ _ a b b _ c` → `a a b c`.

### Krok 2: CTC przeszukiwania wiązki

```python
def ctc_beam(frame_logits, beam=8, blank=0):
    import math
    beams = [([], 0.0)]  # (tokens, log_prob)
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

Produkcja wykorzystuje wyszukiwanie wiązek drzewiastych z prefiksami za pomocą fuzji LM; to jest szkielet pojęciowy.

### Krok 3: WER

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

### Krok 4: wnioskowanie przeciwko Szeptowi

```python
import whisper
model = whisper.load_model("large-v3-turbo")
result = model.transcribe("clip.wav")
print(result["text"])
```

Jednolinijkowy najsilniejszy ogólny ASR w 2026 r. Działa na procesorze graficznym 24 GB w czasie ~20× czasu rzeczywistego.

### Krok 5: przesyłanie strumieniowe za pomocą Parakeet lub wav2vec 2.0

```python
from transformers import pipeline
asr = pipeline("automatic-speech-recognition", model="nvidia/parakeet-tdt-1.1b")
for chunk in streaming_audio():
    print(asr(chunk, return_timestamps=True))
```

Przesyłanie strumieniowe ASR wymaga fragmentarycznej uwagi kodera i stanu przeniesienia; użyj biblioteki, która ją obsługuje (NeMo dla Parakeet, potok `transformers` z `chunk_length_s`).

## Użyj tego

Stos na rok 2026:

| Sytuacja | Wybierz |
|----------|------|
| Angielski, offline, maksymalna jakość | Whisper-large-v3-turbo |
| Wielojęzyczny, solidny | BezproblemowyM4T v2 |
| Przesyłanie strumieniowe, małe opóźnienia | Parakeet-TDT-1.1B lub Riva |
| Edge, mobilny, opóźnienie <500 ms | Whisper-Tiny kwantyzowany lub Moonshine (2024) |
| Długa forma | Szept z fragmentacją opartą na VAD (WhisperX) |
| Specyficzne dla domeny (medyczne, prawne) | Dostosuj fuzję wav2vec 2.0 + domena LM |

## Pułapki, które nadal będą widoczne w 2026 r

- **Brak VAD.** Uruchamianie szeptu w ciszy powoduje halucynacje („Dzięki za obejrzenie!”). Zawsze bramkuj z VAD.
- **Znak vs słowo vs podsłowo WER.** Raport WER na poziomie słowa *po* normalizacji (małe litery, usunięta interpunkcja).
- **Przesunięcie identyfikatora języka.** Automatyczny LID Whispera błędnie kieruje zaszumione klipy na język japoński lub walijski; wymuś `language="en"`, gdy wiesz.
- **Długie klipy bez fragmentacji.** Szept ma 30-sekundowe okno. Używaj `chunk_length_s=30, stride=5` dłużej.

## Wyślij to

Zapisz jako `outputs/skill-asr-picker.md`. Wybierz model, strategię dekodowania, fragmentację i fuzję LM dla danego celu wdrożenia.

## Ćwiczenia

1. **Łatwe.** Uruchom `code/main.py`. Chciwie dekoduje ręcznie wykonane wyjście CTC i oblicza WER na podstawie odniesienia.
2. **Średni.** Prawidłowo zaimplementuj wyszukiwanie belek przedrostkowych w kroku 2 (uwzględnij regułę łączenia z pustymi miejscami). Porównaj z zachłannym na 10-przykładowym syntetycznym zestawie danych.
3. **Trudne.** Użyj `whisper-large-v3-turbo` na [LibriSpeech test-clean](https://www.openslr.org/12). Oblicz WER dla pierwszych 100 wypowiedzi. Porównaj z opublikowanymi liczbami.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| CTC | Strata pustym żetonem | Marginalny dla wszystkich wyrównań ramki do tokenu; nie-AR. |
| RNN-T | Strata transmisji | CTC + predyktor następnego tokenu; obsługuje kolejność słów. |
| Uwaga enc-dec | Szeptem | Koder + dekoder krzyżowy; najlepsza jakość offline. |
| WER | Numer, który zgłaszasz | `(S+D+I)/N` na poziomie słowa. |
| Puste | Pustka | Specjalny token w CTC sygnalizujący „brak emisji tej ramki”. |
| Fuzja LM | Model języka zewnętrznego | Dodawaj ważone sondy logujące LM podczas wyszukiwania wiązki. |
| VAD | Brama ciszy | Detektor aktywności głosowej; przycina niemowę. |

## Dalsze czytanie

- [Graves i in. (2006). Connectionist Temporal Classification] (https://www.cs.toronto.edu/~graves/icml_2006.pdf) — artykuł CTC.
- [Groby (2012). Transdukcja sekwencji za pomocą RNN](https://arxiv.org/abs/1211.3711) — artykuł RNN-T.
- [Radford i in. /OpenAI (2022). Whisper: Solidne rozpoznawanie mowy poprzez słaby nadzór na dużą skalę](https://arxiv.org/abs/2212.04356) – artykuł kanoniczny z 2022 r.; rozszerzenie v3-turbo w 2024 roku.
— [NVIDIA NeMo — karta Parakeet-TDT](https://huggingface.co/nvidia/parakeet-tdt-1.1b) — lider tabeli liderów Open ASR 2026.
– [Hugging Face — tablica liderów Open ASR](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard) — test porównawczy na żywo dla ponad 25 modeli.