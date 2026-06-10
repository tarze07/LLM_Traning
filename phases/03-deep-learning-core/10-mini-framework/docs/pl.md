# Zbuduj własną mini ramę

> Zbudowałeś neurony, warstwy, sieci, podpory, aktywacje, funkcje strat, optymalizatory, regularyzację, inicjalizację i harmonogramy LR. Wszystko jako osobne kawałki. Teraz połącz je razem w ramę. Nie PyTorch. Nie TensorFlow. Twój.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Wszystko z fazy 03 (lekcje 01-09)
**Czas:** ~120 minut

## Cele nauczania

- Zbuduj kompletną strukturę głębokiego uczenia się (~500 linii) z modułem, liniowym, ReLU, Sigmoid, Dropout, BatchNorm, sekwencyjnym, funkcjami utraty, optymalizatorami i DataLoader
- Wyjaśnij abstrakcję modułu (do przodu, do tyłu, parametry) i dlaczego konieczne jest przełączanie trybu pociągu/ewaluacji
- Połącz wszystkie komponenty w działającą pętlę treningową, która szkoli 4-warstwową sieć w zakresie klasyfikacji okręgów
- Zamapuj każdy komponent swojego frameworka na jego odpowiednik w PyTorch (nn.Module, nn.Sequential, optim.Adam, DataLoader)

## Problem

Masz dziesięć lekcji składających się z elementów rozproszonych w oddzielnych plikach. Tutaj zajęcia `Value`, pętla treningowa tam, inicjalizacja ciężaru w innym pliku, harmonogramy tempa nauki w jeszcze innym. Aby wytrenować sieć, kopiuj i wklejaj z pięciu różnych lekcji i ręcznie je połącz.

To właśnie rozwiązują frameworki. PyTorch udostępnia `nn.Module`, `nn.Sequential`, `optim.Adam`, `DataLoader` i wzorzec pętli treningowej, który je łączy. TensorFlow zapewnia `keras.Layer`, `keras.Sequential`, `keras.optimizers.Adam`. To nie są magia. Są to wzorce organizacyjne, które umożliwiają definiowanie, szkolenie i ocenę sieci bez konieczności ciągłego wymyślania instalacji wodociągowej.

Zamierzasz zbudować to samo w ~ 500 liniach Pythona. Nie, nie. Brak zależności zewnętrznych. Framework, który może zdefiniować dowolną sieć ze sprzężeniem zwrotnym, wyszkolić ją z SGD lub Adamem, wsadowo przetwarzać dane, stosować porzucanie i normalizację wsadową, korzystać z dowolnej aktywacji i planować szybkość uczenia się.

Kiedy skończysz, dokładnie zrozumiesz, co się stanie, gdy napiszesz `model = nn.Sequential(...)` w PyTorch. Zrozumiesz, dlaczego istnieją `model.train()` i `model.eval()`. Zrozumiesz, dlaczego `optimizer.zero_grad()` to osobne wywołanie. Zrozumiesz to wszystko, ponieważ to ty to wszystko zbudowałeś.

## Koncepcja

### Abstrakcja modułu

Każda warstwa w PyTorch dziedziczy z `nn.Module`. Moduł ma trzy obowiązki:

1. **forward()** -- oblicza wynik na podstawie danych wejściowych
2. **parameters()** -- zwróć wszystkie możliwe do wytrenowania ciężary
3. **backward()** -- oblicz gradienty (obsługiwane przez autograd w PyTorch, jawnie w naszym)

Warstwa liniowa jest modułem. Aktywacja ReLU jest modułem. Warstwa porzucona to moduł. Warstwa normalizacji wsadowej to moduł. Wszystkie mają ten sam interfejs.

### Kontener sekwencyjny

`nn.Sequential` łączy moduły. Przejście w przód: przepuszczenie danych przez moduł 1, następnie moduł 2, a następnie moduł 3. Przejście w tył: odwrócenie łańcucha. Sam kontener jest modułem — zawiera funkcje forward(), parametry() i backward(). Oto wzór złożony: sekwencja modułów sama w sobie jest modułem.

### Trening a tryb oceny

Rezygnacja losowo zeruje neurony podczas treningu, ale przepuszcza wszystko podczas oceny. Normalizacja wsadowa wykorzystuje statystyki wsadowe podczas uczenia, ale średnie bieżące podczas oceny. Metody `train()` i `eval()` przełączają to zachowanie. Każdy moduł ma flagę `training`.

