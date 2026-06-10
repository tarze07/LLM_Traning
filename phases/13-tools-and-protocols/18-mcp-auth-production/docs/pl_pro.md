# Autoryzacja MCP w środowisku produkcyjnym — rejestracja, odświeżanie JWKS i tokeny powiązane z odbiorcą

> W lekcji 16 uruchomiliśmy w pamięci symulator maszyny stanów OAuth 2.1. W warunkach produkcyjnych każdy serwer MCP wdrażany w organizacji musi spełniać surowe standardy bezpieczeństwa. Obejmuje to: skalowalną rejestrację klientów (z priorytetem dla dokumentów metadanych identyfikatora klienta [CIMD] oraz dynamiczną rejestracją klientów [DCR] jako rozwiązaniem wstecznie kompatybilnym), wykrywanie metadanych serwera autoryzacji (RFC 8414 lub OpenID Connect Discovery), niezawodne odświeżanie pamięci podręcznej JWKS (zapobiegające awariom weryfikacji przy rotacji kluczy w środku nocy) oraz wiązanie tokenów z odbiorcą (audience binding), co wyklucza ataki typu replay. W tej lekcji modelujemy kompletne środowisko z podziałem na trzy role — serwer autoryzacji (Authorization Server), serwer zasobów (Resource Server / serwer MCP) i klient — co pozwala prześledzić cały proces od wykrycia usług po autoryzowane wywołanie narzędzia.
>
> **Uwaga techniczna (specyfikacja z 25.11.2025 r.):** Nowelizacja specyfikacji autoryzacji MCP zmieniła status dynamicznej rejestracji klientów (DCR) z zalecanego (`SHOULD`) na opcjonalny (`MAY`), ustanawiając **Dokumenty metadanych identyfikatora klienta (Client ID Metadata Documents - CIMD)** jako domyślny i preferowany mechanizm. W tej lekcji omawiamy oba podejścia zgodnie z priorytetami specyfikacji oraz analizujemy kod obsługujący DCR, który ze względu na prostotę uruchomienia w jednym procesie ułatwia naukę migracji.

**Typ:** Implementacja (Build)
**Język:** Python (biblioteka standardowa)
**Wymagania wstępne:** Faza 13 · 16 (maszyna stanów OAuth 2.1), Faza 13 · 17 (bramy sieciowe)
**Czas:** ~90 minut

## Cele lekcji

- Lokalizowanie serwera autoryzacji przy użyciu metadanych RFC 8414 i weryfikacja obsługiwanych funkcji.
- Implementacja dynamicznej rejestracji klientów (RFC 7591) w celu automatyzacji rejestracji bez udziału administratora.
- Wdrożenie buforowania i harmonogramu odświeżania kluczy JWKS, aby weryfikacja podpisów działała nieprzerwanie podczas rotacji kluczy.
- Powiązywanie tokenów z konkretnym zasobem MCP przy użyciu wskaźników zasobów (RFC 8707) w celu eliminacji ataków typu replay i zdezorientowanego zastępcy.
- Wyraźne rozdzielenie odpowiedzialności pomiędzy serwer autoryzacji, serwer zasobów i klienta tak, aby każdy komponent realizował wyłącznie przypisane mu kontrole bezpieczeństwa.
- Analiza matrycy możliwości dostawców tożsamości (IdP) i blokowanie wdrożeń w przypadku, gdy dostawca nie spełnia wymagań profilu autoryzacji MCP.

## Problem

Symulator z lekcji 16 uruchamiał przepływ OAuth 2.1 w całości w pamięci. Wdrożenie produkcyjne wiąże się jednak z wyzwaniami operacyjnymi, które nie występują w tak uproszczonym modelu.

Pierwszym wyzwaniem jest rejestracja klientów. Rzeczywiste środowisko korporacyjne może składać się z setek serwerów MCP i tysięcy klientów. Administratorzy nie mogą ręcznie rejestrować każdego programu Cursor jako klienta OAuth. Specyfikacja z 25.11.2025 r. definiuje ścisłą kolejność postępowania: (1) użyj wstępnie skonfigurowanego `client_id`, jeśli istnieje; (2) użyj **dokumentu metadanych identyfikatora klienta (CIMD)**, w którym klient identyfikuje się za pomocą adresu URL HTTPS pod swoim zarządem, a serwer autoryzacji pobiera metadane z tego źródła; (3) użyj dynamicznej rejestracji **RFC 7591 DCR** (klient wysyła żądanie POST pod `/register` i otrzymuje `client_id`); (4) w ostateczności poproś użytkownika o interwencję. CIMD jest zalecanym standardem, ponieważ eliminuje potrzebę przechowywania stanu rejestracji po stronie serwera autoryzacji, opierając zaufanie na systemie DNS. DCR pozostaje wspierany jako rozwiązanie przejściowe dla kompatybilności wstecznej. Oba mechanizmy wykrywają punkty końcowe na podstawie metadanych serwera autoryzacji: odpowiednio przez flagę `client_id_metadata_document_supported` (dla CIMD) oraz pole `registration_endpoint` (dla DCR).

