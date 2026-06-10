Sprawdziłem — sklonowałem repo i przejrzałem każdą lekcję. Dwie ważne wiadomości:

**1. Wszystkie lekcje są gotowe.** Każda z faz 11, 13, 14, 15, 16 ma komplet: kod (Python, często też TS), dokumentację, quizy i pliki wynikowe (skills/prompty). Zajrzałem do środka kilku — to solidna, aktualna treść (np. lekcja o pętli agentowej cytuje paper ReAct, omawia Claude Agent SDK i wzorce z 2026 r.), nie puste szkielety.

**2. Repo mocno się rozrosło względem README** — tabele, na których oparłem poprzednią numerację, są nieaktualne. Phase 14 ma teraz **42 lekcje** zamiast 15, Phase 13 ma 23, Phase 15 ma 22. Numeracja i nazwy się zmieniły, więc oto **skorygowana kolejność** według faktycznych katalogów:

## Miesiąc 1 — Phase 11 (LLM Engineering)

`01-prompt-engineering` → `02-few-shot-cot` → `03-structured-outputs` → `09-function-calling` → `04-embeddings` → `05-context-engineering` (nowa, ważna!) → `06-rag` → `07-advanced-rag` → `10-evaluation` → `11-caching-cost` → `15-prompt-caching`

## Miesiąc 2 — Phase 13 (Tools & MCP) + rdzeń Phase 14

**Phase 13:** `01-the-tool-interface` → `02-function-calling-deep-dive` → `05-tool-schema-design` → `06-mcp-fundamentals` → `07-building-an-mcp-server` → `08-building-an-mcp-client` → `09-mcp-transports` → `10-mcp-resources-and-prompts` → `15-mcp-security-tool-poisoning`

**Phase 14 (rdzeń):** `01-the-agent-loop` → `06-tool-use-and-function-calling` → `02-rewoo-plan-and-execute` → `03-reflexion-verbal-rl` → `05-self-refine-and-critic` → `07-memory-virtual-context-memgpt` → `09-hybrid-memory-mem0` → `12-anthropic-workflow-patterns`

## Miesiąc 3 — produkcja i bezpieczeństwo

**Phase 14 (zaawansowane):** `26-failure-modes-agentic` → `27-prompt-injection-defense` → `28-orchestration-patterns` → `30-eval-driven-agent-development` → `31` do `38` (cykl "agent workbench" — werifikacja, scope contracts, feedback loops) → `42-agent-workbench-capstone` (najbogatsza lekcja w repo, 20 plików)

**Phase 15 (wybrane):** `01-long-horizon-agents` → `10-claude-code-permission-modes` → `12-durable-execution` → `13-cost-governors` → `14-kill-switches-canaries` → `15-propose-then-commit` → `16-checkpoints-rollback`

**Frameworki (na koniec, świadomie):** `14/13-langgraph` → `14/17-claude-agent-sdk` → `11/17-agent-framework-tradeoffs`

**Projekt końcowy:** w Phase 19 jest teraz `06-devops-troubleshooting-agent` — idealnie pokrywa się z tym, co proponowałem jako Twój projekt portfolio. Alternatywnie `16-github-issue-to-pr-agent` lub seria `20-29` (budowa pełnego harnessa agentowego krok po kroku).

Pominięcia bez zmian: fazy 1-10 i 12 nadal zbędne dla tej ścieżki, Phase 16 (multi-agent, 25 lekcji) na miesiąc 4+.

Przeanalizowałem łańcuch zależności — każda lekcja w repo deklaruje swoje `Prerequisites`, więc dało się to prześledzić twardo, nie na wyczucie. Łańcuch wygląda tak:

**Phase 10 ← Phase 7 (Transformers) ← Phase 3 (Deep Learning) + Phase 5 (NLP) ← Phase 1 (Matematyka)**

Lekcja `10/04` (Pre-Training Mini GPT) to serce fazy — budujesz GPT-2 124M **w czystym NumPy**, ręcznie licząc każdy gradient. To ustawia poprzeczkę: musisz rozumieć backpropagację i architekturę transformera od środka, nie z diagramów.

