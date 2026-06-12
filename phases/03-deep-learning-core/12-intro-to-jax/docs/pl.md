# Wprowadzenie do JAX

> PyTorch mutuje tensory. TensorFlow buduje grafy. JAX kompiluje czyste funkcje. Ta ostatnia różnica zmienia sposób myślenia o uczeniu głębokim.

**Typ:** Build
**Języki:** Python
**Wymagania wstępne:** Faza 03, lekcje 01-10, podstawy NumPy
**Czas:** ~90 minut

## Cele nauki

- Pisanie kodu sieci neuronowych w stylu czystych funkcji przy użyciu funkcyjnego API JAX (jax.numpy, jax.grad, jax.jit, jax.vmap)
- Wyjaśnienie kluczowej różnicy projektowej między eagerową mutacją w PyTorch a funkcyjnym modelem kompilacji w JAX
- Zastosowanie kompilacji jit oraz wektoryzacji vmap do przyspieszenia pętli treningowych w porównaniu do naiwnego Pythona
- Wytrenowanie prostej sieci w JAX i porównanie jawnego zarządzania stanem z obiektowym podejściem PyTorch

## Problem

Wiesz, jak budować sieci neuronowe w PyTorch. Definiujesz `nn.Module`, wywołujesz `.backward()`, robisz krok optymalizatora. Działa. Korzystają z tego miliony ludzi.

Jednak PyTorch ma ograniczenie wpisane w swoje DNA: śledzi operacje eagerowo, jedną po drugiej, w Pythonie. Każde `tensor + tensor` to osobne wywołanie kernela. Każdy krok treningowy ponownie interpretuje ten sam kod Pythona. To działa dobrze, dopóki nie musisz wytrenować modelu o 540 miliardach parametrów na 2048 TPU. Wtedy narzut zaczyna zabijać wydajność.

Google DeepMind trenuje Gemini na JAX. Anthropic trenował Claude na JAX. To nie są małe operacje -- to największe treningi sieci neuronowych na świecie. Wybrali JAX, ponieważ traktuje pętlę treningową jako kompilowalny program, a nie sekwencję wywołań Pythona.

JAX to NumPy z trzema supermocami: automatyczne różniczkowanie, kompilacja JIT do XLA i automatyczna wektoryzacja. Piszesz funkcję, która przetwarza jeden przykład. JAX daje ci funkcję, która przetwarza batch, liczy gradienty, kompiluje się do kodu maszynowego i działa na wielu urządzeniach. Wszystko bez zmiany oryginalnej funkcji.

## Koncepcja

### Filozofia JAX

JAX jest frameworkiem funkcyjnym. Brak klas, brak mutowalnego stanu, brak metody `.backward()`. Zamiast tego:

| PyTorch | JAX |
|---------|-----|
| Klasa `nn.Module` ze stanem | Czysta funkcja: `f(params, x) -> y` |
| `loss.backward()` | `jax.grad(loss_fn)(params, x, y)` |
| Wykonanie eagerowe | Kompilacja JIT przez XLA |
| Ręczna pętla `for x in batch:` | Automatyczna wektoryzacja `jax.vmap(f)` |
| `DataParallel` / `FSDP` | Automatyczna równoległość `jax.pmap(f)` |
| Mutowalne `model.parameters()` | Niemutowalny pytree tablic |

To nie jest kwestia preferencji stylistycznych. To ograniczenie wynikające z kompilatora. Kompilacja JIT wymaga czystych funkcji -- te same wejścia zawsze dają te same wyjścia, brak efektów ubocznych. To ograniczenie jest tym, co umożliwia przyspieszenia 100x.

### jax.numpy: znana powierzchnia API

JAX reimplementuje API NumPy na akceleratorach:

```python
import jax.numpy as jnp

a = jnp.array([1.0, 2.0, 3.0])
b = jnp.array([4.0, 5.0, 6.0])
c = jnp.dot(a, b)
```

Te same nazwy funkcji. Te same reguły broadcastingu. Ta sama semantyka wycinania (slicing). Ale tablice żyją na GPU/TPU, a każda operacja jest śledzona (traceable) przez kompilator.

Jedna kluczowa różnica: tablice JAX są niemutowalne. Brak `a[0] = 5`. Zamiast tego: `a = a.at[0].set(5)`. Przez tydzień wydaje się to niewygodne, a potem "klika" -- niemutowalność jest tym, co sprawia, że transformacje takie jak `grad`, `jit` i `vmap` są kompozycyjne.

