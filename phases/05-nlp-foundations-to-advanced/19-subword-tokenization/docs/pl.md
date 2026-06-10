# Tokenizacja podsłów — BPE, WordPiece, Unigram, SentencePiece

> Tokenizatory słów dławią się niewidzialnymi słowami. Tokenizatory znaków zwiększają długość sekwencji. Tokenizatory podsłów dzielą różnicę. Każdy nowoczesny LLM jest dostarczany na jednym.

**Typ:** Ucz się
**Języki:** Python
**Wymagania wstępne:** Faza 5 · 01 (Przetwarzanie tekstu), Faza 5 · 04 (GloVe / FastText / Subword)
**Czas:** ~60 minut

## Problem

Twoje słownictwo liczy 50 000 słów. Użytkownik wpisuje „untokenizable”. Twój tokenizer zwraca `[UNK]`. Modelka nie ma teraz sygnału dotyczącego tego słowa. Co gorsza: dokument na 90. percentylu w Twoim korpusie zawiera 40 rzadkich słów, co oznacza 40 bitów pominiętych informacji na dokument.

Tokenizacja podsłów rozwiązuje ten problem. Powszechnie używane słowa pozostają pojedynczymi tokenami. Rzadkie słowa rozkładają się na znaczące fragmenty: `untokenizable` → `un`, `token`, `izable`. Dane szkoleniowe obejmują wszystko, ponieważ każdy ciąg znaków jest ostatecznie sekwencją bajtów.

Każdy frontier LLM w 2026 roku będzie dostarczany w oparciu o jeden z trzech algorytmów (BPE, Unigram, WordPiece) zapakowany w jedną z trzech bibliotek (tiktoken, SentencePiece, HF Tokenizers). Nie można wysłać modelu językowego bez jego wybrania.

## Koncepcja

![BPE vs Unigram vs WordPiece, znak po znaku](../assets/subword-tokenization.svg)

**BPE (kodowanie par bajtów).** Zacznij od słownictwa na poziomie znakowym. Policz każdą sąsiadującą parę. Połącz najczęstszą parę w nowy token. Powtarzaj, aż osiągniesz docelowy rozmiar słownictwa. Dominujący algorytm: GPT-2/3/4, Lama, Gemma, Qwen2, Mistral.

**BPE na poziomie bajtów.** Ten sam algorytm, ale z wykorzystaniem surowych bajtów (256 tokenów podstawowych) zamiast znaków Unicode. Gwarantuje zero tokenów `[UNK]` — dowolną sekwencję bajtów. GPT-2 wykorzystuje 50 257 tokenów (256 bajtów + 50 000 połączeń + 1 specjalny).

**Unigram.** Zacznij od ogromnego słownictwa. Przypisz każdemu żetonowi prawdopodobieństwo unigramu. Iteracyjnie przycinaj tokeny, których usunięcie najmniej zwiększa prawdopodobieństwo logu korpusowego. Probabilistyczne przy wnioskowaniu: może próbkować tokenizacje (przydatne do powiększania danych poprzez regularyzację podsłów). Używany przez T5, mBART, ALBERT, XLNet, Gemma.

**WordPiece.** Łącz pary, które maksymalizują prawdopodobieństwo korpusu szkoleniowego, a nie surową częstotliwość. Używany przez BERT, DistilBERT, ELECTRA.

**SentencePiece vs tiktoken.** SentencePiece to biblioteka, która *trenuje* słowniki (BPE lub Unigram) bezpośrednio na surowym tekście Unicode, kodując białe znaki jako `▁`. tiktoken to szybki *koder* OpenAI obsługujący gotowe słowniki; to nie trenuje.

Ogólna zasada:

- **Szkolenie nowego słownictwa:** SentencePiece (wielojęzyczny, bez wstępnej tokenizacji) lub Tokenizatory HF.
- **Szybkie wnioskowanie względem słownika GPT:** tiktoken (cl100k_base, o200k_base).
- **Obydwa:** Tokenizatory HF — jedna biblioteka, szkolenie + obsługa.

## Zbuduj to

### Krok 1: BPE od podstaw

Zobacz `code/main.py`. Pętla:

