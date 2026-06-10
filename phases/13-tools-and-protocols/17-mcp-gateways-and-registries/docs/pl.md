# Bramy i rejestry MCP — korporacyjne płaszczyzny kontroli

> Przedsiębiorstwa nie mogą pozwolić, aby każdy programista instalował losowe serwery MCP. Brama centralizuje uwierzytelnianie, RBAC, audyt, ograniczanie szybkości, buforowanie i wykrywanie zatruć narzędzi, a następnie udostępnia połączoną powierzchnię narzędzia jako pojedynczy punkt końcowy MCP. Oficjalny rejestr MCP (Anthropic + GitHub + PulseMCP + Microsoft, zweryfikowany pod kątem przestrzeni nazw) jest kanonicznym źródłem. W tej lekcji omówiono miejsca, w których pasuje brama, omówiono minimalną implementację i przyjrzano się krajobrazowi dostawców w roku 2026.

**Typ:** Ucz się
**Języki:** Python (stdlib, minimalna bramka)
**Wymagania wstępne:** Faza 13 · 15 (zatrucie narzędzia), Faza 13 · 16 (OAuth 2.1)
**Czas:** ~45 minut

## Cele nauczania

- Wyjaśnij, gdzie znajduje się brama MCP (pomiędzy klientami MCP a wieloma serwerami MCP zaplecza).
- Wdrażaj pięć obowiązków bramy: uwierzytelnianie, RBAC, audyt, limit szybkości, zasady.
- Wymuszaj manifest skrótu przypiętego narzędzia w warstwie bramy.
- Odróżnij oficjalny rejestr MCP od metarejestrów (Glama, MCPMarket, MCP.so, Smithery, LobeHub).

## Problem

Lista Fortune 500 ma 30 zatwierdzonych serwerów MCP, 5000 programistów, wymagania dotyczące zgodności i audytu oraz zespół ds. bezpieczeństwa, który chce scentralizowanych zasad. Pozwolenie każdemu programiście na zainstalowanie dowolnych serwerów w swoich IDE nie jest dobrym pomysłem.

Wzór bramy:

1. Bramka działa jako pojedynczy punkt końcowy HTTP, z którym łączą się deweloperzy strumieniowego przesyłania danych.
2. Brama przechowuje poświadczenia dla każdego serwera MCP zaplecza.
3. Każde żądanie programisty jest uwierzytelniane i ustalane w zakresie za pośrednictwem protokołu OAuth bramy.
4. Brama kieruje połączenie do serwera zaplecza, stosując zasady.
5. Wszystkie połączenia rejestrowane w celu audytu.

Portale Cloudflare MCP, Kong AI Gateway, IBM ContextForge, MintMCP, TrueFoundry, Envoy AI Gateway — wszystkie bramy lub funkcje bram dostarczone w latach 2025–2026.

W międzyczasie uruchomiono oficjalny rejestr MCP jako kanoniczny serwer nadrzędny: wyselekcjonowane, zweryfikowane pod kątem przestrzeni nazw serwery z odwróconymi nazwami DNS, z których może pobierać brama. Metarejestry (Glama, MCPMarket, MCP.so, Smithery, LobeHub) agregują serwery z wielu źródeł.

## Koncepcja

### Pięć obowiązków bramy

1. **Auth.** OAuth 2.1 w celu identyfikacji programisty; mapuje do ról użytkowników.
2. **RBAC.** Polityka dotycząca poszczególnych użytkowników: które serwery, jakie narzędzia, jaki zakres.
3. **Audyt.** Każde połączenie rejestrowane z informacją o tym, kto, co, kiedy i wynik.
4. **Limit stawki.** Limity na użytkownika / na narzędzie / na serwer, aby zapobiec nadużyciom.
5. **Zasady.** Odrzuć zatrute opisy, egzekwuj Zasadę Dwóch, zredaguj informacje umożliwiające identyfikację.

### Brama jako pojedynczy punkt końcowy

Dla programistów brama wygląda jak jeden serwer MCP. Wewnętrznie kieruje do N backendów. Identyfikatory sesji (faza 13 · 09) są przepisywane na granicy.

### Przechowywanie danych uwierzytelniających

