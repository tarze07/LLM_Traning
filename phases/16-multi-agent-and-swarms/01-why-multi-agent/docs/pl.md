# Dlaczego wieloagentowy?

> Jeden agent uderza w ścianę. Sprytnym posunięciem nie jest większy agent – ​​to więcej agentów.

**Typ:** Ucz się
**Języki:** TypeScript
**Wymagania wstępne:** Faza 14 (Inżynieria agentów)
**Czas:** ~60 minut

## Cele nauczania

- Zidentyfikuj pułap jednego agenta (przepełnienie kontekstu, mieszana wiedza specjalistyczna, sekwencyjne wąskie gardło) i wyjaśnij, kiedy podział na wielu agentów jest właściwym posunięciem
- Porównaj wzorce orkiestracji (potok, rozgałęzienie równoległe, nadzorca, hierarchiczny) i wybierz właściwy dla danej struktury zadań
- Zaprojektuj system wieloagentowy z jasnymi granicami ról, wspólnym stanem i umową komunikacyjną
- Analizuj kompromisy związane ze złożonością wielu agentów (opóźnienia, koszty, trudności w debugowaniu) w porównaniu z prostotą jednego agenta

## Problem

W fazie 14 zbudowałeś pojedynczego agenta. To działa. Może czytać pliki, uruchamiać polecenia, wywoływać interfejsy API i analizować wyniki. Następnie wskazujesz na prawdziwą bazę kodu: 200 plików, trzy języki, testy zależne od infrastruktury i wymóg sprawdzenia zewnętrznych interfejsów API przed napisaniem kodu.

Agent się krztusi. Nie dlatego, że LLM jest głupi, ale dlatego, że zadanie przekracza możliwości jednej pętli agenta. Okno kontekstowe zapełnia się zawartością pliku. Agent zapomina, co przeczytał 40 wywołań narzędzia temu. Próbuje być badaczem, programistą i recenzentem jednocześnie, ale słabo radzi sobie ze wszystkimi trzema.

To jest pułap jednego agenta. Naciskasz go za każdym razem, gdy zadanie wymaga:

- **Więcej kontekstu niż mieści się w jednym oknie** - odczytanie 50 plików przekracza 200 tys. tokenów
- **Różna wiedza specjalistyczna na różnych etapach** - badania wymagają innego podpowiedzi niż generowanie kodu
- **Praca, która może odbywać się równolegle** - po co czytać trzy pliki sekwencyjnie, skoro można je czytać jednocześnie?

## Koncepcja

### Sufit jednego agenta

Pojedynczy agent to jedna pętla, jedno okno kontekstowe i jeden monit systemowy. Wyobraź to sobie:

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

Psują się trzy rzeczy:

1. **Nasycenie kontekstu** – wyniki narzędzia kumulują się. Do 30. tury agent zużył 150 tys. tokenów zawartości plików, wyników poleceń i wcześniejszych rozumowań. Gubią się krytyczne szczegóły z tury 5.

2. **Pomieszanie ról** – monit systemowy z informacją „jesteś badaczem, programistą, recenzentem i testerem” tworzy agenta, który na wpół bada, na wpół koduje i nigdy nie kończy recenzowania.

3. **Wąskie gardło sekwencyjne** – agent czyta plik A, następnie plik B, a następnie plik C. Trzy szeregowe wywołania LLM. Trzy seryjne wykonania narzędzi. Żadnej równoległości.

### Rozwiązanie wieloagentowe

