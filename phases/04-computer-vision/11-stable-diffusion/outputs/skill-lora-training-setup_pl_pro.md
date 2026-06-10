---

name: skill-lora-training-setup
description: Generowanie kompletnej konfiguracji uczenia adaptera LoRA dla niestandardowego zbioru danych (dobór rang, współczynnika uczenia, parametrów krokowych i formatu podpisów)
version: 1.0.0
phase: 4
lesson: 11
tags: [computer-vision, stable-diffusion, lora, fine-tuning]

---

# Konfiguracja procesu uczenia LoRA

Przekształca opis planowanego dostrojenia w precyzyjną i kompletną konfigurację uczenia, gotową do uruchomienia za pomocą biblioteki `diffusers` lub narzędzia `kohya_ss`.

## Zastosowanie

- Trenowanie adaptera LoRA dla konkretnego obiektu/tematu (np. osoby, przedmiotu, postaci), stylu (np. stylu danego artysty, identyfikacji wizualnej marki) lub koncepcji (np. specyficznej pozy, oświetlenia).
- Rozszerzanie lub aktualizowanie istniejącego adaptera LoRA o nowe dane treningowe.
- Diagnozowanie problemów z uczeniem LoRA, gdy wyjściowe generacje słabo odzwierciedlają cechy ze zbioru treningowego (niedouczenie) lub są ich dosłowną kopią (przeuczenie).

## Dane wejściowe

- `purpose`: temat (`subject`) | styl (`style`) | koncepcja (`concept`)
- `num_images`: liczba dostępnych obrazów treningowych
- `base_model`: model bazowy: SD 1.5 | SDXL | SD3 | FLUX
- `gpu_vram_gb`: dostępna pamięć VRAM karty graficznej: 8 | 12 | 16 | 24 | 48+
- `caption_source`: źródło opisów (etykiet): ręczne (`manual`) | wygenerowane automatycznie (np. przez BLIP2 / CogVLM) | natywne ze zbioru danych

## Dobór rangi (Rank Selection)

| Cel | Ranga (Rank) | Alfa (Alpha) |
|-----|--------------|--------------|
| Temat (Subject) | 8-16 | Równa randze |
| Styl (Style) | 16-32 | Ranga * 2 |
| Koncepcja (Concept) | 32-64 | Równa randze |

Wyższa wartość rangi (rank) oznacza większą pojemność reprezentacji modelu, ale zwiększa ryzyko przeuczenia (overfittingu) przy małych zbiorach danych. Parametr Alpha skaluje siłę wpływu adaptera; ustawienie `alpha == rank` jest bezpieczną wartością domyślną. Wyjątkiem są style: dla nich często stosuje się `alpha == rank * 2` w celu mocniejszego wyeksponowania cech stylu, kosztem ewentualnego przesterowania kolorów – używaj tej opcji tylko wtedy, gdy nie zależy Ci na dokładnym odwzorowaniu konkretnego obiektu.

## Docelowa liczba kroków uczenia

- **Obiekt (subject)** z 5-20 obrazami: 500 - 1500 kroków.
- **Styl (style)** z 30-100 obrazami: 1500 - 4000 kroków.
- **Koncepcja (concept)** z > 100 obrazami: 4000 - 10000 kroków.

Przeuczenie modelu (overtraining) drastycznie ogranicza jego zdolność do generalizacji (generowania obiektu w nowych pozach, kontekstach czy stylach).

## Współczynnik uczenia (Learning Rate – LR)

- **Koder tekstu LoRA**: `1e-4` dla SD 1.5, `5e-5` dla SDXL.
- **U-Net LoRA**: `1e-4` dla SD 1.5, `1e-4` dla SDXL.
- **FLUX / SD3**: `5e-5` dla sieci Transformer (kodery tekstu pozostają zamrożone).
- Zmniejsz współczynnik uczenia o połowę (2x), gdy liczba obrazów treningowych jest mniejsza niż 15 (`num_images < 15`) lub gdy planujesz trening na ponad 3000 kroków. Zarówno bardzo małe zbiory danych, jak i długie procesy uczenia wymagają łagodniejszych aktualizacji wag.

