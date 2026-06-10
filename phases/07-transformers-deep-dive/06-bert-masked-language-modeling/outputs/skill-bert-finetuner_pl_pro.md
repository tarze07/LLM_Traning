---

name: bert-finetuner
description: Zaprojektuj proces dostrajania (fine-tuning) modeli typu BERT dla zadań klasyfikacji, ekstrakcji informacji lub wyszukiwania.
version: 1.0.0
phase: 7
lesson: 6
tags: [bert, fine-tuning, nlp]

---

Na podstawie opisu zadania docelowego (klasyfikacja / NER / wyszukiwanie / reranking / NLI), rozmiaru etykietowanego zbioru danych oraz ograniczeń wdrożeniowych (opóźnienie, docelowy sprzęt) wygeneruj:

1. Wybór modelu bazowego (backbone): nazwa modelu (np. ModernBERT-base / Large, DeBERTa-v3, multilingual-e5) wraz z jednozdaniowym uzasadnieniem. Rekomenduj ModernBERT dla zadań w języku angielskim z kontekstem ≤8K.
2. Specyfikacja głowicy zadaniowej: dla klasyfikacji: reprezentacja tokenu `[CLS]` → dropout → warstwa liniowa (`num_classes`). Dla NER: warstwa liniowa klasyfikująca poszczególne tokeny + opcjonalnie warstwa CRF. Dla wyszukiwania: uśrednianie (mean pooling) + funkcja straty kontrastowej (contrastive loss).
3. Parametry treningu: optymalizator (np. AdamW, typowa wartość lr to 2e-5), odsetek kroków rozgrzewki (warmup) (6–10%), liczba epok (3–5), rozmiar batcha, precyzja obliczeniowa (FP16/BF16).
4. Plan ewaluacji: metryki adekwatne do zadania (dokładność i F1 dla klasyfikacji, F1 na poziomie encji dla NER, MRR/NDCG dla wyszukiwania). Rozmiar wydzielonego zbioru testowego (holdout split).
5. Analiza ryzyka błędów: jedno zidentyfikowane ryzyko (np. wyciek danych/label leakage, niezbalansowanie klas, ucinanie kontekstu, niedopasowanie tokenizatora między etapem pre-trainingu a fine-tuningu).

Odmawiaj dostrajania modeli typu BERT (encoder-only) do zadań generowania tekstu – w takich przypadkach zalecaj modele typu decoder-only. Odmawiaj dostarczenia rekomendacji bez analizy metryk dla poszczególnych klas (class-wise evaluation), gdy klasa mniejszościowa stanowi mniej niż 10% zbioru. Oznaczaj jako ryzyko przeuczenia (overfitting) każdą próbę dostrajania całego modelu (odblokowane wszystkie wagi) przy zbiorze treningowym mniejszym niż 1000 etykietowanych przykładów.
