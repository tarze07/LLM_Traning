---
name: multilingual-picker
description: Wybierz język źródłowy, model bazowy oraz plan ewaluacji dla wielojęzycznego zadania NLP.
version: 1.0.0
phase: 5
lesson: 18
tags: [nlp, multilingual, cross-lingual]
---

Na podstawie wymagań (języki docelowe, typ zadania, dostępne oznaczone dane dla każdego języka) wygeneruj:

1. Język źródłowy do dostrojenia: Domyślnie angielski; sprawdź LANGRANK lub qWALS, jeśli język docelowy posiada bliskiego typologicznie krewniaka o bogatych zasobach.
2. Model bazowy: XLM-R (klasyfikacja), mT5 (generowanie), NLLB (tłumaczenie), Aya-23 (generatywny model LLM).
3. Budżet few-shot: Użyj 100–500 przykładów z języka docelowego, jeśli są dostępne. Podejście zero-shot stosuj wyłącznie, gdy etykietowanie jest niewykonalne.
4. Plan ewaluacji: Dokładność dla każdego języka osobno (unikaj metryk zagregowanych), spójność międzyjęzykowa, miara F1 dla nazw własnych w pismach niełacińskich.

Nigdy nie wdrażaj modelu wielojęzycznego bez przeprowadzenia ewaluacji dla każdego języka osobno – metryki zagregowane maskują błędy w mniej popularnych językach (z długiego ogona). Oznaczaj języki o słabym pokryciu tokenizatora (np. amharski, tigrinia, wiele języków afrykańskich) jako wymagające tokenizatora z obsługą bajtów awaryjnych (SentencePiece z `byte_fallback=True` lub tokenizacji na poziomie bajtów, jak w GPT-2).
