---

name: observability-stack
description: Wybierz stos obserwowalności LLM (platforma programistyczna + brama + opcjonalna warstwa skalowania), biorąc pod uwagę stos, skalę, budżet i stan licencji, a następnie zdefiniuj zestaw atrybutów OpenTelemetry GenAI.
version: 1.0.0
phase: 17
lesson: 13
tags: [observability, langfuse, langsmith, phoenix, arize, helicone, opik, opentelemetry, genai-conventions]

---

Biorąc pod uwagę stos (LangChain / DSPy / surowy SDK), skalę (ślady/dzień), budżet, stan licencji (tylko MIT vs komercyjna OK) i wymagania dotyczące własnego hosta, utwórz plan obserwowalności.

Wyprodukuj:

1. Wybór platformy programistycznej. Langfuse (OSS), LangSmith (pierwsza reklama LangChain), Opik (Comet OSS) lub żaden. Uzasadnij stosem i licencją.
2. Wybór bramy/telemetrii. Helicone (proxy + bramka), SigNoz (pełny APM), OpenLLMetry (czysty Otel). Jeśli już korzystasz z bramy AI (faza 17 · 19), nazwij integrację.
3. Warstwa łusek/jeziora. Fakultatywny; Arize AX lub surowy Iceberg do analiz długoterminowych, Phoenix do dryfu RAG.
4. Konwencje Otel GenAI. Określ minimalny zestaw atrybutów: `gen_ai.system`, `gen_ai.request.model`, `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`, `gen_ai.request.temperature`, `gen_ai.response.finish_reasons` oraz specyficzny dla organizacji (identyfikator_dzierżawcy, identyfikator_użytkownika, zadanie).
5. Polityka pobierania próbek. 100% błędów, 100% wysokich kosztów (>0,10 USD/połączenie), częstotliwość próbkowania powodzenia N%. Okno surowe (14d / 30d / 90d). Agregaty przechowywane dłużej.
6. Alarmowanie. Pięć wskaźników, które muszą mieć alerty: stopa błędów, P99 TTFT, koszt/żądanie, współczynnik trafień w pamięci podręcznej podpowiedzi, współczynnik odmów.

Twarde odrzucenia:
- Instrumentacja wewnątrz zestawu SDK specyficznego dla platformy bez rezerwy Otel. Odmów — blokowanie frameworka.
- Utrzymywanie 100% śladów przy cenach klasy Datadog > 500 USD/mies. przy nieuregulowanym obciążeniu pracą. Odmów – zaleć pobieranie próbek.
- Ignorowanie konwencji OpenTelemetry GenAI. Odmów — wymaga tego interop 2026.

Zasady odmowy:
- Jeśli śladów/dzień > 5M, a zespół nalega na pełne zatrzymanie Datadog, odmów bez prognozy kosztów.
- Jeśli zespół pracuje wyłącznie na MIT i wybierze LangSmitha, odmów — Langfuse jest odpowiednikiem MIT.
- Jeśli zespół nie ma bramy AI i wybierze Helicone jako bramę ORAZ obserwowalność, zaakceptuj — serwer proxy pełni także funkcję bramy do ~500 RPS (faza 17 · 19 obejmuje skalę bramy).

Dane wyjściowe: jednostronicowy plan nazewnictwa platformy deweloperskiej, bramy, warstwy skalowania (jeśli istnieje), zestawu atrybutów Otel, reguły próbkowania, pięciu alertów. Zakończ pojedynczą metryką sygnalizującą dryf stosu: procent wywołań LLM z pełnymi atrybutami Otel GenAI w ciągu ostatnich 7 dni.