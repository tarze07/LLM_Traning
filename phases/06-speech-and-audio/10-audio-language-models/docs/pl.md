# Modele z językiem audio — Qwen2.5-Omni, Audio Flamingo, GPT-4o Audio

> 2026 modeli audio-językowych rozumowanie nad mową + dźwięk otoczenia + muzyka. Qwen2.5-Omni-7B pasuje do dźwięku GPT-4o w MMAU-Pro. Audio Flamingo Next pokonuje Gemini 2.5 Pro na LongAudioBench. Różnica między otwartym a zamkniętym jest w zasadzie zamknięta — z wyjątkiem zadań z wieloma dźwiękami, gdzie wszyscy są prawie losowi.

**Typ:** Ucz się
**Języki:** Python
**Wymagania wstępne:** Faza 6 · 04 (ASR), Faza 12 · 03 (Modele wizjonersko-językowe), Faza 7 · 10 (Transformatory audio)
**Czas:** ~45 minut

## Problem

Masz 5 sekund dźwięku: pies szczeka, ktoś krzyczy „stop!”, a potem cisza. Przydatne pytania obejmują wiele osi:

- **Transkrypcja.** „Co zostało powiedziane?” — terytorium ASR.
- **Rozumowanie semantyczne.** „Czy dana osoba jest w niebezpieczeństwie?” — wymaga wspólnego zrozumienia szczekania + krzyku + ciszy.
- **Rozumowanie muzyczne.** „Jakie instrumenty grają melodię?”
- **Wyszukiwanie długiego dźwięku.** „Gdzie w tym 90-minutowym wykładzie instruktor wyjaśnił opadanie gradientowe?”

Pojedynczy model, który odpowiada na wszystkie te pytania za pomocą jednego monitu, to **model audio-językowy** (LALM / ALM). Oddzielne od czystego ASR: LALM generują odpowiedzi w języku naturalnym w dowolnej formie, a nie tylko transkrypcje.

## Koncepcja

![Model języka audio: koder audio + projektor + dekoder LLM](../assets/alm-architecture.svg)

### Szablon trójskładnikowy

Każdy LALM 2026 ma ten sam szkielet:

1. **Koder audio.** Koder szeptu · BEATs · CLAP · WavLM · lub koder niestandardowy dla każdego modelu.
2. **Projektor.** Liniowe lub MLP funkcje kodera audio łączące się z przestrzenią osadzania tokenu LLM.
3. **LLM.** Dekoder oparty na Llama / Qwen / Gemma. Pobiera przeplatany tekst + tokeny audio; generuje tekst.

Szkolenie:

- **Etap 1.** Zamrożenie kodera + LLM; projektor pociągowy tylko na ASR / dane napisów.
- **Etap 2.** Pełna/LoRA dostrajanie w zakresie zadań dźwiękowych zgodnych z instrukcjami (kontrola jakości, rozumowanie, rozumienie muzyki).
- **Etap 3 (opcjonalnie).** Wejście/wyjście głosu dodaje dekoder mowy. Robią to Qwen2.5-Omni i AF3-Chat.

### Mapa modeli na rok 2026

| Modelka | Kręgosłup | Koder dźwięku | Modalność wyjściowa | Dostęp |
|-------|---------|--------------|-------|--------|
| Qwen2.5-Omni-7B | Qwen2.5-7B | Niestandardowe + Szept | tekst + mowa | Apache-2.0 |
| Qwen3 – Omni | Qwen3 | Niestandardowe | tekst + mowa | Apache-2.0 |
| Audio Flaming 3 | Qwen2 | AF-KLAP | tekst | NVIDIA niekomercyjna |
| Audio Flaming Dalej | Qwen2 | AF-CLAP v2 | tekst | NVIDIA niekomercyjna |
| ŁOSOSI | Wikuna | Szept + uderzenia | tekst | Apache-2.0 |
| LTU / LTU-AS | Lama | CAV-MAE | tekst | Apache-2.0 |
| GAMA | Lama | AST + Q-Former | tekst | Apache-2.0 |
| Gemini 2.5 Flash/Pro (zamknięty) | Bliźnięta | zastrzeżony | tekst + mowa | API |
| GPT-4o Audio (zamknięte) | GPT-4o | zastrzeżony | tekst + mowa | API |

