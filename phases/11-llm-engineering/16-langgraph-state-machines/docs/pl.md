# LangGraph — Maszyny stanowe dla agentów

> Pętla ReAct napisana ręcznie to `while True`. Pętla ReAct napisana w LangGraph to graf, po którym możesz punktować, przerywać, rozgałęziać i podróżować w czasie. Agent się nie zmienił. Uprząż wokół niego ma.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 11 · 09 (Wywoływanie funkcji), Faza 11 · 14 (Protokół kontekstu modelu)
**Czas:** ~75 minut

## Problem

Wysyłasz agenta wywołującego funkcję. Działa przez trzy tury, potem coś idzie nie tak: model wypróbowuje narzędzie, które zwraca 500, użytkownik zmienia zdanie w połowie zadania lub agent decyduje się na zwrot zamówienia bez podpisania przez człowieka. Pętla `while True:` nie ma żadnych zaczepów. Nie można go wstrzymać, przewinąć do tyłu ani przejść do pytania „co by było, gdyby model wybrał inne narzędzie”. W momencie, gdy wyślesz to po wersji demonstracyjnej, agent staje się czarną skrzynką, która albo działała, albo nie.

Następny krok będzie oczywisty, gdy go zobaczysz. Agent jest już maszyną stanów — monit systemowy, historia komunikatów, oczekujące wywołania narzędzi i następna akcja. Wyraźnie określ maszynę stanów: węzły dla „model myśli”, „narzędzie działa”, „człowiek zatwierdza” i krawędzie dla warunkowych przejść między nimi. Gdy wykres jest już wyraźny, uprząż otrzymuje cztery rzeczy za darmo: punkty kontrolne (zapisywanie stanu między krokami), przerwania (pauza dla człowieka), przesyłanie strumieniowe (tokeny strumienia i zdarzenia pośrednie) oraz podróże w czasie (przewiń do poprzedniego stanu i wypróbuj inną gałąź).

LangGraph to biblioteka dostarczająca tę abstrakcję. Nie jest to struktura agenta w sensie LangChain („oto AgentExecutor, powodzenia”). Jest to środowisko wykonawcze wykresów z pierwszorzędnym stanem, pierwszorzędną trwałością i pierwszorzędnymi przerwaniami. Pętla agenta to coś, co rysujesz, a nie coś, co piszesz ręcznie.

## Koncepcja

![LangGraph StateGraph: węzły, krawędzie i wskaźnik kontrolny](../assets/langgraph-stategraph.svg)

`StateGraph` ma trzy rzeczy.

1. **Stan.** Wpisany słownik (model TypedDict lub Pydantic), który przepływa przez wykres. Każdy węzeł otrzymuje pełny stan i zwraca częściową aktualizację, którą LangGraph łączy przy użyciu *reduktora* dla każdego pola — `operator.add` w przypadku list, które powinny się kumulować, domyślnie nadpisują.
2. **Węzły.** Funkcje Pythona `state -> partial_state`. Każdy z nich to odrębny krok: „wywołaj model”, „uruchom narzędzia”, „podsumuj”.
3. **Krawędzie.** Przejścia pomiędzy węzłami. Krawędzie statyczne idą w jedno miejsce. Krawędzie warunkowe przyjmują funkcję routera `state -> next_node_name`, dzięki czemu graf może rozgałęziać się na wyjściu modelu.

Kompilujesz wykres. Kompilacja wiąże topologię, dołącza wskaźnik kontrolny (opcjonalny, ale niezbędny do produkcji) i zwraca plik uruchamialny. Wywołujesz go ze stanem początkowym i `thread_id`. Na każdym etapie wykonania utrzymuje się punkt kontrolny oznaczony na `(thread_id, checkpoint_id)`.

### Cztery supermoce

**Punkty kontrolne.** Każde przejście węzła zapisuje nowy stan do magazynu (w pamięci dla testów, Postgres/Redis/SQLite dla prod). Wznów, wywołując ponownie wykres z tym samym `thread_id`. Wykres rozpoczyna się w miejscu, w którym się zatrzymał.

**Przerwania.** Oznacz węzeł znacznikiem `interrupt_before=["human_review"]`, a wykonanie zostanie zatrzymane przed uruchomieniem tego węzła. Stan trwa. Twój interfejs API odpowiada użytkownikowi komunikatem „oczekuje na zatwierdzenie”. Późniejsze żądanie do tego samego `thread_id` z `Command(resume=...)` wznawia wykonywanie.

