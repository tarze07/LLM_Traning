# MCP Security II — OAuth 2.1, wskaźniki zasobów, zakresy przyrostowe

> Zdalne serwery MCP wymagają autoryzacji, a nie tylko uwierzytelnienia. Specyfikacja z dnia 25.11.2025 jest zgodna z protokołem OAuth 2.1 + PKCE + wskaźnikami zasobów (RFC 8707) + metadanymi zasobów chronionych (RFC 9728). SEP-835 dodaje przyrostową zgodę na zakres ze zwiększoną autoryzacją na 403 WWW-Authenticate. Ta lekcja implementuje przepływ step-up jako maszynę stanów, dzięki czemu można zobaczyć każdy przeskok.

**Typ:** Kompilacja
**Języki:** Python (stdlib, symulator maszyny stanowej OAuth)
**Wymagania:** Faza 13 · 09 (transporty), Faza 13 · 15 (ochrona I)
**Czas:** ~75 minut

## Cele nauczania

- Odróżnij serwer zasobów od obowiązków serwera autoryzacji.
- Przejdź przez przepływ kodu autoryzacyjnego OAuth 2.1 chronionego PKCE.
- Użyj `resource` (RFC 8707) i metadanych zasobów chronionych (RFC 9728), aby zapobiec atakom z użyciem zdezorientowanego zastępcy.
- Zaimplementuj autoryzację typu step-up: serwer odpowiada 403 za pomocą WWW-Authenticate z prośbą o wyższy zakres; klient ponownie pyta użytkownika o zgodę i ponawia próby.

## Problem

Wczesne MCP (sprzed 2025 r.) dostarczało zdalne serwery z kluczami API ad hoc lub nawet bez uwierzytelnienia. Specyfikacja z dnia 25.11.2025 wypełnia tę lukę dzięki pełnemu profilowi ​​OAuth 2.1.

Trzy rzeczywiste potrzeby:

- **Zwykłe serwery zdalne.** Użytkownik instaluje zdalny serwer MCP, który uzyskuje dostęp do jego Notion / GitHub / Gmaila. OAuth 2.1 z PKCE to właściwy kształt.
- **Eskalacja zakresu.** Serwer notatek z przyznanym `notes:read` może później potrzebować `notes:write` do określonego działania. Zamiast powtarzać cały proces, step-up (SEP-835) wymaga dodatkowego zakresu.
- **Zdezorientowana zastępcza ochrona.** Klient posiada token ograniczony do odbiorców dla Serwera A. Serwer A jest złośliwy i próbuje przedstawić token Serwerowi B. Wskaźniki zasobów (RFC 8707) przypinają token do zamierzonej grupy odbiorców.

OAuth 2.1 nie jest niczym nowym. Nowością jest profil MCP: określone wymagane przepływy (tylko kod autoryzacyjny + PKCE; brak ukrytych danych, domyślnie brak poświadczeń klienta), wskaźniki zasobów obowiązkowe przy każdym żądaniu tokena oraz publikowane metadane zasobów chronionych, aby klienci wiedzieli, dokąd się udać.

## Koncepcja

### Role

- **Klient.** Klient MCP (Claude Desktop, Cursor, itp.).
- **Serwer zasobów.** Serwer MCP (notatki, GitHub, Postgres, cokolwiek).
- **Serwer autoryzacji.** Wydaje tokeny. Może to być ta sama usługa, co serwer zasobów lub oddzielny dostawca tożsamości (Auth0, Keycloak, Cognito).

W profilu MCP serwery zasobów i autoryzacji MOGĄ być tym samym hostem, ale POWINNY być rozróżniane za pomocą adresów URL.

### Kod autoryzacyjny + PKCE

Przepływ:

1. Klient generuje `code_verifier` (losowo) i `code_challenge` (SHA256).
2. Klient przekierowuje użytkownika do `/authorize?response_type=code&client_id=...&redirect_uri=...&scope=notes:read&code_challenge=...&resource=https://notes.example.com`.
3. Użytkownik wyraża zgodę. Serwer autoryzacyjny przekierowuje do `redirect_uri?code=...`.
4. Klient wysyła POST do `/token?grant_type=authorization_code&code=...&code_verifier=...&resource=...`.
5. Serwer autoryzacyjny sprawdza hash weryfikatora względem przechowywanego wyzwania i wystawia token dostępu.
6. Klient wykorzystuje token: `Authorization: Bearer ...` przy każdym żądaniu kierowanym do serwera zasobów.

