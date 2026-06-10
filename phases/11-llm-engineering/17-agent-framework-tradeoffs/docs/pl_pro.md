# Analiza porównawcza frameworków agentowych: LangGraph vs CrewAI vs AutoGen vs Agno

> Każdy framework oferuje to samo demo (agent badawczy generujący raport) i ukrywa tę samą wadę (schemat stanu koliduje z warstwą orkiestracji). Wybierz framework, którego abstrakcje odpowiadają specyfice Twojego problemu; wszystko inne to kod łączący (boilerplate), który będziesz musiał napisać dwukrotnie.

**Typ:** Ucz się
**Języki:** Python
**Wymagania wstępne:** Faza 11 · 09 (Wywołanie funkcji), Faza 11 · 16 (LangGraph)
**Czas:** ~45 minut

## Problem

Masz zadanie, które wymaga wykonania wielu zapytań do LLM. Może to być proces badawczy (planowanie, wyszukiwanie, podsumowanie, cytowanie źródeł), potok przeglądu kodu (analiza diffów, krytyka, generowanie łatki, walidacja) lub wieloturowy asystent rezerwujący loty, piszący e-maile i sporządzający raporty z wydatków. Stajesz przed wyborem frameworku.

Trzy dni później zderzasz się z nieszczelną abstrakcją (leaky abstraction) wybranego narzędzia. CrewAI narzuca strukturę opartą na rolach, ale utrudnia przekazanie ustrukturyzowanego planu od „badacza” do „autora”. AutoGen ułatwia komunikację między agentami, ale brakuje mu natywnego zarządzania stanem, przez co punkt kontrolny (checkpointer) staje się zwykłym logiem rozmowy. LangGraph udostępnia graf stanu, ale wymaga jawnego zdefiniowania każdego przejścia, zanim jeszcze dowiesz się, co zrobi agent. Agno oferuje prostą abstrakcję pojedynczego agenta, która przestaje się sprawdzać, gdy chcesz rozproszyć zadania (fan-out) na trzech równoległych wykonawców.

Rozwiązaniem nie jest poszukiwanie „najlepszego frameworku”, lecz dopasowanie jego podstawowej abstrakcji do specyfiki problemu. Ta lekcja pomoże Ci sporządzić taką mapę drogową.

## Koncepcja

![Macierz struktury agenta: abstrakcja rdzenia a kształt problemu](../assets/framework-matrix.svg)

W 2026 roku na rynku dominują cztery frameworki, z których każdy oferuje inne fundamentalne podejście.

| Framework | Główna abstrakcja | Kiedy sprawdza się najlepiej | Kiedy sprawdza się najgorzej |
|----------|--------------------------------|----------|---------------|
| **LangGraph** | `StateGraph` — typowany stan, węzły, krawędzie warunkowe, checkpointer. | Przepływy pracy z jawnym zarządzaniem stanem i punktami przerwania na interwencję człowieka (human-in-the-loop); agenci produkcyjni wymagający debugowania historycznych stanów (time-travel). | Luźne burze mózgów oparte na rolach, gdzie topologia przepływu jest dynamiczna i nieznana z góry. |
| **CrewAI** | `Crew` — role (cel, backstory), zadania, proces (sekwencyjny lub hierarchiczny). | Przepływy pracy oparte na odgrywaniu ról (personas) z prostym, liniowym lub hierarchicznym planem działania. | Scenariusze wymagające czegoś więcej niż prostej historii interakcji agentów; skomplikowane rozgałęzienia. |
| **AutoGen** | Para `ConversableAgent` — co najmniej dwóch agentów wymieniających komunikaty aż do spełnienia warunku wyjścia. | *Dialog* wieloagentowy (nauczyciel-uczeń, generator-krytyk, wykonawca-recenzent), gdzie wnioskowanie wynika z samej konwersacji. | Deterministyczne przepływy pracy oparte na z góry znanym grafie (DAG); scenariusze wymagające trwałego stanu odpornego na restarty serwera. |
| **Agno** | `Agent` — pojedynczy LLM + narzędzia + pamięć, z opcją łączenia w zespoły (teams). | Szybki prototyp pojedynczego agenta lub prostego zespołu; natywna obsługa multimodalności i wbudowane sterowniki baz danych (storage). | Złożone grafy o głębokiej strukturze rozgałęzień z własnymi reduktorami (reducers). |

