---

name: eval-architect
description: Zaprojektuj plan oceny LLM ze skalibrowanym sędzią i bramkami CI.
version: 1.0.0
phase: 5
lesson: 27
tags: [nlp, evaluation, rag]

---

Biorąc pod uwagę przypadek użycia (RAG / agent / zadanie generatywne), wynik:

1. Metryki. Wierność / trafność / precyzja kontekstu / przypomnienie kontekstu + dowolne niestandardowe wskaźniki G-Eval z kryteriami.
2. Model sędziego. Nazwany model + wersja, uzasadnienie kosztów w porównaniu z dokładnością.
3. Kalibracja. Ręcznie oznaczony rozmiar zestawu, docelowy Włócznik rho vs człowiek > 0,7.
4. Wersjonowanie zbioru danych. Strategia tagowania, dziennik zmian, stratyfikacja.
5. Brama CI. Progi na metrykę, logika okna regresji, alert dolnego kwantyla.

Odmawiaj polegania na nieprzetestowanym sędzią na podstawie ≥50 przykładów opatrzonych etykietą człowieka. Odmawiaj samooceny (ten sam model generuje + ocenia). Odrzuć raportowanie wyłącznie zagregowane, bez ujawniania dolnych 10%. Oznacz dowolny potok, w którym ocena sędziowska kończy się bez równoległej oceny linii bazowej.