---

name: vllm-stack-decider
description: Projektowanie architektury wdrożeniowej vLLM – wybór szablonu Helm (vLLM Production Stack), typu odciążania KV (vLLM Native CPU vs LMCache), integracji z routerem i warstwy monitorowania na podstawie specyfiki ruchu i wielkości infrastruktury.
version: 1.0.0
phase: 17
lesson: 18
tags: [vllm, production-stack, lmcache, kv-offload, connector-api]

---

Na podstawie profilu obciążenia (długość promptów, stopień współbieżności, powtarzalność prefiksów), floty GPU (liczba silników, model kart) oraz kontekstu operacyjnego (wdrożenie w Kubernetes, środowisko multi-tenant, budżet), opracuj plan wdrożenia stosu vLLM.

Przygotuj:

1. Wybór szablonu wdrożenia (Stos): Użycie oficjalnego repozytorium Helm Chart dla vLLM Production Stack (rekomendowane dla nowych wdrożeń) lub autorski schemat. Wskaż powiązane operatory i definicje CRD (Custom Resource Definitions).
2. Odciążanie KV-cache (KV Offloading): Wybór spośród opcji:
   - Brak (krótkie prompty, niska współbieżność – narzut sieciowy i wydajnościowy przewyższa korzyści).
   - Natywne odciążanie do CPU we vLLM (vLLM Native CPU offloading – optymalne przy ograniczeniach pamięci HBM na pojedynczym wdrożeniu/węźle).
   - Złącze LMCache (współdzielenie cache KV przez wiele silników, obciążenia podatne na wywłaszczanie zadań, systemy multi-tenant ze wspólnymi promptami).
3. Zarządzanie pamięcią GPU: Konfiguracja parametru `--gpu-memory-utilization` z odpowiednim marginesem bezpieczeństwa; alerty przy zajętości pamięci 92%+ jako wczesne ostrzeganie przed wywłaszczeniem (eviction).
4. Integrację z routerem (Cache-Aware Routing): Router świadomy cache (opisany w fazie 17 · 11). Zweryfikuj konfigurację kanału zdarzeń KV-cache.
5. Monitorowanie (Observability): Zbieranie metryk z vLLM przez Prometheus, wdrożenie atrybutów OpenTelemetry GenAI (opisywanych w fazie 17 · 13), integracja z szablonem dashboardu Grafana dostarczanym wraz z vLLM Production Stack.
6. Prognozę efektów: Szacowany wzrost przepustowości w odniesieniu do parametrów wyjściowych (z uwzględnieniem benchmarków na klastrze 16x H100, gdzie LMCache drastycznie poprawia throughput przy przepełnieniu HBM).

Kryteria odrzucenia planu:
- Rekomendowanie wdrożenia LMCache w środowisku bez współdzielenia prefiksów promptów oraz bez problemów z wywłaszczaniem (preemption). Odrzuć – generuje to wyłącznie narzut bez żadnych korzyści.
- Uruchamianie klastra vLLM bez skonfigurowanego monitorowania zajętości pamięci HBM. Odrzuć – brak kontroli doprowadzi do nagłych błędów oznaczających odrzucanie zapytań.
- Tworzenie własnej konfiguracji wdrożeniowej (manual configuration) od podstaw w sytuacji, gdy oficjalne szablony Helm w pełni pokrywają dany przypadek użycia. Odrzuć – to marnotrawstwo czasu i budżetu.

Zasady odmowy/zastrzeżenia:
- Jeśli flota składa się z mniej niż 2 instancji modelu (silników), odrzuć LMCache (jego główną zaletą jest współdzielenie danych między instancjami); zalecaj natywne odciążanie na pojedynczym węźle.
- Jeśli zadanie operuje na promptach krótszych niż 1K tokenów przy współbieżności poniżej 100 zapytań, odrzuć plany odciążania – wolna pamięć HBM jest w pełni wystarczająca.
- Jeśli zespół nie posiada doświadczenia w administracji Kubernetes, odrzuć vLLM Production Stack – rekomenduj uruchomienie pojedynczych kontenerów vLLM z prostym serwerem proxy.

Format końcowy: Jednostronicowa decyzja architektoniczna określająca: schemat wdrożenia stosu, metodę odciążania KV-cache, strategię monitorowania pamięci HBM, integrację z routerem, plan monitorowania i prognozowane zyski. Raport należy zakończyć zdefiniowaniem kluczowej bramki kontrolnej: zajętości pamięci HBM w 99. percentylu (P99) w ciągu ostatnich 24 godzin.
