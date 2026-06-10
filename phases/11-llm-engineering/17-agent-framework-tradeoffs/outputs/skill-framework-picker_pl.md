---

name: framework-picker
description: Wybierz LangGraph, CrewAI, AutoGen, Agno lub zwykły Python dla zadania agenta, dopasowując abstrakcję do kształtu problemu.
version: 1.0.0
phase: 11
lesson: 17
tags: [langgraph, crewai, autogen, agno, agent-framework, orchestration, decision-matrix]

---

Biorąc pod uwagę opis zadania (kształt problemu, łączna liczba wywołań LLM na przebieg, wzorzec rozgałęzień, wymagania dotyczące trwałości i wznowienia, punkty kontrolne „człowiek w pętli”, równoległe rozgałęzianie, pamięć sesji, oczekiwana dzienna wielkość operacji), wynik:

1. Dopasowanie kształtu. Jedno zdanie określające abstrakcję, która pasuje: wykres (stan wpisany, nazwane przejścia), schemat organizacyjny (role specjalistyczne, przekazania kierowane przez menedżera), czat (agenci rozmawiają do końca), pojedynczy agent z narzędziami. Jeśli nie możesz wybrać jednego, zadanie nie ma jeszcze charakteru agenta; zatrzymaj się i rozłóż.
2. Organ oddziałowy. Kto wybiera następny krok: programista (jawne krawędzie), menedżer LLM (hierarchiczny CrewAI), wschodzący rozmówca (AutoGen GroupChat), samokierowany wywołanie narzędzia (Agno). Jeśli ma to zastosowanie, podaj koszt tokena na turę dla trasy wybranej przez LLM.
3. Budżet państwa. Sprawdź, czy wymagane jest wznowienie po ponownym uruchomieniu, podróż w czasie lub przerwanie przez człowieka. Jeśli tak, LangGraph wygrywa w przypadku abstrakcji skupiających się na stanie; Agno obejmuje tylko pamięć o zasięgu sesji.
4. Wybór ram. Wyprowadź jeden z langgraph, creai, autogen, agno, zwykły_python. Dołącz jednozdaniowe uzasadnienie, które odwzorowuje odpowiedzi dotyczące kształtu i stanu na podstawową abstrakcję platformy.
5. Luk ewakuacyjny. Jeśli dzienny wolumen uruchomień przekracza 10_000 lub zadanie obejmuje dwa lub mniej wywołań LLM bez stanu, zamiast tego polecam zwykły język Python z zestawem SDK dostawcy. Żaden framework nie jest najszybszym frameworkiem, gdy zadanie jest małe.

Odmów polecania AutoGen dla deterministycznych przepływów pracy ze znanym DAG; GroupChatManager wydaje tokeny na wybieranie głośników, które programista mógł podłączyć statycznie. CrewAI obsługuje wyniki zadań strukturalnych poprzez `output_pydantic` / `output_json` (patrz [docs.crewai.com/en/concepts/tasks](https://docs.crewai.com/en/concepts/tasks)), ale jego kanał `context` nadal przepływa przez ciąg znaków zachęty następnego zadania. Odpuść CrewAI, gdy przepływ pracy opiera się na surowym `context` w celu przenoszenia stanu strukturalnego między zadaniami bez podłączonego jednego z tych schematów wyjściowych. Wróć do LangGraph, aby uzyskać podsumowanie dwóch rozmów telefonicznych; koszty ogólne StateGraph to czysty podatek. Odeprzyj Agno, gdy zadanie zostanie rozłożone na więcej niż 4 równoległych podwykonawców z semantyką redukcyjną; Agno dostarcza blok `Parallel`, którego dane wyjściowe łączą się w dyktando oznaczone nazwą kroku (patrz [docs-v1.agno.com/workflows_2/overview](https://docs-v1.agno.com/workflows_2/overview) i [docs.agno.com/workflows/access-previous-steps](https://docs.agno.com/workflows/access-previous-steps)), ale nie udostępnia API typu wysyłania fanout-and-reduce porównywalnego z LangGraph.

Przykładowe dane wejściowe: „Długotrwały proces badawczy: zaplanuj, rozłóż na trzy aportery, dokonaj syntezy, zatwierdzenie przez człowieka briefu, napisz raport, powołaj się na źródła. Należy wznowić po awarii. Produkcja ograniczona do 50 serii dziennie”.

Przykładowe wyjście:
- Kształt: wykres. Wpisany plan, trzy równoległe aportery, nazwane przejścia między syntezą a zapisem.
- Rozgałęzianie: ustalane przez programistę poprzez krawędzie warunkowe. Brak menedżera na turę LLM.
- Stan: wymaga wznowienia i przerwania przez człowieka. LangGraph obowiązkowy.
- Struktura: langgraph. State, Send fanout, przerwanie przed i PostgresSaver są najwyższej klasy.
- Luk ewakuacyjny: nie dotyczy. 50 uruchomień dziennie to znacznie poniżej progu zwykłego Pythona, a przepływ pracy jest zbyt stanowy, aby pozostawić go bez oprawy.