## Harmonogram współczynnika uczenia (LR Scheduler)

- `cosine_with_warmup` (domyślny): faza rozbiegu (warmup) przez pierwsze 5-10% kroków, a następnie stopniowy spadek współczynnika uczenia według funkcji cosinusowej. Zalecany dla procesów trwających $\ge 1000$ kroków.
- `constant`: stały współczynnik uczenia. Stosuj go wyłącznie w przypadku bardzo krótkich sesji treningowych (`steps < 500`) lub podczas wznawiania treningu z istniejącego punktu kontrolnego (checkpointa), kiedy chcesz uniknąć ponownego wyżarzania (re-annealing).

## Przygotowanie opisów (Captioning)

- **Temat (subject)**: do każdego opisu dodaj unikalny token wyzwalający (trigger word), np. `ohwx` lub `zts`. Używaj unikalnych kombinacji znaków, aby uniknąć kolizji z istniejącymi pojęciami w słowniku kodera (unikaj powszechnych słów i imion).
- **Styl (style)**: dodaj unikalny identyfikator stylu na końcu każdego opisu (np. `in the style of mystyle`). Sam identyfikator powinien być unikalnym ciągiem znaków (np. `mystyle`), a nie powszechnie znanym pojęciem (jak `impressionism`), który model już zna.
- **Koncepcja (concept)**: dokładnie opisz pożądaną pozę, kadr lub oświetlenie w każdym opisie, bez dodawania dedykowanego słowa kluczowego. Ograniczenie (np. `low-angle shot`) będzie bezpośrednio powiązane z wzorcami w obrazach treningowych.

## Format konfiguracji (YAML)

```yaml
model:
  base: <base_model HF id>
  precision: fp16 | bf16

lora:
  rank: <int>
  alpha: <int>
  targets: unet.cross_attention  # i/lub unet.to_q, to_k, to_v, to_out

training:
  steps:          <int>
  batch_size:     <int, tuned to gpu_vram_gb>
  grad_accum:     <int, zazwyczaj 1 na >=16 GB, 4 na <=12 GB>
  learning_rate:  <float>
  optimizer:      AdamW8bit | AdamW
  scheduler:      cosine_with_warmup | constant
  warmup_steps:   <int>
  save_every:     <int>

data:
  images_dir:     <path>
  caption_source: <manual | BLIP2 | native>
  trigger_token:   <string if purpose==subject>
  resolution:      <512 dla SD 1.5, 1024 dla SDXL>
  aspect_ratio_bucketing: true
  augmentation:
    flip:          true
    color_jitter:  false

validation:
  prompts:
    - "<trigger> ...test prompt..."
    - "<trigger> in a different scene"
  every_steps: 250
```

## Format raportu

```
[lora setup]
  purpose:   <subject|style|concept>
  base:      <model>
  rank:      <int>
  steps:     <int>
  batch:     <int>   grad_accum: <int>
  lr:        <float>
  vram est.: <float> GB
```

## Reguły

- Nigdy nie zalecaj rangi większej niż 64 (`rank > 64`). Przekroczenie tej wartości sprawia, że LoRA zachowuje się jak pełne dostrojenie, tracąc swoje zalety jako lekki adapter.
- Jeśli `num_images < 5`, wyświetl zdecydowane ostrzeżenie – próba wytrenowania tożsamości na 1-3 obrazach prowadzi do niemal natychmiastowego przeuczenia i braku elastyczności modelu.
- Dla konfiguracji z `gpu_vram_gb < 12` bezwzględnie zalecaj optymalizator `AdamW8bit` oraz aktywowanie techniki gradient checkpointing.
- Jeśli wybranym modelem jest `FLUX`, a `gpu_vram_gb < 24`, wskaż zastosowanie wersji `FLUX.1-schnell` i poinformuj, że proces uczenia będzie bardzo czasochłonny.
- Zawsze dodawaj prompty walidacyjne do konfiguracji; ocena jakości adaptera LoRA bez generowania próbek testowych w trakcie uczenia jest niemożliwa.
