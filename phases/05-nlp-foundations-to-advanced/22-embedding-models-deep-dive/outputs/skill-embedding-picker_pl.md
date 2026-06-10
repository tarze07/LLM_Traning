---

name: embedding-picker
description: Wybierz model osadzania, wymiar i tryb pobierania dla danego korpusu i wdrożenia.
version: 1.0.0
phase: 5
lesson: 22
tags: [nlp, embeddings, retrieval]

---

Biorąc pod uwagę korpus (rozmiar, języki, domena, średnia długość), cel wdrożenia (chmura / brzeg / lokalnie), budżet opóźnień i budżet miejsca na dane, wynik:

1. Modelka. Nazwany punkt kontrolny lub interfejs API. Powód w jednym zdaniu.
2. Wymiar. Pełne/obcięte Matryoshką/kwantyzowane int8. Powód związany z budżetem na przechowywanie.
3. Tryb. Gęsty / rzadki / wielowektorowy / hybrydowy. Powód.
4. Zapytanie o prefiks/szablon zapytania, jeśli wymaga tego karta modelu.
5. Plan ewaluacji. Zadania MTEB dotyczące domeny + ocena wstrzymanej domeny za pomocą nDCG@10.

Odrzuć zalecenia, które obcinają Matrioszkę do tokenów <64 dims without domain validation. Refuse ColBERTv2 for corpora under 10k passages (overhead not justified). Flag long-document corpora (>8k) kierowane do modeli z oknami 512-tokenowymi.