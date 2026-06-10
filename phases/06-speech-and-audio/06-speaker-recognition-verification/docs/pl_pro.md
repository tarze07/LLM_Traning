# Rozpoznawanie i weryfikacja mówcy

> ASR odpowiada na pytanie „co zostało powiedziane?”, natomiast rozpoznawanie mówcy (Speaker Recognition) – „kto to powiedział?”. Matematyczne podstawy są zbliżone – wektory osadzeń (embeddings) i podobieństwo cosinusowe – jednak w systemach produkcyjnych kluczową rolę odgrywa jedna metryka: EER.

**Typ:** Kompendium  
**Języki:** Python  
**Wymagania wstępne:** Faza 6 · 02 (spektrogramy i filtry melowe), Faza 5 · 22 (modele osadzeń)  
**Czas:** ~45 minut  

## Problem

Użytkownik wypowiada określone hasło. Chcesz sprawdzić, czy jest to osoba, za którą się podaje (*weryfikacja*, zadanie 1:1), czy też system ma dopasować głos do jednego ze zarejestrowanych mówców w bazie danych (*identyfikacja*, zadanie 1:N)? A może żadne z powyższych, ponieważ nagranie pochodzi od niezarejestrowanej osoby (*scenariusz otwarty / open-set*)?

Przed rokiem 2018 standardem były modele GMM-UBM oraz i-wektory (i-vectors). Zapewniały one akceptowalny poziom EER, ale były bardzo wrażliwe na zmianę kanału transmisyjnego (np. mikrofon telefonu vs. wbudowany w laptopie) oraz emocje mówcy. W latach 2018–2022 popularność zyskały x-wektory (x-vectors) oparse na architekturze TDNN trenowanej z marginesem kątowym. Od 2022 roku dominują zaawansowane reprezentacje ECAPA-TDNN oraz model WavLM. Do 2026 roku standardem stały się trzy modele i jedna kluczowa metryka.

Metryką tą jest **EER (Equal Error Rate)** — równoważny współczynnik błędów. Określa on punkt, w którym próg decyzyjny daje równy odsetek fałszywych akceptacji (FAR - False Acceptance Rate) oraz fałszywych odrzuceń (FRR - False Rejection Rate). Wskaźnik ten jest standardem w publikacjach naukowych, benchmarkach i specyfikacjach systemów biometrycznych.

## Koncepcja

![Rejestracja i potok weryfikacji mówcy z obliczaniem podobieństwa cosinusowego oraz EER](../assets/speaker-verification.svg)

**Przepływ procesu.** Rejestracja (enrollment): nagranie od 5 do 30 sekund głosu mówcy w celu wygenerowania wektora cech (osadzenia) o stałym wymiarze (np. 192 dla ECAPA-TDNN, 256 dla WavLM-large). Weryfikacja (verification): ekstrakcja wektora cech z próbki testowej, obliczenie podobieństwa cosinusowego do wektora referencyjnego i porównanie wyniku z określonym progiem decyzyjnym.

**ECAPA-TDNN (2020, wciąż niezwykle popularny w 2026 r.).** Architektura oparta na sieci TDNN (Time-Delay Neural Network) z mechanizmami propagacji i agregacji kanałów. Wykorzystuje jednowymiarowe bloki splotowe z mechanizmem Squeeze-and-Excitation (SE), wielogłowicową atencję do agregacji cech (Multi-Head Attention Pooling) oraz warstwę liniową mapującą do 192-wymiarowego wektora. Modele te trenuje się zazwyczaj na zbiorze VoxCeleb 1+2 (ponad 7000 mówców, 1,1 mln wypowiedzi) z funkcją straty AAM-softmax (Additive Angular Margin Softmax).

