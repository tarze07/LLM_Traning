---

name: batch-triager
description: Klasyfikacja zadań LLM na interaktywne, półinteraktywne i wsadowe, obliczanie skumulowanych oszczędności (Batch + Cache) oraz identyfikowanie błędnie przypisanych obciążeń.
version: 1.0.0
phase: 17
lesson: 15
tags: [batch-api, openai-batch, anthropic-batches, vertex-batch, triage, cost]

---

Na podstawie charakterystyki zadania (nazwa, dopuszczalne opóźnienie oczekiwane przez użytkownika, wolumen ruchu, struktura wspólnego promptu), stwórz plan klasyfikacji i optymalizacji kosztów.

Przygotuj:

1. Przypisanie do ścieżki (routing): Interaktywna (kluczowy wskaźnik TTFT, tryb synchroniczny), półinteraktywna (akceptowalne kilkuminutowe opóźnienie, kolejka asynchroniczna) lub wsadowa (wyniki wymagane na rano, Batch API). Uzasadnij wybór realnymi potrzebami użytkownika.
2. Koszt obecny: Oblicz miesięczne koszty przy aktualnej konfiguracji (np. zapytania synchroniczne, brak cache).
3. Koszt docelowy: Oblicz szacowane koszty po wdrożeniu optymalizacji (Batch + Cache lub synchroniczne + Cache) wyrażone jako procent kosztów obecnych.
4. Plan migracji: Kroki wdrożeniowe specyficzne dla dostawcy API (wybierz właściwego dostawcę):
   - OpenAI: migracja na `/v1/batches`. Prompt caching włącza się automatycznie dla kwalifikujących się zapytań (≥1024 tokenów) – brak konieczności konfiguracji `cache_control`.
   - Anthropic: migracja na Message Batches. Ponowne użycie cache wymaga jawnego oznaczenia bloków jako `cache_control` (np. `{"type": "ephemeral"}`) w szablonie promptu; rabat wsadowy łączy się ze zniżką za odczyt z cache.
   - Wspólne dla obu: wdrożenie webhooków powiadamiających o statusie zadania (sukces/błąd) oraz mechanizmu awaryjnego (fallback to sync) w razie opóźnień w realizacji kolejki wsadowej.
5. Analizę ryzyka: Co się stanie, jeśli czas realizacji w percentylu P99 osiągnie 20 godzin? Zdefiniuj mechanizmy rezerwowe (np. wysłanie raportu mailem, przeniesienie zadań krytycznych do kolejki synchronicznej).
6. Metryki i monitorowanie (Observability): Wskaźnik wykrywający błędną klasyfikację zadań – opóźnienie zakończenia zadań wsadowych w percentylu P95. Skonfiguruj alert, gdy czas ten przekroczy 12 godzin.

Kryteria odrzucenia planu:
- Uruchamianie nocnych potoków danych w trybie synchronicznym (bez Batch API), gdy biznes wymaga jedynie dostarczenia wyników „na rano”. Odrzuć taki plan – wykaż stratę finansową sięgającą ~90%.
- Proponowanie Batch API dla zadań, w których użytkownik oczekuje wyniku w czasie krótszym niż 15 minut. Odrzuć – SLA dla trybu wsadowego to 24 godziny.
- Ignorowanie możliwości buforowania promptów (prompt caching) dla zadań wsadowych posiadających wspólny prompt systemowy. Odrzuć – kluczem do oszczędności jest łączenie obu rabatów.

Zasady odmowy/zastrzeżenia:
- Jeśli zadanie jest reklamowane jako działające „w czasie rzeczywistym”, ale rzeczywiste wymagania użytkownika dopuszczają opóźnienie kilkuminutowe, przed rekomendacją Batch API wymagane jest potwierdzenie biznesowe.
- Jeśli zadanie kierowane jest do dostawcy nieobsługującego buforowania promptów w trybie wsadowym (np. własna infrastruktura bez ponownego użycia prefiksów KV), uwzględnij wyłącznie standardowy rabat 50% bez łączenia z prompt caching. Automatyczne buforowanie wsadowe OpenAI działa samoistnie; buforowanie wsadowe Anthropic wymaga jawnych bloków `cache_control`.
- Jeśli zadanie ma restrykcyjne SLA dotyczące opóźnień (np. P99 < 60 sekund), kategorycznie odrzuć tryb wsadowy i skieruj je na ścieżkę synchroniczną.

Format końcowy: Jednostronicowy raport z klasyfikacji zawierający: przypisaną ścieżkę, koszt obecny, koszt docelowy, etapy migracji, analizę ryzyka oraz zalecane metryki monitorowania. Raport należy zakończyć rekomendacją kwartalnego przeglądu – ponownej klasyfikacji zadań LLM wraz z rozwojem funkcjonalności systemu.
