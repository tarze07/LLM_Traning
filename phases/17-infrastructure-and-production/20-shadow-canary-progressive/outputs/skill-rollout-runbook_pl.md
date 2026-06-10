---

name: rollout-runbook
description: Zaprojektuj cień → kanarek → A/B → 100% plan wdrożenia nowego modelu LLM lub szablonu podpowiedzi z pięcioma bramkami kanaryjskimi, progami uwzględniającymi poziom szumów i ścieżką wycofywania w ciągu kilku sekund.
version: 1.0.0
phase: 17
lesson: 20
tags: [rollout, canary, shadow, progressive-delivery, feature-flags, argo-rollouts, flagger, kserve]

---

Biorąc pod uwagę zmianę kandydata (nowy model, nowy szablon monitu, nowe zasady routera), podstawowe metryki produkcji i tolerancję ryzyka, utwórz element Runbook wdrożenia.

Wyprodukuj:

1. Plan cieni. Czas trwania (24-72 godziny). Rejestrowane metryki: dane wyjściowe, liczba tokenów, opóźnienie, odmowa, błąd. Powiadomienie o: przesunięciu kosztów o >20%, przesunięciu długości wyjściowej o >30%, każdym naruszeniu schematu.
2. Progresja kanarkowa. Etapy (1% → 10% → 25% → 50% → 75% → 100%). Czas trwania etapu (30–24 godz. w zależności od natężenia ruchu; upewnij się, że każdy etap zawiera wystarczającą ilość danych zapewniających pewność statystyczną).
3. Pięć bram. Określ dokładne progi opóźnienia P99, kosztu/żądania, błędu/odmowy, długości wyjścia P99 i współczynnika kciuka w dół. Ustaw powyżej poziomu szumów (spodziewaj się 15% nieredukowalnej wariancji).
4. Oprzyrządowanie. Nazwij kontroler wdrażania (Argo Rollouts, Flagger, KServe) i system flag funkcji w celu natychmiastowego wycofania.
5. Ścieżka wycofania. Udokumentuj trzy działania: odwróć flagę → przywróć przypięte podsumowanie → zweryfikuj. Docelowy czas: poniżej 60 sekund od końca do końca.
6. Pominąć A/B? Uzasadniać. Ulepszone zmiany wariantów pomijają A/B; wyraźnie różne zmiany (nowe zachowanie, nowa krzywa kosztów) wymagają A/B.

Twarde odrzucenia:
- Pomijanie trybu cienia. Odmów – skoki kosztów i regresje długości nie pozwalają na ocenę offline.
- Bramy węższe niż 15% wariancji. Odmów — fałszywe alarmy zatrzymają legalne wdrożenia.
— Wycofywanie wymagające ponownego wdrożenia. Odmowa — to nie jest wycofanie, to zgłoszenie szkody.

Zasady odmowy:
- Jeśli zmiana ma kluczowe znaczenie dla bezpieczeństwa (np. zmiana obsługi PII), wymagaj wyraźnej dodatkowej bramki: zerowy wyciek PII w próbce cienia przed uruchomieniem Canary.
- Jeśli natężenie ruchu wynosi <100 żądań/godzinę, należy wymagać wydłużonych stopni kanarkowych — w przeciwnym razie hałas bramki zagłusza sygnał.
- Jeśli zespół nie może dostarczyć podstawowych wskaźników dla pięciu bramek kanaryjskich, odmów wdrożenia – warunkiem wstępnym jest poziom wyjściowy.

Dane wyjściowe: jednostronicowy element Runbook z cieniem, kanarkiem, bramkami, narzędziami, wycofywaniem i postawą A/B. Zakończ wymogiem ćwiczenia wycofywania zmian: przećwicz raz wycofywanie przed pierwszym rzeczywistym wdrożeniem.