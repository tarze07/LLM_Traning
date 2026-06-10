# Dlaczego warto stosować systemy wieloagentowe?

> Gdy pojedynczy agent napotyka barierę swoich możliwości, rozwiązaniem nie jest stworzenie większego agenta – lecz zaangażowanie większej liczby agentów.

**Typ:** Ucz się
**Języki:** TypeScript
**Wymagania wstępne:** Faza 14 (Inżynieria agentów)
**Czas:** ~60 minut

## Cele nauczania

- Zrozumienie ograniczeń pojedynczego agenta (przepełnienie okna kontekstowego, trudności z łączeniem różnych dziedzin wiedzy, wąskie gardło szeregowego przetwarzania) i określenie sytuacji, w których podział na system wieloagentowy jest optymalnym rozwiązaniem.
- Analiza i porównanie modeli orkiestracji (sekwencyjny potok, rozgałęzienie równoległe, model z nadzorcą, struktura hierarchiczna) oraz wybór odpowiedniego schematu dla danego zadania.
- Zaprojektowanie system wieloagentowego opartego na wyraźnym podziale ról, współdzielonym stanie (shared state) i ustalonym protokole komunikacji.
- Ewaluacja kompromisów związanych ze złożonością struktur wieloagentowych (opóźnienia, koszty, utrudnione debugowanie) w zestawieniu z prostotą pojedynczego agenta.

## Problem

W Fazie 14 został zbudowany pojedynczy agent. Działa on poprawnie: potrafi analizować pliki, uruchamiać komendy, wywoływać API oraz przetwarzać wyniki. Wyobraźmy sobie jednak, że przed takim agentem stawiamy rzeczywisty projekt programistyczny: bazę składającą się z 200 plików w trzech różnych językach, testy zależne od infrastruktury oraz konieczność weryfikacji zewnętrznych API przed przystąpieniem do pisania kodu.

W tym scenariuszu pojedynczy agent napotka barierę swoich możliwości. Nie dzieje się tak z powodu słabości samego modelu LLM, lecz dlatego, że poziom skomplikowania zadania przerasta możliwości jednej zamkniętej pętli decyzyjnej. Okno kontekstowe błyskawicznie zapełnia się kodem źródłowym, a agent zapomina informacje odczytane kilkadziesiąt kroków wcześniej. Próbuje jednocześnie pełnić rolę analityka, programisty i recenzenta kodu, co drastycznie obniża jakość każdego z tych zadań.

To jest właśnie ograniczenie pojedynczego agenta. Napotykamy je zawsze, gdy zadanie wymaga:

- **Przetworzenia kontekstu przekraczającego pojemność okna** – np. analiza 50 plików źródłowych może wykraczać poza 200 tysięcy tokenów.
- **Różnych specjalizacji na poszczególnych etapach** – faza analizy wymaga zupełnie innego promptowania i instrukcji systemowych niż bezpośrednie generowanie kodu.
- **Pracy równoległej** – nie ma sensu analizować plików sekwencyjnie jeden po drugim, jeśli można przetwarzać je równolegle.

## Koncepcja

### Ograniczenia pojedynczego agenta

Pojedynczy agent opiera się na jednej pętli, jednym oknie kontekstowym i pojedynczym prompcie systemowym. Ilustruje to schemat:

```
┌─────────────────────────────────────────┐
│            SINGLE AGENT                 │
│                                         │
│  ┌───────────────────────────────────┐  │
│  │         Context Window            │  │
│  │                                   │  │
│  │  research notes                   │  │
│  │  + code files                     │  │
│  │  + test output                    │  │
│  │  + review feedback                │  │
│  │  + API docs                       │  │
│  │  + ...                            │  │
│  │                                   │  │
│  │  ██████████████████████ FULL ███  │  │
│  └───────────────────────────────────┘  │
│                                         │
│  One system prompt tries to cover       │
│  research + coding + review + testing   │
│                                         │
│  Result: mediocre at everything         │
└─────────────────────────────────────────┘
```

W tym podejściu zawodzą trzy główne elementy:

1. **Przepełnienie kontekstu** – rezultaty działania narzędzi szybko się kumulują. W okolicach 30. kroku (tury) agent może zużyć np. 150 tysięcy tokenów na kod źródłowy, logi z terminala i wcześniejsze wnioski. W rezultacie kluczowe detale z początku konwersacji ulegają rozmyciu i zapomnieniu.

2. **Rozproszenie roli** – instrukcja systemowa typu „jesteś analitykiem, deweloperem, recenzentem i testerem” tworzy agenta, który wykonuje te zadania powierzchownie, tracąc ostrość i dokładność na każdym z tych etapów.

3. **Przetwarzanie wyłącznie szeregowe** – agent zmuszony jest analizować pliki krok po kroku (np. plik A, potem B, potem C). Skutkuje to seryjnymi wywołaniami LLM oraz seryjnym uruchamianiem narzędzi, uniemożliwiając jakąkolwiek równoległość działań.

### Rozwiązanie wieloagentowe

Rozwiązaniem jest podział zadań. Każdemu agentowi przydzielane jest jedno precyzyjne zadanie, osobne okno kontekstowe oraz dedykowany prompt systemowy:

```
┌──────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR                          │
│                                                          │
│  "Build a REST API for user management"                  │
│                                                          │
│         ┌──────────┬──────────┬──────────┐               │
│         │          │          │          │               │
│         ▼          ▼          ▼          ▼               │
│   ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│   │RESEARCHER│ │  CODER   │ │ REVIEWER │ │  TESTER  │  │
│   │          │ │          │ │          │ │          │  │
│   │ Analizuje│ │ Pisze    │ │ Weryfikuje│ │ Uruchamia│  │
│   │ dokument.│ │ kod na   │ │ jakość   │ │ testy,   │  │
│   │ szuka    │ │ podst.   │ │ kodu,    │ │ raportuje│  │
│   │ wzorców  │ │ analizy  │ │ błędy    │ │ wyniki   │  │
│   │          │ │ i spec.  │ │          │ │          │  │
│   └─────┬────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘  │
│         │           │            │             │         │
│         └───────────┴────────────┴─────────────┘         │
│                          │                               │
│                    Konsolidacja wyników                  │
└──────────────────────────────────────────────────────────┘
```

Każdy z agentów dysponuje:
- Precyzyjnym promptem systemowym (np. „Jesteś recenzentem kodu. Twoim jedynym celem jest znajdowanie błędów.”).
- Własnym, odizolowanym oknem kontekstowym (które nie jest zaśmiecane logami czy danymi z innych etapów pracy).
- Jasno zdefiniowanym interfejsem wejścia/wyjścia (np. przyjmuje specyfikację techniczną, zwraca gotowy kod).

### Rzeczywiste implementacje

**Podagenty w Claude Code** – podczas delegowania podzadań przez framework Claude Code tworzony jest podagent (child agent) z wąsko zdefiniowanym celem. Pozwala to zachować czystość okna kontekstowego agenta nadrzędnego (parent agent). Podagent realizuje dedykowane zadanie i zwraca jedynie zwięzłe podsumowanie.

**Devin** – tworzy niezależne agenty planisty, programisty oraz przeglądarki. Planista rozbija proces na mniejsze etapy, programista pisze kod źródłowy, a agent przeglądarki analizuje dokumentację techniczną. Każdy z nich działa we własnym oknie kontekstowym.

**Zespoły wieloagentowe w SWE-bench** – najbardziej wydajne rozwiązania w testach SWE-bench wykorzystują strukturę składającą się z analityka (badającego bazę kodu), planisty (projektującego poprawki) oraz programisty (wdrażającego kod). Systemy oparte na jednym agencie osiągają w tych testach znacznie gorsze rezultaty.

**Deep Research (ChatGPT)** – uruchamia równolegle wiele instancji agentów wyszukiwania, z których każda bada temat pod innym kątem, po czym następuje konsolidacja i synteza zebranych wyników.

### Spektrum systemów wieloagentowych

Podejście wieloagentowe nie ma charakteru zero-jedynkowego. Stanowi ono spektrum o różnym stopniu skomplikowania:

