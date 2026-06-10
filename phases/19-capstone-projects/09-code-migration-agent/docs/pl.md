# Capstone 09 — Agent migracji kodu (język na poziomie repo/aktualizacja środowiska wykonawczego)

> MigrationBench firmy Amazon (Java 8–17) i migrator Py2-to-Py3 firmy Google App Engine wyznaczają poprzeczkę na rok 2026. OpenRewrite firmy Moderne wykonuje deterministyczne przepisywanie AST na dużą skalę. Grit ma na celu ten sam problem z DSL w stylu codemod. Wzorzec produkcyjny łączy w sobie oba: deterministyczne podłoże do bezpiecznego przepisywania plus warstwę agenta dla niejednoznacznych przypadków, piaskownicę do kompilacji dla poszczególnych gałęzi oraz okablowanie testowe, które zmienia kolor na zielony przed otwarciem PR. Zwieńczeniem jest migracja 50 prawdziwych repozytoriów i opublikowanie współczynnika pomyślności z taksonomią błędów.

**Typ:** Zwieńczenie
**Języki:** Python (agent), Java / Python (obiekty docelowe), TypeScript (pulpit nawigacyjny)
**Wymagania wstępne:** Faza 5 (NLP), Faza 7 (transformatory), Faza 11 (inżynieria LLM), Faza 13 (narzędzia), Faza 14 (agenci), Faza 15 (autonomia), Faza 17 (infrastruktura)
**Wykonywane fazy:** P5 · P7 · P11 · P13 · P14 · P15 · P17
**Czas:** 30 godzin

## Problem

Migracja kodu na dużą skalę to jedno z najczystszych zastosowań produkcyjnych agentów kodujących 2026. Podstawowa prawda jest oczywista (czy zestaw testów przejdzie po migracji?), nagrody są realne (migracja floty Java-8 to projekt obejmujący skalę zatrudnienia), a testy porównawcze są publiczne (podzbiór 50 repozytoriów MigrationBench). OpenRewrite firmy Moderne obsługuje stronę deterministyczną. Warstwa agenta obsługuje wszystko, czego nie mogą receptury OpenRewrite: niejednoznaczne przepisywanie, dryf systemu kompilacji, składnię długiego ogona, łamanie zależności przechodnich.

Zbudujesz agenta, który pobiera repozytorium Java 8 (lub repozytorium Python 2) i tworzy migrowaną gałąź zielonego CI. Zmierzysz współczynnik zdawalności, zachowanie zasięgu testów, koszt repozytorium i zbudujesz taksonomię niepowodzeń. Porównanie z deterministyczną linią bazową informuje, gdzie faktycznie znajduje się wartość agenta.

## Koncepcja

Rurociąg ma dwie warstwy. **Deterministyczne podłoże** (OpenRewrite dla Java, libcst dla Pythona) bezpiecznie obsługuje większość mechanicznych zapisów: importy, podpisy metod, edycje zapewniające bezpieczeństwo zerowe, wypróbowanie z zasobami, przestarzałe zamienniki API. Jest szybki i generuje kontrolowane różnice. **Warstwa agenta** (OpenAI Agents SDK lub LangGraph nad Claude Opus 4.7 i GPT-5.4-Codex) obsługuje przypadki, których nie mogą receptury: aktualizacje plików kompilacji (Maven/Gradle/pyproject), przechodnie konflikty zależności, płatki testowe, niestandardowe adnotacje.

Każde repozytorium otrzymuje piaskownicę Daytona z preinstalowanym docelowym środowiskiem wykonawczym. Agent wykonuje iteracje: uruchom kompilację, klasyfikuj błędy, zastosuj poprawkę, uruchom ponownie. Twarde limity: 30 minut na repo, 8 dolarów na repo, 20 tur agentów. Jeśli wszystkie testy zakończą się pomyślnie, a delta pokrycia nie będzie ujemna, oddział otwiera PR. Jeśli nie, repo zostanie umieszczone w klasie niepowodzeń wraz z dowodami.

Rezultatem jest taksonomia niepowodzeń. Co się zepsuło w 50 repozytoriach? Depta przejściowa? Niestandardowe adnotacje? Zbuduj wersję narzędzia? Płatki testowe niezwiązane z migracją? Każda klasa otrzymuje liczbę i przykładową różnicę. Przyszli autorzy przepisów mogą kierować reklamy do trzech najlepszych.

