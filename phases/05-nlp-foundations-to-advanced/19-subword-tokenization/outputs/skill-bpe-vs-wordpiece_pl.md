---

name: skill-bpe-vs-wordpiece
description: Wybierz algorytm tokenizera, rozmiar słownika, bibliotekę dla danego korpusu i cel wdrożenia.
version: 1.0.0
phase: 5
lesson: 19
tags: [nlp, tokenization]

---

Biorąc pod uwagę korpus (rozmiar, języki, domena) i cel wdrożenia (szkolenie od podstaw / dostrajanie / wnioskowanie zgodne z API), wynik:

1. Algorytm. BPE, Unigram lub WordPiece. Powód w jednym zdaniu.
2. Biblioteka. SentencePiece, Tokenizery HF lub tiktoken. Powód.
3. Rozmiar słownictwa. Zaokrąglone do najbliższego 1 tys. Powód związany z rozmiarem modelu i zasięgiem językowym.
4. Ustawienia zasięgu. `character_coverage`, `byte_fallback`, lista tokenów specjalnych.
5. Plan walidacji. Średnia liczba tokenów na słowo w zestawie wstrzymanym, współczynnik OOV, współczynnik kompresji, równość dekodowania w obie strony.

Odmów trenowania tokenizera o zasięgu <0,995 w korpusach z zawartością rzadkiego skryptu. Odmów wysłania słownika bez zamrożonego sprawdzania skrótu `tokenizer.json` w CI. Oznacz dowolny jednojęzyczny tokenizer poniżej 16 tys. słownictwa jako prawdopodobnie niezgodny ze specyfikacją.