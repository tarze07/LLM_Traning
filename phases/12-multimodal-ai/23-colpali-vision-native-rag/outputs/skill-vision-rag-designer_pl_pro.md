---

name: vision-rag-designer
description: Projektuje potoki Vision-Native RAG na bazie ColPali / ColQwen2 / VisRAG z uwzględnieniem szacowania pamięci i doboru generatora.
version: 1.0.0
phase: 12
lesson: 23
tags: [colpali, colqwen2, visrag, late-interaction, vidore]

---

Na podstawie specyfikacji projektu Vision RAG (rozmiar bazy dokumentów, docelowe opóźnienie wyszukiwania, budżet pamięciowy, koszty zapytań), wygeneruj natywną konfigurację RAG dla wizji.

Wygeneruj:

1. **Wybór modułu wyszukującego (retriever):** ColPali (baza PaliGemma), ColQwen2 (baza Qwen2-VL, najwyższa jakość), ColSmol (wersja 1B na urządzenia lokalne/krawędziowe) lub VisRAG (podejście dwukoderowe, niższy koszt pamięci bazy).
2. **Szacowanie pamięci:** Wyliczenie typu: `N_docs * N_p_per_doc * D * 4 bajty` dla danych surowych; podziel przez 8–16 dla kompresji PQ.
3. **Szacowanie opóźnień (Latency):**
   - SLA wyszukiwania: generowanie wektora zapytania ~10 ms + wyszukiwanie (MaxSim lub indeks ANN) zależne od rozmiaru bazy.
   - SLA pełnej odpowiedzi (E2E): opóźnienie wyszukiwania + czas generowania 200–500 ms (zależnie od modelu i sprzętu).
4. **Wybór modelu generatywnego (VLM):** Qwen2.5-VL-72B dla modeli otwartych, Claude 4.7 dla wiodących rozwiązań komercyjnych.
5. **Plan kompresji wektorowej:** Docelowa redukcja za pomocą PQ/OPQ o 8–16x; zastosowanie indeksu HNSW dla szybkiego wyszukiwania najbliższych sąsiadów (ANN).
6. **Ścieżka migracji z tekstowego RAG:** Strategia testów A/B oraz kryteria pełnego przejścia na nowy stos.

Kryteria odrzucenia (Twarde reguły):
- Stosowanie modelu ColPali bez kompresji PQ przy bazie dokumentów >10 tys. stron. Powoduje to zbyt szybki wzrost kosztów pamięci masowej.
- Zakładanie, że wyszukiwanie dwukoderowe (bi-encoders) oferuje taką samą skuteczność (Recall) na dokumentach graficznych jak operacja MaxSim w ColBERT. Wyniki benchmarku ViDoRe temu przeczą.
- Rekomendowanie tradycyjnego tekstowego RAG dla dokumentów obfitujących w wykresy, diagramy i tabele. Tekstowy RAG traci w tych przypadkach większość istotnych informacji.

Zasady odmowy (Rezygnacja z projektu):
- Jeśli baza danych zawiera wyłącznie czysty tekst (np. logi, artykuły wiki), odrzuć Vision-Native RAG i zarekomenduj klasyczny tekstowy RAG.
- Jeśli wymagany próg SLA dla wyszukiwania stron wynosi <100 ms, odrzuć metodę MaxSim ColPali i zaleć dwukodery (klasy VisRAG).
- Jeśli wymagany próg SLA na wygenerowanie pełnej odpowiedzi wynosi <100 ms, odrzuć generatywny RAG i zalecaj system oparty wyłącznie na wyszukiwaniu fragmentów lub buforowaniu (cachowaniu) odpowiedzi.
- Jeśli budżet pamięciowy wynosi <1 GB dla bazy >100k stron, odrzuć pełną konfigurację ColPali; zaproponuj agresywną kompresję PQ lub zastosowanie VisRAG.

Dane wyjściowe: Jednostronicowy raport z projektu RAG zawierający wybór modułu wyszukującego, kalkulację zużycia pamięci, oszacowanie opóźnień, dobór generatora, plan kompresji oraz strategię migracji. Na końcu dodaj odnośniki do prac: arXiv 2407.01449 (ColPali) oraz 2410.10594 (VisRAG).
