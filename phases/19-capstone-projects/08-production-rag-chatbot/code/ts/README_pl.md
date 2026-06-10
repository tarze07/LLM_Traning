# Capstone 08 - Chatbot produkcyjny RAG (TypeScript)

Szkielet interfejsu użytkownika czatu, który przesyła strumieniowo odpowiedź zakotwiczoną w cytatach za pośrednictwem funkcji Server-Sent
Wydarzenia. Łączy się z potokiem Pythona w `../main.py`. Stan rozmowy żyje
w mapie w procesie z kluczem `sessionId`, więc ten sam identyfikator sesji może prowadzić
wieloobrotowe dialogi.

## Układ

```text
ts/
  package.json
  tsconfig.json
  src/
    index.ts        # entrypoint, demo + HTTP server
    server.ts      # hono app, /, /chat/stream (SSE), /sessions, /health
    session.ts     # SessionStore (Map<sessionId, Session>)
    stream.ts      # SSE frame encoder + parser + mock retrieval + tokenizer
    types.ts        # Session, Turn, Citation, KbEntry, SseEvent
  tests/
    session.test.ts
    stream.test.ts
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

Serwer interaktywny wybiera wolny port, gdy `PORT` jest rozbrojony, montuje czat
Klient HTML na `/` i strumienie przez `GET /chat/stream?sessionId=...&q=...`. The
klient demonstracyjny używa `EventSource` i nasłuchuje `session`, `citations`, `token`,
i wydarzenia `done`.

## Testy

Biegacz `node --test` przez tsx. Zasięg:

- SessionStore: tworzenie, wyszukiwanie, dołączanie, lista, brak operacji w przypadku brakującego identyfikatora.
- Koder SSE + parser w obie strony; zwiększenie odzyskiwania według znacznika jurysdykcji;
  rezerwowy tokenizer + ogon „Zobacz także”.
- Serwer: `/`, `/health`, `/chat/stream` szczęśliwa ścieżka (sesja + cytaty +
  token + zrobione), 400 na brakujące q, trwałość sesji wieloturowej,
  Lista `/sessions`.