# Ocena dźwięku — WER, MOS, UTMOS, MMAU, FAD i otwarte rankingi

> Nie możesz wysłać czegoś, czego nie możesz zmierzyć. W tej lekcji wymieniono wskaźniki na rok 2026 dla każdego zadania audio: ASR (WER, CER, RTFx), TTS (MOS, UTMOS, SECS, WER-on-ASR-round-trip), język audio (MMAU, LongAudioBench), muzyka (FAD, CLAP) i głośnik (EER). Plus tabele wyników, w których porównujesz.

**Typ:** Ucz się
**Języki:** Python
**Wymagania:** Faza 6 · 04, 06, 07, 09, 10; Faza 2 · 09 (Ocena modelu)
**Czas:** ~60 minut

## Problem

Każde zadanie audio ma wiele wskaźników, z których każdy mierzy inną oś. Użycie niewłaściwej metryki prowadzi do dostarczenia modelu, który wygląda świetnie na desce rozdzielczej i fatalnie w produkcji. Lista kanoniczna na rok 2026:

| Zadanie | Podstawowy | Drugorzędne |
|------|---------|---------------|
| ASR | WER | CER · RTFx · opóźnienie pierwszego tokena |
| TTS | MOS / UTMOS | SECS · WER-on-ASR-podróż w obie strony · CER · TTFA |
| Klonowanie głosu | SECS (cosinus ECAPA) | MOS · CER |
| Weryfikacja mówcy | EER | minDCF · FAR / FRR w punkcie pracy |
| Diaryzacja | DER | JER · zamieszanie w głośnikach |
| Klasyfikacja dźwięku | top-1 · MAPA | makro F1 · Przywołanie poszczególnych klas |
| Pokolenie muzyki | MODA | CLAP · panel odsłuchowy MOS |
| Model języka audio | MMAU-Pro | LongAudioBench · AudioCaps FENSE |
| Przesyłanie strumieniowe S2S | opóźnienie P50/P95 | WER · MOS |

## Koncepcja

![Macierz oceny dźwięku — dane a zadania vs rankingi na rok 2026](../assets/eval-landscape.svg)

### Wskaźniki ASR

**WER (wskaźnik błędów słów).** `(S + D + I) / N`. Małe litery, usuń znaki interpunkcyjne, normalizuj liczby przed punktacją. Użyj `jiwer` lub `whisper_normalizer` OpenAI. < 5% = mowa czytana z parzystością ludzką.

**CER (wskaźnik błędów znaków).** Ta sama formuła, na poziomie znaku. Używany w językach tonowych (mandaryński, kantoński), w których segmentacja słów jest niejednoznaczna.

**RTFx (odwrotny współczynnik czasu rzeczywistego).** Sekundy dźwięku przetwarzane na sekundę zegara ściennego. Wyżej jest lepiej. Parakeet-TDT osiąga 3380×. Whisper-large-v3 wynosi ~ 30×.

**Opóźnienie pierwszego tokena.** Zegar ścienny od wejścia audio do pierwszego tokena transkrypcji. Krytyczne dla transmisji strumieniowej. Deepgram Nova-3: ~150 ms.

### Wskaźniki TTS

**MOS (średni wynik opinii).** Ocena 1-5 według ludzi. Złoty standard, ale powolny. Zbierz ponad 20 słuchaczy na próbkę, ponad 100 próbek na model.

**UTMOS (2022–2026).** Nauczony predyktor MOS. Koreluje ~ 0,9 z ludzkim MOS w standardowych testach porównawczych. F5-TTS: UTMOS 3,95; podstawowa prawda: 4.08.

**SECS (podobieństwo cosinusowe enkodera głośników).** Do klonowania głosu. ECAPA osadza cosinus między odniesieniem a sklonowanym wyjściem. > 0,75 = rozpoznawalny klon.

**WER-on-ASR-w obie strony.** Uruchom Whisper na wyjściu TTS, oblicz WER na podstawie tekstu wejściowego. Wychwytuje regresje zrozumiałości. SOTA 2026: < 2% CER.

**TTFA (czas do pierwszego dźwięku).** Opóźnienie zegara ściennego. Kokoro-82M: ~100 ms; F5-TTS: ~1 s.

### Specyficzne dla klonowania głosu

**SECS + MOS + CER** jako potrójne. Klonowanie, które uzyskuje wysoki wynik SECS, ale niski MOS, oznacza, że ​​barwa jest prawidłowa, ale nienaturalna; odwrotnie, oznacza to naturalny głos, ale niewłaściwego mówcę.

### Weryfikacja mówcy

**EER (równy współczynnik błędów).** Próg, przy którym współczynnik fałszywych akceptacji jest równy współczynnikowi fałszywych odrzuceń. ECAPA na VoxCeleb1-O: 0,87%.

**minDCF (min. koszt wykrycia).** Koszt ważony w wybranym punkcie operacyjnym (często FAR=0,01). Bardziej istotne dla produkcji niż EER.

### Diaryzacja

