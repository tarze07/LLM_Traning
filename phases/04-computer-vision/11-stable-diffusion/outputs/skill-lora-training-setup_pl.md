---

name: skill-lora-training-setup
description: Napisz pełną konfigurację szkoleniową LoRA dla niestandardowego zestawu danych, w tym podpisy, rangę, rozmiar partii i szybkość uczenia się
version: 1.0.0
phase: 4
lesson: 11
tags: [computer-vision, stable-diffusion, lora, fine-tuning]

---

# Konfiguracja szkolenia LoRA

Zamień opis zamiaru dostrojenia w konkretną konfigurację szkoleniową, która jest gotowa do przekazania do `diffusers` lub `kohya_ss`.

## Kiedy używać

- Szkolenie LoRA dla tematu (osoba, przedmiot, postać), stylu (artysta, marka) lub koncepcji (poza, oświetlenie).
- Rozszerzenie istniejącej LoRA o więcej danych.
- Debugowanie przebiegu LoRA, którego dane wyjściowe nie pasują lub nie pasują do obrazów szkoleniowych.

## Wejścia

- `purpose`: temat | styl | koncepcja
- `num_images`: ile obrazów szkoleniowych jest dostępnych
- `base_model`: SD 1,5 | SDXL | SD3 | STRUMIEŃ
- `gpu_vram_gb`: 8 | 12 | 16 | 24 | 48+
- `caption_source`: instrukcja | wygenerowane przez BLIP2 | natywny zbiór danych

## Wybór rang

| Cel | Ranga | Alfa |
|--------|------|-------|
| Temat | 8-16 | ranga |
| Styl | 16-32 | pozycja * 2 |
| Koncepcja | 32-64 | ranga |

Wyższa ranga = większa pojemność, większe ryzyko nadmiernego dopasowania w przypadku małych zbiorów danych. Alpha skaluje siłę efektu LoRA; `alpha == rank` jest bezpiecznym ustawieniem domyślnym. Style stanowią udokumentowany wyjątek: `alpha == rank * 2` zapewnia silniejsze wzmocnienie stylu kosztem większego ryzyka zbytniego przypalenia stylu — używaj tylko wtedy, gdy celem nie jest wierność tematowi.

## Cel kroku treningowego

- `subject` z 5-20 obrazami: 500-1500 kroków.
- `style` z 30-100 obrazami: 1500-4000 kroków.
- `concept` z ponad 100 obrazami: 4000-10000 kroków.

Przekroczenie limitu na własne ryzyko — LoRA, która zapamiętała obrazy szkoleniowe, nie może generalizować.

## Szybkość uczenia się

- Koder tekstu LoRA: `1e-4` dla SD 1.5, `5e-5` dla SDXL.
- U-Net LoRA: `1e-4` dla SD 1.5, `1e-4` dla SDXL.
- FLUX/SD3: `5e-5` dla transformatora, kodery tekstowe zwykle zamrożone.
- Zmniejsz o połowę LR w przypadku `num_images < 15` (podmiot) lub podczas treningu na więcej niż 3000 kroków; Zarówno małe zbiory danych, jak i długie serie korzystają z delikatniejszej aktualizacji.

## Harmonogram

- `cosine_with_warmup` (domyślnie): rozgrzewka przez pierwsze 5-10% kroków, następnie zanik cosinusa. Użyj, gdy `steps >= 1000`; ogon rozpadu daje ostrzejsze próbki końcowe.
- `constant`: używaj tylko w przypadku bardzo krótkich serii (`steps < 500`) lub wznawiając poprzednią LoRA, gdzie chcesz zachować aktualnie wyuczone funkcje bez ponownego wyżarzania.

## Format podpisu

- Temat: do każdego podpisu dołącz unikalny token wyzwalający („moja osoba”). Zachowaj rzadki token wyzwalacza, aby nie nadpisywał istniejących koncepcji. Unikaj prawdziwych słów i popularnych nazw.
- Styl: dołącz unikalny znacznik stylu na końcu każdego podpisu („...w stylu mystyle”). Traktuj sam tag jako rzadki token wyzwalający — `mystyle`, a nie `impressionism`, który już odwzorowuje prawdziwą koncepcję.
- Koncepcja: opisz koncepcję w każdym podpisie; brak znacznika wyzwalacza. Sama koncepcja (np. „ujęcie z niskiego kąta”) jest kotwicą.

## Konfiguracja wyjściowa

```yaml
model:
  base: <base_model HF id>
  precision: fp16 | bf16

lora:
  rank: <int>
  alpha: <int>
  targets: unet.cross_attention  # and/or unet.to_q, to_k, to_v, to_out

training:
  steps:          <int>
  batch_size:     <int, tuned to gpu_vram_gb>
  grad_accum:     <int, usually 1 on >=16 GB, 4 on <=12 GB>
  learning_rate:  <float>
  optimizer:      AdamW8bit | AdamW
  scheduler:      cosine_with_warmup | constant
  warmup_steps:   <int>
  save_every:     <int>

data:
  images_dir:     <path>
  caption_source: <manual | BLIP2 | native>
  trigger_token:   <string if purpose==subject>
  resolution:      <512 for SD 1.5, 1024 for SDXL>
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

## Zgłoś

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

## Zasady

- Nigdy nie polecam `rank > 64`; powyżej LoRA staje się mini-dostrojeniem i traci swój charakter „adaptera”.
- W przypadku `num_images < 5` zdecydowanie ostrzegaj — tożsamości LoRA na 1-3 obrazach są za każdym razem nadmiernie dopasowane.
- W przypadku `gpu_vram_gb < 12` wymagany jest AdamW8bit i punkt kontrolny gradientu.
- Jeśli `base_model == FLUX` i `gpu_vram_gb < 24`, przejdź do wariantu `schnell` i pamiętaj, że szkolenie jest wolniejsze.
- Nigdy nie pomijaj monitów o weryfikację; LoRA bez przykładowych siatek jest niemożliwa do oceny.