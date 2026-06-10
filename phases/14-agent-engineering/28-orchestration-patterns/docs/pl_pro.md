# Wzorce orkiestracji: Nadzorca (Supervisor), Rój (Swarm), Hierarchia (Hierarchical)

> W 2026 roku we frameworkach powtarzają się cztery wzorce orkiestracji: supervisor-worker (nadzorca-pracownik), swarm / peer-to-peer (rój / każdy z każdym), hierarchical (hierarchiczny) oraz debate (debata). Wytyczne Anthropic mówią: "Chodzi o zbudowanie odpowiedniego systemu dla Twoich potrzeb". Zacznij od najprostszego; dodawaj topologię tylko wtedy, gdy pojedynczy agent plus pięć wzorców przepływu pracy (workflow) to za mało.

**Typ:** Nauka + Budowa
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 14 · 12 (Wzorce przepływu pracy), Faza 14 · 25 (Debata wieloagentowa)
**Czas:** ~60 minut

## Cele nauczania

- Wymień cztery najpopularniejsze wzorce orkiestracji i określ przypadki użycia każdego z nich.
- Opisz rekomendacje LangChain na rok 2026: realizacja nadzoru poprzez bezpośrednie wywołania narzędzi (tool calls) kontra dedykowane biblioteki typu supervisor.
- Wyjaśnij zasadę Anthropic „zbuduj odpowiedni system do swoich potrzeb” i jej wpływ na wybór topologii.
- Zaimplementuj wszystkie cztery wzorce w oparciu o bibliotekę standardową (stdlib) z użyciem prostego, oskryptowanego modelu LLM.

## Problem

Zespoły programistów często sięgają po złożone architektury wieloagentowe (multi-agent) na wyrost, zanim pojawią się realne potrzeby biznesowe. We wszystkich najpopularniejszych frameworkach powtarzają się cztery główne wzorce orkiestracji. Ich zrozumienie pozwala na świadomy wybór właściwej topologii lub podjęcie decyzji o całkowitym zrezygnowaniu z architektury wieloagentowej.

## Koncepcja

### Nadzorca-pracownik (Orchestrator/Supervisor-Workers)

- Centralny model LLM (router) przydziela zadania wyspecjalizowanym agentom wykonawczym (workers).
- Nadzorca podejmuje decyzje: kontynuowanie własnej pracy, delegowanie zadania do specjalisty lub zakończenie procesu.
- Agenci wykonawczy nie komunikują się ze sobą bezpośrednio; całe kierowanie ruchem (routing) oraz wymiana danych przechodzą przez nadzorcę.

Frameworki: LangGraph (`create_supervisor`), wzorzec Orchestrator-Workers w Anthropic, CrewAI Hierarchical Process.

**Rekomendacja LangChain (2026):** Implementuj nadzór bezpośrednio za pomocą wywołań narzędzi (tool calls), rezygnując z gotowych abstrakcji typu `create_supervisor`. Daje to pełną kontrolę nad kontekstem przesyłanym do modeli – programista decyduje, jakie dane widzi każdy z agentów wykonawczych.

### Rój / każdy z każdym (Swarm / peer-to-peer)

- Agenci przekazują sobie zadania bezpośrednio (handoffs), korzystając ze wspólnej puli narzędzi.
- Brak centralnego routera (nadzorcy).
- Mniejsze opóźnienia (latency) w porównaniu do wzorca nadzorcy (mniejsza liczba przeskoków między modelami).
- Trudniejsze debugowanie i analiza przepływu (brak jednego, centralnego punktu kontroli).

Frameworki: topologia swarm w LangGraph, mechanizm handoffs w OpenAI Agents SDK (gdzie agenci mogą bezpośrednio przekazywać kontrolę innym).

### Hierarchiczny (Hierarchical)

