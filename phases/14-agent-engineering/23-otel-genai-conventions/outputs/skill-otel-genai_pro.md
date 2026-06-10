---

name: otel-genai
description: Zintegruj agenta z konwencjami semantycznymi OpenTelemetry GenAI – spany invoke_agent, chat oraz tool_call z odpowiednimi atrybutami i bezpiecznym rejestrowaniem treści.
version: 1.0.0
phase: 14
lesson: 23
tags: [opentelemetry, genai, observability, tracing, semantic-conventions]

---

Na podstawie środowiska uruchomieniowego agenta, zaimplementuj i zintegruj konwencje semantyczne OpenTelemetry (OTel) GenAI.

Wyprodukuj:

1. Span typu `invoke_agent` dla każdego wywołania agenta. Typ spanu (Span Kind): `CLIENT` dla usług zdalnych (np. API), `INTERNAL` dla frameworków działających w procesie lokalnym. Nazwa spanu: `invoke_agent {gen_ai.agent.name}`.
2. Span typu `chat` dla wywołań LLM zawierający atrybuty: `gen_ai.operation.name=chat`, `gen_ai.provider.name`, `gen_ai.request.model` oraz `gen_ai.response.model`.
3. Span typu `tool_call` dla wywołań narzędzi zawierający atrybuty: `gen_ai.tool.name` oraz – jeśli ma to zastosowanie – `gen_ai.data_source.id` (np. baza wektorowa RAG lub zewnętrzny magazyn pamięci).
4. Konfigurowalny tryb zbierania treści: domyślnie WYŁĄCZONY (opt-in); po jego aktywacji wejścia i wyjścia powinny być zapisywane w zewnętrznym magazynie, a spany powinny rejestrować jedynie unikalne identyfikatory referencyjne (`*.reference_id`).
5. Propagację kontekstu (Context Propagation): wykorzystaj nagłówki standardu W3C trace context, aby spany generowane w różnych procesach (np. wywołania podprocesu CLI w Claude Agent SDK) łączyły się w jeden spójny ślad (trace).

Kategoryczne odrzucenia (Twarde kryteria):

- Domyślne rejestrowanie pełnych promptów i odpowiedzi wewnątrz spanów (inline). Powoduje to ryzyko wycieku danych osobowych (PII) i haseł oraz jest niezgodne ze specyfikacją OpenTelemetry.
- Brak zdefiniowania atrybutu `gen_ai.provider.name`. Może to popsuć agregację danych i wykresy na dashboardach obsługujących wielu dostawców.
- Tworzenie spanów narzędzi bez powiązania ich ze spanem nadrzędnym (Orphaned spans). Zawsze konfiguruj prawidłową relację rodzic-dziecko za pomocą aktywnego kontekstu.

Zasady odmowy wykonania usługi (Refusal rules):

- Jeśli środowisko uruchomieniowe nie pozwala na propagowanie kontekstu śledzenia między procesami, odmów. W scenariuszach korzystających z Claude Agent SDK + CLI wieloprocesowe łączenie śladów jest krytycznym wymaganiem.
- Jeśli system przetwarza dane podlegające restrykcyjnym regulacjom (np. RODO, HIPAA), kategorycznie odmów bezpośredniego rejestrowania treści w spanach. Wymagaj zapisu w zewnętrznym magazynie z rygorystyczną kontrolą dostępu.
- Jeśli środowisko nie konfiguruje zmiennej `OTEL_SEMCONV_STABILITY_OPT_IN=gen_ai_latest_experimental`, wyświetl ostrzeżenie, że nazwy atrybutów mogą ulec zmianie przy aktualizacji kolektora telemetrycznego.

Pliki wynikowe: `tracer.py`, `attributes.py`, `content_store.py`, `README.md` wyjaśniające strukturę spanów, konfigurację stabilności oraz politykę bezpiecznego zbierania treści. Zakończ sekcją „Dalsza lektura”, wskazując na Lekcję 24 (backendy obserwowalności: Langfuse, Phoenix, Opik) lub Lekcję 17 (propagacja kontekstu śledzenia w Claude Agent SDK).
