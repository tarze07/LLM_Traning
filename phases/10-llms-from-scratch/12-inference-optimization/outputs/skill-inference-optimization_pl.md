---

name: skill-inference-optimization
description: Diagnozuj i optymalizuj wnioskowanie LLM obsługujące przepustowość, opóźnienia i koszty
version: 1.0.0
phase: 10
lesson: 12
tags: [inference, kv-cache, batching, speculative-decoding, vllm, optimization]

---

# Wzorzec optymalizacji wnioskowania LLM

Dwie fazy: wstępne wypełnianie (związane z obliczeniami, równoległe) i dekodowanie (związane z pamięcią, sekwencyjne).
Każda optymalizacja ma na celu jeden lub oba.

```
Request -> Prefill (process prompt) -> Decode (generate tokens) -> Response
              |                            |
         Compute-bound               Memory-bound
         Optimize: fusion,           Optimize: batching,
         prefix caching              quantization, speculation
```

## Ramy decyzyjne

### Krok 1: Zidentyfikuj wąskie gardło

Zmierz współczynnik operacji:bajtów dla swojego obciążenia:

| ops:bajt | Związany | Co optymalizować |
|---------|-------|--------------------------------|
| < 50 | Memory | Quantize KV cache, increase batch size |
| 50-200 | Transitional | Both matter, start with batching |
| > 200 | Oblicz | Fuzja jądra, równoległość tensorów, 8PR |

### Krok 2: Wybierz swój silnik

- **Domyślnie**: vLLM (obsługa najszerszego modelu, PagedAttention, API kompatybilne z OpenAI)
- **Wyjście wieloobrotowe / strukturalne**: SGLang (buforowanie prefiksów RadixAttention, ograniczone dekodowanie)
- **Maksymalna przepustowość NVIDIA**: TensorRT-LLM (fuzja jądra, FP8 na H100)

### Krok 3: Zastosuj optymalizacje w odpowiedniej kolejności

1. **KV cache** – zawsze włączona, bez wad
2. **Ciągłe przetwarzanie wsadowe** – zawsze włączone, bez wad (domyślnie robi to vLLM/SGLang)
3. **Buforowanie prefiksów** – włącz, jeśli masz wspólne podpowiedzi systemowe (większość chatbotów tak robi)
4. **Kwantyzacja** — Pamięć podręczna KV INT8/FP8 zmniejsza pamięć 2-4x przy minimalnej utracie jakości
5. **Dekodowanie spekulatywne** – dodaj, gdy opóźnienie jest ważniejsze niż przepustowość
6. **Równoległość tensorów** – podział na procesory graficzne, gdy model nie mieści się na jednym

## Formuła pamięci podręcznej KV

```
per_token = 2 * num_layers * num_kv_heads * head_dim * bytes_per_param
total = per_token * sequence_length * num_concurrent_users
```

Skrócona instrukcja obsługi popularnych modeli (BF16):

| Modelka | Za token | 100 użytkowników @ 4K |
|-------|-----------|----------------|
| Lama 3 8B | 32KB | 12,5 GB |
| Lama 3 70B | 320 kB | 125 GB |
| Lama 3 405B | 504 kB | 197 GB |

## Spekulacyjna lista kontrolna dekodowania

- Model draftu powinien być 5-10x mniejszy od docelowego (np. draft 8B dla 70B)
- Wskaźnik akceptacji > 70% dla znaczącego przyspieszenia
- Najlepsze w przypadku przewidywalnego tekstu (kod, uporządkowane dane wyjściowe, język naturalny)
- Najgorszy przy zadaniach kreatywnych/z dużą ilością próbek (pomaga niska temperatura)
- EAGLE > wersja robocza > n-gram dla większości obciążeń

## Typowe błędy

- Uruchamianie dekodowania w partii = 1 (związana z pamięcią, procesor graficzny w 95% bezczynny przy obliczeniach)
- Przydzielanie sąsiadujących bloków pamięci podręcznej KV (użyj PagedAttention, uzyskaj niemal zero odpadów)
- Ignorowanie buforowania prefiksów, gdy 80% żądań korzysta z tego samego monitu systemowego
- Nadmiar pamięci GPU dla ciężarów modeli, nie pozostawiając nic dla pamięci podręcznej KV
- Pomiar przepustowości bez pomiaru opóźnienia (wysoka przepustowość przy 10s TTFT jest bezużyteczna)
- Używanie dekodowania spekulatywnego w wysokiej temperaturze (współczynnik akceptacji spada poniżej 50%)

## Lista kontrolna monitorowania

- Czas do pierwszego tokena (TTFT): opóźnienie wstępnego wypełnienia, cel < 500 ms do użytku interaktywnego
- Opóźnienie między tokenami (ITL): prędkość dekodowania, cel < 50 ms dla przesyłania strumieniowego
- Przepustowość (tokeny/sekundę): całkowita dla wszystkich jednoczesnych użytkowników
- Wykorzystanie pamięci podręcznej KV: procent przydzielonej pamięci podręcznej w użyciu
- Wykorzystanie partii: procent zapełnionych miejsc wsadowych na iterację
- Głębokość kolejki: żądania oczekujące na miejsce wsadowe