Programiści nigdy nie widzą tokenów backendu. Brama je przechowuje (lub serwery proxy dostawcy tożsamości, który to robi). Programista z `notes:read` na bramce może przejściowo uzyskiwać dostęp do serwera notes MCP przy użyciu własnych poświadczeń zaplecza bramy — ale tylko zgodnie z zasadami, które wiążą dostęp przechodni.

### Przypinanie skrótu narzędzia do bramy

Bramka przechowuje manifest zatwierdzonych opisów narzędzi (hasze SHA256). W momencie wykrycia pobiera `tools/list` każdego backendu, porównuje skróty z manifestem i usuwa każde narzędzie, którego opis uległ zmianie. Jest to obrona przed wyciąganiem dywanu z fazy 13 · 15, stosowana centralnie.

### Polityka jako kod

Zaawansowane zasady bramek ekspresowych w OPA/Rego, Kyverno lub Styra. Reguły takie jak „użytkownik `alice` może wywoływać `github.open_pr` tylko w repozytoriach w organizacji `acme`” są kodowane deklaratywnie. Proste bramy korzystają z ręcznie kodowanego języka Python. Obydwa kształty są prawidłowe.

### Routing uwzględniający sesję

Gdy sesja użytkownika obejmuje kombinację serwerów, brama multipleksuje: pojedyncza sesja MCP programisty zawiera N sesji zaplecza, po jednej na serwer. Powiadomienia z dowolnej ścieżki backendu przez bramę do sesji programisty.

### Łączenie przestrzeni nazw

Bramy łączą przestrzenie nazw narzędzi ze wszystkich backendów, zazwyczaj z prefiksem w przypadku kolizji. `github.open_pr`, `notes.search`. Dzięki temu routing jest jednoznaczny.

### Rejestry

- **Oficjalny rejestr MCP (`registry.modelcontextprotocol.io`).** Uruchomiony pod nadzorem Anthropic, GitHub, PulseMCP, Microsoft. Zweryfikowano przestrzeń nazw (reverse-DNS: `io.github.user/server`). Wstępnie filtrowane w celu zapewnienia podstawowej jakości.
- **Glama.** Metarejestr zorientowany na wyszukiwanie, skupiający wiele źródeł.
- **MCPMarket.** Katalog o charakterze komercyjnym z listami dostawców.
- **MCP.so.** Katalog społeczności; otwarte zgłoszenia.
- **Smithery.** Przebieg instalacji w stylu menedżera pakietów.
- **LobeHub.** Rejestr zintegrowany z interfejsem użytkownika w aplikacji LobeChat.

Bramy korporacyjne domyślnie pobierają dane z oficjalnego rejestru, zezwalają na wybrane przez administratora dodatki z metarejestrów i odrzucają wszystko, co nie jest przypięte.

### Odwrotne nazewnictwo DNS

Oficjalny rejestr wymaga odwrotnych nazw DNS dla serwerów publicznych: `io.github.alice/notes`. Przestrzenie nazw zapobiegają kucowaniu i sprawiają, że delegowanie zaufania jest jaśniejsze.

### Ankieta wśród dostawców, kwiecień 2026 r

| Sprzedawca | siła |
|------------|---------|
| Portale Cloudflare MCP | Hostowane na krawędzi; Zintegrowany protokół OAuth; darmowy poziom |
| Brama Kong AI | Natywny K8s; szczegółowa polityka; loguje się do OpenTelemetry |
| IBM ContextForge | IAM przedsiębiorstwa; zgodność; audyt eksportu |
| TrueFoundry | Oparty na DevOps; najpierw metryka |
| MintMCP | Zorientowany na platformę programistyczną |
| Brama AI wysłannika | Otwarte oprogramowanie; konfigurowalne filtry |

Faza 17 (infrastruktura produkcyjna) pozwala głębiej poznać operacje na bramkach.

## Użyj tego

`code/main.py` zawiera minimalną bramę w ~150 liniach: uwierzytelnia użytkowników za pomocą fałszywego tokena okaziciela, przechowuje zasady RBAC dla poszczególnych użytkowników, kieruje żądania do dwóch serwerów MCP zaplecza, zapisuje każde wywołanie w dzienniku audytu, wymusza limit szybkości i odrzuca każde narzędzie zaplecza, którego skrót opisu nie pasuje do przypiętego manifestu.

