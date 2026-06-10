---

name: vllm-scheduler-reader
description: Diagnozuj wydajność i konfigurację silnika vLLM. Narzędzie analizuje parametry harmonogramu i identyfikuje wąskie gardła w obszarach: alokacja PagedAttention, ciągłe przetwarzanie wsadowe (continuous batching) lub dzielenie fazy prefill na fragmenty (chunked prefill).
version: 1.0.0
phase: 17
lesson: 04
tags: [vllm, paged-attention, continuous-batching, chunked-prefill, serving, scheduler]

---

Na podstawie parametrów wdrożenia vLLM (model, format danych, specyfikacja sprzętowa, `--gpu-memory-utilization`, `--max-num-batched-tokens`, `--enable-chunked-prefill`, `--speculative-model` lub `--speculative-config`, maksymalny poziom współbieżności oraz obserwowany zestaw metryk wydajności: średnia i percentyl P99 TTFT, średnia i percentyl P99 ITL, przepustowość w tokenach/s) przygotuj diagnozę wydajnościową na poziomie harmonogramu (schedulera).

Przygotuj:

1. **Weryfikacja konfiguracji (Configuration audit).** Dla każdego parametru określ zachowanie harmonogramu, którym steruje, oraz jego domyślną wartość dla wersji vLLM z 2026 roku. Wskaż wszelkie parametry ustawione na wartości inne niż domyślne i wyjaśnij cel tych modyfikacji.
2. **Identyfikacja wąskiego gardła (Bottleneck identification).** Sklasyfikuj główny czynnik ograniczający wydajność jako jeden z następujących: niewłaściwa konfiguracja PagedAttention (blokowanie zapytań przez brak wolnych bloków KV Cache), opóźnienia w ciągłym przetwarzaniu wsadowym (wzrost liczby zadań w kolejce WAITING), nieprawidłowy rozmiar fragmentów prefill (skokowy wzrost percentyli TTFT), ograniczenia obliczeniowe w fazie decode (wysoka minimalna wartość ITL) lub ograniczenia pamięci HBM (brak możliwości zwiększenia rozmiaru paczki - batch). Uzasadnij diagnozę za pomocą dostarczonych metryk.
3. **Rekomendacje strojenia parametrów (Tuning recommendations).** Przedstaw konkretną, uszeregowaną listę działań optymalizacyjnych — które parametry zmienić, jakie wartości przetestować oraz jakie metryki monitorować. Nie sugeruj zakupu dodatkowych zasobów GPU bez wcześniejszego wyczerpania możliwości optymalizacji na poziomie harmonogramu.
4. **Weryfikacja kompatybilności.** Dla vLLM w wersji v0.18.0 wyraźnie oznacz jednoczesne stosowanie parametrów `--enable-chunked-prefill` oraz `--speculative-model` jako krytyczną niekompatybilność. Wskaż jądro dekodowania spekulatywnego N-gram na GPU w harmonogramie V1 jako jedyny udokumentowany wyjątek, jeśli konieczne jest jednoczesne korzystanie z obu optymalizacji.
5. **Zalecane materiały uzupełniające.** W zależności od postawionej diagnozy wskaż jeden z dokumentów źródłowych: oficjalną dokumentację wydania vLLM v0.18.0, oryginalną publikację naukową o PagedAttention lub przewodnik po harmonogramie V1 autorstwa Aleksy Gordicia.

Bezwzględne odrzucenie analizy w przypadku:

- Próby postawienia diagnozy bez kompletu czterech podstawowych metryk (TTFT, ITL, przepustowość, współbieżność). Odmów analizy i poproś o podanie brakujących danych.
- Rekomendowania włączenia `--enable-chunked-prefill` bez uprzedniego sprawdzenia konfiguracji dekodowania spekulatywnego.
- Traktowania metryki `DCGM_FI_DEV_GPU_UTIL` jako sygnału do skalowania zasobów. vLLM wstępnie alokuje pamięć na bloki KV Cache, przez co surowe parametry obciążenia rdzeni GPU są niemiarodajne.

Zasady weryfikacji i odmowy:

- Jeśli raportowana przepustowość systemu wynosi poniżej 100 tokenów/s na układ H100, wąskie gardło najprawdopodobniej leży poza vLLM – wskaż na konieczność weryfikacji opóźnień tokenizatora po stronie klienta, blokad wątków w Pythonie (GIL) lub problemów z serializacją żądań.
- Jeśli parametr `--gpu-memory-utilization` jest ustawiony na wartość poniżej 0.7, odmów dalszego strojenia – operator świadomie rezygnuje z wykorzystania dostępnej pamięci HBM; pierwszym krokiem musi być zwiększenie tego limitu przed modyfikacją innych parametrów.
- Jeśli operator pyta o instrukcję wdrożenia jednoczesnego dekodowania spekulatywnego (z osobnym modelem pomocniczym) oraz chunked prefill, odmów wskazania takiego rozwiązania ze względu na niekompatybilność w wersji v0.18.0. Zamiast tego skieruj użytkownika do technologii EAGLE-3 (faza 17 · 05).

Format wyjściowy: Jednostronicowa diagnoza działania harmonogramu zawierająca analizę parametrów, zidentyfikowane wąskie gardła, uszeregowane zalecenia, uwagi dotyczące kompatybilności oraz zalecane materiały uzupełniające. Zakończ sekcją „Kolejny krok pomiarowy”, wskazując – w zależności od zidentyfikowanego problemu – na konieczność monitorowania wskaźnika P99 ITL, współczynnika alokacji bloków KV Cache lub liczby zapytań w kolejce WAITING.
