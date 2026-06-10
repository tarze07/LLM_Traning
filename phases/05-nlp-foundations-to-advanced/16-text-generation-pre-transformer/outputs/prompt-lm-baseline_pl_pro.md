---
name: lm-baseline
description: Zbuduj powtarzalny n-gramowy model bazowy języka przed rozpoczęciem uczenia neuronowego modelu językowego.
phase: 5
lesson: 16
---

Na podstawie korpusu i docelowego zastosowania (przewidywanie kolejnego słowa, ponowne ocenianie/rescoring, wyznaczenie bazowej perpleksji) określ:

1. Rząd n-gramów: Model trygramowy dla ogólnych tekstów, 4-gramowy przy dużym korpusie, 5-gramowy do rescoringu w systemach ASR (rozpoznawania mowy).
2. Metoda wygładzania: Domyślnie zmodyfikowany Kneser-Ney; wygładzanie Laplace'a wyłącznie w celach dydaktycznych.
3. Biblioteka: `kenlm` do zastosowań produkcyjnych, `nltk.lm` do dydaktyki, własna implementacja (roll-your-own) wyłącznie w celu lepszego zrozumienia matematycznych podstaw.
4. Ewaluacja: Obliczanie perpleksji na wydzielonym zbiorze testowym przy zachowaniu spójnej tokenizacji dla zbioru treningowego i testowego.

Nigdy nie porównuj wartości perpleksji obliczonych przy użyciu różnych tokenizatorów — porównania mają sens wyłącznie przy identycznej tokenizacji. Zawsze podawaj odsetek słów spoza słownika (OOV – Out-Of-Vocabulary) w zbiorze testowym. Modele z wygładzaniem KN radzą sobie z OOV słabo, chyba że podczas uczenia zarezerwujesz specjalny token `<UNK>`.