```
SIMPLE ──────────────────────────────────────────── COMPLEX
 
 Single        Sub-         Pipeline      Team         Swarm
 Agent         agents
 
 ┌───┐       ┌───┐        ┌───┐───┐    ┌───┐───┐    ┌─┐┌─┐┌─┐
 │ A │       │ A │        │ A │ B │    │ A │ B │    │ ││ ││ │
 └───┘       └─┬─┘        └───┘─┬─┘    └─┬─┘─┬─┘    └┬┘└┬┘└┬┘
               │                │        │   │       ┌┴──┴──┴┐
             ┌─┴─┐          ┌───┘───┐    │   │       │shared │
             │ a │          │ C │ D │  ┌─┴───┴─┐    │ state │
             └───┘          └───┘───┘  │  msg   │    └───────┘
                                       │  bus   │
 1 loop      Zadania       Etap po     │       │    N partnerów,
 1 context   nadrz. i      etapie      └───────┘    zachowania
             podrzędne                 Wyraźne      emergente
                                       role
```

**Pojedynczy agent** – jedna pętla, jeden prompt. Sprawdza się w przypadku nieskomplikowanych zadań.

**Podagenty (Sub-agents)** – agent nadrzędny tworzy agenty podrzędne do realizacji konkretnych podzadań. Rodzic nadzoruje ogólny plan, a agenty podrzędne raportują wyniki (metoda stosowana m.in. w Claude Code).

**Potok (Pipeline)** – agenty działają sekwencyjnie (szeregowo). Dane wyjściowe z Agenta A stanowią dane wejściowe dla Agenta B. Model idealny dla etapowych procesów: analiza -> programowanie -> przegląd -> testy.

**Zespół (Team)** – agenty działają równolegle i wymieniają komunikaty poprzez wspólną magistralę. Każdy agent ma przypisaną rolę, a koordynacją procesu zajmuje się orkiestrator. Rozwiązanie sprawdza się, gdy wymagane jest jednoczesne łączenie różnych specjalizacji.

**Rój (Swarm)** – zbiór identycznych lub bardzo podobnych agentów współdzielących wspólny stan. Brak centralnego orkiestratora – agenty pobierają zadania z kolejki. Model optymalny dla przetwarzania równoległego o wysokiej przepustowości.

### Cztery podstawowe wzorce projektowe

#### Wzorzec 1: Potok (Pipeline)

```
Input ──▶ Agent A ──▶ Agent B ──▶ Agent C ──▶ Output
          (research)  (code)      (review)
```

Każdy agent modyfikuje lub przetwarza dane, a następnie przekazuje je do kolejnego ogniwa. Rozwiązanie to jest łatwe do zrozumienia i zaimplementowania, jednak awaria na dowolnym etapie blokuje cały przepływ.

#### Wzorzec 2: Rozwidlenie i konsolidacja (Fan-out / Fan-in)

```
                ┌──▶ Agent A ──┐
                │              │
Input ──▶ Split ├──▶ Agent B ──├──▶ Merge ──▶ Output
                │              │
                └──▶ Agent C ──┘
```

Polega na rozdzieleniu zadań pomiędzy równolegle działające agenty, a następnie na konsolidacji uzyskanych przez nie wyników. Idealne podejście do zadań, które można zdekomponować na niezależne podprocesy.

#### Wzorzec 3: Orkiestrator i wykonawcy (Orchestrator-Worker)

```
                    ┌──────────┐
                    │  Orch.   │
                    └──┬───┬───┘
                  task │   │ task
                 ┌─────┘   └─────┐
                 ▼               ▼
            ┌──────────┐   ┌──────────┐
            │ Worker A │   │ Worker B │
            └──────────┘   └──────────┘
```

Centralny agent (orkiestrator) planuje podział prac, deleguje zadania wykonawcom (workers) i scala wyniki ich działań. Sam orkiestrator jest zaawansowanym agentem wyposażonym w narzędzia do powoływania i nadzorowania innych agentów.

#### Wzorzec 4: Rój autonomiczny (Peer-to-peer Swarm)

