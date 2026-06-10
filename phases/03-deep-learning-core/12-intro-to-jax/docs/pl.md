# Wprowadzenie do JAX

> PyTorch mutuje tensory. TensorFlow buduje wykresy. JAX kompiluje czyste funkcje. To ostatnie zmienia sposób myślenia o głębokim uczeniu się.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 03, lekcje 01-10, podstawowy NumPy
**Czas:** ~90 minut

## Cele nauczania

- Napisz kod sieci neuronowej o czystej funkcjonalności, korzystając z funkcjonalnego API JAX (jax.numpy, jax.grad, jax.jit, jax.vmap)
- Wyjaśnij kluczową różnicę projektową pomiędzy chętną mutacją PyTorch a funkcjonalnym modelem kompilacji JAX
- Zastosuj kompilację jit i wektoryzację vmap, aby przyspieszyć pętle szkoleniowe w porównaniu z naiwnym Pythonem
- Wytrenuj prostą sieć w JAX i porównaj jawne zarządzanie stanem z podejściem obiektowym PyTorch

## Problem

Wiesz, jak budować sieci neuronowe w PyTorch. Definiujesz `nn.Module`, wywołujesz `.backward()`, uruchamiasz optymalizator. To działa. Korzystają z niego miliony ludzi.

Ale PyTorch ma pewne ograniczenie wpisane w swoje DNA: chętnie śledzi operacje w Pythonie, pojedynczo. Każde `tensor + tensor` jest osobnym uruchomieniem jądra. Każdy krok szkoleniowy reinterpretuje ten sam kod Pythona. Działa to dobrze, dopóki nie trzeba wytrenować modelu o 540 miliardach parametrów w 2048 TPU. Wtedy obciążenie cię zabije.

Google DeepMind szkoli Gemini w JAX. Anthropic przeszkolił Claude'a na JAX. To nie są małe operacje – to największe na Ziemi treningi sieci neuronowych. Wybrali JAX, ponieważ traktuje pętlę treningową jako program, który można skompilować, a nie sekwencję wywołań Pythona.

JAX to NumPy z trzema supermocami: automatycznym różnicowaniem, kompilacją JIT do XLA i automatyczną wektoryzacją. Piszesz funkcję, która przetwarza jeden przykład. JAX udostępnia funkcję, która przetwarza wsadowo, oblicza gradienty, kompiluje do kodu maszynowego i działa na wielu urządzeniach. Wszystko bez zmiany pierwotnej funkcji.

## Koncepcja

### Filozofia JAX

JAX to framework funkcjonalny. Żadnych klas, żadnego modyfikowalnego stanu, żadnej metody `.backward()`. Zamiast tego:

| PyTorch | JAX |
|--------|-----|
| `nn.Module` klasa ze stanem | Czysta funkcja: `f(params, x) -> y` |
| `loss.backward()` | `jax.grad(loss_fn)(params, x, y)` |
| Chętna egzekucja | Kompilacja JIT poprzez XLA |
| `for x in batch:` pętla ręczna | `jax.vmap(f)` automatyczna wektoryzacja |
| `DataParallel` / `FSDP` | `jax.pmap(f)` autorównoległość |
| Zmienny `model.parameters()` | Niezmienne pytree tablic |

To nie jest preferencja stylu. Jest to ograniczenie kompilatora. Kompilacja JIT wymaga czystych funkcji - te same dane wejściowe zawsze dają te same wyniki, bez skutków ubocznych. To ograniczenie umożliwia 100-krotne przyspieszenie.

### jax.numpy: Znana powierzchnia

JAX ponownie implementuje API NumPy w akceleratorach:

```python
import jax.numpy as jnp

a = jnp.array([1.0, 2.0, 3.0])
b = jnp.array([4.0, 5.0, 6.0])
c = jnp.dot(a, b)
```

Te same nazwy funkcji. Te same zasady nadawania. Ta sama semantyka krojenia. Ale tablice działają na GPU/TPU, a kompilator może prześledzić każdą operację.

Jedna krytyczna różnica: tablice JAX są niezmienne. Nie `a[0] = 5`. Zamiast tego: `a = a.at[0].set(5)`. Przez tydzień wydaje się to niezręczne, a potem klika — niezmienność sprawia, że ​​transformacje takie jak `grad`, `jit` i `vmap` dają się komponować.

### jax.grad: Funkcjonalna automatyczna różnica

