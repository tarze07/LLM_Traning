---

name: distributed-fsdp-ddp
description: Przeprowadź szkolenie wielopoziomowe za pomocą od podstaw opakowania DDP i szkicu fragmentowania parametrów FSDP na zapleczu gloo lub nccl.
version: 1.0.0
phase: 19
lesson: 48
tags: [distributed, ddp, fsdp, collectives]

---

## Kiedy używać

Model mieści się na jednym urządzeniu, ale wymagana jest większa przepustowość (DDP). Model nie mieści się na jednym urządzeniu (FSDP). W obu przypadkach: wielopoziomowa konfiguracja szkoleniowa z tą samą ścieżką kodu.

## Wyświetl grupę procesów

```python
os.environ["MASTER_ADDR"] = "127.0.0.1"
os.environ["MASTER_PORT"] = str(port)
dist.init_process_group(backend="gloo", rank=rank, world_size=world_size)
```

`gloo` to backend procesora; `nccl` to backend GPU. Obydwa realizują tę samą wspólną powierzchnię.

## Owiń model

1. Na poziomie 0 zbuduj model ze swoich nasion.
2. Owiń go powłoką DDP.
3. `__init__` powłoki wywołuje `dist.broadcast(p.data, src=0)` dla każdego parametru i bufora.
4. Po każdym `loss.backward()` trener wywołuje `sync_grads()`.
5. `sync_grads()` wywołuje `dist.all_reduce(p.grad, op=SUM)` i `p.grad.div_(world_size)`.
6. Krok optymalizatora na każdym poziomie z tym samym uśrednionym gradientem.

## Parametry fragmentu (szkic FSDP)

1. Spłaszcz każdy parametr, uzupełnij do wielokrotności `world_size`.
2. Trzymaj swój odłamek lokalnie; wypuść resztę.
3. Przed przejściem dalej `dist.all_gather(...)` odbuduje pełny tensor na każdej rangi.
4. Po przesłaniu dalej opuść pełny tensor.

## Tryby awarii

- Pomijanie transmisji: rangi zaczynają się od różnych początków, rozchodzą się po cichu.
- Zapominanie o dzieleniu po sumie: gradienty skalowane według rozmiaru_świata, kroki optymalizatora są za duże.
- Używanie zmiany nazwy punktów kontrolnych na różnych urządzeniach: nie jest atomowa; ta sama lekcja 47 pułapka.
- Mieszanie tensorów procesora i CUDA w tym samym zbiorze: niedopasowanie backendu, zawieszanie się działania.