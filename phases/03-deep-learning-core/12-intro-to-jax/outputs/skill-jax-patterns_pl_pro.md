---

name: skill-jax-patterns
description: Funkcjonalne wzorce programowania w JAX – kiedy i jak używać grad, jit, vmap i pmap
version: 1.0.0
phase: 3
lesson: 12
tags: [jax, functional-programming, autodiff, compilation, vectorization]

---

# Wzorce funkcjonalne JAX

JAX opiera się na transformacjach czystych funkcji. Każdy z poniższych wzorców bazuje na jednej wspólnej zasadzie: napisz funkcję, która przyjmuje argumenty i zwraca wynik bez wywoływania jakichkolwiek efektów ubocznych, a następnie zastosuj do niej wybraną transformację.

## Cztery podstawowe transformacje

### grad – Różniczkowanie funkcji

```python
grads = jax.grad(loss_fn)(params, x, y)
loss, grads = jax.value_and_grad(loss_fn)(params, x, y)
```

**Zastosowanie:** Gdy potrzebujesz gradientów do przeprowadzenia procesu optymalizacji.  
**Ograniczenia:** Różniczkowana funkcja musi zwracać wartość skalarną. Dla wyjść wielowymiarowych (wektorów lub macierzy) użyj `jax.jacobian`.

### jit – Kompilacja funkcji

```python
fast_fn = jax.jit(f)
```

**Zastosowanie:** Gdy funkcja będzie uruchamiana wielokrotnie z danymi wejściowymi o stałym kształcie (wymiarach).  
**Ograniczenia:** Wewnątrz kompilowanej funkcji nie można stosować instrukcji sterujących Pythona (`if`, `for`, `while`) zależnych od dynamicznych, śledzonych wartości tablic. Używaj `jax.lax.cond` do warunków oraz `jax.lax.scan` do pętli.

### vmap – Automatyczna wektoryzacja

```python
batch_fn = jax.vmap(f, in_axes=(None, 0))
```

**Zastosowanie:** Gdy posiadasz funkcję napisaną dla pojedynczego przykładu, a chcesz przetwarzać dane w partiach (batches).  
`in_axes` określa, wzdłuż których osi poszczególnych argumentów wejściowych ma nastąpić wektoryzacja. Wartość `None` oznacza brak wektoryzacji danego argumentu (jest on przekazywany w całości do każdego przykładu).

### pmap – Równoległość sprzętowa

```python
parallel_fn = jax.pmap(f, axis_name='devices')
```

**Zastosowanie:** Gdy dysponujesz wieloma akceleratorami (GPU/TPU) i chcesz zaimplementować równoległe przetwarzanie danych (data parallelism).  
Wewnątrz tak zdefiniowanej funkcji możesz wywołać `jax.lax.pmean(x, 'devices')`, aby zsynchronizować i uśrednić gradienty pomiędzy urządzeniami.

## Reguły kompozycji transformacji

Transformacje JAX można swobodnie ze sobą łączyć. Kolejność ich stosowania ma kluczowe znaczenie:

```python
per_example_grads = jax.jit(jax.vmap(jax.grad(loss_fn), in_axes=(None, 0, 0)))
```

Czytając od prawej do lewej: wyznacz gradient funkcji straty (`loss_fn`), zwektoryzuj dla kolejnych przykładów w partii (`vmap`), a następnie skompiluj cały proces (`jit`).

Zalecane kombinacje transformacji:
- `jit(grad(f))` – skompilowane wyznaczanie gradientu.
- `jit(vmap(f))` – skompilowane przetwarzanie wsadowe.
- `vmap(grad(f))` – gradienty wyznaczane osobno dla każdej próbki (per-sample gradients).
- `pmap(jit(f))` – skompilowane obliczenia uruchamiane równolegle na wielu urządzeniach.
- `grad(jit(f))` – gradient skompilowanej funkcji (działa tożsamo jak `jit(grad(f))`).

## Wzorzec zarządzania parametrami

Parametry modelu w JAX są zorganizowane w drzewa Pytree (zagnieżdżone słowniki i listy tablic):

```python
params = {
    'layer1': {'w': jnp.zeros((784, 256)), 'b': jnp.zeros(256)},
    'layer2': {'w': jnp.zeros((256, 10)),  'b': jnp.zeros(10)},
}
```

Aktualizacja wszystkich parametrów jednocześnie:
```python
params = jax.tree.map(lambda p, g: p - lr * g, params, grads)
```

Zliczanie wszystkich parametrów modelu:
```python
n_params = sum(p.size for p in jax.tree.leaves(params))
```

## Zarządzanie kluczami PRNG

