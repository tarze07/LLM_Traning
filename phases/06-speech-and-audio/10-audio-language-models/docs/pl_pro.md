# Modele językowo-audio (Large Audio-Language Models) — Qwen2.5-Omni, Audio Flamingo, GPT-4o Audio

> W 2026 roku modele audio-językowe (LALM) realizują zaawansowane zadania rozumowania nad mową, dźwiękami otoczenia oraz muzyką. Model Qwen2.5-Omni-7B dorównuje wydajnością GPT-4o Audio w benchmarku MMAU-Pro, a Audio Flamingo Next pokonuje model Gemini 2.5 Pro w teście LongAudioBench. Różnice między modelami o otwartym (open-source) i zamkniętym kodzie źródłowym (proprietary) niemal całkowicie się zatarły – z wyjątkiem testów na wielu plikach audio równocześnie, w których wyniki wszystkich modeli nadal oscylują wokół losowego wyboru.

**Typ:** Podręcznik  
**Języki:** Python  
**Wymagania wstępne:** Faza 6 · 04 (ASR), Faza 12 · 03 (Modele wizjonersko-językowe), Faza 7 · 10 (Transformatory audio)  
**Czas:** ~45 minut  

## Problem

Masz 5-sekundowe nagranie audio: słychać szczekanie psa, ktoś krzyczy „stop!”, a potem zapada cisza. Aby w pełni przeanalizować to nagranie, system musi odpowiedzieć na pytania z różnych wymiarów:

- **Transkrypcja:** „Co dokładnie zostało powiedziane?” — klasyczne zadanie ASR.
- **Rozumowanie semantyczne:** „Czy ta osoba znajduje się w niebezpieczeństwie?” — wymaga jednoczesnej analizy szczekania, krzyku i kontekstu ciszy.
- **Rozumowanie muzyczne:** „Jakie instrumenty grają w tle?”
- **Wyszukiwanie w długich nagraniach:** „W którym momencie tego 90-minutowego wykładu prelegent wyjaśnił pojęcie spadku gradientu?”

Uniwersalny model, który potrafi odpowiedzieć na wszystkie te pytania w ramach jednej sesji konwersacyjnej, to **model językowo-audio (Large Audio-Language Model - LALM)**. Odróżnia go to od klasycznego ASR – LALM generują odpowiedzi w języku naturalnym o dowolnej strukturze, a nie tylko suchy tekst wypowiedzi.

## Koncepcja

![Architektura modelu językowo-audio: koder audio + projektor + model LLM](../assets/alm-architecture.svg)

### Trójskładnikowa architektura bazowa

Każdy nowoczesny model LALM w 2026 roku korzysta z tego samego schematu:

1. **Koder audio:** Whisper, BEATs, CLAP, WavLM lub autorski enkoder dedykowany dla konkretnej sieci.
2. **Projektor (Moduł dopasowania cech):** Mapuje wyjściowe cechy z kodera audio (zazwyczaj MLP lub warstwa liniowa) na przestrzeń osadzeń tokenów modelu LLM.
3. **Model LLM:** Dekoder oparty na architekturze Llama, Qwen lub Gemma. Przyjmuje przeplatane tokeny tekstowe oraz audio i generuje tekst wyjściowy.

**Etapy uczenia:**
- **Etap 1:** Zamrożenie wag kodera audio oraz LLM. Trenuje się wyłącznie projektor na zadaniu ASR lub dopasowywania napisów (captions) do dźwięku.
- **Etap 2:** Pełny finetuning (lub LoRA) na zadaniach instruktażowych (Audio Instruction Tuning, np. odpowiedzi na pytania, analiza nastroju, rozumienie muzyki).
- **Etap 3 (opcjonalny):** Dodanie dekodera mowy w celu natywnego generowania odpowiedzi głosowych (np. Qwen2.5-Omni, AF3-Chat).

### Zestawienie modeli w 2026 r.

| Model | Model bazowy (LLM) | Koder audio | Format wyjściowy | Licencja / Dostęp |
|-------|---------|--------------|-------|--------|
| Qwen2.5-Omni-7B | Qwen2.5-7B | Whisper + dedykowany | Tekst + mowa | Apache-2.0 |
| Qwen3-Omni | Qwen3 | Dedykowany | Tekst + mowa | Apache-2.0 |
| Audio Flamingo 3 | Qwen2 | AF-CLAP | Tekst | Dedykowana (niekomercyjna) |
| Audio Flamingo Next | Qwen2 | AF-CLAP v2 | Tekst | Dedykowana (niekomercyjna) |
| SALMONN | Vicuna | Whisper + BEATs | Tekst | Apache-2.0 |
| LTU / LTU-AS | Llama | CAV-MAE | Tekst | Apache-2.0 |
| GAMs | Llama | AST + Q-Former | Tekst | Apache-2.0 |
| Gemini 2.5 Flash/Pro | Gemini | Własny | Tekst + mowa | API |
| GPT-4o Audio | GPT-4o | Własny | Tekst + mowa | API |

