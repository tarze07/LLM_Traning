# Capstone 13 — serwer MCP z rejestracją i zarządzaniem

> Model Context Protocol przestał być przyszłością i stał się domyślną specyfikacją użycia narzędzi w 2026 roku. Anthropic, OpenAI, Google i wszyscy główni IDE dostarczają klientów MCP. Pinterest opublikował swój wewnętrzny ekosystem serwerów MCP. Metadane dotyczące możliwości sformalizowane przez rejestr AAIF znajdują się pod adresem `.well-known`. AWS ECS opublikował referencyjne wdrożenie bezstanowe. Gęsi agent Blocka umieścił ten sam protokół w hostowanym asystencie. Wersja produkcyjna na rok 2026 to: transport StreamableHTTP, zakresy OAuth 2.1, bramkowanie zasad OPA i rejestr, który umożliwia zespołom ds. platform wykrywanie, sprawdzanie poprawności i włączanie serwerów. Zbuduj ten koniec do końca.

**Typ:** Zwieńczenie
**Języki:** Python (serwer, przez FastMCP) lub TypeScript (@modelcontextprotocol/sdk), Go (usługa rejestru)
**Wymagania wstępne:** Faza 11 (inżynieria LLM), Faza 13 (narzędzia i MCP), Faza 14 (agenci), Faza 17 (infrastruktura), Faza 18 (bezpieczeństwo)
**Wykonywane fazy:** P11 · P13 · P14 · P17 · P18
**Czas:** 25 godzin

## Problem

MCP stało się lingua franca używanym w użyciu narzędzi. Claude Code, Cursor 3, Amp, OpenCode, Gemini CLI i każdy zarządzany agent korzystają teraz z serwerów MCP. Wyzwaniami produkcyjnymi nie są serwery autorskie (FastMCP to ułatwia), ale wdrażanie ich na skalę zgodną z wymaganiami przedsiębiorstwa: zakresy OAuth dla poszczególnych dzierżawców, zasady OPA dotyczące narzędzi destrukcyjnych, skalowanie bezstanowe StreamableHTTP, rejestr do wykrywania, dzienniki audytu dla wywołań narzędzi. Wewnętrzny ekosystem MCP Pinteresta i specyfikacja rejestru AAIF wyznaczają poprzeczkę na rok 2026.

Zbudujesz serwer MCP udostępniający 10 wewnętrznych narzędzi (Postgres tylko do odczytu, lista S3, Jira, Linear, Datadog itp.), interfejs rejestru do wykrywania platform oraz bramkę zatwierdzania przez człowieka dla narzędzi destrukcyjnych. Test obciążenia demonstruje skalowanie poziome StreamableHTTP. Ścieżka audytu spełnia wymagania przeglądu bezpieczeństwa przedsiębiorstwa.

## Koncepcja

Wersja MCP 2026 wymaga StreamableHTTP jako domyślnego transportu. W przeciwieństwie do wcześniejszego kształtu stdio-i-SSE, StreamableHTTP jest domyślnie bezstanowy: pojedynczy punkt końcowy HTTP akceptuje żądania JSON-RPC, przesyła strumieniowo odpowiedzi i obsługuje długotrwałe połączenia dla powiadomień. Bezstanowy oznacza skalowalny poziomo za modułem równoważenia obciążenia.

Autoryzacja to OAuth 2.1 z zakresami dla poszczególnych narzędzi. Token zawiera zakresy takie jak `jira:read`, `s3:list`, `postgres:query:readonly`. Serwer MCP sprawdza zakresy w momencie wywołania narzędzia, a nie tylko na początku sesji. W przypadku narzędzi wysokiego ryzyka serwer odrzuca każde wywołanie, którego zakres nie został podniesiony do `approved:by:human` w ciągu ostatnich N minut — podniesienie poziomu pochodzi z karty recenzji Slacka.

Rejestr jest odrębną usługą. Każdy serwer MCP udostępnia dokument `.well-known/mcp-capabilities` z manifestem narzędzia, adresem URL transportu i wymaganiami dotyczącymi uwierzytelniania. Rejestr odpytuje, sprawdza poprawność i indeksuje. Zespoły platformy korzystają z interfejsu użytkownika rejestru, aby sprawdzić, jakie narzędzia są dostępne, jakich zakresów potrzebują i które zespoły są ich właścicielami.

## Architektura