### Co właściwie oznacza „abstrakcja”

Podstawową abstrakcją frameworka jest schemat, który rysujesz na tablicy podczas projektowania architektury.

- **LangGraph** → Rysujesz graf. Węzły to kroki, krawędzie to przejścia, a obiekt stanu w każdym punkcie jest typowany. Model mentalny to maszyna stanów.
- **CrewAI** → Rysujesz schemat organizacyjny. Każda rola ma opis stanowiska, a menedżer przydziela zadania. Model mentalny to mały zespół specjalistów.
- **AutoGen** → Rysujesz czat grupowy. Dwóch agentów wymienia wiadomości, a trzeci dołącza w razie potrzeby jako moderator. Model mentalny to konwersacja.
- **Agno** → Rysujesz pojedynczy blok z podłączonymi narzędziami. Możesz ustawić kilka takich bloków obok siebie, tworząc zespół. Model mentalny to „agent z bateriami w zestawie”.

### Kwestia zarządzania stanem

Zarządzanie stanem to obszar, w którym większość frameworków zawodzi na produkcji.

- **LangGraph:** Typowany stan (`TypedDict` lub model Pydantic), reduktory przypisane do pól, natywny checkpointer (SQLite/Postgres/Redis). Wznawianie działania, punkty przerwania oraz podróże w czasie (time-travel) są dostępne out-of-the-box. *(Patrz faza 11 · 16).*
- **CrewAI:** Stan jest przekazywany między zadaniami w postaci ciągów znaków (poprzez pole `context`) lub strukturyzowany za pomocą `output_pydantic`. Brak wbudowanej trwałości stanu dla całej grupy agentów; musisz samodzielnie zaimplementować obsługę błędów w razie restartu serwera.
- **AutoGen:** Stanem jest historia czatu oraz dowolny zdefiniowany przez użytkownika `context`. Zapisy rozmów są zachowywane, ale stan samego przepływu pracy już nie, chyba że napiszesz własne adaptery.
- **Agno:** Wbudowane sterowniki pamięci masowej (SQLite, Postgres, Mongo, Redis, DynamoDB) są bezpośrednio połączone z obiektem `Agent` poprzez argument `storage=` — sesje rozmów i pamięć użytkowników są automatycznie utrwalane. Nie jest to jednak pełne migawki grafu stanu, a jedynie baza sesji.

### Kwestia rozgałęzień (routingu)

Każdy zaawansowany system agentowy wymaga rozgałęzień. Kluczowe jest to, kto podejmuje decyzję o wyborze ścieżki.

- **LangGraph** — Decyzję podejmuje programista za pomocą krawędzi warunkowych (conditional edges). Routing to zwykła funkcja Pythona zwracająca nazwy kolejnych węzłów. Rozgałęzienia są pełnoprawnymi elementami grafu, a checkpointer dokładnie rejestruje, która ścieżka została wybrana.
- **CrewAI** — Decyzję podejmuje agent-menedżer (w trybie hierarchicznym) lub jest ona zdefiniowana w czasie kompilacji (w trybie sekwencyjnym). Routing jest ukryty w liście zadań; poza promptami menedżera nie ma tu natywnej logiki warunkowej.
- **AutoGen** — Decyzje zapadają w trakcie rozmowy. Rozgałęzianie zależy od tego, który agent zabierze głos jako następny. Obiekt `GroupChatManager` wybiera kolejnego rozmówcę; możesz napisać własną metodę `speaker_selection_method`, ale domyślnie decyduje o tym LLM.
- **Agno** — Agent decyduje, które narzędzie wywołać w następnej kolejności. Zespoły agentów mają predefiniowane tryby współpracy (koordynator, router, współpracownik); bardziej złożona logika leży po stronie programisty.

