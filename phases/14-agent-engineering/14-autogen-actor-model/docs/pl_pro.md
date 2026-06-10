# AutoGen v0.4: Model aktora i architektura agentów

> AutoGen v0.4 (Microsoft Research, styczeń 2025 r.) to architektura orkiestracji agentów przeprojektowana wokół modelu aktora. Wprowadza asynchroniczną wymianę komunikatów, agentów sterowanych zdarzeniami, izolację błędów oraz natywną współbieżność. Framework znajduje się obecnie w trybie utrzymania (maintenance), a jego oficjalnym następcą jest Microsoft Agent Framework (w wersji public preview od października 2025 r.).

**Typ:** Ucz się + Buduj
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 14 · 01 (Pętla agenta), Faza 14 · 12 (Wzorce przepływu pracy)
**Czas:** ~75 minut

## Cele nauczania

- Opisz model aktora: agenci jako aktorzy, komunikaty jako jedyna metoda komunikacji międzyprocesowej (IPC) oraz izolacja awarii na poziomie pojedynczego aktora.
- Wymień trzy warstwy API w AutoGen v0.4 – Core, AgentChat oraz Extensions – i opisz ich przeznaczenie.
- Wyjaśnij, dlaczego oddzielenie procesu dostarczania komunikatów od ich obsługi zapewnia izolację błędów i natywną współbieżność.
- Zaimplementuj w Pythonie (stdlib) uproszczone środowisko uruchomieniowe modelu aktora i zrealizuj w nim proces przeglądu kodu realizowany przez dwóch agentów.

## Problem

Większość frameworków agentowych działa w sposób synchroniczny: jeden agent generuje dane, które kolejny przetwarza bezpośrednio w ramach tego samego stosu wywołań. Awaria jednego elementu powoduje zatrzymanie całego procesu. Współbieżność jest trudna w realizacji, a rozproszenie systemu wymaga głębokiego przepisania kodu.

Rozwiązanie wdrożone w AutoGen v0.4: model aktora. Każdy agent działa jako aktor posiadający prywatną skrzynkę odbiorczą. Wymiana komunikatów jest jedynym sposobem interakcji. Środowisko uruchomieniowe oddziela proces wysyłania komunikatów od ich przetwarzania. Awarie są izolowane do poziomu jednego aktora. Współbieżność jest natywna, a rozproszenie systemu sprowadza się do zmiany warstwy transportowej.

## Koncepcja

### Aktorzy

Każdy aktor posiada:

- Prywatny stan (brak bezpośredniego dostępu z zewnątrz).
- Skrzynkę odbiorczą (kolejkę komunikatów).
- Procedurę obsługi (handler): `receive(message) -> effects`, gdzie efektami mogą być: odpowiedź, wysłanie wiadomości do innego aktora, utworzenie (spawn) nowego aktora, aktualizacja stanu lub zatrzymanie samego siebie.

Aktorzy nie współdzielą pamięci – komunikują się wyłącznie za pomocą wiadomości.

### Trzy warstwy API w AutoGen v0.4

1. **Core.** Niskopoziomowy framework aktorów. `AgentRuntime`, `Agent`, `Message`, `Topic`. Oferuje asynchroniczną wymianę komunikatów sterowaną zdarzeniami.
2. **AgentChat.** Wysokopoziomowe API zorientowane na zadania (zastępujące `ConversableAgent` z wersji 0.2). `AssistantAgent`, `UserProxyAgent`, `RoundRobinGroupChat`, `SelectorGroupChat`.
3. **Extensions.** Integracje (OpenAI, Anthropic, Azure, narzędzia, systemy pamięci).

### Dlaczego oddzielenie ma znaczenie

W wersji v0.2 wywołanie `agent_a.chat(agent_b)` synchronicznie blokowało `agent_a` do czasu zakończenia pracy przez `agent_b`. W wersji 0.4 `send(agent_b, msg)` umieszcza komunikat w skrzynce odbiorczej odbiorcy i natychmiast zwraca sterowanie, a środowisko uruchomieniowe dostarcza go asynchronicznie. Przynosi to trzy główne korzyści:

- **Izolacja błędów (Fault isolation).** Błąd agenta B nie powoduje awarii agenta A – środowisko uruchomieniowe przechwytuje wyjątek w procedurze obsługi B i decyduje o kolejnych krokach (np. logowanie, ponowna próba, przekierowanie do kolejki błędów).
- **Natywna współbieżność.** Wiele komunikatów może być wysyłanych i przetwarzanych współbieżnie przez różnych aktorów.
- **Gotowość do rozproszenia (Distribution-ready).** Abstrakcja skrzynki odbiorczej i warstwy transportowej działa identycznie niezależnie od tego, czy aktorzy działają w jednym procesie, czy na różnych maszynach.

### Topologie orkiestracji

- **RoundRobinGroupChat.** Agenci wykonują ruchy w z góry określonej kolejności kołowej.
- **SelectorGroupChat.** Model selekcjonujący wybiera kolejnego agenta na podstawie dotychczasowego przebiegu konwersacji.
- **Magentic-One.** Referencyjny zespół wieloagentowy (multi-agent) przeznaczony do przeglądania sieci, uruchamiania kodu i operacji na plikach. Zbudowany na bazie warstwy AgentChat.

### Obserwowalność

Wbudowana obsługa OpenTelemetry. Każdy komunikat generuje zakres (span), a wywołania modeli zawierają atrybuty zgodne ze standardami semantycznymi OTel GenAI (Lekcja 23).

### Status projektu: tryb utrzymania