## Architektura

```
target repo
      |
      v
OpenRewrite / libcst deterministic recipes
   (safe, fast, auditable, ~70-80% of fixes)
      |
      v
Daytona sandbox per branch
      |
      v
agent loop (Claude Opus 4.7 / GPT-5.4-Codex):
   - run build -> capture failures
   - classify failures (build, test, lint)
   - apply fix (patch or retry recipe)
   - rerun
   - budget: 30 min, $8, 20 turns
      |
      v
test + coverage delta gate
      |
      v (passed)
open PR
      |
      v (failed)
file under failure class + attach repro
```

## Stos

- Podłoże deterministyczne: OpenRewrite (Java) lub libcst (Python)
- Agent: OpenAI Agents SDK lub LangGraph na Claude Opus 4.7 + GPT-5.4-Codex
- Sandbox: kontenery deweloperskie Daytona na oddział, preinstalowane docelowe środowisko wykonawcze (Java 17 / Python 3.12)
- Budowa systemów: Maven, Gradle, uv (Python)
- Testy porównawcze: podzbiór 50 repozytoriów Amazon MigrationBench (Java 8 do 17), repozytoria Google App Engine Py2-to-Py3
- Wiązka testowa: prowadnica równoległa, zasięg przez Jacoco (Java) lub zasięg.py (Python)
- Obserwowalność: Langfuse + pakiet śledzenia na repozytorium z każdym fragmentem różnicowym
- Pulpit nawigacyjny: pulpit nawigacyjny taksonomii błędów z licznikami dla poszczególnych klas i przykładowymi różnicami

## Zbuduj to

1. **Karta przepisu.** Najpierw uruchom receptury OpenRewrite (Java) lub libcst (Python). Wychwytuj 70–80% migracji mechanicznych. Zatwierdź jako zatwierdzenie „przepisu”.

2. ** Wersja próbna kompilacji.** Sandbox Daytona: zainstaluj docelowe środowisko wykonawcze, uruchom kompilację. Jeśli jest zielony, przejdź do testów. Jeśli jest czerwony, przekaż agentowi.

3. **Pętla agenta.** LangGraph z narzędziami: `run_build`, `read_file`, `edit_file`, `run_test`, `git_diff`. Agent klasyfikuje awarię (dep, składnia, test, narzędzie do kompilacji) i stosuje ukierunkowaną poprawkę. Ponowne odtworzenie.

4. **Ograniczenia budżetu.** 30 minut zegara ściennego na repo, koszt 8 USD, 20 tur agentów. Wszelkie naruszenia zostaną zatrzymane i zapisane w „budget_exhausted” z bieżącą różnicą.

5. **Test + bramka pokrycia.** Gdy kompilacja stanie się ekologiczna, uruchom zestaw testów. Porównaj pokrycie z bazowym repo. Jeżeli pokrycie spadło o więcej niż 2%, zapisz w sekcji „regresja_pokrycia”.

6. **PR open.** Po pomyślnym przesunięciu gałęzi, otwórz PR z różnicą i podsumowaniem, które przepisy zostały zastosowane i które zatwierdzenia są autorstwa agenta.

7. **Taksonomia niepowodzeń.** Dla każdego nieudanego repozytorium oznacz klasę: `dep_upgrade_required`, `build_tool_drift`, `custom_annotation`, `test_flake`, `syntax_edge_case`, `budget_exhausted`. Zbuduj dashboard.

8. **Przebieg 50 repozytoriów.** Wykonaj w podzbiorze MigrationBench. Raportuj współczynnik zdawalności poszczególnych klas, koszt repo, zachowanie zasięgu i linię bazową zawierającą wyłącznie porównanie i determinizm.

## Użyj tego

```
$ migrate legacy-java-service --target java17
[recipe]   27 rewrites applied (JUnit 4->5, HashMap initializer, try-with-resources)
[build]    FAIL: cannot find symbol sun.misc.BASE64Encoder
[agent]    turn 1 classify: removed_jdk_api
[agent]    turn 2 apply: sun.misc.BASE64Encoder -> java.util.Base64
[build]    OK
[tests]    412/412 passing; coverage 84.1% -> 84.3%
[pr]       opened #1841  cost=$3.20  turns=4
```

## Wyślij to

