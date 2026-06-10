# Autoryzacja MCP w produkcji — rejestracja, odświeżanie JWKS, tokeny przypięte przez odbiorców

> Lekcja 16 uruchomiła w pamięci maszynę stanu OAuth 2.1. Do 2026 roku każdy serwer MCP wysyłany do prawdziwej organizacji będzie podlegał uwierzytelnianiu produkcyjnemu: rejestracja klientów skalowana do nieograniczonej populacji klientów (najpierw dokumenty metadanych identyfikatora klienta, dynamiczna rejestracja klienta jako rezerwa kompatybilna wstecz), wykrywanie metadanych serwera autoryzacji (RFC 8414 *lub* OpenID Connect Discovery), odświeżanie pamięci podręcznej JWKS, które nie przerywa weryfikacji tokenu o 3 nad ranem, oraz tokeny przypięte do odbiorców, które odmawiają powtórka między zasobami. W tej lekcji modelujemy całą powierzchnię z trzema rolami — serwerem autoryzacji, serwerem zasobów (serwerem MCP) i klientem — dzięki czemu można prześledzić każdy przeskok od wykrycia do zweryfikowanego wywołania narzędzia.
>
> **Nota techniczna (25.11.2025):** specyfikacja autoryzacji MCP z listopada 2025 r. obniżyła dynamiczną rejestrację klienta z `SHOULD` do `MAY` i uczyniła **Dokumenty metadanych identyfikatora klienta (CIMD)** zalecanym domyślnym mechanizmem rejestracji. Ta lekcja uczy zarówno, w kolejności priorytetów specyfikacji, jak i kodu, który przechowuje DCR na potrzeby przejścia, ponieważ jest on w pełni samodzielny w jednym procesie.

**Typ:** Kompilacja
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 13 · 16 (maszyna stanu OAuth 2.1), faza 13 · 17 (bramy)
**Czas:** ~90 minut

## Cele nauczania

- Znajdź serwer autoryzacyjny za pomocą metadanych RFC 8414 i zweryfikuj umowę.
- Wdrożenie dynamicznej rejestracji klienta RFC 7591, aby klienci MCP rejestrowali się bez interwencji administratora.
- Buforuj i odświeżaj klucze JWKS zgodnie z harmonogramem, aby weryfikacja podpisu przetrwała przeniesienie klucza.
- Przypinaj tokeny do pojedynczego zasobu MCP za pomocą wskaźników zasobów RFC 8707 i odmawiaj ponownego wykorzystania przez zdezorientowanego zastępcę.
- Oddziel wyraźnie trzy role — serwer autoryzacji, serwer zasobów i klient — tak aby każda z nich wymuszała tylko te kontrole, które do niej należą.
- Przeczytaj matrycę możliwości dostawcy tożsamości i odmów wdrożenia, jeśli dostawca tożsamości nie może spełnić wymagań profilu uwierzytelniania MCP.

## Problem

Symulator lekcji 16 uruchamia w pamięci protokół OAuth 2.1. Produkcja ma trzy luki operacyjne, których nie widzi symulator działający wyłącznie w pamięci.

Pierwszą luką jest rejestracja. Prawdziwa organizacja obsługuje setki serwerów MCP i tysiące klientów MCP. Operatorzy nie rejestrują ręcznie każdego użytkownika Cursor jako klienta OAuth. Specyfikacja z dnia 25.11.2025 r. określa priorytetową kolejność rozwiązania tego problemu: użyj wstępnie zarejestrowanego `client_id`, jeśli taki posiadasz, w przeciwnym razie użyj **Dokumentu metadanych identyfikatora klienta** (klient identyfikuje się za pomocą kontrolowanego przez siebie adresu URL HTTPS, a serwer autoryzacji *pobiera* metadane), w przeciwnym razie wróć do **Dokumentu metadanych klienta dynamicznego RFC 7591** (klient *wciska* `POST /register` i natychmiast otrzymuje `client_id`), w przeciwnym razie podpowiada użytkownikowi. Zalecanym ustawieniem domyślnym jest CIMD, ponieważ całkowicie usuwa rejestrację na serwerze, zachowując jednocześnie model zaufania oparty na systemie DNS; DCR zostaje zachowany w celu zapewnienia kompatybilności wstecznej. Obydwa odkrywają swoje punkty wejścia na podstawie metadanych serwera autoryzacyjnego: `client_id_metadata_document_supported` dla CIMD, `registration_endpoint` dla DCR.

Drugą luką jest rotacja klawiszy. Walidacja JWT zależy od kluczy podpisywania serwera autoryzacyjnego, opublikowanych jako zestaw kluczy internetowych JSON (JWKS). Serwer autoryzacyjny zmienia je zgodnie z harmonogramem (często co godzinę, czasem szybciej w ramach reakcji na incydenty). Serwer MCP, który pobiera JWKS raz podczas rozruchu, sprawdza poprawność aż do okna rotacji — wtedy każde żądanie kończy się niepowodzeniem do czasu ponownego uruchomienia. Produkcja łączy JWKS jako wartość buforowaną z zadaniem odświeżania, które nadpisuje pamięć podręczną przed wygaśnięciem poprzednich kluczy, a także pobieraniem awaryjnym w przypadku braku pamięci podręcznej w przypadku, gdy nadejdzie token podpisany kluczem nowszym niż pamięć podręczna.

