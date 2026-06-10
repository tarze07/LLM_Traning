# Lekcja 17 - Osobisty nauczyciel AI (aplikacja internetowa TypeScript)

TypeScript połowa zwieńczenia. Strona Pythona dostarcza model ucznia i
polityka korepetytorów; ten projekt udostępnia powierzchnię aplikacji internetowej: program nauczania DAG
chodzik, model ucznia w stylu BKT i FSRS-lite z odstępami
harmonogram za dwiema trasami HTTP.

## Układ

```text
src/
  index.ts       entry: demo (default) or HTTP server (--serve)
  server.ts      Hono routes (GET /lesson/next, POST /lesson/:id/submit)
  curriculum.ts  DAG fixture + Kahn topo sort + next-lesson picker
  mastery.ts     MasteryStore (per-lesson BKT-ish update)
  repetition.ts  scheduleNextDue (interval doubling / halving, clamped)
  types.ts       Lesson, Mastery, Pick
tests/
  curriculum.test.ts  topo order, BKT update, FSRS scheduling
```

## Biegnij

```bash
npm install
npm run typecheck
npm test
npm start            # self-terminating curriculum walk
npm run serve        # HTTP server on :8090
```