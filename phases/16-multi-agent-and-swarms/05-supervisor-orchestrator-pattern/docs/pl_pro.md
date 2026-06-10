# Wzorzec nadzorcy (Supervisor / Orchestrator-Worker)

> Jeden główny agent planuje i deleguje zadania, a wyspecjalizowani pracownicy wykonują je w odrębnych, równoległych kontekstach i raportują wyniki. To podejście stoi za systemem badawczym firmy Anthropic (Claude Opus 4 jako lider, Sonnet 4 jako subagenci), który według wewnętrznych testów wykazuje wzrost dokładności o +90,2% w porównaniu z jednym agentem Opus 4. W analizie inżynieryjnej Anthropic wskazuje, że aż 80% zmienności w teście BrowseComp wynika z samego sposobu użycia tokenów — architektura wieloagentowa wygrywa głównie dzięki temu, że każdy podagent otrzymuje czyste, świeże okno kontekstowe. W tej lekcji zbudujemy wzorzec nadzorcy od podstaw oraz omówimy wnioski inżynieryjne z wdrożeń produkcyjnych.

**Typ:** Ucz się + Buduj  
**Języki:** Python (stdlib, `threading`)  
**Wymagania wstępne:** Faza 16 · 04 (Model prymitywny)  
**Czas:** ~75 minut  

## Problem

Analiza literatury i głębokie badania to typowe zadania, na których załamują się systemy jednoagentowe. Wyobraź sobie zapytanie: „Co zmieniło się w systemach wieloagentowych w latach 2023–2026?”. Pojedynczy agent czyta kolejno pięć artykułów naukowych, zapełniając nimi połowę swojego kontekstu, po czym musi dokonać ich syntezy. Zanim przeanalizuje piąty tekst, zapomina o szczegółach pierwszego. Ponadto proces ten nie może być zrównoleglony.

Wzorzec nadzorcy skutecznie rozwiązuje ten problem: jeden wiodący agent (Lead) planuje proces wyszukiwania informacji, deleguje szczegółowe pytania cząstkowe do dedykowanych pracowników (Workers), a następnie dokonuje syntezy ich odpowiedzi. Każdy z pracowników otrzymuje własne, czyste okno o rozmiarze 200 tysięcy tokenów na opracowanie jednego, konkretnego pytania. Agent wiodący nigdy nie analizuje surowych dokumentów źródłowych — zapoznaje się jedynie ze zwięzłymi streszczeniami przygotowanymi przez pracowników.

System badawczy Anthropic wykazał wzrost skuteczności o +90,2% w porównaniu z pojedynczym modelem Opus 4. Zauważono, że 80% tej różnicy wynika z *samego zarządzania oknem kontekstowym*. Głównym czynnikiem sukcesu jest świeży, niezanieczyszczony kontekst dla każdego subagenta.

## Koncepcja

### Wzorzec w praktyce

```
                  ┌──────────────┐
                  │     Lead     │  planuje, dekomponuje zadania,
                  │   (Opus 4)   │  dokonuje syntezy
                  └──┬────┬───┬──┘
                     │    │   │
             ┌───────┘    │   └───────┐
             ▼            ▼           ▼
       ┌─────────┐  ┌─────────┐  ┌─────────┐
       │ Worker1 │  │ Worker2 │  │ Worker3 │
       │(Sonnet) │  │(Sonnet) │  │(Sonnet) │
       └─────────┘  └─────────┘  └─────────┘
         świeży       świeży       świeży
         kontekst     kontekst     kontekst
```

Agent wiodący (Lead) nigdy nie czyta surowych danych. Pracownicy nie wiedzą o swoim wzajemnym istnieniu, dopóki Lead nie przystąpi do syntezy ich raportów. Każde połączenie przekazuje jedynie konkretny, wąski artefakt danych.

### Dlaczego to podejście wygrywa

Decydują o tym trzy mechanizmy:

1. **Czysty kontekst na podagenta.** Pracownik badający np. „dziedzictwo FIPA-ACL” nie jest obciążony 40 tysiącami tokenów zużytymi wcześniej na planowanie całego procesu. Otrzymuje pełne okno na analizę wyłącznie jednego pytania.
2. **Specjalizacja instrukcji (system promptów).** Instrukcja dla agenta wiodącego brzmi „podziel zadanie i dokonaj syntezy”, a nie „przeprowadź badania”. Podpowiedzi dla pracowników są precyzyjnie zawężone: „znajdź, co zmieniło się w aspekcie X”. Konkretne instrukcje dają precyzyjne wyniki.
3. **Równoległość wykonania.** Pracownicy realizują swoje zadania w tym samym czasie. Rzeczywisty czas wykonania wynosi w przybliżeniu `max(czasy_pracowników) + planowanie + synteza`, a nie `sum(czasy_pracowników)`.

### Wnioski inżynieryjne (Anthropic)

Wnioski z wdrożeń produkcyjnych:

