# Panel agenta migracji kodu (szkielet TypeScript)

Wieloplikowy szkielet TypeScriptu dla warstwy dashboardu migracji kodu
zwieńczenie agenta. Agent (Python) działa w piaskownicy; ten serwer renderuje
postęp dla operatora.

## Układ

- `src/index.ts` — punkt wejścia, symuluje ticki i opcjonalnie obsługuje HTTP.
- `src/server.ts` — trasy honorowe dla `/`, `/dashboard`, `/migrations`, `/migrations/:id`.
- `src/migrations.ts` — dane maszyny stanu i nasion dla poszczególnych plików.
- `src/cost.ts` — liczenie tur i egzekwowanie budżetu dolarowego.
- `src/types.ts` — typy wspólne.
- Testy w stylu `tests/*.test.ts` — `node --test` poprzez `tsx`.

## Zainstaluj

```bash
npm install
```

## Biegnij

```bash
npm start         # offline: simulate 40 ticks and print rollup
npm run serve     # serve the HTML dashboard on PORT (default 8009)
```

## Zweryfikuj

```bash
npm run typecheck
npm test
```

## Odniesienia do specyfikacji

- Lekcja źródłowa: `phases/19-capstone-projects/09-code-migration-agent/docs/en.md`
- Przepisy: [OpenRewrite](https://docs.openrewrite.org), libcst.