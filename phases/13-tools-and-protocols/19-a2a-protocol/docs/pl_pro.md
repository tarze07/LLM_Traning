# A2A — Protokół komunikacji Agent-Agent

> MCP standaryzuje relację agent-narzędzie. Protokół A2A (Agent-to-Agent) dedykowany jest relacjom agent-agent — to otwarty standard umożliwiający współpracę "czarnoskrzynkowych" (nieprzezroczystych) agentów zbudowanych w oparciu o różne technologie i frameworki. Opracowany by Google w kwietniu 2025 r., przekazany Linux Foundation w czerwcu 2025 r., osiągnął wersję 1.0 w kwietniu 2026 r. przy wsparciu ponad 150 organizacji (m.in. AWS, Cisco, Microsoft, Salesforce, SAP i ServiceNow). Projekt wchłonął specyfikację ACP od IBM i został rozszerzony o protokół płatności agentowych AP2. W tej lekcji omawiamy koncepcję karty agenta (Agent Card), cykl życia zadania oraz dwa standardy transportu.

**Typ:** Implementacja
**Język:** Python (biblioteka standardowa, karta agenta i silnik zadań)
**Wymagania wstępne:** Faza 13 · 06 (podstawy MCP), Faza 13 · 08 (klient MCP)
**Czas:** ~75 minut

## Cele lekcji

- Zrozumienie różnic między scenariuszami agent-narzędzie (MCP) a agent-agent (A2A).
- Udostępnianie karty agenta (Agent Card) pod adresem `/.well-known/agent.json` z opisem umiejętności i punktów końcowych.
- Zarządzanie pełnym cyklem życia zadania (submitted → working → input_required → completed / failed / canceled / rejected).
- Obsługa wiadomości wieloczęściowych (zawierających tekst, pliki, ustrukturyzowane dane) oraz generowanie artefaktów jako wyników pracy.

## Problem

Wyobraźmy sobie agenta obsługi klienta, który musi zlecić sporządzenie raportu wyspecjalizowanemu agentowi analitycznemu. Metody integracji przed wprowadzeniem standardu A2A:

- **Autorskie API REST.** Działa, ale wymaga tworzenia dedykowanej integracji (ad hoc) dla każdego systemu.
- **Wspólna platforma (runtime).** Wymusza, aby oba agenty były uruchamiane w ramach tego samego frameworku.
- **Protokół MCP.** Nie rozwiązuje problemu: MCP standaryzuje wywoływanie narzędzi, a nie autonomiczną współpracę agentów przy zachowaniu prywatności ich wewnętrznych procesów myślowych.

Protokół A2A eliminuje te ograniczenia. Modeluje on współpracę jako proces delegacji zadania przez jednego agenta do drugiego, definiując cykl życia zadania, strukturę wiadomości oraz zwracane artefakty. Stan wewnętrzny realizatora pozostaje nieprzezroczysty (czarna skrzynka) — agent zlecający widzi jedynie postęp prac, stany zadania oraz finalny rezultat.

A2A to standard komunikacyjny umożliwiający współpracę agentów działających w różnych środowiskach i technologiach. Nie zastępuje on MCP – oba protokoły się uzupełniają.

## Założenia koncepcyjne

### Karta agenta (Agent Card)

Każdy agent wspierający standard A2A udostępnia dokument konfiguracyjny pod adresem `.well-known/agent.json`:

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

Wykrywanie usług (discovery) opiera się na analizie adresu URL: system pobiera kartę agenta, odczytuje punkt końcowy A2A i pobiera listę dostępnych umiejętności (skills).

### Podpisane karty agentów (AP2)

Rozszerzenie AP2 (z września 2025 r.) wprowadza podpisy kryptograficzne dla kart agentów. Wydawca podpisuje dokument przy użyciu formatu JWT, co pozwala konsumentom na weryfikację jego autentyczności i zapobiega próbom podszywania się.

### Cykl życia zadania

```
submitted -> working -> completed | failed | canceled | rejected
             -> input_required -> working (loop via message)
```

Zlecający inicjuje zadanie za pomocą metody `tasks/send`. Agent wykonujący zarządza stanami zadania, a zlecający subskrybuje powiadomienia o ich zmianie za pomocą mechanizmu SSE lub zapytań cyklicznych (polling).

### Struktura wiadomości i części (Parts)

Wiadomość in protokole A2A składa się z jednej lub wielu części (wieloczęściowość):

