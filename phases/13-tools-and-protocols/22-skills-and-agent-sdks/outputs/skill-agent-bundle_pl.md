---

name: agent-bundle
description: Utwórz przenośny projekt serwera SKILL.md + AGENTS.md + MCP dla przepływu pracy, który można załadować w Claude Code, Cursor, Codex i kompatybilnych agentach.
version: 1.0.0
phase: 13
lesson: 21
tags: [skills, agents-md, apps-sdk, cross-agent, portability]

---

Mając opis przepływu pracy, utwórz pakiet agenta.

Wyprodukuj:

1. UMIEJĘTNOŚĆ.md. Frontmateria YAML z `name` i `description`, treść przeceny z ponumerowanymi krokami. Jeśli treść jest długa, uwzględnij odniesienia do podzasobów z ujawnianiem stopniowym.
2. Wpis AGENTS.md. Kilka linii do dodania do pliku AGENTS.md repozytorium, odzwierciedlających konwencje, od których zależy dana umiejętność (polecenia linter, polecenia testowe).
3. Projekt serwera MCP. Które narzędzia wymagają umiejętności poprzez MCP; nazwa, opis (wzorzec „Użyj kiedy”) i schemat wejściowy.
4. Tłumaczenia międzyagentowe. Uwagi w stylu SkillKit dotyczące mapowania pliku SKILL.md na reguły kursora, Kodeks `.codex.md` i zasady windsurfingu.
5. Ścieżka ładowania. Gdzie agenci odkryją ten pakiet: `~/.anthropic/skills/`, `./skills/`, `~/.claude/skills/`.

Twarde odrzucenia:
- Dowolny SKILL.md, którego `name` nie jest `kebab-case`. Przerywa odkrywanie.
- Dowolny SKILL.md bez `description` w tle. Środowiska wykonawcze agenta pomijają to.
- Dowolny pakiet, którego narzędzia MCP nie są nazwane zgodnie z zasadami fazy 13 · 05.

Zasady odmowy:
- Jeśli przepływ pracy jest pojedynczym, jednorazowym poleceniem, odmów opracowania umiejętności; recommend inline prompt-engineering.
- Jeśli przepływ pracy wymaga protokołu OAuth (np. post w Slack), zaznacz, że pierwsze wywołanie serwera MCP musi to obsłużyć.
- Jeśli agenci docelowi nie obsługują SKILL.md (niektóre IDE), zalecamy tłumaczenie za pomocą SkillKit lub podobnego.

Wynik: jednostronicowy pakiet zawierający trzy szkicowane pliki, notatki dotyczące tłumaczenia między agentami i ścieżkę ładowania. Zakończ na pojedynczym agencie, aby najpierw przetestować pakiet.