# Capstone 10 — Wieloagentowy zespół inżynierów oprogramowania

> Architektura fabryczna SWE-AF, podpowiedzi oparte na rolach MetaGPT, wykres aktorów typowanych w AutoGen 0.4, Devin firmy Cognition i droidy fabryczne — wszystko to zbiegło się w tym samym kształcie na rok 2026: plany architekta, N programistów pracuje w równoległych drzewach roboczych, bramki recenzenta, weryfikacja testera. Równoległe drzewa robocze przekształcają zegar ścienny w przepustowość. Powierzchnią awarii stają się protokoły stanu współdzielonego i przekazywania. Podstawą jest zbudowanie zespołu, ocena na SWE-bench Pro i raportowanie, które przekazania są przerywane i jak często.

**Typ:** Zwieńczenie
**Języki:** Python / TypeScript (agenci), Shell (skrypty drzewa roboczego)
**Wymagania wstępne:** Faza 11 (inżynieria LLM), Faza 13 (narzędzia), Faza 14 (agenci), Faza 15 (autonomia), Faza 16 (multiagent), Faza 17 (infrastruktura)
**Wykonywane fazy:** P11 · P13 · P14 · P15 · P16 · P17
**Czas:** 40 godzin

## Problem

W przypadku dużych zadań moduły kodowania pojedynczego agenta osiągają pułap. Nie dlatego, że jakikolwiek indywidualny agent jest słaby, ale dlatego, że kontekst zawierający 200 tys. tokenów nie jest w stanie pomieścić planu architektury plus czterech równoległych wycinków bazy kodu, komentarza recenzenta i wyników testów. W fabrykach wieloagentowych problem jest podzielony: architekt jest właścicielem planu, programiści mają własną implementację w równoległych drzewach roboczych, recenzent bramuje, tester weryfikuje. „Fabryczna” architektura SWE-AF, role MetaGPT, typowany wykres aktorów AutoGen — wszystkie trzy kadry opisują ten sam kształt.

Powierzchnią awarii jest przekazanie. Architekt planuje coś, czego programiści nie mogą wdrożyć. Kodery tworzą sprzeczne różnice. Recenzent zatwierdza halucynacyjną poprawkę. Tester ściga się z wciąż piszącym koderem. Stworzysz jeden z tych zespołów, uruchomisz go na 50 wydaniach SWE-bench Pro, będziesz śledzić każde przekazanie i opublikujesz sekcję zwłok.

## Koncepcja

Role są agentami typu. **Architekt** (Claude Opus 4.7) czyta problem, pisze plan i dzieli go na podzadania z wyraźnymi interfejsami. **Programiści** (Claude Sonnet 4.7, N równoległych instancji, każda w `git worktree` + piaskownicy Daytona) niezależnie implementują podzadania. **Recenzent** (GPT-5.4) odczytuje połączone różnice i zatwierdza określone zmiany lub żąda określonych zmian. **Tester** (Gemini 2.5 Pro) uruchamia zestaw testów w izolacji i zgłasza wynik pozytywny/negatywny z artefaktami.

Komunikacja odbywa się poprzez współdzieloną tablicę zadań (opartą na plikach lub Redis). Każda rola pochłania zadania, które może wykonywać. Przekazania to komunikaty oparte na protokole A2A. Koordynacja dotyczy: rozwiązywania konfliktów scalania (rola koordynatora lub automatyczne scalanie trójstronne), synchronizacji stanu współdzielonego (plan jest zamrażany po uruchomieniu programistów; ponowne plany to osobne zdarzenia) i kontroli recenzenta (recenzent nie może zatwierdzić własnych zmian ani zmian, które zaproponował).

Wzmocnienie tokena to ukryty koszt. Każda granica roli dodaje monity podsumowujące i kontekst przekazania. 40-turowa gra z jednym agentem to łącznie 160 tur w czterech rolach. W rubryce tej w szczególności porównuje się wydajność tokena z wartością bazową dla jednego agenta, ponieważ pytanie nie brzmi „czy działa wielu agentów”, ale „czy wygrywa w przeliczeniu na dolara”.

## Architektura

