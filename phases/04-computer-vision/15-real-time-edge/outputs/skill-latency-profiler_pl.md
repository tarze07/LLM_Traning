---

name: skill-latency-profiler
description: Napisz kompletny skrypt do porównywania opóźnień z rozgrzewką, synchronizacją, percentylami i śledzeniem pamięci
version: 1.0.0
phase: 4
lesson: 15
tags: [edge, deployment, profiling, benchmarking]

---

# Profiler opóźnień

Stwórz zdyscyplinowany test porównawczy opóźnień dla dowolnego modelu PyTorch. Raporty, którym może zaufać każdy, kto znajduje się na niższym szczeblu łańcucha dostaw.

## Kiedy używać

- Porównanie wielu kandydatów na szkielety przed wybraniem jednego do wdrożenia.
- Przed i po kwantyzacji lub przycinaniu.
- Po zmianie środowiska wykonawczego (eager vs ONNX vs TensorRT).
- Generowanie raportu gotowości do wdrożenia.

## Wejścia

- `model`: PyTorch `nn.Module`.
- `input_shape`: krotka jak `(1, 3, 224, 224)`.
- `device`: `cpu` | `cuda` | `mps`.
- `warmup`: domyślnie 10.
- `iters`: domyślnie 100.

## Kontrole

### 1. Rozgrzewka
Uruchom model `warmup` razy bez pomiaru czasu. Przechwytuje kompilację JIT z pierwszym przesłaniem i efekty zimnej pamięci podręcznej.

### 2. Synchronizacja
W przypadku `cuda` zadzwoń pod numer `torch.cuda.synchronize()` przed i po każdym określonym czasowo podaniu do przodu.
W przypadku `mps` zadzwoń pod numer `torch.mps.synchronize()`.

### 3. Minutnik
Do pomiaru zegara ściennego użyj `time.perf_counter()`. Zamień na milisekundy.

### 4. Percentyle
Sortuj pełną listę czasów. Zgłoś `p50, p90, p95, p99, mean, std`.

### 5. Pamięć
W przypadku `cuda` zadzwoń do `torch.cuda.max_memory_allocated()` po przebiegu i odejmij dowolną linię bazową.
W przypadku `cpu` użyj `tracemalloc` lub `psutil.Process().memory_info().rss` przed i po.

### 6. Przegląd wielkości partii
Opcjonalnie powtórz test porównawczy dla `batch_size in [1, 4, 16, 32]`, aby wykazać kompromis w zakresie przepustowości i opóźnień.

## Szablon wyjściowy

```python
import time
import torch
import psutil, os

def profile(model, input_shape, device="cpu", warmup=10, iters=100):
    proc = psutil.Process(os.getpid())
    baseline_rss = proc.memory_info().rss / 1e6

    model = model.to(device).eval()
    x = torch.randn(input_shape, device=device)

    def sync():
        if device == "cuda":
            torch.cuda.synchronize()
        elif device == "mps":
            torch.mps.synchronize()

    with torch.no_grad():
        for _ in range(warmup):
            model(x)
        sync()
        if device == "cuda":
            torch.cuda.reset_peak_memory_stats()

        times = []
        for _ in range(iters):
            sync()
            t0 = time.perf_counter()
            model(x)
            sync()
            times.append((time.perf_counter() - t0) * 1000)

    times.sort()
    mean = sum(times) / len(times)
    std  = (sum((t - mean) ** 2 for t in times) / len(times)) ** 0.5

    def pct(p):
        idx = max(0, min(len(times) - 1, int(len(times) * p) - 1))
        return times[idx]

    report = {
        "p50_ms":  pct(0.50),
        "p90_ms":  pct(0.90),
        "p95_ms":  pct(0.95),
        "p99_ms":  pct(0.99),
        "mean_ms": mean,
        "std_ms":  std,
        "rss_mb":  proc.memory_info().rss / 1e6 - baseline_rss,
    }
    if device == "cuda":
        report["peak_cuda_mb"] = torch.cuda.max_memory_allocated() / 1e6

    return report
```

## Zasady

- Zawsze prowadź rozgrzewkę; nigdy nie ufaj wyczuciu czasu pierwszego do przodu.
- Percentyle, nie średnia — pojedyncza wartość odstająca może podwoić średnią, ale ledwo przesuwa p50.
- Użyj tego samego input_shape co produkcja; opóźnienie na 224x224 nie jest opóźnieniem na 384x384.
- W przypadku CUDA nigdy nie pomijaj `torch.cuda.synchronize()`; bez tego liczby nie mają żadnego znaczenia.
- Zapisz wersję palnika, wersję CUDA i nazwę urządzenia wraz z liczbami — w przeciwnym razie przestają być porównywalne.