# LangGraph — Maszyny stanowe dla agentów

> Pętla ReAct napisana ręcznie to zwykłe `while True`. Pętla ReAct w LangGraph to graf, na którym możesz definiować punkty kontrolne, przerywać bieg, rozgałęziać proces i podróżować w czasie. Sam agent się nie zmienił, ale zmieniła się infrastruktura wokół niego.

**Typ:** Kompilacja  
**Języki:** Python  
**Wymagania wstępne:** Faza 11 · 09 (Wywoływanie funkcji), Faza 11 · 14 (Model Context Protocol)  
**Czas:** ~75 minut  

## Problem

Wdrażasz agenta wywołującego funkcje. Działa poprawnie przez pierwsze trzy tury, po czym pojawia się błąd: wywoływane narzędzie zwraca kod 500, użytkownik zmienia zdanie w połowie operacji lub agent decyduje się na zwrot zamówienia bez wymaganej akceptacji człowieka. Zwykła pętla `while True:` nie posiada punktów wejścia do obsługi takich zdarzeń. Nie da się jej wstrzymać, cofnąć ani przetestować scenariusza: „co by było, gdyby model wybrał inne narzędzie”. W momencie wdrożenia produkcyjnego po fazie demo, agent staje się czarną skrzynką, która albo zadziałała, albo nie.

Rozwiązanie staje się oczywiste, gdy je przeanalizujesz. Agent jest z natury maszyną stanową – przechowuje prompt systemowy, historię wiadomości, oczekujące wywołania narzędzi i kolejną akcję do wykonania. Zdefiniuj tę maszynę stanową jawnie w postaci grafu (StateGraph): węzły (nodes) dla stanów typu „model myśli”, „narzędzie wykonuje kod”, „człowiek weryfikuje” oraz krawędzie (edges) dla warunkowych przejść między nimi. Gdy struktura grafu jest czytelna, zyskujesz cztery potężne funkcjonalności bez pisania dodatkowego kodu: punkty kontrolne (checkpoints - zapisywanie stanu między krokami), przerwania (interrupts - wstrzymanie dla akceptacji człowieka), przesyłanie strumieniowe (streaming tokenów i zdarzeń) oraz podróż w czasie (time travel - powrót do poprzedniego stanu i rozgałęzienie na inną ścieżkę).

LangGraph to biblioteka udostępniająca te abstrakcje. Nie jest to sztywny framework agentowy w stylu klasycznego LangChain („oto gotowy AgentExecutor, powodzenia”). To silnik wykonawczy grafów (graph execution engine), w którym stan aplikacji, trwałość danych i przerwania są traktowane jako elementy pierwszej klasy. Pętla agenta to coś, co projektujesz graficznie, a nie piszesz ręcznie.

## Koncepcja

![LangGraph StateGraph: węzły, krawędzie i wskaźnik kontrolny](../assets/langgraph-stategraph.svg)

Struktura klasy `StateGraph` składa się z trzech elementów:

1. **Stan (State).** Strukturyzowany słownik (klasa TypedDict lub model Pydantic), który przepływa przez graf. Każdy węzeł otrzymuje aktualny stan i zwraca częściową aktualizację, którą LangGraph scala za pomocą *reduktora* (reducer) zdefiniowanego dla każdego pola (np. `operator.add` do kumulowania elementów na liście wiadomości, domyślnie nowe wartości nadpisują stare).
2. **Węzły (Nodes).** Funkcje Pythona o sygnaturze `state -> partial_state`. Każdy węzeł reprezentuje jeden krok procesu: „wywołaj model”, „uruchom narzędzia”, „generuj streszczenie”.
3. **Krawędzie (Edges).** Definiują przejścia między węzłami. Krawędzie statyczne prowadzą zawsze do jednego węzła docelowego. Krawędzie warunkowe wykorzystują funkcję rutującą o sygnaturze `state -> next_node_name`, umożliwiając rozgałęzianie ścieżek na podstawie odpowiedzi modelu.

Po zdefiniowaniu grafu kompilujesz go. Kompilacja weryfikuje topologię grafu, dołącza mechanizm zapisu stanów (checkpointer) i zwraca obiekt wykonywalny. Wywołujesz go, przekazując stan początkowy oraz unikalny identyfikator wątku `thread_id`. Po wykonaniu każdego węzła stan jest zapisywany w bazie jako punkt kontrolny powiązany z kluczem `(thread_id, checkpoint_id)`.

