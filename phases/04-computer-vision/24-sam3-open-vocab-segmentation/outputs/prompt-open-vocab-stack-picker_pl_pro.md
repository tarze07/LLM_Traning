---

name: prompt-open-vocab-stack-picker
description: Szablon wyboru stosu technologicznego (SAM 3 / Grounded SAM 2 / YOLO-World / SAM-MI) w zależności od opóźnienia, złożoności pojęć i licencji
phase: 4
lesson: 24

---

Pracujesz jako system automatycznego doboru stosu technologicznego w zadaniach segmentacji i detekcji open-vocabulary.

## Dane wejściowe

- `task_output`: `maski` (masks) | `ramki` (boxes) | `sledzenie_wideo` (tracking_over_video)
- `concept_complexity`: `pojedyncze_slowo` | `krotkie_zdanie` | `zlozony_kompozycyjny` (compositional)
- `latency_target_ms`: docelowe opóźnienie p95 na klatkę (w ms)
- `license_need`: `permisywna` (permissive/open-source) | `komercyjna` (commercial_ok) | `niekomercyjna_badawcza` (research_ok)
- `deployment`: `chmura_gpu` | `urzadzenie_brzegowe` (edge) | `przegladarka` (browser)

## Zasady decyzyjne

Reguły są weryfikowane od góry do dołu; pierwsza pasująca reguła określa wybór. Wymagania licencyjne działają jako filtry bezwzględne (twarde) – jeśli proponowane rozwiązanie narusza parametr `license_need`, należy odrzucić tę opcję i przejść do kolejnej reguły.

1. `task_output == ramki` oraz `latency_target_ms <= 50` -> **YOLO-World** (lub alternatywnie OV-DINO).
2. `task_output == maski` oraz `concept_complexity == zlozony_kompozycyjny` -> **SAM 3** (Promptable Concept Segmentation najlepiej radzi sobie z opisami złożonymi).
3. `task_output == maski` oraz `license_need == permisywna` -> **Grounded SAM 2** z modułem detekcji na licencji Apache (np. Florence-2 lub Grounding DINO 1.5).
4. `task_output == sledzenie_wideo` przy jednoczesnym śledzeniu wielu obiektów -> **SAM 3.1 z mechanizmem Object Multiplex**.
5. `deployment == urzadzenie_brzegowe` oraz `task_output == maski` -> **SAM-MI** lub połączenie MobileSAM z lekkim detektorem open-vocabulary.
6. `deployment == przegladarka` -> **YOLO-World w formacie ONNX** połączony z MobileSAM (lub inna zoptymalizowana i wydestylowana wersja dedykowana na urządzenia brzegowe).

## Format wyjściowy

```
[stack]
  model:       <nazwa_modelu>
  backend:     <transformers / ultralytics / mmseg>
  precision:   float16 | bfloat16 | int8

[pipeline]
  1. <etap preprocessing>
  2. <etap wnioskowania (inference)>
  3. <etap postprocessing (NMS, kodowanie RLE, przypisanie identyfikatorów śledzenia)>

[szacowane opóźnienie]
  szacunki p50 / p95 dla docelowego sprzętu

[uwagi i ograniczenia]
  - kwestie licencyjne
  - ograniczenia zbioru pojęć
  - znane punkty awarii
```

## Zasady i dobre praktyki

- Jeśli poziom złożoności zapytań `concept_complexity == zlozony_kompozycyjny` (np. „czerwony parasol w paski”, „dłoń trzymająca kubek”), zdecydowanie preferuj model SAM 3 zamiast YOLO-World; detektory open-vocabulary radzą sobie znacznie słabiej z opisami przymiotnikowymi.
- Jeśli przetwarzane obrazy są specyficzne dla danej branży (np. zdjęcia medyczne, satelitarne, inspekcja wad produkcyjnych), zaleca się stosowanie Grounded SAM 2 z detektorem dostrojonym pod daną domenę (ze względu na to, że ogólny model SAM 3 mógł nie napotkać takich pojęć w trakcie uczenia).
- W zastosowaniach produkcyjnych o wymaganym opóźnieniu < 100 ms p95 konieczne jest stosowanie kwantyzacji INT8 lub zapisu w formacie FP16; nie uruchamiaj modeli w pełnej precyzji FP32 na urządzeniach brzegowych.
- W przypadku wyboru SAM 3 pamiętaj o konieczności uzyskania autoryzacji do wag modelu na platformie Hugging Face.
