# Kompromisy w ramach Agent Framework — LangGraph vs CrewAI vs AutoGen vs Agno

> Każdy framework sprzedaje to samo demo (agent badawczy tworzy raport) i ukrywa ten sam błąd (schemat stanu walczy z warstwą orkiestracji). Wybierz framework, którego abstrakcje odpowiadają kształtowi Twojego problemu; wszystko inne to klej, który piszesz dwa razy.

**Typ:** Ucz się
**Języki:** Python
**Wymagania wstępne:** Faza 11 · 09 (Wywołanie funkcji), Faza 11 · 16 (LangGraph)
**Czas:** ~45 minut

## Problem

Masz zadanie, które wymaga więcej niż jednego połączenia LLM. Być może jest to proces badawczy (planowanie, wyszukiwanie, podsumowanie, cytowanie). Być może jest to potok przeglądu kodu (analiza różnic, krytyka, łatanie, sprawdzanie poprawności). Być może jest to wieloobrotowy asystent, który rezerwuje loty, pisze e-maile i sporządza raporty z wydatków. Wybierasz framework.

Trzy dni później odkrywasz wyciek abstrakcji frameworku. CrewAI przydziela ci role, ale walczy z tobą, gdy „badacz” musi przekazać ustrukturyzowany plan „pisarzowi”. AutoGen umożliwia czatowanie między agentami, ale nie ma stanu najwyższej klasy, więc Twój punkt kontrolny to tylko dziennik rozmów. LangGraph daje wykres stanu, ale zmusza do nazwania każdego przejścia, zanim dowiesz się, co zrobi agent. Agno oferuje abstrakcję jednego agenta, która krzyczy, gdy próbujesz rozłożyć wachlarz na trzech równoczesnych pracowników.

Rozwiązaniem nie jest „wybranie najlepszego frameworka”. Ma to na celu dopasowanie podstawowej abstrakcji frameworka do kształtu problemu. Ta lekcja rysuje tę mapę.

## Koncepcja

![Macierz struktury agenta: abstrakcja rdzenia a kształt problemu](../assets/framework-matrix.svg)

W krajobrazie roku 2026 dominują cztery ramy. Ich podstawowe abstrakcje nie są takie same.

| Ramy | Abstrakcja rdzenia | Najlepsze dopasowanie | Najgorsze dopasowanie |
|----------|--------------------------------|----------|---------------|
| **LangGraf** | `StateGraph` — wpisany stan, węzły, krawędzie warunkowe, wskaźnik kontrolny. | Przepływy pracy z jawnym stanem i przerwaniami typu „człowiek w pętli”; agenci produkcyjni wymagający debugowania podróży w czasie. | Luźna burza mózgów oparta na rolach, gdzie topologia jest nieznana. |
| **ZałogaAI** | `Crew` — role (cel, historia), zadania, proces (sekwencyjny lub hierarchiczny). | Przepływ pracy oparty na odgrywaniu ról lub osobie z krótkim planem liniowym/hierarchicznym. | Wszystko, co wykracza poza historię tur załogi; złożone rozgałęzienia. |
| **AutoGen** | `ConversableAgent` para — dwóch lub więcej agentów, którzy mówią na zmianę, aż do warunku wyjścia. | *Dialog* wieloagentowy (nauczyciel-uczeń, wnioskodawca-krytyk, aktor-recenzent), w którym myślenie wyłania się z czatu. | Deterministyczne przepływy pracy ze znanym DAG; wszystko, co wymaga trwałego stanu po ponownym uruchomieniu. |
| **Agno** | `Agent` — pojedynczy LLM + narzędzia + pamięć, z możliwością łączenia w zespoły. | Szybkie tworzenie pojedynczych agentów i lekkich zespołów; silna multimodalność i wbudowane sterowniki pamięci masowej. | Głębokie, wyraźnie rozgałęzione wykresy z niestandardowymi reduktorami. |

### Co właściwie oznacza „abstrakcja”.

Podstawową abstrakcją frameworka jest rzecz, którą rysujesz na tablicy podczas przedstawiania architektury.

