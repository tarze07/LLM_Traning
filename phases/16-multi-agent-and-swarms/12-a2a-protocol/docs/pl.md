# A2A — Protokół agent-agent

> Google ogłosił A2A w kwietniu 2025 r.; do kwietnia 2026 r. specyfikacja będzie dostępna pod adresem https://a2a-protocol.org/latest/specification/ i popiera ją ponad 150 organizacji. A2A jest poziomym uzupełnieniem MCP (lekcja 13): gdzie MCP jest pionowe (agent ↔ narzędzia), A2A to peer-to-peer (agent ↔ agent). Definiuje karty agentów (odkrywanie), zadania z artefaktami (tekst, dane strukturalne, wideo), nieprzejrzyste cykle życia zadań i uwierzytelnianie. Systemy produkcyjne coraz częściej łączą MCP z A2A. W latach 2025–2026 Google Cloud włączył obsługę A2A do narzędzia Vertex AI Agent Builder.

**Typ:** Ucz się + Buduj
**Języki:** Python (stdlib, `http.server`, `json`)
**Wymagania wstępne:** Faza 16 · 04 (model prymitywny)
**Czas:** ~75 minut

## Problem

Twój agent musi zadzwonić do innego agenta w innym systemie. Jak? Możesz ujawnić punkt końcowy HTTP, zdefiniować dostosowany schemat JSON i mieć nadzieję, że druga strona to wypowie. Każda para agentów staje się niestandardową integracją.

A2A to uniwersalny protokół przewodowy dla tego połączenia. Standardowe wykrywanie, standardowy model zadań, standardowy transport, standardowe artefakty. Podobnie jak HTTP+REST, ale dla agentów jako obywateli pierwszej klasy.

## Koncepcja

### Cztery żywioły

**Karta agenta.** Dokument JSON pod adresem `/.well-known/agent.json` opisujący agenta: imię i nazwisko, umiejętności, punkty końcowe, obsługiwane modalności, wymagania dotyczące uwierzytelniania. Odkrycie następuje poprzez odczytanie karty.

```
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

**Zadanie.** Jednostka pracy. Asynchroniczny obiekt stanowy z cyklem życia: `submitted → working → completed / failed / canceled`. Klient wysyła zadanie, ankietę lub subskrybuje aktualizacje.

**Artefakt.** Typ wyniku wygenerowanego przez zadanie. Tekst, strukturalny JSON, obraz, wideo, audio. Artefakty są wpisywane na maszynie, więc różne modalności są najwyższej klasy.

**Nieprzejrzysty cykl życia.** A2A nie określa, *w jaki sposób* zdalny agent rozwiąże zadanie. Klient widzi przejścia stanów i artefakty; wdrożenie jest bezpłatne i można wykorzystać dowolny framework.

### Podział MCP/A2A

- **MCP** (Lekcja 13): agent ↔ narzędzie. Agent odczytuje/zapisuje za pośrednictwem JSON-RPC do serwera narzędzi. Domyślnie bezstanowy.
- **A2A**: agent ↔ agent. Protokół równorzędny; obie strony są agentami mającymi własne rozumowanie.

Produkcyjne systemy wieloagentowe korzystają z obu rozwiązań. Partner A2A wywołuje narzędzia MCP na swojej stronie. Podział utrzymuje oba koncerny w czystości.

### Przebieg odkrywania

```
Client                     Agent server
  ├──GET /.well-known/agent.json──>
  <──Agent Card JSON─────────────
  ├──POST /tasks {skill, input}──>
  <──201 task_id, state=submitted
  ├──GET /tasks/{id}──────────────>
  <──state=working, 42% done──────
  ├──GET /tasks/{id}──────────────>
  <──state=completed, artifacts──
