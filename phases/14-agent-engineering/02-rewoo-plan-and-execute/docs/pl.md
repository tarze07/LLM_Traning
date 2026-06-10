# ReWOO i Plan-and-Execute: oddzielone planowanie

> ReAct łączy myśli i działania w jednym strumieniu. ReWOO je rozdziela: jeden duży plan z góry, a następnie wykonanie. 5x mniej tokenów, +4% dokładność w HotpotQA i możesz destylować planistę w model 7B. Uogólnił to plan i wykonanie; Planuj i działaj przeskalowano to do nawigacji internetowej.

**Typ:** Kompilacja
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 14 · 01 (pętla agenta)
**Czas:** ~60 minut

## Cele nauczania

- Wyjaśnij, dlaczego podział Planner / Worker / Solver w ReWOO oszczędza tokeny i poprawia niezawodność w porównaniu z przeplataną pętlą ReAct.
- Zaimplementuj plan DAG, wykonawcę uporządkowaną według zależności i solwer, który tworzy dane wyjściowe procesu roboczego — wszystko stdlib.
- Zdecyduj, kiedy zadanie powinno zostać uruchomione w trybie „zaplanuj, a następnie wykonaj”, a kiedy przeplatane ReAct, korzystając z „pięciu wzorców przepływu pracy” z 2026 r. (Anthropic).
- Rozpoznaj, kiedy syntetyczne dane planu Planuj i działaj są potrzebne do długoterminowych zadań internetowych lub mobilnych.

## Problem

Przeplatana pętla myślenia, działania i obserwacji w ReAct jest prosta i elastyczna, ale każde wywołanie narzędzia musi zawierać pełny wcześniejszy kontekst – łącznie z każdą poprzednią myślą. Użycie tokenów rośnie kwadratowo wraz z głębokością. Gorzej: gdy narzędzie ulegnie awarii w połowie pętli, model musi ponownie wyprowadzić cały plan z obserwacji błędu.

ReWOO (Xu et al., arXiv:2305.18323, maj 2023) zauważył to i postawił zakład: zaplanuj całość z góry, równolegle zbierz dowody, a na końcu ułóż odpowiedź. Jedno wezwanie LLM do planowania, N narzędzi wzywa do dowodów (mogą być równoległe), jedno wezwanie LLM do rozwiązania. Handel polega na mniejszej elastyczności (plan jest statyczny) w celu uzyskania znacznie lepszej wydajności tokena i wyraźniejszych trybów awarii.

## Koncepcja

### Trzy role

```
Planner:  user_question -> [plan_dag]
Workers:  [plan_dag]     -> [evidence]        (tool calls, possibly parallel)
Solver:   user_question, plan_dag, evidence -> final_answer
```

Planista tworzy DAG. Każdy węzeł nazywa narzędzie, jego argumenty i wcześniejsze węzły, od których jest zależne (odniesienia takie jak `#E1`, `#E2`). Procesy robocze wykonują węzły w kolejności topologicznej. Solver łączy wszystko w jedną całość.

### Dlaczego 5x mniej tokenów

ReAct zwiększa długość podpowiedzi liniowo wraz z liczbą kroków. W kroku 10 zachęta zawiera myśl 1 plus działanie 1 plus obserwacja 1 plus myśl 2 plus działanie 2 plus obserwacja 2 i tak dalej. Każdy krok pośredni zawiera również oryginalny monit.

ReWOO płaci za jedno monit planisty (duży), N małych monitów dla pracowników (każde tylko wywołanie narzędzia, bez łańcucha) i jedno monit Solvera. W HotpotQA papier mierzy ~5 razy mniej żetonów, jednocześnie uzyskując +4 absolutnej dokładności.

### Dlaczego jest bardziej wytrzymały

Jeśli proces roboczy 3 nie powiedzie się w ReAct, pętla musi wywnioskować błąd w połowie strumienia. W ReWOO pracownik 3 zwraca ciąg błędu; osoba rozwiązująca widzi to w kontekście pierwotnego planu i może z wdziękiem ulec degradacji. Lokalizacja awarii jest ustalana na węzeł, a nie na krok.

### Destylacja planisty

Drugi wynik artykułu: ponieważ planista nie widzi obserwacji, można dostroić model 7B na podstawie wyników planisty uzyskanych od nauczyciela 175B. Mały model obsługuje planowanie; duży model nie jest potrzebny przy wnioskowaniu. Jest to obecnie standardem — wielu agentów produkcyjnych na rok 2026 korzysta z usług małego planisty i dużego wykonawcy lub odwrotnie.

### Zaplanuj i wykonaj (LangChain, 2023)

W poście zespołu LangChain z sierpnia 2023 r. uogólniono ReWOO w nazwę wzorca: Planuj i wykonaj. Planista z góry generuje listę kroków, wykonawca uruchamia każdy krok, opcjonalny planista może dokonać przeglądu po obserwacji wyników. Jest to bliższe ReAct niż ReWOO (osoba ponownie planująca wprowadza obserwacje z powrotem do planowania), ale zachowuje symboliczne oszczędności.

### Planuj i działaj (Erdogan et al., arXiv:2503.09572, ICML 2025)

Planuj i działaj skaluje wzorzec do długoterminowych agentów internetowych i mobilnych. Kluczowym wkładem są syntetyczne dane planu: oznaczony generator trajektorii generuje dane szkoleniowe tam, gdzie plan jest jawny. Służy do dostrajania modeli planistów, które pracują powyżej 30–50 kroków w zadaniach podobnych do WebArena, w których pojedyncza trajektoria ReAct traci spójność.

### Kiedy wybrać który

