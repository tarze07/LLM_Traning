---

name: training-budget-estimator
description: Estymacja parametrów (N, D, czas w godzinach, liczba GPU) dla nowego procesu trenowania transformera, z uwzględnieniem budżetu obliczeniowego i ograniczeń wdrożeniowych.
version: 1.0.0
phase: 7
lesson: 13
tags: [scaling-laws, training, chinchilla]

---

Na podstawie zdefiniowanego celu treningowego (docelowa strata / docelowe MMLU / docelowa metryka downstream), budżetu obliczeniowego (w USD lub FLOP), wolumenu inferencji (liczba tokenów/miesiąc) oraz ograniczeń sprzętowych (docelowe urządzenie, pamięć, opóźnienie), wygeneruj:

1. **Reżim obliczeniowy**: optymalny pod kątem praw skalowania Chinchilla (Chinchilla-optimal), nadmiernie wytrenowany (zoptymalizowany pod kątem inferencji) lub niedotrenowany (prototyp). Przedstaw jednozdaniowe uzasadnienie powiązane z przewidywanym wolumenem inferencji.
2. **N i D**: konkretne wartości liczby parametrów ($N$) i liczby tokenów ($D$). Podaj stosunek $D/N$. W przypadku modelu nadmiernie wytrenowanego (overtrained) określ przewidywaną karę za stratę (loss penalty) w porównaniu do konfiguracji optymalnej w sensie Chinchilla.
3. **Rzeczywisty czas treningu (wall-clock time)**: iloczyn godzin i liczby procesorów GPU, przy założeniu określonej efektywności wykorzystania GPU (MFU ≈ 40% dla modeli gęstych [dense], ~30% dla modeli MoE). Uwzględnij precyzję obliczeń (bf16 / fp8) oraz zastosowany optymalizator (AdamW / Muon).
4. **Źródła danych**: nazwy konkretnych korpusów lub budżet na dane syntetyczne. Oznacz flagą sytuację, w której wymagana wartość $D$ przekracza dostępny wolumen danych wysokiej jakości.
5. **Analiza ryzyka**: jeden konkretny scenariusz awarii (np. wyciek danych [data contamination], niestabilność optymalizatora przy dużej skali, niedopasowanie tokenizera do długości kontekstu, nasycenie benchmarków ewaluacyjnych).

Odrzuć propozycję trenowania gęstego (dense) modelu o rozmiarze > 8B parametrów w reżimie optymalnym w sensie Chinchilla, jeśli ma on obsługiwać wysoki wolumen zapytań inferencyjnych (ze względu na wysokie koszty inferencji w fazie produkcyjnej). Nie wyznaczaj docelowej wartości straty bez zdefiniowanego zbioru ewaluacyjnego. Oznacz jako błąd (flaguj) każdy plan przeznaczający > 1% budżetu na poszukiwanie architektury (architecture search) zamiast na weryfikację i filtrowanie danych – zysk z takich optymalizacji jest zazwyczaj minimalny. Wymagaj przeprowadzenia pilotażowego uruchomienia o skali 1% budżetu w celu walidacji założeń przed ostatecznym zatwierdzeniem pełnych środków na trening.
