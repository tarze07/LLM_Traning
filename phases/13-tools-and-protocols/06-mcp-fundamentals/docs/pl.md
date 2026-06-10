# Podstawy MCP — elementy podstawowe, cykl życia, baza JSON-RPC

> Każda integracja przed MCP była jednorazowa. Model Context Protocol, dostarczony po raz pierwszy przez firmę Anthropic w listopadzie 2024 r., a obecnie zarządzany przez fundację Agentic AI Foundation przy Linux Foundation, standaryzuje wykrywanie i wywoływanie, dzięki czemu każdy klient może komunikować się z dowolnym serwerem. Specyfikacja z dnia 25.11.2025 określa sześć elementów podstawowych (trzy serwery, trzech klientów), trójfazowy cykl życia i format połączenia JSON-RPC 2.0. Naucz się ich, a reszta rozdziału MCP w tej fazie stanie się czytaniem.

**Typ:** Ucz się
**Języki:** Python (stdlib, parser JSON-RPC)
**Warunki wstępne:** Faza 13 · 01 do 05 (interfejs narzędzia i wywołanie funkcji)
**Czas:** ~45 minut

## Cele nauczania

- Nazwij wszystkie sześć prymitywów MCP (narzędzia, zasoby, podpowiedzi na serwerze; korzenie, próbkowanie, wywoływanie na kliencie) i podaj po jednym przypadku użycia.
- Przejdź przez trójfazowy cykl życia (inicjowanie, działanie, zamknięcie) i określ, kto wysyła który komunikat w każdej fazie.
- Analizuj i emituj koperty żądań, odpowiedzi i powiadomień JSON-RPC 2.0.
- Wyjaśnij, na czym polega negocjowanie możliwości w `initialize` i co bez tego się psuje.

## Problem

Przed MCP każdy agent korzystający z narzędzi miał swój własny protokół. Kursor miał system narzędzi w kształcie MCP, ale niekompatybilny. Claude Desktop został dostarczony z innym. Rozszerzenie Copilot VS Code miało trzecie. Zespół, który zbudował narzędzie „Zapytanie Postgres”, napisał to samo narzędzie trzy razy, za każdym razem w interfejsie API innego hosta. Ponowne użycie wymagało skopiowania kodu.

Rezultatem była kambryjska eksplozja jednorazowych integracji i ograniczenie prędkości ekosystemu.

MCP rozwiązuje ten problem, standaryzując format przewodu. Pojedynczy serwer MCP działa w każdym kliencie MCP: Claude Desktop, ChatGPT, Cursor, VS Code, Gemini, Goose, Zed, Windsurf, ponad 300 klientów do kwietnia 2026. 110 milionów pobrań SDK miesięcznie. Ponad 10 000 serwerów publicznych. Fundacja Linux objęła kierownictwo w grudniu 2025 r. w ramach nowej Fundacji Agentic AI.

Wersja specyfikacji zastosowana na tym etapie to **2025-11-25**. Dodaje zadania asynchroniczne (SEP-1686), wywoływanie trybu URL (SEP-1036), próbkowanie za pomocą narzędzi (SEP-1577), przyrostową zgodę na zakres (SEP-835) i semantykę wskaźnika zasobów OAuth 2.1. Faza 13 · 09 do 16 obejmuje te rozszerzenia. Ta lekcja kończy się u podstawy.

## Koncepcja

### Trzy prymitywy serwera

1. **Narzędzia.** Działania, które można wywołać. Ta sama czteroetapowa pętla z fazy 13 · 01.
2. **Zasoby.** Dane ujawnione. Treść tylko do odczytu adresowana przez URI: `file:///path`, `db://query/...`, schematy niestandardowe.
3. **Podpowiedzi.** Szablony wielokrotnego użytku. Polecenia ukośnikowe w interfejsie użytkownika hosta; serwer dostarcza szablon, klient wypełnia argumenty.

### Trzy elementy podstawowe klienta

4. **Roots.** Zbiór identyfikatorów URI, których serwer może dotykać. Klient je deklaruje; serwer ich szanuje.
5. **Próbkowanie.** Serwer żąda modelu klienta w celu wykonania uzupełnienia. Umożliwia pętle agentów hostowane na serwerze bez kluczy API po stronie serwera.
6. **Wywoływanie.** Serwer pyta użytkownika klienta o ustrukturyzowane dane wejściowe w trakcie lotu. Formularze lub adresy URL (SEP-1036).

Każda zdolność MCP należy dokładnie do jednej z tych sześciu. Faza 13 · 10 do 14 omówić szczegółowo każdy z nich.

### Format przewodu: JSON-RPC 2.0

Każda wiadomość jest obiektem JSON z następującymi polami:

