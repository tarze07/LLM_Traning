---

name: a2a-integrator
description: Zaprojektuj integrację A2A pomiędzy dwoma agentami — kartą agenta, schematami zadań, uwierzytelnianiem, przesyłaniem strumieniowym lub odpytywaniem.
version: 1.0.0
phase: 16
lesson: 12
tags: [multi-agent, a2a, protocol, interoperability, google]

---

Biorąc pod uwagę dwa systemy agentów, które muszą ze sobą współdziałać, utwórz plan integracji A2A: zawartość karty agenta, schematy zadań, uwierzytelnianie, tryb transportu.

Wyprodukuj:

1. **Karta agenta.** Nazwa, wersja, umiejętności, punkty końcowe, obsługiwane modalności (tekst, struktura, obraz, audio, wideo), wersja_protokołu, deklaracja autoryzacji.
2. **Schematy zadań według umiejętności.** Wprowadź schemat JSON + schemat JSON artefaktu. Bądź wyraźny – klienci to zweryfikują.
3. **Wybór uwierzytelnienia.** Token okaziciela (OAuth2 lub nieprzezroczysty), mTLS lub podpisane żądania. Uzasadnij, biorąc pod uwagę model zagrożenia (internet publiczny, VPC, mieszany).
4. **Tryb transportu.** Odpytywanie, przesyłanie strumieniowe SSE i wywołania zwrotne webhooka. Przesyłanie strumieniowe w przypadku zadań długotrwałych lub wymagających dużego postępu; odpytywanie o krótkie zadania.
5. **Limity stawek.** Limity na klienta i na zadanie. Ochrona przed nadużyciami.
6. **Idempotencja.** Strategia dla zduplikowanych żądań `POST /tasks` (klucz zadania po stronie klienta, deduplikacja po stronie serwera).
7. **Obsługa awarii.** Stany zadań wykraczające poza `failed` (możliwość ponownego wykonania lub wykonanie krytyczne), zasady dotyczące niedostarczonych wiadomości, schemat artefaktów błędów.
8. **Podział MCP i A2A.** Jeśli zdalny agent korzysta wewnętrznie z MCP, zwróć uwagę, które narzędzia są dostępne, a które przechowywane wewnętrznie.

Twarde odrzucenia:

- Karty Agentów bez zadeklarowanej wersji protokołu.
- Schematy zadań, które są tekstem w dowolnej formie, gdy przypadek użycia wymaga struktury.
- Auth=none w przypadku wdrożeń w Internecie publicznym.

Zasady odmowy:

- Jeśli obaj agenci działają w tym samym procesie, odrzuć A2A i zaleć bezpośrednie wywołania Pythona/JS. A2A dotyczy granic międzysystemowych.
— Jeśli wymagania dotyczące opóźnienia w obie strony są mniejsze niż 100 ms, odrzuć A2A i zaleć bezpośrednie RPC ze wspólnym schematem.
- Jeśli zdalny agent nie zadeklaruje Karty Agenta, odmów integracji i zaleć najpierw jej opublikowanie.

Wynik: jednostronicowy opis integracji. Zamknij za pomocą wklejonej karty agenta JSON, aby inżynierowie mogli upuścić ją w `/.well-known/agent.json`.