# ReWOO i Plan-and-Execute: odseparowane planowanie

> ReAct łączy myślenie i działanie w ramach jednego strumienia. ReWOO rozdziela te etapy: najpierw tworzy jeden całościowy plan, a następnie go wykonuje. Zapewnia to pięciokrotne oszczędności tokenów, wzrost dokładności o 4% w teście HotpotQA oraz możliwość destylacji modułu planowania (Planner) do mniejszego modelu 7B. Wzorzec ten został uogólniony jako Plan-and-Execute (Zaplanuj i Wykonaj), natomiast Plan-and-Act (Zaplanuj i Działaj) przeskalował go do zadań związanych z nawigacją w sieci.

**Typ:** Kompilacja
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 14 · 01 (pętla agenta)
**Czas:** ~60 minut

## Cele nauczania

- Wyjaśnij, dlaczego podział na role Planner / Worker / Solver w architekturze ReWOO pozwala zaoszczędzić tokeny i zwiększyć niezawodność w porównaniu do przeplatanej pętli ReAct.
- Zaimplementuj plan w postaci skierowanego grafu acyklicznego (DAG), wykonawcę (Executor) respektującego zależności między zadaniami oraz moduł rozwiązujący (Solver) agregujący wyniki pracy – wyłącznie przy użyciu biblioteki standardowej (stdlib).
- Zdecyduj, kiedy zadanie powinno być realizowane w trybie „najpierw zaplanuj, potem wykonaj” (plan-then-execute), a kiedy w przeplatanej pętli ReAct, opierając się na „pięciu wzorcach przepływu pracy” (Anthropic, 2026).
- Dowiedz się, kiedy syntetyczne dane planowania z podejścia Plan-and-Act są niezbędne do realizacji długofalowych zadań w środowiskach internetowych lub mobilnych.

## Problem

Przeplatana pętla myślenia, działania i obserwacji w podejściu ReAct jest prosta i elastyczna, jednak każde kolejne wywołanie narzędzia wymaga przekazania pełnego dotychczasowego kontekstu – w tym wszystkich wcześniejszych myśli. W rezultacie zużycie tokenów rośnie kwadratowo wraz z liczbą kroków. Co gorsza, jeśli narzędzie ulegnie awarii w połowie pętli, model musi na nowo opracować cały plan na podstawie zaobserwowanego błędu.

Twórcy ReWOO (Xu i in., arXiv:2305.18323, maj 2023) dostrzegli ten problem i zaproponowali inne rozwiązanie: zaplanować wszystko z góry, zebrać dowody (wyniki narzędzi) równolegle, a na koniec sformułować odpowiedź. Oznacza to jedno zapytanie do LLM w celu zaplanowania działań, N wywołań narzędzi po dane (które mogą być wykonywane równolegle) oraz jedno końcowe zapytanie do LLM w celu rozwiązania problemu. Ceną za to jest mniejsza elastyczność (plan jest statyczny), ale w zamian zyskujemy znacznie lepszą wydajność tokenów oraz czytelniejszą obsługę błędów.

## Koncepcja

### Trzy role

```
Planner:  user_question -> [plan_dag]
Workers:  [plan_dag]     -> [evidence]        (tool calls, possibly parallel)
Solver:   user_question, plan_dag, evidence -> final_answer
```

Planner (planista) tworzy skierowany graf acykliczny (DAG). Każdy węzeł grafu definiuje wywołanie narzędzia, jego argumenty oraz zależności od wcześniejszych węzłów (oznaczane np. jako `#E1`, `#E2`). Moduły wykonawcze (Workers) uruchamiają zadania z węzłów w kolejności topologicznej. Na końcu Solver (moduł rozwiązujący) łączy wszystkie uzyskane dane w spójną odpowiedź.

### Dlaczego 5x mniej tokenów

ReAct wydłuża prompt liniowo z każdym krokiem. W 10. kroku prompt zawiera myśl 1, działanie 1, obserwację 1, myśl 2, działanie 2, obserwację 2 i tak dalej. Każdy krok pośredni powtarza również pierwotne zapytanie.

W ReWOO koszt zamyka się w jednym (dużym) zapytaniu planisty, N małych zapytaniach dla wykonawców (z których każde zawiera tylko wywołanie pojedynczego narzędzia, bez całego kontekstu) oraz jednym zapytaniu modułu rozwiązującego. W testach HotpotQA autorzy publikacji zmierzyli około pięciokrotnie niższe zużycie tokenów, uzyskując przy tym wzrost dokładności o 4 punkty procentowe.

### Dlaczego jest bardziej wytrzymały

