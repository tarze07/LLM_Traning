# Prymitywny model wieloagentowy

> Każda platforma wieloagentowa, która zostanie dostarczona w 2026 r. — AutoGen, LangGraph, CrewAI, OpenAI Agents SDK, Microsoft Agent Framework — będzie punktem w czterowymiarowej przestrzeni projektowej. Cztery elementy podstawowe, nic więcej: agent, przekazanie, stan współdzielony, orkiestrator. W tej lekcji budujemy je od zera, uruchamiamy system zabawek na wszystkich czterech, a następnie mapujemy wszystkie główne frameworki na te same osie, dzięki czemu można przeczytać każdą nową wersję w jednym akapicie.

**Typ:** Ucz się
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 14 (Inżynieria agentów), Faza 16 · 01 (Dlaczego wieloagentowa)
**Czas:** ~60 minut

## Problem

Co sześć miesięcy dostarczana jest nowa platforma wieloagentowa. AutoGen w 2023 r. CrewAI w 2024 r. LangGraph i OpenAI Swarm w 2024 r. Google ADK w kwietniu 2025 r. Microsoft Agent Framework RC w lutym 2026 r. Każdy komunikat prasowy twierdzi, że jest „właściwą abstrakcją”.

Jeśli będziesz próbował się ich uczyć pojedynczo, wypalisz się. Interfejsy API wyglądają inaczej. Lekarze nie są zgodni co do tego, czym jest „agent”. Jedna struktura nazywa swoją pamięć współdzieloną „tablicą”, inna „pulą komunikatów”, a jeszcze trzecia „StateGraphem”. Zaczynasz podejrzewać, że pole się po prostu burzy.

Tak nie jest. Pod marketingiem kryją się cztery prymitywy, które są stabilne. Naucz się ich raz, przeczytaj każdy nowy framework w jednym akapicie.

## Koncepcja

### Cztery prymitywy

1. **Agent** — monit systemowy plus lista narzędzi. bezpaństwowiec; każde uruchomienie rozpoczyna się od monitu systemowego i bieżącej historii komunikatów.
2. **Przekazanie** — zorganizowane przeniesienie kontroli z jednego agenta na drugiego. Mechanicznie: wywołanie narzędzia, które zwraca nowego agenta lub krawędź wykresu zgodną z warunkiem.
3. **Stan współdzielony** — dowolna struktura danych, którą może odczytać (czasami zapisać) więcej niż jeden agent. Pula wiadomości, tablica, magazyn klucz-wartość, pamięć wektorowa.
4. **Orkiestrator** — od tego, kto zdecyduje, kto będzie mówił dalej. Opcje: jawny wykres (deterministyczny), selektor mówcy LLM (miękki), wywołanie przekazania ostatniego mówcy (OpenAI Swarm) lub harmonogram w kolejce (architektura roju).

To cała przestrzeń projektowa. Każdy framework wybiera wartości domyślne dla każdej osi; reszta to składnia powierzchniowa.

### Jak nawiązuje do tego każda platforma z 2026 r

| Ramy | Agent | Przekazanie | Stan udostępniony | Orkiestrator |
|---------------|-------|---------|--------------|-------------|
| OpenAI Swarm / Agents SDK | `Agent(instructions, tools)` | narzędzie zwraca Agenta | problem dzwoniącego | następne wezwanie do przekazania LLM |
| AutoGen v0.4 / AG2 | `ConversableAgent` | wybór głośników w GroupChat | pula wiadomości | funkcja selektora (LLM lub okrężna) |
| ZałogaAI | `Agent(role, goal, backstory)` | `Process.Sequential / Hierarchical` | Wyniki zadań powiązane | menadżer LLM lub zamówienie statyczne |
| LangGraph | funkcja węzła | krawędź wykresu + warunek | `StateGraph` reduktor | wykres, deterministyczny |
| Struktura agenta Microsoft | agent + wzorce orkiestracji | specyficzny dla wzoru | wątek / kontekst | specyficzny dla wzoru |
| ADK Google | agent + karta A2A | Zadanie A2A | Artefakty A2A | gospodarz decyduje |

Różnice powierzchni wyglądają na ogromne. Pod spodem: te same cztery pokrętła.

### Dlaczego to ma znaczenie

Gdy zobaczysz elementy podstawowe, porównanie frameworków stanie się krótką listą kontrolną:

— Czy orkiestrator ufa LLM w zakresie trasowania (Swarm), czy też przypina routing w kodzie (LangGraph)?
- Czy udostępniony stan ma pełną historię (GroupChat) czy prognozowany (reduktor StateGraph)?
- Czy agenci mogą modyfikować wzajemne polecenia (menedżer CrewAI) lub tylko przekazywać informacje (Swarm)?

Te trzy pytania odpowiadają w 80%, które ramy pasują do danego problemu. Przestajesz kupować „najlepszy framework wieloagentowy” i zaczynasz projektować pod oś, na której Ci naprawdę zależy.