Drugim wyzwaniem jest rotacja kluczy kryptograficznych (JWKS). Weryfikacja tokenów JWT opiera się na kluczach publicznych serwera autoryzacji opublikowanych w formacie JSON Web Key Set (JWKS). Serwer autoryzacji rotuje te klucze według harmonogramu (np. co godzinę lub natychmiastowo w przypadku incydentów bezpieczeństwa). Jeśli serwer MCP pobiera JWKS jednorazowo przy starcie, weryfikacja tokenów przestanie działać po pierwszej rotacji, co będzie wymagało restartu usługi. Wersja produkcyjna wymaga mechanizmu buforowania JWKS powiązanego z cyklicznym zadaniem odświeżania pobierającym nowe klucze przed wygaśnięciem starych, a także procedury awaryjnego odświeżenia (on-demand refetch) w sytuacji, gdy przychodzący token został podpisany nowym kluczem, którego nie ma jeszcze w lokalnej pamięci podręcznej.

Trzecim wyzwaniem jest wiązanie tokenów z odbiorcą (Audience Binding). Wskaźniki zasobów (RFC 8707), wprowadzone w lekcji 16, w środowisku produkcyjnym stanowią bezwzględny wymóg walidacji. Przy każdym żądaniu serwer MCP musi porównać pole `aud` tokenu z własnym kanonicznym adresem URL zasobu i odrzucić żądanie z kodem HTTP 401 w przypadku niezgodności. Jest to kluczowa linia obrony przed atakami polegającymi na przechwyceniu i ponownym użyciu (replay) tokenu przeznaczonego dla serwera A na serwerze B w obrębie tej samej domeny zaufania.

W tej lekcji modelujemy te wymagania w praktyce: dokument metadanych serwera jest udostępniany jako punkt końcowy HTTP, odświeżanie JWKS realizowane jest przez zaplanowane zadanie aktualizujące pamięć podręczną, a weryfikacja JWT stanowi obowiązkowy etap przed każdym wykonaniem narzędzia. Trzy role są ściśle odizolowane: serwer autoryzacji zarządza kluczami i ich rotacją, serwer zasobów (MCP) buforuje klucze i weryfikuje tokeny, a klient odpowiada za autowykrywanie i rejestrację.

## Założenia koncepcyjne

### RFC 8414 — Metadane serwera autoryzacji OAuth

Plik konfiguracyjny pod adresem `.well-known/oauth-authorization-server` zawiera wszystkie niezbędne dane dla klienta:

```json
{
  "issuer": "https://auth.example.com",
  "authorization_endpoint": "https://auth.example.com/authorize",
  "token_endpoint": "https://auth.example.com/token",
  "jwks_uri": "https://auth.example.com/.well-known/jwks.json",
  "registration_endpoint": "https://auth.example.com/register",
  "response_types_supported": ["code"],
  "grant_types_supported": ["authorization_code", "refresh_token"],
  "code_challenge_methods_supported": ["S256"],
  "scopes_supported": ["mcp:tools.read", "mcp:tools.invoke"],
  "token_endpoint_auth_methods_supported": ["none", "private_key_jwt"]
}
```

Proces wykrywania (discovery) przez klienta przebiega następująco: na podstawie adresu URL zasobu MCP odpytuje on plik `.well-known/oauth-protected-resource` (RFC 9728) w celu pobrania adresu wystawcy (issuer), a następnie odczytuje plik metadanych serwera autoryzacji (RFC 8414) w celu zlokalizowania konkretnych punktów końcowych. Dzięki temu klient nie musi mieć na stałe wpisanych adresów URL usług autoryzacyjnych.

Warunki, które musi spełnić dostawca tożsamości (IdP), aby mógł obsługiwać profil autoryzacji MCP:

- Pole `code_challenge_methods_supported` must zawierać wartość `S256` (zgodnie z RFC 7636 dla PKCE). Jeśli ta wartość jest nieobecna, serwer autoryzacji nie wspiera PKCE i klient MA OBOWIĄZEK przerwać proces autoryzacji.
- Pole `grant_types_supported` musi zawierać `authorization_code`, natomiast powinno wykluczać przestarzałe przepływy typu `password` oraz `implicit`.
- Dostępna musi być co najmniej jedna metoda rejestracji: `client_id_metadata_document_supported: true` (preferowany CIMD) lub `registration_endpoint` (RFC 7591 DCR jako metoda rezerwowa).
- Pole `response_types_supported` musi mieć wartość dokładnie `["code"]` (wymóg OAuth 2.1).

Brak obsługi metody `S256` wyklucza danego dostawcę tożsamości z integracji z MCP — dla PKCE nie przewidziano żadnego trybu awaryjnego. Podobnie, jeśli nie skonfigurowano wcześniej statycznego `client_id` oraz serwer nie udostępnia żadnej metody rejestracji, autoryzacja nie będzie możliwa z winy konfiguracji środowiska.

### RFC 9728 — Metadane zasobów chronionych

W środowisku produkcyjnym dokument metadanych chronionego zasobu (RFC 9728) stanowi jedyne autorytatywne źródło informacji o tym, którym serwerom autoryzacji ufa dany serwer MCP. Serwer MCP może akceptować tokeny od wielu różnych wystawców (np. osobny IdP dla pracowników etatowych, osobny dla zewnętrznych partnerów). Lista ta jest definiowana w RFC 9728, natomiast szczegółowa specyfikacja możliwości każdego z tych wystawców jest opisywana w plikach RFC 8414.