### Benchmarkowa weryfikacja rzeczywistości (2026)

**MMAU-Pro.** 1800 par QA obejmujących mowę/dźwięk/muzykę/mieszane. Zawiera podzbiór wielu plików audio.

| Modelka | Ogólnie | Mowa | Dźwięk | Muzyka | Wiele dźwięków |
|-------|--------|--------|-------|-------|------------|
| Gemini 2.5 Pro | ~60% | 73,4% | 51,9% | 64,9% | ~22% |
| Gemini 2.5 Flash | ~57% | 73,4% | 50,5% | 64,9% | 21,2% |
| GPT-4o Audio | 52,5% | — | — | — | 26,5% |
| Qwen2.5-Omni-7B | 52,2% | 57,4% | 47,6% | 61,5% | ~20% |
| Audio Flaming 3 | ~54% | — | — | — | — |
| Audio Flaming Dalej | SOTA na LongAudioBench | — | — | — | — |

**Kolumna z wieloma dźwiękami jest potępiająca dla wszystkich.** Losowa szansa przy wielokrotnym wyborze 4 opcji = 25%; większość modelek zdobywa tam punkty. LALMy wciąż mają trudności z porównaniem dwóch klipów.

### Gdzie LALM są przydatne w 2026 r

- **Audyt zgodności nagrań z call center.** „Czy agent wspomniał o wymaganym ujawnieniu?”
- **Dostępność.** Opisuj zdarzenia dźwiękowe dla niesłyszących użytkowników (nie tylko transkrypcja).
- **Moderowanie treści.** Wykrywaj brutalny język, groźny ton i kontekst tła.
- **Rozdziały podcastów / spotkań.** Podsumowanie semantyczne, a nie tylko zwroty mówców.
- **Analiza katalogu muzycznego.** „Znajdź wszystkie utwory ze zmianą tonacji sekcji B”.

### Gdzie NIE są (jeszcze) przydatne

- Drobnoziarnista teoria muzyki (poniżej poziomu akordów).
- Rozumowanie przypisywane mówcy podczas długich rozmów (pogorsza się w ciągu ostatnich 10 minut).
- Porównanie wielu plików audio (22-26% to wartość nieznacznie powyżej wartości losowej).
- Rozumowanie dotyczące przesyłania strumieniowego w czasie rzeczywistym (większość z nich to wnioskowanie wsadowe w trybie offline).

## Zbuduj to

### Krok 1: zapytanie Qwen2.5-Omni

```python
from transformers import AutoModelForCausalLM, AutoProcessor

processor = AutoProcessor.from_pretrained("Qwen/Qwen2.5-Omni-7B")
model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-Omni-7B", torch_dtype="auto")

audio, sr = load_wav("clip.wav", sr=16000)
messages = [{
    "role": "user",
    "content": [
        {"type": "audio", "audio": audio},
        {"type": "text", "text": "What sounds do you hear, and what's happening?"},
    ],
}]
inputs = processor.apply_chat_template(messages, tokenize=True, return_tensors="pt")
output = model.generate(**inputs, max_new_tokens=200)
print(processor.decode(output[0], skip_special_tokens=True))
```

### Krok 2: wzór projektora

```python
import torch.nn as nn

class AudioProjector(nn.Module):
    def __init__(self, audio_dim=1280, llm_dim=4096):
        super().__init__()
        self.down = nn.Linear(audio_dim, llm_dim)
        self.act = nn.GELU()
        self.up = nn.Linear(llm_dim, llm_dim)

    def forward(self, audio_features):
        return self.up(self.act(self.down(audio_features)))
```

To wszystko. Projektor ma zwykle 1-3 warstwy liniowe. Uczenie go na parach ASR (audio → transkrypcja) jest zadaniem pretekstowym Etapu 1.

### Krok 3: benchmarking MMAU / LongAudioBench

```python
from datasets import load_dataset
mmau = load_dataset("MMAU/MMAU-Pro")

correct = 0
for item in mmau["test"]:
    answer = call_model(item["audio"], item["question"], item["choices"])
    if answer == item["correct_choice"]:
        correct += 1
print(f"Accuracy: {correct / len(mmau['test']):.3f}")
```

