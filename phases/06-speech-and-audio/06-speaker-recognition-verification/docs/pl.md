# Rozpoznawanie i weryfikacja mówcy

> ASR pyta „co powiedzieli?” Funkcja rozpoznawania mówcy pyta „kto to powiedział?” Matematyka wygląda tak samo – osadzania plus cosinus – ale każda decyzja dotycząca produkcji opiera się na jednej liczbie EER.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 6 · 02 (spektrogramy i Mel), Faza 5 · 22 (modele osadzania)
**Czas:** ~45 minut

## Problem

Użytkownik podaje hasło. Chcesz wiedzieć: czy jest to osoba, za którą się podaje (*weryfikacja*, 1:1), czy też jest to pierwsza osoba w Twoim banku rejestracyjnym (*identyfikacja*, 1:N)? Albo żadne — czy to nieznany głośnik (*zestaw otwarty*)?

Przed 2018 r.: GMM-UBM + i-wektory. Rozsądny EER, ale wrażliwy na zmianę kanału (telefon kontra laptop) i emocje. 2018–2022: wektory x (szkielet TDNN przeszkolony z marginesem kątowym). 2022+: duże osadzania ECAPA-TDNN i WavLM. Do 2026 r. w tej dziedzinie będą dominować trzy modele i jeden wskaźnik.

Metryką jest **EER** — równy współczynnik błędów. Ustaw próg decyzyjny tak, aby odsetek fałszywych akceptacji = odsetek fałszywych odrzuceń. Zwrotnica to EER. Używane w każdej gazecie, każdej tabeli liderów, każdym zaproszeniu do zakupów.

## Koncepcja

![Rejestracja + potok weryfikacji z osadzeniem + cosinus + EER](../assets/speaker-verification.svg)

**Potok.** Rejestracja: nagraj 5–30 sekund docelowego mówcy; obliczyć osadzenie o stałym wymiarze (192-d dla ECAPA-TDNN, 256-d dla WavLM-large). Weryfikacja: pobierz osadzoną wypowiedź testową; obliczyć podobieństwo cosinus; porównać z progiem.

**ECAPA-TDNN (2020, nadal dominujący 2026).** Szczególna uwaga, propagacja i agregacja kanałów – sieć neuronowa z opóźnieniem czasowym. Bloki konw. 1D z pobudzeniem ściśnięcia, łączenie uwagi wielu głowic, po których następuje warstwa liniowa do 192-d. Przeszkolony na VoxCeleb 1+2 (2700 mówców, 1,1 mln wypowiedzi) z addytywną utratą marginesu kątowego (AAM-softmax).

**WavLM-SV (2022+).** Dostosuj wstępnie wytrenowany szkielet SSL o dużej wielkości WavLM z utratą AAM. Wyższa jakość, ale wolniejsza — 300+ MB w porównaniu z 15 MB.

**wektor x (wartość bazowa).** TDNN + łączenie statystyk. Klasyczny; nadal przydatny na procesorze/krawędzi.

**AAM-softmax.** Standardowy softmax z dodanym marginesem `m` w przestrzeni kątowej: `cos(θ + m)` dla właściwej klasy. Wymusza międzyklasową separację kątową. Typowy `m=0.2`, skala `s=30`.

### Punktacja

- **Cosinus** pomiędzy osadzeniem rejestracyjnym i testowym. Decyzja oparta na progach.
- **PLDA (Probabilistyczny LDA).** Projekt osadza się w ukrytej przestrzeni, gdzie ten sam mówca w porównaniu z innym mówcą ma zamknięty współczynnik wiarygodności. Dodany do cosinusa w celu zmniejszenia EER o +10–20%. Standard sprzed 2020 r.; obecnie używany tylko w konfiguracjach z zestawem zamkniętym.
- **Normalizacja wyniku.** `S-norm` lub `AS-norm`: normalizuj każdy wynik względem kohorty fałszywych średnich i standardów. Niezbędne do oceny międzydomenowej.

### Liczby, które powinieneś znać (2026)

| Modelka | VoxCeleb1-O EER | Parametry | Przepustowość (A100) |
|-------|-----------------|--------|--------------------------------|
| wektor x (klasyczny) | 3,10% | 5 M | 400×RT |
| ECAPA-TDNN | 0,87% | 15 mln | 200×RT |
| WavLM-SV duży | 0,42% | 316 mln | 20×RT |
| Segmentacja + osadzanie w Pyannote 3.1 | 0,65% | 6 M | 100×RT |
| ReDimNet (2024) | 0,39% | 24 mln | 100×RT |

### Diaryzacja

„Kto mówił, kiedy” w klipie z wieloma głośnikami. Potok: VAD → segment → osadź każdy segment → klaster (aglomeracyjny lub widmowy) → gładkie granice. Nowoczesny stos: `pyannote.audio` 3.1, który obejmuje segmentację głośników + osadzanie + grupowanie w jednym wywołaniu. SOTA DER 2026 na AMI wynosi ~15% (spadek z 23% w 2022 r.).

## Zbuduj to

### Krok 1: osadzanie zabawek ze statystyk MFCC

```python
def embed_mfcc_stats(signal, sr):
    frames = featurize_mfcc(signal, sr, n_mfcc=13)
    mean = [sum(f[i] for f in frames) / len(frames) for i in range(13)]
    std = [
        math.sqrt(sum((f[i] - mean[i]) ** 2 for f in frames) / len(frames))
        for i in range(13)
    ]
    return mean + std  # 26-d
```

