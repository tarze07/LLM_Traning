# Skalowanie produkcyjne – kolejki, punkty kontrolne i trwałość

> Skalowanie systemów wieloagentowych do tysięcy współbieżnych instancji wymaga wdrożenia mechanizmu **trwałego wykonania (durable execution)**. Środowisko uruchomieniowe LangGraph automatycznie zapisuje punkt kontrolny (checkpoint) po każdym kroku (superstep) w kontekście danego wątku (`thread_id`), domyślnie wykorzystując bazę PostgreSQL. Jeśli proces roboczy (worker) ulegnie awarii, zwalnia on blokadę (lease), co umożliwia innemu workerowi przejęcie wątku i wznowienie pracy od ostatniego zapisanego punktu kontrolnego. Agenci mogą w tym schemacie pozostawać w stanie uśpienia przez nieokreślony czas, oczekując na decyzję człowieka (human-in-the-loop). Projekt **MegaAgent** (arXiv:2408.09955) wdraża dedykowaną kolejkę producent-konsument dla każdego agenta z obsługą trzech stanów (Idle/Processing/Response) oraz dwupoziomową koordynację (komunikacja wewnątrz grupy + kanał administracyjny między grupami). Podejście oparte na programowaniu asynchronicznym (**async/await**) oraz procesach lekkich (fibers) znacząco przewyższa tradycyjny model wątków (thread-per-task) w zadaniach obsługi strumieniowej z LLM – wątki systemowe pozostają bezczynne przez 99% czasu, czekając na kolejne tokeny, podczas gdy model asynchroniczny wydajnie współdzieli zasoby we/wy. Kontrargumentem dla skomplikowanych architektur jest manifest „Scaling Agentic Software” (Ashpreet Bedi), który zaleca stosowanie stosu **FastAPI + PostgreSQL + niczym więcej**, dopóki realne obciążenie produkcyjne nie wymusi zmian – proste architektury często pozwalają zajść znacznie dalej, niż zakładano. W tej lekcji zaimplementujesz trwały rejestr punktów kontrolnych (checkpoint store), kolejkę zadań z maszynami stanów dla agentów, porównasz wydajność modelu asynchronicznego z wątkami systemowymi oraz wdrożysz pragmatyczną zasadę prostoty architektury na start.

**Typ:** Ucz się + Buduj
**Języki:** Python (stdlib, `asyncio`, `sqlite3`)
**Wymagania wstępne:** Faza 16 · 09 (Równoległe sieci roju), Faza 16 · 13 (pamięć współdzielona)
**Czas:** ~75 minut

## Problem

Lokalny prototyp systemu wieloagentowego działa bez problemu na pojedynczej maszynie z trzema agentami w pętli zdarzeń w pamięci RAM. Jednak przejście na środowisko produkcyjne ujawnia nowe wyzwania:

- Cykl życia agenta może trwać godzinami (np. wieloetapowe analizy, oczekiwanie na akceptację człowieka).
- Awaria kontenera lub maszyny wirtualnej z procesem roboczym (worker) oznacza całkowitą utratę niezapisanego stanu zadania.
- Obciążenie szczytowe bywa dziesięciokrotnie wyższe od średniego; system wymaga skalowania poziomego.
- Pobieranie opłat za wywołania agentów wymaga zagwarantowania semantyki dokładnie jednego wykonania (exactly-once execution) na potrzeby rozliczeń.

Standardowa, działająca w pamięci pętla zdarzeń nie rozwiąże tych problemów. System produkcyjny wymaga trwałej warstwy wykonawczej. Standardowe rozwiązania w 2026 roku to:

1. Silniki przepływu pracy z automatycznym zapisem stanu (np. Temporal, LangGraph Runtime).
2. Kolejki komunikatów połączone z bazą danych (np. PostgreSQL + Amazon SQS / RabbitMQ).
3. Szablony architektoniczne oparte na modelu aktora (np. dedykowane kolejki producent-konsument dla każdego agenta, jak w MegaAgent).
4. Uproszczony stos oparty na FastAPI i PostgreSQL (zgodnie z sugestią Bediego).

