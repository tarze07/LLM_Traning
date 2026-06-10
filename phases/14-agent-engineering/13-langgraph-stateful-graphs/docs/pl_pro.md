# LangGraph: Grafy stanowe i trwałość wykonywania

> LangGraph to standard na rok 2026 w zakresie niskopoziomowej orkiestracji opartej na stanie. Agent jest maszyną stanów, w której węzły są funkcjami, krawędzie reprezentują przejścia, a stan jest niezmienny (immutable) i utrwalany po każdym kroku. Umożliwia to wznowienie pracy po awarii dokładnie w miejscu jej przerwania.

**Typ:** Ucz się + Buduj
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 14 · 01 (Pętla agenta), Faza 14 · 12 (Wzorce przepływu pracy)
**Czas:** ~75 minut

## Cele nauczania

- Opisz podstawowy model LangGraph: maszynę stanów ze współdzielonym, niezmiennym stanem, węzłami funkcyjnymi, krawędziami warunkowymi oraz punktami kontrolnymi (checkpoints) utrwalanymi po każdym kroku.
- Wymień cztery kluczowe funkcjonalności wyróżniane w dokumentacji: trwałość wykonywania (persistence), przesyłanie strumieniowe (streaming), interakcję z człowiekiem (human-in-the-loop) oraz zaawansowaną pamięć.
- Wyjaśnij trzy topologie orkiestracji wspierane przez LangGraph: nadzorca (supervisor), peer-to-peer (rój / swarm) oraz hierarchiczna (zagnieżdżone podgrafy).
- Zaimplementuj w Pythonie (stdlib) graf stanowy z niezmiennym stanem, krawędziami warunkowymi oraz mechanizmem punktów kontrolnych i wznawiania działania.

## Problem

Agenci i przepływy pracy napotykają wspólny problem: jeśli proces składający się z 40 kroków ulegnie awarii w kroku 38, chcemy wznowić go od tego samego miejsca, zamiast uruchamiać wszystko od początku. Systemy, w których stan nie jest traktowany priorytetowo, zmuszają programistów do implementacji niestabilnych obejść i ponownych prób w bibliotekach, które zakładają uruchamianie procesów od zera.

Rozwiązanie wdrożone w LangGraph: stan jest traktowany jako obywatel pierwszej kategorii (first-class citizen), aktualizacje stanu są jawne, a punkty kontrolne (checkpoints) są zapisywane po wykonaniu każdego węzła. Wznowienie działania sprowadza się do wywołania `load_state(session_id)`.

## Koncepcja

### Graf

Graf definiują:

- **Typ stanu (State Schema).** Typowany słownik (lub model Pydantic), który każdy węzeł może odczytywać i aktualizować.
- **Węzły (Nodes).** Funkcje o sygnaturze `(state) -> state_update`. Zwracane aktualizacje są automatycznie scalane ze stanem głównym.
- **Krawędzie (Edges).** Przejścia bezpośrednie lub warunkowe pomiędzy węzłami.
- **Wejście i wyjście.** Specjalne węzły `START` i `END` wyznaczają granice grafu.

Przykład: agent z węzłami `classify`, `refund`, `bug`, `sales`, `done` – przepływ pracy routingu przedstawiony w postaci grafu.

### Trwałość wykonywania

Po zakończeniu pracy każdego węzła środowisko uruchomieniowe serializuje stan i zapisuje go w punkcie kontrolnym (SQLite, Postgres, Redis lub własnym rozwiązaniu). W przypadku awarii w kroku N, system może wywołać `resume(session_id)` i kontynuować wykonywanie od kroku N+1 z zachowaniem dokładnego stanu.

Dokumentacja LangGraph wyróżnia wdrożenia produkcyjne w firmach takich jak Klarna, Uber czy J.P. Morgan. Kluczem nie jest sam fakt prezentacji logiki jako grafu, lecz to, że architektura grafowa połączona z wersjonowaniem stanu (checkpointing) czyni odzyskiwanie sprawności po błędach niezwykle tanim.

### Przesyłanie strumieniowe

