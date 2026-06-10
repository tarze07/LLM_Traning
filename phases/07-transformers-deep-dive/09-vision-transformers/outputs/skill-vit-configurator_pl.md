---

name: vit-configurator
description: Wybierz wariant ViT, rozmiar poprawki i źródło wstępnego szkolenia dla nowego zadania związanego z wizją.
version: 1.0.0
phase: 7
lesson: 9
tags: [transformers, vit, vision]

---

Biorąc pod uwagę zadanie wizyjne (klasyfikacja/segmentacja/wykrywanie/wyszukiwanie), rozdzielczość obrazu, rozmiar zbioru danych (oznaczony + nieoznaczony) i cel wdrożenia, wynik:

1. Kręgosłup. Jeden z: DINOv2 ViT-L/14 (domyślny do wyszukiwania/klasyfikacji), koder SAM 3 (segmentacja), SigLIP (język wizyjny), ConvNeXt (krytyczny dla opóźnień). Powód w jednym zdaniu.
2. Rozmiar łaty. 16 dla standardowej klasyfikacji przy 224, 14 dla DINOv2, 8 dla gęstej predykcji w wysokiej rozdzielczości. Długość sekwencji flagi `(H/P)^2 + 1` i koszt uwagi `O(N^2)`.
3. Źródło przedtreningowe. Nazwa punktu kontrolnego. W przypadku małych zestawów z etykietami (<10k): DINOv2 features frozen + linear probe. For >100k: dostrój ostatnie bloki. Podaj dlaczego.
4. Przepis na trening. Optymalizator (AdamW), lr, augmentacje (RandAug, MixUp, Random Erasing), wygładzanie etykiet (typowo 0,1), EMA.
5. Uwaga dotycząca ryzyka. Ryzyko reżimu danych (zbyt mało danych do pełnego dostrojenia), niedopasowanie rozdzielczości (wstępne uczenie 224 → wdrożenie 1024 bez interpolacji pozycji), brak tokena rejestru (może zaszkodzić funkcjom DINOv2).

Odmów rekomendowania szkolenia ViT od zera na mniej niż 1 milionie obrazów — wygrają wartości bazowe CNN. Odmów rekomendowania rozmiaru poprawki, który daje długość sekwencji > 4096, bez wyraźnego omówienia Flash Attention + wariantów hierarchicznych (Swin). Oznacz każde wdrożenie, które zmienia rozdzielczość wejściową bez interpolowania osadzania pozycyjnego.