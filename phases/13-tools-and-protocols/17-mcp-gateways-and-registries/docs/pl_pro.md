# Bramy i rejestry MCP — korporacyjne warstwy kontroli (Control Planes)

> Przedsiębiorstwa nie mogą pozwolić sobie na to, aby każdy programista instalował dowolne serwery MCP. Brama centralizuje uwierzytelnianie, RBAC, audyt, limitowanie żądań (rate limiting), buforowanie oraz wykrywanie zatruć narzędzi, a następnie udostępnia skonsolidowany interfejs narzędziowy jako pojedynczy punkt końcowy MCP. Oficjalny rejestr MCP (rozwijany przez Anthropic, GitHub, PulseMCP i Microsoft, ze zweryfikowanymi przestrzeniami nazw) stanowi kanoniczne źródło danych. W tej lekcji wyjaśniamy rolę bramy w architekturze, omawiamy jej minimalną implementację oraz analizujemy rynek dostawców w 2026 roku.

**Typ:** Teoria
**Język:** Python (biblioteka standardowa, minimalna brama)
**Wymagania wstępne:** Faza 13 · 15 (zatrucie narzędzi), Faza 13 · 16 (OAuth 2.1)
**Czas:** ~45 minut

## Cele lekcji

- Zrozumienie roli bramy MCP w architekturze (pośredniczy między klientami MCP a wieloma serwerami zaplecza).
- Zaimplementowanie pięciu głównych zadań bramy: uwierzytelniania, RBAC, audytu, limitowania żądań (rate limiting) oraz reguł bezpieczeństwa.
- Wymuszenie weryfikacji manifestu z przypiętymi skrótami (hash pinning) narzędzi na poziomie bramy.
- Rozróżnienie oficjalnego rejestru MCP od tzw. metarejestrów (Glama, MCPMarket, MCP.so, Smithery, LobeHub).

## Problem

W firmie z listy Fortune 500 mamy do czynienia z 30 zatwierdzonymi serwerami MCP, 5000 programistów, surowymi wymogami zgodności (compliance) i audytu oraz zespołem ds. bezpieczeństwa, który wymaga scentralizowanego zarządzania regułami. Umożliwienie każdemu programiście instalacji dowolnych serwerów bezpośrednio w jego środowisku IDE rodzi ogromne ryzyko.

Wzorzec bramy sieciowej (Gateway):

1. Brama działa jako pojedynczy punkt końcowy HTTP, z którym łączą się aplikacje klienckie deweloperów.
2. Brama przechowuje i chroni dane uwierzytelniające do poszczególnych serwerów MCP w sieci wewnętrznej (backend).
3. Każde żądanie programisty jest uwierzytelniane, a zakres jego uprawnień jest weryfikowany przez serwer OAuth bramy.
4. Brama przekazuje żądanie do odpowiedniego serwera zaplecza (backend), aplikując skonfigurowane reguły bezpieczeństwa.
5. Wszystkie wywołania są rejestrowane w dzienniku audytu.

Cloudflare MCP Ports, Kong AI Gateway, IBM ContextForge, MintMCP, TrueFoundry, Envoy AI Gateway — to przykłady dedykowanych bram lub rozszerzeń bram sieciowych udostępnionych w latach 2025–2026.

W tym samym czasie uruchomiony został oficjalny rejestr MCP jako kanoniczne źródło nadrzędne (upstream): zawiera on zweryfikowane serwery z unikalnymi przestrzeniami nazw opartymi na odwróconym DNS, z których brama może bezpiecznie pobierać dane. Metarejestry (takie jak Glama, MCPMarket, MCP.so, Smithery, LobeHub) pełnią funkcję agregatorów serwerów z różnych źródeł.

## Założenia koncepcyjne

### Pięć głównych zadań bramy

1. **Uwierzytelnianie i autoryzacja (Auth).** OAuth 2.1 w celu identyfikacji programisty i przypisania go do odpowiednich ról.
2. **Kontrola dostępu (RBAC).** Reguły określające uprawnienia użytkownika: które serwery, jakie narzędzia i jakie zakresy są dla niego dostępne.
3. **Audyt (Auditing).** Rejestrowanie każdego wywołania: kto, kiedy, co wywołał oraz jaki był rezultat.
4. **Limitowanie żądań (Rate Limiting).** Narzucanie limitów na użytkownika, narzędzie lub serwer w celu zapobiegania przeciążeniom i nadużyciom.
5. **Reguły bezpieczeństwa (Policies).** Odrzucanie zatrutych opisów, egzekwowanie reguły dwóch oraz maskowanie wrażliwych danych osobowych (PII).

### Brama jako spójny punkt wejścia

Z punktu widzenia programisty brama zachowuje się jak pojedynczy serwer MCP. Wewnętrznie multipleksuje ona żądania do N serwerów backendowych. Identyfikatory sesji (faza 13 · 09) są mapowane i przepisywane na granicy sieciowej bramy.

### Przechowywanie danych uwierzytelniających

