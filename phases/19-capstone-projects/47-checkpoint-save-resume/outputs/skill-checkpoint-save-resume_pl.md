---

name: checkpoint-save-resume
description: Atomowe, podzielone punkty kontrolne z pełnym przechwytywaniem RNG, dzięki czemu zabita seria zostaje wznowiona w połowie epoki z tą samą trajektorią strat.
version: 1.0.0
phase: 19
lesson: 47
tags: [training, durability, resume, sharded-state]

---

## Kiedy używać

Każde szkolenie trwa dłużej niż limit zegara ściennego klastra, każde uruchomienie, które musi przetrwać ponowne uruchomienie węzła, każdy model zbyt duży dla pojedynczego ładunku.

## Kształt ładunku

```python
{
  "schema": "ckpt.v1",
  "model": model.state_dict(),
  "optimizer": opt.state_dict(),
  "scheduler": sched.state_dict(),
  "state": {"step": int, "epoch": int, "batch_in_epoch": int, "losses": [float, ...]},
  "rng": {"python": ..., "numpy": ..., "torch_cpu": ..., "torch_cuda": ...},
  "wall_saved_at": time.time(),
}
```

## Zapis atomowy

1. Zapisz ładunek w unikalnym pliku tymczasowym w tym samym katalogu co element docelowy.
2. `os.replace(tmp, target)` do zamiany atomowej.
3. Nigdy nie pisz bezpośrednio pod nazwę docelową.

## Układ podzielony na fragmenty

- `model.shard-NNN.pt` na fragment, działanie okrężne na kluczach lub podzielone według grupy parametrów.
- `meta.pt` zawiera optymalizator, harmonogram, stan pociągu, RNG i manifest fragmentu.
- `index.json` przenosi `sha256` dla każdego odłamka i dla `meta.pt`.
- Loader weryfikuje każdy skrót przed połączeniem.

## CV ze połowy epoki

- Zapisz `(epoch, batch_in_epoch)` obok `step`.
- Przywróć stan RNG sprzed pierwszej partii wznowionej epoki.
- Przewiń generator do przodu w przypadku zużytych partii.

## Tryby awarii

- Zmiana nazwy na różnych urządzeniach: nie jest atomowa, utraci poprzedni plik. Umieść temp w tym samym katalogu.
- Zapominanie o RNG: wznowiona strata odbiega od wartości wyjściowej. Uruchom asercję demo.
- Zapominanie o stanie optymalizatora: następny krok się zmienia. Wyskakuje ta sama różnica.
- Przycinanie złego punktu kontrolnego: zachowaj ostatnie K i najlepiej.