- **Skalowanie wysiłku do złożoności zapytania (Effort scaling).** Proste zapytania powinny być obsługiwane przez jednego agenta wykonującego 3–10 wywołań narzędzi. Złożone problemy wymagają orkiestracji powyżej 10 agentów. Szacowania trudności powinien dokonywać agent wiodący, a nie wywołujący system programista.
- **Od ogółu do szczegółu (Wide-then-narrow).** Najpierw podziel zadanie na ogólne pytania pomocnicze, a następnie twórz wyspecjalizowanych pracowników do pogłębienia konkretnych wątków.
- **Wdrożenia typu Rainbow (tęczowe).** Agenci działają w sposób długotrwały i stanowy, dlatego klasyczne wdrożenia niebiesko-zielone (blue-green) się nie sprawdzają. Stosuje się podejście Rainbow: nowe wersje agentów są wprowadzane stopniowo, podczas gdy starsze instancje dokończają swoje trwające procesy.
- **Zużycie tokenów dominuje w kosztach.** Wariant wieloagentowy generuje około 15-krotnie większe zużycie tokenów niż pojedynczy agent. Stosuj go tylko wtedy, gdy wartość zadania uzasadnia te koszty.

### Ewolucja zaleceń w LangGraph

Pierwotnie LangGraph oferował bibliotekę `langgraph-supervisor` z wysokopoziomową funkcją pomocniczą `create_supervisor`. Obecnie zaleca się realizację wzorca nadzorcy poprzez bezpośrednie wywoływanie narzędzi (tool calling). Daje to programiście pełną kontrolę nad tym, *jakie dane trafiają do kontekstu nadzorcy* (inżynieria kontekstu). Starsza biblioteka nadal działa, lecz nowa dokumentacja promuje podejście oparte na wywołaniach narzędzi.

### Typowe tryby awarii

- **Halucynacje nadzorcy dotyczące planu.** Jeśli Lead wygeneruje pytania cząstkowe, które nie pokrywają się z istotą głównego problemu, pracownicy przeprowadzą poprawne badania pod kątem niewłaściwego celu.
- **Pracownicy wykraczający poza zakres.** Bez sztywno zdefiniowanych granic pracownicy zbaczają z przypisanych im tematów, zanieczyszczając etap syntezy nadmiarowymi lub powtórzonymi danymi.
- **Konflikty na etapie syntezy.** Dwaj pracownicy dostarczają sprzeczne fakty. Agent wiodący musi w takiej sytuacji dopytać wykonawców (dodać kolejną rundę) lub wyraźnie odnotować brak spójności w raporcie końcowym. Najgorszym błędem jest ciche wybranie jednej z wersji, przez co użytkownik nie dowiaduje się o rozbieżnościach.

### Kiedy wzorzec nadzorcy się nie sprawdza

- **Zadania ściśle sekwencyjne.** Jeśli krok 2 bezwzględnie wymaga danych wejściowych z kroku 1, równoległe uruchomienie agentów nie przyniesie żadnych korzyści. Wtedy właściwym wyborem jest potok (CrewAI Sequential lub liniowy graf w LangGraph).
- **Proste zapytania.** Jeden agent obsłuży je szybciej i znacznie taniej. Przed uruchomieniem orkiestratora zastosuj test oceny złożoności zadania.
- **Ścisły determinizm.** Nadzorca podejmuje decyzje dynamicznie za pomocą LLM. Jeśli kluczowy jest audyt i powtarzalność ścieżki wykonania, lepszym wyborem będą grafy statyczne.

## Zbuduj to

W pliku `code/main.py` zaimplementowano wzorzec nadzorcy zarządzającego trzema równoległymi pracownikami przy użyciu modułu `threading`. Agent wiodący dzieli główne zapytanie na pytania pomocnicze, pracownicy przetwarzają je równolegle, po czym Lead dokonuje ostatecznej syntezy. Zamiast rzeczywistych modeli LLM, pracownicy posługują się prostym skryptem symulującym pobieranie i syntezę danych.

Kluczowe kroki:
- `Lead.plan(query)` dzieli zapytanie na 3 pytania pomocnicze.
- `Worker.run(sub_q)` zwraca wygenerowane podsumowanie.
- `Lead.run(query)` uruchamia pracowników w odrębnych wątkach, zbiera dane i tworzy raport końcowy.

Uruchomienie:

```
python3 code/main.py
```

W konsoli wyświetli się plan, równoległe logi pracowników ze znacznikami czasu oraz raport z syntezy. Zauważysz korzyść czasową: trzech pracowników wykonujących zadania przez 0,3 sekundy kończy pracę w około 0,35 sekundy (zamiast 0,9 sekundy w trybie sekwencyjnym).

## Użyj tego

W pliku `outputs/skill-supervisor-designer.md` zdefiniowano umiejętność, która analizuje zapytanie użytkownika i projektuje dla niego architekturę nadzorcy: instrukcje systemowe dla lidera i pracowników, reguły dekompozycji oraz szablony syntezy raportów. Użyj jej przed rozpoczęciem budowy systemu agentowego o profilu badawczym.

## Wyślij to

