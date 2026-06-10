# Whisper — architektura i dostrajanie

> Whisper to oparta na architekturze Transformer sieć typu koder-dekoder przetwarzająca dźwięk w 30-sekundowych oknach, wytrenowana na 680 tysiącach godzin wielojęzycznych, słabo nadzorowanych (weakly supervised) par audio-tekst. Oferuje jedną uniwersalną architekturę realizującą wiele zadań z solidną obsługą 99 języków. Stanowi referencyjny model ASR w 2026 roku.

**Typ:** Kompendium  
**Języki:** Python  
**Warunki wstępne:** Faza 6 · 04 (ASR), Faza 5 · 10 (Mechanizm atencji), Faza 7 · 05 (Pełna architektura Transformer)  
**Czas:** ~75 minut  

## Problem

Model Whisper, udostępniony przez OpenAI we wrześniu 2022 r., zrewolucjonizował rynek ASR: pozwala na bezproblemowe generowanie transkrypcji w 99 językach, jest wysoce odporny na zakłócenia i może być uruchamiany lokalnie. Do 2024 roku wydano zoptymalizowane warianty Large-v3 oraz Turbo, a do 2026 roku Whisper stał się domyślnym rozwiązaniem do transkrypcji podcastów, asystentów głosowych czy napisów w serwisie YouTube.

Jednak Whisper nie jest idealnym rozwiązaniem typu „czarna skrzynka” do każdego problemu. W przypadku zmiany domeny (np. żargon branżowy, specyficzne akcenty, nazwy własne, bardzo krótkie nagrania, długie okresy ciszy) jakość transkrypcji gwałtownie spada. Aby skutecznie wdrożyć ten model, musisz zrozumieć:
1. Jak dokładnie wygląda wewnętrzna architektura modelu.
2. Jak poprawnie realizować podział na fragmenty (chunking) i przetwarzanie strumieniowe.
3. Kiedy i w jaki sposób przeprowadzić dostrojenie (finetuning).

## Koncepcja

![Whisper: architektura koder-dekoder, zadania, wnioskowanie na fragmentach (chunking), dostrajanie](../assets/whisper.svg)

**Architektura.** Standardowy model koder-dekoder typu Transformer.

- **Wejście:** 30-sekundowy spektrogram log-mel o wymiarach 80 kanałów melowych i kroku (hop) 10 ms, co przekłada się na 3000 ramek czasowych. Krótsze klipy są uzupełniane zerami (padding), a dłuższe dzielone na 30-sekundowe fragmenty (chunks).
- **Koder:** warstwy splotowe zmniejszające rozdzielczość czasową (conv downsampling ze stride=2) + `N` bloków Transformer. Dla wersji Large-v3: 32 warstwy, wymiarowość 1280 (1280-dim), 20 głowic atencji.
- **Dekoder:** `N` bloków Transformer z przyczynową autouwagą (causal self-attention) oraz atencją krzyżową (cross-attention) nakierowaną na wyjścia enkodera. Posiada te same wymiary co enkoder.
- **Wyjście:** tokeny BPE ze słownika o rozmiarze 51 865 pozycji.

Model Large-v3 posiada około 1.55B parametrów. Wersja Turbo wykorzystuje odchudzony dekoder (4 warstwy zamiast 32), co pozwala na 8-krotne zmniejszenie latencji przy minimalnym wzroście współczynnika WER (poniżej 1%).

**Format promptu.** Whisper to model wielozadaniowy sterowany za pomocą specjalnych tokenów (control tokens) umieszczanych na początku sekwencji dekodera:

```
<|startoftranscript|><|en|><|transcribe|><|notimestamps|> Hello world.<|endoftext|>
```

- `<|en|>` — znacznik języka (LID); wymusza transkrypcję w danym języku lub tłumaczenie na ten język.
- `<|transcribe|>` lub `<|translate|>` — definiuje zadanie: dosłowna transkrypcja lub bezpośrednie tłumaczenie na język angielski.
- `<|notimestamps|>` — wyłącza generowanie znaczników czasu (co przyspiesza dekodowanie).