Trzecia luka jest wiążąca dla odbiorców. W lekcji 16 przedstawiono wskaźniki zasobów RFC 8707. W produkcji wskaźnik ten staje się twardą kontrolą roszczenia przy każdym żądaniu. Serwer MCP porównuje `token.aud` z własnym kanonicznym adresem URL zasobu i odrzuca niezgodności z protokołem HTTP 401. Jest to jedyna obrona przed serwerem MCP nadrzędnym (lub złośliwym klientem posiadającym token przeznaczony dla jednego serwera) odtwarzającym ten token przeciwko innemu serwerowi w tej samej siatce zaufania.

W tej lekcji każdą szczelinę odwzorowuje się na betonowym kawałku powierzchni. Dokument metadanych jest punktem końcowym HTTP. Odświeżanie pamięci podręcznej JWKS to zaplanowane zadanie plus pamięć podręczna typu klucz-wartość. Sprawdzanie poprawności JWT to procedura wykonywana przez serwer zasobów przed wysłaniem dowolnego narzędzia. Oddziel trzy role, a każda z nich egzekwuje tylko te kontrole, które posiada: serwer autoryzacji wydaje i obraca klucze, serwer zasobów buforuje i sprawdza poprawność, klient wykrywa i rejestruje.

## Koncepcja

### RFC 8414 — Metadane serwera autoryzacji OAuth

Dokument pod adresem `/.well-known/oauth-authorization-server` opisuje wszystko, czego potrzebuje klient:

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

Klient po wykryciu łańcuchów adresów URL zasobów MCP: `oauth-protected-resource` z RFC 9728 (dokument serwera zasobów) podaje nazwę wystawcy, następnie `oauth-authorization-server` (ten dokument RFC) nadaje nazwę każdemu punktowi końcowemu. Klient nigdy nie koduje na stałe adresu URL autoryzacji.

Umowa, którą weryfikujesz przed zaufaniem dostawcy tożsamości w zakresie MCP:

- `code_challenge_methods_supported` obejmuje `S256` (PKCE zgodnie z RFC 7636). Specyfikacja jest jednoznaczna: jeśli to pole jest **nieobecne**, serwer autoryzacyjny nie obsługuje PKCE i klient **MUSI** odmówić kontynuowania.
- `grant_types_supported` zawiera `authorization_code` i odrzuca `password` i `implicit`.
- Ogłaszana jest co najmniej jedna ścieżka rejestracji: `client_id_metadata_document_supported: true` (preferowany CIMD) **lub** `registration_endpoint` (RFC 7591 DCR, rezerwa). Albo spełnia umowę; nie potrzebujesz już DCR.
- `response_types_supported` to dokładnie `["code"]` dla protokołu OAuth 2.1.

Jeśli brakuje `S256`, serwer MCP odmawia wdrożenia przeciwko temu dostawcy tożsamości — dla PKCE nie ma trybu awaryjnego. Jeśli *żadna* ścieżka rejestracji nie jest ogłaszana i nie masz wcześniej zarejestrowanego `client_id`, również nie możesz się zapisać; manifest wdrożenia jest błędny, a nie kod.

### RFC 9728 (podsumowanie) — Metadane zasobów chronionych

Lekcja 16 dotyczyła RFC 9728. Delta w produkcji: ten dokument to jedyne miejsce, w którym klient szuka serwerów autoryzacyjnych, którym ufa *ten* serwer MCP. Pojedynczy serwer MCP może akceptować tokeny od wielu dostawców tożsamości (jeden dla personelu, jeden dla partnerów). RFC 9728 deklaruje ten zestaw; RFC 8414 dokumentuje to, co obsługuje każdy dostawca tożsamości.

```json
{
  "resource": "https://notes.example.com",
  "authorization_servers": ["https://auth.example.com", "https://partners.example.com"],
  "scopes_supported": ["mcp:tools.invoke"],
  "bearer_methods_supported": ["header"],
  "resource_documentation": "https://notes.example.com/docs"
}
```

### Dokumenty metadanych identyfikatora klienta (zalecane ustawienie domyślne)

CIMD odwraca rejestrację z *push* na *pull*. Zamiast prosić serwer autoryzacyjny o wygenerowanie `client_id`, klient używa kontrolowanego przez siebie adresu URL HTTPS **jako** swojego `client_id`. Adres URL jest przekształcany w dokument metadanych JSON; serwer autoryzacji pobiera go na żądanie podczas przepływu OAuth. Zaufanie ma swoje źródło w DNS: jeśli operator serwera ufa `app.example.com`, ufa klientowi obsługiwanemu z `https://app.example.com/client.json`. Brak konieczności rejestracji w obie strony, brak `client_id` przestrzeni nazw do wyczerpania, brak synchronizacji stanu poszczególnych serwerów.

