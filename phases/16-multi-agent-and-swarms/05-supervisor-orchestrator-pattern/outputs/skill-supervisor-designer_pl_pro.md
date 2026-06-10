---

name: supervisor-designer
description: Zaprojektuj system nadzorcy (Supervisor / Orchestrator-Worker) dla złożonych zadań badawczych, określając rolę i instrukcje agenta wiodącego, role pracowników, reguły dekompozycji oraz szablon syntezy raportu.
version: 1.0.0
phase: 16
lesson: 05
tags: [multi-agent, supervisor, orchestrator, anthropic-research, langgraph]

---

Na podstawie zapytania użytkownika wymagającego równoległych analiz ze strony subagentów zaprojektuj strukturę wzorca nadzorcy, gotową do zaimplementowania w dowolnym środowisku (np. LangGraph, OpenAI Agents SDK, CrewAI Hierarchical).

Wygeneruj:

1. **Ocena złożoności.** Czy zapytanie ma charakter prosty (1 agent, 3–10 wywołań narzędzi), średni (2–4 pracowników) czy złożony (5+ pracowników)? Uzasadnij wybór w jednym zdaniu, odwołując się do heurystyki skalowania wysiłku (effort scaling) firmy Anthropic.
2. **Instrukcja systemowa agenta wiodącego (Lead).** Musi zawierać: (a) reguły dekompozycji zadania, (b) wytyczne dotyczące syntezy, (c) wyraźną zasadę zabraniającą agentowi wiodącemu bezpośredniego czytania surowych materiałów źródłowych (powinien analizować wyłącznie raporty przygotowane przez pracowników).
3. **Instrukcje systemowe pracowników (Workers).** Po jednej instrukcji dla każdej zdefiniowanej roli, określającej wąski zakres odpowiedzialności oraz pożądany format wyjściowy raportu.
4. **Zasady dekompozycji zadań.** W jaki sposób agent wiodący powinien dzielić zapytanie główne? Czy podział powinien iść od ogółu do szczegółu, czy też być bezpośrednim rozbiciem na wątki? Zdefiniuj kryteria odrzucenia błędnego podziału (np. nakładanie się zakresów pytań pomocniczych lub zbyt szeroki zakres pojedynczego pytania).
5. **Szablon syntezy raportu.** Określ jasne reguły rozwiązywania konfliktów informacyjnych: jeśli dwaj pracownicy dostarczą sprzeczne fakty, synteza musi jawnie wskazać tę rozbieżność, zamiast cicho wybierać jedną z wersji.
6. **Dobór modeli.** Wskaż model zalecany do roli nadzorcy (wyższe możliwości rozumowania) oraz modele do ról pracowników (szybsze i tańsze). Uzasadnij ten kompromis kosztowo-jakościowy.
7. **Wymagania dotyczące obserwowalności (observability).** Wskaż minimalne punkty logowania i śledzenia: wygenerowany plan, czas startu/końca pracy każdego z agentów, wejście syntezy oraz raport końcowy.

Twarde kryteria odrzucenia:

- Odrzuć projekty, w których agent wiodący sam korzysta z narzędzi wykonawczych. Lead odpowiada wyłącznie za planowanie, delegowanie i syntezę.
- Odrzuć instrukcje dla pracowników, które zezwalają na niekontrolowane rozszerzanie zakresu badań (np. „zbadaj wszystko powiązane z tematem X” bez sztywnych limitów).
- Odrzuć szablony syntezy, które ukrywają rozbieżności w raportach subagentów.

Zasady obsługi przypadków szczególnych:

- Jeśli zapytanie jest proste (wymaga łącznie mniej niż 10 wywołań narzędzi), odrzuć projekt nadzorcy i zarekomenduj architekturę jednoagentową. Powołaj się na 15-krotny narzut kosztów tokenowych w systemach wieloagentowych wykazany przez Anthropic.
- Jeśli kroki zadania muszą być wykonywane ściśle sekwencyjnie (krok 2 wymaga danych wyjściowych z kroku 1), odrzuć projekt nadzorcy i zarekomenduj wzorzec potoku lub łańcucha zadań.
- Jeśli priorytetem projektu jest pełny determinizm i powtarzalność audytu, odrzuć dynamicznego nadzorcę i zaproponuj statyczny graf LangGraph.

Wynik: jednostronicowy opis projektu. Rozpocznij od oceny złożoności zadania i uzasadnienia wyboru wzorca. Zakończ przypomnieniem o konieczności wdrożenia strategii Rainbow (tęczowej) przy ciągłej pracy systemu.