**Przesyłanie strumieniowe.** `graph.stream(state, mode="updates")` wyświetla różnice stanu na bieżąco. `mode="messages"` przesyła strumieniowo tokeny LLM do węzłów modelu. `mode="values"` wyświetla pełne migawki. Ty wybierasz, co ma być widoczne w Twoim interfejsie użytkownika.

**Podróż w czasie.** `graph.get_state_history(thread_id)` zwraca pełny dziennik punktów kontrolnych. Przekaż dowolne wcześniejsze `checkpoint_id` do `graph.invoke` i od tego momentu rozwidlasz. Świetnie nadaje się do debugowania („co by było, gdyby model zamiast tego wybrał narzędzie B?”) i do testów regresyjnych, które odtwarzają ślady produkcji.

### Najważniejsze są reduktory

Każde pole stanu ma reduktor. Większość ustawień domyślnych jest w porządku — nowa wartość zastępuje starą. Ale listy wiadomości wymagają `operator.add`, aby nowe wiadomości były dołączane zamiast zastępować. Równoległe krawędzie łączą swoje aktualizacje poprzez reduktor. Jeśli oba węzły zaktualizują `messages` i zapomnisz o `Annotated[list, add_messages]`, drugi wygrywa po cichu, a ty tracisz połowę tury. Reduktor to jedyna subtelna rzecz w bibliotece; zrób to dobrze, a reszta komponuje.

### Wykres ReAct w czterech węzłach

Produkcyjny agent ReAct składa się z czterech węzłów i dwóch krawędzi:

1. `agent` — wywołuje LLM z bieżącą historią wiadomości. Zwraca wiadomość asystenta (która może zawierać wywołania narzędzi).
2. `tools` — wykonuje dowolne wywołania narzędzi w ostatniej wiadomości asystenta, dołącza wyniki narzędzia jako komunikaty narzędzia.
3. Warunkowe zbocze z `agent`, które kieruje do `tools`, jeśli ostatni komunikat zawiera wywołania narzędziowe, w przeciwnym razie do `END`.
4. Statyczna krawędź z `tools` z powrotem do `agent`.

To jest to. Otrzymujesz pełną pętlę ReAct (Myśl → Akcja → Obserwacja → Myśl →…) z punktami kontrolnymi, przerwaniami i przesyłaniem strumieniowym, w około 40 liniach kodu.

### StateGraph vs Wyślij (fanout)

`Send(node_name, state)` umożliwia węzłowi wysyłanie równoległych podgrafów. Przykład: agent postanawia zapytać jednocześnie trzy retrievery. Każdy `Send` powoduje równoległe wykonanie węzła docelowego; ich wyjścia łączą się poprzez reduktor stanu. W ten sposób LangGraph wyraża wzorzec koordynator-pracownik bez wątkowania prymitywów.

### Podgrafy

Skompilowany wykres może być węzłem w innym grafie. Wykres zewnętrzny przedstawia pojedynczy węzeł; wykres wewnętrzny ma swój własny stan i własne punkty kontrolne. W ten sposób zespoły budują agentów przełożony-pracownik: wykres nadzorcy kieruje zamiary użytkownika do podgrafu pracownika w danej domenie.

## Zbuduj to

### Krok 1: stan i węzły

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

`add_messages` to reduktor, który powoduje, że lista wiadomości gromadzi się zamiast nadpisywać. Zapominanie o tym jest najczęstszym błędem LangGraph.

### Krok 2: uruchom z wątkiem

```python
config = {"configurable": {"thread_id": "user-42"}}
for event in app.stream(
    {"messages": [HumanMessage("find the Anthropic headquarters address")]},
    config,
    stream_mode="updates",
):
    print(event)
```

Każda aktualizacja jest nakazem `{node_name: state_delta}`. Twój interfejs może przesyłać je strumieniowo do interfejsu użytkownika, dzięki czemu użytkownicy zobaczą „agent myśli… dzwoni do search_web… ma wynik… odpowiada”.

### Krok 3: dodaj przerwanie typu „human-in-the-loop”.

Zaznacz węzeł, aby wykonanie zostało wstrzymane przed uruchomieniem.

