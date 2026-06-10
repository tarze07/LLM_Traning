---

name: mcp-server-platform
description: Wdróż produkcyjny serwer MCP ze StreamableHTTP, zakresami OAuth 2.1, polityką OPA, bramką do zatwierdzania przez człowieka narzędzi destrukcyjnych i rejestrem do wykrywania.
version: 1.0.0
phase: 19
lesson: 13
tags: [capstone, mcp, fastmcp, streamablehttp, oauth, opa, registry, governance]

---

Biorąc pod uwagę środowisko korporacyjne, należy dostarczyć serwer MCP z 10 narzędziami wewnętrznymi, usługą rejestru do wykrywania i warstwą zarządzania, która blokuje destrukcyjne narzędzia poprzez zatwierdzenie Slacka.

Plan budowy:

1. Serwer FastMCP udostępniający 10 narzędzi tylko do odczytu (Postgres, S3, Jira, Linear, Datadog, PagerDuty, GitHub, Notion, Slack, Salesforce), każde z określonym schematem i wymaganym zakresem.
2. Transport StreamableHTTP, bezstanowy za modułem równoważenia obciążenia.
3. Oprogramowanie pośredniczące do introspekcji tokena OAuth 2.1; tożsamość obciążenia poprzez SPIFFE/SPIRE.
4. Decyzje polityczne OPA/Rego dotyczące każdego wywołania narzędzia: egzekwowanie zakresu, redagowanie danych osobowych, ograniczenia rozmiaru ładunku.
5. Narzędzia destrukcyjne (tworzenie Jira, tworzenie liniowe, zapis Postgres) na oddzielnym serwerze MCP wymagającym podniesienia zakresu `approved:by:human` za pomocą karty Slack w ciągu 15 minut.
6. Usługa rejestru, która odpytuje `.well-known/mcp-capabilities` z każdego serwera, sprawdza poprawność za pomocą schematu JSON i udostępnia interfejs użytkownika z listą/wyszukiwaniem/weryfikacją/włączaniem.
7. Dziennik audytu JSONL dla poszczególnych dzierżawców z redakcją Presidio PII przed zapisem.
8. Test obciążenia 100 klientów demonstrujący skalę poziomą; przejść pakiet zgodności MCP.

Rubryka oceny:

| Waga | Kryterium | Pomiar |
|:-:|---|---|
| 25 | Zgodność ze specyfikacją | Manifest możliwości StreamableHTTP + przechodzi testy zgodności MCP |
| 20 | Bezpieczeństwo | Egzekwowanie zakresu, objęcie OPA każdym narzędziem, tajna higiena |
| 20 | Obserwowalność | Dziennik kontroli wywołań poszczególnych narzędzi z redakcją danych osobowych przy zapisie |
| 20 | Skala | Test obciążenia 100 klientów z demonstracją w skali poziomej |
| 15 | Rejestr UX | Odkryj / zatwierdź / włącz-wyłącz wykonywany przepływ pracy |

Twarde odrzucenia:

- Serwery wymagające sesji stanowych (narusza umowę bezstanową StreamableHTTP 2026).
- Topologia jednego serwera, w której narzędzia destrukcyjne mają tę samą powierzchnię uwierzytelniania, co tylko do odczytu.
- Dzienniki audytu, które przechowują surowe informacje umożliwiające identyfikację.
- Ignorowanie manifestu możliwości; integracja rejestru jest trudnym wymogiem.

Zasady odmowy:

- Odmów wdrożenia bez OAuth; dostęp anonimowy jest dyskwalifikujący.
- Odmawiaj wysyłania niszczycielskich narzędzi bez przepływu akceptacji Slack.
- Odmawiaj ujawnienia narzędzia, którego zakresu lub opisu nie ma w manifeście możliwości.

Dane wyjściowe: repozytorium zawierające dwa serwery MCP (tylko do odczytu + destrukcyjne), usługę rejestru, integrację zatwierdzenia Slacka, zasady OPA, wiązkę testów obciążenia dla 100 klientów, wyniki testów zgodności i opis opisujący, które narzędzia rozważałeś ujawnić, ale tego nie zrobiłeś (i dlaczego) oraz trzy najważniejsze reguły OPA, które wyłapały prawie chybienie podczas próby próbnej.