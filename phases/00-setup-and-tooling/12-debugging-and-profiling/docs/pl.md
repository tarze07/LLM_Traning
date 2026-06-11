# Debugowanie i profilowanie

> Najgorsze błędy w AI nie powodują awarii. Trenują się w ciszy na śmieciowych danych i raportują piękną krzywą strat.

**Typ:** Build
**Język:** Python
**Wymagania wstępne:** Lekcja 1 (Środowisko deweloperskie), podstawowa znajomość PyTorch
**Czas:** ~60 minut

## Cele nauki

- Użycie warunkowego `breakpoint()` oraz `debug_print` do inspekcji kształtów tensorów, typów danych (dtype) i wartości NaN w trakcie treningu
- Profilowanie pętli treningowych za pomocą `cProfile`, `line_profiler` i `tracemalloc` w celu znalezienia wąskich gardeł
- Wykrywanie typowych błędów AI: niezgodności kształtów, NaN w stracie, wycieku danych (data leakage) oraz tensorów na niewłaściwym urządzeniu
- Skonfigurowanie TensorBoard do wizualizacji krzywych strat, histogramów wag i rozkładów gradientów

## Problem

Kod AI zawodzi inaczej niż zwykły kod. Aplikacja webowa pada ze stack trace'em. Źle skonfigurowana pętla treningowa działa przez 8 godzin, spala 200 dolarów czasu GPU i produkuje model, który przewiduje średnią z każdego wejścia. Kod nigdy nie zgłosił błędu. Problemem był tensor na niewłaściwym urządzeniu, zapomniane `.detach()` albo etykiety przeciekające do cech.

Potrzebujesz narzędzi do debugowania, które wyłapią te ciche błędy, zanim zmarnują twój czas i moc obliczeniową.

## Koncepcja

Debugowanie AI odbywa się na trzech poziomach:

```mermaid
graph TD
    L3["3. Dynamika treningu<br/>Krzywe strat, normy gradientów, aktywacje"] --> L2
    L2["2. Operacje na tensorach<br/>Kształty, dtypes, urządzenia, wartości NaN/Inf"] --> L1
    L1["1. Standardowy Python<br/>Breakpointy, logowanie, profilowanie, pamięć"]
```

Większość osób od razu przeskakuje do poziomu 3 (wpatrywanie się w TensorBoard). Ale 80% błędów AI żyje na poziomach 1 i 2.

## Zbuduj to

### Część 1: Debugowanie przez printy (tak, to działa)

Debugowanie przez printy jest lekceważone. Niesłusznie. W przypadku kodu z tensorami, celowany print bije krokowe przechodzenie przez debugger, ponieważ musisz zobaczyć kształty, typy danych i zakresy wartości naraz.

```python
def debug_print(name, tensor):
    print(f"{name}: shape={tensor.shape}, dtype={tensor.dtype}, "
          f"device={tensor.device}, "
          f"min={tensor.min().item():.4f}, max={tensor.max().item():.4f}, "
          f"mean={tensor.mean().item():.4f}, "
          f"has_nan={tensor.isnan().any().item()}")
```

Wywołuj to po każdej podejrzanej operacji. Gdy błąd zostanie znaleziony, usuń printy. Proste.

### Część 2: Debugger Pythona (pdb i breakpoint)

Wbudowany debugger jest niedoceniany w pracy z AI. Wstaw `breakpoint()` do swojej pętli treningowej i interaktywnie sprawdzaj tensory.

```python
def training_step(model, batch, criterion, optimizer):
    inputs, labels = batch
    outputs = model(inputs)
    loss = criterion(outputs, labels)

    if loss.item() > 100 or torch.isnan(loss):
        breakpoint()

    loss.backward()
    optimizer.step()
```

Kiedy debugger cię zatrzyma, przydatne komendy:

- `p outputs.shape` aby sprawdzić kształty
- `p loss.item()` aby zobaczyć wartość straty
- `p torch.isnan(outputs).sum()` aby policzyć NaN-y
- `p model.fc1.weight.grad` aby sprawdzić gradienty
- `c` aby kontynuować, `q` aby wyjść

To jest debugowanie warunkowe. Zatrzymujesz się tylko wtedy, gdy coś wygląda podejrzanie. Przy treningu trwającym 10 000 kroków ma to znaczenie.

### Część 3: Logowanie w Pythonie

Zastąp instrukcje print logowaniem, gdy twoje debugowanie wykracza poza szybkie sprawdzenie.

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("training.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

logger.info("Starting training: lr=%.4f, batch_size=%d", lr, batch_size)
logger.warning("Loss spike detected: %.4f at step %d", loss.item(), step)
logger.error("NaN loss at step %d, stopping", step)
```

Logowanie daje ci znaczniki czasu, poziomy ważności (severity levels) i zapis do pliku. Gdy trening padnie o 3 nad ranem, chcesz mieć plik logu, a nie wyjście z terminala, które przewinęło się poza ekran.

### Część 4: Pomiar czasu fragmentów kodu

Wiedza o tym, gdzie ucieka czas, to pierwszy krok do optymalizacji.

```python
import time

class Timer:
    def __init__(self, name=""):
        self.name = name

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, *args):
        elapsed = time.perf_counter() - self.start
        print(f"[{self.name}] {elapsed:.4f}s")

