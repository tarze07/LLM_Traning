# Ochrona przed fałszowaniem głosu i znak wodny audio — ASVspoof 5, AudioSeal, WaveVerify

> Klonowanie głosu dostarczane szybciej niż obrona. Systemy głosowe do produkcji na rok 2026 będą potrzebowały dwóch rzeczy: detektora (AASIST, RawNet2), który klasyfikuje mowę prawdziwą i fałszywą, oraz znaku wodnego (AudioSeal), który przetrwa kompresję i edycję. Wyślij oba lub nie wysyłaj klonowania głosu.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 6 · 06 (rozpoznawanie osoby mówiącej), faza 6 · 08 (klonowanie głosu)
**Czas:** ~75 minut

## Problem

Trzy powiązane mechanizmy obronne:

1. **Zapobieganie fałszowaniu i wykrywanie deepfake’ów.** Biorąc pod uwagę klip audio, czy jest on syntetyczny czy prawdziwy? Testy porównawcze ASVspoof (ASVspoof 2019 → 2021 → 5) to złoty standard.
2. **Znak wodny dźwięku.** Umieść niezauważalny sygnał w generowanym dźwięku, który detektor może później wyodrębnić. Otwartymi opcjami są AudioSeal (Meta) i WavMark.
3. **Uwierzytelnione pochodzenie.** Kryptograficzne podpisywanie plików audio + metadane. C2PA / Inicjatywa na rzecz autentyczności treści.

Wykrywanie radzi sobie z przeciwnikami, którzy nie współpracują. Znak wodny zapewnia zgodność — dźwięk wygenerowany przez sztuczną inteligencję powinien być rozpoznawalny jako taki. Obydwa są wymagane w 2026 r.

## Koncepcja

![Anti-spoofing vs znak wodny vs pochodzenie — trzy warstwy ochrony](../assets/spoofing-watermark.svg)

### ASVspoof 5 — punkt odniesienia na lata 2024–2025

Największa zmiana w stosunku do poprzednich edycji:

- **Dane pochodzące z crowdsourcingu** (nie czyste studyjnie) — realistyczne warunki.
- **~2000 głośników** (w porównaniu z ~100 wcześniej).
- **32 algorytmy ataku.** TTS + konwersja głosu + zakłócenia kontradyktoryjne.
- **Dwie ścieżki.** Samodzielne wykrywanie środków zaradczych (CM); Odporny na fałszowanie ASV (SASV) dla systemów biometrycznych.

Najnowocześniejszy model ASVspoof 5: ~7,23% EER. Na starszym ASVspoof 2019 LA: 0,42% EER. Wdrożenie w świecie rzeczywistym: spodziewaj się 5-10% EER w przypadku klipów w dziczy.

### AASIST i RawNet2 — rodziny modeli detekcji

**AASIST** (2021, aktualizacja do 2026). Wykres - uwaga na cechy widmowe. Bieżące zadanie SOTA dotyczące zadania przeciwdziałania ASVspoof 5.

**RawNet2.** Interfejs splotowy na surowym przebiegu + szkielet TDNN. Prostsza linia bazowa; nadal konkurencyjny dzięki dostrajaniu.

**NeXt-TDNN + funkcje SSL.** Wariant 2025: styl ECAPA + funkcje WavLM + utrata ogniskowej. Osiąga 0,42% EER na ASVspoof 2019 LA.

### AudioSeal — domyślny znak wodny na rok 2024

Meta's **AudioSeal** (styczeń 2024 r., wersja 0.2.12.2024 r.). Kluczowy projekt:

- **Zlokalizowane.** Wykrywa znak wodny na klatkę przy rozdzielczości próbki 16 kHz (1/16000 s).
- **Generator + detektor wspólnie przeszkoleni.** Generator uczy się osadzać niesłyszalny sygnał; Detektor uczy się go znajdować poprzez ulepszenia.
- **Wytrzymały.** Wytrzymuje kompresję MP3 / AAC, EQ, zmianę prędkości ±10%, miks szumów +10 dB SNR.
- **Szybki.** Detektor działa z częstotliwością 485× w czasie rzeczywistym; 1000 razy szybszy niż WavMark.
- **Pojemność.** 16-bitowy ładunek (może kodować identyfikator modelu, znacznik czasu generacji, identyfikator użytkownika) osadzany w każdej wypowiedzi.