### Cztery supermoce LangGraph

**Punkty kontrolne (Checkpoints).** Każde przejście między węzłami automatycznie zapisuje aktualny stan grafu w bazie danych (w pamięci RAM na potrzeby testów, w Postgresie/Redisie/SQLite na produkcji). Możesz wznowić działanie wywołując ponownie graf z tym samym `thread_id` – LangGraph automatycznie odczyta ostatni punkt kontrolny i rozpocznie pracę od miejsca zatrzymania.

**Przerwania (Interrupts).** Oznacz węzeł parametrem `interrupt_before=["human_review"]`, a silnik wstrzyma wykonywanie przed uruchomieniem tego węzła. Stan zostaje zapisany, a serwer może zwrócić odpowiedź użytkownikowi: „oczekiwanie na zatwierdzenie”. Kolejne żądanie do tego samego `thread_id` z obiektem `Command(resume=...)` wznowi pracę grafu.

**Przesyłanie strumieniowe (Streaming).** Metoda `graph.stream(state, mode="updates")` przesyła strumieniowo cząstkowe aktualizacje stanu w locie. Tryb `mode="messages"` przesyła strumieniowo tokeny generowane przez model LLM, a `mode="values"` zwraca pełne migawki stanu po każdym kroku.

**Podróż w czasie (Time Travel).** Wywołanie `graph.get_state_history(thread_id)` zwraca historię wszystkich punktów kontrolnych wątku. Możesz przekazać dowolny wcześniejszy `checkpoint_id` do metody `graph.invoke` i uruchomić nową, alternatywną ścieżkę wykonania od tego momentu. Ułatwia to debugowanie błędów oraz pozwala na pisanie testów regresyjnych odtwarzających historyczne ślady produkcji.

### Rola reduktorów (Reducers)

Każde pole stanu grafu posiada przypisany reduktor. Domyślnie nowa wartość nadpisuje starą, co jest poprawne dla większości typów prostych. Jednak listy wiadomości wymagają użycia reduktora `operator.add` (lub wbudowanego `add_messages`), aby nowe wypowiedzi były dopisywane na koniec listy, a nie zastępowały całej historii konwersacji. Jeśli zapomnisz o adnotacji typu `Annotated[list, add_messages]`, aktualizacje z węzłów będą nadpisywać historię, co doprowadzi do utraty kontekstu.

### Graf ReAct w czterech krokach

Produkcyjny agent typu ReAct składa się z dwóch węzłów i krawędzi warunkowej:

1. Węzeł `agent` — wywołuje model LLM z aktualną historią wiadomości. Zwraca odpowiedź asystenta (która może zawierać wywołania narzędzi).
2. Węzeł `tools` — wykonuje wywołania narzędzi zlecone przez model i dopisuje ich wyniki na koniec listy wiadomości.
3. Krawędź warunkowa (conditional edge) wychodząca z węzła `agent` – kieruje przepływ do węzła `tools`, jeśli model zażądał wywołania narzędzi, lub kończy pracę grafu (`END`).
4. Krawędź statyczna łącząca węzeł `tools` z powrotem z węzłem `agent`.

Taki zapis pozwala na wdrożenie kompletnej pętli ReAct (Myśl → Działanie → Obserwacja → Myśl) z pełną obsługą punktów kontrolnych i przerwaniami w około 40 liniach kodu.

### Rozgałęzianie za pomocą Command/Send

Instrukcja `Send(node_name, state)` pozwala węzłom na dynamiczne uruchamianie równoległych podgrafów (fan-out). Przykład: agent decyduje o jednoczesnym odpytaniu trzech różnych systemów wyszukiwania. Każde wywołanie `Send` uruchamia węzeł docelowy współbieżnie, a ich wyniki są scalane reduktorem stanu na koniec etapu. W ten sposób LangGraph realizuje architekturę koordynator-pracownicy (supervisor-workers) bez ręcznego zarządzania wątkami.

### Podgrafy (Subgraphs)

Skompilowany graf może zostać użyty jako węzeł w innym grafie. Graf nadrzędny traktuje go jako pojedynczy krok wykonawczy, podczas gdy graf wewnętrzny zarządza swoim własnym stanem i punktami kontrolnymi. Umożliwia to budowanie hierarchicznych systemów agentowych.