W tej lekcji zaimplementujesz uproszczone wersje tych koncepcji.

## Koncepcja

### Trwałe wykonanie (Durable Execution)

Silnik trwałego wykonania zapisuje i utrwala pełny stan programu po każdym zakończonym kroku (np. po superkroku/superstep w LangGraph). W przypadku awarii proces wygląda następująco:

```
worker crashes mid-step
  -> lease timeout
  -> another worker picks up the thread_id
  -> resumes from last checkpoint
  -> no duplicate side effects
```

Wymagania niezbędne do wdrożenia trwałego wykonania:

- **Serializowalny stan (serializable state):** kompletny stan agenta musi dawać się zapisać do formatu tekstowego/binarnego (np. JSON). Domknięcia funkcji (closures) trzymające aktywne sockety lub połączenia z bazą danych nie przetrwają restartu.
- **Deterministyczne wznawianie:** mając ten sam stan wejściowy, agent musi wygenerować to samo zachowanie (lub odwołać się do zapisanego, deterministycznego wyniku w przypadku wywołań LLM).
- **Idempotentność efektów ubocznych:** operacje zewnętrzne (np. płatności, wywołania zewnętrznych API) muszą być idempotentne lub zabezpieczone unikalnym kluczem deduplikacyjnym (deduplication key).

LangGraph rejestruje punkty kontrolne po każdym superkroku, Temporal po każdej wykonanej aktywności, a Restate opiera się na trwałym logowaniu zdarzeń (event sourcing). Wszystkie te silniki realizują ten sam schemat architektoniczny.

### Architektura LangGraph Runtime

Każda instancja agenta jest identyfikowana przez unikalny `thread_id`. Stan jest reprezentowany przez ustrukturyzowany słownik (state dict), a każdy zakończony superkrok dopisuje rekord do bazy danych punktów kontrolnych. W przypadku wznowienia wątku system odtwarza stan z ostatniego checkpointu, a nie od początku. Agenci mogą wywołać metodę `interrupt()`, oczekując na akceptację lub dane wejściowe od człowieka – środowisko uruchomieniowe utrwala wtedy stan i zwalnia wątek procesora (worker thread). Gdy dane wejściowe zostaną dostarczone, dowolny wolny worker może podjąć i kontynuować zadanie.

Jest to referencyjny wzorzec architektury produkcyjnej w 2026 roku.

### Kolejkowanie zadań MegaAgent

Praca arXiv:2408.09955 opisuje eksperymenty skalowania tysięcy współbieżnych agentów w jednym klastrze. Struktura systemu prezentuje się następująco:

```
agent i:
  state ∈ {Idle, Processing, Response}
  in_queue   <- messages addressed to agent i
  out_queue  -> replies + side effects

coordinators:
  intra-group chat  (agents in the same group)
  inter-group admin chat  (high-level routing)
```

Dwuwarstwowy model koordynacji umożliwia częstą wymianę komunikatów wewnątrz poszczególnych grup roboczych, podczas gdy komunikacja administracyjna na poziomie międzygrupowym pozostaje rzadka. Wzorzec ten pozwala utrzymać liniowy wzrost kosztów komunikacji przy skali tysięcy agentów.

### Programowanie asynchroniczne (async) vs model wątkowy

Oczekiwanie na odpowiedzi z API LLM to zadanie ograniczone wydajnością operacji we/wy (I/O-bound). Wątek systemowy czekający na przesłanie kolejnego tokenu przez sieć jest bezczynny przez 99% czasu. Każdy wątek systemowy zużywa około 1 MB pamięci RAM na swój stos. Przy 10 000 jednoczesnych połączeń daje to około 10 GB pamięci RAM przeznaczonej na same stosy wątków.

Mechanizmy asynchroniczne (Python `asyncio`, goroutines w języku Go, biblioteka `tokio` w Rust) współdzielą jeden lub kilka wątków systemowych do obsługi many operacji sieciowych jednocześnie. Te same 10 000 połączeń można bez problemu obsłużyć w ramach jednego procesu. Przy skalowaniu agentów LLM asynchroniczność to nie tylko optymalizacja – to kluczowa decyzja architektoniczna.

