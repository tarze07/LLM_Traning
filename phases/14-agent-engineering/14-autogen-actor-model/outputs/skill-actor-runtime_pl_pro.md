---

name: actor-runtime
description: Zbuduj środowisko uruchomieniowe modelu aktora w stylu AutoGen v0.4 z prywatnym stanem, skrzynką odbiorczą dla każdego aktora, komunikacją opartą wyłącznie na wiadomościach, izolacją błędów i kolejką komunikatów nieobsłużonych (DLQ).
version: 1.0.0
phase: 14
lesson: 14
tags: [autogen, actor-model, messaging, fault-isolation, dead-letter]

---

W oparciu o wskazane zadanie wieloagentowe stwórz środowisko uruchomieniowe modelu aktora oraz zdefiniuj niezbędnych aktorów.

Wygeneruj:

1. Typ danych `Message` z polami `sender`, `recipient`, `topic`, `body`, `mid`.
2. Klasę bazową `Actor` z metodą `receive(message, runtime)`. Stan aktora musi być w pełni prywatny.
3. Klasę `Runtime` ze współdzieloną kolejką komunikatów, metodami `send()`, `run_until_idle()` oraz obsługą kolejki DLQ. Wyjątki rzucane przez handlery powinny trafiać do DLQ i nie mogą być propagowane wyżej.
4. Jeden szablon topologii: RoundRobin (stała rotacja), Selector (dynamiczny wybór kolejnego aktora przez LLM) lub własna warstwa routingu.
5. Integrację z telemetrią dla każdego komunikatu: emitowanie spanów OTel z atrybutami `gen_ai.agent.name` oraz `gen_ai.operation.name` (zgodnie z Lekcją 23).

Kryteria odrzucenia (Hard rejects):

- Synchroniczne przekazywanie komunikatów, które blokuje nadawcę do czasu zakończenia przetwarzania przez odbiorcę. Jest to przestarzały model v0.2, który narusza zasady izolacji błędów.
- Współdzielenie modyfikowalnego stanu (shared mutable state) pomiędzy aktorami. Aktorzy mogą wymieniać informacje o swoim stanie wyłącznie za pomocą komunikatów.
- Środowisko uruchomieniowe propagujące wyjątki z procedur obsługi (handlerów). Awarie powinny być kierowane do DLQ, umożliwiając dalsze, nieprzerwane działanie pozostałych aktorów.

Zasady odmowy (Guardrails):

- Jeśli w zadaniu bierze udział tylko dwóch aktorów wymieniających komunikaty sekwencyjnie, odmów wdrożenia modelu aktora i zasugeruj prosty łańcuch promptów (Prompt Chaining z Lekcji 12). Zastosowanie modelu aktora ma uzasadnienie ekonomiczne i techniczne przy co najmniej 3 aktorach lub przy współbieżności asynchronicznej.
- Jeśli użytkownik żąda „trybu synchronicznego” w celu ułatwienia debugowania, odmów. Zamiast tego zaproponuj zaawansowane logowanie i rozproszone śledzenie (Lekcja 23).
- Jeśli zadanie sprowadza się do prostego schematu żądanie-odpowiedź z jednym modelem, zaproponuj routing (Lekcja 12) zamiast całego zespołu aktorów.

Wygenerowana struktura: pliki `message.py`, `actor.py`, `runtime.py`, `teams.py` oraz `README.md` wyjaśniający zasady działania DLQ, wybór topologii oraz integrację ze spanami OTel. Zakończ sekcją „Co czytać dalej”, odsyłając do Lekcji 25 (debata wieloagentowa – jeśli aktorzy negocjują rozwiązania), Lekcji 23 (OTel – jeśli wymagane jest zaawansowane śledzenie) lub Microsoft Agent Framework (jeśli poszukujesz oficjalnego i przyszłościowego środowiska uruchomieniowego).
