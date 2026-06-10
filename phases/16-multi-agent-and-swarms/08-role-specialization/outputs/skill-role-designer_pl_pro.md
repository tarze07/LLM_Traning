---

name: role-designer
description: Zaprojektuj strukturę ról dla systemu wieloagentowego, określając zadania planisty, wykonawcy, krytyka i weryfikatora wraz z jawnymi schematami wejścia/wyjścia.
version: 1.0.0
phase: 16
lesson: 08
tags: [multi-agent, role-specialization, metagpt, chatdev, verification]

---

Na podstawie opisu zadania utwórz strukturę wyspecjalizowanych ról wraz ze schematami wejścia/wyjścia oraz specyfikacją deterministycznego weryfikatora, gotową do zaimplementowania w środowiskach takich jak CrewAI, LangGraph, AutoGen lub w pętli niestandardowej.

Wygeneruj:

1. **Wykaz ról.** Od 3 do 5 ról. Nazwij każdą z nich. Wymagane minimum: planista, wykonawca oraz weryfikator. Rola krytyka jest opcjonalna.
2. **Schemat wejścia/wyjścia dla każdej roli.** Określ dokładnie, jakie dane wejściowe rola konsumuje (od roli nadrzędnej) i jakie dane wyjściowe produkuje (zdefiniuj schemat w postaci notacji klasy danych, unikaj opisów słownych).
3. **Specyfikacja weryfikatora.** Zdefiniuj deterministyczny mechanizm kontroli: wskaż zestaw testów jednostkowych, sprawdzanie typów (type checker), walidator schematów lub linter. Opisz kryteria zaliczenia/niezaliczenia testu.
4. **Specyfikacja krytyka (opcjonalnie).** Jeśli uwzględniasz tę rolę, określ, jakie subiektywne cechy jakościowe ocenia model LLM. Przygotuj konkretną listę kontrolną (unikaj ogólnych sformułowań typu „poprawny kod”).
5. **Wytyczne dotyczące odhalucynowania komunikacyjnego.** Zdefiniuj zestaw pytań, jakie rola wykonawcza może i powinna zadać planiście w przypadku braku precyzyjnych specyfikacji, aby uniknąć zmyślania danych.
6. **Budżet pętli poprawek (Revision Loop).** Określ maksymalną dopuszczalną liczbę iteracji poprawek przed przerwaniem procesu i eskalacją problemu do człowieka. Domyślna wartość to 2.
7. **Mapowanie na frameworki.** Wskaż w jednym zdaniu, jak zaimplementować tę strukturę ról w środowiskach CrewAI, LangGraph oraz AutoGen.

Twarde kryteria odrzucenia:

- Odrzuć projekty, które nie definiują żadnego deterministycznego weryfikatora opartego na kodzie. Struktury oparte wyłącznie na modelach LLM nie spełniają wymogów bezpieczeństwa MAST.
- Odrzuć nieprecyzyjne opisy wejścia/wyjścia (np. „wykonawca zwraca wynik”). Zawsze podawaj dokładny schemat danych.
- Odrzuć łączenie roli krytyka i weryfikatora w jednego agenta. Obie te role wykrywają inne kategorie błędów i muszą działać niezależnie, jeśli ich obecność jest uzasadniona.

Zasady obsługi przypadków szczególnych:

- Jeśli zadanie nie pozwala na wdrożenie deterministycznej weryfikacji poprawności (np. czysta praca kreatywna, pisanie tekstów reklamowych), odrzuć ten wzorzec i zarekomenduj pętlę opartą na krytyce LLM lub debatę wieloagentową (lekcja 07).
- Jeśli zadanie jest zbyt małe i proste, by uzasadnić tworzenie co najmniej 3 ról (odpowiednik poniżej 10 minut pracy człowieka), odrzuć projekt i zarekomenduj architekturę jednoagentową.

Wynik: jednostronicowy opis projektu ról. Zakończ weryfikacją podatności na błędy MAST: potwierdź obecność co najmniej jednego deterministycznego weryfikatora.
