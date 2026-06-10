---

name: mcp-auth-wiring
description: Autoryzacja MCP w trybie stand-up (RFC 8414, CIMD, 7591, 8707, 7636 PKCE, 9728, 9207) — metadane zasobów chronionych, rejestracja, odświeżanie JWKS i weryfikacja tokenu na żądanie.
version: 1.1.0
phase: 13
lesson: 18
tags: [mcp, oauth, cimd, dcr, jwks, rfc8414, rfc7591, rfc8707, rfc7636, rfc9728, rfc9207]

---

Biorąc pod uwagę konfigurację serwera MCP i zestaw możliwości dostawcy tożsamości, wyemituj powierzchnię uwierzytelniania i reguły odmowy, które tworzą produkcyjną warstwę autoryzacji MCP.

Wejścia:

- `mcp_resource_url` — kanoniczny adres URL zasobu (najbardziej szczegółowy identyfikator; zachowaj ścieżkę tylko wtedy, gdy rozróżnia serwery współhostowane), używany jako `aud` i jako wartość metadanych `resource` zasobu chronionego.
- `idp_metadata_url` — adres URL `/.well-known/oauth-authorization-server` (lub OpenID Connect Discovery) dostawcy tożsamości.
- `idp_capabilities` — zaobserwowane wartości dla `code_challenge_methods_supported`, `grant_types_supported`, `client_id_metadata_document_supported` (CIMD), `registration_endpoint` (DCR), `response_types_supported`, `authorization_response_iss_parameter_supported` (RFC 9207).
- `tools` — lista narzędzi MCP z wymaganym zakresem.

Wyprodukuj:

1. **Brama odmowy.** Odmów podłączenia i zatrzymaj się, jeśli jakikolwiek trudny warunek nie zostanie spełniony:
   - Brakuje `S256` w `code_challenge_methods_supported` (PKCE nie ma trybu zdegradowanego).
   - Brakuje `authorization_code` w `grant_types_supported`.
   - `response_types_supported` to coś innego niż dokładnie `["code"]`.
   - Nie istnieje żadna ścieżka rejestracji: żaden z wstępnie zarejestrowanych `client_id`, `client_id_metadata_document_supported: true` (CIMD) ani `registration_endpoint` (DCR) nie jest dostępny. Wystarczy dowolny — sama nieobecność DCR nie jest już odmową (2025-11-25 obniżono DCR do `MAY`; preferowanym ustawieniem domyślnym jest CIMD).

2. **Dokument metadanych dotyczących zasobów chronionych** (RFC 9728) dla serwera MCP do opublikowania w `/.well-known/oauth-protected-resource`. Obejmuje `resource`, `authorization_servers` (lista dozwolonych emitentów), `scopes_supported`, `bearer_methods_supported: ["header"]`.

3. **Punkty końcowe HTTP.**
   - `GET /.well-known/oauth-protected-resource` — zwraca dokument z (2).
   - `POST /mcp` (transport MCP) — przeprowadza weryfikację tokena przed wysłaniem jakiegokolwiek narzędzia.
   - (tylko ścieżka DCR) `POST /register` — rejestrator z przed sobą sprawdzaniem limitu szybkości.

4. **Praca w tle + procedury.**
   — Zaplanowane odświeżenie JWKS, które ponownie pobiera `jwks_uri` do pamięci podręcznej `{keys, fetched_at}`. idempotentny; nigdy nie bije kluczy. AS obraca się; serwer zasobów tylko się odświeża. Domyślny `0 */6 * * *`; dokręć do `*/15 * * * *` dla IdP o dużej rotacji.
   - Procedura `validate` — sprawdza listę dozwolonych `iss`, podpis względem buforowanych JWKS, `aud == mcp_resource_url`, `exp`, wymagany zakres.
   - Ścieżka wydawania stopniowego — tylko jeśli lista narzędzi zawiera operacje zamknięte za zakresem, którego użytkownik początkowo nie przyznał.

