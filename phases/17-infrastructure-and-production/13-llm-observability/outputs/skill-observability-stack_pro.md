---

name: observability-stack
description: Zaprojektuj stos obserwowalności (observability) dla systemów LLM (platforma deweloperska + brama proxy + opcjonalna warstwa skalowania) w oparciu o stos technologiczny, skalę, budżet i wymagania licencyjne, a następnie zdefiniuj zestaw atrybutów OpenTelemetry GenAI.
version: 1.0.0
phase: 17
lesson: 13
tags: [observability, langfuse, langsmith, phoenix, arize, helicone, opik, opentelemetry, genai-conventions]

---

Na podstawie używanego stosu (np. LangChain, DSPy, surowy SDK), skali ruchu (liczby śladów telemetrycznych/dobę), budżetu, ograniczeń licencyjnych (tylko licencje MIT vs akceptacja rozwiązań komercyjnych) oraz wymagań dotyczących hostowania (self-hosted), opracuj plan wdrożenia systemu obserwowalności.

Wygeneruj:

1. Wybór platformy deweloperskiej. Wybierz rozwiązanie: Langfuse (OSS), LangSmith (komercyjne, zoptymalizowane pod LangChain), Opik (Comet OSS) lub brak platformy. Uzasadnij decyzję stosem technologicznym i wymaganiami licencyjnymi.
2. Wybór narzędzia telemetrycznego i bramy (Gateway). Wybierz: Helicone (brama + proxy), SigNoz (pełny monitoring APM) lub OpenLLMetry (czysta telemetria OTel). Jeśli w architekturze funkcjonuje już brama AI (AI Gateway – patrz Faza 17 · 19), zdefiniuj sposób integracji.
3. Warstwa analizy skalowalnej / jeziora danych. Opcjonalnie: Arize AX lub bezpośredni zapis do Apache Iceberg do analiz długoterminowych; Phoenix do wizualizacji dryfu (driftu) modeli w potokach RAG.
4. Konwencje semantyczne OTel GenAI. Zdefiniuj minimalny zestaw atrybutów: `gen_ai.system`, `gen_ai.request.model`, `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`, `gen_ai.request.temperature`, `gen_ai.response.finish_reasons` oraz atrybuty specyficzne dla organizacji (np. identyfikator_dzierżawcy/tenant_id, identyfikator_użytkownika/user_id, typ_zadania/task_type).
5. Polityka próbkowania (Sampling policy). Zapisuj 100% zapytań zakończonych błędem, 100% zapytań o wysokim koszcie (>0,10 USD/wywołanie) oraz N% losowych zapytań zakończonych sukcesem. Określ czas retencji dla surowych logów (np. 14 dni, 30 dni, 90 dni); zbiorcze dane statystyczne przechowuj w dłuższym horyzoncie czasowym.
6. System alertów. Zdefiniuj pięć metryk, dla których należy ustawić progi ostrzegawcze: wskaźnik błędów (error rate), opóźnienie P99 TTFT, średni koszt zapytania, współczynnik trafień cache promptów (prompt cache hit rate) oraz wskaźnik odmów (fallbacks/refusals).

Kategoryczne odrzucenia:
- Wdrażanie systemów monitorowania w oparciu o zamknięte, specyficzne dla danego dostawcy biblioteki SDK bez zapewnienia kompatybilności ze standardem OpenTelemetry (ryzyko vendor lock-in).
- Przechowywanie 100% surowych śladów telemetrycznych przy kosztach systemów klasy Datadog przekraczających 500 USD/miesiąc przy braku precyzyjnie określonych budżetów na ten cel. Bezwzględnie rekomenduj wdrożenie polityki próbkowania.
- Ignorowanie specyfikacji konwencji semantycznych OpenTelemetry GenAI. Wspólny standard jest kluczowy dla interoperacyjności systemów w 2026 roku.

Zasady odmowy wdrożenia (odrzucenie rekomendacji):
- Jeśli dobowy wolumen ruchu przekracza 5 milionów śladów telemetrycznych, a zespół wymaga wdrożenia monitoringu w oparciu o pełną retencję danych w Datadog, odrzuć plan do czasu przedstawienia szczegółowej prognozy kosztów.
- Jeśli zespół wymaga stosowania wyłącznie otwartych licencji MIT, a w planie wskazano komercyjne rozwiązanie LangSmith, odrzuć rekomendację i wskaż Langfuse jako odpowiednik na licencji MIT.
- Jeśli zespół nie posiada wdrożonej bramy AI i zdecyduje się na wybór Helicone jako bramy oraz systemu monitoringu, zaakceptuj wybór – serwer proxy z powodzeniem obsługuje oba te zadania przy ruchu do ok. 500 RPS (zagadnienia skalowania bram sieciowych pokrywa Faza 17 · 19).

Wynik: jednostronicowy plan wdrożenia zawierający: nazwę platformy deweloperskiej, wybrane narzędzie bramowe, specyfikację warstwy jeziora danych (jeśli ma zastosowanie), zestaw atrybutów standardu OTel, reguły próbkowania oraz definicję pięciu alertów. Zakończ pojedynczą kluczową metryką kontrolną: odsetek wywołań LLM z w pełni uzupełnionymi atrybutami OTel GenAI w ciągu ostatnich 7 dni.