Jeśli w pętli ReAct krok 3 zakończy się niepowodzeniem, agent musi zinterpretować ten błąd na bieżąco. W ReWOO wykonawca zwraca po prostu komunikat o błędzie jako wynik danego kroku; Solver widzi go w kontekście całego planu i może w kontrolowany sposób zmodyfikować działanie lub odpowiedź. Awaria jest przypisana do konkretnego węzła grafu, a nie do losowego kroku w pętli.

### Destylacja planisty

Kolejny ważny wniosek z publikacji: ponieważ Planner nie analizuje na bieżąco wyników działania narzędzi, można dostroić mały model 7B przy użyciu planów wygenerowanych przez większy model 175B (nauczyciela). Mniejszy model radzi sobie z samym planowaniem, dzięki czemu podczas wnioskowania nie trzeba angażować dużego modelu. Rozwiązanie to stało się standardem – w 2026 roku wiele systemów agentowych korzysta z mniejszego modelu jako planisty i większego jako wykonawcy (lub na odwrót).

### Zaplanuj i wykonaj (LangChain, 2023)

W sierpniu 2023 roku zespół LangChain uogólnił architekturę ReWOO, wprowadzając nazwę wzorca: Plan-and-Execute (Zaplanuj i Wykonaj). Planner generuje z góry listę kroków, Executor realizuje każdy z nich, a opcjonalny replanner może zmodyfikować plan po zapoznaniu się z wynikami. Podejście to jest bliższe ReAct niż czystemu ReWOO (ponieważ replanner uwzględnia obserwacje przy aktualizacji planu), jednak pozwala zachować znaczne oszczędności na tokenach.

### Planuj i działaj (Erdogan et al., arXiv:2503.09572, ICML 2025)

Wzorzec Plan-and-Act skaluje tę koncepcję na potrzeby długofalowych agentów internetowych i mobilnych. Kluczowym wkładem jest tu generowanie syntetycznych danych planowania: specjalny generator trajektorii tworzy dane treningowe z wyraźnie rozpisanym planem. Służą one do dostrajania modeli planujących, które muszą radzić sobie z zadaniami wymagającymi od 30 do 50 kroków (np. w środowiskach typu WebArena), gdzie tradycyjna, pojedyncza pętla ReAct szybko straciłaby spójność.

### Kiedy wybrać który

| Wzorzec | Kiedy stosować |
|--------|------|
| ReAct | Krótkie zadania, nieznane środowisko, potrzeba reaktywnej obsługi wyjątków |
| ReWOO | Ustrukturyzowane zadania z predefiniowanymi narzędziami, wrażliwość na koszty tokenów, możliwość zrównoleglenia zadań |
| Plan-and-Execute | Podobnie jak ReWOO, ale z możliwością modyfikacji planu po wykonaniu części zadań |
| Plan-and-Act | Długi horyzont czasowy (>30 kroków), interakcja ze stronami www / urządzeniami mobilnymi / komputerem |
| Tree of Thoughts | Gdy wyszukiwanie w przestrzeni rozwiązań uzasadnia wyższy koszt obliczeniowy (Lekcja 04) |

Rekomendacja Anthropic z grudnia 2024 roku: zacznij od najprostszego rozwiązania. Jeśli zadanie sprowadza się do jednego wywołania narzędzia i podsumowania wyniku, nie wdrażaj architektury ReWOO. Jeśli natomiast proces badawczy wymaga wykonania 40 kroków, nie polegaj na samej pętli ReAct.

## Zbuduj to

Plik `code/main.py` implementuje uproszczoną wersję ReWOO:

- `Planner` – komponent oparty na promptach, który generuje plan w postaci grafu DAG.
- `Worker` – uruchamia narzędzia dla poszczególnych węzłów grafu na podstawie rejestru.
- `Solver` – agreguje zgromadzone dowody i formułuje ostateczną odpowiedź.
- Rozwiązywanie zależności: odniesienia takie jak `#E1` są zastępowane rzeczywistymi wynikami wcześniejszych kroków.

Wersja demonstracyjna odpowiada na pytanie: „Jaka jest populacja stolicy Francji w zaokrągleniu do milionów?”, realizując dwuetapowy plan: (1) wyszukaj stolicę, (2) sprawdź jej populację, a następnie sformułuj odpowiedź.

Uruchomienie:

```
python3 code/main.py
```

Logi (ślad wykonania) pokazują najpierw kompletny plan, następnie wyniki działania wykonawców (Workers), a na końcu proces tworzenia odpowiedzi przez Solver. Porównaj zużycie tokenów (program wypisuje przybliżoną liczbę znaków) z tradycyjną pętlą ReAct – ReWOO okazuje się znacznie efektywniejsze przy tego typu ustrukturyzowanych zadaniach.