### Optymalizator

Optymalizator aktualizuje parametry przy użyciu ich gradientów. SGD: `param -= lr * grad`. Adam: utrzymuje szacunki dynamiki i wariancji, a następnie aktualizuje. Optymalizator nie zna architektury sieci — widzi jedynie płaską listę parametrów i ich gradientów.

### Moduł ładowania danych

Dozowanie ma znaczenie z dwóch powodów. Po pierwsze, w przypadku dużych problemów nie można zmieścić całego zestawu danych w pamięci. Po drugie, opadanie gradientowe w małych wsadach zapewnia szum, który pomaga uniknąć lokalnych minimów. DataLoader dzieli dane na partie i opcjonalnie tasuje pomiędzy epokami.

### Architektura ramowa

```mermaid
graph TD
    subgraph "Modules"
        Linear["Linear<br/>W*x + b"]
        ReLU["ReLU<br/>max(0, x)"]
        Sigmoid["Sigmoid<br/>1/(1+e^-x)"]
        Dropout["Dropout<br/>random zero mask"]
        BatchNorm["BatchNorm<br/>normalize activations"]
    end

    subgraph "Containers"
        Sequential["Sequential<br/>chains modules"]
    end

    subgraph "Loss Functions"
        MSE["MSELoss<br/>(pred - target)^2"]
        BCE["BCELoss<br/>binary cross-entropy"]
    end

    subgraph "Optimizers"
        SGD["SGD<br/>param -= lr * grad"]
        Adam["Adam<br/>adaptive moments"]
    end

    subgraph "Data"
        DataLoader["DataLoader<br/>batching + shuffle"]
    end

    Sequential --> |"contains"| Linear
    Sequential --> |"contains"| ReLU
    Sequential --> |"forward/backward"| MSE
    SGD --> |"updates"| Sequential
    DataLoader --> |"feeds"| Sequential
```

### Pętla treningowa

```mermaid
sequenceDiagram
    participant DL as DataLoader
    participant M as Model
    participant L as Loss
    participant O as Optimizer

    loop Each Epoch
        DL->>M: batch of inputs
        M->>M: forward pass (layer by layer)
        M->>L: predictions
        L->>L: compute loss
        L->>M: backward pass (gradients)
        M->>O: parameters + gradients
        O->>M: updated parameters
        O->>O: zero gradients
    end
```

### Hierarchia modułów

```mermaid
classDiagram
    class Module {
        +forward(x)
        +backward(grad)
        +parameters()
        +train()
        +eval()
    }

    class Linear {
        -weights
        -biases
        +forward(x)
        +backward(grad)
    }

    class ReLU {
        +forward(x)
        +backward(grad)
    }

    class Sequential {
        -modules[]
        +forward(x)
        +backward(grad)
        +parameters()
    }

    Module <|-- Linear
    Module <|-- ReLU
    Module <|-- Sequential
    Sequential *-- Module
```

## Zbuduj to

### Krok 1: Klasa bazowa modułu

Abstrakcyjny interfejs implementowany przez każdą warstwę.

```python
class Module:
    def __init__(self):
        self.training = True

    def forward(self, x):
        raise NotImplementedError

    def backward(self, grad):
        raise NotImplementedError

    def parameters(self):
        return []

    def train(self):
        self.training = True

    def eval(self):
        self.training = False
```

### Krok 2: Warstwa liniowa

Podstawowy element konstrukcyjny. Przechowuje wagi i odchylenia, oblicza Wx + b do przodu i gradienty wagi/wejściowe do tyłu.

```python
import math
import random

class Linear(Module):
    def __init__(self, fan_in, fan_out):
        super().__init__()
        std = math.sqrt(2.0 / fan_in)
        self.weights = [[random.gauss(0, std) for _ in range(fan_in)] for _ in range(fan_out)]
        self.biases = [0.0] * fan_out
        self.weight_grads = [[0.0] * fan_in for _ in range(fan_out)]
        self.bias_grads = [0.0] * fan_out
        self.fan_in = fan_in
        self.fan_out = fan_out
        self.input = None

    def forward(self, x):
        self.input = x
        output = []
        for i in range(self.fan_out):
            val = self.biases[i]
            for j in range(self.fan_in):
                val += self.weights[i][j] * x[j]
            output.append(val)
        return output

    def backward(self, grad):
        input_grad = [0.0] * self.fan_in
        for i in range(self.fan_out):
            self.bias_grads[i] += grad[i]
            for j in range(self.fan_in):
                self.weight_grads[i][j] += grad[i] * self.input[j]
                input_grad[j] += grad[i] * self.weights[i][j]
        return input_grad

    def parameters(self):
        params = []
        for i in range(self.fan_out):
            for j in range(self.fan_in):
                params.append((self.weights, i, j, self.weight_grads))
            params.append((self.biases, i, None, self.bias_grads))
        return params
```

