---

name: coref-picker
description: Wybierz podejście korelacyjne, plan ewaluacji i strategię integracji.
version: 1.0.0
phase: 5
lesson: 24
tags: [nlp, coref, information-extraction]

---

Biorąc pod uwagę przypadek użycia (pojedynczy dokument/wiele dokumentów, domena, język), wynik:

1. Podejście. Oparte na regułach / oparte na rozpiętości neuronowej / podpowiadane przez LLM / hybrydowe. Powód w jednym zdaniu.
2. Modelka. Nazwany punkt kontrolny, jeśli jest neuronowy.
3. Integracja. Kolejność operacji: tokenize → NER → coref → zadanie downstream.
4. Ocena. CoNLL F1 (MUC + B³ + średnia CEAF-φ4) na zestawie zatrzymanym + ręczny przegląd skupień na 20 dokumentach.

Odrzuć rdzeń tylko LLM dla dokumentów zawierających ponad 2000 tokenów bez scalania w przesuwanym oknie. Odrzuć jakikolwiek potok obsługujący coref bez raportu o precyzji przypominania na poziomie wzmianki. Flagowe systemy heurystyki płci stosowane w tekście zróżnicowanym demograficznie.