Dokument metadanych hostowany przez klienta:

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

Wartość `client_id` w dokumencie **MUSI** być równa adresowi URL, z którego jest on dostarczany (serwer autoryzacyjny to sprawdza; niedopasowania są odrzucane). Serwer autoryzacyjny ogłasza obsługę za pomocą `client_id_metadata_document_supported: true` w swoich metadanych RFC 8414.

Dwa fakty dotyczące bezpieczeństwa, o których specyfikacja mówi bez ogródek:

- **SSRF.** Serwer autoryzacyjny pobiera adres URL dostarczony przez osobę atakującą. Musi chronić przed fałszowaniem żądań po stronie serwera (bez pobierania do wewnętrznych/administracyjnych punktów końcowych).
- **podszywanie się pod hosta lokalnego.** Sam CIMD nie może powstrzymać lokalnego atakującego przed przejęciem adresu URL metadanych legalnego klienta i powiązaniem dowolnego przekierowania `localhost`. Serwer autoryzacyjny **MUSI** wyraźnie wyświetlać nazwę hosta URI przekierowania podczas wyrażania zgody i **POWINNY** ostrzegać w przypadku przekierowań tylko `localhost`.

Ponieważ CIMD nie potrzebuje stanu po stronie serwera, nie ma rejestratora, który mógłby sprostać wymaganiom DCR. Strona klienta jest przeznaczona tylko do odczytu: udostępniaj dokument metadanych ze statycznego punktu końcowego HTTPS i pozwól serwerowi autoryzacji go pobrać.

### RFC 7591 — dynamiczna rejestracja klienta (kompatybilność awaryjna/wsteczna)

DCR to teraz `MAY`, zachowany ze względu na zgodność wsteczną z wdrożeniami sprzed 2025-11-25 i dostawcami tożsamości, którzy nie obsługują jeszcze CIMD. Bez tego (oraz bez CIMD i rejestracji wstępnej) każdy klient MCP (Cursor, Claude Desktop, agent niestandardowy) potrzebuje wymiany pozapasmowej z administratorem IdP. Dzięki DCR klient publikuje:

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

Serwer odpowiada `client_id` i `registration_access_token` w przypadku późniejszych aktualizacji:

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

`token_endpoint_auth_method: none` to właściwa wartość domyślna dla klientów MCP działających na urządzeniu użytkownika. Dostają tylko `client_id` — bez `client_secret` do eksfiltracji. PKCE zapewnia dowód posiadania, którego potrzebują klienci publiczni.

Trzy pułapki produkcyjne:

— Punkt końcowy rejestracji musi ograniczać szybkość transmisji według źródłowego adresu IP. Bez tego wrogi aktor pisze miliony fałszywych rejestracji i wyczerpuje przestrzeń nazw `client_id`. Przeprowadź kontrolę limitu szybkości, zanim rejestrator obsłuży żądanie.
- `software_statement` (podpisane potwierdzenie JWT dla klienta) jest wymagane przez niektórych dostawców tożsamości w przedsiębiorstwach. Próba lekcji pomija ją; produkcja łączy etap weryfikacji, który odrzuca niepodpisane rejestracje z czegokolwiek innego niż identyfikatory URI przekierowań hosta lokalnego.
- Wartość `registration_access_token` musi być przechowywana jako skrót, a nie zwykły tekst. Kradzież tego tokena oznacza, że ​​osoba atakująca może przepisać identyfikatory URI przekierowania klienta.

### RFC 8707 (podsumowanie) — Wskaźniki zasobów

Lekcja 16 ustaliła kształt. Reguła produkcyjna: każde żądanie tokena zawiera `resource=<canonical-mcp-url>`, a serwer MCP sprawdza, czy `token.aud` pasuje do własnego adresu URL zasobu przy każdym wywołaniu. Kanoniczny URI jest *najbardziej szczegółowym* identyfikatorem serwera: używa schematu i nazwy hosta małymi literami, bez fragmentu i tradycyjnie bez końcowego ukośnika. Komponent ścieżki **nie** jest usuwany przez regułę — specyfikacja zachowuje go, gdy jest potrzebny do zidentyfikowania indywidualnego serwera MCP. Wszystkie `https://mcp.example.com`, `https://mcp.example.com/mcp`, `https://mcp.example.com:8443` i `https://mcp.example.com/server/mcp` są prawidłowymi kanonicznymi identyfikatorami URI. Wybierz jeden na serwer i przypnij `aud` dokładnie do tego. (W tej lekcji próbna wykorzystuje odbiorców typu „bare-host”, np. `https://notes.example.com` dla zwięzłości; wdrożenie, które współhostuje kilka serwerów MCP w ramach jednego źródła, rozróżnia je według ścieżki).

### RFC 7636 (podsumowanie) — PKCE

PKCE jest obowiązkowe w OAuth 2.1. Przepływ kodu autoryzacyjnego lekcji zawsze zawiera `code_challenge` i `code_verifier`. Serwer odrzuca każde żądanie tokenu bez weryfikatora lub z weryfikatorem, który nie łączy się z przechowywanym wyzwaniem.