- Żądania: `{jsonrpc: "2.0", id, method, params}`.
- Odpowiedzi: `{jsonrpc: "2.0", id, result | error}`.
- Powiadomienia: `{jsonrpc: "2.0", method, params}` — brak `id`, nie oczekuje się żadnej odpowiedzi.

Podstawowa specyfikacja zawiera ~15 metod pogrupowanych według metod pierwotnych. Ważne:

- `initialize` / `initialized` (uścisk dłoni)
- `tools/list`, `tools/call`
- `resources/list`, `resources/read`, `resources/subscribe`
- `prompts/list`, `prompts/get`
- `sampling/createMessage` (serwer-klient)
- `notifications/tools/list_changed`, `notifications/resources/updated`, `notifications/progress`

### Trójfazowy cykl życia

**Faza 1: inicjalizacja.**

Klient wysyła `initialize` ze swoimi `capabilities` i `clientInfo`. Serwer odpowiada własnymi `capabilities`, `serverInfo` i wersją specyfikacji, którą obsługuje. Klient wysyła `notifications/initialized` po przetworzeniu odpowiedzi. Od tego momentu każda ze stron może wysyłać żądania w ramach wynegocjowanych możliwości.

**Faza 2: operacja.**

Dwukierunkowy. Klient wywołuje `tools/list`, aby wykryć, a następnie `tools/call`, aby wywołać. Serwer może wysłać `sampling/createMessage`, jeśli zadeklarował taką możliwość. Serwer może wysłać `notifications/tools/list_changed`, gdy jego zestaw narzędzi ulegnie zmianie. Klient może wysłać `notifications/roots/list_changed`, gdy użytkownik zmieni zakres główny.

**Faza 3: wyłączenie.**

Każda ze stron zamyka transport. Brak zorganizowanej metody zamykania w MCP; transport (stdio lub Streamable HTTP, faza 13 · 09) przenosi sygnał końca połączenia.

### Negocjowanie możliwości

`capabilities` w uścisku dłoni `initialize` stanowi umowę. Przykład z serwera:

```json
{
  "tools": {"listChanged": true},
  "resources": {"subscribe": true, "listChanged": true},
  "prompts": {"listChanged": true}
}
```

Serwer deklaruje, że może emitować powiadomienia `tools/list_changed` i obsługuje `resources/subscribe`. Klient wyraża zgodę poprzez oświadczenie własne:

```json
{
  "roots": {"listChanged": true},
  "sampling": {},
  "elicitation": {}
}
```

Jeśli klient nie zadeklaruje `sampling`, serwer nie może wywołać `sampling/createMessage`. Symetryczny: jeśli serwer nie zadeklaruje `resources.subscribe`, klientowi nie wolno próbować subskrybować.

To właśnie zapobiega dryfowi ekosystemu. Klient, który nie obsługuje próbkowania, jest nadal ważnym klientem MCP; serwer, który nie wywołuje `sampling`, jest nadal prawidłowym serwerem MCP. Po prostu nie używają tej funkcji razem.

### Treść uporządkowana i kształty błędów

`tools/call` zwraca `content` tablicę wpisanych bloków: `text`, `image`, `resource`. Faza 13 · 14 dodaje do tej listy aplikacje MCP (`ui://` interaktywny interfejs użytkownika).

Błędy wykorzystują kody błędów JSON-RPC. Dodatki zdefiniowane przez specyfikację: `-32002` „Nie znaleziono zasobu”, `-32603` „Błąd wewnętrzny” oraz dane o błędach specyficznych dla MCP jako `error.data`.

### Możliwości klienta a szczegóły wywołań narzędzi

Częste zamieszanie: `capabilities.tools` dotyczy tego, czy klient obsługuje powiadomienia o zmianie listy narzędzi. To, czy klient wywoła określone narzędzia, zależy od wyboru środowiska wykonawczego na podstawie jego modelu, a nie flagi możliwości. Flaga możliwości to kontrakt na poziomie specyfikacji. Wybór modelu jest ortogonalny.

### Dlaczego JSON-RPC, a nie REST?

JSON-RPC 2.0 (2010) to lekki protokół dwukierunkowy. REST jest inicjowany przez klienta. MCP potrzebowało wiadomości inicjowanych przez serwer (próbkowanie, powiadomienia), więc JSON-RPC z symetrycznym kształtem żądania/odpowiedzi był naturalnym rozwiązaniem. JSON-RPC również komponuje się czysto na stdio i WebSocket/Streamable HTTP bez ponownego wymyślania kształtu żądania HTTP.

## Użyj tego

