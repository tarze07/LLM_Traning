---

name: ab-plan
description: Zaprojektuj test A/B dla LLM – wybierz platformę (Statsig lub GrowthBook), główną metrykę, zabezpieczenia (guardrails), wielkość próbki z uwzględnieniem szumu LLM, CUPED, sekwencyjne zatrzymywanie oraz korektę z tytułu wielokrotnych porównań.
version: 1.0.0
phase: 17
lesson: 21
tags: [ab-testing, statsig, growthbook, cuped, sequential, benjamini-hochberg, srm]

---

Na podstawie zmian w funkcjonalności (parametry promptu / model / generowanie), głównych metryk, oczekiwanego wzrostu (uplift) oraz preferencji zespołu (rozwiązanie OSS zintegrowane z hurtownią danych vs gotowy pakiet SaaS), przygotuj plan testów A/B.

Wygeneruj:

1. Platforma: Statsig (pakiet SaaS, hostowany) lub GrowthBook (licencja MIT OSS, zintegrowany z hurtownią danych). Przedstaw uzasadnienie wyboru.
2. Główna metryka + zabezpieczenia (guardrails): Główna metryka to ta, którą chcesz poprawić. Zabezpieczenia to wskaźniki, które nie mogą ulec pogorszeniu (np. koszt pojedynczego zapytania, opóźnienie P99, współczynnik błędów/odmów).
3. Wielkość próbki: Klasyczne obliczenie mocy statystycznej pomnożone przez 1,4 (bufor na niedeterministyczny charakter LLM).
4. Model testu: Stały horyzont czasowy (fixed-horizon) lub test sekwencyjny. Wybierz test sekwencyjny, jeśli spodziewasz się silnego sygnału; wybierz stały horyzont, jeśli zmiana jest subtelna.
5. CUPED: Włącz, jeśli dla głównej metryki dostępne są dane z okresu przed eksperymentem; wskaż regresor.
6. Korekta: Metoda Bonferroniego w przypadku niewielkiej liczby testów; metoda Benjaminiego-Hochberga przy wielu powiązanych testach.
7. SRM (Sample Ratio Mismatch): Wymagaj weryfikacji SRM dla każdego eksperymentu; w przypadku wykrycia anomalii wstrzymaj test i przeprowadź debugowanie.

Kryteria odrzucenia planu (Hard rejects):
- Wdrożenie "na wyczucie" (shipping on vibes): Odrzuć taki wniosek – wymagaj przeprowadzenia testu A/B lub udokumentowanego i zatwierdzonego odstępstwa.
- Przeprowadzanie > 5 eksperymentów dla tej samej głównej metryki bez zastosowania korekty (np. Benjaminiego-Hochberga lub Bonferroniego): Odrzuć – wysokie ryzyko fałszywie pozytywnego wyniku (false discovery).
- Pomijanie weryfikacji SRM: Odrzuć – błędy w alokacji ruchu zdarzają się często.

Zasady odrzucenia:
- Jeśli ruch dla danej funkcji wynosi < 1000 użytkowników tygodniowo, odrzuć standardowy test A/B ze stałym horyzontem – zamiast tego wymagaj wdrożenia typu Shadow + Canary (Faza 17 · Lekcja 20).
- Jeśli główna metryka jest subiektywna (np. "jakość") i brakuje dla niej obiektywnego wskaźnika zastępczego (proxy), wymagaj równoległego przeprowadzenia oceny przez ludzi (human evaluation).
- Jeśli zakładany wzrost (uplift) w ramach hipotezy jest mniejszy niż poziom szumów LLM, odrzuć plan – wykrycie takiej zmiany przy realistycznej wielkości próby jest niemożliwe.

Wynik: Jednostronicowy plan zawierający wybraną platformę, główną metrykę i wskaźniki zabezpieczające, wielkość próby, model testu, zastosowanie CUPED, korektę wielokrotnych porównań oraz procedurę SRM. Na końcu umieść regułę decyzyjną: jeśli główna metryka osiągnie istotność statystyczną i żadne z zabezpieczeń nie wykaże istotnego pogorszenia parametrów -> wdrożenie (ship); jeśli nastąpi jakiekolwiek naruszenie zabezpieczeń -> wstrzymanie wdrożenia, niezależnie od przyczyny.
