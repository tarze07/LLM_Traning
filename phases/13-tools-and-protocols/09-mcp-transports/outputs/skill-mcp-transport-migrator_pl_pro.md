---

name: mcp-transport-migrator
description: Przygotuj plan migracji ze starszego transportu HTTP+SSE do Streamable HTTP, uwzględniając ciągłość identyfikatora sesji oraz walidację Origin.
version: 1.0.0
phase: 13
lesson: 09
tags: [mcp, streamable-http, sse-migration, session-id, origin]

---

Na podstawie istniejącego serwera MCP korzystającego ze starszego transportu HTTP+SSE przygotuj plan migracji do Streamable HTTP opartego o pojedynczy punkt końcowy.

Wygeneruj:

1. Przebudowa punktów końcowych. Skonsoliduj punkty `/messages` i `/sse` w jeden `/mcp`. Mapuj metodę POST na obsługę żądań, GET na nasłuchiwanie strumienia SSE, a DELETE na zamykanie sesji.
2. Zarządzanie sesją. Wygeneruj bezpieczny identyfikator `Mcp-Session-Id` przy pierwszym zapytaniu POST. Odrzucaj identyfikatory proponowane przez klienta. Jeśli to konieczne, zaimplementuj logikę przejściową obsługującą starsze identyfikatory sesji.
3. Walidacja nagłówka Origin. Zdefiniuj listę dozwolonych domen (np. `https://app.company.com`, `https://claude.ai` oraz adresy lokalne). Wszystkie pozostałe żądania odrzucaj kodem HTTP 403.
4. Odtwarzanie zaległych komunikatów. Zaimplementuj bufor pierścieniowy (ring buffer) przechowujący ostatnie powiadomienia dla każdej sesji, aby umożliwić ich ponowne przesłanie po wznowieniu połączenia (nagłówek `last-event-id`).
5. Harmonogram wycofywania. Określ datę wdrożenia i zaplanuj 60-dniowy okres przejściowy, podczas którego starsze punkty końcowe będą zwracać przekierowanie HTTP 301 (lub 308) na nowy adres wraz z nagłówkiem Warning.

Kryteria odrzucenia (Twarde reguły):
- Utrzymywanie obsługi obu starszych punktów końcowych bezterminowo. Wsparcie dla starszego transportu SSE wygasa całkowicie w 2026 roku.
- Akceptowanie identyfikatorów sesji wygenerowanych przez klienta (łamie to wymaganie silnej losowości kryptograficznej).
- Brak weryfikacji nagłówka Origin (powoduje to podatność serwera na ataki DNS Rebinding).

Zasady odmowy usługi:
- Jeśli serwer działa lokalnie w oparciu o transport stdio, odmów migracji do HTTP (stdio jest optymalne i prawidłowe dla procesów lokalnych).
- Jeśli publicznie dostępny serwer nie obsługuje jeszcze protokołu OAuth, zablokuj migrację do momentu wdrożenia zasad z fazy 13 · 16.
- Jeśli infrastruktura docelowa nie obsługuje długo otwartych połączeń HTTP (np. darmowy pakiet Vercel), odmów weryfikacji i rekomenduj użycie platformy Cloudflare Workers.

Format wyjściowy: Instrukcja migracji (Runbook) opisująca zmiany punktów końcowych, konfigurację listy Origin, strategię przydzielania identyfikatorów sesji, harmonogram wygaszania starszych usług oraz listę kontrolną testów (inicjalizacja, pobieranie listy narzędzi, strumieniowanie powiadomień, wznawianie połączenia na podstawie `last-event-id` oraz jawne zamknięcie sesji żądaniem DELETE).