- `text` — treść tekstowa.
- `file` — pliki przekazywane w postaci bazy base64 wraz z określeniem ich typu MIME.
- `data` — ustrukturyzowany obiekt JSON (dane wejściowe dedykowane dla logiki agenta).

Przykładowe żądanie:

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

Wyniki działania agenta są zwracane w postaci sformalizowanych artefaktów (a nie nieustrukturyzowanego tekstu). Artefakt to nazwany obiekt posiadający określony typ:

```json
{
  "name": "summary",
  "parts": [{"type": "text", "text": "..."}],
  "mimeType": "text/markdown"
}
```

Artefakty mogą być przesyłane strumieniowo w postaci fragmentów (chunks), które są konsolidowane przez system zlecający.

### Standardy transportu

1. **JSON-RPC przez HTTP.** Domyślny protokół: punkt końcowy `/a2a`, żądania przesyłane metodą POST, opcjonalna obsługa SSE dla strumieniowania danych.
2. **gRPC.** Dedykowany dla systemów korporacyjnych, w których standardem komunikacyjnym jest gRPC.

Oba transporty zachowują identyczną strukturę danych wiadomości.

### Zasada nieprzezroczystości (Opacity / Black-box)

Fundamentalne założenie architektoniczne: stan wewnętrzny i logika realizatora zadania są nieprzezroczyste dla zlecającego. Zlecający monitoruje jedynie status zadania i odbiera finalne artefakty. Proces wnioskowania agenta, używane przez niego narzędzia czy wywołania subagentów są całkowicie ukryte. Stanowi to kluczową różnicę w stosunku do MCP, gdzie wywołania narzędzi są w pełni jawne.

Uzasadnienie biznesowe: A2A umożliwia współdziałanie systemów należących do różnych podmiotów bez ujawniania tajemnic handlowych i szczegółów technicznych wdrożenia logiki biznesowej.

### Oś czasu

- **09.04.2025.** Ogłoszenie standardu A2A przez Google.
- **23.06.2025.** Przekazanie projektu do Linux Foundation.
- **Sierpień 2025.** Integracja specyfikacji ACP od IBM.
- **Wrzesień 2025.** Wydanie rozszerzenia AP2 (płatności agentowe).
- **Kwiecień 2026.** Wydanie wersji 1.0 przy wsparciu ponad 150 organizacji.

### Porównanie: MCP a A2A

| Wymiar | MCP | A2A |
|----------|-----|-----|
| Przypadek użycia | Komunikacja Agent-Narzędzie | Komunikacja Agent-Agent |
| Nieprzezroczystość | Pełna jawność wywołań narzędzi | Ukryty proces wnioskowania (czarna skrzynka) |
| Inicjator interakcji | Środowisko uruchomieniowe agenta | Inny agent |
| Zarządzanie stanem | Wynik pojedynczego wywołania | Zadanie posiadające cykl życia |
| Autoryzacja | OAuth 2.1 (Faza 13 · 16) | Karty agenta podpisane kryptograficznie (AP2 / JWT) |
| Protokoły transportowe | Stdio / HTTP (SSE) | JSON-RPC przez HTTP / gRPC |

Wybierz MCP, jeśli potrzebujesz wywołać konkretną funkcję techniczną (narzędzie). Wybierz A2A, gdy chcesz delegować złożone, autonomiczne zadanie do innego agenta. Systemy produkcyjne często łączą oba podejścia: agent wykorzystuje MCP do zarządzania lokalnymi narzędziami, a A2A do komunikacji i współpracy z zewnętrznymi agentami.

## Zastosowanie w praktyce

Skrypt `code/main.py` wdraża uproszczony model protokołu A2A: agent badawczy publikuje swoją kartę konfiguracyjną, a agent realizujący odbiera żądanie `tasks/send` zawierające plik PDF oraz instrukcje tekstowe. Proces przechodzi przez etapy: working → input_required → working → completed, zwracając finalny artefakt tekstowy. Kod korzysta wyłącznie z biblioteki standardowej Pythona oraz komunikacji w pamięci, co ułatwia analizę struktury wiadomości.

Kluczowe elementy:

- Struktura JSON karty agenta.
- Przydzielanie identyfikatorów zadań oraz zarządzanie przejściami stanów.
- Obsługa wiadomości wieloczęściowych (mixed-type parts).
- Obsługa wstrzymania zadania w celu pozyskania dodatkowych danych (input_required).
- Generowanie i zwrot artefaktu po zakończeniu prac.