```python
app = graph.compile(
    checkpointer=MemorySaver(),
    interrupt_before=["tools"],  # pause before every tool call
)

state = app.invoke({"messages": [HumanMessage("delete the production database")]}, config)
# state["__interrupt__"] is set. Inspect proposed tool calls.
# If approved:
from langgraph.types import Command
app.invoke(Command(resume=True), config)
# If denied: write a rejection message and resume
app.update_state(config, {"messages": [AIMessage("Blocked by human reviewer.")]})
```

Stan, punkt kontrolny i wątek pozostają w pamięci przerwania. Nic nie jest w pamięci, z wyjątkiem czasu wykonywania.

### Krok 4: podróż w czasie w celu debugowania

```python
history = list(app.get_state_history(config))
for snapshot in history:
    print(snapshot.values["messages"][-1].content[:80], snapshot.config)

# Fork from a prior checkpoint
target = history[3].config  # three steps back
for event in app.stream(None, target, stream_mode="values"):
    pass  # replay from that point forward
```

Przekazywanie `None` podczas odtwarzania danych wejściowych z danego punktu kontrolnego; przekazanie wartości dołącza ją jako aktualizację stanu tego punktu kontrolnego przed wznowieniem. W ten sposób odtworzysz zły przebieg agenta bez ponownego uruchamiania całej rozmowy.

### Krok 5: zamień punkt kontrolny na produkcję

```python
from langgraph.checkpoint.postgres import PostgresSaver

with PostgresSaver.from_conn_string("postgresql://...") as checkpointer:
    checkpointer.setup()
    app = graph.compile(checkpointer=checkpointer)
```

SQLite, Redis i Postgres są dostarczane. `MemorySaver` jest przeznaczony do testów. Wszystko, co utrzymuje się po ponownym uruchomieniu, wymaga prawdziwego sklepu.

## Umiejętność

> Budujesz agentów jako wykresy, a nie pętle `while True`.

Zanim sięgniesz po LangGraph, wykonaj 60-sekundowy projekt:

1. **Nazwij węzły.** Każda dyskretna decyzja lub działanie uboczne jest węzłem. „Agent myśli”, „narzędzie działa”, „recenzent zatwierdza”, „strumienie odpowiedzi”. Jeśli nie możesz ich wymienić, zadanie nie ma jeszcze kształtu agenta.
2. **Zadeklaruj stan.** Minimalny TypedDict z reduktorem dla każdego pola listy. Nie upychaj wszystkiego w `messages`; przenieś pola specyficzne dla zadania (działająca `plan`, licznik `budget`, lista `retrieved_docs`) na najwyższy poziom.
3. **Narysuj krawędzie.** Statyczne, chyba że następny krok zależy od wyników modelu. Każda krawędź warunkowa potrzebuje funkcji routera z nazwanymi gałęziami.
4. **Wybierz punkt kontrolny z góry.** `MemorySaver` dla testów, Postgres/Redis/SQLite dla czegokolwiek innego. Nie wysyłaj bez niego — brak punktu kontrolnego oznacza brak wznowienia, brak przerwań i podróż w czasie.
5. **Zdecyduj o przerwaniach przed uruchomieniem narzędzi, a nie po.** Zatwierdzenia idą na krawędzi do węzła bocznego, dzięki czemu możesz anulować przed uszkodzeniem; weryfikacja przebiega na granicy modelu, dzięki czemu można tanio odrzucać złe połączenia.
6. **Domyślny strumień.** `mode="updates"` dla interfejsu użytkownika, `mode="messages"` dla przesyłania strumieniowego na poziomie tokena wewnątrz węzłów modelu, `mode="values"` dla pełnych migawek podczas ewaluacji.

Odmów wysłania agenta LangGraph, który nie ma punktu kontrolnego. Odmów wysłania takiego, który zakłóca *po* efekcie ubocznym. Odmów wysłania pola `messages` bez `add_messages` jako jego reduktora.

## Ćwiczenia

