---

name: memory-auditor
description: Przeprowadź audyt projektu pamięci współdzielonej w systemie wieloagentowym pod kątem pochodzenia danych, wersjonowania, separacji weryfikatorów oraz schematu projekcji. Wykrywaj podatności na zatrucie pamięci przed wdrożeniem produkcyjnym.
version: 1.0.0
phase: 16
lesson: 13
tags: [multi-agent, shared-state, blackboard, memory-poisoning, provenance]

---

Na podstawie bazy kodu lub dokumentacji architektury systemu wieloagentowego, przeprowadź audyt projektu pamięci współdzielonej i wskaż potencjalne podatności na zatrucie pamięci.

Opracuj:

1. **Topologia.** Pełna pula wiadomości (message pool), tablica ogłoszeniowa (blackboard) z podziałem tematycznym, dedykowana projekcja stanu na agenta czy model hybrydowy? Określ strukturę danych (lista, słownik, pandas DataFrame, baza wektorowa, tabela SQL). Oszacuj maksymalną liczbę wątków zapisujących i czytających w stanie ustalonym.
2. **Śledzenie pochodzenia (Provenance fields).** Czy każdy zapis rejestruje: identyfikator autora, znacznik czasu, skrót (hash) lub treść promptu, historię wywołań narzędzi (tool call trace) oraz źródłowy adres URI lub nazwę narzędzia? Wypisz dostępne oraz brakujące pola.
3. **Model aktualizacji.** Czy pamięć działa w trybie append-only (tylko do zapisu), czy dopuszczalne są modyfikacje w miejscu (in-place mutations)? W przypadku modyfikacji w miejscu, wskaż mechanizm kontroli współbieżności (blokady, wersjonowanie optymistyczne, brak). Korekty informacji powinny być wprowadzane jako nowe wersje wpisów zastępujące poprzednie — oznacz projekty, które nie spełniają tego kryterium.
4. **Separacja weryfikatora.** Czy zaimplementowano agenta weryfikującego w trybie tylko do odczytu, mającego niezależny dostęp do weryfikowanych źródeł danych? Czy agent ten ma zablokowaną możliwość zapisu do wspólnej pamięci? Gdzie są przekazywane jego raporty?
5. **Schemat projekcji.** Jeśli w projekcie zastosowano dedykowane widoki stanu (reduktory w LangGraph, podział tematyczny na tablicy, widoki ograniczone do ról), czy ich schematy są udokumentowane? W jaki sposób nowo dodawane agenty deklarują pobierane projekcje?
6. **Ocena ryzyka zatrucia pamięci.** Ocena w skali 1-5 na czterech osiach: [kompletność metadanych pochodzenia], [brak modyfikacji w miejscu/wersjonowanie], [niezależność weryfikatora], [przejrzystość schematu projekcji]. Dowolna ocena poniżej 3 na dowolnej osi oznacza oflagowanie systemu jako podatnego.

Kryteria wykluczające:

- Pominięcie w audycie braku dedykowanego weryfikatora. Dedykowany weryfikator bez uprawnień do zapisu i z niezależnym dostępem do źródeł danych stanowi kluczowe zabezpieczenie — bez niego inne środki zaradcze mają charakter wyłącznie kosmetyczny.
- Rekomendowanie „dodania większej liczby testów”. Tradycyjne testy jednostkowe lub integracyjne nie wykrywają zatrucia pamięci, ponieważ zatruty stan generuje logicznie spójne wyniki, które przechodzą standardowe asercje.
- Rekomendowanie sumy kontrolnej (hash) treści jako jedynego zabezpieczenia pochodzenia danych. Hash określa jedynie *co* zostało zapisane, nie informując o tym *kto* dokonał zapisu ani *skąd* pochodzą dane.

Zasady odmowy (Rejection rules):

- Jeśli baza kodu ukrywa stan współdzielony w zewnętrznej bazie danych (np. Redis, PostgreSQL, baza wektorowa) bez udostępnienia narzędzi inspekcyjnych, zgłoś, że audyt nie może zostać ukończony bez dostępu do odczytu środowiska produkcyjnego.
- Jeśli system składa się z mniej niż trzech agentów, zaznacz, że ryzyko zatrucia pamięci jest niskie, ale wdrożenie śledzenia pochodzenia danych nadal pozostaje rekomendowaną i tanią praktyką.
- Jeśli system opiera się na frameworku z wbudowanym mechanizmem zarządzania stanem (np. checkpointy w LangGraph, pula wiadomości w AutoGen), zweryfikuj gwarancje zapewniane przez ten framework zamiast projektować mechanizmy od zera.

Format wyjściowy: dwustronicowy raport. Rozpocznij od jednozdaniowego podsumowania (np. „Współdzielony stan to pełna pula wiadomości bez śledzenia pochodzenia i bez weryfikatora — wysokie ryzyko zatrucia pamięci”), po którym następuje sześć opisanych wyżej sekcji. Zakończ priorytetyzowaną listą działań: wskaż trzy rekomendowane modyfikacje, oznaczając każdą z nich priorytetem [krytyczna], [zalecana] lub [opcjonalna] wraz z szacowanym czasem wdrożenia.