```python
def train_bpe(corpus, num_merges):
    vocab = {tuple(word) + ("</w>",): count for word, count in corpus.items()}
    merges = []
    for _ in range(num_merges):
        pairs = Counter()
        for symbols, freq in vocab.items():
            for a, b in zip(symbols, symbols[1:]):
                pairs[(a, b)] += freq
        if not pairs:
            break
        best = pairs.most_common(1)[0][0]
        merges.append(best)
        vocab = apply_merge(vocab, best)
    return merges
```

Trzy fakty, które algorytm koduje. `</w>` oznacza koniec słowa, więc „niski” (przyrostek) i „niższy” (przedrostek) pozostają odrębne. Ważenie częstotliwości sprawia, że ​​pary o wysokiej częstotliwości wygrywają wcześnie. Lista scalania jest uporządkowana — wnioskowanie stosuje scalanie w kolejności szkoleniowej.

### Krok 2: zakoduj za pomocą wyuczonych łączeń

```python
def encode_bpe(word, merges):
    symbols = list(word) + ["</w>"]
    for a, b in merges:
        i = 0
        while i < len(symbols) - 1:
            if symbols[i] == a and symbols[i + 1] == b:
                symbols = symbols[:i] + [a + b] + symbols[i + 2:]
            else:
                i += 1
    return symbols
```

Naiwny O(n·|scala|). Implementacje produkcyjne (tiktoken, HF Tokenizery) wykorzystują wyszukiwanie rang scalających z kolejkami priorytetowymi i działają w czasie niemal liniowym.

### Krok 3: Fragment zdania w praktyce

```python
import sentencepiece as spm

spm.SentencePieceTrainer.train(
    input="corpus.txt",
    model_prefix="my_tokenizer",
    vocab_size=8000,
    model_type="bpe",          # or "unigram"
    character_coverage=0.9995, # lower for CJK (e.g. 0.9995 for English, 0.995 for Japanese)
    normalization_rule_name="nmt_nfkc",
)

sp = spm.SentencePieceProcessor(model_file="my_tokenizer.model")
print(sp.encode("untokenizable", out_type=str))
# ['▁un', 'token', 'izable']
```

Uwaga: nie jest wymagana wstępna tokenizacja, spacja zakodowana jako `▁`, `character_coverage` kontroluje, jak agresywnie rzadkie znaki są zachowywane w porównaniu z mapowaniem do `<unk>`.

### Krok 4: tiktoken dla słowników kompatybilnych z OpenAI

```python
import tiktoken
enc = tiktoken.get_encoding("o200k_base")
print(enc.encode("untokenizable"))        # [127340, 101028]
print(len(enc.encode("Hello, world!")))   # 4
```

Tylko kodowanie. Szybki (backend rdzy). Dokładne dopasowanie z tokenizacją GPT-4/5 do liczenia bajtów, szacowania kosztów i budżetowania w oknie kontekstowym.

## Pułapki, które nadal będą widoczne w 2026 r

- **Drift tokenizera.** Szkolenie ze słownictwa A, wdrażanie przeciwko słownictwu B. Identyfikatory tokenów różnią się; model wyrzuca śmieci. Sprawdź skrót `tokenizer.json` w CI.
- **Niejednoznaczność białych znaków.** BPE „cześć” i „witaj” dają różne tokeny. Zawsze wyraźnie określaj wartości `add_special_tokens` i `add_prefix_space`.
- **Niedouczenie wielojęzyczne.** Korpusy zawierające dużo języka angielskiego tworzą słowniki, które dzielą pisma inne niż łacińskie na 5–10 razy więcej tokenów. Ten sam monit kosztuje 5–10 razy więcej w języku japońskim/arabskim w przypadku GPT-3.5. o200k_base częściowo to naprawiło.
- **Emoji dzieli się.** Pojedynczy emoji może pomieścić 5 tokenów. Obsługa emoji punktu kontrolnego w kontekście budżetowania.

## Użyj tego

Stos na rok 2026:

| Sytuacja | Wybierz |
|----------|------|
| Szkolenie modelu jednojęzycznego od podstaw | Tokenizatory HF (BPE) |
| Szkolenie modelu wielojęzycznego | Fragment zdania (Unigram, `character_coverage=0.9995`) |
| Udostępnianie interfejsu API zgodnego z OpenAI | tiktoken (`o200k_base` dla GPT-4+) |
| Słownictwo specyficzne dla domeny (kod, matematyka, białko) | Trenuj niestandardowe BPE w korpusie domeny, połącz z podstawowym słownictwem |
| Wnioskowanie o krawędziach, mały model | Unigram (mniejsze słowniki działają lepiej) |

