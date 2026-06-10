# Inżynieria kontekstu: okna, budżety, pamięć i pobieranie

> Inżynieria promptów to jedynie podzbiór. Inżynieria kontekstu to cała gra. Prompt to wpisywany ciąg znaków. Kontekst to wszystko, co trafia do okna modelu: instrukcje systemowe, pobrane dokumenty, definicje narzędzi, historia rozmów, przykłady demonstracyjne i samo zapytanie. Najlepsi inżynierowie AI w 2026 roku to inżynierowie kontekstu. Decydują, co wchodzi do środka, co pozostaje na zewnątrz i w jakiej kolejności.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 10 (LLM od podstaw), Faza 11, lekcja 01-02
**Czas:** ~90 minut
**Powiązane:** Faza 11 · 15 (Podręczne buforowanie) — układ przyjazny pamięci podręcznej jest rozszerzeniem inżynierii kontekstowej. Faza 5 · 28 (Ocena w długim kontekście), jak mierzyć zagubienie w środku za pomocą NIAH/RULER.

## Cele nauczania

- Oblicz budżety tokenów we wszystkich składnikach okna kontekstowego (prompt systemowy, narzędzia, historia, pobrane dokumenty, zapas na generowanie)
- Wdrażaj strategie zarządzania oknami kontekstowymi: obcinanie, podsumowywanie i przesuwanie okna historii rozmów
- Ustalaj priorytety i porządkuj składniki kontekstu, aby zmaksymalizować uwagę modelu na najbardziej istotnych informacjach
- Zbuduj asembler kontekstu, który dynamicznie przydziela tokeny na podstawie rodzaju zapytania i dostępnego miejsca w oknie

## Problem

Claude Opus 4.7 dysponuje oknem 200 tys. tokenów (1 milion w wersji beta). GPT-5 oferuje 400 tys. Gemini 3 Pro — 2M. Llama 4 sięga 10 milionów. Liczby te wydają się ogromne, dopóki faktycznie nie zaczniesz je wypełniać.

Oto realny podział dla asystenta kodowania. Komunikat systemowy: 500 tokenów. Definicje narzędzi dla 50 narzędzi: 8000 tokenów. Pobrana dokumentacja: 4000 tokenów. Historia rozmów (10 tur): 6000 tokenów. Bieżące zapytanie użytkownika: 200 tokenów. Budżet generowania (maksymalna długość odpowiedzi): 4000 tokenów. Razem: 22 700 tokenów — zaledwie 18% okna 128K.

Uwaga modelu nie skaluje się jednak liniowo wraz z długością kontekstu. Model obsługujący 128 tys. tokenów kontekstu ponosi kwadratowy koszt mechanizmu uwagi (O(n²) w klasycznych transformerach, choć większość modeli produkcyjnych korzysta z wariantów efektywnej uwagi). Co ważniejsze, spada dokładność wyszukiwania. Test „Igła w stogu siana" pokazuje, że modele mają trudności ze znalezieniem informacji umieszczonych w środkowej części długich kontekstów. Badania Liu i in. (2023) wykazały, że duże modele językowe lokalizują informacje na początku i na końcu długich kontekstów z niemal idealną dokładnością, lecz ta dokładność spada o 10–20% w przypadku treści umieszczonych pośrodku (na pozycjach 40–70% kontekstu). Zjawisko to określane jest mianem „zagubienia w środku" i dotyczy — w różnym stopniu — wszystkich aktualnych architektur.

Praktyczny wniosek: dysponowanie 200 tys. tokenów nie oznacza, że ich wykorzystanie jest efektywne. Starannie dobrany kontekst złożony z 10 000 tokenów często przewyższa jakością nieuporządkowany kontekst liczący 100 000 tokenów. Inżynieria kontekstu to dyscyplina polegająca na maksymalizacji stosunku sygnału do szumu w oknie kontekstowym.

Każdy token umieszczony w oknie zajmuje miejsce, które mogłoby zawierać bardziej istotne informacje. Zbędna definicja narzędzia, przestarzały fragment rozmowy, pobrany fragment tekstu niezwiązany z pytaniem — każdy z nich obniża skuteczność modelu.

## Koncepcja

### Okno kontekstowe jako zasób rzadki

Myśl o oknie kontekstowym jak o pamięci RAM, nie jak o dysku. Jest szybka i bezpośrednio dostępna, ale ograniczona. Nie da się zmieścić wszystkiego — trzeba wybierać.