## Użyj tego

LangGraph dostarcza Plan-and-Execute jako przepis (`create_react_agent` dla ReAct, niestandardowe wykresy dla planowania-wykonania). Przepływy CrewAI bezpośrednio kodują wzorzec: definiujesz zadania z góry, a Flow DAG je wykonuje. Podejście oparte na danych syntetycznych stosowane w programie Plan-and-Act nadal opiera się głównie na badaniach; wzorzec środowiska wykonawczego (jawny plan DAG) jest dostarczany w fazie produkcyjnej za pośrednictwem przepływów LangGraph i CrewAI.

## Wyślij to

Plik `outputs/skill-rewoo-planner.md` opisuje generowanie grafu DAG dla planu ReWOO na podstawie zapytania użytkownika i katalogu dostępnych narzędzi. Przed przekazaniem planu do wykonawcy weryfikuje on jego poprawność (czy graf jest acykliczny, czy wszystkie odniesienia są prawidłowe oraz czy wywoływane narzędzia istnieją).

## Ćwiczenia

1. Zaimplementuj równoległe uruchamianie wykonawców (Workers) dla niezależnych węzłów planu. Jaki zysk czasowy osiągniesz na 6-węzłowym grafie DAG posiadającym 2 grupy zadań równoległych?
2. Dodaj krok ponownego planowania (replanning), który uruchamia się, gdy dowolny z wykonawców zwróci błąd. Jaka jest minimalna zmiana w architekturze ReWOO, która przekształca ją w pełny wzorzec Plan-and-Execute?
3. Zastąp komponent `Planner` mniejszym modelem (klasy 7B), pozostawiając `Solver` na poziomie najmocniejszego modelu (frontier model). Porównaj jakość całego procesu – w jakich przypadkach taki podział zawodzi?
4. Zapoznaj się z sekcją 4 artykułu o ReWOO poświęconą destylacji planisty. Zapojektuj koncepcyjnie proces przenoszenia wiedzy z modelu 175B do 7B: jakich danych treningowych potrzebujesz i jak ocenisz jakość generowanych planów?
5. Zmodyfikuj uproszczony model tak, aby odzwierciedlał podejście Plan-and-Act (gdzie plan jest sekwencją kroków, a nie grafem DAG). Jak zmieniają się wady i zalety takiego rozwiązania?

## Kluczowe terminy

| Termin | Potoczne określenie | Co to w rzeczywistości oznacza |
|------|----------------|--------------------------------------|
| ReWOO | „Rozumowanie bez obserwacji” (Reasoning Without Observation) | Zaplanowanie działań, równoległe zebranie dowodów, a następnie wypracowanie rozwiązania – brak obserwacji w prompcie planisty. |
| Plan-and-Execute | „Wzorzec planowania i wykonania w LangChain” | Architektura ReWOO rozszerzona o opcjonalny krok ponownego planowania po wykonaniu zadań. |
| Plan-and-Act | „Skalowany wzorzec Plan-and-Execute” | Wyraźny podział na planistę i wykonawcę wspierany syntetycznymi danymi treningowymi, dedykowany do zadań o długim horyzoncie czasowym. |
| Odniesienie do dowodów (Evidence Reference) | „#E1, #E2, …” | Zmienna w planie, która w momencie uruchomienia zadania zostaje zastąpiona rzeczywistym wynikem działania wcześniejszego wykonawcy. |
| Destylacja planisty (Planner Distillation) | „Mały planista, duży wykonawca” | Dostrojenie mniejszego modelu na bazie planów wygenerowanych przez większy model pełniący rolę nauczyciela. |
| Wydajność tokenów | „Mniej zapytań tam i z powrotem” | Zmniejszenie zużycia tokenów (w publikacji wykazano 5-krotne oszczędności w HotpotQA w porównaniu do ReAct). |
| Wykonawca DAG | „Dyspozytor topologiczny” | Komponent uruchamiający węzły planu zgodnie z kolejnością zależności, w tym równolegle w ramach tego samego poziomu. |

## Dalsze czytanie

- [Xu et al., ReWOO: Decoupling Reasoning from Observations (arXiv:2305.18323)](https://arxiv.org/abs/2305.18323) — artykuł kanoniczny
- [Erdogan et al., Plan-and-Act (arXiv:2503.09572)](https://arxiv.org/abs/2503.09572) — skalowany planista-wykonawca z planami syntetycznymi
- [Poradnik LangGraph Plan-and-Execute](https://docs.langchain.com/oss/python/langgraph/overview) — przepis na framework
– [Anthropic, Building Effective Agents](https://www.anthropic.com/research/building-efektywne-agents) — wybierz najprostszy wzór, który działa