Programiści nie mają bezpośredniego dostępu do tokenów uwierzytelniających backend. Brama przechowuje te dane u siebie (lub korzysta z bezpiecznego pośrednictwa dostawcy tożsamości). Programista posiadający uprawnienie `notes:read` na poziomie bramy uzyskuje przechodni dostęp do serwera notatek MCP przy użyciu poświadczeń backendowych bramy — ale wyłącznie w granicach reguł bezpieczeństwa kontrolujących ten przepływ.

### Przypinanie skrótów narzędzi (Hash Pinning) na bramie

Brama przechowuje manifest zawierający skróty SHA256 zatwierdzonych opisów narzędzi. W fazie wykrywania (discovery) pobiera listę narzędzi (`tools/list`) z każdego backendu, porównuje wygenerowane skróty z manifestem i odfiltrowuje narzędzia, których opisy uległy zmianie bez autoryzacji. Jest to skuteczna obrona przed atakiem typu "rug pull" (faza 13 · 15) wdrażana na poziomie centralnym.

### Polityka jako kod (Policy as Code)

Zaawansowane reguły bram są wyrażane deklaratywnie za pomocą silników takich jak OPA/Rego, Kyverno czy Styra. Reguły w rodzaju „użytkownik `alice` może wywołać `github.open_pr` wyłącznie dla repozytoriów z organizacji `acme`” są wdrażane jako kod. Prostsze rozwiązania bazują na logice napisanej w języku Python. Oba podejścia są poprawne.

### Routing uwzględniający sesje (Session-Aware Routing)

Gdy sesja użytkownika wymaga interakcji z wieloma serwerami, brama dokonuje multipleksacji: pojedyncza sesja MCP po stronie programisty jest powiązana z N sesjami backendowymi (po jednej dla każdego serwera docelowego). Powiadomienia z dowolnego backendu są przekazywane przez bramę bezpośrednio do sesji użytkownika.

### Konsolidacja przestrzeni nazw

Bramy konsolidują przestrzenie nazw narzędzi pochodzących ze wszystkich backendów, stosując odpowiednie prefiksy w celu unikania kolizji (np. `github.open_pr`, `notes.search`). Zapewnia to jednoznaczność routingu.

### Rejestry

- **Oficjalny rejestr MCP (`registry.modelcontextprotocol.io`).** Prowadzony wspólnie przez Anthropic, GitHub, PulseMCP i Microsoft. Wymaga weryfikacji przestrzeni nazw (konwencja reverse-DNS, np. `io.github.user/server`) i zapewnia wstępną weryfikację jakości oprogramowania.
- **Glama.** Agregacyjny metarejestr zorientowany na szybkie wyszukiwanie rozwiązań.
- **MCPMarket.** Komercyjny katalog zawierający oferty i profile dostawców serwerów.
- **MCP.so.** Rejestr tworzony przez społeczność, dopuszczający otwarte zgłoszenia.
- **Smithery.** Platforma ułatwiająca instalację i konfigurację serwerów w stylu menedżera pakietów.
- **LobeHub.** Rejestr zintegrowany bezpośrednio z interfejsem aplikacji LobeChat.

Bramy korporacyjne domyślnie pobierają pakiety z oficjalnego rejestru, dopuszczają wybrane przez administratora pozycje z metarejestrów i blokują instalację wszelkich innych, niezatwierdzonych serwerów.

### Nazewnictwo oparte na odwróconym DNS

Oficjalny rejestr wymaga stosowania konwencji odwróconego DNS dla publicznych serwerów (np. `io.github.alice/notes`). Takie przestrzenie nazw chronią przed nieuprawnionym przejmowaniem nazw (squatting) oraz porządkują strukturę zaufania.

### Przegląd dostawców (stan na kwiecień 2026 r.)

| Dostawca | Kluczowe atuty |
|------------|---------|
| Cloudflare MCP Ports | Uruchamianie na brzegu sieci (edge); wbudowane wsparcie dla OAuth; darmowy pakiet startowy |
| Kong AI Gateway | Natywne wsparcie dla Kubernetes; zaawansowane reguły bezpieczeństwa; integracja logowania z OpenTelemetry |
| IBM ContextForge | Integracja z korporacyjnymi systemami IAM; zgodność z regulacjami; eksport logów audytowych |
| TrueFoundry | Zorientowany na DevOps; nacisk na metryki i monitorowanie (observability) |
| MintMCP | Dopasowany do platform deweloperskich |
| Envoy AI Gateway | Otwarte oprogramowanie (Open Source); w pełni konfigurowalne filtry żądań |

## Zastosowanie w praktyce

Skrypt `code/main.py` zawiera uproszczoną wersję bramy w około 150 liniach kodu. Implementuje ona: uwierzytelnianie użytkowników na podstawie tokenu typu Bearer, zarządzanie regułami RBAC dla użytkowników, przekazywanie żądań do dwóch backendowych serwerów MCP, zapisywanie wywołań w dzienniku audytu, limitowanie żądań (rate limiting) oraz blokowanie narzędzi, których skrót SHA256 opisu różni się od wartości zdefiniowanej w manifeście.