```mermaid
graph TD
    subgraph Window["Context Window (128K tokens)"]
        direction TB
        S["System Prompt\n~500 tokens"] --> T["Tool Definitions\n~2K-8K tokens"]
        T --> R["Retrieved Context\n~2K-10K tokens"]
        R --> H["Conversation History\n~2K-20K tokens"]
        H --> F["Few-shot Examples\n~1K-3K tokens"]
        F --> Q["User Query\n~100-500 tokens"]
        Q --> G["Generation Budget\n~2K-8K tokens"]
    end

    style S fill:#1a1a2e,stroke:#e94560,color:#fff
    style T fill:#1a1a2e,stroke:#0f3460,color:#fff
    style R fill:#1a1a2e,stroke:#ffa500,color:#fff
    style H fill:#1a1a2e,stroke:#51cf66,color:#fff
    style F fill:#1a1a2e,stroke:#9b59b6,color:#fff
    style Q fill:#1a1a2e,stroke:#e94560,color:#fff
    style G fill:#1a1a2e,stroke:#0f3460,color:#fff
```

Każdy element rywalizuje o miejsce. Więcej definicji narzędzi oznacza mniej przestrzeni na historię rozmów. Więcej pobranego kontekstu oznacza mniej miejsca na przykłady demonstracyjne. Inżynieria kontekstu to sztuka alokacji budżetu w celu maksymalizacji skuteczności zadania.

### Zagubiony w środku

To najważniejsze odkrycie empiryczne w inżynierii kontekstowej. Modele poświęcają więcej uwagi informacjom znajdującym się na początku i na końcu kontekstu. Treści umieszczone pośrodku są mniej zauważane i częściej pomijane.

Liu i in. (2023) zbadali to systematycznie. Umieszczali właściwy dokument wśród 20 nieistotnych, w różnych miejscach, i mierzyli dokładność odpowiedzi. Gdy dokument był na początku lub końcu, dokładność wynosiła 85–90%. W środku (pozycja 10 z 20) spadała do 60–70%.

Ma to konkretne konsekwencje inżynieryjne:

- Umieszczaj najważniejsze informacje na początku (prompt systemowy, kluczowe instrukcje)
- Bieżące zapytanie i najbardziej trafny kontekst umieszczaj na końcu (minimalizuje efekt aktualności)
- Środek kontekstu traktuj jako strefę najniższego priorytetu
- Jeśli musisz zawrzeć ważne informacje w środku, powtórz kluczowy punkt na końcu

```mermaid
graph LR
    subgraph Attention["Attention Distribution Across Context"]
        direction LR
        P1["Position 0-20%\nHIGH attention\n(system prompt)"]
        P2["Position 20-40%\nMODERATE"]
        P3["Position 40-70%\nLOW attention\n(lost in middle)"]
        P4["Position 70-90%\nMODERATE"]
        P5["Position 90-100%\nHIGH attention\n(current query)"]
    end

    style P1 fill:#51cf66,color:#000
    style P2 fill:#ffa500,color:#000
    style P3 fill:#ff6b6b,color:#fff
    style P4 fill:#ffa500,color:#000
    style P5 fill:#51cf66,color:#000
```

### Składniki kontekstu

**Prompt systemowy**: określa rolę modelu, ograniczenia i reguły zachowania. Pojawia się jako pierwszy i pozostaje niezmienny w kolejnych turach. Claude Code używa około 6000 tokenów w swoich promptach systemowych, wliczając definicje narzędzi i instrukcje behawioralne. Dbaj o jego zwięzłość — każde słowo w promptcie systemowym jest powielane przy każdym wywołaniu API.

**Definicje narzędzi**: każde narzędzie zajmuje 50–200 tokenów (nazwa, opis, schemat parametrów). 50 narzędzi po 150 tokenów to 7500 tokenów, zanim jakakolwiek rozmowa się rozpocznie. Dynamiczny dobór narzędzi — uwzględniający tylko te istotne dla bieżącego zapytania — pozwala zmniejszyć ten koszt o 60–80%.

**Pobrany kontekst**: dokumenty z bazy wektorowej, wyniki wyszukiwania, zawartość plików. Jakość wyszukiwania bezpośrednio przekłada się na jakość odpowiedzi. Złe pobranie jest gorsze niż brak pobrania — wypełnia okno szumem i aktywnie wprowadza model w błąd.