### Krok 3: Moduły aktywacyjne

ReLU, Sigmoid i Tanh jako moduły. Każdy buforuje to, czego potrzebuje do przejścia wstecz.

```python
class ReLU(Module):
    def __init__(self):
        super().__init__()
        self.mask = None

    def forward(self, x):
        self.mask = [1.0 if v > 0 else 0.0 for v in x]
        return [max(0.0, v) for v in x]

    def backward(self, grad):
        return [g * m for g, m in zip(grad, self.mask)]

class Sigmoid(Module):
    def __init__(self):
        super().__init__()
        self.output = None

    def forward(self, x):
        self.output = []
        for v in x:
            v = max(-500, min(500, v))
            self.output.append(1.0 / (1.0 + math.exp(-v)))
        return self.output

    def backward(self, grad):
        return [g * o * (1 - o) for g, o in zip(grad, self.output)]

class Tanh(Module):
    def __init__(self):
        super().__init__()
        self.output = None

    def forward(self, x):
        self.output = [math.tanh(v) for v in x]
        return self.output

    def backward(self, grad):
        return [g * (1 - o * o) for g, o in zip(grad, self.output)]
```

### Krok 4: Moduł rezygnacji

Losowo zeruje elementy podczas treningu. Skaluje pozostałe elementy o 1/(1-p), aby oczekiwane wartości pozostały takie same. Nie robi nic podczas eval.

```python
class Dropout(Module):
    def __init__(self, p=0.5):
        super().__init__()
        self.p = p
        self.mask = None

    def forward(self, x):
        if not self.training:
            return x
        self.mask = [0.0 if random.random() < self.p else 1.0 / (1 - self.p) for _ in x]
        return [v * m for v, m in zip(x, self.mask)]

    def backward(self, grad):
        if self.mask is None:
            return grad
        return [g * m for g, m in zip(grad, self.mask)]
```

### Krok 5: Moduł BatchNorm

Normalizuje aktywacje do średniej zerowej i wariancji jednostkowej na cechę w całej partii. Utrzymuje statystyki działania dla trybu eval.

```python
class BatchNorm(Module):
    def __init__(self, size, momentum=0.1, eps=1e-5):
        super().__init__()
        self.size = size
        self.gamma = [1.0] * size
        self.beta = [0.0] * size
        self.gamma_grads = [0.0] * size
        self.beta_grads = [0.0] * size
        self.running_mean = [0.0] * size
        self.running_var = [1.0] * size
        self.momentum = momentum
        self.eps = eps
        self.x_norm = None
        self.std_inv = None
        self.batch_input = None

    def forward_batch(self, batch):
        batch_size = len(batch)
        output_batch = []

        if self.training:
            mean = [0.0] * self.size
            for sample in batch:
                for j in range(self.size):
                    mean[j] += sample[j]
            mean = [m / batch_size for m in mean]

            var = [0.0] * self.size
            for sample in batch:
                for j in range(self.size):
                    var[j] += (sample[j] - mean[j]) ** 2
            var = [v / batch_size for v in var]

            self.std_inv = [1.0 / math.sqrt(v + self.eps) for v in var]

            self.x_norm = []
            self.batch_input = batch
            for sample in batch:
                normed = [(sample[j] - mean[j]) * self.std_inv[j] for j in range(self.size)]
                self.x_norm.append(normed)
                output = [self.gamma[j] * normed[j] + self.beta[j] for j in range(self.size)]
                output_batch.append(output)

            for j in range(self.size):
                self.running_mean[j] = (1 - self.momentum) * self.running_mean[j] + self.momentum * mean[j]
                self.running_var[j] = (1 - self.momentum) * self.running_var[j] + self.momentum * var[j]
        else:
            std_inv = [1.0 / math.sqrt(v + self.eps) for v in self.running_var]
            for sample in batch:
                normed = [(sample[j] - self.running_mean[j]) * std_inv[j] for j in range(self.size)]
                output = [self.gamma[j] * normed[j] + self.beta[j] for j in range(self.size)]
                output_batch.append(output)

        return output_batch

    def forward(self, x):
        result = self.forward_batch([x])
        return result[0]

    def backward(self, grad):
        if self.x_norm is None:
            return grad
        for j in range(self.size):
            self.gamma_grads[j] += self.x_norm[0][j] * grad[j]
            self.beta_grads[j] += grad[j]
        return [grad[j] * self.gamma[j] * self.std_inv[j] for j in range(self.size)]

    def parameters(self):
        params = []
        for j in range(self.size):
            params.append((self.gamma, j, None, self.gamma_grads))
            params.append((self.beta, j, None, self.beta_grads))
        return params
```

