---

name: skill-linear-probe-runner
description: Napisz pełną ocenę sondy liniowej dla dowolnego zamrożonego kodera i oznaczonego zestawu danych
version: 1.0.0
phase: 4
lesson: 17
tags: [self-supervised, evaluation, linear-probe, pytorch]

---

# Liniowy prowadnica sondy

Oceń funkcje zamrożonego kodera, trenując pojedynczy klasyfikator liniowy na górze. Standardowa ocena każdej pracy samonadzorowanej.

## Kiedy używać

- Porównywanie samonadzorowanych punktów kontrolnych.
- Jakość funkcji śledzenia w okresach przedtreningowych.
- Podejmowanie decyzji, czy wstępnie wytrenowany koder jest wystarczająco dobry do wykonania kolejnego zadania bez dostrajania.

## Wejścia

- `encoder`: zamrożony `nn.Module` zwracający funkcję stałego przyciemnienia na obraz.
- `feature_dim`: wymiarowość wyjścia enkodera.
- `train_dataset`: oznaczony zbiór danych (obraz, class_id).
- `val_dataset`: zestaw wyciągnięty.
- `num_classes`: zajęcia zadaniowe.
- `epochs`: zazwyczaj 100 dla skali ImageNet, 50 dla mniejszych zbiorów danych.

## Kroki

1. Ustaw enkoder w tryb eval i `requires_grad=False` dla każdego parametru.
2. Wyodrębnij jednokrotnie zarówno zestawy pociągowe, jak i val. Przechowuj jako tablice numpy lub plik mapowany w pamięci.
3. Trenuj `nn.Linear(feature_dim, num_classes)` w zakresie funkcji buforowanych za pomocą harmonogramu SGD + cosinus.
4. Standardowe hiperparametry: `lr=0.1`, `momentum=0.9`, `weight_decay=0`, `batch_size=1024`. Sonda liniowa jest zaskakująco wrażliwa na `lr` — przemiataj, jeśli dokładność jest słaba.
5. Na koniec treningu zgłoś najwyższą dokładność wartości val.

## Szablon wyjściowy

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

## Zgłoś

```
[linear probe]
  encoder:     <name + pretrain checkpoint>
  feature_dim: <int>
  epochs:      <int>
  best_val_top1: <float>
```

## Zasady

- Nigdy nie aktualizuj masy enkodera podczas sondy liniowej; byłoby to dostrojenie, a nie badanie.
- Wstępnie oblicz funkcje raz; ponowne uczenie kodera w każdej epoce marnuje 100 razy moc obliczeniową.
- Użyj SGD z harmonogramem cosinus i bez utraty wagi; Adam czasami osiąga tutaj słabsze wyniki.
- Przemiataj współczynniki uczenia się co najmniej raz na rodzinę koderów; wartość optymalna różni się w zależności od metody SSL.