**Historia rozmów**: wszystkie poprzednie wiadomości użytkownika i odpowiedzi asystenta. Rośnie liniowo wraz z długością rozmowy. Rozmowa trwająca 50 tur przy 200 tokenach na turę daje 10 000 tokenów historii — z których większość nie ma związku z bieżącym pytaniem.

**Przykłady demonstracyjne**: pary wejście/wyjście ilustrujące oczekiwane zachowanie. Dwa lub trzy dobrze dobrane przykłady często poprawiają jakość odpowiedzi bardziej niż tysiące słów instrukcji. Mają jednak swoją cenę w tokenach.

**Budżet generowania**: tokeny zarezerwowane na odpowiedź modelu. Jeśli całkowicie wypełnisz okno, model nie będzie miał miejsca na wygenerowanie odpowiedzi. Zarezerwuj co najmniej 2000–4000 tokenów na generowanie.

### Strategie kompresji kontekstu

**Podsumowanie historii**: zamiast przechowywać dosłowny zapis wszystkich poprzednich tur, podsumowuj rozmowę w regularnych odstępach. „Omówiliśmy X, ustaliliśmy Y, użytkownik chce Z" w 100 tokenach zastępuje 10 tur wymagających 2000 tokenów. Uruchamiaj podsumowanie, gdy historia przekroczy określony próg (np. 5000 tokenów).

**Filtrowanie według trafności**: oceniaj każdy pobrany dokument pod kątem bieżącego zapytania i odrzucaj te poniżej progu. Jeśli pobrano 10 fragmentów, ale tylko 3 są istotne, pozostałe 7 należy pominąć. Trzy wysoce trafne fragmenty są wartościowsze niż dziesięć przeciętnych.

**Selekcja narzędzi**: klasyfikuj intencję zapytania użytkownika i dołączaj tylko narzędzia odpowiadające tej intencji. Pytanie o kod nie wymaga narzędzi kalendarza. Pytanie dotyczące planowania nie wymaga narzędzi systemu plików. Zabieg ten może zmniejszyć liczbę tokenów definicji narzędzi z 8000 do 1000.

**Rekurencyjne podsumowanie**: w przypadku bardzo długich dokumentów podsumowuj etapami. Najpierw streszczaj każdą sekcję, następnie podsumuj otrzymane streszczenia. Pięćdziesięciostronicowy dokument można sprowadzić do 500 tokenów zawierających kluczowe punkty.

### Systemy pamięci

Inżynieria kontekstu obejmuje trzy horyzonty czasowe.

**Pamięć krótkotrwała**: bieżąca rozmowa, przechowywana bezpośrednio w oknie kontekstowym. Rośnie z każdą turą. Zarządzana przez podsumowanie i obcinanie.

**Pamięć długoterminowa**: fakty i preferencje zachowywane między sesjami. „Użytkownik preferuje TypeScript." „Projekt korzysta z PostgreSQL." Przechowywane w bazie danych i pobierane na początku sesji. Claude Code przechowuje je w plikach CLAUDE.md. ChatGPT — w swojej pamięci systemowej.

**Pamięć epizodyczna**: konkretne interakcje z przeszłości, które mogą mieć znaczenie w bieżącym kontekście. „W zeszły wtorek debugowaliśmy podobny problem w module uwierzytelniania." Przechowywane jako wektory osadzenia i pobierane wtedy, gdy bieżąca rozmowa przypomina wcześniejszą.

```mermaid
graph TD
    subgraph Memory["Memory Architecture"]
        direction TB
        STM["Short-term Memory\n(current conversation)\nDirect in context window"]
        LTM["Long-term Memory\n(facts, preferences)\nDB -> retrieved on session start"]
        EM["Episodic Memory\n(past interactions)\nEmbeddings -> retrieved on similarity"]
    end

    Q["Current Query"] --> STM
    Q --> LTM
    Q --> EM

    STM --> CW["Context Window"]
    LTM --> CW
    EM --> CW

    style STM fill:#1a1a2e,stroke:#51cf66,color:#fff
    style LTM fill:#1a1a2e,stroke:#0f3460,color:#fff
    style EM fill:#1a1a2e,stroke:#e94560,color:#fff
    style CW fill:#1a1a2e,stroke:#ffa500,color:#fff
```

### Dynamiczne składanie kontekstu

Kluczowa obserwacja: różne zapytania wymagają różnego kontekstu. Statyczny prompt systemowy, statyczne narzędzia i statyczna historia to marnotrawstwo zasobów. Najlepsze systemy składają kontekst dynamicznie, osobno dla każdego zapytania.

