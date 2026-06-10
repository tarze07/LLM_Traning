---

name: skill-tokenizer
description: Wybór i budowanie tokenizerów dla projektów LLM
version: 1.0.0
phase: 10
lesson: 1
tags: [tokenizer, bpe, wordpiece, sentencepiece, llm, nlp]

---

# Wybór i wdrożenie tokenizera

Rozpoczynając projekt LLM, kieruj się poniższym schematem decyzyjnym przy wyborze tokenizatora.

## Kiedy używać każdego tokenizatora

**BPE na poziomie bajtów (byte-level BPE, np. tiktoken):** Budujesz lub dostrajasz modele z rodziny GPT. Potrzebujesz gwarantowanej obsługi dowolnej wejściowej sekwencji bajtów i chcesz uniknąć nieznanych tokenów (out-of-vocabulary).

**WordPiece (Hugging Face):** Pracujesz z modelami z rodziny BERT do celów klasyfikacji, NER (rozpoznawanie jednostek nazwanych) lub osadzania (embeddings). Potrzebujesz prefiksu kontynuacji „##” dla zadań downstream, które opierają się na sygnałach granic słów.

**SentencePiece (BPE lub Unigram):** Trenujesz model od zera. Potrzebujesz tokenizacji niezależnej od języka. Twoje dane obejmują języki CJK, tajski i inne pisma niewykorzystujące spacji/białych znaków do rozdzielania wyrazów. Rozwiązanie to jest stosowane w LLaMA, T5 i większości modeli wielojęzycznych.

## Wytyczne dotyczące rozmiaru słownika (vocabulary size)

- 32 tys. tokenów: dobra wartość domyślna dla modeli jednojęzycznych, pozwala zachować niewielki rozmiar warstwy osadzeń (embeddings)
- 50–64 tys. tokenów: lepsze dla modeli wielojęzycznych lub trenowanych na dużych ilościach kodu
- Ponad 100 tys. tokenów: zalecane tylko przy ogromnych zbiorach danych treningowych i chęci skrócenia długości sekwencji

Większy słownik przekłada się na krótsze sekwencje (tańsze wnioskowanie), ale wymaga więcej parametrów w macierzy osadzeń. Przykładowo, dla słownika o rozmiarze 100 tys. tokenów i wymiarowości osadzeń (embedding dimension) równej 4096, sama warstwa osadzeń zawiera 400 mln parametrów.

## Istotne reguły wstępnej tokenizacji (pre-tokenization)

1. Dziel białe znaki przed zastosowaniem BPE, aby zapobiec łączeniu tokenów na granicach słów.
2. Rozdzielaj cyfry (traktuj każdą cyfrę jako osobny znak), jeśli chcesz, aby model dobrze radził sobie z arytmetyką.
3. Stosuj normalizację Unicode (NFC) przed tokenizacją, aby zapewnić spójność przetwarzania danych.
4. Add specjalne tokeny dostosowane do Twojego przypadku użycia: `<pad>`, `<eos>`, `<bos>`, `<unk>` oraz inne znaczniki specyficzne dla zadań.

## Sygnały ostrzegawcze w działaniu tokenizatora

- Współczynnik fragmentacji (fertility) powyżej 2,0 dla języka docelowego: model marnuje okno kontekstowe.
- Częste słowa specyficzne dla domeny dzielone na 3 lub więcej tokenów: konieczne ponowne wytrenowanie tokenizatora na danych domenowych.
- Niespójna tokenizacja liczb: zweryfikuj reguły podziału cyfr.
- Duży słownik z wieloma rzadko używanymi (unikalnymi) tokenami: zmniejsz rozmiar słownika.

## Tworzenie własnego tokenizatora – lista kontrolna

1. Zbierz reprezentatywne dane treningowe (co najmniej 1 GB tekstu z domeny docelowej).
2. Wybierz algorytm: BPE do ogólnych zastosowań, Unigram dla projektów wielojęzycznych.
3. Dobierz rozmiar słownika na podstawie wcześniejszych wytycznych.
4. Skonfiguruj wstępną tokenizację: dzielenie białych znaków, obsługa cyfr, interpunkcji.
5. Dodaj tokeny specjalne.
6. Przeprowadź trening z użyciem biblioteki `tokenizers` od Hugging Face (szybki backend napisany w języku Rust).
7. Walidacja: sprawdź jakość tokenizacji na wydzielonym tekście testowym (held-out) we wszystkich językach docelowych.
8. Przetestuj przypadki skrajne (edge cases): pusty ciąg znaków, bardzo długie teksty, dane binarne, emoji, tekst pisany od prawej do lewej (RTL).
9. Zapisz i wersjonuj tokenizer wraz z checkpointami modelu.