Dzięki temu jeden zestaw wag modelu realizuje różne zadania – zmiana `<|en|>` na `<|fr|>` automatycznie przełącza model w tryb obsługi języka francuskiego.

**Okno 30-sekundowe.** Domyślny rozmiar wejścia to sztywne 30 sekund. Dłuższe nagrania wymagają podziału na fragmenty, a krótsze dopełnienia zerami. Ponieważ model nie wspiera natywnego przetwarzania strumieniowego, w praktyce produkcyjnej stosuje się rozwiązania takie jak WhisperX, Whisper-Streaming lub bibliotekę faster-whisper.

**Normalizacja log-mel.** Wykorzystuje wzór `(log_mel - mean) / std`, gdzie statystyki pochodzą bezpośrednio ze zbioru treningowego modelu. *Niezbędne* jest używanie oficjalnej funkcji przetwarzania wstępnego Whisper (`whisper.audio.log_mel_spectrogram`), a nie standardowej biblioteki Librosa.

### Warianty modeli w 2026 r.

| Wariant | Liczba parametrów | Latencja (A100) | WER (LibriSpeech test-clean) |
|--------|--------|----------------|----------------------------|
| Tiny | 39M | 0.2× | 5,4% |
| Base | 74M | 0.3× | 4,1% |
| Small | 244M | 0.5× | 3,0% |
| Medium | 769M | 1.0× | 2,7% |
| Large-v3 | 1,55B | 2.0× | 1,8% |
| Large-v3-turbo | 809M | 0.25× | 1,58% |
| Whisper-Streaming (2024) | 1,55B | strumieniowo | 2,0% |

### Dostrojenie (Finetuning)

Kanoniczny proces dostrajania w 2026 r.:
1. Przygotuj od 10 do 100 godzin nagrań audio z docelowej domeny wraz z dokładnymi transkrypcjami.
2. Użyj klasy `transformers.Seq2SeqTrainer` z włączoną opcją `predict_with_generate`.
3. Zastosuj metodę LoRA na warstwach atencji `q_proj`, `k_proj`, `v_proj` — zmniejsza to zużycie pamięci GPU aż 4-krotnie, przy marginalnej różnicy w WER (<0,3% w porównaniu do pełnego finetuningu).
4. Jeśli dysponujesz mniej niż 10 godzinami danych, zamroź enkoder i dostrajaj wyłącznie dekoder.
5. Zawsze korzystaj z oryginalnego tokenizera oraz formatu promptu modelu Whisper; nigdy nie podmieniaj tokenizera na inny.

*Przykłady zastosowań:* Dostrojenie wersji Medium na 20 godzinach dyktand medycznych obniża WER z 12% do 4,5% dla terminologii specjalistycznej. Dostrojenie modelu Turbo na zaledwie 4 godzinach nagrań w języku islandzkim obniżyło WER z 18% do 6%.

## Implementacja krok po kroku

### Krok 1: Wnioskowanie z użyciem domyślnego modelu Whisper (out-of-the-box)

```python
import whisper
model = whisper.load_model("large-v3-turbo")
result = model.transcribe(
    "clip.wav",
    language="pl",
    task="transcribe",
    temperature=0.0,
    condition_on_previous_text=False,  # zapobiega zapętleniom i halucynacjom
)
print(result["text"])
for seg in result["segments"]:
    print(f"[{seg['start']:.2f}–{seg['end']:.2f}] {seg['text']}")
```

*Dobre praktyki:* Zawsze jawnie ustawiaj `temperature=0.0` (domyślnie Whisper zwiększa temperaturę w pętli `0.0 -> 0.2 -> 0.4...` przy niskiej pewności, co sprzyja błędom), wyłączaj `condition_on_previous_text=False` w zaszumionych środowiskach (zapobiega to kaskadowym halucynacjom) oraz kontroluj próg ciszy za pomocą `no_speech_threshold=0.6`.

### Krok 2: Przetwarzanie długich nagrań (chunking)

```python
# WhisperX to standard produkcyjny dla długich nagrań ze znacznikami czasu na poziomie słów
import whisperx
model = whisperx.load_model("large-v3-turbo", device="cuda", compute_type="float16")
result = model.transcribe("1hour.mp3", batch_size=16, chunk_size=30)
```

