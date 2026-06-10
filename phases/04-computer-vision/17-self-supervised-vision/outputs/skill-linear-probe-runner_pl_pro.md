---

name: skill-linear-probe-runner
description: Uruchom ewaluację za pomocą sondy liniowej (linear probe) dla zamrożonego enkodera na oznaczonym zbiorze danych
version: 1.0.0
phase: 4
lesson: 17
tags: [self-supervised, evaluation, linear-probe, pytorch]

---

# Ewaluacja metodą sondy liniowej (Linear Probe Runner)

Oceń jakość reprezentacji (cech) generowanych przez zamrożony enkoder, trenując na nich pojedynczy klasyfikator liniowy. Jest to standardowa metoda ewaluacji modeli szkolonych samonadzorowanie.

## Kiedy stosować

- Porównywanie różnych punktów kontrolnych (checkpoints) modeli samonadzorowanych.
- Monitorowanie jakości cech w trakcie uczenia wstępnego (pre-training).
- Podejmowanie decyzji, czy wstępnie wytrenowany enkoder generuje wystarczająco dobre cechy dla zadania docelowego bez potrzeby pełnego dostrajania (fine-tuning).

## Dane wejściowe

- `encoder`: zamrożony model `nn.Module` zwracający wektor cech o stałej wymiarowości dla każdego obrazu.
- `feature_dim`: wymiarowość wektora cech na wyjściu enkodera.
- `train_dataset`: oznakowany zbiór treningowy zawierający pary (obraz, class_id).
- `val_dataset`: wydzielony zbiór walidacyjny.
- `num_classes`: liczba klas w zadaniu docelowym.
- `epochs`: zazwyczaj 100 dla dużych zbiorów typu ImageNet, 50 dla mniejszych zbiorów danych.

## Procedura krok po kroku

1. Przełącz enkoder w tryb ewaluacji (`encoder.eval()`) i ustaw `requires_grad=False` dla wszystkich jego parametrów.
2. Wyodrębnij wektory cech jednorazowo dla całego zbioru treningowego i walidacyjnego. Zapisz je w pamięci RAM (np. jako tensory PyTorch lub tablice NumPy) albo w plikach mapowanych w pamięci (memmap).
3. Trenuj warstwę liniową `nn.Linear(feature_dim, num_classes)` na zapamiętanych wektorach cech, używając optymalizatora SGD z harmonogramem cosinusowym (Cosine Annealing).
4. Standardowe hiperparametry: `lr=0.1`, `momentum=0.9`, `weight_decay=0`, `batch_size=1024`. Sonda liniowa bywa bardzo wrażliwa na współczynnik uczenia się (`lr`) — przeprowadź przeszukiwanie (sweep) tej wartości, jeśli wyniki są niesatysfakcjonujące.
5. Po zakończeniu treningu zaraportuj najwyższą uzyskaną dokładność na zbiorze walidacyjnym.

## Kod szablonu

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torch.optim import SGD
from torch.optim.lr_scheduler import CosineAnnealingLR

def extract(encoder, loader, device="cpu"):
    encoder.eval()
    feats, labels = [], []
    with torch.no_grad():
        for x, y in loader:
            f = encoder(x.to(device)).cpu()
            feats.append(f)
            labels.append(y)
    return torch.cat(feats), torch.cat(labels)


def linear_probe(encoder, feature_dim, train_loader, val_loader,
                 num_classes, epochs=50, lr=0.1, device="cpu"):
    for p in encoder.parameters():
        p.requires_grad = False

    f_train, y_train = extract(encoder, train_loader, device)
    f_val, y_val = extract(encoder, val_loader, device)

    head = nn.Linear(feature_dim, num_classes).to(device)
    opt = SGD(head.parameters(), lr=lr, momentum=0.9, weight_decay=0)
    sched = CosineAnnealingLR(opt, T_max=epochs)

    ds = torch.utils.data.TensorDataset(f_train, y_train)
    train_iter = DataLoader(ds, batch_size=1024, shuffle=True)

    best_val = 0.0
    for ep in range(epochs):
        head.train()
        for x, y in train_iter:
            x, y = x.to(device), y.to(device)
            loss = F.cross_entropy(head(x), y)
            opt.zero_grad(); loss.backward(); opt.step()
        sched.step()

        head.eval()
        with torch.no_grad():
            acc = (head(f_val.to(device)).argmax(-1).cpu() == y_val).float().mean().item()
        best_val = max(best_val, acc)
    return best_val
```

## Format raportu

```
[linear probe]
  encoder:     <name + pretrain checkpoint>
  feature_dim: <int>
  epochs:      <int>
  best_val_top1: <float>
```

## Zasady i ograniczenia

- Nigdy nie aktualizuj wag enkodera podczas ewaluacji sondą liniową; byłoby to dostrajanie (fine-tuning), a nie badanie właściwości cech (linear probing).
- Oblicz wektory cech jednorazowo przed rozpoczęciem pętli uczenia; przepuszczanie obrazów przez enkoder w każdej epoce marnuje zasoby obliczeniowe (trening trwałby około 100 razy dłużej).
- Używaj optymalizatora SGD z harmonogramem cosinusowym i bez regularyzacji L2 (weight decay); optymalizator Adam osiąga w tym scenariuszu gorsze rezultaty.
- Przetestuj różne wartości współczynnika uczenia się (learning rate) dla każdej rodziny enkoderów; optymalne parametry różnią się znacznie w zależności od zastosowanej metody SSL.