Wyjątek: operacje intensywnie obciążające procesor (np. obliczanie osadzeń/embeddings, tokenizacja) wciąż wymagają delegowania zadań do osobnej puli wątków (thread pool) lub procesów. Warstwę operacji sieciowych (I/O) należy bezwzględnie odseparować od warstwy obliczeniowej (CPU).

### Podejście pragmatyczne: FastAPI + PostgreSQL

Ashpreet Bedi w artykule „Scaling Agentic Software” (2026) zwraca uwagę na to, że większość zespołów przedwcześnie komplikuje architekturę systemu, zanim zmierzy rzeczywiste zapotrzebowanie. Prosty i skuteczny stos na start to:

- Aplikacja FastAPI + baza danych PostgreSQL.
- Każda instancja uruchomieniowa agenta reprezentuje rekord w tabeli, a jego stan jest modyfikowany z wykorzystaniem blokad optymistycznych (optimistic concurrency control).
- Długotrwale zadania są uruchamiane asynchronicznie za pomocą mechanizmu `pg_notify` lub prostego workera Celery.
- Logika ponawiania prób (retry logic) jest zaimplementowana bezpośrednio w kodzie aplikacji.

Dla obciążeń poniżej 100 współbieżnych instancji agentowych wykonujących zadania o przewidywalnym czasie działania, ten uproszczony schemat jest w zupełności wystarczający. Przejdź na bardziej skomplikowane rozwiązania dopiero wtedy, gdy pomiary wskażą ograniczenia prostego stosu.

Złota zasada: wdrażaj dedykowane silniki trwałego wykonania dopiero wtedy, gdy napotkasz konkretny problem (np. konieczność obsługi interakcji z człowiekiem trwającej wiele dni czy rozproszone transakcje), którego prosta baza danych nie jest w stanie obsłużyć.

### Semantyka dokładnie jednego wykonania (Exactly-Once)

W systemach, gdzie za wywołania agentów pobierane są opłaty, niezbędne jest zagwarantowanie semantyki dokładnie jednego wykonania (czyli dostarczenie komunikatu przynajmniej raz połączone z idempotentnym konsumentem). Wykorzystuje się do tego standardowe wzorce:

- **Unikalny klucz deduplikacyjny** generowany dla każdego uruchomienia zadania i przekazywany do wszystkich wywołań zewnętrznych.
- **Wzorzec skrzynki nadawczej (Outbox Pattern):** intencja wykonania operacji zewnętrznej jest najpierw zapisywana w bazie danych, a dopiero potem asynchronicznie procesowana przez dedykowanego workera.
- **Transakcje kompensujące (Saga Pattern):** jeśli operacja zewnętrzna powiodła się, lecz zapis stanu w systemie nadrzędnym zawiódł, automatycznie uruchamiane jest zadanie odwracające skutki (np. zwrot środków).

Są to klasyczne wzorce inżynierii systemów rozproszonych i baz danych, a nie technologie specyficzne dla sztucznej inteligencji. Jedyną specyfiką systemów AI jest powolne tempo generowania odpowiedzi LLM.

### Wdrożenia typu Rainbow (Rainbow Deployments)

Rozproszony system badawczy firmy Anthropic wykorzystuje model wdrażania określany jako „Rainbow Deployments”. Polega on na jednoczesnym utrzymywaniu wielu aktywnych wersji środowiska uruchomieniowego agentów w chmurze. Dzięki temu długo działające procesy badawcze nie są przerywane przy każdym wdrożeniu nowego kodu aplikacji. Nowe zapytania są kierowane do wersji kanaryjskiej (canary), podczas gdy stara wersja jest stopniowo wygaszana dopiero wtedy, gdy wszyscy uruchomieni w niej agenci zakończą swoje zadania.

Rozwiązanie to jest standardem dla systemów stanowych o długim cyklu życia. W erze agentów LLM, których praca może trwać wiele godzin, procesy CI/CD muszą natywnie wspierać takie scenariusze.

