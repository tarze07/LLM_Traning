# A2A — Protokół agent-agent

> Google ogłosiło protokół A2A w kwietniu 2025 r. Do kwietnia 2026 r. specyfikacja została opublikowana pod adresem https://a2a-protocol.org/latest/specification/ i zyskała poparcie ponad 150 organizacji. A2A stanowi horyzontalne uzupełnienie protokołu MCP (Lekcja 13): podczas gdy MCP działa w pionie (agent ↔ narzędzia), A2A definiuje komunikację równorzędną peer-to-peer (agent ↔ agent). Określa standard dla kart agentów (odkrywanie usług), zadań generujących zróżnicowane artefakty (tekst, dane strukturalne, wideo), abstrakcyjnego cyklu życia zadań oraz uwierzytelniania. Systemy produkcyjne coraz częściej łączą MCP z A2A. W latach 2025–2026 Google Cloud zintegrowało obsługę A2A w ramach usługi Vertex AI Agent Builder.

**Typ:** Ucz się + Buduj
**Języki:** Python (biblioteka standardowa: `http.server`, `json`)
**Wymagania wstępne:** Faza 16 · 04 (model prymitywny)
**Czas:** ~75 minut

## Problem

Twój agent musi wywołać innego agenta działającego w zewnętrznym systemie. Jak to zrobić? Możesz wystawić punkt końcowy HTTP, zdefiniować własny schemat JSON i liczyć na to, że druga strona poprawnie zinterpretuje zapytanie. W efekcie każda para agentów wymaga dedykowanej integracji.

A2A to uniwersalny protokół komunikacyjny (wire protocol) rozwiązujący ten problem. Zapewnia on ujednolicone odkrywanie usług, standardowy model zadań, transport oraz zdefiniowane typy artefaktów. Działa podobnie jak HTTP+REST, ale traktuje agentów jako podmioty pierwszej klasy (first-class citizens).

## Koncepcja

### Cztery główne elementy

**Karta agenta (Agent Card).** Dokument JSON dostępny pod adresem `/.well-known/agent.json`, który opisuje agenta: jego nazwę, kompetencje, punkty końcowe (endpoints), obsługiwane formaty danych (modalities) oraz wymagania dotyczące uwierzytelniania. Proces odkrywania polega na pobraniu tej karty.

```json
GET https://agent.example.com/.well-known/agent.json
→ {
    "name": "code-review-agent",
    "skills": ["review-python", "review-typescript"],
    "endpoints": {
      "tasks": "https://agent.example.com/tasks"
    },
    "auth": {"type": "bearer"},
    "modalities": ["text", "structured"]
  }
```

**Zadanie (Task).** Jednostka pracy. Asynchroniczny obiekt stanowy z określonym cyklem życia: `submitted → working → completed / failed / canceled`. Klient może zlecić zadanie, odpytywać o jego status (polling) lub subskrybować aktualizacje.

**Artefakt (Artifact).** Typ wyniku wygenerowanego w ramach zadania (np. tekst, strukturyzowany JSON, obraz, wideo, dźwięk). Artefakty mają ściśle zdefiniowane typy, dzięki czemu obsługa różnych multimediów jest wbudowana w protokół.

**Abstrakcyjny (nieprzezroczysty) cykl życia.** A2A nie narzuca sposobu, w jaki zdalny agent realizuje zadanie. Klient widzi jedynie zmiany stanów oraz końcowe artefakty; implementacja wewnętrzna jest dowolna i może korzystać z dowolnego frameworka.

### Podział ról: MCP a A2A

- **MCP** (Lekcja 13): relacja agent ↔ narzędzie. Agent komunikuje się z serwerem narzędzi przy użyciu protokołu JSON-RPC. Domyślnie bezstanowy.
- **A2A**: relacja agent ↔ agent. Protokół typu peer-to-peer; obie komunikujące się strony to autonomiczne agenty zdolne do podejmowania decyzji.

Produkcyjne systemy wieloagentowe łączą oba podejścia. Agent komunikujący się przez A2A może lokalnie wywoływać narzędzia udostępniane przez MCP. Taki podział ról ułatwia rozdzielenie odpowiedzialności (separation of concerns).

### Przepływ komunikacji

```
Klient                     Serwer agenta
  ├──GET /.well-known/agent.json──>
  <──Agent Card JSON─────────────
  ├──POST /tasks {skill, input}──>
  <──201 task_id, state=submitted
  ├──GET /tasks/{id}──────────────>
  <──state=working, 42% done──────
  ├──GET /tasks/{id}──────────────>
  <──state=completed, artifacts──
```