```
GitHub issue URL
      |
      v
Architect (Opus 4.7)
   reads issue, produces plan with subtasks + interfaces
      |
      v
Task board (file / Redis)
      |
   +-- subtask 1 ---+-- subtask 2 ---+-- subtask 3 ---+-- subtask 4 ---+
   v                v                v                v                v
Coder A          Coder B          Coder C          Coder D          (4 parallel)
 (Sonnet)         (Sonnet)         (Sonnet)         (Sonnet)
 worktree A       worktree B       worktree C       worktree D
 Daytona          Daytona          Daytona          Daytona
      |                |                |                |
      +--------+-------+-------+--------+
               v
           merge coordinator  (three-way merge + conflict resolution)
               |
               v
           Reviewer (GPT-5.4)
               |
               v
           Tester  (Gemini 2.5 Pro)  -> passes? -> open PR
                                     -> fails?  -> route back to coder
```

## Stos

- Orkiestracja: LangGraph ze wspólnym stanem + podwykresy dla poszczególnych agentów
- Przesyłanie wiadomości: protokół A2A (Google 2025) dla wpisywanych wiadomości między agentami
- Modele: Opus 4.7 (architekt), Sonnet 4.7 (kodery), GPT-5.4 (recenzent), Gemini 2.5 Pro (tester)
- Izolacja drzewa roboczego: `git worktree add` na kodera + piaskownica Daytona
- Koordynator ds. łączenia: niestandardowe połączenie trójstronne + rozwiązywanie konfliktów za pośrednictwem LLM
- Eval: SWE-bench Pro (50 numerów), scenariusze SWE-AF, HumanEval++ do testów jednostkowych
- Obserwowalność: Langfuse z zakresami oznaczonymi rolami, rozliczanie tokenów dla poszczególnych agentów
- Wdrożenie: K8 z każdą rolą jako osobne wdrożenie + HPA w zaległościach

## Zbuduj to

1. **Tablica zadań.** JSONL oparty na plikach z wpisanymi wiadomościami: `plan_request`, `subtask`, `diff_ready`, `review_needed`, `test_needed`, `approved`, `rejected`, `replan_needed`. Agenci subskrybują tagi.

2. **Architekt.** Czyta problem z GitHubem, uruchamia Opus 4.7 z szablonem planu wymagającym jawnych interfejsów podzadań (dotknięte pliki, funkcje publiczne, wpływ testów). Emituje jedno `plan_request` z DAG podzadań.

3. **Programiści.** N równoległych pracowników, każdy otrzymuje od planszy jedno podzadanie. Każdy tworzy nową gałąź `git worktree add` oraz piaskownicę Daytona. Realizuje podzadanie. Emituje `diff_ready` z poprawką + delty testowe.

4. **Koordynator scalania.** W przypadku wszystkich programistów, trójkierunkowe połączenie N gałęzi w gałąź pomostową. Rozwiązywanie konfliktów za pośrednictwem LLM tylko wtedy, gdy istnieje nakładanie się na poziomie plików.

5. **Recenzent.** GPT-5.4 odczytuje połączone różnice. Nie można zatwierdzić różnic, których jest autorem. Emituje `approved` (no-op) lub `review_feedback` z konkretnymi żądaniami zmian kierowanymi z powrotem do odpowiedniego kodera.

6. **Tester.** Gemini 2.5 Pro uruchamia zestaw testów w czystej piaskownicy. Przechwytuje artefakty. Emituje `test_passed` lub `test_failed` ze śladami stosu. Nieudane testy wracają do kodera będącego właścicielem nieudanego podzadania.

7. **Rozliczanie przekazania.** Każdy komunikat przekraczający granicę roli otrzymuje w Langfuse zakres z uwzględnieniem rozmiaru ładunku i użytego modelu. Oblicz wzmocnienie tokenu dla poszczególnych podzadań (coder_tokens + recenzent_tokens + tester_tokens + Architect_share / coder_tokens).

8. **Eval.** Działa na 50 wydaniach SWE-bench Pro. Porównaj pass@1 i $-per-solved-issue z punktem odniesienia dla jednego agenta (jeden Sonnet 4.7 w jednym drzewie roboczym).

9. **Badanie pośmiertne.** W przypadku każdego nieudanego problemu zidentyfikuj przekazanie, które się zepsuło (plan zbyt niejasny, konflikt scalania, fałszywa akceptacja recenzenta, błąd testera). Utwórz histogram niepowodzenia przełączania.

## Użyj tego

