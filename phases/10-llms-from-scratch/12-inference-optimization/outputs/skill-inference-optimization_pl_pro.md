---

name: skill-inference-optimization
description: Diagnoza i optymalizacja wnioskowania (inference) LLM pod kątem przepustowości, opóźnień (latency) i kosztów
version: 1.0.0
phase: 10
lesson: 12
tags: [inference, kv-cache, batching, speculative-decoding, vllm, optimization]

---

# Optymalizacja wnioskowania LLM (Inference Optimization)

Proces wnioskowania składa się z dwóch faz: prefill (zorientowana na obliczenia – compute-bound, przetwarzanie równoległe) oraz decode (zorientowana na przepustowość pamięci – memory-bound, generowanie sekwencyjne). Każda metoda optymalizacji celuje w poprawę co najmniej jednej z tych faz.

```
Request -> Prefill (proces promptu) -> Decode (generowanie tokenów) -> Response
              |                            |
         Compute-bound               Memory-bound
         Optymalizacja:               Optymalizacja:
         kernel fusion,               batching, kwantyzacja,
         prefix caching               dekodowanie spekulatywne
```

## Schemat decyzyjny

### Krok 1: Zidentyfikuj wąskie gardło

Zmierz stosunek operacji do bajtów (arithmetic intensity) dla swojego profilu obciążenia:

| Stosunek ops:bajt | Ograniczenie (bound) | Co optymalizować |
|---------|-------|--------------------------------|
| < 50 | Pamięć (Memory-bound) | Kwantyzacja KV cache, zwiększenie rozmiaru batcha |
| 50-200 | Przejściowe | Oba czynniki są ważne, zacznij od batchingu |
| > 200 | Obliczenia (Compute-bound) | Kernel fusion, Tensor Parallelism, precyzja FP8 |

### Krok 2: Wybierz silnik

- **Domyślny wybór**: vLLM (najszersze wsparcie dla modeli, mechanizm PagedAttention, API kompatybilne z OpenAI)
- **Konwersacje wieloturowe / ustrukturyzowane wyjście**: SGLang (buforowanie prefiksów RadixAttention, constrained decoding)
- **Maksymalna wydajność na GPU NVIDIA**: TensorRT-LLM (zaawansowany kernel fusion, natywne FP8 na H100)

### Krok 3: Zastosuj optymalizacje w odpowiedniej kolejności

1. **PagedAttention / Paged KV cache** – zawsze włączone, brak negatywnego wpływu.
2. **Ciągły batching (Continuous batching)** – zawsze włączony, brak wad (domyślnie zaimplementowany w vLLM/SGLang).
3. **Buforowanie prefiksów (Prefix caching)** – włącz, jeśli obsługujesz powtarzające się prompty systemowe (np. w chatbotach).
4. **Kwantyzacja** – kwantyzacja KV cache (INT8/FP8) redukuje zużycie pamięci 2-4x przy minimalnym wpływie na jakość.
5. **Dekodowanie spekulatywne (Speculative decoding)** – wdróż, gdy kluczowe jest zmniejszenie opóźnienia (latency), a przepustowość (throughput) ma drugorzędne znaczenie.
6. **Równoległość tensorowa (Tensor Parallelism)** – podział modelu na wiele GPU, gdy wagi nie mieszczą się w pamięci pojedynczej karty.

## Wzór na rozmiar KV cache

```
per_token = 2 * num_layers * num_kv_heads * head_dim * bytes_per_param
total = per_token * sequence_length * num_concurrent_users
```

Skrócona instrukcja obsługi popularnych modeli (precyzja BF16):

| Model | Rozmiar na token | 100 użytkowników przy 4k kontekstu |
|-------|-----------|----------------|
| Llama 3 8B | 32 KB | 12,5 GB |
| Llama 3 70B | 320 KB | 125 GB |
| Llama 3 405B | 504 KB | 197 GB |

## Lista kontrolna dekodowania spekulatywnego

- Model pomocniczy (draft model) powinien być 5-10x mniejszy niż model główny (target model) (np. draft 8B dla modelu głównego 70B).
- Wskrócony wskaźnik akceptacji propozycji (acceptance rate) powinien wynosić > 70% dla uzyskania zauważalnego przyspieszenia.
- Najlepsze rezultaty osiąga przy powtarzalnych/przewidywalnych tekstach (kod, ustrukturyzowany JSON, prosty język naturalny).
- Działa najgorzej przy zadaniach kreatywnych i wysokich temperaturach próbkowania (pomaga obniżenie temperatury).
- Hierarchia metod dla większości obciążeń: EAGLE > klasyczny model draft > n-gram.

## Typowe błędy

- Obsługa wnioskowania dla rozmiaru batcha = 1 (skrajne ograniczenie pamięciowe, układ GPU jest w 95% bezczynny obliczeniowo).
- Alokowanie ciągłych bloków pamięci dla KV cache (zastosuj PagedAttention, aby zredukować fragmentację i marnowanie pamięci niemal do zera).
- Ignorowanie prefix cachingu w sytuacjach, gdy 80% zapytań użytkowników współdzieli ten sam prompt systemowy.
- Przydzielenie całej dostępnej pamięci GPU na wagi modelu, bez rezerwacji VRAM na KV cache.
- Pomiar przepustowości (throughput) z pominięciem opóźnień (wysoki throughput jest bezużyteczny, jeśli TTFT wynosi 10 sekund).
- Stosowanie dekodowania spekulatywnego przy wysokich temperaturach generowania (współczynnik akceptacji spada wtedy poniżej 50%).

## Lista kontrolna monitorowania (Metryki)

- Czas do pierwszego tokena (TTFT – Time to First Token): opóźnienie fazy prefill, cel: < 500 ms dla zachowania interaktywności.
- Opóźnienie międzytokenowe (ITL – Inter-Token Latency): prędkość fazy decode, cel: < 50 ms dla płynnego streamingu.
- Przepustowość (Throughput – tokeny/s): sumaryczna wartość dla wszystkich aktywnych użytkowników.
- Wykorzystanie KV cache: procentowy stopień zajętości zaalokowanej pamięci podręcznej.
- Wykorzystanie batcha (batch utilization): średni stopień wypełnienia slotów batcha na iterację.
- Rozmiar kolejki (queue depth): liczba zapytań oczekujących na wolne miejsce w batchu.