## Zadanie praktyczne

Efektem tej lekcji powinno być przygotowanie pliku `outputs/skill-a2a-agent-spec.md`. Na podstawie specyfikacji nowego agenta, który ma być udostępniony dla innych systemów agentowych, należy opracować plik JSON karty agenta, strukturę umiejętności oraz plan punktów końcowych.

## Ćwiczenia

1. Uruchom skrypt `code/main.py`. Przeanalizuj cykl życia zadania, zwracając szczególną uwagę na fazę `input_required`, w której agent wstrzymuje pracę, oczekując na dodatkowe wyjaśnienia od zlecającego.

2. Zaimplementuj mechanizm podpisowania kart agentów. Wygeneruj podpis HMAC dla kanonicznej postaci JSON karty, napisz kod weryfikujący podpis i upewnij się, że zmodyfikowany dokument zostanie odrzucony.

3. Zaimplementuj strumieniowanie wyników: agent wykonujący powinien wysyłać fragmenty artefaktu za pomocą mechanizmu SSE, a zlecający konsolidować je w gotowy dokument.

4. Zaprojektuj agenta A2A, który pełni rolę fasady dla serwera MCP. Zmapuj narzędzia MCP na umiejętności A2A i przeanalizuj wady i zalety takiego rozwiązania (zwróć uwagę na utratę szczegółowości i jawności wywołań).

5. Zapoznaj się z informacjami o wydaniu specyfikacji A2A v1.0. Wskaż jedną funkcjonalność, która na dzień kwietnia 2026 r. nie doczekała się jeszcze implementacji w popularnych frameworkach (Wskazówka: przeanalizuj zagadnienie wieloetapowej delegacji zadań - multi-hop task delegation).

## Kluczowe pojęcia

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| A2A | „Komunikacja Agent-Agent” | Otwarty protokół standaryzujący współpracę nieprzezroczystych (czarnoskrzynkowych) agentów |
| Karta agenta | „Dokument opisu agenta” | Plik konfiguracyjny `.well-known/agent.json` określający umiejętności oraz adresy punktów końcowych |
| Umiejętność (Skill) | „Funkcja wywoływalna” | Pojedyncza, zdefiniowana operacja realizowana przez agenta (odpowiednik narzędzia w MCP) |
| Zadanie (Task) | „Jednostka delegacji” | Zlecenie posiadające własny cykl życia, zwracające na koniec artefakt |
| Wiadomość (Message) | „Ładunek komunikacji” | Pakiet danych przesyłany w ramach zadania, złożony z części (parts) |
| Część (Part) | „Segment danych” | Element wiadomości o określonym typie: tekst (`text`), plik (`file`) lub dane (`data`) |
| Artefakt (Artifact) | „Wynik zadania” | Sformalizowany, nazwany obiekt wyjściowy generowany po zakończeniu zadania |
| AP2 | „Płatności agentowe” | Rozszerzenie protokołu obsługujące mechanizmy weryfikacji tożsamości oraz rozliczeń finansowych |
| Nieprzezroczystość (Opacity) | „Zasada czarnej skrzynki” | Ukrywanie szczegółów implementacji i procesu wnioskowania agenta przed systemem zlecającym |
| Brakujące dane (Input Required) | „Wstrzymanie zadania” | Stan cyklu życia zadania, w którym wykonawca oczekuje na dodatkowe informacje od zlecającego |

## Polecana literatura / dokumentacja

- [a2a-protocol.org](https://a2a-protocol.org/latest/) — kanoniczna specyfikacja A2A
- [a2aproject/A2A — GitHub](https://github.com/a2aproject/A2A) — implementacje referencyjne i SDK
- [Linux Foundation — komunikat prasowy dotyczący uruchomienia A2A](https://www.linuxfoundation.org/press/linux-foundation-launches-the-agent2agent-protocol-project-to-enable-secure-intelligent-communication-between-ai-agents) — przeniesienie zarządzania w czerwcu 2025 r.
- [Google Cloud – aktualizacja protokołu A2A](https://cloud.google.com/blog/products/ai-machine-learning/agent2agent-protocol-is-getting-an-upgrade) – plan działania i dynamika partnerów
- [Google Dev – kamień milowy A2A 1.0](https://discuss.google.dev/t/the-a2a-1-0-milestone-ensuring-and-testing-backward-compatibility/352258) – informacje o wersji 1.0 i wskazówki dotyczące zgodności wstecznej
