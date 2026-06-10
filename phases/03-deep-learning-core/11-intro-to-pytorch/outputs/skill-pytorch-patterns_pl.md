---

name: skill-pytorch-patterns
description: Wzorce referencyjne dotyczące szkolenia, oceny i wdrażania PyTorch
version: 1.0.0
phase: 03
lesson: 11
tags: [pytorch, training, deep-learning, gpu, patterns]

---

## Kanoniczna pętla treningowa

```python
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = Model().to(device)
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=0.01)

for epoch in range(num_epochs):
    model.train()
    for inputs, targets in train_loader:
        inputs, targets = inputs.to(device), targets.to(device)
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, targets)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()

    model.eval()
    with torch.no_grad():
        for inputs, targets in val_loader:
            inputs, targets = inputs.to(device), targets.to(device)
            outputs = model(inputs)
```

## Mieszany trening precyzyjny

```python
from torch.amp import autocast, GradScaler

scaler = GradScaler()
for inputs, targets in train_loader:
    inputs, targets = inputs.to(device), targets.to(device)
    optimizer.zero_grad()
    with autocast(device_type="cuda"):
        outputs = model(inputs)
        loss = criterion(outputs, targets)
    scaler.scale(loss).backward()
    scaler.step(optimizer)
    scaler.update()
```

Użyj podczas: szkolenia na GPU ze sprzętem obsługującym float16 (V100, A100, H100, RTX 3090+). Spodziewaj się ~1,5-2x przyspieszenia i ~50% redukcji pamięci.

## Akumulacja gradientu

```python
accumulation_steps = 4
optimizer.zero_grad()
for i, (inputs, targets) in enumerate(train_loader):
    inputs, targets = inputs.to(device), targets.to(device)
    outputs = model(inputs)
    loss = criterion(outputs, targets) / accumulation_steps
    loss.backward()
    if (i + 1) % accumulation_steps == 0:
        optimizer.step()
        optimizer.zero_grad()
```

Użyj, gdy: efektywny rozmiar wsadu musi być większy niż pozwala na to pamięć GPU. Dzielenie straty przez akumulację_kroków pozwala zachować spójność skali gradientu.

## Zapisz i załaduj

```python
torch.save({
    "epoch": epoch,
    "model_state_dict": model.state_dict(),
    "optimizer_state_dict": optimizer.state_dict(),
    "loss": loss.item(),
}, "checkpoint.pt")

checkpoint = torch.load("checkpoint.pt", weights_only=True)
model.load_state_dict(checkpoint["model_state_dict"])
optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
```

Zawsze zapisuj stan optymalizatora, aby móc wznowić szkolenie. Tylko do celów wnioskowania zapisz tylko `model.state_dict()`.

## Niestandardowy zbiór danych

```python
class CustomDataset(torch.utils.data.Dataset):
    def __init__(self, data_dir, transform=None):
        self.samples = self._load_samples(data_dir)
        self.transform = transform

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        x, y = self.samples[idx]
        if self.transform:
            x = self.transform(x)
        return x, y

    def _load_samples(self, data_dir):
        ...
```

## Konfiguracja modułu DataLoader

```python
train_loader = torch.utils.data.DataLoader(
    dataset,
    batch_size=64,
    shuffle=True,
    num_workers=4,
    pin_memory=True,
    drop_last=True,
    persistent_workers=True,
)
```

| Parametr | Co to robi | Kiedy używać |
|----------|------------|------------|
| liczba_pracowników=4 | Równoległe ładowanie danych | Zawsze na maszynach wielordzeniowych |
| pin_memory=Prawda | Pamięć procesora z blokadą strony | Podczas treningu na GPU |
| drop_last=Prawda | Upuść niekompletną ostatnią partię | Podczas korzystania z BatchNorm |
| trwałe_pracownicy=Prawda | Utrzymuj pracowników przy życiu w różnych epokach | Gdy liczba_pracowników > 0 |

## Harmonogramy szybkości uczenia się

```python
scheduler = torch.optim.lr_scheduler.OneCycleLR(
    optimizer,
    max_lr=1e-3,
    total_steps=num_epochs * len(train_loader),
    pct_start=0.1,
)

for epoch in range(num_epochs):
    for inputs, targets in train_loader:
        ...
        optimizer.step()
        scheduler.step()
```

OneCycleLR: najlepsze ustawienie domyślne dla większości zadań. Rozgrzewa się do max_lr, następnie zanika cosinus. Wywołaj `scheduler.step()` po każdej partii, a nie po każdej epoce.

## Inicjalizacja wagi

```python
def init_weights(module):
    if isinstance(module, nn.Linear):
        nn.init.kaiming_normal_(module.weight, nonlinearity="relu")
        if module.bias is not None:
            nn.init.zeros_(module.bias)
    elif isinstance(module, nn.Conv2d):
        nn.init.kaiming_normal_(module.weight, mode="fan_out", nonlinearity="relu")

model.apply(init_weights)
```

## Tryb wnioskowania

```python
model.eval()

with torch.inference_mode():
    outputs = model(inputs)
```

`torch.inference_mode()` jest szybszy niż `torch.no_grad()`, ponieważ całkowicie wyłącza autograd, a nie tylko tłumi obliczenia gradientu.

## Lista kontrolna typowych błędów

1. Zastosowanie softmax przed CrossEntropyLoss (zawiera wewnętrznie log_softmax)
2. Zapomnienie wywołania model.eval() podczas sprawdzania poprawności
3. Zapominanie o przeniesieniu tensorów do tego samego urządzenia, co model
4. Nie wywoływanie Optimizer.zero_grad() (domyślnie akumulują się gradienty)
5. Używanie torch.no_grad() podczas treningu (wyłącza obliczanie gradientu)
6. Ustawienie zbyt dużej wartości num_workers (spawnuje zbyt wiele procesów, zaśmieca pamięć)
7. Nieużywanie pin_memory=True podczas treningu na GPU
8. Zapisanie całego obiektu modelu zamiast state_dict (przerwanie refaktora)