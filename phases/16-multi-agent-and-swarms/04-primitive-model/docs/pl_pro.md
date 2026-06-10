# Prymitywny model wieloagentowy

> Każda platforma wieloagentowa wydana w 2026 roku — AutoGen, LangGraph, CrewAI, OpenAI Agents SDK, Microsoft Agent Framework — stanowi po prostu punkt w czterowymiarowej przestrzeni projektowej. Przestrzeń tę definiują zaledwie cztery elementy podstawowe (prymitywy): agent, przekazanie (handoff), stan współdzielony (shared state) oraz orkiestrator. W tej lekcji zbudujemy je od zera, uruchomimy uproszczony system oparty na wszystkich czterech, a następnie zamapujemy wiodące frameworki na te same cztery osie, co pozwoli Ci zrozumieć architekturę dowolnej nowej biblioteki w zaledwie kilka chwil.

**Typ:** Ucz się  
**Języki:** Python (stdlib)  
**Wymagania wstępne:** Faza 14 (Inżynieria agentów), Faza 16 · 01 (Dlaczego wieloagentowy)  
**Czas:** ~60 minut  

## Problem

Co kilka miesięcy na rynku pojawia się nowy framework wieloagentowy. AutoGen w 2023 roku, CrewAI w 2024 roku, LangGraph i OpenAI Swarm pod koniec 2024 roku, Google ADK w kwietniu 2025 roku, a Microsoft Agent Framework RC w lutym 2026 roku. Każdy z nich reklamuje się jako „jedyna właściwa abstrakcja”.

Próba nauki każdego z nich z osobna szybko doprowadzi do wypalenia. Ich interfejsy API różnią się znacząco, a specjaliści nie są zgodni nawet co do samej definicji „agent”. Jeden framework nazywa swoją pamięć współdzieloną „tablicą” (blackboard), inny „pulą komunikatów” (message pool), a jeszcze inny „grafem stanu” (StateGraph). Można odnieść wrażenie, że w tej dziedzinie panuje chaos.

W rzeczywistości tak nie jest. Pod warstwą marketingową kryją się cztery fundamentalne i stabilne prymitywy. Zrozumienie ich działania pozwoli Ci błyskawicznie przeanalizować dowolną nową platformę.

## Koncepcja

### Cztery prymitywy

1. **Agent** — instrukcja systemowa (system prompt) oraz lista dostępnych narzędzi. Jest całkowicie bezstanowy; każde wywołanie rozpoczyna się od instrukcji systemowej i aktualnej historii wiadomości.
2. **Przekazanie (Handoff)** — ustrukturyzowane przeniesienie kontroli z jednego agenta na drugiego. Mechanicznie realizowane jako wywołanie narzędzia zwracającego instancję innego agenta lub jako warunkowe przejście (conditional edge) na grafie.
3. **Stan współdzielony (Shared State)** — dowolna struktura danych, którą może odczytywać (i opcjonalnie zapisywać) więcej niż jeden agent. Może to być lista wiadomości, tablica danych, magazyn klucz-wartość lub baza wektorowa.
4. **Orkiestrator** — algorytm decydujący o tym, który agent zabierze głos jako następny. Dostępne opcje to: jawny graf przejść (deterministyczny), dynamiczny wybór za pomocą LLM, mechanizm przekazywania bezpośredniego przez wywołanie narzędzia (jak w OpenAI Swarm) lub kolejka zadań (jak w architekturach rojowych).

To definiuje całą przestrzeń projektową. Różne frameworki wybierają po prostu odmienne konfiguracje tych czterech osi, obbudowując je własną składnią.

### Mapowanie platform z 2026 roku na cztery prymitywy

