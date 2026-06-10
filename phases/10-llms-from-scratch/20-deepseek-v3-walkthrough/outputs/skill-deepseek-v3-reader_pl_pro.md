---

name: deepseek-v3-reader
description: Wczytaj konfigurację modelu z rodziny DeepSeek i przeprowadź szczegółową analizę architektury komponent po komponencie.
version: 1.0.0
phase: 10
lesson: 20
tags: [deepseek-v3, deepseek-r1, mla, moe, mtp, dualpipe, architecture]

---

Na podstawie wybranego modelu z rodziny DeepSeek (V3, R1 lub dowolnej pochodnej) oraz jego konfiguracji (hidden_size, layers, num_experts, kv_lora_rank itp.) przygotuj analizę architektury dzielącą model na komponenty i wskazującą zastosowane innowacje specyficzne dla rozwiązań DeepSeek.

Wygeneruj:

1. Szczegółową analizę konfiguracji pole po polu. Dla każdego pola wskaż przypisany komponent oraz liczbę parametrów, które ze sobą niesie. Format: `field_name: value → interpretation → parameter contribution`.
2. Podział parametrów: całkowita liczba parametrów, aktywne parametry oraz współczynnik aktywnych parametrów. Przedstaw szczegółowy podział uwzględniający: warstwę embeddingu (osadzeń), mechanizm attention na warstwę, MLP na warstwę (gęste vs eksperckie), router, moduł MTP, głowicę LM oraz sumaryczny wkład RMSNorm.
3. Zapotrzebowanie na pamięć podręczną KV (KV cache) dla docelowej długości kontekstu. Podaj wartości dla formatów BF16 i FP8. Dołącz porównanie z bazowym rozwiązaniem GQA w stylu Llama-3 (8/128) przy tym samym kontekście i wymiarze ukrytym (hidden size).
4. Listę kontrolną innowacji. Dla każdego z rozwiązań (MLA, MTP, routing bez strat pomocniczych/aux-loss-free routing, DualPipe) określ, czy model go używa i w której części konfiguracji lub publikacji naukowej jest to widoczne.
5. Weryfikację poprawności (sanity check). Oblicz budżet pamięci potrzebnej do inferencji (wagi + KV cache + aktywacje) dla określonego środowiska sprzętowego (H100 80 GB, H200 141 GB, MI300X 192 GB, pojedynczy węzeł vs klaster wielowęzłowy). Określ, czy model zmieści się w pamięci i jaka kwantyzacja będzie wymagana.

Kategoryczne odrzucenia:
- Wszelkie analizy zrównujące architekturę DeepSeek-V3 z gęstymi modelami klasy GPT. Ich architektury są zasadniczo różne.
- Twierdzenia, że MLA jest szybsze niż GQA bez precyzyjnego określenia długości kontekstu. W przypadku krótkiego kontekstu (poniżej 4 tys. tokenów) wydajność jest porównywalna; MLA zyskuje przewagę przy długim kontekście.
- Interpretowanie MTP jako bezpośredniego zamiennika dekodowania spekulatywnego. Jest to cel pre-treningowy, który pełni również funkcję optymalizacji procesu dekodowania.

Zasady odmowy wykonania zadania:
- Jeśli w dostarczonej konfiguracji brakuje parametrów `kv_lora_rank`, `num_experts` lub `first_k_dense_layers` – odrzuć zapytanie (to nie jest model z rodziny DeepSeek).
- Jeśli użytkownik oczekuje dokładnego dopasowania liczby oficjalnie opublikowanych parametrów (z dokładnością do 100 mln), odmów i wyjaśnij, że oficjalne dane uwzględniają parametry strukturalne specyficzne dla konkretnej implementacji, których uproszczony kalkulator nie jest w stanie precyzyjnie odwzorować. Skieruj użytkownika do załącznika do sekcji 2 oficjalnej publikacji (whitepaper).
- Jeśli docelowym środowiskiem uruchomieniowym jest konsumencka karta graficzna (24 GB VRAM lub mniej), odmów i zalecaj skorzystanie z destylowanych i skwantyzowanych modeli pochodnych z rodziny DeepSeek.

Format wyjściowy: Jednostronicowa analiza architektury zawierająca podział parametrów, zapotrzebowanie na KV cache, listę kontrolną innowacji oraz weryfikację środowiska wdrożeniowego. Zakończ sekcją „Sugerowane lektury” odsyłającą do NSA (faza 10, lekcja 17), analiz ablacyjnych MLA z artykułu opisującego V2 lub załącznika do sekcji 2 raportu technicznego V3 – w zależności od zagadnień poruszonych w analizie.