**DER (współczynnik błędów diaryzacji).** `(FA + Miss + Confusion) / total_speaker_time`. Nieodebrana mowa + mowa wywołana fałszywym alarmem + zamieszanie w głośniku, każde jako ułamek. Spotkania AMI: DER ~10-20% jest realistyczne. pyannote 3.1 + reklama Precision-2: <10% DER w przypadku dobrze nagranego dźwięku.

**JER (współczynnik błędów Jaccarda).** Alternatywa dla DER, odchylenie odporne na krótkie segmenty.

### Klasyfikacja dźwięku

Wiele etykiet: **mAP (średnia średnia precyzja)** we wszystkich klasach. Zestaw audio: 0,548 mAP dla BEATs-iter3.

Wyłącznie dla wielu klas: **dokładność top-1, top-5**. Polecenia głosowe wersja 2: 99,0% top-1 (Audio-MAE).

Niezrównoważone: **makro F1** + **przywołanie poszczególnych klas**. Raport według klas — zagregowana dokładność ukrywa, które klasy zawodzą.

### Generowanie muzyki

**FAD (Fréchet Audio Distance).** Odległość pomiędzy rozkładami dźwięku rzeczywistego i generowanego z osadzeniem VGG. MusicGen-small na MusicCaps: 4.5. MuzykaLM: 4.0. Niżej lepiej.

**Wynik CLAP.** Wynik wyrównania tekstu i dźwięku przy użyciu osadzania CLAP. > 0,3 = rozsądne wyrównanie.

**Panel odsłuchowy MOS.** Wciąż ostatnie słowo w sprawie muzyki klasy konsumenckiej. Suno v5 ELO 1293 na TTS Arena (na podstawie sparowanych preferencji ludzkich).

### Testy porównawcze języka audio

**MMAU (Massive Multi-Audio Understanding).** 10 tys. par audio-QA.

**MMAU-Pro.** 1800 twardych elementów, cztery kategorie: mowa / dźwięk / muzyka / multi-audio. Losowa szansa 25% w trybie 4-kierunkowym. Gemini 2.5 Pro ogółem ~60%; multi-audio ~22% we wszystkich modelach.

**LongAudioBench.** Wielominutowe klipy z zapytaniami semantycznymi. Audio Flamingo Next pokonuje Gemini 2.5 Pro.

**AudioCaps / Clotho.** Testy porównawcze napisów. Wskaźniki SPICE, CIDEr, FENSE.

### Przesyłanie strumieniowe mowy na mowę

**Opóźnienie P50 / P95 / P99.** Zegar ścienny od zakończenia mowy użytkownika do pierwszej dźwiękowej odpowiedzi. Moshi: 200 ms; GPT-4o Czas rzeczywisty: 300 ms.

**WER / MOS** na wyjściu.

**Czas reakcji na wtrącenie.** Czas od przerwania użytkownika do wyciszenia asystenta. Cel < 150 ms.

### Tabele liderów na rok 2026

| Tabela liderów | Utwory | Adres URL |
|------------|------------|---------|
| Otwarta tabela liderów ASR (HF) | Angielski + wielojęzyczny + długa forma | `huggingface.co/spaces/hf-audio/open_asr_leaderboard` |
| TTS Arena (HF) | Angielski TTS | `huggingface.co/spaces/TTS-AGI/TTS-Arena` |
| Sztuczna analiza mowy | TTS + STT, ELO z głosów par | `artificialanalysis.ai/speech` |
| MMAU-Pro | Rozumowanie LALM | `mmaubenchmark.github.io` |
| SpeakerBench / VoxSRC | Rozpoznawanie mówcy | `voxsrc.github.io` |
| Podzbiór muzyki MMAU | Muzyka LALM | (w obrębie MMAU) |
| Test porównawczy HEAR | Samonadzorowany dźwięk | `hearbenchmark.com` |

## Zbuduj to

### Krok 1: WER z normalizacją

```python
from jiwer import wer, Compose, ToLowerCase, RemovePunctuation, Strip

transform = Compose([ToLowerCase(), RemovePunctuation(), Strip()])
score = wer(
    truth="Please turn on the lights.",
    hypothesis="please turn on the light",
    truth_transform=transform,
    hypothesis_transform=transform,
)
# ~0.17
```

### Krok 2: podróż w obie strony TTS WER

```python
def ttr_wer(tts_model, asr_model, texts):
    errors = []
    for txt in texts:
        audio = tts_model.synthesize(txt)
        recog = asr_model.transcribe(audio)
        errors.append(wer(truth=txt, hypothesis=recog))
    return sum(errors) / len(errors)
```

### Krok 3: SECS do klonowania głosu

```python
from speechbrain.inference.speaker import EncoderClassifier
sv = EncoderClassifier.from_hparams("speechbrain/spkrec-ecapa-voxceleb")

emb_ref = sv.encode_batch(load_wav("reference.wav"))
emb_clone = sv.encode_batch(load_wav("cloned.wav"))
secs = torch.nn.functional.cosine_similarity(emb_ref, emb_clone, dim=-1).item()
```

### Krok 4: FAD do generowania muzyki

