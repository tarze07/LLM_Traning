# Capstone 16 — Autonomiczny agent GitHub zajmujący się kwestiami PR

> Zdalni agenci SWE AWS, agenci tła kursora, chmura OpenAI Codex i Google Jules mają ten sam kształt produktu na rok 2026: oznacz problem, zdobądź PR. Uruchom agenta w piaskownicy w chmurze, sprawdź, czy testy przebiegły pomyślnie, i opublikuj gotowy do recenzji PR z uzasadnieniem. Najtrudniejsze części polegają na automatycznym odtwarzaniu środowiska kompilacji repozytorium, zapobieganiu wyciekom danych uwierzytelniających, egzekwowaniu budżetów na repo i upewnianiu się, że agent nie może wymusić wypychania. To zwieńczenie tworzy wersję hostowaną na własnym serwerze i porównuje ją pod względem kosztów i współczynnika przepustowości z hostowanymi alternatywami.

**Typ:** Zwieńczenie
**Języki:** Python (agent), TypeScript (aplikacja GitHub), YAML (akcje)
**Wymagania wstępne:** Faza 11 (inżynieria LLM), Faza 13 (narzędzia), Faza 14 (agenci), Faza 15 (autonomia), Faza 17 (infrastruktura)
**Wykonywane fazy:** P11 · P13 · P14 · P15 · P17
**Czas:** 30 godzin

## Problem

Agent kodujący w chmurze asynchronicznej to odrębna kategoria produktów od interaktywnych agentów kodujących (capstone 01). UX to etykieta GitHuba. Etykietujesz problem `@agent fix this`, pracownik uruchamia się w piaskownicy w chmurze, klonuje repozytorium, uruchamia testy, edytuje pliki, weryfikuje i otwiera żądanie ściągnięcia z uzasadnieniem agenta w treści. Żadnej pętli interaktywnej, żadnego terminala. Zdalni agenci SWE AWS, agenci tła kursora, chmura OpenAI Codex, Google Jules i Factory Droids skupiają się na tym.

Wyzwania inżynieryjne są konkretne: reprodukcja środowiska (agent musi zbudować repo od zera bez buforowanego obrazu dewelopera), niestabilne testy (należy uruchomić ponownie lub odizolować), zakres poświadczeń (aplikacja GitHub z minimalnymi szczegółowymi uprawnieniami), egzekwowanie budżetu na repo dziennie i zasady braku wymuszania wypychania. Zwieńczenie mierzy współczynnik zdawalności, koszt i bezpieczeństwo w porównaniu z hostowanymi alternatywami.

## Koncepcja

Wyzwalaczem jest webhook GitHub (etykieta problemu lub komentarz PR). Dyspozytor kolejkuje pracę do ECS Fargate lub Lambda. Pracownik pobiera repozytorium do piaskownicy Daytona lub E2B za pomocą ogólnego pliku Dockerfile wywnioskowanego z repozytorium (język, framework). Agent uruchamia pętlę mini-swe-agent lub SWE-agent v2 przeciwko Claude Opus 4.7 lub GPT-5.4-Codex. Iteruje: czyta kod, proponuje poprawkę, instaluje łatkę, uruchamia testy.

Weryfikacja jest krokiem bramkowym. Pełny CI musi przejść przez piaskownicę przed otwarciem PR. Obliczana jest delta pokrycia; jeśli wartość ujemna przekracza próg, PR otwiera się, ale zostaje oznaczony etykietą `needs-review`. Agent publikuje uzasadnienie jako opis PR oraz wątek `@agent`, do którego recenzent może wysłać polecenie ping w celu uzyskania dalszych informacji.

Bezpieczeństwo obejmuje dwie różne powierzchnie GitHub: aplikacja zapewnia krótkotrwały token instalacyjny z `workflows: read` i wąskim zakresem treści repo/PR; ochrona gałęzi (nie uprawnienia aplikacji) wymusza „żadnych bezpośrednich zapisów do `main`” i „żadnego wymuszania wypychania” — aplikacja nigdy nie jest dodawana do listy obejść. Dostęp tylko do odczytu z ograniczonym zakresem ścieżki do `.github/workflows` nie jest prawdziwym prymitywem aplikacji GitHub, więc lista dozwolonych edycji plików agenta musi wymuszać to na procesie roboczym. Limity budżetu na repo dziennie są egzekwowane u dyspozytora (np. maksymalnie 5 PR na repo dziennie, 20 $ na PR).