Alternatywnie, w przypadku przesyłu strumieniowego (streaming): subskrypcja zdarzeń SSE pod adresem `/tasks/{id}/events` umożliwia otrzymywanie powiadomień push.

### Uwierzytelnianie i autoryzacja

A2A obsługuje trzy typowe wzorce:

- **Token okaziciela (Bearer token)** — OAuth2 lub tokeny nieprzezroczyste (opaque).
- **mTLS (mutual TLS)** — wzajemne uwierzytelnianie TLS; obie strony potwierdzają swoją tożsamość za pomocą certyfikatów.
- **Podpisywanie żądań** — sygnatura HMAC wyliczana z zawartości (payload).

Obsługiwane metody uwierzytelniania są zadeklarowane w Karcie Agenta; klienci odczytują te informacje i stosują się do nich.

### Wsparcie ponad 150 organizacji (stan na kwiecień 2026 r.)

Zainteresowanie ze strony przedsiębiorstw przełożyło się na dynamiczny rozwój i standaryzację A2A. Protokół ten stał się domyślnym standardem bezpiecznej komunikacji między autonomicznymi systemami w różnych domenach zaufania. Google Cloud wbudowało obsługę A2A w Vertex AI Agent Builder, Microsoft wspiera go w ramach Microsoft Agent Framework, a większość wiodących frameworków (LangGraph, CrewAI, AutoGen) dostarcza gotowe adaptery A2A.

### Zalety stosowania protokołu A2A

- **Integracja międzyorganizacyjna.** Agent z firmy A wywołuje agenta z firmy B. Bez A2A każde takie połączenie wymagałoby dedykowanej implementacji.
- **Środowiska heterogeniczne.** Agent w LangGraph wywołuje agenta w CrewAI, który z kolei odwołuje się do niestandardowego skryptu w Pythonie. A2A ujednolica interfejs komunikacyjny.
- **Typowane artefakty.** Wideo, strukturyzowany JSON, audio — wszystkie te formaty są natywnie obsługiwane przez specyfikację.
- **Obsługa zadań długoterminowych.** Abstrakcyjny cykl życia w połączeniu z odpytywaniem (pollingiem) upraszcza koordynację procesów trwających wiele godzin.

### Ograniczenia protokołu A2A

- **Scenariusze wrażliwe na opóźnienia (low-latency).** Model A2A z założenia działa asynchronicznie. W przypadku komunikacji wymagającej opóźnień rzędu milisekund A2A się nie sprawdzi; lepiej zastosować bezpośrednie wywołania RPC.
- **Agenty działające w ramach jednego procesu.** Jeśli oba komponenty działają w tym samym procesie systemu operacyjnego, narzut związany z pełną komunikacją sieciową HTTP przez A2A jest nieuzasadniony.
- **Niewielkie projekty wewnętrzne.** Narzut związany z implementacją pełnej specyfikacji jest odczuwalny. W przypadku systemów zamkniętych, działających wyłącznie wewnętrznie, taka formalizacja może być zbędna.

### A2A a ACP, ANP, NLIP

W okresie 2024–2026 rozwijano kilka pokrewnych specyfikacji:

- **ACP** (IBM / Linux Foundation) — wczesny prekursor A2A o węższym zakresie zastosowań.
- **ANP** (Agent Network Protocol) — kładzie nacisk na zdecentralizowane wykrywanie węzłów sieci (peers).
- **NLIP** (Ecma Natural Language Interaction Protocol, standaryzacja w grudniu 2025 r.) — koncentruje się na komunikacji za pomocą języka naturalnego.

A2A stał się najszerzej przyjętym protokołem komunikacji równorzędnej (stan na kwiecień 2026 r.). Szczegółowe porównanie można znaleźć w artykule arXiv:2505.02279 (Liu et al., „A Survey of Agent Interoperability Protocols”).

## Zbuduj to

Plik `code/main.py` implementuje minimalistyczny serwer i klienta zgodnych z A2A, używając biblioteki standardowej Pythona (`http.server` oraz `json`).

Funkcje serwera:
- udostępnia plik `/.well-known/agent.json`,
- obsługuje żądania `POST /tasks`,
- zarządza stanem realizowanych zadań,
- zwraca wygenerowane artefakty w odpowiedzi na `GET /tasks/{id}`.

Funkcje klienta:
- pobiera Kartę Agenta,
- zleca nowe zadanie,
- odpytuje serwer o status (polling) aż do zakończenia zadania,
- odczytuje wygenerowany artefakt.

Uruchomienie:

```bash
python3 code/main.py
```

Skrypt uruchamia serwer w wątku w tle, a następnie wykonuje zapytania klienckie. Możesz zaobserwować pełną procedurę: odkrycie agenta, utworzenie zadania, monitorowanie postępu i pobranie artefaktu.