| Framework | Agent | Przekazanie (Handoff) | Stan współdzielony | Orkiestrator |
|---------------|-------|---------|--------------|-------------|
| OpenAI Swarm / Agents SDK | `Agent(instructions, tools)` | Narzędzie zwraca obiekt `Agent` | Przekazywany przez wywołującego (caller) | LLM decyduje poprzez wywołanie handoffu |
| AutoGen v0.4 / AG2 | `ConversableAgent` | Wybór kolejnego mówcy w `GroupChat` | Pula wiadomości (Message Pool) | Selektor (LLM lub algorytm Round Robin) |
| CrewAI | `Agent(role, goal, backstory)` | `Process.Sequential` / `Hierarchical` | Powiązane wyniki zadań | Menedżer LLM lub statyczna kolejność |
| LangGraph | Funkcja reprezentująca węzeł | Krawędź grafu + warunek (conditional edge) | Reduktor `StateGraph` | Graf (deterministyczny) |
| Microsoft Agent Framework | Agent + wzorce orkiestracji | Zależne od wzorca | Wątek / Kontekst | Zależny od wybranego wzorca |
| Google ADK | Agent + Karta A2A | Zadanie A2A (Task) | Artefakty A2A | Decyzja hosta |

Różnice na poziomie interfejsów programistycznych wydają się duże, ale pod spodem działają te same mechanizmy.

### Dlaczego ma to znaczenie

Gdy dostrzeżesz te podstawowe elementy, porównywanie frameworków sprowadzi się do krótkiej listy pytań kontrolnych:

- Czy orkiestrator opiera się na dynamicznych decyzjach LLM (Swarm), czy też przebieg jest sztywno zdefiniowany w kodzie (LangGraph)?
- Czy stan współdzielony przechowuje pełną historię (GroupChat w AutoGen), czy jedynie jej przetworzoną projekcję (reduktory w LangGraph)?
- Czy agenci mogą modyfikować nawzajem swoje instrukcje (jak menedżer w CrewAI), czy jedynie przekazywać sobie dane (Swarm)?

Odpowiedzi na te pytania w 80% determinują, który framework najlepiej pasuje do Twojego problemu, pozwalając Ci projektować system pod kątem osi, która jest dla Ciebie najważniejsza.

### Wnioski dotyczące bezstanowości

Wszystkie prymitywy oprócz stanu współdzielonego są z założenia bezstanowe. Agent to czysta funkcja (podpowiedź + narzędzia). Handoff to wywołanie funkcji. Orkiestrator to mechanizm planujący (scheduler). **Jedynym stanowym elementem systemu jest stan współdzielony.** To w tym miejscu pojawia się większość krytycznych błędów: zatruwanie pamięci (lekcja 15), kolejność wiadomości, wersjonowanie i konflikty zapisu.

Frameworki ukrywające stan współdzielony (jak Swarm) przerzucają odpowiedzialność za jego utrzymanie na wywołującego. Frameworki centralizujące stan (np. mechanizmy checkpointingu w LangGraph czy pula wiadomości w AutoGen) ułatwiają monitorowanie systemu, ale zwiększają koszty koordynacji na poziomie implementacji stanu.

### Anatomia pojedynczego prymitywu

#### Agent

```
Agent = (system_prompt, tools, model, optional_name)
```

Brak pamięci wewnętrznej. Brak stanu. Dwóch agentów o tym samym system prompcie i narzędziach jest w pełni zamiennych. Wszelkie dane udające stan agenta w rzeczywistości znajdują się w stanie współdzielonym lub są przesyłane w ładunku przekazania (handoff).

#### Przekazanie (Handoff)

```
Handoff = (from_agent, to_agent, reason, payload)
```

Dominują trzy podejścia implementacyjne:

- **Zwracanie obiektu agenta** — dedykowane narzędzie zwraca instancję kolejnego agenta (wzorzec z OpenAI Swarm). Agenci decydują o routingu bezpośrednio w swoich definicjach narzędzi.
- **Krawędź grafu (Graph Edge)** — wzorzec z LangGraph. Krawędzie są deklaratywne; model LLM generuje wartość, a warunek w kodzie wybiera kolejny węzeł na tej podstawie.
- **Wybór mówcy (Speaker Selection)** — wzorzec z AutoGen GroupChat. Selektor (często oparty na LLM) analizuje pulę wiadomości i decyduje, kto zabierze głos jako następny.

#### Stan współdzielony (Shared State)

```
SharedState = { messages: [], artifacts: {}, context: {} }
```

