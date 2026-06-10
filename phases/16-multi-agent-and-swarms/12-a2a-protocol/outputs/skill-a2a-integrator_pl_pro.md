---

name: a2a-integrator
description: Zaprojektuj integrację A2A pomiędzy dwoma agentami — określ zawartość karty agenta, schematy zadań, metody uwierzytelniania oraz protokół transportu (strumieniowanie lub odpytywanie).
version: 1.0.0
phase: 16
lesson: 12
tags: [multi-agent, a2a, protocol, interoperability, google]

---

Na podstawie charakterystyki dwóch systemów agentów wymagających integracji, opracuj plan integracji A2A określający: strukturę karty agenta, schematy zadań, mechanizm uwierzytelniania oraz tryb transportu danych.

Opracuj:

1. **Karta agenta (Agent Card).** Nazwa, wersja, lista umiejętności (skills), adresy punktów końcowych (endpoints), obsługiwane formaty danych (modalities: tekst, strukturyzowany JSON, obraz, audio, wideo), wersja protokołu oraz deklaracja autoryzacji.
2. **Schematy zadań dla poszczególnych umiejętności.** Zdefiniuj schemat JSON dla parametrów wejściowych oraz schemat JSON dla generowanego artefaktu. Specyfikacja must być precyzyjna, ponieważ klienci będą walidować te dane.
3. **Wybór metody uwierzytelniania.** Token okaziciela (Bearer token - OAuth2 lub nieprzezroczysty), mTLS lub podpisywanie żądań. Przedstaw uzasadnienie w oparciu o model zagrożeń (publiczny internet, sieć prywatna VPC, środowisko hybrydowe).
4. **Protokół transportu.** Odpytywanie (polling), strumieniowanie zdarzeń (SSE) lub wywołania zwrotne (webhooki). Zaleć strumieniowanie dla zadań długotrwałych lub wymagających monitorowania postępu; odpytywanie zarezerwuj dla zadań krótkich.
5. **Limity liczby żądań (Rate limits).** Limity na klienta oraz limity na zadanie, chroniące system przed przeciążeniem i nadużyciami.
6. **Idempotentność.** Strategia obsługi zduplikowanych żądań `POST /tasks` (generowanie unikalnego klucza zadania po stronie klienta i mechanizm deduplikacji po stronie serwera).
7. **Obsługa błędów.** Statusy zadań poza standardowym `failed` (możliwość ponowienia próby lub błąd krytyczny), polityka kolejki wiadomości niedostarczonych (dead-letter queue) oraz schemat JSON dla raportów błędów.
8. **Separacja MCP i A2A.** Jeśli zdalny agent wykorzystuje wewnętrznie architekturę MCP, wskaż, które narzędzia są eksponowane na zewnątrz, a które pozostają wyłącznie do użytku wewnętrznego.

Kryteria wykluczające:

- Karta Agenta bez zadeklarowanej wersji protokołu A2A.
- Definiowanie danych wejściowych zadania jako tekstu w dowolnej formie, gdy specyfika problemu wymaga danych strukturyzowanych.
- Brak uwierzytelniania (`auth: none`) dla punktów końcowych wystawionych w publicznym internecie.

Zasady odmowy (Rejection rules):

- Jeśli oba agenty działają w ramach jednego procesu, odrzuć protokół A2A i zaleć bezpośrednie wywołania w Pythonie/JS. A2A służy do komunikacji na granicach systemowych.
- Jeśli wymagane opóźnienie w obie strony (RTT) wynosi poniżej 100 ms, odrzuć A2A i zaleć bezpośrednie wywołanie RPC ze współdzielonym schematem danych.
- Jeśli zdalny agent nie udostępnia Karty Agenta, odrzuć integrację i wymagaj jej uprzedniego opublikowania.

Format wyjściowy: jednostronicowy opis projektu integracji. Na końcu umieść gotowy do wdrożenia plik JSON Karty Agenta, przeznaczony do publikacji pod adresem `/.well-known/agent.json`.