1. Sklasyfikuj intencję zapytania
2. Wybierz odpowiednie narzędzia (nie wszystkie dostępne)
3. Pobierz pasujące dokumenty (nie stały zestaw)
4. Uwzględnij trafne fragmenty historii (nie całą historię)
5. Dodaj przykłady demonstracyjne dopasowane do typu zadania
6. Ułóż wszystko według istotności: najważniejsze na początku, ważne na końcu, opcjonalne w środku

Właśnie to odróżnia dobrą aplikację AI od świetnej. Model jest ten sam. Kontekst jest czynnikiem wyróżniającym.

## Zbuduj to

### Krok 1: Licznik tokenów

Nie można zarządzać budżetem czegoś, czego nie można zmierzyć. Zbuduj prosty licznik tokenów (przybliżenie na podstawie podziału białymi znakami, gdyż dokładna liczba zależy od tokenizatora).

```python
import json
import numpy as np
from collections import OrderedDict

def count_tokens(text):
    if not text:
        return 0
    return int(len(text.split()) * 1.3)

def count_tokens_json(obj):
    return count_tokens(json.dumps(obj))
```

### Krok 2: Menedżer budżetu kontekstowego

Podstawowa abstrakcja. Menedżer budżetu śledzi, ile tokenów zużywa każdy składnik, i egzekwuje limity.

```python
class ContextBudget:
    def __init__(self, max_tokens=128000, generation_reserve=4000):
        self.max_tokens = max_tokens
        self.generation_reserve = generation_reserve
        self.available = max_tokens - generation_reserve
        self.allocations = OrderedDict()

    def allocate(self, component, content, max_tokens=None):
        tokens = count_tokens(content)
        if max_tokens and tokens > max_tokens:
            words = content.split()
            target_words = int(max_tokens / 1.3)
            content = " ".join(words[:target_words])
            tokens = count_tokens(content)

        used = sum(self.allocations.values())
        if used + tokens > self.available:
            allowed = self.available - used
            if allowed <= 0:
                return None, 0
            words = content.split()
            target_words = int(allowed / 1.3)
            content = " ".join(words[:target_words])
            tokens = count_tokens(content)

        self.allocations[component] = tokens
        return content, tokens

    def remaining(self):
        used = sum(self.allocations.values())
        return self.available - used

    def utilization(self):
        used = sum(self.allocations.values())
        return used / self.max_tokens

    def report(self):
        total_used = sum(self.allocations.values())
        lines = []
        lines.append(f"Context Budget Report ({self.max_tokens:,} token window)")
        lines.append("-" * 50)
        for component, tokens in self.allocations.items():
            pct = tokens / self.max_tokens * 100
            bar = "#" * int(pct / 2)
            lines.append(f"  {component:<25} {tokens:>6} tokens ({pct:>5.1f}%) {bar}")
        lines.append("-" * 50)
        lines.append(f"  {'Used':<25} {total_used:>6} tokens ({total_used/self.max_tokens*100:.1f}%)")
        lines.append(f"  {'Generation reserve':<25} {self.generation_reserve:>6} tokens")
        lines.append(f"  {'Remaining':<25} {self.remaining():>6} tokens")
        return "\n".join(lines)
```

### Krok 3: Zmiana kolejności — zagubiony w środku

Wdrażaj strategię zmiany kolejności: najważniejsze elementy trafiają na początek i koniec, a te o najniższym priorytecie — do środka.

```python
def reorder_lost_in_middle(items, scores):
    paired = sorted(zip(scores, items), reverse=True)
    sorted_items = [item for _, item in paired]

    if len(sorted_items) <= 2:
        return sorted_items

    first_half = sorted_items[::2]
    second_half = sorted_items[1::2]
    second_half.reverse()

    return first_half + second_half

def score_relevance(query, documents):
    query_words = set(query.lower().split())
    scores = []
    for doc in documents:
        doc_words = set(doc.lower().split())
        if not query_words:
            scores.append(0.0)
            continue
        overlap = len(query_words & doc_words) / len(query_words)
        scores.append(round(overlap, 3))
    return scores
```

### Krok 4: Kompresor historii rozmów

Streszczaj stare fragmenty konwersacji, aby odzyskać budżet tokenów.