- **LangGraph** → rysujesz wykres. Węzły to kroki, krawędzie to przejścia, a obiekt stanu w każdym punkcie jest wpisywany. Model mentalny jest maszyną stanów.
- **CrewAI** → rysujesz schemat organizacyjny. Każda rola ma opis stanowiska, a menedżer wyznacza zadania. Model mentalny to mały zespół specjalistów.
- **AutoGen** → losujesz Slack DM. Dwóch agentów pisze do siebie wiadomości; trzecia dołącza, jeśli potrzebujesz moderatora. Model mentalny to czat.
- **Agno** → rysujesz pojedyncze pudełko z wiszącymi na nim narzędziami. Ustaw pudełka obok siebie dla drużyny. Model mentalny to „agent z bateriami w zestawie”.

### Pytanie o stan

Stan to miejsce, w którym większość wyborów ramowych ulega awarii w produkcji.

- **LangGraph.** Stan wpisany (`TypedDict` lub model Pydantic), reduktory według pól, punkt kontrolny pierwszej klasy (SQLite/Postgres/Redis). Wznawianie, przerywanie i podróże w czasie są bezpłatne. *(Patrz faza 11 · 16.)*
- **CrewAI.** Stan przepływa pomiędzy zadaniami w postaci ciągów znaków za pośrednictwem pola `context` lub jest uporządkowany poprzez `output_pydantic`. Brak trwałego magazynu dla załogi; uciekasz sam, jeśli załoga musi przetrwać ponowne uruchomienie.
- **AutoGen.** Stan to historia czatów i dowolne `context` zdefiniowane przez użytkownika. Zapisy rozmów pozostają zachowane; dowolny stan przepływu pracy nie, chyba że napiszesz adaptery.
- **Agno.** Wbudowane sterowniki pamięci masowej (SQLite, Postgres, Mongo, Redis, DynamoDB) dołączone do `Agent` poprzez `storage=` — sesje rozmów i wspomnienia użytkowników są zachowywane automatycznie. Nie jest to pełny punkt kontrolny wykresu; sklep sesyjny.

### Pytanie rozgałęziające

Każdy nietrywialny agent rozgałęzia się. Kto decyduje o branży, ma znaczenie.

- **LangGraph** — Ty decydujesz, korzystając z krawędzi warunkowych. Routing to funkcja Pythona z nazwanymi gałęziami. Gałęzie są pierwszorzędne na sporządzonym wykresie; punkt kontrolny rejestruje, która gałąź została wykorzystana.
- **CrewAI** – menadżer decyduje w trybie hierarchicznym; w trybie sekwencyjnym decydujesz w czasie kompilacji. Routing jest ukryty na liście zadań; poza podpowiedzią menedżera nie ma pierwszorzędnego „jeśli”.
- **AutoGen** — agenci podejmują decyzję za pośrednictwem czatu. Rozgałęzianie wynika z tego, kto mówi dalej. `GroupChatManager` wybiera następnego mówcę; możesz napisać ręcznie `speaker_selection_method`, ale domyślnie jest to oparte na LLM.
- **Agno** — agent decyduje, za pomocą którego narzędzia zadzwoni dalej. Zespoły mają tryb koordynatora/routera/współpracownika; wykraczanie poza ten zakres jest obowiązkiem programisty.

### Pytanie o obserwowalność

- **LangGraph** — OpenTelemetry za pośrednictwem LangSmith lub dowolnego eksportera Otel. Każde przejście węzła jest rozpiętością śledzenia; punkty kontrolne pełnią także funkcję odtwarzalnych śladów. LangSmith to opcja własna; Langfuse/Phoenix mają również adaptery.
- **CrewAI** — najwyższej klasy OpenTelemetry od końca 2025 roku; integracje z Langfuse, Phoenix, Opik, AgentOps.
- **AutoGen** — integracja z OpenTelemetry poprzez `autogen-core`; AgentOps i Opik mają złącza. Szczegółowość śledzenia dotyczy komunikatu agenta, a nie węzła.
- **Agno** — wbudowana flaga `monitoring=True` plus eksportery OpenTelemetry; ścisła integracja z Langfuse w celu śledzenia sesji.

### Koszt i opóźnienie

Wszystkie cztery platformy dodają narzut na połączenie (logika struktury, sprawdzanie poprawności, serializacja). Przybliżona kolejność rosnących kosztów ogólnych: Agno ≈ LangGraph < CrewAI ≈ AutoGen. Różnica jest zdominowana przez ilość dodatkowego routingu LLM, jaki wykonuje framework. Hierarchiczny menedżer CrewAI wydaje tokeny, decydując, kto będzie następny; AutoGen `GroupChatManager` podobnie. LangGraph wydaje tokeny tylko tam, gdzie piszesz `llm.invoke`. Ścieżka Agno z jednym agentem jest cienka.

