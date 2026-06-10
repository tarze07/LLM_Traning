# Bezpieczeństwo MCP II — OAuth 2.1, wskaźniki zasobów i przyrostowe zakresy uprawnień

> Zdalne serwery MCP wymagają autoryzacji, a nie tylko samego uwierzytelnienia. Specyfikacja z dnia 25.11.2025 r. bazuje na protokołach OAuth 2.1, PKCE, wskaźnikach zasobów (RFC 8707) oraz metadanych zasobów chronionych (RFC 9728). Standard SEP-835 wprowadza mechanizm przyrostowej zgody na zakres uprawnień (incremental scope consent) poprzez eskalację autoryzacji (step-up authorization) przy użyciu nagłówka 403 WWW-Authenticate. Ta lekcja implementuje przepływ step-up w postaci maszyny stanów, co pozwala prześledzić każde przejście krok po kroku.

**Typ:** Implementacja
**Język:** Python (biblioteka standardowa, symulator maszyny stanów OAuth)
**Wymagania:** Faza 13 · 09 (protokoły transportowe), Faza 13 · 15 (bezpieczeństwo I)
**Czas:** ~75 minut

## Cele lekcji

- Rozróżnianie odpowiedzialności serwera zasobów (Resource Server) i serwera autoryzacji (Authorization Server).
- Prześledzenie przepływu kodu autoryzacyjnego (Authorization Code Flow) w standardzie OAuth 2.1 zabezpieczonego przez PKCE.
- Wykorzystanie parametru `resource` (RFC 8707) oraz metadanych zasobów chronionych (RFC 9728) w celu ochrony przed atakiem typu "zdezorientowany zastępca" (confused deputy).
- Zaimplementowanie eskalacji autoryzacji (step-up authorization): serwer odpowiada kodem 403 wraz z nagłówkiem WWW-Authenticate, żądając szerszego zakresu uprawnień; klient ponownie prosi użytkownika o zgodę i ponawia żądanie.

## Problem

Wczesne wersje MCP (przed 2025 rokiem) obsługiwały zdalne serwery za pomocą doraźnych (ad hoc) kluczy API lub nawet bez żadnego uwierzytelniania. Specyfikacja z 25.11.2025 r. eliminuje te braki, wprowadzając pełny profil OAuth 2.1.

Trzy kluczowe potrzeby biznesowe i techniczne:

- **Klasyczne serwery zdalne.** Użytkownik instaluje zdalny serwer MCP, który komunikuje się z jego kontem Notion, GitHub czy Gmail. Protokół OAuth 2.1 z PKCE jest do tego optymalnym rozwiązaniem.
- **Eskalacja uprawnień (zakresów).** Serwer obsługujący notatki posiadający uprawnienie `notes:read` może później potrzebować `notes:write` do wykonania konkretnej operacji. Zamiast powtarzać cały proces autoryzacji od początku, mechanizm step-up (SEP-835) pozwala zażądać jedynie brakującego zakresu.
- **Ochrona przed zdezorientowanym zastępcą (Confused Deputy).** Klient posiada token wydany wyłącznie dla Serwera A. Jeśli Serwer A jest złośliwy, może próbować użyć tego tokenu do autoryzacji w Serwerze B. Wskaźniki zasobów (RFC 8707) przypisują token do konkretnego odbiorcy, zapobiegając takim nadużyciom.

OAuth 2.1 sam w sobie nie jest nowym standardem. Nowość stanowi dedykowany profil MCP: ściśle zdefiniowane, wymagane przepływy (wyłącznie Authorization Code Flow + PKCE; brak przepływu typu Implicit, domyślny brak poświadczeń klienta - Client Credentials), obowiązkowe stosowanie wskaźników zasobów przy każdym żądaniu tokenu oraz publikowanie metadanych zasobów chronionych, dzięki czemu klienci automatycznie wykrywają punkty końcowe autoryzacji.

## Założenia koncepcyjne

### Role

