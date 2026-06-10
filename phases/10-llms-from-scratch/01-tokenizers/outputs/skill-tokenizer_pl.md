---

name: skill-tokenizer
description: Wybór i budowanie tokenizerów dla projektów LLM
version: 1.0.0
phase: 10
lesson: 1
tags: [tokenizer, bpe, wordpiece, sentencepiece, llm, nlp]

---

# Wybór i wdrożenie tokenizera

Rozpoczynając projekt LLM, zastosuj te ramy decyzyjne przy wyborze tokenizatora.

## Kiedy używać każdego tokenizatora

**BPE na poziomie bajtów (tiktoken):** Budujesz lub dostrajasz modele z rodziny GPT. Potrzebujesz gwarantowanej obsługi dowolnej sekwencji bajtów wejściowych. Nie chcesz żadnych nieznanych tokenów.

**WordPiece (przytulająca twarz):** Pracujesz z modelami z rodziny BERT do celów klasyfikacji, NER lub osadzania. Potrzebujesz przedrostka kontynuacji „##” dla dalszych zadań, które opierają się na sygnałach granicznych słów.

**SentencePiece (BPE lub Unigram):** Trenujesz od zera. Potrzebujesz tokenizacji niezależnej od języka. Twoje dane obejmują języki CJK, tajski i inne skrypty bez białych znaków. Korzystają z tego LLaMA, T5 i większość modeli wielojęzycznych.

## Wytyczne dotyczące rozmiaru słownictwa

- 32 tys. tokenów: dobre ustawienie domyślne dla modeli jednojęzycznych, utrzymuje małą warstwę osadzającą
- Tokeny 50–64 tys.: lepsze w przypadku modeli wielojęzycznych lub z dużą ilością kodu
- Ponad 100 000 tokenów: tylko wtedy, gdy masz ogromne dane treningowe i chcesz krótkich sekwencji

Większe słownictwo oznacza krótsze sekwencje (tańsze wnioskowanie), ale więcej parametrów w macierzy osadzania. W przypadku słownictwa o wielkości 100 tys. z osadzeniem 4096 wymiarów sama warstwa osadzająca ma 400 mln parametrów.

## Zasady poprzedzające tokenizację, które mają znaczenie

1. Podziel białe znaki przed BPE, aby zapobiec łączeniu krzyżówek
2. Oddziel cyfry indywidualnie, jeśli chcesz, aby model uczył się arytmetyki
3. Normalizuj Unicode (NFC) przed tokenizacją, aby uzyskać spójne zachowanie
4. Dodaj specjalne tokeny dla swojego przypadku użycia: `<pad>`, `<eos>`, `<bos>`, `<unk>` i dowolne znaczniki specyficzne dla zadania

## Sygnały ostrzegawcze w zachowaniu tokenizatora

- Płodność powyżej 2,0 dla Twojego języka docelowego: model marnuje okno kontekstowe
- Wspólne słowa domeny podzielone na 3+ tokeny: ponowne szkolenie z danymi domeny
- Niespójna tokenizacja liczb: sprawdź zasady dzielenia cyfr
- Duże słownictwo z wieloma jednorazowymi tokenami: zmniejsz rozmiar słownictwa

## Tworzenie niestandardowego tokenizera – lista kontrolna

1. Zbierz reprezentatywne dane szkoleniowe (co najmniej 1 GB tekstu w domenie docelowej)
2. Wybierz algorytm: BPE do użytku ogólnego, Unigram do użytku wielojęzycznego
3. Ustaw rozmiar słownictwa w oparciu o powyższe wytyczne
4. Skonfiguruj wstępną tokenizację: dzielenie białych znaków, obsługa cyfr, interpunkcja
5. Dodaj specjalne żetony
6. Trenuj przy użyciu biblioteki tokenizerów Hugging Face (backend Rust, szybki)
7. Sprawdź: sprawdź poprawność zatrzymanego tekstu we wszystkich językach docelowych
8. Testuj przypadki Edge: pusty ciąg znaków, bardzo długie dane wejściowe, dane binarne, emoji, tekst RTL
9. Zapisz i wersjonuj tokenizer wraz z modelowymi punktami kontrolnymi