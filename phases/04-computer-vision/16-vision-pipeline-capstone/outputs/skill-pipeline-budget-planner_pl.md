---

name: skill-pipeline-budget-planner
description: Biorąc pod uwagę docelowe opóźnienia i przepustowość, przypisz budżet czasu do każdego etapu potoku i zaznacz, który etap jako pierwszy nie przekroczy budżetu
version: 1.0.0
phase: 4
lesson: 16
tags: [vision, pipeline, performance, deployment]

---

# Planista budżetu rurociągu

Zmień docelowy poziom opóźnień/przepustowości w budżet etap po etapie, aby każdy członek zespołu wiedział, do jakiej liczby dąży.

## Kiedy używać

- Przed zbudowaniem nowej usługi wizyjnej należy ustalić oczekiwania na każdym etapie.
- Po pierwszym benchmarku, aby zobaczyć, który etap jest najbardziej oddalony od budżetu.
- Kiedy zmienia się umowa SLA i konieczna jest renegocjacja budżetów.

## Wejścia

- `p95_latency_target_ms`: budżet na żądanie.
- `target_qps`: przepustowość na replikę.
- `stages`: lista `{ name: str, current_ms: float }`.

## Zasady alokacji

Domyślny przydział na siedmiu standardowych etapach, jeśli nie podano bieżących pomiarów:

| Scena | Udostępnij |
|-------|-------|
| dekodowanie + wstępne przetwarzanie | 15% |
| detektor do przodu | 55% |
| detekcje postprocesowe (NMS, klamra) | 5% |
| przytnij + zmień rozmiar klasyfikatora | 5% |
| klasyfikator do przodu | 15% |
| walidacja schematu | <1% |
| response serialisation | 4% |

On GPU-bound pipelines (cloud), the detector share often rises to 70%. On CPU, preprocessing and classifier batching eat more.

## Report

PHCB0

## Rules

- Never recommend dropping schema validation from the production path; propose moving it to the boundary instead.
- If preprocessing misses its budget, always try Pillow-SIMD or NVJPEG before changing the model.
- If the detector miss is more than 30% of target, switch models instead of optimising the current one.
- Flag the gate as PHIC5 when current_ms > 1.1 * cel_ms; zaznacz `ok`, jeśli mieści się w 10% budżetu.