- **Klient (Client).** Aplikacja kliencka MCP (np. Claude Desktop, Cursor).
- **Serwer zasobów (Resource Server).** Serwer MCP (np. baza notatek, GitHub, Postgres).
- **Serwer autoryzacji (Authorization Server).** Wystawca tokenów. Może to być ta sama usługa co serwer zasobów lub zewnętrzny dostawca tożsamości (np. Auth0, Keycloak, Cognito).

W profilu MCP serwer zasobów i serwer autoryzacji MOGĄ współdzielić ten sam host, ale POWINNY być rozróżniane za pomocą osobnych adresów URL.

### Przepływ kodu autoryzacyjnego z PKCE

Przebieg procesu:

1. Klient generuje losowy `code_verifier` oraz jego skrót `code_challenge` (przy użyciu SHA256).
2. Klient przekierowuje użytkownika do punktu `/authorize?response_type=code&client_id=...&redirect_uri=...&scope=notes:read&code_challenge=...&resource=https://notes.example.com`.
3. Użytkownik udziela zgody. Serwer autoryzacji przekierowuje z powrotem pod wskazany `redirect_uri?code=...`.
4. Klient wysyła żądanie POST do `/token?grant_type=authorization_code&code=...&code_verifier=...&resource=...`.
5. Serwer autoryzacji weryfikuje poprawność `code_verifier` względem zapisanego wyzwania `code_challenge` i wystawia token dostępu.
6. Klient dołącza token w nagłówku `Authorization: Bearer ...` do każdego zapytania kierowanego do serwera zasobów.

PKCE zapobiega atakom polegającym na przechwyceniu kodu autoryzacyjnego. Wskaźniki zasobów ograniczają ważność tokenu, sprawiając, że nie może on zostać użyty w innym systemie.

### Metadane zasobów chronionych (RFC 9728)

Serwer zasobów udostępnia plik konfiguracyjny pod adresem `.well-known/oauth-protected-resource`:

```json
{
  "resource": "https://notes.example.com",
  "authorization_servers": ["https://auth.example.com"],
  "scopes_supported": ["notes:read", "notes:write", "notes:delete"]
}
```

Klient dynamicznie wykrywa adres serwera autoryzacji na podstawie informacji z serwera zasobów. Upraszcza to konfigurację — klient musi znać jedynie adres URL samego zasobu.

### Wskaźniki zasobów (RFC 8707)

Parametr `resource` w żądaniu tokenu wskazuje docelowego odbiorcę. Wystawiony token zawiera deklarację `aud: "https://notes.example.com"`. Każdy inny serwer MCP, który otrzyma taki token, po zweryfikowaniu pola `aud` odrzuci go.

### Model zakresów uprawnień (Scopes)

Zakresy są reprezentowane przez ciągi znaków rozdzielone spacjami. Typowe konwencje stosowane w MCP:

- `notes:read`, `notes:write`, `notes:delete`
- `admin:*` dla funkcji administracyjnych (zaleca się używać z umiarem)
- `profile:read` do odczytu danych profilowych

Dobór zakresów powinien być zgodny z zasadą najmniejszych uprawnień (least privilege): wnioskuj tylko o te zasoby, które są niezbędne w danym momencie, i eskaluj uprawnienia dopiero wtedy, gdy wymagają tego kolejne operacje.

### Autoryzacja stopniowa / przyrostowa (SEP-835)

Załóżmy, że użytkownik przyznał uprawnienie `notes:read`. W trakcie sesji zleca agentowi usunięcie notatki. W takiej sytuacji serwer odpowiada:

```
HTTP/1.1 403 Forbidden
WWW-Authenticate: Bearer error="insufficient_scope",
    scope="notes:delete", resource="https://notes.example.com"
```

Klient identyfikuje błąd `insufficient_scope`, wyświetla użytkownikowi monit z prośbą o zgodę na dodatkowy zakres, uruchamia uproszczony przepływ OAuth w celu pozyskania nowego tokenu i ponawia pierwotne zapytanie.