```
          ┌───┐ ◄──── msg ────▶ ┌───┐
          │ A │                  │ B │
          └─┬─┘                  └─┬─┘
            │                      │
       msg  │    ┌───────────┐     │ msg
            └───▶│  Shared   │◄────┘
                 │  State    │
            ┌───▶│  / Queue  │◄────┐
            │    └───────────┘     │
       msg  │                      │ msg
          ┌─┴─┐                  ┌─┴─┐
          │ C │ ◄──── msg ────▶ │ D │
          └───┘                  └───┘
```

Brak centralnego punktu zarządzającego. Agenty komunikują się bezpośrednio między sobą (peer-to-peer), a ostateczne decyzje i działania wyłaniają się z ich wzajemnych interakcji. Układ ten jest trudniejszy do debugowania, ale doskonale skaluje się przy dużej liczbie uczestników.

### Kiedy NIE należy stosować systemów wieloagentowych

Wdrażanie struktur wieloagentowych znacząco podnosi stopień skomplikowania systemu. Każdy komunikat przesyłany między agentami stanowi potencjalny punkt awarii. Proces debugowania zmienia się z prostej analizy pojedynczej historii konwersacji w złożone śledzenie przepływu wiadomości pomiędzy wieloma podmiotami.

**Pojedynczy agent jest lepszym rozwiązaniem, gdy:**
- Dane wejściowe i robocze mieszczą się w oknie kontekstowym (poniżej ok. 100 tys. tokenów).
- Nie zachodzi potrzeba stosowania odmiennych instrukcji systemowych dla poszczególnych faz pracy.
- Szeregowy czas wykonania zadań jest w pełni akceptowalny.
- Zadanie jest na tyle nieskomplikowane, że narzut związany z orkiestracją przewyższałby korzyści płynące z podziału pracy.

**Związane z tym koszty i ograniczenia:**
- Każde przekazanie danych między agentami wiąże się ze stratną kompresją informacji (agent A musi streścić swoje wnioski w wiadomości do agenta B).
- Logika koordynująca (określanie kolejności działań i przydziału ról) staje się dodatkowym źródłem błędów programistycznych.
- Rośnie opóźnienie (latency) – zaangażowanie N agentów wymaga co najmniej N sekwencyjnych wywołań LLM (a często znacznie więcej, jeśli zachodzi potrzeba interakcji zwrotnych).
- Koszty finansowe rosną – każdy agent niezależnie generuje zużycie tokenów.

**Złota zasada:** jeśli realizacja zadania wymaga wykonania mniej niż 20 kroków z użyciem narzędzi i mieści się w granicach 100 000 tokenów, należy pozostać przy architekturze opartej na jednym agencie.

## Implementacja krok po kroku

### Krok 1: Przeciążony pojedynczy agent

Poniższy kod przedstawia pojedynczego agenta podejmującego próby realizacji całego procesu. Korzysta on z jednej rozbudowanej instrukcji systemowej oraz pojedynczego okna kontekstowego, w którym gromadzone są wszystkie logi z analizy, pisania kodu i recenzowania:

```typescript
type AgentResult = {
  content: string;
  tokensUsed: number;
  toolCalls: number;
};

async function singleAgentApproach(task: string): Promise<AgentResult> {
  const systemPrompt = `You are a full-stack developer. You must:
1. Research the requirements
2. Write the code
3. Review the code for bugs
4. Write tests
Do ALL of these in a single conversation.`;

  const contextWindow: string[] = [];
  let totalTokens = 0;
  let totalToolCalls = 0;

  const research = await fakeLLMCall(systemPrompt, `Research: ${task}`);
  contextWindow.push(research.output);
  totalTokens += research.tokens;
  totalToolCalls += research.calls;

  const code = await fakeLLMCall(
    systemPrompt,
    `Given this research:\n${contextWindow.join("\n")}\n\nNow write code for: ${task}`
  );
  contextWindow.push(code.output);
  totalTokens += code.tokens;
  totalToolCalls += code.calls;

  const review = await fakeLLMCall(
    systemPrompt,
    `Given all previous context:\n${contextWindow.join("\n")}\n\nReview the code.`
  );
  contextWindow.push(review.output);
  totalTokens += review.tokens;
  totalToolCalls += review.calls;

  return {
    content: contextWindow.join("\n---\n"),
    tokensUsed: totalTokens,
    toolCalls: totalToolCalls,
  };
}
```

