# Klasyfikacja audio — od k-NN na MFCC do AST i BEATs

> Wszystko – od rozróżniania szczekania psa od syreny alarmowej, aż po rozpoznawanie języka – jest zadaniem klasyfikacji audio. Najpopularniejszymi cechami wejściowymi są spektrogramy melowe (mels). Architektury modeli zmieniają się co dekadę, natomiast standardem ewaluacji pozostają wskaźniki AUC, F1-score oraz czułość (recall) dla poszczególnych klas.

**Typ:** Kompendium
**Języki:** Python
**Wymagania wstępne:** Faza 6 · 02 (spektrogramy i filtry melowe), Faza 3 · 06 (CNN), Faza 5 · 08 (CNN i RNN dla tekstu)
**Czas:** ~75 minut

## Problem

Otrzymujesz 10-sekundowy klip audio i chcesz odpowiedzieć na pytanie: „Co słychać na nagraniu?”. Może to być dźwięk otoczenia miejskiego (syrena, wiertarka, pies), komenda głosowa (tak/nie/stop), identyfikator języka (en/es/ar), emocje mówcy (złość/neutralny) czy też akustyka otoczenia (wewnątrz/na zewnątrz, gwar rozmów). Wszystkie te zagadnienia wchodzą w zakres *klasyfikacji audio*. W 2026 roku podstawowy schemat architektury jest w pełni dojrzały: log-mel → CNN lub Transformer → softmax.

Głównym wyzwaniem nie jest sama sieć neuronowa, lecz dane. W zbiorach danych audio powszechnie występuje ogromna nierównowaga klas, silne przesunięcie domenowe (nagrania czyste vs. zaszumione) oraz nieprecyzyjne etykietowanie (kto i na jakiej podstawie zdecydował, gdzie kończy się „gwar w tle”, a zaczyna „hałas restauracyjny”?). Około 80% pracy nad problemem polega na selekcji, oczyszczaniu, augmentacji danych i rzetelnej ewaluacji, a nie na samej zamianie klasycznego CNN na Transformera.

## Koncepcja

![Ewolucja klasyfikacji dźwięku: od k-NN na MFCC, przez AST, po BEATs](../assets/audio-classification.svg)

**k-NN na MFCC (poziom bazowy z lat 90. XX w.).** Spłaszczenie reprezentacji MFCC dla danego klipu, obliczenie podobieństwa cosinusowego do bazy oznaczonych próbek referencyjnych i przypisanie klasy na podstawie większości głosów spośród K najbliższych sąsiadów. Metoda ta jest zaskakująco skuteczna na czystych, małych zbiorach danych (np. komendy głosowe, ESC-50) i działa bez użycia GPU.

**2D CNN na spektrogramach log-mel (2015–2019).** Spektrogram log-mel o wymiarach `(T, n_mels)` jest traktowany jak obraz. Stosuje się klasyczne architektury typu ResNet-18 lub VGG z warstwą globalnego uśredniania (Global Average Pooling) wzdłuż osi czasu i warstwą Softmax na wyjściu. Do dziś (w 2026 roku) stanowi to solidną podstawę w wielu konkursach na Kaggle.

**Audio Spectrogram Transformer, AST (2021–2024).** Dzieli spektrogram log-mel na mniejsze wycinki (patches, np. 16×16), dodaje kodowanie pozycyjne (position embeddings) i przekazuje je do enkodera ViT (Vision Transformer). Rozwiązanie to stanowiło przez pewien czas standard SOTA na zbiorze AudioSet (mAP 0.485) w uczeniu nadzorowanym.

**BEATs i WavLM (2024–2026).** Modele wstępnie wytrenowane w sposób samonadzorowany (self-supervised pre-training) na milionach godzin nagrań. Pozwalają na dostrojenie (finetuning) do konkretnego zadania przy użyciu zaledwie 1–10% nadzorowanych danych. W 2026 roku stanowią one domyślny punkt startowy dla dźwięków innych niż mowa. Model BEATs-iter3 osiąga wyniki o 1-2 mAP lepsze niż AST na zbiorze AudioSet, zużywając przy tym 1/4 mocy obliczeniowej.

**Koder Whisper jako zamrożony model bazowy (2024).** Wykorzystanie samego kodera (encoder) z modelu Whisper bez dekodera i podłączenie do niego prostego klasyfikatora liniowego. Daje to wyniki bliskie SOTA w zadaniach identyfikacji języka oraz prostej klasyfikacji zdarzeń dźwiękowych w trybie zero-shot. Klasyczny przykład skutecznego przenoszenia wiedzy (transfer learning).

### Nierównowaga klasowa to realne wyzwanie

- **ESC-50:** 50 klas, po 40 klipów każda – zbiór w pełni zrównoważony i łatwy.
- **UrbanSound8K:** 10 klas, współczynnik niezrównoważenia sięga 10:1.
- **AudioSet:** 632 klasy o rozkładzie długoogonowym (nawet do 100 000:1).