PyTorch dołącza gradienty do tensorów (`.grad`). JAX dołącza gradienty do funkcji.

```python
import jax

def f(x):
    return x ** 2

df = jax.grad(f)
df(3.0)
```

`jax.grad` pobiera funkcję i zwraca nową funkcję, która oblicza gradient. Brak połączenia `.backward()`. Żaden wykres obliczeniowy nie jest przechowywany na tensorach. Gradient to kolejna funkcja, którą możesz wywołać, utworzyć lub skompilować za pomocą JIT.

To tworzy arbitralnie:

```python
d2f = jax.grad(jax.grad(f))
d2f(3.0)
```

Drugie pochodne. Trzecie pochodne. Jakobiani. Hesowie. Wszystko poprzez komponowanie `grad`. PyTorch też może to zrobić (`torch.autograd.functional.hessian`), ale jest przykręcony. W JAX to podstawa.

Ograniczenie: `grad` działa tylko na czystych funkcjach. Brak instrukcji print w środku (działają podczas śledzenia, a nie wykonywania). Brak mutacji stanu zewnętrznego. Żadnego generowania liczb losowych bez wyraźnego zarządzania kluczami.

### jit: Kompiluj do XLA

```python
@jax.jit
def train_step(params, x, y):
    loss = loss_fn(params, x, y)
    return loss

fast_step = jax.jit(train_step)
```

Przy pierwszym wywołaniu JAX śledzi funkcję - rejestruje, jakie operacje mają miejsce, bez ich wykonywania. Następnie przekazuje ten ślad do XLA (Accelerated Linear Algebra), kompilatora Google dla TPU i GPU. XLA łączy operacje, eliminuje zbędne kopie pamięci i generuje zoptymalizowany kod maszynowy.

Kolejne wywołania całkowicie pomijają Pythona. Skompilowany kod działa na akceleratorze z szybkością C++.

Kiedy JIT pomaga:
- Kroki szkoleniowe (te same obliczenia powtarzane tysiące razy)
- Wnioskowanie (ten sam model, różne dane wejściowe)
- Dowolna funkcja wywoływana więcej niż raz z danymi wejściowymi o podobnym kształcie

Kiedy JIT boli:
- Funkcje z przepływem sterowania w Pythonie zależnym od wartości (`if x > 0` gdzie x jest tablicą śledzoną)
- Obliczenia jednorazowe (narzut kompilacji przekracza czas wykonania)
- Debugowanie (śledzenie ukrywa faktyczne wykonanie)

Ograniczenie przepływu sterowania jest rzeczywiste. `jax.lax.cond` zastępuje `if/else`. `jax.lax.scan` zastępuje pętle `for`. Nie są one opcjonalne – są ceną kompilacji.

### vmap: Automatyczna wektoryzacja

Piszesz funkcję, która przetwarza jeden przykład:

```python
def predict(params, x):
    return jnp.dot(params['w'], x) + params['b']
```

`vmap` podnosi go, aby przetworzyć partię:

```python
batch_predict = jax.vmap(predict, in_axes=(None, 0))
```

`in_axes=(None, 0)` oznacza: nie przetwarzaj wsadowo przez `params` (współdzielone), wsadowo ponad oś 0 `x`. Brak ręcznej pętli `for`. Żadnego przekształcania. Brak gwintowania wymiarów partii. JAX oblicza wymiar wsadowy i wektoryzuje całe obliczenia.

To nie jest cukier syntaktyczny. `vmap` generuje połączony kod wektorowy, który działa 10–100 razy szybciej niż pętla Pythona. I komponuje się z `jit` i `grad`:

```python
per_example_grads = jax.vmap(jax.grad(loss_fn), in_axes=(None, 0, 0))
```

Gradienty według przykładu. Jedna linia. Jest to prawie niemożliwe w PyTorch bez hacków.

### pmap: Równoległość danych na różnych urządzeniach

```python
parallel_step = jax.pmap(train_step, axis_name='devices')
```

`pmap` replikuje tę funkcję na wszystkich dostępnych urządzeniach (GPU/TPU) i dzieli partię. Wewnątrz funkcji `jax.lax.pmean` i `jax.lax.psum` synchronizują gradienty między urządzeniami.

Google szkoli Gemini na tysiącach chipów TPU v5e przy użyciu narzędzia `pmap` (i jego następcy `shard_map`). Model programowania: napisz wersję na jedno urządzenie, zapakuj `pmap` i gotowe.