```python
from frechet_audio_distance import FrechetAudioDistance
fad = FrechetAudioDistance()
score = fad.get_fad_score("generated_folder/", "reference_folder/")
```

### Krok 5: EER w celu weryfikacji mówcy (ten sam kod, co w lekcji 6)

```python
def eer(same_scores, diff_scores):
    thresholds = sorted(set(same_scores + diff_scores))
    best = (1.0, 0.0)
    for t in thresholds:
        far = sum(1 for s in diff_scores if s >= t) / len(diff_scores)
        frr = sum(1 for s in same_scores if s < t) / len(same_scores)
        if abs(far - frr) < best[0]:
            best = (abs(far - frr), (far + frr) / 2)
    return best[1]
```

## Użyj tego

Połącz każde wdrożenie ze stałą wiązką eval, która działa przy każdej aktualizacji modelu. Trzy kardynalne zasady:

1. **Normalizuj przed punktacją.** Małe litery, pasek interpunkcyjny, rozwiń cyfrę. Zgłoś regułę normalizacji.
2. **Raportuj rozkłady, a nie średnie.** P50/P95/P99 dla opóźnienia. Przywołanie poszczególnych klas w celu klasyfikacji. Według kategorii dla MMAU.
3. **Przeprowadź jeden kanoniczny publiczny test porównawczy.** Nawet jeśli dane dotyczące Twojej produkcji się różnią, raportowanie w Open ASR / TTS Arena / MMAU umożliwia recenzentom porównywanie jabłek z jabłkami.

## Pułapki

- **Ekstrapolacja UTMOS.** Przeszkolony w zakresie czystej mowy w stylu VCTK; słabo ocenia dźwięk hałaśliwy/sklonowany/emocjonalny.
- **Błąd panelu MOS.** 20 pracowników Amazon Mechanical Turk ≠ 20 docelowych użytkowników. Zapłać za panel domeny, jeśli stawka jest wysoka.
- **FAD zależy od zestawu referencyjnego.** Porównanie z tym samym rozkładem referencyjnym w różnych modelach.
- **Zagregowany WER.** Ogółem 5% WER może ukryć 30% WER w przypadku mowy akcentowanej. Raport według wycinka demograficznego.
- **Nasycenie publicznych testów porównawczych.** Większość modeli pionierskich znajduje się blisko sufitu w standardowych testach. Zbuduj własny zestaw, który odzwierciedla Twój ruch.

## Wyślij to

Zapisz jako `outputs/skill-audio-evaluator.md`. Wybierz wskaźniki, testy porównawcze i format raportowania dla dowolnej wersji modelu audio.

## Ćwiczenia

1. **Łatwe.** Uruchom `code/main.py`. Oblicz WER/CER/EER/SECS/FAD-ish/MMAU-ish na wejściach zabawek.
2. **Średni.** Zbuduj uprząż WER TTS w obie strony. Uruchom wyjście Kokoro lub F5-TTS przez Whisper. Oblicz WER dla 50 podpowiedzi. Oznacz monity z WER > 10%.
3. **Trudny.** Oceń swój wybór LALM z lekcji 10 dotyczący mowy MMAU-Pro + podzbiory wielu dźwięków (po 50 elementów każdy). Zgłoś dokładność według kategorii i porównaj z opublikowaną liczbą.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| WER | Wynik ASR | `(S+D+I)/N` na poziomie słowa po normalizacji. |
| CER | Charakter WER | Dla języków tonowych lub systemów na poziomie znaków. |
| MOS | Opinia ludzka | ocena 1-5; Ponad 20 słuchaczy × 100 próbek. |
| UTMOS | Predyktor ML MOS | Wyuczony model; koreluje ~ 0,9 z ludzkim MOS. |
| SEK | Podobieństwo klonów głosu | Cosinus ECAPA między odniesieniem a klonem. |
| EER | Wynik weryfikacji mówcy | Próg, gdzie FAR = FRR. |
| DER | Wynik diaryzacji | (FA + Miss + Zamieszanie) / łącznie. |
| MODA | Jakość muzyki | Odległość Frécheta na osadzaniach VGGish. |
| RTFx | Przepustowość | Sekundy audio na sekundę zegara ściennego. |

## Dalsze czytanie

- [jiwer](https://github.com/jitsi/jiwer) — biblioteka WER/CER z narzędziami normalizacyjnymi.
- [UTMOS (Saeki et al. 2022)](https://arxiv.org/abs/2204.02152) — poznany predyktor MOS.
- [Fréchet Audio Distance (Kilgour et al. 2019)](https://arxiv.org/abs/1812.08466) — standard generowania muzyki.
– [Tabela liderów Open ASR](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard) — rankingi na żywo z 2026 r.
– [TTS Arena](https://huggingface.co/spaces/TTS-AGI/TTS-Arena) — tabela wyników TTS głosowana przez ludzi.
- [benchmark MMAU-Pro](https://mmaubenchmark.github.io/) — tabela liderów rozumowania LALM.
- [HEAR benchmark](https://hearbenchmark.com/) — testy porównawcze audio SSL.