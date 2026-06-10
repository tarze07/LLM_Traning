# Wzorce orkiestracji: Nadzorca (Supervisor), Rój (Swarm), Hierarchia (Hierarchical)

> W 2026 roku we frameworkach powtarzają się cztery wzorce orkiestracji: supervisor-worker (nadzorca-pracownik), swarm / peer-to-peer (rój / każdy z każdym), hierarchical (hierarchiczny) oraz debate (debata). Wytyczne Anthropic mówią: "Chodzi o zbudowanie odpowiedniego systemu dla Twoich potrzeb". Zacznij od najprostszego; dodawaj topologię tylko wtedy, gdy pojedynczy agent plus pięć wzorców przepływu pracy (workflow) to za mało.

**Typ:** Nauka + Budowa
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 14 · 12 (Wzorce przepływu pracy), Faza 14 · 25 (Debata wieloagentowa)
**Czas:** ~60 minut

## Cele kształcenia

- Wymienienie czterech powtarzających się wzorców orkiestracji i określenie, kiedy każdy z nich pasuje.
- Opisanie zaleceń LangChain na rok 2026: nadzór oparty na wywołaniach narzędzi (tool calls) vs biblioteki supervisor.
- Wyjaśnienie zasady Anthropic "zbuduj odpowiedni system" i tego, jak warunkuje ona wybór topologii.
- Zaimplementowanie wszystkich czterech w stdlib z użyciem wspólnego, oskryptowanego LLM.

## Problem

Zespoły sięgają po rozwiązania "wieloagentowe" (multi-agent) zanim w ogóle ich potrzebują. Cztery wzorce powtarzają się we wszystkich frameworkach; kiedy nauczysz się je nazywać, będziesz mógł wybrać właściwy — lub całkowicie zrezygnować z topologii.

## Koncepcja

### Nadzorca-pracownik (Supervisor-worker)

- Centralny LLM (router) przydziela zadania wyspecjalizowanym agentom.
- Podejmuje decyzje: zapętlenie do siebie, przekazanie do specjalisty, zakończenie.
- Specjaliści nie rozmawiają ze sobą; całe kierowanie ruchem (routing) przechodzi przez nadzorcę.

Frameworki: LangGraph `create_supervisor`, Anthropic orchestrator-workers, CrewAI Hierarchical Process.

**Zalecenie LangChain (2026):** realizuj nadzór poprzez bezpośrednie wywołania narzędzi (tool calls), a nie `create_supervisor`. Daje to dokładniejszą kontrolę nad inżynierią kontekstu — ty decydujesz, co dokładnie widzi każdy specjalista.

### Rój / każdy z każdym (Swarm / peer-to-peer)

- Agenci przekazują sobie zadania bezpośrednio przez wspólną pulę narzędzi.
- Brak centralnego routera.
- Mniejsze opóźnienia niż w przypadku nadzorcy (mniej przeskoków).
- Trudniejsze do analizowania (brak jednego punktu kontroli).

Frameworki: LangGraph swarm topology, OpenAI Agents SDK handoffs (gdy wszyscy agenci mogą przekazywać zadania wszystkim innym).

### Hierarchiczny (Hierarchical)

- Nadzorcy zarządzający sub-nadzorcami, którzy zarządzają pracownikami.
- Implementowane jako zagnieżdżone podgrafy w LangGraph; zagnieżdżone załogi (crews) w CrewAI.
- Skaluje się do dużych populacji agentów kosztem złożoności operacyjnej.

Kiedy tego potrzebujesz: kiedy budżet kontekstowy pojedynczego nadzorcy nie jest w stanie pomieścić opisów wszystkich specjalistów.

### Debata (Debate)

- Równolegli oferenci (proposers) + iteracyjna wzajemna krytyka (Lekcja 25).
- Tak naprawdę to nie jest orkiestracja — raczej weryfikacja — ale we frameworkach pojawia się jako wybór topologii.

### CrewAI Crew vs Flow

CrewAI formalizuje dwa tryby wdrażania:

- **Flow** dla deterministycznej, sterowanej zdarzeniami automatyzacji (zalecany punkt wyjścia dla środowisk produkcyjnych).
- **Crew** dla autonomicznej współpracy opartej na rolach.

Jest to niezależne od czterech powyższych wzorców, ale mapuje się na topologię: Flow to zazwyczaj nadzorca lub hierarchia; Crew to zazwyczaj nadzorca z routerem LLM.

### Wytyczne Anthropic

"Sukces w przestrzeni LLM nie polega na budowaniu najbardziej wyrafinowanego systemu. Chodzi o zbudowanie odpowiedniego systemu do Twoich potrzeb."

Kolejność podejmowania decyzji:

