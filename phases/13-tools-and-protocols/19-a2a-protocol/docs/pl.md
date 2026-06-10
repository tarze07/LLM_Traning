# A2A — Protokół agent-agent

> MCP to agent-narzędzie. A2A (Agent2Agent) to agent-agent — otwarty protokół umożliwiający współpracę nieprzejrzystych agentów zbudowanych na różnych platformach. Wydany przez Google w kwietniu 2025 r., przekazany fundacji Linux Foundation w czerwcu 2025 r., osiągający wersję 1.0 w kwietniu 2026 r. z ponad 150 zwolennikami, w tym AWS, Cisco, Microsoft, Salesforce, SAP i ServiceNow. Wchłonął ACP IBM i dodał rozszerzenie płatności AP2. W tej lekcji omówiono kartę agenta, cykl życia zadania i dwa powiązania transportowe.

**Typ:** Kompilacja
**Języki:** Python (stdlib, karta agenta + uprząż zadań)
**Wymagania wstępne:** Faza 13 · 06 (podstawy MCP), Faza 13 · 08 (klient MCP)
**Czas:** ~75 minut

## Cele nauczania

- Rozróżnij przypadki użycia agent-narzędzie (MCP) od agenta-agent (A2A).
- Opublikuj kartę agenta pod adresem `/.well-known/agent.json` zawierającą umiejętności i metadane punktu końcowego.
- Przejdź przez cykl życia zadania (przesłane → działające → wymagane dane → zakończone / zakończone niepowodzeniem / anulowane / odrzucone).
- Używaj wiadomości z częściami (tekstem, plikiem, danymi) i artefaktami jako danymi wyjściowymi.

## Problem

Agent obsługi klienta musi zlecić pisanie raportów wyspecjalizowanemu agentowi piszącemu. Opcje przed A2A:

- Niestandardowe API REST. Działa, ale każde połączenie jest jednorazowe.
- Wspólna baza kodu. Wymaga, aby dwaj agenci uruchamiali tę samą platformę.
- MCP. Nie pasuje: MCP służy do wywoływania narzędzi, a nie do współpracy dwóch agentów przy jednoczesnym zachowaniu nieprzejrzystego wewnętrznego rozumowania każdego agenta.

A2A wypełnia tę lukę. Modeluje interakcję jako jeden agent wysyłający zadanie do drugiego, z cyklem życia, komunikatami i artefaktami. Stan wewnętrzny wywoływanego agenta pozostaje nieprzejrzysty — osoba wywołująca widzi tylko zmiany stanu zadania i ewentualne wyniki.

A2A to protokół „pozwól agentom w różnych frameworkach rozmawiać ze sobą”. Nie zastępuje MCP; oba się uzupełniają.

## Koncepcja

### Karta agenta

Każdy agent zgodny z A2A publikuje kartę pod adresem `/.well-known/agent.json`:

```json
{
  "schemaVersion": "1.0",
  "name": "research-agent",
  "description": "Summarizes academic papers and drafts citations.",
  "url": "https://research.example.com/a2a",
  "version": "1.2.0",
  "skills": [
    {
      "id": "summarize_paper",
      "name": "Summarize a paper",
      "description": "Read a paper PDF and produce a 3-paragraph summary.",
      "inputModes": ["text", "file"],
      "outputModes": ["text", "artifact"]
    }
  ],
  "capabilities": {"streaming": true, "pushNotifications": true}
}
```

Wykrywanie opiera się na adresie URL: pobierz kartę, poznaj adres URL punktu końcowego A2A, wylicz umiejętności.

### Podpisane karty agentów (AP2)

Rozszerzenie AP2 (wrzesień 2025) dodaje podpisy kryptograficzne do kart agentów. Wydawca podpisuje własną kartę za pomocą JWT; konsumenci weryfikują. Zapobiega podszywaniu się.

### Cykl życia zadania

```
submitted -> working -> completed | failed | canceled | rejected
             -> input_required -> working (loop via message)
```

