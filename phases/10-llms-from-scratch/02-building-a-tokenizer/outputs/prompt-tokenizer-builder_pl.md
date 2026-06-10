---

name: prompt-tokenizer-builder
description: Twórz i debuguj tokenizatory o jakości produkcyjnej dla projektów LLM
version: 1.0.0
phase: 10
lesson: 2
tags: [tokenizer, bpe, byte-level, special-tokens, chat-template, multilingual]

---

# Konstruktor tokenizatora produkcyjnego

Podczas tworzenia lub debugowania tokenizera dla projektu LLM postępuj zgodnie z tą strukturą.

## Lista kontrolna rurociągu

Każdy tokenizator produkcyjny potrzebuje tych pięciu etapów. Jeśli któregoś brakuje, trafisz na przypadki Edge w produkcji.

1. **Normalizuj** — zastosuj normalizację NFKC Unicode. Spowoduje to zwinięcie ligatur („fi” -> „fi”), normalizację znaków o pełnej szerokości i standaryzację białych znaków. Pomiń to, a to samo słowo otrzyma różne identyfikatory tokenów w zależności od sposobu jego wpisania.

2. **Przed tokenizacją** – Podziel tekst na fragmenty przed BPE. Użyj wzorca wyrażenia regularnego GPT-2 dla modeli skoncentrowanych na języku angielskim. Użyj podejścia opartego na surowych bajtach SentencePiece w przypadku modeli wielojęzycznych. Wybór określa, czy BPE może łączyć się ponad granicami słów.

3. **Scalanie BPE** — Zastosuj wyuczoną tabelę łączenia do sekwencji bajtów w każdym fragmencie. Tabela scalania JEST wiedzą wyuczoną tokenizatora. Cała reszta to hydraulika.

4. **Specjalny zastrzyk tokena** — Dopasuj specjalne tokeny dokładnie przed uruchomieniem BPE. [BOS], [EOS], [PAD], znaczniki szablonów czatu otrzymują stałe identyfikatory. Nigdy nie uczestniczą w fuzjach.

5. **Mapowanie ID** — Konwertuj ciągi tokenów na liczby całkowite. Model widzi tylko liczby całkowite.

## Debugowanie problemów z tokenizerem

**Objaw: model generuje śmieci podczas wprowadzania danych na czacie**
- Sprawdź szablon czatu. Każdy model ma inny format. Lama 3 wykorzystuje znaczniki `<|start_header_id|>`. ChatGPT wykorzystuje znaczniki `<|im_start|>`. Zły szablon powoduje umieszczenie danych wejściowych poza dystrybucją szkoleniową.

**Objaw: tekst w języku innym niż angielski zawiera zbyt wiele tokenów**
- Sprawdź płodność (żetony na słowo). Powyżej 2.0 oznacza, że ​​tokenizer marnuje okno kontekstowe w tym języku. Rozwiązania: przekwalifikuj się z większą liczbą wielojęzycznych danych, zwiększ rozmiar słownictwa lub użyj SentencePiece z Unigramem.

**Objaw: niepowodzenie liczb i arytmetyki**
- Sprawdź, jak cyfry są tokenizowane. „1234” jako jeden token oznacza, że ​​model nie może wykonywać operacji na poziomie cyfr. Podziel cyfry indywidualnie podczas wstępnej tokenizacji.

**Objaw: tokeny kodu są nieefektywne**
- Sprawdź, jak obsługiwane jest wcięcie. Tokenizer GPT-2 marnuje tokeny na spacje. Codex i StarCoder używają specjalnych żetonów wcięć (4 spacje = 1 żeton).

## Decyzja dotycząca rozmiaru słownictwa

- 32 tys. tokenów: jednojęzyczny, mały model, ograniczona moc obliczeniowa. Warstwa osadzająca ma parametry 32K * d_model.
- 50K-64K: wielojęzyczny lub z dużą ilością kodu. Dobra równowaga dla większości projektów.
- 100 tys.+ (GPT-4, Lama 3): tylko z ogromnymi danymi treningowymi. Krótsze sekwencje, ale parametry osadzania 100K * d_model.

Dla modelu 4096-wymiarowego: 32 tys. słów = 131 mln parametrów osadzania. 128 tys. słów = 524 mln parametrów osadzania. Oznacza to 400M parametrów w samej warstwie osadzającej.

## Wymagania dotyczące prędkości

- Tokenizacja danych treningowych: użyj bibliotek opartych na Rust (tiktoken, tokenizery HuggingFace). Czysty Python jest 10-100 razy wolniejszy.
- Tokenizacja wnioskowania: opóźnienie ma mniejsze znaczenie (pojedyncza sekwencja), ale nadal korzystaj z skompilowanych implementacji.
- Test porównawczy: tokenizuj 1 GB tekstu i mierz czas na zegarze ściennym. Jeśli zajmie to więcej niż 60 sekund, przełącz się na backend Rusta.

## Walidacja szablonu czatu

Przed wdrożeniem dowolnego modelu czatu sprawdź szablon:

1. Zakoduj znaną rozmowę z tokenizerem
2. Odszyfruj to z powrotem na tekst
3. Porównaj znak po znaku z oczekiwanym formatem z dokumentacji modelu
4. Zwróć uwagę na: znaki nowej linii po żetonach nagłówka, spacje przed treścią, znaczniki końca tury
5. Przypadki testowe Edge: pusty komunikat systemowy, bardzo długi komunikat użytkownika, wielokrotne tury asystentów

Błędne ustawienie szablonu czatu jest najczęstszą przyczyną obniżonej wydajności modelu czatu.