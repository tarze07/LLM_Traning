# Capstone 01 — Agent kodowania natywnego dla terminala

> Do 2026 roku zostanie ustalony kształt agenta kodującego. Uprząż TUI, plan stanowy, powierzchnia narzędzia w piaskownicy, pętla, która planuje, działa, obserwuje, odzyskuje siły. Claude Code, Cursor 3 i OpenCode wyglądają tak samo z odległości 15 metrów. To zwieńczenie wymaga zbudowania jednego kompleksu — wejścia CLI, wysłania żądania — i porównania go z mini-swe-agentem i Live-SWE-agentem na SWE-bench Pro. Dowiesz się, dlaczego najtrudniejszą częścią nie jest wywołanie modelu, ale pętla narzędzia, piaskownica i pułap kosztów w ciągu 50 tur.

**Typ:** Zwieńczenie
**Języki:** TypeScript / Bun (uprząż), Python (skrypty eval)
**Wymagania wstępne:** Faza 11 (inżynieria LLM), Faza 13 (narzędzia i protokoły), Faza 14 (agenci), Faza 15 (systemy autonomiczne), Faza 17 (infrastruktura)
**Wykonywane fazy:** P0 · P5 · P7 · P10 · P11 · P13 · P14 · P15 · P17 · P18
**Czas:** 35 godzin

## Problem

Agenci kodujący stali się dominującą kategorią aplikacji AI w 2026 r. Claude Code (Anthropic), Cursor 3 z Composer 2 i Agent Tabs (Cursor), Amp (Sourcegraph), OpenCode (112 tys. gwiazdek), Factory Droids i Google Jules – wszystkie wersje tej samej architektury: wiązka terminali, powierzchnia narzędzia z uprawnieniami, piaskownica i pętla „planuj – działaj – obserwuj” zbudowana wokół modelu granicznego. Granica jest wąska — agent Live-SWE osiągnął 79,2% na platformie SWE Verified with Opus 4.5 — ale dziedzina inżynierii jest szeroka. Większość trybów awarii nie jest błędami modelu. Należą do nich niestabilność pętli narzędzi, zatruwanie kontekstu, niekontrolowany koszt tokena i destrukcyjne operacje na systemie plików.

Nie można myśleć o tych agentach z zewnątrz. Musisz go zbudować, obejrzeć awarię pętli w 47. turze, gdy ripgrep zwróci 8 MB dopasowań, i odbudować warstwę obcięcia. Taki jest sens tego zwieńczenia.

## Koncepcja

Uprząż ma cztery powierzchnie. **Plan** utrzymuje obiekt stanu w stylu TodoWrite, który model zapisuje w każdej turze. **Act** wywołuje wywołania narzędzi (czytaj, edytuj, uruchamiaj, szukaj, git). **Observe** przechwytuje kody stdout / stderr / wyjścia, obcina i wyświetla podsumowanie. **Recover** obsługuje błędy narzędzi bez otwierania okna kontekstowego i ciągłego zapętlania. Kształt 2026 dodaje jeszcze jedną rzecz: **haczyki**. `PreToolUse`, `PostToolUse`, `SessionStart`, `SessionEnd`, `UserPromptSubmit`, `Notification`, `Stop` i `PreCompact` — konfigurowalne punkty rozszerzeń, w których operator wprowadza zasady, dane telemetryczne i poręcze.

Piaskownica to E2B lub Daytona. Każde zadanie działa w świeżym kontenerze deweloperskim z zamontowanym w drzewie roboczym git modułem odczytu i zapisu. Uprząż nigdy nie dotyka systemu plików hosta. Drzewo pracy zostaje zniszczone w przypadku sukcesu lub porażki. Kontrola kosztów jest egzekwowana na trzech poziomach: limit żetonów na turę, budżet w dolarach na sesję i twardy limit tur (zwykle 50). Warstwa obserwowalności to zakresy OpenTelemetry z konwencjami semantycznymi GenAI, dostarczane do hostowanego przez siebie Langfuse.

## Architektura

```
  user CLI  ->  harness (Bun + Ink TUI)
                  |
                  v
           plan / act / observe loop  <--->  Claude Sonnet 4.7 / GPT-5.4-Codex / Gemini 3 Pro
                  |                          (via OpenRouter, model-agnostic)
                  v
           tool dispatcher (MCP StreamableHTTP client)
                  |
     +------------+------------+----------+
     v            v            v          v
  read/edit    ripgrep     tree-sitter   git/run
     |            |            |          |
     +------------+------------+----------+
                  |
                  v
           E2B / Daytona sandbox  (worktree isolated)
                  |
                  v
           hooks: Pre/Post, Session, Prompt, Compact
                  |
                  v
           OpenTelemetry -> Langfuse (spans, tokens, $)
                  |
                  v
           PR via GitHub app
```

