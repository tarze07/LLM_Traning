---

name: eval-architect
description: Zaprojektuj plan ewaluacji LLM ze skalibrowanym modelem sędziowskim (LLM-as-a-judge) i bramkami CI/CD.
version: 1.0.0
phase: 5
lesson: 27
tags: [nlp, evaluation, rag]

---

Na podstawie przypadku użycia (RAG / agent / zadanie generatywne) wygeneruj:

1. Metryki: wierność (faithfulness) / trafność odpowiedzi (answer relevance) / precyzja kontekstu (context precision) / czułość kontekstu (context recall) + opcjonalne niestandardowe metryki G-Eval wraz z kryteriami ich oceny.
2. Model sędziowski (LLM-as-a-judge): nazwa modelu i jego wersja oraz uzasadnienie wyboru pod kątem relacji kosztów do dokładności.
3. Kalibracja: rozmiar ręcznie etykietowanego zbioru testowego, docelowa wartość współczynnika korelacji Spearmana (Spearman's rho) w porównaniu do ocen ludzkich (docelowo > 0,7).
4. Wersjonowanie zbioru danych: strategia tagowania wersji, rejestr zmian (changelog) oraz stratyfikacja danych.
5. Bramka CI/CD: progi akceptacji dla poszczególnych metryk, logika wykrywania regresji oraz reguły alertów dla najgorszych wyników (dolny kwantyl).

Odmawiaj polegania na ocenach modelu sędziowskiego (LLM-as-a-judge) bez uprzedniej walidacji na zbiorze co najmniej 50 przykładów ocenionych przez człowieka. Odmawiaj stosowania samooceny (tzn. sytuacji, gdy ten sam model generuje odpowiedź i ją ocenia). Odrzuć raportowanie oparte wyłącznie na wynikach zagregowanych (np. średnich), bez szczegółowego przedstawienia najgorszych 10% przypadków (dolny decyl). Oznacz każdy potok ewaluacji sędziowskiej, który uruchamia się bez równoległego porównania z wynikami linii bazowej (baseline).
