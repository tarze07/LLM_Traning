# Umiejętności i zestawy SDK agentów — Anthropic Skills, AGENTS.md, OpenAI Apps SDK

> MCP mówi „jakie narzędzia istnieją”. Umiejętności mówią „jak wykonać zadanie”. Stos 2026 składa się z obu warstw. Umiejętności agenta firmy Anthropic (standard otwarty, grudzień 2025 r.) są dostarczane jako SKILL.md ze stopniowym ujawnianiem. Zestaw SDK aplikacji OpenAI składa się z MCP i metadanych widżetów. Plik AGENTS.md (obecnie dostępny w ponad 60 000 repozytoriów) znajduje się w katalogu głównym repozytorium jako kontekst agenta na poziomie projektu. W tej lekcji omówiono, co obejmuje każdy z nich, i zbudowano minimalny pakiet SKILL.md + AGENTS.md, który jest przesyłany między agentami.

**Typ:** Ucz się
**Języki:** Python (stdlib, parser i moduł ładujący SKILL.md)
**Wymagania wstępne:** Faza 13 · 07 (serwer MCP)
**Czas:** ~45 minut

## Cele nauczania

- Rozróżnij trzy warstwy: AGENTS.md (kontekst projektu), SKILL.md (know-how wielokrotnego użytku), MCP (narzędzia).
- Napisz SKILL.md z tematem przewodnim YAML i stopniowym ujawnianiem informacji.
- Załaduj umiejętności w stylu systemu plików do środowiska wykonawczego agenta.
- Skomponuj umiejętność za pomocą serwera MCP i pliku AGENTS.md, aby jeden pakiet działał w Claude Code, Cursor i Codex.

## Problem

Inżynier dzieli proces pisania notatek do wydania na wieloetapowy monit: „Przeczytaj najnowsze połączone żądania ściągnięcia. Pogrupuj według obszarów. Podsumuj każdy. Napisz wpis do dziennika zmian zgodnie ze stylem zespołu. Opublikuj wersję roboczą Slacka”. Umieścili to w dokumencie Notion dla swojego zespołu.

Teraz chcą korzystać z tego przepływu pracy z Claude Code, Cursor i Codex CLI. Każdy agent ma inny sposób ładowania instrukcji: polecenia ukośnika Claude Code, reguły kursora, Kodeks `.codex.md`. Inżynier kopiuje przepływ pracy trzy razy i przechowuje trzy kopie.

AGENTS.md i SKILL.md wspólnie naprawiają ten problem:

- **AGENTS.md** znajduje się w katalogu głównym repo. Każdy kompatybilny agent czyta go na początku sesji. „Jak działa ten projekt? Jakie są konwencje? Które polecenia uruchamiają testy?”
- **SKILL.md** to przenośny pakiet: frontmatter YAML (nazwa, opis) + treść przeceny + opcjonalne zasoby. Agenci obsługujący umiejętności ładują je według nazwy na żądanie.
- **MCP** (faza 13 · 06-14) obsługuje narzędzia potrzebne do przywołania umiejętności.

Trzy warstwy, jeden przenośny artefakt.

## Koncepcja

### AGENTÓW.md (agentów.md)

Uruchomiony pod koniec 2025 r., przyjęty przez ponad 60 000 repozytoriów do kwietnia 2026 r. Jeden plik w katalogu głównym repo. Format:

```markdown
# Project: my-service

## Conventions
- TypeScript with strict mode.
- Use Pydantic for models on the Python side.
- Tests run with `pnpm test`.

## Build and run
- `pnpm dev` for local dev server.
- `pnpm build` for production bundle.
```

Agenci czytają to na początku sesji i używają go do kalibracji swojego zachowania dla tego projektu. Każdy agent kodujący w 2026 roku obsługuje AGENTS.md: Claude Code, Cursor, Codex, Copilot Workspace, opencode, Windsurf, Zed.

### Format SKILL.md

Anthropic's Agent Skills (wydany jako otwarty standard w grudniu 2025 r.):

