---
name: tokenizer-picker
description: Wybierz algorytm tokenizacji, rozmiar słownika oraz bibliotekę dla podanego korpusu i celu wdrożenia.
version: 1.0.0
phase: 5
lesson: 19
tags: [nlp, tokenization]
---

Na podstawie charakterystyki korpusu (rozmiar, języki, domena) oraz celu wdrożenia (trening od zera, dostrajanie, zgodność z zewnętrznym API) wygeneruj:

1. Algorytm: BPE, Unigram lub WordPiece (wraz z jednozdaniowym uzasadnieniem).
2. Biblioteka: SentencePiece, Hugging Face Tokenizers lub tiktoken (wraz z uzasadnieniem).
3. Rozmiar słownika: Zaokrąglony do najbliższego tysiąca (powiązany z rozmiarem modelu i zakresem obsługiwanych języków).
4. Konfiguracja pokrycia: Wartości parametrów `character_coverage`, `byte_fallback` oraz lista tokenów specjalnych.
5. Plan walidacji: Średnia liczba tokenów na słowo na wydzielonym zbiorze testowym, wskaźnik OOV, współczynnik kompresji oraz test poprawności rekonstrukcji tekstu (round-trip decode equality).

Nigdy nie trenuj tokenizatora z parametrem `character_coverage` <0.995 na korpusach zawierających rzadkie alfabety/znaki. Bezwzględnie wymagaj weryfikacji sumy kontrolnej pliku `tokenizer.json` w potokach CI. Oznaczaj każdy słownik jednojęzyczny o rozmiarze poniżej 16k jako zbyt ubogi.
