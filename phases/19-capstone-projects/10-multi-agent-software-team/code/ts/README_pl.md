# Zespół programistów obsługujący wiele agentów (szkielet TypeScript)

Wieloplikowy szkielet TypeScript dla zwieńczenia wieloagentowego zespołu programistycznego.
Planiści, programiści i recenzenci współdzielą przestrzeń roboczą i zmieniają się między sobą
koordynator. Odcinek drzewa roboczego uruchamia procesy potomne poprzez plik execFile z rozszerzeniem
lista odrzuconych i odmowa powłoki-metachar.

## Układ

- `src/index.ts` — program demonstracyjny.
- `src/agent.ts` — podstawowa klasa `Agent` plus `PlannerAgent`, `CoderAgent`, `ReviewerAgent`.
- `src/coordinator.ts` — pętla okrężna i śledzenie rotacji.
- `src/workspace.ts` — współdzielony system plików w pamięci i dziennik komunikatów.
- `src/runtime.ts` — Odcinek drzewa roboczego `child_process.execFile` z listą odrzuconych.
- `src/types.ts` — typy wspólne.
- Testy w stylu `tests/*.test.ts` — `node --test` poprzez `tsx`.

## Zainstaluj

```bash
npm install
```

## Biegnij

```bash
npm start
```

## Zweryfikuj

```bash
npm run typecheck
npm test
```

## Odniesienia do specyfikacji

- Lekcja źródłowa: `phases/19-capstone-projects/10-multi-agent-software-team/docs/en.md`
- [MetaGPT](https://github.com/FoundationAgents/MetaGPT) platforma wieloagentowa oparta na rolach.