```markdown
---
name: release-notes-writer
description: Write a changelog entry for the latest merged PRs following this project's style.
---

# Release notes writer

When invoked, run these steps:

1. List PRs merged since the last tag. Use `gh pr list --base main --state merged`.
2. Group by label: feature, fix, chore, docs.
3. For each PR in each group, write one line: `- <title> (#<num>)`.
4. Draft the release notes and stage them in CHANGELOG.md.

If the user says "ship", run `git tag vX.Y.Z` and `gh release create`.

## Notes

- Never include commits without a PR.
- Skip "chore" entries from the public changelog.
```

Frontmatter deklaruje tożsamość umiejętności. Treść to monit pokazywany modelowi po załadowaniu umiejętności.

### Stopniowe ujawnianie

Umiejętności mogą odwoływać się do zasobów podrzędnych, które agent pobiera tylko wtedy, gdy jest to potrzebne. Przykład:

```
skills/
  release-notes-writer/
    SKILL.md
    style-guide.md
    template.md
    scripts/
      generate.sh
```

SKILL.md mówi „zobacz styl-guide.md, aby zapoznać się z zasadami stylu”. Agent pobiera plik style-guide.md tylko wtedy, gdy umiejętność jest aktywnie uruchomiona. Pozwala to uniknąć zapełniania podpowiedzi szczegółami, których model może nie potrzebować.

### Wykrywanie systemu plików

Środowiska wykonawcze agentów skanują znane katalogi w poszukiwaniu plików SKILL.md:

- `~/.anthropic/skills/*/SKILL.md`
- Projekt `./skills/*/SKILL.md`
- `~/.claude/skills/*/SKILL.md`

Ładowanie odbywa się według nazwy folderu i tematu `name`. Claude Code, Anthropic Claude Agent SDK i SkillKit (cross-agent) podążają za tym wzorcem.

### Zestaw SDK agenta Anthropic Claude

`@anthropic-ai/claude-agent-sdk` (TypeScript) i `claude-agent-sdk` (Python) ładują umiejętności na początku sesji i udostępniają je jako wywoływalnych „agentów” w środowisku wykonawczym. Pętla agenta wywołuje umiejętność, gdy użytkownik ją wywoła.

### SDK aplikacji OpenAI

Uruchomiony w październiku 2025 r.; zbudowany bezpośrednio na MCP. Ujednolica wcześniejsze łączniki OpenAI i niestandardowe akcje GPT w ramach jednej platformy programistycznej. Aplikacja Apps SDK to:

- Serwer MCP (narzędzia, zasoby, podpowiedzi).
- Plus metadane widżetów dla interfejsu użytkownika ChatGPT.
- Plus opcjonalne zasoby `ui://` aplikacji MCP dotyczące powierzchni interaktywnych.

Ten sam protokół, bogatszy UX.

### Możliwość przenoszenia między agentami za pomocą zestawu SkillKit

Narzędzia takie jak SkillKit i podobne warstwy dystrybucji między agentami tłumaczą pojedynczy plik SKILL.md na natywny format każdego z ponad 32 agentów AI (Claude Code, Cursor, Codex, Gemini CLI, OpenCode itp.). Jedno źródło prawdy; wielu konsumentów.

### Stos trójwarstwowy

| Warstwa | Plik | Załadowano, gdy | Cel |
|-------|------|------------|--------|
| AGENTÓW.md | korzeń repozytorium | początek sesji | konwencje na poziomie projektu |
| UMIEJĘTNOŚĆ.md | katalog umiejętności | umiejętność przywołana | przepływ pracy wielokrotnego użytku |
| Serwer MCP | proces zewnętrzny | potrzebne narzędzia | wywoływalne działania |

Wszystkie trzy elementy tworzą: agent czyta plik AGENTS.md na początku sesji, użytkownik wywołuje umiejętność, instrukcje umiejętności obejmują wywołania narzędzi MCP, agent wysyła wiadomości za pośrednictwem klienta MCP.

## Użyj tego

`code/main.py` zawiera parser i moduł ładujący stdlib SKILL.md. Odkrywa umiejętności w `./skills/`, analizuje treść YAML plus treść przeceny i tworzy słownik oparty na nazwie umiejętności. Następnie symuluje pętlę agenta, która wywołuje `release-notes-writer` według nazwy.

Na co zwrócić uwagę:

- Materiał frontowy YAML przeanalizowany przy użyciu minimalnego parsera stdlib (bez zależności `pyyaml`).
- Treść umiejętności przechowywana dosłownie; agent dołącza go do zachęty systemowej podczas wywołania.
- Progresywne ujawnianie zademonstrowane za pomocą funkcji `read_subresource`, która pobiera pliki odniesienia na żądanie.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-agent-bundle.md`. Biorąc pod uwagę przepływ pracy, umiejętność tworzy połączony pakiet SKILL.md + AGENTS.md + MCP-server-blueprint, który można przenosić między agentami.

## Ćwiczenia

1. Uruchom `code/main.py`. Dodaj drugą umiejętność w obszarze `skills/` i potwierdź, że moduł ładujący ją podnosi.

2. Napisz plik AGENTS.md dla repozytorium tego kursu. Uwzględnij polecenia testowe, konwencje stylu i model mentalny fazy 13.

3. Przenieś wieloetapowy przepływ pracy z wewnętrznych dokumentów swojego zespołu do SKILL.md. Sprawdź, czy ładuje się w Claude Code.

4. Ręcznie przetłumacz umiejętność na natywne formaty reguł Cursora i Kodeksu. Policz różnice między formatami — to powierzchnia tłumaczenia, którą SkillKit automatyzuje.

5. Przeczytaj wpis na blogu Anthropic Agent Skills. Wskaż jedną funkcję w pakiecie SDK Claude Agent, której nie obejmuje moduł ładujący tej lekcji. (Wskazówka: wywołanie podrzędne agenta.)

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| UMIEJĘTNOŚĆ.md | „Plik umiejętności” | Frontmatter YAML plus treść przeceny, ładowana przez środowisko wykonawcze agenta |
| AGENTÓW.md | „Kontekst agenta root-repo” | Plik konwencji na poziomie projektu odczytywany na początku sesji |
| Stopniowe ujawnianie | „Leniwe ładowanie zasobów podrzędnych” | Treść umiejętności odwołuje się do plików pobieranych tylko w razie potrzeby |
| Temat | „Blok YAML na górze” | Metadane (nazwa, opis) w ogranicznikach `---` |
| SDK agenta Claude'a | „Czas działania umiejętności Anthropic” | `@anthropic-ai/claude-agent-sdk`, ładuje umiejętności i trasy |
| Zestaw SDK aplikacji OpenAI | „Meta widżetu MCP +” | Powierzchnia programistyczna OpenAI zbudowana na hakach MCP i ChatGPT UI |
| Odkrywanie umiejętności | „Skanowanie systemu plików” | Przejdź do znanych katalogów SKILL.md, klucz po nazwie |
| Przenośność między agentami | „Jedna umiejętność, wielu agentów” | Przetłumacz jeden plik SKILL.md na ponad 32 agentów za pomocą narzędzi w stylu SkillKit |
| Umiejętność agenta | „Przenośne know-how” | Szablon zadania wielokrotnego użytku poza koncepcją narzędzia MCP |
| Zestaw SDK aplikacji | „MCP plus interfejs ChatGPT” | Złącza i niestandardowe GPT ujednolicone w MCP |

## Dalsze czytanie

– [Anthropic — ogłoszenie dotyczące umiejętności agenta](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) — premiera w grudniu 2025 r.
- [Anthropic — dokumentacja Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) — odniesienie do formatu SKILL.md
- [OpenAI — Apps SDK](https://developers.openai.com/apps-sdk) — platforma programistyczna oparta na MCP dla ChatGPT
- [agents.md](https://agents.md/) — format AGENTS.md i lista adopcyjna
- [Anthropic — anthropics/skills GitHub](https://github.com/anthropics/skills) — oficjalne przykłady umiejętności