Skuteczne techniki radzenia sobie z tym problemem:
- **Zrównoważone próbkowanie (balanced sampling):** stosowane w trakcie trenowania (ale nie podczas ewaluacji).
- **Mixup:** interpolacja liniowa dwóch losowych klipów (oraz ich etykiet) w celu stworzenia nowej próbki treningowej.
- **SpecAugment:** maskowanie losowych pasm czasu i częstotliwości. Prosta, ale kluczowa metoda augmentacji spektrogramów.

### Ewaluacja

- **Klasyfikacja jednoetykietowa (np. komendy głosowe):** dokładność Top-1 (Accuracy), Top-5.
- **Klasyfikacja wieloetykietowa (np. AudioSet, UrbanSound):** średnia precyzja (mean Average Precision - mAP).
- **Zbiory silnie niezrównoważone:** czułość (recall) dla poszczególnych klas + Macro F1-score.

Wyniki referencyjne (stan na 2026 r.), które warto znać:

| Benchmark | Wynik bazowy | SOTA 2026 | Źródło |
|----------|----------|----------|--------|
| ESC-50 | 82% (AST) | 97,0% (BEATs-iter3) | Artykuł BEATs (2024) |
| AudioSet mAP | 0,485 (AST) | 0,548 (BEATs-iter3) | HEAR Leaderboard 2026 |
| Speech Commands v2 | 98% (CNN) | 99,0% (Audio-MAE) | Wyniki HEAR v2 |

## Implementacja krok po kroku

### Krok 1: Ekstrakcja cech

```python
def featurize_mfcc(signal, sr, n_mfcc=13, n_mels=40, frame_len=400, hop=160):
    mag = stft_magnitude(signal, frame_len, hop)
    fb = mel_filterbank(n_mels, frame_len, sr)
    mels = apply_filterbank(mag, fb)
    log = log_transform(mels)
    return [dct_ii(frame, n_mfcc) for frame in log]
```

### Krok 2: Agregacja do stałej długości

```python
def summarize(mfcc_frames):
    n = len(mfcc_frames[0])
    mean = [sum(f[i] for f in mfcc_frames) / len(mfcc_frames) for i in range(n)]
    var = [
        sum((f[i] - mean[i]) ** 2 for f in mfcc_frames) / len(mfcc_frames) for i in range(n)
    ]
    return mean + var
```

Proste, lecz skuteczne: średnia i wariancja obliczone w czasie dają 26-wymiarowy wektor cech o stałej długości dla 13 współczynników MFCC. Działa natychmiastowo i pozwalało pobić proste sieci neuronowe na zbiorze ESC-50 już w 2017 roku.

### Krok 3: k-NN

```python
def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1e-12
    nb = math.sqrt(sum(x * x for x in b)) or 1e-12
    return dot / (na * nb)

def knn_classify(q, bank, labels, k=5):
    sims = sorted(range(len(bank)), key=lambda i: -cosine(q, bank[i]))[:k]
    votes = Counter(labels[i] for i in sims)
    return votes.most_common(1)[0][0]
```

### Krok 4: Klasyfikator CNN na spektrogramach log-mel

Implementacja w PyTorch:

```python
import torch.nn as nn

class AudioCNN(nn.Module):
    def __init__(self, n_mels=80, n_classes=50):
        super().__init__()
        self.body = nn.Sequential(
            nn.Conv2d(1, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(64, 128, 3, padding=1), nn.ReLU(),
            nn.AdaptiveAvgPool2d(1),
        )
        self.head = nn.Linear(128, n_classes)

    def forward(self, x):  # x: (B, 1, T, n_mels)
        return self.head(self.body(x).flatten(1))
```

Model posiada około 3M parametrów. Czas trenowania na zbiorze ESC-50 przy użyciu jednej karty RTX 4090 wynosi około 10 minut, pozwalając na osiągnięcie ponad 80% dokładności.

### Krok 5: Domyślne podejście w 2026 r. — dostrojenie modelu AST

```python
from transformers import ASTFeatureExtractor, ASTForAudioClassification

ext = ASTFeatureExtractor.from_pretrained("MIT/ast-finetuned-audioset-10-10-0.4593")
model = ASTForAudioClassification.from_pretrained(
    "MIT/ast-finetuned-audioset-10-10-0.4593",
    num_labels=50,
    ignore_mismatched_sizes=True,
)

inputs = ext(audio, sampling_rate=16000, return_tensors="pt")
logits = model(**inputs).logits
```

*Uwaga:* W przypadku modelu BEATs można użyć repozytorium `microsoft/BEATs-base` za pośrednictwem biblioteki `beats`. Interfejs API w bibliotece transformers zachowuje ten sam format danych.

## Sugerowane podejście w zależności od scenariusza

