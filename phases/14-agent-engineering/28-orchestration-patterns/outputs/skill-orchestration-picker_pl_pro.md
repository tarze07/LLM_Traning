---
name: orchestration-picker
description: Wybór optymalnej topologii orkiestracji (nadzorca, rój, hierarchia, debata lub brak) dla wybranego problemu biznesowego oraz jej wdrożenie w minimalnej formie.
version: 1.0.0
phase: 14
lesson: 28
tags: [orchestration, supervisor, swarm, hierarchical, debate]
---

Biorąc pod uwagę domenę produktu oraz klasyfikację zadań, dobierz minimalną niezbędną topologię orkiestracji.

Zasady wyboru:

1. Czy pojedynczy agent oraz podstawowe przepływy pracy (lekcja 12) są wystarczające? -> Zrezygnuj ze złożonej topologii wieloagentowej.
2. Czy wdrażasz od 2 do 4 specjalistów z wyraźnie przypisanymi rolami? -> Wybierz wzorzec **nadzorca-pracownik** (supervisor-worker).
3. Czy kluczowy jest czas odpowiedzi (opóźnienia), a specjaliści mogą bezpośrednio i bezkonfliktowo przekazywać sobie zadania? -> Wybierz wzorzec **rój** (swarm).
4. Czy system obsługuje ponad 10 specjalistów, a limit tokenów kontekstu nadzorcy jest niewystarczający? -> Wybierz wzorzec **hierarchiczny** (hierarchical).
5. Czy jakość wyniku jest ważniejsza niż koszt tokenów, a domena zyskuje na wzajemnej weryfikacji i krytyce agentów? -> Wybierz protokół **debaty** (debate) (lekcja 25).

Zakres wdrożenia:

1. Kod szkieletowy implementujący wybraną topologię.
2. Mechanizmy zabezpieczające: licznik przekazań (hop counter) w roju, limit głębokości zagnieżdżenia w strukturze hierarchicznej lub limit rund w protokole debaty.
3. Punkty zaczepienia (hooks) dla celów obserwowalności wywoływane po każdym przekazaniu lub kroku wykonania (spany OTel GenAI, lekcja 23).
4. Sekcja „Dlaczego to, a nie tamto” w pliku README.

Kryteria odrzucenia (Hard Rejects):

- Definiowanie sekwencyjnego wykonania 3 prostych wywołań LLM jako systemu „wieloagentowego”. Taki przepływ to zwykłe łańcuchowanie promptów (prompt chaining).
- Implementacja wzorca roju (Swarm) bez licznika przekazań (hop counter). Zapętlenia i krążenie zadań między agentami są w takim wypadku nieuniknione.
- Tworzenie struktury hierarchicznej, w której poszczególne gałęzie zarządzają tylko jednym specjalistą. Należy wtedy spłaszczyć architekturę.

Zasady odmowy (Refusal Rules):

- Jeśli użytkownik wnioskuje o architekturę wieloagentową do zadań, które można z powodzeniem zrealizować przy użyciu pojedynczej pętli ReAct, odmów i odeślij do lekcji 01.
- Jeśli użytkownik chce wdrożyć nadzorcę dla prostego procesu 2-krokowego, odmów i zaproponuj łańcuchowanie promptów (lekcja 12).
- Jeśli domena stawia rygorystyczne wymagania dotyczące audytu i zgodności (compliance), odmów wdrożenia roju (swarm) i zaproponuj wzorzec nadzorcy lub strukturę hierarchiczną ze względu na łatwiejsze śledzenie decyzji.

Dane wyjściowe: Pliki kodu wybranej topologii oraz plik README.md zawierający uzasadnienie projektowe. Zakończ sekcją „Co przeczytać dalej”, wskazującą na lekcję 13 (LangGraph) w przypadku nadzorcy, lekcję 16 (OpenAI Agents SDK) dla mechanizmu przekazywania kontroli (handoffs) lub lekcję 25 w celu zgłębienia zasad debaty wieloagentowej.
