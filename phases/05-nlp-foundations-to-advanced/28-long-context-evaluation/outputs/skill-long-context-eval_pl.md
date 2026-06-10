---

name: long-context-eval
description: Zaprojektuj baterię ewaluacyjną o długim kontekście dla danego modelu i przypadku użycia.
version: 1.0.0
phase: 5
lesson: 28
tags: [nlp, long-context, evaluation]

---

Biorąc pod uwagę model docelowy, długość kontekstu docelowego i przypadek użycia, wynik:

1. Testy. Siatka głębokości × długości NIAH; RULER multi-hop; niestandardowe zadanie domeny.
2. Próbkowanie. Głębokości 0, 0,25, 0,5, 0,75, 1,0 na każdej długości.
3. Metryki. Wskaźnik przepustowości pobierania; wskaźnik zdawalności rozumowania; czas do pierwszego tokena; koszt zapytania.
4. Odcięcie. Efektywna długość wyszukiwania (90% sukcesu) i efektywna długość rozumowania (70% sukcesu). Zgłoś oba.
5. Regresja. Naprawiono uprząż, uruchamiano ponownie przy każdej aktualizacji modelu, delty powierzchni.

Odmawiaj zaufania do okna kontekstowego z samej karty modelu. Odrzuć ocenę wyłącznie przez NIAH dla dowolnego obciążenia z wieloma przeskokami. Odrzuć samodzielnie zgłaszane przez dostawcę wyniki w długim kontekście jako niezależny dowód.