| Scenariusz | Punkt wyjścia |
|----------|-----------|
| Mały zbiór danych (<1000 klipów) | k-NN na średnich/wariancjach MFCC (jako linia bazowa) + augmentacja audio |
| Średni zbiór danych (1k–100k klipów) | Dostrojenie (finetuning) modeli BEATs lub AST |
| Duży zbiór danych (>100k klipów) | Trenowanie od zera lub dostrojenie kodera Whisper |
| Przetwarzanie w czasie rzeczywistym (Edge/Embedded) | Lekka sieć CNN na 40 filtrach MFCC, skwantowana do int8 (np. w stylu KWS) |
| Wiele etykiet (np. AudioSet) | BEATs-iter3 z funkcją straty BCE + Mixup + SpecAugment |
| Identyfikacja języka | MMS-LID lub model bazowy SpeechBrain wytrenowany na VoxLingua107 |

Złota zasada brzmi: **zawsze zaczynaj od zamrożonego modelu bazowego (backbone)** zamiast uczyć model od zera. Dostrojenie samej główki klasyfikatora dla modelu BEATs pozwala osiągnąć 95% docelowego wyniku SOTA w kilka godzin, oszczędzając całe tygodnie pracy.

## Zadanie do wykonania

Zapisz jako `outputs/skill-classifier-designer.md`. Dobierz odpowiednią architekturę, metody augmentacji, strategię radzenia sobie z nierównowagą klas oraz metryki ewaluacji dla zadanego problemu klasyfikacji audio.

## Ćwiczenia

1. **Łatwe.** Uruchom skrypt `code/main.py`. Trenuje on bazowy klasyfikator k-NN na MFCC na syntetycznym zbiorze 4 klas (czyste tony o różnych częstotliwościach). Przedstaw wynikową macierz pomyłek.
2. **Średnie.** Zastąp funkcję `summarize` wersją zwracającą `[mean, var, skew, kurtosis]`. Sprawdź, czy dodanie skośności i kurtozy poprawia wynik klasyfikacji k-NN na tym samym syntetycznym zbiorze danych.
3. **Trudne.** Wykorzystując bibliotekę `torchaudio`, wytrenuj model 2D CNN na pierwszym podziale (fold 1) zbioru ESC-50. Przedstaw wynik 5-krotnej walidacji krzyżowej. Następnie dodaj augmentację SpecAugment (maska czasu = 20, maska częstotliwości = 10) i porównaj uzyskane wyniki.

## Kluczowe terminy

| Termin | Potoczne określenie | Co to naprawdę oznacza |
|------|-----------------|----------------------|
| AudioSet | ImageNet dla dźwięku | Stworzony przez Google zbiór 2 milionów 10-sekundowych klipów z YouTube z przypisanymi słabymi etykietami (weak labels) należącymi do 632 klas. |
| ESC-50 | Lekki benchmark klasyfikacyjny | Zbiór 50 klas x 40 klipów zawierających różnorodne dźwięki otoczenia. |
| AST | Audio Spectrogram Transformer | Architektura ViT (Vision Transformer) stosowana bezpośrednio do wycinków (patches) spektrogramu log-mel. SOTA w 2021 r. |
| BEATs | Self-supervised audio model | Model firmy Microsoft. Wersja iter3 dominuje w benchmarku AudioSet od 2026 roku. |
| Mixup | Augmentacja par danych | Metoda augmentacji polegająca na interpolacji liniowej: `x = λ·x1 + (1-λ)·x2; y = λ·y1 + (1-λ)·y2`. |
| SpecAugment | Maskowanie spektrogramu | Wyzerowanie losowych pasm czasu i częstotliwości bezpośrednio na spektrogramie w celu poprawy generalizacji modelu. |
| mAP | Średnia precyzja (mean Average Precision) | Główna metryka dla problemów wieloetykietowych, obliczana jako średnia z pól pod krzywą precyzji/czułości (PR) dla wszystkich klas. |

## Dalsze czytanie

- [Gong, Chung, Glass (2021). AST: Audio Spectrogram Transformer](https://arxiv.org/abs/2104.01778) — kluczowa architektura w latach 2021–2024.
- [Chen et al. (2022, rev 2024). BEATs: Audio Pre-Training with Acoustic Tokenizers](https://arxiv.org/abs/2212.09058) — domyślny wybór od roku 2024+.
- [Park et al. (2019). SpecAugment](https://arxiv.org/abs/1904.08779) — standard w augmentacji danych audio.
- [Piczak (2015). ESC-50 Dataset](https://github.com/karolpiczak/ESC-50) — wciąż popularny i lekki benchmark zawierający 50 klas dźwięków.
- [Gemmeke et al. (2017). AudioSet](https://research.google.com/audioset/) — taksonomia 632 klas dźwięków z serwisu YouTube; wciąż złoty standard w dziedzinie ogólnej klasyfikacji audio.
