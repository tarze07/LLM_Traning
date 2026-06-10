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

Jedna praktyczna uwaga: notebooki są puste (same `.gitkeep`) — nauka idzie przez `code/main.py` + `docs/en.md`, co przy Twoim stylu pracy w terminalu jest raczej zaletą niż wadą.