Kluczowe elementy struktury kodu:

- Słownik `RBAC` mapujący `user_id` na dozwolone pary `server::tool`.
- Lista `AUDIT_LOG` jako rejestr zdarzeń typu append-only.
- Mechanizm rate limiting bazujący na algorytmie token bucket dla każdego użytkownika.
- Słownik z manifestem przypisujący parze `server::tool` oczekiwany skrót SHA256.

## Zadanie praktyczne

Efektem tej lekcji powinno być przygotowanie pliku `outputs/skill-gateway-bootstrap.md`. Na podstawie założeń wdrożenia MCP w przedsiębiorstwie (struktura użytkowników, zaplecza oraz wymogi zgodności) należy opracować specyfikację konfiguracji bramy sieciowej.

## Ćwiczenia

1. Uruchom skrypt `code/main.py`. Wykonaj połączenie jako użytkownik posiadający odpowiednie uprawnienia, następnie jako użytkownik bez uprawnień, a na koniec wykonaj serię żądań przekraczającą dozwolony limit. Zweryfikuj zachowanie systemu we wszystkich trzech przypadkach.

2. Zaimplementuj filtr usuwający dane osobowe (PII) z odpowiedzi serwera przed odesłaniem ich do klienta. Wykorzystaj proste wyrażenie regularne wykrywające numery PESEL/SSN i przeanalizuj trudności związane z wykrywaniem innych typów danych (np. adresów e-mail czy numerów telefonów).

3. Rozbuduj dziennik audytu, tak aby generował telemetrię zgodną ze specyfikacją OpenTelemetry GenAI. Szczegółowy opis atrybutów znajdziesz w lekcji Faza 13 · 20.

4. Zaprojektuj politykę RBAC dla 50-osobowego zespołu deweloperskiego korzystającego z pięciu systemów backendowych (notatki, GitHub, Postgres, Jira, Slack). Zdefiniuj role z uprawnieniami tylko do odczytu oraz do modyfikacji danych.

5. Przeczytaj w całości artykuł firmy Cloudflare na temat Enterprise MCP. Wskaż jedną funkcję dostępną w usłudze Cloudflare, która nie została zaimplementowana w naszej uproszczonej bramie.

## Kluczowe pojęcia

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Brama | „Proxy MCP” | Centralny serwer pośredniczący (proxy) umieszczony pomiędzy klientami a wieloma serwerami backendowymi |
| Przechowywanie danych uwierzytelniających | „Tokeny zaplecza pozostają po stronie serwera” | Zasada, zgodnie z którą dane uwierzytelniające do backendów (upstream tokens) nie są ujawniane klientom programistów |
| Routing świadomy sesji | „Sesja z wieloma backendami” | Zdolność bramy do mapowania jednej sesji użytkownika na N powiązanych sesji z różnymi serwerami zaplecza |
| Przypinanie skrótu narzędzia | „Zatwierdzony manifest” | Przechowywanie skrótów SHA256 zatwierdzonych interfejsów narzędzi w celu ochrony przed nieautoryzowanymi modyfikacjami ("rug pulls") |
| RBAC | „Zasady dotyczące poszczególnych użytkowników” | Kontrola dostępu oparta na rolach (Role-Based Access Control) regulująca uprawnienia do konkretnych narzędzi i serwerów |
| Polityka jako kod | „Reguły deklaratywne” | Deklaratywne definiowanie i egzekwowanie reguł bezpieczeństwa przy użyciu języków takich jak Rego (OPA) |
| Dziennik audytu | „Kto, co, kiedy” | Nienaruszalny (append-only) rejestr zdarzeń umożliwiający weryfikację operacji pod kątem zgodności z regulacjami |
| Limit stawki | „Zbiornik tokenów na użytkownika” | Mechanizmy kontroli natężenia ruchu (np. token bucket) zapobiegające przeciążeniom infrastruktury |
| Oficjalny rejestr MCP | „Kanoniczny upstream” | Oficjalne repozytorium serwerów MCP ze zweryfikowanymi przestrzeniami nazw (registry.modelcontextprotocol.io) |
| Odwrotne nazewnictwo DNS | „Przestrzeń nazw rejestru” | Konwencja identyfikacji serwerów oparta na odwróconym DNS (np. io.github.user/server) |

## Polecana literatura / dokumentacja

- [Oficjalny rejestr MCP](https://registry.modelcontextprotocol.io/) — kanoniczny plik źródłowy, zweryfikowany pod kątem przestrzeni nazw
- [Cloudflare — Enterprise MCP](https://blog.cloudflare.com/enterprise-mcp/) — wzorzec bramy z OAuth i polityką
- [agentic-community — rejestr bramy MCP](https://github.com/agentic-community/mcp-gateway-registry) — bramka referencyjna typu open source
- [TrueFoundry — Co to jest bramka MCP?](https://www.truefoundry.com/blog/what-is-mcp-gateway) — artykuł porównujący funkcje
- [IBM — tworzenie kontekstu MCP](https://github.com/IBM/mcp-context-forge) — brama korporacyjna firmy IBM
