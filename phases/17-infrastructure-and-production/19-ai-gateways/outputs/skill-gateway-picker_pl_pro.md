---

name: gateway-picker
description: Wybór bramy AI (LiteLLM, Portkey, Kong AI Gateway, Cloudflare/Vercel AI Gateway) na podstawie skali ruchu, budżetu opóźnień, wymagań prawnych i zgodności oraz budżetu operacyjnego.
version: 1.0.0
phase: 17
lesson: 19
tags: [ai-gateway, litellm, portkey, kong, cloudflare, vercel, bifrost, fallback, rate-limit, guardrails]

---

Na podstawie natężenia ruchu w RPS (bieżący oraz prognozowany na kolejne 12 miesięcy), budżetu opóźnień, wymagań zgodności prawnej (czy konieczne jest wdrożenie self-hosted), bezpieczeństwa (anonimizacja PII, detekcja jailbreak, log audytowy) oraz budżetu, przygotuj rekomendację wyboru bramy AI.

Przygotuj:

1. Rekomendację bramy podstawowej: Wskazanie konkretnego rozwiązania i uzasadnienie wyboru na podstawie dopuszczalnego RPS, stabilności oraz wymaganych funkcji.
2. Definicję ścieżki awaryjnej (Fallback Chain): Wskazanie trzech dostawców w kolejności (np. OpenAI → Anthropic → własna instancja). Oszacowanie oczekiwanej dostępności (uptime) systemu.
3. Reguły limitowania zapytań (Rate Limiting Policy): Rekomendacja algorytmu przesuwanego okna (sliding window) przy ruchu >500 RPS; algorytm kubełkowy (token bucket) dopuszczalny przy mniejszej skali. Podział limitów na poziomy klientów (tenants).
4. Filtry bezpieczeństwa (Guardrails): Wybór Portkey, jeśli kluczowe jest maskowanie danych osobowych (PII) lub blokowanie ataków jailbreak; Kong w razie potrzeby połączenia dużej skali z barierami ochronnymi; LiteLLM wyłącznie do celów deweloperskich.
5. Konfigurację monitorowania: Integracja z metrykami z fazy 17 · 13 ze sprawdzeniem zachowania standardów OpenTelemetry GenAI.
6. Plan migracji: Etapy przełączania z komunikacji bezpośredniej (na poziomie aplikacji) na nową bramę AI (np. wdrożenie typu canary 1% ruchu i sukcesywne rozszerzanie skali).

Kryteria odrzucenia planu:
- Wdrażanie LiteLLM w środowiskach z ruchem >2000 RPS. Odrzuć – testy obciążeniowe wykazują podatność na błędy kaskadowe w takich warunkach; wymagana jest migracja na bardziej wydajny system.
- Rekomendowanie Portkey przy restrykcyjnym SLA na opóźnienia TTFT P99 < 100 ms. Odrzuć – narzut 20-40 ms na filtry bezpieczeństwa pochłania zbyt dużo dopuszczalnego czasu.
- Wybór Cloudflare AI Gateway dla klienta z regulowanego sektora wymagającego lokalnej instalacji (on-premise / self-hosted). Odrzuć – to usługa wyłącznie chmurowa.

Zasady odmowy/zastrzeżenia:
- Jeśli dynamika rozwoju ruchu jest niepewna (np. obecnie 100 RPS, ale planowany wzrost do >2000 RPS w 6 miesięcy), przed wdrożeniem LiteLLM wymagaj przedstawienia planu migracji na wydajniejszy system.
- Jeśli wymogi prawne nakładają posiadanie certyfikatu SOC 2 Type II, a rekomendowana brama to darmowy wariant open-source bez komercyjnego wsparcia (SLA), wymagane jest poświadczenie audytowe infrastruktury klienta.
- Jeśli zespół nie posiada infrastruktury Kubernetes ani kompetencji do jej utrzymania, a plan zakłada instalację Konga na własnych serwerach, odrzuć plan – zarekomenduj chmurę zarządzaną Kong Cloud lub zarządzany Portkey.

Format końcowy: Jednostronicowa decyzja architektoniczna zawierająca: wybraną bramę AI, strukturę ścieżki awaryjnej, politykę rate limitów, konfigurację filtrów bezpieczeństwa, model monitorowania oraz plan migracji. Raport należy zakończyć zdefiniowaniem kluczowej metryki alarmowej: opóźnienia P99 samej bramy AI w ujęciu godzinowym.
