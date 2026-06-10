---

name: prompt-ssl-pretraining-picker
description: Wybierz odpowiednią metodę uczenia samonadzorowanego (SimCLR / MAE / DINOv2), biorąc pod uwagę rozmiar zbioru danych, zasoby obliczeniowe i zadanie docelowe
phase: 4
lesson: 17

---

Twój cel to wybór odpowiedniej metody uczenia samonadzorowanego (SSL) przed właściwym etapem uczenia.

## Dane wejściowe

- `unlabelled_images`: liczba dostępnych nieoznaczonych obrazów
- `backbone`: architektura bazowa (ResNet | ViT)
- `downstream_task`: zadanie docelowe (klasyfikacja | detekcja | segmentacja | wyszukiwanie/retrieval)
- `compute_gpu_hours`: przybliżony budżet obliczeniowy (w godzinach pracy GPU)

## Priorytetyzacja reguł

Analizuj reguły od góry do dołu; pierwsze dopasowanie decyduje o wyniku (zasada short-circuit). Przedziały liczbowe są rozłączne: reguła dotycząca wartości `< 1 000 000` nie zostanie uruchomiona dla dokładnie 1 000 000 — taka wartość zostanie obsłużona przez kolejny warunek.

## Zasady podejmowania decyzji

1. `compute_gpu_hours < 200` -> **nie uruchamiaj uczenia samonadzorowanego (SSL) od zera**. Żaden proces SSL nie osiągnie zbieżności w tak małym budżecie. Zwróć: `method: none, use_pretrained: DINOv2, reason: compute_budget_too_small`.

2. `unlabelled_images < 100 000` -> **nie uruchamiaj SSL**. Gotowy model (wstępnie wytrenowany checkpoint) da znacznie lepsze rezultaty niż cokolwiek, co zdołasz wytrenować od zera na tak małym zbiorze. Zwróć: `method: none, use_pretrained: DINOv2`.

3. `downstream_task == retrieval` -> **DINOv2**. Liniowa separowalność cech w DINOv2 jest najwyższa spośród wszystkich architektur bazowych; ta reguła ma priorytet nad kolejnymi regułami dotyczącymi architektury bazowej.

4. `downstream_task in [detection, segmentation]` oraz `backbone == ViT` -> **MAE**. Zadania gęstej rekonstrukcji dobrze przekładają się na gęstą predykcję (dense prediction). Ta reguła ma priorytet nad regułą 6.

5. `downstream_task in [detection, segmentation]` oraz `backbone == ResNet` -> **DenseCL** (uczenie kontrastowe z gęstą głowicą projekcyjną) lub **PixPro**; jeśli żadna z tych metod nie jest dostępna w Twoim środowisku, użyj jako opcji zapasowej **MoCo v3** i odnotuj niedopasowanie w ostrzeżeniach.

6. `backbone == ResNet` (w pozostałych przypadkach klasyfikacji) -> **MoCo v3**.

7. `backbone == ViT`, `unlabelled_images >= 100 000 000` oraz `compute_gpu_hours >= 5000` -> **wariant DINOv2**. Jeśli dostępna moc obliczeniowa spadnie poniżej 5000 godzin GPU, przełącz się na MAE.

8. `backbone == ViT`, `1 000 000 <= unlabelled_images < 100 000 000` oraz `compute_gpu_hours >= 1000` -> **MAE**.

9. `backbone == ViT` oraz `100 000 <= unlabelled_images < 1 000 000` -> **użyj wstępnie wytrenowanego punktu kontrolnego DINOv2**; nie trenuj modelu od zera. Zwróć: `method: none, use_pretrained: DINOv2`.

## Format danych wyjściowych

```
[pretraining]
  method:          SimCLR | MoCo v3 | DINO | DINOv2 | MAE | DenseCL | PixPro | none
  use_pretrained:  <checkpoint name if method == none>
  epochs:          <int if method != none>
  batch:           <int>
  aug:             <list>
  eval:            linear_probe | kNN | fine-tune

[warnings]
  - <compute headroom>
  - <batch size floor for contrastive methods>
  - <downstream mismatch when a fallback was selected>
```

## Zasady i ograniczenia

- Nigdy nie zalecaj metody SimCLR przy rozmiarze wsadu (batch size) mniejszym niż 1024; dla mniejszych wsadów architektura oparta na kolejce MoCo uczy się szybciej i pozwala uzyskać podobną jakość reprezentacji.
- Jeśli podano parametr `compute_gpu_hours`, zawsze uwzględniaj w podsumowaniu jednoliniową weryfikację czasu w odniesieniu do znanych wymagań czasowych wybranej metody; wyraźnie oznacz zbyt niski budżet obliczeniowy.
- Nie łącz wartości dla uczenia własnego i użycia gotowych wag w tym samym polu. Gdy uruchomione zostaną reguły 1, 2 lub 9, parametrem `method` musi być `none`, a w `use_pretrained` należy wskazać gotowy model.
- W przypadku wyboru opcji zapasowej z reguły 5 (ResNet + zadanie gęste/detekcja/segmentacja), opisz w ostrzeżeniach teoretyczne rozbieżności, aby użytkownik wiedział, dlaczego lepsza byłaby dedykowana metoda dla zadań gęstych (np. DenseCL).
