---

name: load-test-plan
description: Zaprojektuj realistyczny test obciążenia dla LLM – wybierz narzędzie (LLMPerf, k6, GenAI-Perf, Guidellm), skonfiguruj cztery schematy (stały, narastający, skokowy, długotrwały) oraz bramkę w procesie CI.
version: 1.0.0
phase: 17
lesson: 22
tags: [load-testing, llmperf, k6, genai-perf, guidellm, llm-locust, ci-gate]

---

Na podstawie charakterystyki obciążenia (endpoint, SLA dla TTFT/TPOT/błędów), docelowej skali (współbieżność, RPS) oraz integracji z CI (bramka na poziomie PR lub tylko wydania), przygotuj plan testów obciążeniowych.

Wygeneruj:

1. Narzędzie: LLMPerf do testów bazowych; k6 + rozszerzenie streamingowe dla bramek CI; GenAI-Perf do referencyjnych testów NVIDIA; guidellm do generowania syntetycznego obciążenia na dużą skalę. LLM-Locust dopuszczalny tylko wtedy, gdy zespół korzysta już z Locusta.
2. Rozkład promptów: Średnia (mean) i odchylenie standardowe (stddev) liczby tokenów wejściowych na podstawie rzeczywistego ruchu (jeśli są dostępne) lub publicznych zbiorów danych (ShareGPT / HumanEval). Zabroń stosowania pętli z jednym, powtarzającym się promptem.
3. Cztery schematy obciążenia: Stały (steady state), narastający (ramp), skokowy (spike) i długotrwały (soak). Dla każdego określ: docelowy RPS, czas trwania oraz oczekiwany tryb awarii.
4. Bramka CI: Konkretne progi akceptacji, np. P95 TTFT < X, błędy 5xx < 5%, TPOT < Y. Czas trwania testu na poziomie PR: 3-5 minut.
5. Spójność metryk: Zwróć uwagę, czy dane raportowane są w standardzie GenAI-Perf (gdzie ITL nie obejmuje TTFT), czy LLMPerf (gdzie ITL obejmuje TTFT). Wybierz jedno podejście i stosuj je konsekwentnie.
6. Rezultat: Plik skryptu (np. scenariusz k6 w JS, polecenie LLMPerf CLI) umieszczony w repozytorium.

Kryteria odrzucenia planu (Hard rejects):
- Testy obciążenia z jednolitymi promptami: Odrzuć – uzyskiwane wyniki będą zafałszowane.
- Testy obciążenia bez obsługi streamingu: Odrzuć – endpointy LLM domyślnie przesyłają dane strumieniowo.
- Porównywanie wyników między różnymi narzędziami bez uwzględnienia różnic w definicjach metryk: Odrzuć.

Zasady odrzucenia:
- Jeśli zespół planuje używać standardowego Locusta bez rozszerzenia LLM-Locust, odrzuć plan – ryzyko wpadnięcia w pułapkę GIL.
- Jeśli czas budowania w bramce CI jest ograniczony do < 60 sekund na PR, odrzuć uruchomienie pełnego testu długotrwałego (soak test) – zamiast tego zaproponuj szybki test stanu ustalonego, a test długotrwały przenieś do harmonogramu nocnego.
- Jeśli rzeczywisty rozkład promptów jest niedostępny, wymagaj użycia udokumentowanego publicznego zbioru danych (np. ShareGPT) i odnotuj to założenie.

Wynik: Jednostronicowy plan zawierający wybrane narzędzie, rozkład promptów, cztery schematy obciążenia z celami, progi dla bramki CI oraz ujednolicenie metryk. Na końcu dodaj regułę zaliczenia testów w CI: status Pull Requestu staje się "zielony" tylko po spełnieniu wszystkich progów w trzech kolejnych próbach (stabilność wyników).