1. **Łatwe.** Zaimplementuj powyższy czterowęzłowy wykres ReAct za pomocą narzędzia kalkulatora i narzędzia wyszukiwania w Internecie. Sprawdź, czy `list(app.get_state_history(config))` zwraca co najmniej cztery punkty kontrolne dla konwersacji dwuetapowej.
2. **Medium.** Dodaj węzeł `planner`, który działa przed `agent` i zapisuje do stanu ustrukturyzowany `plan: list[str]`. Niech `agent` oznaczy kroki planu jako wykonane. Nie zdaj testu, jeśli `plan` zostanie utracony po wznowieniu w punkcie kontrolnym (nieprawidłowy reduktor).
3. **Trudne.** Zbuduj graf nadzorcy przedstawiający trasy pomiędzy trzema podgrafami (`researcher`, `writer`, `reviewer`) za pomocą `Send`. Każdy podgraf ma swój własny stan i punkt kontrolny. Dodaj `interrupt_before=["writer"]` na zewnętrznym wykresie, aby człowiek mógł zatwierdzić opis badania. Potwierdź, że podróż w czasie z poprzedniego punktu kontrolnego ponownie przebiega tylko rozwidlaną gałęzią.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Wykres stanu | „Wykres LangGrapha” | Obiekt konstruktora, do którego dodajesz węzły i krawędzie przed kompilacją. |
| Reduktor | „Jak pole się łączy” | Funkcja `(old, new) -> merged` stosowana, gdy węzeł zwraca aktualizację dla tego pola; domyślnie jest nadpisywane, `add_messages` dołącza. |
| Wątek | „Identyfikator rozmowy” | Ciąg `thread_id` obejmujący wszystkie punkty kontrolne w jednej sesji. |
| Punkt kontrolny | „Stan wstrzymania” | Utrwalona migawka stanu pełnego wykresu po przejściu węzła, wpisana w `(thread_id, checkpoint_id)`. |
| Przerwij | „Przerwa dla człowieka” | `interrupt_before` / `interrupt_after` zatrzymuje wykonywanie na granicy węzła; wznów za pomocą `Command(resume=...)`. |
| Podróż w czasie | „Rozwidlenie z poprzedniego kroku” | `graph.invoke(None, config_with_old_checkpoint_id)` odtwarza powtórki od tego punktu kontrolnego do przodu. |
| Wyślij | „Równoległe wysyłanie podgrafów” | Konstruktor, który węzeł może zwrócić, aby odrodzić N równoległych wykonań węzła docelowego. |
| Podgraf | „Skompilowany wykres jako węzeł” | Skompilowany StateGraph używany jako węzeł na innym wykresie; zachowuje swój własny zakres państwowy. |

## Dalsze czytanie

- [Dokumentacja LangGraph](https://langchain-ai.github.io/langgraph/) — kanoniczne odniesienie do StateGraph, reduktorów, punktów kontrolnych i przerwań.
- [Pojęcia LangGraph: stan, reduktory, punkty kontrolne](https://langchain-ai.github.io/langgraph/concepts/low_level/) — model mentalny używany w tej lekcji, prosto ze źródła.
- [LangGraph Persistence and Checkpoints](https://langchain-ai.github.io/langgraph/concepts/persistence/) — szczegóły dotyczące sklepów Postgres/SQLite/Redis, przestrzeni nazw punktów kontrolnych i identyfikatorów wątków.
- [LangGraph Human-in-the-loop](https://langchain-ai.github.io/langgraph/concepts/human_in_the_loop/) — `interrupt_before`, `interrupt_after`, `Command(resume=...)` i wzorzec stanu edycji.
- [Yao i in., „ReAct: Synergizing Reasoning and Acting in Language Models” (ICLR 2023)](https://arxiv.org/abs/2210.03629) — wzorzec implementowany przez każdego agenta LangGraph; przeczytaj to, aby uzyskać uzasadnienie śledzenia.
– [Anthropic — Tworzenie skutecznych agentów (grudzień 2024 r.)](https://www.anthropic.com/research/building-efektywne-agents) — które kształty wykresów (łańcuch, router, orkiestrator-pracownicy, oceniający-optymalizator) preferować i kiedy.
- Faza 11 · 09 (Wywoływanie funkcji) — prymityw wywołania narzędzia, którego używa ponownie każdy węzeł agenta LangGraph.
- Faza 11 · 14 (Model Context Protocol) — wykrywanie narzędzi zewnętrznych, które podłącza się do LangGraph `ToolNode` poprzez adapter MCP.
- Faza 11 · 17 (kompromisy w ramach agenta) — kiedy wybrać LangGraph zamiast CrewAI, AutoGen lub Agno.