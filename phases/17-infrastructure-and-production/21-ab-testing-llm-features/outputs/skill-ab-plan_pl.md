---

name: ab-plan
description: Zaprojektuj test A/B LLM — wybierz platformę (Statsig lub GrowthBook), metrykę podstawową, poręcze, wielkość próbki z buforem szumu LLM, CUPED, zatrzymanie sekwencyjne i korekcję wielokrotnych porównań.
version: 1.0.0
phase: 17
lesson: 21
tags: [ab-testing, statsig, growthbook, cuped, sequential, benjamini-hochberg, srm]

---

Biorąc pod uwagę zmianę funkcji (parametr podpowiedzi / model / generowanie), podstawowe wskaźniki, oczekiwany wzrost i postawę zespołu (natywny dla hurtowni OSS vs pakiet SaaS), utwórz plan A/B.

Wyprodukuj:

1. Platforma. Statsig (w pakiecie SaaS, własność OpenAI) lub GrowthBook (MIT OSS, natywna dla hurtowni). Uzasadniać.
2. Metryka podstawowa + poręcze. Podstawowa to metryka, którą próbujesz przenieść; poręcze to rzeczy, które nie mogą ulec regresji (koszt/żądanie, opóźnienie P99, wskaźnik odmów).
3. Wielkość próbki. Klasyczne obliczanie mocy × 1,4 (bufor niedeterministyczny LLM).
4. Projekt. Stały horyzont lub sekwencyjny. Sekwencyjny, jeśli oczekujesz silnych sygnałów; naprawione, jeśli zmiana jest subtelna.
5. CUPOWANY. Włącz, jeśli dla metryki podstawowej istnieją dane sprzed okresu; określ regresor.
6. Korekta. Bonferroniego za niewielką liczbę testów; Benjamini-Hochberg za wiele powiązanych testów.
7. SRM. Wymagaj kontroli SRM przy każdym eksperymencie; zatrzymaj i debuguj, jeśli jest oflagowany.

Twarde odrzucenia:
- Wysyłka na wibracjach. Odmów – żądaj wyjątku A/B lub udokumentowanego wyjątku „nie-A/B”.
- Przeprowadzenie > 5 eksperymentów z tą samą podstawową metryką bez BH/Bonferroniego. Odmów — fałszywe odkrycie jest pewne.
- Pomijanie kontroli SRM. Odmów — błędy przy przypisywaniu są częste.

Zasady odmowy:
- Jeśli ruch dla tej funkcji wynosi < 1000 użytkowników/tydzień, odrzuć stałą A/B — zamiast tego wymagaj Shadow + Canary (Faza 17 · 20).
- Jeśli główny wskaźnik jest subiektywny (np. „jakość”) bez obiektywnego wskaźnika zastępczego, należy równolegle przeprowadzić ocenę przez człowieka.
- Jeśli hipoteza siły nośnej jest mniejsza niż poziom szumów LLM, odrzuć ją — eksperyment nie może jej wykryć przy realistycznej wielkości próbki.

Dane wyjściowe: jednostronicowy plan z platformą, elementami podstawowymi i poręczami, wielkością próbki, projektem, CUPED, korektą i polityką SRM. Zakończ zasadą decyzyjną: podstawowe znaczące + wszystkie poręcze nieistotne - negatywne → statek; jakiekolwiek naruszenie barier ochronnych → nie wysyłaj niezależnie od przyczyny pierwotnej.