## Zbuduj to

### Krok 1: Definicja stanu i węzłów grafu

Zdefiniujemy graf z reduktorem wiadomości oraz węzłem agenta i narzędzi.

```python
from typing import Annotated, TypedDict
from langchain_core.messages import AnyMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

def agent_node(state: State) -> dict:
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

def should_continue(state: State) -> str:
    last = state["messages"][-1]
    return "tools" if getattr(last, "tool_calls", None) else END

tool_node = ToolNode(tools=[search_web, read_file])

graph = StateGraph(State)
graph.add_node("agent", agent_node)
graph.add_node("tools", tool_node)
graph.set_entry_point("agent")
graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
graph.add_edge("tools", "agent")

app = graph.compile(checkpointer=MemorySaver())
```

Metoda `add_messages` to reduktor sprawiający, że nowe wiadomości są dopisywane do listy, a nie nadpisują poprzednich. Brak tej adnotacji to najczęstszy błąd przy wdrażaniu LangGraph.

### Krok 2: Uruchomienie z obsługą wątków (Threads)

```python
config = {"configurable": {"thread_id": "user-42"}}
for event in app.stream(
    {"messages": [HumanMessage("find the Anthropic headquarters address")]},
    config,
    stream_mode="updates",
):
    print(event)
```

Każde zdarzenie w strumieniu ma format `{node_name: state_delta}`. Serwer może przekazywać te aktualizacje do klienta, dzięki czemu użytkownik widzi postęp prac agenta w czasie rzeczywistym.

### Krok 3: Dodanie akceptacji człowieka (Human-in-the-Loop)

Zdefiniujemy wstrzymanie wykonania grafu przed uruchomieniem węzła narzędzi:

```python
app = graph.compile(
    checkpointer=MemorySaver(),
    interrupt_before=["tools"],  # wstrzymaj przed każdym wywołaniem narzędzia
)

state = app.invoke({"messages": [HumanMessage("delete the production database")]}, config)
# Wykonanie zostało wstrzymane. Sprawdź proponowane parametry wywołania w state["__interrupt__"].
# Jeśli operacja została zaakceptowana:
from langgraph.types import Command
app.invoke(Command(resume=True), config)

# Jeśli operacja została odrzucona: dopisz informację o blokadzie i wznów graf
app.update_state(config, {"messages": [AIMessage("Blocked by human reviewer.")]})
```

### Krok 4: Podróż w czasie (Time Travel) i debugowanie

```python
history = list(app.get_state_history(config))
for snapshot in history:
    print(snapshot.values["messages"][-1].content[:80], snapshot.config)

# Rozgałęzienie (fork) z historycznego punktu kontrolnego
target = history[3].config  # cofnij się o 3 kroki
for event in app.stream(None, target, stream_mode="values"):
    pass  # odtwórz wykonanie od tego punktu w nowej gałęzi
```

Przekazanie wartości `None` uruchamia ponowne odtworzenie od wskazanego punktu kontrolnego; przekazanie słownika aktualizuje stan przed wznowieniem pracy grafu. Pozwala to na reprodukcję i debugowanie błędów produkcyjnych.

### Krok 5: Produkcyjny zapis punktów kontrolnych (Postgres)

```python
from langgraph.checkpoint.postgres import PostgresSaver

with PostgresSaver.from_conn_string("postgresql://...") as checkpointer:
    checkpointer.setup()
    app = graph.compile(checkpointer=checkpointer)
```

Biblioteka dostarcza gotowe adaptery dla baz SQLite, Redis i Postgres. Klasa `MemorySaver` powinna być stosowana wyłącznie w testach lokalnych.

## Ramy projektowania maszyn stanowych

Projektując agenta w LangGraph, zastosuj poniższy schemat postępowania:

