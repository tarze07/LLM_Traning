---

name: skill-pipeline-budget-planner
description: Przypisz budżet czasowy do każdego etapu potoku na podstawie docelowych opóźnień i przepustowości, oraz wskaż etap, który jako pierwszy przekracza założony budżet
version: 1.0.0
phase: 4
lesson: 16
tags: [vision, pipeline, performance, deployment]

---

# Planowanie budżetu potoku (Pipeline Budget Planner)

Przekształć docelowe opóźnienie i przepustowość w szczegółowy budżet czasowy dla poszczególnych etapów, aby każdy członek zespołu znał swoje wartości docelowe.

## Kiedy stosować

- Przed wdrożeniem nowej usługi wizyjnej (Computer Vision), aby określić oczekiwania dla każdego etapu.
- Po przeprowadzeniu pierwszych testów wydajnościowych (benchmarków), w celu zidentyfikowania etapu najbardziej odbiegającego od budżetu.
- W przypadku zmiany umowy SLA i konieczności renegocjacji budżetu czasowego.

## Dane wejściowe

- `p95_latency_target_ms`: docelowe opóźnienie dla 95. percentyla (p95) na pojedyncze żądanie.
- `target_qps`: docelowa przepustowość (liczba zapytań na sekundę) dla pojedynczej repliki.
- `stages`: lista etapów w formacie `{ name: str, current_ms: float }`.

## Zasady alokacji budżetu

Domyślny podział budżetu na siedem standardowych etapów w przypadku braku rzeczywistych pomiarów:

| Etap | Udział |
|---|---|
| dekodowanie + przetwarzanie wstępne | 15% |
| przejście w przód detektora (detector forward) | 55% |
| postprocessing detekcji (NMS, ograniczenie wartości/clamp) | 5% |
| kadrowanie + zmiana rozmiaru pod klasyfikator | 5% |
| przejście w przód klasyfikatora (classifier forward) | 15% |
| walidacja schematu | <1% |
| serializacja odpowiedzi | 4% |

W potokach ograniczonych wydajnością GPU (w chmurze) udział detektora często wzrasta do 70%. Na procesorach (CPU) większą część budżetu pochłania przetwarzanie wstępne i tworzenie paczek (batching) dla klasyfikatora.

## Raport

PHCB0

## Zasady

- Nigdy nie zalecaj rezygnacji z walidacji schematu na ścieżce produkcyjnej; zamiast tego zaproponuj przeniesienie jej na granicę usługi (boundary).
- Jeśli etap przetwarzania wstępnego (preprocessing) nie mieści się w budżecie, przed podjęciem decyzji o zmianie modelu wypróbuj biblioteki takie jak Pillow-SIMD lub NVJPEG.
- Jeśli przekroczenie budżetu przez detektor wynosi ponad 30% wartości docelowej, rozważ zmianę architektury modelu zamiast optymalizacji obecnej wersji.
- Oznacz dany krok flagą `PHIC5`, gdy `current_ms > 1.1 * target_ms`; oznacz jako `ok`, jeśli mieści się w granicach 10% budżetu.