### Kwestia obserwowalności (observability)

- **LangGraph** — Obsługuje OpenTelemetry przez LangSmith lub dowolny inny eksporter OTel. Każde przejście między węzłami jest rejestrowane jako span w śledzeniu; punkty kontrolne ułatwiają dokładne odtwarzanie przebiegów. Obok LangSmitha dostępne są również adaptery dla narzędzi takich jak Langfuse czy Phoenix.
- **CrewAI** — Natywna obsługa OpenTelemetry wprowadzona pod koniec 2025 roku; integracje z platformami Langfuse, Phoenix, Opik oraz AgentOps.
- **AutoGen** — Integracja z OpenTelemetry przez bibliotekę `autogen-core`; dostępne są konektory do AgentOps i Opik. Śledzenie odbywa się na poziomie komunikatów agenta, a nie węzłów grafu.
- **Agno** — Wbudowana flaga `monitoring=True` oraz eksportery OpenTelemetry; ścisła integracja z Langfuse do śledzenia sesji.

### Koszt i opóźnienia

Każdy z czterech frameworków wprowadza pewien narzut wydajnościowy (logika sterująca, walidacja, serializacja). Przybliżony porządek od najmniejszego do największego narzutu: Agno ≈ LangGraph < CrewAI ≈ AutoGen. Różnica ta wynika głównie z liczby dodatkowych wywołań LLM wykonywanych pod maską przez dany framework. Menedżer hierarchiczny w CrewAI oraz `GroupChatManager` w AutoGen zużywają tokeny na samą decyzję o tym, kto ma wykonać kolejny krok. LangGraph wykonuje połączenia z LLM tylko wtedy, gdy jawnie wywołasz `llm.invoke`. Podejście Agno z pojedynczym agentem charakteryzuje się minimalnym narzutem.

Gdy koszty operacyjne mają kluczowe znaczenie, wybieraj routing jawny (krawędzie w LangGraph, własne reguły `speaker_selection_method` w AutoGen) zamiast routingu dynamicznego sterowanego przez LLM.

### Interoperacyjność

- **LangGraph** ↔ Narzędzia, retrievery i modele z ekosystemu **LangChain**. Natywny adapter MCP (narzędzia importowane bezpośrednio jako serwery MCP).
- **CrewAI** ↔ Narzędzia dziedziczące po klasie `BaseTool`; możliwość adaptacji narzędzi z LangChain, LlamaIndex oraz MCP. Delegowanie zadań między załogami realizowane przez flagę `allow_delegation=True`.
- **AutoGen** ↔ Klasa `FunctionTool` opakowuje dowolną funkcję Pythona; dostępny jest adapter MCP. Ścisła integracja z ekosystemem AG2 dla wzorców komunikacji międzyagentowej.
- **Agno** ↔ Dekorator `@tool` lub klasa pochodna `BaseTool`; adapter MCP; łatwe udostępnianie narzędzi między agentami i zespołami.

## Umiejętność w praktyce

> Powinieneś potrafić w jednym zdaniu wyjaśnić, dlaczego dany framework pasuje do konkretnego problemu.

Lista kontrolna przed rozpoczęciem prac projektowych:

1. **Zdefiniuj strukturę grafu.** Czy problem przypomina graf (typowany stan, jawne przejścia)? Odgrywanie ról (przekazywanie zadań między specjalistami)? Czat grupowy (swobodna dyskusja agentów)? Czy pojedynczego agenta z narzędziami?
2. **Określ, kto kontroluje routing.** Routing zdefiniowany przez programistę → LangGraph. Decyzja agenta-menedżera → Hierarchiczny tryb CrewAI. Swobodny przepływ w konwersacji → AutoGen. Wybór narzędzia przez agenta → Agno.
3. **Przeanalizuj wymagania dotyczące stanu.** Czy potrzebujesz wznawiania działania z punktu kontrolnego? Podróży w czasie (time-travel)? Wstrzymywania pracy na akceptację człowieka? Jeśli tak, domyślnym wyborem jest LangGraph. W przypadku prostszych interakcji sesyjnych wystarczą wbudowane bazy danych Agno.
4. **Oceń budżet kosztów.** Routing realizowany przez LLM zużywa dodatkowe tokeny w każdej turze. Jeśli Twój agent wykonuje tysiące zadań dziennie, postaw na routing jawny.
5. **Oszacuj narzut biblioteki.** Każdy framework to dodatkowa zależność w projekcie. Jeśli całe zadanie składa się z dwóch zapytań do LLM i jednego narzędzia, napisz 30 linii w czystym Pythonie – żaden framework nie będzie tańszy i szybszy niż jego brak.

Unikaj sięgania po framework, dopóki nie będziesz w stanie jednoznacznie rozrysować topologii systemu na tablicy. Odrzuć każde narzędzie, które zmusza Cię do walki z jego mechanizmem zarządzania stanem w celu implementacji kluczowych funkcji biznesowych.

## Matryca decyzyjna

| Specyfika problemu | Sugerowany framework | Uzasadnienie |
|--------------|-------|-----|
| Przepływ pracy jako DAG z typowanym stanem, akceptacją człowieka i trwałością długoterminową | LangGraph | Natywne wsparcie dla zarządzania stanem, checkpointerów, punktów przerwania i podróży w czasie. |
| Zadania badawcze/redakcyjne z podziałem na role | CrewAI (sekwencyjnie) lub podgrafy LangGraph | Podział ról i zadań jest bardzo prosty do wyrażenia w CrewAI; przejdź na LangGraph, gdy logika rozgałęzień stanie się skomplikowana. |
| Konwersacja typu generator-krytyk lub nauczyciel-uczeń | AutoGen | Swobodny dialog między dwoma agentami to natywna struktura tego frameworku. |
| Pojedynczy agent z narzędziami, sesjami i pamięcią konwersacyjną | Agno | Najprostsza konfiguracja, wbudowane utrwalanie stanu i pamięć. |
| Tysiące równoległych operacji (fan-out) z agregacją wyników | LangGraph + `Send` | Jedyny framework z natywnym i wydajnym API do obsługi przetwarzania równoległego. |
| Szybki prototyp bez wiązania się z konkretnym frameworkiem | Czysty Python + SDK dostawcy | Brak frameworku to często najszybsza i najprostsza ścieżka. |

## Ćwiczenia

1. **Poziom łatwy.** Weź to samo zadanie — „wyszukaj informacje o siedzibie Anthropic, napisz podsumowanie na 200 słów i podaj źródła” — i zaimplementuj je w LangGraph (cztery węzły: planowanie, wyszukiwanie, pisanie, cytowanie) oraz w CrewAI (trzy role: badacz, pisarz, redaktor). Porównaj koszty tokenów na jedno uruchomienie oraz liczbę linii kodu.
2. **Poziom średni.** Zaimplementuj to samo zadanie w AutoGen (czat badacz ↔ pisarz, z redaktorem dołączającym przez `GroupChat`) oraz Agno (pojedynczy agent z zestawem narzędzi `search_tools` i `write_tools` oraz bazą sesyjną). Oceń wszystkie cztery warianty pod kątem: (a) kosztów uruchomienia, (b) odporności na awarie i możliwości wznowienia pracy, (c) łatwości wdrożenia punktu przerwania na akceptację człowieka przed etapem zapisu.
3. **Poziom trudny.** Napisz skrypt `pick_framework.py`, który na wejściu przyjmuje opis problemu w formacie JSON (np. `{has_typed_state, has_roles, has_dialogue, has_parallel_fanout, needs_resume}`) i zwraca rekomendację frameworku wraz z jednozdaniowym uzasadnieniem. Przetestuj jego działanie na sześciu zróżnicowanych przypadkach testowych.

