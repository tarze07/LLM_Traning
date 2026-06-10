---

name: skill-cmer-monitor
description: Opomiarowanie produkcyjnych punktów końcowych VLM metryką CMER (Cross-Modal Error Rate) wraz z definicją progów alarmowych i dashboardów
version: 1.0.0
phase: 4
lesson: 25
tags: [vlm, production, monitoring, hallucination]

---

# Monitor CMER (Cross-Modal Error Rate Monitor)

Traktuj spójność międzymodalną (cross-modal alignment) jako kluczowy produkcyjny wskaźnik KPI.

## Zastosowanie

- Wdrażanie produkcyjne dowolnego modelu VLM generującego tekst na podstawie obrazu.
- Analiza i diagnostyka zgłoszeń dotyczących halucynacji modelu.
- Monitorowanie, czy przesunięcie rozkładu danych wejściowych (data drift) nie degraduje spójności generacji z obrazem.

## Dane wejściowe

- `vlm_output`: wygenerowany przez model tekst odpowiedzi.
- `text_confidence`: średnie prawdopodobieństwo wygenerowania tokenu (po funkcji softmax), w przedziale `[0, 1]`. Oblicza się je jako `exp(mean(log_probs))`. Bardzo ważne: nie przekazuj surowych logitów (logits) – są one nieograniczone wartościowo, a próg `conf_threshold` bazuje na rozkładzie prawdopodobieństwa.
- `image_embedding`: embedding obrazu wygenerowany za pomocą niezależnego modelu (np. DINOv3, SigLIP, CLIP).
- `text_embedding`: embedding wygenerowanego tekstu z tej samej rodziny modeli (np. CLIP/SigLIP).
- Opcjonalnie `prompt_type`: etykieta ułatwiająca grupowanie (np. `vqa`, `ocr`, `captioning`, `agent`).

## Obliczanie wskaźnika CMER w locie

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

Wektory embeddingów to jednowymiarowe tensory PyTorch (`torch.float32`) pochodzące z zewnętrznego kodera z rodziny CLIP. Jeśli obliczenia są realizowane na tablicach NumPy, należy zastąpić `.norm()` wywołaniem `np.linalg.norm(...)`.

Wartości `sim`, `text_conf`, `flagged`, `prompt_type`, `timestamp`, `model_version` oraz `request_id` należy logować w systemie telemetrycznym (np. Prometheus, Datadog, OpenTelemetry).

## Zbiorczy wskaźnik CMER

```
CMER = (liczba oznaczonych zapytań w oknie czasowym) / (łączna liczba zapytań w oknie czasowym)
```

Metryka powinna być raportowana w podziale na punkty końcowe (endpoints), typy zapytań i wersje modeli.

## Definicje progów alarmowych (Alerting)

- **Bazowy CMER (baseline)**: wyznaczony na podstawie stabilnego działania przez okres 7 dni.
- **Ostrzeżenie (Warning)**: wartość CMER >= 1.5x baseline utrzymująca się przez okres 1 godziny.
- **Alarm krytyczny (Critical)**: wartość CMER >= 2x baseline utrzymująca się przez 30 minut, bądź bezwzględna wartość CMER > 15% w dowolnym oknie czasowym.

## Struktura dashboardu monitorującego

1. Wykres CMER w czasie (okna 5-minutowe, zakres 7 dni).
2. CMER w podziale na typy zapytań (wykres słupkowy skumulowany).
3. Histogram rozkładu podobieństwa `sim` w ujęciu godzinowym.
4. Przykłady halucynacji o najwyższym priorytecie (losowa próba 20 oznaczonych odpowiedzi dziennie przekazywana do ręcznej weryfikacji).

## Procedura reagowania na wzrost CMER

1. Przeanalizuj wybrane próbki oznaczonych zapytań (flagged requests).
2. Upewnij się, że nie doszło do niekontrolowanej zmiany wersji serwowanego modelu.
3. Zweryfikuj rozkład danych wejściowych (np. zmiana formatu plików, nowe źródło obrazów, inny algorytm kompresji zdjęć).
4. Tymczasowo przekieruj podejrzane transakcje do ręcznej weryfikacji (human-in-the-loop) do momentu opanowania problemu.
5. Jeśli podwyższony poziom CMER się utrzymuje, zaplanuj dotrenowanie (fine-tuning) lub wymianę modelu bazowego; nie ignoruj ani nie wyciszaj alertów.

## Zasady i dobre praktyki

- Nigdy nie używaj wyjściowych cech (embeddingów) z samego modelu VLM do wyznaczania podobieństwa cosinusowego; stosuj całkowicie niezależny koder (np. DINOv3, SigLIP lub CLIP-L/14). W przeciwnym razie zmierzysz jedynie spójność wewnętrzną modelu, a nie rzeczywistą jakość dopasowania do prawdy obrazu.
- Zawsze loguj surową wartość podobieństwa `sim`, a nie tylko binarną flagę `flagged`; ewentualny dryf danych i spadek jakości widoczny jest w dolnych kwartylach rozkładu na długo przed masowym wzrostem liczby oznaczonych próbek.
- Nie wdrażaj produkcyjnie modeli VLM bez wdrożenia monitoringu CMER; halucynacje to dominujący i trudny do wykrycia bez tej metryki tryb awarii systemów wizyjno-językowych.
- W zastosowaniach o wysokim stopniu ryzyka (medycyna, prawo, finanse) podnieś próg `sim_threshold` do poziomu 0.35 lub wyżej. Flaga oznaczania ustawiana jest gdy `sim < sim_threshold`, zatem wyższa wartość sprawi, że system będzie bardziej czujny i chętniej oznaczy wątpliwe generacje jako potencjalne halucynacje.