Rozmiar słownictwa jest decyzją skalowania, a nie stałą. Zgrubna heurystyka: 32 tys. dla parametrów <1B, 50-100 tys. dla 1-10B, 200 tys.+ dla wielojęzyczności/granicznej.

## Wyślij to

Zapisz jako `outputs/skill-bpe-vs-wordpiece.md`:

```markdown
---
name: tokenizer-picker
description: Pick tokenizer algorithm, vocab size, library for a given corpus and deployment target.
version: 1.0.0
phase: 5
lesson: 19
tags: [nlp, tokenization]
---

Given a corpus (size, languages, domain) and deployment target (training from scratch / fine-tuning / API-compatible inference), output:

1. Algorithm. BPE, Unigram, or WordPiece. One-sentence reason.
2. Library. SentencePiece, HF Tokenizers, or tiktoken. Reason.
3. Vocab size. Rounded to nearest 1k. Reason tied to model size and language coverage.
4. Coverage settings. `character_coverage`, `byte_fallback`, special-token list.
5. Validation plan. Average tokens-per-word on held-out set, OOV rate, compression ratio, round-trip decode equality.

Refuse to train a character-coverage <0.995 tokenizer on corpora with rare-script content. Refuse to ship a vocab without a frozen `tokenizer.json` hash check in CI. Flag any monolingual tokenizer under 16k vocab as likely under-spec.
```

## Ćwiczenia

1. **Łatwo.** Wytrenuj BPE o liczbie 500 połączeń w maleńkim korpusie `code/main.py`. Zakoduj trzy zatrzymane słowa. Ilu z nich wyprodukowało dokładnie 1 token w porównaniu z > 1 tokenem?
2. **Średni.** Porównaj liczbę tokenów w 100 angielskich zdaniach z Wikipedii pomiędzy `cl100k_base`, `o200k_base` i SentencePiece BPE, którego szkolisz za pomocą vocab=32k. Podaj współczynnik kompresji każdego z nich.
3. **Trudne.** Trenuj ten sam korpus za pomocą BPE, Unigram i WordPiece. Zmierz dokładność w dalszej części procesu, używając każdego z nich w małym klasyfikatorze tonacji. Czy wybór przesuwa igłę o więcej niż 1 punkt F1?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| BPE | Kodowanie par bajtów | Chciwe łączenie najczęściej występujących par znaków, aż do osiągnięcia docelowego rozmiaru słownictwa. |
| BPE na poziomie bajtu | Żadnych nieznanych tokenów nigdy | BPE na surowych 256 bajtach; Użyj tego GPT-2/Lama. |
| Unigram | Tokenizator probabilistyczny | Przycina z dużego zestawu kandydatów przy użyciu logarytmu wiarygodności; używany przez T5, Gemmę. |
| Fragment zdania | Biała spacja | Biblioteka trenująca BPE/Unigram na surowym tekście; spacja zakodowana jako `▁`. |
| tiktoken | Ten szybki | Koder BPE OpenAI wspierany przez Rust dla gotowych słowników. Brak szkoleń. |
| Połącz listę | Magiczne liczby | Uporządkowana lista fuzji `(a, b) → ab`; wnioskowanie ma zastosowanie w kolejności. |
| Pokrycie postaci | Jak rzadkie jest zbyt rzadkie? | Część znaków w korpusie szkoleniowym, którą musi objąć tokenizator; ~0,9995 typowo. |

## Dalsze czytanie

- [Sennrich, Haddow, Brzoza (2015). Neural Machine Translation of Rare Words with Subword Units](https://arxiv.org/abs/1508.07909) – artykuł BPE.
- [Pochwała (2018). Regularyzacja podsłów za pomocą modelu języka Unigram](https://arxiv.org/abs/1804.10959) — artykuł Unigram.
- [Pochwała, Richardson (2018). SentencePiece: prosty i niezależny od języka tokenizator podsłów](https://arxiv.org/abs/1808.06226) — biblioteka.
- [Hugging Face — podsumowanie tokenizatorów](https://huggingface.co/docs/transformers/tokenizer_summary) — zwięzłe odniesienie.
- [Repozytorium tiktoken OpenAI](https://github.com/openai/tiktoken) — książka kucharska + lista kodowania.