### Weryfikacja odbiorcy tokenu (Audience)

Przy każdym żądaniu serwer weryfikuje warunek `token.aud == self.resource_url`. W przypadku niezgodności (mismatch) zwraca kod 401. Zapobiega to używaniu tego samego tokenu na różnych serwerach.

### Krótkotrwałe tokeny i ich rotacja

Tokeny dostępu (access tokens) POWINNY mieć krótki czas życia (domyślnie 1 godzina). Tokeny odświeżania (refresh tokens) powinny podlegać rotacji przy każdym użyciu. Klient odpowiada za ciche odświeżanie tokenów w tle.

### Zakaz przekazywania tokenów

Serwery realizujące próbkowanie (faza 13 · 11) NIE MOGĄ przekazywać tokenu klienta do zewnętrznych usług. Żądanie pobrania próbki stanowi nieprzekraczalną granicę bezpieczeństwa.

### Zapobieganie problemowi zdezorientowanego zastępcy

Token jest ściśle powiązany z odbiorcą (`aud`), a klient identyfikuje się za pomocą `client_id`. Każde przychodzące żądanie podlega weryfikacji pod kątem obu tych parametrów. Specyfikacja wprost zabrania przestarzałego antywzorca polegającego na "przekazywaniu tokenu dalej", powszechnego w dawnych ekosystemach zdalnych narzędzi przed standaryzacją MCP.

### Dynamiczne wykrywanie tożsamości klienta

Każdy klient MCP publikuje swoje metadane pod stałym, publicznym adresem URL. Serwery autoryzacji mogą pobierać ten dokument metadanych, aby automatycznie odczytać dozwolone adresy redirect URI oraz dane kontaktowe. Eliminuje to konieczność ręcznej rejestracji klientów.

### Bramy sieciowe (Gateways) a OAuth

Faza 13 · 17 szczegółowo opisuje obsługę OAuth przez bramy korporacyjne: brama przechowuje dane uwierzytelniające do serwerów nadrzędnych (upstream), tokeny dla klienta są wystawiane bezpośrednio przez bramę, a oryginalne tokeny upstream nigdy jej nie opuszczają. Taki układ odwraca tradycyjny model zaufania — użytkownik uwierzytelnia się jednorazowo w bramie, a ona zarządza autoryzacją w N niezależnych serwerach.

## Zastosowanie w praktyce

Plik `code/main.py` symuluje kompletny proces przyrostowej autoryzacji OAuth 2.1 zaimplementowany jako maszyna stanów. Zawiera on:

- Generowanie wyzwań i weryfikację kodu PKCE.
- Przepływ kodu autoryzacyjnego z uwzględnieniem wskaźników zasobów.
- Punkt końcowy metadanych zasobów chronionych (Protected Resource Metadata).
- Weryfikację tokenów wraz z walidacją pola odbiorcy (audience).
- Obsługę eskalacji uprawnień w przypadku błędu `insufficient_scope`.

W ramach tej lekcji nie uruchamiamy rzeczywistego serwera HTTP – maszyna stanów działa w pamięci podręcznej procesu, co ułatwia analizowanie poszczególnych kroków. Połączenie z fizycznymi protokołami transportowymi zostanie przedstawione w lekcji o bramie sieciowej w fazie 13 · 17.

## Zadanie praktyczne

Ta lekcja wymaga przygotowania pliku `outputs/skill-oauth-scope-planner.md`. Na podstawie specyfikacji zdalnego serwera MCP i udostępnianych przez niego narzędzi należy zaprojektować strukturę zakresów uprawnień, reguły przypinania odbiorców oraz polityki eskalacji autoryzacji.

## Ćwiczenia

1. Uruchom skrypt `code/main.py`. Prześledź przebieg dwuetapowej eskalacji autoryzacji. Zwróć uwagę, które kroki są powtarzane podczas rozszerzania uprawnień.

