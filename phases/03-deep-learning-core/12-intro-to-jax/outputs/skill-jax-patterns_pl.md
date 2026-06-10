---

name: skill-jax-patterns
description: Funkcjonalne wzorce programowania w JAX – kiedy i jak używać grad, jit, vmap i pmap
version: 1.0.0
phase: 3
lesson: 12
tags: [jax, functional-programming, autodiff, compilation, vectorization]

---

# Wzorce funkcjonalne JAX

JAX przekształca czyste funkcje. Każdy poniższy wzór opiera się na jednej zasadzie: napisz funkcję, która pobiera dane wejściowe i zwraca dane wyjściowe, bez żadnych skutków ubocznych. Następnie przekształć go.

## Cztery transformacje

### grad — Różniczkowanie funkcji

```python
grads = jax.grad(loss_fn)(params, x, y)
loss, grads = jax.value_and_grad(loss_fn)(params, x, y)
```

Użyj, gdy: potrzebujesz gradientów do optymalizacji.
Ograniczenie: funkcja musi zwracać skalar. W przypadku wyjść nieskalarnych użyj `jax.jacobian`.

### jit — Skompiluj funkcję

```python
fast_fn = jax.jit(f)
```

Użyj, gdy: funkcja zostanie wywołana więcej niż raz z danymi wejściowymi o tym samym kształcie.
Ograniczenie: brak przepływu sterowania w języku Python, który zależy od prześledzonych wartości. Użyj `jax.lax.cond` dla warunków, `jax.lax.scan` dla pętli.

### vmap — Wektoryzacja funkcji

```python
batch_fn = jax.vmap(f, in_axes=(None, 0))
```

Użyj, gdy: napisałeś funkcję dla jednego przykładu i potrzebujesz jej do pracy w partiach.
`in_axes` określa, która oś argumentu ma zostać przetworzona wsadowo. `None` oznacza brak wsadu (rozgłaszania).

### pmap — Równoległość między urządzeniami

```python
parallel_fn = jax.pmap(f, axis_name='devices')
```

Użyj, gdy: masz wiele procesorów graficznych/TPU i chcesz równoległości danych.
Wewnątrz tej funkcji średnie wartości `jax.lax.pmean(x, 'devices')` dla różnych urządzeń.

## Zasady kompozycji

Transformuje kompozycję. Kolejność ma znaczenie:

```python
per_example_grads = jax.jit(jax.vmap(jax.grad(loss_fn), in_axes=(None, 0, 0)))
```

Czytanie od prawej do lewej: weź gradient straty_fn, wektoryzuj przykłady, skompiluj wynik.

Obowiązujące kompozycje:
- `jit(grad(f))` - skompilowane obliczenia gradientu
- `jit(vmap(f))` - skompilowane obliczenia wsadowe
- `vmap(grad(f))` - gradienty według przykładu
- `pmap(jit(f))` - obliczenia kompilowane równolegle
- `grad(jit(f))` -- gradient skompilowanej funkcji (tak samo jak jit(grad(f)))

## Wzorzec zarządzania parametrami

Parametry JAX to pytrees (zagnieżdżone słowniki tablic):

```python
params = {
    'layer1': {'w': jnp.zeros((784, 256)), 'b': jnp.zeros(256)},
    'layer2': {'w': jnp.zeros((256, 10)),  'b': jnp.zeros(10)},
}
```

Zaktualizuj wszystkie parametry na raz:
```python
params = jax.tree.map(lambda p, g: p - lr * g, params, grads)
```

Parametry zliczania:
```python
n_params = sum(p.size for p in jax.tree.leaves(params))
```

## Zarządzanie kluczami PRNG

JAX wymaga jawnych kluczy losowych:

```python
key = jax.random.PRNGKey(0)
key, subkey = jax.random.split(key)
noise = jax.random.normal(subkey, shape)
```

W przypadku wielu losowych operacji podziel raz:
```python
keys = jax.random.split(key, n)
```

Nigdy nie używaj klucza ponownie. Zawsze dziel przed użyciem.

## Typowe błędy

1. **Mutowanie tablic w jit**: Tablice JAX są niezmienne. Użyj `x.at[i].set(v)` zamiast `x[i] = v`.

2. **Używanie Pythona do drukowania w jit**: `print` działa podczas śledzenia, a nie podczas wykonywania. Użyj `jax.debug.print("{}", x)`.

3. **Python if/for inside jit na śledzonych wartościach**: Użyj `jax.lax.cond`, `jax.lax.switch`, `jax.lax.scan`, `jax.lax.fori_loop`.

4. **Zapominanie o `.block_until_ready()`**: JAX używa wysyłania asynchronicznego. W celu przeprowadzenia testów porównawczych zadzwoń do `.block_until_ready()`, aby poczekać na faktyczne zakończenie.

5. **Ponowne użycie klawiszy PRNG**: Dwie operacje na tym samym kluczu dają te same „losowe” wartości. Zawsze dziel.

6. **Stan globalny w funkcjach z wahaniem**: Zmienne globalne są przechwytywane w czasie śledzenia. Zmiany po prześledzeniu są niewidoczne. Przekaż wszystko jako argumenty.

## Lista kontrolna decyzji

1. Czy funkcja jest wywoływana więcej niż raz? Dodaj `@jax.jit`.
2. Czy potrzebuje gradientów? Owiń za pomocą `jax.grad` lub `jax.value_and_grad`.
3. Czy przetwarza jeden przykład, ale masz partię? Owiń za pomocą `jax.vmap`.
4. Czy masz wiele urządzeń? Owiń `jax.pmap`.
5. Czy wykorzystuje losowość? Przeprowadź klucze PRNG jawnie.
6. Czy Python ma kontrolę nad wartościami tablicy? Zastąp prymitywami `jax.lax`.

## Kiedy używać JAX

Użyj JAX, gdy:
- Potrzebujesz gradientów dla każdego przykładu (prywatność różnicowa, informacje Fishera)
- Szkolisz się na TPU (JAX to natywny framework)
- Potrzebujesz pochodnych wyższego rzędu (Hesjanie, Jakobiani)
- Chcesz skompilować cały krok szkoleniowy do jednego jądra
- Twój zespół pracuje w Google DeepMind lub Anthropic

Użyj PyTorch, gdy:
- Chcesz największego ekosystemu (HuggingFace, torchvision, Lightning)
- Przedkładasz łatwość debugowania nad samą prędkość
- Wdrażasz na procesorach graficznych NVIDIA z TorchServe/Triton
- Zatrudniasz (istnieje więcej programistów PyTorch)
- Chcesz szybko iterować na nowych architekturach