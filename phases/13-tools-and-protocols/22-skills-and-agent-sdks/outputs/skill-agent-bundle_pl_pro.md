---

name: agent-bundle
description: Utwórz przenośny pakiet (SKILL.md + wpis do AGENTS.md + schemat serwera MCP) dla wybranego przepływu pracy, gotowy do załadowania w środowiskach Claude Code, Cursor, Codex i kompatybilnych agentach.
version: 1.0.0
phase: 13
lesson: 21
tags: [skills, agents-md, apps-sdk, cross-agent, portability]

---

Na podstawie opisu przepływu pracy utwórz zintegrowany pakiet konfiguracyjny agenta.

Wygeneruj następujące sekcje:

1. SKILL.md. Nagłówek (frontmatter) YAML zawierający pola `name` i `description`, treść w formacie Markdown z ponumerowanymi krokami procedury. W przypadku obszernych instrukcji wydziel zasoby pomocnicze (sub-resources), stosując zasadę stopniowego ujawniania informacji.
2. Wpis do AGENTS.md. Kilka linii do dodania do pliku konwencji projektu `AGENTS.md` (np. komendy lintera, komendy uruchamiające testy), od których zależy poprawność działania umiejętności.
3. Schemat serwera MCP. Narzędzia, które muszą być udostępnione za pośrednictwem MCP: nazwa, opis (zgodny ze wzorcem „Używaj, gdy...”) oraz schemat parametrów wejściowych.
4. Tłumaczenia międzyagentowe. Wskazówki (w stylu SkillKit) dotyczące mapowania pliku SKILL.md na formaty reguł Cursora (`.cursorrules`), Codexu (`.codex.md`) oraz Windsurfa.
5. Konfiguracja ścieżek wyszukiwania. Lokalizacje, w których agenci będą szukać pakietu (np. `~/.anthropic/skills/`, `./skills/`, `~/.claude/skills/`).

Kategoryczne odrzucenia:
- Dowolny plik SKILL.md, którego pole `name` nie jest zapisane w formacie `kebab-case` (blokuje to autowykrywanie).
- Dowolny plik SKILL.md bez pola `description` zdefiniowanego w nagłówku YAML (środowiska uruchomieniowe pomijają takie pliki).
- Dowolny pakiet, którego powiązane narzędzia MCP nie są nazwane zgodnie z zasadami Fazy 13 · 05.

Reguły odmowy:
- Jeśli przepływ pracy sprowadza się do pojedynczego, prostego polecenia, odrzuć projekt dedykowanej umiejętności i zalecaj bezpośrednie formułowanie promptów (inline prompt engineering).
- Jeśli proces wymaga uwierzytelniania protokołem OAuth (np. publikowanie wiadomości na Slacku), wskaż, że autoryzacja musi być obsłużona podczas pierwszego wywołania serwera MCP.
- Jeśli docelowe systemy agentowe nie wspierają bezpośrednio standardu SKILL.md, zalecaj automatyczne tłumaczenie z użyciem narzędzia SkillKit.

Format wyjściowy: Jednostronicowy pakiet zawierający trzy szkice plików konfiguracyjnych, wykaz reguł mapowania dla różnych agentów oraz zdefiniowane ścieżki wyszukiwania. Na końcu wskaż jedno, konkretne środowisko agentowe, w którym należy przeprowadzić pierwsze testy pakietu.