Klienci inicjują za pomocą `tasks/send`. Wywoływany agent przechodzi przez stany; klienci subskrybują aktualizacje stanu za pośrednictwem SSE lub ankiety.

### Wiadomości i części

Wiadomość zawiera jedną lub więcej części:

- `text` — zwykła treść.
- `file` — obiekt typu blob base64 z typem MIME.
- `data` — wpisany ładunek JSON (ustrukturyzowane dane wejściowe dla wywoływanego agenta).

Przykład:

```json
{
  "role": "user",
  "parts": [
    {"type": "text", "text": "Summarize this paper."},
    {"type": "file", "file": {"name": "paper.pdf", "mimeType": "application/pdf", "bytes": "..."}},
    {"type": "data", "data": {"targetLength": "3 paragraphs"}}
  ]
}
```

### Artefakty

Dane wyjściowe to artefakty, a nie surowe ciągi znaków. Artefakt to nazwane, wpisane wyjście:

```json
{
  "name": "summary",
  "parts": [{"type": "text", "text": "..."}],
  "mimeType": "text/markdown"
}
```

Artefakty można przesyłać strumieniowo w postaci fragmentów. Osoba dzwoniąca gromadzi się.

### Dwa wiązania transportowe

1. **JSON-RPC przez HTTP.** `/a2a` punkt końcowy, POST dla żądań, opcjonalnie SSE dla przesyłania strumieniowego. Domyślne wiązanie.
2. **gRPC.** Dla środowisk korporacyjnych, w których natywna jest gRPC.

Obydwa powiązania niosą ten sam logiczny kształt komunikatu.

### Zachowanie krycia

Kluczowa zasada projektowania: stan wewnętrzny wywoływanego agenta jest nieprzezroczysty. Osoba wywołująca widzi stan zadania i artefakty. Tok myślenia wywoływanego agenta, wywołania jego narzędzi, delegowanie podagenta – wszystko to jest niewidoczne. Różni się to od MCP, gdzie wywołania narzędzi są przezroczyste.

Uzasadnienie: A2A umożliwia konkurentom współpracę bez ujawniania wewnętrznych elementów. A2A może oznaczać „zadzwoń do tego agenta obsługi klienta” bez konieczności dowiedzenia się przez osobę dzwoniącą, w jaki sposób ten agent wdraża usługę.

### Oś czasu

- **2025-04-09.** Google ogłasza A2A.
- **2025-06-23.** Darowizna na rzecz Linux Foundation.
- **2025-08.** Absorbuje ACP IBM.
- **2025-09.** Statki z rozszerzeniem AP2 (płatności dla agentów).
- **2026-04.** wersja 1.0 wydana przez ponad 150 organizacji wspierających.

### Związek z MCP

| Wymiar | MCP | A2A |
|----------|-----|-----|
| Przypadek użycia | Agent-narzędzie | Agent do agenta |
| Nieprzezroczystość | Przejrzyste wywołania narzędzi | Nieprzejrzyste wewnętrzne rozumowanie |
| Typowy rozmówca | Środowisko wykonawcze agenta | Inny agent |
| stan | Wynik wywołania narzędzia | Zadanie z cyklem życia |
| Autoryzacja | OAuth 2.1 (faza 13 · 16) | Karty agenta podpisane przez JWT (AP2) |
| Transport | Stdio / Streamowalny HTTP | JSON-RPC przez HTTP/gRPC |

Użyj MCP, jeśli chcesz wywołać określone narzędzie. Użyj A2A, jeśli chcesz delegować całe zadanie innemu agentowi. Wiele systemów produkcyjnych korzysta z obu rozwiązań: agent używa MCP jako warstwy narzędzi i A2A jako warstwy współpracy.

## Użyj tego

`code/main.py` wdraża minimalną uprząż A2A: agent badawczy publikuje swoją kartę, agent piszący otrzymuje `tasks/send` z częściami zawierającymi plik PDF i instrukcję tekstową, przechodzi przez tryb roboczy → input_required → działa → ukończony i zwraca artefakt tekstowy. Wszystkie stdlib; wykorzystuje transport w pamięci, aby skupić się na kształtach wiadomości.

