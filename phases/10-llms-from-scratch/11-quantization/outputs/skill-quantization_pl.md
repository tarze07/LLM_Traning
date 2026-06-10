---

name: skill-quantization
description: Wybierz odpowiednią strategię kwantyzacji do wdrażania LLM w oparciu o ograniczenia sprzętowe, jakość i opóźnienia
version: 1.0.0
phase: 10
lesson: 11
tags: [quantization, inference, deployment, optimization, fp8, int4, int8, gptq, awq, gguf]

---

# Ramy decyzji kwantyzacji

Podczas wdrażania modelu językowego użyj tej struktury, aby wybrać odpowiedni format liczb, metodę kwantyzacji i strategię sprawdzania jakości.

## Wymagania wejściowe

Zapewnij:
- **Model** (nazwa, liczba parametrów, oryginalna precyzja)
- **Sprzęt docelowy** (model GPU/VRAM, procesor, Apple Silicon, urządzenie brzegowe)
- **Docelowe opóźnienie** (tokeny/sekundę, czas do pierwszego tokena)
- **Dolny poziom jakości** (maksymalny akceptowalny wzrost zakłopotania, delta odniesienia)
- **Wzorzec udostępniania** (wielkość partii, maksymalna długość kontekstu, jednocześni użytkownicy)

## Szybki wybór

| Twoja sytuacja | Formatuj | Metoda | Oczekiwana utrata jakości |
|--------------|--------|------------|----------------------|
| Procesor graficzny H100, maksymalna przepustowość | 8PR E4M3 | Natywny odlew H100 | < 0.1% |
| A100/A10, need 2x throughput | INT8 | LLM.int8() or SmoothQuant | < 0.5% |
| Single 24GB GPU, 70B model | INT4 | AWQ or GPTQ | 1-3% |
| MacBook / Apple Silicon | INT4 GGUF | Q4_K_M via llama.cpp | 1-2% |
| Mobile / edge device | INT4 or INT3 | QAT + device-specific | 2-5% |
| Maximum compression, some loss OK | INT2 | QuIP# or AQLM | 5-15% |
| Training (mixed precision) | BF16 + FP32 accum | Native framework support | 0% |

## Precision Selection by Component

Not all tensors should get the same treatment.

| Component | Safe Minimum | Recommended | Avoid |
|-----------|-------------|-------------|-------|
| FFN weights | INT4 | INT4 (AWQ/GPTQ) | INT2 without QAT |
| Attention weights | INT4 | INT8 or FP8 | INT2 |
| Embedding layer | INT8 | FP16 (keep original) | INT4 |
| Output head | INT8 | FP16 (keep original) | INT4 |
| KV cache | FP8 | FP8 or INT8 | INT4 at long context |
| Attention logits | FP16 | FP16 or BF16 | INT8 |
| Activations (inference) | INT8 | FP8 or INT8 | INT4 |

## Method Comparison

### GPTQ
- **When:** GPU inference, you want a Hugging Face-compatible model
- **Calibration data:** 128 examples, 2048 tokens each
- **Time:** 30-60 minutes for 70B on A100
- **Tooling:** `auto-gptq`, `exllama`, `exllamav2`
- **Strength:** Well-tested, huge model zoo on Hugging Face
- **Weakness:** Slower than AWQ to apply, slightly lower quality than AWQ on some models

### AWQ
- **When:** GPU inference, you want best quality-per-bit
- **Calibration data:** 128 examples
- **Time:** 15-30 minutes for 70B on A100
- **Tooling:** `autoawq`, `vLLM` (native support)
- **Strength:** Best INT4 quality, fast to apply, vLLM integration
- **Weakness:** Smaller model zoo than GPTQ

### GGUF
- **When:** CPU inference, Apple Silicon, llama.cpp ecosystem
- **Variants:** Q2_K, Q3_K_S/M/L, Q4_K_S/M, Q5_K_S/M, Q6_K, Q8_0, F16
- **Recommended default:** Q4_K_M (best quality/size balance)
- **Tooling:** `llama.cpp`, PHIC10, PHIC11
- **Strength:** Self-contained files, mixed precision, massive ecosystem
- **Weakness:** Not optimal for GPU (designed for CPU/Metal)