Główne wady tego podejścia:
- Okno kontekstowe rośnie liniowo wraz z każdym krokiem. W fazie recenzowania zawiera ono jednocześnie notatki z analizy, wygenerowany kod oraz wcześniejszy przebieg myślenia.
- Instrukcja systemowa (system prompt) jest zbyt ogólna i nie pozwala na precyzyjne sterowanie modelem na poszczególnych etapach.
- Zadania nie mogą być uruchamiane równolegle.

### Krok 2: Tworzenie wyspecjalizowanych agentów

Nowy podział zadań. Każdy specjalista otrzymuje precyzyjnie określony cel:

```typescript
type SpecialistAgent = {
  name: string;
  systemPrompt: string;
  run: (input: string) => Promise<AgentResult>;
};

function createSpecialist(name: string, systemPrompt: string): SpecialistAgent {
  return {
    name,
    systemPrompt,
    run: async (input: string) => {
      const result = await fakeLLMCall(systemPrompt, input);
      return {
        content: result.output,
        tokensUsed: result.tokens,
        toolCalls: result.calls,
      };
    },
  };
}

const researcher = createSpecialist(
  "researcher",
  "You are a technical researcher. Read documentation, find patterns, and summarize findings. Output only the facts needed for implementation."
);

const coder = createSpecialist(
  "coder",
  "You are a senior TypeScript developer. Given requirements and research notes, write clean, tested code. Nothing else."
);

const reviewer = createSpecialist(
  "reviewer",
  "You are a code reviewer. Find bugs, security issues, and logic errors. Be specific. Cite line numbers."
);
```

Każdy specjalista ma ukierunkowany monit. Każdy otrzymuje czyste okno kontekstowe zawierające tylko potrzebne dane wejściowe.

### Krok 3: Orkiestracja za pomocą komunikatów

Wymiana danych pomiędzy wyspecjalizowanymi agentami odbywa się za pomocą ustrukturyzowanych komunikatów:

```typescript
type AgentMessage = {
  from: string;
  to: string;
  content: string;
  timestamp: number;
};

async function multiAgentApproach(task: string): Promise<AgentResult> {
  const messages: AgentMessage[] = [];
  let totalTokens = 0;
  let totalToolCalls = 0;

  const researchResult = await researcher.run(task);
  messages.push({
    from: "researcher",
    to: "coder",
    content: researchResult.content,
    timestamp: Date.now(),
  });
  totalTokens += researchResult.tokensUsed;
  totalToolCalls += researchResult.toolCalls;

  const coderInput = messages
    .filter((m) => m.to === "coder")
    .map((m) => `[From ${m.from}]: ${m.content}`)
    .join("\n");

  const codeResult = await coder.run(coderInput);
  messages.push({
    from: "coder",
    to: "reviewer",
    content: codeResult.content,
    timestamp: Date.now(),
  });
  totalTokens += codeResult.tokensUsed;
  totalToolCalls += codeResult.toolCalls;

  const reviewerInput = messages
    .filter((m) => m.to === "reviewer")
    .map((m) => `[From ${m.from}]: ${m.content}`)
    .join("\n");

  const reviewResult = await reviewer.run(reviewerInput);
  messages.push({
    from: "reviewer",
    to: "orchestrator",
    content: reviewResult.content,
    timestamp: Date.now(),
  });
  totalTokens += reviewResult.tokensUsed;
  totalToolCalls += reviewResult.toolCalls;

  return {
    content: messages.map((m) => `[${m.from} -> ${m.to}]: ${m.content}`).join("\n\n"),
    tokensUsed: totalTokens,
    toolCalls: totalToolCalls,
  };
}
```

Każdy agent otrzymuje tylko wiadomości zaadresowane do niego. Żadnego zanieczyszczenia kontekstu. 50 000 tokenów przeznaczonych na analizę dokumentacji przez agenta badawczego nie obciąża okna kontekstowego recenzenta.

### Krok 4: Porównanie wydajności