### jax.grad: funkcyjne automatyczne różniczkowanie

PyTorch dołącza gradienty do tensorów (`.grad`). JAX dołącza gradienty do funkcji.

```python
import jax

def f(x):
    return x ** 2

df = jax.grad(f)
df(3.0)
```

`jax.grad` przyjmuje funkcję i zwraca nową funkcję, która liczy gradient. Brak wywołania `.backward()`. Brak grafu obliczeń przechowywanego na tensorach. Gradient jest po prostu kolejną funkcją, którą możesz wywołać, skomponować lub skompilować JIT-em.

To komponuje się dowolnie:

```python
d2f = jax.grad(jax.grad(f))
d2f(3.0)
```

Drugie derywaty. Trzecie derywaty. Jakobiany. Hesjany. Wszystko poprzez komponowanie `grad`. PyTorch też to umie (`torch.autograd.functional.hessian`), ale jest to dołożone na zewnątrz. W JAX to jest fundament.

Ograniczenie: `grad` działa tylko na czystych funkcjach. Brak instrukcji print w środku (wykonują się podczas tracingu, nie podczas wykonania). Brak mutacji zewnętrznego stanu. Brak generowania liczb losowych bez jawnego zarządzania kluczem.

### jit: kompilacja do XLA

```python
@jax.jit
def train_step(params, x, y):
    loss = loss_fn(params, x, y)
    return loss

fast_step = jax.jit(train_step)
```

Przy pierwszym wywołaniu JAX śledzi (traces) funkcję -- zapisuje, jakie operacje się dzieją, bez ich wykonywania. Następnie przekazuje ten trace do XLA (Accelerated Linear Algebra), kompilatora Google dla TPU i GPU. XLA łączy operacje (fusion), eliminuje zbędne kopie pamięci i generuje zoptymalizowany kod maszynowy.

Kolejne wywołania całkowicie pomijają Pythona. Skompilowany kod działa na akceleratorze z prędkością C++.

Kiedy JIT pomaga:
- Kroki treningowe (te same obliczenia powtarzane tysiące razy)
- Inferencja (ten sam model, różne wejścia)
- Każda funkcja wywoływana więcej niż raz z wejściami o podobnych kształtach

Kiedy JIT szkodzi:
- Funkcje z kontrolą przepływu w Pythonie zależną od wartości (`if x > 0`, gdzie x jest śledzoną tablicą)
- Obliczenia jednorazowe (narzut kompilacji przewyższa czas wykonania)
- Debugowanie (tracing skrywa rzeczywiste wykonanie)

Ograniczenie kontroli przepływu jest realne. `jax.lax.cond` zastępuje `if/else`. `jax.lax.scan` zastępuje pętle `for`. Nie są to opcjonalne udogodnienia -- to cena kompilacji.

### vmap: automatyczna wektoryzacja

Piszesz funkcję, która przetwarza jeden przykład:

```python
def predict(params, x):
    return jnp.dot(params['w'], x) + params['b']
```

`vmap` podnosi ją do przetwarzania batcha:

```python
batch_predict = jax.vmap(predict, in_axes=(None, 0))
```

`in_axes=(None, 0)` znaczy: nie batchuj po `params` (współdzielone), batchuj po osi 0 `x`. Brak ręcznej pętli `for`. Brak reshapingu. Brak ręcznego przeprowadzania wymiaru batcha przez kod. JAX sam ustala wymiar batcha i wektoryzuje całe obliczenie.

To nie jest tylko cukier syntaktyczny. `vmap` generuje połączony (fused), zwektoryzowany kod, który działa 10-100x szybciej niż pętla w Pythonie. I komponuje się z `jit` i `grad`:

```python
per_example_grads = jax.vmap(jax.grad(loss_fn), in_axes=(None, 0, 0))
```

Gradienty per-przykład. Jedna linia. W PyTorch jest to praktycznie niemożliwe bez sztuczek.

### pmap: równoległość danych między urządzeniami

```python
parallel_step = jax.pmap(train_step, axis_name='devices')
```

`pmap` replikuje funkcję na wszystkich dostępnych urządzeniach (GPU/TPU) i dzieli batch. Wewnątrz funkcji `jax.lax.pmean` i `jax.lax.psum` synchronizują gradienty między urządzeniami.

Google trenuje Gemini na tysiącach chipów TPU v5e, używając `pmap` (i jego następcy, `shard_map`). Model programowania: napisz wersję dla jednego urządzenia, owiń ją `pmap`, gotowe.

