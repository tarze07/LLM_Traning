---

name: framework-picker
description: Dobierz optymalny framework (LangGraph, CrewAI, AutoGen, Agno lub czysty Python) dla zadania agentowego poprzez dopasowanie jego podstawowej abstrakcji do specyfiki problemu.
version: 1.0.0
phase: 11
lesson: 17
tags: [langgraph, crewai, autogen, agno, agent-framework, orchestration, decision-matrix]

---

Na podstawie opisu zadania (struktura problemu, łączna liczba wywołań LLM na uruchomienie, wzorzec rozgałęzień, wymagania dotyczące trwałości i wznawiania stanu, punkty kontrolne dla interwencji człowieka (human-in-the-loop), równoległe rozproszone operacje (fan-out), pamięć sesyjna oraz oczekiwana dzienna skala operacji) wygeneruj:

1. Analizę dopasowania struktury (shape matching). Jednozdaniowe określenie pasującej abstrakcji: graf (typowany stan, jawne przejścia), schemat organizacyjny (wyspecjalizowane role, zadania przydzielane przez menedżera), czat (agenci dyskutujący do momentu spełnienia warunku wyjścia) lub pojedynczy agent z narzędziami. Jeśli nie potrafisz jednoznacznie dopasować żadnego z tych modeli, zadanie nie wymaga jeszcze podejścia agentowego – zatrzymaj się i podziel je na mniejsze części.
2. Mechanizm routingu. Kto decyduje o kolejnym kroku: programista (jawne krawędzie w kodzie), menedżer LLM (tryb hierarchiczny w CrewAI), dynamiczny wybór rozmówcy (GroupChat w AutoGen) czy samodzielne wywoływanie narzędzi przez agenta (Agno). W stosownych przypadkach oszacuj koszt tokenów na każdą turę routingu dynamicznego realizowanego przez LLM.
3. Wymagania dotyczące zarządzania stanem. Określ, czy wymagane jest wznawianie pracy po restarcie, podróże w czasie (time-travel) lub zatwierdzanie kroków przez człowieka. Jeśli tak, dla projektów opartych na stanie domyślnym wyborem jest LangGraph; Agno oferuje w tym obszarze jedynie utrwalanie pamięci w zakresie sesji.
4. Rekomendację frameworku. Wybierz jedną z opcji: `langgraph`, `crewai`, `autogen`, `agno` lub `czysty_python`. Dołącz jednozdaniowe uzasadnienie wyjaśniające powiązanie struktury i wymogów zarządzania stanem z wybranym frameworkiem.
5. Opcję uproszczenia (escape hatch). Jeśli dzienna liczba wywołań przekracza 10 000 lub zadanie wymaga co najwyżej dwóch wywołań LLM i nie potrzebuje utrwalania stanu, zalecaj użycie czystego Pythona wraz z oficjalnym SDK dostawcy. Brak frameworku jest najlepszym rozwiązaniem przy małych zadaniach.

Nigdy nie polecaj AutoGen dla deterministycznych przepływów pracy o znanej strukturze DAG – `GroupChatManager` marnuje tokeny na wybór kolejnego agenta, co programista może łatwo zdefiniować statycznie. CrewAI obsługuje ustrukturyzowane formaty wyjściowe zadań poprzez `output_pydantic` / `output_json` (patrz [docs.crewai.com/en/concepts/tasks](https://docs.crewai.com/en/concepts/tasks)), ale domyślnie mechanizm przekazywania kontekstu (`context`) przesyła dane jako surowy ciąg znaków (string) w prompcie kolejnego zadania. Odrzuć CrewAI, jeśli przepływ pracy wymaga przekazywania ustrukturyzowanego stanu między zadaniami bez użycia wspomnianych schematów wyjściowych. Zrezygnuj z LangGrapha, jeśli całe zadanie sprowadza się do prostego podsumowania z dwoma wywołaniami LLM – narzut związany ze `StateGraph` będzie w tym wypadku czystym marnotrawstwem zasobów. Odrzuć Agno, jeśli zadanie wymaga rozproszenia na więcej niż 4 równoległych podwykonawców z późniejszą agregacją (fan-out i reduce). Agno udostępnia blok `Parallel`, którego wyniki są łączone w słownik powiązany z nazwami kroków (patrz [docs-v1.agno.com/workflows_2/overview](https://docs-v1.agno.com/workflows_2/overview) i [docs.agno.com/workflows/access-previous-steps](https://docs.agno.com/workflows/access-previous-steps)), ale nie oferuje tak elastycznego i wydajnego API do agregacji równoległej jak mechanizm `Send` w LangGraph.

Przykładowe dane wejściowe: „Długoterminowy proces badawczy: zaplanuj działania, rozprosz zadanie na trzy retrievery (fan-out), dokonaj syntezy wyników, wstrzymaj działanie na akceptację briefu przez człowieka, wygeneruj raport, dodaj źródła. System musi umożliwiać wznowienie pracy po awarii. Skala produkcyjna: 50 uruchomień dziennie”.

Przykładowe dane wyjściowe:
- Struktura problemu: graf. Typowany plan działania, trzy równoległe retrievery, jawnie zdefiniowane przejścia między syntezą a generowaniem raportu.
- Routing: zdefiniowany statycznie przez programistę za pomocą krawędzi warunkowych. Brak narzutu LLM na koordynację etapów.
- Zarządzanie stanem: wymagane wznawianie po restarcie oraz wstrzymywanie na akceptację przez człowieka. Użycie LangGraph jest konieczne.
- Wybrany framework: `langgraph`. Zarządzanie stanem (State), równoległe przetwarzanie (`Send` fan-out), punkty przerwania (interrupt_before) oraz baza `PostgresSaver` są tu natywnie wspierane.
- Opcja uproszczenia (escape hatch): nie dotyczy. Wolumen 50 uruchomień dziennie jest bardzo niski (daleko poniżej limitu dla czystego Pythona), a sam przepływ pracy wymaga zbyt zaawansowanego zarządzania stanem, aby wdrażać go bez dedykowanego frameworku.
