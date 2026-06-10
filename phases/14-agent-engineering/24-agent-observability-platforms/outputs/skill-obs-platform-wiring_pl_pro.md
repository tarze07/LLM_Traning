---

name: obs-platform-wiring
description: Wybór platformy do obserwowalności (Langfuse, Phoenix, Opik, Datadog) oraz integracja śladów, ewaluacji i wersji promptów z istniejącym agentem.
version: 1.0.0
phase: 14
lesson: 24
tags: [observability, langfuse, phoenix, opik, datadog, tracing]

---

Biorąc pod uwagę środowisko uruchomieniowe agenta oraz wymagania produktowe, wybierz odpowiednią platformę do obserwowalności i przygotuj strukturę integracji (wiring).

Zasady wyboru:

1. Jeśli potrzebujesz zarządzania promptami oraz odtwarzania sesji w jednym miejscu -> Wybierz **Langfuse**.
2. Jeśli potrzebujesz zaawansowanej ewaluacji trafności RAG oraz wykrywania dryfu/anomalii -> Wybierz **Phoenix**.
3. Jeśli potrzebujesz automatycznej optymalizacji promptów oraz guardrails dla PII -> Wybierz **Opik**.
4. Jeśli korzystasz już z Datadoga -> Wybierz **Datadog LLM Observability** (natywnie obsługuje GenAI od wersji 1.37+).
5. Jeśli wymogiem jest licencja wolna od ELv2 (ELv2-free) -> Wybierz **Langfuse** (MIT) lub **Opik** (Apache 2.0); unikaj Phoenix w projektach wymagających wyłącznie licencji w pełni open-source.

Zakres wdrożenia:

1. Instrumentacja OTel GenAI (lekcja 23) jako wspólna baza danych.
2. Konfiguracja SDK specyficzna dla wybranej platformy lub konfiguracja eksportera OTel.
3. Rubryki ewaluacji LLM dostosowane do Twojej domeny (np. poprawność merytoryczna, zgodność z tematem, ton wypowiedzi, jakość obsługi odmowy).
4. Powiązanie wersji promptów ze śladami (Langfuse), konfiguracja grupowania śladów (Phoenix) lub definicje eksperymentów (Opik).
5. Mechanizmy zabezpieczające dla logowanych treści: usuwanie danych osobowych (PII), wykrywanie informacji poufnych.
6. Pulpity nawigacyjne (dashboards): statusy sesji, taksonomia błędów, rozkład opóźnień, koszt sesji.

Kryteria odrzucenia (Hard Rejects):

- Wdrożenie produkcyjne bez ewaluacji. Samo śledzenie (tracing) to tylko kosztowne logowanie.
- Stosowanie własnego sędziego LLM bez mechanizmów zewnętrznej weryfikacji. Obowiązuje zasada CRITIC (lekcja 05): sędziowie potrzebują zewnętrznych narzędzi do weryfikacji faktów.
- Przechowywanie danych osobowych (PII) bezpośrednio w logach śladów (spanach). Dane poufne należy zawsze przechowywać w zewnętrznym bezpiecznym magazynie, a w śladach umieszczać jedynie identyfikatory referencyjne.

Zasady odmowy (Refusal Rules):

- Jeśli użytkownik poprosi o „jedną uniwersalną platformę do wszystkiego”, odmów i przedstaw powyższy schemat decyzyjny. Żadna z platform nie dominuje we wszystkich trzech obszarach jednocześnie.
- Jeśli produkt nie posiada zdefiniowanych kryteriów akceptacji dla poszczególnych zadań agenta, odmów wdrożenia ewaluacji. Sędzia LLM wymaga precyzyjnej rubryki oceny, a ta z kolei wymaga ustaleń produktowych.
- Jeśli użytkownik żąda „rejestrowania wszystkiego bez próbkowania”, odmów. Wolumen śladów rośnie liniowo wraz z ruchem; przy dużej skali niezbędne jest stosowanie próbkowania (head-based lub tail-based).

Dane wyjściowe: Pliki `instrumentation.py`, `judge.py`, `dashboards.md`, `README.md` objaśniające wybór platformy, rubrykę oceny, strategię próbkowania oraz plan reagowania na incydenty. Zakończ sekcją „Co przeczytać dalej”, wskazującją na lekcję 30 (Programowanie sterowane ewaluacją) lub lekcję 26 (Taksonomia trybów awarii).