**WavLM-SV (2022+).** Wykorzystuje wstępnie wytrenowany, potężny model samonadzorowany (SSL) WavLM dostrojony z funkcją straty AAM-softmax. Zapewnia najwyższą jakość reprezentacji, ale cechuje się wolniejszym działaniem i większym rozmiarem (ponad 300 MB w porównaniu do 15 MB dla ECAPA-TDNN).

**x-vector (klasyczny baseline).** Architektura TDNN z warstwą agregującą statystyki (średnia i odchylenie standardowe). Klasyczna metoda, wciąż przydatna na procesorach o ograniczonej wydajności i urządzeniach brzegowych.

**AAM-softmax.** Zmodyfikowana funkcja softmax o dodatkowy margines kary `m` wprowadzony bezpośrednio w przestrzeni kątowej: `cos(θ + m)` dla klasy prawdziwej. Wymusza to silniejszą separację kątową i grupowanie wektorów cech należących do tego samego mówcy. Typowe wartości to `m=0.2` oraz skala `s=30`.

### Metody punktacji (Scoring)

- **Podobieństwo cosinusowe** pomiędzy wektorem referencyjnym (rejestracyjnym) a testowym. Decyzja podejmowana jest na podstawie statycznego lub dynamicznego progu.
- **PLDA (Probabilistic Linear Discriminant Analysis).** Modeluje wektory osadzeń w przestrzeni ukrytej, określając stosunek wiarygodności (likelihood ratio) dla hipotezy o tym samym mówcy vs. o różnych mówcach. Metoda ta pozwala na obniżenie wskaźnika EER o dodatkowe 10–20%. Stosowana głównie w scenariuszach zbioru zamkniętego (closed-set).
- **Normalizacja wyników podobieństwa.** Metody takie jak S-norm lub AS-norm (Adaptive Symmetric Normalization) normalizują wyniki w odniesieniu do kohorty (bazy) innych mówców w celu stabilizacji średniej i odchylenia standardowego. Jest to kluczowy element w scenariuszach międzydomenowych (cross-domain).

### Wartości referencyjne (stan na 2026 r.)

| Model | VoxCeleb1-O EER | Liczba parametrów | Przepustowość (A100) |
|-------|-----------------|--------|--------------------------------|
| x-vector (klasyczny) | 3,10% | 5 M | 400× RT |
| ECAPA-TDNN | 0,87% | 15 M | 200× RT |
| WavLM-SV Large | 0,42% | 316 M | 20× RT |
| Pyannote 3.1 (segmentacja + osadzanie) | 0,65% | 6 M | 100× RT |
| ReDimNet (2024) | 0,39% | 24 M | 100× RT |

### Diaryzacja mówców (Speaker Diarization)

Odpowiada na pytanie: „Kto mówił i w którym momencie?” w nagraniach z udziałem wielu osób. Klasyczny potok: VAD → segmentacja → ekstrakcja osadzeń dla każdego segmentu → klasteryzacja (aglomeracyjna lub spektralna) → wygładzanie granic segmentów. Nowoczesny stos produkcyjny: `pyannote.audio` 3.1, który integruje segmentację, ekstrakcję osadzeń oraz grupowanie w jednym potoku obliczeniowym. Wynik SOTA DER (Diarization Error Rate) w 2026 roku na zbiorze AMI wynosi ok. 15% (w porównaniu do 23% w roku 2022).

## Implementacja krok po kroku

### Krok 1: Uproszczony wektor cech na podstawie statystyk MFCC

```python
def embed_mfcc_stats(signal, sr):
    frames = featurize_mfcc(signal, sr, n_mfcc=13)
    mean = [sum(f[i] for f in frames) / len(frames) for i in range(13)]
    std = [
        math.sqrt(sum((f[i] - mean[i]) ** 2 for f in frames) / len(frames))
        for i in range(13)
    ]
    return mean + std  # 26-wymiarowy wektor
```

*Uwaga:* To rozwiązanie dalekie od SOTA – służy wyłącznie celom demonstracyjnym i testom poprawności kodu w `code/main.py` na syntetycznym zbiorze danych mówców.

