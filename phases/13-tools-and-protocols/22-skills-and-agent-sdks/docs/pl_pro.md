# Umiejętności i zestawy SDK agentów — Anthropic Skills, AGENTS.md i OpenAI Apps SDK

> Protokół MCP określa dostępne narzędzia, natomiast umiejętności (skills) definiują procedurę wykonania zadania. Nowoczesny stos technologiczny (stan na rok 2026) łączy obie te warstwy. Anthropic Agent Skills (otwarty standard wprowadzony w grudniu 2025 r.) są dostarczane w postaci pliku SKILL.md wspierającego stopniowe ujawnianie informacji (progressive disclosure). Z kolei OpenAI Apps SDK integruje protokół MCP z metadanymi widżetów interfejsu. Plik AGENTS.md (obecny w ponad 60 000 repozytoriów) umieszcza się w katalogu głównym projektu jako kontekst operacyjny dla agenta. W tej lekcji omawiamy te standardy i budujemy przenośny pakiet łączący pliki SKILL.md, AGENTS.md oraz specyfikację MCP.

**Typ:** Teoria
**Język:** Python (biblioteka standardowa, parser i moduł ładujący pliki SKILL.md)
**Wymagania wstępne:** Faza 13 · 07 (serwer MCP)
**Czas:** ~45 minut

## Cele lekcji

- Rozróżnianie trzech warstw konfiguracji: AGENTS.md (kontekst projektu), SKILL.md (wielokrotne procedury/know-how) oraz MCP (narzędzia techniczne).
- Tworzenie plików SKILL.md z nagłówkiem YAML (frontmatter) oraz strukturą stopniowego ujawniania informacji.
- Implementacja automatycznego ładowania umiejętności z systemu plików do środowiska uruchomieniowego agenta.
- Konsolidacja umiejętności, specyfikacji serwera MCP oraz pliku AGENTS.md in spójny pakiet działający w środowiskach Claude Code, Cursor i Codex.

## Problem

Wyobraźmy sobie inżyniera, który ustrukturyzował proces generowania notatek z wydania (release notes) w wieloetapową instrukcję: „Odczytaj ostatnio scalone Pull Requesty. Pogrupuj je tematycznie. Podsumuj każdy z nich. Zredaguj wpis do changelogu zgodnie ze stylem zespołu. Opublikuj wersję roboczą na kanale Slack”. Instrukcja ta została zapisana w wewnętrznej bazie wiedzy Notion.

Teraz inżynier chce udostępnić ten proces dla różnych systemów agentowych: Claude Code, Cursor oraz Codex CLI. Każdy z tych agentów ma jednak własny format ładowania reguł: polecenia ukośnika (slash commands) w Claude Code, plik `.cursorrules` w Cursorze czy `.codex.md` w Codex. W rezultacie inżynier musi utrzymywać i synchronizować trzy osobne kopie tego samego procesu.

Wprowadzenie standardów AGENTS.md oraz SKILL.md skutecznie eliminuje ten problem:

- **AGENTS.md** jest umieszczany w katalogu głównym repozytorium. Każdy kompatybilny agent odczytuje go na początku sesji, aby poznać architekturę projektu, konwencje kodowania oraz polecenia testowe.
- **SKILL.md** stanowi przenośny moduł procedury: zawiera nagłówek YAML (nazwa, opis), treść w formacie Markdown oraz opcjonalne zasoby pomocnicze. Agenci ładują te instrukcje dynamicznie na żądanie.
- **MCP** (Faza 13 · 06-14) udostępnia fizyczne narzędzia (API, skrypty) niezbędne do realizacji kroków opisanych w umiejętności.

Trzy warstwy, jeden spójny standard.

## Założenia koncepcyjne

### AGENTS.md

Standard wprowadzony pod koniec 2025 roku, wdrożony w ponad 60 000 projektów do kwietnia 2026 roku. Jest to pojedynczy plik umieszczany w katalogu głównym repozytorium:

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

Agenci analizują ten plik na starcie i dostosowują swoje zachowanie do specyfiki projektu. W 2026 roku standard ten jest natywnie obsługiwany przez wiodące narzędzia deweloperskie AI (np. Claude Code, Cursor, Codex, Copilot Workspace, OpenCode, Windsurf, Zed).

### Format SKILL.md

