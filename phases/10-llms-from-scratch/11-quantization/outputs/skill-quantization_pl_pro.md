---

name: skill-quantization
description: Wybór właściwej strategii kwantyzacji do wdrażania modeli LLM w oparciu o ograniczenia sprzętowe, jakość odpowiedzi i opóźnienia (latency)
version: 1.0.0
phase: 10
lesson: 11
tags: [quantization, inference, deployment, optimization, fp8, int4, int8, gptq, awq, gguf]

---

# Schemat wyboru kwantyzacji (Quantization Decision Framework)

Wdrażając model językowy, skorzystaj z poniższego schematu decyzyjnego, aby dobrać odpowiedni format danych liczbowych, metodę kwantyzacji oraz strategię walidacji jakości.

## Wymagania wejściowe

Podaj (dane wejściowe):
- **Model** (nazwa, liczba parametrów, oryginalna precyzja)
- **Sprzęt docelowy** (model GPU/VRAM, procesor, Apple Silicon, urządzenie brzegowe)
- **Docelowe opóźnienie (latency)**: (liczba tokenów na sekundę, czas do wygenerowania pierwszego tokena – TTFT)
- **Minimalna akceptowalna jakość**: (maksymalny dopuszczalny wzrost perplexity, dopuszczalny spadek względem modelu bazowego)
- **Profil ruchu (serving pattern)**: (rozmiar batcha, maksymalna długość kontekstu, liczba jednoczesnych użytkowników)

## Szybki wybór

| Sytuacja | Format | Metoda | Oczekiwana utrata jakości |
|--------------|--------|------------|----------------------|
| GPU H100, maksymalna przepustowość | FP8 E4M3 | Natywna konwersja (cast) na H100 | < 0,1% |
| A100/A10, potrzeba 2-krotnego wzrostu przepustowości | INT8 | LLM.int8() lub SmoothQuant | < 0,5% |
| Pojedyncze GPU 24 GB, model 70B | INT4 | AWQ lub GPTQ | 1-3% |
| MacBook / Apple Silicon | INT4 GGUF | Q4_K_M przez llama.cpp | 1-2% |
| Urządzenia mobilne / edge | INT4 lub INT3 | QAT + optymalizacja pod sprzęt | 2-5% |
| Maksymalna kompresja, dopuszczalny spadek jakości | INT2 | QuIP# lub AQLM | 5-15% |
| Trening (mieszana precyzja) | BF16 + akumulacja FP32 | Natywne wsparcie frameworku | 0% |

## Wybór precyzji według komponentów

Nie wszystkie tensory powinny być traktowane tak samo.

| Komponent | Bezpieczne minimum | Rekomendowane | Unikaj |
|-----------|-------------|-------------|-------|
| Wagi FFN | INT4 | INT4 (AWQ/GPTQ) | INT2 bez QAT |
| Wagi atencji | INT4 | INT8 lub FP8 | INT2 |
| Warstwa osadzeń (embeddings) | INT8 | FP16 (zachowanie oryginału) | INT4 |
| Głowica wyjściowa (LM head) | INT8 | FP16 (zachowanie oryginału) | INT4 |
| KV cache | FP8 | FP8 lub INT8 | INT4 przy długim kontekście |
| Logity atencji | FP16 | FP16 lub BF16 | INT8 |
| Aktywacje (wnioskowanie) | INT8 | FP8 lub INT8 | INT4 |

## Porównanie metod

### GPTQ
- **Kiedy stosować**: Wnioskowanie na GPU, gdy zależy Ci na kompatybilności z Hugging Face.
- **Dane kalibracyjne**: 128 przykładów o długości 2048 tokenów każdy.
- **Czas**: 30-60 minut dla modelu 70B na GPU A100.
- **Ekosystem / Narzędzia**: `auto-gptq`, `exllama`, `exllamav2`
- **Zalety**: Dobrze przetestowana metoda, olbrzymi zbiór gotowych modeli na Hugging Face.
- **Wady**: Wolniejsza konwersja w porównaniu do AWQ; na niektórych modelach daje minimalnie gorszą jakość niż AWQ.

### AWQ
- **Kiedy stosować**: Wnioskowanie na GPU, gdy zależy Ci na najlepszym stosunku jakości do rozmiaru w bitach.
- **Dane kalibracyjne**: 128 przykładów.
- **Czas**: 15-30 minut dla modelu 70B na GPU A100.
- **Ekosystem / Narzędzia**: `autoawq`, `vLLM` (natywne wsparcie)
- **Zalety**: Najlepsza jakość dla formatu INT4, szybki czas kwantyzacji, integracja z vLLM.
- **Wady**: Mniejszy zbiór gotowych modeli niż w przypadku GPTQ.

### GGUF
- **Kiedy stosować**: Wnioskowanie na CPU, Apple Silicon, ekosystem `llama.cpp`.
- **Warianty**: Q2_K, Q3_K_S/M/L, Q4_K_S/M, Q5_K_S/M, Q6_K, Q8_0, F16
- **Sugerowana wartość domyślna**: Q4_K_M (najlepszy balans między jakością a rozmiarem).
- **Ekosystem / Narzędzia**: `llama.cpp`
- **Zalety**: Samodzielne, pojedyncze pliki modeli, mieszana precyzja, potężny ekosystem.
- **Wady**: Nieoptymalny format pod kątem wydajności na czystym GPU (zaprojektowany dla CPU/Metal).

