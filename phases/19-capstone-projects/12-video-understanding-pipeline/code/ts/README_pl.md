# Lekcja 12 – Potok zrozumienia wideo (interfejs TypeScript)

TypeScript połowa zwieńczenia. Strona Pythona (`code/main.py`) jest właścicielem
indeks wielowektorowy i uziemienie czasowe. Ten projekt zawiera pulpit nawigacyjny
połowa: aplikacja Hono na czterech etapach potoku (fragment, osadzenie, indeks, qa).

## Układ

```text
src/
  index.ts     entry: demo (default) or HTTP server (--serve)
  server.ts    Hono routes (/, /jobs, /job/:id) + HTML index
  jobs.ts     JobStore + fixture seeder
  stages.ts    stage advance + overall status
  types.ts     Stage, StageState, Job
tests/
  stages.test.ts  job state transitions + store
```

## Biegnij

```bash
npm install
npm run typecheck
npm test
npm start              # self-terminating demo
npm run serve          # HTTP server on :8123
```