### Pytrees: uniwersalna struktura danych

JAX operuje na "pytrees" -- zagnieżdżonych kombinacjach list, tupli, dictów i tablic. Parametry twojego modelu są pytree:

```python
params = {
    'layer1': {'w': jnp.zeros((784, 256)), 'b': jnp.zeros(256)},
    'layer2': {'w': jnp.zeros((256, 128)), 'b': jnp.zeros(128)},
    'layer3': {'w': jnp.zeros((128, 10)),  'b': jnp.zeros(10)},
}
```

Każda transformacja JAX -- `grad`, `jit`, `vmap` -- wie, jak przechodzić po pytrees. `jax.tree.map(f, tree)` stosuje `f` do każdego liścia. W ten sposób optymalizatory aktualizują wszystkie parametry na raz:

```python
params = jax.tree.map(lambda p, g: p - lr * g, params, grads)
```

Brak metody `.parameters()`. Brak rejestracji parametrów. Struktura drzewa jest modelem.

### Funkcyjne vs obiektowe

PyTorch przechowuje stan wewnątrz obiektów:

```python
class Model(nn.Module):
    def __init__(self):
        self.linear = nn.Linear(784, 10)

    def forward(self, x):
        return self.linear(x)
```

JAX używa czystych funkcji z jawnym stanem:

```python
def predict(params, x):
    return jnp.dot(x, params['w']) + params['b']
```

Parametry są przekazywane jako argument. Nic nie jest przechowywane. Nic nie jest mutowane. To czyni każdą funkcję testowalną, kompozycyjną i kompilowalną. Oznacza to też, że sam zarządzasz parametrami -- albo używasz biblioteki takiej jak Flax czy Equinox.

### Ekosystem JAX

JAX daje ci prymitywy. Biblioteki dają ci ergonomię:

| Biblioteka | Rola | Styl |
|---------|------|-------|
| **Flax** (Google) | Warstwy sieci neuronowych | `nn.Module` z jawnym stanem |
| **Equinox** (Patrick Kidger) | Warstwy sieci neuronowych | Oparty na pytree, pythoniczny |
| **Optax** (DeepMind) | Optymalizatory + harmonogramy LR | Komponowalne transformacje gradientów |
| **Orbax** (Google) | Checkpointing | Zapis/odtwarzanie pytrees |
| **CLU** (Google) | Metryki + logowanie | Narzędzia do pętli treningowej |

Optax jest standardową biblioteką optymalizatorów. Oddziela transformację gradientu (Adam, SGD, clipping) od aktualizacji parametrów, co sprawia, że komponowanie jest trywialne:

```python
optimizer = optax.chain(
    optax.clip_by_global_norm(1.0),
    optax.adam(learning_rate=1e-3),
)
```

### Kiedy używać JAX, a kiedy PyTorch

| Czynnik | JAX | PyTorch |
|--------|-----|---------|
| Wsparcie TPU | Pierwszorzędne (Google zbudował obie rzeczy) | Wsparcie społeczności (torch_xla) |
| Wsparcie GPU | Dobre (CUDA przez XLA) | Najlepsze w swojej klasie (natywne CUDA) |
| Debugowanie | Trudne (tracing + kompilacja) | Łatwe (eager, linia po linii) |
| Ekosystem | Skoncentrowany na badaniach (Flax, Equinox) | Ogromny (HuggingFace, torchvision itd.) |
| Rekrutacja | Niszowe (Google/DeepMind/Anthropic) | Mainstream (wszędzie) |
| Trening na dużą skalę | Lepszy (XLA, pmap, mesh) | Dobry (FSDP, DeepSpeed) |
| Szybkość prototypowania | Wolniejsza (narzut funkcyjny) | Szybsza (mutuj i działaj) |
| Inferencja produkcyjna | TensorFlow Serving, Vertex AI | TorchServe, Triton, ONNX |
| Kto używa | DeepMind (Gemini), Anthropic (Claude) | Meta (Llama), OpenAI (GPT), Stability AI |

Szczera odpowiedź: używaj PyTorch, jeśli nie masz konkretnego powodu, by używać JAX. Te powody to -- dostęp do TPU, potrzeba gradientów per-przykład, trening na wielu urządzeniach w ogromnej skali, albo praca w Google/DeepMind/Anthropic.

### Liczby losowe w JAX

JAX nie ma globalnego stanu losowości. Każda operacja losowa wymaga jawnego klucza PRNG:

```python
key = jax.random.PRNGKey(42)
key1, key2 = jax.random.split(key)
w = jax.random.normal(key1, shape=(784, 256))
```

Na początku jest to uciążliwe. Ale gwarantuje powtarzalność (reproducibility) między urządzeniami i kompilacjami -- właściwość, której `torch.manual_seed` z PyTorch nie może zagwarantować w środowiskach wielu GPU.

## Zbuduj to

### Krok 1: Konfiguracja i dane

Wytrenujemy 3-warstwowy MLP na MNIST, używając JAX i Optax. 784 wejścia, dwie warstwy skryte o rozmiarach 256 i 128 neuronów, 10 klas wyjściowych.

```python
import jax
import jax.numpy as jnp
from jax import random
import optax

def get_mnist_data():
    from sklearn.datasets import fetch_openml
    mnist = fetch_openml('mnist_784', version=1, as_frame=False, parser='auto')
    X = mnist.data.astype('float32') / 255.0
    y = mnist.target.astype('int')
    X_train, X_test = X[:60000], X[60000:]
    y_train, y_test = y[:60000], y[60000:]
    return X_train, y_train, X_test, y_test
```

### Krok 2: Inicjalizacja parametrów

Brak klasy. Tylko funkcja, która zwraca pytree:

```python
def init_params(key):
    k1, k2, k3 = random.split(key, 3)
    scale1 = jnp.sqrt(2.0 / 784)
    scale2 = jnp.sqrt(2.0 / 256)
    scale3 = jnp.sqrt(2.0 / 128)
    params = {
        'layer1': {
            'w': scale1 * random.normal(k1, (784, 256)),
            'b': jnp.zeros(256),
        },
        'layer2': {
            'w': scale2 * random.normal(k2, (256, 128)),
            'b': jnp.zeros(128),
        },
        'layer3': {
            'w': scale3 * random.normal(k3, (128, 10)),
            'b': jnp.zeros(10),
        },
    }
    return params
```

Inicjalizacja He, wykonana ręcznie. Trzy klucze PRNG, wydzielone (split) z jednego seeda. Każda waga jest niemutowalną tablicą w zagnieżdżonym dicte.

### Krok 3: Przejście w przód (forward pass)

```python
def forward(params, x):
    x = jnp.dot(x, params['layer1']['w']) + params['layer1']['b']
    x = jax.nn.relu(x)
    x = jnp.dot(x, params['layer2']['w']) + params['layer2']['b']
    x = jax.nn.relu(x)
    x = jnp.dot(x, params['layer3']['w']) + params['layer3']['b']
    return x

def loss_fn(params, x, y):
    logits = forward(params, x)
    one_hot = jax.nn.one_hot(y, 10)
    return -jnp.mean(jnp.sum(jax.nn.log_softmax(logits) * one_hot, axis=-1))
```

Czyste funkcje. Parametry na wejściu, predykcja na wyjściu. Brak `self`, brak przechowywanego stanu. `loss_fn` liczy entropię skrośną (cross-entropy) od podstaw -- softmax, logarytm, ujemna średnia.

### Krok 4: Krok treningowy skompilowany przez JIT

```python
@jax.jit
def train_step(params, opt_state, x, y):
    loss, grads = jax.value_and_grad(loss_fn)(params, x, y)
    updates, opt_state = optimizer.update(grads, opt_state, params)
    params = optax.apply_updates(params, updates)
    return params, opt_state, loss

@jax.jit
def accuracy(params, x, y):
    logits = forward(params, x)
    preds = jnp.argmax(logits, axis=-1)
    return jnp.mean(preds == y)
```

`jax.value_and_grad` zwraca jednocześnie wartość straty i gradienty w jednym przejściu. Dekorator `@jax.jit` kompiluje obie funkcje do XLA. Po pierwszym wywołaniu każdy krok treningowy działa, nie dotykając Pythona.

### Krok 5: Pętla treningowa