### Krok 2: Podobieństwo cosinusowe i weryfikacja

```python
def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    return dot / (na * nb) if na and nb else 0.0

def verify(enroll, test, threshold=0.75):
    return cosine(enroll, test) >= threshold
```

### Krok 3: Obliczanie wskaźnika EER (Equal Error Rate)

```python
def eer(same_scores, diff_scores):
    thresholds = sorted(set(same_scores + diff_scores))
    best = (1.0, 1.0, 0.0)  # (fa, fr, threshold)
    for t in thresholds:
        fr = sum(1 for s in same_scores if s < t) / len(same_scores)
        fa = sum(1 for s in diff_scores if s >= t) / len(diff_scores)
        if abs(fa - fr) < abs(best[0] - best[1]):
            best = (fa, fr, t)
    return (best[0] + best[1]) / 2, best[2]
```

Funkcja zwraca `(eer, threshold_at_eer)`. Zgłoś obie te wartości podczas ewaluacji.

### Krok 4: Weryfikacja przy użyciu biblioteki SpeechBrain

```python
from speechbrain.pretrained import EncoderClassifier

clf = EncoderClassifier.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb")

# rejestracja: uśrednienie wektorów cech z 3-5 czystych próbek nagrań
enroll = torch.stack([clf.encode_batch(load(x)) for x in enrollment_clips]).mean(0)

# weryfikacja
score = clf.similarity(enroll, clf.encode_batch(load("test.wav"))).item()
verdict = score > 0.25   # Domyślny próg dla modelu ECAPA; należy go skalibrować na własnych danych
```

### Krok 5: Diaryzacja z użyciem biblioteki Pyannote

```python
from pyannote.audio import Pipeline

pipe = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1")
diarization = pipe("meeting.wav", num_speakers=None)
for turn, _, speaker in diarization.itertracks(yield_label=True):
    print(f"{turn.start:.1f}–{turn.end:.1f}  {speaker}")
```

## Sugerowane rozwiązania (2026)

| Scenariusz | Rekomendowane rozwiązanie |
|----------|------|
| Weryfikacja 1:1 w systemie zamkniętym, urządzenia edge | Model ECAPA-TDNN + próg podobieństwa cosinusowego |
| Weryfikacja w systemie otwartym (open-set), serwery chmurowe | Model WavLM-SV Large + normalizacja AS-norm |
| Diaryzacja (spotkania, podcasty) | Potok `pyannote/speaker-diarization-3.1` |
| Anti-spoofing (wykrywanie deepfake i nagrań odtwarzanych z głośnika) | Model AASIST lub RawNet2 |
| Systemy o ograniczonych zasobach (np. budzenie głosem KWS) | Model TitaNet-Small (NVIDIA NeMo) |

## Typowe pułapki

- **Niedopasowanie kanałów (channel mismatch).** Model wytrenowany na bazie VoxCeleb (nagrania wideo z serwisu YouTube) nie będzie działał optymalnie na nagraniach z mikrofonów telefonicznych (wąskie pasmo 8 kHz). Zawsze testuj system na rzeczywistych urządzeniach docelowych.
- **Zbyt krótkie wypowiedzi.** Czas trwania nagrania poniżej 3 sekund drastycznie zwiększa wskaźnik EER.
- **Zaszumione próbki referencyjne.** Jedno zanieczyszczone nagranie rejestracyjne psuje wektor referencyjny mówcy. Wymagaj co najmniej 3 czystych nagrań i uśredniaj ich reprezentacje.
- **Sztywny próg decyzyjny.** Próg decyzyjny powinien być dynamicznie dobierany lub kalibrowany na zbiorze walidacyjnym z domeny docelowej, a nie przyjmowany na stałe z publikacji naukowych.
- **Brak normalizacji wektorów przy cosinusie.** Zawsze upewnij się, że wektory są znormalizowane (np. normalizacja L2) przed obliczaniem odległości, aby uniknąć wpływu amplitudy sygnału.

