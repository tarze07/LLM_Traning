---
name: nli-picker
description: Wybierz model NLI, szablon hipotezy oraz strukturę ewaluacji dla zadania klasyfikacji, weryfikacji spójności lub klasyfikacji zero-shot.
version: 1.0.0
phase: 5
lesson: 21
tags: [nlp, nli, zero-shot]
---

Na podstawie scenariusza użycia (weryfikacja ugruntowania/faithfulness, klasyfikacja zero-shot, wnioskowanie na poziomie dokumentu) wygeneruj:

1. Model: Dokładna nazwa punktu kontrolnego (checkpoint) modelu NLI wraz z uzasadnieniem (dziedzina, długość kontekstu, język).
2. Szablon (dla zero-shot): Konstrukcja szablonu hipotezy wraz z przykładem.
3. Próg odcięcia (Threshold): Wartość progowa prawdopodobieństwa implikacji dla reguły decyzyjnej wraz z uzasadnieniem (kalibracja).
4. Plan ewaluacji: Dokładność (accuracy) na wydzielonym zbiorze testowym, wynik bazowy dla samej hipotezy (hypothesis-only baseline) oraz wyniki na wrogim podzbiorze testowym.

Nigdy nie wdrażaj klasyfikacji zero-shot bez wcześniejszego testu poprawności (sanity check) na przynajmniej 100 oznaczonych przykładach. Nigdy nie stosuj modeli NLI trenowanych na zdaniach do analizy dokumentów o znacznej długości. Wyraźnie zaznaczaj, że NLI nie eliminuje całkowicie problemu halucynacji – pozwala go jedynie istotnie ograniczyć.
