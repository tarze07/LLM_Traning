---

name: otel-genai-instrumentation
description: Opracuj plan oprzyrządowania telemetrycznego (instrumentation plan) dla bazy kodu agenta w celu emitowania kompleksowych śladów telemetrycznych OTel GenAI.
version: 1.0.0
phase: 13
lesson: 19
tags: [otel, observability, gen-ai, tracing]

---

Na podstawie struktury bazy kodu agenta (zapytania LLM, wywołania narzędzi, klient MCP, subagenty) opracuj plan oprzyrządowania telemetrycznego OTel GenAI.

Wygeneruj następujące sekcje:

1. Hierarchia zakresów (Spans). Zdefiniuj zakres główny `agent.invoke_agent` (INTERNAL) oraz zakresy podrzędne: `llm.chat` (CLIENT), `tool.execute` (INTERNAL), `mcp.call` (CLIENT) oraz `subagent.invoke` (INTERNAL).
2. Lista kontrolna atrybutów dla każdego zakresu. Pola telemetryczne do wypełnienia, w tym: `gen_ai.operation.name`, `gen_ai.provider.name`, `gen_ai.request.model`, `gen_ai.response.model`, `gen_ai.usage.*`, `gen_ai.tool.name` oraz `gen_ai.agent.name`.
3. Reguły propagacji kontekstu. Wstrzykiwanie nagłówka W3C traceparent przy każdym połączeniu zdalnym; dla transportu MCP stdio użyj tymczasowego pola `_meta.traceparent`.
4. Polityka przechwytywania treści. Domyślne wyłączenie rejestrowania treści; opis sposobu aktywacji za pomocą zmiennej środowiskowej wraz ze wskazaniem ryzyka wycieku danych osobowych (PII).
5. Wybór eksportera. Integracja z systemami: Jaeger, Tempo, Langfuse, Phoenix, Datadog lub Honeycomb, z wykorzystaniem protokołu OTLP jako standardu transportu.

Kategoryczne odrzucenia:
- Dowolny plan pozbawiony propagacji kontekstu śledzenia (tracing propagation) przez granice MCP lub subagentów.
- Dowolny plan z domyślnie włączonym przechwytywaniem treści (ryzyko wycieku treści zapytań [prompts] oraz danych osobowych [PII]).
- Dowolny plan emitujący niestandardowe atrybuty bez prefiksu `gen_ai.` lub jawnego prefiksu dostawcy.

Reguły odmowy:
- Jeśli baza kodu opiera się na frameworku posiadającym wbudowane, automatyczne oprzyrządowanie OTel (np. Pydantic AI, LangGraph, AgentOps), zalecaj w pierwszej kolejności użycie natywnych mechanizmów tego frameworka.
- Jeśli system monitorowania (exporter backend) ma być uruchamiany lokalnie, a zespół nie posiada dedykowanego wsparcia inżynierów SRE, zarekomenduj wybór usługi zarządzanej (SaaS).
- Jeśli użytkownik żąda przechwytywania treści zapytań w środowisku produkcyjnym w celach debugowania, odrzuć żądanie, o ile nie zostanie zdefiniowana polityka zgód oraz potok (pipeline) anonimizacji danych osobowych (PII).

Format wyjściowy: Jednostronicowy plan wdrożenia zawierający hierarchię zakresów, listę kontrolną atrybutów dla każdego z nich, reguły propagacji kontekstu, politykę przechwytywania treści oraz rekomendacje dotyczące eksportera. Na końcu wskaż kluczową metrykę, dla której należy skonfigurować alerty (np. percentyl p95 czasu trwania operacji: `gen_ai.client.operation.duration`).