## Minimalna ścieżka przygotowawcza

**Phase 1 — Matematyka (8 z 22 lekcji):**
- `01` + `02` — algebra liniowa, operacje na macierzach
- `04` — pochodne i gradienty
- `05` — chain rule i autodiff ← bez tego backprop będzie magią
- `06` — prawdopodobieństwo i rozkłady
- `08` — gradient descent
- `09` — teoria informacji (entropia, cross-entropy ← to jest loss LLM-ów!)
- `13` — stabilność numeryczna (softmax overflow itp.)

**Phase 3 — Deep Learning Core (lekcje 01-09 + 11):**
Kurs sam mówi: kolejno `01` perceptron → `02` sieci wielowarstwowe → `03` **backpropagacja** → `04` aktywacje → `05` funkcje straty → `06` optymalizatory (Adam/AdamW — tym trenuje się LLM-y) → `07` regularyzacja → `08` inicjalizacja wag → `09` learning rate schedules i warmup (krytyczne przy pre-trainingu). Plus `11` intro do PyTorch — potrzebne od lekcji `10/05` (distributed training). Lekcję `10` (mini framework) możesz pominąć, choć to dobre utrwalenie.

**Phase 5 — NLP (tylko 4 z 29 lekcji):**
- `01` — przetwarzanie tekstu i tokenizacja ← jawny prereq `10/01`
- `03` — Word2Vec (intuicja embeddingów)
- `09` — seq2seq ← prereq Phase 7
- `10` — mechanizm atencji ← prereq Phase 7

**Phase 7 — Transformers (10 z 16 lekcji):**
`01` dlaczego transformery → `02` **self-attention from scratch** → `03` multi-head → `04` positional encoding (RoPE!) → `05` pełny transformer → `06` BERT → `07` **GPT (causal LM)** ← bezpośrednia podstawa `10/04` → `08` T5/BART → `12` KV cache i Flash Attention ← prereq `10/12` → `13` scaling laws. Na koniec `14` capstone "zbuduj transformer" — kurs ostrzega przy nim wprost: nie przeskakuj wcześniejszych. Pomijasz: `09` (ViT), `10` (audio), `15-16` (warianty atencji — potrzebne dopiero do zaawansowanych lekcji 10/16-22).

## Wewnątrz Phase 10 — kolejność z deklarowanych zależności

Rdzeń liniowy: `01 → 02 → 03 → 04 → 05 → 06 → 07 → 08 → 09 → 10 → 11 → 12 → 13` (lekcja 13 wymaga wprost wszystkich 01-12).

Zaawansowane `14-22` (DeepSeek-V3, sparse attention, DualPipe, Jamba) traktuj jako opcjonalny "miesiąc badawczy" — np. `20-deepseek-v3-walkthrough` wymaga aż czterech wcześniejszych lekcji z tej fazy (14, 17, 18, 19).

## Bilans

Razem: **~32 lekcje przygotowania + 13 lekcji rdzenia Phase 10** ≈ 45 lekcji. Przy deklarowanych 60-120 min/lekcję to realnie **2,5-3 miesiące** przy 8-10 h tygodniowo — czyli drugi, osobny projekt o skali Twojego planu agentowego.

Szczera uwaga: do bycia ekspertem od **agentów** Phase 10 nie jest konieczna — to ścieżka "rozumiem model od środka" (badacz/inżynier ML), komplementarna, ale niezależna. Ma jednak realną wartość: po `10/04` przestaniesz traktować LLM jak czarną skrzynkę, a `10/11-12` (kwantyzacja, optymalizacja inferencji) przydają się, gdy agent ma działać na lokalnym modelu. Sensowna kolejność życiowa: najpierw ścieżka agentowa (3 mies.), potem Phase 10 jako pogłębienie.

Chcesz, żebym z tych 45 lekcji ułożył tygodniowy harmonogram jak poprzednio?





Jedna praktyczna uwaga: notebooki są puste (same `.gitkeep`) — nauka idzie przez `code/main.py` + `docs/en.md`, co przy Twoim stylu pracy w terminalu jest raczej zaletą niż wadą.
