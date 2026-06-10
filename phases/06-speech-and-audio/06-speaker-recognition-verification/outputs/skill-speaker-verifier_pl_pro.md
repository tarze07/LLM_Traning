---

name: speaker-verifier
description: Zaprojektuj kompletny potok weryfikacji mówców lub diaryzacji, obejmujący wybór modelu, protokół rejestracji oraz kalibrację progów decyzyjnych.
version: 1.0.0
phase: 6
lesson: 06
tags: [audio, speaker, verification, diarization]

---

Na podstawie zadanego celu (weryfikacja vs. identyfikacja vs. diaryzacja, domena docelowa, kanał transmisyjny, model zagrożeń biometrycznych) oraz danych wejściowych (liczba godzin na strojenie progów, liczba mówców, budżet czasowy nagrania rejestracyjnego), określ:

1. Ekstraktor osadzeń (Embedder): ECAPA-TDNN / WavLM-SV / ReDimNet / x-vector. Uzasadnij wybór.
2. Protokół rejestracji (Enrollment): Liczba klipów referencyjnych, minimalny czas trwania nagrania, bramkowanie szumów (noise gating), strategie dopasowania kanałów (channel matching).
3. Metodę punktacji (Scoring): Podobieństwo cosinusowe / PLDA; zastosowanie normalizacji AS-norm; wielkość kohorty referencyjnej.
4. Próg decyzyjny: Docelowa wartość FAR (False Acceptance Rate) dostosowana do ryzyka oszustwa lub punkt EER; wielkość i opis zbioru kalibracyjnego.
5. Zabezpieczenia przed oszustwami (Anti-spoofing): Model wykrywania prób podszywania się (AASIST, RawNet2), test żywotności (liveness detection / challenge-response) lub wykrywanie odtworzeń (replay attack detection).

Zasady weryfikacji:
- Odrzuć projekty wdrożenia systemów podatnych na próby oszustwa (spoofing) bez zaimplementowanego modułu anti-spoofing.
- Odrzuć raporty wskaźnika EER, które nie podają szczegółowych parametrów zbioru ewaluacyjnego, w tym charakterystyki kanału transmisyjnego i rozkładu długości nagrań.
- Oznacz jako błąd konfiguracje przenoszące progi podobieństwa cosinusowego pomiędzy różnymi domenami bez przeprowadzenia ponownej kalibracji na danych docelowych.
