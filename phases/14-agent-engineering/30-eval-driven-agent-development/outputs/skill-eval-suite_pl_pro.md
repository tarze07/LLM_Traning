---
name: eval-suite
description: Budowa trzywarstwowego pakietu ewaluacyjnego (statyczne benchmarki, niestandardowe testy offline oraz testy online na produkcji) opartego na architekturze ewaluator-optymalizator z integracją z potokami CI (CI gates).
version: 1.0.0
phase: 14
lesson: 30
tags: [evaluation, ci, regression, benchmarks, llm-judge]
---

Mając dany produkt agentowy, stwórz trzywarstwowy zestaw procedur ewaluacyjnych zintegrowany z procesem ciągłej integracji (CI/CD).

Zakres wdrożenia:

1. **Warstwa statycznych benchmarków:** Integracja co najmniej jednego uznanego benchmarku branżowego adekwatnego do domeny projektu (np. SWE-bench Verified dla zadań programistycznych, BFCL V4 dla wywołań narzędzi, WebArena dla aplikacji webowych, OSWorld dla zadań systemowych/desktopowych lub GAIA dla ogólnych zadań asystenckich). Raportowane wyniki powinny zawsze uwzględniać warianty zweryfikowane przez człowieka (human-audited scores).
2. **Warstwa niestandardowych testów offline:** Wdrożenie co najmniej jednej metryki jakościowej opartej na LLM jako sędzim (LLM-as-a-judge) z precyzyjną rubryką oceny (np. jakość odmowy odpowiedzi, ton wypowiedzi, poprawność faktograficzna). Zaimplementowanie co najmniej jednego testu opartego na wykonaniu kodu (execution-based) w celu weryfikacji poprawności działania agenta w czasie rzeczywistym. Wdrożenie przynajmniej jednej metody porównywania ścieżki działania z trajektorią wzorcową (gold path).
3. **Warstwa testów online (produkcyjnych):** Wdrożenie mechanizmów analizy logów produkcyjnych (odtwarzanie sesji/session replays), alertów z systemów zabezpieczających (guardrails) oraz śledzenia kosztów i opóźnień każdego kroku wnioskowania za pomocą OpenTelemetry (OTel GenAI spans, patrz lekcja 23).
4. **Moduł uruchomieniowy ewaluator-optymalizator (Evaluator-optimizer runner):** Implementacja pętli iteracyjnej w schemacie Propose-Judge-Refine (generowanie - ocena - poprawianie) zdefiniowanej z limitem rund (round cap).
5. **Bramki CI (CI gates):** Zautomatyzowany krok w potoku CI blokujący wdrożenie kodu, jeśli regresja dokładności w stosunku do linii bazowej (baseline) przekroczy założony próg (np. >=5%). Powinien on również śledzić trendy jakościowe systemu w czasie (baseline over time).
6. **Tabela mapowania przypadków testowych (Case mapping):** Opracowanie spisu historycznych trybów awarii i wdrożonych zabezpieczeń (guardrails) powiązanego z konkretnymi lekcjami Fazy 14, tak aby każda reguła posiadała co najmniej jeden reprezentatywny przypadek testowy w zestawie ewaluacyjnym.

Kryteria odrzucenia (Hard Rejects):

- Wdrażanie pakietu ewaluacyjnego bez zdefiniowanej i wersjonowanej linii bazowej (baseline). Bez punktu odniesienia niemożliwe jest wykrycie regresji w testach.
- Stosowanie sędziego LLM (LLM-as-a-judge) bez mechanizmów uziemiania (grounding) do bazy wiedzy w przypadku zadań faktograficznych. Niezbędne jest użycie narzędzi weryfikacji zgodnie z wzorcem CRITIC (lekcja 05).
- Obecność niedeterministycznych i niestabilnych testów (flaky tests) bez zamrożonych ziaren losowości (pinned seeds) lub zapisanych migawek stanu systemu (snapshots). Fałszywe alarmy (false alarms) w CI niszczą zaufanie zespołu deweloperskiego do całego systemu testowego.

Zasady odmowy (Refusal Rules):

- Jeśli użytkownik żąda stworzenia testów pokrywających wyłącznie ścieżki optymistyczne („just the happy path”), odmów. Pakiet ewaluacyjny musi obowiązkowo zawierać scenariusze obsługi błędów i nietypowych zachowań zdefiniowane w oparciu o tryby awarii (lekcja 26).
- Jeśli użytkownik wnioskuje o wdrożenie bramki CI bez zdefiniowania testów ewaluacyjnych (evals) działających na realnych danych, odmów. Ślepe bramki bez pokrycia testowego nie zapobiegają regresji.
- Jeśli projekt opiera się wyłącznie na sędziach LLM (all LLM-judges) do weryfikacji zadań deterministycznych, odmów. Wszędzie tam, gdzie to możliwe, należy stosować obiektywne testy programistyczne oparte na wykonaniu kodu (execution-based).

Dane wyjściowe: Struktura katalogów `cases/benchmarks/`, `cases/custom/`, `cases/online/` z odpowiednimi plikami konfiguracyjnymi, skrypt uruchomieniowy ewaluatora (`runner.py`), skrypt bramki integracyjnej (`ci_gate.py`), definicje rubryk oceny (rubrics), zapisane wyniki bazowe (baselines) oraz tabela mapowania (mapping table) wiążąca lekcje Fazy 14 z testami. Zakończ sekcją „Co przeczytać dalej”, odsyłającą do lekcji 24 (Backendy obserwowalności), lekcji 26 (Tryby awarii) oraz lekcji 23 (OTel).