### Specyfikacja MCP 25.11.2025 Profil uwierzytelniający

Specyfikacja MCP (25.11.2025) dokładnie określa, co musi robić warstwa autoryzacji serwera MCP:

- Zaimplementuj metadane zasobów chronionych RFC 9728 i podaj ich lokalizację za pomocą nagłówka `WWW-Authenticate: Bearer resource_metadata="..."` w 401 **lub** dobrze znanego identyfikatora URI `/.well-known/oauth-protected-resource` (w SEP-985 nagłówek stał się opcjonalny z dobrze znanym rozwiązaniem zastępczym). Pole metadanych `authorization_servers` **MUSI** zawierać nazwę co najmniej jednego serwera.
- Akceptuj tokeny tylko za pośrednictwem `Authorization: Bearer ...` na **każde** żądanie — nigdy w ciągu zapytania, nigdy nie sprawdzane tylko na początku sesji.
- Zweryfikuj `aud`, `iss`, `exp` i wymagane zakresy na żądanie. Serwer **MUSI** sprawdzić, czy token został wydany specjalnie dla niego (odbiorcy); brakujący lub niedopasowany `aud` jest odrzucany i nigdy nie jest traktowany jako symbol wieloznaczny.
- W przypadku 401/403 zwróć `WWW-Authenticate: Bearer` zawierający `error=...`, parametr `resource_metadata="<PRM-URL>"` (adres URL dokumentu metadanych, *nie* samego zasobu) i `scope="..."` na `insufficient_scope` (403). Uwaga: parametrem jest `resource_metadata`, wskaźnik wykrywania — w wyzwaniu nie ma parametru `resource`.
- Wykrywanie serwera autoryzacji akceptuje **albo** metadane OAuth RFC 8414 **lub** OpenID Connect Discovery 1.0; klienci muszą wypróbować oba dobrze znane przyrostki w kolejności priorytetów.
- Klient (nie serwer) chroni przed **atakami typu mix-up**: rejestruje oczekiwany `issuer` przed przekierowaniem i sprawdza parametr `iss` autoryzacji-odpowiedzi (RFC 9207) przed realizacją kodu. Sama PKCE nie powstrzymuje pomyłek, ponieważ klient przekazuje swój `code_verifier` do dowolnego punktu końcowego tokenu, do którego został skierowany.

Wersja robocza OAuth 2.1 jest podłożem; RFC 8414/7591/8707/9728/9207 + RFC 7636 + CIMD to powierzchnia; specyfikacją MCP jest profil.

### Macierz możliwości dostawcy tożsamości

Nie każdy dostawca tożsamości obsługuje pełny profil MCP. Poniższa matryca dokumentuje faktyczne stwierdzenia dotyczące możliwości według specyfikacji z dnia 25.11.2025 r. Jest to *brama do wdrożenia*, a nie zalecenie.

CIMD został dostarczony w specyfikacji z dnia 25.11.2025 r., a podstawowa wersja robocza protokołu OAuth została przyjęta dopiero w październiku 2025 r., więc wsparcie dostawców wciąż napływa — traktuj „CIMD” poniżej jako „w obecnym stanie, sprawdź w swojej dzierżawie”, a nie stałe oświadczenie.

| Kategoria dostawcy tożsamości | Metadane AS (8414/OIDC) | CIMD | RFC 7591 DCR | Zasób RFC 8707 | RFC 7636 S256 PKCE | Notatki |
|---|---|---|---|---|---|---|
| Self-hosted (Keycloak) | tak | powstające | tak | tak (od 24.x) | tak | Referencyjny IdP dla profilu MCP w tej lekcji; pełna ścieżka DCR od początku do końca, CIMD śledzi nową specyfikację. |
| Enterprise SSO (identyfikator Microsoft Entra) | tak | powstające | tak (poziomy premium) | tak | tak | Dostępność DCR różni się w zależności od poziomu najemcy; sprawdź w docelowej dzierżawie przed wdrożeniem. |
| Przedsiębiorstwo SSO (Okta) | tak | powstające | tak (Okta CIC / Auth0) | tak | tak | DCR dostępny na Auth0 (obecnie Okta CIC); klasyczne organizacje Okta wymagają wstępnej rejestracji administratora. |
| IdP logowania społecznościowego (ogólne) | różni się | nie | rzadko | rzadko | tak | Większość dostawców tożsamości społecznościowych traktuje klientów jak partnerów statycznych; brak rejestracji samoobsługowej. Używaj tylko jako źródła tożsamości, na wierzchu umieść własny serwer autoryzacji obsługujący MCP. |
| Niestandardowe / domowe | zależy | zależy | zależy | zależy | zależy | Jeśli wysyłasz własny, wyślij pełny profil i preferuj CIMD. Pominięcie PKCE lub powiązania odbiorców powoduje zerwanie umowy uwierzytelniania MCP. |