```python
class ConversationManager:
    def __init__(self, max_history_tokens=5000):
        self.turns = []
        self.summaries = []
        self.max_history_tokens = max_history_tokens

    def add_turn(self, role, content):
        self.turns.append({"role": role, "content": content})
        self._compress_if_needed()

    def _compress_if_needed(self):
        total = sum(count_tokens(t["content"]) for t in self.turns)
        if total <= self.max_history_tokens:
            return

        while total > self.max_history_tokens and len(self.turns) > 4:
            old_turns = self.turns[:2]
            summary = self._summarize_turns(old_turns)
            self.summaries.append(summary)
            self.turns = self.turns[2:]
            total = sum(count_tokens(t["content"]) for t in self.turns)

    def _summarize_turns(self, turns):
        parts = []
        for t in turns:
            content = t["content"]
            if len(content) > 100:
                content = content[:100] + "..."
            parts.append(f"{t['role']}: {content}")
        return "Previous: " + " | ".join(parts)

    def get_context(self):
        parts = []
        if self.summaries:
            parts.append("[Conversation Summary]")
            for s in self.summaries:
                parts.append(s)
        parts.append("[Recent Conversation]")
        for t in self.turns:
            parts.append(f"{t['role']}: {t['content']}")
        return "\n".join(parts)

    def token_count(self):
        return count_tokens(self.get_context())
```

### Krok 5: Dynamiczny wybór narzędzi

Dołączaj tylko narzędzia istotne dla bieżącego zapytania. Sklasyfikuj intencję, a następnie przefiltruj listę narzędzi.

```python
TOOL_REGISTRY = {
    "read_file": {
        "description": "Read contents of a file",
        "tokens": 120,
        "categories": ["code", "files"],
    },
    "write_file": {
        "description": "Write content to a file",
        "tokens": 150,
        "categories": ["code", "files"],
    },
    "search_code": {
        "description": "Search for patterns in codebase",
        "tokens": 130,
        "categories": ["code"],
    },
    "run_command": {
        "description": "Execute a shell command",
        "tokens": 140,
        "categories": ["code", "system"],
    },
    "create_calendar_event": {
        "description": "Create a new calendar event",
        "tokens": 180,
        "categories": ["calendar"],
    },
    "list_emails": {
        "description": "List recent emails",
        "tokens": 160,
        "categories": ["email"],
    },
    "send_email": {
        "description": "Send an email message",
        "tokens": 200,
        "categories": ["email"],
    },
    "web_search": {
        "description": "Search the web for information",
        "tokens": 140,
        "categories": ["research"],
    },
    "query_database": {
        "description": "Run a SQL query on the database",
        "tokens": 170,
        "categories": ["code", "data"],
    },
    "generate_chart": {
        "description": "Generate a chart from data",
        "tokens": 190,
        "categories": ["data", "visualization"],
    },
}

def classify_intent(query):
    query_lower = query.lower()

    intent_keywords = {
        "code": ["code", "function", "bug", "error", "file", "implement", "refactor", "debug", "test"],
        "calendar": ["meeting", "schedule", "calendar", "appointment", "event"],
        "email": ["email", "mail", "send", "inbox", "message"],
        "research": ["search", "find", "what is", "how does", "explain", "look up"],
        "data": ["data", "query", "database", "chart", "graph", "analytics", "sql"],
    }

    scores = {}
    for intent, keywords in intent_keywords.items():
        score = sum(1 for kw in keywords if kw in query_lower)
        if score > 0:
            scores[intent] = score

    if not scores:
        return ["code"]

    max_score = max(scores.values())
    return [intent for intent, score in scores.items() if score >= max_score * 0.5]

def select_tools(query, token_budget=2000):
    intents = classify_intent(query)
    relevant = {}
    total_tokens = 0

    for name, tool in TOOL_REGISTRY.items():
        if any(cat in intents for cat in tool["categories"]):
            if total_tokens + tool["tokens"] <= token_budget:
                relevant[name] = tool
                total_tokens += tool["tokens"]

    return relevant, total_tokens
```

### Krok 6: Potok pełnego składania kontekstu

Połącz wszystkie elementy. Na podstawie zapytania dynamicznie zbuduj optymalny kontekst.

