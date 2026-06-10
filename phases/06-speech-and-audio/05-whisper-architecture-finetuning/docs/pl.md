# Whisper — architektura i dostrajanie

> Whisper to 30-sekundowy koder-dekoder transformatorowy, przeszkolony na 680 tys. godzin wielojęzycznych, słabo nadzorowanych par audio-tekst. Jedna architektura, wiele zadań, solidna obsługa w 99 językach. Referencyjny ASR na rok 2026.

**Typ:** Kompilacja
**Języki:** Python
**Warunki wstępne:** Faza 6 · 04 (ASR), Faza 5 · 10 (Uwaga), Faza 7 · 05 (Pełny transformator)
**Czas:** ~75 minut

## Problem

Whisper, wydany przez OpenAI we wrześniu 2022 r., był pierwszym modelem ASR dostarczanym jako towar: wklej dźwięk, pobierz tekst, 99 języków, odporny na zakłócenia, działa na laptopie. Do 2024 roku OpenAI dostarczyło warianty Large-v3 i Turbo; do 2026 r. Szept stanie się domyślną podstawą dla wszystkiego, od transkrypcji podcastów, przez asystentów głosowych, po napisy w YouTube.

Jednak Whisper nie jest rurociągiem, który można na zawsze traktować jak czarną skrzynkę. Zmiana domeny to zabija — żargon techniczny, akcenty mówiące, rzeczowniki własne, krótkie klipy, cisza. Musisz wiedzieć:

1. Co właściwie kryje się w środku.
2. Jak poprawnie nadać fragmentaryczny, przesyłany strumieniowo lub długi dźwięk.
3. Kiedy i jak dostroić.

## Koncepcja

![Koder-dekoder szeptów, zadania, wnioskowanie fragmentaryczne, dostrajanie](../assets/whisper.svg)

**Architektura.** Standardowy koder-dekoder transformatorowy.

- Wejście: 30-sekundowy spektrogram log-mel, 80 meli, skok 10 ms → 3000 klatek. Krótsze klipy są dopełniane zerami, dłuższe klipy są podzielone na kawałki.
- Koder: conv-downsample (krok 2) + `N` bloki transformatora. Dla Large-v3: 32 warstwy, 1280-dim, 20 głowic.
- Dekoder: `N` bloki transformatorowe z przyczynowym samonastawnością + nawiązaniem krzyżowym na wyjściu enkodera. Ten sam rozmiar co enkoder.
- Dane wyjściowe: tokeny BPE w słownictwie zawierającym 51 865 tokenów.

Large-v3 ma parametry 1,55B. Turbo wykorzystuje 4-warstwowy dekoder (z 32), zmniejszając opóźnienia 8 razy przy trafieniu WER <1%.

**Format podpowiedzi.** Whisper to model wielozadaniowy sterowany specjalnymi tokenami w podpowiedzi dekodera:

```
<|startoftranscript|><|en|><|transcribe|><|notimestamps|> Hello world.<|endoftext|>
```

- `<|en|>` — znacznik języka; wymusza zachowanie polegające na translacji i transkrypcji.
- `<|transcribe|>` lub `<|translate|>` — tłumaczy tekst w języku angielskim z dowolnego języka lub dosłownie.
- `<|notimestamps|>` — pomiń znaczniki czasu na poziomie słowa (szybciej).

Podpowiedź pozwala jednemu modelowi wykonywać wiele zadań. Zmień `<|en|>` na `<|fr|>` i nastąpi transkrypcja języka francuskiego.

**Okno 30-sekundowe.** Wszystko jest przypięte do 30 sekund. Dłuższe klipy wymagają porcjowania; krótsze klipy są wyściełane. Windows nie jest natywnie przesyłany strumieniowo — dlatego istnieją WhisperX, Whisper-Streaming i szybszy szept.

**Normalizacja log-mel.** `(log_mel - mean) / std` gdzie statystyki pochodzą z korpusu szkoleniowego Whisper. *Musisz* używać wstępnego przetwarzania Whisper (`whisper.audio.log_mel_spectrogram`), a nie `librosa.feature.melspectrogram`.

### Warianty w 2026 r

