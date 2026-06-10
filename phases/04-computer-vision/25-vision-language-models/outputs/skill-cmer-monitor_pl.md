---

name: skill-cmer-monitor
description: Instrumentuj produkcyjny punkt końcowy VLM za pomocą monitorowania współczynnika błędów międzymodalnych, pulpitów nawigacyjnych i alertów
version: 1.0.0
phase: 4
lesson: 25
tags: [vlm, production, monitoring, hallucination]

---

#Monitor CMER

Traktuj wyrównanie międzymodalne jako pierwszorzędny KPI produkcyjny.

## Kiedy używać

- Wdrażanie dowolnego punktu końcowego VLM, który generuje tekst na podstawie obrazów.
- Badanie raportów dotyczących reakcji halucynacyjnych.
- Śledzenie, czy przesunięcie dystrybucji sygnału wejściowego pogarsza uziemienie modelu.

## Wejścia

- `vlm_output`: wygenerowany tekst.
- `text_confidence`: średnie prawdopodobieństwo na token po softmax, w `[0, 1]`. Oblicz jako `exp(mean(log_probs))`. Nie przepuszczaj surowych logitów; surowe logity są nieograniczone, a `conf_threshold` zakłada prawdopodobieństwo.
- `image_embedding`: osadzanie obrazu z rodziny CLIP (DINOv3, SigLIP, CLIP).
- `text_embedding`: osadzanie wygenerowanego tekstu z rodziny CLIP.
- Opcjonalnie `prompt_type`: etykieta do grupowania (vqa / ocr / napisy / agent).

## Obliczenia na żądanie

```python
import torch

def cmer_flag(image_emb, text_emb, text_conf, sim_thr=0.25, conf_thr=0.8):
    if image_emb.shape != text_emb.shape:
        raise ValueError(f"emb shape mismatch: {image_emb.shape} vs {text_emb.shape}")
    image_emb = image_emb / (image_emb.norm() + 1e-8)
    text_emb = text_emb / (text_emb.norm() + 1e-8)
    sim = float((image_emb * text_emb).sum())
    flagged = (text_conf > conf_thr) and (sim < sim_thr)
    return {"sim": sim, "flagged": flagged}
```

Osadzania to 1-D tensory PyTorch (`torch.float32`) z niezależnego kodera z rodziny CLIP. Jeśli używasz tablic NumPy, zamień `.norm()` na `np.linalg.norm(...)` i odpowiednio rzuć dane wyjściowe.

Przechowuj `sim`, `text_conf`, `flagged`, `prompt_type`, `timestamp`, `model_version`, `request_id` w swoim potoku monitorowania (Prometheus, DataDog, OpenTelemetry).

## Zbiorcza metryka

```
CMER = (flagged requests in window) / (total requests in window)
```

Raportuj według punktu końcowego, typu podpowiedzi i wersji modelu.

## Progi alertów

- Bazowy CMER: ustalono ponad 7 dni normalnego ruchu.
- Ostrzeżenie: CMER >= 1,5x wartość wyjściowa przez 1 godzinę.
- Krytyczny: CMER >= 2x wartość podstawowa przez 30 minut lub > 15% wartości bezwzględnej dla dowolnego okna.

## Panele deski rozdzielczej

1. CMER w czasie (wiadro 5-minutowe, okno 7-dniowe).
2. CMER według typu zachęty (pasek skumulowany).
3. Rozkład `sim` na godzinę (histogram).
4. Najważniejsze wyniki dotyczące halucynacji (próbka 20 oflagowanych odpowiedzi dziennie do sprawdzenia przez człowieka).

## Działania, gdy CMER rośnie

1. Wypróbuj oflagowane żądania.
2. Sprawdź, czy wersja modelu nie została przypadkowo zmieniona.
3. Sprawdź rozkład sygnału wejściowego (nowy format pliku? nowe źródło obrazu? inna kompresja?).
4. Przekieruj dotknięty ruch do sprawdzenia ręcznego, aż do ustąpienia problemu.
5. Jeśli skok utrzymuje się, dostrój lub wymień model; nie tłumić ostrzeżenia.

## Zasady

- Nigdy nie obliczaj CMER przy użyciu własnych osadzeń VLM; użyj niezależnego enkodera (DINOv3, SigLIP lub CLIP-L/14). W przeciwnym razie mierzysz spójność modelu, a nie wyrównanie.
- Zawsze zapisuj surową wartość `sim`, a nie tylko bit `flagged`; zmiany w dystrybucji pojawiają się w dolnym kwartylu przed zmianą wskaźnika flagowego.
- Nie wysyłaj punktu końcowego VLM bez monitorowania CMER; halucynacje są dominującym rodzajem awarii produkcyjnej i są ciche bez tej metryki.
- W przypadku dziedzin wrażliwych (medycznych, prawnych, finansowych) podnieś `sim_threshold` do 0,35 lub więcej; stan flagi to `sim < sim_threshold`, zatem wyższy próg powoduje, że więcej wyjść jest potencjalnie nieuziemionych — jest to właściwa wartość domyślna w przypadku zastosowań o dużej stawce.