```python
optimizer = optax.adam(learning_rate=1e-3)

X_train, y_train, X_test, y_test = get_mnist_data()
X_train, X_test = jnp.array(X_train), jnp.array(X_test)
y_train, y_test = jnp.array(y_train), jnp.array(y_test)

key = random.PRNGKey(0)
params = init_params(key)
opt_state = optimizer.init(params)

batch_size = 128
n_epochs = 10

for epoch in range(n_epochs):
    key, subkey = random.split(key)
    perm = random.permutation(subkey, len(X_train))
    X_shuffled = X_train[perm]
    y_shuffled = y_train[perm]

    epoch_loss = 0.0
    n_batches = len(X_train) // batch_size
    for i in range(n_batches):
        start = i * batch_size
        xb = X_shuffled[start:start + batch_size]
        yb = y_shuffled[start:start + batch_size]
        params, opt_state, loss = train_step(params, opt_state, xb, yb)
        epoch_loss += loss

    train_acc = accuracy(params, X_train[:5000], y_train[:5000])
    test_acc = accuracy(params, X_test, y_test)
    print(f"Epoch {epoch + 1:2d} | Loss: {epoch_loss / n_batches:.4f} | "
          f"Train Acc: {train_acc:.4f} | Test Acc: {test_acc:.4f}")
```

10 epok. ~97% dokładności na zbiorze testowym. Pierwsza epoka jest wolna (kompilacja JIT). Epoki 2-10 są szybkie.

Zauważ, czego brakuje: brak `.zero_grad()`, brak `.backward()`, brak `.step()`. Cała aktualizacja to jedno złożone wywołanie funkcji. Gradienty są obliczane, transformowane przez Adam i stosowane do parametrów -- wszystko wewnątrz `train_step`.

## Wykorzystaj to

### Flax: standard Google

Flax jest najpopularniejszą biblioteką sieci neuronowych dla JAX. Przywraca `nn.Module`, ale z jawnym zarządzaniem stanem:

```python
import flax.linen as nn

class MLP(nn.Module):
    @nn.compact
    def __call__(self, x):
        x = nn.Dense(256)(x)
        x = nn.relu(x)
        x = nn.Dense(128)(x)
        x = nn.relu(x)
        x = nn.Dense(10)(x)
        return x

model = MLP()
params = model.init(jax.random.PRNGKey(0), jnp.ones((1, 784)))
logits = model.apply(params, x_batch)
```

Ta sama struktura jak w PyTorch, ale `params` jest odseparowane od modelu. `model.init()` tworzy parametry. `model.apply(params, x)` wykonuje przejście w przód. Obiekt modelu nie ma stanu.

### Equinox: pythoniczna alternatywa

Equinox (autor: Patrick Kidger) reprezentuje modele jako pytrees:

```python
import equinox as eqx

model = eqx.nn.MLP(
    in_size=784, out_size=10, width_size=256, depth=2,
    activation=jax.nn.relu, key=jax.random.PRNGKey(0)
)
logits = model(x)
```

Model sam jest pytree. Nie trzeba `.apply()`. Parametry są po prostu liśćmi modelu. To bliżej sposobu myślenia JAX.

### Optax: komponowalne optymalizatory

Optax oddziela transformację gradientu od aktualizacji:

```python
schedule = optax.warmup_cosine_decay_schedule(
    init_value=0.0, peak_value=1e-3,
    warmup_steps=1000, decay_steps=50000
)

optimizer = optax.chain(
    optax.clip_by_global_norm(1.0),
    optax.adamw(learning_rate=schedule, weight_decay=0.01),
)
```

Przycinanie gradientów (gradient clipping), rozgrzewka (warmup) tempa uczenia, regularyzacja wagi (weight decay) -- wszystko skomponowane jako łańcuch transformacji. Każda transformacja widzi gradienty, modyfikuje je i przekazuje do następnej. Brak monolitycznej klasy optymalizatora.

## Wypuść to

**Instalacja:**

```bash
pip install jax jaxlib optax flax
```

Dla wsparcia GPU:

```bash
pip install jax[cuda12]
```

Dla TPU (Google Cloud):

```bash
pip install jax[tpu] -f https://storage.googleapis.com/jax-releases/libtpu_releases.html
```

**Pułapki wydajnościowe:**

- Pierwsze wywołanie JIT jest wolne (kompilacja). Rozgrzej (warm up) przed pomiarem wydajności.
- Unikaj pętli Pythona po tablicach JAX wewnątrz JIT. Używaj `jax.lax.scan` lub `jax.lax.fori_loop`.
- `jax.debug.print()` działa wewnątrz JIT. Zwykły `print()` nie.
- Profiluj za pomocą `jax.profiler` lub TensorBoard. Kompilacja XLA może maskować wąskie gardła.
- JAX domyślnie pre-alokuje 75% pamięci GPU. Ustaw `XLA_PYTHON_CLIENT_PREALLOCATE=false`, aby to wyłączyć.

**Checkpointing:**

```python
import orbax.checkpoint as ocp
checkpointer = ocp.PyTreeCheckpointer()
checkpointer.save('/tmp/model', params)
restored = checkpointer.restore('/tmp/model')
```

