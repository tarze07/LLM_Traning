---

name: skill-residual-block-reviewer
description: Przejrzyj blok resztkowy PyTorch pod kątem poprawności pomijania połączenia, rozmieszczenia BN, kolejności aktywacji i wyrównania kształtu
version: 1.0.0
phase: 4
lesson: 3
tags: [computer-vision, resnet, code-review, pytorch]

---

# Recenzent pozostałych bloków

Ukierunkowany recenzent dowolnego PyTorch `nn.Module`, który twierdzi, że implementuje blok resztkowy. Wychwytuje cztery błędy, które odpowiadają za prawie każde zepsute przepisanie ResNet.

## Kiedy używać

- Ktoś napisał niestandardowy BasicBlock lub wąskie gardło i strata wynosi NaN lub dokładność została zablokowana.
- Przenosisz blok z jednego frameworka do drugiego i chcesz sprawdzić równoważność.
- Przeglądasz PR, który zmienia wewnętrzne elementy ResNet (wstępna aktywacja, wyciskanie-ekscytowanie, wygładzanie).
— Model jest dostarczany prawidłowo w przypadku danych wejściowych o rozmiarze CIFAR, ale ulega awarii przy rozdzielczości ImageNet z powodu nieprawidłowego skrótu.

## Wejścia

- Definicja klasy PyTorch jako tekst źródłowy lub ścieżka do importu.
- Opcjonalnie `variant`: `basic` | `bottleneck` | `preact` | `seblock`.

## Cztery czeki

### 1. Wyrównanie kształtu skrótu

W przypadku dowolnego bloku z `stride != 1` lub `in_channels != out_channels` ścieżka skrótu **musi** być modułem dopasowującym kształt — zazwyczaj konwersja 1x1 plus BN. W tym przypadku goły `nn.Identity()` jest gwarantowanym błędem niedopasowania kształtu w czasie przesyłania.

Diagnostyka:
```
[shortcut]
  detected:  nn.Identity | 1x1 Conv + BN | 1x1 Conv + BN + ReLU | other
  required:  shape-matching Conv if (stride != 1 or in_c != out_c) else Identity
  verdict:   ok | wrong | unnecessarily heavy
```

### 2. Umiejscowienie BN względem dodatku

Dodanie `out + shortcut(x)` musi nastąpić **przed** ostatecznym ReLU (po aktywacji, oryginalny ResNet) lub końcowy ReLU musi być całkowicie nieobecny (przed aktywacją ResNet v2). Blok, który stosuje ReLU w głównej gałęzi, a następnie dodaje surowy skrót, tworzy asymetryczny zakres aktywacji, który szkodzi treningowi.

Diagnostyka:
```
[activation order]
  pattern:  post-act (conv-BN-ReLU-conv-BN-add-ReLU) | pre-act (BN-ReLU-conv-BN-ReLU-conv-add) | other
  verdict:  ok | suspect
```

### 3. Odchylenie w warstwach konw

Konwersje, po których następuje natychmiast BatchNorm, powinny mieć `bias=False`. Wersja beta BN już parametryzuje odchylenie, więc dodatkowe odchylenie konw. marnuje parametry i może spowolnić zbieżność.

Diagnostyka:
```
[bias]
  convs with BN and bias=True: <count>
  recommended fix: set bias=False on those layers
```

### 4. Lokalne ReLU i autograd

`nn.ReLU(inplace=True)` na tensorze, który zostanie dodany do skrótu, zastępuje wartości, które mogą być nadal potrzebne do dodania pozostałości. Oznacz dowolny `inplace=True`, po którym nie następuje warstwa generująca nowy tensor przed dodaniem.

Diagnostyka:
```
[in-place]
  risky inplace ops: <list>
  fix: inplace=False before the residual add
```

## Zgłoś

```
[block-review]
  variant:       basic | bottleneck | preact | se | other
  shortcut:      ok | wrong | heavy
  activation:    ok | suspect
  bias-bn:       ok | <N> convs need bias=False
  in-place:      ok | <N> risky ops
  summary:       one sentence
```

## Zasady

- Nie przepisuj bloku. Tylko zgłoś.
- Jeśli blok jest prawidłowy, powiedz wszędzie `ok` i przestań. Żadnych sugestii.
- Jeśli wiele rzeczy jest nie tak, wypisz je w powyższej kolejności (najpierw skrót, ponieważ jest to najczęstsza przyczyna awarii).
- Nigdy nie oznaczaj celowej aktywacji wstępnej lub wariantu wywołania ściśnięcia jako nieprawidłowego, jeśli określił to użytkownik.