# Konfiguracja GPU i chmura

> Trening na CPU jest w porządku do nauki. Trening "na poważnie" wymaga GPU.

**Typ:** Build
**Języki:** Python
**Wymagania wstępne:** Faza 0, Lekcja 01
**Czas:** ~45 minut

## Cele nauki

- Sprawdzenie dostępności lokalnego GPU za pomocą `nvidia-smi` oraz CUDA API w PyTorch
- Konfiguracja Google Colab z GPU T4 do darmowych eksperymentów w chmurze
- Benchmark mnożenia macierzy na CPU vs GPU oraz pomiar przyspieszenia
- Oszacowanie największego modelu, jaki zmieści się w Twoim VRAM, z wykorzystaniem reguły kciuka dla fp16

## Problem

Większość lekcji w fazach 1-3 działa dobrze na CPU. Ale gdy zaczniesz trenować sieci CNN, transformery lub LLM-y (fazy 4+), będziesz potrzebować akceleracji GPU. Trening, który na CPU zajmuje 8 godzin, na GPU zajmuje 10 minut.

Masz trzy opcje: lokalne GPU, GPU w chmurze lub Google Colab (darmowy).

## Koncepcja

```
Twoje opcje:

1. Lokalne GPU NVIDIA
   Koszt: 0 USD (już je masz)
   Konfiguracja: instalacja CUDA + cuDNN
   Najlepsze dla: regularnego użytku, dużych zbiorów danych

2. Google Colab (darmowy plan)
   Koszt: 0 USD
   Konfiguracja: brak
   Najlepsze dla: szybkich eksperymentów, braku GPU w domu

3. GPU w chmurze (Lambda, RunPod, Vast.ai)
   Koszt: 0,20-2,00 USD/h
   Konfiguracja: SSH + instalacja
   Najlepsze dla: poważnego treningu, dużych modeli
```

## Zbuduj to

### Opcja 1: Lokalne GPU NVIDIA

Sprawdź, czy je posiadasz:

```bash
nvidia-smi
```

Zainstaluj PyTorch z CUDA:

```python
import torch

print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA version: {torch.version.cuda}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
```

### Opcja 2: Google Colab

1. Wejdź na [colab.research.google.com](https://colab.research.google.com)
2. Runtime > Change runtime type > T4 GPU
3. Uruchom `!nvidia-smi`, aby zweryfikować

Wgrywaj notebooki z tego kursu bezpośrednio do Colab.

### Opcja 3: GPU w chmurze

Dla Lambda Labs, RunPod lub Vast.ai:

```bash
ssh user@your-gpu-instance

pip install torch torchvision torchaudio
python -c "import torch; print(torch.cuda.get_device_name(0))"
```

### Brak GPU? Żaden problem.

Większość lekcji działa na CPU. Te, które wymagają GPU, będą to wyraźnie zaznaczać i zawierać linki do Colab.

```python
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using: {device}")
```

## Zbuduj to: benchmark GPU vs CPU

```python
import torch
import time

size = 5000

a_cpu = torch.randn(size, size)
b_cpu = torch.randn(size, size)

start = time.time()
c_cpu = a_cpu @ b_cpu
cpu_time = time.time() - start
print(f"CPU: {cpu_time:.3f}s")

if torch.cuda.is_available():
    a_gpu = a_cpu.to("cuda")
    b_gpu = b_cpu.to("cuda")

    torch.cuda.synchronize()
    start = time.time()
    c_gpu = a_gpu @ b_gpu
    torch.cuda.synchronize()
    gpu_time = time.time() - start
    print(f"GPU: {gpu_time:.3f}s")
    print(f"Speedup: {cpu_time / gpu_time:.0f}x")
```

## Ćwiczenia

1. Uruchom powyższy benchmark i porównaj czasy CPU vs GPU
2. Jeśli nie masz GPU, uruchom go na Google Colab i porównaj wyniki
3. Sprawdź, ile pamięci GPU posiadasz, i oszacuj największy model, jaki możesz w niej zmieścić (reguła kciuka: 2 bajty na parametr dla fp16)

## Kluczowe pojęcia

| Pojęcie | Co się o nim mówi | Co naprawdę oznacza |
|------|----------------|----------------------|
| CUDA | "programowanie GPU" | Platforma firmy NVIDIA do obliczeń równoległych, pozwalająca uruchamiać kod na GPU |
| VRAM | "pamięć GPU" | Pamięć wideo na karcie graficznej, oddzielna od pamięci RAM systemu. Ogranicza rozmiar modelu. |
| fp16 | "połowiczna precyzja" | 16-bitowa liczba zmiennoprzecinkowa, zużywa połowę pamięci fp32 przy minimalnej utracie dokładności |
| Tensor Core | "szybki sprzęt do macierzy" | Wyspecjalizowane rdzenie GPU do mnożenia macierzy, 4-8x szybsze niż zwykłe rdzenie |
