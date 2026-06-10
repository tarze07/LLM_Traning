---

name: slo-goodput-gate
description: Stwórz gotowy do wdrożenia w potoku CI/CD szablon testu benchmarkowego (recepturę), który będzie bramkować wdrożenia modeli LLM w oparciu o wskaźnik goodput, a nie surową przepustowość, z uwzględnieniem percentyli P50/P90/P99 oraz udokumentowanego wyboru narzędzi.
version: 1.0.0
phase: 17
lesson: 08
tags: [inference-metrics, goodput, ttft, tpot, itl, slo, benchmarking]

---

Na podstawie opisu obciążenia (modelu, sprzętu, docelowej współbieżności, typu interakcji z użytkownikiem – np. czat strumieniowy, zapytanie jednorazowe, asystent głosowy, agent), utwórz bramkę SLO opartą na wskaźniku goodput dla potoku CI/CD.

Wygeneruj:

1. Specyfikacja SLO. Określ trzy progi: dla percentyla P99 TTFT, P99 TPOT oraz P99 E2E. Dobierz uzasadnione wartości na podstawie typu interakcji (np. czat strumieniowy: TTFT 500 ms, TPOT 25 ms, E2E 3 s; asystent głosowy: bardziej rygorystyczne TTFT 300 ms; agent: luźniejsze E2E 5 s).
2. Szablon testu porównawczego (receptura). Wybór narzędzia (LLMPerf lub GenAI-Perf – wskaż, które wybierasz i dlaczego). Rozkład promptów (średnia długość promptu wejściowego i wyjściowego oraz ich odchylenie standardowe). Analiza wpływu współbieżności (testy przy 25%, 50%, 100% i 150% docelowego obciążenia).
3. Obliczanie wskaźnika Goodput. Wzór: odsetek zapytań spełniających jednocześnie wszystkie trzy zdefiniowane ograniczenia. Cel: >= 99% na środowisku produkcyjnym, >= 95% dla wdrożeń typu canary.
4. Raportowanie percentyli. Dla każdego wskaźnika należy raportować wartości P50, P90 i P99 (nigdy nie podawaj samej średniej). Uwzględnij adnotację objaśniającą metodę walidacji.
5. Uwaga dotycząca różnic w narzędziach. Określ, czy wybrane narzędzie uwzględnia, czy wyklucza czas TTFT z ITL. Sklaryfikuj te definicje przed porównywaniem wyników między zespołami.
6. Logika bramkowania. Budowanie potoku CI kończy się sukcesem, jeśli wskaźnik goodput wynosi >= docelowej wartości przy pełnej (100%) współbieżności. Zgłoś ostrzeżenie (flagę), jeśli wskaźnik goodput spada o więcej niż 5 punktów procentowych przy wzroście współbieżności ze 100% do 150% – sygnalizuje to brak zapasu wydajności systemu w testach obciążeniowych.

Kategoryczne odrzucenia:
- Bramkowanie wdrożeń wyłącznie na podstawie przepustowości. Odrzuć taki wskaźnik i wymagaj zastosowania wskaźnika goodput.
- Raportowanie wyłącznie średnich wartości bez podawania percentyla P99. Odrzuć taki raport.
- Pomijanie nazwy oraz wersji użytego narzędzia benchmarkującego. Odrzuć taki raport.
- Przeprowadzanie testów porównawczych wyłącznie przy docelowej współbieżności; zawsze wymagaj wykonania testu w pełnym zakresie obciążenia (sweep).

Zasady odmowy wdrożenia (odrzucenie rekomendacji):
- Jeśli użytkownik nie zdefiniował celów SLO, odrzuć proces wdrożenia i w pierwszej kolejności opracuj progi w oparciu o typ interakcji.
- Jeśli rozkład promptów w teście zakłada „identyczne prompty w pętli”, odrzuć test – jest to błąd sztucznej powtarzalności. Wymagaj użycia realistycznego, syntetycznego zestawu testowego.
- Jeśli test benchmarkowy obejmuje mniej niż 30 przebiegów lub mniej niż 100 zapytań na jeden przebieg, odrzuć wyniki jako statystycznie niewiarygodne.

Wynik: jednostronicowa specyfikacja bramki SLO zawierająca listę progów, szablon testu porównawczego, uzasadnienie wyboru narzędzia, szablon raportu percentylowego oraz reguły kwalifikacji CI (Pass/Fail). Zakończ sekcją „Co dalej mierzyć”, wskazującą na analizę krzywej goodput w funkcji współbieżności, badanie wpływu rozkładu długości promptów lub porównanie wydajności z włączonym/wyłączonym mechanizmem chunked prefill – w zależności od zidentyfikowanych wąskich gardeł.
