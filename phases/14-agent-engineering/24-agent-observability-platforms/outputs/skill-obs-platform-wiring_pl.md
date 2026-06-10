---

name: obs-platform-wiring
description: Wybierz platformę obserwowalności (Langfuse, Phoenix, Opik, Datadog) i przesyłaj ślady + oceny + wersje podpowiedzi do istniejącego agenta.
version: 1.0.0
phase: 14
lesson: 24
tags: [observability, langfuse, phoenix, opik, datadog, tracing]

---

Biorąc pod uwagę środowisko wykonawcze agenta i wymagania dotyczące produktu, wybierz platformę obserwowalną i stwórz rusztowanie okablowania.

Decyzja:

1. Potrzebujesz szybkiego zarządzania + powtórki sesji w jednym miejscu -> **Langfuse**.
2. Potrzebujesz głębokiej trafności RAG + wykrywania dryfu/anomalii -> **Phoenix**.
3. Potrzebujesz automatycznej szybkiej optymalizacji + poręczy PII -> **Opik**.
4. Uruchom już Datadog -> **Datadog LLM Observability** (mapuje GenAI natywnie od wersji 1.37+).
5. Potrzebujesz licencji ELv2-free -> **Langfuse** (MIT) lub **Opik** (Apache 2.0); unikaj Phoenix dla czystej dystrybucji OSS.

Wyprodukuj:

1. Oprzyrządowanie Otel GenAI (lekcja 23) — to jest wspólne podłoże.
2. Konfiguracja eksportera SDK lub Otel specyficzna dla platformy.
3. Rubryki oceny LLM dla Twojej domeny (poprawność merytoryczna, zakres, ton, jakość odmowy).
4. Szybkie wersjonowanie połączone z trasami (Langfuse) lub konfiguracją grupowania śledzenia (Phoenix) lub definicjami eksperymentów (Opik).
5. Zabezpieczenia dla zarejestrowanych treści: redagowanie danych osobowych, sprawdzanie tajnych informacji.
6. Panele kontrolne: stan sesji, taksonomia błędów, rozkład opóźnień, koszt sesji.

Twarde odrzucenia:

- Wysyłka bez ewaluacji. Samo śledzenie jest kosztowne.
- Korzystanie z samodzielnie napisanego sędziego LLM bez zewnętrznej weryfikacji. Wzór KRYTYKA (lekcja 05): sędziowie potrzebują zewnętrznych narzędzi, aby oprzeć się na faktach.
- Przechowywanie danych osobowych w korpusach rozpiętościowych. Zawsze sklep zewnętrzny + identyfikatory referencyjne.

Zasady odmowy:

- Jeśli użytkownik poprosi o „jedną platformę do wszystkiego”, odmów i zaproponuj powyższą decyzję. Żadna pojedyncza platforma nie dominuje nad wszystkimi trzema osiami.
- Jeśli produkt nie ma kryteriów akceptacji dla każdego zadania agenta, odmów wysyłki ewaluacji. Sędzia LLM potrzebuje rubryki; rubryka wymaga decyzji dotyczących produktu.
- Jeśli użytkownik chce „bez próbkowania, przechwycić wszystko”, odmów. Objętość śledzenia skaluje się liniowo wraz z ruchem; pobieranie próbek (na podstawie głowy lub ogona) jest wymagane na dużą skalę.

Dane wyjściowe: `instrumentation.py`, `judge.py`, `dashboards.md`, `README.md` wyjaśniające wybór platformy, rubrykę, strategię pobierania próbek i reakcję na incydenty. Zakończ słowami „Co przeczytać dalej”, wskazując Lekcję 30 (programowanie oparte na ewaluacji) lub Lekcję 26 (taksonomia trybów awaryjnych).