- Nadzorcy zarządzają pod-nadzorcami, którzy z kolei zarządzają bezpośrednimi wykonawcami.
- Implementowany jako zagnieżdżone podgrafy (subgraphs) w LangGraph lub zagnieżdżone załogi (nested crews) w CrewAI.
- Pozwala na skalowanie systemu do dużej liczby agentów, jednak kosztem znacznego wzrostu złożoności operacyjnej.

Kiedy stosować: gdy limit tokenów kontekstu (context window) pojedynczego nadzorcy uniemożliwia pomieszczenie instrukcji i opisów wszystkich dostępnych agentów wykonawczych.

### Debata (Debate)

- Agenci generujący propozycje odpowiedzi działają równolegle, a następnie przechodzą przez rundy wzajemnej krytyki (lekcja 25).
- Technicznie nie jest to sam wzorzec orkiestracji zadań, lecz mechanizm weryfikacji i konsensusu – we frameworkach bywa jednak traktowany jako jedna z topologii.

### CrewAI: Crew vs Flow

Framework CrewAI wyróżnia dwa główne tryby organizacji pracy:

- **Flow:** przeznaczony do deterministycznej automatyzacji sterowanej zdarzeniami (event-driven) – zalecany punkt startowy dla systemów produkcyjnych.
- **Crew:** przeznaczony do autonomicznej współpracy agentów realizujących przypisane role.

Pojęcia te są niezależne od wspomnianych wcześniej czterech wzorców, ale przekładają się na topologię: Flow zazwyczaj przyjmuje postać nadzorcy lub hierarchii, natomiast Crew odpowiada strukturze nadzorcy z routerem LLM.

### Rekomendacje Anthropic

„Sukces w tworzeniu systemów LLM nie polega na zbudowaniu najbardziej skomplikowanego rozwiązania. Chodzi o zbudowanie systemu optymalnego dla Twoich konkretnych potrzeb”.

Procedura wyboru architektury:

1. **Pojedynczy agent + podstawowe przepływy pracy (workflows)** (lekcja 12) – domyślny punkt startowy.
2. **Nadzorca-pracownik (Orchestrator-Workers):** gdy wdrażasz od 2 do 4 wyspecjalizowanych agentów wykonawczych.
3. **Rój (Swarm):** gdy minimalizacja opóźnień (latency) jest ważniejsza niż pełna kontrola nad tokiem rozumowania.
4. **Hierarchiczny:** wyłącznie w sytuacjach, gdy limit kontekstu nadzorcy jest niewystarczający na opisy wszystkich specjalistów.
5. **Debata:** gdy poprawność wyniku jest kluczowa i usprawiedliwia wysokie koszty tokenów.

### Gdzie ten wzorzec może zawieść

- **Projektowanie zorientowane na architekturę zamiast na problem:** Podejmowanie decyzji o budowie systemu wieloagentowego przed zdefiniowaniem konkretnego problemu biznesowego.
- **Niekończące się przekazywanie zadań w roju (infinite loops):** Sytuacje typu Agent A -> Agent B -> Agent A -> Agent B. Wymaga to stosowania liczników przekazań (hop counters) i limitów pętli.
- **Nadmiarowa hierarchia:** Tworzenie wielu poziomów orkiestracji (np. z powodu podejścia „enterprise”), gdy w rzeczywistości wystarczą dwa proste zespoły. Należy wtedy upraszczać (spłaszczać) architekturę.

## Zbuduj to

Plik `code/main.py` implementuje wszystkie cztery wzorce w oparciu o bibliotekę standardową (stdlib):

- `Supervisor` – centralny router.
- `Swarm` – architektura peer-to-peer z bezpośrednim przekazywaniem kontroli.
- `Hierarchical` – struktura nadzorców zarządzających podległymi agentami.
- `Debate` – równolegli uczestnicy proponujący odpowiedzi z mechanizmem krytyki.

Każdy wzorzec obsługuje to samo zadanie z trzema typami intencji (zwrot, zgłoszenie błędu, sprzedaż). Generowane ślady (traces) przybierają różne formy.

Uruchomienie:

```bash
python3 code/main.py
```