PKCE zapobiega atakom polegającym na przechwyceniu kodu autoryzacyjnego. Wskaźniki zasobów uniemożliwiają ważność tokena w innym miejscu.

### Metadane zasobów chronionych (RFC 9728)

Serwer zasobów publikuje dokument `.well-known/oauth-protected-resource`:

```json
{
  "resource": "https://notes.example.com",
  "authorization_servers": ["https://auth.example.com"],
  "scopes_supported": ["notes:read", "notes:write", "notes:delete"]
}
```

Klient odkrywa serwer autoryzacji z serwera zasobów. Redukuje konfigurację — klient potrzebuje jedynie adresu URL zasobu.

### Wskaźniki zasobów (RFC 8707)

Parametr `resource` w żądaniu tokenu przypina docelowych odbiorców tokenu. Wystawiony token zawiera `aud: "https://notes.example.com"`. Inny serwer MCP odbierający ten token sprawdza `aud` i odrzuca go.

### Model zakresu

Zakresy to ciągi znaków oddzielone spacjami. Typowe konwencje MCP:

- `notes:read`, `notes:write`, `notes:delete`
- `admin:*` dla funkcji administratora (używaj oszczędnie)
- `profile:read` dla tożsamości

Wybór zakresu powinien być najmniej uprzywilejowany: poproś o to, czego potrzebujesz teraz, zwiększ zakres, gdy potrzebujesz więcej.

### Autoryzacja stopniowa (SEP-835)

Przyznaje użytkownikowi `notes:read`. Później proszą agenta o usunięcie notatki. Serwer odpowiada:

```
HTTP/1.1 403 Forbidden
WWW-Authenticate: Bearer error="insufficient_scope",
    scope="notes:delete", resource="https://notes.example.com"
```

Klient widzi błąd niewystarczającego_zakresu, wyświetla monit o zgodę na dodatkowy zakres, wykonuje dla niego mini przepływ OAuth, ponawia żądanie z nowym tokenem.

### Weryfikacja odbiorców tokenu

Każde żądanie: serwer sprawdza `token.aud == self.resource_url`. Mismatch = 401. To zatrzymuje ponowne użycie tokena między serwerami.

### Tokeny krótkotrwałe i rotacja

Tokeny dostępu POWINNY być krótkotrwałe (domyślnie 1 godzina). Tokeny odświeżania obracają się przy każdym odświeżeniu. Klient obsługuje ciche odświeżanie w tle.

### Brak przekazywania tokenu

Serwery próbkujące (faza 13 · 11) NIE MOGĄ przekazywać tokena klienta do innych usług. Żądanie pobrania próbki jest granicą.

### Zdezorientowany zastępca zapobiegania

Token wiąże się z `aud`. Klient łączy się z `client_id`. Każde żądanie zostało sprawdzone pod kątem obu. Specyfikacja wyraźnie zakazuje starego wzorca „przekaż token”, który był powszechny w ekosystemach narzędzi zdalnych przed wprowadzeniem MCP.

### Wykrywanie identyfikatora klienta

Każdy klient MCP publikuje swoje metadane pod stałym adresem URL. Serwery autoryzacji mogą pobrać dokument metadanych klienta, aby odkryć identyfikatory URI przekierowań i informacje kontaktowe. Eliminuje to ręczną rejestrację klienta.

### Bramy i OAuth

Faza 13 · 17 pokazuje, jak brama korporacyjna obsługuje OAuth: brama przechowuje poświadczenia dla serwerów nadrzędnych, tokeny dla klienta są wydawane przez bramę, a tokeny nadrzędne nigdy nie opuszczają bramy. To odwraca model zaufania — użytkownicy jednokrotnie uwierzytelniają się w bramie; bramka obsługuje autoryzacje N serwerów.

## Użyj tego

`code/main.py` symuluje pełny proces zwiększania poziomu protokołu OAuth 2.1 jako maszyna stanu. Implementuje:

- Weryfikator kodu PKCE / generowanie wyzwań.
- Przepływ kodu autoryzacyjnego ze wskaźnikiem zasobów.
— Punkt końcowy metadanych zasobów chronionych.
- Weryfikacja tokena z kontrolą odbiorców.
- Zwiększenie poziomu `insufficient_scope`.

W tej lekcji nie ma serwera HTTP; maszyna stanów działa w pamięci, dzięki czemu można śledzić każdy przeskok. Lekcja dotycząca bramy z fazy 13 · 17 łączy ją z rzeczywistym transportem.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-oauth-scope-planner.md`. Mając do dyspozycji zdalny serwer MCP z narzędziami, umiejętność projektuje zestaw zakresów, zasady przypinania i zasady zwiększania wydajności.

## Ćwiczenia

1. Uruchom `code/main.py`. Prześledź dwuzakresowy przepływ stopniowy. Zwróć uwagę, które przeskoki powtarzają się przy zwiększaniu głośności.

2. Dodaj rotację tokenów odświeżania: każde odświeżenie generuje nowy token odświeżania i unieważnia stary. Zasymuluj użycie skradzionego tokena odświeżania po rotacji i potwierdź jego niepowodzenie.

3. Zaimplementuj punkt końcowy metadanych chronionych zasobów jako rzeczywistą odpowiedź HTTP przy użyciu stdlib http.server. Odbij punkt końcowy /mcp z lekcji 09.

4. Zaprojektuj hierarchię zakresu dla serwera GitHub MCP: przeczytaj repozytorium, napisz PR, zatwierdź PR, połącz PR, admin. Użyj step-up pomiędzy każdym poziomem.

5. Przeczytaj RFC 8707 i RFC 9728. Zidentyfikuj jedno pole w 9728, którego MCP używa inaczej niż w przykładzie RFC. (Wskazówka: dotyczy `scopes_supported`.)

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| OAuth 2.1 | „Nowoczesne OAuth” | Skonsolidowane RFC, które nakazuje PKCE i zabrania ukrytego przepływu |
| PKCE | „Dowód posiadania” | Weryfikator kodu + wyzwanie polegające na przechwyceniu kodu autoryzacyjnego |
| Wskaźnik zasobów | „Tokenowi odbiorcy” | RFC 8707 `resource` parametr przypinający token do jednego serwera |
| Metadane zasobów chronionych | „Dokument odkrycia” | RFC 9728 `.well-known/oauth-protected-resource` |
| Autoryzacja stopniowa | „Zgoda przyrostowa” | Przepływ SEP-835 dotyczący dodawania zakresów na żądanie |
| `insufficient_scope` | „403 z uwierzytelnianiem WWW” | Sygnał serwera do ponownej zgody na większy zakres |
| Zdezorientowany zastępca | „Ponowne wykorzystanie tokena w różnych usługach” | Atak, w którym zaufany posiadacz w niewłaściwy sposób przekazuje token |
| Znak krótkotrwały | „Token dostępu TTL” | Nośnik, który szybko wygasa; odśwież token odnawia |
| Hierarchia zakresu | „Najmniejszy stos uprawnień” | Zestaw stopniowanych zakresów ze stopniowaniem między poziomami |
| Metadane identyfikatora klienta | „Dokument odkrywania klienta” | Adres URL, pod którym klient publikuje własne metadane OAuth |

## Dalsze czytanie

- [MCP — specyfikacja autoryzacji](https://modelcontextprotocol.io/specification/draft/basic/authorization) — kanoniczny profil MCP OAuth
- [den.dev — listopadowa specyfikacja autoryzacji MCP](https://den.dev/blog/mcp-november-authorization-spec/) — opis zmian 25.11.2025
- [RFC 8707 — Wskaźniki zasobów dla OAuth 2.0] (https://datatracker.ietf.org/doc/html/rfc8707) — dokument RFC przypinający odbiorców
- [RFC 9728 — metadane zasobów chronionych OAuth 2.0] (https://datatracker.ietf.org/doc/html/rfc9728) — dokument RFC dotyczący wykrywania
- [Aembit — MCP OAuth 2.1, PKCE i przyszłość autoryzacji AI](https://aembit.io/blog/mcp-oauth-2-1-pkce-and-the-future-of-ai-authorization/) — praktyczny przewodnik krok po kroku