---

name: skill-latency-profiler
description: Skrypt do dokładnego profilowania i pomiaru opóźnień (latency) w modelach PyTorch, z obsługą rozgrzewki, synchronizacji GPU oraz analizy percentyli
version: 1.0.0
phase: 4
lesson: 15
tags: [edge, deployment, profiling, benchmarking]

---

# Profiler wydajności i opóźnień (Latency Profiler)

Generuje precyzyjne i wiarygodne raporty wydajności (benchmarki) dla dowolnego modelu PyTorch, spełniające rygorystyczne wymagania testów wdrożeniowych.

## Zastosowanie

- Porównywanie wydajności wielu modeli bazowych (backbones) przed podjęciem decyzji o wdrożeniu.
- Profilowanie przed i po operacjach kwantyzacji lub przycinania wag (pruning).
- Porównywanie czasów wykonania w różnych środowiskach (tryb eager PyTorch vs ONNX Runtime vs TensorRT).
- Generowanie raportu gotowości wdrożeniowej (deployment readiness report).

## Dane wejściowe

- `model`: instancja modelu PyTorch (`nn.Module`).
- `input_shape`: krotka opisująca wymiary wejściowe (np. `(1, 3, 224, 224)`).
- `device`: środowisko wykonawcze: `cpu` | `cuda` | `mps`.
- `warmup`: liczba kroków rozgrzewki, domyślnie 10.
- `iters`: liczba mierzonych iteracji, domyślnie 100.

## Procedura pomiarowa

### 1. Rozgrzewka (Warmup)
Uruchomienie przejścia w przód (forward pass) `warmup` razy bez rejestrowania czasu. Pozwala to na wczytanie bibliotek i wykonanie pierwszej kompilacji (np. JIT) oraz rozgrzanie pamięci podręcznej (cache).

### 2. Synchronizacja (Synchronization)
Dla środowiska CUDA wywołaj `torch.cuda.synchronize()` przed oraz po każdej mierzonej iteracji.
Dla środowiska Apple Silicon (MPS) wywołaj `torch.mps.synchronize()`.

### 3. Precyzyjny zegar (Timer)
Do pomiaru czasu wykonania (wall-clock time) używaj wyłącznie `time.perf_counter()`. Wyniki przelicz na milisekundy.

### 4. Percentyle (Percentiles)
Sortowanie zgromadzonych czasów iteracji i wyznaczenie statystyk: percentyli `p50` (mediana), `p90`, `p95`, `p99`, a także średniej (`mean`) i odchylenia standardowego (`std`).

### 5. Monitorowanie zużycia pamięci (Memory tracking)
Dla CUDA wywołaj `torch.cuda.max_memory_allocated()` w celu zmierzenia szczytowej alokacji pamięci VRAM.
Dla CPU wyznacz zużycie pamięci operacyjnej (RAM) przed i po teście przy użyciu `tracemalloc` lub parametru `rss` z biblioteki `psutil`.

### 6. Profilowanie wpływu rozmiaru paczki (Batch size scaling)
Opcjonalne powtórzenie testów dla różnych rozmiarów paczek (np. `batch_size in [1, 4, 16, 32]`) w celu analizy relacji pomiędzy przepustowością (throughput) a opóźnieniem (latency).

## Szablon kodu (PyTorch)

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

## Reguły

- Zawsze przeprowadzaj fazę rozgrzewki; czas pierwszego przejścia w przód jest całkowicie niewiarygodny.
- Analizuj percentyle, a no (nie) tylko średnią arytmetyczną – pojedyncze zakłócenie systemu operacyjnego (wartość odstająca) może drastycznie zawyżyć średnią, nie wpływając na medianę (p50) czy p95.
- Pomiary wykonuj dla dokładnie takich samych wymiarów wejściowych (`input_shape`) jak w docelowym systemie produkcyjnym; profil wydajności dla $224 \times 224$ drastycznie różni się od $384 \times 384$.
- Przy profilowaniu na GPU (CUDA/MPS) nigdy nie pomijaj synchronizacji; brak wywołania synchronizacji sprawia, że wyniki pomiarów są bezużyteczne.
- Zawsze dołączaj wersję biblioteki PyTorch (`torch.__version__`), wersję CUDA oraz dokładną nazwę karty graficznej/procesora; bez tych informacji wyniki są nieporównywalne.
