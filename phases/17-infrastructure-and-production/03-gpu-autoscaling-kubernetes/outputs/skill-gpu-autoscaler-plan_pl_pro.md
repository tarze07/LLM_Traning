---

name: gpu-autoscaler-plan
description: Zaprojektuj trójwarstwowy plan automatycznego skalowania procesorów GPU (Karpenter + KAI Scheduler + sygnały aplikacji) dla klastra Kubernetes obsługującego serwowanie modeli LLM. Narzędzie diagnozuje i eliminuje błędy związane z użyciem metryki DCGM_FI_DEV_GPU_UTIL oraz błędy częściowej alokacji zasobów.
version: 1.0.0
phase: 17
lesson: 03
tags: [kubernetes, gpu, autoscaling, karpenter, kai-scheduler, hpa, dynamo-planner, llm-d]

---

Na podstawie topologii klastra (węzły, typy kart GPU, domeny NVLink), charakterystyki obciążenia (konfiguracja TP/PP, średnia współbieżność zapytań, współczynnik zmienności ruchu) oraz wymagań SLO (percentyl P99 TTFT, goodput) przygotuj trójwarstwowy plan automatycznego skalowania.

Przygotuj:

1. **Warstwa 1 — Konfiguracja Karpenter NodePool.** Określ parametry `instance-type`, `capacity-type` (na żądanie [on-demand] / spot / zarezerwowane [reserved]), `consolidationPolicy` (dla puli GPU musi to być konfiguracja `WhenEmpty` z parametrem `consolidateAfter: 1h`), tolerancje (tolerations) i reguły pokrewieństwa (affinity) wykluczające uruchamianie zadań niezwiązanych z GPU na tych maszynach, a także etykiety (labels) dla integracji z KAI Schedulerem.
2. **Warstwa 2 — Konfiguracja reguł KAI Scheduler.** Określ wymagania dotyczące planowania grupowego (gang scheduling) – obowiązkowe w przypadku konfiguracji TP/PP > 1. Zdefiniuj ograniczenia topologiczne (domena NVLink, szafa rack, strefa dostępności). Określ hierarchię kolejek oraz zasady wywłaszczania (preemption) zadań dla zasobów produkcyjnych i szkoleniowych.
3. **Warstwa 3 — Autoskaler na poziomie aplikacji.** Dobierz odpowiedni wyzwalacz skalowania: głębokość kolejki (queue depth) dla zadań typu prefill, stopień zajętości KV Cache dla zadań typu decoding lub hybrydowe metryki goodput dla zadań mieszanych. Zabroń stosowania metryki `DCGM_FI_DEV_GPU_UTIL` i wyjaśnij uzasadnienie tej decyzji.
4. **Skalowanie w architekturze zdezagregowanej.** Jeśli stosowana jest architektura zdezagregowanego prefill/decode (faza 17 · 17), zdefiniuj osobne mechanizmy HPA: skalowanie puli prefill w oparciu o głębokość kolejki zapytań oraz skalowanie puli decoding w oparciu o poziom zajętości KV Cache.
5. **Rozmiar ciepłej puli replik (warm pool).** Określ minimalną liczbę stale aktywnych replik dla ścieżek krytycznych pod kątem SLO na podstawie percentyla P99 TTFT oraz zmierzonego czasu zimnego startu instancji (czas udostępnienia maszyny w chmurze + czas ładowania modelu do pamięci GPU).
6. **Monitorowanie.** Wskaż kluczowe metryki do wizualizacji na pulpicie nawigacyjnym: głębokość kolejki na replikę, poziom zajętości KV Cache na replikę, czas oczekiwania na udostępnienie węzła, liczba odrzuconych/odłożonych zadań w planowaniu grupowym, zdarzenia konsolidacji wyzwalane przez Karpentera.

Bezwzględne odrzucenie planu w przypadku:

- Rekomendowania konfiguracji HPA w oparciu o metrykę `DCGM_FI_DEV_GPU_UTIL`. Odrzuć taki projekt i wskaż głębokość kolejki oraz zajętość KV Cache jako jedyne prawidłowe sygnały.
- Pozostawienia domyślnej polityki `consolidationPolicy: WhenEmptyOrUnderutilized` dla puli maszyn z GPU. Wymagaj zmiany ze względu na ryzyko przerywania aktywnych procesów wnioskowania.
- Pominięcia mechanizmu planowania grupowego (gang scheduling) w przypadku obciążeń typu TP/PP. Brak tego mechanizmu to antywzorzec prowadzący do marnowania budżetu na częściowo alokowane zasoby.

Zasady weryfikacji i odmowy:

- Jeśli klaster dysponuje tylko jednym typem GPU i składa się z pojedynczego węzła, odrzuć wdrażanie Karpentera – w tym scenariuszu klient powinien najpierw rozważyć zarządzane usługi bezserwerowe (faza 17 · 02).
- Jeśli operator żąda konfiguracji autoskalowania na podstawie ogólnego zużycia pamięci GPU (VRAM), odrzuć tę prośbę – vLLM alokuje całą pamięć (zgodnie z `--gpu-memory-utilization`) zaraz po starcie, co sprawia, że wskaźnik ten stale wynosi ok. 90% niezależnie od liczby obsługiwanych zapytań.
- Jeśli projekt zakłada wyłączenie planowania grupowego dla obciążeń skali TP-8 ze względu na złożoność konfiguracji, odmów zatwierdzenia planu – uruchomienie pojedynczego logicznego podu na 8 rozproszonych maszynach z GPU wymaga atomowej koordynacji startu.

Format wyjściowy: Jednostronicowy plan zawierający fragment kodu YAML dla Karpentera, konfigurację KAI Schedulera, dobór sygnału dla HPA/autoskalera aplikacji, rozmiar ciepłej puli replik oraz pięć kluczowych metryk do wizualizacji na pulpicie nawigacyjnym. Zakończ określeniem reguły awaryjnej (fail-safe): jeśli percentyl P99 TTFT przekroczy dopuszczalne limity, przywróć ostatnią znaną stabilną konfigurację autoskalowania.