### Pytrees: uniwersalna struktura danych

JAX działa na „pytrees” – zagnieżdżonych kombinacjach list, krotek, słowników i tablic. Parametry Twojego modelu to pytree:

```python
params = {
    'layer1': {'w': jnp.zeros((784, 256)), 'b': jnp.zeros(256)},
    'layer2': {'w': jnp.zeros((256, 128)), 'b': jnp.zeros(128)},
    'layer3': {'w': jnp.zeros((128, 10)),  'b': jnp.zeros(10)},
}
```

Każda transformacja JAX — `grad`, `jit`, `vmap` — wie, jak przeglądać pytree. `jax.tree.map(f, tree)` dotyczy `f` do każdego liścia. W ten sposób optymalizatory aktualizują wszystkie parametry na raz:

```python
params = jax.tree.map(lambda p, g: p - lr * g, params, grads)
```

Brak metody `.parameters()`. Brak rejestracji parametrów. Modelem jest struktura drzewa.

### Funkcjonalne a obiektowe

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

Parametry są przekazywane. Nic nie jest przechowywane. Nic nie jest zmutowane. Dzięki temu każdą funkcję można testować, komponować i kompilować. Oznacza to również, że możesz samodzielnie zarządzać parametrami lub korzystać z bibliotek takich jak Flax lub Equinox.

### Ekosystem JAX

JAX daje prymitywy. Biblioteki zapewniają ergonomię:

| Biblioteka | Rola | Styl |
|--------|------|-------|
| **Len** (Google) | Warstwy sieci neuronowej | `nn.Module` z jawnym stanem |
| **Równonoc** (Patrick Kidger) | Warstwy sieci neuronowej | Oparte na Pytree, Pythonic |
| **Optax** (Głęboki Umysł) | Optymalizatory + harmonogramy LR | Kompozytowalne transformacje gradientowe |
| **Orbax** (Google) | Punkt kontrolny | Zapisz/przywróć pytrees |
| **CLU** (Google) | Metryki + rejestrowanie | Narzędzia pętli treningowej |

Optax to standardowa biblioteka optymalizatora. Oddziela transformację gradientu (Adam, SGD, obcinanie) od aktualizacji parametrów, dzięki czemu komponowanie jest banalne:

```python
optimizer = optax.chain(
    optax.clip_by_global_norm(1.0),
    optax.adam(learning_rate=1e-3),
)
```

### Kiedy używać JAX zamiast PyTorch

| Czynnik | JAX | PyTorch |
|--------|-----|--------|
| Wsparcie TPU | Pierwszorzędna (Google zbudował oba) | Utrzymywany przez społeczność (torch_xla) |
| Obsługa GPU | Dobrze (CUDA przez XLA) | Najlepszy w swojej klasie (natywny CUDA) |
| Debugowanie | Trudne (śledzenie + kompilacja) | Łatwy (chętny, linia po linii) |
| Ekosystem | Skoncentrowany na badaniach (len, równonoc) | Masywny (HuggingFace, widzenie z pochodnią itp.) |
| Zatrudnianie | Nisza (Google/DeepMind/Anthropic) | Główny nurt (wszędzie) |
| Szkolenia na dużą skalę | Superior (XLA, pmap, siatka) | Dobry (FSDP, DeepSpeed) |
| Szybkość prototypowania | Wolniejsze (narzut funkcjonalny) | Szybciej (mutuj i idź) |
| Wnioskowanie o produkcji | Obsługa TensorFlow, Vertex AI | TorchServe, Triton, ONNX |
| Kto tego używa | DeepMind (Bliźnięta), Antropiczny (Claude) | Meta (Lama), OpenAI (GPT), Stabilność AI |

Szczera odpowiedź: użyj PyTorch, chyba że masz konkretny powód, aby używać JAX. Powody te są następujące: dostęp do TPU, potrzeba stosowania gradientów według przykładu, szkolenie na wielu urządzeniach na masową skalę lub praca w Google/DeepMind/Anthropic.

### Liczby losowe w JAX

JAX nie ma globalnego stanu losowego. Każda losowa operacja wymaga jawnego klucza PRNG:

```python
key = jax.random.PRNGKey(42)
key1, key2 = jax.random.split(key)
w = jax.random.normal(key1, shape=(784, 256))
```

