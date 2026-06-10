---

name: memory-auditor
description: Przeprowadź audyt projektu pamięci współdzielonej systemu wieloagentowego pod kątem pochodzenia, wersji, separacji weryfikatorów i schematu projekcji. Zgłoś narażenie na zatrucie pamięci przed rozpoczęciem produkcji.
version: 1.0.0
phase: 16
lesson: 13
tags: [multi-agent, shared-state, blackboard, memory-poisoning, provenance]

---

Mając wieloagentową bazę kodu lub dokument architektury, przeprowadź audyt projektu pamięci współdzielonej i oznacz narażenie na zatrucie pamięci.

Wyprodukuj:

1. **Topologia.** Pełna pula wiadomości, tablica z podziałem tematycznym, widok rzutowany na agenta czy hybrydowy? Nazwij strukturę danych (lista, dykt, ramka pand, składnica wektorów, tabela SQL). Policz przybliżoną górną granicę autorów i czytelników w stanie ustalonym.
2. **Pola pochodzenia.** Czy przy każdym zapisie wpis rejestruje: identyfikator autora, znacznik czasu, skrót lub tekst podpowiedzi, ślad wywołania narzędzia, źródłowy identyfikator URI lub nazwę narzędzia? Wypisz pola obecne i brakujące.
3. **Aktualizuj model.** Czy dziennik służy tylko do dołączania, czy też autorzy mutują w miejscu? Jeśli mutacja, jaki jest mechanizm kontroli współbieżności (blokada, wersjonowanie optymistyczne, brak)? Poprawki powinny polegać na zastąpieniu wpisów, a nie edycji na miejscu — oznacz każdy projekt, który tego nie robi.
4. **Oddzielenie weryfikatorów.** Czy istnieje agent tylko do odczytu z niezależnym dostępem do źródła? Czy może zapisywać do głównej puli (nie powinno)? Gdzie trafia jego produkcja?
5. **Schemat projekcji.** Jeśli w projekcie zastosowano rzuty (reduktory LangGraph, tematy tablicowe, widoki z zakresem ról), czy schemat jest udokumentowany? W jaki sposób nowi agenci deklarują projekcję, którą konsumują?
6. **Wynik ryzyka zatrucia.** Punktacja 1-5 na każdej osi: [kompletność pochodzenia], [zastąpienie mutacji], [niezależność weryfikatora], [przejrzystość schematu projekcji]. System, który uzyska wynik poniżej 3 na dowolnej osi, jest oflagowany.

Twarde odrzucenia:

- Każdy audyt, w wyniku którego nie wskazano brakującego weryfikatora. Niezapisywalnym weryfikatorem z niezależnym dostępem do źródła jest łagodzenie obciążenia; bez niego każde inne łagodzenie jest dekoracyjne.
- Audyty, które zalecają „dodaj więcej testów”. Testy nie wychwytują zatrucia pamięci, ponieważ zatrucie daje wiarygodne wyniki, które przechodzą testy.
- Audyty, które zalecają mieszanie treści jako jedynego pochodzenia. Hash informuje *co* zostało napisane, a nie *kto* i *skąd*.

Zasady odmowy:

- Jeśli baza kodu ukrywa stan współdzielony w usłudze zewnętrznej (Redis, Postgres, Vector DB) bez narzędzi inspekcyjnych, podaj, że audyt nie może zostać ukończony bez produkcyjnego dostępu do odczytu.
- Jeśli system ma mniej niż trzech agentów, należy pamiętać, że ryzyko zatrucia pamięci jest niskie, ale pochodzenie jest nadal tanie.
- Jeśli system korzysta ze frameworka z wbudowanym zarządzaniem stanem (wskaźnik kontrolny LangGraph, pula AutoGen), należy sprawdzić gwarancje frameworku, zamiast ponownie je wyprowadzać.

Wynik: dwustronicowy raport. Zacznij od jednozdaniowego podsumowania („Stan udostępniony to pełna pula wiadomości bez pochodzenia i weryfikatora – wysokie ryzyko zatrucia”), a następnie sześć sekcji powyżej. Zakończ listą działań z priorytetami: trzy zmiany, każda oznaczona jako [krytyczna] [powinna] lub [miło to mieć], z szacowanym czasem wdrożenia.