Każdy węzeł może generować częściowe wyniki. Graf przesyła strumieniowo zdarzenia i zmiany stanu dla poszczególnych węzłów do wywołującego, co pozwala na bieżąco aktualizować interfejs użytkownika w trakcie wykonywania.

### Interakcja z człowiekiem (Human-in-the-loop)

Możliwość weryfikacji i modyfikacji stanu pomiędzy węzłami. Typowy scenariusz: wstrzymanie wykonania przed krokiem krytycznym, prezentacja stanu człowiekowi, oczekiwanie na akceptację lub edycję i wznowienie. Zapisywanie punktów kontrolnych ułatwia ten proces, ponieważ stan jest już zserializowany.

### Pamięć

Pamięć krótkoterminowa (w obrębie jednego uruchomienia – np. historia konwersacji) oraz długoterminowa (pomiędzy uruchomieniami – utwalana w punktach kontrolnych oraz w zewnętrznych bazach). LangGraph integruje się z zewnętrznymi systemami pamięci (np. Mem0) poprzez interfejsy narzędzi.

### Trzy topologie orkiestracji

1. **Nadzorca (Supervisor).** Centralny model pełniący rolę koordynatora decyduje o przekazywaniu zadań do wyspecjalizowanych subagentów. Choć istnieje dedykowana klasa `create_supervisor()` w pakiecie `langgraph-supervisor`, zespół LangChain w 2026 r. często rekomenduje realizację tego wzorca poprzez bezpośrednie wywołania narzędzi przez model w celu lepszej kontroli nad oknem kontekstowym.
2. **Rój / Peer-to-Peer.** Subagenci komunikują się bezpośrednio i przekazują sobie zadania za pośrednictwem współdzielonej przestrzeni narzędzi. W tym scenariuszu brak jest centralnego orkiestratora.
3. **Hierarchiczna.** Struktura, w której nadrzędne orkiestratory zarządzają podległymi koordynatorami, zaimplementowana w postaci zagnieżdżonych podgrafów.

### Potencjalne problemy i wady wzorca

- **Zbyt ograniczony zakres punktów kontrolnych.** Zapisywanie wyłącznie historii konwersacji sprawia, że stan narzędzi i pamięci roboczej staje się nie do odzyskania. Serializacji musi podlegać pełny stan grafu.
- **Niedeterministyczne węzły.** Wznawianie działania zakłada, że ponowne wywołanie węzła z tymi samymi danymi wejściowymi da identyczny wynik. Należy zadbać o przechwytywanie zmiennych losowych (seeds), czasu systemowego oraz wyników zewnętrznych API.
- **Nadużywanie krawędzi warunkowych.** Graf, w którym każda krawędź jest warunkowa, staje się maszyną stanów niezwykle trudną w analizie i debugowaniu. Zaleca się stosowanie czytelnych, liniowych przepływów z nielicznymi rozgałęzieniami.

## Zbuduj to

Plik `code/main.py` implementuje graf stanowy przy użyciu biblioteki standardowej Pythona:

- `State` – typowany słownik (dict) zawierający klucze `messages`, `step`, `route`, `output`, `human_approval`.
- `Node` – obiekt wywoływalne (callable) przyjmujący stan i zwracający słownik z aktualizacją stanu.
- `StateGraph` – klasa zarządzająca węzłami, krawędziami bezpośrednimi i warunkowymi, uruchomieniem oraz wznawianiem działania.
- `SQLiteCheckpointer` (mockowany w pamięci) – serializuje stan po wykonaniu każdego węzła; `load(session_id)` przywraca stan.
- Przykładowy graf: klasyfikacja -> rozgałęzienie (zwrot / zgłoszenie błędu / sprzedaż) -> weryfikacja przez człowieka -> wysyłka.

Uruchomienie:

```
python3 code/main.py
```

Logi (trace) pokazują zatrzymanie pierwszego uruchomienia na etapie weryfikacji przez człowieka, utrwalenie stanu, a następnie wznowienie procesu i wygenerowanie ostatecznego wyniku.

