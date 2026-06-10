---

name: skill-freeze-inspector
description: Raportuj, które parametry można wytrenować, które warstwy BatchNorm są w trybie ewaluacyjnym i czy optymalizator faktycznie zużywa parametry, które można wytrenować
version: 1.0.0
phase: 4
lesson: 5
tags: [computer-vision, transfer-learning, debugging, pytorch]

---

# Audytor stanów zamrożenia wag (Freeze Inspector)

Błędy w uczeniu transferowym (transfer learning) najczęściej kryją się w trzech miejscach: parametrach, które powinny zostać zamrożone, ale pozostały trenowalne; parametrach, które powinny być trenowalne, lecz są zamrożone; oraz w konfiguracji optymalizatorów utworzonych przed modyfikacją flag `requires_grad` parametrów. Ten moduł ułatwia jednoczesną detekcję wszystkich trzech typów błędów.

## Zastosowanie

- Bezpośrednio po modyfikacji flagi `requires_grad` dla podzbioru warstw sieci.
- Przed wywołaniem pętli treningowej dla procesu dostrajania (fine-tuning).
- Po wywołaniu funkcji `freeze_bn_stats` lub innych funkcji przełączających stan warstw BatchNorm.
- Gdy dokładność walidacyjna utrzymuje się na poziomie losowym i podejrzewasz, że optymalizator nie modyfikuje wag modelu.

## Dane wejściowe

- `model`: obiekt modelu w PyTorch (`nn.Module`).
- `optimizer`: obiekt optymalizatora przypisanego do treningu.
- Opcjonalny parametr `expected_frozen_prefixes`: lista przedrostków (prefiksów) nazw parametrów, które powinny być zamrożone (np. `["conv1", "bn1", "layer1"]`).

## Procedura audytu

1. **Weryfikacja parametrów (parameter loop)**: Dla każdego elementu `(name, param)`:
   - Sprawdź status flagi `requires_grad`.
   - Zapisz kształt (shape) oraz całkowitą liczbę parametrów (numel).

2. **Weryfikacja modułów (module loop)**: Dla każdego modułu w sieci:
   - Jeśli moduł jest warstwą BatchNorm, sprawdź, czy działa w trybie ewaluacji (`model.training == False` lub `m.training == False`) i czy jego parametry afiniczne (gamma i beta) są ustawione jako trenowalne.

3. **Weryfikacja powiązania optymalizatora**:
   - Pobierz zestaw unikalnych identyfikatorów `id(p)` dla parametrów przekazanych do optymalizatora.
   - Porównaj go z zestawem identyfikatorów `id(p)` wszystkich parametrów modelu posiadających flagę `requires_grad == True`.

4. **Detekcja czterech typów błędów**:
   - **leaked_train**: parametr ma flagę `requires_grad=True`, ale nie został przekazany do optymalizatora (gradienty są wyliczane w kroku wstecznym, lecz wagi nie podlegają aktualizacji).
   - **ghost_train**: parametr został przekazany do optymalizatora, ale ma flagę `requires_grad=False` (zasoby optymalizatora są marnowane na śledzenie nieaktywnego parametru).
   - **bn_mismatch**: niespójność konfiguracji warstwy BatchNorm. Występuje, gdy (a) warstwa BN działa w trybie treningowym (wylicza statystyki partii), lecz jej parametry afiniczne (`weight`, `bias`) są zamrożone, lub (b) warstwa BN działa w trybie ewaluacji (eval – zamrożone statystyki), lecz jej parametry afiniczne są trenowalne. Oba stany są niespójne metodologicznie i niemal zawsze oznaczają błąd implementacyjny.
   - **expected_vs_actual**: parametr pasujący do jednego z prefiksów z listy `expected_frozen_prefixes` jest oznaczony jako trenowalny (nie został zamrożony).

## Format raportu

```
[freeze-inspector]
  model trainable params: <liczba parametrów trenowalnych>
  model frozen params:    <liczba parametrów zamrożonych>
  batchnorm layers in eval mode: <liczba warstw BN w trybie eval>
  batchnorm layers in train mode: <liczba warstw BN w trybie train>

[optimizer coverage]
  trainable params fed to optimizer: <M> z <N>
  leaked_train: <lista nazw parametrów> (trenowalne, ale brak w optymalizatorze)
  ghost_train:  <lista nazw parametrów> (w optymalizatorze, ale zamrożone)

[bn audit]
  mismatched layers: <lista nazw warstw BatchNorm z niespójnością>

[expectations]
  expected_frozen_prefixes: <lista oczekiwanych prefiksów>
  violating params:         <lista parametrów naruszających oczekiwania>

[verdict]
  ok | <krótkie podsumowanie najpoważniejszego problemu w jednym zdaniu>
```

## Reguły

- Raportuj wyłącznie nazwy parametrów; nigdy nie wyświetlaj ich wartości liczbowych (wag).
- Sortuj listy parametrów alfabetycznie.
- Jeśli pokrycie parametrów w optymalizatorze wynosi 100% i nie wykryto niespójności, zwróć wynik `ok` i zakończ działanie.
- W przypadku wykrycia błędu `leaked_train` zawsze zalecaj ponowną inicjalizację (przebudowanie) obiektu optymalizatora po zmianie stanów zamrożenia wag.
- W przypadku wykrycia błędu `ghost_train` zalecaj usunięcie zoptymalizowanej grupy parametrów z optymalizatora lub zmianę flagi na `requires_grad=True`, jeśli dany parametr miał podlegać treningowi.
