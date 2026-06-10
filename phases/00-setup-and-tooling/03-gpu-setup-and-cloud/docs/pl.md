# Konfiguracja GPU i chmura

> Szkolenie na temat procesora jest dobrym sposobem na naukę. Trening na realne potrzeby GPU.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania:** Faza 0, Lekcja 01
**Czas:** ~45 minut

## Cele nauczania

- Sprawdź dostępność lokalnego procesora graficznego za pomocą `nvidia-smi` i interfejsu API CUDA PyTorch
- Skonfiguruj Google Colab z procesorem graficznym T4, aby móc przeprowadzać bezpłatne eksperymenty w chmurze
- Porównaj mnożenie macierzy na CPU vs GPU i zmierz przyspieszenie
- Oszacuj największy model, który zmieści się w Twojej pamięci VRAM, korzystając z praktycznej reguły fp16

## Problem

Większość lekcji w fazach 1-3 działa poprawnie na procesorze. Ale gdy zaczniesz trenować CNN, transformatory lub LLM (fazy 4 i nowsze), potrzebujesz akceleracji GPU. Trening, który zajmuje 8 godzin na procesorze, zajmuje 10 minut na GPU.

Masz trzy opcje: lokalny procesor graficzny, procesor graficzny w chmurze lub Google Colab (bezpłatny).

## Koncepcja

```
Your options:

1. Local NVIDIA GPU
   Cost: $0 (you already have it)
   Setup: Install CUDA + cuDNN
   Best for: Regular use, large datasets

2. Google Colab (free tier)
   Cost: $0
   Setup: None
   Best for: Quick experiments, no GPU at home

3. Cloud GPU (Lambda, RunPod, Vast.ai)
   Cost: $0.20-2.00/hr
   Setup: SSH + install
   Best for: Serious training, large models
```

## Zbuduj to

### Opcja 1: Lokalny procesor graficzny NVIDIA

Sprawdź, czy masz:

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

1. Przejdź do [colab.research.google.com](https://colab.research.google.com)
2. Środowisko wykonawcze > Zmień typ środowiska wykonawczego > GPU T4
3. Uruchom `!nvidia-smi`, aby sprawdzić

Prześlij notatki z tego kursu bezpośrednio do Colab.

### Opcja 3: GPU w chmurze

W przypadku Lambda Labs, RunPod lub Vast.ai:

```bash
ssh user@your-gpu-instance

pip install torch torchvision torchaudio
python -c "import torch; print(torch.cuda.get_device_name(0))"
```

### Brak procesora graficznego? Bez problemu.

Większość lekcji działa na procesorze. Ci, którzy potrzebują GPU, powiedzą to i dołączą linki Colab.

```python
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using: {device}")
```

## Build It: test porównawczy procesora graficznego i procesora

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

1. Uruchom powyższy test porównawczy i porównaj czasy procesora i karty graficznej
2. Jeśli nie masz procesora graficznego, uruchom go w Google Colab i porównaj
3. Sprawdź ile masz pamięci GPU i oszacuj jaki największy model możesz zmieścić (praktyczna zasada: 2 bajty na parametr dla fp16)

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|----------------------|
| CUDA | „Programowanie GPU” | Platforma obliczeń równoległych firmy NVIDIA, która umożliwia uruchamianie kodu na procesorze graficznym |
| VRAM | „Pamięć GPU” | Pamięć RAM wideo na GPU, oddzielna od systemowej pamięci RAM. Ogranicza rozmiar modelu. |
| fp16 | „Półprecyzja” | 16-bitowy zmiennoprzecinkowy, wykorzystuje połowę pamięci fp32 przy minimalnej utracie dokładności |
| Rdzeń Tensora | „Sprzęt szybkiej matrycy” | Wyspecjalizowane rdzenie GPU do mnożenia macierzy, 4-8x szybsze niż zwykłe rdzenie |