```

Lub w przypadku przesyłania strumieniowego: subskrypcja SSE w `/tasks/{id}/events` w celu uzyskania aktualizacji push.

### Autoryz

A2A obsługuje trzy typowe wzorce:

- **Token okaziciela** — OAuth2 lub nieprzezroczysty.
- **mTLS** — wzajemny TLS; organizacje udowadniają sobie nawzajem tożsamość.
- **Podpisane żądania** — HMAC przez ładunek.

Autoryzacja jest zadeklarowana na Karcie Agenta; klienci odkrywają i przestrzegają.

### 150+ organizacji do kwietnia 2026 r

Wdrożenie w przedsiębiorstwach doprowadziło do skali A2A. Nagłówek: A2A stało się sposobem, w jaki systemy agentów korporacyjnych przekraczają granice zaufania. Google Cloud dostarczyło obsługę Vertex AI Agent Builder A2A; Obsługuje to Microsoft Agent Framework; większość głównych frameworków (LangGraph, CrewAI, AutoGen) zawiera adaptery A2A.

### Gdzie wygrywa A2A

- **Połączenia między organizacjami.** Agent w firmie A dzwoni do agenta w firmie B. Bez A2A każda para to umowa na zamówienie.
- **Struktury heterogeniczne.** Agent LangGraph wywołuje agenta CrewAI wywołującego niestandardowego agenta Pythona. A2A normalizuje się.
- **Artefakty wpisane.** Wynik wideo, strukturalny JSON, dźwięk — wszystko najwyższej klasy.
- **Zadania długotrwałe.** Nieprzezroczysty cykl życia + odpytywanie sprawia, że ​​wielogodzinne zadania stają się proste.

### Gdzie A2A ma problemy

- **Mikropołączenia wrażliwe na opóźnienia.** Cykl życia A2A jest asynchroniczny. Czas między agentami krótszy niż milisekunda nie pasuje; użyj bezpośredniego RPC.
- **Ściśle powiązani agenci wewnątrzprocesowi.** Jeśli obaj agenci działają w tym samym procesie Pythona, korzystanie z protokołu HTTP w obie strony przez A2A jest przesadą.
- **Małe zespoły.** Koszty ogólne specyfikacji są realne; agenci pracujący wyłącznie wewnętrznie mogą nie potrzebować tej formalności.

### A2A kontra ACP, ANP, NLIP

W latach 2024–2026 pojawiło się kilka powiązanych specyfikacji:

- **ACP** (IBM/Linux Foundation) — poprzednik A2A, węższy zakres.
- **ANP** (Protokół sieci agentów) — intensywne wykrywanie peerów, przede wszystkim zdecentralizowane.
- **NLIP** (Ecma Natural Language Interaction Protocol, ustandaryzowany w grudniu 2025 r.) — typ treści w języku naturalnym.

A2A jest najczęściej stosowanym protokołem równorzędnym według stanu na kwiecień 2026 r. Porównanie można znaleźć w artykule arXiv:2505.02279 (Liu i in., „A Survey of Agent Interoperability Protocols”).

## Zbuduj to

`code/main.py` implementuje serwer i klienta o minimalnym formacie A2A przy użyciu `http.server` i JSON. Serwer:

- eksponuje `/.well-known/agent.json`,
- akceptuje `POST /tasks`,
- zarządza stanem zadania,
- zwraca artefakty na `GET /tasks/{id}`.

Klient:

- pobiera Kartę Agenta,
- przesyła zadanie,
- ankiety do zakończenia,
- czyta artefakt.

Uruchom:

```
python3 code/main.py
```

Skrypt uruchamia serwer w wątku w tle, a następnie uruchamia na nim klienta. Widzisz cały proces: odkrycie, przesłanie, ankieta, artefakt.

## Użyj tego

`outputs/skill-a2a-integrator.md` projektuje integrację A2A: zawartość karty agenta, schematy zadań, wybór uwierzytelnienia, przesyłanie strumieniowe a odpytywanie.

## Wyślij to

Lista kontrolna:

- **Przypnij wersję specyfikacji.** A2A wciąż się rozwija; Karta Agenta powinna deklarować wersję protokołu.
- **Tworzenie zadania idempotentnego.** Zduplikowane zgłoszenia (ponowne próby sieciowe) powinny skutkować powstaniem jednego zadania.
- **Schematy artefaktów.** Zadeklaruj, jakie kształty zwraca agent; konsumenci powinni zweryfikować.
- **Limity stawek + autoryzacja.** A2A jest publicznie dostępne; zastosuj standardowe zabezpieczenia sieciowe.
- **Niedostarczona wiadomość w przypadku zadań zakończonych niepowodzeniem.** Sprawdzaj wzorce w czasie pod kątem powtarzających się typów błędów.

## Ćwiczenia

1. Uruchom `code/main.py`. Potwierdź, że klient odnalazł serwer i otrzymał poprawny artefakt.
2. Dodaj drugą umiejętność na serwer (np. "podsumowanie"). Zaktualizuj kartę agenta. Napisz klienta, który wybiera umiejętność na podstawie rodzaju zadania.
3. Zaimplementuj punkt końcowy przesyłania strumieniowego SSE: `/tasks/{id}/events`, który emituje zmiany stanu. Co klient musi zrobić inaczej?
4. Przeczytaj specyfikację A2A (https://a2a-protocol.org/latest/specification/). Zidentyfikuj trzy rzeczy wymagane przez specyfikację, których to demo nie implementuje.
5. Porównaj A2A (wykrywanie karty agenta) z MCP (lista możliwości po stronie serwera za pośrednictwem `listTools`). Jaki jest kompromis pomiędzy samoopisującymi się agentami a badaniem możliwości?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| A2A | „Agent do agenta” | Protokół równorzędny dla agentów umożliwiający wywoływanie innych agentów w różnych systemach. Google 2025. |
| Karta agenta | „Wizytówka agenta” | JSON w `/.well-known/agent.json` opisujący umiejętności, punkty końcowe, uwierzytelnianie. |
| Zadanie | „Jednostka pracy” | Asynchroniczny obiekt stanowy z cyklem życia; artefakty powstałe po ukończeniu. |
| Artefakt | „Rezultat” | Wpisane dane wyjściowe: tekst, strukturalny JSON, obraz, wideo, audio. Media pierwsza klasa. |
| Nieprzezroczysty cykl życia | „Jak to rozwiązać, to sprawa agenta” | Klient widzi przejścia stanów; serwer ma swobodę wyboru frameworka/narzędzi. |
| Odkrycie | „Znalezienie agenta” | `GET /.well-known/agent.json` zwraca kartę. |
| MCP kontra A2A | „Narzędzia kontra koledzy” | MCP: agent pionowy ↔ narzędzie. A2A: agent horyzontalny ↔ agent. |
| AKP/ANP/NLIP| „Protokoły rodzeństwa” | Sąsiednie specyfikacje; A2A jest najczęściej przyjętym rokiem 2026. |

## Dalsze czytanie

- [Specyfikacja A2A](https://a2a-protocol.org/latest/specification/) — specyfikacja kanoniczna
– [Blog Google Developers – ogłoszenie A2A](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/) – post o wprowadzeniu na rynek z kwietnia 2025 r.
- [Repo A2A GitHub](https://github.com/a2aproject/A2A) — implementacje referencyjne i pakiety SDK
- [Liu i in. — Przegląd protokołów interoperacyjności agentów](https://arxiv.org/html/2505.02279v1) — Porównanie MCP, ACP, A2A, ANP