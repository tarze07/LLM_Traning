---

name: terminal-coding-agent
description: Zbuduj i oceń natywnego dla terminala agenta kodującego w porównaniu z SWE-bench Pro z ograniczonym kosztem, narzędziami w trybie piaskownicy i pełną powierzchnią haków na rok 2026.
version: 1.0.0
phase: 19
lesson: 01
tags: [capstone, coding-agent, claude-code, swe-bench, mcp, hooks, sandbox]

---

Mając docelowe repozytorium i zadanie w języku naturalnym, zbuduj uprząż, która planuje, wykonuje w piaskownicy i otwiera żądanie ściągnięcia. Dorównaj lub pobij poziom bazowy mini-swe-agent w podzbiorze SWE Bench Pro składającym się z 30 zadań, utrzymując budżet poniżej 5 USD na zadanie.

Plan budowy:

1. Stwórz uprząż TUI Bun + Ink z panelem planu, strumieniem wywołań narzędzi i bieżącym budżetem tokenów/dolarów.
2. Zdefiniuj sześć narzędzi (read_file, edit_file, ripgrep, Tree_sitter_symbols, run_shell, git) za pośrednictwem protokołu Model Context Protocol StreamableHTTP. Każde połączenie zwraca co najwyżej 4 tys. tokenów.
3. Uruchom każde wywołanie narzędzia w piaskownicy E2B lub Daytona na świeżej gałęzi `git worktree add`. Nigdy nie dotykaj systemu plików hosta.
4. Połącz wszystkie osiem zdarzeń haków 2026: SessionStart, SessionEnd, PreToolUse, PostToolUse, UserPromptSubmit, Notification, Stop, PreCompact. Wyślij co najmniej cztery hooki stworzone przez użytkownika (ochrona poleceń niszczących, księgowanie tokenów, emiter zakresu Otel, moduł zapisujący pakiety śledzenia).
5. Egzekwuj trzy budżety: 50 tur, 200 tys. tokenów, 5 dolarów. PreCompact strzela przy 150 tys. i podsumowuje starsze zakręty.
6. Emituj zakresy OpenTelemetry z konwencjami semantycznymi GenAI do hostowanego przez siebie Langfuse.
7. Jeśli się powiedzie, popchnij gałąź i otwórz PR z pakietem planu i śledzenia w treści.
8. Oceń działanie mini-swe-agenta w podzbiorze Pro Python z 30 wydaniami w środowisku SWE i zapisz pass@1, tury, tokeny i dolary na zadanie.

Rubryka oceny:

| Waga | Kryterium | Pomiar |
|:-:|---|---|
| 25 | SWE-bench Pro pass@1 | Dopasowany podzbiór 30 zadań w porównaniu z wartością bazową mini-swe-agent |
| 20 | Przejrzystość architektury | Rozdzielenie planu/działania/obserwowania, powierzchnia haka, czytelność schematu narzędzia |
| 20 | Bezpieczeństwo | Ucieczka z piaskownicy z drużyny czerwonej + audyt straży dowodzenia niszczycielskiego |
| 20 | Obserwowalność | 100% wywołań narzędzi w całym okresie, rozliczanie tokenów na turę |
| 15 | Programista UX | Zimny ​​start poniżej 2 s, odzyskiwanie po awarii, Ctrl-C semantyka anulowania |

Twarde odrzucenia:

- Uprząż, która umożliwia git w systemie plików hosta zamiast w piaskownicy.
- Dowolny agent, który może pisać poza drzewem roboczym lub zwijać zewnętrzne adresy URL bez wyraźnego przechwytywania listy dozwolonych.
- Liczby ewaluacyjne zgłoszone bez dopasowanego przebiegu bazowego dla tych samych 30 problemów.
- Twierdzenia „Współczynnik zdawalności” zależne od `git reset --hard` pomiędzy ponownymi próbami; SWE-bench Pro to pass@1.

Zasady odmowy:

- Odmawiaj wypychania bezpośrednio do głównego w dowolnej konfiguracji. Tylko oddziały PR.
- Odmów wyłączenia strażnika dowodzenia niszczycielskiego. Jest to twardy wymóg rubryki.
- Odmówić startu bez pułapu budżetowego. Przebiegi otwarte zanieczyszczają porównanie eval.

Dane wyjściowe: repozytorium zawierające wiązkę przewodów, stała wiązka SWE-bench Pro eval z 30 zadaniami z dopasowanym przebiegiem bazowym mini-swe-agent, archiwum śledzenia OpenTelemetry dla co najmniej 5 pełnych przebiegów oraz zapis nazewnictwa zadań, które wiązka rozwiązuje, a których nie rozwiązuje linia bazowa i odwrotnie. Zakończ sekcją dotyczącą trzech głównych trybów awarii, które zaobserwowałeś, oraz zmianą zaczepu, która naprawiła każdy z nich.