Na początku jest to denerwujące. Gwarantuje jednak odtwarzalność na różnych urządzeniach i w kompilacjach — właściwość, której `torch.manual_seed` PyTorch nie może zagwarantować w przypadku ustawień wielu procesorów graficznych.

## Zbuduj to

### Krok 1: Konfiguracja i dane

Będziemy trenować 3-warstwowy MLP na MNIST przy użyciu JAX i Optax. 784 wejścia, dwie ukryte warstwy po 256 i 128 neuronów, 10 klas wyjściowych.

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

### Krok 2: Zainicjuj parametry

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

He-inicjalizacja, wykonywana ręcznie. Trzy klucze PRNG wydzielone z jednego ziarna. Każda waga jest niezmienną tablicą w zagnieżdżonym dyktacie.

### Krok 3: Podanie w przód

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

Czyste funkcje. Parametry wprowadzone, przewidywanie wyłączone. Nie `self`, brak stanu zapisanego. `loss_fn` oblicza entropię krzyżową od podstaw — softmax, log, średnia ujemna.

### Krok 4: Krok szkolenia skompilowany przez JIT

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

`jax.value_and_grad` zwraca zarówno wartość straty, jak i gradienty w jednym przebiegu. Dekorator `@jax.jit` kompiluje obie funkcje do XLA. Po pierwszym wywołaniu każdy etap szkolenia przebiega bez dotykania Pythona.

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

10 epok. Dokładność testu ~97%. Pierwsza epoka jest powolna (kompilacja JIT). Epoki 2-10 są szybkie.

Zwróć uwagę, czego brakuje: nie `.zero_grad()`, nie `.backward()`, nie `.step()`. Cała aktualizacja to jedno złożone wywołanie funkcji. Gradienty są obliczane, przekształcane przez Adama i stosowane do parametrów — wszystko wewnątrz `train_step`.

## Użyj tego

### Len: standard Google

Flax jest najpopularniejszą biblioteką sieci neuronowych JAX. Dodaje `nn.Module` z powrotem, ale z jawnym zarządzaniem stanem:

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

Taka sama struktura jak PyTorch, ale `params` jest oddzielna od modelu. `model.init()` tworzy parametry. `model.apply(params, x)` uruchamia podanie do przodu. Obiekt modelu nie ma stanu.

### Równonoc: pytoniczna alternatywa

Equinox (autor: Patrick Kidger) przedstawia modele jako pytrees:

```python
import equinox as eqx

model = eqx.nn.MLP(
    in_size=784, out_size=10, width_size=256, depth=2,
    activation=jax.nn.relu, key=jax.random.PRNGKey(0)
)
logits = model(x)
```

Sam model to pytree. Nie jest potrzebny `.apply()`. Parametry to tylko liście modelu. To jest bliższe temu, co myśli JAX.

### Optax: Optymalizatory komponowalne

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

Przycinanie gradientu, nagrzewanie tempa uczenia się, spadek wagi – wszystko to składa się z łańcucha transformacji. Każda transformacja widzi gradienty, modyfikuje je i przekazuje do następnej. Brak monolitycznej klasy optymalizatora.

## Wyślij to

**Instalacja:**

```bash
pip install jax jaxlib optax flax
```

W przypadku obsługi procesora graficznego:

```bash
pip install jax[cuda12]
```

W przypadku TPU (Google Cloud):

```bash
pip install jax[tpu] -f https://storage.googleapis.com/jax-releases/libtpu_releases.html
```

**Wady dotyczące wydajności:**

- Pierwsze wywołanie JIT jest powolne (kompilacja). Rozgrzewka przed benchmarkingiem.
- Unikaj pętli Pythona na tablicach JAX wewnątrz JIT. Użyj `jax.lax.scan` lub `jax.lax.fori_loop`.
- `jax.debug.print()` działa w JIT. Zwykły `print()` nie.
- Profil z `jax.profiler` lub TensorBoard. Kompilacja XLA może ukryć wąskie gardła.
- JAX domyślnie wstępnie przydziela 75% pamięci GPU. Ustaw `XLA_PYTHON_CLIENT_PREALLOCATE=false`, aby wyłączyć.

**Punkty kontrolne:**

```python
import orbax.checkpoint as ocp
checkpointer = ocp.PyTreeCheckpointer()
checkpointer.save('/tmp/model', params)
restored = checkpointer.restore('/tmp/model')
```