Standard otwarty Anthropic Agent Skills (opublikowany w grudniu 2025 r.):

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

Nagłówek YAML (frontmatter) określa metadane i tożsamość umiejętności. Treść Markdown stanowi instrukcję systemową (prompt) dołączaną do kontekstu modelu po aktywacji danej umiejętności.

### Stopniowe ujawnianie informacji (Progressive Disclosure)

Standard umożliwia leniwe ładowanie (lazy loading) zasobów podrzędnych, które agent pobiera wyłącznie wtedy, gdy są one niezbędne do realizacji bieżącego kroku. Przykład struktury:

```
skills/
  release-notes-writer/
    SKILL.md
    style-guide.md
    template.md
    scripts/
      generate.sh
```

Plik `SKILL.md` może zawierać odwołanie w rodzaju: „zapoznaj się z plikiem `style-guide.md` w celu weryfikacji stylu”. Agent pobierze ten plik dopiero w momencie wywołania tej konkretnej reguły. Chroni to kontekst (prompt size) przed przepełnieniem nadmiarowymi informacjami.

### Wykrywanie w systemie plików

Środowiska uruchomieniowe agentów automatycznie skanują predefiniowane ścieżki w poszukiwaniu plików `SKILL.md`:

- `~/.anthropic/skills/*/SKILL.md`
- Katalog projektu: `./skills/*/SKILL.md`
- `~/.claude/skills/*/SKILL.md`

Wyszukiwanie i indeksowanie bazuje na nazwach katalogów oraz polu `name` w nagłówku YAML. Schemat ten jest stosowany m.in. przez Claude Code, Anthropic Claude Agent SDK oraz multi-agentowe narzędzie SkillKit.

### Zestaw SDK Anthropic Claude Agent

Biblioteki `@anthropic-ai/claude-agent-sdk` (TypeScript) oraz `claude-agent-sdk` (Python) ładują zdefiniowane umiejętności na starcie sesji, udostępniając je jako moduły wykonawcze. Pętla agenta deleguje zadania do odpowiedniej umiejętności w oparciu o intencje użytkownika.

### OpenAI Apps SDK

Wprowadzony w październiku 2025 roku standard zbudowany bezpośrednio na protokole MCP. Konsoliduje on wcześniejsze integracje OpenAI oraz wtyczki Custom GPTs w jedną spójną platformę deweloperską. Na zestaw OpenAI Apps SDK składają się:

- Serwer MCP (dostarczający narzędzia, zasoby i prompty).
- Metadane widżetów dedykowane dla interfejsu ChatGPT.
- Opcjonalne zasoby interaktywnego interfejsu graficznego (schemat `ui://`).

Identyczny protokół bazowy, rozszerzony o interfejs graficzny.

### Przenośność między agentami (Cross-Agent Portability)

Narzędzia takie jak SkillKit kompilują i tłumaczą pojedynczy plik źródłowy `SKILL.md` na formaty natywne dla ponad 32 różnych środowisk agentowych (m.in. Claude Code, Cursor, Codex, Gemini CLI, OpenCode). Zapewnia to jedno źródło prawdy dla wielu konsumentów.

### Trójwarstwowy stos konfiguracyjny

| Warstwa | Plik | Moment załadowania | Zastosowanie |
|-------|------|------------|--------|
| AGENTS.md | Katalog główny repozytorium | Start sesji | Ogólne konwencje i architektura projektu |
| SKILL.md | Katalog danej umiejętności | Wywołanie danej umiejętności | Opis procedury i przepływu pracy |
| Serwer MCP | Zewnętrzny proces (daemon/serwer) | Wywołanie powiązanego narzędzia | Fizyczne akcje techniczne (narzędzia) |

Wszystkie trzy elementy współpracują ze sobą: agent odczytuje reguły `AGENTS.md` na starcie sesji, użytkownik wywołuje określoną procedurę ze `SKILL.md`, a instrukcja ta wykonuje niskopoziomowe narzędzia techniczne za pośrednictwem serwera MCP.

## Zastosowanie w praktyce

Skrypt `code/main.py` zawiera parser i moduł ładujący pliki `SKILL.md` oparty na bibliotece standardowej Pythona. Wyszukuje on umiejętności w katalogu `./skills/`, przetwarza strukturę YAML oraz Markdown (bez użycia zewnętrznych bibliotek typu `pyyaml`) i indeksuje je w słowniku. Następnie skrypt symuluje pętlę agenta wywołującą moduł `release-notes-writer`.