Lista kontrolna przed wdrożeniem produkcyjnym wzorca nadzorcy:

- **Dobór modeli (Model pairing).** Do roli nadzorcy wybierz model o najwyższych możliwościach rozumowania (klasa Opus, `o3`). Do ról pracowników przypisz modele szybsze i tańsze (Sonnet, `o4-mini`).
- **Limity czasowe pracowników (Timeouts).** Pracownik przekraczający dwukrotność średniego czasu wykonania powinien być automatycznie zatrzymywany. Nadzorca decyduje wtedy o ponownym uruchomieniu z węższym zakresem lub o syntezie na podstawie pozostałych danych.
- **Limity tokenów na pracownika.** Sztywne ograniczenie liczby tokenów (np. 10-krotność oczekiwanego wejścia) zapobiega niekontrolowanemu zużyciu budżetu przez zapętlonego agenta.
- **Obserwowalność.** Rejestruj plan nadzorcy, logi wywołań narzędzi każdego z pracowników oraz wejście i wyjście etapu syntezy. To podstawa debugowania systemów wieloagentowych.
- **Wdrożenia typu Rainbow.** Długotrwale działające, stanowe agenty wymagają strategii stopniowego wygaszania starszych wersji, a nie natychmiastowego zastępowania kodu w locie.

## Ćwiczenia

1. Uruchom `code/main.py`, a następnie zmodyfikuj kod, aby uruchomić 5 pracowników zamiast 3. Zaobserwuj czasy wykonania. Przy jakiej liczbie agentów narzut na zarządzanie wątkami zaczyna przewyższać korzyści z zrównoleglenia zadań?
2. Zaimplementuj mechanizm timeoutu: zatrzymaj każdego pracownika, który działa dłużej niż 0,5 sekundy, i poleć nadzorcy dokonanie syntezy na podstawie niepełnych danych. Jakie metryki są potrzebne, aby wykryć takie zdarzenie?
3. Dodaj detekcję sprzeczności do etapu syntezy: jeśli pracownicy zwrócą sprzeczne informacje, nadzorca musi to wyraźnie zaraportować, zamiast wybierać losowo jedną z opcji. Jak zaimplementować takie wykrywanie bez kosztownego wywoływania LLM?
4. Przeanalizuj artykuł inżynieryjny Anthropic o systemach badawczych. Wskaż trzy mechanizmy ochronne, które należałoby wdrożyć w naszej demonstracji, aby nadawała się do pracy w środowisku produkcyjnym.
5. Porównaj starszą funkcję `create_supervisor` z LangGraph z nowoczesnym podejściem opartym na bezpośrednim wywoływaniu narzędzi. Dlaczego Anthropic przekazuje do syntezy wyłącznie przetworzone odpowiedzi pracowników, a nie ich pełne, surowe okna kontekstowe?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Nadzorca (Supervisor) | „Agent lider” | Agent orkiestrujący, który odpowiada za planowanie, delegowanie zadań i syntezę wyników. Nie wykonuje pracy bezpośredniej. |
| Pracownik (Worker) | „Subagent” | Wyspecjalizowany agent o wąskim zakresie odpowiedzialności, uruchamiany w odrębnym oknie kontekstowym. |
| Czysty kontekst | „Fresh window” | Kontekst pracownika inicjowany wyłącznie jego instrukcją systemową i zadanym pytaniem pomocniczym. |
| Wdrożenie Rainbow | „Płynne wersjonowanie” | Strategia wdrażania agentów stanowych polegająca na pozwoleniu starym instancjom na dokończenie zadań przed ich wygaszeniem. |
| Zużycie tokenów | „Koszt kontekstu” | Główny składnik kosztowy systemów wieloagentowych. Praca w tym wzorcu zużywa około 15-krotnie więcej tokenów niż pojedynczy agent. |
| Skalowanie wysiłku | „Effort scaling” | Dobór liczby subagentów dynamicznie przez nadzorcę w zależności od ocenionej trudności pytania. |
| Konflikt syntezy | „Sprzeczność danych” | Sytuacja, w której raporty pracowników zawierają wykluczające się fakty; nadzorca musi ujawnić tę rozbieżność w raporcie. |

## Dalsze czytanie

- [Anthropic Engineering: Building a research system](https://www.anthropic.com/engineering/multi-agent-research-system) — referencyjny opis wdrożenia produkcyjnego wzorca nadzorcy.
- [LangGraph Workflows & Agents](https://docs.langchain.com/oss/python/langgraph/workflows-agents) — zalecenia dotyczące realizacji orkiestracji za pomocą bezpośrednich wywołań narzędzi.
- [Dokumentacja referencyjna LangGraph Supervisor](https://reference.langchain.com/python/langgraph-supervisor) — opis starszego pomocnika `create_supervisor`.
- [OpenAI Cookbook: Orchestrating Agents](https://developers.openai.com/cookbook/examples/orchestrating_agents) — wariant nadzorcy zaimplementowany przy użyciu bezpośredniego przekazywania zadań (handoff).
