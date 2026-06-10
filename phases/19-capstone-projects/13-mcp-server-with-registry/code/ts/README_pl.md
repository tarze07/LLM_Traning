# Lekcja 13 – Wewnętrzny serwer MCP (TypeScript)

TypeScript połowa zwieńczenia. Strona Pythona (`code/main.py`) dostarcza
bramka rejestru i polityk; tym projektem jest transport MCP: ręcznie walcowany
JSON-RPC 2.0 rozdzielany znakami nowej linii przez stdio z trzema narzędziami do próbnych incydentów. Nie
`@modelcontextprotocol/sdk`; możesz zobaczyć każdy bajt w przewodzie.

## Układ

```text
src/
  index.ts      entry: fixture demo (default) or stdio loop (--serve)
  transport.ts  stdin readline + fixture replay
  protocol.ts   initialize / tools/list / tools/call / shutdown
  tools.ts      three incident tools + executors
  types.ts      JSON-RPC + tool shapes
tests/
  protocol.test.ts  roundtrip, list shape, dispatch, parse error
```

## Biegnij

```bash
npm install
npm run typecheck
npm test
npm start            # self-terminating fixture demo
npm run serve        # real stdio loop (waits on stdin)
```