### Krok 6: Kontener sekwencyjny

Moduły łańcuchów. Do przodu idzie od lewej do prawej, do tyłu idzie od prawej do lewej.

```python
class Sequential(Module):
    def __init__(self, *modules):
        super().__init__()
        self.modules = list(modules)

    def forward(self, x):
        for module in self.modules:
            x = module.forward(x)
        return x

    def backward(self, grad):
        for module in reversed(self.modules):
            grad = module.backward(grad)
        return grad

    def parameters(self):
        params = []
        for module in self.modules:
            params.extend(module.parameters())
        return params

    def train(self):
        self.training = True
        for module in self.modules:
            module.train()

    def eval(self):
        self.training = False
        for module in self.modules:
            module.eval()
```

### Krok 7: Funkcje straty

MSE i binarna entropia krzyżowa. Każdy zwraca wartość straty i udostępnia funkcję backward(), która zwraca gradient.

```python
class MSELoss:
    def __call__(self, predicted, target):
        self.predicted = predicted
        self.target = target
        n = len(predicted)
        self.loss = sum((p - t) ** 2 for p, t in zip(predicted, target)) / n
        return self.loss

    def backward(self):
        n = len(self.predicted)
        return [2 * (p - t) / n for p, t in zip(self.predicted, self.target)]

class BCELoss:
    def __call__(self, predicted, target):
        self.predicted = predicted
        self.target = target
        eps = 1e-7
        n = len(predicted)
        self.loss = 0
        for p, t in zip(predicted, target):
            p = max(eps, min(1 - eps, p))
            self.loss += -(t * math.log(p) + (1 - t) * math.log(1 - p))
        self.loss /= n
        return self.loss

    def backward(self):
        eps = 1e-7
        n = len(self.predicted)
        grads = []
        for p, t in zip(self.predicted, self.target):
            p = max(eps, min(1 - eps, p))
            grads.append((-t / p + (1 - t) / (1 - p)) / n)
        return grads
```

### Krok 8: Optymalizatory SGD i Adama

Oba pobierają listę parametrów i aktualizują wagi za pomocą gradientów.

```python
class SGD:
    def __init__(self, parameters, lr=0.01):
        self.params = parameters
        self.lr = lr

    def step(self):
        for container, i, j, grad_container in self.params:
            if j is not None:
                container[i][j] -= self.lr * grad_container[i][j]
            else:
                container[i] -= self.lr * grad_container[i]

    def zero_grad(self):
        for container, i, j, grad_container in self.params:
            if j is not None:
                grad_container[i][j] = 0.0
            else:
                grad_container[i] = 0.0

class Adam:
    def __init__(self, parameters, lr=0.001, beta1=0.9, beta2=0.999, eps=1e-8):
        self.params = parameters
        self.lr = lr
        self.beta1 = beta1
        self.beta2 = beta2
        self.eps = eps
        self.t = 0
        self.m = [0.0] * len(parameters)
        self.v = [0.0] * len(parameters)

    def step(self):
        self.t += 1
        for idx, (container, i, j, grad_container) in enumerate(self.params):
            if j is not None:
                g = grad_container[i][j]
            else:
                g = grad_container[i]

            self.m[idx] = self.beta1 * self.m[idx] + (1 - self.beta1) * g
            self.v[idx] = self.beta2 * self.v[idx] + (1 - self.beta2) * g * g

            m_hat = self.m[idx] / (1 - self.beta1 ** self.t)
            v_hat = self.v[idx] / (1 - self.beta2 ** self.t)

            update = self.lr * m_hat / (math.sqrt(v_hat) + self.eps)

            if j is not None:
                container[i][j] -= update
            else:
                container[i] -= update

    def zero_grad(self):
        for container, i, j, grad_container in self.params:
            if j is not None:
                grad_container[i][j] = 0.0
            else:
                grad_container[i] = 0.0
```