**Ta lekcja daje:**
- `outputs/prompt-jax-optimizer.md` — monit o wybranie właściwej konfiguracji optymalizatora JAX
- `outputs/skill-jax-patterns.md` — umiejętność obejmująca wzorce funkcjonalne w JAX

## Ćwiczenia

1. Dodaj rezygnację do MLP. W JAX przerwanie wymaga klucza PRNG - przeciągnij klucz przez przejście do przodu i podziel go dla każdej warstwy porzucenia. Porównaj dokładność testu z i bez.

2. Użyj `jax.vmap`, aby obliczyć gradienty na przykładach dla partii 32 obrazów MNIST. Oblicz normę gradientu dla każdego przykładu. Które przykłady mają największe gradienty i dlaczego?

3. Zastąp ręczną funkcję przesyłania dalej ogólną funkcją `mlp_forward(params, x)`, która działa dla dowolnej liczby warstw. Użyj `jax.tree.leaves`, aby automatycznie określić głębokość.

4. Wykonaj test porównawczy na etapie szkolenia z `@jax.jit` i bez niego. Czas na 100 kroków każdego. Jak duże jest przyspieszenie na twoim sprzęcie? Jaki jest narzut kompilacji przy pierwszym wywołaniu?

5. Zaimplementuj obcinanie gradientu, tworząc `optax.chain(optax.clip_by_global_norm(1.0), optax.adam(1e-3))`. Trenuj z przycinaniem i bez. Narysuj normę gradientu podczas treningu, aby zobaczyć efekt.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|----------------------|
| XLA | „To, co sprawia, że ​​JAX jest szybki” | Accelerated Linear Algebra - kompilator, który łączy operacje i generuje zoptymalizowane jądra GPU/TPU z wykresu obliczeniowego |
| JIT | „Kompilacja na czas” | JAX śledzi funkcję przy pierwszym wywołaniu, kompiluje do XLA, a następnie uruchamia skompilowaną wersję przy kolejnych wywołaniach
| Czysta funkcja | „Brak skutków ubocznych” | Funkcja, w której wynik zależy tylko od danych wejściowych — bez stanu globalnego, bez mutacji, bez losowości bez jawnych kluczy |
| mapa | „Automatyczne dozowanie” | Przekształca funkcję przetwarzającą jeden przykład w funkcję przetwarzającą partię bez przepisywania |
| mapa | „Autorównoległość” | Replikuje funkcję na wielu urządzeniach i dzieli partię wejściową |
| Pytree | „Zagnieżdżony dykt tablic” | Dowolna zagnieżdżona struktura list, krotek, słowników i tablic, które JAX może przeglądać i przekształcać |
| Śledzenie | „Zapisywanie obliczeń” | JAX wykonuje funkcję z wartościami abstrakcyjnymi, aby zbudować wykres obliczeniowy, bez obliczania rzeczywistych wyników
| Funkcjonalna automatyczna różnica | „grad funkcji” | Obliczanie pochodnych poprzez transformację funkcji, a nie przez dołączenie pamięci gradientu do tensorów |
| Optax | „Biblioteka optymalizatora JAX” | Komponowana biblioteka transformacji gradientowych – Adam, SGD, obcinanie, planowanie – które łączą się w całość |
| Len | „Moduł nn.JAX” | Biblioteka sieci neuronowej Google dla JAX, dodająca abstrakcje warstw przy jednoczesnym zachowaniu jawności stanu |

## Dalsze czytanie

- Dokumentacja JAX: https://jax.readthedocs.io/ - oficjalna dokumentacja ze świetnymi tutorialami na temat grad, jit i vmap
- „JAX: komponowalne transformacje programów Python+NumPy” (Bradbury et al., 2018) – artykuł oryginalny wyjaśniający filozofię projektowania
- Dokumentacja Flax: https://flax.readthedocs.io/ -- biblioteka sieci neuronowych Google dla JAX
– Patrick Kidger, „Equinox: sieci neuronowe w JAX poprzez wywoływalne drzewa PyTrees i filtrowane transformacje” (2021) – Pythonowa alternatywa dla Flaxa
- DeepMind, „Optax: komponowalna transformacja i optymalizacja gradientu” – standardowa biblioteka optymalizatora
- „You Don’t Know JAX” (Colin Raffel, 2020) – praktyczny przewodnik po gotchach i wzorcach JAX, od jednego z autorów T5