### Bezstanowy wgląd

Każdy prymityw z wyjątkiem stanu współdzielonego jest bezstanowy. Agent jest funkcją (podpowiedź, narzędzia). Handoff jest wywołaniem funkcji. Orchestrator to osoba planująca. **Jedyną stanową rzeczą w systemie jest stan współdzielony.** To tam występują wszystkie interesujące błędy: zatruwanie pamięci (lekcja 15), porządkowanie komunikatów, wersjonowanie, rywalizacja o zapis.

Struktury ukrywające stan współdzielony (Rój) przekazują problem osobie dzwoniącej. Ramy, które go centralizują (punkt kontrolny LangGraph, pula AutoGen) umożliwiają inspekcję, ale przenoszą koszty koordynacji na implementację stanu współdzielonego.

### Anatomia pojedynczego prymitywu

####Agencie

```
Agent = (system_prompt, tools, model, optional_name)
```

Brak pamięci. Brak stanu. Dwóch agentów z tym samym monitem systemowym i narzędziami jest wymiennych. Wszystko, co wygląda jak stan poszczególnych agentów, jest w rzeczywistości w stanie udostępnionym lub w protokole przekazania.

#### Przekazanie

```
Handoff = (from_agent, to_agent, reason, payload)
```

Dominują trzy wdrożenia:

- **Funkcja powrotu** — narzędzie zwraca kolejnego agenta. To jest wzorzec OpenAI Swarm. Agenci wykonują routing w swoich schematach narzędzi.
- **Krawędź wykresu** — LangGraph. Krawędzie są deklaratywne. LLM generuje wartość; warunek wybiera następny węzeł.
- **Wybór głośników** — Czat grupowy AutoGen. Funkcja selektora (czasami będąca wywołaniem LLM) odczytuje pulę i wybiera osobę, która będzie mówić jako następna.

#### Stan udostępniony

```
SharedState = { messages: [], artifacts: {}, context: {} }
```

Przynajmniej lista wiadomości. Często więcej: artefakty strukturalne (wyjścia zadań CrewAI), kontekst wpisany (reduktory LangGraph), pamięć zewnętrzna (MCP, wektor DB).

Dwie topologie: **pełna pula** (każdy agent widzi każdą wiadomość) i **projekcja** (agenci widzą widok ograniczony do roli). Pełne pule są proste i źle skalowane. Przewidywane pule skalują się, ale wymagają wstępnego zaprojektowania schematu.

#### Orkiestrator

```
Orchestrator = ({state, last_speaker}) -> next_agent
```

Cztery smaki:

- **Statyczny** — wykres jest stały w czasie kompilacji (deterministyczny LangGraph, sekwencyjny CrewAI).
- **Wybrany przez LLM** — LLM odczytuje pulę i wybiera następnego mówcę (AutoGen, CrewAI Hierarchical).
- **Oparta na przekazaniu** — aktualny agent decyduje, wywołując narzędzie przekazywania (Rój).
- **Oparty na kolejce** — pracownicy pobierają dane ze wspólnej kolejki; brak wyraźnego następnego mówcy (architektura roju, Matrix).

### Jakie zmiany pomiędzy frameworkami

Po naprawieniu prymitywów pozostałe decyzje projektowe to:

- **Strategia pamięci** — efemeryczne a trwałe punkty kontrolne (punkt kontrolny LangGraph).
- **Granica bezpieczeństwa** — kto może zatwierdzić przekazanie (człowiek w pętli).
- **Rachunek kosztów** — budżety tokenów na agenta.
- **Obserwowalność** — śledzenie przekazań, utrzymywanie stanu do powtórki.

Wszystko możliwe do wdrożenia na elementach pierwotnych. Żaden z nich nie jest nowym prymitywem.

## Zbuduj to

`code/main.py` implementuje cztery elementy podstawowe w ~150 liniach standardowego Pythona. Żadnego prawdziwego LLM – każdy agent ma opisaną politykę, więc uwaga pozostaje skupiona na strukturze koordynacyjnej.

Eksport pliku:

- `Agent` — klasa danych zawierająca nazwę, monit systemowy, narzędzia, funkcję polityki.
- `Handoff` — funkcja zwracająca nowego agenta.
- `SharedState` — pula komunikatów bezpieczna dla wątków.
- `Orchestrator` — trzy warianty: `StaticOrchestrator`, `HandoffOrchestrator`, `LLMSelectorOrchestrator` (symulowane).

Wersja demonstracyjna uruchamia ten sam potok składający się z trzech agentów (badanie → zapis → recenzja) przez wszystkie trzy typy koordynatorów i na końcu drukuje pulę komunikatów. Możesz zobaczyć, że wyniki różnią się tylko tym, kto wybiera następny*; agenci i stan współdzielony są identyczne w różnych przebiegach.

Uruchom to:

```
python3 code/main.py
```

