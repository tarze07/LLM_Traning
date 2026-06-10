---

name: eagle3-tuner
description: Wybór i dostrajanie strategii dekodowania spekulatywnego (klasyczne / Medusa / EAGLE-1/2/3 / lookahead) pod kątem profilu obciążenia wnioskowaniem (inference)
version: 1.0.0
phase: 10
lesson: 15
tags: [speculative-decoding, eagle, eagle-3, medusa, inference, vllm, sglang, tensorrt-llm]

---

Na podstawie docelowych parametrów produkcyjnego wnioskowania (model weryfikujący/target model, rozmiar batcha, rozkład długości sekwencji, docelowe opóźnienie p50/p99, typ akceleratora, oczekiwany współczynnik akceptacji $\alpha$ z telemetrii oraz rodzaj zadań), zaproponuj strategię dekodowania spekulatywnego oraz parametry dostrajania. Rekomendacja musi bezwzględnie zachować matematyczny rozkład wyników modelu głównego (target/verifier) – jakikolwiek spadek jakości odpowiedzi jest niedopuszczalny.

Zwróć:

1. **Wybór rodziny metod**: Wybierz spośród klasycznej (vanilla), Medusa, EAGLE-1, EAGLE-2, EAGLE-3 lub lookahead. Uzasadnij wybór na podstawie telemetrii współczynnika akceptacji $\alpha$ (lub skalibrowanego szacunku), dopuszczalnego kosztu treningu (brak, krótki SFT lub pełny trening na $\ge$ 60B tokenów) oraz dostępności gotowych checkpointów modelu pomocniczego (istnieją gotowe modele EAGLE-3 dla Llama 3.1/3.3, DeepSeek-V3, Qwen 2.5).
2. **Optymalną długość propozycji (draft length) N**: Wybierz liczbę całkowitą $N$ minimalizującą oczekiwany rzeczywisty czas (wall-clock time) przetwarzania jednego tokena, wyliczony na podstawie współczynnika $\alpha$ oraz stosunku kosztu pojedynczego kroku modelu draft do modelu głównego ($c$). Wzór do optymalizacji: $\text{minimalizuj } \frac{1 + N \cdot c}{(1 - \alpha^{N+1}) / (1 - \alpha)}$. Przedstaw obliczenia dla trzech kandydujących wartości $N$ wokół punktu optymalnego.
3. **Strukturę drzewa propozycji (dla EAGLE-2/3)**: Dobierz głębokość drzewa oraz współczynnik rozgałęzienia (branching factor) w oparciu o budżet pamięci. Sugerowane wartości domyślne: głębokość 3 z rozgałęzieniem (4, 2, 2) dla batch_size $\le$ 8; głębokość 2 z rozgałęzieniem (4, 2) dla batch_size 16–64; brak struktury drzewiastej (tylko sekwencja liniowa) dla batch_size > 64.
4. **Progi temperaturowe (temperature gating)**: Dla temperatury próbkowania > 0,8 współczynnik $\alpha$ drastycznie spada. Zarekomenduj automatyczne wyłączanie dekodowania spekulatywnego powyżej tego progu lub przełączenie na szersze drzewo z mniejszym współczynnikiem rozgałęzienia na węzeł.
5. **Mechanizm przywracania stanów KV (KV rollback)**: Wskaż specyfikę implementacji pamięci podręcznej KV w wybranym silniku (np. bufor alokowany w vLLM vs logiczna długość sekwencji w TensorRT-LLM) i potwierdź obsługę cofania stanów KV cache dla zapytań w batchu przy docelowym obciążeniu.

Zasady bezwzględnego odrzucenia (red flags):
- Rekomendacje, które modyfikują rozkład prawdopodobieństwa tokenów modelu głównego (np. przybliżona weryfikacja spekulatywna – approximate speculative decoding, łagodne kryteria odrzucenia/soft rejection).
- Wdrażanie dekodowania spekulatywnego dla rozmiaru batcha = 1 na małym modelu głównym, gdzie narzut generowany przez model draft przewyższa zysk z pominięcia kroków modelu głównego.
- Stosowanie modeli pomocniczych (draft) EAGLE wytrenowanych z użyciem innego tokenizera lub na innej wersji modelu bazowego niż model główny.
- Uruchomienie dekodowania spekulatywnego bez obsługi przywracania stanów KV cache (KV rollback) – prowadzi to do niezauważalnego uszkodzenia spójności generowanych tokenów.

Kryteria odmowy zatwierdzenia:
- Jeśli telemetria współczynnika $\alpha$ jest niedostępna, a zbiór zadań obejmuje kreatywne pisanie z wysoką temperaturą próbkowania – odrzuć projekt i zażądaj wstępnego przeprowadzenia kalibracji.
- Jeśli model główny posiada mniej niż 7B parametrów (dense), zalecane jest całkowite wyłączenie dekodowania spekulatywnego zamiast wdrażania jakiejkolwiek metody.
- Jeśli stos serwujący nie wspiera wybranej rodziny modeli draft (np. starsza wersja vLLM bez natywnej obsługi EAGLE-3), zalecane jest przejście na EAGLE-2 zamiast wymuszania aktualizacji lub przebudowy stosu przez użytkownika.

Rezultat: jednostronicowa specyfikacja zawierająca rekomendację modelu draft, wartość $N$, strukturę drzewa (jeśli ma zastosowanie), potwierdzenie wdrożenia KV rollback oraz szacowany wskaźnik przyspieszenia (speedup). Zakończ dokument sekcją „Plan telemetrii współczynnika akceptacji”, wskazując precyzyjnie punkty rejestracji logów (logging endpoints), które użytkownik musi dodać na swoim serwerze produkcyjnym, aby zweryfikować efektywność metody w pierwszym tygodniu działania.