Zgłaszaj osobno poszczególne kategorie (mowa / dźwięk / muzyka / multi-audio). Liczby zagregowane ukrywają miejsca, w których model zawodzi.

## Użyj tego

| Zadanie | wybór 2026 |
|------|-----------|
| Kontrola jakości dźwięku w dowolnej formie (otwarta) | Qwen2.5-Omni-7B |
| Najlepiej otwarte na długim dźwięku | Audio Flaming Dalej |
| Najlepiej zamknięte | Gemini 2.5 Pro |
| Agent głosu / głosu | Qwen2.5-Omni lub GPT-4o Audio |
| Rozumowanie muzyczne | Audio Flamingo 3 lub 2 (specjalizacja muzyczna AF-CLAP) |
| Audyt call center | Gemini 2.5 Pro poprzez API, z RAG nad dokumentami polisowymi |

## Pułapki

- **Nadmierne zaufanie do wielu plików audio.** Jeśli Twoje zadanie wymaga „który klip ma X”, wydajność na poziomie losowej szansy jest realna.
- **Długie pogorszenie jakości dźwięku.** W ciągu ostatnich 10 minut w większości modeli następuje przerwa w przypisywaniu głośników. Najpierw wykonaj diaryzację (lekcja 6), a następnie podsumuj.
- **Halucynacje po ciszy.** Ten sam problem w stylu szeptu, dziedziczony przez LALMy używające kodera szeptu. Bramka VAD.
- **Wybieranie benchmarków.** Wpisy na blogach dostawców przedstawiają najlepsze kategorie. Uruchom samodzielnie podzestaw multi-audio MMAU-Pro.

## Wyślij to

Zapisz jako `outputs/skill-alm-picker.md`. Wybierz LALM + podzbiór wzorcowy + modalność wyjściową (tekst vs mowa) dla danego zadania rozumienia dźwięku.

## Ćwiczenia

1. **Łatwo.** Uruchom `code/main.py`, aby zobaczyć wzór projektora zabawkowego + fałszywe routing LALM (osadzanie audio, tokeny tekstowe) → tokeny wyjściowe.
2. **Średni.** Oceń Qwen2.5-Omni-7B w 100 wypowiedziach MMAU-Pro. Porównaj z numerem podanym w gazecie.
3. **Trudne.** Stwórz minimalną bazę napisów dźwiękowych: koder BEATs + projektor 2-warstwowy + zamrożona lama-3.2-1B. Dostosuj tylko projektor w AudioCaps. Porównaj z SALMONN na Clotho-AQA.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| LALM | Czat audioGPT | Koder audio + projektor + dekoder LLM. |
| Projektor | Adapter | Małe funkcje audio MLP mapujące w przestrzeń osadzania LLM. |
| MMAU | Punkt odniesienia | 10 tys. par audio-QA obejmujących mowę, dźwięk i muzykę. |
| MMAU-Pro | Trudniejsze MMAU | 1800 pytań wymagających wielu dźwięków i wymagających rozumowania. |
| LongAudioBench | Ewaluacja w długiej formie | Kilkuminutowe klipy z zapytaniami semantycznymi. |
| Głos wejściowy / głosowy | Natywny dla mowy | Model przyswaja mowę i emituje mowę bez obchodzenia się z tekstem. |

## Dalsze czytanie

- [Chu i in. (2024). Qwen2-Audio](https://arxiv.org/abs/2407.10759) — architektura referencyjna.
- [Alibaba (2025). Qwen2.5-Omni](https://huggingface.co/Qwen/Qwen2.5-Omni-7B) — mowa-w-mowie.
- [NVIDIA (2025). Audio Flamingo 3](https://arxiv.org/abs/2507.08128) — otwarty lider długiego audio.
- [NVIDIA (2026). Audio Flamingo Dalej](https://arxiv.org/abs/2604.10905) — LongAudioBench SOTA.
- [Tang i in. (2023). SALMONN](https://arxiv.org/abs/2310.13289) — pionier podwójnego kodera.
– [Tabela liderów MMAU-Pro](https://mmaubenchmark.github.io/) — rankingi na żywo z 2026 r.