Oczekiwany wynik: trzy uruchomienia programu Orchestrator, po jednym na wzorzec. Każdy drukuje ostateczną pulę komunikatów. Przebieg oparty na przekazywaniu informacji dociera do mniejszej liczby agentów, jeśli badacz zdecyduje, że zostanie przeprowadzony wcześniej – to kompromis w zakresie routingu LLM w miniaturze.

## Użyj tego

`outputs/skill-primitive-mapper.md` to umiejętność, która odczytuje dowolną wieloagentową bazę kodu lub dokument frameworka i zwraca mapowanie czterech prymitywów. Uruchom go w nowej wersji frameworka, aby zapoznać się z jednym akapitem przed dogłębnym zapoznaniem się z dokumentacją.

## Wyślij to

Przed przyjęciem nowego frameworka napisz dla niego pierwotne mapowanie. Jeśli nie możesz, dokumenty są niekompletne lub framework wymyśla piąty element podstawowy (rzadko — sprawdź, czy nie widziałeś wersji stanu współdzielonego).

Przypnij mapowanie w dokumencie architektury. Gdy dołączy nowy członek zespołu, wyślij mu mapowanie przed dokumentacją API. Gdy zmieniają się wersje frameworka, różnicuj mapowanie, a nie dziennik zmian.

## Ćwiczenia

1. Uruchom `code/main.py` trzy razy z różnymi zasadami agenta. Obserwuj, jak wybór koordynatora zmienia uruchamianych agentów.
2. Zaimplementuj czwarty typ orkiestratora: sterowany kolejką, w którym agenci odpytują stan współdzielony pod kątem pracy. Jaki impas może wystąpić i jak go wykryć?
3. Skorzystaj z przewodnika szybkiego startu LangGraph (https://docs.langchain.com/oss/python/langgraph/workflows-agents) i przepisz go jako cztery elementy podstawowe. Które z abstrakcji LangGrapha mapują 1:1, a które są wygodnymi opakowaniami?
4. Przeczytaj książkę kucharską OpenAI Swarm (https://developers.openai.com/cookbook/examples/orchestrating_agents). Zidentyfikuj, który z czterech prymitywów sprawia, że ​​Swarm jest najbardziej ergonomiczny, a który przekazuje dzwoniącemu.
5. Znajdź w tej tabeli jedną strukturę, która całkowicie ukrywa stan współdzielony. Wyjaśnij, jakie przerwy występują, gdy agenci muszą koordynować przekazania bez ponownego czytania historii.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Agent | „LLM z narzędziami” | `(system_prompt, tools, model)` potrójny. Bezpaństwowiec. |
| Przekazanie | „Przekazanie kontroli” | Wywołanie strukturalne, które podaje nazwę następnego agenta i opcjonalnego ładunku. Trzy implementacje: powrót funkcji, krawędź wykresu, wybór głośników. |
| Stan udostępniony | „Pamięć” / „kontekst” | Jedyna stanowa część systemu wieloagentowego. Pula wiadomości lub tablica. |
| Orkiestrator | „Koordynator” | Ktokolwiek zdecyduje, kto będzie następny. Wykres statyczny, selektor LLM, sterowany przekazywaniem lub sterowany kolejką. |
| Prymitywny | „Abstrakcja” | Jedna z czterech osi parametryzowanych przez każdą platformę. Nie jest to funkcja frameworka. |
| Pula wiadomości | „Wspólna historia czatów” | Stan udostępniony z pełną historią. Łatwo to uzasadnić, źle się skaluje. |
| Przewidywany stan | „Widok w zakresie” | Widok stanu udostępnionego specyficzny dla roli. Skaluje, wymaga projektu schematu. |
| Wybór głośników | „Kto będzie mówił dalej” | Wzorzec Orchestrator, w którym funkcja (często LLM) wybiera następnego agenta z grupy. |

## Dalsze czytanie

- [Książka kucharska OpenAI: Agenci orkiestrujący — procedury i przekazywanie](https://developers.openai.com/cookbook/examples/orchestrating_agents) — najjaśniejsze przedstawienie orkiestracji opartej na przekazywaniu poleceń
- [Dokumentacja stabilnej wersji AutoGen](https://microsoft.github.io/autogen/stable/) — GroupChat + wybór głośników stanowi punkt odniesienia dla orkiestracji wybranej przez LLM
- [Przepływy pracy i agenci LangGraph](https://docs.langchain.com/oss/python/langgraph/workflows-agents) — orkiestracja krawędzi wykresu i stan współdzielony oparty na reduktorach
- [Wprowadzenie do CrewAI](https://docs.crewai.com/en/introduction) — agenci roli, celu, historii, procesy sekwencyjne/hierarchiczne
– [AG2 (kontynuacja społeczności AutoGen)](https://github.com/ag2ai/ag2) — aktywna linia AutoGen v0.2 po tym, jak Microsoft przeniósł wersję 0.4 do konserwacji