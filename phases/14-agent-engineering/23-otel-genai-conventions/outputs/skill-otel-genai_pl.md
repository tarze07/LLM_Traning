---

name: otel-genai
description: Przystosuj agenta do konwencji semantycznych OpenTelemetry GenAI — zakresy invoke_agent, chat, Tool_call z poprawnymi atrybutami i przechwytywaniem treści po wyrażeniu zgody.
version: 1.0.0
phase: 14
lesson: 23
tags: [opentelemetry, genai, observability, tracing, semantic-conventions]

---

Biorąc pod uwagę czas działania agenta, połącz konwencje semantyczne Otel GenAI.

Wyprodukuj:

1. Zakres `invoke_agent` na uruchomienie agenta. Miły KLIENT w przypadku usług zdalnych agentów, WEWNĘTRZNY w przypadku usług w toku. Nazwa: `invoke_agent {gen_ai.agent.name}`.
2. Zakres `chat` na połączenie LLM z `gen_ai.operation.name=chat`, `gen_ai.provider.name`, `gen_ai.request.model`, `gen_ai.response.model`.
3. Zakres `tool_call` na wywołanie narzędzia z `gen_ai.tool.name` i, jeśli ma to zastosowanie, `gen_ai.data_source.id` (korpus RAG/magazyn pamięci).
4. Włącz przechwytywanie treści: domyślnie WYŁĄCZONE; gdy jest włączony, przechowuj wejścia/wyjścia na zewnątrz i zapisuj `*.reference_id` na przęsłach.
5. Propagacja kontekstu: użyj nagłówków kontekstu śledzenia W3C, aby przebiegi wielu procesów (podproces Claude Agent SDK CLI) połączyły się w jeden ślad.

Twarde odrzucenia:

- Domyślne przechwytywanie pełnych podpowiedzi/wyjść w trybie inline. Ryzyko wycieku danych osobowych i tajemnic; narusza również specyfikację.
- Brakuje `gen_ai.provider.name`. Pulpity nawigacyjne wielu dostawców ulegają awarii.
- Rozpiętości narzędzi sierocych. Zawsze ustawiaj relację rodzic-dziecko poprzez aktywny kontekst.

Zasady odmowy:

- Jeśli środowisko wykonawcze nie może propagować kontekstu pomiędzy granicami procesu, odmów. W przypadku użytkowników Claude Agent SDK + CLI wymagane jest wieloprocesowe łączenie śledzenia.
- Jeśli produkt podlega ograniczeniom regulacyjnym (HIPAA, RODO), odmów przechwytywania treści w trybie online. Sklep zewnętrzny wyłącznie z kontrolą dostępu.
- Jeśli backend nie ustawia `OTEL_SEMCONV_STABILITY_OPT_IN=gen_ai_latest_experimental`, ostrzegaj: nazwy atrybutów mogą ulec zmianie po aktualizacji modułu zbierającego.

Dane wyjściowe: `tracer.py`, `attributes.py`, `content_store.py`, `README.md` wyjaśniające strukturę zakresu, zgodę na stabilność i zasady przechwytywania treści. Zakończ słowami „Co przeczytać dalej”, wskazując Lekcję 24 (backendy: Langfuse, Phoenix, Opik) lub Lekcję 17 dotyczącą propagacji kontekstu śledzenia zestawu SDK Claude Agent.