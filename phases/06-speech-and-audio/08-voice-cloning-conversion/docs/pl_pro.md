# Klonowanie głosu i konwersja głosu

> Klonowanie głosu (Voice Cloning) pozwala na odczytanie dowolnego tekstu głosem wybranego mówcy. Konwersja głosu (Voice Conversion) przekształca brzmienie Twojego głosu w głos innej osoby, zachowując przy tym oryginalną wypowiedź. Oba te zadania opierają się na tej samej zasadzie: oddzieleniu tożsamości mówcy (speaker identity) od treści językowej (content).

**Typ:** Kompendium  
**Języki:** Python  
**Warunki wstępne:** Faza 6 · 06 (Rozpoznawanie i weryfikacja mówcy), Faza 6 · 07 (Text-to-Speech)  
**Czas:** ~75 minut  

## Problem

W 2026 roku zaledwie 5-sekundowe nagranie audio wystarcza do stworzenia wysokiej jakości klonu głosu na konsumenckiej karcie graficznej. Narzędzia takie jak ElevenLabs, F5-TTS, OpenVoice v2 czy VoiceBox oferują klonowanie w trybie zero-shot (bez dodatkowego uczenia) lub few-shot (z kilkoma próbkami). Technologia ta jest zarówno przełomem (ułatwienia dostępności, dubbing, syntezatory mowy dla osób chorych), jak i zagrożeniem (oszustwa telefoniczne, dezinformacja polityczna oparta na deepfake'ach, naruszenia praw autorskich).

Dwa ściśle ze sobą powiązane zadania:
- **Klonowanie głosu (TTS):** tekst wejściowy + 5-sekundowe nagranie referencyjne → wygenerowana mowa w tym samym głosie.
- **Konwersja głosu (VC):** nagranie źródłowe (mówca A wypowiadający tekst X) + nagranie referencyjne mówcy B → nagranie mówcy B wypowiadającego tekst X.

Oba procesy wymagają zdekomponowania wejściowej fali dźwiękowej (rozdzielenia informacji o treści, tożsamości mówcy oraz prozodii), a następnie połączenia treści z jednego źródła z barwą głosu drugiego.

Kluczowe wymagania prawne (stan na 2026 r.): **nakładanie cyfrowych znaków wodnych (watermarking) oraz wdrożenie mechanizmów weryfikacji zgody są prawnie wymagane w Unii Europejskiej (EU AI Act, obowiązujący od sierpnia 2026 r.) oraz w Kalifornii (AB 2905, od 2025 r.)**. Twój potok produkcyjny musi osadzać niesłyszalny znak wodny w generowanym pliku oraz uniemożliwiać klonowanie głosu bez udokumentowanej zgody właściciela.

## Koncepcja

![Klonowanie a konwersja głosu: dekompozycja, zamiana reprezentacji mówcy i rekombinacja](../assets/voice-cloning.svg)

**Klonowanie zero-shot.** Przekazanie 5-sekundowej próbki do modelu wytrenowanego na nagraniach tysięcy mówców. Enkoder mówcy (speaker encoder) mapuje próbkę na wektor osadzenia mówcy (speaker embedding); dekoder TTS generuje mowę na podstawie tego wektora oraz tekstu.  
*Przykłady:* F5-TTS (2024), YourTTS (2022), XTTS v2 (2024), OpenVoice v2 (2024).

**Dostrojenie few-shot (kilkupróbkowe).** Wykorzystując nagranie głosu docelowego o długości od 5 do 30 minut oraz metodę LoRA, dostraja się model bazowy przez około godzinę. Jakość generowanej mowy rośnie wówczas od poziomu „akceptowalnego” do „nie do odróżnienia” od oryginału. Metodę tę wspierają rozwiązania komercyjne oraz otwarte biblioteki powiązane z F5-TTS.

**Konwersja głosu (Voice Conversion - VC).** Dwa główne podejścia:
- **Synteza na podstawie rozpoznawania (Recognition-Synthesis).** Wykorzystuje się model zbliżony do ASR do ekstrakcji reprezentacji treści (np. prawdopodobieństw fonemów - PPG, Phonetic Posteriorgrams), a następnie syntezuje się dźwięk na nowo, warunkując go wektorem osadzenia docelowego mówcy. Metoda ta jest odporna na różnice językowe i akcent. Przykłady: KNN-VC (2023), Diff-HierVC (2023).
- **Rozplątywanie cech (Disentanglement).** Trenuje się autoenkoder z wąskim gardłem (bottleneck), który uczy się oddzielać reprezentacje treści, mówcy i prozodii w przestrzeni ukrytej. Podczas wnioskowania podmienia się wektor osadzenia mówcy na docelowy. Metoda charakteryzuje się niższą jakością, ale jest bardzo szybka. Przykłady: AutoVC (2019), warianty VITS-VC.

**Klonowanie oparte na kodekach neuronowych (2024+).** Modele takie jak VALL-E, VALL-E 2, NaturalSpeech 3 czy VoiceBox traktują dźwięk jako ciąg dyskretnych tokenów z kodeków takich jak SoundStream lub EnCodec. Wykorzystują one duże modele autoregresyjne (AR) lub modele dopasowywania przepływu (flow matching) bezpośrednio na tokenach kodeka. Pozwala to uzyskać jakość syntezy porównywalną z najlepszymi systemami komercyjnymi.

### Etyka i bezpieczeństwo w systemach produkcyjnych

**Cyfrowy znak wodny (Audio Watermarking).** Narzędzia takie jak SilentCipher (2024) pozwalają na niesłyszalne zakodowanie informacji o rozmiarze 16–32 bitów w sygnale audio. Znak wodny jest wysoce odporny na kompresję stratną (np. MP3), re-sampling i typowe operacje edycyjne.

**Bramki weryfikacji zgody (Consent Gates).** Każda wygenerowana próbka mowy musi być powiązana z kryptograficznie podpisanym rekordem zgody: „Ja, Jan Kowalski, w dniu 22.04.2026 autoryzuję użycie mojego głosu do celów X”. Rekord ten powinien być zapisywany w bezpiecznym logu systemowym odpornym na modyfikacje.

**Detekcja deepfake.** Modele AASIST, RawNet2 oraz Wav2Vec2-AASIST stanowią standard w dziedzinie detektorów mowy syntetycznej. W benchmarku ASVspoof 2025 detektory te osiągnęły wskaźnik EER na poziomie 0,8–2,3% w konfrontacji z najnowszymi generatorami (ElevenLabs, VALL-E 2, Bark).

### Wyniki porównawcze (stan na 2026 r.)

| Model | Zero-shot? | SECS (podobieństwo do wzorca) | WER (zrozumiałość ASR) | Liczba parametrów |
|-------|------|----------|--------------|--------|
| F5-TTS | Tak | 0,72 | 2,1% | 335M |
| XTTS v2 | Tak | 0,65 | 3,5% | 470M |
| OpenVoice v2 | Tak | 0,70 | 2,8% | 220M |
| VALL-E 2 | Tak | 0,77 | 2,4% | 370M |
| VoiceBox | Tak | 0,78 | 2,1% | 330M |

Wartość SECS > 0,70 oznacza zazwyczaj, że wygenerowany głos jest dla większości słuchaczy nie do odróżnienia od prawdziwego głosu mówcy.

## Implementacja krok po kroku

### Krok 1: Koncepcyjny potok weryfikacji i syntezy (na bazie ppg)

```python
def clone_pipeline(ref_audio, text, target_embedder, tts_model):
    speaker_emb = target_embedder.encode(ref_audio)
    mel = tts_model(text, speaker=speaker_emb)
    return vocoder(mel)
```

Potok jest koncepcyjnie prosty – główna trudność leży w odpowiedniej architekturze modelu TTS oraz enkodera mówcy (speaker encoder).

### Krok 2: Klonowanie zero-shot z użyciem modelu F5-TTS

```python
from f5_tts.api import F5TTS
tts = F5TTS()
wav = tts.infer(
    ref_file="user_5s.wav",
    ref_text="The quick brown fox jumps over the lazy dog.",
    gen_text="Please add milk and bread to my shopping list.",
)
```

Transkrypcja próbki referencyjnej (`ref_text`) musi dokładnie odpowiadać nagraniu (`ref_file`); wszelkie rozbieżności zakłócają proces dopasowania czasowego (alignment) i generowania.

### Krok 3: Konwersja głosu przy użyciu modelu KNN-VC

```python
import torch
from knnvc import KNNVC  # Model KNN-VC (https://github.com/bshall/knn-vc)
vc = KNNVC.load("wavlm-base-plus")
out_wav = vc.convert(source="my_voice.wav", target_pool=["target_speaker_1.wav", "target_speaker_2.wav"])
```

KNN-VC wykorzystuje model WavLM do ekstrakcji reprezentacji ramka-po-ramce dla nagrania źródłowego i docelowego, a następnie zastępuje każdą ramkę źródłową jej najbliższym sąsiadem (nearest neighbor) z puli docelowej. Metoda ta jest w pełni nieparametryczna i wymaga zaledwie minuty nagrań docelowych.

### Krok 4: Osadzanie cyfrowego znaku wodnego

```python
from silentcipher import SilentCipher
sc = SilentCipher(model="2024-06-01")
payload = b"consent_id:abc123;ts:1745353200"
watermarked = sc.embed(wav, sr=24000, message=payload)
detected = sc.detect(watermarked, sr=24000)   # zwraca bajty ładunku (payload)
```

Ładunek o długości ok. 32 bitów jest w pełni wykrywalny nawet po kompresji do MP3 i dodaniu lekkiego szumu.

### Krok 5: Implementacja bramki weryfikacji zgody

```python
def cloned_inference(text, ref_audio, consent_record):
    assert verify_signature(consent_record), "Signed consent required"
    assert consent_record["speaker_id"] == hash_speaker(ref_audio)
    wav = tts.infer(ref_file=ref_audio, gen_text=text)
    wav = watermark(wav, payload=consent_record["id"])
    return wav
```

## Sugerowane rozwiązania (2026)

| Scenariusz | Rekomendowane rozwiązanie |
|----------|------|
| Szybkie klonowanie zero-shot (open-source) | Model F5-TTS lub OpenVoice v2 |
| Klonowanie na potrzeby komercyjne | API Instant Voice Cloning (ElevenLabs v2.5) |
| Konwersja głosu (Voice Conversion) | KNN-VC lub Diff-HierVC |
| Dostrojenie do wielu mówców | StyleTTS 2 z dedykowanymi adapterami mówcy |
| Klonowanie międzyjęzykowe (cross-lingual) | Model XTTS v2 lub VALL-E X |
| Detekcja deepfake | Systemy oparte o model Wav2Vec2-AASIST |

## Typowe pułapki

- **Rozbieżności w transkrypcji referencyjnej.** F5-TTS i podobne modele wymagają, aby tekst referencyjny dokładnie odpowiadał wypowiedzi na nagraniu, łącznie ze znakami interpunkcyjnymi.
- **Nagrania w pomieszczeniach z pogłosem (echo).** Pogłos drastycznie pogarsza jakość klonowania. Wymagaj nagrań w dobrze wygłuszonym pomieszczeniu i z bliskiej odległości od mikrofonu.
- **Niedopasowanie ekspresji emocjonalnej.** Jeśli próbka referencyjna jest wypowiedziana radosnym tonem, wygenerowany klon również będzie zawsze brzmiał radośnie. Dobierz ekspresję próbki referencyjnej do przeznaczenia systemu.
- **Wpływ języka ojczystego (language leakage).** Próba wygenerowania mowy w języku polskim z próbki referencyjnej mówcy anglojęzycznego często skutkuje silnym, nienaturalnym akcentem. Stosuj dedykowane modele międzyjęzykowe (np. XTTS v2, VALL-E X).
- **Brak cyfrowego znaku wodnego.** Niezgodność z prawem UE od sierpnia 2026 r. (EU AI Act).

## Zadanie do wykonania

Zapisz jako `outputs/skill-voice-cloner.md`. Zaprojektuj kompletny potok klonowania lub konwersji głosu, zawierający bramkę weryfikacji zgody, moduł znaku wodnego oraz określone metryki jakości.

## Ćwiczenia

1. **Łatwe.** Uruchom skrypt `code/main.py`. Demonstruje on zamianę wektorów cech mówcy, obliczając podobieństwo cosinusowe pomiędzy próbkami przed i po konwersji.
2. **Średnie.** Wykorzystaj model OpenVoice v2 do sklonowania własnego głosu. Oblicz podobieństwo SECS pomiędzy klonem a nagraniem wzorcowym, a także wskaźnik CER (za pomocą modelu Whisper).
3. **Trudne.** Zaimplementuj SilentCipher, zakoduj znak wodny w 20 próbkach audio, poddaj je kompresji MP3 (128 kbps) i spróbuj odczytać dane. Podaj procent poprawnie odczytanych bitów (bit accuracy).

## Kluczowe terminy

| Termin | Potoczne określenie | Co to naprawdę oznacza |
|------|-----------------|----------------------|
| Zero-shot cloning | Klonowanie z krótkiej próbki | Generowanie głosu na podstawie 5-sekundowej próbki i wektora osadzenia mówcy bez dodatkowego procesu trenowania. |
| PPG | Phonetic Posteriorgram | Wyjściowe prawdopodobieństwa fonemów z modelu ASR dla każdej ramki czasowej, służące jako niezależna od mówcy reprezentacja treści. |
| KNN-VC | Metoda najbliższych sąsiadów | Nieparametryczna konwersja głosu polegająca na podmianie ramek cech nagrania źródłowego na najbliższe im cechy mówcy docelowego. |
| Neural Codec TTS | Synteza oparta na kodekach | Modele syntezy mowy generujące bezpośrednio tokeny dyskretnych kodeków audio (np. EnCodec), spopularyzowane przez model VALL-E. |
| Watermark | Cyfrowy znak wodny | Niesłyszalna sygnatura bitowa wbudowana w sygnał audio, odporna na próby usunięcia i kompresję stratną. |
| SECS | Speaker Cosine Similarity | Wskaźnik oceny wierności klonowania obliczany jako podobieństwo cosinusowe wektora cech głosu referencyjnego i wygenerowanego. |
| AASIST | Detektor deepfake | Model sieci głębokiej służący do weryfikacji autentyczności głosu i wykrywania mowy syntetycznej. |

## Dalsze czytanie

- [Chen et al. (2024). F5-TTS: A Simple and Strong Zero-Shot Text-to-Speech System](https://arxiv.org/abs/2410.06885) — wiodąca otwarta architektura syntezy zero-shot.
- [Wang et al. / Microsoft (2023). Neural Codec Language Models are Zero-Shot Text to Speech Synthesizers](https://arxiv.org/abs/2301.02111) — oryginalna praca wprowadzająca model VALL-E.
- [Qian et al. (2019). AutoVC: Zero-Shot Voice Style Transfer with Only Autoencoder Loss](https://arxiv.org/abs/1905.05879) — pionierska praca nad rozplątywaniem cech w konwersji głosu.
- [Baas, Waubert de Puiseau, Kamper (2023). KNN-VC: Voice Conversion by k-Nearest Neighbors Filtering](https://arxiv.org/abs/2305.18975) — prosty i skuteczny algorytm konwersji głosu.
- [SilentCipher (2024) — Audio Watermarking](https://github.com/sony/silentcipher) — otwarta biblioteka firmy Sony do znakowania audio.
- [ASVspoof Challenges](https://www.asvspoof.org/) — strona cyklu międzynarodowych konkursów w dziedzinie wykrywania deepfake.