Co najmniej lista wiadomości, a często także: artefakty strukturyzowane (wyniki zadań w CrewAI), typowany kontekst (reduktory w LangGraph) lub zewnętrzna pamięć (serwery MCP, bazy wektorowe).

Dwie główne topologie: **pełna pula** (każdy agent widzi każdą wiadomość) oraz **projekcja** (agenci widzą widok przefiltrowany pod kątem ich roli). Pełne pule są proste w implementacji, ale słabo się skalują. Projekcje skalują się dobrze, ale wymagają wcześniejszego zaprojektowania schematu danych.

#### Orkiestrator

```
Orchestrator = ({state, last_speaker}) -> next_agent
```

Cztery warianty:

- **Statyczny** — graf jest zdefiniowany na etapie kompilacji (deterministyczny graf w LangGraph, proces sekwencyjny w CrewAI).
- **Wybrany przez LLM** — model analizuje stan współdzielony i wybiera kolejnego agenta (AutoGen, hierarchiczny proces w CrewAI).
- **Oparty na przekazywaniu (Handoff-driven)** — bieżący agent sam decyduje o kolejnym kroku poprzez wywołanie narzędzia (Swarm).
- **Oparty na kolejce (Queue-driven)** — agenci (pracownicy) pobierają zadania ze wspólnej kolejki; brak jawnego wskazywania kolejnego wykonawcy (architektura rojowa).

### Co różni poszczególne frameworki

Po ustaleniu prymitywów pozostałe decyzje projektowe dotyczą:

- **Strategii pamięci** — ulotna kontra trwała (np. mechanizmy checkpointingu w LangGraph).
- **Granic bezpieczeństwa** — autoryzacja przekazania zadań (wzorzec Human-in-the-loop).
- **Limitów kosztów** — budżety tokenów na agenta lub na całe wykonanie.
- **Obserwowalności** — logowanie ścieżki przekazywania zadań i wersjonowanie stanu na potrzeby odtwarzania błędów (replay).

Wszystkie te funkcje są budowane na bazie czterech podstawowych prymitywów.

## Zbuduj to

W pliku `code/main.py` zaimplementowano cztery elementy podstawowe w około 150 liniach standardowego kodu w Pythonie. W celu uproszczenia nie używamy rzeczywistych modeli LLM — każdy agent posiada zdefiniowaną w kodzie logikę decyzyjną (policy), dzięki czemu uwaga skupia się na samej strukturze koordynacji.

Zdefiniowane klasy i funkcje:

- `Agent` — struktura przechowująca nazwę, instrukcję systemową, listę narzędzi oraz funkcję wykonawczą.
- `Handoff` — mechanizm przekazania, zwracający kolejnego agenta.
- `SharedState` — pula wiadomości bezpieczna dla wątków.
- `Orchestrator` — trzy warianty planisty: `StaticOrchestrator`, `HandoffOrchestrator` oraz symulowany `LLMSelectorOrchestrator`.

Demo uruchamia ten sam potok złożony z trzech agentów (badanie → pisanie → recenzja) przy użyciu trzech różnych typów orkiestratorów, po czym prezentuje stan puli wiadomości. Zauważysz, że wyniki różnią się jedynie sposobem wyboru kolejnego wykonawcy; sami agenci oraz stan współdzielony pozostają identyczni.

Uruchomienie:

```
python3 code/main.py
```

## Użyj tego

W pliku `outputs/skill-primitive-mapper.md` zdefiniowano umiejętność, która analizuje bazę kodu lub dokumentację dowolnego frameworka wieloagentowego i generuje jego mapowanie na cztery podstawowe prymitywy. Użyj jej do szybkiego zrozumienia architektury nowo wydanej biblioteki przed przystąpieniem do szczegółowej lektury dokumentacji API.

## Wyślij to

Przed wdrożeniem nowego frameworka przygotuj dla niego mapowanie na cztery prymitywy. Jeśli nie jesteś w stanie tego zrobić, oznacza to, że dokumentacja jest niekompletna lub framework próbuje zdefiniować piąty prymityw (co zdarza się niezwykle rzadko — upewnij się, czy nie jest to po prostu odmiana stanu współdzielonego).

