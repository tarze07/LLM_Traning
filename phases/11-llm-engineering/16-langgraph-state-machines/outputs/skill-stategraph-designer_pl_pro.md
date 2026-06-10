---

name: stategraph-designer
description: Przekształć zadanie agenta w obiekt LangGraph StateGraph z nazwanymi węzłami, typowanym stanem, reduktorami (reducers), mechanizmem zapisu stanu (checkpointer) i punktami przerwania na interwencję człowieka (human-in-the-loop).
version: 1.0.0
phase: 11
lesson: 16
tags: [langgraph, stategraph, checkpointer, interrupt, time-travel, react-agent, human-in-the-loop]

---

Na podstawie zadania agenta (celu użytkownika, dostępnych narzędzi, oczekiwanej liczby tur, skutków ubocznych o określonym bezpiecznym promieniu rażenia, wymagań dotyczących trwałości stanu, docelowego limitu opóźnień) wygeneruj:

1. Listę węzłów (nodes). Nazwij każdy odrębny krok: wywołanie LLM (reasoning), uruchomienie narzędzia (tool execution), krok weryfikacji przez człowieka (human review), krok podsumowania/krytyki czy pobierania danych (retrieval). Odrzuć projekt, jeśli jakikolwiek węzeł odpowiada za więcej niż jedno zadanie – w takim przypadku należy go podzielić.
2. Schemat stanu (state schema). Pola `TypedDict` (lub Pydantic) z reduktorem (reducer) dla każdej listy. Dziennik wiadomości (message log) powinien być zawsze opatrzony adnotacją `Annotated[list, add_messages]`. Wyodrębnij z historii wiadomości wszelkie listy specyficzne dla danego zadania (np. plan działania, licznik budżetu, listę pobranych dokumentów), aby reduktory działały poprawnie przy równoległych aktualizacjach.
3. Mapę krawędzi (edges). Krawędzie statyczne (gdy kolejny krok jest deterministyczny) oraz krawędzie warunkowe z nazwaną funkcją routującą (tylko wtedy, gdy model wybiera kolejny krok). Odrzuć każdy graf, w którym funkcja routująca wymaga nowego wywołania LLM, które nie zostało jeszcze wykonane w poprzednim węźle.
4. Punkty przerwania (interrupts). Zastosuj `interrupt_before` (przerwanie przed) na każdym węźle z nieodwracalnymi skutkami ubocznymi (zapisy, usunięcia, płatności, kosztowne wywołania zewnętrznych API). Użyj `interrupt_after` (przerwanie po) w węźle modelu, jeśli walidacja danych wyjściowych odbywa się w osobnym procesie. Odrzuć `interrupt_after` w węzłach generujących skutki uboczne – w ich przypadku na przerwane działanie jest już za późno.
5. Mechanizm zapisu stanu (checkpointer). Używaj `MemorySaver` wyłącznie do testów. Wybierz `PostgresSaver`, `SQLiteSaver` lub `RedisSaver` dla środowisk produkcyjnych, które muszą zachować stan po ponownym uruchomieniu serwera. Określ strategię `thread_id` (na użytkownika, na sesję, na rozmowę) oraz czas życia (TTL) punktu kontrolnego.

Nigdy nie wdrażaj grafu LangGraph bez checkpointera. Brak checkpointera uniemożliwia wstrzymywanie/wznawianie działania, podróż w czasie (time travel) oraz interwencję człowieka w pętli. Nigdy nie definiuj pola wiadomości bez `add_messages` – w przeciwnym razie kolejny zapis po cichu nadpisze poprzedni i połowa historii rozmowy zniknie. Odrzuć graf, w którym każde przejście jest krawędzią warunkową sterowaną przez planistę LLM (taki schemat to w zasadzie AutoGen generujący niepotrzebne koszty tokenów w każdej turze).

Przykładowe dane wejściowe: „Agent obsługujący zwroty oparty na modelu Anthropic Claude z trzema narzędziami (lookup_order, issue_refund, send_email); musi zatrzymać się i czekać na akceptację człowieka przed dokonaniem jakiegokolwiek zwrotu powyżej 100 USD; stan musi zostać zachowany po restarcie serwera; budżet opóźnienia p95 wynosi 8 sekund”.

Przykładowe dane wyjściowe:
- Węzły: `agent` (wywołanie LLM), `lookup_tool`, `refund_tool`, `email_tool`, `human_review`.
- Stan: `messages` (z `add_messages`), `order_context` (nadpisywanie), `refund_amount` (nadpisywanie), `reviewer_decision` (nadpisywanie).
- Krawędzie: router `should_continue` z węzła `agent` kierujący do gałęzi: `lookup_tool`, `refund_tool`, `email_tool`, `human_review`, `END`. Węzły narzędzi wracają do węzła `agent`.
- Przerwania: `interrupt_before` dla węzła `refund_tool`, gdy `refund_amount > 100`. Brak przerw przed `lookup_tool` oraz `email_tool`.
- Checkpointer: `PostgresSaver` ze strategią `thread_id` w formacie `"user:{user_id}:case:{case_id}"` oraz 30-dniowym TTL.
