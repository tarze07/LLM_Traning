---

name: gradient-accumulation
description: Trenuj na efektywnej partii większej niż pamięć urządzenia, skalując straty w mikropartiach i uruchamiając optymalizator raz na okno.
version: 1.0.0
phase: 19
lesson: 46
tags: [training, batch-size, distributed, scaling]

---

## Kiedy używać

Efektywna partia to dźwignia, która wygładza gradient i dopasowuje harmonogram szybkości uczenia się. Jeśli nie możesz sobie na to pozwolić w jednym podaniu do przodu, oto przepis.

## Przepis

1. Wybierz `micro_batch` jako największy rozmiar mieszczący się w pamięci i obciążający akcelerator.
2. Wybierz `effective_batch` z harmonogramu szybkości uczenia się.
3. Ustaw `accum_steps = effective_batch // (micro_batch * world_size)` i upewnij się, że dzieli się równomiernie.
4. Na mikropartię: `loss = criterion(model(x), y) / accum_steps; loss.backward()`.
5. W przypadku mikrosów innych niż końcowe wprowadź `model.no_sync()`, aby pominąć redukcję wszystkich gradientów w DDP.
6. Po ostatniej mikropartii uruchom raz `optimizer.step()`. Zero gradientów przed następnym oknem.
7. Stan optymalizatora zmienia się raz na efektywną partię; harmonogram szybkości uczenia się zaznacza raz na efektywną partię.

## Rejestrowanie

Emituj mały rekord JSON na każdy efektywny krok z `samples_per_sec`, `median_step_ms`, `sync_calls`, `accum_steps`, `effective_batch`. Bez tego handel kosztami jest niewidoczny.

## Tryby awarii

- Zapominając o skalowaniu `/ accum_steps`: gradienty eksplodują o N.
- Krok w środku okna: dryf parametrów.
- Synchronizacja każdej mikropartii: połączenie sieciowe bez korzyści statystycznych.
- Łączenie tego z mieszaną precyzją nieskalowania: skaluj tylko nieskalowaną stratę.