### WavMark

Otwarta linia bazowa sprzed wersji AudioSeal. Odwracalna sieć neuronowa, 32 bity/sek. Problemy:

- Synchronizacja brute-force jest powolna.
- Można usunąć za pomocą szumu Gaussa lub kompresji MP3.
- Nie jest przyjazny w czasie rzeczywistym.

### WaveVerify (lipiec 2025 r.)

Eliminuje słabości AudioSeal — w szczególności manipulacje czasowe (odwrócenie, prędkość). Wykorzystuje generator oparty na FiLM + detektor Mixture-of-Experts. Konkurencyjny z AudioSeal w standardowych atakach; obsługuje edycje tymczasowe.

### Luka, którą wykorzystują przeciwnicy

Z AudioMarkBench: „przy zmianie wysokości tonu wszystkie znaki wodne wykazują dokładność odzyskiwania bitów poniżej 0,6, co wskazuje na prawie całkowite usunięcie”. **Przesunięcie wysokości to atak uniwersalny.** Znak wodny nr 2026 jest w pełni odporny na agresywną modyfikację wysokości. Dlatego obok znaku wodnego potrzebujesz wykrywania (AASIST).

### C2PA / Inicjatywa na rzecz autentyczności treści

Nie jest to technika ML — format manifestu. Pliki audio zawierają podpisane kryptograficznie metadane dotyczące narzędzia tworzenia, autora i daty. Audiobox / Bezproblemowe korzystanie z niego. Dobre pochodzenie; nic nie robi, jeśli zły aktor ponownie koduje i usuwa metadane.

## Zbuduj to

### Krok 1: prosty detektor cech widmowych (zabawka)

```python
def spectral_rolloff(spec, percentile=0.85):
    cum = 0
    total = sum(spec)
    if total == 0:
        return 0
    threshold = total * percentile
    for k, v in enumerate(spec):
        cum += v
        if cum >= threshold:
            return k
    return len(spec) - 1

def is_suspicious(audio):
    spec = magnitude_spectrum(audio)
    rolloff = spectral_rolloff(spec)
    return rolloff / len(spec) > 0.92
```

Mowa syntetyczna często charakteryzuje się niezwykle płaską energią w zakresie wysokich częstotliwości. Detektory produkcyjne korzystają z AASIST, a nie z tego. Ale intuicja działa.

### Krok 2: Osadź i wykryj AudioSeal

```python
from audioseal import AudioSeal
import torch

generator = AudioSeal.load_generator("audioseal_wm_16bits")
detector = AudioSeal.load_detector("audioseal_detector_16bits")

audio = load_wav("generated.wav", sr=16000)[None, None, :]
payload = torch.tensor([[1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0]])
watermark = generator.get_watermark(audio, sample_rate=16000, message=payload)
watermarked = audio + watermark

result, decoded_payload = detector.detect_watermark(watermarked, sample_rate=16000)
# result: float in [0, 1] — probability of watermark presence
# decoded_payload: 16 bits; match against embedded payload
```

### Krok 3: ewaluacja – EER

```python
def eer(real_scores, fake_scores):
    thresholds = sorted(set(real_scores + fake_scores))
    best = (1.0, 0.0)
    for t in thresholds:
        far = sum(1 for s in fake_scores if s >= t) / len(fake_scores)
        frr = sum(1 for s in real_scores if s < t) / len(real_scores)
        if abs(far - frr) < best[0]:
            best = (abs(far - frr), (far + frr) / 2)
    return best[1]
```

### Krok 4: integracja produkcji

```python
def safe_tts(text, voice, clone_reference=None):
    if clone_reference is not None:
        verify_consent(user_id, clone_reference)
    audio = tts_model.synthesize(text, voice)
    audio_with_wm = audioseal_embed(audio, payload=build_payload(user_id, model_id))
    manifest = c2pa_sign(audio_with_wm, user_id, timestamp=now())
    return audio_with_wm, manifest
```

Każda generacja dostarcza: (1) znak wodny, (2) podpisany manifest, (3) dziennik audytu zgodny z zasadami przechowywania.

## Użyj tego

