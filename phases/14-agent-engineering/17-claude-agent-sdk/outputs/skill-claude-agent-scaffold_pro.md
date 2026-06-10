---

name: claude-agent-scaffold
description: Stwórz szkielet aplikacji Claude Agent SDK z podagentami, hakami cyklu życia, magazynem sesji, integracją z serwerem MCP i propagacją kontekstu śledzenia W3C.
version: 1.0.0
phase: 14
lesson: 17
tags: [claude-agent-sdk, subagents, hooks, session-store, mcp]

---

Na podstawie domeny produktu i listy serwerów MCP zbuduj aplikację korzystającą z Claude Agent SDK.

Wyprodukuj:

1. Definicję głównego agenta wraz z instrukcjami, wbudowanym dostępem do narzędzi (odczyt/zapis plików, powłoka systemowa, grep, glob, pobieranie z Internetu) oraz własnymi narzędziami funkcyjnymi.
2. Moduł uruchamiania (spawnera) podagentów w celu zapewnienia równoległości i izolacji kontekstu. Używaj go w sytuacjach, gdy główny koordynator (orkiestrator) bezpotrzebnie zużywałby limit okna kontekstowego.
3. Zarejestrowane haki (hooks) cyklu życia: `PreToolUse` i `PostToolUse` do audytu operacji, `SessionStart` do konfiguracji początkowej, `SessionEnd` do zamykania sesji oraz `UserPromptSubmit` do walidacji reguł (zgodnie ze wzorcami zaawansowanych przepływów pracy - pro-workflow).
4. Magazyn sesji (domyślnie SQLite) z obsługą metody `list_subkeys` w celu wizualizacji drzewa podagentów.
5. Integrację z serwerem MCP w celu uzyskania dostępu do zewnętrznych narzędzi i zasobów.
6. Propagację kontekstu śledzenia W3C, zapewniającą ciągłość spanów OpenTelemetry (OTel) z procesu wywołującego do podprocesu CLI.

Kategoryczne odrzucenia (Twarde kryteria):

- Tworzenie podagenta dla pojedynczej operacji narzędziowej. Podagenci powinni być używani do równoległego wykonywania zadań lub izolacji kontekstu, a nie do wywoływania pojedynczych akcji, takich jak np. `read_file`.
- Implementowanie w hakach czasochłonnych, synchronicznych operacji. Czas wykonania haka powinien mieścić się w przedziale mikro- lub milisekund. Długotrwałe zadania powinny być zlecane podagentom.
- Stosowanie magazynów sesji bez mechanizmu kaskadowego usuwania. Pozostawianie osieroconych sesji podagentów prowadzi do niepotrzebnego gromadzenia danych.

Zasady odmowy wykonania usługi (Refusal rules):

- Jeśli produkt wymaga długotrwałego, asynchronicznego działania (od kilku godzin do kilku dni), odmów wdrożenia z użyciem SDK na własnej infrastrukturze i skieruj użytkownika do usługi Claude Managed Agents.
- Jeśli użytkownik żąda zapisu lustrzanego sesji (`--session-mirror`) do współdzielonego katalogu, odmów. Transkrypcje sesji zawierają dane osobowe (PII) – zapisy lustrzane powinny trafiać wyłącznie do zaszyfrowanego, dedykowanego obszaru pamięci użytkownika.
- Jeśli agent ma jedynie przesyłać strumieniowo odpowiedzi z LLM do interfejsu użytkownika bez korzystania z żadnych narzędzi, odmów wdrożenia Agent SDK i zarekomenduj bezpośrednie użycie Client SDK.

Pliki wynikowe: `agent.py`, `tools.py`, `hooks.py`, `session.py`, `README.md` wyjaśniające zasady zarządzania podagentami, rejestrację haków, backend sesji, integrację z MCP oraz konfigurację OpenTelemetry. Zakończ sekcją „Dalsza lektura”, wskazując na Lekcję 22 (obsługa głosu), Lekcję 23 (konfiguracja i propagacja spanów OTel) lub Lekcję 18 (wybór środowiska uruchomieniowego).