5. **Plan pamięci podręcznej.** Jeden wpis na zaakceptowanego wystawcę z kluczem `issuer`, posiadającego `{keys, fetched_at}`. Udokumentuj wzorzec odczytu: moduł sprawdzania poprawności odczytuje pamięć podręczną i powraca do pojedynczego synchronicznego odświeżenia w przypadku braku `kid` (ponowne pobranie, a nie rotacja — ponowne pobranie jest idempotentne i nie można go przekształcić w DoS tworzenia klucza).

6. **Mapowanie zakresu.** Mapuj każde narzędzie do wymaganego zakresu. Wyprowadź tabelę:
   `| tool | required_scope | rationale |`. Grupuj destrukcyjne narzędzia według własnego zakresu; nigdy nie używaj ponownie zakresu odczytu dla narzędzia do zapisu.

7. **Zasady odmowy w czasie wykonywania** (walidator musi je zakodować):
   - Odrzuć, gdy `aud != mcp_resource_url` → 401 `Bearer error="invalid_token", error_description="audience mismatch", resource_metadata="<prm_url>"`.
   - Odrzuć, gdy `iss not in authorization_servers`.
   - Odrzuć, gdy `kid` nie znajduje się w buforowanym JWKS po pojedynczym ponownym pobraniu.
   - Odrzuć w przypadku braku wymaganego zakresu → 403 `Bearer error="insufficient_scope", scope="<required>", resource_metadata="<prm_url>"`.
   - Odrzuć każde żądanie tokena bez parametru `code_verifier` lub `resource`.

Twarde odrzucenia (nigdy nie łącz żadnego z nich — odrzuć prośbę i udokumentuj dlaczego):

- Przechowywanie `client_secret` w postaci zwykłego tekstu. Klienci publiczni korzystają z `token_endpoint_auth_method: none`; poufni klienci korzystają z `private_key_jwt`. Żadne wspólne sekrety w postaci zwykłego tekstu nie są przechowywane ani w dziennikach odpowiedzi na rejestrację.
- Pominięcie kontroli `aud` w walidatorze. Powiązanie odbiorców (ograniczenie uprawnień tokenu dostępu) jest głównym powodem RFC 8707 + RFC 9728.
— Okablowanie funkcji awaryjnego braku pamięci podręcznej JWKS do obracania i odtwarzania zamiast ponownego pobierania. Nigdy nie generuje brakującego klucza `kid` i umożliwia kontrolowanym przez atakującego wartościom `kid` wymuszenie nieograniczonego tworzenia klucza. Rozwiązaniem awaryjnym musi być odświeżenie idempotentne.
- Zezwalanie na żądania kodu autoryzacyjnego bez PKCE. OAuth 2.1 tego zabrania; walidator musi odrzucić każdą wymianę `/token`, której przechowywany rekord kodu autoryzacyjnego nie zawiera `code_challenge`.
- Buforowanie JWKS bez zadania odświeżania. Albo zaplanowane odświeżenie zostanie wysłane, albo powierzchnia uwierzytelniająca nie zostanie wdrożona.
- Zaufanie twierdzeniu `iss` bez listy dozwolonych. Każdy walidator, który akceptuje token z dowolnego `iss`, pozwala atakującemu postawić własnego dostawcę tożsamości i sfałszować tokeny.
- Przekazywanie przychodzącego tokena MCP do nadrzędnego interfejsu API (przekazywanie tokenu). Jeśli serwer MCP wywołuje nadrzędne interfejsy API, MUSI uzyskać własny, oddzielny token; przejście stwarza problem zdezorientowanego zastępcy.
- Przechowywanie `registration_access_token` w postaci zwykłego tekstu. Hash w stanie spoczynku; wymagają czystego tekstu przy każdej aktualizacji.

Dane wyjściowe: jednostronicowy plan z dokumentem chronionego zasobu, wybraną ścieżką rejestracji (CIMD / rejestracja wstępna / DCR), punktami końcowymi HTTP, zadaniem odświeżania JWKS, planem pamięci podręcznej, tabelą mapowania zakresu i zakodowanymi regułami odmowy w czasie wykonywania. Zakończ pojedynczą luką blokującą wdrożenie, która najprawdopodobniej pojawi się w przypadku wybranego dostawcy tożsamości – zazwyczaj niezależnie od tego, czy CIMD jest już obsługiwany, powracając do dostępności DCR dla korporacyjnego logowania jednokrotnego.