### Wyniki w benchmarkach (stan na 2026 r.)

**MMAU-Pro.** Zbiór 1800 pytań testowych (wielokrotnego wyboru) sprawdzających rozumienie mowy, ogólnych dźwięków, muzyki oraz analizę wielu nagrań.

| Model | Wynik ogólny | Mowa | Dźwięki | Muzyka | Analiza wielu plików |
|-------|--------|--------|-------|-------|------------|
| Gemini 2.5 Pro | ~60% | 73,4% | 51,9% | 64,9% | ~22% |
| Gemini 2.5 Flash | ~57% | 73,4% | 50,5% | 64,9% | 21,2% |
| GPT-4o Audio | 52,5% | — | — | — | 26,5% |
| Qwen2.5-Omni-7B | 52,2% | 57,4% | 47,6% | 61,5% | ~20% |
| Audio Flamingo 3 | ~54% | — | — | — | — |

Wyniki w kolumnie poświęconej analizie wielu plików audio są bezlitosne dla wszystkich modeli. Przy 4 opcjach wyboru losowa szansa na trafną odpowiedź wynosi 25% – i wokół tej wartości oscylują wyniki większości z nich. Modele LALM wciąż mają ogromne trudności z porównywaniem i zestawianiem ze sobą dwóch różnych nagrań.

### Zastosowania komercyjne modeli LALM

- **Audyt i analiza nagrań call center:** Automatyczna weryfikacja, czy konsultant wypowiedział wymagane klauzule i zachował odpowiedni ton wypowiedzi.
- **Ułatwienia dostępu (accessibility):** Szczegółowe opisywanie otaczających zdarzeń dźwiękowych dla osób słabosłyszących i niesłyszących.
- **Moderacja treści:** Wykrywanie agresji, gróźb w głosie oraz nieodpowiednich odgłosów w tle na nagraniach wideo.
- **Generowanie konspektów i podsumowań spotkań:** Semantyczna analiza wypowiedzi z podziałem na wątki tematyczne.
- **Wyszukiwanie i kategoryzacja zasobów muzycznych:** Klasyfikacja utworów na podstawie cech harmonicznych i zmian tonacji.

### Obszary, w których modele te wciąż zawodzą

- Precyzyjna teoria muzyki (analiza struktur i transkrypcja nutowa).
- Identyfikacja i przypisywanie wypowiedzi mówców (speaker attribution) w bardzo długich dyskusjach (jakość spada po 10 minutach nagrania).
- Równoległe porównywanie wielu nagrań audio.
- Wnioskowanie strumieniowe o skrajnie niskim opóźnieniu (większość LALM to modele wsadowe przetwarzające audio offline).

## Implementacja krok po kroku

### Krok 1: Wnioskowanie z użyciem modelu Qwen2.5-Omni

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

### Krok 2: Implementacja projektora (pseudokod)

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

To kompletna implementacja projektora – zazwyczaj składa się on z 1–3 warstw liniowych z funkcją aktywacji. Trening tego modułu na parach ASR (audio → transkrypcja) stanowi zadanie pretekstowe (pretext task) podczas Etapu 1 uczenia modelu.

### Krok 3: Ewaluacja na zbiorze MMAU / LongAudioBench

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

Analizuj wyniki dla każdej kategorii osobno (mowa / dźwięk / muzyka / wiele nagrań). Zagregowane statystyki często maskują obszary słabości modelu.

## Sugerowane rozwiązania (2026)

| Zadanie | Rekomendowany model (2026) |
|---|---|
| Analiza ogólnych zdarzeń dźwiękowych (open-source) | Qwen2.5-Omni-7B |
| Analiza długich nagrań (open-source) | Audio Flamingo Next |
| Analiza długich nagrań (systemy komercyjne) | Gemini 2.5 Pro (API) |
| Systemy konwersacyjne (Speech-to-Speech) | Qwen2.5-Omni lub GPT-4o Audio |
| Analiza i klasyfikacja muzyki | Audio Flamingo 3 |
| Audyt i analiza nagrań call center | Gemini 2.5 Pro z bazą wiedzy RAG |