WhisperX integruje: (1) bramkowanie za pomocą Silero VAD, (2) dokładne wyrównanie czasowe (forced alignment) na poziomie słów z użyciem modelu wav2vec 2.0, (3) diaryzację mówców (speaker diarization) za pomocą `pyannote.audio`. To kluczowy zestaw narzędzi w systemach produkcyjnych.

### Krok 3: Dostrajanie przy użyciu metody PEFT/LoRA

```python
from transformers import WhisperForConditionalGeneration, WhisperProcessor
from peft import LoraConfig, get_peft_model

model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-large-v3-turbo")
lora = LoraConfig(
    r=16, lora_alpha=32, target_modules=["q_proj", "v_proj"],
    lora_dropout=0.1, bias="none", task_type="SEQ_2_SEQ_LM",
)
model = get_peft_model(model, lora)
# model.print_trainable_parameters()  -> ~3M parametrów trenowalnych na 809M wszystkich
```

Po przygotowaniu adaptera LoRA uruchom standardową pętlę uczenia Hugging Face `Seq2SeqTrainer`. Zapisuj punkty kontrolne (checkpoints) co 1000 kroków i monitoruj postęp za pomocą metryki WER na zbiorze walidacyjnym.

### Krok 4: Analiza wag atencji krzyżowej (cross-attention)

```python
# Pobranie wag atencji krzyżowej podczas generowania w celu weryfikacji wyrównania czasowego.
with torch.inference_mode():
    out = model.generate(
        input_features=features,
        return_dict_in_generate=True,
        output_attentions=True,
    )
# out.cross_attentions zawiera tensory o kształcie: warstwa x głowica x krok x długość_źródła
```

Wizualizacja za pomocą mapy ciepła (heatmap) ujawnia wyraźną przekątną podczas generowania kolejnych kroków dekodera na osi czasu enkodera. Ta przekątna odpowiada za mechanizm wyznaczania znaczników czasu (timestamps) na poziomie słów.

## Sugerowane rozwiązania (2026)

| Scenariusz | Wybierz |
|----------|------|
| Ogólne zastosowania ASR, tryb offline | Large-v3-turbo uruchamiany przez `whisperx` |
| Urządzenia mobilne i wbudowane (edge) | Skwantowany (int8) model Whisper-Tiny lub Moonshine |
| Przetwarzanie długich, wielojęzycznych nagrań | Large-v3 z użyciem `whisperx` + diaryzacja mówców |
| Języki o ograniczonych zasobach (low-resource) | Dostrojenie wersji Medium lub Turbo przy użyciu metody LoRA |
| Niskie opóźnienia (streaming, latencja ~2 s) | Whisper-Streaming lub Parakeet-TDT |
| Dokładne dopasowanie czasowe słów | WhisperX (wymuszone wyrównanie za pomocą wav2vec 2.0) |

*Wskazówka:* Biblioteka `faster-whisper` (wykorzystująca silnik CTranslate2) zapewnia najszybsze wnioskowanie na CPU oraz GPU, osiągając nawet 4-krotne przyspieszenie przy zachowaniu identycznej dokładności co implementacja referencyjna.

## Typowe pułapki (wciąż aktualne w 2026 r.)

- **Halucynacje na fragmentach ciszy.** Whisper został wytrenowany na napisach z internetu, przez co na cichych fragmentach potrafi generować frazy typu: „Dzięki za obejrzenie!”, „Subskrybuj nasz kanał!” czy losowe fragmenty piosenek. Zawsze filtruj wejściowe audio za pomocą bramki VAD przed przekazaniem go do modelu.
- **Kaskadowe błędy przy włączonym `condition_on_previous_text`.** Pojedyncza halucynacja w jednym oknie czasowym zanieczyszcza kontekst dla kolejnych okien. Ustaw ten parametr na `False`, chyba że bardzo zależy Ci na spójności stylistycznej i ciągłości zdań między fragmentami.
- **Dopełnianie krótkich nagrań (padding).** Krótkie nagranie (np. 2-sekundowe) dopełnione do 30 sekund może prowokować model do halucynowania w końcowej strefie ciszy. Używaj VAD lub upewnij się, że poprawnie konfigurujesz maskowanie dopełnienia.
- **Niedopasowanie ekstrakcji cech.** Użycie spektrogramów wygenerowanych za pomocą biblioteki Librosa zamiast funkcji wbudowanej w Whisper daje niemal losowe, błędne wyniki. Zawsze stosuj `whisper.audio.log_mel_spectrogram`.

