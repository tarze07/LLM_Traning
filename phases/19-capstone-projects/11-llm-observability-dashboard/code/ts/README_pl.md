# Pulpit nawigacyjny obserwowalności LLM (szkielet TypeScript)

Wieloplikowy szkielet TypeScript dla zwieńczenia pulpitu nawigacyjnego obserwowalności LLM.
Serwer Hono akceptuje rozpiętości OpenTelemetry GenAI i utrzymuje je w pierścieniu 10 tys
bufora i renderuje opóźnienia p50/p95/p99 i koszt na model.

## Układ

- `src/index.ts` — punkt wejścia, wysyła syntetyczne rozpiętości i opcjonalnie obsługuje HTTP.
- `src/server.ts` — trasy honorowe dla `/trace`, `/`, `/dashboard`, `/dashboard.json`, `/healthz`.
- `src/spans.ts` — `RingBuffer` i `ObservabilityStore` (domyślnie 10 tys. rozpiętości).
- `src/rollup.ts` — `percentile` i `rollUpByModel`.
- `src/pricing.ts` — 2026 ceny poszczególnych modeli i pomocnicy kosztowi.
- `src/types.ts` — typy wspólne.
- Testy w stylu `tests/*.test.ts` — `node --test` poprzez `tsx`.

## Zainstaluj

```bash
npm install
```

## Biegnij

```bash
npm start         # seeds 1200 synthetic spans and prints the rollup
npm run serve     # also serves the HTTP ingest + dashboard on PORT (default 8011)
```

## Zweryfikuj

```bash
npm run typecheck
npm test
```

## Odniesienia do specyfikacji

- Lekcja źródłowa: `phases/19-capstone-projects/11-llm-observability-dashboard/docs/en.md`
- [Konwencje semantyczne OpenTelemetry GenAI](https://opentelemetry.io/docs/specs/semconv/gen-ai/)