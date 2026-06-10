---

name: prompt-tokenizer-builder
description: Twórz i debuguj tokenizatory o jakości produkcyjnej dla projektów LLM
version: 1.0.0
phase: 10
lesson: 2
tags: [tokenizer, bpe, byte-level, special-tokens, chat-template, multilingual]

---

# Konstruktor tokenizatorów produkcyjnych

Podczas tworzenia lub debugowania tokenizera dla projektu LLM postępuj zgodnie z tą strukturą.

## Lista kontrolna potoku tokenizacji (pipeline)

Każdy produkcyjny tokenizer musi przejść przez poniższe pięć etapów. Pominięcie któregokolwiek z nich doprowadzi do błędów w przypadkach skrajnych (edge cases) na produkcji.

1. **Normalizacja**: Zastosowanie normalizacji Unicode (np. NFKC). Pozwala to na scalenie ligatur (np. „fi” -> „fi”), standaryzację znaków o pełnej szerokości i ujednolicenie białych znaków. Pominięcie tego kroku sprawi, że to samo słowo otrzyma różne identyfikatory (IDs) w zależności od sposobu zapisu.

2. **Wstępna tokenizacja (pre-tokenization)**: Podział tekstu na mniejsze fragmenty przed właściwym procesem BPE. Użyj wzorca wyrażenia regularnego z GPT-2 dla modeli zorientowanych na język angielski, lub podejścia opartego na surowych bajtach (SentencePiece) dla modeli wielojęzycznych. Ten krok decyduje o tym, czy tokeny BPE będą mogły łączyć się ponad granicami słów.

3. **Scalanie BPE (BPE merges)**: Zastosowanie wyuczonej tabeli łączenia do sekwencji bajtów w każdym fragmencie. Tabela scaleń stanowi właściwą wiedzę tokenizatora. Cała reszta to jedynie techniczna infrastruktura (plumbing).

4. **Wstrykiwanie tokenów specjalnych**: Przypisanie tokenów specjalnych bezpośrednio przed uruchomieniem BPE. Tokeny takie jak [BOS], [EOS], [PAD] czy znaczniki szablonu czatu otrzymują stałe identyfikatory (IDs) i nigdy nie biorą udziału w procesie scalania (merging).

5. **Mapowanie identyfikatorów (ID mapping)**: Konwersja ciągów tokenów na liczby całkowite (integers), ponieważ model operuje wyłącznie na liczbach.

## Rozwiązywanie problemów (debugging)

**Objaw: model generuje niezrozumiały tekst (garbage) podczas interakcji na czacie**
- Sprawdź szablon czatu (chat template). Każdy model korzysta z innego formatu. Llama 3 używa znaczników `<|start_header_id|>`, z kolei ChatGPT (ChatML) korzysta z `<|im_start|>`. Błędny szablon sprawia, że dane wejściowe trafiają poza rozkład danych treningowych (out-of-distribution).

**Objaw: teksty w językach innych niż angielski zużywają zbyt dużo tokenów**
- Sprawdź współczynnik fragmentacji (fertility – liczba tokenów na słowo). Wartość powyżej 2,0 oznacza marnowanie okna kontekstowego dla danego języka. Rozwiązania: ponowne wytrenowanie tokenizatora z większym udziałem danych wielojęzycznych, zwiększenie rozmiaru słownika lub użycie SentencePiece z algorytmem Unigram.

**Objaw: model popełnia proste błędy w obliczeniach i arytmetyce**
- Sprawdź sposób tokenizacji liczb. Jeśli „1234” jest traktowane jako pojedynczy token, model nie ma możliwości wykonywania operacji na poziomie poszczególnych cyfr. Należy rozdzielać cyfry na poziomie wstępnej tokenizacji.

**Objaw: tokenizacja kodu źródłowego jest nieefektywna**
- Sprawdź obsługę wcięć (indentation). Tokenizer GPT-2 zużywa osobny token na każdą spację wcięcia. Modele takie jak Codex czy StarCoder stosują dedykowane tokeny dla wcięć (np. 4 spacje = 1 token).

## Decyzje o rozmiarze słownika (vocabulary size)

- 32 tys. tokenów: model jednojęzyczny, mniejsze architektury, ograniczone zasoby obliczeniowe. Rozmiar warstwy osadzeń wynosi 32K * d_model.
- 50K-64K: model wielojęzyczny lub trenowany na dużych ilościach kodu. Optymalny kompromis dla większości zastosowań.
- Ponad 100 tys. tokenów (np. GPT-4, Llama 3): uzasadnione tylko przy ogromnych zbiorach treningowych. Skraca długość sekwencji, ale zwiększa parametry warstwy osadzeń do 100K * d_model.

Dla modelu o wymiarowości 4096: słownik 32 tys. = 131 mln parametrów warstwy osadzeń; słownik 128 tys. = 524 mln parametrów warstwy osadzeń. Oznacza to dodatkowe ~400 mln parametrów w samej warstwie osadzeń.

## Wymagania dotyczące wydajności (szybkości)

- Tokenizacja danych treningowych: korzystaj z bibliotek z backendem w języku Rust (`tiktoken`, `tokenizers` od Hugging Face). Czysty Python jest 10-100 razy wolniejszy.
- Tokenizacja przy wnioskowaniu (inference): opóźnienie (latency) pojedynczej sekwencji jest kluczowe, dlatego zaleca się korzystanie ze skompilowanych implementacji.
- Test wydajnościowy (benchmark): przeprowadź tokenizację 1 GB tekstu i zmierz rzeczywisty czas wykonania (wall-clock time). Jeśli proces trwa dłużej niż 60 sekund, przejdź na backend w Rust.

## Walidacja szablonu czatu (chat template)

Przed wdrożeniem modelu zoptymalizowanego pod kątem konwersacji zweryfikuj szablon czatu:

1. Zakoduj przykładową rozmowę za pomocą tokenizatora.
2. Zdekoduj uzyskane identyfikatory z powrotem na tekst.
3. Porównaj wynik znak po znaku z oczekiwanym formatem opisanym w dokumentacji modelu.
4. Zwróć szczególną uwagę na: znaki nowej linii po tokenach nagłówkowych, spacje przed treścią wiadomości oraz znaczniki końca tury (end-of-turn tokens).
5. Przetestuj przypadki skrajne (edge cases): pusta wiadomość systemowa (system message), bardzo długi prompt użytkownika, czy następujące po sobie bezpośrednio wypowiedzi asystenta.

Błędna konfiguracja szablonu czatu to najczęstszą przyczyna drastycznego spadku jakości generowanych odpowiedzi w modelach konwersacyjnych.