Podziel pracę. Przydziel każdemu agentowi jedno zadanie, jedno okno kontekstowe i jeden monit systemowy dostosowany do tego zadania:

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
│   │ Reads    │ │ Writes   │ │ Checks   │ │ Runs     │  │
│   │ docs,    │ │ code     │ │ code     │ │ tests,   │  │
│   │ finds    │ │ based on │ │ quality, │ │ reports  │  │
│   │ patterns │ │ research │ │ finds    │ │ results  │  │
│   │          │ │ + spec   │ │ bugs     │ │          │  │
│   └─────┬────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘  │
│         │           │            │             │         │
│         └───────────┴────────────┴─────────────┘         │
│                          │                               │
│                     Merge results                        │
└──────────────────────────────────────────────────────────┘
```

Każdy agent posiada:
- Ukierunkowany monit systemowy („Jesteś recenzentem kodu. Twoim jedynym zadaniem jest znajdowanie błędów.”)
- Własne okno kontekstowe (niezanieczyszczone pracą innych agentów)
- Jasna umowa wejścia/wyjścia (otrzymuje notatki z badań, kod wyników)

### Prawdziwe systemy, które to robią

**Podagenci Claude Code** — gdy Claude Code tworzy podagenta z `Task`, tworzy agenta podrzędnego z zadaniem o określonym zakresie. Rodzic utrzymuje swój kontekst w czystości. Dziecko wykonuje skupioną pracę i zwraca podsumowanie.

**Devin** – uruchamia agenta planisty, agenta kodera i agenta przeglądarki. Planista dzieli pracę na etapy. Koder pisze kod. Przeglądarka przegląda dokumentację. Każdy ma odrębny kontekst.

**Wieloagentowe zespoły programistyczne (SWE-bench)** — w przypadku najskuteczniejszych systemów na SWE-bench zatrudniony jest badacz, który czyta bazę kodu, planista projektujący poprawkę i programista, który ją wdraża. Systemy jednoagentowe uzyskują niższe wyniki.

**Głębokie badania ChatGPT** – uruchamia równolegle wielu agentów wyszukiwania, każdy bada inny kąt, a następnie syntezuje wyniki.

### Spektrum

Multiagent nie jest binarny. Jest to widmo:

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
 1 loop      Parent +      Stage by    │       │    N peers,
 1 context   child tasks   stage       └───────┘    emergent
                                       Explicit      behavior
                                       roles
```

**Pojedynczy agent** – jedna pętla, jeden monit. Dobry do prostych zadań.

**Podagenci** – rodzic tworzy dzieci w celu wykonania określonych podzadań. Rodzic podtrzymuje plan. Dzieci składają relację. To właśnie robi Claude Code.

**Pipeline** – agenci działają sekwencyjnie. Dane wyjściowe Agenta A stają się danymi wejściowymi Agenta B. Dobre dla etapowych przepływów pracy: badania -> kod -> recenzja -> test.

**Zespół** – agenci działają równolegle ze współdzieloną magistralą komunikatów. Każdy ma swoją rolę. Koordynatorem jest orkiestrator. Dobrze, gdy potrzebne są jednocześnie różne umiejętności.

**Rój** – wiele identycznych lub prawie identycznych agentów ze wspólnym stanem. Brak stałego orkiestratora. Agenci odbierają pracę z kolejki. Dobry do zadań równoległych o dużej przepustowości.

### Cztery wzorce wieloagentowe

#### Wzorzec 1: Potok

```
Input ──▶ Agent A ──▶ Agent B ──▶ Agent C ──▶ Output
          (research)  (code)      (review)
```

Każdy agent przekształca dane i przekazuje je dalej. Proste do uzasadnienia. Niepowodzenie na jednym etapie blokuje resztę.

#### Wzór 2: Wentylacja / Wentylacja

```
                ┌──▶ Agent A ──┐
                │              │
Input ──▶ Split ├──▶ Agent B ──├──▶ Merge ──▶ Output
                │              │
                └──▶ Agent C ──┘
```

Podziel pracę między równoległych agentów, a następnie połącz wyniki. Dobre do zadań, które rozkładają się na niezależne podzadania.

#### Wzorzec 3: Orkiestrator-Pracownik

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

Inteligentny koordynator decyduje, co zrobić, deleguje pracownikom i syntezuje wyniki. Orkiestrator sam w sobie jest agentem posiadającym narzędzia do tworzenia pracowników.

#### Wzór 4: Rój rówieśniczy

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

Brak centralnego koordynatora. Agenci komunikują się peer-to-peer. Decyzje wynikają z interakcji. Trudniejsze do debugowania, ale skaluje się do wielu agentów.

### Kiedy NIE używać Multi-Agenta

Obsługa wielu agentów zwiększa złożoność. Każda wiadomość przesyłana pomiędzy agentami jest potencjalnym punktem awarii. Debugowanie przechodzi od „przeczytania jednej rozmowy” do „śledzenia wiadomości od pięciu agentów”.

**Pozostań jednym agentem, gdy:**
- Zadanie mieści się w jednym oknie kontekstowym (poniżej ~100 tys. tokenów danych roboczych)
- Nie potrzebujesz różnych podpowiedzi systemowych dla różnych etapów
- Wykonanie sekwencyjne jest wystarczająco szybkie
- Zadanie jest na tyle proste, że jego podzielenie powoduje większy narzut niż wartość

**Koszt złożoności:**
- Każda granica agenta jest krokiem kompresji stratnej: pełny kontekst agenta A jest podsumowywany w wiadomości dla agenta B
- Logika koordynacji (kto co robi, kiedy, w jakiej kolejności) jest sama w sobie źródłem błędów
- Zwiększa się opóźnienie: N agentów oznacza minimum N seryjnych połączeń LLM, więcej, jeśli muszą rozmawiać tam i z powrotem
- Koszt się mnoży: każdy agent pali żetony niezależnie

