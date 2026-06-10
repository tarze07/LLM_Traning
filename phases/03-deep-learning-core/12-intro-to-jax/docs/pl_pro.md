# Wprowadzenie do JAX

> PyTorch mutuje tensory. TensorFlow buduje statyczne wykresy. JAX kompiluje czyste funkcje. To ostatnie podejście całkowicie zmienia sposób myślenia o głębokim uczeniu.

**Typ:** Kompilacja  
**Języki:** Python  
**Wymagania wstępne:** Faza 03, lekcje 01-10, podstawy NumPy  
**Czas:** ~90 minut  

## Cele kształcenia

- Pisanie kodu sieci neuronowych w czysto funkcjonalnym stylu przy użyciu API JAX (`jax.numpy`, `jax.grad`, `jax.jit`, `jax.vmap`).
- Wyjaśnienie kluczowych różnic projektowych pomiędzy ewaluacją natychmiastową (eager evaluation) z mutacją stanu w PyTorch a funkcjonalnym modelem kompilacji w JAX.
- Zastosowanie kompilacji JIT (`jit`) oraz automatycznej wektoryzacji (`vmap`) w celu znacznego przyspieszenia pętli treningowych w porównaniu do czystego Pythona.
- Wytrenowanie prostej sieci w JAX i porównanie jawnego zarządzania stanem z obiektowym podejściem w PyTorch.

## Problem

Wiesz już, jak budować sieci neuronowe w PyTorch. Definiujesz klasę `nn.Module`, wywołujesz `loss.backward()` i uruchamiasz optymalizator. To działa i jest powszechnie stosowane przez miliony programistów.

PyTorch ma jednak w swojej architekturze pewną cechę: domyślnie wykonuje i śledzi operacje w Pythonie krok po kroku (eager execution). Każda operacja typu `tensor + tensor` to osobne uruchomienie jądra (kernel) na karcie graficznej. Każdy krok treningowy na nowo interpretuje ten sam kod Pythona. Sprawdza się to znakomicie do momentu, gdy musisz wytrenować model o 540 miliardach parametrów na 2048 układach TPU. Wtedy narzut interpretera Pythona staje się wąskim gardłem.

Google DeepMind trenuje modele Gemini w JAX. Anthropic przeszkolił modele Claude również przy użyciu JAX. Nie są to małe eksperymenty – to jedne z największych procesów obliczeniowych w historii sztucznej inteligencji. Twórcy wybrali JAX, ponieważ traktuje on całą pętlę treningową jako program podlegający kompilacji, a nie jako sekwencję niezależnych wywołań Pythona.

JAX to w uproszczeniu NumPy wyposażony w trzy supermoce: automatyczne różniczkowanie, kompilację JIT (Just-In-Time) do formatu XLA oraz automatyczną wektoryzację. Piszesz funkcję dla jednego przykładu, a JAX udostępnia narzędzia do jej przetwarzania w partiach, wyznaczania gradientów, kompilacji do zoptymalizowanego kodu maszynowego i uruchamiania na wielu urządzeniach równolegle – wszystko to bez modyfikacji oryginalnego kodu funkcji.

## Koncepcja

### Filozofia JAX

JAX to framework w pełni funkcjonalny. Nie znajdziesz tu klas reprezentujących warstwy, modyfikowalnych stanów ani metody `.backward()`. Zamiast tego stosuje się następujące mapowanie pojęć:

| PyTorch | JAX |
| :--- | :--- |
| Klasa ze stanem (`nn.Module`) | Czysta funkcja: `f(params, x) -> y` |
| Wsteczna propagacja (`loss.backward()`) | `jax.grad(loss_fn)(params, x, y)` |
| Ewaluacja natychmiastowa (Eager) | Kompilacja JIT za pomocą XLA |
| Ręczna pętla po partii (`for x in batch:`) | Automatyczna wektoryzacja (`jax.vmap(f)`) |
| Równoległość (`DataParallel` / `FSDP`) | Równoległość sprzętowa (`jax.pmap(f)`) |
| Zmienny stan parametrów (`model.parameters()`) | Niezmienne drzewo Pytree zawierające tablice |

To nie jest kwestia stylu programowania – to wymóg kompilatora. Kompilacja JIT wymaga stosowania czystych funkcji (pure functions). Oznacza to, że funkcja dla tych samych danych wejściowych musi zawsze zwracać ten sam wynik i nie może wywoływać skutków ubocznych (side effects). To ograniczenie pozwala jednak na uzyskanie nawet 100-krotnego przyspieszenia obliczeń.