```python
class ContextEngine:
    def __init__(self, max_tokens=128000, generation_reserve=4000):
        self.budget = ContextBudget(max_tokens, generation_reserve)
        self.conversation = ConversationManager(max_history_tokens=5000)
        self.system_prompt = (
            "You are a helpful AI assistant. You have access to tools for "
            "code editing, file management, web search, and data analysis. "
            "Use the appropriate tools for each task. Be concise and accurate."
        )
        self.knowledge_base = [
            "Python 3.12 introduced type parameter syntax for generic classes using bracket notation.",
            "The project uses PostgreSQL 16 with pgvector for embedding storage.",
            "Authentication is handled by Supabase Auth with JWT tokens.",
            "The frontend is built with Next.js 15 using the App Router.",
            "API rate limits are set to 100 requests per minute per user.",
            "The deployment pipeline uses GitHub Actions with Docker multi-stage builds.",
            "Test coverage must be above 80% for all new modules.",
            "The codebase follows the repository pattern for data access.",
        ]

    def assemble(self, query):
        self.budget = ContextBudget(self.budget.max_tokens, self.budget.generation_reserve)

        system_content, _ = self.budget.allocate("system_prompt", self.system_prompt, max_tokens=1000)

        tools, tool_tokens = select_tools(query, token_budget=2000)
        tool_text = json.dumps(list(tools.keys()))
        tool_content, _ = self.budget.allocate("tools", tool_text, max_tokens=2000)

        relevance = score_relevance(query, self.knowledge_base)
        threshold = 0.1
        relevant_docs = [
            doc for doc, score in zip(self.knowledge_base, relevance)
            if score >= threshold
        ]

        if relevant_docs:
            doc_scores = [s for s in relevance if s >= threshold]
            reordered = reorder_lost_in_middle(relevant_docs, doc_scores)
            doc_text = "\n".join(reordered)
            doc_content, _ = self.budget.allocate("retrieved_context", doc_text, max_tokens=3000)

        history_text = self.conversation.get_context()
        if history_text.strip():
            history_content, _ = self.budget.allocate("conversation_history", history_text, max_tokens=5000)

        query_content, _ = self.budget.allocate("user_query", query, max_tokens=500)

        return self.budget

    def chat(self, query):
        self.conversation.add_turn("user", query)
        budget = self.assemble(query)
        response = f"[Response to: {query[:50]}...]"
        self.conversation.add_turn("assistant", response)
        return budget

def run_demo():
    print("=" * 60)
    print("  Context Engineering Pipeline Demo")
    print("=" * 60)

    engine = ContextEngine(max_tokens=128000, generation_reserve=4000)

    print("\n--- Query 1: Code task ---")
    budget = engine.chat("Fix the bug in the authentication module where JWT tokens expire too early")
    print(budget.report())

    print("\n--- Query 2: Research task ---")
    budget = engine.chat("What is the best approach for implementing vector search in PostgreSQL?")
    print(budget.report())

    print("\n--- Query 3: After conversation history builds up ---")
    for i in range(8):
        engine.conversation.add_turn("user", f"Follow-up question number {i+1} about the implementation details of the system")
        engine.conversation.add_turn("assistant", f"Here is the response to follow-up {i+1} with technical details about the architecture")

    budget = engine.chat("Now implement the changes we discussed")
    print(budget.report())

    print("\n--- Tool Selection Examples ---")
    test_queries = [
        "Fix the bug in auth.py",
        "Schedule a meeting with the team for Tuesday",
        "Show me the database query performance stats",
        "Search for best practices on error handling",
    ]

    for q in test_queries:
        tools, tokens = select_tools(q)
        intents = classify_intent(q)
        print(f"\n  Query: {q}")
        print(f"  Intents: {intents}")
        print(f"  Tools: {list(tools.keys())} ({tokens} tokens)")

    print("\n--- Lost-in-the-Middle Reordering ---")
    docs = ["Doc A (most relevant)", "Doc B (somewhat relevant)", "Doc C (least relevant)",
            "Doc D (relevant)", "Doc E (moderately relevant)"]
    scores = [0.95, 0.60, 0.20, 0.80, 0.50]
    reordered = reorder_lost_in_middle(docs, scores)
    print(f"  Original order: {docs}")
    print(f"  Scores:         {scores}")
    print(f"  Reordered:      {reordered}")
    print(f"  (Most relevant at start and end, least relevant in middle)")
```

## Użyj tego

### Strategia kontekstowa Claude Code

Claude Code zarządza kontekstem warstwowo. Prompt systemowy zawiera reguły zachowania i definicje narzędzi (~6 tys. tokenów). Po otwarciu pliku jego zawartość jest wstrzykiwana jako kontekst. Wyniki wyszukiwania są dołączane na bieżąco. Stare fragmenty konwersacji są streszczane. Plik CLAUDE.md zapewnia pamięć długoterminową utrzymującą się przez całą sesję.

Kluczowa decyzja architektoniczna: Claude Code nie ładuje całej bazy kodu do kontekstu. Pobiera odpowiednie pliki na żądanie. To właśnie jest inżynieria kontekstu w praktyce.