Gdy liczy się koszt wykonania, preferuj routing jawny (krawędzie LangGraph, AutoGen `speaker_selection_method`) zamiast routingu wybranego przez LLM.

### Interoperacyjność

- **LangGraph** ↔ **LangChain** narzędzia, retrievery, LLM. Pierwszorzędny adapter MCP (narzędzia importowane jako serwery MCP).
- **CrewAI** ↔ narzędzia dziedziczą z `BaseTool`; Narzędzia LangChain, narzędzia LlamaIndex i narzędzia MCP dostosowują się. Delegowanie między załogami za pośrednictwem `allow_delegation=True`.
- **AutoGen** → `FunctionTool` otacza dowolne wywołanie Pythona; Dostępny adapter MCP. Ścisłe powiązanie z ekosystemem AG2 dla wzorców agent-agent.
- **Agno** → `@tool` dekorator lub podklasa BaseTool; Adapter MCP; narzędzia można udostępniać agentom i zespołom.

## Umiejętność

> Możesz w jednym zdaniu wyjaśnić, dlaczego dany framework jest odpowiedni dla danego problemu agenta.

Lista kontrolna przed kompilacją:

1. **Narysuj kształt.** Czy to wykres (stan wpisany, nazwane przejścia)? Odgrywanie ról (specjaliści przekazują pracę)? Czat (agenci rozmawiają do końca)? Pojedynczy agent z narzędziami?
2. **Zdecyduj, kto będzie rozgałęział.** Rozgałęzianie wybierane przez programistę → LangGraph. Decyzja menedżera-agenta → Hierarchiczna CrewAI. Pojawiające się na czacie → AutoGen. Decyzja o wywołaniu narzędzia → Agno.
3. **Sprawdź budżet państwa.** Potrzebujesz CV z punktu kontrolnego? Podróż w czasie? Człowiek przerywa w połowie biegu? Jeśli tak, LangGraph jest ustawieniem domyślnym; Sesje Agno obejmują stan o zasięgu konwersacji.
4. **Sprawdź budżet kosztów.** Wybrany przez LLM routing kosztuje dodatkowe tokeny na turę. Jeśli agent działa tysiące razy dziennie, preferuj routing jawny.
5. **Zaplanuj budżet na framework.** Każdy framework jest inną zależnością. Jeśli zadaniem są dwa wywołania LLM i narzędzie, napisz 30 linii zwykłego Pythona; żaden framework nie jest tańszy niż brak frameworka.

Odmawiaj sięgania po framework, zanim będziesz mógł narysować wykres, schemat organizacyjny, czat lub skrzynkę agenta. Odmawiaj wyboru takiego, który zmusza cię do walki z jego modelem stanu o rzecz, której naprawdę potrzebujesz.

## Matryca decyzyjna

| Kształt problemu | Preferowane ramy | Dlaczego |
|--------------|-------|-----|
| DAG przepływu pracy z wpisanym stanem, zatwierdzeniami człowieka, długotrwałymi | LangGraph | Stan pierwszej klasy, punkt kontrolny, przerwania, podróże w czasie. |
| Prace badawcze/pisarskie z różnymi rolami | Podgrafy CrewAI (sekwencyjne) lub LangGraph | Podział roli na zadanie jest tani do wyrażenia w CrewAI; zwiększaj skalę dzięki LangGraph, gdy rozgałęzianie staje się skomplikowane. |
| Dialog wnioskodawca-krytyk lub nauczyciel-uczeń | AutoGen | Czat dwuagentowy to jego natywny kształt. |
| Pojedynczy agent z narzędziami, sesjami, pamięcią | Agno | Najcieńsza konfiguracja, wbudowana pamięć i pamięć. |
| Tysiące równoległych rozwinięć z reduktorami | LangGraph + `Send` | Jedyny z najwyższej klasy interfejsem API do przesyłania równoległego. |
| Szybki prototyp, bez zobowiązań ramowych | Zwykły Python + SDK dostawcy | Żaden framework nie jest najszybszym frameworkiem. |

## Ćwiczenia