## Zastosowanie

Plik `outputs/skill-a2a-integrator.md` opisuje projekt integracji A2A: strukturę karty agenta, schematy zadań, wybraną metodę uwierzytelniania oraz porównanie przesyłu strumieniowego (streaming) z odpytywaniem (polling).

## Wdrożenie produkcyjne

Lista kontrolna:

- **Określenie wersji specyfikacji.** Standard A2A stale się rozwija, dlatego Karta Agenta powinna jawnie deklarować obsługiwaną wersję protokołu.
- **Idempotentność tworzenia zadań.** Ponowne wysłanie tego samego żądania (np. wskutek problemów sieciowych) powinno skutkować zarejestrowaniem tylko jednego zadania.
- **Schematy struktur artefaktów.** Zadeklaruj strukturę danych zwracanych przez agenta, aby klienci mogli je poprawnie zwalidować.
- **Ograniczanie liczby żądań (Rate limiting) i autoryzacja.** Ponieważ punkty końcowe A2A mogą być publicznie dostępne, zastosuj standardowe zabezpieczenia sieciowe i limity zapytań.
- **Kolejka wiadomości niedostarczonych (Dead-letter queue) dla błędnych zadań.** Monitoruj nieudane procesy, aby wykrywać powtarzające się wzorce błędu.

## Ćwiczenia

1. Uruchom `code/main.py`. Upewnij się, że klient poprawnie odnalazł serwer i pobrał oczekiwany artefakt.
2. Dodaj nową kompetencję na serwerze (np. `summarize`). Zaktualizuj Kartę Agenta. Zaimplementuj logikę klienta wybierającą odpowiednią umiejętność na podstawie typu zadania.
3. Zaimplementuj punkt końcowy dla strumieniowania zdarzeń (Server-Sent Events): `/tasks/{id}/events`, który na bieżąco wysyła zmiany statusu. Jakie zmiany w obsłudze połączenia musi wprowadzić klient?
4. Przeanalizuj oficjalną specyfikację A2A (https://a2a-protocol.org/latest/specification/). Wskaż trzy wymagane elementy standardu, które zostały pominięte w niniejszej uproszczonej demonstracji.
5. Porównaj podejście A2A (odkrywanie przez Kartę Agenta) z MCP (listowanie narzędzi po stronie serwera za pomocą metody `listTools`). Jakie są wady i zalety samoopisujących się agentów w porównaniu z odpytywaniem o dostępne możliwości?

## Kluczowe terminy

| Termin | Obiegowe określenie | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| A2A | „Agent-to-Agent” | Protokół komunikacji równorzędnej umożliwiający agentom wywoływanie innych agentów w rozproszonych systemach (Google 2025). |
| Karta agenta (Agent Card) | „Wizytówka agenta” | Dokument JSON dostępny pod adresem `/.well-known/agent.json`, opisujący kompetencje, punkty końcowe i metody uwierzytelniania. |
| Zadanie (Task) | „Jednostka pracy” | Asynchroniczny obiekt o określonym cyklu życia; po zakończeniu udostępnia wygenerowane artefakty. |
| Artefakt (Artifact) | „Wynik działania” | Typowany obiekt wyjściowy: tekst, strukturyzowany JSON, obraz, wideo lub dźwięk. Obsługa multimediów jest tu kluczowym elementem. |
| Abstrakcyjny cykl życia | „Sposób wykonania leży po stronie agenta” | Klient monitoruje jedynie zmiany stanów zadania, natomiast serwer ma pełną swobodę w wyborze technologii i frameworka do jego realizacji. |
| Odkrywanie usług (Discovery) | „Wyszukanie agenta” | Wywołanie `GET /.well-known/agent.json` w celu pobrania właściwości agenta. |
| MCP a A2A | „Narzędzia kontra partnerzy” | MCP: komunikacja pionowa agent ↔ narzędzie. A2A: komunikacja pozioma agent ↔ agent. |
| ACP / ANP / NLIP | „Pokrewne protokoły” | Pokrewne standardy; A2A zyskał największą popularność do 2026 roku. |

## Literatura uzupełniająca

- [Specyfikacja A2A](https://a2a-protocol.org/latest/specification/) — specyfikacja kanoniczna
- [Blog Google Developers – ogłoszenie A2A](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/) — wpis z kwietnia 2025 r. wprowadzający standard
- [Repozytorium A2A na GitHubie](https://github.com/a2aproject/A2A) — implementacje referencyjne i pakiety SDK
- [Liu i in. — Przegląd protokołów interoperacyjności agentów](https://arxiv.org/html/2505.02279v1) — porównanie standardów MCP, ACP, A2A, ANP