Kluczowe elementy:

- Parser frontmattera YAML napisany bez zewnętrznych zależności.
- Instrukcja Markdown dołączana bezpośrednio do systemowego promptu przy wywołaniu.
- Leniwe pobieranie powiązanych zasobów na żądanie (funkcja `read_subresource`).

## Zadanie praktyczne

Wynikiem tej lekcji powinno być przygotowanie pliku `outputs/skill-agent-bundle.md`. Na podstawie opisu wybranego przepływu pracy należy utworzyć zintegrowany pakiet składający się z plików SKILL.md, AGENTS.md oraz schematu serwera MCP (MCP server blueprint), który można łatwo wdrażać w różnych środowiskach agentowych.

## Ćwiczenia

1. Uruchom skrypt `code/main.py`. Add nową umiejętność w katalogu `./skills/` i upewnij się, że została prawidłowo wykryta i załadowana.

2. Utwórz plik `AGENTS.md` dedykowany dla repozytorium tego kursu. Uwzględnij w nim polecenia uruchamiające testy, styl kodowania oraz założenia modelu mentalnego Fazy 13.

3. Przepisz jeden z wieloetapowych procesów deweloperskich swojego zespołu do pliku `SKILL.md`. Przetestuj jego poprawne ładowanie w środowisku Claude Code.

4. Dokonaj ręcznego mapowania pliku `SKILL.md` na formaty `.cursorrules` oraz `.codex.md`. Przeanalizuj różnice strukturalne i wysiłek potrzebny na synchronizację (to zadanie automatyzuje narzędzie SkillKit).

5. Zapoznaj się z oficjalnymi materiałami Anthropic na temat Agent Skills. Wskaż jedną zaawansowaną funkcję w Claude Agent SDK, której nie wspiera nasz uproszczony parser (Wskazówka: przeanalizuj wywołania subagentów).

## Kluczowe pojęcia

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| SKILL.md | „Opis umiejętności” | Plik zawierający nagłówek YAML oraz treść Markdown z procedurą zadania |
| AGENTS.md | „Kontekst projektu” | Plik konwencji i reguł projektu umieszczany w katalogu głównym repozytorium |
| Stopniowe ujawnianie | „Leniwe ładowanie” | Dynamiczne pobieranie zasobów podrzędnych (sub-resources) dopiero w momencie ich użycia |
| Frontmatter | „Nagłówek YAML” | Blok metadanych umieszczony na początku pliku Markdown pomiędzy znacznikami `---` |
| Claude Agent SDK | „Środowisko uruchomieniowe” | Oficjalny zestaw narzędzi SDK do ładowania i wykonywania umiejętności agentowych |
| OpenAI Apps SDK | „Integracja MCP i UI” | Zestaw narzędzi programistycznych integrujący serwery MCP z widżetami w interfejsie ChatGPT |
| Autowykrywanie | „Skanowanie systemu plików” | Automatyczne wyszukiwanie plików `SKILL.md` w zdefiniowanych ścieżkach |
| Przenośność | „Cross-Agent Portability” | Zdolność do kompilacji jednego pliku `SKILL.md` na formaty natywne dla wielu agentów (np. przez SkillKit) |
| Umiejętność (Skill) | „Know-how” | Przenośny i wielokrotnego użytku szablon postępowania opisujący procedurę wykonania zadania |
| Apps SDK | „MCP z interfejsem graficznym” | Nowy standard OpenAI ujednolicający wcześniejsze integracje w oparciu o MCP |

## Polecana literatura / dokumentacja

- [Anthropic — ogłoszenie dotyczące umiejętności agenta](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) — premiera w grudniu 2025 r.
- [Anthropic — dokumentacja Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) — odniesienie do formatu SKILL.md
- [OpenAI — Apps SDK](https://developers.openai.com/apps-sdk) — platforma programistyczna oparta na MCP dla ChatGPT
- [agents.md](https://agents.md/) — format AGENTS.md i lista adopcyjna
- [Anthropic — anthropics/skills GitHub](https://github.com/anthropics/skills) — oficjalne przykłady umiejętności
