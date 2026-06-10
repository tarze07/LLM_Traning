---

name: skill-vit-patch-and-pos-embed-inspector
description: Narzędzie do sprawdzania zgodności wymiarów rzutowania patchów oraz wektorów kodowania pozycyjnego ViT z docelową rozdzielczością obrazu
version: 1.0.0
phase: 4
lesson: 14
tags: [vision-transformer, debugging, pytorch]

---

# Inspektor rzutowania patchów i kodowania pozycyjnego ViT

Najczęstszy błąd podczas migracji modeli ViT: wczytanie punktu kontrolnego (checkpointa) pre-trenowanego w rozdzielczości 224x224 do modelu skonfigurowanego dla rozdzielczości 384x384 (lub odwrotnie). W takim przypadku wektor kodowania pozycyjnego ma niepoprawną długość, co sprawia, że model nie zgłasza błędu kodu, lecz generuje bezużyteczne wyniki (silent bug).

## Zastosowanie

- Dostrajanie (fine-tuning) pre-trenowanego modelu ViT w rozdzielczości innej niż domyślna rozdzielczość oryginalna.
- Weryfikacja problemów z migracją wag pomiędzy wersjami ViT-B/16 a ViT-B/32; skrypt zasygnalizuje niedopasowanie rozmiaru patcha, co wskazuje na konieczność zmiany architektury docelowej.
- Diagnozowanie modeli ViT, które wczytują się poprawnie i bez borrów (błędów), lecz proces ich uczenia nie przynosi oczekiwanych rezultatów.

## Dane wejściowe

- `model`: instancja modelu ViT (`nn.Module`).
- `expected_image_size`: docelowa rozdzielczość obrazu (wysokość x szerokość) w środowisku produkcyjnym.
- `patch_size`: oczekiwany rozmiar patcha.

## Etapy weryfikacji

1. Zlokalizuj warstwę splotową realizującą rzutowanie patchów (patch embedding conv) w strukturze modelu. Odczytaj jej parametry: `kernel_size`, `stride`, `in_channels` oraz `out_channels`.
2. Oblicz oczekiwaną liczbę patchów. Dla obrazów kwadratowych: `(image_size / patch_size)^2`. Dla obrazów prostokątnych: `(H / patch_size) * (W / patch_size)`. Wymagaj pełnej podzielności: `H % patch_size == 0` oraz `W % patch_size == 0` (w przeciwnym razie zgłoś błąd i przerwij procedurę).
3. Zidentyfikuj tensor wyuczonego kodowania pozycyjnego (`pos_embed`) i sprawdź jego wymiary: `(1, N, dim)`.
4. Porównaj wartość `N` z oczekiwaną liczbą tokenów: `num_patches + 1` (jeśli stosowany jest token `[CLS]`) lub `num_patches` (bez tokena klasy). Dowolne niedopasowanie wskazuje, że punkt kontrolny (checkpoint) pochodzi z modelu o innej rozdzielczości wejściowej lub innym rozmiarze patcha.
5. Upewnij się, że liczba kanałów wyjściowych (`out_channels`) splotu rzutującego jest równa wymiarowi cech (`dim`) kodowania pozycyjnego.
6. Jeśli docelowa rozdzielczość różni się od oryginalnej, zweryfikuj dostępność funkcji do interpolacji wektorów pozycyjnych (np. w modelach z biblioteki `timm` odbywa się to automatycznie za pomocą funkcji `resize_pos_embed`).

## Format raportu

```
[vit-inspector]
  image_size:         HxW
  patch_size:         <int>
  num_patches (computed): <int>
  patch_conv:         k=<int>  s=<int>  in=<int>  out=<int>
  pos_embed shape:    (1, N, dim)
  has CLS token:      yes | no
  pos_embed N:        <int>    expected: <int>
  verdict:            ok | mismatch

[if mismatch]
  action:  reinitialise pos_embed for new sequence length
  tool:    timm.models.vision_transformer.resize_pos_embed
```

## Reguły

- Nigdy nie wykonuj interpolacji automatycznie i bez powiadomienia; zawsze poinformuj użytkownika o tej operacji, ponieważ zaburza to oryginalną przestrzenną strukturę nauczoną przez model.
- Jeżeli niedopasowanie dotyczy rozmiaru patcha (patch_size), nie zalecaj interpolacji – w tym przypadku jedynym rozwiązaniem jest zmiana modelu na właściwą architekturę.
- Nie modyfikuj wag modelu bezpośrednio w kodzie inspektora; ogranicz się do analizy, raportowania i sugerowania właściwych rozwiązań.
