---

name: multilingual-picker
description: Wybierz język źródłowy, model docelowy i plan ewaluacji dla wielojęzycznego zadania NLP.
version: 1.0.0
phase: 5
lesson: 18
tags: [nlp, multilingual, cross-lingual]

---

Biorąc pod uwagę wymagania (języki docelowe, typ zadania, dostępne dane oznaczone etykietami dla każdego języka), wynik:

1. Język źródłowy do dostrojenia. Domyślny angielski; sprawdź LANGRANK lub qWALS, jeśli język docelowy ma typologicznie zbliżony język o dużych zasobach.
2. Model podstawowy. XLM-R (klasyfikacja), mT5 (generacja), NLLB (tłumaczenie), Aya-23 (generatywne LLM).
3. Niewielki budżet. Zacznij od 100–500 przykładów w języku docelowym, jeśli są dostępne. Zero-shot tylko wtedy, gdy etykietowanie jest niewykonalne.
4. Plan ewaluacji. Dokładność w poszczególnych językach (nie zagregowana), spójność międzyjęzykowa, F1 na poziomie jednostki w pismach innych niż łacińskie.

Odmów dostarczenia modelu wielojęzycznego bez oceny poszczególnych języków – zagregowane metryki ukrywają błędy związane z długim ogonem. Oznacz skrypty o niskim pokryciu tokenizacją (amharski, tigrinia, wiele języków afrykańskich) jako wymagające modelu z rezerwą bajtową (SentencePiece z byte_fallback=True lub tokenizator na poziomie bajtów, taki jak GPT-2).