| Wariant | Parametry | Opóźnienie (A100) | WER (czyszczenie LibriSpeech) |
|--------|--------|----------------|----------------------------|
| Mały | 39M | 1× w czasie rzeczywistym | 5,4% |
| Baza | 74M | 1× | 4,1% |
| Mały | 244M | 1× | 3,0% |
| Średni | 769M | 1× | 2,7% |
| Duży-v3 | 1,55B | 2× | 1,8% |
| Duże-v3-turbo | 809M | 8× | 1,58% |
| Przesyłanie strumieniowe szeptów (2024) | 1,55B | przesyłanie strumieniowe | 2,0% |

### Dostrajanie

Kanoniczny przepływ pracy w 2026 r.:

1. Zbierz 10–100 godzin nagrań audio z domeny docelowej z dopasowanymi transkrypcjami.
2. Uruchom `transformers.Seq2SeqTrainer` z wywołaniem zwrotnym `generate_with_loss`.
3. Wydajność pod względem parametrów: LoRA na `q_proj`, `k_proj`, `v_proj` warstw uwagi zmniejsza pamięć GPU 4-krotnie przy koszcie WER <0,3.
4. Zamroź koder, jeśli masz <10 godzin. Tylko dostrój dekoder.
5. Użyj własnego tokenizera i formatu podpowiedzi Whisper; nigdy nie wymieniaj tokenizerów.

Wyniki społeczności: dostrojenie Medium w przypadku 20 godzin dyktando medycznego obniża WER z 12% do 4,5% w przypadku słownictwa medycznego. Dostrojenie Turbo na 4 godziny islandzkiego zmniejsza WER z 18% do 6%.

## Zbuduj to

### Krok 1: uruchom Whisper po wyjęciu z pudełka

```python
import whisper
model = whisper.load_model("large-v3-turbo")
result = model.transcribe(
    "clip.wav",
    language="en",
    task="transcribe",
    temperature=0.0,
    condition_on_previous_text=False,  # prevents runaway repetition
)
print(result["text"])
for seg in result["segments"]:
    print(f"[{seg['start']:.2f}–{seg['end']:.2f}] {seg['text']}")
```

Kluczowe wartości domyślne, które zawsze należy zastępować: `temperature=0.0` (domyślne próbkowanie to 0,0 → 0,2 → 0,4… łańcuch awaryjny), `condition_on_previous_text=False` (zapobiega problemowi kaskadowych halucynacji) i `no_speech_threshold=0.6` (wykrywanie ciszy).

### Krok 2: długi, kawałkowany

```python
# whisperx is the 2026 reference for long-form with word-level timestamps
import whisperx
model = whisperx.load_model("large-v3-turbo", device="cuda", compute_type="float16")
segments = model.transcribe("1hour.mp3", batch_size=16, chunk_size=30)
```

WhisperX dodaje (1) bramkowanie Silero VAD, (2) wyrównanie na poziomie słowa za pomocą wav2vec 2.0, (3) diaryzację za pomocą `pyannote.audio`. Najważniejszy element transkrypcji produkcji na rok 2026.

### Krok 3: dostosuj się do LoRA

```python
from transformers import WhisperForConditionalGeneration, WhisperProcessor
from peft import LoraConfig, get_peft_model

model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-large-v3-turbo")
lora = LoraConfig(
    r=16, lora_alpha=32, target_modules=["q_proj", "v_proj"],
    lora_dropout=0.1, bias="none", task_type="SEQ_2_SEQ_LM",
)
model = get_peft_model(model, lora)
# model.print_trainable_parameters()  -> ~3M trainable / 809M total
```

Następnie standardowa pętla Trainer. Punkt kontrolny co 1000 kroków. Oceń za pomocą WER w przypadku wstrzymania.

### Krok 4: sprawdź, czego uczy się każda warstwa

```python
# Grab cross-attention weights during decode to see what the decoder attends to.
with torch.inference_mode():
    out = model.generate(
        input_features=features,
        return_dict_in_generate=True,
        output_attentions=True,
    )
# out.cross_attentions: layer × head × step × src_len
```

Wizualizuj za pomocą mapy cieplnej — zobaczysz wyrównanie po przekątnej podczas skanowania kroków dekodera przez ramki kodera. Ta przekątna to koncepcja znaczników czasu słów Whispera.

## Użyj tego

Stos na rok 2026:

