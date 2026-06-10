---

name: mcp-server-designer
description: Zaprojektuj i wygeneruj strukturę serwera MCP z narzędziami, zasobami i domyślnymi zabezpieczeniami.
version: 1.0.0
phase: 11
lesson: 14
tags: [llm-engineering, mcp, tool-use]

---

Biorąc pod uwagę domenę docelową (wewnętrzne API, baza danych, system plików) oraz hosty nadrzędne, które zamontują serwer MCP, wygeneruj:

1. **Mapę prymitywów (Primitives Map):** Określenie, które funkcjonalności stają się narzędziami (`tools` - akcje), które zasobami (`resources` - dane tylko do odczytu), a które szablonami promptów (`prompts` - wywoływane przez użytkownika). Jedna linia opisu na każdy prymityw.
2. **Plan autoryzacji:** Wybór i uzasadnienie protokołu transportowego (Stdio dla zaufanego środowiska lokalnego, strumieniowy HTTP z kluczem API dla zespołów lub OAuth 2.1 z PKCE).
3. **Szkice schematów:** Schemat JSON Schema dla każdego parametru wejściowego narzędzi z polami `description` zoptymalizowanymi pod kątem precyzyjnego wyboru narzędzi przez model LLM (opisy celowane na intencję, a nie sucha dokumentacja techniczna API).
4. **Listę operacji destrukcyjnych:** Identyfikacja wszystkich narzędzi modyfikujących stan systemu, które wymagają wdrożenia flagi `destructiveHint: true` oraz zatwierdzenia operacji przez człowieka (Human-in-the-Loop).
5. **Plan testów:** Dla każdego narzędzia zdefiniuj jeden test kontraktowy zgodności schematu, jeden test integracyjny typu round-trip przez klienta MCP oraz jeden scenariusz testowy odporności na wstrzykiwanie promptów (prompt injection).

Zablokuj wdrożenie serwera, który dokonuje zapisu na dysku lub wywołuje zewnętrzne interfejsy API bez wdrożonej ścieżki akceptacji. Nie udostępniaj więcej niż 20 narzędzi w ramach jednego serwera MCP – w przypadku większych systemów podziel funkcjonalności na osobne serwery zorientowane domenowo.