## Architektura

```
GitHub issue labeled `@agent fix` or PR comment
            |
            v
    GitHub App webhook -> AWS Lambda dispatcher
            |
            v
    ECS Fargate task (or GitHub Actions self-hosted runner)
       - pull repo
       - infer Dockerfile (language, package manager)
       - Daytona / E2B sandbox with target runtime
       - clone -> git worktree -> agent branch
            |
            v
    mini-swe-agent / SWE-agent v2 loop
       Claude Opus 4.7 or GPT-5.4-Codex
       tools: ripgrep, tree-sitter, read/edit, run_tests, git
            |
            v
    verify CI passes in-sandbox + coverage delta check
            |
            v (verified)
    git push + open PR via GitHub App
       PR body = rationale + diff summary + trace URL
       label: needs-review
            |
            v
    operator reviews; can @-mention agent for follow-ups
```

## Stos

- Wyzwalacz: aplikacja GitHub z precyzyjnym tokenem; odbiornik webhook za pośrednictwem Lambda lub Fly.io
- Proces roboczy: zadanie ECS Fargate (lub hostowany moduł uruchamiający GitHub Actions)
- Piaskownica: kontener deweloperski Daytona lub piaskownica E2B na zadanie
- Pętla agenta: mini-swe-agent baseline lub SWE-agent v2 na Claude Opus 4.7 / GPT-5.4-Codex
- Pobieranie: mapa repozytorium drzew + ripgrep
- Weryfikacja: pełna CI w piaskownicy + bramka delta zasięgu
- Obserwowalność: Langfuse z archiwum śledzenia PR powiązanym z organem PR
- Budżet: dzienny pułap w dolarach na repo; maksymalne PR na repo dziennie

## Zbuduj to

1. **Aplikacja GitHub.** Szczegółowy token instalacji: problemy z odczytem i zapisem, zapis pull_requests, odczyt i zapis treści, odczyt przepływów pracy. Ochrona gałęzi (jedyna powierzchnia, która może to zrobić) wymusza „żadnego bezpośredniego wypychania do `main`” i „żadnego wypychania na siłę”; aplikacji nie ma na liście obejść. Proces roboczy wymusza „żadnych zapisów w `.github/workflows`” w ramach sprawdzania listy dozwolonych dla proponowanej różnicy, ponieważ uprawnienia aplikacji GitHub nie są ograniczone do ścieżki.

2. **Odbiornik webhooka.** Funkcja Lambda akceptuje webhooki z etykietą wydania / komentarzem PR. Filtruje według etykiety `@agent fix this`. Kolejka do SQS.

3. **Dyspozytor.** Wyskakuje zadania z SQS. Egzekwuje dzienny budżet na repo. Uruchamia zadanie ECS Fargate z adresem URL repozytorium, treścią problemu i nową piaskownicą Daytona.

4. **Wnioskowanie o środowisku.** Wykryj język (Python, Node, Go, Rust) i menedżera pakietów (uv, pnpm, go mod, cargo). Wygeneruj plik Dockerfile na bieżąco, jeśli taki nie istnieje.

5. **Pętla agenta.** mini-swe-agent lub SWE-agent v2 z Claude Opus 4.7. Narzędzia: ripgrep, mapa repozytorium drzewa, plik_odczytu, plik_edycji, testy_run, git. Twarde limity: koszt 20 dolarów, 30-minutowy zegar ścienny, 30 tur agentów.

6. **Weryfikacja.** Po zakończeniu pętli uruchom pełny zestaw testów w piaskownicy. Oblicz różnicę zasięgu za pomocą jacoco / zasięg.py. Jeśli CI jest czerwony: zatrzymaj, nie otwieraj PR. Jeśli zasięg spadnie o więcej niż 2%: otwórz PR z etykietą `needs-review`.

7. **Ogłoszenie PR.** Popchnij gałąź agenta. Otwórz PR poprzez API GitHub z: tytułem, uzasadnieniem, podsumowaniem różnic, adresem URL śledzenia, kosztem, obrotami.

8. **Higiena poświadczeń.** Pracownik działa z krótkotrwałym tokenem instalacyjnym aplikacji GitHub. Przed archiwizacją dzienniki są czyszczone pod kątem tajemnic.