### jax.numpy: Znajomy interfejs

JAX reimplementuje API NumPy w sposób umożliwiający uruchamianie kodu na akceleratorach:

```python
import jax.numpy as jnp

a = jnp.array([1.0, 2.0, 3.0])
b = jnp.array([4.0, 5.0, 6.0])
c = jnp.dot(a, b)
```

Nazwy funkcji, zasady rozgłaszania wymiarów (broadcasting) oraz semantyka wycinania (slicing) są identyczne jak w NumPy. Jednak tablice te działają bezpośrednio na GPU/TPU, a kompilator może śledzić wykonywane na nich operacje.

Kluczowa różnica: tablice w JAX są niezmienne (immutable). Zamiast zapisu `a[0] = 5`, musisz użyć składni: `a = a.at[0].set(5)`. Na początku może wydawać się to uciążliwe, ale niezmienność danych gwarantuje, że transformacje takie jak `grad`, `jit` i `vmap` można bezpiecznie ze sobą komponować.

### jax.grad: Funkcjonalne różniczkowanie automatyczne

PyTorch przypisuje gradienty bezpośrednio do obiektów tensorów (`tensor.grad`). JAX z kolei przypisuje gradienty do funkcji.

```python
import jax

def f(x):
    return x ** 2

df = jax.grad(f)
df(3.0)  # Zwraca 6.0
```

Funkcja `jax.grad` przyjmuje inną funkcję i zwraca nową funkcję obliczającą jej gradient. Nie ma potrzeby wywoływania `.backward()`. Na tensorach nie jest przechowywany żaden wykres obliczeniowy. Gradient to po prostu kolejna funkcja, którą można wywoływać, przekazywać dalej lub kompilować za pomocą JIT.

Dzięki temu kompozycja transformacji staje się naturalna:

```python
d2f = jax.grad(jax.grad(f))
d2f(3.0)  # Druga pochodna, zwraca 2.0
```

W ten sposób możesz bez przeszkód liczyć pochodne dowolnego rzędu, jakobiany czy hesjany. W PyTorch również jest to możliwe (`torch.autograd.functional`), ale wymaga to dodatkowych zabiegów. W JAX stanowi to sam fundament biblioteki.

Ograniczenie: `grad` działa wyłącznie na czystych funkcjach. Wewnątrz nich nie mogą występować operacje wejścia/wyjścia (np. instrukcje `print` wykonają się tylko podczas budowania wykresu, a nie jego późniejszego uruchamiania), mutacje zewnętrznego stanu ani generowanie liczb losowych bez jawnego przekazywania klucza losowości.

### jit: Kompilacja za pomocą XLA

```python
@jax.jit
def train_step(params, x, y):
    loss = loss_fn(params, x, y)
    return loss

fast_step = jax.jit(train_step)
```

Przy pierwszym wywołaniu JAX śledzi funkcję (tracing) – rejestruje sekwencję operacji na abstrakcyjnych obiektach o określonych kształtach i typach danych. Następnie przekazuje ten wykres do kompilatora XLA (Accelerated Linear Algebra), który łączy operacje (operator fusion), eliminuje zbędne kopiowanie pamięci i generuje wysoce zoptymalizowany kod maszynowy dla GPU lub TPU.

Kolejne wywołania całkowicie pomijają interpreter Pythona, uruchamiając skompilowany kod bezpośrednio na akceleratorze z prędkością kodu C++.

Kiedy warto stosować JIT:
- W krokach treningowych (powtarzanych tysiące razy).
- W procesie wnioskowania (inference) dla modelu.
- Dla dowolnej funkcji wywoływanej wielokrotnie z danymi o stałym kształcie.

Kiedy JIT stwarza problemy:
- W funkcjach z instrukcjami warunkowymi Pythona zależnymi od dynamicznych wartości tablic (`if x > 0` dla śledzonej zmiennej `x`).
- Przy jednorazowych obliczeniach (czas kompilacji przewyższy czas wykonania).
- Podczas debugowania (proces śledzenia ukrywa rzeczywisty przebieg wykonania kodu).

W przypadku kompilacji JIT tradycyjne konstrukcje sterujące muszą być zastąpione ich funkcjonalnymi odpowiednikami: `jax.lax.cond` zamiast `if/else`, a `jax.lax.scan` zamiast pętli `for`. To cena za wydajność kompilacji.