Reguła odmowy dla manifestu wdrożenia: jeśli wybrany dostawca tożsamości nie wymieni `S256` w `code_challenge_methods_supported`, serwer MCP odmawia uruchomienia — PKCE nie ma trybu zdegradowanego. Rejestracja to łagodniejsza bramka: potrzebujesz *jednej* ścieżki roboczej (wstępnie zarejestrowanej `client_id`, `client_id_metadata_document_supported: true` lub `registration_endpoint`). Sama nieobecność DCR nie jest już powodem odmowy, ponieważ CIMD lub rejestracja wstępna mogą to pokryć.

### Wzór odświeżania JWKS (obróć w AS, odśwież na serwerze zasobów)

Zachowaj dwa czasowniki oddzielnie, ponieważ ich łączenie to prawdziwy błąd produkcyjny:

- **Obrót** jest tym, co robi *serwer autoryzacji*: wygeneruj nowy klucz podpisujący, opublikuj go w JWKS, a stary wycofaj później. Serwer zasobów nie ma w tym żadnego udziału i nie może tego zrobić — nie przechowuje kluczy prywatnych dostawcy tożsamości.
- **Odświeżanie** jest tym, co robi *serwer zasobów*: ponownie `GET` opublikowany JWKS do swojej pamięci podręcznej. Jest to jedyna akcja JWKS, jaką kiedykolwiek wykonuje serwer zasobów.

Tryb awarii produkcyjnej to przestarzała pamięć podręczna. Rozwiąż go za pomocą zaplanowanego zadania odświeżania i pamięci podręcznej klucz-wartość. Serwer zasobów uruchamia zadanie (cron, timer, cokolwiek oferuje środowisko wykonawcze), które w ustalonych odstępach czasu pobiera `<issuer>/.well-known/jwks.json` i zastępuje `cache[issuer] = {keys, fetched_at}`. Walidator odczytuje z tej pamięci podręcznej. Token, którego w pamięci podręcznej brakuje `kid`, uruchamia **jedno** synchroniczne odświeżenie w trybie awaryjnym, a następnie ponownie sprawdza. Obsługuje to jednocześnie dwa przypadki: zaplanowane odświeżenie i okna nakładania się kluczy, w których token podpisany nowym kluczem pojawia się przed następnym zaplanowanym odświeżeniem.

Rozwiązanie awaryjne **musi polegać na ponownym pobraniu, a nie na rotacji**. Jeśli połączysz ścieżkę pomijania pamięci podręcznej z metodą „rotate-and-mint”, dwie rzeczy psują się: (1) wybicie nowego klucza powoduje wygenerowanie `kid`, który *nadal* nie pasuje do tokena, więc wyszukiwanie i tak kończy się niepowodzeniem; oraz (2) atakujący, który rozpyla tokeny z losowymi wartościami `kid`, wymusza nieograniczoną serię kluczowych kreacji — samookaleczający się DoS. Ponowne pobranie jest idempotentne, więc fałszywe `kid` kosztuje co najwyżej jedno zmarnowane pobranie.

Kształt pamięci podręcznej:

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

Dwa klawisze na raz to stan ustalony. Serwery autoryzacji zmieniają się, wprowadzając kolejny klucz (`k_2026_04`) przed wycofaniem poprzedniego (`k_2026_03`), więc tokeny wydane pod starym kluczem pozostają ważne aż do wygaśnięcia. Pamięć podręczna zawiera związek; walidator wybiera według `kid`.

### Procedura sprawdzania poprawności

Serwer MCP przeprowadza weryfikację przed wysłaniem dowolnego narzędzia. Kształt `code/main.py` wykorzystuje:

```python
result = server.validate(bearer_token, required_scope="mcp:tools.invoke")
if not result["valid"]:
    return {"status": result["status"], "WWW-Authenticate": result["www_authenticate"]}
```

`validate` dekoduje token JWT, rozpoznaje klucz podpisu z pamięci podręcznej JWKS (odświeżając raz w przypadku braku), weryfikuje podpis, następnie sprawdza `iss` z listą dozwolonych, `aud` z kanonicznym zasobem tego serwera, `exp` i wymagany zakres — zwracanie wyzwania `WWW-Authenticate` przy pierwszym niepowodzeniu. Utrzymanie jednej procedury na serwerze zasobów oznacza, że ​​każdy punkt wejścia (każde wywołanie narzędzia, każdy transport) przechodzi tę samą kontrolę; nie ma ścieżki prowadzącej do narzędzia bez uprzedniej walidacji.

### Przewodnik po powtórce odbiorców (ograniczenie uprawnień tokena dostępu)

Serwer A (`notes.example.com`) i serwer B (`tasks.example.com`) rejestrują się na tym samym serwerze autoryzacyjnym. Serwer A jest zagrożony. Osoba atakująca bierze token notatek użytkownika i odtwarza go przeciwko Serwerowi B.

Walidator serwera B:

1. Zdekoduj JWT, pobierz JWKS przez `kid`, zweryfikuj podpis.
2. Sprawdź `iss` względem metadanych chronionego zasobu `authorization_servers`. (Pass — ten sam dostawca tożsamości.)
3. Sprawdź `aud == "https://tasks.example.com"`. (Niepowodzenie — `aud` tokena to `https://notes.example.com`.)
4. Zwróć 401 z `WWW-Authenticate: Bearer error="invalid_token", error_description="audience mismatch", resource_metadata="https://tasks.example.com/.well-known/oauth-protected-resource"`.

