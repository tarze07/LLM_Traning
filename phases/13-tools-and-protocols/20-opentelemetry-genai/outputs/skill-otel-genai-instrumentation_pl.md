---

name: otel-genai-instrumentation
description: Utwórz plan oprzyrządowania dla bazy kodu agenta, aby emitować kompleksowo rozwiązania Otel GenAI.
version: 1.0.0
phase: 13
lesson: 19
tags: [otel, observability, gen-ai, tracing]

---

Mając bazę kodu agenta (wywołania LLM, wysyłka narzędzi, klient MCP, agenci podrzędni), utwórz plan oprzyrządowania Otel GenAI.

Wyprodukuj:

1. Hierarchia rozpiętości. Główny `agent.invoke_agent` (WEWNĘTRZNY) i dzieci: `llm.chat` (KLIENT), `tool.execute` (WEWNĘTRZNY), `mcp.call` (KLIENT), `subagent.invoke` (WEWNĘTRZNY).
2. Lista kontrolna atrybutów dla każdego zakresu. `gen_ai.operation.name`, `gen_ai.provider.name`, `gen_ai.request.model`, `gen_ai.response.model`, `gen_ai.usage.*`, `gen_ai.tool.name`, `gen_ai.agent.name`.
3. Reguła propagacji. Wstrzykuj Traceparent W3C przy każdym zdalnym połączeniu; dla MCP stdio użyj `_meta.traceparent` jako pola tymczasowego.
4. Polityka przechwytywania treści. Domyślnie wyłączone; dokument, który umożliwia env var; wymienić ryzyko umożliwiające identyfikację osób.
5. Wybór eksportera. Jaeger / Tempo / Langfuse / Phoenix / Datadog / Honeycomb; OTLP jako przewód.

Twarde odrzucenia:
- W jakimkolwiek planie brakuje propagacji śladów przez granice MCP lub podagenta.
- Dowolny plan z domyślnie włączonym przechwytywaniem treści. Wycieki podpowiedzi i informacje umożliwiające identyfikację.
- Dowolny plan, który emituje dowolne atrybuty niestandardowe bez `gen_ai.` lub wyraźnego przedrostka dostawcy.

Zasady odmowy:
- Jeśli baza kodu korzysta z frameworka z wbudowaną automatyczną instrumentacją Otel (Pydantic AI, LangGraph, AgentOps), zalecamy najpierw hak frameworka.
— Jeśli backend eksportera działa lokalnie, a zespół nie ma wsparcia w zakresie SRE, zarekomenduj zarządzany backend.
— Jeśli użytkownik poprosi o przechwycenie treści w celu debugowania produktu, odmów bez wpisywania zasad zgody i potoku redagowania informacji umożliwiających identyfikację.

Dane wyjściowe: jednostronicowy plan z hierarchią zakresu, listą kontrolną atrybutów dla każdego zakresu, regułą propagacji, polityką przechwytywania treści i wyborem eksportera. Zakończ najwyższą metryką, o której ma być alert (zwykle p95 `gen_ai.client.operation.duration`).