### vmap: Automatyczna wektoryzacja

Wyobraź sobie, że piszesz funkcję przetwarzającą pojedynczy przykład:

```python
def predict(params, x):
    return jnp.dot(params['w'], x) + params['b']
```

Dzięki `vmap` możesz natychmiast przystosować ją do przetwarzania całej partii danych (batch):

```python
batch_predict = jax.vmap(predict, in_axes=(None, 0))
```

Zapis `in_axes=(None, 0)` oznacza: nie wektoryzuj po parametrach `params` (są wspólne dla całej partii), natomiast wektoryzuj po zerowym wymiarze argumentu `x`. Nie potrzebujesz ręcznych pętli `for` ani operacji zmiany wymiarów (reshaping). JAX automatycznie zarządza wymiarem partii.

To nie jest jedynie uproszczenie składni. `vmap` generuje zunifikowany kod wektorowy działający od 10 do 100 razy szybciej niż pętla w Pythonie. Co ważne, komponuje się z `jit` oraz `grad`:

```python
per_example_grads = jax.vmap(jax.grad(loss_fn), in_axes=(None, 0, 0))
```

Dzięki temu obliczanie gradientów osobno dla każdego przykładu w partii sprowadza się do jednej linijki kodu. W PyTorch jest to bardzo trudne do zrealizowania bez specjalnych obejść (np. functorch).

### pmap: Równoległość sprzętowa

```python
parallel_step = jax.pmap(train_step, axis_name='devices')
```

`pmap` replikuje funkcję na wszystkich dostępnych urządzeniach (GPU/TPU) i automatycznie dzieli partię danych wejściowych pomiędzy nie. Funkcje `jax.lax.pmean` oraz `jax.lax.psum` pozwalają na synchronizację gradientów pomiędzy fizycznymi układami wewnątrz kompilowanego kodu.

Google trenuje swoje największe modele (Gemini) na tysiącach układów TPU przy użyciu `pmap` (oraz nowszego narzędzia `shard_map`). Model programowania jest prosty: napisz kod dla jednego urządzenia, a następnie opakuj go w transformację równoległą.

### Pytrees: Uniwersalna struktura danych

JAX operuje na strukturach zwanych „pytrees” – zagnieżdżonych strukturach składających się z list, krotek, słowników oraz tablic JAX. Parametry Twojego modelu to klasyczny przykład pytree:

```python
params = {
    'layer1': {'w': jnp.zeros((784, 256)), 'b': jnp.zeros(256)},
    'layer2': {'w': jnp.zeros((256, 128)), 'b': jnp.zeros(128)},
    'layer3': {'w': jnp.zeros((128, 10)),  'b': jnp.zeros(10)},
}
```

Transformacje JAX – takie jak `grad`, `jit` czy `vmap` – potrafią rekurencyjnie przetwarzać struktury pytree. Funkcja `jax.tree.map(f, tree)` aplikuje funkcję `f` do każdego liścia drzewa. Umożliwia to aktualizację wszystkich parametrów sieci w jednej linii kodu:

```python
params = jax.tree.map(lambda p, g: p - lr * g, params, grads)
```

Nie potrzebujesz metody `.parameters()` ani rejestracji zmiennych w obiektach. Model jest po prostu strukturą danych.

### Podejście funkcjonalne a obiektowe

PyTorch przechowuje stan wewnątrz obiektów:

```python
class Model(nn.Module):
    def __init__(self):
        super().__init__()
        self.linear = nn.Linear(784, 10)

    def forward(self, x):
        return self.linear(x)
```

JAX z kolei wykorzystuje czyste funkcje z jawnym przekazywaniem stanu:

```python
def predict(params, x):
    return jnp.dot(x, params['w']) + params['b']
```

Parametry są przekazywane jako jawny argument. Funkcja nie przechowuje stanu i niczego nie modyfikuje na stałe. Dzięki temu kod jest łatwy w testowaniu i optymalizacji, choć zmusza programistę do samodzielnego zarządzania strukturą parametrów (lub korzystania z bibliotek pomocniczych, takich jak Flax lub Equinox).

### Ekosystem bibliotek JAX

JAX dostarcza niskopoziomowe operatory. Ergonomię pracy zapewniają zewnętrzne biblioteki:

| Biblioteka | Rola | Styl |
| :--- | :--- | :--- |
| **Flax** (Google) | Warstwy sieci neuronowych | Definiowanie modułów z jawnym stanem |
| **Equinox** (Patrick Kidger) | Warstwy sieci neuronowych | Reprezentacja modeli bezpośrednio jako Pytrees |
| **Optax** (DeepMind) | Optymalizatory i harmonogramy LR | Komponowalne transformacje gradientów |
| **Orbax** (Google) | Zapisywanie stanów (checkpointing) | Zapis i odczyt struktur pytree |
| **CLU** (Google) | Metryki i logowanie | Narzędzia ułatwiające pisanie pętli treningowych |

Optax stanowi standard w dziedzinie optymalizacji. Oddziela on przekształcenia gradientów (takie jak przycinanie gradientów, Adam czy SGD) od samej procedury aktualizacji wag:

```python
optimizer = optax.chain(
    optax.clip_by_global_norm(1.0),
    optax.adam(learning_rate=1e-3),
)
```

### Kiedy wybrać JAX, a kiedy PyTorch?

| Cecha | JAX | PyTorch |
| :--- | :--- | :--- |
| **Wsparcie dla TPU** | Natywne i kompletne (Google rozwija oba projekty) | Przez zewnętrzną bibliotekę `torch_xla` |
| **Wsparcie dla GPU** | Bardzo dobre (kompilacja CUDA via XLA) | Najlepsze (natywne, zoptymalizowane jądra CUDA) |
| **Debugowanie kodu** | Trudniejsze (przez etap śledzenia i kompilacji) | Proste i intuicyjne (kod wykonywany linia po linii) |
| **Ekosystem** | Nastawiony na badania naukowe (Flax, Equinox) | Ogromny i uniwersalny (HuggingFace, torchvision itp.) |
| **Rynek pracy** | Specjalistyczny (Google, DeepMind, Anthropic) | Powszechny (większość firm komercyjnych) |
| **Skalowanie treningu** | Doskonałe (XLA, pmap, shard_map) | Dobre (FSDP, DeepSpeed) |
| **Szybkość prototypowania** | Wolniejsza (wymaga dyscypliny funkcjonalnej) | Szybka (brak restrykcji funkcjonalnych) |
| **Wdrożenia produkcyjne** | Integracja z ekosystemem TensorFlow, Vertex AI | TorchServe, Triton, eksport do ONNX |
| **Główni użytkownicy** | DeepMind (Gemini), Anthropic (Claude) | Meta (Llama), OpenAI (GPT), Stability AI |

W praktyce najlepiej wybrać PyTorch, chyba że masz konkretne wymagania: dostęp do infrastruktury TPU, zapotrzebowanie na wyznaczanie gradientów dla pojedynczych przykładów (per-sample gradients) czy masowe skalowanie obliczeń na wielu maszynach równolegle.

### Obsługa liczb losowych w JAX

W JAX nie ma globalnego stanu generatora liczb losowych. Każda operacja losowa wymaga jawnego przekazania klucza stanu (PRNGKey):

```python
key = jax.random.PRNGKey(42)
key1, key2 = jax.random.split(key)
w = jax.random.normal(key1, shape=(784, 256))
```

Choć bywa to uciążliwe na etapie pisania kodu, gwarantuje absolutną powtarzalność obliczeń niezależnie od platformy sprzętowej czy podziału pracy na wiele GPU.

## Implementacja krok po kroku

### Krok 1: Przygotowanie danych

Wytrenujemy 3-warstwową sieć MLP na zbiorze MNIST przy użyciu bibliotek JAX i Optax. Sieć będzie składać się z 784 wejść, dwóch warstw ukrytych (256 i 128 neuronów) oraz 10 wyjść.

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

Napiszemy czystą funkcję zwracającą strukturę parametrów (pytree):

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

Zastosowaliśmy ręczną inicjalizację He. Klucze losowości generowane są poprzez podział klucza bazowego.

### Krok 3: Krok w przód (Forward Pass) i funkcja straty

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

Są to czyste funkcje. Stan nie jest modyfikowany ani zapisywany wewnątrz obiektów. Funkcja straty oblicza entropię krzyżową z log-softmaxem.

### Krok 4: Skompilowany krok treningowy (JIT)

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

Funkcja `jax.value_and_grad` wyznacza jednocześnie wartość straty oraz jej gradienty. Dekorator `@jax.jit` kompiluje te kroki przy użyciu XLA, eliminując narzut interpretera Pythona.