### Produkcyjna lista kontrolna

- **Trwałość stanu:** systematyczny zapis punktów kontrolnych (checkpointing), migawek (snapshots) lub implementacja wzorca Outbox z dziennikiem zdarzeń.
- **Idempotentność efektów ubocznych.**
- **Asynchroniczna warstwa sieciowa (I/O):** dedykowana do obsługi zapytań do API LLM.
- **Gwarancja dostarczenia co najmniej raz (at-least-once) z deduplikacją komunikatów.**
- **Strategia wdrożeń Rainbow/Canary** dla długo żyjących procesów stanowych.
- **Kompleksowy monitoring (observability):** rejestrowanie logów jednostkowych agentów, audyt kroków (supersteps) oraz śledzenie liczby ponownych prób.

## Zbuduj to

Skrypt `code/main.py` implementuje:

- `CheckpointStore` – trwały rejestr punktów kontrolnych w bazie SQLite powiązany z identyfikatorami wątków (`thread_id`). Każdy superkrok dopisuje rekord do bazy.
- `run_with_checkpoint(agent, thread_id)` – symulację awarii procesu w trakcie działania; nowy proces wznawia wykonywanie zadania od ostatniego zapisanego checkpointu.
- `AgentQueue` – maszynę stanów (Idle/Processing/Response) połączoną z uproszczoną kolejką zadań.
- `demo_async_vs_threads()` – benchmark uruchamiający 500 współbieżnych, symulowanych zapytań do LLM przy użyciu modelu asynchronicznego oraz wątków systemowych; porównuje czas wykonania oraz zużycie pamięci.

Uruchom:

```
python3 code/main.py
```

Oczekiwany wynik: pomyślne wznowienie pracy z punktu kontrolnego po symulowanej awarii; wersja asynchroniczna przetwarza 500 połączeń w czasie poniżej 1 sekundy, podczas gdy wersja wątkowa potrzebuje kilku sekund i zużywa znacznie więcej pamięci RAM.

## Użyj tego

Plik `outputs/skill-scaling-advisor.md` doradza w wyborze odpowiedniej warstwy trwałego wykonania zoptymalizowanej pod kątem skali obciążeń, wymagań dotyczących stanowości oraz polityki CI/CD (FastAPI + PostgreSQL, LangGraph Runtime, Temporal lub rozwiązania dedykowane).

## Wdrożenie produkcyjne

- **Zacznij od prostego stosu (zasada Bediego).** Konfiguracja FastAPI + PostgreSQL jest w zupełności wystarczająca, dopóki testy obciążeniowe nie wykażą jej ograniczeń.
- **Mierz przed optymalizacją.** Monitoruj histogramy opóźnień procesów, czasy trwania kroków pośrednich (supersteps), liczbę ponownych prób i typy błędów.
- **Stosuj wzorzec skrzynki nadawczej (Outbox Pattern) dla efektów ubocznych.** Jest to szczególnie istotne w obszarze mikropłatności oraz integracji z zewnętrznymi interfejsami API.
- **Wdróż mechanizm Rainbow Deployments.** Unikaj nagłego przerywania pracy agentów podczas wdrażania nowych wersji oprogramowania na produkcji.
- **Zintegruj zaawansowane silniki trwałego wykonania (np. Temporal, LangGraph Runtime lub Restate) dopiero wtedy, gdy** napotkasz konkretne bariery: wielodniowe oczekiwanie na dane wejściowe, złożone transakcje rozproszone czy wielopoziomowe pętle ponawiania prób.
- **Korzystaj z asynchroniczności (asyncio) do obsługi zadań sieciowych (I/O).** Wątki systemowe powinny być rezerwowane wyłącznie dla operacji silnie obciążających procesor (CPU-bound).

## Ćwiczenia

