---
name: coref-picker
description: Wybierz metodę rozstrzygania koreferencji, zaprojektuj plan ewaluacji oraz strategię integracji.
version: 1.0.0
phase: 5
lesson: 24
tags: [nlp, coref, information-extraction]
---

Na podstawie scenariusza użycia (pojedynczy/wielokrotny dokument, dziedzina, język) wygeneruj:

1. Podejście: Regułowe, neuronowe (span-based), oparte na modelach LLM lub hybrydowe wraz z jednozdaniowym uzasadnieniem.
2. Model: Dokładna nazwa punktu kontrolnego (checkpoint) w przypadku modeli neuronowych.
3. Integracja: Kolejność operacji potoku (np. tokenizacja → NER → koreferencja → zadanie docelowe).
4. Plan ewaluacji: Wskaźnik CoNLL F1 (średnia z metryk MUC, B³ oraz CEAF-φ4) na wydzielonym zbiorze testowym oraz ręczny audyt klastrów dla przynajmniej 20 dokumentów.

Nigdy nie akceptuj rozwiązań opartych wyłącznie na LLM dla dokumentów dłuższych niż 2000 tokenów bez zastosowania okna przesuwnego z późniejszym scalaniem. Zawsze odrzucaj potoki przetwarzania, które nie generują raportu precyzji i pełności (precision/recall) na poziomie pojedynczych wzmianek. Oznaczaj jako ryzykowne systemy oparte na prostych regułach płci/rodzaju wdrażane dla zróżnicowanych demograficznie tekstów.
