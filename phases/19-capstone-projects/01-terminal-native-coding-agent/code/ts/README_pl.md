# Capstone 19/01 — Agent kodowania natywnego dla terminala (TypeScript)

Wieloplikowa uprząż TypeScript dla pętli planuj/działaj/obserwuj opisana w
`../docs/en.md`. Offline, deterministyczne, zero połączeń sieciowych.

## Układ

```text
src/
  index.ts     entry point; runs a scripted demo and the eval, then exits 0
  repl.ts      interactive command parser (run / eval / help / quit)
  harness.ts   the plan-act-observe loop, wired through the hook bus
  hooks.ts     eight-event hook bus plus a destructive-command guard
  model.ts     scripted offline LLM that drives the demo
  tools.ts     read_file + run_shell with zod-validated args
  plan.ts     PlanState (todo rewrite) + Budget (turn / token / dollar ceilings)
  eval.ts      tiny pass/fail counter across three offline tasks
  types.ts     shared shape definitions
tests/
  harness.test.ts
  tools.test.ts
```

## Biegnij

```bash
npm install
npm start                # runs the scripted demo + offline eval, exits 0
npm start -- --repl      # opens the interactive harness REPL
npm test                 # node --test runner via tsx
npm run typecheck        # tsc --noEmit
```

Nieinteraktywna ścieżka `npm start` potwierdza, że raport eval „passed=3
nieudane=0` i że uruchomienie skryptowe zbiega się z gotowym planem. Jakikolwiek dryf
nie udaje się uruchomić.