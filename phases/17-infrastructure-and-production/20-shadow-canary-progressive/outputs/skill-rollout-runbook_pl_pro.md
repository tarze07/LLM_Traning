---

name: rollout-runbook
description: Projektowanie planu wdrożenia (Shadow → Canary → A/B → 100%) dla modeli LLM lub szablonów promptów, zawierającego 5 bramek kontrolnych (gates), progi uwzględniające szum niedeterminizmu oraz procedurę natychmiastowego wycofania zmian (rollback).
version: 1.0.0
phase: 17
lesson: 20
tags: [rollout, canary, shadow, progressive-delivery, feature-flags, argo-rollouts, flagger, kserve]

---

Na podstawie parametrów nowej wersji (nowy model, zaktualizowany szablon promptu, nowe zasady routingu), bazowych metryk produkcyjnych oraz tolerancji ryzyka, przygotuj dokument Runbook wdrożenia.

Przygotuj:

1. Plan fazy Shadow (Shadow deployment plan): Czas trwania (24-72 godziny). Rejestrowane metryki: wyjście modelu, liczba tokenów, opóźnienia, odmowy, błędy. Alerty w przypadku: wzrostu kosztów o >20%, zmiany długości odpowiedzi o >30% lub naruszenia schematu wyjścia.
2. Harmonogram wdrożenia Canary (Canary progression): Etapy (np. 1% → 10% → 25% → 50% → 100%). Czas trwania każdego kroku (np. od 30 minut do 24 godzin w zależności od wolumenu ruchu – celem jest zebranie reprezentatywnej statystycznie próby).
3. Definicję 5 bramek kontrolnych (Gates): Dokładne progi dla: opóźnienia P99, kosztu zapytania, współczynnika błędów/odmów, długości odpowiedzi P99 oraz negatywnych ocen użytkowników. Progi muszą być ustawione powyżej szumu tła (uwzględniając nieredukowalną wariancję na poziomie 15%).
4. Infrastrukturę wdrożeniową (Oprzyrządowanie): Wybór kontrolera (Argo Rollouts, Flagger, KServe) oraz systemu Feature Flags do szybkiego wycofania zmian.
5. Procedurę awaryjnego wycofania (Rollback path): Trzy proste kroki: przełączenie flagi logicznej → powrót do przypisanego hasha stabilnego modelu → weryfikacja. Cel czasowy: poniżej 60 sekund dla całego procesu.
6. Decyzję dotyczącą testów A/B: Uzasadnienie, czy ten etap jest konieczny. Optymalizacje techniczne (ten sam model, ale tańszy) mogą pomijać A/B; zmiany funkcjonalne (inne zachowanie, nowa krzywa kosztów) wymagają weryfikacji w teście A/B.

Kryteria odrzucenia runbooka:
- Pominięcie fazy Shadow traffic. Odrzuć – skoki kosztów i anomalie w długości odpowiedzi nie są weryfikowalne w testach offline.
- Ustawienie bramek tolerancji na poziomie poniżej 15% szumu wariancji. Odrzuć – spowoduje to fałszywe alarmy i blokowanie poprawnych wdrożeń.
- Procedura rollbacku wymagająca ponownego wdrożenia kodu (redeploy). Odrzuć – to potężne ryzyko awarii, a nie bezpieczny rollback.

Zasady odmowy/zastrzeżenia:
- Jeśli zmiana dotyczy mechanizmów bezpieczeństwa danych (np. ochrony danych osobowych/PII), wymagaj dodatkowej bramki: absolutne zero wycieków danych PII w fazie shadow traffic przed przejściem do canary.
- Jeśli natężenie ruchu wynosi <100 zapytań na godzinę, wymagaj znacznego wydłużenia czasu trwania etapów canary – w przeciwnym razie szum statystyczny uniemożliwi poprawną ocenę bramek.
- Jeśli zespół nie posiada infrastruktury umożliwiającej pomiar metryk dla 5 bramek canary, odrzuć plan – monitoring to warunek konieczny uruchomienia procesu.

Format końcowy: Jednostronicowy runbook zawierający plan fazy shadow, harmonogram canary, progi bramek kontrolnych, wykaz narzędzi, procedurę rollbacku oraz plan testów A/B. Dokument należy zakończyć wymogiem próbnego wycofania wersji: przeprowadzenie jednego testowego rollbacku na środowisku stagingowym przed wdrożeniem produkcyjnym.
