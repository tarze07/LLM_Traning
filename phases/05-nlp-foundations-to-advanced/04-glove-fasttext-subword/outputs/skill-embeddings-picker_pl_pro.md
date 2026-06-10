---
name: skill-embeddings-picker
description: Wybierz podejście tokenizacyjne dla nowego modelu języka lub potoku tekstowego.
version: 1.0.0
phase: 5
lesson: 04
tags: [nlp, tokenization, embeddings]
---

Na podstawie opisu zadania i zbioru danych określ:

1. Rekomendowaną strategię tokenizacji (poziom słów, BPE, WordPiece, SentencePiece lub poziom bajtów) wraz z jednozdaniowym uzasadnieniem.
2. Docelowy rozmiar słownika (np. 32 tys. dla modeli jednojęzycznych angielskich, 64 tys. - 100 tys. dla modeli wielojęzycznych, 50 tys. - 100 tys. dla kodu źródłowego).
3. Konkretne wywołanie biblioteki wraz z parametrami treningowymi (np. Hugging Face `tokenizers` lub `sentencepiece`).
4. Zidentyfikowanie jednej kluczowej pułapki wdrożeniowej (np. cichy błąd niedopasowania tokenizatora do modelu, wskazując, które elementy muszą bezwzględnie współpracować, i ostrzegając przed ich podmianą).

Odmów polecania trenowania nowego tokenizatora w przypadku dostrajania (fine-tuning) istniejących modeli LLM (dostrajanie musi bezwzględnie korzystać z wbudowanego tokenizera). Odmów polecania tokenizacji na poziomie słów dla modeli wdrażanych produkcyjnie. Wyraźnie zaznacz, że teksty wielojęzyczne lub korzystające z wielu alfabetów (skryptów) wymagają SentencePiece z obsługą bajtów jako fallback.