## Kluczowe terminy

| Termin | Potoczne określenie | Co to dokładnie oznacza |
|------|-----------------|----------------------|
| Orkiestracja | „Jak agenci ze sobą współpracują” | Warstwa sterująca decydująca o tym, który węzeł, rola lub agent wykonuje kolejny krok. |
| Trwałość stanu (persistence) | „Wznawianie po restarcie” | Zapisywanie stanu w taki sposób, aby przetrwał restart procesu – powiązane z checkpointerem lub bazą sesji. |
| Routing sterowany przez LLM | „Pozwól modelowi zdecydować” | Agent planujący (LLM) wybiera kolejny krok w każdej turze; rozwiązanie elastyczne, ale generujące koszty tokenów. |
| Routing jawny (deterministryczny) | „Decyzja po stronie kodu” | Funkcja w Pythonie lub statyczne połączenie między węzłami decyduje o kolejnym kroku; rozwiązanie stabilne i tanie. |
| Załoga (Crew) | „Zespół w CrewAI” | Zestaw ról, zadań oraz proces (sekwencyjny lub hierarchiczny) połączony w jedną strukturę wykonawczą. |
| Czat grupowy (Group Chat) | „Wieloagentowy czat w AutoGen” | Konwersacja między wieloma agentami koordynowana przez selektor kolejnego rozmówcy. |
| Zespół (Team w Agno) | „Wieloagentowy zespół w Agno” | Współpraca agentów zorganizowana w trybie koordynatora, routera lub bezpośrednich pomocników. |
| Graf stanu | „Graf w LangGraph” | Maszyna stanów składająca się z typowanego stanu, węzłów, krawędzi warunkowych i checkpointera. |

## Dalsze czytanie

- [Dokumentacja LangGraph](https://langchain-ai.github.io/langgraph/) — StateGraph, checkpointery, punkty przerwania, podróż w czasie (time-travel).
- [Dokumentacja CrewAI](https://docs.crewai.com/) — Załogi, przepływy, agenci, zadania i procesy.
- [Dokumentacja AutoGen](https://microsoft.github.io/autogen/) — Klasa `ConversableAgent`, czaty grupowe, zespoły i narzędzia.
- [Dokumentacja Agno](https://docs.agno.com/) — Klasa `Agent`, zespoły, przepływy pracy, pamięć i mechanizmy składowania danych.
- [Anthropic — Building Effective Agents (Grudzień 2024)](https://www.anthropic.com/research/building-effective-agents) — Przegląd wzorców projektowych dla systemów agentowych (workflow, routing, parallelization, orchestrator-workers, evaluator-optimizer) niezależny od frameworków.
- [Yao et al., „ReAct: Synergizing Reasoning and Acting” (ICLR 2023)](https://arxiv.org/abs/2210.03629) — Publikacja opisująca podstawową pętlę wnioskowania i działania wykorzystywaną przez większość frameworków.
- [Wu et al., „AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation” (2023)](https://arxiv.org/abs/2308.08155) — Publikacja wprowadzająca architekturę AutoGen.
- [Park et al., „Generative Agents: Interactive Simulacra of Human Behavior” (UIST 2023)](https://arxiv.org/abs/2304.03442) — Praca leżąca u podstaw systemów opartych na rolach i symulacji osobowości w stylu CrewAI.
- Faza 11 · 16 (LangGraph) — Lekcja szczegółowo omawiająca ten framework.
- Faza 11 · 19 (Refleksja) — Wzorzec projektowy łatwy do wdrożenia w LangGraph, ale trudny w CrewAI.
- Faza 11 · 22 (Produkcyjna obserwowalność) — Jak monitorować i instrumentować wybrane frameworki.
