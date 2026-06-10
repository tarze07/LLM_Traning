# Capstone 06 - Agent rozwiązywania problemów DevOps (TypeScript)

Szkielet integracji Slacka dla agenta dyżurującego w `../main.py`. Odsłania A
punkt końcowy polecenia ukośnika i punkt końcowy interaktywności (kliknięcie przycisku), oba bramkowane
przez podpis żądania HMAC-SHA256 firmy Slack plus 5-minutowe okno powtórki.
Niszczące środki zaradcze są uruchamiane dopiero po zatwierdzeniu karty Slack.

## Układ

```text
ts/
  package.json
  tsconfig.json
  src/
    index.ts          # entrypoint, demo + HTTP server
    server.ts         # hono app, /slack/command + /slack/interactivity
    slack_verify.ts   # HMAC v0 verification + timing-safe compare
    agent.ts          # mocked hypothesis ranker
    blocks.ts         # Block Kit response builder
    types.ts          # Hypothesis, AgentReport, SlackResponse, OutboundCall
  tests/
    slack_verify.test.ts
    agent.test.ts
    server.test.ts
```

## Biegnij

```bash
npm install
npm run typecheck
npm test
npm start          # one self-check pass, exits 0
npm run serve      # interactive HTTP server on 127.0.0.1:<port>
```

Ustaw `SLACK_SIGNING_SECRET=...`, aby zastąpić sekret zastępczy. The
serwer interaktywny drukuje wybrany port (losowo, gdy `PORT` jest rozbrojony).

## Testy

Biegacz `node --test` przez tsx. Zasięg:

- Weryfikacja podpisu Slack: ważny podpis przechodzi, podpis sfałszowany jest
  odrzucony, nieaktualny znacznik czasu (przesunięcie> 5 minut) zostaje odrzucony, nienumeryczny znacznik czasu jest odrzucany
  odrzucona, przed porównaniem w stałym czasie wykonywana jest ścieżka z niedopasowaniem długości.
- Próbny agent: ścieżka słowa kluczowego OOM, ścieżka słowa kluczowego CrashLoop, ścieżka zastępcza.
- Serwer: `/health`, `/slack/command` szczęśliwe/sfałszowane/nieaktualne ścieżki,
  `/slack/interactivity` zatwierdza działanie.