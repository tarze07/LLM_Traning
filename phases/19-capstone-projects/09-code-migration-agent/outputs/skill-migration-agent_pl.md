---

name: migration-agent
description: Zbuduj agenta migracji kodu na poziomie repozytorium, który łączy deterministyczne receptury z pętlą awaryjną agenta, przechodzi MigrationBench i publikuje taksonomię błędów.
version: 1.0.0
phase: 19
lesson: 09
tags: [capstone, code-migration, openrewrite, libcst, migrationbench, agent, sandbox]

---

Mając repozytorium Java 8 lub Python 2, utwórz migrowaną gałąź (do Java 17 lub Python 3.12) z zielonym zestawem testów i minimalną regresją pokrycia. Oceń w podzbiorze MigrationBench obejmującym 50 repozytoriów.

Plan budowy:

1. Przejście deterministyczne: OpenRewrite (Java) lub libcst (Python) najpierw uruchamia mechaniczne przepisywanie. Zatwierdź jako „przepis” z czystą różnicą.
2. Sandbox Daytona: preinstalowane docelowe środowisko wykonawcze; kompilacja na oddział; montowanie źródła tylko do odczytu.
3. Pętla agenta: LangGraph lub OpenAI Agents SDK na Claude Opus 4.7 + GPT-5.4-Codex. Narzędzia: `run_build`, `read_file`, `edit_file`, `run_test`, `git_diff`. Sklasyfikuj awarię (dep, składnia, test, narzędzie do kompilacji), zastosuj ukierunkowaną poprawkę, uruchom ponownie.
4. Limity budżetu: 30 minut, 8 dolarów, 20 tur. Naruszenie jakichkolwiek zatrzymań i plików pod `budget_exhausted` przy bieżącej różnicy.
5. Test + bramka zasięgu: zbuduj ekologicznie, a następnie testuj ekologicznie; zasięg nie może spaść o więcej niż 2%.
6. Otwarcie PR z zatwierdzeniem przepisu + zatwierdzeniem agenta + komentarzem podsumowującym.
7. Taksonomia niepowodzeń: znacznik per-repo z `{dep_upgrade_required, build_tool_drift, custom_annotation, test_flake, syntax_edge_case, budget_exhausted, coverage_regression}`.
8. Przebieg 50 repo w MigrationBench; publikuj współczynnik zdawalności na zajęcia, koszt repo i zachowanie zasięgu; porównanie z deterministyczną linią bazową.

Rubryka oceny:

| Waga | Kryterium | Pomiar |
|:-:|---|---|
| 25 | Wskaźnik zdawalności MigrationBench | Podzbiór 50 repozytoriów pass@1 |
| 20 | Zachowanie pokrycia testowego | Średnia delta pokrycia w stosunku do gałęzi podstawowej |
| 20 | Koszt migrowanego repozytorium | Średnie $/repo przy przechodzących biegach |
| 20 | Integracja agenta / narzędzia deterministycznego | Część poprawek obsługiwanych przez OpenRewrite w porównaniu z agentem |
| 15 | Zapis analizy awarii | Kompletność taksonomii z przykładami |

Twarde odrzucenia:

- Rurociągi, które pomijają przejście deterministyczne. OpenRewrite obsługuje mechanizmy mechaniczne 70-80% taniej i bardziej niezawodnie niż jakikolwiek inny agent.
- Regresje pokrycia powyżej 2% traktowane jako przemijające.
- PR, które łączą zmiany mechaniczne i stworzone przez agenta w jedno zatwierdzenie. Należy rozdzielić.
- Raportowanie współczynnika pomyślności bez dopasowanej, deterministycznej linii bazowej w tych samych 50 repozytoriach.

Zasady odmowy:

- Odmawiaj wpychania na siłę migrowanej gałęzi przez bazę. Zawsze nowy oddział + PR.
- Odmów otwarcia PR, którego CI nie zmienił koloru na zielony w piaskownicy.
- Odmawiaj uruchamiania na korporacyjnych repozytoriach bez wyraźnej licencji na modyfikację.

Dane wyjściowe: repozytorium zawierające dwuwarstwowy potok migracji, 50 repozytoriów dzienników uruchomień MigrationBench, pulpit nawigacyjny taksonomii błędów, dopasowany przebieg bazowy wyłącznie deterministyczny oraz opis trzech najpopularniejszych klas błędów i zmiany receptury, która eliminuje każdą z nich.