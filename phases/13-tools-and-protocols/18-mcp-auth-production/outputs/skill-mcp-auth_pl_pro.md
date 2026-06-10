---

name: mcp-auth-wiring
description: Projekt wdrożenia autoryzacji MCP (zgodny z RFC 8414, CIMD, RFC 7591, RFC 8707, RFC 7636 PKCE, RFC 9728, RFC 9207) — obejmujący projekt metadanych zasobów chronionych, rejestrację klientów, odświeżanie JWKS oraz walidację tokenów w locie.
version: 1.1.0
phase: 13
lesson: 18
tags: [mcp, oauth, cimd, dcr, jwks, rfc8414, rfc7591, rfc8707, rfc7636, rfc9728, rfc9207]

---

Na podstawie specyfikacji serwera MCP oraz profilu możliwości dostawcy tożsamości (IdP) opracuj kompletną architekturę bezpieczeństwa i reguły walidacji dla produkcyjnej warstwy autoryzacji MCP.

Parametry wejściowe:
- `mcp_resource_url` — kanoniczny adres URL zasobu (najbardziej szczegółowy identyfikator; zachowaj ścieżkę tylko wtedy, gdy służy do rozróżniania współdzielonych serwerów), używany jako pole `aud` w tokenie oraz wartość `resource` w metadanych chronionego zasobu.
- `idp_metadata_url` — adres URL pliku metadanych dostawcy tożsamości (`/.well-known/oauth-authorization-server` lub OpenID Connect Discovery).
- `idp_capabilities` — zweryfikowane możliwości dostawcy tożsamości w zakresie: `code_challenge_methods_supported`, `grant_types_supported`, `client_id_metadata_document_supported` (CIMD), `registration_endpoint` (DCR), `response_types_supported` oraz `authorization_response_iss_parameter_supported` (RFC 9207).
- `tools` — wykaz narzędzi MCP wraz z przypisanymi im zakresami uprawnień.

Wygeneruj następujące sekcje:

1. **Reguły kategorycznego odrzucenia (Gatekeeper).** Natychmiast odrzuć projekt, jeśli którykolwiek z poniższych warunków nie jest spełniony:
   - Brak obsługi metody `S256` w polu `code_challenge_methods_supported` (PKCE jest obligatoryjne; brak trybu awaryjnego).
   - Brak typu grantu `authorization_code` w polu `grant_types_supported`.
   - Parametr `response_types_supported` zawiera wartości inne niż dokładnie `["code"]`.
   - Brak jakiejkolwiek metody rejestracji klientów (brak statycznej konfiguracji `client_id`, brak obsługi CIMD (`client_id_metadata_document_supported: true`) oraz brak punktu rejestracji DCR (`registration_endpoint`)). Dowolna z tych metod jest wystarczająca — brak samego DCR nie stanowi powodu do odrzucenia (w specyfikacji z 25.11.2025 r. status DCR obniżono do `MAY`, a standardem domyślnym stał się CIMD).

2. **Dokument metadanych chronionego zasobu** (RFC 9728) dla serwera MCP (publikowany pod adresem `/.well-known/oauth-protected-resource`). Powinien zawierać pola: `resource`, `authorization_servers` (lista zaufanych wystawców), `scopes_supported` oraz `bearer_methods_supported: ["header"]`.

3. **Punkty końcowe HTTP.**
   - `GET /.well-known/oauth-protected-resource` — zwracający dokument metadanych zasobu chronionego.
   - `POST /mcp` (kanał transportu MCP) — realizujący walidację tokenu przed wykonaniem jakiejkolwiek operacji na narzędziach.
   - `POST /register` (tylko w przypadku wyboru ścieżki DCR) — punkt rejestracji zabezpieczony limitem żądań (rate limiting).