Roszczenie odbiorców jest jedyną obroną przed tym atakiem w warstwie protokołu. Pomijanie tego ze względu na wydajność jest najczęstszym błędem produkcyjnym; walidator musi działać przy każdym żądaniu, a nie tylko na początku sesji. Specyfikacja nazywa to **ograniczeniem uprawnień tokenu dostępu**: serwer MCP `MUST` odrzuca każdy token, który nie wymienia go na liście odbiorców.

> **Notatka na temat nazwy.** Specyfikacja zastrzega termin *zdezorientowany zastępca* dla powiązanego, ale odrębnego problemu: serwera MCP działającego jako **proxy** protokołu OAuth dla interfejsu API strony trzeciej, korzystającego ze statycznego identyfikatora klienta, który przekazuje token bez uzyskiwania zgody użytkownika na klienta. Wiązanie odbiorców naprawia powtórkę powyżej; poprawką zdezorientowanego zastępcy jest zgoda na klienta **plus** nigdy nie przesyła tokenu przychodzącego do interfejsów API nadrzędnych (serwer MCP `MUST` otrzymuje własny oddzielny token nadrzędny).

### Ataki mieszane (obrona po stronie klienta, której serwer nie może zapewnić)

Klient komunikuje się z wieloma serwerami autoryzacyjnymi przez całe życie. Złośliwy system AS może próbować zmusić klienta do wykorzystania uczciwego kodu autoryzacyjnego AS w punkcie końcowym tokenu atakującego. Wiązanie odbiorców tutaj nie pomaga — atak ma miejsce, zanim pojawi się jakikolwiek token. Obrona żyje w kliencie (RFC 9207):

1. Przed przekierowaniem klient zapisuje oczekiwane `issuer` ze zweryfikowanych metadanych AS.
2. W odpowiedzi autoryzacyjnej klient porównuje zwrócony parametr `iss` z zarejestrowanym wystawcą (proste porównanie ciągów znaków, bez normalizacji) przed wysłaniem kodu w dowolne miejsce.
3. Niezgodność (lub brak `iss`, gdy system AS ogłaszał `authorization_response_iss_parameter_supported`) → odrzuć i nawet nie wyświetlaj pól `error`.

Sama PKCE nie powstrzymuje pomyłek, ponieważ klient przekazuje swój `code_verifier` do dowolnego punktu końcowego tokenu, do którego został skierowany. Właśnie dlatego specyfikacja rejestruje wystawcę na żądanie wraz z weryfikatorem PKCE i `state`.

### Tryby awarii

- **Nieaktualny JWKS.** Walidator odrzuca ważne tokeny po obróceniu klucza przez system AS. Rozwiązaniem jest powyższy wzorzec cron-refresh + cache-miss-refetch. Nigdy nie buforuj JWKS bez zadania odświeżania.
- **Obróć w razie awarii.** Podłączenie ścieżki pomijania pamięci podręcznej do ścieżki obracania i tworzenia zamiast ponownego pobierania to prawdziwy błąd: nigdy nie generuje brakujących `kid`, a zmienia kontrolowane przez atakującego wartości `kid` w DoS służący do tworzenia kluczy. Rezerwa rezerwowa musi być idempotentem `refresh-jwks`.
- **Brak roszczenia `aud`.** Niektórzy dostawcy tożsamości domyślnie pomijają `aud`, chyba że w żądaniu tokenu znajduje się `resource`. Walidator musi odrzucić tokeny z brakującym `aud`, a nie traktować nieobecności jako symbolu wieloznacznego.
- **Pomyłka spowodowana brakiem kontroli `iss`.** Klient, który nie sprawdza poprawności parametru odpowiedzi autoryzacyjnej `iss` RFC 9207 w stosunku do wystawcy zarejestrowanego przed przekierowaniem, może zostać nakłoniony do wykorzystania uczciwego kodu AS w punkcie końcowym tokenu atakującego. Jest to błąd po stronie klienta; serwer zasobów nie jest w stanie tego zrekompensować.
- **Wyścig o ulepszenie zakresu.** Dwa jednoczesne procesy zwiększania zakresu dla tego samego użytkownika mogą zakończyć się sukcesem i wygenerować dwa tokeny dostępu o różnych zakresach. Walidator musi użyć tokena przedstawionego w żądaniu, a nie sprawdzać „bieżący zakres użytkownika” — tworzy to okno TOCTOU.
- **Kradzież tokena rejestracji.** Wyciek `registration_access_token` umożliwia atakującemu przepisanie identyfikatorów URI przekierowań. Mieszaj je w spoczynku; wymagać od klienta przedstawienia jawnego tekstu przy każdej aktualizacji; obracać się w przypadku podejrzeń.
- **`iss` nie jest przypięty.** Walidator akceptujący dowolne `iss` umożliwia atakującemu utworzenie własnego serwera autoryzacyjnego, zarejestrowanie klienta dla docelowych odbiorców i wystawienie tokenów. Lista `authorization_servers` metadanych zasobów chronionych jest listą dozwolonych; egzekwować to.