```
MCP client (Claude Code, Cursor 3, ...)
          |
          v
StreamableHTTP over HTTPS (JSON-RPC + streaming)
          |
          v
MCP server (FastMCP) behind load balancer
          |
   +------+------+---------+----------+------------+
   v             v         v          v            v
Postgres    S3 listing  Jira       Linear     Datadog
(read-only) (paged)     (read)     (read)     (query)
          |
   +------+-------------+
   v                    v
 OPA policy gate   destructive tool MCP (separate server)
                        |
                        v
                   human approval via Slack
                        |
                        v
                   audit log (append-only, per-tenant)

  registry service
     |
     v  GET /.well-known/mcp-capabilities from each server
     v
     UI: search / validate / enable-disable / ownership
```

## Stos

- Struktura serwera: FastMCP (Python) lub `@modelcontextprotocol/sdk` (TypeScript)
- Transport: StreamableHTTP przez HTTPS (bezstanowy)
- Auth: OAuth 2.1 z tożsamością obciążenia poprzez SPIFFE/SPIRE
- Polityka: zasady OPA / Rego dla każdego narzędzia; usługa podejmowania decyzji politycznych na żądanie
- Rejestr: hostowany samodzielnie, wykorzystuje manifesty `.well-known/mcp-capabilities`
- Zatwierdzenie przez człowieka: interaktywna wiadomość Slack dotycząca destrukcyjnych narzędzi
- Wdrożenie: AWS ECS Fargate lub Fly.io, jeden serwer na dzierżawcę lub współdzielony z dzierżawcą
- Audyt: ustrukturyzowany zbiór JSONL na dzierżawcę z pochodzeniem na połączenie

## Zbuduj to

1. **Powierzchnia narzędzia.** Udostępnij 10 wewnętrznych narzędzi: zapytanie Postgres tylko do odczytu, obiekty listy S3, wyszukiwanie/pobieranie Jira, wyszukiwanie/pobieranie liniowe, zapytanie o metrykę Datadog, wyszukiwanie na żądanie PagerDuty, tylko do odczytu GitHub, wyszukiwanie Notion, wyszukiwanie w Slack, odczyt Salesforce. Każde narzędzie ma przypisany schemat i etykietę zakresu.

2. **Serwer FastMCP.** Zamontuj narzędzia. Skonfiguruj transport StreamableHTTP. Dodaj oprogramowanie pośredniczące do introspekcji tokenu OAuth i egzekwowania zakresu.

3. **Zasady OPA.** Zasady Rego dla poszczególnych narzędzi: jakie zakresy pozwalają na wywoływanie, jakie stosuje się redagowanie danych osobowych, jakie obowiązują ograniczenia rozmiaru ładunku. Usługa decyzyjna wywoływana przy każdym wywołaniu narzędzia.

4. **Usługa rejestru.** Oddzielna usługa Go lub TS, która odpytuje `.well-known/mcp-capabilities` z zarejestrowanych serwerów, sprawdza poprawność za pomocą schematu JSON i udostępnia interfejs użytkownika z listą/wyszukiwaniem/weryfikacją/włączanie-wyłączanie.

5. **Manifest możliwości.** Każdy serwer udostępnia `.well-known/mcp-capabilities` z: listą narzędzi, wymaganiami dotyczącymi uwierzytelniania, adresem URL transportu, zespołem właścicieli, SLO.

6. **Destrukcyjna separacja narzędzi.** Narzędzia zmieniające stan (tworzenie Jira, tworzenie liniowe, zapis Postgres) znajdują się na drugim serwerze MCP z bardziej rygorystycznym przepływem uwierzytelniania: tokeny muszą mieć zakres `approved:by:human` podniesiony za pomocą karty Slack w ciągu 15 minut.

7. **Dziennik audytu.** JSONL z możliwością dołączenia na każdego dzierżawcę: `{timestamp, user, tool, args_redacted, response_redacted, outcome}`. Redakcja PII poprzez Presidio przed zapisem.

8. **Test obciążenia.** 100 jednoczesnych klientów na StreamableHTTP. Zademonstruj skalowanie poziome, dodając drugą replikę; pokaż redystrybucję modułu równoważenia obciążenia bez sztywności sesji.

9. **Testy zgodności.** Uruchom oficjalny pakiet zgodności MCP na obu serwerach. Zalicz wszystkie obowiązkowe sekcje.

## Użyj tego