`code/main.py` dostarcza minimalny parser i emiter JSON-RPC 2.0, a następnie przechodzi przez `initialize` → `tools/list` → `tools/call` → `shutdown` sekwencję ręcznie, drukując każdą wiadomość. Brak prawdziwego transportu; tylko kształty wiadomości. Porównaj ze specyfikacją podaną w dalszej części czytania, aby zweryfikować każdą kopertę.

Na co zwrócić uwagę:

- `initialize` deklaruje możliwości w obie strony; odpowiedź zawiera `serverInfo` i `protocolVersion: "2025-11-25"`.
- `tools/list` zwraca tablicę `tools`; każdy wpis zawiera `name`, `description`, `inputSchema`.
- `tools/call` używa `params.name` i `params.arguments`.
- Odpowiedź `content` jest tablicą bloków `{type, text}`.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-mcp-handshake-tracer.md`. Biorąc pod uwagę transkrypcję w stylu pcap interakcji klient-serwer MCP, umiejętność opisuje każdą wiadomość, z jakim elementem podstawowym, w której fazie cyklu życia i od jakich możliwości zależy.

## Ćwiczenia

1. Uruchom `code/main.py`. Wskaż linię, w której odbywa się negocjowanie możliwości i opisz, co by się zmieniło, gdyby serwer nie zadeklarował `tools.listChanged`.

2. Rozszerz parser o obsługę `notifications/progress`. Kształt wiadomości: `{method: "notifications/progress", params: {progressToken, progress, total}}`. Wyemituj go, gdy trwa długotrwałe `tools/call` i potwierdź, że moduł obsługi klienta wyświetli pasek postępu.

3. Przeczytaj specyfikację MCP 2025-11-25 od góry do dołu — cały dokument liczy około 80 stron. Zidentyfikuj jedną flagę możliwości, której większość serwerów NIE potrzebuje. Wskazówka: dotyczy subskrypcji zasobów.

4. Naszkicuj na papierze prymityw, do którego będzie należeć hipotetyczna funkcja „zadania cron”. (Wskazówka: serwer chce, aby klient wywołał go w zaplanowanym czasie. Żaden z sześciu elementów podstawowych nie pasuje dzisiaj.) Plan działania MCP na rok 2026 zawiera wersję roboczą SEP.

5. Przeanalizuj jeden dziennik sesji z otwartego serwera MCP w GitHub. Policz żądania, odpowiedzi i powiadomienia. Oblicz, jaka część ruchu to cykl życia w stosunku do operacji.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| MCP | „Protokół kontekstu modelu” | Otwarty protokół do wykrywania i wywoływania modelu do narzędzia |
| Serwer pierwotny | „Co ujawnia serwer” | narzędzia (akcje), zasoby (dane), podpowiedzi (szablony) |
| Klient prymitywny | „Co klient pozwala serwerom używać” | pierwiastki (zakres), próbkowanie (wywołania zwrotne LLM), wywoływanie (wprowadzane przez użytkownika) |
| JSON-RPC 2.0 | „Format drutu” | Symetryczne koperty z żądaniami/odpowiedziami/powiadomieniami |
| `initialize` uścisk dłoni | „Negocjowanie możliwości” | Pierwsza para wiadomości; serwery i klienci deklarują funkcje, które obsługują |
| `tools/list` | „Odkrycie” | Klient pyta serwer o bieżący zestaw narzędzi |
| `tools/call` | „Inwokacja” | Klient prosi serwer o wykonanie narzędzia z argumentami |
| `notifications/*_changed` | „Zdarzenia mutacyjne” | Serwer informuje klienta, że ​​jego lista pierwotna uległa zmianie |
| Blok treści | „Wpisany wynik” | `{type: "text" \| "image" \| "resource" \| "ui_resource"}` w wyniku narzędzia |
| wrzesień | „Propozycja ewolucji Spec” | Nazwany projekt propozycji (np. SEP-1686 dla zadań asynchronicznych) |

## Dalsze czytanie

- [Model Context Protocol — Specyfikacja 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25) — dokument specyfikacji kanonicznej
- [Model Context Protocol — Koncepcje architektury](https://modelcontextprotocol.io/docs/concepts/architecture) — sześcioprymitywny model mentalny
– [Anthropic — wprowadzenie protokołu kontekstu modelu](https://www.anthropic.com/news/model-context-protocol) — post o uruchomieniu z listopada 2024 r.
– [Blog MCP — Pierwsza rocznica MCP](https://blog.modelcontextprotocol.io/posts/2025-11-25-first-mcp-anniversary/) — roczna retrospektywa i zmiany specyfikacji 2025-11-25
- [WorkOS — aktualizacja specyfikacji MCP 2025-11-25](https://workos.com/blog/mcp-2025-11-25-spec-update) — podsumowanie SEP-1686, 1036, 1577, 835 i 1724