### SmoothQuant
- **Kiedy stosować**: INT8 na GPU, gdy potrzebujesz jednoczesnej kwantyzacji wag i aktywacji.
- **Główna idea**: Przeniesienie trudności kwantyzacji z aktywacji na wagi za pomocą skalowania per-channel.
- **Ekosystem / Narzędzia**: Integracja w zaawansowanych silnikach wnioskowania (np. TensorRT-LLM, vLLM).
- **Zalety**: Umożliwia format W8A8 (wagi i aktywacje w INT8) dający ok. 2-krotne przyspieszenie.
- **Wady**: Wsparcie jedynie dla precyzji INT8, brak możliwości zejścia do INT4.

## Protokół walidacji jakości

Po kwantyzacji zweryfikuj model przed wdrożeniem:

1. **Test perplexity**: Oblicz na zbiorze WikiText-2 lub na własnym korpusym domenowym. Różnica $\Delta < 0,5$ jest doskonała, $0,5$–$1,0$ dobra, a $> 2,0$ sygnalizuje problem.
2. **Testy benchmarkowe**: Uruchom MMLU (wiedza ogólna), GSM8K (matematyka) oraz HumanEval (kodowanie). Zadania matematyczne i programistyczne są najbardziej wrażliwe na utratę precyzji.
3. **Porównanie wyników**: Wygeneruj 100 odpowiedzi z modelu oryginalnego i skwantowanego. Wykorzystaj LLM-as-a-judge do obliczenia współczynnika wygranych (win rate). Cel: model skwantowany wygrywa lub remisuje w ponad 90% przypadków.
4. **Pomiar opóźnienia (latency)**: Zmierz liczbę tokenów na sekundę dla rozmiaru batcha równego 1 oraz dla docelowego obciążenia produkcyjnego. Upewnij się, że zysk wydajnościowy uzasadnia minimalny spadek jakości.
5. **Ewaluacja długiego kontekstu**: Jeśli obsługujesz długi kontekst (> 4k tokenów), przetestuj model przy maksymalnej długości sekwencji. Błędy kwantyzacji KV cache kumulują się nieliniowo wraz z długością kontekstu.

## Kalkulator budżetu pamięci

```
Pamięć wag (GB) = parametry (B) * bity / 8 / 1.073741824
Pamięć KV cache na token (MB) = 2 * num_layers * d_model * bity / 8 / 1048576
Pamięć KV cache dla całego kontekstu (GB) = kv_per_token * max_context_length / 1024
Pamięć aktywacji (GB) ~ 1-4 GB (wartość w miarę stała, zależna od batch_size)
Suma = pamiec_wag + kv_cache + pamiec_aktywacji + narzut (10-20%)
```

Przykład dla modelu Llama 3 70B w precyzji INT4, z kontekstem 32k:
- Waga: 70B * 4 / 8 / 1,07 = 32,6 GB
- KV cache (FP16): ~40 GB
- KV cache (FP8): ~20 GB
- Razem z FP8 KV cache: ~55 GB (mieści się na jednej karcie A100 80 GB)

## Typowe błędy

| Typowy błąd | Dlaczego to nie działa | Rozwiązanie |
|-------------|------------|-----|
| Kwantyzacja warstwy osadzeń (embeddings) do INT4 | Pierwsza warstwa kumuluje i potęguje błędy w całej sieci | Zachowaj precyzję FP16 lub INT8 dla osadzeń |
| Stosowanie skalowania per-tensor dla INT4 | Pojedyncza wartość odstająca (outlier) drastycznie niszczy precyzję pozostałych wag | Zastosuj skalowanie per-channel lub per-group |
| Pominięcie kalibracji GPTQ/AWQ | Brak reprezentatywnych danych kalibracyjnych powoduje błędne wyznaczenie skal | Wykorzystaj min. 128 zróżnicowanych przykładów ze swojej domeny |
| Jednolita precyzja (bitwidth) dla wszystkich warstw | Pierwsza i ostatnia warstwa są znacznie bardziej wrażliwe na kwantyzację | Zastosuj precyzję mieszaną (mixed precision) – zachowaj wyższą precyzję dla pierwszej i ostatniej warstwy |
| Kwantyzacja KV cache w bardzo długich kontekstach | Błędy kwantyzacji kumulują się nieliniowo wraz z długością sekwencji | Stosuj precyzję FP8 dla KV cache zamiast formatu INT4 |
| Pomijanie walidacji jakości | Niektóre modele słabo znoszą kwantyzację (zwłaszcza na granicach precyzji) | Zawsze wykonuj testy perplexity i weryfikację na dedykowanych zadaniach |

## Przepisy wdrożeniowe

### Przepis 1: vLLM z AWQ (serwer GPU)
```
pip install vllm autoawq
vllm serve model-awq --quantization awq --dtype half --max-model-len 8192
```

### Przepis 2: llama.cpp z GGUF (MacBook)
```
./llama-server -m model.Q4_K_M.gguf -c 4096 -ngl 99
```

### Przepis 3: TensorRT-LLM z FP8 (H100)
```
trtllm-build --model_dir model --output_dir engine --dtype float16 --use_fp8
```
