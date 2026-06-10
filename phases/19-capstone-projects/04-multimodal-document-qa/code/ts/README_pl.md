# Capstone 04 - Multimodalna kontrola jakości dokumentów (TypeScript)

Szkielet przeglądarki, który zwraca adres URL obrazu strony oraz listę JSON cytowanych ograniczeń
pudełka na dokumenty. Odpowiedź HTML zawiera mały skrypt nakładki na płótnie
który rysuje cytowane regiony na górze obrazu strony. Pasuje do Pythona
rurociąg w `../main.py`.

## Układ

```text
ts/
  package.json
  tsconfig.json
  src/
    index.ts        # entrypoint, demo + HTTP server
    server.ts       # hono app, /health, /, /document/:id
    fixtures.ts     # 10-K table + Nature figure fixtures
    render.ts       # HTML index + per-document overlay renderer
    types.ts        # DocumentFixture, EvidenceRegion, BoundingBox
  tests/
    fixtures.test.ts
    render.test.ts
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

Serwer interaktywny wybiera wolny port, gdy `PORT` jest rozbrojony i drukuje
wybrany adres URL na standardowe wyjście. Odwiedź `/` dla indeksu, `/document/10k-acme-2025` dla
nakładkę demonstracyjną lub ustaw `accept: application/json`, aby uzyskać uporządkowaną odpowiedź.

## Testy

Biegacz `node --test` przez tsx. Testy obejmują wyszukiwanie urządzeń (pozytywne + negatywne),
Ucieczka HTML dla pięciu wrogich znaków, struktura ładunku HTML dokumentu,
oraz trasy honorowe (200, 404, negocjacja treści).