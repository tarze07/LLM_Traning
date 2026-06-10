---

name: bert-finetuner
description: Zakres dostrojenia BERT do nowego zadania klasyfikacji, ekstrakcji lub wyszukiwania.
version: 1.0.0
phase: 7
lesson: 6
tags: [bert, fine-tuning, nlp]

---

Biorąc pod uwagę kolejne zadanie (klasyfikacja / NER / pobieranie / zmiana rankingu / NLI), oznaczony rozmiar danych i ograniczenia wdrażania (opóźnienie, urządzenie), wynik:

1. Wybór szkieletu. Nazwa modelu (ModernBERT-base / Large, DeBERTa-v3, multilingual-e5 itp.) z jednym zdaniem. Preferuj ModernBERT do zadań w języku angielskim wymagających kontekstu ≤8 tys.
2. Specyfikacja głowicy Klasyfikacja: `[CLS]` → rezygnacja → liniowa (num_classes). NER: liniowy na token + opcjonalnie CRF. Odzyskiwanie: pula średnia + strata kontrastowa.
3. Przepis na trening. Optymalizator (AdamW, typowo lr 2e-5), % rozgrzania (6–10%), epoki (3–5), wielkość partii, fp16/bf16.
4. Plan ewaluacyjny. Metryki odpowiednie do zadania (dokładność + F1 do klasyfikacji, F1 na poziomie jednostki dla NER, MRR/NDCG do wyszukiwania). Przetrzymywany rozmiar podziału.
5. Kontrola trybu awaryjnego. Jedno określone ryzyko: wyciek etykiet, brak równowagi klas, obcięcie kontekstu, niedopasowanie tokenizatora między korpusami wstępnego uczenia i dostrajania.

Odmów dostrajania BERT pod kątem wyjścia generatywnego (generowanie tekstu) — zamiast tego zaleć tylko dekoder. Odmów dostarczenia poprawki bez ewaluacji ze względu na klasę, gdy klasa mniejszości jest poniżej 10%. Oflaguj wszelkie poprawki, które odblokowują cały szkielet z <1000 oznaczonymi przykładami, jako prawdopodobne przepełnienie.