**Ta lekcja tworzy:**
- `outputs/prompt-jax-optimizer.md` -- prompt do wyboru właściwej konfiguracji optymalizatora JAX
- `outputs/skill-jax-patterns.md` -- skill obejmujący wzorce funkcyjne w JAX

## Zadania

1. Dodaj dropout do MLP. W JAX dropout wymaga klucza PRNG -- przeprowadź klucz przez przejście w przód i wydziel (split) go dla każdej warstwy dropout. Porównaj dokładność testową z dropoutem i bez niego.

2. Użyj `jax.vmap`, aby obliczyć gradienty per-przykład dla batcha 32 obrazów MNIST. Oblicz normę gradientu dla każdego przykładu. Które przykłady mają największe gradienty i czemu?

3. Zastąp ręczną funkcję forward generyczną funkcją `mlp_forward(params, x)`, która działa dla dowolnej liczby warstw. Użyj `jax.tree.leaves`, aby automatycznie ustalić głębokość.

4. Zmierz wydajność kroku treningowego z `@jax.jit` i bez niego. Zmierz czas 100 kroków każdego wariantu. Jak duże jest przyspieszenie na twoim sprzęcie? Jaki jest narzut kompilacji przy pierwszym wywołaniu?

5. Zaimplementuj przycinanie gradientów (gradient clipping) poprzez skomponowanie `optax.chain(optax.clip_by_global_norm(1.0), optax.adam(1e-3))`. Trenuj z przycinaniem i bez niego. Wykreśl normę gradientu w trakcie treningu, aby zobaczyć efekt.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to faktycznie znaczy |
|------|----------------|----------------------|
| XLA | "To, co sprawia, że JAX jest szybki" | Accelerated Linear Algebra -- kompilator, który łączy (fuses) operacje i generuje zoptymalizowane kernele GPU/TPU z grafu obliczeń |
| JIT | "Kompilacja just-in-time" | JAX śledzi (traces) funkcję przy pierwszym wywołaniu, kompiluje do XLA, a następnie uruchamia skompilowaną wersję przy kolejnych wywołaniach |
| Czysta funkcja | "Brak efektów ubocznych" | Funkcja, której wyjście zależy tylko od wejść -- brak globalnego stanu, brak mutacji, brak losowości bez jawnych kluczy |
| vmap | "Automatyczny batching" | Przekształca funkcję przetwarzającą jeden przykład w funkcję przetwarzającą batch, bez przepisywania kodu |
| pmap | "Automatyczna równoległość" | Replikuje funkcję na wielu urządzeniach i dzieli batch wejściowy |
| Pytree | "Zagnieżdżony dict tablic" | Każda zagnieżdżona struktura list, tupli, dictów i tablic, po której JAX może przechodzić i którą może transformować |
| Tracing | "Zapisywanie obliczenia" | JAX wykonuje funkcję na abstrakcyjnych wartościach, aby zbudować graf obliczeń, bez liczenia rzeczywistych wyników |
| Funkcyjne automatyczne różniczkowanie | "grad funkcji" | Obliczanie derywatów poprzez transformowanie funkcji, a nie poprzez dołączanie magazynu gradientów do tensorów |
| Optax | "Biblioteka optymalizatorów JAX" | Komponowalna biblioteka transformacji gradientów -- Adam, SGD, clipping, scheduling -- które łączą się w łańcuch |
| Flax | "nn.Module dla JAX" | Biblioteka sieci neuronowych Google dla JAX, dodająca abstrakcje warstw przy zachowaniu jawnego stanu |

## Dalsze materiały

- Dokumentacja JAX: https://jax.readthedocs.io/ -- oficjalna dokumentacja, ze świetnymi tutorialami o grad, jit i vmap
- "JAX: composable transformations of Python+NumPy programs" (Bradbury et al., 2018) -- oryginalna praca wyjaśniająca filozofię projektową
- Dokumentacja Flax: https://flax.readthedocs.io/ -- biblioteka sieci neuronowych Google dla JAX
- Patrick Kidger, "Equinox: neural networks in JAX via callable PyTrees and filtered transformations" (2021) -- pythoniczna alternatywa do Flax
- DeepMind, "Optax: composable gradient transformation and optimisation" -- standardowa biblioteka optymalizatorów
- "You Don't Know JAX" (Colin Raffel, 2020) -- praktyczny przewodnik po pułapkach i wzorcach JAX, od jednego z autorów T5