| Przypadek użycia | Obrona |
|---------|---------|
| Wysyłka TTS / klonowanie głosu | AudioSeal osadzony na każdym wyjściu (nie podlega negocjacji) |
| Biometryczne odblokowanie głosowe | zespół AASIST + ECAPA; wyzwanie życia |
| Wykrywanie oszustw w call center | AASIST na 20% próbie połączeń przychodzących |
| Autentyczność podcastu | Podpisywanie C2PA przy przesyłaniu, AudioSeal w przypadku wygenerowania przez sztuczną inteligencję |
| Detektory badawcze/szkoleniowe | ASVspoof 5 zestawów pociągowych/programistycznych/ewaluacyjnych |

## Pułapki

- **Znak wodny bez działającego kiedykolwiek detektora.** Bez sensu. Wyślij detektor do swojego CI.
- **Wykrywanie bez kalibracji.** Zespół AASIST przeszkolony w zakresie overfitingu ASVspoof LA; spada dokładność w świecie rzeczywistym. Kalibruj w swojej domenie.
- **Odstęp zmiany wysokości tonu.** Agresywna zmiana wysokości tonu usuwa większość znaków wodnych. Mają rezerwę wykrywania.
- **Usuwanie i ponowne hostowanie metadanych.** C2PA można w prosty sposób ominąć poprzez ponowne kodowanie. Zawsze łącz ochronę kryptograficzną i percepcyjną (znak wodny).
- **Żywotność jako wykrywanie.** Poproś użytkownika o wypowiedzenie losowej frazy. Zapobiega atakom polegającym na powtarzaniu, ale nie klonowaniu w czasie rzeczywistym.

## Wyślij to

Zapisz jako `outputs/skill-spoof-defender.md`. Wybierz model wykrywania, znak wodny, manifest pochodzenia i podręcznik operacyjny na potrzeby wdrożenia generatora głosu.

## Ćwiczenia

1. **Łatwe.** Uruchom `code/main.py`. Detektor zabawek + osadzanie/wykrywanie znaku wodnego zabawek w syntetycznym dźwięku.
2. **Średni.** Zainstaluj `audioseal`, osadź 16-bitowy ładunek w wyjściu TTS, ponownie zdekoduj. Zniszcz dźwięk za pomocą szumów i zmierz dokładność odzyskiwania bitów.
3. **Trudne.** Dostosuj RawNet2 lub AASIST na ASVspoof 2019 LA. Zmierz EER. Przetestuj na wyciągniętym zestawie klipów generowanych przez F5-TTS — zobacz, jak pogarsza się wykrywanie OOD.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| ASVspoof | Punkt odniesienia | Wyzwanie dwuletnie; 2024 = ASVspoof 5. |
| CM (środek zaradczy) | Detektor | Klasyfikator: mowa prawdziwa vs syntetyczna / przekonwertowana. |
| SASV | Weryfikacja mówcy + CM | Zintegrowane wykrywanie biometryczne + parodia. |
| Uszczelka Audio | Metaznak wodny | Zlokalizowany, 16-bitowy ładunek, 485 razy szybszy niż WavMark. |
| Dokładność odzyskiwania bitów | Przetrwanie znaku wodnego | Część fragmentów ładunku odzyskana po ataku. |
| C2PA | Manifest pochodzenia | Metadane kryptograficzne o stworzeniu/autorstwie. |
| POMOC | Rodzina detektorów | SOTA oparta na grafach i przeciwdziałająca fałszowaniu. |

## Dalsze czytanie

- [Todisco i in. (2024). ASVspoof 5](https://dl.acm.org/doi/10.1016/j.csl.2025.101825) — aktualny benchmark.
- [Defossez i in. (2024). AudioSeal](https://arxiv.org/abs/2401.17264) — domyślny znak wodny.
- [Chen i in. (2025). WaveVerify](https://arxiv.org/abs/2507.21150) — detektor MoE do wykrywania ataków czasowych.
- [Jung i in. (2022). AASIST](https://arxiv.org/abs/2110.01200) — szkielet wykrywania SOTA.
- [AudioMarkBench (2024)](https://proceedings.neurips.cc/paper_files/paper/2024/file/5d9b7775296a641a1913ab6b4425d5e8-Paper-Datasets_and_Benchmarks_Track.pdf) – ocena solidności.
- [Specyfikacja C2PA](https://c2pa.org/specifications/specifications/) — format manifestu pochodzenia.