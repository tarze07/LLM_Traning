---

name: load-test-plan
description: Zaprojektuj realistyczny test obciążenia LLM — wybierz narzędzie (LLMPerf, k6, GenAI-Perf, Guidellm), zbuduj cztery wzorce (stały, rampowy, skokowy, namacalny) i bramkę w CI.
version: 1.0.0
phase: 17
lesson: 22
tags: [load-testing, llmperf, k6, genai-perf, guidellm, llm-locust, ci-gate]

---

Biorąc pod uwagę obciążenie pracą (punkt końcowy, SLA dla TTFT/TPOT/błąd), skalę docelową (współbieżność, RPS) i stan CI (brama PR lub tylko wersja), utwórz plan testów obciążeniowych.

Wyprodukuj:

1. Narzędzie. LLMPerf dla przebiegów podstawowych; k6 + rozszerzenie strumieniowe dla bramek CI; GenAI-Perf dla uruchomień referencyjnych NVIDIA; przewodnik dla dużych syntetycznych. LLM – Szarańcza tylko jeśli już jesteś na Szarańczy.
2. Szybka dystrybucja. Średnie + tokeny wejściowe stddev z rzeczywistego ruchu (jeśli są dostępne) lub opublikowanej dystrybucji (ShareGPT / HumanEval). Zabroń pętli z jednym monitem.
3. Cztery wzory. Stały, rampa, kolec, moczenie. Dla każdego: docelowy RPS, czas trwania, oczekiwany tryb awarii.
4. Brama CI. Specyficzne progi: TTFT P95 < X, 5xx < 5%, TPOT < Y. Czas działania na PR: 3-5 min.
5. Ujednolicenie metryczne. Zwróć uwagę, czy narzędzie do raportowania jest w stylu GenAI-Perf (ITL nie obejmuje TTFT), czy w stylu LLMPerf (ITL obejmuje TTFT). Wybierz jeden i bądź konsekwentny.
6. Wyjście. Plik skryptu (k6 JS, LLMPerf CLI) zapisany w repozytorium.

Twarde odrzucenia:
- Test obciążenia z jednolitymi monitami. Odmawiaj – liczby kłamią.
- Test obciążenia bez obsługi przesyłania strumieniowego. Odmów — punkty końcowe LLM domyślnie przesyłają strumieniowo.
- Porównywanie liczb pomiędzy narzędziami bez uwzględniania różnic w definicji metryki. Odmawiać.

Zasady odmowy:
- Jeśli zespół zamierza korzystać z zasobów szarańczy bez rozszerzenia LLM-Locust, odmów — pułapka GIL.
- Jeśli budżet bramki CI wynosi < 60 s na PR, odmów pełnego namaczania — zaproponuj szybki stan ustalony plus oddzielne nocne namaczanie.
- Jeśli dane dotyczące szybkiej dystrybucji są niedostępne, należy zażądać udokumentowanej opublikowanej dystrybucji (ShareGPT) i zanotować założenia.

Wynik: jednostronicowy plan z narzędziem, szybka dystrybucja, cztery wzorce z celami, progi bramek CI, wyrównanie metryk. Zakończ pojedynczym wyjściem CI: PR zielony tylko w przypadku osiągnięcia wszystkich progów, stabilność 3-biegowa.