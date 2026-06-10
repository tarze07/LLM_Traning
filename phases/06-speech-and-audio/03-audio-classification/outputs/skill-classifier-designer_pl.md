---

name: classifier-designer
description: Wybierz architekturę, rozszerzenie, strategię równowagi klas i metrykę oceny dla zadania klasyfikacji dźwięku.
version: 1.0.0
phase: 6
lesson: 03
tags: [audio, classification, beats, ast]

---

Biorąc pod uwagę zadanie klasyfikacji audio (domena, liczba etykiet, gęstość etykiet na klip, ilość danych, cel wdrożenia), wynik:

1. Architektura. k-NN-MFCC / 2D CNN / AST / BEATs / Koder szeptów. Powód w jednym zdaniu.
2. Ulepszenia. Parametry SpecAugment (maska ​​czasowa, liczba masek częstotliwości), miksowanie α, poziom miksowania szumów tła.
3. Równowaga klas. Zrównoważony próbnik vs strata ogniskowa vs wagi klas. Przypnij do proporcji ogona do głowy.
4. Strata + metryka. CE / p.n.e. / ogniskowa; metryka podstawowa (top-1 / mAP / makro-F1) i wtórna.
5. Split + plan ewaluacyjny. Stratyfikowane k-krotnie, rozłączne głośniki w przypadku mowy, podział czasowy w przypadku przesyłania strumieniowego danych.

Odrzuć wszelkie zadania wymagające wielu etykiet, które uzyskały tylko najwyższą dokładność; wymagają mapy. Odmów oceny zadania uwarunkowanego mówcą bez podziału na rozłączne głośniki. Oznacz dowolną architekturę od podstaw w klipach z etykietami <10 tys. — zacznij od wstępnie wytrenowanego szkieletu SSL.