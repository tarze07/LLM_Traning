# Capstone 19/03 — Asystent głosowy w czasie rzeczywistym (TypeScript)

Wieloplikowa wiązka klienta internetowego TypeScript do strumieniowego przesyłania głosu
opisane w `../docs/en.md`. Symulacja maszyny stanu offline oraz transmisja na żywo
Serwer WebSocket obsługiwany przez pakiet `ws`.

## Układ

```text
src/
  index.ts        entry point; runs two offline sessions, probes the live ws, exits 0
  server.ts       hono /healthz + ws upgrade via WebSocketServer
  orchestrator.ts IDLE -> LISTENING -> WAITING -> THINKING -> SPEAKING with barge-in
  vad.ts          turn-completion scorer + synthetic 20ms-frame generator
  protocol.ts     zod-validated frame envelope (event / summary)
  types.ts        AudioChunk, Metrics, SessionOptions, SessionSummary
tests/
  vad.test.ts
  orchestrator.test.ts
  protocol.test.ts
```

## Biegnij

```bash
npm install
npm start                # runs two offline sessions + ws self-probe, exits 0
npm start -- --serve     # keep ws server up; ctrl-c to stop
npm test                 # node --test runner via tsx
npm run typecheck        # tsc --noEmit
```

Nieinteraktywna ścieżka `npm start` zapewnia osiągnięcie czystej sesji
`first_audio_out`, sesja wtrącenia rejestruje co najmniej jedno zdarzenie wtrącenia,
a aktywna sonda WebSocket odbiera ramkę `summary` przed zamknięciem.