Na co zwrócić uwagę:

- `RBAC` dykt kluczowany przez `user_id` z dozwolonymi wpisami `server_tool`.
- `AUDIT_LOG` to lista wydarzeń przeznaczona wyłącznie do dodawania.
- Limit szybkości wykorzystuje wiadro tokenów na użytkownika.
- Przypięty manifest jest dyktatem `server::tool -> hash`.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-gateway-bootstrap.md`. Biorąc pod uwagę plan MCP przedsiębiorstwa (użytkownicy, zaplecze, zgodność), umiejętność tworzy specyfikację konfiguracji bramy.

## Ćwiczenia

1. Uruchom `code/main.py`. Wykonaj połączenie jako uprawniony użytkownik; następnie jako niedozwolony użytkownik; następnie seria z przekroczeniem limitu szybkości. Sprawdź wszystkie trzy przepływy.

2. Dodaj zasadę, która usuwa dane osobowe z wyników przed przesłaniem ich do klienta. Użyj prostego wyrażenia regularnego dla ciągów w kształcie SSN; zanotuj lukę (e-maile, numery telefonów).

3. Rozszerz dziennik audytu, aby emitować zakresy OpenTelemetry GenAI. Faza 13 · 20 obejmuje dokładne atrybuty.

4. Zaprojektuj politykę RBAC dla 50-osobowego zespołu programistów z pięcioma backendami (notes, github, postgres, jira, slack). Kto na każdym z nich otrzymuje uprawnienia tylko do odczytu? Kto pisze?

5. Przeczytaj post dotyczący MCP dla przedsiębiorstw Cloudflare od góry do dołu. Zidentyfikuj jedną funkcję Cloudflare, której nie ma ta brama stdlib.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Brama | „Proxy MCP” | Centralizacja serwera pomiędzy klientami i backendami |
| Przechowywanie danych uwierzytelniających | „Tokeny zaplecza pozostają po stronie serwera” | Programiści nigdy nie widzą tokenów nadrzędnych |
| Routing świadomy sesji | „Sesja z wieloma backendami” | Brama multipleksuje N sesji backendu na sesję programisty |
| Przypinanie skrótu narzędzia | „Zatwierdzony manifest” | SHA256 każdego zatwierdzonego opisu narzędzia; blokuje dywaniki centralnie |
| RBAC | „Zasady dotyczące poszczególnych użytkowników” | Kontrola dostępu oparta na rolach do narzędzi i serwerów |
| Polityka jako kod | „Reguły deklaratywne” | Zasady OPA/Rego, Kyverno, Styra egzekwowane na bramce |
| Dziennik audytu | „Kto, co, kiedy” | Dziennik zdarzeń z możliwością dołączenia w celu zapewnienia zgodności |
| Limit stawki | „Zbiornik tokenów na użytkownika” | Limity minutowe, aby zapobiec nadużyciom |
| Oficjalny rejestr MCP | „Kanoniczny upstream” | `registry.modelcontextprotocol.io`, zweryfikowane w przestrzeni nazw |
| Odwrotne nazewnictwo DNS | „Przestrzeń nazw rejestru” | `io.github.user/server` konwencja |

## Dalsze czytanie

- [Oficjalny rejestr MCP](https://registry.modelcontextprotocol.io/) — kanoniczny plik źródłowy, zweryfikowany pod kątem przestrzeni nazw
- [Cloudflare — Enterprise MCP](https://blog.cloudflare.com/enterprise-mcp/) — wzorzec bramy z OAuth i polityką
- [agentic-community — rejestr bramy MCP](https://github.com/agentic-community/mcp-gateway-registry) — bramka referencyjna typu open source
- [TrueFoundry — Co to jest bramka MCP?](https://www.truefoundry.com/blog/what-is-mcp-gateway) — artykuł porównujący funkcje
- [IBM — tworzenie kontekstu MCP](https://github.com/IBM/mcp-context-forge) — brama korporacyjna firmy IBM