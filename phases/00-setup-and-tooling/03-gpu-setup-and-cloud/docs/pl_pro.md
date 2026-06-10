# Konfiguracja GPU i chmura

> Trenowanie modeli na procesorze (CPU) to dobry sposób na naukę. Prawdziwe trenowanie wymaga jednak karty graficznej (GPU).

**Typ:** Konfiguracja (Build)
**Języki:** Python
**Wymagania:** Faza 0, Lekcja 01
**Czas:** ~45 minut

## Cele nauczania

- Sprawdzisz dostępność lokalnego GPU za pomocą `nvidia-smi` oraz API CUDA w bibliotece PyTorch.
- Skonfigurujesz Google Colab z akceleratorem GPU T4, aby móc przeprowadzać darmowe eksperymenty w chmurze.
- Porównasz czas mnożenia macierzy na CPU i GPU oraz zmierzysz przyspieszenie.
- Oszacujesz, jak duży model zmieści się w Twojej pamięci VRAM, korzystając z praktycznej reguły dla precyzji fp16.

## Problem

Większość lekcji w fazach 1-3 działa bez problemu na samym procesorze (CPU). Kiedy jednak zaczniesz trenować sieci konwolucyjne (CNN), transformery czy duże modele językowe (LLM) w fazach 4 i późniejszych, będziesz potrzebować akceleracji GPU. Trenowanie, które na CPU trwa 8 godzin, na GPU może zająć 10 minut.

Masz trzy opcje: lokalne GPU, GPU w chmurze lub Google Colab (darmowe).

## Koncepcja

```
Twoje opcje:

1. Lokalne GPU NVIDIA
   Koszt: 0 zł (już je masz)
   Konfiguracja: Instalacja CUDA + cuDNN
   Najlepsze do: Regularnej pracy, dużych zbiorów danych

2. Google Colab (darmowy plan)
   Koszt: 0 zł
   Konfiguracja: Brak
   Najlepsze do: Szybkich eksperymentów, braku mocnego GPU w domu

3. GPU w chmurze (Lambda, RunPod, Vast.ai)
   Koszt: 0.20-2.00 USD/godz.
   Konfiguracja: SSH + instalacja środowiska
   Najlepsze do: Poważnego trenowania modeli, dużych modeli (LLM)
```

## Konfiguracja (Zbuduj to)

### Opcja 1: Lokalne GPU NVIDIA

Sprawdź, czy karta jest dostępna:

```bash
nvidia-smi
```

Sprawdź instalację PyTorch z obsługą CUDA:

```python
import torch

print(f"Dostępność CUDA: {torch.cuda.is_available()}")
print(f"Wersja CUDA: {torch.version.cuda}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"Pamięć: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
```

### Opcja 2: Google Colab

1. Wejdź na [colab.research.google.com](https://colab.research.google.com).
2. Wybierz *Środowisko wykonawcze* > *Zmień typ środowiska wykonawczego* > wybierz *GPU T4*.
3. Uruchom w komórce `!nvidia-smi`, aby sprawdzić przypisane GPU.

Możesz przesyłać notebooki z tego kursu bezpośrednio do środowiska Colab.

### Opcja 3: GPU w chmurze

Jeśli korzystasz z Lambda Labs, RunPod lub Vast.ai:

```bash
ssh user@twoja-instancja-gpu

pip install torch torchvision torchaudio
python -c "import torch; print(torch.cuda.get_device_name(0))"
```

### Brak GPU? To nie problem.

Większość wprowadzających lekcji działa bez problemu na CPU. W lekcjach wymagających GPU zostanie to wyraźnie zaznaczone i dołączymy linki do gotowych notatników Colab.

```python
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Używane urządzenie: {device}")
```

## Praktyka (Zbuduj to): Test porównawczy CPU vs GPU

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
    print(f"Przyspieszenie: {cpu_time / gpu_time:.0f}x")
```

## Ćwiczenia

1. Uruchom powyższy test porównawczy i zestaw wyniki czasu dla CPU oraz GPU.
2. Jeśli nie masz własnego GPU, uruchom test w Google Colab i sprawdź wynik.
3. Sprawdź, ile posiadasz pamięci VRAM na GPU i oszacuj, jaki największy model się w niej zmieści (praktyczna zasada: 2 bajty pamięci na każdy parametr modelu dla formatu fp16).

## Kluczowe pojęcia

| Termin | Potoczne określenie | Rzeczywiste znaczenie |
|------|----------------|----------------------|
| CUDA | „Programowanie GPU” | Platforma obliczeń równoległych od NVIDII, która umożliwia uruchamianie kodu (np. w Pythonie) bezpośrednio na GPU. |
| VRAM | „Pamięć GPU” | Pamięć wideo dedykowana układowi GPU, niezależna od systemowej pamięci RAM. Jej ilość ogranicza maksymalny rozmiar wczytywanego modelu. |
| fp16 | „Półprecyzja” | Format zmiennoprzecinkowy 16-bitowy. Zużywa o połowę mniej pamięci niż fp32 przy niemal niezauważalnej utracie dokładności. |
| Tensor Core | „Sprzęt do szybkiej matematyki” | Wyspecjalizowane rdzenie w nowszych GPU NVIDII służące wyłącznie do przyspieszania operacji mnożenia macierzy, działające 4-8x szybciej niż standardowe rdzenie CUDA. |