### Krok 9: Moduł ładowania danych

Dzieli dane na partie, opcjonalnie tasuje każdą epokę.

```python
class DataLoader:
    def __init__(self, data, batch_size=32, shuffle=True):
        self.data = data
        self.batch_size = batch_size
        self.shuffle = shuffle

    def __iter__(self):
        indices = list(range(len(self.data)))
        if self.shuffle:
            random.shuffle(indices)
        for start in range(0, len(indices), self.batch_size):
            batch_indices = indices[start:start + self.batch_size]
            batch = [self.data[i] for i in batch_indices]
            inputs = [item[0] for item in batch]
            targets = [item[1] for item in batch]
            yield inputs, targets

    def __len__(self):
        return (len(self.data) + self.batch_size - 1) // self.batch_size
```

### Krok 10: Trenuj sieć 4-warstwową w oparciu o klasyfikację okręgową

Połącz wszystko razem. Zdefiniuj model, wybierz stratę, wybierz optymalizator, uruchom pętlę treningową.

```python
def make_circle_data(n=500, seed=42):
    random.seed(seed)
    data = []
    for _ in range(n):
        x = random.uniform(-2, 2)
        y = random.uniform(-2, 2)
        label = 1.0 if x * x + y * y < 1.5 else 0.0
        data.append(([x, y], [label]))
    return data

def train():
    random.seed(42)

    model = Sequential(
        Linear(2, 16),
        ReLU(),
        Linear(16, 16),
        ReLU(),
        Linear(16, 8),
        ReLU(),
        Linear(8, 1),
        Sigmoid(),
    )

    criterion = BCELoss()
    optimizer = Adam(model.parameters(), lr=0.01)

    data = make_circle_data(500)
    split = int(len(data) * 0.8)
    train_data = data[:split]
    test_data = data[split:]

    loader = DataLoader(train_data, batch_size=16, shuffle=True)

    model.train()

    for epoch in range(100):
        total_loss = 0
        total_correct = 0
        total_samples = 0

        for batch_inputs, batch_targets in loader:
            batch_loss = 0
            for x, t in zip(batch_inputs, batch_targets):
                pred = model.forward(x)
                loss = criterion(pred, t)
                batch_loss += loss

                optimizer.zero_grad()
                grad = criterion.backward()
                model.backward(grad)
                optimizer.step()

                predicted_class = 1.0 if pred[0] >= 0.5 else 0.0
                if predicted_class == t[0]:
                    total_correct += 1
                total_samples += 1

            total_loss += batch_loss

        avg_loss = total_loss / total_samples
        accuracy = total_correct / total_samples * 100

        if epoch % 10 == 0 or epoch == 99:
            print(f"Epoch {epoch:3d} | Loss: {avg_loss:.6f} | Train Accuracy: {accuracy:.1f}%")

    model.eval()
    correct = 0
    for x, t in test_data:
        pred = model.forward(x)
        predicted_class = 1.0 if pred[0] >= 0.5 else 0.0
        if predicted_class == t[0]:
            correct += 1
    test_accuracy = correct / len(test_data) * 100
    print(f"\nTest Accuracy: {test_accuracy:.1f}% ({correct}/{len(test_data)})")

    return model, test_accuracy
```

## Użyj tego

Oto odpowiednik tego, co właśnie zbudowałeś w PyTorch:

```python
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

model = nn.Sequential(
    nn.Linear(2, 16),
    nn.ReLU(),
    nn.Linear(16, 16),
    nn.ReLU(),
    nn.Linear(16, 8),
    nn.ReLU(),
    nn.Linear(8, 1),
    nn.Sigmoid(),
)

criterion = nn.BCELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

for epoch in range(100):
    model.train()
    for inputs, targets in dataloader:
        optimizer.zero_grad()
        predictions = model(inputs)
        loss = criterion(predictions, targets)
        loss.backward()
        optimizer.step()

    model.eval()
    with torch.no_grad():
        test_predictions = model(test_inputs)
```

