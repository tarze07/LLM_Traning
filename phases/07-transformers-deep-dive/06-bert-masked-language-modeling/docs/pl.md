# BERT — Modelowanie języka zamaskowanego

> GPT przewiduje następne słowo. BERT przewiduje brakujące słowo. Jedno zdanie różnicy — i pół dekady wszystkiego, co ma kształt osadzania.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 7 · 05 (pełny transformator), faza 5 · 02 (reprezentacja tekstu)
**Czas:** ~45 minut

## Problem

W 2018 roku każde zadanie NLP — nastroje, NER, kontrola jakości, zaangażowanie — trenowało od podstaw własny model na podstawie własnych oznaczonych danych. Nie było żadnego wytrenowanego punktu kontrolnego „zrozumienia angielskiego”, który można by dostroić. Projekt ELMo (2018) pokazał, że można wstępnie wytrenować osadzanie kontekstowe za pomocą dwukierunkowego LSTM; pomogło, ale nie uogólniało.

BERT (Devlin i in. 2018) zapytał: co by było, gdybyśmy wzięli koder transformatorowy, trenowali go pod kątem każdego zdania w Internecie i zmusili go do przewidywania brakujących słów z kontekstu po obu stronach? Następnie dostrajasz jedną głowę do dalszego zadania. Wydajność parametrów była rewelacją.

Rezultat: w ciągu 18 miesięcy BERT i jego odmiany (RoBERTa, ALBERT, ELECTRA) zdominowały każdą istniejącą tabelę liderów NLP. Do 2020 r. każda wyszukiwarka, kanał moderacji treści i system wyszukiwania semantycznego na świecie będą miały BERT w środku.

W 2026 r. modele wykorzystujące wyłącznie kodery nadal będą właściwym narzędziem do klasyfikacji, wyszukiwania i ekstrakcji strukturalnej — działają 5–10 razy szybciej na token niż dekodery, a ich osadzanie stanowi podstawę każdego nowoczesnego stosu wyszukiwania. ModernBERT (grudzień 2024 r.) przesunął architekturę do kontekstu 8K za pomocą Flash Attention + RoPE + GeGLU.

## Koncepcja

![Modelowanie języka maskowanego: wybieraj tokeny, maskuj je, przewidywaj oryginały](../assets/bert-mlm.svg)

### Sygnał treningowy

Weź zdanie: `the quick brown fox jumps over the lazy dog`.

Zamaskuj losowo 15% żetonów:

```
input:  the [MASK] brown fox jumps [MASK] the lazy dog
target: the  quick brown fox jumps  over  the lazy dog
```

Wytrenuj model, aby przewidywał oryginalne tokeny w zamaskowanych pozycjach. Ponieważ koder jest dwukierunkowy, przewidywanie `[MASK]` na pozycji 1 może użyć `brown fox jumps` na pozycjach 2+. To jest rzecz, której GPT nie może zrobić.

### Maska BERT rządzi

Z 15% tokenów wybranych do przewidywania:

- 80% zostaje zastąpionych przez `[MASK]`.
- 10% zostaje zastąpionych losowym żetonem.
- 10% pozostaje bez zmian.

Dlaczego nie zawsze `[MASK]`? Ponieważ wartość `[MASK]` nigdy nie pojawia się w momencie wnioskowania. Uczenie modelu tak, aby oczekiwał `[MASK]` przy 100% zamaskowanych pozycji, spowodowałoby przesunięcie dystrybucji między uczeniem wstępnym a dostrajaniem. 10% losowe + 10% niezmienne sprawia, że ​​model jest uczciwy.

### Przewidywanie następnego zdania (NSP) — i dlaczego zostało porzucone

Oryginalny BERT również trenował NSP: biorąc pod uwagę dwa zdania A i B, przewiduj, czy B następuje po A. RoBERTa (2019) ablował to i pokazał, że NSP boli, ale nie pomogło. Nowoczesne kodery pomijają to.

### Co zmieniło się w 2026 roku: ModernBERT

Artykuł ModernBERT z 2024 r. przebudował blok z prymitywami 2026:

| Składnik | Oryginalny BERT (2018) | NowoczesnyBERT (2024) |
|----------|----------------------|--------------------------------|
| Pozycyjne | Nauczyłem się absolutu | LINA |
| Aktywacja | ŻELU | GeGLU |
| Normalizacja | Norma warstwy | Wstępna norma RMSNorm |
| Uwaga | Pełna gęstość | Naprzemiennie lokalnie (128) + globalnie |
| Długość kontekstu | 512 | 8192 |
| Tokenizer | Słowo | BPE |

W odróżnieniu od stosu z 2018 r. jest on natywny dla Flash-Attention. Wnioskowanie jest 2–3 razy szybsze przy długości sekwencji 8 tys. niż DeBERTa-v3 z lepszymi wynikami GLUE.

### Przypadki użycia, które nadal wybierają koder w 2026 r

| Zadanie | Dlaczego koder bije dekoder |
|------|--------------------------|
| Pobieranie / osadzanie wyszukiwania semantycznego | Kontekst dwukierunkowy = lepsza jakość osadzania na token |
| Klasyfikacja (nastroje, zamiary, toksyczność) | Jedno podanie do przodu; brak kosztów ogólnych wytwarzania |
| Oznakowanie NER / token | Wyjście na pozycję, natywnie dwukierunkowe |
| Zasada zerowego strzału (NLI) | Głowica klasyfikatora na górze enkodera |
| Zmiana rankingu dla RAG | Punktacja między koderami, 10 razy szybsza niż rerankery LLM |

## Zbuduj to

### Krok 1: logika maskowania

Zobacz `code/main.py`. Funkcja `create_mlm_batch` pobiera listę identyfikatorów tokenów, rozmiar słownika i prawdopodobieństwo maski. Zwraca identyfikatory wejściowe (z zastosowanymi maskami) i etykiety (tylko w pozycjach zamaskowanych, w innych miejscach -100 — konwencja ignorowania indeksu PyTorch).

```python
def create_mlm_batch(tokens, vocab_size, mask_prob=0.15, rng=None):
    input_ids = list(tokens)
    labels = [-100] * len(tokens)
    for i, t in enumerate(tokens):
        if rng.random() < mask_prob:
            labels[i] = t
            r = rng.random()
            if r < 0.8:
                input_ids[i] = MASK_ID
            elif r < 0.9:
                input_ids[i] = rng.randrange(vocab_size)
            # else: keep original
    return input_ids, labels
```

### Krok 2: uruchom prognozę MLM na małym korpusie

Wytrenuj 2-warstwowy koder + głowę MLM na słownictwie składającym się z 20 słów i 200 zdań. Brak gradientu — przeprowadzamy kontrolę poprawności przebiegu w przód. Pełne szkolenie wymaga PyTorch.

### Krok 3: porównaj typy masek

Pokaż, jak reguła trójstronna zapewnia użyteczność modelu bez `[MASK]`. Wytypuj zdanie zdemaskowane i zdanie zamaskowane. Obydwa powinny generować rozsądne rozkłady tokenów, ponieważ model widział oba wzorce podczas szkolenia.

### Krok 4: dostrojenie głowy

Zastąp nagłówek MLM nagłówkiem klasyfikacyjnym w zestawie danych dotyczących nastrojów na zabawki. Tylko główni trenują; koder jest zamrożony. Jest to wzór, według którego podąża każda aplikacja BERT.

## Użyj tego

```python
from transformers import AutoModel, AutoTokenizer

tok = AutoTokenizer.from_pretrained("answerdotai/ModernBERT-base")
model = AutoModel.from_pretrained("answerdotai/ModernBERT-base")

text = "Attention is all you need."
inputs = tok(text, return_tensors="pt")
out = model(**inputs).last_hidden_state   # (1, N, 768)
```

**Modele osadzania są precyzyjnie dostrojone BERT.** `sentence-transformers` modele takie jak `all-MiniLM-L6-v2` to BERT trenowane ze stratą kontrastową. Koder jest ten sam. Strata się zmieniła.

**Urządzenia do zmiany rankingu za pomocą koderów krzyżowych są również dopracowane w BERT.** Klasyfikacja par w `[CLS] query [SEP] doc [SEP]`. Dwukierunkowa uwaga między zapytaniem a dokumentem jest dokładnie tym, co zapewnia cross-enkoderom przewagę jakościową nad biencoderami.