1. Uruchom `code/main.py`. Zweryfikuj poprawność wznawiania działania z zapisanego punktu kontrolnego oraz porównaj zużycie zasobów w modelu asynchronicznym i wątkowym.
2. Zaimplementuj tabelę **skrzynki nadawczej (outbox)**: każde wywołanie zewnętrznego narzędzia powinno być najpierw rejestrowane w bazie danych, a dopiero potem procesowane przez niezależnego workera. Przetestuj idempotentność poprzez dwukrotne wywołanie tego samego zadania.
3. Zaimplementuj prostą symulację **wdrożenia typu Rainbow**: uruchom jednocześnie dwie wersje środowiska wykonawczego. Skieruj nowe zapytania (`thread_id`) do nowej wersji i upewnij się, że zadania w toku na starej wersji nie zostały przerwane i dobiegły końca.
4. Przeczytaj dokumentację LangGraph Runtime. Zastanów się, które z wbudowanych mechanizmów tego środowiska wymagałyby najwięcej pracy przy samodzielnej implementacji w FastAPI + PostgreSQL. Czy funkcje te uzasadniają wdrożenie gotowego frameworka na obecnym etapie projektu?
5. Przeczytaj rozdział 3 w publikacji MegaAgent (arXiv:2408.09955). Zaprojektuj architekturę odwzorowującą opisany dwupoziomowy model koordynacji (komunikacja wewnątrz grupy oraz administracja międzygrupowa) na strukturę kolejek komunikatów.

## Kluczowe terminy

| Termin | Co się potocznie mówi | Co to właściwie oznacza |
|---|---|---|
| Trwałe wykonanie (Durable Execution) | „Utrzymywanie stanu programu” | Silnik zapisu stanu aplikacji po każdym superkroku; umożliwia bezpieczne wznawianie pracy po awarii. |
| Superkrok (Superstep) | „Granica transakcji” | Pojedyncza faza obliczeń wykonywana pomiędzy kolejnymi punktami kontrolnymi w LangGraph. |
| thread_id | „Identyfikator wątku agenta” | Klucz identyfikujący konkretny przebieg zadania, służący do odzyskiwania stanu i pobierania checkpointów. |
| Idempotentność (Idempotency) | „Możliwość bezpiecznego ponowienia” | Właściwość operacji gwarantująca, że jej wielokrotne wykonanie przyniesie identyczny skutek jak jednokrotne. |
| Wzorzec skrzynki nadawczej (Outbox Pattern) | „Zapis przed wysyłką” | Wzorzec zapisu intencji wykonania operacji sieciowej do lokalnej bazy danych przed jej faktycznym zrealizowaniem. |
| Dostarczenie co najmniej raz | „Ryzyko duplikatów” | Gwarancja systemów kolejkowych zapewniająca, że komunikat dotrze do odbiorcy, choć może zostać dostarczony wielokrotnie. |
| Wdrożenie Rainbow | „Wielowersyjność w locie” | Równoległe utrzymywanie w chmurze wielu wersji kodu aplikacji w celu bezkonfliktowego dokończenia długotrwałych zadań. |
| Asynchroniczność (Async / Fibers) | „Współdzielenie wątków” | Model programowania asynchronicznego, w którym jeden wątek systemowy obsługuje wiele operacji sieciowych jednocześnie. |
| Punkt kontrolny (Checkpoint) | „Zrzut stanu” | Zapisany w bazie danych serializowany stan aplikacji na granicy superkroku, umożliwiający późniejsze wznowienie działania. |

## Dalsze czytanie

- [LangChain – Concept Guide: LangGraph Runtime](https://www.langchain.com/conceptual-guides/runtime-behind-production-deep-agents) – architektura i mechanizmy działania LangGraph Runtime
- [MegaAgent](https://arxiv.org/abs/2408.09955) – model kolejkowania producent-konsument dla populacji tysięcy agentów
- [Matrix](https://arxiv.org/abs/2511.21686) – zdecentralizowany framework wykorzystujący kolejki komunikatów jako warstwę koordynacji
- [Dokumentacja silnika Temporal](https://docs.temporal.io/) – dokumentacja referencyjnego silnika trwałego wykonywania przepływów pracy
- [Anthropic – Multi-Agent Research System](https://www.anthropic.com/engineering/multi-agent-research-system) – praktyczne wnioski produkcyjne, w tym opis wdrożeń typu Rainbow