```
$ team run --issue https://github.com/acme/widget/issues/842
[architect] plan: 4 subtasks (parser, cache, api, migration)
[board]     dispatched to 4 coders in parallel worktrees
[coder-A]   subtask parser  -> 42 lines, tests pass locally
[coder-B]   subtask cache   -> 88 lines, tests pass locally
[coder-C]   subtask api     -> 31 lines, tests pass locally
[coder-D]   subtask migration -> 19 lines, tests pass locally
[merge]     3-way merge: 0 conflicts
[reviewer]  comments on cache (thread pool sizing); routed to coder-B
[coder-B]   revision: 92 lines; submits
[reviewer]  approved
[tester]    all 412 tests pass
[pr]        opened #3382   4 coders, 1 revision, $4.90, 18m
```

## Wyślij to

Elementem dostarczanym jest `outputs/skill-multi-agent-team.md`. Biorąc pod uwagę adres URL problemu i poziom równoległości, zespół tworzy PR gotowy do scalania z rozliczaniem tokenów dla poszczególnych ról.

| Waga | Kryterium | Jak to się mierzy |
|:-:|---|---|
| 25 | SWE-bench Pro pass@1 | Dopasowany podzbiór 50 numerów, pass@1 |
| 20 | Równoległe przyspieszenie | Zegar ścienny a punkt odniesienia dla jednego agenta |
| 20 | Jakość recenzji | Wskaźnik fałszywych zatwierdzeń w przypadku sondy zawierającej wstrzyknięty błąd |
| 20 | Wydajność tokena | Całkowita liczba tokenów na rozwiązany problem w porównaniu z pojedynczym agentem |
| 15 | Inżynieria koordynacji | Rozwiązywanie konfliktów scalania, histogram niepowodzenia przekazania |
| **100** | | |

## Ćwiczenia

1. Wprowadź oczywisty błąd do pliku różnicowego w połowie (dodatkowe `return None` przed głównym elementem). Zmierz odsetek fałszywych zatwierdzeń recenzentów. Dostosuj monity recenzenta, aż odsetek fałszywych zatwierdzeń będzie mniejszy niż 5%.

2. Ogranicz do dwóch programistów (architekt + programista + recenzent + tester, programista wykonuje po kolei dwa podzadania). Porównaj zegar ścienny i zdawalność.

3. Zastąp koordynatora scalania ograniczeniem pojedynczego zapisu (zadania podrzędne dotyczą rozłącznych zestawów plików). Zmierz obciążenie planistyczne architekta.

4. Zmień recenzenta z GPT-5.4 na Claude Opus 4.7. Zmierz współczynnik fałszywych zatwierdzeń i różnicę kosztów tokena.

5. Dodaj piątą rolę: dokumentalista (Haiku 4.5). Po sprawdzeniu tworzy wpis w dzienniku zmian. Zmierz, czy jakość dokumentacji uzasadnia dodatkowe wydatki na tokeny.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| Równoległe drzewo pracy | „Odosobniony oddział” | `git worktree add` tworzenie nowego drzewa roboczego dla każdego kodera |
| Tablica zadań | „Wspólna magistrala wiadomości” | Magazyn plików lub Redis z wpisanymi wiadomościami, które agenci subskrybują |
| Przekazanie | „Granica roli” | Dowolny komunikat przechodzący z kontekstu jednej roli do kontekstu innej roli |
| Wzmocnienie symbolu | „Narzut wieloagentowy” | Łączna liczba tokenów dla różnych ról/tokenów jednego agenta dla tego samego zadania |
| Protokół A2A | „Agent do agenta” | Specyfikacja Google na rok 2025 dotycząca pisanych wiadomości między agentami |
| Koordynator scalania | „Integrator” | Komponent uruchamiający trójstronne scalanie i pośredniczący w konfliktach |
| Fałszywa akceptacja | „halucynacja recenzenta” | Recenzent zatwierdza różnicę ze znanymi błędami |

## Dalsze czytanie

– [Architektura fabryczna SWE-AF](https://github.com/Agent-Field/SWE-AF) — referencyjna fabryka wieloagentowa na rok 2026
- [MetaGPT](https://github.com/FoundationAgents/MetaGPT) — platforma wieloagentowa oparta na rolach
- [AutoGen v0.4](https://github.com/microsoft/autogen) — framework aktorów typowanych firmy Microsoft
- [Cognition AI (Devin)](https://cognition.ai) — produkt referencyjny
- [Factory Droids](https://www.factory.ai) — alternatywny produkt referencyjny
- [Protokół Google A2A](https://developers.google.com/agent-to-agent) — specyfikacja przesyłania wiadomości między agentami
- [dokumentacja git worktree](https://git-scm.com/docs/git-worktree) — podłoże izolacyjne
- [SWE-bench Pro](https://www.swebench.com) — cel oceny