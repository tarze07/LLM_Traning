---

name: training-budget-estimator
description: Oszacowanie (N, D, godziny, liczba procesorów graficznych) dla nowego przebiegu szkoleniowego transformatora, biorąc pod uwagę budżet obliczeniowy i ograniczenia dotyczące wdrożenia.
version: 1.0.0
phase: 7
lesson: 13
tags: [scaling-laws, training, chinchilla]

---

Biorąc pod uwagę cel szkoleniowy (strata docelowa / docelowa MMLU / docelowa metryka downstream), budżet obliczeniowy (w dolarach lub FLOP), wielkość wnioskowania (tokeny/miesiąc) i ograniczenia (urządzenie docelowe, pamięć, opóźnienie), wynik:

1. Reżim obliczeniowy. Optymalna dla szynszyli, przeszkolona (zoptymalizowana pod kątem wnioskowania), niedostatecznie przeszkolona (prototyp). Powód jednozdaniowy powiązany z objętością wnioskowania.
2. N i D. Wartości konkretne. Wydrukuj współczynnik `D/N`. Jeśli jesteś przeszkolony, zwróć uwagę na karę za stratę w porównaniu z optymalną szynszylą.
3. Zegar ścienny treningowy. Godziny × liczba procesorów graficznych, biorąc pod uwagę zakładaną przepustowość szkolenia (MFU ≈ 40% dla gęstego, ~30% dla MoE). Budżetuj precyzję (bf16 / fp8) i optymalizator (AdamW / Muon).
4. Źródła danych. Korpusy nazwane lub budżet syntetyczny. Oznacz, jeśli wymagany `D` przekracza dostępne tokeny wysokiej jakości.
5. Uwaga dotycząca ryzyka. Jeden konkretny tryb awarii: zanieczyszczenie danych, niestabilność optymalizatora na dużą skalę, niedopasowanie tokenizera długości kontekstu, nasycenie zestawu ewaluacyjnego.

Odmów trenowania gęstego modelu > 8B w trybie optymalnym dla szynszyli, jeśli będzie on obsługiwał dużą liczbę wnioskowań – co wiąże się z kosztami wnioskowania. Odmawiaj ustalenia docelowej straty bez zdefiniowanego zestawu ocen. Oznacz dowolny plan wydatkowaniem >1% budżetu na wyszukiwanie architektury, a nie na sprawdzanie danych — wiadomo, że zwroty są niewielkie. Wymagaj uruchomienia 1% budżetu na dużą skalę, aby zweryfikować założenia przed zatwierdzeniem całego budżetu.