2. Zaimplementuj rotację tokenów odświeżania: każda operacja odświeżenia powinna generować nowy token odświeżania i unieważniać poprzedni. Przetestuj scenariusz użycia skradzionego tokenu po dokonaniu rotacji i upewnij się, że operacja ta zostanie zablokowana.

3. Zaimplementuj punkt końcowy metadanych zasobów chronionych jako rzeczywistą odpowiedź HTTP z użyciem wbudowanego modułu `http.server` w Pythonie. Zintegruj go z punktem końcowym `/mcp` z lekcji 09.

4. Zaprojektuj strukturę zakresów uprawnień dla serwera GitHub MCP: odczyt repozytorium, tworzenie PR, zatwierdzanie PR, scalanie PR, uprawnienia administratora. Zastosuj mechanizm step-up pomiędzy poszczególnymi poziomami.

5. Zapoznaj się z dokumentami RFC 8707 oraz RFC 9728. Wskaż jedno pole w specyfikacji RFC 9728, którego MCP używa w odmienny sposób niż opisano w przykładach normy (Wskazówka: przeanalizuj użycie `scopes_supported`).

## Kluczowe pojęcia

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| OAuth 2.1 | „Nowoczesne OAuth” | Skonsolidowany standard RFC nakazujący stosowanie PKCE i zakazujący przepływu typu Implicit |
| PKCE | „Dowód posiadania” | Mechanizm zabezpieczający (Proof Key for Code Exchange) oparty na parze weryfikator-wyzwanie, zapobiegający przechwyceniu kodu autoryzacyjnego |
| Wskaźnik zasobów | „Tokenowi odbiorcy” | Parametr `resource` z RFC 8707 przypisujący token do konkretnego serwera |
| Metadane zasobów chronionych | „Dokument odkrycia” | Standard RFC 9728 definiujący plik autowykrywania `.well-known/oauth-protected-resource` |
| Autoryzacja stopniowa | „Zgoda przyrostowa” | Przepływ SEP-835 umożliwiający dynamiczne rozszerzanie uprawnień na żądanie |
| `insufficient_scope` | „403 z uwierzytelnianiem WWW” | Zwracany przez serwer kod błędu sygnalizujący potrzebę ponownej autoryzacji w celu uzyskania szerszych uprawnień |
| Zdezorientowany zastępca | „Ponowne wykorzystanie tokena w różnych usługach” | Klasyczny podatność/atak (confused deputy), w którym zaufany podmiot nieumyślnie przekazuje lub używa tokenu w nieautoryzowanym celu |
| Krótkotrwały token | „Token dostępu TTL” | Krótki czas życia tokenu dostępu; mechanizm rotacji z użyciem tokenu odświeżania |
| Hierarchia zakresu | „Najmniejszy stos uprawnień” | Struktura uprawnień zaprojektowana zgodnie z zasadą najmniejszych uprawnień z przejściami step-up |
| Metadane identyfikatora klienta | „Dokument odkrywania klienta” | Adres URL, pod którym klient MCP udostępnia własne metadane OAuth |

## Polecana literatura / dokumentacja

- [MCP — specyfikacja autoryzacji](https://modelcontextprotocol.io/specification/draft/basic/authorization) — kanoniczny profil MCP OAuth
- [den.dev — listopadowa specyfikacja autoryzacji MCP](https://den.dev/blog/mcp-november-authorization-spec/) — opis zmian 25.11.2025
- [RFC 8707 — Wskaźniki zasobów dla OAuth 2.0](https://datatracker.ietf.org/doc/html/rfc8707) — dokument RFC przypinający odbiorców
- [RFC 9728 — metadane zasobów chronionych OAuth 2.0](https://datatracker.ietf.org/doc/html/rfc9728) — dokument RFC dotyczący wykrywania
- [Aembit — MCP OAuth 2.1, PKCE i przyszłość autoryzacji AI](https://aembit.io/blog/mcp-oauth-2-1-pkce-and-the-future-of-ai-authorization/) — praktyczny przewodnik krok po kroku
