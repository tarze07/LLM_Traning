# Środowiska uruchomieniowe (Production Runtimes): Kolejki, Zdarzenia, Cron

> W środowiskach produkcyjnych agenci działają w ramach sześciu głównych modeli uruchomieniowych: żądanie-odpowiedź (request-response), przesyłanie strumieniowe (streaming), trwałe wykonywanie (durable execution), operacje w tle oparte na kolejkach (queue-based background), sterowanie zdarzeniami (event-driven) oraz zadania cykliczne (scheduled/cron). Dobór odpowiedniego modelu powinien poprzedzać wybór konkretnego frameworka. We wszystkich tych modelach kluczową rolę odgrywa obserwowalność.

**Typ:** Nauka
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 14 · 13 (LangGraph), Faza 14 · 22 (Głos)
**Czas:** ~60 minut

## Cele nauczania

- Wymień sześć środowisk uruchomieniowych i dopasuj je do odpowiednich frameworków oraz wzorców produktowych.
- Wyjaśnij znaczenie trwałego wykonywania (durable execution) w LangGraph dla długoterminowych procesów agentowych.
- Opisz specyfikę środowiska sterowanego zdarzeniami oraz przypadki użycia platformy Claude Managed Agents.
- Wyjaśnij, dlaczego dokładna obserwowalność (observability) jest kluczowym filarem wdrażania wieloetapowych agentów.

## Problem

W środowisku produkcyjnym agenci napotykają problemy, których nie widać w notatnikach Jupyter: limity czasu sieciowego (timeouts) przy 37. kroku, zerwanie połączenia przez użytkownika w połowie interakcji głosowej, przerwanie długiego zadania cron po restarcie serwera czy wyczerpanie pamięci przez worker działający w tle. Wybór odpowiedniego modelu uruchomieniowego decyduje o tym, czy aplikacja będzie potrafiła wyjść z takich sytuacji bez utraty danych.

## Koncepcja

### Żądanie-odpowiedź (Request-response)

- Synchroniczne zapytania HTTP. Użytkownik czeka na zakończenie przetwarzania zadania.
- Stosuje się wyłącznie do bardzo krótkich operacji (poniżej 30 sekund).
- Narzędzia: Agno (Python + FastAPI), Mastra (TypeScript + Express/Hono/Fastify/Koa).
- Obserwowalność: standardowe logi HTTP oraz spany OpenTelemetry (OTel spans).

### Przesyłanie strumieniowe (Streaming)

- Przesyłanie danych w czasie rzeczywistym za pomocą SSE (Server-Sent Events) lub protokołu WebSocket.
- Narzędzie LiveKit rozszerza ten schemat o standard WebRTC na potrzeby komunikacji głosowej i wideo (lekcja 22).
- Narzędzia: dowolny framework obsługujący streaming połączony z aplikacją kliencką czytającą strumień SSE/WS.
- Obserwowalność: czas trwania pojedynczych pakietów (chunks), czas do wygenerowania pierwszego tokena (TTFT – Time to First Token) oraz opóźnienie z długim ogonem (tail latency).

### Trwałe wykonywanie (Durable execution)

- Stan agenta jest zapisywany w bazie danych po każdym wykonanym kroku (checkpointing); w razie awarii serwera proces wznawia działanie od ostatniego poprawnego stanu.
- Model aktorowy we frameworku AutoGen v0.4 pozwala na izolowanie awarii do poziomu pojedynczego agenta (lekcja 14).
- Jest to kluczowa cecha wyróżniająca system LangGraph (lekcja 13).
- Rozwiązanie niezbędne przy nieznanej liczbie kroków oraz wysokim koszcie ponownego uruchomienia procesu.

### Operacje w tle oparte na kolejkach (Queue-based / background)

- Zadanie trafia do kolejki wiadomości, procesy robocze (workers) pobierają je asynchronicznie, a wyniki są zwracane poprzez webhooki lub model pub/sub.
- Niezbędne w przypadku agentów wykonujących długie zadania (od kilkudziesięciu do setek kroków, np. przy obsłudze interfejsu graficznego za pomocą modeli Anthropic).
- Narzędzia: Celery (Python), BullMQ (Node.js), AWS SQS + Lambda, własne implementacje brokerów wiadomości.
- Obserwowalność: długość kolejki, czas przetwarzania zadań, rozmiar i analiza kolejki wiadomości niedoręczonych (DLQ – Dead-letter queue).

### Sterowane zdarzeniami (Event-driven)