| Sytuacja | Wybierz |
|----------|------|
| Ogólny angielski, offline | Large-v3-turbo przez `whisperx` |
| Mobilne / brzegowe | Whisper-Tiny kwantyzowany (int8) lub Moonshine |
| Wielojęzyczny, długi formularz | Large-v3 poprzez `whisperx` + diaryzacja |
| Język o niskich zasobach | Dostosuj Medium lub Turbo za pomocą LoRA |
| Przesyłanie strumieniowe (opóźnienie 2 s) | Whisper-Streaming lub Parakeet-TDT |
| Znaczniki czasu na poziomie słów | WhisperX (wymuszone wyrównanie przez wav2vec 2.0) |

`faster-whisper` (backend CTranslate2) to najszybsze środowisko wykonawcze wnioskowania CPU+GPU w 2026 r. — 4 razy szybsze niż wanilia przy identycznych wynikach.

## Pułapki, które nadal będą widoczne w 2026 r

- **Halucynacyjny tekst o ciszy.** Szepty wytrenowane na napisach obejmują „Dzięki za obejrzenie!”, „Subskrybuj!”, teksty piosenek. Zawsze przed wywołaniem należy bramkę VAD.
- **`condition_on_previous_text` kaskada.** Jedna halucynacja zanieczyszcza kolejne okna. Ustaw `False`, chyba że potrzebujesz płynności w poszczególnych fragmentach.
- **Dopełnienie krótkiego klipu.** 2-sekundowy klip skrócony do 30 sekund może wywoływać halucynacje w końcowej ciszy. Użyj `pad=False` lub bramki VAD.
- **Błędne statystyki mel.** Używanie meli librosy zamiast Whispera daje niemal losowe wyniki. Użyj `whisper.audio.log_mel_spectrogram`.

## Wyślij to

Zapisz jako `outputs/skill-whisper-tuner.md`. Zaprojektuj potok dostrajania lub wnioskowania Whisper dla danej domeny.

## Ćwiczenia

1. **Łatwe.** Uruchom `code/main.py`. Tokenizuje monit w stylu szeptu, oblicza zdekodowane budżety kształtów i drukuje harmonogram fragmentów dla 10-minutowego klipu.
2. **Średni.** Zainstaluj `faster-whisper`, dokonaj transkrypcji 10-minutowego podcastu, porównaj WER z transkrypcją ludzką. Wypróbuj `language="auto"` zamiast wymuszonego `language="en"`.
3. **Trudny.** Używając HF `datasets`, wybierz język, z którym Whisper ma problemy (np. urdu), dostrój Medium za pomocą LoRA przez 2 epoki po 2 godziny i zgłoś różnicę WER.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Okno 30-sekundowe | Granica szeptu | Twardy korek wejściowy; fragment dłuższego dźwięku. |
| CZAS | Początek transkrypcji | `<\|startoftranscript\|>` uruchamia monit dekodera. |
| Token znaczników czasu | Wyrównanie czasowe | Każde przesunięcie o 0,02 s jest specjalnym znacznikiem w słownictwie 51 tys. |
| Turbo | Szybki wariant | 4 warstwy dekodera, 8 razy szybciej, <1% regresji WER. |
| SzeptX | Długie opakowanie | VAD + Whisper + wyrównanie wav2vec + diaryzacja. |
| Dostrojenie LoRA | Wydajne strojenie | Dodaj do uwagi adaptery niskiej rangi; trenuj ~0,3% parametrów. |
| Halucynacja | Cicha porażka | Whisper generuje płynny angielski na podstawie hałasu/ciszy. |

## Dalsze czytanie

- [Radford i in. (2022). Papier szeptany](https://arxiv.org/abs/2212.04356) — oryginalna recepta na architekturę i szkolenie.
- [OpenAI (2024). Wersja Whisper Large-v3-turbo](https://github.com/openai/whisper/discussions/2363) — dekoder 4-warstwowy, przyspieszenie 8×.
- [Bain i in. (2023). WhisperX](https://arxiv.org/abs/2303.00747) — długa forma, wyrównana do słów, diaaryzowana.
- [Systran — repozytorium szybszego szeptu](https://github.com/SYSTRAN/faster-whisper) — wspierane przez CTranslate2, 4 razy szybsze.
- [HuggingFace — samouczek dostrajania szeptu](https://huggingface.co/blog/fine-tune-whisper) — kanoniczny przewodnik po LoRA/pełnym FT.