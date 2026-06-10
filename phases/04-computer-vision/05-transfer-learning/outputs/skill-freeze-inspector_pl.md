---

name: skill-freeze-inspector
description: Raportuj, które parametry można wytrenować, które warstwy BatchNorm są w trybie ewaluacyjnym i czy optymalizator faktycznie zużywa parametry, które można wytrenować
version: 1.0.0
phase: 4
lesson: 5
tags: [computer-vision, transfer-learning, debugging, pytorch]

---

# Inspektor zamrożenia

Błędy związane z uczeniem się transferu kryją się w trzech miejscach: parametry, które powinny zostać zamrożone, ale tak się nie dzieje, parametry, które powinny dać się wytrenować, ale nie są, oraz optymalizatory, które zostały zbudowane przed zmianą stanu zamrożenia. Ta umiejętność ujawnia wszystkie trzy w jednym przejściu.

## Kiedy używać

- Zaraz po ustawieniu `requires_grad` na podzbiorze parametrów.
- Przed pierwszym krokiem treningowym biegu wytrenowanego.
- Po wywołaniu `freeze_bn_stats` lub dowolnego pomocnika, który przełącza tryb BN.
- Kiedy dokładność Val jest przypadkowa i podejrzewasz, że tak naprawdę nic nie jest treningiem.

## Wejścia

- `model`: PyTorch `nn.Module`.
- `optimizer`: optymalizator, który będzie używany do szkolenia.
- Opcjonalnie `expected_frozen_prefixes`: lista przedrostków nazw parametrów, które powinny zostać zamrożone (np. `["conv1", "bn1", "layer1"]`).

## Kroki

1. **Parametry spaceru.** Dla każdego `(name, param)`:
   - zapisz `requires_grad`
   - zapisz `shape` i `numel`

2. **Moduły spaceru.** Dla każdego modułu:
   - jeśli jest to BatchNorm, zapisz, czy jest w trybie eval i czy można wytrenować jego parametry afiniczne.

3. **Sprawdź optymalizator.** Dla każdej grupy parametrów:
   - spłaszczyć `params` w zestaw `id(p)`.
   - porównaj z zestawem wszystkich `id(p)` dla parametrów, gdzie `requires_grad == True`.

4. **Wykryj cztery tryby awarii:**
   - `leaked_train`: parametr ma `requires_grad=True`, ale nie pojawia się w optymalizatorze (gradient jest obliczany, ale nigdy nie jest stosowany).
   - `ghost_train`: parametr pojawia się w optymalizatorze, ale ma `requires_grad=False` (stan optymalizatora jest zmarnowany; może również powodować błędy, jeśli później ponownie włączysz require_grad).
   - `bn_mismatch`: albo (a) warstwa BN jest w trybie uczenia (gromadzi bieżące statystyki), podczas gdy jej parametry afiniczne (`weight`, `bias`) są zablokowane, lub (b) warstwa BN jest w trybie eval (zamrożone statystyki), podczas gdy jej parametry afiniczne można trenować. Obydwa stany są niespójne i prawie zawsze stanowią błąd.
   - `expected_vs_actual`: każdy przedrostek wymieniony w `expected_frozen_prefixes` nadal posiada parametr, który można wytrenować.

## Zgłoś

```
[freeze-inspector]
  model trainable params: <N>
  model frozen params:    <N>
  batchnorm layers in eval mode: <count>
  batchnorm layers in train mode: <count>

[optimizer coverage]
  trainable params fed to optimizer: <M> of <N>
  leaked_train: <list of names> (trainable but not in optimizer)
  ghost_train:  <list of names> (in optimizer but frozen)

[bn audit]
  mismatched layers: <list of names>

[expectations]
  expected_frozen_prefixes: <...>
  violating params:         <list>

[verdict]
  ok | <one-line summary of the most severe issue>
```

## Zasady

- Tylko nazwy parametrów raportu; nigdy nie drukuj samych ciężarów.
- Sortuj każdą listę alfabetycznie według nazwy parametru.
- Jeśli pokrycie optymalizatora wynosi 100% i nie ma żadnych niezgodności, zwróć `ok` i zatrzymaj.
- W przypadku `leaked_train` zawsze zalecaj przebudowę optymalizatora po zmianie stanu zamrożenia.
- W przypadku `ghost_train` zalecamy usunięcie grupy parametrów lub ustawienie `requires_grad=True`, jeśli zamiarem było jej wyszkolenie.