## Zadanie do wykonania

Zapisz jako `outputs/skill-speaker-verifier.md`. Dobierz model, protokół rejestracji, metodę kalibracji progu decyzyjnego oraz mechanizmy zabezpieczające przed próbami oszustwa (anti-spoofing).

## Ćwiczenia

1. **Łatwe.** Uruchom skrypt `code/main.py`. Generuje on profile syntetycznych mówców (o różnych częstotliwościach tonu podstawowego), rejestruje ich w systemie, a następnie oblicza EER dla 100 par testowych.
2. **Średnie.** Wykorzystaj model ECAPA z biblioteki SpeechBrain na 30 nagraniach z bazy VoxCeleb1 (5 mówców po 6 próbek). Porównaj wskaźnik EER uzyskany za pomocą zwykłego podobieństwa cosinusowego oraz z użyciem klasyfikatora PLDA.
3. **Trudne.** Zaprojektuj kompletny proces: rejestracja → diaryzacja → weryfikacja z użyciem `pyannote.audio` i oblicz wskaźnik DER na zbiorze walidacyjnym AMI.

## Kluczowe terminy

| Termin | Potoczne określenie | Co to naprawdę oznacza |
|------|-----------------|----------------------|
| EER | Equal Error Rate | Próg decyzyjny, przy którym odsetek fałszywych akceptacji (FAR) jest równy odsetkowi fałszywych odrzuceń (FRR). |
| Weryfikacja | Zadanie 1:1 | Sprawdzenie tożsamości: „Czy ten głos należy do zadeklarowanego użytkownika X?”. |
| Identyfikacja | Zadanie 1:N | Przypisanie tożsamości: „Do kogo z bazy zarejestrowanych osób należy ten głos?”. |
| Open-set | Zbiór otwarty | Scenariusz, w którym próbka testowa może pochodzić od osoby nieobecnej w bazie zarejestrowanych użytkowników. |
| Enrollment | Rejestracja | Proces zbierania próbek głosu i generowania wzorcowego wektora cech dla danego użytkownika. |
| AAM-softmax | Additive Angular Margin | Zmodyfikowana funkcja straty wprowadzająca margines kary kątowej, wymuszająca większą separację cech różnych mówców w przestrzeni ukrytej. |
| PLDA | Probabilistic LDA | Model statystyczny nakładany na wektory osadzeń, szacujący prawdopodobieństwo przynależności próbek do tej samej osoby. |
| DER | Diarization Error Rate | Podstawowa metryka jakości diaryzacji, sumująca czas pominiętej mowy (miss), fałszywych alarmów (false alarm) oraz błędnego przypisania mówcy (speaker confusion). |

## Dalsze czytanie

- [Snyder et al. (2018). X-Vectors: Robust DNN Embeddings for Speaker Recognition](https://www.danielpovey.com/files/2018_icassp_xvectors.pdf) — kamień milowy we wdrożeniu głębokich sieci neuronowych w SV.
- [Desplanques et al. (2020). ECAPA-TDNN](https://arxiv.org/abs/2005.07143) — publikacja wprowadzająca wiodącą architekturę ECAPA-TDNN.
- [Chen et al. (2022). WavLM: Large-Scale Self-Supervised Pre-Training for Full Stack Speech Processing](https://arxiv.org/abs/2110.13900) — model WavLM jako potężny backend dla zadań przetwarzania mowy.
- [Bredin et al. (2023). pyannote.audio 3.1](https://github.com/pyannote/pyannote-audio) — otwarta biblioteka do diaryzacji i segmentacji mówców.
- [VoxCeleb Speaker Recognition Challenge](https://www.robots.ox.ac.uk/~vgg/data/voxceleb/) — oficjalna strona konkursowa z aktualną tabelą wyników i najnowszymi modelami SOTA.
