---

name: skill-residual-block-reviewer
description: Przejrzyj blok resztkowy PyTorch pod kątem poprawności pomijania połączenia, rozmieszczenia BN, kolejności aktywacji i wyrównania kształtu
version: 1.0.0
phase: 4
lesson: 3
tags: [computer-vision, resnet, code-review, pytorch]

---

# Audytor bloków resztkowych (Residual Blocks)

Dedykowane narzędzie do weryfikacji poprawności implementacji dowolnego modułu `nn.Module` w PyTorch reprezentującego blok resztkowy. Pozwala na wykrycie czterech najczęstszych błędów popełnianych podczas implementacji architektury ResNet.

## Zastosowanie

- Niestandardowy blok resztkowy (BasicBlock lub Bottleneck) powoduje generowanie wartości NaN lub dokładność modelu zatrzymała się na niskim poziomie.
- Kod bloku jest przenoszony między różnymi frameworkami i konieczne jest zweryfikowanie poprawności zachowania.
- Przeprowadzasz przegląd kodu (PR), który modyfikuje strukturę ResNetu (np. wprowadzenie pre-activation, Squeeze-and-Excitation (SE) lub modyfikację downsamplingu).
- Model działa poprawnie na danych o wymiarach CIFAR, ale zgłasza błąd podczas przetwarzania obrazów ImageNet z powodu niedopasowania wymiarów w połączeniu skrótowym (shortcut).

## Dane wejściowe

- Kod źródłowy klasy w PyTorch lub ścieżka do jej importu.
- Opcjonalny parametr `variant`: `basic` | `bottleneck` | `preact` | `seblock`.

## Cztery etapy weryfikacji

### 1. Dopasowanie wymiarów połączenia skrótowego (shortcut)

Dla dowolnego bloku z krokiem `stride != 1` lub `in_channels != out_channels` ścieżka omijająca **musi** zawierać moduł dopasowujący wymiary przestrzenne i kanały (zazwyczaj konwolucja 1x1 połączona z BatchNorm). Zastosowanie w takich przypadkach samego `nn.Identity()` jest gwarantowanym źródłem błędu niezgodności wymiarów (shape mismatch) w kroku w przód (forward pass).

Format diagnostyczny:
```
[shortcut]
  detected:  nn.Identity | 1x1 Conv + BN | 1x1 Conv + BN + ReLU | inny
  required:  dopasowujący wymiary Conv (jeśli stride != 1 lub in_c != out_c), w przeciwnym razie Identity
  verdict:   ok | błąd | niepotrzebnie obciążony obliczeniowo
```

### 2. Umiejscowienie BatchNorm i operacji dodawania

Dodawanie wartości `out + shortcut(x)` musi nastąpić przed ostateczną aktywacją ReLU (tryb post-activation, oryginalny ResNet) lub aktywacja ReLU musi znajdować się przed warstwą konwolucyjną (tryb pre-activation, ResNet v2). Implementacja, która aplikuje ReLU w głównej gałęzi, a następnie dodaje surową, nieprzetworzoną wartość ze ścieżki omijającej, powoduje zaburzenie przepływu aktywacji i utrudnia trening.

Format diagnostyczny:
```
[activation order]
  pattern:  post-act (conv-BN-ReLU-conv-BN-add-ReLU) | pre-act (BN-ReLU-conv-BN-ReLU-conv-add) | inny
  verdict:  ok | podejrzany
```

### 3. Parametr bias w warstwach konwolucyjnych

Warstwy konwolucyjne, za którymi bezpośrednio znajduje się BatchNorm, powinny mieć ustawioną wartość `bias=False`. Parametr beta warstwy BatchNorm pełni już funkcję biasu, więc włączenie go w konwolucji powoduje nadmiarowość parametrów i spowalnia uczenie.

Format diagnostyczny:
```
[bias]
  liczba warstw conv z BN i bias=True: <wartość>
  rekomendowane rozwiązanie: ustaw bias=False w tych warstwach
```

### 4. Funkcja ReLU modyfikująca tensor w miejscu (in-place) a autograd

Zastosowanie `nn.ReLU(inplace=True)` na tensorze, który ma zostać dodany do ścieżki omijającej (shortcut), modyfikuje jego wartości w miejscu, co może zakłócić wyznaczanie pochodnych w kroku wstecz. Zgłoś ostrzeżenie dla każdej operacji in-place wykonywanej bezpośrednio przed sumowaniem.

Format diagnostyczny:
```
[in-place]
  ryzykowne operacje inplace: <lista>
  rozwiązanie: ustaw inplace=False przed dodawaniem wartości resztkowej (residual add)
```

## Format raportu

```
[block-review]
  variant:       basic | bottleneck | preact | se | inny
  shortcut:      ok | błąd | zbyt obciążony
  activation:    ok | podejrzany
  bias-bn:       ok | <N> warstw conv wymaga bias=False
  in-place:      ok | <N> ryzykownych operacji
  summary:       [podsumowanie w jednym zdaniu]
```

## Reguły

- Nie poprawiaj ani nie przepisuj kodu bloku. Przedstaw wyłącznie raport diagnostyczny.
- Jeśli struktura bloku jest w pełni poprawna, oznacz każdy punkt jako `ok` i zakończ analizę bez podawania dodatkowych sugestii.
- W przypadku wykrycia wielu nieprawidłowości, opisz je w powyższej kolejności (zaczynając od połączenia skrótowego, jako najczęstszego źródła błędów).
- Nigdy nie oznaczaj świadomie zaimplementowanych wariantów pre-activation lub modułów Squeeze-and-Excitation (SE) jako niepoprawnych, jeśli użytkownik jawnie wskazał taki wariant architektury.