## Użyj tego

`code/main.py` realizuje cały proces produkcyjny przy użyciu stdlib Python i trzech ról — `AuthorizationServer`, `ResourceServer` i `Client`. Przepływ:

1. Serwer autoryzacyjny publikuje metadane RFC 8414 pod adresem `/.well-known/oauth-authorization-server`.
2. Klient MCP wywołuje punkt końcowy metadanych i sprawdza jego opcje rejestracji (`client_id_metadata_document_supported` dla CIMD, `registration_endpoint` dla DCR) i `S256` obsługę PKCE.
3. Przewodnik wykorzystuje ścieżkę zastępczą DCR: klient wysyła wiadomość do `/register` (RFC 7591) i otrzymuje `client_id`. (Zamiast tego klient CIMD przedstawiłby własny adres URL HTTPS `client_id` i pominął ten krok).
4. Klient MCP uruchamia przepływ kodu autoryzacyjnego chronionego PKCE (RFC 7636) ze wskaźnikiem `resource` (RFC 8707).
5. Klient MCP wywołuje narzędzie na serwerze MCP za pomocą `Authorization: Bearer ...`.
6. Serwer MCP uruchamia `validate`, rozpoznając klucz podpisujący z pamięci podręcznej JWKS.
7. IdP obraca klucz; zaplanowane odświeżenie ponownie pobiera JWKS do pamięci podręcznej.
8. Następne wywołanie sprawdza poprawność odświeżonych kluczy bez ponownego uruchamiania, a poprzedni token nadal sprawdza poprawność w oknie nakładania się.
9. Próba powtórki dla innego zasobu MCP kończy się wynikiem 401 ze wskaźnikiem `audience mismatch` i wskaźnikiem `resource_metadata`.