Ogólna zasada: jeśli zadanie wymaga mniej niż 20 wywołań narzędzi i mieści 100 000 tokenów, zachowaj je dla jednego agenta.

## Zbuduj to

### Krok 1: Przeciążony pojedynczy agent

Oto pojedynczy agent, który próbuje zrobić wszystko. Zawiera jeden ogromny monit systemowy i jedno okno kontekstowe zawierające badania, kod i recenzje:

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

Problemy z tym podejściem:
- Okno kontekstowe rośnie z każdym etapem. Na etapie przeglądu zawiera uwagi badawcze ORAZ kod ORAZ wcześniejsze uzasadnienie.
- Podpowiedź systemowa ma charakter ogólny. Nie można go dostosować do każdego etapu.
- Nic nie działa równolegle.

### Krok 2: Agenci wyspecjalizowani

Teraz podziel to. Każdy agent otrzymuje jedno zadanie:

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

### Krok 3: Koordynacja poprzez wiadomości

Połącz specjalistów, przekazując wyraźne komunikaty:

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

Każdy agent otrzymuje tylko wiadomości zaadresowane do niego. Żadnego zanieczyszczenia kontekstu. 50 000 dowodów przeczytania dokumentacji przez badacza nigdy nie wchodzi w kontekst recenzenta.

### Krok 4: Porównaj

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

Wersja wieloagentowa wykorzystuje więcej tokenów (trzech agentów, trzy oddzielne wywołania LLM), ale kontekst każdego agenta pozostaje czysty. Jakość każdego etapu poprawia się, ponieważ monit systemowy jest wyspecjalizowany.

## Użyj tego

W ramach tej lekcji zostanie wyświetlony monit wielokrotnego użytku umożliwiający podjęcie decyzji o przejściu na pracę wieloagentową. Zobacz `outputs/prompt-multi-agent-decision.md`.

## Ćwiczenia

1. Dodaj czwartego specjalistę: agenta „testera”, który otrzymuje kod od kodera i przegląda informację zwrotną od recenzenta, a następnie pisze testy
2. Zmodyfikuj potok, aby recenzent mógł przesłać informację zwrotną do programisty w celu przeprowadzenia pętli rewizyjnej (maks. 2 rundy)
3. Przekształć potok sekwencyjny w rozgałęziony: uruchom równolegle badacza i agenta „analizatora wymagań”, a następnie połącz ich wyniki przed przekazaniem do kodera

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|----------------------|
| Rój | „Umysł ula agentów AI” | Zbiór równorzędnych agentów ze wspólnym stanem i bez stałego lidera. Zachowanie wyłania się z lokalnych interakcji. |
| Orkiestrator | „Agent szef” | Agent, którego narzędzia obejmują tworzenie innych agentów i zarządzanie nimi. Planuje i deleguje zadania, ale może nie wykonywać faktycznej pracy. |
| Koordynator | „Policjant drogowy” | Komponent niebędący agentem (często tylko kod, a nie LLM), który kieruje komunikaty między agentami na podstawie reguł. |
| Konsensus | „Agenci zgadzają się” | Protokół, w którym wielu agentów musi osiągnąć porozumienie przed kontynuowaniem. Używane, gdy sprzeczne wyjścia wymagają rozwiązania. |
| Pojawiające się zachowanie | „Agenci sami to odkryli” | Wzorce na poziomie systemu, które powstają w wyniku interakcji agentów, ale nie zostały jawnie zaprogramowane. Może być przydatny lub szkodliwy. |
| Rozwinięcie/rozwinięcie | „Zmniejszanie mapy dla agentów” | Podział zadania na równoległych agentów (fan-out), a następnie połączenie ich wyników (fan-in). |
| Wiadomość przekazana | „Agenci rozmawiają ze sobą” | Mechanizm komunikacji pomiędzy agentami: ustrukturyzowane dane przesyłane od jednego agenta do drugiego, zastępując współdzielone okna kontekstowe. |

## Dalsze czytanie

- [Krajobraz wyłaniających się architektur agentów AI](https://arxiv.org/abs/2409.02977) - przegląd wzorców wieloagentowych
— [AutoGen: Włączanie aplikacji LLM nowej generacji](https://arxiv.org/abs/2308.08155) — Struktura konwersacji między agentami firmy Microsoft
- [Dokumentacja podagentów Claude Code](https://docs.anthropic.com/en/docs/claude-code) - jak Claude Code deleguje zadania
- [Dokumentacja CrewAI](https://docs.crewai.com/) - framework wieloagentowy oparty na rolach