## Stos

- Czas działania uprzęży: Bun 1.2 + Atrament 5 (reagowanie w terminalu)
- Dostęp do modelu: zunifikowany API OpenRouter z Claude Sonnet 4.7, GPT-5.4-Codex, Gemini 3 Pro, Opus 4.5 (do najcięższych zadań)
- Tool transport: Model Context Protocol StreamableHTTP (MCP 2026 revision)
- Sandbox: E2B sandboxes (JS SDK) or Daytona devcontainers
- Wyszukiwanie kodu: podproces ripgrep, parsery nadzorujące drzewo dla 17 języków (wstępnie skompilowane)
- Izolacja: `git worktree add` na zadanie, czyszczenie w przypadku sukcesu/porażki
- Uprząż Eval: SWE-bench Pro (zweryfikowany podzbiór) + Terminal-Bench 2.0 + własny zestaw 30 zadań
- Obserwowalność: OpenTelemetry SDK z `gen_ai.*` semconv → hostowany Langfuse
- Publikacja PR: aplikacja GitHub z precyzyjnym tokenem, zakres ograniczony do docelowego repozytorium

## Zbuduj to

1. **TUI i pętla poleceń.** Stwórz projekt Bun za pomocą Ink. Zaakceptuj `agent run <repo> "<task>"`. Wydrukuj podzielony widok: panel planu (na górze), strumień wywołań narzędzi (na środku), budżet tokenów (na dole). Dodaj anulowanie na Ctrl-C, które uruchamia hak `SessionEnd` przed wyjściem.

2. **Stan planu.** Zdefiniuj wpisany schemat TodoWrite (oczekujące / w toku / elementy wykonane z notatkami). Model zapisuje pełny stan w każdej turze jako wywołanie narzędzia — nie pozwól, aby mutował stopniowo. Utrzymaj plan `.agent/state.json`, aby awarie mogły zostać wznowione.

3. **Powierzchnia narzędzia.** Zdefiniuj sześć narzędzi: `read_file`, `edit_file` (z podglądem różnicowym), `ripgrep`, `tree_sitter_symbols`, `run_shell` (z limitem czasu), `git` (status / różnica / zatwierdzenie / push). Wystaw na MCP StreamableHTTP, aby uprząż była niezależna od transportu. Każde narzędzie zwraca obcięte dane wyjściowe (ograniczenie do 4 tys. tokenów na wywołanie).

4. **Owijanie piaskownicy.** Każde zadanie tworzy piaskownicę E2B. `git worktree add -b agent/$TASK_ID` świeża gałąź. Wszystkie wywołania narzędzi są wykonywane wewnątrz piaskownicy. System plików hosta jest nieosiągalny.

5. **Haki.** Zastosuj wszystkie osiem typów haków 2026. Podłącz co najmniej cztery zaczepy autorstwa użytkownika: (a) `PreToolUse` ochrona poleceń niszczących, która blokuje `rm -rf` poza drzewem roboczym, (b) `PostToolUse` księgowanie tokenów, (c) `SessionStart` inicjalizacja budżetu, (d) `Stop` zapisuje końcowy pakiet śledzenia.

6. **Pętla Eval.** Sklonuj 30-wydaniowy podzbiór SWE-bench Pro Python. Nasuń uprząż na każdy z nich. Porównaj z mini-swe-agentem (minimalna linia bazowa) w przypadku pass@1, obrotów na zadanie i $ na zadanie. Zapisz wyniki w `eval/results.jsonl`.

7. **Kontrola kosztów.** Ostateczne limity: 50 tur, kontekst 200 tys., 5 USD za zadanie. Hak `PreCompact` podsumowuje starsze zwroty w blok stanu poprzedniego na poziomie 150 tys., uwalniając miejsce na nowe obserwacje bez utraty planu.

8. **Opublikowanie PR.** Po pomyślnym zakończeniu ostatnim krokiem jest `git push` + wywołanie API GitHub, które otwiera PR z planem i podsumowaniem różnic w treści.

## Użyj tego

```
$ agent run ./my-repo "Fix the race condition in worker.rs"
[plan]  1 locate worker.rs and enumerate mutex uses
        2 identify shared state under contention
        3 propose fix, verify tests
[tool]  ripgrep mutex.*lock -t rust           (44 matches, truncated)
[tool]  read_file src/worker.rs 120..180
[tool]  edit_file src/worker.rs (+8 -3)
[tool]  run_shell cargo test worker::          (passed)
[plan]  1 done · 2 done · 3 done
[done]  PR opened: #482   turns=9   tokens=38k   cost=$0.41
```

## Wyślij to