Umieść to mapowanie w dokumentacji architektury swojego projektu. Udostępnij je nowym członkom zespołu przed lekturą dokumentacji API. Przy aktualizacji wersji frameworka porównuj zmiany na poziomie tego mapowania, a nie tylko sam changelog.

## Ćwiczenia

1. Uruchom `code/main.py` i zmodyfikuj zasady działania agentów. Zaobserwuj, jak zmiana typu orkiestratora wpływa na to, którzy agenci są wywoływani.
2. Zaimplementuj czwarty typ orkiestratora: sterowany kolejką (Queue-driven), w którym agenci samodzielnie odpytują stan współdzielony w poszukiwaniu nowych zadań. Zidentyfikuj ryzyko zakleszczenia (deadlock) i opisz sposób jego wykrywania.
3. Przeanalizuj przewodnik szybkiego startu LangGraph (https://docs.langchain.com/oss/python/langgraph/workflows-agents) i rozpisz go na cztery podstawowe prymitywy. Które elementy LangGraph mapują się w relacji 1:1, a które są jedynie wygodnymi wrapperami?
4. Zapoznaj się z przykładami w OpenAI Swarm (https://developers.openai.com/cookbook/examples/orchestrating_agents). Wskaż, który z czterech prymitywów sprawia, że Swarm jest tak ergonomiczny, a który przerzuca odpowiedzialność na programistę.
5. Znajdź w tabeli framework, który całkowicie ukrywa stan współdzielony. Opisz problemy, jakie pojawiają się, gdy agenci muszą koordynować przekazywanie zadań bez możliwości odczytania historii wiadomości.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Agent | „Model LLM z narzędziami” | Trójka: `(system_prompt, tools, model)`. Z założenia bezstanowy. |
| Przekazanie (Handoff) | „Przeniesienie kontroli” | Strukturalne wskazanie kolejnego agenta i ładunku. Implementowane jako zwrócenie obiektu, przejście grafu lub wybór mówcy. |
| Stan współdzielony | „Pamięć” / „kontekst” | Jedyny stanowy element systemu wieloagentowego. Pula wiadomości lub wspólna tablica danych. |
| Orkiestrator | „Koordynator” | Algorytm wyboru kolejnego agenta (graf statyczny, selektor LLM, przekazywanie bezpośrednie lub kolejka). |
| Prymityw | „Abstrakcja” | Jedna z czterech osi parametryzujących architekturę każdego frameworka wieloagentowego. |
| Pula wiadomości (Message Pool) | „Wspólna historia czatu” | Stan współdzielony przechowujący pełną historię wiadomości. Prosty w użyciu, ale słabo skalowalny. |
| Projekcja stanu | „Widok w zakresie” | Przefiltrowany, dostosowany do roli widok stanu współdzielonego. Ułatwia skalowanie kosztem projektu schematu. |
| Wybór mówcy | „Kto mówi jako następny” | Wzorzec orkiestracji, w którym dedykowana funkcja (często LLM) wybiera kolejnego agenta z grupy. |

## Dalsze czytanie

- [OpenAI Cookbook: Orchestrating Agents](https://developers.openai.com/cookbook/examples/orchestrating_agents) — klarowne omówienie wzorca orkiestracji opartej na przekazywaniu (handoff).
- [Dokumentacja AutoGen](https://microsoft.github.io/autogen/stable/) — GroupChat i dynamiczny wybór mówcy jako punkt odniesienia dla orkiestracji wybieranej przez LLM.
- [LangGraph Workflows & Agents](https://docs.langchain.com/oss/python/langgraph/workflows-agents) — opis orkiestracji opartej na krawędziach grafu i reduktorach stanu.
- [CrewAI Framework](https://docs.crewai.com/en/introduction) — rola, cel i profil agentów, procesy sekwencyjne oraz hierarchiczne.
- [AG2 (AutoGen Community Edition)](https://github.com/ag2ai/ag2) — aktywnie rozwijana wersja AutoGen po zmianach organizacyjnych w Microsoft.
