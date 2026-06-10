---

name: oauth-scope-planner
description: Zaprojektuj strukturę zakresów uprawnień OAuth 2.1, reguły przypisywania odbiorców (resource indicators) oraz zasady eskalacji autoryzacji (step-up) dla zdalnego serwera MCP.
version: 1.0.0
phase: 13
lesson: 16
tags: [oauth, pkce, resource-indicators, step-up, sep-835]

---

Na podstawie specyfikacji zdalnego serwera MCP wraz z listą udostępnianych narzędzi zaprojektuj model autoryzacji.

Wygeneruj następujące sekcje:

1. Hierarchia zakresów. Zestaw stopniowanych zakresów (np. `read` -> `write` -> `delete` -> `admin`). Zdefiniuj po jednym zakresie na klasę operacji; unikaj nadmiernego rozdrobnienia i eksplozji liczby zakresów.
2. Mapowanie narzędzi do zakresów. Przypisanie wymaganego zakresu do każdego narzędzia. Wskaż narzędzia, które wymagają więcej niż jednego zakresu.
3. Polityka eskalacji autoryzacji (Step-up). Określenie, które operacje wymagają dynamicznej eskalacji uprawnień (step-up) zamiast wstępnej zgody użytkownika. Standardowo: operacje destrukcyjne powinny wymagać eskalacji.
4. Identyfikator zasobu. Kanoniczny adres URL przekazywany w parametrze `resource`. Upewnij się, że adres URL jest spójny z polem `resource` w pliku `.well-known/oauth-protected-resource`.
5. Metadane zasobów chronionych. Projekt struktury JSON pliku `.well-known/oauth-protected-resource` zawierający pola: `authorization_servers`, `scopes_supported` oraz `resource`.

Kategoryczne odrzucenia:
- Dowolne narzędzie wymagające uprawnień administratora (admin), które może być wywołane bez wyraźnego potwierdzenia przez użytkownika. Wymaga ono eskalacji autoryzacji (step-up).
- Dowolny zakres obejmujący więcej niż jedną klasę operacji (ryzyko nadmiarowych uprawnień - privilege creep).
- Dowolny serwer, który pomija weryfikację odbiorcy (audience check) – podatność na atak typu "zdezorientowany zastępca" (confused deputy).

Reguły odmowy:
- Jeśli serwer komunikuje się lokalnie (stdio), odrzuć konfigurację OAuth i wskaż, że transport stdio dziedziczy poziom zaufania z procesu nadrzędnego.
- Jeśli serwer opiera się na przestarzałym, ukrytym przepływie (implicit flow) OAuth 2.0, odrzuć konfigurację i nakaż migrację do OAuth 2.1 + PKCE.
- Jeśli użytkownik żąda uwierzytelniania za pomocą samego klucza API (API key only) bez dodatkowych zabezpieczeń dla serwerów zdalnych, odrzuć żądanie. Serwery zdalne wymagają przepływu Authorization Code Flow w standardzie OAuth 2.1 + PKCE z użyciem wskaźników zasobów do autoryzacji operacji wykonywanych w imieniu użytkownika. Poświadczenia klienta (Client Credentials) są dopuszczalne wyłącznie w scenariuszach komunikacji maszynowej (M2M) bez udziału użytkownika.

Format wyjściowy: Jednostronicowy plan autoryzacji zawierający hierarchię zakresów, mapowanie narzędzi do zakresów, zasady eskalacji autoryzacji (step-up), identyfikator zasobu oraz strukturę JSON metadanych chronionych zasobów. Na końcu wskaż operację wymagającą eskalacji autoryzacji (step-up), która może być najbardziej zaskakująca dla użytkownika podczas pierwszej interakcji.