Nie SOTA na milę - tylko do nauczania. `code/main.py` wykorzystuje to jako dowód słuszności koncepcji danych dotyczących głośników syntetycznych.

### Krok 2: cosinus podobieństwa + próg

```python
def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    return dot / (na * nb) if na and nb else 0.0

def verify(enroll, test, threshold=0.75):
    return cosine(enroll, test) >= threshold
```

### Krok 3: EER z par podobieństwa

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

Zwroty (eer, próg_at_eer). Zgłoś oba.

### Krok 4: produkcja za pomocą SpeechBrain

```python
from speechbrain.pretrained import EncoderClassifier

clf = EncoderClassifier.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb")

# enroll: average the embeddings of 3-5 clean samples
enroll = torch.stack([clf.encode_batch(load(x)) for x in enrollment_clips]).mean(0)
# verify
score = clf.similarity(enroll, clf.encode_batch(load("test.wav"))).item()
verdict = score > 0.25   # ECAPA typical threshold; tune on your data
```

### Krok 5: diaryzacja za pomocą pyannote

```python
from pyannote.audio import Pipeline

pipe = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1")
diarization = pipe("meeting.wav", num_speakers=None)
for turn, _, speaker in diarization.itertracks(yield_label=True):
    print(f"{turn.start:.1f}–{turn.end:.1f}  {speaker}")
```

## Użyj tego

Stos na rok 2026:

| Sytuacja | Wybierz |
|----------|------|
| Weryfikacja 1:1 w układzie zamkniętym, krawędź | ECAPA-TDNN + próg cosinusa |
| Weryfikacja otwartego zestawu, chmura | WavLM-SV + norma AS |
| Diaryzacja (spotkania, podcasty) | `pyannote/speaker-diarization-3.1` |
| Anti-spoofing (wykrywanie powtórek / deepfake) | AASIST lub RawNet2 |
| Mały osadzony (KWS + zapisy) | Titanet-mały (NeMo) |

## Pułapki

- **Niedopasowanie kanałów.** Modelka przeszkolona w VoxCeleb (wideo internetowe) ≠ Dźwięk rozmów telefonicznych. Zawsze oceniaj na kanale docelowym.
- **Krótkie wypowiedzi.** EER gwałtownie spada poniżej 3 sekund testowego dźwięku.
- **Rejestracja z hałasem.** Jedna hałaśliwa rejestracja zatruwa kotwicę. Użyj ≥3 czystych próbek i średniej.
- **Naprawiono próg dla różnych warunków.** Zawsze dostosowuj próg dla wstrzymanego zestawu deweloperskiego z domeny docelowej.
- **Cosinus na nieznormalizowanych osadzaniach.** L2 – najpierw normalizacja; w przeciwnym razie dominuje wielkość.

## Wyślij to

Zapisz jako `outputs/skill-speaker-verifier.md`. Wybierz model, protokół rejestracji, plan dostrajania progów i zabezpieczenia przed oszustwami.

## Ćwiczenia

1. **Łatwe.** Uruchom `code/main.py`. Buduje syntetyczne „głośniki” (różne profile tonów), rejestruje się, oblicza EER na liście próbnej zawierającej 100 par.
2. **Średni.** Użyj SpeechBrain ECAPA w 30 wypowiedziach VoxCeleb1 (5 mówców × 6 każdy). Oblicz EER za pomocą cosinusa vs PLDA.
3. **Trudne.** Zbuduj pełną rejestrację → diarizuj → zweryfikuj potok za pomocą `pyannote.audio`. Oceń DER na zestawie deweloperskim AMI.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| EER | Metryka nagłówka | Próg, przy którym fałszywa akceptacja = fałszywe odrzucenie. |
| Weryfikacja | 1:1 | „Czy to Alicja?” |
| Identyfikacja | 1:N | "Z kim mam przyjemność?" |
| Zestaw otwarty | Nieznane możliwe | Zestaw testowy może zawierać niezarejestrowane głośniki. |
| Zapisy | Rejestracja | Obliczanie osadzania odniesienia głośnika. |
| AAM-softmax | Strata | Softmax z dodatkowym marginesem kątowym; wymusza separację klastrów. |
| PLDA | Klasyczna punktacja | Probabilistyczny LDA; punktacja współczynnika wiarygodności na górze osadzania. |
| DER | Metryka diaryzacji | Współczynnik błędów diaryzacji — chybienie + fałszywy alarm + zamieszanie. |

## Dalsze czytanie

- [Snyder i in. (2018). X-Vectors: Solidne osadzanie DNN do rozpoznawania głośników](https://www.danielpovey.com/files/2018_icassp_xvectors.pdf) — klasyczny dokument do głębokiego osadzania.
- [Desplanques i in. (2020). ECAPA-TDNN](https://arxiv.org/abs/2005.07143) — architektura dominująca 2020–2026.
- [Chen i in. (2022). WavLM: Samonadzorowane szkolenie wstępne na dużą skalę w zakresie przetwarzania mowy w pełnym stosie](https://arxiv.org/abs/2110.13900) — szkielet SSL dla SV i diaryzacji.
- [Bredin i in. (2023). pyannote.audio 3.1](https://github.com/pyannote/pyannote-audio) — diaryzacja produkcji + osadzanie stosu.
– [Tabela liderów VoxCeleb (aktualizacja 2026 r.)](https://www.robots.ox.ac.uk/~vgg/data/voxceleb/) — aktualne rankingi EER dla poszczególnych modeli.