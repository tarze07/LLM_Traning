# Klasyfikacja audio — od k-NN na MFCC do AST i BEAT

> Wszystko, od „szczekanie psa czy syrena” po „jaki to język” jest klasyfikacją audio. Funkcje to Mels. Architektura zmienia się co dekadę. Ocena pozostaje AUC, F1 i przypomnienie dla poszczególnych klas.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 6 · 02 (spektrogramy i Mel), Faza 3 · 06 (CNN), Faza 5 · 08 (CNN i RNN dla tekstu)
**Czas:** ~75 minut

## Problem

Dostajesz 10-sekundowy klip. Chcesz wiedzieć: „co to jest?” Dźwięk miejski (syrena, musztra, pies), polecenie głosowe (tak/nie/stop), identyfikator języka (en/es/ar), emocje mówiącego (zły/neutralny) lub dźwięki otoczenia (w pomieszczeniu/na zewnątrz, bełkot). Wszystko to jest *klasyfikacja audio*, a w 2026 roku podstawowa architektura jest już dojrzała: log-mel → CNN lub Transformer → softmax.

Podstawową trudnością nie jest sieć. To są dane. W zbiorach danych audio występuje brutalna nierównowaga klas, silne przesunięcie domeny (czysty vs hałaśliwy) i szum etykiet (kto zdecydował, że „miejski bełkot” a „hałas z restauracji”?). 80% problemu polega na selekcji, ulepszaniu i ocenie, a nie na zamianie CNN na Transformera.

## Koncepcja

![Drabina klasyfikacji dźwięku: k-NN na MFCC do AST do BEAT](../assets/audio-classification.svg)

**k-NN na MFCC (poziom bazowy z lat 90. XX w.).** Spłaszcz MFCC na klip, oblicz podobieństwo cosinusa do oznaczonego banku, zwróć większość głosów górnego K. Zaskakująco silny na czystych, małych zestawach danych (polecenia mowy, ESC-50). Działa bez GPU.

**2D CNN na temat log-mels (2015–2019).** Traktuj `(T, n_mels)` log-mel jako obraz. Zastosuj styl ResNet-18 lub VGG. Globalna średnia pula osi czasu. Softmax na zajęciach. Nadal stanowi podstawę w większości zawodów kaggle w 2026 roku.

**Audio Spectrogram Transformer, AST (2021-2024).** Patchuj log-mel (np. patche 16×16), dodaj osadzanie pozycji, przesyłaj sygnał do ViT. Najnowocześniejszy zestaw AudioSet (mAP 0.485) do nauki pod nadzorem.

**BEATs i baza WavLM (2024–2026).** Samonadzorowane szkolenie wstępne trwające miliony godzin. Dopracuj swoje zadanie, korzystając z 1–10% nadzorowanych danych, których potrzebujesz. W roku 2026 będzie to domyślny punkt wyjścia dla dźwięku innego niż mowa. BEATs-iter3 pokonuje AST o 1-2 mAP na AudioSet, używając 1/4 mocy obliczeniowej.

**Koder szeptu jako zamrożony szkielet (2024).** Weź koder szeptu, odrzuć dekoder, podłącz klasyfikator liniowy. Prawie SOTA w zakresie identyfikatora języka i prostej klasyfikacji zdarzeń przy zerowym wzmocnieniu dźwięku. Podstawowa zasada „darmowego lunchu”.

### Brak równowagi klasowej jest prawdziwym wyzwaniem

ESC-50: 50 klas, po 40 klipów każda — zrównoważone, łatwe. UrbanSound8K: 10 klas, niezrównoważone 10:1. AudioSet: 632 klasy z długim ogonem 100 000:1. Techniki, które działają:

- Zrównoważone pobieranie próbek podczas szkolenia (nie podczas oceny).
- Mieszanie: interpolacja liniowa dwóch klipów (i ich etykiet) w ramach wzmocnienia.
- SpecAugment: maskuj losowe pasma czasu i częstotliwości. Prosty; krytyczny.

### Ocena

- Ekskluzywna wieloklasowość (polecenia mowy): dokładność na poziomie 1, dokładność na poziomie 5.
- Multiclass multi-label (AudioSet, styl UrbanSound): średnia średnia precyzja (mAP).
- Silnie niezrównoważony: przywołanie poszczególnych klas + makro F1.

Numery 2026, które powinieneś znać:

| punkt odniesienia | Linia bazowa | SOTA 2026 | Źródło |
|----------|----------|----------|--------|
| ESC-50 | 82% (AST) | 97,0% (BEATs-iter3) | Artykuł BEATs (2024) |
| AudioSet mAP | 0,485 (AST) | 0,548 (BEATs-iter3) | SŁUCHAJ tabelę wyników 2026 |
| Polecenia mowy v2 | 98% (CNN) | 99,0% (Audio-MAE) | SŁUCHAJ wyników v2 |

## Zbuduj to

### Krok 1: wyróżnij

```python
def featurize_mfcc(signal, sr, n_mfcc=13, n_mels=40, frame_len=400, hop=160):
    mag = stft_magnitude(signal, frame_len, hop)
    fb = mel_filterbank(n_mels, frame_len, sr)
    mels = apply_filterbank(mag, fb)
    log = log_transform(mels)
    return [dct_ii(frame, n_mfcc) for frame in log]
```