JAX wymaga jawnego przekazywania i kontrolowania kluczy stanu losowości:

```python
key = jax.random.PRNGKey(0)
key, subkey = jax.random.split(key)
noise = jax.random.normal(subkey, shape)
```

W przypadku zapotrzebowania na wiele losowych operacji, podziel klucz na odpowiednią liczbę podkluczy:
```python
keys = jax.random.split(key, n)
```

Nigdy nie używaj tego samego klucza wielokrotnie. Zawsze wykonuj podział (`split`) przed kolejną losową operacją.

## Typowe błędy i pułapki (Gotchas)

1. **Mutowanie tablic wewnątrz funkcji JIT**: Tablice JAX są niezmienne (immutable). Używaj składni `x.at[i].set(v)` zamiast przypisania `x[i] = v`.
2. **Używanie standardowych instrukcji print wewnątrz JIT**: Instrukcja `print()` wykona się wyłącznie raz – podczas budowania grafu (śledzenia). Do wypisywania wartości w czasie rzeczywistym używaj `jax.debug.print("{}", x)`.
3. **Instrukcje warunkowe oraz pętle Pythona w JIT operujące na wartościach dynamicznych**: Tradycyjne `if` oraz `for` oparte na wartościach tablic JAX zakończą się błędem kompilacji. Zastąp je konstrukcjami `jax.lax.cond`, `jax.lax.switch`, `jax.lax.scan` lub `jax.lax.fori_loop`.
4. **Ignorowanie asynchroniczności i brak block_until_ready()**: JAX wysyła operacje na urządzenie asynchronicznie. Robiąc testy wydajności (benchmarking), pamiętaj o wywołaniu `.block_until_ready()` na wyjściu funkcji, aby wymusić zakończenie obliczeń przed zatrzymaniem stopera.
5. **Ponowne użycie tego samego klucza PRNG**: Generowanie liczb losowych z tym samym kluczem PRNG da dokładnie te same wartości pseudolosowe. Zawsze dbaj o split klucza.
6. **Próba użycia stanu globalnego w śledzonych funkcjach**: Zmienne globalne są odczytywane i utrwalane w momencie kompilacji (śledzenia). Ich późniejsze modyfikacje w Pythonie nie zostaną uwzględnione przez skompilowane jądro. Wszystkie zmienne wejściowe przekazuj jako jawne argumenty funkcji.

## Lista kontrolna / Schemat decyzyjny

1. Czy funkcja będzie uruchamiana wielokrotnie? Zastosuj `@jax.jit`.
2. Czy musisz obliczyć gradienty? Użyj `jax.grad` lub `jax.value_and_grad`.
3. Czy funkcja operuje na pojedynczym przykładzie, a chcesz przetworzyć całą partię? Użyj `jax.vmap`.
4. Czy dysponujesz wieloma GPU/TPU i chcesz podzielić na nie dane? Użyj `jax.pmap`.
5. Czy w obliczeniach występuje losowość? Przekazuj i dziel klucze PRNG jawnie.
6. Czy przepływ sterowania zależy od wartości tablic? Zastąp konstrukcje Pythona prymitywami z `jax.lax`.

## Kiedy warto wybrać JAX

Wybierz JAX, jeśli:
- Potrzebujesz gradientu osobno dla każdego przykładu (np. w prywatności różnicowej - DP-SGD, szacowaniu macierzy informacji Fishera).
- Główną infrastrukturą sprzętową w Twoim projekcie są układy TPU (JAX jest dla nich natywnym frameworkiem).
- Obliczenia wymagają pochodnych wyższego rzędu (hesjany, jakobiany, optymalizacja gradientowa wyższego poziomu).
- Chcesz skompilować całą pętlę uczenia w jedno wysoce zoptymalizowane jądro obliczeniowe.
- Twój zespół badawczy pracuje w strukturach takich jak Google DeepMind lub Anthropic.

## Kiedy lepiej wybrać PyTorch

Wybierz PyTorch, jeśli:
- Chcesz korzystać z najbogatszego ekosystemu narzędzi (HuggingFace, torchvision, PyTorch Lightning, timm).
- Priorytetem jest dla Ciebie łatwość debugowania kodu linia po linii, a nie maksymalna prędkość kompilacji.
- Wdrażasz modele produkcyjnie na kartach graficznych NVIDIA przy użyciu TorchServe lub Triton Inference Server.
- Budujesz zespół (na rynku jest znacznie więcej inżynierów znających PyTorch).
- Chcesz szybko i elastycznie eksperymentować z nowymi architekturami sieci bez narzuconej dyscypliny funkcjonalnej.
