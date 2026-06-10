---

name: swarm-optimizer
description: Wybierz pomiędzy algorytmami PSO, ACO, genetycznymi i optymalizatorami opartymi na gradientach dla danego problemu optymalizacji LLM lub systemów agentowych. Metody rojowe inspirowane naturą nie wymagają gradientów i są idealne w scenariuszach, gdy przestrzeń poszukiwań jest dyskretna lub funkcja przystosowania (fitness) ma charakter czarnej skrzynki.
version: 1.0.0
phase: 16
lesson: 19
tags: [multi-agent, swarm-optimization, PSO, ACO, prompt-optimization, routing]

---

Na podstawie specyfikacji problemu optymalizacji modelu LLM lub systemu agentowego wybierz odpowiedni algorytm optymalizacyjny.

Opracuj następujące elementy:

1. **Profil problemu (problem fingerprint).** Przestrzeń poszukiwań (wartości ciągłe, ciąg znaków promptu, wagi modeli, graf routingu), sygnał przystosowania (fitness signal – automatyczne testy, ocena LLM, ocena ludzka, biznesowe wskaźniki KPI) oraz dopuszczalny czas obliczeń (minuty, godziny, dni).
2. **Wybór optymalizatora.** Wybierz spośród: PSO, ACO, algorytm genetyczny, DPO/RL, strojenie ręczne. Każda z tych metod ma dedykowany obszar zastosowań:
   - Wartości ciągłe w ograniczonej przestrzeni parametrów → PSO
   - Wybór optymalnej trasy lub ścieżki przepływu → ACO
   - Dyskretne struktury symboliczne lub kod programów → algorytmy genetyczne (GA)
   - Ciągłe, różniczkowalne nagrody (rewards) → DPO/RL
   - Niskowymiarowe przestrzenie i krótki czas ewaluacji → przeszukiwanie losowe lub przeszukiwanie siatki (grid search)
3. **Wielkość populacji.** Przedział 10-30 cząstek dla PSO/GA lub rozmiar macierzy feromonów dla ACO. Obliczanie budżetu: `N * T * koszt ewaluacji`. Koszt działania roju nie może przewyższać zysków generowanych przez zoptymalizowane rozwiązanie.
4. **Funkcja przystosowania i bramka jakości (quality gate).** Jaka metryka służy do ewaluacji kandydata? Jaki próg jakości w przypadku routingu ACO jest wymagany do zdeponowania feromonów na ścieżce?
5. **Monitorowanie zbieżności (convergence).** Logowanie wartości `g_best` lub stabilności feromonów w każdej iteracji. Ustawienie alertów dla zjawisk dywergencji (katastrofalnego dryfu) oraz przedwczesnej zbieżności (utknięcia w optimum lokalnym).
6. **Strojenie parametrów parowania i eksploracji.** Dobór współczynnika bezwładności oraz wag poznawczych/społecznych dla PSO; dobór tempa parowania feromonów oraz ilości odkładanego feromonu dla ACO. Zależność: zbyt małe tempo parowania/bezwładność powoduje zablokowanie na wczesnych rozwiązaniach; zbyt duże – prowadzi to do utraty pamięci o dobrych ścieżkach.
7. **Warunki resetu.** W przypadku zmiany rozkładu danych testowych (data drift) lub schematu zadań należy tymczasowo zresetować wartość `g_best` lub wyzerować macierz feromonów. Przechowywanie nieaktualnych danych jest gorsze niż brak historii.

Kryteria twardego odrzucenia projektu:

- Stosowanie algorytmów rojowych w zadaniach, gdzie ocena przystosowania wymaga manualnej weryfikacji przez człowieka. Budżet i czas iteracji są wtedy nieakceptowalne.
- Rozmiar populacji powyżej 50 cząstek bez wyraźnego uzasadnienia ekonomicznego (efekt malejących przychodów).
- Wdrożenie routingu opartego na feromonach bez bramki jakości. Szybcy, lecz zwracający błędne odpowiedzi agenci zablokują system.
- Stosowanie PSO in dyskretnych przestrzeniach poszukiwań, które nie posiadają naturalnych reprezentacji ciągłych (embeddings). W takich przypadkach należy zastosować algorytmy genetyczne (GA) lub symulowane wyżarzanie.

Zasady odmowy (rekomendacje alternatywne):

- Jeśli użytkownik próbuje przeprowadzić optymalizację bez jasno sprecyzowanej funkcji przystosowania, zalecaj w pierwszej kolejności zdefiniowanie metryki ewaluacyjnej. Algorytmy rojowe nie mogą działać bez automatycznego oceniającego.
- Jeśli planowany budżet jest mniejszy niż 100 USD, zalecaj ręczne strojenie parametrów oraz stosowanie pamięci podręcznej (caching) zamiast uruchamiania systemów rojowych.
- Jeśli rozkład danych wejściowych ulega drastycznym zmianom każdego dnia, zalecaj podejście uczenia online lub algorytmy bandytów (multi-armed bandits) zamiast optymalizatorów rojowych.

Format wyjściowy: jednostronicowy brief projektowy. Rozpocznij od jednozdaniowej rekomendacji (np. „Zastosuj algorytm ACO z bramką jakości kontrolującą odkładanie feromonów dla problemu routingu 3 agentów × 4 typy zadań. Współczynnik parowania 0,05, próg bramki 0,6, 200 iteracji rozbiegowych”), po czym przedstaw omówienie siedmiu powyższych punktów. Dokument zakończ szacowanym budżetem oraz tygodniowym planem wdrożenia.
