# Lekcja 16 - GitHub Issue-to-PR Agent (odbiornik webhooka TypeScript)

TypeScript połowa zwieńczenia. Strona Pythona dostarcza pętlę agenta i
dyspozytor; Strona YAML dostarcza przepływ pracy Akcje. Ten projekt to GitHub
Odbiornik webhooka aplikacji: HMAC weryfikuje surową treść, trasę według typu zdarzenia, wysyłkę
agent zastępczy dla `issues.opened`.

## Układ

```text
src/
  index.ts    entry: demo (default) or HTTP server (--serve)
  server.ts   Hono webhook receiver (POST /webhook)
  verify.ts   X-Hub-Signature-256 HMAC, timing-safe
  router.ts   event-type routing (ping, issues, pull_request)
  agent.ts    stub agent + audit log
  types.ts    payload + audit shapes
tests/
  verify.test.ts  signature pass, tampered, router pathing
```

## Biegnij

```bash
npm install
npm run typecheck
npm test
npm start            # self-terminating demo (in-process replays)
npm run serve        # HTTP server on :8081
```

Sekret HMAC jest odczytywany z `GH_WEBHOOK_SECRET` (domyślnie `demo-shared-secret`
na demonstrację).