### Krok 5: Pętla uczenia

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
    print(f"Epoka {epoch + 1:2d} | Strata: {epoch_loss / n_batches:.4f} | "
          f"Dokładność Train: {train_acc:.4f} | Dokładność Test: {test_acc:.4f}")
```

Model osiąga około 97% dokładności na zbiorze testowym w 10 epok. Pierwsza epoka trwa zauważalnie dłużej z powodu narzutu na kompilację JIT, natomiast kolejne epoki wykonywane są błyskawicznie.

Zauważ, że nie stosujemy tu jawnego zerowania gradientów ani wywołań typu `.backward()`. Cała operacja aktualizacji wag zachodzi wewnątrz skompilowanej funkcji `train_step`.

## Wykorzystanie bibliotek Flax i Equinox

### Flax: Standard od Google

Flax przywraca strukturę zbliżoną do klas PyTorch, zachowując jednak jawne przekazywanie parametrów (stateless):

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
# Inicjalizacja parametrów
params = model.init(jax.random.PRNGKey(0), jnp.ones((1, 784)))
# Uruchomienie modelu
logits = model.apply(params, x_batch)
```

Sam obiekt modelu `model` nie przechowuje stanu parametrów `params`. Muszą być one jawnie przekazane przy użyciu metody `apply`.

### Equinox: Podejście oparte na strukturach Pytree

Equinox reprezentuje modele bezpośrednio jako drzewa Pytree:

```python
import equinox as eqx

model = eqx.nn.MLP(
    in_size=784, out_size=10, width_size=256, depth=2,
    activation=jax.nn.relu, key=jax.random.PRNGKey(0)
)
logits = model(x)
```

Dzięki temu model może być wywoływany bezpośrednio (jak w PyTorch), będąc jednocześnie w pełni kompatybilnym z transformacjami JAX.

### Optax: Komponowalne optymalizatory

Optax pozwala na łączenie kroków modyfikacji gradientów w czytelne łańcuchy (chains):

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

## Praktyczne wskazówki i instalacja

**Instalacja JAX:**

```bash
pip install jax jaxlib optax flax
```

Dla systemów z obsługą kart NVIDIA (CUDA):

```bash
pip install jax[cuda12]
```

Dla środowisk TPU (w chmurze Google Cloud):

```bash
pip install jax[tpu] -f https://storage.googleapis.com/jax-releases/libtpu_releases.html
```

**Optymalizacja wydajności:**
- Pierwsze wywołanie funkcji oznaczonej `@jax.jit` trwa dłużej ze względu na kompilację. Wykonaj jedno próbne uruchomienie (warmup) przed pomiarem wydajności (benchmarking).
- Unikaj pętli Pythona operujących na elementach tablic JAX wewnątrz funkcji kompilowanych za pomocą JIT. Korzystaj z `jax.lax.scan` lub `jax.lax.fori_loop`.
- Do debugowania wartości wewnątrz funkcji JIT używaj `jax.debug.print()`. Standardowa instrukcja `print()` wykona się wyłącznie raz (podczas kompilacji).
- Domyślnie JAX rezerwuje około 75% dostępnej pamięci GPU przy inicjalizacji. Aby to zmienić, ustaw zmienną środowiskową `XLA_PYTHON_CLIENT_PREALLOCATE=false`.

**Zapisywanie punktów kontrolnych (Checkpointing):**

```python
import orbax.checkpoint as ocp
checkpointer = ocp.PyTreeCheckpointer()
checkpointer.save('/tmp/model', params)
restored = checkpointer.restore('/tmp/model')
```

**Materiały powiązane z tą lekcją:**
- `outputs/prompt-jax-optimizer.md` – szablon monitu służący do konfiguracji optymalizatorów Optax w JAX.
- `outputs/skill-jax-patterns.md` – podręcznik najpopularniejszych wzorców funkcjonalnych w JAX.

## Zadania do samodzielnego wykonania