9. **Eval.** 30 rozstawionych problemów wewnętrznych o różnym stopniu trudności. Zmierz współczynnik przepustowości, jakość PR (rozmiar różnicy, styl, zasięg), koszt, opóźnienia. Porównaj z agentami tła kursora i zdalnymi agentami AWS SWE pod kątem tych samych problemów.

## Użyj tego

```
# on github.com
  - user labels issue #842 with `@agent fix this`
  - PR #1903 appears 14 minutes later
  - body:
    > Fixed NPE in widget.dedupe() caused by null comparator entry.
    > Added regression test widget_test.go::TestDedupeNullComparator.
    > Coverage delta: +0.12%
    > Turns: 7  Cost: $1.80  Trace: langfuse:...
    > Label: needs-review
```

## Wyślij to

Elementem dostawy jest `outputs/skill-issue-to-pr.md`. Usługa GitHub App + asynchroniczna chmura robocza, która zamienia oznaczone problemy w komunikaty PR gotowe do przeglądu z ograniczonymi kosztami i poświadczeniami o określonym zakresie.

| Waga | Kryterium | Jak to się mierzy |
|:-:|---|---|
| 25 | Zdawalność w 30 wydaniach | Kompleksowy sukces (CI zielony + zasięg OK) |
| 20 | Jakość PR | Rozmiar różnicy, delta pokrycia, zgodność ze stylem |
| 20 | Koszt i opóźnienie na rozwiązany problem | $ i zegar ścienny na PR |
| 20 | Bezpieczeństwo | Token o określonym zakresie, budżet na repo, brak wymuszania, higiena poświadczeń |
| 15 | UX operatora | Komentarze uzasadniające, możliwość ponownej próby, śledzenie @wzmianek |
| **100** | | |

## Ćwiczenia

1. Dodaj tryb „napraw niestabilny test”: etykieta `@agent stabilize-flake TestX` uruchamia test 50 razy w piaskownicy i proponuje minimalną zmianę, która go stabilizuje.

2. Porównaj koszty z agentami tła kursora w trzech wspólnych kwestiach. Zgłoś, które narzędzia gdzie wygrywają.

3. Zaimplementuj panel budżetu: koszt dzienny za repo, koszt za użytkownika. Alarm w przypadku anomalii.

4. Zbuduj tryb próbny, który otwiera wersję roboczą żądania ściągnięcia bez uruchamiania CI, aby recenzenci mogli tanio sprawdzić plan.

5. Dodaj politykę przechowywania: Oddziały PR starsze niż 7 dni bez połączenia są automatycznie usuwane.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| Aplikacja GitHub | „Tożsamość bota o określonym zakresie” | Aplikacja z szczegółowymi uprawnieniami + krótkotrwały token instalacji |
| Agent chmury asynchronicznej | „Agent działający w tle” | Nieinteraktywny proces roboczy działający w piaskownicy w chmurze, a nie w terminalu |
| Wnioskowanie o środowisku | „Synteza pliku Docker” | Wykryj język + menedżer pakietów, wygeneruj plik Dockerfile, jeśli go nie ma |
| Weryfikacja | „CI-w piaskownicy” | Uruchom pełny zestaw testów wewnątrz pracownika przed otwarciem PR |
| Delta pokrycia | „Zachowanie zasięgu” | Zmiana % pokrycia testowego z gałęzi podstawowej do gałęzi agenta |
| Budżet na repo | „Pułap dzienny” | U dyspozytora obowiązuje limit dolarów i PR
| Uzasadnienie | „Wyjaśnienia organu PR” | Podsumowanie agenta dotyczące tego, co się zmieniło i dlaczego; wymagane w organie PR |

## Dalsze czytanie

- [Zdalni agenci SWE AWS](https://github.com/aws-samples/remote-swe-agents) — kanoniczne odniesienie do agenta asynchronicznego w chmurze
- [SWE-agent](https://github.com/SWE-agent/SWE-agent) — odniesienie do CLI
- [Agenty działające w tle kursora](https://docs.cursor.com/background-agent) — alternatywa komercyjna
- [OpenAI Codex (chmura)](https://openai.com/codex) — hostowany konkurent
– [Google Jules](https://jules.google) – wersja hostowana przez Google
- [Factory Droids](https://www.factory.ai) — alternatywne odniesienie komercyjne
- [Dokumentacja aplikacji GitHub](https://docs.github.com/en/apps) — tożsamość bota o określonym zakresie
- [Piaskownice w chmurze Daytona](https://daytona.io) — piaskownica referencyjna