Elementem dostawy jest `outputs/skill-migration-agent.md`. Mając repozytorium, wykonuje deterministyczne receptury, a następnie pętlę agenta w celu utworzenia zielonej migrowanej gałęzi lub umieszcza repozytorium w klasie taksonomii.

| Waga | Kryterium | Jak to się mierzy |
|:-:|---|---|
| 25 | Wskaźnik zdawalności MigrationBench | Podzbiór 50 repozytoriów pass@1 |
| 20 | Zachowanie pokrycia testowego | Średnia delta pokrycia w porównaniu z bazą |
| 20 | Koszt migrowanego repozytorium | $/repo przy przechodzących biegach |
| 20 | Integracja agenta / narzędzia deterministycznego | Część poprawek obsługiwanych przez OpenRewrite w porównaniu do poprawek stworzonych przez agenta |
| 15 | Zapis analizy awarii | Kompletność taksonomii z przykładami |
| **100** | | |

## Ćwiczenia

1. Uruchom potok migracji tylko za pomocą OpenRewrite (bez agenta). Porównaj współczynnik przepustowości z pełnym potokiem. Zidentyfikuj przypadki, w których sam agent stanowi różnicę.

2. Zaimplementuj kontrolę „czyszczącą”: ​​po migracji uruchom linter stylowy (bez skazy dla Java, ruff dla Pythona). Niepowodzenie PR, jeśli pojawią się nowe błędy lint. Zmierz stopę regresji przy zachowaniu zasięgu, ale w stylu.

3. Dodaj optymalizator „minimal-diff”: po przejściu testów gałęzi agenta usuń niepotrzebne zmiany w drugim przebiegu. Zgłoś zmniejszenie rozmiaru różnic.

4. Rozszerz o trzecią migrację: od węzła 18 do węzła 22. Użyj ponownie opakowania piaskownicy; zamień warstwę przepisu na niestandardowy kodmod.

5. Zmierz czas do pierwszej zielonej kompilacji (TTFGB) jako miarę UX. Cel: p50 poniżej 10 minut.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| Podłoże deterministyczne | „Silnik receptur” | OpenRewrite / libcst: deklaratywne przepisywanie AST z gwarancjami bezpieczeństwa |
| Kodmod | „Program modyfikujący kod” | Reguła przepisywania, która mechanicznie zmienia kod źródłowy |
| Zbuduj dryf | „Pochylenie wersji narzędzia” | Subtelne zmiany zachowania Mavena/Gradle/uv pomiędzy głównymi wersjami |
| Klasa awarii | „Wiadro taksonomii” | Oznaczony powód, dla którego repozytorium nie zostało przeniesione: dep, składnia, test, narzędzie do kompilacji, budżet |
| Delta pokrycia | „Zachowanie zasięgu” | Zmiana % pokrycia testowego z gałęzi podstawowej do gałęzi migrowanej |
| Kolej agenta | „Runda wywołania narzędzia” | Jeden plan -> działanie -> obserwowanie cyklu w pętli agenta |
| Wyczerpanie budżetu | „Uderz w sufit” | Repo wykorzystało limit 30 minut / 8 USD / 20 tur bez przejścia |

## Dalsze czytanie

– [Amazon MigrationBench](https://aws.amazon.com/blogs/devops/amazon-introduces-two-benchmark-datasets-for-evaluating-ai-agents-ability-on-code-migration/) — kanoniczny test porównawczy na rok 2026
- [Platforma Moderne.io OpenRewrite](https://www.moderne.io) — deterministyczne odniesienie do podłoża
- [Dokumentacja OpenRewrite](https://docs.openrewrite.org) — tworzenie receptur
- [Grit.io](https://www.grit.io) — alternatywny mod kodowy DSL
- [Książka kucharska dotycząca migracji w trybie sandbox OpenAI](https://developers.openai.com/cookbook/examples/agents_sdk/sandboxed-code-migration/sandboxed_code_migration_agent) — informacje o pakiecie SDK agentów
- [Migrator Google App Engine Py2 do Py3](https://cloud.google.com/appengine) — alternatywny test porównawczy migracji
- [libcst](https://github.com/Instagram/LibCST) — Deterministyczne podłoże Pythona
- [Piaskownice Daytona](https://daytona.io) — odniesienia do piaskownicy dla poszczególnych oddziałów