## Zadanie do wykonania

Zapisz jako `outputs/skill-whisper-tuner.md`. Zaprojektuj kompletny potok dostrajania (finetuning) lub wnioskowania (inference) modelu Whisper dla wybranej domeny.

## Ćwiczenia

1. **Łatwe.** Uruchom skrypt `code/main.py`. Skrypt tokenizuje prompt w formacie modelu Whisper, oblicza wymiary tensorów wejściowych i wyjściowych oraz planuje podział na 30-sekundowe okna czasowe dla 10-minutowego pliku audio.
2. **Średnie.** Zainstaluj `faster-whisper`, wykonaj transkrypcję 10-minutowego podcastu i porównaj wskaźnik WER z transkrypcją referencyjną. Sprawdź zachowanie modelu przy `language='auto'` w porównaniu z jawnym ustawieniem `language='pl'`.
3. **Trudne.** Używając zbiorów danych Hugging Face (np. Common Voice), wybierz język o słabszym wsparciu w modelu Whisper (np. urdu), dostrój wersję Medium przy użyciu LoRA przez 2 epoki i porównaj wskaźnik WER przed i po dostrojeniu.

## Kluczowe terminy

| Termin | Potoczne określenie | Co to naprawdę oznacza |
|------|-----------------|----------------------|
| Okno 30-sekundowe | Limit okna wejściowego | Sztywne ograniczenie długości wejścia modelu Whisper; dłuższe pliki muszą być dzielone na części. |
| SOT token | Start of Transcript | Specjalny token `<\|startoftranscript\|>` rozpoczynający generowanie sekwencji w dekoderze. |
| Token znaczników czasu | Timestamp Token | Specjalne tokeny w słowniku reprezentujące przesunięcia czasowe (z krokiem 20 ms), służące do lokalizowania słów w czasie. |
| Turbo | Odchudzona wersja | Wariant z 4-warstwowym dekoderem; działa 8-krotnie szybciej przy niemal niezauważalnym spadku jakości. |
| WhisperX | Zaawansowany wrapper | Narzędzie integrujące VAD, transkrypcję Whisper, wyrównanie czasowe za pomocą wav2vec 2.0 oraz diaryzację mówców. |
| Dostrajanie LoRA | Parameter-Efficient Tuning | Metoda dołączania niskopoziomowych adapterów (adapters) do warstw atencji; trenuje się tylko ok. 0.3% parametrów sieci. |
| Halucynacja | Cichy błąd (silent failure) | Wygenerowanie przez model gramatycznie poprawnego i płynnego tekstu na podstawie szumu tła lub ciszy. |

## Dalsze czytanie

- [Radford et al. (2022). Whisper Paper](https://arxiv.org/abs/2212.04356) — oryginalna publikacja wprowadzająca model Whisper oraz zasady uczenia na dużą skalę.
- [OpenAI (2024). Whisper Large-v3-turbo Release](https://github.com/openai/whisper/discussions/2363) — specyfikacja wariantu Turbo z przyspieszonym dekoderem.
- [Bain et al. (2023). WhisperX](https://arxiv.org/abs/2303.00747) — technika precyzyjnego wyrównywania czasowego i diaryzacji długich nagrań.
- [Systran — faster-whisper Repository](https://github.com/SYSTRAN/faster-whisper) — zoptymalizowana wersja modelu wykorzystująca CTranslate2.
- [Hugging Face — Whisper Fine-Tuning Tutorial](https://huggingface.co/blog/fine-tune-whisper) — kompletny przewodnik po dostrajaniu modelu z użyciem bibliotek PEFT i Transformers.
