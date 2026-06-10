---

name: inference-optimizer
description: Wybierz implementację uwagi, strategię pamięci podręcznej KV, kwantyzację i dekodowanie spekulatywne dla nowego wdrożenia wnioskowania.
version: 1.0.0
phase: 7
lesson: 12
tags: [transformers, inference, flash-attention, kv-cache]

---

Biorąc pod uwagę wdrożenie wnioskowania (nazwa modelu + parametry, sprzęt docelowy, współbieżność, maksymalna długość kontekstu, opóźnienie SLO, docelowa przepustowość), wynik:

1. Stos do serwowania. vLLM (produkcja domyślna), SGLang (najniższe opóźnienie na token), TensorRT-LLM (optymalnie dla NVIDIA), llama.cpp (edge/CPU), MLX (krzem Apple). Powód w jednym zdaniu.
2. Realizacja uwagi. Flash Attention 2 (domyślnie Ampere/Ada), Flash Attention 3 (Hopper), Flash Attention 4 (Blackwell, tylko do przodu). Określ rezerwę.
3. Pamięć podręczna KV. Dtype (domyślnie fp16, fp8, jeśli jest obsługiwany), stronicowany a ciągły, włączanie/wyłączanie buforowania prefiksów, współdzielona wartość KV dla próbkowania równoległego.
4. Kwantyzacja. fp16 / bf16 (domyślnie), int8 (tylko waga), AWQ / GPTQ / GGUF dla wag. Kwantyzacja aktywacyjna tylko w przypadku testów porównawczych.
5. Dodatkowe przyspieszenia. Dekodowanie spekulatywne (EAGLE 2 / Medusa / model roboczy), ciągłe przetwarzanie wsadowe (zawsze włączone), wstępne wypełnianie fragmentaryczne (obciążenia wymagające długiego monitu), buforowanie prefiksów w przypadku powtarzających się monitów.

Odmów wdrożenia Flash Attention 4 do celów szkoleniowych – w momencie uruchomienia jest on przesyłany tylko do przodu. Odmawiaj rekomendowania pamięci podręcznej KV fp8 bez sprawdzenia wpływu jakości na docelowe zadanie. Oznacz dowolny model 70B+ bez GQA jako posiadający niezarządzaną pamięć podręczną KV w kontekście 32K+. Wymagaj włączenia buforowania prefiksów dla każdego wdrożenia wywołującego agenta/narzędzie z powtarzającymi się monitami systemowymi.