1. **Łatwo.** Podejmij to samo zadanie — „przeszukaj siedzibę Anthropic, napisz brief na 200 słów, cytuj źródła” — i zaimplementuj je w LangGraph (cztery węzły: planowanie, wyszukiwanie, pisanie, cytowanie) i w CrewAI (trzy role: badacz, pisarz, redaktor). Raportuj koszt tokena na uruchomienie i wiersze kodu.
2. **Medium.** Zbuduj to samo zadanie w AutoGen (czat badacza ↔ pisarza, redaktor dołącza przez `GroupChat`) i Agno (pojedynczy agent z `search_tools` i `write_tools` oraz magazyn sesji). Oceń cztery implementacje pod względem (a) kosztu uruchomienia, (b) możliwości wznowienia działania po awarii, (c) możliwości wprowadzenia zgody człowieka przed etapem zapisu.
3. **Trudne.** Zbuduj skrypt drzewa decyzyjnego `pick_framework.py`, który pobiera krótki opis problemu (JSON: `{has_typed_state, has_roles, has_dialogue, has_parallel_fanout, needs_resume}`) i zwraca rekomendację z uzasadnieniem w jednym zdaniu. Sprawdź to na sześciu zaprojektowanych przez siebie przypadkach.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Orkiestracja | „Jak agenci koordynują działania” | Warstwa decydująca, który węzeł/rola/agent będzie następny. |
| Stan trwały | „Wznów po ponownym uruchomieniu” | Stan, który przetrwa śmierć procesu, dołączony do punktu kontrolnego lub magazynu sesji. |
| Routing wybrany przez LLM | „Niech zdecyduje model” | Planista LLM wybiera następny krok w każdej turze; elastyczny, ale płaci tokeny za każdą decyzję. |
| Jawne routing | „Deweloper decyduje” | Funkcja Pythona lub statyczna krawędź wybiera następny krok; tanie i sprawdzone. |
| Załoga | „Zespół CrewAI” | Role + zadania + proces (sekwencyjny lub hierarchiczny) powiązane w jeden plik uruchamialny. |
| Czat grupowy | „Czat wieloagentowy AutoGen” | Zarządzana rozmowa pomiędzy N agentami z selektorem mówców. |
| Zespół (Agno) | „Wieloagentowy Agno” | Tryb kierowania/koordynowania/współpracy za pośrednictwem zestawu agentów. |
| Wykres stanu | „Wykres LangGrapha” | Wpisany stan, węzeł, krawędź warunkowa, abstrakcja punktu kontrolnego. |

## Dalsze czytanie

- [Dokumentacja LangGraph](https://langchain-ai.github.io/langgraph/) — StateGraph, punkty kontrolne, przerwania, podróże w czasie.
- [Dokumentacja CrewAI](https://docs.crewai.com/) — Załogi, przepływy, agenci, zadania, procesy.
- [Dokumentacja AutoGen](https://microsoft.github.io/autogen/) — ConversableAgent, GroupChat, zespoły, narzędzia.
- [Dokumentacja Agno](https://docs.agno.com/) — Agent, zespół, przepływ pracy, pamięć, pamięć.
— [Anthropic — Tworzenie skutecznych agentów (grudzień 2024 r.)](https://www.anthropic.com/research/building-efektywne-agents) — biblioteka wzorców (szybkie łączenie, routing, równoległość, Orchestrator-workers, Evaluator-optimizer) framework-agnostic.
– [Yao i in., „ReAct: Synergizing Reasoning and Acting” (ICLR 2023)](https://arxiv.org/abs/2210.03629) — pętla, którą ubiera każdy framework.
- [Wu i in., „AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation” (2023)](https://arxiv.org/abs/2308.08155) — artykuł projektowy AutoGen.
- [Park i in., „Generative Agents: Interactive Simulacra of Human Behaviour” (UIST 2023)] (https://arxiv.org/abs/2304.03442) — podstawa odgrywania ról, na której opierają się stosy osobowości w stylu CrewAI.
- Faza 11 · 16 (LangGraph) — ramy, do których odnosi się ta lekcja.
- Faza 11 · 19 (Refleksja) — wzór, który jest dobrze odwzorowany na LangGraph, ale niezdarnie na CrewAI.
- Faza 11 · 22 (obserwowalność produkcji) – jak instrumentować dowolną wybraną platformę.