```json
{
  "resource": "https://notes.example.com",
  "authorization_servers": ["https://auth.example.com", "https://partners.example.com"],
  "scopes_supported": ["mcp:tools.invoke"],
  "bearer_methods_supported": ["header"],
  "resource_documentation": "https://notes.example.com/docs"
}
```

### Dokumenty metadanych identyfikatora klienta (CIMD - preferowany standard)

CIMD odwraca dotychczasowy paradygmat rejestracji typu push (gdzie klient wysyła swoje dane) na pull (gdzie serwer pobiera dane klienta). Zamiast prosić serwer autoryzacji o wygenerowanie unikalnego `client_id`, klient jako swój `client_id` podaje adres URL HTTPS, pod którym sam udostępnia dokument konfiguracyjny JSON. Serwer autoryzacji pobiera ten dokument dynamicznie w trakcie przepływu OAuth. W tym modelu zaufanie opiera się na strukturze DNS: jeśli administrator serwera ufa domenie `app.example.com`, ufa również klientowi pobieranemu z adresu `https://app.example.com/client.json`. Rozwiązanie to eliminuje potrzebę dwukierunkowej komunikacji podczas rejestracji, ryzyko wyczerpania identyfikatorów `client_id` oraz potrzebę synchronizacji stanu rejestracji pomiędzy rozproszonymi instancjami.

Przykładowy dokument metadanych hostowany przez klienta:

```json
{
  "client_id": "https://app.example.com/oauth/client.json",
  "client_name": "Example MCP Client",
  "client_uri": "https://app.example.com",
  "redirect_uris": ["http://127.0.0.1:7333/callback", "http://localhost:7333/callback"],
  "grant_types": ["authorization_code", "refresh_token"],
  "response_types": ["code"],
  "token_endpoint_auth_method": "none"
}
```

Wartość pola `client_id` w dokumencie MUST być identyczna z adresem URL, pod którym dokument ten jest wystawiony. Serwer autoryzacji obowiązkowo weryfikuje ten warunek i odrzuca żądania w przypadku niezgodności. Serwer autoryzacji ogłasza obsługę tego standardu flagą `client_id_metadata_document_supported: true` w dokumencie metadanych RFC 8414.

Dwojakie aspekty bezpieczeństwa, na które wprost wskazuje specyfikacja:

- **Zabezpieczenie przed SSRF (Server-Side Request Forgery).** Serwer autoryzacji pobiera dane z adresu URL podanego przez klienta (który może być kontrolowany przez atakującego). Serwer autoryzacji musi bezwzględnie blokować zapytania kierowane do wewnętrznych adresów IP i administracyjnych punktów końcowych.
- **Podszywanie się pod localhost.** Sam mechanizm CIMD nie zapobiega przejęciu adresu URL metadanych przez lokalnego atakującego w celu zarejestrowania przekierowania na `localhost`. Serwer autoryzacji MA OBOWIĄZEK wyraźnie prezentować użytkownikowi nazwę hosta z adresu przekierowania (redirect URI) na ekranie zgody oraz POWINIEN wyświetlać ostrzeżenie w przypadku korzystania z adresów `localhost`.

### RFC 7591 — Dynamiczna rejestracja klienta (DCR - standard wsteczny)

Dynamiczna rejestracja klientów (DCR) ma obecnie status opcjonalny (`MAY`). Jest wspierana ze względu na kompatybilność wsteczną z systemami wdrożonymi przed listopadem 2025 r. oraz dostawcami tożsamości, którzy nie zaimplementowali jeszcze standardu CIMD. Bez wsparcia dla DCR, CIMD lub statycznej konfiguracji, rejestracja każdego nowego klienta MCP wymagałaby ręcznej interwencji administratora IdP. W przepływie DCR klient wysyła żądanie:

```json
POST /register
Content-Type: application/json

{
  "redirect_uris": ["http://127.0.0.1:7333/callback"],
  "grant_types": ["authorization_code", "refresh_token"],
  "response_types": ["code"],
  "token_endpoint_auth_method": "none",
  "scope": "mcp:tools.invoke",
  "client_name": "Cursor",
  "software_id": "com.cursor.cursor",
  "software_version": "0.42.0"
}
```

Serwer autoryzacji zwraca wygenerowany `client_id` oraz token `registration_access_token` umożliwiający modyfikację rejestracji:

```json
{
  "client_id": "c_3e7f1a",
  "client_id_issued_at": 1769472000,
  "redirect_uris": ["http://127.0.0.1:7333/callback"],
  "grant_types": ["authorization_code", "refresh_token"],
  "registration_access_token": "regt_b2...",
  "registration_client_uri": "https://auth.example.com/register/c_3e7f1a"
}
```

Ustawienie `token_endpoint_auth_method: none` jest właściwym wyborem dla aplikacji klienckich MCP uruchamianych bezpośrednio na stacjach roboczych użytkowników. Klient otrzymuje jedynie identyfikator `client_id` i nie przechowuje żadnego sekretu (`client_secret`), który mógłby zostać wykradziony. Zabezpieczenie procesu autoryzacji gwarantuje PKCE.

Trzy wyzwania wdrożeniowe dla DCR in produkcji:

— **Limitowanie żądań (Rate Limiting).** Punkt końcowy `/register` musi ograniczać liczbę zapytań na podstawie adresu IP nadawcy. W przeciwnym razie atakujący może wygenerować miliony fałszywych rejestracji i doprowadzić do wyczerpania puli identyfikatorów client ID.
- **Deklaracja oprogramowania (Software Statement).** Niektóre korporacyjne systemy IAM wymagają dołączania podpisanego tokenu JWT (`software_statement`) opisującego aplikację kliencką. Produkcyjne wdrożenia odrzucają niepodpisane żądania rejestracji, chyba że dotyczą one przekierowań na adresy lokalne (localhost).
- **Ochrona tokenów rejestracyjnych.** Token `registration_access_token` musi być przechowywany w bazie danych w postaci zahaszowanej. Wyciek tego tokenu pozwala atakującemu na zmodyfikowanie adresów przekierowań klienta i przejęcie sesji użytkowników.

### RFC 8707 — Wskaźniki zasobów (Resource Indicators)

W środowisku produkcyjnym każde żądanie tokenu musi jawnie określać cel za pomocą parametru `resource=<canonical-mcp-url>`. Serwer MCP przy każdym zapytaniu sprawdza, czy pole `aud` w tokenie odpowiada jego kanonicznemu adresowi URL. Kanoniczny URI to unikalny identyfikator serwera: zawiera małe litery w schemacie i nazwie hosta, nie zawiera kotwicy/fragmentu (#) i zazwyczaj nie kończy się ukośnikiem (slash). Ścieżka URL (path) jest istotna i nie powinna być pomijana, jeśli służy do rozróżniania serwerów MCP współdzielących ten sam host. Adresy takie jak `https://mcp.example.com`, `https://mcp.example.com/mcp`, `https://mcp.example.com:8443` czy `https://mcp.example.com/server/mcp` są unikalnymi, poprawnymi identyfikatorami. Wybierz jeden schemat adresacji dla swojego serwera i przypisz pole `aud` dokładnie do tej wartości.

### RFC 7636 — PKCE (Proof Key for Code Exchange)

PKCE jest obligatoryjnym elementem standardu OAuth 2.1. Przepływ kodu autoryzacji musi zawierać parametry `code_challenge` oraz `code_verifier`. Serwer autoryzacji odrzuca żądania wydania tokenu, jeśli weryfikator jest nieobecny lub nie odpowiada wcześniej przesłanemu wyzwaniu.

### Profil autoryzacji w specyfikacji MCP z dnia 25.11.2025 r.

Specyfikacja precyzyjnie definiuje obowiązki warstwy autoryzacyjnej serwera MCP:

- **Implementacja specyfikacji metadanych zasobów chronionych (RFC 9728)** i wskazanie ich lokalizacji za pomocą nagłówka `WWW-Authenticate: Bearer resource_metadata="..."` w odpowiedzi 401 lub poprzez znany punkt końcowy `/.well-known/oauth-protected-resource` (standard SEP-985 uczynił nagłówek opcjonalnym pod warunkiem udostępnienia standardowej ścieżki). Pole `authorization_servers` musi wskazywać co najmniej jeden serwer.
- **Akceptowanie tokenów wyłącznie w nagłówku `Authorization: Bearer ...`** przy każdym pojedynczym żądaniu. Niedozwolone jest przekazywanie tokenów w parametrach zapytania (query parameters) ani walidacja wyłącznie na etapie nawiązywania sesji.
- **Walidacja pól `aud` (odbiorca), `iss` (wystawca), `exp` (czas ważności) oraz wymaganych zakresów** dla każdego żądania. Serwer ma obowiązek upewnić się, że token jest dedykowany dla niego – brak lub niezgodność pola `aud` skutkuje odrzuceniem żądania.
- **Zwracanie nagłówka `WWW-Authenticate: Bearer`** w przypadku błędów 401/403, zawierającego dyrektywy: `error=...`, `resource_metadata="<PRM-URL>"` (wskazujący adres URL dokumentu konfiguracyjnego PRM, a nie adres URL samego zasobu) oraz opcjonalnie `scope="..."` przy kodzie 403 (`insufficient_scope`).
- **Wsparcie dla standardu RFC 8414 (OAuth Metadata) lub OpenID Connect Discovery 1.0** w celach wykrywania usług; aplikacje klienckie odpytują te ścieżki kolejno według priorytetu.
- **Zabezpieczenie przed atakakami typu mix-up leży po stronie klienta (nie serwera):** klient zapisuje oczekiwany identyfikator `issuer` przed przekierowaniem użytkownika, a następnie weryfikuje parametr `iss` w odpowiedzi autoryzacyjnej (zgodnie z RFC 9207) przed przesłaniem kodu. Samo PKCE nie chroni przed tym atakiem, ponieważ klient bez weryfikacji przekazałby `code_verifier` do podstawionego punktu tokenów.

### Macierz możliwości dostawców tożsamości (IdP)

| Typ dostawcy tożsamości | Metadane AS (8414/OIDC) | CIMD | RFC 7591 DCR | Wskaźniki zasobów (8707) | PKCE (S256) | Uwagi |
|---|---|---|---|---|---|---|
| Self-hosted (Keycloak) | Tak | Wdrażane | Tak | Tak (od wersji 24.x) | Tak | Referencyjny dostawca tożsamości dla profilu MCP; w pełni obsługuje DCR i wdraża standard CIMD. |
| Enterprise SSO (Entra ID) | Tak | Wdrażane | Tak (plany premium) | Tak | Tak | Dostępność funkcji DCR zależy od wersji licencyjnej. |
| Enterprise SSO (Okta) | Tak | Wdrażane | Tak (Auth0 / Okta CIC) | Tak | Tak | Platforma Auth0 (Okta CIC) w pełni wspiera dynamiczną rejestrację; klasyczna Okta wymaga statycznej konfiguracji. |
| IdP społecznościowe (np. Google, GitHub) | Różnie | Nie | Rzadko | Rzadko | Tak | Zewnętrzni dostawcy społecznościowi zazwyczaj wymagają statycznej rejestracji. Zaleca się stosowanie ich jako dostawców tożsamości podpiętych pod własną bramę/serwer autoryzacji zgodny z MCP. |
| Własne / dedykowane | Zależy | Zależy | Zależy | Zależy | Zależy | W przypadku własnej implementacji należy zapewnić pełną zgodność z profilem MCP, ze szczególnym uwzględnieniem PKCE i wiązania odbiorców. |

### Wzorzec odświeżania JWKS (Rotacja w AS, aktualizacja w serwerze zasobów)

Należy wyraźnie rozróżnić te dwa procesy, ponieważ ich utożsamianie prowadzi do poważnych błędów produkcyjnych:

- **Rotacja (Rotation)** leży po stronie serwera autoryzacji (AS): polega na wygenerowaniu nowej pary kluczy, opublikowaniu klucza publicznego w JWKS i wycofaniu starego klucza po okresie przejściowym. Serwer zasobów nie uczestniczy w tym procesie i nie ma dostępu do kluczy prywatnych.
- **Odświeżanie (Refresh)** leży po stronie serwera zasobów (Resource Server): polega na pobraniu aktualnego pliku JWKS (żądanie GET) i zaktualizowaniu lokalnej pamięci podręcznej. Jest to jedyna operacja na kluczach, jaką wykonuje serwer zasobów.

Najnajczęstszą przyczyną błędów produkcyjnych jest nieaktualna pamięć podręczna kluczy. Rozwiązaniem jest cykliczne zadanie odświeżające (np. cron lub timer wbudowany w aplikację), które w określonych odstępach czasu pobiera plik `jwks.json` i aktualizuje lokalny słownik: `cache[issuer] = {keys, fetched_at}`. Moduł walidacji odczytuje klucze z tej pamięci. Jeżeli przychodzący token zawiera identyfikator klucza `kid`, którego brakuje w cache, uruchamiane jest jednorazowe, synchroniczne pobranie kluczy (on-demand refetch) w celu obsłużenia sytuacji, gdy nowy klucz został użyty zanim zaplanowane zadanie zdążyło zaktualizować pamięć podręczną.

Procedura awaryjna musi polegać na ponownym pobraniu kluczy, a nie na ich generowaniu. Błędne powiązanie braku klucza z żądaniem wygenerowania nowego klucza (rotate-and-mint) niesie dwa zagrożenia: (1) wygenerowanie nowego klucza na serwerze autoryzacji stworzy klucz o nowym identyfikatorze `kid`, który i tak no nie dopasuje się do weryfikowanego tokenu; (2) atakujący wysyłający tokeny z losowymi wartościami `kid` może wymusić masowe generowanie kluczy na serwerze autoryzacji, co doprowadzi do awarii typu Denial of Service (DoS). Pobranie kluczy (GET) z serwera autoryzacji jest operacją idempotentną, więc błędny token z losowym `kid` spowoduje co najwyżej jedno dodatkowe zapytanie sieciowe.

Słownik pamięci podręcznej kluczy:

```json
{
  "https://auth.example.com": {
    "keys": [
      {"kid": "k_2026_03", "kty": "RSA", "n": "...", "e": "AQAB", "alg": "RS256", "use": "sig"},
      {"kid": "k_2026_04", "kty": "RSA", "n": "...", "e": "AQAB", "alg": "RS256", "use": "sig"}
    ],
    "fetched_at": 1772668800
  }
}
```

### Procedura walidacji

Serwer MCP bezwzględnie weryfikuje token przed wykonaniem jakiejkolwiek operacji narzędziowej. W skrypcie `code/main.py` realizuje to następujący blok:

```python
result = server.validate(bearer_token, required_scope="mcp:tools.invoke")
if not result["valid"]:
    return {"status": result["status"], "WWW-Authenticate": result["www_authenticate"]}
```

Metoda `validate` dekoduje token JWT, wyszukuje odpowiedni klucz w pamięci podręcznej JWKS (w razie potrzeby pobierając aktualne klucze), weryfikuje podpis kryptograficzny, a następnie sprawdza zgodność pól `iss` (wystawca), `aud` (odbiorca), `exp` (czas wygaśnięcia) oraz wymagane zakresy uprawnień. Wykrycie jakiejkolwiek niezgodności skutkuje przerwaniem procesu i zwróceniem nagłówka `WWW-Authenticate`. Scentralizowanie tej logiki gwarantuje, że każde zapytanie (niezależnie od transportu czy wywoływanego narzędzia) podlega dokładnie tym samym regułom bezpieczeństwa.

### Ochrona przed atakiem typu Replay (Wiązanie odbiorcy)

Załóżmy, że serwer A (`notes.example.com`) oraz serwer B (`tasks.example.com`) korzystają z tego samego serwera autoryzacji. W przypadku przejęcia serwera A, atakujący może próbować użyć tokenu wydanego dla serwera A w celu autoryzacji na serwerze B.

Logika weryfikacji na serwerze B:

1. Dekoduje token JWT, odczytuje klucze JWKS i weryfikuje podpis.
2. Sprawdza pole `iss` pod kątem zaufanych wystawców (test pomyślny – ten sam dostawca tożsamości).
3. Weryfikuje warunek `aud == "https://tasks.example.com"` (test niepomyślny – pole `aud` w tokenie wskazuje na serwer A).
4. Przerywa połączenie i zwraca kod 401 z odpowiednim nagłówkiem `WWW-Authenticate`: `Bearer error="invalid_token", error_description="audience mismatch", resource_metadata="https://tasks.example.com/.well-known/oauth-protected-resource"`.

Weryfikacja pola `aud` jest jedynym skutecznym zabezpieczeniem przed tym zagrożeniem na poziomie protokołu. Pomijanie tej kontroli (np. w celu optymalizacji) to poważny błąd. Walidacja musi być przeprowadzana przy każdym zapytaniu. Specyfikacja MCP kategorycznie wymaga odrzucania tokenów, które nie wskazują danego serwera w polu odbiorcy.

> **Wyjasnienie pojęciowe:** Specyfikacja rezerwuje termin *zdezorientowany zastępca (confused deputy)* dla sytuacji, w której serwer MCP pośredniczy w autoryzacji do zewnętrznego API przy użyciu statycznego klienta i przekazuje tokeny bez wyraźnej zgody użytkownika. Wiązanie odbiorców (audience binding) chroni przed ponownym użyciem tokenu (replay), natomiast ochrona przed zdezorientowanym zastępcą wymaga zbierania zgody oraz zakazu przekazywania tokenów klienckich do systemów nadrzędnych (serwer MCP musi pozyskać własne poświadczenia).

### Ataki typu Mix-Up (Ochrona po stronie klienta)

Klient w cyklu swojego życia może komunikować się z różnymi serwerami autoryzacji. Złośliwy lub przejęty serwer autoryzacji może próbować nakłonić klienta do przesłania kodu autoryzacji uzyskanego z zaufanego serwera do punktu końcowego kontrolowanego przez atakującego. W tym scenariuszu walidacja pola `aud` nie chroni przed zagrożeniem, ponieważ token nie został jeszcze wygenerowany. Zabezpieczenie musi zostać wdrożone po stronie klienta (zgodnie z RFC 9207):

1. Przed przekierowaniem użytkownika klient zapisuje identyfikator `issuer` zaufanego serwera autoryzacji.
2. W odpowiedzi zwrotnej klient weryfikuje parametr `iss` z zapisaną wartością przed przesłaniem kodu autoryzacyjnego pod jakikolwiek adres.
3. W przypadku wykrycia niezgodności lub braku parametru `iss` (jeżeli serwer deklarował jego obsługę), klient przerywa proces i nie przetwarza odpowiedzi.

Samo PKCE nie chroni przed tym atakiem, ponieważ klient bez weryfikacji przekazałby `code_verifier` do podstawionego punktu tokenów.

### Scenariusze awarii i podatności

- **Nieaktualna pamięć podręczna JWKS.** Odrzucanie poprawnych tokenów po rotacji kluczy. Rozwiązanie: wdrożenie cyklicznej aktualizacji oraz awaryjnego odświeżania przy braku klucza w cache.
- **Wywoływanie generowania kluczy zamiast pobierania.** Próba tworzenia nowych kluczy na serwerze przy braku dopasowania `kid` (zamiast pobrania pliku JWKS z serwera autoryzacji) prowadzi do awarii i podatności DoS. Procedura awaryjna musi ograniczać się wyłącznie do idempotentnej operacji pobrania kluczy.
- **Brak pola `aud` w tokenie.** Niektóre serwery autoryzacji nie generują pola `aud`, o ile klient nie zażądał konkretnego zasobu. Walidator must bezwzględnie odrzucać tokeny pozbawione tej deklaracji.
- **Brak weryfikacji parametru `iss` (Mix-Up).** Podatność klienta na przekierowanie kodu autoryzacyjnego do wrogiego serwera autoryzacji. Wymaga weryfikacji pola `iss` zgodnie z RFC 9207 po stronie klienta.
- **Wyścig przy eskalacji uprawnień (Race Condition).** Ryzyko niespójności stanu przy równoległych żądaniach step-up. Walidator musi weryfikować zakresy z samego tokenu przekazanego w nagłówku żądania, a nie odpytywać o aktualny profil uprawnień użytkownika (zapobiega to podatnościom typu TOCTOU).
- **Kradzież tokenu rejestracyjnego.** Przejęcie tokenu `registration_access_token` przez atakującego pozwala na zmianę adresów przekierowań klienta. Rozwiązanie: haszowanie tokenów w bazie danych oraz ich regularna rotacja.
- **Brak weryfikacji wystawcy (`iss`).** Akceptowanie dowolnego wystawcy pozwala atakującemu na postawienie własnego serwera autoryzacji i generowanie fałszywych tokenów. Walidator musi sprawdzać pole `iss` w oparciu o listę zaufanych serwerów zdefiniowaną w pliku metadanych chronionego zasobu.

## Zastosowanie w praktyce

Skrypt `code/main.py` demonstruje kompletny przepływ produkcyjny z wykorzystaniem biblioteki standardowej Pythona, modelując role: `AuthorizationServer` (serwer autoryzacji), `ResourceServer` (serwer zasobów) oraz `Client` (klient). Przepływ obejmuje:

1. Serwer autoryzacji udostępnia plik metadanych (RFC 8414) pod adresem `/.well-known/oauth-authorization-server`.
2. Klient MCP odczytuje te metadane, sprawdzając obsługiwane metody rejestracji (`client_id_metadata_document_supported` lub `registration_endpoint`) oraz wsparcie dla PKCE (`S256`).
3. W tym przykładzie klient korzysta z metody rezerwowej DCR, wysyłając żądanie rejestracji pod `/register` (RFC 7591) i uzyskując `client_id` (klient wspierający CIMD pominąłby ten krok, podając jako `client_id` swój adres URL).
4. Klient inicjuje przepływ kodu autoryzacji z PKCE (RFC 7636) wraz z parametrem `resource` (RFC 8707).
5. Klient wykonuje zapytanie do serwera MCP, dołączając nagłówek `Authorization: Bearer ...`.
6. Serwer MCP uruchamia procedurę `validate`, weryfikując podpis tokenu przy użyciu kluczy z bufora JWKS.
7. Serwer autoryzacji rotuje klucze; cykliczne zadanie pobiera nowy zestaw JWKS do lokalnej pamięci podręcznej.
8. Kolejne żądania są pomyślnie weryfikowane przy użyciu zaktualizowanych kluczy (poprzedni token zachowuje ważność w oknie nakładania się czasów życia kluczy).
9. Próba użycia tego samego tokenu na innym serwerze kończy się błędem 401 (`audience mismatch`) wraz ze wskazaniem lokalizacji metadanych zasobu.

W celach demonstracyjnych skrypt wykorzystuje algorytm symetryczny HS256 ze wspólnym sekretem. Wdrożenia produkcyjne opierają się na algorytmach asymetrycznych (np. RS256 lub EdDSA) pobierających klucze publiczne z pliku JWKS. Pozostała logika walidacji tokenu jest tożsama.

## Zadanie praktyczne

Wynikiem tej lekcji powinno być przygotowanie pliku `outputs/skill-mcp-auth.md`. Na podstawie specyfikacji serwera MCP oraz profilu dostawcy tożsamości (IdP) należy opracować kompletną specyfikację konfiguracji bezpieczeństwa. Powinna ona obejmować: projekt metadanych chronionego zasobu, wybór optymalnej ścieżki rejestracji klientów (CIMD, statyczna konfiguracja lub rezerwa DCR), harmonogram odświeżania JWKS, mapowanie zakresów uprawnień oraz reguły odrzucenia w przypadku braku pełnej zgodności IdP ze standardami.

## Ćwiczenia

1. Uruchom skrypt `code/main.py`. Przeanalizuj przebieg operacji. Zwróć uwagę na moment rotacji klucza na serwerze autoryzacji (krok 6) oraz na to, jak cykliczne zadanie `refresh_jwks` aktualizuje bufor kluczy, umożliwiając poprawną weryfikację zarówno starego tokenu (w okresie przejściowym), jak i nowego tokenu.

2. Dodaj drugiego dostawcę tożsamości do tablicy `authorization_servers` w pliku metadanych chronionego zasobu. Wygeneruj token podpisany przez nowego dostawcę i zweryfikuj jego akceptację przez serwer. Następnie wygeneruj token od niezaufanego wystawcy i upewnij się, że zostanie odrzucony z błędem `iss not allowed` w nagłówku `WWW-Authenticate`.

3. Zaimplementuj mechanizm rate limiting dla punktu końcowego `/register`. Przed przetworzeniem rejestracji sprawdź limit zapytań dla adresu IP nadawcy przy użyciu algorytmu token bucket (przechowując dane w słowniku w pamięci).

4. Zapoznaj się z dokumentem RFC 7591. Wskaż dwa parametry wejściowe, których nie weryfikuje nasza uproszczona implementacja rejestracji `/register` i dodaj do nich odpowiednie reguły walidacji (Wskazówka: przeanalizuj formaty adresów URL w polach `software_statement` oraz `redirect_uris`).

5. Zaimplementuj uproszczony mechanizm CIMD. Klient powinien udostępnić plik `client.json`, w którym wartość `client_id` jest zgodna z adresem URL pliku. Serwer autoryzacji powinien pobrać ten dokument i zweryfikować spójność identyfikatora (odrzucić żądanie w przypadku braku zgodności). Upewnij się, że klient korzystający z CIMD przechodzi autoryzację bez wywoływania metody dynamicznej rejestracji.

6. Przetestuj odporność na ataki DoS. Wyślij token zawierający losowy, nieistniejący identyfikator `kid` i upewnij się, że zapytanie sieciowe o klucze (`refresh_jwks`) zostanie wykonane maksymalnie raz, a serwer nie zacznie generować nowych kluczy. Następnie celowo zmodyfikuj kod tak, aby przy braku klucza generował nowy klucz (antywzorzec) i zaobserwuj niekontrolowany przyrost kluczy przy wysyłaniu fałszywych tokenów.

7. Zaimplementuj po stronie klienta ochronę przed atakiem mix-up (zgodnie z RFC 9207): zapisz identyfikator oczekiwanego wystawcy (`iss`) przed przekierowaniem użytkownika i odrzuć odpowiedź autoryzacji, jeśli zwrócony parametr `iss` jest niezgodny z zapisanym.

## Kluczowe pojęcia

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Metadane AS | „Dokument metadanych OAuth” | Standard RFC 8414 definiujący plik metadanych serwera autoryzacji |
| CIMD | „URL metadanych klienta” | Client ID Metadata Document – adres URL HTTPS klienta stanowiący jego `client_id`, skąd serwer autoryzacji pobiera plik JSON |
| DCR | „Dynamiczna rejestracja klienta” | Standard RFC 7591 umożliwiający rejestrację klientów przez POST pod `/register`; od 25.11.2025 r. ma status opcjonalny (`MAY`) |
| JWKS | „Zestaw kluczy weryfikacyjnych” | JSON Web Key Set – opublikowany zestaw kluczy publicznych serwera autoryzacji, indeksowany po `kid` |
| Rotacja a odświeżanie | „Aktualizacja kluczy” | Rotacja to wygenerowanie nowych kluczy i wycofanie starych na serwerze autoryzacji; odświeżenie to pobranie aktualnego zestawu kluczy przez serwer zasobów |
| Wskaźnik zasobu | „Parametr odbiorcy” | Parametr `resource` (RFC 8707) przypisujący token do konkretnego adresu URL serwera |
| aud | „Odbiorca (Audience)” | Deklaracja w tokenie JWT weryfikowana pod kątem zgodności z kanonicznym adresem URL serwera MCP |
| Replay ataku (Audience Replay) | „Przejęcie tokenu” | Próba użycia tokenu wydanego dla serwera A na serwerze B; blokowana przez weryfikację pola `aud` (zasada ograniczenia uprawnień tokenu) |
| Zdezorientowany zastępca (Confused Deputy) | „Brak delegacji uprawnień” | Podatność polegająca na pośredniczeniu i przekazywaniu tokenu bez uzyskania zgody użytkownika dla konkretnego podmiotu |
| Atak Mix-Up | „Przejęcie kodu autoryzacji” | Wyłudzenie kodu autoryzacyjnego przez skierowanie klienta do złośliwego punktu końcowego; blokowany po stronie klienta za pomocą RFC 9207 `iss` |
| Lista zaufanych wystawców | „Zaufane serwery autoryzacyjne” | Zbiór serwerów zdefiniowany w polu `authorization_servers` metadanych chronionego zasobu |
| resource_metadata | „Adres metadanych zasobu” | Wskazówka w nagłówku `WWW-Authenticate` zawierająca adres URL do dokumentu konfiguracyjnego RFC 9728 |
| Klient publiczny | „Aplikacja kliencka” | Klient OAuth uruchamiany na urządzeniu użytkownika bez bezpiecznego magazynu na `client_secret` (wymaga zabezpieczenia przez PKCE) |
| WWW-Authenticate | „Nagłówek odpowiedzi” | Standardowy nagłówek HTTP informujący klienta o wymaganej autoryzacji i sposobie jej uzyskania |

## Polecana literatura / dokumentacja

- [MCP — Specyfikacja autoryzacji (25.11.2025)](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization) — profil uwierzytelniania MCP implementowany w tej lekcji
- [Blog MCP — Rok MCP: wydanie specyfikacji z listopada 2025 r.](https://blog.modelcontextprotocol.io/posts/2025-11-25-first-mcp-anniversary/) — co zmieniło się w 25.11.2025 r. (degradacja CIMD, XAA, DCR)
- [Aaron Parecki — Rejestracja klienta w specyfikacji autoryzacji MCP z listopada 2025 r.](https://aaronparecki.com/2025/11/25/1/mcp-authorization-spec-update) — uzasadnienie CIMD-over-DCR
- [Dokument metadanych identyfikatora klienta OAuth (draft-ietf-oauth-client-id-metadata-document-00)](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-client-id-metadata-document-00) – CIMD
- [RFC 8414 — Metadane serwera autoryzacji OAuth 2.0](https://datatracker.ietf.org/doc/html/rfc8414) — umowa dotycząca wykrywania
- [RFC 7591 — Protokół dynamicznej rejestracji klienta OAuth 2.0](https://datatracker.ietf.org/doc/html/rfc7591) — DCR (ścieżka zastępcza)
- [RFC 7636 — Klucz próbny do wymiany kodów (PKCE)](https://datatracker.ietf.org/doc/html/rfc7636) — dowód posiadania dla klienta publicznego
- [RFC 8707 — Wskaźniki zasobów dla OAuth 2.0](https://datatracker.ietf.org/doc/html/rfc8707) — przypinanie odbiorców
- [RFC 9728 — Metadane zasobów chronionych OAuth 2.0](https://datatracker.ietf.org/doc/html/rfc9728) — wykrywanie serwera zasobów
- [RFC 9207 — Identyfikacja wystawcy serwera autoryzacji OAuth 2.0](https://datatracker.ietf.org/doc/html/rfc9207) — parametr `iss` chroniący przed atakami typu mix-up
- [Wersja robocza OAuth 2.1](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-v2-1) — skonsolidowane podłoże OAuth