Na co zwrócić uwagę:

- Kształt karty agenta JSON.
- Przydzielanie identyfikatorów zadań i zmiany stanów.
- Wiadomości z częściami typu mieszanego.
— Oddział wymagający danych wejściowych w trakcie zadania.
- Zwrot artefaktu po ukończeniu.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-a2a-agent-spec.md`. Biorąc pod uwagę nowego agenta, który powinien być wywoływany przez innych agentów, umiejętność generuje kod JSON karty agenta, schemat umiejętności i plan punktu końcowego.

## Ćwiczenia

1. Uruchom `code/main.py`. Śledź pełny cykl życia zadania, łącznie z pauzą wymaganą do wprowadzenia danych, podczas której wywoływany agent prosi o wyjaśnienia.

2. Dodaj podpisaną Kartę Agenta. Podpisz w HMAC za pomocą kanonicznego JSON karty. Napisz weryfikator i potwierdź jego niepowodzenie na zmutowanej karcie.

3. Zaimplementuj strumieniowanie zadań: agent piszący emituje trzy przyrostowe fragmenty artefaktów za pośrednictwem SSE, a osoba wywołująca gromadzi je.

4. Zaprojektuj agenta A2A, który otacza serwer MCP. Przypisz każde narzędzie MCP do umiejętności A2A. Zwróć uwagę na kompromisy — jakie krycie zostaje utracone?

5. Przeczytaj ogłoszenie A2A v1.0 i znajdź jedną funkcję, która nie jest jeszcze zaimplementowana w żadnym frameworku od kwietnia 2026 r. (Wskazówka: dotyczy delegowania zadań typu multi-hop).

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| A2A | „Protokół agent-agent” | Otwarty protokół nieprzejrzystej współpracy agentów |
| Karta agenta | "`.well-known/agent.json`” | Opublikowane metadane opisujące umiejętności agenta i punkt końcowy |
| Umiejętność | „Jednostka wywoływalna” | Nazwana operacja obsługiwana przez agenta (narzędzie analogowe do MCP) |
| Zadanie | „Jednostka delegacji” | Element pracy z cyklem życia i końcowym artefaktem |
| Wiadomość | „Wprowadzenie zadania” | Przenosi części (tekst, plik, dane) |
| Część | „Wpisany fragment” | `text` / `file` / `data` element wiadomości |
| Artefakt | „Wyjście zadania” | Nazwane, wpisane dane wyjściowe zwracane po zakończeniu |
| AP2 | „Protokół płatności agenta” | Rozszerzenie podpisanych kart agentów dla zaufania i płatności |
| Nieprzezroczystość | „Współpraca czarnej skrzynki” | Dane wewnętrzne wywoływanego agenta są ukryte przed rozmówcą |
| Wymagane dane wejściowe | „Przerwa w zadaniu” | Stan cyklu życia, w którym agent potrzebuje więcej informacji |

## Dalsze czytanie

- [a2a-protocol.org](https://a2a-protocol.org/latest/) — kanoniczna specyfikacja A2A
- [a2aproject/A2A — GitHub](https://github.com/a2aproject/A2A) — implementacje referencyjne i SDK
– [Linux Foundation — komunikat prasowy dotyczący uruchomienia A2A](https://www.linuxfoundation.org/press/linux-foundation-launches-the-agent2agent-protocol-project-to-enable-secure-intelligent-komunikacja-between-ai-agents) — przeniesienie zarządzania w czerwcu 2025 r.
– [Google Cloud – aktualizacja protokołu A2A](https://cloud.google.com/blog/products/ai-machine-learning/agent2agent-protocol-is-getting-an-upgrade) – plan działania i dynamika partnerów
– [Google Dev – kamień milowy A2A 1.0](https://discuss.google.dev/t/the-a2a-1-0-milestone-ensuring-and-testing-backward-compatibility/352258) – informacje o wersji 1.0 i wskazówki dotyczące zgodności wstecznej