4. **Zadania w tle i procedury.**
   - Cykliczne odświeżanie JWKS — pobieranie danych z adresu `jwks_uri` i aktualizacja lokalnego bufora `{keys, fetched_at}`. Operacja musi być idempotentna (serwer zasobów nigdy nie inicjuje rotacji kluczy kryptograficznych – rotacją zarządza serwer autoryzacji, serwer zasobów jedynie odświeża lokalny bufor). Zalecany interwał: `0 */6 * * *` (lub `*/15 * * * *` dla systemów o częstej rotacji).
   - Procedura `validate` — weryfikująca zaufanego wystawcę (`iss`), podpis tokenu z użyciem bufora JWKS, zgodność pola odbiorcy (`aud == mcp_resource_url`), czas ważności (`exp`) oraz wymagane zakresy uprawnień.
   - Przepływ eskalacji autoryzacji (step-up Flow) — mechanizm obsługi żądań o rozszerzenie uprawnień w przypadku wywołania narzędzi wymagających dodatkowych zakresów.

5. **Projekt pamięci podręcznej.** Struktura słownika pamięci podręcznej kluczy dla zaufanych wystawców zawierająca pola `{keys, fetched_at}`. Udokumentuj algorytm odczytu: moduł walidacji odczytuje klucze z pamięci podręcznej, a w przypadku braku dopasowania identyfikatora `kid` wykonuje jednorazowe, synchroniczne pobranie kluczy w locie (on-demand refetch, a nie generowanie kluczy — pobranie jest idempotentne i eliminuje ryzyko ataku DoS polegającego na przeciążeniu operacjami kryptograficznymi).

6. **Mapowanie narzędzi do zakresów.** Przypisanie zakresu uprawnień do każdego narzędzia. Przedstaw dane w postaci tabeli:
   `| tool | required_scope | rationale |`.
   Przypisz osobnym, dedykowanym zakresom narzędzia o charakterze destrukcyjnym; nigdy nie przypisuj zakresu odczytu (read) do operacji zapisu (write).

7. **Reguły odmowy w czasie wykonywania (Runtime Deny Rules):**
   - Odrzuć żądanie, gdy `aud != mcp_resource_url` → kod 401 z nagłówkiem `Bearer error="invalid_token", error_description="audience mismatch", resource_metadata="<prm_url>"`.
   - Odrzuć żądanie, gdy wystawca `iss` nie znajduje się na liście zaufanych serwerów `authorization_servers`.
   - Odrzuć żądanie, gdy identyfikator klucza `kid` jest nieznany nawet po wykonaniu awaryjnego odświeżenia bufora JWKS.
   - Odrzuć żądanie w przypadku braku wymaganego zakresu → kod 403 z nagłówkiem `Bearer error="insufficient_scope", scope="<required>", resource_metadata="<prm_url>"`.
   - Odrzuć każde żądanie wydania tokenu pozbawione parametrów `code_verifier` lub `resource`.

Kategoryczne kryteria odrzucenia projektu (nie dopuszczaj żadnego z poniższych rozwiązań):
- Przechowywanie tokenu `registration_access_token` lub danych uwierzytelniających w bazie w postaci otwartego tekstu (wymagane haszowanie w spoczynku i przesyłanie w bezpiecznym kanale).
- Pomijanie weryfikacji pola `aud` (odbiorca) w procesie walidacji (naruszenie mechanizmu wiązania odbiorców).
- Powiązanie procedury obsługi braku klucza w cache z żądaniem generowania nowych kluczy (rotate-and-mint) zamiast pobrania JWKS z serwera autoryzacji (podatność DoS).
- Zezwalanie na autoryzację bez PKCE w przepływie kodu autoryzacji (niezgodność z OAuth 2.1).
- Buforowanie JWKS bez zdefiniowania cyklicznego zadania aktualizacji bufora.
- Walidacja tokenów od dowolnego wystawcy bez weryfikacji z listą zaufanych serwerów `authorization_servers`.
- Przekazywanie tokenów klienckich MCP do zewnętrznych, nadrzędnych systemów API (antywzorzec rodzący podatność typu confused deputy).

Format wyjściowy: Jednostronicowy plan wdrożenia zawierający specyfikację metadanych chronionego zasobu, wybór ścieżki rejestracji (CIMD / statyczna / DCR), opis punktów końcowych HTTP, konfigurację zadania aktualizacji JWKS, architekturę pamięci podręcznej, tabelę mapowania zakresów oraz zestaw reguł odmowy w czasie wykonywania. Na końcu wskaż jedną, kluczową barierę wdrożeniową dla wybranego dostawcy tożsamości – na przykład brak wsparcia dla standardu CIMD i konieczność weryfikacji obsługi DCR w korporacyjnych systemach SSO.