## Typowe pułapki

- **Błędne założenie o sprawności w zadaniach multi-audio.** Modele bardzo słabo radzą sobie z porównywaniem cech między dwoma klipami audio; unikaj opierania systemów produkcyjnych na takich funkcjach.
- **Analiza długich rozmów bez uprzedniej diaryzacji.** Modele LALM gubią kontekst przypisania wypowiedzi w nagraniach powyżej 10 minut. Wykonaj najpierw diaryzację (Speaker Diarization), a dopiero potem generuj podsumowania.
- **Halucynacje na cichych fragmentach.** Jeśli model LALM wykorzystuje enkoder Whisper, odziedziczy po nim problem halucynowania w ciszy. Przed uruchomieniem analizatora zawsze filtruj nagrania bramką VAD.
- **Analiza wyłącznie uśrednionych metryk.** Materiały marketingowe dostawców zazwyczaj prezentują wyniki z wybranych, najkorzystniejszych kategorii. Zawsze przeprowadź niezależne testy na trudniejszych podzbiorach, np. analizie wielu plików z MMAU-Pro.

## Zadanie do wykonania

Zapisz jako `outputs/skill-alm-picker.md`. Dobierz odpowiedni model LALM, zestaw testowy (benchmark) oraz format wyjściowy (tekst vs. mowa) dla zadanego zadania analizy audio.

## Ćwiczenia

1. **Łatwe.** Uruchom skrypt `code/main.py`, aby przeanalizować uproszczoną implementację projektora i symulację przepływu danych (wektory audio + tokeny tekstowe) przez model LALM.
2. **Średnie.** Przeprowadź ewaluację modelu Qwen2.5-Omni-7B na 100 przykładach ze zbioru MMAU-Pro. Porównaj wyniki z deklaracjami w oficjalnej publikacji naukowej.
3. **Trudne.** Zbuduj uproszczony potok napisów dźwiękowych: koder BEATs + 2-warstwowy projektor + zamrożony model Llama-3.2-1B. Dostrój wyłącznie projektor na zbiorze AudioCaps. Porównaj wyniki z modelem SALMONN na zbiorze Clotho-AQA.

## Kluczowe terminy

| Termin | Potoczne określenie | Co to naprawdę oznacza |
|------|-----------------|----------------------|
| LALM / ALM | Model audio-LLM | Sieć łącząca enkoder audio, projektor mapujący cechy oraz dekoder LLM w celu semantycznej analizy dźwięków. |
| Projector | Adapter cech audio | Warstwy MLP dopasowujące wymiarowość wyjścia kodera audio do wymiarowości tokenów wejściowych modelu LLM. |
| MMAU | Zbiór testowy MMAU | Wielozadaniowy benchmark zawierający ponad 10 tysięcy par pytań i odpowiedzi dotyczących mowy, muzyki i dźwięków. |
| MMAU-Pro | Trudny podzbiór MMAU | Zbiór 1800 pytań wymagających logicznego rozumowania nad kilkoma nagraniami audio jednocześnie. |
| LongAudioBench | Benchmark długiego audio | Zbiór testowy weryfikujący umiejętność wyszukiwania i analizy informacji w nagraniach o długości kilkunastu/kilkudziesięciu minut. |
| Speech-to-Speech | Potok natywny mowa-mowa | Architektura, w której model przyjmuje bezpośrednio sygnał mowy i generuje mowę wyjściową bez konieczności pośredniej transkrypcji na tekst. |

## Dalsze czytanie

- [Chu et al. (2024). Qwen2-Audio: Large Audio-Language Models with Unified Pre-training and Instruction Tuning](https://arxiv.org/abs/2407.10759) — fundament pod architekturę Qwen Audio.
- [Alibaba (2025). Qwen2.5-Omni Technical Report](https://huggingface.co/Qwen/Qwen2.5-Omni-7B) — specyfikacja modelu Speech-to-Speech od Alibaby.
- [NVIDIA (2025). Audio Flamingo 3: Understanding Long Audio and Music](https://arxiv.org/abs/2507.08128) — dokumentacja modelu Audio Flamingo w zadaniach długodystansowych.
- [Tang et al. (2023). SALMONN: Towards Generic Hearing Abilities for Large Language Models](https://arxiv.org/abs/2310.13289) — pionierska publikacja opisująca wykorzystanie podwójnego kodera audio.
- [MMAU Benchmark Official Website](https://mmaubenchmark.github.io/) — strona projektu z tabelą wyników i najnowszymi modelami.