1. **Zdefiniuj węzły.** Każda odrębna decyzja lub akcja generująca efekty uboczne powinna być węzłem. Jeśli nie potrafisz ich wydzielić, proces nie ma jeszcze struktury maszyny stanowej.
2. **Określ strukturę stanu.** Przygotuj klasę TypedDict z reduktorami. Unikaj przechowywania wszystkich danych w historii wiadomości `messages` – wydziel istotne parametry (np. `plan`, `budget`, `retrieved_docs`) na najwyższy poziom stanu.
3. **Zdefiniuj krawędzie.** Krawędzie powinny być statyczne, chyba że kolejny krok zależy bezpośrednio od wygenerowanej odpowiedzi modelu. Krawędzie warunkowe wymagają funkcji rutującej (router function).
4. **Wybierz mechanizm zapisu stanów (Checkpointer).** Zastosuj bazy SQLite/Postgres/Redis na produkcji. Brak checkpointera uniemożliwia wstrzymywanie zadań, obsługę przerw oraz podróż w czasie.
5. **Zaplanuj przerwania przed efektami ubocznymi.** Weryfikacja i akceptacja człowieka powinny odbywać się przed wywołaniem narzędzi modyfikujących dane, co pozwala na bezpieczne anulowanie operacji.
6. **Dobierz tryb strumieniowania.** Stosuj `mode="updates"` do ogólnego monitorowania kroków, `mode="messages"` do strumieniowania tokenów LLM na poziomie interfejsu oraz `mode="values"` do analizy pełnych migawek w testach ewaluacyjnych.

*Zablokuj wdrożenie agenta na produkcji, jeśli nie posiada skonfigurowanego trwałego checkpointera lub jeśli lista wiadomości `messages` nie posiada reduktora `add_messages`.*

## Ćwiczenia

1. **Poziom łatwy.** Zaimplementuj graf ReAct składający się z węzła agenta oraz narzędzi (kalkulator i wyszukiwarka). Zweryfikuj za pomocą metody `graph.get_state_history`, czy historia zawiera co najmniej cztery punkty kontrolne po dwuetapowej konwersacji.
2. **Poziom średni.** Dodaj węzeł planowania `planner`, który uruchamia się przed agentem i zapisuje strukturę planu `plan: list[str]` do stanu grafu. Sprawdzaj, czy agent poprawnie aktualizuje statusy kroków planu. Upewnij się, że stan planu nie zostaje nadpisany ani utracony po wznowieniu grafu z punktu kontrolnego (weryfikacja reduktora).
3. **Poziom trudny.** Zbuduj graf hierarchiczny (supervisor graph) koordynujący pracę trzech podgrafów (`researcher`, `writer`, `reviewer`) za pomocą instrukcji `Send`. Każdy podgraf powinien posiadać własną strukturę stanu i checkpointer. Dodaj regułę `interrupt_before=["writer"]` w grafie głównym w celu akceptacji raportu z badań przez człowieka. Przetestuj podróż w czasie z wybranego punktu kontrolnego i upewnij się, że ponowne wykonanie dotyczy tylko nowo utworzonej gałęzi.

## Kluczowe terminy

| Termin | Potoczne rozumienie | Rzeczywiste znaczenie techniczne |
|------|-----------------|----------------------|
| StateGraph | „Graf LangGraph” | Klasa reprezentująca topologię grafu, do której dodajesz węzły i krawędzie przed kompilacją |
| Reduktor (Reducer) | „Scalanie pól stanu” | Funkcja o sygnaturze `(old, new) -> merged` wywoływana przy aktualizacji pola stanu; domyślnie nadpisuje wartość, `add_messages` dopisuje |
| Wątek (Thread) | „ID sesji” | Identyfikator `thread_id` grupujący wszystkie punkty kontrolne w ramach jednej sesji konwersacyjnej |
| Punkt kontrolny (Checkpoint) | „Zapisany stan grafu” | Migawka stanu grafu utrwalona po wykonaniu kroku, adresowana za pomocą klucza `(thread_id, checkpoint_id)` |
| Przerwanie (Interrupt) | „Wstrzymanie grafu” | Mechanizm wstrzymujący pracę silnika przed lub po wykonaniu węzła; wznowienie następuje przez przesłanie `Command(resume=...)` |
| Time Travel | „Przewijanie historii” | Odtwarzanie lub rozgałęzianie wykonania grafu od wybranego punktu kontrolnego wstecz |
| Send | „Uruchomienie podgrafów” | Konstrukcja służąca do dynamicznego, równoległego uruchamiania N instancji węzłów docelowych (fan-out) |
| Podgraf (Subgraph) | „Graf w grafie” | Skompilowany graf `StateGraph` pełniący rolę węzła w grafie nadrzędnym; posiada własny stan i checkpointer |