### Dynamiczne ładowanie kontekstu w Cursor

Cursor indeksuje całą bazę kodu w postaci wektorów osadzenia. Gdy wpisujesz zapytanie, system pobiera najbardziej trafne pliki i bloki kodu na podstawie podobieństwa wektorowego. Tylko te elementy trafiają do okna kontekstowego. Baza kodu licząca 500 tys. linii zostaje skompresowana do 5–10 najbardziej odpowiednich fragmentów.

Wzorzec jest prosty: osadzaj wszystko, pobieraj na żądanie, dołączaj tylko to, co istotne.

### Pamięć ChatGPT

ChatGPT przechowuje preferencje i fakty użytkownika w postaci pamięci długoterminowej. Na początku każdej rozmowy odpowiednie wspomnienia są pobierane i wstrzykiwane do promptu systemowego. „Użytkownik preferuje Python" kosztuje 5 tokenów, lecz pozwala zaoszczędzić setki tokenów powtarzanych instrukcji w kolejnych sesjach.

### RAG jako inżynieria kontekstu

Retrieval-Augmented Generation to sformalizowana inżynieria kontekstowa. Zamiast wbudowywać wiedzę w wagi modelu (trening) lub prompt systemowy (kontekst statyczny), w czasie wykonywania zapytania pobierasz odpowiednie dokumenty i wstawiasz je do okna kontekstowego. Cały potok RAG — fragmentacja, osadzanie, pobieranie, zmiana rankingu — istnieje po to, by rozwiązać jeden problem: umieścić właściwe informacje we właściwym miejscu okna kontekstowego.

## Wyślij to

Ta lekcja generuje `outputs/prompt-context-optimizer.md` — wielokrotnego użytku prompt sprawdzający strategię składania kontekstu i wskazujący optymalizacje. Podaj dane o promptach systemowych, liczbie narzędzi, średniej długości historii i strategii wyszukiwania, a narzędzie zidentyfikuje marnotrawstwo tokenów i zaproponuje usprawnienia.

Lekcja generuje też `outputs/skill-context-engineering.md` — strukturę decyzyjną do projektowania potoków składania kontekstu z uwzględnieniem rodzaju zadania, rozmiaru okna kontekstowego i budżetu opóźnień.

## Ćwiczenia

1. Dodaj „wykrywacz marnotrawstwa tokenów" do klasy ContextBudget. Powinien oznaczać składniki zużywające więcej niż 30% budżetu i proponować strategie kompresji właściwe dla danego typu składnika (podsumowanie historii, selekcja narzędzi, ponowne uszeregowanie dokumentów).

2. Zaimplementuj semantyczną deduplikację pobranego kontekstu. Jeśli dwa odzyskane dokumenty są podobne w ponad 80% (pod względem nakładania się słów lub podobieństwa cosinusowego ich osadzeń), zachowaj tylko ten z wyższą oceną trafności. Zmierz, ile tokenów budżetu udaje się odzyskać.

3. Zbuduj narzędzie do „odtwarzania kontekstu". Mając zapis rozmowy, odtwórz go za pomocą ContextEngine i zwizualizuj, jak zmienia się alokacja budżetu w kolejnych turach. Narysuj wykres wykorzystania tokenów według składnika w czasie. Wskaż turę, w której kontekst zaczyna się kompresować.

4. Zaimplementuj selektor narzędzi oparty na priorytetach. Zamiast binarnego włączania i wyłączania narzędzi, przypisz każdemu z nich ocenę trafności względem bieżącego zapytania. Dołączaj narzędzia w malejącej kolejności trafności, aż wyczerpie się budżet. Porównaj skuteczność zadań przy zestawach 5, 10, 20 i 50 dołączonych narzędzi.