Dostarczona umiejętność znajduje się w `outputs/skill-terminal-coding-agent.md`. Mając ścieżkę do repozytorium i opis zadania, uruchamia pełną pętlę „planuj – działaj – obserwuj” w piaskownicy i zwraca adres URL PR oraz pakiet śledzenia. Rubryka tego zwieńczenia:

| Waga | Kryterium | Jak to się mierzy |
|:-:|---|---|
| 25 | SWE-bench Pro pass@1 vs poziom bazowy | Twoja uprząż kontra mini-swe-agent w 30 dopasowanych zadaniach w Pythonie |
| 20 | Przejrzystość architektury | Zaplanuj/działaj/obserwuj separację, powierzchnię haka, schemat narzędzia — porównano z układem agenta Live-SWE |
| 20 | Bezpieczeństwo | Testy ucieczki z piaskownicy, monity o pozwolenie, dowodzenie niszczycielskie przechodzi przez drużynę czerwoną |
| 20 | Obserwowalność | Kompletność śledzenia (100% wszystkich wywołań narzędzi), rozliczanie tokenów na turę |
| 15 | Programista UX | Zimny ​​​​start < 2 s, przywracanie planu odzyskiwania po awarii, Ctrl-C anuluje w połowie narzędzia |
| **100** | | |

## Ćwiczenia

1. Zamień model podkładowy z Claude Sonnet 4.7 na Qwen3-Coder-30B udostępniany na vLLM. Porównaj pass@1 i $-per-zadanie. Zgłaszaj, gdzie model otwarty osiąga gorsze wyniki.

2. Dodaj subagenta `reviewer`, który odczytuje różnicę przed opublikowaniem PR i może poprosić o pętlę poprawek. Zmierz, czy fałszywie pozytywne recenzje obniżą wskaźnik zdawalności testów SWE poniżej poziomu bazowego w przypadku pojedynczego agenta (wskazówka: zwykle tak).

3. Przetestuj piaskownicę: napisz zadanie próbujące `curl` zewnętrzny adres URL i zadanie zapisujące poza drzewem roboczym. Upewnij się, że oba są zablokowane przez hak PreToolUse. Rejestruj próby.

4. Zaimplementuj `PreCompact` podsumowanie z mniejszym modelem (Haiku 4.5). Zmierz, ile wierności planu zostało utracone przy 3-krotnym zagęszczeniu.

5. Zamień transport MCP StreamableHTTP na stdio. Test porównawczy zimnego startu i opóźnienia poszczególnych połączeń. Wybierz zwycięzcę do użytku wyłącznie lokalnego.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| Uprząż | „Pętla agenta” | Kod otaczający model, który uruchamia narzędzia, utrzymuje stan planu i wymusza budżety |
| Hak | „Odbiornik zdarzeń agenta” | Skrypt autorstwa użytkownika uruchamiany na jednym z ośmiu zdarzeń cyklu życia przez wiązkę |
| Drzewo pracy | „Piaskownica Git” | Połączona kasa git w osobnej ścieżce; jednorazowe bez dotykania głównego klonu |
| Do zrobieniaNapisz | „Stan planu” | Wpisana lista elementów oczekujących/w toku/ukończonych, które model przepisuje w każdej turze |
| StreamableHTTP | „Transport MCP” | Wersja MCP 2026: długotrwałe połączenie HTTP z dwukierunkowym przesyłaniem strumieniowym; zastępuje SSE |
| Żetonowy sufit | „Budżet kontekstowy” | Limit na turę lub sesję na żetonach wejścia i wyjścia; powoduje zagęszczenie lub zakończenie |
| pass@1 | „Współczynnik zaliczenia pojedynczej próby” | Część zadań w środowisku SWE rozwiązanych przy pierwszym uruchomieniu bez konieczności ponawiania prób lub podglądania zestawu testowego |

## Dalsze czytanie

- [Dokumentacja Claude Code](https://docs.anthropic.com/en/docs/claude-code) — uprząż referencyjna firmy Anthropic
– [Dziennik zmian Cursor 3](https://cursor.com/changelog) — Karty agentów i uwagi o produkcie Composer 2
– [mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent) — minimalna wartość bazowa dla porównania uprzęży SWE-bench
- [Live-SWE-agent](https://github.com/OpenAutoCoder/live-swe-agent) — 79,2% SWE-bench zweryfikowane w Opus 4.5
- [OpenCode](https://opencode.ai) — otwarta uprząż, 112 tys. gwiazdek
– [Tablica wyników SWE-bench Pro](https://www.swebench.com) — ocena, której celem jest to podsumowanie
— [Plan działania dotyczący protokołu Model Context Protocol na 2026 r.](https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/) — StreamableHTTP, metadane możliwości
- [Konwencje semantyczne OpenTelemetry GenAI](https://opentelemetry.io/docs/specs/semconv/gen-ai/) — schemat rozpiętości wywołań narzędzi i użycia tokenów