Struktura jest identyczna. `Sequential`, `Linear`, `ReLU`, `Sigmoid`, `BCELoss`, `Adam`, `zero_grad`, `backward`, `step`, `train`, `eval`. Każda koncepcja jest odwzorowana jeden do jednego. Różnica polega na tym, że PyTorch automatycznie obsługuje autograd (nie ma potrzeby implementowania funkcji backward() w każdym module), działa na GPU i jest optymalizowany od lat. Ale kości są takie same.

Teraz, gdy zobaczysz kod PyTorch, wiesz dokładnie, co dzieje się w każdej linii. O to właśnie chodzi.

## Wyślij to

Ta lekcja daje:
- `outputs/prompt-framework-architect.md` — zachęta do projektowania architektur sieci neuronowych przy użyciu abstrakcji frameworka

## Ćwiczenia

1. Dodaj klasę `SoftmaxCrossEntropyLoss` dla klasyfikacji wieloklasowej. Softmax prognozy, oblicza stratę entropii krzyżowej i obsługuje połączone przejście wstecz. Przetestuj to na zbiorze danych spirali 3 klas.

2. Zaimplementuj w optymalizatorze planowanie szybkości uczenia się: dodaj metodę `set_lr()` i połącz harmonogram cosinusów z lekcji 09. Wytrenuj klasyfikator kołowy za pomocą rozgrzewki + cosinus i porównaj ze stałym LR.

3. Dodaj metody `save()` i `load()` do Sequential, które serializują wszystkie wagi do pliku JSON i ładują je z powrotem. Sprawdź, czy załadowany model generuje takie same przewidywania jak oryginał.

4. Zaimplementuj rozkład masy (regularyzacja L2) w optymalizatorze Adama. Dodaj parametr `weight_decay`, który w każdym kroku zmniejsza wagę do zera. Porównaj trening z zanikiem = 0 vs zanikiem = 0,01.

5. Zastąp pętlę szkoleniową dla poszczególnych próbek odpowiednią akumulacją gradientów w minipartiach: zsumuj gradienty we wszystkich próbkach w partii, następnie podziel przez wielkość partii i wykonaj jeden krok optymalizatora. Zmierz, czy zmienia to prędkość konwergencji.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|----------------------|
| Moduł | „Warstwa” | Podstawowa abstrakcja w frameworku — wszystko z forward(), backward() i parametrami() |
| Sekwencyjny | „Ułóż warstwy w kolejności” | Kontener, który łączy moduły, stosując je sekwencyjnie do przodu i do tyłu do tyłu |
| Podanie w przód | „Uruchom sieć” | Obliczanie wyniku poprzez przekazywanie danych wejściowych przez każdy moduł w kolejności |
| Podanie do tyłu | „Oblicz gradienty” | Propagowanie gradientu strat przez każdy moduł w odwrotnej kolejności w celu obliczenia gradientów parametrów |
| Parametry | „Ciężary nadające się do treningu” | Wszystkie wartości w sieci, które optymalizator może aktualizować — wagi i błędy systematyczne |
| Optymalizator | „To, co aktualizuje wagę” | Algorytm wykorzystujący gradienty do aktualizacji parametrów, implementujący SGD, Adam lub inne reguły |
| Moduł ładowania danych | „To, co zasila dane” | Iterator dzielący zbiór danych na partie, opcjonalnie mieszając między epokami |
| Tryb treningowy | "model.pociąg()" | Flaga umożliwiająca zachowanie stochastyczne, takie jak porzucanie i normalizacja wsadowa za pomocą statystyk wsadowych |
| Tryb oceny | "model.eval()" | Flaga wyłączająca porzucanie i wykorzystująca statystyki bieżące do normalizacji wsadowej |
| Zerowy stopień | „Wyczyść gradienty” | Resetowanie wszystkich gradientów parametrów do zera przed obliczeniem gradientów następnej partii |

## Dalsze czytanie

- Paszke i in., „PyTorch: An Imperative Style, High-Performance Deep Learning Library” (2019) – artykuł opisujący decyzje projektowe PyTorch
– Chollet, „Deep Learning with Python, Second Edition” (2021) – Rozdział 3 omawia elementy wewnętrzne Keras z tą samą abstrakcją modułów/warstw
– Johnson, „Tiny-DNN” (https://github.com/tiny-dnn/tiny-dnn) — platforma głębokiego uczenia się C++ zawierająca tylko nagłówki, umożliwiająca zrozumienie wewnętrznych elementów frameworka