with Timer("data loading"):
    batch = next(dataloader_iter)

with Timer("forward pass"):
    outputs = model(batch)

with Timer("backward pass"):
    loss.backward()
```

Częste odkrycie: ładowanie danych zajmuje 60% czasu treningu. Rozwiązaniem jest `num_workers > 0` w twoim DataLoaderze, a nie szybsze GPU.

### Część 5: cProfile i line_profiler

Gdy potrzebujesz czegoś więcej niż ręcznych timerów:

```bash
python -m cProfile -s cumtime train.py
```

To pokazuje każde wywołanie funkcji posortowane według czasu skumulowanego (cumulative time). Do profilowania linia po linii:

```bash
pip install line_profiler
```

```python
@profile
def train_step(model, data, target):
    output = model(data)
    loss = F.cross_entropy(output, target)
    loss.backward()
    return loss

# Run with: kernprof -l -v train.py
```

### Część 6: Profilowanie pamięci

#### Pamięć CPU za pomocą tracemalloc

```python
import tracemalloc

tracemalloc.start()

# your code here
model = build_model()
data = load_dataset()

snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics("lineno")
for stat in top_stats[:10]:
    print(stat)
```

#### Pamięć CPU za pomocą memory_profiler

```bash
pip install memory_profiler
```

```python
from memory_profiler import profile

@profile
def load_data():
    raw = read_csv("data.csv")       # watch memory jump here
    processed = preprocess(raw)       # and here
    return processed
```

Uruchom za pomocą `python -m memory_profiler your_script.py`, aby zobaczyć zużycie pamięci linia po linii.

#### Pamięć GPU za pomocą PyTorch

```python
import torch

if torch.cuda.is_available():
    print(torch.cuda.memory_summary())

    print(f"Allocated: {torch.cuda.memory_allocated() / 1e9:.2f} GB")
    print(f"Cached: {torch.cuda.memory_reserved() / 1e9:.2f} GB")
```

Gdy trafisz na OOM (Out of Memory):

1. Zmniejsz rozmiar batcha (zawsze pierwsza rzecz do wypróbowania)
2. Użyj `torch.cuda.empty_cache()`, aby zwolnić pamięć z cache
3. Użyj `del tensor`, a następnie `torch.cuda.empty_cache()` dla dużych wartości pośrednich
4. Użyj precyzji mieszanej (`torch.cuda.amp`), aby zmniejszyć zużycie pamięci o połowę
5. Użyj gradient checkpointing dla bardzo głębokich modeli

### Część 7: Typowe błędy AI i jak je wyłapać

#### Niezgodność kształtów (Shape Mismatch)

Najczęstszy błąd. Tensor ma kształt `[batch, features]`, podczas gdy model oczekuje `[batch, channels, height, width]`.

```python
def check_shapes(model, sample_input):
    print(f"Input: {sample_input.shape}")
    hooks = []

    def make_hook(name):
        def hook(module, inp, out):
            in_shape = inp[0].shape if isinstance(inp, tuple) else inp.shape
            out_shape = out.shape if hasattr(out, "shape") else type(out)
            print(f"  {name}: {in_shape} -> {out_shape}")
        return hook

    for name, module in model.named_modules():
        hooks.append(module.register_forward_hook(make_hook(name)))

    with torch.no_grad():
        model(sample_input)

    for h in hooks:
        h.remove()
```

Uruchom to raz z przykładowym batchem. Mapuje to każdą transformację kształtu w twoim modelu.

#### NaN w stracie (NaN Loss)

NaN w stracie oznacza, że coś eksplodowało. Częste przyczyny:

- Zbyt wysoki learning rate
- Dzielenie przez zero w niestandardowej funkcji straty
- Logarytm zera lub liczby ujemnej
- Eksplodujące gradienty w RNN-ach

```python
def detect_nan(model, loss, step):
    if torch.isnan(loss):
        print(f"NaN loss at step {step}")
        for name, param in model.named_parameters():
            if param.grad is not None:
                if torch.isnan(param.grad).any():
                    print(f"  NaN gradient in {name}")
                if torch.isinf(param.grad).any():
                    print(f"  Inf gradient in {name}")
        return True
    return False
```

#### Wyciek danych (Data Leakage)

Twój model osiąga 99% dokładności na zbiorze testowym. Brzmi świetnie. To błąd.

```python
def check_data_leakage(train_set, test_set, id_column="id"):
    train_ids = set(train_set[id_column].tolist())
    test_ids = set(test_set[id_column].tolist())
    overlap = train_ids & test_ids
    if overlap:
        print(f"DATA LEAKAGE: {len(overlap)} samples in both train and test")
        return True
    return False