### Krok 2: podsumowanie o stałej długości

```python
def summarize(mfcc_frames):
    n = len(mfcc_frames[0])
    mean = [sum(f[i] for f in mfcc_frames) / len(mfcc_frames) for i in range(n)]
    var = [
        sum((f[i] - mean[i]) ** 2 for f in mfcc_frames) / len(mfcc_frames) for i in range(n)
    ]
    return mean + var
```

Proste, ale mocne: średnia + wariancja w czasie daje 26-przyciemnione stałe osadzenie dla 13-współczynnikowego MFCC. Działa natychmiast. Pokonaj najnowocześniejsze wartości bazowe NN na ESC-50 już w 2017 roku.

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

### Krok 4: uaktualnij do CNN na log-mels

W PyTorchu:

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

Parametry 3M. Trenuje w ~10 minut na ESC-50 z pojedynczym RTX 4090. Dokładność ponad 80%.

### Krok 5: wartość domyślna z 2026 r. — dostrojenie BEAT-ów

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

W przypadku BEAT-ów użyj `microsoft/BEATs-base` poprzez bibliotekę `beats`; API transformatorów ma ten sam kształt.

## Użyj tego

Stos na rok 2026:

| Sytuacja | Zacznij od |
|----------|-----------|
| Mały zbiór danych (<1000 klipów) | k-NN na MFCC oznacza (twoją linię bazową) + wzmocnienie dźwięku |
| Średni zbiór danych (1–100 tys.) | BEATs lub AST dostrojenie |
| Duży zbiór danych (>100 tys.) | Trenuj od zera lub dostosowuj koder Whisper |
| W czasie rzeczywistym, brzeg | 40-MFCC CNN, skwantowane do int8 (w stylu KWS) |
| Wiele etykiet (AudioSet) | BEATs-iter3 ze stratą BCE + miks + SpecAugment |
| Identyfikator języka | MMS-LID, wartość bazowa SpeechBrain VoxLingua107 |

Zasada decyzji: **zacznij od zamrożonego kręgosłupa, a nie świeżego modelu**. Dopracowanie głowicy BEATs pozwala uzyskać 95% SOTA w ciągu kilku godzin, a nie tygodni.

## Wyślij to

Zapisz jako `outputs/skill-classifier-designer.md`. Wybierz architekturę, ulepszenia, strategię równowagi klas i metrykę oceny dla danego zadania klasyfikacji audio.

## Ćwiczenia

1. **Łatwe.** Uruchom `code/main.py`. Uczy linię bazową k-NN MFCC na 4-klasowym syntetycznym zestawie danych (czyste tony o różnych wysokościach). Zgłoś matrycę zamieszania.
2. **Średni.** Zamień `summarize` na [średnia, var, skew, kurtosis]. Czy 4-momentowe dudnienie łączenia oznacza + var w tym samym syntetycznym zestawie danych?
3. **Trudne.** Używając `torchaudio`, wytrenuj CNN 2D na ESC-50 krotnie 1. Zgłoś 5-krotną dokładność weryfikacji krzyżowej. Dodaj SpecAugment (maska ​​czasu = 20, maska ​​częstotliwości = 10) i zgłoś różnicę.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Zestaw audio | ImageNet dźwięku | Klip Google o długości 2M, słabo oznaczony zbiór danych YouTube klasy 632. |
| ESC-50 | Mały punkt odniesienia w zakresie klasyfikacji | 50 zajęć × 40 klipów dźwięków otoczenia. |
| AST | Transformator spektrogramu audio | ViT na plastrach log-mel; SOTA 2021. |
| BITY | Samonadzorowany dźwięk | Model Microsoftu, iter3 prowadzi AudioSet od 2026 roku. |
| Mieszanka | Powiększenie pary | `x = λ·x1 + (1-λ)·x2; y = λ·y1 + (1-λ)·y2`. |
| Rozszerzenie specyfikacji | Augmentacja oparta na masce | Wyzeruj losowe pasma czasu i częstotliwości spektrogramu. |
| MAPA | Główny wskaźnik dotyczący wielu etykiet | Średnia średnia precyzja w klasach i progach. |

## Dalsze czytanie

- [Gong, Chung, Szkło (2021). AST: Audio Spectrogram Transformer](https://arxiv.org/abs/2104.01778) — architektura zapisu na lata 2021–2024.
- [Chen i in. (2022, wersja 2024). BEATs: wstępne szkolenie audio z tokenizatorami akustycznymi](https://arxiv.org/abs/2212.09058) — ustawienie domyślne na rok 2024+.
- [Park i in. (2019). SpecAugment](https://arxiv.org/abs/1904.08779) — dominujące wzmocnienie dźwięku.
- [Piczak (2015). Zbiór danych ESC-50](https://github.com/karolpiczak/ESC-50) — benchmark klasy 50, który wciąż żyje.
- [Gemmeke i in. (2017). AudioSet](https://research.google.com/audioset/) — taksonomia YouTube klasy 632; nadal złoty standard.