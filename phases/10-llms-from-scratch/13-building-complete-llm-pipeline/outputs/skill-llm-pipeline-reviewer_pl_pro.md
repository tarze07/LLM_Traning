---

name: llm-pipeline-reviewer
description: Przegląd i weryfikacja kompleksowego manifestu potoku treningowego LLM przed kosztownym uruchomieniem na dużą skalę.
version: 1.0.0
phase: 10
lesson: 13
tags: [pipeline, training, manifest, eval-gate, cost, rollback]

---

Na podstawie proponowanego manifestu potoku treningowego (YAML lub JSON opisującego etapy: tokenizer, przygotowanie danych, pre-training, SFT, dopasowanie/alignment, ewaluację, kwantyzację oraz serwowanie/serving), przygotuj raport zawierający:

1. **Wykres etapów (DAG potoku)**: Upewnij się, że każdy etap ma precyzyjnie zdefiniowane wejścia i wyjścia. Wskaż brakujące zależności, ukryte stany (implicit state) lub etapy, które odwołują się bezpośrednio do katalogu zamiast do nazwanego hasha artefaktu.
2. **Łańcuch haszujący (hash chain)**: Sprawdź, czy `output_hash` etapu $N$ odpowiada jednemu z `input_hash` w kolejnych etapach potoku. Każda niezgodność oznacza niespójność manifestu i blokuje uruchomienie potoku.
3. **Bramki ewaluacyjne (evaluation gates)**: Każda metryka w bramkach weryfikacyjnych musi mieć przypisaną wartość liczbową, operator porównania, próg zaliczenia oraz źródło pomiaru. Odrzuć bramki oparte na kryteriach subiektywnych (np. „wygląda dobrze”), bez określonego progu lub mierzone na danych treningowych.
4. **Zabezpieczenie przed regresją (regression checks)**: Wyniki standardowych benchmarków (np. MMLU, MATH, HumanEval+, GPQA lub specyficznych dla domeny) muszą mieć przypisane wartości bazowe (baselines). Uruchomienie potoku bez punktów odniesienia uniemożliwia wykrycie regresji modelu.
5. **Budżet KL**: Etapy dopasowania (RLHF, DPO, CAI, GRPO) muszą mieć zdefiniowany maksymalny limit skumulowanej dywergencji KL względem modelu referencyjnego. Brak ograniczenia KL prowadzi do niekontrolowanego dryfu modelu.
6. **Detekcja skażenia danych (contamination checks)**: Zbiory treningowe oraz ewaluacyjne muszą przejść udokumentowany test nakładania się (wycieku danych) za pomocą dokładnego dopasowania (exact match) lub n-gramów (np. 13-gramów). Maksymalny próg dopuszczalnego nakładania się danych: < 0,1%.
7. **Szacowanie kosztów**: Przedtreningowe oszacowanie kosztów dla każdego etapu oraz sumaryczny koszt porównany z bramką budżetową. Jeśli szacowany koszt przekracza limit, potok nie może zostać uruchomiony.
8. **Plan awaryjny (rollback plan)**: Dla każdego etapu określ procedury na wypadek niepowodzenia (restart, wycofanie do poprzedniego stabilnego artefaktu, weryfikacja wejść i restart etapów downstream). Kosztowne etapy (np. pre-training) muszą mieć wdrożoną strategię częstego zapisu checkpointów (warm checkpointing).
9. **Repozytorium artefaktów (artifact store)**: Checkpointy, zbiory danych, tokenizatory oraz raporty z ewaluacji muszą być adresowane zawartością za pomocą sum kontrolnych (SHA-256). Artefakty identyfikowane jedynie po nazwie pliku (np. „latest.pt”) są bezwzględnie odrzucane.
10. **Obserwowalność (observability)**: Każdy etap musi generować strukturyzowane logi zawierające trace_id (identyfikator śledzenia), nazwę etapu, hash wejściowy, hash wyjściowy, czas rzeczywisty (wall-clock time) oraz koszt. Brak trace_id uniemożliwia późniejsze debugowanie procesu.

Sygnały ostrzegawcze skutkujące zablokowaniem potoku (HOLD):
- Brak zdefiniowanego źródła pomiaru w bramce ewaluacyjnej (bramka zdefiniowana dla metryki, która nie jest obliczana na żadnym etapie).
- Współdzielenie checkpointów między etapami (brak separacji zadań – separation of concerns).
- Etap dopasowania (alignment) bez zdefiniowanego modelu referencyjnego (brak punktu odniesienia dla dywergencji KL).
- Wykorzystanie LLM-as-a-judge, gdzie model oceniający należy do tej samej rodziny co oceniana polityka (ryzyko stronniczości/skażenia).
- Szacowany koszt przekraczający budżet o ponad 20%.
- Plan awaryjny (rollback plan) polegający wyłącznie na „restarcie od zera”.

Rezultat: dwustronicowy raport z recenzji ze statusem PASS/HOLD dla każdej bramki, wskazaniem konkretnego pola w manifeście, które wywołało dany werdykt, oraz opisem minimalnej zmiany wymaganej do zmiany statusu z HOLD na PASS.