Stan na początek 2026 r.: AutoGen v0.7.x pozostaje stabilnym rozwiązaniem do zastosowań badawczych i prototypowania. Microsoft przeniósł jednak główny rozwój na Microsoft Agent Framework (wersja public preview od października 2025 r., wersja stabilna planowana na Q1 2026 r.). Niemniej koncepcje wprowadzone w AutoGen są w pełni przenaszalne – model aktora to sprawdzony i trwały wzorzec projektowy.

## Zbuduj to

Plik `code/main.py` implementuje uproszczone środowisko uruchomieniowe modelu aktora przy użyciu biblioteki standardowej Pythona:

- `Message` – typowany komunikat zawierający klucze `sender`, `recipient`, `topic`, `body`.
- `Actor` – klasa abstrakcyjna definiująca metodę `receive(message, runtime)`.
- `Runtime` – pętla zdarzeń zarządzająca współdzieloną kolejką komunikatów, ich dostarczaniem oraz izolacją błędów.
- Przykładowy scenariusz z dwoma aktorami: `ReviewerAgent` dokonuje przeglądu kodu, a `ChecklistAgent` weryfikuje go na podstawie listy kontrolnej. Aktorzy wymieniają komunikaty aż do wypracowania spójnego werdyktu.

Uruchomienie:

```
python3 code/main.py
```

Wygenerowane logi pokazują asynchroniczne dostarczanie komunikatów, symulację awarii jednego z aktorów (która nie przerywa działania całego systemu) oraz wypracowanie ostatecznego werdyktu.

## Użyj tego

- **AutoGen v0.4/v0.7** (tryb utrzymania) – stabilny framework do celów badawczych i prototypowania systemów wieloagentowych.
- **Microsoft Agent Framework** (wersja public preview) – rekomendowana ścieżka migracji; te same koncepcje modelu aktora w nowym interfejsie API.
- **Topologia roju (swarm) w LangGraph** (Lekcja 13) – alternatywna realizacja podobnego wzorca oparta na przekazywaniu zadań.
- **Własne środowisko uruchomieniowe** – gdy wymagana jest pełna kontrola nad warstwą transportową (np. integracja z NATS, RabbitMQ, gRPC).

## Wyślij to

Plik `outputs/skill-actor-runtime.md` generuje uproszczone środowisko uruchomieniowe oraz szablon orkiestracji (RoundRobin lub Selector) dla wskazanego zadania wieloagentowego.

## Ćwiczenia

1. Zaimplementuj obsługę kolejki komunikatów nieobsłużonych (Dead Letter Queue - DLQ): w przypadku błędu handlera, przekieruj komunikat do DLQ w celu weryfikacji przez operatora. Przetestuj działanie tego mechanizmu.
2. Zaimplementuj `SelectorGroupChat`: model selekcjonujący decyduje, który aktor powinien przetworzyć kolejny komunikat, bazując na historii rozmowy.
3. Wprowadź rozproszoną warstwę transportową: zastąp kolejkę wewnątrzprocesową przesyłaniem komunikatów JSON przez HTTP, umożliwiając uruchomienie aktorów w osobnych procesach.
4. Zaimplementuj uproszczone śledzenie OpenTelemetry dla każdego komunikatu. Emituj atrybuty `gen_ai.agent.name` oraz `gen_ai.operation.name` zgodnie z wytycznymi z Lekcji 23.
5. Zapoznaj się ze szczegółami architektury AutoGen v0.4. Przepisz uproszczoną implementację z użyciem biblioteki `autogen_core`. Przeanalizuj, jakie produkcyjne aspekty (np. obsługa sieci, bezpieczeństwo) zostały pominięte w uproszczonej wersji.

## Kluczowe terminy

| Termin | Co mówią ludzie | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Aktor (Actor) | „Agent” | Prywatny stan + skrzynka odbiorcza + handler; brak współdzielonej pamięci |
| Komunikat (Message) | „Zdarzenie” | Typowana struktura danych; jedyny sposób interakcji między aktorami |
| Skrzynka odbiorcza (Inbox) | „Kolejka komunikatów” | Kolejka wiadomości przypisana do konkretnego aktora |
| Środowisko uruchomieniowe (Runtime) | „Host agentów” | Pętla zdarzeń odpowiedzialna za routing komunikatów oraz izolację awarii |
| Temat (Topic) | „Kanał” | Nazwana przestrzeń do publikowania i subskrybowania komunikatów (Pub/Sub) przez aktorów |
| Izolacja błędów (Fault Isolation) | „Let it crash” | Awaria wewnątrz jednego aktora nie wpływa na stabilność pozostałych komponentów |
| RoundRobinGroupChat | „Rotacja kołowa” | Agenci wykonują ruchy po kolei w ustalonej pętli |
| SelectorGroupChat | „Wybór na podstawie kontekstu” | Dynamiczny wybór kolejnego wykonawcy na podstawie stanu konwersacji |
| Magentic-One | „Zbiór referencyjny” | Gotowy, wieloagentowy zespół do zadań sieciowych, programistycznych i plikowych |

## Dalsze czytanie

- [Microsoft Research, AutoGen v0.4](https://www.microsoft.com/en-us/research/articles/autogen-v0-4-reimagining-the-foundation-of-agentic-ai-for-scale-extensibility-and-robustness/) — oficjalny artykuł o nowej architekturze
- [Dokumentacja LangGraph](https://docs.langchain.com/oss/python/langgraph/overview) — grafowa alternatywa orkiestracji stanu
- [Konwencje semantyczne OpenTelemetry GenAI](https://opentelemetry.io/docs/specs/semconv/gen-ai/) — specyfikacja atrybutów telemetrycznych wdrażana domyślnie w systemach agentowych