| Wzór | Kiedy |
|--------|------|
| Reaguj | Krótkie zadania, nieznane środowisko, wymagają reaktywnej obsługi wyjątków |
| ReWOO | Ustrukturyzowane zadania ze znanymi narzędziami, dowody wrażliwe na tokeny i możliwe do zrównoleglenia |
| Zaplanuj i wykonaj | Podobnie jak ReWOO, ale z ponownym planowaniem po częściowym wykonaniu |
| Planuj i działaj | Długi horyzont (>30 kroków), korzystanie z Internetu/mobilu/komputera |
| Drzewo Myśli | Za wyszukiwanie warto zapłacić (Lekcja 04) |

Wytyczne Anthropic z grudnia 2024 r.: zacznij od najprostszego. Jeśli zadanie składa się z jednego wywołania narzędzia i podsumowania, nie twórz ReWOO. Jeśli zadanie badawcze składa się z 40 kroków, nie wykonuj ReAct samodzielnie.

## Zbuduj to

`code/main.py` implementuje zabawkę ReWOO:

- `Planner` — strategia skryptowa, która emituje plan DAG z podpowiedzi.
- `Worker` — wywołuje wywołanie narzędzia każdego węzła za pośrednictwem rejestru.
- `Solver` — kompozycja skryptowa, która odczytuje dowody i daje ostateczną odpowiedź.
- Rozwiązywanie zależności — odniesienia takie jak `#E1` są zastępowane wcześniejszymi wynikami procesu roboczego.

Demo odpowiada na pytania: „Jaka jest populacja stolicy Francji, w zaokrągleniu do milionów?” stosując plan dwuetapowy: (1) wyszukaj stolicę, (2) sprawdź populację, a następnie rozwiąż.

Uruchom to:

```
python3 code/main.py
```

Ślad pokazuje najpierw pełny plan, następnie wyniki pracownika, a następnie kompozycję rozwiązania. Porównaj liczbę tokenów (drukujemy przybliżoną liczbę znaków) z przebiegiem z przeplotem w stylu ReAct — ReWOO wygrywa w przypadku tego rodzaju ustrukturyzowanego zadania.

## Użyj tego

LangGraph dostarcza Plan-and-Execute jako przepis (`create_react_agent` dla ReAct, niestandardowe wykresy dla planowania-wykonania). Przepływy CrewAI bezpośrednio kodują wzorzec: definiujesz zadania z góry, a Flow DAG je wykonuje. Podejście oparte na danych syntetycznych stosowane w programie Plan-and-Act nadal opiera się głównie na badaniach; wzorzec środowiska wykonawczego (jawny plan DAG) jest dostarczany w fazie produkcyjnej za pośrednictwem przepływów LangGraph i CrewAI.

## Wyślij to

`outputs/skill-rewoo-planner.md` generuje DAG planu ReWOO na podstawie żądania użytkownika, biorąc pod uwagę katalog narzędzi. Weryfikuje plan (acykliczny, rozwiązane każde odniesienie, każde narzędzie istnieje) przed przekazaniem wykonawcy.

## Ćwiczenia

1. Zrównoleglanie wykonywania procesów roboczych dla niezależnych węzłów planu. Co Ci to daje na 6-węzłowym DAG z 2 równoległymi grupami?
2. Dodaj węzeł narzędzia ponownego planowania, który będzie uruchamiany, jeśli dowolny proces roboczy zwróci błąd. Jaka jest najmniejsza zmiana w ReWOO, która sprawia, że ​​można go zaplanować i wykonać?
3. Zamień `Planner` na mały model (klasa 7B) i zachowaj `Solver` na modelu granicznym. Porównaj jakość od początku do końca — gdzie podział zawodzi?
4. Przeczytaj sekcję 4 artykułu ReWOO na temat destylacji planistycznej. Odtwórz koncepcyjnie wynik 175B -> 7B: jakich danych szkoleniowych potrzebujesz i jak oceniasz jakość planu?
5. Przenieś zabawkę na kształt trajektorii Planuj i działaj: plan to sekwencja, a nie DAG. Jakie kompromisy się zmieniają?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| ReWOO | „Rozumowanie bez obserwacji” | Zaplanuj, następnie pobierz równolegle dowody, a następnie rozwiąż — brak obserwacji w wierszu planowania |
| Zaplanuj i wykonaj | „Wzorzec planu i wykonania LangChaina” | ReWOO z opcjonalnym węzłem replanera po wykonaniu |
| Planuj i działaj | „Skalowany plan-wykonanie” | Jawny podział planisty/wykonawcy z syntetycznymi danymi szkoleniowymi planu dla zadań długoterminowych |
| Odniesienie do dowodów | „#E1, #E2, …” | Symbol zastępczy węzła planu zastąpiony wcześniejszymi wynikami procesu roboczego w momencie wysyłki |
| Planista destylacji | „Mały planista, duży wykonawca” | Dostosuj mały model na śladach planisty od dużego nauczyciela |
| Wydajność tokena | „Mniej podróży w obie strony” | 5x mniej tokenów na HotpotQA vs ReAct w gazecie |
| Wykonawca DAG | „Dyspozytor topologiczny” | Uruchamia węzły planu w kolejności zależności; równolegle na każdym poziomie |

## Dalsze czytanie

- [Xu et al., ReWOO: Decoupling Reasoning from Observations (arXiv:2305.18323)](https://arxiv.org/abs/2305.18323) — artykuł kanoniczny
- [Erdogan et al., Plan-and-Act (arXiv:2503.09572)](https://arxiv.org/abs/2503.09572) — skalowany planista-wykonawca z planami syntetycznymi
- [Poradnik LangGraph Plan-and-Execute](https://docs.langchain.com/oss/python/langgraph/overview) — przepis na framework
– [Anthropic, Building Effective Agents](https://www.anthropic.com/research/building-efektywne-agents) — wybierz najprostszy wzór, który działa