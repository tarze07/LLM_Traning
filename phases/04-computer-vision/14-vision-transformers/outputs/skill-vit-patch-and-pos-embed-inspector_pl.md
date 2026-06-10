---

name: skill-vit-patch-and-pos-embed-inspector
description: Sprawdź, czy kształty osadzania łatek i osadzania pozycyjnego ViT odpowiadają oczekiwanej długości sekwencji modelu
version: 1.0.0
phase: 4
lesson: 14
tags: [vision-transformer, debugging, pytorch]

---

# Inspektor łat ViT i osadzania pozycyjnego

Najczęstszy błąd przenoszenia ViT: ładowanie punktu kontrolnego wstępnie wytrenowanego w rozdzielczości 224x224 do modelu skonfigurowanego dla rozdzielczości 384x384 (lub odwrotnie). Osadzanie pozycyjne ma niewłaściwą długość sekwencji i model po cichu generuje śmieci.

## Kiedy używać

- Dostrajanie wstępnie wyszkolonego ViT w rozdzielczości innej niż domyślna.
- Audyt, dlaczego port wagi pomiędzy ViT-B/16 i ViT-B/32 nie działa; inspektor oznaczy niezgodność rozmiaru poprawki, aby osoba dzwoniąca wiedziała, że ​​należy zamienić architektury, zamiast wymuszać port.
- Debugowanie ViT, który ładuje się bez błędów, ale słabo się trenuje.

## Wejścia

- `model`: instancja ViT `nn.Module`.
- `expected_image_size`: wys. x szer., który model zobaczy w produkcji.
- `patch_size`: oczekiwany rozmiar poprawki.

## Kroki

1. Znajdź łatkę osadzającą conv wewnątrz modelu. Zgłoś jego `kernel_size`, `stride`, `in_channels`, `out_channels`.
2. Oblicz oczekiwaną liczbę poprawek. Dla obrazu kwadratowego: `(image_size / patch_size)^2`. Dla prostokąta: `(H / patch_size) * (W / patch_size)`. Wymagaj `H % patch_size == 0` i `W % patch_size == 0`; w przeciwnym razie zgłoś i odmów.
3. Zlokalizuj wyuczone osadzenie pozycyjne. Zgłoś jego kształt `(1, N, dim)`.
4. Porównaj `N` z `num_patches + 1` (z CLS) lub `num_patches` (bez CLS). Niezgodność oznacza, że ​​punkt kontrolny został wstępnie przeszkolony w innej rozdzielczości lub rozmiarze poprawki.
5. Sprawdź, czy `out_channels` konw. łaty jest równe `dim` osadzania pozycyjnego.
6. Jeśli model ma interpolować osadzania pozycyjne dla nowych rozdzielczości, sprawdź, czy istnieje narzędzie do interpolacji (większość ViT `timm` robi to automatycznie poprzez `resize_pos_embed`).

## Zgłoś

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

## Zasady

- Nigdy nie interpoluj po cichu bez ostrzeżenia; wydobyć akcję, aby użytkownik wiedział, że wstępnie wytrenowana struktura pozycyjna mogła się przesunąć.
- Jeśli rozmiar_łatki jest niezgodny, odmów zalecania interpolacji - zamień na poprawną architekturę.
- Nie próbuj mocować modelu na miejscu; zgłaszać i sugerować.