Wyniki: wizualizacja śladów i metryk dla każdego wzorca. Wzorzec nadzorcy (supervisor) generuje najbardziej uporządkowane logi; rój (swarm) ma najmniej kroków pośrednich; hierarchia ma największą głębokość wywołań; debata generuje najwyższe koszty tokenów.

## Użyj tego

- **LangGraph:** do realizacji wzorców nadzorcy i hierarchii (poprzez zagnieżdżone podgrafy).
- **OpenAI Agents SDK:** do implementacji handoffs jako wywołań narzędzi (wzorzec Swarm).
- **CrewAI Flow:** do budowy produkcyjnych systemów deterministycznych.
- **Własna implementacja (Custom):** do realizacji protokołów debaty lub gdy wymagana jest precyjna kontrola nad przepływem wiadomości.

## Wyślij to

Plik `outputs/skill-orchestration-picker.md` ułatwia wybór odpowiedniej topologii i opisuje jej implementację.

## Ćwiczenia

1. Zmodyfikuj strukturę nadzorca-pracownik na strukturę roju (swarm) poprzez usunięcie centralnego routera. Zaobserwuj, jakie problemy się pojawiają, a co ulega poprawie.
2. Dodaj licznik przeskoków (hop counter) do topologii roju: zablokuj wykonanie po przekroczeniu 3 przekazań. Sprawdź, czy pozwala to wykryć zapętlenia typu Agent A -> Agent B -> Agent A.
3. Zaprojektuj dwupoziomowy system hierarchiczny dla domeny obsługującej 12 specjalistów. Wykaż, w którym miejscu limit kontekstu pojedynczego modelu uniemożliwia płaską architekturę.
4. Przeprowadź profilowanie wszystkich czterech wzorców pod kątem obciążeń produkcyjnych. Porównaj je w metrykach: opóźnienie (latency), zużycie tokenów, precyzja i łatwość debugowania.
5. Zapoznaj się z artykułem Anthropic „Building Effective Agents”. Przyporządkuj swoje dotychczasowe procesy produkcyjne do jednego z czterech wzorców. Zidentyfikuj te, które nie pasują do żadnego schematu.

## Kluczowe pojęcia

| Termin | Co potocznie się mówi | Co to oznacza w rzeczywistości |
|------|----------------|------------------------|
| Nadzorca-pracownik (Supervisor-worker) | „Router i specjaliści” | Centralny model LLM deleguje zadania do agentów wykonawczych; specjaliści nie komunikują się ze sobą bezpośrednio |
| Rój (Swarm) | „Architektura p2p” | Bezpośrednie przekazywanie zadań (handoffs) między modelami bez udziału centralnego koordynatora |
| Hierarchiczny (Hierarchical) | „Drzewo nadzorców” | Zagnieżdżona struktura orkiestracji (podgrafy) przeznaczona do obsługi dużej liczby agentów |
| Debata (Debate) | „Głosowanie z krytyką” | Równoległe generowanie propozycji i ich iteracyjna wzajemna ewaluacja (lekcja 25) |
| Nadzór oparty na wywołaniach narzędzi | „Nadzorca bez frameworka” | Ręczna implementacja routingu za pomocą standardowych wywołań funkcji w celu pełnej kontroli nad kontekstem |
| Crew (Załoga) | „Autonomiczny zespół” | Model współpracy opartej na rolach w CrewAI |
| Flow (Przepływ) | „Deterministyczny graf” | Sterowany zdarzeniami (event-driven), przewidywalny przepływ pracy w CrewAI |

## Dalsza lektura

- [Anthropic, Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) – pięć fundamentalnych wzorców orkiestracji
- [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview) – opis struktur supervisor, swarm i hierarchii
- [CrewAI docs](https://docs.crewai.com/en/introduction) – dokumentacja porównująca podejścia Crew oraz Flow
- [Du et al., Society of Minds (arXiv:2305.14325)](https://arxiv.org/abs/2305.14325) – naukowe omówienie wzorca debaty wieloagentowej