**Kiedy nie wybierać BERT-a w 2026 roku.** Wszystko, co generuje energię. Koder nie ma rozsądnego sposobu na autoregresyjne tworzenie tokenów. Ponadto: wszystko o parametrach poniżej 1B, gdzie mały dekoder może dorównać jakością przy większej elastyczności (Phi-3-Mini, Qwen2-1.5B).

## Wyślij to

Zobacz `outputs/skill-bert-finetuner.md`. Umiejętność obejmuje precyzyjne dostrojenie BERT (wybór szkieletu, specyfikacja głowicy, dane, ocena, zatrzymanie) pod kątem nowego zadania klasyfikacji lub ekstrakcji.

## Ćwiczenia

1. **Łatwe.** Uruchom `code/main.py` i wydrukuj rozkład maski na 10 000 tokenów. Potwierdź, że wybrano ~15%, a z tych ~80% stanie się `[MASK]`.
2. **Średni.** Zastosuj maskowanie całego słowa: jeśli słowo jest podzielone na słowa podrzędne, maskuj wszystkie słowa podrzędne razem lub nie maskuj ich wcale. Zmierz, czy poprawia to dokładność MLM w korpusie składającym się z 500 zdań.
3. **Trudne.** Wytrenuj małego (2-warstwowego, d=64) BERT-a na 10 000 zdań z publicznego zbioru danych. Dostosuj token `[CLS]` dla tokenu SST-2. Porównanie z linią bazową obejmującą wyłącznie dekoder przy dopasowanych parametrach — co wygrywa?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| MLM | „Modelowanie języka zamaskowanego” | Sygnał szkoleniowy: losowo zamień 15% tokenów na `[MASK]`, przewiduj oryginały. |
| Dwukierunkowy | „Wygląda w obie strony” | Uwaga enkodera nie ma maski przyczynowej – każda pozycja widzi każdą inną pozycję. |
| `[CLS]` | „Token puli” | Do każdej sekwencji dołączony jest specjalny token; jego ostateczne osadzenie służy jako reprezentacja na poziomie zdania. |
| `[SEP]` | „Separator segmentów” | Oddziela sparowane sekwencje (np. zapytanie/doc, zdanie A/B). |
| NSP | „Przewidywanie następnego zdania” | Drugie zadanie przedszkoleniowe BERT; okazał się bezużyteczny w RoBERTa, usunięty po 2019 r. |
| Dostrajanie | „Dostosuj się do zadania” | Trzymaj koder w większości zamrożony; wytrenuj małą głowę na górze, aby wykonać dalsze zadanie. |
| Koder krzyżowy | „Reranker” | BERT, który jako dane wejściowe przyjmuje zarówno zapytanie, jak i dokument, generuje wynik trafności. |
| NowoczesnyBERT | „Odświeżenie 2024” | Koder przebudowany z RoPE, RMSNorm, GeGLU, naprzemienna uwaga lokalna/globalna, kontekst 8K. |

## Dalsze czytanie

- [Devlin i in. (2018). BERT: Pre-training of Deep Bilateral Transformers for Language Understanding](https://arxiv.org/abs/1810.04805) — artykuł oryginalny.
- [Liu i in. (2019). RoBERTa: solidnie zoptymalizowane podejście do treningu wstępnego BERT](https://arxiv.org/abs/1907.11692) — jak dobrze wyszkolić BERT; zabija NSP.
- [Clark i in. (2020). ELECTRA: Wstępne szkolenie koderów tekstu jako dyskryminatorów, a nie generatorów](https://arxiv.org/abs/2003.10555) — wykrywanie zastąpionego tokena pokonuje MLM przy dopasowanych obliczeniach.
- [Warner i in. (2024). Inteligentniejszy, lepszy, szybszy, dłuższy: nowoczesny koder dwukierunkowy](https://arxiv.org/abs/2412.13663) — artykuł ModernBERT.
- [HuggingFace `modeling_bert.py`](https://github.com/huggingface/transformers/blob/main/src/transformers/models/bert/modeling_bert.py) — odniesienie do kodera kanonicznego.