JWT używa tutaj HS256 ze wspólnym sekretem (więc lekcja działa tylko na stdlib). Produkcja wykorzystuje RS256 lub EdDSA z powyższym wzorcem JWKS; poza tym logika walidacji jest identyczna. Ponieważ dostawca tożsamości i serwer zasobów działają w jednym procesie, `refresh_jwks` bezpośrednio odczytuje listę kluczy serwera autoryzacyjnego; poprzez kabel jest to HTTP `GET` do `jwks_uri`.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-mcp-auth.md`. Biorąc pod uwagę konfigurację serwera MCP i zestaw możliwości dostawcy tożsamości, umiejętność wysyła powierzchnię uwierzytelniającą do działania — metadane chronionych zasobów, ścieżkę rejestracji do użycia (CIMD, rejestracja wstępna lub rezerwa DCR), harmonogram odświeżania JWKS, mapowanie zakresu i reguły odmowy stosowane, gdy dostawca tożsamości nie obsługuje pełnego profilu RFC.

## Ćwiczenia

1. Uruchom `code/main.py`. Śledź przepływ. Zwróć uwagę, jak dostawca tożsamości zmienia klucz w kroku 6, zaplanowane `refresh_jwks` ponownie pobiera opublikowany zestaw, a zarówno stary token (okno nakładania się), jak i nowy token sprawdzają poprawność bez ponownego uruchamiania.

2. Dodaj nowego dostawcę tożsamości do listy `authorization_servers` metadanych chronionego zasobu. Wydaj token podpisany przez nowego dostawcę tożsamości i potwierdź, że walidator go akceptuje. Wydaj token podpisany przez niezarejestrowanego dostawcę tożsamości i potwierdź odmowę walidatora za pomocą `WWW-Authenticate: Bearer error="invalid_token", error_description="iss not allowed"`.

3. Dodaj kontrolę limitu szybkości do `register_client`, która będzie uruchamiana, zanim rejestrator zaakceptuje żądanie. Użyj zasobnika tokenów na źródłowy adres IP przechowywany w małym dyktacie z kluczem IP.

4. Przeczytaj dokument RFC 7591 i zidentyfikuj dwa pola, których moduł obsługi `/register` lekcji nie sprawdza. Dodaj weryfikację. (Wskazówka: schemat URI `software_statement` i `redirect_uris`.)

5. Dodaj ścieżkę dokumentu metadanych identyfikatora klienta. Podaj `client.json`, którego `client_id` jest równy jego własnemu adresowi URL i poproś serwer autoryzacyjny o pobranie i zweryfikowanie go (odrzuć, jeśli `client_id` ≠ URL). Potwierdź, że klient CIMD rejestruje się bez wywołania `register_client`.

6. Udowodnij poprawkę DoS. Wyślij do walidatora token z losowym `kid` i potwierdź, że `refresh_jwks` zostanie uruchomiony najwyżej raz, a liczba kluczy serwera autoryzacyjnego nie wzrośnie. Następnie celowo podłącz powrót do funkcji „obróć i wybij” i obserwuj, jak rośnie liczba kluczy na fałszywy token – a następnie przywróć ponowne pobieranie.

7. Zaimplementuj po stronie klienta kontrolę `iss` zgodnie z RFC 9207 z sekcji pomyłek: zapisz oczekiwanego wystawcę przed żądaniem autoryzacji, a następnie odrzuć odpowiedź autoryzacyjną, której `iss` nie pasuje.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| ASM | „Dokument metadanych OAuth” | RFC 8414 `/.well-known/oauth-authorization-server` JSON |
| CIMD | „URL metadanych klienta” | Dokument metadanych identyfikatora klienta — adres URL HTTPS używany jako `client_id`; AS pobiera JSON. Zalecane ustawienie domyślne od 2025-11-25 |
| DCR | „Samoobsługowa rejestracja klienta” | RFC 7591 `POST /register` przepływ; zdegradowany do `MAY` rozwiązania zastępczego w 25.11.2025 r. |
| JWKS | „Klucze publiczne do walidacji JWT” | Zestaw kluczy internetowych JSON, pobrany z `jwks_uri`, zaindeksowany przez `kid` |
| Obróć a odśwież | „Aktualizacja kluczy” | *Obróć* = AS wycofuje/wycofuje klucze do podpisywania; *refresh* = serwer zasobów ponownie pobiera opublikowany zestaw. Serwery zasobów zawsze się odświeżają |
| Wskaźnik zasobów | „Parametr odbiorców” | RFC 8707 Parametr `resource` przypinający token do jednego serwera |
| `aud` roszczenie | „Publiczność” | JWT twierdzi, że walidator porównuje z kanonicznym adresem URL zasobu |
| Powtórka publiczności | „Powtórka żetonu” | Token wydany dla Serwera A przedstawiony Serwerowi B; bronione przez weryfikację odbiorców (specyfikacja: ograniczenie uprawnień tokenu dostępu) |
| Zdezorientowany zastępca | „Niewłaściwe użycie tokena proxy” | Serwer proxy MCP ze statycznym identyfikatorem klienta przesyłający token bez zgody każdego klienta; różni się od powtórki publiczności |
| Pomieszany atak | „Zły punkt końcowy tokenu” | Klient zdecydował się wykorzystać uczciwy kod AS w punkcie końcowym atakującego; broniona po stronie klienta za pomocą RFC 9207 `iss` |
| `iss` lista dozwolonych | „Zaufane serwery autoryzacyjne” | Zestaw nazwany w metadanych zasobów chronionych `authorization_servers` |
| `resource_metadata` | „Gdzie znaleźć dokument PRM” | Parametr `WWW-Authenticate` określający adres URL metadanych RFC 9728 w standardzie 401/403 |
| Klient publiczny | „Klient natywny lub przeglądarkowy” | Klient OAuth bez `client_secret`; PKCE rekompensuje |
| `WWW-Authenticate` | „Nagłówek odpowiedzi 401/403” | Zawiera `Bearer error=...` dyrektywy, które przyspieszają odzyskiwanie klienta |

## Dalsze czytanie

- [MCP — Specyfikacja autoryzacji (25.11.2025)](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization) — profil uwierzytelniania MCP implementowany w tej lekcji
- [Blog MCP — Rok MCP: wydanie specyfikacji z listopada 2025 r.](https://blog.modelcontextprotocol.io/posts/2025-11-25-first-mcp-anniversary/) — co zmieniło się w 25.11.2025 r. (degradacja CIMD, XAA, DCR)
- [Aaron Parecki — Rejestracja klienta w specyfikacji autoryzacji MCP z listopada 2025 r.](https://aaronparecki.com/2025/11/25/1/mcp-authorization-spec-update) — uzasadnienie CIMD-over-DCR
- [Dokument metadanych identyfikatora klienta OAuth (draft-ietf-oauth-client-id-metadata-document-00)](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-client-id-metadata-document-00) – CIMD
- [RFC 8414 — Metadane serwera autoryzacji OAuth 2.0](https://datatracker.ietf.org/doc/html/rfc8414) — umowa dotycząca wykrywania
- [RFC 7591 — Protokół dynamicznej rejestracji klienta OAuth 2.0](https://datatracker.ietf.org/doc/html/rfc7591) — DCR (ścieżka zastępcza)
— [RFC 7636 — Klucz próbny do wymiany kodów (PKCE)](https://datatracker.ietf.org/doc/html/rfc7636) — dowód posiadania dla klienta publicznego
- [RFC 8707 — Wskaźniki zasobów dla OAuth 2.0](https://datatracker.ietf.org/doc/html/rfc8707) — przypinanie odbiorców
- [RFC 9728 — Metadane zasobów chronionych OAuth 2.0](https://datatracker.ietf.org/doc/html/rfc9728) — wykrywanie serwera zasobów
- [RFC 9207 — Identyfikacja wystawcy serwera autoryzacji OAuth 2.0](https://datatracker.ietf.org/doc/html/rfc9207) — parametr `iss` chroniący przed atakami typu mix-up
- [Wersja robocza OAuth 2.1](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-v2-1) — skonsolidowane podłoże OAuth