1. **Wdrożenie Dropoutu:** Dodaj warstwę Dropout do modelu MLP. Pamiętaj, że w JAX Dropout wymaga unikalnego klucza PRNGKey dla każdego kroku. Przekaż klucz przez funkcję forward i podziel go dla każdej warstwy Dropout. Porównaj wyniki treningu z regularyzacją i bez niej.
2. **Gradienty dla pojedynczych próbek (Per-sample gradients):** Użyj połączenia `jax.vmap` oraz `jax.grad`, aby obliczyć normy gradientów osobno dla każdego z 32 obrazów w partii MNIST. Zidentyfikuj przykłady generujące największe wartości gradientów i spróbuj wyjaśnić dlaczego.
3. **Generyczny krok w przód (Forward):** Zastąp ręcznie napisaną funkcję forward generyczną funkcją `mlp_forward(params, x)`, która obsługuje sieć o dowolnej liczbie warstw ukrytych. Wykorzystaj `jax.tree.leaves` do automatycznego odczytania głębokości struktury parametrów.
4. **Test wydajności JIT:** Zmierz czas wykonania 100 kroków uczenia z dekoratorem `@jax.jit` oraz bez niego. Jak duże przyspieszenie udało się uzyskać na Twoim sprzęcie? Ile czasu zajęła wstępna kompilacja kodu?
5. **Przycinanie gradientów w Optax:** Skonfiguruj optymalizator z przycinaniem gradientów za pomocą `optax.chain(optax.clip_by_global_norm(1.0), optax.adam(1e-3))`. Zwizualizuj normę gradientu w czasie treningu dla obu wariantów (z przycinaniem i bez) i przeanalizuj różnice.

## Słownik kluczowych pojęć

| Termin | Potoczne określenie | Co to dokładnie oznacza |
| :--- | :--- | :--- |
| **XLA (Accelerated Linear Algebra)** | „Silnik stojący za JAX” | Kompilator grafów obliczeniowych Google, optymalizujący operacje matematyczne i łączący je w zunifikowane jądra dla GPU/TPU |
| **JIT (Just-In-Time Compilation)** | „Kompilacja w locie” | Proces polegający na rejestracji operacji na abstrakcyjnych kształtach (śledzeniu) przy pierwszym uruchomieniu i kompilacji zoptymalizowanego kodu maszynowego |
| **Czysta funkcja (Pure Function)** | „Funkcja bez stanu i skutków ubocznych” | Funkcja, której wynik zależy wyłącznie od parametrów wejściowych i która nie modyfikuje żadnych stanów zewnętrznych ani zmiennych |
| **vmap (Vectorized Map)** | „Automatyczne wektoryzowanie partii” | Transformacja przekształcająca funkcję napisaną dla pojedynczego przykładu w wersję operującą na partii danych |
| **pmap (Parallel Map)** | „Równoległość sprzętowa” | Narzędzie rozdzielające obliczenia i partię danych na wiele fizycznych akceleratorów (GPU/TPU) jednocześnie |
| **Pytree** | „Struktura drzewiasta danych” | Zagnieżdżona struktura (np. słowniki słowników, listy krotek) zawierająca tablice JAX w swoich liściach |
| **Tracing (Śledzenie)** | „Budowanie wykresu obliczeń” | Proces, w którym JAX uruchamia funkcję na symbolicznych danych w celu stworzenia reprezentacji grafu operacji dla kompilatora XLA |
| **Różniczkowanie funkcjonalne** | `jax.grad()` | Wyznaczanie gradientów poprzez transformacje matematyczne samych definicji funkcji, a nie poprzez rejestrację ścieżki w obiektach tensorów |
| **Optax** | „Biblioteka optymalizacji” | Zestaw komponentów (m.in. Adam, SGD, przycinanie) pozwalających na elastyczne budowanie optymalizatorów poprzez łańcuchy transformacji |
| **Flax** | „Biblioteka warstw sieciowych” | Najpopularniejsza biblioteka Google ułatwiająca definicję struktur sieciowych w JAX przy zachowaniu zasad programowania funkcjonalnego |

## Literatura uzupełniająca

- *JAX Documentation* (https://jax.readthedocs.io/) – oficjalna dokumentacja projektu zawierająca szczegółowe poradniki dotyczące transformacji `grad`, `jit` i `vmap`.
- Bradbury i in., *„JAX: composable transformations of Python+NumPy programs”* (2018) – oryginalna praca naukowa przedstawiająca architekturę i założenia projektowe frameworka.
- *Flax Documentation* (https://flax.readthedocs.io/) – oficjalne źródło wiedzy na temat biblioteki Flax.
- Patrick Kidger, *„Equinox: neural networks in JAX via callable PyTrees and filtered transformations”* (2021) – praca opisująca alternatywne podejście do reprezentacji modeli w JAX.
- Colin Raffel, *„You Don't Know JAX”* (2020) – praktyczny, przystępny przewodnik omawiający najczęstsze błędy (gotchas) oraz wzorce projektowe w JAX.
