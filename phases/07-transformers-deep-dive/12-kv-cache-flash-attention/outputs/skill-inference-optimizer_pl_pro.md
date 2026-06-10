---

name: inference-optimizer
description: Dobierz silnik serwujący, wariant atencji, strategię zarządzania KV Cache, metodę kwantyzacji oraz techniki optymalizacji dla nowego wdrożenia produkcyjnego modelu.
version: 1.0.0
phase: 7
lesson: 12
tags: [transformers, inference, flash-attention, kv-cache]

---

Na podstawie parametrów wdrożenia (nazwa modelu i liczba parametrów, sprzęt docelowy, oczekiwana współbieżność, maksymalna długość kontekstu, wymagane opóźnienie SLO, docelowa przepustowość) wygeneruj:

1. Silnik serwujący (serving engine): vLLM (zalecany domyślnie na produkcję), SGLang (najniższe opóźnienie na token), TensorRT-LLM (zoptymalizowany dla kart NVIDIA), llama.cpp (dla urządzeń brzegowych/CPU) lub MLX (dla architektury Apple Silicon). Podaj jednozdaniowe uzasadnienie.
2. Implementacja mechanizmu atencji: FlashAttention-2 (domyślnie dla architektur Ampere/Ada Lovelace), FlashAttention-3 (dla Hopper) lub FlashAttention-4 (dla Blackwell, obsługuje wyłącznie krok forward). Wskaż rozwiązanie awaryjne (fallback).
3. Konfiguracja KV Cache: typ danych (domyślnie FP16, lub FP8 jeśli jest obsługiwany), podział: stronicowany (PagedAttention) vs ciągły, włączenie/wyłączenie buforowania prefiksów (prefix caching), współdzielenie KV Cache na potrzeby próbkowania równoległego.
4. Kwantyzacja: FP16 / BF16 (domyślnie), int8 (wyłącznie kwantyzacja wag), AWQ / GPTQ / GGUF dla wag. Kwantyzacja aktywacji (activation quantization) zalecana wyłącznie w celach testowo-porównawczych.
5. Dodatkowe metody optymalizacji: dekodowanie spekulatywne (np. EAGLE-2 / Medusa / model pomocniczy drafter), ciągłe batchowanie (continuous batching - rekomendowane zawsze), wstępne przetwarzanie blokowe (chunked prefill dla długich promptów) oraz buforowanie prefiksów (prefix caching) przy powtarzających się promptach.

Odmawiaj rekomendowania biblioteki FlashAttention-4 do procesów treningowych – na obecnym etapie obsługuje ona wyłącznie krok forward. Odmawiaj rekomendowania kwantyzacji KV Cache do formatu FP8 bez uprzedniego zweryfikowania jej wpływu na jakość wyników w docelowym zadaniu. Oznacz jako krytyczne projekty modeli o rozmiarze 70B+ parametrów bez wdrożonej technologii GQA, ze względu na niekontrolowany rozrost rozmiaru KV Cache przy kontekstach 32K+. Wymagaj włączenia buforowania prefiksów (prefix caching) dla każdego wdrożenia agenta lub narzędzia, które regularnie przesyła powtarzające się prompty systemowe.