- Agenci subskrybują określone wyzwalacze (triggers), np. odebranie e-maila, utworzenie Pull Requestu czy zakończenie innego zadania.
- Usługa Claude Managed Agents zapewnia takie środowisko w pełni zarządzane przez dostawcę (lekcja 17).
- Moduł CrewAI Flows (lekcja 15) ułatwia budowanie deterministycznych grafów zdarzeń.
- Obserwowalność: źródło zdarzenia (provenance), opóźnienie reakcji (event-to-start latency) oraz czas działania agenta (agent execution latency).

### Zadania cykliczne (Scheduled / Cron)

- Agenci uruchamiani okresowo według harmonogramu.
- Zaleca się łączenie z trwałym wykonywaniem (durable execution), aby przerwane w nocy zadanie mogło zostać automatycznie wznowione przy kolejnym uruchomieniu.
- Narzędzia: Kubernetes CronJob zintegrowany z trwałym frameworkiem lub usługi typu Render cron / Vercel cron.

### Wdrożenia produkcyjne w 2026 roku

- **CrewAI Flows:** do procesów sterowanych zdarzeniami.
- **Agno (FastAPI):** do budowy bezstanowych mikroserwisów w Pythonie.
- **Mastra (Express, Hono, Fastify):** do osadzania procesów agentowych w aplikacjach Node.js.
- **Pipecat / LiveKit Cloud:** do obsługi potoków głosowych w czasie rzeczywistym (lekcja 22).
- **Claude Managed Agents:** do długich, asynchronicznych zadań hostowanych bezpośrednio przez Anthropic.

### Obserwowalność jako warunek konieczny (Load-bearing)

Bez wdrożenia standardu OpenTelemetry GenAI (lekcja 23) oraz integracji z platformami takimi jak Langfuse, Phoenix czy Opik (lekcja 24), niemożliwe jest debugowanie agenta, który uległ awarii np. w 45. kroku wieloetapowego procesu. W systemach produkcyjnych zaawansowane śledzenie (tracing) decyduje o tym, czy zespół potrafi zdiagnozować błąd w kilka minut, czy zmuszony jest do ponownego odtwarzania całej sesji z włączonym bardziej szczegółowym logowaniem (verbose).

### Gdzie zawodzą poszczególne środowiska uruchomieniowe

- **Niewłaściwy dobór modelu:** Wybór synchronicznego modelu „żądanie-odpowiedź” dla zadań trwających 5 minut. Skutkuje to zrywaniem połączeń przez klientów i przepełnieniem serwerów przez nakładające się ponowne wywołania (retries).
- **Brak obsługi kolejki DLQ:** Ignorowanie obsługi wiadomości niedoręczonych. Powoduje to, że zadania, które uległy awarii, bezpowrotnie znikają z systemu.
- **Brak śledzenia zadań w tle:** Uruchamianie workerów bez eksportu śladów (traces). Wszelkie błędy jakościowe modeli pozostają niewykryte, dopóki klienci nie zaczną zgłaszać reklamacji.
- **Pominięcie zapisu trwałego stanu (durable state):** Próba uruchamiania zadań trwających dłużej niż 30 sekund bez możliwości wznowienia od punktu awarii. Każdy błąd sieciowy zmusza system do kosztownego restartu od zera.

## Zbuduj to

Plik `code/main.py` zawiera demonstrację obsługi wielu formatów uruchomieniowych w oparciu o bibliotekę standardową:

- Synchroniczny punkt końcowy (request-response).
- Generator obsługujący przesyłanie strumieniowe (streaming).
- Moduł roboczy (worker) z obsługą kolejki zadań i rejestrem wiadomości niedoręczonych (DLQ).
- Rejestr wyzwalaczy dla zdarzeń (event trigger registry).
- Harmonogram zadań cyklicznych (cron-shaped scheduler).

Uruchomienie:

```bash
python3 code/main.py
```

Dane wyjściowe: pięć śladów (traces) pokazujących zachowanie systemu przy realizacji tego samego zadania w różnych modelach uruchomieniowych. Rdzeń logiki agenta pozostaje bez zmian, modyfikacji ulega jedynie środowisko wykonawcze. Szósta forma – trwałe wykonywanie (durable execution) – została szczegółowo omówiona w lekcji 13 przy analizie mechanizmu punktów kontrolnych (checkpointing) w LangGraph.

## Użyj tego