```typescript
async function compare() {
  const task = "Build a rate limiter middleware for an Express.js API";

  console.log("=== Single Agent ===");
  const single = await singleAgentApproach(task);
  console.log(`Tokens: ${single.tokensUsed}`);
  console.log(`Tool calls: ${single.toolCalls}`);

  console.log("\n=== Multi-Agent ===");
  const multi = await multiAgentApproach(task);
  console.log(`Tokens: ${multi.tokensUsed}`);
  console.log(`Tool calls: ${multi.toolCalls}`);
}
```

Podejście wieloagentowe generuje wyższe zużycie tokenów (uruchomienie trzech agentów wymaga trzech oddzielnych wywołań LLM), jednak okno kontekstowe każdego z nich pozostaje czyste. Jakość poszczególnych etapów rośnie dzięki zastosowaniu wyspecjalizowanych promptów systemowych.

## Jak tego użyć

W ramach tej lekcji przygotowano szablon promptu decyzyjnego, ułatwiający ocenę zasadności wdrożenia architektury wieloagentowej. Zobacz plik [outputs/prompt-multi-agent-decision.md](file:///C:/poligon/LLM_Traning/phases/16-multi-agent-and-swarms/01-why-multi-agent/outputs/prompt-multi-agent-decision_pl.md).

## Ćwiczenia

1. Dodaj do systemu czwartego agenta – testera, którego zadaniem będzie analiza kodu źródłowego oraz uwag recenzenta, a następnie pisanie testów jednostkowych.
2. Zmodyfikuj potok (pipeline) tak, aby recenzent mógł przekazywać uwagi z powrotem do programisty w celu poprawy kodu (wprowadź pętlę korekty ograniczoną do maksymalnie 2 iteracji).
3. Przekształć potok szeregowy w rozgałęziony: uruchom równolegle agenta analitycznego oraz agenta badawczego, a następnie scal ich wnioski przed przekazaniem do programisty.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|----------------------|
| Rój (Swarm) | „Decentralizacja systemów” | Zbiór równorzędnych agentów (peers) współdzielących wspólny stan, działających bez centralnego lidera. Globalne zachowanie systemu wyłania się z lokalnych interakcji. |
| Orkiestrator (Orchestrator) | „Agent zarządzający” | Agent, którego głównym zadaniem jest tworzenie podagentów, planowanie pracy oraz delegowanie zadań, bez konieczności samodzielnego pisania kodu czy analizowania logów. |
| Koordynator (Router/Coordinator) | „Przełącznik wiadomości” | Tradycyjny komponent programistyczny (kod bez wywołań LLM) przekazujący komunikaty między agentami na podstawie sztywnych reguł logiki biznesowej. |
| Konsensus (Consensus) | „Uzgodnienie stanowisk” | Protokół wymagający od wielu agentów wypracowania wspólnego stanowiska przed przejściem do kolejnego kroku, stosowany przy rozbieżnych wynikach cząstkowych. |
| Zachowania emergente (Emergent behavior) | „Właściwości wyłaniające się” | Globalne wzorce zachowań systemu wieloagentowego, które nie zostały wprost zaprogramowane, lecz wynikają z sumy prostych interakcji między agentami. |
| Fan-out / Fan-in | „Rozwidlenie i scalenie” | Strategia polegająca na rozdzieleniu zadania na wiele równoległych podzadań (fan-out), a następnie na konsolidacji cząstkowych wyników w spójną całość (fan-in). |
| Przekazywanie komunikatów (Message passing) | „Komunikacja międzyagentowa” | Protokół przesyłania ustrukturyzowanych danych między niezależnymi agentami, stosowany zamiast współdzielenia jednego okna kontekstowego. |

## Dalsza lektura

- [The Landscape of Emerging AI Agent Architectures](https://arxiv.org/abs/2409.02977) – przegląd wzorców wieloagentowych.
- [AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation](https://arxiv.org/abs/2308.08155) – framework firmy Microsoft do konwersacji między agentami.
- [Dokumentacja podagentów Claude Code](https://docs.anthropic.com/en/docs/claude-code) – delegowanie zadań w frameworku Claude Code.
- [Dokumentacja CrewAI](https://docs.crewai.com/) – framework do orkiestracji systemów wieloagentowych opartych na rolach.