5. Zbuduj kompresor kontekstu obsługujący kilka strategii. Zastosuj trzy podejścia do kompresji (obcinanie, podsumowanie, ekstrakcja kluczowych zdań) i porównaj je na zestawie 20 dokumentów. Zmierz kompromis między współczynnikiem kompresji a zachowaniem informacji (czy skompresowana wersja nadal zawiera odpowiedź na zapytanie?).

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|----------------------|
| Okno kontekstowe | „Ile model może odczytać" | Maksymalna liczba tokenów (wejście + wyjście), które model przetwarza w jednym przebiegu do przodu — 400 tys. dla GPT-5, 200 tys. (1M beta) dla Claude Opus 4.7, 2M dla Gemini 3 Pro |
| Inżynieria kontekstowa | „Zaawansowana inżynieria promptów" | Dyscyplina decydowania o tym, co trafia do okna kontekstowego, w jakiej kolejności i z jakim priorytetem — obejmuje pobieranie, kompresję, wybór narzędzi i zarządzanie pamięcią |
| Zagubiony w środku | „Modele zapominają o tym, co jest pośrodku" | Empiryczne ustalenie, że LLM lepiej skupiają się na początku i końcu kontekstu, przy spadku dokładności o 10–20% w przypadku informacji umieszczonych w środkowej części |
| Budżet tokenów | „Ile zostało ci tokenów" | Jawny przydział pojemności okna kontekstowego między składniki (prompt systemowy, narzędzia, historia, pobieranie, generowanie) z limitami na składnik |
| Kontekst dynamiczny | „Ładowanie zasobów w locie" | Odmienne składanie okna kontekstowego dla każdego zapytania w oparciu o klasyfikację intencji, dobór narzędzi i wyniki wyszukiwania |
| Podsumowanie historii | „Kompresowanie rozmowy" | Zastąpienie dosłownych starych tur konwersacji zwięzłym streszczeniem — redukuje koszt tokenowy przy zachowaniu kluczowych informacji |
| Selekcja narzędzi | „Uwzględnianie tylko odpowiednich narzędzi" | Klasyfikacja intencji zapytania i dołączanie wyłącznie pasujących definicji narzędzi, co zmniejsza koszt tokenowy o 60–80% |
| Pamięć długoterminowa | „Zapamiętywanie między sesjami" | Fakty i preferencje przechowywane w bazie danych i pobierane na początku sesji — CLAUDE.md, ChatGPT Memory i podobne mechanizmy |
| Pamięć epizodyczna | „Pamiętanie konkretnych zdarzeń z przeszłości" | Wcześniejsze interakcje przechowywane jako osadzenia i pobierane, gdy bieżące zapytanie jest podobne do poprzedniej rozmowy |
| Budżet generowania | „Miejsce na odpowiedź" | Tokeny zarezerwowane na wyjście modelu — jeśli kontekst całkowicie wypełni okno, model nie będzie miał miejsca na udzielenie odpowiedzi |

## Dalsze czytanie

– [Liu i in., 2023 – „Lost in the Middle: How Models Language Use Long Contexts"](https://arxiv.org/abs/2307.03172) – przełomowe badanie dotyczące uwagi zależnej od pozycji, pokazujące trudności modeli z informacjami w środku długich kontekstów
– [Post na blogu Anthropic's Contextual Retrieval](https://www.anthropic.com/news/contextual-retrieval) – jak Anthropic podchodzi do kontekstowego wyszukiwania fragmentów, ograniczając liczbę niepowodzeń przy pobieraniu o 49%
– [„Context Engineering" Simona Willisona](https://simonwillison.net/2025/Jun/27/context-engineering/) – post, w którym po raz pierwszy nazwano tę dyscyplinę i odróżniono ją od inżynierii promptów
- [Dokumentacja LangChain na temat RAG](https://python.langchain.com/docs/tutorials/rag/) — praktyczna implementacja Retrieval-Augmented Generation jako wzorca inżynierii kontekstu
– [Test igły w stogu siana Grega Kamradta](https://github.com/gkamradt/LLMTest_NeedleInAHaystack) – test porównawczy, który ujawnił błędy pobierania zależne od pozycji we wszystkich głównych modelach
– [Pope i in., „Efficiently Scaling Transformer Inference" (2022)](https://arxiv.org/abs/2211.05102) – dlaczego długość kontekstu wpływa na pamięć i opóźnienia oraz jak pamięć podręczna KV, MQA i GQA zmieniają obliczenia budżetu
- [Agrawal i in., „SARATHI: Efficient LLM Inference by Piggybacking Decodes with Chunked Prefills" (2023)](https://arxiv.org/abs/2308.16369) — dwie fazy wnioskowania, które sprawiają, że długie prompty są kosztowne pod względem TTFT, lecz tanie pod względem TPOT; podstawa zrozumienia kompromisów przy pakowaniu kontekstu
– [Ainslie i in., „GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints" (EMNLP 2023)](https://arxiv.org/abs/2305.13245) – artykuł o Grouped Query Attention, który zmniejsza pamięć KV 8-krotnie w dekoderach produkcyjnych bez utraty jakości
