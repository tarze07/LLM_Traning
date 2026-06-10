---

name: mcp-server-designer
description: Zaprojektuj i zbuduj serwer MCP z narzędziami, zasobami i domyślnymi ustawieniami bezpieczeństwa.
version: 1.0.0
phase: 11
lesson: 14
tags: [llm-engineering, mcp, tool-use]

---

Biorąc pod uwagę domenę (wewnętrzny interfejs API, bazę danych, źródło pliku) i hosty, które zamontują serwer, wypisz:

1. Mapa prymitywna. Które możliwości stają się `tools` (akcja), które stają się `resources` (dane tylko do odczytu), a które stają się `prompts` (szablony wywoływane przez użytkownika). Jedna linia na element pierwotny.
2. Plan autoryzacji. Stdio (zaufany lokalnie), strumieniowy protokół HTTP z kluczem API lub OAuth 2.1 z PKCE. Wybierz i uzasadnij.
3. Projekt schematu. Schemat JSON dla każdego parametru narzędzia, z polami `description` dostrojonymi do wyboru narzędzia modelu (nie dokumentacja API).
4. Lista działań destrukcyjnych. Każde narzędzie zmieniające stan; wymagają `destructiveHint: true` i zgody człowieka.
5. Plan testów. Na narzędzie: jeden test kontraktu obejmujący tylko schemat, jeden test w obie strony przez klienta MCP, jeden przypadek szybkiego wstrzyknięcia przez zespół czerwony.

Odmów dostarczenia serwera, który zapisuje na dysk lub wywołuje zewnętrzne interfejsy API bez ścieżki zatwierdzenia. Odmawiaj udostępniania więcej niż 20 narzędzi na jednym serwerze; zamiast tego podzielić na serwery o zasięgu domeny.