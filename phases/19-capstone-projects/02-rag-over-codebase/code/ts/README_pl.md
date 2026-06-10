# Capstone 19/02 — RAG na bazie kodu (TypeScript)

Wieloplikowy interfejs API wyszukiwania kodu TypeScript dla potoku pobierania hybrydowego
opisane w `../docs/en.md`. Offline, deterministyczny, sześcioczęściowy korpus próbek,
węzeł:http za modułem obsługi hono fetch.

## Układ

```text
src/
  index.ts        entry point; boots node:http + self-probe + exits 0
  server.ts       hono routes (/healthz, /query) with zod-validated POST body
  retrieval.ts    runQuery + RRF merge over dense and BM25
  index_store.ts  FNV-1a hash embedder, cosine, field-weighted BM25
  corpus.ts       six-chunk sample (uploader / auth / client / catalog)
  types.ts        Chunk, RankedChunk, QueryResponse, anchor()
tests/
  index_store.test.ts
  retrieval.test.ts
  server.test.ts
```

## Biegnij

```bash
npm install
npm start                # boots api, probes three queries, exits 0
npm start -- --serve     # keep server up; ctrl-c to stop
npm test                 # node --test runner via tsx
npm run typecheck        # tsc --noEmit
```

Nieinteraktywna ścieżka `npm start` zapewnia, że `/healthz` zwraca 200 i
że każde zapytanie sondujące zwraca co najmniej jeden cytat. Trasy:

- `GET /healthz` — zwraca `{ok, corpus}`.
- `GET /query?q=...` – uruchamia zapytanie hybrydowe.
- `POST /query` — JSON `{q, topK?}`, zatwierdzony przez zod (`topK` ograniczony do 50).