### SmoothQuant
- **When:** INT8 on GPU, need both weight and activation quantization
- **Key idea:** Migrate quantization difficulty from activations to weights via per-channel scaling
- **Tooling:** PHIC12, PHIC13
- **Strength:** Enables W8A8 (both weights and activations in INT8) for 2x speedup
- **Weakness:** INT8 only, does not extend to INT4

## Quality Validation Protocol

After quantizing, validate before deploying:

1. **Perplexity test.** Compute on WikiText-2 or your domain corpus. Delta < 0.5 is excellent, 0.5-1.0 is good, > 2.0 jest problemem.

2. **Przegląd testu porównawczego.** Uruchom MMLU (ogólne), GSM8K (matematyczne), HumanEval (kod). Matematyka i kod są najbardziej wrażliwe na utratę precyzji.

3. **Porównanie wyników.** Wygeneruj 100 odpowiedzi zarówno z modelu oryginalnego, jak i skwantowanego. Użyj LLM-as-sędziego, aby obliczyć współczynnik wygranych. Cel: model skwantowany wygrywa lub remisuje w > 90% podpowiedzi.

4. **Pomiar opóźnienia.** Zmierz tokeny na sekundę przy partii o rozmiarze 1 i docelowej wielkości partii. Sprawdź, czy przyspieszenie uzasadnia koszt jakości.

5. **Test długiego kontekstu.** Jeśli obsługujesz długie konteksty (> 4 tys. tokenów), testuj przy maksymalnej długości kontekstu. Błędy kwantyzacji pamięci podręcznej KV złożone z długością sekwencji.

## Kalkulator budżetu pamięci

```
Weight memory (GB) = parameters (B) * bits / 8 / 1.073741824
KV cache per token (MB) = 2 * num_layers * d_model * bits / 8 / 1048576
KV cache for context (GB) = kv_per_token * max_context_length / 1024
Activation memory (GB) ~ 1-4 GB (relatively constant, depends on batch size)
Total = weight_memory + kv_cache + activation_memory + overhead (10-20%)
```

Przykład dla Lamy 3 70B w kontekście INT4, 32K:
- Waga: 70B * 4 / 8 / 1,07 = 32,6 GB
- Pamięć podręczna KV (FP16): 2 * 80 * 8192 * 16 / 8 / 1e9 * 32768 = ~40 GB
- Pamięć podręczna KV (FP8): ~20 GB
- Łącznie z FP8 KV: ~55 GB (pasuje do jednego 80 GB A100)

## Typowe błędy

| Błąd | Dlaczego to się nie udaje | Napraw |
|-------------|------------|-----|
| Kwantyzacja warstwy osadzającej na INT4 | Pierwsza warstwa wzmacnia błędy w całym modelu | Zachowaj osadzanie na FP16 lub INT8 |
| Korzystanie ze skal per-tensorowych dla INT4 | Jeden odstający wiersz niszczy precyzję wszystkich wierszy | Użyj skal dla kanału lub grupy |
| Brak kalibracji GPTQ/AWQ | Współczynniki skali są błędne bez reprezentatywnych danych | Użyj 128 przykładów ze swojej domeny |
| Ta sama szerokość bitowa dla wszystkich warstw | Pierwsza/ostatnia warstwa jest bardziej wrażliwa | Mieszana precyzja: wyższe bity dla pierwszego/ostatniego |
| Kwantyzacja pamięci podręcznej KV w bardzo długim kontekście | Błędy łączą się kwadratowo z długością sekwencji | Użyj FP8 dla pamięci podręcznej KV, a nie INT4 |
| Pomijanie sprawdzania jakości | Niektóre modele słabo kwantyzują (szczególnie na granicach) | Zawsze uruchamiaj zakłopotanie + ewaluacja zadania |

## Przepisy wdrożeniowe

### Przepis 1: vLLM z AWQ (serwer GPU)
```
pip install vllm autoawq
vllm serve model-awq --quantization awq --dtype half --max-model-len 8192
```

### Przepis 2: lama.cpp z GGUF (MacBook)
```
./llama-server -m model.Q4_K_M.gguf -c 4096 -ngl 99
```

### Przepis 3: TensorRT-LLM z FP8 (H100)
```
trtllm-build --model_dir model --output_dir engine --dtype float16 --use_fp8
```