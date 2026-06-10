---

name: claude-agent-scaffold
description: Stwórz szkielet aplikacji Claude Agent SDK z podagentami, hakami cyklu życia, magazynem sesji, przyłączem serwera MCP i propagacją śledzenia W3C.
version: 1.0.0
phase: 14
lesson: 17
tags: [claude-agent-sdk, subagents, hooks, session-store, mcp]

---

Mając domenę produktu i listę serwerów MCP, zbuduj aplikację Claude Agent SDK.

Wyprodukuj:

1. Definicja głównego agenta z instrukcjami, wbudowany dostęp do narzędzi (plik_odczytu, plik_zapisu, powłoka, grep, glob, pobieranie z Internetu) i narzędzia funkcji niestandardowych.
2. Spawnik podagentów do równoległości i izolacji kontekstu. Użyj, gdy orkiestrator w przeciwnym razie zmarnowałby budżet kontekstowy.
3. Zarejestrowano hooki cyklu życia: PreToolUse + PostToolUse do audytu, SessionStart do konfiguracji, SessionEnd do rozłączania, UserPromptSubmit do egzekwowania reguł (zobacz wzorce pro-workflow).
4. Magazyn sesji (domyślnie SQLite) z podłączonym `list_subkeys` w celu renderowania drzewa podagentów.
5. Przyłączenie serwera MCP do zewnętrznych powierzchni narzędzi/zasobów.
6. Propagacja kontekstu śledzenia W3C, tak aby zakresy Otel od osoby wywołującej były kontynuowane przez CLI.

Twarde odrzucenia:

- Tworzenie subagenta dla zadania z jednym narzędziem. Podagenci służą do równoległości lub izolacji kontekstu; nie dla „jednego wywołania pliku read_file”.
- Haki z synchroniczną, kosztowną pracą. Hooki powinny mieć długość od mikrosekund do milisekund. Długa praca należy do subagenta.
- Magazyny sesji bez polityki usuwania kaskadowego. Osierocone sesje podagentów powodują nadmierne przechowywanie danych.

Zasady odmowy:

- Jeśli produkt wymaga długotrwałej pracy asynchronicznej (z godzin na dni), odrzuć pakiet SDK na własnym serwerze i kieruj się do agentów zarządzanych Claude.
- Jeśli użytkownik poprosi o `--session-mirror` do udostępnionej lokalizacji, odmów. Transkrypcje sesji zawierają informacje umożliwiające identyfikację; lustro do zaszyfrowanej pamięci dla poszczególnych użytkowników.
- Jeśli agent polega na surowym przesyłaniu strumieniowym LLM dla UX bez użycia narzędzi, odrzuć pakiet SDK agenta i poleć bezpośrednio zestaw SDK klienta.

Dane wyjściowe: `agent.py`, `tools.py`, `hooks.py`, `session.py`, `README.md` wyjaśniające politykę podagentów, rejestr haków, zaplecze sesji, załączniki MCP i okablowanie Otel. Zakończ słowami „Co dalej czytać”, wskazując Lekcję 22 dotyczącą przekazywania głosu, Lekcję 23 dotyczącą przypisania zakresu Otel lub Lekcję 18, jeśli produkt wymaga kształtu środowiska wykonawczego.