---

name: vision-rag-designer
description: Zaprojektuj dokument RAG z wizją, używając ColPali / ColQwen2 / VisRAG, z oszacowaniem pamięci i wyborem generatora.
version: 1.0.0
phase: 12
lesson: 23
tags: [colpali, colqwen2, visrag, late-interaction, vidore]

---

Biorąc pod uwagę projekt dokumentu RAG (rozmiar korpusu, docelowe opóźnienie zapytania, budżet magazynu, koszt zapytania), wyemituj natywną konfigurację RAG dla wizji.

Wyprodukuj:

1. Wybór retrievera. ColPali (baza PaliGemma), ColQwen2 (baza Qwen2-VL, lepsza jakość), ColSmol (1B dla krawędzi) lub VisRAG (bi-enkoder, tańsza pamięć masowa).
2. Szacunek przechowywania. N_docs * N_p_per_doc * D * 4 bajty surowe; podziel przez 8, aby uzyskać PQ.
3. Oszacowanie opóźnienia.
   - SLA pobierania: osadzanie zapytania ~ 10 ms + pobieranie z góry (MaxSim lub ANN), zależne od rozmiaru indeksu.
   - Umowa SLA z pełną odpowiedzią: opóźnienie pobierania + generator 200–500 ms (w zależności od modelu i sprzętu).
4. Wybór generatora. Qwen2.5-VL-72B dla otwartego, Claude Opus 4.7 dla granicy.
5. Plan kompresji. Docelowy stosunek PQ/OPQ 8-16x; Indeks HNSW dla szybkiej SSN.
6. Ścieżka migracji z tekstu-RAG. Jak A/B, kiedy całkowicie przejść na inne.

Twarde odrzucenia:
- Używanie ColPali bez kompresji PQ w korpusach > 10 tys. stron. Magazyn eksploduje.
- Zgłaszanie żądania pobrania dwuenkodera odpowiada ColBERT MaxSim w przypadku wycofania dokumentu. Nie dotyczy to ViDoRe.
- Polecanie tekstu-RAG dla obciążeń związanych z wykresami i tabelami. Text-RAG traci większość sygnału.

Zasady odmowy:
- Jeśli korpus składa się z czystego tekstu (wiki, logi czatów), odrzuć RAG natywny dla wizji i zaleć standardowy RAG tekstowy.
- Jeśli pobierzesz strony SLA <100ms, prefer VisRAG (bi-encoder) over ColPali MaxSim.
- If full-answer SLA <100ms, refuse generative RAG entirely and recommend retrieval-only UX or cached answers.
- If storage budget is <1 GB and corpus is >100k, odmów pełnej wierności ColPali; zaproponuj agresywny PQ lub VisRAG.

Dane wyjściowe: jednostronicowy projekt RAG z wyborem modułu pobierającego, szacunkową pamięcią, opóźnieniem, generatorem, kompresją i migracją. Zakończ arXiv 2407.01449 (ColPali), 2410.10594 (VisRAG).