- **Żądanie-odpowiedź (Request-response):** do synchronicznych i krótkich interakcji, np. w komunikatorach tekstowych.
- **Przesyłanie strumieniowe (Streaming):** do stopniowego wyświetlania wygenerowanych odpowiedzi w czasie rzeczywistym.
- **Trwałe wykonywanie (Durable execution):** do złożonych, wieloetapowych procesów o długim horyzoncie czasowym.
- **Kolejki (Queue-based):** do asynchronicznego przetwarzania zadań wsadowych (batch processing) lub operacji w tle.
- **Sterowanie zdarzeniami (Event-driven):** do reagowania na zmiany stanów w zewnętrznych systemach (np. webhooki).
- **Zadania cykliczne (Cron):** do rutynowych zadań administracyjnych (np. czyszczenie bazy danych, synchronizacja pamięci czy raportowanie kosztów).

## Wyślij to

Plik `outputs/skill-runtime-shape.md` pomaga w doborze optymalnego modelu uruchomieniowego dla konkretnego procesu biznesowego oraz opisuje proces integracji z systemami obserwowalności.

## Ćwiczenia

1. Przeprojektuj swoją pętlę ReAct (z lekcji 01) tak, aby przetestować jej zachowanie w każdym z sześciu opisanych modeli uruchomieniowych. Zwróć uwagę na różnice w obsłudze błędów.
2. Zaimplementuj obsługę wiadomości niedoręczonych (DLQ) w środowisku kolejkowym. Przetestuj działanie systemu, symulując 10-procentowy wskaźnik błędów, i zaobserwuj przyrost zadań trafiających do kolejki DLQ.
3. Stwórz agenta cyklicznego (cron), który raz na dobę analizuje logi i agreguje 20 najczęstszych akcji podjętych przez pozostałe agenty w systemie.
4. Wprowadź mechanizm kontroli przepływu (backpressure) do procesu przesyłania strumieniowego. Powinien on wstrzymać działanie agenta, jeśli po stronie klienta wystąpią opóźnienia w przetwarzaniu danych. Jak taka kontrola wpływa na budżet czasu przydzielony na pojedynczą turę (turn budget)?
5. Zapoznaj się z dokumentacją usługi Claude Managed Agents. Zdefiniuj scenariusze, w których hostowanie własnego środowiska wykonawczego dla długotrwałych zadań staje się nieopłacalne w porównaniu z rozwiązaniem zarządzanym przez Anthropic.

## Kluczowe pojęcia

| Termin | Co potocznie się mówi | Co to oznacza w rzeczywistości |
|------|----------------|------------------------|
| Żądanie-odpowiedź (Request-response) | „Zapytanie synchroniczne” | Użytkownik oczekuje na wynik; stosowane wyłącznie dla zadań trwających poniżej 30 sekund |
| Przesyłanie strumieniowe (Streaming) | „Strumień SSE / WebSocket” | Stopniowe dostarczanie danych do klienta; skraca odczuwalny czas odpowiedzi (UX) |
| Trwałe wykonywanie (Durable execution) | „Wznawianie po błędach” | System zapisuje punkty kontrolne stanu; w razie awarii serwera proces startuje od ostatniego checkpointu |
| Model kolejkowy (Queue-based) | „Asynchroniczne workery” | Podział architektury na producenta zadań, kolejkę wiadomości, pulę workerów oraz kolejkę DLQ |
| Sterowanie zdarzeniami (Event-driven) | „Reagowanie na webhooki” | Uruchamianie logiki agenta w odpowiedzi na sygnały z systemów zewnętrznych |
| DLQ (Dead-letter queue) | „Kolejka błędnych zadań” | Wydzielona baza danych/kolejka przechowująca zadania, których nie udało się pomyślnie przetworzyć |
| Claude Managed Agents | „Zarządzani agenci Anthropic” | Hostowane przez Anthropic środowisko do wykonywania długich zadań wieloetapowych (z wbudowanym buforowaniem i optymalizacją) |

## Dalsza lektura

- [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview) – szczegółowe informacje o wdrażaniu mechanizmów trwałego wykonywania (durable execution)
- [Claude Managed Agents overview](https://platform.claude.com/docs/en/managed-agents/overview) – opis architektury hostowanej dla asynchronicznych operacji długoterminowych
- [Anthropic, Introducing computer use](https://www.anthropic.com/news/3-5-models-and-computer-use) – charakterystyka zadań wymagających setek kroków wykonania
- [AutoGen v0.4 (Microsoft Research)](https://www.microsoft.com/en-us/research/articles/autogen-v0-4-reimagining-the-foundation-of-agentic-ai-for-scale-extensibility-and-robustness/) – omówienie izolacji błędów na poziomie agenta opartego na modelu aktorowym