## Użyj tego

- **LangGraph** – referencyjne rozwiązanie produkcyjne. Umożliwia korzystanie z `create_react_agent`, `create_supervisor` lub budowanie własnych grafów od podstaw.
- **AutoGen v0.4** (Lekcja 14) – alternatywny framework oparty na modelu aktora, przeznaczony do scenariuszy o dużej współbieżności.
- **Claude Agent SDK** (Lekcja 17) – zarządzany framework ze zintegrowanym mechanizmem sesyjnym.
- **Własna implementacja** – gdy wymagana jest pełna kontrola nad strukturą stanu lub mechanizmem zapisu punktów kontrolnych.

## Wyślij to

Plik `outputs/skill-state-graph.md` tworzy szkielet grafu stanowego w stylu LangGraph dla dowolnego środowiska uruchomieniowego z obsługą punktów kontrolnych i wznawiania działania.

## Ćwiczenia

1. Dodaj krawędź warunkową z węzła `classify` do `END` w przypadku, gdy pewność klasyfikacji jest zbyt niska. Umożliw wznawianie procesu po ręcznym zdefiniowaniu parametru `route` przez operatora.
2. Zastąp mockowany SQLite rzeczywistą bazą danych SQLite. Zmierz narzut wydajnościowy (overhead) serializacji na każdym kroku.
3. Zaimplementuj krawędzie równoległe: dwa węzły wykonują się współbieżnie, a ich wyniki są scalane za pomocą niestandardowego reduktora. Jaką rolę odgrywa tutaj niezmienność (immutability) stanu?
4. Zapoznaj się z dokumentacją `langgraph-supervisor`. Przepisz uproszczony przykład z użyciem `create_supervisor` i porównaj logi wykonania obu wersji.
5. Add streaming: make each node generate partial states while executing. Print deltas live to the console.

## Kluczowe terminy

| Termin | Co mówią ludzie | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Graf stanowy (State Graph) | „Agent jako maszyna stanów” | Typowana struktura stanu + węzły + krawędzie + funkcje redukujące |
| Punkt kontrolny (Checkpoint) | „Mechanizm trwałości” | Zapis zserializowanego stanu po wykonaniu węzła; umożliwia odzyskanie i wznowienie działania |
| Reduktor (Reducer) | „Scalanie stanów” | Funkcja określająca, jak połączyć dotychczasowy stan z aktualizacją z węzła |
| Krawędź warunkowa (Conditional Edge) | „Rozgałęzienie” | Przejście w grafie wybierane dynamicznie na podstawie aktualnego stanu |
| Podgraf (Sub-graph) | „Graf zagnieżdżony” | Graf działający jako pojedynczy węzeł wewnątrz grafu nadrzędnego |
| Trwałość wykonywania (Persistence) | „Wznawianie po awarii” | Odzyskanie stanu z ostatniego zapisanego punktu kontrolnego i kontynuacja od kolejnego węzła |
| Nadzorca (Supervisor) | „Orkiestrator LLM” | Centralny model przydzielający zadania wyspecjalizowanym subagentom |
| Rój (Swarm) | „Agenci P2P (Peer-to-Peer)” | Subagenci komunikujący się bezpośrednio i przekazujący sobie zadania; brak centralnego koordynatora |

## Dalsze czytanie

- [Dokumentacja LangGraph](https://docs.langchain.com/oss/python/langgraph/overview) — oficjalne materiały referencyjne
- [Dokumentacja langgraph-supervisor](https://reference.langchain.com/python/langgraph/supervisor/) — specyfikacja API dla wzorca orkiestratora
- [Microsoft Research, AutoGen v0.4](https://www.microsoft.com/en-us/research/articles/autogen-v0-4-reimagining-the-foundation-of-agentic-ai-for-scale-extensibility-and-robustness/) — alternatywne podejście oparte na modelu aktora
- [Opis sesji i subagentów w Claude Agent SDK](https://platform.claude.com/docs/en/agent-sdk/overview) — zarządzanie stanem i orkiestracja według Anthropic
