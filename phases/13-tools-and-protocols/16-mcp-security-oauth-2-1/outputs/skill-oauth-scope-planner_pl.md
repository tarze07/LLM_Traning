---

name: oauth-scope-planner
description: Zaprojektuj zestaw zakresów OAuth 2.1, reguły przypinania i zasady zwiększania poziomu dla zdalnego serwera MCP.
version: 1.0.0
phase: 13
lesson: 16
tags: [oauth, pkce, resource-indicators, step-up, sep-835]

---

Mając zdalny serwer MCP z listą narzędzi, zaprojektuj model autoryzacji.

Wyprodukuj:

1. Hierarchia zakresu. Zestaw stopniowanych zakresów (np. `read` -> `write` -> `delete` -> `admin`). Jeden zakres na klasę operacyjną; nie eksploduj zestawu lunety.
2. Mapowanie zakresu do narzędzia. Każde narzędzie ma adnotację z wymaganym zakresem. Oznacz dowolne narzędzie, które wymaga więcej niż jednego zakresu.
3. Polityka step-up. Które operacje wymagają przyspieszenia, a nie wstępnej zgody. Typowe: destrukcyjne operacje wymagają wzmożenia działań.
4. Wartość wskaźnika zasobu. Kanoniczny adres URL używany w parametrze `resource`. Upewnij się, że adres URL jest zgodny z polem zasobu `.well-known/oauth-protected-resource`.
5. Metadane zasobów chronionych. Wersja robocza `.well-known/oauth-protected-resource` JSON z `authorization_servers`, `scopes_supported` i `resource`.

Twarde odrzucenia:
- Każde narzędzie wymagające zakresu administratora, ale wywoływane bez wyraźnego okna dialogowego potwierdzenia. Potrzebuje wzmocnienia.
- Dowolny zakres obejmujący więcej niż jedną klasę operacji. Pełzanie przywilejów.
- Dowolny serwer, który pomija weryfikację odbiorców. Luka w zabezpieczeniach zdezorientowanego zastępcy.

Zasady odmowy:
- Jeśli serwer jest lokalny (stdio), odrzuć OAuth i podaj, że stdio dziedziczy zaufanie nadrzędne.
- Jeśli serwer zależy od starszego, ukrytego przepływu OAuth 2.0, odmów i zlec migrację do wersji 2.1 + PKCE.
- Jeśli użytkownik poprosi o autoryzację „tylko klucz API” bez hasła, odmów w przypadku serwerów zdalnych; wymagają kodu autoryzacyjnego OAuth 2.1 + PKCE ze wskaźnikami zasobów dla dostępu autoryzowanego przez użytkownika. Poświadczenia klienta są odpowiednie tylko w przypadku scenariuszy między maszynami bez delegowania użytkowników.

Dane wyjściowe: jednostronicowy plan autoryzacji z hierarchią zakresu, mapowaniem zakresu do narzędzia, zasadami zwiększania poziomu, wskaźnikiem zasobów i metadanymi JSON chronionych zasobów. Zakończ operację zwiększania poziomu, która najprawdopodobniej zaskoczy użytkowników przy pierwszym spotkaniu.