1. Pojedynczy agent + wzorce przepływu pracy (Lekcja 12) — zacznij tutaj.
2. Nadzorca-pracownik — gdy masz 2-4 specjalistów.
3. Rój (Swarm) — gdy opóźnienia są ważniejsze niż przejrzystość rozumowania.
4. Hierarchiczny — tylko gdy budżet kontekstu nadzorcy jest niewystarczający.
5. Debata — gdy dokładność liczy się bardziej niż koszt.

### Gdzie ten wzorzec zawodzi

- **Myślenie ukierunkowane w pierwszej kolejności na topologię.** "Potrzebujemy systemu wieloagentowego" przed zidentyfikowaniem problemu, który taki system ma rozwiązać.
- **Odbijające się przekazania w roju.** A -> B -> A -> B. Użyj liczników przeskoków (hop counters).
- **Fałszywa hierarchia.** Trzy poziomy, bo to "enterprise"; tak naprawdę to dwa zespoły. Spłaszcz to.

## Zbuduj to

`code/main.py` implementuje wszystkie cztery wzorce w stdlib na podstawie oskryptowanego LLM:

- `Supervisor` — centralny router.
- `Swarm` — peer-to-peer z bezpośrednim przekazywaniem.
- `Hierarchical` — nadzorcy nadzorców.
- `Debate` — równolegli oferenci + krytyka.

Każdy wzorzec obsługuje to samo trzyintencyjne zadanie (zwrot / błąd / sprzedaż). Ślady (traces) przybierają różne kształty.

Uruchom to:

```bash
python3 code/main.py
```

Wynik: ślad dla każdego wzorca + liczba operacji. Nadzorca (supervisor) jest najczystszy; rój (swarm) jest najkrótszy; hierarchia jest najgłębsza; debata jest najdroższa.

## Użyj tego

- **LangGraph** dla nadzorcy i hierarchii (zagnieżdżone podgrafy).
- **OpenAI Agents SDK** dla przekazań jako narzędzi (kształt nadzorcy).
- **CrewAI Flow** dla produkcyjnych rozwiązań deterministycznych.
- **Własne (Custom)** dla debaty lub gdy chcesz mieć dokładną kontrolę.

## Wdróż to

`outputs/skill-orchestration-picker.md` wybiera topologię i implementuje ją.

## Ćwiczenia

1. Zmień strukturę nadzorca-pracownik na rój (swarm), usuwając router. Co się psuje? Co się poprawia?
2. Dodaj licznik przeskoków (hop counter) do roju: odmów po 3 przekazaniach. Czy wyłapuje to odbijanie A->B->A?
3. Zbuduj dwupoziomowy system hierarchiczny dla domeny z 12 specjalistami. W którym miejscu budżet kontekstu zawodzi bez zagnieżdżania?
4. Sprofiluj wszystkie cztery wzorce na obciążeniu o charakterze produkcyjnym. Który z nich wygrywa w jakiej metryce (opóźnienie, koszt, dokładność, łatwość debugowania)?
5. Przeczytaj post Anthropic "Building Effective Agents". Przypisz każdy ze swoich przepływów produkcyjnych do jednego z czterech wzorców. Czy są jakieś, które nie pasują do żadnego?

## Kluczowe pojęcia

| Termin | Co mówią ludzie | Co to w rzeczywistości oznacza |
|------|----------------|------------------------|
| Nadzorca-pracownik (Supervisor-worker) | "Router + specjaliści" | Centralny LLM rozdziela zadania specjalistom; oni ze sobą nie rozmawiają |
| Rój (Swarm) | "Peer-to-peer" | Bezpośrednie przekazania (handoffs) poprzez wspólne narzędzia; brak centralnego routera |
| Hierarchiczny (Hierarchical) | "Nadzorcy nadzorców" | Zagnieżdżone podgrafy dla dużych populacji |
| Debata (Debate) | "Proposer + krytyka" | Równolegli oferenci, wzajemna krytyka (Lekcja 25) |
| Nadzór oparty na wywołaniach narzędzi | "Nadzorca bez biblioteki" | Implementacja nadzorcy jako bezpośrednich wywołań narzędzi (tool calls) dla kontroli kontekstu |
| Crew (Załoga) | "Autonomiczny zespół" | Tryb współpracy opartej na rolach w CrewAI |
| Flow (Przepływ) | "Deterministyczny workflow" | Produkcyjny tryb sterowany zdarzeniami w CrewAI |

## Dalsza lektura

- [Anthropic, Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) — pięć wzorców + agent vs workflow
- [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview) — nadzorca, rój, hierarchia
- [CrewAI docs](https://docs.crewai.com/en/introduction) — Crew vs Flow
- [Du et al., Society of Minds (arXiv:2305.14325)](https://arxiv.org/abs/2305.14325) — wzorzec debaty