```
$ curl -H "Authorization: Bearer eyJhbGc..." \
       -X POST https://mcp.internal.example.com/ \
       -d '{"jsonrpc":"2.0","method":"tools/call",
            "params":{"name":"postgres.readonly","arguments":{"sql":"SELECT 1"}}}'
[registry]   capability validated: postgres.readonly v1.2
[policy]    scope postgres:query:readonly present; allowed
[audit]     logged: user=u42 tool=postgres.readonly outcome=ok
response:    { "result": { "rows": [[1]] } }
```

## Wyślij to

`outputs/skill-mcp-server.md` opisuje element dostarczany. Serwer MCP klasy produkcyjnej + rejestr + warstwa audytu dla narzędzi wewnętrznych z zakresami OAuth 2.1 i bramkowaniem OPA.

| Waga | Kryterium | Jak to się mierzy |
|:-:|---|---|
| 25 | Zgodność ze specyfikacją | Manifest możliwości StreamableHTTP + przechodzi testy zgodności MCP |
| 20 | Bezpieczeństwo | Egzekwowanie zakresu, objęcie OPA każdym narzędziem, tajna higiena |
| 20 | Obserwowalność | Dziennik kontroli wywołań poszczególnych narzędzi z redakcją informacji umożliwiających identyfikację |
| 20 | Skala | Test obciążenia 100 klientów, demonstracja w skali poziomej |
| 15 | Rejestr UX | Odkryj / zweryfikuj / włącz-wyłącz przepływ pracy |
| **100** | | |

## Ćwiczenia

1. Dodaj nowe narzędzie (wyszukiwanie Confluence). Wyślij go przez proces sprawdzania rejestru bez dotykania głównego serwera.

2. Napisz politykę OPA, która redaguje wyniki zapytań Postgres zawierających kolumny o nazwach `email`, `ssn` lub `phone`. Ćwicz z zapytaniem sondującym.

3. Test porównawczy StreamableHTTP vs stdio pod kątem lokalnego opóźnienia. Raportuj każde połączenie p50/s95.

4. Wprowadź limit na dzierżawcę: maksymalnie N połączeń na minutę na narzędzie na dzierżawcę. Wyegzekwuj za pomocą drugiej reguły OPA.

5. Uruchom pakiet zgodności MCP z [mcp-conformance-tests](https://github.com/modelcontextprotocol/conformance) i napraw każdą awarię.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| StreamableHTTP | „Transport MCP 2026” | Bezstanowy HTTP + przesyłanie strumieniowe; zastępuje SSE + stdio dla serwerów sieciowych |
| Manifest zdolności | „Dobrze znany doktor” | `.well-known/mcp-capabilities` z listą narzędzi, autoryzacją, adresem URL transportu |
| OPA / Rego | „Silnik polityki” | Open Policy Agent do autoryzacji wywołań narzędzi zgodnie z regułami zewnętrznymi |
| Wysokość zakresu | „Zatwierdzone przez człowieka” | Krótkoterminowy zakres przyznany poprzez zatwierdzenie Slacka, wymagany w przypadku narzędzi niszczących |
| Rejestr | „Odkrycie narzędzia” | Usługa indeksująca serwery MCP na podstawie manifestów ich możliwości |
| Tożsamość obciążenia | „SPIFFE/IŚLEŃ” | Tożsamość usługi kryptograficznej na potrzeby wydawania tokenu OAuth |
| Pakiet zgodności | „Testy spec” | Oficjalna bateria testowa MCP dla StreamableHTTP + manifest poprawności narzędzia |

## Dalsze czytanie

– [Plan działania dotyczący protokołu Model Context Protocol na 2026 r.](https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/) — StreamableHTTP, metadane możliwości, rejestr
– [Specyfikacja rejestru AAIF MCP](https://github.com/modelcontextprotocol/registry) — specyfikacja rejestru na rok 2026
- [Wdrożenie referencyjne AWS ECS](https://aws.amazon.com/blogs/containers/deploying-model-context-protocol-mcp-servers-on-amazon-ecs/) — referencyjne wdrożenie produkcyjne
- [Wewnętrzny ekosystem MCP Pinteresta](https://www.infoq.com/news/2026/04/pinterest-mcp-ecosystem/) — referencyjne wdrożenie wewnętrzne
- [Blokuj `goose` użycie MCP](https://block.github.io/goose/) — wzorzec zużycia agenta referencyjnego
- [FastMCP](https://github.com/jlowin/fastmcp) — Framework serwerowy Python
- [Open Policy Agent](https://www.openpolicyagent.org/) — informacje o silniku zasad
- [SPIFFE / SPIRE](https://spiffe.io) — odniesienie do tożsamości obciążenia