```

Sprawdź też wyciek czasowy (temporal leakage): wykorzystywanie przyszłych danych do przewidywania przeszłości. Posortuj według znacznika czasu przed podziałem.

#### Niewłaściwe urządzenie (Wrong Device)

Tensory na różnych urządzeniach (CPU vs GPU) powodują błędy w czasie wykonania. Ale czasem tensor po cichu pozostaje na CPU, podczas gdy wszystko inne jest na GPU, i trening po prostu działa wolno.

```python
def check_devices(model, *tensors):
    model_device = next(model.parameters()).device
    print(f"Model device: {model_device}")
    for i, t in enumerate(tensors):
        if t.device != model_device:
            print(f"  WARNING: tensor {i} on {t.device}, model on {model_device}")
```

### Część 8: Podstawy TensorBoard

TensorBoard pokazuje, co dzieje się wewnątrz treningu w czasie.

```bash
pip install tensorboard
```

```python
from torch.utils.tensorboard import SummaryWriter

writer = SummaryWriter("runs/experiment_1")

for step in range(num_steps):
    loss = train_step(model, batch)

    writer.add_scalar("loss/train", loss.item(), step)
    writer.add_scalar("lr", optimizer.param_groups[0]["lr"], step)

    if step % 100 == 0:
        for name, param in model.named_parameters():
            writer.add_histogram(f"weights/{name}", param, step)
            if param.grad is not None:
                writer.add_histogram(f"grads/{name}", param.grad, step)

writer.close()
```

Uruchom go:

```bash
tensorboard --logdir=runs
```

Na co zwracać uwagę:

- **Strata nie maleje**: Learning rate zbyt niski lub problem z architekturą modelu
- **Strata oscyluje gwałtownie**: Learning rate zbyt wysoki
- **Strata przechodzi w NaN**: Niestabilność numeryczna (zob. sekcja o NaN powyżej)
- **Strata treningowa maleje, strata walidacyjna rośnie**: Przeuczenie (overfitting)
- **Histogramy wag zapadają się do zera**: Zanikające gradienty (vanishing gradients)
- **Histogramy gradientów eksplodują**: Potrzebne przycinanie gradientów (gradient clipping)

### Część 9: Debugger VS Code

Do debugowania interaktywnego skonfiguruj VS Code za pomocą `launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug Training",
            "type": "debugpy",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "justMyCode": false
        }
    ]
}
```

Ustaw breakpointy, klikając na marginesie (gutter). Użyj panelu Variables, aby sprawdzić właściwości tensorów. Debug Console pozwala na uruchamianie dowolnych wyrażeń Pythona w trakcie wykonywania.

Przydatne do krokowego przechodzenia przez pipeline'y preprocessingu danych, gdzie chcesz zobaczyć każdą transformację.

## Zastosuj to

Oto przepływ debugowania, który wyłapuje większość błędów AI:

1. **Przed treningiem**: Uruchom `check_shapes` z przykładowym batchem. Zweryfikuj, czy wymiary wejścia i wyjścia odpowiadają oczekiwaniom.
2. **Pierwsze 10 kroków**: Użyj `debug_print` na stracie, wyjściach i gradientach. Potwierdź, że nic nie jest NaN i wartości mieszczą się w rozsądnych zakresach.
3. **W trakcie treningu**: Loguj stratę, learning rate i normy gradientów. Użyj TensorBoard do wizualizacji.
4. **Gdy coś się psuje**: Wstaw `breakpoint()` w miejscu awarii. Sprawdzaj tensory interaktywnie.
5. **Pod kątem wydajności**: Zmierz czas ładowania danych w porównaniu z forward i backward pass. Profiluj pamięć, jeśli zbliżasz się do OOM.

## Wdróż to

Uruchom skrypt zestawu narzędzi do debugowania:

```bash
python phases/00-setup-and-tooling/12-debugging-and-profiling/code/debug_tools.py
```

Zobacz `outputs/prompt-debug-ai-code.md`, aby znaleźć prompt pomagający diagnozować błędy specyficzne dla AI.

## Ćwiczenia

1. Uruchom `debug_tools.py` i przeczytaj wyniki każdej sekcji. Zmodyfikuj model dummy, aby wprowadzić NaN (wskazówka: dzielenie przez zero w forward pass) i zobacz, jak detektor go wyłapuje.
2. Sprofiluj pętlę treningową za pomocą `cProfile` i zidentyfikuj najwolniejszą funkcję.
3. Użyj `tracemalloc`, aby znaleźć, która linia w twoim pipeline'ie ładowania danych alokuje najwięcej pamięci.
4. Skonfiguruj TensorBoard dla prostego przebiegu treningowego i ustal, czy model się przeucza.
5. Użyj `breakpoint()` wewnątrz pętli treningowej. Poćwicz sprawdzanie kształtów tensorów, urządzeń i wartości gradientów z poziomu konsoli debuggera.
